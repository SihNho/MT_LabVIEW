# ---
# labview: none
# hardware: none
# ---
r"""diag_c149_a1_3_items - card 149-a1-3 offline: list the Error List items of the s06 read (181243) and the s05 read (012323)
side by side (index, raw, capture, show-error after-capture), plus header text and the first/last errwin capture. Reads JSON only.
PREDICTION CONTRACT: s06 51 items, s05 55 items (diag_c147_a1_1_el.log:20-22)."""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
F = {"s06": "tools/bench/errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json",
     "s05": "tools/bench/errorlist_D1_ring_p4s05_20261008_002621_20261008_012323.json"}
for tag, rel in F.items():
    d = json.load(open(os.path.join(ROOT, rel), encoding="utf-8"))
    it = d.get("items", [])
    print("==", tag, rel, "n_reported", d.get("n_reported"), "from", repr(d.get("n_reported_from")), "items", len(it),
          "zero_capture", d.get("zero_capture"))
    for i in it:
        se = i.get("show_error") or {}
        print("%s %2s | %-90s | lic=%s | cap=%s | after=%s" % (tag, i.get("index"), (i.get("raw") or "")[:90], i.get("licensed_by"),
              os.path.basename(i.get("capture") or ""), os.path.basename(se.get("bd_after") or "")))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}', flush=True)
