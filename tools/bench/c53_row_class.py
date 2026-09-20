"""
CYCLE 53 MATERIAL TASK 3 -- TEST A: classify every terminal that a `move_in` of the
1.5 FOCUS set would CUT.  PURE FILE READ: no LabVIEW, no COM, no VI opened.

PRIOR ART CHECKED BEFORE WRITING (CLAUDE.md "before creating any new tool"):
  * `tools/gscript.py` has no row-classifier (`grep "^def "` -> wiring/traverse ops only).
  * `tools/bench/` already holds the INPUT censuses; no file cross-classifies them:
      - tools/bench/d1_rewire_sources.json   (109 cut rows, the brief's T0 input)
      - tools/bench/main_vi_netmap.json      (independent per-diagram wire->terminal map)
      - tools/bench/main_vi_shiftregs_v1.json(SR pair inside/outside terminals + wires)
      - tools/bench/diagram19.json           (Diagram traverse index 19 node census)
  * `tools/recipes/` NOT touched, NOT read for reuse (task-3 brief forbids touching it).
This file is a DIAGNOSTIC under tools/bench/, never a recipe.

PREDICTION CONTRACT (checked by the gates below, all from files, none from memory):
  G1  the 1.5 FOCUS members {10407, 48, 3529, 3560, 3447} all appear as row owners.
  G2  the cut-row count equals the terminal count those uids expose in the
      INDEPENDENT netmap wire table for their diagram -- two files must agree.
  G3  every row's `wire` uid is confirmed by the netmap on the same diagram.
  G4  the diagram traverse indices the rewire JSON names ("43", "19") resolve, in the
      netmap, to owner classes WhileLoop / FlatSequenceFrame respectively.
  G5  no row carries a `Required` field  -> the column is reported UNKNOWN, not guessed.
  G2b/G2c  REWRITTEN after a FAILED PREDICTION and an adversarial peer review that REFUTED my
      explanation (archive/peer/2026-09-20-c53-g2b-caseselector.md, claude/hypothesis, opus max,
      ANSWERED).  The original G2b asserted the netmap's per-node `terms` array would hold 17 wired
      terminals on the 5 uids; it holds 16, and my "the CaseStructure SELECTOR is omitted" story was
      wrong: `tools/bench/sweep_netmap_main.py:63-64` filters out EVERY unnamed terminal on EVERY node
      of EVERY class and discards the terminal index.  The gates now run the peer's own discriminating
      test over every node present in both censuses.
  G6  the 17 cut rows are confirmed by a THIRD, independently-taken census
      (`main_vi_nodeterms.json`, OpNodeTerms_v0 -- not the op that produced the netmap).
  C1  claim (i)  : #48 t3 <- wire 1731 <- inside(LeftShiftRegister #4344);
                   #4344 outside wire 4185 ; #4334 outside wire 7506.
  C2  claim (ii) : d1-build-plan.md:402-403 "Both SR pairs are re-created on the new loop"
                   and :418 on refnum border tunnels.
Competing predictions on the record -- REPORTED, never argued:
  37(g)=0 cross-loop rows | P6 review=3 (:1748,:1793,:1892) | prior-art adds a 4th (#10407 t6 -> #12589 t1).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(ROOT) if os.path.basename(ROOT) == "tools" else ROOT
PROJ = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
B = os.path.join(PROJ, "tools", "bench")
D = os.path.join(PROJ, "docs")

FOCUS_NODES = [10407, 48, 3529, 3560, 3447]
SR_PAIRS = {"visa": (4334, 4344), "position": (4256, 4274)}

npass = nfail = 0
lines = []


def out(s):
    lines.append(s)
    print(s)


def gate(label, ok, detail=""):
    global npass, nfail
    if ok:
        npass += 1
    else:
        nfail += 1
    out("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail))


src = json.load(open(os.path.join(B, "d1_rewire_sources.json"), encoding="utf-8"))
net = json.load(open(os.path.join(B, "main_vi_netmap.json"), encoding="utf-8"))
sr = json.load(open(os.path.join(B, "main_vi_shiftregs_v1.json"), encoding="utf-8"))
raw = open(os.path.join(B, "d1_rewire_sources.json"), encoding="utf-8").read().splitlines()

out("=" * 78)
out("TEST A -- 1.5 FOCUS set cut-row classification (file reads only)")
out("=" * 78)
out("inputs: d1_rewire_sources.json (%d rows) | main_vi_netmap.json (source=%s)"
    % (len(src["rows"]), net.get("source")))

# ---------------------------------------------------------------- G4 : index -> owner class
owners = net["diagram_owners"]
gate("G4a", owners[43] == "WhileLoop", "diagram_owners[43]=%r" % owners[43])
gate("G4b", owners[19] == "FlatSequenceFrame", "diagram_owners[19]=%r" % owners[19])
d43 = net["diagrams"]["43"]
d19 = net["diagrams"]["19"]

# netmap `nodes` is keyed BY UID: {"<uid>": {"label":..., "terms":[[name, wire], ...]}}
# its `wires` table addresses nodes by POSITION in that dict, so build the map from the order.
idx2uid43 = {i: int(k) for i, k in enumerate(d43["nodes"])}
uid2idx43 = {v: k for k, v in idx2uid43.items()}

# ---------------------------------------------------------------- line numbers of each row
row_lines = {}
for ln, text in enumerate(raw, 1):
    if text.strip() == "{":
        # the next two lines are uid / i
        try:
            u = int(raw[ln].split(":")[1].strip().rstrip(","))
            i = int(raw[ln + 1].split(":")[1].strip().rstrip(","))
        except Exception:
            continue
        row_lines[(u, i)] = ln

# ---------------------------------------------------------------- collect the cut rows
cut = [r for r in src["rows"] if r["uid"] in FOCUS_NODES]
gate("G1", sorted({r["uid"] for r in cut}) == sorted(FOCUS_NODES),
     "row owners present = %s" % sorted({r["uid"] for r in cut}))

# independent terminal census from the netmap for those uids on diagram 43
netterms = {}   # uid -> set of terminal indices
for wuid, ends in d43["wires"].items():
    for e in ends:
        nidx, tidx, tname = e[0], e[1], e[2]
        u = idx2uid43.get(nidx)
        if u in FOCUS_NODES:
            netterms.setdefault(u, {})[tidx] = (tname, int(wuid))
n_net = sum(len(v) for v in netterms.values())
gate("G2", n_net == len(cut),
     "netmap terminal ends on the 5 uids = %d ; rewire cut rows = %d" % (n_net, len(cut)))

bad = []
for r in cut:
    t = netterms.get(r["uid"], {}).get(r["i"])
    if t is None or t[1] != r["wire"]:
        bad.append((r["uid"], r["i"], r["wire"], t))
gate("G3", not bad, "wire uid mismatches vs netmap: %s" % (bad or "none"))

gate("G5", not any("required" in k.lower() for r in cut for k in r),
     "no Required field in any cut row -> column reported UNKNOWN")

# independent per-node terminal census (total vs WIRED) straight from the netmap
term_census = {}
for u in FOCUS_NODES:
    nd = d43["nodes"].get(str(u))
    if nd is None:
        term_census[u] = {"total": "UNKNOWN", "wired": "UNKNOWN", "terms": []}
        continue
    tm = nd["terms"]
    term_census[u] = {
        "total": len(tm),
        "wired": sum(1 for t in tm if t[1]),
        "terms": [{"i": i, "name": t[0], "wire": t[1]} for i, t in enumerate(tm)],
    }
out("  OBS   netmap per-node `terms` array, total/wired: %s"
    % {u: "%s/%s" % (term_census[u]["total"], term_census[u]["wired"]) for u in FOCUS_NODES})

# -------------------------------------------------------------------------------------------------
# G2b/G6 -- THE REWRITTEN GATE.  My first G2b predicted the netmap `terms` array would carry 17 wired
# terminals on the 5 uids; it carries 16.  My explanation ("the array omits the CaseStructure
# SELECTOR") was dispatched to an adversarial peer and REFUTED:
#   archive/peer/2026-09-20-c53-g2b-caseselector.md  (claude / hypothesis, opus max, ANSWERED, $3.2538, 497 s)
# Measured mechanism, cited by the peer and re-run here: `tools/bench/sweep_netmap_main.py:63-64` writes
#   "terms": [[t, w] for _ti, t, w in terms if t]
# -- an UNNAMED-terminal filter on every node of every class, which also DISCARDS the real terminal
# index `_ti`.  So a netmap `terms` index carries no index information at all, and the array is the
# NAMED SUBSET in order.  G2b compared a name-filtered set (16) with a wire-filtered set (17): a
# category error, not a discovery.  Both numbers were right.  The peer's own falsifier is on disk:
# WhileLoop #637 t37 is unnamed AND wired (main_vi_nodeterms.json:6868-6872) -- not a Case Structure.
# THE PEER'S DISCRIMINATING TEST IS RUN BELOW over all nodes present in both files.
nt = json.load(open(os.path.join(B, "main_vi_nodeterms.json"), encoding="utf-8"))
nt_nodes = {}
for dk, dv in nt["diagrams"].items():
    for nd in dv.get("nodes", []):
        nt_nodes[(dk, int(nd["uid"]))] = nd["terms"]

sweep = {"checked": 0, "shortfall_eq_unnamed": 0, "named_subset_matches": 0,
         "violations_shortfall": [], "violations_named": [], "nodes_with_shortfall": 0}
for dk, dv in net["diagrams"].items():
    for uk, nm_node in dv.get("nodes", {}).items():
        terms = nt_nodes.get((dk, int(uk)))
        if terms is None:
            continue
        sweep["checked"] += 1
        A = [(t["name"], t["wire"]) for t in terms if t["name"]]
        Bn = [(t[0], t[1]) for t in nm_node["terms"]]
        shortfall = len(terms) - len(Bn)
        unnamed = sum(1 for t in terms if not t["name"])
        if shortfall:
            sweep["nodes_with_shortfall"] += 1
        if shortfall == unnamed:
            sweep["shortfall_eq_unnamed"] += 1
        elif len(sweep["violations_shortfall"]) < 10:
            sweep["violations_shortfall"].append(
                {"diagram": dk, "uid": int(uk), "shortfall": shortfall, "unnamed": unnamed})
        if A == Bn:
            sweep["named_subset_matches"] += 1
        elif len(sweep["violations_named"]) < 10:
            sweep["violations_named"].append({"diagram": dk, "uid": int(uk),
                                              "nodeterms_named": A[:6], "netmap_terms": Bn[:6]})
gate("G2b(rewritten) netmap `terms` == the NAMED SUBSET, in order, for EVERY node in both files",
     sweep["checked"] and sweep["named_subset_matches"] == sweep["checked"],
     "%d/%d nodes match; violations %s"
     % (sweep["named_subset_matches"], sweep["checked"], sweep["violations_named"][:2]))
gate("G2c the per-node SHORTFALL equals that node's UNNAMED-terminal count, for EVERY node "
     "(refutes 'CaseStructure selector only'; confirms the write-time `if t` filter)",
     sweep["checked"] and sweep["shortfall_eq_unnamed"] == sweep["checked"],
     "%d/%d; %d nodes have a shortfall at all; violations %s"
     % (sweep["shortfall_eq_unnamed"], sweep["checked"], sweep["nodes_with_shortfall"],
        sweep["violations_shortfall"][:2]))
unnamed_wired = [(dk, uid, t["i"], t["wire"])
                 for (dk, uid), terms in nt_nodes.items() for t in terms
                 if not t["name"] and t["wire"]]
out("      unnamed-AND-WIRED terminals in main_vi_nodeterms.json: %d "
    "(every one invisible in the netmap `terms` array). WhileLoop #637 t37 among them: %s"
    % (len(unnamed_wired), any(u == 637 and i == 37 for _d, u, i, _w in unnamed_wired)))

# G6 -- the 17 cut rows, agreed by a THIRD, independently-taken census (OpNodeTerms_v0, not OpNetInfo_v0)
mism = []
for r in cut:
    terms = nt_nodes.get(("43", r["uid"]))
    t = next((x for x in terms if x["i"] == r["i"]), None) if terms else None
    if t is None or t["name"] != r["name"] or t["wire"] != r["wire"] or t["is_source"] != r["is_source"]:
        mism.append((r["uid"], r["i"], t))
gate("G6 all %d cut rows agree with main_vi_nodeterms.json on (name, wire, is_source)" % len(cut),
     not mism, "mismatches: %s" % (mism or "none"))
gate("G6b #10407 t0 (name '', wire 10799) IS carried by that third census, with clean error columns",
     any(t["i"] == 0 and t["name"] == "" and t["wire"] == 10799 and t["errs"] == [0, 0, 0, 0]
         for t in nt_nodes.get(("43", 10407), [])),
     "=> d1_rewire_sources.json did NOT invent index 0")

# ---------------------------------------------------------------- classify
SR_BY_RIGHT = {v[0]: k for k, v in SR_PAIRS.items()}


def other_end_where(r):
    """Where the far end of this wire sits AT THE MOMENT S3 WOULD RUN."""
    res = []
    for oe in r.get("other_ends", []):
        u = oe.get("uid")
        loc = "#639 (diagram idx 43, owner class %s)" % owners[43]
        moves = u in FOCUS_NODES
        dest = None
        for rr in src["rows"]:
            if rr["uid"] == u:
                dest = rr.get("dest")
                break
        res.append({"kind": "node", "uid": u, "i": oe.get("i"), "name": oe.get("name"),
                    "sits_on": loc,
                    "moves_with_1.5_set": moves,
                    "planned_dest_row": dest if dest else "UNKNOWN (no row of its own)"})
    s = r.get("source")
    if s and s.get("kind") == "sr":
        res.append({"kind": "shift-register", "right": s["right"], "left": s["left"],
                    "row": s["row"], "side": s["side"],
                    "sits_on": "to be CREATED on the new 1.5 loop (d1-build-plan.md:402)"})
    if s and s.get("kind") == "tunnel":
        res.append({"kind": "tunnel", "uid": s["uid"], "index_mode": s.get("index_mode"),
                    "out_name": s.get("out_name"),
                    "outer_wire": r.get("outer_wire"),
                    "outer_source": r.get("outer_source"),
                    "sits_on": "border of WhileLoop #637; outer terminal on #686 "
                               "(diagram idx 19, owner class %s)" % owners[19]})
    return res


def verb(r):
    a = r["action"]
    if a.startswith("cross-loop"):
        return "queue endpoint (Q_focus, d1-build-plan.md:424-429)"
    if a == "from-tunnel":
        return "border tunnel (created on the new 1.5 loop)"
    if a in ("to-sr", "from-sr"):
        return "add_shift_reg / wire_sr -- CREATED, not moved (d1-build-plan.md:402)"
    # same-loop / source-side: is the far end inside the moved set?
    ends = [oe.get("uid") for oe in r.get("other_ends", [])]
    if ends and all(u in FOCUS_NODES for u in ends):
        return "move_in both ends, then re-wire INSIDE the new 1.5 loop"
    if not ends:
        return "UNKNOWN (no far end recorded in the file)"
    return "UNKNOWN (far end does not move; no verb named by d1-build-plan.md section 6)"


table = []
for r in sorted(cut, key=lambda x: (FOCUS_NODES.index(x["uid"]), x["i"])):
    table.append({
        "owner_uid": r["uid"],
        "terminal_index": r["i"],
        "terminal_name": r["name"],
        "is_source": r["is_source"],
        "source_or_sink": "source" if r["is_source"] else "sink",
        "action_verbatim": r["action"],
        "wire": r["wire"],
        "json_line": row_lines.get((r["uid"], r["i"]), "UNKNOWN"),
        "dest_row": r.get("dest"),
        "other_end": other_end_where(r),
        "required": "UNKNOWN (neither d1_rewire_sources.json nor d1-build-plan.md section 6 "
                    "carries a LabVIEW Required flag)",
        "construction_verb": verb(r),
    })

out("")
out("--- TABLE: %d cut terminals ---" % len(table))
hdr = "%-6s %-3s %-38s %-6s %-22s %-6s %-6s" % (
    "uid", "t", "terminal name", "src?", "action (verbatim)", "wire", "line")
out(hdr)
out("-" * len(hdr))
for t in table:
    out("%-6s %-3s %-38s %-6s %-22s %-6s %-6s" % (
        t["owner_uid"], t["terminal_index"], repr(t["terminal_name"])[:38],
        "SRC" if t["is_source"] else "sink", t["action_verbatim"], t["wire"], t["json_line"]))

# ---------------------------------------------------------------- counts
cross = [t for t in table if t["action_verbatim"].startswith("cross-loop:")]
by_action = {}
for t in table:
    by_action[t["action_verbatim"]] = by_action.get(t["action_verbatim"], 0) + 1

src_on_639 = [t for t in table
              if any(o["kind"] == "node" for o in t["other_end"])
              and (t["action_verbatim"] in ("same-loop",) or t["action_verbatim"].startswith("cross-loop"))]
resolved_src_node = [t for t in table
                     if next((r for r in cut if r["uid"] == t["owner_uid"] and r["i"] == t["terminal_index"]), {})
                     .get("source", {}) and
                     (next(r for r in cut if r["uid"] == t["owner_uid"] and r["i"] == t["terminal_index"])
                      .get("source") or {}).get("kind") == "node"]
src_on_686 = [t for t in table if any(o.get("kind") == "tunnel" and o.get("outer_source") for o in t["other_end"])]
sr_rows = [t for t in table if t["action_verbatim"] in ("to-sr", "from-sr")]
inside_12 = [t for t in table
             if any(o.get("kind") == "node" and o.get("planned_dest_row") == "1.2" for o in t["other_end"])]

out("")
out("--- COUNTS (measured) ---")
out("total cut rows                                  : %d" % len(table))
out("by action                                       : %s" % json.dumps(by_action))
out("action starts 'cross-loop:'                     : %d  -> %s"
    % (len(cross), [(t["owner_uid"], t["terminal_index"], t["json_line"]) for t in cross]))
out("rows whose resolved SOURCE is a node on #639    : %d  -> %s"
    % (len(resolved_src_node), [(t["owner_uid"], t["terminal_index"]) for t in resolved_src_node]))
out("rows whose resolved source is on #686           : %d  (outer_source non-null on a tunnel row)"
    % len(src_on_686))
out("rows whose far end is a node planned for 1.2    : %d  -> %s"
    % (len(inside_12), [(t["owner_uid"], t["terminal_index"]) for t in inside_12]))
out("SR-created rows (to-sr / from-sr)               : %d  -> %s"
    % (len(sr_rows), [(t["owner_uid"], t["terminal_index"]) for t in sr_rows]))

# far ends that are NOT cut but lose their wire's other end
orphans = []
for t in table:
    for o in t["other_end"]:
        if o.get("kind") == "node" and not o.get("moves_with_1.5_set"):
            orphans.append((o["uid"], o["i"], o["name"], t["wire"]))
out("counterpart terminals on NON-moved nodes (orphaned, not cut): %d -> %s"
    % (len(orphans), orphans))

# ---------------------------------------------------------------- C1 : the SR claim
out("")
out("--- C1: claim (i), main_vi_shiftregs_v1.json ---")
regs = sr["registers"] if isinstance(sr, dict) else sr
out("      main_vi_shiftregs_v1.json: vi=%s loop_uid=%s registers=%d"
    % (os.path.basename(sr.get("vi", "?")) if isinstance(sr, dict) else "?",
       sr.get("loop_uid") if isinstance(sr, dict) else "?", len(regs)))
pair = next((x for x in regs if x.get("uid") == 4334), None)
left = pair.get("left") if pair else None
c1a = bool(left) and left.get("uid") == 4344 and left.get("class") == "LeftShiftRegister"
c1b = bool(left) and left["out"]["wire"] == 4185
c1c = bool(left) and left["inside"][0]["wire"] == 1731
c1d = bool(pair) and pair["out"]["wire"] == 7506
r48t3 = next(r for r in cut if r["uid"] == 48 and r["i"] == 3)
c1e = r48t3["wire"] == 1731 and r48t3["source"]["left"] == 4344 and r48t3["source"]["right"] == 4334
gate("C1a", c1a, "#4334.left = %s" % (left.get("uid") if left else None))
gate("C1b", c1b, "#4344 OUTSIDE wire = %s (claim 4185)" % (left["out"]["wire"] if left else None))
gate("C1c", c1c, "#4344 INSIDE wire = %s  == #48 t3 wire %s" % (left["inside"][0]["wire"] if left else None, r48t3["wire"]))
gate("C1d", c1d, "#4334 OUTSIDE wire = %s (claim 7506)" % (pair["out"]["wire"] if pair else None))
gate("C1e", c1e, "#48 t3 action=%s sr=(r%s,l%s)" % (r48t3["action"], r48t3["source"]["right"], r48t3["source"]["left"]))
# where do 4185 / 7506 live?
w19 = d19["wires"]
loc4185 = w19.get("4185")
loc7506 = w19.get("7506")
n19 = {i: int(k) for i, k in enumerate(d19["nodes"])}
gate("C1f", loc4185 is not None and loc7506 is not None,
     "on diagram idx 19 (#686): 4185 ends=%s  7506 ends=%s" % (loc4185, loc7506))
pair2 = next((x for x in regs if x.get("uid") == 4256), None)
left2 = pair2.get("left") if pair2 else None
r48t4 = next(r for r in cut if r["uid"] == 48 and r["i"] == 4)
gate("C1g", bool(left2) and left2["uid"] == 4274 and left2["inside"][0]["wire"] == r48t4["wire"],
     "position pair: #4256 outside w%s / inside w%s ; #4274 outside w%s / inside w%s == #48 t4 w%s"
     % (pair2["out"]["wire"] if pair2 else None,
        pair2["inside"][0]["wire"] if pair2 else None,
        left2["out"]["wire"] if left2 else None,
        left2["inside"][0]["wire"] if left2 else None, r48t4["wire"]))
gate("C1h", (sr.get("loop_uid") if isinstance(sr, dict) else None) == 637,
     "both SR pairs are registers of loop_uid=%s" % (sr.get("loop_uid") if isinstance(sr, dict) else "?"))
out("      -> both wires appear ONLY as terminals of node idx 4 = uid %s (= WhileLoop #637) on #686;"
    % n19.get(4))
out("      -> NO other node terminal on #686 carries either wire, so the SOURCE OBJECT of 4185 is")
out("         UNMEASURED by these files (not a node terminal: constant / control term / FS tunnel).")

# ---------------------------------------------------------------- C2 : the plan claim
out("")
out("--- C2: claim (ii), docs/d1-build-plan.md ---")
plan = open(os.path.join(D, "d1-build-plan.md"), encoding="utf-8").read().splitlines()
l402, l403, l418 = plan[401], plan[402], plan[417]
gate("C2a", "Both SR pairs are re-created on the new loop" in l402,
     ":402 = %r" % l402[:110])
gate("C2b", "4256" in l402 and "4274" in l402 and "4334" in l402 and "4344" in l402,
     ":402 names both pairs")
gate("C2c", "refnum" in l418.lower() and "tunnel" in l418.lower(),
     ":418 = %r" % l418[:130])
out("      :403 = %r" % l403[:120])
out("      NOTE (verbatim, :418-419): the same sentence says the route is one 'the plan never named',")
out("      and :419 says 'Adding move-table rows is a judgement call => flagged (11.6), not patched.'")

# ---------------------------------------------------------------- write
res = {
    "generated": "cycle53 material task 3 / TEST A",
    "inputs": ["tools/bench/d1_rewire_sources.json", "tools/bench/main_vi_netmap.json",
               "tools/bench/main_vi_shiftregs_v1.json", "tools/bench/diagram19.json",
               "docs/d1-build-plan.md:396-421"],
    "focus_set": FOCUS_NODES,
    "sr_pairs": SR_PAIRS,
    "diagram_index_map": {"43": {"owner_class": owners[43],
                                 "identified_as": "Diagram #639 (WhileLoop #637 body) -- "
                                 "corroborated by tools/bench/diag_movein_set.json, cycle 52"},
                          "19": {"owner_class": owners[19],
                                 "identified_as": "Diagram #686 -- holds WhileLoop #637 as node idx %s"
                                 % n19.get(4)}},
    "counts": {
        "total_cut_rows": len(table),
        "by_action": by_action,
        "cross_loop_rows": [(t["owner_uid"], t["terminal_index"], t["json_line"]) for t in cross],
        "n_cross_loop": len(cross),
        "n_source_is_node_on_639": len(resolved_src_node),
        "n_source_on_686": len(src_on_686),
        "n_far_end_planned_for_1_2": len(inside_12),
        "n_sr_created_rows": len(sr_rows),
        "orphaned_counterpart_terminals": orphans,
    },
    "predictions_on_the_record": {
        "pre_decided_37g": 0,
        "p6_review": {"n": 3, "lines": [1748, 1793, 1892]},
        "prior_art_extra": "#10407 t6 -> #12589 t1",
    },
    "netmap_terminal_census_diagram43": term_census,
    "g2b_refutation": {
        "review": "archive/peer/2026-09-20-c53-g2b-caseselector.md (claude/hypothesis, opus max, "
                  "ANSWERED, $3.2538, 497 s)",
        "my_refuted_explanation": "the netmap `terms` array omits the CaseStructure SELECTOR",
        "measured_mechanism": "tools/bench/sweep_netmap_main.py:63-64 writes "
                              "`\"terms\": [[t, w] for _ti, t, w in terms if t]` -- an UNNAMED-terminal "
                              "filter on every node of every class, which also discards the real "
                              "terminal index _ti",
        "peer_falsifier_on_disk": "WhileLoop #637 t37 is unnamed AND wired "
                                  "(main_vi_nodeterms.json:6868-6872) -- not a CaseStructure",
        "discriminating_test": sweep,
        "n_unnamed_and_wired_terminals": len(unnamed_wired),
        "consequence": "state counts as WIRED TERMINALS; the netmap `terms` array is NOT a terminal "
                       "census and its indices are not terminal indices",
    },
    "gates": {"pass": npass, "fail": nfail},
    "table": table,
}
outp = os.path.join(B, "c53_row_class.json")
json.dump(res, open(outp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
out("")
out("wrote %s" % outp)
out("%d pass / %d fail" % (npass, nfail))
