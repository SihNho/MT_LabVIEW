# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_155-a4-1.md
# ---
r"""prep_c155_a4_1_mk - card 155-a4-1 (OFFLINE, json only, no LabVIEW, no COM): the P5-2 PLAN (docs/d1/ring-p5.md PD374(b)(c)(d), PD376(d),
PD378(c)) on the REAL P5-1 graph graph_ring_p5s01_20261009_125622.json 6716c499 (adopted VI D1_ring_p5s01_20261009_124542.vi 7f2582ae, never opened).
Skeleton = prep_c155_a2_1_mk.py (2c766af9): the cut / pass A / TIE / REALSIM / X10 / X8 / X17 / SG-census / session blocks are COPIED from it
(OPEN in the facts: they live in no shared module and the extraction is outside this card's write globs). NEW in this maker:
  (n1) ROWS from the decisions only, as GROUPS: A refnum SR on 1.7 + Dequeue + Release (PD376(d)); B Dequeue timeout 100 ms (PD374(a)); C Case
       on Dequeue 'timed out?' (PD374(d)); D move #376 / #3052 / #3453 into its not-timed-out frame + their two same-frame wires (PD374(d));
       E t5 <- the dequeued element (PD374(d)); F1-F3 in-tunnels #24357 / #24361 / #25223 keep their sources (PD374(d)); G / H #376's error /
       total-data shift registers pass through the timed-out frame (PD374(d)); I the 1.7 record counter SR, read on its LEFT side into t7
       (PD374(b)); J the stop of PD374(c) with the scaffold #23042 / #23501 removed; K3 / K4 the two NEW SRs for t3 / t4 (PD374(d)).
  (n2) MAP: every PD-named uid is checked in the graph (class, owner, the wire that ties it to #376); the uids PD374 does not name (#376's LEFT
       registers, the cond wire, the out-tunnels) are READ from the graph wires; QO1 (Obtain) from the P5-1b session's symbol_map (79447fab).
       Base terminal ends carry the graph's term_uid; move positions are each node's graph position. Nothing retyped.
  (n3) ROUTE CENSUS (greedy, existing functions only): compile (stagexec.compile_plan, base owners) + X17 (stage_prerun.prim_donor_check) +
       stagesim.simulate of all non-GAP groups; the first refused action marks its group GAP (with the refusing tool line found by the message
       text), the groups that depend on it are BLOCKED, and the rest is re-run. The >= 0 comparison of PD374(c) is censused by donor search
       (main_vi_node_labels.json labels + PRIM_DONORS) BEFORE any row is written: no donor -> GAP row, no plan row (no tool written).
  (n4) the CUT is the longest op prefix with MAIN <= 680 AND <= 40 actions at an action boundary (PD374(e)); later cut points are listed.
Existing tools used (no new op, no tool edit): stagesim.simulate / base_case_frames / V.key_parts, stagexec.compile_plan / plan_base_owners /
create_route / is_ct / BIND_KINDS, stage_prerun x10_start / x10_model_peak / control_path_lint / x17_gate / prim_donor_check / prim_donor_labels /
PRIM_DONORS, protocol.validate_obj.
PREDICTION CONTRACT: M0 pins; P no pre-existing output; MAP every symbol -> a real uid with the checked rows; GE the >= 0 donor search is printed
  (GAP when empty); CEN every group OK, GAP or BLOCKED, every GAP with its error and tool line; CUT a first step of <= 40 actions with MAIN <= 680;
  SA pass A failed None, 0 PROVISIONAL; TIE; SB REALSIM FINAL, route check PASS, states == pass A; X10 == MAIN(n*); X8 clean; X17 clean; U inputs.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/prep_c155_a4_1_mk.log -- py -u tools/bench/prep_c155_a4_1_mk.py"""
import collections, copy, hashlib, json, os, re, sys                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                                   # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
GRAPH = os.path.join(B, "graph_ring_p5s01_20261009_125622.json")
P51_IN, P51B = os.path.join(B, "plan_ring_p5s01_in.json"), os.path.join(B, "plan_ring_p5s01b.json")
SESS51B = os.path.join(B, "prep_c155_a2_1_session.json")
DQJ = os.path.join(B, "donor_queue_v0.json")
MMF = os.path.join(B, "memory_model.json")
ROOTS = dict((k, os.path.join(SIM, "ring_p5s02", k)) for k in ("_census", "_passA"))
ALLF = os.path.join(B, "plan_ring_p5s02_all.json")
AIN, IN, OUT = os.path.join(ROOTS["_passA"], "plan_ring_p5s02p_in.json"), os.path.join(B, "plan_ring_p5s02_in.json"), os.path.join(B, "plan_ring_p5s02.json")
FACTS = os.path.join(B, "prep_c155_a4_1_session.json")
VI_MD5 = "7f2582ae54dc5bc42c3df0bdf3c72d2e"
WANT = {GRAPH: "6716c499", P51_IN: "fabc4b9c", P51B: "75a77a00", SESS51B: "79447fab", DQJ: "15269b6c", MMF: "c87d170a",
        os.path.join(ROOT, "docs", "d1", "ring-p5.md"): "a4b596f0", os.path.join(ROOT, "tools", "stagesim.py"): "eb99c6ba",
        os.path.join(ROOT, "tools", "stagexec.py"): "53e17623", os.path.join(ROOT, "tools", "stage_prerun.py"): "9decb20f",
        os.path.join(ROOT, "tools", "vigraph.py"): "a7eb58c7", os.path.join(ROOT, "tools", "stagekit.py"): "aec03c6c",
        os.path.join(CD, "DonorQueue_v0.vi"): "81dba822"}
