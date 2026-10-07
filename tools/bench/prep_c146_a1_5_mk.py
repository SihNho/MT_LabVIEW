# ---
# labview: none
# hardware: none
# ---
r"""prep_c146_a1_5_mk - card 146-a1-5 step 1 (OFFLINE, no LabVIEW, never launched). P4 session 6 of plan v18 (2ea6cafa) = v18 ops 115..cut,
PROVISIONAL on session 5's SIMULATED end (plan_ring_p4_s05v18.json 1fc9b486, finalized last step sim/ring_p4_s05v18/step_21_create.json
ca3661f3); the --rebase onto the REAL s05 graph is a later card.
COPIED from prep_c146_a1_3_mk.py (8a0a8304) with:
  (1) s04 -> s05 (END4 -> END5, S4N -> S5N); made_prev = s01..s05 symbols; s05 symbols -> END5 sym (negative); s04 symbols -> s04v18 END sym
      (f349c39a step_23 b5ae7f79) -> s04's creation map (creation_map/plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl) -> REAL uid; s01..s03
      symbols -> s03 END sym -> s03's creation map (as before); (uid, class) checked against END5 and against the s05 rebase where it bound them;
  (2) START is PROVISIONAL (s05's file does not exist yet): predicted s05 load = load_by_vi[95e408ff] 605.4 + memory_model load_growth_mb_per_op
      0.719 (memory_model.json:70-73, 'used only to PREDICT an unsaved file's load') x the s05 plan's compiled op count (17), + op0_read_mb 5.9
      (the x10_start rule, stage_prerun.py:2043-2052);
  (3) the cut = the LONGEST prefix from op 115 that splits no 'of' group and whose MAIN-recipe X10 (Executor + 2 source census reads at read_mb,
      stage_prerun.py:2590-2593) <= 680 at START; the cut at START -5 / +5 MB is printed (sensitivity);
  (4) no prov copies (s06 is new); session table -> prep_c146_a1_5_session.json; card id / goal strings.
Existing tools checked: prep_c146_a1_3_mk.py (copied), stage_prerun.read_creation_map / x10_model_peak / load_memory_model, stagesim.simulate /
obj_class, stagexec.compile_plan; no new op, no tool edit.
PREDICTION CONTRACT: M0 input md5 == pins; X0 START = round(605.4 + 0.719*17 + 5.9, 1) = 623.5; S5 v18 ops 1..114 == s01..s05 ids; E5 END step file
  on its pin; CUT >= 115, splits no 'of' group, MAIN peak <= 680 (projection about op 130); R every s01..s04 symbol -> real uid, same class;
  C2 s05 refs negative, no later ref; SA pass A replays; TIE every end row tied; SB plan FINAL provisional, open_rows_match; X10s compiled
  plan peak == table at START; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c146_a1_5_mk.log -- py -u tools/bench/prep_c146_a1_5_mk.py"""
import collections, copy, hashlib, json, os, sys, traceback                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V18, S01, S02, S03, S04, S05 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02v18.json",
                                                              "plan_ring_p4_s03v18.json", "plan_ring_p4_s04v18.json", "plan_ring_p4_s05v18.json"))
END3F = os.path.join(SIM, "ring_p4_s03v18", "step_20_create.json")
END4F = os.path.join(SIM, "ring_p4_s04v18", "step_23_wire.json")
END5F = os.path.join(SIM, "ring_p4_s05v18", "step_21_create.json")
CMAP3 = os.path.join(B, "creation_map", "plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl")
CMAP4 = os.path.join(B, "creation_map", "plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl")
S6D = os.path.join(SIM, "ring_p4_s06v18")
D6 = os.path.join(S6D, "s05end")
PROVB = os.path.join(D6, "base_provisional.json")
PAROOT = os.path.join(S6D, "_passA")
DA = os.path.join(PAROOT, "ring_p4_s06v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s06v18a_in.json"), os.path.join(B, "plan_ring_p4_s06v18_in.json"), os.path.join(B, "plan_ring_p4_s06v18.json")
FACTS = os.path.join(B, "prep_c146_a1_5_session.json")
MAIN_SRC_READS = 2                       # main recipe source census_snapshot reads (prep_c146_a1_3_prerun.log:92-94, source 2)
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S05: "1fc9b486551b3f1fe42f25167375ba30", S04: "f349c39a17330531e688ff1f70ce426e",
        S03: "da66a0300851133d93881be3c28f2fdc", END5F: "ca3661f3e02bcac1749e1edcf0a1f018", END4F: "b5ae7f79975b9faca0722bb4dc6e3781",
        END3F: "5f31db45b1b8c7f66b48cf28d92a1e03"}
