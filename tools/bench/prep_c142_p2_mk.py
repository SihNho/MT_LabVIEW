r"""prep_c142_p2_mk - card 142-P2 (OFFLINE, no LabVIEW, no COM, never launched). PD330(a)/(e), brief_142-P2.md.
v18 = v17 (e19d7e14) with the S1 group (G2 minus p4_or_w1) and the S2 group (G5's scalar core) each replaced by ONE `create` class
SubVI (stagexec route `subvi`, stagexec.py:438-441 needs `subvi_path` + declared `terminals`; stagesim models it by the GENERIC
create path, stagesim.py:2092,2156-2165: the plan's declared terminal list, the file is never read). Boundary wires re-pointed by
terminal NAME; a boundary wire that only duplicated an input the subVI now takes once (LRN4 -> For tunnel; TN1.outer branches into
GT2.x / SLL1.t; SD1L.inner branch into SLD1.t) is removed. Existing tools reused (nothing rebuilt): stagesim.simulate / graph /
obj_class, stagexec.compile_plan / BIND_KINDS, stage_prerun.load_memory_model / X10_FAIL_MB, the session-table loop of
prep_c141_p1_mk.py:207-247 (copied). S1 terminals = MEASURED: build_ringpickslot_v2.log pane read-back (11 Num, 10 last, 3 min Num,
2 min slot, 1 found, others free) + bed graph rows show a subVI's unassigned pane slots as '' sinks with wire 0 (graph_ring_p4s01
owner #30804 / #4620) -> 12 rows. S2 terminals = PROVISIONAL (card 142-4 builds RingSeqCheck_v0.vi now): only the 8 named ones.
PREDICTION CONTRACT:
  M0 input md5 == card, RingPickSlot_v0.vi md5 6fcf153f, v17's end step file on its pin;  R removed = 19 (S1) + 16 (S2) = 35, added 2,
  v18 = 202 actions; re-pointed 5 (S1) + 14 (S2);  DEP no kept action names a removed alias;  V v18_in validates;  RP replay END
  (203 steps, no error);  E end cdiff rows == v17's;  ED end-graph edges v17 vs v18 differ only on edges touching a removed alias,
  PS1/SQ1 or an alias-less new object;  C compile_plan v18, every action once;  X10 session table of the non-repair part at 596.5.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c142_p2_mk.log -- py -u tools/bench/prep_c142_p2_mk.py"""
import collections, copy, hashlib, json, os, shutil, sys, traceback                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V17 = os.path.join(B, "plan_ring_p4_v17.json")
GRAPH = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json")
CDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
PS_VI, SQ_VI = os.path.join(CDEV, "RingPickSlot_v0.vi"), os.path.join(CDEV, "RingSeqCheck_v0.vi")
V18IN, V18, META18 = (os.path.join(B, n) for n in ("plan_ring_p4_v18_in.json", "plan_ring_p4_v18.json", "plan_ring_p4_v18_meta.json"))
SIM18 = os.path.join(SIM, "ring_p4_v18")
TAB = os.path.join(B, "prep_c142_p2_sessions.json")
WANT = {V17: "e19d7e142fef66f9e118ae4061e9e718", os.path.join(B, "cards", "brief_142-P2.md"): "06ef76b82887dbd24136ee793975ba03",
        os.path.join(B, "prep_c142_p1_subvi_table.md"): "2e032d3c8923131ebcc8f7e8b8933e5e",
        os.path.join(B, "build_ringpickslot_v2.log"): "4337475f29bafa7b719597fa966b2cb0", GRAPH: "50595c62d0332a94bf066538cf20c0ae",
        PS_VI: "6fcf153f7b8fecda727f5dcf944faab9"}
START = 596.5
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


gate("M0 input md5 == card; RingPickSlot_v0.vi 6fcf153f", all(os.path.isfile(p) and md5(p) == w for p, w in WANT.items()),
     dict((os.path.basename(p), md5(p) if os.path.isfile(p) else None) for p in WANT))
v17 = J(V17)
ls17 = v17["finalized"]["last_step"]
gate("M1 v17 end step file on its pin", md5(os.path.join(ROOT, ls17["path"])) == ls17["md5"], ls17)
print("FACT v17 final {0} | failed {1} | open_rows_match {2} | undecided {3} | route_check {4}".format(
      v17.get("final"), v17["finalized"].get("failed"), v17["finalized"].get("open_rows_match"), v17["finalized"].get("undecided"),
      (v17["finalized"].get("route_check") or {}).get("status")), flush=True)
