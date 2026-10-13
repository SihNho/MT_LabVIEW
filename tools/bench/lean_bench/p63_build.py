r"""p63_build - lean task P6-3: the test copies, ALL saved under claudeDev\bench\lean (nothing else is saved).
Input = the P6 replay copy bench\lean\D1_ring_p6_replay_20261013_135743.vi (09a23608, read-only; byte copies only).
  [L] T-load (run 4 route, see ring_wait): two byte copies whose ONE RingSeqCheck_v0 call (loop 1.2) calls a byte copy of
      RingSeqCheck_v0 + ONE Wait (ms) (input = a panel control, default W; output unwired). Gates: subVI edges == before + the
      control->Wait edge, ES 1; the P6 copy: callee diff == that swap, edge diff 0 after remap, ES 1; saved.
      (Runs 1-3 put the Wait INTO the P6 copy: ExecState 0, nothing saved - add_wait, kept as the record.)
  [G1] gap wrapper: byte copy of replay\replay_get_buff_image_paced60.vi (59ec66b6) + ONE Increment (donor copy from the
      paced buf stand-in's own Increment) on the stand-in's `Buffer Number Out` wire: BN Out -> Inc.x, Inc.x+1 -> the old
      sinks (`current image number`, #76 `y`). Gates: edge set after == before - old 2 edges + the 3 new ones; ES 1; saved.
  [G2] gap P6 copy: byte copy of the input; replace_object #31533 (the P6-2 swap's get-buff call) -> the gap wrapper.
      Gates as stage_replay_swap A2-A6 (callee diff == exactly that swap, edge diff 0 after remap, ES 1); saved.
  [C] cold: each saved file ExecState 1 in a fresh LabVIEW, md5 unchanged by the load. LabVIEW killed, verified gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/lean_bench/p63_build.log -- py -u tools/bench/lean_bench/p63_build.py"""
import json, os, shutil, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
IN, IN_MD5 = os.path.join(LEAN, "D1_ring_p6_replay_20261013_135743.vi"), "09a23608c223a9a31ea6ca3638c1241c"
GBP, GBP_MD5 = os.path.join(L.RP, "replay_get_buff_image_paced60.vi"), "59ec66b61f3518b049a3c532a8e65482"
SBP, SBP_MD5 = os.path.join(L.RP, "replay_imaqdx_get_image_buf_paced60.vi"), "e40ec86722948812d155d6e4047a3ef9"
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_ring_p6_20261012_212645.vi"), "c2d9c13cb40c0a5cab7433896d1df157"
S1R, S1R_MD5 = os.path.join(L.RP, "D1_s1_replay_20260925_075422.vi"), "126f84975fca9f6124432a7e4decd0c8"
LOOP12, BODY12, TRACKER = 10170, 23166, 5058
GETBUFF_CALL = 31533                      # lean_report.md: plan swap #6810 -> new uid 31533 (#22692 -> 6829)
TS = time.strftime("%Y%m%d_%H%M%S")
W_HI, W_LO = 100, 40
P_W = {W_HI: os.path.join(LEAN, "D1_ring_p6_replay_w%d_%s.vi" % (W_HI, TS)),
       W_LO: os.path.join(LEAN, "D1_ring_p6_replay_w%d_%s.vi" % (W_LO, TS))}
P_GW = os.path.join(LEAN, "gap_get_buff_image_paced60_%s.vi" % TS)
P_GP = os.path.join(LEAN, "D1_ring_p6_replay_gap_%s.vi" % TS)


def live(p):
    return WB.read_live(p, fs_pairs=[])


def terms_of(lv, owner):
    return [r for r in lv["terminals"] if int(r["owner_uid"]) == int(owner)]


RSC, RSC_MD5 = os.path.join(K.CLAUDEDEV, "RingSeqCheck_v0.vi"), "0295a8d349a3b61151cd87797119b9b1"


