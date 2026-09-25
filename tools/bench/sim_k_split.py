r"""sim_k_split - card 79-3 S0: stage K (docs/d1-loop12-17-split-plan.md Pre-decided 177) as a stageplan/1 file, SIMULATED
on the live S4 base (tools/stagesim.py) and FINALIZED. PURE PYTHON, no LabVIEW. Writes tools/bench/stageplan_k_split.json,
tools/bench/plan_k_split.json (+ tools/bench/sim/k_split/step_NN_*.json) and tools/bench/plan_k_rows.json (the recipe's
`decisions` rows for tools/stage_prerun.py X2-X5, one per compiled real op).
WHAT EXISTED FIRST: sim_l7_split.py (same shape: RULE-CHAIN-S1 rows from jev_candidates.s1_chains, tunnel groups
tunnel+in+out, moves with L7's offsets); k_facts_79.json (#5058's 16 terminals, their other ends and tags, the 1.2 SR
pairs); k_contract_79.json (live base graph + loop table, the 2 indicators, the 6 original IndexModes). EVERY row is READ
from those files by the 177 rule that owns it - no uid or terminal name is typed here except the rule tags:
  (a) move #5058 -> the body of the 1.2 loop that holds no plan node yet (Pre-decided 163: #23166 of #10170, from the
      contract's diagram tree);   (b) the S1 chain of #5058 (s1_chains) -> ONE new SR pair: out->R, L->in, init;
  (c) every 'from-tunnel' row -> a NEW input tunnel fed from the SAME FSIT source term, IndexMode = original's;
  (d) the contract's 2 indicators move first, then wire from t8;   (e) every other wired terminal stays OPEN.
PREDICTION (run 3, card 79-4, Pre-decided 178(b)(c)): A0 is an OWNERSHIP check (#23166 owned by #10170, read from the
dump's structure->diagram order, the same reader returning L7's pair; #5058 owned by #23166 at the end); base cdiff == the 2
carried L7 rows; every action applies on a MEASURED op model; the end cdiff rows are EXPLAINED by the (e) rows plus the 2
carried L7 rows; t3 is credited by END-GRAPH evidence (unwired, #5796's right inner sourceless), no (e) terminal wired or
END-sourcing an end row; the negative control (fake t3 -> #2626 'array' on a copy) FAILS P3; end rows == 178(c)'s 10;
plan FINAL; 11 wired rows (1 init + 2 chain + 6 tunnel + 2 indicator), 0 Jev candidates undecided. Expected 21/0.
    MATERIAL=1 py tools/bgrun.py --material --max-min 10 --log tools/bench/sim_k_split.log -- py -u tools/bench/sim_k_split.py"""
