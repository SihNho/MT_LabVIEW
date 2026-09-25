r"""sim_l2a1_81b - card 81-5 B1 + S1/S2 (docs/d1-loop12-17-split-plan.md 182(a)-(e)). sim_l2a1_81.py (card 81-2) with the
three builder defects the review archive/peer/2026-09-25-hyp-sim-l2a1-81.md found, fixed in the BUILDER (182(d)), not in the
model. PURE PYTHON, no LabVIEW. Writes only tools/bench/sim/l2a1/** and tools/bench/sim/<run>/**.
FIXES: (1) a lost edge = an S1 wire edge whose two terminals do NOT share a wire after the moves (81's edges() dropped any edge
whose source had flipped, so rw_5705_5999 re-wired a wire the closure never cut); (2) owners gain every LoopTunnel of the base
as [loop class, loop uid] via its inner terminal's frame diagram (81's lookup returned null for #5752/#5569 -> AMBIGUOUS, no
rule-166 tunnel); (3) the 181(b) frame-uid sets come from the graph: the SelectorTunnels whose inner frame diagram is owned by
#5540/#10445, and the set must be {5582,5592,10453,10459} (81 read ([],[])). PD182(a)(b): #10739 #10929 #17272 are moved
after their consumers; PD182(c): the #10382/#11529 edges are not wired - they are PB open rows owed to QRT.
WHAT EXISTED FIRST: sim_l2a1_81.py (this file is it + the 3 fixes; same gates G0-G1, B*, T*, P0-P5).
PREDICTION: B1a-c pass (no in-closure re-wire, owners carry #5752/#5569 -> 637, frame set = the 4 uids); T gates for the two
tunnels; in mode `sim`: P2 no SimError iff stagesim models what M1 (l2a1_unflip_81.log) measured; P3 = frame cdiff == PB.
  MATERIAL=1 py tools/bgrun.py --material --max-min 20 --log tools/bench/sim_l2a1_81b_plan.log -- py -u tools/bench/sim_l2a1_81b.py plan
  MATERIAL=1 py tools/bgrun.py --material --max-min 20 --log tools/bench/sim_l2a1_81b.log -- py -u tools/bench/sim_l2a1_81b.py sim"""
import collections, copy, json, os, re, sys                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path.insert(0, TOOLS)  # noqa: E702
import stagesim as S, vigraph as V, jev_candidates as JC, protocol                     # noqa: E401,E402
MODE = sys.argv[1] if len(sys.argv) > 1 else "plan"
GATES, OUT = [], os.path.join(HERE, "sim", "l2a1")
def gate(l, ok, d=""): GATES.append((l, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:1500]), flush=True)  # noqa: E702,E704
def fact(t): print("  FACT  " + str(t)[:2500], flush=True)                          # noqa: E704
J = lambda p: json.load(open(p, encoding="utf-8"))                                     # noqa: E731
os.makedirs(OUT, exist_ok=True)
GP, FP = os.path.join(HERE, "l2a1_graph_k_80.json"), os.path.join(HERE, "l2a1_facts_80.json")
gate("G0 inputs: graph c764150c, facts d5003581", (S.md5_file(GP), S.md5_file(FP)) == ("c764150c4587b78429d0bbdb9d30c27f", "d5003581aa1469ac5b82728d22361f0d"))
P, SRC, _e, _g = S.model_for("move_in", S.load_models()); fact("move_in model {0} params {1}".format(SRC, P))   # noqa: E702
g = J(GP); F = J(FP); gb = dict(g, owners=F["owners"]); BP = os.path.join(OUT, "graph_k_80_owners.json")   # noqa: E702
json.dump(gb, open(BP, "w", encoding="utf-8"), separators=(",", ":"))
gate("G1 derived base == l2a1_graph_k_80.json + owners only", all(J(BP)[k] == g[k] for k in g) and set(J(BP)) - set(g) == {"owners"}, S.md5_file(BP))
LAB, S1 = JC.node_labels_default(), JC.load(JC.S1_KEY)
LOOP, BODY, PAR, KERN = 10170, 23166, 686, 5058                                        # PD163 / PD177(a) / l2a1_facts_80.log:44,217
TOPS = [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634, 23541, 10739, 10929, 17272]   # PD181(d) + PD182(a)(b)
QRT = {10382, 11529}                                                                   # PD182(c): stay on 1.1, PB open rows
PAIRS = [(1147, 1142), (5796, 5805), (7311, 11001)]
st0 = S.base_state(copy.deepcopy(gb)); stm = copy.deepcopy(st0); effs = []              # noqa: E702
# FIX (2): owners + every LoopTunnel -> [loop class, loop uid] from its inner terminal's frame diagram
OWN = dict(F["owners"])
for r in st0["terminals"]:
    if r["owner_class"] == "LoopTunnel" and r["term_class"] == "InnerTerminal" and str(r["frame_diagram"]) in F["owners"]:
        OWN.setdefault(str(r["owner_uid"]), F["owners"][str(r["frame_diagram"])])
