r"""diag_wiki_probe2 - the FULL row dump of two tiny background VIs, so the wiki graph model is READ from
the machine instead of inferred. Read-only; no VI is run; nothing is created or deleted.

WHY: `diag_wiki_probe` measured that `Traverse('Terminal')` is INCLUSIVE of its subclasses
(21 rows = Terminal 5 + ParameterTerminal 8 + ControlTerminal 4 + OverridableParameterTerminal 4 on
`rect coord from center.vi`), while `read_terms`' `owner_class` column is the OWNER's class, not the
terminal's. So two things are still unknown and both decide the graph:
  Q1 what LEAF class each terminal row has (join term_uid against the GObject census), and
  Q2 what a ControlTerminal's `owner_uid` is - itself, or the Diagram. If it is the Diagram, every
     front-panel terminal collapses into ONE graph node and node-level reachability is worthless, so
     `vigraph` must key those rows on term_uid instead.
FACT-ONLY: no prediction is asserted here, so there is nothing to fail; the dump is the answer.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import allterms as A                                                               # noqa: E402

BG = os.path.join(g.CLAUDEDEV, "background VIs_COPY")
OUT = os.path.join(HERE, "diag_wiki_probe2.json")
REC = {}

for name in ("rect coord from center.vi", "build cal image.vi"):
    p = os.path.join(BG, name)
    objs = g.report_all(p, "GObject")
    cls = dict((int(o["uid"]), o["class"]) for o in objs)
    pos = dict((int(o["uid"]), tuple(o["pos"])) for o in objs)
    rows, dt = A.read_terms(p)
    dump = []
    for r in rows:
        dump.append({"term_uid": r["term_uid"], "term_class": cls.get(r["term_uid"], "?"),
                     "name": r["term_name"], "src": r["is_source"], "wire": r["wire_uid"],
                     "owner_uid": r["owner_uid"], "owner_class": r["owner_class"],
                     "owner_leaf": cls.get(r["owner_uid"], "?")})
    REC[name] = {"seconds": round(dt, 2), "objects": [(int(o["uid"]), o["class"], tuple(o["pos"]),
                                                       o["owner"]) for o in objs], "terminals": dump}
    print("\n---------- [{0}]  {1} objects / {2} terminal rows / {3:.2f}s".format(
        name, len(objs), len(rows), dt), flush=True)
    print("  FACT  GObject census: {0}".format(
        json.dumps([(o["class"], int(o["uid"]), tuple(o["pos"])) for o in objs])), flush=True)
    for d in dump:
        print("  FACT  t#{term_uid:<6} {term_class:<28} name={name!r:<34} src={src!s:<5} "
              "wire={wire:<6} owner=#{owner_uid} {owner_leaf}".format(**d), flush=True)

with open(OUT, "w", encoding="utf-8") as f:
    json.dump(REC, f, indent=1)
print("\n  FACT  wrote {0}".format(OUT), flush=True)
print("=== GATES: 0 pass / 0 fail (fact-only dump)", flush=True)
