r"""prep_c143_3_s02 - card 143-3 step 1 (OFFLINE, no LabVIEW; PD333(a)): the EXPECTED Error List file of P4 session 2's adopted file
claudeDev\D1_ring_p4s02_20261003_110001.vi (84cac487), from its full measured read
errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json (53 items), in the form of errorlist_expected_D1_ring_p3b2b_20261002_130007.json:
the 10 P3b-2b entries (all 51 licences used by the read, licence_usage) + 2 entries for the by-design session-boundary items (unwired
StopAll READ Local #6902, While #10170 cond #23246 - diag_c143_2_facts.md). Also records the fixed predictor's s02 result in
plan_ring_p4_s02v18_pred.json's errorlist block (selftest_elpred.json), every other key unchanged.
PREDICTION CONTRACT: R read has 53 items == n_reported; X compare(read items, new expected) -> extra [] missing []; T total 53 ==
  sum(counts); P pred errorlist predicted_total 53 == measured, other pred keys unchanged.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c143_3_s02.log -- py -u tools/bench/prep_c143_3_s02.py"""
import copy, hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                          # noqa: E731
READ = os.path.join(B, "errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json")
OLD = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
NEW = os.path.join(B, "errorlist_expected_D1_ring_p4s02_20261003_110001.json")
PP = os.path.join(B, "plan_ring_p4_s02v18_pred.json")
SELF = os.path.join(B, "selftest_elpred.json")
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p4s02_20261003_110001.vi"
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


rd, old = J(READ), J(OLD)
items = rd["items"]
gate("R read has 53 items == n_reported", len(items) == 53 == rd.get("n_reported"), (len(items), rd.get("n_reported"), md5(READ)))
exp = copy.deepcopy(old["expected"]) + [
    {"norm_all": ["localvariable", "variableisnotconnectedtoanything"], "count": 1,
     "label": "Local Variable: This variable is not connected to anything. (StopAll READ Local #6902, output unwired by design)",
     "cite": "PD333(a); diag_c143_2_facts.md (b): Local #6902 term #23310 'StopAll' is_source, wire 0; wired by s03 action 1 p4_w_stop12"},
    {"norm_all": ["whileloop", "conditionalterminalisnotwired"], "count": 1,
     "label": "While Loop: Conditional terminal is not wired (While #10170 body #23166 cond #23246, scaffold wire w23310 cut by plan)",
     "cite": "PD333(a); diag_c143_2_facts.md (a): plan_ring_p4_s02v18.json p4_dw_23310; wired by s03 action 1 p4_w_stop12"}]
total = sum(int(e["count"]) for e in exp)
ex, mi, usage = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi, "used": [u["used"] for u in usage]})
gate("T total 53 == sum(counts)", total == 53, total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": "84cac48781c7c915c8f0d7e8fb079341",
       "decided_by": "card 143-3 (PD333(a)): P3b-2b's 51 entries unchanged (the s02 full read used every licence: licence_usage) + the 2 by-design "
                     "session-boundary items measured by uid in card 143-2 (review archive/peer/2026-10-03-c143-2-el53.md, verdict supported)",
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(OLD), "total": total, "expected": exp,
       "format_note": old.get("format_note"), "closes_in_s03": "both new entries are wired by plan_ring_p4_s03v18.json action 1 p4_w_stop12"}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
p = J(PP)
before = dict((k, json.dumps(v, sort_keys=True)) for k, v in p.items() if k != "errorlist")
st = J(SELF)["s02"]
el = dict(p["errorlist"])
el.update({"predicted_total": st["predicted_total"], "new_items_predicted": len(st["new_items"]) - len(st["closed_items"]),
           "alternative_total": None, "fixed": st, "measured_total": 53, "measured_from": rel(READ), "expected_file": rel(NEW),
           "rule": st["rule"] + "; base = session 1 launch full Error List 51 (PD326(a)); card 143-3 re-derive (selftest_elpred.log)",
           "superseded_rule": "PD322(e) predicted 51 / alternative 52 (cards 142-5, 143-1)", "checked": True})
p["errorlist"] = el
json.dump(p, open(PP, "w", encoding="utf-8"), indent=1)
q = J(PP)
gate("P pred errorlist predicted_total 53 == measured, other keys unchanged",
     q["errorlist"]["predicted_total"] == 53 and before == dict((k, json.dumps(v, sort_keys=True)) for k, v in q.items() if k != "errorlist"),
     {"plan_md5": q["plan"]["md5"], "pred_md5": md5(PP)})
ARTS.append({"path": rel(PP), "md5": md5(PP)})
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
