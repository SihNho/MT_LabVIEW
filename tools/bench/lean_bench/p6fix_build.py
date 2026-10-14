r"""p6fix_build - lean task p6fix: the fixed P6 and its test copies, ALL saved under claudeDev\bench\lean (nothing else is saved).
Input = the P6 bed claudeDev\D1_ring_p6_20261012_212645.vi (c2d9c13c, read-only; byte copies only). Design: lean_report_p6fix.md s2.
  [F] fixed P6 (the Stage's work copy D1_ring_p6fix_<ts>.vi): Flat Sequence #29721 (one frame d29869 = the n2 read) gets ONE new
      frame BEFORE it (fs_add_frame); the 4 per-slot Locals (BufDiff #30294, TransPos #30116, RotPos #30215, FrameIdx #30239) and
      their IndexArrays (#30300, #30119, #30216, #30240) are MOVED into it (build_d1_v0.move_in, uid kept); Remove Bad Wires clears
      the severed stubs; every wire they had is re-made by connect_term_uid (LabVIEW makes the frame's tunnels). Gates: frames
      [new, 29869], owners, ExecState 1, callee census unchanged, edge set with the new tunnels collapsed == before.
  [R] replay copy: byte copy of [F] + plan 170's two swaps (#6810 -> replay_get_buff_image_paced60, #22692 -> replay_get_image_cal).
  [G] gap copy: byte copy of [R] + get-buff call -> P6-3's gap wrapper (a885a8fb).
  [W] W40 / W100 copies: byte copies of [R] + RingSeqCheck #29724 -> P6-3's RingSeqCheck_w40 / _w100 (581e2953 / 429cdc5d).
  [C] cold: each file ExecState 1 in a fresh LabVIEW, edges vs the cold reference, md5 unchanged by the load. LabVIEW gone.
    py tools/bgrun.py --material --max-min 60 --log tools/bench/lean_bench/p6fix_build.log -- py -u tools/bench/lean_bench/p6fix_build.py"""
import json, os, shutil, sys, time                                                       # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_ring_p6_20261012_212645.vi"), "c2d9c13cb40c0a5cab7433896d1df157"
GBP, GBP_MD5 = os.path.join(L.RP, "replay_get_buff_image_paced60.vi"), "59ec66b61f3518b049a3c532a8e65482"
CALR, CALR_MD5 = os.path.join(L.RP, "replay_get_image_cal.vi"), "afce0d04346fc58234d28bcc0fc42e55"
GW, GW_MD5 = os.path.join(LEAN, "gap_get_buff_image_paced60_20261013_161639.vi"), "a885a8fbc06351ab789d539af460a8d7"
RW = {40: (os.path.join(LEAN, "RingSeqCheck_w40_20261013_161639.vi"), "581e2953c10b91439eedcaa18656b13f"),
      100: (os.path.join(LEAN, "RingSeqCheck_w100_20261013_161639.vi"), "429cdc5dc55cbc861a609b9249c9347d")}
S1R, S1R_MD5 = os.path.join(L.RP, "D1_s1_replay_20260925_075422.vi"), "126f84975fca9f6124432a7e4decd0c8"
RSC, RSC_MD5 = os.path.join(K.CLAUDEDEV, "RingSeqCheck_v0.vi"), "0295a8d349a3b61151cd87797119b9b1"
FS, N2FRAME, PICK_TUN, RSC_CALL = 29721, 29869, 30179, 29724
LOCALS = {30294: "BufDiff", 30116: "TransPos", 30215: "RotPos", 30239: "FrameIdx"}
IA = {30294: 30300, 30116: 30119, 30215: 30216, 30239: 30240}                         # Local -> its IndexArray
MEMBERS = [u for l in LOCALS for u in (l, IA[l])]
SWAPS = [(6810, GBP), (22692, CALR)]                                                    # plan 170
TS = time.strftime("%Y%m%d_%H%M%S")
P_FIX = os.path.join(LEAN, "D1_ring_p6fix_%s.vi" % TS)
P_REP = os.path.join(LEAN, "D1_ring_p6fix_replay_%s.vi" % TS)
P_GAP = os.path.join(LEAN, "D1_ring_p6fix_replay_gap_%s.vi" % TS)
P_W = dict((w, os.path.join(LEAN, "D1_ring_p6fix_replay_w%d_%s.vi" % (w, TS))) for w in RW)


