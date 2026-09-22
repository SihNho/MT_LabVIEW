r"""diag_c89_execstate_factorial - THE 4-ARM FACTORIAL ON THE ROW-D BED. MEASUREMENT ONLY.

PREDICTION CONTRACT (the brief's, verbatim; a deviation is THE FINDING, not a thing to repair)
  A0 control, no mutation .......................... ExecState 0   (a CONTROL READ - reported as a ROW, never gated)
  A1 the three stray `Invoke` deletes only ......... ExecState 0   GATED
  A2 Remove Bad Wires only ......................... ExecState 0   GATED
  A3 deletes THEN Remove Bad Wires ................. ExecState 1   GATED
  Per delete: target class == 'Invoke', 6 terminals, 0 WIRED, uid echo == uid; Node census drops EXACTLY 1.
  Per RBW arm: THREE deltas (Wire census, NODE census, Diagram #686 node count) + the removed wire-uid SET
  against baseline [1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540]. A Node/tunnel disappearing
  under RBW is a rule-1a hazard and is GATED, not assumed away.
  P2 read-only: `gscript.shift_reg_left` over every WhileLoop owned by `Diagram #639`; report the FULL
  left/right shift-register uid list and membership of #4344 #4274 #4334; probe `LoopTunnel #9641`.

NOTHING IS SAVED, NOTHING IS BUILT, NO OP IS CREATED, THE BED IS NEVER MUTATED AND NEVER RUN (34(f)).
Four separate dated scratch COPIES, each md5-asserted against the bed before it is touched, all deleted in
this run; `THE FILES THIS RUN LEFT ON DISK: []` is gated by stagekit's H6.

WHAT ALREADY EXISTS (CLAUDE.md "check what exists first"; PHASE 0 grep of tools/bench/*.log + archive/peer/*.md)
  * `tools/bench/build_d1_m3a3b_rowD_clean.log:229` IS a prior A2: Remove Bad Wires on `..._bwprobe.vi`, a
    byte-identical copy of THIS bed - "Wire 1920 -> 1909 ... 11 bad wire(s); ExecState after 0". So A2 is a
    RE-MEASUREMENT with the two extra deltas the brief asks for. NO prior measurement exists of ExecState
    after deleting the stray `Invoke` nodes (A1) or after both (A3) - the greps for 4859/24012/24005 return
    only `build_d1_m3a2.log` (a DIFFERENT, purged-in-run node that happened to recycle uid 24005) and
    `build_d1_m3a3.log` (wire 4859, not node #4859).
  * `tools/stagekit.py` (pins, restart, preload, scratch, hygiene), `build_opfsinnertunnelconnect_v0.del_node`,
    `build_d1_m3a1.node_census/node_view`, `build_d1_v0.owner_of/diag_index`, `gscript.shift_reg_left`,
    `gscript.remove_bad_wires_scripted`, `gscript.node_labels`. NOTHING NEW IS WRITTEN HERE.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
STRAYS = (4859, 24012, 24005)
BASELINE_BAD = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
SR_ASK = (4344, 4274, 4334)
D639, D686, TUNNEL = 639, 686, 9641


def d_idx(p, uid):
    return [o["uid"] for o in g.report_all(p, "Diagram")].index(uid)


def n_nodes(s, p, di):
    rows, _e = s.safe("node_labels({0})".format(di), lambda: g.node_labels(p, di), [])
    return len(rows or [])


def node_count(s, p, tag):
    cen, _e = s.safe("node_census {0}".format(tag), lambda: K.mod("build_d1_m3a1").node_census(p, tag)[0], [])
    return cen or []


def do_deletes(s, p, arm):
    """Three uid-addressed deletes, each preceded by its three assertions and followed by its census delta."""
    M, C82 = K.mod("build_d1_m3a1"), K.mod("build_opfsinnertunnelconnect_v0")
    for uid in STRAYS:
        di = d_idx(p, D686)                                     # RE-READ per delete - indices shift, uids do not
        before = node_count(s, p, "{0} before #{1}".format(arm, uid))
        row = next((n for n in before if n["uid"] == uid), None)
        loc, rows = M.node_view(p, uid, [di], "{0} #{1}".format(arm, uid))
        wired = [r for r in rows if r.get("has_wire")]
        found = loc.get("found") or {}
        ok = (row is not None and row.get("class") == "Invoke" and len(rows) == 6 and not wired
              and loc.get("uid_echo") == uid and found.get("diagram_uid") == D686)
        s.gate("{0} target #{1}: class Invoke / 6 terminals / 0 wired / uid echo / on Diagram #686".format(arm, uid),
               ok, "class={0!r} terms={1} wired={2} echo={3!r} diagram_uid={4!r} pos={5!r}".format(
                   (row or {}).get("class"), len(rows), len(wired), loc.get("uid_echo"),
                   found.get("diagram_uid"), (row or {}).get("pos")))
        if not ok:
            s.fact("{0} MISMATCH -> #{1} IS NOT DELETED (the brief: do not delete a target that does not match)"
                   .format(arm, uid))
            continue
        d686_b = n_nodes(s, p, di)
        gone, _e = s.safe("{0} del_node #{1}".format(arm, uid),
                          lambda u=uid: C82.del_node(p, "Node", u, "{0} ".format(arm)))
        after = node_count(s, p, "{0} after #{1}".format(arm, uid))
        d686_a = n_nodes(s, p, d_idx(p, D686))
        s.fact("{0} DELETE #{1}: Node census {2} -> {3} ; Diagram #686 nodes {4} -> {5} ; gone={6!r}".format(
            arm, uid, len(before), len(after), d686_b, d686_a, gone))
        s.gate("{0} Node census drops by EXACTLY 1 on the #{1} delete".format(arm, uid),
               len(after) == len(before) - 1, "{0} -> {1}".format(len(before), len(after)))


def do_rbw(s, p, arm):
    """Remove Bad Wires with all THREE deltas and the removed-wire SET."""
    di = d_idx(p, D686)
    nb, wb, d6b = len(node_count(s, p, arm + " rbw before")), g.uids(p, "Wire"), n_nodes(s, p, di)
    (wires_after, es), err = s.safe("{0} remove_bad_wires_scripted".format(arm),
                                    lambda: g.remove_bad_wires_scripted(p), (None, None))
    di2 = d_idx(p, D686)
    na, wa, d6a = len(node_count(s, p, arm + " rbw after")), g.uids(p, "Wire"), n_nodes(s, p, di2)
    removed, added = sorted(wb - wa), sorted(wa - wb)
    s.fact("{0} RBW THREE DELTAS: Wire {1} -> {2} (op says {3!r}) ; NODE {4} -> {5} ; Diagram #686 nodes "
           "{6} -> {7} ; op ExecState {8!r} ; err {9!r}".format(arm, len(wb), len(wa), wires_after, nb, na,
                                                                d6b, d6a, es, err))
    s.fact("{0} RBW REMOVED WIRE UIDS ({1}): {2!r} ; ADDED: {3!r} ; baseline ({4}): {5!r} ; set-equal: {6}".format(
        arm, len(removed), removed, added, len(BASELINE_BAD), BASELINE_BAD, removed == sorted(BASELINE_BAD)))
    s.gate("{0} RBW deleted NO Node and NO node on Diagram #686 (rule-1a hazard: RBW is on record deleting a "
           "TUNNEL in this project)".format(arm), na == nb and d6a == d6b,
           "Node {0}->{1}, #686 {2}->{3}".format(nb, na, d6b, d6a))
    return removed


def phase2(s, p, owner_uid=D639):
    s.head("[P2] READ-ONLY shift-register enumeration, loops owned by Diagram #{0} - nothing wired, deleted "
           "or saved".format(owner_uid))
    s.fact("SIGNATURE (tools/gscript.py:826): shift_reg_left(target, loop_index, reg_index, left_index=0, "
           "class_name='WhileLoop') -> OpShiftRegs_v1; returns {uid, class, out, inside, left_uids, "
           "left:{uid,class,out,inside}, errors}. loop_index indexes report_all('WhileLoop').")
    V = K.mod("build_d1_v0")
    loops = g.report_all(p, "WhileLoop")
    owned = []
    for L in loops:
        (oc, ou), e = s.safe("owner_of(#{0})".format(L["uid"]), lambda u=L["uid"]: V.owner_of(p, u), (None, None))
        s.fact("P2 WhileLoop #{0} (index {1}) owner -> {2!r} #{3!r} {4}".format(L["uid"], L["i"], oc, ou, e))
        if owner_uid is None or ou == owner_uid:
            owned.append((L["i"], L["uid"]))
    s.fact("P2 WhileLoops selected (owner filter {0!r}): {1!r}  (of {2} WhileLoop(s) on the VI)".format(
        owner_uid, owned, len(loops)))
    named = []
    for li, luid in owned:
        for ri in range(8):
            r, e = s.safe("shift_reg_left(loop {0}, reg {1})".format(li, ri), lambda i=li, j=ri:
                          g.shift_reg_left(p, i, j, 0))
            if not r or not r.get("uid"):
                break
            lefts = [int(u) for u in (r.get("left_uids") or [])]
            named.append({"loop_index": li, "loop_uid": luid, "reg_index": ri, "right": int(r["uid"]),
                          "right_class": r.get("class"), "left_uids": lefts,
                          "left_class": (r.get("left") or {}).get("class"), "errors": r.get("errors"), "err": e})
            s.fact("P2   loop {0} reg {1}: RIGHT #{2} ({3}) ; LEFTS {4!r} ({5}) ; errors {6!r}".format(
                li, ri, r["uid"], r.get("class"), lefts, (r.get("left") or {}).get("class"), r.get("errors")))
    allu = sorted({n["right"] for n in named} | {u for n in named for u in n["left_uids"]})
    s.fact("P2 FULL shift-register uid list the op names on Diagram #639 ({0}): {1!r}".format(len(allu), allu))
    for u in SR_ASK:
        s.fact("P2 MEMBERSHIP #{0}: {1}".format(u, "PRESENT" if u in allu else "ABSENT"))
    tun = sorted(g.uids(p, "LoopTunnel"))
    (toc, tou), te = s.safe("owner_of(LoopTunnel #{0})".format(TUNNEL), lambda: V.owner_of(p, TUNNEL), (None, None))
    s.fact("P2 LoopTunnel #{0}: in report_all('LoopTunnel') ({1} rows) -> {2} ; owner_of -> {3!r} #{4!r} err {5!r}"
           .format(TUNNEL, len(tun), TUNNEL in tun, toc, tou, te))
    s.R["p2"] = {"loops_on_639": owned, "registers": named, "all_uids": allu,
                 "membership": {u: (u in allu) for u in SR_ASK},
                 "tunnel_9641": {"in_looptunnel_census": TUNNEL in tun, "owner": [toc, tou], "err": te}}


def main(s):
    s.start()
    s.discard_work()                                  # the work copy IS arm A0's scratch; nothing is saved
    s.head("[A0] CONTROL - no mutation. PREDICTED ExecState 0. Reported as a VALUE, never gated.")
    s.row("A0 ExecState (control, no mutation)", s.es("A0 control"), 0)
    s.census(tag="A0 control")
    s.fact("A0 Diagram #686 node count: {0}".format(n_nodes(s, s.work, d_idx(s.work, D686))))
    # P2ALL=1: the SAME read-only enumeration with the owner filter OFF. Run 1 measured that Diagram #639
    # owns NO WhileLoop, so the briefed filter selected an empty set and the membership answer carried no
    # information; this pass answers it over the loops that DO exist. No arm runs, nothing is mutated.
    if "--p2-all" in sys.argv:
        phase2(s, s.work, owner_uid=None)
        return
    phase2(s, s.work)

    for arm, deletes, rbw, pred in (("A1", True, False, 0), ("A2", False, True, 0), ("A3", True, True, 1)):
        if s.left_s() < 180:
            s.gate("{0} had time to run inside the deadline".format(arm), False, "left {0:.0f} s".format(s.left_s()))
            break
        p = s.scratch(arm.lower())
        s.head("[{0}] deletes={1} remove_bad_wires={2}. PREDICTED ExecState {3}.".format(arm, deletes, rbw, pred))
        s.gate("{0} scratch md5 == the bed's before anything is touched".format(arm),
               K.md5(p) == BED_MD5, K.md5(p), fatal=True)
        if deletes:
            do_deletes(s, p, arm)
        if rbw:
            do_rbw(s, p, arm)
        got = s.es("{0} final".format(arm), target=p)
        s.row("{0} ExecState".format(arm), got, pred)
        s.gate("{0} ExecState == the PREDICTED {1}".format(arm, pred), got == pred, "observed {0!r}".format(got))
        s.drop_scratch(p, "H4 {0}".format(arm))


S = K.Stage(BED, BED_MD5, "diag_c89_execstate_factorial", deadline_min=21.0, reserve_s=260.0,
            out_json=os.path.join(K.BENCH, "diag_c89_execstate_factorial.json"),
            task="4-arm ExecState factorial on the Row-D bed; measurement only, nothing saved")
sys.exit(K.run(main, S))
