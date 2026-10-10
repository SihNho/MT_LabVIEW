# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c158_a2_3_facts.md
# ---
r"""selftest_c158_gates386 - card 158-a3-1 (docs/d1/ring-p5.md PD386(a)(b)(c)), OFFLINE on the RECORDED c158-a2-2 scratch (no LabVIEW).
Shared functions under test (stagekit, the ones RingSession.gate_pb / gates_ng_fr_d / gate_td / gate_cen2 call): pb_386 (-> frame_tag_map,
frame_src_resolve, case_move_frames, pb_check_bound, pb_check), term_identity_pairs (-> wire_pairs_pos, term_identity_pos),
run_bind, real_rows_from_record, scratch_census, Stage.census_gate.
Data: diag_c156_p5s02a_scratch.json (the c158-a2-2 run: real_end_rows, stagexec `bound`), its log (last segment), the plan's sim end
(plan_ring_p5s02a.json step_files[-1]), graph 6716c499 (the plan's base), plan_ring_p5s02a_pred.json.
PREDICTION (gates):
 P0  inputs md5 pins; bindings from the json == the log's `bound {...}` lines (12 uids); real rows rebuilt, 0 unmatched.
 P1  the sim tag '@-44/f1' resolves to frame -29 (bound 31506) and the real '@31546/f0' to 31506: the ordinal flip is neutralised.
 A1  PB on the recorded data: ok, real == sim-bound row for row, RECORDED = the two #376 rows (cal cluster path, file size), none blocked.
 A2  D / TD on the recorded data: d_ok, td_ok; RECORDED source-only stub = wire 24091's end (25223, 1, InnerTerminal) on the sim side only;
     the TD unwired entry (25223, 1, InnerTerminal, True) is recorded, not blocking.
 A3  control: the OLD gates (pb_check, term_identity_gates) on the same data still fail (PB extra 2 rows; D 21 vs 22; TD unwired 1).
 B1  re-sourced #376 'cal cluster path' (same sink, source t3060's wire) -> PB BLOCK.
 B2  tag on a frame that is NOT the plan's (tunnel 31546's inner faces swap frames 31506 <-> 31517): real only -> PB BLOCK; the same swap
     on BOTH sides (equality holds) -> PB BLOCK by the frame rule.
 B3  TF1's outer fed from t24367's wire (source 1766 under tag @31546): real only -> BLOCK; on both sides -> BLOCK by the S1-uid rule.
 B4  a new pair on real only (an unwired base sink wired to t3060's wire) -> D BLOCK.
 B5  a sink-bearing wire dropped on real only (t3060's wire, whole wire; and sinks only, leaving a stub) -> D BLOCK both ways.
 B6  CEN2: census == the pred's MEASURED-SCRATCH census -> PASS; one class +1 -> FAIL; pred census_overall == MEASURED-SCRATCH and
     == the scratch log's CENSUS-ALL line (scratch_census).
Usage: py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_c158_gates386.log -- py -u tools/bench/selftest_c158_gates386.py"""
import copy
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

PLAN, PRED = os.path.join(K.BENCH, "plan_ring_p5s02a.json"), os.path.join(K.BENCH, "plan_ring_p5s02a_pred.json")
LIC, SGC = os.path.join(K.BENCH, "plan_ring_p5s02a_licence.json"), os.path.join(K.BENCH, "prep_c156_a1_1_session.json")
REAL, RLOG = os.path.join(K.BENCH, "diag_c156_p5s02a_scratch.json"), os.path.join(K.BENCH, "diag_c156_p5s02a_scratch.log")
PINS = {PLAN: "4284c22a", os.path.join(K.BENCH, "graph_ring_p5s01_20261009_125622.json"): "6716c499"}
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


