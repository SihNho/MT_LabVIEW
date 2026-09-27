r"""diag_c110_xcheck - card 110-1 P1 OFFLINE (PD158): group-B rows of d1_rewire_sources.json (derived from build_d1_v0.json's cut)
vs the rows this card derived from the L2-A3 bed (plan_l2b1_in.json wire rows + open_rows + the B2/B3 rows of split_plan_110.md s3).
Prints each rewire_sources row with its action/source and whether the bed-derived set names the same sink (uid, terminal name).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c110_xcheck.log -- py -u tools/bench/diag_c110_xcheck.py"""
import json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                                # noqa: E402
RS = json.load(open(os.path.join(HERE, "d1_rewire_sources.json"), encoding="utf-8"))
BV = json.load(open(os.path.join(HERE, "build_d1_v0.json"), encoding="utf-8"))
PL = json.load(open(os.path.join(HERE, "plan_l2b1_in.json"), encoding="utf-8"))
GR = json.load(open(os.path.join(HERE, "graph_l2a3_bed_20260927.json"), encoding="utf-8"))
B = {1359, 2222, 2626, 6104, 8885, 9833, 11261, 29874, 403, 9306, 28170, 29091}
NM = dict((int(r["term_uid"]), (int(r["owner_uid"]), r["term_name"])) for r in GR["terminals"])
# bed-derived sinks: B1 wire rows, B2/B3 rows (split page s3, typed from diag_c110_terms_bed.log), open rows (QRT/judgement)
mine = set(NM.get(a["dst"]["term_uid"], (a["dst"]["uid"], "?")) for a in PL["actions"] if a["op"] == "wire")
mine |= set(NM[t] for t in (2811, 9092, 29928, 28378, 2996, 3193, 6400, 8894, 9845, 10182, 29782, 9508, 2832, 4160, 4165, 11273))
mine |= set((int(r["node"]), r["term"]) for r in PL["open_rows"])
rows = [r for r in RS["rows"] if int(r["uid"]) in B]
moved_bv = [m for m in BV.get("moved", []) if int(m[1]) in B]
print("BUILD_D1_V0 moved rows for B: {0}".format(moved_bv), flush=True)
miss, agree = [], 0
for r in rows:
    src = r.get("source") or {}
    key = (int(r["uid"]), r.get("name") or "")
    hit = key in mine or any(k[0] == key[0] and k[1] == key[1] for k in mine)
    agree += bool(hit)
    hit or miss.append(key)
    print("RS #{0} i{1} {2!r} src={3} action={4} src={5} -> {6}".format(r["uid"], r["i"], r.get("name"), r.get("is_source"), r.get("action"),
          (src.get("kind"), src.get("uid"), src.get("name") or src.get("out_name")), "COVERED" if hit else "NOT IN BED-DERIVED SET"), flush=True)
print("TOTAL rewire_sources B rows {0}: covered {1}, not covered {2}: {3}".format(len(rows), agree, len(miss), miss), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
