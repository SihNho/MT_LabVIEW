r"""build_opctlsinkwire_v1 - card 85-2, Pre-decided 191(a): a verb whose SINK is a front-panel ControlTerminal and whose
SOURCE is a bare node terminal (R41 rw_10988_17272). PRIOR ART (checked first): OpConstWire_v1 (the donor, 85-1, 31/0,
tools/bench/constsrc_l2a1_85_build.log:43-74: PN Constant.Terminal #136, PN Node.Terms[] #139, IA #142, Invoke Connect
Wire #145, TMSC #683 source / #788 sink); Wire Indicators.vi needs a WIRED source (tools/gscript.py:1835-1838, kept);
OpWireCtl_v0 sources a control, not sinks one. No new primitive: delete, re-wire and re-type the seed only.
DESIGN (ladders swapped, hyp-unroutable-85.md:64-69): delete PN #136; IA#142.element -> Invoke.Wire Source;
 a Terminal-typed seed (create_control on Invoke.reference) retargets TMSC #683; #683 -> Invoke.reference / error in.
 Call: Class Name='ControlTerminal'/index = the sink CT; Class Name 2/index 2/'index 3' = the source node + terminal.
PREDICTION CONTRACT:
 B  PN #136 gone, 4 re-wires land the same wire uid on both ends, one new seed control, ExecState 1, saved, labels file
 N  negative x20 on a D1_k scratch: sink class 'Comparison' (a Node, not a Terminal) -> err carries 1057 every call,
    Wire/Invoke counts unchanged, LabVIEW handles flat +-100
 H  D1_k md5 unchanged, scratch deleted, LabVIEW gone.
   py tools/bgrun.py --material --max-min 20 --log tools/bench/unroutable_l2a1_85_build_ctl.log -- py -u tools/recipes/build_opctlsinkwire_v1.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g                                                  # noqa: E401,E402
N = K.mod("build_opconnectnested_v1")
OPS = os.path.join(g.CLAUDEDEV, "ops")
D1K, D1K_MD5 = os.path.join(g.CLAUDEDEV, "D1_k_20260925_100155.vi"), "6cf5b0777aafa12112d8a786a9eed1ed"
DONOR_MD5 = "c978863c68161ed051285fccdcd071e5"
PNC, PNT, IA, INV, SRC_TM = 136, 139, 142, 145, 683


def body(s):
    print(__doc__, flush=True)
    op = s.start()
    w = N.walk(op, 0)
    s.gate("B0 donor holds PN #136/#139, IA #142, Invoke #145, TMSC #683", all(u in w for u in (PNC, PNT, IA, INV, SRC_TM)),
           sorted(w), fatal=True)
    old_seed = N.term(w[SRC_TM][2], "target class", False)["wire"]
    g.delete_object(op, "Property", N.idx(op, "Property", PNC))
    g.remove_bad_wires_scripted(op)
    w = N.walk(op, 0)
    s.gate("B1 PN Constant.Terminal #136 deleted", PNC not in w, sorted(w), fatal=True)
    N.del_net(op, N.term(w[IA][2], "element", True)["wire"], "IA->ref ")

    def link(a, an, b, bn):
        br = bool((N.term(N.walk(op, 0)[a][2], an, True) or {}).get("wire"))
        wu = N.connect(op, a, an, b, bn, branch=br, tag="B ")
        s.gate("B wire #{0}.{1!r} -> #{2}.{3!r} on both ends".format(a, an, b, bn), bool(wu), "w{0}".format(wu))
    link(IA, "element", INV, "Wire Source")
    w = N.walk(op, 0)
    seed = g.create_control(op, w[INV][0], N.term(w[INV][2], "reference", False)["i"])[1]
    s.gate("B2 Terminal-typed seed control created on Invoke.reference", bool(seed), repr(seed), fatal=True)
    N.del_net(op, {r["label"]: r for r in g.panel_wiring(op)}[seed]["wire"], "seed ")
    if old_seed:
        N.del_net(op, old_seed, "old-seed ")
    g.wire_control(op, [seed], "Function", N.idx(op, "Function", SRC_TM), ["target class"])
    link(SRC_TM, "specific class reference", INV, "reference")
    link(SRC_TM, "error out", INV, "error in (no error)")
    g.set_auto_error_handling(op, False)
    s.gate("E op ExecState 1 before the save", s.es("op assembled", op) == 1, fatal=True)
    s.R["op_md5"] = s.save()
    old = json.load(open(g.CONST_WIRE_LABELS, encoding="utf-8"))
    labels = {"term": old["term"], "err": old["err"], "seed": seed}
    with open(g.CTLSINK_WIRE_LABELS, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    s.fact("OP {0} md5 {1}; labels {2}".format(op, s.R["op_md5"], labels))
    scr = s.scratch("neg", source=D1K)
    di = s.uid_index("Comparison", 10950, target=scr)
    bp = K.mod("bench_prep")
    h0, i0, w0 = bp.labview_handles(), s.count("Invoke", scr), s.count("Wire", scr)
    neg = [g._opcw_call(g.OP_CTLSINK_WIRE, None, scr, "Comparison", di, "Comparison", di, 0, labels) for _ in range(20)]
    h1 = bp.labview_handles()
    s.gate("N1 negative x20: non-Terminal sink refused with 1057, no wire", all(d == 0 and "1057" in e for d, e in neg),
           repr(neg[0])[:200])
    s.gate("N2 Wire and Invoke counts unchanged on the scratch", s.count("Wire", scr) == w0 and s.count("Invoke", scr) == i0)
    s.gate("N3 handles flat over 20 calls (+-100)", h0 and h1 and abs(h1 - h0) <= 100, "{0} -> {1}".format(h0, h1))
    s.drop_scratch(scr)
    s.dump()


if __name__ == "__main__":
    s = K.Stage(g.OP_CONST_WIRE, DONOR_MD5, "D1_k_scratch_c85ctl", work_name="OpCtlSinkWire_v1.vi", work_dir=OPS,
                preload=False, deadline_min=15, out_json=os.path.join(K.BENCH, "unroutable_l2a1_85_build_ctl.json"),
                task="card 85-2 P2-op")
    s.close = lambda: K.Stage.close(s, expect_files=[])
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    s.gate("H1 LabVIEW process gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True,
                                                                          text=True, timeout=60).stdout.lower())
    s.gate("H2 D1_k md5 unchanged", K.md5(D1K) == D1K_MD5)
    s.summary()
    sys.exit(1 if s.fails else 0)
