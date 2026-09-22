r"""selftest_guard_bash_jev.py - the two ADVISORY readings added to tools/hooks/guard_bash.py on 2026-09-22
(docs/jev-integration-plan.md second wave #4 drift and #3 pre-flight), tested WITH STUBS AND NO NETWORK.

What is being asserted, once per case, is the property the user's rule actually depends on: these readings
never change whether a command runs. The blocking gates' own outcomes are re-checked here too, because an
advisory wired into the wrong place in main() would be invisible until it silently swallowed a refusal.

    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_guard_bash_jev.log \
        -- py -u tools/bench/selftest_guard_bash_jev.py

NO network: jev.ask is replaced by a counting stub, so a missing key or a dead link cannot change the result.
"""
import io
import json
import os
import sys
import tempfile
from contextlib import redirect_stderr

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, HERE)

import guard_bash  # noqa: E402
import jev  # noqa: E402
import jev_drift  # noqa: E402
import jev_preflight  # noqa: E402

PASS, FAIL = [], []
CALLS = []


def gate(name, ok, detail=""):
    (PASS if ok else FAIL).append(name)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", name, detail))
    sys.stdout.flush()
    return ok


def stub(p_on=0.05, cls="missing-guard", raise_it=False, err=None):
    """Replace jev.ask with a counting stub answering every question this project asks it."""
    def fake(state, questions, purpose="", timeout=60, retries=3):
        CALLS.append(purpose)
        if raise_it:
            raise RuntimeError("stub explodes")
        if err:
            return None, err
        name = list(questions)[0]
        q = questions[name]
        if q.get("type") == "choice":
            keys = list(q.get("criteria") or {"other": ""})
            pick = cls if cls in keys else keys[0]
            return {"answers": {name: {"type": "choice", "choice": pick,
                                       "probabilities": {k: (0.7 if k == pick else 0.1) for k in keys}}}}, None
        return {"answers": {name: {"type": "noul", "noul": p_on}}}, None
    jev.ask = fake


def fresh_state():
    """A private rate-limit state file, so the test never reads or writes the project's."""
    fd, path = tempfile.mkstemp(suffix=".json", prefix="jev_drift_state_")
    os.close(fd)
    os.unlink(path)
    jev_drift.RATE_STATE = path
    return path


def run_main(cmd, background=False, timeout=None):
    """guard_bash.main() over one Bash tool call. Returns (rc, stderr text)."""
    payload = {"tool_name": "Bash", "session_id": "selftest-jev",
               "tool_input": {"command": cmd, "run_in_background": background, "timeout": timeout}}
    old = sys.stdin
    buf = io.StringIO()
    try:
        sys.stdin = io.StringIO(json.dumps(payload))
        with redirect_stderr(buf):
            rc = guard_bash.main()
    finally:
        sys.stdin = old
    return rc, buf.getvalue()


BG = ("py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log "
      "-- py -u tools/bench/diag_c88_brokenwires.py")


