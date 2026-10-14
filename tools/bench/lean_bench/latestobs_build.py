r"""latestobs_build - lean task latest RETRY 1: the per-pick observer. ALL saves under claudeDev\bench\lean (nothing else is saved).
Design: lean_report_latest.md s2. Nothing is edited inside a big P6 VI (user note 2026-10-13): the W100 copy's ONE RingPickSlot_latest
call #31367 is swapped (replace_object) for the observer, a byte copy of RingPickSlot_latest_20261014_010104.vi with, inside it only:
  Tick Count + Build Array (Num ++ [last, max value, max index, tick]) on the top level, a Case on `found` (#198 x < y?) and, in its
  True frame only, the logger PickLog (Write Delimited Spreadsheet (I64), path / append = panel defaults) fed by the Build Array.
  [G] PickLog_latestobs_<ts>.vi = byte copy of EMPTY_v0 + the writer + controls/indicator + pane {11: 1D data} + defaults.
  [S] observer edits + gates (ES, pane, edge diff = exactly +7 planned, nothing removed), vectors + log lines warm.
  [P] test copy = byte copy of fail1's W100 copy 04e54006 + swap #31367 -> [S]; callee diff, edge diff 0 after remap, ES 1.
  [C] cold: [S] ES, pane, vectors + log lines again; [P] ES 1, cold edges == source's cold edges, md5 kept; loaded-VI list.
    py tools/bgrun.py --material --max-min 60 --log tools/bench/lean_bench/latestobs_build.log -- py -u tools/bench/lean_bench/latestobs_build.py"""
import json, os, shutil, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import diag_replay_lib as L                                                              # noqa: E402
import latest_build as LB                                                                # noqa: E402 (constants + helpers only)
K, g = L.K, L.g
LEAN = LB.LEAN
RPSL, RPSL_MD5 = os.path.join(LEAN, "RingPickSlot_latest_20261014_010104.vi"), "8fc2ec267b3919402124f23a40f9ffae"
W100, W100_MD5 = os.path.join(LEAN, "D1_ring_p6latest_replay_w100_20261014_010104.vi"), "04e5400646af36b7afc3876d6fe3b6a7"
FAIL1 = {"replay": ("D1_ring_p6latest_replay_20261014_010104.vi", "d615e096075c74c5ac0c63c05a722217"),
         "gap": ("D1_ring_p6latest_replay_gap_20261014_010104.vi", "f656620329ffaf8c675fe050192ff9d3"),
         "w40": ("D1_ring_p6latest_replay_w40_20261014_010104.vi", "0eb42f736d6874e1af58781c82e81e37"),
         "fix": ("D1_ring_p6latest_20261014_010104.vi", "15c664e3eed1c580e05b13e42c86566f")}
EMPTY = os.path.join(K.CLAUDEDEV, "EMPTY_v0.vi")
WDS = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\file.llb\Write Delimited Spreadsheet (I64).vi"
CALL = 31367
TOP = 3                                                    # the subVI's top-level diagram uid (fail1 build log line 59)
AMM, LT = 117, 198
DON_TICK, DON_BA = 10972, 23365                            # bed graph: Tick Count, Build Array (array + 4 elements)
OUT2 = os.path.join(HERE, "out_latest2")
LOG = os.path.join(OUT2, "picklog_w100.txt")
TS = time.strftime("%Y%m%d_%H%M%S")
LOGGER = os.path.join(LEAN, "PickLog_latestobs_%s.vi" % TS)
OBS = os.path.join(LEAN, "RingPickSlot_latestobs_%s.vi" % TS)
DST = os.path.join(LEAN, "D1_ring_p6latestobs_replay_w100_%s.vi" % TS)
BDON = os.path.join(LEAN, "scratch_latestobs_bdon_%s.vi" % TS)
BG = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE)))))), "background VIs")
VEC, ref, PANE = LB.VEC, LB.ref, LB.PANE


def live(p):
    return LB.live(p)


def nrows(p):
    return sum(1 for ln in open(p, encoding="utf-8", errors="replace") if ln.strip()) if os.path.isfile(p) else 0


def last_line(p):
    ls = [ln for ln in open(p, encoding="utf-8", errors="replace") if ln.strip()]
    return [int(round(float(x))) for x in ls[-1].strip().split("\t")] if ls else None


