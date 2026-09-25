"""dry_l2a1_86-4_cp - card 86-4: the real L2-A1 plan dry-run on SimBackend WITH the PD193 checkpoint set
{0,15,19,23,27,28,40,41,42} (stage_d1_l2a1.CHECKPOINTS). No LabVIEW. PRIOR ART: stagexec.dry_run (no checkpoints).
PREDICTION: binding ops (add_sr/tunnel) are a subset of the set; 42 ops; run PASS; reads real == 8 non-zero set members;
0 unroutable rows."""
import os, sys                                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagexec as SX, stagesim as SS, protocol                                     # noqa: E401,E402
CP = (0, 15, 19, 23, 27, 28, 40, 41, 42)
p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sim", "l2a1", "plan_l2a1.json")
plan, _ = SX.load_final_plan(p)
base = SX._j(SX._abs(plan["finalized"]["base"]["path"]))
be = SX.SimBackend(plan, SS.base_state(base, plan.get("context")), SS.load_models())
ex = SX.Executor(p, be, log=lambda *a: None, checkpoints=CP)
bind = [k for k, o in enumerate(ex.ops, 1) if o["kind"] in ("add_sr", "tunnel")]
print("binding ops", bind, "n ops", len(ex.ops), flush=True)
err = None
try:
    ex.run()
except SX.ExecStop as e:
    err = str(e)[:600]
print("exc", err, "\nreads real", ex.reads_real, "skipped", len(ex.reads_skipped), "retries", ex.stale_retries,
      "unroutable", be.unroutable, flush=True)
ok = [err is None, set(bind) <= set(CP), len(ex.ops) == 42, ex.reads_real == [k for k in CP if k], not be.unroutable]
print(protocol.result_line(protocol.make_result(sum(ok), len(ok) - sum(ok), None if all(ok) else "checkpoint dry: " + str(ok))))
sys.exit(0 if all(ok) else 1)
