r"""diag_c100_verbs_build.py - cards 100-2 / 100-4 (PD212(i)5(b), PD213(b)(e)): the LabVIEW-side verbs the display rows need.
RUN 3 = card 100-4 (escalation rung 1 of 100-2). Runs 1/2 (diag_c100_verbs_build.log / _build2.log) built and cold-checked
OpCreateIndicatorNested/ControlNested/ConstValueB/VisibleSet _v0 (kept, not rebuilt) and passed V1/V4; run 2 then died in
THIS harness: term_index() read #9227's owner as ('ForLoop', 1359) and silently used Diagram[0] (_build2.log:81-91).
FOUND FIRST (card 100-4 "check what exists"):
  * a tunnel face is NOT reachable through Traverse('Node')/Nodes[]->Terminals[] (a For loop's Terminals[] made DANGLING
    indicators, gscript.tunnel_indicator docstring, 2026-09-13) - but `OpTunnelInd_v0` (Traverse('LoopTunnel')[i] -> cast ->
    Tunnel.Outside Terminal 6356001 -> Terminal.Create Indicator 6349C02) exists and is FUNCTIONAL (test_optunnelind.log),
    and `OpTunnels_v0` echoes the tunnel uid at a Traverse index. So the tunnel/terminal extension of create_indicator_nested
    is PYTHON ONLY (gscript._tunnel_outer_face / _create_on_tunnel_outer); no op changes.
  * V6: S1 has NO Max & Min (docs/wiki/subvi/D1_s1_copy.json: no 'max(x, y)' terminal). The fixture copier
    (OpMoveByIndex_v0 / stagekit.copy_in) is bound to the ONE Moving-Objects Source file, which the display stage already
    uses for the base (copy_in rows) - so V6 needs a PATH-driven donor. `OpSetIndexMode_v0` carries TWO Open VI References
    (inspect_setindexmode.log: Function #43 <- `vi path`, #316 <- `vi path 2`, the latter an orphan), so OpPrimCopyNested_v0
    is built on a copy of it with the proven c97 retarget (TMSC seeded to VI Server:Diagram) + GObject.Move 632A400 (as
    build_opmoveout.py) + `UID to GObject Reference.vi` (as probe_move_into_v0.py). A Move whose owner is in ANOTHER VI
    duplicates (archive/peer/2026-08-28-copy-nodes-between-vis.md:31-44). Donor = a BYTE COPY of NI
    examples\Comparison\Max and Min.vi -> claudeDev\OpPrimDonor_v0.vi; the Max & Min is FOUND by node label.
PREDICTION (GATE lines): OpPrimCopyNested_v0 D donor ES 1 / X+S retarget ES 1 / O the `vi path 2` OVR found by its input wire /
A assembled ES 1 / V saved / C COLD ES 1 (+ OpTunnelInd_v0, OpTunnels_v0 cold ES 1). Self-test on a never-saved scratch_c100
copy of D1_s1_copy.vi (md5 == S1 at creation, deleted at exit): V1 regression; V1b #9227 owner chain READ = [ForLoop #1359,
Diagram #639], term_index REFUSES a border node, create_indicator_nested(#9234, None) and (#9227,'outer') -> one indicator
on w9215, echo 9227, terminal on Diagram #639; inner face / 'inner' / a wire uid refused; V3 F/T/F read back; V2 on Wait
(ms) #44143; V5 through gscript.create_local_write (stagekit's core; stagekit not imported - guard_bash gates a script that
imports it and calls delete_object/save as a STAGE); V6 Max & Min on Diagram #639, echoes + label + owner; each with
a negative and 20 calls handles flat (+-100); S1 md5 3e3d23ce start and end; LabVIEW gone at exit.
RUN 4 (`--only-v6`): run 3 (27/3) predicted ONE `Max & Min` in the donor and found SIX (_build3.log:7-8) - the lowest uid is
taken now; and Create Control on a WIRED sink made a DANGLING control instead of failing (_build3.log:45) - the verb now reads
the sink first and refuses. Only V2 and the V6 donor/build/cold/self-test run (V1b/V3/V5 are run 3's record); facts ->
facts_c100_verbs2_v6.json.
    py tools/bgrun.py --material --max-min 32 --log tools/bench/diag_c100_verbs_build3.log -- py -u tools/bench/diag_c100_verbs_build.py
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c100_verbs_build4.log -- py -u tools/bench/diag_c100_verbs_build.py --only-v6
"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep                                                                         # noqa: E402
CD = g.CLAUDEDEV
LAB_P = os.path.join(HERE, "facts_c100_oplabels.json")
ONLY_V6 = "--only-v6" in sys.argv          # run 4: V1b..V5 were measured by run 3 (diag_c100_verbs_build3.log)
FACTS_P = os.path.join(HERE, "facts_c100_verbs2_v6.json" if ONLY_V6 else "facts_c100_verbs2.json")
S1 = os.path.join(CD, "D1_s1_copy.vi")
S1_MD5 = "3e3d23ce"
SCR = os.path.join(CD, "scratch_c100_%s.vi" % time.strftime("%H%M%S"))
STD = ("reference", "reference out", "error in (no error)", "error out")
U2G = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to GObject Reference.vi"
DONOR_EX = r"C:\Program Files\National Instruments\LabVIEW 2026\examples\Comparison\Max and Min.vi"
PRIM_DONOR = os.path.join(CD, "OpPrimDonor_v0.vi")
g._run.__defaults__ = (6.0, 180.0)
G, LAB, F = {}, {}, {}


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  GATE %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:400]), flush=True); return bool(ok)  # noqa: E702


def fact(k, v):
    F[k] = v; print("  FACT  %s: %s" % (k, str(v)[:400]), flush=True)                    # noqa: E702


class B(object):
    def __init__(s, donor, out):
        s.op = os.path.join(CD, out)
        if os.path.exists(s.op):
            os.remove(s.op)
        shutil.copyfile(os.path.join(CD, donor), s.op); time.sleep(0.3)                  # noqa: E702
        g.open_panel(s.op); time.sleep(1.0); s.inv0 = set(g.uids(s.op, "Invoke"))        # noqa: E702

    def purge(s):
        junk = [u for u in g.uids(s.op, "Invoke") if u not in s.inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(s.op, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(s.op, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(s.op)

    def idx(s, cls, uid): return [o["uid"] for o in g.report_all(s.op, cls)].index(uid)

    def terms(s, uid):
        for c in range(80):
            nu, rows = g.node_terms_uid(s.op, 0, c)
            if not nu:
                return None, []
            if nu == uid:
                return c, rows
        return None, []

    def pn(s, cls, props, pos):
        r = g.build_property(s.op, cls, props, pos); s.purge(); return int(r[-1]["uid"])  # noqa: E702

    def w(s, su, st, du, dt, sc="Property", dc="Property", branch=False):
        g.wire(s.op, sc, s.idx(sc, su), st, dc, s.idx(dc, du), dt, branch=branch); s.purge()  # noqa: E702

    def panel(s, ind): return set(r["label"] for r in g.panel_wiring(s.op) if r["indicator"] == ind)

    def ind(s, uid, term):
        n, rows = s.terms(uid); t = next(r["i"] for r in rows if r["name"] == term and r["is_source"])  # noqa: E702
        b = s.panel(True); g.create_indicator(s.op, n, t); s.purge(); new = sorted(s.panel(True) - b)  # noqa: E702
        assert len(new) == 1, (term, new)
        return new[0]

    def ctl(s, uid, term):
        n, rows = s.terms(uid)
        t = next(r["i"] for r in rows if r["name"] == term and not r["is_source"])
        b = s.panel(False); g.create_control(s.op, n, t); s.purge(); new = sorted(s.panel(False) - b)  # noqa: E702
        assert len(new) == 1, (term, new)
        return new[0]

    def data(s, uid, src):
        return [r["name"] for r in s.terms(uid)[1] if bool(r["is_source"]) == src and r["name"] not in STD]

    def wired(s, uid, name, src):
        return any(r["wire"] for r in s.terms(uid)[1] if r["name"] == name and bool(r["is_source"]) == src)

    def finish(s, key, lab):
        g.set_auto_error_handling(s.op, False); s.purge(); es = g.exec_state(s.op)       # noqa: E702
        if gate("%s A assembled ExecState 1" % key, es == 1, es):
            g.save(s.op); lab["controls"] = [r["label"] for r in g.panel_wiring(s.op) if not r["indicator"]]  # noqa: E702
            LAB[key] = lab; gate("%s V saved by script" % key, os.path.getsize(s.op) > 0, (os.path.getsize(s.op), md5(s.op)))  # noqa: E702
        else:                                            # card rule: the Error List is READ before any second construction
            try:
                import lv_errorlist
                R = lv_errorlist.read(s.op, out_json=os.path.join(HERE, "facts_c100_errlist_%s.json" % key))
                fact("%s Error List (read before any second construction)" % key, str(R)[:1500])
            except Exception as e:                                                        # noqa: BLE001
                fact("%s Error List read raised" % key, repr(e)[:300])
        try:
            g.close_panel(s.op)
        except Exception:                                                                 # noqa: BLE001
            pass


def retarget(b, key, cls, props, pos):
    """diag_c97_tools_opbuild.retarget:104 verbatim in substance: delete the donor IndexMode PN, seed-retarget the TMSC."""
    nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24)
    props0 = {p["uid"] for p in g.report_all(b.op, "Property")}
    pn_w = next((u for _k, (u, _l, t) in nodes.items() if any(x == "IndexMode" for _i, x, _w in t) and u in props0), None)
    g.delete_object(b.op, "Property", b.idx("Property", pn_w)); g.remove_bad_wires_scripted(b.op); b.purge()  # noqa: E702
    if not gate("%s X donor IndexMode PN #%s deleted, ES 1" % (key, pn_w), g.exec_state(b.op) == 1):
        return None, None
    nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24)
    tm = next(((u, t) for _k, (u, _l, t) in nodes.items() if any(x == "target class" for _i, x, _w in t)
               and any(x == "specific class reference" for _i, x, _w in t)), None)
    W = next(w for _i, x, w in tm[1] if x == "target class")
    p = b.pn(cls, props, pos)
    n, rows = b.terms(p); t_ref = next(r for r in rows if r["name"] == "reference" and not r["is_source"])  # noqa: E702
    _o, seed = g.create_control(b.op, n, t_ref["i"]); b.purge()                           # noqa: E702
    w_seed = next(r["wire"] for r in b.terms(p)[1] if r["i"] == t_ref["i"])
    wires = [o["uid"] for o in g.report_all(b.op, "Wire")]; g.delete_object(b.op, "Wire", wires.index(w_seed))  # noqa: E702
    wires = [o["uid"] for o in g.report_all(b.op, "Wire")]; g.delete_object(b.op, "Wire", wires.index(W))  # noqa: E702
    g.wire_control(b.op, [seed], "Function", b.idx("Function", tm[0]), ["target class"]); b.purge()  # noqa: E702
    b.w(tm[0], "specific class reference", p, "reference", sc="Function")
    ok = gate("%s S %s seed %r -> TMSC #%s -> PN #%s: ES 1" % (key, cls, seed, tm[0], p), g.exec_state(b.op) == 1)
    return (tm[0], p) if ok else (None, None)


def uid_echo(b, tmsc, pos):
    u = b.pn("VI Server:GObject", [("632A813", False)], pos)
    b.w(tmsc, "specific class reference", u, "reference", sc="Function", branch=True)
    return u


def build_nested(key, method):
    b = B("OpSetIndexMode_v0.vi", key + ".vi")
    if not gate("%s D donor copy ES 1" % key, g.exec_state(b.op) == 1):
        return
    tm, pn = retarget(b, key, "VI Server:Node", [("6359000", False)], (900, 450))
    if not tm:
        return
    arr = b.data(pn, True)
    ia = int(g.build_index_array(b.op, (1100, 450))[-1]["uid"]); b.purge()                  # noqa: E702
    b.w(pn, arr[0], ia, "array", dc="IndexArray")
    inv = int(g.build_invoke(b.op, "VI Server:Terminal", method, (1300, 450))[-1]["uid"]); b.inv0.add(inv); b.purge()  # noqa: E702
    b.w(ia, "element", inv, "reference", sc="IndexArray", dc="Invoke")
    b.w(pn, "error out", inv, "error in (no error)", dc="Invoke")
    census = [(r["i"], r["name"], "OUT" if r["is_source"] else "IN", r["wire"]) for r in b.terms(inv)[1]]
    params = [r["name"] for r in b.terms(inv)[1] if not r["is_source"] and not r["wire"] and r["name"] not in STD
              and not r["name"].startswith("Create ")]           # peer c100-verbs-build §1: only the method's own pair
    lab = {"method": method, "census": census, "params": {}}
    for nm in params:
        lab["params"][nm] = b.ctl(inv, nm)
    outs = b.data(inv, True)
    pu = b.pn("VI Server:GObject", [("632A813", False)], (1550, 450))
    b.w(inv, outs[0], pu, "reference", sc="Invoke")
    b.w(inv, "error out", pu, "error in (no error)", sc="Invoke")
    ue = uid_echo(b, tm, (900, 700))
    lab["k"] = b.ctl(ia, "index")
    lab["Created"] = b.ind(pu, "UID"); lab["Err"] = b.ind(pu, "error out")                   # noqa: E702
    lab["UID"] = b.ind(ue, "UID"); lab["UIDErr"] = b.ind(ue, "error out")                    # noqa: E702
    b.finish(key, lab)


# ================================================================ V6: the donor and OpPrimCopyNested_v0
def prim_donor():
    """A BYTE COPY of the NI example (the original is only read); the Max & Min node FOUND by node label."""
    m_ex = md5(DONOR_EX)
    if not os.path.exists(PRIM_DONOR) or md5(PRIM_DONOR) != m_ex:
        shutil.copyfile(DONOR_EX, PRIM_DONOR); time.sleep(0.3)                           # noqa: E702
    gate("V6 D0 OpPrimDonor_v0.vi is a byte copy of examples\\Comparison\\Max and Min.vi", md5(PRIM_DONOR) == m_ex, m_ex)
    diags = g.report_all(PRIM_DONOR, "Diagram")
    hits, seen = [], []
    for d in diags:
        for r in g.node_labels(PRIM_DONOR, d["i"]):
            seen.append((d["uid"], r["uid"], r["label"]))
            if (r["label"] or "").strip() == "Max & Min":
                hits.append((int(r["uid"]), int(d["uid"])))
    fact("V6 donor node labels (diagram, uid, label)", seen)
    cls = dict((int(o["uid"]), o["class"]) for o in g.report_all(PRIM_DONOR, "Node"))
    # run 3 (diag_c100_verbs_build3.log:7-8): the example holds SIX `Max & Min` nodes on Diagram #3 (uids 337 43 116 94
    # 1478 705) - "exactly one" was my wrong prediction. The primitive is polymorphic, so ANY instance is a donor; the
    # LOWEST uid is taken, deterministically, and every hit is recorded.
    if not gate("V6 D1 `Max & Min` found by label in the donor (lowest uid of %d taken)" % len(hits), bool(hits), hits):
        return None
    u, d = min(hits)
    reg = {"Max & Min": {"donor": PRIM_DONOR, "md5": m_ex, "uid": u, "diagram": d, "class": cls.get(u),
                         "source": DONOR_EX}}
    fact("V6 donor registry", reg)
    try:
        g.close_panel(PRIM_DONOR)
    except Exception:                                                                     # noqa: BLE001
        pass
    gate("V6 D2 the NI example's bytes are unchanged", md5(DONOR_EX) == m_ex, m_ex)
    return reg


def build_primcopy(reg):
    key = "OpPrimCopyNested_v0"
    b = B("OpSetIndexMode_v0.vi", key + ".vi")
    if not gate("%s D donor copy ES 1" % key, g.exec_state(b.op) == 1):
        return
    tm, pd = retarget(b, key, "VI Server:Diagram", [("632A813", False)], (900, 450))
    if not tm:
        return
    w2 = int(next((r["wire"] for r in g.panel_wiring(b.op) if r["label"] == "vi path 2"), 0) or 0)
    ovr = None
    for f in sorted(g.uids(b.op, "Function")):
        _n, rows = b.terms(f)
        if w2 and any(r["name"] == "vi path" and not r["is_source"] and r["wire"] == w2 for r in rows):
            ovr = f
            fact("%s OVR #%s terminals" % (key, f), [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows])
            break
    if not gate("%s O the `vi path 2` Open VI Reference found by its input wire w%s" % (key, w2), ovr is not None, ovr):
        return
    mv = int(g.build_invoke(b.op, "VI Server:GObject", "632A400", (1300, 450))[-1]["uid"]); b.inv0.add(mv); b.purge()  # noqa: E702
    census = [(r["i"], r["name"], "OUT" if r["is_source"] else "IN", r["wire"]) for r in b.terms(mv)[1]]
    fact("%s Move 632A400 terminal census" % key, census)
    b.w(tm, "specific class reference", mv, "owner", sc="Function", dc="Invoke", branch=True)
    s0 = set(g.uids(b.op, "SubVI")); g.drop_subvi(b.op, U2G, 0, (1000, 700)); b.purge()      # noqa: E702
    new = sorted(set(g.uids(b.op, "SubVI")) - s0)
    if not gate("%s U `UID to GObject Reference.vi` dropped" % key, len(new) == 1, new):
        return
    u2g = new[0]
    b.w(ovr, "vi reference", u2g, "Owning VI", sc="Function", dc="SubVI", branch=b.wired(ovr, "vi reference", True))
    b.w(u2g, "GObject", mv, "reference", sc="SubVI", dc="Invoke")
    b.w(u2g, "error out", mv, "error in (no error)", sc="SubVI", dc="Invoke")
    lab = {"method": "632A400", "census": census, "ovr_b": ovr, "u2g": u2g, "donors": reg}
    lab["DonorUIDin"] = b.ctl(u2g, "UID")
    lab["position"] = b.ctl(mv, "position")
    lab["duplicate"] = b.ctl(mv, "duplicate") if any(r["name"] == "duplicate" and not r["is_source"]
                                                    for r in b.terms(mv)[1]) else None
    pe = b.pn("VI Server:GObject", [("632A813", False)], (1300, 700))
    b.w(u2g, "GObject", pe, "reference", sc="SubVI", branch=True)
    lab["DonorUID"] = b.ind(pe, "UID"); lab["DonorErr"] = b.ind(pe, "error out")                # noqa: E702
    lab["DiagUID"] = b.ind(pd, "UID"); lab["DiagErr"] = b.ind(pd, "error out")                  # noqa: E702
    lab["Err"] = b.ind(mv, "error out")
    fact("%s labels" % key, lab)
    b.finish(key, lab)


# ================================================================ SELF-TEST on a scratch copy of S1
def hands(): return bench_prep.labview_handles()


def owner_chain(t, uid, hops=4):
    """[(cls, uid), ...] from #uid up to the first Diagram, READ at every hop (OpOwnerChain_v1) - never a fallback."""
    import build_d1_v0 as BD
    chain, u = [], uid
    for _ in range(hops):
        c, o = BD.owner_of(t, u, strict=True)
        chain.append((c, int(o)))
        if c == "Diagram":
            return chain
        u = o
    raise ValueError("#%s: no Diagram within %d owner hops %r" % (uid, hops, chain))