MAIN_SRC_READS = 2                                    # main recipe source census_snapshot reads (prep_c152_b2_1_mk.py:79)
MAXACT, LIMIT = 40, 680.0
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                   # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d="", fatal=True):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok and fatal:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
pre = [rel(p) for p in (ALLF, IN, OUT, FACTS) if os.path.exists(p)]
gate("P no pre-existing P5-2 plan / plan_in / all / session file", not pre, pre)
# ---- (n2) the graph and the map
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
    gate("ROW #{0} {1!r} src={2} tu={3} unique in the graph".format(u, name, src, tu), len(rr) == 1, [(r["term_uid"], r["term_name"]) for r in rr], fatal=True)
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


QO1 = mapped("QO1 (Obtain, P5-1)", int(SESS1["symbol_map"]["new:QO1"]),
             OBJ.get(int(SESS1["symbol_map"]["new:QO1"]), {}).get("class") == "Function" and OWN.get("23041", [None, None])[1] is not None,
             "prep_c155_a2_1_session.json symbol_map new:QO1; rows {0}".format([r["term_name"] for r in T if int(r["owner_uid"]) == int(SESS1["symbol_map"]["new:QO1"])]))
qo_out = row(QO1, "queue out", True)
DQ = J(DQJ)
ROLE = dict((o["role"], o) for o in DQ["objects"])
gate("QO1 terminal names == DonorQueue_v0 Obtain's {0}".format([t["name"] for t in ROLE["obtain"]["terminals"]]),
     sorted(r["term_name"] for r in T if int(r["owner_uid"]) == QO1) == sorted(t["name"] for t in ROLE["obtain"]["terminals"]))
L17 = mapped("L17 loop 1.7", 23041, OBJ.get(23041, {}).get("class") == "WhileLoop", "PD374(a) `#23041`; owners {0}".format(OWN.get("23041")))
F8 = mapped("F8 frame 686", int(OWN["23041"][1]), int(OWN["23041"][1]) == 686 and int(row(QO1, "queue out", True)["frame_diagram"]) == 686,
            "owner diagram of #23041 == Obtain's diagram (PD376(a) 686)")
B17 = mapped("B17 body", 23405, OWN.get("23405") == ["WhileLoop", L17], "PD374(a) body #23405; owners {0}".format(OWN.get("23405")))
S376 = mapped("SAVE #376", 376, OBJ.get(376, {}).get("class") == "SubVI" and all(int(r["frame_diagram"]) == B17 for r in T if int(r["owner_uid"]) == 376),
              "PD374(d) `#376` SubVI on #23405")
for nm in ("current frame data array in", "frame index"):
    gate("#376 {0!r} unwired in the P5-1 graph (declared open, PD374(b)/(d))".format(nm), not row(S376, nm, False).get("wire_uid"))
r_ref = row(S376, "saved file refnum", False)
REF = mapped("REF #3052", 3052, [int(x["owner_uid"]) for x in peers(r_ref)] == [3052] and OBJ.get(3052, {}).get("class") == "ControlReferenceConstant",
             "PD374(d) `#3052`, the source of #376 'saved file refnum'")
r_prog = row(S376, "file progress", True)
pp = peers(r_prog)
PROG = mapped("PROG #3453", 3453, any(int(x["term_uid"]) == 3453 for x in pp) and OBJ.get(3453, {}).get("class") == "ControlTerminal",
              "PD374(d) `#3453` 'file progress', a sink of #376 'file progress' {0}".format([(x["owner_uid"], x["term_uid"]) for x in pp]))
