r"""diag_c100_rows - card 100-1 (PD212(i)5(a)), OFFLINE, no LabVIEW: the display-loop STAGE PLAN ROWS R1-R8 of
tools/bench/cards/rows_spec_100.md on D1_s1_copy.vi's graph, the stage card whose `requires` cites every op / verb /
terminal the rows use, and the facts. No VI is opened, edited or saved.

WHAT EXISTED FIRST (checked 2026-09-26): graph = tools/bench/par1359_95_graph.json (S1 terminal table + objs, md5
3e3d23ce; no `owners` - loop<->body links from tools/bench/sim/l2a1/graph_k_80_owners.json, diag_c100_probe2.log);
format = tools/bench/sim/l2a1/stageplan_l2a1.json (stageplan/1); executor tools/stagexec.py (compile_plan :153 - no
`create` executor :200-201, move_in dest int :975); simulator tools/stagesim.py (OPS :802; op_create :787 int diagram;
move_in :461 / tunnel :643 int diagrams). Verbs: gscript.loop_in :1249 (OpWhileLoopIn_v0/OpForLoopIn_v0),
stagekit.move_in :595 (OpMoveIn_v0), stagekit.copy_in :779 (OpMoveByIndex_v0), stagexec's connect route =
connect_nested_v1 (tools/recipes/build_opconnectnested_v1.py:418, OpConnectNested_v1) / stagekit.connect_from_wire :608
(NOT stagekit.connect :601 -> gscript.connect_nested_v2, which raises at entry: op never built, gscript.py:3224-3247), gscript.create_indicator :2633 / create_control :2605
(TOP-LEVEL Nodes[] only), gscript.set_control_label :3433 (OpLabelSet_v0), gscript.set_default_in_memory :3450,
OpCreateLocalRead_v0 (Write? steers READ/WRITE, toolkit-capabilities.md:76; READ caller diag_c62_s3b_build.py:359),
OpStopFromNode_v0 (toolkit-capabilities.md:67), OpCreateConstOnTerm_v0 (toolkit-capabilities.md:70).

PREDICTION CONTRACT: D1_s1_copy.vi md5 == 3e3d23ce... at start and end; graph md5 field the same; every bound
(owner uid, term uid) pair exists in the graph with the stated direction; every moved node's frame_diagram is 7911
(R3) / 639 (R4); LabVIEW process count 0 at start and end (the script never starts it).
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol  # noqa: E402

VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi"
S1MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
GRAPH = os.path.join(HERE, "par1359_95_graph.json")
KOWN = os.path.join(HERE, "sim", "l2a1", "graph_k_80_owners.json")
OUTD = os.path.join(HERE, "sim", "disp")
PLAN = os.path.join(OUTD, "stageplan_disp.json")
CARD = os.path.join(HERE, "cards", "stage_disp_requires.json")
FACTS = os.path.join(HERE, "facts_c100_rows.json")
GFILE = "tools/bench/par1359_95_graph.json"
npass = nfail = 0
first_fail = None


def gate(label, ok, detail=""):
    global npass, nfail, first_fail
    npass, nfail = npass + bool(ok), nfail + (not ok)
    if not ok and first_fail is None:
        first_fail = label
    print("GATE {0} {1} {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lv_count():
    out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout
    return sum(1 for ln in out.splitlines() if "labview" in ln.lower())


gate("H0 LabVIEW not running at start", lv_count() == 0)
gate("H1 D1_s1_copy md5 start", md5(VI) == S1MD5)
G = json.load(open(GRAPH, encoding="utf-8"))
gate("H2 graph md5 field == S1", G["md5"] == S1MD5, G["md5"])
T = G["terminals"]
OBJ = {o["uid"]: o for o in G["objs"]}
KO = json.load(open(KOWN, encoding="utf-8"))["owners"]
BYT = {}
for r in T:
    BYT.setdefault(r["term_uid"], r)


def B(owner, term, src=None, fd=None):
    """A bound end, read from the S1 graph: {uid, term_uid, term_name, is_source, frame_diagram, wire_uid}."""
    r = BYT.get(term)
    ok = r is not None and r["owner_uid"] == owner and (src is None or r["is_source"] == src) and \
        (fd is None or r["frame_diagram"] == fd)
    gate("B #{0}.t{1}".format(owner, term), ok, "" if r is None else "{0!r} src={1} fd{2} w{3}".format(
        r["term_name"], r["is_source"], r["frame_diagram"], r["wire_uid"]))
    r = r or {}
    return {"uid": owner, "term_uid": term, "term_name": r.get("term_name"), "is_source": r.get("is_source"),
            "frame_diagram": r.get("frame_diagram"), "s1_wire": r.get("wire_uid")}


def ctl(term):
    """A front-panel terminal's label, read from the graph by term uid (never typed)."""
    r = BYT.get(term)
    gate("CT t{0} is ControlTerminal".format(term), bool(r) and r["term_class"] == "ControlTerminal",
         repr(r and r["term_name"]))
    return r["term_name"] if r else None