V, SX = K.pure("vigraph"), K.pure("stagexec")
RS = K.RingSession(PLAN, PRED, LIC, SGC)
L0 = RS.SIM_END
D = K.jload(REAL)
gate("P0a input md5 pins (plan, base graph)", all(K.md5(p).startswith(m) for p, m in PINS.items()), dict((os.path.basename(p), K.md5(p)[:8]) for p in PINS))
FLAT = K.run_bind(report=D["stagexec"])
seg = open(RLOG, encoding="utf-8", errors="replace").read().split("BGRUN START")[-1]
logb = {}
for m in re.finditer(r"STEPX \d+ .*? bound (\{[^}]*\}) diff", seg):
    logb.update(dict((int(k), int(v)) for k, v in json.loads(re.sub(r"(-?\d+):", r'"\1":', m.group(1))).items()))
gate("P0b bindings: json stagexec `bound` == the log's last-segment `bound {...}` lines (12 uids)", FLAT == logb and len(FLAT) == 12, (FLAT, logb))
REAL_ROWS, AL = K.real_rows_from_record(D["real_end_rows"], L0["terminals"], FLAT)
gate("P0c real end rows rebuilt from the 5-column record: 0 unmatched, every row kept", not AL["unmatched"] and len(REAL_ROWS) == len(D["real_end_rows"]), AL)
S1 = K.s1_frame_graph(RS.LAB)


def pb(L=None, real=None):
    L, real = L or L0, real or REAL_ROWS
    Lb = SX.bind_state(L, {"obj": FLAT, "term": {}, "diag": {}})[0]
    return K.pb_386(RS.BASE["terminals"], L, real, Lb.get("objs") or [], FLAT, RS.P, RS.PRED["cdiff_rows"], RS.P["open_rows"], RS.LAB,
                    RS.FSPAIRS, RS.REN, S1, V)


def ti(L=None, real=None):
    return K.term_identity_pairs(RS.BASE["terminals"], (L or L0)["terminals"], real or REAL_ROWS, bind={"term": {}, "obj": FLAT})


Gp = K.pred_end_graph(L0, RS.LAB, RS.FSPAIRS)
fs, fr = K.frame_tag_map(Gp), None
sim_src = "1766|ParameterTerminal|32bit integer|0@-49/f1"
r0 = pb()
fr = K.frame_tag_map(r0["G1"])
a, b = K.frame_src_resolve(sim_src, fs), K.frame_src_resolve("1766|ParameterTerminal|32bit integer|0@31557/f0", fr)
gate("P1 sim '@-49/f1' -> frame -29 (bound 31506); real '@31557/f0' -> 31506", a[1] == frozenset([(-49, -29)]) and b[1] == frozenset([(31557, 31506)])
     and FLAT.get(-29) == 31506 and FLAT.get(-49) == 31557, (a, b))
WANT_REC = ["376|Terminal|cal cluster path|0", "376|Terminal|file size|0"]
gate("A1 PB(386) on the recorded data: ok, real == sim-bound, RECORDED == the two #376 tag rows, nothing blocked",
     r0["ok"] and not r0["eq_diff"] and sorted(x["sink"] for x in r0["recorded"]) == WANT_REC and not r0["blocked"],
     {k: r0[k] for k in ("ok", "eq_diff", "recorded", "blocked", "pairs_extra_left", "move_frames")})
t0 = ti()
STUB = [(25223, 1, "InnerTerminal", True)]
gate("A2 D/TD(386): d_ok, td_ok; stub recorded sim-only = wire 24091's end (25223,1,InnerTerminal); TD unwired recorded == that end",
     t0["d_ok"] and t0["td_ok"] and [s["sources"] for s in t0["stubs"]["sim_only"]] == [STUB] and not t0["stubs"]["real_only"]
     and t0["unwired_recorded"] == STUB and not t0["unwired"] and [s["wire"] for s in t0["stubs"]["sim_only"]] == [24091],
     {k: t0[k] for k in ("d_ok", "td_ok", "pairs", "stubs", "unwired", "unwired_recorded")})
old_ti = K.term_identity_gates(RS.BASE["terminals"], L0["terminals"], REAL_ROWS, renames=RS.REN, bind={"term": {}, "obj": FLAT})
gate("A3 control: the OLD gates still fail on the same data (pb_check extra 2; D new 21 vs 22; TD unwired 1)",
     not r0["old"]["ok"] and r0["old"]["extra_sinks"] == WANT_REC and not old_ti["d_ok"] and not old_ti["td_ok"]
     and old_ti["d_new"] == 21 and len(old_ti["sim_new"]) == 22, (r0["old"]["extra_sinks"], old_ti["d_new"], len(old_ti["sim_new"]), old_ti["unwired"]))


