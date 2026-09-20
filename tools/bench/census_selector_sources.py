r"""census_selector_sources.py - name the objects that feed the three reseed selector wires whose SOURCE owner came
back as 'Diagram' from OpWireSource_v1 (tools/bench/build_opwiresource_v1.log run 4: wires 10312 Or.y, 9806 And.y,
10142 Equal?.y). 'Diagram' is the documented signature of a front-panel CONTROL TERMINAL - its Owner is the diagram,
not the control (peer archive/peer/2026-09-15-opconstvaluen-scan-three-selectors-missing.md §4 caveat).

gscript.panel_wiring(MAIN) lists every TOP-LEVEL front-panel object with the wire uid its diagram terminal carries, in
ONE op run - so if these wires are control terminals of top-level panel objects, the labels fall out immediately and
independently of the property chain. Read-only; the main VI is never modified.

predict: the three wires appear in panel_wiring as CONTROLS (indicator False); wire 10850 does NOT (it is the constant).

  py tools/bgrun.py --max-min 8 --log tools/bench/census_selector_sources.log -- py -u tools/bench/census_selector_sources.py
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import MAIN, com_preflight  # noqa: E402

TARGETS = {10312: "Or.y", 9806: "And.y", 10142: "Equal?.y (auto-reset period)", 10850: "Less?.y (constant I32 0)"}


def main():
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    g.reset(); com_preflight()
    t0 = time.time(); rows = g.panel_wiring(MAIN)
    print(f"   panel_wiring(MAIN) -> {len(rows)} top-level panel objects in {time.time() - t0:.1f}s", flush=True)
    by_wire = {}
    for r in rows:
        by_wire.setdefault(r["wire"], []).append(r)
    for wu, role in TARGETS.items():
        hits = by_wire.get(wu, [])
        if hits:
            for h in hits:
                print(f"OBSERVED: wire {wu} ({role}) <- panel object {h['label']!r} "
                      f"{'indicator' if h['indicator'] else 'CONTROL'} uid {h['uid']}", flush=True)
        else:
            print(f"OBSERVED: wire {wu} ({role}) has no TOP-LEVEL panel object (nested cluster/tab element, a local, "
                  f"or not a control terminal)", flush=True)
    wired = sorted(w for w in by_wire if w)
    print(f"   panel wires seen: {len(wired)}; sample {wired[:12]}", flush=True)
    same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
    print(f"   {'PASS' if same else 'FAIL'} main VI unchanged", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
