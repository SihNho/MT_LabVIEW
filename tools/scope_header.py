# ---
# labview: none
# hardware: none
# ---
"""DECLARED-SCOPE HEADER of every tools/ script (card chat-E3, user 2026-10-04: "훅 작동을 위해서는 프론트매터에 특정 플래그를
달도록 강제해야겠음" ... "이번 훅을 넣는 가장 큰 이유는 초장에 에러 발생을 극소화하여 시간 낭비를 최소화하는게 목적임").

Every tools/**/*.py and tools/**/*.ps1 carries ONE block, in the same words as the task/1 card flags:

    # ---
    # labview: none        # none | read | build
    # hardware: none       # none | camera | motor
    # offline-args: adopt selftest      (optional) argv tokens that make THIS run labview none + hardware none
    # evidence: tools/bench/x.log:12     (required with offline-args, or for a `none` that imports a LabVIEW-run module)
    # ---

POSITION: the first 12 lines (after a shebang / coding cookie / BOM) or the last 8 lines. The migration (`migrate
--apply`) APPENDS the block at the END and keeps each file's mtime, so every existing `file:line` citation into a
tools script stays valid (the docs carry thousands) and every mtime-ordered gate (guard_cycle's review-vs-recipe order)
sees the same order as before. A script written new may put it at the top.

CANONICAL BYTES: canonical_bytes() removes exactly the block (and, for an appended block, exactly what the migration
added), so sha256/md5 records written before the migration (stop_record releases, stage_prerun dry/prerun records,
card input pins) still match: canonical_sha256 / canonical_md5 are what those readers use for a .py/.ps1.

USED BY: protocol.check_command (card flags at launch), guard_peer.offline_command, stop_record.offline_checker
(an offline program naming a recipe is not a launch), tools/hooks/guard_write.py (PostToolUse, at write time).

Levels: labview none < read < build; card hardware `none` admits script hardware none|camera (the camera is reached
through LabVIEW, governed by the labview level), card hardware `gate` admits motor too.
"""
import ast
import hashlib
import io
import json
import os
import re
import shlex
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = os.path.join(ROOT, "tools")

LEVELS = {"none": 0, "read": 1, "build": 2}
HW_LEVELS = {"none": 0, "camera": 1, "motor": 2}
CARD_HW_MAX = {"none": 1, "gate": 2}           # card flags.hardware -> highest script hardware level it admits
KEYS = ("labview", "hardware", "offline-args", "evidence")
SCRIPT_EXT = (".py", ".ps1")

OPEN_RE = re.compile(rb"^#[ \t]*---[ \t]*\r?$")
KEY_RE = re.compile(r"^#[ \t]*([a-z][a-z-]*)[ \t]*:[ \t]*([^#]*?)[ \t]*(?:#.*)?$")
HEAD_LINES, TAIL_LINES = 12, 8

# Modules whose import makes a script a LabVIEW client (direct COM) or a LabVIEW-run library (runs stages / VIs).
LV_DIRECT = {"gscript", "lvclick", "win32com", "pythoncom", "comtypes", "win32gui", "win32api"}
LV_RUN = {"stagekit", "stagexec"}
LV_TEXT_RE = re.compile(r"lv_gui\.ps1|LabVIEW\.exe|\bLabVIEW\.Application\b", re.I)
RECIPE_TEXT_RE = re.compile(r"tools[\\/]recipes[\\/]", re.I)
SHELL_FUNCS = {"run", "popen", "call", "check_call", "check_output", "system", "spawnv", "spawnl", "startfile"}
PS1_LV_RUN_RE = re.compile(r"&\s*[\"']?[^\"'\s]*lv_gui\.ps1|lv_gui\.ps1[\"']?\s+-Action|-File\s+[\"']?[^\"'\s]*lv_gui\.ps1|"
                           r"Start-Process[^\n]*LabVIEW\.exe|&\s*[\"']?[^\"'\n]*LabVIEW\.exe|ComObject\s+[\"']?LabVIEW|"
                           r"Stop-Process\s+-Name\s+LabVIEW", re.I)
MOTOR_TEXT_RE = re.compile(r"motor_gate\.py|motor_send_pi\.ps1|motor_asi_io\.ps1|SetCommand(?:_signed)?\.vi", re.I)
CAMERA_TEXT_RE = re.compile(r"\bpypylon\b|camera_contract|IMAQdx", re.I)


# ------------------------------------------------------------------------------------------------ the block itself
def _lines(b):
    return b.splitlines(True)


