# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_152-a2-1.md
# ---
r"""diag_c152_a2_1_regress - card 152-a2-1 steps 1/4: COPY of selftest_c134_2_regress.py's runner (same TESTS list, same 600 s
per-child cap, same PASS rule) with ONE change, taken from selftest_t3_regress.py:36-43: a child whose own scope header is not
`labview: none` is SKIPPED, never launched (the card's flags.labview is none; selftest_c134_1_dry.py declares labview: read,
gate-fp fp-71). Why a copy: selftest_c134_2_regress.py launches that child itself (diag_c152_a2_1_base_regress.log:4) and was
killed at my 5-min bgrun cap after 11 of 17 children (:17); its docstring asks 25 min.
EXISTING checked first: selftest_c134_2_regress.py (launches the read child), selftest_t3_regress.py / selftest_t6_regress.py
(other TESTS lists, header filter).
PREDICTION: before == after child by child (same PASS/FAIL per child, same RESULT counts); stagesim selftest 105/0.
    py tools/bgrun.py --material --max-min 60 --log tools/bench/diag_c152_a2_1_regress_<mode>.log -- py -u tools/bench/diag_c152_a2_1_regress.py"""
import json, os, re, subprocess, sys, time                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                          # noqa: E402
TESTS = [["tools/bench/selftest_c134_2_gates.py"], ["tools/bench/selftest_c134_1_dry.py"], ["tools/bench/selftest_c134_1_fsmap.py"],
         ["tools/bench/selftest_dry_c130_5.py"], ["tools/bench/selftest_stage_prerun_stageplan.py"],
         ["tools/bench/selftest_chat_p3.py"], ["tools/bench/selftest_prerun_diag.py"], ["tools/stagesim.py", "selftest"],
         ["tools/bench/selftest_stage_prerun_c128.py"], ["tools/bench/selftest_stage_prerun_c128b.py"], ["tools/bench/selftest_c133_6_fr.py"],
         ["tools/bench/selftest_stage_prerun_c103.py"], ["tools/bench/selftest_stage_prerun_c106c.py"],
         ["tools/bench/selftest_stage_prerun_c106e.py"], ["tools/bench/selftest_stage_prerun_c114d.py"],
         ["tools/bench/selftest_stage_prerun_graphload.py"], ["tools/bench/c125_1_offline_measure.py"]]
if os.path.exists(os.path.join(ROOT, "tools", "hooks", "guard_bash.py.new")):
    print("  STOP  a guard_bash.py.new is staged; selftest_launch_gate (via stageplan) would install it", flush=True)
    sys.exit(2)
res, fails = [], []
for t in TESTS:
    p = os.path.join(ROOT, t[0])
    if not os.path.isfile(p):
        print("  SKIP  {0} (missing)".format(t), flush=True)
        continue
    hdr = re.findall(r"^# labview: (\w+)\s*$", open(p, encoding="utf-8", errors="replace").read(), re.M)
    if hdr != ["none"] and t[0] != "tools/stagesim.py":
        print("  SKIP  {0} (declares labview {1}; card flags.labview none)".format(" ".join(t), hdr), flush=True)
        continue
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-u", p] + t[1:], cwd=ROOT, capture_output=True, text=True, timeout=600)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -9
    rl = [ln for ln in out.splitlines() if ln.startswith("RESULT ")]
    st = json.loads(rl[-1][7:]).get("status") if rl else None
    ok = rc == 0 and st == "PASS"
    res.append(ok)
    ff = [ln[:300] for ln in out.splitlines() if "FAIL" in ln or "Error" in ln][:4]
    print("  {0}  {1} rc={2} result={3} {4:.0f}s {5}".format("PASS" if ok else "FAIL", " ".join(t), rc, rl[-1][7:180] if rl else None,
                                                          time.time() - t0, "" if ok else ff), flush=True)
    if not ok:
        fails.append(" ".join(t))
print(P.result_line(P.make_result(res.count(True), res.count(False), fails[0] if fails else None)), flush=True)
sys.exit(1 if fails else 0)
