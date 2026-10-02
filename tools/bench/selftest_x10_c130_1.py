r"""selftest_x10_c130_1 - card 130-1 (PD267(b)) self-test of the X10 MODEL in tools/stage_prerun.py. OFFLINE, no LabVIEW, no COM.
FIXTURES FROM GIT (commit d70963a7 = cycle 129's outputs): tools/recipes/stage_d1_ring_p3b1.py (the 129-8 bytes, sha256 cca5d88c,
prerun_records.jsonl:554), tools/bench/plan_ring_p3b1.json (129-8 plan md5 10a0f401) and _pred.json (129-8 pred with memory_pred
688.5) -> tools/bench/sim/x10_c130_1/. The 129-1 bytes are not a separate commit: they are RECONSTRUCTED from the 129-8 bytes by
removing card 129-8's two checkpoint lines and its `checkpoints=` argument + L1 label suffix, and ACCEPTED only when their sha256 ==
e5ebcb03 (prerun_records.jsonl:532, the 129-1 dry). Probe copies (in %TEMP%) differ from those bytes ONLY in the PLAN/PRED literals,
redirected to the fixture copies, so a later re-cut of plan_ring_p3b1.json does not change this test.
PRIOR ART: selftest_stage_prerun_c106c.py (X9/X10 record-based); stage_prerun.x10_probe / x10_gate (this card).
PREDICTION: T1 129-1 bytes -> every-op reads, N 40, R 41, peak 728.9 > 675 FAIL; T2 129-8 bytes -> N 40, BIND 23, R 25, peak 688.5
(== pred memory_pred) FAIL; T3 a recipe naming no plan -> FAIL UNMEASURED; T4 stage_d1_ring_p3a.py (P3a, launched and passed
cycle 124; 22 actions compile to 21 ops) -> PASS (N 21, R 22, 654.6 - run 1 printed it, the prediction said N 22); T5 the model file's every value carries a cite.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_x10_c130_1.log -- py -u tools/bench/selftest_x10_c130_1.py"""
import hashlib, json, os, subprocess, sys, tempfile                                 # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP, protocol as P                                          # noqa: E401,E402
FX = os.path.join(B, "sim", "x10_c130_1")
COMMIT = "d70963a7"
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


def git_bytes(path):
    return subprocess.run(["git", "show", "{0}:{1}".format(COMMIT, path)], cwd=ROOT, capture_output=True, check=True).stdout


os.makedirs(FX, exist_ok=True)
for f in ("plan_ring_p3b1.json", "plan_ring_p3b1_pred.json"):
    b_ = git_bytes("tools/bench/" + f)                       # git stores LF; the working files were written CRLF (Windows
    if b"\r\n" not in b_:                                    # text-mode json.dump), and the pred keys the CRLF plan's md5
        b_ = b_.replace(b"\n", b"\r\n")
    open(os.path.join(FX, f), "wb").write(b_)
pmd5 = hashlib.md5(open(os.path.join(FX, "plan_ring_p3b1.json"), "rb").read()).hexdigest()
pred = json.load(open(os.path.join(FX, "plan_ring_p3b1_pred.json"), encoding="utf-8"))
gate("T0 fixtures from git {0}: plan md5 10a0f401, pred keyed to it, pred memory_pred 688.5".format(COMMIT),
     pmd5 == "10a0f401a877061f224900cf00ed6071" and pred["plan"]["md5"] == pmd5 and pred.get("memory_pred", {}).get("peak_mb") == 688.5,
     (pmd5, pred.get("memory_pred", {}).get("peak_mb")))
r8 = git_bytes("tools/recipes/stage_d1_ring_p3b1.py").decode("utf-8")
L = r8.splitlines(True)
r1 = "".join(ln for ln in L if not ln.startswith(("BIND = set(k for k", "CHECKPOINTS = tuple(sorted(")))
r1 = r1.replace(", checkpoints=CHECKPOINTS)", ")").replace(
    'each action once; checkpoints {2}".format(len(A), len(x.ops), CHECKPOINTS)', 'each action once".format(len(A), len(x.ops))')
sha = lambda t: hashlib.sha256(t.encode("utf-8")).hexdigest()                    # noqa: E731
gate("T0b the 129-8 bytes sha256 == cca5d88c (prerun_records.jsonl:554); reconstructed 129-1 bytes sha256 == e5ebcb03 (:532)",
     sha(r8).startswith("cca5d88c") and sha(r1).startswith("e5ebcb03"), (sha(r8)[:8], sha(r1)[:8]))
tmp = tempfile.mkdtemp(prefix="x10_c130_1_")


def probe_copy(text, name):
    t = text.replace('"plan_ring_p3b1.json")', '"sim", "x10_c130_1", "plan_ring_p3b1.json")').replace(
        '"plan_ring_p3b1_pred.json")', '"sim", "x10_c130_1", "plan_ring_p3b1_pred.json")')
    p = os.path.join(tmp, name)
    open(p, "w", encoding="utf-8").write(t)
    return p