def _find_block(lines):
    """(start, end) line indexes (end exclusive) of the header block, or None. Head window first, then tail."""
    n = len(lines)

    def scan(lo, hi):
        i = lo
        while i < hi:
            if OPEN_RE.match(lines[i].rstrip(b"\n")):
                j = i + 1
                while j < min(n, i + 9):
                    if OPEN_RE.match(lines[j].rstrip(b"\n")):
                        body = lines[i + 1:j]
                        if body and all(KEY_RE.match(x.decode("utf-8", "replace").strip()) for x in body):
                            return i, j + 1
                        break
                    j += 1
            i += 1
        return None
    skip = 0
    while skip < min(n, 2) and (lines[skip].lstrip(b"\xef\xbb\xbf").startswith(b"#!") or
                                re.match(rb"^\xef?\xbb?\xbf?#.*coding[:=]", lines[skip])):
        skip += 1
    hit = scan(skip, min(n, skip + HEAD_LINES))
    if hit:
        return hit
    return scan(max(0, n - TAIL_LINES - 6), n)


def parse_bytes(b):
    """(header dict | None, error | None). Error = the block exists but is invalid; (None, None) = no block."""
    lines = _lines(b)
    span = _find_block(lines)
    if not span:
        return None, None
    h = {}
    for raw in lines[span[0] + 1:span[1] - 1]:
        m = KEY_RE.match(raw.decode("utf-8", "replace").strip())
        k, v = m.group(1), m.group(2).strip()
        if k not in KEYS:
            return None, "unknown header key %r (allowed: %s)" % (k, ", ".join(KEYS))
        if k in h:
            return None, "header key %r given twice" % k
        h[k] = v
    for k in ("labview", "hardware"):
        if k not in h:
            return None, "header lacks `%s:`" % k
    if h["labview"] not in LEVELS:
        return None, "labview: %r is not none | read | build" % h["labview"]
    if h["hardware"] not in HW_LEVELS:
        return None, "hardware: %r is not none | camera | motor" % h["hardware"]
    h["offline-args"] = [t for t in re.split(r"[\s,]+", h.get("offline-args", "")) if t]
    if h["offline-args"] and not h.get("evidence"):
        return None, "offline-args needs `evidence:` (a log or file:line showing those runs never open LabVIEW)"
    return h, None


def read(path):
    try:
        with open(path, "rb") as f:
            return parse_bytes(f.read())
    except OSError as e:
        return None, "unreadable: %s" % e


def canonical_bytes(b):
    """The bytes without the header block - exactly the file before the migration added it (see module doc)."""
    lines = _lines(b)
    span = _find_block(lines)
    if not span:
        return b
    s, e = span
    if e == len(lines) and not lines[-1].endswith(b"\n") and s > 0:
        # appended to a file that had no final newline: the migration wrote "\n" + block (no final newline)
        prev = lines[s - 1]
        cut = 2 if prev.endswith(b"\r\n") else 1
        return b"".join(lines[:s - 1]) + prev[:-cut]
    return b"".join(lines[:s] + lines[e:])


def _canon_file(path):
    with open(path, "rb") as f:
        b = f.read()
    return canonical_bytes(b) if path.lower().endswith(SCRIPT_EXT) else b


def canonical_sha256(path):
    return hashlib.sha256(_canon_file(path)).hexdigest()


def canonical_md5(path):
    return hashlib.md5(_canon_file(path)).hexdigest()


def render(labview, hardware, offline_args=(), evidence=None, nl="\n"):
    out = ["# ---", "# labview: %s" % labview, "# hardware: %s" % hardware]
    if offline_args:
        out.append("# offline-args: %s" % " ".join(offline_args))
    if evidence:
        out.append("# evidence: %s" % evidence)
    out.append("# ---")
    return nl.join(out) + nl


def append_block(b, block_text):
    """The file bytes with the block appended so that canonical_bytes() gives `b` back exactly."""
    nl = "\r\n" if b"\r\n" in b[:4000] else "\n"
    blk = block_text.replace("\n", nl).encode("ascii") if nl == "\r\n" else block_text.encode("ascii")
    if not b or b.endswith(b"\n"):
        return b + blk
    return b + nl.encode("ascii") + blk.rstrip(b"\r\n")


# ------------------------------------------------------------------------------------------------- static reading
def _imports(tree):
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out.update(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom) and n.module and not n.level:
            out.add(n.module.split(".")[0])
    return out


def _shell_consts(tree):
    """String constants passed to a subprocess/os.system-style call (positional, keyword, or inside a list arg)."""
    out = []
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if name.lower() in SHELL_FUNCS:
                for a in list(n.args) + [k.value for k in n.keywords]:
                    for c in ast.walk(a):
                        if isinstance(c, ast.Constant) and isinstance(c.value, str):
                            out.append(c.value)
    return out


