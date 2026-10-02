r"""prep_c141_p1_mk - card 141-P1 (OFFLINE, no LabVIEW, no COM, never launched). PD324(c)(d), judgement 141.
(1) v17 = v16 (36981c83) with ONE change: p4_eq_seq's $work donor #10171 (deleted by p4_do_10171, so X17 refuses v16) -> a bed Equal?
    node v16 never deletes. Candidates are COMPUTED: label 'Equal?' in main_vi_node_labels.json, an object of the bed graph, not a
    delete_object uid of v16 (prep_c141_p1_q1.log: #3812 #10019 #22284 #22731 #29111). Types: no terminal type of any candidate is
    in a measured file (grep of tools/bench/*type* empty; prep_c141_p1_q2.log lists their sources), so 'I32 preferred' is UNMEASURED
    for all five; PICK #10019 = the one Equal? with a MEASURED $work duplicate (create_primitive_nested -> class Comparison, terminals
    'x = y?' i0 / 'y' i1 / 'x' i2 == the plan's declared names; docs/NAMES.md:1387); its inputs are counters (x '# of Auto-Reset'
    .Value, y 'Limit of Program', prep_c141_p1_q2.log). v17 is FINALIZED by stagesim like v16 (prep_c141_1_mkv16.py skeleton, copied).
(2) Session 2 of v17 by PD320(c) (prep_c141_1_s01.py session-table code, copied): ops after session 1 (= plan_ring_p4_s01.json's 24
    actions, checked) up to the longest prefix with predicted X10 peak <= 675 at start 606.1 that splits no `of` pair / repair block.
    PROVISIONAL base = stagesim's END of plan_ring_p4_s01.json (f4831031) re-simulated on the bed graph (sim/ring_p4_s02_s01end);
    base {path, md5, provisional, sim_of: {plan_ring_p4_s01.json, f4831031}} = the --rebase contract (stage_prerun.py:3667-3682).
    Cross-session `new:` refs -> negative uids of that base, pass A / tie / pass B / pred = prep_c140_p1_s02.py (copied).
PREDICTION CONTRACT:
  M0 input md5 == card;  D candidates computed, #10019 among them, label 'Equal?';  A17 v17 == v16 except p4_eq_seq.donor.uid (+why);
  V17 validates;  R17 replay END (236 steps);  E17 end cdiff == v16's;  PS17 per-step cdiff == v16's summary per id;  RC17 route PASS;
  C17 compile ALL, ops == v16's;  RD17 route diff only on p4_eq_seq;  X17 PASS over all of v17;  O24 v17 #1..24 == s01's actions ==
  v16's;  MT meta17 stepped;  U v16/s01 untouched;  T session table on v17 == prep_c141_1_sessions.json table;  P0 s01 re-sim end rows
  == s01's finalized;  C1 s02 = ops 25..54 (p4_rp29048_dwo..p4_c_stopall_f), peak 675.0;  C2 cross refs -> negative uids;  SA/TIE/SB;
  X10s2 compiled peak == table;  X17s2 PASS;  SP pred written.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c141_p1_mk.log -- py -u tools/bench/prep_c141_p1_mk.py"""
