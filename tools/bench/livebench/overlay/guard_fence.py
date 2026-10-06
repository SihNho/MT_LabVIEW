# ---
# labview: none
# hardware: none
# ---
r"""guard_fence - livebench SHELL write fence (card chat-B7; chat decision 2026-10-06: close the fence gap before any
arm runs). Installed ONLY in a bench worktree (<wt>/.livebench/guard_fence.py, registered first in that worktree's
.claude/settings.json PreToolUse Bash|PowerShell); never in the main repo. The Python write fence (sitecustomize) covers
Python file writes; this covers Bash / PowerShell commands; lb_run's post-cycle snapshots stay the backstop.

REFUSES (exit 2, stderr "BLOCKED by .livebench/guard_fence.py ...") a command that WRITES to
  * the claudeDev root outside claudeDev\bench\<arm>\ (the Moving Objects fixture excepted, as in sitecustomize), or
  * the main project folder,
where "writes" = an output redirect (> >> 2> &>) to such a path; the DESTINATION of cp / copy / Copy-Item / xcopy /
robocopy / rsync / scp / ln; ANY path argument of rm / mv / Move-Item / Remove-Item / Rename-Item / New-Item / mkdir /
touch / tee / Tee-Object / Set-Content / Add-Content / Out-File / Clear-Content / sed -i / truncate / chmod; a git
write subcommand (add, commit, checkout, reset, stash, rm, mv, clean, merge, pull, push, worktree, branch, tag, rebase,
restore, switch, apply, am, cherry-pick, revert) run on the main project (-C <main> or cwd inside it); a .NET file
write ([IO.File]::Write*/Append*/Copy/Move/Delete/Create) naming such a path. Reads (ls, cat, md5sum, grep, git log,
cp FROM the root INTO the arm folder) pass. Paths: quotes stripped, /c/... and C:/... forms normalised, relative paths
resolved against the payload's cwd. Variables ($x) cannot be resolved here: the Python fence and the snapshots cover
them. Every refusal is appended to LIVEBENCH_WRITELOG (event "shell") so lb_collect counts it.
Config: <this dir>/arm.json env (LIVEBENCH_CLAUDEDEV, LIVEBENCH_CLAUDEDEV_ROOT, LIVEBENCH_MAIN, LIVEBENCH_WRITELOG).
  py guard_fence.py --selftest     refuse + allow cases against this worktree's config"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
try:
    CFG = json.load(open(os.path.join(HERE, "arm.json"), encoding="utf-8"))
except (OSError, ValueError):
    CFG = {}
ENV = CFG.get("env") or {}
OUT = ENV.get("LIVEBENCH_CLAUDEDEV") or os.environ.get("LIVEBENCH_CLAUDEDEV") or ""
ROOT = ENV.get("LIVEBENCH_CLAUDEDEV_ROOT") or os.environ.get("LIVEBENCH_CLAUDEDEV_ROOT") or ""
MAIN = ENV.get("LIVEBENCH_MAIN") or os.environ.get("LIVEBENCH_MAIN") or ""
WLOG = ENV.get("LIVEBENCH_WRITELOG") or os.environ.get("LIVEBENCH_WRITELOG") or ""

ALL_ARGS = {"rm", "rmdir", "del", "erase", "rd", "mv", "move", "move-item", "mi", "remove-item", "ri", "rename-item",
            "ren", "rni", "new-item", "ni", "mkdir", "md", "touch", "tee", "tee-object", "set-content", "sc",
            "add-content", "ac", "out-file", "clear-content", "clc", "truncate", "chmod", "install", "unlink"}
DEST_ONLY = {"cp", "copy", "copy-item", "cpi", "xcopy", "rsync", "scp", "ln"}
GIT_WRITE = {"add", "commit", "checkout", "reset", "stash", "rm", "mv", "clean", "merge", "pull", "push", "worktree",
             "branch", "tag", "rebase", "restore", "switch", "apply", "am", "cherry-pick", "revert"}
NET_WRITE_RE = re.compile(r"\[(?:System\.)?IO\.(?:File|Directory)\]::(?:Write|Append|Copy|Move|Delete|Create|Replace)", re.I)


def _norm(p):
    return os.path.normcase(os.path.abspath(p)) if p else ""


N_OUT, N_ROOT, N_MAIN = _norm(OUT), _norm(ROOT), _norm(MAIN)
N_FIX = os.path.join(N_ROOT, "niscriptingexamples", "moving objects") if N_ROOT else ""


def _under(p, d):
    return bool(d) and (p == d or p.startswith(d.rstrip("\\/") + os.sep))


def classify(path):
    if not path:
        return None
    if _under(path, N_OUT):
        return "arm"
    if _under(path, N_FIX):
        return "fixture"
    if _under(path, N_ROOT):
        return "outside"
    if _under(path, N_MAIN):
        return "main"
    return None


def resolve(tok, cwd):
    t = tok.strip().strip("'\"")
    if not t or t.startswith(("$", "-", "~", "%")) or "$(" in t:
        return None
    m = re.match(r"^/([A-Za-z])(/.*)?$", t)
    if m:
        t = m.group(1).upper() + ":" + (m.group(2) or "/")
    t = t.replace("/", "\\")
    if not re.match(r"^[A-Za-z]:\\", t):
        if not cwd:
            return None
        t = os.path.join(cwd, t)
    return _norm(t)


def split_segments(cmd):
    """Split on ; && || | & and newlines OUTSIDE quotes; keep backslashes (Windows paths)."""
    segs, cur, q, i = [], [], None, 0
    while i < len(cmd):
        c = cmd[i]
        if q:
            cur.append(c)
            if c == q:
                q = None
        elif c in "'\"":
            q = c
            cur.append(c)
        elif c in ";|\n" or (c == "&" and not (cur and cur[-1] in "<>") and cmd[i + 1:i + 2] != ">"):
            segs.append("".join(cur))
            cur = []
            if cmd[i:i + 2] in ("&&", "||"):
                i += 1
        else:
            cur.append(c)
        i += 1
    segs.append("".join(cur))
    return [s.strip() for s in segs if s.strip()]


def tokens(seg):
    """Whitespace tokens outside quotes, quotes kept (resolve() strips them); a redirect operator is its own token."""
    out, cur, q = [], [], None
    i = 0
    while i < len(seg):
        c = seg[i]
        if q:
            cur.append(c)
            if c == q:
                q = None
        elif c in "'\"":
            q = c
            cur.append(c)
        elif c.isspace():
            if cur:
                out.append("".join(cur))
                cur = []
        elif c == ">":
            if cur and not re.fullmatch(r"\d|&", "".join(cur)):
                out.append("".join(cur))
            cur = []
            j = i
            while j + 1 < len(seg) and seg[j + 1] in ">&":
                j += 1
            out.append(">")
            i = j
        else:
            cur.append(c)
        i += 1
    if cur:
        out.append("".join(cur))
    return out


def targets(cmd, cwd):
    """[(path, why)] of every path this command would write."""
    hits = []
    for seg in split_segments(cmd):
        tk = tokens(seg)
        for k, t in enumerate(tk):
            if t == ">" and k + 1 < len(tk):
                hits.append((resolve(tk[k + 1], cwd), "redirect"))
        tk = [t for k, t in enumerate(tk) if t != ">" and not (k > 0 and tk[k - 1] == ">")]
        while tk and (re.match(r"^\w+=", tk[0]) or tk[0] in ("&", ".", "sudo", "command", "builtin", "exec")):
            tk = tk[1:]
        if not tk:
            continue
        verb = os.path.basename(tk[0].strip("'\"").replace("\\", "/")).lower()
        verb = re.sub(r"\.(exe|cmd|bat)$", "", verb)
        args = tk[1:]
        pos = [a for a in args if not a.startswith("-") and not re.match(r"^/[A-Za-z]$", a)]
        if verb == "git":
            g_cwd, sub, it = cwd, None, iter(range(len(args)))
            for k in it:
                a = args[k]
                if a == "-C" and k + 1 < len(args):
                    g_cwd = resolve(args[k + 1], cwd) or g_cwd
                    next(it, None)
                elif not a.startswith("-"):
                    sub = a.lower()
                    break
            if sub in GIT_WRITE:
                hits.append((_norm(g_cwd) if g_cwd else None, "git " + sub))
        elif verb in DEST_ONLY:
            dest = None
            for k, a in enumerate(args):
                m = re.match(r"^-destination(?::(.+))?$", a, re.I)
                if m:
                    dest = m.group(1) or (args[k + 1] if k + 1 < len(args) else None)
            if dest is None and pos:
                dest = pos[-1]
            hits.append((resolve(dest, cwd) if dest else None, verb + " destination"))
        elif verb == "robocopy" and len(pos) >= 2:
            hits.append((resolve(pos[1], cwd), "robocopy destination"))
        elif verb in ALL_ARGS or (verb == "sed" and any(a.startswith("-i") for a in args)):
            for a in args:
                m = re.match(r"^-(?:path|literalpath|filepath|destination)(?::(.+))?$", a, re.I)
                if m and m.group(1):
                    hits.append((resolve(m.group(1), cwd), verb))
                elif not a.startswith("-"):
                    hits.append((resolve(a, cwd), verb))
        if NET_WRITE_RE.search(seg):
            for m in re.finditer(r"""['"]([A-Za-z]:[\\/][^'"]+|/[A-Za-z]/[^'"]+)['"]""", seg):
                hits.append((resolve(m.group(1), cwd), ".NET file write"))
    return [(p, w) for p, w in hits if p]


def decide(cmd, cwd):
    bad = [(p, w, classify(p)) for p, w in targets(cmd, cwd) if classify(p) in ("outside", "main")]
    return bad


def _log(rec):
    if not WLOG or os.environ.get("LIVEBENCH_FENCE_NOLOG"):
        return
    import time
    rec["t"] = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(WLOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    except OSError:
        pass


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:                                                              # noqa: BLE001
        return 0
    if data.get("tool_name") not in ("Bash", "PowerShell") or not (N_ROOT or N_MAIN):
        return 0
    cmd = (data.get("tool_input") or {}).get("command") or ""
    bad = decide(cmd, data.get("cwd") or os.getcwd())
    if not bad:
        return 0
    for p, w, c in bad:
        _log({"event": "shell", "path": p, "class": c, "refused": True, "why": w, "cmd": cmd[:200]})
    sys.stderr.write("BLOCKED by .livebench/guard_fence.py (livebench fence, card chat-B7): this bench arm writes only under "
                     "%s; the command writes %s\n" % (OUT, "; ".join("%s (%s: %s)" % (p, c, w) for p, w, c in bad[:4])))
    return 2


def selftest():
    wt = os.path.dirname(HERE)
    other = os.path.join(os.path.dirname(OUT), "ZZ_other_arm")
    root_b, out_b, main_b = ROOT.replace("\\", "/"), OUT.replace("\\", "/"), MAIN.replace("\\", "/")
    root_gb = "/" + root_b[0].lower() + root_b[2:]
    main_rel = os.path.relpath(MAIN, wt).replace("\\", "/")
    refuse = [
        ('cp x.vi "%s/x.vi"' % root_gb, "bash cp into the claudeDev root (/c/ form)"),
        ("Copy-Item a.vi -Destination '%s\\y.vi'" % ROOT, "PS Copy-Item -Destination root"),
        ('echo hi > "%s/STATUS.md"' % main_b, "bash redirect into main"),
        ("Set-Content -Path '%s\\tools\\x.txt' -Value 1" % MAIN, "PS Set-Content main"),
        ('rm "%s/D1_x.vi"' % root_b, "rm in the root"),
        ("cp a.py %s/tools/x.py" % main_rel, "relative path into main"),
        ('git -C "%s" commit -m x' % main_b, "git commit on main"),
        ('mv "%s/a.vi" "%s/a.vi"' % (root_b, out_b), "mv OUT of the root (modifies the root)"),
        ('cp x.vi "%s/x.vi"' % other.replace("\\", "/"), "write into ANOTHER arm's folder"),
        ("ls; cat f >> '%s\\log.txt'" % MAIN, "second segment appends into main"),
        ("[IO.File]::WriteAllText('%s\\z.txt', 'x')" % ROOT, ".NET write in the root"),
    ]
    allow = [
        ('cp "%s/DonorX.vi" "%s/x.vi"' % (root_b, out_b), "copy FROM the root INTO the arm folder"),
        ('ls "%s"; md5sum "%s/STATUS.md"' % (root_b, main_b), "reads"),
        ("echo x > tools/bench/foo.txt", "write inside the worktree"),
        ("Copy-Item x -Destination '%s\\y.vi'" % OUT, "PS copy into the arm folder"),
        ('git -C "%s" log --oneline -1' % main_b, "git read on main"),
        ("py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/recipes/x.py", "normal run"),
        ('cp a "%s/NIScriptingExamples/Moving Objects/Test - Moving Objects Source.vi"' % root_b, "the gscript fixture"),
        ("grep -n x \"%s/tools/gscript.py\" 2>/dev/null" % main_b, "read with a stderr redirect to /dev/null"),
    ]
    res = []
    for cmd, label in refuse:
        res.append(("REFUSE " + label, bool(decide(cmd, wt))))
    for cmd, label in allow:
        res.append(("ALLOW " + label, not decide(cmd, wt)))
    import subprocess
    env = dict(os.environ, LIVEBENCH_FENCE_NOLOG="1")       # a self-test refusal is not an arm event
    r = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(
        {"tool_name": "Bash", "tool_input": {"command": refuse[0][0]}, "cwd": wt}), capture_output=True, text=True, env=env)
    res.append(("HOOK protocol: exit 2 + BLOCKED message on stdin payload", r.returncode == 2 and "BLOCKED by" in r.stderr))
    r = subprocess.run([sys.executable, os.path.abspath(__file__)], input=json.dumps(
        {"tool_name": "Bash", "tool_input": {"command": allow[0][0]}, "cwd": wt}), capture_output=True, text=True, env=env)
    res.append(("HOOK protocol: exit 0 on an allowed command", r.returncode == 0))
    for label, ok in res:
        print("CASE %s: %s" % (label, "PASS" if ok else "FAIL"), flush=True)
    n = sum(1 for _l, ok in res if ok)
    print("FENCE-SELFTEST %s arm %s: %d pass / %d fail" % (wt, CFG.get("arm"), n, len(res) - n), flush=True)
    return 0 if n == len(res) else 1


if __name__ == "__main__":
    sys.exit(selftest() if "--selftest" in sys.argv else main())
