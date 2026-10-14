r"""p64p1_build - lean task p64p1 (P6-4 preparation P-1): the start-value wrapper and the 90 Hz observer copy BOBS90.
ALL saves under claudeDev\bench\lean (gscript.save refuses elsewhere). Nothing is edited inside the big P6 VI (user note
2026-10-13): BOBS90 is a byte copy of the final VI 15c664e3 with exactly two callee swaps (replace_object).
  [S] COLD read-only of 15c664e3: census (the #31710 / #6810 callees), wire edges (the cold reference for [C]).
  [G] GetBuffLog_<ts>.vi = byte copy of PickLog_latestobs e5810aec (Write Delimited Spreadsheet (I64), pane {11: 1D data}) with
      ONE change: the path control's default -> claudeDev\bench\lean\obs\getbuff_first.txt (make_default; append stays True).
  [W] GetBuffFirst_<ts>.vi = the Stage's work copy = byte copy of get buff (9aaaef21, same pane / execution settings by
      construction). Its 4 body nodes (#529 IMAQdx Get Image, #581 mode constant, #76 Subtract, #65 Equal To 0?) are deleted and
      replaced by ONE call of the get-buff file 15c664e3's #6810 calls, every input / output wired straight through (9 edges).
      Log branch: Tick Count (bed #10972), Build Array (bed #25992, 3 elements) = [Buffer to extract (requested), current image
      number (returned), tick] -> a ONE-iteration While loop whose UNINITIALIZED shift register (False until the first call writes
      True) selects a Case (DonorCase_v0); the logger sits in its FALSE frame only. (No First Call? donor exists: p64p1_lvprobe
      scans 1+2 read 155 VIs and found none; the GUI Quick Drop route is not permitted in this session.)
  [T] two TEST copies of [W]: inner call -> replay_get_buff_image_paced60 (Out = In) / the P6-3 gap wrapper (Out = In + 1).
  [H] two harnesses (byte copies of EMPTY_v0): ONE For loop (parallelism off), ONE test-wrapper node, Buffer to extract
      auto-indexed from an I64[] control; 3 calls per run. Runs: warm x2 + cold x1 per harness -> exactly 1 log line per run.
  [B] BOBS90 = byte copy of 15c664e3; #31710 -> RingPickSlot_latestobs 9504e0cf; #6810 -> [W]. Callee diff == exactly the
      two swaps; edge diff 0 after remap; ES 1; the wrapper at exactly ONE call site.
  [C] cold: [W] ES 1, pane == get buff's, execution properties == get buff's; BOBS90 ES 1, cold edges == [S] edges; md5s kept.
    py tools/bgrun.py --material --max-min 75 --log tools/bench/lean_bench/p64p1_build.log -- py -u tools/bench/lean_bench/p64p1_build.py"""
import json, os, shutil, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import diag_replay_lib as L                                                              # noqa: E402
import latest_build as LB                                                                # noqa: E402 (helpers only)
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = LB.LEAN
TS = time.strftime("%Y%m%d_%H%M%S")
GB, GB_MD5 = L.GB, "9aaaef21e8426035f64a04ec816491d0"                       # claudeDev byte copy of the original get buff
FIX, FIX_MD5 = os.path.join(LEAN, "D1_ring_p6latest_20261014_010104.vi"), "15c664e3eed1c580e05b13e42c86566f"
RPSL, RPSL_MD5 = os.path.join(LEAN, "RingPickSlot_latest_20261014_010104.vi"), "8fc2ec267b3919402124f23a40f9ffae"
OBS, OBS_MD5 = os.path.join(LEAN, "RingPickSlot_latestobs_20261014_025316.vi"), "9504e0cffe372cd6ad35ab6842ec089d"
PLOG, PLOG_MD5 = os.path.join(LEAN, "PickLog_latestobs_20261014_025316.vi"), "e5810aecfc6f78aa1469c6061946b5b9"
PACED, PACED_MD5 = os.path.join(L.RP, "replay_get_buff_image_paced60.vi"), "59ec66b61f3518b049a3c532a8e65482"
GAPW, GAPW_MD5 = os.path.join(LEAN, "gap_get_buff_image_paced60_20261013_161639.vi"), "a885a8fbc06351ab789d539af460a8d7"
EMPTY, EMPTY_MD5 = L.EMPTY, "6544be40470e80763764089fd2767f2a"
BED, BED_MD5 = LB.BED, LB.BED_MD5
PICK_CALL, GB_CALL = 31710, 6810
TOP = 3                                                   # get buff's top-level diagram uid (p64p1_lvprobe.log)
BODY = {529: "IMAQdx Get Image", 581: "Buffer Number Mode constant", 76: "Subtract", 65: "Equal To 0?"}
INS = ["Session In", "Image In", "Buffer to extract", "error in"]
OUTS = ["Session Out", "Image Out", "Missed frames?", "current image number", "error out"]
GB_PANE = {0: ("Session In", False), 1: (None, None), 2: (None, None), 3: (None, None), 4: ("Session Out", True), 5: ("Image In", False),
           6: ("Image Out", True), 7: ("Buffer to extract", False), 8: ("Missed frames?", True), 9: (None, None),
           10: ("current image number", True), 11: ("error in", False), 12: (None, None), 13: (None, None), 14: (None, None),
           15: ("error out", True)}
