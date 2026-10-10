# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_158-a2-1.md
# ---
r"""selftest_c158_wire0face - card 158-a2-1 (docs/d1/ring-p5.md PD385(a)(b)(c)), OFFLINE on recorded data (no LabVIEW, no COM).
Shared functions under test (stagexec): loop_face_wire0_act + struct_parent_diags (called by LVBackend.connect and
SimBackend.connect for a 'cfw' route whose info carries src_wire0), LVBackend.connect_term_uid (the existing verb wrapper and its
result checks, reused), state_addr (the Addr / loop_of / read of a recorded state, also used by route_on_state), checkpoint_ops.
Data: plan_ring_p5s02a.json 4284c22a and its sim steps tools/bench/sim/ring_p5s02a/ (the fixtures selftest_c157_innerface.py uses).
WHAT EXISTED FIRST: selftest_c157_innerface.py (route_on_state, the SynthBE read-only override of dry_run, the C1/C3 stop texts);
selftest_case_frame_c124.py L04 (LVBackend on fakes: object.__new__ + a recording gscript). Both are called/mirrored, not edited.
PREDICTION (gates):
 A1/A2  ops 16 (#24360 -> 5760) and 17 (#24367 -> 5778) through LVBackend.connect on a RECORDING backend, on step_15 and on the
        executor's prev step: face WIRED -> exactly one connect_from_wire to dst (1,1,6) / (1,1,9), no connect_term_uid;
        face WIRE 0 -> exactly one gscript.connect_term_uid(work, sink 5760 / 5778, src 24360 / 24367), no connect_from_wire,
        variant 'loop_inner_face_wire0', census == ROUTE_CENSUS register_end_case_border (dst on a case frame on body #23405),
        census_status UNMEASURED.
 A3     the reused result checks: no wire back / Is Broken? True / a junk Invoke left -> ExecStop (existing texts).
 S1     dry_run of p5s02a, unpatched: ops 16/17 check route 'cfw', triple [1,1,6] / [1,1,9], no 'act' key.
 S2     dry_run with the c157 synthetic read (#24360 wire 0 after ops 10..15, #24367 after 10..16, #3060 after 10): ops 16/17 route
        'cfw', same triples, check['act'] = connect_term_uid src 24360 / 24367 -> dst 5760 / 5778, census R1, UNMEASURED; status
        and first_fail equal to the unpatched run's.
 C1/C3  a SelectorTunnel inner face (C1) and #24360 with its body relabelled CaseStructure (C3), wire 0, through LVBackend.connect
        -> the existing stop text verbatim, nothing dispatched; C2 a FlatSequenceInnerTunnel face if one is recorded.
 V1-V4  loop_face_wire0_act: dst on the face's own diagram -> {Wire 1}; dst elsewhere -> None 'UNPREDICTED'; a row missing from
        the read -> ExecStop; 'loop_inner_face_wire0' NOT a key of ROUTE_CENSUS['connect_term_uid'] (U01 table unchanged).
 K1     checkpoint_ops(p5s02a) == (0,1,3,6,8,9,12,15,16,17).
 P      pins: stagesim 95a162ba (re-pinned 160-a2-1 from a3261b56; 160-a1-1 from eb99c6ba), addrcheck 207beb0d, stage_prerun 7605116f (re-pinned 159-f1-1 from 9decb20f), gscript 1a80236e, plan 4284c22a, step_15 b7da7fa7.
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c158_wire0face.log -- py -u tools/bench/selftest_c158_wire0face.py"""
import copy
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagexec as SX  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
PLAN = os.path.join(HERE, "plan_ring_p5s02a.json")
STOP_TXT = "ADDRESS: #{0} is an INNER face of {1} #{2}: only the outer face's owner route is measured (l2a1_faces_81.log)"
R1 = SX.ROUTE_CENSUS["connect_term_uid"]["register_end_case_border"]
WORK = "C:/fake/work.vi"


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


def raises(fn):
    try:
        fn()
    except SX.ExecStop as e:
        return str(e)
    return None


P = jl(PLAN)
OPS = SX.compile_plan(P)
STEPS = dict((int(s["n"]), os.path.join(ROOT, s["path"])) for s in P["finalized"]["step_files"])
state = lambda n: jl(STEPS[n])["state"]                                            # noqa: E731
CASES = (("op16", 16, 24360, 5760, [1, 1, 6]), ("op17", 17, 24367, 5778, [1, 1, 9]))