print("FACT RingSeqCheck_v0.vi exists now: {0}".format(os.path.isfile(SQ_VI)), flush=True)
if G["fail"]:
    done()
A17 = v17["actions"]
ix = dict((a["id"], n) for n, a in enumerate(A17))
# ------------------------------------------------------------------ S1 / S2 action sets (prep_c142_p1_subvi_table.md:33-42, 70-...)
S1_NODES = ["p4_gt_last", "p4_f_min", "p4_sel_mask", "p4_k_max", "p4_k_max_found", "p4_amm", "p4_lt_found"]
S1_INNER = ["p4_t_fnum", "p4_t_fnum_out", "p4_t_fgt", "p4_t_fgt_in", "p4_t_fgt_out", "p4_w_max_sel", "p4_t_fsel", "p4_t_fsel_in",
            "p4_t_fsel_out", "p4_w_min_lt", "p4_w_max_lt"]
S1_DUP = ["p4_t_fnum_in"]                      # LRN4.value -> TFN1.outer: Num enters the subVI once (p4_w_num_gt)
S2_NODES = ["p4_eq_seq", "p4_gt_n1", "p4_and", "p4_dec", "p4_sel_last", "p4_sel_disc", "p4_inc_disc"]
S2_INNER = ["p4_w_eq_and", "p4_w_gt_and", "p4_w_dec_sel", "p4_w_and_sel", "p4_w_inc_sel", "p4_w_and_seld"]
S2_DUP = ["p4_w_n1_gt", "p4_w_n1_sel", "p4_w_disc_sel"]   # n1 and discards enter the subVI once
REMOVE = S1_NODES + S1_INNER + S1_DUP + S2_NODES + S2_INNER + S2_DUP
# re-points: id -> (field, new address)
RE1 = {"p4_t_last_out": ("dst", "new:PS1.last"), "p4_w_num_gt": ("dst", "new:PS1.Num"), "p4_w_lt_or": ("src", "new:PS1.found"),
       "p4_t_n1_in": ("src", "new:PS1.min Num"), "p4_t_slot_in": ("src", "new:PS1.min slot")}
RE2 = {"p4_w_last_gt": ("dst", "new:SQ1.last"), "p4_t_n1_out": ("dst", "new:SQ1.n1"), "p4_w_lat_dec": ("dst", "new:SQ1.Latest"),
       "p4_w_sel_last": ("src", "new:SQ1.next last"), "p4_w_disc_inc": ("dst", "new:SQ1.discards"),
       "p4_w_seld_r": ("src", "new:SQ1.next discards"), "p4_x_n2_out": ("dst", "new:SQ1.n2")}
for k in "ABCDEFR":
    RE2["p4_rb{0}_s".format(k)] = ("src", "new:SQ1.valid")
missing = [i for i in REMOVE + list(RE1) + list(RE2) if i not in ix]
gate("R0 every named id is in v17 ({0} remove, {1} re-point)".format(len(REMOVE), len(RE1) + len(RE2)), not missing, missing)
if G["fail"]:
    done()
gone_alias = set()
for i in REMOVE:
    a = A17[ix[i]]
    if a.get("as"):
        gone_alias.add(a["as"])
print("FACT removed aliases:", sorted(gone_alias), flush=True)
TERM = lambda n, s: {"name": n, "is_source": s, "term_class": "Terminal"}                   # noqa: E731
# RingPickSlot_v0 pane slots 0..11 (build_ringpickslot_v2.log pane read back): 1 found, 2 min slot, 3 min Num, 10 last, 11 Num
PS_T = []
for slot in range(12):
    nm = {1: "found", 2: "min slot", 3: "min Num", 10: "last", 11: "Num"}.get(slot, "")
    PS_T.append(TERM(nm, slot in (1, 2, 3)))
SQ_T = [TERM("n1", False), TERM("n2", False), TERM("last", False), TERM("Latest", False), TERM("discards", False),
        TERM("next last", True), TERM("next discards", True), TERM("valid", True)]
