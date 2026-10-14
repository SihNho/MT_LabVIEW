r"""p64p2r1_build - lean task p64p2 RETRY 1 (2026-10-15; copy of p64p2_build.py, which stays unchanged). ALL saves under
claudeDev\bench\lean. Nothing is edited inside a big P6 / S1 VI (user note 2026-10-13): byte copies + ONE callee swap.
The one change from the failed cycle (review c5): the logger has NO `error in`; `Merge Errors.vi` input 1 = the readback
chain's `error out` (2nd ValueString node), input 2 = the logger's `error out`; its output is the ONLY source of Configure
Grab's `error in` -> Configure Grab cannot start before the line is written, and a camera error is still logged.
Parts (argv[1]):
  w       [W] ConfigureGrab_rate150_<ts>.vi = EMPTY_v0 copy (body as d30c29b1 + Merge Errors as above); saved; then COLD:
              defaults (re-applied once if lost, as fixdef), then the structure gates (a)-(e) on the saved file.
  copies  A90 byte copy of S1 into bench\lean; A150 / B150 / BOBS150 = byte copy + ONE swap #13962 -> the new wrapper;
          [H] Rate150Harness_p64p2r1_<ts>.vi = byte copy of the old harness 0b0ed57c + ONE swap #44 old wrapper -> new;
          warm gates; then COLD gates (fresh LabVIEW) per file.
  run     30 s camera-only check: run the new harness ONCE (camera `cam1`), save the per-frame array, move the line file.
    py tools/bgrun.py --material --max-min 60 --log tools/bench/lean_bench/p64p2r1_build_<part>.log -- py -u tools/bench/lean_bench/p64p2r1_build.py <part>"""
import json, os, shutil, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import diag_replay_lib as L                                                              # noqa: E402
import latest_build as LB                                                                # noqa: E402 (helpers only)
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = LB.LEAN
PART = sys.argv[1] if len(sys.argv) > 1 else "w"
STATE = os.path.join(HERE, "p64p2r1_state.json")
OLD_ST = json.load(open(os.path.join(HERE, "p64p2_state.json"), encoding="utf-8"))      # the failed cycle's record, read only
ST = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
TS = ST.get("ts") or time.strftime("%Y%m%d_%H%M%S")
DXL = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb"
CG, CG_MD5 = os.path.join(DXL, "IMAQdx Configure Grab.vi"), "306a6f92c10e66ff419b3e74a315c20e"
RAS = os.path.join(DXL, "IMAQdx Read Attributes From String.vi")
OC, GI2, SA, CC = [os.path.join(DXL, "IMAQdx %s.vi" % n) for n in ("Open Camera", "Get Image2", "Stop Acquisition", "Close Camera")]
WDS = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\file.llb\Write Delimited Spreadsheet (string).vi"
IC = L.C_VI
EMPTY, EMPTY_MD5 = L.EMPTY, "6544be40470e80763764089fd2767f2a"
S3BED, S3BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi"), "0b84595245dd650c0e8fd3f57104782c"
E2W = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb\Error to Warning.vi"
GS = r"C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision Acquisition\NI-IMAQdx\Camera Attributes\Getting Started with Attributes.vi"
DON_TC, DON_N2S, DON_BA1, DON_BAP = 10972, 16746, 4117, 27844        # s3 bed (allterms_bed_20260923.json, p64p2_donorscan.py)
DON_UB = 157                                                          # Error to Warning.vi: Unbundler cluster -> status, code, source
DON_PNA, DON_PNV = 1014, 129                                          # Getting Started: [ActiveAttribute w, 4 reads] / [ValueString r]
RATE_ATTR = "CameraAttributes::AcquisitionControl::AcquisitionFrameRate"
EXP_ATTR = "CameraAttributes::AcquisitionControl::ExposureTime"
ATTR_TEXT = '[NIIMAQ_HEADER]\r\nType = 2\r\nVersion = 8\r\n\r\n[CAMERA_DATA]\r\n%s = "150"\r\n' % RATE_ATTR
CG_PANE = {11: "Session In", 10: "Number of Buffers", 8: "error in", 3: "Session Out", 0: "error out"}
PROPS = ("ReentrancyType", "IsReentrant", "ExecPriority", "PreferredExecSystem", "AllowDebugging")
OBSDIR = os.path.join(LEAN, "obs")
OBSLOG = os.path.join(OBSDIR, "configgrab_rate150.txt")
OUTD = os.path.join(HERE, "out_p64", "p64p2_r1")                      # out_p64/p64p2/ is never written
WRAP = ST.get("wrap") or os.path.join(LEAN, "ConfigureGrab_rate150_%s.vi" % TS)
HARN = ST.get("harn") or os.path.join(LEAN, "Rate150Harness_p64p2r1_%s.vi" % TS)
ME = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb\Merge Errors.vi"
ME_MD5 = "2369e859d849ae0036fe2fdd6142fc7d"
OLD_WRAP, OLD_WRAP_MD5 = os.path.join(LEAN, "ConfigureGrab_rate150_20261014_140059.vi"), "d30c29b16813e225473a77d830912528"
OLD_HARN, OLD_HARN_MD5 = os.path.join(LEAN, "Rate150Harness_p64p2_20261014_140059.vi"), "0b0ed57c81f03d94f73bc7e4e26348e2"
OLD_HARN_WCALL = 44                                                   # the old harness's wrapper call (p64p2_state.json harness.nodes.W)
N_FRAMES = 4500
CAM = "cam1"
SRC = {"A150": (L.S1, L.S1_MD5), "B150": (os.path.join(LEAN, "D1_ring_p6latest_20261014_010104.vi"), "15c664e3eed1c580e05b13e42c86566f"),
       "BOBS150": (os.path.join(LEAN, "D1_ring_p64Bobs_20261014_114246.vi"), "257fb8522d557305ab6fe2aa11a04b61")}
CG_CALL = 13962


def save_state():
    ST["ts"] = TS
    json.dump(ST, open(STATE, "w", encoding="utf-8"), indent=1, default=str)


def live(p):
    return WB.read_live(p, fs_pairs=[])


def owner_of(t, u):
    g._c97_paths()
    import build_d1_v0 as B
    return tuple(B.owner_of(t, int(u), strict=False))


def nterms(t, u):
    c, o = owner_of(t, u)
    d = g._uid_index(t, "Diagram", o)
    echo, rows = g.node_terms_uids(t, d, g._node_index(t, d, u))
    if echo != int(u):
        raise RuntimeError("node_terms echo %r != #%s" % (echo, u))
    return rows