class RecS(object):
    """stagekit.Stage stand-in: records connect_from_wire, runs _op like the real one (err on exception)."""
    work = WORK

    def __init__(self, log):
        self.log = log

    def _op(self, verb, fn, detail=""):
        try:
            return {"verb": verb, "err": None, "result": fn(), "s": 0.0}
        except Exception as x:   # noqa: BLE001
            return {"verb": verb, "err": str(x), "result": None, "s": 0.0}

    def junk_purge(self, tag="", hints=()):
        return None

    def connect_from_wire(self, d, n, t, w, i, labels=None):
        self.log.append(("connect_from_wire", d, n, t, w, i))
        return {"err": None, "result": [True, 0, ""], "s": 0.0}


class RecG(object):
    """gscript stand-in: records connect_term_uid(target, sink_uid, src_uid) and answers like OpConnectTermUid_v0."""

    def __init__(self, log, **over):
        self.log, self.over = log, over

    def connect_term_uid(self, target, sink_uid, src_uid):
        self.log.append(("connect_term_uid", target, sink_uid, src_uid))
        r = {"wire_uid": 99001, "broken": False, "sink_echo": sink_uid, "src_echo": src_uid, "err": "", "purged": 0, "invoke_left": []}
        r.update(self.over)
        return r


class RecK(object):
    """stagekit stand-in: mod('build_opconnectfromwire_v0').wire_source_owner answers from the read's source rows."""

    def __init__(self, real, log):
        self.real, self.log = real, log

    def mod(self, name):
        rk = self

        class F(object):
            @staticmethod
            def wire_source_owner(target, w, n=8):
                rk.log.append(("wire_source_owner", w))
                return [{"owner_uid": SX.V.node_of(r), "is_source": True, "i": 0} for r in rk.real
                        if int(r["wire_uid"] or 0) == int(w) and r["is_source"]]
        return F


def lv_connect(st, src, dst, op, zero=(), **gover):
    """LVBackend.connect on a recording backend over recorded state `st` (faces in `zero` read at wire 0)."""
    s, addr, loop_of, real = SX.state_addr(st, zero)
    log = []
    be = object.__new__(SX.LVBackend)
    be.g, be.s, be.K, be.addr = RecG(log, **gover), RecS(log), RecK(real, log), addr
    try:
        out = be.connect(src, dst, real, loop_of, op)
    except SX.ExecStop as e:
        return "STOP", str(e), [x for x in log if x[0] != "wire_source_owner"]
    return "OK", out, [x for x in log if x[0] != "wire_source_owner"]


print("---------- (i) ops 16/17 through the act path (LVBackend.connect, recording backend)", flush=True)
for lab, k, src, dst, tri in CASES:
    op = OPS[k - 1]
    for sn in sorted({15, op["acts"][0] - 1}):
        st = state(sn)
        k1, o1, l1 = lv_connect(st, src, dst, op)
        k0, o0, l0 = lv_connect(st, src, dst, op, zero=[src])
        print("FACT A {0} step_{1:02d} WIRED {2} calls {3} how {4} | WIRE 0 {5} calls {6} variant {7} census {8} status {9!r}".format(
            lab, sn, k1, l1, (o1 or {}).get("how") if k1 == "OK" else o1, k0, l0, (o0 or {}).get("variant") if k0 == "OK" else o0,
            (o0 or {}).get("census") if k0 == "OK" else None, ((o0 or {}).get("census_status") or "")[:40] if k0 == "OK" else None), flush=True)
        gate("A {0} step_{1:02d} wired: ONE connect_from_wire to dst {2}, no connect_term_uid".format(lab, sn, tri),
             k1 == "OK" and len(l1) == 1 and l1[0][0] == "connect_from_wire" and list(l1[0][1:4]) == tri, l1)
        gate("A {0} step_{1:02d} wire 0: ONE connect_term_uid(work, sink {2}, src {3}), variant loop_inner_face_wire0, census R1, "
             "UNMEASURED".format(lab, sn, dst, src),
             k0 == "OK" and l0 == [("connect_term_uid", WORK, dst, src)] and o0.get("variant") == SX.LOOP_FACE_WIRE0
             and o0.get("census") == R1 and str(o0.get("census_status")).startswith("UNMEASURED") and o0.get("wire_uid") == 99001,
             (k0, l0, o0))
