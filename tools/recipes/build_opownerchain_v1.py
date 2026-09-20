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
    diag_ownerchain_state.log:13-19 lists all seven under `Node`; 1044 ONLY there, at :19, 1221 at :22),
    wires by class `Wire`.
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
    Invoke on the target per call (docs/keystone-op-spec.md:565-573 §33) and v0's `net_map` calls were silently
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

THIRD PRIOR-ART REVIEW: archive/peer/2026-09-16-priorart-priorart-a1-ownerchain-v1-rev3.md (claude/opus, 578 s,
4 verdicts, all accepted):
  * (1) the `:19-24` citation survived at one of the two sites round 2 named - fixed above.
  * (2) `STATUS.md:182` still prescribed deleting by class `GObject`; STATUS is corrected to `Node`/`Wire` with
    the reason, so the plan of record and the recipe agree.
  * (3) THE IMPORTANT ONE: deleting a node has MEASURED wire collateral on this very donor
    (tools/bench/diag_delete_matrix.log:112 - one SubVI delete also removed `Wire: [1068, 1208]`), node 1044 is a
    sink on wire 1081 (diag_ownerchain_state.log:61), and a class-scoped `Node` diff cannot see a wire vanish.
    New gate **B3c** reads 1081 back by name at nodes 990 / 307 / 310 before any connect, and the whole delete
    batch is bracketed by a Wire-uid snapshot. Without it the first failing gate would have been B5a/B6, twenty
    minutes later, with the cause invisible.
  * (4) `tools/bench/diag_save_persists.py` already asks B5b's question in 29 s and never completed - it aborted
    on `delete_object: expected 1 object gone, got 0` at 15:22, i.e. on the silent-decline bug `ensure_loaded`
    fixed later the same day. It is re-run IMMEDIATELY BEFORE this recipe, in the same batch, and this build is
    not worth starting if a verified delete does not survive save + a fresh LabVIEW.

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
    class/ID strings (docs/keystone-op-spec.md:565-573 §33; gscript.py:2308-2317 records three OpReportNodes
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
    # WIRE COLLATERAL IS MEASURED ON THIS DONOR, and a class-scoped `Node` diff cannot see it:
    # tools/bench/diag_delete_matrix.log:112 - deleting ONE SubVI on a copy of OpWireSource_v5 also removed
    # `Wire: [1068, 1208]`. Node 1044 is a SINK on wire 1081 (diag_ownerchain_state.log:61), and 1081 also feeds
    # the `reference` of KEPT nodes 307 and 310 (census_opwiresource_v5.log:200,206) - a required input. So the
    # whole batch is bracketed by a Wire snapshot, and B3c below checks 1081 by name before anything is connected.
    wires_before = g.uids(OP, "Wire")
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

    # B3c: the deletes must NOT have taken wire 1081 with them. Measured collateral, see wires_before.
    wires_gone = wires_before - g.uids(OP, "Wire")
    keep = {990: twire(by, N_U2G, "GObject"), 307: twire(by, 307, "reference"), 310: twire(by, 310, "reference")}
    print(f"  wires removed by the delete batch: {sorted(wires_gone)} (expected exactly {sorted(wire_targets)} "
          f"plus branches of deleted nodes); wire 1081 endpoints now {keep}", flush=True)
    keep_ok = w_gobj0 and all(v == w_gobj0 for v in keep.values())
    gate("B3c the UID-to-GObject wire survived the deletes and still feeds kept nodes 307/310",
         keep_ok, f"{keep} vs {w_gobj0}")
    if not keep_ok:
        print("STOP: wire 1081 did not survive - nodes 307/310 `reference` would be left bare (required input), "
              "and B2's 'branch preserves the wire' premise is void", flush=True)
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
