# ---
# labview: none
# hardware: none
# ---
"""Card 154-a1-2 follow-up: owner chains (s09 owners map) of the diagrams the census walk reached, plus the
terminal rows of a few named nodes in S1 and s09 (stored json only, no LabVIEW).
Prior art: diag_c154_a1_2_census.py (same files). Prediction: every listed uid prints a chain or 'no owner row';
ends with a RESULT line (PASS when both files parse)."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import protocol
s1 = json.loads((ROOT / "docs/wiki/subvi/D1_s1_copy.json").read_text(encoding="utf-8"))
s9 = json.loads((ROOT / "tools/bench/graph_ring_p4s09_20261009_062044.json").read_text(encoding="utf-8"))
own = {int(k): v for k, v in s9["owners"].items()}
cls = {o["uid"]: (o["class"], o["owner"]) for o in s9["objs"]}
fsf = s9["fs_measured"]["fs_frames"]
fs_of = {d: int(fs) for fs, ds in fsf.items() for d in ds}


def chain(u):
    out, seen = [], set()
    while u in own and u not in seen:
        seen.add(u)
        c, p = own[u]
        out.append(f"{c}#{p}")
        u = p
    return out


for d in (639, 3227, 3292, 27219, 27232, 32464, 16565, 11926, 11936, 7911, 29894, 23166, 10417, 10423, 12599, 12617,
          4866, 686, 536, 759):
    print(f"CHAIN d{d}: {chain(d)} | fs_frame_of {fs_of.get(d)} | obj {cls.get(d)}")
for u in (22694, 27509, 16543, 10407, 1359, 29874, 23032, 10170, 637, 3045, 29440, 12195, 11942, 3302, 12633, 10429):
    print(f"OBJ #{u}: {cls.get(u)} owner-chain-of-uid {chain(u)}")
for name, g in (("S1", s1), ("s09", s9)):
    for u in (194, 2347, 30146, 10114, 29415, 22694, 3191):
        rows = sorted({(t["term_uid"], t["term_name"], t["is_source"], t["wire_uid"], t["frame_diagram"], t["owner_class"])
                       for t in g["terminals"] if t["owner_uid"] == u})
        print(f"TERMS[{name}] #{u}: {rows}")
for name, g in (("S1", s1), ("s09", s9)):
    for u in (10686, 10429, 3302, 12633, 11942):
        rows = sorted({(t["term_uid"], t["term_name"], t["is_source"], t["wire_uid"], t["frame_diagram"])
                       for t in g["terminals"] if t["owner_uid"] == u})
        print(f"TERMS[{name}] #{u}: {rows}")
    for w in (3051, 3082, 1420, 1827, 10799, 3050, 23526, 23847):
        rows = sorted({(t["owner_uid"], t["owner_class"], t["term_name"], t["is_source"], t["frame_diagram"])
                       for t in g["terminals"] if t["wire_uid"] == w})
        print(f"WIRE[{name}] w{w}: {rows}")
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
