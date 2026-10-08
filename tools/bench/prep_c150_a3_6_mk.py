# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a3_6_mk - card 150-a3-6 (RETRY of 150-a3-5) step 1 (OFFLINE). COPY of prep_c150_a3_5_mk.py (b6448a4c) with ONLY:
  (a) THE CAP, ONE LINE: MAXACT = 19 (line 64, was 40 at prep_c150_a3_5_mk.py:57) - action 20 of the remainder, p4_x_n2_order (v18 op 185), wires into frame #29869 of FS #29721
      whose diagram is unmeasured (prep_c150_a3_5_mk.log:53, stagesim.py:1805-1807 PD289(f)); gate CAP checks that id is not in s08;
  (b) gate P: the pre-existing s08 files are exactly 150-a3-5's partial sim tree (s07end/base_provisional.json + _passA/**); they are BYTE-COPIED
      into tools/bench/prep_c150_a3_6_prev_s08.zip (md5 manifest printed) before anything is written; no plan/_in/_pred/_licence/recipe existed;
  (c) BOUNDARY facts: tail ops after the cut, 'of' groups across the cut, tail refs to s08-made symbols, 150-a3-5's pass-A failure read from the copy;
  (d) names: card id 150-a3-6, session table prep_c150_a3_6_session.json. Everything else unchanged. --- original docstring follows ---
