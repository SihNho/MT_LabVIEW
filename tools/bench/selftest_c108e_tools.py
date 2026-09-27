r"""selftest_c108e_tools.py - card 108-5 offline self-test (no LabVIEW, no VISA port, no peer dispatch).
FOUND FIRST (reused): selftest_cycle_runner_ladder.py (the --dry-cmd stand-in + temp bench pattern), selftest_leg_guard.py
(leg-loop stubs), diag_c108e_dry_replay.py (the G3 replay of diag_c108b_dry.log, run separately), disp_107_abba.json/.log
(the real VISA-refused ABBA run, 2026-09-27 07:50).
PREDICTION CONTRACT (negatives in brackets):
 G1 gates_due(): fixture peer dir with 1 outcome review then 7 newer retrospectives -> item 'outcome' due True ('7 cycle
    retrospectives'); [outcome review newer than every retrospective -> due False]; items violations/retro-debt present;
    next.json act naming stage_d1_l2a3.py -> an item 'recipe:stage_d1_l2a3.py'; the list validates inside a cycle/1 card
    [a gates_due item with an unknown key is refused by the schema]
 G2 runner --cycles 1 --dry-cmd <session stand-in> --outcome-cmd <outcome stand-in> on the 7-retro fixture: the outcome
    stand-in RAN (its marker exists) BEFORE the session stand-in (marker order + OUTCOME-REVIEW line before CYCLE-CARD),
    card cycle_1.json validates and carries gates_due with outcome 'RAN ... now: not due'; [dry run WITHOUT --outcome-cmd
    -> 'DUE, not dispatched (dry run)', no stand-in marker]
 G3 stage_prerun._UnroutableTap flags diag_c108b_dry.log:39 and the stagexec forms; [a prose line mentioning the word, a
    STEPX line -> not flagged]
 G4 drive_legguard.refusal_verdict on disp_107_abba.json (real refused run) -> SKIP, fail 0; its RESULT line validates and
    protocol.result_failed False; guard_peer.log_failure on disp_107_abba.log with that RESULT + rc 0 -> NOT failed;
    [same with M2 md5 gate False -> FAIL]; [a real leg failure (not refused, rc 1, A before pick 1) -> FAIL, and
    guard_peer arms on it]; [SKIP with gates.fail 1 -> result_failed True]; no refusal + all pass -> PASS
    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c108e_tools.log -- py -u tools/bench/selftest_c108e_tools.py"""
import json
import os
import re
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import protocol as P  # noqa: E402

MODE = sys.argv[1] if len(sys.argv) > 1 else ""
if MODE == "session-stand-in":                      # the runner's --dry-cmd: record WHEN the session would have started
    open(os.environ["C108E_SESSION_MARK"], "w").write("%.6f" % time.time())
    print("dry session stand-in")
    sys.exit(0)
if MODE == "outcome-stand-in":                      # the runner's --outcome-cmd: an outcome review lands in the peer dir
    time.sleep(0.05)
    open(os.environ["C108E_OUTCOME_MARK"], "w").write("%.6f" % time.time())
    open(os.path.join(os.environ["C108E_PEER"], "2026-09-27-outcome-review-stub.md"), "w").write("stub\n")
    print(P.result_line(P.make_result(1, 0)))
    sys.exit(0)

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


import cycle_runner as CR  # noqa: E402


def peer_fixture(n_retro, outcome_last=False):
    d = tempfile.mkdtemp(prefix="c108e_peer_")
    t0 = time.time() - 3600
    op = os.path.join(d, "2026-09-26-outcome-review-20260926.md")
    open(op, "w").write("x\n")
    os.utime(op, (t0, t0))
    for i in range(n_retro):
        p = os.path.join(d, "2026-09-27-retrospective-cycle%d.md" % (100 + i))
        open(p, "w").write("- **outcome:** ANSWERED\n")
        os.utime(p, (t0 + 60 * (i + 1), t0 + 60 * (i + 1)))
    if outcome_last:
        os.utime(op, (t0 + 60 * (n_retro + 5),) * 2)
    return d


def bench_fixture(act):
    b = tempfile.mkdtemp(prefix="c108e_bench_")
    open(os.path.join(b, "STATUS.md"), "w", encoding="utf-8").write("## NEXT\nx\n")
    nx = {"schema": "next/1", "cycle": 0, "act": act, "task_kind": "build", "stop_requested": False, "unblocks": "M3"}
    json.dump(nx, open(os.path.join(b, "next.json"), "w", encoding="utf-8"))
    return b


