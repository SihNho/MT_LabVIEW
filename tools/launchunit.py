"""launchunit - the ONE launch-unit rule for every command gate (card 111-3; docs/violation-decisions.md device-failed
2026-09-27 15:49 and 20:20): which `.py` files a shell command RUNS, and which it only names as an ARGUMENT.

Before this module the rule lived in three places and was repaired in one: `stage_prerun.launched_py` (launch gate,
repaired 15:55), `protocol._launched_scripts` (card flags: every existing `.py` after a token starting `py`, so
`pyflakes X` read as "python pyflakes X" - guard_card.log:371) and `stop_record.segment_class` (`py -m <module>` =
"build" unless the module is py_compile/ast/tokenize/tabnanny - material_marker.log:2434). All three now ask here.

THE RULE (decision 15:49): `py [flags] -m <module> args...` launches the MODULE; a later token is an ARGUMENT, not a
launch unit - for the READ-ONLY modules (READONLY_MODULES: pyflakes, pycodestyle, py_compile, ast, tokenize, tabnanny).
FAIL-CLOSED (review archive/peer/2026-09-27-c111c-regress.md s64-78, ACCEPTED): a deny-list of "runner" modules is a
closed list over an open set (`py -m mprof run X`, `py -m streamlit run X` run X), so any OTHER module's path arguments
count as launch units, as does the module itself when it resolves to a project file (`py -m tools.recipes.x`, or a
`pyflakes.py` shadow at the root: `-m` puts the working directory first on sys.path).
`module_arg_segment` (the stop-record's read-only credit) also requires: program exactly py/python[N.N][.exe], no env
prefix (PYTHONPATH hijack), plain path-ish arguments only, and every `cd` in the command to the project root (msys
`/g/...` and Windows forms both resolve), because a shadow module in another directory would run.
Pure functions, stdlib only, no LabVIEW. Self-test: tools/bench/selftest_c111c_launchunit.py.
"""
import collections
import os
import re
import shlex

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY_PROG_RE = re.compile(r"^py(?:thon)?[\d.]*(?:\.exe)?$", re.I)
# modules whose `py -m <mod> X` only READS X - the only ones whose arguments are not launch units, on all three paths.
# Exactly the two lists already accepted: stop_record.PY_READONLY_MODULES and guard_bash.LINT_SEG_RE (card 103-4 review:
# an unknown module stays "build", selftest_c103d_hooks.py S7).
READONLY_MODULES = frozenset(("py_compile", "ast", "tokenize", "tabnanny", "pyflakes", "pycodestyle"))
_SEG_SPLIT_RE = re.compile(r"\s*(?:&&|\|\||;|\||\r?\n|(?<![>&])&(?![&>]))\s*")   # + a lone `&` (bash background,
_PLAIN_ARG_RE = re.compile(r"^(?:[\w./\\:-]+|2>&1)$")                                # cmd.exe; not 2>&1 / &> / &&)
_CONT_RE = re.compile(r"(?:\\|`)[ \t]*\r?\n")
_CD_RE = re.compile(r"^[ \t(]*cd[ \t]+(\"[^\"\n]*\"|'[^'\n]*'|[^\s\"']+)[ \t]*$", re.I)
_ENV_PREFIX_RE = re.compile(r"^\s*(?:\$env:)?\w+\s*=")


def segments(cmd):
    """The command split into shell segments (&& || ; | newline), a line continuation (bash `\\`, PowerShell backtick)
    joined first - the split stage_prerun.launched_py used since card 106-5."""
    return _SEG_SPLIT_RE.split(_CONT_RE.sub(" ", cmd or ""))


def _tokens(seg):
    try:
        toks = shlex.split(seg, posix=False)
    except ValueError:
        toks = seg.split()
    return [t.strip("\"'") for t in toks]


def norm(p, root=None):
    """A path token -> normcase absolute path (relative ones against root)."""
    return os.path.normcase(os.path.normpath(p if os.path.isabs(p) else os.path.join(root or ROOT, p)))


def module_file(mod, root=None):
    """The project file `-m <mod>` would run from the project root, or None (a/b -> a/b.py | a/b/__main__.py |
    a/b/__init__.py)."""
    if not mod or not re.match(r"^[\w.]+$", mod):
        return None
    base = os.path.join(root or ROOT, *mod.split("."))
    for c in (base + ".py", os.path.join(base, "__main__.py"), os.path.join(base, "__init__.py")):
        if os.path.isfile(c):
            return os.path.normpath(c)
    return None


def units(cmd, root=None):
    """Every python unit of the command: dicts {kind: 'script'|'module'|'module_arg', path, module, seg}.
    'script' = `py [flags] X.py` (X runs); 'module' = the project file a `-m` module resolves to (it runs);
    'module_arg' = a .py token after `py -m <module>` - a launch only when the module is in RUNNER_MODULES."""
    root = root or ROOT
    out = []
    for seg in segments(cmd):
        toks = _tokens(seg)
        i = 0
        while i < len(toks):
            if not PY_PROG_RE.match(os.path.basename(toks[i])):
                i += 1
                continue
            j, mod = i + 1, None
            while j < len(toks) and toks[j].startswith("-"):
                if toks[j] == "-m" or (toks[j].startswith("-m") and len(toks[j]) > 2):
                    if toks[j] == "-m":
                        mod, j = (toks[j + 1] if j + 1 < len(toks) else ""), j + 2
                    else:
                        mod, j = toks[j][2:], j + 1
                    break
                j += 2 if toks[j] in ("-X", "-W") else 1
            if mod is not None:
                mf = module_file(mod, root)
                if mf:
                    out.append({"kind": "module", "path": mf, "module": mod, "seg": seg})
                k = j
                while k < len(toks) and not PY_PROG_RE.match(os.path.basename(toks[k])):
                    if toks[k].lower().endswith(".py"):
                        p = toks[k] if os.path.isabs(toks[k]) else os.path.join(root, toks[k])
                        out.append({"kind": "module_arg", "path": os.path.normpath(p), "module": mod, "seg": seg})
                    k += 1
                i = k                      # a later `py` token in the segment (e.g. after bgrun's `--`) is scanned again
                continue
            if j < len(toks):
                p = toks[j]
                if p.lower().endswith(".py"):
                    out.append({"kind": "script", "path": os.path.normpath(p if os.path.isabs(p) else os.path.join(root, p)),
                                "module": None, "seg": seg})
                i = j + 1
                continue
            i += 1
    return out


