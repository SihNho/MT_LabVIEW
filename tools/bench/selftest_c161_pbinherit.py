# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c161_a2_1_facts.md
# ---
r"""selftest_c161_pbinherit - card 161-a3-1 (docs/d1/ring-p5b.md PD394(a), PD395(b)(c)), OFFLINE on STORED data (no LabVIEW).
Shared functions under test (stagekit): pb_inherit_ctx (the adopted chain's case frames, from adopted_scratch.jsonl + each step's scratch
`stagexec` bindings), pb_inherited_row (class 1 / class 2 of ONE pred-extra PB row), and pb_check_bound / pb_386 which call it (inherit=).
Data: plan_ring_p5s02b.json sim end (G1 := the sim end re-keyed by the dry's bindings, prep_c161_b1_2_measure.py:27, as 161-a2-1 did); the
adopted scratch records p5s01a / p5s01b / p5s02a (adopted_scratch.jsonl:9-11, their json real_end_rows + stagexec bindings).
PREDICTION (gates):
 C0  ctx: inherited frames {376, 3052, 3453: [31506]}; adopted case 31308 -> frames [31506, 31517]; nothing missing.
 A1  p5s02b sim end: the 5 #376 rows RECORDED, class 1 = cal cluster path, file size; class 2 = selected path (w_in3_376), error in
     (w_g376), total data array in (w_h376); PB ok, pairs_extra_left []; eq_diff / pairs_missing / n_rows / old dict == the inherit-off run.
 B1  changed source uid (class-1 and class-2 row) -> BLOCK.   B2  a tag on a frame of a non-adopted case -> BLOCK.
 B3  an f1 tag on a sink outside PD374(d)'s pass-through (selected path, multiplicity = frame count) -> BLOCK.
 B4  a class-2 row with no connect action (ctx without w_in3_376) -> BLOCK, and PB (pb_check_bound) not ok.
 B5  multiplicity 3 on error in / 2 on selected path -> BLOCK.
 R1-R3  stored p5s01a / p5s01b / p5s02a: pb_386 with inherit off == inherit on (ok, rows, recorded, blocked); counts vs the stored run.
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c161_pbinherit.log -- py -u tools/bench/selftest_c161_pbinherit.py"""
import json
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
P = K.jload(K.BENCH, "plan_ring_p5s02b.json")
PRED = K.jload(K.BENCH, "plan_ring_p5s02b_pred.json")
FS = K.jload(K.ROOT, P["finalized"]["base"]["path"]).get("fs_tunnel_pairs")
FLAT = {-1: 10000003, -7: 10000008, -12: 10000014, -19: 10000020, -24: 10000026}   # the dry's bindings (prep_c161_b1_2_measure.py:27)
L = K.jload(K.ROOT, P["finalized"]["step_files"][-1]["path"])["state"]
Gb = K.pred_end_graph(SX.bind_state(L, {"obj": FLAT, "term": {}, "diag": {}})[0], LAB, FS)
Gp = K.pred_end_graph(L, LAB, FS)
mf = K.case_move_frames(P, L, FLAT)
ctx = K.pb_inherit_ctx(P, FLAT, labels=LAB, fs_pairs=FS, S1f=S1f, V=V)
gate("C0 ctx: inherited frames {376,3052,3453: [31506]}, case 31308 -> [31506, 31517], nothing missing",
     dict((n, sorted(f)) for n, f in ctx["frames"].items()) == {376: [31506], 3052: [31506], 3453: [31506]}
     and ctx["cases"].get(31308) == [31506, 31517] and not ctx["missing"], {"frames": ctx["frames"], "cases": ctx["cases"], "missing": ctx["missing"],
                                                                          "chain": [c["plan"] for c in ctx["chain"]]})
run = lambda c: K.pb_check_bound(S1f, Gb, Gp, Gb, PRED["cdiff_rows"], P["open_rows"], mf, (), V, inherit=c)   # noqa: E731
r_off, r_on = run(None), run(ctx)
cls = dict((x["sink"].split("|")[2], (x.get("class"), x.get("action"))) for x in r_on["recorded"])
WANT = {"cal cluster path": (1, None), "file size": (1, None), "selected path": (2, "w_in3_376"), "error in": (2, "w_g376"),
        "total data array in": (2, "w_h376")}
same = all(r_on[k] == r_off[k] for k in ("eq_diff", "pairs_missing", "n_rows")) and all(
    r_on["old"][k] == r_off["old"][k] for k in r_off["old"] if k != "cd")
gate("A1 p5s02b sim end: 5 #376 rows RECORDED (2 class 1, 3 class 2 + action), PB ok, pairs_extra_left []; other outputs == inherit off "
     "(off: recorded {0}, blocked {1}, extra_left {2})".format(len(r_off["recorded"]), len(r_off["blocked"]), len(r_off["pairs_extra_left"])),
     cls == WANT and r_on["ok"] and r_on["pairs_extra_left"] == [] and not r_on["blocked"] and same and not r_off["ok"],
     {"classes": cls, "ok": r_on["ok"], "blocked": r_on["blocked"], "left": r_on["pairs_extra_left"], "same": same})
by = dict((y["sink"], y) for y in r_on["old"]["cd"]["rows"])
fm = K.frame_tag_map(Gb)
RB = K.pb_bound_rows(r_on["old"]["cd"], Gb, V)
SK = dict((s.split("|")[2], s) for s in by if s.startswith("376|"))