def term(t, u, name, src, rows=None):
    h = [r for r in (rows or nterms(t, u)) if str(r["name"]) == name and bool(r["is_source"]) == bool(src)]
    if len(h) != 1:
        raise RuntimeError("#%s terminal %r src=%s: %d matches in %r" % (u, name, src, len(h), [(r["name"], r["is_source"]) for r in (rows or [])][:30]))
    return h[0]


def wire(s, t, sink, src, tag):
    """sink = (uid, name), src = (uid, name): Connect Wire terminal -> terminal (any diagram; a border makes the tunnel)"""
    a, b = term(t, sink[0], sink[1], False), term(t, src[0], src[1], True)
    r = g.connect_term_uid(t, int(a["uid"]), int(b["uid"]))
    s.gate("%s %s.%s <- %s.%s: err '' and not broken" % (tag, sink[0], sink[1], src[0], src[1]), not r.get("err") and r.get("broken") is False, r, fatal=True)
    return r


def es_settled(s, t, tag, waits=(0, 5, 15)):
    """ExecState read now / +5 s / +20 s (P6-3 saw a transient 0 right after an edit, p63_diag_wait.py)"""
    v = None
    for w in waits:
        time.sleep(w)
        v = s.es("%s +%ds" % (tag, w), t)
        if v == 1:
            break
    return v


def errlist(s, W):
    """the live Error List of W (errorlist_check, as p63_diag_wait.el) -> facts"""
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE))))
    import errorlist_check as EC
    EC._lv_imports()
    out = os.path.join(HERE, "p64p2_errorlist.json")
    R = {"errors": []}
    try:
        g.open_panel(W); time.sleep(1.0)                                                  # noqa: E702
        R["block_diagram_open"] = EC.open_diagram(W, R)
        r = EC.E.read(W, out.replace(".json", "_raw.json"), log=lambda t: print(t, flush=True), on_item=EC.make_on_item(W, R))
        R.update({k: r.get(k) for k in ("n_reported", "items", "categories")})
    except Exception as e:                                                             # noqa: BLE001
        R["errors"].append("%s: %s" % (type(e).__name__, str(e)[:200]))
    json.dump(R, open(out, "w", encoding="utf-8"), indent=1, default=str)
    for it in (R.get("items") or [])[:20]:
        s.fact("EL item %r" % ({k: it.get(k) for k in ("raw", "detail", "object", "reason")},))
    s.fact("EL n_reported %r errors %r" % (R.get("n_reported"), R["errors"]))


def same(a, b):
    if isinstance(a, bool) or isinstance(b, bool):
        return bool(a) == bool(b) and type(a) == type(b)
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def props(t):
    out = {}
    with g.vi_ref(t) as vi:
        for p in PROPS:
            try:
                v = getattr(vi, p); out[p] = v if isinstance(v, (int, float, str, bool)) else str(v)    # noqa: E702
            except Exception as e:                                                     # noqa: BLE001
                out[p] = "ERR %s" % str(e)[:60]
    return out


def top_uid(t):
    ds = [int(o["uid"]) for o in g.report_all(t, "Diagram")]
    return ds[0]


def dropsub(s, t, path, diag_uid, pos, tag):
    s0 = g.uids(t, "SubVI")
    g.drop_subvi(t, path, g._uid_index(t, "Diagram", diag_uid), pos)
    new = sorted(g.uids(t, "SubVI") - s0)
    s.gate("%s one %s node dropped" % (tag, os.path.basename(path)), len(new) == 1, new, fatal=True)
    return new[0]


def donor(s, t, diag, name, src, uid, pos, tag):
    u = g.create_primitive_nested(t, diag, name, pos, donor={"donor": src, "uid": uid})
    s.fact("%s %s #%s (donor #%d of %s)" % (tag, name, u, uid, os.path.basename(src)))
    return u


def _top_create(s, t, u, name, src, tag):
    """a top-level node (create_*_nested refuses TopLevelDiagram owners, run 3 13:59): Terminal.Create Control / Indicator
    through OpCreateControl_v0 / OpCreateIndicator_v0 on top-level Nodes[] index; the new panel object read by label diff
    and its wire read back"""
    i = int(term(t, u, name, src)["i"])
    b0 = set(l for _i, l, _ind in g.fp_labels(t))
    if src:
        g.create_indicator(t, g._node_index(t, 0, u), i)
    else:
        g.create_control(t, g._node_index(t, 0, u), i)
    nl = sorted(set(l for _i, l, _ind in g.fp_labels(t)) - b0)
    w = L.pwire(t, nl[0]) if len(nl) == 1 else 0
    s.gate("%s %s on #%s.%s -> %r, wired (w%s)" % (tag, "indicator" if src else "control", u, name, nl, w), len(nl) == 1 and w, fatal=True)
    return nl[0]


def ctl(s, t, u, name, tag):
    if owner_of(t, u)[0] == "TopLevelDiagram":
        return _top_create(s, t, u, name, False, tag)
    r = g.create_control_nested(t, u, int(term(t, u, name, False)["i"]))
    lab = (r.get("new_panel") or [{}])[0].get("label")
    s.gate("%s control on #%s.%s -> %r: err ''" % (tag, u, name, lab), not r.get("err") and len(r.get("new_panel") or []) == 1, r, fatal=True)
    return lab


def ind(s, t, u, name, tag):
    if owner_of(t, u)[0] == "TopLevelDiagram":
        return _top_create(s, t, u, name, True, tag)
    r = g.create_indicator_nested(t, u, int(term(t, u, name, True)["i"]))
    lab = (r.get("new_panel") or [{}])[0].get("label")
    s.gate("%s indicator on #%s.%s -> %r: err ''" % (tag, u, name, lab), not r.get("err") and len(r.get("new_panel") or []) == 1, r, fatal=True)
    return lab


def scratch(s, src, tag):
    dst = os.path.join(LEAN, "scratch_p64p2_%s_%s.vi" % (tag, TS))
    shutil.copyfile(src, dst); s.scratches.append(dst)                                    # noqa: E702
    s.gate("D %s donor = byte copy of %s (%s)" % (tag, os.path.basename(src), K.md5(src)), K.md5(dst) == K.md5(src), fatal=True)
    return dst


