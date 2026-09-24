r"""diag_replay_skeleton - card 76-4 pass lines 3+4 (m8 plan PD16(c)(d), PD17(c')). Runs only op VIs; no target VI is run.
PRIOR ART: connect_ctl (OpConnectCtl_v0, sink = panel terminal, source = Nodes[] terminal; gscript.py connect_ctl) is the donor;
no ctl->ind verb exists (docs/toolkit-capabilities.md:25). Creators: build_index_array/build_property/connect_terminals/
create_control/copy_by_index (Close Reference = KernelBuilder_v1 #157, as diag_swap_build.py); pane: conpane/conpane_assign;
swap: replace_object (PD15). Unowned-pane candidate tried FIRST = "a new VI whose pane is set by scripting" (EMPTY_v0 copy +
controls created FROM a dropped IMAQdx Get Image node, so every type is the vi.lib terminal's own).
PREDICTION: V1 OpConnectCtlInd_v0 ES 1 warm and COLD, 2+ Close Reference nodes; K1 EMPTY_v0 pane has 12 free slots;
K2 9 panel objects created (5 ctl, 4 ind); K3 per slot label+direction == IMAQdx Get Image.vi; K4 VI.Name has no ':'
(no lvlib); K5 ES 1 cold; K6 replace #529 in a get-buff scratch by the base: every terminal wired before is wired after,
ES 1 (type check of the wired slots); T1 verb wires Session/error/Buffer Number In->Out (same wire uid both ends), ES 1;
T2 20 delete+reconnect calls, handles range <= 100; H vi.lib GI + lvlib + get-buff md5 unchanged, LabVIEW gone."""
import os, sys, json, shutil, subprocess, time                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                     # noqa: E402
g = K.g; bp = K.mod("bench_prep")
D = K.CLAUDEDEV; RP = os.path.join(D, "replay"); os.makedirs(RP, exist_ok=True)
DONOR, OP, KB = [os.path.join(D, n) for n in ("OpConnectCtl_v0.vi", "OpConnectCtlInd_v0.vi", "KernelBuilder_v1.vi")]
EMPTY, BASE = os.path.join(D, "EMPTY_v0.vi"), os.path.join(RP, "replay_imaqdx_pane_base.vi")
GI = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Get Image.vi"
LIB = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\NI_Vision_Acquisition_Software.lvlib"
GB = os.path.join(D, "background VIs_COPY", "get buff image-lost frames.vi"); LAB = os.path.join(K.BENCH, "replay_vis_76_ctlind_labels.json")
s = K.Stage(DONOR, None, "replay_skel_76c", fresh=False, preload=False, deadline_min=40, pins=(),
            out_json=os.path.join(K.BENCH, "replay_vis_76c_skeleton.json"), task="76-4")
PIN = {k: K.md5(p) for k, p in (("GI", GI), ("lvlib", LIB), ("gb", GB))}; s.R["pins"] = PIN
CI = []


def sweep(t):
    out = {}
    for n in range(60):
        u, r = g.node_terms_uid(t, 0, n)
        if not u:
            break
        out[int(u)] = (n, r)
    return out


def assign(t, pairs):
    """conpane_assign without its per-call save + full re-read (each free slot read = one ~8 s dialog, gscript.conpane)"""
    g.open_panel(t); time.sleep(0.5); labels = [l for _i, l, _ind in g.fp_labels(t)]; vi = g.op(g.OP_CONPANE_ASSIGN)
    for slot, l in pairs:
        vi.SetControlValue("vi path", t); vi.SetControlValue("index", labels.index(l)); vi.SetControlValue("Terminal Index", int(slot))
        for x in ("Names", "Names 2"):
            vi.SetControlValue(x, [])
        for x in ("Class Name", "Class Name 2"):
            vi.SetControlValue(x, "")
        g._run(vi); e = g._err(vi)
        if e:
            raise RuntimeError("assign {0}->{1}: {2}".format(l, slot, e))


def T(by, u, name=None, src=None):
    return next((r for r in by[u][1] if (name is None or r["name"] == name) and (src is None or r["is_source"] == src)), None)


def has(by, name, src):
    return [u for u in by if T(by, u, name, src)]


def idx(t, cls, uid):
    return [int(o["uid"]) for o in g.report_all(t, cls)].index(uid)


