# ---
# labview: none
# hardware: none
# evidence: tools/bench/selftest_c155_basecase_frame.log:3
# ---
"""Self-test of card 155-a1-1 (docs/d1/ring-p5.md PD378(a)): a CaseStructure of the REAL base graph is addressed like a
plan-made one - `frame: "#<frame diagram uid>"` on its tunnel faces (stagesim.case_frame_of / case_frame_names,
stagexec.case_frame_op / base_case_of_frame) and its register-end tunnel groups (R1/R2 connect_term_uid, stagexec.compile_plan).
No LabVIEW, no COM: recorded graphs and logs only.

WHAT EXISTED FIRST: card 124-2/124-6 (case_frame_wire, R1/R2) for a case THIS plan made (selftest_case_frame_c124.py); card 126-3
FS faces '#<diagram uid>' (stagesim._fsit_rows, stagexec.FS_FACE_RE). This card adds the base-case lookup only.
PREDICTION (gates):
 M1/M2 frame index = position in the graph's frame list, measured on TWO cases and equal to LabVIEW's frame index:
   #30726 [30914, 30922] (graph bd67a511 vs Frames[k] binding diag_c154_p5s01a_scratch.log:144; Enqueue planned on 'True'
   = f1 sits on #30922); #22694 [27219, 27232] (graph_ring_p3a_20261001_190155.json vs stage_d1_ring_p3a.log:146 binding
   and :231/:256 - case_frame_wire frame 0 put Q&R.x on #27219).
 A  (a) P5-1b's 12 actions (plan_ring_p5s01_in.json 21..32, mapped as recorded at prep_c154_a4_1_mk.log:16-27, frame
   'False' -> '#30914') compile to the 8 op kinds of the whole-P5-1 compile ops 15..22 (prep_c154_a3_2b_mk.log:23-30):
   case_frame_wire, create, connect, add_sr, connect, connect_term_uid x2 (register_end_case_border), case_frame_wire;
   both frame wires case 30726 frame_index 0; same with owners passed explicitly; pass A simulates all 12 steps, the two
   frame wires' effect case_frame (30726, 0, '#30914').
 B  (b) a uid that is not a frame of #30726 is refused: compile (plan tunnel end, '#23166' and '#27219') and
   stagesim.resolve_addr (base tunnel #31175, '#23166'), each message naming case 30726 and its frames.
 C  (c) frame 'False' on the base case is still refused by compile and by resolve_addr (no name inference).
 D  (d) plan-made cases unchanged: plan_ring_p5s01.json and plan_ring_p5s01a.json compile EQUAL to the before-list
   (tools/bench/prep_c155_a1_1_compile_before.json, written before the edit); case_frame_of on a plan-made case unchanged.
 P  pins: stagekit aec03c6c, stage_prerun 9decb20f, addrcheck 207beb0d, gscript 1a80236e, vigraph a7eb58c7.
Usage: py tools/bench/selftest_c155_basecase_frame.py"""
import ast
import copy
import json
import os
import re
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagekit as SK  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402

B = lambda *p: os.path.join(ROOT, "tools", "bench", *p)  # noqa: E731
G5A = "tools/bench/graph_ring_p5s01a_20261009_103621.json"
G3A = "tools/bench/graph_ring_p3a_20261001_190155.json"
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


def refused(fn, exc):
    try:
        fn()
        return None
    except exc as e:
        return str(e)


def log_line(path, n):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().splitlines()[n - 1]


def bound_of(line):
    return dict((int(k), int(v)) for k, v in re.findall(r"(-?\d+): (\d+)", line.split("bound", 1)[1]))


# ---- M1: #30726
g5 = SK.jload(G5A)
gate("M0 inputs: graph bd67a511, p3a graph 2fa6ce0c, scratch log b60e27b9, step_20 c9c3a0b8, P5-1a plan ed62e8d6",
     SK.md5(os.path.join(ROOT, G5A)).startswith("bd67a511") and SK.md5(os.path.join(ROOT, G3A)).startswith("2fa6ce0c")
     and SK.md5(B("diag_c154_p5s01a_scratch.log")).startswith("b60e27b9")
     and SK.md5(B("sim", "ring_p5s01a", "step_20_wire.json")).startswith("c9c3a0b8")
     and SK.md5(B("plan_ring_p5s01a.json")).startswith("ed62e8d6"))
