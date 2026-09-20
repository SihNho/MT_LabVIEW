r"""diag_hierarchy_a3.py - A3 (pre-rig-master-plan.md:66-72): complete the 170-diagram hierarchy FROM THE MACHINE,
replacing position matching. Read-only on the main VI. No op VI is built, modified or saved.

WHAT ALREADY EXISTS (checked before writing a line - CLAUDE.md "before creating any new op, tool or recipe";
`grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, docs/toolkit-capabilities.md):
  * `g.report_all(target, cls)` (gscript.py:294) - uid + pos + OWNER CLASS for every object of a class in ONE op
    run. The 170 diagram uids and the 132 LoopTunnel uids both come from it; this is the helper the cycle-12
    prior-art review used to delete 18 op runs from A2.
  * `OpOwnerChain_v1.vi` + `read_owner()` (tools/recipes/build_opownerchain_v1.py:246) - any uid -> its owner's
    class AND uid. Built and FUNCTIONAL 2026-09-16 (20 gates). Outputs are poisoned before each run. UNCHANGED here.
  * `OpTunnelRead_v0.vi` + `read_inner()` (build_optunnelread_v0.py:180) - a TUNNEL uid + inner-terminal index ->
    that terminal's **frame DIAGRAM uid** (`Terminal.Diagram` 634A002 -> UID), inner wire, owner. 24/24 verified,
    docs/toolkit-capabilities.md:50. **This is the candidate top-down reader for FlatSequence and it already
    exists** - nothing is built for part B.
  * `OpWireSource_v5.vi` + `read_terminal()` (build_opwiresource_v5.py:155) - which object DRIVES a wire. 12/12.
  * `g.tunnels(target, index)` (gscript.py:747) - a LoopTunnel's direction (`out_is_source` / `in_is_source`),
    outer + inner wire uids, index_mode. `tools/bench/main_vi_tunnels.json` already holds all 132 rows with the
    access index each one needs.
  * `g.node_labels(target, diagram_index)` (:393) and `g.panel_wiring(target)` (:632) - label text per node uid,
    and label + terminal WIRE per front-panel control. Naming a source uses these two, never position.
  * `g.build_property(target, cls, props, location)` (:1989) - used in part B ONLY as an ATTACH TEST on a scratch
    copy: OpBuildPN_v1 surfaces the creator's own error and an unsupported property id raises 1077, so this is a
    machine verdict on whether a property exists for a class, without building a reader.
  * `tools/bench/diagram_hierarchy.json` - the POSITION-MATCHED tree A3 replaces (129 resolved + 41 unresolved,
    each resolved row carrying a `distance`); `tools/bench/diagram_tree_main.json` - 170 owner-class strings and a
    `structures` uid map for five classes (FlatSequence absent).
  * `tools/bench/owner_semantics.json` - A2's result: five classes resolve diagram->structure->parent with no
    error; FlatSequence gives owner uid 0 + error 1055 on TWO diagrams (113 and 686).
  NOT retried, by standing decision: `OpCaseFrames_v0` (failed five times, pre-rig-master-plan.md:286).
  NOT built, by the judgement call that opened cycle 13: `ClassSpecifierConstant.AllTypes[]` (docs/NAMES.md:611-622).

PREDICTION CONTRACT (machine-checked; a miss is a failed prediction and owes a peer review).

  A0  TRIPWIRE  `report_all(MAIN,'Diagram')` returns 170 rows, owner-class histogram equal to
                diagram_tree_main.json's (CaseStructure 76 · FlatSequenceFrame 57 · ForLoop 17 · Sequence 11 ·
                EventStructure 5 · WhileLoop 3 · '' 1).
  A1            exactly 112 diagrams have a CLEAN owner class (170 - 57 FlatSequenceFrame - 1 top level).
  A2            every one of those 112 resolves diagram -> structure: non-zero owner uid, no error.
  A3            every distinct structure so found resolves structure -> parent `Diagram`, non-zero, no error.
  A4            **0 DISAGREEMENTS** against the position-matched `owner_uid` in diagram_hierarchy.json, over the
                diagrams where position matching had an answer. This is the headline of 3a; A2's sample was 14/14.
  A5            every structure uid found is a member of diagram_tree_main.json `structures[<class>]`.
  B1  MEASURED, NOT PREDICTED: which traverse class strings for a structure tunnel exist (`Tunnel`,
                `SequenceTunnel`, `FlatSequenceTunnel`, `Structure`, `MultiFrameStructure`). Error 109 = unknown
                name, error 1092 = not in the GObject hierarchy (docs/NAMES.md:566-580).
  B2            IF a tunnel class traverses AND some of its objects are owned by a FlatSequence, `read_inner`
                returns a NON-ZERO `frame_uid` that is one of the 57 FlatSequenceFrame diagram uids. That is the
                whole test: a frame diagram uid reached top-down, from a reader we already own.
  B3  STOP      if no existing reader returns those uids, the branch STOPS: candidate property ids go under OPEN
                and NOTHING is built. `MultiFrameStructure.Frames[]` **6363801** is attach-tested on a scratch
                copy for the ONE class nobody has tried, `VI Server:FlatSequence` - a fact for OPEN, not a reader.
  C1            on a FlatSequenceFrame diagram EVERY error indicator of OpOwnerChain_v1 is read INDIVIDUALLY
                (errL/errT/errO/errU/errG/errS/errWU/errCO), where A2 merged five of them into one string.
                Predicted, from A2: at least one carries 1055. **WHICH one is the entire measurement**, and the
                competing candidate is `errG` - the UID Property Node DOWNSTREAM of the cast. The control read on
                a clean diagram must come back all-empty.
  D1            `main_vi_nodeterms.json` diagram "43" node 16 already holds ForLoop #1359's ten terminals; a live
                `node_terms_uid` read returns the same uid and the same wire set.
  D2  MEASURED, NOT PREDICTED: the class/uid/label of the node driving each of 1359's INPUT wires, and whether
                wire **9806** - the `Auto-Reset` control's wire (docs/main-vi-panel-map.md:317, uid 17472) - is
                among them. **What it means for STATUS OPEN 1 is judgement and is NOT written here.**

WHAT THE CYCLE-13 PRIOR-ART REVIEW CHANGED IN THIS SCRIPT
(`archive/peer/2026-09-16-priorart-priorart-cycle13-a3.md`, claude/opus, ANSWERED 591 s, $5.1239, 10 verdicts -
every one of them landed here or in `docs/cycle13-plan.md`, none was argued):
  A3-i  `contradicted`   : **`errCO` is NOT "the cast node's own error".** `build_opwiresource_v4.py:108-115` shows
                           it is the `error out` of a `Generic.ClassName` Property Node hanging off the cast's
                           OUTPUT, and the cast (`To More Specific Class`, a Function) has **no error indicator
                           anywhere in the op**. So "the cast generated it" and "a downstream node generated it"
                           are NOT separable by this test, and this script no longer claims they are.
  A3-iv `contradicted`   : **1077 is not a verdict for a valid id on the wrong class.** The measured 1077 came
                           from a deliberately bogus id (`toolkit-capabilities.md:226`); a valid id on the wrong
                           class has been seen to create a node with **no data terminal, silently**
                           (`:131`, `Control.Value` 633200D). The attach test's verdict is therefore the
                           **data-terminal-name census**, the check `build_opcaseframes_v0.py:49-58` already uses.
  B2    `already-failed` : the **`Frames[]` route IS `OpCaseFrames_v0`**, which failed five times - and the attach
                           PASSED in every one of those runs; the failures were downstream (a terminal-reader
                           chain inherited from the donor, then a downcast trap). Nothing here walks that route:
                           the frame-uid attempt uses `OpTunnelRead_v0`, a DIFFERENT and working op (24/24), and
                           the `Frames[]` work is reduced to one attach census.
  B3a   `helper-exists`  : 3d's membership walk is GONE. `tools/bench/main_vi_nodeterms.json` diagram "43" node 16
                           already carries uid 1359's ten terminals with `is_source` and wire uids, and
                           `g.node_terms_uid` re-reads them in ONE op run - where the draft ran `OpOwnerChain_v1`
                           over every ForLoop-owned LoopTunnel in the VI (~40 runs) to discover the same thing.
  B3b   `helper-exists`  : `diagram_tree_main.json`'s per-diagram `uids` lists make structure -> home diagram a
                           FILE lookup for catalogued structures; 3a now diffs against it as a third reference
                           and says in writing why it re-measures (the file covers neither FlatSequence, nor
                           tunnels, nor anything past net_map's 120-node cap).
  B4a   `already-measured`: `Frames[]` 6363801 on `VI Server:MultiFrameStructure` attaches and its data terminal
                           is named `Frames[]` - measured FIVE times, `build_opcaseframes_v0.log:9-11,36-38,61-63,
                           90-92,120-122`. That class is not re-tested; only `VI Server:FlatSequence` is.
  B4b   `already-measured`: `errO` was already read and merged into `errs` (`build_opownerchain_v1.py:268-269`),
                           so A2 already proved that one of errL/errT/errO/errU/errG carries the 1055. Reading
                           `errO` alone settles nothing - hence the full de-merge above.
  A4    `unread-evidence` : `docs/main-vi-panel-map.md:317` pins `Auto-Reset` (uid 17472) to **wire 9806**, and
                           `docs/frame-loop-wire-graph.md:440` records #1359 t1 (wire 9097) as fed by
                           `#8953 Initialize Array`. 3d tests those two as membership/identity facts instead of
                           re-deriving them.
  A3-ii, A3-iii `contradicted`: two ACTIVE docs contradict the measurement; both are annotated in this cycle -
                           see the FIXED: lines in the review file.
  Z             main VI md5 `2a78e17c449cacdaf5da389818526859` identical before and after (rule 1d).

  MATERIAL=1 py tools/bgrun.py --max-min 40 --log tools/bench/diag_hierarchy_a3.log -- py -u tools/bench/diag_hierarchy_a3.py
"""
import collections
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402
from build_opownerchain_v1 import MAIN, OP as OP_CHAIN, LABELS as LABELS_CHAIN, read_owner  # noqa: E402
from build_opwiresource_v5 import OP as OP_WIRE, MAP_OUT as LABELS_WIRE, read_terminal  # noqa: E402
from build_optunnelread_v0 import OP as OP_TUNREAD, MAP_OUT as LABELS_TUNREAD, read_inner  # noqa: E402

