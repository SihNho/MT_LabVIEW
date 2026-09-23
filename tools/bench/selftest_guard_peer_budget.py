r"""selftest_guard_peer_budget.py - the self-test demanded by docs/violation-decisions.md
`## repeated-failure-class - 2026-09-24 03:53`: "a newer failing build log that owes a review and has no discharge
line blocks the next launch of the same recipe".

MEASURED CAUSE (tools/bench/replay_guard_peer_c70.py -> tools/bench/replay_guard_peer_c70.log): on the cycle-70
state guard_peer.main() DOES return 2, but only after 127-139 s of Jev calls (ladder 22-48 s, discharge 70-98 s,
gate-row advisory 9-18 s); `.claude/settings.json` gives the hook 15 s and Claude Code lets a timed-out PreToolUse
hook's tool call through. The repair (guard_peer.HOOK_BUDGET_S) bounds the Jev rungs and fails CLOSED.

    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_guard_peer_budget.log -- \
        py -u tools/bench/selftest_guard_peer_budget.py            (env GUARD_PEER_UNDER_TEST=guard_peer_new for a copy)

NO LabVIEW, NO API call: every Jev rung is a stub; "slow" = a stub that sleeps past the budget.
PREDICTION CONTRACT (budget set to 2.0 s here)
  B1 run 1 reviewed, run 2 (newer) failing with no review/discharge, the ladder hangs    -> 2 in < 3.5 s, warmer asked once
  B2 same, the ladder answers "below: old path" at once and the DISCHARGE hangs (the live -> 2 in < 3.5 s, JEV-BUDGET line
     cycle-70 shape)
  B3 the ladder answers allow=True at once                                                -> 0 (the budget does not eat allows)
  B4 the discharge grants at once                                                         -> 0
  B5 no key (both rungs return at once with nothing)                                      -> 2, NO warmer asked
  B6 _spawn_warmer twice for one log (Popen stubbed)                                      -> started, then already warming
  B7 the hook file as a real process: a non-build command, and `--warm <missing file>`    -> exit 0 both, < 10 s
"""
import importlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for _p in (TOOLS, HERE, os.path.join(TOOLS, "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import jev_gate  # noqa: E402
MOD = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GUARD_PEER_UNDER_TEST", "guard_peer")
gp = importlib.import_module(MOD)

passes, fails = [], []


def gate(ok, label, detail=""):
    (passes if ok else fails).append(label)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)   # the documented emitter (37(i))


LOG = ("BGRUN START 2026-09-24 03:%s limit 45 min: py -u tools/recipes/stage_fixture.py\n"
       "  PASS  P1 move done\n  " + "FAIL" + "  P2a init: every Jev row acts\n")
REVIEW = ("# r1\n\n- **agent:** claude\n- **role:** hypothesis\n- **model:** opus (effort max)\n- **outcome:** ANSWERED (90s)\n"
          "\n## Question\n\nATTACK run 1 of stage_fixture_r1.log\n\n## Answer\n\nno.\n")


def fixture(tmp, tag):
    bench, peer = os.path.join(tmp, tag, "bench"), os.path.join(tmp, tag, "peer")
    os.makedirs(bench), os.makedirs(peer)
    now = time.time()
    r1 = os.path.join(bench, "stage_fixture_r1.log")
    open(r1, "w", encoding="utf-8").write(LOG % "10:33")
    os.utime(r1, (now - 900, now - 900))
    rv = os.path.join(peer, "2026-09-24-r1-review.md")        # reviews run 1 only, OLDER than run 2, and 7 h old
    open(rv, "w", encoding="utf-8").write(REVIEW)             # (outside SAME_ROW_AGE_S, so it cannot cite by row)
    os.utime(rv, (now - 7 * 3600, now - 7 * 3600))
    r2 = os.path.join(bench, "stage_fixture_r2.log")
    open(r2, "w", encoding="utf-8").write(LOG % "26:11")
    os.utime(r2, (now - 60, now - 60))
    gp.BENCH, gp.PEER = bench, peer
    gp.WARM_STATE = os.path.join(bench, "jev_warm_state.json")
    gp.GATEROW_STATE = os.path.join(bench, "jev_gaterow_state.json")
    jev_gate.PEER, jev_gate.GATE_LOG = peer, os.path.join(bench, "jev_gate.log")
    return bench


def run_main():
    cmd = "py tools\\bgrun.py --material --max-min 45 --log tools/bench/stage_fixture_r3.log -- py -u tools/recipes/stage_fixture.py"
    old_in, old_err = sys.stdin, sys.stderr
    sys.stdin, sys.stderr = io.StringIO(json.dumps({"tool_input": {"command": cmd}})), io.StringIO()
    t = time.time()
    try:
        rc = gp.main()
    finally:
        err = sys.stderr.getvalue()
        sys.stdin, sys.stderr = old_in, old_err
    return rc, time.time() - t, err


def slow(*a, **k):
    time.sleep(30)
    return None, None


def main():
    print("=== selftest_guard_peer_budget on %s (%s) ===" % (MOD, gp.__file__), flush=True)
    if not hasattr(gp, "HOOK_BUDGET_S"):
        gate(False, "B0 the module under test has a Jev budget (HOOK_BUDGET_S)", "absent - pre-repair hook")
        print("\n=== selftest_guard_peer_budget: %d pass, %d fail ===" % (len(passes), len(fails)), flush=True)
        return 1
    gp.HOOK_BUDGET_S = 2.0
    warm = []
    real_spawn = gp._spawn_warmer
    gp._spawn_warmer = lambda path: (warm.append(path), "warmer stubbed")[1]
    gp.gaterow_advisory = lambda path: []
    orig = (jev_gate.jev_ladder, jev_gate.jev_discharge)
    tmp = tempfile.mkdtemp(prefix="gp_budget_")
    try:
        bench = fixture(tmp, "b1")
        jev_gate.jev_ladder, jev_gate.jev_discharge = slow, slow
        rc, dt, err = run_main()
        gate(rc == 2 and dt < 3.5 and len(warm) == 1 and "BLOCKED by tools/hooks/guard_peer.py" in err,
             "B1 newer unreviewed failure + hanging ladder BLOCKS inside the budget",
             "returned %s after %.1fs, warmers %d" % (rc, dt, len(warm)))
        glog = open(os.path.join(bench, "jev_gate.log"), encoding="utf-8").read()
        gate("JEV-BUDGET | " in glog and "stage_fixture_r2.log" in glog, "B1b the JEV-BUDGET line names run 2's log")

        fixture(tmp, "b2")
        warm.clear()
        jev_gate.jev_ladder = lambda *a, **k: (None, "JEV-LADDER | x | stage_fixture_r2.log | new-problem p=0.74 | below")
        jev_gate.jev_discharge = slow
        rc, dt, err = run_main()
        gate(rc == 2 and dt < 3.5 and len(warm) == 1, "B2 fast ladder + hanging discharge (the live cycle-70 shape) BLOCKS",
             "returned %s after %.1fs, warmers %d" % (rc, dt, len(warm)))

        fixture(tmp, "b3")
        warm.clear()
        jev_gate.jev_ladder = lambda *a, **k: (True, "JEV-LADDER | x | our-script-bug p=0.9 | ALLOW")
        rc, dt, err = run_main()
        gate(rc == 0 and not warm, "B3 a fast ladder ALLOW still allows", "returned %s after %.1fs" % (rc, dt))

        fixture(tmp, "b4")
        jev_gate.jev_ladder = lambda *a, **k: (None, None)
        jev_gate.jev_discharge = lambda *a, **k: (True, "JEV-DISCHARGE | x | stage_fixture_r2.log covered by r p=0.9")
        rc, dt, err = run_main()
        gate(rc == 0 and not warm, "B4 a fast discharge grant still allows", "returned %s after %.1fs" % (rc, dt))

        fixture(tmp, "b5")
        jev_gate.jev_discharge = lambda *a, **k: (False, None)
        rc, dt, err = run_main()
        gate(rc == 2 and not warm and dt < 1.5, "B5 no key: blocks at once, no warmer", "returned %s after %.1fs" % (rc, dt))

        b6 = fixture(tmp, "b6")
        started = []

        class FakePopen:
            def __init__(self, argv, **kw):
                started.append(argv)
        real_popen, subprocess.Popen = subprocess.Popen, FakePopen
        try:
            s1 = real_spawn(os.path.join(b6, "stage_fixture_r2.log"))
            s2 = real_spawn(os.path.join(b6, "stage_fixture_r2.log"))
        finally:
            subprocess.Popen = real_popen
        gate(s1 == "warmer started" and s2 == "already warming" and len(started) == 1
             and started[0][-2] == "--warm", "B6 one warmer per log revision", "%s / %s / %d" % (s1, s2, len(started)))
    finally:
        jev_gate.jev_ladder, jev_gate.jev_discharge = orig

    hook = os.path.abspath(gp.__file__)
    t = time.time()
    p1 = subprocess.run([sys.executable, hook], input=json.dumps({"tool_input": {"command": "ls tools"}}),
                        capture_output=True, text=True, timeout=30)
    p2 = subprocess.run([sys.executable, hook, "--warm", os.path.join(tmp, "missing.log")],
                        capture_output=True, text=True, timeout=30)
    gate(p1.returncode == 0 and p2.returncode == 0 and time.time() - t < 10,
         "B7 the file runs as a hook process and as a warmer", "exits %d/%d in %.1fs" % (p1.returncode, p2.returncode,
                                                                                         time.time() - t))
    # R1..R4: every EXISTING guard_peer self-test, re-run on the same module (they honour GUARD_PEER_UNDER_TEST).
    env = dict(os.environ, GUARD_PEER_UNDER_TEST=MOD)
    for tag, name in (("R1", "selftest_guard_peer_failre.py"), ("R2", "selftest_guard_peer_jev.py"),
                      ("R3", "selftest_guard_peer_ladder.py"), ("R4", "selftest_guard_peer_samerow.py")):
        p = subprocess.run([sys.executable, "-u", os.path.join(HERE, name)], env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=600)
        tail = [ln.strip() for ln in (p.stdout or "").splitlines() if ln.strip()][-1:] or [""]
        ok = p.returncode == 0
        if tag == "R1" and not ok:
            # E1 scans tools/bench/*.py SOURCES for bold emitters, not the hook: diag_c83_connect2x2.py:143,
            # diag_c83_connect2x2_r2.py:132 and diag_c86_norbw.py:175 fail it on the LIVE guard_peer as well
            # (tools/bench/selftest_guard_peer_failre.log, 25/1 on 2026-09-24 04:2x). Only that row may differ.
            ok = "/ 1 fail ===" in (p.stdout or "") and tail[0].startswith("not passing: E1 ")
        gate(ok, "%s existing %s passes on %s" % (tag, name, MOD),
             "exit %d; last line: %s" % (p.returncode, tail[0][:140]))
    print("\n=== selftest_guard_peer_budget: %d pass, %d fail ===" % (len(passes), len(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    rc = main()
    sys.stdout.flush()
    os._exit(rc)       # the slow stubs' daemon threads are still sleeping