def close_ref(ref_src, err_src=None):
    """one Close Reference copied into OP, `reference` <- ref_src (node uid, terminal name), error in <- err_src"""
    if not CI:
        s.restart(); CI.append(next((i, c) for c in ("Node", "Function") for i, o in enumerate(g.report(KB, c)) if int(o["uid"]) == 157))
    ci = CI[0]; g.reset(); s.restart()

    def fin(dst, added):
        b = sweep(dst); cr = [u for u in b if u in set(int(o["uid"]) for o in added)][0]
        for (u, nm), sink in [(x, k) for x, k in ((ref_src, "reference"), (err_src, "error in")) if x]:
            if u:
                g.connect_terminals(dst, b[cr][0], T(b, cr, sink, False)["i"] if T(b, cr, sink, False) else
                                    next(r["i"] for r in b[cr][1] if r["name"].startswith(sink)), b[u][0], T(b, u, nm, True)["i"])
    return g.copy_by_index(KB, ci[1], ci[0], OP, expect_uid=157, finish=fin)


def build_verb():
    s.head("[A] OpConnectCtlInd_v0 from OpConnectCtl_v0"); s.restart()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copy2(DONOR, OP); g.open_panel(OP); by = sweep(OP)
    cpn, inv, bd, pn_n, pn_t = [has(by, *a)[0] for a in (("Controls[]", True), ("Wire Source", False), ("Diagram", True),
                                                          ("Nodes[]", True), ("Terms[]", True))]
    ia = {w: u for u in by for r in by[u][1] if r["name"] == "array" and not r["is_source"] for w in [r["wire"]]}
    ia_n, ia_t = ia[T(by, pn_n, "Nodes[]", True)["wire"]], ia[T(by, pn_t, "Terms[]", True)["wire"]]
    s.fact("donor: Controls[] #{0} invoke #{1} ladder {2}".format(cpn, inv, (bd, pn_n, ia_n, pn_t, ia_t)))
    ia2 = int(g.build_index_array(OP, (760, 420))[0]["uid"]); pn2 = int(g.build_property(OP, "VI Server:Control", [("6332006", False)], (900, 420))[0]["uid"])
    by = sweep(OP)
    g.connect_terminals(OP, by[ia2][0], T(by, ia2, "array", False)["i"], by[cpn][0], T(by, cpn, "Controls[]", True)["i"])
    g.connect_terminals(OP, by[pn2][0], T(by, pn2, "reference", False)["i"], by[ia2][0], T(by, ia2, "element", True)["i"])
    w = T(by, inv, "Wire Source", False)["wire"]; g.delete_object(OP, "Wire", idx(OP, "Wire", w), verify=False)
    for cls, u in (("Property", bd), ("Property", pn_n), ("IndexArray", ia_n), ("Property", pn_t), ("IndexArray", ia_t)):
        g.delete_object(OP, cls, idx(OP, cls, u))
    s.fact("RBW after the ladder delete: {0}".format(g.remove_bad_wires_scripted(OP))); by = sweep(OP)
    g.connect_terminals(OP, by[inv][0], T(by, inv, "Wire Source", False)["i"], by[pn2][0], T(by, pn2, "Terminal", True)["i"])
    _n, lab = g.create_control(OP, by[ia2][0], T(by, ia2, "index", False)["i"])
    es = g.exec_state(OP); s.gate("V0 verb assembled, ES 1 before Close References", es == 1, (es, lab), fatal=True); g.save(OP)
    json.dump({"index_sink": "index", "index_source": lab, "error": "error out 2"}, open(LAB, "w"), indent=1)
    vr = has(sweep(OP), "vi reference", True)[0]
    for ref, err in (((inv, "reference out"), None), ((pn2, "Terminal"), (inv, "error out")), ((vr, "vi reference"), (inv, "error out"))):
        s.fact("Close Reference on {0}: {1}".format(ref, close_ref(ref, err)[1]))
    s.restart(); lbl = [x["label"] for x in g.node_labels(OP, 0)]
    s.gate("V1 OpConnectCtlInd_v0 ES 1 COLD, 3 Close Reference", g.exec_state(OP) == 1 and lbl.count("Close Reference") >= 3,
           (lbl.count("Close Reference"), K.md5(OP)))
    s.R["verb"] = {"path": OP, "md5": K.md5(OP), "labels": json.load(open(LAB)), "node_labels": lbl}


