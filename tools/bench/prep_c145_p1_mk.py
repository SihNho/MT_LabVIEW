# ---
# labview: none
# hardware: none
# ---
r"""prep_c145_p1_mk - card 145-a1-P1 step 1/2 (OFFLINE, no LabVIEW, never launched). P4 session 5 of plan v18 (2ea6cafa) = v18 ops
98..cut, cut = the longest prefix after s04v18 (ops 79..97, 9ff46b0e, rebased on the REAL s03 graph) that splits no 'of' group (PD320(c))
with X10 <= memory_model fail_above_mb (680, PD331(c)) at the PROVISIONAL start 598.5 (= s03 file's measured fresh load; s04's real load is
measured later by card 145-a1-1). PROVISIONAL base = stagesim's END graph of plan_ring_p4_s04v18.json (its finalized step 23 file,
sim/ring_p4_s04v18/step_23_wire.json 3c4d8f8c) -> base {path, md5, provisional: true, sim_of: {plan_ring_p4_s04v18.json, 9ff46b0e}}.
COPIED from prep_c144_p1_mk.py (d3eb89fd) with: s03 -> s04 (END3 -> END4, S3N -> S4N), made_prev = s01..s04 symbols, START 598.5,
names (s04v18 -> s05v18, card id). ONE CHANGE in sub(): s04 was rebased onto the REAL s03 graph, so the END4 graph holds s01..s03 objects
under their REAL uids and END4's sym lists s04 symbols only. A ref to an s04 symbol -> END4 sym (negative, as before); a ref to an
s01..s03 symbol -> s03v18 END sym (sim id) -> s03's creation map (creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl,
the record of the run that saved the s03 file) -> REAL uid, keyed by (uid, class): the real uid's class in END4 must equal the sim id's
class in s03's END (PD350(d), W1 While #16483), and where the rebased s04 plan bound the same symbol the value must agree.
Found before writing: prep_c144_p1_mk.py / prep_c143_p1_mk.py are the makers of a provisional next-session plan; probe
(prep_c145_p1_probe.log): ops > 97 reference s03 symbols (W1, W1.body, SL1R, SD1L, SD1R), s04 symbols (22 refs) and later ones; none
of s01/s02. stage_prerun.read_creation_map / stagesim.obj_class are used as is; no new op, no tool edit.
PREDICTION CONTRACT: M0 input md5 == card / pins; S4 v18 ops 1..97 == s01's + s02v18's + s03v18's + s04v18's ids; E4 s04v18 END step
  file on its pin, sym/neg present; CUT found, peak <= 680; R3 every s01..s03 symbol referenced -> a real uid with the same class, agreeing
  with the s04 rebase; C2 cross refs -> negative (s04) / real (s03) uids, no ref to a later session's symbol; SA pass A replays to end;
  TIE every end row tied (session-5 action or s04v18 open row); SB plan FINAL provisional, open_rows_match; X10s compiled plan peak == table;
  U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c145_p1_mk.log -- py -u tools/bench/prep_c145_p1_mk.py"""
import collections, copy, hashlib, json, os, sys, traceback                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX, stage_prerun as SPR                               # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V18, S01, S02, S03, S04 = (os.path.join(B, n) for n in ("plan_ring_p4_v18.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02v18.json",
                                                         "plan_ring_p4_s03v18.json", "plan_ring_p4_s04v18.json"))
END3F = os.path.join(SIM, "ring_p4_s03v18", "step_20_create.json")
END4F = os.path.join(SIM, "ring_p4_s04v18", "step_23_wire.json")
CMAP3 = os.path.join(B, "creation_map", "plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl")
D5 = os.path.join(SIM, "ring_p4_s05v18_s04end")
PROVB = os.path.join(D5, "base_provisional.json")
DA = os.path.join(SIM, "ring_p4_s05v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s05v18a_in.json"), os.path.join(B, "plan_ring_p4_s05v18_in.json"), os.path.join(B, "plan_ring_p4_s05v18.json")
FACTS = os.path.join(B, "prep_c145_p1_session.json")
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S04: "9ff46b0ece1f238c831d7786616c4f05", S03: "da66a0300851133d93881be3c28f2fdc",
        END4F: "3c4d8f8c4db4fa9c08868dd7e3d4afd0", END3F: "5f31db45b1b8c7f66b48cf28d92a1e03"}
