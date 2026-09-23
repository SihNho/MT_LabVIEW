r"""replay_guard_peer_c70 - OFFLINE replay of the cycle-70 launch that guard_peer let through (cycle 71, R1 of the
repair decided in docs/violation-decisions.md `## repeated-failure-class - 2026-09-24 03:53`).

THE CASE. 2026-09-24 03:25:55 (tools/hooks/material_marker.log:1251) `py tools\bgrun.py --material --max-min 45 --log
tools/bench/stage_d1_l7_1_r2.log -- py -u tools/recipes/stage_d1_l7_1.py` launched while tools/bench/stage_d1_l7_1.log
(run 1, rc=1, `  FAIL  P2a ...`) owed a review. No BLOCKED text reached the session; jev_gate.log:473 holds a
JEV-LADDER line at 03:26:08 (13 s after the launch) that says "below 0.80: old path"; BGRUN START is 03:26:11.

WHAT THIS DOES. Rebuilds the state as of 03:25:55 in a temp dir - BENCH = that one failing log, PEER = every
archive/peer/*.md born before the launch (born time preserved), empty Jev caches, LADDER_P = 0.80 (its value then) -
and runs guard_peer.main() on the exact command, timing each stage. No LabVIEW. Jev calls: one ladder, one discharge,
one gate-row advisory (a few cents).

PREDICTION CONTRACT (written before the run):
  P1 newest_failing_log() == stage_d1_l7_1.log
  P2 newest_bound_peer() finds no review (priorart/outcome archives are claude non-hypothesis roles)
  P3 same_row_review() == None
  P4 the ladder returns allow=None (below band -> old path)
  P5 main() returns 2 (a BLOCK) when allowed to run to completion
  P6 the total wall time exceeds 15 s = the hook timeout in .claude/settings.json:64 -> Claude Code treats a timed-out
     PreToolUse hook as non-blocking, so the launch proceeded. If P6 fails, the allow came from somewhere else.
PRIOR ART: tools/bench/selftest_guard_peer_jev.py / _ladder.py / _samerow.py redirect BENCH/PEER the same way.
"""
import glob
import io
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import importlib         # noqa: E402
import jev_gate as jg    # noqa: E402
# argv[1] = the hook module to replay (default the live `guard_peer`; `guard_peer_new` = the repaired candidate).
MODULE = sys.argv[1] if len(sys.argv) > 1 else "guard_peer"
gp = importlib.import_module(MODULE)
CANDIDATE = hasattr(gp, "HOOK_BUDGET_S")
warm_calls = []
if CANDIDATE:
    gp._spawn_warmer = lambda path: (warm_calls.append(path), "warmer stubbed in replay")[1]

LAUNCH = time.mktime(time.strptime("2026-09-24 03:25:55", "%Y-%m-%d %H:%M:%S"))
CMD = ("py tools\\bgrun.py --material --max-min 45 --log tools/bench/stage_d1_l7_1_r2.log -- "
       "py -u tools/recipes/stage_d1_l7_1.py")
HOOK_TIMEOUT_S = 15

tmp = tempfile.mkdtemp(prefix="replay_gp_c70_")
bench, peer = os.path.join(tmp, "bench"), os.path.join(tmp, "peer")
os.makedirs(bench), os.makedirs(peer)
shutil.copy2(os.path.join(ROOT, "tools", "bench", "stage_d1_l7_1.log"), bench)
n_peer = 0
for p in glob.glob(os.path.join(ROOT, "archive", "peer", "*.md")):
    st = os.stat(p)
    born = min(st.st_ctime, st.st_mtime)
    if born < LAUNCH:
        dst = os.path.join(peer, os.path.basename(p))
        shutil.copyfile(p, dst)
        os.utime(dst, (born, born))
        n_peer += 1
gp.BENCH, gp.PEER = bench, peer
gp.GATEROW_STATE = os.path.join(bench, "jev_gaterow_state.json")
jg.PEER, jg.GATE_LOG = peer, os.path.join(bench, "jev_gate.log")
jg.LADDER_P = 0.80
print("replay dir %s ; peer archives born before launch: %d" % (tmp, n_peer))

T0 = time.time()
marks = []


def timed(name, fn):
    def w(*a, **k):
        t = time.time()
        r = fn(*a, **k)
        shown = ("list of %d advisory rows" % len(r)) if isinstance(r, list) else repr(r)[:160]
        marks.append((name, t - T0, time.time() - T0, shown))
        return r
    return w


gp.newest_failing_log = timed("newest_failing_log", gp.newest_failing_log)
gp.newest_bound_peer = timed("newest_bound_peer", gp.newest_bound_peer)
gp.same_row_review = timed("same_row_review", gp.same_row_review)
gp.gaterow_advisory = timed("gaterow_advisory", gp.gaterow_advisory)
jg.jev_ladder = timed("jev_ladder", jg.jev_ladder)
jg.jev_discharge = timed("jev_discharge", jg.jev_discharge)

sys.stdin = io.StringIO(json.dumps({"tool_input": {"command": CMD}}))
err = io.StringIO()
real_err, sys.stderr = sys.stderr, err
try:
    rc = gp.main()
finally:
    sys.stderr = real_err
total = time.time() - T0

for name, a, b, r in marks:
    print("  %-20s start %6.2fs end %6.2fs  -> %s" % (name, a, b, r))
# Report WITHOUT echoing the hook's stderr: it quotes the failing log (`STOP:` rows), and this run's own log must
# not become a failing build log that arms guard_peer against the parallel session.
print("main() returned %s after %.2fs; refusal text present: %s" % (
    rc, total, "BLOCKED by tools/hooks/guard_peer.py" in err.getvalue()))
at15 = [m[0] for m in marks if m[1] <= HOOK_TIMEOUT_S < m[2]]
print("stage executing at t=%ds: %s" % (HOOK_TIMEOUT_S, at15 or "(none - finished or between stages)"))

res = dict((m[0], m) for m in marks)
checks = [
    ("P1 newest failing is stage_d1_l7_1.log", "stage_d1_l7_1.log" in res.get("newest_failing_log", ("", 0, 0, ""))[3]),
    ("P2 no bound peer", "(None," in res.get("newest_bound_peer", ("", 0, 0, ""))[3]),
    ("P3 no same-row review", res.get("same_row_review", ("", 0, 0, ""))[3] == "None"),
    ("P4 ladder allow=None", res.get("jev_ladder", ("", 0, 0, ""))[3].startswith("(None")),
    ("P5 main() would BLOCK (returns 2)", rc == 2),
]
if CANDIDATE:
    # The repaired hook: the same case must BLOCK inside the 15 s hook timeout, with one warmer requested.
    checks[3] = ("P4 (candidate) ladder/discharge cut off by the budget or finished", True)
    checks += [("P6 (candidate) total < %ds hook timeout" % HOOK_TIMEOUT_S, total < HOOK_TIMEOUT_S - 2),
               ("P7 (candidate) one warmer requested", len(warm_calls) == 1)]
else:
    checks += [("P6 total > %ds hook timeout" % HOOK_TIMEOUT_S, total > HOOK_TIMEOUT_S)]
print("module under replay: %s (candidate=%s)" % (MODULE, CANDIDATE))
for label, ok in checks:
    print("  %s  %s" % ("PASS" if ok else "FAIL", label))
shutil.rmtree(tmp, ignore_errors=True)
print("GATES %d pass / %d fail" % (sum(ok for _, ok in checks), sum(not ok for _, ok in checks)))
sys.stdout.flush()
os._exit(0 if all(ok for _, ok in checks) else 1)   # a candidate's cut-off Jev thread must not delay exit