def ring_wait(s, w):
    """RUN 4 route (runs 2/3 + p63_diag_wait: a node copied INTO the P6 copy re-sourced calibration flat-sequence wires and broke
    it). T-load copy = byte copy of the P6 replay copy whose ONE RingSeqCheck_v0 call (loop 1.2, once per tracked pick) is
    replaced (replace_object, the P6-2 route) by a byte copy of RingSeqCheck_v0 + ONE Wait (ms) fed by a panel control (default
    W), output unwired: the check's outputs leave after max(its arithmetic, W). No wire into the arithmetic."""
    sub = os.path.join(LEAN, "RingSeqCheck_w%d_%s.vi" % (w, TS))
    s.head("[L] W=%d subVI %s" % (w, os.path.basename(sub)))
    shutil.copyfile(RSC, sub)
    s.gate("L0 W%d RingSeqCheck copy md5 == 0295a8d3" % w, K.md5(sub) == RSC_MD5, fatal=True)
    g.ensure_loaded(sub)
    s.gate("L1 W%d subVI ExecState 1 before" % w, s.es("rsc w%d before" % w, sub) == 1, fatal=True)
    lv0 = live(sub); E0 = L.edges(lv0, {})
    top = sorted(set(int(r["owner_uid"]) for r in lv0["terminals"] if r["owner_class"] == "TopLevelDiagram"))
    s.gate("L2 W%d one top-level diagram uid" % w, len(top) == 1, top, fatal=True)
    wu = g.create_primitive_nested(sub, top[0], "Wait (ms)", (40, 200))
    tw = terms_of(live(sub), wu)
    sink = [r for r in tw if not r["is_source"]]
    s.gate("L3 W%d the Wait has one unwired input" % w, len(sink) == 1 and not sink[0]["wire_uid"], tw, fatal=True)
    # run 4: create_control_nested refuses a TopLevelDiagram owner -> the top-level verb create_control (Nodes[] of Diagram 0),
    # as diag_replay_standins.py used it; value set by make_default below
    wt = L.walk(sub, 0)
    ni, rows = wt[wu][0], wt[wu][2]
    ti = L.term(rows, sink[0]["term_name"], False)["i"]
    new, lab = g.create_control(sub, ni, ti)
    rec = {"new": new, "label": lab, "node_index": ni, "term_index": ti}
    s.fact("W%d create_control %r" % (w, rec))
    s.gate("L4 W%d one new panel control" % w, len(new) == 1 and lab, rec, fatal=True)
    E1 = L.edges(live(sub), {})
    add, rem = E1 - E0, E0 - E1
    s.gate("L5 W%d subVI edges == before + exactly one edge into the Wait's input" % w,
           not rem and len(add) == 1 and list(add)[0][2] == wu, (sorted(add), sorted(rem)), fatal=True)
    s.gate("L6 W%d subVI ExecState 1 after" % w, s.es("rsc w%d after" % w, sub) == 1, fatal=True)
    g.make_default(sub, {lab: w})
    msub = K.md5(sub); s.fact("SAVED %s md5 %s (control %r default %d)" % (sub, msub, lab, w))
    path = P_W[w]
    if not os.path.exists(path):                       # W_HI: the Stage's own work copy (already a byte copy of IN)
        shutil.copyfile(IN, path)
    s.gate("L7 W%d P6 copy md5 == input" % w, K.md5(path) == IN_MD5, fatal=True)
    g.ensure_loaded(path)
    c0 = L.census(path)
    cs = [u for u, p in c0.items() if os.path.basename(str(p)).lower() == "ringseqcheck_v0.vi"]
    s.gate("L8 W%d exactly one RingSeqCheck_v0 call in the P6 copy" % w, len(cs) == 1, cs, fatal=True)
    g._c97_paths()
    import build_d1_v0 as B
    own = B.owner_of(path, cs[0], strict=False)
    chain = [tuple(own)]
    for _i in range(6):
        if chain[-1][0] in ("WhileLoop", "TopLevelDiagram") or not chain[-1][1]:
            break
        chain.append(tuple(B.owner_of(path, int(chain[-1][1]), strict=False)))
    s.fact("W%d RingSeqCheck call #%d owner chain %r" % (w, cs[0], chain))
    s.gate("L9 W%d the call is inside loop 1.2 (While #%d)" % (w, LOOP12), ("WhileLoop", LOOP12) in chain, chain, fatal=True)
    s.gate("L10 W%d ExecState 1 before" % w, s.es("w%d before" % w, path) == 1, fatal=True)
    E0 = L.edges(live(path), {})
    r = g.replace_object(path, cs[0], sub); s.fact("W%d replace_object #%d -> %s: %r" % (w, cs[0], os.path.basename(sub), r))
    s.gate("L11 W%d replace: no error, new uid" % w, not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(path); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("L12 W%d callee diff == exactly the RingSeqCheck swap" % w,
           set(dd) == {cs[0], nu} and os.path.normcase(str(c1.get(nu))) == os.path.normcase(sub), dd, fatal=True)
    E1 = L.edges(live(path), {nu: cs[0]})
    s.gate("L13 W%d wire-edge diff 0 after remap (%d edges)" % (w, len(E0)), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]), fatal=True)
    s.gate("L14 W%d ExecState 1 after" % w, s.es("w%d after" % w, path) == 1, fatal=True)
    g.save(path); g.reset()
    m = K.md5(path); s.fact("SAVED %s md5 %s" % (path, m))
    return {"path": path, "md5": m, "new_uid": nu, "old_uid": cs[0], "sub": sub, "sub_md5": msub, "control": lab, "wait_uid": wu,
            "sub_edges_added": sorted(add), "callee_diff": dict((str(k), v) for k, v in dd.items()), "edges": len(E0)}


