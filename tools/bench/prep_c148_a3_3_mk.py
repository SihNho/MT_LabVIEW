# ---
# labview: none
# hardware: none
# ---
r"""prep_c148_a3_3_mk - card 148-a3-3 step 1 (OFFLINE, no LabVIEW, never launched). P4 session 7 of plan v18 (2ea6cafa) = v18 ops 136..cut,
PROVISIONAL on session 6's SIMULATED end (plan_ring_p4_s06v18.json cfbd9823 = the s06 plan rebased onto the real s05 graph, finalized last step
sim/ring_p4_s06v18/step_25_wire.json abe1dd11); the --rebase onto the REAL s06 graph is a later card (PD358(f), PD360(d), PD361(d)).
COPY of prep_c147_a1_3_mk.py (8900e0df) with ONLY:
  (1) BASE: s06's simulated end (END6) instead of s05's; S6N = 135 (s01..s06 ids); session-7 names (sim/ring_p4_s07v18, plan_ring_p4_s07v18*,
      FACTS prep_c148_a3_3_session.json); symbol origins one session deeper: s06 symbols -> END6 sym (negative, provisional); s05 symbols ->
      s05 END sym (step_21_create ca3661f3) -> s05's creation map (plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl) -> REAL uid; s04 / s01..s03
      as before; (uid, class) checked against END6 and against the s06 plan (rebased) where it bound them;
  (2) START RULE INPUTS: the provisional rule of prep_c147_a1_2_mk.py (the a1-2 maker, used while the previous file does not exist): predicted
      s06 load = load_by_vi[3f9ac26b] 606.7 (MEASURED adopted s05 file) + load_growth_mb_per_op 0.719 (memory_model.json, 'used only to PREDICT
      an unsaved file's load') x 21 compiled s06 ops, + op0_read_mb 5.9 = 627.7. The prerun cannot give a start for a provisional base
      (stage_prerun.py:2079-2080 x10_plan_start None; :2593-2599 X10 refuses) - the maker's MAIN formula (== x10_model_peak + 2 source reads,
      stage_prerun.py:2608-2611) is the cut rule, as in 147-a1-2;
  (3) REPORT ONLY (no gate): the sink-gate census of the s07 wire rows (a ControlTerminal sink in the sim state before the row: wired source ->
      'indicator' route = wire_indicators, which needs a declared sink gate on this ExecState-0 bed, stagexec.py:1372-1397, 2975-2990).
Existing tools checked: prep_c147_a1_3_mk.py (copied), prep_c147_a1_2_mk.py (start rule), stage_prerun.read_creation_map / x10_model_peak /
load_memory_model, stagesim.simulate / obj_class, stagexec.compile_plan / is_ct; no new op, no tool edit.
PREDICTION CONTRACT: M0 input md5 == pins; X0 START = round(606.7 + 0.719*21 + 5.9, 1) = 627.7; S6 v18 ops 1..135 == s01..s06 ids; E6 END step
  file on its pin, s06 base real; CUT >= 136, splits no 'of' group, MAIN peak <= 680 (projection about op 148: ~15 MB over the s06 start);
  R every s01..s05 symbol -> real uid, same class, == the s06 plan's binding; C2 s06 refs negative, no later ref; SA pass A replays; TIE every
  end row tied; SB plan FINAL provisional, open_rows_match; NEG refused; X10s compiled plan peak == table at START, kinds pass; V18E cdiff 0;
  U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c148_a3_3_mk.log -- py -u tools/bench/prep_c148_a3_3_mk.py"""
import collections, copy, glob, hashlib, json, os, re, sys, traceback                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V18, S01, S02, S03, S04, S05, S06 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02v18.json",
                                                                   "plan_ring_p4_s03v18.json", "plan_ring_p4_s04v18.json", "plan_ring_p4_s05v18.json",
                                                                   "plan_ring_p4_s06v18.json"))
