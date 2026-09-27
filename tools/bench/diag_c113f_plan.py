r"""diag_c113f_plan - card 113-4 P2 (OFFLINE, no LabVIEW): re-finalize L2-B2b WITHOUT row b2_03 (judgement PD227(d): b2_03 moves to the
stage that wires t11273 / the #11608 open row). Only change to plan_l2b2b_in.json: action b2_03 removed, open row (#11261, 'array') declared
(its pair stays open). Every other row, the base graph and the D4 scope (20 nodes) are unchanged; plan_l2b2b_d4.json gets the new plan md5.
History copies (byte-identical): plan_l2b2b_in_9row.json (d13c0de4), plan_l2b2b_9row.json (58046f2f).
PRIOR ART: diag_c113c_plan.py (card 113-2 P2), whose sim() this repeats with why_new=None. No new tool.
PREDICTION: FINAL, open_rows_match (16 declared), route check PASS 8/8: b2_01 nested, b2_02 cfw, b2_04 ctltun, b2_05 ctltun, b2_06 cfw,
  b2_07 ctlsink, b2_08 cfw, b2_16 ctltun; (11261,'array') in the simulated end pairs AND declared (open, not new).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c113f_plan.log -- py -u tools/bench/diag_c113f_plan.py"""
import hashlib, json, os, shutil, sys                                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagesim as SS, protocol                                                       # noqa: E401,E402
GR = os.path.join(HERE, "graph_l2b2a_20260928.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                         # noqa: E731
gates, arts = [], []


def gate(lab, ok, det=""):
    gates.append((lab, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:900]), flush=True)


kp = lambda keys: sorted(set((SS.V.key_parts(k)[0], SS.V.key_parts(k)[2]) for k in keys or []))   # noqa: E731
PIN = os.path.join(HERE, "plan_l2b2b_in.json")
FIN = os.path.join(HERE, "plan_l2b2b.json")
D4P = os.path.join(HERE, "plan_l2b2b_d4.json")
OLD_IN, OLD_FIN = "d13c0de4f260373ecde033d1e8a04a13", "58046f2f2d445a332b4a5b13bf405646"
gate("P2 input plan_l2b2b_in.json md5 == 113-2 pin d13c0de4 (9 rows)", md5(PIN) == OLD_IN, md5(PIN))
gate("P2 old finalized plan_l2b2b.json md5 == 58046f2f (recorded)", md5(FIN) == OLD_FIN, md5(FIN))
if not all(ok for _g, ok in gates):
    print(protocol.result_line(protocol.make_result(0, len(gates), gates[0][0], arts))); sys.exit(1)   # noqa: E702
for src, dst in ((PIN, "plan_l2b2b_in_9row.json"), (FIN, "plan_l2b2b_9row.json")):
    shutil.copyfile(src, os.path.join(HERE, dst)); arts.append({"path": "tools/bench/" + dst, "md5": md5(os.path.join(HERE, dst))})   # noqa: E702
pin = json.load(open(PIN, encoding="utf-8"))
n0 = len(pin["actions"])
pin["actions"] = [a for a in pin["actions"] if a["id"] != "b2_03"]
pin["open_rows"].append({"node": 11261, "term": "array", "why": "PD227(d), card 113-4: row b2_03 (#11363 t11369 -> #11261 t11270, S1 wire 11352) "
                         "moved to the stage that wires t11273 (#11608 open row); its pair stays open here"})
pin["open_rows"].sort(key=lambda r: (int(r["node"]), r["term"]))
pin["goal"] = pin.get("goal", "") + " | card 113-4: b2_03 removed (PD227(d)), 8 rows"
gate("P2 row set: 9 -> 8 actions, b2_03 gone, 16 open rows declared", n0 == 9 and len(pin["actions"]) == 8 and len(pin["open_rows"]) == 16,
     (n0, [a["id"] for a in pin["actions"]], len(pin["open_rows"])))
json.dump(pin, open(PIN, "w", encoding="utf-8"), indent=1)
S = SS.simulate(PIN, GR, out_root=os.path.join(HERE, "sim", "l2b2"), plan_out_dir=HERE, route_check=True)
end = kp(S.get("end_cdiff_rows"))
decl = sorted(set((int(r["node"]), r["term"]) for r in pin["open_rows"]))
print("SIM FINAL", S["final"], "open_rows_match", S["open_rows_match"], "failed", S["failed"], "end pairs", len(end), "declared", len(decl), flush=True)
print("END-ONLY", sorted(set(end) - set(decl)), "DECLARED-ONLY", sorted(set(decl) - set(end)), flush=True)
rc = S.get("route_check") or {}
for r in rc.get("rows") or []:
    print("ROUTE-ROW", r.get("k"), r.get("ids"), r.get("route"), "|", r.get("how"), "|", r.get("unroutable"), flush=True)
want = {"b2_01": "nested", "b2_02": "cfw", "b2_04": "ctltun", "b2_05": "ctltun", "b2_06": "cfw", "b2_07": "ctlsink", "b2_08": "cfw", "b2_16": "ctltun"}
got = dict((r["ids"][0], r.get("route")) for r in rc.get("rows") or [] if r.get("ids"))
gate("P2 FINAL and open_rows_match", bool(S["final"] and S["open_rows_match"]), (S["final"], S["open_rows_match"], S["failed"]))
gate("P2 route check PASS, 8/8 routed, none UNROUTABLE", rc.get("status") == "PASS" and len(got) == 8 and
     not any(r.get("unroutable") for r in rc.get("rows") or []), (rc.get("status"), str(rc.get("first_fail"))[:600]))
gate("P2 routes == prediction", got == want, got)
gate("P2 (11261,'array') is in the simulated end AND declared: open, not new", (11261, "array") in end and (11261, "array") in decl,
     [p for p in end if p[0] == 11261])
print("OPEN-ROWS-CLASSED", json.dumps((S.get("finalized") or {}).get("open_rows_classed") or S.get("open_rows_classed"), default=str)[:1500], flush=True)
if S.get("plan_out") and S["final"]:
    arts.append({"path": "tools/bench/plan_l2b2b_in.json", "md5": md5(PIN)})
    arts.append({"path": S["plan_out"]["path"], "md5": S["plan_out"]["md5"]})
    d4 = json.load(open(D4P, encoding="utf-8"))
    d4["plan_md5"], d4["card"] = S["plan_out"]["md5"], d4["card"] + "; plan_md5 re-pinned by card 113-4 (diag_c113f_plan.py, b2_03 removed), scope unchanged"
    json.dump(d4, open(D4P, "w", encoding="utf-8"), indent=1)
    arts.append({"path": "tools/bench/plan_l2b2b_d4.json", "md5": md5(D4P)})
    gate("P2 D4 scope = 20 nodes (unchanged), plan_md5 == new plan", len(d4["scope_nodes"]) == 20 and d4["plan_md5"] == md5(FIN), (len(d4["scope_nodes"]), d4["plan_md5"]))
np_ = sum(1 for _g, ok in gates if ok)
print(protocol.result_line(protocol.make_result(np_, len(gates) - np_, next((g_ for g_, ok in gates if not ok), None), arts)))
