# ---
# labview: none
# hardware: none
# ---
r"""prep_c144_p1_mk - card 144-P1 step 1/2 (OFFLINE, no LabVIEW, never launched). P4 session 4 of plan v18 (2ea6cafa) = v18 ops
79..cut, cut = the longest prefix after s03v18 (ops 59..78, da66a030) that splits no 'of' group (PD320(c)) with X10 <= memory_model
fail_above_mb (680, PD331(c)) at the PROVISIONAL start 596.0 (s03's real load is measured later by card 144-2). PROVISIONAL base =
stagesim's END graph of plan_ring_p4_s03v18.json (its finalized step 20 file, the sim on the REAL s02 graph after --rebase,
sim/ring_p4_s03v18/step_20_create.json 5f31db45) -> base {path, md5, provisional: true, sim_of: {plan_ring_p4_s03v18.json, da66a030}}.
COPIED from prep_c143_p1_mk.py (d78de7e0) with: s02 -> s03 (END2 -> END3, S2N -> S3N), made_prev = s01 + s02 + s03 symbols, START 596.0,
names (s03v18 -> s04v18, card id). Found before writing: prep_c143_p1_mk.py / prep_c142_5_mk.py / prep_c141_p1_mk.py are the makers of a
provisional next-session plan (ls tools/bench/prep_c14*_mk.py); no new op, no tool edit.
Probe (prep_c144_p1_probe.log): ops > 78 reference only s03 symbols (18 refs: W1, W1.body, SL1L/R, SD1L/R, LRN4) and later ones; none of s01/s02.
PREDICTION CONTRACT: M0 input md5 == card; S3 v18 ops 1..78 == s01's + s02v18's + s03v18's ids; E3 s03v18 END step file on its pin, sym/neg
  present; CUT found, peak <= 680; C2 cross refs to s01/s02/s03 symbols -> negative uids of the provisional base, no ref to a later session's
  symbol; SA pass A replays to end; TIE every end row tied (session-4 action or s03v18 open row); SB plan FINAL provisional, open_rows_match;
  X10s compiled plan peak == table; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c144_p1_mk.log -- py -u tools/bench/prep_c144_p1_mk.py"""
import collections, copy, hashlib, json, os, sys, traceback                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V18, S01, S02, S03 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02v18.json", "plan_ring_p4_s03v18.json"))
END3F = os.path.join(SIM, "ring_p4_s03v18", "step_20_create.json")
D4 = os.path.join(SIM, "ring_p4_s04v18_s03end")
PROVB = os.path.join(D4, "base_provisional.json")
DA = os.path.join(SIM, "ring_p4_s04v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s04v18a_in.json"), os.path.join(B, "plan_ring_p4_s04v18_in.json"), os.path.join(B, "plan_ring_p4_s04v18.json")
FACTS = os.path.join(B, "prep_c144_p1_session.json")
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S03: "da66a0300851133d93881be3c28f2fdc", END3F: "5f31db45b1b8c7f66b48cf28d92a1e03"}
START = 596.0
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
print("FACT s01 md5 {0}, s02v18 md5 {1} (ids only)".format(md5(S01), md5(S02)), flush=True)
v18, s01, s02, s03 = J(V18), J(S01), J(S02), J(S03)
gate("E3 s03v18 finalized last step file == {0} (pinned md5), state has sym/neg".format(rel(END3F)),
     (s03["finalized"]["step_files"][-1]["path"] == rel(END3F)) and s03["finalized"]["step_files"][-1]["md5"] == WANT[END3F], s03["finalized"]["step_files"][-1])