prep_c150_a3_5_mk - card 150-a3-5 step 1 (OFFLINE, no LabVIEW, never launched). P4 session 8 of plan v18 (2ea6cafa) MADE at the MEASURED s07
load (PD365(g), PD366(f)): v18 ops 166..cut, the longest prefix with MAIN X10 <= 680, <= 40 actions, no 'of' group split. Made on session 7's
SIMULATED end (plan_ring_p4_s07v18.json 08c2ad4d, finalized last step sim/ring_p4_s07v18/step_30_create.json c2b902b7 - the s07 plan's own
rebased simulation on the real s06 base) and then rebased by stage_prerun --rebase onto the REAL s07 graph graph_ring_p4s07_20261008_224835.json
71935a84 (separate bgrun) - the route s07 took (prep_c150_a1_1_mk.py made on s06's sim end step_25_wire, then prep_c150_a2_5_rebase.log).
COPY of prep_c150_a1_1_mk.py (7a275061) with ONLY:
  (1) START = stage_prerun.x10_start(<adopted s07 file md5 b3f86b32..>) = load_by_vi 589.4 (memory_model b4a6eec6, diag_c150_a3_2_graph.log:24)
      + op0_read_mb 5.9 - the s05/s06 re-cut rule (prep_c146_a1_2_mk.py:52-53, stage_prerun.py:2061-2070); gate X0 checks load == 589.4;
  (2) one more session: s07 symbols -> negative provisional uids of END7 (s07's sim end); s06 symbols -> REAL uids by s06's sim end step_25_wire
      (abe1dd11) + the s06 creation map the s07 rebase used (plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl, prep_c150_a2_5_rebase.log);
      the binding cross-check REB reads the REBASED s07 plan (08c2ad4d) instead of the s06 plan;
  (3) gate P: no pre-existing s08 file (none to byte-copy; the 148 prov copies are not repeated) - s07 files are never written;
  (4) V18E: END7 already carries s06's real names (#2626 'element', RENAMED-OLD of prep_c150_a2_5_rebase.log), so the maker gate is
      "the s08 end difference vs v18 is no larger than the difference inherited at step 0 (V18E-BASE)"; the full V18E-R' runs in the pred
      after the rebase (PD366(c));
  (5) names: session table prep_c150_a3_5_session.json, sim/ring_p4_s08v18, card id / goal strings; WANT adds s07 plan / END7 / graph s07 / mm b4a6eec6.
Existing tools checked: prep_c150_a1_1_mk.py (copied), stage_prerun.x10_start / read_creation_map / x10_model_peak, stagesim.simulate / obj_class,
stagexec.compile_plan / is_ct; no new op, no tool edit.
PREDICTION CONTRACT: M0 input md5 == pins; P no s08 file before; X0 START 595.3; S7 v18 ops 1..165 == s01..s07 ids; E7 END step pin;
  CUT = op 190 if the whole remainder fits (<= 40 actions, MAIN <= 680) else the longest prefix; R s01..s06 symbols -> real uid; C2; SA; TIE;
  SB FINAL provisional; NEG refused; X10s == table, kinds pass; V18E end diff within the inherited base diff; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c150_a3_6_mk.log -- py -u tools/bench/prep_c150_a3_6_mk.py"""
import collections, copy, glob, hashlib, json, os, sys, traceback                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V18, S01, S02, S03, S04, S05, S06, S07 = (os.path.join(B, n) for n in (
    "plan_ring_p4_v18.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02v18.json", "plan_ring_p4_s03v18.json", "plan_ring_p4_s04v18.json",
    "plan_ring_p4_s05v18.json", "plan_ring_p4_s06v18.json", "plan_ring_p4_s07v18.json"))
END3F = os.path.join(SIM, "ring_p4_s03v18", "step_20_create.json")
END4F = os.path.join(SIM, "ring_p4_s04v18", "step_23_wire.json")
END5F = os.path.join(SIM, "ring_p4_s05v18", "step_21_create.json")
END6F = os.path.join(SIM, "ring_p4_s06v18", "step_25_wire.json")
END7F = os.path.join(SIM, "ring_p4_s07v18", "step_30_create.json")
CMAP3 = os.path.join(B, "creation_map", "plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl")
CMAP4 = os.path.join(B, "creation_map", "plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl")
CMAP5 = os.path.join(B, "creation_map", "plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl")
CMAP6 = os.path.join(B, "creation_map", "plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl")
GRAPH7 = os.path.join(B, "graph_ring_p4s07_20261008_224835.json")
MMF = os.path.join(B, "memory_model.json")
S8D = os.path.join(SIM, "ring_p4_s08v18")
D8 = os.path.join(S8D, "s07end")
PROVB = os.path.join(D8, "base_provisional.json")
PAROOT = os.path.join(S8D, "_passA")
DA = os.path.join(PAROOT, "ring_p4_s08v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s08v18a_in.json"), os.path.join(B, "plan_ring_p4_s08v18_in.json"), os.path.join(B, "plan_ring_p4_s08v18.json")
FACTS = os.path.join(B, "prep_c150_a3_6_session.json")
MAIN_SRC_READS = 2                       # main recipe source census_snapshot reads (diag_c147_c3_2_prerun.log:112: R 8 = Executor 6 + 2)
MAXACT = 19                              # card 150-a3-6 CAP (was 40, PD364(c)): stop before action 20 p4_x_n2_order (frame #29869 / FS #29721 unmeasured)
CAPID = "p4_x_n2_order"                  # the first action that must NOT be in s08 (prep_c150_a3_5_mk.log:53)
PREVZIP = os.path.join(B, "prep_c150_a3_6_prev_s08.zip")
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S07: "08c2ad4d2e6dd4bddd4dd5b18326562c", S06: "cfbd9823d3b47be39de94f2125ad6b66",
        S05: "1fc9b486551b3f1fe42f25167375ba30", S04: "f349c39a17330531e688ff1f70ce426e", S03: "da66a0300851133d93881be3c28f2fdc",
        END7F: "c2b902b761ea28ad5ecb4b87d7d95ba9", END6F: "abe1dd1113d181cbaa0dd723979a4f2e", END5F: "ca3661f3e02bcac1749e1edcf0a1f018",
        END4F: "b5ae7f79975b9faca0722bb4dc6e3781", END3F: "5f31db45b1b8c7f66b48cf28d92a1e03", CMAP5: "50d2b2ff208370e90a463230cc76d390",
        GRAPH7: "71935a845efedd8123044aab288cd81c", MMF: "b4a6eec651c348c395b2baa01d7f0f5f"}
S07VI_MD5 = "b3f86b322292a6ec6c67976a589b5b06"                                            # the ADOPTED s07 file = s08's input (150-a3-2)
LOAD7 = 589.4                                                                               # memory_model load_by_vi s07 (diag_c150_a3_2_graph.log:24)
MODEL = SPR.load_memory_model()
SUBVI = {"p4_s1_pickslot": "PS1", "p4_s2_seqcheck": "SQ1"}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:800]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


gate("M0 input md5 == card / pins", all(md5(p) == w for p, w in WANT.items()), dict((os.path.basename(p), md5(p)) for p in WANT))
# (b) card 150-a3-6: the pre-existing s08 files must be exactly 150-a3-5's partial sim tree; byte-copy them into a zip before anything is written
import zipfile                                                                                # noqa: E402
pre8 = sorted(glob.glob(os.path.join(B, "*s08v18*")) + glob.glob(os.path.join(ROOT, "tools", "recipes", "*s08*")))
pre8sim = sorted(rel(os.path.join(dp, n)) for dp, _d, fn in os.walk(S8D) for n in fn)
okset = not pre8 and pre8sim and all(f.startswith(rel(D8) + "/") or f.startswith(rel(PAROOT) + "/") for f in pre8sim) and not os.path.isfile(PREVZIP)
gate("P pre-existing s08 files == 150-a3-5's sim tree only (s07end + _passA: {0} files); no plan/_in/_pred/_licence/recipe; no earlier copy zip".format(len(pre8sim)),
     okset, {"bench_recipes": pre8, "sim": pre8sim, "zip_exists": os.path.isfile(PREVZIP)})
PREVMD5 = dict((f, md5(os.path.join(ROOT, f))) for f in pre8sim)
with zipfile.ZipFile(PREVZIP, "w", zipfile.ZIP_STORED) as zf:
    for f in pre8sim:
        zf.write(os.path.join(ROOT, f), f)
with zipfile.ZipFile(PREVZIP) as zf:
    zback = dict((n, hashlib.md5(zf.read(n)).hexdigest()) for n in zf.namelist())
for f in pre8sim:
    print("FACT PREV-COPY {0} {1}".format(PREVMD5[f], f), flush=True)
gate("PC byte-copy {0} ({1} files) read back == originals".format(rel(PREVZIP), len(zback)), zback == PREVMD5, md5(PREVZIP))
with zipfile.ZipFile(PREVZIP) as zf:
    PREVSUM = json.loads(zf.read(rel(os.path.join(PAROOT, "ring_p4_s08v18a", "summary.json"))).decode("utf-8"))
print("FACT 150-a3-5 pass-A sim (copy): failed {0}".format(json.dumps(PREVSUM.get("failed"))), flush=True)
v18, s01, s02, s03, s04, s05, s06, s07 = J(V18), J(S01), J(S02), J(S03), J(S04), J(S05), J(S06), J(S07)
N7 = len(SX.compile_plan(s07))
LBV = (MODEL.get("load_by_vi") or {}).get(S07VI_MD5) or {}
OP0 = float(MODEL["op0_read_mb"]["value"])
XS = SPR.x10_start(S07VI_MD5, MODEL)
START = XS[0] if XS else None
START_CITE = "MEASURED: stage_prerun.x10_start(b3f86b32..) = {0} (s05 re-cut rule, prep_c146_a1_2_mk.py:52-53; stage_prerun.py:2061-2070)".format(XS and XS[1])
gate("X0 MEASURED start: load_by_vi[b3f86b32] == {0}; x10_start == load + op0_read_mb ({1}) = {2}".format(LOAD7, OP0, START),
     LBV.get("value") == LOAD7 and START is not None and abs(START - round(LOAD7 + OP0, 1)) < 0.05, XS)
print("FACT X10 START {0} = {1}".format(START, START_CITE), flush=True)
gate("E7 s07v18 finalized last step file == {0} (pinned md5); s07 base real (not provisional), rebased".format(rel(END7F)),
     s07["finalized"]["step_files"][-1]["path"] == rel(END7F) and s07["finalized"]["step_files"][-1]["md5"] == WANT[END7F]
     and not (s07.get("base") or {}).get("provisional") and bool(s07["finalized"].get("rebase")), s07["finalized"]["step_files"][-1])
END7, END6, END5, END4, END3 = J(END7F)["state"], J(END6F)["state"], J(END5F)["state"], J(END4F)["state"], J(END3F)["state"]
gate("E7b END7 state sym/neg present", isinstance(END7.get("sym"), dict) and isinstance(END7.get("neg"), int), (END7.get("sym"), END7.get("neg")))
os.makedirs(D8, exist_ok=True)
json.dump(END7, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)          # prep_c146_a1_3_mk.py:105
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END7.get("sym")), "neg", END7.get("neg"), "vi md5", END7.get("md5"), flush=True)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
prev3 = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]]
prev4 = prev3 + [x["id"] for x in s04["actions"]]
prev5 = prev4 + [x["id"] for x in s05["actions"]]
prev6 = prev5 + [x["id"] for x in s06["actions"]]
prev_ids = prev6 + [x["id"] for x in s07["actions"]]
S7N = max(act2op[n] for n in range(1, len(prev_ids) + 1))
gate("S7 v18 ops 1..{0} = s01's {1} + s02's {2} + s03's {3} + s04's {4} + s05's {5} + s06's {6} + s07's {7} ids".format(S7N, len(s01["actions"]), len(s02["actions"]),
     len(s03["actions"]), len(s04["actions"]), len(s05["actions"]), len(s06["actions"]), len(s07["actions"])),
     [ids[n - 1] for k in range(1, S7N + 1) for n in OPS[k - 1]["acts"]] == prev_ids and S7N == 165)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
nact = lambda a, b: sum(len(OPS[k - 1]["acts"]) for k in range(a + 1, b + 1))             # noqa: E731
pk = lambda st, a, b: round(st + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
mk = lambda st, a, b: round(pk(st, a, b) + MAIN_SRC_READS * v("read_mb"), 1)                # noqa: E731  stage_prerun.py:2608-2611
lcut = lambda st: max([b for b in range(S7N + 1, NOP + 1) if mk(st, S7N, b) <= SPR.X10_FAIL_MB and cut_ok(b) and nact(S7N, b) <= MAXACT] or [None], key=lambda x: x or 0)   # noqa: E731
cut = lcut(START)
first_over = next((b for b in range(S7N + 1, NOP + 1) if mk(START, S7N, b) > SPR.X10_FAIL_MB), None)
first_cap = next((b for b in range(S7N + 1, NOP + 1) if nact(S7N, b) > MAXACT), None)
split_skipped = [b for b in range(S7N + 1, (first_over or NOP + 1)) if not cut_ok(b) and (cut is None or b > cut)]
gate("CUT longest prefix from op {0} splitting no 'of' group, <= {1} actions, with MAIN X10 <= {2} at {3}: op {4} (v18 last op {5}; whole remainder fits: {6})".format(
     S7N + 1, MAXACT, SPR.X10_FAIL_MB, START, cut, NOP, cut == NOP),
     cut is not None and cut >= S7N + 1 and cut_ok(cut) and mk(START, S7N, cut) <= SPR.X10_FAIL_MB and nact(S7N, cut) <= MAXACT,
     {"first_over": first_over, "first_over_40_actions": first_cap, "groups_split_at": split_skipped})
SENS = {}
for d in (-5.0, 0.0, 5.0, 13.6):
    st = round(START + d, 1)
    c = lcut(st)
    SENS[str(d)] = {"start": st, "cut": c, "main_peak": c and mk(st, S7N, c), "exec_peak": c and pk(st, S7N, c), "actions": c and nact(S7N, c)}
    print("FACT SENS start {0} ({1:+} MB): cut op {2}, MAIN peak {3}, Executor peak {4}, actions {5}".format(st, d, c, SENS[str(d)]["main_peak"],
          SENS[str(d)]["exec_peak"], SENS[str(d)]["actions"]), flush=True)
print("FACT X10-MAIN at {0}: ops {1}..{2} MAIN peak {3} (Executor {4}; fail_above {5} margin {6}; MEMSTOP {7} margin {8}); "
      "first op over 680: {9}; first op over {10} actions: {11}; group-split ops skipped above the cut {12}".format(
          START, S7N + 1, cut, mk(START, S7N, cut), pk(START, S7N, cut), SPR.X10_FAIL_MB, round(SPR.X10_FAIL_MB - mk(START, S7N, cut), 1), SX.MEM_STOP_MB,
          round(SX.MEM_STOP_MB - mk(START, S7N, cut), 1), first_over, MAXACT, first_cap, split_skipped), flush=True)
if cut < NOP:
    print("FACT next op {0} MAIN {1}".format(cut + 1, mk(START, S7N, cut + 1)), flush=True)
for b in range(S7N + 1, min(NOP, (first_over or NOP) + 2) + 1):
    print("FACT X10-OP op {0} kind {1} bind {2} exec {3} main {4} cut_ok {5} actions {6}".format(b, OPS[b - 1]["kind"], b in BIND, pk(START, S7N, b), mk(START, S7N, b),
          cut_ok(b), nact(S7N, b)), flush=True)
ids8 = [ids[n - 1] for k in range(S7N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
TAIL = [(k, OPS[k - 1]["kind"], [ids[n - 1] for n in OPS[k - 1]["acts"]]) for k in range(cut + 1, NOP + 1)]
XGRP = [g for g in groups if g[0] <= cut < g[1]]
gate("CAP s08 = {0} actions <= {1}, {2} (op {3}) NOT in s08 and it is the first action after the cut; no 'of' group across the cut {4}".format(
     len(ids8), MAXACT, CAPID, act2op[pos[CAPID]], XGRP),
     len(ids8) <= MAXACT and CAPID not in ids8 and TAIL and TAIL[0][2][0] == CAPID and not XGRP, {"tail": TAIL})
print("FACT CAP first op NOT included: op {0} {1} {2}; tail ops {3}..{4} ({5} ops): {6}".format(
      TAIL[0][0], TAIL[0][1], TAIL[0][2], cut + 1, NOP, len(TAIL), TAIL), flush=True)
subv = dict((SUBVI[i], {"op": act2op[pos[i]], "in_session": S7N < act2op[pos[i]] <= cut}) for i in SUBVI if i in pos)
rest = NOP - cut
X11OPS = {118: "p4_w_tp_row", 119: "p4_w_rp_row", 132: "p4_w_bd_row", 150: "p4_rbB_sel_t4168"}
x11 = dict((k, {"id": n, "v18_op_ids": [ids[m - 1] for m in OPS[k - 1]["acts"]], "in_s08": S7N < k <= cut}) for k, n in X11OPS.items())
print("FACT session 8 = {0} actions {1}..{2}; ops {3}..{4}; subVI drops {5}; ops left after s08 {6} of {7}".format(
      len(ids8), ids8[0], ids8[-1], S7N + 1, cut, subv, rest, NOP), flush=True)
print("FACT X11 earlier #2626-type rows by v18 op (none expected in s08): {0}".format(json.dumps(x11)), flush=True)
made3 = set("new:" + x["as"] for x in s01["actions"] + s02["actions"] + s03["actions"] if x.get("as"))
made4s = set("new:" + x["as"] for x in s04["actions"] if x.get("as"))
made5s = set("new:" + x["as"] for x in s05["actions"] if x.get("as"))
made6s = set("new:" + x["as"] for x in s06["actions"] if x.get("as"))
made7s = set("new:" + x["as"] for x in s07["actions"] if x.get("as"))
made_prev = made3 | made4s | made5s | made6s | made7s
made8 = set("new:" + A[pos[i] - 1]["as"] for i in ids8 if A[pos[i] - 1].get("as"))
_h3, CM3, _s3 = SPR.read_creation_map(CMAP3)
_h4, CM4, _s4 = SPR.read_creation_map(CMAP4)
_h5, CM5, _s5 = SPR.read_creation_map(CMAP5)
_h6, CM6, _s6 = SPR.read_creation_map(CMAP6)
gate("CM s03 / s04 / s05 / s06 creation map headers == plans da66a030 / f349c39a / 1fc9b486 / cfbd9823 (s06 map {0} md5 {1})".format(rel(CMAP6), md5(CMAP6)),
     _h3.get("plan_md5") == WANT[S03] and _h4.get("plan_md5") == WANT[S04] and _h5.get("plan_md5") == WANT[S05] and _h6.get("plan_md5") == WANT[S06],
     (_h3, _h4, _h5, _h6))
inr = lambda r, made: r in made or r[:-1] in made                                          # noqa: E731


def real_of(sym):
    """s01..s06 symbol -> (real uid, sim id, map kind, sim class) via that session's END sym + its creation map (obj, diag, term)."""
    root = sym.split(".")[0]
    if inr(root, made6s):
        st, cm = END6, CM6
    elif inr(root, made5s):
        st, cm = END5, CM5
    elif inr(root, made4s):
        st, cm = END4, CM4
    else:
        st, cm = END3, CM3
    sid = st["sym"].get(sym)
    if not isinstance(sid, int):
        return None, sid, None, None
    for k in ("obj", "diag", "term"):
        if sid in cm[k]:
            return int(cm[k][sid]["real"]), sid, k, SS.obj_class(st, sid)
    return None, sid, None, None


s07by = dict((x["id"], x) for x in s07["actions"])
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
REB = collections.defaultdict(set)                                                           # how the REBASED s07 plan bound s01..s06 symbols
for a in A[len(prev6):len(prev_ids)]:
    for f in UIDF + ADDRF:
        y = a.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if isinstance(s, str) and s.startswith("new:") and inr(s.split(".")[0], made3 | made4s | made5s | made6s):
            z = s07by[a["id"]].get(f)
            zu = z.get("uid") if isinstance(z, dict) else z
            REB[s if not (f in ADDRF and isinstance(y, str)) else s.split(".")[0]].add(zu)
CROSS, bad, RMAP = [], [], {}


def sub(x):                                                                                   # prep_c150_a1_1_mk.py:204-231, copied; s01..s06 -> REAL
    for f in UIDF + ADDRF:
        y = x.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if not inr(root, made_prev):
            continue
        key = root if (f in ADDRF and isinstance(y, str)) else s
        early = not inr(root, made7s)
        if early:
            u, sid, kind, csim = real_of(key)
            creal = SS.obj_class(END7, u) if isinstance(u, int) else None
            RMAP[key] = {"real": u, "sim": sid, "kind": kind, "class_sim": csim, "class_real": creal, "s07_bound": sorted(REB.get(key) or [])}
            ok = isinstance(u, int) and u > 0 and creal is not None and (csim is None or csim == creal) and (not REB.get(key) or REB[key] == {u})
        else:
            u = END7["sym"].get(key)
            ok = isinstance(u, int) and u < 0
        if f in ADDRF and isinstance(y, str):
            x[f] = {"uid": u, "term": s.split(".", 1)[1]}
        elif isinstance(y, dict):
            x[f]["uid"] = u
        else:
            x[f] = u
        CROSS.append({"action": x["id"], "field": f, "symbol": s, "uid": u, "from": "s01-s06 real" if early else "s07 provisional"})
        ok or bad.append((x["id"], f, s, u))
    return x


keep = [sub(copy.deepcopy(A[pos[i] - 1])) for i in ids8]
for k in sorted(RMAP):
    print("FACT R {0} -> real #{1} (sim #{2}, map kind {3}); class sim {4} / real {5}; s07 plan bound {6}".format(
          k, RMAP[k]["real"], RMAP[k]["sim"], RMAP[k]["kind"], RMAP[k]["class_sim"], RMAP[k]["class_real"], RMAP[k]["s07_bound"]), flush=True)
gate("R {0} s01..s06 symbol(s) -> real uid by that session's creation map, (uid, class) equal in END7, == the rebased s07 plan where it bound them".format(len(RMAP)),
     all(isinstance(r["real"], int) and r["real"] > 0 and r["class_real"] is not None and (r["class_sim"] is None or r["class_sim"] == r["class_real"])
         and (not r["s07_bound"] or r["s07_bound"] == [r["real"]]) for r in RMAP.values()), RMAP)
late = [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), str) and x[f].startswith("new:") and not inr(x[f].split(".")[0], made8)]
late += [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), dict) and isinstance(x[f].get("uid"), str)
         and x[f]["uid"].startswith("new:") and not inr(x[f]["uid"].split(".")[0], made8)]
