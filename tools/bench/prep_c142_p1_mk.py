r"""prep_c142_p1_mk - card 142-P1 pass 2a (OFFLINE, no LabVIEW, no COM, never launched). The REST of the slot-write repair as one
bed session: v17's p4_rp* actions NOT applied by session 1 (plan_ring_p4_s01.json = v17 ops 1..24) plus only the v17 actions they
depend on, planned on the SAME provisional base as plan_ring_p4_s02.json (stagesim END of s01 f4831031, 2d0c2c99) so that
`stage_prerun.py --rebase ... --graph graph_ring_p4s01_20261002_234419.json` (the next step, CLI) binds s01's created objects.
Existing route reused, not rebuilt: prep_c141_p1_mk.py pass 3 (pass A / tie / pass B, copied); the 26 actions are taken from
plan_ring_p4_s02.json (5e483ea6), whose cross-session ref p4_rp29048_out.src is already the provisional uid -13 (RX3).
PREDICTION CONTRACT:
  M0 input md5 == card (v17, s01, s02, s01 graph, provisional base);  R remaining = v17 p4_rp* minus s01 ids = 26 = v17 actions 25..50,
  == s02's p4_rp* ids in order, and each == v17's except the one cross ref;  DEP every 'new:' symbol a remaining action uses is made by
  s01 or by a remaining action (no non-repair dependency), every wire/node uid it names is in the s01 graph;  SA pass A replays to its
  end;  TIE every end row tied;  SB plan FINAL on the provisional base, open_rows_match;  U v17/s01/s02 untouched.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c142_p1_mk.log -- py -u tools/bench/prep_c142_p1_mk.py"""
import copy, hashlib, json, os, sys, traceback                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS                                                                     # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
SIM = os.path.join(B, "sim")
V17, S01, S02 = (os.path.join(B, n) for n in ("plan_ring_p4_v17.json", "plan_ring_p4_s01.json", "plan_ring_p4_s02.json"))
GR = os.path.join(B, "graph_ring_p4s01_20261002_234419.json")
BEDPLAN = os.path.join(B, "plan_ring_p3b2b.json")
PROVB = os.path.join(SIM, "ring_p4_s02_s01end", "base_provisional.json")
DA = os.path.join(SIM, "ring_p4_rasresta")
RAIN, RRIN, RRP = os.path.join(DA, "plan_ring_p4_rasresta_in.json"), os.path.join(B, "plan_ring_p4_rasrest_in.json"), os.path.join(B, "plan_ring_p4_rasrest.json")
WANT = {V17: "e19d7e142fef66f9e118ae4061e9e718", S01: "f4831031c738c997391b5bcace19d9f0", S02: "5e483ea6ccf9897f37da71b975bcde29",
        GR: "f697a0b21c3bdb481207318812a0adad", PROVB: "2d0c2c99a5525713edd638f89229e028"}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
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


def tie_rows(S, keep, ok_pairs):
    """prep_c141_p1_mk.py:74-92 (copied)."""
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


gate("M0 input md5 == card / s02 base", all(md5(p) == w for p, w in WANT.items()), dict((os.path.basename(p), md5(p)) for p in WANT))
if G["fail"]:
    done()
v17, s01, s02, gr = J(V17), J(S01), J(S02), J(GR)
A17, ids1 = v17["actions"], [a["id"] for a in s01["actions"]]
rem = [a for a in A17 if a["id"].startswith("p4_rp") and a["id"] not in ids1]
pos = dict((a["id"], n) for n, a in enumerate(A17, 1))
s02rp = [a for a in s02["actions"] if a["id"].startswith("p4_rp")]
gate("R remaining repair = {0} actions = v17 #{1}..#{2} ({3}..{4}); == s02's p4_rp ids in order".format(
     len(rem), pos[rem[0]["id"]], pos[rem[-1]["id"]], rem[0]["id"], rem[-1]["id"]),
     len(rem) == 26 and [pos[a["id"]] for a in rem] == list(range(25, 51)) and [a["id"] for a in rem] == [a["id"] for a in s02rp])
diff = [(a["id"], sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))) for a, b in zip(rem, s02rp) if a != b]
gate("R2 s02's copies == v17's except the cross-session ref: {0}".format(diff), diff == [("p4_rp29048_out", ["src"])],
     [(b["id"], b.get("src")) for a, b in zip(rem, s02rp) if a != b])
if G["fail"]:
    done()
made1 = set(x["as"] for x in s01["actions"] if x.get("as"))
madeR = set(x["as"] for x in rem if x.get("as"))
made_nr = set(x["as"] for x in A17 if x.get("as") and not x["id"].startswith("p4_rp"))
syms, uids = [], []


def scan(a, v, f):
    if isinstance(v, str) and v.startswith("new:"):
        syms.append((a["id"], f, v[4:].split(".")[0]))
    elif isinstance(v, dict):
        for k, y in v.items():
            scan(a, y, f + "." + k)
    elif isinstance(v, int) and not isinstance(v, bool) and f.split(".")[-1] in ("uid", "wire_uid", "term_uid", "diagram"):
        uids.append((a["id"], f, v))


for a in rem:
    for f in ("src", "dst", "uid", "wire_uid", "diagram", "on", "born_on"):
        if f in a:
            scan(a, a[f], f)
