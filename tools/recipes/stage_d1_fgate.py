r"""stage_d1_fgate - card 97-4 (PD205(d)(e)2, PD206(b)(c)(f)(g); brief_97-4.md): S1 copy -> claudeDev\D1_s1_fgate_<ts>.vi, #1359's graph
chain in case A (#1359 body) + #8323's BuildArray/terminal in case B (#637 body), upd = (Q&R(i, N).rem == 0), N = new I32 control, default 9.
Rows ONLY from plans/plan_fgate_97.json. FOUND FIRST, no new op: gscript case_in/move_into_frame/case_frames/set_control_label/
tunnel_use_default (97-3 selftest), stagekit copy_in on the Moving-Objects pair (q_m4_copy_probe, stage_d1_m4b), carrier-IA ctl (T4a).
PREDICTION = the F0..F6 gates below (each fatal where a later step depends on it); pins/S1 md5 same; fixtures restored; LabVIEW gone.
card 97-5: copy_in FIRST, then K.unload_donor() (fact: donor resident False, MB drop) BEFORE the MEMSTOP-metered op() edits.
    MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/fgate_97_stage.log -- py -u tools/recipes/stage_d1_fgate.py"""
import json, os, shutil, subprocess, sys, time; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa: E401,E702
import stagekit as K, gscript as g, jev_candidates as JC, vigraph as V                           # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                               # noqa: E731
P = J(K.BENCH, "plans/plan_fgate_97.json"); U, T, XY = P["uids"], P["terms"], P["pos"]         # noqa: E702
DRY = bool(getattr(g.report_all, "_dry", False))
FINAL = os.path.join(K.CLAUDEDEV, "D1_s1_fgate_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
first = lambda xs, d=0: next(iter(list(xs)), d)                                                   # noqa: E731
e3 = lambda res: str(res[2]) if isinstance(res, tuple) and len(res) >= 3 else ""; D639, D7911 = U["loop_body"], U["for_body"]  # noqa: E731,E702


def body(s):
    s.start(); W = s.work; B, CN, CF = (K.mod(m) for m in ("build_d1_v0", "build_opconnectnested_v1", "build_opconnectfromwire_v0"))  # noqa: E702
    CNL = J(CN.MAP_OUT); shutil.copyfile(s.input_vi, g.MOVE_SRC)                                   # noqa: E702
    s.gate("K4 MOVE_SRC holds S1's bytes (copy_in donor)", DRY or K.md5(g.MOVE_SRC) == s.input_md5, fatal=True)
    s.gate("F0 ExecState 1 at MOVE_DST", s.es("F0") == 1, fatal=True)

    def op(verb, fn, detail=""):
        r = s._op(verb, fn, detail); s.junk_purge(verb); pb = (K.private_bytes() or 0) / 1e6    # noqa: E702
        s.fact("MEM after {0}: {1:.1f} MB".format(verb, pb))
        s.gate("OP {0} {1} ran without an error".format(verb, detail), not r["err"] and not e3(r["result"]), (r["err"], e3(r["result"])), fatal=True)
        if pb > P["memstop_mb"]:
            raise K.Stop("MEMSTOP {0:.0f} MB > {1}".format(pb, P["memstop_mb"]))
        return r["result"]

    def tri(u, name, src, d=D639):                                                               # (diag idx, node idx, term idx)
        dd = g._uid_index(W, "Diagram", d); nn = g._node_index(W, dd, u); _e, rows = g.node_terms_uid(W, dd, nn)  # noqa: E702
        return dd, nn, first(r["i"] for r in rows if (name is None or r["name"] == name) and bool(r["is_source"]) == src)
    own = lambda u: (lambda o: (o[0], o[1]))(B.owner_of(W, u, strict=False))                    # noqa: E731
    cen = lambda: dict((c, s.count(c)) for c in P["census"])                                     # noqa: E731
    c0, lp0, ia0, un0 = cen(), set(g.uids(W, "LoopTunnel")), set(g.uids(W, "IndexArray")), dict((u, own(u)) for u in P["untouched"])
    qr, eq = [s.copy_in(U[k + "_cls"], U[k], D639, tuple(XY[k]), k) if not DRY else 0 for k in ("qr", "eq0")]   # donors FIRST (card 97-5)
    s.gate("F2a Q&R #{0} and Equal To 0? #{1} copies owned by Diagram #{2}".format(qr, eq, D639), own(qr)[1] == D639 and own(eq)[1] == D639, (own(qr), own(eq)), fatal=True)
    s.fact("DONOR UNLOAD before the MEMSTOP-metered edits (judgement c97): {0}".format("dry" if DRY else K.unload_donor()))
    op("build_index_array", lambda: g.build_index_array(W, tuple(XY["carrier"])))
    ia = first(u for u in g.uids(W, "IndexArray") if u not in ia0); ni = first([t[0] for t in g.node_info(W) if t[1] == "Index Array"][-1:])  # noqa: E702
    new, L = op("create_control", lambda: g.create_control(W, ni, P["carrier_term"])) or ([], ""); ct = first(x["uid"] for x in new)   # noqa: E702
    s.gate("F1a one new control from the carrier IA #{0}: {1!r}".format(ia, L), len(new) == 1 and bool(L), new, fatal=True)
    cases, mv = {}, {}
    for t, D in (("A", D7911), ("B", D639)):
        c = op("case_in", lambda D=D, t=t: g.case_in(W, D, tuple(XY["build_" + t]), L, position=tuple(XY["case_" + t])), t)
        s.gate("F3 case {0} #{1} owned by Diagram #{2}, 2 frames".format(t, c["case"], D), c["owner"] == D and len(c["frames"]) == 2, c, fatal=True)
        cases[t] = c["case"]
    p = first(i for i, r in enumerate(g.panel_wiring(W)) if r["label"] == L)
    lr = op("set_control_label", lambda: g.set_control_label(W, p, P["label"]), "panel[{0}]".format(p))
    dv = op("set_default", lambda: g.set_default_in_memory(W, P["label"], P["default"], P["probe"]))
    row = first([r for r in g.panel_wiring(W) if r["label"] == P["label"]], {})
    s.gate("F1b label {0!r} + default {1} read back".format(P["label"], P["default"]), lr["text_back"] == P["label"] and int(dv["after_reinit"]) == P["default"] and bool(row), (lr, dv, row), fatal=True)
    wl = row.get("wire") if isinstance(row, dict) else 0
    for cls, u in (("Wire", wl), ("IndexArray", ia)):                                           # L's top-level wire first, then the carrier
        _x = u and op("delete_object", lambda cls=cls, u=u: g.delete_object(W, cls, [o["uid"] for o in g.report_all(W, cls)].index(u), verify=False), "{0} #{1}".format(cls, u))
    s.gate("F1c carrier IA and L's top-level wire gone", ia not in g.uids(W, "IndexArray") and wl not in g.uids(W, "Wire"), (ia, wl), fatal=True)
    op("move_in", lambda: B.move_in(W, ct, g._uid_index(W, "Diagram", D639), tuple(XY["nctl"])), "ctl #{0}".format(ct))
    s.gate("F1d the N control terminal #{0} owned by Diagram #{1}".format(ct, D639), own(ct)[1] == D639, own(ct), fatal=True)
    wi =first(x["i"] for x in CF.wire_source_owner(W, U["iter_wire"], n=10) if x.get("is_source"))
    r = s.connect_from_wire(*(tri(qr, T["qr_x"], False) + (U["iter_wire"], wi)))
    s.gate("OP connect_from_wire w{0} -> Q&R.x no error".format(U["iter_wire"]), not r["err"] and not e3(r["result"]), (r["err"], e3(r["result"])), fatal=True); s.junk_purge("connect_from_wire")  # noqa: E702 run 1: its junk Invoke was never purged (F5a 1->2, ExecState 0)
    op("wire_control", lambda: g.wire_control(W, [P["label"]], U["qr_cls"], s.uid_index(U["qr_cls"], qr), [T["qr_y"]], src_diagram_index=g._uid_index(W, "Diagram", D639)), "N -> Q&R.y")
    op("connect_nested_v1", lambda: CN.connect_nested_v1(W, *(tri(eq, T["eq0_x"], False) + tri(qr, T["qr_rem"], True) + (CNL,))), "rem -> Eq0.x")
    for t, D in (("B", D639), ("A", D7911)):
        op("connect_nested_v1", lambda D=D, t=t: CN.connect_nested_v1(W, *(tri(cases[t], None, False, D) + tri(eq, T["eq0_out"], True) + (CNL,))), "upd -> case " + t)
    s.fact("E1 (review c97-fgate-es0) ExecState {0}, Invoke {1} after wiring, before moves".format(s.es("E1"), s.count("Invoke"))); rows = K.mod("allterms").read_terms(W)[0]; ow = lambda u: [x for x in rows if int(x["owner_uid"]) == int(u)]  # noqa: E702,E731
    nl = sorted(set(g.uids(W, "LoopTunnel")) - lp0); tun = first(nl); li = s.uid_index("LoopTunnel", tun); mode = g.tunnels(W, li)["index_mode"] if li is not None else None   # noqa: E702
    if mode not in (0, None):
        op("set_index_mode", lambda: g.set_index_mode(W, li, 0), "#{0}".format(tun)); mode = g.tunnels(W, li)["index_mode"]  # noqa: E702
    s.gate("F3b exactly one new #1359 LoopTunnel {0}, IndexMode 0 (non-indexed)".format(nl), len(nl) == 1 and mode == 0, (nl, mode), fatal=True)
    upd = first(x["wire_uid"] for x in ow(eq) if x["is_source"]); tw = set(int(x["wire_uid"] or 0) for x in ow(tun))   # noqa: E702
    sel = dict((t, first(x["wire"] for x in g.node_terms_uid(W, *tri(cases[t], None, False, D)[:2])[1] if not x["is_source"])) for t, D in (("A", D7911), ("B", D639)))
    s.gate("F3c one upd wire: B's selector == upd #{0} == tunnel outer; tunnel inner == A's selector".format(upd), upd and sel["B"] == upd and {upd, sel["A"]} <= tw, (upd, sel, tw), fatal=True)
    fr = dict((t, g.case_frames(W, cases[t])) for t in cases)
    tf = dict((t, first(f for n, f in zip(fr[t]["names"], fr[t]["frames"]) if str(n).strip() == "True")) for t in fr)
    s.gate("F3d frames ' False '/' True ' after the boolean selectors; True frames {0}".format(tf), all(sorted(str(n).strip() for n in fr[t]["names"]) == ["False", "True"] for t in fr), fr, fatal=True)
    for t in ("A", "B"):
        mv[t] = m = op("move_into_frame", lambda t=t: g.move_into_frame(W, tf[t], P["set_" + t.lower()], tuple(XY["case_" + t])), t); s.R["move_" + t] = m   # noqa: E702
        s.gate("F4 {0}: every member owned by the ' True ' frame #{1}".format(t, tf[t]), all(o[1] == tf[t] for o in m["owners_after"].values()), m["owners_after"], fatal=True)
        s.gate("F4 {0}: edge table (src term uid -> sink term uid, new tunnels collapsed) == before ({1} edges)".format(t, len(m["edges_before"])), not m["missing"] and not m["extra"], {"missing": m["missing"], "extra": m["extra"]}, fatal=True)
    rows = K.mod("allterms").read_terms(W)[0]; wo = first(x["wire_uid"] for x in ow(U["out_loop_tunnel"]) if not x["is_source"])   # noqa: E702
    outA = sorted(set(int(x["owner_uid"]) for x in rows if x["wire_uid"] == wo and x["is_source"] and int(x["owner_uid"]) in mv["A"]["new_tunnels"]))
    s.gate("F4c case A's output tunnel(s) {0}: {1} expected (feed LoopTunnel #{2})".format(outA, P["a_out_tunnels"], U["out_loop_tunnel"]), len(outA) == P["a_out_tunnels"], outA, fatal=True)
    for tu in outA:
        u = op("tunnel_use_default", lambda tu=tu: g.tunnel_use_default(W, tu, True), "#{0}".format(tu)); s.gate("F4d #{0} UseDefault reads True".format(tu), u["after"] is True and not u["err"], u)  # noqa: E702
    s.fact("E3 ExecState {0} after use-default; new tunnels A {1} B {2}".format(s.es("E3"), mv["A"]["new_tunnels"], mv["B"]["new_tunnels"])); c1 = cen(); s.fact("CENSUS before {0} after {1}".format(c0, c1)); s.R["census"] = [c0, c1]; s.gate("F5a Invoke count unchanged (junk purged)", c1["Invoke"] == c0["Invoke"], (c0["Invoke"], c1["Invoke"]))  # noqa: E702
    un1 = dict((u, own(u)) for u in P["untouched"]); s.gate("F5b untouched objects keep their owners", un1 == un0, (un0, un1))   # noqa: E702
    S1 = JC.load(JC.S1_KEY); lv = K.mod("wiki_build").read_live(W, fs_pairs=S1["wiki"]["fs_tunnel_pairs"])   # noqa: E702
    cd = V.computation_diff(S1, JC.from_parts({"terminals": lv["terminals"], "graph_summary": S1["wiki"]["graph_summary"]}, lv["objs"],
                            J(JC._newest("graph_loops_s1_*.json"))["loops"], JC.node_labels_default(), lv["fs_tunnel_pairs"], "fgate"))
    [s.fact("CDIFF ROW {0}".format(dict((k, V.show(v) if k == "sink" else v) for k, v in y.items()))) for y in cd["rows"]]
    ok_new = set([qr, eq, ct, cases["A"], cases["B"]] + nl + list(mv["A"]["new_tunnels"]) + list(mv["B"]["new_tunnels"]))
    added = [(x["node"], x["class"]) for x in cd["computation_nodes_added"]]; s.R["cdiff"] = cd       # noqa: E702
    s.fact("CDIFF rows {0}; added {1}; removed {2}".format(len(cd["rows"]), added, cd["computation_nodes_removed"]))
    s.gate("F5c cdiff(S1, fgate): 0 rows, 0 removed, added only new objects", not cd["rows"] and not cd["computation_nodes_removed"] and all(n in ok_new for n, _c in added), (len(cd["rows"]), added))   # not fatal: rows are listed for judgement
    s.gate("F6a ExecState 1 warm", s.es("warm, before save") == 1, fatal=True)
    m = s.save(); shutil.copyfile(W, FINAL)                                                        # noqa: E702
    s.gate("F6b artefact {0} == the saved bytes".format(os.path.basename(FINAL)), DRY or (m and K.md5(FINAL) == m), m, fatal=True)
    s.restart(); s.gate("F6c ExecState 1 COLD in a fresh LabVIEW", s.es("cold reload", target=FINAL) == 1)   # noqa: E702
    s.R["fgate"] = {"final": FINAL, "md5": m, "bytes": os.path.exists(FINAL) and os.path.getsize(FINAL), "qr": qr, "eq0": eq, "ctl": ct,
                    "cases": cases, "true_frames": tf, "tunnel_1359": nl, "upd": upd, "outA": outA}; s.dump()   # noqa: E702


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [os.path.basename(FINAL)] if os.path.exists(FINAL) else [])


if __name__ == "__main__":
    g.restore_move_fixtures(); FXL = K.fixture_listing()                                           # noqa: E702
    st = St(os.path.join(K.CLAUDEDEV, P["input"]["vi"]), P["input"]["md5"], "stage_d1_fgate", preload=False, deadline_min=40,
            work_dir=os.path.dirname(g.MOVE_DST), work_name=os.path.basename(g.MOVE_DST), task="card 97-4", out_json=os.path.join(K.BENCH, "fgate_97_stage.json"))
    rc = K.run(body, st)
    if not DRY:
        K.mod("bench_prep").restart_labview(); g.reset(); g.restore_move_fixtures()                 # noqa: E702
        rc = rc if K.fixtures_check((st.input_md5,), FXL) else 1
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0); print("LabVIEW gone at exit:", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), flush=True)  # noqa: E702
    sys.exit(rc)