def live(p):
    return WB.read_live(p, fs_pairs=[])


def own_map(lv):
    return dict((int(r["owner_uid"]), r["owner_class"]) for r in lv["terminals"])


def collapse(E, tunnels):
    """(owner, term, owner, term) edges with every owner in `tunnels` collapsed to a pass-through."""
    E = set(E)
    for t in tunnels:
        ins = set(e for e in E if e[2] == t)
        outs = set(e for e in E if e[0] == t)
        E -= ins | outs
        E |= set((a[0], a[1], b[2], b[3]) for a in ins for b in outs)
    return E


def new_tunnels(lv, before_owners):
    return sorted(u for u, c in own_map(lv).items() if u not in before_owners and "Tunnel" in str(c))


def term(lv, owner, name, src):
    h = [r for r in lv["terminals"] if int(r["owner_uid"]) == int(owner) and r["term_name"] == name and bool(r["is_source"]) == src]
    if len(h) != 1:
        raise RuntimeError("term #%s %r src=%s: %d matches" % (owner, name, src, len(h)))
    return h[0]


def el(s, W):
    """LabVIEW's Error List of the (broken) work copy, read by the GUI reader as p63_diag_wait.el did (errorlist_check). Facts only."""
    sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
    import errorlist_check as EC
    EC._lv_imports()
    out = os.path.join(HERE, "p6fix_errorlist.json")
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
        s.fact("EL item %r" % (it,))
    s.fact("EL n_reported %r errors %r" % (R.get("n_reported"), R["errors"]))