END3F = os.path.join(SIM, "ring_p4_s03v18", "step_20_create.json")
END4F = os.path.join(SIM, "ring_p4_s04v18", "step_23_wire.json")
END5F = os.path.join(SIM, "ring_p4_s05v18", "step_21_create.json")
END6F = os.path.join(SIM, "ring_p4_s06v18", "step_25_wire.json")
CMAP3 = os.path.join(B, "creation_map", "plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl")
CMAP4 = os.path.join(B, "creation_map", "plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl")
CMAP5 = os.path.join(B, "creation_map", "plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl")
S7D = os.path.join(SIM, "ring_p4_s07v18")
D7 = os.path.join(S7D, "s06end")
PROVB = os.path.join(D7, "base_provisional.json")
PAROOT = os.path.join(S7D, "_passA")
DA = os.path.join(PAROOT, "ring_p4_s07v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s07v18a_in.json"), os.path.join(B, "plan_ring_p4_s07v18_in.json"), os.path.join(B, "plan_ring_p4_s07v18.json")
FACTS = os.path.join(B, "prep_c148_a3_3_session.json")
MAIN_SRC_READS = 2                       # main recipe source census_snapshot reads (diag_c147_c3_2_prerun.log:112: R 8 = Executor 6 + 2)
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S06: "cfbd9823d3b47be39de94f2125ad6b66", S05: "1fc9b486551b3f1fe42f25167375ba30",
        S04: "f349c39a17330531e688ff1f70ce426e", S03: "da66a0300851133d93881be3c28f2fdc", END6F: "abe1dd1113d181cbaa0dd723979a4f2e",
        END5F: "ca3661f3e02bcac1749e1edcf0a1f018", END4F: "b5ae7f79975b9faca0722bb4dc6e3781", END3F: "5f31db45b1b8c7f66b48cf28d92a1e03",
        CMAP5: "50d2b2ff208370e90a463230cc76d390"}
S05VI_MD5 = "3f9ac26b69179eb53c202d90407ce7ee"                                            # the ADOPTED s05 file = s06's input (147-a1-1)
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
v18, s01, s02, s03, s04, s05, s06 = J(V18), J(S01), J(S02), J(S03), J(S04), J(S05), J(S06)
N6 = len(SX.compile_plan(s06))
LBV = (MODEL.get("load_by_vi") or {}).get(S05VI_MD5) or {}
GROW = float(MODEL["load_growth_mb_per_op"]["value"])
OP0 = float(MODEL["op0_read_mb"]["value"])
LOAD6 = round(float(LBV["value"]) + GROW * N6, 1)
START = round(float(LBV["value"]) + GROW * N6 + OP0, 1)
START_CITE = ("PROVISIONAL: predicted s06 file load {0} = load_by_vi[3f9ac26b] {1} (memory_model.json load_by_vi, diag_c147_a1_1_graph.log:24) + "
              "load_growth_mb_per_op {2} (memory_model.json load_growth_mb_per_op) x {3} compiled ops of plan_ring_p4_s06v18.json cfbd9823; + op0_read_mb {4} "
              "(x10_start rule, stage_prerun.py:2061-2070). REPLACE by the s06 file's measured load at rebase").format(LOAD6, LBV.get("value"), GROW, N6, OP0)
gate("X0 PROVISIONAL start: load_by_vi[3f9ac26b] == 606.7; {0} compiled s06 ops; START {1} = 606.7 + {2} x {0} + {3}".format(N6, START, GROW, OP0),
     LBV.get("value") == 606.7 and N6 == 21 and START is not None, (LOAD6, START))
print("FACT X10 START {0} = {1}".format(START, START_CITE), flush=True)
print("FACT not used as the start: the s06 PREDICTED peaks (diag_c147_a1_3_facts.md:20) Executor 674.2 / MAIN 679.3 are in-session peaks of the s06 "
      "Executor run, not the saved s06 file's load (a start there leaves {0} MB below 680)".format(round(680.0 - 674.2 - OP0, 1)), flush=True)
