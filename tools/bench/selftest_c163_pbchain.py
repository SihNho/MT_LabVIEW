# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c163_a1_4_ctx.log
# ---
r"""selftest_c163_pbchain - card 163-a1-4 (gate-fp fp-86), OFFLINE on STORED data (no LabVIEW).
Shared functions under test (stagekit): pb_inherit_ctx (+ chain_connects / chain_tunnel_case: the adopted plans' wire actions onto base
terminals and their tunnels, through each step's recorded run bindings) and pb_inherited_row class 3 (class 2 CARRIED: a row an ADOPTED
earlier plan wired into an adopted case, untouched since the base), via pb_check_bound(inherit=).
Data: plan_ring_p5s02c.json sim end re-keyed by the dry's bindings (prep_c163_a1_3_dry.log STEPX 01-07; same construction as
selftest_c161_pbinherit.py:43-48); adopted chain from adopted_scratch.jsonl (newest p5s02b = the plan that wired #376 t0/t1, w_g376 / w_h376).
PREDICTION (gates):
 C0  chain_connects (376,'error in') -> (p5s02b, w_g376), (376,'total data array in') -> (p5s02b, w_h376); tunnels 31593 31598 31628 31640
     -> (p5s02b, case 31308); case 31308 frames [31506, 31517]; nothing missing.
 A1  p5s02c: #376 error in / total data array in RECORDED class 3 (w_g376 / w_h376); cal cluster path, file size, selected path class 1;
     PB ok, blocked [], pairs_extra_left []; eq_diff / pairs_missing / n_rows / old dict == the inherit-off run.
 A2  ctx WITHOUT chain_connects (= stagekit before the edit) -> the 2 rows BLOCKED, PB not ok (163-a1-3's dry verdict reproduced).
 N1  a tag on a frame outside the chain (999993) -> BLOCK.          N2  a source terminal uid changed -> BLOCK.
 N3  multiplicity 3 (an entry duplicated) / 1 (an entry dropped) -> BLOCK.
 N4  a tag on a tunnel the wiring plan did not create (999995) -> BLOCK.
 N5  base PB != end (bound_end altered) -> BLOCK.        N6  chain_connects naming p5s02a (whose tunnels are not on these tags) -> BLOCK.
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c163_pbchain.log -- py -u tools/bench/selftest_c163_pbchain.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


V, SX, JC = K.pure("vigraph"), K.pure("stagexec"), K.pure("jev_candidates")
LAB = JC.node_labels_default()
S1f = K.s1_frame_graph(LAB)
P = K.jload(K.BENCH, "plan_ring_p5s02c.json")
PRED = K.jload(K.BENCH, "plan_ring_p5s02c_pred.json")
FS = K.jload(K.ROOT, P["finalized"]["base"]["path"]).get("fs_tunnel_pairs")
FLAT = {-1: 10000001, -2: 10000004, -7: 10000007, -10: 10000010, -13: 10000015, -19: 10000021}   # the dry's bindings (prep_c163_a1_3_dry.log)
L = K.jload(K.ROOT, P["finalized"]["step_files"][-1]["path"])["state"]
Gb = K.pred_end_graph(SX.bind_state(L, {"obj": FLAT, "term": {}, "diag": {}})[0], LAB, FS)
Gp = K.pred_end_graph(L, LAB, FS)
mf = K.case_move_frames(P, L, FLAT)
ctx = K.pb_inherit_ctx(P, FLAT, labels=LAB, fs_pairs=FS, S1f=S1f, V=V)
B2 = "tools/bench/plan_ring_p5s02b.json"
cc, tc = ctx["chain_connects"], ctx["chain_tunnel_case"]
gate("C0 chain_connects #376 t0/t1 -> p5s02b w_g376/w_h376; tunnels 31593/31598/31628/31640 -> (p5s02b, 31308); case 31308 [31506,31517]; no missing",
     cc.get((376, "error in")) == (B2, "w_g376") and cc.get((376, "total data array in")) == (B2, "w_h376")
     and all(tc.get(u) == (B2, 31308) for u in (31593, 31598, 31628, 31640)) and ctx["cases"].get(31308) == [31506, 31517] and not ctx["missing"],
     {"cc376": dict((k, v) for k, v in cc.items() if k[0] == 376), "tc": dict((u, v) for u, v in tc.items() if v[0] == B2), "missing": ctx["missing"]})
run = lambda c: K.pb_check_bound(S1f, Gb, Gp, Gb, PRED["cdiff_rows"], P["open_rows"], mf, (), V, inherit=c)   # noqa: E731
r_off, r_on = run(None), run(ctx)
cls = dict((x["sink"].split("|")[2], (x.get("class"), x.get("action"))) for x in r_on["recorded"])
WANT = {"cal cluster path": (1, None), "file size": (1, None), "selected path": (1, None), "error in": (3, "w_g376"),
        "total data array in": (3, "w_h376")}
same = all(r_on[k] == r_off[k] for k in ("eq_diff", "pairs_missing", "n_rows")) and all(
    r_on["old"][k] == r_off["old"][k] for k in r_off["old"] if k != "cd")
gate("A1 p5s02c: #376 error in / total data array in class 3, 3 rows class 1; PB ok, blocked [], extra_left []; other outputs == inherit off",
     cls == WANT and r_on["ok"] and not r_on["blocked"] and r_on["pairs_extra_left"] == [] and same,
     {"classes": cls, "ok": r_on["ok"], "blocked": r_on["blocked"], "left": r_on["pairs_extra_left"], "same": same})
c_old = dict(ctx, chain_connects={}, chain_tunnel_case={})
r_old = run(c_old)
gate("A2 ctx without the chain (stagekit before the edit) -> #376 error in / total data array in BLOCKED, PB not ok",
     not r_old["ok"] and sorted(x["sink"] for x in r_old["blocked"]) == ["376|Terminal|error in|0", "376|Terminal|total data array in|0"],
     [x["sink"] for x in r_old["blocked"]])
by = dict((y["sink"], y) for y in r_on["old"]["cd"]["rows"])
fm = K.frame_tag_map(Gb)
RB = K.pb_bound_rows(r_on["old"]["cd"], Gb, V)
SK = dict((s.split("|")[2], s) for s in by if s.startswith("376|"))
res0 = lambda n: [K.frame_src_resolve(x, fm) for x in by[SK[n]]["after"]]   # noqa: E731


def row(name, res=None, G1=None, c=None, bound=None):
    s = SK[name]
    return K.pb_inherited_row(s, by[s], res if res is not None else res0(name), G1 or Gb, S1f, RB.get(s) if bound is None else bound, c or ctx)


def g_uid(src_key, uid):
    G1 = dict(Gb)
    G1["rows"] = dict(Gb["rows"])
    G1["rows"][src_key] = dict(Gb["rows"][src_key], term_uid=uid)
    return G1


NM = ("error in", "total data array in")
pos = [row(n) for n in NM]
gate("A3 pb_inherited_row direct: both rows class 3", [x[0] for x in pos] == [3, 3], pos)
n1 = [row(n, res=[(b, frozenset((tn, 999993 if f == 31517 else f) for tn, f in t)) for b, t in res0(n)]) for n in NM]
gate("N1 a tag on frame 999993 (not in the chain) -> BLOCK", all(x[0] is None for x in n1), n1)
n2 = [row(n, G1=g_uid(res0(n)[0][0], 999991)) for n in NM]
gate("N2 a source terminal uid changed (999991) -> BLOCK", all(x[0] is None for x in n2), n2)
n3 = [row(n, res=res0(n) + [res0(n)[0]]) for n in NM] + [row(n, res=res0(n)[1:]) for n in NM]
gate("N3 multiplicity 3 (entry duplicated) / 1 (entry dropped) -> BLOCK", all(x[0] is None for x in n3), n3)
n4 = [row(n, res=[(b, frozenset((999995 if i == 0 else tn, f) for i, (tn, f) in enumerate(sorted(t)))) for b, t in res0(n)]) for n in NM]
gate("N4 a tag on tunnel 999995 (not created by the wiring plan) -> BLOCK", all(x[0] is None for x in n4), n4)
n5 = [row(n, bound=frozenset(list(RB.get(SK[n]))[1:])) for n in NM]
gate("N5 base PB != end (one bound row dropped) -> BLOCK", all(x[0] is None for x in n5), n5)
cc6 = dict(cc)
cc6.update({(376, "error in"): ("tools/bench/plan_ring_p5s02a.json", "x"), (376, "total data array in"): ("tools/bench/plan_ring_p5s02a.json", "y")})
c6 = dict(ctx, chain_connects=cc6)
n6 = [row(n, c=c6) for n in NM]
gate("N6 chain_connects naming p5s02a (tags are p5s02b's tunnels) -> BLOCK", all(x[0] is None for x in n6), n6)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
