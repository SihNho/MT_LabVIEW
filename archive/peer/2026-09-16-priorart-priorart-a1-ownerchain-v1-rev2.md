# priorart-priorart-a1-ownerchain-v1-rev2

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.8660  in 64 / out 44005 / cache-create 222049 / cache-read 5090128  (621s, 47 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (625s)
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
REVISION 2 OF THE A1 BUILD (cycle 11, Stage 3) ??the plan CHANGED in response to your own round-1 review.

Round 1 is archived at `archive/peer/2026-09-16-priorart-priorart-a1-ownerchain-v1.md`; its nine findings and
their dispositions are in that file's "What was done with it" table, and the two refutations are the two
`REFUTED:` lines at its end. What changed, in one line each:
  (2) Remove Bad Wires moved OUT of the transient window: one call, after the connects, plus a new gate B3b that
      re-reads the whole chain afterwards.
  (3)+(9) delete class `GObject` dropped: nodes go by class `Node` (measured, diag_ownerchain_state.log:19-24),
      wires by class `Wire`, each with a CLASS-SCOPED before/after uid diff and `verify=False`.
  (6a) wires 318 and 751 are now deleted EXPLICITLY, before the nodes.
  (7) a new gate B4b MEASURES report() vs report_all() uid order for `Wire` and `Node` before using an index.
  (1), (4), (8) released in writing inside the recipe's docstring (scope sentence, citation fixed to
      gscript.py:2206-2207, and why OpTunnelRead_v0 does not reach OPEN 1's object).
  (5), (6b) refuted with citations - see the two REFUTED: lines.

WHAT IS UNDER REVIEW NOW IS THE RECIPE FILE ITSELF, verbatim below. It has not been run. Review the ARTIFACT as
written: has this been built, measured, tried or refuted before, and does any fact it cites conflict with another
file? Please check the ROUND-1 DISPOSITIONS too - if one of my refutations is wrong, say so with the citation.

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
     tools/bench/diag_ownerchain_state.log:19 - `uid 1044 classes: ['Node']`. v1 deletes every node under class
     `Node` and every wire under class `Wire`, and asserts each uid is in that class's list before deleting.
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
import gscript as g  # noqa: E402

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
# tools/bench/diag_ownerchain_state.log:19-24 - all seven are enumerated under `Node` (1044 and 1221 ONLY there),
# which is also the class docs/cycle11-plan.md:120 settled on after v0 died with "1044 is not in list".
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
        print("STOP: refusing to connect into a wired sink (gscript.py:2110 - LabVIEW re-routes and breaks it)",
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

    # ---- clean up ONCE, now that the graph is complete, and re-check that it did not eat the chain --
    wires_after, st_rbw = g.remove_bad_wires_scripted(OP)
    print(f"  remove_bad_wires (once, at the end) -> {wires_after} wires, ExecState {st_rbw}; "
          f"delete notes {delete_notes}", flush=True)
    by = sweep()
    post = {N_IDENT: (twire(by, N_IDENT, "reference"), twire(by, N_IDENT, "Owner"))}
    post.update({u: twire(by, u, "reference") for u in CONSUMERS})
    gate("B3b Remove Bad Wires did not eat the new chain",
         twire(by, N_IDENT, "reference") == b and twire(by, N_IDENT, "Owner") == w_owner
         and all(twire(by, u, "reference") == w_owner for u in CONSUMERS), str(post))

    # ---- B5: save, forget everything, reopen -------------------------------------------------------
    st = g.exec_state(OP)
    gate("B5a ExecState == 1 before saving", st == 1, str(st))
    if st != 1:
        print("STOP: not saving a broken VI", flush=True)
        print(f"MAIN md5 after: {md5(MAIN)} (before {main_md5_before})", flush=True)
        return 1
    size = g.save(OP)
    g.reset()
    st2 = g.exec_state(OP)
    print(f"  saved {size} bytes; after reset+reopen ExecState {st2}", flush=True)
    gate("B5 the SAVED op is still legal", st2 == 1, str(st2))

    # ---- B6: functional, against the main VI, read-only ---------------------------------------------
    vi = g.op(OP)
    res = {}
    for uid, want in ((10407, ("Diagram", 639)), (1359, ("Diagram", 639))):
        res[uid] = read_owner(vi, labels, uid)
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

# PRIOR-ART REVIEW — `build_opownerchain_v1.py` (rev 2, not yet run)

**Verdict: 6 findings. One of them (the junk-Invoke purge) is a protocol this project wrote down, applied in the only other recipe that calls `connect2`, and this rewrite silently dropped when it removed `net_map`. Two more are gates that do not measure what they claim. I confirm two of your three round-1 refutations and narrow the third.**

---

## PART A — THE DIRECTION

### A1 · SETTLED ALREADY — in the plan's favour, no slug

`STATUS.md` → NEXT: *"🔶 **RE-RUN A1 as `build_opownerchain_v1.py`**, and expect the `ensure_loaded` fix to carry most of it"*, and B7 (delete `OpDelete_v1.vi`) is decided in the same paragraph. Nothing to re-open.

Also released, because I checked and it is clean: deleting under Traverse class **`Node`** is established practice, not a guess — `tools/recipes/build_harness_copy.py:83`, `build_gpu_kernel.py:92`, `build_harness_gpu2.py:99`, `build_opclfnparams.py:101`, `tools/bench/astra_wiring_bench.py:38` all delete by `"Node"`. Round-1 finding (3) was disposed correctly.

---

### A4 · UNREAD EVIDENCE

**(1) `connect2` drops a junk Invoke node on the target per run, the purge protocol is written in our spec, and this recipe calls it four times and never purges. `net_map` — the thing rev 2 removed — is what was silently paying this bill in v0.**

> `docs/keystone-op-spec.md:565-573`, §33 — *"OpNetInfo_v1 / **OpConnect2_v0** keep the erdosmiller `Create Invoke Node.vi` … empty class/ID strings still make it drop an untyped Invoke node — 1,403 junk nodes on a scratch in one net_map … **Protocol: every use of these ops on a target is followed by `new_since(target,"Invoke")` → delete each junk Invoke → Remove Bad Wires** (fix_v3_starting_xy.py `purge_junk`)."*
> `tools/recipes/fix_v3_starting_xy.py:5-6` — the same sentence, in the docstring of **the only other recipe in the tree that calls `connect2`**; `:17-26` is `purge_junk`; `:39-41` is `connect2`, `connect2`, **`purge_junk`**.
> `tools/gscript.py:2308-2317` — junk Invokes "left it ExecState 0 … it explains … why every ladder probe and **three OpReportNodes builds ended broken** — they had called net_map on the target."
> `tools/bench/build_opownerchain_v0.log:51-59` — v0's second pass purged **166** junk Invokes. That purge was `net_map`'s, and rev 2's change (5) deleted `net_map` from the recipe without moving the purge anywhere.

`connect2` (`tools/gscript.py:2432`) now also calls `ensure_loaded`, i.e. the target's panel is open for every one of the four calls, which is the state `docs/toolkit-capabilities.md:54-56` says junk lands on (*"junk Invokes land only on an open target"*).

**Predicted outcome as written:** four untyped Invoke nodes on `OpOwnerChain_v1`, gate **B3b**/`B5a` reading `ExecState 0`, and — if the single Remove Bad Wires happens to clear it — four junk nodes **saved into the op**. Release path: snapshot `uids(OP,"Invoke")` before R1 and run `purge_junk` after the connects (before the final Remove Bad Wires), or show in writing that `OpConnect2_v0`'s creator has since been removed.

**(2) Gate B5 cannot tell "saved to disk" from "still in this LabVIEW's memory" — and that is the exact distinction the v0 post-mortem could not make, which is why `fresh()` was brought in.**

> recipe: *"B5 ExecState == 1 before the single save; after `save` + `g.reset()` + reopen it is STILL 1."*
> `tools/gscript.py:80-87`, `reset()` — *"Forget the Application AND every cached op-VI proxy."* It clears `_lv`, `_cache`, `_loaded`. **It does not restart LabVIEW.** The next `exec_state(OP)` re-acquires a reference to the same still-loaded (panel-open) VI in the same instance.
> `archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:178-184` — *"`tools/bench/diag_ownerchain_state.log` read the SAVED op and found the donor's topology entirely unchanged … The connects' in-memory effects (1208, 1444) were gone … `tools/bench/diag_save_persists.py` is separating the two worlds (**does ONE verified delete survive save + a fresh LabVIEW?**) before any rebuild."*
> `tools/bench/diag_save_persists.py:41,71,103` — `from build_opconstvalue_v1 import fresh`, called around the save.
> `tools/recipes/build_opconstvalue_v1.py:80-87`, `fresh()` — kills the LabVIEW process, sleeps 8 s, `g.reset()`, `com_preflight()`.

The recipe already reads that file (`MAIN` is annotated *"verbatim from tools/recipes/build_opconstvalue_v1.py:42"`), so the helper was one line away. Release path: call `fresh()` between `save` and the re-read, or state in writing that B5 claims in-memory legality only — and then do not let B5 stand as the answer to "did the edits persist", which is still open from 2026-09-16.

---

### A3 · CONTRADICTED

**(3) The line reference for the delete class does not say what it is cited for, and the wrong `gscript.py` pointer that round-1 finding (4) fixed is still live inside the code.**

> recipe (twice — docstring and the `DELETE_NODES` comment): *"MEASURED in `tools/bench/diag_ownerchain_state.log:19-24` — all seven are enumerated under `Node`"*
> `tools/bench/diag_ownerchain_state.log:19-24` — those six lines are uids **1044, 241, 163, 1221, 482, 990**. Four of them are not delete targets; three of them (241, 163, 482) are nodes the build must **keep**. The seven delete targets are at **`:13-19`** (145, 151, 157, 1319, 1326, 1329 at `:13-18`, 1044 at `:19`).
>
> recipe, B3a stop branch: `print("STOP: refusing to connect into a wired sink (gscript.py:2110 - LabVIEW re-routes and breaks it)")`
> `tools/gscript.py:2108-2110` — `except RuntimeError as e:` / `if "modal dialog" not in str(e):` / `raise` — `move_object`'s handler, exactly as round-1 finding (4) said.

The docstring fixed the pointer to `:2206-2207` (which I verified is correct) and then the executable line printed the wrong one anyway. That is the fifth appearance of this pointer in a build that claims to have retired it. Release path: change `:19-24` → `:13-19` and `:2110` → `:2206-2207`. No rework.

---

## PART B — THE ARTIFACT

### B4 · ALREADY MEASURED

**(4) "Which diagram does this node live on" is already measured for the whole main VI — for every node, not just the five structure classes the docstring's release sentence allows. And the motivating case's driving node is reachable today with two verified ops, one of which is the donor.**

> recipe, release of finding (1): *"for the five catalogued structure classes, structure -> home diagram is already a lookup in `tools/bench/diagram_tree_main.json` … This op exists for what that file does NOT hold"*
> `tools/bench/diagram_tree_main.py:67-68` — `nodes, _ = g.net_map(WORK, diagram_index=k, …)` / `uids = [uid for uid, _lbl, _t in nodes.values()]`. The per-diagram `uids` list is **net_map's full NODE list**, not a structure roster.
> `tools/bench/diagram_tree_main.json:370-405` — diagram 43's list holds `5058` (SubVI), `10068` (**Function**), `10950` (Comparison), `1359`, `10407`, … The structures roster is a *separate* key (`:54-55` of the script).

So node → home diagram is a lookup for every node the walk saw, and the recipe's own scope sentence understates its own prior art.

For **OPEN 1** specifically, the hop the recipe says is unreached is one op short of reached:

> `docs/toolkit-capabilities.md:24` — `tunnels(target, index)` returns the tunnel's **outer terminal (name / source? / wire)**, 132 tunnels censused.
> `docs/toolkit-capabilities.md:48` — `OpWireSource_v5` = *"**which object drives a wire** — addressed by UID … per terminal: `Is Source?`, reciprocal wire, **owner class + owner `UID`**"*, verified *"row 43: wire 10850 → constant 10739 / sink Comparison 10950, 12/12"*.
> `tools/bench/diag_reset_arm.log:14-17` — this pair was **already run on this exact question**: *"RESULT wire 10103: source ('LoopTunnel', 10114); sinks [('Function', 10068)]"*, and `:27-28` even returns `owner 'Diagram' uid 639`.

**Scope, precisely — this does not kill the op.** I verified the recipe's negative claim myself: `10114` and `10177` appear **0 times** in `diagram_tree_main.json`, and the walk is capped at `max_nodes=120` per diagram (`diagram_tree_main.py:67`), so the JSON is not a general answer. But the measurement that would tell you whether A1 is needed for OPEN 1 at all — read the **outer** wire of 10114/10177 with `tunnels()`, hand it to `OpWireSource_v5`, look the driver's uid up in the JSON — costs two op runs and has never been run. Release path: run it, or say in writing why the answer would not change the decision.

**(5) Gate B4b re-measures a comparison already recorded in the helper it calls, and does not measure the pair the review it answers actually named.**

> recipe: *"(7) cross-op Traverse index transfer is MEASURED before it is used, not assumed (gate B4b)"* — B4b compares `report(OP, cls)` vs `report_all(OP, cls)`.
> `tools/gscript.py:823-827`, `uids()` — *"report_all, not report: one op run instead of one per object (**rows verified IDENTICAL 2026-09-13**)."*
> `tools/gscript.py:2095`, `move_object` — *"the `index`-th object of class `cls` (**Traverse order, same as `report()`**)"*, and `move_object` was *"built by script on 2026-09-06 **from OpDelete_v0**"* (`:2097`).
> `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:28-30` — *"Do not assume indices from `OpReportAll_v0` select the same objects in `OpReport_v3`-derived operations … Do not assume a cached index remains stable across executions, reloads, **edits**, or sessions … If index selection remains anywhere, **retain the UID identity gate on every read**."*

B4b runs **once, before nine edits**, and compares two reporters — never `OpDelete_v0`'s own Traverse, which is the third enumeration and the one that selects the victim. The thing that actually protects this build is the per-delete `gone == {uid}` diff, which is `:30`'s prescription. Release path: one sentence saying B4b re-confirms `gscript.py:824` on this target and these classes, and that the identity gate, not B4b, is the guard.

### B3 · HELPER EXISTS

**(6) The per-delete class-scoped before/after diff is `delete_object(..., verify=True)`, re-implemented.**

> recipe: `g.delete_object(OP, cls, idx, verify=False)` then `gone = set(before) - set(cls_uids(cls))`, stop unless `gone == {uid}`.
> `tools/gscript.py:2054,2085-2087` — `before = uids(target, cls) if verify else None` … `gone = before - uids(target, cls)` … `if len(gone) != 1: raise`. Same snapshot, same class scope, same op runs.
> `tools/gscript.py:2045-2048` — *"⚠️ **verify=False MEANS THIS CALL CANNOT TELL YOU WHETHER IT DELETED ANYTHING** … Use verify=False only with a snapshot around the batch, and never as a way to make a failing delete quiet."*

Round-1 finding (9) justified `verify=False` by `GObject`'s cross-class collateral; with the class now `Node`/`Wire` that reason is gone, and `verify=True` gives an identical check for free. Release path: one written sentence — *"we keep our own diff so the loop STOPS on the first mismatch instead of raising mid-batch"* — which is a real difference and costs nothing to say.

---

## Round-1 dispositions — audited against the files

| # | your disposition | my check |
|---|---|---|
| 5 | **REFUTED** (the sweep between R1 and R2 exists) | **CORRECT.** `by = sweep()` runs immediately after R1, and R2's `by[u][0]` / `tindex(by, N_IDENT, "Owner")` come from it. The citation does not cover this build. |
| 6b | **REFUTED** (wire 1081 must not be deleted) | **CORRECT, and the citation is exact.** `tools/bench/census_opwiresource_v5.log:197,200,206` — node 1044 `reference` 1081, node **307** `reference` **1081**, node **310** `reference` **1081**. Deleting 1081 would bare two required `reference` inputs, and `archive/peer/2026-09-15-opwiresource-fail3-branch-wire-is-one-object.md:24` (*"deleting the Wire GObject removes the complete net — including the healthy sink"*) makes that certain, not likely. |
| 8 | **REFUTED** (no existing op reaches OPEN 1's object) | **SURVIVES NARROWLY.** `docs/toolkit-capabilities.md:49` does give `OpTunnelRead_v0` the *inner* frame diagram, so your reading is right, and no op gives a node's home diagram. But the clause *"the node DRIVING the outer terminal … which no existing op reaches"* is wrong about the **node**: `tunnels()` + `OpWireSource_v5` reach it, and `diag_reset_arm.log:14-17` already did. Filed as finding (4), not as a re-opening of (8). |
| 1, 2, 3, 4, 6a, 7, 9 | accepted / implemented | Verified present in the file. (2) is implemented exactly as the `optunnelread` review prescribes; (3)'s class choice is well-supported prior art; (4)'s docstring fix is right but see finding (3) for where the old pointer survives. |

Also verified clean, so nobody re-checks them: B0's expected topology (`census_opwiresource_v5.log:152,161,183,221` — 241.`reference` 318; 163/1221/482 `reference` 751), the `:57-59` and `nodes 11/12/10` citations, and every `gscript.py` line number in the docstring except the two named above.

---

```
PRIOR-ART: unread-evidence
PRIOR-ART: unread-evidence
PRIOR-ART: contradicted
PRIOR-ART: already-measured
PRIOR-ART: already-measured
PRIOR-ART: helper-exists
```

**Cheapest release path:** (1) is one `purge_junk` call and a snapshot — it is the one that will otherwise cost the run. (2) is `fresh()`, already imported elsewhere. (3) is two line numbers. (5) and (6) release in a sentence each. (4) releases either by one written argument or, better, by two op runs that may make the whole build unnecessary for OPEN 1 — that is the one worth spending ten minutes on before the 25-minute batch.

## Sources

(extract from answer)

## What was done with it

**Three findings implemented, three released in writing — and finding (1) is the one that would have cost the
run.** All changes are in `tools/recipes/build_opownerchain_v1.py` and were made before it was ever executed.

| # | verdict | disposition |
|---|---|---|
| 1 | unread-evidence | **ACCEPTED, and it is the finding that saves this run.** `OpConnect2_v0` carries the erdosmiller creator and drops one untyped Invoke on the TARGET per call (`docs/keystone-op-spec.md:565-573` §33; `tools/gscript.py:2308-2317` — three OpReportNodes builds left `ExecState 0` by exactly this). v0's four `net_map` walks were purging them as a side effect (`build_opownerchain_v0.log:51-59`, "166 junk Invoke(s)"), and rev 2 removed `net_map` without moving the purge. The recipe now snapshots `uids(OP,"Invoke")` before R1, calls a local `purge_junk()` after the connects and before the single Remove Bad Wires — the order `fix_v3_starting_xy.py:39-41` uses — and gate **B4c** fails if any junk survives. |
| 2 | unread-evidence | **ACCEPTED.** `g.reset()` (`tools/gscript.py:80-87`) clears this client's caches and leaves the VI loaded in the same instance, so the old B5 could not tell "saved" from "still in memory" — the exact distinction `archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md:178-184` left open for this op. B5 now calls `fresh()` (`build_opconstvalue_v1.py:80-87`: kill LabVIEW, 8 s, `reset`, COM preflight) and a new gate **B5b** re-reads the topology cold from disk: deleted nodes absent, `Owner` wire intact, all three consumers on it. |
| 3 | contradicted | **ACCEPTED, both halves.** `diag_ownerchain_state.log:19-24` does list 241/163/482 — nodes this build KEEPS; the citation is now `:13-19` in both places. The `gscript.py:2110` that survived inside the B3a stop message is now `:2206-2207` (it was fixed minutes after this review was dispatched, so the reviewer read the older file). |
| 4 | already-measured | **RELEASED IN WRITING, with the scope the reviewer asked for.** `diagram_tree_main.json`'s per-diagram `uids` are net_map's full node lists (`tools/bench/diagram_tree_main.py:67-68`), so node → home diagram is a lookup for every node that walk SAW — the recipe's docstring now says this instead of "the five catalogued structure classes". It is still not a general answer: the walk is capped at `max_nodes=120` per diagram and neither 10114 nor 10177 appears in the file (the reviewer verified this independently). **The reviewer's better idea is recorded, not taken:** `tunnels()` + `OpWireSource_v5` on the OUTER wire of 10114/10177 plus a JSON lookup — two op runs — might answer OPEN 1 without A1 at all (`tools/bench/diag_reset_arm.log:14-17` shows the pair already doing this shape of read). Whether that makes A1 unnecessary for OPEN 1 is a scope decision, and this session is material: it goes to the judgement session as an OPEN item, with A1 built either way since `STATUS.md`'s NEXT and `docs/pre-rig-master-plan.md`'s A2←A1 both depend on it. |
| 5 | already-measured | **RELEASED IN WRITING.** Correct: B4b compares two reporters and never reaches `OpDelete_v0`'s own Traverse, which is the enumeration that selects the victim. `gscript.py:824` already recorded the two reporters as identical on 2026-09-13. The docstring now says B4b is a cheap precondition and that the per-delete `gone == {uid}` identity diff — `archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:30`'s actual prescription — is the guard. B4b is kept because it costs two runs and its failure would invalidate the whole delete plan up front. |
| 6 | helper-exists | **RELEASED IN WRITING, in the reviewer's own words.** The diff is `delete_object(verify=True)` re-implemented, and the difference is the reason: this loop STOPS at the first mismatch and logs WHICH uid vanished, where the wrapper raises mid-batch with only a count (`gscript.py:2086`). Written into the docstring. |

**Round-1 refutations audited:** (5) and (6b) confirmed CORRECT by this reviewer against the files, (8) "survives
narrowly" — its claim about `OpTunnelRead_v0` is right, but the clause "no existing op reaches the driving node"
is wrong, and that correction is finding (4) above, now carried in the docstring.

REFUTED: already-measured - findings (4) and (5). `tools/bench/diagram_tree_main.py:67` caps the walk at
`max_nodes=120` per diagram and the reviewer itself verified 10114 / 10177 appear **0 times** in
`diagram_tree_main.json`, so that measurement does not cover the objects this op exists for; and
`tools/gscript.py:824`'s "rows verified IDENTICAL" is about the two REPORTERS, which is exactly what B4b
re-confirms on this target - neither line reaches `OpDelete_v0`'s own Traverse, so neither makes the identity
gate redundant.

REFUTED: helper-exists - `tools/gscript.py:2085-2087` raises `expected 1 object gone, got N` and reports only a
COUNT, mid-batch; the recipe's own diff names the uid that actually disappeared and STOPS the loop before the
next index is used. The cited helper does not cover that behaviour, which is the whole point of doing nine
indexed deletes in a row. (The reviewer proposed this same sentence as the release path.)

**The remaining two slugs are released as FIXED, not refuted** (`guard_cycle.py` gained that form on 2026-09-16):

FIXED: unread-evidence - tools/recipes/build_opownerchain_v1.py:442 - findings (1) and (2): `purge_junk()` (:231) now runs after the connects and before the single Remove Bad Wires, with gate B4c at :443 failing if any junk Invoke survives; and B5 calls `fresh()` (:469, kill + 8 s + COM preflight) with new gate B5b at :477 re-reading the topology cold from disk.

FIXED: contradicted - tools/recipes/build_opownerchain_v1.py:52 - finding (3): the `diag_ownerchain_state.log` citation is `:13-19` (with `:22` for the 1221 clause), not `:19-24` which lists nodes this build keeps, and the B3a stop message cites `gscript.py:2206-2207` (:391) rather than `:2110`.