f1 = SS.base_case_frames(g5["owners"], 30726)
sym = SK.jload("tools/bench/sim/ring_p5s01a/step_20_wire.json")["state"]["sym"]
l144 = log_line(B("diag_c154_p5s01a_scratch.log"), 144)
bd = bound_of(l144)
lv1 = [bd[sym["new:CQ1.f0"]], bd[sym["new:CQ1.f1"]]]          # Frames[0], Frames[1] (stagexec._bind_create <- gscript.case_frames)
eq = [r["frame_diagram"] for r in g5["terminals"] if r["owner_uid"] == 30756][:1]
gate("M1 #30726: graph frame list == LabVIEW Frames[k] order (diag_c154_p5s01a_scratch.log:144); EQ1 planned on f1 sits on Frames[1]",
     f1 == lv1 == [30914, 30922] and eq == [30922], {"graph": f1, "lv": lv1, "EQ1 frame": eq, "log144": l144[:120]})
# ---- M2: #22694
g3 = SK.jload(G3A)
f2 = SS.base_case_frames(g3["owners"], 22694)
l146 = log_line(B("stage_d1_ring_p3a.log"), 146)
l231 = log_line(B("stage_d1_ring_p3a.log"), 231)
l256 = log_line(B("stage_d1_ring_p3a.log"), 256)
bd3 = bound_of(l146)
qr = re.search(r"'owner_uid': 27373, 'owner_class': 'Function', 'frame_diagram': (\d+)", l256)
gate("M2 #22694: graph frame list == binding order (stage_d1_ring_p3a.log:146) and frame 0 of case_frame_wire landed on its "
     "1st entry (:231 frame 0 -> Q&R #27373, :256 Q&R.x on #27219)",
     f2 == [bd3[-22], bd3[-23]] == [27219, 27232] and "case #22694 frame 0" in l231 and "'node': 27373" in l231
     and qr is not None and int(qr.group(1)) == f2[0], {"graph": f2, "bound": bd3, "qr": qr and qr.group(1)})

# ---- the mapped P5-1b actions (recorded data)
SIN = SK.jload("tools/bench/plan_ring_p5s01_in.json")
RAW = copy.deepcopy(SIN["actions"][20:32])
rows = {}
for n in range(16, 28):
    m = re.match(r"^FACT ROW (\S+) \S+: changed (.*)$", log_line(B("prep_c154_a4_1_mk.log"), n))
    rows[m.group(1)] = ast.literal_eval(m.group(2))
ACTS = []
for a in RAW:
    b = copy.deepcopy(a)
    for k, (old, new) in rows.get(a["id"], {}).items():
        assert b[k] == old, (a["id"], k)
        b[k] = new
    for e in (b.get("src"), b.get("dst")):
        if isinstance(e, dict) and e.get("frame") == "False":
            e["frame"] = "#30914"
    ACTS.append(b)
BASE = {"path": G5A, "md5": SK.md5(os.path.join(ROOT, G5A))}
TOP = {"schema": "stageplan/1", "context": SIN.get("context") or {"s1_key": "D1_s1_copy"}, "stage": "c155_p5s01b_selftest",
       "goal": "card 155-a1-1 self-test: P5-1b mapped on the P5-1a graph", "base": BASE}


def plan(acts):
    return dict(TOP, actions=acts)


gate("S0 the mapped 12 actions (ids w_false_pass..w_q_false) validate against stageplan/1 with frame '#30914'",
     [a["id"] for a in ACTS][::11] == ["w_false_pass", "w_q_false"] and protocol.validate_obj(plan(ACTS))[0],
     protocol.validate_obj(plan(ACTS)))
