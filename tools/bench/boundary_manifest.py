"""boundary_manifest.py - the pre-cut audit for ONE candidate subVI seam.

Peer review (archive/peer/2026-09-12-restructure-plan-4.6-attack.md) refused the claim that extracting a region into a
subVI preserves behaviour "by construction", and named exactly what crosses a boundary by routes other than a wire:

  * a **local variable** inside the selection becomes a control reference + a `Value` property node in the child -
    which would manufacture the UI-thread access this whole restructuring exists to remove;
  * a **control reference** stays reference-based UI work, not dataflow;
  * **error-cluster ordering** only exists along the chain actually wired;
  * a **non-reentrant** extracted subVI serialises concurrent callers, a reentrant one duplicates internal state;
  * **uninitialised shift registers, feedback nodes, First Call?, static VI refs, event registrations** carry state;
  * an extracted **Event Structure** is the worst case - a latch-action Boolean read through a property node never
    resets mechanically;
  * NI's **CAR 571520**: a polymorphic VI selector inside the selection can break unrelated wires.

So no seam is cut until this manifest is written for it. The rule adopted in docs/restructure-plan-4.6.md is that the
hazard is a property of WHERE the seam is drawn, so the manifest is what chooses the cut rather than merely describing
it.

CANDIDATE SEAM: the bead-selection / cross-hair cluster, diagrams 160-163. Chosen first because it has the clearest
existing seam - diagrams 161 and 162 already each call the same cross-drawing subVI (uids 24170, 24656) - and because
the whole-VI state sweep found the region's only nearby local (uid 16942) on diagram 99, i.e. OUTSIDE it.

READ-ONLY: reports only; nothing is created, moved or saved. No hardware.
  py tools/bgrun.py --max-min 30 --log tools/bench/boundary_manifest.log -- py -u tools/bench/boundary_manifest.py [dia,dia,...]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
TREE = os.path.join(HERE, "diagram_tree_main.json")
OUT = os.path.join(HERE, "boundary_manifest.json")
SEAM = [int(x) for x in (sys.argv[1].split(",") if len(sys.argv) > 1 else "160,161,162,163".split(","))]
# every class the peer named as a boundary hazard, plus the ones needed to describe the cut
HAZARD = ("Local", "Global", "Property", "Invoke", "FeedbackNode", "EventStructure", "SubVI")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    tree = json.load(open(TREE, encoding="utf-8"))["diagrams"]
    inside = set()
    for d in SEAM:
        inside |= {int(u) for u in tree[str(d)]["uids"]}
    print(f"SEAM = diagrams {SEAM}; {len(inside)} node uids inside\n", flush=True)

    where = {}
    for d, info in tree.items():
        for u in info["uids"]:
            where.setdefault(int(u), int(d))

    man = {"seam": SEAM, "inside_uids": sorted(inside), "hazards": {}}
    for cls in HAZARD:
        try:
            objs = g.report(WORK, cls)
        except Exception as e:
            print(f"{cls:<16} not traversable: {str(e)[:70]}", flush=True)
            continue
        hit = [o for o in objs if o["uid"] in inside]
        man["hazards"][cls] = [{"uid": o["uid"], "diagram": where.get(o["uid"]), "pos": list(o.get("pos") or ())}
                               for o in hit]
        verdict = "CLEAN" if not hit else f"{len(hit)} INSIDE THE SEAM"
        print(f"{cls:<16} {len(objs):>4} in the VI   ->  {verdict}", flush=True)
        for o in hit:
            print(f"      uid {o['uid']:<7} diagram {where.get(o['uid'])}  pos {o.get('pos')}", flush=True)

    # wires that cross the seam become connector terminals; count them, because a pane has a finite pattern
    print("\ncrossing wires (these become the connector pane):", flush=True)
    crossing = {}
    for d in SEAM:
        try:
            nodes, nets = g.net_map(WORK, diagram_index=d, max_nodes=100, max_terms=24)
        except Exception as e:
            print(f"   diagram {d}: net_map FAILED {str(e)[:80]}", flush=True)
            continue
        byu = {i: uid for i, (uid, l, t) in nodes.items()}
        for w, mem in nets.items():
            if not w:
                continue
            uids_on = {byu.get(n) for n, _, _ in mem}
            if len(mem) == 1:
                crossing.setdefault("to_invisible_object", []).append((d, w, [(byu.get(n), nm) for n, _, nm in mem]))
            elif not uids_on <= inside:
                crossing.setdefault("leaves_the_seam", []).append((d, w, [(byu.get(n), nm) for n, _, nm in mem]))
    for k, v in crossing.items():
        print(f"   {k}: {len(v)}", flush=True)
        for d, w, mem in v[:12]:
            print(f"      diagram {d} wire {w}: {mem}", flush=True)
    man["crossing"] = {k: [[d, w, [[u, nm] for u, nm in mem]] for d, w, mem in v] for k, v in crossing.items()}

    json.dump(man, open(OUT, "w", encoding="utf-8"), indent=1)
    clean = all(not v for k, v in man["hazards"].items() if k in ("Local", "Global", "EventStructure", "FeedbackNode"))
    print(f"\n{'=' * 70}", flush=True)
    print(f"SEAM VERDICT: {'no state-carrier hazard inside' if clean else 'HAZARD INSIDE - move the seam'}", flush=True)
    print("written to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