# ---- structure facts (graph + K owners)
gate("S #25380 owner diagram 686 (K owners[25392]=[WhileLoop,25380], tunnel outer faces on 686)",
     KO.get("25392") == ["WhileLoop", 25380] and OBJ.get(25380, {}).get("class") == "WhileLoop")
gate("S #1359 body 7911", KO.get("7911") == ["ForLoop", 1359])
gate("S #637 body 639", KO.get("639") == ["WhileLoop", 637])
BODY7911 = OBJ[7911]["pos"]
BODY639 = OBJ[639]["pos"]

L_TURNOFF, L_BASE, L_FHW, L_EHW, L_FORCE = ctl(24444), ctl(8476), ctl(28170), ctl(29091), ctl(8323)
L_RING, L_WLC, L_PERIOD = "plot ring (display)", "plot WLC (display)", "Display period (ms)"   # rows_spec_100.md R5/R7

A = []


def act(**k):
    A.append(k)
    return k


def move(uid, dest, body_pos, row, verb):
    o = OBJ.get(uid)
    gate("M #{0} exists".format(uid), o is not None, o and o["class"])
    fd = {r["frame_diagram"] for r in T if r["owner_uid"] == uid and r["term_class"] not in ("OuterTerminal",)}
    rel = [o["pos"][0] - body_pos[0], o["pos"][1] - body_pos[1]] if o else None
    act(op="move_in", id="mv_{0}".format(uid), row=row, nodes=[uid], dest_diagram=dest, pos=None,
        pos_rel_to_old_body=rel, from_diagram=sorted(fd), cls=o and o["class"], verb=verb)
    return fd


def wire(src, dst, row, id_, verb="stagexec connect: connect_from_wire (source wired) else connect_nested_v1 "
                                  "(OpConnectNested_v1)"):
    act(op="wire", id=id_, row=row, src=src, dst=dst, verb=verb)


# ---- R1 display loop on 686 ; R2 For inside it
act(op="create", id="r1_dl", row="R1", **{"class": "WhileLoop"}, diagram=686, **{"as": "DL"}, body="new:DL.body",
    pos=None, verb="gscript.loop_in('while', target, diagram_index(686), location) tools/gscript.py:1249",
    op_vi="OpWhileLoopIn_v0", note="sibling of #637/#25380 on 686; 686 holds #25380 (sequenced after #8603 on 4866)")
act(op="create", id="r2_dlf", row="R2", **{"class": "ForLoop"}, diagram="new:DL.body", **{"as": "DLF"},
    body="new:DLF.body", pos=None, verb="gscript.loop_in('for', target, diagram_index(new:DL.body), location)",
    op_vi="OpForLoopIn_v0")
# ---- R3 move the 11363-only set into DLF's body (one node per action, R-SEQ)
SET = [8775, 8795, 8741, 8764, 28180, 28233, 27716, 29009, 11310]
for u in SET:
    fd = move(u, "new:DLF.body", BODY7911, "R3", "stagekit.move_in tools/stagekit.py:595 (OpMoveIn_v0)")
    gate("R3 #{0} sits on 7911".format(u), fd == {7911}, sorted(fd))
