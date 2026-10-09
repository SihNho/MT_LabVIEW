# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a1-1.md
# ---
r"""prep_c156_a1_1_mk - card 156-a1-1 (OFFLINE, json only, no LabVIEW, no COM): the P5-2 PLAN RE-MADE per docs/d1/ring-p5.md PD379(a)-(e) on the
REAL P5-1 graph graph_ring_p5s01_20261009_125622.json 6716c499 (adopted VI D1_ring_p5s01_20261009_124542.vi 7f2582ae, never opened).
Base = prep_c155_a4_1_mk.py (166f6003): MAP, groups A..I, the greedy census loop, pass A / REALSIM / X10 / X8 / X17 are that maker's; gate(),
step_facts, the TIE loop, main_of and the SG census are CALLED from prep_c156_a1_1_lib.py (one copy, self-tested 3/0), not pasted again. The MAP /
census / cut code below is still a copy of 155's (OPEN in the facts: no shared module holds it; stagekit is pinned).
CHANGES (PD379), stated before the run:
  (a) J: no '>= 0' and no And. Equal?(counter after this iteration = TD7.outer, the 'records final' local) -> loop 1.7's cond directly. The stop
      mode is READ: the graph's cond terminal t23456 is fed by #23042 'x = y?' whose x and y are both fed by #23501 (always True); the graph carries
      no stop-mode field, so the mode is quoted from the measurement of #23041 (Stop if True, diag_c138_5_facts.md:37-38) - a True cond stops.
  (b) K3 / K4 (#376 t3 'file progress' / t4 'file number to append out'): NEW SR (init = the I32 0 donor P5-1 used; the terminal TYPE is not in the
      graph: OPEN); out-tunnel group (body = not-timed-out frame f0): #376 tk -> O.inner, O.outer -> SR R.inner; in-tunnel group (body = timed-out
      frame f1): SR L.inner -> I.outer, I.inner -> O.inner = THE PASS WIRE as the in-tunnel's one group out-wire (no `frame` end). Feed (K3f / K4f):
      O.outer -> out-tunnel #5204 / #10404 inner face (form T: their outers keep feeding #6384 / #2048). Census decides OK / GAP; no tool edit.
  (c) cut: never inside a group; <= 40 actions; MAIN <= 675 (LIMIT 675; stage_prerun's own X10_FAIL_MB stays 680, memory_model.json pinned).
  (d) sr_q R.outer t31246 stays unwired (gated: no action names it).
PREDICTION CONTRACT: M0 pins; P no pre-existing output; MAP every symbol -> a real uid; STOP the scaffold read; CEN every group OK/GAP/BLOCKED with
  its refusal; NT3/NT4 the t3/t4 sink nets in the census sim (when K compiles); CUT a first step at a group boundary, <= 40 actions, MAIN <= 675;
  SA pass A failed None, 0 PROVISIONAL; TIE; SB REALSIM FINAL, route check PASS, states == pass A; X10 == MAIN(n*) <= 675; X8; X17; Q31246; U.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/prep_c156_a1_1_mk.log -- py -u tools/bench/prep_c156_a1_1_mk.py"""
import collections, json, os, re, sys                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH = os.path.join(B, "graph_ring_p5s01_20261009_125622.json")
P51_IN, P51B = os.path.join(B, "plan_ring_p5s01_in.json"), os.path.join(B, "plan_ring_p5s01b.json")
SESS51B = os.path.join(B, "prep_c155_a2_1_session.json")
DQJ = os.path.join(B, "donor_queue_v0.json")
MMF = os.path.join(B, "memory_model.json")
ROOTS = dict((k, os.path.join(SIM, "ring_p5s02a", k)) for k in ("_census", "_passA"))
RIN, ALLF = os.path.join(B, "plan_ring_p5s02r_in.json"), os.path.join(B, "plan_ring_p5s02r_all.json")
AIN, IN, OUT = os.path.join(ROOTS["_passA"], "plan_ring_p5s02ap_in.json"), os.path.join(B, "plan_ring_p5s02a_in.json"), os.path.join(B, "plan_ring_p5s02a.json")
FACTS = os.path.join(B, "prep_c156_a1_1_session.json")
VI_MD5 = "7f2582ae54dc5bc42c3df0bdf3c72d2e"
WANT = {GRAPH: "6716c499", P51_IN: "fabc4b9c", P51B: "75a77a00", SESS51B: "79447fab", DQJ: "15269b6c", MMF: "c87d170a",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "742e54c4", os.path.join(ROOT, "tools", "stagesim.py"): "eb99c6ba",
        os.path.join(ROOT, "tools", "stagexec.py"): "53e17623", os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f",
        os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7", os.path.join(ROOT, "tools", "stagekit.py"): "aec03c6c",
        os.path.join(CD, "DonorQueue_v0.vi"): "81dba822", os.path.join(B, "diag_c138_5_facts.md"): ""}
MAIN_SRC_READS = 2
MAXACT, LIMIT = 40, 675.0
gate = L.Gate()
ARTS = gate.ARTS
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
pre = [rel(p) for p in (ALLF, IN, OUT, FACTS) if os.path.exists(p)]
gate("P no pre-existing P5-2r_all / P5-2a plan / session file (plan_ring_p5s02r_in.json is this maker's own as-written plan, rewritten each run)", not pre, pre)
# ---- the graph and the map (prep_c155_a4_1_mk.py:76-191, copied: OPEN)
GR = J(GRAPH)
T, OWN = GR["terminals"], GR.get("owners") or {}
OBJ = dict((int(o["uid"]), o) for o in GR.get("objs") or [])
BYW = collections.defaultdict(list)
for r_ in T:
    if r_.get("wire_uid"):
        BYW[int(r_["wire_uid"])].append(r_)


def uniq(rows):
    return list(dict((int(r["term_uid"]), r) for r in rows).values())


def row(u, name=None, src=None, tu=None):
    rr = uniq([r for r in T if (int(r["owner_uid"]) == u or (tu is not None and int(r["term_uid"]) == tu))
               and (name is None or r["term_name"] == name) and (src is None or bool(r["is_source"]) == src)
               and (tu is None or int(r["term_uid"]) == tu)])
    gate("ROW #{0} {1!r} src={2} tu={3} unique in the graph".format(u, name, src, tu), len(rr) == 1, [(r["term_uid"], r["term_name"]) for r in rr])
    return rr[0]


