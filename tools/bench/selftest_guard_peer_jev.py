r"""selftest_guard_peer_jev.py - does the JEV-DISCHARGE branch of tools/hooks/guard_peer.py do what it claims?

NO LabVIEW, and NO API CALL in the branch cases: `jev_gate.covers_failure` is stubbed with a fixed probability,
so each branch is exercised deterministically and for free. One OPTIONAL live case runs at the end when
TYPESAFE_API_KEY is visible, to prove the wiring reaches the real transport.

The fake log and the fake review live in a temp directory and `guard_peer.BENCH` / `guard_peer.PEER` /
`jev_gate.PEER` / `jev_gate.GATE_LOG` are pointed at it for the duration. NOTHING under tools/bench/ or
archive/peer/ is written by this file - deliberately: a fixture that is failure-shaped by construction must never
become the newest failing log of the real gate (the regression already recorded at guard_peer.py's
SELFTEST_LOG_RE, where exactly that happened on 2026-09-20).

Prints the project's documented gate rows (`  PASS  ` / `  FAIL  `, never the markdown-bold form).
"""
import json
import io
import os
import shutil
import sys
import tempfile
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for _p in (TOOLS, HERE, os.path.join(TOOLS, "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import jev            # noqa: E402
import jev_gate       # noqa: E402
import importlib      # noqa: E402
guard_peer = importlib.import_module(os.environ.get("GUARD_PEER_UNDER_TEST", "guard_peer"))  # override: a candidate copy

NPASS = NFAIL = 0


def gate(ok, label, detail=""):
    global NPASS, NFAIL
    if ok:
        NPASS += 1
        print("  PASS  %s  %s" % (label, detail))
    else:
        NFAIL += 1
        global FIRST_FAIL
        FIRST_FAIL = FIRST_FAIL or label
        print("  FAIL  %s  %s" % (label, detail))


FIRST_FAIL = None


# THE FIXTURE'S FAILURE MARKER IS `STOP:`, NOT `FAIL`, AND THAT IS DELIBERATE. guard_peer.FAILURE_RE matches
# both, so the gate sees this log either way - but guard_peer ECHOES the first failure line into its block
# message, and bgrun's inner-failure scanner then reads this test's own stdout as four real failures and ends
# `BGRUN END rc=1` on a 15-pass/0-fail run (measured here, first run, 2026-09-22 08:43). A self-test whose rc can
# never be 0 cannot be told apart from a broken one, and tools/cycle_runner.py counts repeated rc!=0 on one script
# toward a firefighter cycle. Same class as the carve-out guard_peer.SELFTEST_LOG_RE already documents: a file
# full of failure-shaped text by construction. Fixed at the FIXTURE, not by loosening any scanner.
FAKE_LOG = """BGRUN START 2026-09-22 09:00:00 limit 10 min: py -u tools/recipes/fake_stage.py
  PASS  A1 the bed md5 is unchanged
STOP: A2 THE WIDGET RESOLVED - widget #4242 appears exactly once on Frobnicator #99's terminal table
      FAILED PREDICTION - Frobnicator #99 did not resolve to a readable Nodes[] terminal table
  FACT  A2 Frobnicator #99 lives at: None (173 diagrams scanned)
BGRUN END rc=1 after 61s
"""

FAKE_REVIEW = """# fake-widget-failpred

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max)
- **kind:** review
- **outcome:** ANSWERED (400s)

## Question

# FAILED PREDICTION - fake stage, run 1, log tools/bench/fake_stage.log

PREDICTED: widget #4242 is indexed on its owning structure node Frobnicator #99's terminal table exactly once.
OBSERVED: find_node(#99) scanned 173 of 173 diagrams and reported '#99 lives at: None'.

## Answer

The premise is wrong: a Frobnicator is not a Nodes[] member over this COM path.

## What was done with it

Row deferred; nothing improvised.
"""


class Stub(object):
    """Replace jev_gate.covers_failure with a constant, or with a raiser."""

    def __init__(self, p=None, raises=False):
        self.p, self.raises, self.calls = p, raises, 0

    def __call__(self, fs, rs, purpose="x"):
        self.calls += 1
        if self.raises:
            raise RuntimeError("stub blows up")
        return self.p, None


def main():
    print("=== selftest_guard_peer_jev: the JEV-DISCHARGE branch of tools/hooks/guard_peer.py ===")
    print("NO LabVIEW. Branch cases make NO API call (covers_failure is stubbed).\n")
    tmp = tempfile.mkdtemp(prefix="jevselftest_")
    bench, peer = os.path.join(tmp, "bench"), os.path.join(tmp, "peer")
    os.makedirs(bench)
    os.makedirs(peer)
    logp = os.path.join(bench, "fake_stage.log")
    revp = os.path.join(peer, "2026-09-22-fake-widget-failpred.md")
    # THE REVIEW IS WRITTEN FIRST, ON PURPOSE. This is the live shape the device exists for: the review that
    # attacks the prediction was archived BEFORE the run that reports it failing (2026-09-22, the real pair was
    # three minutes apart), so guard_peer's own creation-time binding cannot see it and the gate blocks a failure
    # that is already reviewed. Writing the log first would let newest_bound_peer() lift the gate and the
    # JEV-DISCHARGE branch would never be reached.
    with open(revp, "w", encoding="utf-8") as f:
        f.write(FAKE_REVIEW)
    time.sleep(1.1)
    with open(logp, "w", encoding="utf-8") as f:
        f.write(FAKE_LOG)

    ob, op, ojp, ogl, ocf, okey, orr = (guard_peer.BENCH, guard_peer.PEER, jev_gate.PEER, jev_gate.GATE_LOG,
                                        jev_gate.covers_failure, jev.get_key, guard_peer.ROOT)
    # THE LADDER IS SWITCHED OFF FOR THIS FILE (added 2026-09-22 with 2차 #1). guard_peer.main() now asks
    # jev_gate.jev_ladder BEFORE the discharge, and this file stubs a FAKE key ("x"*40) - so the ladder's own
    # classify and its gate-row pass went to the real API and came back 401 twenty times on one run (measured:
    # tools/bench/jev_usage.jsonl, purpose `guard-peer-ladder`, 2026-09-22 20:20:33). The cases below are about
    # the DISCHARGE branch; the ladder has its own file, tools/bench/selftest_guard_peer_ladder.py. Returning
    # (None, None) is exactly "the ladder did not act", which is the state every case here assumes.
    oladder = jev_gate.jev_ladder
    jev_gate.jev_ladder = lambda *a, **k: (None, None)
    # THE SAME-ROW RUNG IS SWITCHED OFF FOR THIS FILE TOO (added 2026-09-22 with "one review per row per
    # cycle"). It sits ABOVE both Jev branches: this fixture's review names `fake_stage` in its `## Question`
    # and is minutes old, so the rung would release every case here before the DISCHARGE branch under test ever
    # ran - and it would be RIGHT to, which is the point. The rung has its own file,
    # tools/bench/selftest_guard_peer_samerow.py. Returning None is exactly "no same-row review exists".
    osr = guard_peer.same_row_review
    guard_peer.same_row_review = lambda *a, **k: None
    # ROOT moves with BENCH/PEER: guard_peer's block message does `os.path.relpath(path, ROOT)`, and on Windows
    # relpath RAISES ValueError across drives ("path is on mount 'C:', start on mount 'G:'"). The fixture lives in
    # the system TEMP (C:) and the project on G:, so leaving ROOT alone made the very branch under test crash
    # before it printed anything. Measured here on the first run, not guessed.
    guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT = bench, peer, tmp
    jev_gate.PEER, jev_gate.GATE_LOG = peer, os.path.join(bench, "jev_gate.log")
    cmd = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/recipes/next_stage.py"

    try:
        # --- C0: the fixture itself is what the gate would block on
        failing = guard_peer.newest_failing_log()
        gate(failing is not None and os.path.basename(failing[0]) == "fake_stage.log",
             "C0 the fake failing log is the one the gate sees",
             "" if failing else "newest_failing_log() found nothing")
        # and with NO jev at all, the gate blocks (the behaviour being preserved)
        jev.get_key = lambda: None
        rc = run_main(cmd)
        gate(rc == 2, "C0b with no key the gate still BLOCKS (old behaviour preserved)", "rc=%s" % rc)

        # --- C1: p above the threshold -> ALLOW, gate log line, citation in the review
        jev.get_key = lambda: "x" * 40
        st = Stub(0.97)
        jev_gate.covers_failure = st
        rc = run_main(cmd)
        gate(rc == 0, "C1 p=0.97 -> the gate ALLOWS", "rc=%s, %d stub call(s)" % (rc, st.calls))
        gl = read(jev_gate.GATE_LOG)
        gate("JEV-DISCHARGE |" in gl and "fake_stage.log" in gl and "p=0.970" in gl,
             "C1b the JEV-DISCHARGE line is appended to jev_gate.log",
             (gl.strip().splitlines() or ["(empty)"])[-1][:110])
        rv = read(revp)
        gate("JEV-DISCHARGE: fake_stage.log" in rv and "p=0.970" in rv,
             "C1c the citation is written into the review under its disposition heading",
             "disposition heading present once: %s" % (rv.count(jev_gate.DISPOSITION_H) == 1))
        gate(not any(ln.startswith(("FIXED:", "REFUTED:", "PRIOR-ART:")) for ln in rv.splitlines()),
             "C1d the citation writes NO release line (cannot free a prior-art verdict)")

        _clear_cache()
        # --- C2: the unknown band -> BLOCK, plus one advisory line
        jev_gate.covers_failure = Stub(0.55)
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2, "C2 p=0.55 -> the gate BLOCKS as before", "rc=%s" % rc)
        gate("JEV-ADVISORY |" in err, "C2b an advisory line is emitted with the block",
             next((ln for ln in err.splitlines() if "JEV-ADVISORY" in ln), "(none)")[:110])
        gate("BLOCKED by tools/hooks/guard_peer.py" in err,
             "C2c the original block message is still printed in full")

        _clear_cache()
        # --- C3: clearly unrelated -> BLOCK, no advisory noise
        jev_gate.covers_failure = Stub(0.02)
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2 and "JEV-ADVISORY" not in err, "C3 p=0.02 -> BLOCK with no advisory line", "rc=%s" % rc)

        _clear_cache()
        # --- C4: the call raises -> the old behaviour, never a wedge
        jev_gate.covers_failure = Stub(raises=True)
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2 and "BLOCKED by tools/hooks/guard_peer.py" in err,
             "C4 an exception inside the discharge degrades to the old block", "rc=%s" % rc)

        # --- C5: the exemptions are untouched
        jev_gate.covers_failure = Stub(0.02)
        remedy = ("py tools/bgrun.py --max-min 14 --log tools/bench/peer_x.log -- powershell -NoProfile "
                  "-File tools/peer.ps1 -Agent claude -Role hypothesis -Slug x -TaskFile t.txt")
        runner = "py tools/bgrun.py --max-min 600 --log tools/bench/runner.log -- py tools/cycle_runner.py"
        gate(run_main(remedy) == 0, "C5 the REMEDY exemption still passes (peer.ps1 dispatch)")
        gate(run_main(runner) == 0, "C5b the cycle_runner exemption still passes")

        # --- C7: THE OTHER HALF OF THE JEV EXEMPTION (user, 2026-09-22 "Jev는 면제"; added 2026-09-22 09:1x after
        # tools/bench/jev_discharge.log - a Jev self-test bundle whose FIXTURE text quotes "STOP:"/"FAIL" by
        # construction - armed this gate against a read-only LabVIEW diagnostic). A log whose LAST run was started
        # on a Jev script is not a failed prediction this project owes a peer review; every other failing log is.
        jevp = os.path.join(bench, "jev_bundle.log")
        with open(jevp, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-22 09:10:00 limit 12.0 min: py -u tools/bench/jev_run_all.py\n"
                    "  FAIL  SELF-TEST fixture line quoted by construction\n"
                    "STOP: fixture text\nBGRUN END rc=1 after 39s\n")
        time.sleep(1.1)
        os.utime(jevp, None)
        failing2 = guard_peer.newest_failing_log()
        gate(failing2 is not None and os.path.basename(failing2[0]) == "fake_stage.log",
             "C7 a NEWER Jev-script log does not become the failing log the gate blocks on",
             "newest_failing_log() -> %r" % (os.path.basename(failing2[0]) if failing2 else None))
        # Fixture RENAMED 2026-09-26 (card 101-2) from `jev_mentioning_build.log`: tools/bench/jev_* basenames are
        # now excluded BY PATH (the jev ledgers, C10 below). The case's intent is unchanged - the CONTENT mentions a
        # Jev script, the command is a recipe, so it gates.
        nonjev = os.path.join(bench, "build_mentioning_jev.log")
        with open(nonjev, "w", encoding="utf-8") as f:
            f.write("BGRUN START 2026-09-22 09:11:00 limit 12.0 min: py -u tools/recipes/build_x.py\n"
                    "  FAIL  a real build failure that merely mentions tools/bench/jev_run_all.py\n"
                    "BGRUN END rc=1 after 5s\n")
        time.sleep(1.1)
        os.utime(nonjev, None)
        failing3 = guard_peer.newest_failing_log()
        gate(failing3 is not None and os.path.basename(failing3[0]) == "build_mentioning_jev.log",
             "C7b a NON-Jev build that merely MENTIONS a Jev script still gates (scoped by the command, not the "
             "filename)", "newest_failing_log() -> %r" % (os.path.basename(failing3[0]) if failing3 else None))
        os.remove(jevp)
        os.remove(nonjev)

        # --- C8: THE SELF-TEST EXEMPTION IS SCOPED BY THE COMMAND (card 77-1, 2026-09-25; retrospective-cycle76
        # device-failed: selftest_make_default.log - a LabVIEW-touching self-test - failed its prediction and the
        # filename exemption hid it, so no JEV-LADDER line was written, jev_gate.log:887). Fixture scripts live
        # under the temp ROOT; the LabVIEW one reaches `stagekit` only TRANSITIVELY, through a helper module.
        fbench = os.path.join(tmp, "tools", "bench")
        os.makedirs(fbench)
        for name, body in (("fixture_lvlib.py", "import os\nimport stagekit as K   # noqa: E402\n"),
                           ("selftest_lvfix.py", "import os, sys\nimport fixture_lvlib as L   # noqa: E402\n"),
                           ("selftest_purefix.py", "import json\nimport os, sys  # noqa\nimport logclass\n")):
            with open(os.path.join(fbench, name), "w", encoding="utf-8") as f:
                f.write(body)

        def flog(name, script, marker=True, start=True):
            p = os.path.join(bench, name)
            with open(p, "w", encoding="utf-8") as f:
                if start:
                    f.write("BGRUN START 2026-09-22 09:20:00 limit 12.0 min: py -u %s\n" % script)
                f.write("  PASS  x\nSTOP: fixture failed prediction\nBGRUN END rc=1 after 9s\n" if marker else
                        "  PASS  x\nBGRUN END rc=0 after 9s\n")
            time.sleep(1.1)
            os.utime(p, None)
            return p

        def newest():
            nf = guard_peer.newest_failing_log()
            return os.path.basename(nf[0]) if nf else None

        made = [flog("selftest_lvfix.log", "tools/bench/selftest_lvfix.py")]
        got = newest()
        gate(got == "selftest_lvfix.log", "C8 a selftest_*.log whose command reaches LabVIEW (transitively, via an "
             "imported helper) GATES", "newest_failing_log() -> %r" % got)
        made.append(flog("selftest_purefix.log", "tools/bench/selftest_purefix.py"))
        got = newest()
        gate(got == "selftest_lvfix.log", "C8b a NEWER pure-Python selftest log does NOT become the failing log",
             "newest_failing_log() -> %r" % got)
        made.append(flog("oddly_named.log", "tools/bench/selftest_purefix.py"))
        got = newest()
        gate(got == "selftest_lvfix.log", "C8c scoped by COMMAND: a non-selftest-NAMED log running a pure-Python "
             "self-test is excluded too", "newest_failing_log() -> %r" % got)
        made.append(flog("selftest_named_recipe.log", "tools/recipes/build_y.py"))
        got = newest()
        gate(got == "selftest_named_recipe.log", "C8d scoped by COMMAND: a selftest-NAMED log whose command runs a "
             "recipe GATES", "newest_failing_log() -> %r" % got)
        made.append(flog("selftest_missing.log", "tools/bench/selftest_not_on_disk.py"))
        got = newest()
        gate(got == "selftest_missing.log", "C8e fails CLOSED: a selftest script that cannot be read GATES",
             "newest_failing_log() -> %r" % got)
        made.append(flog("selftest_nostart.log", "", start=False))
        got = newest()
        gate(got == "selftest_missing.log", "C8f no BGRUN START at all -> the old filename rule still excludes it",
             "newest_failing_log() -> %r" % got)
        for p in made:
            os.remove(p)

        # --- C10: THE JEV LEDGERS ARE EXCLUDED BY PATH (card 101-2, PD213(g)1, 2026-09-26). The live defect:
        # tools/bench/jev_gate.log - no BGRUN START, a JEV-GATEROW line quoting a gated log's STOP row - became the
        # newest failing log and re-armed the gate on the lines its own refusals append (result_101-1.json).
        ledger = os.path.join(bench, "jev_gate.log")
        with open(ledger, "a", encoding="utf-8") as f:
            f.write("2026-09-26 22:45:44 JEV-GATEROW | stage_d1_disp.log | E1 defect p=0.9 | STOP: E1 fixture row\n"
                    "2026-09-26 23:12:44 JEV-LADDER | new-problem p=0.40 | stage_d1_disp.log | NEXT-ACTION: "
                    "hypothesis review owed (old path)\n")
        time.sleep(1.1)
        os.utime(ledger, None)
        gate(guard_peer.log_failure(read(ledger))[0],
             "C10 fixture check: the ledger text IS failure-shaped (so only the path rule can exclude it)")
        got = newest()
        gate(got == "fake_stage.log", "C10b NEGATIVE: a newer tools/bench/jev_gate.log with a JEV-GATEROW STOP line "
             "does NOT become the failing log", "newest_failing_log() -> %r" % got)
        real_build = flog("stage_real_build.log", "tools/recipes/stage_real.py")
        got = newest()
        gate(got == "stage_real_build.log", "C10c POSITIVE: a newer real build log with a STOP line still GATES",
             "newest_failing_log() -> %r" % got)
        gate(guard_peer.is_jev_ledger(os.path.join(bench, "jev_usage.jsonl"))
             and not guard_peer.is_jev_ledger(os.path.join(tmp, "elsewhere", "jev_gate.log"))
             and not guard_peer.is_jev_ledger(os.path.join(bench, "stage_jev_gate.log")),
             "C10d keyed on PATH: bench/jev_*.jsonl yes; jev_gate.log outside BENCH no; non-jev_ prefix no")
        os.remove(real_build)
        os.remove(ledger)

        # --- C6: OPTIONAL live call, only if the key is really there
        jev.get_key, jev_gate.covers_failure = okey, ocf
        if jev.get_key():
            p, err2 = jev_gate.covers_failure(jev.summarise_failure(logp), jev_gate.summarise_review(revp))
            gate(p is not None and 0.0 <= p <= 1.0,
                 "C6 LIVE: the real transport answers this fixture pair", "p=%s err=%s" % (p, err2))
            gate(p is None or p >= 0.5,
                 "C6b LIVE: the review that attacks this very prediction reads as covering it", "p=%s" % p)
        else:
            print("  SKIP  C6 live call - TYPESAFE_API_KEY not visible to this process")
    finally:
        (guard_peer.BENCH, guard_peer.PEER, jev_gate.PEER, jev_gate.GATE_LOG,
         jev_gate.covers_failure, jev.get_key, guard_peer.ROOT) = ob, op, ojp, ogl, ocf, okey, orr
        jev_gate.jev_ladder = oladder
        guard_peer.same_row_review = osr
        shutil.rmtree(tmp, ignore_errors=True)

    # --- C9: the REAL project files, read-only (ROOT restored above). The measured instance of the defect.
    real = "BGRUN START 2026-09-25 05:18:01 limit 12.0 min: py -u tools/bench/selftest_make_default.py"
    gate(not guard_peer.selftest_exempt(real), "C9 the real selftest_make_default.py command is NOT exempt "
         "(it reaches LabVIEW via diag_replay_lib -> stagekit)")
    own = "BGRUN START 2026-09-25 06:00:00 limit 5.0 min: py -u tools/bench/selftest_guard_peer_jev.py"
    gate(guard_peer.selftest_exempt(own), "C9b this file's own command IS exempt (pure Python, no LabVIEW)")

    print("\n=== selftest_guard_peer_jev: %d pass / %d fail ===" % (NPASS, NFAIL))
    import protocol   # C6 RESULT line (session protocol v1); tools/ is on sys.path
    print(protocol.result_line(protocol.make_result(NPASS, NFAIL, FIRST_FAIL)))
    return 0 if NFAIL == 0 else 1


def read(p):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""



def _clear_cache():
    """The discharge cache (jev_gate, 2026-09-22) makes a granted discharge FINAL for a log; the cases below reuse one
    fake log name, so each block case starts from an empty cache."""
    try:
        os.remove(os.path.join(os.path.dirname(jev_gate.GATE_LOG), "jev_discharge_cache.json"))
    except OSError:
        pass


def run_main(cmd, capture=False):
    """Drive guard_peer.main() with a PreToolUse payload; optionally capture its stderr."""
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}})
    old_in, old_err = sys.stdin, sys.stderr
    sys.stdin = io.StringIO(payload)
    buf = io.StringIO()
    if capture:
        sys.stderr = buf
    try:
        rc = guard_peer.main()
    finally:
        sys.stdin, sys.stderr = old_in, old_err
    return (rc, buf.getvalue()) if capture else rc


if __name__ == "__main__":
    sys.exit(main())