TREE = os.path.join(HERE, "diagram_tree_main.json")
HIER = os.path.join(HERE, "diagram_hierarchy.json")
CENSUS = os.path.join(HERE, "main_vi_tunnels.json")
OUT = os.path.join(HERE, "diagram_tree_a3.json")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")

FS_OWNER = "FlatSequenceFrame"
TARGET_LOOP = 1359                 # the ForLoop STATUS OPEN 1 now points at (A2: 10177 -> ForLoop#1359)
FRAME_DIAGRAM = 639                # ForLoop#1359's own parent diagram (A2), i.e. the frame loop's diagram
FS_CASE = 113                      # a FlatSequenceFrame-owned diagram, measured in A2
CLEAN_CASE = 639                   # the control: resolves with no error
TUNNEL_CLASS_PROBES = ["Tunnel", "SequenceTunnel", "FlatSequenceTunnel", "Structure", "MultiFrameStructure"]
FRAMES_PID = "6363801"             # MultiFrameStructure.Frames[] (docs/NAMES.md:841)
# ONLY the class nobody has tried. `VI Server:MultiFrameStructure` attaches and censuses as data terminal
# 'Frames[]' in five recorded runs (build_opcaseframes_v0.log:9-11,36-38,61-63,90-92,120-122) - prior-art B4a.
ATTACH_CLASSES = ["VI Server:FlatSequence"]
ERR_KEYS = ["errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO"]
AUTO_RESET_WIRE = 9806             # the `Auto-Reset` control (uid 17472), docs/main-vi-panel-map.md:317
NODETERMS = os.path.join(HERE, "main_vi_nodeterms.json")

