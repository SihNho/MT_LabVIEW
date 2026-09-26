r"""diag_c97_tools_opbuild.py - card 97-3 (escalation of 97-2), plan PD206(d) tools 1(reader) / 4 / 5: three op VIs by
the PROVEN typed-control-seed route (tools/bench/diag_c92_clfn_thread.py build() + diag_c92b_anythread.py writer shape).
  OpCaseFrames_v1.vi      T1 reader. Donor OpSetIndexMode_v0: Traverse(Class Name,index)->IA->TMSC, TMSC retargeted by a
                          CaseStructure-typed seed -> CaseStructure.Frame Names 6365002 -> (ref/err chain)
                          MultiFrameStructure.Frames[] 6363801 -> Index Array[k] -> GObject.UID 632A813; + UID echo.
  OpTunnelUseDefault_v0.vi T5. Same donor, ConditionalTunnel-typed seed -> READ 5D251C00 (before) -> WRITE 5D251C00 ->
                          READ 5D251C00 (after), chained by reference + error so the order is dataflow; + UID echo.
  OpLabelSet_v0.vi        T4. Donor OpFPLabels_v0 (VI->Front Panel->Panel.Controls[index]->Control.Label, :build_opfplabels
                          .py:109-118) + Text.Text 632D800 WRITE on a branch of `Label` -> Text.Text READ chained after it.
FOUND FIRST (card 97-3 rule "check what exists"): OpCaseFrames_v0.vi was never runnable (build_opcaseframes_v0.log: the
MultiFrameStructure seed read ES 0); no Use-Default setter (NAMES.md:1036) and no label writer (cycle27-plan.md:2084) exist.
Ids: archive/peer/2026-09-15-case-frame-reader-property-ids.md:28-35, NAMES.md:1026-1038 (data terminal names are
CENSUSED here, never assumed). No stagekit import: an op build on donor copies, gscript only (the c92 pattern); the
target of the later self-test is a never-saved scratch (judgement c97).
PREDICTION (GATE lines, per op): D donor copy ES 1; X donor write PN deleted ES 1 (SetIndexMode donors); S seed wired
ES 1; A assembled ES 1; V COM save + labels; C COLD ES 1 in a fresh LabVIEW. Handles read at start/end.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c97_tools_opbuild.log -- py -u tools/bench/diag_c97_tools_opbuild.py
"""
import hashlib, json, os, shutil, subprocess, sys, time                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep                                                                         # noqa: E402
CD, LAB_P = g.CLAUDEDEV, os.path.join(HERE, "diag_c97_tools_oplabels.json")
STD = ("reference", "reference out", "error in (no error)", "error out")
g._run.__defaults__ = (6.0, 120.0)
G, LAB = {}, {}


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:300]), flush=True); return bool(ok)  # noqa: E702


