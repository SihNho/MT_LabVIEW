r"""selftest_guard_cycle_offline.py - card 112-1 T6 (PD225(h)3 (vi); docs/violation-decisions.md device-failed 2026-09-27 22:20).

WHAT EXISTED: selftest_guard_cycle_fixed.py / _rerun.py (premature_build on fabricated files); stop_record.offline_checker
(card 107-1) already exempted `stage_prerun --dry|--prerun` in the LAUNCH gate only.

FIXTURE (card chat-P3 1.2, 2026-09-28; review archive/peer/2026-09-28-p2-offline-fixture.md): the first version read the
LIVE archive state of 2026-09-27 22:2x (c111e unreleased for stage_d1_l2b2a) and went stale 1 h 12 min later when a
later record (c112d) released those bytes, after which O3/O4 passed twice for an unrelated reason and then failed.
This version BUILDS ITS OWN state, like selftest_stoprecord_supersession.py: a scratch recipe under tools/recipes/
(created and deleted by this run), a scratch prior-art review with an UNRELEASED non-novel verdict in a temp dir, and
`stop_record.STORE` / `.MARKER` pointed at a temp store. The REAL `guard_cycle.main()` is driven IN-PROCESS (stdin =
the PreToolUse JSON; SystemExit code read), because a subprocess could not see the patched store.

PREDICTION CONTRACT
  O0 fixture: exactly one record in the temp store, verdict ['already-failed'], released None
  O1 `py tools/bgrun.py --material ... -- py -u tools/stage_prerun.py --dry <scratch recipe>` -> ALLOWED (exit 0)
  O2 the same with --prerun, not bgrun-wrapped -> ALLOWED
  O3 `py -u <scratch recipe>` (a LAUNCH) -> REFUSED (exit 2) by the stop-record launch gate while the verdict is unreleased
  O4 a dry chained with a launch (`... --dry X && py -u X`) -> REFUSED (one launch segment keeps every gate on)
  O5 offline_only() unit: True for O1/O2, False for O3/O4 and for a command naming no recipe
  O6 discriminator: after a REFUTED: line is appended to the scratch review, stop_record.check_command(LAUNCH) ALLOWS
     (so O3's refusal is caused by the unreleased verdict, not by something else)
  O7 cleanup: scratch recipe deleted; the live store's bytes unchanged
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_guard_cycle_offline.log -- py -u tools/bench/selftest_guard_cycle_offline.py
"""
import hashlib
import io
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_cycle as G   # noqa: E402
import protocol           # noqa: E402
import stop_record        # noqa: E402  (the same module object guard_cycle uses)

gates = []
REVIEW = ("# prior-art review - SCRATCH (selftest_guard_cycle_offline)\n\n- **agent:** claude\n- **date:** {d}\n"
          "- **outcome:** ANSWERED\n\n## Question\n\n(scratch)\n\n## Answer\n\nPRIOR-ART: already-failed\n\n"
          "## What was done with it\n\n(Claude fills in)\n")
RELEASE = ("\nREFUTED: already-failed - tools/bench/selftest_guard_cycle_offline.py:1 says this is a scratch fixture, "
           "which does not cover a real build because no real build is involved.\n")


def gate(name, ok, detail=""):
    gates.append((name, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(detail)[:300]), flush=True)


def md5(p):
    try:
        with open(p, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except OSError:
        return "absent"


def hook(cmd):
    """Drive the real guard_cycle.main() in-process; returns (exit code, first stderr line)."""
    old_in, old_err = sys.stdin, sys.stderr
    sys.stdin = io.StringIO(json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}}))
    sys.stderr = err = io.StringIO()
    os.environ.pop("CYCLE_GUARD_OFF", None)
    try:
        G.main()
        rc = 0
    except SystemExit as e:
        rc = e.code if isinstance(e.code, int) else 1
    finally:
        sys.stdin, sys.stderr = old_in, old_err
    return rc, err.getvalue().strip().splitlines()[:1]


live_store, live_marker = stop_record.STORE, stop_record.MARKER
live_md5 = md5(live_store)
tmp = tempfile.mkdtemp(prefix="gcoffline_")
stem = "scratch_gcoffline_%d_%d" % (os.getpid(), int(time.time()))
R = "tools/recipes/%s.py" % stem
R_ABS = os.path.join(ROOT, "tools", "recipes", stem + ".py")
DRY = "py tools/bgrun.py --material --max-min 5 --log tools/bench/%s_dry.log -- py -u tools/stage_prerun.py --dry %s" % (stem, R)
PRE = "py -u tools/stage_prerun.py --prerun " + R
LAUNCH = "py -u " + R
CHAIN = "py -u tools/stage_prerun.py --dry {0} && py -u {0}".format(R)
try:
    stop_record.STORE = os.path.join(tmp, "stop_records.json")
    stop_record.MARKER = os.path.join(tmp, "stop_records.marker")
    with open(R_ABS, "w", encoding="utf-8") as f:
        f.write("# scratch recipe for selftest_guard_cycle_offline. Never run; deleted by the same run.\nprint('x')\n")
    rev = os.path.join(tmp, "priorart-scratch.md")
    with open(rev, "w", encoding="utf-8") as f:
        f.write(REVIEW.format(d=time.strftime("%Y-%m-%d")))
    stop_record.write_stop_record(R, rev, ["already-failed"])
    recs = stop_record.load_records()
    gate("O0 fixture: one unreleased already-failed record in the temp store",
         len(recs) == 1 and recs[0].get("verdict") == ["already-failed"] and recs[0].get("released") is None,
         [(r.get("recipe_path"), r.get("verdict"), r.get("released")) for r in recs])
    rc, why = hook(DRY)
    gate("O1 bgrun-wrapped stage_prerun --dry of the unreleased recipe is ALLOWED", rc == 0, (rc, why))
    rc, why = hook(PRE)
    gate("O2 plain stage_prerun --prerun of the unreleased recipe is ALLOWED", rc == 0, (rc, why))
    rc, why = hook(LAUNCH)
    gate("O3 the recipe's LAUNCH is REFUSED while its prior-art verdict is unreleased",
         rc == 2 and bool(why) and "stop_record" in why[0], (rc, why))
    rc, why = hook(CHAIN)
    gate("O4 a dry chained with a launch is REFUSED", rc == 2 and bool(why) and "stop_record" in why[0], (rc, why))
    u = [G.offline_only(c) for c in (DRY, PRE, LAUNCH, CHAIN, "py -u tools/bench/diag_c112a_peek.py x")]
    gate("O5 offline_only: [True, True, False, False, False]", u == [True, True, False, False, False], u)
    with open(rev, "a", encoding="utf-8") as f:
        f.write(RELEASE)
    allow, msg = stop_record.check_command(LAUNCH)
    gate("O6 discriminator: with a REFUTED: line the same LAUNCH passes the stop-record gate", allow,
         (msg or "").strip().splitlines()[:1])
finally:
    stop_record.STORE, stop_record.MARKER = live_store, live_marker
    try:
        os.remove(R_ABS)
    except OSError:
        pass
gate("O7 cleanup: scratch recipe gone, live store bytes unchanged",
     not os.path.exists(R_ABS) and md5(live_store) == live_md5, (os.path.exists(R_ABS), live_md5[:8], md5(live_store)[:8]))
n_pass = sum(1 for _n, ok in gates if ok)
n_fail = len(gates) - n_pass
first = next((n for n, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, n_fail))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
