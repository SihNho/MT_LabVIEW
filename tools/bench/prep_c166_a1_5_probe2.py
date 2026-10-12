# ---
# labview: none
# hardware: none
# ---
"""Card 166-a1-5 probe 2: compact listing of the 46 expected entries (47 items) of the P5-final expected file, and the
47 read items' object/reason (json only, no LabVIEW). Prediction: count sum 47; read items 47 with uid null."""
import json, os, sys, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT); sys.path.insert(0, "tools")
import protocol
B = "tools/bench/"
X = json.load(open(B + "errorlist_expected_D1_ring_p5_20261010_172913.json", encoding="utf-8"))
E = json.load(open(B + "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json", encoding="utf-8"))
print("format_note", X["format_note"])
n = 0
for e in X["expected"]:
    n += e.get("count", 0)
    if "item" not in e:
        print("EXP-OTHER", json.dumps(e)[:1500]); continue
    print("EXP", e["item"], e["class"], e["count"], json.dumps(e["object"]), "|", e["clears_by"]["kind"], "|",
          e["clears_by"].get("cause", "")[:260], "| plan_action", e.get("plan_action"), "| read", e["read_index"],
          "| extra-keys", sorted(set(e) - {"item", "norm_all", "count", "label", "class", "object", "pairing", "clears_by", "cite", "read_index"}))
print("SUM", n, collections.Counter(e.get("class") for e in X["expected"]))
for it in E["items"]:
    print("READ", it["index"], it["raw"][:120])
print("missing", json.dumps(E["missing"])[:800]); print("by_design", json.dumps(E["by_design"])[:800])
print(protocol.result_line({"status": "PASS" if n == 47 else "FAIL", "gates": {"pass": int(n == 47), "fail": int(n != 47)},
                            "first_fail": None if n == 47 else "sum!=47", "artefacts": []}))
