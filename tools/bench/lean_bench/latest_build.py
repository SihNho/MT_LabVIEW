r"""latest_build - lean task latest (U8/U13 latest-wins): ALL saves under claudeDev\bench\lean (nothing else is saved).
Design: lean_report_latest.md s2. Nothing is edited inside a big P6 VI (user note 2026-10-13): the ONE RingPickSlot call #29719
of loop 1.2's pick loop is swapped (replace_object) for a byte copy of RingPickSlot_v0 whose pick rule is "largest Num > last".
  [S] the Stage's work copy = claudeDev\bench\lean\RingPickSlot_latest_<ts>.vi (byte copy of RingPickSlot_v0 6fcf153f):
      KMX1 (I32 max, Select f) and KMX2 (I32 max, Less? y) deleted; wires AMM.min value (-> min Num, LT.x) and AMM.min index
      (-> min slot) deleted; new wires: last -> SW.f, last -> LT.x, AMM.max value -> min Num + LT.y, AMM.max index -> min slot.
      Gates: ES 1, edge diff (new For tunnel collapsed) == exactly the planned one, no Constant left, pane unchanged, vectors.
  [P] D1_ring_p6latest_<ts>.vi = byte copy of the p6fix VI 3e847397 + swap #29719 -> [S]; the test copies the same way from
      the p6fix replay / gap / w40 / w100 copies. Gates per file: callee diff == exactly the swap, edge diff 0 after remap, ES 1.
  [C] cold: [S] ES 1, md5 kept, pane, vectors again; every P6 file ES 1, cold edges (remapped) == its source's cold edges, md5 kept.
    py tools/bgrun.py --material --max-min 70 --log tools/bench/lean_bench/latest_build.log -- py -u tools/bench/lean_bench/latest_build.py"""
import json, os, shutil, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
RPS, RPS_MD5 = os.path.join(K.CLAUDEDEV, "RingPickSlot_v0.vi"), "6fcf153f7b8fecda727f5dcf944faab9"
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_ring_p6_20261012_212645.vi"), "c2d9c13cb40c0a5cab7433896d1df157"
PFX = "20261013_231910"
SRC = {"fix": ("D1_ring_p6fix_%s.vi" % PFX, "3e847397eb120860adb2e868792345f7"),
       "replay": ("D1_ring_p6fix_replay_%s.vi" % PFX, "ae83d1aa088ba4546c65e039c6b4d16d"),
       "gap": ("D1_ring_p6fix_replay_gap_%s.vi" % PFX, "2c499c7ba1a38c813d784efe7eacee76"),
       "w40": ("D1_ring_p6fix_replay_w40_%s.vi" % PFX, "db5e2e958201df1f1de928558aeff3ac"),
       "w100": ("D1_ring_p6fix_replay_w100_%s.vi" % PFX, "ae8474bc8b33506c3659af407c2e7696")}
SRC = dict((k, (os.path.join(LEAN, n), m)) for k, (n, m) in SRC.items())
PICK_CALL, PICK_LOOP = 29719, 16483
TS = time.strftime("%Y%m%d_%H%M%S")
SUB = os.path.join(LEAN, "RingPickSlot_latest_%s.vi" % TS)
DST = {"fix": "D1_ring_p6latest_%s.vi", "replay": "D1_ring_p6latest_replay_%s.vi", "gap": "D1_ring_p6latest_replay_gap_%s.vi",
       "w40": "D1_ring_p6latest_replay_w40_%s.vi", "w100": "D1_ring_p6latest_replay_w100_%s.vi"}
DST = dict((k, os.path.join(LEAN, v % TS)) for k, v in DST.items())
PANE = {0: None, 1: "found", 2: "min slot", 3: "min Num", 4: None, 5: None, 6: None, 7: None, 8: None, 9: None, 10: "last", 11: "Num"}
R3, R5, I20 = [20, 21, 22] + list(range(3, 20)), [-1, 21, 22] + list(range(3, 20)), list(range(20))
VEC = [([-1] * 20, -1), (I20, 4), (R3, 5), (R3, 19), (R5, 20), (R5, 22), (I20, 19), (R3, 21), ([7] + [-1] * 19, -1),
       ([41, 42, 43, 44, -1] + list(range(25, 40)), 24)]