import collections, copy, hashlib, json, os, shutil, sys, traceback                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR, census_predict as CPR      # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V16, META16 = os.path.join(B, "plan_ring_p4_v16.json"), os.path.join(B, "plan_ring_p4_v16_meta.json")
S01, S01PRED = os.path.join(B, "plan_ring_p4_s01.json"), os.path.join(B, "plan_ring_p4_s01_pred.json")
TAB16 = os.path.join(B, "prep_c141_1_sessions.json")
GRAPH, BEDPLAN = os.path.join(B, "graph_ring_p3b2b_20261002_133824.json"), os.path.join(B, "plan_ring_p3b2b.json")
EL = os.path.join(B, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
V17IN, V17, META17 = os.path.join(B, "plan_ring_p4_v17_in.json"), os.path.join(B, "plan_ring_p4_v17.json"), os.path.join(B, "plan_ring_p4_v17_meta.json")
SIM17 = os.path.join(SIM, "ring_p4_v17")
D1 = os.path.join(SIM, "ring_p4_s02_s01end")
B1IN, PROVB = os.path.join(D1, "plan_ring_p4_s02_s01end_in.json"), os.path.join(D1, "base_provisional.json")
DA = os.path.join(SIM, "ring_p4_s02a")
S2AIN, S2IN, S2P, PP = (os.path.join(DA, "plan_ring_p4_s02a_in.json"), os.path.join(B, "plan_ring_p4_s02_in.json"),
                        os.path.join(B, "plan_ring_p4_s02.json"), os.path.join(B, "plan_ring_p4_s02_pred.json"))
TAB17 = os.path.join(B, "prep_c141_p1_sessions.json")
WANT = {V16: "36981c838a0177a6a44cdd9edb8dc32f", META16: "1a169e10b2c16a4b2733a28ca58aa563", S01: "f4831031c738c997391b5bcace19d9f0",
        TAB16: "d9eb0d6cb66de4341e3ae7948047ef60", GRAPH: "50595c62d0332a94bf066538cf20c0ae"}
DONOR_PICK = 10019            # docs/NAMES.md:1387 - the measured $work Equal? duplicate (gated below to be a computed candidate)
LIMIT = 675.0
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:800]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


def sig(o):
    return json.dumps(dict((k, v) for k, v in o.items() if k not in ("acts", "in_act", "out_act", "of_act")), sort_keys=True, default=str)


def by_ids(ops, A):
    return dict((tuple(A[n - 1]["id"] for n in o["acts"]), sig(o)) for o in ops)


def tie_rows(S, keep, ok_pairs):
    """prep_c140_p1_s02.py:51-69 (copied)."""
    ties, untied = {}, []
    for key in S["end_cdiff_rows"]:
        n0 = S["steps"][-1]["n"]
        for s in reversed(S["steps"]):
            if s.get("cdiff_rows") is not None and key in s["cdiff_rows"]:
                n0 = s["n"]
            else:
                break
        p = (SS.V.key_parts(key)[0], SS.V.key_parts(key)[2])
        if n0 >= 1:
            a = keep[n0 - 1]
            ties[key] = {"n": n0, "id": a["id"], "op": a["op"], "class": a.get("class") or a["op"], "pair": p}
        elif p in ok_pairs:
            ties[key] = {"n": 0, "id": ok_pairs[p], "op": "base", "class": "step0-declared", "pair": p}
        else:
            untied.append((key, n0))
    return ties, untied


gate("M0 input md5 == card (v16, meta16, s01, sessions, bed graph)", all(md5(p) == w for p, w in WANT.items()), dict((os.path.basename(p), md5(p)) for p in WANT))
if G["fail"]:
    done()
v16, gr, LAB = J(V16), J(GRAPH), SPR.prim_donor_labels()
A16 = v16["actions"]
deleted = set(int(a["uid"]) for a in A16 if a.get("op") == "delete_object" and a.get("uid") is not None)
objs = set(int(o["uid"]) for o in gr["objs"])
CAND = sorted(u for u, l in LAB.items() if l == "Equal?" and u in objs and u not in deleted)
gate("D Equal? donors that survive v16 (label file x bed graph objs - v16 deletes): {0}; pick #{1} label {2!r} (NAMES.md:1387 measured $work duplicate)".format(
     CAND, DONOR_PICK, LAB.get(DONOR_PICK)), DONOR_PICK in CAND and LAB.get(DONOR_PICK) == "Equal?", {"deleted": sorted(deleted)})
if G["fail"]:
    done()
# ---------------------------------------------------------------- v17
A17 = copy.deepcopy(A16)
eq = next(a for a in A17 if a["id"] == "p4_eq_seq")
old_donor = dict(eq["donor"])
eq["donor"] = {"donor": "$work", "uid": DONOR_PICK}
eq["why"] = ("ROUTE create | PRECEDENT | card 141-P1 (PD324(c)): $work donor #{0} 'Equal?' (main_vi_node_labels.json; bed diagram 639; "
             "never deleted by the plan) replaces #10171 (deleted by p4_do_10171, X17); measured $work duplicate of #{0}: docs/NAMES.md:1387").format(DONOR_PICK)[:400]