PS = {"op": "create", "id": "p4_s1_pickslot", "class": "SubVI", "diagram": A17[ix["p4_gt_last"]]["diagram"], "as": "PS1",
      "subvi_path": PS_VI, "terminals": PS_T,
      "why": ("ROUTE subvi (drop_subvi, stagexec.py:438-441,3047-3054) | MEASURED terminals | PD330(a) S1 RingPickSlot_v0.vi md5 6fcf153f "
              "(card 142-3, build_ringpickslot_v2.log 87/0: pane 11 Num, 10 last, 3 min Num, 2 min slot, 1 found; unassigned slots '' sinks "
              "as bed SubVI rows) replaces p4_gt_last..p4_lt_found + their For/wires (prep_c142_p1_subvi_table.md G2 minus p4_or_w1)")[:400]}
SQ = {"op": "create", "id": "p4_s2_seqcheck", "class": "SubVI", "diagram": A17[ix["p4_eq_seq"]]["diagram"], "as": "SQ1",
      "subvi_path": SQ_VI, "terminals": SQ_T,
      "why": ("ROUTE subvi (drop_subvi) | PROVISIONAL terminals: names n1 n2 last Latest discards / next last, next discards, valid "
              "from brief_142-P2.md; card 142-4 builds RingSeqCheck_v0.vi now (pane slots + unassigned '' rows unread) | PD330(a) S2 "
              "replaces p4_eq_seq..p4_inc_disc + inner wires (G5 scalar core)")[:400]}
A18, repointed = [], []
for a in A17:
    i = a["id"]
    if i == "p4_gt_last":
        A18.append(PS)
        continue
    if i == "p4_eq_seq":
        A18.append(SQ)
        continue
    if i in REMOVE:
        continue
    b = copy.deepcopy(a)
    if i in RE1 or i in RE2:
        f, new = (RE1.get(i) or RE2.get(i))
        old = b[f]
        b[f] = new
        b["why"] = ("c142-P2 re-pointed {0} {1} -> {2} (PD330(a) subVI terminal by name) | {3}".format(f, old, new, a.get("why") or ""))[:400]
        repointed.append((i, f, old, new))
    A18.append(b)
for r in repointed:
    print("REPOINT", r, flush=True)
gate("R removed {0} = S1 {1} + S2 {2}; added 2; v18 {3} actions (v17 {4}); re-pointed {5} = S1 {6} + S2 {7}".format(
     len(REMOVE), len(S1_NODES + S1_INNER + S1_DUP), len(S2_NODES + S2_INNER + S2_DUP), len(A18), len(A17), len(repointed),
     len(RE1), len(RE2)), len(REMOVE) == 35 and len(A18) == len(A17) - 35 + 2 == 202 and len(repointed) == 19)
txt = [(b["id"], s) for b in A18 for s in sorted(gone_alias) if ('"new:' + s + '.') in json.dumps(b) or ('"new:' + s + '"') in json.dumps(b)]
gate("DEP no kept action names a removed alias", not txt, txt[:10])
if G["fail"]:
    done()
raw = copy.deepcopy(v17)
raw["actions"] = A18
raw["base"] = {"path": v17["base"]["path"], "md5": v17["base"]["md5"]}
raw["goal"] = ("P4 v18 (card 142-P2, PD330(a)): v17 e19d7e14 with S1 (G2 minus p4_or_w1) -> SubVI RingPickSlot_v0.vi and S2 (G5 scalar core) "
               "-> SubVI RingSeqCheck_v0.vi (S2 terminals PROVISIONAL); never launched")
raw.pop("finalized", None)
raw.pop("final", None)
json.dump(raw, open(V18IN, "w", encoding="utf-8"), indent=1, default=str)
gate("V v18_in validates (stageplan/1)", *protocol.validate_obj(J(V18IN)))
if G["fail"]:
    done()
os.makedirs(SIM18, exist_ok=True)
S = None
try:
    S = SS.simulate(V18IN, GRAPH, out_root=SIM18, plan_out_dir=SIM18, log=lambda *x: None)
except Exception as e:                                                                          # noqa: BLE001
    traceback.print_exc()
    gate("S simulate returned", False, "{0}: {1}".format(type(e).__name__, e))
    done()
steps = S.get("steps") or []
errs = [s for s in steps if s.get("error")]
gate("RP replay END (base + {0} steps, no error)".format(len(A18)), not errs and len(steps) == len(A18) + 1,
     (len(steps), (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:600]) if errs else None))
if G["fail"]:
    done()