# ------------------------------------------------------------------ G1
peer7 = peer_fixture(7)
nx = {"act": "L2-A3 launch of tools/recipes/stage_d1_l2a3.py after re-plan"}
items = CR.gates_due(tempfile.mkdtemp(), peer7, nx)
by = dict((x["gate"], x) for x in items)
gate("G1a 7 retros since the last outcome review -> gates_due 'outcome' due True",
     by.get("outcome", {}).get("due") is True and "7 cycle retrospectives" in by["outcome"]["detail"], by.get("outcome"))
gate("G1b items violations + retro-debt present (bool or null), recipe:stage_d1_l2a3.py present",
     "violations" in by and "retro-debt" in by and "recipe:stage_d1_l2a3.py" in by, [(x["gate"], x["due"]) for x in items])
items0 = CR.gates_due(tempfile.mkdtemp(), peer_fixture(7, outcome_last=True), {"act": "no recipe named"})
by0 = dict((x["gate"], x) for x in items0)
gate("G1c [outcome review newer than every retrospective -> due False; no recipe item]",
     by0.get("outcome", {}).get("due") is False and not any(k.startswith("recipe:") for k in by0), by0.get("outcome"))
card = {"schema": "cycle/1", "cycle": 1, "rig_state": "unknown", "model": "m", "effort": "high", "next": "x",
        "budget": {"minutes": 1.0, "dispatches": 8}, "gates_due": items}
ok1, why1 = P.validate_obj(card)
bad_card = dict(card, gates_due=[dict(items[0], extra=1)])
ok2, why2 = P.validate_obj(bad_card)
gate("G1d cycle/1 with gates_due validates; [an item with an unknown key is refused]", ok1 and not ok2, (why1, why2))

# ------------------------------------------------------------------ G2
def run_runner(peer, outcome_cmd):
    b = bench_fixture("build per plan")
    marks = {"s": os.path.join(b, "session.mark"), "o": os.path.join(b, "outcome.mark")}
    env = dict(os.environ, C108E_SESSION_MARK=marks["s"], C108E_OUTCOME_MARK=marks["o"], C108E_PEER=peer)
    argv = [sys.executable, os.path.join(ROOT, "tools", "cycle_runner.py"), "--cycles", "1", "--bench-dir", b,
            "--status", os.path.join(b, "STATUS.md"), "--peer-dir", peer, "--goalmap", os.path.join(b, "nogoalmap.json"),
            "--no-motor-hooks", "--no-errorlist-hook", "--no-labview-close",
            "--dry-cmd", "py tools/bench/selftest_c108e_tools.py session-stand-in"]
    if outcome_cmd:
        argv += ["--outcome-cmd", "py tools/bench/selftest_c108e_tools.py outcome-stand-in"]
    r = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=ROOT,
                       timeout=600)
    log = open(os.path.join(b, "cycle_runner.log"), encoding="utf-8").read() if os.path.isfile(
        os.path.join(b, "cycle_runner.log")) else ""
    try:
        c = json.load(open(os.path.join(b, "cards", "cycle_1.json"), encoding="utf-8"))
    except (OSError, ValueError):
        c = {}
    rd = lambda p: float(open(p).read()) if os.path.isfile(p) else None  # noqa: E731
    return r, log, c, rd(marks["s"]), rd(marks["o"])


r, log, c, ts, to = run_runner(peer_fixture(7), True)
oc = next((x for x in c.get("gates_due") or [] if x["gate"] == "outcome"), {})
ln = log.splitlines()
i_or = next((i for i, x in enumerate(ln) if x.startswith("OUTCOME-REVIEW") and "running before the session" in x), None)
i_cc = next((i for i, x in enumerate(ln) if x.startswith("CYCLE-CARD")), None)
gate("G2a due outcome review RAN before the session: stand-in marker < session marker, OUTCOME-REVIEW before CYCLE-CARD",
     to is not None and ts is not None and to < ts and i_or is not None and i_cc is not None and i_or < i_cc,
     "outcome %s session %s lines %s<%s rc %s" % (to, ts, i_or, i_cc, r.returncode))
ok_c, why_c = P.validate_obj(c) if c else (False, "no card")
gate("G2b cycle_1.json validates; gates_due outcome RAN, now not due", ok_c and oc.get("due") is False and
     oc.get("detail", "").startswith("RAN before the session"), (why_c, oc))
if not (gates[-1][1] and gates[-2][1]):
    print(log[-3000:], r.stdout[-1500:], r.stderr[-1500:])
r, log, c, ts, to = run_runner(peer_fixture(7), False)
oc = next((x for x in c.get("gates_due") or [] if x["gate"] == "outcome"), {})
gate("G2c [dry run without --outcome-cmd -> 'DUE, not dispatched (dry run)', card outcome due True, no stand-in ran]",
     "DUE, not dispatched (dry run)" in log and oc.get("due") is True and to is None and ts is not None, oc)

