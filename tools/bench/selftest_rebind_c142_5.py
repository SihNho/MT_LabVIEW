r"""selftest_rebind_c142_5 - card 142-5 (PD330(d)/PD331(d), docs/d1/ring-p4b.md:109,134): stage_prerun.rebind must tell a
terminal uid LabVIEW RE-USED for a new object from the old one, keying terminals by (uid, owner uid, name) as PD325(b) did for
TD (stagekit.term_key). The case is 142-P1's refusal (prep_c142_p1_rebase.log:3): rebase of plan_ring_p4_rasrest.json onto
graph_ring_p4s01_20261002_234419.json, where base 'output array' terminals 28004/28979 of the DELETED #27928/#28916 came back
as terminals of the NEW #6942/#6805 (prep_c142_5_probe.log). Offline; the real plan file is never written (copies in %TEMP%).
PREDICTION (before the fix K1/K2/K3 FAIL with the logged refusal; after the fix all PASS):
  K1 rebind(before, prov, real) returns a binding (no BINDING shape refusal)
  K2 the two created Replace Array Subset nodes bind to #6942 and #6805, and 28004 / 28979 are bound as created terminals
  K3 rebase(simulate=False) of a copy of plan_ring_p4_rasrest.json PASSES with no negative uid left
  K4 a synthetic recycled uid on a node of ANOTHER class still REFUSES (stagexec.uid_reuse kept in front)
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_rebind_c142_5.log -- py -u tools/bench/selftest_rebind_c142_5.py"""
import copy, json, os, sys, shutil, tempfile                                        # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, stage_prerun as SP                                           # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))               # noqa: E731
NP, NF = [0], [None]


def gate(name, ok, val=""):
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:400]), flush=True)
    NP[0] += bool(ok)
    if not ok and NF[0] is None:
        NF[0] = name


PLAN = "tools/bench/plan_ring_p4_rasrest.json"
GRAPH = os.path.join(R, "tools/bench/graph_ring_p4s01_20261002_234419.json")
plan = J(PLAN)
pv = J(plan["base"]["path"])
pn = J(plan["base"]["sim_of"]["plan"])
bn = (pn.get("finalized") or {}).get("base") or pn.get("base")
bf, rl = J(bn["path"]), J("tools/bench/graph_ring_p4s01_20261002_234419.json")
info = {}
M, why = SP.rebind(bf["terminals"], pv["terminals"], rl["terminals"], prov_doc=pv, real_doc=rl, before_doc=bf, info=info)
N = info.get("nodes", {})
print("  FACT  why={0} nodes={1} modes={2}".format(why, N, dict(__import__("collections").Counter(info.get("mode", {}).values()))), flush=True)
gate("K1 rebind returns a binding (no name-free shape refusal)", M is not None, why)
gate("K2 created GrowableFunctions bind to #6942 and #6805; 28004/28979 bound as created terminals",
     M is not None and {6942, 6805} <= set(N.values()) and {28004, 28979} <= set(M.values()),
     (sorted(N.items()), M and sorted(v for v in M.values() if v in (28004, 28979))))
tmp = tempfile.mkdtemp(prefix="c142_5_rebind_")
try:
    pp = os.path.join(tmp, "plan_ring_p4_rasrest_t.json")
    json.dump(plan, open(pp, "w", encoding="utf-8"), indent=1)
    ok, det = SP.rebase(pp, GRAPH, log=lambda s: print("  LOG   " + s, flush=True), simulate=False)
    new = json.load(open(pp, encoding="utf-8"))
    neg = [v for a in new["actions"] for v in json.dumps(a).replace(",", " ").replace("}", " ").split() if v.lstrip("-").isdigit() and v.startswith("-")]
    gate("K3 rebase(simulate=False) of a copy PASSES, no negative uid left", ok and not neg, (det[:300], neg[:6]))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
rl2 = copy.deepcopy(rl["terminals"])
for r in rl2:
    if r["term_uid"] == 28004:
        r["owner_class"] = "Bundler"                                               # recycled uid on a node of ANOTHER class
M4, why4 = SP.rebind(bf["terminals"], pv["terminals"], rl2, prov_doc=pv, real_doc=rl, before_doc=bf)
gate("K4 a recycled uid whose owner class changed still REFUSES (uid_reuse)", M4 is None and "UID-REUSE" in str(why4), why4)
NT = 4
print(P.result_line(P.make_result(NP[0], NT - NP[0], NF[0])), flush=True)
sys.stdout.flush()
os._exit(0 if NP[0] == NT else 1)
