---
card: 144-a2-3
date: 2026-10-07
---
# Card 144-a2-3 facts: fp-34 guard_peer carve-out, stop_record replay

## fp-34: DRAINED
- Edit: `tools/hooks/guard_peer.py:189-193` in `log_failure`, after the chat-S5 rc 0/1/2 carve-out and before
  `return bool(v["failed"]) ...` (now :194). Condition (:191-192): `v["failed"] and not v.get("timeout") and
  v.get("rc") == 3 and not v.get("results")` and the BGRUN command matches `stage_prerun\.py\s+--scratch-required\b`
  and the segment has a line starting `SCRATCH-REQUIRED | ` -> `return False, None`. Nothing else in the file changed.
- Self-test `tools/bench/selftest_guard_peer_scrreq_c144.py` -> `tools/bench/selftest_guard_peer_scrreq_c144.log`:
  12 pass / 0 fail. Real log `prep_c140_2_scrreq_r3.log` -> (False, None); rc 3 without the line, rc 3 of a recipe /
  `--rebase` / plain stage_prerun -> failed `BGRUN END rc=3`; rc 1 / rc 2 -> failed `BGRUN END rc=1|2` (unchanged);
  rc 3 + failing RESULT -> failed; TIMEOUT -> failed.
- `py tools/gate_fp.py drain --id fp-34 --fixed tools/hooks/guard_peer.py:191 --selftest selftest_guard_peer_scrreq_c144`
  printed `DRAINED fp-34 (tools/hooks/guard_peer.py:191, selftest_guard_peer_scrreq_c144)`.

## stop_record replay: neither command is refused today; no fix needed
- `tools/bench/diag_c144_a2_3_stoprec.py` -> `tools/bench/diag_c144_a2_3_stoprec.log`: 20 pass / 0 fail. Pure replay of
  `guard_bash.stop_gate` (save_records and note patched to no-ops; `tools/bench/stop_records.json` unchanged in git).
- `material_marker.log:3332` (`git add <peer review> <brief> ...`): stop_gate 0. Rule: `git add`/`commit` are in
  `GIT_READONLY` (`tools/stop_record.py:237`, chat-E3 fp-38) -> class readonly, which DECISION_TABLE allows in every state
  (`tools/stop_record.py:207-208`, `:733`). Reconstructed with the p4_s03v18 recipe paths: also 0, tokens readonly.
- `material_marker.log:3333` (`git show HEAD:<recipe> | md5sum; ...`): stop_gate 0; `git show` in GIT_READONLY,
  `md5sum` in READONLY_PROGRAMS (`tools/stop_record.py:214`). Both logged lines were refused on 2026-10-03, before
  chat-E3 added `add`/`commit`; the logged commands are truncated at ~200 chars, so both the logged text and a
  reconstructed full form were replayed.
- Recipe launch `py tools/bgrun.py ... -- py -u tools/recipes/stage_d1_ring_p4_s04v18_scratch.py`: recipe token classed
  `build` (unchanged); stop_gate 0 because no refusing record exists for that path today. Control: 7 recorded recipe
  paths (of 123 records) are still refused as a bgrun launch (e.g. `tools/recipes/stage_d1_s2.py`, undisposed;
  `build_d1_m3a2.py`, sha mismatch), and `git add X && md5sum X` of each is allowed.

## New entry
- fp-45 (guard_write): the Write-check at `tools/hooks/guard_write.py:84` reported this card's own authorised edit of
  `tools/hooks/guard_peer.py` as "works on a stale copy" (same class as fp-43). Logged, open.
