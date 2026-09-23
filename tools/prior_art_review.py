r"""prior_art_review.py - the FOURTH review: "have we already done this?"

Added 2026-09-15 on the user's instruction, after a day in which most of the cost came not from bad reasoning but
from not looking:

  * step 0a derived a Traverse index by hand THREE times while `fidx()`, `new_since()` and `loop_diagram()`
    already existed - one of them documented as "Use this, NOT position matching";
  * "can we move a node between diagrams?" was called the central risk while docs/toolkit-capabilities.md already
    had the heading "the build route is clear, and 'move a node' was never needed";
  * camera-acquisition-facts.md line 183 was quoted to justify an ordering that line 139 of the same file refutes;
  * `VI.Get Errors` was nearly rebuilt, though the same file records it as having FAILED twice.

The other three reviews cannot catch this. guard_peer attacks a DIAGNOSIS, retrospective.py attacks how a CYCLE
was run, outcome_review.py attacks whether the work reaches the GOAL. None asks the cheapest question first.

The peer gets the plan plus a MACHINE-GATHERED inventory of what the project already owns, so the answer is
grounded in the repository rather than in my summary of it. Codex is the reviewer: it reads the project directory.

  py tools/prior_art_review.py --plan-file <path> --slug <slug> --recipe tools/recipes/<r>.py
  py tools/prior_art_review.py --plan-file <path> --slug <slug> --no-recipe "why there is no recipe"
  py tools/prior_art_review.py --plan "..." --recipe <r> --dry-run

ONE OF `--recipe` / `--no-recipe "<reason>"` IS MANDATORY (cycle 18, 2026-09-18). Until that date, omitting
`--recipe` merely printed `STOP RECORD: NOT ARMED` and carried on - so the launch gate built to stop a blocked
recipe could be left inert by simple OMISSION, which is not a decision anybody ever took. This script now REFUSES
instead, and keeps the opt-out explicit and auditable: `--no-recipe "<reason>"` runs the review, writes the reason
verbatim into the archived review file, and says on the line that no launch gate was armed. Same shape as the GUI
gate's `-Exception` + `-Evidence`.
"""
import argparse
import glob
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

QUESTIONS = """You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle."""


def inventory(use_index=False):
    """NO INDEX. This is the measured configuration, not an omission.

    An index was built for this reviewer and benchmarked against eight real prior-art items split by whether the
    index carried the answer (tools/bench/priorart_scores.md, two arms x two repeats, opus/high):

        arm             group A (in the index)   group B (old, unindexed)   cost
        no index              3.0 / 4                  3.5 / 4             $2.94
        sharded index         4.0 / 4                  1.0 / 4             $3.60

    The index helps on what it contains and CRIPPLES everything else - both indexed runs scored 1/4 on the old
    material, both control runs 3/4 and 4/4. Given an index the cell treats it as the evidence base and stops
    searching `archive/`; given nothing it searches, and the half-forgotten exchanges are exactly what this review
    exists to surface. Total recall 6.5/8 against 5.0/8, and 22 % cheaper.

    So the reviewer is pointed at the repository and left to search it. `--index` is kept only to re-run the
    experiment; it needs an index that no longer exists (`docs/index/` and its builder were deleted on the user's
    instruction, 2026-09-16). Read priorart_scores.md before building another one - this was measured, not argued.
    """
    if not use_index:
        return ("=== NO INDEX ===\nSearch the project directory yourself: `docs/`, `archive/` (peer exchanges and "
                "narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, "
                "`archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as "
                "the corpus - the answers that matter are often in old exchanges nobody annotated.\n")
    return _name_lists()


