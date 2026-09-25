r"""sim_l2a1_81 - card 81-2: PD181(a)1 check + PD181(d) L2-A1 as a stageplan/1, SIMULATED on D1_k and (if it can be)
FINALIZED. PURE PYTHON, no LabVIEW. Writes only tools/bench/sim/l2a1/** (stageplan, step files, plan_l2a1.json, summary).
WHAT EXISTED FIRST: sim_k_split.py (same shape: moves, RULE-CHAIN-S1 pairs, rule-166 tunnels, finalize with open_rows);
selftest_stagesim_l2a1_80.py (the 11-top sequential order of the measured 80-5 move, owner-map context); vigraph.build4
frame_keyed + computation_diff_frame (80-7); l2a1_facts_80.json (owner map, F1-F4 border rows). Nothing new is modelled.
OWNER MAP: stageplan/1 `context` has no `owners` field and l2a1_graph_k_80.json carries none, so the base the plan names is
sim/l2a1/graph_k_80_owners.json = l2a1_graph_k_80.json + key `owners` from l2a1_facts_80.json (G0 checks every other key equal).
ROWS (PD181(d)): move group A (8) + #17487 #5634 in the 80-5 order, then #23541; 3 new register pairs on #10170 from the mixed
pairs (R.inner <- the S1 source of the old right, L.inner -> the S1 sinks of the old left, L.outer <- the base init source -
RULE-CHAIN-S1); rule-166 tunnels for #637 input LoopTunnels feeding a moved sink (IndexMode = the recorded original's); every
S1 wire edge between two nodes of M = moved + #5058 that is absent after the moves (K rows t0 t7 t8 + lost member edges).
A reconnect row whose S1 partner is a non-relay node left on #639 is NOT wired: it is reported as AMBIGUOUS and stays open.
PREDICTION: G0-G2 pass; P1 selftests unchanged (42/0, 4/0, 13/0); every wire action whose source reads is_source False after the
moves (a flipped tunnel outer) is ordered LAST - if any exists the simulator STOPS there (no un-flip rule exists, not refit here)
and P3 FAILS with that step; otherwise P3 = frame cdiff == open rows. P4/P5 are reports.
    MATERIAL=1 py tools/bgrun.py --material --max-min 20 --log tools/bench/sim_l2a1_81.log -- py -u tools/bench/sim_l2a1_81.py"""
import collections, copy, json, os, re, subprocess, sys                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path.insert(0, TOOLS)  # noqa: E702
import stagesim as S, vigraph as V, jev_candidates as JC, protocol                     # noqa: E401,E402
GATES, OUT = [], os.path.join(HERE, "sim", "l2a1")
def gate(l, ok, d=""): GATES.append((l, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:1500]), flush=True)  # noqa: E702,E704
def fact(t): print("  FACT  " + str(t)[:2500], flush=True)                          # noqa: E704
J = lambda p: json.load(open(p, encoding="utf-8"))                                     # noqa: E731
os.makedirs(OUT, exist_ok=True)
GP, FP, PLANDOC = os.path.join(HERE, "l2a1_graph_k_80.json"), os.path.join(HERE, "l2a1_facts_80.json"), os.path.join(TOOLS, "..", "docs", "d1-loop12-17-split-plan.md")
gate("G0 inputs: graph c764150c, facts d5003581, plan doc 2cdc66bb", (S.md5_file(GP), S.md5_file(FP), S.md5_file(PLANDOC)) ==
     ("c764150c4587b78429d0bbdb9d30c27f", "d5003581aa1469ac5b82728d22361f0d", "2cdc66bb7e5b3ac6694e1fb43127c1d5"))
