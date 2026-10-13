# ---
# labview: none
# hardware: none
# ---
"""git_push.py - upload master to origin (github.com/SihNho/MT_LabVIEW, private; shared with a lab colleague).

User 2026-10-13: "Github은 (b) 조건 및 명시적인 요청" - once a day by a scheduled task, and whenever the user asks.
Never at every cycle (the runner does not push). Before pushing, the lines the push would ADD are scanned for secret
shapes (CLAUDE.md never-9); a hit refuses the push and prints the pattern NAME only, never the matched text.
    py tools/git_push.py            # scan, then push master
    py tools/git_push.py --check    # scan only
Exit 0 = pushed / clean (or nothing to push), 3 = secret shape found, 1 = git error. Ends with a RESULT line.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_RES = [("api-key", re.compile(r"(?<![\w-])sk-(?:ant-)?[A-Za-z0-9_-]{20,}|AIza[0-9A-Za-z_-]{30,}")),
              ("github-token", re.compile(r"ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{20,}")),
              ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY")),
              ("oauth-secret", re.compile(r"(?:client_secret|refresh_token)\"?\s*[:=]\s*\"[^\"\s]{8,}"))]


def secret_hits(diff_text):
    """Names of the SECRET_RES patterns found in the ADDED lines of a unified diff (empty list = clean)."""
    added = "\n".join(l for l in diff_text.splitlines() if l.startswith("+") and not l.startswith("+++"))
    return [name for name, rx in SECRET_RES if rx.search(added)]


assert (secret_hits("+x = 'ghp_" + "a" * 36 + "'\n-old") == ["github-token"] and secret_hits("+plain text") == []
        and secret_hits("+name: ask-the-user-about-rig-domain-meaning") == [])


def git(*args, timeout=300):
    return subprocess.run(["git"] + list(args), cwd=ROOT, timeout=timeout, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def main():
    res = {"branch": git("branch", "--show-current").stdout.strip()}
    if res["branch"] != "master":
        res["status"] = "skipped: not on master"
        print("RESULT " + json.dumps(res))
        return 0
    git("fetch", "origin", "--quiet", timeout=300)
    res["ahead"] = int((git("rev-list", "--count", "origin/master..master").stdout or "0").strip() or 0)
    if res["ahead"] == 0:
        res["status"] = "nothing to push"
        print("RESULT " + json.dumps(res))
        return 0
    res["secret_hits"] = secret_hits(git("diff", "origin/master..master", timeout=600).stdout or "")
    if res["secret_hits"]:
        res["status"] = "REFUSED: secret shape in outgoing lines"
        print("RESULT " + json.dumps(res))
        return 3
    if "--check" in sys.argv:
        res["status"] = "clean (check only)"
        print("RESULT " + json.dumps(res))
        return 0
    p = git("push", "origin", "master", timeout=1800)
    res["status"] = "pushed" if p.returncode == 0 else "push failed rc=%d: %s" % (
        p.returncode, ((p.stderr or "").strip().splitlines() or [""])[-1][:200])
    print("RESULT " + json.dumps(res))
    return 0 if p.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
