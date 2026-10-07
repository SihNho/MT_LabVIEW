# ---
# labview: none
# hardware: none
# ---
r"""prep_c145_a2_6_mk - card 145-a2-6 step 1 (OFFLINE, no LabVIEW, never launched). Re-makes P4 session 5 = v18 ops 98..124 (FIXED by the
card, not re-cut) on the CURRENT s04 plan's simulated end (plan_ring_p4_s04v18.json f349c39a, its finalized last step file
sim/ring_p4_s04v18/step_23_wire.json b5ae7f79), as a PROVISIONAL plan {provisional: true, sim_of: {s04v18, f349c39a}} that the next step
rebases (stage_prerun.py --rebase) onto the REAL s04 graph graph_ring_p4s04_20261007_223245.json (094ba298).
COPIED from prep_c145_p1_mk.py (c7fdf263) with these changes ONLY:
  (1) pins: S04 9ff46b0e -> f349c39a, END4F 3c4d8f8c -> b5ae7f79 (the s04 plan was re-simulated by prep_c145_2_fix.py: SQ1 terminal row);
  (2) START 598.5 -> 605.4 (s04 adopted file's MEASURED fresh load, diag_c145_a2_1_facts.md:15);
  (3) the cut is FIXED at ops 98..124 by the card (gate CUT checks it splits no 'of' group); the per-op formula's own longest cut at 605.4 is
      printed as a FACT (report only, no re-cut); X10 vs fail 680 is REPORTED, not a gate (brief step 3);
  (4) the provisional s05 files are first byte-copied to *_prov (plan/_in/_pred -> tools/bench/plan_ring_p4_s05v18*_prov.json; the step
      files of sim/ring_p4_s05v18/ -> sim/ring_p4_s05v18/_prov/, inside the card's write glob) and md5-checked;
  (5) paths inside the card's write globs: base -> sim/ring_p4_s05v18/s04end/base_provisional.json, pass A -> sim/ring_p4_s05v18/_passA/,
      session table -> prep_c145_a2_6_session.json; card id.
Existing tools checked: prep_c145_p1_mk.py (the maker, copied), stage_prerun.read_creation_map / x10_model_peak, stagesim.simulate /
obj_class; no new op, no tool edit.
PREDICTION CONTRACT: M0 input md5 == card / pins; P provisional copies == originals; S4 v18 ops 1..97 == s01..s04 ids; E4 END step file on
  its pin; CUT 124 splits no 'of' group; R3 every s01..s03 symbol -> real uid with the same class == s04 rebase; C2 s04 refs negative, no
  later ref; SA pass A replays; TIE every end row tied; SB plan FINAL provisional, open_rows_match; X10s compiled plan peak == table;
  U inputs untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c145_a2_6_mk.log -- py -u tools/bench/prep_c145_a2_6_mk.py"""
import collections, copy, hashlib, json, os, shutil, sys, traceback                       # noqa: E401
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
S5D = os.path.join(SIM, "ring_p4_s05v18")
D5 = os.path.join(S5D, "s04end")
PROVB = os.path.join(D5, "base_provisional.json")
PAROOT = os.path.join(S5D, "_passA")
DA = os.path.join(PAROOT, "ring_p4_s05v18a")
AIN, IN, OUT = os.path.join(DA, "plan_ring_p4_s05v18a_in.json"), os.path.join(B, "plan_ring_p4_s05v18_in.json"), os.path.join(B, "plan_ring_p4_s05v18.json")
PRED = os.path.join(B, "plan_ring_p4_s05v18_pred.json")
FACTS = os.path.join(B, "prep_c145_a2_6_session.json")
WANT = {V18: "2ea6cafa7d368dc7a054346d398daa3e", S04: "f349c39a17330531e688ff1f70ce426e", S03: "da66a0300851133d93881be3c28f2fdc",
        END4F: "b5ae7f79975b9faca0722bb4dc6e3781", END3F: "5f31db45b1b8c7f66b48cf28d92a1e03"}