gate("E6 s06v18 finalized last step file == {0} (pinned md5); base real (not provisional)".format(rel(END6F)),
     s06["finalized"]["step_files"][-1]["path"] == rel(END6F) and s06["finalized"]["step_files"][-1]["md5"] == WANT[END6F]
     and not (s06.get("base") or {}).get("provisional"), s06["finalized"]["step_files"][-1])
END6, END5, END4, END3 = J(END6F)["state"], J(END5F)["state"], J(END4F)["state"], J(END3F)["state"]
gate("E6b END6 state sym/neg present", isinstance(END6.get("sym"), dict) and isinstance(END6.get("neg"), int), (END6.get("sym"), END6.get("neg")))
os.makedirs(D7, exist_ok=True)
json.dump(END6, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)          # prep_c146_a1_3_mk.py:105
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END6.get("sym")), "neg", END6.get("neg"), "vi md5", END6.get("md5"), flush=True)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
prev3 = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]]
prev4 = prev3 + [x["id"] for x in s04["actions"]]
prev5 = prev4 + [x["id"] for x in s05["actions"]]
prev_ids = prev5 + [x["id"] for x in s06["actions"]]
S6N = max(act2op[n] for n in range(1, len(prev_ids) + 1))
gate("S6 v18 ops 1..{0} = s01's {1} + s02's {2} + s03's {3} + s04's {4} + s05's {5} + s06's {6} ids".format(S6N, len(s01["actions"]), len(s02["actions"]),
     len(s03["actions"]), len(s04["actions"]), len(s05["actions"]), len(s06["actions"])),
     [ids[n - 1] for k in range(1, S6N + 1) for n in OPS[k - 1]["acts"]] == prev_ids and S6N == 135)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