END3 = J(END3F)["state"]
gate("E3b END state sym/neg present", isinstance(END3.get("sym"), dict) and isinstance(END3.get("neg"), int), (END3.get("sym"), END3.get("neg")))
os.makedirs(D4, exist_ok=True)
json.dump(END3, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)          # prep_c143_p1_mk.py:56
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END3.get("sym")), "neg", END3.get("neg"), "vi md5", END3.get("md5"), flush=True)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
prev_ids = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]]
S3N = max(act2op[n] for n in range(1, len(prev_ids) + 1))
gate("S3 v18 ops 1..{0} = s01's {1} + s02v18's {2} + s03v18's {3} ids".format(S3N, len(s01["actions"]), len(s02["actions"]), len(s03["actions"])),
     [ids[n - 1] for k in range(1, S3N + 1) for n in OPS[k - 1]["acts"]] == prev_ids)
MODEL = SPR.load_memory_model()
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
peak = lambda a, b: round(START + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
cut = max([b for b in range(S3N + 1, NOP + 1) if peak(S3N, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
first_over = next((b for b in range(S3N + 1, NOP + 1) if peak(S3N, b) > SPR.X10_FAIL_MB), None)
gate("CUT ops {0}..{1}: peak {2} <= {3} at start {4}; op {5} would be {6}; first op over the limit {7}".format(S3N + 1, cut, cut and peak(S3N, cut),
     SPR.X10_FAIL_MB, START, cut and cut + 1, cut and cut < NOP and peak(S3N, cut + 1), first_over), cut is not None)
ids4 = [ids[n - 1] for k in range(S3N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
blocked = [(b, peak(S3N, b), [g for g in groups if g[0] <= b < g[1]]) for b in range(cut + 1, (first_over or cut + 1))]
subv = dict((SUBVI[i], {"op": act2op[pos[i]], "in_session": S3N < act2op[pos[i]] <= cut}) for i in SUBVI if i in pos)
print("FACT session 4 = {0} actions {1}..{2}; ops {3}..{4}; peak {5}; margin {6} MB; next op {7} peak {8}; cuts refused by 'of' groups below the limit {9}; subVI drops {10}".format(
      len(ids4), ids4[0], ids4[-1], S3N + 1, cut, peak(S3N, cut), round(SPR.X10_FAIL_MB - peak(S3N, cut), 1), cut + 1, cut < NOP and peak(S3N, cut + 1), blocked, subv), flush=True)
made_prev = set("new:" + x["as"] for x in s01["actions"] + s02["actions"] + s03["actions"] if x.get("as"))
made4 = set("new:" + A[pos[i] - 1]["as"] for i in ids4 if A[pos[i] - 1].get("as"))
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
CROSS, bad = [], []


def sub(x):                                                                                   # prep_c143_p1_mk.py:87-107, copied (END2 -> END3)
    for f in UIDF + ADDRF:
        y = x.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if root not in made_prev and root[:-1] not in made_prev:
            continue
        if f in ADDRF and isinstance(y, str):
            u = END3["sym"].get(root)
            x[f] = {"uid": u, "term": s.split(".", 1)[1]}
        elif isinstance(y, dict):
            u = END3["sym"].get(s)
            x[f]["uid"] = u
        else:
            u = END3["sym"].get(s)
            x[f] = u
        CROSS.append({"action": x["id"], "field": f, "symbol": s, "provisional_uid": u})
        (isinstance(u, int) and u < 0) or bad.append((x["id"], f, s, u))
    return x


keep = [sub(copy.deepcopy(A[pos[i] - 1])) for i in ids4]
late = [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), str) and x[f].startswith("new:")
        and x[f].split(".")[0] not in made4 and x[f].split(".")[0][:-1] not in made4]                # prep_c143_p1_mk.py:111-112
late += [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), dict) and isinstance(x[f].get("uid"), str)
         and x[f]["uid"].startswith("new:") and x[f]["uid"].split(".")[0] not in made4 and x[f]["uid"].split(".")[0][:-1] not in made4]
gate("C2 {0} cross ref(s) to s01/s02/s03 symbols -> negative provisional uids {1}; no ref to a later session's symbol".format(
     len(CROSS), [(c["action"], c["symbol"], c["provisional_uid"]) for c in CROSS]), not bad and not late, {"bad": bad, "late": late[:8]})
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S03), "md5": md5(S03)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s04v18a", goal="card 144-P1 PASS A: P4 v18 session 4 (ops {0}..{1}), no open_rows".format(S3N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(AIN)))
try:
    SA = SS.simulate(AIN, PROVB, out_root=SIM, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "s03v18-open") for r in s03.get("open_rows") or [])
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c143_p1_mk.py:129-142, copied
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
gate("TIE every end row ({0}) tied to a session-4 action or an s03v18 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c144-P1: made by session-4 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c144-P1: open at step 0 = declared open row of plan_ring_p4_s03v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s04v18", goal=("RING P4 v18 LabVIEW session 4 (card 144-P1, PD330(d)/PD331(c)): v18 ops {0}..{1} ({2} actions) on session 3's "
               "SIMULATED end (provisional; stage_prerun --rebase onto session 3's saved in-between file's graph)").format(S3N + 1, cut, len(keep)),
               base=BASEREF, open_rows=orows, actions=keep), open(IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(OUT) if os.path.isfile(OUT) else {}
gate("SB plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"]})
o4 = SX.compile_plan(p)
mp = SPR.x10_model_peak([o["kind"] for o in o4], sorted({0, len(o4)} | set(k for k, o in enumerate(o4, 1) if o["kind"] in SX.BIND_KINDS)),
                        model=MODEL, start_mb=START)