OT3 = mapped("OT3 out-tunnel t3", 5204, sorted(int(x["owner_uid"]) for x in pp if int(x["term_uid"]) != 3453) == [5204], "PD374(d) t3 -> `#5204`")
OT4 = mapped("OT4 out-tunnel t4", 10404, [int(x["owner_uid"]) for x in peers(row(S376, "file number to append out", True))] == [10404], "PD374(d) t4 -> `#10404`")
RSR = {}
for nm, u in (("error out", 24083), ("total data array out", 24150)):
    pr = peers(row(S376, nm, True))
    RSR[nm] = mapped("RSR {0}".format(nm), u, [(int(x["owner_uid"]), x["owner_class"]) for x in pr] == [(u, "RightShiftRegister")],
                     "PD374(d) t{0} -> RSR `#{1}`".format(0 if nm == "error out" else 1, u))
LSR = {}
for nm in ("error in", "total data array in"):
    pr = peers(row(S376, nm, False))
    LSR[nm] = mapped("LSR {0} (read from the graph)".format(nm), int(pr[0]["owner_uid"]) if len(pr) == 1 else None,
                     len(pr) == 1 and pr[0]["owner_class"] == "LeftShiftRegister" and pr[0]["term_class"] == "InnerTerminal",
                     "the source of #376 {0!r}: {1}".format(nm, [(x["owner_uid"], x["owner_class"], x["term_uid"]) for x in pr]))
TIN = {}
for nm, u in (("cal cluster path", 24357), ("file size", 24361), ("selected path", 25223)):
    pr = peers(row(S376, nm, False))
    TIN[nm] = mapped("TIN {0}".format(nm), u, [(int(x["owner_uid"]), x["owner_class"], x["term_class"]) for x in pr] == [(u, "LoopTunnel", "InnerTerminal")],
                     "PD374(d) in-tunnel `#{0}` -> #376 {1!r}".format(u, nm))
cond = [r for r in T if int(r["owner_uid"]) == B17 and int(r["frame_diagram"]) == B17 and not r["is_source"] and not r["term_name"] and r.get("wire_uid")]
cond = uniq(cond)
scaf_src = [x for x in peers(cond[0]) if int(x["owner_uid"]) != B17] if len(cond) == 1 else []
SCAF = mapped("SCAF #23042 (scaffold stop)", 23042, len(cond) == 1 and [(int(x["owner_uid"]), x["term_name"]) for x in scaf_src] == [(23042, "x = y?")],
              "PD374(d) `#23042` 'x = y?' drives the 1.7 cond terminal t{0} by w{1}".format(cond and cond[0]["term_uid"], cond and cond[0]["wire_uid"]))
W_COND = int(cond[0]["wire_uid"])
SCIN = mapped("SCIN #23501 (scaffold in-tunnel)", 23501, sorted(set(int(x["owner_uid"]) for x in peers(row(SCAF, "x", False)))) == [23042, 23501] and
              OBJ.get(23501, {}).get("class") == "LoopTunnel", "PD374(d) in-tunnel `#23501` feeds #23042 x and y")
gate("NOT #8486: #23501's outer is fed by #8486 'x+1', which stays (PD374(d))", 8486 in [int(x["owner_uid"]) for x in peers(row(SCIN, "", False, None) if False else
     next(r for r in T if int(r["owner_uid"]) == SCIN and r["term_class"] == "OuterTerminal"))])
P51 = J(P51_IN)
K0D = next(a for a in P51["actions"] if a["id"] == "c_k0")["donor"]          # DonorSRInit_v0 #248, as P5-1 (read, not typed)
INCD = next(a for a in P51["actions"] if a["id"] == "c_inc")                 # Increment $work #1978, as P5-1
LAB = SPR.prim_donor_labels()
WORKD = {"Equal?": 10019, "And": 9647}                                       # the $work donors stored plans used (plan_ring_p3a.json:7, plan_ring_p4_v10.json:46)
for p_, u in WORKD.items():
    gate("WD $work donor #{0} label {1!r} == {2!r}, present in the P5-1 graph".format(u, LAB.get(u), p_), LAB.get(u) == p_ and u in OBJ)


def wterms(u):
    return [{"name": r["term_name"], "is_source": bool(r["is_source"]), "term_class": r["term_class"]} for r in uniq([r for r in T if int(r["owner_uid"]) == u])]


def dterms(role):
    return [{"name": t["name"], "is_source": t["is_source"], "term_class": "ParameterTerminal"} for t in ROLE[role]["terminals"]]


EQ_T, AND_T = wterms(WORKD["Equal?"]), wterms(WORKD["And"])                   # terminal names read from the graph rows of the donors
EQ_OUT = [t["name"] for t in EQ_T if t["is_source"]]
EQ_IN = sorted(t["name"] for t in EQ_T if not t["is_source"])
AND_OUT = [t["name"] for t in AND_T if t["is_source"]]
AND_IN = sorted(t["name"] for t in AND_T if not t["is_source"])
gate("WT donor terminals: Equal? in {0} out {1}; And in {2} out {3}".format(EQ_IN, EQ_OUT, AND_IN, AND_OUT),
     len(EQ_OUT) == 1 and len(EQ_IN) == 2 and len(AND_OUT) == 1 and len(AND_IN) == 2)