gate("C2 {0} cross ref(s): s07 symbols -> negative provisional uids, s01..s06 -> real uids {1}; no ref to a later session's symbol".format(
     len(CROSS), [(c["action"], c["symbol"], c["uid"]) for c in CROSS]), not bad and not late, {"bad": bad, "late": late[:8]})
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S07), "md5": md5(S07)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s08v18a", goal="card 150-a3-6 PASS A: P4 v18 session 8 (ops {0}..{1}), no open_rows".format(S7N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(AIN)))
try:
    SA = SS.simulate(AIN, PROVB, out_root=PAROOT, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "s07v18-open") for r in s07.get("open_rows") or [])
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c146_a1_3_mk.py:239-252, copied
    n0 = SA["steps"][-1]["n"]
    for st in reversed(SA["steps"]):
        if st.get("cdiff_rows") is not None and key in st["cdiff_rows"]:
            n0 = st["n"]
        else:
            break
    p = (SS.V.key_parts(key)[0], SS.V.key_parts(key)[2])
    if n0 >= 1:
        ties[key] = {"n": n0, "id": keep[n0 - 1]["id"], "op": keep[n0 - 1]["op"], "class": keep[n0 - 1].get("class") or keep[n0 - 1]["op"], "pair": p}
    elif p in ok_pairs:
        ties[key] = {"n": 0, "id": ok_pairs[p], "op": "base", "class": "step0-declared", "pair": p}
    else:
        untied.append((key, n0))
