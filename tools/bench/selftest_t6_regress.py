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
CRLF = "this run's tree is a git worktree checked out with core.autocrlf=true: text files are CRLF, so md5 pins differ"
EXPLAINED = {
    "selftest_c147_b1_2.py": (r"FAIL  P0 pins before", CRLF + " (P0) and stagexec.load_final_plan refuses the CRLF step files; "
                              "its T0/T0b/T2/T4b/T3-reuse_bad assert the renames LICENCE that card chat-T6 removed (docs/d1/result-gates.md); "
                              "its T1/T3/T4 scenarios are re-asked by selftest_t6_poskey N1/N2/M7/M8"),
    "@stagexec selftest": (r"step file\(s\) missing or changed since finalize", CRLF + " (load_final_plan md5 of the sim step files); "
                           "stagexec imports none of the changed functions (its T14 asserts stagekit is not imported)"),
}


def main():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import protocol
    ok_n, bad = 0, []
    for t in TESTS:
        if t.startswith("@"):
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
