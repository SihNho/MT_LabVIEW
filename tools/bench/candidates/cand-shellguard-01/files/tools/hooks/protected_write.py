# ---
# labview: none
# hardware: none
# ---
"""protected_write.py - ONE decision for writes to PROTECTED files, called by guard_bash (shell), guardcore (Codex
write/patch) and guard_card (Claude Write/Edit). CANDIDATE, card chat-X9 (discussion structure-equal-02 round 10, both
sides STATE agreed: "셸 허용은 rules_apply apply <id>만" / "반영 허용은 명령 이름뿐 아니라 실행 버전·합의 묶음·대상·시험 결과
확인" / settings.local.json "모든 에이전트 쓰기(Write/Edit/patch/셸) 거부").

    shell_decision(cmd, cwd, root=None, shell=None) -> reason | None     every shell form, Claude and Codex alike
    agent_write_decision(paths, cwd, root=None)   -> reason | None     Write/Edit/patch: only agent_write_denied

Lists come from <root>/tools/rules_protected.json (the ONE place): `globs` (minus `exclude`) and `chain_checked` (the
ledger) may be written by a shell ONLY through the exact command `py tools/rules_apply.py apply <bundle-id>`, and only
when <root>/tools/rules_apply.py has the md5 the bundle names, the bundle exists and rules_apply.check() passes (agreement
token of THIS bundle in both relay files, bundle hash, targets protected and listed, tests PASS, token unused, chain
intact). `agent_write_denied` (.claude/settings.local.json) is refused for every tool and every form, rules_apply
included. VERIFICATION LEVEL: command TEXT is judged (redirection, write cmdlets/commands and their path arguments,
git checkout/restore/rm/mv/reset --hard/stash, nested shells, inline interpreter code); a script that writes a protected
file from inside is invisible here - the post-hoc `rules_apply.py audit` (hash chain + md5) is the backstop.
PRIOR ART: tools/hooks/guardcore.py (path rules R1-R3, judge per event), tools/rules_apply.py (lists, globs, check);
no earlier shell write-target parser in tools/ (grep "Set-Content" tools/hooks: only guard text). Self-test:
tools/bench/selftest_shellguard_cand.py.
"""
import base64
import hashlib
import importlib.util
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
PROTECTED_REL = "tools/rules_protected.json"
RULES_APPLY_REL = "tools/rules_apply.py"


def find_root(start=HERE):
    """The nearest ancestor of `start` holding tools/rules_protected.json (the repo root once installed)."""
    d = os.path.abspath(start)
    while True:
        if os.path.isfile(os.path.join(d, PROTECTED_REL)):
            return d
        up = os.path.dirname(d)
        if up == d:
            return None
        d = up


def _glob_re(g):
    out, i = "", 0
    while i < len(g):
        if g.startswith("**/", i):
            out, i = out + "(?:.*/)?", i + 3
        elif g.startswith("**", i):
            out, i = out + ".*", i + 2
        elif g[i] == "*":
            out, i = out + "[^/]*", i + 1
        elif g[i] == "?":
            out, i = out + "[^/]", i + 1
        else:
            out, i = out + re.escape(g[i]), i + 1
    return re.compile("^" + out + "$", re.I)


def load_lists(root):
    """{globs, exclude, chain_checked, agent_write_denied} from the protected list, or None when unreadable."""
    try:
        with open(os.path.join(root, PROTECTED_REL), encoding="utf-8") as f:
            d = json.load(f)
        return {k: list(d.get(k) or []) for k in ("globs", "exclude", "chain_checked", "agent_write_denied")}
    except (OSError, ValueError, TypeError):
        return None


def _prefix(g):
    """Literal leading part of a glob (up to the first wildcard), lower-case."""
    m = re.search(r"[*?\[]", g)
    return (g[:m.start()] if m else g).lower()


def classify(rel, L):
    """'agent_denied' | 'chain' | 'protected' | None for a clean repo-relative path."""
    r = rel.replace("\\", "/")
    if any(_glob_re(g).match(r) for g in L["agent_write_denied"]):
        return "agent_denied"
    if any(_glob_re(g).match(r) for g in L["chain_checked"]):
        return "chain"
    if any(_glob_re(g).match(r) for g in L["globs"]) and not any(_glob_re(g).match(r) for g in L["exclude"]):
        return "protected"
    return None