def _invokes_lv(tree):
    """The LabVIEW program a subprocess/os.system-style call starts (lv_gui.ps1, LabVIEW.exe), or a
    Dispatch("LabVIEW.Application") COM call - else ''. A NAME in a regex, a docstring or a message is not an invocation."""
    m = LV_TEXT_RE.search(" ".join(_shell_consts(tree)))
    if m:
        return m.group(0)
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
            if name in ("Dispatch", "DispatchEx", "GetActiveObject", "EnsureDispatch") and any(
                    isinstance(a, ast.Constant) and isinstance(a.value, str) and "labview" in a.value.lower()
                    for a in n.args):
                return "%s(LabVIEW.Application)" % name
    return ""


PY_RECIPE_RE = re.compile(r"(?:^|[\s\\/\"'])py(?:thon)?[\w.]*(?:\.exe)?\s+(?:-\S+\s+)*\S*tools[\\/]recipes[\\/]\S*\.py",
                          re.I)


def _runs_recipe(tree):
    """True when a subprocess/os.system-style call RUNS a tools/recipes/ script: a command string `py ... recipe.py`,
    or an argv list whose first .py element is a recipe (`[sys.executable, "-u", "tools/recipes/x.py"]`). A recipe path
    passed as an ARGUMENT to another program (`git show`, `prior_art_review.py --recipe`) is not a run."""
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else "")
        if name.lower() not in SHELL_FUNCS or not n.args:
            continue
        a0 = n.args[0]
        if isinstance(a0, ast.Constant) and isinstance(a0.value, str) and PY_RECIPE_RE.search(a0.value):
            return True
        if isinstance(a0, (ast.List, ast.Tuple)):
            consts = [e.value for e in a0.elts if isinstance(e, ast.Constant) and isinstance(e.value, str)]
            first_py = next((c for c in consts if c.lower().endswith(".py") or
                             re.match(r"^(?:git|powershell|pwsh|cmd)(?:\.exe)?$", c, re.I)), None)
            if first_py and RECIPE_TEXT_RE.search(first_py):
                return True
    return False


def _code_only(src):
    try:
        sys.path.insert(0, HERE)
        import protocol
        return protocol.code_only(src)
    except Exception:              # noqa: BLE001
        return src


def honesty(path, h, src=None):
    """Problems with a DECLARED header against the code (an empty list = honest). Only `labview: none` (and
    hardware none) can be dishonest in the direction that matters: a script that says it never opens LabVIEW."""
    if src is None:
        with open(path, encoding="utf-8", errors="replace") as f:
            src = f.read()
    probs = []
    if path.lower().endswith(".ps1"):
        m = PS1_LV_RUN_RE.search(src)
        if h["labview"] == "none" and m and not h.get("evidence"):
            probs.append("labview: none but the script invokes %s" % m.group(0)[:60])
        return probs
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return probs            # compile() reports it
    if h["labview"] == "none":
        imp = _imports(tree)
        direct = sorted(imp & LV_DIRECT)
        if direct:
            probs.append("labview: none but it imports %s (a LabVIEW/COM client) - declare read or build" %
                         ", ".join(direct))
        run = sorted(imp & LV_RUN)
        if run and not h.get("evidence") and not _offline_selftest(path) and _closure_touches(path):
            probs.append("labview: none but it imports %s (LabVIEW-run module) without `evidence:` of an offline "
                         "measurement - declare read/build, or cite the measurement" % ", ".join(run))
        code = _code_only(src)
        m = _invokes_lv(tree)
        if m:
            probs.append("labview: none but the code invokes %s" % m)
        if _runs_recipe(tree):
            probs.append("labview: none but it starts a tools/recipes/ script in a subprocess")
        if not h.get("evidence") and re.search(r"\brunpy\.run_(?:path|module)\s*\(", code):
            probs.append("labview: none but it runs another file in-process (runpy) without `evidence:` that the run "
                         "is sandboxed (as tools/stage_prerun.py:17 is)")
    if h["labview"] == "read":
        try:
            import protocol
            f = protocol.src_features(src)
            bad = [k for k in ("save", "gui", "run") if f[k]]
        except Exception:          # noqa: BLE001
            bad = []
        if bad:
            probs.append("labview: read but the code calls %s (save / state-changing GUI / VI Run) - declare build"
                         % "/".join(bad))
        if RECIPE_TEXT_RE.search(path):
            probs.append("labview: read on a tools/recipes/ script - recipes build (flags.labview 'read' refuses them)")
    if h["hardware"] == "none":
        m = MOTOR_TEXT_RE.search(" ".join(_shell_consts(tree)))
        if m:
            probs.append("hardware: none but it runs %s in a subprocess - declare hardware: motor" % m.group(0))
    if h.get("evidence"):
        ev = re.sub(r":\d+(?:-\d+)?$", "", h["evidence"])
        if not os.path.exists(ev if os.path.isabs(ev) else os.path.join(ROOT, ev)):
            probs.append("evidence: %s does not exist" % h["evidence"])
    return probs


