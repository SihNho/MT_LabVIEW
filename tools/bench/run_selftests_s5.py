r"""run_selftests_s5 - card chat-S5: re-run the EXISTING offline self-tests of the modules S5 touched (stagesim, stagexec,
stage_prerun, stagekit, gateclass, protocol, guard_peer, errorlist_check, the EL rule, rebind/rebase) and print one line each.
OFFLINE, no LabVIEW (each script was checked for COM use: none; selftest_errorlist_reuse_81 only asserts LabVIEW modules are NOT
loaded). Children run one at a time, 240 s cap each.
PREDICTION CONTRACT: every child ends rc 0 / RESULT PASS, or the line says why (pre-existing vs caused by S5 is read per child).
    py tools/bgrun.py --material --max-min 40 --log tools/bench/run_selftests_s5.log -- py -u tools/bench/run_selftests_s5.py"""
import os, re, subprocess, sys, time                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as PR                                                                     # noqa: E402
B = "tools/bench/"
RUNS = [["tools/stagesim.py", "selftest"], ["tools/stagexec.py", "selftest"]] + [[B + s + ".py"] for s in (
    "selftest_gateclass_s2", "selftest_gateclass_s3", "selftest_protocol", "selftest_protocol_wiring",
    "selftest_guard_peer_budget", "selftest_guard_peer_failre", "selftest_guard_peer_jev", "selftest_guard_peer_ladder",
    "selftest_guard_peer_samerow", "selftest_guard_peer_scan_tmp", "selftest_stagekit", "selftest_elpred",
    "selftest_rebind_c142_5", "selftest_rebind_c132_5", "selftest_rebase_c132_6", "selftest_rebase_c133_3",
    "selftest_rebase_uidreuse_c143_4", "selftest_stage_prerun_stageplan", "selftest_stage_prerun_graphload",
    "selftest_stage_prerun_c103", "selftest_stage_prerun_c106c", "selftest_stage_prerun_c106e", "selftest_stage_prerun_c110g",
    "selftest_stage_prerun_c114", "selftest_stage_prerun_c114d", "selftest_stage_prerun_c115a", "selftest_stage_prerun_c115c",
    "selftest_stage_prerun_c128", "selftest_stage_prerun_c128b", "selftest_stage_prerun_headcmp_79-6", "selftest_prerun_diag",
    "selftest_stagexec_gate", "selftest_stagexec_s4", "selftest_stagexec_c124_6", "selftest_stagesim_k79",
    "selftest_stagesim_l2a1_80", "selftest_stagesim_unflip_81", "selftest_stagesim_pin", "selftest_stagesim_tunnel_naming",
    "selftest_stagesim_fsexit_c138_1", "selftest_errorlist_check_header", "selftest_errorlist_retry",
    "selftest_errorlist_reuse_81", "selftest_errorlist_ocr_c127", "selftest_s5")]
env = dict(os.environ, ADDR_JEV="0", GATE_SOFT_LOG=os.path.join(os.environ.get("TEMP", "."), "s5_selftests_soft.jsonl"))
ok_n, bad = 0, []
for argv in RUNS:
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, "-u"] + argv, cwd=ROOT, capture_output=True, text=True, timeout=240, env=env,
                           encoding="utf-8", errors="replace")
        out, rc = (p.stdout or "") + (p.stderr or ""), p.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -9
    rl = PR.all_result_lines(out)
    last = rl[-1] if rl else None
    st = (last or {}).get("status")
    tally = re.findall(r"(\d+)\s*(?:pass|PASS)\D{1,6}(\d+)\s*(?:fail|FAIL)", out)
    good = rc == 0 and st in (None, "PASS")
    ok_n += good
    if not good:
        bad.append(argv[0])
    tail = [ln for ln in out.splitlines() if re.search(r"FAIL|Error|Traceback", ln)][:3]
    print("SELFTEST {0} | {1} | rc {2} | RESULT {3} {4} | tally {5} | {6:.0f}s | {7}".format(
        "PASS" if good else "FAIL", " ".join(argv), rc, st, (last or {}).get("gates"), tally[-1:] , time.time() - t0,
        "" if good else " || ".join(x[:220] for x in tail)), flush=True)
print(PR.result_line(PR.make_result(ok_n, len(bad), ("selftests failing: " + ", ".join(os.path.basename(b) for b in bad))[:190] if bad else None,
                                    [])), flush=True)