def ref(num, last):
    m = [n if n > last else last for n in num]
    v = max(m)
    return [v, m.index(v), last < v]


assert ref(R3, 5) == [22, 2, True] and ref([-1] * 20, -1) == [-1, 0, False] and ref(R5, 22) == [22, 0, False]
assert ref([41, 42, 43, 44, -1] + list(range(25, 40)), 24) == [44, 3, True]


def live(p):
    return WB.read_live(p, fs_pairs=[])


def own_map(lv):
    return dict((int(r["owner_uid"]), r["owner_class"]) for r in lv["terminals"])


def collapse(E, tunnels):
    E = set(E)
    for t in tunnels:
        ins = set(e for e in E if e[2] == t)
        outs = set(e for e in E if e[0] == t)
        E -= ins | outs
        E |= set((a[0], a[1], b[2], b[3]) for a in ins for b in outs)
    return E


def owner_with(lv, names):
    """the one owner uid whose terminal names include all of `names`"""
    by = {}
    for r in lv["terminals"]:
        by.setdefault(int(r["owner_uid"]), set()).add(r["term_name"])
    h = [u for u, ns in by.items() if set(names) <= ns]
    if len(h) != 1:
        raise RuntimeError("owner with %r: %r" % (names, h))
    return h[0]


def trow(lv, owner, name, src):
    h = [r for r in lv["terminals"] if int(r["owner_uid"]) == int(owner) and r["term_name"] == name and bool(r["is_source"]) == src]
    if len(h) != 1:
        raise RuntimeError("term #%s %r src=%s: %d matches" % (owner, name, src, len(h)))
    return h[0]


def run_vectors(s, tag, path):
    out = []
    with g.vi_ref(path) as vi:
        for k, (num, last) in enumerate(VEC):
            vi.SetControlValue("Num", num); vi.SetControlValue("last", last); g._run(vi)       # noqa: E702
            got = [vi.GetControlValue("min Num"), vi.GetControlValue("min slot"), vi.GetControlValue("found")]
            want = ref(num, last)
            ok = [int(got[0]), int(got[1]), bool(got[2])] == want
            out.append((k + 1, last, want, got))
            s.gate("%s vector %d last=%s -> %s (got %s)" % (tag, k + 1, last, want, got), ok)
    return out