gate("TIE every end row ({0}) tied to a session-8 action or an s07v18 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c150-a3-6: made by session-8 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c150-a3-6: open at step 0 = declared open row of plan_ring_p4_s07v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s08v18", goal=("RING P4 v18 LabVIEW session 8 (card 150-a3-6, made at the measured s07 load, PD365(g), capped before p4_x_n2_order): v18 ops {0}..{1} "
               "({2} actions), cut so the MAIN recipe's X10 (Executor + source reads) <= 680 at the MEASURED start {3} (s07 load 589.4 + op-0), <= 40 actions, on "
               "session 7's SIMULATED end (plan 08c2ad4d; provisional -> stage_prerun --rebase onto the adopted s07 file's graph 71935a84)").format(S7N + 1, cut, len(keep), START),
               base=BASEREF, open_rows=orows, actions=keep), open(IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(OUT) if os.path.isfile(OUT) else {}
gate("SB plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"]})
o8 = SX.compile_plan(p)
cps8 = sorted({0, len(o8)} | set(k for k, o in enumerate(o8, 1) if o["kind"] in SX.BIND_KINDS))
mp = SPR.x10_model_peak([o["kind"] for o in o8], cps8, model=MODEL, start_mb=START)
kv, k8 = [o["kind"] for o in OPS[S7N:cut]], [o["kind"] for o in o8]
srx = [(S7N + 1 + j, OPS[S7N + j].get("reg")) for j in range(len(kv)) if j < len(k8) and kv[j] != k8[j]]
MKOP = dict(("new:" + a["as"], act2op[pos[a["id"]]]) for a in A if a.get("as"))            # card 147-a1-2: 'new:<sym>' -> creating v18 op


