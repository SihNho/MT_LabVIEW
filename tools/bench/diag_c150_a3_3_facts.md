---
type: facts
status: current
date: 2026-10-08
card: 150-a3-3
---
# Card 150-a3-3 facts: tools/dispo.py wired at 4 sites; self-test old 9/13 vs new 19/0; archive census FAILS on 10 two-heading files
## Helper and sites (line numbers unchanged by the edits)
- `tools/dispo.py` 27f21667: `heading_index` / `find_disposition` / `disposition_len`, LAST `^## What was done with it[ \t\r]*$` (re.M).
- `tools/violations.py:177` answer = `dispo.find_disposition(body)[0]`; import on :43 (was a blank line). md5 7482e9b7 -> 0cae42f3.
- `tools/cycle_runner.py:1017-1021` retro_undisposed -> `dispo.disposition_len(body)` (None or < 80 = undisposed). 72ab9def -> 508854ca.
- `tools/audit_cycle.py:619` A4 and `:326` A9 -> `dispo.heading_index(body)`; import on :115. c57668a5 -> 3bd22d7b.
- A9 :326 HAD the same defect (`body.find`): an answer that quotes the heading before 'ACCEPTED ... not built' became a candidate (old A9-1 n=1).
## Self-test `tools/bench/selftest_c150_a3_3.log` (OLD = byte snapshots `prep_c150_a3_3_old_*.txt`, md5 == card inputs)
- OLD 9 pass / 13 fail: V1-V4, R1-R4, A4-1..4, A9-1 fail; NEW 19 pass / 0 fail (`SITE-FAILS` lines).
- RESULT FAIL 2/1: gate 'archive outputs ... every change is on a file that quotes the heading inline' FAILED.
- Census: 1119 archive/peer files carry the string; 1071 same cut; 38 differ and quote inline; 10 differ with TWO column-0 headings.
- Two-heading pattern A (8 files: cycle7, d1-s1-diagram-count, d1-s1-stale-in-memory-copy, d1-s3-stale-traverse-index,
  d1-s3b-uid-reuse-after-delete, moveinto-p1-execstate0, d0-bandpass x2): 1st heading = placeholder, 2nd = real text
  (e.g. `archive/peer/2026-09-17-d1-s1-diagram-count.md:64,68`). OLD A4 called them blank; NEW calls them annotated.
- Pattern B (2 files): real text under the 1st heading, placeholder left under the last
  (`2026-09-16-load-vs-editmode-23c-r2.md:52,87`, `2026-09-18-retrospective-cycle17.md:12,281`). NEW calls them blank (A4) /
  undisposed (R, cycle17); OLD called them annotated. V: cycle17 now counts device-failed (OLD counted nothing).
- Output changes on inline-quoting files (intended): V cycle49, 148, 149; R cycle16, 16b, 26; A4 8 files. A4 blank 279 -> 282 of 1119 (+8 inline, -7 pattern A, +2 pattern B). A9 old == new.
## Regression (`prep_c150_a3_3_before.log` / `_after.log`)
- `py tools/violations.py`: 0 awaiting before and after; retrospective-cycle148 listed under 1 slug, cycle149 under 2 (after);
  totals device-failed 59 -> 61, repeated-failure-class 41 -> 42, inference-over-measurement 31 -> 32, unreported-fact 8 -> 9.
- Old self-tests, before = after: selftest_cycle_runner_retro 9/0 rc 0; selftest_audit_a9_witness 10/0 rc 0;
  selftest_c116a_landed 14/4 rc 1 (pre-existing, first_fail 'S2 cited by tools/x.py -> landed'); selftest_stamp_window 15/0 rc 0.
  selftest_c108e_tools.py not run (its header is `labview: read`).
## gate_fp log (tools/bench/gate_fp_queue.jsonl)
- fp-67 guard_peer :849-851 first-occurrence misread; fp-68 guard_assign PD361(c)(1) provenance; fp-69 guard_bash quoted --cmd
  (retrospective-cycle149:374); fp-70 checker:stagekit:computation_diff name keys (vigraph.py:847-871, PD366(b)).
## Invariants
- prep after 14/0: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847,
  stagesim 748bbf30, s06 569ffbf5, s05 3f9ac26b, bed 39511877, s07 b3f86b32, card inputs. tools/hooks: 10 .py + 13 .pyc md5 equal;
  tree md5 35bfcf87 -> 170023fc only because tools/hooks/material_marker.log (written by the hooks at each bgrun) changed. No LabVIEW launched.
OPEN: two-heading files - keep LAST heading (fixes 8, breaks 2: 23c-r2, cycle17) or choose another rule (e.g. last non-placeholder)?
