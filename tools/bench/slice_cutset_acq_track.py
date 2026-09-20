r"""slice_cutset_acq_track.py - the cut set of the ACQUISITION+TRACKING slice of the frame loop. OFFLINE.

WHY THIS EXISTS. On 2026-09-15 `boundary_manifest.py 43` was run to decide whether the acquisition/tracking hot
path can be replaced in place inside a copy of the original. A peer refuted the reading
(`archive/peer/2026-09-15-frameloop-seam-77-crossings.md`), on two grounds that both hold:

  * it audited ALL 75 nodes of diagram 43, so it could not say anything about a SMALLER slice - and the frame
    loop's other occupants (the ASI focus subVI #48, the Event Structure #10153) are not in the kernel's slices;
  * its `to_invisible_object` count (77) is `len(net) == 1` - "only one end of this wire was visible to the node
    walk". It never resolves the other end, so it conflates a real loop-border tunnel with a constant or a
    front-panel terminal. 77 is not 77 crossings, and `leaves_the_seam` was 0 by construction because the seam
    was every uid in the diagram.

So this computes the thing that was actually asked, from data already on disk (no LabVIEW, no hardware):
given the measured slice around the kernel, WHICH NETS connect it to the rest of the frame loop, and which run
off to the loop border?

THE SLICE is not chosen by me: it is the backward slice (7 nodes), the forward slice (14) and the two subVIs at
its centre, exactly as `docs/frame-loop-wire-graph.md` measured them on 2026-09-14 from the same JSON.

  py tools/bench/slice_cutset_acq_track.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TERMS = os.path.join(HERE, "main_vi_nodeterms.json")
LABELS = os.path.join(HERE, "main_vi_node_labels.json")
DIAGRAM = "43"

KERNEL = [5058, 6810]                                             # the two subVIs being replaced
BACKWARD = [5540, 6810, 9647, 10247, 10445, 10950, 17289]         # docs/frame-loop-wire-graph.md
FORWARD = [376, 1359, 2222, 2626, 6104, 8885, 9833, 10407,
           10757, 10969, 11261, 11639, 12589, 29874]
SLICE = set(KERNEL) | set(BACKWARD) | set(FORWARD)

# The two occupants of diagram 43 the peer said are NOT in the slice. Asserted, not assumed.
MUST_BE_OUTSIDE = {48: "ASI_adjust focus-subvi.vi", 10153: "EventStructure"}


def label_of(labels, uid):
    v = labels.get(str(uid)) if isinstance(labels, dict) else None
    if isinstance(v, dict):
        return v.get("label") or v.get("name") or ""
    return v or ""


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    terms = json.load(open(TERMS, encoding="utf-8"))
    try:
        labels = json.load(open(LABELS, encoding="utf-8"))
    except Exception:
        labels = {}
    dia = terms["diagrams"][DIAGRAM]
    nodes = dia["nodes"]
    all_uids = {n["uid"] for n in nodes}

    print(f"diagram {DIAGRAM} ({dia.get('owner')}): {len(nodes)} nodes; slice = {len(SLICE)} nodes")
    missing = SLICE - all_uids
    print(f"  slice uids not found in the diagram: {sorted(missing) if missing else 'none'}")
    for uid, what in MUST_BE_OUTSIDE.items():
        where = "INSIDE THE SLICE" if uid in SLICE else ("in the diagram, outside the slice" if uid in all_uids
                                                         else "not in this diagram at all")
        print(f"  #{uid} {what}: {where}")

    # net -> [(uid, terminal name, is_source)]
    nets = {}
    for n in nodes:
        for t in n.get("terms", []):
            w = t.get("wire")
            if not w:
                continue
            nets.setdefault(w, []).append((n["uid"], t.get("name", ""), bool(t.get("is_source"))))

    internal, crossing, to_border, elsewhere = [], [], [], []
    for w, mem in nets.items():
        on = {u for u, _, _ in mem}
        if not (on & SLICE):
            elsewhere.append(w)
        elif on <= SLICE:
            (to_border if len(mem) == 1 else internal).append((w, mem))
        else:
            crossing.append((w, mem))

    print(f"\nnets touching the slice: {len(internal) + len(crossing) + len(to_border)}"
          f"   (diagram has {len(nets)} nets in total)")
    print(f"  INTERNAL   (both ends inside the slice)            : {len(internal)}")
    print(f"  CROSSING   (slice <-> another node of diagram 43)  : {len(crossing)}   <- the real cut")
    print(f"  TO BORDER  (only end visible is in the slice; the other is a loop tunnel, shift register,\n"
          f"              front-panel terminal or constant - NOT resolved here)   : {len(to_border)}")

    print("\n--- CROSSING nets, resolved: which node outside the slice, on which terminal ---")
    for w, mem in sorted(crossing, key=lambda x: x[0]):
        ins = [(u, t) for u, t, s in mem if u in SLICE]
        outs = [(u, t) for u, t, s in mem if u not in SLICE]
        i_txt = "; ".join(f"#{u}.{t or '(unnamed)'}" for u, t in ins)
        o_txt = "; ".join(f"#{u} {label_of(labels, u)}.{t or '(unnamed)'}".strip() for u, t in outs)
        print(f"  wire {w:6}  slice[{i_txt}]  <->  outside[{o_txt}]")

    print("\n--- TO BORDER nets (these become tunnels / shift registers of whatever loop owns the slice) ---")
    for w, mem in sorted(to_border, key=lambda x: x[0]):
        u, t, s = mem[0]
        print(f"  wire {w:6}  #{u}.{t or '(unnamed)'}  ({'source' if s else 'sink'})")

    print(f"\nSUMMARY: the acquisition+tracking slice is {len(SLICE)} of {len(nodes)} nodes. Lifting it out of the "
          f"frame loop cuts {len(crossing)} net(s) to sibling nodes and carries {len(to_border)} net(s) that "
          f"already run to the loop border.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