def peers(r):
    return [x for x in uniq(BYW.get(int(r.get("wire_uid") or 0), [])) if int(x["term_uid"]) != int(r["term_uid"])]


def end(u, name, src=None):
    r = row(u, name, src)
    return {"uid": u, "term": name, "term_uid": int(r["term_uid"])}


SESS1 = J(SESS51B)
MAP = {}


def mapped(sym, u, ok, why):
    MAP[sym] = u
    print("FACT MAP {0} -> #{1}: {2}".format(sym, u, why), flush=True)
    gate("MAP {0} -> #{1}".format(sym, u), ok, why)
    return u


QO1 = mapped("QO1 (Obtain, P5-1)", int(SESS1["symbol_map"]["new:QO1"]), OBJ.get(int(SESS1["symbol_map"]["new:QO1"]), {}).get("class") == "Function",
             "prep_c155_a2_1_session.json symbol_map new:QO1; rows {0}".format([r["term_name"] for r in T if int(r["owner_uid"]) == int(SESS1["symbol_map"]["new:QO1"])]))
DQ = J(DQJ)
ROLE = dict((o["role"], o) for o in DQ["objects"])
gate("QO1 terminal names == DonorQueue_v0 Obtain's", sorted(r["term_name"] for r in T if int(r["owner_uid"]) == QO1) == sorted(t["name"] for t in ROLE["obtain"]["terminals"]))
L17 = mapped("L17 loop 1.7", 23041, OBJ.get(23041, {}).get("class") == "WhileLoop", "PD374(a) `#23041`; owners {0}".format(OWN.get("23041")))
F8 = mapped("F8 frame 686", int(OWN["23041"][1]), int(OWN["23041"][1]) == 686 and int(row(QO1, "queue out", True)["frame_diagram"]) == 686,
            "owner diagram of #23041 == Obtain's diagram (PD376(a) 686)")
B17 = mapped("B17 body", 23405, OWN.get("23405") == ["WhileLoop", L17], "PD374(a) body #23405; owners {0}".format(OWN.get("23405")))
S376 = mapped("SAVE #376", 376, OBJ.get(376, {}).get("class") == "SubVI" and all(int(r["frame_diagram"]) == B17 for r in T if int(r["owner_uid"]) == 376),
              "PD374(d) `#376` SubVI on #23405")
r_ref = row(S376, "saved file refnum", False)
REF = mapped("REF #3052", 3052, [int(x["owner_uid"]) for x in peers(r_ref)] == [3052] and OBJ.get(3052, {}).get("class") == "ControlReferenceConstant",
             "PD374(d) `#3052`, the source of #376 'saved file refnum'")
r_prog = row(S376, "file progress", True)
pp = peers(r_prog)
PROG = mapped("PROG #3453", 3453, any(int(x["term_uid"]) == 3453 for x in pp) and OBJ.get(3453, {}).get("class") == "ControlTerminal",
              "PD374(d) `#3453` 'file progress', a sink of #376 'file progress'")
OT3 = mapped("OT3 out-tunnel t3", 5204, sorted(int(x["owner_uid"]) for x in pp if int(x["term_uid"]) != 3453) == [5204], "PD374(d) t3 -> `#5204`")
OT4 = mapped("OT4 out-tunnel t4", 10404, [int(x["owner_uid"]) for x in peers(row(S376, "file number to append out", True))] == [10404], "PD374(d) t4 -> `#10404`")
OTI = dict((u, next(r for r in uniq([r for r in T if int(r["owner_uid"]) == u]) if r["term_class"] == "InnerTerminal")) for u in (OT3, OT4))
OTO = dict((u, next(r for r in uniq([r for r in T if int(r["owner_uid"]) == u]) if r["term_class"] == "OuterTerminal")) for u in (OT3, OT4))
for u in (OT3, OT4):
    print("FACT T34 out-tunnel #{0} inner t{1} outer t{2} -> P5-1 sinks {3}".format(u, OTI[u]["term_uid"], OTO[u]["term_uid"],
          [(x["owner_uid"], x["term_name"], x["term_uid"]) for x in peers(OTO[u])]), flush=True)
RSR, LSR, TIN = {}, {}, {}
for nm, u in (("error out", 24083), ("total data array out", 24150)):
    pr = peers(row(S376, nm, True))
    RSR[nm] = mapped("RSR {0}".format(nm), u, [(int(x["owner_uid"]), x["owner_class"]) for x in pr] == [(u, "RightShiftRegister")], "PD374(d) RSR `#{0}`".format(u))
for nm in ("error in", "total data array in"):
    pr = peers(row(S376, nm, False))
    LSR[nm] = mapped("LSR {0} (read from the graph)".format(nm), int(pr[0]["owner_uid"]) if len(pr) == 1 else None,
                     len(pr) == 1 and pr[0]["owner_class"] == "LeftShiftRegister" and pr[0]["term_class"] == "InnerTerminal",
                     "the source of #376 {0!r}: {1}".format(nm, [(x["owner_uid"], x["owner_class"], x["term_uid"]) for x in pr]))
for nm, u in (("cal cluster path", 24357), ("file size", 24361), ("selected path", 25223)):
    pr = peers(row(S376, nm, False))
    TIN[nm] = mapped("TIN {0}".format(nm), u, [(int(x["owner_uid"]), x["owner_class"], x["term_class"]) for x in pr] == [(u, "LoopTunnel", "InnerTerminal")],
                     "PD374(d) in-tunnel `#{0}` -> #376 {1!r}".format(u, nm))
cond = uniq([r for r in T if int(r["owner_uid"]) == B17 and int(r["frame_diagram"]) == B17 and not r["is_source"] and not r["term_name"] and r.get("wire_uid")])
scaf_src = [x for x in peers(cond[0]) if int(x["owner_uid"]) != B17] if len(cond) == 1 else []
SCAF = mapped("SCAF #23042 (scaffold stop)", 23042, len(cond) == 1 and [(int(x["owner_uid"]), x["term_name"]) for x in scaf_src] == [(23042, "x = y?")],
              "`#23042` 'x = y?' drives the 1.7 cond terminal t{0} by w{1}".format(cond and cond[0]["term_uid"], cond and cond[0]["wire_uid"]))
