# ---
# labview: none
# hardware: none
# ---
r"""selftest_t3_regress - card chat-T3: re-run every EXISTING offline self-test that covers code this card changed
(stagexec adopt / loop_parent / Executor, stage_prerun rebind / rebase, gateclass HARD_MARK_RE, protocol RESULT/STOP lines)
and print each one's RESULT line. Found by `grep -l "adopt_verdict|rebind(|.rebase(|loop_parent|HARD_MARK_RE|soft_only|
address_only|all_result_lines" tools/bench/selftest*.py` plus stagexec's own `selftest` entry. One child at a time,
600 s cap each; never opens LabVIEW (each child declares labview: none, stagexec's selftest is its offline-arg).
Usage: py -u tools/bench/selftest_t3_regress.py [--root <tree>]   (--root = another checkout, e.g. HEAD in %TEMP%)
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = ["selftest_c133_1_fsroutes.py", "selftest_chat_p1.py", "selftest_rebase_c132_6.py", "selftest_rebase_c133_3.py",
         "selftest_rebase_uidreuse_c143_4.py", "selftest_rebind_c132_5.py", "selftest_rebind_c142_5.py", "selftest_s5.py",
         "selftest_stage_prerun_c106e.py", "selftest_stagexec_s4.py", "selftest_t3.py", "@stagexec selftest"]


def main(argv):
    root = os.path.abspath(argv[argv.index("--root") + 1]) if "--root" in argv else os.path.dirname(os.path.dirname(HERE))
    sys.path.insert(0, os.path.join(root, "tools"))
    import protocol
    ok_n, bad = 0, []
    for t in TESTS:
        if t.startswith("@"):
            cmd = [sys.executable, "-u", os.path.join(root, "tools", "stagexec.py"), "selftest"]
        else:
            p = os.path.join(root, "tools", "bench", t)
            if not os.path.isfile(p):
                print("REGRESS {0} | absent in {1}".format(t, root), flush=True)
                continue
            # a child runs only when its OWN scope header says labview: none - this driver never launders a read/build
            # script past the card's labview flag (found after the first run: selftest_chat_p1 / selftest_stagexec_s4
            # declare `labview: read`; both touch no LabVIEW by their imports, but the header is the contract)
            hdr = re.findall(r"^# labview: (\w+)\s*$", open(p, encoding="utf-8", errors="replace").read(), re.M)
            if hdr != ["none"]:
                print("REGRESS {0} | SKIPPED: declares labview {1} (run it under a card whose labview flag allows it)".format(
                    t, hdr), flush=True)
                continue
            cmd = [sys.executable, "-u", p]
        try:
            r = subprocess.run(cmd, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
            out, rc = (r.stdout or "") + (r.stderr or ""), r.returncode
        except subprocess.TimeoutExpired:
            out, rc = "", "TIMEOUT"
        res = protocol.parse_result_line(out)
        fails = [ln.strip()[:200] for ln in out.splitlines() if ln.lstrip().startswith("FAIL ") or ln.startswith("  FAIL  ")]
        print("REGRESS {0} | rc {1} | {2} | fails {3}".format(t, rc, None if res is None else "{0} {1}/{2}".format(
            res.get("status"), (res.get("gates") or {}).get("pass"), (res.get("gates") or {}).get("fail")), fails[:4]), flush=True)
        if rc == 0 and res is not None and not protocol.result_failed(res):
            ok_n += 1
        else:
            bad.append(t)
    print(protocol.result_line(protocol.make_result(ok_n, len(bad), ("failing: " + ", ".join(bad))[:200] if bad else None)))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
