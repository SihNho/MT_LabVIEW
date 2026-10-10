# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a2-4.md
# ---
"""diag_c158_a2_4_mut - card 158-a2-4 (OFFLINE, no LabVIEW, no gate edit): the GATE MUTATION TABLE of steer debate:plan-overall-02
(docs/d1/ring-p5.md:277-284, PD384(d)) on the stored P5-1 graph graph_ring_p5s01_20261009_125622.json (6716c499).
Each mutation is applied to its OWN deep copy in memory (the file is only read; md5 checked before and after). Each mutated copy is
scored as the REAL end against the unmutated graph as BASE and as the SIMULATED end (the prediction "nothing changes"), by CALLING:
  CD  vigraph.computation_diff(build4(G0), build4(Gm))                default mode (the simulator's / pred's cdiff mode)
  CDF vigraph.computation_diff_frame(frame-keyed G0, frame-keyed Gm)   frame-keyed mode (PB's mode)
  TD / D  stagekit.term_identity_gates(base=G0, sim=G0, real=Gm, bind={})   (position keys, chat-T6)
  PB  stagekit.pb_check(S1 frame graph, Gm, G0, pred rows = cdiff(S1, G0) sinks, open rows = their (node, name) pairs)
  E1  stagexec.compare(sim=G0, real=Gm, bind={}) + stagexec.classify_step_diff (fail = BLOCK, warn / log = RECORD)
  INV invcheck (tools/invcheck.py:97 run_inv): file-md5 pins and snapshots, no graph-pair input -> n.a. for every row.
Existing code found (docs/script-writing.md rule 8): no shared graph-mutation helper exists (only an inline `mut` in
tools/bench/selftest_c153_compdiff_poskey.py:51, rename / remove / unwire of one row); the mutation builders below are this card's own.
CLASS RULE (stated once): INVARIANT = the mutation removes or re-points a wire end, or changes a value (M1, M2, M3c, M6);
REPRESENTATION = only names, uids, diagram membership or relay (tunnel) objects change and every computation input keeps its source
through relays (M3r, M3t, M4, M5).
TARGET RULE: eligible lists sorted by uid; targets = first / middle (len//2) / last. COMP = owners not in vigraph.SCHED_OWNER, not
*Constant, with >= 1 wired input and >= 1 wired output; WIRES = wires with exactly 1 source row and a sink row on a COMP node;
M2's new source = the source of the next WIRES entry whose source owner differs from the target's sink and source owners; M3's new
diagram = the smallest frame_diagram uid in the graph that differs from the node's; M4 = the middle owner of each tunnel class;
M6 = owners *Constant with a wired output.
PREDICTION CONTRACT: P1 graph md5 6716c499 before and after; P2 M0 (identity copy) passes every gate; P3 every mutation changed its
copy; P4 >= 3 targets per kind M1..M6; P5 the md table <= 60 lines.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c158_a2_4_mut.log -- py -u tools/bench/diag_c158_a2_4_mut.py"""
import os, sys, copy, json, time, collections                                              # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                        # noqa: E402
import protocol                                                                             # noqa: E402

# ---- INPUTS --------------------------------------------------------------------------------------------------------------------------
GF, GPIN = os.path.join(K.BENCH, "graph_ring_p5s01_20261009_125622.json"), "6716c49948f097b8ac0e1780930bfab1"
OUTJ, OUTM = os.path.join(K.BENCH, "mutation_table_p5.json"), os.path.join(K.BENCH, "mutation_table_p5.md")
OFF = 9000000                       # uid offset for renumbering (above every uid in the graph; checked)
GATES = ("CD", "CDF", "TD", "D", "PB", "E1", "INV")
INV_NA = "n.a.: invcheck.run_inv pins file md5s / snapshots (tools/invcheck.py:7-12, :97); it takes no graph pair"

