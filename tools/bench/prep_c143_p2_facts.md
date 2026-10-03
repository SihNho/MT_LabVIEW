---
type: facts
status: current
date: 2026-10-03
---
# Card 143-P2 facts — port of 143-1's three s02v18 changes into the s03v18 pair (offline)

Source diff: `git diff HEAD` of the s02v18 pair (HEAD 27157531 / 44ba6b23 blobs -> working 4af581f4 / 7d80df4d).

## Applied (nothing else changed)
| change | s02v18 (source) | s03v18 (now) |
|---|---|---|
| save_for_resume before report_stop (PD329(b)) | `stage_d1_ring_p4_s02v18.py:47-50` | `stage_d1_ring_p4_s03v18.py:47-50` (call :48) |
| MEM_STOP_MB = SX.X10_FAIL_MB (PD328(a)) | `_scratch.py:21`, gate `:84`, label `:86` | `stage_d1_ring_p4_s03v18_scratch.py:22`, gate `:85`, label `:87` |
| work_name D1_ring_p4s0N_<ts>.vi (PD329(a)) + `import time` | `_scratch.py:73`, `:16` | `stage_d1_ring_p4_s03v18_scratch.py:74` (`D1_ring_p4s03_<ts>.vi`), `:13` |
| docstrings state the port | `_scratch.py:4,7,10,12-14` | recipe `:7`; scratch `:3-4,8,11,13-15` |

Log/out/sum names and card id in the scratch sum JSON were left as 143-P1 wrote them (brief: nothing else changes).
md5: recipe 345b2c8b -> d420f951; scratch 00378892 -> 573b8537; plan 9d5049d8 unchanged.

## Release of the 143-P1 review
`archive/peer/2026-10-03-priorart-c143-p1-p4s03v18.md` `## What was done with it`: FIXED lines with the VERDICT slugs
`already-failed` (scratch :22), `helper-exists` (recipe :48), `contradicted` (scratch :74 + docstrings).

## Dry / prerun (provisional plan; outcome == 143-P1's)
- `prep_c143_p2_dry.log`: rc 1, E1 BASE unbound [-21,-19,-16,-15,-12,-11] (expected on a provisional base); new FACT
  "RESUME none: stopped in op None" shows the ported save_for_resume path executing.
- `prep_c143_p2_prerun.log`: 13/3 (X1 dry stop, X5 cascade, X10 UNMEASURED provisional) — same as `prep_c143_p1_prerun.log`.
- `prep_c143_p2_scr_dry.log`: rc 1, same E1 stop; prints `MEM_STOP_MB 680.0; X10 from the md5-pinned pred 676.9`.
- `prep_c143_p2_scr_prerun.log`: 13/3 same; X9 work = `claudeDev\D1_ring_p4s03_<ts>.vi` (work_name took effect).

## Prior-art review
`archive/peer/2026-10-03-priorart-c143-p2-p4s03v18.md` — `novel` (log `prior_art_c143_p2_p4s03.log`, rc 0, 89 s); NOVEL RECORDs
written for both recipes. Non-blocking note: pred Error List 54 rests on s02's PREDICTED 51, s02 scratch measured 53
(`result_143-1.json`); pred itself says re-derive at rebase (`plan_ring_p4_s03v18_pred.json:109-111`).

## Gate refusal (not logged as a false positive)
A `diff <(git show ...) <recipe>` command naming the s03v18 recipe was refused by the stop_record launch gate (then still armed).
The command used process substitution, which the gate classes as an executor (`tools/stop_record.py:136`), so it is not shown
FALSE; the comparison was done with the Read tool and `git diff HEAD` of the s02v18 pair instead.
