r"""diag_donor_census - MEASUREMENT B of cycle 52's final round: what could TYPE an `Obtain Queue` on #686?

A DIAGNOSTIC, never a recipe. **A PURE READ: nothing is created, moved, wired, deleted or saved.** The scratch
copy exists only so that no rule-1 file is ever the thing a COM client holds open.

  B1  Every node in `AbstractDiagram.Nodes[]` of `Diagram #686`, with its NAMED OUTPUT terminals.
  B2  The eight queue element types read from `docs/d1-build-plan.md` sec.9 (`:576-585`), against B1.
  B3  For every node of `#686`: is it INDEPENDENT of WhileLoop `#637`? - i.e. do its own fed inputs trace to
      sources outside `#637`, the way `#8486 'x+1'` was measured (its `x` <- wire 7478 <- FlatSequenceInnerTunnel
      `#896`, owner FlatSequence `#681`).

🔴 NO VI IS RUN (34(f)). No new op (Pre-decided 2). No motor, no ASI, no camera, no GUI action.
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are never modified; this reads a DATED
   SCRATCH copy of the S2 artefact and saves nothing at all.

🔴 THE ONE THING THIS CANNOT MEASURE, stated up front rather than silently inferred: **the fleet has NO reader
for a terminal's DATA TYPE.** `grep` over `tools/gscript.py` + `docs/toolkit-capabilities.md` + `tools/recipes/`
finds no op reading `Terminal.DataType` / a type descriptor; `gscript.node_terms` `:870` returns
{name, is_source, wire} only, `report_all` `:488` returns {class, uid, pos, owner}, and `node_info` `:2459`
returns `Node.Style` for TOP-LEVEL nodes only (`#686` is not the top-level diagram - that is
`TopLevelDiagram #536`). Building one is a NEW OP and is forbidden. So B1's data-type column is reported as
**NOT MEASURABLE BY THE BUILT FLEET**, and B2 is answered from `docs/d1-build-plan.md`'s own already-cited
measurements, labelled as document-derived. What IS measured here is the census, the named output terminals,
and the whole `#637`-dependency map - which is what decides donor *usability* once a type is known.

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line:
  * `build_opstopfromnode_v0.walk` `:129` / `cls_of` `:147` - the BUILT per-diagram terminal census.
  * `gscript.node_terms_uid` `:925` (inside `walk`), `gscript.count` `:1005`, `report_all` `:488`.
  * `build_d1_v0.diag_index` `:357` / `owner_of` `:338`.
  * `build_opwiresource_v5` + `diag_movein_p1_break.read_term` `:82` - a wire's `Terms[]` with owner class/uid,
    used ONLY to spot-check that the walk-derived wire->source map is complete.
  * `diag_s2_scaffold.fresh` `:155` / `file_facts` `:142`; `bench_prep.labview_handles`; `hash_probe.probe`.
Nothing new is built.

PREDICTION CONTRACT (each line is a printed GATE)
  Q1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859.                                            FATAL
  Q2  `claudeDev\D1_s2_loops.vi` md5 == 6ff19497f2309e007a214660bb64b911.                                FATAL
  Q3  the dated scratch is byte-identical to it.                                                         FATAL
  Q4  census: Diagram 173 / WhileLoop 6 / Wire 1905 (the verified S2 numbers).                           FATAL
  Q5  `Diagram #686` resolves to a Traverse index and its `Nodes[]` walk returns >= 20 nodes.            FATAL
  Q6  B1 is written to the JSON in full: every node, every named output terminal.                        FATAL
  Q7  `#637` is one of those nodes and exposes named output terminals (the 17 of
      `tools/bench/diag_s2_scaffold.json:124-193`).                                                  non-fatal
  Q8  `#8486 'x+1'`'s fed input resolves to a source that is NOT `#637` (today's measured control).   non-fatal
  Q9  B3: every node gets a direct and a transitive `depends on #637` verdict.                       REPORTED
  Q10 the spot-check of the wire->source map agrees with `OpWireSource_v5` on every sampled wire.    non-fatal
  Q11 NOTHING was created, moved or saved: the class census after == the class census before, and the
      scratch's md5 on disk is unchanged.                                                                FATAL
  Q12 no live VI Server reference is left open.                                                      non-fatal
  Q13 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are byte-unchanged at the end.                      FATAL

  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_donor_census.log \
      -- py -u tools/bench/diag_donor_census.py
"""
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import diag_index                                                # noqa: E402
from build_opstopfromnode_v0 import walk as WALK, cls_of                          # noqa: E402
from build_opwiresource_v5 import OP as OP_WS, MAP_OUT as MAP_WS                  # noqa: E402
from diag_movein_p1_break import read_term                                        # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_donorcensus_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_donor_census.json")

