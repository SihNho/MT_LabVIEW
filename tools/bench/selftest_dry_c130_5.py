r"""selftest_dry_c130_5 - card 130-5 (PD268(b), docs/d1/tooling.md:20-38): `stage_prerun --dry` FAILs when a stagexec.Executor
stopped before its plan's last op. PURE PYTHON, no LabVIEW (COM stubbed by stage_prerun.install). Review that found the hole:
archive/peer/2026-10-02-hyp-c130-4-c128b.md (a dry stopped at op 48 of 63 PASSed, stage_prerun.py card 108-5 comment).
EXISTING FIRST: selftest_stage_prerun_c128b.py (in-process main --dry pattern), selftest_x10_c130_1.py (Executor capture).
Prediction contract:
  T1 (only while plan_ring_p3b.json is the STALE 4003eaa5 fixture) main --dry stage_d1_ring_p3b.py -> rc 1, first_fail
     'EXECUTOR-STOP ... executed 47 of 63 ops, stopped IN op ... 48'; otherwise SKIP-as-FACT (the stale plan is gone)
  T2 injected stop (Executor.step raises ExecStop once op K=5 is current) on stage_d1_ring_p3a.py -> rc 1, EXECUTOR-STOP
     'executed 4 of N'
  T3 full run: main --dry stage_d1_ring_p3a.py -> rc 0, DRY PASS, every Executor run completed (executed == planned)
  T4 executor_stops() unit: completed -> [], not run -> EXECUTOR-NOT-RUN, compile error -> [] (X10 reports it)
    py tools/bgrun.py --material --max-min 8 --log tools/bench/selftest_dry_c130_5.log -- py -u tools/bench/selftest_dry_c130_5.py
"""
import builtins, contextlib, hashlib, io, json, os, sys    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)  # noqa: E702
sys.path.insert(0, TOOLS)
import stage_prerun as SP, stagexec as SX, protocol    # noqa: E401,E402
REAL_OPEN = builtins.open
G = []


def gate(l, ok, d=""):
    G.append((l, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:700]), flush=True)


def dry(recipe):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = SP.main(["--dry", recipe, "--no-record"])
        except SystemExit as e:
            rc = e.code
    builtins.open = REAL_OPEN
    out = buf.getvalue()
    dl = [ln for ln in out.splitlines() if ln.startswith("=== DRY")][-1:]
    return rc, dl[0] if dl else None, [dict(plan=x.get("plan"), run=x.get("run")) for x in SP.D.executors]


P3B = os.path.join(TOOLS, "recipes", "stage_d1_ring_p3b.py")
P3A = os.path.join(TOOLS, "recipes", "stage_d1_ring_p3a.py")
pm = hashlib.md5(open(os.path.join(HERE, "plan_ring_p3b.json"), "rb").read()).hexdigest()
print("  FACT plan_ring_p3b.json md5 {0}".format(pm), flush=True)
if pm == "4003eaa587a8c00b4a933f8dab749379":
    rc, dl, ex = dry(P3B)
    print("  FACT T1 rc {0} | {1} | executors {2}".format(rc, dl, json.dumps(ex, default=str)[:600]), flush=True)
    gate("T1 stale P3b (48/63 case): --dry rc 1, EXECUTOR-STOP executed 47 of 63, stopped IN op 48",
         rc == 1 and dl and "EXECUTOR-STOP" in dl and "executed 47 of 63" in dl and "'k': 48" in dl, dl)
else:
    print("  FACT T1 SKIPPED: plan_ring_p3b.json is no longer the stale 4003eaa5 fixture (re-finalized, PD268(c));"
          " T2 reproduces the class by injection", flush=True)

K_STOP = 5
orig_step = SX.Executor.step


def step_inj(self, n):
    if (self.cur or {}).get("k") == K_STOP:
        raise SX.ExecStop("SELFTEST injected stop at op {0}".format(K_STOP))
    return orig_step(self, n)


SX.Executor.step = step_inj
try:
    rc, dl, ex = dry(P3A)
finally:
    SX.Executor.step = orig_step
print("  FACT T2 rc {0} | {1}".format(rc, dl), flush=True)
gate("T2 injected stop at op 5 on stage_d1_ring_p3a.py: --dry rc 1, EXECUTOR-STOP executed 4 of N",
     rc == 1 and dl and "EXECUTOR-STOP" in dl and "executed 4 of" in dl, dl)
rc, dl, ex = dry(P3A)
print("  FACT T3 rc {0} | {1} | executors {2}".format(rc, dl, json.dumps(ex, default=str)[:600]), flush=True)
gate("T3 full run stage_d1_ring_p3a.py: --dry rc 0 PASS, every Executor completed, executed == planned",
     rc == 0 and dl and "DRY PASS" in dl and ex and all(e["run"] and e["run"]["completed"]
                                                        and e["run"]["executed"] == e["run"]["planned"] for e in ex), dl)
u1 = SP.executor_stops([{"plan": "a", "run": {"completed": True, "executed": 3, "planned": 3}}])
u2 = SP.executor_stops([{"plan": "b"}])
u3 = SP.executor_stops([{"plan": "c", "error": "ExecStop: x"}])
gate("T4 executor_stops unit: completed [], not run EXECUTOR-NOT-RUN, compile error []",
     u1 == [] and len(u2) == 1 and u2[0].startswith("EXECUTOR-NOT-RUN") and u3 == [], (u1, u2, u3))
np_, nf = sum(1 for _l, c in G if c), sum(1 for _l, c in G if not c)
print(protocol.result_line(protocol.make_result(np_, nf, next((l for l, c in G if not c), None))), flush=True)
os._exit(1 if nf else 0)