def row(name, res=None, G1=None, c=None):
    s = SK[name]
    res = res if res is not None else [K.frame_src_resolve(x, fm) for x in by[s]["after"]]
    return K.pb_inherited_row(s, by[s], res, G1 or Gb, S1f, RB.get(s), c or ctx)


def g_uid(src_key, uid):
    G1 = dict(Gb)
    G1["rows"] = dict(Gb["rows"])
    G1["rows"][src_key] = dict(Gb["rows"][src_key], term_uid=uid)
    return G1


res0 = lambda n: [K.frame_src_resolve(x, fm) for x in by[SK[n]]["after"]]   # noqa: E731
b1 = [row(n, G1=g_uid(res0(n)[0][0], 999991)) for n in ("cal cluster path", "selected path")]
gate("B1 changed source uid (cal cluster path class 1, selected path class 2) -> BLOCK", all(x[0] is None for x in b1), b1)
b2 = [row(n, res=[(b, frozenset((tn, 999993) for tn, _f in t)) for b, t in res0(n)]) for n in ("cal cluster path", "selected path")]
gate("B2 a tag on a frame (999993) of a non-adopted case -> BLOCK", all(x[0] is None for x in b2), b2)
sp = res0("selected path")
b3 = row("selected path", res=sp + [(sp[0][0], frozenset([(10000003, 31517)]))])
gate("B3 f1 tag on 'selected path' (outside PD374(d)), multiplicity 2 == frame count -> BLOCK", b3[0] is None, b3)
c4 = dict(ctx)
c4["connects"] = dict((k, v) for k, v in ctx["connects"].items() if v != "w_in3_376")
b4, r4 = row("selected path", c=c4), run(c4)
gate("B4 class-2 row with no connect action -> BLOCK; pb_check_bound not ok, the row blocked", b4[0] is None and not r4["ok"]
     and [x["sink"] for x in r4["blocked"]] == [SK["selected path"]], (b4, [x["sink"] for x in r4["blocked"]]))
ei = res0("error in")
b5 = [row("error in", res=ei + [ei[0]]), row("selected path", res=sp + [sp[0]])]
gate("B5 multiplicity 3 on error in ({0} entries + 1), 2 on selected path ({1} + 1) -> BLOCK".format(len(ei), len(sp)),
     all(x[0] is None for x in b5) and len(sp) == 1, b5)
# ---- R: stored adopted runs reproduce (pb_386 inherit off == on; counts vs the stored run) --------------------------------------------
recs = [json.loads(x) for x in open(os.path.join(K.BENCH, "adopted_scratch.jsonl"), encoding="utf-8") if x.strip()]
for ln, stem in ((9, "p5s01a"), (10, "p5s01b"), (11, "p5s02a")):
    r = recs[ln - 1]
    pp = list(r["plan_md5s"])[0]
    Pq = K.jload(K.ROOT, pp)
    D = K.jload(K.ROOT, r["log"].replace("\\", "/")[:-4] + ".json")
    Bq = K.jload(K.ROOT, Pq["finalized"]["base"]["path"])
    Lq = K.jload(K.ROOT, Pq["finalized"]["step_files"][-1]["path"])["state"]
    Fq = K.run_bind(report=D["stagexec"])
    real, al = K.real_rows_from_record(D["real_end_rows"], Lq["terminals"], Fq)
    PRq = K.jload(K.ROOT, pp.replace(".json", "_pred.json"))
    REN = K.licence_renames(K.jload(K.ROOT, pp.replace(".json", "_licence.json")))
    objs = SX.bind_state(Lq, {"obj": Fq, "term": {}, "diag": {}})[0].get("objs") or []
    FSq = Bq.get("fs_tunnel_pairs", Bq.get("fs_pairs"))
    q = lambda inh: K.pb_386(Bq["terminals"], Lq, real, objs, Fq, Pq, PRq["cdiff_rows"], Pq["open_rows"], LAB, FSq, REN, S1f, V, inherit=inh)   # noqa: E731
    o, n = q(False), q(None)
    pick = lambda x: (x["ok"], x["old"]["rows"], [y["sink"] for y in x["recorded"]], [y["sink"] for y in x["blocked"]], x["pairs_extra_left"])   # noqa: E731
    stored = D.get("ring_" + stem) or {}
    lg = [(i, x.strip()[:4]) for i, x in enumerate(open(os.path.join(K.ROOT, r["log"].replace("\\", "/")), encoding="utf-8", errors="replace"), 1)
          if x.strip().startswith(("PASS  PB ", "FAIL  PB "))][-1:]
    gate("R {0} pb_386 inherit off == on: ok {1}/{2}, rows {3}/{4} (stored cdiff_rows {5}), recorded {6}, blocked {7}; stored PB gate (log line, "
         "verdict) {8}; inherited frames {9}, unmatched real rows {10}".format(stem, o["ok"], n["ok"], len(o["old"]["rows"]), len(n["old"]["rows"]),
                                                                len(stored.get("cdiff_rows") or []), len(n["recorded"]), len(n["blocked"]),
                                                                lg, n.get("inherit_frames"), len(al["unmatched"])),
         pick(o) == pick(n) and len(n["old"]["rows"]) == len(stored.get("cdiff_rows") or []) and lg and lg[0][1] == ("PASS" if n["ok"] else "FAIL"),
         (pick(n)[0], pick(n)[2:]))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
