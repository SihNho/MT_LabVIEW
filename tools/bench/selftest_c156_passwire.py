# ---
# labview: none
# hardware: none
# evidence: tools/bench/prep_c156_a1_2_measure.log
# ---
r"""Self-test of card 156-a1-2 (docs/d1/ring-p5.md PD379(b)): the PASS WIRE of a case in-tunnel group - SR L.inner -> case
in-tunnel I -> pass wire in the in-tunnel's frame -> case out-tunnel O (made earlier, its group in the OTHER frame) - is
written with `frame: <the in-tunnel's body frame>` on its DST end and stays the group's one out-wire
(stagexec.case_pass_wire, called by compile_plan's tunnel-group rule). stagesim is unchanged: with the dst `frame` it
resolves O's inner face on the in-tunnel's frame (resolve_addr) and replays a same-diagram wire.
No LabVIEW, no COM: the recorded P5-1 graph graph_ring_p5s01_20261009_125622.json (6716c499) and the K rows the 156-a1-1 maker
wrote (plan_ring_p5s02r_in.json d84634bd, actions 61..80; its first 60 = plan_ring_p5s02r_all.json 15da9551), via
prep_c156_a1_2_lib (k_actions, sim_plan, last_state).
WHAT EXISTED FIRST: compile's tunnel group (stagexec.py:850-876, card 120-3/124-6 R1/R2), the frame wire of a plan-made case
(card 124-2, G/H/I `w_*pass` rows with `frame` on BOTH ends after both groups), the base-case frame (card 155-a1-1).
PREDICTION (gates):
 A  (a) K3 + K3f with frame 'True' on w_k3pass: compile accepts; acts 67..69 = ONE connect_term_uid register_end_case_border
    on new:CQ7 (out_act 69); every K op kind is a kind the 12 other groups use; simulate all 70 actions, failed None,
    0 PROVISIONAL; w_k3pass effect = same-diagram wire on CQ7 frame 'True' (index 1); route check: no UNROUTABLE row names
    a K R1 group, and the 60-action baseline's UNROUTABLE rows (G/H out-groups, measured in the first run of this test, not
    touched by this card) recur unchanged; w_k<k>f (feed form T into a LoopTunnel INNER face) is reported as a FACT;
    end state: SK3 R.inner's net holds OK3.outer and #5204 inner t8776, and #5204 outer t9631's net still holds #6384 t6480
    and #2048 t3182 (the P5-1 t3 sinks).
 B  (b) the same for K4 + K4f: #10404 inner t24342 on SK4 R.inner's net; #10404 outer t24363 -> #6384 t6511.
 AB K3, K3f, K4, K4f together (80 actions): compile + simulate to the end, 0 PROVISIONAL, route check no UNROUTABLE.
 C  (c) the old refusal still fires: the frameless pass wire (as written) fails in stagesim at action 69 with 'source on
    diagram -30, sink on diagram -29 - a border needs a tunnel/register action first' (stagesim.py:1536); compile refuses a
    pass-wire `frame` that is not the in-tunnel's own frame ('False') and a `frame` dst that is not an earlier tunnel of the
    same case (SK3R), each with the case_pass_wire message.
 D  (d) ordinary plan-made case groups unchanged: plan_ring_p5s02r_all.json (G/H/I pass wires), p5s02a, p5s01a, p5s01b,
    p5s01_in compile EQUAL to tools/bench/sim/ring_p5s02pw/compile_before.json (written before the edit).
 P  pins: stagekit aec03c6c, stage_prerun 9decb20f, addrcheck 207beb0d, gscript 1a80236e, vigraph a7eb58c7; stagesim eb99c6ba.
Usage: py tools/bench/selftest_c156_passwire.py"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import protocol  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402
import prep_c156_a1_2_lib as L  # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


def refused(fn, exc):
    try:
        fn()
        return None
    except exc as e:
        return str(e)


def net(st, tu):
    """[(owner, term_uid, term_class, frame)] of the wire terminal tu sits on in state st ([] when unwired)."""
    w = next((r["wire_uid"] for r in st["terminals"] if r["term_uid"] == tu), 0)
    return sorted(set((r["owner_uid"], r["term_uid"], r["term_class"], r["frame_diagram"]) for r in st["terminals"]
                      if w and r["wire_uid"] == w))


gate("M0 inputs: graph 6716c499, plan_ring_p5s02r_in d84634bd, plan_ring_p5s02r_all 15da9551; first 60 actions equal",
     L.md5(L.GRAPH).startswith("6716c499") and L.md5(L.RIN).startswith("d84634bd") and L.md5(L.ALLF).startswith("15da9551")
     and L.jload(L.RIN)["actions"][:60] == L.jload(L.ALLF)["actions"])
TOP0, ALL60 = L.k_actions(())
OTHER = set(o["kind"] for o in SX.compile_plan(dict(TOP0, actions=ALL60)))
K_PASS_IDS = ["t_k3o", "w_k3out", "w_k3r", "t_k3i", "w_k3l", "w_k3pass", "t_k4o", "w_k4out", "w_k4r", "t_k4i", "w_k4l", "w_k4pass"]
R60 = L.sim_plan(TOP0, ALL60, "pw_all60", route_check=True)
RC60 = R60.get("route_check") or {}
BASE_UN = [(r.get("k"), r.get("ids"), r.get("unroutable")) for r in RC60.get("rows") or [] if r.get("unroutable")]
BASE_UN_K = set(u[0] for u in BASE_UN)
print("FACT ROUTE-UN baseline (plan_ring_p5s02r_all.json's 60 actions, no K row, tools as edited): status {0}; {1}".format(
    RC60.get("status"), BASE_UN), flush=True)
SINKS = {"3":(5204, 8776, 9631, [(6384, 6480), (2048, 3182)]), "4": (10404, 24342, 24363, [(6384, 6511)])}


def k_case(k, groups, name):
    top, acts = L.k_actions(groups, pass_frame="True")
    ops = SX.compile_plan(dict(top, actions=acts))
    kops = [o for o in ops if max(o["acts"]) >= 61]                 # the K rows follow the 60 all-plan actions
    ctu = [(o["acts"], o.get("variant"), o.get("case"), o.get("out_act")) for o in kops if o["kind"] == "connect_term_uid"]
    print("FACT {0} K ops {1}".format(name, [(o["kind"], o["acts"], o.get("variant") or o.get("route")) for o in kops]), flush=True)
    R = L.sim_plan(top, acts, name, route_check=True)
    prov = [s["n"] for s in R.get("steps") or [] if s.get("provisional")]
    rc = R.get("route_check") or {}
    un = [(r.get("k"), r.get("ids"), r.get("unroutable")) for r in rc.get("rows") or [] if r.get("unroutable")]
    return top, acts, ops, kops, ctu, R, prov, rc, un


for k in ("3", "4"):
    top, acts, ops, kops, ctu, R, prov, rc, un = k_case(k, ("K" + k, "K" + k + "f"), "pw_k" + k)
    gate("A{0}1 compile K{0}+K{0}f (frame 'True' on w_k{0}pass): acts 67..69 = ONE connect_term_uid register_end_case_border on "
         "new:CQ7, out_act 69; K op kinds within the other groups' kinds {1}".format(k, sorted(OTHER)),
         [c for c in ctu if c[0] == [67, 68, 69]] == [([67, 68, 69], "register_end_case_border", "new:CQ7", 69)]
         and set(o["kind"] for o in kops) <= OTHER, ctu)
    st = L.last_state(R)
    pw = next((s for s in R.get("steps") or [] if s.get("id") == "w_k{0}pass".format(k)), {})
    eff = pw.get("effect") or pw.get("effect_summary") or {}
    gate("A{0}2 simulate all {1} actions: failed None, 0 PROVISIONAL; w_k{0}pass = same-diagram wire on CQ7 frame 'True' "
         "(index 1)".format(k, len(acts)),
         R.get("failed") is None and len(R.get("steps") or []) == len(acts) + 1 and not prov
         and (eff.get("case_frame") or {}).get("name") == "True" and (eff.get("case_frame") or {}).get("index") == 1,
         {"failed": R.get("failed"), "steps": len(R.get("steps") or []), "prov": prov, "cf": eff.get("case_frame")})
    kun = [u for u in un if set(u[1] or []) & set(K_PASS_IDS)]
    print("FACT ROUTE-UN pw_k{0}: {1}".format(k, un), flush=True)
    gate("A{0}3 route check (dry backend): rows for every op; no UNROUTABLE row names a K{0} R1 group (t_k{0}o/t_k{0}i, w_k{0}pass); "
         "the other UNROUTABLE rows are the 60-action baseline's G/H rows plus w_k{0}f (feed form T, not this card's fix)".format(k),
         len(rc.get("rows") or []) == len(ops) and not kun and [u for u in un if u[0] in BASE_UN_K] == BASE_UN,
         {"status": rc.get("status"), "rows": len(rc.get("rows") or []), "k_un": kun, "un": un})
    tun, tin, tout, sinks = SINKS[k]
    sr = st["sym"]["new:SK{0}R".format(k)]
    ri = next(r["term_uid"] for r in st["terminals"] if r["owner_uid"] == sr and r["term_class"] == "InnerTerminal")
    n_r, n_o = net(st, ri), net(st, tout)
    print("FACT SINK K{0} SK{0} R.inner t{1} net {2}".format(k, ri, n_r), flush=True)
    print("FACT SINK K{0} #{1} outer t{2} net {3}".format(k, tun, tout, n_o), flush=True)
    gate("A{0}4 end state: SK{0} R.inner's net holds OK{0}.outer and #{1} inner t{2}; #{1} outer t{3}'s net holds the P5-1 t{0} "
         "sinks {4}".format(k, tun, tin, tout, sinks),
         any(o == st["sym"]["new:OK" + k] and c == "OuterTerminal" for o, _t, c, _f in n_r) and any(t == tin for _o, t, _c, _f in n_r)
         and all(any((o, t) == s for o, t, _c, _f in n_o) for s in sinks), {"R.inner": n_r, "outer": n_o})
top, acts, ops, kops, ctu, R, prov, rc, un = k_case("34", ("K3", "K3f", "K4", "K4f"), "pw_k34")
gate("AB K3+K3f+K4+K4f ({0} actions): compile {1} ops, two R1 groups for the pass wires; simulate failed None, 0 PROVISIONAL; "
     "route check rows for every op, no UNROUTABLE row names a K R1 group".format(len(acts), len(ops)),
     len([c for c in ctu if c[3] in (69, 79)]) == 2 and R.get("failed") is None and len(R.get("steps") or []) == len(acts) + 1
     and not prov and len(rc.get("rows") or []) == len(ops) and not [u for u in un if set(u[1] or []) & set(K_PASS_IDS)]
     and [u for u in un if u[0] in BASE_UN_K] == BASE_UN,
     {"ctu": ctu, "failed": R.get("failed"), "un": un, "rc": rc.get("status"), "rows": len(rc.get("rows") or [])})
# ---- (c)
top, acts = L.k_actions(("K3",))
gate("C1 as written (frameless pass dst) compile still accepts the group (stagexec unchanged for it)",
     refused(lambda: SX.compile_plan(dict(top, actions=acts)), SX.ExecStop) is None)
R = L.sim_plan(top, acts, "pw_c_old")
f = R.get("failed") or {}
gate("C2 as written: stagesim refuses action 69 w_k3pass with the stagesim.py:1536 border message (faces on -30 / -29)",
     f.get("n") == 69 and f.get("id") == "w_k3pass" and "source on diagram -30, sink on diagram -29 - a border needs a "
     "tunnel/register action first" in str(f.get("error")), f)
top, acts = L.k_actions(("K3",), pass_frame="False")
e = refused(lambda: SX.compile_plan(dict(top, actions=acts)), SX.ExecStop)
gate("C3 compile refuses frame 'False' on the pass dst (not the in-tunnel's body frame 'True')",
     e is not None and "must name the in-tunnel's own body frame 'True'" in e, e)
top, acts = L.k_actions(("K3",), pass_frame="True")
acts[-1]["dst"] = {"uid": "new:SK3R", "side": "inner", "frame": "True"}
e = refused(lambda: SX.compile_plan(dict(top, actions=acts)), SX.ExecStop)
gate("C4 compile refuses a `frame` pass dst that is not an earlier tunnel of the same case (SK3R inner)",
     e is not None and "must be the INNER face of an earlier tunnel of the same case" in e, e)
# ---- (d)
before = L.jload(os.path.join(L.SIMD, "compile_before.json"))
for p in ("plan_ring_p5s02r_all.json", "plan_ring_p5s02a.json", "plan_ring_p5s01a.json", "plan_ring_p5s01b.json", "plan_ring_p5s01_in.json"):
    k_ = "tools/bench/" + p
    now = json.loads(json.dumps(SX.compile_plan(L.jload(os.path.join(HERE, p))), sort_keys=True, default=str))
    gate("D {0} compiles EQUAL to the before-list ({1} ops)".format(p, len(now)), (before.get(k_) or {}).get("ops") == now,
         len((before.get(k_) or {}).get("ops") or []))
# ---- pins
pins = {"stagekit.py": "aec03c6c", "stage_prerun.py": "9decb20f", "addrcheck.py": "207beb0d", "gscript.py": "1a80236e",
        "vigraph.py": "a7eb58c7", "stagesim.py": "eb99c6ba"}
got = dict((k_, L.md5(os.path.join(ROOT, "tools", k_))[:8]) for k_ in pins)
gate("P protected pins unchanged (stagesim not edited)", got == pins, got)
print("FACT stagexec.py", L.md5(os.path.join(ROOT, "tools", "stagexec.py")), "stagesim.py", L.md5(os.path.join(ROOT, "tools", "stagesim.py")))
npass = sum(1 for _l, ok in gates if ok)
nfail = len(gates) - npass
print(protocol.result_line({"status": "PASS" if not nfail else "FAIL", "gates": {"pass": npass, "fail": nfail},
                            "first_fail": next((l for l, ok in gates if not ok), None), "artefacts": []}))
sys.exit(1 if nfail else 0)
