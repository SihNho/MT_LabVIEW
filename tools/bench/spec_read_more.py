"""spec_read_more.py - same read as spec_read.py (FP datatypes, object lists, net_map of every diagram) for the
calibration-loader VI COPIES in claudeDev\SPEC, whose inventory (fp labels, diagram count) is taken here first.
  py tools/bgrun.py --max-min 45 --log tools/bench/spec_read_more.log -- py -u tools/bench/spec_read_more.py
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import gscript as g
import spec_read as sr
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
NAMES = ["make both cosine bandpass.vi", "proc cal image-make bandpass.vi", "prep cal image.vi", "build cal image.vi",
         "calibration- generate 1 I of r, reentrant.vi", "calibration- generate 2 I of r, reentrant.vi", "Load and prep N cal images.vi"]
INV_OUT = os.path.join(HERE, "spec_inventory_more.json")


def main():
    inv = json.load(open(INV_OUT, encoding="utf-8")) if os.path.exists(INV_OUT) else {}
    for name in NAMES:
        path = os.path.join(sr.SPEC, name)
        if name not in inv:
            t0 = time.time(); g.report(path, "SubVI")
            fp = g.fp_labels(path)
            counts = {c: g.count(path, c) for c in ("Node", "Constant", "Wire", "Diagram")}
            inv[name] = {"fp": fp, "counts": counts}
            json.dump(inv, open(INV_OUT, "w", encoding="utf-8"), indent=1)
            print(f"inventory {name}: {len(fp)} fp, {counts} ({time.time() - t0:.0f}s)", flush=True)
    sr.INV.update(inv)
    sr.ORDER[:] = NAMES
    sr.OUT = os.path.join(HERE, "spec_wiring_more.json")
    return sr.main()


if __name__ == "__main__":
    sys.exit(main())
