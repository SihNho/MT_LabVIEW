r"""diag_c88_p2rbw - card 88-1 parts (A)+(B). A DIAGNOSTIC: measures, decides nothing, saves nothing.
    MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/diag_c88_p2rbw.log -- py -u tools/bench/diag_c88_p2rbw.py
PRIOR ART (read first, nothing new built): stagekit.Stage (pins, restart, dated copies, hygiene), stagekit.address +
cfw_second_pass's body (stagekit.py:713,848 - called here WITH objs so a SelectorTunnel OUTER face addresses; the
recipe's :90 blanks owner/term class, PD194(a)), wiki_build.read_live (terminals+term_class+objs), allterms.read_terms,
stage_d1_l2a1.py:112-118 (RBW on a scratch), errorlist_check.open_diagram/make_on_item/compare + lv_errorlist.read.
The BED is only byte-COPIED: (A) runs on copy D1_l2a1_scratch_88_p2_*, (B) on D1_l2a1_scratch_88_*_rbw; both deleted.
PREDICTION (A): desk (sim step_46) = each of the 5 sinks has ONE source, the new SR-L / tunnel inner (real uids by the
stage BINDING, stage_d1_l2a1.json:795); live: sole source == planned, sole sink == planned SelectorTunnel OuterTerminal,
ordered idempotent re-connect wire_delta 0 and `Is Broken?` False. (B): RBW deletes 29 wires (stage_d1_l2a1.json:865);
the Error List is then read in full (items == window N). No prediction on which items survive: that is the measurement."""
import collections, json, os, subprocess, sys, time                                 # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, allterms as AT, wiki_build as W, errorlist_check as EC  # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_l2_a1_20260925_235224.vi"), "51d9b8a3af5b4240cdc2ad193d9b4f41"
SIM = os.path.join(K.BENCH, "sim", "l2a1")
P = J(SIM, "plan_l2a1.json"); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); S46 = J(SIM, "step_46_wire.json")  # noqa: E702
ST = S46.get("state", S46)
BIND = {-1: 10850, -2: 25240, -9: 25339, -10: 25344, -17: 25371, -18: 25382, -25: 25422, -29: 25428}  # stage_d1_l2a1.json:795
ROWS = (("sr1_L0", "sr1_L0"), ("sr2_L0", "sr2_L0"), ("sr3_L0", "sr3_L0"), ("tun1", "tun1_in"), ("tun2", "tun2_in"))
STAMP = time.strftime("%Y%m%d_%H%M%S")


def desk(s):
    s.head("[A0] DESK CHECK from tools/bench/sim/l2a1/step_46_wire.json (final simulated state)")
    T, A, out = ST["terminals"], dict((a["id"], a) for a in P["actions"]), {}
    for row, aid in ROWS:
        a = A[aid]; st = a["dst"]["term_uid"]; sk = [r for r in T if r["term_uid"] == st]   # noqa: E702
        w = sk[0]["wire_uid"] if len(sk) == 1 else None
        src = [r for r in T if w and r["wire_uid"] == w and r["is_source"]]
        snk = [r for r in T if w and r["wire_uid"] == w and not r["is_source"]]
        out[row] = {"sink_term": st, "sink_owner": a["dst"]["uid"], "src_sym": a["src"], "sim_src_owner": [r["owner_uid"] for r in src],
                    "planned_src_owner": BIND.get(src[0]["owner_uid"]) if len(src) == 1 else None,
                    "src_class": [r["owner_class"] for r in src], "sink_class": [(r["owner_class"], r["term_class"]) for r in snk]}
        s.fact("DESK {0}: plan {1} src {2} -> sim source owner {3} {4} (real #{5}); sink #{6} term {7} {8}; sinks on net {9}".format(
            row, aid, a["src"], out[row]["sim_src_owner"], out[row]["src_class"], out[row]["planned_src_owner"], a["dst"]["uid"], st,
            out[row]["sink_class"], len(snk)))
        s.gate("A0 {0} simulated net has exactly one source and one sink".format(row), len(src) == 1 and len(snk) == 1)
    return out


def net(T, w):
    return [r for r in T if w and r["wire_uid"] == w]


