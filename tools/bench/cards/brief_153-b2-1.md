---
card: 153-b2-1
status: current
date: 2026-10-09
---
# Brief 153-b2-1 - drain gate-fp fp-70 and fp-72 (docs/d1/ring-p4d.md PD370(d)); offline, two tool edits

Read `docs/d1/ring-p4d.md` PD370 (d) and (e). Gate false positives are in `tools/bench/gate_fp_queue.jsonl` (ids fp-70, fp-72); drain with `tools/gate_fp.py` (read its usage; find the verb that closes an entry with a discharge record, as used for fp-61 in cycle 151).
fp-62..69 and fp-71 are NOT yours (hooks; the chat drains them). Do not touch `tools/hooks/**`.

## fp-70 - `tools/vigraph.py` `computation_diff` (line 847; `computation_diff_frame` line 840)
It keys rows by terminal NAME, so a renamed old terminal reads as lost+new. Key rows by POSITION (owner, index, class), the same way chat-T6 keys D/TD/PB in `tools/stagekit.py` (read how, `docs/d1/INDEX.md:264`, PD366(b); copy the key shape, do not edit stagekit).
Rename-only rows must stop reading as lost+new; a real lost or new terminal still reads as lost / new.
Re-score the STORED end reads of s06..s09 and S1-vs-s09 (the existing `tools/bench/graph_*` jsons the earlier stages used; find each pair from `tools/bench/graph_diff_*` / `graph_computation_diff_*` and the s06..s09 graph files, `docs/d1/ring-p4*.md`): every result stays the SAME as the stored one except rows that were rename-only. Quote a table: pair, old rows (lost/new/changed), new rows, the rename-only rows removed. A result that changes for any other reason is a STOP with the facts (`OPEN:`), not a fix.
Add a self-test (`tools/bench/selftest_c153_compdiff_poskey.py`, <= 120 lines): a rename-only fixture -> 0 rows; a real removal -> still a row; plus the old `tools/bench/selftest_chatl1_selftest_vigraph_frame_80`-style vigraph self-tests still pass (run before and after; quote counts).

## fp-72 - `tools/card_clock.py` line 19 `CITE`
`CITE = re.compile(r"budget|minute|\bmin\b|time.?out|deadline", re.I)` matches the word 'min' inside a quoted LabVIEW terminal name ('min slot') in a result's `blocked_by`. A quoted terminal name is not a budget citation: make CITE ignore text inside quotes (single, double or backtick) before matching, nothing else. Keep behaviour for every other input; run `tools/bench/selftest_card_clock.py` before and after and add the 'min slot' case to a NEW self-test (`tools/bench/selftest_c153_cardclock_quoted.py`), do not edit the old one.
Then `py tools/protocol.py validate tools/bench/cards/result_152-a2-2.json` must validate; quote its output.

## Drain
Close fp-70 and fp-72 in the queue with the gate_fp verb, citing the new md5s and the self-test logs; quote the drain lines.

## Invariants (md5 before/after; unchanged)
stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, s09 VI eb1d0f31, graph 22f967b5. `stagesim.py` is being edited by ANOTHER card at the same time: do not read it as an invariant and do not touch it.
Changed files: `tools/vigraph.py` (13be0847 -> new), `tools/card_clock.py` (-> new). No recipe gate-criterion change; no hook edit; no LabVIEW (labview none); no motor or camera.

## Return (<= 30 lines)
New md5s; the re-score table; the two drain lines; self-test counts old/new; result_152-a2-2 validate output. `OPEN:` for anything needing judgement. Failure budget 2.
