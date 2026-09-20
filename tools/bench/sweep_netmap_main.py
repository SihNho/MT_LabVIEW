"""sweep_netmap_main.py - net_map EVERY diagram of the main VI once, and cache it.

THE INSIGHT THAT UNBLOCKS THE DOCUMENTATION. I had concluded the inventory was blocked on reading node LABELS
per diagram, and spent three failed builds plus three failed probes chasing that. It is not blocked:

    **net_map already returns each node's TERMINAL NAMES, and terminal names identify a subVI.**

A node carrying `Baseline Startpoint`, `Pos_degree` and `Ring` IS the Autonics `SetCommand.vi` call - no label
needed. That is exactly how nodes were identified inside the driver VI itself; I simply never turned the trick on
the main VI. Everything the remaining documents need is a terminal-name search:

    rotor call sites     `Baseline Startpoint`, `Pos_degree`, `Ring`, `Numeric`
    shared-state access  `Trans position`, `Rot position`, `Focus position`
    camera config        `Width`, `Height`, IMAQdx attribute names
    stage / motor        `Move Axis to Position`-style terminals, `MOV`/`VEL`/`GOH` inputs

COST, measured rather than estimated: 12 diagrams took 312 s, so ~26 s each and **~74 min for all 170**. That is
why this is a one-shot cached sweep run unattended, not something called repeatedly. Output is JSON so every
later question is answered by grepping the cache instead of re-reading LabVIEW.

The sweep writes INCREMENTALLY, after every diagram. If it is killed by its deadline, whatever completed is
still usable and the log says exactly how far it got - a half-finished sweep is partial data, not a lost run.

READ-ONLY on the main VI working copy: traversal only, never opened as a window, never saved.

  py tools/bgrun.py --max-min 95 --log tools/bench/sweep_netmap_main.log -- py -u tools/bench/sweep_netmap_main.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
        r"\Min_Track N beads V6_ParallelLoop.vi")
OUT = os.path.join(HERE, "main_vi_netmap.json")
g._run.__defaults__ = (6.0, 300.0)


def main():
    g._lv = None
    t0 = time.time()
    dias = g.report_all(MAIN, "Diagram")
    print(f"{len(dias)} diagrams listed in {time.time() - t0:.1f} s", flush=True)

    cache = {"source": MAIN, "started": time.strftime("%Y-%m-%d %H:%M:%S"),
             "diagram_owners": [d["owner"] for d in dias], "diagrams": {}}
    done = 0
    for i, d in enumerate(dias):
        t1 = time.time()
        try:
            nodes, wires = g.net_map(MAIN, i, max_nodes=200, max_terms=40)
        except Exception as e:
            print(f"  [{i:3d}/{len(dias)}] owner={d['owner']:<18} EXC {str(e)[:90]}", flush=True)
            cache["diagrams"][str(i)] = {"owner": d["owner"], "error": str(e)[:200]}
            continue
        # net_map's node map is {index: (uid, label, [(ti, name, wire), ...])}; keep it JSON-shaped.
        rec = {"owner": d["owner"], "nodes": {}}
        for _k, (uid, lbl, terms) in nodes.items():
            rec["nodes"][str(uid)] = {"label": lbl,
                                      "terms": [[t, w] for _ti, t, w in terms if t]}
        rec["wires"] = {str(w): v for w, v in (wires or {}).items()}
        cache["diagrams"][str(i)] = rec
        done += 1
        print(f"  [{i:3d}/{len(dias)}] owner={d['owner']:<18} {len(nodes):3d} nodes  "
              f"{time.time() - t1:5.1f}s", flush=True)

        # Write after EVERY diagram: a deadline kill then costs one diagram, not the whole sweep.
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)

    cache["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    cache["complete"] = done == len(dias)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False)
    print(f"\n{done}/{len(dias)} diagrams cached in {(time.time() - t0)/60:.1f} min -> {OUT}", flush=True)
    print("complete:", cache["complete"], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