START = 598.5
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
print("FACT s01 md5 {0}, s02v18 md5 {1} (ids only); s03 creation map md5 {2}".format(md5(S01), md5(S02), md5(CMAP3)), flush=True)
v18, s01, s02, s03, s04 = J(V18), J(S01), J(S02), J(S03), J(S04)
gate("E4 s04v18 finalized last step file == {0} (pinned md5)".format(rel(END4F)),
     (s04["finalized"]["step_files"][-1]["path"] == rel(END4F)) and s04["finalized"]["step_files"][-1]["md5"] == WANT[END4F], s04["finalized"]["step_files"][-1])
END4 = J(END4F)["state"]
END3 = J(END3F)["state"]
gate("E4b END state sym/neg present", isinstance(END4.get("sym"), dict) and isinstance(END4.get("neg"), int), (END4.get("sym"), END4.get("neg")))
os.makedirs(D5, exist_ok=True)
json.dump(END4, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)          # prep_c144_p1_mk.py:60
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END4.get("sym")), "neg", END4.get("neg"), "vi md5", END4.get("md5"), flush=True)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
prev3 = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]]
prev_ids = prev3 + [x["id"] for x in s04["actions"]]
S4N = max(act2op[n] for n in range(1, len(prev_ids) + 1))
gate("S4 v18 ops 1..{0} = s01's {1} + s02v18's {2} + s03v18's {3} + s04v18's {4} ids".format(S4N, len(s01["actions"]), len(s02["actions"]), len(s03["actions"]),
     len(s04["actions"])), [ids[n - 1] for k in range(1, S4N + 1) for n in OPS[k - 1]["acts"]] == prev_ids)