def partA(s, D):
    s.head("[A] P2 READ on the byte copy of the bed (work copy, deleted at close)")
    F = K.mod("build_opconnectfromwire_v0"); lab = J(F.MAP_OUT)                                 # noqa: E702
    lv = W.read_live(s.work, fs_pairs=BASE["fs_tunnel_pairs"]); T = lv["terminals"]             # noqa: E702
    s.fact("LIVE READ {0}".format(lv["secs"])); s.R["p2"] = {}                                  # noqa: E702
    for row, _aid in ROWS:
        d = D[row]; sk = [r for r in T if r["term_uid"] == d["sink_term"]]                     # noqa: E702
        w = int(sk[0]["wire_uid"] or 0) if len(sk) == 1 else 0
        nt = net(T, w); src = [r for r in nt if r["is_source"]]; snk = [r for r in nt if not r["is_source"]]  # noqa: E702
        so = [(r["owner_class"], r["owner_uid"], r["term_uid"]) for r in src]
        sn = [(r["owner_class"], r["owner_uid"], r["term_uid"], r.get("term_class")) for r in snk]
        src_ok = len(src) == 1 and src[0]["owner_uid"] == d["planned_src_owner"]
        snk_ok = len(snk) == 1 and snk[0]["term_uid"] == d["sink_term"] and snk[0]["owner_uid"] == d["sink_owner"] \
            and snk[0]["owner_class"] == "SelectorTunnel" and snk[0].get("term_class") == "OuterTerminal"
        s.fact("P2 {0}: wire w{1}; sources {2}; sinks {3}; planned src #{4} sink #{5}/t{6}".format(
            row, w, so, sn, d["planned_src_owner"], d["sink_owner"], d["sink_term"]))
        s.gate("A1 {0} sole source == planned #{1}".format(row, d["planned_src_owner"]), src_ok, so)
        s.gate("A2 {0} sole sink == planned SelectorTunnel #{1} OuterTerminal t{2}".format(row, d["sink_owner"], d["sink_term"]), snk_ok, sn)
        end = {"uid": d["sink_owner"], "term": "", "diagram": 23166, "owner_class": "SelectorTunnel", "term_class": "OuterTerminal",
               "verify_term_uid": d["sink_term"]}

        def again(e=end, ww=w, su=d["planned_src_owner"], rid=row):
            (dd, dn, dt), how = s.address(e, False, objs=lv["objs"]); s.fact("{0} sink addressed: D[{1}].N[{2}].t{3} via {4}".format(rid, dd, dn, dt, how))  # noqa: E702
            hit = [x for x in F.wire_source_owner(s.work, ww, n=8) if x.get("owner_uid") == su and x.get("is_source")]
            s.node_mark("2nd " + rid); dw, _es, err, sub = F.connect_from_wire(s.work, ww, int(hit[0]["i"]), dd, dn, dt, lab)  # noqa: E702
            s.junk_purge("2nd purge " + rid, hints=[dd, 0])
            return {"is_broken": (sub or {}).get("Is Broken?"), "sink_wire_uid": (sub or {}).get("UID 2"), "err": err, "wire_delta_op": dw}
        r = s.expect_is_broken_false("A3 " + row, lambda f=again, rid=row: s.safe("2nd pass " + rid, f, {})[0], wire_uid=w)
        s.R["p2"][row] = {"wire": w, "sources": so, "sinks": sn, "src_ok": src_ok, "sink_ok": snk_ok, "wire_delta": r["wire_delta"], "is_broken": r["is_broken"]}
    extra = {"SR_R_inner": [BIND[-1], BIND[-9], BIND[-17]], "node_9703": [9703]}          # review 2026-09-26-c87-errorlist-extras §1/§2
    for tag, owners in extra.items():
        for r in [x for x in T if x["owner_uid"] in owners]:
            nt = net(T, int(r["wire_uid"] or 0))
            s.fact("EXTRA {0} #{1} t{2} {3!r} src={4} wire w{5}: net sources {6}; net sinks {7}".format(
                tag, r["owner_uid"], r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"],
                [(x["owner_class"], x["owner_uid"], x["term_name"]) for x in nt if x["is_source"]],
                [(x["owner_class"], x["owner_uid"], x["term_name"]) for x in nt if not x["is_source"]]))
    s.drop_scratch(s.work, "A-H4")