_gates = []
out = {"part_a": {}, "part_b": {}, "part_c": {}, "part_d": {}}


def gate(label, ok, detail=""):
    _gates.append((label, bool(ok)))
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}{('   ' + detail) if detail else ''}", flush=True)
    return bool(ok)


def dump():
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)


def chain(vi, labels, uid, quiet=True):
    """read_owner VERBATIM (build_opownerchain_v1.py:246). `quiet` suppresses its per-call print for the bulk walk."""
    if quiet:
        real, sys.stdout = sys.stdout, open(os.devnull, "w", encoding="utf-8")
        try:
            r = read_owner(vi, labels, uid)
        finally:
            sys.stdout.close(); sys.stdout = real
    else:
        r = read_owner(vi, labels, uid)
    return r


def errors_individually(vi, labels, uid):
    """Every error indicator of OpOwnerChain_v1 read SEPARATELY - the 3c measurement. read_owner merges five of
    them into `errs` and has never reported which node produced the 1055."""
    r = chain(vi, labels, uid, quiet=False)
    per = {}
    for k in ERR_KEYS:
        lab = labels.get(k)
        if not lab:
            per[k] = "(label absent from opwiresource_v5_labels.json)"
            continue
        try:
            per[k] = g._err(vi, lab) or ""
        except Exception as e:
            per[k] = f"EXC {str(e)[:70]}"
    per["error out (the op's own)"] = r["err"]
    for k, v in per.items():
        print(f"        {k:28} ({labels.get(k, 'error out')!r:>16}) = {v[:100]!r}", flush=True)
    return r, per