PROV_WANT = {OUT: "b7d27e24e27a196a071c490053feafaa", PRED: "6666a7183fc4a2ca428e62fab5897803", IN: "7fbdaa62298596fb5287a660a1cc9e81"}
START = 605.4
CUT_OPS = (98, 124)
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
# (4) provisional copies first
gate("P0 provisional s05 plan/_pred/_in on their pins (b7d27e24 / 6666a718 / 7fbdaa62)", all(md5(p) == w for p, w in PROV_WANT.items()),
     dict((os.path.basename(p), md5(p)) for p in PROV_WANT))
cp = {}
for p in PROV_WANT:
    q = p[:-5] + "_prov.json"
    if not os.path.isfile(q):
        shutil.copyfile(p, q)
    cp[rel(q)] = md5(q)
os.makedirs(os.path.join(S5D, "_prov"), exist_ok=True)
for n in sorted(os.listdir(S5D)):
    if os.path.isfile(os.path.join(S5D, n)) and not os.path.isfile(os.path.join(S5D, "_prov", n)):
        shutil.copyfile(os.path.join(S5D, n), os.path.join(S5D, "_prov", n))
simcp = dict((n, md5(os.path.join(S5D, "_prov", n))) for n in sorted(os.listdir(os.path.join(S5D, "_prov"))))
simok = all(md5(os.path.join(S5D, n)) == simcp.get(n) for n in os.listdir(S5D) if os.path.isfile(os.path.join(S5D, n)))
gate("P provisional copies == originals: {0}; sim/ring_p4_s05v18/_prov {1} files".format(cp, len(simcp)),
     all(cp[rel(p[:-5] + "_prov.json")] == w for p, w in PROV_WANT.items()) and simok and len(simcp) >= 35, simcp)
print("FACT PROV-SIM {0}".format(json.dumps(simcp)), flush=True)
print("FACT s01 md5 {0}, s02v18 md5 {1} (ids only); s03 creation map md5 {2}".format(md5(S01), md5(S02), md5(CMAP3)), flush=True)
v18, s01, s02, s03, s04 = J(V18), J(S01), J(S02), J(S03), J(S04)
gate("E4 s04v18 finalized last step file == {0} (pinned md5)".format(rel(END4F)),
     (s04["finalized"]["step_files"][-1]["path"] == rel(END4F)) and s04["finalized"]["step_files"][-1]["md5"] == WANT[END4F], s04["finalized"]["step_files"][-1])
END4 = J(END4F)["state"]
END3 = J(END3F)["state"]
gate("E4b END state sym/neg present", isinstance(END4.get("sym"), dict) and isinstance(END4.get("neg"), int), (END4.get("sym"), END4.get("neg")))
os.makedirs(D5, exist_ok=True)
json.dump(END4, open(PROVB, "w", encoding="utf-8"), separators=(",", ":"), default=str)          # prep_c145_p1_mk.py:63
print("FACT provisional base", rel(PROVB), md5(PROVB), "sym", json.dumps(END4.get("sym")), "neg", END4.get("neg"), "vi md5", END4.get("md5"), flush=True)
A, OPS = v18["actions"], SX.compile_plan(v18)
ids, NOP = [a["id"] for a in A], len(OPS)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
prev3 = [x["id"] for x in s01["actions"]] + [x["id"] for x in s02["actions"]] + [x["id"] for x in s03["actions"]]
prev_ids = prev3 + [x["id"] for x in s04["actions"]]
S4N = max(act2op[n] for n in range(1, len(prev_ids) + 1))
gate("S4 v18 ops 1..{0} = s01's {1} + s02v18's {2} + s03v18's {3} + s04v18's {4} ids".format(S4N, len(s01["actions"]), len(s02["actions"]), len(s03["actions"]),
     len(s04["actions"])), [ids[n - 1] for k in range(1, S4N + 1) for n in OPS[k - 1]["acts"]] == prev_ids and S4N + 1 == CUT_OPS[0])
