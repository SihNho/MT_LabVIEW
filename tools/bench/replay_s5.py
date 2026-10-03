r"""replay_s5 - card chat-S5 (PD337): would 143-1 / 143-3 / 143-4 / 143-5 have resolved WITHOUT a new card under the S1 fix?
OFFLINE, no LabVIEW; every write goes to a temp dir (the real plans, graphs and pred files are only read; md5s checked after).
Inputs (all on disk, md5-pinned below): the s03 stage input plan_ring_p4_s03v18_in.json (= 143-4's plan with 143-5's one-field fix,
prep_c143_5_fix.log: action 1 src #-20 'value' -> 'StopAll'; the replay puts 'value' back = the plan 143-3/143-4 rebased), the
provisional base, the real s02 graph eda9db40, the rebased s03 plan da66a030 (143-5's end state), 143-1's Error List read.
PREDICTION CONTRACT:
  R1 143-3/143-4: rebase of the 'value' plan on eda9db40 -> PASS, REUSE-NOTED 23276, ADDRESS-RESOLVED #-20.'value' (value-alias,
     unique-dir), final; its actions == 143-5's rebased plan's actions in every machine field (why aside).
  R2 negative: the same plan with 'NoSuchName' -> REFUSED with ADDRESS-UNRESOLVED, nothing written outside temp.
  R3 stagesim on the provisional base records finalized.addr_pos for action 1 src: owner -20, index 0, source True.
  R4 143-5 (a): the _in plan + a 545-char why validates; (b) on da66a030 the old token scan finds '-1', negative_uids_left finds none.
  R5 143-1: errorlist_check.by_design on the 110836 read with the 51-entry P3b-2b expectation -> log, re-derived 53 == 53.
  R6 every input md5 unchanged after the run.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/replay_s5.log -- py -u tools/bench/replay_s5.py"""
import copy, hashlib, json, os, shutil, sys, tempfile                                    # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.environ["ADDR_JEV"] = "0"
os.environ["GATE_SOFT_LOG"] = os.path.join(tempfile.gettempdir(), "s5_replay_soft.jsonl")
import protocol as PR, stage_prerun as SPR, stagesim as SS, errorlist_check as EC     # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
IN = {"plan_in": ("plan_ring_p4_s03v18_in.json", "2c2c0edb0457567d6407ea1f1e061b11"),
      "graph": ("graph_ring_p4s02_20261003_112505.json", "eda9db4088d1be89623e6333268e09ff"),
      "prov": ("sim/ring_p4_s03v18_s02end/base_provisional.json", "1181117690431ea67c9a8847266a2192"),
      "s02plan": ("plan_ring_p4_s02v18.json", "e941ebbfaa3d98099bcd10d8c6237ef4"),
      "rebased": ("plan_ring_p4_s03v18.json", "da66a0300851133d93881be3c28f2fdc"),
      "el": ("errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json", None),
      "el_exp51": ("errorlist_expected_D1_ring_p3b2b_20261002_130007.json", None)}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
P = dict((k, os.path.join(B, v[0])) for k, v in IN.items())
G, LOG = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


before = dict((k, md5(p)) for k, p in P.items())
gate("IN md5s as pinned", all(before[k] == v[1] for k, v in IN.items() if v[1]), before)
tmp = tempfile.mkdtemp(prefix="replay_s5_")


def variant(name, term):
    d = json.load(open(P["plan_in"], encoding="utf-8"))
    d["actions"][0]["src"] = {"uid": -20, "term": term}
    p = os.path.join(tmp, name, "plan_ring_p4_s03v18.json")
    os.makedirs(os.path.join(tmp, name, "sim"))
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
    return p


p1 = variant("r1", "value")
L1 = []
ok1, det1 = SPR.rebase(p1, P["graph"], log=lambda s: (L1.append(s), print("  R1| " + s[:300], flush=True)),
                       out_root=os.path.join(tmp, "r1", "sim"))
res = [s for s in L1 if s.startswith("ADDRESS-RESOLVED")]
gate("R1 143-3/143-4 plan ('value') rebases on eda9db40: PASS, REUSE-NOTED 23276, ADDRESS-RESOLVED by position",
     ok1 and any(s.startswith("REUSE-NOTED 23276") for s in L1) and len(res) == 1 and "value-alias" in res[0] and "unique-dir" in res[0],
     [det1] + res)
