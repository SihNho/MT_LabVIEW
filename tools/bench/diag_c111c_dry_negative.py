r"""diag_c111c_dry_negative - card 111-3 D1/D2/D5 (docs/violation-decisions.md device-failed 2026-09-27 20:20). OFFLINE: no
LabVIEW, no COM, no stage_prerun record; plan files READ ONLY (md5 checked before/after), every written file in %TEMP%.

NEGATIVE INPUT: the pre-re-cut plan_l2b1_in.json is NOT on disk (git holds one version, 5df38325 = the POST-re-cut input,
plan_l2b1_dry4-6.log DRY PASS; the dry-1..3 inputs f7d3c425 / 56887e7a / 8b9cb7cb were overwritten). It is REBUILT as that
file + the 7 rows the re-cuts moved to B2 (split_plan_110.md:35, ends from diag_c110_terms_bed.log:22-68): the 5
LoopTunnel sinks of plan_l2b1_dry.log:22 (#10004 #30135 #31051 #31137 #30896) and the 2 dead rows of
plan_l2b1_dry3.log:84-85 (rw_403_2282, rw_9306_6142), simulated by stagesim into %TEMP%.
PRIOR ART: stagexec.dry_run / SimBackend / Executor (the code under test), stagexec selftest T29 (2 injected unroutable
rows), selftest_c108e_tools.py (UNROUTABLE_RE). HEAD = `git show HEAD:tools/stagexec.py` loaded as a module.
PREDICTION: N0 HEAD stops before op 1 on the negative (PRIME), naming neither dead row; N1 NEW dry_run FAILs ONCE with exactly
the 7 rows (5 ADDRESS + 2 CONNECT-NO-VERB) named by id; N2 NEW Executor with the pre-J3 checkpoint rule FAILs naming
CHECKPOINT + the same 7 rows, and simulates to the last op; N3 every collected row prints as a line stage_prerun's
UNROUTABLE_RE turns into a dry FAIL; P1 plan_l2b1 / l2a3 / l2a2 dry_run verdicts NEW == HEAD; P2 plan files unchanged.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c111c_dry_negative.log -- py -u tools/bench/diag_c111c_dry_negative.py"""
import copy, hashlib, importlib.util, json, os, subprocess, sys, tempfile      # noqa: E401
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)   # noqa: E702
sys.path.insert(0, TOOLS)
import stagexec as SX, stagesim as SS, stage_prerun as SP, protocol as P          # noqa: E401,E402
print(__doc__, flush=True)
B = os.path.join(TOOLS, "bench"); md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()   # noqa: E702,E731
G = []


def gate(lab, ok, det=""):
    G.append((lab, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:900]), flush=True)   # noqa: E702


PLANS = ["plan_l2b1_in.json", "plan_l2b1.json", "plan_l2a3.json", "plan_l2a2.json"]
M0 = dict((p, md5(os.path.join(B, p))) for p in PLANS)
print("  FACT plan md5 before", M0, flush=True)
TMP = tempfile.mkdtemp(prefix="c111c_neg_")
hp = os.path.join(TMP, "stagexec_head.py")
open(hp, "wb").write(subprocess.run(["git", "show", "HEAD:tools/stagexec.py"], cwd=ROOT, capture_output=True, check=True).stdout)
spec = importlib.util.spec_from_file_location("stagexec_head", hp); HX = importlib.util.module_from_spec(spec)   # noqa: E702
spec.loader.exec_module(HX); HX.HERE, HX.ROOT, HX.BENCH = TOOLS, ROOT, B                                           # noqa: E702
print("  FACT HEAD stagexec md5 {0} (working copy {1})".format(md5(hp), md5(os.path.join(TOOLS, "stagexec.py"))), flush=True)
# ---- the negative input: the 5df38325 input + the 7 rows the re-cuts removed
IN = json.load(open(os.path.join(B, "plan_l2b1_in.json"), encoding="utf-8"))
ROWS = [("rw_8891_10009", 8885, 8891, 10004, 10009), ("rw_8891_30144", 8885, 8891, 30135, 30144),
        ("rw_28170_31055", 28170, 28170, 31051, 31055), ("rw_29091_31158", 29091, 29091, 31137, 31158),
        ("rw_29091_30901", 29091, 29091, 30896, 30901), ("rw_403_2282", 403, 403, 2276, 2282), ("rw_9306_6142", 9306, 9306, 6132, 6142)]
NEG = copy.deepcopy(IN); NEG["stage"] = "c111cneg"; NEG["goal"] = "card 111-3 NEGATIVE: plan_l2b1_in 5df38325 + the 7 pre-re-cut rows"   # noqa: E702
NEG["actions"] += [{"op": "wire", "id": i, "src": {"uid": su, "term_uid": st}, "dst": {"uid": du, "term_uid": dt}} for i, su, st, du, dt in ROWS]
WANT = [r[0] for r in ROWS]
negin = os.path.join(TMP, "plan_c111cneg_in.json"); json.dump(NEG, open(negin, "w", encoding="utf-8"), indent=1)   # noqa: E702
S = SS.simulate(negin, os.path.join(ROOT, IN["base"]["path"]), out_root=os.path.join(TMP, "sim"), plan_out_dir=TMP, log=lambda m: None)
negp = os.path.join(TMP, "plan_c111cneg.json")
print("  FACT negative plan {0} actions, sim failed={1} final={2} end rows {3}".format(len(NEG["actions"]), S["failed"], S["final"],
      len(S["end_cdiff_rows"] or [])), flush=True)