# ---- (n3) the >= 0 donor search (PD374(c) 'records final >= 0')
GE_CANDS = sorted(set(l for l in LAB.values() if l and re.search(r"Greater Or Equal|>=|\u2265", str(l))) |
                  set(v[0] for v in SPR.PRIM_DONORS.values() if re.search(r"Greater Or Equal|>=", v[0])))
print("FACT GE donor search 'Greater Or Equal*' in main_vi_node_labels.json ({0} labels) + PRIM_DONORS ({1} entries): {2}".format(
      len(LAB), len(SPR.PRIM_DONORS), GE_CANDS), flush=True)
DQF = os.path.join(CD, "DonorQueue_v0.vi")
W = lambda i, s, d, w: {"op": "wire", "id": i, "src": s, "dst": d, "why": w}                   # noqa: E731
TUN = lambda i, d, a, w, f=0: {"op": "tunnel", "id": i, "loop": "new:CQ7", "body": "new:CQ7.f{0}".format(f), "parent": B17, "dir": d, "as": a, "why": w}  # noqa: E731
FR = lambda a, f: {"uid": "new:" + a, "side": "inner", "frame": f}            # noqa: E731
pos = lambda u: [int(OBJ[u]["pos"][0]), int(OBJ[u]["pos"][1])]                 # noqa: E731
PDA, PDB, PDC, PDD, PD6 = "PD376(d)", "PD374(b)", "PD374(c)", "PD374(d)", "PD374(a)"
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
    W("w_q7_rel", "new:QS7R.outer", "new:RQ1.queue", PDA + " R.outer -> Release (row-18 route)")]}
GROUPS["B"] = {"deps": ["A"], "link": "I32 100 constant on Dequeue 'timeout in ms (-1)'", "acts": [
    {"op": "create", "id": "c_tmo", "class": "DigitalNumericConstant", "diagram": B17, "as": "TM1", "on": "new:DQ1.timeout in ms (-1)", "value": 100,
     "why": PD6 + " Dequeue with timeout 100 ms (const_on_term, plan_ring_p4_s04v18_in.json p4_wait_k)"}]}
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
    ri = row(RSR[no], None, False, None) if False else next(r for r in uniq([r for r in T if int(r["owner_uid"]) == RSR[no] and r["term_class"] == "InnerTerminal"]))
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
GROUPS["J"] = {"deps": ["I"], "link": "stop: delete scaffold #23042 / #23501; local 'records final' == counter after the iteration AND (>= 0: GAP) -> cond", "acts": [
    {"op": "delete_wire", "id": "dw_cond", "wire_uid": W_COND, "why": PDD + " scaffold stop wire #23042 -> cond (read from the graph)"},
    {"op": "delete_object", "id": "do_23042", "uid": SCAF, "why": PDD + " scaffold stop `#23042` removed"},
    {"op": "delete_object", "id": "do_23501", "uid": SCIN, "why": PDD + " scaffold in-tunnel `#23501` removed (NOT #8486)"},
    {"op": "create", "id": "c_lr7", "class": "Local", "diagram": B17, "as": "LR7", "label": "records final (1.2 to 1.7)", "mode": "read",
     "terminals": [{"name": "records final (1.2 to 1.7)", "is_source": True, "term_class": "Terminal"}], "why": PDC + " published counter read by a local"},
    {"op": "create", "id": "c_eq7", "class": OBJ[WORKD["Equal?"]]["class"], "diagram": B17, "as": "EQ7", "prim": "Equal?", "donor": {"donor": "$work", "uid": WORKD["Equal?"]},
     "terminals": wterms(WORKD["Equal?"]), "why": PDC + " counter (after this iteration) == records final"},
    W("w_eq7_x", "new:TD7.outer", "new:EQ7." + EQ_IN[0], PDC + " the counter AFTER this iteration = the case out-tunnel value"),
    W("w_eq7_y", "new:LR7.value", "new:EQ7." + EQ_IN[1], PDC),
    {"op": "create", "id": "c_and7", "class": OBJ[WORKD["And"]]["class"], "diagram": B17, "as": "AN7", "prim": "And", "donor": {"donor": "$work", "uid": WORKD["And"]},
     "terminals": wterms(WORKD["And"]), "why": PDC + " (records final >= 0) AND (counter == records final)"},
    W("w_and7_x", "new:EQ7." + EQ_OUT[0], "new:AN7." + AND_IN[0], PDC),
    W("w_and7_cond", "new:AN7." + AND_OUT[0], {"uid": L17, "term": "cond"}, PDC + " 1.7 stops")]}