def _closure_touches(path):
    """guard_peer.script_touches_labview (v2, card 131-2): does what this script USES of stagekit/stagexec reach
    LabVIEW? Fails closed (True) when the analysis cannot run."""
    try:
        sys.path.insert(0, os.path.join(TOOLS, "hooks"))
        import guard_peer
        return guard_peer.script_touches_labview(path)
    except Exception:              # noqa: BLE001
        return True


def _offline_selftest(path):
    try:
        import protocol
        rel = os.path.relpath(os.path.abspath(path), ROOT).replace("\\", "/")
        return any(os.path.normcase(k) == os.path.normcase(rel) for k in protocol.OFFLINE_SELFTESTS)
    except Exception:              # noqa: BLE001
        return False


def compile_error(path, src=None):
    """None, or the syntax/parse error text. .py: compile() in memory; .ps1: the PowerShell parser (one process)."""
    if path.lower().endswith(".py"):
        if src is None:
            with open(path, "rb") as f:
                src = f.read()
        try:
            compile(src, path, "exec", dont_inherit=True)
            return None
        except (SyntaxError, ValueError) as e:
            return "%s: %s" % (type(e).__name__, e)
    if path.lower().endswith(".ps1"):
        import subprocess
        ps = ("$e=$null;$t=$null;[void][System.Management.Automation.Language.Parser]::ParseFile('%s',[ref]$t,[ref]$e);"
              "foreach($x in $e){Write-Output ('{0}:{1} {2}' -f $x.Extent.StartLineNumber,$x.Extent.StartColumnNumber,"
              "$x.Message)}" % path.replace("'", "''"))
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], capture_output=True,
                               text=True, timeout=20)
        except (OSError, subprocess.TimeoutExpired):
            return None             # no parser available: not a refusal (fail open on the TOOL, never on content)
        out = (r.stdout or "").strip()
        return ("PowerShell parse: " + out.splitlines()[0]) if out else None
    return None


def infer(path, src=None):
    """The migration's scope for an existing script. labview: none when nothing in its import closure reaches LabVIEW
    (guard_peer.script_touches_labview, v2) and it names no lv_gui/LabVIEW.exe; read when it reaches LabVIEW, is not
    a recipe and has no save/gui/run call (exactly what flags.labview 'read' admitted before); build otherwise.
    Anything unparseable -> build (unclear = build: nothing is loosened)."""
    if src is None:
        with open(path, encoding="utf-8", errors="replace") as f:
            src = f.read()
    hw = "none"
    if path.lower().endswith(".ps1"):
        # fp-40 follow-up: the word "LabVIEW" in a prompt or message (peer.ps1) is not a LabVIEW run - an INVOCATION is
        lv = "build" if PS1_LV_RUN_RE.search(src) else "none"
        if MOTOR_TEXT_RE.search(src) or re.search(r"\bSerialPort\b|\bVISA\b", src):
            hw = "motor"
        return {"labview": lv, "hardware": hw}
    try:
        ast.parse(src)
    except SyntaxError:
        return {"labview": "build", "hardware": "none"}
    sys.path.insert(0, os.path.join(TOOLS, "hooks"))
    sys.path.insert(0, HERE)
    import protocol
    try:
        import guard_peer
        touches = guard_peer.script_touches_labview(path)
    except Exception:              # noqa: BLE001
        touches = True
    try:
        tree = ast.parse(src)
    except SyntaxError:
        tree = None
    # fp-40 (chat-A1, 2026-10-04): an lv_gui.ps1 / LabVIEW.exe NAME inside a regex or a message (protocol.py's own
    # LV_CMD_RE) is not a LabVIEW run; only a subprocess/os.system call that INVOKES it is.
    if not touches and tree is not None and _invokes_lv(tree):
        touches = True
    if not touches:
        lv = "none"
    else:
        f = protocol.src_features(src)
        recipe = bool(protocol.RECIPE_PATH_RE.search(path))
        lv = "build" if (recipe or f["save"] or f["gui"] or f["run"]) else "read"
    try:
        consts = " ".join(_shell_consts(ast.parse(src)))
    except SyntaxError:
        consts = ""
    if MOTOR_TEXT_RE.search(consts) or re.search(r"(?m)^\s*(?:import|from)\s+(?:serial|pyvisa)\b", src):
        hw = "motor"
    elif CAMERA_TEXT_RE.search(protocol.code_only(src)):
        hw = "camera"
    return {"labview": lv, "hardware": hw}