# ----------------------------------------------------------------------------------------------- part A (3a)
def part_a(vi, labels, rows, tree, hier):
    print("\n=== 3a  FULL HIERARCHY, FIVE CLEAN CLASSES ===", flush=True)
    posmatch = {int(r["diagram_uid"]): r for r in hier.get("resolved", [])}
    unresolved = {int(r["diagram_uid"]) for r in hier.get("unresolved", [])}
    structures = tree["structures"]
    # PRIOR-ART B3b: `diagram_tree_main.json`'s per-diagram `uids` lists make structure -> home diagram a FILE
    # lookup for catalogued structures - raised at archive/peer/2026-09-15-priorart-ownerchain.md:125 and again
    # at ...-a1-ownerchain-v1.md:334-342 and never disposed. It is used HERE as a third cross-check. This run
    # still measures, because the file covers neither FlatSequence, nor tunnels, nor anything past net_map's
    # 120-node-per-diagram cap (tools/bench/diagram_tree_main.py:67) - i.e. it is partial, not general.
    idx_to_uid = {r["i"]: int(r["uid"]) for r in rows}
    struct_home_from_tree = {}
    for idx, dv in tree["diagrams"].items():
        home = idx_to_uid.get(int(idx))
        for u in dv.get("uids", []):
            struct_home_from_tree.setdefault(int(u), home)
    clean = [r for r in rows if r["owner"] not in (FS_OWNER, "")]
    gate(f"A1 exactly 112 diagrams have a clean owner class (170 - 57 {FS_OWNER} - 1 top level)",
         len(clean) == 112, f"got {len(clean)}")
    table, parent_memo, bad = [], {}, []
    t0 = time.time()
    for n, r in enumerate(clean, 1):
        dg = int(r["uid"])
        s = chain(vi, labels, dg)
        st = int(s["owner_uid"])
        row = {"diagram_uid": dg, "diagram_index": r["i"], "owner_class": s["ownercls"],
               "recorded_owner_class": r["owner"], "structure_uid": st,
               "err": s["err"], "errs": s["errs"]}
        if st and st not in parent_memo:
            parent_memo[st] = chain(vi, labels, st)
        p = parent_memo.get(st)
        row["parent_diagram_class"] = p["ownercls"] if p else None
        row["parent_diagram_uid"] = int(p["owner_uid"]) if p else 0
        row["parent_err"] = ((p["err"] + " " + p["errs"]).strip() if p else "no structure uid")
        if not st or s["err"] or s["errs"] or s["ownercls"] != r["owner"]:
            bad.append(row)
        pm = posmatch.get(dg)
        if pm:
            row["position_owner_uid"] = pm.get("owner_uid")
            row["position_distance"] = pm.get("distance")
            row["position_agrees"] = (pm.get("owner_uid") == st)
        else:
            row["position_owner_uid"] = None
            row["position_agrees"] = None
            row["newly_resolved"] = True
        if st and r["owner"] in structures and st not in structures[r["owner"]]:
            row["not_in_tree_structures"] = True
        tree_home = struct_home_from_tree.get(st)
        row["tree_parent_diagram_uid"] = tree_home
        row["tree_parent_agrees"] = (None if tree_home is None else tree_home == row["parent_diagram_uid"])
        table.append(row)
        if n % 20 == 0:
            print(f"    ... {n}/{len(clean)} diagrams, {len(parent_memo)} distinct structures, "
                  f"{time.time() - t0:.0f} s", flush=True)
    agree = [r for r in table if r.get("position_agrees") is True]
    dis = [r for r in table if r.get("position_agrees") is False]
    new = [r for r in table if r.get("position_agrees") is None]
    bad_parent = [r for r in table if r["structure_uid"] and
                  (r["parent_diagram_class"] != "Diagram" or not r["parent_diagram_uid"] or r["parent_err"])]
    not_in_tree = [r for r in table if r.get("not_in_tree_structures")]
    tree_dis = [r for r in table if r.get("tree_parent_agrees") is False]
    tree_none = [r for r in table if r.get("tree_parent_agrees") is None]
    out["part_a"] = {"n_clean": len(clean), "table": table,
                     "n_distinct_structures": len(parent_memo),
                     "agree": len(agree), "disagree": len(dis), "newly_resolved": len(new),
                     "disagreements": dis, "unresolved_in_posmatch_now_resolved":
                         sorted(r["diagram_uid"] for r in table if r["diagram_uid"] in unresolved and r["structure_uid"]),
                     "failed_rows": bad, "failed_parent_rows": bad_parent,
                     "structure_uid_not_in_tree": [r["diagram_uid"] for r in not_in_tree],
                     "tree_parent_disagreements": tree_dis,
                     "tree_parent_no_answer": len(tree_none)}
    dump()
    gate("A2 every clean diagram resolves to a structure (non-zero uid, no error, class as recorded)",
         not bad, f"{len(bad)} failed: {[r['diagram_uid'] for r in bad][:10]}")
    gate("A3 every structure resolves to a parent Diagram (non-zero, no error)",
         not bad_parent, f"{len(bad_parent)} failed: {[r['diagram_uid'] for r in bad_parent][:10]}")
    gate("A4 ZERO disagreements with the POSITION-MATCHED owner_uid", not dis,
         f"agree {len(agree)} / disagree {len(dis)} / no position answer {len(new)}")
    gate("A5 every structure uid is in diagram_tree_main.json structures[<class>]",
         not not_in_tree, f"{len(not_in_tree)} outside: {[r['diagram_uid'] for r in not_in_tree][:10]}")
    for d in dis:
        print(f"    DISAGREEMENT diagram {d['diagram_uid']} ({d['recorded_owner_class']}): machine "
              f"{d['structure_uid']} vs position {d['position_owner_uid']} (distance {d.get('position_distance')})",
              flush=True)
    print(f"  X B3b structure -> parent, machine vs the diagram_tree_main.json `uids` lookup: "
          f"{len(table) - len(tree_dis) - len(tree_none)} agree, {len(tree_dis)} DISAGREE, "
          f"{len(tree_none)} the file has no answer for (reported, never gated - the file is partial by "
          f"construction: no FlatSequence, no tunnels, 120-node cap)", flush=True)
    for d in tree_dis[:10]:
        print(f"    TREE-LOOKUP DISAGREEMENT diagram {d['diagram_uid']}: structure {d['structure_uid']} -> "
              f"machine {d['parent_diagram_uid']} vs file {d['tree_parent_diagram_uid']}", flush=True)
    print(f"  3a SUMMARY: {len(table)} diagrams -> {len(parent_memo)} distinct structures; "
          f"agree {len(agree)}, disagree {len(dis)}, newly resolved {len(new)}; "
          f"of the 41 position-unresolved, {len(out['part_a']['unresolved_in_posmatch_now_resolved'])} now resolved",
          flush=True)


