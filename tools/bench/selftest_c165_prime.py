# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-3-1.md
# ---
r"""selftest_c165_prime - card 165-3-1 (docs/d1/ring-p5c.md PD402(b)), OFFLINE on the recorded graph 2a5fa0c4 (no LabVIEW, no COM).
Shared function under test: stagexec.prime_deleted_face_skip, called by Executor.run's PRIME pass. Plan maker CALLED, not copied:
prep_plan_flow_lib.make_step_plan with prep_c165_a2_1_mk.py:63-65's arguments, outputs redirected to tools/bench/sim/ring_p5s02e/_selftest165p.
WHAT EXISTED FIRST: selftest_c165_innerface.py (route of the post-delete inner face; stored-plan byte-equal B1/B2 - run with --pre for this card),
stagexec selftest T20/T22b (the non-collecting PRIME contract: be.unroutable = None).
PREDICTION (gates):
 A  make_step_plan(r_in 0b895983, K3f K4 K4f) chooses K3f+K4+K4f (13 rows); its SB gate passes: REALSIM final, route PASS, 0 UNROUTABLE.
 B1 Executor on that plan with a NON-collecting SimBackend: PRIME does not raise; exactly 2 PRIME-SKIP lines, ends #8776 (w10362) / #24342 (w25232).
 B2 the same run completes (no ExecStop).
 N1 no delete_wire op for w10362 -> PRIME raises naming #8776 (not #24342).   N2 the delete row names another wire (25232) -> PRIME raises #8776.
 N2b the w10362 delete op is not a checkpoint -> PRIME raises #8776.         N3 the delete op placed after the connect op -> PRIME raises #8776.
 U  prime_deleted_face_skip unit: LoopTunnel #8776 positive control -> skip; delete ACTION after the connect action -> None;
    wired SelectorTunnel inner sink and wired Flat-Sequence inner sink (FSIT, else 'Tunnel' on an FS frame) -> None.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/selftest_c165_prime.log -- py -u tools/bench/selftest_c165_prime.py"""
import os, sys                                                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, CD, ROOT, SX, SS = FL.L, FL.J, FL.md5, FL.CD, FL.ROOT, FL.SX, FL.SS
P = lambda n: os.path.normpath(os.path.join(B, n))                                           # noqa: E731
RR = os.path.join(B, "sim", "ring_p5s02e", "_selftest165p")
os.makedirs(RR, exist_ok=True)
gate = L.Gate(fatal_default=False)
GRAPH = P("graph_ring_p5s02d_20261010_154830.json")
VID, VIC = os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi"), os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi")
VIA, VIB = os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"), os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")
SRC = [{"name": "p5s02a", "plan": P("plan_ring_p5s02a.json"), "graph_after": P("graph_ring_p5s02a_20261010_032547.json"), "vi": VIA},
       {"name": "p5s02b", "plan": P("plan_ring_p5s02b.json"), "graph_after": P("graph_ring_p5s02b_20261010_111905.json"), "vi": VIB},
       {"name": "p5s02c", "plan": P("plan_ring_p5s02c.json"), "graph_after": P("graph_ring_p5s02c_20261010_131658.json"), "vi": VIC},
       {"name": "p5s02d", "plan": P("plan_ring_p5s02d.json"), "graph_after": GRAPH, "vi": VID}]
goal = lambda lo, hi, cand, ch: "card 165-3-1 SELFTEST (not a launch plan): step-5 A{0}..A{1} {2}".format(lo, hi, ch)   # noqa: E731
print("---------- (a) the step-5 plan finalizes", flush=True)
F = FL.make_step_plan(gate, P("plan_ring_p5s02r_in.json"), ["K3f", "K4", "K4f"], GRAPH, VID, P("plan_ring_p5s02d.json"), SRC, "c165-3-1",
                      "ring_p5s02e", os.path.join(RR, "plan_ring_p5s02e_in.json"), os.path.join(RR, "selftest165p_session.json"), goal,
                      "card 165-3-1 PROBE (self-test)", plan_out_dir=RR, sim_root=RR, census=P("prep_c165_a2_1_census.json"))
rc = F["realsim"]["route_check"]
nun = sum(1 for x in rc.get("rows") or [] if x.get("unroutable"))
gate("A chosen K3f+K4+K4f, 13 rows, REALSIM final, route {0}, UNROUTABLE {1}; plan {2}".format(rc.get("status"), nun, F["plan"]["md5"][:8]),
     F["chosen"] == "K3f+K4+K4f" and len(F["actions"]) == 13 and F["realsim"]["final"] and rc.get("status") == "PASS" and nun == 0, rc.get("first_fail"))
FIN = os.path.join(ROOT, F["plan"]["path"])
MODELS = SS.load_models()


