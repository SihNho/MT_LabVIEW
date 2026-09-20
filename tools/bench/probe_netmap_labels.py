"""probe_netmap_labels.py - does net_map already return subVI NAMES per diagram?

If it does, `OpReportNodes_v0` is unnecessary and three failed build attempts can be abandoned rather than
debugged. That is worth one cheap probe before any more tool-building: the last three builds each ended at
ExecState 0 for a different reason, and the peer gate now (correctly) blocks another attempt until the failure
has been reviewed.

WHY IT MIGHT ALREADY WORK. `net_map` returns `(uid, label, terminals)` per node. Every label seen so far has
been `''` - but every node seen so far was a **primitive or property node**, which genuinely has no label. A
subVI's label defaults to its VI name, so the field should be populated for exactly the nodes the inventory
needs. `node_info` already proved the principle on a top-level diagram:

    (1, 'Unknown', 'Traverse for GObjects.vi')     <- Style 'Unknown', LABEL = the VI name

and `node_info` is top-level only, which is why it cannot serve the main VI's ~170 diagrams. `net_map` takes a
diagram index.

METHOD: list the main VI's diagrams, then net_map the first few that actually contain nodes, and report how many
carry a non-empty label. READ-ONLY.

  py tools/bench/probe_netmap_labels.py
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
        r"\Min_Track N beads V6_ParallelLoop.vi")
g._run.__defaults__ = (6.0, 300.0)


def main():
    g._lv = None
    t0 = time.time()
    dias = g.report_all(MAIN, "Diagram")
    print(f"{len(dias)} diagrams in {time.time() - t0:.1f} s (report_all)", flush=True)
    owners = {}
    for d in dias:
        owners[d["owner"]] = owners.get(d["owner"], 0) + 1
    print("diagram owners:", owners, flush=True)

    checked = 0
    total_nodes = 0
    labelled = 0
    for i, d in enumerate(dias):
        if checked >= 12:
            break
        try:
            nodes, _w = g.net_map(MAIN, i, max_nodes=60, max_terms=4)
        except Exception as e:
            print(f"  diagram {i:3d}: EXC {str(e)[:100]}", flush=True)
            continue
        if not nodes:
            continue
        checked += 1
        named = [(uid, lbl) for _k, (uid, lbl, _t) in nodes.items() if lbl]
        total_nodes += len(nodes)
        labelled += len(named)
        print(f"  diagram {i:3d} (owner {d['owner']}): {len(nodes):3d} nodes, "
              f"{len(named):3d} labelled", flush=True)
        for uid, lbl in named[:8]:
            print(f"        uid={uid:<6} {lbl!r}", flush=True)

    print(f"\n{checked} non-empty diagrams sampled: {total_nodes} nodes, {labelled} with a label", flush=True)
    print("VERDICT:", "net_map gives names - OpReportNodes_v0 NOT needed" if labelled else
          "no labels - the style/label reader really is required", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
