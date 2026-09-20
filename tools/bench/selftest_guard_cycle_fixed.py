"""SELF-TEST for `guard_cycle.premature_build` condition (b) and its 2026-09-17 refinement (§11g.3).

PREDICTION CONTRACT - three cases, asserted mechanically, no LabVIEW, no network, no project file touched:

  T1  recipe edited AFTER its review + the NEWEST prior-art archive's "## What was done with it" cites that
      recipe in a valid `FIXED:` line                                    -> ALLOWED  (premature_build -> None)
  T2  recipe edited AFTER its review, no such citation anywhere          -> REFUSED  (a refusal string)
  T3  no prior-art review archived at all                               -> REFUSED  (a refusal string)

Plus three lines that must NOT release, because the refinement must not become a way around the verdict gate:
  T4  the FIXED line cites the recipe but sits ABOVE the disposition heading -> REFUSED
  T5  the FIXED line cites a path that does not exist                        -> REFUSED
  T6  the FIXED line cites a recipe last changed BEFORE the review           -> REFUSED

PRIOR ART CHECKED BEFORE WRITING (CLAUDE.md, the fourth review's question - has this already been built?):
  `ls tools/bench/selftest*` -> `selftest_bgrun.py` only (a bgrun runner test, unrelated);
  `grep -rl premature_build tools/` -> only `tools/hooks/guard_cycle.py` itself. No existing test covers it.
  The hook is exercised nowhere else, which is why the 2026-09-17 `_rel()` ValueError crash was found by hand.

B1/B2 - THE DELIBERATE-BAD-INPUT PROOF (added 2026-09-18, cycle 20 step 1, plan Pre-decided 3: "a gate that
passes only its happy path is not accepted"). The same two fixtures as T6/T1, differing in ONE bit - whether the
cited path's last change is BEFORE or AFTER the review - printed with the gate's VERBATIM text, so the log shows
the refusal itself rather than a score:
  B1  BAD  : `FIXED:` release citing a path last changed BEFORE the review -> must REFUSE (CLAUDE.md:449 (b))
  B2  GOOD : the same release citing a path last changed AFTER the review  -> must ALLOW

HOW IT ISOLATES. `premature_build` reads three module globals - ROOT, BENCH, PEER. The test points all three at
a temp tree, so nothing under the project is created, read or timestamped. The real `archive/peer/` and
`tools/bench/` are never consulted.
"""
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import guard_cycle  # noqa: E402

REVIEW = """---
type: peer
---
- **date:** 2026-09-17 10:00
- **outcome:** ANSWERED

## Answer
PRIOR-ART: novel

%s
"""


def build_tree(td, *, with_review=True, fixed_line=None, above=False, recipe_mtime_offset=+600):
    """A temp project: <td>/tools/recipes/r.py, <td>/tools/bench, <td>/archive/peer."""
    rec_dir = os.path.join(td, "tools", "recipes")
    bench = os.path.join(td, "tools", "bench")
    peer = os.path.join(td, "archive", "peer")
    for d in (rec_dir, bench, peer):
        os.makedirs(d, exist_ok=True)
    recipe = os.path.join(rec_dir, "r.py")
    with open(recipe, "w", encoding="utf-8") as f:
        f.write("# recipe\n")
    rt = time.mktime((2026, 9, 17, 10, 0, 0, 0, 0, -1))          # the review's frontmatter instant
    os.utime(recipe, (rt + recipe_mtime_offset, rt + recipe_mtime_offset))
    if with_review:
        body = REVIEW % (("%s\n\n## What was done with it\n" % fixed_line) if (fixed_line and above)
                         else ("## What was done with it\n\n%s\n" % (fixed_line or "nothing to fix.")))
        p = os.path.join(peer, "2026-09-17-priorart-selftest.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        os.utime(p, (rt, rt))
    guard_cycle.ROOT, guard_cycle.BENCH, guard_cycle.PEER = td, bench, peer
    return recipe


def run(name, expect_allowed, **kw):
    with tempfile.TemporaryDirectory() as td:
        recipe = build_tree(td, **kw)
        cmd = "py tools/recipes/r.py"
        # premature_build resolves a relative recipe against ROOT, which is the temp tree here.
        msg = guard_cycle.premature_build(cmd)
        allowed = msg is None
        ok = (allowed == expect_allowed)
        print("%-4s %-8s expected=%-8s got=%-8s %s" % (
            name, "PASS" if ok else "FAIL",
            "ALLOWED" if expect_allowed else "REFUSED",
            "ALLOWED" if allowed else "REFUSED",
            "" if allowed else "| " + (msg or "").splitlines()[0][:70]))
        assert os.path.isfile(recipe)
        return ok


def verbatim(name, expect_allowed, **kw):
    """One case printed WITH THE GATE'S OWN TEXT - the negative proof the plan's Pre-decided 3 demands."""
    with tempfile.TemporaryDirectory() as td:
        build_tree(td, **kw)
        msg = guard_cycle.premature_build("py tools/recipes/r.py")
        allowed = msg is None
        ok = (allowed == expect_allowed)
        print("\n" + "=" * 96)
        print("%s   expected=%s  got=%s  ->  %s" % (
            name, "ALLOWED" if expect_allowed else "REFUSED",
            "ALLOWED" if allowed else "REFUSED", "PASS" if ok else "FAIL"))
        print("-" * 96)
        print(msg if msg is not None else
              "(premature_build returned None - ALLOWED, so the gate emits no text)")
        print("=" * 96)
        return ok


FIXED_OK = "FIXED: novel - tools/recipes/r.py:1 - the review's findings were folded into the recipe."
FIXED_MISSING = "FIXED: novel - tools/recipes/nosuch.py:1 - cites a file that does not exist."
FIXED_OTHER = "FIXED: novel - tools/recipes/r.py:1 - cited, but above the heading."


def main():
    saved = (guard_cycle.ROOT, guard_cycle.BENCH, guard_cycle.PEER)
    try:
        results = [
            run("T1", True, fixed_line=FIXED_OK),
            run("T2", False, fixed_line=None),
            run("T3", False, with_review=False),
            run("T4", False, fixed_line=FIXED_OTHER, above=True),
            run("T5", False, fixed_line=FIXED_MISSING),
            run("T6", False, fixed_line=FIXED_OK, recipe_mtime_offset=-600),
        ]
        neg = [
            verbatim("B1 BAD  INPUT  - FIXED: cites a path last changed BEFORE the review (CLAUDE.md:449 b)",
                     False, fixed_line=FIXED_OK, recipe_mtime_offset=-600),
            verbatim("B2 GOOD INPUT  - the same FIXED: line, path last changed AFTER the review",
                     True, fixed_line=FIXED_OK, recipe_mtime_offset=+600),
        ]
    finally:
        guard_cycle.ROOT, guard_cycle.BENCH, guard_cycle.PEER = saved
    npass = sum(1 for r in results if r)
    print("\nSELFTEST guard_cycle premature_build (b): %d pass / %d fail" % (npass, len(results) - npass))
    print("NEGATIVE PROOF (plan Pre-decided 3): %d pass / %d fail   [B1 must REFUSE, B2 must ALLOW]"
          % (sum(1 for r in neg if r), sum(1 for r in neg if not r)))
    return 0 if (npass == len(results) and all(neg)) else 1


if __name__ == "__main__":
    sys.exit(main())