# ---------------------------------------------------------------------------------------------------------------- [W]
def build_wrapper(s):
    t = s.work
    s.head("[W] wrapper %s" % os.path.basename(t))
    s.gate("W0 work copy md5 == EMPTY_v0", K.md5(t) == EMPTY_MD5, fatal=True)
    s.gate("W0b Configure Grab md5 == start record 306a6f92", K.md5(CG) == CG_MD5, fatal=True)
    pane0 = g.conpane(t)
    s.gate("W1 EMPTY_v0 pane has 12 terminals (Configure Grab's 4x2x2x4), all free", sorted(pane0) == list(range(12)) and not any(pane0.values()), pane0, fatal=True)
    with g.vi_ref(CG) as vi:
        nb_def = vi.GetControlValue("Number of Buffers")
    cg_props = props(CG); g.reset()                                                       # noqa: E702
    s.fact("Configure Grab: Number of Buffers default %r; props %r" % (nb_def, cg_props))
    T = top_uid(t)
    don_s3, don_e2w, don_gs = scratch(s, S3BED, "s3bed"), scratch(s, E2W, "e2w"), scratch(s, GS, "gsattr")
    s.gate("D s3 bed md5 == 0b845952", K.md5(S3BED) == S3BED_MD5, fatal=True)
    g.ensure_loaded(t)
    U = {}
    U["RAS"] = dropsub(s, t, RAS, T, (100, 200), "W2")
    U["P1"] = donor(s, t, T, "IMAQdxPN_ActiveAttr", don_gs, DON_PNA, (300, 200), "W3")
    U["P2"] = donor(s, t, T, "IMAQdxPN_ValueString", don_gs, DON_PNV, (480, 200), "W3")
    U["P3"] = donor(s, t, T, "IMAQdxPN_ActiveAttr", don_gs, DON_PNA, (660, 200), "W3")
    U["P4"] = donor(s, t, T, "IMAQdxPN_ValueString", don_gs, DON_PNV, (840, 200), "W3")
    U["CG"] = dropsub(s, t, CG, T, (1100, 200), "W4")
    U["UB"] = donor(s, t, T, "Unbundle", don_e2w, DON_UB, (900, 420), "W5")
    U["TC"] = donor(s, t, T, "TickCount", don_s3, DON_TC, (900, 520), "W5")
    U["N1"] = donor(s, t, T, "NumToDecStr", don_s3, DON_N2S, (1000, 420), "W5")
    U["N2"] = donor(s, t, T, "NumToDecStr", don_s3, DON_N2S, (1000, 520), "W5")
    U["N0"] = donor(s, t, T, "NumToDecStr", don_s3, DON_N2S, (500, 400), "W5")      # requested Hz (control default 150) -> "150"
    U["BA1"] = donor(s, t, T, "BuildArray1", don_s3, DON_BA1, (600, 400), "W5")
    for k in range(1, 5):
        U["BAP%d" % k] = donor(s, t, T, "BuildArrayAppend", don_s3, DON_BAP, (640 + 90 * k, 400), "W5")
    U["WDS"] = dropsub(s, t, WDS, T, (1150, 420), "W6")
    s.gate("W6a Merge Errors.vi md5 == start record 2369e859", K.md5(ME) == ME_MD5, fatal=True)
    U["ME"] = dropsub(s, t, ME, T, (1000, 300), "W6b")
    s.fact("NODES %r" % U)
    rows = dict((k, nterms(t, u)) for k, u in U.items())
    for k, rs in rows.items():
        s.fact("TERMS %s #%s %r" % (k, U[k], [(r["name"], "OUT" if r["is_source"] else "IN") for r in rs]))
    s.R["wrap_nodes"] = U
    s.dump()
    # ---- the camera chain (error-chain order)
    SES = "IMAQdx Session"
    EIN, EOUT = "error in (no error)", "error out"
    wire(s, t, (U["P1"], SES), (U["RAS"], "Session Out"), "W7"); wire(s, t, (U["P1"], EIN), (U["RAS"], "error out"), "W7")
    for a, b in (("P2", "P1"), ("P3", "P2"), ("P4", "P3")):
        wire(s, t, (U[a], SES), (U[b], SES), "W7"); wire(s, t, (U[a], EIN), (U[b], EOUT), "W7")   # noqa: E702
    wire(s, t, (U["CG"], "Session In"), (U["P4"], SES), "W8")
    # Merge Errors (retry 1): input 1 = the readback chain (P4), input 2 = the logger; its output = Configure Grab's ONLY error in
    mi = [str(r["name"]) for r in rows["ME"] if not r["is_source"] and str(r["name"])]
    mo = [str(r["name"]) for r in rows["ME"] if r["is_source"] and str(r["name"])]
    # vi.lib names (run 1 01:57): 'error in 1 (no error)', 'error in 2 (no error)', 'error in 3 (no error)', 'error array in'
    me1 = [n for n in mi if n.startswith("error in 1")]
    me2 = [n for n in mi if n.startswith("error in 2")]
    s.gate("W8a Merge Errors: one input `error in 1..`, one `error in 2..`, one output `error out` (inputs %r, outputs %r)" % (mi, mo),
           len(me1) == 1 and len(me2) == 1 and mo == ["error out"], (mi, mo), fatal=True)
    U_ME1, U_ME2 = me1[0], me2[0]
    s.R["merge_terms"] = {"in1": U_ME1, "in2": U_ME2, "inputs": mi, "outputs": mo}
    wire(s, t, (U["ME"], U_ME1), (U["P4"], EOUT), "W8b")
    wire(s, t, (U["CG"], "error in"), (U["ME"], "error out"), "W8c")
    # ---- log branch
    ubi = [r["name"] for r in rows["UB"] if not r["is_source"]]
    s.gate("W9 unbundler: one input `cluster`", ubi == ["cluster"], ubi, fatal=True)
    wire(s, t, (U["UB"], "cluster"), (U["P4"], EOUT), "W9")
    ubo = [r["name"] for r in nterms(t, U["UB"]) if r["is_source"]]      # the outputs take the cluster's names once it is wired
    s.gate("W9b unbundler outputs after wiring == [status, code, source]", ubo == ["status", "code", "source"], ubo, fatal=True)
    wire(s, t, (U["N1"], "number"), (U["UB"], "code"), "W10"); wire(s, t, (U["N2"], "number"), (U["TC"], "millisecond timer value"), "W10")
    # every Build Array gets its typed ELEMENT first, then its array input (an untyped array wired first turns the
    # array input into a second `element`, run 2 13:55)
    wire(s, t, (U["BA1"], "element"), (U["N0"], "decimal integer string"), "W11")
    for k, (srcu, srcn) in enumerate(((U["P2"], "ValueString"), (U["P4"], "ValueString"), (U["N1"], "decimal integer string"),
                                      (U["N2"], "decimal integer string")), 1):
        wire(s, t, (U["BAP%d" % k], "element"), (srcu, srcn), "W11")
        wire(s, t, (U["BAP%d" % k], "array"), (U["BA%d" % k] if k == 1 else U["BAP%d" % (k - 1)], "appended array"), "W11")
    wire(s, t, (U["WDS"], "1D data"), (U["BAP4"], "appended array"), "W12")
    wire(s, t, (U["ME"], U_ME2), (U["WDS"], "error out"), "W12b")       # the logger's error in stays UNWIRED
    # ---- controls (pane) and value controls (defaults, not on the pane)
    lab = {}
    lab["Session In"] = ctl(s, t, U["RAS"], "Session In", "W13")
    lab["error in"] = ctl(s, t, U["RAS"], "error in", "W13")
    lab["Number of Buffers"] = ctl(s, t, U["CG"], "Number of Buffers", "W13")
    lab["Session Out"] = ind(s, t, U["CG"], "Session Out", "W13")
    lab["error out"] = ind(s, t, U["CG"], "error out", "W13")
    s.gate("W14 the 5 pane objects carry Configure Grab's labels", all(lab[k] == k for k in lab), lab, fatal=True)
    vals = {}
    vals[ctl(s, t, U["RAS"], "Attributes String In", "W15")] = ATTR_TEXT
    vals[ctl(s, t, U["P1"], "ActiveAttribute", "W15")] = RATE_ATTR
    vals[ctl(s, t, U["P3"], "ActiveAttribute", "W15")] = EXP_ATTR
    vals[ctl(s, t, U["N0"], "number", "W15")] = 150
    fpn = [r["name"] for r in rows["WDS"] if not r["is_source"] and "file path" in str(r["name"])]
    apn = [r["name"] for r in rows["WDS"] if not r["is_source"] and str(r["name"]).startswith("append")]
    s.gate("W15b logger has one `file path` and one `append` input", len(fpn) == 1 and len(apn) == 1, (fpn, apn), fatal=True)
    vals[ctl(s, t, U["WDS"], fpn[0], "W15")] = OBSLOG
    vals[ctl(s, t, U["WDS"], apn[0], "W15")] = True
    os.makedirs(OBSDIR, exist_ok=True)
    s.fact("value controls %r" % vals)
    with g.vi_ref(t) as vi:
        nb_new = vi.GetControlValue("Number of Buffers")
    if nb_new != nb_def:
        vals["Number of Buffers"] = nb_def
    s.fact("Number of Buffers default: Configure Grab %r, the created control %r" % (nb_def, nb_new))
    g.make_default(t, vals)
    with g.vi_ref(t) as vi:
        back = dict((k, vi.GetControlValue(k)) for k in list(vals) + ["Number of Buffers"])
    s.gate("W16 defaults read back (attribute text, names, '150', log path, append True, Number of Buffers == Configure Grab's %r)" % nb_def,
           all(same(back[k], v) for k, v in vals.items()) and same(back["Number of Buffers"], nb_def), back, fatal=True)
    # ---- pane
    for slot, name in sorted(CG_PANE.items()):
        g.conpane_assign(t, name, slot)
    pane = L.pane_dirs(t)
    want = dict((k, (CG_PANE.get(k), (None if k not in CG_PANE else k in (0, 3)))) for k in range(12))
    s.gate("W17 pane == Configure Grab's slot by slot (label, direction)", pane == want, (pane, want), fatal=True)
    # ---- execution settings
    with g.vi_ref(t) as vi:
        for p in ("IsReentrant", "ReentrancyType", "ExecPriority", "PreferredExecSystem", "AllowDebugging"):
            try:
                setattr(vi, p, cg_props[p])
            except Exception as e:                                                     # noqa: BLE001
                s.fact("set %s failed: %s" % (p, str(e)[:120]))
    s.safe("set_auto_error_handling(wrap, False)", lambda: g.set_auto_error_handling(t, False))
    pw = props(t)
    s.gate("W18 execution properties == Configure Grab's %r" % (PROPS,), pw == cg_props, (pw, cg_props))
    s.gate("W19 ExecState 1", s.es("wrap", t) == 1, fatal=True)
    E = struct_gates(s, t, U, s.R["merge_terms"], "W")
    g.save(t)
    m = K.md5(t); s.fact("SAVED %s md5 %s" % (t, m))                                       # noqa: E702
    g.reset()
    return {"path": t, "md5": m, "nodes": U, "labels": lab, "values": dict((k, str(v)) for k, v in vals.items()), "props": pw,
            "cg_props": cg_props, "pane": pane, "edges": len(E), "edges_set": sorted(E), "nb_default": nb_def,
            "merge_terms": s.R["merge_terms"]}