# ----------------------------------------------------------------------------------------------- part B (3b)
def part_b(rows, fs_uids):
    print("\n=== 3b  FLATSEQUENCE TOP-DOWN: does a reader we ALREADY OWN return the frames' DIAGRAM uids? ===",
          flush=True)
    fs_diagrams = {int(r["uid"]) for r in rows if r["owner"] == FS_OWNER}
    probes = {}
    for cls in TUNNEL_CLASS_PROBES:
        try:
            probes[cls] = {"count": int(g.count(MAIN, cls)), "error": ""}
        except Exception as e:
            probes[cls] = {"count": None, "error": str(e)[:160]}
        print(f"  B1 traverse class {cls!r}: {probes[cls]}", flush=True)
    out["part_b"] = {"class_probes": probes, "n_flatsequence_frame_diagrams": len(fs_diagrams)}
    dump()
    workable = [c for c, v in probes.items() if v["count"]]
    resolved = {}
    tun_rows = []
    forloop_tunnels = []
    if workable:
        cls = workable[0]
        allrows = g.report_all(MAIN, cls)
        owners = collections.Counter(r["owner"] for r in allrows)
        print(f"  B2 report_all({cls!r}) = {len(allrows)} objects, owner-class histogram {dict(owners)}", flush=True)
        out["part_b"]["tunnel_class_used"] = cls
        out["part_b"]["tunnel_owner_histogram"] = dict(owners)
        # docs/NAMES.md:67 - "a For Loop's `N` terminal reports as `Tunnel`". If this class traverses, the count
        # terminal 3d asks about is IN this list, so collect the ForLoop-owned rows for part D.
        forloop_tunnels = [int(r["uid"]) for r in allrows if r["owner"] == "ForLoop"]
        out["part_b"]["tunnel_uids_owner_forloop"] = forloop_tunnels
        print(f"  B2 {len(forloop_tunnels)} {cls!r} objects report owner class 'ForLoop' (docs/NAMES.md:67 says a "
              f"For loop's N terminal reports as 'Tunnel'; part D checks which belong to #{TARGET_LOOP})",
              flush=True)
        cand = [r for r in allrows if r["owner"] in ("FlatSequence", FS_OWNER)]
        out["part_b"]["n_candidate_tunnels"] = len(cand)
        print(f"  B2 tunnels owned by a FlatSequence / {FS_OWNER}: {len(cand)}", flush=True)
        if cand:
            vi = g.op(OP_TUNREAD)
            with open(LABELS_TUNREAD, encoding="utf-8") as f:
                tl = json.load(f)
            # Bounded sweep: 3 candidate tunnels answer "does the reader work at all" (the brief's test); if it
            # does, keep going over every candidate until a 300 s budget is spent, and REPORT the coverage
            # reached rather than claiming all 57. Cost is ~1 s per inner-terminal read on the main VI.
            t0 = time.time()
            stopped_at = None
            for k, r in enumerate(cand):
                if k >= 3 and (not resolved or time.time() - t0 > 300):
                    stopped_at = k
                    break
                for i in range(12):
                    rr = read_inner(vi, tl, int(r["uid"]), i)
                    if rr["errs"] and not rr["frame_uid"]:
                        break
                    tun_rows.append(rr)
                    if rr["frame_uid"]:
                        resolved.setdefault(int(rr["frame_uid"]), []).append(int(r["uid"]))
            out["part_b"]["tunnels_read"] = stopped_at if stopped_at is not None else len(cand)
            out["part_b"]["sweep_seconds"] = round(time.time() - t0, 1)
        out["part_b"]["inner_rows"] = tun_rows
        out["part_b"]["frame_diagram_uids_reached"] = sorted(resolved)
        hit = sorted(set(resolved) & fs_diagrams)
        out["part_b"]["frame_uids_that_are_flatsequenceframe_diagrams"] = hit
        gate(f"B2 an EXISTING reader returned frame DIAGRAM uids that are {FS_OWNER}-owned diagrams",
             bool(hit), f"{len(hit)} of the {len(fs_diagrams)} reached: {hit[:12]}")
        print(f"  3b COVERAGE: {len(hit)} / {len(fs_diagrams)} FlatSequence frame diagrams reached top-down",
              flush=True)
    else:
        gate("B2 an EXISTING reader returned frame DIAGRAM uids", False,
             "no structure-tunnel traverse class resolved; the top-down route STOPS here (contract B3)")

    # Attach test - a fact for OPEN, NOT a reader (contract B3). The VERDICT IS THE DATA-TERMINAL-NAME CENSUS,
    # not the absence of error 1077: prior-art A3-iv showed 1077 was only ever measured from a BOGUS id, while a
    # VALID id on the WRONG class has created a node with no data terminal and no error at all
    # (docs/toolkit-capabilities.md:131,226). This is the check build_opcaseframes_v0.py:49-58 already uses.
    scratch = os.path.join(g.CLAUDEDEV, f"ScratchA3_{os.getpid()}.vi")
    attach = {}
    try:
        shutil.copy2(EMPTY, scratch)
        for cls in ATTACH_CLASSES:
            row = {"creator": "", "data_terminals": None, "all_terminals": None, "verdict": ""}
            try:
                before = g.uids(scratch, "Property")
                g.build_property(scratch, cls, [(FRAMES_PID, False)], (100 + 60 * len(attach), 60))
                new = [u for u in g.uids(scratch, "Property") if u not in before]
                row["creator"] = f"created {len(new)} Property node(s) {new}"
                terms = []
                for n in range(40):                      # a scratch EMPTY VI holds a handful of nodes
                    uid, rows = g.node_terms_uid(scratch, 0, n)
                    if not uid:
                        break
                    if new and uid == new[0]:
                        terms = rows
                        break
                row["all_terminals"] = [(r["name"], r["is_source"]) for r in terms]
                data = [r for r in terms if r["is_source"] and r["name"] not in ("reference out", "error out")]
                row["data_terminals"] = [r["name"] for r in data]
                row["verdict"] = (f"ATTACHED - data terminal {data[0]['name']!r}" if len(data) == 1
                                  else f"DID NOT ATTACH - {len(data)} data source terminals")
            except Exception as e:
                row["verdict"] = f"CREATOR REFUSED: {str(e)[:150]}"
            attach[cls] = row
            print(f"  B3 attach census {cls} + Frames[] {FRAMES_PID}: {row['verdict']}; "
                  f"terminals {row['all_terminals']}", flush=True)
    except Exception as e:
        attach["setup"] = f"EXC {str(e)[:150]}"
    finally:
        try:
            g.close_panel(scratch)
        except Exception:
            pass
        if os.path.exists(scratch):
            os.remove(scratch)
        print(f"  B3 scratch {os.path.basename(scratch)} deleted: {not os.path.exists(scratch)}", flush=True)
    out["part_b"]["frames_property_attach_test"] = attach
    dump()
    return forloop_tunnels