S04VI_MD5 = "95e408ff14a406edd3f16b32ba7324f1"
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
v18, s01, s02, s03, s04, s05 = J(V18), J(S01), J(S02), J(S03), J(S04), J(S05)
N5 = len(SX.compile_plan(s05))
LBV = (MODEL.get("load_by_vi") or {}).get(S04VI_MD5) or {}
GROW = float(MODEL["load_growth_mb_per_op"]["value"])
OP0 = float(MODEL["op0_read_mb"]["value"])
LOAD5 = round(float(LBV["value"]) + GROW * N5, 1)
START = round(float(LBV["value"]) + GROW * N5 + OP0, 1)
START_CITE = ("PROVISIONAL: predicted s05 file load {0} = load_by_vi[95e408ff] {1} (memory_model.json load_by_vi, diag_c145_2_graph.log:24) + "
              "load_growth_mb_per_op {2} (memory_model.json:70-73) x {3} compiled ops of plan_ring_p4_s05v18.json 1fc9b486; + op0_read_mb {4} "
              "(x10_start rule, stage_prerun.py:2043-2052). REPLACE by the s05 file's measured load at rebase").format(LOAD5, LBV["value"], GROW, N5, OP0)
gate("X0 PROVISIONAL start: load_by_vi[95e408ff] == 605.4; {0} compiled s05 ops; START {1} = 605.4 + {2} x {0} + {3}".format(N5, START, GROW, OP0),
     LBV.get("value") == 605.4 and N5 == 17 and START is not None, (LOAD5, START))
print("FACT X10 START {0} = {1}".format(START, START_CITE), flush=True)
print("FACT alt start by ACTIONS (21 s05 actions x {0}) = {1} (not used; the model is per op)".format(GROW, round(605.4 + GROW * len(s05["actions"]) + OP0, 1)), flush=True)
gate("E5 s05v18 finalized last step file == {0} (pinned md5); base real (not provisional)".format(rel(END5F)),
     s05["finalized"]["step_files"][-1]["path"] == rel(END5F) and s05["finalized"]["step_files"][-1]["md5"] == WANT[END5F]
     and not (s05.get("base") or {}).get("provisional"), s05["finalized"]["step_files"][-1])
