r"""prep_c138_2_x10 - card 138-2 pass 4: X10 rerun (OFFLINE, no LabVIEW, no COM, writes nothing but its log) on the P3b-2
recipes tools/recipes/stage_d1_ring_p3b2a.py and stage_d1_ring_p3b2b.py, after X10 counts whole-VI reads from the SOURCE.
For each: a full dry (stage_prerun.dry, as --prerun does, no record written) -> dry status, the dry-executed whole-VI read count
(trace x10_reads), the Executors the dry built; X10 on that trace. Recipe b's dry stops at K1 (its input VI scratch_c133_6 was
deleted), so b is ALSO modelled on its plan file plan_ring_p3b2b.json (the record x10_capture_executors builds, checkpoints by
the recipe's own rule stage_d1_ring_p3b2b.py:27-28). Recorded preruns to compare: a stage_prerun_c134_p1_p3b2a_prerun.log:101
(R 14, 671.8), b stage_prerun_c134_5_p3b2b_prerun.log:97 (R 12, 667.0).
PREDICTION: source count 2 for each (census_snapshot via `snap` x2); a: dry PASS-or-not printed, X10 PASS, R 16, peak 676.9;
b (plan record): X10 PASS, R 14, peak 672.1; verdicts unchanged (PASS), peaks +5.1 (2 x 2.53).
    py tools/bgrun.py --material --max-min 6 --log tools/bench/prep_c138_2_x10.log -- py -u tools/bench/prep_c138_2_x10.py"""
import builtins, json, os, sys                                                       # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP, protocol as P                                           # noqa: E401,E402
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:600]), flush=True)


def runs_of(det):
    return [dict((k, r.get(k)) for k in ("plan", "N", "exec_R", "R", "exec_peak_mb", "peak_mb", "ok", "src_reads", "dry_reads"))
            for r in det.get("runs") or []]


out = {}
for tag, rn, want_R, want_pk in (("a", "stage_d1_ring_p3b2a.py", 16, 676.9), ("b", "stage_d1_ring_p3b2b.py", 14, 672.1)):
    rp = os.path.join(ROOT, "tools", "recipes", rn)
    src = SP.x10_source_reads(rp)
    SP.D.__init__()
    try:
        tr = SP.dry(rp)
    finally:
        builtins.open = SP.REAL_OPEN
    dry_n = len(tr.get("x10_reads") or [])
    ok, det = SP.x10_gate(rp, tr.get("executors"), trace=tr)
    print("  FACT  {0} {1}: source {2}; dry {3} (first_fail {4!r}), dry-executed reads {5} {6}, executors {7}".format(
        tag, rn, SP.x10_reads_line(src, dry_n), tr.get("status"), str(tr.get("first_fail"))[:160], dry_n,
        tr.get("x10_reads"), len(tr.get("executors") or [])), flush=True)
    print("  FACT  {0} X10 on the dry trace: ok {1}; runs {2}; why {3}".format(tag, ok, runs_of(det), det.get("why")), flush=True)
    if not tr.get("executors"):                                       # b: the dry stopped before its Executor
        pl = json.load(open(os.path.join(B, "plan_ring_p3b2b.json"), encoding="utf-8"))
        import stagexec as SX
        ops = SX.compile_plan(pl)
        rec = {"plan": "tools/bench/plan_ring_p3b2b.json", "kinds": [o["kind"] for o in ops], "stop_after": None,
               "from_step": None, "error": None,
               "checkpoints": sorted({0, len(ops)} | set(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS))}
        ok, det = SP.x10_gate(rp, [rec], trace=tr)
        print("  FACT  {0} X10 on the plan record: ok {1}; runs {2}; why {3}".format(tag, ok, runs_of(det), det.get("why")),
              flush=True)
    r = (det.get("runs") or [{}])[0]
    out[tag] = {"recipe": "tools/recipes/" + rn, "source": src["reads"], "dry_status": tr.get("status"), "dry_reads": dry_n,
                "ok": ok, "R": r.get("R"), "exec_R": r.get("exec_R"), "peak": r.get("peak_mb"), "exec_peak": r.get("exec_peak_mb")}
    gate("{0} {1}: source 2, X10 PASS, R {2} == {3}, peak {4} == {5}".format(tag, rn, r.get("R"), want_R, r.get("peak_mb"), want_pk),
         src["reads"] == 2 and ok is True and r.get("R") == want_R and r.get("peak_mb") == want_pk, out[tag])
print("  FACT  SUMMARY " + json.dumps(out, sort_keys=True), flush=True)
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
