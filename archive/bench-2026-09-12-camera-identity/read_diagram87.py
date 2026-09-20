"""read_diagram87.py - the camera configuration step, read with its WIRES.

Diagram 87 is the configuration step the user pointed at ("코드 시작부분이 configuration step이잖아"). The targeted
scan found three camera nodes on it, and one of them is the node the whole halving question turns on:

    uid 9775  terminals in order: ['IMAQdx Session', 'IMAQdx Session', 'error in (no error)', 'error out',
                                   'Height', 'Width']

An IMAQdx property node. Terminal order **Height then Width**, which matches the order the two strings appear in the
VI file (`Height&2` before `Width&2`) - so the byte scan and the COM read agree, and the node is real rather than an
artefact of string adjacency, which a peer review had rightly said the byte evidence could not establish on its own.

What terminal NAMES cannot tell us is the one thing that decides everything: **is this node reading the camera or
writing it?** A read explains the front-panel indicators `Width`/`Height` (which hold 640 and 512) and means the VI
never sets the ROI. A write means the VI sets it, and then the value on the wire is the answer.

Wires settle it. `net_map` returns nets as {wire uid: [(node, terminal index, terminal name), ...]}, so every terminal
sharing a wire with `Height` or `Width` is listed - a constant or control on the same net means the node is fed
(write); an indicator on the same net means the node feeds it (read).

READ-ONLY: never modifies, never saves, never runs the VI. No hardware.
  py tools/bgrun.py --max-min 20 --log tools/bench/read_diagram87.log -- py -u tools/bench/read_diagram87.py [diagram]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
DIA = int(sys.argv[1]) if len(sys.argv) > 1 else 87
OUT = os.path.join(HERE, f"diagram{DIA}_netmap.json")
TARGET_TERMS = ("height", "width")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    nodes, nets = g.net_map(WORK, diagram_index=DIA, max_nodes=140, max_terms=60)
    print(f"diagram {DIA}: {len(nodes)} nodes, {len(nets)} nets\n", flush=True)

    by_uid = {}
    for n, (uid, lbl, terms) in nodes.items():
        by_uid[n] = uid
        names = [nm for _, nm, _ in terms if nm]
        print(f"   node[{n}] uid {uid:<7} {len(names):>2} terms: {names}", flush=True)

    print(f"\n{'=' * 78}\nNETS TOUCHING A 'Height' OR 'Width' TERMINAL", flush=True)
    shown = 0
    for wire, members in nets.items():
        if wire == 0:                       # 0 means unwired, not a real net
            continue
        if not any(nm and nm.lower() in TARGET_TERMS for _, _, nm in members):
            continue
        shown += 1
        print(f"\n   wire {wire}: {len(members)} terminals on it", flush=True)
        for n, t, nm in members:
            print(f"      node[{n}] uid {by_uid.get(n)} terminal[{t}] {nm!r}", flush=True)
    if not shown:
        print("   NONE - the Height/Width terminals are UNWIRED. A property node with unwired terminals does nothing,\n"
              "   which would mean the camera geometry is neither read nor written here.", flush=True)

    # the unwired case is itself an answer, so record which of the two terminals carry a wire at all
    for n, (uid, lbl, terms) in nodes.items():
        for t, nm, w in terms:
            if nm and nm.lower() in TARGET_TERMS:
                print(f"\n   uid {uid} terminal {nm!r}: wire {w}  ({'wired' if w else 'UNWIRED'})", flush=True)

    json.dump({"nodes": {str(k): [v[0], v[1], [list(x) for x in v[2]]] for k, v in nodes.items()},
               "nets": {str(k): [list(x) for x in v] for k, v in nets.items()}},
              open(OUT, "w", encoding="utf-8"), indent=1)
    print("\nwritten to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