pk = lambda st, a, b: round(st + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
mk = lambda st, a, b: round(pk(st, a, b) + MAIN_SRC_READS * v("read_mb"), 1)                # noqa: E731  stage_prerun.py:2608-2611
lcut = lambda st: max([b for b in range(S6N + 1, NOP + 1) if mk(st, S6N, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)   # noqa: E731
cut = lcut(START)
first_over = next((b for b in range(S6N + 1, NOP + 1) if mk(START, S6N, b) > SPR.X10_FAIL_MB), None)
split_skipped = [b for b in range(S6N + 1, (first_over or NOP + 1)) if not cut_ok(b) and (cut is None or b > cut)]
gate("CUT longest prefix from op {0} splitting no 'of' group with MAIN X10 <= {1} at {2}: op {3}".format(S6N + 1, SPR.X10_FAIL_MB, START, cut),
     cut is not None and cut >= S6N + 1 and cut_ok(cut) and mk(START, S6N, cut) <= SPR.X10_FAIL_MB, {"first_over": first_over, "groups_split_at": split_skipped})
SENS = {}
for d in (-5.0, 0.0, 5.0):
    st = round(START + d, 1)
    c = lcut(st)
    SENS[str(d)] = {"start": st, "cut": c, "main_peak": c and mk(st, S6N, c), "exec_peak": c and pk(st, S6N, c), "actions": c and sum(len(OPS[k - 1]["acts"]) for k in range(S6N + 1, c + 1))}
    print("FACT SENS start {0} ({1:+} MB): cut op {2}, MAIN peak {3}, Executor peak {4}, actions {5}".format(st, d, c, SENS[str(d)]["main_peak"],
          SENS[str(d)]["exec_peak"], SENS[str(d)]["actions"]), flush=True)
print("FACT X10-MAIN at {0}: ops {1}..{2} MAIN peak {3} (Executor {4}; fail_above {5} margin {6}; MEMSTOP {7} margin {8}); next op {9} MAIN {10}; "
      "first op over: {11}; group-split ops skipped above the cut {12}".format(
          START, S6N + 1, cut, mk(START, S6N, cut), pk(START, S6N, cut), SPR.X10_FAIL_MB, round(SPR.X10_FAIL_MB - mk(START, S6N, cut), 1), SX.MEM_STOP_MB,
          round(SX.MEM_STOP_MB - mk(START, S6N, cut), 1), cut + 1, mk(START, S6N, cut + 1), first_over, split_skipped), flush=True)
nxt = max([b for b in range(cut + 1, NOP + 1) if mk(START, cut, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
print("FACT next session at the SAME start would end at op {0} (formula only)".format(nxt), flush=True)
for b in range(S6N + 1, min(NOP, (first_over or NOP) + 2) + 1):
    print("FACT X10-OP op {0} kind {1} bind {2} exec {3} main {4} cut_ok {5}".format(b, OPS[b - 1]["kind"], b in BIND, pk(START, S6N, b), mk(START, S6N, b), cut_ok(b)), flush=True)
ids7 = [ids[n - 1] for k in range(S6N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
subv = dict((SUBVI[i], {"op": act2op[pos[i]], "in_session": S6N < act2op[pos[i]] <= cut}) for i in SUBVI if i in pos)
rest = NOP - cut
X11OPS = {118: "p4_w_tp_row", 119: "p4_w_rp_row", 132: "p4_w_bd_row", 150: "p4_rbB_sel_t4168"}
x11 = dict((k, {"id": n, "v18_op_ids": [ids[m - 1] for m in OPS[k - 1]["acts"]], "in_s07": S6N < k <= cut}) for k, n in X11OPS.items())
print("FACT session 7 = {0} actions {1}..{2}; ops {3}..{4}; subVI drops {5}; ops left after s07 {6} of {7}".format(
      len(ids7), ids7[0], ids7[-1], S6N + 1, cut, subv, rest, NOP), flush=True)
print("FACT X11 #2626 rows by v18 op: {0}".format(json.dumps(x11)), flush=True)
made3 = set("new:" + x["as"] for x in s01["actions"] + s02["actions"] + s03["actions"] if x.get("as"))
made4s = set("new:" + x["as"] for x in s04["actions"] if x.get("as"))
made5s = set("new:" + x["as"] for x in s05["actions"] if x.get("as"))
made6s = set("new:" + x["as"] for x in s06["actions"] if x.get("as"))
made_prev = made3 | made4s | made5s | made6s
made7 = set("new:" + A[pos[i] - 1]["as"] for i in ids7 if A[pos[i] - 1].get("as"))
_h3, CM3, _s3 = SPR.read_creation_map(CMAP3)
_h4, CM4, _s4 = SPR.read_creation_map(CMAP4)
_h5, CM5, _s5 = SPR.read_creation_map(CMAP5)
gate("CM s03 / s04 / s05 creation map headers == plans da66a030 / f349c39a / 1fc9b486",
     _h3.get("plan_md5") == WANT[S03] and _h4.get("plan_md5") == WANT[S04] and _h5.get("plan_md5") == WANT[S05], (_h3, _h4, _h5))
inr = lambda r, made: r in made or r[:-1] in made                                          # noqa: E731


def real_of(sym):
    """s01..s05 symbol -> (real uid, sim id, map kind, sim class) via that session's END sym + its creation map (obj, diag, term)."""
    root = sym.split(".")[0]
    st, cm = (END5, CM5) if inr(root, made5s) else ((END4, CM4) if inr(root, made4s) else (END3, CM3))
    sid = st["sym"].get(sym)
    if not isinstance(sid, int):
        return None, sid, None, None
    for k in ("obj", "diag", "term"):
        if sid in cm[k]:
            return int(cm[k][sid]["real"]), sid, k, SS.obj_class(st, sid)
    return None, sid, None, None


s06by = dict((x["id"], x) for x in s06["actions"])
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
REB = collections.defaultdict(set)                                                           # how the s06 plan (rebased) bound s01..s05 symbols
for a in A[len(prev5):len(prev_ids)]:
    for f in UIDF + ADDRF:
        y = a.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if isinstance(s, str) and s.startswith("new:") and inr(s.split(".")[0], made3 | made4s | made5s):
            z = s06by[a["id"]].get(f)
            zu = z.get("uid") if isinstance(z, dict) else z
            REB[s if not (f in ADDRF and isinstance(y, str)) else s.split(".")[0]].add(zu)
CROSS, bad, RMAP = [], [], {}


def sub(x):                                                                                   # prep_c147_a1_3_mk.py:176-203, copied; s01..s05 -> REAL
    for f in UIDF + ADDRF:
        y = x.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if not inr(root, made_prev):
            continue
        key = root if (f in ADDRF and isinstance(y, str)) else s
        early = not inr(root, made6s)
        if early:
            u, sid, kind, csim = real_of(key)
            creal = SS.obj_class(END6, u) if isinstance(u, int) else None
            RMAP[key] = {"real": u, "sim": sid, "kind": kind, "class_sim": csim, "class_real": creal, "s06_bound": sorted(REB.get(key) or [])}
            ok = isinstance(u, int) and u > 0 and creal is not None and (csim is None or csim == creal) and (not REB.get(key) or REB[key] == {u})
        else:
            u = END6["sym"].get(key)
            ok = isinstance(u, int) and u < 0
        if f in ADDRF and isinstance(y, str):
            x[f] = {"uid": u, "term": s.split(".", 1)[1]}
        elif isinstance(y, dict):
            x[f]["uid"] = u
        else:
            x[f] = u
        CROSS.append({"action": x["id"], "field": f, "symbol": s, "uid": u, "from": "s01-s05 real" if early else "s06 provisional"})
        ok or bad.append((x["id"], f, s, u))
    return x


keep = [sub(copy.deepcopy(A[pos[i] - 1])) for i in ids7]
for k in sorted(RMAP):
    print("FACT R {0} -> real #{1} (sim #{2}, map kind {3}); class sim {4} / real {5}; s06 plan bound {6}".format(
          k, RMAP[k]["real"], RMAP[k]["sim"], RMAP[k]["kind"], RMAP[k]["class_sim"], RMAP[k]["class_real"], RMAP[k]["s06_bound"]), flush=True)
gate("R {0} s01..s05 symbol(s) -> real uid by that session's creation map, (uid, class) equal in END6, == the s06 plan where it bound them".format(len(RMAP)),
     all(isinstance(r["real"], int) and r["real"] > 0 and r["class_real"] is not None and (r["class_sim"] is None or r["class_sim"] == r["class_real"])
         and (not r["s06_bound"] or r["s06_bound"] == [r["real"]]) for r in RMAP.values()), RMAP)
late = [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), str) and x[f].startswith("new:") and not inr(x[f].split(".")[0], made7)]
late += [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), dict) and isinstance(x[f].get("uid"), str)
         and x[f]["uid"].startswith("new:") and not inr(x[f]["uid"].split(".")[0], made7)]
gate("C2 {0} cross ref(s): s06 symbols -> negative provisional uids, s01..s05 -> real uids {1}; no ref to a later session's symbol".format(
     len(CROSS), [(c["action"], c["symbol"], c["uid"]) for c in CROSS]), not bad and not late, {"bad": bad, "late": late[:8]})
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S06), "md5": md5(S06)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s07v18a", goal="card 148-a3-3 PASS A: P4 v18 session 7 (ops {0}..{1}), no open_rows".format(S6N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(AIN)))
try:
    SA = SS.simulate(AIN, PROVB, out_root=PAROOT, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "s06v18-open") for r in s06.get("open_rows") or [])
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
gate("TIE every end row ({0}) tied to a session-7 action or an s06v18 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c148-a3-3: made by session-7 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c148-a3-3: open at step 0 = declared open row of plan_ring_p4_s06v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s07v18", goal=("RING P4 v18 LabVIEW session 7 (card 148-a3-3, PROVISIONAL): v18 ops {0}..{1} ({2} actions), cut so the MAIN recipe's X10 "
               "(Executor + source reads) <= 680 at the PROVISIONAL start {3} (predicted s06 load), on session 6's SIMULATED end (plan cfbd9823; provisional -> "
               "stage_prerun --rebase onto session 6's adopted file's graph)").format(S6N + 1, cut, len(keep), START),
               base=BASEREF, open_rows=orows, actions=keep), open(IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(OUT) if os.path.isfile(OUT) else {}
gate("SB plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"]})
o7 = SX.compile_plan(p)
cps7 = sorted({0, len(o7)} | set(k for k, o in enumerate(o7, 1) if o["kind"] in SX.BIND_KINDS))
mp = SPR.x10_model_peak([o["kind"] for o in o7], cps7, model=MODEL, start_mb=START)
kv, k7 = [o["kind"] for o in OPS[S6N:cut]], [o["kind"] for o in o7]
srx = [(S6N + 1 + j, OPS[S6N + j].get("reg")) for j in range(len(kv)) if j < len(k7) and kv[j] != k7[j]]
MKOP = dict(("new:" + a["as"], act2op[pos[a["id"]]]) for a in A if a.get("as"))            # card 147-a1-2: 'new:<sym>' -> creating v18 op


def kdec(k, kv_, ks_, first_op, s7src):
    """card 147-a1-2 (PD353(e)): one kind-gate decision for v18 op k (v18 kind kv_, s07 kind ks_)."""
    if kv_ == ks_:
        return True, "same kind"
    if kv_ == "wire_sr" and ks_ == "connect" and inr(str(OPS[k - 1].get("reg")), made_prev):
        return True, "wire_sr -> connect on a register made earlier (146-a1-5 rule, unchanged)"
    if kv_ == "branch" and ks_ == "connect":
        sym = OPS[k - 1].get("tunnel")
        c = MKOP.get(sym)
        su = s7src.get("uid") if isinstance(s7src, dict) else s7src
        why = "source tunnel {0} created by v18 op {1}; session first op {2}; s07 src uid {3!r}".format(sym, c, first_op, su)
        if c is not None and c < first_op and isinstance(su, int) and not isinstance(su, bool):
            return True, "branch -> connect ALLOWED (PD353(e)): " + why
        return False, "branch -> connect REFUSED (source not made in an earlier session): " + why
    return False, "pair {0} -> {1} not whitelisted".format(kv_, ks_)


KD = []
for j in range(len(kv)):
    ks_ = k7[j] if j < len(k7) else None
    a7 = p["actions"][o7[j]["acts"][0] - 1] if j < len(o7) else {}
    ok_, why_ = kdec(S6N + 1 + j, kv[j], ks_, S6N + 1, a7.get("src"))
    KD.append({"op": S6N + 1 + j, "v18": kv[j], "s07": ks_, "action": a7.get("id"), "ok": ok_, "why": why_})
    print("FACT KIND op {0} {1} -> {2} action {3}: {4} - {5}".format(S6N + 1 + j, kv[j], ks_, a7.get("id"), "PASS" if ok_ else "REFUSED", why_), flush=True)
kinds_ok = len(kv) == len(k7) and all(d["ok"] for d in KD)
print("FACT kind differences v18 -> s07 (op, v18 reg symbol): {0}".format(srx), flush=True)
neg = [k for k in range(S6N + 1, cut + 1) if OPS[k - 1]["kind"] == "branch" and S6N + 1 <= (MKOP.get(OPS[k - 1].get("tunnel")) or 0) <= cut]
nk, nfirst = (neg[0], S6N + 1) if neg else (116, MKOP.get(OPS[115].get("tunnel")))
nok, nwhy = kdec(nk, "branch", "connect", nfirst, {"uid": -999, "term": "outer"})
print("NEGCTL synthetic branch -> connect on v18 op {0} ({1}), session first op {2}, fake src uid -999: {3} - {4} (no file written)".format(
      nk, "real in-session branch" if neg else "op 116 with the session started at its source's creating op", nfirst, "PASS" if nok else "REFUSED", nwhy), flush=True)
gate("NEG negative control: branch -> connect with the source made in this session is REFUSED", not nok, nwhy)
print("FACT X10s compiled plan N {0} R {1} Executor peak {2}, MAIN {3} at {4}; MEMSTOP {5}".format(mp["N"], mp["R"], mp["peak_mb"],
      round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), START, SX.MEM_STOP_MB), flush=True)
