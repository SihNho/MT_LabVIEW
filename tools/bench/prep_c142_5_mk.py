r"""prep_c142_5_mk - card 142-5 pass 2 (OFFLINE, no LabVIEW, never launched). PD330(d)/PD331(d): P4 session 2 of plan v18
(2ea6cafa) = v18 ops 25..cut, cut = the longest prefix after s01 (ops 1..24) that splits no 'of' group with X10 <= memory_model
fail_above_mb (680) at start 596.5 (session 1 file's measured load, PD326(a)). Planned on the SAME provisional base as rasrest/s02
(stagesim END of s01 f4831031 = 2d0c2c99) so `stage_prerun --rebase ... --graph graph_ring_p4s01_20261002_234419.json` binds s01's
objects (rebind key fixed by this card). Route COPIED, not rebuilt: prep_c141_p1_mk.py:284-360 (cross refs via END1.sym, pass A /
tie / pass B) and prep_c142_p2_mk.py:236-262 (cut_ok, peak); s02's step-0 open rows reused (prep_c142_p1_mk.py:135-137).
PREDICTION CONTRACT: M0 input md5 == card; S1 v18 ops 1..24 == s01's ids; RR v18 #25..#50 after cross-ref == rasrest's 26 actions;
  CUT cut found, peak <= 680; C2 cross refs to s01 symbols -> negative uids of the provisional base; SA pass A replays to end;
  TIE every end row tied; SB plan FINAL provisional, open_rows_match; X10s compiled plan peak == table; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c142_5_mk.log -- py -u tools/bench/prep_c142_5_mk.py"""
import collections, copy, hashlib, json, os, sys, traceback                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V18, S01, S02, RAS = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02.json", "plan_ring_p4_rasrest.json"))
PROVB, BEDPLAN = os.path.join(SIM, "ring_p4_s02_s01end", "base_provisional.json"), os.path.join(B, "plan_ring_p3b2b.json")
DA = os.path.join(SIM, "ring_p4_s02v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s02v18a_in.json"), os.path.join(B, "plan_ring_p4_s02v18_in.json"), os.path.join(B, "plan_ring_p4_s02v18.json")
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S01: "f4831031c738c997391b5bcace19d9f0", S02: "5e483ea6ccf9897f37da71b975bcde29",
        RAS: "4ad2d288", PROVB: "2d0c2c99a5525713edd638f89229e028"}
START = 596.5
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


gate("M0 input md5 == card", all(md5(p).startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), md5(p)) for p in WANT))
v18, s01, s02, ras, END1 = J(V18), J(S01), J(S02), J(RAS), J(PROVB)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
S1N = max(act2op[n] for n in range(1, len(s01["actions"]) + 1))
gate("S1 v18 ops 1..{0} = s01's {1} ids".format(S1N, len(s01["actions"])), [ids[n - 1] for k in range(1, S1N + 1) for n in OPS[k - 1]["acts"]]
     == [x["id"] for x in s01["actions"]])
MODEL = SPR.load_memory_model()
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
peak = lambda a, b: round(START + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
cut = max([b for b in range(S1N + 1, NOP + 1) if peak(S1N, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
gate("CUT ops {0}..{1}: peak {2} <= {3} at start {4}; op {5} would be {6}".format(S1N + 1, cut, cut and peak(S1N, cut), SPR.X10_FAIL_MB, START,
     cut and cut + 1, cut and cut < NOP and peak(S1N, cut + 1)), cut is not None)
ids2 = [ids[n - 1] for k in range(S1N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
print("FACT session 2 = {0} actions {1}..{2}; groups {3}".format(len(ids2), ids2[0], ids2[-1], groups), flush=True)
made1 = set("new:" + x["as"] for x in s01["actions"] if x.get("as"))
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
CROSS, bad = [], []


def sub(x):                                                                                   # prep_c141_p1_mk.py:290-310, copied
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


keep = [sub(copy.deepcopy(A[pos[i] - 1])) for i in ids2]
gate("C2 {0} cross ref(s) to s01 symbols -> negative provisional uids {1}".format(len(CROSS), [(c["action"], c["provisional_uid"]) for c in CROSS]), not bad, bad)
rin = J(os.path.join(B, "plan_ring_p4_rasrest_in.json"))["actions"]
gate("RR v18 #25..#50 after cross-ref == rasrest_in's 26 actions", keep[:26] == rin, [k["id"] for k, r in zip(keep, rin) if k != r][:6])
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = copy.deepcopy(ras["base"])
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s02v18a", goal="card 142-5 PASS A: P4 v18 session 2 (ops {0}..{1}), no open_rows".format(S1N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
try:
    SA = SS.simulate(AIN, PROVB, out_root=SIM, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "bed") for r in J(BEDPLAN).get("open_rows") or [])
ok_pairs.update(((int(r["node"]), r["term"]), "s02-step0") for r in s02.get("open_rows") or [] if "step 0" in r.get("why", ""))
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c141_p1_mk.py:74-92 (tie_rows), copied
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
gate("TIE every end row ({0}) tied to a session-2 action or a step-0 declared pair".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c142-5: made by session-2 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c142-5: open at step 0 = " + t["id"])[:300]})
json.dump(dict(TOP, stage="ring_p4_s02v18", goal=("RING P4 v18 LabVIEW session 2 (card 142-5, PD330(d)/PD331(d)): v18 ops {0}..{1} ({2} actions: "
               "rest of the slot-write repair + the first non-repair ops) on session 1's SIMULATED end (provisional; stage_prerun --rebase "
               "onto D1_ring_p4s01_20261002_232547.vi's graph)").format(S1N + 1, cut, len(keep)), base=BASEREF, open_rows=orows, actions=keep),
          open(IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(OUT) if os.path.isfile(OUT) else {}
gate("SB plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"]})
o2 = SX.compile_plan(p)
mp = SPR.x10_model_peak([o["kind"] for o in o2], sorted({0, len(o2)} | set(k for k, o in enumerate(o2, 1) if o["kind"] in SX.BIND_KINDS)),
                        model=MODEL, start_mb=START)
gate("X10s compiled plan: N {0} R {1} peak {2} == table {3} <= {4}; kinds == v18 ops {5}..{6}".format(mp["N"], mp["R"], mp["peak_mb"], peak(S1N, cut),
     SPR.X10_FAIL_MB, S1N + 1, cut), abs(mp["peak_mb"] - peak(S1N, cut)) < 0.05 and mp["ok"] and [o["kind"] for o in o2] == [o["kind"] for o in OPS[S1N:cut]],
     dict(collections.Counter(o["kind"] for o in o2)))
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (AIN, IN, OUT))
gate("U v18 / s01 / s02 / rasrest / provisional base untouched", all(md5(q).startswith(w) for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