import json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))   # noqa: E702
import stagesim as S, stagexec as SX, vigraph as V, jev_candidates as JC, protocol  # noqa: E401,E402
J = lambda f: json.load(open(os.path.join(HERE, f), encoding="utf-8"))            # noqa: E731
GATES = []
def gate(label, ok, detail=""):
    GATES.append((label, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)  # noqa: E702
def fact(t): print("  FACT  " + str(t)[:1200], flush=True)                          # noqa: E704

KF, C, L7 = J("k_facts_79.json"), J("k_contract_79_data.json"), J("plan_l7_split.json")
GP = os.path.join(os.path.dirname(HERE), "..", C["graph"]["path"]); GP = os.path.normpath(GP)
gate("C0 base graph + loop table unchanged since the contract", S.md5_file(GP) == C["graph"]["md5"] and
     S.md5_file(os.path.normpath(os.path.join(HERE, "..", "..", C["loops"]["path"]))) == C["loops"]["md5"], C["graph"])
BASE = json.load(open(GP, encoding="utf-8"))
ROWS = dict((r["t"], r) for r in KF["rows"])
KERN = next(r["owner_uid"] for r in BASE["terminals"] if r["term_uid"] == ROWS[8]["term_uid"])
ctx = {"loops": {"path": C["loops"]["path"]}, "fs_pairs_wiki": {"path": L7["context"]["fs_pairs_wiki"]["path"]}, "s1_key": JC.S1_KEY}
st0 = S.base_state(BASE, ctx); G0 = S.graph(st0, JC.node_labels_default()); S1 = JC.load(JC.S1_KEY)
# (a) destination, NAMED by Pre-decided 177(a)/163 (the one pair typed here, as sim_l7_split.py typed #23041/#23405) and
# VERIFIED against the live base: same parent diagram as L7's body, body = loop + (10, 1) exactly as L7's pair, no node yet
LOOP, BODY = 10170, 23166
l7_body = next(a["dest_diagram"] for a in L7["actions"] if a["op"] == "move_in")
l7_loop = next(a["loop"] for a in L7["actions"] if a["op"] == "add_shift_reg")
par = dict((int(k), v) for k, v in C["diagram_parent"].items())
P_ = dict((o["uid"], o["pos"]) for o in st0["objs"])
dl = lambda L, b: (P_[b][0] - P_[L][0], P_[b][1] - P_[L][1])                     # noqa: E731
inb = sorted(set(V.node_of(r) for r in st0["terminals"] if r["frame_diagram"] == BODY))
fact("A0 body #{0}: parent {1} (L7 body parent {2}); body-loop offset {3} (L7 {4}); nodes on it {5}".format(
    BODY, par.get(BODY), par.get(l7_body), dl(LOOP, BODY), dl(l7_loop, l7_body), [(u, S.obj_class(st0, u)) for u in inb]))
# PD178(b): A0 is an OWNERSHIP check, never a pixel comparison. The dump lists every structure immediately followed by
# the Diagram(s) it owns (owner class = the structure's class); the loop -> body owner is read from that traversal order,
# and the same reader must also return L7's measured pair (a control on the method). #KERN's ownership is checked at the end.
OB = st0["objs"]
def owned_body(loop):          # measured order (sim_k_probe_79.log): loop, its border OuterTerminals, then its body Diagram
    i = next(k for k, o in enumerate(OB) if int(o["uid"]) == loop) + 1
    while i < len(OB) and OB[i]["class"] == "OuterTerminal":
        i += 1
    nx = OB[i] if i < len(OB) else {}
    return int(nx["uid"]) if nx.get("class") == "Diagram" and nx.get("owner") == S.obj_class(st0, loop) else None
fact("A0 ownership: body of #{0} = #{1}; body of L7 loop #{2} = #{3} (L7 plan body #{4})".format(LOOP, owned_body(LOOP), l7_loop, owned_body(l7_loop), l7_body))
gate("A0 #BODY is owned by #LOOP (WhileLoop), same parent diagram as L7's body, reader returns L7's pair too, holds no plan node",
     S.obj_class(st0, BODY) == "Diagram" and S.obj_class(st0, LOOP) == "WhileLoop" and owned_body(LOOP) == BODY and
     owned_body(l7_loop) == l7_body and par.get(BODY) == par.get(l7_body) and
     not set(inb) & set(o["uid"] for r in KF["rows"] for o in r["other"]), inb)
bp, l7p = P_[BODY], P_[l7_body]
off = dict((a["nodes"][0], (a["pos"][0] - l7p[0], a["pos"][1] - l7p[1])) for a in L7["actions"] if a["op"] == "move_in")
sub_off, ind_off = off[next(u for u in off if S.obj_class(st0, u) == "SubVI")], off[next(u for u in off if S.obj_class(st0, u) == "ControlTerminal")]
A = []
IND = [x["obj"] for x in C["indicators"]]
for k, u in enumerate(IND):                                                          # (d) indicators first (a live cut)
    A.append({"op": "move_in", "id": "move_ind_{0}".format(k + 1), "nodes": [u], "dest_diagram": BODY,
              "pos": [bp[0] + ind_off[0], bp[1] + ind_off[1] + 60 * k]})
A.append({"op": "move_in", "id": "move_kernel", "nodes": [KERN], "dest_diagram": BODY, "pos": [bp[0] + sub_off[0], bp[1] + sub_off[1]]})
chains = JC.s1_chains(S1, KERN); fact("RULE-CHAIN-S1 chains of #{0}: {1}".format(KERN, [(c["chain"], c["out"], c["in"], c["s1_right"], c["init"]) for c in chains]))
gate("B0 exactly one S1 chain, and it is the kernel-only pair of k_facts (left read by the kernel only)",
     len(chains) == 1 and [k for k, v in KF["f3"].items() if [x["uid"] for x in v["left_read_by"]] == [KERN]] == ["{0}/{1}".format(chains[0]["s1_right"], chains[0]["s1_left"])],
     (chains, list(KF["f3"])))
c = chains[0]
lo = [r for r in st0["terminals"] if r["owner_uid"] == c["s1_left"] and r["term_class"] == "OuterTerminal" and not r["is_source"]]
isrc = [r for r in st0["terminals"] if lo and r["wire_uid"] == lo[0]["wire_uid"] and r["is_source"]]
gate("B1 the old left #{0}'s outer init wire has ONE source, owned by the S1 chain's init #{1} (177(b) single candidate)".format(c["s1_left"], c["init"][0]),
     len(lo) == 1 and len(isrc) == 1 and isrc[0]["owner_uid"] == c["init"][0], (lo, isrc))
A += [{"op": "add_shift_reg", "id": "sr_" + c["chain"], "loop": LOOP, "body": BODY, "as": "SR1", "y": next(a["y"] for a in L7["actions"] if a["op"] == "add_shift_reg")},
      {"op": "wire", "id": "chain_R", "src": {"uid": KERN, "term": c["out"]}, "dst": "new:SR1R.inner"},
      {"op": "wire", "id": "chain_L", "src": "new:SR1L.inner", "dst": {"uid": KERN, "term": c["in"]}},
      {"op": "wire", "id": "chain_init", "src": {"uid": c["init"][0], "term_uid": isrc[0]["term_uid"]}, "dst": "new:SR1L.outer"}]
TUN = []
for t, r in sorted(ROWS.items()):                                                    # (c) tunnels, IndexMode = original's
    if "from-tunnel" not in (r.get("rw") or ""):
        continue
    old, face = r["other"][0]["uid"], r["via"][0]["outer"][0]
    fsit = face["ends"][0]["uid"]
    src = [x for x in st0["terminals"] if x["owner_uid"] == fsit and x["wire_uid"] == face["face_wire"] and x["is_source"]]
    gate("T0 t{0}: ONE source term of FSIT #{1} on the old tunnel #{2}'s outer wire w{3}".format(t, fsit, old, face["face_wire"]), len(src) == 1, src)
    im = C["index_modes"][str(old)]["index_mode"]; n = len(TUN) + 1; TUN.append({"t": t, "old": old, "as": "T{0}".format(n), "index_mode": im})  # noqa: E702
    A += [{"op": "tunnel", "id": "tun_t{0}".format(t), "loop": LOOP, "body": BODY, "dir": "in", "as": "T{0}".format(n), "indexing": bool(im)},
          {"op": "wire", "id": "tun_t{0}_out".format(t), "src": {"uid": fsit, "term_uid": src[0]["term_uid"]}, "dst": "new:T{0}.outer".format(n)},
          {"op": "wire", "id": "tun_t{0}_in".format(t), "src": "new:T{0}.inner".format(n), "dst": {"uid": KERN, "term": r["name"]}}]
for k, x in enumerate(C["indicators"]):
    A.append({"op": "wire", "id": "ind_{0}".format(k + 1), "src": {"uid": KERN, "term": c["out"]}, "dst": {"uid": x["obj"], "term": x["name"]}})
REMADE = set([c["in"], c["out"]] + [ROWS[x["t"]]["name"] for x in TUN])
E_IN = [r["name"] for t, r in sorted(ROWS.items()) if r["dir"] == "IN" and r["bed_wire"] and r["name"] not in REMADE]
E_OUT = [r["name"] for t, r in sorted(ROWS.items()) if r["dir"] == "OUT" and r["bed_wire"] and
         (r["name"] != c["out"] or any(o["uid"] not in IND and "SR" not in o["tag"] and o["class"] != "Diagram" for o in r["other"]))]
T8_OPEN = set(o["uid"] for o in ROWS[8]["other"] if o["uid"] not in IND and "SR" not in o["tag"] and o["class"] != "Diagram")
fact("(e) OPEN by rule: inputs {0}; outputs {1}; t8's open sinks {2}".format(E_IN, E_OUT, sorted(T8_OPEN)))
def mk(open_rows, name):
    plan = {"schema": "stageplan/1", "stage": "k_split", "goal": "stage K (Pre-decided 177): kernel #{0} into 1.2 body #{1}".format(KERN, BODY),
            "base": {"path": C["graph"]["path"], "md5": C["graph"]["md5"]}, "context": ctx, "actions": A,
            "open_rows": [{"node": n, "term": t, "why": "Pre-decided 177(e) / carried L7 row (175)"} for n, t in open_rows]}
    p = os.path.join(HERE, name); json.dump(plan, open(p, "w", encoding="utf-8"), indent=1); return p   # noqa: E702
gate("P0 plan validates as stageplan/1 ({0} actions)".format(len(A)), protocol.validate_obj(json.load(open(mk([], "stageplan_k_split.json"))))[0])
R0 = S.simulate(os.path.join(HERE, "stageplan_k_split.json"), GP, labels=JC.node_labels_default(), log=lambda *_a: None)
gate("P1 every action applied", R0["failed"] is None, R0["failed"])
gate("P2 base computation_diff(S1) == the contract's 2 carried L7 rows", sorted((V.key_parts(k)[0], V.key_parts(k)[2]) for k in R0["steps"][0]["cdiff_rows"]) == sorted(tuple(x) for x in C["cdiff_rows"]), R0["steps"][0]["cdiff_rows"])
end = sorted(set((V.key_parts(k)[0], V.key_parts(k)[2]) for k in R0["end_cdiff_rows"] or []))
stE = json.load(open(R0["steps"][-1]["file"]["path"], encoding="utf-8"))["state"]
EK = set(E_IN) | set(E_OUT)
kd = sorted(set(r["frame_diagram"] for r in stE["terminals"] if V.node_of(r) == KERN))
gate("A0-END #KERN is owned by #BODY at the end (every #{0} terminal on diagram #{1})".format(KERN, BODY), kd == [BODY], kd)
def p3(st, rows):
    """PD178(b). S1 credits an (e) OUTPUT only through rows on OTHER nodes; an output whose only S1 consumer is #KERN
    itself (t3) is credited by END-GRAPH evidence: it is unwired and every base consumer on its base wire is sourceless.
    For every (e) terminal: no wire to any other terminal at the end; no end row has an (e) terminal among its END sources."""
    G = S.graph(st, JC.node_labels_default()); why, used, bad = {}, set(), []       # the labels simulate() uses
    ek = set(k for k in G["rows"] if V.key_parts(k)[0] == KERN and V.key_parts(k)[2] in EK)
    for k in rows:
        n, _c, t, _o = V.key_parts(k)
        if (n, t) in set(tuple(x) for x in C["cdiff_rows"]):
            why[(n, t)] = "L7 carried"; continue                                     # noqa: E702
        es = V.effective_sources(G, k) & ek
        if es:
            bad.append("row #{0} {1} END-sourced by (e) {2}".format(n, t, sorted(V.key_parts(e)[2] for e in es)))
        k1, _h = JC.map_key(S1, k, G); eff = V.effective_sources(S1, k1) if k1 else set()
        hit = sorted(V.key_parts(e)[2] for e in eff if V.key_parts(e)[0] == KERN and V.key_parts(e)[2] in E_OUT and n != KERN and
                     (V.key_parts(e)[2] != c["out"] or n in T8_OPEN))                # t8: only its (e) sinks, never K's own rows
        own = [t] if (n == KERN and t in E_IN) else []
        why[(n, t)] = "; ".join((["(e) in"] if own else []) + (["(e) out via " + ",".join(hit)] if hit else [])) or "UNEXPLAINED"
        used.update(hit + own)
    for r in st["terminals"]:                                                        # every (e) terminal is open at the end
        if V.node_of(r) == KERN and r["term_name"] in EK - REMADE and r["wire_uid"] and any(x is not r for x in S.wire_rows(st, r["wire_uid"])):
            bad.append("(e) {0} still wired (w{1})".format(r["term_name"], r["wire_uid"]))
    for t in sorted(set(E_OUT) - used):                                              # end-graph credit (t3)
        b = [r for r in st0["terminals"] if V.node_of(r) == KERN and r["term_name"] == t and r["is_source"]]
        cons = [r for r in st0["terminals"] if b and r["wire_uid"] == b[0]["wire_uid"] and not r["is_source"] and V.node_of(r) != KERN]
        endw = [(x["term_uid"], x["wire_uid"], S.has_source(st, x["wire_uid"])) for r in cons for x in st["terminals"]
                if x["term_uid"] == r["term_uid"] and x["term_class"] == r["term_class"]]
        e_on = [r for r in st["terminals"] if V.node_of(r) == KERN and r["term_name"] == t and r["wire_uid"]]
        ok_t = bool(b) and bool(cons) and not e_on and endw and not any(h for _u, _w, h in endw)
        why["end-graph " + t] = "credited: unwired, base consumers {0} sourceless {1}".format([r["term_uid"] for r in cons], endw) if ok_t else \
            "NOT credited: wired {0}, base consumers {1}".format([r["wire_uid"] for r in e_on], endw)
        if ok_t:
            used.add(t)
    ok = all(v != "UNEXPLAINED" for v in why.values()) and used == EK and not bad
    return ok, {"unexplained": [k for k, v in why.items() if v == "UNEXPLAINED"], "unused": sorted(EK - used), "bad": bad}, why
ok3, d3, why = p3(stE, R0["end_cdiff_rows"] or [])
for x in end: fact("END CDIFF ROW {0} <- {1}".format(x, why.get(x)))                  # noqa: E701
for k_, v_ in why.items():
    if isinstance(k_, str): fact("P3 {0} <- {1}".format(k_, v_))                     # noqa: E701
gate("P3 every end row is an (e)/L7 row, every (e) terminal credited (t3 by end-graph sources), no (e) terminal wired or END-sourcing a row", ok3, d3)
# PD178(b) negative control: a fake t3 -> #2626 'array' edge on a COPY of the end state must FAIL the same gate
neg, T3, NS = json.loads(json.dumps(stE)), ROWS[3]["name"], min(x for x in end if x[1] == "array")     # t3; #2626 'array'
nsrc = [r for r in neg["terminals"] if V.node_of(r) == KERN and r["term_name"] == T3 and r["is_source"]]
nsnk = [r for r in neg["terminals"] if (V.node_of(r), r["term_name"]) == NS and not r["is_source"]]
fake = S.new_uid(neg)
for r in nsrc + nsnk: r["wire_uid"] = fake                                           # noqa: E701
okn, dn, _w = p3(neg, S.cdiff_keys(V.computation_diff(S1, S.graph(neg, JC.node_labels_default()))))
gate("P3-NEG fake {0} -> #{1} '{2}' edge ({3} src + {4} sink rows) FAILS P3".format(T3, NS[0], NS[1], len(nsrc), len(nsnk)),
     len(nsrc) == 1 and len(nsnk) == 1 and not okn and any(T3 in b for b in dn["bad"]), dn)          # fails FOR t3, not by accident
PD178C = sorted([(376, "current frame data array in"), (376, "frame index"), (2626, "array"), (5696, "x,y,z array"), (6085, "x,y,z array"),
                 (10757, "array"), (10969, "array"), (KERN, "Bead is good? array in"), (KERN, "Image In"), (KERN, "x,y,z array")])
gate("PB end rows == Pre-decided 178(c)'s 10 rows (typed from the ruling)", end == PD178C, {"extra": sorted(set(end) - set(PD178C)), "missing": sorted(set(PD178C) - set(end))})
R = S.simulate(mk(end, "stageplan_k_split.json"), GP, labels=JC.node_labels_default(), log=print)
gate("P4 plan FINAL: end rows == declared open_rows ({0} rows), no undecided row".format(len(end)), R["final"] and R["open_rows_match"], (R["final"], R["failed"]))
srcs = sorted(set(x.get("model_source") for x in R["steps"][1:]))
gate("P5 every step ran on a MEASURED op model", all(str(x).startswith("measured:") for x in srcs), srcs)
plan = json.load(open(os.path.join(HERE, "plan_k_split.json"), encoding="utf-8"))
ops = SX.compile_plan(plan); WIR = ("tunnel", "connect", "wire_sr", "branch")
fact("COMPILED {0} real ops: {1}".format(len(ops), [(o["kind"], o["acts"]) for o in ops]))
gate("P6 11 wired rows (1 init + 2 chain + 6 tunnel + 2 indicator)", sum(1 for o in ops if o["kind"] in WIR) == 11, [o["kind"] for o in ops])
st, ff, _ex = SX.dry_run(os.path.join(HERE, "plan_k_split.json"), log=lambda *_a: None)
gate("P7 stagexec dry run on the simulated backend PASS", st == "PASS", ff)
BY = {"chain_R": "RULE-CHAIN-S1", "chain_L": "RULE-CHAIN-S1", "chain_init": "RULE-SINGLE-CANDIDATE (165)"}
dec = []
for o in ops:
    a = plan["actions"][o["acts"][-1 if o["kind"] == "tunnel" else 0] - 1]
    ex = dict((s_, a[s_]) for s_ in ("src", "dst") if isinstance(a.get(s_), dict) and isinstance(a[s_].get("uid"), int))
    if o["kind"] == "tunnel":
        ex["src"] = plan["actions"][o["in_act"] - 1]["src"]
    dec.append({"id": plan["actions"][o["acts"][0] - 1]["id"], "action": "wire" if o["kind"] in WIR else o["kind"], "kind": o["kind"], "acts": o["acts"],
                "decided_by": BY.get(a["id"], "rule 166 tunnel" if o["kind"] == "tunnel" else "rule 177(d) indicator" if o["kind"] == "connect" else "rule 177(a)"), "exec": ex})
json.dump({"schema": "k-rows/1", "plan": {"path": "tools/bench/plan_k_split.json", "md5": S.md5_file(os.path.join(HERE, "plan_k_split.json"))},
           "tunnels": TUN, "open": [list(x) for x in end], "why": dict(("#{0} {1}".format(*k), v) for k, v in why.items()), "decisions": dec},
          open(os.path.join(HERE, "plan_k_rows.json"), "w", encoding="utf-8"), indent=1)
fact("plan_out {0}; rows file tools/bench/plan_k_rows.json ({1} decisions)".format(R["plan_out"], len(dec)))
n_pass = sum(1 for _l, ok in GATES if ok); n_fail = len(GATES) - n_pass; first = next((l for l, ok in GATES if not ok), None)  # noqa: E702
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, [{"path": R["plan_out"]["path"], "md5": R["plan_out"]["md5"]}])))