# ---- P1: move_in.json sim carries the 80-6 params; model_source cites that file; existing selftests unchanged
P, SRC, _e, _g = S.model_for("move_in", S.load_models()); SIMP = J(os.path.join(HERE, "opmodels", "move_in.json"))["sim"]  # noqa: E702
NEW = {"closure": True, "sequential": True, "flip_moved_inputs": True, "flip_needs_wired": True, "bare_half_wire": "delete"}
gate("P1a opmodels/move_in.json sim carries the 5 card-80-6 params; model_source is measured:<that file>@<its md5>",
     all(SIMP.get(k) == v for k, v in NEW.items()) and SRC == "measured:tools/bench/opmodels/move_in.json@" + S.md5_file(os.path.join(HERE, "opmodels", "move_in.json")), SRC)
for lbl, cmd, want in (("stagesim selftest", [os.path.join(TOOLS, "stagesim.py"), "selftest"], (42, 0)), ("selftest_stagesim_k79", [os.path.join(HERE, "selftest_stagesim_k79.py")], (4, 0)),
                       ("selftest_stagesim_l2a1_80", [os.path.join(HERE, "selftest_stagesim_l2a1_80.py")], (13, 0))):
    p = subprocess.run([sys.executable, "-u"] + cmd, capture_output=True, text=True, timeout=400)
    m = re.findall(r"=== GATES: (\d+) pass / (\d+) fail", p.stdout); got = tuple(int(x) for x in m[-1]) if m else None   # noqa: E702
    gate("P1b {0} unchanged {1}/{2}".format(lbl, *want), got == want, (got, p.returncode))
# ---- base = graph + owner map
g = J(GP); F = J(FP); gb = dict(g, owners=F["owners"]); BP = os.path.join(OUT, "graph_k_80_owners.json")   # noqa: E702
json.dump(gb, open(BP, "w", encoding="utf-8"), separators=(",", ":"))
gate("G1 derived base == l2a1_graph_k_80.json + owners only", all(J(BP)[k] == g[k] for k in g) and set(J(BP)) - set(g) == {"owners"}, S.md5_file(BP))
LAB, S1 = JC.node_labels_default(), JC.load(JC.S1_KEY)
LOOP, BODY, PAR, KERN = 10170, 23166, 686, 5058                                        # PD163 / PD177(a) / l2a1_facts_80.log:44,217
TOPS = [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634, 23541]        # PD181(d); 80-5 measured order + #23541
PAIRS = [(1147, 1142), (5796, 5805), (7311, 11001)]                                    # PD181(d)/180(e) mixed pairs
st0 = S.base_state(copy.deepcopy(gb)); stm = copy.deepcopy(st0); effs = []              # noqa: E702
for u in TOPS:
    effs.append(S.op_move_in(stm, {"nodes": [u], "dest_diagram": BODY}, P, S1, LAB)[0])
M = set(x for e in effs for x in e["moved"]) | {KERN}
def edges(st):
    byw = collections.defaultdict(lambda: ([], [])); rows = dict((r["term_uid"], r) for r in st["terminals"])   # noqa: E702
    for r in st["terminals"]:
        if r["wire_uid"]: byw[r["wire_uid"]][0 if r["is_source"] else 1].append(r["term_uid"])   # noqa: E701
    return set((a, b) for s, k in byw.values() for a in s for b in k), rows
E0, R0 = edges(st0); Em, Rm = edges(stm)                                                # noqa: E702
fact("moves: {0} nodes moved, cuts {1}, flips {2}, bare {3}".format(len(M) - 1, sum(e["n_cut"] for e in effs), [(f["tunnel"], f["term_uid"]) for e in effs for f in e["tunnel_flips"]],
     [(b["wire"], b["term_uid"]) for e in effs for b in e["bare_deleted"]]))