# internal edges of the set, re-made after the sequential moves cut them (stagesim R-SEQ)
INTERNAL = [((8775, 8774), (8741, 8753)), ((8795, 8794), (8741, 8762)), ((8741, 8750), (8764, 8790)),
            ((8741, 8759), (28233, 28291)), ((8764, 8770), (29009, 29049)), ((28180, 28189), (28233, 28281)),
            ((28233, 28251), (27716, 27827)), ((29009, 29025), (11310, 11320)), ((27716, 27784), (11310, 11323))]
for (su, st), (du, dt) in INTERNAL:
    s, d = B(su, st, True, 7911), B(du, dt, False, 7911)
    gate("R3 edge w{0} internal".format(s["s1_wire"]), s["s1_wire"] and s["s1_wire"] == d["s1_wire"])
    wire(s, d, "R3", "rw_{0}_{1}".format(st, dt))
# ---- R4 BuildArray #11261 into DL's body
fd = move(11261, "new:DL.body", BODY639, "R4", "stagekit.move_in tools/stagekit.py:595 (OpMoveIn_v0)")
gate("R4 #11261 sits on 639", fd == {639}, sorted(fd))
# ---- R5 frame side: two NEW hidden indicators on existing wires inside 639
RING_SRC = B(9227, 9234, True, 639)          # w9215 source (#9227 index-out tunnel outer face)
WLC_SRC = B(11608, 11614, True, 639)         # #11608 'output cluster' (w12256)
gate("R5 ring source wire is w9215", RING_SRC["s1_wire"] == 9215, RING_SRC["s1_wire"])
for sid, lab, src in (("IND_RING", L_RING, RING_SRC), ("IND_WLC", L_WLC, WLC_SRC)):
    act(op="create", id="r5_" + sid.lower(), row="R5", **{"class": "ControlTerminal"}, diagram=639, **{"as": sid},
        indicator=True, label=lab, visible=False, born_on=src,
        verb="MISSING nested create-indicator: gscript.create_indicator :2633 addresses VI->Block Diagram->Nodes[] "
             "only; 639 is #637's body", then=["gscript.set_control_label :3433 (OpLabelSet_v0)",
                                                "MISSING Visible=False writer"])
# ---- R6 display side: local READs, tunnels into DLF, #11261 wiring, local WRITE of #8323
RD = "OpCreateLocalRead_v0 Write?=False (toolkit-capabilities.md:76; caller tools/bench/diag_c62_s3b_build.py:359) " \
     "on the top-level diagram + stagekit.move_in to new:DL.body"
for sid, lab in (("LR_RING", L_RING), ("LR_WLC", L_WLC), ("LR_BASE", L_BASE), ("LR_FHW", L_FHW),
                 ("LR_EHW", L_EHW)):
    act(op="create", id="r6_" + sid.lower(), row="R6", **{"class": "Local"}, diagram="new:DL.body", **{"as": sid},
        label=lab, mode="read", terminals=[{"name": "", "is_source": True}], verb=RD)