# card 144-P1: a v18 'wire_sr' whose register is an EARLIER session's (bound to a uid by sub()) compiles to 'connect' and is routed to
# wire_sr at run time when it touches a base register's inner face (stagexec.py:1494-1505 base_sr_route, :2576-2579; card 112-1 T1).
kv, k4 = [o["kind"] for o in OPS[S3N:cut]], [o["kind"] for o in o4]
srx = [(S3N + 1 + j, OPS[S3N + j].get("reg")) for j in range(len(kv)) if j < len(k4) and kv[j] != k4[j]]
kinds_ok = len(kv) == len(k4) and all(kv[j] == k4[j] or (kv[j] == "wire_sr" and k4[j] == "connect" and (str(OPS[S3N + j].get("reg")) in made_prev or str(OPS[S3N + j].get("reg"))[:-1] in made_prev))   # add_sr 'as' SL1 -> SL1L/SL1R (sub() root[:-1])
                                       for j in range(len(kv)))
print("FACT kind differences v18 -> s04 (op, v18 reg symbol): {0}".format(srx), flush=True)
gate("X10s compiled plan: N {0} R {1} peak {2} == table {3} <= {4}; kinds == v18 ops {5}..{6} except wire_sr -> connect on an earlier session's register {7}".format(
     mp["N"], mp["R"], mp["peak_mb"], peak(S3N, cut), SPR.X10_FAIL_MB, S3N + 1, cut, srx), abs(mp["peak_mb"] - peak(S3N, cut)) < 0.05 and mp["ok"] and kinds_ok,
     dict(collections.Counter(o["kind"] for o in o4)))
json.dump({"card": "144-P1", "v18": {"path": rel(V18), "md5": md5(V18)}, "ops": [S3N + 1, cut], "first": ids4[0], "last": ids4[-1], "actions": len(keep),
           "start_mb": START, "start_cite": "PROVISIONAL (brief 144-P1 step 1): s03's real load is measured by card 144-2", "peak_mb": peak(S3N, cut),
           "margin_mb": round(SPR.X10_FAIL_MB - peak(S3N, cut), 1), "next_op": cut + 1, "next_peak_mb": cut < NOP and peak(S3N, cut + 1), "limit_mb": SPR.X10_FAIL_MB,
           "first_op_over_limit": first_over, "cuts_refused_by_of": blocked, "subvi_drops": subv, "cross_refs": CROSS, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "kinds": dict(collections.Counter(o["kind"] for o in o4))}, open(FACTS, "w", encoding="utf-8"), indent=1)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s03v18 / s03 END step file untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
