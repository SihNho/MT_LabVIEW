"""find_scheduler2.py - second attempt at locating the cycle-schedule consumer.

Attempt 1 ranked diagrams by Index Array density and landed on diagrams 160-165, which turned out to be bead selection
and cross-hair drawing - the largest 2-D array user in the VI, but not the scheduler. The negative result narrowed
things: `CycleSchedule` reads back as ((0.0,),(0.0,),(0.0,)), i.e. **one column**, and the user confirmed the layout is
rows = items (speed / force / wait / rotor) and columns = cycles, resized by the Event Structure.

So this attempt uses a different key: the indicators the scheduler DRIVES. A node that computes `SubCycle`,
`Total cycle #`, `Cycle Start Time`, `Estimated end time (min)`, `Mag Arr` or `Force Arr` is either the consumer or
sits next to it. ControlTerminal objects carry the front-panel label, so they can be placed by the same UID-lookup
method that mapped the Property nodes in 107 s.

READ-ONLY. No hardware.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
TREE = os.path.join(HERE, "diagram_tree_main.json")
WANT = ("subcycle", "total cycle", "cycle start", "estimated end", "mag arr", "force arr",
        "cycleschedule", "numcol", "set # of cycles", "start cycles", "mag position")


def main():
    g._lv = None
    tree = json.load(open(TREE, encoding="utf-8"))["diagrams"]
    where = {}
    for dia, info in tree.items():
        for uid in info["uids"]:
            where.setdefault(int(uid), int(dia))

    # ControlTerminal = a front-panel object's terminal ON the diagram; its label identifies which control it is.
    terms = g.report(WORK, "ControlTerminal")
    print(f"{len(terms)} ControlTerminal objects", flush=True)
    labs = {lbl.lower(): (uid, lbl) for uid, lbl, ind in g.fp_labels(WORK, max_n=400)}
    print(f"{len(labs)} front-panel labels\n", flush=True)

    # match by position: a ControlTerminal has no label of its own in report(), so pair it with the diagram it sits on
    hits = {}
    for t in terms:
        d = where.get(t["uid"])
        hits.setdefault(d, []).append(t["uid"])
    print("ControlTerminals per diagram (top 15):", flush=True)
    for d, us in sorted(hits.items(), key=lambda kv: -len(kv[1]))[:15]:
        owner = tree[str(d)]["owner"] if d is not None and str(d) in tree else "?"
        print(f"   diagram {str(d):<6} {len(us):>3} terminals   owner {owner}", flush=True)

    print("\nscheduler-ish front-panel labels present in the VI:", flush=True)
    for low, (uid, lbl) in sorted(labs.items()):
        if any(k in low for k in WANT):
            print(f"   uid {uid:<7} {lbl!r}   (diagram {where.get(uid)})", flush=True)
    json.dump({"per_diagram": {str(k): v for k, v in hits.items()}},
              open(os.path.join(HERE, "controlterminal_map.json"), "w", encoding="utf-8"), indent=1)
    print("\nwritten", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