# ------------------------------------------------------------------ G3
import io  # noqa: E402
import stage_prerun as SP  # noqa: E402
dry_log = open(os.path.join(HERE, "diag_c108b_dry.log"), encoding="utf-8").read().splitlines()
buf = io.StringIO()
tap = SP._UnroutableTap(buf)
for x in [dry_log[38], "  UNROUTABLE acts [7] ids ['x']: y", "UNROUTABLE 2 row(s): acts [1]; acts [2]",
          "PRIOR ART: the UNROUTABLE rule of stagexec", dry_log[35], "  STEPX 06 connect diff 0"]:
    tap.write(x + "\n")
tap.flush_tail()
gate("G3 tap flags diag_c108b_dry.log:39 + 2 stagexec forms; [prose + STEPX lines not flagged]; output passes through",
     len(tap.hits) == 3 and tap.hits[0] == dry_log[38] and buf.getvalue().count("\n") == 6, tap.hits)

# ------------------------------------------------------------------ G4
import drive_legguard as LG  # noqa: E402
sys.path.append(os.path.join(ROOT, "tools", "hooks"))
import guard_peer as GP  # noqa: E402
dj = json.load(open(os.path.join(HERE, "disp_107_abba.json"), encoding="utf-8"))
g107, rows107, stop107 = dict(dj["gates"]), dj["rows"], dj.get("leg_loop_stop")
st, npass, nfail, first = LG.refusal_verdict(g107, rows107, stop107)
line = P.result_line(P.make_result(npass, nfail, first, status=st))
d = P.parse_result_line(line)
gate("G4a disp_107 (VISA-refused) -> SKIP, fail 0, RESULT validates, result_failed False",
     st == "SKIP" and nfail == 0 and d and d["status"] == "SKIP" and not P.result_failed(d), line)
txt = open(os.path.join(HERE, "disp_107_abba.log"), encoding="utf-8").read()
now = time.strftime("%Y-%m-%d %H:%M:%S")
body = re.sub(r"^BGRUN START \S+ \S+", "BGRUN START " + now, txt, count=1, flags=re.M)
body = re.sub(r"^RESULT .*$", line, body, flags=re.M)
body = re.sub(r"^BGRUN END rc=\d+", "BGRUN END rc=0", body, flags=re.M)
f_skip = GP.log_failure(body, time.time())
f_old = GP.log_failure(re.sub(r"^BGRUN START \S+ \S+", "BGRUN START " + now, txt, count=1, flags=re.M), time.time())
gate("G4b guard_peer does NOT arm on the SKIP replay of disp_107_abba.log; [the original FAIL text still arms]",
     f_skip[0] is False and f_old[0] is True, (f_skip, f_old[1][:120]))
g2 = dict(g107)
g2[[k for k in g2 if k.startswith("M2 ")][0]] = False
st2 = LG.refusal_verdict(g2, rows107, stop107)
gate("G4c [refused run with M2 md5 gate False -> FAIL on M2]", st2[0] == "FAIL" and st2[3].startswith("M2 "), st2)
rows_f = [{"leg": "leg1 A@15", "slot": 1, "arm": "A", "rc": 1, "registered_ok": False, "picks_clicked": 0}]
g3 = {"V1 leg1 A@15 VISA precheck Rotor+ASRL5 status 0": True, "T1 leg1 A@15 rc 0": False,
      "T12 slot1 A@15 registered == target (<= 1 rerun)": False,
      "T17 leg loop ran every slot (stopped: A leg failed before pick 1 (rc 1))": False, "T7 camera restored 90 Hz": True}
st3 = LG.refusal_verdict(g3, rows_f, {"slot": 1, "arm": "A", "reason": "A leg failed before pick 1 (rc 1)"})
l3 = P.result_line(P.make_result(st3[1], st3[2], st3[3], status=st3[0]))
b3 = "BGRUN START %s limit 60.0 min: py -u tools/bench/diag_c104_abba.py\n%s\nBGRUN END rc=1 after 5s\n" % (now, l3)
gate("G4d [a real leg failure (not refused) -> FAIL, guard_peer arms]", st3[0] == "FAIL" and st3[2] == 3
     and GP.log_failure(b3, time.time())[0] is True, st3)
gate("G4e [SKIP with gates.fail 1 -> result_failed True]; no refusal + all pass -> PASS",
     P.result_failed({"status": "SKIP", "gates": {"pass": 1, "fail": 1}})
     and LG.refusal_verdict({"a": True}, [], None)[0] == "PASS", "")

n_pass = sum(ok for _, ok in gates)
first = next((l for l, ok in gates if not ok), None)
print("%d/%d PASS" % (n_pass, len(gates)), flush=True)
print(P.result_line(P.make_result(n_pass, len(gates) - n_pass, first)), flush=True)
sys.stdout.flush()
os._exit(0 if n_pass == len(gates) else 1)
