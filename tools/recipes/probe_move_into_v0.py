r"""probe_move_into_v0.py - D1 phase P: CAN AN EXISTING NODE BE REPARENTED INTO ANOTHER DIAGRAM BY SCRIPT?

THIS IS THE ONE FACT D1 TURNS ON, AND IT HAS NEVER BEEN MEASURED (docs/d1-build-plan.md s1).

REV 7, 2026-09-17 - THE REPAIR, third and last attempt on this op (judgement decision A, cycle 15).
Run 2's P1 failure is MEASURED, not inferred: `archive/peer/2026-09-17-moveinto-p1-execstate0.md` (codex,
ANSWERED) proposed collateral net loss as its THIRD explanation, and `tools/bench/diag_movein_p1_break.log`
(5/5, read-only) confirmed it - **wire 464 is ONE net: source `IndexArray`#236, sinks `Property`#237,
`Property`#240 and `Invoke`#741 (the Move).** Deleting the Wire object to bare `Move.reference` also bares the
REQUIRED `reference` input of #237 and #240, which leaves no broken wire for Remove Bad Wires and pins ExecState
at 0. Both of my own hypotheses were wrong: `report_all('Invoke')` is `[741]` on donor and artefact alike.

THE REPAIR, and why it is spelled this way. The judgement decision is "do NOT leave #237/#240 bare; #741's
`reference` ends up fed from the same `IndexArray#236` net". Its literal first clause - *do not delete wire 464* -
is not simultaneously realisable with feeding `Move.reference` from the UID-addressed GObject, for a reason that
is now checked rather than assumed: a sink terminal takes exactly ONE source, and there is **no
`Terminal.Disconnect` method in `docs/vi-server-ids.json`** (it holds `Terminal.Connect Wire` 6349C03,
`Create Control/Indicator/Constant`, and only `ConnectorPane.Disconnect Terminal` 239A8002 /
`Disconnect All Terminals` 239A8003, which act on the connector pane, not on a diagram wire). So "bare only the
Move's own terminal" has no scripted route here. What IS realisable, and is the SAME END STATE for #237/#240, is
the peer's other named option: delete the net, then immediately re-wire `#237.reference` and `#240.reference`
from `IndexArray#236`'s `element` output - the second of those is a branch of an already-wired source, which
`gscript.connect_terminals`' docstring records as safe (`gscript.py:2205-2207`: *"an already-wired source is
BRANCHED (wire count unchanged, ExecState 0->1); an already-wired SINK is not safe"*). New gate **P1b** proves
both were restored before anything else is built. **FLAGGED FOR JUDGEMENT** in this run's report.

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
  P1b (REV 7) the two collateral sinks of wire 464 - `Property`#237.reference and `Property`#240.reference - are
      wired again, from `IndexArray`#236, before anything else is built. This is the measured cause of run 2's
      P1 failure and the only construction change in rev 7.
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
# REV 7b, 2026-09-17 - A UNIQUE WORKING COPY PER RUN, and it is not cosmetic. Rev 7's first run read the
# "donor copy" as ExecState 0 with `UID to GObject Reference.vi` already dropped as uid 148 and wire 464 already
# gone: run 2 had called `g.open_panel(OpMoveIn_v0.vi)`, failed at P1 and returned WITHOUT closing it, so the SAME
# LabVIEW process (pid 21512, handles 30,812) still held that path in memory with run 2's unsaved edits.
# `os.remove` + `shutil.copyfile` replaced the FILE; `GetVIReference(path)` still returned the in-memory object,
# so the whole of phase 1 ran against the previous failure's artefact. A name no LabVIEW instance has ever seen
# cannot be served from cache - the same reason SCRATCH is timestamped (CLAUDE.md: unique scratch name per run,
# created and deleted in the same run). The canonical name is written at the END, from the saved file.
OPIN_CANON = os.path.join(CLAUDEDEV, "OpMoveIn_v0.vi")
OPIN = os.path.join(CLAUDEDEV, f"OpMoveIn_v0_{int(time.time())}.vi")
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
    es_donor, n_donor, w_donor = g.exec_state(OPIN), g.count(OPIN, "Node"), g.count(OPIN, "Wire")
    print(f"  donor copy ExecState {es_donor}  nodes {n_donor} wires {w_donor}", flush=True)

    by = walk(OPIN, 0)
    # P1z (REV 7b): PROVE THE WORKING COPY IS THE DONOR before touching it. Rev 7's first run edited the previous
    # run's in-memory artefact for 2 s and reported a gate failure that said nothing about the question; nothing
    # in the script checked WHICH VI it had. The donor's identity is measured
    # (tools/bench/diag_movein_p1_break.log): ExecState 1, Node 15, Wire 29, subVIs Clear Errors / Create Invoke
    # Node / Traverse for GObjects, and NO `UID to GObject Reference.vi`.
    # `subvis()` returns [{uid, name, path}] dicts (gscript.py:331-333), NOT (uid, name) pairs - the pairs in
    # tools/bench/diag_movein_p1_break.log are that script's own formatting of the same rows.
    donor_subs = [r.get("name", "") for r in g.subvis(OPIN, 0)]
    u2g_present = any("UID to GObject" in s for s in donor_subs)
    if not gate("P1z the working copy is a FRESH copy of OpMoveOut_v0, not a cached artefact",
                es_donor == 1 and n_donor == 15 and not u2g_present,
                f"ExecState {es_donor} (want 1), Node {n_donor} (want 15), Wire {w_donor}, "
                f"subVIs {donor_subs}, U2G already present: {u2g_present}"):
        return False
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

    # 1) cut the wire that feeds `reference` today (IA_n.element -> Move.reference).
    #    REV 7: this wire is a NET with three sinks (diag_movein_p1_break.log, 5/5) - #237, #240 and the Move.
    #    Deleting the Wire object bares all three, and #237/#240's `reference` is REQUIRED, which is exactly why
    #    run 2 ended at ExecState 0 with nothing for Remove Bad Wires to find. Record the collateral sinks and
    #    the net's SOURCE now, while the net still exists, and restore them at step 2b.
    ref_src = [e for e in wire_ends(by, ref_wire) if e[3]]
    ref_sinks = [e for e in wire_ends(by, ref_wire, exclude_uid=mv_uid) if not e[3]]
    fact(f"wire {ref_wire} net: SOURCE {ref_src}, collateral SINKS (besides the Move) {ref_sinks}")
    if not ref_src:
        gate("P1 OpMoveIn_v0 builds", False, f"no SOURCE terminal carries the reference wire {ref_wire}")
        return False
    ia_uid, _iai, ia_name, _is = ref_src[0]
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

    # 2b) REV 7 - RESTORE the collateral sinks. Class INDICES are re-resolved here, after the deletes: removing
    #     `Property` uid 744 shifts every later Property's index, and a cached index is the recorded way to edit
    #     the wrong object (docs/NAMES.md:511-534). The first connect makes a fresh wire, the second BRANCHES an
    #     already-wired source - both are passed branch=True because the count check cannot describe either.
    sc, si = cls_index(OPIN, ia_uid)
    if sc is None:
        gate("P1 OpMoveIn_v0 builds", False, f"the reference net's source uid {ia_uid} is no longer a Node")
        return False
    for u, _i, nm, _s in ref_sinks:
        kc, ki = cls_index(OPIN, u)
        if kc is None:
            gate("P1 OpMoveIn_v0 builds", False, f"collateral sink uid {u} vanished after the deletes")
            return False
        try:
            g.wire(OPIN, sc, si, ia_name, kc, ki, nm, branch=True)
            fact(f"restored {kc}[{ki}] uid {u} .{nm} <- {sc}[{si}] uid {ia_uid} .{ia_name}")
        except Exception as e:
            gate("P1 OpMoveIn_v0 builds", False, f"restore of uid {u}.{nm} raised: {str(e)[:160]}")
            return False
    by = walk(OPIN, 0)
    restored = {}
    for u, _i, nm, _s in ref_sinks:
        row = term(by[u][2], nm, False) if u in by else None
        restored[u] = row["wire"] if row else 0
    same_net = len(set(w for w in restored.values() if w)) == 1
    srcs_ok = all(any(e[0] == ia_uid and e[3] for e in wire_ends(by, w, exclude_uid=u))
                  for u, w in restored.items() if w)
    if not gate("P1b the collateral sinks of the old reference net are wired again from the IndexArray",
                all(restored.values()) and same_net and srcs_ok,
                f"{restored} (0 = still bare); one shared net {same_net}; sourced at uid {ia_uid} {srcs_ok}"):
        return False

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


def retire_working_copy():
    """The per-run working copy becomes the canonical `OpMoveIn_v0.vi` on disk and is then deleted (CLAUDE.md:
    scratch is created and deleted in the same run). The canonical file is a byte copy, never a LabVIEW save, so
    no instance holds it open - which is the whole point of the unique name."""
    try:
        if os.path.exists(OPIN):
            shutil.copyfile(OPIN, OPIN_CANON)
            os.remove(OPIN)
            print(f"  working copy retired -> {os.path.basename(OPIN_CANON)} (scratch {os.path.basename(OPIN)} "
                  f"deleted)", flush=True)
    except Exception as e:
        print(f"  working copy NOT retired: {e}", flush=True)


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

    # An EXCEPTION inside phase 1 used to leave the per-run working copy on disk (one `OpMoveIn_v0_<epoch>.vi`
    # survived rev 7b's ValueError and had to be deleted by hand) - CLAUDE.md's scratch rule says created and
    # deleted in the SAME run, including the crashing one.
    try:
        uid_label = build_opmovein()
    except BaseException:
        retire_working_copy()
        raise
    if not uid_label:
        print("\nSTOP after phase 1 (failure budget: no repair pass).", flush=True)
        retire_working_copy()
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

        # REV 7: the BOUNDARY-WIRE census the judgement brief asks for. There is no per-wire reader for
        # `Wire.Is Broken?` (6371004) on this fleet - STATUS OPEN 13's sibling, still unbuilt - so the census is
        # stated at the level that IS readable: Wire and LoopTunnel counts around each move, plus ExecState.
        # A relocation that LabVIEW re-routes through the loop border shows up as new LoopTunnels; one that simply
        # cuts the wires shows up as a Wire-count drop with no new tunnels.
        w_before = g.count(SCRATCH, "Wire")
        t_before = g.count(SCRATCH, "LoopTunnel")
        fact(f"census before the moves: Wire {w_before}, LoopTunnel {t_before}")

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
        w_after, t_after = g.count(SCRATCH, "Wire"), g.count(SCRATCH, "LoopTunnel")
        try:
            body_now = [r_["uid"] for r_ in g.node_labels(SCRATCH, diag_index(SCRATCH, body_uid))]
        except Exception as e:
            body_now = f"<node_labels: {str(e)[:80]}>"
        fact(f"census after the moves: Wire {w_before} -> {w_after}, LoopTunnel {t_before} -> {t_after}; "
             f"new loop body Diagram#{body_uid} now holds {body_now}")
        gate("P4 no node lost by the two moves", n_after == n_before + 1,   # +1 = the new While loop node
             f"Node {n_before} -> {n_after}; ExecState now {es1} (0 expected: wires were cut)")
        fact(f"ExecState after the moves and Remove Bad Wires: {es1}")
    finally:
        retire_working_copy()
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
