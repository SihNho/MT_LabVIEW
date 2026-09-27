r"""diag_c112a_ctltun - card 112-1 T2 SCRATCH VERIFY of the new stagexec 'ctltun' route (PD225(h)3 (ii), B2-15 shape):
a BARE ControlTerminal SOURCE -> a structure Tunnel's OUTER SINK, written by gscript.wire_ctlsink (OpCtlSinkWire_v1) with the
roles REVERSED (Connect Wire invoked ON the CT, `Wire Source` = the owner CaseStructure's Terminals[t]). The route stands on
LabVIEW wiring by the terminals' directions; this measures it. FIXTURE: a scratch byte copy (discard_work, deleted at close)
of claudeDev\background VIs_COPY\Motor control.vi (never the bed, never a D1_* file): its case-selector 'Tunnel' #613 is
fed by ControlTerminal #483 'Home' (docs/wiki/subvi/Motor control.json; diag_c112a_fixture.log). Nothing saved, no VI run.
PRIOR ART: stagekit delete_wire / uid_index / es; gscript node_labels / node_terms_uid / wire_ctlsink; wiki_build.read_live.
PREDICTION: F the fixture row exists (Tunnel outer sink whose wire's ONE source is a CT) and exactly one node on its diagram
holds that wire at a sink Terminals[t]; C after delete_wire the face is bare at the same index; W wire_ctlsink returns no
error and Wire +1; R the face's new wire has exactly ONE source = the CT, the index t reads that wire; E ExecState back to
its pre-cut value; H scratch deleted, fixture md5 unchanged, LabVIEW gone.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c112a_ctltun.log -- py -u tools/bench/diag_c112a_ctltun.py"""
import json, os, subprocess, sys, time                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g                                                  # noqa: E401,E402
FIX = os.path.join(g.CLAUDEDEV, "background VIs_COPY", "Motor control.vi")
FIX_MD5 = K.md5(FIX)
FUNC, REC_DIR = "stagexec.ctl_to_tunnel", os.path.join(K.BENCH, "scratch_verify")


def fixture_row(rows):
    byw = {}
    for r in rows:
        if r["wire_uid"]:
            byw.setdefault(int(r["wire_uid"]), []).append(r)
    for r in rows:
        if r["owner_class"] == "Tunnel" and r["term_class"] == "OuterTerminal" and not r["is_source"] and r["wire_uid"]:
            src = [x for x in byw[int(r["wire_uid"])] if x["is_source"]]
            if len(src) == 1 and src[0]["term_class"] == "ControlTerminal" and len(byw[int(r["wire_uid"])]) == 2:
                return r, src[0]
    return None, None


