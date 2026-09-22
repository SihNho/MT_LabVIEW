r"""stage_d1_m3a3_rowD - M3a-3b ROW D on `tools/stagekit.py`: STATUS NEXT's FIRST ACT, delete THEN connect.

THE ROW: `FlatSequenceInnerTunnel #7468`'s LeftTerm `#7488` is fed by the OLD `RightShiftRegister #4334`
through wire `7506`; it must be fed by the NEW `RightShiftRegister #23868`. (1) delete 7506 so the net has
ZERO sources - **and NO Remove Bad Wires anywhere** (plan 111a: c83's `error 1055` may have been
`remove_bad_wires_scripted` deleting the tunnel one line after `del_wire`, `diag_c83_connect2x2_r2.py:449`;
refused as a rule-1a hazard at `docs/cycle27-plan.md:1860-1862`); (2) re-read `#7488`, require it BARE;
(3) `OpFsInnerTunnelConnect_v1` from the NEW loop's `Outgoing Handle` (Diagram #686 / Nodes[21] /
Terminals[1], owner `#23868` by Pre-decided 120) to `#7488`; (4) junk purge; (5) the gates; (6) ONE save.
🔴 BROKEN BY DESIGN, NEVER RUN (34(f)). No new op/device, no motor/ASI/camera.
INPUT - ⚠️ A FORK THIS FILE DOES NOT DECIDE. STATUS NEXT names `D1_s3b_m3a2_20260922_023029.vi`, but ROW C
was DELIVERED on top of it as `D1_s3b_m3a3_20260922_081056.vi` (`33ef524e...`) and EVERY address this row
uses was measured ON THAT BED (c81-c84); from M3a-2 the row would discard Row C and use uids never verified
there, so `INPUT` is the BED and the fork goes to judgement.
ALREADY MEASURED, and this run RE-ASSERTS rather than discovers it (prior-art c87 A1/A4): `diag_c86_norbw.py`
ran this exact sequence on a byte-identical scratch of this bed with RBW rebound to a raising guard and the
same op - D1 `uid_back=7468`/`term_a_uid=7488`/`wire_a=0` (`tools/bench/diag_c86_norbw.log:74-77`), D0 wire
25324 on BOTH ends, `wire_delta 1` (`:87`), D2/D3/D4 `[('RightShiftRegister', 23868)]`, `#4334` off, PD85 0
(`:105-110`). c86 SAVED NOTHING and deleted its scratch (`:113`), so what is NEW here is the SAVE, D5, D6, D7.
GATES, each printing the value it compared: D1 the FSIT still RESOLVES and `#7488` is BARE after the delete ·
D0 a wire was written · D2 ONE source terminal, owner `#23868` · D3 the OLD `#4334` OFF that net · D4 PD85 0 ·
D5 `Is Broken?` False on the ORDERED second pass (42(b)), wire_delta 0 · D5b a FRESH `net_sources` walk after
that second pass (prior-art c87 B4: this op MERGES, so `wire_delta 0` alone is NOT evidence the pass was
inert) · D7 the `#637` terminal SET DIFFERENCE · D7b zero UNREAD rows · D8 THIS RUN adds no net `Node` ·
D6 broken wires <= baseline 11, on a SCRATCH (RBW DELETES).
⚠️ TWO CHANGES vs the 15:36:12 run (`tools/bench/build_d1_m3a3b_rowD.log`), both decided by judgement:
(1) THE JUNK PURGE NOW RUNS TWICE - the first one where it always was, a SECOND after the D5 ordered second
pass, because that pass mints its own stray `Invoke` too and the 15:36:12 artefact was SAVED carrying it
(`Node` 635 -> 636 at `:86` vs `:201`, `Diagram #686` `nodes_on_diagram` 27 -> 28). THE REASON IS §5's OWN
TWO: an `Invoke` whose `reference` is unwired is a BROKEN NODE that pins `ExecState` 0, and it is an object
the original never had = a rule-1a hazard. ⚠️ The "spare node shifts every INDEX TRIPLE" reason that stood
here until 2026-09-22 16:1x is WITHDRAWN AS REFUTED by this build's own readings (prior-art c87b A3(i)): the
junk node is appended at the TAIL (`nodes_index 27` of 28, `build_d1_m3a3b_rowD.log:99`), `#637` still
resolved at `Nodes[4]` with uid echo 637 at 28 nodes (`:137-138`), and `Diagram[19].Nodes[21]` echoed
`23032 -> MATCH` at 27 nodes (`:22`). Nothing this build addresses is index-unstable.
D8 asserts THIS RUN adds no net `Node` (AFTER == BEFORE, both printed). ⚠️ IT IS NOT A CLEAN-BED CLAIM: the
BED ITSELF already carries one inherited unpurged second-pass `Invoke` (`Node` 634 cold at
`build_d1_m3a3_run2.log:33` -> 635 saved at `:187`/`:195`; `Diagram #686` 26 -> 27 nodes), because Row C's
second pass was idempotent and `build_d1_m3a3.py:1432`'s `if not idempotent:` guard skipped ITS purge.
`junk_purge` only ever deletes nodes new since the last `node_mark` (`stagekit.py:460-474`), so this run
CANNOT remove that inherited node and does not claim to. ⚠️ FOR JUDGEMENT: if §5's broken-node reasoning is
right, that inherited node may block M4's COLD `ExecState` 1 target from inside the bed.
(2) D7 IS A SET DIFFERENCE, NOT A COUNT. The review showed the count form is green by construction (the
`total` half cannot move and the WIRED half is the row's own purpose), so D7 now keys BOTH tables on
(i, name, is_source, `build_d1_m3a1.term_state()`) and PASSES only when the symmetric difference is exactly
{t10 'Outgoing Handle' WIRED, t10 'Outgoing Handle' BARE}. The review's own free offline test was run first
on the 15:36:12 tables and returns exactly that (2 elements, 0 UNREAD, 48 -> 47 WIRED, 12 -> 13 BARE), so
this gate is a PREDICTION here, not a restatement. Two scope notes, both from prior-art c87b:
  * B4: the UNREAD check is SPLIT OUT of D7's pass condition into its OWN gate D7b, and is labelled WEAK -
    `conn_err` reads 0 on every row of this table including the bare ones (`:27`, `:33`, `:101-106`) while
    `gscript.py:914` documents bare as carrying 1055 there, so one of `term_state`'s four inputs is a
    constant here and UNREAD lends D7 no assurance. It still FAILS the run; it just no longer props up D7.
  * B3: the key folds state into itself and keeps no value, so a WIRED->WIRED change of the WIRE IDENTITY
    under a terminal is OUT OF SCOPE for the gate. Accepted deliberately: the gate's key is fixed by this
    dispatch's brief, and every net-identity claim Row D makes is carried by D2/D3/D5b's `net_sources`
    OWNER walk, which is wire-addressed. The wire-identity delta is PRINTED as a fact so it is not lost."""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [p for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"), HERE)
                if p not in sys.path]
