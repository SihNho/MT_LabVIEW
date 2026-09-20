"""find_scheduler3.py - find the cycle-schedule consumer by the NAME its front-panel terminal carries.

Two attempts have failed, and each narrowed the search:

  1. Ranking diagrams by Index Array density landed on 160-165, which turned out to be bead selection and cross-hair
     drawing - the VI's largest 2-D array user, not the scheduler.
  2. Cross-referencing `fp_labels` UIDs against the diagram tree does not work: a front-panel object's UID and the UID
     of its terminal ON the diagram are different objects.

What does work was noticed while reading diagram 19 for the globals: a terminal-like node reports **its own name as a
terminal name**. `node[5] uid 6951 ['Rot position']` is the global `Rot position`; nothing else on that node. So a
front-panel terminal for `CycleSchedule` should appear the same way - a node whose only terminal is named
`CycleSchedule`.

That turns the search into a name match instead of a heuristic. The diagram holding that terminal is where the schedule
enters the code, and since the VI has only 8 locals (none of them on the frame loop), the terminal is where it is read.

Cost control: net_map is ~8 s per node, so the diagram list is taken from the ControlTerminal map rather than walked
blindly, cheapest-first.

READ-ONLY. No hardware.
  py tools/bgrun.py --max-min 30 --log tools/bench/find_scheduler3.log -- py -u tools/bench/find_scheduler3.py [dia,dia,...]
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
TREE = os.path.join(HERE, "diagram_tree_main.json")
CTMAP = os.path.join(HERE, "controlterminal_map.json")
OUT = os.path.join(HERE, "scheduler_located.json")
# the names that identify the scheduler where it touches the diagram
NAMES = ("cycleschedule", "numcol", "subcycle", "total cycle", "cycle start", "estimated end",
         "set # of cycles", "start cycles", "mag arr", "force arr", "mag position")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    tree = json.load(open(TREE, encoding="utf-8"))["diagrams"]

    if len(sys.argv) > 1:
        dias = [int(x) for x in sys.argv[1].split(",")]
    elif os.path.exists(CTMAP):
        per = json.load(open(CTMAP, encoding="utf-8"))["per_diagram"]
        dias = [int(d) for d, us in sorted(per.items(), key=lambda kv: -len(kv[1])) if d != "null"]
        print(f"diagrams holding front-panel terminals, richest first: {dias[:20]}", flush=True)
    else:
        print("no ControlTerminal map yet - pass a diagram list", flush=True)
        return 2

    # cheapest first among the candidates, so a hit is likely found before the expensive diagrams
    dias.sort(key=lambda d: len(tree[str(d)]["uids"]) if str(d) in tree else 999)
    found = []
    for d in dias:
        n_nodes = len(tree[str(d)]["uids"]) if str(d) in tree else "?"
        try:
            nodes, _ = g.net_map(WORK, diagram_index=d, max_nodes=100, max_terms=24)
        except Exception as e:
            print(f"diagram {d}: FAILED {str(e)[:90]}", flush=True)
            continue
        hits = []
        for i, (uid, lbl, terms) in nodes.items():
            names = [nm for _, nm, _ in terms if nm]
            low = " | ".join(names).lower()
            if any(k in low for k in NAMES):
                hits.append({"uid": uid, "terms": names})
        if hits:
            owner = tree[str(d)]["owner"] if str(d) in tree else "?"
            print(f"\n*** diagram {d} ({n_nodes} nodes, owner {owner}): {len(hits)} scheduler-named nodes", flush=True)
            for h in hits:
                print(f"      uid {h['uid']:<7} {h['terms'][:14]}", flush=True)
            found.append({"diagram": d, "owner": owner, "hits": hits})
            json.dump(found, open(OUT, "w", encoding="utf-8"), indent=1)
        else:
            print(f"diagram {d:<5} ({n_nodes} nodes): no scheduler name", flush=True)

    print(f"\n{'=' * 70}\nDIAGRAMS NAMING THE SCHEDULE: {[f['diagram'] for f in found]}", flush=True)
    print("written to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