def fix(s, path):
    s.head("[F] fixed P6: new frame 0 in Flat Sequence #%d + move the 4 per-slot reads into it" % FS)
    s.gate("F1 ExecState 1 before", s.es("fix before", path) == 1, fatal=True)
    lv0 = live(path); E0 = L.edges(lv0, {}); c0 = L.census(path); O0 = own_map(lv0)
    s.fact("before: %d edges, %d owners, %d callees" % (len(E0), len(O0), len(c0)))
    mem_edges = sorted(e for e in E0 if e[0] in MEMBERS or e[2] in MEMBERS)
    s.fact("member edges before (%d): %r" % (len(mem_edges), mem_edges))
    s.gate("F2 member edges = 4 Local->array + 4 index + 6 element sinks = 14", len(mem_edges) == 14, mem_edges, fatal=True)
    fr0 = g.fs_frames(path, FS)
    s.gate("F3 FS #%d has ONE frame d%d" % (FS, N2FRAME), fr0["frames"] == [N2FRAME], fr0, fatal=True)
    r = g.fs_add_frame(path, FS, 0, after=False); s.fact("fs_add_frame %r" % r)
    nf = int(r["new_frame"])
    s.gate("F4 frames after == [new d%d, d%d] (new frame FIRST)" % (nf, N2FRAME), r["frames_after"] == [nf, N2FRAME], r, fatal=True)
    s.gate("F5 ExecState 1 after the empty frame", s.es("fix +frame", path) == 1, fatal=True)
    pos = dict((int(o["uid"]), o["pos"]) for o in live(path)["objs"]).get(nf) or (0, 0)
    s.fact("new frame d%d pos %r" % (nf, pos))
    _ = g._c97_paths()
    import build_d1_v0 as B
    di = g._uid_index(path, "Diagram", nf)
    inv0 = set(g.uids(path, "Invoke"))
    for j, m in enumerate(MEMBERS):
        u = B.move_in(path, m, di, (int(pos[0]) + 20 + 70 * (j % 2), int(pos[1]) + 20 + 40 * (j // 2)))
        di = g._uid_index(path, "Diagram", nf)
        own = B.owner_of(path, m, strict=False)
        s.fact("move_in #%d (%s) -> returned uid %r, owner %r" % (m, LOCALS.get(m, "IndexArray"), u, own))
        s.gate("F6 #%d moved, owner = new frame d%d (uid-addressed re-read)" % (m, nf), tuple(own)[1] == nf, (u, own), fatal=True)
    # run 4 (23:18): the warm edge set was EXACTLY the bed's but ExecState 0, with 8 new unwired Invoke nodes = one junk Invoke per
    # OpMoveIn call (gscript._move_into_frame purges them after each move for the same reason). Purge them here.
    npur, left = g._purge_new_invokes(path, inv0)
    s.fact("junk Invokes left by the 8 moves: purged %r, left %r" % (npur, left))
    s.gate("F6b every junk Invoke the moves left is deleted", not left and not (set(g.uids(path, "Invoke")) - inv0), (npur, left), fatal=True)
    n_after, es_rbw = g.remove_bad_wires_scripted(path)
    s.fact("Remove Bad Wires after the moves: wires %r, ExecState %r" % (n_after, es_rbw))
    lv1 = live(path); E1 = L.edges(lv1, {})
    lost = sorted(e for e in (E0 - E1) if e not in mem_edges)
    s.fact("after moves+RBW: edges lost vs before (non-member) %r" % lost)
    # run 1 (22:37): RBW also removed the INNER wire of loop tunnel #9503 (For Loop #1359 -> `Magnet position` #28083), whose outer
    # source (IndexArray #30119) had been cut by the move. Such an edge (source = a tunnel that was a member's sink) is re-made below
    # by its ORIGINAL terminal uids after the tunnel has its input again; any other lost edge stops the run.
    tun_sinks = set(e[2] for e in mem_edges if e[0] in MEMBERS and e[2] not in MEMBERS)
    s.gate("F7 every NON-member edge lost by the moves + RBW starts at a tunnel fed by a member", all(e[0] in tun_sinks and "Tunnel" in str(O0.get(e[0]))
                                                                                                 for e in lost), lost, fatal=True)
    relink = []
    for e in lost:
        srcs = [r for r in lv0["terminals"] if int(r["owner_uid"]) == e[0] and r["term_name"] == e[1] and r["is_source"] and int(r["wire_uid"])]
        pair = [(a, b) for a in srcs for b in lv0["terminals"] if int(b["wire_uid"]) == int(a["wire_uid"]) and not b["is_source"]
                and int(b["owner_uid"]) == e[2] and b["term_name"] == e[3]]
        s.gate("F7b lost edge %r maps to exactly one terminal pair" % (e,), len(pair) == 1, pair, fatal=True)
        relink.append((e, pair[0][0], pair[0][1]))
    ops = []
    # (a) Local -> IndexArray `array`, inside the new frame
    for l, ia in IA.items():
        lv = live(path)
        sk, sr = term(lv, ia, "array", False), [r for r in lv["terminals"] if int(r["owner_uid"]) == l and r["is_source"]][0]
        ops.append(("array", l, ia, g.connect_term_uid(path, int(sk["term_uid"]), int(sr["term_uid"]))))
    # (b) pick loop tunnel `min slot` -> the 4 `index`: first one from the outer source, the other 3 from the new tunnel's inner face
    src0 = [e for e in mem_edges if e[2] in IA.values() and e[3] == "index"]
    s.gate("F8 the 4 index sources are the pick loop tunnel #%d" % PICK_TUN, len(src0) == 4 and all(e[0] == PICK_TUN for e in src0), src0, fatal=True)
    lv = live(path)
    tsrc = term(lv, PICK_TUN, src0[0][1], True)
    first = True
    for ia in IA.values():
        lv = live(path)
        sk = term(lv, ia, "index", False)
        if first:
            ops.append(("index", PICK_TUN, ia, g.connect_term_uid(path, int(sk["term_uid"]), int(tsrc["term_uid"]))))
            first = False
            lv = live(path)
            w = int(term(lv, ia, "index", False)["wire_uid"])
            inner = [r for r in lv["terminals"] if int(r["wire_uid"]) == w and r["is_source"]]
            s.fact("index wire w%d source(s) after the first connect: %r" % (w, inner))
            s.gate("F9 the first index wire is fed by a new tunnel inside the new frame",
                   len(inner) == 1 and "Tunnel" in str(inner[0]["owner_class"]) and int(inner[0]["frame_diagram"]) == nf, inner, fatal=True)
            tin = inner[0]
        else:
            ops.append(("index", int(tin["owner_uid"]), ia, g.connect_term_uid(path, int(sk["term_uid"]), int(tin["term_uid"]))))
    # (c) IndexArray `element` -> its old sinks: first one direct (LabVIEW makes the out tunnel), the rest from the tunnel's outer face
    # run 2 (22:48): loop tunnel #9503's outer terminal #9508 was no longer in the VI after the moves + RBW. A sink is found by uid,
    # else by (owner, name, direction, diagram) unwired; if its owner (a tunnel) is GONE, the tunnel's own inner sinks are wired
    # instead (LabVIEW makes a new tunnel) and the old tunnel is collapsed as a pass-through in the BEFORE set for the edge gate.
    gone = []

    def find_free(lv, r0):
        h = [r for r in lv["terminals"] if r["term_uid"] == r0["term_uid"] and not int(r["wire_uid"])]
        if len(h) != 1:
            h = [r for r in lv["terminals"] if int(r["owner_uid"]) == int(r0["owner_uid"]) and r["term_name"] == r0["term_name"]
                 and bool(r["is_source"]) == bool(r0["is_source"]) and int(r["frame_diagram"]) == int(r0["frame_diagram"]) and not int(r["wire_uid"])]
        return h[0] if len(h) == 1 else None
    for ia in IA.values():
        w0 = int(term(lv0, ia, "element", True)["wire_uid"])                       # the EXACT sink terminals (by uid) from before:
        sinks = [r for r in lv0["terminals"] if int(r["wire_uid"]) == w0 and not r["is_source"]]   # BuildArray has 3 `element`s
        s.fact("#%d element sinks before: %r" % (ia, [(r["owner_uid"], r["term_name"], r["term_uid"]) for r in sinks]))
        lv = live(path)
        el = term(lv, ia, "element", True)
        tout = None
        todo = list(sinks)
        while todo:
            e0 = todo.pop(0)
            lv = live(path)
            sk = find_free(lv, e0)
            if sk is None:
                alive = [r for r in lv["terminals"] if int(r["owner_uid"]) == int(e0["owner_uid"])]
                s.fact("sink #%s of #%s (%s) not free: owner terminals now %r" % (e0["term_uid"], e0["owner_uid"], e0["owner_class"], alive))
                if alive or "Tunnel" not in str(e0["owner_class"]):
                    raise RuntimeError("sink terminal #%s of #%s not found free after RBW: %r" % (e0["term_uid"], e0["owner_uid"], alive))
                tu = int(e0["owner_uid"]); gone.append(tu)                             # noqa: E702
                ins = [r for r in lv0["terminals"] if int(r["owner_uid"]) == tu and r["is_source"] and int(r["wire_uid"])]
                down = [r for a in ins for r in lv0["terminals"] if int(r["wire_uid"]) == int(a["wire_uid"]) and not r["is_source"]]
                s.fact("tunnel #%d GONE; wiring its inner sinks instead: %r" % (tu, [(r["owner_uid"], r["term_name"], r["term_uid"]) for r in down]))
                relink[:] = [x for x in relink if x[0][0] != tu]
                todo = down + todo
                continue
            e = (ia, "element", int(e0["owner_uid"]), e0["term_name"])
            if tout is None:
                ops.append(("element", ia, e[2], g.connect_term_uid(path, int(sk["term_uid"]), int(el["term_uid"]))))
                lv = live(path)
                w = int([r for r in lv["terminals"] if r["term_uid"] == sk["term_uid"]][0]["wire_uid"])
                srcs = [r for r in lv["terminals"] if int(r["wire_uid"]) == w and r["is_source"]]
                s.fact("element #%d -> #%d %r: sink wire w%d source(s) %r" % (ia, e[2], e[3], w, srcs))
                s.gate("F10 #%d element reaches #%d through a new out tunnel of the new frame" % (ia, e[2]),
                       len(srcs) == 1 and "Tunnel" in str(srcs[0]["owner_class"]) and int(srcs[0]["frame_diagram"]) != nf, srcs, fatal=True)
                tout = srcs[0]
            else:
                ops.append(("element", int(tout["owner_uid"]), e[2], g.connect_term_uid(path, int(sk["term_uid"]), int(tout["term_uid"]))))
    for e, rs, rk in relink:                                                           # (d) the tunnel-downstream edges RBW removed
        lv = live(path)
        a = [r for r in lv["terminals"] if r["term_uid"] == rs["term_uid"]] or [
            r for r in lv["terminals"] if int(r["owner_uid"]) == int(rs["owner_uid"]) and r["is_source"]
            and int(r["frame_diagram"]) == int(rs["frame_diagram"])]
        b = find_free(lv, rk)
        if len(a) != 1 or b is None:
            raise RuntimeError("relink %r: source %r sink %r" % (e, a, b))
        ops.append(("relink", e[0], e[2], g.connect_term_uid(path, int(b["term_uid"]), int(a[0]["term_uid"]))))
    s.fact("connects: %r" %[(a, b, c, {k: d.get(k) for k in ("wire_uid", "broken", "err")}) for a, b, c, d in ops])
    s.gate("F11 every connect: no error, not broken", all(not d["err"] and not d["broken"] for *_x, d in ops), fatal=True)
    es = s.es("fix after", path)
    if es != 1:                                                                         # run 3 (23:02): ES 0 here -> wait, re-read
        time.sleep(8); es = s.es("fix after +8 s", path)
    lv2 = live(path); E2 = L.edges(lv2, {}); c2 = L.census(path)
    nt = new_tunnels(lv2, O0)
    Ec = collapse(E2, nt)
    E0x = collapse(E0, gone)
    s.fact("new tunnels %r; gone tunnels %r; warm edges +%r -%r" % (nt, gone, sorted(Ec - E0x)[:20], sorted(E0x - Ec)[:20]))
    s.fact("new owners: %r" % [(u, own_map(lv2)[u]) for u in sorted(set(own_map(lv2)) - set(O0))])
    if es != 1:
        try:
            el(s, path)
        except Exception as e:                                                         # noqa: BLE001
            s.fact("Error List read failed: %r" % e)
    s.gate("F12 ExecState 1 after the fix (warm)", es == 1, fatal=True)
    s.gate("F12b no new object besides the frame's tunnels and the new For Loop tunnel",
           all("Tunnel" in str(own_map(lv2)[u]) for u in set(own_map(lv2)) - set(O0)), sorted(set(own_map(lv2)) - set(O0)))
    s.gate("F13 callee census unchanged", c2 == c0, fatal=True)
    s.gate("F14 WARM edge set with the new tunnels (and gone tunnels %r) collapsed == before (%d edges)" % (gone, len(E0x)), Ec == E0x,
           (sorted(Ec - E0x)[:12], sorted(E0x - Ec)[:12]))
    new_owners = sorted(set(own_map(lv2)) - set(O0))
    s.fact("new owners (frame tunnels etc.): %r" % [(u, own_map(lv2)[u]) for u in new_owners])
    g.save(path); g.reset()
    m = K.md5(path); s.fact("SAVED %s md5 %s" % (path, m))
    return {"path": path, "md5": m, "new_frame": nf, "tunnels": nt, "gone": gone, "edges": len(E0),"ops": [(a, b, c, d.get("wire_uid")) for a, b, c, d in ops],
            "member_edges": mem_edges, "new_owners": new_owners}


def swap(s, tag, src, src_md5, dst, pairs):
    """byte copy src -> dst, then replace_object per (uid, new path); gates: callee diff == the swaps, edge diff 0 after remap, ES 1."""
    s.head("[%s] %s" % (tag, os.path.basename(dst)))
    shutil.copyfile(src, dst)
    s.gate("%s.0 copy md5 == source %s" % (tag, src_md5[:8]), K.md5(dst) == src_md5, fatal=True)
    g.ensure_loaded(dst)
    s.gate("%s.1 ExecState 1 before" % tag, s.es("%s before" % tag, dst) == 1, fatal=True)
    c0 = L.census(dst); E0 = L.edges(live(dst), {})
    remap, news = {}, {}
    for uid, newp in pairs:
        s.gate("%s.2 #%d is a callee" % (tag, uid), uid in c0, c0.get(uid), fatal=True)
        r = g.replace_object(dst, uid, newp); s.fact("%s replace_object #%d -> %s: %r" % (tag, uid, os.path.basename(newp), r))
        s.gate("%s.3 replace #%d: no error, new uid" % (tag, uid), not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
        remap[r["new_uid"]] = uid; news[uid] = r["new_uid"]
    c1 = L.census(dst); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u))
    want = set(remap) | set(remap.values())
    s.gate("%s.4 callee diff == exactly the swap(s)" % tag,
           set(dd) == want and all(os.path.normcase(str(c1.get(news[u]))) == os.path.normcase(p) for u, p in pairs),
           dd, fatal=True)
    E1 = L.edges(live(dst), remap)
    s.gate("%s.5 wire-edge diff 0 after remap (%d edges)" % (tag, len(E0)), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]), fatal=True)
    s.gate("%s.6 ExecState 1 after" % tag, s.es("%s after" % tag, dst) == 1, fatal=True)
    g.save(dst); g.reset()
    m = K.md5(dst); s.fact("SAVED %s md5 %s" % (dst, m))
    return {"path": dst, "md5": m, "src": src, "remap": dict((str(k), v) for k, v in remap.items()), "new_uids": news,
            "callee_diff": dict((str(k), v) for k, v in dd.items()), "edges": len(E0)}