import stagekit as K                                                               # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                      # noqa: E402

INPUT, INPUT_MD5 = C82.BED, C82.BED_MD5          # the Row-C bed - see INPUT above
BASELINE_BAD, OLD_LOOP = 11, 637     # broken wires on the bed's own bytes (STATUS, c84 S(d2)); the OLD loop
D7_T, D7_NAME = 10, "Outgoing Handle"          # the ONE row Row D is allowed to change: the OLD source
D7_EXPECT = {(D7_T, D7_NAME, True, "WIRED"), (D7_T, D7_NAME, True, "BARE")}   # its two states, nothing else

def work(s):
    s.start()
    d_idx, _t = C82.resolve_triple(s.work, "rowD")
    _l0, rows0 = s.wired_terminals(OLD_LOOP, hints=[d_idx], tag="D7 BEFORE")
    cen0 = s.census(("Wire", "Node", "LoopTunnel"), tag="BEFORE")
    s.delete_wire(C82.ROWD_WIRE, "rowD ")        # NO Remove Bad Wires anywhere in this file (plan 111a)
    b = s.fs_inner_tunnel_read(C82.FSIT_UID, tag="rowD AFTER THE DELETE")
    s.gate("D1 FSIT #{0} still resolves and its LeftTerm #{1} is BARE after the delete".format(
        C82.FSIT_UID, C82.LEFT_TERM_EXPECT),
        b.get("term_a_uid") == C82.LEFT_TERM_EXPECT and not b.get("wire_a"),
        "LeftTerm #{0!r} wire {1!r} err {2!r}".format(b.get("term_a_uid"), b.get("wire_a"), b.get("err")),
        fatal=True)

    def connect():
        di, _tt = C82.resolve_triple(s.work, "rowD re-resolve")     # re-read, never carried (34(h))
        return s.fs_inner_tunnel_connect(C82.FSIT_UID, di, C82.LOOP_NODES_IDX, C82.LOOP_TERM_IDX)

    r = connect()
    s.junk_purge("rowD", hints=[d_idx])
    after = s.fs_inner_tunnel_read(C82.FSIT_UID, tag="rowD AFTER THE CONNECT")
    wire = after.get("wire_a")
    s.gate("D0 the connect wrote a wire onto #{0}".format(C82.LEFT_TERM_EXPECT), bool(wire),
           "wire {0!r} op err {1!r} invoke err {2!r}".format(wire, r.get("err"), r.get("invoke_err")),
           fatal=True)
    net = s.net_sources(wire, tag="rowD")
    s.gate("D2 exactly ONE source terminal on the net, owner RightShiftRegister #{0}".format(C82.RSR_EXPECT),
           net["source_owners"] == [("RightShiftRegister", C82.RSR_EXPECT)], repr(net["source_owners"]))
    s.gate("D3 the OLD source #{0} is OFF that net".format(C82.OLD_SOURCE),
           bool(net["all_owners"]) and all(u != C82.OLD_SOURCE for _c, u in net["all_owners"]),
           "every owner {0!r}".format(net["all_owners"]))
    s.gate("D4 PD85 violations 0 on the walk", not net["pd85"], repr(net["pd85"]))
    s.expect_is_broken_false("D5", connect, wire_uid=wire)
    s.junk_purge("rowD SECOND PASS", hints=[d_idx])   # c87 §5: that pass mints its own stray `Invoke` too
    net2 = s.net_sources(wire, tag="rowD SECOND PASS")   # prior-art c87 B4: a MERGE also yields wire_delta 0
    s.gate("D5b the ordered second pass left ONE source on the net, still owner #{0}".format(C82.RSR_EXPECT),
           net2["source_owners"] == [("RightShiftRegister", C82.RSR_EXPECT)] and not net2["pd85"],
           "owners {0!r} pd85 {1!r}".format(net2["source_owners"], net2["pd85"]))
    _l1, rows1 = s.wired_terminals(OLD_LOOP, hints=[d_idx], tag="D7 AFTER")
    M1 = K.mod("build_d1_m3a1")
    key = (lambda q: set((t["i"], t["name"], bool(t["is_source"]), M1.term_state(t)) for t in q))
    sym = sorted(key(rows0) ^ key(rows1), key=lambda q: (q[0], q[3]))
    unread = [t for q in (rows0, rows1) for t in q if M1.term_state(t) == "UNREAD"]
    w0, w1 = [dict((t["i"], t["wire"]) for t in q) for q in (rows0, rows1)]   # B3: PRINTED, not gated
    s.fact("D7 SET DIFFERENCE on (i, name, is_source, state): {0!r} ; UNREAD rows {1} ; totals before {2} "
           "after {3} ; wire-identity deltas {4!r}".format(
               sym, len(unread), len(rows0), len(rows1),
               sorted((i, w0[i], w1[i]) for i in w0 if w0.get(i) != w1.get(i))))
    s.gate("D7 #{0}'s terminal set difference is EXACTLY t{1} {2!r} WIRED->BARE and nothing else".format(
        OLD_LOOP, D7_T, D7_NAME), set(sym) == D7_EXPECT, "sym diff {0!r}".format(sym))
    s.gate("D7b zero UNREAD rows on either table (WEAK: `conn_err` is a constant 0 here - prior-art c87b B4)",
           not unread, "UNREAD {0} of {1} rows".format(len(unread), len(rows0) + len(rows1)))
    cen1 = s.census(("Wire", "Node", "LoopTunnel"), tag="AFTER")
    s.gate("D8 THIS RUN adds no net `Node` (AFTER == BEFORE; NOT a clean-bed claim - the bed carries one "
           "inherited unpurged `Invoke`, prior-art c87b A3(ii))",
           cen1.get("Node") == cen0.get("Node"),
           "Node before {0!r} after {1!r}".format(cen0.get("Node"), cen1.get("Node")))
    md5_out = s.save(broken_ok=True)             # the bed is BROKEN BY DESIGN; the approved gui_save route
    s.fact("ROW D ARTEFACT: {0} md5 {1}".format(os.path.basename(s.work), md5_out))
    if md5_out:
        probe = s.scratch("bwprobe", source=s.work)
        bw = s.broken_wire_count(target=probe, allow_mutation=True, tag="D6")
        s.gate("D6 the diagram-wide broken-wire count <= the baseline {0}".format(BASELINE_BAD),
               bw["bad"] <= BASELINE_BAD, "{0} bad wire(s) vs baseline {1}".format(bw["bad"], BASELINE_BAD))


if __name__ == "__main__":
    st = K.Stage(INPUT, INPUT_MD5, "D1_s3b_m3a3b_rowD", fresh=True, pins=C82.PINS, deadline_min=40,
                 reserve_s=300, task="M3a-3b Row D: 7506 out, #23868 -> FSIT #7468 LeftTerm #7488")
    sys.exit(K.run(work, st))
