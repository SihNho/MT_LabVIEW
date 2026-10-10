# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-a2-1.md
# ---
r"""selftest_c160_regface - card 160-a2-1 (docs/d1/ring-p5b.md PD391(a)(c)(d)), OFFLINE: no LabVIEW, no COM.
Under test (called, not copied): stagexec.compile_plan (a BASE register's inner face as a tunnel group's outside end), stagexec.base_register_end /
plan_base_state / plan_base_docs (new), stagesim.simulate + its route check (stagesim.route_report -> stagexec.dry_run), stagesim.sourceless_wire.
Data: tools/bench/graph_ring_p5s02a_20261010_032547.json (read of 94ffff94, 7ac24924); plan_ring_p5s02b_in.json (56bfddd3); plan_ring_p5s01a/b.json;
the BEFORE side = tools/bench/diag_c160_a2_1_baseline.json (25b320c4, written by diag_c160_a2_1_baseline.py on stagesim a3261b56 / stagexec c4a6e0b6).
PREDICTION: P0 pins. R1 the temp plan tools/bench/diag_c160_a2_1_plan_tmp.json = plan_ring_p5s02b_in.json + `delete_wire <w of t24139>` before
group t_go and `delete_wire <w of t24235>` before group t_ho (wire uids read from the graph rows of the w_gr / w_hr sink ends) simulates final with the
route check PASS, 0 UNROUTABLE; groups t_go / t_ho compile to connect_term_uid register_end_case_border and route connect_term_uid; t_gi / t_hi
route cfw. R2 plan_ring_p5s01a / p5s01b compile to op lists IDENTICAL to the baseline (md5 5f95830f / b8b59791). R3 every op of plan_ring_p5s02b_in
other than the t_go / t_ho groups compiles as in the baseline; base_register_end is '' for the non-register outside ends (t_in3 LoopTunnel inner,
p5s01a t_el BuildArray). R4 the LSR-face groups t_gi / t_hi (wired source stubs w24285 / w24312) still compile to `tunnel` as in the baseline
(MERGE rows stay cfw); an UNWIRED copy of the same LSR face would give 'srL'. V0/V1 VI pins and tool pins unchanged."""
import copy, hashlib, json, os, shutil, sys, tempfile  # noqa: E401

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402
import stage_shared as SH  # noqa: E402  insert_stub_deletes (card 162-a2-3)

G = {"pass": 0, "fail": 0, "first": None}
B = "tools/bench/"
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
jl = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))              # noqa: E731
dump = lambda x: json.dumps(x, sort_keys=True, default=str)                          # noqa: E731
omd5 = lambda ops: hashlib.md5(dump(ops).encode()).hexdigest()                       # noqa: E731 - as diag_c160_a2_1_baseline.py


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


GP, PIN_IN, BL = B + "graph_ring_p5s02a_20261010_032547.json", B + "plan_ring_p5s02b_in.json", B + "diag_c160_a2_1_baseline.json"
PINS = {GP: "7ac24924", PIN_IN: "56bfddd3", B + "plan_ring_p5s01a.json": "ed62e8d6", B + "plan_ring_p5s01b.json": "75a77a00", BL: "25b320c4",
        "tools/stagekit.py": "9b8f82c1", "tools/stage_prerun.py": "7605116f", "tools/addrcheck.py": "207beb0d", "tools/vigraph.py": "a7eb58c7"}