def struct_gates(s, t, U, mt, tag):
    """the wrapper's structure gates (a)-(c) on the diagram in memory (warm after the build, cold from the saved file)"""
    SES, EIN, EOUT = "IMAQdx Session", "error in (no error)", "error out"
    c = L.census(t)
    want = (RAS, CG, WDS, ME)
    s.gate("%s.c1 census == {Read Attributes From String, Configure Grab, Write Delimited Spreadsheet (string), Merge Errors}" % tag,
           sorted(os.path.normcase(str(p)) for p in c.values()) == sorted(os.path.normcase(p) for p in want), c, fatal=True)
    s.gate("%s.c2 exactly one Configure Grab, one logger, one Merge Errors call" % tag,
           all(sum(1 for p in c.values() if os.path.normcase(str(p)) == os.path.normcase(w)) == 1 for w in (CG, WDS, ME)), c)
    lv = live(t); E = L.edges(lv, {}); O = LB.own_map(lv)
    for e in sorted(E):
        s.fact("%s EDGE %r" % (tag, e))
    from collections import Counter
    cls = Counter(str(v) for v in O.values())
    s.fact("%s owner classes %r" % (tag, dict(cls)))
    s.gate("%s.c3 no serial / VISA object (class or callee name)" % tag,
           not any(("visa" in k.lower() or "serial" in k.lower()) for k in cls)
           and not any(("visa" in os.path.basename(str(p)).lower() or "serial" in os.path.basename(str(p)).lower()) for p in c.values()), dict(cls))
    tops = [u for u, cl in O.items() if cl == "TopLevelDiagram"]
    TOPU = tops[0] if len(tops) == 1 else None
    chain = {(U["RAS"], "Session Out", U["P1"], SES), (U["RAS"], "error out", U["P1"], EIN), (U["P4"], SES, U["CG"], "Session In"),
             (U["CG"], "Session Out", TOPU, "Session Out"), (U["CG"], "error out", TOPU, "error out"),
             (TOPU, "Session In", U["RAS"], "Session In"), (TOPU, "error in", U["RAS"], "error in"), (TOPU, "Number of Buffers", U["CG"], "Number of Buffers")}
    chain |= set((U[b], x, U[a], y) for a, b in (("P2", "P1"), ("P3", "P2"), ("P4", "P3")) for x, y in ((SES, SES), (EOUT, EIN)))
    s.gate("%s.c4 the camera chain edges are present (Session / error through RAS -> P1..P4; session -> Configure Grab -> outputs)" % tag,
           chain <= E, sorted(chain - E), fatal=True)
    mein = sorted(e for e in E if e[2] == U["ME"])
    meout = sorted(e for e in E if e[0] == U["ME"])
    want_in = sorted([(U["P4"], EOUT, U["ME"], mt["in1"]), (U["WDS"], "error out", U["ME"], mt["in2"])])
    s.gate("%s.a1 Merge Errors #%s inputs == exactly {%s <- readback chain's last node #%s error out, %s <- logger #%s error out}"
           % (tag, U["ME"], mt["in1"], U["P4"], mt["in2"], U["WDS"]), mein == want_in, (mein, want_in))
    s.gate("%s.a2 Merge Errors output -> Configure Grab #%s `error in` and nothing else" % (tag, U["CG"]),
           meout == [(U["ME"], "error out", U["CG"], "error in")], meout)
    cgerr = sorted(e for e in E if e[2] == U["CG"] and e[3] == "error in")
    s.gate("%s.a3 Configure Grab `error in` has exactly one source = Merge Errors" % tag, cgerr == [(U["ME"], "error out", U["CG"], "error in")], cgerr)
    cgin = sorted(e for e in E if e[2] == U["CG"])
    s.gate("%s.a4 Configure Grab's inputs are exactly Session In (P4) / Number of Buffers (pane) / error in (Merge Errors)" % tag,
           cgin == sorted([(U["P4"], SES, U["CG"], "Session In"), (TOPU, "Number of Buffers", U["CG"], "Number of Buffers"),
                           (U["ME"], "error out", U["CG"], "error in")]), cgin)
    wdsin = sorted(e for e in E if e[2] == U["WDS"])
    s.gate("%s.b the logger's `error in` is UNWIRED (logger inputs %r)" % (tag, [e[3] for e in wdsin]),
           not any(str(e[3]).startswith("error in") for e in wdsin), wdsin)
    p4err = sorted(e for e in E if e[0] == U["P4"] and e[1] == EOUT)
    s.gate("%s.a5 the readback chain's error out feeds exactly Merge Errors input 1 and the line's Unbundle" % tag,
           p4err == sorted([(U["P4"], EOUT, U["ME"], mt["in1"]), (U["P4"], EOUT, U["UB"], "cluster")]), p4err)
    return E


