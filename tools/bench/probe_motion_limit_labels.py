r"""probe_motion_limit_labels.py - M3 SENSITIVITY CHECK. Read-only, no motor, no serial, nothing saved.

probe_flatseq_walk_run2.log reports "LIMITING-construct matches: 0" for every motion subVI. That number is only
meaningful if the method CAN see an unlabelled primitive: gscript.node_labels reads Node.Label 6359001, and a
LabVIEW primitive that the user never renamed may report ''. So before "no limits live in these subVIs" is
written down anywhere, measure the method's own sensitivity:

  * how many NODES exist per diagram (report_all 'Node'-ish classes / count) vs how many LABELS came back
    non-empty, and
  * the FULL label list, verbatim, so a human can see what the scan actually had to work with.

PREDICTION CONTRACT:
  S1 for each VI, node_labels returns one row per node (rows == the node count), i.e. no node is skipped.
  S2 if a large fraction of those rows have an EMPTY label, then "0 limiting-construct matches" is WEAK
     evidence and must be reported as such; if labels are mostly non-empty it is strong.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

LV = r"C:\Program Files\National Instruments\LabVIEW 2026"
MERC = os.path.join(LV, r"instr.lib\Mercury\GCS_LabVIEW\Low Level")
LAB = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
VIS = [
    ("MOV.vi", os.path.join(MERC, r"General command.llb\MOV.vi")),
    ("VEL.vi", os.path.join(MERC, r"General command.llb\VEL.vi")),
    ("GOH.vi", os.path.join(MERC, r"Limits.llb\GOH.vi")),
    ("TMX?.vi", os.path.join(MERC, r"Limits.llb\TMX?.vi")),
    ("ASI Move Axis to Position.vi", os.path.join(LV, r"instr.lib\ASI TG-1000\Public\Action\Move Axis to Position.vi")),
    ("Autonics SetCommand.vi", os.path.join(LV, r"instr.lib\Autonics Motor\SetCommand.vi")),
    ("Max Trans Pos.vi", os.path.join(LAB, r"DY\Background VIs\Max Trans Pos.vi")),
]
OUT = os.path.join(HERE, "probe_motion_limit_labels.json")


def main():
    fresh()
    res = {}
    try:
        for name, path in VIS:
            print(f"\n=== {name}\n    {path}", flush=True)
            rec = {"path": path, "diagrams": {}}
            try:
                nd = int(g.count(path, "Diagram"))
            except Exception as e:
                print(f"    count(Diagram) RAISED {str(e)[:160]}", flush=True)
                res[name] = {"err": str(e)[:200]}
                continue
            tot = named = 0
            for di in range(nd):
                try:
                    rows = g.node_labels(path, di)
                except Exception as e:
                    print(f"    d{di}: node_labels RAISED {str(e)[:110]}", flush=True)
                    continue
                labs = [r["label"] for r in rows]
                tot += len(rows)
                named += sum(1 for x in labs if x.strip())
                rec["diagrams"][di] = [{"uid": r["uid"], "label": r["label"]} for r in rows]
                if rows:
                    print(f"    d{di}: {len(rows)} node(s) -> {[x if x else '<EMPTY>' for x in labs]}", flush=True)
            rec["nodes_total"] = tot
            rec["labels_nonempty"] = named
            frac = (named / tot * 100) if tot else 0.0
            print(f"    TOTAL {tot} node rows, {named} with a non-empty label ({frac:.0f} %)", flush=True)
            res[name] = rec
    finally:
        try:
            g.reset()
        except Exception:
            pass
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, ensure_ascii=False)
        print("\nSENSITIVITY SUMMARY (VI: node rows / non-empty labels)", flush=True)
        for k, v in res.items():
            if "nodes_total" in v:
                print(f"   {k:32s} {v['nodes_total']:4d} / {v['labels_nonempty']:4d}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
