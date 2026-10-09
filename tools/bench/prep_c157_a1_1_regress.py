# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_157-a1-1.md
# ---
r"""prep_c157_a1_1_regress - card 157-a1-1 measurements 1, 2 and 4 (OFFLINE, json only, no LabVIEW, no COM).
WHAT EXISTED FIRST and is CALLED, not copied: prep_c156_a1_2_lib.compile_all / run_suite / jload / md5 (its SUITE list is extended
here by assignment, the runner is the lib's), stagexec.compile_plan, stagekit.RingSession (built, never run - as selftest_t7_ring.py
R1/R2 does).
  before : store the compiled op lists of plan_ring_p5s01a / p5s01b / p5s02a, every stored plan's compile (compile_all), each
           ring P5 recipe's RingSession.CHECKPOINTS, into tools/bench/sim/ring_p5s02a_c157/before.json; run the suite (tag c157before).
           Also prints the recorded rows the self-test needs (step 10-12 only_sink, sinks on the six wires, owners of #24357/#24361,
           recorded SelectorTunnel inner faces).
  after  : the same, compared with before.json; suite tag c157after.
PREDICTION CONTRACT (after): op lists of the three plans EQUAL; every stored plan's compile EQUAL; CHECKPOINTS of each recipe differ
from before only by the plan's move_in ops (p5s02a: + 10, 11, 12; the others: none); each suite entry keeps its before counts.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/prep_c157_a1_1_before.log -- py -u tools/bench/prep_c157_a1_1_regress.py before"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import protocol  # noqa: E402
import prep_c156_a1_2_lib as L  # noqa: E402
import stagexec as SX  # noqa: E402
import stagekit as K  # noqa: E402

OUT = os.path.join(HERE, "sim", "ring_p5s02a_c157")
PLANS = ["plan_ring_p5s01a.json", "plan_ring_p5s01b.json", "plan_ring_p5s02a.json"]
RECIPES = [("stage_d1_ring_p5s01a", "plan_ring_p5s01a", "prep_c154_a3_2b_session.json"),
           ("stage_d1_ring_p5s01b", "plan_ring_p5s01b", "prep_c155_a2_1_session.json"),
           ("stage_d1_ring_p5s02", "plan_ring_p5s02", "prep_c155_a4_1_session.json"),
           ("stage_d1_ring_p5s02a", "plan_ring_p5s02a", "prep_c156_a1_1_session.json")]
L.SUITE = L.SUITE + [("addrcheck_s5", ["tools/bench/selftest_s5.py"]), ("t7_ring", ["tools/bench/selftest_t7_ring.py"]),
                     ("c156_passwire", ["tools/bench/selftest_c156_passwire.py"])]
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


def record():
    """{md5, ops, compile_all, checkpoints, move_in} measured with the tools as they are now."""
    rec = {"md5": dict((m, L.md5(os.path.join(ROOT, "tools", m + ".py"))) for m in ("stagexec", "stagesim", "addrcheck", "stagekit")),
           "ops": {}, "checkpoints": {}, "move_in": {}}
    for p in PLANS:
        rec["ops"][p] = json.loads(json.dumps(SX.compile_plan(L.jload(os.path.join(HERE, p))), sort_keys=True, default=str))
    for name, stem, census in RECIPES:
        rs = K.RingSession(os.path.join(HERE, stem + ".json"), os.path.join(HERE, stem + "_pred.json"),
                           os.path.join(HERE, stem + "_licence.json"), os.path.join(HERE, census))
        ops = SX.compile_plan(rs.P)
        rec["checkpoints"][name] = list(rs.CHECKPOINTS)
        rec["move_in"][name] = [k for k, o in enumerate(ops, 1) if o["kind"] == "move_in"]
    rec["compile_all"] = L.compile_all()
    return rec


def recorded_rows():
    """FACT lines: the recorded sim rows the c157 self-test builds on."""
    P = L.jload(os.path.join(HERE, "plan_ring_p5s02a.json"))
    steps = dict((int(s["n"]), os.path.join(ROOT, s["path"])) for s in P["finalized"]["step_files"])
    for n in (10, 11, 12):
        eff = L.jload(steps[n]).get("effect") or {}
        print("FACT step_{0:02d} only_sink {1} allow_either {2}".format(n, eff.get("only_sink"), eff.get("allow_either")), flush=True)
    s9 = L.jload(steps[9])["state"]
    for w in (10394, 24091, 24153, 24285, 24312, 24330):
        print("FACT step_09 wire {0} rows {1}".format(w, sorted(L.term_brief(r) + (r["is_source"],) for r in s9["terminals"]
                                                               if r["wire_uid"] == w)), flush=True)
    s15 = L.jload(steps[15])["state"]
    for t in (24357, 24361):
        fr = sorted(set(r["frame_diagram"] for r in s15["terminals"] if r["owner_uid"] == t and r["term_class"] == "InnerTerminal"))
        print("FACT step_15 LoopTunnel #{0} inner frames {1} owners {2}".format(t, fr, [(f, (s15.get("owners") or {}).get(str(f)))
                                                                                    for f in fr]), flush=True)
    sel = [L.term_brief(r) for r in s15["terminals"] if r["owner_class"] in ("SelectorTunnel", "FlatSequenceInnerTunnel")
           and r["term_class"] == "InnerTerminal"]
    print("FACT step_15 SelectorTunnel/FSIT inner faces {0} (first 6) {1}".format(len(sel), sel[:6]), flush=True)


mode = sys.argv[1] if len(sys.argv) > 1 else "after"
os.makedirs(OUT, exist_ok=True)
now = record()
print("FACT md5 {0}".format(now["md5"]), flush=True)
print("FACT checkpoints {0}".format(now["checkpoints"]), flush=True)
print("FACT move_in ops {0}".format(now["move_in"]), flush=True)
print("FACT op counts {0}".format(dict((p, len(v)) for p, v in now["ops"].items())), flush=True)
if mode == "before":
    recorded_rows()
    with open(os.path.join(OUT, "before.json"), "w", encoding="utf-8") as f:
        json.dump(now, f, sort_keys=True)
    gate("B before.json written ({0} stored plans compiled)".format(len(now["compile_all"])), True)
else:
    bef = L.jload(os.path.join(OUT, "before.json"))
    for p in PLANS:
        gate("A1 {0} op list EQUAL to before ({1} ops)".format(p, len(now["ops"][p])), now["ops"][p] == bef["ops"][p])
    diff = sorted(k for k in set(bef["compile_all"]) | set(now["compile_all"]) if bef["compile_all"].get(k) != now["compile_all"].get(k))
    gate("A2 every stored plan compiles EQUAL to before ({0} plans, {1} differ)".format(len(now["compile_all"]), len(diff)), not diff, diff[:10])
    for name in now["checkpoints"]:
        b, a = set(bef["checkpoints"][name]), set(now["checkpoints"][name])
        gate("A3 {0} CHECKPOINTS after == before + its move_in ops {1}".format(name, now["move_in"][name]),
             a == b | set(now["move_in"][name]) and b <= a, {"before": sorted(b), "after": sorted(a)})
    gate("A4 p5s02a CHECKPOINTS == [1,3,6,8,9,15,16,17] + [10,11,12] sorted (+ 0)",
         [k for k in now["checkpoints"]["stage_d1_ring_p5s02a"] if k] == [1, 3, 6, 8, 9, 10, 11, 12, 15, 16, 17],
         now["checkpoints"]["stage_d1_ring_p5s02a"])
for name, rc, npass, nfail, last in L.run_suite("c157" + mode, outdir=OUT):
    print("SUITE {0} rc={1} PASS-lines={2} FAIL-lines={3} | {4}".format(name, rc, npass, nfail, last), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