X8741 = B(8741, 8747, False, 7911)
X8764 = B(8764, 8777, False, 7911)
X27716 = B(27716, 27818, False, 7911)
X28180 = B(28180, 28223, False, 7911)
X29009R, X29009L = B(29009, 29043, False, 7911), B(29009, 29046, False, 7911)
gate("R6 old inbound: #8741 array <- w8811", X8741["s1_wire"] == 8811)
gate("R6 old inbound: #8764 y <- w7931 (Exp Baseline)", X8764["s1_wire"] == 7931)
gate("R6 old inbound: #27716/#28180 <- w31064 (tunnel 31051 inner)", X27716["s1_wire"] == X28180["s1_wire"] == 31064)
gate("R6 old inbound: #29009 ranks <- w31128 (tunnel 31137 inner)", X29009R["s1_wire"] == X29009L["s1_wire"] == 31128)
for tid, lr, idx, sinks in (("T_RING", "LR_RING", True, [X8741]), ("T_BASE", "LR_BASE", False, [X8764]),
                            ("T_FHW", "LR_FHW", False, [X27716, X28180]), ("T_EHW", "LR_EHW", False, [X29009R, X29009L])):
    act(op="tunnel", id=tid.lower(), row="R6", loop="new:DLF", body="new:DLF.body", parent="new:DL.body", dir="in",
        **{"as": tid}, indexing=idx)
    act(op="wire", id=tid.lower() + "_out", row="R6", src="new:{0}.value".format(lr), dst="new:{0}.outer".format(tid),
        verb="stagexec tunnel group = one connect (connect_nested_v1 / OpConnectNested_v1 across the DLF border)")
    act(op="wire", id=tid.lower() + "_in", row="R6", src="new:{0}.inner".format(tid), dst=sinks[0],
        verb="(same connect)")
    for s in sinks[1:]:
        act(op="wire", id=tid.lower() + "_br_{0}".format(s["term_uid"]), row="R6", src="new:{0}.inner".format(tid),
            dst=s, verb="stagexec branch = connect_from_wire on the tunnel's inner wire")
O11310 = B(11310, 11316, True, 7911)
gate("R6 #11310 output cluster old sink = #11363 inner (w11374)", O11310["s1_wire"] == 11374)
X11261A, X11261E, O11261 = B(11261, 11270, False, 639), B(11261, 11273, False, 639), B(11261, 11267, True, 639)
act(op="tunnel", id="t_out", row="R6", loop="new:DLF", body="new:DLF.body", parent="new:DL.body", dir="out",
    **{"as": "T_OUT"}, indexing=True, note="auto-indexed output = one plot per bead, the role of #11363")
act(op="wire", id="t_out_in", row="R6", src=O11310, dst="new:T_OUT.inner", verb="(tunnel group connect)")
act(op="wire", id="t_out_out", row="R6", src="new:T_OUT.outer", dst=X11261A, verb="(tunnel group connect)")
wire("new:LR_WLC.value", X11261E, "R6", "r6_wlc_element")
act(op="create", id="r6_lw_force", row="R6", **{"class": "Local"}, diagram="new:DL.body", **{"as": "LW_FORCE"},
    label=L_FORCE, mode="write", terminals=[{"name": "", "is_source": False}],
    verb="op OpCreateLocalRead_v0 Write?=True (MEASURED WRITE, toolkit-capabilities.md:76 S4_b); NO gscript/stagekit "
         "function passes Write?=True (stagekit.create_local_read :676 drives OpCreateLocal_v0)")
wire(O11261, "new:LW_FORCE.value", "R6", "r6_force_write")
# ---- R7 period control -> Max(x,1) -> Wait (ms) in DL's body
WAIT_DONOR = [r["owner_uid"] for r in T if r["term_name"] == "milliseconds to wait" and not r["is_source"]
              and r["owner_class"] == "Function"]
MAX_DONOR = [r["owner_uid"] for r in T if r["term_name"] in ("max(x, y)", "min(x, y)")]
gate("R7 Wait (ms) donor in S1 (a Function with sink 'milliseconds to wait')", bool(WAIT_DONOR), WAIT_DONOR)
print("FACT R7 Max & Min donor in S1 (terminal 'max(x, y)'):", sorted(set(MAX_DONOR)), flush=True)
act(op="create", id="r7_wait", row="R7", **{"class": "Function"}, diagram="new:DL.body", **{"as": "WAIT"},
    donor_uid=WAIT_DONOR[0] if WAIT_DONOR else None, terminals=[{"name": "milliseconds to wait", "is_source": False},
                                                                {"name": "millisecond timer value", "is_source": True}],
    verb="stagekit.copy_in :779 (OpMoveByIndex_v0 duplicate=True, S1 as donor) - precondition work == gscript.MOVE_DST")