def _contains_protected(rel, L):
    """True when directory `rel` ('' = repo root) holds protected paths (a recursive delete/move would hit them)."""
    r = rel.rstrip("/").lower()
    pre = r + "/" if r else ""
    return any(_prefix(g).startswith(pre) for g in L["globs"] + L["chain_checked"] + L["agent_write_denied"])


def to_rel(token, cwd, root):
    """Repo-relative path for a path-like token, or None (outside the root, empty, a URL, a variable, a device)."""
    t = (token or "").strip().strip("'\"").strip()
    t = re.sub(r"^(?:-[A-Za-z]+:|of=|--output=|--target-directory=)", "", t)
    if not t or "://" in t or t.startswith(("$", "%", "&")) or t.lower() in ("nul", "$null", "/dev/null", "-"):
        return None
    t = t.replace("\\\\", "\\").replace("\\", "/")
    m = re.match(r"^/([a-zA-Z])/(.*)$", t)               # git-bash /g/Codes/... -> G:/Codes/...
    if m:
        t = m.group(1) + ":/" + m.group(2)
    p = t if (os.path.isabs(t) or re.match(r"^[A-Za-z]:", t)) else os.path.join(cwd or root, t)
    p = os.path.normpath(p)
    try:
        rel = os.path.relpath(p, root).replace("\\", "/")
    except ValueError:
        return None
    if rel == "." :
        return ""
    if rel.startswith("../") or rel == "..":
        return None
    return rel


def path_hit(token, cwd, root, L, recursive=False):
    """(rel, class) when the token names a protected path (or, with recursive, a directory holding one / a wildcard
    reaching one), else None."""
    rel = to_rel(token, cwd, root)
    if rel is None:
        return None
    if re.search(r"[*?\[]", rel):
        pre, tre = _prefix(rel), _glob_re(rel)
        for g in L["globs"] + L["chain_checked"] + L["agent_write_denied"]:
            if not re.search(r"[*?\[]", g):
                if tre.match(g):                   # the wildcard reaches a literal protected file
                    return rel, "wildcard"
                continue
            gp = _prefix(g)
            if gp.startswith(pre) or pre.startswith(gp):
                return rel, "wildcard"
        return None
    c = classify(rel, L) if rel else None
    if c:
        return rel, c
    if recursive and _contains_protected(rel, L):
        return rel, "directory"
    return None


# ------------------------------------------------------------------ tokenizer
OPS = ("&&", "||", ";", "|", "&", "\n", "(", ")", "{", "}")


def tokenize(cmd):
    """Segments of a command line: [{"words": [str], "redirs": [str], "heredocs": [str], "quoted": [str]}].
    Quotes group words; backslash is literal (Windows paths); `>`/`>>`/`N>`/`*>` record a write target (`>&1` none);
    `<<MARK` records the heredoc body. Crude on purpose: text, not a shell."""
    segs, cur, word, i, n = [], None, None, 0, len(cmd)

    def new():
        return {"words": [], "redirs": [], "heredocs": [], "quoted": []}

    cur = new()

    def flush():
        nonlocal word
        if word is not None:
            cur["words"].append(word)
        word = None

    while i < n:
        c = cmd[i]
        if c in "'\"":
            j = cmd.find(c, i + 1)
            j = n if j < 0 else j
            word = (word or "") + cmd[i + 1:j]
            cur["quoted"].append(cmd[i + 1:j])
            i = j + 1
            continue
        if c == ">" or (c in "0123456789*" and i + 1 < n and cmd[i + 1] == ">" and word is None):
            flush()
            if c != ">":
                i += 1
            i += 1
            if i < n and cmd[i] == ">":
                i += 1
            if i < n and cmd[i] == "|":
                i += 1
            while i < n and cmd[i] in " \t":
                i += 1
            if i < n and cmd[i] == "&":           # 2>&1
                i += 1
                while i < n and cmd[i].isalnum():
                    i += 1
                continue
            if i < n and cmd[i] in "'\"":
                q = cmd[i]
                j = cmd.find(q, i + 1)
                j = n if j < 0 else j
                cur["redirs"].append(cmd[i + 1:j])
                i = j + 1
            else:
                m = re.match(r"[^\s;&|<>()]+", cmd[i:])
                if m:
                    cur["redirs"].append(m.group(0))
                    i += m.end()
            continue
        if c == "<" and cmd.startswith("<<", i):
            flush()
            m = re.match(r"<<-?\s*['\"]?(\w+)['\"]?", cmd[i:])
            if m:
                mark = m.group(1)
                eol = cmd.find("\n", i)
                end = re.search(r"(?m)^\s*" + re.escape(mark) + r"\s*$", cmd[eol + 1:]) if eol >= 0 else None
                body = cmd[eol + 1:eol + 1 + end.start()] if end else (cmd[eol + 1:] if eol >= 0 else "")
                cur["heredocs"].append(body)
                i += m.end()
                if eol >= 0:                       # the rest of the heredoc line stays in this segment
                    rest = cmd[i:eol]
                    cmd = cmd[:i] + rest + "\n" + (cmd[eol + 1 + end.end():] if end else "")
                    n = len(cmd)
                continue
            i += 2
            continue
        if c in " \t\r":
            flush()
            i += 1
            continue
        op = next((o for o in OPS if cmd.startswith(o, i)), None)
        if op:
            flush()
            if cur["words"] or cur["redirs"] or cur["heredocs"]:
                segs.append(cur)
            cur = new()
            i += len(op)
            continue
        if c == "`" and i + 1 < n and cmd[i + 1] in "\r\n":   # PowerShell line continuation
            i += 2
            continue
        word = (word or "") + c
        i += 1
    flush()
    if cur["words"] or cur["redirs"] or cur["heredocs"]:
        segs.append(cur)
    return segs