MODEL = SPR.load_memory_model()
v = lambda k: float(MODEL[k]["value"])                                                      # noqa: E731
BIND = set(k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS)
pos = dict((i, k) for k, i in enumerate(ids, 1))
groups = [(act2op[pos[a["of"]]], act2op[pos[a["id"]]]) for a in A if a.get("of") and a["of"] in pos]
cut_ok = lambda b: b == NOP or not any(lo <= b < hi for lo, hi in groups)                  # noqa: E731
peak = lambda a, b: round(START + len({a, b} | set(k for k in BIND if a < k <= b)) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)   # noqa: E731
fcut = max([b for b in range(S4N + 1, NOP + 1) if peak(S4N, b) <= SPR.X10_FAIL_MB and cut_ok(b)] or [None], key=lambda x: x or 0)
first_over = next((b for b in range(S4N + 1, NOP + 1) if peak(S4N, b) > SPR.X10_FAIL_MB), None)
cut = CUT_OPS[1]
print("FACT X10-FORMULA at {0}: card cut ops {1}..{2} peak {3} (fail_above {4}, MEMSTOP {5}); formula's own longest cut <= {4}: op {6} (peak {7}); "
      "first op over {4}: {8}; next op {9} peak {10}".format(START, S4N + 1, cut, peak(S4N, cut), SPR.X10_FAIL_MB, SX.MEM_STOP_MB, fcut, fcut and peak(S4N, fcut),
                                                             first_over, cut + 1, peak(S4N, cut + 1)), flush=True)
gate("CUT ops {0}..{1} (card) splits no 'of' group".format(S4N + 1, cut), cut_ok(cut), [g for g in groups if g[0] <= cut < g[1]])
ids5 = [ids[n - 1] for k in range(S4N + 1, cut + 1) for n in OPS[k - 1]["acts"]]
subv = dict((SUBVI[i], {"op": act2op[pos[i]], "in_session": S4N < act2op[pos[i]] <= cut}) for i in SUBVI if i in pos)
rest = NOP - cut
print("FACT session 5 = {0} actions {1}..{2}; ops {3}..{4}; peak {5}; margin {6} MB; subVI drops {7}; ops left after s05 {8} of {9}".format(
      len(ids5), ids5[0], ids5[-1], S4N + 1, cut, peak(S4N, cut), round(SPR.X10_FAIL_MB - peak(S4N, cut), 1), subv, rest, NOP), flush=True)
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


def sub(x):                                                                                   # prep_c145_p1_mk.py:94-123, copied
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
        and x[f].split(".")[0] not in made5 and x[f].split(".")[0][:-1] not in made5]
late += [(x["id"], f) for x in keep for f in UIDF + ADDRF if isinstance(x.get(f), dict) and isinstance(x[f].get("uid"), str)
         and x[f]["uid"].startswith("new:") and x[f]["uid"].split(".")[0] not in made5 and x[f]["uid"].split(".")[0][:-1] not in made5]
gate("C2 {0} cross ref(s): s04 symbols -> negative provisional uids, s01..s03 -> real uids {1}; no ref to a later session's symbol".format(
     len(CROSS), [(c["action"], c["symbol"], c["uid"]) for c in CROSS]), not bad and not late, {"bad": bad, "late": late[:8]})
TOP = dict((k, copy.deepcopy(v18[k])) for k in ("schema", "context") if k in v18)
BASEREF = {"path": rel(PROVB), "md5": md5(PROVB), "provisional": True, "sim_of": {"plan": rel(S04), "md5": md5(S04)}}
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_s05v18a", goal="card 145-a2-6 PASS A: P4 v18 session 5 (ops {0}..{1}), no open_rows".format(S4N + 1, cut),
               base=BASEREF, actions=keep), open(AIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(AIN)))