PROPS = ("ReentrancyType", "IsReentrant", "ExecPriority", "PreferredExecSystem", "AllowDebugging")
DON_TICK, DON_BA3 = 10972, 25992                          # bed graph: Tick Count; Build Array with 3 `element` inputs
PLOG_PATH_LABEL = "file path (dialog if empty)"
OBSDIR = os.path.join(LEAN, "obs")
OBSLOG = os.path.join(OBSDIR, "getbuff_first.txt")
OUT = os.path.join(HERE, "out_p64")
WRAP = os.path.join(LEAN, "GetBuffFirst_%s.vi" % TS)
LOGGER = os.path.join(LEAN, "GetBuffLog_%s.vi" % TS)
TEST = {"paced": os.path.join(LEAN, "GetBuffFirst_test_paced_%s.vi" % TS), "gap": os.path.join(LEAN, "GetBuffFirst_test_gap_%s.vi" % TS)}
INNER = {"paced": (PACED, PACED_MD5), "gap": (GAPW, GAPW_MD5)}
HARN = {"paced": os.path.join(LEAN, "GetBuffFirst_harness_paced_%s.vi" % TS), "gap": os.path.join(LEAN, "GetBuffFirst_harness_gap_%s.vi" % TS)}
BOBS = os.path.join(LEAN, "D1_ring_p64Bobs_%s.vi" % TS)
BDON = os.path.join(LEAN, "scratch_p64p1_bdon_%s.vi" % TS)
FDON = os.path.join(LEAN, "scratch_p64p1_fcdon_%s.vi" % TS)
VEC = [8217, 8218, 8219]
PROBE = os.path.join(HERE, "p64p1_lvprobe.json")


def live(p):
    return WB.read_live(p, fs_pairs=[])


def nrows(p):
    return sum(1 for ln in open(p, encoding="utf-8", errors="replace") if ln.strip()) if os.path.isfile(p) else 0


def last_line(p):
    ls = [ln for ln in open(p, encoding="utf-8", errors="replace") if ln.strip()]
    return [int(round(float(x))) for x in ls[-1].strip().split("\t")] if ls else None


def fc_donor():
    """the First Call? donor found by p64p1_lvprobe's scan (a claudeDev byte copy of a background VI): (file, md5, uid)"""
    env = os.environ.get("P64P1_FC")
    if env:
        f, u = env.split("::")
        return f, K.md5(f), int(u)
    fj = os.path.join(HERE, "p64p1_fcdonor.json")
    if os.path.exists(fj):
        rec = json.load(open(fj, encoding="utf-8"))
        if rec.get("saved"):
            return rec["path"], rec["md5"], int(rec["uid"])
    hits = []
    for p in (PROBE, PROBE.replace(".json", "_scan2.json")):
        if os.path.exists(p):
            pr = json.load(open(p, encoding="utf-8"))
            hits += [h for h in (pr.get("scan") or {}).get("hits", []) if any(str(t[0]).lower() == "first call?" and t[1] for t in h["terms"])]
    if not hits:
        raise RuntimeError("no First Call? donor in %s (+ _scan2)" % PROBE)
    h = hits[0]
    return h["file"], h["md5"], int(h["uid"])


def props(t):
    out = {}
    with g.vi_ref(t) as vi:
        for p in PROPS:
            try:
                v = getattr(vi, p)
                out[p] = v if isinstance(v, (int, float, str, bool)) else str(v)
            except Exception as e:                                                     # noqa: BLE001
                out[p] = "ERR %s" % str(e)[:60]
    return out


def owner_of(t, u):
    g._c97_paths()
    import build_d1_v0 as B
    return tuple(B.owner_of(t, int(u), strict=False))


def del_uid(s, t, u, tag):
    for cls in ("SubVI", "Function", "EnumConstant", "Constant", "Node"):
        order = [int(o["uid"]) for o in g.report_all(t, cls)]
        if int(u) in order:
            gone = g.delete_object(t, cls, order.index(int(u)), verify=True)
            s.fact("%s deleted #%d (%s) as %s: gone %r" % (tag, u, BODY.get(u, ""), cls, gone))
            return cls
    raise RuntimeError("%s: #%d not found in any class" % (tag, u))


# ---------------------------------------------------------------------------------------------------------------- [S]
def source_read(s):
    s.head("[S] COLD read-only %s" % os.path.basename(FIX))
    s.gate("S0 15c664e3 ExecState 1 cold", g.exec_state(FIX) == 1, fatal=True)
    c = L.census(FIX)
    E = L.edges(live(FIX), {})
    rp = sorted(u for u, p in c.items() if os.path.basename(str(p)).lower() == os.path.basename(RPSL).lower())
    gb = sorted(u for u, p in c.items() if os.path.basename(str(p)).lower() == "get buff image-lost frames.vi")
    s.fact("15c664e3: %d edges; RingPickSlot_latest calls %r; get-buff calls %r (%r)" % (len(E), rp, gb, [c[u] for u in gb]))
    s.gate("S1 exactly one RingPickSlot_latest call, #%d" % PICK_CALL, rp == [PICK_CALL], rp, fatal=True)
    s.gate("S2 exactly one get-buff call, #%d" % GB_CALL, gb == [GB_CALL], gb, fatal=True)
    gbp = str(c[GB_CALL])
    s.gate("S3 #%d's callee file md5 == 9aaaef21 (the original get buff)" % GB_CALL, K.md5(gbp) == GB_MD5, (gbp, K.md5(gbp)), fatal=True)
    s.R["source"] = {"edges": len(E), "census_n": len(c), "gb_path": gbp, "pick_path": str(c[PICK_CALL])}
    g.reset()
    return E, c, gbp