st15 = state(15)
e_nw = lv_connect(st15, 24360, 5760, OPS[15], zero=[24360], wire_uid=0)
e_br = lv_connect(st15, 24360, 5760, OPS[15], zero=[24360], broken=True)
e_iv = lv_connect(st15, 24360, 5760, OPS[15], zero=[24360], invoke_left=[9])
gate("A3 reused checks: no wire back / Is Broken? True / junk Invoke left -> ExecStop (existing texts)",
     e_nw[0] == "STOP" and "no wire came back" in e_nw[1] and e_br[0] == "STOP" and "Is Broken? True" in e_br[1]
     and e_iv[0] == "STOP" and "junk Invoke" in e_iv[1], (e_nw[1], e_br[1], e_iv[1]))

print("---------- (i') ops 16/17 through the dry act path (SimBackend.connect via dry_run)", flush=True)
DROP = {24360: (10, 15), 24367: (10, 16), 3060: (10, 10)}   # the c157 F1-F3 synthetic read
SEEN = {}


class SynthBE(SX.SimBackend):
    """The dry backend whose READ shows LabVIEW having dropped the DROP faces' wires (its own state is untouched) - c157's."""

    def read(self):
        rows, n = super(SynthBE, self).read(), len(self.calls)
        for r in rows:
            lo_hi = DROP.get(r["term_uid"])
            if lo_hi and lo_hi[0] <= n <= lo_hi[1]:
                r["wire_uid"] = 0
        SEEN[n] = dict((r["term_uid"], int(r["wire_uid"] or 0)) for r in rows if r["term_uid"] in DROP)
        return rows


def chk_of(ex, k):
    r = next((x for x in ex.report if x.get("k") == k), {})
    return (r.get("result") or {}).get("check") or {}


st0, ff0, ex0 = SX.dry_run(PLAN, log=lambda m: None)
orig = SX.SimBackend
SX.SimBackend = SynthBE
try:
    st1, ff1, ex1 = SX.dry_run(PLAN, log=lambda m: None)
finally:
    SX.SimBackend = orig
for lab, k, src, dst, tri in CASES:
    c0, c1 = chk_of(ex0, k), chk_of(ex1, k)
    print("FACT S {0} unpatched {1} | synthetic {2}".format(lab, c0, c1), flush=True)
    # the dry backend's Diagram index is its own list's (183 on the full graph); node / terminal = the state_addr triple's
    gate("S1 {0} unpatched dry: route 'cfw', triple [*, {1}, {2}], no 'act'".format(lab, tri[1], tri[2]),
         c0.get("route") == "cfw" and (c0.get("triple") or [None])[1:] == tri[1:] and "act" not in c0, c0)
    a = c1.get("act") or {}
    gate("S2 {0} wire-0 dry: route 'cfw', SAME triple as unpatched, act connect_term_uid {1} -> {2}, census R1, UNMEASURED".format(
        lab, src, dst),
         c1.get("route") == "cfw" and c1.get("triple") == c0.get("triple") and a.get("act") == "connect_term_uid" and a.get("src_term") == src
         and a.get("dst_term") == dst and a.get("census") == R1 and str(a.get("census_status")).startswith("UNMEASURED"), c1)
gate("S2 synthetic status/first_fail == unpatched ({0}); reads 15/16 show #24360 / #24367 at wire 0".format(st0),
     (st1, ff1) == (st0, ff0) and (SEEN.get(15) or {}).get(24360) == 0 and (SEEN.get(16) or {}).get(24367) == 0,
     ((st1, str(ff1)[:200]), SEEN.get(15), SEEN.get(16)))

print("---------- (ii) Case / FS inner face with wire 0 still stops (act path)", flush=True)
sel = sorted((r for r in st15["terminals"] if r["owner_class"] == "SelectorTunnel" and r["term_class"] == "InnerTerminal"
              and r["wire_uid"] and r["is_source"]), key=lambda r: r["term_uid"])
r0 = sel[0]
kc, tc, lc = lv_connect(st15, r0["term_uid"], 5760, OPS[15], zero=[r0["term_uid"]])
gate("C1 SelectorTunnel inner face #{0} wire 0 -> the existing stop verbatim, nothing dispatched".format(r0["term_uid"]),
     kc == "STOP" and tc == STOP_TXT.format(r0["term_uid"], "SelectorTunnel", SX.V.node_of(r0)) and not lc, (tc, lc))