chg = [(a["id"], [k for k in set(a) | set(b) if a.get(k) != b.get(k)]) for a, b in zip(A17, A16) if a != b]
gate("A17 v17 == v16 except p4_eq_seq donor (+why): {0}".format(chg), len(A17) == len(A16) and chg == [("p4_eq_seq", sorted(["donor", "why"]))]
     or (len(chg) == 1 and chg[0][0] == "p4_eq_seq" and set(chg[0][1]) == {"donor", "why"}), {"old": old_donor, "new": eq["donor"]})
raw = copy.deepcopy(v16)
raw["actions"] = A17
raw["base"] = {"path": v16["base"]["path"], "md5": v16["base"]["md5"]}
raw["goal"] = ("P4 v17 (card 141-P1, PD324(c)): v16 36981c83 with p4_eq_seq's $work donor #10171 (deleted by p4_do_10171) -> #{0} 'Equal?'; "
               "fs_routes regenerated; never launched").format(DONOR_PICK)
raw.pop("finalized", None)
raw.pop("final", None)
json.dump(raw, open(V17IN, "w", encoding="utf-8"), indent=1, default=str)
gate("V17 v17_in validates (stageplan/1)", *protocol.validate_obj(J(V17IN)))
if G["fail"]:
    done()
os.makedirs(SIM17, exist_ok=True)
S = None
try:
    S = SS.simulate(V17IN, GRAPH, out_root=SIM17, plan_out_dir=SIM17, log=lambda *x: None)
except Exception as e:                                                                          # noqa: BLE001
    print("SIM EXCEPTION", type(e).__name__, e)
    traceback.print_exc()
gate("S17 simulate returned", S is not None)
if S is None:
    done()
po = S["plan_out"]["path"]
po = po if os.path.isabs(po) else os.path.join(ROOT, po)
shutil.copyfile(po, V17)
v17 = J(V17)
fz = v17.get("finalized") or {}
fr = fz.get("fs_routes") or {}
badr = [(k, r.get("id"), A17[int(k) - 1]["id"]) for k, r in fr.items() if A17[int(k) - 1]["id"] != r.get("id")]
gate("FR17 v17 actions == A17; fs_routes regenerated ({0} keys) == v16's; base not provisional".format(len(fr)), v17["actions"] == A17 and bool(fr) and not badr
     and fr == (v16.get("finalized") or {}).get("fs_routes") and not (v17.get("base") or {}).get("provisional"), {"bad": badr})
steps = S.get("steps") or []
errs = [s for s in steps if s.get("error")]
gate("R17 replay END (base + {0} steps, no error)".format(len(A17)), not errs and len(steps) == len(A17) + 1,
     (len(steps), (errs[0].get("n"), errs[0].get("id"), str(errs[0].get("error"))[:400]) if errs else None))
fz16 = v16.get("finalized") or {}
end, end16 = set(S.get("end_cdiff_rows") or []), set(fz16.get("end_cdiff_rows") or [])
gate("E17 end cdiff rows == v16's ({0})".format(len(end16)), end == end16 and len(end16) == 24, sorted(end ^ end16))
sm16 = fz16["summary"]
gate("SM16 v16's summary file still on its pin", md5(os.path.join(ROOT, sm16["path"])) == sm16["md5"], sm16)
c16 = dict((s.get("id"), s.get("cdiff_rows")) for s in (J(sm16["path"]).get("steps") or []))
dif = [(s.get("n"), s.get("id")) for s in steps[1:] if c16.get(s.get("id")) != s.get("cdiff_rows")]
gate("PS17 per-step cdiff == v16's summary for every action id", not dif and len(c16) >= len(A17), dif[:6])
rc = fz.get("route_check") or {}
gate("RC17 route_check PASS", rc.get("status") == "PASS", rc.get("first_fail"))
try:
    o16, o17 = SX.compile_plan(v16), SX.compile_plan(v17)
except SX.ExecStop as e:
    gate("C17 compile_plan v16/v17", False, e)
    done()