def add_wait(s, path, w):
    """NOT USED since run 4 (kept as the record of runs 1-3): a Wait copied INTO the P6 copy broke it (ExecState 0)."""
    s.head("[L] W=%d on %s" % (w, os.path.basename(path)))
    g.ensure_loaded(path)
    s.gate("L0 W%d ExecState 1 before" % w, s.es("w%d before" % w, path) == 1, fatal=True)
    lv0 = live(path); c0 = L.census(path); E0 = L.edges(lv0, {})                        # noqa: E702
    objs = dict((o["uid"], o) for o in lv0["objs"])
    s.fact("W%d #%d obj %r; d%d obj %r" % (w, TRACKER, objs.get(TRACKER), BODY12, objs.get(BODY12)))
    g._c97_paths()
    import build_d1_v0 as B
    ot, od = B.owner_of(path, TRACKER, strict=False), B.owner_of(path, BODY12, strict=False)
    s.fact("W%d owner_of #%d = %r; owner_of d%d = %r" % (w, TRACKER, ot, BODY12, od))
    s.gate("L1 W%d tracker #%d sits on d%d" % (w, TRACKER, BODY12), tuple(ot) == ("Diagram", BODY12), ot, fatal=True)
    tp = objs[TRACKER]["pos"]
    wu = g.create_primitive_nested(path, BODY12, "Wait (ms)", (int(tp[0]), int(tp[1]) - 60))
    s.fact("W%d new Wait (ms) node #%d" % (w, wu))
    lv1 = live(path)
    tw = terms_of(lv1, wu)
    s.fact("W%d Wait terminals %r" % (w, [(r["term_name"], r["is_source"], r["wire_uid"]) for r in tw]))
    sink = [r for r in tw if not r["is_source"]]
    s.gate("L2 W%d the Wait has one input terminal, unwired" % w, len(sink) == 1 and not sink[0]["wire_uid"], tw, fatal=True)
    # run 2 (16:06): stagekit.const_row (OpCreateConstOnTerm_v0, WhileLoop[i].Diagram.Nodes[n]) answered created_uid 20140 =
    # an EXISTING object, no new node, and ExecState went 0 -> it addressed another node. Now: create_control_nested, which
    # finds the node BY UID among all nodes and refuses a wired sink; the Wait's input gets a panel control, default = W.
    ti = None
    for t in range(4):
        try:
            if g._node_term_row(path, wu, t)["name"] == sink[0]["term_name"]:
                ti = t
                break
        except ValueError:
            break
    s.gate("L2b W%d Wait input terminal index found" % w, ti is not None, ti, fatal=True)
    rec = g.create_control_nested(path, wu, ti, value=w)
    s.fact("W%d create_control_nested %r" % (w, rec))
    s.gate("L2c W%d one new panel control, wired, uid echo ok" % w, not rec["err"] and len(rec["new_panel"]) == 1, rec, fatal=True)
    lab = rec["new_panel"][0]["label"]
    cu = None
    lv2 = live(path); E2 = L.edges(lv2, {}); c2 = L.census(path)
    add, rem = E2 - E0, E0 - E2
    s.fact("W%d edges +%r -%r" % (w, sorted(add), sorted(rem)))
    # run 1 (16:02): the WARM re-read after the edit also differed in 15 flat-sequence-tunnel edges of the calibration area
    # (owner attribution of pass-through terminals), so the warm diff is RECORDED; the gate is the COLD diff in [C] (CE).
    s.fact("L3 W%d WARM edge diff (recorded, not gated): exactly-one-new-edge-into-the-Wait = %s" % (
        w, (not rem and len(add) == 1 and list(add)[0][2] == wu)))
    s.gate("L3 W%d the warm diff contains the edge const -> Wait input" % w,
           any(e[2] == wu and e[3] == sink[0]["term_name"] for e in add), sorted(add), fatal=True)
    s.gate("L4 W%d the Wait's output is unwired" % w, all(not r["wire_uid"] for r in terms_of(lv2, wu) if r["is_source"]))
    s.gate("L5 W%d callee census unchanged" % w, c2 == c0, fatal=True)
    s.gate("L6 W%d ExecState 1 after" % w, s.es("w%d after" % w, path) == 1, fatal=True)
    g.make_default(path, {lab: w})                    # sets the value, Make Current Default, saves, reads back (raises on mismatch)
    g.reset()
    m = K.md5(path); s.fact("SAVED %s md5 %s (control %r default %d)" % (path, m, lab, w))
    return {"path": path, "md5": m, "wait_uid": wu, "control": lab, "control_rec": rec, "edges_added": sorted(add), "census": len(c2)}


