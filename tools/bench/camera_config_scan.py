"""camera_config_scan.py - find the main VI's camera configuration step and read what it writes, in what order.

The camera was just read directly through niimaqdx.dll (tools/bench/imaqdx_limits.py) and two things came out:
the frame is 1280x1024 at 2x2 binning RIGHT AFTER a fresh open, and the ceiling is 247.95 Hz. The user's report that
"the first run halves the image and the second restores it" therefore cannot be the camera persisting a bad state -
opening a session already puts it back to full size. Whatever halves it is the configuration step itself, which the
user placed exactly: "당연히 프런트패널이 아니고 블락 다이어그램에 있지. 코드 시작부분이 configuration step이잖아",
"property node로 입력되는 상수값이거든".

An IMAQdx property node names each attribute it touches as a TERMINAL, so the attribute list and the write ORDER are
both readable without running anything. Order is the whole question: writing Width before Binning lets the camera
divide the width by the new binning factor, which is the one mechanism that produces exactly half.

Scans diagram by diagram and prints only the nodes that mention a camera attribute, with a JSON checkpoint after each
diagram so an interrupted run resumes instead of restarting.

READ-ONLY: opens the working copy, never modifies it, never saves, never runs it. No hardware.
  py tools/bgrun.py --max-min 25 --log tools/bench/camera_config_scan.log -- py -u tools/bench/camera_config_scan.py [first] [last]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
OUT = os.path.join(HERE, "camera_config_scan.json")
# Either a range (first last) or an explicit comma-separated list of diagram indices. The list form is what actually
# works: `tools/bench/find_property_nodes.py` maps every Property node to its diagram in ~100 s by cross-referencing
# the Step-0 diagram tree, so only the diagrams that HOLD a property node need walking - 38 of 170 - and they can be
# ordered cheapest-first by node count. Walking 0..169 blindly was never going to finish inside a deadline.
if len(sys.argv) > 1 and "," in sys.argv[1]:
    DIAGRAMS = [int(x) for x in sys.argv[1].split(",")]
else:
    FIRST = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    LAST = int(sys.argv[2]) if len(sys.argv) > 2 else 40
    DIAGRAMS = list(range(FIRST, LAST + 1))
g._run.__defaults__ = (6.0, 60.0)

# terminal-name fragments that mark a camera node. "session" and "attribute" catch the IMAQdx VIs even when the
# property node itself is elsewhere; the geometry names are the ones that decide the halving question.
CAM = ("width", "height", "binning", "offsetx", "offsety", "offset x", "offset y", "pixel format", "pixelformat",
       "attribute", "imaqdx", "camera", "session", "frame rate", "framerate", "exposure", "buffer", "image out",
       "acquisition", "roi", "decimation", "reverse")
# KNOWN BLIND SPOT of the list above (noticed 2026-09-12 while diagram 19 came back): a `Value` property node on a
# front-panel control named `Width` has the TERMINAL name `Value` - the control's label never appears in the terminal
# list - so a configuration that writes the camera through such a node is invisible here. Adding "value" would match
# most of the VI and drown the signal, so the complementary evidence is gathered separately instead, by reading the
# front-panel control VALUES with tools/bench/main_vi_camera_values.py. Neither scan alone is sufficient.
GEOM = ("width", "height", "binning", "offset", "pixelformat", "pixel format")


def main():
    g._lv = None
    # NO g.report() passes here, deliberately. The first version classified every node by traversing the VI once per
    # class (SubVI, 5 structure classes, Property, Invoke) - 13 whole-hierarchy traversals of a 473 KB main VI with a
    # deep subVI tree - and produced ZERO output in 19 minutes before its deadline (2026-09-12). net_map's terminal
    # NAMES already identify a camera node, which is the only thing this scan needs, so the classification is dropped
    # and the first printed line now arrives after the first diagram instead of after the traversals.
    subs, structs, pos = set(), {}, {}

    out = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    for dia in DIAGRAMS:
        if str(dia) in out:
            continue
        try:
            nodes, _ = g.net_map(WORK, diagram_index=dia, max_nodes=140, max_terms=24)
        except Exception as e:
            print(f"diagram {dia}: FAILED {str(e)[:110]}", flush=True)
            out[str(dia)] = {"error": str(e)[:200]}
            json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
            continue
        hits = []
        for _, (uid, lbl, terms) in nodes.items():
            names = [nm for _, nm, _ in terms if nm]
            low = " | ".join(names).lower()
            if not any(k in low for k in CAM):
                continue
            kind = "SubVI" if uid in subs else structs.get(uid, "primitive/other")
            hits.append({"uid": uid, "kind": kind, "label": lbl, "pos": pos.get(uid),
                         "terms": names,
                         "geometry": sorted({k for k in GEOM if k in low})})
        out[str(dia)] = hits
        json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
        if hits:
            print(f"\n==== diagram {dia}: {len(nodes)} nodes, {len(hits)} camera-related", flush=True)
            for h in hits:
                mark = "  <== GEOMETRY" if h["geometry"] else ""
                print(f"   {h['kind']:<16} uid {h['uid']:<6} pos {h['pos']}{mark}", flush=True)
                print(f"      terminals (in order): {h['terms']}", flush=True)
        else:
            print(f"diagram {dia}: {len(nodes)} nodes, no camera node", flush=True)

    geo = [(d, h) for d, hs in out.items() if isinstance(hs, list) for h in hs if h.get("geometry")]
    print(f"\n{'=' * 78}\nGEOMETRY-TOUCHING NODES: {len(geo)}", flush=True)
    for d, h in geo:
        print(f"   diagram {d} uid {h['uid']} ({h['kind']}) {h['geometry']}  ->  {h['terms']}", flush=True)
    print("\nwritten to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