# ----------------------------------------------------------------------------------------------- part C (3c)
def part_c(vi, labels):
    print("\n=== 3c  WHERE THE 1055 COMES FROM: every error indicator read SEPARATELY ===", flush=True)
    print(f"  control, a CLEAN diagram ({CLEAN_CASE}):", flush=True)
    rc, pc = errors_individually(vi, labels, CLEAN_CASE)
    print(f"  the {FS_OWNER} case (diagram {FS_CASE}):", flush=True)
    rf, pf = errors_individually(vi, labels, FS_CASE)
    carriers = sorted(k for k, v in pf.items() if "1055" in str(v))
    out["part_c"] = {"clean": {"uid": CLEAN_CASE, "owner": rc["ownercls"], "owner_uid": rc["owner_uid"],
                              "per_indicator": pc},
                     "flatsequence": {"uid": FS_CASE, "owner": rf["ownercls"], "owner_uid": rf["owner_uid"],
                                      "per_indicator": pf},
                     "indicators_carrying_1055": carriers}
    dump()
    gate("C1 the control diagram comes back with every error indicator empty",
         not any(v for v in pc.values()), f"non-empty: {[k for k, v in pc.items() if v]}")
    gate(f"C1 the {FS_OWNER} case carries 1055 in errCO (reproducing A2)", "1055" in str(pf.get("errCO")),
         f"errCO = {str(pf.get('errCO'))[:80]!r}")
    print(f"  3c MEASURED: indicators carrying 1055 = {carriers}", flush=True)
    print("  3c READ THIS BEFORE INTERPRETING (prior-art A3-i, build_opwiresource_v4.py:108-115): `errCO` is the "
          "error of a `Generic.ClassName` PROPERTY NODE hanging off the CAST'S OUTPUT, i.e. DOWNSTREAM of the "
          "cast; the cast itself (`To More Specific Class`, a Function) has NO error indicator in this op. "
          "`errG` is the UID Property Node, also downstream. So this run says WHICH indicator carries the 1055 "
          "- it cannot separate 'the cast generated it' from 'a downstream node generated it'. The conclusion "
          "is NOT written here.", flush=True)