# ------------------------------------------------------------------------------------------------ launch reading
# scope-cwd-fix-20261012 (card chat-X11; Claude + GPT agreed, tools/bench/debate/scope-cwd-fix/relay/round_06_*.md; user
# 2026-10-12 "동의 받고 고쳐"): every launch reader takes the hook payload's `cwd`. cwd None = the behaviour before the fix,
# byte for byte (relative paths against ROOT, no folder-change / mix / absolute-path rule). Self-test:
# tools/bench/selftest_scope_cwd.py.
DRIVE_ABS_RE = re.compile(r"^[A-Za-z]:[\\/]")
CD_WORDS = {"cd", "chdir", "pushd", "popd", "set-location", "push-location", "pop-location", "sl"}
PWSH_RE = re.compile(r"(?:^|[\\/])(?:powershell|pwsh)(?:\.exe)?$", re.I)


def _base(cwd=None):
    """The folder a relative script path resolves against: the payload's cwd when given, else ROOT."""
    return os.path.normpath(cwd) if cwd else ROOT


def is_root(cwd):
    """True when cwd is absent or (normalized, case-folded) the main tree ROOT."""
    return not cwd or os.path.normcase(os.path.normpath(cwd)) == os.path.normcase(ROOT)


def _under(p, folder):
    return os.path.normcase(os.path.normpath(p)).startswith(os.path.normcase(os.path.normpath(folder)) + os.sep)


def _abs(p, cwd=None):
    p = p.strip("\"'")
    return os.path.normpath(p if os.path.isabs(p) else os.path.join(_base(cwd), p))


def in_tools(p, cwd=None):
    """True when `p` (resolved against cwd, else ROOT) lies under that folder's tools/."""
    return _under(_abs(p, cwd), os.path.join(_base(cwd), "tools"))


INTERP_RE = re.compile(r"^(?:\"[^\"]*\"|'[^']*'|\S+)$")
PY_PROG_RE = re.compile(r"(?:^|[\\/])py(?:thon)?[\w.]*?(?:\.exe)?$", re.I)
PS1_RE = re.compile(r"(?:(?:^|[\s\"'(;])&\s*|-File\s+)([\"']?)([^\"'\s;|&]+\.ps1)\1", re.I)


def _segments(cmd):
    sys.path.insert(0, HERE)
    import stop_record
    return stop_record.split_segments(cmd or "")


def _tok(seg):
    try:
        return [t.strip("\"'") for t in shlex.split(seg, posix=False)]
    except ValueError:
        return [t.strip("\"'") for t in seg.split()]


def launches(cmd, cwd=None):
    """[(script abs path, argv tokens after it)] for every script RUN by `cmd`: a .py in command position of a
    segment (env prefix allowed, interpreter flags skipped; `-c` / `-m <module>` run no file of ours), the child after
    a bgrun `--`, and a .ps1 after `&` or `-File`. A path that is only READ (`grep x a.py`, `git add a.py`,
    `py -m py_compile a.py`) is not here. Relative paths resolve against `cwd` (else ROOT)."""
    return [(p, a) for p, a, _raw in _runs(cmd, cwd)]


def _runs(cmd, cwd=None):
    """[(script abs path, argv, raw path token as written)] - launches() plus the token, for the absolute-path rule."""
    out = []
    for seg in _segments(cmd):
        out.extend(_seg_runs(seg, 0, cwd))
    return out


def _env_skip(toks):
    i = 0
    while i < len(toks) and re.match(r"^\w+=", toks[i]):
        i += 1
    return i


def _pwsh_inner(seg):
    """The command string a `powershell|pwsh ... -Command <x>` segment runs, or None."""
    m = re.search(r"-Command\s+(\"(?:[^\"]*)\"|'(?:[^']*)'|.+)$", seg, re.I)
    if not m:
        return None
    inner = m.group(1).strip()
    return inner[1:-1] if inner[:1] in "\"'" and inner[-1:] == inner[:1] else inner


def _seg_launches(seg, depth=0, cwd=None):
    return [(p, a) for p, a, _raw in _seg_runs(seg, depth, cwd)]


def _seg_runs(seg, depth=0, cwd=None):
    out = []
    for m in PS1_RE.finditer(seg):
        rest = seg[m.end():]
        out.append((_abs(m.group(2), cwd), _tok(rest), m.group(2)))
    toks = _tok(seg)
    i = _env_skip(toks)
    if i < len(toks) and depth < 2 and PWSH_RE.search(toks[i]):
        inner = _pwsh_inner(seg)       # the command string it runs
        if inner is not None:
            for s in _segments(inner):
                out.extend(x for x in _seg_runs(s, depth + 1, cwd) if x not in out)
        return out
    if i >= len(toks) or not PY_PROG_RE.search(toks[i]):
        return out
    i += 1
    while i < len(toks) and toks[i].startswith("-"):
        if toks[i] in ("-c", "-m"):
            return out
        i += 1
    if i >= len(toks) or not toks[i].lower().endswith(".py"):
        return out
    script, argv = _abs(toks[i], cwd), toks[i + 1:]
    out.append((script, argv, toks[i]))
    if os.path.basename(script).lower() == "bgrun.py" and "--" in argv:
        child = argv[argv.index("--") + 1:]
        # the child runs in bgrun's PROJECT (tools/bgrun.py:32,236 = the folder above bgrun's tools/); with a cwd that
        # is where its relative paths resolve (== cwd whenever bgrun itself sits in cwd's tools/). cwd None: as before.
        ccwd = os.path.dirname(os.path.dirname(script)) if cwd else None
        out.extend(_seg_runs(" ".join('"%s"' % t if " " in t else t for t in child), 0, ccwd))
    return out