def main():
    real_ask = jev.ask
    jev_drift.GATE_LOG = os.path.join(tempfile.gettempdir(), "jev_gate_selftest.log")
    jev_preflight.GATE_LOG = jev_drift.GATE_LOG
    # The synthetic commands below must NEVER reach the real records: tools/hooks/material_marker.log is the
    # audit's count of judgement-session bypasses, and 12 test entries had to be scrubbed from it once before.
    guard_bash.MARKER_LOG = os.path.join(tempfile.gettempdir(), "material_marker_selftest.log")
    jev_drift.MARKER_LOG = os.path.join(ROOT, "tools", "hooks", "material_marker.log")   # read-only use
    print("=== selftest_guard_bash_jev  (stubbed, no network)")

    # C1 a read-only command spends nothing and prints nothing
    fresh_state()
    CALLS.clear()
    stub(p_on=0.02)
    rc, err = run_main("cat tools/bench/diag_c88_brokenwires.py", timeout=10_000)
    gate("C1 a read-only command triggers NO Jev call and no advisory",
         not CALLS and "JEV-" not in err, "rc=%s calls=%d" % (rc, len(CALLS)))

    # C2 an off-task run prints the drift line AND the pre-flight line, and is still allowed
    fresh_state()
    CALLS.clear()
    stub(p_on=0.05, cls="missing-guard")
    rc, err = run_main(BG, background=True)
    gate("C2 an off-task launch prints JEV-DRIFT and does not block",
         rc == 0 and "JEV-DRIFT" in err, "rc=%s calls=%d" % (rc, len(CALLS)))
    gate("C2b the same launch prints JEV-PREFLIGHT for the script after the `--`",
         "JEV-PREFLIGHT" in err, err.strip().splitlines()[-1][:90] if err.strip() else "(no stderr)")

    # C3 an on-task run prints no drift line (the pre-flight line is independent of it)
    fresh_state()
    CALLS.clear()
    stub(p_on=0.95, cls="ready")
    rc, err = run_main(BG, background=True)
    gate("C3 an on-task launch prints NO JEV-DRIFT line and does not block",
         rc == 0 and "JEV-DRIFT" not in err, "rc=%s" % rc)

    # C4 the 60 s rate limit: the second launch in the same session asks nothing
    fresh_state()
    stub(p_on=0.05)
    CALLS.clear()
    run_main(BG, background=True)
    first = len(CALLS)
    run_main(BG, background=True)
    gate("C4 a second launch within 60 s adds no Jev call", len(CALLS) == first,
         "%d then %d" % (first, len(CALLS)))

    # C5 an erroring / exploding Jev is silence, never a refusal
    fresh_state()
    CALLS.clear()
    stub(err="HTTP 500 boom")
    rc1, err1 = run_main(BG, background=True)
    fresh_state()
    stub(raise_it=True)
    rc2, err2 = run_main(BG, background=True)
    gate("C5 a failed or raising reading changes nothing (no line, rc unchanged)",
         rc1 == 0 and rc2 == 0 and "JEV-" not in err1 and "JEV-" not in err2,
         "rc=%s/%s" % (rc1, rc2))

    # C6 the advisory NEVER rescues a command the blocking gates refuse, and never runs for one
    fresh_state()
    CALLS.clear()
    stub(p_on=0.99)
    rc, err = run_main("py tools/bgrun.py --max-min 5 --log tools/bench/x.log "
                       "-- py -u tools/bench/diag_c88_brokenwires.py", background=True)
    # The detail says "code 2", never "rc=2": bgrun's inner-failure scanner matches `rc=<nonzero>` anywhere in
    # a line, so a test that correctly REPORTS a refusal would mark its own passing run as failed.
    gate("C6 an unmarked material run is still blocked (code 2) and costs no Jev call",
         rc == 2 and not CALLS, "code %s calls=%d" % (rc, len(CALLS)))

    # C7 a Jev script of our own never asks about itself
    fresh_state()
    CALLS.clear()
    stub(p_on=0.01)
    rc, err = run_main("py tools/bgrun.py --material --max-min 5 --log tools/bench/jev_x.log "
                       "-- py -u tools/bench/jev_wave2b_trials.py", background=True)
    gate("C7 a jev_* command triggers no reading", not CALLS and "JEV-" not in err,
         "rc=%s calls=%d" % (rc, len(CALLS)))

    # C8 first_act() takes the bullet that says FIRST ACT, not merely the first red one
    txt = ("## NEXT\n"
           "\U0001F534 **STATE: the bed is unchanged and nothing was saved.**\n"
           "\U0001F534 **FIRST ACT - run tools/recipes/stage_x.py from bed Y and save Z.**\n"
           "⚠️ housekeeping\n\n## OTHER\nnot this\n")
    act = jev_drift.first_act(text=txt)
    gate("C8 first_act() picks the FIRST ACT bullet over an earlier red STATE bullet",
         act.startswith("\U0001F534 **FIRST ACT"),
         act[:60].encode("ascii", "backslashreplace").decode("ascii"))   # the console here is cp949

    # C9 the static pre-flight checks run with no model at all
    res, findings = jev_preflight.static_checks(os.path.join(HERE, "diag_c88_brokenwires.py"))
    gate("C9 static_checks() returns the five findings with no Jev call",
         len(findings) >= 5 and res.get("lines", 0) > 0,
         "%d findings, %d lines, stagekit=%s" % (len(findings), res.get("lines"), res.get("stagekit")))

    # C10 is_run_command separates runs from reads
    ok = (jev_drift.is_run_command(BG)
          and not jev_drift.is_run_command("grep -n foo tools/bench/diag_c88_brokenwires.py")
          and not jev_drift.is_run_command("git log --oneline -3")
          and jev_drift.is_run_command("powershell -Command \"& 'tools/peer.ps1' -Agent claude\""))
    gate("C10 is_run_command() accepts launches and rejects reads", ok)

    jev.ask = real_ask
    print("\n=== %d PASS / %d FAIL%s" % (len(PASS), len(FAIL), (": " + ", ".join(FAIL)) if FAIL else ""))
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
