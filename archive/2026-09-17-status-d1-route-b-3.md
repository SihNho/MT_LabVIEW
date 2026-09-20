---
type: archive
status: history
date: 2026-09-17
tags: [status, narrative, cycle15, route-b, open31, open38, open39]
---

# STATUS narrative relocated 2026-09-17 ~18:1x — material session "route B (3) — save it"

Rule 4: nothing is deleted, only moved. STATUS.md keeps one line per item and a pointer here.

## 1. The lock block, verbatim as it stood at the end of the session

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 16:4x-18:2x material/cycle15-route-B-3: RELEASED. ORIGINAL md5 2a78e17c449cacdaf5da389818526859
# before AND after every run. Runs, all bgrun, all terminated:
#   selftest_stamp_window.log        (3 runs; final 15 pass / 0 fail, rc=0, 23 s)
#   peer_open31_window.log           (codex ANSWERED 371 s; opus arm killed by the 14-min deadline, TIMEOUT)
#   priorart_opgeterrors.log         (rc=0 669 s; codex ANSWERED 216 s, opus ANSWERED 452 s)
#   peer_open31b_stamp.log           (rc=0 916 s; codex ANSWERED 224 s, opus ANSWERED 684 s)
#   priorart_routeb_run3.log         (rc=0 952 s; codex ANSWERED 332 s, opus ANSWERED 619 s)
#   bench_prep_run3.log              (rc=0 64 s; handles 34,230 -> restart -> 33,908)
#   diag_sr_transport.log            (rc=0 200 s; 10 pass / 0 fail, READ-ONLY)
#   build_d1_routeb_v0_run3.log      (see OPEN 38)
# One scratch class per run, created and deleted in the same run; claudeDev holds no leftover.
# No GUI, no hardware. Two builds NOT started because their own prior-art reviews stopped them (OPEN 39, 38).
```

## 2. OPEN 31 — CLOSED. The three wrong retrospective windows, and what actually caused them

OPEN 31 said the cause was `guard_cycle.stamp()` = `min(ctime, mtime)`, because "RE-ARCHIVING an existing slug
keeps the OLD ctime and the gate never sees the new review". **That is not what happened**, and the self-test
that was written to prove it disproved it instead (`tools/bench/selftest_stamp_window.py`, log
`tools/bench/selftest_stamp_window.log`, final run 15 pass / 0 fail).

**The measured cause** is `tools/retrospective.py`'s `cycle_window()`: `end = dispatch_time(retro_archive(n))`,
and `retro_archive(n)` matched only basenames ending `retrospective-cycle<n>.md`. A SECOND retrospective of the
same cycle number filed under a different slug therefore took its `end` from the FIRST one's dispatch. The three
archives' own EVIDENCE WINDOW basis lines are its fingerprint:

| review | dispatched | window it was handed | newest build log it should have seen |
|---|---|---|---|
| `retrospective-cycle15-d1-build3` | 10:02:15 | 07:10:02 .. 08:04:04 | `diag_d1_full_route.log` @ 09:59:07 |
| `retrospective-cycle16b` | 08:11:43 | 08:06:44 .. 08:07:42 (1 min) | `build_opstopfromnode_v0.log` @ 08:04:50 |
| `retrospective-cycle15-routeb` | 16:11:54 | 07:10:02 .. 13:32:51 | `build_d1_routeb_v0.log` @ 15:58:11 |

**Three changes, all measured, all reviewed:**

1. `cycle_window()`: `end` is now `now` (labelled honestly as "now, at window computation", because codex
   showed it is captured minutes before the dispatch); `start` is `newest_retro_before()` — the newest
   retrospective archived before now, of ANY cycle, excluding this run's own slug, dated with
   `guard_cycle.stamp()` rather than raw `getmtime`.
2. `--since-hours` is now an EXPLICIT OVERRIDE. It used to be read only on the no-boundary path, so the
   cycle-16b run, which passed `--since-hours 1.2` (`tools/bench/retro_cycle16b.log:1`), had it silently
   discarded. The reviewer of that very cycle wrote the same finding into its own archive and nobody read it.
3. `guard_cycle.stamp()` prefers the archive's own `- **date:**` frontmatter, which `tools/peer.ps1` now writes
   as `yyyy-MM-dd HH:mm:ss`; `_fm_date` parses only the text above `## Question` and refuses on more than one
   match; and the result is CLAMPED to the file's mtime so it can never be inflated.

