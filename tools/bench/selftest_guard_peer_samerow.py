r"""selftest_guard_peer_samerow.py - does the ONE REVIEW PER ROW PER CYCLE rung of tools/hooks/guard_peer.py
do what it claims, and only that?

NO LabVIEW, NO API CALL, NOTHING WRITTEN UNDER tools/bench/ OR archive/peer/: every fixture lives in a temp
directory, `jev.get_key` is forced to None so neither Jev insertion can act, and every module constant is
restored in `finally`. The rung itself is mechanical (a filename and a timestamp), so nothing needs stubbing
to make it deterministic.

  S0  the fixture is the log the gate would otherwise block on            (the precondition of every case)
  S1  same script, review 10 min old        -> ALLOW
  S2  same script, review 7 h old           -> BLOCK (outside the 6 h window)
  S3  a DIFFERENT script's review           -> BLOCK
  S4  `_v3` log vs a review naming `_v7`    -> ALLOW (the version suffix is not part of the row)
  S5  same script, outcome TIMEOUT          -> BLOCK (review_quality still decides who may be cited)
  S6  the citation lands ONCE               -> two blocked runs of the same log add one `SAME-ROW:` line
  S7  the release is recorded in jev_gate.log as RULE-SAME-ROW, naming the log and the script
  S8  a review that names the script only in its ANSWER (not the question/headers) -> BLOCK
  S9  log_script() strips `_v\d+` and takes the script after the `--`, not bgrun.py

THE FIXTURE'S FAILURE MARKER IS `STOP:`, NOT `FAIL` - the same deliberate choice recorded in
selftest_guard_peer_jev.py and ...ladder.py: guard_peer echoes the first failure line into its block message,
and bgrun's inner-failure scanner would then read this test's own stdout as real failures and force rc=1 on a
clean run.

    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_guard_peer_samerow.log \
        -- py -u tools/bench/selftest_guard_peer_samerow.py
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
except Exception:      # noqa: BLE001
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
for _p in (TOOLS, HERE, os.path.join(TOOLS, "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import jev            # noqa: E402
import importlib      # noqa: E402
guard_peer = importlib.import_module(os.environ.get("GUARD_PEER_UNDER_TEST", "guard_peer"))  # override: a candidate copy

NPASS = NFAIL = 0

LOG_TMPL = """BGRUN START 2026-09-22 18:00:00 limit 10 min: py tools/bgrun.py --material --max-min 10 \
--log tools/bench/%(log)s -- py -u tools/recipes/%(script)s.py
  PASS  A1 the bed md5 is unchanged
STOP: A2 THE ROW LANDED - wire #9999 appears exactly once on the terminal table
BGRUN END rc=1 after 44s
"""

REVIEW_TMPL = """# %(slug)s

- **agent:** %(agent)s
- **role:** %(role)s
- **model:** opus (effort max)
- **kind:** review
- **slug:** %(slug)s
- **task:** ATTACK the claim below
- **outcome:** %(outcome)s (400s)

## Question

# FAILED PREDICTION - %(names)s

PREDICTED: the row lands and the terminal count is unchanged.
OBSERVED: it did not.

## Answer