# ---- (a)
ops = SX.compile_plan(plan(ACTS))
want = ["case_frame_wire", "create", "connect", "add_sr", "connect", "connect_term_uid", "connect_term_uid", "case_frame_wire"]
cfw = [(o["case"], o["frame"], o["frame_index"], o["variant"]) for o in ops if o["kind"] == "case_frame_wire"]
ctu = [(o["acts"], o.get("variant"), o.get("case")) for o in ops if o["kind"] == "connect_term_uid"]
gate("A1 compile: kinds == whole-P5-1 ops 15..22 (prep_c154_a3_2b_mk.log:23-30); frame wires case 30726 index 0; groups R1/R2",
     [o["kind"] for o in ops] == want and [c[:3] for c in cfw] == [(30726, "#30914", 0)] * 2
     and ctu == [([6, 7, 8], "register_end_case_border", 30726), ([9, 10, 11], "register_end_case_border", 30726)],
     {"kinds": [o["kind"] for o in ops], "cfw": cfw, "ctu": ctu})
ops2 = SX.compile_plan({"actions": ACTS}, owners=g5["owners"])
gate("A2 compile with owners passed explicitly (no plan base) == A1", ops2 == ops, len(ops2))
gate("A3 compile WITHOUT a base (no owners) keeps the old shape: groups plain tunnel (the graph is what tells a base case)",
     [o["kind"] for o in SX.compile_plan({"actions": [a for a in ACTS if a["id"] not in ("w_false_pass", "w_q_false")]})]
     == ["create", "connect", "add_sr", "connect", "tunnel", "tunnel"])
tmp = tempfile.mkdtemp(prefix="c155_bc_")
pin = os.path.join(tmp, "plan_c155_p5s01b_selftest_in.json")
json.dump(plan(ACTS), open(pin, "w", encoding="utf-8"), indent=1)
R = SS.simulate(pin, os.path.join(ROOT, G5A), out_root=tmp, plan_out_dir=tmp, log=lambda *x: None, route_check=False)
cf = [(s.get("id"), (s.get("effect") or s.get("effect_summary") or {}).get("case_frame")) for s in R.get("steps") or []
      if s.get("id") in ("w_false_pass", "w_q_false")]
sids = [s.get("id") for s in R.get("steps") or [] if s.get("id") in set(a["id"] for a in ACTS)]
gate("A4 pass A on the real P5-1a graph: all 12 actions simulate (+ step 0 = base); the frame wires' case_frame = "
     "(30726, 0, '#30914', #30914)",
     R.get("failed") is None and sids == [a["id"] for a in ACTS]
     and all(c and (c.get("case"), c.get("index"), c.get("name"), c.get("diagram")) == (30726, 0, "#30914", 30914) for _i, c in cf)
     and len(cf) == 2, {"failed": R.get("failed"), "n": len(R.get("steps") or []), "cf": cf})
R2 = SS.simulate(pin, os.path.join(ROOT, G5A), out_root=os.path.join(tmp, "rc"), plan_out_dir=os.path.join(tmp, "rc"),
                 log=lambda *x: None, route_check=True)
rc = R2.get("route_check") or {}
un = [(r.get("k"), r.get("ids"), r.get("unroutable")) for r in rc.get("rows") or [] if r.get("unroutable")]
gate("A5 route check (stagexec dry backend on the BASE case): 8 rows, routes case_frame_wire x2 + connect_term_uid x2, no "
     "UNROUTABLE row (prep_c155_a1_1_probe.log: k6 'case #30726 sits on #None' before the dry parent fix)",
     R2.get("failed") is None and len(rc.get("rows") or []) == 8 and not un
     and [r.get("route") for r in rc.get("rows") or []].count("case_frame_wire") == 2
     and [r.get("route") for r in rc.get("rows") or []].count("connect_term_uid") == 2,
     {"status": rc.get("status"), "first_fail": str(rc.get("first_fail"))[:200], "un": un})
# ---- (b)
st = SS.base_state(g5)
for fr in ("#23166", "#27219"):
    bad = copy.deepcopy(ACTS)
    bad[-1]["src"]["frame"] = bad[-1]["dst"]["frame"] = fr
    e = refused(lambda: SX.compile_plan(plan(bad)), SX.ExecStop)
    gate("B1 compile refuses w_q_false frame {0!r} (not a frame of #30726), naming the case and its frames".format(fr),
         e is not None and "30726" in e and "#30914" in e and "#30922" in e, e)