for k3, (nm, ot) in (("K3", ("file progress", OT3)), ("K4", ("file number to append out", OT4))):
    s_ = k3.lower()
    GROUPS[k3] = {"deps": ["D"], "link": "NEW SR for #376 {0!r} (today -> #{1}): case tunnel out -> R.inner; L.inner -> case tunnel in -> timed-out frame pass-through".format(nm, ot),
                  "acts": [
        {"op": "add_shift_reg", "id": "sr_" + s_, "loop": L17, "body": B17, "parent": F8, "as": "S" + k3, "why": PDD + " NEW SR for t" + k3[1]},
        TUN("t_{0}o".format(s_), "out", "O" + k3, PDD), W("w_{0}out".format(s_), end(S376, nm, True), "new:O{0}.inner".format(k3), PDD),
        W("w_{0}r".format(s_), "new:O{0}.outer".format(k3), "new:S{0}R.inner".format(k3), PDD),
        TUN("t_{0}i".format(s_), "in", "I" + k3, PDD), W("w_{0}l".format(s_), "new:S{0}L.inner".format(k3), "new:I{0}.outer".format(k3), PDD),
        W("w_{0}pass".format(s_), FR("I" + k3, "True"), FR("O" + k3, "True"), PDD + " value passes through the timed-out frame")]}
GAP_GE = {"group": "J", "row": "J-ge0", "kind": "create primitive (>= 0 comparison, PD374(c) 'records final >= 0') + its two wires", "from": "LR7 'records final' value",
          "to": "AN7 'y'", "status": "GAP", "error": "no donor with a 'Greater Or Equal*' label: main_vi_node_labels.json {0} labels, PRIM_DONORS {1} entries -> {2}".format(
              len(LAB), len(SPR.PRIM_DONORS), GE_CANDS),
          "tool": "tools/stage_prerun.py:2846-2866 (prim_donor_check: '$work donor ... UNMEASURED' / 'external donor ... UNMEASURED (not in PRIM_DONORS)')"}
if GE_CANDS:
    GAP_GE = None
gate("GE >= 0 donor search done ({0})".format("GAP" if GAP_GE else GE_CANDS), True)
# ---- (n3) greedy census
TOP = {"schema": "stageplan/1", "context": P51.get("context") or {"s1_key": "D1_s1_copy"}}
BASEREF = {"path": rel(GRAPH), "md5": md5(GRAPH)}
OWNERS = SX.plan_base_owners({"base": BASEREF})
gate("BO base owner map read by stagexec.plan_base_owners ({0} entries) == graph owners".format(len(OWNERS)), OWNERS == OWN and bool(OWNERS))
SRC = dict((f, open(os.path.join(ROOT, "tools", f), encoding="utf-8").read().splitlines()) for f in ("stagesim.py", "stagexec.py", "stage_prerun.py"))


def cite(msg):
    """the tool line whose source text holds the longest literal piece of a refusal message (>= 16 chars)."""
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
    print("FACT CENSUS GAP {0} ({1}): {2} | tool {3}".format(g, kind, str(why)[:400], ERR[g]["tool"]), flush=True)
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
    json.dump(dict(TOP, stage="ring_p5s02c", goal="card 155-a4-1 ROUTE CENSUS round {0}: groups {1}".format(rnd, live), base=BASEREF, actions=acts),
              open(CPATH, "w", encoding="utf-8"), indent=1)
    try:
        SC = SS.simulate(CPATH, GRAPH, out_root=ROOTS["_census"], plan_out_dir=ROOTS["_census"], log=lambda *x: None, route_check=False)
    except Exception as e:                                                                    # noqa: BLE001 - a simulator crash is a census fact
        crash = "CRASH {0}: {1}".format(type(e).__name__, e)
        hit = None
        for j in range(1, len(live) + 1):                                                    # the first group whose prefix crashes
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
        routes = sorted(set("{0}/{1}".format(*opof[i]) for i in idx))
        prov = [i for i in idx if (eff.get(i) or {}).get("provisional")]
        msrc = sorted(set(str((eff.get(i) or {}).get("model_source")) for i in idx))
        CROWS.append({"group": g, "link": gg["link"], "status": "OK", "actions": [a["id"] for a in gg["acts"]], "routes": routes, "sim_steps": idx,
                      "model_source": msrc, "provisional": prov})
    else:
        CROWS.append({"group": g, "link": gg["link"], "status": STATUS[g], "actions": [a["id"] for a in gg["acts"]], "error": ERR[g]["error"],
                      "stage": ERR[g]["stage"], "tool": ERR[g]["tool"]})
if GAP_GE:
    CROWS.append(GAP_GE)
for c in CROWS:
    print("CENSUS {0} | {1} | {2} | {3}".format(c.get("group"), c.get("status"), c.get("link") or c.get("kind"),
          c.get("routes") or (c.get("error"), c.get("tool"))), flush=True)
