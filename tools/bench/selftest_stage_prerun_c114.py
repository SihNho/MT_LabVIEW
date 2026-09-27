"""card 114-1 S0/S0b self-test of stage_prerun X11 (buildarray_open_sibling, PD227(j)).
Prediction contract: synthetic T1..T8 as labelled; replay R1 plan_l2b1*.json flags #2626 only (licensed by
plan_l2b1_licence.json), R2 plan_l2b2b_9row.json flags #11261 only (unlicensed), R3 delivered plan_l2b2b.json (8 rows)
flags nothing, R4 every other stageplan/1 under tools/bench flags nothing (0 regressions). Ends with a RESULT line."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stage_prerun as SP  # noqa: E402
import protocol as P  # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


def T(name, is_src, tu, owner=1):
    return {"term_uid": tu, "term_name": name, "is_source": is_src, "wire_uid": 0, "owner_uid": owner}


BA = ({1: "BuildArray", 2: "Add", 9: "ForLoop"},
      {1: [T("appended array", True, 10), T("array", False, 11), T("element", False, 12)],
       2: [T("x+y", True, 20, 2), T("x", False, 21, 2), T("y", False, 22, 2)]})


def plan(dst, opens, src=(9, 90)):
    return {"actions": [{"op": "wire", "id": "r1", "src": {"uid": src[0], "term_uid": src[1]}, "dst": dst}],
            "open_rows": [{"node": n, "term": t, "why": "test"} for n, t in opens]}


f = SP.buildarray_open_sibling(plan({"uid": 1, "term_uid": 11}, [(1, "element")]), base=BA)
gate("T1 BA input 'array' wired, sibling 'element' open -> FLAG unlicensed", len(f) == 1 and f[0]["node"] == 1 and
     f[0]["open"] == ["element"] and f[0]["licensed"] is None, f)
f = SP.buildarray_open_sibling(plan({"uid": 1, "term_uid": 11}, []), base=BA)
gate("T2 same row, no open row -> clean", f == [], f)
f = SP.buildarray_open_sibling(plan({"uid": 1, "term_uid": 11}, [(1, "element")]), base=BA, licences={1: "lic.json"})
gate("T3 same with a licence covering #1 -> FLAG licensed", len(f) == 1 and f[0]["licensed"] == "lic.json", f)
f = SP.buildarray_open_sibling(plan({"uid": 2, "term_uid": 21}, [(2, "y")]), base=BA)
gate("T4 non-BuildArray node (Add) with open sibling -> clean", f == [], f)
f = SP.buildarray_open_sibling(plan({"uid": 1, "term_uid": 11}, [(1, "appended array")]), base=BA)
gate("T5 open row on the OUTPUT only -> clean", f == [], f)
f = SP.buildarray_open_sibling(plan({"uid": 1, "term_uid": 11}, [(5, "element")]), base=BA)
gate("T6 open row on ANOTHER node -> clean", f == [], f)
BA4 = ({1: "BuildArray"}, {1: [T("appended array", True, 10)] + [T("array", False, 11 + i) for i in range(4)]})
f = SP.buildarray_open_sibling(plan({"uid": 1, "term_uid": 12}, [(1, "array")]), base=BA4)
gate("T7 4 inputs all 'array', one wired, 'array' open -> FLAG (same name, sibling)", len(f) == 1, f)
BA2 = ({1: "BuildArray"}, {1: [T("appended array", True, 10), T("array", False, 11), T("element", False, 12)]})
f = SP.buildarray_open_sibling(plan({"uid": 1, "term_uid": 11}, [(1, "array")]), base=BA2)
gate("T8 the only 'array' input is the wired one, open row names it -> clean (not a sibling)", f == [], f)


def replay(p):
    return SP.buildarray_open_sibling(json.load(open(p, encoding="utf-8")), licences=SP.pb_licences(p))


b1 = sorted(glob.glob(os.path.join(HERE, "plan_l2b1*.json")))
b1 = [p for p in b1 if json.load(open(p, encoding="utf-8")).get("schema") == "stageplan/1"]
r1 = dict((os.path.basename(p), replay(p)) for p in b1)
nodes1 = sorted(set(x["node"] for v in r1.values() for x in v))
gate("R1 plan_l2b1* ({0}) flag #2626 only".format(sorted(r1)), nodes1 == [2626],
     dict((k, [(x["row"], x["node"], x["wired"], x["open"], x["licensed"]) for x in v]) for k, v in r1.items()))
# review archive/peer/2026-09-28-c114a-selftest.md item 3: the licence lookup itself is checked
gate("R1b plan_l2b1.json's #2626 flag is licensed by plan_l2b1_licence.json; plan_l2b1_in.json's is not",
     [x["licensed"] for x in r1.get("plan_l2b1.json", [])] == ["tools/bench/plan_l2b1_licence.json"] and
     [x["licensed"] for x in r1.get("plan_l2b1_in.json", [])] == [None], r1)
# review item 4 (cheapest test): the in-plan IS the 9-row final's input (md5 recorded by card 113-4) and has its rows
p9, p9i = [json.load(open(os.path.join(HERE, n), encoding="utf-8")) for n in ("plan_l2b2b_9row.json", "plan_l2b2b_in_9row.json")]
gate("R2a plan_l2b2b_in_9row.json md5 == d13c0de4 (result_113-4.json) and its actions/open_rows == the 9-row final's",
     SP.md5(os.path.join(HERE, "plan_l2b2b_in_9row.json")) == "d13c0de4f260373ecde033d1e8a04a13" and
     p9["actions"] == p9i["actions"] and p9["open_rows"] == p9i["open_rows"], SP.md5(os.path.join(HERE, "plan_l2b2b_in_9row.json")))
for nm in ("plan_l2b2b_9row.json", "plan_l2b2b_in_9row.json"):       # the final 9-row plan and its input plan
    r2 = replay(os.path.join(HERE, nm))
    gate("R2 {0} flags #11261 only, unlicensed".format(nm), [x["node"] for x in r2] == [11261] and
         not r2[0]["licensed"], [(x["row"], x["node"], x["wired"], x["open"], x["licensed"]) for x in r2])
for nm in ("plan_l2b2b.json", "plan_l2b2b_in.json"):                  # the delivered 8-row plan and its input plan
    r3 = replay(os.path.join(HERE, nm))
    gate("R3 delivered {0} (8 rows) not flagged".format(nm), r3 == [], r3)
skip = set(b1) | set(os.path.join(HERE, n) for n in ("plan_l2b2b_9row.json", "plan_l2b2b.json", "plan_l2b2b_in_9row.json",
                                                     "plan_l2b2b_in.json"))
others, hits = 0, []
for p in sorted(glob.glob(os.path.join(HERE, "*.json"))):
    if p in skip:
        continue
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    if not isinstance(d, dict) or d.get("schema") != "stageplan/1":
        continue
    others += 1
    hits += [(os.path.basename(p), x["row"], x["node"], x["licensed"]) for x in SP.buildarray_open_sibling(
        d, licences=SP.pb_licences(p))]
gate("R4 every other TOP-LEVEL tools/bench/*.json stageplan/1 ({0} files) flags nothing".format(others), not hits, hits[:10])
# review item 4: tools/bench/sim/** (rehearsal / step copies) is REPORTED, not gated - its copies of l2b1/l2b2b plans flag
sim = []
for p in sorted(glob.glob(os.path.join(HERE, "sim", "**", "*.json"), recursive=True)):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:  # noqa: BLE001
        continue
    if isinstance(d, dict) and d.get("schema") == "stageplan/1":
        sim += [(os.path.relpath(p, HERE), x["row"], x["node"]) for x in SP.buildarray_open_sibling(d, licences=SP.pb_licences(p))]
print("  INFO sim/** stageplan flags (not gated): {0}".format(sorted(set((n, r) for _p, r, n in sim))), flush=True)
npass = sum(1 for g in gates if g[1])
first = next((g[0] for g in gates if not g[1]), None)
print(P.result_line(P.make_result(npass, len(gates) - npass, first, status="PASS" if npass == len(gates) else "FAIL")))
