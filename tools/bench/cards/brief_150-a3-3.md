---
card: 150-a3-3
status: current
date: 2026-10-08
---
# Brief 150-a3-3 - PARSER DEVICE (docs/d1/ring-p4c.md PD365(f), PD364(e)) + the four gate_fp log entries; offline, ALONE

No LabVIEW, camera or motor; no other card is live (this edits gate tools). **`tools/hooks/**` is NEVER edited** (user 2026-10-08; `assign_config.json` `never_in_runner_globs`).

## Problem (read, do not re-derive)
Four tools find the disposition heading of an archived review by first-occurrence substring: `tools/violations.py:177` (`body.split("## What was done with it")[0]`), `tools/cycle_runner.py:995-1040` (`retro_undisposed`, constant `RETRO_DISPOSITION_H`),
`tools/audit_cycle.py` A4 (:619-620 `body.find(...)`) and :326 (A9). A retrospective whose ANSWER quotes the heading inline (as `archive/peer/2026-10-08-retrospective-cycle149.md` does) is cut at the quote:
the real disposition section is missed (counted undisposed / the answer truncated). `tools/hooks/guard_peer.py:849-851` has the same first-occurrence misread but is a hook: LOG it, do not edit.

## Steps
1. **Helper** in a NEW non-hook module `tools/dispo.py` (stdlib only, no LabVIEW import): `find_disposition(body) -> (answer, disposition_text|None)` using the LAST LINE-ANCHORED heading (`^## What was done with it\s*$`, multiline, at column 0);
   an inline quote is not a heading. Also `disposition_len(body)` with the `(Claude fills in)` placeholder stripped, as `cycle_runner.py` does now. Header per the repo rule (`# labview: none / # hardware: none`).
2. **Wire the sites**: `violations.py:177`, `cycle_runner.py` `retro_undisposed` (:995-1040), `audit_cycle.py` A4 (:612-625). Look at `audit_cycle.py:326` (A9): wire it too ONLY if it has the same first-occurrence defect; say which.
   Behaviour on a file with ONE heading at column 0 is identical to now (byte-identical outputs on the archive's existing files except those that quote the heading inline). No other change to those files.
3. **Self-test** `tools/bench/selftest_c150_a3_3.py` on COPIES of retro-149 (and a copy of retro-148, and a synthetic body with an inline quote + a real heading, one with no heading, one with only the placeholder): run it against the OLD code first (copy the old function bodies, or `git show HEAD:tools/<file>`)
   and show it FAILS at the three sites, then against the new code and show it PASSES. Quote both counts.
4. **Regression**: `py tools/violations.py` lists retrospectives 148 and 149 with 0 awaiting; the old self-tests of the three files (grep `tools/bench/selftest_*` for `violations`, `retro_undisposed`, `audit_cycle`) give rc 0 or the same counts as before (record the before counts first).
5. **gate_fp log** (`py tools/gate_fp.py log --gate G --cmd C --why W --card 150-a3-3 [--line L]`; card chat reads them): four entries, ids quoted:
   (a) `guard_peer` :849-851 first-occurrence misread; (b) PD361(c)(1) `guard_assign` provenance check (no runner card may make it now); (c) retrospective-cycle149:374 - the launch gate refused `gate_fp.py log --cmd` because a recipe path sat inside the quoted `--cmd` text
   (put the text in `--why` or shorten `--cmd` if the refusal repeats; never an env bypass); (d) `computation_diff` keys rows by terminal NAME (`tools/vigraph.py:847-871`; PD366(b)). Facts only in `--why`.
6. **Invariants** md5 before = after: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847, stagesim 748bbf30, s06 569ffbf5, s05 3f9ac26b, bed 39511877, s07 adopted b3f86b32, `tools/hooks/**` tree (list md5 before/after).

## Return conditions
A hook edit would be needed; a site whose old behaviour on non-quoting files cannot be preserved; the old self-tests changing counts; a gate refusing twice at the same place (log it with gate_fp first).

## Report `tools/bench/diag_c150_a3_3_facts.md` (<= 35 lines)
Helper name + 3 sites (file:line before/after), self-test old vs new counts, violations.py listing, old self-test counts before/after, gate_fp ids, files changed (md5 before/after), invariants, `OPEN:`. Facts only.