gate("CEN every group censused OK / GAP / BLOCKED; every GAP carries its refusal ({0} OK, {1} GAP, {2} BLOCKED)".format(
     sum(1 for c in CROWS if c["status"] == "OK"), sum(1 for c in CROWS if c["status"] == "GAP"), sum(1 for c in CROWS if c["status"] == "BLOCKED")),
     all(c["status"] in ("OK", "GAP", "BLOCKED") and (c["status"] != "GAP" or c.get("error")) for c in CROWS))
OKG = [g for g in GROUPS if STATUS[g] == "OK"]
ALLACTS, ALLOWN = flat(OKG)
json.dump(dict(TOP, stage="ring_p5s02_all", goal=("card 155-a4-1 P5-2 INPUT PLAN (PD374(b)(c)(d), PD376(d)): every censused-OK group {0} on the REAL P5-1 graph 6716c499; "
                                                   "GAP/BLOCKED groups {1} are not rows").format(OKG, [g for g in GROUPS if STATUS[g] != "OK"])[:400],
               base=BASEREF, actions=ALLACTS), open(ALLF, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(ALLF))
gate("S00 the all-groups input plan validates ({0} actions)".format(len(ALLACTS)), ok_, why_)
# ---- (n4) the cut
OPS = SX.compile_plan(dict(TOP, actions=ALLACTS), owners=OWNERS)
KINDS = [o["kind"] for o in OPS]
MODEL = SPR.load_memory_model()
XS = SPR.x10_start(VI_MD5, MODEL)
START = XS[0] if XS else None
gate("XS x10_start(7f2582ae) measured: {0}".format(XS), XS is not None)
v = lambda k: float(MODEL[k]["value"])                                                        # noqa: E731


def main_of(n):
    cps = sorted({0, n} | set(k for k in range(1, n + 1) if KINDS[k - 1] in SX.BIND_KINDS))
    mp = SPR.x10_model_peak(KINDS[:n], cps, model=MODEL, start_mb=START)
    return round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), mp, cps


TAB = [(n, main_of(n)[0], max(OPS[n - 1]["acts"])) for n in range(1, len(OPS) + 1)]
print("FACT CUT start {0} ({1}); ops {2}; per-prefix (n, MAIN, last action) {3}".format(START, XS and XS[1], len(OPS), TAB), flush=True)
fit = [n for n, m, ka in TAB if m <= LIMIT and ka <= MAXACT and sorted(x for o in OPS[:n] for x in o["acts"]) == list(range(1, ka + 1))]
NS = max(fit) if fit else 0
gate("CUT first step: n* {0} of {1} ops (MAIN {2} <= {3}, actions {4} <= {5})".format(NS, len(OPS), NS and TAB[NS - 1][1], LIMIT, NS and TAB[NS - 1][2], MAXACT),
     NS >= 1, TAB)
KA = TAB[NS - 1][2]
LATER, k0 = [], NS
while k0 < len(OPS):                                                                       # later cut points: same rule from the end of the previous step
    s0 = max(OPS[k0 - 1]["acts"])
    best = None
    for n in range(k0 + 1, len(OPS) + 1):
        ka = max(OPS[n - 1]["acts"])
        if ka - s0 <= MAXACT and sorted(x for o in OPS[k0:n] for x in o["acts"]) == list(range(s0 + 1, ka + 1)):
            best = n
    if best is None:
        break
    LATER.append({"ops": [k0 + 1, best], "actions": [s0 + 1, max(OPS[best - 1]["acts"])], "ids": [ALLACTS[s0]["id"], ALLACTS[max(OPS[best - 1]["acts"]) - 1]["id"]],
                  "groups": sorted(set(ALLOWN[s0:max(OPS[best - 1]["acts"])])), "x10": "start = the measured load of the previous step's adopted file (not known offline)"})
    k0 = best
