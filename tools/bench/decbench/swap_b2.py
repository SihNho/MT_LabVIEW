"""swap_b2 - card chat-B2 items 1-3: replace S3/T2/R3 in cases.json by the cases in new_cases_b2.json (same position).
Keeps the replaced case text in cases_replaced_b2.json (nothing deleted). Idempotent: a swap whose new id is already present
is skipped. PREDICTION: 3 swapped, 10 cases after, ids unique. Ends with a RESULT line.
    py tools/bench/decbench/swap_b2.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "cases.json")
doc = json.load(open(P, encoding="utf-8"))
sw = json.load(open(os.path.join(HERE, "new_cases_b2.json"), encoding="utf-8"))["swaps"]
old_p = os.path.join(HERE, "cases_replaced_b2.json")
kept = json.load(open(old_p, encoding="utf-8")) if os.path.exists(old_p) else {"schema": "decbench-replaced/1", "cases": []}
ids = [c["id"] for c in doc["cases"]]
done, fails = 0, []
for s in sw:
    new = s["case"]
    if new["id"] in ids:
        print("SKIP %s already present" % new["id"])
        continue
    if s["replaces"] not in ids:
        fails.append("missing %s" % s["replaces"])
        continue
    i = ids.index(s["replaces"])
    kept["cases"].append(doc["cases"][i])
    doc["cases"][i] = new
    ids[i] = new["id"]
    done += 1
    print("SWAP %s -> %s" % (s["replaces"], new["id"]))
if len(set(ids)) != len(ids) or len(ids) != 10:
    fails.append("ids %s" % ids)
if not fails:
    json.dump(doc, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(kept, open(old_p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("CASES", ids)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                              "gates": {"pass": 0 if fails else 1, "fail": len(fails)},
                              "first_fail": fails[0] if fails else None, "artefacts": []}))