def rw(rows, term, wire):
    """A copy of `rows` with term uid `term`'s wire set to `wire`."""
    out = copy.deepcopy(rows)
    for r in out:
        if int(r["term_uid"]) == term:
            r["wire_uid"] = wire
    return out


def wire_of(rows, term):
    return next(int(r["wire_uid"] or 0) for r in rows if int(r["term_uid"]) == term)


def face(rows, owner, cls):
    return [int(r["term_uid"]) for r in rows if int(r["owner_uid"]) == owner and r.get("term_class") == cls]


def swap_frames(rows, owner, f0, f1):
    out = copy.deepcopy(rows)
    for r in out:
        if int(r["owner_uid"]) == owner and r.get("term_class") == "InnerTerminal":
            r["frame_diagram"] = f1 if int(r["frame_diagram"] or 0) == f0 else (f0 if int(r["frame_diagram"] or 0) == f1 else r["frame_diagram"])
    return out


def with_terms(L, rows):
    S = copy.deepcopy(L)
    S["terminals"] = rows
    return S


W3060 = wire_of(REAL_ROWS, 3060)
r = pb(real=rw(REAL_ROWS, 5760, W3060))
gate("B1 re-sourced #376 'cal cluster path' (t5760 on t3060's wire {0}) -> PB BLOCK".format(W3060), not r["ok"],
     {k: r[k] for k in ("eq_diff", "blocked")})
r = pb(real=swap_frames(REAL_ROWS, 31546, 31506, 31517))
r2 = pb(L=with_terms(L0, swap_frames(L0["terminals"], -44, -29, -30)), real=swap_frames(REAL_ROWS, 31546, 31506, 31517))
gate("B2 tag on a non-plan frame (31546's inner faces 31506<->31517): real only BLOCK; both sides: equal, BLOCK by the frame rule",
     not r["ok"] and not r2["ok"] and not r2["eq_diff"] and any("frame" in x["why"] for x in r2["blocked"]),
     {"real_only": r["eq_diff"][:2], "both": r2["blocked"]})
o_r, o_s = face(REAL_ROWS, 31546, "OuterTerminal"), face(L0["terminals"], -44, "OuterTerminal")
r = pb(real=rw(REAL_ROWS, o_r[0], wire_of(REAL_ROWS, 24367)))
r2 = pb(L=with_terms(L0, rw(L0["terminals"], o_s[0], wire_of(L0["terminals"], 24367))), real=rw(REAL_ROWS, o_r[0], wire_of(REAL_ROWS, 24367)))
gate("B3 TF1 outer (t{0}/t{1}) fed from t24367's wire: real only BLOCK; both sides: equal, BLOCK by the S1-source-uid rule".format(o_r, o_s),
     len(o_r) == 1 and len(o_s) == 1 and not r["ok"] and not r2["ok"] and not r2["eq_diff"] and any("source" in x["why"] for x in r2["blocked"]),
     {"real_only": r["eq_diff"][:2], "both": r2["blocked"]})
base_nodes = set(int(x["owner_uid"]) for x in RS.BASE["terminals"])
free = sorted(int(x["term_uid"]) for x in REAL_ROWS if not x["is_source"] and not int(x["wire_uid"] or 0) and int(x["owner_uid"]) in base_nodes
              and x.get("term_class") == "ParameterTerminal")
t = ti(real=rw(REAL_ROWS, free[0], W3060))
gate("B4 a new pair on real only (unwired base sink t{0} wired to t3060's wire) -> D BLOCK".format(free[0]), not t["d_ok"], t["pairs"])
whole = copy.deepcopy(REAL_ROWS)
for x in whole:
    if int(x["wire_uid"] or 0) == W3060:
        x["wire_uid"] = 0
