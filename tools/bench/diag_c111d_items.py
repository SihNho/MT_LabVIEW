"""Card 111-4 helper (offline, no LabVIEW): list the 99 raw items of the 111-1 read with their norm() text."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
B = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(B, "errorlist_D1_l2_b1_20260927_193100_c111.json"), encoding="utf-8"))
print({k: d.get(k) for k in ("bed", "bed_md5_before", "bed_md5_after", "n_reported", "item_count", "verdict", "gates")})
r = json.load(open(os.path.join(B, "errorlist_D1_l2_b1_20260927_193100_c111_raw.json"), encoding="utf-8"))
print("raw items", len(r["items"]))
for i, it in enumerate(r["items"]):
    print(i, "|", it.get("raw"), "|", (it.get("detail") or "")[:140].replace("\n", " "))