# ------------------------------------------------------------------ verbs
ALL_ARGS = {"rm", "del", "erase", "rd", "rmdir", "unlink", "touch", "truncate", "tee", "remove-item", "ri",
            "set-content", "sc", "add-content", "ac", "out-file", "new-item", "ni", "clear-content", "clc",
            "tee-object", "mkdir", "md", "shred", "chmod", "attrib", "icacls", "takeown"}
RECURSIVE = {"rm", "del", "erase", "rd", "rmdir", "remove-item", "ri", "shred"}
DEST = {"cp", "copy", "copy-item", "cpi", "install", "ln", "xcopy", "robocopy", "scp", "rsync"}
BOTH = {"mv", "move", "move-item", "mi", "rename-item", "rni", "ren", "rename"}
INPLACE = {"sed", "perl", "ruby"}
SHELLS = {"bash", "sh", "zsh", "dash", "powershell", "pwsh", "cmd"}
PYTHONS = {"py", "python", "python3", "pythonw", "node", "perl", "ruby", "deno"}
PS_VALUE = {"-path", "-literalpath", "-filepath", "-destination", "-value", "-name", "-newname", "-itemtype",
            "-encoding", "-filter", "-include", "-exclude", "-stream", "-inputobject", "-width", "-credential",
            "-target", "-pspath", "-delimiter", "-outfile", "-o", "--output", "-s", "--size", "-t",
            "--target-directory", "-e", "-c", "-m"}
PS_TARGET = ("-path", "-literalpath", "-filepath", "-destination", "-pspath", "-outfile", "-o", "--output", "-t",
             "--target-directory", "-target")
WRAPPERS = {"sudo", "env", "nohup", "time", "exec", "call", "start", "start-process", "&", ".", "command",
            "invoke-expression", "iex"}
WRITE_API_RE = re.compile(
    r"open\s*\([^)]*,\s*(?:mode\s*=\s*)?['\"]r?[wax+]|write_text|write_bytes|\.write\s*\(|shutil\.|os\.(?:remove|unlink|rename|replace|"
    r"rmdir|removedirs|truncate|makedirs|mkdir|chmod)|\.(?:unlink|rename|replace|touch|rmdir|mkdir)\s*\(|copyfile|"
    r"writeFile|appendFile|unlinkSync|rmSync|renameSync|copyFileSync|WriteAll|AppendAll|File\]::|subprocess|"
    r"os\.system|Popen|check_call|check_output|\brun\s*\(", re.I)
NET_FILE_RE = re.compile(r"\[(?:System\.)?IO\.(?:File|Directory)\]::\s*(?:Write|Append|Delete|Copy|Move|Replace|"
                         r"Create|Open|SetAttributes)", re.I)


def _verb(w):
    b = re.split(r"[\\/]", w)[-1].lower()
    return re.sub(r"\.(?:exe|cmd|bat|ps1)$", "", b)