print("FACT LATER cut points (by <= 40 actions; X10 of each from its own adopted start): {0}".format(LATER), flush=True)
ACTS = ALLACTS[:KA]
print("FACT STEP1 actions 1..{0}: groups {1}".format(KA, sorted(set(ALLOWN[:KA]), key=list(GROUPS).index)), flush=True)
os.makedirs(ROOTS["_passA"], exist_ok=True)
json.dump(dict(TOP, stage="ring_p5s02p", goal="card 155-a4-1 PASS A: P5-2 step 1 = actions 1..{0} on the real P5-1 graph, no open_rows".format(KA),
               base=BASEREF, actions=ACTS), open(AIN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(AIN))
gate("S0 pass-A input validates against stageplan/1 ({0} actions)".format(len(ACTS)), ok_, why_)
SA = SS.simulate(AIN, GRAPH, out_root=ROOTS["_passA"], plan_out_dir=ROOTS["_passA"], log=lambda *x: None, route_check=False)


def step_facts(tag, R_):                                                                     # copied from prep_c155_a2_1_mk.py:255-264 (OPEN)
    out = {}
    for st in (R_ or {}).get("steps") or []:
        p_ = (st.get("file") or {}).get("path")
        sj = J(p_)
        out[st["n"]] = hashlib.md5(json.dumps(sj["state"], sort_keys=True, default=str).encode("utf-8")).hexdigest()
        print("FACT STEP {0} n {1:02d} op {2} id {3}: {4} model {5}; file {6} md5 {7}; state {8}".format(
              tag, st["n"], st.get("op"), st.get("id"), "ERROR " + str(st.get("error")) if st.get("error") else ("PROVISIONAL" if st.get("provisional") else "ok"),
              st.get("model_source"), p_ and rel(p_), p_ and md5(p_), out[st["n"]][:8]), flush=True)
    return out


HA = step_facts("PASSA", SA)
provA = [s["n"] for s in SA["steps"] if s.get("provisional")]
gate("SA pass A replays every action to its end: failed {0}; steps {1} == actions + 1; PROVISIONAL steps {2}".format(
     json.dumps(SA.get("failed"), default=str), len(SA["steps"]), provA), SA["failed"] is None and len(SA["steps"]) == len(ACTS) + 1 and not provA
     and SA.get("end_cdiff_rows") is not None, SA.get("failed"))
P51BJ = J(P51B)
ok_pairs = dict(((int(r["node"]), r["term"]), "p5s01-open") for r in P51BJ.get("open_rows") or [])
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c155_a2_1_mk.py:274-287, copied (OPEN)
    n0 = SA["steps"][-1]["n"]
    for st in reversed(SA["steps"]):
        if st.get("cdiff_rows") is not None and key in st["cdiff_rows"]:
            n0 = st["n"]
        else:
            break
    p = (SS.V.key_parts(key)[0], SS.V.key_parts(key)[2])
    if n0 >= 1:
        ties[key] = {"n": n0, "id": ACTS[n0 - 1]["id"], "op": ACTS[n0 - 1]["op"], "class": ACTS[n0 - 1].get("class") or ACTS[n0 - 1]["op"], "pair": p}
    elif p in ok_pairs:
        ties[key] = {"n": 0, "id": ok_pairs[p], "op": "base", "class": "step0-declared", "pair": p}
    else:
        untied.append((key, n0))
print("FACT TIE end rows {0}: by action {1}; step-0 declared {2}".format(len(SA["end_cdiff_rows"]),
      sorted((k, t["id"]) for k, t in ties.items() if t["n"] >= 1), sum(1 for t in ties.values() if t["n"] == 0)), flush=True)
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    print("FACT TIE-ROW owner #{0} term {1!r} made by {2} (step {3}, {4}) key {5}".format(t["pair"][0], t["pair"][1], t["id"], t["n"], t["class"], k), flush=True)
gate("TIE every end row ({0}) tied to a P5-2 action or a P5-1 declared open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c155-a4-1: made by P5-2 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c155-a4-1: open at step 0 = declared open row of plan_ring_p5s01b.json")[:300]})
GOAL = ("RING P5-2 step 1 (card 155-a4-1, PD374(b)(d) + PD376(d), PD378(c)): actions 1..{0} ({1} ops) = groups {2} - refnum SR on 1.7, Dequeue (100 ms), "
        "Release on 686, Case on 'timed out?', #376/#3052/#3453 moved into it and re-wired; on the REAL P5-1 graph 6716c499").format(
        KA, NS, sorted(set(ALLOWN[:KA]), key=list(GROUPS).index))
json.dump(dict(TOP, stage="ring_p5s02", goal=GOAL[:400], base=BASEREF, open_rows=orows, actions=ACTS), open(IN, "w", encoding="utf-8"), indent=1)
ok_, why_ = protocol.validate_obj(J(IN))
gate("S1 plan input validates ({0} actions, {1} open pairs)".format(len(ACTS), len(orows)), ok_, why_)
SB = SS.simulate(IN, GRAPH, out_root=SIM, plan_out_dir=B, log=lambda m: print(m, flush=True), route_check=True)
HB = step_facts("REALSIM", SB)
p = J(OUT) if os.path.isfile(OUT) else {}
fz = p.get("finalized") or {}
provB = [s["n"] for s in SB["steps"] if s.get("provisional")]
gate("SB REALSIM plan FINAL on the real graph: failed {0}; route check {1}; fs_border_gate {2}; open_rows_match; end rows == pass A; PROVISIONAL {3}".format(
     SB.get("failed"), (fz.get("route_check") or {}).get("status"), (fz.get("fs_border_gate") or {}).get("status"), provB),
     bool(SB["final"]) and p.get("final") is True and fz.get("open_rows_match") is True and (fz.get("route_check") or {}).get("status") == "PASS"
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and not provB, {"final": SB["final"], "rc": fz.get("route_check")})
gate("SAME pass A and REALSIM step states equal at every step ({0} steps)".format(len(HA)), HA == HB,
     [n for n in sorted(set(HA) | set(HB)) if HA.get(n) != HB.get(n)])
