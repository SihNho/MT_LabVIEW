# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-a1-1.md
# ---
r"""selftest_c160_delwire - card 160-a1-1 (docs/d1/ring-p5b.md PD390(a)(b)), OFFLINE: no LabVIEW, no COM.
Under test (called, not copied): stagesim.termless_wire / op_delete_wire (new branch), stagexec.Executor.execute 'delete_wire' (new branch)
-> LVBackend.delete_wire -> Stage.delete_wire (stagekit.py:687, the uid path; a stub Stage records the call), SimBackend.delete_wire (dry),
stagexec.compile_plan; comparison by stagekit.wire_end_pairs / sim_census_snapshot and vigraph.dedupe_rows.
Data: tools/bench/graph_ring_p5s02a_20261010_032547.json (read of 94ffff94, 7ac24924), loaded as selftest_c159_cen2_ends.py does.
Pre-edit tools: selftest_c160_delwire_stagesim_eb99c6ba.txt / _stagexec_7a712ccb.txt (kept by diag_c160_a1_1_probe.py), imported from %TEMP%.
PREDICTION: P0 pins; T1 w10394 (Wire, 0 rows) deleted by the simulator (effect termless_wire_object), terminal rows identical, end pairs
identical, census differs by exactly {10394: Wire}; compile_plan -> one 'delete_wire' op; executor -> LVBackend -> stub Stage.delete_wire(10394,
'stagexec') once; dry SimBackend removes the object; the pre-edit tools refuse it ("not in the current graph" / ExecStop).
T2 absent uid refused by both (same message as pre-edit); T3 non-Wire uid (SubVI 26582) refused by both, termless_wire False;
T4 Wire 32594 (2 rows) new == pre-edit (effect + state; executor call); T5 second delete of w10394 in the same plan refused (sim + executor),
w10394 still in the base list. V0/V1 VI pins unchanged; tool pins (stagekit, stage_prerun, addrcheck, vigraph) unchanged. Card 160-b1-1 re-pinned stagekit ac3a8f57 -> 1441bb4c (six mapping fns added). 160-e5-1 re-pinned 1441bb4c -> 0b5bb678.
Card 160-a2-1 (PD391(b)): + stagesim.sourceless_wire (a Wire with NO SOURCE row). Pre-edit side = selftest_c160_delwire_stagesim_a3261b56.txt /
_stagexec_c4a6e0b6.txt (kept by diag_c160_a2_1_baseline.py). TA delete w10394, w24264, w24300 in that order (one plan): all three Wire objects gone,
t24139 / t24235 kept with wire 0, every other row and state key unchanged, end pairs lose ONLY the two (None, sink, frame) stub pairs
(stagekit.wire_end_pairs keys a sink-only wire that way), census diff == the three wires; the executor
sends the uid call for each (24264 / 24300 by the terminal path, one live wire carrying exactly the sink); dry SimBackend unwires t24139 and drops
w24264. TA2 a second delete of w24264 is refused (sim + executor). TB w24285 (source-only stub) and w32594 (source + sink) take the old path, effect
+ state + executor call == the a3261b56 / c4a6e0b6 tools, sourceless_wire False. TC the pre-edit simulator left w24264's Wire object in objs (the
termless branch would then accept a second delete) - recorded as the fact this branch fixes."""
import copy, hashlib, importlib.util, json, os, shutil, sys, tempfile  # noqa: E401

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import stagekit as K  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
B = "tools/bench/"
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
jl = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))              # noqa: E731
dump = lambda x: json.dumps(x, sort_keys=True, default=str)                          # noqa: E731


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


GP = B + "graph_ring_p5s02a_20261010_032547.json"
PINS = {GP: "7ac24924", B + "selftest_c160_delwire_stagesim_eb99c6ba.txt": "eb99c6ba", B + "selftest_c160_delwire_stagexec_7a712ccb.txt": "7a712ccb",
        "tools/stagekit.py": "9b8f82c1", "tools/stage_prerun.py": "7605116f", "tools/addrcheck.py": "207beb0d", "tools/vigraph.py": "a7eb58c7",
        B + "selftest_c160_delwire_stagesim_a3261b56.txt": "a3261b56", B + "selftest_c160_delwire_stagexec_c4a6e0b6.txt": "c4a6e0b6"}
