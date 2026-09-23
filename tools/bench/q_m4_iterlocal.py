r"""q_m4_iterlocal - cycle 68 MATERIAL, brief Q4. MEASUREMENT ONLY on a dated SCRATCH of the M3a-4 bed.

Question: can the frame loop's iteration terminal #644 (owner Diagram #639 = WhileLoop #637's body, the only
SOURCE of wire 3268 - docs/wiki/subvi/D1_s1_copy.json:36385) be wired as a SOURCE into a WRITE-mode Local placed
in #639, using ONLY existing verbs?
Existing tools found and reused (nothing new built):
  - OpCreateLocalRead_v0 (Write? steers mode; born on TopLevelDiagram #536 - tools/bench/diag_c61_localdir_write2.log:83)
    via tools/bench/diag_c61_localdir_write2.call_new_op:591
  - OpMoveIn_v0 via Stage.move_in (tools/stagekit.py:538) - the verb S3b/M3a-1 used to put Locals in a body
  - OpConnectFromWire_v0 via Stage.connect_from_wire (:551) - the only writer whose SOURCE is addressed by WIRE
    (docs/toolkit-capabilities.md), so the unnamed Diagram-owned #644 is reachable as Wire(3268).Terms[k]
  - OpWireSource_v5 via Stage.net_sources (:367) to find k with Is Source? and owner #639.
Ops that do NOT fit (offline, recorded in the reply): OpFsInnerTunnelConnect_v1 (sink = FSIT uid, source = a
Nodes[] triple - #644 is in no Nodes[]); OpConnectNested_v1 (both ends Nodes[] triples).
PREDICTION CONTRACT:
  P1 bed ES 1 on open (M3a-4 delivered ES 1).   P2 one new Local, is_source False (WRITE), owner TopLevelDiagram.
  P3 after move_in the Local's uid is in Diagram #639's Nodes[] census.   P4 ES after move = RECORDED, not gated
     (an unwired write-Local's effect on ExecState is unmeasured here).
  P5 net_sources(3268): exactly one row is_source with owner_uid 639.
  P6 connect_from_wire: op errors empty, Is Broken? False, wire delta 0 (a branch of w3268), ES 1.
RUN 2 (after run 1 FAILED P6d: ES 0 after connect, Is Broken? False, ES already 0 right after create):
  junk_purge after move and after connect; P6d becomes a ROW; P8 = broken-wire count on the discarded work;
  C1 = control arm - an unwired READ Local on the same indicator, ES recorded (separates "unwired WRITE Local
  breaks the VI" from "the create op breaks it"). Attempt 2 of the failure budget.
Scratch only; the bed's md5 is gated before and after; the work copy is discarded (files left = []).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a4_20260923_185345.vi")
BED_MD5 = "fdd6d74ac8a5ba0c1a545ad89ff2996f"
BODY_UID, SRC_WIRE, SRC_TERM_UID = 639, 3268, 644
LABEL = "current image number"          # a numeric INDICATOR (docs/main-vi-panel-map.md:383); scratch only


def main(s):
    s.start()
    s.discard_work()
    p = s.work
    L = K.mod("diag_c61_localdir_write2")
    B = K.mod("build_d1_v0")
    es0 = s.es("P1 on open")
    s.gate("P1 bed ExecState 1 on open", es0 == 1, repr(es0))
    fpl, _e = s.safe("fp_labels", lambda: g.fp_labels(p), [])
    hits = [(i, t, ind) for (i, t, ind) in (fpl or []) if t == LABEL]
    s.fact("panel rows labelled {0!r}: {1!r}".format(LABEL, hits))
    s.gate("P0 exactly one panel object labelled {0!r}".format(LABEL), len(hits) == 1, repr(hits), fatal=True)

    s.head("[1] OpCreateLocalRead_v0 with Write? = True (the verb S3b used, mode steered)")
    s.node_mark("create_local_write")
    rd, err = s.safe("call_new_op", lambda: L.call_new_op(p, hits[0][0], True, "Write?", "Q4"), {})
    new = (rd or {}).get("local_uids_added") or []
    s.fact("create: err_cluster {0} run_err {1!r} new {2!r}".format(
        (rd or {}).get("error_cluster_verbatim"), (rd or {}).get("run_error_verbatim"), new))
    s.gate("P2a exactly one new Local", len(new) == 1, repr(new), fatal=True)
    lu = int(new[0])
    oc, ou = B.owner_of(p, lu, strict=True)
    s.fact("new Local #{0} owner {1}#{2}".format(lu, oc, ou))
    s.gate("P2b new Local born on the TopLevelDiagram", "TopLevel" in str(oc), "{0}#{1}".format(oc, ou))
    s.es("after create (Local unwired, top level)")

    s.head("[2] move_in the Local into Diagram #639 (WhileLoop #637 body)")
    di, _e = s.safe("diag_index(#639)", lambda: B.diag_index(p, BODY_UID))
    s.fact("Diagram #639 traverse index = {0!r}".format(di))
    s.move_in(lu, di, (40, 40))
    s.junk_purge("after move", hints=[di, 0])            # run 2: run 1 saw Node census +1 across move_in
    s.es("after move + junk purge")
    oc2, ou2 = B.owner_of(p, lu, strict=True)
    s.fact("after move: Local #{0} owner {1}#{2}".format(lu, oc2, ou2))
    rows, _e = s.safe("node_labels(#639)", lambda: g.node_labels(p, di), [])
    uids = [r["uid"] for r in (rows or [])]
    s.gate("P3 Local #{0} is in Diagram #639's Nodes[]".format(lu), lu in uids, "owner {0}#{1}".format(oc2, ou2))
    s.es("P4 after move (write-Local unwired, recorded)")
    if lu not in uids:
        return
    ni = uids.index(lu)
    s.fact("Local #{0} = Diagram[{1}].Nodes[{2}] (of {3})".format(lu, di, ni, len(uids)))
    _loc, trows = s.wired_terminals(lu, hints=[di])
    s.fact("Local terminals: {0!r}".format(trows))

    s.head("[3] which Wire(3268).Terms[k] is #644 (OpWireSource_v5)")
    net = s.net_sources(SRC_WIRE, n=12, target=p, tag="w3268")
    src = [r for r in (net.get("walk") or []) if r.get("is_source") and r.get("owner_uid")]
    s.fact("source rows on w3268: {0!r}".format(src))
    s.gate("P5 exactly one source row, owner #639", len(src) == 1 and int(src[0]["owner_uid"]) == BODY_UID,
           repr(src))
    if len(src) != 1:
        return
    k = int(src[0]["i"])

    s.head("[4] OpConnectFromWire_v0: sink D[{0}].N[{1}].t0 <- w3268.Terms[{2}] (#644)".format(di, ni, k))
    wbefore = g.count(p, "Wire")
    rec = s.connect_from_wire(di, ni, 0, SRC_WIRE, k)
    res = rec.get("result") or (None, None, rec.get("err"), {})
    dw, es, err, sub = res
    s.fact("connect: wire delta {0!r} ES {1!r} err {2!r} sub {3!r} (Wire {4} before)".format(dw, es, err, sub,
                                                                                          wbefore))
    s.gate("P6a op error empty", not err and not any((sub or {}).get(x) for x in ("err_uidvi", "err_wirepn")),
           repr((err, sub)))
    s.gate("P6b Is Broken? False", (sub or {}).get("Is Broken?") is False, repr((sub or {}).get("Is Broken?")))
    s.gate("P6c wire delta 0 (branch of w3268)", dw == 0, repr(dw))
    s.es("after connect (run 1: 0)")
    s.junk_purge("after connect", hints=[di, 0])          # the OpConnect* family mints 1 stray Invoke/call
    es_after = s.es("P6d after connect + junk purge")
    s.row("P6d ExecState after connect + purge", es_after, 1)
    _loc, trows2 = s.wired_terminals(lu, hints=[di])
    s.fact("Local terminals after connect: {0!r}".format(trows2))
    s.broken_wire_count(allow_mutation=True, tag="P8 work copy (discarded)")
    s.head("[5] CONTROL ARM on a fresh scratch: the SAME indicator, Write? = False (READ Local), top level")
    c = s.scratch("readarm", source=BED)
    rc, _e = s.safe("call_new_op read", lambda: L.call_new_op(c, hits[0][0], False, "Write?", "Q4c"), {})
    s.fact("control arm: new {0!r} err {1}".format((rc or {}).get("local_uids_added"),
                                                   (rc or {}).get("error_cluster_verbatim")))
    s.row("C1 ExecState after an unwired READ Local", s.es("C1 read-arm", target=c), "recorded")
    s.drop_scratch(c)
    s.gate("P7 bed md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))


S = K.Stage(BED, BED_MD5, "q_m4_iterlocal", deadline_min=18.0, reserve_s=240.0,
            pins=tuple(K.DEFAULT_PINS) + (("M3a-4 bed", BED, BED_MD5),),
            out_json=os.path.join(K.BENCH, "q_m4_iterlocal.json"),
            task="cycle 68 Q4: #644 -> write-Local in #639 by existing verbs, on a scratch")
sys.exit(K.run(main, S))
