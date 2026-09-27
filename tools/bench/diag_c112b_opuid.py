r"""diag_c112b_opuid - card 112-2 D2/S3: BUILD the reader the uid route needs - claudeDev\OpNodeTermsUid_v0.vi = a byte copy of
OpNodeTerms_v0 (the donor is never written) + ONE property node GObject.UID 632A813 on each Terminals[] entry's OWN reference
(PN_C `reference out`, inside the For loop) -> auto-indexed tunnel -> array indicator (+ its error out) - then MEASURE it.
PRIOR ART (checked first): no reader returns a per-terminal uid from the node side (docs/cycle27-plan.md:2925; gscript
node_terms / net_map / OpWireSource_v5 / OpOwnerChain_v1 give none); the build steps are tools/recipes/build_opnodeterms_v0.py
5-9 verbatim in kind (build_property, wire, exit_loop, set_index_mode, tunnel_indicator, save). Plain gscript: a TOOL build.
PREDICTION (gates): B1 copy ExecState 1; B2 PN_C found (a body Property with a 'Wire' source and a bare 'reference out');
B3 PN_U + wire -> ExecState 1; B4 exit_loop 'UID' and 'error out' -> exactly 1 new LoopTunnel each; B5 two new indicators;
B6 ExecState 1 + saved; F1 on the donor OpNodeTerms_v0.vi (read-only, md5 unchanged) EVERY node on EVERY diagram: node echo ==
node uid, every entry's uid is a terminal of the whole-VI table (OpAllTerms_v1) with the same direction + wire, and the
old columns == OpNodeTerms_v0's for the same node; F2 (v) the diagram-0 ForLoop's Terminals[] hold its LoopTunnels' OUTER faces
by uid; F3 20 calls leave the LabVIEW handle count flat (+-100); H LabVIEW gone at exit.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c112b_opuid.log -- py -u tools/bench/diag_c112b_opuid.py"""
import hashlib, json, os, shutil, subprocess, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)                # noqa: E702
import gscript as g, allterms as A, bench_prep as bp, protocol                     # noqa: E401,E402
DONOR, OP = g.OP_NODE_TERMS, g.OP_NODE_TERMS_UID
LAB_IN = os.path.join(HERE, "opnodeterms_labels.json")
G_ = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, detail=""):
    G_["pass" if ok else "fail"] += 1
    G_["first"] = G_["first"] or (None if ok else label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)
    return ok


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def props_on(body):
    out = []
    for n, x in enumerate(g.node_labels(OP, body)):
        e, nt = g.node_terms_uid(OP, body, n)
        out.append((int(x["uid"]), [(t["name"], bool(t["is_source"]), int(t["wire"] or 0)) for t in nt]))
    return out


def pidx(uid):
    return [o["uid"] for o in g.report_all(OP, "Property")].index(uid)


