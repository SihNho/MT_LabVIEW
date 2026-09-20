"""READ-ONLY: terminals of the three path/string primitives in claudeDev/background VIs_COPY/save N xyz traces.vi
(donor for FramePath.vi). py tools/bgrun.py --max-min 5 --log tools/bench/census_savetraces_terms.log -- py -u tools/bench/census_savetraces_terms.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
P = os.path.join(g.CLAUDEDEV, "background VIs_COPY", "save N xyz traces.vi")
g._lv = None
labels = {r["uid"]: r["label"] for r in g.node_labels(P, 0)}
for n in range(40):
    u, rows = g.node_terms_uid(P, 0, n)
    if not u: break
    if labels.get(u) in ("Path To String", "Format Into String", "String To Path", "Build Path", "Strip Path"):
        print(f"n{n} uid {u} {labels[u]!r}: {[(r['i'], r['name'], 'S' if r['is_source'] else 's', r['wire']) for r in rows]}", flush=True)
print("controls:", [(l, ind) for _i, l, ind in g.fp_labels(P)], flush=True)
