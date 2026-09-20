# priorart-priorart-moveinto-rev6

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.6594  in 52 / out 39563 / cache-create 173528 / cache-read 3869572  (553s, 35 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (557s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
ONE FILE: tools/recipes/probe_move_into_v0.py, REV 6. FIFTH prior-art round, and intended to be the last.

Round 4 (archive/peer/2026-09-17-priorart-priorart-moveinto-rev5.md) returned exactly ONE finding, B2/B3:
no Invoke snapshot/purge, so gate P4 would fail on the ops' own litter rather than on node loss. ACCEPTED.
REV 6 is that one fix and nothing else: a snapshot after open_panel, a purge + new gate P4a before the count.
The disposition is in that review under '## What was done with it'.

SCOPE, and please respect it: this probe has been reviewed FOUR times and run ONCE (run 1 died in its own
harness at P1, never reaching the question). Four rounds have cost roughly 35 minutes of wall clock. The
project's cycle-10 retrospective costed this exact pattern - review output bought faster than it is disposed -
at 48 min and 28 USD, and named it the cycle's most expensive fault. So: report ONLY a defect that would make
run 2 produce a WRONG ANSWER or NO answer about whether GObject.Move with a wired owner reparents a node, and
a STRUCTURE WITH ITS CONTENTS, into another diagram of the same VI. Everything else - wording, unused names,
extra assertions that would be nice to have, citations that could be fuller - is explicitly out of scope.
If there is no such defect, answer PRIOR-ART: novel and say so in one line.

===================== tools/recipes/probe_move_into_v0.py (REV 6) =====================
r"""probe_move_into_v0.py - D1 phase P: CAN AN EXISTING NODE BE REPARENTED INTO ANOTHER DIAGRAM BY SCRIPT?

THIS IS THE ONE FACT D1 TURNS ON, AND IT HAS NEVER BEEN MEASURED (docs/d1-build-plan.md s1).

REV 4, 2026-09-17, after `archive/peer/2026-09-17-priorart-priorart-loopendref-rev2.md` (File 2: four slugs, all
accepted). Run 1 stopped at gate P1 - not on the question, on the probe's own harness - and the review found a
SECOND harness defect in run 1's own log that rev 3 had left in place. Both are now fixed, and neither cause was
new knowledge: our files already carried it.

  1. `net_map` returned only the FIRST FOUR of `UID to GObject Reference.vi`'s TWELVE terminals, and the
     VI-reference input is named **'Owning VI'**, which the old "'vi' and 'ref' in the name" test could never
     match (log:78-80). The cause is documented: `tools/gscript.py:2352-2355` - the per-terminal walker stops
     after three consecutive empty terminals, and an unassigned connector-pane slot is indistinguishable from the
     end of the list; U2G's conpane has empties at 4-7. `docs/toolkit-capabilities.md:482-485,:23` already marks
     that heuristic SUPERSEDED by `node_terms`/`node_terms_uid`, and `:294` records net_map leaving an op target
     at ExecState 0. Confirmed on the machine by `tools/bench/diag_u2g_terminals.log` (5/5).
  2. The MOVE INVOKE's terminals were keyed by NAME ALONE, and they are duplicated: log:44 shows
     `8:'owner'=w872, 9:'owner'=w0`, and log:46 shows run 1 picking index 9 - the UNWIRED OUTPUT. log:47 is that
     mistake surfacing, so the delete of the old `VI.Block Diagram` owner source never ran. Since
     `gscript.wire()` declines an illegal name-matched connect SILENTLY (`:1149-1152`) and `branch=True` disables
     the count check, run 1 could have produced an `OpMoveIn_v0` whose `owner` was still `VI.Block Diagram`,
     moved both nodes to the TOP LEVEL, and reported P2/P3 FAIL - a FALSE NEGATIVE on the single question D1
     turns on. Remedy adopted here 2026-09-14 and now applied:
     `archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29,:47`,
     `docs/toolkit-capabilities.md:242-244` - key on `(name, is_source)`, never on the name.

So: **net_map and the name-keyed lookup are gone from this file.** Every terminal in every phase is resolved by
`build_track_v6_core.walk()` / `.term(rows, name, is_source)`, new gate **P1a** asserts that `Move.owner` is
actually driven by the Diagram cast before anything is moved, and `owner_of()` carries `read_owner`'s five error
columns and identity echo so an unresolved read cannot masquerade as `owner_uid == 0` on P2/P3. The QUESTION P2/P3
ask is unchanged, and run 1 never reached it.

REV 2 after archive/peer/2026-09-17-priorart-priorart-d1-build.md (findings A1, A6, B1, B2). Rev 1 claimed the
whole relocation question was unexercised. It is not: `tools/recipes/probe_relocate_route.py:10-15` asked it in
2026-09-15 and DELIBERATELY excluded `GObject.Move` with an owner, because `create the loop -> drop the subVI in
it -> wire across the border -> delete the original` works and is now the project's settled method
(docs/decisions.md:19, docs/restructure-plan-4.6.md:79-81 - "GObject.Move is not needed"). That route covers
plain primitives and subVI calls. It does NOT cover a STRUCTURE WITH ITS CONTENTS, and the frame loop's forward
slice contains six of those (#5540 #2222 #12589 #10407 #1359 #29874), for which the fresh-build route is
OpCaseFrames_v0 - which failed five times and must not be retried. THAT, and only that, is what this probe is for.

THE EXCHANGE THAT ALREADY ANSWERED P1's PREMISE, and was cited nowhere in this file until REV 5 (rev4 finding
A4): `archive/peer/2026-08-28-copy-nodes-between-vis.md:23,:43,:47,:53` answers "does `GObject.Move` with a
DESTINATION OWNER reparent across diagrams" with sources, and `:51` is the gotcha `move_in()` below is built
around - **the Move returns NO REFERENCE to the object at its new home**, which is why every check here is a
uid-addressed re-read rather than a returned handle, and `:158` is the cross-VI caveat.
(`docs/d1-build-plan.md:63-64` says of the same question that "neither was cited before" while citing this very
file at :40 and :67 - noted so the next reader is not misled by that sentence.)

The documented route for a wired fragment is `Make Selection` 0x6349002 -> `Copy Selection` 0x6349003 ->
`AbstractDiagram.Paste` 0x6375400 onto the SUBDIAGRAM reference (.claude/skills/labview-automation/references/
vi-scripting.md:323-325; archive/peer/2026-09-13-scripted-diagram-selection.md:143,:162,:166-172, whose forum
citation says explicitly "including contents of a structure frame"). It is a new op family and a separate cycle.
This probe measures the CHEAPER route first because our own `move_out` already contradicts that exchange's
general claim ("GObject.Move is not a cross-VI reparenting method") for the WITHIN-VI case.

WHAT ALREADY EXISTS - checked before writing a line (CLAUDE.md "before creating any new op"):
  * `gscript.move_out()` / `OpMoveOut_v0.vi` (gscript.py:2469, tools/recipes/build_opmoveout.py) already proves
    `GObject.Move` 632A400 with a wired `owner` reparents a node from a NESTED diagram to the VI's TOP-LEVEL
    diagram. Its `owner` is hard-wired to a `VI.Block Diagram` (23C) Property node, which is why it can only ever
    reach the top level. It is the DONOR here, not the answer.
  * `gscript.move_object()` / `OpMove_v0` (gscript.py:2094) moves by POSITION with `owner` UNWIRED = same diagram.
    docs/toolkit-capabilities.md:363-392 records a probe that believed position alone reparented a node and was
    then CORRECTED - "ExecState was already 0 immediately after for_loop". So position-only reparenting is
    unproven and is not assumed here.
  * `copy_by_index()` (gscript.py:1282) copies an object into a target's TOP-LEVEL diagram through the NI Move
    example fixtures and requires the target to be runnable before it saves - it cannot place into a nested
    diagram and cannot relocate inside one VI. Not a route.
  * `UID to GObject Reference.vi` (C:\...\vi.lib\VIServer\) is already used as node 990 of `OpWireSource_v5` and
    by `OpOwnerChain_v1` (tools/recipes/build_opownerchain_v1.py:170) - that is where the UID-addressing comes
    from; nothing is hand-rolled.
  * readers used (REV 4 removed `net_map`): report/report_all/node_terms_uid via `build_track_v6_core.walk`,
    `.term`, `node_labels`, subvis/exec_state/ownerchain via `OpOwnerChain_v1`, `bench_prep.labview_handles`,
    delete_object,
    connect2, wire, drop_subvi, create_control, remove_bad_wires_scripted, loop_in - all in
    docs/toolkit-capabilities.md.
  * `grep -n "move" tools/gscript.py` shows no *move-into-a-diagram* helper. `ls tools/recipes | grep -i move`
    shows build_opmove.py / build_opmovebyindex.py / build_opmoveout.py only.

WHY IT DECIDES D1. The tracking kernel's FORWARD SLICE is 14 nodes (docs/frame-loop-wire-graph.md:45), five of
them structures, plus the reseed case #5540 and two shift registers. D1 rows 1.2/1.7 put those on NEW loops. The
fleet can CREATE a loop inside an existing VI and DROP a subVI in it (probe_migrate_v2 3/3, probe_migrate_v3 5/5)
- it has never MOVED existing code into one. If P2/P3 fail, D1 as specified is not buildable with today's fleet
and that is a judgement-session decision, not a third attempt.

PREDICTION CONTRACT
  P0  the original's md5 is 2a78e17c449cacdaf5da389818526859 before AND after; no original is opened for writing.
  P1  OpMoveIn_v0.vi builds from OpMoveOut_v0.vi (reference <- a UID-addressed GObject; owner <- the existing
      Traverse-"Diagram"[index] cast, i.e. the DESTINATION diagram) and reads ExecState 1.
  P2  on a scratch copy of the original: a PLAIN node (#8885 Multiply, on Diagram 43) moves into the body diagram
      of a While loop freshly created on Diagram 19 - afterwards OpOwnerChain_v1 reads
      8885 -> <new body diagram> -> <new WhileLoop>.
  P3  a STRUCTURE (#12589 CaseStructure, on Diagram 43) moves the same way AND ITS CONTENTS COME WITH IT:
      ownerchain(12589) -> <new body diagram>, and the VI's total Diagram count is unchanged by the move
      (a frame diagram destroyed or orphaned would change it).
  P4  no node is lost: total Node count after both moves == before. ExecState is expected to be 0 (wires were
      cut by the move) and that is NOT a failure; it is reported.
  P5  the scratch copy is deleted in the same run; LabVIEW handle count is recorded before and after.

Any of P1/P2/P3 failing stops the run and reports - no repair pass, no second construction (failure budget).

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/probe_move_into_v0.log \
        -- py -u tools/recipes/probe_move_into_v0.py
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402  - walk()/term(): the (name, is_source) readers, rev2 finding B3-i

ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
CLAUDEDEV = g.CLAUDEDEV
DONOR_OP = os.path.join(CLAUDEDEV, "OpMoveOut_v0.vi")
OPIN = os.path.join(CLAUDEDEV, "OpMoveIn_v0.vi")
U2G = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to GObject Reference.vi"
SCRATCH = os.path.join(CLAUDEDEV, f"SCRATCH_d1move_{int(time.time())}.vi")

FRAME_BODY_UID = 639        # Diagram owned by WhileLoop #637 - the frame loop body
SIBLING_DIAG_UID = 686      # the FlatSequenceFrame diagram that holds #637 itself (main-vi-stop-and-save.md s0)
PLAIN_NODE = 8885           # Multiply, in the kernel's forward slice
STRUCT_NODE = 12589         # CaseStructure, in the kernel's forward slice

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def handles():
    """P5 promises a HANDLE COUNT, and run 1 printed a Korean 'no such task' line instead
    (tools/bench/probe_move_into_v0.log:3) - rev4 finding B3. The reader already exists:
    `tools/bench/bench_prep.py:64-71 labview_handles()`, with `HANDLE_LIMIT` at :61 and the restart policy at
    :111-117, and CLAUDE.md's reference-hygiene rule is stated in terms of that number against the ~31,500
    baseline. The tasklist line is kept as a fallback, clearly marked, so P5 never silently promises a number it
    did not read."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
        from bench_prep import labview_handles          # noqa: E402
        h = labview_handles()
        return f"handles={h} (bench_prep.labview_handles; fresh-instance baseline ~31,500)"
    except Exception as e:
        try:
            import subprocess
            out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe", "/FO", "CSV", "/NH"],
                                 capture_output=True, text=True, timeout=30).stdout
            return f"NO HANDLE COUNT ({str(e)[:60]}); tasklist says: {out.strip()[:100]}"
        except Exception as e2:
            return f"NO HANDLE COUNT ({str(e)[:60]} / {e2})"


# ---------------------------------------------------------------- phase 1: build OpMoveIn_v0
# REV 4, 2026-09-17, after archive/peer/2026-09-17-priorart-priorart-loopendref-rev2.md (File 2: four slugs).
# `net_map` and the name-keyed `find_term()` are GONE from this file. Both were already documented defects:
#   * `tools/gscript.py:2352-2355` - the per-terminal walker stops after three consecutive empty terminals, and an
#     unassigned connector-pane slot looks exactly like the end of the list ("2026-09-07: those truncated the
#     list"). `docs/toolkit-capabilities.md:482-485,:23` marks that heuristic SUPERSEDED by node_terms/
#     node_terms_uid, and `:294` records net_map leaving an op target at ExecState 0. That is why run 1 saw 4 of
#     `UID to GObject Reference.vi`'s 12 terminals (tools/bench/diag_u2g_terminals.log). (A4)
#   * a dict keyed by NAME ALONE keeps the last row of a duplicated name, and this op's terminals ARE duplicated:
#     probe_move_into_v0.log:44 shows `8:'owner'=w872, 9:'owner'=w0` on the Move Invoke, and :46 shows run 1
#     picking index 9 - the UNWIRED OUTPUT side. :47 (`owner wire 0 also touches []`) is that mistake surfacing:
#     the delete of the old `VI.Block Diagram` owner source never ran. `gscript.wire()` declines an illegal but
#     name-matched connect SILENTLY (:1149-1152) and `branch=True` disables the count check, so the run could have
#     produced an OpMoveIn_v0 still owned by `VI.Block Diagram` - moving nodes to the TOP LEVEL and reporting
#     P2/P3 FAIL. That is a FALSE NEGATIVE on the one question D1 turns on. The remedy was adopted here on
#     2026-09-14: archive/peer/2026-09-14-opexitwhile-fail1-duplicate-terminal-names.md:24-29,:47 - "Require
#     `(name, is_source)` and never source-match unless `wire != 0`"; docs/toolkit-capabilities.md:242-244. (B2)
# The helpers that do this correctly already exist and are imported, not re-written (B3-i):
# `build_track_v6_core.walk(target, diagram)` (uid-keyed, via node_terms_uid) and `.term(rows, name, is_source)`.
walk, term = B.walk, B.term


def wire_ends(by, wire, exclude_uid=None):
    """Every terminal carrying `wire`, as (node_uid, term_index, name, is_source). Wire 0 means UNWIRED and can
    never identify anything, so it returns nothing rather than every bare terminal in the VI."""
    if not wire:
        return []
    return [(u, r["i"], r["name"], r["is_source"])
            for u, (_n, _l, rows) in by.items() if u != exclude_uid
            for r in rows if r["wire"] == wire]


def cls_index(target, uid):
    """(class_name, index-within-that-class) for an object uid, from report_all('Node')."""
    for o in g.report_all(target, "Node"):
        if o["uid"] == uid:
            cls = o.get("class") or o.get("Class Name") or ""
            same = [x["uid"] for x in g.report(target, cls)]
            return cls, same.index(uid)
    return None, None


def build_opmovein():
    print("\n=== PHASE 1: build OpMoveIn_v0 from OpMoveOut_v0", flush=True)
    if not os.path.exists(DONOR_OP):
        gate("P1 OpMoveIn_v0 builds", False, f"donor missing: {DONOR_OP}")
        return False
    if os.path.exists(OPIN):
        os.remove(OPIN)
    shutil.copyfile(DONOR_OP, OPIN)
    g.open_panel(OPIN)
    time.sleep(0.5)
    print(f"  donor copy ExecState {g.exec_state(OPIN)}  nodes {g.count(OPIN, 'Node')} "
          f"wires {g.count(OPIN, 'Wire')}", flush=True)

    by = walk(OPIN, 0)
    for u, (n, _l, rows) in sorted(by.items(), key=lambda kv: kv[1][0]):
        print(f"    node[{n}] uid {u}: "
              + ", ".join(f"{r['i']}:{r['name']!r}{'>' if r['is_source'] else '<'}=w{r['wire']}" for r in rows),
              flush=True)

    # THE MOVE INVOKE, and its two SINK terminals - `(name, is_source)`, never name alone (B2).
    mv_uid = next((u for u, (_n, _l, rows) in by.items()
                   if term(rows, "owner", False) and term(rows, "reference", False)), None)
    if mv_uid is None:
        gate("P1 OpMoveIn_v0 builds", False,
             "no node carries both a SINK 'owner' and a SINK 'reference' (the Move Invoke)")
        return False
    mv_rows = by[mv_uid][2]
    owner_row, ref_row = term(mv_rows, "owner", False), term(mv_rows, "reference", False)
    fact(f"Move Invoke uid {mv_uid}: SINK owner = index {owner_row['i']} wire {owner_row['wire']}, "
         f"SINK reference = index {ref_row['i']} wire {ref_row['wire']} "
         f"(all 'owner' rows: {[(r['i'], r['is_source'], r['wire']) for r in mv_rows if r['name'] == 'owner']})")
    owner_wire, ref_wire = owner_row["wire"], ref_row["wire"]
    if not owner_wire:
        gate("P1 OpMoveIn_v0 builds", False,
             "the Move Invoke's SINK `owner` is already unwired - the donor is not OpMoveOut_v0 as recorded")
        return False

    # the node that DRIVES `owner` today is the VI.Block Diagram (23C) property node - delete it
    owner_src = [e for e in wire_ends(by, owner_wire, exclude_uid=mv_uid) if e[3]]
    fact(f"owner wire {owner_wire} is driven by {owner_src}")
    if not owner_src:
        gate("P1 OpMoveIn_v0 builds", False, f"no SOURCE terminal carries the owner wire {owner_wire}")
        return False
    # the Diagram-typed source we WANT is whatever drives the `Nodes[]` property node's `reference`
    nodes_uid = next((u for u, (_n, _l, rows) in by.items()
                      if any(r["name"].startswith("Nodes") for r in rows)), None)
    if nodes_uid is None:
        gate("P1 OpMoveIn_v0 builds", False, "cannot find the Nodes[] property node")
        return False
    nref = term(by[nodes_uid][2], "reference", False)
    diag_wire = nref["wire"] if nref else 0
    diag_src = [e for e in wire_ends(by, diag_wire, exclude_uid=nodes_uid) if e[3]]
    fact(f"Nodes[] uid {nodes_uid}; its SINK reference wire {diag_wire} driven by {diag_src}")
    if not diag_src:
        gate("P1 OpMoveIn_v0 builds", False, "cannot find the Diagram-typed cast that feeds Nodes[]")
        return False
    tmsc_uid, _ti, tmsc_name, _src = diag_src[0]

    # 1) cut the wire that feeds `reference` today (IA_n.element -> Move.reference)
    wl = [o["uid"] for o in g.report_all(OPIN, "Wire")]
    if ref_wire in wl:
        g.delete_object(OPIN, "Wire", wl.index(ref_wire))
        fact(f"deleted wire {ref_wire} (old Move.reference source)")
    # 2) delete the VI.Block Diagram property node that feeds `owner`
    deleted_any = False
    for u, _t, _nm, _s in owner_src:
        c, i = cls_index(OPIN, u)
        if c:
            g.delete_object(OPIN, c, i)
            deleted_any = True
            fact(f"deleted {c}[{i}] uid {u} (old Move.owner source)")
    if not deleted_any:
        gate("P1 OpMoveIn_v0 builds", False,
             "the old `owner` source was never deleted - `owner` would stay bound to VI.Block Diagram and every "
             "move would go to the TOP LEVEL, which is exactly the false negative this gate exists to stop")
        return False
    g.remove_bad_wires_scripted(OPIN)

    # 3) branch the Diagram cast into `owner`. The SINK must be bare first: wiring into an already-wired sink is
    #    the recorded way to break a VI (gscript.py:2206-2207), and a silently declined connect here would leave
    #    `owner` unwired = a move to the top level = a false P2/P3 FAIL.
    by = walk(OPIN, 0)
    orow = term(by[mv_uid][2], "owner", False)
    fact(f"after the deletes, Move.owner SINK wire = {orow['wire']} (0 = bare, required)")
    if orow["wire"]:
        gate("P1 OpMoveIn_v0 builds", False, f"Move.owner is still wired ({orow['wire']}) - refusing to connect")
        return False
    c, i = cls_index(OPIN, tmsc_uid)
    fact(f"Diagram cast uid {tmsc_uid} is {c}[{i}], output terminal {tmsc_name!r}")
    mc, mi = cls_index(OPIN, mv_uid)
    try:
        g.wire(OPIN, c, i, tmsc_name, mc, mi, "owner", branch=True)
        fact("wired Diagram cast -> Move.owner (branch)")
    except Exception as e:
        gate("P1 OpMoveIn_v0 builds", False, f"cast -> owner wire raised: {str(e)[:160]}")
        return False
    by = walk(OPIN, 0)
    orow = term(by[mv_uid][2], "owner", False)
    ends = wire_ends(by, orow["wire"], exclude_uid=mv_uid)
    if not gate("P1a Move.owner is now driven by the Diagram cast, not by VI.Block Diagram",
                bool(orow["wire"]) and any(e[0] == tmsc_uid and e[3] for e in ends),
                f"owner wire {orow['wire']}, its other ends {ends}, wanted source uid {tmsc_uid}"):
        return False

    # 4) drop UID to GObject Reference.vi, feed it the VI reference + a UID control, wire it into `reference`
    sv0 = g.uids(OPIN, "SubVI")
    g.drop_subvi(OPIN, U2G, 0, (300, 1000))
    new_sub = g.new_since(OPIN, "SubVI", sv0)
    if len(new_sub) != 1:
        gate("P1 OpMoveIn_v0 builds", False, f"drop_subvi added {len(new_sub)} subVIs")
        return False
    # REV 3, 2026-09-17, after run 1 failed here (tools/bench/probe_move_into_v0.log:78-80). MEASURED cause, not
    # inferred - tools/bench/diag_u2g_terminals.log: `UID to GObject Reference.vi` has TWELVE connector-pane
    # terminals (`conpane()` on the file itself: 0 'error out', 2 'GObject', 3 'dup Owning VI', 8 'error in (no
    # error)', 10 'UID', 11 'Owning VI'), and `node_terms_uid` on the dropped instance returns all twelve - while
    # `net_map` returned only the FIRST FOUR, which is why the name search found no input at all. The VI-reference
    # input is called **'Owning VI'**, so the old "'vi' and 'ref' in the name" test could never have matched it.
    # Every terminal below is therefore resolved through node_terms_uid, by EXACT name, never through net_map.
    by = walk(OPIN, 0)
    u2g_rec = by.get(new_sub[0]["uid"])
    u2g_n, u2g_rows = (u2g_rec[0], u2g_rec[2]) if u2g_rec else (None, None)
    if u2g_rows is None:
        gate("P1 OpMoveIn_v0 builds", False, "the dropped UID->GObject VI is not visible to walk()")
        return False
    print(f"    U2G node[{u2g_n}] terminals: "
          + ", ".join(f"[{r['i']}]{r['name']!r}{'>' if r['is_source'] else '<'}" for r in u2g_rows), flush=True)
    fact(f"U2G terminals (walk/node_terms_uid): {[(r['i'], r['name'], r['is_source']) for r in u2g_rows]}")
    need = (("Owning VI", False), ("UID", False), ("GObject", True))
    got = {(nm, src): term(u2g_rows, nm, src) for nm, src in need}
    if any(v is None for v in got.values()):
        gate("P1 OpMoveIn_v0 builds", False,
             f"U2G lacks {[k for k, v in got.items() if v is None]} "
             f"(diag_u2g_terminals.log measured all three: UID<10, Owning VI<11, GObject>2)")
        return False
    uid_term = got[("UID", False)]["i"]

    # The VI-reference SOURCE is found by following the wire that already feeds the Traverse node's 'VI Refnum'
    # INPUT (measured: wire 467 on node uid 124, diag_u2g_terminals.log part C) rather than by guessing a node
    # name - the donor's own Open VI Reference is whatever object SOURCES that wire.
    vi_ref_wire = next((term(rows, "VI Refnum", False)["wire"] for _u, (_n, _l, rows) in by.items()
                        if term(rows, "VI Refnum", False) and term(rows, "VI Refnum", False)["wire"]), 0)
    if not vi_ref_wire:
        gate("P1 OpMoveIn_v0 builds", False, "no node has a wired 'VI Refnum' INPUT - cannot find the VI reference")
        return False
    holders = [e for e in wire_ends(by, vi_ref_wire) if e[3]]
    if not holders:
        gate("P1 OpMoveIn_v0 builds", False, f"no SOURCE terminal carries the VI-reference wire {vi_ref_wire}")
        return False
    holder = (holders[0][0], holders[0][2])
    fact(f"VI reference wire {vi_ref_wire}; its source terminal is {holder[1]!r} of node uid {holder[0]}")
    oc, oi = cls_index(OPIN, holder[0])
    uc, ui = cls_index(OPIN, new_sub[0]["uid"])
    try:
        g.wire(OPIN, oc, oi, holder[1], uc, ui, "Owning VI", branch=True)
        fact("wired the VI reference -> U2G 'Owning VI' (branch)")
    except Exception as e:
        gate("P1 OpMoveIn_v0 builds", False, f"VI reference -> U2G wire raised: {str(e)[:160]}")
        return False
    new_ctl, lab = g.create_control(OPIN, u2g_n, uid_term)
    fact(f"UID control created: {lab!r} ({[o['uid'] for o in new_ctl]})")
    try:
        g.wire(OPIN, uc, ui, "GObject", mc, mi, "reference")
        fact("wired U2G 'GObject' -> Move.reference")
    except Exception as e:
        gate("P1 OpMoveIn_v0 builds", False, f"U2G -> Move.reference wire raised: {str(e)[:160]}")
        return False

    g.set_auto_error_handling(OPIN, False)
    es = g.exec_state(OPIN)
    if es != 1:
        g.remove_bad_wires_scripted(OPIN)
        es = g.exec_state(OPIN)
    if not gate("P1 OpMoveIn_v0 builds and is runnable", es == 1, f"ExecState {es}"):
        return False
    g.save(OPIN)
    fact(f"OpMoveIn_v0 saved; UID control label {lab!r}")
    return lab


# ---------------------------------------------------------------- the op wrapper
def move_in(target, node_uid, dest_diagram_index, position, uid_label):
    g.ensure_loaded(target)
    vi = g.op(OPIN)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", int(dest_diagram_index))
    vi.SetControlValue("index 2", 0)
    vi.SetControlValue("index 3", 0)
    vi.SetControlValue("error in (no error)", (False, 0, ""))
    vi.SetControlValue("error in", (True, 1, "neutralised creator"))
    vi.SetControlValue("Class Name 3", "")
    vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue(uid_label, int(node_uid))
    vi.SetControlValue("position", tuple(int(v) for v in position))
    g._run(vi)
    return int(vi.GetControlValue("UID"))


def diag_index(target, uid):
    return [o["uid"] for o in g.report_all(target, "Diagram")].index(uid)


OWNER_OP = os.path.join(CLAUDEDEV, "OpOwnerChain_v1.vi")
OWNER_LABELS = os.path.join(ROOT, "tools", "bench", "opwiresource_v5_labels.json")
_OL = None


def owner_read(target, uid):
    """The FULL read of `read_owner()` (tools/recipes/build_opownerchain_v1.py:246-279), target path parameterised.

    REV 4 (rev2 finding B3-ii): the earlier version kept the poisoning but returned only (class, uid), so a
    property read that ERRORED and a move that genuinely FAILED both surfaced as `owner_uid == 0` - on P2/P3, the
    two gates this whole probe exists to decide. The five error columns and the `uid_back`/`cls_back` identity
    cross-check are what separate "wrong owner" from "wrong object" without another run
    (build_opownerchain_v1.py:247-248,:268-269,:274-275), and
    archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:29 requires that check on EVERY
    read. They are restored here."""
    global _OL
    if _OL is None:
        import json
        with open(OWNER_LABELS, encoding="utf-8") as f:
            _OL = json.load(f)
    lab = _OL
    vi = g.op(OWNER_OP)
    for k in (lab["ownercls"], "Class Name 3", lab["cast_class"], lab["cls_back"]):
        try:
            vi.SetControlValue(k, "POISON")
        except Exception:
            pass
    for k in (lab["owner_uid"], lab["uid_back"]):
        try:
            vi.SetControlValue(k, 0)
        except Exception:
            pass
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", 0)
    vi.SetControlValue(lab["uid_in"], int(uid))
    vi.SetControlValue(lab["term_index"], 0)
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:100]}"
    errs = " ".join(x for x in (g._err(vi, lab[k]) or ""
                                for k in ("errL", "errT", "errO", "errU", "errG")) if x)
    out = dict(uid=int(uid), ownercls=vi.GetControlValue(lab["ownercls"]),
               owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
               uid_back=int(vi.GetControlValue(lab["uid_back"])),
               cls_back=vi.GetControlValue(lab["cls_back"]),
               cast_class=vi.GetControlValue(lab["cast_class"]), err=err, errs=errs)
    print(f"  OBSERVED uid {out['uid']} -> owner {out['ownercls']!r}#{out['owner_uid']} | "
          f"self {out['cls_back']!r}#{out['uid_back']} | cast {out['cast_class']!r} "
          f"| {out['err'][:40]} {out['errs'][:60]}", flush=True)
    return out


