r"""build_optunouter_v1 - card 85-2, Pre-decided 191(b): a verb whose SOURCE is a structure tunnel's OUTER face, addressed
by the TUNNEL (R45 rw_6007_5082, R46 rw_6026_5164) - never through the owner's Terminals[] (the T2c2 failure on this same
tunnel #5680, docs/NAMES.md:1132-1137). PRIOR ART (checked first): OpConstWire_v1 (the donor, 85-1: PN Constant.Terminal
#136, PN Node.Terms[] #139, IA #142, Invoke Connect Wire #145, TMSC #683/#788); OpTunnelRead_v0 cast(Tunnel) on both #5540
output tunnels 24/24 (docs/toolkit-capabilities.md:77); Tunnel.Outside Terminal 6356001, short name 'Outer Term'
(docs/NAMES.md:856). No new primitive: one build_property + the donor's seed re-type pattern.
DESIGN: replace PN #136 (Constant.Terminal) by PN VI Server:Tunnel[6356001]; its output -> Invoke.Wire Source; a
 Tunnel-typed seed (create_control on the new PN's reference) retargets TMSC #683; the sink ladder is untouched.
PREDICTION CONTRACT:
 B  PN #136 gone, one new Tunnel PN with one data output, 4 wires same uid on both ends, ExecState 1, saved, labels file
 N  negative x20 on a D1_k scratch: source class 'Comparison' (a Node, not a Tunnel) -> 1057 every call, Wire/Invoke
    counts unchanged, handles flat +-100
 H  D1_k md5 unchanged, scratch deleted, LabVIEW gone.
   py tools/bgrun.py --material --max-min 20 --log tools/bench/unroutable_l2a1_85_build_tun.log -- py -u tools/recipes/build_optunouter_v1.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g                                                  # noqa: E401,E402
N = K.mod("build_opconnectnested_v1")
OPS = os.path.join(g.CLAUDEDEV, "ops")
D1K, D1K_MD5 = os.path.join(g.CLAUDEDEV, "D1_k_20260925_100155.vi"), "6cf5b0777aafa12112d8a786a9eed1ed"
DONOR_MD5 = "c978863c68161ed051285fccdcd071e5"
PNC, INV, SRC_TM = 136, 145, 683


def body(s):
    print(__doc__, flush=True)
    op = s.start()
    w = N.walk(op, 0)
    s.gate("B0 donor holds PN #136, Invoke #145, TMSC #683", all(u in w for u in (PNC, INV, SRC_TM)), sorted(w), fatal=True)
    s.fact("B0 delete_object returned {0!r}".format(g.delete_object(op, "Property", N.idx(op, "Property", PNC))))
    g.remove_bad_wires_scripted(op)
    pu = sorted(o["uid"] for o in g.report_all(op, "Property"))
    s.gate("B1a PN Constant.Terminal #136 deleted (Property uids after the delete)", PNC not in pu, pu, fatal=True)
    pn = g.build_property(op, "VI Server:Tunnel", [("6356001", False)], (900, 250))[0]["uid"]   # uid 136 may be REUSED (run 1;
    w = N.walk(op, 0)                                                                            # hyp-optunouter-uidreuse-85)
    outs = [r["name"] for r in w[pn][2] if r["is_source"] and r["name"] not in ("reference out", "error out")]
    s.gate("B1 Tunnel PN #{0} ({1!r}) has ONE data output, 'Outer Term' (identity by output name, not uid)".format(pn, w[pn][1]),
           outs == ["Outer Term"], outs, fatal=True)

    def link(a, an, b, bn):
        br = bool((N.term(N.walk(op, 0)[a][2], an, True) or {}).get("wire"))
        wu = N.connect(op, a, an, b, bn, branch=br, tag="B ")
        s.gate("B wire #{0}.{1!r} -> #{2}.{3!r} on both ends".format(a, an, b, bn), bool(wu), "w{0}".format(wu))
    link(pn, outs[0], INV, "Wire Source")
    w = N.walk(op, 0)
    seed = g.create_control(op, w[pn][0], N.term(w[pn][2], "reference", False)["i"])[1]
    s.gate("B2 Tunnel-typed seed control created on the PN reference", bool(seed), repr(seed), fatal=True)
    N.del_net(op, {r["label"]: r for r in g.panel_wiring(op)}[seed]["wire"], "seed ")
    old_seed = N.term(N.walk(op, 0)[SRC_TM][2], "target class", False)["wire"]     # re-read now: wire uids are recycled
    s.gate("B2a #683 'target class' still fed by the OLD seed control", old_seed == {r["label"]: r for r in g.panel_wiring(op)}.get(
        "reference", {}).get("wire"), old_seed, fatal=True)
    N.del_net(op, old_seed, "old-seed ")
    g.wire_control(op, [seed], "Function", N.idx(op, "Function", SRC_TM), ["target class"])
    link(SRC_TM, "specific class reference", pn, "reference")
    link(SRC_TM, "error out", pn, "error in (no error)")
    link(pn, "error out", INV, "error in (no error)")
    g.set_auto_error_handling(op, False)
    s.gate("E op ExecState 1 before the save", s.es("op assembled", op) == 1, fatal=True)
    s.R["op_md5"] = s.save()
    old = json.load(open(g.CONST_WIRE_LABELS, encoding="utf-8"))
    labels = {"term": old["term"], "err": old["err"], "seed": seed, "outer": outs[0]}
    with open(g.TUNOUTER_WIRE_LABELS, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    s.fact("OP {0} md5 {1}; labels {2}".format(op, s.R["op_md5"], labels))
    scr = s.scratch("neg", source=D1K)
    di = s.uid_index("Comparison", 10950, target=scr)
    bp = K.mod("bench_prep")
    h0, i0, w0 = bp.labview_handles(), s.count("Invoke", scr), s.count("Wire", scr)
    neg = [g.wire_tunouter(scr, "Comparison", di, "Comparison", di, 0, labels) for _ in range(20)]
    h1 = bp.labview_handles()
    s.gate("N1 negative x20: non-Tunnel source refused with 1057, no wire", all(d == 0 and "1057" in e for d, e in neg),
           repr(neg[0])[:200])
    s.gate("N2 Wire and Invoke counts unchanged on the scratch", s.count("Wire", scr) == w0 and s.count("Invoke", scr) == i0)
    s.gate("N3 handles flat over 20 calls (+-100)", h0 and h1 and abs(h1 - h0) <= 100, "{0} -> {1}".format(h0, h1))
    fs = [o["uid"] for o in g.report_all(scr, "FlatSequenceOuterTunnel")]          # prior-art A3: the 1077 class boundary
    w1 = s.count("Wire", scr)
    r4 = g.wire_tunouter(scr, "FlatSequenceOuterTunnel", 0, "Comparison", di, 0, labels) if fs else (0, "none on the scratch")
    s.gate("N4 a FlatSequenceOuterTunnel source -> an error and no wire", r4[0] == 0 and bool(r4[1]) and s.count("Wire", scr) == w1,
           repr(r4)[:200])
    s.drop_scratch(scr)
    s.dump()


if __name__ == "__main__":
    s = K.Stage(g.OP_CONST_WIRE, DONOR_MD5, "D1_k_scratch_c85tun", work_name="OpTunOuterWire_v1.vi", work_dir=OPS,
                preload=False, deadline_min=15, out_json=os.path.join(K.BENCH, "unroutable_l2a1_85_build_tun.json"),
                task="card 85-2 P3-op")
    s.close = lambda: K.Stage.close(s, expect_files=[])
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    s.gate("H1 LabVIEW process gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True,
                                                                          text=True, timeout=60).stdout.lower())
    s.gate("H2 D1_k md5 unchanged", K.md5(D1K) == D1K_MD5)
    s.summary()
    sys.exit(1 if s.fails else 0)
