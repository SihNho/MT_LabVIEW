"""sim_k_x4probe_79 - card 79-4 read-only diagnostic: stage_prerun's own X4 check (addr_offline) over EVERY exec end of
plan_k_rows.json (the prerun printed only 8), once as written and once with each term_uid end carrying the graph's own
terminal name. Pure Python, no LabVIEW. PREDICTION: as written the 7 FSIT-sourced ends fail; with names 0 fail."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import stage_prerun as SP, protocol  # noqa: E401,E402
GP = os.path.join(HERE, "graph_k_s4_20260925.json")
OG = SP.OfflineGraph(GP); T = json.load(open(GP, encoding="utf-8"))["terminals"]
RW = json.load(open(os.path.join(HERE, "plan_k_rows.json"), encoding="utf-8"))
nb = [0, 0]
for k, named in enumerate((False, True)):
    for r in RW["decisions"]:
        for side, is_src in (("src", True), ("dst", False)):
            e = (r.get("exec") or {}).get(side)
            if not isinstance(e, dict):
                continue
            if named and "term" not in e and e.get("term_uid") is not None:
                e = dict(e, term=next(x["term_name"] for x in T if x["owner_uid"] == e["uid"] and x["term_uid"] == e["term_uid"]))
            why = SP.addr_offline(OG, e, is_src)
            if why:
                nb[k] += 1
                print("named" if named else "as-is", r["id"], side, e, "->", why)
print("X4 failures as-is", nb[0], "named", nb[1])
for u in (6239, 3862, 5659, 3173):
    print("RAW rows of #", u, [(x["term_uid"], x["term_name"], x["is_source"], x["wire_uid"], x.get("term_class"), x.get("frame_diagram")) for x in T if x["owner_uid"] == u])
print(protocol.result_line(protocol.make_result(1 if nb[1] == 0 else 0, 0 if nb[1] == 0 else 1, None if nb[1] == 0 else "named ends still fail", [])))