po = S["plan_out"]["path"]
po = po if os.path.isabs(po) else os.path.join(ROOT, po)
shutil.copyfile(po, V18)
v18 = J(V18)
fz = v18["finalized"]
print("FACT v18 final {0} | open_rows_match {1} | undecided {2} | route_check {3} {4} | fs_border_gate {5}".format(
      v18.get("final"), fz.get("open_rows_match"), fz.get("undecided"), (fz.get("route_check") or {}).get("status"),
      str((fz.get("route_check") or {}).get("first_fail"))[:400], (fz.get("fs_border_gate") or {}).get("status")), flush=True)
end18, end17 = set(S.get("end_cdiff_rows") or []), set(v17["finalized"].get("end_cdiff_rows") or [])
gate("E end cdiff rows v18 == v17's ({0} vs {1})".format(len(end18), len(end17)), end18 == end17, {"only18": sorted(end18 - end17), "only17": sorted(end17 - end18)})
# ------------------------------------------------------------------ ED: end-graph edges, new objects named by alias
st17 = J(ls17["path"])["state"]
st18 = S["_state"]


def edges(st):
    inv = {}
    for k, u in sorted(st["sym"].items(), key=lambda kv: len(kv[0])):
        inv.setdefault(u, k)
    Gs = SS.graph(st)
    nm = lambda u: u if u >= 0 else (inv.get(u) or "NEW:{0}".format(SS.obj_class(st, u)))       # noqa: E731
    out = collections.Counter()
    for k, a, b, _i in Gs["edges"]:
        pa, pb = SS.V.key_parts(a), SS.V.key_parts(b)
        out[(k, nm(int(pa[0])), pa[2], pa[3] if len(pa) > 3 else 0, nm(int(pb[0])), pb[2], pb[3] if len(pb) > 3 else 0)] += 1
    return out


e17, e18 = edges(st17), edges(st18)
only17, only18 = sorted((e17 - e18).elements(), key=repr), sorted((e18 - e17).elements(), key=repr)
expect = gone_alias | {"PS1", "SQ1"}
# run 1 (10:08) FAILED this gate on the checker itself: sym keys carry the 'new:' prefix ('new:AMM1'), so no edge matched;
# the log's ED lines show 126/127 name a removed alias / PS1 / SQ1 and the 127th is FMN1's count Tunnel (thru, alias-less)
touch = lambda e: any(isinstance(x, str) and (x.split(":", 1)[-1].split(".")[0] in expect) for x in (e[1], e[4]))       # noqa: E731
anon = lambda e: any(isinstance(x, str) and x.startswith("NEW:") for x in (e[1], e[4]))              # noqa: E731
other = [e for e in only17 + only18 if not touch(e)]
for e in only17:
    print("ED only17", e, flush=True)
for e in only18:
    print("ED only18", e, flush=True)
gate("ED end edges v17 {0} / v18 {1}: {2} only in v17, {3} only in v18; every one touches a removed alias / PS1 / SQ1 ({4} do not, "
     "{5} of them alias-less new objects)".format(sum(e17.values()), sum(e18.values()), len(only17), len(only18), len(other),
                                                  len([e for e in other if anon(e)])), not [e for e in other if not anon(e)], other[:12])
# ------------------------------------------------------------------ C: compile
try:
    o18 = SX.compile_plan(v18)
except SX.ExecStop as e:
    gate("C compile_plan v18", False, e)
    done()
o17 = SX.compile_plan(v17)
gate("C compile_plan v18: {0} ops (v17 {1}); every action once".format(len(o18), len(o17)),
     sorted(n for o in o18 for n in o["acts"]) == list(range(1, len(A18) + 1)))
for k, o in enumerate(o18, 1):
    if any(A18[n - 1]["id"] in ("p4_s1_pickslot", "p4_s2_seqcheck") or A18[n - 1]["id"] in RE1 or A18[n - 1]["id"] in RE2 for n in o["acts"]):
        print("OP {0} {1} {2}".format(k, o["kind"], [A18[n - 1]["id"] for n in o["acts"]]), flush=True)