act(op="create", id="r7_max", row="R7", **{"class": "Function"}, diagram="new:DL.body", **{"as": "MAX"},
    donor_uid=(MAX_DONOR or [None])[0], verb="MISSING: no Max & Min in S1 to copy_in; no creator")
act(op="create", id="r7_one", row="R7", **{"class": "DigitalNumericConstant"}, diagram="new:DL.body",
    **{"as": "ONE"}, value=1, on="new:MAX.y", verb="OpCreateConstOnTerm_v0 (toolkit-capabilities.md:70, While body node)")
act(op="create", id="r7_ctl", row="R7", **{"class": "ControlTerminal"}, diagram="new:DL.body", **{"as": "CTL_PERIOD"},
    label=L_PERIOD, representation="I32", default=100, on="new:MAX.x",
    verb="MISSING nested create-control (gscript.create_control :2605 top-level Nodes[] only); then "
         "gscript.set_control_label :3433 + gscript.set_default_in_memory :3450")
wire("new:MAX.max(x, y)", "new:WAIT.milliseconds to wait", "R7", "r7_max_wait")
# ---- R8 stop on a local READ of TurnOff
act(op="create", id="r8_lr_turnoff", row="R8", **{"class": "Local"}, diagram="new:DL.body", **{"as": "LR_TURNOFF"},
    label=L_TURNOFF, mode="read", terminals=[{"name": "", "is_source": True}], verb=RD)
act(op="wire", id="r8_stop", row="R8", src="new:LR_TURNOFF.value", dst="new:DL.cond",
    verb="OpStopFromNode_v0 (toolkit-capabilities.md:67: While cond from a node inside its own body)")
gate("R8 TurnOff terminal #24444 is written from w3457 (the #637 stop value)", BYT[24444]["wire_uid"] == 3457)

# ---- leftovers the rows create (facts, not rows)
LEFT = {
    "#11363 (For #1359 output tunnel)": "inner w11374 cut by R3 (#11310 moves), outer w11352 cut by R4 (#11261 moves):"
                                        " both faces unwired after the batch; rows_spec keeps it (not deleted)",
    "#8323 indicator terminal": "stays on 639, w10908 cut by R4 -> unwired indicator (legal)",
    "#8476 Exp Baseline terminal": "stays on 7911, w7931 cut by R3 (#8764 moves) -> unwired control (legal)",
    "tunnels 31051/31137": "outer faces keep w31059/w31166; inner w31064/w31128 cut by R3",
}
os.makedirs(OUTD, exist_ok=True)
plan = {"schema": "stageplan/1", "stage": "disp", "final": False,
        "goal": "PD212(c)/(h)/(i)3 display loop on D1_s1_copy.vi: rows R1-R8 of tools/bench/cards/rows_spec_100.md",
        "base": {"path": GFILE, "md5": md5(GRAPH), "vi_md5": S1MD5,
                 "owners_from": "tools/bench/sim/l2a1/graph_k_80_owners.json (D1_k; S1 carries no owners map)"},
        "context": {"s1_key": "D1_s1_copy", "output": "claudeDev\\D1_s1_disp_<ts>.vi"},
        "symbols": {"new:DL.body": "body diagram of R1's While", "new:DLF.body": "body of R2's For",
                    "new:DL.cond": "R1's conditional terminal", "new:<LOCAL>.value": "a Local's one terminal"},
        "actions": A, "leftovers": LEFT,
        "not_executable_now": ["stagexec.compile_plan refuses op 'create' (tools/stagexec.py:200-201)",
                               "stagesim/stagexec take int diagrams: move_in dest (stagesim.py:461, stagexec.py:975), "
                               "tunnel loop/body (stagesim.py:643), create diagram (stagesim.py:788); rows need "
                               "new:DL.body / new:DLF.body"]}
