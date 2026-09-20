r"""selftest_guard_cycle_rerun.py - the three cases of guard_cycle.premature_build condition (b) after the
2026-09-17 RE-RUN EXEMPTION (judgement decision B, cycle 15).

WHAT ALREADY EXISTS, checked before writing this (CLAUDE.md "before creating any new op/tool"):
  * `tools/bench/selftest_bgrun_fail_scan.log` (7/7, 2026-09-17) is the pattern this file copies - a self-test of a
    GATE, driven by fabricated files in a temp directory, asserting the gate's own function rather than a run.
  * `grep -n "^def " tools/hooks/guard_cycle.py` -> premature_build/fixed_slugs/review_time/stamp/newest_*; no
    self-test existed for any of them. `ls tools/bench | grep -i selftest` -> selftest_bgrun_fail_scan.py only.
  * The gate is exercised in anger by every recipe run, but only in its BLOCKING direction; nothing ever proved the
    ALLOW direction, which is exactly the half this change adds.

METHOD. `premature_build()` reads BENCH and PEER as module globals and resolves the recipe path itself, so the test
monkey-patches those two globals to temp directories and passes an ABSOLUTE recipe path (so ROOT never matters).
No LabVIEW, no network, no project file is written or read for its content.

PREDICTION CONTRACT
  C1 recipe edited/created AFTER its prior-art review, and NO build log for it newer than that review
     -> BLOCKED (the first run after an edit still owes a review).
  C2 same, plus `tools/bench/<stem>.log` newer than the review (the recipe already ran once under it)
     -> ALLOWED (None) - a repair re-run inside the failure budget.
  C3 no prior-art review archived at all, even with a build log present
     -> BLOCKED (nothing has ever reviewed this direction).
  C4 (regression, not in the brief - the exemption must not swallow the OTHER half of (b)) a review NEWER than the
     recipe -> ALLOWED, as before the change.

    py tools/bgrun.py --max-min 5 --log tools/bench/selftest_guard_cycle_rerun.log \
        -- py -u tools/bench/selftest_guard_cycle_rerun.py
"""
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import guard_cycle as G  # noqa: E402

NOW = time.time()
passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)


def touch(path, when, body="x"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    os.utime(path, (when, when))
    return path


def scenario(tmp, review_age_h=None, log_age_h=None, recipe_age_h=0.0):
    """Build one filesystem situation and return premature_build()'s verdict.

    `*_age_h` = hours BEFORE now; None = that file is not created."""
    bench = os.path.join(tmp, "bench")
    peer = os.path.join(tmp, "peer")
    for d in (bench, peer):
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.remove(os.path.join(d, f))
    # BUILD_RE only recognises a path containing `tools/recipes/` in COMMAND POSITION, so the fake recipe must
    # live under that spelling or premature_build() returns None for a reason unrelated to the change under test -
    # which is exactly how the first run of this self-test passed C2/C4 and "passed" nothing at all.
    rdir = os.path.join(tmp, "tools", "recipes")
    os.makedirs(rdir, exist_ok=True)
    recipe = touch(os.path.join(rdir, "probe_selftest_v0.py"), NOW - recipe_age_h * 3600)
    if review_age_h is not None:
        touch(os.path.join(peer, "2026-09-17-priorart-selftest.md"), NOW - review_age_h * 3600,
              "- **date:** 2026-09-17\n")
    if log_age_h is not None:
        touch(os.path.join(bench, "probe_selftest_v0.log"), NOW - log_age_h * 3600, "BGRUN END rc=1\n")
    G.BENCH, G.PEER = bench, peer
    cmd = f'py tools/bgrun.py --max-min 20 --log x.log -- py -u "{recipe}"'
    # premature_build resolves the recipe from BUILD_RE's capture group; an absolute path keeps ROOT out of it.
    return G.premature_build(cmd)


def main():
    tmp = tempfile.mkdtemp(prefix="guardcycle_")
    print(f"  temp: {tmp}", flush=True)

    v1 = scenario(tmp, review_age_h=2.0, log_age_h=None, recipe_age_h=0.0)
    gate("C1 first run after an edit, no log under the review -> REFUSED",
         bool(v1) and "NO PRIOR-ART REVIEW NEWER THAN ITSELF" in (v1 or ""),
         "blocked" if v1 else "ALLOWED (wrong)")

    v2 = scenario(tmp, review_age_h=2.0, log_age_h=1.0, recipe_age_h=0.0)
    gate("C2 edited after a failed run that ran under the review -> ALLOWED", v2 is None,
         "allowed" if v2 is None else f"blocked: {v2.splitlines()[0][:80]}")

    v3 = scenario(tmp, review_age_h=None, log_age_h=1.0, recipe_age_h=0.0)
    gate("C3 no prior-art review at all -> REFUSED",
         bool(v3) and "none archived" in (v3 or ""),
         "blocked" if v3 else "ALLOWED (wrong)")

    v4 = scenario(tmp, review_age_h=0.0, log_age_h=None, recipe_age_h=2.0)
    gate("C4 (regression) review newer than the recipe -> ALLOWED", v4 is None,
         "allowed" if v4 is None else f"blocked: {v4.splitlines()[0][:80]}")

    print(f"\n=== selftest_guard_cycle_rerun: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