def build_logger(s):
    s.head("[G] logger %s" % os.path.basename(LOGGER))
    shutil.copyfile(EMPTY, LOGGER)
    s.fact("EMPTY_v0 md5 %s; logger copy md5 %s" % (K.md5(EMPTY), K.md5(LOGGER)))
    s.gate("G0 logger copy md5 == EMPTY_v0's", K.md5(LOGGER) == K.md5(EMPTY), fatal=True)
    g.ensure_loaded(LOGGER)
    s0 = g.uids(LOGGER, "SubVI")
    g.drop_subvi(LOGGER, WDS, 0, (200, 120))
    new = sorted(g.uids(LOGGER, "SubVI") - s0)
    s.gate("G1 one writer dropped", len(new) == 1, new, fatal=True)
    W = new[0]
    ni = g._node_index(LOGGER, 0, W)
    nu, rs = g.node_terms_uid(LOGGER, 0, ni)
    s.fact("writer #%s terminals %r" % (W, [(r["i"], r["name"], r["is_source"]) for r in rs]))
    pick = lambda pref, src: [r for r in rs if str(r["name"]).startswith(pref) and bool(r["is_source"]) == src]   # noqa: E731
    want = {"path": pick("file path", False), "data": pick("1D data", False), "append": pick("append", False), "err": pick("error out", True)}
    s.gate("G2 writer has one file path / 1D data / append / error out terminal", all(len(v) == 1 for v in want.values()),
           dict((k, [(r["i"], r["name"]) for r in v]) for k, v in want.items()), fatal=True)
    labels = {}
    for k in ("path", "data", "append"):
        ni = g._node_index(LOGGER, 0, W)
        new_ct, lab = g.create_control(LOGGER, ni, int(want[k][0]["i"]))
        s.fact("CONTROL %s -> %r %r" % (k, lab, new_ct))
        s.gate("G3 control on %s created" % k, len(new_ct) == 1 and lab, (new_ct, lab), fatal=True)
        labels[k] = lab
    ni = g._node_index(LOGGER, 0, W)
    ind = g.create_indicator(LOGGER, ni, int(want["err"][0]["i"]))
    s.fact("INDICATOR error out -> %r" % (ind,))
    s.gate("G4 error out indicator created", bool(ind), ind, fatal=True)
    s.gate("G5 logger ExecState 1", s.es("logger", LOGGER) == 1, fatal=True)
    pane = g.conpane_assign(LOGGER, labels["data"], 11)
    s.fact("logger pane %r" % pane)
    s.gate("G6 logger pane: only terminal 11 = the 1D data control", [k for k, v in pane.items() if v] == [11] and pane[11] == labels["data"], pane, fatal=True)
    g.make_default(LOGGER, {labels["path"]: LOG, labels["append"]: True})
    s.gate("G7 logger ExecState 1 after defaults + save", s.es("logger saved", LOGGER) == 1, fatal=True)
    m = K.md5(LOGGER); s.fact("SAVED %s md5 %s" % (LOGGER, m))                            # noqa: E702
    g.reset()
    return {"path": LOGGER, "md5": m, "writer_uid": W, "labels": labels, "pane": pane}


def run_vectors(s, tag, path):
    out = []
    with g.vi_ref(path) as vi:
        for k, (num, last) in enumerate(VEC):
            n0 = nrows(LOG)
            vi.SetControlValue("Num", num); vi.SetControlValue("last", last); g._run(vi)       # noqa: E702
            got = [vi.GetControlValue("min Num"), vi.GetControlValue("min slot"), vi.GetControlValue("found")]
            want = ref(num, last)
            n1 = nrows(LOG)
            line = last_line(LOG) if n1 > n0 else None
            ok_out = [int(got[0]), int(got[1]), bool(got[2])] == want
            ok_log = (n1 - n0 == 1 and line is not None and len(line) == 24 and line[:20] == list(num) and line[20:23] == [last, want[0], want[1]]) \
                if want[2] else (n1 == n0)
            out.append({"k": k + 1, "last": last, "want": want, "got": [int(got[0]), int(got[1]), bool(got[2])], "lines_added": n1 - n0, "line": line})
            s.gate("%s vector %d last=%s -> %s (got %s)" % (tag, k + 1, last, want, got), ok_out)
            s.gate("%s vector %d log: %s (added %d, line %s)" % (tag, k + 1, "1 line = Num + [last, picked Num, slot] + tick" if want[2] else "no line",
                                                                n1 - n0, line), ok_log)
    return out