def gap_wrapper(s):
    s.head("[G1] gap wrapper %s" % os.path.basename(P_GW))
    shutil.copyfile(GBP, P_GW)
    s.gate("G1.0 gap wrapper copy md5 == 59ec66b6", K.md5(P_GW) == GBP_MD5, fatal=True)
    g.ensure_loaded(P_GW)
    s.gate("G1.1 ExecState 1 before", s.es("gapw before", P_GW) == 1, fatal=True)
    lv0 = live(P_GW); E0 = L.edges(lv0, {}); c0 = L.census(P_GW)
    s.fact("gapw census %r" % c0)
    sb = [u for u, p in c0.items() if os.path.basename(str(p)).lower() == os.path.basename(SBP).lower()]
    s.gate("G1.2 exactly one call of the paced buf stand-in", len(sb) == 1, c0, fatal=True)
    sb = sb[0]
    bno = [r for r in terms_of(lv0, sb) if r["term_name"] == "Buffer Number Out" and r["is_source"]]
    s.gate("G1.3 its Buffer Number Out is wired", len(bno) == 1 and bno[0]["wire_uid"], bno, fatal=True)
    w99 = int(bno[0]["wire_uid"])
    sinks = [r for r in lv0["terminals"] if int(r["wire_uid"]) == w99 and not r["is_source"]]
    s.fact("gapw BN Out wire w%d sinks %r" % (w99, [(r["owner_uid"], r["owner_class"], r["term_name"], r["term_uid"]) for r in sinks]))
    s.gate("G1.4 the wire's sinks = `current image number` + one `y`", sorted(r["term_name"] for r in sinks) == ["current image number", "y"],
           sinks, fatal=True)
    top = [r["owner_uid"] for r in sinks if r["owner_class"] == "TopLevelDiagram"][0]
    # donor: the paced buf stand-in's own Increment (terminals x / x+1); the donor file is only read, never saved
    g.ensure_loaded(SBP)
    lvd = live(SBP)
    own = {}
    for r in lvd["terminals"]:
        own.setdefault(int(r["owner_uid"]), set()).add((r["term_name"], bool(r["is_source"])))
    inc = [u for u, ts in own.items() if ts == {("x", False), ("x+1", True)}]
    s.fact("donor Increment candidates in %s: %r" % (os.path.basename(SBP), inc))
    s.gate("G1.5 exactly one Increment in the donor", len(inc) == 1, inc, fatal=True)
    pos = dict((o["uid"], o["pos"]) for o in lv0["objs"]).get(sb, (200, 200))
    iu = g.create_primitive_nested(P_GW, int(top), "Increment", (int(pos[0]) + 120, int(pos[1]) + 80), donor={"donor": SBP, "uid": inc[0]})
    s.fact("gapw new Increment #%d on top diagram #%s" % (iu, top))
    order = [o["uid"] for o in g.report_all(P_GW, "Wire")]
    g.delete_object(P_GW, "Wire", order.index(w99), verify=False)
    s.gate("G1.6 wire w%d deleted" % w99, w99 not in g.uids(P_GW, "Wire"), fatal=True)
    lv1 = live(P_GW); ti = dict((r["term_name"], r) for r in terms_of(lv1, iu))
    s.fact("gapw Increment terminals %r" % ti)
    r1 = g.connect_term_uid(P_GW, int(ti["x"]["term_uid"]), int(bno[0]["term_uid"]))
    r2 = g.connect_term_uid(P_GW, int([r for r in sinks if r["term_name"] == "current image number"][0]["term_uid"]), int(ti["x+1"]["term_uid"]))
    r3 = g.connect_term_uid(P_GW, int([r for r in sinks if r["term_name"] == "y"][0]["term_uid"]), int(ti["x+1"]["term_uid"]))
    s.fact("gapw connects %r | %r | %r" % (r1, r2, r3))
    lv2 = live(P_GW); E2 = L.edges(lv2, {})
    want_rem = set((sb, "Buffer Number Out", int(r["owner_uid"]), r["term_name"]) for r in sinks)
    want_add = {(sb, "Buffer Number Out", iu, "x")} | set((iu, "x+1", int(r["owner_uid"]), r["term_name"]) for r in sinks)
    s.fact("gapw edges +%r -%r" % (sorted(E2 - E0), sorted(E0 - E2)))
    s.fact("G1.7 WARM edge diff == the planned one: %s (recorded; the gate is CE in [C])" % (E0 - E2 == want_rem and E2 - E0 == want_add))
    s.gate("G1.8 no broken wire among the new ones", not any(x.get("broken") for x in (r1, r2, r3)))
    s.gate("G1.9 callee census unchanged", L.census(P_GW) == c0, fatal=True)
    s.gate("G1.10 ExecState 1 after", s.es("gapw after", P_GW) == 1, fatal=True)
    g.save(P_GW)
    m = K.md5(P_GW); s.fact("SAVED %s md5 %s" % (P_GW, m))
    return {"path": P_GW, "md5": m, "inc_uid": iu, "wire_deleted": w99, "edges_added": sorted(want_add), "edges_removed": sorted(want_rem),
            "sb": sb}


