r"""selftest_stage_prerun_c128b - card 128-4 (PD261(b), gate-fp X5): X5 counts RLE ops 1:1 against plan RLE rows; an
in-process --dry then --prerun counts once. PURE PYTHON, no LabVIEW (COM stubbed by stage_prerun.install).
EXISTING FIRST: selftest_stage_prerun_c128.py (builtins.open restore, 3/0), diag_c128_3_x5.py (M1 trace, M2 repro, wrapdepth).
Fixture: diag_c128_3_recipe_dry.json (128-3's fresh-process dry trace of stage_d1_ring_p3b.py, 63 ops) + the plan it ran,
plan_ring_p3b.json md5 4003eaa5... (pinned; if the plan file moves on, T1-T3 use the recorded copy in the trace's own plan).
RE-PINNED card 130-5 (PD268(c)): the 63-action 4003eaa5 fixture was finalized before stagesim 129-7 (its dry stopped at op 48,
archive/peer/2026-10-02-hyp-c130-4-c128b.md); the fixture is now the RE-FINALIZED unsplit 70 (plan_ring_p3b.json, REFERENCE, never
launched, written by plan_ring_p3b_split.py S1u) and the trace selftest_stage_prerun_c128b_trace.json (fresh-process --dry of
stage_d1_ring_p3b.py on it, --json-out). Counts follow the 70 rows: 25 create, 16 wire, 14 crossing, 15 RLE.
Prediction contract: T1-T5 PASS -
  T1 x5_count(trace, P3b plan) PASS: wiring 30 == 16 wire + 14 crossings, RLE 15 == 15
  T2 NEGATIVE: the same trace + one extra `wire_connect` FAILS
  T3 NEGATIVE: the same trace + one extra `wire_remove_loose_ends` FAILS (an unplanned RLE op is not free)
  T4 in-process main --dry then main --prerun on stage_d1_ring_p3b.py: D.ops 70 after EACH, Stage._op wrap depth 1 after each
  T5 the in-process --prerun's X5 line is PASS
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_stage_prerun_c128b.log -- py -u tools/bench/selftest_stage_prerun_c128b.py
"""
import builtins, contextlib, hashlib, importlib, io, json, os, sys    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)  # noqa: E702
sys.path.insert(0, TOOLS)
import stage_prerun as SP, stagexec as SX, protocol    # noqa: E401,E402
REAL_OPEN = builtins.open
G = []


def gate(l, ok, d=""):
    G.append((l, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:600]), flush=True)


PLAN_P = os.path.join(HERE, "plan_ring_p3b.json")
REC = os.path.join(TOOLS, "recipes", "stage_d1_ring_p3b.py")
pm = hashlib.md5(open(PLAN_P, "rb").read()).hexdigest()
tr = json.load(open(os.path.join(HERE, "selftest_stage_prerun_c128b_trace.json"), encoding="utf-8"))
print("  FACT plan_ring_p3b.json md5 {0} (trace taken on {1})".format(pm, tr.get("plan_md5")), flush=True)
PLAN = json.load(open(PLAN_P, encoding="utf-8"))
gate("T0 fixture pinned: plan_ring_p3b.json md5 == the trace's plan md5, 70 actions",
     pm == tr.get("plan_md5") and len(PLAN["actions"]) == 70, (pm, tr.get("plan_md5"), len(PLAN["actions"])))
ops = list(tr["ops"])
spc = {PLAN_P: (True, None, PLAN, SX.compile_plan(PLAN))}
ok1, d1 = SP.x5_count(ops, [], spc)
gate("T1 x5_count(P3b fresh-process trace, plan_ring_p3b.json) PASS: 30 wiring + 15 RLE, each 1:1",
     ok1 and "ops 30 vs plan wire rows 0 + stageplan wiring real ops 30" in d1 and "RLE ops 15 vs plan RLE rows 15" in d1, d1)
ok2, d2 = SP.x5_count(ops + ["wire_connect"], [], spc)
gate("T2 NEGATIVE: one extra wire_connect FAILS", not ok2, d2)
ok3, d3 = SP.x5_count(ops + ["wire_remove_loose_ends"], [], spc)
gate("T3 NEGATIVE: one extra wire_remove_loose_ends FAILS", not ok3, d3)


def wrapdepth():
    S, n = importlib.import_module("stagekit").Stage._op, 0
    while getattr(S, "__closure__", None):
        nxt = [c.cell_contents for c in S.__closure__ if isinstance(c.cell_contents, dict) and "_op" in c.cell_contents]
        if not nxt:
            break
        S, n = nxt[0]["_op"], n + 1
    return n


seq = []
for mode in ("--dry", "--prerun"):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = SP.main([mode, REC, "--no-record"])
        except SystemExit as e:
            rc = e.code
    out = buf.getvalue()
    x5l = [ln.strip() for ln in out.splitlines() if " X5 " in ln][:1]
    seq.append({"mode": mode, "rc": rc, "D.ops": len(SP.D.ops), "depth": wrapdepth(), "x5_line": x5l,
                "result": [ln for ln in out.splitlines() if ln.startswith("RESULT")][-1:]})
    print("  FACT in-process {0}: {1}".format(mode, json.dumps(seq[-1], default=str)[:900]), flush=True)
builtins.open = REAL_OPEN
gate("T4 in-process --dry then --prerun: D.ops 70 after EACH call, Stage._op wrap depth 1 after each; the --dry rc 0",
     [s["D.ops"] for s in seq] == [70, 70] and seq[0]["rc"] == 0 and [s["depth"] for s in seq] == [1, 1], [(s["D.ops"], s["depth"]) for s in seq])
gate("T5 the in-process --prerun's X5 line is PASS", bool(seq[1]["x5_line"]) and seq[1]["x5_line"][0].startswith("PASS"),
     seq[1]["x5_line"])
np_, nf = sum(1 for _l, c in G if c), sum(1 for _l, c in G if not c)
print(protocol.result_line(protocol.make_result(np_, nf, next((l for l, c in G if not c), None))), flush=True)
os._exit(1 if nf else 0)