def term_index(t, uid, pred):
    """RUN-2 FAULT FIXED (_build2.log:81-91): a border node (owner = a structure) is in no Diagram.Nodes[], so it is
    REFUSED here instead of being looked up in Diagram[0]."""
    chain = owner_chain(t, uid)
    if len(chain) != 1:
        raise ValueError("#%s is a border node (owner chain %r): use the tunnel route" % (uid, chain))
    c, o = chain[0]
    d = g._uid_index(t, "Diagram", o)
    _u, rows = g.node_terms_uid(t, d, g._node_index(t, d, uid))
    hit = [r for r in rows if pred(r)]
    return (hit[0]["i"] if hit else None), rows, (c, o)


def block(name, fn):
    try:
        return fn()
    except Exception as e:                                                                # noqa: BLE001
        traceback.print_exc(); gate("%s block completed without an exception" % name, False, repr(e)[:300])  # noqa: E702


def v1(T):
    ti, rows, own = term_index(T, 11608, lambda x: x["is_source"] and x["wire"] == 12256)
    r = g.create_indicator_nested(T, 11608, ti)
    fact("V1 #11608 t%s" % ti, r)
    newrow = r["new_panel"][0] if len(r["new_panel"]) == 1 else None
    ok = len(r["new_terminals"]) == 1 and newrow is not None and not r["err"] and newrow["wire"] == 12256
    gate("V1 regression: indicator on #11608 t%s (Diagram #%s) on w12256, echo ok" % (ti, own[1]), ok, r)
    return newrow