MODEL = SPR.load_memory_model()
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
peak = lambda a, b: round(START + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
cut = max([b for b in range(S4N + 1, NOP + 1) if peak(S4N, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
first_over = next((b for b in range(S4N + 1, NOP + 1) if peak(S4N, b) > SPR.X10_FAIL_MB), None)
gate("CUT ops {0}..{1}: peak {2} <= {3} at start {4}; op {5} would be {6}; first op over the limit {7}".format(S4N + 1, cut, cut and peak(S4N, cut),
     SPR.X10_FAIL_MB, START, cut and cut + 1, cut and cut < NOP and peak(S4N, cut + 1), first_over), cut is not None)
ids5 = [ids[n - 1] for k in range(S4N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
blocked = [(b, peak(S4N, b), [g for g in groups if g[0] <= b < g[1]]) for b in range(cut + 1, (first_over or cut + 1))]
subv = dict((SUBVI[i], {"op": act2op[pos[i]], "in_session": S4N < act2op[pos[i]] <= cut}) for i in SUBVI if i in pos)
rest = NOP - cut
print("FACT session 5 = {0} actions {1}..{2}; ops {3}..{4}; peak {5}; margin {6} MB; next op {7} peak {8}; cuts refused by 'of' groups below the limit {9}; "
      "subVI drops {10}; ops left after s05 {11} of {12}".format(len(ids5), ids5[0], ids5[-1], S4N + 1, cut, peak(S4N, cut), round(SPR.X10_FAIL_MB - peak(S4N, cut), 1),
                                                              cut + 1, cut < NOP and peak(S4N, cut + 1), blocked, subv, rest, NOP), flush=True)
made3 = set("new:" + x["as"] for x in s01["actions"] + s02["actions"] + s03["actions"] if x.get("as"))
made4s = set("new:" + x["as"] for x in s04["actions"] if x.get("as"))
made_prev = made3 | made4s
made5 = set("new:" + A[pos[i] - 1]["as"] for i in ids5 if A[pos[i] - 1].get("as"))
_hd, CM, _st = SPR.read_creation_map(CMAP3)
gate("CM s03 creation map header == plan s03v18 da66a030", _hd.get("plan_md5") == WANT[S03], _hd)


def real_of(sym):
    """s01..s03 symbol -> (real uid, sim id, kind) via s03v18 END sym + s03's creation map (obj, diag, term)."""
    sid = END3["sym"].get(sym)
    if not isinstance(sid, int):
        return None, sid, None
    for k in ("obj", "diag", "term"):
        if sid in CM[k]:
            return int(CM[k][sid]["real"]), sid, k
    return None, sid, None


s04by = dict((x["id"], x) for x in s04["actions"])
UIDF, ADDRF = ("dest_diagram", "loop", "body", "parent", "uid", "diagram"), ("at", "src", "dst", "born_on", "on")
REB = collections.defaultdict(set)                                                           # how the s04 rebase bound s01..s03 symbols
for a in A[len(prev3):len(prev_ids)]:
    for f in UIDF + ADDRF:
        y = a.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if isinstance(s, str) and s.startswith("new:") and (s.split(".")[0] in made3 or s.split(".")[0][:-1] in made3):
            z = s04by[a["id"]].get(f)
            zu = z.get("uid") if isinstance(z, dict) else z
            REB[s if not (f in ADDRF and isinstance(y, str)) else s.split(".")[0]].add(zu)
CROSS, bad, RMAP = [], [], {}


def sub(x):                                                                                   # prep_c144_p1_mk.py:91-111, copied; s01..s03 -> REAL
    for f in UIDF + ADDRF:
        y = x.get(f)
        s = y.get("uid") if isinstance(y, dict) else y
        if not (isinstance(s, str) and s.startswith("new:")):
            continue
        root = s.split(".")[0]
        if root not in made_prev and root[:-1] not in made_prev:
            continue
        key = root if (f in ADDRF and isinstance(y, str)) else s
        early = root in made3 or root[:-1] in made3
        if early:
            u, sid, kind = real_of(key)
            c3, c4 = SS.obj_class(END3, sid) if isinstance(sid, int) else None, SS.obj_class(END4, u) if isinstance(u, int) else None
            RMAP[key] = {"real": u, "sim": sid, "kind": kind, "class_sim": c3, "class_real": c4, "s04_rebase": sorted(REB.get(key) or [])}
            ok = isinstance(u, int) and u > 0 and c4 is not None and (c3 is None or c3 == c4) and (not REB.get(key) or REB[key] == {u})
        else:
            u = END4["sym"].get(key)
            ok = isinstance(u, int) and u < 0
        if f in ADDRF and isinstance(y, str):
            x[f] = {"uid": u, "term": s.split(".", 1)[1]}
        elif isinstance(y, dict):
            x[f]["uid"] = u
        else:
            x[f] = u
        CROSS.append({"action": x["id"], "field": f, "symbol": s, "uid": u, "from": "s01-s03 real" if early else "s04 provisional"})
        ok or bad.append((x["id"], f, s, u))
    return x


keep = [sub(copy.deepcopy(A[pos[i] - 1])) for i in ids5]
for k in sorted(RMAP):
    print("FACT R3 {0} -> real #{1} (s03 sim #{2}, map kind {3}); class sim {4} / real {5}; s04 rebase bound {6}".format(
          k, RMAP[k]["real"], RMAP[k]["sim"], RMAP[k]["kind"], RMAP[k]["class_sim"], RMAP[k]["class_real"], RMAP[k]["s04_rebase"]), flush=True)
gate("R3 {0} s01..s03 symbol(s) -> real uid by s03's creation map, (uid, class) equal, == the s04 rebase where it bound them".format(len(RMAP)),
     all(isinstance(r["real"], int) and r["real"] > 0 and r["class_real"] is not None and (r["class_sim"] is None or r["class_sim"] == r["class_real"])
         and (not r["s04_rebase"] or r["s04_rebase"] == [r["real"]]) for r in RMAP.values()), RMAP)
late = [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), str) and x[f].startswith("new:")
        and x[f].split(".")[0] not in made5 and x[f].split(".")[0][:-1] not in made5]                # prep_c144_p1_mk.py:115-118
late += [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), dict) and isinstance(x[f].get("uid"), str)
         and x[f]["uid"].startswith("new:") and x[f]["uid"].split(".")[0] not in made5 and x[f]["uid"].split(".")[0][:-1] not in made5]
gate("C2 {0} cross ref(s): s04 symbols -> negative provisional uids, s01..s03 -> real uids {1}; no ref to a later session's symbol".format(
     len(CROSS), [(c["action"], c["symbol"], c["uid"]) for c in CROSS]), not bad and not late, {"bad": bad, "late": late[:8]})
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S04), "md5": md5(S04)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s05v18a", goal="card 145-a1-P1 PASS A: P4 v18 session 5 (ops {0}..{1}), no open_rows".format(S4N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(AIN)))
try:
    SA = SS.simulate(AIN, PROVB, out_root=SIM, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "s04v18-open") for r in s04.get("open_rows") or [])
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c144_p1_mk.py:135-148, copied
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
gate("TIE every end row ({0}) tied to a session-5 action or an s04v18 open row".format(len(SA["end_cdiff_rows"])), not untied, untied[:10])
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] not in seen:
        seen.add(t["pair"])
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c145-P1: made by session-5 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c145-P1: open at step 0 = declared open row of plan_ring_p4_s04v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s05v18", goal=("RING P4 v18 LabVIEW session 5 (card 145-a1-P1, PD350(e)/PD331(c)): v18 ops {0}..{1} ({2} actions) on session 4's "
               "SIMULATED end (provisional; stage_prerun --rebase onto session 4's saved in-between file's graph)").format(S4N + 1, cut, len(keep)),
               base=BASEREF, open_rows=orows, actions=keep), open(IN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(IN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(OUT) if os.path.isfile(OUT) else {}
gate("SB plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"]})
o5 = SX.compile_plan(p)
mp = SPR.x10_model_peak([o["kind"] for o in o5], sorted({0, len(o5)} | set(k for k, o in enumerate(o5, 1) if o["kind"] in SX.BIND_KINDS)),
                        model=MODEL, start_mb=START)