%(answer)s
"""


def gate(ok, label, detail=""):
    global NPASS, NFAIL
    if ok:
        NPASS += 1
        print("  PASS  %s  %s" % (label, detail))
    else:
        NFAIL += 1
        print("  FAIL  %s  %s" % (label, detail))
    sys.stdout.flush()


def read(p):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def write_log(bench, script, log="stage_row.log"):
    p = os.path.join(bench, log)
    with open(p, "w", encoding="utf-8") as f:
        f.write(LOG_TMPL % {"script": script, "log": log})
    return p


def write_review(peer, name, names, agent="claude", role="hypothesis", outcome="ANSWERED",
                 age_s=600, answer="The prediction is what is wrong.", slug=None):
    """A review archive whose CREATION time is `age_s` seconds ago (both stamps moved: guard_peer reads
    min(ctime, mtime) on Windows, and os.utime cannot move ctime, so the fixture leans on mtime being the
    smaller of the two)."""
    p = os.path.join(peer, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(REVIEW_TMPL % {"slug": slug or name[:-3], "agent": agent, "role": role,
                               "outcome": outcome, "names": names, "answer": answer})
    t = time.time() - age_s
    os.utime(p, (t, t))
    return p


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


CMD = "py tools/bgrun.py --material --max-min 5 --log tools/bench/y.log -- py -u tools/recipes/next.py"


def case(tmp, label, script, review_kw, expect_rc, detail_extra=""):
    """One case: a fresh bench+peer pair, one failing log, one review, one run of guard_peer.main()."""
    bench, peer = os.path.join(tmp, label, "bench"), os.path.join(tmp, label, "peer")
    os.makedirs(bench)
    os.makedirs(peer)
    logp = write_log(bench, script)
    revp = write_review(peer, "2026-09-22-%s.md" % label, **review_kw)
    guard_peer.BENCH, guard_peer.PEER = bench, peer
    rc, err = run_main(CMD, capture=True)
    return rc, err, logp, revp, bench, peer


def main():
    print("=== selftest_guard_peer_samerow: ONE REVIEW PER ROW PER CYCLE (tools/hooks/guard_peer.py) ===")
    print("NO LabVIEW, NO API call (jev.get_key forced to None, so neither Jev insertion can act).\n")
    tmp = tempfile.mkdtemp(prefix="jevsamerow_")
    saved = (guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT, jev.get_key)
    guard_peer.ROOT = tmp
    jev.get_key = lambda: None
    try:
        # --- S0 the precondition: with NO review at all, this fixture blocks.
        bench0, peer0 = os.path.join(tmp, "s0", "bench"), os.path.join(tmp, "s0", "peer")
        os.makedirs(bench0)
        os.makedirs(peer0)
        write_log(bench0, "stage_d1_m3a3_rowD")
        guard_peer.BENCH, guard_peer.PEER = bench0, peer0
        failing = guard_peer.newest_failing_log()
        rc, err = run_main(CMD, capture=True)
        gate(failing is not None and rc == 2 and "BLOCKED by tools/hooks/guard_peer.py" in err,
             "S0 with no review the fixture is a log the gate BLOCKS on", "rc=%s" % rc)

        # --- S1 same script, 10 minutes old -> ALLOW
        rc, err, logp, revp, bench, peer = case(
            tmp, "s1", "stage_d1_m3a3_rowD",
            {"names": "tools/recipes/stage_d1_m3a3_rowD.py, log tools/bench/stage_row.log", "age_s": 600},
            0)
        gate(rc == 0, "S1 same script, review 10 min old -> ALLOW", "returned %s" % rc)
        gate("RULE-SAME-ROW" in err, "S1b the release says RULE-SAME-ROW on stderr",
             (err.strip().splitlines() or ["(none)"])[0][:110])

        # --- S2 same script but SEVEN HOURS old -> BLOCK
        rc, err, _l, _r, _b, _p = case(
            tmp, "s2", "stage_d1_m3a3_rowD",
            {"names": "tools/recipes/stage_d1_m3a3_rowD.py", "age_s": 7 * 3600}, 2)
        gate(rc == 2 and "RULE-SAME-ROW" not in err,
             "S2 the same review 7 h old is outside the window -> BLOCK", "returned %s" % rc)

        # --- S3 a review of a DIFFERENT script -> BLOCK
        rc, err, _l, _r, _b, _p = case(
            tmp, "s3", "stage_d1_m3a3_rowD",
            {"names": "tools/recipes/build_d1_m3a2_initvals.py", "age_s": 600}, 2)
        gate(rc == 2 and "RULE-SAME-ROW" not in err,
             "S3 a review naming a different script does not release this row", "returned %s" % rc)

        # --- S4 `_v3` log vs a review that names `_v7`
        rc, err, _l, _r, _b, _p = case(
            tmp, "s4", "stage_d1_m3a3_rowD_v3",
            {"names": "tools/recipes/stage_d1_m3a3_rowD_v7.py", "age_s": 600}, 0)
        gate(rc == 0 and "RULE-SAME-ROW" in err,
             "S4 _v3 vs _v7 is the SAME row -> ALLOW", "returned %s" % rc)

        # --- S5 the review TIMED OUT -> not citable
        rc, err, _l, _r, _b, _p = case(
            tmp, "s5", "stage_d1_m3a3_rowD",
            {"names": "tools/recipes/stage_d1_m3a3_rowD.py", "age_s": 600, "outcome": "TIMEOUT"}, 2)
        gate(rc == 2 and "RULE-SAME-ROW" not in err,
             "S5 a TIMEOUT exchange is not a citable review -> BLOCK", "returned %s" % rc)

        # --- S6/S7 the citation lands ONCE, and the gate log records the release
        bench, peer = os.path.join(tmp, "s6", "bench"), os.path.join(tmp, "s6", "peer")
        os.makedirs(bench)
        os.makedirs(peer)
        logp = write_log(bench, "stage_d1_m3a3_rowD")
        revp = write_review(peer, "2026-09-22-s6.md",
                            names="tools/recipes/stage_d1_m3a3_rowD.py", age_s=600)
        guard_peer.BENCH, guard_peer.PEER = bench, peer
        rc1 = run_main(CMD)
        rc2 = run_main(CMD)
        body = read(revp)
        n_cit = body.count("SAME-ROW: stage_row.log")
        gate(rc1 == 0 and rc2 == 0 and n_cit == 1,
             "S6 two releases of the same log write exactly ONE SAME-ROW citation",
             "rc %s/%s, citations=%d" % (rc1, rc2, n_cit))
        gate(guard_peer.DISPOSITION_H in body,
             "S6b the citation sits under the review's own disposition heading")
        gl = read(os.path.join(bench, "jev_gate.log"))
        gate("RULE-SAME-ROW |" in gl and "stage_d1_m3a3_rowD" in gl and "stage_row.log" in gl,
             "S7 jev_gate.log records the release, the log and the script",
             (gl.strip().splitlines() or ["(empty)"])[-1][:120])
        gate(not any(x.startswith("FIXED:") or x.startswith("REFUTED:") or x.startswith("PRIOR-ART:")
                     for x in body.splitlines()),
             "S7b the citation is NOT a release line (cannot release a prior-art verdict)")

        # --- S8 named only in the ANSWER, not in the question or the headers
        rc, err, _l, _r, _b, _p = case(
            tmp, "s8", "stage_d1_m3a3_rowD",
            {"names": "an unrelated row", "age_s": 600,
             "answer": "compare this with tools/recipes/stage_d1_m3a3_rowD.py, which does it differently"}, 2)
        gate(rc == 2 and "RULE-SAME-ROW" not in err,
             "S8 a script mentioned only inside the ANSWER does not bind the review to it",
             "returned %s" % rc)

        # --- S9 log_script(): the script after the `--`, version suffix stripped
        s = guard_peer.log_script(LOG_TMPL % {"script": "stage_x_v12", "log": "z.log"})
        s2 = guard_peer.log_script("no bgrun line here at all\nPASS something\n")
        gate(s == "stage_x" and s2 is None,
             "S9 log_script() takes the run script and strips _v12; None when there is no BGRUN START line",
             "got %r / %r" % (s, s2))

        # --- S10 the REMEDY exemption is untouched
        guard_peer.BENCH, guard_peer.PEER = bench, peer
        gate(run_main("py tools/bgrun.py --max-min 14 --log tools/bench/peer_x.log -- powershell -NoProfile "
                      "-File tools/peer.ps1 -Agent claude -Role hypothesis -Slug x -TaskFile t.txt") == 0,
             "S10 the REMEDY exemption still passes (peer.ps1 dispatch)")
    finally:
        guard_peer.BENCH, guard_peer.PEER, guard_peer.ROOT, jev.get_key = saved
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n=== selftest_guard_peer_samerow: %d pass / %d fail ===" % (NPASS, NFAIL))
    return 0 if NFAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