W_COND = int(cond[0]["wire_uid"])
SCIN = mapped("SCIN #23501 (scaffold in-tunnel)", 23501, sorted(set(int(x["owner_uid"]) for x in peers(row(SCAF, "x", False)))) == [23042, 23501] and
              OBJ.get(23501, {}).get("class") == "LoopTunnel", "in-tunnel `#23501` feeds #23042 x and y")
gate("NOT #8486: #23501's outer is fed by #8486, which stays", 8486 in [int(x["owner_uid"]) for x in peers(next(r for r in T if int(r["owner_uid"]) == SCIN and r["term_class"] == "OuterTerminal"))])
# ---- (a) the stop mode READ (PD379(a))
xy = [(n_, [(int(x["owner_uid"]), x["term_uid"]) for x in peers(row(SCAF, n_, False))]) for n_ in ("x", "y")]
SM = [ln for ln in open(os.path.join(B, "diag_c138_5_facts.md"), encoding="utf-8").read().splitlines()[36:38]]
print("FACT STOP graph 6716c499: cond terminal t{0} (#23405, unnamed sink) <- w{1} <- #23042 'x = y?' t{2}; #23042 inputs {3}; the graph has no "
      "stop-mode field (keys {4}); measured mode of #23041: diag_c138_5_facts.md:37-38 {5!r}".format(
          cond[0]["term_uid"], W_COND, scaf_src[0]["term_uid"], xy, sorted(GR.keys()), SM), flush=True)
gate("STOP the scaffold is x = y? of ONE source (#23501) = True every iteration, and #23041 reads Stop if True (diag_c138_5_facts.md:37-38): a True "
     "cond stops 1.7, so Equal?(counter, records final) -> cond is the polarity-correct form (no Not)",
     all(set(u for u, _t in v if u != SCAF) == {SCIN} for _n, v in xy) and "Stop if True" in " ".join(SM) and "23041" in " ".join(SM), xy)
P51 = J(P51_IN)
K0D = next(a for a in P51["actions"] if a["id"] == "c_k0")["donor"]
INCD = next(a for a in P51["actions"] if a["id"] == "c_inc")
LAB = SPR.prim_donor_labels()
WEQ = 10019                                                                                   # the $work Equal? donor (plan_ring_p3a.json:7), as 155
gate("WD $work donor #{0} label {1!r} == 'Equal?', present in the P5-1 graph".format(WEQ, LAB.get(WEQ)), LAB.get(WEQ) == "Equal?" and WEQ in OBJ)


def wterms(u):
    return [{"name": r["term_name"], "is_source": bool(r["is_source"]), "term_class": r["term_class"]} for r in uniq([r for r in T if int(r["owner_uid"]) == u])]


def dterms(role):
    return [{"name": t["name"], "is_source": t["is_source"], "term_class": "ParameterTerminal"} for t in ROLE[role]["terminals"]]


EQ_T = wterms(WEQ)
EQ_OUT, EQ_IN = [t["name"] for t in EQ_T if t["is_source"]], sorted(t["name"] for t in EQ_T if not t["is_source"])
gate("WT Equal? in {0} out {1}".format(EQ_IN, EQ_OUT), len(EQ_OUT) == 1 and len(EQ_IN) == 2)
DQF = os.path.join(CD, "DonorQueue_v0.vi")
W = lambda i, s, d, w: {"op": "wire", "id": i, "src": s, "dst": d, "why": w}                   # noqa: E731
TUN = lambda i, d, a, w, f=0: {"op": "tunnel", "id": i, "loop": "new:CQ7", "body": "new:CQ7.f{0}".format(f), "parent": B17, "dir": d, "as": a, "why": w}  # noqa: E731
FR = lambda a, f: {"uid": "new:" + a, "side": "inner", "frame": f}            # noqa: E731
pos = lambda u: [int(OBJ[u]["pos"][0]), int(OBJ[u]["pos"][1])]                 # noqa: E731
PDA, PDB, PDC, PDD, PD6, P9 = "PD376(d)", "PD374(b)", "PD374(c)+PD379(a)", "PD374(d)", "PD374(a)", "PD379(b)"
GROUPS = collections.OrderedDict()
GROUPS["A"] = {"deps": [], "link": "refnum SR on 1.7 (2nd branch of Obtain 'queue out') -> Dequeue; R.outer -> Release on 686", "acts": [
    {"op": "add_shift_reg", "id": "sr_q7", "loop": L17, "body": B17, "parent": F8, "as": "QS7", "why": PDA + " refnum SR on 1.7"},
    W("w_obt_q7", end(QO1, "queue out", True), "new:QS7L.outer", PDA + " 2nd branch of Obtain #{0} 'queue out'".format(QO1)),
    {"op": "create", "id": "c_deq", "class": "Function", "diagram": B17, "as": "DQ1", "prim": "Dequeue Element", "donor": {"donor": DQF, "uid": ROLE["dequeue"]["uid"]},
     "terminals": dterms("dequeue"), "data_stream": True, "why": PDA + "; DATA stream 1.2 -> 1.7 results FIFO (PD374(a), CLAUDE.md 1c'': queues for lossless data only)"},
    W("w_q7_deq", "new:QS7L.inner", "new:DQ1.queue", PDA + " Dequeue on L.inner"),
    W("w_deq_q7", "new:DQ1.queue out", "new:QS7R.inner", PDA + " refnum back to R.inner"),
    {"op": "create", "id": "c_rel", "class": "Function", "diagram": F8, "as": "RQ1", "prim": "Release Queue", "donor": {"donor": DQF, "uid": ROLE["release"]["uid"]},
     "terminals": dterms("release"), "data_stream": True, "why": PDA + " Release on 686 after 1.7; DATA stream 1.2 -> 1.7 results FIFO (CLAUDE.md 1c'')"},
    W("w_q7_rel", "new:QS7R.outer", "new:RQ1.queue", PDA + " + PD379(d) R.outer of 1.7's refnum SR -> Release (row-18 route)")]}
GROUPS["B"] = {"deps": ["A"], "link": "I32 100 constant on Dequeue 'timeout in ms (-1)'", "acts": [
    {"op": "create", "id": "c_tmo", "class": "DigitalNumericConstant", "diagram": B17, "as": "TM1", "on": "new:DQ1.timeout in ms (-1)", "value": 100,
     "why": PD6 + " Dequeue with timeout 100 ms (const_on_term)"}]}
