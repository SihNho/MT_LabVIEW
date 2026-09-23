r"""q_m4_probe - cycle 68 MATERIAL, READ-ONLY facts for M4a/M4b and the #10686 question, on a dated SCRATCH of the
M3a-4 bed (discarded; files left = []). No mutation verb is called; nothing is run but the reader op VIs.
Existing tools reused (checked first): stagekit.Stage (wired_terminals = build_d1_m3a1.node_view, net_sources =
OpWireSource_v5), gscript.report_all / node_labels / shift_reg_left, build_d1_v0.owner_of. Nothing new built.
PREDICTION CONTRACT (facts, not decisions):
  R1 bed ES 1 on open.   R2 #23032 is a WhileLoop whose body is Diagram #23058.
  R3 #10407 t0 is fed by a Local on #23058 (source owner class 'Local').
  R4 #10686 has two wired boolean inputs; their net sources are REPORTED (no prediction on what they are).
  R5 donors Not/And/Wait (ms) each resolve to a Nodes[] row with a terminal table (names reported).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a4_20260923_185345.vi")
BED_MD5 = "fdd6d74ac8a5ba0c1a545ad89ff2996f"
LOOP, BODY, SINK, SCHED = 23032, 23058, 10407, 10686
DONORS = {"Not": [10382, 10285, 10825, 17837, 21959, 22028], "And": [9647, 18900, 21925, 15392],
          "Wait (ms)": [22343, 32538, 44143]}


def main(s):
    s.start()
    s.discard_work()
    p = s.work
    B = K.mod("build_d1_v0")
    es0 = s.es("R1 on open")
    s.gate("R1 bed ExecState 1 on open", es0 == 1, repr(es0))
    objs = {int(o["uid"]): o for o in g.report_all(p, "GObject")}
    diags = g.report_all(p, "Diagram")
    s.R["diag_index"] = {int(d["uid"]): d["i"] for d in diags}
    for u in [LOOP, BODY, SINK, SCHED] + sum(DONORS.values(), []):
        o = objs.get(u) or {}
        oc, ou = s.safe("owner_of #{0}".format(u), lambda uu=u: B.owner_of(p, uu, strict=True), (None, None))[0]
        s.fact("OBJ #{0}: class {1} pos {2} owner {3}#{4}".format(u, o.get("class"), o.get("pos"), oc, ou))
        if ou:
            oc2, ou2 = s.safe("owner_of #{0}".format(ou), lambda uu=ou: B.owner_of(p, uu, strict=True),
                              (None, None))[0]
            s.fact("   owner #{0} -> its owner {1}#{2} (class of #{0}: {3})".format(
                ou, oc2, ou2, (objs.get(ou) or {}).get("class")))
    s.gate("R2 #23032 is a WhileLoop", (objs.get(LOOP) or {}).get("class") == "WhileLoop",
           repr(objs.get(LOOP)))
    loops = g.report_all(p, "WhileLoop")
    li = next((r["i"] for r in loops if int(r["uid"]) == LOOP), None)
    s.fact("WhileLoop #{0} traverse index {1} of {2}".format(LOOP, li, len(loops)))
    if li is not None:
        sr, e = s.safe("shift_reg_left", lambda: g.shift_reg_left(p, li, 0))
        s.fact("existing shift registers on #{0}: {1!r}".format(LOOP, sr))
    bi = s.R["diag_index"].get(BODY)
    rows, _e = s.safe("node_labels(body)", lambda: g.node_labels(p, bi), [])
    s.fact("Diagram #{0} (idx {1}) Nodes[]: {2!r}".format(BODY, bi, [(r["uid"], (objs.get(r["uid"]) or {}).get(
        "class"), r["label"]) for r in (rows or [])]))
    s.head("[2] #10407 and what feeds its t0")
    _l, t = s.wired_terminals(SINK)
    if t and t[0].get("wire"):
        net = s.net_sources(t[0]["wire"], n=10, tag="#10407.t0")
        s.gate("R3 #10407 t0 source owner is a Local", any(c == "Local" for c, _u in net["source_owners"]),
               repr(net["source_owners"]))
        for c, u in net["source_owners"]:
            s.wired_terminals(u, tag="feeder #{0}".format(u))
    s.head("[3] #10686 'x .and. y?' inputs, two levels up")
    _l, t = s.wired_terminals(SCHED)
    ins = [r for r in t if not r["is_source"] and r.get("wire")]
    s.gate("R4 #10686 has two wired inputs", len(ins) == 2, repr(ins))
    for r in t:
        if not r.get("wire"):
            continue
        net = s.net_sources(r["wire"], n=12, tag="#10686.t{0}".format(r["i"]))
        if r["is_source"]:
            continue
        for c, u in net["source_owners"]:
            _l2, t2 = s.wired_terminals(u, tag="L1 #{0} {1}".format(u, c))
            for r2 in t2:
                if not r2["is_source"] and r2.get("wire"):
                    n2 = s.net_sources(r2["wire"], n=12, tag="L2 #{0}.t{1}".format(u, r2["i"]))
                    for c3, u3 in n2["source_owners"]:
                        s.fact("L2 #{0}.t{1} {2!r} <- {3}#{4} label {5!r}".format(
                            u, r2["i"], r2["name"], c3, u3, (objs.get(u3) or {}).get("class")))
                        if c3 in ("Function", "Comparison", "SubVI", "DigitalNumericConstant", "Local"):
                            s.wired_terminals(u3, tag="L3 #{0} {1}".format(u3, c3))
    s.head("[4] donor terminal tables")
    for lab, us in DONORS.items():
        s.wired_terminals(us[0], tag="donor {0} #{1}".format(lab, us[0]))
    s.gate("R6 bed md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))


S = K.Stage(BED, BED_MD5, "q_m4_probe", deadline_min=20.0, reserve_s=240.0,
            pins=tuple(K.DEFAULT_PINS) + (("M3a-4 bed", BED, BED_MD5),),
            out_json=os.path.join(K.BENCH, "q_m4_probe.json"),
            task="cycle 68 read-only probe: loop 1.5 / #10407 / #10686 inputs / donors")
sys.exit(K.run(main, S))