# prep_c144_p1_mk.py:169-174: a v18 'wire_sr' whose register is an EARLIER session's (bound to a uid by sub()) compiles to 'connect'.
kv, k5 = [o["kind"] for o in OPS[S4N:cut]], [o["kind"] for o in o5]
srx = [(S4N + 1 + j, OPS[S4N + j].get("reg")) for j in range(len(kv)) if j < len(k5) and kv[j] != k5[j]]
kinds_ok = len(kv) == len(k5) and all(kv[j] == k5[j] or (kv[j] == "wire_sr" and k5[j] == "connect" and (str(OPS[S4N + j].get("reg")) in made_prev or str(OPS[S4N + j].get("reg"))[:-1] in made_prev))
                                       for j in range(len(kv)))
print("FACT kind differences v18 -> s05 (op, v18 reg symbol): {0}".format(srx), flush=True)
gate("X10s compiled plan: N {0} R {1} peak {2} == table {3} <= {4}; kinds == v18 ops {5}..{6} except wire_sr -> connect on an earlier session's register {7}".format(
     mp["N"], mp["R"], mp["peak_mb"], peak(S4N, cut), SPR.X10_FAIL_MB, S4N + 1, cut, srx), abs(mp["peak_mb"] - peak(S4N, cut)) < 0.05 and mp["ok"] and kinds_ok,
     dict(collections.Counter(o["kind"] for o in o5)))
json.dump({"card": "145-a1-P1", "v18": {"path": rel(V18), "md5": md5(V18)}, "ops": [S4N + 1, cut], "first": ids5[0], "last": ids5[-1], "actions": len(keep),
           "start_mb": START, "start_cite": "PROVISIONAL (brief 145-a1-P1 step 1): s03 file's measured fresh load 598.5; s04's real load is measured by card 145-a1-1",
           "peak_mb": peak(S4N, cut), "margin_mb": round(SPR.X10_FAIL_MB - peak(S4N, cut), 1), "next_op": cut + 1, "next_peak_mb": cut < NOP and peak(S4N, cut + 1),
           "limit_mb": SPR.X10_FAIL_MB, "first_op_over_limit": first_over, "cuts_refused_by_of": blocked, "subvi_drops": subv, "cross_refs": CROSS, "real_map": RMAP,
           "open_rows": len(orows), "end_rows": len(SA["end_cdiff_rows"]), "ops_total": NOP, "ops_left_after": rest,
           "kinds": dict(collections.Counter(o["kind"] for o in o5))}, open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s04v18 / s03v18 / END step files untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
