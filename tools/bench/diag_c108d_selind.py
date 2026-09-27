r"""diag_c108d_selind - card 108-4 V2: SCRATCH-VI verification of gscript.create_indicator_nested's new SelectorTunnel
OUTER-face route (card 108-4 V1: gscript._selector_outer_face + _create_on_selector_outer) BEFORE any stage uses it.
FIXTURE: a byte copy of claudeDev\TRACK_kernel_v1.vi - the smallest VI on disk with a Case Structure whose OUTPUT tunnels
feed pane indicators (case 154; 3 output tunnels -> pane indicators; ExecState 1, tools/bench/build_track_kernel_v1.log:60-66).
The copy is a scratch (discard_work): never saved, deleted at close; TRACK_kernel_v1.vi is never opened for writing; the
stage input (L2-A2) is not touched. No VI is run - only op VIs execute.
PRIOR ART: create_indicator_nested LoopTunnel route (card 100-4, OpTunnelInd_v0), its Node route (diag_c100_verbs_build2.log:
75-79), the PD185 owner route (stagexec._triple), selftest_c98_move.py (fixture / gate shape). NO NEW OP VI.
PREDICTION (gates):
 F  >=1 SelectorTunnel OUTER source face wired to a ControlTerminal; ExecState 1 before
 V  create_indicator_nested(W, <face term uid>, None): err '', route SelectorTunnel owner, echo == the owner case uid, exactly
    1 new panel object on the face's wire, ControlTerminal +1, Wire count unchanged (a BRANCH)
 R  graph read back (allterms): the face is still the ONLY source on its wire; the wire's sinks == before + the new
    indicator's terminal, which sits on the face's diagram
 E  ExecState 1 after
 A  alias (SelectorTunnel uid, None) -> same route, +1 indicator on the same wire
 N  NEGATIVE: the tunnel's INNER face and an INPUT tunnel's outer face -> ValueError, ControlTerminal count unchanged
 H  20 more calls: handles flat +-100; refs closed (H5); scratch deleted; fixture md5 unchanged; LabVIEW gone at exit
    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/diag_c108d_selind.log -- py -u tools/bench/diag_c108d_selind.py
"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g                                                  # noqa: E401,E402
PL = json.load(open(os.path.join(K.BENCH, "diag_c108d_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
SZ = PL["sizes"]
FIX = os.path.join(g.CLAUDEDEV, PL["input"]["vi"])
FUNC = "gscript.create_indicator_nested"
REC_DIR = os.path.join(K.BENCH, "scratch_verify")


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work(); W = s.work; bp = K.mod("bench_prep")               # noqa: E702
    RL = lambda: K.mod("wiki_build").read_live(W, fs_pairs=[])["terminals"]          # noqa: E731  rows WITH term_class
    rows = RL()
    byw = lambda rs, w: [r for r in rs if int(r["wire_uid"] or 0) == w]              # noqa: E731
    faces = [r for r in rows if r["owner_class"] == "SelectorTunnel" and r["term_class"] == "OuterTerminal" and r["is_source"]
             and int(r["wire_uid"] or 0) and any(x["term_class"] == "ControlTerminal" for x in byw(rows, int(r["wire_uid"])))]
    s.fact("F {0} SelectorTunnel outer source face(s) feeding a ControlTerminal: {1}".format(
        len(faces), [(f["owner_uid"], f["term_uid"], f["wire_uid"], f["term_name"]) for f in faces]))
    s.gate("F >=1 SelectorTunnel OUTER source face wired to a ControlTerminal", faces, fatal=True)
    s.gate("F ExecState 1 before", s.es("before") == 1, fatal=True)
    f = faces[0]; w = int(f["wire_uid"]); tun = int(f["owner_uid"])                  # noqa: E702
    sinks0 = sorted(int(x["term_uid"]) for x in byw(rows, w) if not x["is_source"])
    ct0, w0 = g.count(W, "ControlTerminal"), g.count(W, "Wire")
    r = g.create_indicator_nested(W, int(f["term_uid"]), None)
    s.fact("V result {0}".format(json.dumps(r, default=str)))
    np_ = r.get("new_panel") or []
    s.gate("V err '' and route = SelectorTunnel owner", not r["err"] and "SelectorTunnel" in str(r.get("route")), (r["err"], r.get("route")))
    s.gate("V echo == the owner case uid", r["echo"] == (r.get("face") or {}).get("case") and r["echo"] > 0, (r["echo"], r.get("face")))
    s.gate("V exactly 1 new panel object, on the face's wire w{0}".format(w), len(np_) == 1 and int(np_[0].get("wire") or 0) == w, np_)
    s.gate("V ControlTerminal +1, Wire count unchanged (branch)", g.count(W, "ControlTerminal") == ct0 + 1 and g.count(W, "Wire") == w0,
           (ct0, g.count(W, "ControlTerminal"), w0, g.count(W, "Wire")))
    rows2 = RL()
    on = byw(rows2, w); srcs = [int(x["term_uid"]) for x in on if x["is_source"]]  # noqa: E702
    sinks1 = sorted(int(x["term_uid"]) for x in on if not x["is_source"])
    new = [x for x in on if int(x["term_uid"]) in [int(t) for t in r.get("new_terminals") or []]]
    s.gate("R the face is the ONLY source on w{0}".format(w), srcs == [int(f["term_uid"])], srcs)
    s.gate("R sinks == before + the new indicator's terminal", len(new) == 1 and sinks1 == sorted(sinks0 + [int(new[0]["term_uid"])]),
           {"before": sinks0, "after": sinks1, "new": [x["term_uid"] for x in new]})
    s.gate("R the new terminal is a ControlTerminal on the face's diagram", new and new[0]["term_class"] == "ControlTerminal" and
           new[0]["frame_diagram"] == f["frame_diagram"], new and (new[0]["term_class"], new[0]["frame_diagram"], f["frame_diagram"]))
    s.gate("E ExecState 1 after", s.es("after V") == 1)
    ra = g.create_indicator_nested(W, tun, None)
    s.gate("A alias (SelectorTunnel #{0}, None): same route, 1 new panel object on w{1}".format(tun, w),
           not ra["err"] and ra.get("face", {}).get("face_term") == int(f["term_uid"]) and len(ra.get("new_panel") or []) == 1 and
           int(ra["new_panel"][0].get("wire") or 0) == w, (ra["err"], ra.get("face"), ra.get("new_panel")))
    inner = [x for x in rows2 if int(x["owner_uid"]) == tun and x["term_class"] != "OuterTerminal"]
    ins = [x for x in rows2 if x["owner_class"] == "SelectorTunnel" and x["term_class"] == "OuterTerminal" and not x["is_source"]]
    for tag, cand in (("INNER face", inner), ("INPUT tunnel outer face", ins)):
        ct1 = g.count(W, "ControlTerminal")
        v, err = s.safe("N " + tag, lambda c=cand: g.create_indicator_nested(W, int(c[0]["term_uid"]), None)) if cand else (None, "no candidate")
        s.gate("N {0} -> ValueError, ControlTerminal unchanged".format(tag), cand and v is None and err.startswith("ValueError") and
               g.count(W, "ControlTerminal") == ct1, (cand and cand[0]["term_uid"], err, ct1, g.count(W, "ControlTerminal")))
    h1 = bp.labview_handles(); errs = []                                            # noqa: E702
    for _k in range(SZ["NCALL"]):
        errs.append(g.create_indicator_nested(W, int(f["term_uid"]), None)["err"])
    h2 = bp.labview_handles()
    s.gate("H {0} more calls: no error, handles flat +-{1} ({2} -> {3})".format(SZ["NCALL"], SZ["HANDLE_TOL"], h1, h2),
           not any(errs) and abs(h2 - h1) <= SZ["HANDLE_TOL"], [e for e in errs if e][:3])
    s.gate("E ExecState 1 after all calls", s.es("after H") == 1)
    s.R["c108d"] = {"face": f, "result": r, "alias": ra, "handles": [h1, h2]}; s.dump()   # noqa: E702


if __name__ == "__main__":
    st = K.Stage(FIX, K.md5(FIX), "scratch_c108d_selind", preload=False, deadline_min=SZ["DEADLINE_MIN"], pins=K.DEFAULT_PINS[:SZ["NPINS"]],
                 out_json=os.path.join(K.BENCH, "diag_c108d_selind.json"), task="card 108-4 V2")
    K.run(body, st)
    DRY = bool(getattr(g.report_all, "_dry", False))                                # stage_d1_l2a3.py's dry test
    if not DRY:
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        st.gate("H LabVIEW gone at exit", gone)
    rc = st.summary()
    if rc == 0 and not DRY:
        os.makedirs(REC_DIR, exist_ok=True)
        rec = os.path.join(REC_DIR, "{0}_{1}.json".format(FUNC, st.stamp))
        json.dump({"function": FUNC, "status": "PASS", "t": time.time(), "card": "108-4", "route": "SelectorTunnel outer face via owner "
                   "CaseStructure Terms[] (OpCreateIndicatorNested_v0)", "fixture": "TRACK_kernel_v1.vi byte copy",
                   "log": "tools/bench/diag_c108d_selind.log"}, open(rec, "w", encoding="utf-8"), indent=1)
    sys.exit(rc)