class B(object):
    def __init__(s, donor, out):
        s.op = os.path.join(CD, out)
        if os.path.exists(s.op):
            os.remove(s.op)
        shutil.copyfile(os.path.join(CD, donor), s.op); time.sleep(0.3)                  # noqa: E702
        g.open_panel(s.op); time.sleep(1.0); s.inv0 = g.uids(s.op, "Invoke")             # noqa: E702

    def purge(s):
        junk = [u for u in g.uids(s.op, "Invoke") if u not in s.inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(s.op, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(s.op, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(s.op)

    def idx(s, cls, uid): return [o["uid"] for o in g.report_all(s.op, cls)].index(uid)

    def terms(s, uid):
        for c in range(80):
            nu, rows = g.node_terms_uid(s.op, 0, c)
            if not nu:
                return None, []
            if nu == uid:
                return c, rows
        return None, []

    def pn(s, cls, props, pos):
        r = g.build_property(s.op, cls, props, pos); s.purge(); return int(r[-1]["uid"])  # noqa: E702

    def w(s, su, st, du, dt, sc="Property", dc="Property", branch=False):
        g.wire(s.op, sc, s.idx(sc, su), st, dc, s.idx(dc, du), dt, branch=branch); s.purge()  # noqa: E702

    def panel(s, ind): return set(r["label"] for r in g.panel_wiring(s.op) if r["indicator"] == ind)

    def ind(s, uid, term):
        n, rows = s.terms(uid); t = next(r["i"] for r in rows if r["name"] == term and r["is_source"])  # noqa: E702
        b = s.panel(True); g.create_indicator(s.op, n, t); s.purge(); new = sorted(s.panel(True) - b)  # noqa: E702
        assert len(new) == 1, (term, new)
        return new[0]

    def ctl(s, uid, term):
        n, rows = s.terms(uid)
        hits = [r["i"] for r in rows if r["name"] == term and not r["is_source"]]
        free = [r["i"] for r in rows if not r["is_source"] and not r["wire"] and r["name"] not in STD]
        print("  FACT  ctl on #%s %r: terminals %r" % (uid, term, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows]), flush=True)
        t = hits[0] if hits else (free[0] if len(free) == 1 else None)
        b = s.panel(False); g.create_control(s.op, n, t); s.purge(); new = sorted(s.panel(False) - b)  # noqa: E702
        assert len(new) == 1, (term, new)
        return new[0]

    def data(s, uid, src):
        return [r["name"] for r in s.terms(uid)[1] if bool(r["is_source"]) == src and r["name"] not in STD]

    def finish(s, key, lab):
        g.set_auto_error_handling(s.op, False); s.purge(); es = g.exec_state(s.op)       # noqa: E702
        if gate("%s A assembled ExecState 1" % key, es == 1, es):
            g.save(s.op); lab["controls"] = [r["label"] for r in g.panel_wiring(s.op) if not r["indicator"]]  # noqa: E702
            LAB[key] = lab; gate("%s V saved by script" % key, os.path.getsize(s.op) > 0, (os.path.getsize(s.op), md5(s.op)))  # noqa: E702
        try:
            g.close_panel(s.op)
        except Exception:                                                                 # noqa: BLE001
            pass


def retarget(b, key, cls, props, pos):
    """diag_c92_clfn_thread.build() B2-B6 on an OpSetIndexMode_v0 copy: delete the IndexMode PN, seed-retarget the TMSC."""
    nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24)
    props0 = {p["uid"] for p in g.report_all(b.op, "Property")}
    pn_w = next((u for _k, (u, _l, t) in nodes.items() if any(x == "IndexMode" for _i, x, _w in t) and u in props0), None)
    g.delete_object(b.op, "Property", b.idx("Property", pn_w)); g.remove_bad_wires_scripted(b.op); b.purge()  # noqa: E702
    if not gate("%s X donor IndexMode PN #%s deleted, ES 1" % (key, pn_w), g.exec_state(b.op) == 1):
        return None, None
    nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24)
    tm = next(((u, t) for _k, (u, _l, t) in nodes.items() if any(x == "target class" for _i, x, _w in t)
               and any(x == "specific class reference" for _i, x, _w in t)), None)
    W = next(w for _i, x, w in tm[1] if x == "target class")
    p = b.pn(cls, props, pos)
    n, rows = b.terms(p); t_ref = next(r for r in rows if r["name"] == "reference" and not r["is_source"])  # noqa: E702
    _o, seed = g.create_control(b.op, n, t_ref["i"]); b.purge()                           # noqa: E702
    w_seed = next(r["wire"] for r in b.terms(p)[1] if r["i"] == t_ref["i"])
    wires = [o["uid"] for o in g.report_all(b.op, "Wire")]; g.delete_object(b.op, "Wire", wires.index(w_seed))  # noqa: E702
    wires = [o["uid"] for o in g.report_all(b.op, "Wire")]; g.delete_object(b.op, "Wire", wires.index(W))  # noqa: E702
    g.wire_control(b.op, [seed], "Function", b.idx("Function", tm[0]), ["target class"]); b.purge()  # noqa: E702
    b.w(tm[0], "specific class reference", p, "reference", sc="Function")
    ok = gate("%s S %s seed %r -> TMSC #%s -> PN #%s: ES 1" % (key, cls, seed, tm[0], p), g.exec_state(b.op) == 1)
    return (tm[0], p) if ok else (None, None)


def uid_echo(b, tmsc, pos):
    u = b.pn("VI Server:GObject", [("632A813", False)], pos)
    b.w(tmsc, "specific class reference", u, "reference", sc="Function", branch=True)
    return u


def build_caseframes():
    b = B("OpSetIndexMode_v0.vi", "OpCaseFrames_v1.vi"); key = "OpCaseFrames_v1"          # noqa: E702
    if not gate("%s D donor copy ES 1" % key, g.exec_state(b.op) == 1):
        return
    tm, pn_n = retarget(b, key, "VI Server:CaseStructure", [("6365002", False)], (900, 450))
    if not tm:
        return
    pn_f = b.pn("VI Server:MultiFrameStructure", [("6363801", False)], (1100, 450))
    b.w(pn_n, "reference out", pn_f, "reference"); b.w(pn_n, "error out", pn_f, "error in (no error)")  # noqa: E702
    ia = int(g.build_index_array(b.op, (1300, 450))[-1]["uid"]); b.purge()                  # noqa: E702
    fr = b.data(pn_f, True)
    b.w(pn_f, fr[0], ia, "array", dc="IndexArray")
    pn_u = b.pn("VI Server:GObject", [("632A813", False)], (1500, 450))
    b.w(ia, "element", pn_u, "reference", sc="IndexArray"); b.w(pn_f, "error out", pn_u, "error in (no error)")  # noqa: E702
    ue = uid_echo(b, tm, (900, 700))
    lab = {"names_data": b.data(pn_n, True), "frames_data": fr}
    lab["k"] = b.ctl(ia, "index")
    lab["FrameNames"] = b.ind(pn_n, lab["names_data"][0]); lab["FrameUID"] = b.ind(pn_u, "UID")  # noqa: E702
    lab["FrameErr"] = b.ind(pn_u, "error out"); lab["UID"] = b.ind(ue, "UID"); lab["UIDErr"] = b.ind(ue, "error out")  # noqa: E702
    print("  FACT  %s labels %r" % (key, lab), flush=True)
    b.finish(key, lab)