END5, END4, END3 = J(END5F)["state"], J(END4F)["state"], J(END3F)["state"]
gate("E5b END5 state sym/neg present", isinstance(END5.get("sym"), dict) and isinstance(END5.get("neg"), int), (END5.get("sym"), END5.get("neg")))
os.makedirs(D6, exist_ok=True)
json.dump(END5, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)          # prep_c146_a1_3_mk.py:105
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END5.get("sym")), "neg", END5.get("neg"), "vi md5", END5.get("md5"), flush=True)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
prev3 = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]]
prev4 = prev3 + [x["id"] for x in s04["actions"]]
prev_ids = prev4 + [x["id"] for x in s05["actions"]]
S5N = max(act2op[n] for n in range(1, len(prev_ids) + 1))
gate("S5 v18 ops 1..{0} = s01's {1} + s02's {2} + s03's {3} + s04's {4} + s05's {5} ids".format(S5N, len(s01["actions"]), len(s02["actions"]),
     len(s03["actions"]), len(s04["actions"]), len(s05["actions"])),
     [ids[n - 1] for k in range(1, S5N + 1) for n in OPS[k - 1]["acts"]] == prev_ids and S5N == 114)
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
pk = lambda st, a, b: round(st + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
mk = lambda st, a, b: round(pk(st, a, b) + MAIN_SRC_READS * v("read_mb"), 1)                # noqa: E731  stage_prerun.py:2590-2593
lcut = lambda st: max([b for b in range(S5N + 1, NOP + 1) if mk(st, S5N, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)   # noqa: E731
cut = lcut(START)
first_over = next((b for b in range(S5N + 1, NOP + 1) if mk(START, S5N, b) > SPR.X10_FAIL_MB), None)
split_skipped = [b for b in range(S5N + 1, (first_over or NOP + 1)) if not cut_ok(b) and (cut is None or b > cut)]
gate("CUT longest prefix from op {0} splitting no 'of' group with MAIN X10 <= {1} at {2}: op {3}".format(S5N + 1, SPR.X10_FAIL_MB, START, cut),
     cut is not None and cut >= S5N + 1 and cut_ok(cut) and mk(START, S5N, cut) <= SPR.X10_FAIL_MB, {"first_over": first_over, "groups_split_at": split_skipped})
SENS = {}
for d in (-5.0, 0.0, 5.0):
    st = round(START + d, 1)
    c = lcut(st)
    SENS[str(d)] = {"start": st, "cut": c, "main_peak": c and mk(st, S5N, c), "exec_peak": c and pk(st, S5N, c), "actions": c and sum(len(OPS[k - 1]["acts"]) for k in range(S5N + 1, c + 1))}
    print("FACT SENS start {0} ({1:+} MB): cut op {2}, MAIN peak {3}, Executor peak {4}, actions {5}".format(st, d, c, SENS[str(d)]["main_peak"],
          SENS[str(d)]["exec_peak"], SENS[str(d)]["actions"]), flush=True)
print("FACT X10-MAIN at {0}: ops {1}..{2} MAIN peak {3} (Executor {4}; fail_above {5} margin {6}; MEMSTOP {7} margin {8}); next op {9} MAIN {10}; "
      "first op over: {11}; group-split ops skipped above the cut {12}".format(
          START, S5N + 1, cut, mk(START, S5N, cut), pk(START, S5N, cut), SPR.X10_FAIL_MB, round(SPR.X10_FAIL_MB - mk(START, S5N, cut), 1), SX.MEM_STOP_MB,
          round(SX.MEM_STOP_MB - mk(START, S5N, cut), 1), cut + 1, mk(START, S5N, cut + 1), first_over, split_skipped), flush=True)
nxt = max([b for b in range(cut + 1, NOP + 1) if mk(START, cut, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
print("FACT next session at the SAME start would end at op {0} (formula only)".format(nxt), flush=True)
for b in range(S5N + 1, min(NOP, (first_over or NOP) + 2) + 1):
    print("FACT X10-OP op {0} kind {1} bind {2} exec {3} main {4} cut_ok {5}".format(b, OPS[b - 1]["kind"], b in BIND, pk(START, S5N, b), mk(START, S5N, b), cut_ok(b)), flush=True)
ids6 = [ids[n - 1] for k in range(S5N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
subv = dict((SUBVI[i], {"op": act2op[pos[i]], "in_session": S5N < act2op[pos[i]] <= cut}) for i in SUBVI if i in pos)
rest = NOP - cut
X11OPS = {118: "p4_w_tp_row", 119: "p4_w_rp_row", 132: "p4_w_bd_row", 150: "p4_rbB_sel_t4168"}
x11 = dict((k, {"id": n, "v18_op_ids": [ids[m - 1] for m in OPS[k - 1]["acts"]], "in_s06": S5N < k <= cut}) for k, n in X11OPS.items())
print("FACT session 6 = {0} actions {1}..{2}; ops {3}..{4}; subVI drops {5}; ops left after s06 {6} of {7}".format(
      len(ids6), ids6[0], ids6[-1], S5N + 1, cut, subv, rest, NOP), flush=True)
print("FACT X11 #2626 rows by v18 op: {0}".format(json.dumps(x11)), flush=True)
made3 = set("new:" + x["as"] for x in s01["actions"] + s02["actions"] + s03["actions"] if x.get("as"))
made4s = set("new:" + x["as"] for x in s04["actions"] if x.get("as"))
made5s = set("new:" + x["as"] for x in s05["actions"] if x.get("as"))
made_prev = made3 | made4s | made5s
made6 = set("new:" + A[pos[i] - 1]["as"] for i in ids6 if A[pos[i] - 1].get("as"))
_h3, CM3, _s3 = SPR.read_creation_map(CMAP3)
_h4, CM4, _s4 = SPR.read_creation_map(CMAP4)
gate("CM s03 / s04 creation map headers == plans da66a030 / f349c39a", _h3.get("plan_md5") == WANT[S03] and _h4.get("plan_md5") == WANT[S04], (_h3, _h4))
inr = lambda r, made: r in made or r[:-1] in made                                          # noqa: E731


def real_of(sym):
    """s01..s04 symbol -> (real uid, sim id, map kind, sim class) via that session's END sym + its creation map (obj, diag, term)."""
    root = sym.split(".")[0]
    st, cm = (END4, CM4) if inr(root, made4s) else (END3, CM3)
    sid = st["sym"].get(sym)
    if not isinstance(sid, int):
        return None, sid, None, None
    for k in ("obj", "diag", "term"):
        if sid in cm[k]:
            return int(cm[k][sid]["real"]), sid, k, SS.obj_class(st, sid)
    return None, sid, None, None


s05by = dict((x["id"], x) for x in s05["actions"])
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
REB = collections.defaultdict(set)                                                           # how the s05 rebase bound s01..s04 symbols
for a in A[len(prev4):len(prev_ids)]:
    for f in UIDF + ADDRF:
        y = a.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if isinstance(s, str) and s.startswith("new:") and inr(s.split(".")[0], made3 | made4s):
            z = s05by[a["id"]].get(f)
            zu = z.get("uid") if isinstance(z, dict) else z
            REB[s if not (f in ADDRF and isinstance(y, str)) else s.split(".")[0]].add(zu)
CROSS, bad, RMAP = [], [], {}


def sub(x):                                                                                   # prep_c146_a1_3_mk.py:182-209, copied; s01..s04 -> REAL
    for f in UIDF + ADDRF:
        y = x.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if not inr(root, made_prev):
            continue
        key = root if (f in ADDRF and isinstance(y, str)) else s
        early = not inr(root, made5s)
        if early:
            u, sid, kind, csim = real_of(key)
            creal = SS.obj_class(END5, u) if isinstance(u, int) else None
            RMAP[key] = {"real": u, "sim": sid, "kind": kind, "class_sim": csim, "class_real": creal, "s05_rebase": sorted(REB.get(key) or [])}
            ok = isinstance(u, int) and u > 0 and creal is not None and (csim is None or csim == creal) and (not REB.get(key) or REB[key] == {u})
        else:
            u = END5["sym"].get(key)
            ok = isinstance(u, int) and u < 0
        if f in ADDRF and isinstance(y, str):
            x[f] = {"uid": u, "term": s.split(".", 1)[1]}
        elif isinstance(y, dict):
            x[f]["uid"] = u
        else:
            x[f] = u
        CROSS.append({"action": x["id"], "field": f, "symbol": s, "uid": u, "from": "s01-s04 real" if early else "s05 provisional"})
        ok or bad.append((x["id"], f, s, u))
    return x


keep = [sub(copy.deepcopy(A[pos[i] - 1])) for i in ids6]
for k in sorted(RMAP):
    print("FACT R {0} -> real #{1} (sim #{2}, map kind {3}); class sim {4} / real {5}; s05 rebase bound {6}".format(
          k, RMAP[k]["real"], RMAP[k]["sim"], RMAP[k]["kind"], RMAP[k]["class_sim"], RMAP[k]["class_real"], RMAP[k]["s05_rebase"]), flush=True)
gate("R {0} s01..s04 symbol(s) -> real uid by that session's creation map, (uid, class) equal in END5, == the s05 rebase where it bound them".format(len(RMAP)),
     all(isinstance(r["real"], int) and r["real"] > 0 and r["class_real"] is not None and (r["class_sim"] is None or r["class_sim"] == r["class_real"])
         and (not r["s05_rebase"] or r["s05_rebase"] == [r["real"]]) for r in RMAP.values()), RMAP)
late = [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), str) and x[f].startswith("new:") and not inr(x[f].split(".")[0], made6)]
late += [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), dict) and isinstance(x[f].get("uid"), str)
         and x[f]["uid"].startswith("new:") and not inr(x[f]["uid"].split(".")[0], made6)]
gate("C2 {0} cross ref(s): s05 symbols -> negative provisional uids, s01..s04 -> real uids {1}; no ref to a later session's symbol".format(
     len(CROSS), [(c["action"], c["symbol"], c["uid"]) for c in CROSS]), not bad and not late, {"bad": bad, "late": late[:8]})
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S05), "md5": md5(S05)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s06v18a", goal="card 146-a1-5 PASS A: P4 v18 session 6 (ops {0}..{1}), no open_rows".format(S5N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(AIN)))
try:
    SA = SS.simulate(AIN, PROVB, out_root=PAROOT, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "s05v18-open") for r in s05.get("open_rows") or [])
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
gate("TIE every end row ({0}) tied to a session-6 action or an s05v18 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c146-a1-5: made by session-6 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c146-a1-5: open at step 0 = declared open row of plan_ring_p4_s05v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s06v18", goal=("RING P4 v18 LabVIEW session 6 (card 146-a1-5, PROVISIONAL): v18 ops {0}..{1} ({2} actions), cut so the MAIN recipe's X10 "
               "(Executor + source reads) <= 680 at the PROVISIONAL start {3} (predicted s05 load), on session 5's SIMULATED end (plan 1fc9b486; provisional -> "
               "stage_prerun --rebase onto session 5's adopted file's graph)").format(S5N + 1, cut, len(keep), START),
               base=BASEREF, open_rows=orows, actions=keep), open(IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(OUT) if os.path.isfile(OUT) else {}
gate("SB plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"]})
o6 = SX.compile_plan(p)
cps6 = sorted({0, len(o6)} | set(k for k, o in enumerate(o6, 1) if o["kind"] in SX.BIND_KINDS))
mp = SPR.x10_model_peak([o["kind"] for o in o6], cps6, model=MODEL, start_mb=START)
kv, k6 = [o["kind"] for o in OPS[S5N:cut]], [o["kind"] for o in o6]
srx = [(S5N + 1 + j, OPS[S5N + j].get("reg")) for j in range(len(kv)) if j < len(k6) and kv[j] != k6[j]]
kinds_ok = len(kv) == len(k6) and all(kv[j] == k6[j] or (kv[j] == "wire_sr" and k6[j] == "connect" and inr(str(OPS[S5N + j].get("reg")), made_prev))
                                       for j in range(len(kv)))
print("FACT kind differences v18 -> s06 (op, v18 reg symbol): {0}".format(srx), flush=True)
print("FACT X10s compiled plan N {0} R {1} Executor peak {2}, MAIN {3} at {4}; MEMSTOP {5}".format(mp["N"], mp["R"], mp["peak_mb"],
      round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), START, SX.MEM_STOP_MB), flush=True)