def v1b(T):
    ch = owner_chain(T, 9227)
    fact("V1b owner chain of #9227", ch)
    gate("V1b harness READS #9227's owner chain = [ForLoop #1359, Diagram #639] (no Diagram[0] fallback)",
         ch == [("ForLoop", 1359), ("Diagram", 639)], ch)
    try:
        term_index(T, 9227, lambda x: True); neg = False                                  # noqa: E702
    except ValueError as e:
        neg = True; fact("V1b term_index on a border node", str(e))                       # noqa: E702

    def good(r):
        np_ = r["new_panel"]
        if r["err"] or r["echo"] != 9227 or len(np_) != 1 or int(np_[0]["wire"] or 0) != 9215 or len(r["new_terminals"]) != 1:
            return False
        o = owner_chain(T, r["new_terminals"][0])
        fact("V1b new terminal #%s owner chain" % r["new_terminals"][0], o)
        return o == [("Diagram", 639)]
    gate("V1b term_index REFUSES a border node", neg)
    r = g.create_indicator_nested(T, 9234, None)
    fact("V1b create_indicator_nested(#9234, None)", r)
    gate("V1b indicator on #9234 (#9227 outer face): one panel object on w9215, echo 9227, terminal on Diagram #639",
         good(r) and r["face"]["face_term"] == 9234, r)
    r2 = g.create_indicator_nested(T, 9227, "outer")
    fact("V1b create_indicator_nested(#9227, 'outer')", r2)
    gate("V1b alias (#9227, 'outer') -> the same face, same checks", good(r2), r2)
    c0, negs = g.count(T, "ControlTerminal"), []
    for args in ((9230, None), (9227, "inner"), (9215, None)):
        try:
            g.create_indicator_nested(T, *args); negs.append((args, "NOT REFUSED"))      # noqa: E702
        except ValueError as e:
            negs.append((args, str(e)[:120]))
    fact("V1b negatives", negs)
    gate("V1b negatives: inner face #9230, 'inner', a wire uid -> ValueError, nothing created",
         all(m != "NOT REFUSED" for _a, m in negs) and g.count(T, "ControlTerminal") == c0, (c0, negs))
    h0, ok = hands(), 0
    for _ in range(20):
        ok += int(not g.create_indicator_nested(T, 9227, "outer")["err"])
    h1 = hands()
    gate("V1b 20 calls: 20 clean, handles flat (+-100)", ok == 20 and abs(h1 - h0) <= 100, (ok, h0, h1))


