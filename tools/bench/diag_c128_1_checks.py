"""diag_c128_1_checks - card 128-1 (PD260(b)) OFFLINE (no LabVIEW, no COM): after the frame-keyed multi-object binder
(stagexec.bind_by_frames, called from bind_new for LoopTunnel / FlatSequenceOuterTunnel) re-run 127-4's remaining checks on
the plan of record. EXISTING FIRST: same steps as diag_c127_4_checks.py C2/C4/C5 + diag_c127_4_dryrow.py (re-used, not rebuilt);
C1 (re-simulate) is NOT run, so plan_ring_p3b.json keeps md5 4003eaa5 (127-4 found the resim rewrites it).
  C0 plan md5 == 4003eaa587a8c00b4a933f8dab749379 (plan of record)
  C2a stagexec.dry_run UNFILTERED: the last logged step + status (names the row of any failure)
  C2 stage_prerun --dry / --prerun on plan_ring_p3b.json (recorded in prerun_records)
  C3 plan_ring_p3b_pred.json gets a `checks_128_1` record (dry/prerun outcomes, plan md5); its prediction body is unchanged
  C4 stage_prerun --dry / --prerun on the RECIPE tools/recipes/stage_d1_ring_p3b.py (COM stubbed, NOT launched)
  C5 stage_prerun.scratch_requirement(recipe) -> SCRATCH-REQUIRED / SCRATCH-SKIP-PROVEN, recorded
PREDICTION: C0 PASS; C2a dry PASS past p3b_x_pool; C2 PASS PASS; C3 written; C4 PASS PASS; C5 SCRATCH-REQUIRED; plan md5 unchanged.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c128_1_checks.log -- py -u tools/bench/diag_c128_1_checks.py"""
import contextlib, hashlib, io, json, os, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagexec as SX, stage_prerun as SP     # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()   # noqa: E731
PLAN_MD5 = "4003eaa587a8c00b4a933f8dab749379"
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", n, str(d)[:1500]), flush=True)


def run(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = fn(*a)
        except SystemExit as e:
            rc = e.code
    out = buf.getvalue()
    for ln in [x for x in out.splitlines() if x.startswith(("RESULT", "===", "  FAIL", "FAIL", "SCRATCH", "  WARN", "ADVISORY"))][:40]:
        print("    | " + ln[:600], flush=True)
    return rc, out


po = os.path.join(B, "plan_ring_p3b.json")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b.py")
gate("C0 plan_ring_p3b.json is the plan of record", md5(po) == PLAN_MD5, md5(po))
logs = []
try:
    st, ff, ex = SX.dry_run(po, log=lambda m: logs.append(str(m)))
except SX.ExecStop as e:
    st, ff, ex = "FAIL", str(e), None
steps = [x for x in logs if x.lstrip().startswith(("STEP", "STEPX"))]
print("  FACT dry log lines {0}, STEP lines {1}; last 6 STEP lines:".format(len(logs), len(steps)), flush=True)
for x in steps[-6:]:
    print("    | " + x[:500], flush=True)
print("  FACT dry cur {0}".format(getattr(ex, "cur", None)), flush=True)
gate("C2a stagexec dry_run (unfiltered) PASS past p3b_x_pool", st == "PASS", str(ff)[:800])
res = {}
for mode in ("--dry", "--prerun"):
    rc, out = run(SP.main, [mode, po])
    res[mode] = [ln for ln in out.splitlines() if ln.startswith("RESULT")]
    gate("C2 stage_prerun {0} on plan_ring_p3b.json PASS".format(mode), rc == 0, res[mode])
    if rc != 0:
        break
c2_ok = sum(1 for n, c in ok if n.startswith("C2 ") and c) == 2
PO = os.path.join(B, "plan_ring_p3b_pred.json")
pred = json.load(open(PO, encoding="utf-8"))
pred["checks_128_1"] = {"card": "128-1", "plan_md5": md5(po), "binder": "stagexec.bind_by_frames (frame-keyed, B3 self-test T128a-d)",
                        "dry_unfiltered": {"status": st, "first_fail": str(ff)[:400] if ff else None, "steps_logged": len(steps)},
                        "stage_prerun": res, "pred_keyed_to_plan": (pred.get("plan") or {}).get("md5")}
if c2_ok:
    for mode in ("--dry", "--prerun"):
        rc, out = run(SP.main, [mode, REC])
        res["recipe " + mode] = [ln for ln in out.splitlines() if ln.startswith(("RESULT", "=== "))]
        gate("C4 stage_prerun {0} on the recipe (COM stubbed, NOT launched) PASS".format(mode), rc == 0, res["recipe " + mode])
        if rc != 0:
            break
    req, why, st_ = SP.scratch_requirement(REC)
    line = ("SCRATCH-REQUIRED | {0} | {1}".format(SP.stage_key(REC), why) if req else
            "SCRATCH-SKIP-PROVEN | {0} | proven: {1}".format(SP.stage_key(REC), ", ".join(st_)))
    print("  FACT " + line, flush=True)
    pred["checks_128_1"]["scratch"] = line
    gate("C5 --scratch-required decision recorded (predicted SCRATCH-REQUIRED)", req, line)
json.dump(pred, open(PO, "w", encoding="utf-8"), indent=1)
gate("C3 plan_ring_p3b_pred.json checks_128_1 written; plan md5 unchanged", md5(po) == PLAN_MD5, {"pred_md5": md5(PO), "plan": md5(po)})
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None),
                                  [{"path": "tools/bench/plan_ring_p3b_pred.json", "md5": md5(PO)}])), flush=True)
sys.exit(1 if nf else 0)
