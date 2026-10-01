"""card 126-3: read-only probe of the P3a base graph (no LabVIEW, no COM) - keys, fs_tunnel_pairs shape, owners of the
case #22694 frames, FSIT row shape. PREDICTION: prints facts only; ends with a RESULT line."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

d = json.load(open(os.path.join(ROOT, "tools/bench/graph_ring_p3a_20261001_190155.json"), encoding="utf-8"))
print("KEYS", list(d))
fp = d.get("fs_tunnel_pairs")
print("FSPAIRS", type(fp).__name__, len(fp or []), (fp or [])[:2])
o = d.get("owners") or {}
print("OWNERS n", len(o), "27219", o.get("27219"), "27232", o.get("27232"), "22694", o.get("22694"))
fsit = [r for r in d["terminals"] if r["owner_class"] == "FlatSequenceInnerTunnel"]
print("FSIT rows", len(fsit), fsit[:4])
print("rows on 27219", sum(1 for r in d["terminals"] if r["frame_diagram"] == 27219))
print("ROW0", d["terminals"][0])
print("OBJ0", (d.get("objs") or [None])[0], "n objs", len(d.get("objs") or []))
print("FS objs", [x for x in d.get("objs") or [] if x.get("class") in ("FlatSequence", "FlatSequenceInnerTunnel")][:4])
print(protocol.result_line(protocol.make_result(1, 0)))