def _parse_args(words):
    """(positionals, {param: value}) - PowerShell/GNU style; unknown -flags are switches."""
    pos, kv, i = [], {}, 0
    while i < len(words):
        w = words[i]
        lw = w.lower()
        if lw.startswith("--") and "=" in lw:
            k, v = w.split("=", 1)
            kv.setdefault(k.lower(), []).append(v)
        elif re.match(r"^-[A-Za-z][\w-]*:.+", w) and not re.match(r"^-[A-Za-z]:[\\/]", w):
            k, v = w.split(":", 1)
            kv.setdefault(k.lower(), []).append(v)
        elif lw in PS_VALUE and i + 1 < len(words):
            kv.setdefault(lw, []).append(words[i + 1])
            i += 1
        elif lw.startswith("-") and len(lw) > 1:
            pass
        else:
            pos.append(w)
        i += 1
    return pos, kv


def _targets(verb, args, cwd):
    """(write-target tokens, recursive?) for one write verb."""
    pos, kv = _parse_args(args)
    named = [v for k in PS_TARGET for v in kv.get(k, [])]
    if verb in ("new-item", "ni") and kv.get("-name"):
        base = (kv.get("-path") or pos[:1] or ["."])[0]
        return [os.path.join(base, kv["-name"][0])], False
    if verb in ("rename-item", "rni", "ren", "rename"):
        src = (kv.get("-path") or kv.get("-literalpath") or pos[:1] or [""])[0]
        new = (kv.get("-newname") or pos[1:2] or [""])[0]
        return [src, os.path.join(os.path.dirname(src.replace("\\", "/")), new) if new else ""], False
    if verb in ALL_ARGS:
        if verb in ("set-content", "sc", "add-content", "ac", "out-file", "new-item", "ni", "clear-content", "clc"):
            return (named or pos[:1]), False
        return named + pos, verb in RECURSIVE
    if verb in BOTH:
        return named + pos, True
    if verb in DEST:
        if named:
            dests = named
        elif verb == "robocopy":
            dests = pos[1:2]
        else:
            dests = pos[-1:] if len(pos) >= 2 else []
        out = list(dests)
        srcs = [p for p in pos if p not in dests]
        for d in dests:
            dd = d if os.path.isabs(d) else os.path.join(cwd, d)
            if os.path.isdir(dd):
                out += [os.path.join(d, os.path.basename(s.replace("\\", "/").rstrip("/"))) for s in srcs]
        return out, False
    return [], False


def _code_hits(code, cwd, root, L):
    """Protected names mentioned in inline interpreter code (quoted strings, tokens, literal list prefixes)."""
    norm = (code or "").replace("\\\\", "/").replace("\\", "/")
    hits = []
    for tok in re.findall(r"""['"]([^'"]+)['"]|([\w./:-]+)""", norm):
        t = tok[0] or tok[1]
        if to_rel(t, cwd, root) in (None, ""):
            continue
        h = path_hit(t, cwd, root, L, recursive=bool(tok[0]))     # a quoted directory name may be a delete target
        if h:
            hits.append(h[0])
    low = norm.lower()
    for g in L["globs"] + L["chain_checked"] + L["agent_write_denied"]:
        p = _prefix(g).rstrip("/")
        if p and p.lower() in low:
            hits.append(p)
    return hits


def _reason(what, rel, cls):
    if cls == "agent_denied":
        return ("protected file %s: the user's own settings - every agent write is refused (Write/Edit/patch/shell, "
                "rules_apply included; discussion structure-equal-02 round 10). The user edits it by hand." % rel)
    return ("shell write to a protected file (%s via %s, class %s). Protected files (tools/rules_protected.json) change "
            "only through `py tools/rules_apply.py apply <bundle-id>` after both debaters agree "
            "(discussion structure-equal-02 round 10)." % (rel, what, cls))


# ------------------------------------------------------------------ rules_apply exception
APPLY_RE = re.compile(r"^\s*(?:py|python3?)(?:\.exe)?\s+(?:-u\s+)?"
                      r"(?:\"(?P<p1>[^\"]*rules_apply\.py)\"|'(?P<p2>[^']*rules_apply\.py)'|(?P<p3>[^'\"\s]*rules_apply\.py))"
                      r"\s+apply\s+(?P<id>[A-Za-z0-9._-]+@[0-9a-f]{8})\s*$", re.I)