def obs_edit(s, logger):
    t = s.work
    s.head("[S] observer %s" % os.path.basename(t))
    s.gate("S0 work copy md5 == RingPickSlot_latest 8fc2ec26", K.md5(t) == RPSL_MD5, fatal=True)
    s.gate("S1 ExecState 1 before", s.es("obs before", t) == 1, fatal=True)
    s.gate("S1b pane before == fail1's", g.conpane(t) == PANE, fatal=True)
    lv0 = live(t); E0 = L.edges(lv0, {}); O0 = set(LB.own_map(lv0))
    s.fact("obs BEFORE edges %r" % sorted(E0))
    tid = g._uid_index(t, "Diagram", TOP)
    s.gate("S2 top-level diagram #%d is Diagram[%d]" % (TOP, tid), tid == 0, tid, fatal=True)
    shutil.copyfile(LB.BED, BDON); s.scratches.append(BDON)                              # noqa: E702
    s.gate("S3 donor = byte copy of the P6 bed", K.md5(BDON) == LB.BED_MD5, fatal=True)
    TC = g.create_primitive_nested(t, TOP, "TickCount", (60, 420), donor={"donor": BDON, "uid": DON_TICK})
    BA = g.create_primitive_nested(t, TOP, "BuildArray", (260, 420), donor={"donor": BDON, "uid": DON_BA})
    s.fact("new Tick Count #%s, Build Array #%s" % (TC, BA))
    echo, rs = g.node_terms_uids(t, 0, g._node_index(t, 0, BA))
    s.fact("BA #%s terminals %r" % (echo, [(r["i"], r["name"], r["is_source"], r["wire"], r["uid"]) for r in rs]))
    s.gate("S4a BA node echo", echo == BA, echo, fatal=True)
    els = sorted([r for r in rs if str(r["name"]) == "element" and not r["is_source"]], key=lambda r: int(r["i"]))
    arr = [r for r in rs if str(r["name"]) == "array" and not r["is_source"]]
    bout = [r for r in rs if str(r["name"]).startswith("appended") and r["is_source"]]
    s.gate("S4 BA = 1 array + 4 element inputs + 1 appended array output, all unwired", len(els) == 4 and len(arr) == 1 and len(bout) == 1
           and not any(int(r["wire"] or 0) for r in rs), fatal=True)
    lv = live(t)
    src = {"Num": LB.trow(lv, TOP, "Num", True), "last": LB.trow(lv, TOP, "last", True),
           "maxv": LB.trow(lv, AMM, "max value", True), "maxi": LB.trow(lv, AMM, "max index (indices)", True),
           "tick": LB.trow(lv, TC, "millisecond timer value", True)}
    snk = {"Num": arr[0], "last": els[0], "maxv": els[1], "maxi": els[2], "tick": els[3]}
    con = {}
    for k in ("Num", "last", "maxv", "maxi", "tick"):
        r = g.connect_term_uid(t, int(snk[k]["uid"]), int(src[k]["term_uid"]))
        con[k] = r; s.fact("CONNECT BA.%s(i%s) <- %s: %r" % (snk[k]["name"], snk[k]["i"], k, r))   # noqa: E702
        s.gate("S5 wire BA <- %s: err '' and not broken" % k, not r.get("err") and r.get("broken") is False, r, fatal=True)
    s.gate("S6 ExecState 1 after the Build Array", s.es("obs after BA", t) == 1, fatal=True)
    cw = g.case_wired(t, TOP, LT, "x < y?", pos=(560, 360))
    s.fact("CASE %r" % dict((k, v) for k, v in cw.items() if k not in ("terms_before", "terms_after")))
    names = [n.strip() for n in cw["names"]]
    s.gate("S7 case frames {False, True}", sorted(names) == ["False", "True"], names, fatal=True)
    tf = cw["frames"][names.index("True")]
    s0 = g.uids(t, "SubVI")
    g.drop_subvi(t, logger["path"], g._uid_index(t, "Diagram", tf), (40, 40))
    new = sorted(g.uids(t, "SubVI") - s0)
    s.gate("S8 one logger node dropped", len(new) == 1, new, fatal=True)
    LG = new[0]
    c = L.census(t)
    s.gate("S8b the new node calls the logger", os.path.normcase(str(c.get(LG))) == os.path.normcase(logger["path"]), c.get(LG), fatal=True)
    lv = live(t)
    lrow = [r for r in lv["terminals"] if int(r["owner_uid"]) == LG]
    s.fact("logger node #%s terminals %r" % (LG, [(r["term_uid"], r["term_name"], r["is_source"], r.get("frame_diagram")) for r in lrow]))
    ld = LB.trow(lv, LG, logger["labels"]["data"], False)
    bo = LB.trow(lv, BA, bout[0]["name"], True)
    r = g.connect_term_uid(t, int(ld["term_uid"]), int(bo["term_uid"]))
    con["row"] = r; s.fact("CONNECT logger.%s <- BA.%s: %r" % (logger["labels"]["data"], bout[0]["name"], r))   # noqa: E702
    s.gate("S9 wire logger <- BA (into the True frame): err '' and not broken", not r.get("err") and r.get("broken") is False, r, fatal=True)
    lv1 = live(t); E1 = L.edges(lv1, {}); O1 = LB.own_map(lv1)
    newo = sorted(set(O1) - O0)
    tun = sorted(u for u in newo if "Tunnel" in str(O1[u]) and any(e[2] == u for e in E1) and any(e[0] == u for e in E1))
    Ec = LB.collapse(E1, tun)
    alltun = set(u for u, cl in list(LB.own_map(lv0).items()) + list(O1.items()) if "Tunnel" in str(cl))
    nm = lambda E: set((a, "*" if a in alltun else ta, b, "*" if b in alltun else tb) for a, ta, b, tb in E)   # noqa: E731
    removed, added = sorted(nm(E0) - nm(Ec)), sorted(nm(Ec) - nm(E0))
    s.fact("S10 new owners %r (classes %r); collapsed tunnels %r; removed %r; added %r" % (newo, [O1[u] for u in newo], tun, removed, added))
    plan_src = sorted([(TOP, "Num"), (TOP, "last"), (AMM, "max value"), (AMM, "max index (indices)"), (TC, "millisecond timer value"),
                       (LT, "x < y?"), (BA, bout[0]["name"])])
    s.gate("S10 edge diff: nothing removed; added == exactly 7 edges from the 7 planned sources, every sink a NEW owner",
           not removed and len(added) == 7 and sorted((a, ta) for a, ta, _b, _tb in added) == plan_src
           and all(b in set(newo) for _a, _ta, b, _tb in added), (removed, added), fatal=True)
    s.gate("S10b BA out -> logger 1D data and #198 -> a new owner (the selector) are among the added edges",
           (BA, bout[0]["name"], LG, logger["labels"]["data"]) in set(Ec) and any(a == LT and b in set(newo) for a, _ta, b, _tb in added), fatal=True)
    s.gate("S11 ExecState 1 after", s.es("obs after", t) == 1, fatal=True)
    s.gate("S12 pane after == fail1's", g.conpane(t) == PANE, fatal=True)
    s.gate("S13 no Constant on the observer", not g.uids(t, "Constant"), g.uids(t, "Constant"))
    g.save(t)
    m = K.md5(t); s.fact("SAVED %s md5 %s" % (t, m))                                       # noqa: E702
    vec = run_vectors(s, "V warm", t)
    s.gate("S14 md5 unchanged by the vector runs", K.md5(t) == m)
    g.reset()
    return {"path": t, "md5": m, "tick": TC, "build_array": BA, "case": cw["case"], "true_frame": tf, "logger_node": LG,
            "connects": con, "new_owners": newo, "added": added, "edges_before": len(E0), "edges_after": len(E1), "vectors_warm": vec}