GROUPS["C"] = {"deps": ["A"], "link": "Case on Dequeue 'timed out?' (case_wired, frames False/True)", "acts": [
    {"op": "create", "id": "c_case7", "class": "CaseStructure", "diagram": B17, "as": "CQ7", "selector_as": "SL7", "frames": ["False", "True"],
     "src": "new:DQ1.timed out?", "why": PDD + " NEW Case on Dequeue 'timed out?'; False = an element was dequeued"}]}
GROUPS["D"] = {"deps": ["C"], "link": "move #376 / #3052 / #3453 into the not-timed-out frame; #3052 -> #376, #376 -> #3453 re-wired there", "acts": [
    {"op": "move_in", "id": "mv_376", "nodes": [S376], "dest_diagram": "new:CQ7.f0", "pos": pos(S376), "why": PDD + " `#376` MOVED in (not changed)"},
    {"op": "move_in", "id": "mv_3052", "nodes": [REF], "dest_diagram": "new:CQ7.f0", "pos": pos(REF), "why": PDD + " `#3052` refnum constant"},
    {"op": "move_in", "id": "mv_3453", "nodes": [PROG], "dest_diagram": "new:CQ7.f0", "pos": pos(PROG), "why": PDD + " `#3453` 'file progress'"},
    W("w_ref", {"uid": REF, "term": "File # Saved", "term_uid": int(row(REF, "File # Saved", True)["term_uid"])}, end(S376, "saved file refnum", False),
      PDD + " the wire #3052 -> #376 as in the P5-1 graph (w{0})".format(r_ref["wire_uid"])),
    W("w_prog", end(S376, "file progress", True), {"uid": PROG, "term_uid": PROG}, PDD + " the wire #376 -> #3453 as in the P5-1 graph (w{0})".format(r_prog["wire_uid"]))]}
GROUPS["E"] = {"deps": ["D"], "link": "Dequeue 'element' -> case tunnel in -> #376 t5", "acts": [
    TUN("t_el7", "in", "TE7", PDD + " t5 <- the dequeued element"),
    W("w_el7_in", "new:DQ1.element", "new:TE7.outer", PDD), W("w_el7_376", "new:TE7.inner", end(S376, "current frame data array in", False), PDD)]}
for k, (nm, u) in enumerate(sorted(TIN.items(), key=lambda x: x[1]), 1):
    ti = row(u, None, True)
    GROUPS["F{0}".format(k)] = {"deps": ["D"], "link": "in-tunnel #{0} inner -> case tunnel in -> #376 {1!r}".format(u, nm), "acts": [
        TUN("t_in{0}".format(k), "in", "TF{0}".format(k), PDD + " in-tunnel #{0} keeps its source".format(u)),
        W("w_in{0}_t".format(k), {"uid": u, "term": ti["term_name"], "term_uid": int(ti["term_uid"])}, "new:TF{0}.outer".format(k), PDD),
        W("w_in{0}_376".format(k), "new:TF{0}.inner".format(k), end(S376, nm, False), PDD)]}
for gk, (ni, no, a1, a2) in (("G", ("error in", "error out", "TG1", "TG2")), ("H", ("total data array in", "total data array out", "TH1", "TH2"))):
    li = row(LSR[ni], None, True)
    ri = next(r for r in uniq([r for r in T if int(r["owner_uid"]) == RSR[no] and r["term_class"] == "InnerTerminal"]))
    GROUPS[gk] = {"deps": ["D"], "link": "#376 {0!r}/{1!r}: LSR #{2} inner -> case tunnel in; case tunnel out -> RSR #{3} inner; timed-out frame pass-through".format(
        ni, no, LSR[ni], RSR[no]), "acts": [
        TUN("t_{0}i".format(gk.lower()), "in", a1, PDD + " existing SR of #376 (LSR #{0})".format(LSR[ni])),
        W("w_{0}l".format(gk.lower()), {"uid": LSR[ni], "term": li["term_name"], "term_uid": int(li["term_uid"])}, "new:{0}.outer".format(a1), PDD),
        W("w_{0}376".format(gk.lower()), "new:{0}.inner".format(a1), end(S376, ni, False), PDD),
        TUN("t_{0}o".format(gk.lower()), "out", a2, PDD + " existing SR of #376 (RSR #{0})".format(RSR[no])),
        W("w_{0}out".format(gk.lower()), end(S376, no, True), "new:{0}.inner".format(a2), PDD),
        W("w_{0}r".format(gk.lower()), "new:{0}.outer".format(a2), {"uid": RSR[no], "term": ri["term_name"], "term_uid": int(ri["term_uid"])}, PDD),
        W("w_{0}pass".format(gk.lower()), FR(a1, "True"), FR(a2, "True"), PDD + " value passes through the timed-out frame")]}
