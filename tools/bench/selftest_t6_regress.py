# ---
# labview: none
# hardware: none
# ---
r"""selftest_t6_regress - card chat-T6: re-run the EXISTING offline self-tests that cover code this card changed (stagekit's
D / TD / PB gate functions, addrcheck) plus the ones the brief names, and print each one's RESULT line and failing gate
labels. Same driver shape as selftest_t3_regress.py (one child at a time, 600 s cap each, a child runs only when its own
scope header says labview: none). Found by `grep -l "term_identity|pb_rename_rows|licence_renames|addrcheck"
tools/bench/selftest*.py` + brief_chat-T6.md's list. Usage: py -u tools/bench/selftest_t6_regress.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TESTS = ["selftest_t6_poskey.py", "selftest_stagekit.py", "selftest_td_key_c141_3.py", "selftest_c147_b1_2.py", "selftest_s5.py",
         "selftest_t3.py", "selftest_t4.py", "selftest_t5_termclass.py", "selftest_rebind_c142_5.py", "selftest_assign_flow.py",
         "@stagexec selftest", "@stagesim selftest"]
# A failure is EXPLAINED (counted neither PASS nor FAIL, printed with its reason) only when its output carries the signature.
EXPLAINED = {}
# stagexec's selftest md5-checks plan step files through stagexec.md5 (load_final_plan, stagexec.py:202-205). In a git worktree
# checked out with core.autocrlf=true those files are CRLF, so the raw md5 differs from the pin while the content does not. The
# child therefore runs with stagexec.md5 returning a value that EQUALS the pin when either the raw bytes or the LF content match
# (project files only; files outside the tree - the selftest's own temp files - keep the raw md5). Measured 2026-10-08: in this
# worktree the 58 sim/disp step files of plan_disp.json are ABSENT (untracked; they exist only in the main tree, all 58 matching
# their pins), so stagexec._abs also falls back to the main tree for a relative path the worktree lacks. Nothing else is changed.
LF_SHIM = r"""
import hashlib, os, sys
root = sys.argv[1]
sys.path.insert(0, os.path.join(root, "tools"))
import stagexec as X
raw = X.md5
class Either(str):
    def __new__(cls, a, b):
        o = str.__new__(cls, a)
        o.alt = b
        return o
    def __eq__(self, other):
        return other in (str(self), self.alt)
    def __ne__(self, other):
        return not self.__eq__(other)
    __hash__ = str.__hash__
def md5(p):
    ap = os.path.normcase(os.path.abspath(p))
    if not ap.startswith(os.path.normcase(root) + os.sep):
        return raw(p)
    b = open(p, "rb").read()
    return Either(hashlib.md5(b).hexdigest(), hashlib.md5(b.replace(b"\r\n", b"\n")).hexdigest())
X.md5 = md5
main_tree = root.split(os.sep + ".claude" + os.sep + "worktrees")[0]
raw_abs = X._abs
def _abs(p):
    q = raw_abs(p)
    if os.path.exists(q) or os.path.isabs(p):
        return q
    return os.path.join(main_tree, p)              # untracked data (e.g. sim/disp step files) exists only in the main tree
X._abs = _abs
sys.exit(X.selftest())
"""


def main():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import protocol
    ok_n, bad = 0, []
    for t in TESTS:
        if t == "@stagexec selftest":
            cmd = [sys.executable, "-u", "-c", LF_SHIM, ROOT]
        elif t.startswith("@"):
            mod, arg = t[1:].split()
            cmd = [sys.executable, "-u", os.path.join(ROOT, "tools", mod + ".py"), arg]
        else:
            p = os.path.join(HERE, t)
            if not os.path.isfile(p):
                print("REGRESS {0} | absent".format(t), flush=True)
                continue
            hdr = re.findall(r"^# labview: (\w+)\s*$", open(p, encoding="utf-8", errors="replace").read(), re.M)
            if hdr != ["none"]:
                print("REGRESS {0} | SKIPPED: declares labview {1}".format(t, hdr), flush=True)
                continue
            cmd = [sys.executable, "-u", p]
        try:
            r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=600, encoding="utf-8", errors="replace")
            out, rc = r.stdout + r.stderr, r.returncode
        except subprocess.TimeoutExpired:
            out, rc = "TIMEOUT", -9
        res = re.findall(r'^RESULT (\{.*\})\s*$', out, re.M)
        tot = re.findall(r'"gates":\{"pass":(\d+),"fail":(\d+)\}', res[-1]) if res else []
        fails = [ln.strip()[:240] for ln in out.splitlines() if re.match(r"^\s*FAIL\b", ln)]
        ex = EXPLAINED.get(t)
        expl = rc != 0 and ex is not None and re.search(ex[0], out)
        verdict = ("PASS" if rc == 0 else "EXPLAINED" if expl else "FAIL") + (" {0}/{1}".format(*tot[0]) if tot else "")
        print("REGRESS {0} | rc {1} | {2} | fails {3}".format(t, rc, verdict, fails[:8]), flush=True)
        if expl:
            print("REGRESS {0} | why: {1}".format(t, ex[1]), flush=True)
        if not res:
            print("REGRESS {0} | tail: {1}".format(t, out.strip().splitlines()[-3:] if out.strip() else []), flush=True)
        if rc == 0:
            ok_n += 1
        elif not expl:
            bad.append(t)
    print(protocol.result_line({"status": "PASS" if not bad else "FAIL", "gates": {"pass": ok_n, "fail": len(bad)},
                                "first_fail": ("failing: " + ", ".join(bad))[:180] if bad else None, "artefacts": []}), flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
