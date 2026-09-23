r"""m3a4_reverify - connectivity-map-plan STEP 6.0: re-verify the M3a-4 draft record on the COMPLETED graph. OFFLINE.

Pre-decided 142 PRECONDITION: the step-5 record (`tools/bench/decision_m3a4.json`) is a DRAFT until the live-consumer
check is re-run on the graph WITH the step-4b flat-sequence pairs. This file does exactly that, no LabVIEW, no model.

PRIOR ART USED, NOT RE-TYPED: jev_candidates.load (bed + S1 graphs, wiki fs_tunnel_pairs, bed loops), jev_candidates.
map_key (renamed terminals, PD137), vigraph.reach4/effective_sources/computation_diff. Nothing new was built.

VERDICTS (mechanical):
  row   keep            the S1 edge (mapped) is an edge of the bed
        delete-halfwire the severed wire is a half-wire in the bed AND the S1 sink is live-fed in the bed with
                        effective sources == S1's (non-empty)
        retire          the S1 sink is itself a carrier (w7337 -> #4334): its half-wire is deleted, the carrier retired
        llm             anything else (reported, never executed)
  carrier retire        reach4 from it reaches no node outside the carrier set (no live CONSUMER)
          llm           a live consumer exists - do NOT touch, report
PREDICTION CONTRACT (desk-checked; the numbers the stage gates on are written into the record's `predict`):
  11 rows = 5 keep (+2 S3b rows keep) , 3 delete-halfwire, 1 retire; 8 carriers retire, 0 llm; Node 635 -> 632 (only
  the 3 Invokes are in the Node traverse); computation_diff(S1,bed)
  rows 0 already (so 6.3's rows-empty gate is re-cut as "stays 0" and its nodes_added as "= bed's minus the 3 Invokes").

    MATERIAL=1 py tools/bgrun.py --max-min 3 --log tools/bench/m3a4_reverify.log -- py -u tools/bench/m3a4_reverify.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import jev_candidates as JC                                                        # noqa: E402
import vigraph as V                                                                # noqa: E402

DRAFT = os.path.join(HERE, "decision_m3a4.json")
OUT = os.path.join(HERE, "decision_m3a4_v2.json")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
CARRIERS = {4334: "RightShiftRegister", 4344: "LeftShiftRegister", 4256: "RightShiftRegister",
            4274: "LeftShiftRegister", 9641: "LoopTunnel", 4859: "Invoke", 24012: "Invoke", 24005: "Invoke"}
P142 = {1731: "delete-halfwire", 3947: "delete-halfwire", 9635: "delete-halfwire", 7337: "retire"}


def show(keys):
    return sorted(V.show(k) for k in keys)


def main():
    t0 = time.time()
    d0 = json.load(open(DRAFT, encoding="utf-8"))
    B, S = JC.load(JC.BED_KEY), JC.load(JC.S1_KEY)
    ok = [("wiki bed md5 == bed pin", B["wiki"]["md5"] == BED_MD5 == d0["bed_md5"]),
          ("bed graph uses the 4b machine faces", "machine faces" in B["method"]["fs_tunnel"]["rule"])]
    edges = set((k, a, b) for k, a, b, _i in B["edges"])
    half = dict((f["wire_uid"], f) for f in B["flags"] if f["n_src"] == 0 or f["n_sink"] == 0)
    wired = set(r["wire_uid"] for r in B["rows"].values() if r["wire_uid"])
    rows, decisions = [], []
    for it in d0["intent"]:
        w = it["id"]
        e = [(a, b) for k, a, b, i in S["edges"] if k == "wire" and i == w]
        sk, dk = e[0] if e else (it["true_src"], it["true_dst"])
        G1 = S if e else B
        msk, _h1 = JC.map_key(B, sk, G1)
        mdk, _h2 = JC.map_key(B, dk, G1)
        live = [(k, V.show(a)) for k, a, _i in B["in"].get(mdk, ()) if k != "thru"] if mdk else []
        e1 = set(V.show(x) for x in V.effective_sources(G1, dk))
        e2 = set(V.show(x) for x in V.effective_sources(B, mdk)) if mdk else set()
        sink_node = V.key_parts(mdk)[0] if mdk else None
        r = {"id": w, "s1_edge": [V.show(sk), V.show(dk)] if e else None, "bed_src": msk and V.show(msk),
             "bed_sink": mdk and V.show(mdk), "edge_in_bed": ("wire", msk, mdk) in edges,
             "bed_wire_state": "half-wire" if w in half else ("termless" if w not in wired else "whole"),
             "sink_live_sources": live, "eff_equal_nonempty": bool(e1) and e1 == e2, "eff_s1": sorted(e1),
             "draft_action": next(x["action"] for x in d0["decisions"] if x["intent_id"] == w)}
        if sink_node in CARRIERS:
            r["verdict"] = "retire"
            r["why"] = "the S1 sink is carrier #{0}; its half-wire is deleted, the carrier retired".format(sink_node)
        elif r["edge_in_bed"]:
            r["verdict"] = "keep"
        elif w in half and live and r["eff_equal_nonempty"]:
            r["verdict"] = "delete-halfwire"
        else:
            r["verdict"] = "llm"
        r["plan142"] = P142.get(w, "keep")
        r["verdict_changed_vs_142"] = r["verdict"] != r["plan142"]
        if w in half:
            decisions.append({"id": w, "action": "delete", "exec": {"wire_uid": w}, "row_verdict": r["verdict"]})
        rows.append(r)
    carriers = []
    for u, cls in CARRIERS.items():
        terms = V.terminals(B, node=u)
        cons = sorted(set(V.key_parts(k)[0] for k in V.reach4(B, [u])) - set(CARRIERS))
        prod = []
        for k in terms:
            for kind, a, _i in B["in"].get(k, ()):
                if kind != "thru" and V.key_parts(a)[0] not in CARRIERS:
                    wu = B["rows"][k]["wire_uid"]
                    others = [V.show(x) for x in V.wire_terminals(B, wu) if x != k and x != a]
                    prod.append({"from": V.show(a), "into": V.show(k), "wire": wu, "wire_other_sinks": others})
        c = {"uid": u, "class": B["cls"].get(u), "class_expected": cls, "n_terms": len(terms),
             "wires": sorted(set(B["rows"][k]["wire_uid"] for k in terms if B["rows"][k]["wire_uid"])),
             "live_consumers": cons, "live_producers": prod, "verdict": "retire" if not cons else "llm"}
        carriers.append(c)
        if c["verdict"] == "retire":
            decisions.append({"id": u, "action": "retire", "exec": {"class": cls, "uid": u}})
    cd = V.computation_diff(S, B)
    rem = [(k, V.show(a), V.show(b)) for k, a, b in sorted(edges)
           if k != "thru" and (V.key_parts(a)[0] in CARRIERS or V.key_parts(b)[0] in CARRIERS)
           and not (V.key_parts(a)[0] in CARRIERS and V.key_parts(b)[0] in CARRIERS and k == "wire")]
    retired = [c["uid"] for c in carriers if c["verdict"] == "retire"]
    rec = {"stage": "m3a4", "version": 2, "bed_md5": BED_MD5, "draft": os.path.basename(DRAFT),
           "created": time.strftime("%Y-%m-%d %H:%M:%S"), "graph": {"bed_fs": B["method"]["fs_tunnel"]["rule"],
                                                                      "bed_nodes": len(B["cls"]), "bed_edges": len(edges)},
           "rows": rows, "carriers": carriers, "decisions": decisions,
           "changed_vs_142": [r["id"] for r in rows if r["verdict_changed_vs_142"]] +
                             [c["uid"] for c in carriers if c["verdict"] != "retire"],
           # prior-art m3a4-step6 B4 (already measured, c89 :141 / plan 4b): tunnels and shift registers are NOT in the
           # `Node` traverse (518 FSIT + 138 LoopTunnel > 635) - only the Invokes leave it (c89: 635 -> 632); every
           # carrier class is counted in its OWN traverse.
           "predict": {"node_before": 635, "node_after": 635 - sum(1 for u in retired if CARRIERS[u] == "Invoke"),
                       "class_removed": dict((k, sorted(u for u in retired if CARRIERS[u] == k))
                                             for k in sorted(set(CARRIERS.values()))), "wire_before": 1920,
                       "wire_after_deletes": 1920 - sum(1 for x in decisions if x["action"] == "delete"),
                       "rbw_removes": sorted(r["id"] for r in rows if r["bed_wire_state"] == "termless"),
                       "exec_state": 1, "diff_bed_new_nodes_removed": sorted(retired),
                       "diff_bed_new_edges_removed": [list(x) for x in rem], "diff_bed_new_edges_added": [],
                       "cdiff_s1_bed": {"rows": len(cd["rows"]), "added": [x["node"] for x in cd["computation_nodes_added"]],
                                        "removed": [x["node"] for x in cd["computation_nodes_removed"]]},
                       "cdiff_s1_new": {"rows": 0, "added": sorted(x["node"] for x in cd["computation_nodes_added"]
                                                                  if x["node"] not in CARRIERS), "removed": []}},
           "checks": ok, "seconds": round(time.time() - t0, 1)}
    json.dump(rec, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
    for c_label, c_ok in ok:
        print("  {0}  {1}".format("PASS" if c_ok else "FAIL", c_label))
    for r in rows:
        print("  ROW   w{id} verdict={verdict} (draft {draft_action}, 142 {plan142}) wire={bed_wire_state} "
              "edge_in_bed={edge_in_bed} eff_eq={eff_equal_nonempty} live={sink_live_sources}".format(**r))
    for c in carriers:
        print("  CARR  #{uid} {class} verdict={verdict} consumers={live_consumers} producers={live_producers}".format(**c))
    print("  FACT  changed vs 142: {0}".format(rec["changed_vs_142"]))
    print("  FACT  predict: {0}".format(json.dumps(rec["predict"])))
    print("  FACT  wrote {0} in {1} s".format(OUT, rec["seconds"]))
    return 0 if all(x for _l, x in ok) and not rec["changed_vs_142"] else 1


if __name__ == "__main__":
    sys.exit(main())