def gap_p6(s):
    s.head("[G2] gap P6 copy %s" % os.path.basename(P_GP))
    shutil.copyfile(IN, P_GP)
    s.gate("G2.0 copy md5 == input", K.md5(P_GP) == IN_MD5, fatal=True)
    g.ensure_loaded(P_GP)
    c0 = L.census(P_GP)
    s.gate("G2.1 #%d calls replay_get_buff_image_paced60.vi" % GETBUFF_CALL,
           os.path.basename(str(c0.get(GETBUFF_CALL, ""))).lower() == os.path.basename(GBP).lower(), c0.get(GETBUFF_CALL), fatal=True)
    s.gate("G2.2 ExecState 1 before", s.es("gapP6 before", P_GP) == 1, fatal=True)
    E0 = L.edges(live(P_GP), {})
    r = g.replace_object(P_GP, GETBUFF_CALL, P_GW); s.fact("replace_object #%d -> gap wrapper: %r" % (GETBUFF_CALL, r))
    s.gate("G2.3 replace: no error, new uid", not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(P_GP); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    s.gate("G2.4 callee diff == exactly #%d -> gap wrapper" % GETBUFF_CALL,
           set(dd) == {GETBUFF_CALL, nu} and os.path.normcase(str(c1.get(nu))) == os.path.normcase(P_GW), dd)
    E1 = L.edges(live(P_GP), {nu: GETBUFF_CALL})
    s.gate("G2.5 wire-edge diff 0 after remap (%d edges)" % len(E0), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]))
    s.gate("G2.6 ExecState 1 after", s.es("gapP6 after", P_GP) == 1, fatal=True)
    g.save(P_GP); g.reset()
    m = K.md5(P_GP); s.fact("SAVED %s md5 %s" % (P_GP, m))
    return {"path": P_GP, "md5": m, "new_uid": nu, "callee_diff": dict((str(k), v) for k, v in dd.items()), "edges": len(E0)}


