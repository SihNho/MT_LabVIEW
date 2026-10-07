---
card: 144-3
date: 2026-10-07
---
# Card 144-3 facts: gate false positives fp-34 and fp-41

## fp-41: DRAINED
- `tools/bench/selftest_fn_f2.py` was already rewritten so it no longer imports stagekit (`selftest_fn_f2.py:8-14`).
  Before the edit, `stage_prerun.vi_modifying_calls` already returned `[]` (`tools/bench/diag_c144_3_check.log`, F41a/F41b).
- Added a byte pin anyway, as the card asked: `tools/stage_prerun.py:3133`
  `VI_MOD_EXEMPT_PATHS["tools/bench/selftest_fn_f2.py"] = c744f767...a7ff508` (sha256 without the scope header).
  Re-check: `tools/bench/diag_c144_3_check_r2.log`, 4 pass / 0 fail. The pin matches the current bytes, and
  `launched_vi_modifying(<fp-41 cmd>) == []`.
- `py tools/gate_fp.py drain --id fp-41 --fixed tools/stage_prerun.py:3133 --selftest diag_c144_3_check`
  printed `DRAINED fp-41`.

## fp-34: NOT DRAINED (the fix needs tools/hooks/**)
- `tools/hooks/guard_peer.py:176` calls `protocol.run_verdict`, which counts any `rc != 0` as failed
  (`tools/protocol.py:426`). The carve-outs at `guard_peer.py:180` (rc in 0,1) and `:186` (rc in 0,1,2) do not
  cover rc 3. So `prep_c140_2_scrreq_r3.log` (`SCRATCH-REQUIRED ...`, `BGRUN END rc=3`) still reads as failed
  (diag F34a, first_fail `BGRUN END rc=3`).
- rc 3 is the documented decision code of `stage_prerun.py --scratch-required`
  (`tools/stage_prerun.py:2670`, `:4686`, `:4946`). Changing it in stage_prerun would change the CLI contract,
  so it was not changed.
- The exact edit is to insert this in `tools/hooks/guard_peer.py` `log_failure`, after line 188 and before
  `return bool(v["failed"]) ...` at line 189:

```python
        # fp-34 (card 144-3): `stage_prerun.py --scratch-required` exits 3 with a SCRATCH-REQUIRED decision line -
        # a decision, not a failed prediction (tools/stage_prerun.py:4686, :4946)
        if v["failed"] and not v.get("timeout") and v.get("rc") == 3 and not v.get("results") and re.search(
                r"stage_prerun\.py\s+--scratch-required\b", cmd or "") and re.search(r"^SCRATCH-REQUIRED \| ", seg, re.M):
            return False, None
```

## New entry
- fp-43 (guard_write): the edit check at `tools/hooks/guard_write.py:84` reports card 144-3 as "works on a stale copy"
  when 144-3 makes its own authorised edit to `tools/stage_prerun.py`. The card pins that file at `task_144-3.json:8`
  and lists it under `flags.write` at `:19`. Logged; status open.
