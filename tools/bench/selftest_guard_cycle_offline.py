r"""selftest_guard_cycle_offline.py - card 112-1 T6 (PD225(h)3 (vi); docs/violation-decisions.md device-failed 2026-09-27 22:20).

WHAT EXISTED: selftest_guard_cycle_fixed.py / _rerun.py (premature_build on fabricated files); stop_record.offline_checker
(card 107-1) already exempted `stage_prerun --dry|--prerun` in the LAUNCH gate only. This test drives the REAL hook
(`py tools/hooks/guard_cycle.py`, PreToolUse JSON on stdin) against the REAL state of 2026-09-27 22:2x, in which the
prior-art review archive/peer/2026-09-27-priorart-c111e-l2b2a.md is UNRELEASED for tools/recipes/stage_d1_l2b2a.py.

PREDICTION CONTRACT
  O1 the 22:01:39 argv `py tools/bgrun.py --material --max-min 5 --log tools/bench/plan_l2b2a_dry.log -- py -u
     tools/stage_prerun.py --dry tools/recipes/stage_d1_l2b2a.py` -> ALLOWED (exit 0)
  O2 the same with --prerun, not bgrun-wrapped -> ALLOWED
  O3 `py -u tools/recipes/stage_d1_l2b2a.py` (a LAUNCH) -> REFUSED (exit 2) while the verdict is unreleased
  O4 a dry chained with a launch (`... --dry X && py -u X`) -> REFUSED (one launch segment keeps every gate on)
  O5 offline_only() unit: True for O1/O2, False for O3/O4 and for a command naming no recipe
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_guard_cycle_offline.log -- py -u tools/bench/selftest_guard_cycle_offline.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_cycle as G   # noqa: E402
import protocol           # noqa: E402

R = "tools/recipes/stage_d1_l2b2a.py"
DRY = "py tools/bgrun.py --material --max-min 5 --log tools/bench/plan_l2b2a_dry.log -- py -u tools/stage_prerun.py --dry " + R
PRE = "py -u tools/stage_prerun.py --prerun " + R
LAUNCH = "py -u " + R
CHAIN = "py -u tools/stage_prerun.py --dry {0} && py -u {0}".format(R)
gates = []


def gate(name, ok, detail=""):
    gates.append((name, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(detail)[:300]), flush=True)


def hook(cmd):
    env = dict(os.environ)
    env.pop("CYCLE_GUARD_OFF", None)
    p = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "hooks", "guard_cycle.py")], cwd=ROOT, env=env,
                       input=json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}), capture_output=True,
                       text=True, timeout=180)
    return p.returncode, (p.stderr or "").strip().splitlines()[:1]


rc, why = hook(DRY)
gate("O1 bgrun-wrapped stage_prerun --dry of the unreleased recipe is ALLOWED", rc == 0, (rc, why))
rc, why = hook(PRE)
gate("O2 plain stage_prerun --prerun of the unreleased recipe is ALLOWED", rc == 0, (rc, why))
rc, why = hook(LAUNCH)
gate("O3 the recipe's LAUNCH is still REFUSED while its prior-art verdict is unreleased", rc == 2, (rc, why))
rc, why = hook(CHAIN)
gate("O4 a dry chained with a launch is REFUSED", rc == 2, (rc, why))
u = [G.offline_only(c) for c in (DRY, PRE, LAUNCH, CHAIN, "py -u tools/bench/diag_c112a_peek.py x")]
gate("O5 offline_only: [True, True, False, False, False]", u == [True, True, False, False, False], u)
n_pass = sum(1 for _n, ok in gates if ok)
n_fail = len(gates) - n_pass
first = next((n for n, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, n_fail))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