def _name_lists():
    def ls(pat, n=400):
        return sorted(os.path.basename(p) for p in glob.glob(os.path.join(ROOT, pat)))[:n]

    gs = os.path.join(ROOT, "tools", "gscript.py")
    funcs = []
    if os.path.exists(gs):
        with open(gs, encoding="utf-8", errors="replace") as f:
            funcs = re.findall(r"^def (\w+)\(", f.read(), re.M)
    idx_rows = 0
    idx = os.path.join(ROOT, "archive", "benchmarks", "INDEX.md")
    if os.path.exists(idx):
        with open(idx, encoding="utf-8", errors="replace") as f:
            idx_rows = len(re.findall(r"^\| \d+ \|", f.read(), re.M))
    claudedev = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
    vis = sorted(os.path.basename(p) for p in glob.glob(os.path.join(claudedev, "*.vi"))) \
        if os.path.isdir(claudedev) else []
    return (
        "=== WHAT THIS PROJECT ALREADY OWNS (machine-gathered) ===\n"
        f"-- docs/ ({len(ls('docs/*.md'))}):\n   " + ", ".join(ls("docs/*.md")) + "\n"
        f"-- tools/recipes/ ({len(ls('tools/recipes/*.py'))}):\n   " + ", ".join(ls("tools/recipes/*.py")) + "\n"
        f"-- tools/bench/ logs ({len(ls('tools/bench/*.log'))}):\n   " + ", ".join(ls("tools/bench/*.log")) + "\n"
        f"-- gscript.py public functions ({len(funcs)}):\n   " + ", ".join(funcs) + "\n"
        f"-- claudeDev VIs ({len(vis)}):\n   " + ", ".join(vis) + "\n"
        f"-- archived peer exchanges ({len(ls('archive/peer/*.md'))}):\n   "
        + ", ".join(ls("archive/peer/*.md")) + "\n"
        f"-- archive/benchmarks/INDEX.md has {idx_rows} numbered rows\n"
        "Read any of these directly; they are all in the project directory.\n")


# THE TWO REFUSALS (cycle 18, 2026-09-18 - the judgement decision that followed the stop-record build).
# "A device that can be left un-armed by simple omission is not running - it is inert." An OMISSION is not a
# decision; an explicit, reasoned opt-out is. Same shape as the GUI gate's `-Exception` + `-Evidence`, which is the
# one place in this project where that distinction is already mechanical.
_USAGE = ("  py tools/bgrun.py --max-min 20 --log tools/bench/priorart_<slug>.log -- \\\n"
          "     py tools/prior_art_review.py --plan-file <plan> --slug <slug> --trigger cycle-start \\\n"
          "        --recipe tools/recipes/<the recipe this review is about>.py\n"
          "  (repeat --recipe for each recipe; launch it from PowerShell - the Bash tool returns rc 127 today)\n")

REFUSE_NO_RECIPE = (
    "REFUSED by tools/prior_art_review.py: no --recipe, and no explicit opt-out.\n\n"
    "A prior-art verdict other than `novel` has to STOP the recipe it is about, and stopping needs that recipe's\n"
    "PATH. This script cannot derive one from --plan/--slug, so the caller states it. Until 2026-09-18 omitting\n"
    "the flag printed one line and carried on - which left the launch gate armed or inert depending on whether\n"
    "somebody remembered a flag. That is not a decision anybody took.\n\n"
    "Name the recipe:\n" + _USAGE +
    "\nOr state, in words, why this review has no recipe - a plan document, a direction change:\n"
    "     py tools/prior_art_review.py --plan-file <plan> --slug <slug> \\\n"
    "        --no-recipe \"this reviews a plan document; no recipe exists yet\"\n"
    "The reason is written verbatim into the archived review file, so the opt-out is auditable. An empty or\n"
    "whitespace-only reason is not an opt-out. --no-recipe releases nothing and stops nothing; it only records\n"
    "that no launch gate was armed, and why.\n")

REFUSE_BOTH = (
    "REFUSED by tools/prior_art_review.py: --recipe and --no-recipe were BOTH given.\n"
    "They are contradictory: --recipe arms the launch gate for a named recipe, --no-recipe records that this\n"
    "review has none. Pass exactly one.\n")