# ---------------------------------------------------------------------------------------------------------------- [G]
def build_logger(s):
    s.head("[G] logger %s" % os.path.basename(LOGGER))
    shutil.copyfile(PLOG, LOGGER)
    s.gate("G0 logger copy md5 == PickLog e5810aec", K.md5(LOGGER) == PLOG_MD5, fatal=True)
    g.ensure_loaded(LOGGER)
    s.gate("G1 logger ExecState 1", s.es("logger", LOGGER) == 1, fatal=True)
    os.makedirs(OBSDIR, exist_ok=True)
    g.make_default(LOGGER, {PLOG_PATH_LABEL: OBSLOG})
    with g.vi_ref(LOGGER) as vi:
        ap = vi.GetControlValue("append to file? (new file:F)")
    s.gate("G2 path default -> obs\\getbuff_first.txt (read back by make_default), append default True", bool(ap), ap, fatal=True)
    pane = g.conpane(LOGGER)
    s.gate("G3 logger pane: only terminal 11 = 1D data", [k for k, v in pane.items() if v] == [11] and pane[11] == "1D data", pane, fatal=True)
    s.gate("G4 logger ExecState 1 after", s.es("logger saved", LOGGER) == 1, fatal=True)
    m = K.md5(LOGGER); s.fact("SAVED %s md5 %s" % (LOGGER, m))                            # noqa: E702
    g.reset()
    return {"path": LOGGER, "md5": m}


