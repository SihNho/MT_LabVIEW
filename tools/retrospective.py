r"""retrospective.py (v2) - end-of-cycle review of HOW the cycle was run, not of any single hypothesis.

WHY THIS EXISTS. The peer loop can only attack what Claude chooses to send it: a framing Claude wrote, evidence
Claude picked. So it criticises hypotheses well and criticises JUDGEMENT AND EXECUTION not at all (user,
2026-09-15: "피어 리뷰를 통해 판단 및 실행 구조에 대한 비평은 할 수 없는 것 같아"). Nobody ever asked whether a
question was worth asking, whether twenty failures were the same failure, or whether a tool should have been built
first. The material is not a summary Claude wrote: it is the machine's own record - the compliance audit
(tools/audit_cycle.py) plus the cycle's build logs, handed to the peer with CLAUDE.md. The questions are fixed, so
Claude cannot steer them.

=== WHY v2 EXISTS (user's decision, 2026-09-16; proposals 1, 2 and 4 adopted, 3 deferred) ===

v1 is frozen at `tools/retrospective_v1.py` and stays runnable for the comparison. It was replaced because it
SATURATED, and the saturation is measured, not argued: seven retrospectives ran (cycles 7-13); five slugs fired in
7 of 7, and cycles 11, 12 and 13 each fired ALL NINE slugs. A counter that always reads "nine" carries no
information, and the rule built on it ("3 occurrences -> build the mechanical device") degenerated into "build a
device every cycle" - which is itself the `tooling-over-delivery` fault the outcome layer exists to catch.

Five causes, each answered by one change here:

  1. ONE QUESTION = ONE SLUG. v1 asked seven questions and offered nine slugs, so a diligent reviewer emitted
     roughly one slug per question by construction.  -> v2's OUTPUT CONTRACT asks for the ONE most costly
     structural fault (at most two), and everything else becomes prose FINDINGS with no slug.
  2. "NAME ONE IF ANY" PHRASING. Every v1 question presupposed its own answer.  -> v2 states in the prompt that
     `VIOLATION: none` is a legitimate and expected answer, and describes what a well-run cycle looks like.
  3. NO SIZE. A 90-second annoyance and a five-hour detour emitted the same line.  -> every violation now carries
     `loss_min`, `loss_usd` (or `?`) and a counterfactual, so the tally can be sorted by cost instead of by count.
  4. NO DEVICE FEEDBACK. Seven cycles of devices were built and nobody ever asked whether one worked.  -> the
     device list is built MECHANICALLY from docs/violation-decisions.md and attached, with the question "did the
     fault this device exists to stop happen anyway?". Its slug is `device-failed`, threshold 1: a device that
     failed once is a broken device, and one more cycle of evidence is not needed to say so.
  5. WRONG EVIDENCE WINDOW. v1 passed `--since-hours` to an audit whose own docstring says it is "a TIME WINDOW,
     not a cycle boundary"; cycle 12's audit therefore reported 19 builds and 37 peer logs spanning three cycles.
     -> v2 computes an explicit window, passes it to audit_cycle.py as --from/--to, lists only the logs inside it,
     and states the window in the task text so the reviewer can see what it is being held to. The FIRST version of
     that window used the plan documents' mtimes and under-captured by construction (a plan is last edited after
     its cycle starts; cycle 11 lost `gscript.py` by 15 seconds). Since 2026-09-16 the boundary is the PREVIOUS
     CYCLE'S RETROSPECTIVE - see cycle_window().

MACHINE-READABLE OUTPUT. The peer answers in prose AND ends with:

    VIOLATION: <slug> | loss_min=<n> | loss_usd=<n or ?> | evidence=<file:line>
    VIOLATION: none

`tools/violations.py` parses both this form and v1's bare `VIOLATION: <slug>`, so the seven historical archives
still count. Claude does not do the counting.

  py tools/retrospective.py --cycle 14 [--slug retrospective-cycle14] [--dry-run]
  py tools/retrospective.py --cycle 11 --slug retrospective-v2-cycle11    # the retroactive comparison runs
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
DECISIONS = os.path.join(ROOT, "docs", "violation-decisions.md")
sys.path.insert(0, HERE)
import logclass  # noqa: E402  - ONE definition of build-vs-machinery; see tools/logclass.py

# THE CONSOLE CODE PAGE IS NOT COSMETIC (measured here 2026-09-16, and it is the THIRD time this project has paid
# for it: retro_cycle12.log:33-36 exited rc=1 on the same defect while the review it wrapped had completed, and
# prior-art run 3 was voided by mojibake evidence). `--dry-run` prints a task full of `—` and Korean; on this
# box's cp949 console that raises UnicodeEncodeError and the tool dies AFTER doing its work.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

SLUGS = ("repeated-failure-class · tool-not-built · inference-over-measurement · rule-evaded · wrong-ordering · "
         "unreported-fact · scope-creep · premature-build · judgement-in-material · device-failed")

CONTRACT = """=== OUTPUT CONTRACT - read this before you read anything else ===