def swap(s, obs):
    s.head("[P] %s" % os.path.basename(DST))
    shutil.copyfile(W100, DST)
    s.gate("P0 copy md5 == fail1 W100 04e54006", K.md5(DST) == W100_MD5, fatal=True)
    g.ensure_loaded(DST)
    s.gate("P1 ExecState 1 before", s.es("w100obs before", DST) == 1, fatal=True)
    c0 = L.census(DST); E0 = L.edges(live(DST), {})
    rp = [u for u, p in c0.items() if os.path.basename(str(p)).lower() == os.path.basename(RPSL).lower()]
    s.gate("P2 exactly one RingPickSlot_latest call, #%d" % CALL, rp == [CALL], rp, fatal=True)
    r = g.replace_object(DST, CALL, obs); s.fact("replace_object #%d -> %s: %r" % (CALL, os.path.basename(obs), r))   # noqa: E702
    s.gate("P3 replace: no error, new uid", not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(DST); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("P4 callee diff == exactly #%d -> %s" % (CALL, os.path.basename(obs)),
           set(dd) == {CALL, nu} and os.path.normcase(str(c1.get(nu))) == os.path.normcase(obs), dd, fatal=True)
    E1 = L.edges(live(DST), {nu: CALL})
    s.gate("P5 wire-edge diff 0 after remap (%d edges)" % len(E0), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]), fatal=True)
    s.gate("P6 ExecState 1 after", s.es("w100obs after", DST) == 1, fatal=True)
    g.save(DST); g.reset()                                                                 # noqa: E702
    m = K.md5(DST); s.fact("SAVED %s md5 %s" % (DST, m))                                   # noqa: E702
    return {"path": DST, "md5": m, "src": W100, "src_md5": W100_MD5, "new_uid": nu, "callee_diff": dict((str(k), v) for k, v in dd.items()), "edges": len(E0)}