def sub_edit(s):
    sub = s.work
    s.head("[S] %s" % os.path.basename(sub))
    s.gate("S0 work copy md5 == RingPickSlot_v0 6fcf153f", K.md5(sub) == RPS_MD5, fatal=True)
    s.gate("S1 ExecState 1 before", s.es("sub before", sub) == 1, fatal=True)
    s.gate("S1b pane before == v0's", g.conpane(sub) == PANE, fatal=True)
    lv0 = live(sub); E0 = L.edges(lv0, {}); O0 = set(own_map(lv0))
    s.fact("sub BEFORE edges %r" % sorted(E0))
    GT, SW = owner_with(lv0, ["x > y?"]), owner_with(lv0, ["s? t:f"])
    AMM, LT = owner_with(lv0, ["min value"]), owner_with(lv0, ["x < y?"])
    km1 = [e for e in E0 if e[2] == SW and e[3] == "f"]
    km2 = [e for e in E0 if e[2] == LT and e[3] == "y"]
    lst = [e for e in E0 if e[2] == GT and e[3] == "y"]
    s.gate("S2 one source each for SW.f (KMX1), LT.y (KMX2), GT.y (last)", len(km1) == len(km2) == len(lst) == 1, (km1, km2, lst), fatal=True)
    KMX1, KMX2, LAST = km1[0][0], km2[0][0], (lst[0][0], lst[0][1])
    oc = own_map(lv0)
    s.fact("nodes GT #%d SW #%d AMM #%d LT #%d KMX1 #%d (%s) KMX2 #%d (%s) last %r" % (GT, SW, AMM, LT, KMX1, oc[KMX1], KMX2, oc[KMX2], LAST))
    s.gate("S3 KMX1 / KMX2 are constants of value 2147483647",
           all((g.read_const_value(sub, u) or {}).get("value") == 2147483647 for u in (KMX1, KMX2)), fatal=True)
    amm_out = sorted(r["term_name"] for r in lv0["terminals"] if int(r["owner_uid"]) == AMM and r["is_source"])
    s.fact("AMM outputs %r" % amm_out)
    MAXV = [n for n in amm_out if n.startswith("max value")]
    MAXI = [n for n in amm_out if n.startswith("max index")]
    MINI = [n for n in amm_out if n.startswith("min index")]
    s.gate("S4 AMM has one max value / max index / min index terminal", len(MAXV) == len(MAXI) == len(MINI) == 1, amm_out, fatal=True)
    MAXV, MAXI, MINI = MAXV[0], MAXI[0], MINI[0]
    rem = set(e for e in E0 if e[0] in (KMX1, KMX2) or (e[0] == AMM and e[1] in ("min value", MINI)))
    ind_minnum = [e[2:] for e in rem if e[0] == AMM and e[1] == "min value" and e[2] != LT]
    ind_minslot = [e[2:] for e in rem if e[0] == AMM and e[1] == MINI]
    s.gate("S5 removed set = KMX1->SW.f, KMX2->LT.y, AMM.min value->{min Num, LT.x}, AMM.min index->min slot (5 edges)",
           len(rem) == 5 and len(ind_minnum) == 1 and len(ind_minslot) == 1 and (AMM, "min value", LT, "x") in rem, sorted(rem), fatal=True)
    add = {(LAST[0], LAST[1], SW, "f"), (LAST[0], LAST[1], LT, "x"), (AMM, MAXV, LT, "y"),
           (AMM, MAXV) + tuple(ind_minnum[0]), (AMM, MAXI) + tuple(ind_minslot[0])}
    s.R["sub_plan"] = {"GT": GT, "SW": SW, "AMM": AMM, "LT": LT, "KMX1": KMX1, "KMX2": KMX2, "last": LAST,
                       "rem": sorted(rem), "add": sorted(add)}
    # sink/source terminal uids BEFORE any delete (terminal uids of surviving nodes are kept by LabVIEW)
    t_swf, t_ltx, t_lty = trow(lv0, SW, "f", False), trow(lv0, LT, "x", False), trow(lv0, LT, "y", False)
    t_last = trow(lv0, LAST[0], LAST[1], True)
    t_maxv, t_maxi = trow(lv0, AMM, MAXV, True), trow(lv0, AMM, MAXI, True)
    t_mn = trow(lv0, ind_minnum[0][0], ind_minnum[0][1], False)
    t_ms = trow(lv0, ind_minslot[0][0], ind_minslot[0][1], False)
    w_minv, w_mini = int(trow(lv0, AMM, "min value", True)["wire_uid"]), int(trow(lv0, AMM, MINI, True)["wire_uid"])
    # deletes: the two AMM min wires, then the two constants (their wires go broken), then Remove Bad Wires
    for w in (w_minv, w_mini):
        order = [int(o["uid"]) for o in g.report_all(sub, "Wire")]
        g.delete_object(sub, "Wire", order.index(w), verify=False)
        s.gate("S6 wire w%d deleted" % w, w not in g.uids(sub, "Wire"), fatal=True)
    for u in (KMX1, KMX2):
        order = [int(o["uid"]) for o in g.report_all(sub, "Constant")]
        g.delete_object(sub, "Constant", order.index(u), verify=False)
        s.gate("S7 constant #%d deleted" % u, u not in g.uids(sub, "Constant"), fatal=True)
    s.fact("RBW %r" % (g.remove_bad_wires_scripted(sub),))
    s.gate("S8 no Constant left", not g.uids(sub, "Constant"), g.uids(sub, "Constant"), fatal=True)
    lvm = live(sub)                                       # terminals re-read by (owner, name) after the deletes; uid kept?
    tm = [trow(lvm, int(t["owner_uid"]), t["term_name"], bool(t["is_source"])) for t in (t_swf, t_ltx, t_lty, t_last, t_maxv, t_maxi, t_mn, t_ms)]
    s.fact("terminal uids before -> after deletes: %r" % [(t["term_uid"], u["term_uid"]) for t, u in zip((t_swf, t_ltx, t_lty, t_last, t_maxv, t_maxi, t_mn, t_ms), tm)])
    t_swf, t_ltx, t_lty, t_last, t_maxv, t_maxi, t_mn, t_ms = tm
    s.gate("S8b the 5 sinks are unwired, the AMM max outputs unwired", all(not t["wire_uid"] for t in (t_swf, t_ltx, t_lty, t_mn, t_ms, t_maxv, t_maxi)),
           [(t["term_name"], t["wire_uid"]) for t in tm], fatal=True)
    con = {}
    for tag, snk, src in (("SW.f <- last", t_swf, t_last), ("LT.x <- last", t_ltx, t_last), ("LT.y <- AMM.max value", t_lty, t_maxv),
                          ("min Num <- AMM.max value", t_mn, t_maxv), ("min slot <- AMM.max index", t_ms, t_maxi)):
        r = g.connect_term_uid(sub, int(snk["term_uid"]), int(src["term_uid"]))
        con[tag] = r; s.fact("CONNECT %s: %r" % (tag, r))                                 # noqa: E702
        s.gate("S9 wire %s: err '' and not broken" % tag, not r.get("err") and r.get("broken") is False, r, fatal=True)
    lv1 = live(sub); E1 = L.edges(lv1, {})
    nt = sorted(u for u, c in own_map(lv1).items() if u not in O0 and "Tunnel" in str(c))
    gone = sorted(O0 - set(own_map(lv1)))
    s.fact("sub AFTER: new tunnels %r, gone owners %r, edges %r" % (nt, gone, sorted(E1)))
    Ec = collapse(E1, nt)
    # run 1 (01:00): the For loop's OUTPUT tunnel #199 (Select out -> AMM.array) read its terminal name as '' before and 'last'
    # after (LabVIEW propagates the data name of the wire now feeding Select.f); same owners, same wire. So a TUNNEL's terminal
    # name is not part of the identity in this gate (owners still are); the rename is recorded as a fact.
    tun = set(u for u, c in list(own_map(lv0).items()) + list(own_map(lv1).items()) if "Tunnel" in str(c))
    nm = lambda E: set((a, "*" if a in tun else ta, b, "*" if b in tun else tb) for a, ta, b, tb in E)   # noqa: E731
    s.fact("S10 raw diff (tunnel names kept): -%r +%r" % (sorted(E0 - Ec - rem), sorted(Ec - E0 - add)))
    s.gate("S10 edge diff (new tunnels collapsed, tunnel terminal names ignored) == exactly -5 planned / +5 planned",
           nm(E0) - nm(Ec) == nm(rem) and nm(Ec) - nm(E0) == nm(add), (sorted(nm(E0) - nm(Ec)), sorted(nm(Ec) - nm(E0))), fatal=True)
    s.gate("S11 gone owners == {KMX1, KMX2}; at most one new tunnel (last into the For loop)", gone == sorted([KMX1, KMX2]) and len(nt) <= 1, (gone, nt), fatal=True)
    s.gate("S12 ExecState 1 after", s.es("sub after", sub) == 1, fatal=True)
    s.gate("S13 pane after == v0's", g.conpane(sub) == PANE, fatal=True)
    g.save(sub)
    m = K.md5(sub); s.fact("SAVED %s md5 %s" % (sub, m))
    vec = run_vectors(s, "V warm", sub)
    s.gate("S14 md5 unchanged by the vector runs", K.md5(sub) == m)
    g.reset()
    return {"path": sub, "md5": m, "connects": con, "new_tunnels": nt, "gone": gone, "edges_before": len(E0), "edges_after": len(E1),
            "vectors_warm": vec}