def ex_run(mut=None):
    """Executor on FIN with a NON-collecting SimBackend (stagexec selftest T20 form); mut(ex) edits ops/plan/checkpoints first."""
    plan, _p = SX.load_final_plan(FIN, True)
    st = SS.base_state(J(plan["finalized"]["base"]["path"]), plan.get("context"))
    SS.seed_base_flips_modelled(st, MODELS)
    be = SX.SimBackend(plan, st, MODELS)
    be.unroutable = None
    lines = []
    ex = SX.Executor(FIN, be, log=lines.append)
    if mut:
        mut(ex)
    try:
        ex.run()
        return ex, None, lines
    except SX.ExecStop as e:
        return ex, str(e), lines


print("---------- (b) real-backend (non-collect) PRIME", flush=True)
ex, err, lines = ex_run()
sk = [ln for ln in lines if "PRIME-SKIP" in ln]
for ln in sk + [ln for ln in lines if ln.lstrip().startswith("PRIME ")]:
    print("FACT " + ln.strip(), flush=True)
gate("B1 PRIME silent on #8776 / #24342; 2 skips {0}".format(sorted((s["term"], s["wire"], s["del_op"]) for s in ex.prime_skips)),
     not str(err).startswith("PRIME") and sorted((s["term"], s["wire"]) for s in ex.prime_skips) == [(8776, 10362), (24342, 25232)], err)
gate("B2 the non-collect run completes ({0} ops)".format(len(ex.ops)), err is None, err)
ids = [a.get("id") for a in ex.plan["actions"]]
pos = lambda i: ids.index(i) + 1                                                            # noqa: E731
kop = lambda e, i: next(k for k, o in enumerate(e.ops, 1) if pos(i) in o["acts"])           # noqa: E731


def swap(e):
    a, b = kop(e, "dw_10362") - 1, kop(e, "w_k3f") - 1
    e.ops[a], e.ops[b] = e.ops[b], e.ops[a]


NEG = [("N1 no delete_wire op for w10362", lambda e: setattr(e, "ops", [o for o in e.ops if pos("dw_10362") not in o["acts"]])),
       ("N2 the delete row names another wire (25232)", lambda e: e.plan["actions"][pos("dw_10362") - 1].update(wire_uid=25232)),
       ("N2b the w10362 delete op is not a checkpoint", lambda e: setattr(e, "checkpoints", set(range(len(e.ops) + 1)) - {kop(e, "dw_10362")})),
       ("N3 the delete op placed after the connect op", swap)]
print("---------- (c) negatives still refuse", flush=True)
for lab, mut in NEG:
    e, err, lines = ex_run(mut)
    gate("{0} -> PRIME raises naming #8776 only; skips {1}".format(lab, [s["term"] for s in e.prime_skips]),
         str(err).startswith("PRIME: 1 wired end(s)") and "#8776" in str(err) and "#24342" not in str(err), err)
S0 = SS.base_state(J(GRAPH))
T = dict((r["term_uid"], r) for r in S0["terminals"])


def unit(row, order=("dw", "w")):
    A = {"dw": {"op": "delete_wire", "id": "dw", "wire_uid": int(row["wire_uid"])},
         "w": {"op": "wire", "id": "w", "dst": {"uid": row["owner_uid"], "term_uid": row["term_uid"]}}}
    acts = [A[x] for x in order]
    ops = [{"kind": "delete_wire" if a["op"] == "delete_wire" else "connect", "acts": [n]} for n, a in enumerate(acts, 1)]
    ops.sort(key=lambda o: o["kind"] != "delete_wire")                                     # the delete OP always first
    return SX.prime_deleted_face_skip(acts, ops, None, order.index("w") + 1, row)


gate("U0 positive control: LoopTunnel #8776 (w10362) -> skip", bool(unit(T[8776])), unit(T[8776]))
gate("U3 delete ACTION after the connect action (op still first) -> None", unit(T[8776], ("w", "dw")) is None)
wired = lambda cls, ok=lambda r: r["term_class"] == "InnerTerminal": sorted((r for r in S0["terminals"] if r["owner_class"] == cls   # noqa: E731
                                              and not r["is_source"] and int(r["wire_uid"] or 0) and ok(r)), key=lambda r: r["term_uid"])
fsf = set(k for k, v in (S0.get("owners") or {}).items() if v[0] in ("FlatSequenceFrame", SS.FS_CLS))
for lab, rows in (("SelectorTunnel", wired("SelectorTunnel")),
                  ("Flat Sequence", wired(SX.FSIT_CLS, lambda r: True) or wired("Tunnel", lambda r: str(r["frame_diagram"]) in fsf))):
    r0 = rows[0] if rows else None
    gate("N4 wired {0} inner sink {1} -> None".format(lab, r0 and (r0["term_uid"], r0["owner_class"], r0["owner_uid"], r0["wire_uid"])),
         r0 is not None and unit(r0) is None, len(rows))
gate("P graph 2a5fa0c4, stagesim 95a162ba, stagekit 22967183 unchanged", md5(GRAPH).startswith("2a5fa0c4") and md5(SS.__file__).startswith("95a162ba")
     and md5(FL.K.__file__).startswith("22967183"), (md5(GRAPH)[:8], md5(SS.__file__)[:8]))
print("FACT md5 stagexec {0}".format(md5(SX.__file__)), flush=True)
sys.exit(gate.result())