gate("X10s compiled plan: Executor peak {0} == table {1}; MAIN {2} <= {3}; kinds == v18 ops {4}..{5} except wire_sr -> connect on an earlier register / branch -> connect on an earlier-session source {6}".format(
     mp["peak_mb"], pk(START, S6N, cut), round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), SPR.X10_FAIL_MB, S6N + 1, cut, srx),
     abs(mp["peak_mb"] - pk(START, S6N, cut)) < 0.05 and round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1) <= SPR.X10_FAIL_MB and kinds_ok,
     dict(collections.Counter(o["kind"] for o in o7)))
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
n_last, n_prev = pos[ids7[-1]], pos[prev_ids[-1]]
e7, e18 = set(SB.get("end_cdiff_rows") or []), set(v18n[n_last].get("cdiff_rows") or [])
b7, b18 = set(SB["steps"][0].get("cdiff_rows") or []), set(v18n[n_prev].get("cdiff_rows") or [])
print("FACT V18E v18 summary {0} md5 {1} (plan {2}); s07 last action {3} = v18 action #{4}; s06 last action {5} = v18 action #{6}".format(
      rel(V18SUM), md5(V18SUM), V18S["plan"], ids7[-1], n_last, prev_ids[-1], n_prev), flush=True)
print("FACT V18E-BASE s07 step 0 rows {0} vs v18 after #{1} rows {2}; only s07 {3}; only v18 {4}".format(
      len(b7), n_prev, len(b18), sorted(b7 - b18), sorted(b18 - b7)), flush=True)