gate("B1b owners carry LoopTunnels #5752/#5569 -> loop #637", [(OWN.get(u) or [0, 0])[1] for u in ("5752", "5569")] == [637, 637], [OWN.get(u) for u in ("5752", "5569")])
# FIX (3): frame-uid sets from the graph
D0 = set(int(d) for d, v in F["owners"].items() if int(v[1] or 0) in (5540, 10445))
CT = set(r["owner_uid"] for r in st0["terminals"] if r["owner_class"] == "SelectorTunnel" and r["term_class"] == "InnerTerminal" and int(r["frame_diagram"] or 0) in D0)
fr = lambda st: set(int(r["frame_diagram"]) for r in st["terminals"] if r["owner_uid"] in CT and r["term_class"] == "InnerTerminal")   # noqa: E731
gate("B1c frame-uid set sourced from the graph == {5582,5592,10453,10459}, non-empty", D0 == fr(st0) == {5582, 5592, 10453, 10459}, (sorted(D0), sorted(fr(st0)), len(CT)))
for u in TOPS:
    effs.append(S.op_move_in(stm, {"nodes": [u], "dest_diagram": BODY}, P, S1, LAB)[0])
M = set(x for e in effs for x in e["moved"]) | {KERN}
Rm = dict((r["term_uid"], r) for r in stm["terminals"])
same_wire = lambda s, d: bool(Rm[s]["wire_uid"]) and Rm[s]["wire_uid"] == Rm[d]["wire_uid"]   # noqa: E731
fact("moves: {0} nodes moved, cuts {1}, flips {2}, bare {3}".format(len(M) - 1, sum(e["n_cut"] for e in effs), [(f["tunnel"], f["term_uid"]) for e in effs for f in e["tunnel_flips"]],
     [(b["wire"], b["term_uid"]) for e in effs for b in e["bare_deleted"]]))
S1E = set((S1["rows"][a]["term_uid"], S1["rows"][b]["term_uid"], V.key_parts(a)[0], V.key_parts(b)[0]) for k, a, b, _i in S1["edges"] if k == "wire")
node = lambda t: V.node_of(Rm[t]) if t in Rm else None                                  # noqa: E731
POS = dict((int(o["uid"]), o["pos"]) for o in st0["objs"])                            # PD183(e): pos = the node's base position (K convention, sim_k_split.py:70-72)
A = [{"op": "move_in", "id": "mv_{0}".format(u), "nodes": [u], "dest_diagram": BODY, "pos": POS[u]} for u in TOPS]
WIRES, AMBIG, sr_ids = [], [], {}
rights = dict((int(r), [int(x) for x in (ls if isinstance(ls, list) else [ls])]) for L in st0["loops"] or [] if int(L["loop_uid"]) == 637 for r, ls in (L.get("left_of") or {}).items())
for n, (R, L) in enumerate(PAIRS, 1):
    gate("B{0} #{1}/#{2} is a pair of loop #637 in the base loop table".format(n, R, L), L in rights.get(R, []), rights.get(R))
    rin = [(s, d, na) for s, d, na, nb in S1E if nb == R]; lout = [(s, d, nb) for s, d, na, nb in S1E if na == L]   # noqa: E702
    lo = [r for r in st0["terminals"] if V.node_of(r) == L and r["term_class"] == "OuterTerminal" and not r["is_source"]]
    ini = [r for r in st0["terminals"] if lo and lo[0]["wire_uid"] and r["wire_uid"] == lo[0]["wire_uid"] and r["is_source"]]
    ok = len(rin) == 1 and rin[0][2] in M and lout and all(x[2] in M for x in lout) and len(ini) == 1
    gate("B{0}b RULE-CHAIN-S1: old right fed by ONE S1 source in M, old left feeds only M, ONE base init source".format(n), ok, (rin, lout, [(r["term_uid"], V.node_of(r), r["frame_diagram"]) for r in ini]))
    A += [{"op": "add_shift_reg", "id": "sr{0}".format(n), "loop": LOOP, "body": BODY, "parent": PAR, "as": "SR{0}".format(n)},
          {"op": "wire", "id": "sr{0}_init".format(n), "src": {"uid": V.node_of(ini[0]), "term_uid": ini[0]["term_uid"]}, "dst": "new:SR{0}L.outer".format(n)},
          {"op": "wire", "id": "sr{0}_R".format(n), "src": {"uid": rin[0][2], "term_uid": rin[0][0]}, "dst": "new:SR{0}R.inner".format(n)}]
    A += [{"op": "wire", "id": "sr{0}_L{1}".format(n, i), "src": "new:SR{0}L.inner".format(n), "dst": {"uid": x[2], "term_uid": x[1]}} for i, x in enumerate(lout)]
    sr_ids[R] = sr_ids[L] = n
