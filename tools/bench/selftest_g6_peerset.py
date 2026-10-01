"""Card chat-G6: run the existing peer / guard_peer self-tests after the peer.ps1 fact-chain change.

Prediction contract: every listed self-test exits rc 0 (they touch no LabVIEW, no peer call is dispatched by them).
Found before writing (ls tools/bench/selftest_*peer*.py + grep peer.ps1): the guard_peer set (budget, failre, jev,
ladder, samerow, scan_tmp, 77_measure) and the ones that read peer.ps1 text (c106d_tools H4, protocol_wiring,
guard_bash_jev, logclass_cmd, audit_c4c_split, stamp_window). Nothing new is built here; this only runs them.
"""
import os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
TESTS = ["selftest_guard_peer_budget.py", "selftest_guard_peer_failre.py", "selftest_guard_peer_jev.py",
         "selftest_guard_peer_ladder.py", "selftest_guard_peer_samerow.py", "selftest_guard_peer_scan_tmp.py",
         "selftest_guard_peer_77_measure.py", "selftest_c106d_tools.py", "selftest_protocol_wiring.py",
         "selftest_guard_bash_jev.py", "selftest_logclass_cmd.py", "selftest_audit_c4c_split.py",
         "selftest_stamp_window.py"]
npass = nfail = 0
first_fail = None
for t in TESTS:
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, t)], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=300)
        rc, tail = r.returncode, (r.stdout + r.stderr).strip().splitlines()[-1:] or [""]
    except subprocess.TimeoutExpired:
        rc, tail = "TIMEOUT", ["timeout 300 s"]
    ok = rc == 0
    npass += ok; nfail += (not ok)
    if not ok and first_fail is None:
        first_fail = f"{t} rc={rc}"
    print(f"GATE {'PASS' if ok else 'FAIL'} | {t} | rc={rc} | {time.time()-t0:.1f}s | {tail[0][:160]}", flush=True)

try:
    import protocol
    print(protocol.result_line({"status": "PASS" if nfail == 0 else "FAIL",
                                "gates": {"pass": npass, "fail": nfail}, "first_fail": first_fail,
                                "artefacts": []}), flush=True)
except Exception as e:  # fall back to a hand-written C6 line
    import json
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if nfail == 0 else "FAIL",
                                  "gates": {"pass": npass, "fail": nfail}, "first_fail": first_fail,
                                  "artefacts": [], "note": f"protocol.result_line unavailable: {e}"}), flush=True)
sys.exit(0 if nfail == 0 else 1)