This review has run seven times before. Five slugs fired in 7 of 7 runs, and the last three cycles each fired ALL
NINE. That is saturation, not measurement: the format asked seven questions, offered nine slugs, and got one slug
per question. A tally that always reads "nine" cannot tell a bad cycle from a good one, and the device rule built
on it turned into "build a device every cycle". So the contract has changed, and it is the part of this prompt
that matters most.

1. NAME THE ONE MOST COSTLY STRUCTURAL FAULT OF THIS CYCLE. At most TWO, and a second only if it is genuinely of
   the same magnitude as the first. Not a list. Not one per question. If you find yourself with five candidates,
   your job is to rank them and report the top one - the ranking IS the review.

2. `VIOLATION: none` IS A LEGITIMATE ANSWER, and it is the expected answer for a cycle that was run well. A cycle
   whose faults are all minor - a slow log read, a slightly wide scope, a sentence that could have been clearer -
   has NO structural fault, and saying so is a correct review, not a failed one. Do not manufacture a violation to
   look thorough. Do not treat "something could have been better" as a structural fault; a structural fault is one
   that changed how the cycle ENDED - what it cost, what it produced, or whether it produced anything.

3. FOR EACH FAULT YOU NAME, give all three of:
   (a) THE SLUG, from the fixed list at the bottom. Map to the closest one; do not invent slugs.
   (b) A LOSS ESTIMATE, in minutes AND in dollars where the logs carry the number. The logs that carry cost:
       `COST: $<n>` lines in tools/bench/priorart_*.log and peer_*.log; `BGRUN END rc=<n> after <n>s` in every
       bgrun log; the audit's C3 (build wall-clock), C4 (review wall-clock and cost) and C5 (total) lines. If no
       log carries a dollar figure for this fault, write `loss_usd=?` - a guessed number is worse than an honest
       unknown, and this project has been burned by exactly that (a cost argument made against a figure an order
       of magnitude too small).
   (c) A COUNTERFACTUAL, concrete and on the clock: "had X been done at attempt N / at HH:MM, the cycle would have
       ended at T instead of T'". If you cannot construct one, the fault is probably a FINDING, not a violation.

4. EVERYTHING ELSE YOU OBSERVE GOES IN THE PROSE, UNDER `FINDINGS`. Findings are wanted - the seven questions
   below exist to produce them. They simply do not each produce a slug, and they never did deserve one.
"""

FINDINGS_Q = """=== FINDINGS - answer all seven in prose. These do NOT each produce a slug. ===

Be concrete about which log or file shows each one (file:line).

1. REPEATED FAILURE. Did the same class of failure recur? On which attempt should the approach have changed, and
   to what? Name the attempt number.
2. MISSING TOOL. Is there a reader or op that was NOT built and whose absence made the cycle more expensive? Say
   which failures it would have answered.
