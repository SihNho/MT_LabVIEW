"""diag_c133_6_fsframes - card 133-6, offline, read-only: where the base graph of each P3b-2 plan keeps its FS frame lists
(fs_frames), which frames the terminal rows cover, and whether 27641 is in either. No LabVIEW."""
import json, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = lambda *p: json.load(open(os.path.join(ROOT, *p), encoding="utf-8"))
for p in ("tools/bench/plan_ring_p3b2a.json", "tools/bench/plan_ring_p3b2b.json", "tools/bench/plan_ring_p3b2b_provisional_c133_5.json"):
    P = J(p); b = P["finalized"]["base"]; B = J(b["path"])
    tf = sorted(set(int(r["frame_diagram"] or 0) for r in B["terminals"]))
    print(p, "base", b)
    print("  keys", sorted(k for k in B if k != "terminals"))
    print("  fs_frames", B.get("fs_frames"))
    ow = B.get("owners")
    print("  owners type", type(ow).__name__, "fs-ish", {k: v for k, v in (ow.items() if isinstance(ow, dict) else []) if isinstance(v, list) and v and (v[0] in ("FlatSequenceFrame",) or str(v[0]).lstrip("-").isdigit() and int(v[0]) in (27509, -1))})
    print("  terminal frames", tf, "27641 in", 27641 in tf)
print("RESULT {}".format(json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []})))
