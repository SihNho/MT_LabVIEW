"""whats_next_to_9775.py - is the camera's Height/Width property node READING or WRITING?

Where this stands. The configuration step is diagram 87, and exactly one node in the entire main VI touches camera
geometry: uid 9775, an IMAQdx property node with terminals `Height` then `Width`. Reading the diagram's nets showed
both terminals ARE wired - wire 32937 (Height) and 32938 (Width) - but each net came back with only ONE terminal on
it, its own. The other end of each wire is an object that neither `net_map` nor the Step-0 diagram tree enumerates:
both are built from the same `Nodes[]` walk, and diagram 87's tree entry lists exactly the 14 nodes net_map found, so
front-panel TERMINALS and CONSTANTS are invisible to both.

That is not a dead end, it is just a different enumeration. `Traverse for GObjects` by class reaches them, and each
object reports a position. uid 9775 sits at **(-15780, 1017)**, so:

  * a **Constant** just to its LEFT at a similar y  => the node is being FED => it WRITES the camera ROI, and that
    constant's value is the answer to the user's halving report;
  * an indicator **Terminal** just to its RIGHT     => the node FEEDS it => it READS the camera, the VI never sets the
    ROI, and the 640x512 came from outside the VI entirely.

Proximity is evidence, not proof, so the script prints everything within a generous box and sorts by distance rather
than announcing a winner from the nearest hit alone. If the picture is ambiguous the next step is the constant-value
op (tools/recipes/build_opconstvalue.py), which would read the constant outright.

READ-ONLY: Traverse only; never modifies, never saves, never runs the VI. No hardware.
  py tools/bgrun.py --max-min 20 --log tools/bench/whats_next_to_9775.log -- py -u tools/bench/whats_next_to_9775.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
OUT = os.path.join(HERE, "near_9775.json")
ANCHOR = (-15780, 1017)                 # uid 9775, from property_node_map.json
BOX = 700                               # generous: a wire can run a long way before it reaches its source
CLASSES = ("Terminal", "Constant", "DigitalNumericConstant", "NumericConstant", "StringConstant", "GObject")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    rows = []
    for cls in CLASSES:
        try:
            n = g.count(WORK, cls)
        except Exception as e:
            print(f"{cls:<24} class not traversable: {str(e)[:90]}", flush=True)
            continue
        print(f"{cls:<24} {n} objects in the VI", flush=True)
        if n == 0 or n > 1200:            # GObject will be huge; skip rather than spend an hour
            print(f"   (skipping the per-object read: {'empty' if n == 0 else 'too many, use a narrower class'})",
                  flush=True)
            continue
        try:
            objs = g.report(WORK, cls)
        except Exception as e:
            print(f"   report failed: {str(e)[:110]}", flush=True); continue
        for o in objs:
            p = o.get("pos") or (0, 0)
            dx, dy = p[0] - ANCHOR[0], p[1] - ANCHOR[1]
            if abs(dx) <= BOX and abs(dy) <= BOX:
                rows.append({"cls": cls, "uid": o["uid"], "pos": list(p), "dx": dx, "dy": dy,
                             "side": "LEFT (feeds the node -> WRITE)" if dx < 0 else "RIGHT (fed by the node -> READ)",
                             "dist": abs(dx) + abs(dy), "owner": o.get("owner")})

    rows.sort(key=lambda r: r["dist"])
    print(f"\n{'=' * 78}\nOBJECTS WITHIN {BOX} OF uid 9775 AT {ANCHOR}: {len(rows)}", flush=True)
    for r in rows[:40]:
        print(f"   {r['cls']:<22} uid {r['uid']:<7} pos {r['pos']}  dx {r['dx']:+6d} dy {r['dy']:+6d}  "
              f"{r['side']}   owner {r['owner']}", flush=True)
    json.dump(rows, open(OUT, "w", encoding="utf-8"), indent=1)
    print("\nwritten to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