def changes_folder(cmd, depth=0):
    """True when a segment of `cmd` (or of a nested `powershell -Command`) starts with a folder change: cd / chdir /
    pushd / popd / Set-Location / Push-Location / Pop-Location / sl (a leading `(` or `{` of a subshell is skipped).
    Relative script paths after it no longer resolve against the payload cwd, so no timeout exemption (chat-X11)."""
    for seg in _segments(cmd):
        toks = _tok(seg.lstrip(" \t({"))
        i = _env_skip(toks)
        if i >= len(toks):
            continue
        if toks[i].lower() in CD_WORDS:
            return True
        if depth < 2 and PWSH_RE.search(toks[i]):
            inner = _pwsh_inner(seg)
            if inner is not None and changes_folder(inner, depth + 1):
                return True
    return False


def effective(h, argv):
    """(labview, hardware) for ONE run: offline-args present in its argv -> ('none', 'none')."""
    if h.get("offline-args") and any(t in h["offline-args"] for t in argv):
        return "none", "none"
    return h["labview"], h["hardware"]


def _judged(p, cwd=None):
    """A launched path launch_scope judges: under ROOT's tools/, or (cwd given) under the cwd's tools/ as well."""
    return _under(p, TOOLS) or bool(cwd and _under(p, os.path.join(_base(cwd), "tools")))


def launch_scope(cmd, extra=(), cwd=None):
    """[(path, labview, hardware, problem|None)] for every tools/ script `cmd` runs. problem: missing/invalid header,
    or a .py that does not compile. `extra`: paths another detector (protocol.PY_TOKEN_RE) saw in command position
    that launches() did not parse - judged by their header with NO offline-args (fail closed, never looser).
    cwd (chat-X11): relative paths resolve against it; scripts under ROOT's tools/ AND under the cwd's tools/ are judged,
    and a script outside ROOT's tools/ (a bench-cell file) also gets the header honesty check (problem when dishonest)."""
    out = []
    runs = launches(cmd, cwd)
    seen = {os.path.normcase(p) for p, _a in runs}
    runs += [(_abs(p, cwd), []) for p in extra if os.path.normcase(_abs(p, cwd)) not in seen]
    for p, argv in runs:
        if not _judged(p, cwd) or not os.path.isfile(p):
            continue
        h, err = read(p)
        if not err and _rel(p) in NO_TOUCH:      # chat-A1's files (this card may not edit them): registry fills the gap
            k = KNOWN[_rel(p)]
            if h is None:
                h = {"labview": k["labview"], "hardware": k["hardware"], "offline-args": k.get("offline-args") or [],
                     "evidence": k.get("evidence")}
            elif not h.get("offline-args") and k.get("offline-args"):
                # its owner's header (d60ddbc0) omits the offline modes protocol has allowed since 2026-09-24
                # (`cycle_runner.py --dry-run|--dry-cmd|--no-motor-hooks` under hardware none) - kept until the owner adds them
                h = dict(h, **{"offline-args": k["offline-args"], "evidence": h.get("evidence") or k.get("evidence")})
        if h is not None:
            h["_path"] = p
        if err or h is None:
            out.append((p, "build", "motor", "no valid scope header (%s)" % (err or "missing") +
                        " - add `# ---` / `# labview: none|read|build` / `# hardware: none|camera|motor` / `# ---`"))
            continue
        ce = compile_error(p) if p.lower().endswith(".py") else None
        lv, hw = effective(h, argv)
        _OFFLINE_HINT[os.path.normcase(p)] = h.get("offline-args") or []
        prob = ("does not compile: %s" % ce) if ce else None
        if prob is None and cwd and not _under(p, TOOLS):
            prob = _cell_honesty(p, h)
        out.append((p, lv, hw, prob))
    return out


def _cell_honesty(p, h):
    """None, or the problem: honesty() of a script outside ROOT's tools/ (guard_write never saw it). Fails closed."""
    try:
        probs = honesty(p, h)
    except Exception as e:         # noqa: BLE001
        probs = ["honesty check could not run (%s: %s)" % (type(e).__name__, e)]
    return ("scope header is not honest: %s" % "; ".join(probs)) if probs else None


