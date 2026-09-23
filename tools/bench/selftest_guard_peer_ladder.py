r"""selftest_guard_peer_ladder.py - does the REVIEW LADDER branch of tools/hooks/guard_peer.py do what it claims?

NO LabVIEW and NO API CALL: `jev_gate.ladder_classify`, `jev_gate.covers_failure` and
`jev_gaterow.verdicts_for` are stubbed, so every branch is exercised deterministically and for free.

The sibling file tools/bench/selftest_guard_peer_jev.py covers the DISCHARGE branch and must keep passing
17/0 after this change; this file covers only what the ladder adds on top of it:

  L0  the fixture is the log the gate would block on                       (the precondition of every case)
  L1  our-script-bug p=0.95        -> ALLOW, one JEV-LADDER line, one jev_ladder_allowed.jsonl line
  L2  already-reviewed-class 0.92, a covering review   -> ALLOW (through the ORDINARY discharge)
  L3  already-reviewed-class 0.92, no covering review  -> BLOCK, and the discharge runs ONCE, not twice
  L4  new-problem p=0.95           -> BLOCK, and the ordinary discharge is still consulted (old path intact)
  L5  the unknown band p=0.55      -> the ladder does not act; the old path's discharge ALLOWS as it always did
  L6  no key                       -> the ladder is inert and the gate blocks exactly as before
  L7  ladder_classify raises       -> the old path, unchanged, with the full block message
  L8  our-script-bug p=0.79        -> below LADDER_P: no allow, the old path decides

THE FIXTURE'S FAILURE MARKER IS `STOP:`, NOT `FAIL` - the same deliberate choice recorded in
selftest_guard_peer_jev.py: guard_peer echoes the first failure line into its block message, and bgrun's
inner-failure scanner would then read this test's own stdout as real failures and force rc=1 on a clean run.
NOTHING under tools/bench/ or archive/peer/ is written: the fixture lives in a temp directory and every module
constant is restored in `finally`.
"""
import io
import json
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
import jev_gaterow    # noqa: E402
import guard_peer     # noqa: E402

NPASS = NFAIL = 0

FAKE_LOG = """BGRUN START 2026-09-22 18:00:00 limit 10 min: py -u tools/recipes/fake_ladder_stage.py
  PASS  A1 the bed md5 is unchanged
STOP: A2 THE ROW LANDED - wire #9999 appears exactly once on WhileLoop #637's terminal table
      FAILED PREDICTION - WhileLoop #637's wired terminal count went 48 -> 47
BGRUN END rc=1 after 44s
"""

FAKE_REVIEW = """# fake-ladder-review

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max)
- **kind:** review
- **outcome:** ANSWERED (400s)

## Question

# FAILED PREDICTION - fake ladder stage, log tools/bench/fake_ladder_stage.log

PREDICTED: WhileLoop #637's wired terminal count is unchanged by the row.
OBSERVED: 48 -> 47.

## Answer

The prediction is the thing that is wrong: deleting the old shift-register wire removes one wired terminal.
"""


def gate(ok, label, detail=""):
    global NPASS, NFAIL
    if ok:
        NPASS += 1
        print("  PASS  %s  %s" % (label, detail))
    else:
        NFAIL += 1
        print("  FAIL  %s  %s" % (label, detail))


class LadderStub(object):
    """Replace jev_gate.ladder_classify with a constant verdict, or with a raiser."""

    def __init__(self, cls=None, p=None, raises=False):
        self.cls, self.p, self.raises, self.calls = cls, p, raises, 0

    def __call__(self, fs, rows="", recent="", purpose="x", n=None):
        self.calls += 1
        if self.raises:
            raise RuntimeError("stub blows up")
        return self.cls, self.p, 0.0


class CoversStub(object):
    """Replace jev_gate.covers_failure with a constant probability."""

    def __init__(self, p=None):
        self.p, self.calls = p, 0

    def __call__(self, fs, rs, purpose="x", n=None):
        self.calls += 1
        return self.p, None


def read(p):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def _clear_cache():
    # Both caches live beside GATE_LOG (the temp bench here). Every case reuses ONE fake log, so the ladder's
    # once-per-(log, md5) cache (2026-09-24) must be cleared too, or case L2 would read L1's verdict.
    for name in ("jev_discharge_cache.json", "jev_ladder_cache.jsonl"):
        try:
            os.remove(os.path.join(os.path.dirname(jev_gate.GATE_LOG), name))
        except OSError:
            pass