def loaded_list(s):
    """every VI in memory after the cold load of the test copy; the paths of those named like a file of `background VIs`"""
    names = [str(n) for n in (g.lv().ExportedVIs or ())]
    bgn = {}
    for dp, _dn, fs in os.walk(BG):
        for f in fs:
            bgn.setdefault(f.lower(), []).append(os.path.join(dp, f))
    hits = {}
    for n in names:
        if n.lower() in bgn:
            p = None
            try:
                r = g.lv().GetVIReference(n, "", False, 0)
                p = str(r.Path)
                del r
            except Exception as e:                                                         # noqa: BLE001
                p = "ERR %s" % str(e)[:80]
            hits[n] = p
    s.fact("COLD load: %d VIs in memory; %d named like a background VI: %r" % (len(names), len(hits), hits))
    return {"n_in_memory": len(names), "names": sorted(names), "background": hits}


def body(s):
    s.start(); R = s.R
    os.makedirs(OUT2, exist_ok=True)
    s.gate("A0 the pick log does not exist yet", not os.path.exists(LOG), LOG, fatal=True)
    s.gate("A1 fail1 W100 copy md5 == 04e54006", K.md5(W100) == W100_MD5, fatal=True)
    R["logger"] = lg = build_logger(s); s.dump()                                           # noqa: E702
    s.restart()
    g.ensure_loaded(s.work)
    R["obs"] = ob = obs_edit(s, lg); s.dump()                                              # noqa: E702
    s.restart()
    R["copy"] = cp = swap(s, ob["path"]); s.dump()                                         # noqa: E702
    s.restart()
    s.head("[C] COLD observer")
    s.gate("C1 observer ExecState 1 COLD", g.exec_state(ob["path"]) == 1)
    s.gate("C1b observer pane COLD == fail1's", g.conpane(ob["path"]) == PANE)
    ob["vectors_cold"] = run_vectors(s, "V cold", ob["path"])
    g.reset()
    s.gate("C2 observer md5 unchanged by the cold load + runs", K.md5(ob["path"]) == ob["md5"])
    s.gate("C2b logger md5 unchanged", K.md5(lg["path"]) == lg["md5"])
    s.restart()
    s.head("[C] COLD source (read-only) %s" % os.path.basename(W100))
    g.ensure_loaded(W100); Es = L.edges(live(W100), {}); g.reset()                         # noqa: E702
    s.restart()
    s.head("[C] COLD %s" % os.path.basename(DST))
    g.ensure_loaded(DST)
    s.gate("C3 test copy ExecState 1 COLD", g.exec_state(DST) == 1)
    Ec = L.edges(live(DST), {cp["new_uid"]: CALL})
    s.gate("C4 COLD edges (new uid -> #%d) == cold source edges (%d)" % (CALL, len(Es)), Ec == Es, (sorted(Ec - Es)[:6], sorted(Es - Ec)[:6]))
    c = L.census(DST)
    s.gate("C5 COLD call #%d -> %s" % (cp["new_uid"], os.path.basename(ob["path"])), os.path.normcase(str(c.get(cp["new_uid"]))) == os.path.normcase(ob["path"]), c.get(cp["new_uid"]))
    R["loaded"] = loaded_list(s)
    g.reset()
    s.gate("C6 test copy md5 unchanged by the cold load", K.md5(DST) == cp["md5"])
    s.gate("C7 source md5 unchanged", K.md5(W100) == W100_MD5)
    s.gate("C8 the pick log holds exactly the functional-test lines (7 found=True vectors x warm + cold = 14)", nrows(LOG) == 14, nrows(LOG))
    ft = os.path.join(OUT2, "picklog_functest_%s.txt" % TS)
    os.replace(LOG, ft)
    s.gate("C9 test lines moved to %s; the pick log path is empty for the leg" % os.path.basename(ft), os.path.exists(ft) and not os.path.exists(LOG))
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + (("P6 bed", LB.BED, LB.BED_MD5), ("RingPickSlot_latest", RPSL, RPSL_MD5), ("W100 fail1", W100, W100_MD5)) + \
        tuple(("fail1 " + k, os.path.join(LEAN, n), m) for k, (n, m) in FAIL1.items())
    st = St(RPSL, RPSL_MD5, "latestobs_build", preload=False, deadline_min=58, work_dir=LEAN, work_name=os.path.basename(OBS), pins=pins,
            task="lean-latest-retry", out_json=os.path.join(HERE, "latestobs_build.json"))
    sys.exit(K.run(body, st))
