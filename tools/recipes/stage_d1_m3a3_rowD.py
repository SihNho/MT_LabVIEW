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
GATES, each printing the value it compared: D1 the FSIT still RESOLVES and `#7488` is BARE after the delete ·
D0 a wire was written · D2 ONE source terminal, owner `#23868` · D3 the OLD `#4334` OFF that net · D4 PD85 0 ·
D5 `Is Broken?` False on the ORDERED second pass (42(b)), wire_delta 0 · D7 `#637`'s terminal counts
unchanged · D6 broken wires <= baseline 11, on a SCRATCH (Remove Bad Wires DELETES)."""
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

def work(s):
    s.start()
    d_idx, _t = C82.resolve_triple(s.work, "rowD")
    _l0, rows0 = s.wired_terminals(OLD_LOOP, hints=[d_idx], tag="D7 BEFORE")
    s.census(("Wire", "Node", "LoopTunnel"), tag="BEFORE")
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
    _l1, rows1 = s.wired_terminals(OLD_LOOP, hints=[d_idx], tag="D7 AFTER")
    n0, n1 = [(len(q), len([x for x in q if x.get("has_wire")])) for q in (rows0, rows1)]
    s.gate("D7 WhileLoop #{0}'s terminal counts unchanged (total, wired)".format(OLD_LOOP), n0 == n1,
           "before {0!r} after {1!r}".format(n0, n1))
    s.census(("Wire", "Node", "LoopTunnel"), tag="AFTER")
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