def run_main(cmd, capture=False):
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


def main():
    print("=== selftest_guard_peer_ladder: the REVIEW LADDER branch of tools/hooks/guard_peer.py ===")
    print("NO LabVIEW, NO API call (ladder_classify / covers_failure / verdicts_for are stubbed).\n")
    tmp = tempfile.mkdtemp(prefix="jevladder_")
    bench, peer = os.path.join(tmp, "bench"), os.path.join(tmp, "peer")
    os.makedirs(bench)
    os.makedirs(peer)
    logp = os.path.join(bench, "fake_ladder_stage.log")
    revp = os.path.join(peer, "2026-09-22-fake-ladder-review.md")
    with open(revp, "w", encoding="utf-8") as f:
        f.write(FAKE_REVIEW)
    time.sleep(1.1)
    with open(logp, "w", encoding="utf-8") as f:
        f.write(FAKE_LOG)

    saved = (guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT, jev_gate.PEER, jev_gate.GATE_LOG,
             jev_gate.LADDER_ALLOWED, jev_gate.ladder_classify, jev_gate.covers_failure,
             jev_gaterow.verdicts_for, jev.get_key, guard_peer.same_row_review)
    # THE SAME-ROW RUNG IS SWITCHED OFF FOR THIS FILE (added 2026-09-22 with "one review per row per cycle").
    # It runs BEFORE the ladder and costs no model call, and this fixture's review names `fake_ladder_stage` in
    # its `## Question` minutes before the log - so the rung would release every case here and the LADDER branch
    # under test would never be reached. Its own file is tools/bench/selftest_guard_peer_samerow.py.
    guard_peer.same_row_review = lambda *a, **k: None
    guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT = bench, peer, tmp
    jev_gate.PEER, jev_gate.GATE_LOG = peer, os.path.join(bench, "jev_gate.log")
    jev_gate.LADDER_ALLOWED = os.path.join(bench, "jev_ladder_allowed.jsonl")
    jev_gaterow.verdicts_for = lambda *a, **k: "D7: prediction-error (p=0.91) | FAIL D7 ..."
    jev.get_key = lambda: "x" * 40
    cmd = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/recipes/next.py"

    try:
        failing = guard_peer.newest_failing_log()
        gate(failing is not None and os.path.basename(failing[0]) == "fake_ladder_stage.log",
             "L0 the fake failing log is the one the gate sees",
             "" if failing else "newest_failing_log() found nothing")

        # --- L1 our-script-bug -> ALLOW, logged, recorded in the jsonl
        _clear_cache()
        ls, cs = LadderStub("our-script-bug", 0.95), CoversStub(0.02)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc = run_main(cmd)
        gate(rc == 0, "L1 our-script-bug p=0.95 -> the gate ALLOWS", "returned %s" % rc)
        gl = read(jev_gate.GATE_LOG)
        gate("JEV-LADDER |" in gl and "our-script-bug" in gl and "ALLOW" in gl,
             "L1b a JEV-LADDER line records the release",
             (gl.strip().splitlines() or ["(empty)"])[-1][:120])
        jl = [json.loads(x) for x in read(jev_gate.LADDER_ALLOWED).splitlines() if x.strip()]
        gate(len(jl) == 1 and jl[0]["class"] == "our-script-bug" and jl[0]["log"] == "fake_ladder_stage.log",
             "L1c exactly one jev_ladder_allowed.jsonl line, naming the log and the class", str(jl)[:120])
        gate(cs.calls == 0, "L1d the ordinary discharge was NOT consulted (the ladder released it first)",
             "covers_failure calls=%d" % cs.calls)

        # --- L2 already-reviewed-class with a covering review -> ALLOW through the discharge
        _clear_cache()
        ls, cs = LadderStub("already-reviewed-class", 0.92), CoversStub(0.97)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc = run_main(cmd)
        gate(rc == 0, "L2 already-reviewed-class + a covering review -> ALLOW", "returned %s" % rc)
        gate(cs.calls >= 1, "L2b the ordinary discharge decided it (it was consulted)",
             "covers_failure calls=%d" % cs.calls)
        gate("JEV-DISCHARGE: fake_ladder_stage.log" in read(revp),
             "L2c the citation still lands in the review's own disposition section")
        n_jl = len([x for x in read(jev_gate.LADDER_ALLOWED).splitlines() if x.strip()])
        gate(n_jl == 1, "L2d a discharge-backed allow does NOT add a jsonl line (the citation is its record)",
             "jsonl lines=%d" % n_jl)

        # --- L3 already-reviewed-class with NO covering review -> BLOCK, discharge consulted once
        _clear_cache()
        ls, cs = LadderStub("already-reviewed-class", 0.92), CoversStub(0.05)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2, "L3 already-reviewed-class with no citable review -> BLOCK", "returned %s" % rc)
        gate(cs.calls == 1, "L3b the discharge ran exactly ONCE (not re-run by the old path)",
             "covers_failure calls=%d" % cs.calls)
        gate("BLOCKED by tools/hooks/guard_peer.py" in err, "L3c the original block message is printed in full")

        # --- L4 new-problem -> BLOCK, and the old path still runs its own discharge
        _clear_cache()
        ls, cs = LadderStub("new-problem", 0.95), CoversStub(0.02)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2 and "BLOCKED by tools/hooks/guard_peer.py" in err,
             "L4 new-problem p=0.95 -> BLOCK exactly as before", "returned %s" % rc)
        gate(cs.calls == 1, "L4b the old path's discharge was still consulted (nothing was short-circuited)",
             "covers_failure calls=%d" % cs.calls)

        # --- L5 the unknown band -> the ladder does not act; the old path decides, and here it ALLOWS
        _clear_cache()
        ls, cs = LadderStub("our-script-bug", 0.55), CoversStub(0.97)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc = run_main(cmd)
        gate(rc == 0 and cs.calls >= 1,
             "L5 p=0.55 -> the ladder abstains and the OLD discharge decides (here: allow)",
             "returned %s covers_failure calls=%d" % (rc, cs.calls))

        # --- L6 no key -> inert
        _clear_cache()
        jev.get_key = lambda: None
        ls, cs = LadderStub("our-script-bug", 0.99), CoversStub(0.99)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2 and ls.calls == 0 and cs.calls == 0,
             "L6 with no key the ladder never asks and the gate BLOCKS (old behaviour preserved)",
             "returned %s ladder=%d covers=%d" % (rc, ls.calls, cs.calls))
        jev.get_key = lambda: "x" * 40

        # --- L7 the ladder raises -> the old path, unchanged
        _clear_cache()
        ls, cs = LadderStub(raises=True), CoversStub(0.02)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2 and "BLOCKED by tools/hooks/guard_peer.py" in err,
             "L7 an exception inside the ladder degrades to the old block", "returned %s" % rc)
        gate(cs.calls == 1, "L7b and the old path's discharge still ran", "covers_failure calls=%d" % cs.calls)

        # --- L8 just below the threshold
        _clear_cache()
        ls, cs = LadderStub("our-script-bug", jev_gate.LADDER_P - 0.01), CoversStub(0.02)
        jev_gate.ladder_classify, jev_gate.covers_failure = ls, cs
        rc, err = run_main(cmd, capture=True)
        gate(rc == 2, "L8 our-script-bug at just below LADDER_P -> no allow", "returned %s" % rc)
        gate("below %.2f: old path" % jev_gate.LADDER_P in read(jev_gate.GATE_LOG),
             "L8b and the abstention is still recorded in jev_gate.log")

        # --- L9 the exemptions are untouched
        gate(run_main("py tools/bgrun.py --max-min 14 --log tools/bench/peer_x.log -- powershell -NoProfile "
                      "-File tools/peer.ps1 -Agent claude -Role hypothesis -Slug x -TaskFile t.txt") == 0,
             "L9 the REMEDY exemption still passes (peer.ps1 dispatch)")
    finally:
        (guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT, jev_gate.PEER, jev_gate.GATE_LOG,
         jev_gate.LADDER_ALLOWED, jev_gate.ladder_classify, jev_gate.covers_failure,
         jev_gaterow.verdicts_for, jev.get_key, guard_peer.same_row_review) = saved
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n=== selftest_guard_peer_ladder: %d pass / %d fail ===" % (NPASS, NFAIL))
    return 0 if NFAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
