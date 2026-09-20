"""loop_contents.py - name what actually sits in each of the main VI's three While loops.

Step 0's walk (tools/bench/diagram_tree_main.json) established the skeleton: the tracking call site uid 5058 sits on
diagram 43, that diagram is owned by a WhileLoop, and the three While loops are diagrams 20, 43 and 99 holding 13, 75 and
22 nodes. The checkpoint stored node UIDs only, so the subVIs are counted but not identified.

This re-reads just those three diagrams and keeps each node's TERMINAL NAMES, which identify a subVI by its connector
pane far more reliably than a position would — `x,y,z array out` is the tracking kernel, `VISA resource name` is a serial
wrapper, `Value` on a Property Node is a front-panel access that costs a UI-thread switch.

The question it answers, and the reason the whole Step 0 exists: how much of the per-frame path is work that must be
inline, and how much is display, logging and instrument chatter that a producer/consumer split could take off the
critical path. Three diagrams only, so it is minutes rather than the hour the full walk took.

READ-ONLY: opens the working copy, never modifies, never saves, never runs it. No hardware.
  py tools/bgrun.py --max-min 25 --log tools/bench/loop_contents.log -- py -u tools/bench/loop_contents.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
OUT = os.path.join(HERE, "loop_contents.json")
LOOPS = [(20, "loop A"), (43, "FRAME LOOP (holds the tracking call, uid 5058)"), (99, "loop C")]
g._run.__defaults__ = (6.0, 60.0)

# terminal names that flag a cost we care about
FLAGS = {
    "UI-thread property access": ("value",),
    "serial / VISA": ("visa", "resource name"),
    "timing": ("milliseconds to wait", "millisecond timer"),
    "file IO": ("path", "file"),
    "image": ("image", "pixmap", "pixel"),
}


def main():
    g._lv = None
    subs = {o["uid"] for o in g.report(WORK, "SubVI")}
    structs = {}
    for cls in ("WhileLoop", "ForLoop", "CaseStructure", "Sequence", "EventStructure"):
        for o in g.report(WORK, cls):
            structs[o["uid"]] = cls
    out = {}
    for dia, label in LOOPS:
        print(f"\n{'=' * 78}\n== diagram {dia}: {label}", flush=True)
        nodes, _ = g.net_map(WORK, diagram_index=dia, max_nodes=140, max_terms=20)
        rows = []
        for i, (uid, lbl, terms) in nodes.items():
            names = [nm for _, nm, _ in terms if nm]
            kind = "SubVI" if uid in subs else structs.get(uid, "primitive/other")
            hits = sorted({tag for tag, keys in FLAGS.items() for nm in names if any(k in nm.lower() for k in keys)})
            rows.append({"uid": uid, "kind": kind, "label": lbl, "terms": names, "flags": hits})
        out[str(dia)] = rows
        for r in sorted(rows, key=lambda r: (r["kind"] != "SubVI", r["uid"])):
            flag = ("   [" + ", ".join(r["flags"]) + "]") if r["flags"] else ""
            print(f"   {r['kind']:<14} uid {r['uid']:<6} {r['terms'][:12]}{flag}", flush=True)
        n_sub = len([r for r in rows if r["kind"] == "SubVI"])
        tally = {}
        for r in rows:
            for f in r["flags"]:
                tally[f] = tally.get(f, 0) + 1
        print(f"   -- {len(rows)} nodes, {n_sub} subVI calls, flags {tally}", flush=True)
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    print("\nwritten to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