def arg_is_launch(mod, root=None):
    """True unless `-m <mod>` only READS its arguments: mod in READONLY_MODULES and not a project-file shadow."""
    return (mod or "").lower() not in READONLY_MODULES or bool(module_file(mod, root))


def launched_py(cmd, root=None):
    """Every script path the command RUNS: `py X.py` (past interpreter flags, also after bgrun's `--`), a `-m` module
    that is a project file, and the path arguments of any `-m` module not in READONLY_MODULES. Order of appearance,
    duplicates kept."""
    return [u["path"] for u in units(cmd, root)
            if u["kind"] in ("script", "module") or (u["kind"] == "module_arg" and arg_is_launch(u["module"], root))]


def module_arg_counts(cmd, root=None):
    """Counter {norm(path): n} of the .py tokens that are only ARGUMENTS of a read-only `-m` module."""
    return collections.Counter(norm(u["path"], root) for u in units(cmd, root)
                               if u["kind"] == "module_arg" and not arg_is_launch(u["module"], root))


def drop_module_args(cmd, paths, root=None):
    """The card-flag filter (guard_card): `paths` = one entry per place another detector saw a launched .py. An entry
    is dropped only when (a) this module does not see that path launched anywhere in the command and (b) the other
    detector saw it no more often than it appears as a non-runner module argument - so a second, smuggled occurrence
    (e.g. inside a quoted `cmd /c "py X.py"`) keeps the path."""
    marg = module_arg_counts(cmd, root)
    if not marg:
        return list(paths)
    launched = set(norm(p, root) for p in launched_py(cmd, root))
    seen = collections.Counter(norm(p, root) for p in paths)
    return [p for p in paths if not (norm(p, root) in marg and norm(p, root) not in launched
                                     and seen[norm(p, root)] <= marg[norm(p, root)])]


def _cd_dir(arg):
    a = arg.strip("'\"").replace("\\", "/")
    m = re.match(r"^/([A-Za-z])(/.*)?$", a)                      # msys / git-bash `/g/Codes/...`
    if m:
        a = m.group(1) + ":" + (m.group(2) or "/")
    return os.path.normcase(os.path.normpath(os.path.abspath(a)))


def cd_only_to_root(cmd, root=None):
    """True when every `cd` segment of the command targets the project root (or there is none)."""
    want = os.path.normcase(os.path.normpath(root or ROOT))
    for seg in segments(cmd):
        m = _CD_RE.match(seg)
        if m and _cd_dir(m.group(1)) != want:
            return False
        if not m and re.match(r"^[ \t(]*(?:cd|pushd|set-location|sl|chdir)\b", seg, re.I):
            return False                                          # an unparsed cd form: fail closed
    return True


def module_arg_segment(seg, whole_cmd="", root=None):
    """stop_record's read-only credit for ONE segment: it is exactly `py[thon][N.N][.exe] [flags] -m <module> args`
    with no env prefix, the module is in READONLY_MODULES and not a project file (no shadow), every argument is a plain
    path-ish word, and the whole command cd's nowhere but the project root. Then every path in it is only READ."""
    if _ENV_PREFIX_RE.match(seg or ""):
        return False
    toks = _tokens(seg or "")
    if not toks or not PY_PROG_RE.match(os.path.basename(toks[0])):
        return False
    j = 1
    mod = None
    while j < len(toks) and toks[j].startswith("-"):
        if toks[j] == "-m":
            mod = toks[j + 1] if j + 1 < len(toks) else None
            break
        if toks[j].startswith("-m") and len(toks[j]) > 2:
            mod = toks[j][2:]
            break
        j += 2 if toks[j] in ("-X", "-W") else 1
    if not mod or arg_is_launch(mod, root):
        return False
    try:                                                        # the RAW tokens (quotes kept): every argument must be
        raw = shlex.split(seg, posix=False)                       # a plain path-ish word (or 2>&1) - a quote, `&`, `>`,
    except ValueError:                                            # `$`, `=` may hide a second command (guard_bash
        return False                                              # LINT_SEG_RE's argument rule, card 103-4 review)
    k = raw.index(toks[j]) if toks[j] in raw else j               # the -m / -mX token
    rest = raw[k + (2 if toks[j] == "-m" else 1):]
    if not all(_PLAIN_ARG_RE.match(t) for t in rest):
        return False
    if any(PY_PROG_RE.match(os.path.basename(t)) for t in rest):
        return False                                              # a second interpreter inside the segment
    return cd_only_to_root(whole_cmd or seg, root)