def offline_exemption(cmd, cwd=None):
    """(exempt, hint|None): may `cmd` run without the 2b timeout because every script it runs is effectively labview
    none + hardware none? cwd None = the rule before chat-X11 exactly. With a cwd (scope-cwd-fix-20261012, agreed):
    never exempt when it changes folder (changes_folder) or runs a script that is not a file under the cwd's tools/
    (unconfirmed / outside); and when the normalized cwd is not ROOT, every script must be written as a drive-absolute
    path. hint is set ONLY when that absolute-path rule is the reason. Self-test: tools/bench/selftest_scope_cwd.py."""
    if cwd is None:
        sc = launch_scope(cmd)
        return bool(sc) and all(lv == "none" and hw == "none" and not prob for _p, lv, hw, prob in sc), None
    if changes_folder(cmd):
        return False, None
    runs = _runs(cmd, cwd)
    btools = os.path.join(_base(cwd), "tools")
    if not runs or any(not _under(p, btools) or not os.path.isfile(p) for p, _a, _r in runs):
        return False, None
    sc = launch_scope(cmd, cwd=cwd)
    if len(sc) != len(runs) or not all(lv == "none" and hw == "none" and not prob for _p, lv, hw, prob in sc):
        return False, None
    rel = [p for p, _a, raw in runs if not DRIVE_ABS_RE.match(raw)]
    if rel and not is_root(cwd):
        return False, ("the command runs in %s, not the main tree: there a script runs without a timeout only when it "
                       "is given by its ABSOLUTE path with the drive, inside %s - e.g. py \"%s\""
                       % (_base(cwd), btools, rel[0]))
    return True, None


_OFFLINE_HINT = {}


def _hint(p):
    oa = _OFFLINE_HINT.get(os.path.normcase(p)) or []
    return ("; use %s for an offline run" % " / ".join(oa)) if oa else ""


def check_launch(flags, cmd, extra=()):
    """None, or the refusal: a run whose declared scope exceeds the card's flags, a header missing/invalid, a compile
    error. `flags` = task/1 flags (labview none|read|build, hardware none|gate)."""
    lvmax = LEVELS.get(str(flags.get("labview") or "none"), 0)
    hwmax = CARD_HW_MAX.get(str(flags.get("hardware") or "none"), 1)
    for p, lv, hw, prob in launch_scope(cmd, extra):
        r = _rel(p)
        if prob:
            return "%s: %s" % (r, prob)
        if LEVELS[lv] > lvmax:
            what = "recipes are refused - " if (RECIPE_TEXT_RE.search(p) and lvmax == 1) else ""
            return "flags.labview is %r - %s%s declares labview: %s (scope header)%s" % (
                flags.get("labview", "none"), what, r, lv, _hint(p))
        if HW_LEVELS[hw] > hwmax:
            return "flags.hardware is %r - %s declares hardware: %s (scope header)%s" % (
                flags.get("hardware", "none"), r, hw, _hint(p))
    return None


def offline_run(cmd):
    """True when `cmd` runs at least one tools/ script and EVERY tools/ script it runs is effectively labview none
    (bgrun included); None when it runs no tools/ script (undecided here); False otherwise."""
    sc = launch_scope(cmd)
    if not sc:
        return None
    return all(prob is None and lv == "none" for _p, lv, _hw, prob in sc)


def _rel(p):
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:
        return p


# --------------------------------------------------------------------------------------------------- migration
def all_scripts():
    out = []
    for d, dirs, files in os.walk(TOOLS):
        dirs[:] = [x for x in dirs if x not in ("__pycache__", ".git")]
        for f in files:
            if f.lower().endswith(SCRIPT_EXT):
                out.append(os.path.join(d, f))
    return sorted(out)


# Scripts whose offline modes are documented and measured (evidence cited in the header): fp-37, fp-39.
KNOWN = {
    "tools/stage_prerun.py": {"labview": "build", "hardware": "none",
                              "offline-args": ["--dry", "--prerun", "--scratch-required", "--rebase", "--check-launch",
                                               "--control-lint", "--selftest-control-lint", "--buildarray-check",
                                               "--opmodel-conformance"],
                              "evidence": "tools/stage_prerun.py:17"},
    "tools/stagexec.py": {"labview": "build", "hardware": "none", "offline-args": ["selftest", "adopt"],
                          "evidence": "tools/bench/c125_1_offline_measure.log"},
    "tools/bgrun.py": {"labview": "none", "hardware": "none"},
    "tools/motor_gate.py": {"labview": "none", "hardware": "motor", "offline-args": ["--dry-run", "--help"],
                            "evidence": "tools/motor_gate.py:1"},
    "tools/motor_send_pi.ps1": {"labview": "none", "hardware": "motor"},
    "tools/motor_asi_io.ps1": {"labview": "none", "hardware": "motor"},
    "tools/cycle_runner.py": {"labview": "build", "hardware": "motor",
                              "offline-args": ["--dry-run", "--dry-cmd", "--no-motor-hooks"],
                              "evidence": "tools/protocol.py:1100"},
    "tools/lv_gui.ps1": {"labview": "read", "hardware": "none"},
}
NO_TOUCH = {"tools/cycle_runner.py", "tools/hooks/guard_session.py"}     # owned by the parallel card chat-A1