bad_sym = [s for s in syms if s[2] not in made1 | madeR]
nr_sym = [s for s in syms if s[2] in made_nr]
gr_t = set(r["term_uid"] for r in gr["terminals"])
gr_w = set(r["wire_uid"] for r in gr["terminals"] if r["wire_uid"])
gr_o = set(o["uid"] for o in gr["objs"] if isinstance(o, dict))
miss = [u for u in uids if u[2] >= 0 and u[2] not in (gr_t | gr_w | gr_o)]
print("FACT negative (provisional) uids named:", [u for u in uids if u[2] < 0], flush=True)
gate("DEP symbols used {0}: all made by s01 {1} or by the remaining actions {2}; none by a non-repair action; every named uid in the s01 graph".format(
     sorted(set(s[2] for s in syms)), sorted(made1), sorted(madeR)), not bad_sym and not nr_sym and not miss,
     {"bad": bad_sym, "nonrepair": nr_sym, "missing_uids": miss})
print("FACT later v17 actions (#51..) that name a remaining-repair symbol RX4/RX5:", [a["id"] for a in A17[50:] if any(
      s in json.dumps(a) for s in ("new:RX4", "new:RX5"))], flush=True)
if G["fail"]:
    done()
keep = copy.deepcopy(s02rp)
TOP = dict((k, copy.deepcopy(s02[k])) for k in ("schema", "context") if k in s02)
BASEREF = copy.deepcopy(s02["base"])
os.makedirs(DA, exist_ok=True)
json.dump(dict(TOP, stage="ring_p4_rasresta", goal="card 142-P1 PASS A: rest of the slot-write repair (v17 #25..#50), no open_rows", base=BASEREF, actions=keep),
          open(RAIN, "w", encoding="utf-8"), indent=1)
gate("S0 pass-A input validates ({0} actions)".format(len(keep)), *protocol.validate_obj(J(RAIN)))
try:
    SA = SS.simulate(RAIN, PROVB, out_root=SIM, plan_out_dir=DA, log=lambda *x: None, route_check=False)
except Exception as ex:                                                                     # noqa: BLE001
    traceback.print_exc()
    gate("SA pass A simulate returned", False, ex)
    done()
gate("SA pass A replays to its end ({0} end rows)".format(len(SA.get("end_cdiff_rows") or [])), SA["failed"] is None and SA.get("end_cdiff_rows") is not None, SA["failed"])
if G["fail"]:
    done()
bed_pairs = dict(((int(r["node"]), r["term"]), "bed") for r in J(BEDPLAN).get("open_rows") or [])
ok_pairs = dict(((int(r["node"]), r["term"]), "s02-declared") for r in s02.get("open_rows") or [])
ok_pairs.update(bed_pairs)
ties, untied = tie_rows(SA, keep, ok_pairs)
for k in sorted(ties):
    print("TIE", k, json.dumps(dict((x, y) for x, y in ties[k].items() if x != "pair")))
gate("TIE every end row tied to a remaining-repair action or to a step-0 declared pair", not untied, {"untied": untied[:10]})
if G["fail"]:
    done()
orows, seen = [], set()
for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
    t = ties[k]
    if t["pair"] in seen:
        continue
    seen.add(t["pair"])
    why = ("c142-P1: made by rasrest action {0} (#{1} {2} {3})".format(t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else
           "c142-P1: open at step 0 = {0}".format("declared open row of plan_ring_p3b2b.json" if t["id"] == "bed" else "declared open row of plan_ring_p4_s02.json"))
    orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": why[:300]})
json.dump(dict(TOP, stage="ring_p4_rasrest", goal=("RING P4 slot-write repair, REST (card 142-P1; user 2026-10-03, docs/d1/ring-p4b.md:94-103): v17 #25..#50 "
               "({0} actions: finish #29048, repair #29265 and #29316) as ONE bed session on session 1's SIMULATED end (provisional; "
               "stage_prerun --rebase onto D1_ring_p4s01_20261002_232547.vi's graph)").format(len(keep)), base=BASEREF, open_rows=orows, actions=keep),
          open(RRIN, "w", encoding="utf-8"), indent=1)
SB = SS.simulate(RRIN, PROVB, out_root=SIM, plan_out_dir=B, log=lambda *x: None, route_check=False)
p = J(RRP) if os.path.isfile(RRP) else {}
gate("SB rasrest plan FINAL on the provisional base, end rows == pass A, open_rows_match ({0} pairs)".format(len(orows)),
     bool(SB["final"]) and p.get("final") is True and (p.get("finalized") or {}).get("open_rows_match") is True
     and sorted(SB.get("end_cdiff_rows") or []) == sorted(SA["end_cdiff_rows"]) and (p.get("base") or {}).get("provisional") is True,
     {"final": SB["final"], "failed": SB["failed"], "base": p.get("base")})
print("FACT end rows", len(SB.get("end_cdiff_rows") or []), "s02 end rows", len(s02["finalized"]["end_cdiff_rows"]),
      "| rows only in rasrest", sorted(set(SB.get("end_cdiff_rows") or []) - set(s02["finalized"]["end_cdiff_rows"])),
      "| rows only in s02", sorted(set(s02["finalized"]["end_cdiff_rows"]) - set(SB.get("end_cdiff_rows") or [])), flush=True)
ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (RAIN, RRIN, RRP) if os.path.isfile(x))
gate("U v17 / s01 / s02 untouched", md5(V17) == WANT[V17] and md5(S01) == WANT[S01] and md5(S02) == WANT[S02])
done()