# ---------------------------------------------------------------------------------------------------------------- [W]
def build_wrapper(s, gbp, logger):
    t = s.work
    s.head("[W] wrapper %s" % os.path.basename(t))
    s.gate("W0 work copy md5 == get buff 9aaaef21", K.md5(t) == GB_MD5, fatal=True)
    s.gate("W1 ExecState 1 before", s.es("wrap before", t) == 1, fatal=True)
    p0 = props(t); s.fact("PROPS before %r" % p0)                                         # noqa: E702
    lv0 = live(t); E0 = L.edges(lv0, {})
    own0 = sorted(set(int(r["owner_uid"]) for r in lv0["terminals"]))
    s.gate("W2 owners == top + the 4 body nodes", own0 == sorted([TOP] + list(BODY)), own0, fatal=True)
    for u in (65, 76, 529, 581):
        del_uid(s, t, u, "W3")
    s.fact("RBW %r" % (g.remove_bad_wires_scripted(t),))
    lv1 = live(t)
    s.gate("W4 only the top-level terminals left, no wire", sorted(set(int(r["owner_uid"]) for r in lv1["terminals"])) == [TOP]
           and not any(int(r["wire_uid"] or 0) for r in lv1["terminals"]), fatal=True)
    s0 = g.uids(t, "SubVI")
    g.drop_subvi(t, gbp, 0, (300, 200))
    new = sorted(g.uids(t, "SubVI") - s0)
    s.gate("W5 one get-buff node dropped", len(new) == 1, new, fatal=True)
    G = new[0]
    c = L.census(t)
    s.gate("W6 census == {#%d: the get-buff file 15c664e3 calls}" % G, set(c) == {G} and os.path.normcase(str(c[G])) == os.path.normcase(gbp), c, fatal=True)
    lv = live(t)
    con = {}
    for n in INS:
        r = g.connect_term_uid(t, int(LB.trow(lv, G, n, False)["term_uid"]), int(LB.trow(lv, TOP, n, True)["term_uid"]))
        con[n] = r; s.gate("W7 %s -> get buff: err '' and not broken" % n, not r.get("err") and r.get("broken") is False, r, fatal=True)   # noqa: E702
    for n in OUTS:
        r = g.connect_term_uid(t, int(LB.trow(lv, TOP, n, False)["term_uid"]), int(LB.trow(lv, G, n, True)["term_uid"]))
        con[n] = r; s.gate("W7 get buff -> %s: err '' and not broken" % n, not r.get("err") and r.get("broken") is False, r, fatal=True)   # noqa: E702
    lv2 = live(t); E2 = L.edges(lv2, {})
    plan = set((TOP, n, G, n) for n in INS) | set((G, n, TOP, n) for n in OUTS)
    s.gate("W8 edges == exactly the 9 pass-through edges", E2 == plan, (sorted(E2 - plan), sorted(plan - E2)), fatal=True)
    s.gate("W9 ExecState 1 (pass-through only)", s.es("wrap pass", t) == 1, fatal=True)
    # ---- log branch
    shutil.copyfile(BED, BDON); s.scratches.append(BDON)                                  # noqa: E702
    s.gate("W10 donor = byte copy of the P6 bed c2d9c13c", K.md5(BDON) == BED_MD5, fatal=True)
    TC = g.create_primitive_nested(t, TOP, "TickCount", (200, 470), donor={"donor": BDON, "uid": DON_TICK})
    BA = g.create_primitive_nested(t, TOP, "BuildArray", (360, 400), donor={"donor": BDON, "uid": DON_BA3})
    s.fact("new Tick Count #%s, Build Array #%s" % (TC, BA))
    lv = live(t)
    echo, rs = g.node_terms_uids(t, 0, g._node_index(t, 0, BA))
    els = sorted([r for r in rs if str(r["name"]) == "element" and not r["is_source"]], key=lambda r: int(r["i"]))
    bout = [r for r in rs if str(r["name"]).startswith("appended") and r["is_source"]]
    s.gate("W13 Build Array = 3 element inputs + 1 output, unwired", echo == BA and len(els) == 3 and len(bout) == 1 and len(rs) == 4
           and not any(int(r["wire"] or 0) for r in rs), rs, fatal=True)
    srcs = [("S Buffer to extract", LB.trow(lv, TOP, "Buffer to extract", True)), ("R current image number", LB.trow(lv, G, "current image number", True)),
            ("tick", LB.trow(lv, TC, "millisecond timer value", True))]
    order = []
    for (tag, src), el in zip(srcs, els):
        r = g.connect_term_uid(t, int(el["uid"]), int(src["term_uid"]))
        con["BA." + tag] = r; order.append((tag, int(el["i"])))                         # noqa: E702
        s.gate("W14 BA element(i%s) <- %s: err '' and not broken" % (el["i"], tag), not r.get("err") and r.get("broken") is False, r, fatal=True)
    s.fact("Build Array column order (terminal index ascending = array index): %r" % order)
    s.gate("W15 ExecState 1 after the Build Array", s.es("wrap BA", t) == 1, fatal=True)
    # ---- the once-latch (no First Call? creation route here, report section 2): a ONE-iteration While loop (stop terminal <-
    # Boolean constant True) with ONE UNINITIALIZED shift register: left inner -> case selector, right inner <- the same True.
    # The register holds False (its default) until the clone's first call writes True -> the FALSE frame (logger) runs once per
    # load of the clone; every later call takes the empty TRUE frame.
    d0, w0 = g.uids(t, "Diagram"), g.uids(t, "WhileLoop")
    g.while_loop(t, (560, 330))
    WLs, bodies = sorted(g.uids(t, "WhileLoop") - w0), sorted(g.uids(t, "Diagram") - d0)
    s.gate("W16 one While loop + one body diagram", len(WLs) == 1 and len(bodies) == 1, (WLs, bodies), fatal=True)
    WL, body = WLs[0], bodies[0]
    wi = L.fidx(t, "WhileLoop", WL)
    wc = g.create_const_loop_term(t, "while_cond", wi, value=True)
    C = int(wc.get("created_uid") or 0)
    bc = g.read_bool_const(t, C) if C else {}
    s.fact("stop constant %r value %r" % (wc, bc))
    s.gate("W17 stop terminal <- Boolean constant #%d, value True (read back)" % C, C and not wc.get("err") and not wc.get("inv_err")
           and bc.get("value") is True and not bc.get("err"), (wc, bc), fatal=True)
    rsr = g.add_shift_reg(t, wi, 60, "WhileLoop")
    lv = live(t)
    rin = [r for r in lv["terminals"] if int(r["owner_uid"]) == rsr and r["term_class"] == "InnerTerminal" and not r["is_source"]]
    lsrs = sorted(set(int(r["owner_uid"]) for r in lv["terminals"] if r["owner_class"] == "LeftShiftRegister"))
    lin = [r for r in lv["terminals"] if int(r["owner_uid"]) in lsrs and r["term_class"] == "InnerTerminal" and r["is_source"]]
    lout = [r for r in lv["terminals"] if int(r["owner_uid"]) in lsrs and r["term_class"] == "OuterTerminal"]
    s.fact("SR right #%d inner %r; left %r inner %r outer %r" % (rsr, rin, lsrs, lin, lout))
    s.gate("W18 one shift register: right inner sink, left inner source, left outer (initializer) unwired",
           len(rin) == 1 and len(lsrs) == 1 and len(lin) == 1 and all(not int(r["wire_uid"] or 0) for r in lout), (rin, lsrs, lin, lout), fatal=True)
    cout = [r for r in lv["terminals"] if int(r["owner_uid"]) == C and r["is_source"]]
    r = g.connect_term_uid(t, int(rin[0]["term_uid"]), int(cout[0]["term_uid"]))
    con["sr_right <- True"] = r
    s.gate("W19 right SR <- the True constant: err '' and not broken", not r.get("err") and r.get("broken") is False, r, fatal=True)
    cp = g.struct_copy_nested(t, body, "CaseStructure", {"donor": g.DONOR_CASE, "uid": g.DONOR_CASE_UID}, (140, 40))
    case = cp["uid"]
    di = g._uid_index(t, "Diagram", body)
    ce, crows = g.node_terms_uids(t, di, g._node_index(t, di, case))
    bare = [x for x in crows if not x["is_source"] and not int(x["wire"] or 0)]
    s.gate("W20 case #%d in the loop body, exactly one bare sink (the selector)" % case, ce == case and len(bare) == 1, crows, fatal=True)
    r = g.connect_term_uid(t, int(bare[0]["uid"]), int(lin[0]["term_uid"]))
    con["selector <- left SR"] = r
    s.gate("W21 case selector <- left SR: err '' and not broken", not r.get("err") and r.get("broken") is False, r, fatal=True)
    fr = g.case_frames(t, case)
    names = [str(n).strip() for n in fr["names"]]
    s.gate("W22 case frames {False, True}", sorted(names) == ["False", "True"], fr, fatal=True)
    ff = fr["frames"][names.index("False")]
    s1 = g.uids(t, "SubVI")
    g.drop_subvi(t, logger["path"], g._uid_index(t, "Diagram", ff), (40, 40))
    new = sorted(g.uids(t, "SubVI") - s1)
    s.gate("W23 one logger node dropped", len(new) == 1, new, fatal=True)
    LG = new[0]
    s.gate("W23b the logger node sits in the FALSE frame d%s" % ff, owner_of(t, LG) == ("Diagram", int(ff)), owner_of(t, LG), fatal=True)
    lv = live(t)
    r = g.connect_term_uid(t, int(LB.trow(lv, LG, "1D data", False)["term_uid"]), int(LB.trow(lv, BA, bout[0]["name"], True)["term_uid"]))
    con["logger"] = r
    s.gate("W24 logger 1D data <- Build Array (into loop + False frame): err '' and not broken", not r.get("err") and r.get("broken") is False, r, fatal=True)
    lv3 = live(t); E3 = L.edges(lv3, {}); O3 = LB.own_map(lv3)
    newo = sorted(set(O3) - {TOP, G})
    tun = sorted(u for u in newo if "Tunnel" in str(O3[u]) and any(e[2] == u for e in E3) and any(e[0] == u for e in E3))
    Ec = LB.collapse(E3, tun)
    removed, added = sorted(E2 - Ec), sorted(Ec - E2)
    s.fact("W25 new owners %r (%r); collapsed tunnels %r; removed %r; added %r" % (newo, [O3[u] for u in newo], tun, removed, added))
    plan_src = {(TOP, "Buffer to extract"), (G, "current image number"), (TC, "millisecond timer value"), (BA, bout[0]["name"])}
    srcs_ok = all((a, ta) in plan_src or a in (C, lsrs[0]) for a, ta, _b, _tb in added)
    s.gate("W25 edge diff: nothing removed; every added edge from a planned source (S, R, tick, BA, True constant, left SR); "
           "BA -> logger 1D data present", not removed and srcs_ok and (BA, bout[0]["name"], LG, "1D data") in set(Ec)
           and any(a == C and b == rsr for a, _ta, b, _tb in added), (removed, added), fatal=True)
    s.gate("W26 the logger's 1D data has the Build Array as its only source", [e for e in Ec if e[2] == LG] == [(BA, bout[0]["name"], LG, "1D data")],
           [e for e in Ec if e[2] == LG], fatal=True)
    s.gate("W27 the 9 pass-through edges are unchanged", plan <= Ec, fatal=True)
    s.gate("W28 ExecState 1 after", s.es("wrap after", t) == 1, fatal=True)
    c = L.census(t)
    s.gate("W29 census == {get buff, logger}", c == {G: c.get(G), LG: c.get(LG)} and os.path.normcase(str(c[G])) == os.path.normcase(gbp)
           and os.path.normcase(str(c[LG])) == os.path.normcase(logger["path"]), c, fatal=True)
    p1 = props(t); s.fact("PROPS after %r" % p1)                                          # noqa: E702
    s.gate("W30 execution properties unchanged %r" % (PROPS,), p1 == p0, (p0, p1), fatal=True)
    g.save(t)
    m = K.md5(t); s.fact("SAVED %s md5 %s" % (t, m))                                       # noqa: E702
    g.reset()
    return {"path": t, "md5": m, "get_buff_uid": G, "tick": TC, "build_array": BA, "while": WL, "body": body, "stop_const": C,
            "sr_right": rsr, "sr_left": lsrs[0], "case": case, "false_frame": ff, "logger_node": LG, "ba_order": order,
            "added": added, "props": p1, "connects": con, "gb_path": gbp}


