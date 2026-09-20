r"""outcome_review.py - the THIRD review layer: does the project's work reach the project's goal?

WHY THIS EXISTS (user, 2026-09-15: "주기적으로 프로젝트의 성과를 판단하는 피어도 필요하지 않을까 싶은데").
The two existing layers both ask HOW, never WHETHER:

    guard_peer      -> per failed prediction : "is this diagnosis right?"
    retrospective   -> per cycle             : "was this cycle run well?"
    outcome_review  -> per 5 cycles or 7 d   : "did any of it move the deliverable?"    <- this file

A cycle can be run impeccably - every hypothesis reviewed, every rule honoured - and still be the
wrong cycle. Nobody was asking whether 168 op VIs was the right price for the spine, or whether the
standing work order still made sense. That question cannot come from the session doing the work.

DELIBERATELY SMALL. The first honest verdict of a review like this, in a project that already owns
four hooks, an audit, a retrospective dispatcher and a violation counter, is very likely
`tooling-over-delivery`. Building an elaborate apparatus to hear that would prove the point. So this
is one script, one dispatch and one line in guard_cycle.py - nothing else, by the user's condition.

The peer WAS CODEX, never claude: "was this work worth doing" is exactly the question a reviewer that
shares the asker's priors is worst at.

CHANGED 2026-09-18 (user's decision, a TRIAL): the reviewer is now `peer.ps1 -Agent claude -Role outcome`
= FABLE at medium effort, run with --safe-mode so the cell does NOT load CLAUDE.md or this project's rules
into its system prompt. Codex is at 9 % of its weekly quota ("Codex 잔여량이 생각보다 얼마 남지 않음 ...
Codex가 수행중인 역할을 fable로 구동하는게 어떨까 싶음"), and a review layer that cannot be dispatched is
worth less than one dispatched to a different model. The ORIGINAL objection still stands and is answered by
the thin prompt rather than by the vendor: what made codex the right reviewer was that it did not share the
asking session's priors, and a cell that never reads CLAUDE.md, STATUS.md's framing or the plan documents
starts from the user's requirements and the counted output - which is what QUESTIONS below hands it.
Codex remains one flag away: `-Agent codex -Kind fact`.

  py tools/outcome_review.py [--dry-run]        # --due prints whether one is overdue, and exits
                                                # --dry-run also resolves the dispatch via peer.ps1 -DryRun
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PEER = os.path.join(ROOT, "archive", "peer")
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"

EVERY_N_CYCLES = 5
EVERY_N_DAYS = 7

QUESTIONS = """Judge this project's OUTCOMES, not its process. Its individual cycles have already been reviewed for
how they were run, and those reviews passed; that is not what is being asked here. You are being asked whether the
work is reaching the goal the user actually stated, and whether its price was defensible.

Read project-requirements/ first - that is the user's own statement of what this project is for - then answer these
in order, naming the file or log that shows each thing:

1. DELIVERABLE. What can the user RUN today that they could not at the last outcome review? Name the artefact and
   the evidence that it works. "A VI exists" is not evidence; "it ran and produced these numbers" is.
2. GOAL ALIGNMENT. Go through the numbered requirements one by one. Which advanced? Which has NOT MOVED since the
   project began? Say the second list out loud even if it is uncomfortable.
3. COST vs PRODUCT. The counted output is attached. Is that ratio defensible for what exists? Name specifically
   what a competent engineer would have SKIPPED.
4. ORDERING AT PROJECT SCALE. The standing work order is in STATUS.md. Given everything now known, is it still
   right - or should something currently scheduled last come first?
5. STALE DECISIONS. Which OPEN questions have been open longest, and what is blocked behind each? Is anything
   waiting on the user that should have been asked weeks ago?
6. THE EXPERIMENT TEST. If the user had to run a real experiment next week, what would they use: the original VI,
   or something this project produced? If the original, say plainly why.
7. TERMINATION. What is the SHORTEST remaining path to something the user can actually use, and what should be
   abandoned to get there?

Then END YOUR ANSWER with machine-readable lines, one per finding, using a slug from this list:
  goal-requirement-not-advanced - tooling-over-delivery - product-not-runnable - ordering-stale -
  decision-starved - scope-inflation - measurement-without-product
Format exactly:
  OUTCOME-VIOLATION: <slug>
Use `OUTCOME-VIOLATION: none` if there are none. Do not invent slugs; map to the closest and explain in the prose.

