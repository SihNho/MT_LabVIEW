r"""plan_l2r2_make - card 116-2 P1/P2 (offline, no LabVIEW): the L2-R2 plan from the SAVED R1 graph (graph_l2r1_saved_20260928.json, dumped by
diag_c116b_props.py from a byte copy of D1_l2_r1_20260928_055441.vi). Cut of the plan_l2r1 shape (PD230(f): stub wires first, then the object):
per retired LoopTunnel T of PD228(f)/(g) (13; #32572 stays): delete_wire of every wire whose EVERY terminal is on T, then delete_object T.
Re-checks P1 on the saved graph: M1 every T has rows and no SOURCE face of T sits on a wire with a sink owned by another node (live-consumer
rule, stagexec.retire_check); M2 #32572 keeps its wired consumer (SelectorTunnel #24364, facts_c114e_inventory.json); M3 no stub wire carries
both a source and a sink. PREDICTIONS written to plan_l2r2_pred.json (P2), each with its derivation:
  cdiff == R1's 16 rows (stage_d1_l2r1.json l2r1.cdiff_rows); census removal set = 13 tunnels + the stubs; terminal-list diff: the stubs vanish,
  each shared net loses exactly T's terminals, every other wire's terminal list is unchanged; Error List (R1 pinned loose 24 / no-source 1 /
  not-connected 20 / other 10 = 55, errorlist_expected_D1_l2_r1_20260928_055441.json): loose' = 24 - source-only stubs + shared nets on which T
  was a SINK and which were not already loose in R1 (one item per WIRE OBJECT, rev 3; R1 measured 11 stubs -> -6 loose/-5 no-source, 7 nets losing
  one sink -> +7 loose); no-source' = 1 - sink-only stubs; other classes unchanged. The per-segment (+2) and swap (+1) alternatives are recorded.
  Output: tools/bench/plan_l2r2_in.json + tools/bench/plan_l2r2_pred.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
J = lambda fn: json.load(open(os.path.join(B, fn), encoding="utf-8"))  # noqa: E731
GF = "graph_l2r1_saved_20260928.json"
G, INV, ST = J(GF), J("facts_c114e_inventory.json"), J("stage_d1_l2r1.json")["l2r1"]
P1 = J("plan_l2r1_in.json")
RET = [2294, 3644, 2580, 2396, 4432, 3656, 3920, 4031, 5129, 5328, 28343, 5752, 5569]
KEEP = 32572
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:1200]), flush=True)


byw = {}
for r in G["terminals"]:
    if r["wire_uid"]:
        byw.setdefault(int(r["wire_uid"]), []).append(r)
own = lambda u: [r for r in G["terminals"] if int(r["owner_uid"]) == u]  # noqa: E731
# rev 3 (review archive/peer/2026-09-28-c116b-plan.md:52-57): M0 recomputes the set ON THE SAVED R1 GRAPH instead of comparing with the B3-era file:
# every LoopTunnel whose InnerTerminal rows sit on #637's body (diagram 639) and none of whose SOURCE faces shares a wire with another node's sink.
lt = set(int(o["uid"]) for o in G["objs"] if o["class"] == "LoopTunnel")
on637 = set(int(r["owner_uid"]) for r in G["terminals"] if int(r["owner_uid"]) in lt and r["term_class"] == "InnerTerminal" and int(r["frame_diagram"] or 0) == 639)
free = set(u for u in on637 if not any(r["is_source"] and r["wire_uid"] and any(not x["is_source"] and int(x["owner_uid"]) != u for x in byw[int(r["wire_uid"])])
                                       for r in G["terminals"] if int(r["owner_uid"]) == u))
gate("M0 on the saved R1 graph: consumer-less LoopTunnels with an inner face on diagram 639 == the 13 retire uids ({0} tunnels on 639)".format(len(on637)),
     free == set(RET), {"extra": sorted(free - set(RET)), "missing": sorted(set(RET) - free)})
actions, per, cons, stubs_all, shared_sink, shared_src, mixed = [], {}, [], [], [], [], []
for t in RET:
    rows = own(t)
    for r in rows:
        if r["is_source"] and r["wire_uid"]:
            cons += [(t, int(r["term_uid"]), int(x["owner_uid"]), int(x["term_uid"])) for x in byw[int(r["wire_uid"])] if not x["is_source"] and int(x["owner_uid"]) != t]
    ws = sorted(set(int(r["wire_uid"]) for r in rows if r["wire_uid"]))
    st = [w for w in ws if all(int(x["owner_uid"]) == t for x in byw[w])]
    sh = [w for w in ws if w not in st]
    for w in st:
        k = set(bool(x["is_source"]) for x in byw[w])
        (mixed if k == {True, False} else stubs_all).append((t, w, "src" if k == {True} else ("sink" if k == {False} else "mixed")))
    for w in sh:
        mine = [bool(x["is_source"]) for x in byw[w] if int(x["owner_uid"]) == t]
        (shared_sink if not any(mine) else shared_src).append((t, w))
    per[t] = {"rows": [(int(r["term_uid"]), r["term_class"], bool(r["is_source"]), int(r["wire_uid"] or 0), r["frame_diagram"]) for r in rows], "stubs": st, "shared": sh}
    print("  T #{0}: {1}".format(t, json.dumps(per[t])), flush=True)
    for w in st:
        actions.append({"op": "delete_wire", "id": "r2_w{0}".format(w), "wire_uid": w, "why": "stub: every terminal on #{0} ({1})".format(t, [x["term_class"] for x in byw[w]])})
    actions.append({"op": "delete_object", "id": "r2_t{0}".format(t), "uid": t, "why": "PD228(f)/(g) consumer-less LoopTunnel on #637 (facts_c114e_inventory.json); shared nets {0} lose only its terminal".format(sh)})
gate("M1 every retired tunnel has rows; no source face of one feeds a sink owned by another node", all(per[t]["rows"] for t in RET) and not cons, cons[:20])
k32 = own(KEEP)
k32c = [(int(x["owner_uid"]), x["owner_class"]) for r in k32 if r["wire_uid"] for x in byw[int(r["wire_uid"])] if int(x["owner_uid"]) != KEEP]
gate("M2 #32572 is kept and still shares a wire with SelectorTunnel #24364", k32 and any(u == 24364 for u, _c in k32c) and KEEP not in RET, k32c)
gate("M3 no stub wire carries both a source and a sink; no shared net where a retired tunnel is the SOURCE", not mixed and not shared_src, {"mixed": mixed, "shared_src": shared_src})
el = {"loose": 24, "nosource": 1, "notconn": 20, "other": 10}
nsrc, nsink = sum(1 for x in stubs_all if x[2] == "src"), sum(1 for x in stubs_all if x[2] == "sink")
# rev 3 (review c116b-plan.md:61-82): the Error List item is per WIRE OBJECT (one 'has loose ends' item per wire, however many dangling segments).
# R1's accepted accounting (PD230(d)) puts one dangling branch on each of its 7 shared nets, so a net of that set that loses a second sink adds nothing.
R1LOOSE = {8590, 9051, 11253, 11389, 25438, 25461, 29122}
already = [w for _t, w in shared_sink if w in R1LOOSE]
pred_el = dict(el, loose=el["loose"] - nsrc + len(shared_sink) - len(already), nosource=el["nosource"] - nsink)
pred_el["total"] = sum(pred_el[k] for k in ("loose", "nosource", "notconn", "other"))
gate("M4 prediction is non-negative", pred_el["nosource"] >= 0 and pred_el["loose"] >= 0, pred_el)
stubs = [w for _t, w, _k in stubs_all]
term_lost = sorted(int(r["term_uid"]) for t in RET for r in own(t))
shared_after = dict((w, sorted(int(x["term_uid"]) for x in byw[w] if int(x["owner_uid"]) not in RET)) for _t, w in shared_sink)
import hashlib  # noqa: E402
GMD5 = hashlib.md5(open(os.path.join(B, GF), "rb").read()).hexdigest()
pin = {"schema": "l2r2-pred/1", "graph": {"path": "tools/bench/" + GF, "md5": GMD5},
       "retire": RET, "keep": KEEP, "stubs": stubs, "stubs_srconly": nsrc, "stubs_sinkonly": nsink, "shared_sink_nets": [w for _t, w in shared_sink],
       "shared_after": shared_after, "terminal_rows_lost": term_lost,
       "census": {"LoopTunnel": -13, "Wire": -len(stubs)}, "cdiff_rows": sorted(ST["cdiff_rows"]),
       "errorlist": {"r1": el, "pred": pred_el, "model": "per wire object", "already_loose_in_r1": already,
                     "alternatives": {"per_segment": el["loose"] - nsrc + len(shared_sink), "swap_one_r1_net_not_loose": el["loose"] - nsrc + len(shared_sink) - len(already) + 1},
                     "derivation": "loose {0} - {1} source-only stubs + {2} shared nets losing a tunnel sink - {3} of them already loose in R1 ({4}) = {5}; no-source {6} - {7} sink-only stubs = {8}; not-connected {9}, other {10} unchanged; total {11}".format(
           el["loose"], nsrc, len(shared_sink), len(already), already, pred_el["loose"], el["nosource"], nsink, pred_el["nosource"], el["notconn"], el["other"], pred_el["total"])}}
plan = {"schema": "stageplan/1", "stage": "l2r2", "goal": "L2-R2 (PD228(f)/(g), PD230(f), card 116-2): on the SAVED R1 bed D1_l2_r1_20260928_055441.vi retire the 13 consumer-less LoopTunnels on #637 (#32572 stays); deletes only, stub wires first",
        "base": {"path": "tools/bench/" + GF, "md5": GMD5}, "context": P1["context"], "actions": actions, "open_rows": P1["open_rows"]}
if all(c for _n, c in ok):
    json.dump(plan, open(os.path.join(B, "plan_l2r2_in.json"), "w", encoding="utf-8"), indent=1)
    json.dump(pin, open(os.path.join(B, "plan_l2r2_pred.json"), "w", encoding="utf-8"), indent=1)
    print("  FACT WROTE plan_l2r2_in.json ({0} actions: {1} delete_wire + 13 delete_object) and plan_l2r2_pred.json".format(len(actions), len(stubs)), flush=True)
    print("  FACT PRED " + pin["errorlist"]["derivation"], flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