def record_opt_out(review_path, reason):
    """Write a `--no-recipe` reason into the archived review file. Returns True if it landed.

    AUDITABILITY IS THE POINT (the GUI gate logs every authorized exception to tools/gui_actions.log; this is the
    same idea one layer up). The block is deliberately shaped so that NO gate can mistake it for something else:
    no line in it starts with `FIXED:`, `REFUTED:` or `PRIOR-ART:` - the three line-anchored patterns
    guard_cycle.py matches (FIXED_RE, REFUTED_RE, PRIOR_ART_RE, all `re.M` with `^`) - and the heading is not
    `## What was done with it`, so it neither releases a verdict nor counts as a disposition for doc_lint's L6."""
    block = ("\n\n## Launch gate - NO RECIPE (explicit opt-out)\n\n"
             "No stop record was armed for this review. `tools/prior_art_review.py` was run with `--no-recipe`,\n"
             "and its mandatory reason is recorded here verbatim:\n\n"
             "    NO-RECIPE: %s\n\n"
             "This is an opt-out, not a release. It frees no recipe and discharges no verdict; the only release\n"
             "lines are the two `guard_cycle.py` already validates, and neither of them is this.\n"
             % " ".join(str(reason).split()))
    try:
        with open(review_path, "a", encoding="utf-8") as f:
            f.write(block)
    except OSError as e:
        print("   NO-RECIPE opt-out could NOT be recorded in %s: %s" % (review_path, e), flush=True)
        return False
    try:
        shown = os.path.relpath(review_path, ROOT)
    except ValueError:
        shown = review_path
    print("   NO-RECIPE opt-out recorded in %s: %s" % (shown, " ".join(str(reason).split())), flush=True)
    return True