GROUPS["I"] = {"deps": ["D"], "link": "1.7 record counter SR (I32 0) -> case tunnel -> Increment (+ #376 t7 on the LEFT value) -> case tunnel out -> R.inner; pass-through", "acts": [
    {"op": "add_shift_reg", "id": "sr_c7", "loop": L17, "body": B17, "parent": F8, "as": "CS7", "why": PDB + " 1.7 record counter SR"},
    {"op": "create", "id": "c_k07", "class": "DigitalNumericConstant", "diagram": F8, "as": "K07", "prim": "const_donor", "donor": K0D,
     "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}], "why": PDB + " init 0 (donor as P5-1 c_k0)"},
    W("w_k07", "new:K07.value", "new:CS7L.outer", PDB),
    {"op": "create", "id": "c_inc7", "class": "Function", "diagram": "new:CQ7.f0", "as": "IN7", "prim": INCD["prim"], "donor": INCD["donor"],
     "terminals": INCD["terminals"], "why": PDB + " +1 only where an element was dequeued (donor as P5-1 c_inc)"},
    TUN("t_ci7", "in", "TC7", PDB), W("w_ci7_in", "new:CS7L.inner", "new:TC7.outer", PDB), W("w_ci7_inc", "new:TC7.inner", "new:IN7.x", PDB),
    W("w_c7_fi", FR("TC7", "False"), end(S376, "frame index", False), PDB + " t7 <- the counter's LEFT value (before this call)"),
    TUN("t_co7", "out", "TD7", PDB), W("w_inc7_co", "new:IN7.x+1", "new:TD7.inner", PDB), W("w_co7_r", "new:TD7.outer", "new:CS7R.inner", PDB),
    W("w_c7_pass", FR("TC7", "True"), FR("TD7", "True"), PDB + " no element -> no increment")]}
GROUPS["J"] = {"deps": ["I"], "link": "stop: delete scaffold #23042 / #23501; Equal?(counter after the iteration, local 'records final') -> cond (no >= 0, no And)", "acts": [
    {"op": "delete_wire", "id": "dw_cond", "wire_uid": W_COND, "why": PDD + " scaffold stop wire #23042 -> cond (read from the graph)"},
    {"op": "delete_object", "id": "do_23042", "uid": SCAF, "why": PDD + " scaffold stop `#23042` removed"},
    {"op": "delete_object", "id": "do_23501", "uid": SCIN, "why": PDD + " scaffold in-tunnel `#23501` removed (NOT #8486)"},
    {"op": "create", "id": "c_lr7", "class": "Local", "diagram": B17, "as": "LR7", "label": "records final (1.2 to 1.7)", "mode": "read",
     "terminals": [{"name": "records final (1.2 to 1.7)", "is_source": True, "term_class": "Terminal"}], "why": PDC + " published counter read by a local"},
    {"op": "create", "id": "c_eq7", "class": OBJ[WEQ]["class"], "diagram": B17, "as": "EQ7", "prim": "Equal?", "donor": {"donor": "$work", "uid": WEQ},
     "terminals": wterms(WEQ), "why": PDC + " counter (after this iteration) == records final; feeds cond directly (Stop if True, read)"},
    W("w_eq7_x", "new:TD7.outer", "new:EQ7." + EQ_IN[0], PDC + " the counter AFTER this iteration = the case out-tunnel value"),
    W("w_eq7_y", "new:LR7.value", "new:EQ7." + EQ_IN[1], PDC),
    W("w_eq7_cond", "new:EQ7." + EQ_OUT[0], {"uid": L17, "term": "cond"}, PDC + " 1.7 stops when they are equal")]}
for kk, (nm, ot) in (("K3", ("file progress", OT3)), ("K4", ("file number to append out", OT4))):
    s_ = kk.lower()
    GROUPS[kk] = {"deps": ["D"], "link": "NEW SR for #376 {0!r}: init const -> L.outer; out-tunnel (f0) #376 -> O.inner, O.outer -> R.inner; in-tunnel (f1) L.inner -> "
                  "I.outer, I.inner -> O.inner = the pass wire (the in-tunnel's one group out-wire)".format(nm), "acts": [
        {"op": "add_shift_reg", "id": "sr_" + s_, "loop": L17, "body": B17, "parent": F8, "as": "S" + kk, "why": P9 + " NEW SR for t" + kk[1]},
        {"op": "create", "id": "c_{0}i".format(s_), "class": "DigitalNumericConstant", "diagram": F8, "as": "KI" + kk[1], "prim": "const_donor", "donor": K0D,
         "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}], "why": P9 + " SR init = the type's default (I32 0 donor as P5-1 c_k0; type OPEN)"},
        W("w_{0}i".format(s_), "new:KI{0}.value".format(kk[1]), "new:S{0}L.outer".format(kk), P9),
        TUN("t_{0}o".format(s_), "out", "O" + kk, P9 + " case out-tunnel, #376 side = not-timed-out frame", 0),
        W("w_{0}out".format(s_), end(S376, nm, True), "new:O{0}.inner".format(kk), P9),
        W("w_{0}r".format(s_), "new:O{0}.outer".format(kk), "new:S{0}R.inner".format(kk), P9),
        TUN("t_{0}i".format(s_), "in", "I" + kk, P9 + " case in-tunnel, pass side = timed-out frame", 1),
        W("w_{0}l".format(s_), "new:S{0}L.inner".format(kk), "new:I{0}.outer".format(kk), P9),
        W("w_{0}pass".format(s_), "new:I{0}.inner".format(kk), "new:O{0}.inner".format(kk), P9 + " the pass wire in the timed-out frame = the in-tunnel's one out-wire")]}
    GROUPS[kk + "f"] = {"deps": [kk], "link": "the value at S{0} R.inner (O{0}.outer) -> out-tunnel #{1} inner (form T: #{1} outer keeps feeding the P5-1 sinks)".format(kk, ot), "acts": [
        W("w_{0}f".format(s_), "new:O{0}.outer".format(kk), {"uid": ot, "term_uid": int(OTI[ot]["term_uid"])}, P9 + " #6384/#2048 take the value that reaches R.inner")]}
json.dump({"schema": "stageplan/1", "context": P51.get("context") or {"s1_key": "D1_s1_copy"}, "stage": "ring_p5s02r",
           "goal": "card 156-a1-1 P5-2 INPUT PLAN as written (PD374/PD376/PD379), before the census: groups {0}".format(list(GROUPS))[:400],
           "base": {"path": rel(GRAPH), "md5": md5(GRAPH)}, "actions": [a for g in GROUPS.values() for a in g["acts"]]}, open(RIN, "w", encoding="utf-8"), indent=1)
gate("Q31246 sr_q R.outer t31246 (loop 1.2) is named by no action (PD379(d))", "31246" not in json.dumps(J(RIN)["actions"]))
# ---- greedy census (prep_c155_a4_1_mk.py:292-405, copied: OPEN)
TOP = {"schema": "stageplan/1", "context": P51.get("context") or {"s1_key": "D1_s1_copy"}}
BASEREF = {"path": rel(GRAPH), "md5": md5(GRAPH)}
OWNERS = SX.plan_base_owners({"base": BASEREF})
gate("BO base owner map == graph owners ({0})".format(len(OWNERS)), OWNERS == OWN and bool(OWNERS))
SRC = dict((f, open(os.path.join(ROOT, "tools", f), encoding="utf-8").read().splitlines()) for f in ("stagesim.py", "stagexec.py", "stage_prerun.py"))


def cite(msg):
    for p_ in sorted(set(x.strip(" :;,.-()") for x in re.split(r"#?-?[0-9]+|[{}\[\]'\"]", str(msg))), key=len, reverse=True):
        if len(p_) < 16:
            break
        for f, lines in SRC.items():
            for i, ln in enumerate(lines, 1):
                if p_ in ln:
                    return "tools/{0}:{1}".format(f, i)
    return None


STATUS, ERR = dict((g, "OK") for g in GROUPS), {}


def flat(gs):
    out, own = [], []
    for g in gs:
        for a in GROUPS[g]["acts"]:
            out.append(a)
            own.append(g)
    return out, own


def drop(g, why, kind):
    STATUS[g], ERR[g] = "GAP", {"stage": kind, "error": str(why)[:600], "tool": cite(why)}
    print("FACT CENSUS GAP {0} ({1}): {2} | tool {3}".format(g, kind, str(why)[:500], ERR[g]["tool"]), flush=True)
    changed = True
    while changed:
        changed = False
        for h, gg in GROUPS.items():
            if STATUS[h] == "OK" and any(STATUS[d] != "OK" for d in gg["deps"]):
                STATUS[h], ERR[h] = "BLOCKED", {"stage": "dep", "error": "depends on {0}".format([d for d in gg["deps"] if STATUS[d] != "OK"]), "tool": None}
                changed = True


os.makedirs(ROOTS["_census"], exist_ok=True)
CPATH = os.path.join(ROOTS["_census"], "plan_ring_p5s02c_in.json")
rnd = 0
while True:
    rnd += 1
    live = [g for g in GROUPS if STATUS[g] == "OK"]
    acts, own = flat(live)
    try:
        SX.compile_plan(dict(TOP, actions=acts), owners=OWNERS)
    except SX.ExecStop as e:
        m = re.search(r"action (\d+)", str(e))
        gate("CEN round {0}: compile ExecStop names an action".format(rnd), bool(m), str(e))
        drop(own[int(m.group(1)) - 1], e, "compile")
        continue
    bad17 = SPR.prim_donor_check({"actions": acts}, LAB, base_uids=set(OBJ))
    if bad17:
        ids = dict((a.get("id"), g) for a, g in zip(acts, own))
        drop(ids[bad17[0]["action"]], json.dumps(bad17[0]), "x17")
        continue
    json.dump(dict(TOP, stage="ring_p5s02c", goal="card 156-a1-1 ROUTE CENSUS round {0}: groups {1}".format(rnd, live), base=BASEREF, actions=acts),
              open(CPATH, "w", encoding="utf-8"), indent=1)
    try:
        SC = SS.simulate(CPATH, GRAPH, out_root=ROOTS["_census"], plan_out_dir=ROOTS["_census"], log=lambda *x: None, route_check=False)
    except Exception as e:                                                                    # noqa: BLE001 - a simulator crash is a census fact
        crash = "CRASH {0}: {1}".format(type(e).__name__, e)
        hit = None
        for j in range(1, len(live) + 1):
            a2, _o2 = flat(live[:j])
            json.dump(dict(TOP, stage="ring_p5s02c", goal="census crash bisect", base=BASEREF, actions=a2), open(CPATH, "w", encoding="utf-8"), indent=1)
            try:
                r2 = SS.simulate(CPATH, GRAPH, out_root=ROOTS["_census"], plan_out_dir=ROOTS["_census"], log=lambda *x: None, route_check=False)
                if r2.get("failed"):
                    hit = live[j - 1]
                    break
            except Exception:                                                                # noqa: BLE001
                hit = live[j - 1]
                break
        drop(hit or live[-1], crash, "sim-crash")
        continue
    if SC.get("failed"):
        n = int(SC["failed"]["n"])
        drop(own[n - 1], "action {0} ({1} {2}): {3}".format(n, SC["failed"].get("op"), SC["failed"].get("id"), SC["failed"].get("error")), "sim")
        continue
    break
print("FACT CENSUS rounds {0}; last sim steps {1}; provisional {2}".format(rnd, len(SC["steps"]), [s["n"] for s in SC["steps"] if s.get("provisional")]), flush=True)
CROWS = []
cops = SX.compile_plan(dict(TOP, actions=acts), owners=OWNERS)
opof = {}
for o in cops:
    for n_ in o["acts"]:
        opof[n_] = (o["kind"], o.get("variant") or o.get("route"))
eff = dict((s["n"], s) for s in SC["steps"])
for g, gg in GROUPS.items():
    if STATUS[g] == "OK":
        idx = [i for i, x in enumerate(own, 1) if x == g]
        CROWS.append({"group": g, "link": gg["link"], "status": "OK", "actions": [a["id"] for a in gg["acts"]], "routes": sorted(set("{0}/{1}".format(*opof[i]) for i in idx)),
                      "sim_steps": idx, "model_source": sorted(set(str((eff.get(i) or {}).get("model_source")) for i in idx)),
                      "provisional": [i for i in idx if (eff.get(i) or {}).get("provisional")]})
    else:
        CROWS.append({"group": g, "link": gg["link"], "status": STATUS[g], "actions": [a["id"] for a in gg["acts"]], "error": ERR[g]["error"],
                      "stage": ERR[g]["stage"], "tool": ERR[g]["tool"]})
for c in CROWS:
    print("CENSUS {0} | {1} | {2} | {3}".format(c.get("group"), c.get("status"), c.get("link"), c.get("routes") or (c.get("error"), c.get("tool"))), flush=True)
gate("CEN every group censused OK / GAP / BLOCKED; every GAP carries its refusal ({0} OK, {1} GAP, {2} BLOCKED)".format(
     sum(1 for c in CROWS if c["status"] == "OK"), sum(1 for c in CROWS if c["status"] == "GAP"), sum(1 for c in CROWS if c["status"] == "BLOCKED")),
     all(c["status"] in ("OK", "GAP", "BLOCKED") and (c["status"] != "GAP" or c.get("error")) for c in CROWS))
# ---- (b) the t3/t4 sink nets in the census sim's end state (when K compiles)
SIMEND = J(SC["steps"][-1]["file"]["path"])["state"]
NT = {}
for kk, ot in (("K3", OT3), ("K4", OT4)):
    if STATUS.get(kk) != "OK" or STATUS.get(kk + "f") != "OK":
        NT[kk] = {"status": "not compiled ({0} {1}, {2}f {3})".format(kk, STATUS.get(kk), kk, STATUS.get(kk + "f"))}
        print("FACT NT {0}: {1}".format(kk, NT[kk]["status"]), flush=True)
        continue
    sym = SIMEND.get("sym") or {}
    ST = SIMEND["terminals"]
    ou, iu, su = sym.get("new:O" + kk), sym.get("new:I" + kk), sym.get("new:S" + kk + "R")
    w_of = lambda tu: next((r.get("wire_uid") for r in ST if r["term_uid"] == tu), None)           # noqa: E731
    net = lambda w: sorted(set((int(r["owner_uid"]), r["term_name"], r["term_uid"], r["term_class"], r.get("frame_diagram")) for r in ST if w and r.get("wire_uid") == w))  # noqa: E731
    oo = [r for r in ST if r["owner_uid"] == ou and r["term_class"] == "OuterTerminal"]
    oin = [r for r in ST if r["owner_uid"] == ou and r["term_class"] == "InnerTerminal"]
    iin = [r for r in ST if r["owner_uid"] == iu and r["term_class"] == "InnerTerminal"]
    frames = (SIMEND.get("case_frames") or {})
    n_out = net(oo[0].get("wire_uid")) if oo else []
    n_tun = net(w_of(int(OTO[ot]["term_uid"])))
    NT[kk] = {"O": ou, "I": iu, "S_R": su, "O_outer_net": n_out, "tunnel_outer_net": n_tun,
              "O_inner_faces": [(r["term_uid"], r["frame_diagram"], r.get("wire_uid")) for r in oin], "I_inner_faces": [(r["term_uid"], r["frame_diagram"], r.get("wire_uid")) for r in iin],
              "pass_nets": [net(r.get("wire_uid")) for r in iin if r.get("wire_uid")]}
    print("FACT NT {0}: {1}".format(kk, json.dumps(NT[kk], default=str)), flush=True)
    sinks = [(x["owner_uid"], x["term_uid"]) for x in peers(OTO[ot])]
    ok_ = any(o == ot and c == "InnerTerminal" for o, _n, _t, c, _f in n_out) and all(any((o, t) == (a, b) for o, _n, t, _c, _f in n_tun) for a, b in sinks)
    gate("NT{0} census sim end: O{0}.outer (the value at S{0} R.inner) feeds #{1} inner, and #{1} outer still feeds the P5-1 sinks {2}".format(kk[1], ot, sinks), ok_, NT[kk], fatal=False)
OKG = [g for g in GROUPS if STATUS[g] == "OK"]
ALLACTS, ALLOWN = flat(OKG)
json.dump(dict(TOP, stage="ring_p5s02r_all", goal=("card 156-a1-1 P5-2 ALL-GROUPS PLAN (PD374/PD376/PD379): every censused-OK group {0} on the REAL P5-1 graph 6716c499; "
                                                    "GAP/BLOCKED groups {1} are not rows").format(OKG, [g for g in GROUPS if STATUS[g] != "OK"])[:400],
               base=BASEREF, actions=ALLACTS), open(ALLF, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(ALLF))
gate("S00 the all-groups plan validates ({0} actions)".format(len(ALLACTS)), ok_, why_)
# ---- (c) the cut: group boundaries only
OPS = SX.compile_plan(dict(TOP, actions=ALLACTS), owners=OWNERS)
KINDS = [o["kind"] for o in OPS]
MODEL = SPR.load_memory_model()
XS = SPR.x10_start(VI_MD5, MODEL)
START = XS[0] if XS else None
gate("XS x10_start(7f2582ae) measured: {0}".format(XS), XS is not None)
GEND = set(i for i in range(1, len(ALLACTS) + 1) if i == len(ALLACTS) or ALLOWN[i] != ALLOWN[i - 1])        # last action of each group
TAB = [(n, L.main_of(n, KINDS, SX, SPR, MODEL, START, MAIN_SRC_READS)[0], max(OPS[n - 1]["acts"])) for n in range(1, len(OPS) + 1)]
print("FACT CUT start {0} ({1}); ops {2}; group ends (action) {3}; per-prefix (n, MAIN, last action) {4}".format(START, XS and XS[1], len(OPS), sorted(GEND), TAB), flush=True)
fit = [n for n, m, ka in TAB if m <= LIMIT and ka <= MAXACT and ka in GEND and sorted(x for o in OPS[:n] for x in o["acts"]) == list(range(1, ka + 1))]
NS = max(fit) if fit else 0
gate("CUT first step at a group boundary: n* {0} of {1} ops (MAIN {2} <= {3}, actions {4} <= {5})".format(NS, len(OPS), NS and TAB[NS - 1][1], LIMIT, NS and TAB[NS - 1][2], MAXACT),
     NS >= 1, TAB)
KA = TAB[NS - 1][2]
LATER, k0 = [], NS
while k0 < len(OPS):
    s0 = max(OPS[k0 - 1]["acts"])
    best = None
    for n in range(k0 + 1, len(OPS) + 1):
        ka = max(OPS[n - 1]["acts"])
        if ka - s0 <= MAXACT and ka in GEND and sorted(x for o in OPS[k0:n] for x in o["acts"]) == list(range(s0 + 1, ka + 1)):
            best = n
    if best is None:
        break
    LATER.append({"ops": [k0 + 1, best], "actions": [s0 + 1, max(OPS[best - 1]["acts"])], "groups": sorted(set(ALLOWN[s0:max(OPS[best - 1]["acts"])]), key=list(GROUPS).index),
                  "x10": "start = the measured load of the previous step's adopted file (not known offline); MAIN <= 675 re-checked then"})
    k0 = best
NSTEP = 1 + len(LATER)
NAMES = ["claudeDev\\D1_ring_p5s02{0}_<ts>.vi".format(chr(ord("a") + i)) for i in range(NSTEP - 1)] + ["claudeDev\\D1_ring_p5_<ts>.vi"]
print("FACT LATER cut points (group boundaries, <= 40 actions; X10 of each from its own adopted start): {0}; saved files per step {1}".format(LATER, NAMES), flush=True)
ACTS = ALLACTS[:KA]
print("FACT STEP1 actions 1..{0} ({1} ops): groups {2}".format(KA, NS, sorted(set(ALLOWN[:KA]), key=list(GROUPS).index)), flush=True)
os.makedirs(ROOTS["_passA"], exist_ok=True)
json.dump(dict(TOP, stage="ring_p5s02ap", goal="card 156-a1-1 PASS A: P5-2 step 1 = actions 1..{0} on the real P5-1 graph, no open_rows".format(KA),
               base=BASEREF, actions=ACTS), open(AIN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(AIN))
gate("S0 pass-A input validates ({0} actions)".format(len(ACTS)), ok_, why_)
SA = SS.simulate(AIN, GRAPH, out_root=ROOTS["_passA"], plan_out_dir=ROOTS["_passA"], log=lambda *x: None, route_check=False)
HA = L.step_facts("PASSA", SA)
provA = [s["n"] for s in SA["steps"] if s.get("provisional")]
gate("SA pass A replays every action: failed {0}; steps {1} == actions + 1; PROVISIONAL {2}".format(json.dumps(SA.get("failed"), default=str), len(SA["steps"]), provA),
     SA["failed"] is None and len(SA["steps"]) == len(ACTS) + 1 and not provA and SA.get("end_cdiff_rows") is not None, SA.get("failed"))
ok_pairs = dict(((int(r["node"]), r["term"]), "p5s01-open") for r in J(P51B).get("open_rows") or [])
ties, untied, orows = L.tie_rows(SA, ACTS, ok_pairs, SS.V.key_parts, "c156-a1-1")
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    print("FACT TIE-ROW owner #{0} term {1!r} made by {2} (step {3}, {4}) key {5}".format(t["pair"][0], t["pair"][1], t["id"], t["n"], t["class"], k), flush=True)
gate("TIE every end row ({0}) tied to a P5-2 action or a P5-1 declared open row ({1} open pairs)".format(len(SA["end_cdiff_rows"]), len(orows)), not untied, untied[:10])
GOAL = ("RING P5-2 step 1 of {0} (card 156-a1-1, PD374(b)(d) + PD376(d) + PD379): actions 1..{1} ({2} ops) = groups {3} on the REAL P5-1 graph 6716c499; "
        "never cut inside a group; MAIN <= 675").format(NSTEP, KA, NS, sorted(set(ALLOWN[:KA]), key=list(GROUPS).index))
json.dump(dict(TOP, stage="ring_p5s02a", goal=GOAL[:400], base=BASEREF, open_rows=orows, actions=ACTS), open(IN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(IN))
gate("S1 plan input validates ({0} actions, {1} open pairs)".format(len(ACTS), len(orows)), ok_, why_)
SB = SS.simulate(IN, GRAPH, out_root=SIM, plan_out_dir=B, log=lambda m: print(m, flush=True), route_check=True)
HB = L.step_facts("REALSIM", SB)
p = J(OUT) if os.path.isfile(OUT) else {}
fz = p.get("finalized") or {}
provB = [s["n"] for s in SB["steps"] if s.get("provisional")]
gate("SB REALSIM plan FINAL: failed {0}; route check {1}; PROVISIONAL {2}".format(SB.get("failed"), (fz.get("route_check") or {}).get("status"), provB),
     bool(SB["final"]) and p.get("final") is True and fz.get("open_rows_match") is True and (fz.get("route_check") or {}).get("status") == "PASS"
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and not provB, {"final": SB["final"], "rc": fz.get("route_check")})
gate("SAME pass A and REALSIM step states equal ({0} steps)".format(len(HA)), HA == HB, [n for n in sorted(set(HA) | set(HB)) if HA.get(n) != HB.get(n)])
for r in (fz.get("route_check") or {}).get("rows") or []:
    print("FACT ROUTE k {0} {1} {2}: {3} {4}".format(r.get("k"), r.get("op"), r.get("ids"), r.get("route"), (r.get("how") or "")[:80]), flush=True)
ops = SX.compile_plan(p)
MAIN, mp, cps = L.main_of(len(ops), [o["kind"] for o in ops], SX, SPR, MODEL, START, MAIN_SRC_READS)
print("FACT X10 start {0}; ops {1} kinds {2}; checkpoints {3}; N {4} R {5}; Executor peak {6}; MAIN {7}; card limit {8}; stage_prerun fail_above {9}; MEMSTOP {10}".format(
      START, len(ops), dict(collections.Counter(o["kind"] for o in ops)), cps, mp["N"], mp["R"], mp["peak_mb"], MAIN, LIMIT, SPR.X10_FAIL_MB, SX.MEM_STOP_MB), flush=True)
gate("X10 step-1 plan: ops == ops 1..{0}; MAIN {1} == MAIN(n*) {2} <= {3} (card limit; stage_prerun 680, MEMSTOP {4})".format(NS, MAIN, TAB[NS - 1][1], LIMIT, SX.MEM_STOP_MB),
     [(o["kind"], o["acts"]) for o in ops] == [(o["kind"], o["acts"]) for o in OPS[:NS]] and MAIN == TAB[NS - 1][1] and MAIN <= LIMIT and SX.MEM_STOP_MB == 695, mp)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean", not lint, lint)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17)
SGC = L.sg_census(p, SX)
print("FACT SG-CENSUS {0} ControlTerminal-sink row(s); {1} need a declared sink gate: {2}".format(len(SGC), sum(1 for e in SGC if e["needs_sink_gate"]), SGC), flush=True)
gate("Q31246b step-1 plan names no t31246", "31246" not in json.dumps(p.get("actions")))
json.dump({"card": "156-a1-1", "plan": {"path": rel(OUT), "md5": md5(OUT)}, "all_plan": {"path": rel(ALLF), "md5": md5(ALLF)}, "input_plan": {"path": rel(RIN), "md5": md5(RIN)},
           "symbol_map": MAP, "census": CROWS, "t34_nets": NT, "actions": len(ACTS), "ops": len(ops),
           "cut": {"n_ops": NS, "k_actions": KA, "per_prefix_main": TAB, "limit": LIMIT, "max_actions": MAXACT, "group_ends": sorted(GEND)}, "later_cuts": LATER,
           "saved_files": NAMES, "kinds": dict(collections.Counter(o["kind"] for o in ops)), "start_mb": START, "start_cite": XS and XS[1],
           "exec_peak_mb": mp["peak_mb"], "main_peak_mb": MAIN, "main_src_reads": MAIN_SRC_READS, "checkpoints": cps, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ties": ties, "sink_gate_census": SGC, "passA_states": HA, "realsim_states": HB,
           "steps": [{"n": s["n"], "op": s.get("op"), "id": s.get("id"), "model_source": s.get("model_source"), "file": rel(s["file"]["path"]), "md5": s["file"]["md5"]}
                     for s in SB["steps"]]}, open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RIN, ALLF, AIN, IN, OUT, FACTS))
gate("U inputs untouched", all(md5(q) == M0[q] for q in WANT))
sys.exit(gate.result())