def build_usedefault():
    b = B("OpSetIndexMode_v0.vi", "OpTunnelUseDefault_v0.vi"); key = "OpTunnelUseDefault_v0"  # noqa: E702
    if not gate("%s D donor copy ES 1" % key, g.exec_state(b.op) == 1):
        return
    tm, r0 = retarget(b, key, "VI Server:ConditionalTunnel", [("5D251C00", False)], (900, 450))
    if not tm:
        return
    pw = b.pn("VI Server:ConditionalTunnel", [("5D251C00", True)], (1100, 450))
    b.w(r0, "reference out", pw, "reference"); b.w(r0, "error out", pw, "error in (no error)")  # noqa: E702
    r1 = b.pn("VI Server:ConditionalTunnel", [("5D251C00", False)], (1300, 450))
    b.w(pw, "reference out", r1, "reference"); b.w(pw, "error out", r1, "error in (no error)")  # noqa: E702
    ue = uid_echo(b, tm, (900, 700))
    lab = {"write_sink": b.data(pw, False), "read_data": b.data(r1, True)}
    lab["value_ctl"] = b.ctl(pw, lab["write_sink"][0])
    lab["Before"] = b.ind(r0, b.data(r0, True)[0]); lab["After"] = b.ind(r1, lab["read_data"][0])  # noqa: E702
    lab["Err"] = b.ind(r1, "error out"); lab["UID"] = b.ind(ue, "UID"); lab["UIDErr"] = b.ind(ue, "error out")  # noqa: E702
    print("  FACT  %s labels %r" % (key, lab), flush=True)
    b.finish(key, lab)


def build_labelset():
    b = B("OpFPLabels_v0.vi", "OpLabelSet_v0.vi"); key = "OpLabelSet_v0"                     # noqa: E702
    if not gate("%s D donor copy ES 1" % key, g.exec_state(b.op) == 1):
        return
    nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24)
    props0 = {p["uid"] for p in g.report_all(b.op, "Property")}
    pc = next((u for _k, (u, _l, t) in nodes.items() if any(x == "Label" for _i, x, _w in t) and u in props0), None)
    gate("%s X donor Control PN with a `Label` output found" % key, pc is not None, pc)
    pw = b.pn("VI Server:Text", [("632D800", True)], (900, 450))
    b.w(pc, "Label", pw, "reference", branch=True)
    pr = b.pn("VI Server:Text", [("632D800", False)], (1100, 450))
    b.w(pw, "reference out", pr, "reference"); b.w(pw, "error out", pr, "error in (no error)")  # noqa: E702
    lab = {"write_sink": b.data(pw, False), "read_data": b.data(pr, True)}
    lab["text_ctl"] = b.ctl(pw, lab["write_sink"][0])
    lab["TextBack"] = b.ind(pr, lab["read_data"][0]); lab["Err"] = b.ind(pr, "error out")  # noqa: E702
    print("  FACT  %s labels %r" % (key, lab), flush=True)
    b.finish(key, lab)


h0 = None
try:
    bench_prep.restart_labview(); g.reset(); time.sleep(3); h0 = bench_prep.labview_handles()  # noqa: E702
    print("  FACT  handles after restart %r" % h0, flush=True)
    for fn in (build_caseframes, build_usedefault, build_labelset):
        try:
            fn()
        except Exception as e:                                                            # noqa: BLE001
            import traceback
            traceback.print_exc(); gate("%s completed without an exception" % fn.__name__, False, repr(e)[:200])  # noqa: E702
    json.dump(LAB, open(LAB_P, "w"), indent=1)
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
    for key in LAB:
        p = os.path.join(CD, key + ".vi")
        gate("%s C COLD ExecState 1 (fresh LabVIEW)" % key, g.exec_state(p) == 1, md5(p))
except Exception as e:                                                                    # noqa: BLE001
    import traceback
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:200])  # noqa: E702
finally:
    try:
        print("  FACT  handles at end %r (start %r); refs %r" % (bench_prep.labview_handles(), h0, g.ref_counts()), flush=True)
    except Exception:                                                                     # noqa: BLE001
        pass
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("H LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    bad = [k for k, v in G.items() if not v]
    arts = [{"path": os.path.join(CD, k + ".vi"), "md5": md5(os.path.join(CD, k + ".vi"))} for k in LAB if os.path.exists(os.path.join(CD, k + ".vi"))]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