# --- JEV: HAS THIS STEP ALREADY BEEN PRIOR-ART REVIEWED? (2026-09-22, docs/jev-integration-plan.md row #6) ----
# ADVISORY ONLY, BY THE USER'S OWN PROCEDURE for every Jev insertion: "보조 신호로 시작해 몇 사이클 일치를 본 뒤
# 승격한다" - start as a side signal that overrides no existing rule, watch it for a few cycles, then promote.
# So this NEVER refuses a dispatch and never changes what the reviewer is asked. It prints one line to stderr and
# appends the same line to tools/bench/jev_gate.log when some recently archived prior-art review already answers
# this step at p >= jev_gate.DUP_P, so the cycles of agreement can be counted from a file rather than remembered.
# Promotion to a refusal is the USER's call, not this file's.
def jev_advisory(slug, plan):
    """One `JEV-PRIORART-DUP` line when an archived prior-art review already answers this step. Never raises,
    never blocks, and is a complete no-op without TYPESAFE_API_KEY."""
    try:
        sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
        import jev_gate
        # The STEP, not the whole plan: the first non-empty, non-frontmatter, non-heading prose of what is under
        # review, plus the slug. A whole plan document scores as "the whole plan", which is the useless answer.
        lines, body = [], plan.split("---", 2)[-1] if plan.lstrip().startswith("---") else plan
        for ln in body.splitlines():
            s = ln.strip().lstrip("#*- ").strip()
            if len(s) > 40 and not s.startswith("|"):
                lines.append(s)
            if len(" ".join(lines)) > 600:
                break
        step = ("prior-art slug %s. " % slug) + " ".join(lines)[:700]
        line = jev_gate.jev_priorart_dup(step)
        if line:
            sys.stderr.write(line + "\n   ADVISORY ONLY - this dispatch is NOT blocked. Open that review before "
                             "paying for another one (CLAUDE.md section 5: check archive/peer/ before re-asking).\n")
            print("   " + line, flush=True)
    except Exception:                    # noqa: BLE001 - an advisory must never break the dispatcher
        pass


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan")
    ap.add_argument("--plan-file")
    ap.add_argument("--slug", default="prior-art")
    # The three moments this review fires (user's decision, 2026-09-15). `new-op` is the one a cycle-start-only
    # trigger would miss: OpOwnerChain_v0 was invented in the middle of a cycle.
    ap.add_argument("--trigger", choices=["cycle-start", "direction-change", "new-op"], default="new-op")
    ap.add_argument("--model", default="claude-opus-5-5")  # user 2026-09-23: Opus 5.5 pinned
    ap.add_argument("--effort", default="medium", choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--index", action="store_true",
                    help="re-run the losing experiment: attach a name listing. Default is NO index - see the "
                         "measurement in tools/bench/priorart_scores.md before using this.")
    ap.add_argument("--dry-run", action="store_true")
    # THE STOP RECORD (cycle 18, docs/cycle18-plan.md Pre-decided 2). A verdict other than `novel` must STOP the
    # recipe it is about, and stopping needs the recipe's PATH + HASH.
    # MEASURED LIMIT, not a workaround: this script CANNOT derive that path. Its inputs are `--plan/--plan-file`
    # (a document) and `--slug` (a label); nothing here names a recipe, and guessing one from the plan's prose is
    # exactly the inference this project keeps paying for. So the caller states it - and since 2026-09-18 the
    # caller MUST state it, either as a path or as a reason (see REFUSE_NO_RECIPE below).
    ap.add_argument("--recipe", action="append", default=[],
                    help="the recipe file(s) this review is about. A verdict other than `novel` then plants a "
                         "stop record (tools/stop_record.py) that refuses to LAUNCH them until a FIXED:/REFUTED: "
                         "line releases it. Required unless --no-recipe is given.")
    ap.add_argument("--no-recipe", dest="no_recipe", metavar="REASON",
                    help="EXPLICIT, REASONED OPT-OUT from arming the launch gate, for a review that genuinely has "
                         "no recipe (a plan document, a direction change). The reason is mandatory, must be "
                         "non-empty, and is written verbatim into the archived review file so the opt-out is "
                         "auditable. It is not a release: it stops nothing and frees nothing.")
    a = ap.parse_args()
    reason = (a.no_recipe or "").strip()
    if a.recipe and reason:
        sys.stderr.write(REFUSE_BOTH); return 2
    if not a.recipe and not reason:
        sys.stderr.write(REFUSE_NO_RECIPE); return 2
    if a.plan_file:
        plan = open(a.plan_file, encoding="utf-8").read()
    elif a.plan:
        plan = a.plan
    else:
        print("need --plan or --plan-file"); return 2

    status = ""
    sp = os.path.join(ROOT, "STATUS.md")
    if os.path.exists(sp):
        with open(sp, encoding="utf-8", errors="replace") as f:
            status = f.read()
    task = (f"PRIOR-ART REVIEW (trigger: {a.trigger}).\n\n{QUESTIONS}\n\n"
            f"=== WHAT IS UNDER REVIEW ===\n{plan}\n\n"
            f"=== STATUS.md IN FULL (the project's current decisions and state) ===\n{status}\n\n"
            f"{inventory(a.index)}")
    jev_advisory(a.slug, plan)
    scratch = os.path.join(os.environ.get("TEMP", "."), f"priorart_{a.slug}.txt")
    with open(scratch, "w", encoding="utf-8") as f:
        f.write(task)
    print(f"   task written to {scratch} ({len(task)} chars)", flush=True)
    if a.dry_run:
        print(task[:2000]); return 0
    # The CLAUDE peer, in its `priorart` role: this job needs to read archive/ as well as the active docs, which is
    # what the claude cell is briefed to do (and an explicit exception to CLAUDE.md rule 4). opus / high effort
    # because a shallow read misses exactly what this review exists to catch. -Kind fact: the prompt carries its own
    # instruction set and has no claim to refute.
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           f"& '{os.path.join(HERE, 'peer.ps1')}' -Agent claude -Role priorart -Kind fact "
           f"-Model {a.model} -Effort {a.effort} -TimeoutSec 900 "
           f"-Slug priorart-{a.slug} -Task (Get-Content -Raw '{scratch}')"]
    r = subprocess.run(cmd, cwd=ROOT, text=True, timeout=900)
    print(f"   peer.ps1 rc {r.returncode}; archived as archive/peer/<date>-priorart-{a.slug}.md", flush=True)
    arm_stop_records(a.slug, a.recipe, opt_out=reason)
    return r.returncode