e = refused(lambda: SS.resolve_addr(st, {"uid": 31175, "side": "inner", "frame": "#23166"}, True), SS.SimError)
gate("B2 stagesim.resolve_addr refuses base tunnel #31175 frame '#23166', naming case 30726 and its frames",
     e is not None and "30726" in e and "#30914" in e and "#30922" in e, e)
ok_ = SS.resolve_addr(st, {"uid": 31175, "side": "inner", "frame": "#30914"}, True)
gate("B3 resolve_addr #31175 frame '#30914' = its False-frame inner face t31177 (prep_c154_a4_1_mk.log:13)",
     ok_["term_uid"] == 31177, ok_)
# ---- (c)
for idx in (0, 11):
    bad = copy.deepcopy(ACTS)
    bad[idx]["src"]["frame"] = bad[idx]["dst"]["frame"] = "False"
    e = refused(lambda: SX.compile_plan(plan(bad)), SX.ExecStop)
    gate("C1 compile still refuses frame 'False' on base case #30726 ({0})".format(bad[idx]["id"]), e is not None, e)
e = refused(lambda: SS.resolve_addr(st, {"uid": 31175, "side": "inner", "frame": "False"}, True), SS.SimError)
gate("C2 resolve_addr refuses frame 'False' on base tunnel #31175 (a base case's frame is '#<diagram uid>')",
     e is not None and "never by name" in e, e)
# ---- (d)
before = SK.jload("tools/bench/prep_c155_a1_1_compile_before.json")
for p in ("tools/bench/plan_ring_p5s01.json", "tools/bench/plan_ring_p5s01a.json"):
    now = json.loads(json.dumps(SX.compile_plan(SK.jload(p)), sort_keys=True, default=str))
    gate("D1 {0} (plan-made case) compiles EQUAL to the before-list ({1} ops)".format(p, len(now)),
         before.get(p, {}).get("ops") == now, len((before.get(p) or {}).get("ops") or []))
w5 = SX.compile_plan(SK.jload("tools/bench/plan_ring_p5s01.json"))
gate("D2 whole P5-1 (plan-made CQ1): ops 15/22 case_frame_wire frame 'False' index 0 case 'new:CQ1'; 20/21 R1/R2",
     [(w5[k]["kind"], w5[k].get("frame"), w5[k].get("frame_index"), w5[k].get("case")) for k in (14, 21)]
     == [("case_frame_wire", "False", 0, "new:CQ1")] * 2
     and [w5[k].get("variant") for k in (19, 20)] == ["register_end_case_border"] * 2)
sp = {"owners": {"5": ["CaseStructure", 4], "6": ["CaseStructure", 4], "4": ["Diagram", 1]},
      "case_frames": {"4": [["False", 5], ["True", 6]]}}
gate("D3 case_frame_of / case_frame_names on a plan-made case: names from case_frames (unchanged)",
     SS.case_frame_of(sp, 6) == (4, 1, "True") and SS.case_frame_names(sp, 4) == [["False", 5], ["True", 6]]
     and SS.case_frame_of(dict(sp, case_frames={}), 6) == (4, 1, "#6"))
# ---- pins
pins = {"stagekit.py": "aec03c6c", "stage_prerun.py": "9decb20f", "addrcheck.py": "207beb0d", "gscript.py": "1a80236e",
        "vigraph.py": "a7eb58c7"}
got = dict((k, SK.md5(os.path.join(ROOT, "tools", k))[:8]) for k in pins)
gate("P1 protected pins unchanged", got == pins, got)
print("FACT stagexec.py", SK.md5(os.path.join(ROOT, "tools", "stagexec.py")), "stagesim.py",
      SK.md5(os.path.join(ROOT, "tools", "stagesim.py")))
npass = sum(1 for _l, ok in gates if ok)
nfail = len(gates) - npass
print(protocol.result_line({"status": "PASS" if not nfail else "FAIL", "gates": {"pass": npass, "fail": nfail},
                            "first_fail": next((l for l, ok in gates if not ok), None), "artefacts": []}))
sys.exit(1 if nfail else 0)
