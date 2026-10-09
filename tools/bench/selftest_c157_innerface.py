# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_157-a1-1.md
# ---
r"""selftest_c157_innerface - card 157-a1-1 (docs/d1/ring-p5.md PD381(b)(c)(d)), OFFLINE on recorded data (no LabVIEW, no COM).
Shared functions under test (stagexec): loop_inner_face_route (called by connect_route), route_on_state, fate_lines (called by
Executor.run after a move_in checkpoint read), checkpoint_ops (called by stagekit.RingSession). Data: plan_ring_p5s02a.json 4284c22a
and its sim steps tools/bench/sim/ring_p5s02a/ (step_15 b7da7fa7).
WHAT EXISTED FIRST: diag_c156_a3_1_route.py (the M1 cases, its private route() helper is now stagexec.route_on_state - the old
script is the record of what ran and is not rewritten); selftest_c156_passwire.py (shape of a replay self-test); stagexec.dry_run.
PREDICTION (gates):
 I1/I2  op 16 (#24360 -> 5760) and op 17 (#24367 -> 5778), on step_15 and on the executor's prev step: AS STORED -> 'cfw';
        WIRE 0 on the source -> 'cfw' too, same dst triple, src_diag 23405 (body of WhileLoop #23041 in the graph owners).
 C1     a recorded Case inner face (SelectorTunnel InnerTerminal, step_15) with wire 0 -> the EXISTING stop text, verbatim:
        'ADDRESS: #<t> is an INNER face of SelectorTunnel #<owner>: only the outer face's owner route is measured (l2a1_faces_81.log)'.
 C2     a FlatSequenceInnerTunnel inner face with wire 0 -> its existing stop ('is a FlatSequenceInnerTunnel face') - if one is
        recorded on step_15; else a FACT that none is.
 C3     #24360 wire 0 with its loop's owners entry relabelled CaseStructure (synthetic) -> the existing LoopTunnel inner-face stop.
 F1-F3  dry_run of plan_ring_p5s02a with a SYNTHETIC read (the SimBackend's read with these source faces set to wire 0: #24360
        after ops 10..15, #24367 after ops 10..16, #3060 after op 10; every other row as the sim keeps it) logs exactly six
        FATE lines, all step=10: w10394 src 3060 src_wire 0 | w24091 src 25235 src_wire 24091 | w24153 src 24367 src_wire 0 |
        w24285 src 24190 src_wire 24285 | w24312 src 24288 src_wire 24312 | w24330 src 24360 src_wire 0; sinks 5772 / 5787 /
        5778 / 5683 / 5782 / 5760 with sink_wire == the step_10 sim value (0); none for steps 11/12; status/first_fail equal
        to the unpatched dry_run's; ops 16/17 ran on the zeroed read and routed 'cfw'.
 K1/K2  RingSession(p5s02a inputs).CHECKPOINTS == checkpoint_ops == (0, 1,3,6,8,9,10,11,12,15,16,17); no recipe assigns CHECKPOINTS.
 P      pins: stagesim eb99c6ba, addrcheck 207beb0d, plan 4284c22a, step_15 b7da7fa7 unchanged.
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c157_innerface.log -- py -u tools/bench/selftest_c157_innerface.py"""
import glob
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402
import stagekit as K  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
PLAN = os.path.join(HERE, "plan_ring_p5s02a.json")
STOP_TXT = "ADDRESS: #{0} is an INNER face of {1} #{2}: only the outer face's owner route is measured (l2a1_faces_81.log)"


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