def partB(s):
    s.head("[B] RBW on a SCRATCH byte copy, then the Error List of that in-memory scratch (never saved)")
    rb = s.scratch("rbw", BED); rows0 = AT.read_terms(rb, AT.OP_ALLTERMS_V1)[0]; w0 = set(AT.all_wire_uids(rb)[0])  # noqa: E702
    s.broken_wire_count(target=rb, tag="RBW"); gone = sorted(w0 - set(AT.all_wire_uids(rb)[0]))                     # noqa: E702
    s.fact("RBW deleted {0} wire(s): {1}".format(len(gone), gone))
    for w in gone:
        s.fact("RBW w{0} ends: {1}".format(w, [(r["owner_class"], r["owner_uid"], r["term_name"], r["term_uid"], "src" if r["is_source"] else "snk")
                                               for r in rows0 if r["wire_uid"] == w] or "NONE (termless wire)"))
    EC._lv_imports(); E = EC.E; R = {"errors": [], "gui_acts_outer": []}                   # noqa: E702
    g.open_panel(rb); time.sleep(1.0); R["bd"] = EC.open_diagram(rb, R)                   # noqa: E702
    raw = os.path.join(K.BENCH, "errorlist_rbw_l2a1_88_{0}_raw.json".format(STAMP))
    r = E.read(rb, raw, log=lambda m: print(m, flush=True), on_item=EC.make_on_item(rb, R))
    items = r.get("items") or []; n = r.get("n_reported")                                   # noqa: E702
    s.gate("B1 Error List read complete: items {0} == window N {1}".format(len(items), n), n is not None and len(items) == n, r.get("errors"))
    sp, pp, plan = EC.plan_for_bed(BED); extra, _miss, usage = EC.compare(items, [], EC.derive_expected(plan) if plan else [])  # noqa: E702
    cls = collections.Counter(i.get("raw") for i in items)
    for k, v in sorted(cls.items(), key=lambda kv: -kv[1]):
        s.fact("B CLASS x{0}: {1!r}".format(v, k))
    txt = [EC.norm("{0} {1}".format(i.get("raw"), i.get("detail"))) for i in items]
    pres = {"polymorphic": sum("polymorphicterminalcannotacceptthisdatatype" in t for t in txt),
            "not_connected_to_anything": sum("isnotconnectedtoanything" in t for t in txt),
            "less_right_shift_register": sum("less" in t and "rightshiftregister" in t for t in txt)}
    s.fact("B PRESENCE after RBW: {0} ; checker extra {1} ; usage {2}".format(pres, extra, usage))
    out = os.path.join(K.BENCH, "errorlist_rbw_l2a1_88_{0}.json".format(STAMP))
    json.dump({"scratch": rb, "rbw_deleted": gone, "items": items, "n_reported": n, "classes": cls, "presence": pres, "extra": extra,
               "usage": usage, "gui": R, "closed_with_esc": r.get("closed_with_esc")}, open(out, "w", encoding="utf-8"), indent=1, default=str)
    s.R["errorlist_rbw"] = out
    s.drop_scratch(rb, "B-H4")


def body(s):
    print(__doc__, flush=True)
    D = desk(s)
    s.start(); s.discard_work()                                                                  # noqa: E702
    for tag, fn in (("A", lambda: partA(s, D)), ("B", lambda: partB(s))):
        _r, e = s.safe("part " + tag, fn)
        s.gate("{0}9 part {0} ran to its end".format(tag), not e, e)


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "D1_l2a1_scratch_88", work_name="D1_l2a1_scratch_88_p2_{0}.vi".format(STAMP), preload=False,
                 deadline_min=40, out_json=os.path.join(K.BENCH, "p2check_l2a1_88.json"), task="card 88-1 A+B")
    rc = K.run(body, st)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)  # noqa: E702
    print("LabVIEW gone at exit:", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), flush=True)
    sys.exit(rc)