m16, m17 = by_ids(o16, A16), by_ids(o17, A17)
diffs = sorted(set(k for k in set(m16) | set(m17) if m16.get(k) != m17.get(k)))
other = [k for k in diffs if "p4_eq_seq" not in k]
gate("C17 compile ALL: v17 ops {0} == v16 ops {1}; every action once".format(len(o17), len(o16)),
     len(o17) == len(o16) and sorted(n for o in o17 for n in o["acts"]) == list(range(1, len(A17) + 1)), (len(o16), len(o17)))
gate("RD17 route compare v16->v17: differing ops {0}, none without p4_eq_seq".format(diffs), not other, other[:6])
ok17, det17 = SPR.x17_gate([v17])
gate("X17 over the whole v17", ok17, det17)
s01 = J(S01)
gate("O24 v17 actions 1..24 == plan_ring_p4_s01.json's 24 actions == v16's", len(s01["actions"]) == 24 and A17[:24] == s01["actions"] == A16[:24],
     [a["id"] for a in s01["actions"]][:3])
meta = copy.deepcopy(J(META16))
nmeta = 0
for m in meta.get("actions") or []:
    if isinstance(m, dict) and m.get("id") == "p4_eq_seq":
        m["cite"] = "$work donor #{0} 'Equal?' (main_vi_node_labels.json; NAMES.md:1387) replaces #10171 deleted by p4_do_10171 [v17, card 141-P1]".format(DONOR_PICK)
        nmeta += 1
meta["recut_c141_p1"] = {"from_md5": md5(META16), "plan": "plan_ring_p4_v17.json", "changed": ["p4_eq_seq ($work donor #10171 -> #{0})".format(DONOR_PICK)],
                         "why": "PD324(c): X17 refused v16's p4_eq_seq ($work donor deleted earlier by p4_do_10171)"}
json.dump(meta, open(META17, "w", encoding="utf-8"), indent=1)
st = {}


def walk(o):
    if isinstance(o, dict):
        if "id" in o and "step" in o and "unit" in o:
            st[o["id"]] = (o["step"], o.get("session"))
        for v in o.values():
            walk(v)
    elif isinstance(o, list):
        for v in o:
            walk(v)


walk(J(META17))
gate("MT meta17: p4_eq_seq cite updated ({0} entry), every v17 id stepped".format(nmeta), nmeta == 1 and all(a["id"] in st for a in A17),
     [a["id"] for a in A17 if a["id"] not in st][:6])
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (V17, V17IN, META17))
print("V17 md5 {0} actions {1} ops {2}".format(md5(V17), len(A17), len(o17)), flush=True)
if G["fail"]:
    done()
# ---------------------------------------------------------------- session table on v17 (prep_c141_1_s01.py:59-107, copied)
A = A17
ids = [a["id"] for a in A]
OPS = o17
NOP = len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
MODEL = SPR.load_memory_model()
xs = SPR.x10_start(gr["md5"], MODEL)
START = xs[0]
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = []
for a in A:
    if a.get("of"):
        groups.append((act2op[pos[a["of"]]], act2op[pos[a["id"]]]))
for n in sorted(set(i.split("_")[1] for i in ids if i.startswith("p4_rp"))):
    groups.append((act2op[pos["p4_{0}_dwo".format(n)]], act2op[pos["p4_{0}_out".format(n)]]))
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731


def peak(a, b):
    reads = {a, b} | set(k for k in BIND if a < k <= b)
    return round(START + len(reads) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1), len(reads)


TABLE, a = [], 0
while a < NOP:
    best, b = None, a + 1
    while b <= NOP and peak(a, b)[0] <= LIMIT:
        if cut_ok(b):
            best = b
        b += 1
    if best is None:
        TABLE.append({"session": len(TABLE) + 1, "ops": [a + 1, None], "error": "no allowed cut <= {0}".format(LIMIT)})
        break
    pk, R_ = peak(a, best)
    acts = [n for k in range(a + 1, best + 1) for n in OPS[k - 1]["acts"]]
    TABLE.append({"session": len(TABLE) + 1, "ops": [a + 1, best], "first": ids[acts[0] - 1], "last": ids[acts[-1] - 1], "actions": len(acts),
                  "N": best - a, "R": R_, "start_mb": START, "peak_mb": pk, "kinds": dict(collections.Counter(OPS[k - 1]["kind"] for k in range(a + 1, best + 1)))})
    a = best