IM = dict((int(u), int(m)) for u, m in re.findall(r"'uid': (\d+), 'index_mode': (\d)", open(os.path.join(HERE, "diag_d1_step0.log"), encoding="utf-8").read()))
nt = 0
for e in effs:
    for row in e["reconnect"]:
        if row["side"] != "moved" or row["term_uid"] not in Rm:
            continue
        t = row["term_uid"]; mine = [(s, d, na, nb) for s, d, na, nb in S1E if (d == t if not row["is_source"] else s == t)]   # noqa: E702
        for s, d, na, nb in mine:
            other = na if not row["is_source"] else nb
            oc = S.obj_class(st0, other)
            if other in M or other in sr_ids:
                continue
            if oc == "LoopTunnel" and (OWN.get(str(other)) or [0, 0])[1] == 637 and not row["is_source"]:
                fo = [r for r in st0["terminals"] if V.node_of(r) == other and r["term_class"] == "OuterTerminal"]
                src = [r for r in st0["terminals"] if fo and fo[0]["wire_uid"] and r["wire_uid"] == fo[0]["wire_uid"] and r["is_source"]]
                nt += 1; ok = len(src) == 1 and other in IM                              # noqa: E702
                gate("T{0} rule-166 tunnel for #637 input LoopTunnel #{1} -> #{2} t{3}: ONE outer source, recorded IndexMode {4}".format(nt, other, node(t), t, IM.get(other)), ok, src and src[0]["term_uid"])
                A += [{"op": "tunnel", "id": "tun{0}".format(nt), "loop": LOOP, "body": BODY, "parent": PAR, "dir": "in", "as": "T{0}".format(nt), "indexing": bool(IM.get(other))},
                      {"op": "wire", "id": "tun{0}_out".format(nt), "src": {"uid": V.node_of(src[0]), "term_uid": src[0]["term_uid"]}, "dst": "new:T{0}.outer".format(nt)},
                      {"op": "wire", "id": "tun{0}_in".format(nt), "src": "new:T{0}.inner".format(nt), "dst": {"uid": node(t), "term_uid": t}}]
            else:
                AMBIG.append({"moved_term": t, "moved_node": node(t), "dir": "out" if row["is_source"] else "in", "s1_partner": other, "partner_class": oc,
                              "partner_diagram": (OWN.get(str(other)) or [None, None])[1], "cut_wire": row["cut_wire"], "pd182c_qrt": other in QRT})
inclosure = []
for s, d, na, nb in sorted(S1E):                                                          # FIX (1): lost = not on one wire now
    if na in M and nb in M:
        if s not in Rm or d not in Rm:
            AMBIG.append({"s1_edge": [s, d, na, nb], "why": "terminal absent from the base"}); continue   # noqa: E702
        if same_wire(s, d):
            inclosure.append((s, d)); continue                                             # noqa: E702
        WIRES.append({"op": "wire", "id": "rw_{0}_{1}".format(s, d), "src": {"uid": na, "term_uid": s}, "dst": {"uid": nb, "term_uid": d}})
gate("B1a no re-wire row joins two terminals already on one wire (rw_5705_5999 absent)",
     not any(same_wire(w["src"]["term_uid"], w["dst"]["term_uid"]) for w in WIRES) and "rw_5705_5999" not in [w["id"] for w in WIRES], len(inclosure))
