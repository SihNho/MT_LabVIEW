"""
CYCLE 54 MATERIAL -- JOB 1: replay `net_map`'s terminal walk over the COMPLETE census and
re-derive every netmap-sourced fact about `WhileLoop #637`'s border.

PURE FILE READ.  No LabVIEW, no COM, no `.vi` opened, no motor/ASI/camera/GUI.
This file is a DIAGNOSTIC under tools/bench/, never a recipe.

PRIOR ART CHECKED BEFORE WRITING (CLAUDE.md "before creating any new op, tool, or recipe"):
  * `grep "^def " tools/gscript.py` -> wiring / traverse / report ops only; no replay, no
    wire-index builder, no census comparator.  `net_map` (:2500-2600) is the PRODUCER of the
    truncated file, not a checker of it.
  * `tools/bench/` already holds every INPUT; nothing replays the walk offline:
      - tools/bench/main_vi_nodeterms.json  (OpNodeTerms_v0: 626 nodes / 3328 terminals,
        REAL terminal indices, is_source, per-field error columns -- the complete census)
      - tools/bench/main_vi_netmap.json     (net_map via sweep_netmap_main.py -- the truncated one)
      - tools/bench/c53_row_class.json      (the 17 cut rows of the 1.5 FOCUS set)
      - tools/bench/sweep_nodeterms_main.py (collection-time PREFIX check, not a replay:
        it reported 626 checked / 11 mismatches, all "node index out of range")
      - tools/bench/c53_row_class.py        (classifier; it READ the netmap and is the file
        whose C1f negative claim this job re-derives)
  * `docs/toolkit-capabilities.md` lists no offline census-replay tool.
  * NO NEW OP IS BUILT (Pre-decided 2).  NO LabVIEW RE-SWEEP (the review's own instruction:
    a re-sweep at max_terms=80 would cost ~74 min re-collecting what is on disk).

SOURCE OF THE RECIPE: archive/peer/2026-09-20-c53-netmap-terms-truncation.md section 6
(claude/hypothesis, opus max, ANSWERED, ACCEPTED IN FULL by the cycle-53 judgement session).

PREDICTION CONTRACT -- stated up front, checked by the gates below, every gate REPORTED and
none required (a FAIL here is a reading, not a build failure):

  P1  nodeterms holds 626 nodes.  The comparison runs over every (diagram, node uid) present
      in BOTH censuses.
  P2  574 of 626 nodes agree between the two censuses; 52 do not.
  P3  `WhileLoop #637` has 59 terminals and the netmap keeps 28 of them
      (12 of i0..i39 unnamed => 40 - 12 = 28).
  P4  Replaying gscript.py:2548-2569 over nodeterms and applying sweep_netmap_main.py:63-64's
      `if t` filter reproduces ALL 52 shortfalls: `cap@40` holds EXACTLY #637 (1 node),
      `empties>=3` holds the other 51 (#30804 and #4620 among them), `unexplained` is EMPTY.
      Falsifier, stated by the reviewer: any node left `unexplained`, or any node whose netmap
      array is shorter than the replay predicts while having <40 terminals, no 3-empty run and
      clean errs on the first dropped terminal.
  P5  netmap Diagram 19 (= Diagram #686) is missing all of #637's i40..i58 wire ends
      9051, 9000, 9649, 11253, 16421, 29006, 29122, 28392, 29081, 29106, 32583, 32344.
      (G12 FAILED on the literal reading and the run was refined -- see G12/G12b: the netmap
      `wires` table is keyed by WIRE UID and filled from every node of the diagram, so 7 of the
      12 appear in it via OTHER nodes.  The sound restatement, G12b, is that #637's OWN end is
      missing for all 12.  Recorded as a reading, not argued away.)
  P6  RE-DERIVATION, NO PREDICTION MADE (38(h) forbids one): for each of the 17 cut rows in
      c53_row_class.json, which node terminals of the COMPLETE census carry that row's wire;
      and whether ANY node terminal on Diagram #686 carries wire 4185 or 7506.  The count
      "sources on #686" is re-derived and REPORTED at whatever it comes out to -- the struck
      negative claim of Pre-decided 38(b) was drawn off the truncated table and is UNRESOLVED.

OUTPUT: tools/bench/replay_netmap_truncation.json  (all readings, machine-readable).
"""
import json
import os
import re

PROJ = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
B = os.path.join(PROJ, "tools", "bench")
D = os.path.join(PROJ, "docs")

npass = nfail = 0
lines = []


def out(s):
    lines.append(s)
    print(s, flush=True)


