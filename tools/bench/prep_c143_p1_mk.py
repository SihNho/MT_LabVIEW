r"""prep_c143_p1_mk - card 143-P1 step 1/2 (OFFLINE, no LabVIEW, never launched). P4 session 3 of plan v18 (2ea6cafa) = v18 ops
59..cut, cut = the longest prefix after s02v18 (ops 25..58, e941ebbf) that splits no 'of' group (PD320(c)) with X10 <= memory_model
fail_above_mb (680, PD331(c)) at the PROVISIONAL start 596.5 (s02's real load is measured later by card 143-1). PROVISIONAL base =
stagesim's END graph of plan_ring_p4_s02v18.json (its finalized step 34 file, the re-sim on the real s01 graph after --rebase,
prep_c142_5_rebase.log:74) -> base {path, md5, provisional: true, sim_of: {plan_ring_p4_s02v18.json, e941ebbf}} (the --rebase
contract, stage_prerun.py:3393-3409). Route COPIED, not rebuilt: prep_c142_5_mk.py (cut_ok / peak / sub / pass A / tie / pass B / X10s)
and prep_c141_p1_mk.py:280-320 (END state -> provisional base file; 'late' ref check). Found before writing: prep_c142_5_mk.py and
prep_c141_p1_mk.py are the only makers of a provisional next-session plan (ls tools/bench/prep_c14*_mk.py); no new op, no tool edit.
Probe (prep_c143_p1_probe.log): ops > 58 reference ONE earlier-session symbol, new:LRS2 (s02, END sym -20); none of s01's.
PREDICTION CONTRACT: M0 input md5 == card; S2 v18 ops 1..58 == s01's + s02v18's ids; E2 s02v18 END step file on its pin, sym/neg present;
  CUT found, peak <= 680; C2 cross refs to s01/s02 symbols -> negative uids of the provisional base, no ref to a later session's symbol;
  SA pass A replays to end; TIE every end row tied (session-3 action or s02v18 open row); SB plan FINAL provisional, open_rows_match;
  X10s compiled plan peak == table; U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c143_p1_mk.log -- py -u tools/bench/prep_c143_p1_mk.py"""
import collections, copy, hashlib, json, os, sys, traceback                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V18, S01, S02 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02v18.json"))
END2F = os.path.join(SIM, "ring_p4_s02v18", "step_34_create.json")
D3 = os.path.join(SIM, "ring_p4_s03v18_s02end")
PROVB = os.path.join(D3, "base_provisional.json")
DA = os.path.join(SIM, "ring_p4_s03v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s03v18a_in.json"), os.path.join(B, "plan_ring_p4_s03v18_in.json"), os.path.join(B, "plan_ring_p4_s03v18.json")
FACTS = os.path.join(B, "prep_c143_p1_session.json")
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S01: "f4831031c738c997391b5bcace19d9f0", S02: "e941ebbfaa3d98099bcd10d8c6237ef4",
        END2F: "5f74a80438da12ed6079f15d109b3762"}
START = 596.5
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
v18, s01, s02 = J(V18), J(S01), J(S02)
gate("E2 s02v18 finalized last step file == {0} (pinned md5), state has sym/neg".format(rel(END2F)),
     (s02["finalized"]["step_files"][-1]["path"] == rel(END2F)) and s02["finalized"]["step_files"][-1]["md5"] == WANT[END2F], s02["finalized"]["step_files"][-1])
END2 = J(END2F)["state"]
gate("E2b END state sym/neg present", isinstance(END2.get("sym"), dict) and isinstance(END2.get("neg"), int), (END2.get("sym"), END2.get("neg")))
os.makedirs(D3, exist_ok=True)
json.dump(END2, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)          # prep_c141_p1_mk.py:280-281
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END2.get("sym")), "neg", END2.get("neg"), "vi md5", END2.get("md5"), flush=True)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
prev_ids = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]]
S2N = max(act2op[n] for n in range(1, len(prev_ids) + 1))
gate("S2 v18 ops 1..{0} = s01's {1} + s02v18's {2} ids".format(S2N, len(s01["actions"]), len(s02["actions"])),
     [ids[n - 1] for k in range(1, S2N + 1) for n in OPS[k - 1]["acts"]] == prev_ids)
