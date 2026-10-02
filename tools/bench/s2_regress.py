r"""s2_regress - card chat-S2 (offline): run the existing stagekit / stagexec / stage_prerun / census / guard_peer self-tests
and list each one's RESULT gate counts, BEFORE and AFTER the STOP-vs-LOG gate classification (tools/gateclass.py).
Prior art: tools/bench/prep_c138_1_regress.py (same subprocess-per-test shape, copied; the HEAD shim is not needed here).
PREDICTION CONTRACT: every child exits 0 with a PASS RESULT line (fail 0), or the difference is explained in the card result.
Usage: py -u tools/bench/s2_regress.py [--only a.py,b.py]
"""
import json
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                        # noqa: E402

TESTS = [("tools/stagexec.py", ["selftest"])] + [("tools/bench/" + n, []) for n in (
    # selftest_stagekit.py is NOT run: its case J reached a real LabVIEW through COM twice on 2026-10-03 00:17/00:20
    # (s2_regress_before*.log: com_error 'File not found' for stub.vi) even under the c125 tripwire; card chat-S2 is labview:none
    "selftest_stagexec_gate.py", "selftest_stagexec_c124_6.py", "selftest_namegate_c132_1.py",
    "selftest_stage_prerun_c103.py", "selftest_stage_prerun_c106c.py", "selftest_stage_prerun_c106e.py",
    "selftest_stage_prerun_c110g.py", "selftest_stage_prerun_c114.py", "selftest_stage_prerun_c114d.py",
    "selftest_stage_prerun_c115a.py", "selftest_stage_prerun_c115c.py", "selftest_stage_prerun_c128.py",
    "selftest_stage_prerun_c128b.py", "selftest_stage_prerun_graphload.py", "selftest_stage_prerun_headcmp_79-6.py",
    "selftest_stage_prerun_stageplan.py", "selftest_prerun_diag.py",
    "selftest_census_predict.py", "selftest_census_hookin_c123.py",
    "selftest_guard_peer_77_measure.py", "selftest_guard_peer_budget.py", "selftest_guard_peer_failre.py",
    "selftest_guard_peer_jev.py", "selftest_guard_peer_ladder.py", "selftest_guard_peer_samerow.py",
    "selftest_guard_peer_scan_tmp.py", "selftest_gateclass_s2.py")]
RES_RE = re.compile(r"^RESULT (\{.*\})\s*$", re.M)
TRIP = os.path.join(HERE, "c125_1_offline_measure.py")


def main():
    tot_p = tot_f = 0
    bad, rows = [], []
    only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
    tests = [(p, a) for p, a in TESTS if (only is None or os.path.basename(p) in only) and os.path.exists(os.path.join(ROOT, p))]
    for path, args in tests:
        tf = os.path.join(tempfile.gettempdir(), "s2_trip_%d_%s.txt" % (os.getpid(), os.path.basename(path)))
        if os.path.exists(tf):
            os.remove(tf)
        try:
            # every child runs under c125_1_offline_measure's COM TRIPWIRE: a COM entry point raises before it reaches
            # LabVIEW (card chat-S2 is labview:none; the first baseline run reached LabVIEW from selftest_stagekit case J)
            env = dict(os.environ, GATE_SOFT_LOG=os.path.join(tempfile.gettempdir(), "s2_regress_soft.jsonl"))  # never the real log
            p = subprocess.run([sys.executable, "-u", TRIP, "--child", os.path.join(ROOT, path), tf] + args, cwd=ROOT, env=env,
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
            out, rc, err = p.stdout or "", p.returncode, p.stderr or ""
        except subprocess.TimeoutExpired:
            out, rc, err = "", "TIMEOUT", ""
        trips = open(tf, encoding="utf-8").read().count("TRIP ") if os.path.exists(tf) else 0
        if trips:
            print("    TRIPWIRE %d COM call(s) refused in %s" % (trips, path), flush=True)
        m = RES_RE.findall(out)
        try:
            r = json.loads(m[-1]) if m else None
        except ValueError:
            r = None
        g = (r or {}).get("gates") or {}
        tail = out.strip().splitlines()[-3:] if not r else []
        print("%-48s rc=%s %s pass=%s fail=%s %s" % (path, rc, (r or {}).get("status", "NO-RESULT"), g.get("pass"),
                                                    g.get("fail"), (r or {}).get("first_fail") or (tail + [err[-300:]])), flush=True)
        if rc != 0 or not r or r.get("status") != "PASS":
            bad.append(path)
            for ln in out.splitlines():
                if re.match(r"^\s*(->\s*)?FAIL\b", ln):
                    print("    | " + ln[:300], flush=True)
        tot_p += int(g.get("pass") or 0)
        tot_f += int(g.get("fail") or 0)
        rows.append({"test": path, "rc": rc, "status": (r or {}).get("status"), "gates": g})
    print("TOTAL tests %d gates pass %d fail %d; not PASS: %s" % (len(tests), tot_p, tot_f, bad), flush=True)
    print(protocol.result_line(protocol.make_result(len(tests) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