if ok1:
    a_new = PR.machine_view(json.load(open(p1, encoding="utf-8")), "stageplan")["actions"]
    a_ref = PR.machine_view(json.load(open(P["rebased"], encoding="utf-8")), "stageplan")["actions"]
    diff = [i for i, (x, y) in enumerate(zip(a_new, a_ref), 1) if x != y]
    gate("R1b its actions == 143-5's rebased plan (da66a030) in every machine field; a1 src == {6902,'StopAll'}",
         len(a_new) == len(a_ref) and not diff and a_new[0]["src"] == {"uid": 6902, "term": "StopAll"}, (diff, a_new[0].get("src")))
else:
    gate("R1b skipped (R1 failed)", False, det1)
p2 = variant("r2", "NoSuchName")
L2 = []
ok2, det2 = SPR.rebase(p2, P["graph"], log=lambda s: (L2.append(s), print("  R2| " + s[:300], flush=True)),
                       out_root=os.path.join(tmp, "r2", "sim"))
gate("R2 negative: an unknown name is REFUSED with ADDRESS-UNRESOLVED (+ ADDRESS-LLM-OWED with Jev off)",
     not ok2 and "ADDRESS-UNRESOLVED" in det2 and any(s.startswith("ADDRESS-LLM-OWED") for s in L2), det2)
p3 = variant("r3", "value")
S = SS.simulate(p3, P["prov"], out_root=os.path.join(tmp, "r3", "sim"), plan_out_dir=os.path.join(tmp, "r3"), log=lambda s: None)
fin = json.load(open(os.path.join(ROOT, S["plan_out"]["path"]) if not os.path.isabs(S["plan_out"]["path"]) else S["plan_out"]["path"],
                     encoding="utf-8"))
ap = [r for r in fin["finalized"].get("addr_pos") or [] if r["n"] == 1 and r["source"]]
gate("R3 stagesim records the triple: action 1 src owner -20, index 0, source True ({0} records)".format(
     len(fin["finalized"].get("addr_pos") or [])), S["failed"] is None and len(ap) == 1 and ap[0]["owner"] == -20 and ap[0]["index"] == 0,
     (ap, "final={0}: the route check refuses any PROVISIONAL base (unbound negatives), same for the 'StopAll' variant".format(S["final"])))
d4 = json.load(open(P["plan_in"], encoding="utf-8"))
d4["actions"][0]["why"] = "x" * 545
okv, whyv = PR.validate_obj(d4)
reb = json.load(open(P["rebased"], encoding="utf-8"))
old_neg = [v for a in reb["actions"] for v in json.dumps(a).replace(",", " ").replace("}", " ").split() if v.lstrip("-").isdigit() and v.startswith("-")]
gate("R4 143-5: a 545-char why validates; old scan finds {0}, negative_uids_left finds none".format(old_neg),
     okv and old_neg and SPR.negative_uids_left(reb) == [], (whyv, old_neg, SPR.negative_uids_left(reb)))
R = json.load(open(P["el"], encoding="utf-8"))
exp51 = json.load(open(P["el_exp51"], encoding="utf-8")).get("expected") or []
plan02 = json.load(open(P["s02plan"], encoding="utf-8"))
ex51, mi51, _u = EC.compare(copy.deepcopy(R.get("items") or []), exp51)
R5 = dict(R, extra=ex51, missing=mi51)
bv, brule, bdet = EC.by_design(R5, exp51, plan02, record=False)
gate("R5 143-1: Error List read vs the 51-entry expectation -> extra {0}; by-design verdict log, re-derived == measured".format(len(ex51)),
     bv == "log" and bdet.get("rederived_total") == bdet.get("measured_total") == 53, (bv, brule, {k: bdet.get(k) for k in
     ("extra_classes", "rederived_new", "rederived_total", "measured_total", "base_total")}))
after = dict((k, md5(p)) for k, p in P.items())
gate("R6 every input md5 unchanged", after == before, [k for k in P if after[k] != before[k]])
shutil.rmtree(tmp, ignore_errors=True)
print(PR.result_line(PR.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