flipped_src = [w for w in WIRES if not Rm[w["src"]["term_uid"]]["is_source"]]
A += [w for w in WIRES if w not in flipped_src] + flipped_src
fact("RECONNECT: {0} lost edges re-wired {1}; {2} kept (still on one wire); {3} need a source that reads is_source False after the moves: {4}".format(
     len(WIRES), [w["id"] for w in WIRES], len(inclosure), len(flipped_src), [(w["id"], w["src"]) for w in flipped_src]))
for a in AMBIG: fact("AMBIGUOUS (not wired, stays open) " + json.dumps(a))              # noqa: E701
gate("B1d the only non-QRT, non-tunnel AMBIGUOUS rows are K's frame-image row class (no #5752/#5569 left)", not [a for a in AMBIG if a.get("s1_partner") in (5752, 5569)], [a.get("s1_partner") for a in AMBIG])
ctl = [a["id"] for a in A if a["op"] == "wire" and isinstance(a["dst"], dict) and S.obj_class(st0, a["dst"]["uid"]) == "ControlTerminal"]
fact("P5 sink_gates needed (wire rows whose SINK is a ControlTerminal, 179(b) reader): {0}".format(ctl))
def mk(open_rows):
    p = os.path.join(OUT, "stageplan_l2a1.json")
    json.dump({"schema": "stageplan/1", "stage": "l2a1", "goal": "L2-A1 (Pre-decided 181(d)+182(a)-(c)): group A + reset controls + #23541 + #10739 #10929 #17272 into 1.2 body #23166",
               "base": {"path": S._rel(BP), "md5": S.md5_file(BP)}, "context": {"s1_key": JC.S1_KEY}, "actions": A,
               "open_rows": [{"node": n, "term": t, "why": "PD181(d)/182(c): simulator's finalized open-row list"} for n, t in open_rows]}, open(p, "w", encoding="utf-8"), indent=1)
    return p
gate("P0 plan validates as stageplan/1 ({0} actions)".format(len(A)), protocol.validate_obj(J(mk([])))[0])
art = []
if MODE == "sim":
    sim = lambda o: S.simulate(mk(o), BP, out_root=os.path.join(HERE, "sim"), plan_out_dir=OUT, labels=LAB, log=print)   # noqa: E731
    R = sim([])
    gate("P2 every action applied (no SimError)", R["failed"] is None, R["failed"])
    last = J(R["steps"][-1]["file"]["path"])["state"]
    gate("P3b frame-diagram uid sets of #5540/#10445 equal before/after (181(b)), from the graph", fr(st0) == fr(last) == D0 and D0, (sorted(fr(st0)), sorted(fr(last))))
    if R["failed"] is None:
        s1p = J(os.path.join(JC.WIKI, JC.S1_KEY + ".json"))
        S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
        cf = lambda st: sorted(set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in V.computation_diff_frame(S1f, V.build4(st["terminals"], st["objs"], st["loops"], LAB, st["fs_pairs"], frame_keyed=True))["rows"]))   # noqa: E731
        b0, e0 = cf(st0), cf(last); mrg = sorted(set((V.key_parts(k)[0], V.key_parts(k)[2]) for k in R["end_cdiff_rows"] or []))   # noqa: E702
        fact("base frame cdiff {0} rows {1}".format(len(b0), b0)); fact("END frame cdiff {0} rows (= PB) {1}; merged {2}".format(len(e0), e0, len(mrg)))   # noqa: E702
        fact("PB rows on the PD182(c) QRT sinks' partner #10886: {0}".format([x for x in e0 if x[0] == 10886]))
        R2 = sim(e0)
        gate("P3 FINAL: frame cdiff(S1, end) == the plan's open rows ({0}) and merged end rows agree".format(len(e0)), R2["final"] and e0 == mrg, (R2["final"], R2["failed"]))
        R = R2
    else:
        gate("P3 FINAL: frame cdiff(S1, end) == PB", False, "not reached: simulation stopped at step {0}".format(R["failed"]))
    fact("plan_out {0}; steps {1}; candidates {2}".format(R["plan_out"], len(R["steps"]) - 1, R["n_candidates"]))
    art = [{"path": R["plan_out"]["path"], "md5": R["plan_out"]["md5"]}]
n_pass = sum(1 for _l, ok in GATES if ok); first = next((l for l, ok in GATES if not ok), None)   # noqa: E702
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, len(GATES) - n_pass, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, len(GATES) - n_pass, first, art)))
