r"""build_opconstwire_v1 - card 85-1 P1 + the op half of P2 (Pre-decided 188(c)): a verb whose SOURCE is a bare
diagram CONSTANT. PRIOR ART (checked first): OpWire_v1 (erdosmiller Get Outputs needs a Node - 1057 on a constant,
constsrc_l2a1_82.log:511), OpWireCtl_v0 (labels, 5001), OpConnectNested_v1 (Nodes[] omits constants), OpConstValueN_v1
(Constant.Terminal 634AC04 measured functional, reads only), OpConnect_v0 (Connect Wire 6349C03, Terminal-typed ends;
keystone-op-spec.md §24/§28), build_opconstwire_v0 (never built). The typed-seed TMSC retarget is build_opconnectnested_v1
V3/V5. Nothing here is a new primitive: every step is an existing gscript verb.
DESIGN: copy OpWire_v1 (ops\OpConstWire_v1.vi); delete Get Outputs #216 and Wire Inputs #262;
 SOURCE Traverse(Class Name)[index] -> TMSC #683 retargeted by a Constant-typed seed -> Constant.Terminal -> Wire Source;
 SINK   Traverse(Class Name 2)[index 2] -> TMSC #788 (Node) -> Node.Terminals[] -> IA[<term>] -> Connect Wire reference.
PREDICTION CONTRACT:
 P1 separator (hyp-constsrc82.md:84): g.wire(Comparison #10950 'zz_nonexistent' -> 'y') on a D1_k scratch raises 5001
    (Get Outputs), NOT 1057, and adds no wire -> the 1057 was the SOURCE cast -> route = the new op (188(c)).
 B  4 nodes built (+1 each), 8 connects each with the same wire uid on both ends, 1 seed + 1 index control +
    1 error indicator, ExecState 1, scripted save, ExecState 1 cold.
 N  negative: source = Comparison (a Node, not a Constant) x20 on the scratch: err carries 1057 every call, Wire and
    Invoke counts unchanged, LabVIEW handles flat within +-100.
 H  D1_k md5 unchanged, scratch deleted, LabVIEW gone.
   py tools/bgrun.py --material --max-min 30 --log tools/bench/constsrc_l2a1_85_build.log -- py -u tools/recipes/build_opconstwire_v1.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g                                                  # noqa: E401,E402
N = K.mod("build_opconnectnested_v1")
OPS = os.path.join(g.CLAUDEDEV, "ops")
D1K, D1K_MD5 = os.path.join(g.CLAUDEDEV, "D1_k_20260925_100155.vi"), "6cf5b0777aafa12112d8a786a9eed1ed"
SRC_TM, DST_TM, GETOUT, WIREIN = 683, 788, 216, 262


def body(s):
    print(__doc__, flush=True)
    op = s.start()
    scr = s.scratch("sep", source=D1K)
    di = s.uid_index("Comparison", 10950, target=scr)
    w0 = s.count("Wire", scr)
    _r, err = s.safe("P1 separator", lambda: g.wire(scr, "Comparison", di, "zz_nonexistent", "Comparison", di, "y"))
    s.R["separator"] = err
    s.gate("P1a separator made no wire", s.count("Wire", scr) == w0, "Comparison[{0}]".format(di))
    s.gate("P1 separator: 5001 and no 1057 -> the 82-3 1057 was the SOURCE cast -> route = new op (188(c))",
           "5001" in err and "1057" not in err, err[:240], fatal=True)
    w = N.walk(op, 0)
    tm = sorted(u for u, v in w.items() if N.term(v[2], "specific class reference", True))
    s.gate("B0 donor holds TMSC 683/788 and SubVIs 216/262", tm == [SRC_TM, DST_TM] and GETOUT in w and WIREIN in w,
           "TMSC {0}, nodes {1}".format(tm, len(w)), fatal=True)
    for u in (GETOUT, WIREIN):
        g.delete_object(op, "SubVI", s.uid_index("SubVI", u, op))
    g.remove_bad_wires_scripted(op)
    pnc = g.build_property(op, "VI Server:Constant", [("634AC04", False)], (900, 250))[0]["uid"]
    pnt = g.build_property(op, "VI Server:Node", [("6359000", False)], (1000, 450))[0]["uid"]
    iat = g.build_index_array(op, (1150, 450))[0]["uid"]
    inv = g.build_invoke(op, "VI Server:Terminal", "6349C03", (1300, 350))[0]["uid"]
    s.fact("B built PN Constant.Terminal #{0}, PN Node.Terminals[] #{1}, IA #{2}, Invoke Connect Wire #{3}".format(
        pnc, pnt, iat, inv))

    def ein(u):
        return next(r["name"] for r in N.walk(op, 0)[u][2] if not r["is_source"] and r["name"].startswith("error in"))

    def link(a, an, b, bn):
        br = bool((N.term(N.walk(op, 0)[a][2], an, True) or {}).get("wire"))
        wu = N.connect(op, a, an, b, bn, branch=br, tag="B ")
        s.gate("B wire #{0}.{1!r} -> #{2}.{3!r} on both ends".format(a, an, b, bn), bool(wu), "w{0}".format(wu))
    link(DST_TM, "specific class reference", pnt, "reference")
    link(pnt, "Terms[]", iat, "array")
    link(iat, "element", inv, "reference")
    link(pnc, "Terminal", inv, "Wire Source")
    link(DST_TM, "error out", pnt, ein(pnt))
    w = N.walk(op, 0)
    seed = g.create_control(op, w[pnc][0], N.term(w[pnc][2], "reference", False)["i"])[1]
    s.gate("B seed control created on the Constant PN reference", bool(seed), repr(seed), fatal=True)
    N.del_net(op, {r["label"]: r for r in g.panel_wiring(op)}[seed]["wire"], "seed ")
    N.del_net(op, N.term(N.walk(op, 0)[SRC_TM][2], "target class", False)["wire"], "class-const ")
    g.wire_control(op, [seed], "Function", N.idx(op, "Function", SRC_TM), ["target class"])
    link(SRC_TM, "specific class reference", pnc, "reference")
    link(SRC_TM, "error out", pnc, ein(pnc))
    link(pnc, "error out", inv, ein(inv))
    w = N.walk(op, 0)
    lab_t = g.create_control(op, w[iat][0], N.term(w[iat][2], "index", False)["i"])[1]
    ind0 = {l for _i, l, ind in g.fp_labels(op) if ind}
    w = N.walk(op, 0)
    g.create_indicator(op, w[inv][0], N.term(w[inv][2], "error out", True)["i"])
    lab_e = [l for _i, l, ind in g.fp_labels(op) if ind and l not in ind0]
    s.gate("B index control + one error indicator labelled", bool(lab_t) and len(lab_e) == 1,
           "{0!r} {1!r}".format(lab_t, lab_e), fatal=True)
    g.set_auto_error_handling(op, False)
    s.gate("E op ExecState 1 before the save", s.es("op assembled", op) == 1, fatal=True)
    s.R["op_md5"] = s.save()
    labels = {"term": lab_t, "err": lab_e[0], "seed": seed}
    with open(g.CONST_WIRE_LABELS, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    s.fact("OP {0} md5 {1}; labels {2}".format(op, s.R["op_md5"], labels))
    bp = K.mod("bench_prep")
    h0, i0, w0 = bp.labview_handles(), s.count("Invoke", scr), s.count("Wire", scr)
    neg = [g.wire_const(scr, "Comparison", di, "Comparison", di, 0, labels) for _ in range(20)]
    h1 = bp.labview_handles()
    s.gate("N1 negative x20: non-Constant source refused with 1057, no wire", all(d == 0 and "1057" in e for d, e in neg),
           repr(neg[0])[:200])
    s.gate("N2 Wire and Invoke counts unchanged on the scratch", s.count("Wire", scr) == w0 and s.count("Invoke", scr) == i0)
    s.gate("N3 handles flat over 20 calls (+-100)", h0 and h1 and abs(h1 - h0) <= 100, "{0} -> {1}".format(h0, h1))
    s.drop_scratch(scr)
    s.dump()


if __name__ == "__main__":
    os.makedirs(OPS, exist_ok=True)
    s = K.Stage(g.OP_WIRE, K.md5(g.OP_WIRE), "D1_k_scratch_c85", work_name="OpConstWire_v1.vi", work_dir=OPS,
                preload=False, deadline_min=25, out_json=os.path.join(K.BENCH, "constsrc_l2a1_85_build.json"),
                task="card 85-1 P1/P2-op")
    s.close = lambda: K.Stage.close(s, expect_files=[])      # the op lives in claudeDev\ops, not claudeDev\*.vi
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    s.gate("H1 LabVIEW process gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True,
                                                                          text=True, timeout=60).stdout.lower())
    s.gate("H2 D1_k md5 unchanged", K.md5(D1K) == D1K_MD5)
    s.summary()
    sys.exit(1 if s.fails else 0)