S1E = set((S1["rows"][a]["term_uid"], S1["rows"][b]["term_uid"], V.key_parts(a)[0], V.key_parts(b)[0]) for k, a, b, _i in S1["edges"] if k == "wire")
node = lambda t: V.node_of(Rm[t]) if t in Rm else None                                  # noqa: E731
A = [{"op": "move_in", "id": "mv_{0}".format(u), "nodes": [u], "dest_diagram": BODY} for u in TOPS]
WIRES, AMBIG, sr_ids = [], [], {}
rights = dict((int(r), [int(x) for x in (ls if isinstance(ls, list) else [ls])]) for L in st0["loops"] or [] if int(L["loop_uid"]) == 637 for r, ls in (L.get("left_of") or {}).items())
for n, (R, L) in enumerate(PAIRS, 1):
    gate("B{0} #{1}/#{2} is a pair of loop #637 in the base loop table".format(n, R, L), L in rights.get(R, []), rights.get(R))
    rin = [(s, d, na) for s, d, na, nb in S1E if nb == R]; lout = [(s, d, nb) for s, d, na, nb in S1E if na == L]
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
OWN, nt = F["owners"], 0
for e in effs:                                                                           # the reconnect table, row by row
    for row in e["reconnect"]:
        if row["side"] != "moved" or row["term_uid"] not in Rm:
            continue
        t = row["term_uid"]; mine = [(s, d, na, nb) for s, d, na, nb in S1E if (d == t if not row["is_source"] else s == t)]   # noqa: E702
        for s, d, na, nb in mine:
            other = na if not row["is_source"] else nb
            oc = S.obj_class(st0, other)
            if other in M or other in sr_ids:
                continue                                                                  # M-M edges below; SR rows above
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
                              "partner_diagram": (OWN.get(str(other)) or [None, None])[1], "cut_wire": row["cut_wire"]})
for s, d, na, nb in sorted(S1E):                                                          # every S1 M-M edge missing after the moves
    if na in M and nb in M and (s, d) not in Em:
        if s not in Rm or d not in Rm:
            AMBIG.append({"s1_edge": [s, d, na, nb], "why": "terminal absent from the base"}); continue   # noqa: E702
        WIRES.append({"op": "wire", "id": "rw_{0}_{1}".format(s, d), "src": {"uid": na, "term_uid": s}, "dst": {"uid": nb, "term_uid": d}})
flipped_src = [w for w in WIRES if not Rm[w["src"]["term_uid"]]["is_source"]]
A += [w for w in WIRES if w not in flipped_src] + flipped_src                              # flipped-source rows LAST
fact("RECONNECT: {0} S1-mapped re-wires (lost member/K edges) {1}; {2} of them need a source that reads is_source False after the moves: {3}".format(
     len(WIRES), [w["id"] for w in WIRES], len(flipped_src), [(w["id"], w["src"]) for w in flipped_src]))
for a in AMBIG: fact("AMBIGUOUS (not wired, stays open) " + json.dumps(a))              # noqa: E701
ctl = [a["id"] for a in A if a["op"] == "wire" and isinstance(a["dst"], dict) and S.obj_class(st0, a["dst"]["uid"]) == "ControlTerminal"]
fact("P5 sink_gates needed (wire rows whose SINK is a ControlTerminal, 179(b) reader): {0}".format(ctl))
def mk(open_rows):
    p = os.path.join(OUT, "stageplan_l2a1.json")
    json.dump({"schema": "stageplan/1", "stage": "l2a1", "goal": "L2-A1 (Pre-decided 181(d)): group A + reset controls + #23541 into 1.2 body #23166",
               "base": {"path": S._rel(BP), "md5": S.md5_file(BP)}, "context": {"s1_key": JC.S1_KEY}, "actions": A,
               "open_rows": [{"node": n, "term": t, "why": "PD181(d): simulator's finalized open-row list"} for n, t in open_rows]}, open(p, "w", encoding="utf-8"), indent=1)
    return p