json.dump(plan, open(PLAN, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
gate("P rows R1..R8 all present", sorted({a["row"] for a in A}) == ["R1", "R2", "R3", "R4", "R5", "R6", "R7", "R8"],
     sorted({a["row"] for a in A}))
print("FACT plan actions", len(A), "by op", {o: sum(1 for a in A if a["op"] == o) for o in {a["op"] for a in A}})
print("FACT stagexec compile:", end=" ")
try:
    import stagexec
    stagexec.compile_plan(plan)
    print("compiled")
except Exception as e:  # noqa: BLE001
    print("REFUSED", type(e).__name__, str(e)[:200])

REQ = [{"kind": "op", "name": n} for n in (
    "OpWhileLoopIn_v0", "OpForLoopIn_v0", "OpMoveIn_v0", "OpMoveByIndex_v0", "OpConnectNested_v1",
    "OpConnectFromWire_v0", "OpCreateLocalRead_v0", "OpStopFromNode_v0", "OpCreateConstOnTerm_v0", "OpLabelSet_v0",
    "OpCreateIndicatorNested_v0", "OpCreateControlNested_v0", "OpVisibleSet_v0",
    "OpConstValueB_v0")]      # PD212(h)3: the stage pre-run READS #25261 (BooleanConstant) as a gate - no reader
REQ += [{"kind": "verb", "name": n} for n in (
    "gscript.loop_in", "stagekit.move_in", "stagekit.copy_in", "stagekit.connect_from_wire",
    "gscript.set_control_label", "gscript.set_default_in_memory", "stagekit.create_local_write",
    "gscript.create_indicator_nested", "gscript.create_control_nested", "gscript.set_visible",
    "stagexec.exec_create")]
REQ += [{"kind": "verb", "name": "call_donor", "where": "tools/bench/diag_c62_s3b_build.py"},
        {"kind": "verb", "name": "connect_nested_v1", "where": "tools/recipes/build_opconnectnested_v1.py"}]
REQ += [{"kind": "terminal", "name": n, "where": "D1_s1_copy"} for n in (
    L_TURNOFF, L_BASE, L_FHW, L_EHW, L_FORCE, "output cluster", "appended array", "element", "array", "subarray",
    "index (row)", "x-y", "y", "x", "second subarray", "index", "forward coefficients", "half-width",
    "FIR Coefficients", "X", "Filtered X", "right rank", "left rank", "milliseconds to wait")]
REQ += [{"kind": "file", "name": "tools/bench/sim/disp/stageplan_disp.json"},
        {"kind": "file", "name": VI}]
card = {"schema": "task/1", "id": "disp-stage", "kind": "build",
        "goal": "PD212 display-loop stage on D1_s1_copy.vi from tools/bench/sim/disp/stageplan_disp.json (rows R1-R8)",
        "why": "card 100-1 step (a): the requires list of the stage; executed only after (b) missing verbs + (c) sim",
        "inputs": [{"path": "tools/bench/sim/disp/stageplan_disp.json", "md5": md5(PLAN)},
                   {"path": VI, "md5": S1MD5}],
        "requires": REQ,
        "pass": ["computation_diff 0 other than the added objects", "ExecState 1 once at the end",
                 "saved claudeDev\\D1_s1_disp_<ts>.vi by script"],
        "outputs": ["C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\D1_s1_disp_*.vi"],
        "flags": {"labview": "build", "gui": False, "hardware": "none", "run_vi": False,
                  "write": ["tools/bench/sim/disp/**", "tools/bench/stage_disp*"], "status_edit": False,
                  "git_commit": False, "peers": ["hypothesis", "priorart"]},
        "budget": {"failures": 2, "minutes": 60},
        "rules": ["rows only from tools/bench/sim/disp/stageplan_disp.json", "RETRY_CAP applies"],
        "advances": ["M8", "M3", "R1", "R3"]}
json.dump(card, open(CARD, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
gate("H3 D1_s1_copy md5 end", md5(VI) == S1MD5)
gate("H4 LabVIEW not running at end", lv_count() == 0)
print(protocol.result_line(protocol.make_result(npass, nfail, first_fail, artefacts=[
    {"path": os.path.relpath(p, ROOT), "md5": md5(p)} for p in (PLAN, CARD)])), flush=True)