def kdec(k, kv_, ks_, first_op, s8src):
    """card 147-a1-2 (PD353(e)): one kind-gate decision for v18 op k (v18 kind kv_, s08 kind ks_)."""
    if kv_ == ks_:
        return True, "same kind"
    if kv_ == "wire_sr" and ks_ == "connect" and inr(str(OPS[k - 1].get("reg")), made_prev):
        return True, "wire_sr -> connect on a register made earlier (146-a1-5 rule, unchanged)"
    if kv_ == "branch" and ks_ == "connect":
        sym = OPS[k - 1].get("tunnel")
        c = MKOP.get(sym)
        su = s8src.get("uid") if isinstance(s8src, dict) else s8src
        why = "source tunnel {0} created by v18 op {1}; session first op {2}; s08 src uid {3!r}".format(sym, c, first_op, su)
        if c is not None and c < first_op and isinstance(su, int) and not isinstance(su, bool):
            return True, "branch -> connect ALLOWED (PD353(e)): " + why
        return False, "branch -> connect REFUSED (source not made in an earlier session): " + why
    return False, "pair {0} -> {1} not whitelisted".format(kv_, ks_)


KD = []
for j in range(len(kv)):
    ks_ = k8[j] if j < len(k8) else None
    a8 = p["actions"][o8[j]["acts"][0] - 1] if j < len(o8) else {}
    ok_, why_ = kdec(S7N + 1 + j, kv[j], ks_, S7N + 1, a8.get("src"))
    KD.append({"op": S7N + 1 + j, "v18": kv[j], "s08": ks_, "action": a8.get("id"), "ok": ok_, "why": why_})
    print("FACT KIND op {0} {1} -> {2} action {3}: {4} - {5}".format(S7N + 1 + j, kv[j], ks_, a8.get("id"), "PASS" if ok_ else "REFUSED", why_), flush=True)
