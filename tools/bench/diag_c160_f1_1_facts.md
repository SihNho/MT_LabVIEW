---
type: facts
status: current
date: 2026-10-10
card: 160-f1-1
---
# Which commit drops PB rows 2626|Terminal|array|0-3 from selftest_c134_1_dry (PD390(g)) - measured; nothing edited
## 1 Bisect (diag_c160_f1_1_bisect.py, every top-level tools/*.py served from the git revision in memory, recipe/data from disk)
| rev | PB | rows | log |  | rev | PB | rows | log |
|---|---|---|---|---|---|---|---|---|
| 421d6108 | PASS | 16 | bisect.log:14 |  | 36da0566 (Cycle 148) | PASS | 16 | :29 |
| 2deaaad7 | PASS | 16 | :18 |  | 771a39a1 (chat-T6) | PASS | 16 | :31 |
| b21b9026 (Cycle 152) | PASS | 16 | :20 |  | 653d1b61 (chat-T6 follow-up) | PASS | 16 | :33 |
| **18c241ec (Cycle 153)** | **FAIL** | 12 | :26 |  | 1449ae07 / 9dbd384b (T6 merge) | PASS | 16 | :35,:37 |
| 57e7de7d / 1370c454 | FAIL | 12 | :24,:22 |  | 676f874f (chat-T7) | FAIL | 12 | :39 |
| a9d0da22 (HEAD) | FAIL | 12 | :16 |  | | | | |
- Every FAIL: missing exactly 2626|Terminal|array|0..3, extra [] (log:16,22,24,26,39).
- Single-module swaps (diag_c160_f1_1_swap.log:3,5): b21b9026 + vigraph@18c241ec -> FAIL 12; 18c241ec + vigraph@b21b9026 -> PASS 16. vigraph alone decides.
## 2 First bad commit
- 18c241ec143fbff25f09d0205f5527049820dfea, Fri Oct 9 08:09:31 2026 +0900, "Cycle 153: session outputs (runner auto-commit)". Tool files changed vs b21b9026: vigraph.py, stagesim.py only.
- Decisive hunk: vigraph 13be0847 -> a7eb58c7 (card 153-b2-1, fp-70): new pos_keys (vigraph.py:847-862), computation_diff pairs sinks by position `PA, PB = pos_keys(A), pos_keys(B)` (:889) and a slot whose sources are equal on position keys becomes a `renames` entry, not a row (:896-913).
- Adopted by PD370(b) (docs/d1/ring-p4d.md:172-183): "one row per changed input slot ... s06's #2626: slot 4 was rename-only and gives no row; slots 1-3 ... 3 changed rows instead of 3 lost+new pairs"; "The stored pred files stay byte-unchanged" (converter in self-tests).
- Not chat-T6: 771a39a1 / 653d1b61 / 9dbd384b PASS (T6 moved stagekit's gates; this recipe's PB calls V.computation_diff_frame directly, stage_d1_ring_p3b2a.py:71). Not chat-T7: 676f874f FAILs only because its parent is 18c241ec (same vigraph a7eb58c7, log:40).
## 3 The four rows under the position PB (18c241ec / HEAD, bisect.json "pos_s1" / "pos_end" / "n2626" / "renames2626")
- S1 #2626 positions: 0 appended array (src), 1 element|0, 2 element|1, 3 element|2, 4 array|0. END: 1 array|0, 2 array|1, 3 array|2, 4 array|3.
- array|3 (END pos 4) <-> S1 array|0 (pos 4): same source 5058 x,y,z array out -> `renames` [{sink 2626|Terminal|array|0, sink_b array|3}], no row.
- END array|0..2 (pos 1-3) share the position of S1 element|0..2 -> reported as rows element|0/1/2 (before 5119 x-y / 30117 Value / 4580 Value, after []). So all four pred rows are old NAME keys of terminals the position PB merges (3) or drops as rename-only (1). New rk = 12 rows = pred minus the four.
## 4 Re-pin decision (brief step 3): NOT written
- First bad commit is 18c241ec (Cycle 153 runner commit carrying card 153-b2-1), not chat-T6 771a39a1/9dbd384b nor chat-T7 676f874f -> rule says OPEN. plan_ring_p3b2a_pred_c160.json not created.
- Fact for the decision: a pred re-pin alone would not PASS. L0 requires pred cdiff_rows == plan finalized end_cdiff_rows (stage_d1_ring_p3b2a.py:39), and PB's second half needs the 11 open (node, term) pairs incl. (2626,'array') (plan_ring_p3b2a.json:17-21); the position PB yields 10 pairs (no 2626 array).
## 5 T2a pin proposal (not applied)
- selftest_c134_1_dry.py:82 `...startswith("bb5ba064")...` (label "T2a fixed recipe md5 == bb5ba064") -> `startswith("0d1f0c15")` (label "== 0d1f0c15"); 0d1f0c15 = bb5ba064 + the 4 chat-E3 header lines (diag_c159_f1_2_facts.md:10).
## 6 Unchanged / clean
- md5 before == after the runs (bisect.log:12,41): stagekit 1441bb4c, stage_prerun 7605116f, stagesim a3261b56, stagexec c4a6e0b6, vigraph a7eb58c7. stagekit/stagesim/stagexec differ from c159's ac3a8f57/eb99c6ba/7a712ccb: edited by a parallel card, not by this one.
- recipe 0d1f0c15, selftest_c134_1_dry 10178208, plan_ring_p3b2a_pred 45eb0b67 unchanged. `git status --short tools/hooks` -> only material_marker.log (bgrun). No LabVIEW process. No temp dirs (bytes served in memory, no git archive extract). VI md5s not re-read (md5sum on claudeDev denied by permission); this card opened no VI.
- FALLTHROUGH check printed nothing (the dry exits before the child's finally); every SERVED line names the revision's md5s (bisect.log:15-40).
OPEN: 18c241ec (card 153-b2-1, PD370(b)) is the intended position PB but not the chat-T6/T7 commit the rule names - re-pin pred AND plan end_cdiff_rows/open_rows (2626 array -> none), or keep and convert?
OPEN (carried, diag_c159_f1_2_facts.md:30): T2 requires `unverified 0` (selftest_c134_1_dry.py:84) but PD387(e) counts the recipe's CEN2 UNVERIFIED-DRY line (stage_prerun.py:1074-1075).
