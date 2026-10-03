r"""selftest_rebase_uidreuse_c143_4 - card 143-4 (PD334(b), docs/d1/ring-p4b.md:187): in `stage_prerun --rebase` ONLY, a uid
LabVIEW re-issued between N's base and the real graph of N's artefact is FATAL only when the plan being rebased NAMES it;
otherwise rebase logs `REUSE-NOTED <uid> <old>-><new>` and binds by (uid, owner, name). Execution-time stagexec.uid_reuse
callers are untouched (a direct rebind() call without `named` still refuses, K4 of selftest_rebind_c142_5).
Existing pieces checked first: stagexec.uid_reuse (stagexec.py:942), stage_prerun.rebind/rebase/carry_fs, stagexec._ints_in,
selftest_rebind_c142_5 (28004/28979 case). Offline; real plan files are never written (copies + out_root in %TEMP%).
PREDICTION (before the fix U1 FAILS with 143-3's refusal, prep_c143_3_rebase.log:3; after the fix all PASS):
  U1 (i)  rebase(simulate=False) of a copy of plan_ring_p4_s03v18.json on graph_ring_p4s02 PASSES, logs REUSE-NOTED 23276
  U2 (ii) the same copy with one action naming uid 23276 -> REFUSED 'UID-REUSE ... the plan NAMES'
  U3 (ii') rasrest rebind with named={28004} (same class, owner changed) -> REFUSED; with its own named set -> binds
  U4 (iii) rebase of a copy of plan_ring_p4_rasrest.json on graph_ring_p4s01 PASSES, 28004/28979 bound (as c142_5 K2/K3)
  U5 a direct rebind() without `named` on the s03 case still refuses UID-REUSE (default unchanged)
  U6 carry_fs/rebind object identity: an FS object whose uid was another class in N's base counts as NEW (_obj_id)
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_rebase_uidreuse_c143_4.log -- py -u tools/bench/selftest_rebase_uidreuse_c143_4.py"""
import json, os, sys, shutil, tempfile                                              # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, stage_prerun as SP                                           # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))               # noqa: E731
NP, NF, NT = [0], [None], 6


def gate(name, ok, val=""):
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:500]), flush=True)
    NP[0] += bool(ok)
    if not ok and NF[0] is None:
        NF[0] = name


def docs(plan):
    pn = J(plan["base"]["sim_of"]["plan"])
    bn = (pn.get("finalized") or {}).get("base") or pn.get("base")
    return J(bn["path"]), J(plan["base"]["path"])


def rebase_copy(plan, graph, tmp, tag):
    pp = os.path.join(tmp, "{0}.json".format(tag))
    json.dump(plan, open(pp, "w", encoding="utf-8"), indent=1)
    lines = []
    ok, det = SP.rebase(pp, os.path.join(R, graph), log=lines.append, simulate=False, out_root=tmp)
    for s in lines:
        print("  LOG   " + s[:300], flush=True)
    return ok, det, lines, json.load(open(pp, encoding="utf-8"))


S03, G02 = "tools/bench/plan_ring_p4_s03v18.json", "tools/bench/graph_ring_p4s02_20261003_112505.json"
RAS, G01 = "tools/bench/plan_ring_p4_rasrest.json", "tools/bench/graph_ring_p4s01_20261002_234419.json"
tmp = tempfile.mkdtemp(prefix="c143_4_uidreuse_")
try:
    p3 = J(S03)
    ok, det, lines, _n = rebase_copy(p3, G02, tmp, "s03_u1")
    gate("U1 s03 rebase on s02 graph PASSES and logs REUSE-NOTED 23276", ok and any(s.startswith("REUSE-NOTED 23276 ") for s in lines),
         det[:300])
    p3b = json.loads(json.dumps(p3))
    p3b["actions"][0]["dst"] = dict(p3b["actions"][0]["dst"], uid=23276)          # the plan now NAMES the re-issued uid
    ok2, det2, _l, _n = rebase_copy(p3b, G02, tmp, "s03_u2")
    gate("U2 a plan naming re-issued uid 23276 is REFUSED (UID-REUSE ... NAMES)", not ok2 and "UID-REUSE" in det2 and "NAMES" in det2
         and "23276" in det2, det2[:300])
    pr = J(RAS)
    bf, pv = docs(pr)
    rl = J(G01)
    M3, why3 = SP.rebind(bf["terminals"], pv["terminals"], rl["terminals"], prov_doc=pv, real_doc=rl, before_doc=bf, named={28004})
    M3b, why3b = SP.rebind(bf["terminals"], pv["terminals"], rl["terminals"], prov_doc=pv, real_doc=rl, before_doc=bf,
                           named=SP.plan_named_uids(pr))
    gate("U3 owner-changed uid 28004 named -> REFUSED; rasrest's own named set -> binds",
         M3 is None and "28004" in str(why3) and M3b is not None, (why3, why3b))
    ok4, det4, _l, n4 = rebase_copy(pr, G01, tmp, "ras_u4")
    info4 = {}
    M4, _w = SP.rebind(bf["terminals"], pv["terminals"], rl["terminals"], prov_doc=pv, real_doc=rl, before_doc=bf, info=info4,
                       named=SP.plan_named_uids(pr))
    neg = [v for a in n4["actions"] for v in json.dumps(a).replace(",", " ").replace("}", " ").split()
           if v.lstrip("-").isdigit() and v.startswith("-")]
    gate("U4 rasrest rebase PASSES, 28004/28979 bound, no negative uid left",
         ok4 and not neg and M4 is not None and {28004, 28979} <= set(M4.values()) and {6942, 6805} <= set(info4["nodes"].values()),
         (det4[:200], neg[:6]))
    b3, v3 = docs(p3)
    M5, why5 = SP.rebind(b3["terminals"], v3["terminals"], J(G02)["terminals"], prov_doc=v3, real_doc=J(G02), before_doc=b3)
    gate("U5 direct rebind without named still refuses UID-REUSE (default unchanged)", M5 is None and "UID-REUSE" in str(why5), why5)
    bd = {"objs": [{"uid": 900001, "class": "Comparison", "owner": "Diagram"}]}
    rd = {"objs": [{"uid": 900001, "class": "FlatSequence", "owner": "TopLevelDiagram"}]}
    gate("U6 _obj_id: a uid re-issued to another class is NEW (FS identity, not raw uid)",
         SP._obj_id(bd).get(900001) != (rd["objs"][0]["class"], rd["objs"][0]["owner"]), (SP._obj_id(bd), SP._obj_id(rd)))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print(P.result_line(P.make_result(NP[0], NT - NP[0], NF[0])), flush=True)
sys.stdout.flush()
os._exit(0 if NP[0] == NT else 1)