# ---------------------------------------------------------------------------------------------------------------- [H]
def build_harness(s, wpath):
    """retry 1: the new harness = byte copy of the old harness 0b0ed57c + ONE swap (old wrapper call #44 -> the new wrapper);
    its labels (camera / image name / indicators) are the old harness's (p64p2_state.json harness)"""
    H = HARN
    s.head("[H] harness %s = byte copy of %s + one swap" % (os.path.basename(H), os.path.basename(OLD_HARN)))
    s.gate("H0a old harness md5 == 0b0ed57c; old wrapper md5 == d30c29b1", K.md5(OLD_HARN) == OLD_HARN_MD5 and K.md5(OLD_WRAP) == OLD_WRAP_MD5, fatal=True)
    shutil.copyfile(OLD_HARN, H)
    s.gate("H0 copy md5 == old harness 0b0ed57c", K.md5(H) == OLD_HARN_MD5, fatal=True)
    g.ensure_loaded(H)
    s.gate("H1 ExecState 1 before", s.es("harness before", H) == 1, fatal=True)
    c0 = L.census(H); E0 = L.edges(live(H), {})
    ow = sorted(u for u, p in c0.items() if os.path.normcase(str(p)) == os.path.normcase(OLD_WRAP))
    s.gate("H2 exactly one call of the old wrapper, #%d" % OLD_HARN_WCALL, ow == [OLD_HARN_WCALL], (ow, c0), fatal=True)
    r = g.replace_object(H, OLD_HARN_WCALL, wpath); s.fact("harness replace #%d -> %s: %r" % (OLD_HARN_WCALL, os.path.basename(wpath), r))   # noqa: E702
    s.gate("H3 replace: no error, new uid", not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(H); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("H4 callee diff == exactly {#%d old wrapper gone, #%d -> new wrapper}" % (OLD_HARN_WCALL, nu), set(dd) == {OLD_HARN_WCALL, nu}
           and os.path.normcase(str(c1[nu])) == os.path.normcase(wpath) and os.path.normcase(str(dd[OLD_HARN_WCALL][0])) == os.path.normcase(OLD_WRAP), dd, fatal=True)
    E1 = L.edges(live(H), {nu: OLD_HARN_WCALL})
    s.gate("H5 wire-edge diff 0 after remap (%d edges)" % len(E0), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]), fatal=True)
    s.gate("H6 ExecState 1 after", s.es("harness after", H) == 1, fatal=True)
    g.save(H); g.reset()                                                                   # noqa: E702
    m = K.md5(H); s.fact("SAVED %s md5 %s" % (H, m))                                       # noqa: E702
    s.gate("H7 old harness / old wrapper md5 unchanged", K.md5(OLD_HARN) == OLD_HARN_MD5 and K.md5(OLD_WRAP) == OLD_WRAP_MD5)
    oh = OLD_ST["harness"]
    return {"path": H, "md5": m, "new_uid": nu, "edges": len(E0), "edges_set": sorted(E0), "callee_diff": dict((str(k), v) for k, v in dd.items()),
            "cam": oh["cam"], "image_name": oh["image_name"], "ind": oh["ind"], "src_md5": OLD_HARN_MD5}