def v3(T, newrow):
    u = int(newrow["uid"])
    a = g.set_visible(T, u, False); b_ = g.set_visible(T, u, True); c_ = g.set_visible(T, u, False)  # noqa: E702
    fact("V3 set_visible False/True/False on #%s" % u, (a, b_, c_))
    gate("V3 Visible written and read back (F,T,F), echo ok",
         (a["visible_back"], b_["visible_back"], c_["visible_back"]) == (False, True, False)
         and not (a["err"] or b_["err"] or c_["err"]), (a, b_, c_))
    try:
        g.set_visible(T, 11608, False); neg = False                                       # noqa: E702
    except ValueError:
        neg = True
    gate("V3 negative: a non-panel uid is refused", neg)
    h0 = hands()
    bad = [k for k in range(20) if g.set_visible(T, u, bool(k % 2))["visible_back"] != bool(k % 2)]
    h1 = hands()
    gate("V3 20 calls read back, handles flat", not bad and abs(h1 - h0) <= 100, (bad, h0, h1))


def v2(T):
    tw, rows, ownw = term_index(T, 44143, lambda x: (not x["is_source"]) and x["name"] == "milliseconds to wait")
    wire0 = next((x["wire"] for x in rows if x["i"] == tw), None)
    fact("V2 #44143 owner %r, t%s wire %r" % (ownw, tw, wire0), [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rows])
    # run 3 (_build3.log:45): Create Control on this WIRED sink made a DANGLING control (wire 0, err '') - the verb now
    # READS the sink first and refuses; the negative is that refusal with nothing created.
    c0 = g.count(T, "ControlTerminal")
    try:
        g.create_control_nested(T, 44143, tw); neg = "NOT REFUSED"                        # noqa: E702
    except ValueError as e:
        neg = str(e)
    fact("V2 negative (wired sink)", neg)
    gate("V2 negative: a wired sink -> ValueError before any edit, no control created",
         neg != "NOT REFUSED" and g.count(T, "ControlTerminal") == c0, (neg, c0))

    def cut():
        _t, rr, _o = term_index(T, 44143, lambda x: x["i"] == tw)
        w = next((x["wire"] for x in rr if x["i"] == tw), 0)
        if w:
            wires = [o["uid"] for o in g.report_all(T, "Wire")]
            g.delete_object(T, "Wire", wires.index(w), verify=False)
    cut()
    r = g.create_control_nested(T, 44143, tw, value=100)
    fact("V2 positive (value=100)", r)
    ok2 = len(r["new_terminals"]) == 1 and not r["err"] and len(r["new_panel"]) == 1 and r["new_panel"][0]["wire"]
    if ok2:
        ok2 = owner_chain(T, r["new_terminals"][0]) == [ownw]
        try:
            with g.vi_ref(T) as v:
                fact("V2 created control %r value read back (reported, not gated)" % r["new_panel"][0]["label"],
                     v.GetControlValue(r["new_panel"][0]["label"]))
        except Exception as e:                                                             # noqa: BLE001
            fact("V2 created control value read", repr(e)[:200])
    gate("V2 control created on Wait (ms) #44143 in Diagram #%s, wired, echo ok" % ownw[1], ok2, r)
    h0, made = hands(), 0
    for _ in range(19):
        cut()
        made += len(g.create_control_nested(T, 44143, tw, value=100)["new_terminals"])
    h1 = hands()
    gate("V2 19 more cut+create calls: 19 controls, handles flat", made == 19 and abs(h1 - h0) <= 100, (made, h0, h1))
    return ownw[1]


