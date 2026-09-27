r"""diag_c113e_concat - card 113-3 (measurement only): why BuildArray #11261 input t11270 reads 'element' after b2_03 (review
archive/peer/2026-09-28-c113d-pb.md s4 separator). FIXTURES: dated byte copies claudeDev\scratch_c113e_bed_<ts>.vi of the B2a bed
(md5 107a3ef1) and scratch_c113e_bed_<ts>_s1.vi of D1_s1_copy.vi; both DELETED at close; nothing saved, no VI run.
PRIOR ART: diag_c113c_scratch.py (LVBackend on a scratch) - this reuses stagexec.LVBackend.connect (the route b2_03 took in
stage_d1_l2b2b.py, 'nested') and wiki_build.read_live; no new op. READERS: terminal NAME / wire / term_class per node (read_live),
ExecState, the connect op readback. NO READER EXISTS for BuildArray 'Concatenate Inputs' (grep 0 in tools/docs), LoopTunnel IndexMode
read-back (gscript.py:2001-2002 'no scripted read-back op yet') or Terminal.DataType (docs/NAMES.md:475-476, cycle27-plan.md:1055):
those three are REPORTED as 'no reader', never inferred.
PREDICTION (review's alternative): M1 t11270 'array', t11273 'element', both unwired; M2 after b2_03 alone t11270 reads 'element'
(as stage_d1_l2b2b.log:187-189); M3 after wiring #11608 'output cluster' t11614 -> t11273 t11270 reads 'array' again; M4 S1 copy
t11270 'array' / t11273 'element' both wired. H: bed + S1 md5 unchanged, scratches deleted, LabVIEW gone, handles flat (+-100) k1->end.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c113e_concat.log -- py -u tools/bench/diag_c113e_concat.py"""
import json, os, sys                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagexec as SX, gscript as g                                  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_b2a_20260928_001426.vi"
S1VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi"
BASE = J(K.BENCH, "graph_l2b2a_20260928.json")
S1J = J(K.ROOT, "docs/wiki/subvi/D1_s1_copy.json")
NODES = (11261, 11363, 11608)
st_md5 = "107a3ef12da41b25d533f8a4c761aae8"
NOREADER = {"BuildArray.ConcatenateInputs": "no reader (grep 0 hits in tools/, docs/)",
            "LoopTunnel.IndexMode": "no read-back op (gscript.py:2001-2002)",
            "Terminal.DataType": "no reader over this COM path (docs/NAMES.md:475-476; cycle27-plan.md:1055)"}
TAB = {}


def snap(s, tag, path, fs):
    lv = K.mod("wiki_build").read_live(path, fs_pairs=fs)
    rows = SX.dedupe(lv["terminals"])
    mine = sorted(({k: r.get(k) for k in ("owner_uid", "term_uid", "term_name", "wire_uid", "is_source", "term_class", "frame_diagram")}
                   for r in rows if int(r.get("owner_uid") or 0) in NODES), key=lambda r: (r["owner_uid"], r["term_uid"]))
    es = s.es(tag, path)
    for r in mine:
        s.fact("{0} #{1} t{2} {3!r} wire {4} src {5} {6} diag {7}".format(tag, r["owner_uid"], r["term_uid"], r["term_name"], r["wire_uid"],
                                                                          r["is_source"], r["term_class"], r["frame_diagram"]))
    nm = dict((r["term_uid"], r["term_name"]) for r in mine)
    TAB[tag] = {"exec_state": es, "t11270": nm.get(11270), "t11273": nm.get(11273), "terms": mine, "unread": NOREADER,
                "n11261_inputs": [r["term_name"] for r in mine if r["owner_uid"] == 11261 and not r["is_source"]]}
    return rows