def owner_slot(W, didx, w):
    hits = []
    for ni, u in enumerate(int(x["uid"]) for x in g.node_labels(W, didx)):
        echo, nt = g.node_terms_uid(W, didx, ni)
        hits += [(ni, echo, int(t["i"]), t) for t in nt if int(t["wire"] or 0) == w and not t["is_source"]]
    return hits


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work(); W = s.work                                         # noqa: E702
    rows = K.mod("wiki_build").read_live(W, fs_pairs=[])["terminals"]
    sel, ct = fixture_row(rows)
    s.gate("F a Tunnel outer sink fed by ONE ControlTerminal exists", sel is not None, (sel, ct), fatal=True)
    w, D = int(sel["wire_uid"]), int(sel["frame_diagram"])
    s.fact("FIXTURE tunnel #{0} outer t{1} <- CT #{2} {3!r} on wire {4}, diagram #{5}".format(
        sel["owner_uid"], sel["term_uid"], ct["term_uid"], ct["term_name"], w, D))
    didx = [int(d["uid"]) for d in g.report_all(W, "Diagram")].index(D)
    hits = owner_slot(W, didx, w)
    s.gate("F exactly one node on the diagram holds the wire at a sink Terminals[t] (the owner route)", len(hits) == 1,
           [(h[0], h[1], h[2]) for h in hits], fatal=True)
    ni, owner, t, t0 = hits[0]
    cs = [int(o["uid"]) for o in g.report_all(W, "CaseStructure")]
    s.gate("F the owner is a CaseStructure (the B2-15 shape)", owner in cs, (owner, len(cs)), fatal=True)
    es0 = s.es("before cut")
    s.delete_wire(w, "cut CT -> selector")
    _e, nt = g.node_terms_uid(W, didx, ni)
    s.gate("C the face is bare at the same Terminals[t], same name/direction", int(nt[t]["wire"] or 0) == 0 and
           nt[t]["name"] == t0["name"] and not nt[t]["is_source"], nt[t])
    same = [x for x in nt if (x["name"], bool(x["is_source"]), int(x["wire"] or 0)) == (t0["name"], False, 0)]
    s.fact("AFTER CUT: {0} bare sink(s) named {1!r} on the owner (1 = uniquely addressable by (name,dir,wire))".format(
        len(same), t0["name"]))
    ci, oi = s.uid_index("ControlTerminal", int(ct["term_uid"])), s.uid_index("CaseStructure", owner)
    wc0 = g.count(W, "Wire")
    dw, err = g.wire_ctlsink(W, ci, "CaseStructure", oi, t)
    s.fact("wire_ctlsink(CT[{0}] #{1}, CaseStructure[{2}] #{3}, t{4}) -> delta {5}, err {6!r}".format(
        ci, ct["term_uid"], oi, owner, t, dw, err))
    s.gate("W wire_ctlsink (roles reversed) returns no error and Wire +1", not err and g.count(W, "Wire") == wc0 + 1,
           (dw, err, wc0, g.count(W, "Wire")))
    _e, nt2 = g.node_terms_uid(W, didx, ni)
    nw = int(nt2[t]["wire"] or 0)
    rows2 = K.mod("wiki_build").read_live(W, fs_pairs=[])["terminals"]
    on = [r for r in rows2 if nw and int(r["wire_uid"] or 0) == nw]
    srcs = [r["term_uid"] for r in on if r["is_source"]]
    s.gate("R the face's new wire has ONE source = the CT, and the selector outer face is on it",
           nw != 0 and srcs == [ct["term_uid"]] and any(r["term_uid"] == sel["term_uid"] for r in on), (nw, srcs, len(on)))
    es1 = s.es("after reconnect")
    s.gate("E ExecState back to its pre-cut value", es1 == es0, (es0, es1))
    s.R["c112a"] = {"tunnel": sel["owner_uid"], "face": sel["term_uid"], "ct": ct["term_uid"], "owner": owner, "t": t,
                    "new_wire": nw, "es": [es0, es1], "same_name_bare_after_cut": len(same)}
    s.dump()


if __name__ == "__main__":
    st = K.Stage(FIX, FIX_MD5, "scratch_c112a_ctltun", deadline_min=15, out_json=os.path.join(K.BENCH, "diag_c112a_ctltun.json"),
                 task="card 112-1 T2")
    K.run(body, st)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    st.gate("H LabVIEW gone at exit; fixture md5 unchanged; scratch deleted", gone and K.md5(FIX) == FIX_MD5 and
            not os.path.exists(st.work), (gone, K.md5(FIX), os.path.exists(st.work)))
    rc = st.summary()
    if rc == 0:
        os.makedirs(REC_DIR, exist_ok=True)
        json.dump({"function": FUNC, "status": "PASS", "t": time.time(), "card": "112-1", "route": "ctltun: CT own uid -> "
                   "owner CaseStructure Terminals[t] via OpCtlSinkWire_v1 roles reversed", "fixture": "Motor control.vi byte copy",
                   "facts": st.R.get("c112a"), "log": "tools/bench/diag_c112a_ctltun.log"},
                  open(os.path.join(REC_DIR, "{0}_{1}.json".format(FUNC, st.stamp)), "w", encoding="utf-8"), indent=1)
    sys.exit(rc)