t16 = J(TAB16)["table"]
gate("T session table on v17 ({0} sessions) == prep_c141_1_sessions.json's (v16) table; start {1}".format(len(TABLE), START),
     TABLE == t16 and START == 606.1, [r for r, q in zip(TABLE, t16) if r != q][:2])
json.dump({"card": "141-P1", "plan": {"path": rel(V17), "md5": md5(V17)}, "ops": NOP, "actions": len(A), "start_mb": START, "start_cite": xs[1],
           "limit_mb": LIMIT, "groups": groups, "table": TABLE}, open(TAB17, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(TAB17), "md5": md5(TAB17)})
S1N, b = TABLE[0]["ops"][1], TABLE[1]["ops"][1]
ids1 = [ids[n - 1] for k in range(1, S1N + 1) for n in OPS[k - 1]["acts"]]
ids2 = [ids[n - 1] for k in range(S1N + 1, b + 1) for n in OPS[k - 1]["acts"]]
gate("C1 session 1 = s01's ids; session 2 = v17 ops {0}..{1} ({2}..{3}), {4} actions, N {5}, R {6}, peak {7} <= {8}".format(
     S1N + 1, b, ids2[0], ids2[-1], len(ids2), TABLE[1]["N"], TABLE[1]["R"], TABLE[1]["peak_mb"], LIMIT),
     ids1 == [x["id"] for x in s01["actions"]] and TABLE[1]["peak_mb"] <= LIMIT and cut_ok(S1N) and cut_ok(b), TABLE[1])
if G["fail"]:
    done()
# ---------------------------------------------------------------- provisional base = stagesim END of plan_ring_p4_s01.json
TOP = dict((k, copy.deepcopy(v17[k])) for k in ("schema", "context") if k in v17)
os.makedirs(D1, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s02_s01end", goal="card 141-P1: plan_ring_p4_s01.json (f4831031) actions re-simulated on the P3b-2b graph; its END = "
               "session 2's provisional base", base={"path": rel(GRAPH), "md5": md5(GRAPH)}, actions=copy.deepcopy(s01["actions"])),
          open(B1IN, "w", encoding="utf-8"), indent=1)
try:
    S1 = SS.simulate(B1IN, GRAPH, out_root=SIM, plan_out_dir=D1, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("P0 s01 re-simulate returned", False, ex)
    done()
bed_pairs = dict(((int(r["node"]), r["term"]), "bed") for r in J(BEDPLAN).get("open_rows") or [])
t1, u1 = tie_rows(S1, s01["actions"], bed_pairs) if S1["failed"] is None else ({}, ["not replayed"])
gate("P0 s01 re-sim replays to its end; end rows == s01's finalized ({0}); every row tied".format(len(S1.get("end_cdiff_rows") or [])),
     S1["failed"] is None and sorted(S1["end_cdiff_rows"]) == sorted(s01["finalized"]["end_cdiff_rows"]) and not u1, {"failed": S1["failed"], "untied": u1[:6]})
if G["fail"]:
    done()
END1 = J(S1["steps"][-1]["file"]["path"])["state"]
json.dump(END1, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END1.get("sym")), "neg", END1.get("neg"), flush=True)
ok_pairs = dict(bed_pairs, **dict((t["pair"], t["id"]) for t in t1.values() if t["n"] >= 1))
# ---------------------------------------------------------------- C2 cross-session refs (prep_c140_p1_s02.py:131-164, copied)
made1 = set("new:" + x["as"] for x in s01["actions"] if x.get("as"))
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
CROSS, bad = [], []


def sub(x):
    for f in UIDF + ADDRF:
        y = x.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if root not in made1 and root[:-1] not in made1:
            continue
        if f in ADDRF and isinstance(y, str):
            u = END1["sym"].get(root)
            x[f] = {"uid": u, "term": s.split(".", 1)[1]}
        elif isinstance(y, dict):
            u = END1["sym"].get(s)
            x[f]["uid"] = u
        else:
            u = END1["sym"].get(s)
            x[f] = u
        CROSS.append({"action": x["id"], "field": f, "symbol": s, "provisional_uid": u})
        (isinstance(u, int) and u < 0) or bad.append((x["id"], f, s, u))
    return x