kinds_ok = len(kv) == len(k8) and all(d["ok"] for d in KD)
print("FACT kind differences v18 -> s08 (op, v18 reg symbol): {0}".format(srx), flush=True)
neg = [k for k in range(S7N + 1, cut + 1) if OPS[k - 1]["kind"] == "branch" and S7N + 1 <= (MKOP.get(OPS[k - 1].get("tunnel")) or 0) <= cut]
nk, nfirst = (neg[0], S7N + 1) if neg else (116, MKOP.get(OPS[115].get("tunnel")))
nok, nwhy = kdec(nk, "branch", "connect", nfirst, {"uid": -999, "term": "outer"})
print("NEGCTL synthetic branch -> connect on v18 op {0} ({1}), session first op {2}, fake src uid -999: {3} - {4} (no file written)".format(
      nk, "real in-session branch" if neg else "op 116 with the session started at its source's creating op", nfirst, "PASS" if nok else "REFUSED", nwhy), flush=True)
gate("NEG negative control: branch -> connect with the source made in this session is REFUSED", not nok, nwhy)
print("FACT X10s compiled plan N {0} R {1} Executor peak {2}, MAIN {3} at {4}; MEMSTOP {5}".format(mp["N"], mp["R"], mp["peak_mb"],
      round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), START, SX.MEM_STOP_MB), flush=True)