def cold_harness(s, rec, wpath):
    s.head("[HC] COLD %s" % os.path.basename(rec["path"]))
    p = rec["path"]
    s.gate("HC1 harness ExecState 1 COLD", g.exec_state(p) == 1)
    Ec = L.edges(live(p), {rec["new_uid"]: OLD_HARN_WCALL})
    E0 = set(tuple(e) for e in rec["edges_set"])
    s.gate("HC2 COLD edges (remapped) == the old harness's (%d)" % len(E0), Ec == E0, (sorted(Ec - E0)[:6], sorted(E0 - Ec)[:6]))
    c = L.census(p)
    s.gate("HC3 COLD: #%d -> new wrapper, once; no old-wrapper call" % rec["new_uid"],
           os.path.normcase(str(c.get(rec["new_uid"]))) == os.path.normcase(wpath)
           and sum(1 for q in c.values() if os.path.normcase(str(q)) == os.path.normcase(wpath)) == 1
           and not any(os.path.normcase(str(q)) == os.path.normcase(OLD_WRAP) for q in c.values()), c)
    labs = [l for _i, l, _ind in g.fp_labels(p)]
    need = [rec["cam"], rec["image_name"]] + list(rec["ind"].values())
    s.gate("HC4 COLD: the harness panel carries the labels the run uses %r" % need, all(n in labs for n in need), labs)
    g.reset()
    s.gate("HC5 md5 unchanged by the cold load", K.md5(p) == rec["md5"])


# ---------------------------------------------------------------------------------------------------------------- run
def run_check(s):
    h, w = ST["harness"], ST["wrapper"]
    s.head("[R] 30 s camera-only check (no beads, no motor, no product VI)")
    s.gate("R0 tools/bench/motor_session.json exists; no STOP file", os.path.exists(os.path.join(os.path.dirname(HERE), "motor_session.json"))
           and not os.path.exists(os.path.join(HERE, "STOP")), fatal=True)
    s.gate("R1 wrapper / harness md5 as saved", K.md5(w["path"]) == w["md5"] and K.md5(h["path"]) == h["md5"], fatal=True)
    s.gate("R2 the wrapper's line file does not exist before the run", not os.path.exists(OBSLOG), OBSLOG, fatal=True)
    s.gate("R3 harness ExecState 1 (cold)", g.exec_state(h["path"]) == 1, fatal=True)
    os.makedirs(OUTD, exist_ok=True)
    # retry 1 (run 1 15:00 was stopped by a modal dialog after 8 s, no line written, screenshot not saved): the wrapper's value
    # defaults read COLD, and the dialog's own text recorded by a second poller
    with g.vi_ref(w["path"]) as vi:
        wd = dict((k, str(vi.GetControlValue(k))[:200]) for k in w["values"])
    s.fact("WRAPPER DEFAULTS COLD %r" % wd)
    g.reset()
    import threading
    dlg, stop = [], threading.Event()

    def poll():
        while not stop.wait(1.5):
            try:
                out = g._lv_gui("-Action", "dialogs")
            except Exception as e:                                                     # noqa: BLE001
                out = "poll err %s" % e
            if "BLOCKED" in out and (not dlg or dlg[-1] != out):
                dlg.append(out)
    th = threading.Thread(target=poll, daemon=True); th.start()                           # noqa: E702
    t0 = time.time()
    with g.vi_ref(h["path"]) as vi:
        # the IMAQdx session control reads ('', 0) through COM (build h3 14:58): set it as (name, 0) and READ IT BACK first
        for v in ((CAM, 0), CAM):
            try:
                vi.SetControlValue(h["cam"], v)
            except Exception as e:                                                     # noqa: BLE001
                s.fact("SetControlValue(camera, %r) raised %s" % (v, str(e)[:120]))
            cb = vi.GetControlValue(h["cam"])
            if (cb[0] if isinstance(cb, (tuple, list)) else cb) == CAM:
                break
        vi.SetControlValue(h["image_name"], "p64p2_rate150")
        s.fact("camera control reads back %r" % (cb,))
        s.gate("R3b camera control holds %r before the run" % CAM, (cb[0] if isinstance(cb, (tuple, list)) else cb) == CAM, cb, fatal=True)
        _r, rerr = s.safe("harness run", lambda: g._run(vi, hard_timeout_s=150.0))
        stop.set()
        for d in dlg:
            s.fact("DIALOG TEXT %r" % d[:1500])
        s.gate("R3c the harness run returned without a modal dialog", not rerr, rerr)
        bn = [int(x) for x in vi.GetControlValue(h["ind"]["Buffer Number Out"])]
        tk = [int(x) for x in vi.GetControlValue(h["ind"]["millisecond timer value"])]
        er = [tuple(e)[:2] for e in vi.GetControlValue(h["ind"]["error out"])]
        ce = tuple(vi.GetControlValue(h["ind"]["close error"]))[:3]
    wall = time.time() - t0
    g.reset()
    s.fact("run wall %.1f s; %d buffer numbers, %d ticks, %d errors entries; close error %r" % (wall, len(bn), len(tk), len(er), ce))
    with open(os.path.join(OUTD, "rate150_frames.txt"), "w", encoding="utf-8") as f:
        f.write("# p64p2 retry 1 30 s camera-only check, harness %s md5 %s, wrapper md5 %s; columns: i, buffer number, ms tick, error status, error code\n"
                % (os.path.basename(h["path"]), h["md5"], w["md5"]))
        for i in range(len(bn)):
            e = er[i] if i < len(er) else ("", "")
            f.write("%d\t%d\t%d\t%s\t%s\n" % (i, bn[i], tk[i] if i < len(tk) else -1, e[0], e[1]))
    lines = [ln.rstrip("\r\n") for ln in open(OBSLOG, encoding="utf-8", errors="replace")] if os.path.exists(OBSLOG) else []
    s.fact("WRAPPER LINE FILE %r" % lines)
    dst = os.path.join(OUTD, "configgrab_rate150_check.txt")
    if os.path.exists(OBSLOG):
        shutil.copyfile(OBSLOG, dst)
        if open(dst, "rb").read() == open(OBSLOG, "rb").read():
            os.remove(OBSLOG)
    s.gate("R4 line file moved to out_p64/p64p2_r1/configgrab_rate150_check.txt; obs path empty", os.path.exists(dst) and not os.path.exists(OBSLOG))
    s.gate("R5 exactly ONE wrapper line", len([x for x in lines if x.strip()]) == 1, lines)
    rec = {"wall_s": wall, "n": len(bn), "close_error": list(map(str, ce)), "lines": lines}
    if lines:
        p = lines[0].split("\t")
        rec["line"] = p
        try:
            req, rb, ex, code, tick = p[0], float(p[1]), float(p[2]), int(p[3]), int(p[4])
            rec.update(requested=req, readback=rb, exposure=ex, code=code, tick=tick)
            s.gate("R6 readback within 150 +- 0.1 (%r) and error code 0 (%r)" % (rb, code), abs(rb - 150.0) <= 0.1 and code == 0)
        except Exception as e:                                                         # noqa: BLE001
            s.gate("R6 line parses as requested, readback, exposure, code, tick", False, "%r %s" % (p, e))
    ok = [i for i in range(len(bn)) if i < len(er) and not er[i][0] and int(er[i][1]) == 0]
    s.gate("R7 every Get Image2 returned no error (%d of %d)" % (len(ok), len(bn)), len(bn) == N_FRAMES and len(ok) == len(bn), (len(ok), len(bn)))
    if len(bn) > 1:
        d = [bn[i + 1] - bn[i] for i in range(len(bn) - 1)]
        gaps = sum(x - 1 for x in d if x > 1)
        fps = (bn[-1] - bn[0]) / ((tk[-1] - tk[0]) / 1000.0) if tk[-1] != tk[0] else 0.0
        rec.update(first=bn[0], last=bn[-1], gaps=gaps, steps={str(k): d.count(k) for k in sorted(set(d))}, fps=fps,
                   span_s=(tk[-1] - tk[0]) / 1000.0, fps_rows=(len(bn) - 1) / ((tk[-1] - tk[0]) / 1000.0))
        s.fact("FRAMES first %d last %d; steps %r; gaps %d; span %.3f s; fps (buffer delta / tick delta) %.3f; rows/s %.3f"
               % (bn[0], bn[-1], rec["steps"], gaps, rec["span_s"], fps, rec["fps_rows"]))
        s.gate("R8 frames/s within 150 +- 1 %% (%.3f)" % fps, abs(fps - 150.0) <= 1.5)
        s.row("R9 buffer gaps (expected 0)", gaps, 0)
    ST["run"] = rec; save_state()