def build_base():
    s.head("[B] unowned pane-identical base (candidate: new VI + pane set by script)")
    if os.path.exists(BASE):
        os.remove(BASE)
    shutil.copy2(EMPTY, BASE); g.open_panel(BASE)
    gi_pane, gi_fp = g.conpane(GI), {l: ind for _i, l, ind in g.fp_labels(GI)}
    k1 = g.conpane(BASE); s.gate("K1 EMPTY_v0 pane: 12 slots, all free", len(k1) == 12 and not any(k1.values()), k1, fatal=True)
    g.drop_subvi(BASE, GI, 0, (400, 300)); by = sweep(BASE); gu = has(by, "Session In", False)[0]
    for r in by[gu][1]:
        if r["name"]:
            (g.create_indicator if r["is_source"] else g.create_control)(BASE, by[gu][0], r["i"])
    fp = {l: ind for _i, l, ind in g.fp_labels(BASE)}
    s.gate("K2 9 panel objects, labels == GI's pane labels", set(fp) == set(l for l in gi_pane.values() if l), (sorted(fp), gi_pane), fatal=True)
    g.delete_object(BASE, "SubVI", idx(BASE, "SubVI", gu)); s.fact("RBW {0}".format(g.remove_bad_wires_scripted(BASE)))
    assign(BASE, [(slot, l) for slot, l in sorted(gi_pane.items()) if l]); g.save(BASE)
    pane = g.conpane(BASE); d = {k: (pane.get(k), fp.get(pane.get(k))) for k in gi_pane if (pane.get(k), fp.get(pane.get(k))) != (gi_pane[k], gi_fp.get(gi_pane[k]))}
    s.gate("K3 per slot label+direction == IMAQdx Get Image.vi", not d, d); g.save(BASE)
    s.restart()
    with g.vi_ref(BASE) as v:
        nm = str(v.Name)
    s.gate("K4 VI.Name has no library qualifier", ":" not in nm, nm); s.gate("K5 base ES 1 COLD", g.exec_state(BASE) == 1, K.md5(BASE))
    sc = s.scratch("GB", source=GB); b0 = sweep(sc); w0 = {r["name"]: bool(r["wire"]) for r in b0[529][1] if r["name"]}
    rep = g.replace_object(sc, 529, BASE); b1 = sweep(sc); nu = rep["new_uid"]
    w1 = {r["name"]: bool(r["wire"]) for r in b1[nu][1] if r["name"]} if nu in b1 else {}
    s.gate("K6 replace #529 by the base keeps every wire, ES 1", w1 == w0 and g.exec_state(sc) == 1, (rep, w0, w1))
    s.drop_scratch(sc, "K6"); s.R["base"] = {"path": BASE, "md5": K.md5(BASE), "pane": pane, "fp": fp, "name": nm}


def test_verb():
    s.head("[T] verb on a scratch of the base"); sc = s.scratch("T", source=BASE); g.open_panel(sc)
    L = [l for _i, l, _ind in g.fp_labels(sc)]
    prs = [(L.index(a + " Out" if a != "error" else "error out"), L.index(a + " In" if a != "error" else "error in")) for a in ("Session", "error", "Buffer Number")]
    errs = [g.connect_ctl_ind(sc, k, c) for k, c in prs]; pw = g.panel_wiring(sc)
    ok = all(pw[k]["wire"] and pw[k]["wire"] == pw[c]["wire"] for k, c in prs)
    s.gate("T1 Session/error/BN In->Out wired (same uid both ends), ES 1", ok and g.exec_state(sc) == 1, (errs, [(pw[k]["wire"], pw[c]["wire"]) for k, c in prs]))
    hs = []
    for _i in range(20):
        w = g.panel_wiring(sc)[prs[0][0]]["wire"]; g.delete_object(sc, "Wire", idx(sc, "Wire", w), verify=False)
        g.connect_ctl_ind(sc, *prs[0]); hs.append(bp.labview_handles())
    pw = g.panel_wiring(sc); s.R["handles20"] = hs
    s.gate("T2 20 delete+reconnect: wired at the end, handles range <= 100", pw[prs[0][0]]["wire"] == pw[prs[0][1]]["wire"] != 0 and max(hs) - min(hs) <= 100, (min(hs), max(hs)))
    s.drop_scratch(sc, "T")


for fn in (build_verb, build_base, test_verb):
    try:
        fn()
    except K.Stop as e:
        s.gate("STOP {0}".format(e), False); break
    except Exception as e:                                                               # noqa: BLE001
        import traceback; traceback.print_exc(); s.gate("{0} completed without exception".format(fn.__name__), False, str(e)[:200]); break  # noqa: E702
s.R["ref_counts"] = g.ref_counts(); s.fact("ref_counts {0}".format(s.R["ref_counts"])); g.reset()  # noqa: E702
s.gate("H1 vi.lib GI, lvlib, get-buff md5 unchanged", {k: K.md5(p) for k, p in (("GI", GI), ("lvlib", LIB), ("gb", GB))} == PIN, PIN)
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(6); s.gate("H2 LabVIEW gone", "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout)
s.dump(); sys.exit(s.summary())