V, SX = K.pure("vigraph"), K.pure("stagexec")
LAB = K.pure("jev_candidates").node_labels_default()
md5_before = K.md5(GF)
G0 = K.jload(GF)
T0 = G0["terminals"]
ok, res = [], {"graph": {"path": "tools/bench/graph_ring_p5s01_20261009_125622.json", "md5_before": md5_before}, "rows": []}
print("== P1 graph md5 before", md5_before, flush=True)
ok.append(md5_before == GPIN)
maxuid = max(max(int(r["term_uid"]), int(r["owner_uid"]), int(r["wire_uid"] or 0), int(r["frame_diagram"] or 0)) for r in T0)
maxuid = max(maxuid, max(int(o["uid"]) for o in G0["objs"]))
print("   max uid", maxuid, "OFF", OFF, flush=True)
ok.append(maxuid < OFF)


def state0():
    return {"terminals": copy.deepcopy(T0), "objs": copy.deepcopy(G0["objs"]), "loops": copy.deepcopy(G0["loops"]),
            "fs": copy.deepcopy(G0["fs_tunnel_pairs"])}


def build(S, fk):
    return V.build4(S["terminals"], S["objs"], copy.deepcopy(S["loops"]), LAB, S["fs"], frame_keyed=fk)


# ---- eligible targets ------------------------------------------------------------------------------------------------------------
by_owner = collections.OrderedDict()
for r in T0:
    by_owner.setdefault(int(r["owner_uid"]), []).append(r)
ocls = dict((u, rs[0]["owner_class"]) for u, rs in by_owner.items())
wired = lambda rs, src: [r for r in rs if r.get("wire_uid") and bool(r["is_source"]) == src]   # noqa: E731
COMP = sorted(u for u, rs in by_owner.items() if ocls[u] not in V.SCHED_OWNER and not ocls[u].endswith("Constant")
              and all(r.get("term_class") != V.FP_CLASS for r in rs) and wired(rs, False) and wired(rs, True))
CONST = sorted(u for u, rs in by_owner.items() if ocls[u].endswith("Constant") and wired(rs, True))
WR = collections.defaultdict(list)
for r in T0:
    if r.get("wire_uid"):
        WR[int(r["wire_uid"])].append(r)
WIRES = sorted(w for w, rs in WR.items() if len([r for r in rs if r["is_source"]]) == 1
               and any(not r["is_source"] and int(r["owner_uid"]) in set(COMP) for r in rs))
TUN = dict((c, sorted(u for u in by_owner if ocls[u] == c)) for c in ("LoopTunnel", "Tunnel", "SelectorTunnel", "FlatSequenceInnerTunnel",
                                                                          "FlatSequenceOuterTunnel"))