fs = sorted((r for r in st15["terminals"] if r["owner_class"] == SX.FSIT_CLS and r["is_source"]), key=lambda r: r["term_uid"])
if fs:
    kf, tf, lf = lv_connect(st15, fs[0]["term_uid"], 5760, OPS[15], zero=[fs[0]["term_uid"]])
    gate("C2 FlatSequenceInnerTunnel face #{0} wire 0 -> its existing stop".format(fs[0]["term_uid"]),
         kf == "STOP" and "is a FlatSequenceInnerTunnel face" in str(tf) and not lf, (tf, lf))
else:
    print("FACT C2 no FlatSequenceInnerTunnel source row on step_15 ({0} SelectorTunnel inner source faces)".format(len(sel)), flush=True)
s15c = copy.deepcopy(st15)
s15c["owners"]["23405"] = ["CaseStructure", s15c["owners"]["23405"][1]]
k3, t3, l3 = lv_connect(s15c, 24360, 5760, OPS[15], zero=[24360])
gate("C3 #24360 wire 0, body relabelled CaseStructure -> the existing LoopTunnel stop, nothing dispatched",
     k3 == "STOP" and t3 == STOP_TXT.format(24360, "LoopTunnel", 24357) and not l3, (t3, l3))

print("---------- (iii) the census variant", flush=True)
_s, _a, _l, real = SX.state_addr(st15, [24360])
rs = next(r for r in real if r["term_uid"] == 24360)
rd = next(r for r in real if r["term_uid"] == 5760)
v0 = SX.loop_face_wire0_act(real, rs, rd, st15["owners"])
print("FACT V0 {0}".format(v0), flush=True)
gate("V0 op16 on step_15: dst on a frame of a CaseStructure on body #23405 -> census R1 {0}".format(R1),
     v0["census"] == R1 and SX.struct_parent_diags(real, int(st15["owners"][str(rd["frame_diagram"])][1]), st15["owners"]) == [23405], v0)
rd_same = dict(rd, frame_diagram=rs["frame_diagram"])
v1 = SX.loop_face_wire0_act(real + [rd_same], rs, rd_same, st15["owners"])
gate("V1 dst on the face's own diagram (synthetic) -> census {'Wire': 1}, UNMEASURED", v1["census"] == {"Wire": 1}
     and v1["census_status"].startswith("UNMEASURED"), v1)
rd_far = dict(rd, frame_diagram=int(rs["frame_diagram"]) + 7)
v2 = SX.loop_face_wire0_act(real + [rd_far], rs, rd_far, st15["owners"])
gate("V2 dst on an unknown diagram (synthetic) -> census None, UNPREDICTED", v2["census"] is None and v2["census_status"] == "UNPREDICTED", v2)
e4 = raises(lambda: SX.loop_face_wire0_act([r for r in real if r["term_uid"] != 24360], rs, rd, st15["owners"]))
gate("V3 the face row missing from the read -> ExecStop naming it", e4 is not None and "24360" in e4, e4)
gate("V4 'loop_inner_face_wire0' is NOT a key of ROUTE_CENSUS['connect_term_uid'] (U01's table unchanged)",
     SX.LOOP_FACE_WIRE0 not in SX.ROUTE_CENSUS["connect_term_uid"], sorted(SX.ROUTE_CENSUS["connect_term_uid"]))

print("---------- (iv) checkpoints", flush=True)
gate("K1 checkpoint_ops(p5s02a) == (0,1,3,6,8,9,12,15,16,17)", SX.checkpoint_ops(OPS) == (0, 1, 3, 6, 8, 9, 12, 15, 16, 17),
     SX.checkpoint_ops(OPS))
PINS = {"tools/stagesim.py": "95a162ba", "tools/addrcheck.py": "207beb0d", "tools/stage_prerun.py": "7605116f",
        "tools/gscript.py": "1a80236e", "tools/bench/plan_ring_p5s02a.json": "4284c22a",
        "tools/bench/sim/ring_p5s02a/step_15_tunnel.json": "b7da7fa7"}
got = dict((k, md5(k)[:8]) for k in PINS)
gate("P pins unchanged", got == PINS, got)
print("FACT md5 stagexec {0} stagekit {1}".format(md5("tools/stagexec.py"), md5("tools/stagekit.py")), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