for r in (fz.get("route_check") or {}).get("rows") or []:
    print("FACT ROUTE k {0} {1} {2}: {3} {4}".format(r.get("k"), r.get("op"), r.get("ids"), r.get("route"), (r.get("how") or "")[:80]), flush=True)
ops = SX.compile_plan(p)                                                                      # the plan's own pinned base (plan_base_owners)
cps = sorted({0, len(ops)} | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))
mp = SPR.x10_model_peak([o["kind"] for o in ops], cps, model=MODEL, start_mb=START)
MAIN = round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1)
print("FACT X10 start {0}; ops {1} kinds {2}; checkpoints {3}; N {4} R {5}; Executor peak {6}; MAIN {7}; fail_above {8}; MEMSTOP {9}".format(
      START, len(ops), dict(collections.Counter(o["kind"] for o in ops)), cps, mp["N"], mp["R"], mp["peak_mb"], MAIN, SPR.X10_FAIL_MB, SX.MEM_STOP_MB), flush=True)
gate("X10 P5-2 step-1 plan: kinds/acts == ops 1..{0}; MAIN {1} == MAIN(n*) {2} <= {3} at start {4} (Executor {5}; MEMSTOP {6} unchanged)".format(
     NS, MAIN, TAB[NS - 1][1], LIMIT, START, mp["peak_mb"], SX.MEM_STOP_MB),
     [(o["kind"], o["acts"]) for o in ops] == [(o["kind"], o["acts"]) for o in OPS[:NS]] and MAIN == TAB[NS - 1][1] and MAIN <= LIMIT
     and SPR.X10_FAIL_MB == LIMIT and SX.MEM_STOP_MB == 695, mp)
lint = SPR.control_path_lint(p)
gate("X8 control_path_lint clean (queue creates carry data_stream + why; no edge detector)", not lint, lint)
ok17, det17 = SPR.x17_gate([p])
gate("X17 x17_gate over the plan", ok17, det17)
SF = dict((int(x["n"]), x["path"]) for x in fz.get("step_files") or [])
SGC = []
for n, a in enumerate(p["actions"], 1):                                                     # prep_c155_a2_1_mk.py:336-347, copied (OPEN)
    if a.get("op") != "wire" or n not in SF or (n - 1) not in SF:
        continue
    eff_ = J(SF[n]).get("effect") or {}
    prev = J(SF[n - 1])["state"]["terminals"]
    du, su = eff_.get("dst_term_uid"), eff_.get("src_term_uid")
    rd = next((r for r in prev if r["term_uid"] == du), None)
    rs = next((r for r in prev if r["term_uid"] == su), None)
    if rd is not None and SX.is_ct(rd):
        route = "indicator" if (rs is not None and rs.get("wire_uid")) else "ctlsink"
        SGC.append({"n": n, "id": a["id"], "sink": [rd["owner_uid"], rd["term_name"]], "dst_term_uid": du, "src_term_uid": su, "route": route,
                    "needs_sink_gate": route == "indicator"})
print("FACT SG-CENSUS {0} ControlTerminal-sink row(s); {1} need a declared sink gate: {2}".format(
      len(SGC), sum(1 for e in SGC if e["needs_sink_gate"]), SGC), flush=True)
json.dump({"card": "155-a4-1", "plan": {"path": rel(OUT), "md5": md5(OUT)}, "all_plan": {"path": rel(ALLF), "md5": md5(ALLF)},
           "symbol_map": MAP, "census": CROWS, "actions": len(ACTS), "ops": len(ops),
           "cut": {"n_ops": NS, "k_actions": KA, "per_prefix_main": TAB, "limit": LIMIT, "max_actions": MAXACT}, "later_cuts": LATER,
           "kinds": dict(collections.Counter(o["kind"] for o in ops)), "start_mb": START, "start_cite": XS and XS[1],
           "exec_peak_mb": mp["peak_mb"], "main_peak_mb": MAIN, "main_src_reads": MAIN_SRC_READS, "checkpoints": cps, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ties": dict((k, t) for k, t in ties.items()), "sink_gate_census": SGC, "passA_states": HA,
           "realsim_states": HB, "steps": [{"n": s["n"], "op": s.get("op"), "id": s.get("id"), "model_source": s.get("model_source"),
                                           "file": rel(s["file"]["path"]), "md5": s["file"]["md5"]} for s in SB["steps"]]},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (ALLF, AIN, IN, OUT, FACTS))
gate("U inputs untouched", all(md5(q) == M0[q] for q in WANT))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