# ---------------------------------------------------------------------------------------------------------------- cold [W]
def wrapper_cold(s):
    """the failed cycle's lesson F1 (fail1.md:82-83): make_default's own read-back sees CURRENT values, the defaults were lost
    by the build save -> prove them COLD after a restart, re-apply once on the saved file if lost (as fixdef did), then the
    structure gates (a)-(e) COLD on the final saved file."""
    w = ST["wrapper"]
    want = dict(w["values"])
    want["number"] = 150
    want["append to file? (new file:F)"] = True
    p = w["path"]
    s.head("[F] wrapper defaults, proven cold")

    def cold(tag):
        s.restart()
        with g.vi_ref(p) as vi:
            got = dict((k, vi.GetControlValue(k)) for k in want)
        g.reset()
        ok = all(same(got[k], v) for k, v in want.items())
        s.fact("COLD %s %r -> %s" % (tag, dict((k, str(v)[:90]) for k, v in got.items()), ok))
        return ok
    s.gate("F0 wrapper md5 as saved %s" % w["md5"], K.md5(p) == w["md5"], fatal=True)
    ok = cold("before")
    if not ok:
        g.make_default(p, want); g.reset()                                                # noqa: E702
        ok = cold("after make_default (reentrant)")
    if not ok:
        with g.vi_ref(p) as vi:
            vi.IsReentrant = False
        g.save(p); g.make_default(p, want); g.reset()                                     # noqa: E702
        ok = cold("after make_default (NON-reentrant)")
        ST["wrapper"]["reentrant_dropped"] = True
    s.gate("F1 (d) the wrapper's value defaults hold COLD (attribute text, names, 150, log path, append True)", ok, fatal=True)
    m = K.md5(p)
    s.fact("WRAPPER md5 now %s (build save %s)" % (m, w["md5"]))
    ST["wrapper"]["md5_build"] = w["md5"]; ST["wrapper"]["md5"] = m                          # noqa: E702
    save_state()
    s.restart()
    s.head("[WC] COLD structure gates on the saved wrapper %s" % os.path.basename(p))
    with g.vi_ref(p) as vi:
        nb = vi.GetControlValue("Number of Buffers")
    s.gate("WC0 (d) Number of Buffers default COLD == Configure Grab's %r" % w["nb_default"], same(nb, w["nb_default"]), nb)
    s.gate("WC1 (e) wrapper ExecState 1 COLD", g.exec_state(p) == 1)
    pw = props(p); g.reset()                                                              # noqa: E702
    pane = L.pane_dirs(p); g.reset()                                                      # noqa: E702
    want_p = dict((k, (CG_PANE.get(k), (None if k not in CG_PANE else k in (0, 3)))) for k in range(12))
    s.gate("WC2 (e) pane COLD == Configure Grab's slot by slot", pane == want_p, pane)
    s.gate("WC3 (e) execution properties COLD == Configure Grab's %r" % (w["cg_props"],), pw == w["cg_props"], (pw, w["cg_props"]))
    g.ensure_loaded(p)
    U = dict((k, int(v)) for k, v in w["nodes"].items())
    Ec = struct_gates(s, p, U, w["merge_terms"], "WC")
    s.gate("WC4 COLD edges == the warm build's (%d)" % len(w["edges_set"]), Ec == set(tuple(e) for e in w["edges_set"]),
           (sorted(Ec - set(tuple(e) for e in w["edges_set"]))[:6], sorted(set(tuple(e) for e in w["edges_set"]) - Ec)[:6]))
    g.reset()
    s.gate("WC5 wrapper md5 unchanged by the cold checks", K.md5(p) == m)
    ST["wrapper"]["props_final"] = pw; save_state()                                       # noqa: E702


