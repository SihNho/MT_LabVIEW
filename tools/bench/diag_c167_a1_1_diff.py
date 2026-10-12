# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-1.json
# ---
r"""diag_c167_a1_1_diff - card 167-a1-1 step 5 (OFFLINE, stored json only): the wires Remove Bad Wires deleted.

Inputs: graph BEFORE tools/bench/graph_ring_p5s02e_20261012_173009.json (7815af09, P5 final 75773b0d), graph AFTER = argv[1]
(tools/bench/graph_ring_p6rbw_<stamp>.json written by diag_c167_a1_1_rbw.py), the 22 termless 'not connected' uids of
tools/bench/p6_facts.json rows.F1 (class notconnected; gate F1c of p6_facts.md:14).
Found before writing (CALLED, not copied): vigraph.dedupe_rows (duplicate Diagram-owned terminal rows, vigraph.py:260) and
allterms.join_wires (one row per wire from the terminal table + the termless Wire objects, allterms.py:106: n_src / n_sink).
Wire set of a graph = its objs of class 'Wire' (a termless wire has no terminal row, only the object).
Deleted = wire uids BEFORE minus AFTER; new = AFTER minus BEFORE. Tag per deleted wire: 'data-carrying' iff it had >= 1 source
AND >= 1 sink terminal BEFORE, else 'not data-carrying'. Writes tools/bench/p6_rbw_deleted.json + .md.
PREDICTION (PD404(d)): the 22 termless wires are among the deleted; the number of data-carrying deleted wires is UNPREDICTED.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c167_a1_1_diff.log -- py -u tools/bench/diag_c167_a1_1_diff.py <after graph>"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)   # noqa: E702
import protocol                                                                              # noqa: E402
import vigraph as V                                                                          # noqa: E402
import allterms as A                                                                         # noqa: E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402

BEFORE = os.path.join(HERE, "graph_ring_p5s02e_20261012_173009.json")
AFTER = os.path.join(ROOT, sys.argv[1]) if len(sys.argv) > 1 else None
gate = L.Gate(fatal_default=False)


def load(p):
    gr = json.load(open(p, encoding="utf-8"))
    rows, rec = V.dedupe_rows(gr["terminals"])
    wobj = sorted(int(o["uid"]) for o in gr["objs"] if o["class"] == "Wire")
    wires = dict((int(w["wire_uid"]), w) for w in A.join_wires(rows, wobj))
    by_wire = {}
    for r in rows:
        if r.get("wire_uid"):
            by_wire.setdefault(int(r["wire_uid"]), []).append(r)
    return gr, rows, rec, set(wobj), wires, by_wire


def ends(rs):
    return [{"owner_uid": r.get("owner_uid"), "owner_class": r.get("owner_class"), "term_uid": r.get("term_uid"),
             "term_name": r.get("term_name"), "term_class": r.get("term_class"), "end": "source" if r.get("is_source") else "sink"}
            for r in sorted(rs, key=lambda r: (not r.get("is_source"), r.get("owner_uid") or 0, r.get("term_uid") or 0))]


gate("I0 before graph is 7815af09", L.md5(BEFORE).startswith("7815af09"), L.md5(BEFORE))
gate("I1 after graph given and present", bool(AFTER) and os.path.exists(AFTER), AFTER)
facts = json.load(open(os.path.join(HERE, "p6_facts.json"), encoding="utf-8"))
TERMLESS = sorted(int(r["uid"]) for r in facts["rows"]["F1"] if r.get("class") == "notconnected")
gate("I2 22 termless F1 uids", len(TERMLESS) == 22, TERMLESS)
gb, rb, recb, wb, jb, byb = load(BEFORE)
ga, ra, reca, wa, ja, bya = load(AFTER)
w_tl_b = sorted(u for u, w in jb.items() if w["termless"])
gate("I3 the 22 F1 uids are the termless Wire objects of the before graph", set(TERMLESS) == set(w_tl_b), {"termless_before": w_tl_b})
deleted, new = sorted(wb - wa), sorted(wa - wb)
D = []
for u in deleted:
    w = jb[u]
    dc = w["n_src"] >= 1 and w["n_sink"] >= 1
    D.append({"wire_uid": u, "tag": "data-carrying" if dc else "not data-carrying", "n_src": w["n_src"], "n_sink": w["n_sink"],
              "termless": w["termless"], "f1_termless": u in TERMLESS, "terminals_before": ends(byb.get(u, []))})
N = [{"wire_uid": u, "n_src": ja[u]["n_src"], "n_sink": ja[u]["n_sink"], "termless": ja[u]["termless"],
      "terminals_after": ends(bya.get(u, []))} for u in new]
# a terminal that LOST its wire: term uid wired before (wire deleted) - read after (its row, wire 0 or another wire)
ta = dict((int(r["term_uid"]), r) for r in ra)
for d in D:
    for t in d["terminals_before"]:
        r = ta.get(int(t["term_uid"]))
        t["after"] = None if r is None else {"wire_uid": r.get("wire_uid"), "owner_uid": r.get("owner_uid")}
tl = dict((u, "deleted" if u in deleted else "kept") for u in TERMLESS)
nd = sum(1 for d in D if d["tag"] == "data-carrying")
shape = {}
for d in D:
    k = "termless" if d["termless"] else ("src+sink" if d["n_src"] and d["n_sink"] else ("source-only" if d["n_src"] else "sink-only"))
    shape[k] = shape.get(k, 0) + 1
S = {"schema": "p6-rbw-deleted/1", "card": "167-a1-1", "before": {"path": os.path.relpath(BEFORE, ROOT), "md5": L.md5(BEFORE)},
     "after": {"path": os.path.relpath(AFTER, ROOT), "md5": L.md5(AFTER)},
     "method": "Wire objs before - after; ends from vigraph.dedupe_rows + allterms.join_wires of the BEFORE graph",
     "counts": {"wires_before": len(wb), "wires_after": len(wa), "deleted": len(D), "deleted_data_carrying": nd,
                "deleted_not_data_carrying": len(D) - nd, "deleted_by_shape": shape, "new": len(N),
                "termless22_deleted": sum(1 for v in tl.values() if v == "deleted"), "termless22_kept": sum(1 for v in tl.values() if v == "kept"),
                "dedupe_before": recb["dropped"], "dedupe_after": reca["dropped"]},
     "termless22": tl, "deleted": D, "new": N}
jp = os.path.join(HERE, "p6_rbw_deleted.json")
json.dump(S, open(jp, "w", encoding="utf-8"), indent=1)
md = ["---", "type: facts", "status: current", "date: 2026-10-12", "card: 167-a1-1", "---",
      "# P6-0 (d): wires deleted by ONE VI-level Remove Bad Wires on a scratch copy of 75773b0d (facts only)",
      "Written by `tools/bench/diag_c167_a1_1_diff.py` from `{0}` ({1}) minus `{2}` ({3}). Machine-readable: `tools/bench/p6_rbw_deleted.json`.".format(
          S["before"]["path"], S["before"]["md5"][:8], S["after"]["path"], S["after"]["md5"][:8]),
      "", "Counts: `{0}`".format(json.dumps(S["counts"])), "",
      "22 termless F1 uids: " + ", ".join("{0} {1}".format(u, v) for u, v in sorted(tl.items())), "",
      "| wire | tag | shape (src/sink) | F1 termless | terminals before (owner #uid class : term #uid 'name' end) |", "|---|---|---|---|---|"]
for d in D:
    md.append("| {0} | {1} | {2}/{3} | {4} | {5} |".format(d["wire_uid"], d["tag"], d["n_src"], d["n_sink"], "yes" if d["f1_termless"] else "no",
              "; ".join("#{0} {1} : t{2} '{3}' {4}".format(t["owner_uid"], t["owner_class"], t["term_uid"], t["term_name"], t["end"])
                        for t in d["terminals_before"]) or "(no terminal)"))
md += ["", "New wire uids after RBW (not in the before graph): {0}".format(len(N))]
for n in N:
    md.append("- {0}: {1}/{2} {3}".format(n["wire_uid"], n["n_src"], n["n_sink"], "; ".join("#{0} {1} : t{2} '{3}' {4}".format(
        t["owner_uid"], t["owner_class"], t["term_uid"], t["term_name"], t["end"]) for t in n["terminals_after"])))
mp = os.path.join(HERE, "p6_rbw_deleted.md")
open(mp, "w", encoding="utf-8").write("\n".join(md) + "\n")
print("FACT counts {0}".format(json.dumps(S["counts"])), flush=True)
print("FACT termless22 deleted {0} kept {1}: kept {2}".format(S["counts"]["termless22_deleted"], S["counts"]["termless22_kept"],
                                                               [u for u, v in tl.items() if v == "kept"]), flush=True)
print("FACT data-carrying deleted: {0}".format([d["wire_uid"] for d in D if d["tag"] == "data-carrying"]), flush=True)
print("FACT WROTE {0} md5 {1}; {2} md5 {3}".format(jp, L.md5(jp), mp, L.md5(mp)), flush=True)
gate("P1 (prediction PD404(d)) the 22 termless F1 wires are all deleted", S["counts"]["termless22_kept"] == 0,
     [u for u, v in tl.items() if v == "kept"])
sys.exit(gate.result([{"path": protocol._rel(jp), "md5": L.md5(jp)}, {"path": protocol._rel(mp), "md5": L.md5(mp)}]))