def tracked_scripts():
    """git-tracked tools scripts only: an untracked file belongs to a card still writing it (chat-A1 runs beside
    chat-E3); the write-time hook asks its author for the header instead."""
    import subprocess
    r = subprocess.run(["git", "ls-files", "-z", "tools"], cwd=ROOT, capture_output=True)
    names = [x for x in r.stdout.decode("utf-8", "replace").split("\0") if x.lower().endswith(SCRIPT_EXT)]
    return sorted(os.path.join(ROOT, x.replace("/", os.sep)) for x in names)


def migrate(apply=False, paths=None):
    rows = []
    for p in (paths or tracked_scripts()):
        rel = _rel(p)
        with open(p, "rb") as f:
            b = f.read()
        h, err = parse_bytes(b)
        if h is not None or err:
            rows.append((rel, "has-header" if h else "INVALID: " + err, None))
            continue
        if rel in NO_TOUCH:
            rows.append((rel, "skipped (owned by chat-A1)", None))
            continue
        k = KNOWN.get(rel)
        sc = dict(k) if k else infer(p)
        blk = render(sc["labview"], sc["hardware"], sc.get("offline-args") or (), sc.get("evidence"))
        nb = append_block(b, blk)
        assert canonical_bytes(nb) == b, rel
        if apply:
            st = os.stat(p)
            with open(p, "wb") as f:
                f.write(nb)
            os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
        rows.append((rel, "%s/%s" % (sc["labview"], sc["hardware"]), sc))
    return rows


def rescope(apply=False):
    """fp-40: re-infer every MIGRATION-written header (a tail block with no offline-args/evidence, not KNOWN, not
    NO_TOUCH) with the corrected rule and rewrite the block where it differs; mtime kept, canonical bytes unchanged."""
    rows = []
    for p in tracked_scripts():
        rel = _rel(p)
        if rel in KNOWN or rel in NO_TOUCH:
            continue
        with open(p, "rb") as f:
            b = f.read()
        lines = _lines(b)
        span = _find_block(lines)
        h, err = parse_bytes(b)
        if not span or err or h is None or h.get("offline-args") or h.get("evidence") or span[1] != len(lines):
            continue
        sc = infer(p)
        if (sc["labview"], sc["hardware"]) == (h["labview"], h["hardware"]):
            continue
        rows.append((rel, "%s/%s -> %s/%s" % (h["labview"], h["hardware"], sc["labview"], sc["hardware"])))
        if apply:
            orig = canonical_bytes(b)
            nb = append_block(orig, render(sc["labview"], sc["hardware"]))
            assert canonical_bytes(nb) == orig, rel
            st = os.stat(p)
            try:
                with open(p, "wb") as f:
                    f.write(nb)
                os.utime(p, ns=(st.st_atime_ns, st.st_mtime_ns))
            except OSError as e:
                rows[-1] = (rel, "WRITE FAILED (%s) - header left as %s/%s" % (e.strerror, h["labview"], h["hardware"]))
    return rows


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if not a or a[0] in ("-h", "--help"):
        print("usage: scope_header.py check <file> | infer <file> | migrate [--apply] [--summary] | launch <cmd>")
        return 0
    if a[0] == "check":
        h, err = read(a[1])
        print(json.dumps({"header": h, "error": err, "honesty": honesty(a[1], h) if h else None,
                          "compile": compile_error(a[1])}))
        return 0 if h and not err else 1
    if a[0] == "infer":
        print(json.dumps(infer(a[1])))
        return 0
    if a[0] == "launch":
        print(json.dumps(launch_scope(" ".join(a[1:]))))
        return 0
    if a[0] == "rescope":
        rows = rescope(apply="--apply" in a)
        from collections import Counter
        for k, v in sorted(Counter(r[1] for r in rows).items()):
            print("%5d  %s" % (v, k))
        return 0
    if a[0] == "migrate":
        rows = migrate(apply="--apply" in a)
        from collections import Counter
        c = Counter(r[1] for r in rows)
        for k, v in sorted(c.items()):
            print("%5d  %s" % (v, k))
        if "--summary" not in a:
            for r in rows:
                if r[1].startswith("INVALID") or "motor" in r[1] or "camera" in r[1]:
                    print("  ", r[0], r[1])
        return 0
    print("unknown command %r" % a[0])
    return 2


if __name__ == "__main__":
    sys.exit(main())