got = dict((p, md5(p)[:8]) for p in PINS)
gate("P0 pins (graph, plans, baseline, stagekit, stage_prerun, addrcheck, vigraph)", got == PINS, got)
CD = os.path.join(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev", "D1_ring_")   # read as bytes only
VIS = {"p5s02a_20261010_023239": "94ffff94", "p4s09_20261009_060515": "eb1d0f31", "p5s01a_20261009_101219": "2482fe7b", "p5s01_20261009_124542": "7f2582ae"}
vi_md5 = lambda: dict((k, md5(CD + k + ".vi")[:8]) for k in VIS)                     # noqa: E731
V0 = vi_md5()
gate("V0 claudeDev VI pins before (94ffff94, s09, P5-1a, P5-1)", V0 == VIS, V0)
BASE_LINE = jl(BL)["plans"]


def groups(plan, ops):
    """{tunnel action id: op} for every tunnel-group op (kind tunnel / connect_term_uid with in_act)."""
    return dict((plan["actions"][o["acts"][0] - 1].get("id"), o) for o in ops if "in_act" in o)


# R1 -----------------------------------------------------------------------------------------------------------------------
PIN = jl(PIN_IN)
GR = jl(GP)
BASE = SS.base_state(GR)
A = PIN["actions"]
ids = [a.get("id") for a in A]
sink = lambda wid: next(a["dst"] for a in A if a.get("id") == wid)                                     # noqa: E731
wire_of = lambda e: next(r["wire_uid"] for r in BASE["terminals"] if r["term_uid"] == e["term_uid"])  # noqa: E731
DW = {"t_go": wire_of(sink("w_gr")), "t_ho": wire_of(sink("w_hr"))}
print("FACT R1 stub wires read from the graph: t_go group sink {0} -> w{1}; t_ho group sink {2} -> w{3}; sourceless {4}".format(
    sink("w_gr")["term_uid"], DW["t_go"], sink("w_hr")["term_uid"], DW["t_ho"], [SS.sourceless_wire(BASE, w) for w in DW.values()]), flush=True)
TP = copy.deepcopy(PIN)
TP["stage"] = "diag_c160_a2_1_tmp"
TP["goal"] = "card 160-a2-1 R1 temp plan (NOT a stage plan): plan_ring_p5s02b_in.json + the two PD391(a) stub deletes"
acts = SH.insert_stub_deletes(TP["actions"], DW, "PD391(a): sink-only stub on the base register inner face; deleted before the group's connect")
TP["actions"] = acts                                                                                   # card 162-a2-3: tools/stage_shared.py
TPP = B + "diag_c160_a2_1_plan_tmp.json"
with open(os.path.join(ROOT, TPP), "w", encoding="utf-8") as f:
    json.dump(TP, f, indent=1)
print("FACT R1 temp plan {0} md5 {1}: {2} actions (input {3})".format(TPP, md5(TPP), len(acts), len(A)), flush=True)
tops = SX.compile_plan(TP)
tg = groups(TP, tops)
print("FACT R1 compiled groups {0}".format(dict((k, (o["kind"], o.get("variant"))) for k, o in tg.items())), flush=True)
gate("R1a compile: t_go / t_ho -> connect_term_uid register_end_case_border; t_gi / t_hi -> tunnel",
     all((tg[k]["kind"], tg[k].get("variant")) == ("connect_term_uid", "register_end_case_border") for k in ("t_go", "t_ho"))
     and all(tg[k]["kind"] == "tunnel" for k in ("t_gi", "t_hi")), dict((k, (o["kind"], o.get("variant"))) for k, o in tg.items()))
tmp = tempfile.mkdtemp(prefix="c160_a2_1_")
LOG = []
SB = SS.simulate(os.path.join(ROOT, TPP), os.path.join(ROOT, GP), out_root=tmp, plan_out_dir=tmp, log=LOG.append, route_check=True)
rc = SB.get("route_check") or {}
rows = rc.get("rows") or []
for x in rows:
    print("FACT R1 ROUTE k={0} {1} {2}: route {3}{4}".format(x.get("k"), x.get("op"), x.get("ids"), x.get("route"),
                                                             "  UNROUTABLE " + str(x["unroutable"])[:300] if x.get("unroutable") else ""), flush=True)
for m in [m for m in LOG if "REFUSED" in str(m) or "UNROUTABLE" in str(m)]:
    print("FACT R1 sim log: {0}".format(str(m)[:600]), flush=True)
byid = dict((tuple(x.get("ids") or ()), x) for x in rows)
rt = dict((k, next((x for i_, x in byid.items() if k in i_), None)) for k in ("t_go", "t_ho", "t_gi", "t_hi", "dw_go", "dw_ho"))
nun = sum(1 for x in rows if x.get("unroutable"))
print("FACT R1 simulate final {0}, failed {1}, route check {2}, first_fail {3}".format(SB.get("final"), dump(SB.get("failed"))[:300],
                                                                                     rc.get("status"), str(rc.get("first_fail"))[:300]), flush=True)
gate("R1b routes 4/7 (groups t_go / t_ho) ROUTABLE as connect_term_uid; 0 UNROUTABLE; route check PASS; plan final", rc.get("status") == "PASS"
     and nun == 0 and SB.get("final") and all(rt[k] and rt[k].get("route") == "connect_term_uid" for k in ("t_go", "t_ho")),
     dict((k, (v or {}).get("route")) for k, v in rt.items()))
gate("R1c the LSR MERGE groups t_gi / t_hi still route cfw; the two stub deletes route delete_wire",
     all(rt[k] and rt[k].get("route") == "cfw" for k in ("t_gi", "t_hi")) and all(rt[k] and rt[k].get("route") == "delete_wire"
                                                                               for k in ("dw_go", "dw_ho")),
     dict((k, (v or {}).get("route")) for k, v in rt.items()))
shutil.rmtree(tmp, ignore_errors=True)

# R2 -----------------------------------------------------------------------------------------------------------------------
for name in ("plan_ring_p5s01a.json", "plan_ring_p5s01b.json"):
    ops = SX.compile_plan(jl(B + name))
    print("FACT R2 {0}: new ops md5 {1}, baseline {2}".format(name, omd5(ops), BASE_LINE[name]["ops_md5"]), flush=True)
    gate("R2 {0} compiles to the op list IDENTICAL to the baseline".format(name), dump(ops) == dump(BASE_LINE[name]["ops"])
         and omd5(ops) == BASE_LINE[name]["ops_md5"], omd5(ops))

# R3 / R4 ------------------------------------------------------------------------------------------------------------------
nops = SX.compile_plan(PIN)
bops = BASE_LINE["plan_ring_p5s02b_in.json"]["ops"]
ng, bg = groups(PIN, nops), groups(PIN, bops)
chg = [k for k in bg if dump(ng.get(k)) != dump(bg[k])]
rest_n = [o for o in nops if o not in [ng["t_go"], ng["t_ho"]]]
rest_b = [o for o in bops if o not in [bg["t_go"], bg["t_ho"]]]
print("FACT R3 plan_ring_p5s02b_in: changed groups {0}; new {1} / baseline {2} ops".format(chg, len(nops), len(bops)), flush=True)
gate("R3a every op of plan_ring_p5s02b_in other than the t_go / t_ho groups compiles as in the baseline", sorted(chg) == ["t_go", "t_ho"]
     and dump(rest_n) == dump(rest_b), chg)
NR = [x for p in BASE_LINE.values() for x in p["not_register_face"] if x["row"] and "error" not in x["row"]]
st_of = {}
for name in BASE_LINE:
    P_ = jl(B + name)
    st_of[name] = SX.plan_base_state(P_)
nrv = [(name, x["tunnel_id"], SX.base_register_end(st_of[name], x["end"], x["side"] == "src")) for name, p in BASE_LINE.items()
       for x in p["not_register_face"] if x["row"] and "error" not in x["row"]]
print("FACT R3 non-register outside ends -> base_register_end {0}".format(nrv), flush=True)
gate("R3b base_register_end is '' for every non-register plain outside end of the three plans ({0})".format(len(NR)),
     len(nrv) >= 2 and all(v == "" for _n, _t, v in nrv), nrv)
gate("R4a LSR-face groups t_gi / t_hi (wired source stubs) still compile to `tunnel`, == baseline", all(
    dump(ng[k]) == dump(bg[k]) and ng[k]["kind"] == "tunnel" for k in ("t_gi", "t_hi")), dict((k, ng[k]["kind"]) for k in ("t_gi", "t_hi")))
lsr = next(a["src"] for a in A if a.get("id") == "w_gl")
s0 = copy.deepcopy(st_of["plan_ring_p5s02b_in.json"])
for r in s0["terminals"]:
    if r["term_uid"] == lsr["term_uid"]:
        r["wire_uid"] = 0
v_w, v_0 = SX.base_register_end(st_of["plan_ring_p5s02b_in.json"], lsr, True), SX.base_register_end(s0, lsr, True)
v_r = SX.base_register_end(st_of["plan_ring_p5s02b_in.json"], sink("w_gr"), False)
print("FACT R4 base_register_end: LSR face {0} wired -> {1!r}; same face unwired -> {2!r}; RSR face {3} -> {4!r}".format(
    lsr["term_uid"], v_w, v_0, sink("w_gr")["term_uid"], v_r), flush=True)
gate("R4b base_register_end: wired LSR source '' (cfw kept), unwired LSR face 'srL', RSR inner sink 'srR'", (v_w, v_0, v_r) == ("", "srL", "srR"))

gate("V1 claudeDev VI pins after == before; tool / plan pins after == P0; temp removed", vi_md5() == V0
     and dict((p, md5(p)[:8]) for p in PINS) == PINS and not os.path.exists(tmp), vi_md5())
print("FACT md5 stagesim {0} stagexec {1} stagekit {2} stage_prerun {3}".format(*[md5("tools/" + m) for m in (
    "stagesim.py", "stagexec.py", "stagekit.py", "stage_prerun.py")]), flush=True)
print("=== TOTALS {0} pass / {1} fail".format(G["pass"], G["fail"]), flush=True)
print("RESULT {0}/{1}".format(G["pass"], G["fail"]), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": TPP, "md5": md5(TPP)}])), flush=True)
sys.exit(1 if G["fail"] else 0)