def _md5(path):
    if not os.path.isfile(path):
        return None
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _load_rules_apply(root):
    """The rules_apply module loaded from <root>/tools/rules_apply.py (the file whose md5 was just checked)."""
    spec = importlib.util.spec_from_file_location("rules_apply_live_%s" % hashlib.md5(root.encode()).hexdigest()[:8],
                                                  os.path.join(root, RULES_APPLY_REL))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def apply_exception(cmd, cwd, root):
    """(matched, reason). matched=True when the WHOLE command is the exact apply form; reason None = allowed."""
    m = APPLY_RE.match(cmd or "")
    if not m:
        return False, None
    path = m.group("p1") or m.group("p2") or m.group("p3")
    if to_rel(path, cwd, root) != RULES_APPLY_REL:
        return True, ("rules_apply apply must run THE project copy %s, not %s" % (RULES_APPLY_REL, path))
    bid = m.group("id")
    cid = bid.split("@", 1)[0]
    mp = os.path.join(root, "tools", "bench", "candidates", cid, "manifest.json")
    try:
        with open(mp, encoding="utf-8") as f:
            man = json.load(f)
    except (OSError, ValueError) as e:
        return True, "bundle %s does not exist (%s)" % (bid, e)
    live = _md5(os.path.join(root, RULES_APPLY_REL))
    if not live or live != man.get("rules_apply_md5"):
        return True, ("tools/rules_apply.py md5 %s differs from the version bundle %s names (%s) - a changed apply "
                      "device does not run" % (live, bid, man.get("rules_apply_md5")))
    try:
        RA = _load_rules_apply(root)
        gates = RA.check(root, bid)
    except Exception as e:     # noqa: BLE001 - fail closed
        return True, "rules_apply.check(%s) could not run: %s: %s" % (bid, type(e).__name__, str(e)[:200])
    bad = [n for n, ok, _ in gates if not ok]
    if bad:
        return True, "bundle %s does not pass rules_apply check: %s" % (bid, ", ".join(bad[:6]))
    return True, None