gate("X10s compiled plan: Executor peak {0} == table {1}; MAIN {2} <= {3}; kinds == v18 ops {4}..{5} except wire_sr -> connect on an earlier register {6}".format(
     mp["peak_mb"], pk(START, S5N, cut), round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1), SPR.X10_FAIL_MB, S5N + 1, cut, srx),
     abs(mp["peak_mb"] - pk(START, S5N, cut)) < 0.05 and round(mp["peak_mb"] + MAIN_SRC_READS * v("read_mb"), 1) <= SPR.X10_FAIL_MB and kinds_ok,
     dict(collections.Counter(o["kind"] for o in o6)))
json.dump({"card": "146-a1-5", "main_src_reads": MAIN_SRC_READS, "v18": {"path": rel(V18), "md5": md5(V18)}, "s05": {"path": rel(S05), "md5": md5(S05)},
           "ops": [S5N + 1, cut], "first": ids6[0], "last": ids6[-1], "actions": len(keep), "start_mb": START, "start_cite": START_CITE,
           "start_rule": "PROVISIONAL predicted s05 load (load_growth_mb_per_op) + op0_read_mb", "pred_s05_load_mb": LOAD5, "s05_ops": N5,
           "exec_peak_mb": pk(START, S5N, cut), "main_peak_mb": mk(START, S5N, cut), "margin_mb": round(SPR.X10_FAIL_MB - mk(START, S5N, cut), 1),
           "memstop_margin_mb": round(SX.MEM_STOP_MB - mk(START, S5N, cut), 1), "next_op": cut + 1, "next_main_peak_mb": mk(START, S5N, cut + 1),
           "limit_mb": SPR.X10_FAIL_MB, "memstop_mb": SX.MEM_STOP_MB, "first_op_over_limit": first_over, "sensitivity": SENS,
           "next_session_cut_same_start": nxt, "x11_rows": x11, "subvi_drops": subv, "cross_refs": CROSS, "real_map": RMAP, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "ops_total": NOP, "ops_left_after": rest, "kinds": dict(collections.Counter(o["kind"] for o in o6))},
          open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s05 / s04 / s03 / END step files untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
