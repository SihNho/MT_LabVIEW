"""patch_nodeterms_classes.py - re-read the class censuses (Global/Local/Property/Invoke uids) that sweep run 1 lost
(its final stats assignment overwrote them) and write them into main_vi_nodeterms.json's stats. Four report_all runs.
  py tools/bgrun.py --max-min 4 --log tools/bench/patch_nodeterms_classes.log -- py -u tools/bench/patch_nodeterms_classes.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

P = os.path.join(HERE, "main_vi_nodeterms.json")


def main():
    g._lv = None
    d = json.load(open(P, encoding="utf-8"))
    for cls in ("Global", "Local", "Property", "Invoke"):
        rows = g.report_all(d["vi"], cls)
        d["stats"][f"class_{cls}"] = [o["uid"] for o in rows]
        print(f"class {cls!r}: {len(rows)} -> {[o['uid'] for o in rows][:12]}{'...' if len(rows) > 12 else ''}", flush=True)
    with open(P, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=1, ensure_ascii=False)
    print("patched", P, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