gate("X10s compiled plan: Executor peak {0} == table {1}; MAIN {2} <= {3}; kinds == v18 ops {4}..{5} except wire_sr -> connect on an earlier register / branch -> connect on an earlier-session source {6}".format(
     mp["peak_mb"], pk(START, S7N, cut), round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), SPR.X10_FAIL_MB, S7N + 1, cut, srx),
     abs(mp["peak_mb"] - pk(START, S7N, cut)) < 0.05 and round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1) <= SPR.X10_FAIL_MB and kinds_ok,
     dict(collections.Counter(o["kind"] for o in o8)))
# ---- card 148-a3-3 (3): sink-gate census, REPORT ONLY - a wire row whose dst is a ControlTerminal in the sim state before it
SF = dict((int(x["n"]), x["path"]) for x in (p.get("finalized") or {}).get("step_files") or [])
SGC = []
for n, a in enumerate(p["actions"], 1):
    if a.get("op") != "wire" or n not in SF or (n - 1) not in SF:
        continue
    eff = J(SF[n]).get("effect") or {}
    prev = J(SF[n - 1])["state"]["terminals"]
    du, su = eff.get("dst_term_uid"), eff.get("src_term_uid")
    rd = next((r for r in prev if r["term_uid"] == du), None)
    rs = next((r for r in prev if r["term_uid"] == su), None)
    if rd is not None and SX.is_ct(rd):
        route = "indicator" if (rs is not None and rs.get("wire_uid")) else "ctlsink"
        SGC.append({"n": n, "id": a["id"], "sink": [rd["owner_uid"], rd["term_name"]], "dst_term_uid": du, "src_term_uid": su, "route": route,
                    "needs_sink_gate": route == "indicator"})
for e in SGC:
    print("FACT SG-CENSUS row #{0} {1}: ControlTerminal sink {2} t{3} from t{4}: route {5}; declared sink gate needed {6}".format(
          e["n"], e["id"], e["sink"], e["dst_term_uid"], e["src_term_uid"], e["route"], e["needs_sink_gate"]), flush=True)
print("FACT SG-CENSUS {0} ControlTerminal-sink row(s); {1} need a declared sink gate: {2}".format(
      len(SGC), sum(1 for e in SGC if e["needs_sink_gate"]), [e["id"] for e in SGC if e["needs_sink_gate"]]), flush=True)
V18SUM = os.path.join(SIM, "ring_p4_v18", "ring_p4_v3", "summary.json")                   # card 147-a1-2: v18's own simulated per-action cdiff
V18S = J(V18SUM)
v18n = dict((s["n"], s) for s in V18S["steps"])
n_last, n_prev = pos[ids8[-1]], pos[prev_ids[-1]]
e8, e18 = set(SB.get("end_cdiff_rows") or []), set(v18n[n_last].get("cdiff_rows") or [])
b8, b18 = set(SB["steps"][0].get("cdiff_rows") or []), set(v18n[n_prev].get("cdiff_rows") or [])
print("FACT V18E v18 summary {0} md5 {1} (plan {2}); s08 last action {3} = v18 action #{4}; s07 last action {5} = v18 action #{6}".format(
      rel(V18SUM), md5(V18SUM), V18S["plan"], ids8[-1], n_last, prev_ids[-1], n_prev), flush=True)
print("FACT V18E-BASE s08 step 0 rows {0} vs v18 after #{1} rows {2}; only s08 {3}; only v18 {4}".format(
      len(b8), n_prev, len(b18), sorted(b8 - b18), sorted(b18 - b8)), flush=True)