def x10(path):
    ex = SP.x10_probe(path)
    ok, det = SP.x10_gate(path, ex)
    return ok, det


def l0_conditions(tag):
    """card 130-4 P1 (review hyp-c130-3 alt (a)): the recipe's L0 (stage_d1_ring_p3b1.py:33-36) ANDs these 8 atoms but
    prints 3 values; evaluate each atom on the FIXTURE plan/pred the probe copy loads and print it, so a FAIL names its atom."""
    md5f = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                 # noqa: E731
    pl_p = os.path.join(FX, "plan_ring_p3b1.json")
    pl, pr = json.load(open(pl_p, encoding="utf-8")), json.load(open(os.path.join(FX, "plan_ring_p3b1_pred.json"), encoding="utf-8"))
    fz = pl["finalized"]
    bpath = os.path.join(ROOT, fz["base"]["path"])
    base = json.load(open(bpath, encoding="utf-8")) if os.path.isfile(bpath) else {}
    atoms = [("L0.1 plan final", pl.get("final") is True),
             ("L0.2 open_rows_match", fz.get("open_rows_match") is True),
             ("L0.3 plan_in stem endswith plan_ring_p3b1_in", os.path.splitext(fz["plan_in"]["path"])[0].endswith("plan_ring_p3b1_in")),
             ("L0.4 finalized.base.md5 == pred.graph.md5", fz["base"]["md5"] == pr["graph"]["md5"]),
             ("L0.5 pred.graph.md5 == md5(base file {0})".format(fz["base"]["path"]), os.path.isfile(bpath) and pr["graph"]["md5"] == md5f(bpath)),
             ("L0.6 base.md5 == pred.bed_md5", base.get("md5") == pr.get("bed_md5")),
             ("L0.7 sorted(end_cdiff_rows) == pred.cdiff_rows", sorted(fz["end_cdiff_rows"]) == pr.get("cdiff_rows")),
             ("L0.8 pred.plan.md5 == md5(plan)", pr["plan"]["md5"] == md5f(pl_p))]
    for nm, v in atoms:
        print("  {0} {1}: {2}".format(tag, nm, "TRUE" if v else "FALSE"), flush=True)
    return all(v for _n, v in atoms)


# card 132-1 (PD275(a)): the model gained final_read_mb 17.4 (memory_model.json) - both peaks +17.4 (728.9 -> 746.3,
# 688.5 -> 705.9); verdicts unchanged (both > fail_above_mb 690).
# card 133-3 (PD283(e)): the start is the MEASURED load of the input VI (P3a bed 561.8 + op-0 read 5.9 = 567.7, memory_model.json
# load_by_vi / op0_read_mb) instead of start_mb 570.0 - both peaks -2.3 (746.3 -> 744.0, 705.9 -> 703.6); verdicts unchanged.
for tag, text, want in (("T1 129-1 bytes (read after every op)", r1, 744.0), ("T2 129-8 bytes ({0, len} | BIND)", r8, 703.6)):
    gate("{0} L0 atoms on the fixtures: all 8 TRUE".format(tag[:2]), l0_conditions(tag[:2]))
    ok, det = x10(probe_copy(text, tag[:2] + ".py"))
    runs = det.get("runs") or []
    # card 138-2 (PD299(b)): peak_mb now adds the script's source-counted reads; the pinned figure is the Executor-only one
    gate("{0}: X10 FAILS, Executor-only predicted peak {1} (expected {2}; with source reads {3})".format(
        tag, runs[0].get("exec_peak_mb") if runs else None, want, runs[0]["peak_mb"] if runs else None),
         ok is False and len(runs) == 1 and abs(runs[0]["exec_peak_mb"] - want) < 0.05,
         [dict((k, r.get(k)) for k in ("N", "bind", "exec_R", "R", "exec_peak_mb", "peak_mb", "src_reads")) for r in runs] or det)
np_ = os.path.join(tmp, "stage_noplan_c130_1.py")
open(np_, "w", encoding="utf-8").write("import sys\nprint('no plan, no Executor')\nsys.exit(0)\n")
ok, det = x10(np_)
gate("T3 a recipe with no plan: X10 FAILS UNMEASURED", ok is False and str(det.get("why", "")).startswith("UNMEASURED"), det.get("why"))
ok, det = x10(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3a.py"))
runs = det.get("runs") or []
gate("T4 stage_d1_ring_p3a.py (passed cycle 124): X10 PASSES", ok is True and len(runs) == 1,
     [dict((k, r.get(k)) for k in ("N", "bind", "exec_R", "R", "exec_peak_mb", "peak_mb", "src_reads")) for r in runs] or det)
m = SP.load_memory_model()
gate("T5 memory_model.json: start/read/edit/other/fail each {value, cite}", all(m[k]["cite"] for k in
     ("start_mb", "read_mb", "edit_mb", "other_mb", "fail_above_mb")), dict((k, m[k]["value"]) for k in m if isinstance(m[k], dict) and "value" in m[k]))   # card 133-3: load_by_vi has no value
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