DIAGS = sorted(set(int(r["frame_diagram"]) for r in T0 if r.get("frame_diagram")))
fml = lambda L: [L[0], L[len(L) // 2], L[-1]]                                                 # noqa: E731
print("== eligible: COMP {0} CONST {1} WIRES {2} TUN {3} DIAGS {4}".format(len(COMP), len(CONST), len(WIRES),
      dict((c, len(v)) for c, v in TUN.items()), len(DIAGS)), flush=True)
src_of = lambda w: next(r for r in WR[w] if r["is_source"])                                  # noqa: E731
sink_on_comp = lambda w: next(r for r in WR[w] if not r["is_source"] and int(r["owner_uid"]) in set(COMP))   # noqa: E731


def diag_of(u):
    return collections.Counter(int(r["frame_diagram"]) for r in by_owner[u]).most_common(1)[0][0]


def new_diag(u):
    return next(d for d in DIAGS if d != diag_of(u))


def owner_val(o, d):
    return str(d) if isinstance(o.get("owner"), str) else d


# ---- mutations: each returns (state, description) on a fresh copy -----------------------------------------------------------------
def m_drop(w):
    S = state0()
    for r in S["terminals"]:
        if int(r.get("wire_uid") or 0) == w:
            r["wire_uid"] = 0
    return S, "wire {0} ({1} -> {2}) deleted".format(w, src_of(w)["owner_uid"], sink_on_comp(w)["owner_uid"])


def m_resource(w):
    sk, s0 = sink_on_comp(w), src_of(w)
    i = WIRES.index(w)
    w2 = next(x for x in WIRES[i + 1:] + WIRES[:i] if int(src_of(x)["owner_uid"]) not in (int(sk["owner_uid"]), int(s0["owner_uid"])))
    S = state0()
    for r in S["terminals"]:
        if r["term_uid"] == sk["term_uid"]:
            r["wire_uid"] = w2
    if len([r for r in WR[w] if not r["is_source"]]) == 1:
        for r in S["terminals"]:
            if r["term_uid"] == s0["term_uid"] and int(r.get("wire_uid") or 0) == w:
                r["wire_uid"] = 0
    return S, "sink t{0} on #{1} moved from wire {2} (src #{3}) to wire {4} (src #{5})".format(
        sk["term_uid"], sk["owner_uid"], w, s0["owner_uid"], w2, src_of(w2)["owner_uid"])


def _move(S, u, d):
    terms = set(r["term_uid"] for r in by_owner[u])
    for r in S["terminals"]:
        if int(r["owner_uid"]) == u:
            r["frame_diagram"] = d
    for o in S["objs"]:
        if int(o["uid"]) == u:
            o["owner"] = owner_val(o, d)
    return terms


def m_move(u, mode):
    S, d0, d = state0(), diag_of(u), new_diag(u)
    _move(S, u, d)
    if mode == "c":
        ws = set(int(r["wire_uid"]) for r in by_owner[u] if r.get("wire_uid"))
        for r in S["terminals"]:
            if int(r.get("wire_uid") or 0) in ws:
                r["wire_uid"] = 0
        return S, "#{0} {1} diagram {2} -> {3}; its {4} wires deleted".format(u, ocls[u], d0, d, len(ws))
    if mode == "t":
        nu = OFF + 500000 + u * 10
        k = 0
        for r in [x for x in S["terminals"] if int(x["owner_uid"]) == u and x.get("wire_uid")]:
            k += 1
            T, NW = nu + 3 * k, nu + 3 * k + 1
            w = r["wire_uid"]
            outer = {"term_uid": T + 1, "term_name": r["term_name"], "is_source": bool(r["is_source"]), "wire_uid": w, "owner_uid": T,
                     "owner_class": "Tunnel", "frame_diagram": d0, "term_class": "OuterTerminal"}
            inner = {"term_uid": T + 2, "term_name": r["term_name"], "is_source": not r["is_source"], "wire_uid": NW, "owner_uid": T,
                     "owner_class": "Tunnel", "frame_diagram": d, "term_class": "InnerTerminal"}
            S["terminals"] += [outer, inner]
            S["objs"].append({"uid": T, "class": "Tunnel", "pos": [0, 0], "owner": owner_val(S["objs"][0], d)})
            r["wire_uid"] = NW
        return S, "#{0} {1} diagram {2} -> {3}; its {4} wires relayed through {4} new Tunnels".format(u, ocls[u], d0, d, k)
    return S, "#{0} {1} diagram {2} -> {3}; wires untouched".format(u, ocls[u], d0, d)


def m_rename(u):
    S = state0()
    for r in S["terminals"]:
        if int(r["owner_uid"]) == u:
            r["term_name"] = str(r["term_name"] or "") + " ~renamed"
    return S, "{0} #{1}: {2} term names + ' ~renamed'".format(ocls[u], u, len(by_owner[u]))


def m_renum_node(u):
    S, terms = state0(), set(int(r["term_uid"]) for r in by_owner[u])
    ids = terms | {u}
    for r in S["terminals"]:
        if int(r["owner_uid"]) == u:
            r["owner_uid"] = u + OFF
        if int(r["term_uid"]) in terms:
            r["term_uid"] = int(r["term_uid"]) + OFF
    for o in S["objs"]:
        if int(o["uid"]) in ids:
            o["uid"] = int(o["uid"]) + OFF
        if str(o.get("owner")) == str(u):
            o["owner"] = owner_val(o, u + OFF)
    return S, "#{0} {1}: owner uid and its {2} term uids + {3}".format(u, ocls[u], len(terms), OFF)


def m_renum_wire(w):
    S = state0()
    for r in S["terminals"]:
        if int(r.get("wire_uid") or 0) == w:
            r["wire_uid"] = w + OFF
    for o in S["objs"]:
        if int(o["uid"]) == w:
            o["uid"] = w + OFF
    return S, "wire uid {0} -> {1}".format(w, w + OFF)


def m_renum_all():
    S = state0()
    f = lambda v: (int(v) + OFF) if str(v).lstrip("-").isdigit() and int(v) > 0 else v       # noqa: E731
    for r in S["terminals"]:
        for c in ("term_uid", "owner_uid", "wire_uid", "frame_diagram"):
            if r.get(c):
                r[c] = f(r[c])
    for o in S["objs"]:
        o["uid"] = f(o["uid"])
        if o.get("owner") not in (None, ""):
            o["owner"] = owner_val(o, f(o["owner"]))
    for lp in S["loops"]:
        lp["loop_uid"] = f(lp["loop_uid"])
        lp["right_uids"] = [f(x) for x in lp.get("right_uids") or []]
        lp["left_of"] = dict((str(f(k)), [f(x) for x in (v if isinstance(v, list) else [v])]) for k, v in (lp.get("left_of") or {}).items())
    for p in S["fs"]:
        for c in ("uid", "term_a", "term_b", "wire_a", "wire_b", "uid_back"):
            if p.get(c):
                p[c] = f(p[c])
    return S, "every uid (terms, owners, wires, diagrams, objs, loops, fs pairs) + {0}".format(OFF)


def m_const(u):
    S = state0()
    for r in S["terminals"]:
        if int(r["owner_uid"]) == u:
            r["value"] = "MUTATED"
    for o in S["objs"]:
        if int(o["uid"]) == u:
            o["value"] = "MUTATED"
    return S, "{0} #{1}: value -> 'MUTATED' (new `value` key; the graph has no value column)".format(ocls[u], u)


CASES = [("M0", "identity copy", "control", lambda: (state0(), "no change"))]
CASES += [("M1", "wire dropped", "invariant", (lambda w: lambda: m_drop(w))(w)) for w in fml(WIRES)]
CASES += [("M2", "wire re-sourced", "invariant", (lambda w: lambda: m_resource(w))(w)) for w in fml(WIRES)]
CASES += [("M3c", "node moved, wires broken", "invariant", (lambda u: lambda: m_move(u, "c"))(u)) for u in fml(COMP)]
CASES += [("M3r", "node moved, wires kept", "representation", (lambda u: lambda: m_move(u, "r"))(u)) for u in fml(COMP)]
CASES += [("M3t", "node moved, relayed by new tunnels", "representation", (lambda u: lambda: m_move(u, "t"))(u)) for u in fml(COMP)]
CASES += [("M4", "tunnel renamed", "representation", (lambda u: lambda: m_rename(u))(TUN[c][len(TUN[c]) // 2])) for c in TUN if TUN[c]]
CASES += [("M5n", "node uids renumbered", "representation", (lambda u: lambda: m_renum_node(u))(u)) for u in fml(COMP)]
CASES += [("M5w", "wire uid renumbered", "representation", (lambda w: lambda: m_renum_wire(w))(w)) for w in fml(WIRES)]
CASES += [("M5a", "all uids renumbered", "representation", m_renum_all)]
CASES += [("M6", "constant value changed", "invariant", (lambda u: lambda: m_const(u))(u)) for u in fml(CONST)]

# ---- reference graphs (built once) -------------------------------------------------------------------------------------------------
t0 = time.time()
S0 = state0()
GA0, GF0 = build(S0, False), build(S0, True)
S1f = K.s1_frame_graph(LAB)
cd_s1 = V.computation_diff_frame(S1f, GF0)
PRED = sorted(str(y["sink"]) for y in cd_s1["rows"])
OPEN = [{"node": n, "term": t} for n, t in sorted(set((int(s.split("|", 1)[0]), s.split("|")[2]) for s in PRED))]
print("== reference: cdiff(S1, G0) frame-keyed rows {0}, open pairs {1}; built in {2:.1f}s".format(len(PRED), len(OPEN), time.time() - t0), flush=True)
BIND = {"term": {}, "obj": {}}


def score(S):
    g, det = {}, {}
    GA, GFm = build(S, False), build(S, True)
    for tag, A, B in (("CD", GA0, GA), ("CDF", GF0, GFm)):
        c = V.computation_diff(A, B)
        n = (len(c["rows"]), len(c["computation_nodes_added"]), len(c["computation_nodes_removed"]))
        g[tag] = "BLOCK" if any(n) else "PASS"
        det[tag] = {"rows": n[0], "nodes_added": n[1], "nodes_removed": n[2], "first": [y["sink"] for y in c["rows"][:2]]}
    ti = K.term_identity_gates(T0, T0, S["terminals"], bind=BIND)
    g["TD"] = "PASS" if ti["td_ok"] else "BLOCK"
    det["TD"] = {"unwired": len(ti["unwired"]), "lost": len(ti["lost"]), "moved": len(ti["moved"]), "gone": len(ti["gone"]), "extra": len(ti["extra"])}
    g["D"] = "PASS" if ti["d_ok"] else "BLOCK"
    det["D"] = {"d_new": ti["d_new"], "sim_new": len(ti["sim_new"]), "d_lost": ti["d_lost"], "sim_lost": len(ti["sim_lost_w"]), "renames": len(ti["renames"])}
    pb = K.pb_check(S1f, GFm, GF0, PRED, OPEN, (), V)
    g["PB"] = "PASS" if pb["ok"] else "BLOCK"
    det["PB"] = {"extra": [str(x) for x in pb["extra"][:3]], "missing": [str(x) for x in pb["missing"][:3]], "n_extra": len(pb["extra"]),
                 "n_missing": len(pb["missing"])}
    d = SX.compare(T0, S["terminals"], BIND)
    cl = SX.classify_step_diff({"actions": []}, 0, d)[0] if d["n"] else "pass"
    g["E1"] = {"fail": "BLOCK", "warn": "RECORD", "log": "RECORD", "pass": "PASS"}[cl]
    det["E1"] = dict((k, len(d[k])) for k in ("only_sim_terms", "only_real_terms", "only_sim_edges", "only_real_edges", "dangling_sim_only",
                                              "dangling_real_only", "unbound"))
    det["E1"]["class"] = cl
    g["INV"] = "n.a."
    net = "BLOCK" if "BLOCK" in g.values() else ("RECORD" if "RECORD" in g.values() else "PASS")
    return g, det, net


cnt = collections.Counter()
for i, (kind, what, cls, fn) in enumerate(CASES):
    t1 = time.time()
    S, desc = fn()
    changed = (S["terminals"] != T0 or S["objs"] != G0["objs"] or S["loops"] != G0["loops"] or S["fs"] != G0["fs_tunnel_pairs"])
    g, det, net = score(S)
    rid = "{0}.{1}".format(kind, cnt[kind])
    cnt[kind] += 1
    row = {"id": rid, "kind": kind, "mutation": what, "target": desc, "class": cls, "changed": changed, "gates": g, "net": net, "detail": det}
    res["rows"].append(row)
    print("ROW {0:6s} {1:15s} {2:6s} {3} | {4} | {5}".format(rid, cls, net, " ".join("{0}={1}".format(k, g[k]) for k in GATES), desc,
          json.dumps(det, default=str)[:600]), flush=True)
    print("    {0:.1f}s".format(time.time() - t1), flush=True)
    if kind == "M0":
        ok.append(net == "PASS" and all(g[k] in ("PASS", "n.a.") for k in GATES))
        print("== P2 M0 passes every gate:", ok[-1], flush=True)
    else:
        ok.append(changed)

kinds = collections.Counter(r["kind"][:2] for r in res["rows"])
ok.append(all(kinds[k] >= 3 for k in ("M1", "M2", "M3", "M4", "M5", "M6")))
print("== P4 targets per kind", dict(kinds), ok[-1], flush=True)
gap = [r["id"] for r in res["rows"] if r["class"] == "invariant" and all(v in ("PASS", "n.a.", "RECORD") for v in r["gates"].values())]
fblock = [r["id"] for r in res["rows"] if r["class"] == "representation" and r["net"] == "BLOCK"]
res.update({"class_rule": "INVARIANT = removes or re-points a wire end, or changes a value (M1, M2, M3c, M6); REPRESENTATION = only names, uids, "
            "diagram membership or relay objects change, every computation input keeps its source through relays (M3r, M3t, M4, M5)",
            "target_rule": "eligible lists sorted by uid; first / middle (len//2) / last; M4 = middle owner of each tunnel class",
            "gates": {"CD": "vigraph.computation_diff default mode", "CDF": "vigraph.computation_diff_frame", "TD": "stagekit.term_identity_gates td_ok",
                      "D": "stagekit.term_identity_gates d_ok", "PB": "stagekit.pb_check", "E1": "stagexec.compare + classify_step_diff",
                      "INV": INV_NA},
            "reference": {"pred_rows": len(PRED), "open_pairs": len(OPEN)}, "list_gaps_invariant_passing": gap, "list_false_blocks_representation": fblock,
            "per_gate_block": dict((k, dict((c, sum(1 for r in res["rows"] if r["class"] == c and r["gates"][k] == "BLOCK"))
                                            for c in ("invariant", "representation", "control"))) for k in GATES)})
# ---- the md table ---------------------------------------------------------------------------------------------------------------------
L = ["---", "type: facts", "status: current", "date: 2026-10-10", "card: 158-a2-4", "---",
     "# Gate mutation table on graph 6716c499 (steer debate:plan-overall-02, PD384(d)) - made by `diag_c158_a2_4_mut.py`, every row in the json",
     "Class rule: " + res["class_rule"] + ". Real end = mutated copy; base = sim end = the unmutated graph. RECORD = E1 warn/log class (not a block).",
     "Gates: CD/CDF vigraph.computation_diff default / frame-keyed; TD, D stagekit.term_identity_gates; PB stagekit.pb_check (S1 vs real, pred = cdiff(S1, G0) "
     "{0} rows); E1 stagexec.compare; INV {1}.".format(len(PRED), INV_NA), "",
     "| id | mutation | target | class | " + " | ".join(GATES) + " | net |", "|" + "---|" * (len(GATES) + 5)]
for r in res["rows"]:
    L.append("| {0} | {1} | {2} | {3} | {4} | {5} |".format(r["id"], r["mutation"], r["target"][:70], r["class"][:3] if r["class"] != "control" else "ctl",
                                                         " | ".join(r["gates"][k] for k in GATES), r["net"]))
L += ["", "(1) INVARIANT rows passing every gate (gaps): " + (", ".join(gap) or "none"),
      "(2) REPRESENTATION rows that block (false blocks): " + (", ".join(fblock) or "none"),
      "Blocks per gate (inv / rep): " + "; ".join("{0} {1}/{2}".format(k, v["invariant"], v["representation"]) for k, v in res["per_gate_block"].items())]
with open(OUTM, "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
ok.append(len(L) <= 60)
print("== P5 md lines", len(L), ok[-1], flush=True)
res["md5_after"] = K.md5(GF)
ok.append(res["md5_after"] == GPIN)
print("== P1 graph md5 after", res["md5_after"], ok[-1], flush=True)
with open(OUTJ, "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, default=str)
print("GAPS", gap, "| FALSE BLOCKS", fblock, flush=True)
print(protocol.result_line({"status": "PASS" if all(ok) else "FAIL", "gates": {"pass": sum(ok), "fail": len(ok) - sum(ok)},
                            "first_fail": None if all(ok) else "prediction contract P1-P5 (see log)",
                            "artefacts": [{"path": "tools/bench/mutation_table_p5.json", "md5": K.md5(OUTJ)},
                                          {"path": "tools/bench/mutation_table_p5.md", "md5": K.md5(OUTM)}]}), flush=True)
sys.exit(0 if all(ok) else 1)
