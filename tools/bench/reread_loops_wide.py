"""reread_loops_wide.py - re-read the frame loop and the display loop with the terminal list NOT truncated.

The hunt for the camera's Width/Height property node has cleared every diagram except two, and it cleared them
soundly: `find_property_nodes.py` placed all 106 Property nodes (0 unplaced), and the targeted walk of every diagram
holding one came back with no geometry terminals. The two exceptions are **diagram 43 (the frame loop) and diagram 99
(the display loop)**, which were never re-walked for this question - the data used for them came from
`tools/bench/loop_contents.json`, read on 2026-09-12 with **`max_terms=20`**.

That cap is the blind spot. A node with more than 20 terminals had its list silently cut at 20, so "no Width/Height in
43 or 99" is only true of the first 20 terminals of each node. Diagram 43 holds 10 Property nodes - the most of any
diagram in the VI - which is exactly where a multi-attribute IMAQdx property node would live.

So this re-reads only those two diagrams, with `max_terms=60`, and prints every Property node's full terminal list
plus anything matching a camera-geometry name. If the node is here, this finds it and gives the terminal ORDER, which
is the part that matters: a property node executes its terminals top to bottom.

If this ALSO comes back empty, the conclusion is not "keep looking harder" but "the node is not a VI-Server `Property`
object in the main VI" - e.g. it lives inside a subVI - and the search moves to the subVI hierarchy.

READ-ONLY: never modifies, never saves, never runs the VI. No hardware.
  py tools/bgrun.py --max-min 35 --log tools/bench/reread_loops_wide.log -- py -u tools/bench/reread_loops_wide.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
PMAP = os.path.join(HERE, "property_node_map.json")
OUT = os.path.join(HERE, "reread_loops_wide.json")
LOOPS = [(99, "display / bead-selection loop"), (43, "FRAME LOOP - 10 Property nodes, the most in the VI")]
GEOM = ("width", "height", "binning", "offset", "pixelformat", "pixel format", "roi", "decimation")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    pmap = json.load(open(PMAP, encoding="utf-8"))["Property"]
    prop_uids = {r["uid"] for r in pmap}
    per_dia = {}
    for r in pmap:
        per_dia.setdefault(r["diagram"], []).append(r["uid"])

    out = {}
    for dia, label in LOOPS:
        want = sorted(per_dia.get(dia, []))
        print(f"\n{'=' * 78}\n== diagram {dia}: {label}\n   {len(want)} Property nodes here: {want}", flush=True)
        nodes, _ = g.net_map(WORK, diagram_index=dia, max_nodes=140, max_terms=60)
        rows = []
        for _, (uid, lbl, terms) in nodes.items():
            names = [nm for _, nm, _ in terms if nm]
            low = " | ".join(names).lower()
            hit = sorted({k for k in GEOM if k in low})
            is_prop = uid in prop_uids
            rows.append({"uid": uid, "property_node": is_prop, "n_terms": len(names),
                         "terms": names, "geometry": hit})
            if hit:
                print(f"\n   *** GEOMETRY *** uid {uid} {'(Property node)' if is_prop else ''} {hit}", flush=True)
                print(f"       terminals in order: {names}", flush=True)
            elif is_prop:
                print(f"   Property uid {uid:<7} {len(names):>2} terminals: {names}", flush=True)
        out[str(dia)] = rows
        json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
        wide = [r for r in rows if r["n_terms"] >= 20]
        print(f"   -- {len(rows)} nodes; {len(wide)} had 20+ terminals "
              f"(these are the ones loop_contents.json truncated)", flush=True)

    geo = [(d, r) for d, rs in out.items() for r in rs if r["geometry"]]
    print(f"\n{'=' * 78}\nGEOMETRY NODES FOUND: {len(geo)}", flush=True)
    for d, r in geo:
        print(f"   diagram {d} uid {r['uid']} property_node={r['property_node']} -> {r['terms']}", flush=True)
    if not geo:
        print("   none. The camera geometry node is NOT a Property object on the main VI's diagrams - every one of the\n"
              "   106 was placed and walked. Next: the subVI hierarchy.", flush=True)
    print("\nwritten to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
