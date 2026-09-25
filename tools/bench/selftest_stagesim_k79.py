r"""selftest_stagesim_k79 - card 79-7 M2: the simulator's step after K op 3 (move_in #5058) must EQUAL the headless LabVIEW
read tools/bench/k_op3_read_79.json (M1, k_op3_read_79.log). Pure Python, no LabVIEW.
  S1 the fixture is the M1 read of THIS plan's op 3 on the bed 4b621946 (schema, bed md5, sim_step 3);
  S2 the CURRENT sim step file for op 3 (tools/bench/sim/k_split, written by sim_k_split.py) vs the fixture: stagexec.compare
     n == 0 (edges + dangling terminals, the executor's own E1 comparison);
  S3 re-applying op_move_in to the step-2 state with the measured move_in model reproduces the same (n == 0);
  S4 NEGATIVE CONTROL: the same re-application with the flip restricted to the OLD classes (TUN1, LoopTunnel/Tunnel) gives
     the 79-6 divergence back (only_sim_edges [[2789,6253],[2792,5910]]) - so S2/S3 pass BECAUSE of the widened rule.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stagesim_k79.log -- py -u tools/bench/selftest_stagesim_k79.py"""
import copy, json, os, sys                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))   # noqa: E702
import stagesim as S, stagexec as SX, jev_candidates as JC, protocol               # noqa: E401,E402
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


FIX = os.path.join(HERE, "k_op3_read_79.json")
PLAN = os.path.join(HERE, "plan_k_split.json")
F = json.load(open(FIX, encoding="utf-8"))
P = json.load(open(PLAN, encoding="utf-8"))
steps = P["finalized"]["steps"] if "steps" in P.get("finalized", {}) else None
gate("S1 fixture = M1 read of op 3 on bed 4b621946", F.get("schema") == "k_op3_read/1" and F.get("sim_step") == 3 and
     F.get("bed_md5") == "4b621946492da3d2fbb96b6053e715ec", (F.get("schema"), F.get("sim_step"), F.get("bed_md5"), S.md5_file(FIX)))
ex = SX.Executor(PLAN, None, log=lambda *_a: None)
st3 = ex.step(3)
d = SX.compare(st3["state"]["terminals"], F["terminals"], {"obj": {}, "term": {}})
gate("S2 current sim step 3 ({0}) == the M1 read (stagexec.compare n == 0)".format(ex.step_paths[3] if isinstance(ex.step_paths[3], str)
     else ex.step_paths[3]), d["n"] == 0, {k: v for k, v in d.items() if v})
print("  FACT  step 3 tunnel_flips: {0}".format((st3.get("effect") or {}).get("tunnel_flips")), flush=True)
a3 = P["actions"][2]
models = S.load_models()
Pm, src, _ev, _g = S.model_for("move_in", models)
S1g, labels = S.load_s1(P), JC.node_labels_default()


def reapply():
    st = copy.deepcopy(ex.step(2)["state"])
    eff, _c = S.op_move_in(st, a3, Pm, S1g, labels)
    return SX.compare(st["terminals"], F["terminals"], {"obj": {}, "term": {}}), eff


d3, eff3 = reapply()
gate("S3 op_move_in re-applied to step 2 with {0} reproduces the M1 read (n == 0)".format(src), d3["n"] == 0,
     {"diff": {k: v for k, v in d3.items() if v}, "flips": eff3.get("tunnel_flips")})
old = S.TUN_FLIP
S.TUN_FLIP = S.TUN1
try:
    d4, _e = reapply()
finally:
    S.TUN_FLIP = old
gate("S4 NEGATIVE: flip restricted to TUN1 gives the 79-6 divergence back", d4["n"] > 0 and
     d4.get("only_sim_edges") == [(2789, 6253), (2792, 5910)] or [list(x) for x in d4.get("only_sim_edges", [])] == [[2789, 6253], [2792, 5910]],
     {k: v for k, v in d4.items() if v and k != "who"})
n_pass = sum(1 for _l, ok in GATES if ok)
first = next((l for l, ok in GATES if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, len(GATES) - n_pass))
print(protocol.result_line(protocol.make_result(n_pass, len(GATES) - n_pass, first)))
sys.exit(0 if first is None else 1)