# ---------------------------------------------------------------------------------------------------------------- [T]
def build_test(s, tag, w):
    dst = TEST[tag]; inner, inner_md5 = INNER[tag]
    s.head("[T %s] %s" % (tag, os.path.basename(dst)))
    shutil.copyfile(w["path"], dst)
    s.gate("T%s.0 copy md5 == wrapper" % tag, K.md5(dst) == w["md5"], fatal=True)
    s.gate("T%s.0b inner file md5 == %s" % (tag, inner_md5[:8]), K.md5(inner) == inner_md5, fatal=True)
    g.ensure_loaded(dst)
    c0 = L.census(dst); E0 = L.edges(live(dst), {})
    r = g.replace_object(dst, w["get_buff_uid"], inner); s.fact("T%s replace #%d -> %s: %r" % (tag, w["get_buff_uid"], os.path.basename(inner), r))
    s.gate("T%s.1 replace: no error, new uid" % tag, not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(dst); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("T%s.2 callee diff == exactly the inner swap" % tag, set(dd) == {w["get_buff_uid"], nu} and os.path.normcase(str(c1[nu])) == os.path.normcase(inner), dd, fatal=True)
    E1 = L.edges(live(dst), {nu: w["get_buff_uid"]})
    s.gate("T%s.3 wire-edge diff 0 after remap (%d edges)" % (tag, len(E0)), E0 == E1, (sorted(E0 - E1), sorted(E1 - E0)), fatal=True)
    s.gate("T%s.4 ExecState 1" % tag, s.es("test %s" % tag, dst) == 1, fatal=True)
    g.save(dst); g.reset()                                                                 # noqa: E702
    m = K.md5(dst); s.fact("SAVED %s md5 %s" % (dst, m))                                   # noqa: E702
    return {"path": dst, "md5": m, "inner": inner, "new_uid": nu}


# ---------------------------------------------------------------------------------------------------------------- [H]
def build_harness(s, tag, logger, test):
    H = HARN[tag]
    s.head("[H %s] %s" % (tag, os.path.basename(H)))
    shutil.copyfile(EMPTY, H)
    s.gate("H%s.0 copy md5 == EMPTY_v0" % tag, K.md5(H) == EMPTY_MD5, fatal=True)
    g.ensure_loaded(H)
    s0 = g.uids(H, "SubVI")
    g.drop_subvi(H, logger["path"], 0, (100, 500))
    u = sorted(g.uids(H, "SubVI") - s0)[0]
    wt = L.walk(H, 0)
    new, lab = g.create_control(H, wt[u][0], L.term(wt[u][2], "1D data", False)["i"])
    s.fact("H%s array control %r %r (from the logger's 1D data input)" % (tag, lab, new))
    g.delete_object(H, "Wire", L.fidx(H, "Wire", L.pwire(H, lab)), verify=False)
    g.delete_object(H, "SubVI", L.fidx(H, "SubVI", u), verify=True)
    g.remove_bad_wires_scripted(H)
    s.gate("H%s.1 a free I64[] control %r, no subVI left" % (tag, lab), L.pwire(H, lab) == 0 and not g.uids(H, "SubVI"), fatal=True)
    f0, k0 = g.uids(H, "ForLoop"), g.uids(H, "SubVI")
    try:
        g.loop_kernel(H, (300, 100), [lab], test["path"], ["Buffer to extract"], parallel=0)
    except RuntimeError as e:
        # run 1 (11:41): "expected 1 new wires, got 2" - the wire into the loop is two Wire objects (control -> tunnel -> kernel);
        # the loop and the kernel were made. Verified here instead: one new loop, one new kernel inside it, the edge below.
        s.fact("H%s loop_kernel raised %r - checked by H%s.1b/c instead" % (tag, str(e)[:160], tag))
        if "new wires, got 2" not in str(e):
            raise
    nf, nk = sorted(g.uids(H, "ForLoop") - f0), sorted(g.uids(H, "SubVI") - k0)
    s.gate("H%s.1b one new For loop, one new kernel node" % tag, len(nf) == 1 and len(nk) == 1, (nf, nk), fatal=True)
    ku = nk[0]
    own = owner_of(H, ku)
    s.fact("H%s kernel #%d owner %r" % (tag, ku, own))
    El = L.edges(live(H), {}); Ol = LB.own_map(live(H))
    tin = [e for e in El if e[2] == ku and e[3] == "Buffer to extract"]
    s.gate("H%s.1c the kernel's Buffer to extract <- a loop tunnel <- the I64[] control (nothing else wired)" % tag,
           len(tin) == 1 and "Tunnel" in str(Ol.get(tin[0][0])) and any(e[2] == tin[0][0] and e[1] == lab for e in El)
           and len([e for e in El if e[2] == ku]) == 1 and own[0] == "Diagram", (tin, own), fatal=True)
    t0 = set(g.uids(H, "LoopTunnel"))
    g.exit_loop(H, L.fidx(H, "SubVI", ku), ["current image number", "Missed frames?", "error out"], L.diag_index(H, own[1]))
    tn = sorted(set(g.uids(H, "LoopTunnel")) - t0)
    s.gate("H%s.2 three output tunnels" % tag, len(tn) == 3, tn, fatal=True)
    Ek = L.edges(live(H), {})
    by_name = {}
    for n in ("current image number", "Missed frames?", "error out"):
        h = [e[2] for e in Ek if e[0] == ku and e[1] == n and e[2] in tn]
        s.gate("H%s.2b kernel `%s` -> exactly one new tunnel" % (tag, n), len(h) == 1, h, fatal=True)
        by_name[n] = h[0]
    labs = {}
    for n, tu in by_name.items():
        b0 = set(l for _i, l, ind in g.fp_labels(H) if ind)
        ix = L.fidx(H, "LoopTunnel", tu)
        g.set_index_mode(H, ix, 1)
        g.tunnel_indicator(H, ix)
        nl = sorted(set(l for _i, l, ind in g.fp_labels(H) if ind) - b0)
        s.gate("H%s.3 one new indicator on the `%s` tunnel #%d: %r" % (tag, n, tu, nl), len(nl) == 1, nl, fatal=True)
        labs[n] = nl[0]
    lab_cin, lab_mf, lab_err = [labs["current image number"]], [labs["Missed frames?"]], [labs["error out"]]
    par = g.loop_par_set(H, 0, False); s.fact("H%s loop_par_set %r" % (tag, par))         # noqa: E702
    lc = g.loop_cast(H, 0, "ForLoop"); s.fact("H%s loop_cast %r" % (tag, lc))            # noqa: E702
    s.gate("H%s.4 For loop parallelism OFF (read back)" % tag, par["parallel_enabled"] is False and not par["err"]
           and lc.get("parallel_enabled") is False, (par, lc), fatal=True)
    s.safe("set_auto_error_handling(H, False)", lambda: g.set_auto_error_handling(H, False))
    c = L.census(H)
    s.gate("H%s.5 census == {the kernel: the test wrapper}" % tag, c == {ku: c.get(ku)} and os.path.normcase(str(c[ku])) == os.path.normcase(test["path"]), c, fatal=True)
    s.gate("H%s.6 ExecState 1" % tag, s.es("harness %s" % tag, H) == 1, fatal=True)
    g.save(H)
    m = K.md5(H); s.fact("SAVED %s md5 %s" % (H, m))                                       # noqa: E702
    return {"path": H, "md5": m, "array": lab, "cin": lab_cin[0], "mf": lab_mf[0], "err": lab_err[0], "kernel": ku}


def inner_ref(s, tag):
    inner = INNER[tag][0]
    out = []
    with g.vi_ref(inner) as vi:
        for b in VEC:
            vi.SetControlValue("Buffer to extract", b); g._run(vi)                        # noqa: E702
            out.append((int(vi.GetControlValue("current image number")), bool(vi.GetControlValue("Missed frames?"))))
    s.fact("REF %s direct calls of %s with %r -> %r" % (tag, os.path.basename(inner), VEC, out))
    return out


def run_harness(s, tag, h, ref, run_tag, want_lines):
    n0 = nrows(OBSLOG)
    with g.vi_ref(h["path"]) as vi:
        vi.SetControlValue(h["array"], VEC); g._run(vi)                                   # noqa: E702
        cin = [int(x) for x in vi.GetControlValue(h["cin"])]
        mf = [bool(x) for x in vi.GetControlValue(h["mf"])]
        er = [tuple(e)[:2] for e in vi.GetControlValue(h["err"])]
    n1 = nrows(OBSLOG); line = last_line(OBSLOG) if n1 > n0 else None
    want_r = VEC[0] + (1 if tag == "gap" else 0)
    rec = {"run": run_tag, "cin": cin, "missed": mf, "err": [list(map(str, e)) for e in er], "lines_added": n1 - n0, "line": line}
    s.fact("RUN %s %s %r" % (tag, run_tag, rec))
    s.gate("U %s %s outputs == the inner VI's own outputs for %r" % (tag, run_tag, VEC), list(zip(cin, mf)) == ref, (cin, mf, ref))
    s.gate("U %s %s exactly %d log line(s) for 3 calls of one clone (added %d)" % (tag, run_tag, want_lines, n1 - n0), n1 - n0 == want_lines, n1 - n0)
    if want_lines:
        s.gate("U %s %s the line = [requested %d, returned %d, tick]" % (tag, run_tag, VEC[0], want_r), line is not None and len(line) == 3
               and line[:2] == [VEC[0], want_r], line)
    return rec


# ---------------------------------------------------------------------------------------------------------------- [B]
def build_bobs(s, w, gbp):
    s.head("[B] %s" % os.path.basename(BOBS))
    shutil.copyfile(FIX, BOBS)
    s.gate("B0 copy md5 == 15c664e3", K.md5(BOBS) == FIX_MD5, fatal=True)
    g.ensure_loaded(BOBS)
    s.gate("B1 ExecState 1 before", s.es("bobs before", BOBS) == 1, fatal=True)
    c0 = L.census(BOBS); E0 = L.edges(live(BOBS), {})
    s.gate("B2 #%d -> RingPickSlot_latest, #%d -> get buff" % (PICK_CALL, GB_CALL),
           os.path.normcase(str(c0.get(PICK_CALL))) == os.path.normcase(RPSL) and os.path.normcase(str(c0.get(GB_CALL))) == os.path.normcase(gbp),
           (c0.get(PICK_CALL), c0.get(GB_CALL)), fatal=True)
    r1 = g.replace_object(BOBS, PICK_CALL, OBS); s.fact("replace #%d -> %s: %r" % (PICK_CALL, os.path.basename(OBS), r1))
    s.gate("B3 replace #%d: no error, new uid" % PICK_CALL, not (r1["err"] or r1["err_replace"] or r1["err_uid"]) and r1["new_uid"] > 0, r1, fatal=True)
    r2 = g.replace_object(BOBS, GB_CALL, w["path"]); s.fact("replace #%d -> %s: %r" % (GB_CALL, os.path.basename(w["path"]), r2))
    s.gate("B4 replace #%d: no error, new uid" % GB_CALL, not (r2["err"] or r2["err_replace"] or r2["err_uid"]) and r2["new_uid"] > 0, r2, fatal=True)
    n1, n2 = r1["new_uid"], r2["new_uid"]
    c1 = L.census(BOBS); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("B5 callee diff == exactly {#%d -> observer, #%d -> wrapper}" % (PICK_CALL, GB_CALL),
           set(dd) == {PICK_CALL, GB_CALL, n1, n2} and os.path.normcase(str(c1[n1])) == os.path.normcase(OBS)
           and os.path.normcase(str(c1[n2])) == os.path.normcase(w["path"]), dd, fatal=True)
    sites = sorted(u for u, p in c1.items() if os.path.normcase(str(p)) == os.path.normcase(w["path"]))
    obs_sites = sorted(u for u, p in c1.items() if os.path.normcase(str(p)) == os.path.normcase(OBS))
    gb_left = sorted(u for u, p in c1.items() if os.path.basename(str(p)).lower() == "get buff image-lost frames.vi")
    s.gate("B6 the wrapper at exactly ONE call site (#%d); the observer at one; no direct get-buff call left" % n2,
           sites == [n2] and obs_sites == [n1] and not gb_left, (sites, obs_sites, gb_left), fatal=True)
    E1 = L.edges(live(BOBS), {n1: PICK_CALL, n2: GB_CALL})
    s.gate("B7 wire-edge diff 0 after remap (%d edges)" % len(E0), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]), fatal=True)
    s.gate("B8 ExecState 1 after", s.es("bobs after", BOBS) == 1, fatal=True)
    g.save(BOBS); g.reset()                                                                # noqa: E702
    m = K.md5(BOBS); s.fact("SAVED %s md5 %s" % (BOBS, m))                                 # noqa: E702
    return {"path": BOBS, "md5": m, "new_pick_uid": n1, "new_gb_uid": n2, "edges": len(E0),
            "callee_diff": dict((str(k), v) for k, v in dd.items())}