def owner_of(target, uid):
    """(owner class, owner uid), but ONLY when the op actually resolved the object asked about: a read whose
    identity echo does not come back as `uid` is not an answer, and is raised rather than returned as 0."""
    r = owner_read(target, uid)
    if r["uid_back"] != int(uid) or r["errs"]:
        raise RuntimeError(f"owner_of({uid}) is not an answer: self-read echoed {r['cls_back']!r}#{r['uid_back']}, "
                           f"errors {r['errs'][:120]!r} {r['err'][:60]!r}")
    return r["ownercls"], r["owner_uid"]


# ---------------------------------------------------------------- phase 2: the real question
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    m0 = md5(ORIGINAL)
    gate("P0a original md5 before", m0 == ORIG_MD5, m0)
    if m0 != ORIG_MD5:
        return 1
    print(f"  handles/tasklist before: {handles()}", flush=True)

    uid_label = build_opmovein()
    if not uid_label:
        print("\nSTOP after phase 1 (failure budget: no repair pass).", flush=True)
        return 1

    print("\n=== PHASE 2: move real nodes of the frame loop into a new sibling While loop", flush=True)
    shutil.copy2(ORIGINAL, SCRATCH)
    try:
        g.open_panel(SCRATCH)
        # REV 6 (rev5 finding B2/B3): SNAPSHOT THE Invoke NODES. `OpMoveIn_v0` is a byte copy of `OpMoveOut_v0`,
        # which build_opmoveout.py:11 builds from the `OpNetInfo_v1` family - it carries the erdosmiller
        # `Create Invoke Node.vi` creator, and gscript.py:2471-2472 says in so many words that `move_out()`
        # "leaves the op's junk Invoke on the target", one per run. docs/keystone-op-spec.md:567-573 s33 makes the
        # purge a PROTOCOL and docs/NAMES.md:307-313 records THREE recipe runs broken by skipping it (an Invoke
        # with an unwired `reference` makes a VI non-executable and Remove Bad Wires reports nothing). Invoke
        # counts under `Node` (NAMES.md:315-320), so without this the two `move_in` calls would leave
        # n_before + 3 and gate P4's `n_before + 1` would FAIL for a reason that has nothing to do with
        # reparenting - on run 2 of a failure budget of 2, in a log bgrun now scores rc=1.
        # And the trap is specifically this rev: run 1 was purged by ACCIDENT, because net_map purges as a side
        # effect ("153 junk Invoke(s) purged" in its own log), and REV 4 removed net_map. Exactly what
        # build_opownerchain_v1.py:231-243 warns: "removing net_map removed the purge with it."
        inv0_s = g.uids(SCRATCH, "Invoke")
        n_before = g.count(SCRATCH, "Node")
        d_before = g.count(SCRATCH, "Diagram")
        es0 = g.exec_state(SCRATCH)
        fact(f"scratch copy: Node {n_before}, Diagram {d_before}, ExecState {es0}")

        sib_i = diag_index(SCRATCH, SIBLING_DIAG_UID)
        fact(f"Diagram#{SIBLING_DIAG_UID} (holder of WhileLoop#637) is Traverse index {sib_i}")
        dg0 = g.uids(SCRATCH, "Diagram")
        wl0 = g.uids(SCRATCH, "WhileLoop")
        g.loop_in("while", SCRATCH, sib_i, (2600, 2600))
        new_dg = g.new_since(SCRATCH, "Diagram", dg0)
        new_wl = g.new_since(SCRATCH, "WhileLoop", wl0)
        if not gate("P2a a While loop was created on the sibling diagram",
                    len(new_dg) == 1 and len(new_wl) == 1,
                    f"+{len(new_dg)} diagrams, +{len(new_wl)} while loops"):
            return 1
        body_uid = new_dg[0]["uid"]
        loop_uid = new_wl[0]["uid"]
        # REV 5 (rev4 finding B2): the destination index comes from **new_since's own `i`**, the index the
        # creating op reported, not from a position in a whole-VI `report_all` listing. docs/NAMES.md:511-534
        # records three runs burned on exactly that derivation and states the remedy twice - use new_since's `i`,
        # and "verify by listing that diagram's contents, never by a whole-VI count"; see also
        # archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:28-30 and
        # docs/d1-build-plan.md:45. An index silently off by one moves the nodes into SOME OTHER diagram and
        # P2/P3 then report a false FAIL on the one question D1 turns on.
        body_i = new_dg[0].get("i", diag_index(SCRATCH, body_uid))
        fact(f"new WhileLoop uid {loop_uid}, body Diagram uid {body_uid} at Traverse index {body_i} "
             f"(from new_since; report_all would say {diag_index(SCRATCH, body_uid)})")

        # ---- P2: a plain node (CONTROL ARM - the settled route already covers this; a failure here means the
        #      probe is broken, not the capability. docs/toolkit-capabilities.md:200-214.)
        r = move_in(SCRATCH, PLAIN_NODE, body_i, (60, 60), uid_label)
        p2_ok = False
        try:
            oc, ou = owner_of(SCRATCH, PLAIN_NODE)
            oc2, ou2 = owner_of(SCRATCH, ou) if ou else (None, None)
            p2_ok = gate("P2 a PLAIN node reparents into the new loop body",
                         ou == body_uid and ou2 == loop_uid,
                         f"move returned {r}; owner({PLAIN_NODE}) = {oc}#{ou} (want Diagram#{body_uid}); "
                         f"owner(owner) = {oc2}#{ou2} (want WhileLoop#{loop_uid})")
        except Exception as e:
            # an UNRESOLVED read is not a negative result about reparenting - it is no result (rev2 B3-ii)
            gate("P2 a PLAIN node reparents into the new loop body", False, f"UNRESOLVED READ: {str(e)[:220]}")
        if not p2_ok:
            # THE CONTROL ARM FAILING MAKES THE RUN INVALID, AND THE RUN MUST STOP (rev4 finding A3; this file's
            # own :90, docs/d1-build-plan.md:126-127 "INVALID, conclude nothing"). P3's verdict on a probe whose
            # control arm did not work says nothing about reparenting, and printing it invites exactly the
            # false negative rev2 B2 was about.
            print("\nSTOP: the CONTROL ARM failed, so this run is INVALID - P3 is not attempted and nothing is "
                  "concluded about relocating a structure.", flush=True)
            return 1

        # ---- P3: a structure, with its contents  <- THE QUESTION
        d_mid = g.count(SCRATCH, "Diagram")
        # IDENTITY GATE on the destination before the second mutation: list that diagram's contents and require
        # the node P2 just moved to be on it (docs/NAMES.md:511-534, "verify by listing that diagram's contents").
        try:
            body_rows = g.node_labels(SCRATCH, body_i)
            on_body = [r_["uid"] for r_ in body_rows]
        except Exception as e:
            on_body = f"<node_labels: {str(e)[:80]}>"
        if not gate("P2b the destination index still names the diagram that received the plain node",
                    isinstance(on_body, list) and PLAIN_NODE in on_body,
                    f"Diagram[{body_i}] (uid {body_uid}) holds {on_body}"):
            print("\nSTOP: the destination Traverse index no longer identifies the new loop body - moving again "
                  "would write into an unknown diagram.", flush=True)
            return 1
        r2 = move_in(SCRATCH, STRUCT_NODE, body_i, (60, 400), uid_label)
        d_after = g.count(SCRATCH, "Diagram")
        try:
            oc3, ou3 = owner_of(SCRATCH, STRUCT_NODE)
            gate("P3 a STRUCTURE reparents AND keeps its frame diagrams",
                 ou3 == body_uid and d_after == d_mid,
                 f"move returned {r2}; owner({STRUCT_NODE}) = {oc3}#{ou3} (want Diagram#{body_uid}); "
                 f"Diagram count {d_mid} -> {d_after}")
            # The rev2 review's optional upgrade - assert each frame diagram still names the moved structure as
            # its owner (docs/diagram-hierarchy.md:85,:92) - is NOT run here, and the reason is cost, not doubt:
            # it needs `owner_read` per Diagram, and this target carries ~170 of them at ~1 s per op run. The
            # frame uids of #12589 are not in any file we hold, so there is no cheap subset to check. The gate
            # therefore stays the Diagram-count invariant of docs/d1-build-plan.md:128-129, and the frame-owner
            # test belongs to whichever build actually relocates the six structures.
            fact(f"per-frame owner re-check for #{STRUCT_NODE} deliberately not run (~170 Diagram reads); "
                 f"P3's evidence is the Diagram-count invariant {d_mid} -> {d_after}")
        except Exception as e:
            gate("P3 a STRUCTURE reparents AND keeps its frame diagrams", False,
                 f"UNRESOLVED READ: {str(e)[:220]}; Diagram count {d_mid} -> {d_after}")

        # ---- P4: nothing lost. Purge the ops' own litter FIRST, otherwise this gate measures the creator, not
        #      the moves. Same shape as build_opownerchain_v1.py:231-243 / fix_v3_starting_xy.py:17-26.
        junk = g.new_since(SCRATCH, "Invoke", inv0_s)
        for o in junk:
            ids = [x["uid"] for x in g.report(SCRATCH, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(SCRATCH, "Invoke", ids.index(o["uid"]), verify=False)
        fact(f"purged {len(junk)} junk Invoke node(s) left by the two move_in runs: {[o['uid'] for o in junk]}")
        g.remove_bad_wires_scripted(SCRATCH)
        left = g.new_since(SCRATCH, "Invoke", inv0_s)
        gate("P4a the ops' junk Invokes are all gone before the node count", not left, f"still present {left}")
        n_after = g.count(SCRATCH, "Node")
        es1 = g.exec_state(SCRATCH)
        gate("P4 no node lost by the two moves", n_after == n_before + 1,   # +1 = the new While loop node
             f"Node {n_before} -> {n_after}; ExecState now {es1} (0 expected: wires were cut)")
        fact(f"ExecState after the moves and Remove Bad Wires: {es1}")
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("  scratch deleted", flush=True)
            except Exception as e:
                print(f"  scratch NOT deleted: {e}", flush=True)
        m1 = md5(ORIGINAL)
        gate("P0b original md5 after", m1 == ORIG_MD5, m1)
        print(f"  handles/tasklist after: {handles()}", flush=True)

    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== probe_move_into_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Narrative relocated **verbatim** (rule 4): cycle 11??3 ??`archive/2026-09-16-status-cycles-11-13-narrative.md`;
D0 (15??8), the GPU numbers, the lock history and the long OPEN forms ??**`archive/2026-09-17-status-d0-and-gpu-narrative.md`** (STATUS was 268 lines). Open one only when a line here is ambiguous.
?좑툘 **ONE SESSION AT A TIME** (two ran concurrently on 2026-09-16) ??**re-read `CLAUDE.md` and this from disk**.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`cycle10-plan.md` superseded = its Phase A); settled decisions
   **`docs/decisions.md`**; current cycle plan `docs/cycle14-plan.md`.
2. ??**Prior-art gate live, hole fixed** ??`guard_cycle.py` accepts `REFUTED:` and `FIXED: <slug> - <path>:<line> - <what>`.
3. ??**Retrospectives 10??3 done/disposed**; `retrospective.py` **v2** fixes slug saturation (`tools/bench/retro_v2_comparison.md`).
4. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** (not "diagram loaded" ??refuted); fixed by `ensure_loaded()` in `tools/gscript.py`, 26 mutating wrappers.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-d1-preconditions
  since: 2026-09-17 03:5x
  purpose: probe_move_into_v0 on a SCRATCH COPY, then build OpLoopEndRef_v0 and read WhileLoop#637's
    conditional terminal on the MAIN VI read-only. Original md5 2a78e17c449... asserted before and after.
# 2026-09-17 03:0x-04:0x material/cycle15-d1-build: **NO LabVIEW was ever started** - the D1 phase-P probe was
# written and gated but never ran (guard_cycle: violations due). Original md5 verified 2a78e17c449... untouched.
# 2026-09-17 material/gpu-n1-localise: NO LabVIEW touched (DLL + recorded files only, ctypes; no COM anywhere in
# the import chain) - gates G0a/G0b assert tasklist shows no LabVIEW.exe at start and at end.
# Holder history (cycle15 D0 v1/v2/v3, md5s, scratch copies created+deleted, TIFFs written+deleted, GUI action
# counts): archive/2026-09-17-status-d0-and-gpu-narrative.md 짠1. Earlier: the 2026-09-16 narrative archive.
```
**Never assume an instance exited** (pid 14352 did not): `tasklist | grep -i labview`, kill strays. Fresh instances
??1,500 handles; unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change**; never infer one, never
ask per incident inside a declared state. Instruments: rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024,
offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure**, so the
acquisition loop applies the contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**;
fixture work unaffected (10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand
**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` / `instrument-libraries` / `frame-loop-wire-graph` /
`rotor-sign-diagnosis` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS** (`docs/stage2-plan.md`): `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi`
162/162. **Say it exactly:** bit-identical to the reference for the **first 10,018 frames only** (before the first
bead loss), and both are **replay** artefacts ??recorded TIFFs, `FOR` loops, no acquisition, no stop protocol.
**THE GAP (outcome review):** 168 op VIs, 116 recipes, 217 peer exchanges ??two replay VIs, **zero runnable
experimental VIs**.

## OPEN ??one line each; the long form is in the narrative archives

1. ?윞 **PERIODIC auto-reset not gated by `Auto-Reset` at the wire level** (`ForLoop#1359`, 10 terminals, 0 panel sources); one `Value` read inside #1359 closes it. ??2026-09-16 archive, OPEN 1.
2. ?윟 **Autofocus CLOSED** ??`Auto-Focus` uid 24266 stops the piezo; `CaseStructure #10407` every 25 frames ??3.6 Hz.
2c. ?윟 **uid 9775 READS camera geometry** (the size written is the panel display area, not the ROI) ??the 1280횞1024 budget basis is safe. Residual: `Property Items[] ??Is Write` over the 106 Property nodes.
3. ?윞 **Peer-archive dispositions** ??39 pre-09-15 `legacy`; **27 are real debt** (L6); L1: 64/336 docs lack frontmatter.
5. **Startup drives instruments** (ASI diagrams 10/88, PI 1/3/4/5 ??`main-vi-startup.md:22-33`): fine while apart, a hard blocker at assembly; excise node-by-node (rule 1a).
6??. ??RESOLVED ??bgrun regex, REVIEW-log scan skip, `premature-build`/`scope-creep` devices. 4. `Global motor pos.vi` write-only; **user: keep it**.
9. ?윟 **A2 DONE** ??owner semantics, six structure classes (54/54); `FlatSequence` the exception (owner uid 0, error 1055). `docs/diagram-hierarchy.md`.
10. ?윟 **A3 MEASURED for the 112 clean diagrams** (100 agree / 0 disagree); left: the 57 `FlatSequenceFrame` diagrams, reachable via `FlatSequence.Diagrams[]` **3578BC00**. ?윞 Needs ONE new op VI ??judgement call.
11??2. ??**Retrospective v2 ADOPTED** (A?밇 closed, `violations.py --due` empty rc=0); **doc lint + ingest BUILT**, but
   MEASURED 2026-09-17: **2 fail / 4 warn / 3 pass** ???뵶 L4 *two* `current` cycle plans (14 + 15) and L6 27 undisposed
   reviews; the "1 fail/3 warn/5 pass" figure is stale. ??archive 짠2.
13. ??**CLOSED 2026-09-17 ??the reader was BUILT and the stop is MEASURED.** `OpLoopEndRef_v0.vi`
   (`WhileLoop.Loop End Ref` **6362C00**, short name `LpEndRef`, id now verified on this machine) reads
   **#637 ??conditional terminal uid 648 ??wire 3457 ??source `CompoundArithmetic` #11639** = `stop (end)` uid 7
   OR-ed, all inside `Diagram#639`. `stop (end) 2` #19587 ??#17883 ??`Tunnel#22085` of `CaseStructure#22082` is a
   SEPARATE path. 16/16, MAIN md5 unchanged (`tools/bench/build_oploopendref_v0.log`, `loopendref_637.json`);
   also #25380??5410/1737 and #15173??5276/19456. ??`docs/main-vi-stop-and-save.md` 짠1. **This is D1's S4 gate.**
14. ?뵶 **The cycle-15 prior-art review is only PARTLY disposed** ??A1/A2 `settled-already`, A3?밃6/B2 `contradicted`,
   A7/B3 `unread-evidence` BLOCK on purpose (D1's method vs `decisions.md:19`; `SubVI.Replace` 635E001 unverified).
   **Only a judgement session may refute or fix those.** ??archive 짠2.
15. ??**`bgrun.py --detach` BUILT and MEASURED** (deadline + END/TIMEOUT survive detachment; `BGRUN KILL` line;
   detached stdout ??the log). 15b. ?뵶 **its deadline kill does NOT kill an ORPHANED grandchild**
   (`detach_canary.log`) ??pre-existing; the Job-Object fix is a **judgement call**. ??archive 짠3.
16. ?뵢 **GPU N1, full fixture: max |?x| 4.13e-06 px 쨌 |?y| 3.13e-05 px 쨌 |?z| 1.28e-05 쨉m 쨌 1 flip** vs acceptance
   `decisions.md:38` (x,y ??1e-6, 0 flips) ??**x/y and the flip are OUTSIDE it**. **LOCALISED 2026-09-17**
   (`docs/gpu-backend.md` 짠2026-09-17, raw `tools/bench/gpu_n1_deltas.json`, 8/8 gates): every x/y exceedance is
   **bead 4 on 10 frames of f11805?밼11823**, in the all-beads-lost tail, interleaving the 13 recorded lost rows;
   **over the first 10,018 frames max |?x| 4.86e-07 쨌 |?y| 4.68e-07 쨌 0 exceedances**; the flip is k1679/f1937
   bead 4, one cal slice (?z 4.7 nm); **two runs bit-identical**. ?뵶 **Acceptability is a JUDGEMENT call.**
17. ??**D0 CLOSED ??the original's full unattended cycle RAN, 16 pass / 0 fail** (`drive_original_copy_v3.py`,
   HWND-gated clickprobe, `SetControlValue` stop ??idle in 2 s, `tra001-000` written, md5 unchanged). ??archive 짠5.
17b. ?뵶 **v3's R11 never gated on the stop** ??`rec(..., left2, ...)` (`drive_original_copy_v3.py:415-418`) scores the
   *restart*, and `reset_controls()` runs only at line 248, so "stop works only in the frame loop" is **UNPROVEN**
   (peer `??026-09-17-d0v3-stop-heuristic.md`, ANSWERED, adopted). Next D0 step is its VI-Server-only test: stops
   `False` + readback ??restart ??one `True` each ??poll values + `ExecState`.
19. ?뵶 **D1 REV 2 (`docs/d1-build-plan.md`) is written and prior-art-reviewed; the build did NOT start.**
   `archive/peer/2026-09-17-priorart-priorart-d1-build.md` ??**10 findings, 0 novel, all accepted and disposed**
   (`FIXED:` 횞6). The two that change the cycle: **(A1+A6)** relocating a plain primitive or a subVI call is the
   *settled* route (`decisions.md:19`, `restructure-plan-4.6.md:79-81`, and `tools/recipes/probe_relocate_route.py`
   asked this in cycle 8) ??so D1's ONLY real unknown is **relocating a STRUCTURE WITH ITS CONTENTS**
   (`#5540 #2222 #12589 #10407 #1359 #29874`), whose documented route is `Make Selection` 0x6349002 ??
   `Copy Selection` 0x6349003 ??`AbstractDiagram.Paste` 0x6375400 (`vi-scripting.md:323-325`) and **has never been
   run here**; **(A4)** `#10407` (autofocus) is in the kernel's forward slice and **neither placement is legal** ??
   tracking loop = VISA on a path whose stall makes acquisition skip reads (rule 1c / `decisions.md:30`),
   acquisition loop = its input no longer exists. ?뵶 **JUDGEMENT.** Also A5 (writer must STREAM, not relocate the
   accumulator), A3 (`#11639` AND `#17883` are two nodes; `CaseStructure#22082` unplaced), A2 (row 1.7 before the
   per-frame measurement `decisions.md:46,:52`). Probe written, gated, unrun: `tools/recipes/probe_move_into_v0.py`.
21. ??**Round-5 devices BOTH BUILT 2026-09-17** (`docs/violation-decisions.md` 03:38). (a) `device-failed`:
   `tools/bgrun.py` now scans build/diagnostic logs for `^\s*(?:->\s*)?FAIL\b` and forces rc=1 ??
   `tools/bench/selftest_bgrun_fail_scan.log` **7/7**, incl. the literal `diag_stop_condterm_panel.log:15-19`
   lines ending rc=1 where they used to end rc=0, a PASS-only log still rc=0, `FAILED`/`FAILURE`/`failures` not
   tripping it, and a `peer_*.log` still exempt via logclass. (b) `repeated-failure-class`: `OpLoopEndRef_v0`,
   OPEN 13 above.
20. ?뵶 **Cycle 14's retrospective ran** (`archive/peer/2026-09-17-retrospective-cycle14.md`, ANSWERED) and left
   **two slugs DUE, which now BLOCK every recipe build**: `repeated-failure-class` 7/3 (the 2026-09-16 disposition
   gate **failed at its in-flight edge**) and `device-failed` 1/1 (the `unreported-fact` runner-exit device let
   `diag_stop_condterm_panel.log:15-18` end **rc=0 with a failed gate**). Each needs a dated `DECISION:` block in
   `docs/violation-decisions.md`. Its finding 7 also flags *judgement taken inside material sessions*.
18. ?뵶 **The original saves EVERY FRAME as a 1.3 MB TIFF** (`IMAQ Write TIFF File 2` #22700, diagram 43) ??
   **~118 MB/s at 90 Hz**. Any unattended overnight harness must bound this or the disk fills in minutes.

## NEXT

?윟 **Slug block cleared** (`violations.py --due` empty, rc=0); the **OUTCOME REVIEW is RUN and disposed**
(`archive/peer/2026-09-16-outcome-review-20260916.md`, ANSWERED, **7 OUTCOME-VIOLATION slugs**).
?뵶 **BLOCKING, in order:** (1) the two DUE slugs of OPEN 20 ??`py tools/violations.py --due` rc=1; (2) OPEN 19's
three D1 design calls (`#10407`'s loop 쨌 streaming writer vs `.tra` format 쨌 row 1.7 before the p50/p99 measurement).
Then Phase P: `MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/probe_move_into_v0.log -- py -u
tools/recipes/probe_move_into_v0.py` (builds `OpMoveIn_v0`, control arm `#8885`, real question `#12589`).
?뵶 **Earlier JUDGEMENT item:** CLAUDE.md turns that into a **delivery** cycle, contradicting
`docs/cycle14-plan.md` (짠3 `Diagrams[]` op, 짠4 A3 ??170/170, 짠5 OPEN 1's read, 짠6 A4). Queued second: **is item
16's GPU divergence acceptable**, on the 2026-09-17 localisation.

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
`docs/restructure-plan-4.6.md` target 쨌 `docs/pre-rig-master-plan.md` the plan 쨌 `docs/diagram-hierarchy.md` A2/A3 쨌
`docs/gpu-backend.md` GPU 쨌 narrative: the 2026-09-17 and 2026-09-16 status archives 쨌 `archive/` history (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled in this session, so the review is below in full.

# PRIOR-ART REVIEW — `tools/recipes/probe_move_into_v0.py` REV 6 (round 5, trigger: new-op)

Scope honoured: only a defect that would make **run 2** give a WRONG or NO answer about whether `GObject.Move` with a wired `owner` reparents a node — and a structure with its contents — into another diagram of the same VI. Nothing run, no lock taken, no project file touched.

## PART A — THE DIRECTION

**Nothing blocks.** A1/A2/A3/A4 are unchanged from round 4's clearance and I re-checked the three that could have moved: `docs/d1-build-plan.md:56` still lists the six structures as the open unknown; `tools/recipes/probe_relocate_route.py:10-15` still excludes `GObject.Move` with an owner deliberately; the `632A400` / `GObject.Move` sweep across `docs/`, `archive/` and `tools/bench/` turns up no exchange or log beyond the ones this file already cites.

## PART B — THE ARTIFACT

**No slug.** Round 4's B2/B3 is discharged, and discharged the documented way rather than by an invented shape:

- The snapshot-after-`open_panel` + purge-before-the-count + assert-none-left sequence is literally the rule at `docs/NAMES.md:312-313` and the protocol at `docs/keystone-op-spec.md:567-573` §33.
- The four lines are the shape already in `tools/recipes/build_opownerchain_v1.py:231-243` and `tools/recipes/fix_v3_starting_xy.py:17-26`. Re-reading `g.report(SCRATCH,"Invoke")` inside the loop makes index-shift-after-delete moot (`gscript.subvis(..., purge=True)` at `tools/gscript.py:368-380` solves it the other way, by reverse order — either is correct).
- `verify=False` is used the only way its own docstring permits, *"only with a snapshot around the batch"* (`tools/gscript.py:2042-2048`); **P4a is that snapshot**.
- `new_since` compares uids (`tools/gscript.py:838`) against a uid set (`:827`), so the main VI's one pre-existing Invoke (`docs/NAMES.md:320`, census row `Invoke 1`) and anything inside `#12589` cannot be purged by mistake.

## Checked and cleared — so round 6 does not re-derive it

1. **Phase 1 (`OPIN`) does not need the same purge.** `docs/NAMES.md:309-310` names `OpCreateControl` as a creator-carrier, which would break P1's `ExecState == 1`. Functionally refuted by a later build: `tools/recipes/build_track_v6_core.py:148,:211,:222` calls `create_control` with **no Invoke snapshot in the file**, and that build is the 69/69 `Track_v6_CPU_core_v0.vi`. `create_control` now drives `OpCreateControl_v1.vi` (`tools/gscript.py:2143`); `walk`/`node_terms` are explicitly 0-junk (`tools/gscript.py:683`). REV 4's removal of `net_map` cost the purge only on the phase-2 target — the one REV 6 fixed.
2. **`sib_i` is a legitimate Traverse index.** `diag_index` reads `report_all`, whose rows are Traverse order and verified identical to `report()` (`tools/gscript.py:824-827`). The three burned runs at `docs/NAMES.md:511-518` were `count-1` and **set iteration order**, neither used here. `#686` being FlatSequence-owned does not remove it from the list — `docs/diagram-hierarchy.md:114-115` counts all 57 `FlatSequenceFrame` rows inside the 170; what is unresolved for them is their **owner uid**, not their index (`:135`), and the probe never reads `#686`'s owner.
3. **P4's `n_before + 1` is the right arithmetic.** `loop_in` with `src_names=()` makes no tunnels (`tools/gscript.py:979-983`), and no loop-terminal class appears in the `report_all(main,"Node")` census (`docs/NAMES.md:317-320`) despite 3 WhileLoops and 17 ForLoops.
4. **The Move Invoke is insulated from the donor's ladder.** `tools/bench/probe_move_into_v0.log:44` shows node[13]'s `error in (no error)` at `w0`, so the empty `Nodes[]`/IndexArray chain on a freshly created (empty) destination cannot skip the move and fake a FAIL.

## Residual, deliberately NOT slugged

Nothing gates the *arrival* of the new loop on `Diagram#686` — round 4 raised it, round 5 released it, and item 2 shows the index derivation is sound. `owner_of(SCRATCH, loop_uid) == SIBLING_DIAG_UID` would close the one exotic case (a loop created inside `#12589`'s own subtree, which would make P3 fail for a non-capability reason); nice-to-have, out of scope.

```
tools/recipes/probe_move_into_v0.py REV 6
PRIOR-ART: novel
```

There is no in-scope defect: REV 6 is the round-4 fix and nothing else, and the fix is correct — run it.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)

## What was done with it

PRIOR-ART: novel - released, and the probe was RUN as reviewed (REV 6, no further edit).
Five rounds on one probe is itself the finding this session reports upward: rounds 2-4 each returned real
run-breaking defects (name-keyed terminals, a cached Traverse index, the missing Invoke purge), so none was
wasted, but the cost - ~45 min of wall clock across five dispatches on a 3-minute run - belongs in cycle 15'
retrospective under the same heading cycle 10 used.

RESULT OF RUN 2: tools/bench/probe_move_into_v0.log (appended after run 1).