A note on what a finding here means: a process violation is answered by building a mechanical device. An OUTCOME
violation cannot be - no tool fixes goal drift. It is answered by making the next cycle a DELIVERY cycle, and on
repetition by stopping and re-planning with the user. Write your answer knowing that is the consequence."""


def _count(pattern):
    try:
        return len(glob.glob(pattern))
    except OSError:
        return 0


def reviews_since_last():
    """(n_retrospectives_since, days_since, last_path_or_None) - the cadence, read from the files."""
    outs = sorted(glob.glob(os.path.join(PEER, "*outcome-review*.md")), key=os.path.getmtime)
    last = outs[-1] if outs else None
    since = os.path.getmtime(last) if last else 0.0
    retros = [p for p in glob.glob(os.path.join(PEER, "*retrospective-cycle*.md"))
              if os.path.getmtime(p) > since]
    days = (time.time() - since) / 86400.0 if last else 999.0
    return len(retros), days, last


def is_due():
    n, days, last = reviews_since_last()
    if last is None:
        return True, "no outcome review has ever been archived"
    if n >= EVERY_N_CYCLES:
        return True, f"{n} cycle retrospectives since {os.path.basename(last)} (every {EVERY_N_CYCLES})"
    if days >= EVERY_N_DAYS:
        return True, f"{days:.1f} days since {os.path.basename(last)} (every {EVERY_N_DAYS})"
    return False, f"{n}/{EVERY_N_CYCLES} cycles, {days:.1f}/{EVERY_N_DAYS} days since {os.path.basename(last)}"


def evidence():
    reqs = sorted(glob.glob(os.path.join(ROOT, "project-requirements", "*.md")))
    bench_rows = 0
    idx = os.path.join(ROOT, "archive", "benchmarks", "INDEX.md")
    if os.path.exists(idx):
        with open(idx, encoding="utf-8", errors="replace") as f:
            bench_rows = len(re.findall(r"^\| \d+ \|", f.read(), re.M))
    open_block = ""
    st = os.path.join(ROOT, "STATUS.md")
    if os.path.exists(st):
        with open(st, encoding="utf-8", errors="replace") as f:
            body = f.read()
        m = re.search(r"^## OPEN.*?(?=^## |\Z)", body, re.M | re.S)
        open_block = m.group(0) if m else "(no OPEN section found in STATUS.md)"
    n, days, last = reviews_since_last()
    return (
        "=== COUNTED OUTPUT (machine-gathered; this is the price side of question 3) ===\n"
        f"  op VIs in claudeDev      : {_count(os.path.join(CLAUDEDEV, '*.vi'))}\n"
        f"  recipe scripts           : {_count(os.path.join(ROOT, 'tools', 'recipes', '*.py'))}\n"
        f"  archived peer exchanges  : {_count(os.path.join(PEER, '*.md'))}\n"
        f"  benchmark rows in INDEX  : {bench_rows}\n"
        f"  documents under docs/    : {_count(os.path.join(ROOT, 'docs', '*.md'))}\n"
        f"  cycle retrospectives     : {_count(os.path.join(PEER, '*retrospective-cycle*.md'))}"
        f"  ({n} since the last outcome review, {days:.1f} days)\n"
        f"  deliverable VIs built    : "
        f"{', '.join(os.path.basename(p) for p in glob.glob(os.path.join(CLAUDEDEV, 'Track_v6*.vi'))) or '(none)'}\n"
        "\n=== THE USER'S OWN STATEMENT OF THE GOAL (read these in full) ===\n"
        + "\n".join("  " + os.path.relpath(p, ROOT) for p in reqs)
        + "\n\n=== STILL OPEN, from STATUS.md (question 5) ===\n" + open_block
        + "\n\nAlso on disk: STATUS.md (current state and the standing work order), "
          "archive/benchmarks/INDEX.md (what was measured and what it showed), "
          "docs/restructure-plan-4.6.md (the plan the work order defers to the end), CLAUDE.md (the rules).\n")


def main():
    # The task embeds STATUS.md's OPEN section, which is partly Korean, and this console is cp949.
    # Without this, --dry-run dies in print() rather than in anything that matters.
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--due", action="store_true", help="print whether a review is overdue, then exit")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    due, why = is_due()
    if a.due:
        print(("DUE: " if due else "not due: ") + why)
        return 1 if due else 0

    task = (f"OUTCOME REVIEW of this project (read-only; open any file you need).\n\n{QUESTIONS}\n\n{evidence()}")
    slug = "outcome-review-" + time.strftime("%Y%m%d")
    scratch = os.path.join(os.environ.get("TEMP", "."), f"{slug}.txt")
    with open(scratch, "w", encoding="utf-8") as f:
        f.write(task)
    print(f"   cadence: {why}", flush=True)
    print(f"   task written to {scratch} ({len(task)} chars)", flush=True)
    # -Kind fact: the adversarial suffix peer.ps1 appends to a 'review' is written for a CLAIM under
    # attack; this dispatch carries its own, longer instruction set and no claim to refute.
    # -Role outcome: fable / medium, --safe-mode (see this file's docstring, 2026-09-18).
    # -TaskFile, not -Task (Get-Content -Raw ...): the question set is 5 kB of mixed Korean/English and argv is
    # exactly what -TaskFile exists to avoid (peer.ps1's own note on PowerShell 5.1 quoting).
    dispatch = (f"& '{os.path.join(HERE, 'peer.ps1')}' -Agent claude -Role outcome -Kind fact -Slug {slug} "
                f"-TimeoutSec 600 -TaskFile '{scratch}'")
    if a.dry_run:
        # Resolve the routing through peer.ps1 itself rather than describing it here - a second description of
        # the role table is how the two copies of a list drift apart (CLAUDE.md's own recurring finding).
        print(task)
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
                            dispatch + " -DryRun"], cwd=ROOT, text=True, timeout=120)
        return r.returncode
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", dispatch]
    r = subprocess.run(cmd, cwd=ROOT, text=True, timeout=900)
    print(f"   peer.ps1 rc {r.returncode}; archived as archive/peer/<date>-{slug}.md", flush=True)
    print("   Now annotate it: 'why asked' and 'verdict', and act on the OUTCOME-VIOLATION lines.", flush=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
