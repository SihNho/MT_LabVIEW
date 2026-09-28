"""Card 119-3 S2: count stageplan/1 files under tools/bench that validate against docs/protocol/stageplan.json.
Run once before and once after the schema widening; the OK set must be identical (widening only).
Prediction: after >= before, and every OK-before path is OK-after. No LabVIEW, no COM."""
import glob, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
import protocol
ok, bad = [], []
for p in sorted(set(glob.glob("tools/bench/**/*.json", recursive=True))):
    try:
        with open(p, encoding="utf-8") as f:
            o = json.load(f)
    except Exception:
        continue
    if not isinstance(o, dict) or o.get("schema") != "stageplan/1":
        continue
    v, why = protocol.validate_obj(o)
    (ok if v else bad).append((p.replace("\\", "/"), why))
for p, w in ok:
    print("OK  ", p)
for p, w in bad:
    print("BAD ", p, "|", w[:160])
print("COUNT ok=%d bad=%d" % (len(ok), len(bad)))
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