# ----------------------------------------------------------------------------------------------- part D (3d)
def part_d(vi, labels, rows, plain_tunnels=()):
    print(f"\n=== 3d  STATUS OPEN 1: ALL tunnels of ForLoop #{TARGET_LOOP} and what drives each input ===",
          flush=True)
    # PRIOR-ART B3a: the membership walk is a FILE LOOKUP plus ONE live op run, not ~40 OpOwnerChain_v1 calls.
    # main_vi_nodeterms.json already holds ForLoop #1359's terminals (diagram "43", node 16).
    with open(CENSUS, encoding="utf-8") as f:
        census = {int(t["uid"]): t for t in json.load(f)["tunnels"]}
    with open(NODETERMS, encoding="utf-8") as f:
        nt = json.load(f)
    rec_node, rec_diag = None, None
    for dkey, dval in nt["diagrams"].items():
        for n in dval.get("nodes", []):
            if int(n.get("uid") or 0) == TARGET_LOOP:
                rec_node, rec_diag = n, dkey
    if not rec_node:
        gate(f"D1 main_vi_nodeterms.json holds ForLoop #{TARGET_LOOP}", False, "not found")
        return
    print(f"  D1 recorded: diagram {rec_diag!r} node index {rec_node['n']} uid {rec_node['uid']}, "
          f"{len(rec_node['terms'])} terminals", flush=True)
    for t in rec_node["terms"]:
        print(f"        recorded t{t['i']}  name {t['name']!r:38} is_source {t['is_source']!s:5} "
              f"wire {t['wire']}", flush=True)
    live_uid, live_terms = g.node_terms_uid(MAIN, int(rec_diag), int(rec_node["n"]))
    same_wires = [int(t["wire"]) for t in rec_node["terms"]] == [int(r["wire"]) for r in live_terms]
    gate(f"D1 live node_terms_uid(diagram {rec_diag}, node {rec_node['n']}) returns uid {TARGET_LOOP} and the "
         f"recorded wire set", live_uid == TARGET_LOOP and same_wires,
         f"live uid {live_uid}, {len(live_terms)} terms, wires "
         f"{[int(r['wire']) for r in live_terms]}")
    terms = live_terms if live_uid == TARGET_LOOP else []
    in_wires = [int(r["wire"]) for r in terms if not r["is_source"] and int(r["wire"])]
    bare = [r["i"] for r in terms if not int(r["wire"])]
    out_wires = [int(r["wire"]) for r in terms if r["is_source"] and int(r["wire"])]
    print(f"  D1 ForLoop #{TARGET_LOOP}: {len(terms)} terminals - inputs {in_wires}, outputs {out_wires}, "
          f"BARE (unwired) terminal indices {bare}", flush=True)
    gate("D1b the PERIODIC remainder wire 10187 is one of #1359's INPUT wires (A2 said 10177 -> ForLoop#1359)",
         10187 in in_wires, str(in_wires))
    gate(f"D1c the `Auto-Reset` control's wire {AUTO_RESET_WIRE} (uid 17472, main-vi-panel-map.md:317) is NOT "
         f"directly among #{TARGET_LOOP}'s terminal wires", AUTO_RESET_WIRE not in (in_wires + out_wires),
         f"inputs {in_wires} outputs {out_wires}")
    count_terms = list(plain_tunnels)[:0]      # prior-art B3a removed the traverse-based count-terminal hunt

    labmap = {}
    try:
        di = next(r["i"] for r in rows if int(r["uid"]) == FRAME_DIAGRAM)
        labmap = {int(x["uid"]): x["label"] for x in g.node_labels(MAIN, di)}
        print(f"  D2 node_labels on diagram {FRAME_DIAGRAM} (index {di}): {len(labmap)} nodes", flush=True)
    except Exception as e:
        print(f"  D2 node_labels failed: {str(e)[:140]}", flush=True)
    panel = []
    try:
        panel = g.panel_wiring(MAIN)
        print(f"  D2 panel_wiring: {len(panel)} front-panel objects", flush=True)
    except Exception as e:
        print(f"  D2 panel_wiring failed: {str(e)[:140]}", flush=True)
    by_wire = {int(p["wire"]): p for p in panel if p.get("wire")}

    viw = g.op(OP_WIRE)
    with open(LABELS_WIRE, encoding="utf-8") as f:
        wlabels = json.load(f)
    tun_out, src_out = [], []
    # only the tunnel A2 already tied to this loop is re-read through the census - the rest of the direction
    # information now comes from the node's own terminals (prior-art B3a).
    for uid in (10177,):
        rec = census.get(uid)
        if not rec:
            tun_out.append({"uid": uid, "in_census": False})
            continue
        live = g.tunnels(MAIN, rec["index"])
        row = {"uid": uid, "in_census": True, "index": rec["index"], "live_uid": live["uid"],
               "index_agrees": live["uid"] == uid, "out_name": live["out_name"],
               "out_is_source": live["out_is_source"], "out_wire": live["out_wire"],
               "in_is_source": live["in_is_source"], "in_wires": live["in_wires"],
               "index_mode": live["index_mode"],
               "direction": ("INTO the loop (input tunnel)" if not live["out_is_source"]
                             else "OUT of the loop (output tunnel)")}
        tun_out.append(row)
        print(f"  D3 tunnel {uid} idx {rec['index']} name {live['out_name']!r} outer wire {live['out_wire']} "
              f"out_is_source {live['out_is_source']} inner {live['in_wires']} {row['direction']}", flush=True)
    dump()

    by_wire_term = {int(r["wire"]): r for r in terms if int(r["wire"])}
    print(f"  D4 resolving the driving node of ForLoop #{TARGET_LOOP}'s {len(in_wires)} INPUT wires with "
          f"OpWireSource_v5: {in_wires}", flush=True)
    for w in in_wires:
        tname = (by_wire_term.get(w) or {}).get("name", "")
        tidx = (by_wire_term.get(w) or {}).get("i")
        wterms = []
        for i in range(8):
            r = read_terminal(viw, wlabels, w, i)
            if r["errs"] and r["owner_uid"] == 0:
                break
            wterms.append(r)
        srcs = [r for r in wterms if r["is_source"] and r["recip_wire"] == w]
        src = (srcs[0]["owner_class"], int(srcs[0]["owner_uid"])) if srcs else None
        sinks = [(r["owner_class"], int(r["owner_uid"])) for r in wterms if not r["is_source"] and r["owner_uid"]]
        name = labmap.get(src[1], "") if src else ""
        ctl = by_wire.get(w)
        row = {"terminal_index": tidx, "terminal_name": tname, "wire": w, "source": src,
               "source_node_label": name, "sinks": sinks,
               "panel_control_on_this_wire": ({"label": ctl["label"], "uid": ctl["uid"],
                                               "indicator": ctl["indicator"]} if ctl else None)}
        src_out.append(row)
        print(f"  D4 t{tidx} {tname!r} wire {w}: source {src} label {name!r}; panel control on the same wire: "
              f"{row['panel_control_on_this_wire']}; sinks {sinks}", flush=True)
    ctl_srcs = [r for r in src_out if r["source"] and r["source"][0] in ("ControlTerminal", "Terminal")]
    fn_srcs = [r for r in src_out if r["source"] and r["source"][0] in ("Function", "GrowableFunction",
                                                                        "CompoundArithmetic")]
    autoreset = [r for r in src_out if "auto-reset" in (str(r["source_node_label"]) + " "
                 + str((r["panel_control_on_this_wire"] or {}).get("label", ""))).lower()]
    out["part_d"] = {"recorded_node": {"diagram": rec_diag, "node_index": rec_node["n"],
                                       "terms": rec_node["terms"]},
                     "live_uid": live_uid, "live_terms": [{"i": r["i"], "name": r["name"],
                                                           "is_source": r["is_source"], "wire": int(r["wire"])}
                                                          for r in terms],
                     "input_wires": in_wires, "output_wires": out_wires, "bare_terminal_indices": bare,
                     "tunnel_10177": tun_out, "input_wire_sources": src_out,
                     "control_terminal_sources": [r["wire"] for r in ctl_srcs],
                     "function_sources": [r["wire"] for r in fn_srcs],
                     "rows_mentioning_auto_reset": autoreset,
                     "auto_reset_wire": AUTO_RESET_WIRE,
                     "auto_reset_wire_is_a_terminal_wire_of_1359": AUTO_RESET_WIRE in (in_wires + out_wires),
                     "count_terminal": "a For loop's N terminal is a terminal of the ForLoop NODE, not a "
                                       "LoopTunnel, so g.tunnels() never exposes it - node_terms does, and it is "
                                       "reported above as a BARE terminal index (wire 0) if N is unwired"}
    dump()
    print(f"  3d SUMMARY: {len(terms)} terminals on ForLoop #{TARGET_LOOP}; {len(src_out)} input wires resolved; "
          f"control-terminal sources {[r['wire'] for r in ctl_srcs]}; function sources "
          f"{[r['wire'] for r in fn_srcs]}; rows mentioning 'Auto-Reset': {len(autoreset)}; "
          f"Auto-Reset wire {AUTO_RESET_WIRE} a terminal wire of #{TARGET_LOOP}: "
          f"{AUTO_RESET_WIRE in (in_wires + out_wires)}", flush=True)
    print("  3d COUNT TERMINAL: " + out["part_d"]["count_terminal"] + f"   BARE indices: {bare}", flush=True)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    print(f"MAIN md5 before: {md5}", flush=True)
    for p in (OP_CHAIN, OP_WIRE, OP_TUNREAD, EMPTY):
        if not os.path.exists(p):
            print(f"STOP: {os.path.basename(p)} missing", flush=True)
            return 3
    with open(LABELS_CHAIN, encoding="utf-8") as f:
        labels = json.load(f)
    with open(TREE, encoding="utf-8") as f:
        tree = json.load(f)
    with open(HIER, encoding="utf-8") as f:
        hier = json.load(f)
    g._lv = None
    fresh()
    try:
        vi = g.op(OP_CHAIN)
        rows = g.report_all(MAIN, "Diagram")
        hist = collections.Counter(r["owner"] for r in rows)
        tree_hist = collections.Counter(tree["owners"])
        print(f"A0 report_all('Diagram'): {len(rows)} rows, owner-class histogram {dict(hist)}", flush=True)
        gate("A0 TRIPWIRE 170 diagrams and the owner-class histogram matches diagram_tree_main.json",
             len(rows) == 170 and hist == tree_hist, f"n={len(rows)}")
        fs_uids = sorted(g.uids(MAIN, "FlatSequence"))
        print(f"A0 FlatSequence structures: {len(fs_uids)} {fs_uids}", flush=True)
        part_a(vi, labels, rows, tree, hier)
        plain = part_b(rows, fs_uids) or []
        part_c(vi, labels)
        part_d(vi, labels, rows, plain)
    finally:
        dump()
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        gate("Z main VI md5 unchanged (rule 1d: read-only)", same)
        try:
            g.reset()          # release this client's cached VI references (CLAUDE.md reference hygiene)
        except Exception as e:
            print(f"   reset() raised {e}", flush=True)
    npass = sum(1 for _, ok in _gates if ok)
    nfail = len(_gates) - npass
    print(f"   wrote {OUT}", flush=True)
    print(f"=== diag_hierarchy_a3: {npass} pass, {nfail} fail ===", flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