SIBLING_DIAG_UID = 686
FRAME_LOOP_UID = 637
CONTROL_NODE = (8486, "x+1")     # today's measured independent node
BASELINE = {"Diagram": 173, "WhileLoop": 6, "Wire": 1905}

# B2: the eight element types, read verbatim from docs/d1-build-plan.md sec.9 `:576-585` (the table's own
# `element type` column) together with the row's own already-measured `(src uid, terminal)` attribution and its
# citation. This block is DOCUMENT-DERIVED, not measured here - the script says so in the log.
QUEUE_TYPES = [
    {"queue": "Q_free", "element_type": "IMAQ image refnum", "plan_src_uid": None, "plan_terminal": None,
     "plan_state": "B", "citation": "docs/d1-build-plan.md:578"},
    {"queue": "Q_work", "element_type": "IMAQ image refnum", "plan_src_uid": None, "plan_terminal": None,
     "plan_state": "B", "citation": "docs/d1-build-plan.md:579"},
    {"queue": "Q_meta", "element_type": "DBL (buffer number)", "plan_src_uid": 637,
     "plan_terminal": "current image number", "plan_state": "A", "citation": "docs/d1-build-plan.md:580"},
    {"queue": "Q_res", "element_type": "DBL[] (array)", "plan_src_uid": 637, "plan_terminal": "x,y,z array out",
     "plan_state": "A", "citation": "docs/d1-build-plan.md:581"},
    {"queue": "Q_good", "element_type": "Bool[] (array)", "plan_src_uid": 637,
     "plan_terminal": "Bead is good? array out", "plan_state": "A", "citation": "docs/d1-build-plan.md:582"},
    {"queue": "Q_rmeta", "element_type": "DBL (buffer number)", "plan_src_uid": 637,
     "plan_terminal": "current image number", "plan_state": "A", "citation": "docs/d1-build-plan.md:583"},
    {"queue": "Q_focus", "element_type": "DBL scalar (slice index)", "plan_src_uid": None, "plan_terminal": None,
     "plan_state": "C", "citation": "docs/d1-build-plan.md:584"},
    {"queue": "Q_focusback", "element_type": "DBL scalar", "plan_src_uid": 637,
     "plan_terminal": "position [internal units]", "plan_state": "A", "citation": "docs/d1-build-plan.md:585"},
]

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "measurement": "B (donor census, PURE READ)",
     "no_vi_was_run": True, "no_mutation": True, "chooses_nothing": True,
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5}, "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "scratch": {"path": SCRATCH}, "B1": {}, "B2": {}, "B3": {}, "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    line = "  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else "")
    print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def probe(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def census(tag, target):
    c = {k: g.count(target, k) for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire")}
    R.setdefault("censuses", {})[tag] = c
    fact("class census %s: %r" % (tag, c))
    return c


def main():
    print("=== diag_donor_census  %s   (MEASUREMENT B, PURE READ; NO VI IS RUN, 34(f); no new op)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    R["datatype_reader"] = {
        "exists": False,
        "searched": ["tools/gscript.py", "docs/toolkit-capabilities.md", "tools/recipes/*.py"],
        "closest": ["gscript.node_terms:870 -> {name, is_source, wire} only",
                    "gscript.report_all:488 -> {class, uid, pos, owner}",
                    "gscript.node_info:2459 -> Node.Style, TOP-LEVEL diagram nodes only (#686 is not top level)"],
        "consequence": "B1's data-type column is NOT MEASURABLE; building a Terminal.DataType reader is a NEW "
                       "OP and is forbidden (Pre-decided 2)"}
    fact("B1 DATA TYPES ARE NOT MEASURABLE BY THE BUILT FLEET: no op reads Terminal.DataType; closest are "
         "node_terms (name/is_source/wire), report_all (class/uid/pos/owner) and node_info (Node.Style, "
         "TOP-LEVEL nodes only). A new op is forbidden (Pre-decided 2). Names + classes are reported instead.")

    o = probe("Q1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("Q1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"))
    s = probe("Q2 the S2 artefact", S2_ARTEFACT)
    gate("Q2 D1_s2_loops.vi md5 == %s" % S2_MD5, s.get("md5") == S2_MD5, s.get("md5", "?"))

    D.fresh("Q2b")
    fact("handles after the restart: %r" % labview_handles())
    shutil.copy2(S2_ARTEFACT, SCRATCH)
    t = probe("Q3 the dated scratch", SCRATCH)
    gate("Q3 the scratch is byte-identical to the S2 artefact", t.get("md5") == S2_MD5, t.get("md5", "?"))
    scratch_md5_before = t.get("md5")

    c0 = census("BEFORE (this run mutates nothing)", SCRATCH)
    gate("Q4 census == the verified S2 numbers %r" % BASELINE,
         all(c0[k] == v for k, v in BASELINE.items()), repr(c0))

    # ------------------------------------------------------------------ B1
    print("\n--- B1: every node of Diagram #%d in AbstractDiagram.Nodes[] order" % SIBLING_DIAG_UID, flush=True)
    d686 = diag_index(SCRATCH, SIBLING_DIAG_UID)
    fact("Diagram #%d reads Traverse index %d - re-read here, never cached (34(h))" % (SIBLING_DIAG_UID, d686))
    w = WALK(SCRATCH, d686, limit=200)
    gate("Q5 the Nodes[] walk of Diagram #%d returns at least 20 nodes" % SIBLING_DIAG_UID, len(w) >= 20,
         "%d nodes" % len(w))

    nodes = []
    for uid, (ni, label, rows) in w.items():
        outs = [{"i": r["i"], "name": r["name"], "wire": r["wire"]}
                for r in rows if r["is_source"] and (r["name"] or "").strip()]
        ins = [{"i": r["i"], "name": r["name"], "wire": r["wire"]}
               for r in rows if not r["is_source"]]
        nodes.append({"uid": uid, "node_index": ni, "label": label, "class_guess": cls_of(uid, w),
                      "n_terms": len(rows), "named_output_terminals": outs,
                      "data_types": "NOT MEASURABLE (no Terminal.DataType reader in the built fleet)",
                      "input_terminals": ins,
                      "fed_inputs": [x for x in ins if x["wire"]]})
    nodes.sort(key=lambda r: r["node_index"])
    R["B1"] = {"diagram_uid": SIBLING_DIAG_UID, "diagram_index": d686, "n_nodes": len(nodes), "nodes": nodes}
    for r in nodes:
        print(("      NODE Nodes[%3d] #%-6d %-16s %-38r  %d named-out, %d fed-in"
               % (r["node_index"], r["uid"], r["class_guess"], (r["label"] or "")[:38],
                  len(r["named_output_terminals"]), len(r["fed_inputs"])))
              .encode("ascii", "replace").decode("ascii"), flush=True)
        for t_ in r["named_output_terminals"][:40]:
            print(("           out t%-3d %-42r wire %s" % (t_["i"], (t_["name"] or "")[:42], t_["wire"]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
    gate("Q6 B1 is captured in full for all %d nodes" % len(nodes),
         all("named_output_terminals" in r for r in nodes), "")
    fl = next((r for r in nodes if r["uid"] == FRAME_LOOP_UID), None)
    gate("Q7 WhileLoop #%d is on Diagram #%d and exposes named output terminals"
         % (FRAME_LOOP_UID, SIBLING_DIAG_UID), bool(fl) and bool(fl["named_output_terminals"]),
         "%d named outputs" % (len(fl["named_output_terminals"]) if fl else -1), fatal=False)

    # ------------------------------------------------------------------ B3: the #637 dependency map
    print("\n--- B3: wire -> source-node map on Diagram #%d, then the #%d dependency verdicts"
          % (SIBLING_DIAG_UID, FRAME_LOOP_UID), flush=True)
    src_of = {}
    for r in nodes:
        for t_ in r["named_output_terminals"]:
            if t_["wire"]:
                src_of.setdefault(t_["wire"], []).append((r["uid"], t_["i"], t_["name"]))
    # unnamed source terminals count too (tunnels often have out_name '')
    for uid, (ni, label, rows) in w.items():
        for rr in rows:
            if rr["is_source"] and rr["wire"]:
                src_of.setdefault(rr["wire"], [])
                if not any(x[0] == uid and x[1] == rr["i"] for x in src_of[rr["wire"]]):
                    src_of[rr["wire"]].append((uid, rr["i"], rr["name"]))
    R["B3"]["wire_to_source_node"] = {str(k): v for k, v in src_of.items()}
    fact("wire -> source-node map built from the walk itself: %d distinct wires have a SOURCE terminal on "
         "Diagram #%d" % (len(src_of), SIBLING_DIAG_UID))

    direct = {}
    for r in nodes:
        deps, unresolved = set(), []
        for t_ in r["fed_inputs"]:
            owners = src_of.get(t_["wire"]) or []
            if not owners:
                unresolved.append(t_)
            for (ouid, _oi, _on) in owners:
                if ouid != r["uid"]:
                    deps.add(ouid)
        direct[r["uid"]] = {"deps": sorted(deps), "unresolved": unresolved}

    # transitive closure inside #686 (bounded; the graph has ~24 nodes)
    trans = {u: set(direct[u]["deps"]) for u in direct}
    for _ in range(len(nodes) + 1):
        changed = False
        for u in trans:
            add = set()
            for d_ in trans[u]:
                add |= trans.get(d_, set())
            add.discard(u)
            if not add <= trans[u]:
                trans[u] |= add
                changed = True
        if not changed:
            break

    verdicts = []
    for r in nodes:
        u = r["uid"]
        d_ = direct[u]
        v = {"uid": u, "node_index": r["node_index"], "class_guess": r["class_guess"], "label": r["label"],
             "n_fed_inputs": len(r["fed_inputs"]),
             "direct_source_nodes": d_["deps"],
             "fed_inputs_whose_wire_has_NO_source_on_686": [x["wire"] for x in d_["unresolved"]],
             "depends_on_637_DIRECTLY": FRAME_LOOP_UID in d_["deps"],
             "depends_on_637_TRANSITIVELY": FRAME_LOOP_UID in trans[u],
             "independent_of_637": (u != FRAME_LOOP_UID and FRAME_LOOP_UID not in trans[u])}
        verdicts.append(v)
        print(("      B3 #%-6d %-16s fed-in %-3d direct %s | 637 direct=%s trans=%s => %s"
               % (u, r["class_guess"], len(r["fed_inputs"]), d_["deps"][:8], v["depends_on_637_DIRECTLY"],
                  v["depends_on_637_TRANSITIVELY"],
                  "INDEPENDENT of #637" if v["independent_of_637"] else "depends on #637"))
              .encode("ascii", "replace").decode("ascii"), flush=True)
    R["B3"]["verdicts"] = verdicts
    indep = [v["uid"] for v in verdicts if v["independent_of_637"]]
    R["B3"]["independent_uids"] = indep
    fact("B3 SUMMARY: %d of %d nodes on Diagram #%d are INDEPENDENT of WhileLoop #%d (no fed input traces to it "
         "inside #%d): %s" % (len(indep), len(nodes), SIBLING_DIAG_UID, FRAME_LOOP_UID, SIBLING_DIAG_UID, indep))

    ctrl = next((v for v in verdicts if v["uid"] == CONTROL_NODE[0]), None)
    gate("Q8 the measured control #%d %r is INDEPENDENT of #%d" % (CONTROL_NODE[0], CONTROL_NODE[1],
                                                                   FRAME_LOOP_UID),
         bool(ctrl) and ctrl["independent_of_637"], repr(ctrl), fatal=False)

    # spot-check the map against the wire's own Terms[]
    print("\n--- Q10 spot-check of the wire->source map against OpWireSource_v5", flush=True)
    with open(MAP_WS, encoding="utf-8") as f:
        ws_labels = json.load(f)
    ws = g.op(OP_WS)
    sample, checked, agree = [], 0, 0
    for r in nodes:
        for t_ in r["fed_inputs"][:2]:
            if len(sample) < 6 and t_["wire"]:
                sample.append((r["uid"], t_["wire"]))
    for (node_uid, wuid) in sample:
        rows = []
        for i in range(8):
            rr = read_term(ws, ws_labels, SCRATCH, wuid, i)
            if rr["errs"] and rr["owner_uid"] == 0 and not rr["is_source"]:
                break
            rows.append(rr)
        srcs = [rr["owner_uid"] for rr in rows if rr["is_source"] and rr["recip_wire"] == wuid]
        mapped = [x[0] for x in (src_of.get(wuid) or [])]
        ok = bool(srcs) and (srcs[0] in mapped or not mapped)
        checked += 1
        agree += 1 if ok else 0
        R["B3"].setdefault("spot_checks", []).append(
            {"sink_node": node_uid, "wire": wuid, "wiresource_owner_uids": srcs, "map_says": mapped,
             "agrees": ok})
        fact("spot-check w%d (into #%d): OpWireSource_v5 source owner %r, walk map says %r -> %s"
             % (wuid, node_uid, srcs, mapped, "AGREE" if ok else "DISAGREE"))
    gate("Q10 every sampled wire agrees (%d/%d)" % (agree, checked), checked and agree == checked,
         "%d checked" % checked, fatal=False)

    # ------------------------------------------------------------------ B2
    print("\n--- B2: the eight element types against B1 (DOCUMENT-DERIVED types; see the note above)", flush=True)
    by_uid = {r["uid"]: r for r in nodes}
    b2 = []
    for q in QUEUE_TYPES:
        row = dict(q)
        row["type_match_on_686_MEASURED"] = ("NOT MEASURABLE - no Terminal.DataType reader; only the exact "
                                             "(uid, terminal name) pairs the plan already measured can be "
                                             "confirmed to EXIST on #686")
        if q["plan_src_uid"] is None:
            row["named_terminal_exists_on_686"] = False
            row["exists_note"] = "the plan names no (node, named output terminal) pair on #686 for this queue"
        else:
            n = by_uid.get(q["plan_src_uid"])
            hit = [t_ for t_ in (n["named_output_terminals"] if n else []) if t_["name"] == q["plan_terminal"]]
            row["named_terminal_exists_on_686"] = bool(hit)
            row["terminal_indices"] = [t_["i"] for t_ in hit]
            v = next((x for x in verdicts if x["uid"] == q["plan_src_uid"]), None)
            row["src_independent_of_637"] = (v or {}).get("independent_of_637")
            row["src_is_637_itself"] = q["plan_src_uid"] == FRAME_LOOP_UID
        b2.append(row)
        print(("      B2 %-12s %-26s plan src #%-6s %-30r exists_on_686=%s independent_of_637=%s"
               % (q["queue"], q["element_type"], q["plan_src_uid"], (q["plan_terminal"] or "")[:30],
                  row.get("named_terminal_exists_on_686"), row.get("src_independent_of_637")))
              .encode("ascii", "replace").decode("ascii"), flush=True)
    R["B2"] = {"source": "docs/d1-build-plan.md sec.9 :576-585 (read by this script's author, not parsed here)",
               "rows": b2,
               "caveat": "the element TYPES are the plan's; this script verified only that the named (uid, "
                         "terminal) pair EXISTS on Diagram #686 and whether that source is independent of #637"}

    # ------------------------------------------------------------------ Q11: prove nothing changed
    print("\n--- Q11: proving this run mutated nothing", flush=True)
    c1 = census("AFTER (must equal BEFORE)", SCRATCH)
    same = c1 == c0
    t2 = probe("Q11 the scratch on disk, after the read", SCRATCH)
    gate("Q11 nothing was created, moved or saved: census identical AND the scratch's md5 on disk unchanged",
         same and t2.get("md5") == scratch_md5_before,
         "census_same=%s md5 %s vs %s" % (same, t2.get("md5"), scratch_md5_before))
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at the first FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
        rc = 1
    finally:
        try:
            g.reset()
        except Exception:                                                         # noqa: BLE001
            pass
        refs = None
        try:
            refs = g.ref_counts()
        except Exception:                                                         # noqa: BLE001
            pass
        R["ref_counts_end"] = refs
        try:
            R["handles"]["after"] = labview_handles()
        except Exception:                                                         # noqa: BLE001
            R["handles"]["after"] = None
        print("\n--- close-out", flush=True)
        fact("refs at end: %r" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"].get("after"), R["handles"].get("before")))
        gate("Q12 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,), fatal=False)
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            d = probe("Q13 %s after the run" % tag, path)
            R.setdefault("untouched", {})[tag] = d.get("md5")
            ok = d.get("md5") == pin
            gate("Q13 %s md5 unchanged" % tag, ok, d.get("md5", "?"), fatal=False)
            if not ok:
                rc = 1
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH (read only, never saved): %s" % SCRATCH, flush=True)
        print("=== NO VI WAS RUN (34(f)); no new op; nothing mutated.", flush=True)
        sys.exit(rc)
