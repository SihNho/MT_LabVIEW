"""diag_c131_2_suite - card 131-2 P4: rerun the EXISTING offline self-tests of every hook/tool this card edits
(guard_peer, guard_cycle, protocol.peer_role_of consumed by guard_bash) and tally each one's RESULT line. Copied from
diag_c130_2_suite.py (found before writing); groups re-cut for this card. Excluded on purpose: selftest_c100_v5wrap
(imports stagekit = LabVIEW), selftest_motor_gate2 (motor tooling, card flags.hardware none, not edited here),
selftest_g6_peerset (a wrapper that reruns the guard_peer group below - a duplicate, and it TIMEOUTed in c130).
Usage: py -u tools/bench/diag_c131_2_suite.py <tag> ; tag only names the run (before/after).
PREDICTION: every listed self-test ends rc 0 with a PASS RESULT line (or none) - the BEFORE run records pre-existing
failures so the AFTER run is judged against it."""
import json, os, re, subprocess, sys, time                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                               # noqa: E402
NAMES = [
    # guard_peer
    "selftest_guard_peer_ladder", "selftest_guard_peer_budget", "selftest_guard_peer_77_measure",
    "selftest_guard_peer_scan_tmp", "selftest_guard_peer_samerow", "selftest_guard_peer_failre",
    "selftest_guard_peer_jev", "selftest_jev_ladder_action", "selftest_stamp_window", "selftest_audit_c4c_split",
    "selftest_logclass_cmd", "selftest_c125_1", "selftest_chat_p1", "selftest_c130_2_tools",
    # guard_cycle
    "selftest_guard_cycle_fixed", "selftest_guard_cycle_offline", "selftest_guard_cycle_rerun",
    "selftest_stoprecord_offline_c107", "selftest_logclass_recipebuild",
    # protocol / guard_bash (peer_role_of -> check_command)
    "selftest_protocol", "selftest_protocol_wiring", "selftest_requires", "selftest_chat_p2", "selftest_c121_3_gatefp",
    "selftest_c106d_tools", "selftest_c108e_tools", "selftest_c103d_hooks", "selftest_guard_bash_jev",
    "selftest_launch_gate", "selftest_c110_launchgate", "selftest_guard_session", "selftest_stoprecord_c130_2",
]
RES_RE = re.compile(r"^RESULT (\{.*\})\s*$", re.M)
tag = (sys.argv[1:] or ["run"])[0]
print("SUITE TAG %s  %d tests" % (tag, len(NAMES)), flush=True)
ok = bad = 0
first = None
for n in NAMES:
    path = os.path.join(ROOT, "tools", "bench", n + ".py")
    if not os.path.isfile(path):
        print("SUITE %-40s MISSING" % n, flush=True); bad += 1; first = first or n + " missing"
        continue
    t0 = time.time()
    try:
        cp = subprocess.run([sys.executable, "-u", path], cwd=ROOT, capture_output=True, text=True, timeout=240,
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
print("=== SUITE %s: %d ok / %d fail" % (tag, ok, bad), flush=True)
print(P.result_line(P.make_result(ok, bad, first)), flush=True)