sinks_only = copy.deepcopy(REAL_ROWS)
for x in sinks_only:
    if int(x["wire_uid"] or 0) == W3060 and not x["is_source"]:
        x["wire_uid"] = 0
t, t2 = ti(real=whole), ti(real=sinks_only)
gate("B5 a sink-bearing wire (t3060's {0}) dropped on real only -> D BLOCK; its sinks only (a stub left) -> D BLOCK".format(W3060),
     not t["d_ok"] and not t2["d_ok"], (t["pairs"], t2["pairs"], t2["stubs"]["real_only"]))
# ---- B6 CEN2 --------------------------------------------------------------------------------------------------------------------------
meas, ln_no, seg0 = K.scratch_census(RLOG, os.path.join(K.BENCH, "diag_c156_p5s02a_scratch_sum.json"))
pr = K.jload(PRED)


class Stub(object):
    """The two attributes Stage.census_gate uses (gate, R) - no LabVIEW."""
    def __init__(self):
        self.R, self.res = {}, []

    def gate(self, label, ok, detail="", fatal=False, kind=None):
        self.res.append(bool(ok))
        return ok


def snaps(census):
    after, u = {}, 1
    for c, n in sorted(census.items()):
        for _ in range(int(n)):
            after[u] = c
            u += 1
    return {}, after


st = Stub()
b0, a0 = snaps(pr["census"])
K.Stage.census_gate(st, "CEN2 test", b0, a0, pr["census"])
plus = dict(pr["census"])
plus["Wire"] = plus.get("Wire", 0) + 1
b1, a1 = snaps(plus)
K.Stage.census_gate(st, "CEN2 test +1", b1, a1, pr["census"])
gate("B6 CEN2: pred census_overall MEASURED-SCRATCH == log line {0} (segment from {1}); equal census PASS; Wire +1 FAIL".format(ln_no, seg0),
     pr.get("census_overall") == "MEASURED-SCRATCH" and pr["census"] == meas and st.res == [True, False], (pr.get("census_overall"), st.res, meas))
# ---- C printing helpers of the scratch recipe (no LabVIEW) ----------------------------------------------------------------------------
tf1 = [x for x in REAL_ROWS if int(x["owner_uid"]) == 31546]
oc = K.op_class_census([x for x in REAL_ROWS if int(x["owner_uid"]) != 31546], REAL_ROWS)
gate("C1 op_class_census: tunnel 31546's rows removed then present = 1 owner of its class, its {0} terms, 0 lost".format(len(tf1)),
     oc["owners"] == {tf1[0]["owner_class"]: 1} and sum(oc["terms"].values()) == len(tf1) and oc["lost_terms"] == 0, oc)


class FakeX(object):
    report = [None] * 15


class FakeRS(object):
    x = FakeX()


cls = K.sink_gate_backend_class()
H = K.op_class_census_install(FakeRS(), (16,))
keep = cls._opc_base
cls._opc_base = lambda self: [x for x in REAL_ROWS if int(x["owner_uid"]) != 31546]
FakeRS.x.report = [None] * 14                      # the read after op 15: the report holds ops 1..14 -> k 15
cls.read(None)
FakeRS.x.report = [None] * 15
cls._opc_base = lambda self: REAL_ROWS
cls.read(None)
cls._opc_base = keep
pr16 = K.op_class_census_print(H)
gate("C2 op_class_census_install keeps the reads after ops 15 and 16 (k = len(report) + 1) and prints op 16", pr16.get(16) == oc, pr16)
ra = K.retry_card_arg(["x.py", "--retry-card", "tools/bench/cards/task_158-a3-1.json"], os.path.join(K.ROOT, "tools", "recipes", "stage_d1_ring_p5s02a_scratch.py"))
rb = K.retry_card_arg(["x.py"], "stage_d1_ring_p5s02a_scratch.py")
gate("C3 retry_card_arg reads a recipe-argv card (id 158-a3-1, retry_of None -> matches False); none in argv -> path None",
     ra.get("id") == "158-a3-1" and ra.get("matches") is False and rb.get("path") is None, (ra, rb))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