def md5(rel):
    with open(os.path.join(ROOT, rel), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def jl(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


P = jl(PLAN)
A = P["actions"]
OPS = SX.compile_plan(P)
STEPS = dict((int(s["n"]), os.path.join(ROOT, s["path"])) for s in P["finalized"]["step_files"])
state = lambda n: jl(STEPS[n])["state"]                                            # noqa: E731
end = lambda e: int(e["term_uid"]) if isinstance(e, dict) and e.get("term_uid") is not None else None   # noqa: E731
PINS = {"tools/stagesim.py": "eb99c6ba", "tools/addrcheck.py": "207beb0d", "tools/bench/plan_ring_p5s02a.json": "4284c22a",
        "tools/bench/sim/ring_p5s02a/step_15_tunnel.json": "b7da7fa7"}

print("---------- (i) wire-0 inner face of a While-loop tunnel routes as wired", flush=True)
for lab, k, src, dst in (("I1 op16", 16, 24360, 5760), ("I2 op17", 17, 24367, 5778)):
    op = OPS[k - 1]
    ok_ends = end(A[op["in_act"] - 1]["src"]) == src and end(A[op["out_act"] - 1]["dst"]) == dst
    for sn in sorted({15, op["acts"][0] - 1}):
        st = state(sn)
        k1, i1 = SX.route_on_state(st, src, dst)
        k0, i0 = SX.route_on_state(st, src, dst, zero_terms=[src])
        print("FACT {0} step_{1:02d} WIRED {2} dst {3} | WIRE 0 {4} {5}".format(lab, sn, k1, i1.get("dst") if k1 != "STOP" else i1,
                                                                             k0, i0 if k0 == "STOP" else (i0.get("dst"), i0.get("src_how"))), flush=True)
        gate("{0} step_{1:02d}: plan ends ({2} -> {3}); wired 'cfw'; wire 0 'cfw', same dst, src_diag 23405".format(lab, sn, src, dst),
             ok_ends and k1 == "cfw" and k0 == "cfw" and i1.get("dst") == i0.get("dst") and i0.get("src_wire0") is True
             and i0.get("src_diag") == 23405 and i0.get("src_loop") == 23041 and i0.get("src_loop_cls") == "WhileLoop", (k1, k0))

print("---------- (ii) Case / FS inner face with wire 0 still stops with the existing text", flush=True)
s15 = state(15)
sel = sorted((r for r in s15["terminals"] if r["owner_class"] == "SelectorTunnel" and r["term_class"] == "InnerTerminal"
              and r["wire_uid"] and r["is_source"]), key=lambda r: r["term_uid"])        # a SOURCE face, as ops 16/17's
r0 = sel[0]
k0, t0 = SX.route_on_state(s15, r0["term_uid"], 5760, zero_terms=[r0["term_uid"]])
want = STOP_TXT.format(r0["term_uid"], "SelectorTunnel", SX.V.node_of(r0))
gate("C1 recorded SelectorTunnel inner face #{0} (owner #{1}, frame #{2}, wire {3} -> 0) -> the existing stop verbatim".format(
    r0["term_uid"], r0["owner_uid"], r0["frame_diagram"], r0["wire_uid"]), k0 == "STOP" and t0 == want, t0)
fs = sorted((r for r in s15["terminals"] if r["owner_class"] == SX.FSIT_CLS and r["is_source"]),
            key=lambda r: r["term_uid"])
if fs:
    kf, tf = SX.route_on_state(s15, fs[0]["term_uid"], 5760, zero_terms=[fs[0]["term_uid"]])
    gate("C2 recorded FlatSequenceInnerTunnel face #{0} wire 0 -> its existing stop".format(fs[0]["term_uid"]),
         kf == "STOP" and "is a FlatSequenceInnerTunnel face" in str(tf), tf)
else:
    print("FACT C2 no FlatSequenceInnerTunnel InnerTerminal row on step_15 ({0} SelectorTunnel inner faces)".format(len(sel)), flush=True)
s15c = json.loads(json.dumps(s15))
s15c["owners"]["23405"] = ["CaseStructure", s15c["owners"]["23405"][1]]
k3, t3 = SX.route_on_state(s15c, 24360, 5760, zero_terms=[24360])
gate("C3 #24360 wire 0 with body 23405's owner relabelled CaseStructure (synthetic) -> the existing LoopTunnel stop",
     k3 == "STOP" and t3 == STOP_TXT.format(24360, "LoopTunnel", 24357), t3)

print("---------- (iii) FATE lines: dry_run of p5s02a on a synthetic read", flush=True)
DROP = {24360: (10, 15), 24367: (10, 16), 3060: (10, 10)}   # source face -> the ops after which the read shows wire 0
print("FACT synthetic read: the SimBackend read with these source faces at wire 0 after ops (first, last): {0}".format(DROP), flush=True)


class SynthBE(SX.SimBackend):
    """The dry backend whose READ shows LabVIEW having dropped the DROP faces' wires (its own state is untouched)."""

    def read(self):
        rows, n = super(SynthBE, self).read(), len(self.calls)
        for r in rows:
            lo_hi = DROP.get(r["term_uid"])
            if lo_hi and lo_hi[0] <= n <= lo_hi[1]:
                r["wire_uid"] = 0
        SEEN[n] = dict((r["term_uid"], int(r["wire_uid"] or 0)) for r in rows if r["term_uid"] in DROP)
        return rows


SEEN = {}   # ops applied -> the DROP faces' wires in the read taken then (dry_run reads after every op: op k routes on SEEN[k-1])


LOG0, LOG1 = [], []
st0, ff0, ex0 = SX.dry_run(PLAN, log=LOG0.append)
orig = SX.SimBackend
SX.SimBackend = SynthBE
try:
    st1, ff1, ex1 = SX.dry_run(PLAN, log=LOG1.append)
finally:
    SX.SimBackend = orig
fate = [ln.strip() for ln in LOG1 if ln.strip().startswith("FATE")]
for ln in fate:
    print("  " + ln, flush=True)
s10 = dict((r["term_uid"], int(r["wire_uid"] or 0)) for r in state(10)["terminals"])
EXP = [(10394, 3060, 0, 5772), (24091, 25235, 24091, 5787), (24153, 24367, 0, 5778), (24285, 24190, 24285, 5683),
       (24312, 24288, 24312, 5782), (24330, 24360, 0, 5760)]
want_f = ["FATE step=10 wire={0} src_term={1} src_wire={2} sink_term={3} sink_wire={4}".format(w, s, sw, t, s10.get(t))
          for w, s, sw, t in EXP]
gate("F1 exactly six FATE lines, all step=10, == the stated synthetic read (sink_wire = step_10 sim value)", sorted(fate) == sorted(want_f),
     {"got": fate, "want": want_f})
gate("F2 FATE lines in the unpatched dry run: six, step=10, src_wire = the sim's kept wire", len([x for x in LOG0 if x.strip().startswith("FATE")]) == 6,
     [x.strip() for x in LOG0 if x.strip().startswith("FATE")])
r16 = [r for r in ex1.report if r.get("k") in (16, 17)]
routes = [(((r.get("result") or {}).get("check") or {}).get("route"), r.get("k")) for r in r16]
gate("F3 synthetic run status/first_fail == unpatched ({0} / {1}); ops 16/17 routed 'cfw' on reads with #24360 / #24367 at wire 0".format(
    st0, str(ff0)[:120]), (st1, ff1) == (st0, ff0) and routes == [("cfw", 16), ("cfw", 17)]
     and (SEEN.get(15) or {}).get(24360) == 0 and (SEEN.get(16) or {}).get(24367) == 0,
     {"synthetic": (st1, str(ff1)[:300]), "routes": routes, "read15": SEEN.get(15), "read16": SEEN.get(16)})
print("FACT op 10-12 acts {0}; unpatched {1} {2}".format([OPS[k - 1]["acts"] for k in (10, 11, 12)], st0, str(ff0)[:200]), flush=True)

print("---------- (iv) checkpoints", flush=True)
rs = K.RingSession(PLAN, os.path.join(HERE, "plan_ring_p5s02a_pred.json"), os.path.join(HERE, "plan_ring_p5s02a_licence.json"),
                   os.path.join(HERE, "prep_c156_a1_1_session.json"))
want_cp = (0, 1, 3, 6, 8, 9, 10, 11, 12, 15, 16, 17)
gate("K1 RingSession(p5s02a).CHECKPOINTS == checkpoint_ops(ops) == {0}".format(want_cp),
     tuple(rs.CHECKPOINTS) == SX.checkpoint_ops(OPS) == want_cp, rs.CHECKPOINTS)
hits = [p for p in glob.glob(os.path.join(ROOT, "tools", "recipes", "*.py"))
        if re.search(r"\.CHECKPOINTS\s*=", open(p, encoding="utf-8", errors="replace").read())]
gate("K2 no recipe assigns .CHECKPOINTS (recipes stay inputs-only)", not hits, hits)

got = dict((k, md5(k)[:8]) for k in PINS)
gate("P pins unchanged", got == PINS, got)
print("FACT md5 stagexec {0} stagekit {1}".format(md5("tools/stagexec.py"), md5("tools/stagekit.py")), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