MODEL = SPR.load_memory_model()
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
peak = lambda a, b: round(START + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
cut = max([b for b in range(S2N + 1, NOP + 1) if peak(S2N, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
first_over = next((b for b in range(S2N + 1, NOP + 1) if peak(S2N, b) > SPR.X10_FAIL_MB), None)
gate("CUT ops {0}..{1}: peak {2} <= {3} at start {4}; op {5} would be {6}; first op over the limit {7}".format(S2N + 1, cut, cut and peak(S2N, cut),
     SPR.X10_FAIL_MB, START, cut and cut + 1, cut and cut < NOP and peak(S2N, cut + 1), first_over), cut is not None)
ids3 = [ids[n - 1] for k in range(S2N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
blocked = [(b, peak(S2N, b), [g for g in groups if g[0] <= b < g[1]]) for b in range(cut + 1, (first_over or cut + 1))]
subv = dict((SUBVI[i], {"op": act2op[pos[i]], "in_session": S2N < act2op[pos[i]] <= cut}) for i in SUBVI if i in pos)
print("FACT session 3 = {0} actions {1}..{2}; ops {3}..{4}; peak {5}; margin {6} MB; next op {7} peak {8}; cuts refused by 'of' groups below the limit {9}; subVI drops {10}".format(
      len(ids3), ids3[0], ids3[-1], S2N + 1, cut, peak(S2N, cut), round(SPR.X10_FAIL_MB - peak(S2N, cut), 1), cut + 1, cut < NOP and peak(S2N, cut + 1), blocked, subv), flush=True)
made_prev = set("new:" + x["as"] for x in s01["actions"] + s02["actions"] if x.get("as"))
made3 = set("new:" + A[pos[i] - 1]["as"] for i in ids3 if A[pos[i] - 1].get("as"))
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
CROSS, bad = [], []


def sub(x):                                                                                   # prep_c142_5_mk.py:66-86, copied (END1 -> END2)
    for f in UIDF + ADDRF:
        y = x.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if root not in made_prev and root[:-1] not in made_prev:
            continue
        if f in ADDRF and isinstance(y, str):
            u = END2["sym"].get(root)
            x[f] = {"uid": u, "term": s.split(".", 1)[1]}
        elif isinstance(y, dict):
            u = END2["sym"].get(s)
            x[f]["uid"] = u
        else:
            u = END2["sym"].get(s)
            x[f] = u
        CROSS.append({"action": x["id"], "field": f, "symbol": s, "provisional_uid": u})
        (isinstance(u, int) and u < 0) or bad.append((x["id"], f, s, u))
    return x


keep = [sub(copy.deepcopy(A[pos[i] - 1])) for i in ids3]
late = [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), str) and x[f].startswith("new:")
        and x[f].split(".")[0] not in made3 and x[f].split(".")[0][:-1] not in made3]                # prep_c141_p1_mk.py:316-318, adapted
gate("C2 {0} cross ref(s) to s01/s02 symbols -> negative provisional uids {1}; no ref to a later session's symbol".format(
     len(CROSS), [(c["action"], c["symbol"], c["provisional_uid"]) for c in CROSS]), not bad and not late, {"bad": bad, "late": late[:8]})
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S02), "md5": md5(S02)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s03v18a", goal="card 143-P1 PASS A: P4 v18 session 3 (ops {0}..{1}), no open_rows".format(S2N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(AIN)))
try:
    SA = SS.simulate(AIN, PROVB, out_root=SIM, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "s02v18-open") for r in s02.get("open_rows") or [])
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c142_5_mk.py:107-120, copied
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
gate("TIE every end row ({0}) tied to a session-3 action or an s02v18 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c143-P1: made by session-3 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c143-P1: open at step 0 = declared open row of plan_ring_p4_s02v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s03v18", goal=("RING P4 v18 LabVIEW session 3 (card 143-P1, PD330(d)/PD331(c)): v18 ops {0}..{1} ({2} actions) on session 2's "
               "SIMULATED end (provisional; stage_prerun --rebase onto session 2's saved in-between file's graph)").format(S2N + 1, cut, len(keep)),
               base=BASEREF, open_rows=orows, actions=keep), open(IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(OUT) if os.path.isfile(OUT) else {}
gate("SB plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"]})
o3 = SX.compile_plan(p)
mp = SPR.x10_model_peak([o["kind"] for o in o3], sorted({0, len(o3)} | set(k for k, o in enumerate(o3, 1) if o["kind"] in SX.BIND_KINDS)),
                        model=MODEL, start_mb=START)
gate("X10s compiled plan: N {0} R {1} peak {2} == table {3} <= {4}; kinds == v18 ops {5}..{6}".format(mp["N"], mp["R"], mp["peak_mb"], peak(S2N, cut),
     SPR.X10_FAIL_MB, S2N + 1, cut), abs(mp["peak_mb"] - peak(S2N, cut)) < 0.05 and mp["ok"] and [o["kind"] for o in o3] == [o["kind"] for o in OPS[S2N:cut]],
     dict(collections.Counter(o["kind"] for o in o3)))
json.dump({"card": "143-P1", "v18": {"path": rel(V18), "md5": md5(V18)}, "ops": [S2N + 1, cut], "first": ids3[0], "last": ids3[-1], "actions": len(keep),
           "start_mb": START, "start_cite": "PROVISIONAL (brief 143-P1 step 1): s02's real load is measured by card 143-1", "peak_mb": peak(S2N, cut),
           "margin_mb": round(SPR.X10_FAIL_MB - peak(S2N, cut), 1), "next_op": cut + 1, "next_peak_mb": cut < NOP and peak(S2N, cut + 1), "limit_mb": SPR.X10_FAIL_MB,
           "first_op_over_limit": first_over, "cuts_refused_by_of": blocked, "subvi_drops": subv, "cross_refs": CROSS, "open_rows": len(orows),
           "end_rows": len(SA["end_cdiff_rows"]), "kinds": dict(collections.Counter(o["kind"] for o in o3))}, open(FACTS, "w", encoding="utf-8"), indent=1)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s01 / s02v18 / s02 END step file untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
