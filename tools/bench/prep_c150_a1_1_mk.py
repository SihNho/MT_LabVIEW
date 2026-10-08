# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a1_1_mk - card 150-a1-1 step 2 (OFFLINE, no LabVIEW, never launched). P4 session 7 of plan v18 (2ea6cafa) RE-MADE at the MEASURED s06
load (PD364(c)): v18 ops 136..cut, the longest prefix with MAIN X10 <= 680, <= 40 actions, no 'of' group split. Made on session 6's SIMULATED end
(plan_ring_p4_s06v18.json cfbd9823, step_25_wire abe1dd11) and then rebased by stage_prerun --rebase onto the REAL s06 graph
graph_ring_p4s06_20261008_192149.json a3ecb92b (separate bgrun) - the route the s05 re-cut took (prep_c146_a1_2_mk.py:5-9, prep_c146_a1_2_rebase.log)
and s06 took (prep_c147_a1_3_pred.py:5-7); stagesim simulates on a sim state, the real binding is the rebase's (no tool edit).
COPY of prep_c148_a3_3_mk.py (5f00cd4f) with ONLY:
  (1) START = stage_prerun.x10_start(<adopted s06 file md5 569ffbf5..>) = load_by_vi 593.8 (memory_model 8eec443c, diag_c149_a3_2_graph.log:24) + op0_read_mb
      5.9 = 599.7 - the s05 re-cut rule (prep_c146_a1_2_mk.py:52-53, stage_prerun.py:2061-2070); gate X0 checks load == 593.8, START == 593.8 + op0;
  (2) cut cap: at most MAXACT = 40 actions (card 150-a1-1 / PD364(c)); the rest of the cut rule unchanged;
  (3) the 148-a3-3 provisional files are byte-copied first to *_prov148 (plan / _in / _pred) and sim/ring_p4_s07v18/*.json -> _prov148/ (gate P),
      so PD364(c)'s fallback (rebase the 14-action s07) stays possible;
  (4) names: session table prep_c150_a1_1_session.json, card id / goal strings; WANT adds the s06 graph a3ecb92b and memory_model 8eec443c.
Existing tools checked: prep_c148_a3_3_mk.py (copied), prep_c146_a1_2_mk.py (start rule), stage_prerun.x10_start / read_creation_map / x10_model_peak,
stagesim.simulate / obj_class, stagexec.compile_plan / is_ct; no new op, no tool edit.
PREDICTION CONTRACT: M0 input md5 == pins; P prov148 copies == originals; X0 START 599.7; S6 v18 ops 1..135 == s01..s06 ids; E6 END step pin;
  CUT >= 150 (start 28 MB lower than 627.7), <= 40 actions, no 'of' split, MAIN <= 680; R s01..s05 symbols -> real uid; C2; SA; TIE; SB FINAL provisional;
  NEG refused; X10s == table, kinds pass; V18E cdiff 0; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c150_a1_1_mk.log -- py -u tools/bench/prep_c150_a1_1_mk.py"""
import collections, copy, glob, hashlib, json, os, re, shutil, sys, traceback             # noqa: E401
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
GRAPH6 = os.path.join(B, "graph_ring_p4s06_20261008_192149.json")
MMF = os.path.join(B, "memory_model.json")
S7D = os.path.join(SIM, "ring_p4_s07v18")
D7 = os.path.join(S7D, "s06end")
PROVB = os.path.join(D7, "base_provisional.json")
PAROOT = os.path.join(S7D, "_passA")
DA = os.path.join(PAROOT, "ring_p4_s07v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s07v18a_in.json"), os.path.join(B, "plan_ring_p4_s07v18_in.json"), os.path.join(B, "plan_ring_p4_s07v18.json")
PREDF = os.path.join(B, "plan_ring_p4_s07v18_pred.json")
FACTS = os.path.join(B, "prep_c150_a1_1_session.json")
MAIN_SRC_READS = 2                       # main recipe source census_snapshot reads (diag_c147_c3_2_prerun.log:112: R 8 = Executor 6 + 2)
MAXACT = 40                              # card 150-a1-1 / PD364(c): at most 40 actions
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S06: "cfbd9823d3b47be39de94f2125ad6b66", S05: "1fc9b486551b3f1fe42f25167375ba30",
        S04: "f349c39a17330531e688ff1f70ce426e", S03: "da66a0300851133d93881be3c28f2fdc", END6F: "abe1dd1113d181cbaa0dd723979a4f2e",
        END5F: "ca3661f3e02bcac1749e1edcf0a1f018", END4F: "b5ae7f79975b9faca0722bb4dc6e3781", END3F: "5f31db45b1b8c7f66b48cf28d92a1e03",
        CMAP5: "50d2b2ff208370e90a463230cc76d390", GRAPH6: "a3ecb92b27654c3d85b9ab5ff58aa069", MMF: "8eec443c5f0a9e6b44b0e5e180357e4b"}
PROV = {OUT: "aeae610ee123bf30d8ed92016282189f", IN: "97e4e0911a30edd255eb82d2a091d13f", PREDF: "e888ab67228f04ba98ed08d4e40055f6"}
S06VI_MD5 = "569ffbf51eb6051bf0fdb58946f9bb02"                                            # the ADOPTED s06 file = s07's input (149-a3-1)
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
# (3) the 148-a3-3 provisional s07 files are copied first (PD364(c) fallback stays possible)
P148 = os.path.join(S7D, "_prov148")
os.makedirs(P148, exist_ok=True)
pc = {}
if all(md5(p) == w for p, w in PROV.items()):
    for p in PROV:
        q = p.replace(".json", "_prov148.json")
        shutil.copyfile(p, q)
        pc[rel(q)] = md5(q)
    for p in sorted(glob.glob(os.path.join(S7D, "*.json"))):
        q = os.path.join(P148, os.path.basename(p))
        shutil.copyfile(p, q)
        pc[rel(q)] = md5(q) == md5(p)
gate("P prov148 copies: plan aeae610e / _in 97e4e091 / _pred e888ab67 + {0} sim/ring_p4_s07v18/*.json, byte-identical".format(
     len(glob.glob(os.path.join(P148, "*.json")))),
     md5(OUT.replace(".json", "_prov148.json")) == PROV[OUT] and md5(IN.replace(".json", "_prov148.json")) == PROV[IN]
     and md5(PREDF.replace(".json", "_prov148.json")) == PROV[PREDF] and len(glob.glob(os.path.join(P148, "*.json"))) >= 16, pc)
v18, s01, s02, s03, s04, s05, s06 = J(V18), J(S01), J(S02), J(S03), J(S04), J(S05), J(S06)
N6 = len(SX.compile_plan(s06))
LBV = (MODEL.get("load_by_vi") or {}).get(S06VI_MD5) or {}
OP0 = float(MODEL["op0_read_mb"]["value"])
XS = SPR.x10_start(S06VI_MD5, MODEL)
START = XS[0] if XS else None
START_CITE = "MEASURED: stage_prerun.x10_start(569ffbf5..) = {0} (s05 re-cut rule, prep_c146_a1_2_mk.py:52-53; stage_prerun.py:2061-2070)".format(XS and XS[1])
gate("X0 MEASURED start: load_by_vi[569ffbf5] == 593.8; x10_start == load + op0_read_mb ({0}) = {1}".format(OP0, START),
     LBV.get("value") == 593.8 and START is not None and abs(START - round(593.8 + OP0, 1)) < 0.05, XS)
print("FACT X10 START {0} = {1}".format(START, START_CITE), flush=True)
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
nact = lambda a, b: sum(len(OPS[k - 1]["acts"]) for k in range(a + 1, b + 1))             # noqa: E731
pk = lambda st, a, b: round(st + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
mk = lambda st, a, b: round(pk(st, a, b) + MAIN_SRC_READS * v("read_mb"), 1)                # noqa: E731  stage_prerun.py:2608-2611
lcut = lambda st: max([b for b in range(S6N + 1, NOP + 1) if mk(st, S6N, b) <= SPR.X10_FAIL_MB and cut_ok(b) and nact(S6N, b) <= MAXACT] or [None], key=lambda x: x or 0)   # noqa: E731
cut = lcut(START)
first_over = next((b for b in range(S6N + 1, NOP + 1) if mk(START, S6N, b) > SPR.X10_FAIL_MB), None)
first_cap = next((b for b in range(S6N + 1, NOP + 1) if nact(S6N, b) > MAXACT), None)
split_skipped = [b for b in range(S6N + 1, (first_over or NOP + 1)) if not cut_ok(b) and (cut is None or b > cut)]
gate("CUT longest prefix from op {0} splitting no 'of' group, <= {1} actions, with MAIN X10 <= {2} at {3}: op {4}".format(S6N + 1, MAXACT, SPR.X10_FAIL_MB, START, cut),
     cut is not None and cut >= S6N + 1 and cut_ok(cut) and mk(START, S6N, cut) <= SPR.X10_FAIL_MB and nact(S6N, cut) <= MAXACT,
     {"first_over": first_over, "first_over_40_actions": first_cap, "groups_split_at": split_skipped})
SENS = {}
for d in (-5.0, 0.0, 5.0):
    st = round(START + d, 1)
    c = lcut(st)
    SENS[str(d)] = {"start": st, "cut": c, "main_peak": c and mk(st, S6N, c), "exec_peak": c and pk(st, S6N, c), "actions": c and nact(S6N, c)}
    print("FACT SENS start {0} ({1:+} MB): cut op {2}, MAIN peak {3}, Executor peak {4}, actions {5}".format(st, d, c, SENS[str(d)]["main_peak"],
          SENS[str(d)]["exec_peak"], SENS[str(d)]["actions"]), flush=True)
print("FACT X10-MAIN at {0}: ops {1}..{2} MAIN peak {3} (Executor {4}; fail_above {5} margin {6}; MEMSTOP {7} margin {8}); next op {9} MAIN {10}; "
      "first op over 680: {11}; first op over {12} actions: {13}; group-split ops skipped above the cut {14}".format(
          START, S6N + 1, cut, mk(START, S6N, cut), pk(START, S6N, cut), SPR.X10_FAIL_MB, round(SPR.X10_FAIL_MB - mk(START, S6N, cut), 1), SX.MEM_STOP_MB,
          round(SX.MEM_STOP_MB - mk(START, S6N, cut), 1), cut + 1, mk(START, S6N, cut + 1), first_over, MAXACT, first_cap, split_skipped), flush=True)
nxt = max([b for b in range(cut + 1, NOP + 1) if mk(START, cut, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
print("FACT next session at the SAME start would end at op {0} (formula only)".format(nxt), flush=True)
for b in range(S6N + 1, min(NOP, (first_over or NOP) + 2) + 1):
    print("FACT X10-OP op {0} kind {1} bind {2} exec {3} main {4} cut_ok {5} actions {6}".format(b, OPS[b - 1]["kind"], b in BIND, pk(START, S6N, b), mk(START, S6N, b),
          cut_ok(b), nact(S6N, b)), flush=True)
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
json.dump(dict(TOP, stage="ring_p4_s07v18a", goal="card 150-a1-1 PASS A: P4 v18 session 7 (ops {0}..{1}), no open_rows".format(S6N + 1, cut),
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
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c150-a1-1: made by session-7 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c150-a1-1: open at step 0 = declared open row of plan_ring_p4_s06v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s07v18", goal=("RING P4 v18 LabVIEW session 7 (card 150-a1-1, RE-MADE at the measured s06 load, PD364(c)): v18 ops {0}..{1} "
               "({2} actions), cut so the MAIN recipe's X10 (Executor + source reads) <= 680 at the MEASURED start {3} (s06 load 593.8 + op-0), <= 40 actions, on "
               "session 6's SIMULATED end (plan cfbd9823; provisional -> stage_prerun --rebase onto the adopted s06 file's graph a3ecb92b)").format(S6N + 1, cut, len(keep), START),
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
json.dump({"card": "150-a1-1", "main_src_reads": MAIN_SRC_READS, "v18": {"path": rel(V18), "md5": md5(V18)}, "s06": {"path": rel(S06), "md5": md5(S06)},
           "ops": [S6N + 1, cut], "first": ids7[0], "last": ids7[-1], "actions": len(keep), "start_mb": START, "start_cite": START_CITE,
           "start_rule": "stage_prerun.x10_start(adopted s06 569ffbf5) = measured load 593.8 + op0_read_mb (PD352(b), s05 re-cut rule prep_c146_a1_2_mk.py)",
           "s06_ops": N6, "max_actions": MAXACT, "first_op_over_max_actions": first_cap,
           "exec_peak_mb": pk(START, S6N, cut), "main_peak_mb": mk(START, S6N, cut), "margin_mb": round(SPR.X10_FAIL_MB - mk(START, S6N, cut), 1),
           "memstop_margin_mb": round(SX.MEM_STOP_MB - mk(START, S6N, cut), 1), "next_op": cut + 1, "next_main_peak_mb": mk(START, S6N, cut + 1),
           "limit_mb": SPR.X10_FAIL_MB, "memstop_mb": SX.MEM_STOP_MB, "first_op_over_limit": first_over, "sensitivity": SENS,
           "next_session_cut_same_start": nxt, "x11_rows": x11, "subvi_drops": subv, "cross_refs": CROSS, "real_map": RMAP, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ops_total": NOP, "ops_left_after": rest, "kinds": dict(collections.Counter(o["kind"] for o in o7)),
           "kind_decisions": KD, "negctl": {"op": nk, "first_op": nfirst, "ok": nok, "why": nwhy}, "sink_gate_census": SGC,
           "v18e": {"v18_action": n_last, "s07_end_rows": len(e7), "v18_rows": len(e18), "cdiff": len(e7 ^ e18)}},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s06 / s05 / s04 / s03 / END step files / s05 map / s06 graph / memory_model untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