print("FACT V18E-END s07 end rows {0} vs v18 after #{1} rows {2}; only s07 {3}; only v18 {4}".format(
      len(e7), n_last, len(e18), sorted(e7 - e18), sorted(e18 - e7)), flush=True)
gate("V18E s07 sim end cdiff rows == v18 sim cdiff rows after the same last action #{0} (cdiff {1})".format(n_last, len(e7 ^ e18)), e7 == e18,
     {"only_s07": sorted(e7 - e18), "only_v18": sorted(e18 - e7)})
json.dump({"card": "148-a3-3", "main_src_reads": MAIN_SRC_READS, "v18": {"path": rel(V18), "md5": md5(V18)}, "s06": {"path": rel(S06), "md5": md5(S06)},
           "ops": [S6N + 1, cut], "first": ids7[0], "last": ids7[-1], "actions": len(keep), "start_mb": START, "start_cite": START_CITE,
           "start_rule": "PROVISIONAL predicted s06 load (load_by_vi[3f9ac26b] + load_growth_mb_per_op x s06 ops) + op0_read_mb (prep_c147_a1_2_mk.py rule)",
           "pred_s06_load_mb": LOAD6, "s06_ops": N6,
           "exec_peak_mb": pk(START, S6N, cut), "main_peak_mb": mk(START, S6N, cut), "margin_mb": round(SPR.X10_FAIL_MB - mk(START, S6N, cut), 1),
           "memstop_margin_mb": round(SX.MEM_STOP_MB - mk(START, S6N, cut), 1), "next_op": cut + 1, "next_main_peak_mb": mk(START, S6N, cut + 1),
           "limit_mb": SPR.X10_FAIL_MB, "memstop_mb": SX.MEM_STOP_MB, "first_op_over_limit": first_over, "sensitivity": SENS,
           "next_session_cut_same_start": nxt, "x11_rows": x11, "subvi_drops": subv, "cross_refs": CROSS, "real_map": RMAP, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ops_total": NOP, "ops_left_after": rest, "kinds": dict(collections.Counter(o["kind"] for o in o7)),
           "kind_decisions": KD, "negctl": {"op": nk, "first_op": nfirst, "ok": nok, "why": nwhy}, "sink_gate_census": SGC,
           "v18e": {"v18_action": n_last, "s07_end_rows": len(e7), "v18_rows": len(e18), "cdiff": len(e7 ^ e18)}},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s06 / s05 / s04 / s03 / END step files / s05 map untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