gate("P0 plan validates as stageplan/1 ({0} actions)".format(len(A)), protocol.validate_obj(J(mk([])))[0])
sim = lambda o: S.simulate(mk(o), BP, out_root=os.path.join(HERE, "sim"), plan_out_dir=OUT, labels=LAB, log=print)   # noqa: E731
R = sim([])
gate("P2 every action applied (no SimError)", R["failed"] is None, R["failed"])
last = J(R["steps"][-1]["file"]["path"])["state"]
DRV = dict((r["owner_uid"], r["term_class"]) for r in st0["terminals"] if r["owner_class"] == "Tunnel" and not r["is_source"])
def orphan_tunnels(st):                   # P4: class 'Tunnel' whose BASE driving side has no sourced wire while its other side is wired
    by = collections.defaultdict(list); out = []                                         # noqa: E702
    for r in st["terminals"]:
        if r["owner_class"] == "Tunnel" and r["owner_uid"] in DRV: by[r["owner_uid"]].append(r)   # noqa: E701
    for u, rs in by.items():
        drv = [r for r in rs if r["term_class"] == DRV[u]]; oth = [r for r in rs if r["term_class"] != DRV[u]]   # noqa: E702
        if not any(r["wire_uid"] and S.has_source(st, r["wire_uid"]) for r in drv) and any(r["wire_uid"] for r in oth):
            out.append((u, [r["wire_uid"] for r in rs if r["wire_uid"]]))
    return sorted(out)
base_orph = set(u for u, _w in orphan_tunnels(st0)); P4 = {}
for s_ in R["steps"][1:]:
    for u, w in orphan_tunnels(J(s_["file"]["path"])["state"]):
        if u not in base_orph: P4.setdefault(u, (s_["n"], w))                              # noqa: E701
fact("P4 WIRED class-Tunnel orphaned by the plan (uid: first step, wires): {0}".format(P4 or "none"))
fr = lambda st: set(int(r["frame_diagram"]) for r in st["terminals"] if r["term_class"] == "InnerTerminal" and (OWN.get(str(V.node_of(r))) or [0, 0])[1] in (5540, 10445))
gate("P3b frame-diagram uid sets of #5540/#10445 equal before/after (181(b))", fr(st0) == fr(last) == {5582, 5592, 10453, 10459}, (sorted(fr(st0)), sorted(fr(last))))
if R["failed"] is None:
    s1p = J(os.path.join(JC.WIKI, JC.S1_KEY + ".json"))
    S1f = V.build4(s1p["terminals"], J(JC._newest("graph_objs_s1_*.json"))["objects"], J(JC._newest("graph_loops_s1_*.json"))["loops"], LAB, s1p["fs_tunnel_pairs"], frame_keyed=True)
    cf = lambda st: sorted(set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in V.computation_diff_frame(S1f, V.build4(st["terminals"], st["objs"], st["loops"], LAB, st["fs_pairs"], frame_keyed=True))["rows"]))   # noqa: E731
    b0, e0 = cf(st0), cf(last); mrg = sorted(set((V.key_parts(k)[0], V.key_parts(k)[2]) for k in R["end_cdiff_rows"] or []))   # noqa: E702
    fact("base frame cdiff {0} rows {1}".format(len(b0), b0)); fact("END frame cdiff {0} rows {1}; merged {2}".format(len(e0), e0, len(mrg)))   # noqa: E702
    R2 = sim(e0)
    gate("P3 FINAL: frame cdiff(S1, end) == the plan's open rows ({0}) and merged end rows agree".format(len(e0)), R2["final"] and e0 == mrg, (R2["final"], R2["failed"]))
else:
    gate("P3 FINAL: frame cdiff(S1, end) == PB", False, "not reached: simulation stopped at step {0}".format(R["failed"]))
fact("plan_out {0}; steps {1}; candidates {2}".format(R["plan_out"], len(R["steps"]) - 1, R["n_candidates"]))
n_pass = sum(1 for _l, ok in GATES if ok); first = next((l for l, ok in GATES if not ok), None)   # noqa: E702
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, len(GATES) - n_pass, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, len(GATES) - n_pass, first, [{"path": R["plan_out"]["path"], "md5": R["plan_out"]["md5"]}])))
