"""READ-ONLY: every 'Format Into String' instance in the small lab VIs (claudeDev/background VIs_COPY, top-level
diagram) with its argument-terminal count - the FramePath donor must have exactly ONE argument ('input 1') so the
safe form is initial string <- base, format '\img%05d.tif', argument = index (peer ...-revised-forloop-route).
  py tools/bgrun.py --max-min 8 --log tools/bench/census_fis_donors.log -- py -u tools/bench/census_fis_donors.py"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
BG = os.path.join(g.CLAUDEDEV, "background VIs_COPY")
g._lv = None
for f in sorted(os.listdir(BG)):
    p = os.path.join(BG, f)
    if not f.lower().endswith(".vi") or os.path.getsize(p) > 120_000:
        continue
    try:
        labels = {r["uid"]: r["label"] for r in g.node_labels(p, 0)}
    except Exception:
        continue
    if "Format Into String" not in labels.values():
        continue
    for n in range(60):
        u, rows = g.node_terms_uid(p, 0, n)
        if not u: break
        if labels.get(u) == "Format Into String":
            args = [r["name"] for r in rows if r["name"].startswith("input ")]
            print(f"{f}: n{n} uid {u} args={len(args)} {args}  wired={[(r['name'], r['wire']) for r in rows if r['wire']]}", flush=True)