def body(s):
    s.start(); R = s.R
    R["copies"] = {}
    R["copies"]["w%d" % W_HI] = ring_wait(s, W_HI); s.dump()                            # noqa: E702
    s.restart()
    R["copies"]["w%d" % W_LO] = ring_wait(s, W_LO); s.dump()                            # noqa: E702
    s.restart()
    R["copies"]["gap_wrapper"] = gap_wrapper(s); s.dump()                               # noqa: E702
    R["copies"]["gap_p6"] = gap_p6(s); s.dump()                                         # noqa: E702
    s.restart()
    s.head("[C] COLD reads of the two INPUTS (read-only, nothing saved)")
    g.ensure_loaded(IN); E_in = L.edges(live(IN), {}); E_gbp = L.edges(live(GBP), {}); g.reset()
    s.fact("cold input edges: P6 replay copy %d, paced get-buff %d" % (len(E_in), len(E_gbp)))
    for tag, rec in R["copies"].items():
        s.restart()
        s.head("[C] COLD %s" % tag)
        g.ensure_loaded(rec["path"])
        s.gate("C1 %s ExecState 1 COLD" % tag, g.exec_state(rec["path"]) == 1)
        if tag.startswith("w"):
            Ec = L.edges(live(rec["path"]), {rec["new_uid"]: rec["old_uid"]})
            s.gate("CE %s COLD edges (new uid -> #%d) == cold input edges" % (tag, rec["old_uid"]), Ec == E_in,
                   (sorted(Ec - E_in)[:6], sorted(E_in - Ec)[:6]))
            c = L.census(rec["path"])
            s.gate("CS %s COLD call #%d -> %s" % (tag, rec["new_uid"], os.path.basename(rec["sub"])),
                   os.path.normcase(str(c.get(rec["new_uid"]))) == os.path.normcase(rec["sub"]), c.get(rec["new_uid"]))
            with g.vi_ref(rec["sub"]) as vi:
                cv = vi.GetControlValue(rec["control"])
            s.gate("CV %s COLD subVI control %r value == %s" % (tag, rec["control"], tag[1:]), float(cv) == float(tag[1:]), cv)
            s.gate("CM %s subVI md5 unchanged by the cold load" % tag, K.md5(rec["sub"]) == rec["sub_md5"])
        elif tag == "gap_wrapper":
            Ec = L.edges(live(rec["path"]), {})
            wa, wr = set(tuple(e) for e in rec["edges_added"]), set(tuple(e) for e in rec["edges_removed"])
            s.gate("CE gap_wrapper COLD edges == cold paced get-buff - BN Out's 2 edges + the 3 Increment edges",
                   Ec - E_gbp == wa and E_gbp - Ec == wr, (sorted(Ec - E_gbp), sorted(E_gbp - Ec)))
        else:
            Ec = L.edges(live(rec["path"]), {rec["new_uid"]: GETBUFF_CALL})
            s.gate("CE gap_p6 COLD edges (new uid -> #%d) == cold input edges" % GETBUFF_CALL, Ec == E_in,
                   (sorted(Ec - E_in)[:6], sorted(E_in - Ec)[:6]))
        g.reset()
        s.gate("C2 %s md5 unchanged by the cold load" % tag, K.md5(rec["path"]) == rec["md5"])
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + (("P6 replay copy", IN, IN_MD5), ("paced get-buff", GBP, GBP_MD5), ("paced buf stand-in", SBP, SBP_MD5),
                                        ("P6 bed", BED, BED_MD5), ("S1 replay copy", S1R, S1R_MD5), ("RingSeqCheck_v0", RSC, RSC_MD5))
    st = St(IN, IN_MD5, "p63_build", preload=False, deadline_min=48, work_dir=LEAN, work_name=os.path.basename(P_W[W_HI]), pins=pins,
            task="lean-p6-3", out_json=os.path.join(HERE, "p63_build.json"))
    sys.exit(K.run(body, st))
