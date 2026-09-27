"""diag_c115b_inv - card 115-2: read-only summary of the 12 SR candidates in facts_c114e_inventory.json (no LabVIEW)."""
import json, os
os.chdir(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
d = json.load(open("tools/bench/facts_c114e_inventory.json", encoding="utf-8"))
print([k for k in d])
for c in d["candidates"]:
    if c.get("class") not in ("RightShiftRegister", "LeftShiftRegister"):
        continue
    print(c["uid"], c["class"], "pair", c.get("pair"), "live", c["live_consumers_n"], "s1eff", c.get("s1_effective_consumers"))
    for f in c["faces"]:
        print("   ", f["term_uid"], f["tclass"], "src" if f["is_source"] else "snk", "w", f["wire"], "diag", f["frame_diagram"],
              "rows", [(r[0], r[1], r[2], r[3][:6]) for r in f["raw_wire_rows"]])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