keep2 = [sub(copy.deepcopy(x)) for x in A if x["id"] in ids2]
for c in CROSS:
    print("CROSS", json.dumps(c), flush=True)
late = [(x["id"], f) for x in A if x["id"] in ids2 for f in UIDF + ADDRF
        if isinstance(x.get(f), str) and x[f].startswith("new:") and x[f].split(".")[0] not in made1
        and not any(y.get("as") and "new:" + y["as"] == x[f].split(".")[0] for y in A if y["id"] in ids2)]
gate("C2 {0} session-2 ref(s) to session-1 symbols, each a negative uid of the provisional base; no ref to a LATER session's symbol".format(len(CROSS)),
     not bad and not late, {"bad": bad, "late": late[:6]})
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S01), "md5": md5(S01)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s02a", goal="card 141-P1 PASS A: P4 session 2 (v17 ops {0}..{1}), no open_rows".format(S1N + 1, b),
               base=BASEREF, actions=keep2), open(S2AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep2)), *protocol.validate_obj(J(S2AIN)))
try:
    SA = SS.simulate(S2AIN, PROVB, out_root=SIM, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
    done()
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
if G["fail"]:
    done()
ties, untied = tie_rows(SA, keep2, ok_pairs)
for k in sorted(ties):
    print("TIE", k, json.dumps(dict((x, y) for x, y in ties[k].items() if x != "pair")))
gate("TIE every end row tied to a session-2 action or to a step-0 pair (bed-declared / session-1 action)", not untied,
     {"untied": untied[:10], "own": sum(1 for t in ties.values() if t["n"] >= 1), "step0": sum(1 for t in ties.values() if t["n"] == 0)})
if G["fail"]:
    done()
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] in seen:
        continue
    seen.add(t["pair"])
    why = ("c141-P1 PD320: made by session-2 action {0} (#{1} {2} {3})".format(t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else
           "c141-P1 PD320: open at step 0 of session 2 = {0}".format("declared open row of plan_ring_p3b2b.json" if t["id"] == "bed"
                                                                      else "made by session-1 action " + t["id"]))
    orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": why[:300]})
json.dump(dict(TOP, stage="ring_p4_s02", goal="RING P4 LabVIEW session 2 (card 141-P1, PD320(c)(e), PD324(d)): v17 ops {0}..{1} ({2} actions) on session 1's "
               "SIMULATED end (provisional; stage_prerun --rebase onto session 1's saved in-between file)".format(S1N + 1, b, len(keep2)),
               base=BASEREF, open_rows=orows, actions=keep2), open(S2IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(S2IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p2 = J(S2P)
gate("SB session-2 plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p2.get("final") is True and (p2.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p2.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"], "base": p2.get("base")})
if G["fail"]:
    done()
ops2 = SX.compile_plan(p2)
bind2 = sorted(k for k, o in enumerate(ops2, 1) if o["kind"] in SX.BIND_KINDS)
cps = sorted(set([0, len(ops2)]) | set(bind2))
mp = SPR.x10_model_peak([o["kind"] for o in ops2], cps, model=MODEL, start_mb=START)
gate("X10s2 compiled session-2 plan at start {0}: N {1} R {2} peak {3} == table {4} <= {5}; kinds == v17 ops {6}..{7}".format(
     START, mp["N"], mp["R"], mp["peak_mb"], TABLE[1]["peak_mb"], LIMIT, S1N + 1, b), abs(mp["peak_mb"] - TABLE[1]["peak_mb"]) < 0.05
     and mp["peak_mb"] <= LIMIT and [o["kind"] for o in ops2] == [o["kind"] for o in OPS[S1N:b]], {"ops2": [o["kind"] for o in ops2]})
ok2, det2 = SPR.x17_gate([p2])
gate("X17s2 over session 2", ok2, det2)
rep = CPR.predict(p2, {}, J(os.path.join(B, "census_samples.json")))
p1pred = J(S01PRED)
gate("EL0 s01 pred keyed to s01 (plan md5 f4831031)", (p1pred.get("plan") or {}).get("md5") == WANT[S01], p1pred.get("plan"))
st0 = J(SB["steps"][0]["file"]["path"])["state"]
last = J(SB["steps"][-1]["file"]["path"])["state"]
madeu = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int))