def swap(s, tag, src, src_md5, dst, sub):
    s.head("[P %s] %s" % (tag, os.path.basename(dst)))
    shutil.copyfile(src, dst)
    s.gate("%s.0 copy md5 == source %s" % (tag, src_md5[:8]), K.md5(dst) == src_md5, fatal=True)
    g.ensure_loaded(dst)
    s.gate("%s.1 ExecState 1 before" % tag, s.es("%s before" % tag, dst) == 1, fatal=True)
    c0 = L.census(dst); E0 = L.edges(live(dst), {})
    rp = [u for u, p in c0.items() if os.path.basename(str(p)).lower() == "ringpickslot_v0.vi"]
    s.gate("%s.2 exactly one RingPickSlot_v0 call, #%d" % (tag, PICK_CALL), rp == [PICK_CALL], rp, fatal=True)
    r = g.replace_object(dst, PICK_CALL, sub); s.fact("%s replace_object #%d -> %s: %r" % (tag, PICK_CALL, os.path.basename(sub), r))
    s.gate("%s.3 replace: no error, new uid" % tag, not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(dst); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("%s.4 callee diff == exactly #%d -> %s" % (tag, PICK_CALL, os.path.basename(sub)),
           set(dd) == {PICK_CALL, nu} and os.path.normcase(str(c1.get(nu))) == os.path.normcase(sub), dd, fatal=True)
    E1 = L.edges(live(dst), {nu: PICK_CALL})
    s.gate("%s.5 wire-edge diff 0 after remap (%d edges)" % (tag, len(E0)), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]), fatal=True)
    s.gate("%s.6 ExecState 1 after" % tag, s.es("%s after" % tag, dst) == 1, fatal=True)
    g.save(dst); g.reset()
    m = K.md5(dst); s.fact("SAVED %s md5 %s" % (dst, m))
    return {"path": dst, "md5": m, "src": src, "src_md5": src_md5, "new_uid": nu, "callee_diff": dict((str(k), v) for k, v in dd.items()),
            "edges": len(E0)}


