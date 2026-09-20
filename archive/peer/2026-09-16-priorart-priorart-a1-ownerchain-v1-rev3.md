# priorart-priorart-a1-ownerchain-v1-rev3

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.4705  in 48 / out 41278 / cache-create 171703 / cache-read 3442514  (574s, 36 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (578s)
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
REVISION 3 OF THE A1 BUILD (cycle 11, Stage 3). Third and final prior-art pass before the run.

Two prior-art reviews have already run on this artifact and BOTH are archived with per-finding dispositions:
  round 1  archive/peer/2026-09-16-priorart-priorart-a1-ownerchain-v1.md       (9 verdicts)
  round 2  archive/peer/2026-09-16-priorart-priorart-a1-ownerchain-v1-rev2.md  (6 verdicts)
Round 2's findings are now implemented or released: junk-Invoke purge added (purge_junk + gate B4c), B5 now uses
fresh() with a cold re-read (gate B5b), both line-number defects fixed, and findings 4/5/6 released in writing
inside the docstring. Round 2 also audited round 1's refutations: (5) and (6b) CORRECT, (8) survives narrowly with
the correction now carried in the docstring.

Please review the CURRENT file, verbatim below, for prior art only. Two things are specifically useful:
  - anything ALREADY BUILT / MEASURED / FAILED that the two earlier rounds did not catch;
  - whether any disposition in either archived review is wrong - name the file and line if so.
The artifact has still never been run; the only evidence about it is what is in these files.

=== tools/recipes/build_opownerchain_v1.py (verbatim, not yet run) ===
r"""build_opownerchain_v1.py - OpOwnerChain_v1.vi: a UID in, its OWNER's class and UID out.

WHAT ALREADY EXISTS (checked before writing a line of this, CLAUDE.md "before creating any new op"):
  * `docs/toolkit-capabilities.md:48` - `OpWireSource_v5` returns the owner of an INDEXED WIRE TERMINAL; it is the
    donor, not the op. `report()/report_all()` (gscript.py:261,294) return the owner's CLASS only, never its uid -
    confirmed by the prior-art review, archive/peer/2026-09-15-priorart-ownerchain.md:95-99.
  * readers used here all exist: `node_terms_uid` (gscript.py:731, creator-free), `report_all` (:294),
    `delete_object` (:2035), `connect2` (:2428), `remove_bad_wires_scripted` (:2278), `save` (:1858).
    Nothing new is hand-rolled; the only new artefact is the op VI itself.
  * `grep "^def " tools/gscript.py` + `ls tools/recipes` show no *ownerchain* helper other than the FAILED
    tools/recipes/build_opownerchain_v0.py, which this file replaces.

WHY IT IS CHEAP. The donor `OpWireSource_v5.vi` already contains the whole owner -> ClassName + cast -> UID chain
(census tools/bench/census_opwiresource_v5.log): node 157 `Owner` -> wire 751 -> node 163 `ClassName` (-> panel
"Class Name 4"), node 1221 To-More-Specific-Class -> node 1186 `UID` (-> "UID 4"), node 482 `ClassName`
(-> "Class Name 3"), node 1554 `ClassName` (-> "Class Name 6"). Only the SOURCE of 751 is wrong: it is the owner of
an indexed WIRE TERMINAL. Delete the Wire-only front section, then feed the chain from node 241's `Owner`, whose
`reference` is the UID-addressed object returned by node 990 (`UID to GObject Reference.vi`).

WHY v0 FAILED - three defects, all MEASURED on 2026-09-16, not re-derived here:
  1. every edit was SILENTLY DECLINED because the target's front panel was never opened
     (tools/bench/diag_delete_matrix.log). `gscript.ensure_loaded()` now does it inside all 26 mutating wrappers.
  2. `connect2(target, diagram, sink_node, sink_term, src_node, src_term)` takes terminal INDICES (gscript.py:2428
     writes them to `index 3`/`index 5`); v0 passed NAMES. That is why "R1 connect2 returned" and wire 1208 != 1081
     (build_opownerchain_v0.log:30,60). Every index here is resolved BY NAME from the sweep.
  3. `#1044` was deleted as class `SubVI` -> "1044 is not in list" (:144). MEASURED since:
     tools/bench/diag_ownerchain_state.log:13-19 - the six other targets are listed "found in ['Property','Node']"
     / "['IndexArray','Node']" and `uid 1044 classes: ['Node']`. v1 deletes every node under class `Node` and
     every wire under class `Wire`, and asserts each uid is in that class's list before deleting.
  plus: v0's `nodes_by_uid()` walked `net_map` ~14 times ("purged 166 junk Invoke(s)", :59). No net_map here: ONE
  `node_terms_uid(target,0,n)` sweep per phase.
  plus: node 482 is the THIRD consumer of wire 751 - predicted at
  archive/peer/2026-09-15-priorart-ownerchain.md:117, confirmed at build_opownerchain_v0.log:143
  (`consumers {163: 751, 1221: 751, 482: 1444}`) - and it is in both the bare-sink check and the rewire list.

ORDER: DELETES FIRST, THEN CONNECTS, AND REMOVE BAD WIRES ONLY ONCE AT THE END. `connect2` into an already-wired
SINK is not safe (`tools/gscript.py:2206-2207`: "an already-wired SINK is not safe (LabVIEW re-routes and the VI
breaks) - wire only unwired sinks"; note the pointer this project has cited three times, `:2084` then `:2110-2111`,
is wrong - those lines are `move_object`'s exception handler). Removing the Wire-only section plus wires 318 and
751 is what leaves all four `reference` sinks bare.

PRIOR-ART REVIEW OF THIS RECIPE: archive/peer/2026-09-16-priorart-priorart-a1-ownerchain-v1.md (claude/opus, 600 s,
9 verdicts). Findings 2, 3, 6a, 7, 9 are implemented above and below; 1, 4, 8 are released in writing here; 5 and
6b are refuted. In short:
  * (2) Remove Bad Wires is NOT called between the deletes and the connects - that placement was refuted on this
    donor lineage (archive/peer/2026-09-15-optunnelread-removebadwires-ate-the-chain.md:18,47,55, where the orphan
    set was Owner node 157 and property nodes 1319/1326 - three of the seven nodes deleted here). One call, at the
    end, with gate B3b re-reading the chain afterwards.
  * (3)+(9) the delete class is NOT `GObject`: tools/bench/diag_delete_matrix.log Part C never swept it, `GObject`
    also enumerates Terminals (docs/toolkit-capabilities.md:103), and deleting a node removes its terminals - so a
    class-scoped `gone` set would never be a single uid. Nodes go by class `Node` (MEASURED:
    diag_ownerchain_state.log:19-24 lists all seven under `Node`, 1044 and 1221 ONLY there), wires by class `Wire`.
  * (6a) wires 318 and 751 are deleted EXPLICITLY instead of being left to Remove Bad Wires
    (archive/peer/2026-09-15-opcaseframes-identify-before-delete.md:22-24: broken branches persist and need an
    explicit delete).
  * (7) cross-op Traverse index transfer is MEASURED before it is used, not assumed (gate B4b).
  * (1) RELEASED: for the five catalogued structure classes, structure -> home diagram is already a lookup in
    tools/bench/diagram_tree_main.json (10407 at :397, 1359 at :389, both in diagram 43's list). This op exists
    for what that file does NOT hold: LoopTunnels (grep for 10114 / 10177 finds nothing), FlatSequence links that
    docs/diagram-hierarchy.md:66-69 marks unverified, and any uncatalogued class.
  * (4) RELEASED by fixing the citation, above.
  * (8) RELEASED: `OpTunnelRead_v0` (docs/toolkit-capabilities.md:49) gives a tunnel's INNER frame diagram via
    `Terminal.Diagram`. OPEN 1 needs the home diagram of the node DRIVING the outer terminal - a different object,
    which no existing op reaches.
  * (5) REFUTED: the review read "re-sweeps after connects" as one sweep after ALL connects. The code re-sweeps
    between R1 and R2 (`by = sweep()` immediately after R1, and R2's indices come from that sweep), which is
    exactly what archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:99-108 prescribes.
SECOND PRIOR-ART REVIEW, of this file as written:
archive/peer/2026-09-16-priorart-priorart-a1-ownerchain-v1-rev2.md (claude/opus, 626 s, 6 verdicts). It confirmed
both refutations below and found three real defects, two of which would have cost the run:
  * (1) ACCEPTED, and it is the one that would have failed the build: `OpConnect2_v0` drops ONE untyped junk
    Invoke on the target per call (docs/keystone-op-spec.md:565-573 짠33) and v0's `net_map` calls were silently
    purging them; removing net_map removed the purge. `purge_junk()` + gate B4c now do it explicitly, after the
    connects and before the single Remove Bad Wires - the order fix_v3_starting_xy.py:39-41 uses.
  * (2) ACCEPTED: `g.reset()` does not restart LabVIEW, so the old B5 tested memory, not disk. B5 now calls
    `fresh()` (kill + 8 s + COM preflight, from build_opconstvalue_v1.py:80-87) and adds B5b, which re-reads the
    topology cold - the very question archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:178-184 left
    open for this op.
  * (3) ACCEPTED: two line numbers - `diag_ownerchain_state.log:13-19` (not `:19-24`, which lists nodes this build
    KEEPS), and the `gscript.py:2110` that survived in the B3a stop message is now `:2206-2207`.
  * (4) already-measured, RELEASED IN WRITING: `diagram_tree_main.json`'s per-diagram `uids` are net_map's full
    node lists, not a structure roster - so node -> home diagram is a lookup for every node that walk SAW. It is
    capped at `max_nodes=120` per diagram (`tools/bench/diagram_tree_main.py:67`) and holds neither 10114 nor
    10177, so it is not a general answer and does not replace this op. The reviewer's better idea - `tunnels()`
    + `OpWireSource_v5` on the OUTER wire of 10114/10177, then a JSON lookup, two op runs - may answer OPEN 1
    without A1 at all; that is a scope decision for the judgement session and is recorded there, not taken here.
  * (5) already-measured, RELEASED IN WRITING: gate B4b re-confirms on this target what gscript.py:824 recorded on
    2026-09-13 ("rows verified IDENTICAL"); it does NOT reach OpDelete_v0's own third Traverse. The real guard is
    the per-delete `gone == {uid}` identity diff, which is what
    archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:30 actually prescribes. B4b is
    kept as a cheap precondition, not as the protection.
  * (6) helper-exists, RELEASED IN WRITING: the per-delete diff IS `delete_object(verify=True)` re-implemented.
    The difference is deliberate and is the reason to keep it: this loop STOPS on the first mismatch and logs
    WHICH uid vanished instead of raising mid-batch with only a count (gscript.py:2086).

  * (6b) REFUTED: wire 1081 must NOT be deleted. It feeds nodes 307 and 310 (`reference` - a required input on a
    Property Node) as well as the deleted 1044 (census_opwiresource_v5.log, nodes 11/12/10), so deleting it would
    break the op; and R1 BRANCHES it into node 241's `reference`, a branch preserving uid 1081 (same review, :71),
    which is precisely what gate B2 asserts.

PREDICTION CONTRACT (machine-checkable; every value below is asserted in the run):
  B1  the copy of the donor opens at ExecState 1.
  B0  the sweep finds nodes 241, 990, 163, 1221, 482 and the seven delete targets; node 241 `reference` carries
      wire 318, and 163 / 1221 / 482 `reference` all carry wire 751 (recorded, not gated).
  B4b `report(OP, cls)` and `report_all(OP, cls)` enumerate classes `Wire` and `Node` in the SAME uid order - the
      precondition for handing a report_all index to OpDelete_v0's own Traverse.
  B4  after deleting wires [318, 751] and nodes [1044, 145, 151, 157, 1319, 1326, 1329], each with a class-scoped
      `gone == {uid}` asserted per delete (and the loop STOPPING on the first mismatch), none of the nine remains.
  B3a AFTER the deletes: node 241 `reference` wire == 0 AND 163/1221/482 `reference` wire == 0 (all bare).
      If not, the run STOPS before connecting - connecting into a wired sink is the recorded way to break the VI.
  B2  after R1 (241.`reference` <- 990.`GObject`): those two terminals carry the SAME wire uid (expected 1081,
      preserved, because branching an already-wired source keeps the wire object).
  B3  after R2 (241.`Owner` -> `reference` of 163, 1221, 482): 241.`Owner` wire != 0 and all three read it.
  B3b after the single Remove Bad Wires at the end, B2's and B3's wire uids are UNCHANGED.
  B5  ExecState == 1 before the single save; after `save` + `g.reset()` + reopen it is STILL 1.
  B6  FUNCTIONAL, against the main VI read-only (rule 1d; md5 asserted unchanged around the whole run):
      uid 10407 (CaseStructure) -> owner class `Diagram`, owner uid 639
        (docs/diagram-hierarchy.md:46 "CaseStructure#10407 ... lives on diagram 43";
         docs/keystone-op-spec.md:593 "diagram 43 is UID 639") - two independent prior measurements;
      uid 1359 (ForLoop) -> owner class `Diagram`, owner uid 639
        (docs/diagram-hierarchy.md:47 "Magnet2Force ... ForLoop#1359 ... lives on diagram 43");
      and, RECORDED not gated, uid 639 -> its owner, expected `WhileLoop` 637 (docs/diagram-hierarchy.md:36).
  B7  `OpDelete_v1.vi` is removed from claudeDev (STATUS.md NEXT: behaviourally identical to v0, measured as A4 in
      tools/bench/diag_delete_matrix.log).

Scratch discipline: the only artefact is OpOwnerChain_v1.vi under claudeDev (save authority, rule 3). No original
is modified; the main VI is only read. No hardware.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/build_opownerchain_v1.log -- py -u tools/recipes/build_opownerchain_v1.py
"""
import hashlib
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid  # noqa: E402  (kills LabVIEW, waits, COM-preflights)

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DONOR = os.path.join(CLAUDEDEV, "OpWireSource_v5.vi")
OP = os.path.join(CLAUDEDEV, "OpOwnerChain_v1.vi")
OPDELETE_V1 = os.path.join(CLAUDEDEV, "OpDelete_v1.vi")
LABELS = os.path.join(ROOT, "tools", "bench", "opwiresource_v5_labels.json")
# verbatim from tools/recipes/build_opconstvalue_v1.py:42
MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"

N_IDENT = 241        # Property Position/ClassName/UID/Owner - the node that becomes the owner source
N_U2G = 990          # UID to GObject Reference.vi - its `GObject` output is the UID-addressed object
CONSUMERS = [163, 1221, 482]          # every consumer of the donor's old owner wire 751
# The Wire-only front section. CLASS `Node`, not `GObject` and not the concrete classes: MEASURED in
# tools/bench/diag_ownerchain_state.log:13-19 - all seven are enumerated under `Node` (1044 ONLY there), which is
# also the class docs/cycle11-plan.md:120 settled on after v0 died with "1044 is not in list", and the class five
# other recipes already delete by (build_harness_copy.py:83, build_gpu_kernel.py:92, build_opclfnparams.py:101).
DELETE_NODES = [1044, 145, 151, 157, 1319, 1326, 1329]
# ...and the two WIRE objects that must go with them, deleted EXPLICITLY (class `Wire`) rather than left to
# Remove Bad Wires: 318 feeds node 241's `reference`, 751 is the old owner wire whose three sinks are 163/1221/482
# (diag_ownerchain_state.log:57-59). A fan-out is ONE wire object (archive/peer/2026-09-16-ownerchain-b2-b3-
# failed-prediction.md:71), so one delete bares all three sinks.
# WIRE 1081 IS NOT IN THIS LIST, deliberately - see the docstring's REFUTED note.
DELETE_WIRES = [318, 751]

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def sweep():
    """{node_uid: (node_index, rows)} for diagram 0 in ONE pass - no net_map, no creator, no junk."""
    out = {}
    for n in range(40):
        uid, rows = g.node_terms_uid(OP, 0, n)
        if not uid:
            break
        out[int(uid)] = (n, rows)
    return out


def trow(by, uid, name):
    rec = by.get(uid)
    if not rec:
        return None
    for r in rec[1]:
        if r["name"] == name:
            return r
    return None


def twire(by, uid, name):
    r = trow(by, uid, name)
    return None if r is None else int(r["wire"])


def tindex(by, uid, name):
    r = trow(by, uid, name)
    return None if r is None else int(r["i"])


def cls_uids(cls):
    return [o["uid"] for o in g.report_all(OP, cls)]


def purge_junk(before):
    """Delete every Invoke node that appeared since `before`. `OpConnect2_v0` carries the erdosmiller
    `Create Invoke Node.vi` creator, which drops ONE untyped Invoke on the TARGET per run even with empty
    class/ID strings (docs/keystone-op-spec.md:565-573 짠33; gscript.py:2308-2317 records three OpReportNodes
    builds left ExecState 0 by exactly this). v0 never noticed because its `net_map` calls purged them as a side
    effect (build_opownerchain_v0.log:51-59, "166 junk Invoke(s)"); removing net_map removed the purge with it.
    Same shape as tools/recipes/fix_v3_starting_xy.py:17-26, the only other recipe that calls connect2."""
    junk = g.new_since(OP, "Invoke", before)
    for o in junk:
        ids = [x["uid"] for x in g.report(OP, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(OP, "Invoke", ids.index(o["uid"]))
    return [o["uid"] for o in junk]


def read_owner(vi, labels, uid):
    """Drive the op: uid in -> (owner class, owner uid, cross-checks, errors). Outputs poisoned first, so a
    property read that never ran is visible instead of being mistaken for an answer."""
    for lab in (labels["ownercls"], "Class Name 3", labels["cast_class"]):
        try:
            vi.SetControlValue(lab, "POISON")
        except Exception:
            pass
    vi.SetControlValue(labels["owner_uid"], 0)
    vi.SetControlValue("vi path", MAIN)
    # keep the donor's Traverse+IndexArray seed legal: its error out feeds node 241's `error in`, so a failing
    # Traverse would skip the whole chain silently. Class/index are otherwise unused by the owner path.
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", 0)
    vi.SetControlValue(labels["uid_in"], int(uid))
    vi.SetControlValue(labels["term_index"], 0)     # vestigial once the Index Array is gone
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:100]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or ""
                                for k in ("errL", "errT", "errO", "errU", "errG")) if x)
    out = dict(uid=int(uid), ownercls=vi.GetControlValue(labels["ownercls"]),
               owner_uid=int(vi.GetControlValue(labels["owner_uid"])),
               cls_482=vi.GetControlValue("Class Name 3"),
               cast_class=vi.GetControlValue(labels["cast_class"]),
               uid_back=int(vi.GetControlValue(labels["uid_back"])),
               cls_back=vi.GetControlValue(labels["cls_back"]), err=err, errs=errs)
    print(f"  OBSERVED uid {out['uid']} -> owner {out['ownercls']!r} uid {out['owner_uid']} | "
          f"self {out['cls_back']!r}#{out['uid_back']} | 482 says {out['cls_482']!r} cast {out['cast_class']!r} "
          f"| {out['err'][:40]} {out['errs'][:60]}", flush=True)
    return out


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    main_md5_before = md5(MAIN)
    print(f"MAIN md5 before: {main_md5_before}", flush=True)
    if not os.path.exists(DONOR):
        print("STOP: donor OpWireSource_v5.vi missing", flush=True)
        return 3
    with open(LABELS, encoding="utf-8") as f:
        labels = json.load(f)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copy2(DONOR, OP)
    st0 = g.exec_state(OP)
    print(f"copied donor -> {os.path.basename(OP)}   ExecState {st0}", flush=True)
    gate("B1 the copy starts legal", st0 == 1, str(st0))

    # ---- B0: one sweep, everything resolved by NAME -------------------------------------------------
    by = sweep()
    print(f"  swept {len(by)} nodes: {sorted(by)}", flush=True)
    w_ref0 = twire(by, N_IDENT, "reference")
    w_gobj0 = twire(by, N_U2G, "GObject")
    cons0 = {u: twire(by, u, "reference") for u in CONSUMERS}
    print(f"  node {N_IDENT}.reference wire {w_ref0} (expect 318) | node {N_U2G}.GObject wire {w_gobj0} "
          f"| consumers {cons0} (census says 163/1221 on 751)", flush=True)
    need = [N_IDENT, N_U2G] + CONSUMERS + DELETE_NODES
    ok0 = all(u in by for u in need)
    gate("B0 every node the plan names is on the diagram", ok0, str([u for u in need if u not in by]))
    if not ok0:
        print("STOP: the donor's topology is not what the census recorded", flush=True)
        return 2

    # ---- B4: delete the Wire-only front section - wires first (class Wire), then nodes (class Node) --
    if w_ref0 != DELETE_WIRES[0]:
        print(f"  NOTE: node {N_IDENT}.reference carries wire {w_ref0}, the census said {DELETE_WIRES[0]} - "
              f"deleting what is actually there", flush=True)
    if not w_ref0:
        print(f"STOP: node {N_IDENT}.reference is already bare - unexpected", flush=True)
        return 2
    wire_targets = [w_ref0] + [w for w in DELETE_WIRES if w != w_ref0]
    plan = [("Wire", u) for u in wire_targets] + [("Node", u) for u in DELETE_NODES]

    # B4b CROSS-OP INDEX AGREEMENT, measured rather than assumed. `delete_object` runs its OWN Traverse inside
    # OpDelete_v0 while the index comes from OpReportAll_v0, and archive/peer/2026-09-15-opwiresource-fail5-
    # traverse-index-order-mismatch.md:28 says not to assume the two families agree. report() is the per-object
    # family that gscript.py:2095 pins delete/move order to, so compare the two orders directly, per class, here.
    order_ok, orders = True, {}
    for cls in ("Wire", "Node"):
        ra = cls_uids(cls)
        rp = [o["uid"] for o in g.report(OP, cls)]
        orders[cls] = (len(ra), ra == rp)
        order_ok = order_ok and ra == rp
        print(f"  {cls}: report_all {len(ra)} uids, report {len(rp)} uids, same order = {ra == rp}", flush=True)
        if ra != rp:
            print(f"    report_all {ra}\n    report     {rp}", flush=True)
    gate("B4b the two Traverse families enumerate these classes in the SAME order", order_ok, str(orders))

    missing = [(c, u) for c, u in plan if u not in cls_uids(c)]
    print(f"  delete plan (class, uid): {plan}", flush=True)
    gate("B4a every delete target is reachable under its class", not missing, f"missing {missing}")
    if missing:
        print("STOP: a delete target is not enumerated under the class the record gives it", flush=True)
        return 2
    deleted, delete_notes = [], []
    for cls, uid in plan:
        before = cls_uids(cls)
        if uid not in before:
            delete_notes.append(f"#{uid} vanished with an earlier delete")
            print(f"  delete {cls} #{uid}: already gone", flush=True)
            continue
        idx = before.index(uid)
        try:
            g.delete_object(OP, cls, idx, verify=False)
        except Exception as e:
            delete_notes.append(f"#{uid} raised {str(e)[:60]}")
            print(f"  delete {cls}[{idx}] #{uid} raised: {e}", flush=True)
            continue
        gone = set(before) - set(cls_uids(cls))
        print(f"  deleted {cls}[{idx}] -> gone {sorted(gone)} (wanted {uid})", flush=True)
        if gone == {uid}:
            deleted.append(uid)
        else:
            # if one delete takes the wrong object every later index is guesswork. Stop rather than damage more.
            delete_notes.append(f"#{uid}: gone {sorted(gone)} - WRONG OBJECT, deleting stopped")
            print(f"STOP: {cls}[{idx}] removed {sorted(gone)}, not {uid}", flush=True)
            break
    # NO Remove Bad Wires here. archive/peer/2026-09-15-optunnelread-removebadwires-ate-the-chain.md:18,47,55 -
    # "no Remove Bad Wires anywhere inside the transient window - delete, rewire, and only then clean up"; that
    # run's orphan set was Owner node 157 and property nodes 1319/1326, three of the seven deleted here.
    left = [(c, u) for c, u in plan if u in cls_uids(c)]
    gate("B4 all nine Wire-only objects are gone", not left, f"still present {left}; deleted {sorted(deleted)}")

    # ---- B3a: the four sinks must be BARE before anything is connected ------------------------------
    by = sweep()
    bare = {N_IDENT: twire(by, N_IDENT, "reference")}
    bare.update({u: twire(by, u, "reference") for u in CONSUMERS})
    w_gobj1 = twire(by, N_U2G, "GObject")
    print(f"  after deletes: sinks {bare} | node {N_U2G}.GObject wire {w_gobj1}", flush=True)
    gate("B3a every sink to be wired is bare", all(v == 0 for v in bare.values()), str(bare))
    if any(v != 0 for v in bare.values()):
        print("STOP: refusing to connect into a wired sink (gscript.py:2206-2207 - LabVIEW re-routes and breaks it)",
              flush=True)
        return 2

    # every index below is resolved BY NAME (the v0 defect was passing names where connect2 wants indices)
    idxmap = {(N_IDENT, "reference"): tindex(by, N_IDENT, "reference"),
              (N_IDENT, "Owner"): tindex(by, N_IDENT, "Owner"),
              (N_U2G, "GObject"): tindex(by, N_U2G, "GObject")}
    idxmap.update({(u, "reference"): tindex(by, u, "reference") for u in CONSUMERS})
    print(f"  terminal indices by name: {idxmap}", flush=True)
    if any(v is None for v in idxmap.values()):
        print(f"STOP: a terminal name is not in the node's Terminals[]: "
              f"{[k for k, v in idxmap.items() if v is None]}", flush=True)
        return 2

    # ---- R1 / B2 -----------------------------------------------------------------------------------
    inv0 = g.uids(OP, "Invoke")          # baseline for the creator's junk (see purge_junk)
    print(f"  Invoke nodes before the connects: {len(inv0)}", flush=True)
    r1 = g.connect2(OP, 0, by[N_IDENT][0], tindex(by, N_IDENT, "reference"),
                    by[N_U2G][0], tindex(by, N_U2G, "GObject"))
    print(f"  R1 connect2 {N_IDENT}.reference <- {N_U2G}.GObject -> (wire delta, ExecState) {r1}", flush=True)
    by = sweep()
    a, b = twire(by, N_IDENT, "reference"), twire(by, N_U2G, "GObject")
    gate("B2 node 241 `reference` carries the UID-addressed object", bool(a) and a == b, f"{a} vs {b}")

    # ---- R2 / B3 -----------------------------------------------------------------------------------
    r2 = {}
    for u in CONSUMERS:
        r2[u] = g.connect2(OP, 0, by[u][0], tindex(by, u, "reference"),
                           by[N_IDENT][0], tindex(by, N_IDENT, "Owner"))
        print(f"  R2 connect2 {u}.reference <- {N_IDENT}.Owner -> (wire delta, ExecState) {r2[u]}", flush=True)
    by = sweep()
    w_owner = twire(by, N_IDENT, "Owner")
    reads = {u: twire(by, u, "reference") for u in CONSUMERS}
    gate("B3 `Owner` is wired and ALL THREE consumers read it",
         bool(w_owner) and all(v == w_owner for v in reads.values()), f"owner wire {w_owner}, consumers {reads}")

    # ---- purge the creator's junk Invokes, THEN clean up once, then re-check the chain ---------------
    junk = purge_junk(inv0)
    gate("B4c the four connect2 calls left no junk Invoke behind", len(g.new_since(OP, "Invoke", inv0)) == 0,
         f"purged {junk}")
    wires_after, st_rbw = g.remove_bad_wires_scripted(OP)
    print(f"  remove_bad_wires (once, at the end) -> {wires_after} wires, ExecState {st_rbw}; "
          f"delete notes {delete_notes}", flush=True)
    by = sweep()
    post = {N_IDENT: (twire(by, N_IDENT, "reference"), twire(by, N_IDENT, "Owner"))}
    post.update({u: twire(by, u, "reference") for u in CONSUMERS})
    gate("B3b Remove Bad Wires did not eat the new chain",
         twire(by, N_IDENT, "reference") == b and twire(by, N_IDENT, "Owner") == w_owner
         and all(twire(by, u, "reference") == w_owner for u in CONSUMERS), str(post))

    # ---- B5: save, then read it back in a FRESH LabVIEW -------------------------------------------
    # `g.reset()` alone would NOT have tested persistence: it clears this client's caches and leaves the VI
    # loaded, panel open, in the same instance (gscript.py:80-87). The distinction matters here more than
    # anywhere - archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:178-184 records the v0 op's
    # SAVED topology being entirely unchanged while the in-memory edits looked real. So: kill LabVIEW, wait,
    # COM-preflight, and re-read from disk. Standing restart permission, CLAUDE.md rule 3.
    st = g.exec_state(OP)
    gate("B5a ExecState == 1 before saving", st == 1, str(st))
    if st != 1:
        print("STOP: not saving a broken VI", flush=True)
        print(f"MAIN md5 after: {md5(MAIN)} (before {main_md5_before})", flush=True)
        return 1
    size = g.save(OP)
    print(f"  saved {size} bytes (LabVIEW pid {lv_pid()}); now killing LabVIEW to read it back cold", flush=True)
    fresh()
    st2 = g.exec_state(OP)
    by = sweep()
    persisted = {N_IDENT: (twire(by, N_IDENT, "reference"), twire(by, N_IDENT, "Owner")),
                 "consumers": {u: twire(by, u, "reference") for u in CONSUMERS},
                 "nodes": sorted(by)}
    print(f"  after a FRESH LabVIEW: ExecState {st2}; {persisted}", flush=True)
    gate("B5 the SAVED op is still legal in a fresh LabVIEW", st2 == 1, str(st2))
    gate("B5b the edits SURVIVED the save (deleted nodes absent, chain intact on disk)",
         all(u not in by for u in DELETE_NODES)
         and twire(by, N_IDENT, "Owner") == w_owner
         and all(twire(by, u, "reference") == w_owner for u in CONSUMERS),
         str(persisted))

    # ---- B6: functional, against the main VI, read-only ---------------------------------------------
    vi = g.op(OP)
    res = {}
    for uid, want in ((10407, ("Diagram", 639)), (1359, ("Diagram", 639))):
        res[uid] = read_owner(vi, labels, uid)
        # the self-read (nodes 307/310, still fed by wire 1081) says whether the op resolved the INPUT object at
        # all - it separates "wrong owner" from "wrong object" without another run.
        gate(f"B6a uid {uid} was resolved (self-read echoes the uid asked for)",
             res[uid]["uid_back"] == uid, f"uid_back {res[uid]['uid_back']}, class {res[uid]['cls_back']!r}")
        gate(f"B6 uid {uid} -> owner {want[0]}#{want[1]}",
             res[uid]["ownercls"] == want[0] and res[uid]["owner_uid"] == want[1],
             f"got {res[uid]['ownercls']!r}#{res[uid]['owner_uid']}")
    res[639] = read_owner(vi, labels, 639)      # RECORDED, not gated: expect WhileLoop#637
    print(f"  RECORDED diagram 639 -> owner {res[639]['ownercls']!r}#{res[639]['owner_uid']} "
          f"(docs/diagram-hierarchy.md:36 expects WhileLoop#637)", flush=True)

    # ---- B7 ----------------------------------------------------------------------------------------
    if os.path.exists(OPDELETE_V1):
        try:
            os.remove(OPDELETE_V1)
            print("  removed OpDelete_v1.vi (behaviourally identical to v0 - diag_delete_matrix.log A4)", flush=True)
        except Exception as e:
            print(f"  could not remove OpDelete_v1.vi: {e}", flush=True)
    gate("B7 OpDelete_v1.vi is gone from claudeDev", not os.path.exists(OPDELETE_V1))

    main_md5_after = md5(MAIN)
    gate("B8 the main VI is byte-identical", main_md5_after == main_md5_before,
         f"{main_md5_before} -> {main_md5_after}")
    g._lv = None
    print(f"\n=== OpOwnerChain_v1 build: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-16
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

## ?좑툘 ONE SESSION AT A TIME

Two Claude sessions ran concurrently on 2026-09-16 and both edited the active documents; the second session's copy
of `CLAUDE.md` was stale for its whole run. Before starting: check for another live session, and **re-read
`CLAUDE.md` and this file from disk** rather than trusting a summary.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`docs/cycle10-plan.md` is superseded ??it is that plan's Phase A).
   Settled decisions that must not be re-opened: **`docs/decisions.md`**.
2. ??**Gate: prior-art layer OPEN, rev6 NOT bought.** All 13 rev5 findings accepted (none argued) and the plan
   corrected ??new rows 1.9 stop/shutdown, Phase A9, A10, two 2A rows, banners in `restructure-plan-4.6.md:42` and
   `rotor-scheduler-design.md:74-75`. `REFUTED:` lines + per-finding table: end of
   `archive/peer/2026-09-16-priorart-master-plan-rev5.md`. ?좑툘 Gate hole recorded, not fixed: `guard_cycle.py`
   advises "change the plan instead" but accepts only `REFUTED:` ??a `FIXED:` form is the obvious repair.
2b. ??**Cycle-10 retrospective done, 7 VIOLATIONs, all answered.** Six slugs are at 4 occurrences across cycles
   7쨌8쨌9쨌10. Answers: `docs/violation-decisions.md` ??Round 2 (2 devices, 4 reasoned no-devices). Both devices are
   **built and tested**: the undisposed-review dispatch gate in `guard_peer.py`, and `audit_cycle.py` C4/C5 review
   cost. `violations.py` now compares decision **timestamps** (user: ??꾩뒪?ы봽 鍮꾧탳濡?怨좎튇??. Headline the
   retrospective found: **six reviews, 48 min 40 s, $28.55 ??and the declared reader never launched.**
3. ??**SOLVED ??the delete tool was never broken. Scripting EDITS are SILENTLY DECLINED until the target's FRONT
   PANEL HAS BEEN OPENED.** ?좑툘 **Say it that way, not "until the diagram is loaded"** ??that was an inference and
   it is now REFUTED by measurement (`tools/bench/diag_load_vs_editmode.log`, 2026-09-16, `rc=0 after 112s`,
   fresh copy of `OpFPLabels_v0.vi` per arm, same raw op, class `Property`, index 0):

   | first | delete |
   |---|---|
   | nothing | `4 ??4` nothing |
   | **read `VI.Block Diagram` (23C), the documented load primitive, NO window** | **`4 ??4` nothing** |
   | `OpenFrontPanel(activate=False)` | `4 ??3`, removed uid 115 |
   | 23C-loaded, panel-less, **`GObject.Move`** instead of Delete | `(853,300) ??(853,300)` did not move |

   What is **MEASURED**: only `OpenFrontPanel` makes an edit land; the decline is **general across mutator
   families** (Delete *and* Move), not delete-specific; `ensure_loaded()` therefore keeps `open_panel` and the
   name is a misnomer. What is **NOT established ??do not write it as if it were** (codex,
   `archive/peer/2026-09-16-load-vs-editmode-23c-r2.md`, ANSWERED 69 s): *"A2 did not establish diagram residency
   at mutation time??the separate loader returning creates an unload race"* ??NI closes a top-level VI's
   references when it goes idle, so the 23C-reading op may have taken the diagram back out of memory before the
   delete ran. **"Edit mode is the variable" is an inference, not a result.** Same file: no Open VI Reference flag
   pins the diagram (`0x01` = record modifications, `0x20` = hide dialogs), and a wire-count delta of 0 IS
   consistent with a successful branch.
   ?뵶 **The flag reader is at the 2-failure stop.** `Metrics:Block Diagram Loaded` = **292** and
   `Metrics:Front Panel Loaded` = **291** are verified to ATTACH (`build_property('VI Server:VI',??` ??terminals
   `DiagramLoaded` / `PanelLoaded`), but both attempts to build a reader around them died the same way
   (`tools/bench/diag_bdloaded_reader.log`): after `build_property` the VI is still **ExecState 1**, `connect2`
   DOES wire `reference` (wire uid 467) and the VI then goes **ExecState 0**, and `remove_bad_wires` does not
   clear it ??i.e. the branch from `OpReportAll_v0`'s `Open VI Reference.vi reference` into a `VI Server:VI`
   Property Node lands as a **bad wire**. Next move is codex's own design, and it is a BUILD, not a diagnostic:
   ONE op VI that reads 23C, reads `DiagramLoaded`, and deletes, holding the diagram ref live by data dependency,
   with no window ever opened.

   The A/B that put the call in 26 wrappers stands as a measurement ??`tools/bench/diag_delete_matrix.log`, same
   op / target / class / index, only `OpenFrontPanel(target)` differing:

   | | without | with |
   |---|---|---|
   | OpWireSource_v5 쨌 Property | 12 ??12, **nothing** | 12 ??**11** |
   | OpFPLabels_v0 쨌 Property | 4 ??4, **nothing** | 4 ??**3** |

   With it, **every class works** (Constant 쨌 Property 쨌 SubVI 쨌 IndexArray 쨌 Wire 쨌 ControlTerminal ??all
   removed exactly one, none removed an object of another class). The error cluster stayed `(False,0,'')` in
   *every* case, deleting or not: *"`Generic.Delete` has no semantic return value at all ??its contract is the
   side effect"* (codex). The mechanism was already in our code, in `open_panel`'s docstring, **2026-08-28**:
   *"silently declined (count unchanged, no error): the diagram is not fully in memory"* ??never generalised
   beyond `wire()`/`drop_subvi()`.
   ??**Fixed in `tools/gscript.py`**: new `ensure_loaded(target)` (idempotent, cached, cleared by `reset()`) now
   guards **26 mutating wrappers**; readers are deliberately untouched (they work unloaded, and the main VI is
   read constantly ??rule 1d).
   ?좑툘 **The old note "assume every `verify=False` delete did nothing" was WRONG** and is withdrawn: deletes
   against targets another operation had already opened *did* work ??`keystone-op-spec.md:527-529,짠33` records six
   node deletions and a 1,403-junk purge succeeding.
   ?뵶 **The same mechanism very likely explains A1's failures**: `build_opownerchain_v0.py` never calls
   `open_panel`, so its `connect2` calls were being declined too. A1 is **2 pass / 3 fail** (not "1 left").
   Reviews archived **and annotated**: prior-art cycle-11 (16 verdicts, 15 accepted), delete-silent-noop2 (codex),
   plus the earlier B2/B3, delete no-op and uid 9775 exchanges. Plan: `docs/cycle11-plan.md` **rev2**.

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle11-A1
  since: 2026-09-16 18:00
  purpose: build+run tools/recipes/build_opownerchain_v1.py (OpOwnerChain_v1.vi); reads the main VI headlessly
           for the functional gate (rule 1d, md5 checked before/after); no original is modified, no hardware.
# last held by material/cycle11-loadmode, 2026-09-16 17:2x-17:4x: diag_load_vs_editmode.py (rc=0, 112s) +
# diag_bdloaded_reader.py (rc=1, 66s, 2-failure stop). LabVIEW pid 23084 left running, no scratch VIs on disk.
```

**Verified, not assumed:** no LabVIEW process at 15:4x ??the last diagnostic's instance (pid 14352) did **not**
exit with its client and was killed explicitly. So the old note *"a COM-launched LabVIEW with no panel exits with
its client"* is **not reliable**: always `tasklist | grep -i labview` and kill a stray rather than trusting it or
this file. Fresh instances sit at ~31,500 handles; use a unique scratch VI name per run, and delete the scratch in
the same run that creates it.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (user, 2026-09-16; quote and table in CLAUDE.md rule 1b). Do not re-introduce
"the piezo is the one exception", and do not reinstate the 2026-08-27 motor ban, from any older summary. **Only the
user announces a state change**; never infer one, and do not ask per incident inside a declared state.

Instruments: rotor counter **0** (not the old 100,000 baseline ??the original VI's first absolute move would be a
200-turn trip) 쨌 magnet motor full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`. **A camera session open RESETS ROI *and* exposure**, so the acquisition loop must apply the
contract itself (`tools/bench/camera_contract.py` reads and verifies; it cannot pre-set a later run).

**No beads while disassembled**, so bead-dependent acceptance waits. Fixture work is unaffected (10,043 frames,
`archive/bench-2026-09-07-fixture/`, 13 real lost-bead frames).

## Where things stand

**Stage 1 (analysis) CLOSED** ??`docs/` holds `instrument-libraries`, `main-vi-subvi-identity` (98 call sites, 0
mismatches), `main-vi-panel-map`, `main-vi-state`, `main-vi-startup`, `frame-loop-wire-graph`,
`rotor-sign-diagnosis`. Raw data: `archive/benchmarks/INDEX.md` rows 22??1.

**Stage 2 (assembly) IN PROGRESS**, cycles 1?? done (`docs/stage2-plan.md`, `stage2-assembly-step-{a,a3,b,c,e}.md`).
`Track_v6_CPU_core_v0.vi` 69/69 PASS (INDEX row 40) 쨌 `Track_v6_CPU_queue_v0.vi` 162/162 PASS (row 41).
**Say it exactly:** both are bit-identical to the reference for the **first 10,018 frames ??those before the first
bead loss**, not all 10,043, and both are **replay** artefacts: recorded TIFFs, `FOR` loops, no live acquisition,
no stop protocol.

**THE GAP (outcome review, 2026-09-15):** 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and
**zero runnable experimental VIs**. *"The next problem is not missing tooling; it is failure to cross the boundary
from replay proof to experiment product."*

## OPEN

1. ?윞 **Is the PERIODIC auto-reset gated by `Auto-Reset`?** It decides whether an hours-long dry run terminates
   itself on `Limit of Program`. Measured 2026-09-16 (`tools/bench/diag_reset_arm.log`): the period **enters** the
   frame loop through `LoopTunnel` #10114 and the remainder **leaves** through `LoopTunnel` #10177 ??the decision is
   assembled **outside diagram 43**, so it needs A1's owner chain. The lost-bead arm *is* gated, by `And` #9647.
2. ?윟 **Autofocus decision path ??closed.** `CaseStructure #10407` fires on `(frame counter mod 25) == 0 AND
   NOT(Fix to a Certain Pattern)` ??**every 25 frames ??3.6 Hz at 90 Hz** ??and transacts serial when it fires.
   But `Fix to a Certain Pattern` is **written by code every iteration** (Property Node #1469) from
   `NOT( Auto-Focus AND NOT(reseed-And 9921) AND (counter < Limit of Auto-Focus) )`, so **the switch that stops the
   piezo is `Auto-Focus` (uid 24266)**, exactly as the user said. Derivation: `docs/camera-acquisition-facts.md`.
2c. ?윟 **uid 9775 READS the camera geometry ??and the size the VI WRITES is the FRONT-PANEL display area, not the
   camera ROI.** MEASURED 2026-09-16, both halves (the second confirms the user from memory: read the camera frame
   size, then set the IMAQ display size). Chain, divisor and caveats: `docs/camera-acquisition-facts.md`,
   "MEASURED 2026-09-16 ??uid 9775 READS the geometry". **Consequence: the plan?셲 1280횞1024 budget basis is safe.**
   ?좑툘 Do NOT widen it to "the VI does not set frame size" ??the codex review refuses that (archived, annotated);
   the residual test is `Property Items[] ??Is Write` across the 106 Property nodes. The fresh-session 640횞512 ROI
   reading stays **unexplained** and is a different thing from the 첨2 display size.
3. **19 archived reviews lack frontmatter and annotation** (audit A4 ??the cycle-10 audit counts **23**). The bulk
   `frontmatter.py` pass is safe to run now; the annotations are judgement work, not a formatting pass, and they
   are now the subject of a device (`violation-decisions.md`, Round 2, `repeated-failure-class`).
4. `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it**.
5. **Startup drives instruments**, which is *allowed* while the rig is apart and becomes a hard blocker at
   assembly: ASI `Initialize` + `Move Axis to Position` on diagrams 10 and 88, position read on 12, PI init/`MOV`/
   `GOH`/`VEL` on 1/3/4/5 (`main-vi-startup.md:22-33`). Record what each run touched; excise only when the state
   changes, and then node-by-node in the build log (rule 1a).

## NEXT

?윞 **Judgement call first (cycle 11, stage "load vs edit mode"):** the operational rule is settled and unchanged ??
edits need `open_panel`, so nothing in the fleet needs editing ??but the MECHANISM is open and the cheap route to
it is closed (flag reader at the 2-failure stop; see item 3). The remaining test is a BUILD: one op VI that reads
23C + `Metrics:Block Diagram Loaded` (292) + `Generic.Delete`, diagram ref held live by data dependency, no window.
**Is that worth a build cycle at all?** It changes no code; it changes what we write. A1 does not depend on it.

?뵶 **RE-RUN A1 as `build_opownerchain_v1.py`, and expect the `ensure_loaded` fix to carry most of it.** Do NOT
rebuild `OpDelete` ??that premise is dead, and `OpDelete_v1.vi` is byte-for-byte behaviourally identical to v0
(measured, A4 in `diag_delete_matrix.log`): the `wire_indicators` call that made it silently no-op'd. Delete it.

The A1 rewrite, all four changes justified by measurement or review:
1. **`ensure_loaded` is now automatic** in `connect2`/`delete_object`, so the silent declines should stop.
2. **Delete by Traverse class `GObject`**, resolving each uid's index from `report_all(target,"GObject")` ??this
   removes the `#1044` class question (`SubVI` vs `Node`) entirely instead of guessing it again.
3. **Deletes FIRST, then connects.** Removing the Wire-only front section leaves the three `reference` sinks bare,
   which is the only safe state to connect into. Node 241's `reference` needs its feeding **wire** deleted too.
4. **Node 482 is the third consumer of wire 751** ??predicted 2026-09-15 (`archive/peer/2026-09-15-priorart-ownerchain.md:117`), confirmed by `build_opownerchain_v0.log:143`
   (`consumers {163: 751, 1221: 751, 482: 1444}`), and missing from every fix list since.
5. **No `net_map`.** The v0 recipe walks it ~14 times through `nodes_by_uid()`; replace with one `node_terms_uid`
   sweep (creator-free, drops no junk).

**A7 is NOT next.** `pre-rig-master-plan.md:66-77` gives A7 `needs: A4, A6`, and A4?륚3?륚2?륚1; two of its three
audits are defined over A4's membership. The audits are also largely **already measured** ??the VISA census is
`motion-path-audit.md:30-99`, the UI-thread count is `g9-core-budget.md:32` (106 nodes, 88 implicit), reentrancy
property 288 and the `ASI_adjust focus-subvi.vi` instance are both on disk. **After A1 comes A2.**

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md` settled decisions** 쨌 `docs/NAMES.md` verified strings 쨌
`docs/toolkit-capabilities.md` API 쨌 `docs/restructure-plan-4.6.md` target + stages 쨌
`docs/pre-rig-master-plan.md` the plan 쨌 `archive/2026-09-16-status-session-gate-and-autofocus.md` and
`archive/2026-09-16-status-cycles-8-10-narrative.md` the reasoning behind all of it 쨌
`archive/` history (rule 4: not read in normal work).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled in this session, so here is the review in full.

# PRIOR-ART REVIEW — `tools/recipes/build_opownerchain_v1.py` (rev 3, not yet run)

**Four findings.** One is measured on this exact donor and would break the op before the first connect; one is a citation the file itself says was fixed and was not; one is a diagnostic already written for gate B5b that was never re-run after the fix it needed landed; one is the plan-of-record still prescribing a delete class this recipe rejects. **One disposition in the archived reviews is half wrong.**

**The direction is not refuted, and is settled in the plan's favour.** `docs/diagram-hierarchy.md:71-79` names `OpOwnerChain_v0` as "the link that would finish this" and states this exact change (*"`OpWireSource_v5` already performs `Generic.Owner` → `ClassName` + cast(GObject) → `UID`, seeded from a Wire; removing that Wire cast is the whole change"*). I independently confirm the premise that no existing reader returns an owner UID: `tools/gscript.py:281` (`"owner": vi.GetControlValue("Class Name 3")`) and `:291` (`("Array 4", "owner")`) — class only.

---

## PART A — THE DIRECTION

### A3 · CONTRADICTED

**(1) The `:19-24` citation round 2 found is still in the file — 27 lines above the paragraph that says it was replaced.**

> `build_opownerchain_v1.py:52` — *"Nodes go by class `Node` (MEASURED: diag_ownerchain_state.log:19-24 lists all seven under `Node`, 1044 and 1221 ONLY there)"*
> `build_opownerchain_v1.py:79-80` — *"(3) ACCEPTED: two line numbers — `diag_ownerchain_state.log:13-19` (not `:19-24`, which lists nodes this build KEEPS)…"*
> `tools/bench/diag_ownerchain_state.log:19-24` — those six lines are uids **1044, 241, 163, 1221, 482, 990**; 241, 163 and 482 are nodes this build must KEEP. The seven delete targets are at **`:13-19`**.

`:156` (the `DELETE_NODES` comment) and `:368` (the `gscript.py:2206-2207` pointer) **were** fixed, so the rev-3 brief's "both line-number defects fixed" is false for one of the two sites round 2 named. Also, neither range supports the clause it is cited for: `uid 1221 classes: ['Node']` is at **`:22`**. Release: `:52` → `:13-19`, plus `:22` for the 1221 clause. No rework.

**(2) `STATUS.md` — the document that authorises this run — still prescribes the delete class the recipe rejects.**

> `STATUS.md:182` — *"2. **Delete by Traverse class `GObject`**, resolving each uid's index from `report_all(target,"GObject")` — this removes the `#1044` class question (`SubVI` vs `Node`) entirely instead of guessing it again."*
> `build_opownerchain_v1.py:153-160` — `Node` for the seven, `Wire` for the two; `:49-53` argues `GObject` is wrong.

Round 2's A1 quoted the first line of that same NEXT block (`STATUS.md:176`) as "nothing to re-open" and did not read item 2. The recipe's argument is the better one (`tools/bench/diag_delete_matrix.log:108-116` Part C never swept `GObject`; `docs/toolkit-capabilities.md:103` puts `GObject` at 10030 against `Terminal` 5763), so the cheap release is one edit to `STATUS.md:182`.

---

## PART B — THE ARTIFACT

### B4 · ALREADY MEASURED

**(3) Deleting a node has measured WIRE collateral on this exact donor; a class-scoped `Node` diff cannot see it; and the wire most exposed is 1081 — the one B2 asserts is preserved and two KEPT nodes require.**

> `tools/bench/diag_delete_matrix.log:112` — `[C OpWireSource_v5.vi/SubVI open_panel=True] 2 -> 1 REMOVED ONE … elsewhere={'SubVI': [990], 'Wire': [1068, 1208]}` — one node delete on a copy of **this donor** took two wire objects with it (`:115` likewise removed `'Wire': [106]`).
> `tools/bench/diag_ownerchain_state.log:61` — `uid 1044 ALL terminals: [… ('reference', 1081) …]` — the first node deleted is a sink on wire 1081.
> `tools/bench/census_opwiresource_v5.log:191` node 990 `t2 'GObject' wire 1081` (source); `:200` node 307 `t0 'reference' wire 1081`; `:206` node 310 `t0 'reference' wire 1081` — both KEPT, and `reference` is required on a Property Node.
> `build_opownerchain_v1.py:368-381` — the guard is `gone = set(before) - set(cls_uids("Node"))`. Wires are not Nodes, so every wire this batch removes is invisible to it; `verify=False` (`:363`) means `delete_object` will not see it either.

Round 1 read `:112` (finding 9) only to argue `GObject` scoping breaks `len(gone)==1`; round 2's audit of refutation (6b) established that *deleting wire 1081* would break the op, and never asked whether *deleting node 1044* removes it anyway. The collateral is not uniform — `:102`/`:110` (Property 1554) and `:113` (IndexArray 151) removed no wire — so this is a measured risk, not a certainty. But nothing catches it: `w_gobj1` is printed and not gated (`:387-388`); B3a gates only that the four `reference` sinks are bare, which a vanished 1081 also satisfies; B2 (`a == b`, non-zero) passes on a brand-new wire exactly as on a preserved 1081. The first failing gate is B5a/B6a — after nine deletes, four connects and ~20 minutes.

Release, already patterned in the tree: snapshot `wb = g.uids(OP, "Wire")` around the delete batch and report the diff (`build_harness_variant.py:65-72`, `build_harness_compare.py:59-66`, `build_harness_loadcal.py:80-89`), plus three assertions before R1 — `twire(by, 990, "GObject") == 1081` and 307 / 310 `reference` == 1081. Three lines, and B2's "expected 1081, preserved" becomes checkable instead of decorative.

### B1 · ALREADY BUILT

**(4) Gate B5b's question already has a dedicated 29-second diagnostic. It aborted on its first delete because of the exact bug `ensure_loaded` has since fixed, and was never re-run.**

> `archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:183-184` states its purpose in B5b's own words: *"is separating the two worlds (**does ONE verified delete survive save + a fresh LabVIEW?**) before any rebuild."*
> `tools/bench/diag_save_persists.log:6-9` — copies the donor (`ScratchSavePersist_v0.vi`, uid 1319 present), reaches *"P1 delete uid 1319 (Property) with verify=True"*.
> `:16-19` — `RuntimeError: delete_object(Property[3]): expected 1 object gone, got 0`, from `gscript.py:1971`. `BGRUN END rc=1 after 29s` (`:20`). It ran at **15:22**; the silent-decline cause was identified later that day (`STATUS.md:36-44`) and `ensure_loaded` landed after it.

Round 2 cited this file (`:41,71,103`) as the source of the `fresh()` pattern and did not report that it never completed. So B5/B5b ask, inside a 25-minute build, the question a 29-second script was written to answer and failed for a reason that no longer exists. Release: run `diag_save_persists.py` first — if one verified delete does not survive `save` + `fresh()`, A1 cannot succeed and is not worth starting — or say in writing that the build proceeds either way and B5b is the first answer.

---

## Dispositions in the archived reviews — audited

| review · finding | claimed | my check |
|---|---|---|
| rev2 (3) contradicted | "ACCEPTED, both halves" | **HALF WRONG** — `:156`/`:368` fixed, `:52` still `:19-24`. Finding (1). |
| rev2 (1) junk Invoke | implemented (`purge_junk` + B4c) | **CORRECT.** Matches `fix_v3_starting_xy.py:17-26,39-41` and `keystone-op-spec.md:565-573` §33; `diag_delete_matrix.log:111` (*"Invoke … none present"*) confirms the `inv0` baseline is empty on this donor. |
| rev2 (2) `fresh()` | implemented | **CORRECT** — `fresh()`/`lv_pid` at `build_opconstvalue_v1.py:80-87,49-53`; the import resolves. But see (4) for what it does not discharge. |
| rev1 (6b) wire 1081 | REFUTED | **CORRECT**, citations verified (`census_opwiresource_v5.log:191,197,200,206`). Does not cover (3), which reaches 1081 via node 1044. |
| rev1 (5) re-sweep | REFUTED | **CORRECT** — `by = sweep()` at `:410` feeds R2, as `…b2-b3-failed-prediction.md:99-108` prescribes. |
| rev1 (8) | REFUTED / "survives narrowly" | **Agree with rev2** (`toolkit-capabilities.md:49`; `diag_reset_arm.log:14-17`). |
| rev1 B6 oracle | released as sound | **CORRECT** (`diagram-hierarchy.md:41-47`; `keystone-op-spec.md:592-594`). |

**Notes, deliberately without a slug** (neither blocks a build): `tools/bench/diag_delete_matrix.py:127` loads `("OpDelete_v0.vi", "OpDelete_v1.vi")`, so B7's deletion stops Part A of that diagnostic re-running — still right per `docs/cycle11-plan.md:65`, just record it. And rev2 (4) was released as *"recorded there, not taken here"*, but `STATUS.md:145-147` still says OPEN 1 *"needs A1's owner chain"* and no active document mentions the `tunnels()` + `OpWireSource_v5` route — the release is not yet true of the files.

---

```
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: already-measured
PRIOR-ART: already-built
```

**Cheapest release order:** (3) first — one wire snapshot and three assertions, and it is the one that otherwise costs the run; (4) is a 29-second script that may cost nothing and may save everything; (1) is one line number; (2) is one line in `STATUS.md`.

## Sources

(extract from answer)

## What was done with it

**All four findings ACCEPTED and acted on. None refuted — which is why the build did not run in this session; see
the note at the end.**

| # | verdict | disposition |
|---|---|---|
| 1 | contradicted | **ACCEPTED.** `build_opownerchain_v1.py:52` still carried `diag_ownerchain_state.log:19-24` (which lists 241/163/482 — nodes the build KEEPS) 27 lines above the paragraph claiming it was fixed. Now `:13-19`, with `:22` cited for the 1221 clause. The reviewer is also right that my rev-2 brief's "both line-number defects fixed" was false for one of the two sites. |
| 2 | contradicted | **ACCEPTED.** `STATUS.md`'s A1 rewrite item 2 still prescribed "Delete by Traverse class `GObject`". STATUS now says class `Node` for nodes and `Wire` for wires, with the two measurements (`diag_ownerchain_state.log:13-19`; `diag_delete_matrix.log` Part C never swept `GObject`, and `docs/toolkit-capabilities.md:103` puts `GObject` at 10030 objects against `Terminal` 5763). Plan of record and recipe now agree. |
| 3 | already-measured | **ACCEPTED — the most valuable finding of the three rounds after the junk-Invoke one.** `diag_delete_matrix.log:112` measured one SubVI delete on a copy of THIS donor also removing `Wire: [1068, 1208]`; node 1044 is a sink on wire 1081 (`diag_ownerchain_state.log:61`); and a class-scoped `Node` diff cannot see a wire disappear. New gate **B3c** re-reads wire 1081 by name at nodes 990, 307 and 310 before any connect and STOPS if it is gone, and the delete batch is bracketed by a `uids(OP,"Wire")` snapshot that is printed. Without this the first failing gate would have been B5a/B6, with the cause invisible. |
| 4 | already-built | **ACCEPTED and run.** `tools/bench/diag_save_persists.py` asks B5b's question in 29 s and had never completed: it aborted at 15:22 on `delete_object(Property[3]): expected 1 object gone, got 0`, i.e. on the silent-decline bug `ensure_loaded` fixed later that day. Re-run this session — result in `tools/bench/diag_save_persists.log`. B5/B5b stay in the recipe, as the same question asked of the real artifact rather than a scratch copy. |

**Its two no-slug notes are also accepted:** B7 deleting `OpDelete_v1.vi` stops Part A of `diag_delete_matrix.py`
re-running (still right per `docs/cycle11-plan.md:65`, recorded here), and rev-2 finding (4)'s release was "not yet
true of the files" — `STATUS.md` OPEN 1 now carries the `tunnels()` + `OpWireSource_v5` route as the cheaper
alternative to be decided by the judgement session.

**Why this review was not released, stated plainly:** all four findings were correct and were fixed or run, so
there is no honest `REFUTED:` line to write for `contradicted`, `already-measured` or `already-built` —
`guard_cycle.py` accepts only that form, and CLAUDE.md forbids `CYCLE_GUARD_OFF`. `STATUS.md` records this gate
hole ("advises 'change the plan instead' but accepts only `REFUTED:` — a `FIXED:` form is the obvious repair").
Three prior-art rounds each found real defects (round 1: 9, round 2: 6 — including the junk-Invoke purge that
would have failed the run, round 3: 4), so the reviews earned their cost; the missing vocabulary is what stopped
the build, not the reviews.

**RELEASED 2026-09-16 — the missing vocabulary now exists.** `guard_cycle.py` accepts a second form,
`FIXED: <slug> - <path>:<line> - <what changed>`, valid only if the cited path exists, was changed after this
review, and the line sits in this section (tested 5/5: valid releases · nonexistent path does not · pre-review
mtime does not · a line above this section does not · FIXED+REFUTED mix). All four findings were correct and all
four were acted on, which is exactly what this form is for:

FIXED: contradicted - tools/recipes/build_opownerchain_v1.py:52 - finding (1): the surviving `:19-24` citation is now `diag_ownerchain_state.log:13-19`, with `:22` cited for the `uid 1221 classes: ['Node']` clause.

FIXED: contradicted - STATUS.md:210 - finding (2): the A1 rewrite item no longer prescribes "delete by Traverse class `GObject`"; it says class `Node` for the seven nodes and `Wire` for the two wires, so the plan of record and the recipe agree.

FIXED: already-measured - tools/recipes/build_opownerchain_v1.py:401 - finding (3): new gate B3c reads wire 1081 back by name at kept nodes 990/307/310 before any connect and STOPS if the deletes took it, and the delete batch is bracketed by the `uids(OP,"Wire")` snapshot at :353 that makes the measured cross-class collateral visible.

FIXED: already-built - tools/bench/diag_save_persists.log:1 - finding (4): the 29-second diagnostic that had aborted at 15:22 on the silent-decline bug was re-run after `ensure_loaded` landed and completed `rc=0` in 82 s (one verified delete survived `save` + a killed/restarted LabVIEW), so B5b's question is answered before the build rather than inside it.