try:
    SA = SS.simulate(AIN, PROVB, out_root=PAROOT, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                         # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
gate("SA pass A replays to its end", SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
ok_pairs = dict(((int(r["node"]), r["term"]), "s04v18-open") for r in s04.get("open_rows") or [])
ties, untied = {}, []
for key in SA["end_cdiff_rows"]:                                                              # prep_c145_p1_mk.py:150-163, copied
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
        orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("c145-a2-6: made by session-5 action {0} (#{1} {2} {3})".format(
            t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "c145-a2-6: open at step 0 = declared open row of plan_ring_p4_s04v18.json")[:300]})
json.dump(dict(TOP, stage="ring_p4_s05v18", goal=("RING P4 v18 LabVIEW session 5 (card 145-a2-6, PD351(d)): v18 ops {0}..{1} ({2} actions) on session 4's "
               "SIMULATED end (plan f349c39a; provisional -> stage_prerun --rebase onto session 4's adopted file's graph 094ba298)").format(S4N + 1, cut, len(keep)),
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
kv, k5 = [o["kind"] for o in OPS[S4N:cut]], [o["kind"] for o in o5]
srx = [(S4N + 1 + j, OPS[S4N + j].get("reg")) for j in range(len(kv)) if j < len(k5) and kv[j] != k5[j]]
kinds_ok = len(kv) == len(k5) and all(kv[j] == k5[j] or (kv[j] == "wire_sr" and k5[j] == "connect" and (str(OPS[S4N + j].get("reg")) in made_prev or str(OPS[S4N + j].get("reg"))[:-1] in made_prev))
                                       for j in range(len(kv)))
print("FACT kind differences v18 -> s05 (op, v18 reg symbol): {0}".format(srx), flush=True)
print("FACT X10s compiled plan N {0} R {1} peak {2} at {3}; ok(<= {4}) {5}; MEMSTOP {6}".format(mp["N"], mp["R"], mp["peak_mb"], START, SPR.X10_FAIL_MB,
      mp["ok"], SX.MEM_STOP_MB), flush=True)
gate("X10s compiled plan: peak {0} == table {1}; kinds == v18 ops {2}..{3} except wire_sr -> connect on an earlier session's register {4} (limit reported, not gated)".format(
     mp["peak_mb"], peak(S4N, cut), S4N + 1, cut, srx), abs(mp["peak_mb"] - peak(S4N, cut)) < 0.05 and kinds_ok, dict(collections.Counter(o["kind"] for o in o5)))
json.dump({"card": "145-a2-6", "v18": {"path": rel(V18), "md5": md5(V18)}, "s04": {"path": rel(S04), "md5": md5(S04)}, "ops": [S4N + 1, cut], "first": ids5[0],
           "last": ids5[-1], "actions": len(keep), "start_mb": START,
           "start_cite": "s04 adopted file D1_ring_p4s04_20261007_215031.vi (95e408ff) MEASURED fresh load 605.4 MB (diag_c145_a2_1_facts.md:15)",
           "peak_mb": peak(S4N, cut), "margin_mb": round(SPR.X10_FAIL_MB - peak(S4N, cut), 1), "next_op": cut + 1, "next_peak_mb": peak(S4N, cut + 1),
           "limit_mb": SPR.X10_FAIL_MB, "memstop_mb": SX.MEM_STOP_MB, "formula_cut": fcut, "first_op_over_limit": first_over, "subvi_drops": subv,
           "cross_refs": CROSS, "real_map": RMAP, "open_rows": len(orows), "end_rows": len(SA["end_cdiff_rows"]), "ops_total": NOP, "ops_left_after": rest,
           "prov_copies": cp, "prov_sim": simcp, "kinds": dict(collections.Counter(o["kind"] for o in o5))}, open(FACTS, "w", encoding="utf-8"), indent=1, default=str)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PROVB, AIN, IN, OUT, FACTS))
gate("U v18 / s04v18 / s03v18 / END step files untouched", all(md5(q) == w for q, w in WANT.items()))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