def v5(T, dest):
    """gscript.create_local_write = the core stagekit.create_local_write binds to (stagekit.py:685-697 adds only the
    exact-label -> panel_index resolution, reproduced here). stagekit is NOT imported: a script that imports it and
    calls delete_object/save is gated as a STAGE by guard_bash (stage_prerun.is_vi_modifying, card chat-N1)."""
    rows = [i for i, x in enumerate(g.panel_wiring(T)) if x["label"].startswith("Force (pN) vs Extension (nm)")]
    fact("V5 panel rows for the plot (stagekit's exact-label resolution needs exactly one)", rows)
    pi = rows[0]
    L0 = g.count(T, "Local")
    try:
        g.create_local_write(T, pi, 44143, (60, 60)); neg = False                         # noqa: E702
    except ValueError as e:
        neg = True; fact("V5 negative", str(e))                                           # noqa: E702
    gate("V5 negative: a non-Diagram destination is refused BEFORE creating", neg and g.count(T, "Local") == L0,
         (neg, L0))
    r = g.create_local_write(T, pi, dest, (60, 60))
    fact("V5 positive", r)
    gate("V5 WRITE local in nested Diagram #%s (owner, all terminals sinks)" % dest,
         r["owner_class"] == "Diagram" and r["owner"] == dest and bool(r["is_source"]) and not any(r["is_source"])
         and not r["err"], r)
    h0, ok = hands(), 0
    for _ in range(20):
        x = g.create_local_write(T, pi, dest, (80, 80))
        ok += int(x["owner"] == dest and not x["err"])
    h1 = hands()
    gate("V5 20 calls all placed, handles flat", ok == 20 and abs(h1 - h0) <= 100, (ok, h0, h1))