def unwired_in(state):
    out = collections.defaultdict(list)
    for r in state["terminals"]:
        if not r.get("is_source") and not r.get("wire_uid") and r.get("term_class") != "ControlTerminal":
            out[int(r["owner_uid"])].append(r.get("term_name"))
    return out


u0, u2 = unwired_in(st0), unwired_in(last)
created_unw = sorted((u, u2[u]) for u in u2 if u in madeu)
base_new = sorted((u, u2[u]) for u in u2 if u not in madeu and u not in u0)
s1_total = p1pred["errorlist"]["predicted_total"]
print("EL session-1 predicted total", s1_total, "| s02-created nodes with an unwired input", created_unw, "| base nodes newly unwired", base_new, flush=True)
pred = {"schema": "ring-p3b-pred/1", "card": "141-P1", "note": "P4 LabVIEW session 2 (v17 ops {0}..{1}; in-between file, D-2026-10-02-02); PROVISIONAL base = "
        "session 1's simulated end - regenerate after stage_prerun --rebase onto session 1's saved file (start = its MEASURED load, PD320(d))".format(S1N + 1, b),
        "plan": {"path": rel(S2P), "md5": md5(S2P)}, "graph": {"path": rel(PROVB), "md5": md5(PROVB)}, "bed": END1.get("vi"), "bed_md5": END1.get("md5"),
        "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [p2["actions"][k - 1]["id"] for k in rep["unpredicted"]],
        "ops": [o["kind"] for o in ops2], "cdiff_rows": sorted(SB.get("end_cdiff_rows") or []), "cross_session_refs": CROSS,
        "row_ties": dict((k, dict((x, y) for x, y in t.items() if x != "pair")) for k, t in ties.items()),
        "errorlist": {"bed_total": s1_total, "new_items_predicted": len(created_unw), "predicted_total": s1_total + len(created_unw),
                      "alternative_total": s1_total + len(created_unw) + len(base_new),
                      "created_nodes_unwired_input": [[u, n] for u, n in created_unw], "base_nodes_newly_unwired": [[u, n] for u, n in base_new],
                      "rule": "PD322(e) per created node; base = session 1's PREDICTED total (plan_ring_p4_s01_pred.json) - re-derive from session 1's "
                              "measured Error List at rebase", "base_file": rel(S01PRED), "checked": False},
        "memory_pred": {"card": "141-P1", "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind2, "op_kinds": [o["kind"] for o in ops2],
                        "start_mb": START, "start_cite": "PD320(c) planning start 606.1 = bed load 600.2 + op-0 5.9; REPLACE by session 1 file's measured load "
                        "+ op-0 at rebase (PD320(d))", "peak_mb": mp["peak_mb"], "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"],
                        "card_limit_mb": LIMIT, "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
        "session_table": {"path": rel(TAB17), "md5": md5(TAB17)}, "summary": (p2.get("finalized") or {}).get("summary")}
json.dump(pred, open(PP, "w", encoding="utf-8"), indent=1)
print("FACT s02 ops", dict(collections.Counter(pred["ops"])), "census", pred["census"], "unpredicted", len(pred["census_unpredicted"]),
      "| EL", pred["errorlist"]["predicted_total"], "alt", pred["errorlist"]["alternative_total"], "| end rows", len(pred["cdiff_rows"]), "open pairs", len(orows), flush=True)
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (B1IN, PROVB, S2IN, S2P, PP))
gate("SP pred written: ops == compile, each action once", sorted(n for o in ops2 for n in o["acts"]) == list(range(1, len(keep2) + 1)), len(ops2))
gate("U v16 / meta16 / s01 untouched", md5(V16) == WANT[V16] and md5(META16) == WANT[META16] and md5(S01) == WANT[S01])
done()
