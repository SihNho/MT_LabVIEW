---
type: brief
status: current
date: 2026-10-07
---
# Brief 146-a1-1 — drain gate-fp fp-43..50 (guard_write stale-pin class + guard_peer fp-44/fp-46) — offline, ALONE

Purpose item (PD352(e), `docs/d1/ring-p4b.md:300-303`): ONE tooling card, run alone, edits ONLY `tools/hooks/guard_write.py`,
`tools/hooks/guard_peer.py` and their self-tests. The hook edits are authorised by the cycle-146 purpose. No other card is live.

## Measure (facts, from the queue `tools/bench/gate_fp_queue.jsonl`)
- fp-43/45/47/48/49/50: one class. `guard_write.py` `open_card_pins` (~line 58-84) reports `open card X pins <file> at md5 A; the file
  on disk is now B - stale copy` when the card that pins a file as an INPUT also lists it in `flags.write`. The pin is the pre-edit
  baseline of a file the card is authorised to edit; its own edit is not a stale copy. Read each queue row's `why` and reproduce the
  refusal on a scratch card + file pair before changing code.
- fp-44: `guard_peer` takes a Jev-ladder `new-problem` verdict on an OFFLINE json-reading helper whose scope header is `labview: none`
  as a failed prediction owing a hypothesis review (queue row for the log and card).
- fp-46: `guard_peer` counts a prediction log whose LAST line is the report-only X10 rc=1 line (`gate fatal=False by design`, log
  `tools/bench/prep_c145_2_pred.log`) as a failing run.
Reproduce fp-44 and fp-46 from the cited logs before editing; if one is not reproducible from the cited log with the current code, report
that and do not edit for it (drain with `gate_fp.py close --reason`).

## Do
1. Fix `guard_write.py` so a card's own authorised edit is NOT reported stale: a file the pinning card lists in its `flags.write`
   (glob match) is exempt from the stale-pin message for THAT card only; a pin on a file the card does NOT list in `flags.write` still
   refuses (keep that case, add a negative test). Smallest edit.
2. Fix `guard_peer.py` for fp-44 and fp-46 narrowly: (fp-46) a log whose failing line is a report-only line marked non-fatal by its
   own text does not arm the gate; (fp-44) a `labview: none`-header script with no machine hypothesis does not owe a hypothesis review
   on a ladder `new-problem`. Both keyed on the evidence the log or header carries, never on a filename list.
3. Add test cases for every fix and its negative twin to the existing self-tests (`tools/bench/selftest_c_e3.py` for guard_write;
   the `selftest_guard_peer_*.py` family for guard_peer, e.g. `selftest_guard_peer_scrreq_c144.py`). Existing cases must not change.
4. Run, before AND after, every old hook self-test: `selftest_c_e3.py`, `selftest_guard_peer_budget.py`, `_failre.py`, `_jev.py`,
   `_ladder.py`, `_samerow.py`, `_scan_tmp.py`, `_77_measure.py`, `_scrreq_c144.py`. Report pass/fail counts per file; all old cases stay green.
5. Drain: for each of fp-43..50 run `py tools/gate_fp.py drain --id <fp-n> --fixed <path:line> --selftest <name>` (or `close --reason`
   where Do-step 2's reproduction failed). `py tools/gate_fp.py list --open` must then show none of them.
6. md5 before/after of every file the card touches; every other file under `tools/` unchanged.

## Never
LabVIEW, camera, motor; editing any file other than the two hooks, the self-tests and the queue; editing any plan, recipe, pred or
stage tool; loosening a refusal that is not one of the three named classes; `CYCLE_GUARD_OFF` or any env bypass.

## Return
`result/1`; md5 old -> new of the two hooks; the repro line per fp id; the self-test counts before and after.
