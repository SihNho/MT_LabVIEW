"""diag_c130_2_suite - card 130-2 P6: rerun the EXISTING offline self-tests of every hook/tool this card edits and tally
each one's RESULT line. Offline: every listed self-test documents itself as no-LabVIEW / no-motion (hooks called with
stubbed payloads). Usage: py -u tools/bench/diag_c130_2_suite.py <group> ; groups below.
PREDICTION: every listed self-test ends with a RESULT line and rc 0 (any FAIL is reported with its first failing gate)."""
import json, os, re, subprocess, sys, time                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                               # noqa: E402
GROUPS = {
    "guard_bash": ["selftest_stoprecord_c130_2", "selftest_c103d_hooks", "selftest_c106d_tools", "selftest_guard_bash_jev",
                   "selftest_launch_gate", "selftest_c110_launchgate", "selftest_c121_3_gatefp", "selftest_chat_p1",
                   "selftest_protocol_wiring", "selftest_guard_session", "selftest_g6_peerset", "selftest_c100_v5wrap",
                   "selftest_requires", "selftest_next_gate_jev", "selftest_retry_cap", "selftest_motor_gate2",
                   "selftest_stoprecord_c116a", "selftest_stoprecord_offline_c107", "selftest_stoprecord_table",
                   "selftest_stoprecord_bgrun", "selftest_stoprecord_eqform", "selftest_stoprecord_supersession"],
    "protocol": ["selftest_c130_2_tools", "selftest_card_clock", "selftest_protocol", "selftest_protocol_wiring",
                 "selftest_requires", "selftest_chat_p1", "selftest_chat_p2", "selftest_c121_3_gatefp", "selftest_c125_1",
                 "selftest_c108e_tools", "selftest_c106d_tools"],
    "guard_peer": ["selftest_guard_peer_ladder", "selftest_guard_peer_budget", "selftest_guard_peer_77_measure",
                   "selftest_guard_peer_scan_tmp", "selftest_guard_peer_samerow", "selftest_guard_peer_failre",
                   "selftest_guard_peer_jev", "selftest_jev_ladder_action", "selftest_stamp_window",
                   "selftest_audit_c4c_split", "selftest_logclass_cmd", "selftest_g6_peerset"],
}
RES_RE = re.compile(r"^RESULT (\{.*\})\s*$", re.M)
names = []
for g in sys.argv[1:] or ["guard_bash"]:
    names += [n for n in GROUPS.get(g, [g]) if n not in names]
ok = bad = 0
first = None
for n in names:
    path = os.path.join(ROOT, "tools", "bench", n + ".py")
    if not os.path.isfile(path):
        print("SUITE %-40s MISSING" % n, flush=True); bad += 1; first = first or n + " missing"
        continue
    t0 = time.time()
    try:
        cp = subprocess.run([sys.executable, "-u", path], cwd=ROOT, capture_output=True, text=True, timeout=600,
                            encoding="utf-8", errors="replace")
        out, rc = cp.stdout + cp.stderr, cp.returncode
    except subprocess.TimeoutExpired:
        out, rc = "", "TIMEOUT"
    m = RES_RE.findall(out)
    gates = json.loads(m[-1]).get("gates", {}) if m else {}
    tail = re.findall(r"=== GATES?:?[^\n]*|^\s*\d+\s*/\s*\d+[^\n]*", out, re.M)
    good = rc == 0 and (not m or json.loads(m[-1]).get("status") in ("PASS", "SKIP"))
    ok += good; bad += (not good)
    if not good and first is None:
        first = n
    fl = [ln for ln in out.splitlines() if re.search(r"\bFAIL\b", ln)][:2]
    print("SUITE %-40s rc=%s gates=%s %s %.0fs %s" % (n, rc, gates or (tail[-1] if tail else "-"), "OK" if good else "FAIL",
                                                     time.time() - t0, (" | ".join(fl))[:300] if not good else ""), flush=True)
print("=== SUITE: %d ok / %d fail" % (ok, bad), flush=True)
print(P.result_line(P.make_result(ok, bad, first)), flush=True)
