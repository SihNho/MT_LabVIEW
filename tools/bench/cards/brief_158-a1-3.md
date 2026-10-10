# Brief 158-a1-3 (assignment 158-1): prior-art disposition + dry + prerun of plan_ring_p5s02a on the new stagexec bytes, offline

Read first: `CLAUDE.md`, `docs/script-writing.md`, `docs/d1/ring-p5.md` item 384 (b)(c), `tools/bench/diag_c158_a1_2_facts.md`
(card 158-a1-2 changed stagexec to df82d75e: run-closing checkpoints), `tools/bench/diag_c158_a1_1_facts.md` (part (a), the wire-0
inner-face act, is NOT built: no `Nodes[]` row for a loop inner face; do not touch it), `tools/bench/diag_c157_a1_2_facts.md`
(the commands and launch-gate text from the previous bytes). No LabVIEW, no hook edit, no recipe / plan / pred / licence / tool edit.
Pins: stagexec df82d75e, stagekit 0d8f6d25, stagesim eb99c6ba, addrcheck 207beb0d, stage_prerun 9decb20f. A later card may change
stagexec again (part (a)); this card's records are for the CURRENT bytes only, say so in the facts.

## Part 1 - disposition of the c156-a1-1 prior-art review
`archive/peer/2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md` ends with an EMPTY `## What was done with it`
("(Claude fills in)"). It blocks the next prior-art dispatch. Fill that section with one line per finding of the review, each with
`file:line` of what was done (or `REFUTED:` / `FIXED:` forms exactly as CLAUDE.md section 5 defines them: path exists, newer than the
review, line under that heading). The review's verdict is `novel` and its discriminating test is E1 at ops 10-12 on the scratch.
Do not invent a disposition: if a finding has no change behind it yet, write that it is carried to the scratch card and cite the plan
row, using no release keyword. Then run `py tools/prior_art_review.py` in its check form (read its usage first) and quote what the gate
says about this file.

## Part 2 - dry + prerun on the new bytes
Same commands as `brief_157-a1-2.md` Part 2 items 1-4 (read it; call the same stage_prerun functions), under
`py tools/bgrun.py --max-min 10 --log tools/bench/diag_c158_a1_3_<name>.log -- ...`, for `tools/recipes/stage_d1_ring_p5s02a.py` and
`..._scratch.py`: dry, prerun, `--scratch-required`, the launch gate on the FULL scratch command (not run). Quote PASS counts, the X10
line (planned MAIN peak vs 675; Executor-only), X17, X14, PB state, the checkpoint list actually used (must be
(0,1,3,6,8,9,12,15,16,17)), and the exact `DRY-UNVERIFIED-OK` label prefix the launch gate asks for. If planned MAIN is above 675: do
NOT re-cut; report the number and stop (judgement owns the cut).

Facts file `tools/bench/diag_c158_a1_3_facts.md` (<= 40 lines, facts only, an `OPEN:` line per unresolved thing, md5 of every file
changed). Return the standard <= 30-line summary. Failure budget 2.