gate("N-SIM the negative plan simulates through all {0} actions (a routability dry needs every step file)".format(len(NEG["actions"])), not S["failed"], S["failed"])


def ids_in(msg):
    return [i for i in WANT if i in (msg or "")]


# N0 HEAD
logs0 = []
st0, ff0, ex0 = HX.dry_run(negp, log=logs0.append, require_final=False)
gate("N0 HEAD dry_run stops BEFORE op 1 on the negative (PRIME), naming neither dead row", st0 == "FAIL" and "stop before op 1" in (ff0 or "")
     and "rw_403_2282" not in (ff0 or "") and "rw_9306_6142" not in (ff0 or ""), (ff0 or "")[:400])
# N1 NEW dry_run (no checkpoint set)
logs1 = []
st1, ff1, ex1 = SX.dry_run(negp, log=logs1.append, require_final=False)
un1 = ex1.be.unroutable
kinds1 = sorted(set(u["err"].split(":")[0] for u in un1))
print("  FACT N1 first_fail: " + (ff1 or "")[:1500], flush=True)
gate("N1 NEW dry_run FAILs ONCE naming exactly the 7 rows {0}".format(WANT), st1 == "FAIL" and (ff1 or "").startswith("UNROUTABLE 7 row(s)")
     and ids_in(ff1) == WANT, {"ids": ids_in(ff1), "kinds": kinds1, "n_records": len(un1)})
gate("N1b the 5 LoopTunnel rows carry ADDRESS (PRIME) and the 2 dead rows CONNECT-NO-VERB; the run reached the last op",
     all(any(u["ids"] == [i] and u["err"].startswith("ADDRESS") for u in un1) for i in WANT[:5])
     and all(any(u["ids"] == [i] and "CONNECT-NO-VERB" in u["err"] for u in un1) for i in WANT[5:])
     and ex1.report[-1].get("k") == len(ex1.ops), {"last_k": ex1.report[-1].get("k"), "ops": len(ex1.ops)})
# N2 NEW Executor with the pre-J3 checkpoint rule (plan_l2b1_dry2.log:22's class)
A = NEG["actions"]; KIND = [a["op"] for a in A]                                   # noqa: E702
CP = tuple(sorted({0, len(A)} | {i + 1 for i in range(len(A) - 1) if KIND[i] != KIND[i + 1]} | set(range(4, len(A), 4 if len(A) < 30 else 6))))
pl, _p = SX.load_final_plan(negp, False)
be2 = SX.SimBackend(pl, SS.base_state(json.load(open(SX._abs(pl["finalized"]["base"]["path"]), encoding="utf-8")), pl.get("context")), SS.load_models())
x2 = SX.Executor(negp, be2, log=lambda m: None, checkpoints=set(CP), require_final=False)
try:
    x2.run(); ff2 = None                                                          # noqa: E702
except SX.ExecStop as e:
    ff2 = str(e)
print("  FACT N2 checkpoints {0}; first_fail: {1}".format(CP, (ff2 or "")[:1500]), flush=True)
gate("N2 NEW Executor, pre-J3 checkpoints: ONE stop naming CHECKPOINT + the 7 rows, after simulating to the last op",
     ff2 is not None and "CHECKPOINT: set" in ff2 and ids_in(ff2) == WANT and ff2.startswith("UNROUTABLE 8 row(s)")
     and x2.report[-1].get("k") == len(x2.ops), {"ids": ids_in(ff2), "pre_op": [u["err"][:60] for u in x2.pre_op_fails]})
lines = ["  FACT  UNROUTABLE acts {0} ids {1}: {2}".format(u["acts"], u["ids"], u["err"]) for u in be2.unroutable] + [x for x in logs1 if "UNROUTABLE" in x]
gate("N3 every collected row prints as a line stage_prerun.UNROUTABLE_RE turns into a dry FAIL ({0} lines)".format(len(lines)),
     lines and all(SP.UNROUTABLE_RE.search(x) for x in lines), [x[:80] for x in lines if not SP.UNROUTABLE_RE.search(x)])
# P1 positive controls: NEW == HEAD on the finalized plans
for pn in ("plan_l2b1.json", "plan_l2a3.json", "plan_l2a2.json"):
    pp = os.path.join(B, pn)
    try:
        h = HX.dry_run(pp, log=lambda m: None)[:2]
    except Exception as e:                                                        # noqa: BLE001
        h = ("ERROR", str(e)[:200])
    try:
        n = SX.dry_run(pp, log=lambda m: None)[:2]
    except Exception as e:                                                        # noqa: BLE001
        n = ("ERROR", str(e)[:200])
    gate("P1 {0}: dry_run verdict NEW == HEAD".format(pn), n[0] == h[0] and (n[0] == "PASS" or (n[1] or "")[:40] == (h[1] or "")[:40]),
         {"head": (h[0], (h[1] or "")[:160]), "new": (n[0], (n[1] or "")[:160])})
M1 = dict((p, md5(os.path.join(B, p))) for p in PLANS)
gate("P2 plan files unchanged (read only)", M1 == M0, M1)
npass = sum(1 for _l, ok in G if ok); nfail = len(G) - npass
first = next((lab for lab, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail  (tmp {2})".format(npass, nfail, TMP), flush=True)
print(P.result_line(P.make_result(npass, nfail, first, status="PASS" if not nfail else "FAIL")), flush=True)
sys.exit(0 if not nfail else 1)