def gate(label, ok, detail=""):
    """The DOCUMENTED emitter (two spaces each side).  Never `**FAIL**` -- guard_peer's
    FAILURE_RE is `\\*{0,2}FAIL` and a bolded one is not the project's form."""
    global npass, nfail
    if ok:
        npass += 1
    else:
        nfail += 1
    out("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail))


# ---------------------------------------------------------------- inputs
NT = json.load(open(os.path.join(B, "main_vi_nodeterms.json"), encoding="utf-8"))
NM = json.load(open(os.path.join(B, "main_vi_netmap.json"), encoding="utf-8"))
RC = json.load(open(os.path.join(B, "c53_row_class.json"), encoding="utf-8"))

out("=" * 92)
out("CYCLE 54 JOB 1 -- net_map truncation REPLAY + #637 border RE-DERIVATION (files only)")
out("=" * 92)
out("nodeterms : %s  nodes=%d terminals=%d  vi=%s"
    % ("main_vi_nodeterms.json", NT["stats"]["nodes"], NT["stats"]["terminals"],
       os.path.basename(NT["vi"])))
out("netmap    : %s  diagrams=%d complete=%s"
    % ("main_vi_netmap.json", len(NM["diagrams"]), NM.get("complete")))
out("row table : %s  cut rows=%d" % ("c53_row_class.json", len(RC["table"])))
out("")

# ---------------------------------------------------------------- the replay
JUNK = ["reference", "reference out", "error in (no error)", "error out", "Method", "Method"]
MAX_TERMS = 40          # tools/gscript.py:2549  ->  for t in range(max_terms)
EMPTY_STOP = 3          # tools/gscript.py:2557-2560 -> break after 3 consecutive unnamed+unwired


def replay(terms, max_terms=MAX_TERMS):
    """Replay tools/gscript.py:2548-2569 exactly, then sweep_netmap_main.py:63-64's `if t`.

    Returns (emitted [[name, wire], ...] or None for the junk-Invoke signature, stop reason).
    """
    em, empties, stop = [], 0, "end-of-list"
    visited = 0
    for t in terms:
        if t["i"] >= max_terms:
            break
        visited += 1
        if t["name"] == "" and t["wire"] == 0:
            empties += 1
            if empties >= EMPTY_STOP:
                stop = "empties%d@i%d" % (EMPTY_STOP, t["i"])
                break
            em.append(t)
            continue
        empties = 0
        em.append(t)
        # gscript.py:2564-2565 -- the op's own junk Invoke signature ends the WHOLE walk
        if t["i"] == 5 and [x["name"] for x in em[:6]] == JUNK:
            return None, "junk-invoke@i5"
    else:
        if len(terms) > max_terms:
            stop = "cap@%d" % max_terms
    if stop == "end-of-list" and visited == max_terms and len(terms) > max_terms:
        stop = "cap@%d" % max_terms
    # gscript.py:2568-2569 -- pop trailing empties
    while em and em[-1]["name"] == "" and em[-1]["wire"] == 0:
        em.pop()
    return [[x["name"], x["wire"]] for x in em if x["name"]], stop


def full_named(terms):
    """What a COMPLETE walk would emit through the same `if t` filter."""
    return [[t["name"], t["wire"]] for t in terms if t["name"]]


# ---------------------------------------------------------------- PART 1 : the 52 shortfalls
out("-" * 92)
out("PART 1 -- reproduce every netmap/nodeterms disagreement  (review section 6 recipe)")
out("-" * 92)

rows = []
n_both = 0
n_agree = 0
n_missing_from_netmap = 0
unnamed_wired_total = 0
by_cause = {}

for dk, dv in sorted(NT["diagrams"].items(), key=lambda kv: int(kv[0])):
    nmd = NM["diagrams"].get(dk)
    for nd in dv["nodes"]:
        uid = nd["uid"]
        terms = nd["terms"]
        unnamed_wired_total += sum(1 for t in terms if t["name"] == "" and t["wire"])
        if not nmd or "nodes" not in nmd:
            continue
        rec = nmd["nodes"].get(str(uid))
        if rec is None:
            n_missing_from_netmap += 1
            continue
        n_both += 1
        actual = [list(x) for x in rec["terms"]]
        full = full_named(terms)
        rep, stop = replay(terms)
        agrees_with_full = (actual == full)
        if agrees_with_full:
            n_agree += 1
            continue
        reproduced = (rep is not None and rep == actual)
        if rep is None:
            cause = "junk-invoke"
        elif not reproduced:
            cause = "unexplained"
        elif stop.startswith("cap@"):
            cause = "cap@40"
        elif stop.startswith("empties"):
            cause = "empties>=3"
        else:
            cause = "unexplained(end-of-list)"
        by_cause[cause] = by_cause.get(cause, 0) + 1
        first_dropped = None
        if rep is not None and len(rep) < len(full):
            first_dropped = full[len(rep)]
        rows.append({
            "diagram": int(dk), "uid": uid, "n_terminals": len(terms),
            "netmap_len": len(actual), "full_named_len": len(full),
            "shortfall": len(full) - len(actual),
            "replay_len": None if rep is None else len(rep),
            "reproduced": reproduced, "stop": stop, "cause": cause,
            "first_dropped": first_dropped,
            "unnamed_terminals": sum(1 for t in terms if t["name"] == ""),
            "unnamed_and_wired": sum(1 for t in terms if t["name"] == "" and t["wire"]),
        })

out("nodes present in BOTH censuses            : %d" % n_both)
out("nodes in nodeterms but NOT in the netmap   : %d" % n_missing_from_netmap)
out("nodes that AGREE (netmap == full `if t`)   : %d" % n_agree)
out("nodes that DISAGREE                        : %d" % len(rows))
out("")
out("per-node table of every disagreement:")
hdr = "%-6s %-7s %-6s %-7s %-7s %-6s %-6s %-16s %-12s" % (
    "dia", "uid", "#term", "netmap", "full", "short", "repro", "stop", "cause")
out("  " + hdr)
out("  " + "-" * len(hdr))
for r in sorted(rows, key=lambda x: (-x["shortfall"], x["uid"])):
    out("  %-6s %-7s %-6s %-7s %-7s %-6s %-6s %-16s %-12s" % (
        r["diagram"], r["uid"], r["n_terminals"], r["netmap_len"], r["full_named_len"],
        r["shortfall"], "yes" if r["reproduced"] else "NO", r["stop"], r["cause"]))
out("")
out("TOTALS PER CAUSE : %s" % json.dumps(by_cause))
out("terminals the `if t` filter drops that ARE WIRED (whole census): %d" % unnamed_wired_total)
out("")

cap_nodes = [r["uid"] for r in rows if r["cause"] == "cap@40"]
emp_nodes = [r["uid"] for r in rows if r["cause"] == "empties>=3"]
unexp = [r for r in rows if r["cause"].startswith("unexplained") or not r["reproduced"]]

gate("G1  P1 nodeterms node count == 626", NT["stats"]["nodes"] == 626,
     "nodes=%d" % NT["stats"]["nodes"])
gate("G2  P2 agree == 574", n_agree == 574, "agree=%d of %d compared (626 in nodeterms)"
     % (n_agree, n_both))
gate("G3  P2 disagree == 52", len(rows) == 52, "disagree=%d" % len(rows))
gate("G4  P4 every disagreement reproduced", len(unexp) == 0,
     "unexplained=%d -> %s" % (len(unexp), [(u["diagram"], u["uid"]) for u in unexp][:10]))
gate("G5  P4 cap@40 holds EXACTLY #637", cap_nodes == [637], "cap@40 nodes=%s" % cap_nodes)
gate("G6  P4 empties>=3 holds the other 51", len(emp_nodes) == 51, "empties>=3 nodes=%d" % len(emp_nodes))
gate("G7  P4 #30804 and #4620 are empties>=3 cases",
     30804 in emp_nodes and 4620 in emp_nodes,
     "30804 in=%s 4620 in=%s" % (30804 in emp_nodes, 4620 in emp_nodes))
out("")

# ---------------------------------------------------------------- PART 2 : #637 re-derived
out("-" * 92)
out("PART 2 -- #637's border RE-DERIVED FROM NODETERMS ONLY (main_vi_nodeterms.json:6424-7131)")
out("-" * 92)

n637 = None
d637 = None
for dk, dv in NT["diagrams"].items():
    for nd in dv["nodes"]:
        if nd["uid"] == 637:
            n637, d637 = nd, int(dk)
t637 = n637["terms"]
nm637 = NM["diagrams"][str(d637)]["nodes"]["637"]["terms"]
unnamed_lo = [t["i"] for t in t637 if t["i"] < MAX_TERMS and t["name"] == ""]

out("#637 sits on nodeterms diagram %d (owner class %r) as node n=%d"
    % (d637, NT["diagrams"][str(d637)]["owner"], n637["n"]))
out("#637 terminals (nodeterms) : %d     netmap array length : %d" % (len(t637), len(nm637)))
out("unnamed terminals inside i0..i39 : %d -> %s" % (len(unnamed_lo), unnamed_lo))
out("arithmetic of the cap: %d - %d = %d" % (MAX_TERMS, len(unnamed_lo), MAX_TERMS - len(unnamed_lo)))
out("")
out("FULL 59-TERMINAL TABLE (index | name | is_source | wire | in netmap?)")
hdr2 = "%-4s %-42s %-8s %-8s %-9s" % ("i", "name", "is_src", "wire", "in netmap")
out("  " + hdr2)
out("  " + "-" * len(hdr2))
nm_pairs = [tuple(x) for x in nm637]
seen = {}
t637_table = []
for t in t637:
    nm_in = ""
    if t["name"]:
        key = (t["name"], t["wire"])
        k = seen.get(key, 0)
        nm_in = "yes" if nm_pairs.count(key) > k else "NO"
        seen[key] = k + 1
    else:
        nm_in = "n/a (`if t`)"
    disp = t["name"].replace("\n", "\\n")
    out("  %-4s %-42s %-8s %-8s %-9s" % (t["i"], repr(disp)[:42], t["is_source"], t["wire"], nm_in))
    t637_table.append({"i": t["i"], "name": t["name"], "is_source": t["is_source"],
                       "wire": t["wire"], "errs": t["errs"], "in_netmap": nm_in})
out("")

EXPECTED_MISSING = [9051, 9000, 9649, 11253, 16421, 29006, 29122, 28392, 29081, 29106, 32583, 32344]
hi = [t for t in t637 if t["i"] >= MAX_TERMS]
hi_wires = [t["wire"] for t in hi if t["wire"]]
d19w = NM["diagrams"][str(d637)]["wires"]
absent = [w for w in EXPECTED_MISSING if str(w) not in d19w]
present_but_claimed = [w for w in EXPECTED_MISSING if str(w) in d19w]
not_on_hi = [w for w in EXPECTED_MISSING if w not in hi_wires]

out("i40..i58 (the CAPPED tail): %d terminals, %d with a non-zero wire" % (len(hi), len(hi_wires)))
out("  i40..i58 wire ends : %s" % hi_wires)
out("  the 12 wires named by the review, absent from netmap diagram %d : %d of 12"
    % (d637, len(absent)))
out("")
out("  REFINEMENT (the review's claim measured exactly): the netmap wires table is keyed by")
out("  wire uid and filled from EVERY node of the diagram, so a wire can be present in it while")
out("  #637's OWN end is missing.  #637 is walk index n=%d on this diagram." % n637["n"])
tail_detail = []
for w in EXPECTED_MISSING:
    ends = d19w.get(str(w))
    has637 = bool(ends) and any(e[0] == n637["n"] for e in ends)
    tail_detail.append({"wire": w, "in_netmap_wires_table": ends is not None,
                        "netmap_ends": ends, "has_637_end": has637})
    out("    wire %-6s in table=%-5s  #637 end present=%-5s  ends=%s"
        % (w, ends is not None, has637, ends))
no_637_end = [d["wire"] for d in tail_detail if not d["has_637_end"]]

# ---- the peer's DISCRIMINATING TEST (archive/peer/2026-09-20-c54-netmap-wires-table-restatement.md
# section 4): "walk-index 4 is #637" was IMPORTED from the other file and assumed, never read.
# sweep_netmap_main.py:62 throws `n` away when it re-keys by uid, so `n` survives only in `wires`.
# Invert diagram 19's wires table into n -> {(t, name)} and match against nodeterms'
# uid -> {(i, name) : i < 40, wire != 0}  (nets gates on `if uid`, i.e. on a NON-ZERO WIRE, not on
# the name -- gscript.py:2570-2572).  Pass criterion: containment picks out exactly one uid per n,
# and n=4 matches uid 637 and nothing else.
out("")
out("  BIJECTION TEST (peer's section 4) -- is netmap `n` the same index space as nodeterms' node order?")
by_n = {}
for w, ends in d19w.items():
    for e in ends:
        by_n.setdefault(e[0], set()).add((e[1], e[2], int(w)))
nt19 = {nd["uid"]: set((t["i"], t["name"], t["wire"])
                       for t in nd["terms"] if t["i"] < MAX_TERMS and t["wire"])
        for nd in NT["diagrams"][str(d637)]["nodes"]}
nt19_order = [nd["uid"] for nd in NT["diagrams"][str(d637)]["nodes"]]
bij = {}
ambiguous = []
for n, s in sorted(by_n.items()):
    cands = [u for u, ts in nt19.items() if s <= ts]
    bij[n] = cands
    if len(cands) != 1:
        ambiguous.append((n, cands))
    out("    n=%-4s ends=%-4s -> candidate uid(s) %s%s"
        % (n, len(s), cands, "" if len(cands) == 1 else "   <-- NOT UNIQUE"))
n4 = bij.get(4, [])
order_ok = all(len(v) == 1 and nt19_order[k] == v[0] for k, v in bij.items() if k < len(nt19_order))
empty_named_ends = sum(1 for ends in d19w.values() for e in ends if e[2] == "")
nm19_wires = set(int(x) for x in d19w)
nt19_wires = set(t for nd in NT["diagrams"][str(d637)]["nodes"] for t in
                 (x["wire"] for x in nd["terms"]) if t)
gate("G12c PEER TEST: netmap `n` resolves to exactly one nodeterms uid",
     not ambiguous, "ambiguous n values: %s" % ambiguous[:6])
gate("G12d PEER TEST: n=4 resolves to uid 637 and nothing else", n4 == [637],
     "n=4 -> %s" % n4)
gate("G12e PEER TEST: every resolved n equals the nodeterms node ORDER at that index",
     order_ok, "bijection matches nodeterms node order on diagram %d" % d637)
out("    FREE COUNTERS the peer asked for:")
out("      netmap diagram %d wire-ends whose NAME is empty : %d  (the `wires` table records"
    % (d637, empty_named_ends))
out("        unnamed-but-wired terminals; the `nodes` table drops them -- DIFFERENT POPULATIONS)")
out("      wires on diagram %d : netmap %d, nodeterms %d; netmap-only %d, nodeterms-only %d"
    % (d637, len(nm19_wires), len(nt19_wires),
       len(nm19_wires - nt19_wires), len(nt19_wires - nm19_wires)))
out("      netmap-only wire uids : %s" % sorted(nm19_wires - nt19_wires))
gate("G8  P3 #637 has 59 terminals", len(t637) == 59, "n=%d" % len(t637))
gate("G9  P3 netmap keeps 28", len(nm637) == 28, "netmap len=%d" % len(nm637))
gate("G10 P3 40 - unnamed(i0..i39) == netmap length",
     MAX_TERMS - len(unnamed_lo) == len(nm637),
     "40-%d=%d vs %d" % (len(unnamed_lo), MAX_TERMS - len(unnamed_lo), len(nm637)))
gate("G11 P5 all 12 named wires sit on i40..i58", not not_on_hi,
     "not on the tail: %s" % not_on_hi)
gate("G12 P5 all 12 absent from the netmap wires table", len(absent) == 12,
     "absent=%d present=%s -- MEASURED REFINEMENT of the review's wording: only %d of the 12 are "
     "absent from the TABLE; the other %d appear there via OTHER nodes of the same diagram"
     % (len(absent), present_but_claimed, len(absent), 12 - len(absent)))
gate("G12b P5 restated: #637's OWN end is missing for all 12", len(no_637_end) == 12,
     "wires with no #637 end in the netmap table: %d of 12 -> %s" % (len(no_637_end), no_637_end))
out("")

# ---------------------------------------------------------------- PART 3 : wire re-derivation
out("-" * 92)
out("PART 3 -- RE-DERIVED from nodeterms: who carries the 17 cut rows' wires, and 4185 / 7506")
out("-" * 92)

# complete wire -> node-terminal index over the WHOLE census
WIDX = {}
for dk, dv in NT["diagrams"].items():
    for nd in dv["nodes"]:
        for t in nd["terms"]:
            if t["wire"]:
                WIDX.setdefault(t["wire"], []).append({
                    "diagram": int(dk), "owner_class": dv["owner"], "node_uid": nd["uid"],
                    "i": t["i"], "name": t["name"], "is_source": t["is_source"]})
out("complete wire index built from nodeterms: %d distinct wire uids over %d diagrams"
    % (len(WIDX), len(NT["diagrams"])))
DIA_686 = d637          # the diagram #637 sits on == Diagram #686 (c53_row_class diagram_index_map)
DIA_639 = 43
out("diagram index %d = Diagram #686 (holds #637) | diagram index %d = Diagram #639 (#637's body)"
    % (DIA_686, DIA_639))
out("")

row_out = []
hdr3 = "%-7s %-3s %-30s %-7s %-22s %-7s" % ("uid", "t", "terminal name", "wire", "action", "carriers")
out("  " + hdr3)
out("  " + "-" * len(hdr3))
for r in RC["table"]:
    w = r["wire"]
    carriers = WIDX.get(w, [])
    others = [c for c in carriers
              if not (c["node_uid"] == r["owner_uid"] and c["i"] == r["terminal_index"])]
    on686 = [c for c in carriers if c["diagram"] == DIA_686]
    src686 = [c for c in on686 if c["is_source"]]
    out("  %-7s %-3s %-30s %-7s %-22s %-7s" % (
        r["owner_uid"], r["terminal_index"], repr(r["terminal_name"].replace("\n", "\\n"))[:30],
        w, r["action_verbatim"], len(carriers)))
    for c in carriers:
        out("        dia %-3s %-18s node #%-7s i%-3s %-8s %s"
            % (c["diagram"], c["owner_class"], c["node_uid"], c["i"],
               "SRC" if c["is_source"] else "sink", repr(c["name"].replace("\n", "\\n"))[:40]))
    row_out.append({
        "owner_uid": r["owner_uid"], "terminal_index": r["terminal_index"],
        "terminal_name": r["terminal_name"], "wire": w,
        "action_verbatim": r["action_verbatim"],
        "carriers": carriers, "other_carriers": len(others),
        "carriers_on_686": on686, "sources_on_686": src686,
    })
out("")

rows_with_src686 = [r for r in row_out if r["sources_on_686"]]
rows_with_any686 = [r for r in row_out if r["carriers_on_686"]]
out("RE-DERIVED COUNTS over the 17 cut rows (complete census):")
out("  rows whose wire is carried by ANY node terminal on Diagram #686 : %d" % len(rows_with_any686))
out("  rows whose wire has a SOURCE node terminal on Diagram #686      : %d" % len(rows_with_src686))
out("  (the struck claim in Pre-decided 38(b) said 0, drawn off the TRUNCATED table)")
out("")

for w in (4185, 7506):
    carr = WIDX.get(w, [])
    on686 = [c for c in carr if c["diagram"] == DIA_686]
    out("wire %d : %d node terminal(s) in the COMPLETE census, %d of them on Diagram #686"
        % (w, len(carr), len(on686)))
    for c in carr:
        out("      dia %-3s %-18s node #%-7s i%-3s %-8s %s"
            % (c["diagram"], c["owner_class"], c["node_uid"], c["i"],
               "SRC" if c["is_source"] else "sink", repr(c["name"].replace("\n", "\\n"))[:40]))
    in_netmap_d19 = str(w) in d19w
    out("      netmap diagram %d wires table carries %d : %s (netmap ends=%s)"
        % (DIA_686, w, in_netmap_d19, d19w.get(str(w))))
out("")
c4185 = WIDX.get(4185, [])
c7506 = WIDX.get(7506, [])
only637_4185 = all(c["node_uid"] == 637 for c in c4185) and bool(c4185)
only637_7506 = all(c["node_uid"] == 637 for c in c7506) and bool(c7506)
gate("G13 4185 is carried by at least one node terminal", bool(c4185),
     "carriers=%d -> %s" % (len(c4185), [(c["node_uid"], c["i"]) for c in c4185]))
gate("G14 7506 is carried by at least one node terminal", bool(c7506),
     "carriers=%d -> %s" % (len(c7506), [(c["node_uid"], c["i"]) for c in c7506]))
gate("G15 no OTHER *NODE TERMINAL* on #686 carries 4185/7506",
     only637_4185 and only637_7506,
     "4185 only-#637=%s  7506 only-#637=%s -- TRUE BUT NOT LICENSED AS A GENERAL NEGATIVE "
     "CLAIM: see G15b" % (only637_4185, only637_7506))
out("")
out("  G15b -- THE SCOPE CORRECTION the peer forced (section 5 of")
out("  archive/peer/2026-09-20-c54-netmap-wires-table-restatement.md).  nodeterms enumerates")
out("  `Node` terminals ONLY.  The S1 census of the same VI counts, alongside Node 626:")
out("  LoopTunnel 132 and ControlTerminal 114, plus shift registers (gscript.py:948: 'Shift")
out("  registers are NOT LoopTunnels ... not covered') and Constants (a GObject, not a Node, so")
out("  Diagram.Nodes[] never returns one).  A wire with exactly ONE endpoint is not a wire:")
out("  4185 and 7506 each have exactly one NODE carrier, so each one's OTHER end is necessarily")
out("  an object class this census does not enumerate.  The answer was already on disk:")
SR1 = json.load(open(os.path.join(B, "main_vi_shiftregs_v1.json"), encoding="utf-8"))
regs = SR1["registers"] if isinstance(SR1, dict) else SR1
sr_hits = []
for r in regs:
    for side, rec in (("right", r), ("left", r.get("left"))):
        if not rec:
            continue
        ow = (rec.get("out") or {}).get("wire")
        if ow in (4185, 7506):
            sr_hits.append({"wire": ow, "side": side, "uid": rec.get("uid"),
                            "class": rec.get("class"), "name": rec.get("name"),
                            "inside_wire": (rec.get("inside") or [{}])[0].get("wire")})
for h in sr_hits:
    out("    wire %-6s <- %-20s #%-6s name=%-12r inside wire %s"
        % (h["wire"], h["class"], h["uid"], h["name"], h["inside_wire"]))
gate("G15b both 4185 and 7506 resolve to a SHIFT REGISTER outer terminal of #637",
     {h["wire"] for h in sr_hits} == {4185, 7506},
     "resolved from main_vi_shiftregs_v1.json (loop_uid=%s): %d hit(s) -- so the missing "
     "endpoint is NOT unmeasured, it is measured in a DIFFERENT file, and the negative claim "
     "'no OTHER object carries this wire' remains UNLICENSED"
     % (SR1.get("loop_uid") if isinstance(SR1, dict) else "?", len(sr_hits)))
carrier_hist = {}
for w, cs in WIDX.items():
    carrier_hist[len(cs)] = carrier_hist.get(len(cs), 0) + 1
one_carrier = sum(1 for cs in WIDX.values() if len(cs) == 1)
out("    carrier-count histogram over all %d wires in the complete census : %s"
    % (len(WIDX), json.dumps({str(k): v for k, v in sorted(carrier_hist.items())})))
out("    wires with exactly ONE node carrier (i.e. whose other end is NOT a Node) : %d of %d"
    % (one_carrier, len(WIDX)))
out("")
out("  ONE MORE READING the peer named and I had not reported: nodeterms diagram '0' holds %d"
    % len(NT["diagrams"]["0"]["nodes"]))
out("  node(s) -- the VI's TOP-LEVEL diagram is reported EMPTY -- and all %d 'mismatches' in the"
    % len(NT["mismatches"]))
out("  census are uid 22963, `net_map`'s own junk Invoke recorded as a node and purged afterwards.")
out("  So 'complete census' is NOT an established property of this file; what IS measured is that")
out("  its node ENUMERATION agrees with the netmap on 626 of 626 nodes.")
out("")

# ---------------------------------------------------------------- PART 4 : the doc
out("-" * 92)
out("PART 4 -- does docs/frame-loop-wire-graph.md carry the re-derived #637 wires?")
out("-" * 92)
doc_path = os.path.join(D, "frame-loop-wire-graph.md")
doc = open(doc_path, encoding="utf-8").read()
doc_ints = set(int(x) for x in re.findall(r"\b\d+\b", doc))
nonzero = sorted({t["wire"] for t in t637 if t["wire"]})
missing_from_doc = [w for w in nonzero if w not in doc_ints]
out("doc generators (grep): stitch_state_carriers.py:24 and stitch_frame_loop_border.py:20 both")
out("  load main_vi_nodeterms.json; NEITHER loads main_vi_netmap.json, and the string 'netmap'")
out("  does not occur in docs/frame-loop-wire-graph.md.  So the doc is NOT netmap-sourced.")
out("#637 distinct non-zero wires (nodeterms) : %d" % len(nonzero))
out("  of those, not printed anywhere in the doc TEXT : %d -> %s"
    % (len(missing_from_doc), missing_from_doc))
out("")
out("EXACT CHECK -- re-run stitch_state_carriers.py:40-45's derivation on the complete 59-row")
out("table and compare to tools/bench/frame_loop_state.json, the artefact the doc section")
out("was rendered from.  That is the only #637-sourced content in the file.")
BJ = json.load(open(os.path.join(B, "frame_loop_border.json"), encoding="utf-8"))
FS = json.load(open(os.path.join(B, "frame_loop_state.json"), encoding="utf-8"))
known_tunnel_outer = {b["outer_wire"] for b in BJ["border"]}
outer = {}
for t in t637:
    if t["wire"] in known_tunnel_outer:
        continue
    o = outer.setdefault(t["name"], {"init": [], "final": []})
    o["final" if t["is_source"] else "init"].append(t["wire"])
doc_rows = {r["name"]: r for r in FS["rows"]}
diffs = []
for nm, o in outer.items():
    r = doc_rows.get(nm)
    if r is None:
        diffs.append({"name": nm, "why": "name absent from frame_loop_state.json",
                      "derived": o})
    elif r["outer_init_wires"] != o["init"] or r["outer_final_wires"] != o["final"]:
        diffs.append({"name": nm, "why": "wire lists differ",
                      "derived": o,
                      "doc": {"init": r["outer_init_wires"], "final": r["outer_final_wires"]}})
out("  #637 terminals excluded as already-named LoopTunnel outer wires : %d of %d"
    % (sum(1 for t in t637 if t["wire"] in known_tunnel_outer), len(t637)))
out("  distinct terminal NAMES on #637 after that exclusion            : %d" % len(outer))
out("  names whose re-derived outer wire lists DIFFER from the doc      : %d" % len(diffs))
for d_ in diffs:
    out("    %r : %s  derived=%s  doc=%s"
        % (d_["name"].replace("\n", "\\n")[:40], d_["why"], d_["derived"], d_.get("doc")))
gate("G16 the doc's #637 outer rows == the complete-census re-derivation",
     not diffs, "differing names=%d (the doc section was already generated from the "
                "COMPLETE nodeterms census, not from the netmap)" % len(diffs))
out("")

# ---------------------------------------------------------------- readings
readings = {
    "generated": "2026-09-20 cycle 54 material",
    "inputs": {
        "nodeterms": "tools/bench/main_vi_nodeterms.json",
        "netmap": "tools/bench/main_vi_netmap.json",
        "row_table": "tools/bench/c53_row_class.json",
        "recipe": "archive/peer/2026-09-20-c53-netmap-terms-truncation.md section 6",
    },
    "mechanism": {
        "cap": "tools/gscript.py:2549  for t in range(max_terms), max_terms=40",
        "empties": "tools/gscript.py:2557-2560  break after 3 consecutive unnamed+unwired",
        "if_t": "tools/bench/sweep_netmap_main.py:63-64  [[t, w] for _ti, t, w in terms if t]",
        "nets_same_loop": "tools/gscript.py:2570-2572  the wires table inherits the truncation",
    },
    "part1": {
        "nodes_in_nodeterms": NT["stats"]["nodes"],
        "nodes_compared": n_both,
        "nodes_only_in_nodeterms": n_missing_from_netmap,
        "agree": n_agree, "disagree": len(rows),
        "by_cause": by_cause,
        "cap_nodes": cap_nodes,
        "empties_nodes": sorted(emp_nodes),
        "unexplained": [(u["diagram"], u["uid"]) for u in unexp],
        "unnamed_and_wired_terminals_whole_census": unnamed_wired_total,
        "table": rows,
    },
    "part2_637": {
        "diagram_index": d637, "n_terminals": len(t637), "netmap_len": len(nm637),
        "unnamed_in_i0_i39": unnamed_lo,
        "tail_i40_i58_wires": hi_wires,
        "review_named_wires": EXPECTED_MISSING,
        "review_named_wires_absent_from_netmap": absent,
        "review_named_wires_tail_detail": tail_detail,
        "review_named_wires_with_no_637_end_in_netmap": no_637_end,
        "bijection_n_to_uid": {str(k): v for k, v in bij.items()},
        "bijection_ambiguous": ambiguous,
        "netmap_d19_ends_with_empty_name": empty_named_ends,
        "d19_wires_netmap_only": sorted(nm19_wires - nt19_wires),
        "d19_wires_nodeterms_only": sorted(nt19_wires - nm19_wires),
        "terminals": t637_table,
    },
    "part3_rederivation": {
        "diagram_686_index": DIA_686, "diagram_639_index": DIA_639,
        "distinct_wires_in_complete_census": len(WIDX),
        "rows": row_out,
        "rows_with_any_carrier_on_686": len(rows_with_any686),
        "rows_with_source_on_686": len(rows_with_src686),
        "wire_4185_carriers": c4185,
        "wire_7506_carriers": c7506,
        "wire_4185_7506_shift_register_ends": sr_hits,
        "carrier_count_histogram": {str(k): v for k, v in sorted(carrier_hist.items())},
        "wires_with_one_node_carrier": one_carrier,
        "scope_limit": "nodeterms enumerates Node terminals ONLY; LoopTunnel / ControlTerminal / "
                       "shift registers / Constants are outside it, so a negative claim of the "
                       "form 'no OTHER object carries this wire' is NOT licensed by this file",
        "nodeterms_diagram_0_nodes": len(NT["diagrams"]["0"]["nodes"]),
        "nodeterms_mismatches": NT["mismatches"],
        "note": "38(b)'s 'sources on #686 = 0' was drawn off the TRUNCATED table; this is the "
                "re-derivation from the complete census, reported at whatever it measures.",
    },
    "part4_doc": {
        "path": "docs/frame-loop-wire-graph.md",
        "n637_nonzero_wires": nonzero,
        "wires_not_printed_in_doc_text": missing_from_doc,
        "doc_reads_netmap": False,
        "outer_map_rederived": {k: v for k, v in outer.items()},
        "differences_vs_frame_loop_state_json": diffs,
    },
    "gates": {"pass": npass, "fail": nfail, "policy": "REPORTED, not required"},
}
with open(os.path.join(B, "replay_netmap_truncation.json"), "w", encoding="utf-8") as f:
    json.dump(readings, f, indent=1, ensure_ascii=False)

out("=" * 92)
out("%d pass / %d fail   (gates REPORTED, not required)" % (npass, nfail))
out("readings -> tools/bench/replay_netmap_truncation.json")
out("=" * 92)