# ---------------------------------------------------------------------------------------------------------------- copies
def build_copy(s, tag, wpath):
    src, smd5 = SRC[tag]
    s.head("[C %s] from %s" % (tag, os.path.basename(src)))
    if tag == "A150":
        a90 = os.path.join(LEAN, "D1_s1_p64A_%s.vi" % TS)
        shutil.copyfile(src, a90)
        s.gate("C%s.a A90 = byte copy of S1 in bench\\lean (md5 3e3d23ce)" % tag, K.md5(a90) == smd5, a90, fatal=True)
        ST["a90"] = {"path": a90, "md5": K.md5(a90)}
        src = a90
    dst = os.path.join(LEAN, {"A150": "D1_s1_p64A150_%s.vi", "B150": "D1_ring_p64B150_%s.vi", "BOBS150": "D1_ring_p64Bobs150_%s.vi"}[tag] % TS)
    shutil.copyfile(src, dst)
    s.gate("C%s.0 copy md5 == source %s" % (tag, smd5[:8]), K.md5(dst) == smd5, fatal=True)
    g.ensure_loaded(dst)
    s.gate("C%s.1 ExecState 1 before" % tag, s.es("%s before" % tag, dst) == 1, fatal=True)
    c0 = L.census(dst); E0 = L.edges(live(dst), {})
    cg = sorted(u for u, p in c0.items() if os.path.basename(str(p)).lower() == "imaqdx configure grab.vi")
    s.gate("C%s.2 exactly one Configure Grab call, #%d" % (tag, CG_CALL), cg == [CG_CALL], cg, fatal=True)
    r = g.replace_object(dst, CG_CALL, wpath); s.fact("%s replace #%d -> %s: %r" % (tag, CG_CALL, os.path.basename(wpath), r))
    s.gate("C%s.3 replace: no error, new uid" % tag, not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(dst); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("C%s.4 callee diff == exactly {#%d gone, #%d -> wrapper}" % (tag, CG_CALL, nu), set(dd) == {CG_CALL, nu}
           and os.path.normcase(str(c1[nu])) == os.path.normcase(wpath), dd, fatal=True)
    s.gate("C%s.5 the wrapper at exactly one call site; no Configure Grab call left" % tag,
           sum(1 for p in c1.values() if os.path.normcase(str(p)) == os.path.normcase(wpath)) == 1
           and not any(os.path.basename(str(p)).lower() == "imaqdx configure grab.vi" for p in c1.values()), fatal=True)
    E1 = L.edges(live(dst), {nu: CG_CALL})
    s.gate("C%s.6 wire-edge diff 0 after remap (%d edges)" % (tag, len(E0)), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]), fatal=True)
    s.gate("C%s.7 ExecState 1 after" % tag, s.es("%s after" % tag, dst) == 1, fatal=True)
    g.save(dst); g.reset()                                                                 # noqa: E702
    m = K.md5(dst); s.fact("SAVED %s md5 %s" % (dst, m))                                   # noqa: E702
    s.gate("C%s.8 source md5 unchanged" % tag, K.md5(SRC[tag][0]) == smd5)
    return {"path": dst, "md5": m, "new_uid": nu, "edges": len(E0), "edges_set": sorted(E0), "callee_diff": dict((str(k), v) for k, v in dd.items())}


def cold_copy(s, tag, rec, wpath):
    s.head("[CC %s] COLD %s" % (tag, os.path.basename(rec["path"])))
    p = rec["path"]
    s.gate("CC%s.1 ExecState 1 COLD" % tag, g.exec_state(p) == 1)
    Ec = L.edges(live(p), {rec["new_uid"]: CG_CALL})
    E0 = set(tuple(e) for e in rec["edges_set"])
    s.gate("CC%s.2 COLD edges (remapped) == the source's (%d)" % (tag, len(E0)), Ec == E0, (sorted(Ec - E0)[:6], sorted(E0 - Ec)[:6]))
    c = L.census(p)
    s.gate("CC%s.3 COLD: #%d -> wrapper, once; no Configure Grab call" % (tag, rec["new_uid"]),
           os.path.normcase(str(c.get(rec["new_uid"]))) == os.path.normcase(wpath)
           and sum(1 for q in c.values() if os.path.normcase(str(q)) == os.path.normcase(wpath)) == 1
           and not any(os.path.basename(str(q)).lower() == "imaqdx configure grab.vi" for q in c.values()), c.get(rec["new_uid"]))
    g.reset()
    s.gate("CC%s.4 md5 unchanged by the cold load" % tag, K.md5(p) == rec["md5"])


def body(s):
    s.start(); R = s.R
    if PART == "w":
        ST["wrap"], ST["harn"] = WRAP, HARN
        R["wrapper"] = ST["wrapper"] = build_wrapper(s); save_state(); s.dump()          # noqa: E702
        wrapper_cold(s)
        R["wrapper"] = dict((k, v) for k, v in ST["wrapper"].items() if k != "edges_set")
    elif PART == "run":
        run_check(s)
    elif PART == "wcold":                                                                 # re-run of the cold gates only
        wrapper_cold(s)
    elif PART == "copies":
        wp = ST["wrapper"]["path"]
        s.gate("P0 wrapper md5 as saved (after the cold defaults step)", K.md5(wp) == ST["wrapper"]["md5"], fatal=True)
        ST.setdefault("copies", {})
        for tag in ("A150", "B150", "BOBS150"):
            if tag in ST["copies"]:
                continue
            s.restart()
            ST["copies"][tag] = build_copy(s, tag, wp); save_state(); s.dump()           # noqa: E702
        if not ST.get("harness"):
            s.restart()
            ST["harness"] = build_harness(s, wp); save_state(); s.dump()                 # noqa: E702
        for tag in ("A150", "B150", "BOBS150"):
            s.restart()
            cold_copy(s, tag, ST["copies"][tag], wp); s.dump()                            # noqa: E702
        s.restart()
        cold_harness(s, ST["harness"], wp); s.dump()                                      # noqa: E702
        s.gate("P9 wrapper md5 unchanged", K.md5(wp) == ST["wrapper"]["md5"])
        R["copies"] = dict((k, dict((kk, vv) for kk, vv in v.items() if kk != "edges_set")) for k, v in ST["copies"].items())
        R["harness"] = dict((k, v) for k, v in ST["harness"].items() if k != "edges_set")
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + tuple(("src " + k, p, m) for k, (p, m) in SRC.items()) + (
        ("Configure Grab", CG, CG_MD5), ("EMPTY_v0", EMPTY, EMPTY_MD5), ("Merge Errors", ME, ME_MD5),
        ("old wrapper", OLD_WRAP, OLD_WRAP_MD5), ("old harness", OLD_HARN, OLD_HARN_MD5))
    work = WRAP if PART == "w" else os.path.join(LEAN, "scratch_p64p2r1_%s_work_%s.vi" % (PART, time.strftime("%H%M%S")))
    st = St(EMPTY, EMPTY_MD5, "p64p2r1_build_" + PART, preload=False, deadline_min=58, work_dir=LEAN, work_name=os.path.basename(work), pins=pins,
            task="lean-p64p2r1", out_json=os.path.join(HERE, "p64p2r1_build_%s.json" % PART))
    if PART != "w":
        st.scratches.append(st.work)
    if PART == "w" and ST.get("wrapper"):
        sys.exit("p64p2r1_build w: a wrapper is already recorded in p64p2r1_state.json; nothing done")
    sys.exit(K.run(body, st))