def body(s):
    s.start(); R = s.R
    os.makedirs(OUT, exist_ok=True)
    s.gate("A0 the wrapper log file does not exist yet", not os.path.exists(OBSLOG), OBSLOG, fatal=True)
    Es, cs, gbp = source_read(s); s.dump()                                                 # noqa: E702
    s.restart()
    R["logger"] = lg = build_logger(s); s.dump()                                          # noqa: E702
    s.restart()
    g.ensure_loaded(s.work)
    R["wrapper"] = w = build_wrapper(s, gbp, lg); s.dump()                                # noqa: E702
    R["tests"], R["harness"], R["runs"] = {}, {}, {}
    for tag in ("paced", "gap"):
        s.restart()
        R["tests"][tag] = build_test(s, tag, w); s.dump()                                 # noqa: E702
        s.restart()
        R["harness"][tag] = h = build_harness(s, tag, lg, R["tests"][tag]); s.dump()       # noqa: E702
        ref = inner_ref(s, tag)
        # the latch is per LOAD of the clone (not per run): warm run 1 logs once, warm run 2 in the same LabVIEW logs nothing
        R["runs"][tag] = [run_harness(s, tag, h, ref, "warm1", 1), run_harness(s, tag, h, ref, "warm2", 0)]
        g.reset()
        s.gate("U %s harness md5 unchanged by the runs" % tag, K.md5(h["path"]) == h["md5"])
        s.dump()
    s.restart()
    R["bobs"] = b = build_bobs(s, w, gbp); s.dump()                                       # noqa: E702
    # ---- cold
    for tag in ("paced", "gap"):
        s.restart()
        s.head("[C] COLD harness %s" % tag)
        h = R["harness"][tag]
        s.gate("C1 %s harness ExecState 1 COLD" % tag, g.exec_state(h["path"]) == 1)
        ref = inner_ref(s, tag)
        R["runs"][tag].append(run_harness(s, tag, h, ref, "cold", 1))
        g.reset()
        s.gate("C1b %s harness / test md5 unchanged" % tag, K.md5(h["path"]) == h["md5"] and K.md5(R["tests"][tag]["path"]) == R["tests"][tag]["md5"])
        s.dump()
    s.restart()
    s.head("[C] COLD wrapper")
    s.gate("C2 wrapper ExecState 1 COLD", g.exec_state(w["path"]) == 1)
    pane = L.pane_dirs(w["path"]); R["wrapper"]["pane_cold"] = pane                       # noqa: E702
    s.gate("C3 wrapper pane COLD == get buff's (slot -> label, direction)", pane == GB_PANE, pane)
    pc = props(w["path"])
    s.gate("C4 wrapper execution properties COLD == get buff's", pc == w["props"], (pc, w["props"]))
    cw = L.census(w["path"])
    s.gate("C5 wrapper census COLD == {get buff, logger}", sorted(os.path.normcase(str(p)) for p in cw.values())
           == sorted([os.path.normcase(gbp), os.path.normcase(lg["path"])]), cw)
    g.reset()
    s.gate("C6 wrapper / logger md5 unchanged", K.md5(w["path"]) == w["md5"] and K.md5(lg["path"]) == lg["md5"])
    s.restart()
    s.head("[C] COLD %s" % os.path.basename(BOBS))
    g.ensure_loaded(BOBS)
    s.gate("C7 BOBS90 ExecState 1 COLD", g.exec_state(BOBS) == 1)
    Ec = L.edges(live(BOBS), {b["new_pick_uid"]: PICK_CALL, b["new_gb_uid"]: GB_CALL})
    s.gate("C8 BOBS90 COLD edges (remapped) == 15c664e3 cold edges (%d)" % len(Es), Ec == Es, (sorted(Ec - Es)[:6], sorted(Es - Ec)[:6]))
    c = L.census(BOBS)
    s.gate("C9 BOBS90 COLD: #%d -> observer, #%d -> wrapper, the wrapper once" % (b["new_pick_uid"], b["new_gb_uid"]),
           os.path.normcase(str(c.get(b["new_pick_uid"]))) == os.path.normcase(OBS) and os.path.normcase(str(c.get(b["new_gb_uid"]))) == os.path.normcase(w["path"])
           and sum(1 for p in c.values() if os.path.normcase(str(p)) == os.path.normcase(w["path"])) == 1, (c.get(b["new_pick_uid"]), c.get(b["new_gb_uid"])))
    dd = dict((u, (cs.get(u), c.get(u))) for u in set(cs) | set(c) if cs.get(u) != c.get(u))
    s.gate("C10 BOBS90 COLD callee diff vs 15c664e3 == exactly the 2 swaps (4 rows)", set(dd) == {PICK_CALL, GB_CALL, b["new_pick_uid"], b["new_gb_uid"]}, dd)
    g.reset()
    s.gate("C11 BOBS90 md5 unchanged by the cold load", K.md5(BOBS) == b["md5"])
    s.gate("C12 15c664e3 md5 unchanged", K.md5(FIX) == FIX_MD5)
    s.gate("C13 the log file holds exactly the 4 test lines (2 harnesses x warm1 + cold; warm2 none)", nrows(OBSLOG) == 4, nrows(OBSLOG))
    ft = os.path.join(OUT, "getbuff_first_functest_%s.txt" % TS)
    os.replace(OBSLOG, ft)
    s.gate("C14 test lines moved to %s; the wrapper log path is empty for the leg" % os.path.basename(ft), os.path.exists(ft) and not os.path.exists(OBSLOG))
    R["functest_log"] = ft
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + (("get buff copy", GB, GB_MD5), ("get buff orig", L.GB_ORIG, GB_MD5), ("final VI", FIX, FIX_MD5),
                                        ("RingPickSlot_latest", RPSL, RPSL_MD5), ("observer", OBS, OBS_MD5), ("PickLog", PLOG, PLOG_MD5),
                                        ("paced get-buff", PACED, PACED_MD5), ("gap wrapper", GAPW, GAPW_MD5), ("EMPTY_v0", EMPTY, EMPTY_MD5),
                                        ("P6 bed", BED, BED_MD5))
    st = St(GB, GB_MD5, "p64p1_build", preload=False, deadline_min=73, work_dir=LEAN, work_name=os.path.basename(WRAP), pins=pins,
            task="lean-p64p1", out_json=os.path.join(HERE, "p64p1_build.json"))
    sys.exit(K.run(body, st))