# ------------------------------------------------------------------ decisions
def shell_decision(cmd, cwd=None, root=None, shell=None, _depth=0):
    """Reason string when the command writes a protected path (or runs rules_apply apply outside the exact allowed
    form), None when it may run. Nested shells and inline code are scanned recursively (depth 3)."""
    root = root or find_root()
    if not root or not cmd or _depth > 3:
        return None
    cwd = cwd or root
    L = load_lists(root)
    if L is None:
        if re.search(r">|Set-Content|Add-Content|Out-File|Remove-Item|\brm\b|\bmv\b|\bcp\b", cmd, re.I):
            return "protected list %s unreadable - write-shaped command refused (fail closed)" % PROTECTED_REL
        return None
    matched, why = apply_exception(cmd, cwd, root) if _depth == 0 else (False, None)
    if matched:
        return why
    for seg in tokenize(cmd):
        words = list(seg["words"])
        while words and (re.match(r"^\$?(?:env:)?[A-Za-z_]\w*=", words[0]) or _verb(words[0]) in WRAPPERS):
            words.pop(0)
        for r in seg["redirs"]:
            h = path_hit(r, cwd, root, L)
            if h:
                return _reason("redirection >", *h)
        raw = " ".join(seg["words"])
        if NET_FILE_RE.search(raw):
            for q in seg["quoted"] + seg["words"]:
                h = path_hit(q, cwd, root, L)
                if h:
                    return _reason(".NET File/Directory call", *h)
        if not words:
            continue
        v, args = _verb(words[0]), words[1:]
        if v in ("cd", "set-location", "sl", "pushd", "chdir") and args:
            nd = args[0] if os.path.isabs(args[0].strip("'\"")) else os.path.join(cwd, args[0])
            cwd = os.path.normpath(nd.strip("'\""))
            continue
        if any(re.search(r"(?:^|[\\/])rules_apply\.py$", w, re.I) for w in words[:3]) or (
                v in PYTHONS and "-m" in args and "rules_apply" in args):
            low = [a.lower() for a in args]
            if "apply" in low or ("--baseline" in low and "--dry" not in low):
                rootarg = next((args[i + 1] for i, a in enumerate(args[:-1]) if a == "--root"), None)
                if rootarg is None or to_rel(rootarg, cwd, root) == "":
                    return ("rules_apply apply / audit --baseline only as the exact whole command "
                            "`py tools/rules_apply.py apply <bundle-id>` (the project copy, nothing before or after it, "
                            "no --root on the real tree); the genesis baseline is written before activation")
            continue
        if v in SHELLS:
            for i, a in enumerate(args):
                al = a.lower()
                if al in ("-c", "-lc", "/c", "/k", "-command", "-commandwithargs") and i + 1 < len(args):
                    why = shell_decision(" ".join(args[i + 1:]), cwd, root, None, _depth + 1)
                    if why:
                        return why
                    break
                if al in ("-encodedcommand", "-enc", "-e", "-ec") and i + 1 < len(args):
                    try:
                        dec = base64.b64decode(args[i + 1]).decode("utf-16-le")
                    except Exception:      # noqa: BLE001
                        return "undecodable -EncodedCommand - refused (fail closed)"
                    why = shell_decision(dec, cwd, root, None, _depth + 1)
                    if why:
                        return why
            continue
        if v in PYTHONS:
            code = None
            for i, a in enumerate(args):
                if a in ("-c", "-e") and i + 1 < len(args):
                    code = args[i + 1]
                    break
            if code is None and (("-" in args) or not [a for a in args if not a.startswith("-")]) and seg["heredocs"]:
                code = "\n".join(seg["heredocs"])
            if code is not None:
                if "rules_apply" in code:
                    return "rules_apply runs only as `py tools/rules_apply.py apply <bundle-id>`, not from inline code"
                if WRITE_API_RE.search(code):
                    hits = _code_hits(code, cwd, root, L)
                    if hits:
                        return ("inline %s code that writes and names a protected path (%s) - refused (shell write "
                                "to a protected file; text check, conservative)" % (v, hits[0]))
            if v in ("perl", "ruby") and any(a.startswith("-i") or a == "-pi" for a in args):
                for a in args:
                    h = path_hit(a, cwd, root, L)
                    if h:
                        return _reason(v + " -i", *h)
            continue
        if v == "git" and args:
            sub = args[0].lower()
            rest = args[1:]
            if sub in ("checkout", "restore", "rm", "mv", "clean", "stash", "reset"):
                if sub == "reset" and not any(a in ("--hard", "--merge", "--keep") for a in rest):
                    continue
                if sub == "stash" and rest and rest[0] in ("list", "show"):
                    continue
                if sub in ("reset", "stash"):
                    return ("git %s can rewrite protected files in the working tree - refused while the shell guard "
                            "is on (restore = an approved bundle via rules_apply, or the pre-install state)" % sub)
                after = rest[rest.index("--") + 1:] if "--" in rest else rest
                for a in after:
                    if a in (".", ":/", "*", ":(top)"):
                        return _reason("git %s %s" % (sub, a), a, "directory")
                    h = path_hit(a, cwd, root, L, recursive=sub in ("rm", "mv", "clean", "checkout", "restore"))
                    if h:
                        return _reason("git " + sub, *h)
            continue
        if v == "dd":
            for a in args:
                if a.lower().startswith("of="):
                    h = path_hit(a[3:], cwd, root, L)
                    if h:
                        return _reason("dd of=", *h)
            continue
        if v in ("curl", "wget", "invoke-webrequest", "iwr", "invoke-restmethod", "irm", "tar", "expand-archive",
                 "unzip", "7z"):
            pos, kv = _parse_args(args)
            for k in ("-o", "--output", "-outfile", "-destinationpath", "-c", "-d", "-O"):
                for t in kv.get(k.lower(), []):
                    h = path_hit(t, cwd, root, L, recursive=True)
                    if h:
                        return _reason(v, *h)
            continue
        if v in INPLACE:
            if any(a == "-i" or a.startswith("-i") or a.startswith("--in-place") for a in args):
                for a in args:
                    h = path_hit(a, cwd, root, L)
                    if h:
                        return _reason(v + " -i", *h)
            continue
        if v in ALL_ARGS or v in DEST or v in BOTH:
            tg, rec = _targets(v, args, cwd)
            for t in tg:
                h = path_hit(t, cwd, root, L, recursive=rec)
                if h:
                    return _reason(words[0], *h)
    return None


def agent_write_decision(paths, cwd=None, root=None):
    """Reason when any written path (old or new side) is on `agent_write_denied`, else None. Write/Edit/patch tools."""
    root = root or find_root()
    if not root:
        return None
    L = load_lists(root)
    if L is None:
        return None
    for e in paths or []:
        for side in ("old", "new"):
            p = e.get(side) if isinstance(e, dict) else (e if side == "new" else None)
            if not p:
                continue
            rel = to_rel(p, cwd or root, root)
            if rel and classify(rel, L) == "agent_denied":
                return _reason("%s tool" % (e.get("op") if isinstance(e, dict) else "write"), rel, "agent_denied")
    return None
