r"""census_dnc_property_ids.py - which unique ID is DigitalNumericConstant.'Numeric Text' in LabVIEW 2026? The wiki table
said 634D004; the fleet's build_property attached RadixVis for it (tools/bench/build_opconstvaluen_v0.log run 1). Sweep
634D000..634D00F (and 5DCFC00..5DCFC03 as a control) on a SCRATCH copy of OpReport_v3.vi: one property node per id,
record the DATA terminal name it produces (the fleet reads terminal names, never IDs). Nothing saved; scratch deleted;
a fresh LabVIEW instance so the dirty OpConstValueN_v0 in memory from run 1 is gone.
predict: exactly one id in the sweep yields a terminal named like 'Numeric Text' / 'NumText'; 634D004 -> RadixVis again.

  py tools/bgrun.py --max-min 10 --log tools/bench/census_dnc_property_ids.log -- py -u tools/bench/census_dnc_property_ids.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

walk = B.walk
SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
SCR = os.path.join(g.CLAUDEDEV, "OpCensus_scratch.vi")
# review ...-opconstvaluen-fail1-634d004-is-radixvis: no blind sweep - only the class's DOCUMENTED public members
# (634D001..634D008 per the wiki, whose numbering is shifted); 634D003 is the reviewer's leading candidate
IDS = [f"634D{i:03X}" for i in range(0x01, 0x09)]


def main():
    fresh()
    if os.path.exists(SCR):
        os.remove(SCR)
    shutil.copyfile(SRC, SCR); time.sleep(0.3)
    found = {}
    try:
        g.open_panel(SCR); time.sleep(0.8)
        y = 300
        for pid in IDS:
            pn0 = g.uids(SCR, "Property")
            try:
                g.build_property(SCR, "VI Server:DigitalNumericConstant", [(pid, False)], (1500, y)); y += 120
            except Exception as e:
                print(f"OBSERVED: {pid} -> build EXC {str(e)[:90]}", flush=True); continue
            new = [u for u in g.uids(SCR, "Property") if u not in pn0]
            if len(new) != 1:
                print(f"OBSERVED: {pid} -> {len(new)} new nodes", flush=True); continue
            w = walk(SCR, 0)
            data = [r["name"] for r in w[new[0]][2] if r["name"] not in ("reference", "reference out", "error in (no error)", "error out")]
            print(f"OBSERVED: {pid} -> terminals {data}", flush=True); found[pid] = data
    finally:
        try:
            g.close_panel(SCR)
        except Exception as e:
            print(f"   close_panel EXC {str(e)[:80]}", flush=True)
        time.sleep(0.5)
        if os.path.exists(SCR):
            os.remove(SCR); print("   scratch deleted", flush=True)
    hits = {p: n for p, n in found.items() if any("numeric" in x.lower() or "numtext" in x.lower() or "text" in x.lower() for x in n)}
    print(f"SUMMARY candidates for Numeric Text: {hits}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