def body(s):
    s.start(); R = s.R
    for k, (p, mm) in SRC.items():
        s.gate("P0 source %s md5 == %s" % (os.path.basename(p), mm[:8]), K.md5(p) == mm, fatal=True)
    R["sub"] = sub = sub_edit(s); s.dump()                                               # noqa: E702
    R["copies"] = {}
    for tag in ["fix", "replay", "gap", "w40", "w100"]:
        s.restart()
        R["copies"][tag] = swap(s, tag, SRC[tag][0], SRC[tag][1], DST[tag], sub["path"]); s.dump()   # noqa: E702
    # [C] cold
    s.restart()
    s.head("[C] COLD subVI")
    s.gate("C1 sub ExecState 1 COLD", g.exec_state(sub["path"]) == 1)
    s.gate("C1b sub pane COLD == v0's", g.conpane(sub["path"]) == PANE)
    R["sub"]["vectors_cold"] = run_vectors(s, "V cold", sub["path"])
    g.reset()
    s.gate("C2 sub md5 unchanged by the cold load + runs", K.md5(sub["path"]) == sub["md5"])
    for tag in ["fix", "replay", "gap", "w40", "w100"]:
        rec = R["copies"][tag]
        s.restart()
        s.head("[C] COLD %s source (read-only)" % tag)
        g.ensure_loaded(rec["src"]); Es = L.edges(live(rec["src"]), {}); g.reset()        # noqa: E702
        s.restart()
        s.head("[C] COLD %s" % tag)
        g.ensure_loaded(rec["path"])
        s.gate("C3 %s ExecState 1 COLD" % tag, g.exec_state(rec["path"]) == 1)
        lv = live(rec["path"])
        Ec = L.edges(lv, {rec["new_uid"]: PICK_CALL})
        s.gate("C4 %s COLD edges (new uid -> #%d) == cold source edges (%d)" % (tag, PICK_CALL, len(Es)), Ec == Es,
               (sorted(Ec - Es)[:6], sorted(Es - Ec)[:6]))
        c = L.census(rec["path"])
        s.gate("C5 %s COLD call #%d -> %s" % (tag, rec["new_uid"], os.path.basename(sub["path"])),
               os.path.normcase(str(c.get(rec["new_uid"]))) == os.path.normcase(sub["path"]), c.get(rec["new_uid"]))
        g.reset()
        s.gate("C6 %s md5 unchanged by the cold load" % tag, K.md5(rec["path"]) == rec["md5"])
        s.gate("C7 %s source md5 unchanged" % tag, K.md5(rec["src"]) == rec["src_md5"])
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + (("P6 bed", BED, BED_MD5),) + tuple(("p6fix " + k, p, m) for k, (p, m) in SRC.items())
    st = St(RPS, RPS_MD5, "latest_build", preload=False, deadline_min=68, work_dir=LEAN, work_name=os.path.basename(SUB), pins=pins,
            task="lean-latest", out_json=os.path.join(HERE, "latest_build.json"))
    sys.exit(K.run(body, st))