got = dict((p, md5(p)[:8]) for p in PINS)
gate("P0 pins (graph, pre-edit stagesim/stagexec copies, stagekit, stage_prerun, addrcheck, vigraph)", got == PINS, got)
CD = os.path.join(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev", "D1_ring_")   # read as bytes only
VIS = {"p5s02a_20261010_023239": "94ffff94", "p4s09_20261009_060515": "eb1d0f31", "p5s01a_20261009_101219": "2482fe7b", "p5s01_20261009_124542": "7f2582ae"}
vi_md5 = lambda: dict((k, md5(CD + k + ".vi")[:8]) for k in VIS)                     # noqa: E731
V0 = vi_md5()
gate("V0 claudeDev VI pins before (94ffff94, s09, P5-1a, P5-1)", V0 == VIS, V0)

tmp = tempfile.mkdtemp(prefix="c160_a1_1_")


def load_pre(name, txt):
    shutil.copy(os.path.join(HERE, txt), os.path.join(tmp, name + "_pre.py"))
    spec = importlib.util.spec_from_file_location(name + "_pre", os.path.join(tmp, name + "_pre.py"))
    m = importlib.util.module_from_spec(spec)
    m.__file__ = os.path.join(ROOT, "tools", name + ".py")      # its data paths (bench/memory_model.json, ...) resolve as the real tool's
    spec.loader.exec_module(m)
    return m


PS = load_pre("stagesim", "selftest_c160_delwire_stagesim_eb99c6ba.txt")
PX = load_pre("stagexec", "selftest_c160_delwire_stagexec_7a712ccb.txt")
PX.SS = PS                                              # the pre-edit executor on the pre-edit simulator
PS2 = load_pre("stagesim", "selftest_c160_delwire_stagesim_a3261b56.txt")      # card 160-a2-1: the tools before PD391(b)
PX2 = load_pre("stagexec", "selftest_c160_delwire_stagexec_c4a6e0b6.txt")
PX2.SS = PS2
GR = jl(GP)
BASE = SS.base_state(GR)
REAL = K.pure("vigraph").dedupe_rows(GR["terminals"])[0]
BT = dict((r["term_uid"], r["owner_class"]) for r in REAL)
BF = set(r.get("frame_diagram") or 0 for r in REAL) | set(int(k) for k in GR.get("owners") or {})
pairs = lambda st: K.wire_end_pairs(st["terminals"], BT, BF)                          # noqa: E731
census = lambda st: dict(K.sim_census_snapshot(st))                                  # noqa: E731


MP = {}


def sim(mod, st, w):
    """(effect or None, error text or None, state after) - one delete_wire action on a copy of `st`."""
    s = copy.deepcopy(st)
    a = {"op": "delete_wire", "wire_uid": w}
    try:
        if mod not in MP:
            MP[mod] = mod.model_for("delete_wire", mod.load_models())[0]
        return mod.op_delete_wire(s, a, MP[mod], None, {})[0], None, s
    except mod.SimError as e:
        return None, str(e), s


class StubStage(object):
    """Records the uid-path call LVBackend.delete_wire makes on its stagekit Stage (no LabVIEW)."""
    def __init__(self):
        self.calls = []

    def delete_wire(self, wire_uid, tag=""):
        self.calls.append((int(wire_uid), tag))
        return {"err": None, "s": 0.0}

    def junk_purge(self, tag):
        return {}


def run_exec(mod, prev, w, be=None):
    """(result or None, ExecStop text or None, stub calls) - Executor.execute of one compiled delete_wire op."""
    plan = {"actions": [{"op": "delete_wire", "wire_uid": w}]}
    ops = mod.compile_plan(plan, owners={})
    stub = StubStage()
    if be is None:
        be = object.__new__(mod.LVBackend)
        be.s = stub
    ex = object.__new__(mod.Executor)
    ex.plan, ex.be, ex.bind, ex.allow = plan, be, {"term": {}, "obj": {}, "diag": {}}, set()
    try:
        return ex.execute(ops[0], prev, prev, REAL), None, stub.calls, ops
    except mod.ExecStop as e:
        return None, str(e), stub.calls, ops


# T1 -----------------------------------------------------------------------------------------------------------------------
W1 = 10394
o1 = [o for o in BASE["objs"] if int(o["uid"]) == W1]
gate("T1a w10394 in the base objects as Wire with 0 terminal rows; termless_wire True", len(o1) == 1 and o1[0]["class"] == "Wire"
     and not SS.wire_rows(BASE, W1) and SS.termless_wire(BASE, W1), o1)
eff, err, S1 = sim(SS, BASE, W1)
print("FACT T1 sim effect {0} err {1}".format(eff, err), flush=True)
CB, C1 = census(BASE), census(S1)
dc = dict((k, v) for k, v in CB.items() if C1.get(k) != v)
PB, P1 = pairs(BASE), pairs(S1)
gate("T1b simulator deletes it: rows identical {0}, end pairs identical {1}, census diff {2} (want {{10394: 'Wire'}})".format(
    dump(S1["terminals"]) == dump(BASE["terminals"]), P1 == PB, dc),
     err is None and eff.get("termless_wire_object") and eff.get("n_terminals") == 0 and dump(S1["terminals"]) == dump(BASE["terminals"])
     and P1 == PB and dc == {W1: "Wire"} and len(C1) == len(CB) - 1
     and dump(dict((k, v) for k, v in S1.items() if k != "objs")) == dump(dict((k, v) for k, v in BASE.items() if k != "objs")))
res, xerr, calls, ops = run_exec(SX, BASE, W1)
print("FACT T1 compile {0}; executor result {1} err {2}; Stage.delete_wire calls {3}".format(ops, res, xerr, calls), flush=True)
gate("T1c compile_plan -> one delete_wire op; executor -> LVBackend.delete_wire -> Stage.delete_wire(10394, 'stagexec') once (uid path)",
     ops == [{"kind": "delete_wire", "acts": [1]}] and xerr is None and calls == [(W1, "stagexec")] and res == {"err": None, "s": 0.0},
     (ops, calls, res, xerr))
sbe = SX.SimBackend({"actions": [{"op": "delete_wire", "wire_uid": W1}]}, BASE, SS.load_models())
dres, derr, _c, _o = run_exec(SX, BASE, W1, be=sbe)
gate("T1d dry SimBackend applies it: object gone, rows unchanged ({0})".format(derr), derr is None and sbe.calls == ["delete_wire"]
     and not any(int(o["uid"]) == W1 for o in sbe.st["objs"]) and dump(sbe.st["terminals"]) == dump(BASE["terminals"]), sbe.calls)
peff, perr, _s = sim(PS, BASE, W1)
pres, pxerr, pcalls, _o = run_exec(PX, BASE, W1)
print("FACT T1 pre-edit: sim err {0!r}; executor err {1!r}".format(perr, pxerr), flush=True)
gate("T1e pre-edit tools refuse it (the c159 block): sim 'not in the current graph', executor ExecStop, no Stage call",
     peff is None and "not in the current graph" in (perr or "") and pxerr is not None and not pcalls, (perr, pxerr))

# T2 -----------------------------------------------------------------------------------------------------------------------
W2 = 99999999
e2, r2, _s = sim(SS, BASE, W2)
pe2, pr2, _s = sim(PS, BASE, W2)
x2, xe2, c2, _o = run_exec(SX, BASE, W2)
px2, pxe2, _c, _o = run_exec(PX, BASE, W2)
print("FACT T2 absent uid {0}: sim {1!r} / pre {2!r}; executor {3!r} / pre {4!r}".format(W2, r2, pr2, xe2, pxe2), flush=True)
gate("T2 absent uid refused, same as pre-edit (sim + executor), no Stage call", e2 is None and r2 == pr2 and r2 and xe2 == pxe2 and xe2
     and not c2 and not SS.termless_wire(BASE, W2))

# T3 -----------------------------------------------------------------------------------------------------------------------
W3 = 26582
cls3 = SS.obj_class(BASE, W3)
e3, r3, _s = sim(SS, BASE, W3)
pe3, pr3, _s = sim(PS, BASE, W3)
x3, xe3, c3, _o = run_exec(SX, BASE, W3)
px3, pxe3, _c, _o = run_exec(PX, BASE, W3)
print("FACT T3 non-Wire uid {0} ({1}, owns {2} rows, carries {3}): sim {4!r} / pre {5!r}; executor {6!r} / pre {7!r}".format(
    W3, cls3, len(SS.node_rows(BASE, W3)), len(SS.wire_rows(BASE, W3)), r3, pr3, xe3, pxe3), flush=True)
gate("T3 non-Wire uid refused, same as pre-edit (sim + executor), termless_wire False, no Stage call", cls3 == "SubVI" and e3 is None
     and r3 == pr3 and r3 and xe3 == pxe3 and xe3 and not c3 and not SS.termless_wire(BASE, W3))

# T4 -----------------------------------------------------------------------------------------------------------------------
W4 = 32594
e4, r4, s4 = sim(SS, BASE, W4)
pe4, pr4, ps4 = sim(PS, BASE, W4)
x4, xe4, c4, _o = run_exec(SX, BASE, W4)
px4, pxe4, pc4, _o = run_exec(PX, BASE, W4)
print("FACT T4 Wire {0} ({1} rows): sim effect {2} / pre {3}; executor calls {4} / pre {5}".format(
    W4, len(SS.wire_rows(BASE, W4)), e4, pe4, c4, pc4), flush=True)
gate("T4 Wire with terminal rows keeps the old path: effect + state == pre-edit, executor call == pre-edit, termless_wire False",
     r4 is None and e4 == pe4 and "termless_wire_object" not in e4 and dump(s4) == dump(ps4) and xe4 is None and c4 == pc4 == [(W4, "stagexec")]
     and x4 == px4 and not SS.termless_wire(BASE, W4), (e4, c4))

# T5 -----------------------------------------------------------------------------------------------------------------------
e5, r5, s5 = sim(SS, S1, W1)                       # S1 = the state after T1's delete of w10394 (the same plan, a later action)
x5, xe5, c5, _o = run_exec(SX, S1, W1)
print("FACT T5 second delete of w{0}: sim {1!r}; executor {2!r}; still in base objs {3}".format(
    W1, r5, xe5, any(int(o["uid"]) == W1 for o in BASE["objs"])), flush=True)
gate("T5 already deleted earlier in the plan: branch not taken, refused (sim + executor), not counted, no Stage call",
     e5 is None and "not in the current graph" in (r5 or "") and xe5 and not c5 and not SS.termless_wire(S1, W1)
     and any(int(o["uid"]) == W1 for o in BASE["objs"]))

# TA (card 160-a2-1, PD391(b)) ---------------------------------------------------------------------------------------------
SINKS = dict((w, [r["term_uid"] for r in SS.wire_rows(BASE, w)]) for w in (24264, 24300))   # read from the graph, not typed
print("FACT TA sink rows from the graph: {0}".format(SINKS), flush=True)
TW = (W1, 24264, 24300)
SA, effs, errs, xcalls = BASE, [], [], []
for w in TW:
    xr, xe, xc, _o = run_exec(SX, SA, w)
    xcalls.append((xc, xe))
    e_, r_, SA = sim(SS, SA, w)
    effs.append(e_)
    errs.append(r_)
print("FACT TA sim effects {0} errs {1}; executor calls {2}".format(effs, errs, xcalls), flush=True)
gone = dict((w, any(int(o["uid"]) == w for o in SA["objs"])) for w in TW)
U = set(t for ts_ in SINKS.values() for t in ts_)
ra = dict((r["term_uid"], r) for r in SA["terminals"])
keep = lambda st: [r for r in st["terminals"] if r["term_uid"] not in U]                 # noqa: E731
CA = census(SA)
dca = dict((k, v) for k, v in CB.items() if CA.get(k) != v)
gate("TA1 sim deletes w10394, w24264, w24300: no error, the three Wire objects gone, census diff == the three wires ({0})".format(dca),
     errs == [None] * 3 and not any(gone.values()) and dca == dict((w, "Wire") for w in TW) and len(CA) == len(CB) - 3
     and SINKS == {24264: [24139], 24300: [24235]} and all(e_.get("sourceless_wire_object") for e_ in effs[1:])
     and all(e_.get("n_terminals") == 1 and e_.get("auto_removed_tunnels") == [] for e_ in effs[1:]), (gone, effs))
PA = pairs(SA)
# stagekit.wire_end_pairs keys a sink-only wire as (None, sink, frame) (stagekit.py:2102-2103): deleting a sourceless wire removes exactly
# its own (None, sink, frame) pairs; WANT is read from the base pair table, not typed
WANT = dict((k, v) for k, v in PB[0].items() if k[0] is None and k[1] in U)
gone_p, new_p = dict(PB[0] - PA[0]), dict(PA[0] - PB[0])
ta2 = {"sinks_wire0": all(t in ra and ra[t]["wire_uid"] == 0 for t in U), "n_rows": len(SA["terminals"]) == len(BASE["terminals"]),
       "other_rows": dump(keep(SA)) == dump(keep(BASE)), "pairs_removed_eq_stub_pairs": gone_p == WANT and len(WANT) == 2,
       "pairs_added": new_p, "stubs_same": PA[1] == PB[1],
       "other_keys": [k for k in set(SA) | set(BASE) if k not in ("objs", "terminals") and dump(SA.get(k)) != dump(BASE.get(k))]}
print("FACT TA2 checks {0}; end pairs removed {1}".format(ta2, gone_p), flush=True)
gate("TA2 t24139 / t24235 kept with wire 0; every other row and state key unchanged; end pairs lose ONLY the two (None, sink, frame) stub pairs",
     ta2["sinks_wire0"] and ta2["n_rows"] and ta2["other_rows"] and ta2["pairs_removed_eq_stub_pairs"] and not new_p and ta2["stubs_same"]
     and not ta2["other_keys"], [(t, ra.get(t, {}).get("wire_uid")) for t in sorted(U)])
gate("TA3 executor: one uid call each, in order - Stage.delete_wire(10394), (24264), (24300) - no ExecStop",
     [c for c, _e in xcalls] == [[(w, "stagexec")] for w in TW] and all(e_ is None for _c, e_ in xcalls), xcalls)
sbe2 = SX.SimBackend({"actions": [{"op": "delete_wire", "wire_uid": 24264}]}, BASE, SS.load_models())
dres2, derr2, _c, _o = run_exec(SX, BASE, 24264, be=sbe2)
gate("TA4 dry SimBackend: w24264 object gone, t24139 wire 0, other rows unchanged ({0})".format(derr2), derr2 is None
     and not any(int(o["uid"]) == 24264 for o in sbe2.st["objs"]) and dict((r["term_uid"], r["wire_uid"]) for r in sbe2.st["terminals"])
     .get(24139) == 0 and dump([r for r in sbe2.st["terminals"] if r["term_uid"] != 24139]) == dump(
         [r for r in BASE["terminals"] if r["term_uid"] != 24139]), sbe2.calls)
e6, r6, _s = sim(SS, SA, 24264)
x6, xe6, c6, _o = run_exec(SX, SA, 24264)
print("FACT TA5 second delete of w24264: sim {0!r}; executor {1!r}; calls {2}".format(r6, xe6, c6), flush=True)
gate("TA5 a second delete of w24264 in the same plan is refused (sim + executor), not counted, no Stage call",
     e6 is None and "not in the current graph" in (r6 or "") and xe6 and not c6 and not SS.sourceless_wire(SA, 24264))

# TB -----------------------------------------------------------------------------------------------------------------------
for wb in (24285, W4):
    eb, rb, sb = sim(SS, BASE, wb)
    peb, prb, psb = sim(PS2, BASE, wb)
    xb, xeb, cb, _o = run_exec(SX, BASE, wb)
    pxb, pxeb, pcb, _o = run_exec(PX2, BASE, wb)
    srcs = [(r["term_uid"], r["is_source"]) for r in SS.wire_rows(BASE, wb)]
    print("FACT TB w{0} rows {1}: sim {2} / pre {3}; executor {4} / pre {5}".format(wb, srcs, eb, peb, cb, pcb), flush=True)
    gate("TB w{0} (a source row: {1}) takes the OLD path: effect + state == a3261b56, executor call == c4a6e0b6, sourceless_wire False".format(
        wb, srcs), rb is None and prb is None and eb == peb and "sourceless_wire_object" not in eb and dump(sb) == dump(psb)
         and xeb is None and pxeb is None and cb == pcb == [(wb, "stagexec")] and not SS.sourceless_wire(BASE, wb)
         and any(s for _t, s in srcs), (eb, cb))

# TC -----------------------------------------------------------------------------------------------------------------------
pe7, pr7, ps7 = sim(PS2, BASE, 24264)
left = any(int(o["uid"]) == 24264 for o in ps7["objs"])
print("FACT TC pre-edit (a3261b56) delete of w24264: effect {0}; Wire object left in objs {1}; pre-edit termless_wire after {2}".format(
    pe7, left, PS2.termless_wire(ps7, 24264)), flush=True)
gate("TC the pre-edit simulator unwired t24139 but LEFT w24264 in objs (termless afterwards) - the gap this branch closes",
     pr7 is None and left and PS2.termless_wire(ps7, 24264))

shutil.rmtree(tmp, ignore_errors=True)
gate("V1 claudeDev VI pins after == before; tool pins after == P0; temp removed", vi_md5() == V0
     and dict((p, md5(p)[:8]) for p in PINS) == PINS and not os.path.exists(tmp), vi_md5())
print("FACT md5 stagesim {0} stagexec {1} stagekit {2} stage_prerun {3}".format(*[md5("tools/" + m) for m in (
    "stagesim.py", "stagexec.py", "stagekit.py", "stage_prerun.py")]), flush=True)
print("=== TOTALS {0} pass / {1} fail".format(G["pass"], G["fail"]), flush=True)
print("RESULT {0}/{1}".format(G["pass"], G["fail"]), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