def body(s):
    print(__doc__, flush=True)
    s1m0 = K.md5(S1VI)
    s.gate("L0 S1 VI md5 == the S1 graph dump's md5", s1m0 == S1J.get("md5"), (s1m0, S1J.get("md5")))
    s.start(); s.discard_work()                                                     # noqa: E702
    bp = K.mod("bench_prep")
    be = SX.LVBackend(s, BASE["fs_tunnel_pairs"], sink_gates=[], gates={}, mem_stop_mb=SX.MEM_STOP_MB)
    be.addr.owners = BASE["owners"]                                                 # as Executor.run PRIME does (stagexec.py:1374)
    real = snap(s, "M1", s.work, BASE["fs_tunnel_pairs"])
    h1 = bp.labview_handles()
    s.gate("M1 bed copy before b2_03: t11270 'array' and t11273 'element' (graph_l2b2a)", TAB["M1"]["t11270"] == "array"
           and TAB["M1"]["t11273"] == "element", (TAB["M1"]["t11270"], TAB["M1"]["t11273"]))
    try:                                                                            # b2_03 ALONE: plan_l2b2b.json row b2_03
        r2 = be.connect(11369, 11270, real, {}, "b2_03")
    except SX.ExecStop as e:
        r2 = {"stop": str(e)[:400]}
    s.fact("M2 connect b2_03 (#11363 t11369 -> #11261 t11270): {0}".format(json.dumps(r2, default=str)[:600]))
    real = snap(s, "M2", s.work, BASE["fs_tunnel_pairs"])
    TAB["M2"]["connect"] = r2
    s.gate("M2 b2_03 connected, no op error", not r2.get("stop") and not r2.get("err"), r2)
    s.row("M2 t11270 name after b2_03 alone", TAB["M2"]["t11270"], "'element' (review alternative) / 'array' (plan)")
    try:                                                                            # M3: #11608 'output cluster' -> t11273
        r3 = be.connect(11614, 11273, real, {}, "m3")
    except SX.ExecStop as e:
        r3 = {"stop": str(e)[:400]}
    s.fact("M3 connect #11608 t11614 -> #11261 t11273: {0}".format(json.dumps(r3, default=str)[:600]))
    snap(s, "M3", s.work, BASE["fs_tunnel_pairs"])
    TAB["M3"]["connect"] = r3
    s.gate("M3 t11273 connected, no op error", not r3.get("stop") and not r3.get("err"), r3)
    s.row("M3 t11270 name after t11273 wired", TAB["M3"]["t11270"], "'array' if the open t11273 row causes the rename")
    h3 = bp.labview_handles()
    s1c = s.scratch("s1", S1VI)
    snap(s, "M4", s1c, S1J["fs_tunnel_pairs"])
    s.gate("M4 S1 copy: t11270 'array', t11273 'element'", TAB["M4"]["t11270"] == "array" and TAB["M4"]["t11273"] == "element",
           (TAB["M4"]["t11270"], TAB["M4"]["t11273"]))
    s.drop_scratch(s1c, "H4-s1")
    h4 = bp.labview_handles()
    s.fact("HANDLES after M1 {0} -> after M3 {1} -> after M4 {2}".format(h1, h3, h4))
    s.gate("HF handles flat (+-100) from the read after M1 to the end", isinstance(h1, int) and isinstance(h4, int) and abs(h4 - h1) <= 100, [h1, h3, h4])
    TAB["handles"] = [h1, h3, h4]
    TAB["md5_end"] = {"bed": K.md5(BED), "s1": K.md5(S1VI)}
    s.gate("H originals' md5 unchanged (bed 107a3ef1, S1 = dump md5)", TAB["md5_end"]["bed"] == st_md5 and TAB["md5_end"]["s1"] == s1m0, TAB["md5_end"])
    s.R["c113e"] = TAB
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BED, st_md5, "scratch_c113e_bed", preload=False, deadline_min=18,
                 out_json=os.path.join(K.BENCH, "diag_c113e_concat.json"), task="card 113-3")
    rc = K.run(body, st)
    gone = bool(getattr(g.report_all, "_dry", False)) or SX.kill_labview_at_exit()
    sys.exit(rc if gone else 1)