def v6(T):
    D = 639
    k0, negs = g.count(T, "Node"), []
    for args in ((D, "No Such Primitive"), (44143, "Max & Min")):
        try:
            g.create_primitive_nested(T, args[0], args[1], (60, 60)); negs.append((args, "NOT REFUSED"))  # noqa: E702
        except ValueError as e:
            negs.append((args, str(e)[:120]))
    fact("V6 negatives", negs)
    gate("V6 negatives: unknown primitive / non-Diagram destination -> ValueError before any edit",
         all(m != "NOT REFUSED" for _a, m in negs) and g.count(T, "Node") == k0, (k0, negs))
    u = g.create_primitive_nested(T, D, "Max & Min", (120, 60))
    rows = g.node_labels(T, g._uid_index(T, "Diagram", D))
    labs = [r["label"] for r in rows if int(r["uid"]) == u]
    fact("V6 placed #%s, label on Diagram #%s" % (u, D), labs)
    gate("V6 `Max & Min` placed in nested Diagram #639 by DONOR COPY: echoes + node delta + owner (verb) and label",
         labs and labs[0].strip() == "Max & Min", (u, labs))
    h0, got = hands(), []
    for k in range(20):
        got.append(g.create_primitive_nested(T, D, "Max & Min", (140 + 5 * k, 90)))
    h1 = hands()
    gate("V6 20 calls: 20 distinct new nodes, handles flat", len(set(got)) == 20 and abs(h1 - h0) <= 100, (len(set(got)), h0, h1))
    fact("V6 scratch ExecState after the unwired copies (not gated)", g.exec_state(T))