**Self-test, 15 pass / 0 fail**, including the mechanism measurements that settled the argument:
* `T1` NTFS tunneling is real *within* the cache (delete + rewrite after 2 s keeps the old ctime).
* `T1b` after 18 s ABSENT it does not — and the first draft of this test slept BEFORE the delete, so its
  "failure" was the probe's, not the filesystem's (codex found it; MS KB 172190 creates the tunnel entry at
  removal).
* `T1d` the mechanism that actually matters: `Set-Content` over an existing path OVERWRITES IN PLACE and leaves
  creation time untouched, so `min(ctime, mtime)` can be stale with no tunneling at all. This is the only
  surviving evidence for the stamp change.
* `T2a/T2b/T2d/T2e` stamp never later than mtime; exact when the frontmatter is timed; a 2030 date is clamped;
  a `- **date:**` line below `## Question` is ignored.
* `T5` all three windows above are now covered.

**OPEN, handed to judgement** (`archive/peer/2026-09-17-open31b-stamp-opus.md`): that arm measured that the
stamp change has **zero effect on 339 of 340 archives** (only four carry a frontmatter TIME, all written today)
and that its only observable effect is to lower three stamps — the newest, gate-relevant ones. Its position is
that a change whose intended effect is unobservable and whose only observable effect is a side effect should be
reverted. The codex arm's position is that it is safe once clamped. Both are archived; a material session may
not decide a revert. Also still open, from the first round: E4-2 (work done while a reviewer runs falls in no
window) and E4-3 (two concurrent retrospectives double-count) need a RECORDED closure timestamp per review.

## 3. OPEN 39 — `OpGetErrors_v0` NOT BUILT. Stopped by its own prior-art review

The brief authorised the third attempt at `VI.Get Errors` 452 and required a `-Dual` prior-art review FIRST.
Both arms independently stopped it: codex `refuted-already` + `already-failed`; opus `settled-already`,
`refuted-already`, 5 × `contradicted`, `helper-exists`, `already-measured`. The citation, opened and found to
cover the case exactly, is `docs/d1-build-plan.md:859-860` — a judgement decision taken THE SAME DAY:
*"No diagnostic, framework, or review cycle before F1/F2 — the outcome reviewer's own ordering, adopted: third
op → PHASE "full" → save → N1 → F1 (5 min) → F2."* `OpGetErrors_v0` is a diagnostic and F1/F2 have never run,
so the "refute the citation" override was not available. Reinforced by
`archive/peer/2026-09-15-outcome-review-20260915.md:146,151` and by STATUS OPEN 32.

Two corrections the review made, which stand regardless and are written into `docs/d1-route-b-plan.md` §10:
* **§10b.1 is CONFIRMED** — `tools/gscript.py:2094-2123` shows `build_invoke()` swallowing the creator's error
  while `build_property()` raises at `:2156-2158`. So both recorded failures (2026-09-09, 2026-09-14) are
  uninterpretable, and `OpBuildInvoke_v1` is the right instrument if this is ever authorised.
* **§10c.2 is CONTRADICTED** — I wrote "no donor is known to exist"; `docs/toolkit-capabilities.md:187-189` and
  the NI thread's snippet say a LabVIEW snippet is a PNG carrying diagram code, so the donor is
  **manufacturable**, not merely findable.
Nobody disputes the reader's VALUE — the cycle-9 retrospective still calls it the primary missing tool. The
dispute is ordering and authority.

## 4. OPEN 38 — route B run 3: decision (1) refuted before it ran, decision (2) measured

See `docs/d1-route-b-plan.md` §11 and §11a for the full numbers; they are not repeated here. The short form:
the two `LeftShiftRegister` rows are not a transport problem with a queue answer — the sink AUTO-INDEXES
(`index_mode 1`), the registers are READ-WRITE and the queue carried only the read side, and the queue's element
type had no named source to come from (on the machine, the right-inside wire's source is a `LoopTunnel`, not a
node at all). `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:126-129` had already dispatched, attacked
and abandoned "queues standing in for shift registers". `SR_QUEUE_AUTHORISED = False` and
`TEMP_SINK_AUTHORISED = False` in `tools/recipes/build_d1_routeb_v0.py`.

## 5. A rule broken, recorded rather than hidden

CLAUDE.md "NEVER patch a file with a `py - <<'EOF'` heredoc" was broken once, at 17:28, to rename two variables
in `tools/recipes/build_d1_routeb_v0.py` (`enq[0]`/`deq[0]` → `enq_uid`/`deq_uid`). The patch landed and
compiled, and was verified by grep + `py_compile` immediately afterwards, but the rule exists because three such
patches died silently in one session on 2026-09-09. It should have been an Edit call. Reported here so the
retrospective counts it.
