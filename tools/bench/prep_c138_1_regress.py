r"""prep_c138_1_regress - card 138-1 pass 2 (offline): run every existing stagesim / stagexec offline self-test after the
FS-exit + delete_wire edits and list each one's RESULT gate counts. The two stagekit-importing OFFLINE_SELFTESTS entries
(selftest_c134_1_dry.py, selftest_census_hookin_c123.py) are run by c125_1_offline_measure.py under its COM tripwire, not here.
Prior art: c125_1_offline_measure.py runs children the same way (subprocess, one per entry). No new op.
PREDICTION CONTRACT: every child exit 0 with a PASS RESULT line (fail 0); totals printed; ends with a RESULT line.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                        # noqa: E402

TESTS = [("tools/stagesim.py", ["selftest"]), ("tools/stagexec.py", ["selftest"])] + [
    ("tools/bench/" + n, []) for n in (
        "selftest_stagesim_k79.py", "selftest_stagesim_l2a1_80.py", "selftest_stagesim_unflip_81.py", "selftest_stagesim_pin.py",
        "selftest_stagesim_tunnel_naming.py", "selftest_stagexec_gate.py", "selftest_stagexec_c124_6.py",
        "selftest_c133_1_fsroutes.py", "selftest_c134_1_fsmap.py", "selftest_c134_2_gates.py", "selftest_c134_2_regress.py",
        "selftest_c134_4_owners.py", "selftest_c135_2_device.py", "selftest_fs_c126.py", "selftest_case_frame_c124.py",
        "selftest_stagesim_fsexit_c138_1.py")]
RES_RE = re.compile(r"^RESULT (\{.*\})\s*$", re.M)
# --only a,b : run only those test files; --head M1,M2 : preload the git-HEAD copies (tools/bench/sim/c138_1_head/<m>_head.py)
# of modules M (stagesim / stagexec / stage_prerun) into sys.modules before the test runs - the before/after discriminator
HEADDIR = os.path.join(HERE, "sim", "c138_1_head")
SHIM = ("import importlib.util, runpy, sys\n"
        "sys.path.insert(0, %r)\n"
        "for m in sys.argv[2].split(',') if sys.argv[2] else []:\n"
        "    sp = importlib.util.spec_from_file_location(m, %r + '/' + m + '_head.py'); mod = importlib.util.module_from_spec(sp)\n"
        "    sys.modules[m] = mod; sp.loader.exec_module(mod)\n"
        "p = sys.argv[1]; sys.argv = [p] + sys.argv[3:]\n"
        "runpy.run_path(p, run_name='__main__')\n")


def main():
    tot_p = tot_f = 0
    bad = []
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    head = sys.argv[sys.argv.index("--head") + 1] if "--head" in sys.argv else ""
    tests = [(p, a) for p, a in TESTS if only is None or os.path.basename(p) in only]
    if head:
        print("HEAD modules preloaded:", head)
    for path, args in tests:
        cmd = [sys.executable, "-u", "-c", SHIM % (os.path.join(ROOT, "tools"), HEADDIR.replace("\\", "/")),
               os.path.join(ROOT, path), head] + args
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        m = RES_RE.findall(p.stdout or "")
        r = json.loads(m[-1]) if m else None
        g = (r or {}).get("gates") or {}
        tail = (p.stdout or "").strip().splitlines()[-3:] if not r else []
        print("%-48s rc=%s %s pass=%s fail=%s %s" % (path, p.returncode, (r or {}).get("status", "NO-RESULT"), g.get("pass"),
                                                    g.get("fail"), (r or {}).get("first_fail") or (tail + [(p.stderr or "")[-300:]])))
        tot_p += int(g.get("pass") or 0)
        tot_f += int(g.get("fail") or 0)
        if p.returncode != 0 or not r or r.get("status") != "PASS":
            bad.append(path)
        if "--verbose" in sys.argv and (p.returncode != 0 or not r or r.get("status") != "PASS"):
            for ln in (p.stdout or "").splitlines():
                if "FAIL" in ln or "rebase" in ln.lower() or "Error" in ln:
                    print("    | " + ln[:400])
            print("    | stderr: " + (p.stderr or "")[-600:].replace("\n", " / "))
    print("TOTAL tests %d gates pass %d fail %d; not PASS: %s" % (len(tests), tot_p, tot_f, bad))
    print(protocol.result_line(protocol.make_result(len(tests) - len(bad), len(bad), bad[0] if bad else None, [])))
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