print("FACT op kinds v17", dict(collections.Counter(o["kind"] for o in o17)), flush=True)
print("FACT op kinds v18", dict(collections.Counter(o["kind"] for o in o18)), flush=True)
# ------------------------------------------------------------------ X10 session table, non-repair part (prep_c141_p1_mk.py:207-247)
ids = [a["id"] for a in A18]
NOP = len(o18)
act2op = dict((n, k) for k, o in enumerate(o18, 1) for n in o["acts"])
BIND = set(k for k, o in enumerate(o18, 1) if o["kind"] in SX.BIND_KINDS)
MODEL = SPR.load_memory_model()
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
pos = dict((i, k) for k, i in enumerate(ids, 1))
rep_ops = sorted(set(act2op[pos[i]] for i in ids if i.startswith("p4_rp")))
A0 = max(rep_ops)
mixed = [k for k in range(1, A0 + 1) if any(not ids[n - 1].startswith("p4_rp") for n in o18[k - 1]["acts"])]
gate("XR repair actions = ops 1..{0}, none mixed with a non-repair action".format(A0), rep_ops == list(range(1, A0 + 1)) and not mixed, mixed)
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A18 if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731


def peak(a, b):
    reads = {a, b} | set(k for k in BIND if a < k <= b)
    return round(START + len(reads) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1), len(reads)


def table(limit):
    T, a = [], A0
    while a < NOP:
        best, b = None, a + 1
        while b <= NOP and peak(a, b)[0] <= limit:
            if cut_ok(b):
                best = b
            b += 1
        if best is None:
            T.append({"session": len(T) + 1, "ops": [a + 1, None], "error": "no allowed cut <= {0}".format(limit)})
            break
        pk, R_ = peak(a, best)
        acts = [n for k in range(a + 1, best + 1) for n in o18[k - 1]["acts"]]
        T.append({"session": len(T) + 1, "ops": [a + 1, best], "first": ids[acts[0] - 1], "last": ids[acts[-1] - 1], "actions": len(acts),
                  "N": best - a, "R": R_, "start_mb": START, "peak_mb": pk,
                  "kinds": dict(collections.Counter(o18[k - 1]["kind"] for k in range(a + 1, best + 1)))})
        a = best
    return T


T680, T675 = table(SPR.X10_FAIL_MB), table(675.0)
for lim, T in ((SPR.X10_FAIL_MB, T680), (675.0, T675)):
    for r in T:
        print("X10 limit {0} | {1}".format(lim, json.dumps(r)), flush=True)
json.dump({"card": "142-P2", "plan": {"path": rel(V18), "md5": md5(V18)}, "ops": NOP, "non_repair_from_op": A0 + 1, "actions": len(A18),
           "start_mb": START, "start_cite": "docs/d1/ring-p4b.md:78,84 (load 596.5 MB of D1_ring_p4s01, PD320(d))",
           "model": dict((k, v(k)) for k in ("read_mb", "edit_mb", "other_mb", "final_read_mb")),
           "groups": groups, "table_680": T680, "table_675": T675}, open(TAB, "w", encoding="utf-8"), indent=1)
gate("X10 session table at {0}: {1} sessions at {2} (memory_model fail_above_mb), {3} at 675; no session without a cut".format(
     START, len(T680), SPR.X10_FAIL_MB, len(T675)), all("error" not in r for r in T680 + T675))
json.dump({"schema": "p4v18-meta/0", "card": "142-P2", "from_v17": {"path": rel(V17), "md5": md5(V17)},
           "removed": REMOVE, "repointed": [list(r) for r in repointed], "added": ["p4_s1_pickslot", "p4_s2_seqcheck"],
           "provisional": {"action": "p4_s2_seqcheck", "subvi_path": SQ_VI, "terminals": [t["name"] for t in SQ_T],
                           "addresses": [r[3] for r in repointed if r[3].startswith("new:SQ1.")],
                           "why": "card 142-4 builds RingSeqCheck_v0.vi now; names from brief_142-P2.md, pane unread"},
           "measured": {"action": "p4_s1_pickslot", "subvi_md5": WANT[PS_VI], "cite": "tools/bench/build_ringpickslot_v2.log pane read back"},
           "counts": {"v17_actions": len(A17), "v18_actions": len(A18), "v17_ops": len(o17), "v18_ops": len(o18)}},
          open(META18, "w", encoding="utf-8"), indent=1)
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (V18, V18IN, META18, TAB))
gate("U v17 untouched", md5(V17) == WANT[V17])
print("V18 md5 {0} actions {1} ops {2}".format(md5(V18), len(A18), len(o18)), flush=True)
done()