def selftest():
    T = SCR
    shutil.copyfile(S1, T); time.sleep(0.3)                                                # noqa: E702
    gate("T0 scratch byte-identical to S1 at creation", md5(T) == md5(S1), md5(T))
    g.open_panel(T); time.sleep(2.0)                                                      # noqa: E702
    fact("T0 scratch ExecState", g.exec_state(T))
    if ONLY_V6:
        block("V2", lambda: v2(T))
        if "OpPrimCopyNested_v0" in LAB:
            block("V6", lambda: v6(T))
        else:
            gate("V6 run (needs OpPrimCopyNested_v0)", False)
        return

    def v4():
        r = g.read_bool_const(T, 25261)
        gate("V4 regression: #25261 = %r, echo ok" % r["value"], isinstance(r["value"], bool) and not r["err"], r)
    block("V4", v4)
    newrow = block("V1", lambda: v1(T))
    block("V1b", lambda: v1b(T))
    if newrow:
        block("V3", lambda: v3(T, newrow))
    else:
        gate("V3 run (needs V1's indicator)", False)
    dest = block("V2", lambda: v2(T)) or 44125
    block("V5", lambda: v5(T, dest))
    if "OpPrimCopyNested_v0" in LAB:
        block("V6", lambda: v6(T))
    else:
        gate("V6 run (needs OpPrimCopyNested_v0)", False)
    fact("T9 scratch ExecState after the edits (not gated)", g.exec_state(T))