def build():
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(DONOR, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(1.0)   # noqa: E702
    if not gate("B1 the copy of OpNodeTerms_v0 is runnable", g.exec_state(OP) == 1, g.exec_state(OP)):
        return None
    body = [i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner"))]
    pn = props_on(body[0]) if len(body) == 1 else []
    pnc = [u for u, ts in pn if ("Wire", True) in [(a, b) for a, b, _w in ts] and ("reference out", True, 0) in ts]
    if not gate("B2 ONE body Property with a 'Wire' source and a BARE 'reference out' (PN_C)", len(body) == 1 and len(pnc) == 1, (body, pn)):
        return None
    pnu = g.build_property(OP, "VI Server:GObject", [("632A813", False)], (2400, 950), diagram_index=body[0])[-1]["uid"]
    g.wire(OP, "Property", pidx(pnc[0]), "reference out", "Property", pidx(pnu), "reference")
    if not gate("B3 PN_U GObject[UID] on PN_C 'reference out' -> ExecState 1", g.exec_state(OP) == 1, (pnu, g.exec_state(OP))):
        return None
    lab, meaning = json.load(open(LAB_IN, encoding="utf-8")), {}
    for out_name, mean in (("UID", "TermUID"), ("error out", "TermUIDErr")):
        t0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
        g.exit_loop(OP, pidx(pnu), [out_name], body[0], node_class="Property")
        new = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in t0]
        if not gate("B4 exit_loop {0!r} -> exactly 1 new LoopTunnel".format(out_name), len(new) == 1, new):
            return None
        before = set(l_ for _i, l_, ind in g.fp_labels(OP) if ind)
        g.set_index_mode(OP, new[0]["i"], 1)
        g.tunnel_indicator(OP, new[0]["i"])
        added = [l_ for _i, l_, ind in g.fp_labels(OP) if ind and l_ not in before]
        if not gate("B5 {0}: one new array indicator".format(mean), len(added) == 1, added):
            return None
        meaning[added[0]] = mean
    g.set_auto_error_handling(OP, False)
    es = g.exec_state(OP)
    if not gate("B6 ExecState 1 before the save", es == 1, es):
        return None
    g.save(OP)
    lab.update(meaning)
    json.dump(lab, open(g.NODE_TERMS_UID_LABELS, "w", encoding="utf-8"), indent=2)
    return gate("B6 OpNodeTermsUid_v0 saved; labels written", os.path.exists(OP), (md5(OP), meaning))


def measure():
    m0 = md5(DONOR)
    T = DONOR
    g.ensure_loaded(T)
    rows = dict((int(r["term_uid"]), r) for r in A.read_terms(T, A.OP_ALLTERMS_V1)[0])
    cls = dict((int(o["uid"]), o["class"]) for o in g.report_all(T, "GObject"))
    bad, n_ent, loop_faces = [], 0, []
    for di in range(len(g.report_all(T, "Diagram"))):
        for ni, x in enumerate(g.node_labels(T, di)):
            echo, ent = g.node_terms_uids(T, di, ni)
            e0, old = g.node_terms_uid(T, di, ni)
            if echo != int(x["uid"]) or [(a["name"], a["is_source"], a["wire"]) for a in ent] != \
                    [(b["name"], b["is_source"], b["wire"]) for b in old]:
                bad.append(("node", di, ni, x["uid"], echo, e0))
            for a in ent:
                n_ent += 1
                r = rows.get(int(a["uid"]))
                if r is None or bool(r["is_source"]) != bool(a["is_source"]) or int(r["wire_uid"] or 0) != int(a["wire"] or 0):
                    bad.append(("entry", di, x["uid"], a["i"], a["uid"], a["uid_err"], r and (r["is_source"], r["wire_uid"])))
                elif cls.get(int(x["uid"])) == "ForLoop" and r["owner_class"] == "LoopTunnel":
                    loop_faces.append((int(x["uid"]), a["i"], int(a["uid"]), int(r["owner_uid"])))
    gate("F1 every entry of every node: node echo, uid in the whole-VI table with the same direction + wire, old columns == "
         "OpNodeTerms_v0 ({0} entries)".format(n_ent), not bad and n_ent > 0, bad[:8])
    gate("F2 (v) a ForLoop's Terminals[] list its LoopTunnels' OUTER faces, each told by its own uid", len(loop_faces) >= 2, loop_faces)
    d0, n0 = next((di, ni) for di in range(len(g.report_all(T, "Diagram"))) for ni, x in enumerate(g.node_labels(T, di))
                  if cls.get(int(x["uid"])) == "ForLoop")
    h0 = bp.labview_handles()
    for _k in range(20):
        g.node_terms_uids(T, d0, n0)
    h1 = bp.labview_handles()
    gate("F3 20 calls leave the LabVIEW handle count flat (+-100)", h0 is not None and h1 is not None and abs(h1 - h0) <= 100, (h0, h1))
    gate("F4 the donor OpNodeTerms_v0.vi md5 is unchanged", md5(DONOR) == m0, (m0, md5(DONOR)))


if __name__ == "__main__":
    print(__doc__, flush=True)
    bp.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    try:
        if build():
            measure()
    except Exception as e:                                                            # noqa: BLE001
        import traceback
        traceback.print_exc()
        gate("the run completed without an unhandled exception", False, str(e)[:300])
    try:
        g.close_panel(OP)
    except Exception:                                                                 # noqa: BLE001
        pass
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("H LabVIEW gone at exit", gone)
    print(protocol.result_line(protocol.make_result(G_["pass"], G_["fail"], G_["first"],
                                                    [{"path": OP, "md5": md5(OP)}] if os.path.exists(OP) else [])))
    sys.exit(0 if not G_["fail"] else 1)