def body(s):
    s.start(); R = s.R
    R["copies"] = {}
    for p, mm in [(GW, GW_MD5)] + list(RW.values()):
        s.gate("P0 reused test file %s md5 == %s" % (os.path.basename(p), mm[:8]), K.md5(p) == mm, fatal=True)
    R["copies"]["fix"] = f = fix(s, s.work); s.dump()                                   # noqa: E702
    s.restart()
    R["copies"]["replay"] = rp = swap(s, "R", f["path"], f["md5"], P_REP, SWAPS); s.dump()   # noqa: E702
    gb_new = rp["new_uids"][6810]
    s.restart()
    R["copies"]["gap"] = swap(s, "G", rp["path"], rp["md5"], P_GAP, [(gb_new, GW)]); s.dump()   # noqa: E702
    for w in sorted(RW):
        s.restart()
        R["copies"]["w%d" % w] = swap(s, "W%d" % w, rp["path"], rp["md5"], P_W[w], [(RSC_CALL, RW[w][0])]); s.dump()   # noqa: E702
    # [C] cold
    s.restart()
    s.head("[C] COLD reads: the bed (read-only) and every saved file")
    g.ensure_loaded(BED); E_bed = L.edges(live(BED), {}); O_bed = set(own_map(live(BED))); g.reset()
    s.fact("cold bed edges %d" % len(E_bed))
    cold = {}
    for tag in ["fix", "replay", "gap", "w40", "w100"]:
        rec = R["copies"][tag]
        s.restart()
        g.ensure_loaded(rec["path"])
        s.gate("C1 %s ExecState 1 COLD" % tag, g.exec_state(rec["path"]) == 1)
        lv = live(rec["path"])
        if tag == "fix":
            nt = new_tunnels(lv, O_bed)
            Ec = collapse(L.edges(lv, {}), nt)
            Eb = collapse(E_bed, rec["gone"])
            s.gate("CE fix COLD edges, new tunnels %r (bed: gone %r) collapsed == cold bed edges (%d)" % (nt, rec["gone"], len(Eb)), Ec == Eb,
                   (sorted(Ec - Eb)[:12], sorted(Eb - Ec)[:12]))
            s.gate("CO fix COLD the 8 moved nodes are in the new frame d%d" % rec["new_frame"],
                   all(int(r["frame_diagram"]) == rec["new_frame"] for r in lv["terminals"] if int(r["owner_uid"]) in MEMBERS))
            fr = g.fs_frames(rec["path"], FS)["frames"]
            s.gate("CF fix COLD FS #%d frames == [d%d, d%d]" % (FS, rec["new_frame"], N2FRAME), fr == [rec["new_frame"], N2FRAME], fr)
            cold["fix"] = L.edges(lv, {})
        else:
            ref = cold["fix"] if tag == "replay" else cold["replay"]
            Ec = L.edges(lv, dict((int(k), v) for k, v in rec["remap"].items()))
            s.gate("CE %s COLD edges (remapped) == cold source edges" % tag, Ec == ref, (sorted(Ec - ref)[:6], sorted(ref - Ec)[:6]))
            if tag == "replay":
                cold["replay"] = L.edges(lv, {})
        g.reset()
        s.gate("C2 %s md5 unchanged by the cold load" % tag, K.md5(rec["path"]) == rec["md5"])
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + (("P6 bed", BED, BED_MD5), ("paced get-buff", GBP, GBP_MD5), ("replay cal", CALR, CALR_MD5),
                                        ("gap wrapper", GW, GW_MD5), ("RSC w40", RW[40][0], RW[40][1]), ("RSC w100", RW[100][0], RW[100][1]),
                                        ("S1 replay copy", S1R, S1R_MD5), ("RingSeqCheck_v0", RSC, RSC_MD5))
    st = St(BED, BED_MD5, "p6fix_build", preload=False, deadline_min=58, work_dir=LEAN, work_name=os.path.basename(P_FIX), pins=pins,
            task="lean-p6fix", out_json=os.path.join(HERE, "p6fix_build.json"))
    sys.exit(K.run(body, st))