def main():
    h0 = None
    try:
        gate("H0 S1 md5 pin at start", md5(S1).startswith(S1_MD5), md5(S1))
        bench_prep.restart_labview(); g.reset(); time.sleep(3); h0 = hands()             # noqa: E702
        fact("handles after restart", h0)
        old = json.load(open(LAB_P, encoding="utf-8")) if os.path.exists(LAB_P) else {}
        done = set(k for k in old if os.path.exists(os.path.join(CD, k + ".vi")))
        fact("ops kept from runs 1-2 (not rebuilt)", sorted(done))
        for k in done:
            LAB[k] = old[k]
        if "OpPrimCopyNested_v0" not in done:
            reg = block("V6 donor", prim_donor)
            if reg:
                block("V6 build", lambda: build_primcopy(reg))
        old.update(LAB); json.dump(old, open(LAB_P, "w"), indent=1)                      # noqa: E702
        g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                # noqa: E702
        stale = os.path.join(CD, "OpPrimCopyNested_v0.vi")
        if "OpPrimCopyNested_v0" not in LAB and os.path.exists(stale):
            os.remove(stale); fact("unsaved OpPrimCopyNested_v0 copy removed (build did not pass)", stale)  # noqa: E702
        for key in ("OpPrimCopyNested_v0", "OpTunnelInd_v0", "OpTunnels_v0", "OpCreateIndicatorNested_v0",
                    "OpCreateControlNested_v0", "OpVisibleSet_v0"):
            p = os.path.join(CD, key + ".vi")
            if os.path.exists(p):
                gate("%s C COLD ExecState 1 (fresh LabVIEW)" % key, g.exec_state(p) == 1, md5(p))
        block("self-test", selftest)
    except Exception as e:                                                                # noqa: BLE001
        traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:200])  # noqa: E702
    finally:
        try:
            fact("handles at end / start / refs", (hands(), h0, g.ref_counts()))
        except Exception:                                                                 # noqa: BLE001
            pass
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
        gate("H LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
        if os.path.exists(SCR):
            os.remove(SCR)
        gate("H scratch deleted", not os.path.exists(SCR), SCR)
        gate("H1 S1 md5 pin at end", md5(S1).startswith(S1_MD5), md5(S1))
        json.dump({"gates": G, "facts": {k: str(v)[:2000] for k, v in F.items()}}, open(FACTS_P, "w"), indent=1)
        bad = [k for k, v in G.items() if not v]
        arts = [{"path": os.path.join(CD, k + ".vi"), "md5": md5(os.path.join(CD, k + ".vi"))}
                for k in ("OpPrimCopyNested_v0",) if os.path.exists(os.path.join(CD, k + ".vi"))]
        if os.path.exists(PRIM_DONOR):
            arts.append({"path": PRIM_DONOR, "md5": md5(PRIM_DONOR)})
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
        sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