print("FACT V18E-END s08 end rows {0} vs v18 after #{1} rows {2}; only s08 {3}; only v18 {4}".format(
      len(e8), n_last, len(e18), sorted(e8 - e18), sorted(e18 - e8)), flush=True)
gate("V18E s08 sim end vs v18 sim after the same last action #{0}: end difference {1} within the difference inherited at step 0 {2} (only-s08 {3} subset of {4}; "
     "only-v18 {5} subset of {6}); full V18E-R' after the rebase in the pred".format(n_last, len(e8 ^ e18), len(b8 ^ b18), sorted(e8 - e18), sorted(b8 - b18),
                                                                                    sorted(e18 - e8), sorted(b18 - b8)),
     (e8 - e18) <= (b8 - b18) and (e18 - e8) <= (b18 - b8), {"only_s08": sorted(e8 - e18), "only_v18": sorted(e18 - e8)})
# ---- card 150-a3-6 (c): BOUNDARY s08/s09, read from the plan + sims, no inference
TREF = []
for k, _kd, tids in TAIL:
    for i in tids:
        a = A[pos[i] - 1]
        for f in UIDF + ADDRF:
            y = a.get(f)
            s = y.get("uid") if isinstance(y, dict) else y
            if isinstance(s, str) and s.startswith("new:"):
                r0 = s.split(".")[0]
                TREF.append({"op": k, "id": i, "field": f, "symbol": s, "made_in": "s08" if inr(r0, made8) else ("s01-s07" if inr(r0, made_prev) else "tail/later")})
for t in TREF:
    print("FACT BOUNDARY tail ref op {0} {1}.{2} = {3} made in {4}".format(t["op"], t["id"], t["field"], t["symbol"], t["made_in"]), flush=True)
endn = sorted(set(int(SS.V.key_parts(k)[0]) for k in (SB.get("end_cdiff_rows") or [])))
FRAME_HIT = [n for n in endn if n in (29869, 29721)]
print("FACT BOUNDARY 'of' groups across the cut {0}; s08 sim end rows {1} on nodes {2}; open_rows {3}; end rows on #29869/#29721 {4}; "
      "150-a3-5 pass-A stopped at n {5} {6} (copy summary)".format(XGRP, len(SB.get("end_cdiff_rows") or []), endn, len(orows), FRAME_HIT,
                                                                   (PREVSUM.get("failed") or {}).get("n"), (PREVSUM.get("failed") or {}).get("id")), flush=True)
json.dump({"card": "150-a3-6", "cap": {"max_actions": MAXACT, "cap_id": CAPID, "first_not_included": TAIL[0], "tail": TAIL, "of_across_cut": XGRP,
                                       "tail_refs": TREF, "end_nodes": endn, "end_rows_on_fs29721": FRAME_HIT, "prev_copy": {"zip": rel(PREVZIP), "md5": md5(PREVZIP), "files": PREVMD5},
                                       "prev_failed": PREVSUM.get("failed")},
           "main_src_reads": MAIN_SRC_READS, "v18": {"path": rel(V18), "md5": md5(V18)}, "s07": {"path": rel(S07), "md5": md5(S07)},
           "ops": [S7N + 1, cut], "first": ids8[0], "last": ids8[-1], "actions": len(keep), "start_mb": START, "start_cite": START_CITE,
           "start_rule": "stage_prerun.x10_start(adopted s07 b3f86b32) = measured load 589.4 + op0_read_mb (PD352(b), s05 re-cut rule prep_c146_a1_2_mk.py)",
           "s07_ops": N7, "max_actions": MAXACT, "first_op_over_max_actions": first_cap, "whole_remainder": cut == NOP,
           "exec_peak_mb": pk(START, S7N, cut), "main_peak_mb": mk(START, S7N, cut), "margin_mb": round(SPR.X10_FAIL_MB - mk(START, S7N, cut), 1),
           "memstop_margin_mb": round(SX.MEM_STOP_MB - mk(START, S7N, cut), 1), "next_op": cut + 1 if cut < NOP else None,
           "limit_mb": SPR.X10_FAIL_MB, "memstop_mb": SX.MEM_STOP_MB, "first_op_over_limit": first_over, "sensitivity": SENS,
           "x11_rows": x11, "subvi_drops": subv, "cross_refs": CROSS, "real_map": RMAP, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ops_total": NOP, "ops_left_after": rest, "kinds": dict(collections.Counter(o["kind"] for o in o8)),
           "kind_decisions": KD, "negctl": {"op": nk, "first_op": nfirst, "ok": nok, "why": nwhy}, "sink_gate_census": SGC,
           "v18e": {"v18_action": n_last, "s08_end_rows": len(e8), "v18_rows": len(e18), "cdiff": len(e8 ^ e18), "base_cdiff": len(b8 ^ b18)}},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s07 / s06 / s05 / s04 / s03 / END step files / s05 map / s07 graph / memory_model untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