def arm_stop_records(slug, recipes, opt_out=""):
    """Plant a stop record for each `--recipe` if this review's verdicts are not all `novel`.

    The verdict parse is guard_cycle's, imported, not restated: same `PRIOR_ART_RE`, same allowlist, same
    "scan the ANSWER, not the question's menu line" rule that made the gate inert for a day in cycle 12."""
    sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import guard_cycle
    import stop_record
    cands = glob.glob(os.path.join(ROOT, "archive", "peer", f"*priorart-{slug}*.md"))
    if not cands:
        print(f"   STOP RECORD: none - no archived review matched *priorart-{slug}*.md", flush=True)
        if opt_out:
            print("   NO-RECIPE opt-out could NOT be recorded: there is no archived review to write it into. "
                  "The reason given was: %s" % " ".join(str(opt_out).split()), flush=True)
        return []
    path = max(cands, key=os.path.getmtime)
    if opt_out:
        record_opt_out(path, opt_out)
    with open(path, encoding="utf-8", errors="replace") as f:
        body = f.read()
    answer = body.split("\n## Answer", 1)[-1]
    found = [s for s in guard_cycle.PRIOR_ART_RE.findall(answer)
             if s in guard_cycle.PRIOR_ART_SLUGS and s != "novel"]
    found = list(dict.fromkeys(found))
    if not found:
        print(f"   STOP RECORD: none - {os.path.basename(path)} carries no blocking verdict", flush=True)
        # cycle 72 firefighter: a novel verdict over EDITED bytes must be recorded, or an OLDER released record
        # (stamped for the previous bytes) keeps refusing the launch (stop_record.write_novel_record).
        out = []
        for rp in recipes:
            try:
                rec = stop_record.write_novel_record(rp, path)
            except stop_record.StoreError as e:
                print(f"   NOVEL RECORD not written for {rp}: {e}", flush=True)
                continue
            out.append(rec)
            print(f"   NOVEL RECORD written: {rec['recipe_path']} sha {(rec['reviewed_sha256'] or '')[:12]} "
                  f"-> these bytes are released by this review; editing them again re-arms the gate", flush=True)
        return out
    if not recipes:
        # ONLY REACHABLE UNDER AN EXPLICIT OPT-OUT: main() refuses when neither --recipe nor --no-recipe is given
        # (2026-09-18). So this line no longer reports an omission - it reports a decision somebody made and
        # signed, and it still says loudly that blocking verdicts are standing with nothing to enforce them.
        print(f"   STOP RECORD: NOT ARMED BY EXPLICIT OPT-OUT - verdicts {', '.join(found)} block, and "
              f"--no-recipe was given:\n"
              f"     reason: {' '.join(str(opt_out).split()) or '(none - this is a bug; main() should have refused)'}\n"
              f"   If this review does become a recipe, plant the record by hand:\n"
              f"     py tools/stop_record.py write --recipe <recipe> --review "
              f"{os.path.relpath(path, ROOT)} --verdict {' '.join(found)}", flush=True)
        return []
    out = []
    for rp in recipes:
        rec = stop_record.write_stop_record(rp, path, found)
        out.append(rec)
        print(f"   STOP RECORD armed: {rec['recipe_path']} sha {(rec['reviewed_sha256'] or '')[:12]} "
              f"verdict {', '.join(found)} -> launching it is refused until a FIXED:/REFUTED: line releases it",
              flush=True)
    return out


if __name__ == "__main__":
    sys.exit(main())