3. UNMEASURED STEPS. Was anything decided by inference where a measurement was available and cheap?
4. RULE COMPLIANCE. Read the attached CLAUDE.md. Which of its rules were broken, evaded, or satisfied only
   formally? The compliance audit output is attached - say also what the audit does NOT cover.
5. ORDERING. Was the cycle's order of work defensible, or should some later step have come first?
6. WHAT WAS NOT REPORTED. From the raw logs, is there anything the session's own summary would have hidden or
   understated?
7. JUDGEMENT INSIDE A MATERIAL SESSION. Was any decision taken inside a MATERIAL sub-session (agent `material`,
   `log-reader`, `reporter`, or any `claude -p` cell) that belonged to the judgement session: a design change, a
   choice between explanations, accepting/rejecting a review finding, a change of plan direction, or an action
   pre-scripted in the brief as "if X then do Y"? Cite the log or archive file and line.
"""

DEVICE_Q = """=== DEVICE EFFECT - the question nobody has ever asked ===

Every list below is a MECHANICAL DEVICE this project built because a slug reached its threshold. The list is
generated from docs/violation-decisions.md, not written by the session under review. Seven cycles of devices have
been built and no reviewer has ever been asked whether one of them WORKED.

For EACH device: did the fault it exists to stop occur ANYWAY, inside this cycle's evidence window? Cite
file:line. A device can fail three ways and all three count: it never fired when it should have; it fired and was
worked around; or it fired on the wrong thing so often that it is now routinely bypassed.

If any device failed, emit `VIOLATION: device-failed` with the device named in the `evidence=` field.
ITS THRESHOLD IS 1, NOT 3 - a device that failed once is a broken device, and waiting for two more cycles of
evidence to say so is the same patience that produced the saturation this format replaces.
"""


def parse_devices(path):
    """Every `DECISION: device` block in docs/violation-decisions.md -> (slug, stamp, one-line device).

    Mechanical on purpose (proposal 2): the session under review must not be the one that decides which of its
    devices are worth mentioning. Blocks are `## <slug> — <YYYY-MM-DD>[ HH:MM][ (round N)]`, the same heading form
    `tools/violations.py` already parses, so the two tools cannot drift apart about what a decision block is.
    """
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            body = f.read()
    except OSError:
        return []
    heads = list(re.finditer(r"^##\s*([a-z0-9-]+)\s*[-–—]\s*(\d{4}-\d{2}-\d{2})(?:[ T]+(\d{2}:\d{2}))?(.*)$",
                             body, re.M))
    out = []
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        block = body[m.start():end]
        if not re.search(r"^DECISION:\s*device", block, re.M):
            continue
        # The one-liner: an explicit `Device:` line if the block has one, else the first prose sentence after the
        # DECISION line. Both forms exist in the file; neither is normalised, so read both rather than demanding
        # a format nobody wrote to.
        dm = re.search(r"^Device:\s*(.+?)(?:\n\n|\Z)", block, re.M | re.S)
        if dm:
            one = " ".join(dm.group(1).split())
        else:
            tail = block.split("DECISION:", 1)[-1]
            tail = tail.split("\n", 1)[-1].strip()
            one = " ".join(tail.split())
        out.append((m.group(1), (m.group(2) + (" " + m.group(3) if m.group(3) else "")).strip(),
                    (one[:400] + "…") if len(one) > 400 else one))
    return out


PEER_DIR = os.path.join(ROOT, "archive", "peer")

sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
try:
    from guard_cycle import stamp as _stamp          # bulk-edit-proof, re-archive-aware (2026-09-17, OPEN 31)
except Exception:                                    # pragma: no cover - the gate must never take this file down
    def _stamp(p):
        try:
            return min(os.path.getctime(p), os.path.getmtime(p))
        except OSError:
            return 0.0


def retro_archive(n):
    """The archive of cycle <n>'s OWN retrospective, or None.

    Matched on the exact suffix `retrospective-cycle<n>.md`, which deliberately excludes
    `retrospective-v2-cycle<n>.md`: those are the retroactive comparison runs, not the cycle's review, and letting
    one serve as a boundary would date a cycle by a measurement taken hours after it closed.
    """
    hits = [f for f in glob.glob(os.path.join(PEER_DIR, "*.md"))
            if os.path.basename(f).endswith(f"retrospective-cycle{n}.md")]
    return max(hits, key=os.path.getmtime) if hits else None


def newest_retro_before(now, exclude_slug=None):
    """(path, mtime) of the newest retrospective archived strictly BEFORE `now`, or None.

    EVERY retrospective closes a window, not just the previous CYCLE's (OPEN 31, measured 2026-09-17). A cycle
    number is a label Claude chooses; four of today's reviews were filed as "cycle 15" and "cycle 16" within the
    same eight hours, and `retro_archive(n - 1)` cannot see a same-cycle predecessor, so the route-B review started
    its window at cycle 14's retrospective (07:10) and re-reviewed six hours of already-reviewed morning work.
    The boundary that is actually reliable is "the last time a retrospective was written", whoever it was labelled
    for. `retrospective-v2-*` is still excluded for `retro_archive`'s reason (comparison runs, not closures), and
    a re-run of the SAME slug must not use its own previous archive as its start.
    """
    best = None
    for f in glob.glob(os.path.join(PEER_DIR, "*retrospective*.md")):
        b = os.path.basename(f)
        if "retrospective-v2-" in b:
            continue
        if exclude_slug and b.endswith(f"-{exclude_slug}.md"):
            continue
        # `guard_cycle.stamp()`, NOT raw getmtime - codex, `archive/peer/2026-09-17-open31-window-codex.md` E4-4:
        # "a cosmetic rewrite can therefore make an old retrospective appear to be the newest boundary - the exact
        # class of problem `stamp()` was introduced to resist". The first draft of this function used getmtime and
        # walked straight back into it.
        mt = _stamp(f)
        if not mt or mt >= now:
            continue
        if best is None or mt > best[1]:
            best = (f, mt)
    return best


def dispatch_time(path):
    """When a retrospective was DISPATCHED = its archive's mtime minus the elapsed seconds peer.ps1 recorded.

    peer.ps1 writes the archive only after the answer returns, and stamps `- **outcome:** ANSWERED (362s)`. The
    file's mtime is therefore the END of the review, and a cycle whose window ran to that instant would swallow the
    5-10 minutes the reviewer itself spent. Subtracting the recorded elapsed gives the moment the cycle actually
    stopped producing work. If no elapsed figure is present, the mtime stands (conservative: a slightly wide window
    over-reports, which is visible, while a narrow one silently loses evidence - the defect this whole change fixes).
    """
    mt = os.path.getmtime(path)
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            head = f.read(4000)
    except OSError:
        return mt, "archive mtime (unreadable)"
    m = re.search(r"^\-\s*\*\*outcome:\*\*\s*\w+\s*\((\d+)s\)", head, re.M)
    if m:
        return mt - int(m.group(1)), f"{os.path.basename(path)} mtime - {m.group(1)}s (its dispatch)"
    return mt, f"{os.path.basename(path)} mtime (no elapsed recorded)"


def cycle_window(cycle, slug=None):
    """(start, end, basis) - the cycle's real boundary.

    === WHY THIS IS NOT THE PLAN DOCUMENT'S MTIME ANY MORE (decided 2026-09-16, OPEN-E) ===

    v2's proposal 4 replaced v1's 24-hour sliding audit with "start = mtime of docs/cycle<N>-plan.md", and the
    comparison measured what that cost (tools/bench/retro_v2_comparison.md section 5): **a plan document in this
    project is written and last edited AFTER the cycle's work has started**, so its mtime is a LAGGING boundary.
    Both of cycle 11's defining errors fell outside "cycle 11": `build_opdelete_v1.log` at 16:27 and the 26-wrapper
    `ensure_loaded` patch to `tools/gscript.py` at 17:38:29 - the latter missed by FIFTEEN SECONDS, because
    cycle11-plan.md was last saved at 17:38:44. v1 charged one cycle for three cycles' work; v2 charged it for a
    suffix of its own. Both are wrong, and the second is worse because it looks precise.

    The boundary this project actually records reliably is **the previous cycle's retrospective**: it is written
    once, at the moment the previous cycle was declared closed, and it is never edited to plan future work.

      start = mtime of archive/peer/*retrospective-cycle<N-1>.md
      end   = cycle N's own retrospective DISPATCH time if it has one, else now
      fallback: docs/cycle<N>-plan.md mtime, ONLY when no previous retrospective exists (cycles 1-6)

    Verified on cycle 11: start 2026-09-16 14:33:20 (cycle 10's retrospective), so build_opdelete_v1.log (16:27:59)
    and tools/gscript.py (17:38:29) are both inside, which is what the judgement session believed all along.
    """
    try:
        n = int(cycle)
    except (TypeError, ValueError):
        return None, None, "cycle is not a number - no window"

    now = time.time()
    prev = newest_retro_before(now, exclude_slug=slug)
    if prev:
        start = prev[1]
        sbasis = (f"archive/peer/{os.path.basename(prev[0])} stamp "
                  f"(the LAST retrospective written before this one; a plan mtime lags the work - see the docstring)")
    else:
        cur = os.path.join(ROOT, "docs", f"cycle{n}-plan.md")
        if not os.path.isfile(cur):
            return None, None, (f"no earlier retrospective and no docs/cycle{n}-plan.md exists - no window")
        start = os.path.getmtime(cur)
        sbasis = f"docs/cycle{n}-plan.md mtime (FALLBACK: no earlier retrospective is archived)"

    # END IS ALWAYS NOW - this review is being dispatched now, so the cycle stopped producing work now.
    # It used to be `dispatch_time(retro_archive(n))`, and that is OPEN 31's defect, measured: a SECOND review of
    # the same cycle number under a different slug clamped `end` to the FIRST one's dispatch. Three windows were
    # wrong that way today, the worst being `retrospective-cycle15-routeb` (dispatched 16:11), which was handed
    # 07:10:02 .. 13:32:51 and so never saw route B at all. `dispatch_time()` survives only for the note below,
    # and the `end <= start` rescue is gone because `now` cannot precede a strictly-earlier archive.
    # HONEST LABEL (codex E4-1, same archive): `now` is captured HERE, before audit_cycle.py, the task build and
    # peer.ps1's launch - it is when the WINDOW was computed, which is minutes before the review is dispatched.
    # Work done during those minutes falls in no window; that gap, and the overlap of two concurrent
    # retrospectives (E4-2/E4-3), need a recorded closure timestamp rather than a derived one - NOT taken here.
    end, ebasis = now, "now, at window computation (minutes before the dispatch itself; codex E4-1)"
    return start, end, f"start = {sbasis}; end = {ebasis}"


def fmt(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--slug", default=None, help="archive slug (default retrospective-cycle<N>)")
    ap.add_argument("--since-hours", type=float, default=None,
                    help="EXPLICIT OVERRIDE of the window start (and the fallback when no boundary exists). "
                         "Until 2026-09-17 it was applied ONLY when cycle_window() failed outright, so a run "
                         "that asked for it while a previous retrospective existed had it silently discarded.")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    start, end, basis = cycle_window(a.cycle, a.slug or f"retrospective-cycle{a.cycle}")
    if start is None:
        hrs = a.since_hours if a.since_hours else 20.0
        start, end = time.time() - hrs * 3600, time.time()
        basis += f"; fell back to --since-hours {hrs:g}"
    elif a.since_hours:
        # AN EXPLICIT OVERRIDE IS AN OVERRIDE (codex, `archive/peer/2026-09-17-open31b-stamp-codex.md` §3). The
        # cycle-16b run was invoked as `--cycle 16 --slug retrospective-cycle16b --since-hours 1.2`
        # (`tools/bench/retro_cycle16b.log:1`) and got 08:06:44 .. 08:07:42 anyway, missing the 08:04:05 build it
        # existed to judge - because the flag was only read on the no-boundary path. The reviewer of that very
        # cycle wrote the same finding into its own archive. Now the flag wins, and says so in the basis line.
        start = end - a.since_hours * 3600
        basis = (f"start = --since-hours {a.since_hours:g} BEFORE the end, an explicit override of "
                 f"[{basis}]; end = now, at window computation")
    win = f"{fmt(start)}  ..  {fmt(end)}   ({(end - start) / 60:.0f} min)\n    basis: {basis}"

    # ENCODING IS NOT COSMETIC HERE - this text becomes the peer's EVIDENCE (lint, 2026-09-16). `text=True` with no
    # `encoding=` decodes the child's stdout with the console code page (cp949 on this box), and audit_cycle writes
    # `…` and Korean; the audit block reached the reviewer as mojibake, e.g. `md5 2a78e17c449c<?>`. This is the same
    # defect that voided prior-art run 3 ($2.53, `tools/bench/priorart_scores.md`) - a review fed corrupted evidence
    # is a review that told you nothing, and nothing in the transcript says so. Force UTF-8 on both ends.
    audit = subprocess.run([sys.executable, os.path.join(HERE, "audit_cycle.py"),
                            "--from", "%.0f" % start, "--to", "%.0f" % end, "--cycle", str(a.cycle)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=300).stdout
    # BUILD LOGS ARE THE PRIMARY RECORD; the machinery's own logs are listed separately and labelled, because they
    # are evidence ABOUT the cycle and never the thing under test (tools/logclass.py has the four false positives
    # that taught this). They are still named, and only for one reason: they are where the `COST: $...` lines live,
    # and the output contract asks for a dollar figure wherever a log carries one.
    logs, machinery = [], []
    bench = os.path.join(HERE, "bench")
    for p in sorted(os.listdir(bench)):
        fp = os.path.join(bench, p)
        if not p.endswith(".log"):
            continue
        try:
            mt = os.path.getmtime(fp)
        except OSError:
            continue
        if start <= mt <= end:
            (logs if logclass.is_build_log(fp) else machinery).append((p, mt))

    devices = parse_devices(DECISIONS)
    dev_text = "\n".join(f"  - `{s}` (decided {d}): {one}" for s, d, one in devices) or "  (none on file)"

    task = (
        f"RETROSPECTIVE (v2) of cycle {a.cycle} (read-only; you may open any file in the project).\n\n"
        f"=== EVIDENCE WINDOW - this cycle is EXACTLY this interval, and nothing outside it is this cycle ===\n"
        f"    {win}\n"
        f"The compliance audit below was run over that window (--from/--to), and the build-log list is the logs\n"
        f"whose mtime falls inside it. Earlier work belongs to an earlier cycle: do not attribute its cost here,\n"
        f"and say so if the attached evidence contradicts the window.\n\n"
        f"{CONTRACT}\n"
        f"{FINDINGS_Q}\n"
        f"{DEVICE_Q}\n"
        f"Devices on file (docs/violation-decisions.md, machine-extracted):\n{dev_text}\n\n"
        f"=== END YOUR ANSWER WITH MACHINE-READABLE LINES ===\n"
        f"One line per structural fault you named - normally ONE, at most two - in exactly this form:\n"
        f"  VIOLATION: <slug> | loss_min=<number> | loss_usd=<number or ?> | evidence=<file:line>\n"
        f"or, if the cycle had no structural fault:\n"
        f"  VIOLATION: none\n"
        f"Slugs: {SLUGS}\n"
        f"Do not invent new slugs; map to the closest one and explain in the prose. `loss_min` is a whole number\n"
        f"of minutes. `loss_usd` is a number only when a log carries it, otherwise `?`. `evidence` is one\n"
        f"file:line that a reader can open.\n"
        # OPEN-C of tools/bench/retro_v2_comparison.md, decided 2026-09-16. All three v2 runs echoed the literal
        # template line `VIOLATION: <slug> | ...` and the line `VIOLATION: none` back into the answer while
        # explaining the contract. The tally survived it by luck - `<slug>` fails violations.py's `[a-z0-9-]+` and
        # `none` is dropped by name - but a format the parser only tolerates by accident is one line away from
        # being counted, so say it once, here, where the format is defined.
        f"WRITE A `VIOLATION:` LINE ONLY AS YOUR OWN FINAL VERDICT. Do not quote, restate, echo or illustrate this\n"
        f"format anywhere in your answer - not in the prose, not while explaining what you are about to do. Every\n"
        f"`VIOLATION:` line in your answer is read by a parser as a real occurrence.\n\n"
        f"=== COMPLIANCE AUDIT (tools/audit_cycle.py --from/--to, machine-generated) ===\n{audit}\n"
        f"=== BUILD LOGS INSIDE THE WINDOW ({len(logs)}; read them directly, they are the primary record) ===\n"
        + "\n".join(f"tools/bench/{n}  ({fmt(mt)})" for n, mt in logs)
        + f"\n\n=== REVIEW/AUDIT MACHINERY LOGS INSIDE THE WINDOW ({len(machinery)}) - NOT builds, and not part of\n"
          f"the cycle's build cost. Listed for ONE reason: they carry the `COST: $...` and wall-clock lines the\n"
          f"output contract asks you to quote. Never read a reviewer's quoted sentence as a build failure.\n"
        + "\n".join(f"tools/bench/{n}  ({fmt(mt)})" for n, mt in machinery)
        + "\n\nThe rules are in CLAUDE.md at the project root; this cycle's own plan is "
          f"docs/cycle{a.cycle}-plan.md and the hand-off document is STATUS.md; every hypothesis-level review of "
          "this cycle is in archive/peer/.")

    slug = a.slug or f"retrospective-cycle{a.cycle}"
    scratch = os.path.join(os.environ.get("TEMP", "."), f"retro_task_{slug}.txt")
    with open(scratch, "w", encoding="utf-8") as f:
        f.write(task)
    print(f"   window {fmt(start)} .. {fmt(end)} ({(end - start) / 60:.0f} min); {len(logs)} build logs, "
          f"{len(machinery)} machinery logs, {len(devices)} devices", flush=True)
    print(f"   task written to {scratch} ({len(task)} chars)", flush=True)
    if a.dry_run:
        print(task)
        return 0
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           # -TimeoutSec 600: peer.ps1's 180 s default is far too short for this question. A retrospective
           # attaches the audit, every build log of the cycle and CLAUDE.md, and the peer reads them; measured
           # siblings take 215-395 s, and cycle 8's attempt TIMED OUT at 180 s on 2026-09-15 with nothing
           # learned. -Kind fact because this prompt carries its own instruction set and has no claim to refute.
           # 2026-09-18: codex quota at 9 % (user) - the retrospective goes to the thin claude `outcome` role
           # (fable/medium, --safe-mode, reads the attached audit/logs). Codex stays one flag away.
           f"& '{os.path.join(HERE, 'peer.ps1')}' -Agent claude -Role outcome -Kind fact -TimeoutSec 600 "
           f"-Slug {slug} -Task (Get-Content -Raw '{scratch}')"]
    r = subprocess.run(cmd, cwd=ROOT, text=True, timeout=900)
    print(f"   peer.ps1 rc {r.returncode}; archived as archive/peer/<date>-{slug}.md", flush=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
