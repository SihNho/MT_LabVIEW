---
card: 160-d4-1
status: current
date: 2026-10-10
---
# Brief 160-d4-1 (assignment 160-2) - OFFLINE: prior-art review of plan_ring_p5s02b.json (PD391(e)), disposition written, step 2 NOT launched

`labview: none` (no LabVIEW process; `tasklist` may be refused - say so), `peers: ["priorart"]`, no `--launch`, no `tools/**` edit, no recipe / plan / pred / licence edit. Read `docs/d1/ring-p5b.md`
(PD388-PD391), `docs/script-writing.md`, `CLAUDE.md` section 5 (the fourth layer: the only two releases `REFUTED:` / `FIXED:`, and what a `novel` verdict needs).
Step 2 plan: `tools/bench/plan_ring_p5s02b.json` (f4520b10, FINAL on 94ffff94: 20 actions = delete w10394, A24..A40 groups F3 G H, `dw_go` / `dw_ho` stub deletes; 10 ops; MAIN 657.4 <= 675).
Facts: `tools/bench/diag_c160_b3_1_facts.md` (e38a4f74), `diag_c160_a2_1_facts.md` (4a1d31e9), `diag_c160_c3_1_facts.md`, pred `plan_ring_p5s02b_pred.json` (48b50b29).

## Do
1. Write the plan-under-review text `tools/bench/prep_c160_d4_1_priorart_plan.md` (<= 60 lines; frontmatter like `prep_c156_a1_1_priorart_plan.md`, which is the TEMPLATE for shape - do not paste its blocks): design (PD388-PD391), the 20 actions by
   group, and the NEW-vs-earlier list the reviewer must test. At least: (i) deleting a sink-only stub wire (w24264 / w24300 / w10394) before connecting its terminal; (ii) the base RSR face connected through
   `connect_term_uid` `register_end_case_border` (stagexec.base_register_end, card 160-a2-1) instead of MERGE; (iii) MERGE kept for A28 / A35 (LSR faces, stubs w24285 / w24312), CEN2 judged by wire ENDS;
   (iv) case tunnel groups whose outside source is a BASE loop tunnel's inner face (G, H), (v) predicted step-2-end Error List counts (cleared 5 / raised 0 / unpredicted 2, `diag_c160_c3_1_facts.md`).
   Quote ONLY facts from those files; cite file:line. Do not claim anything about a LabVIEW run.
2. Dispatch under bgrun exactly as the 156 card did (`tools/bench/prep_c156_a1_1_priorart.log` line 1): `py tools/bgrun.py --material --max-min 12 --log tools/bench/prep_c160_d4_1_priorart.log -- py -u tools/prior_art_review.py
   --plan-file tools/bench/prep_c160_d4_1_priorart_plan.md --slug priorart-c160-d4-1-p5s02b --trigger new-op --recipe tools/recipes/stage_d1_ring_p5s02b.py` (read `prior_art_review.py` usage first; keep the flags the 156 run used).
   Foreground waits <= 6 min per call. If the dispatch hits a QUOTA / TIMEOUT / ERROR outcome, that told you nothing: report it, do not write a disposition.
3. Archive file `archive/peer/2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md` (path as the tool prints it): fill `## What was done with it` - one line per finding of the review, each with `file:line` of what
   changed or a stated carry to the scratch card (cite the plan row / pred line); `REFUTED:` / `FIXED:` ONLY with the citation CLAUDE.md requires. Do not invent a disposition. If the verdict is not `novel` or a finding
   would need a plan change: do NOT change the plan; report it as a FAIL-with-facts (judgement decides). Then run the prior-art gate's check form on the file and quote its words.
4. NOT launched: confirm `tasklist` (or state it was refused) shows no LabVIEW started by this card; no `--launch` anywhere.

## Report `tools/bench/diag_c160_d4_1_facts.md` (<= 30 lines, facts only)
Verdict card path + verdict; cost line; one line per finding with its disposition; the gate's check words; md5 of every file written; md5 UNCHANGED: plan f4520b10, pred 48b50b29, in/in2, graph 7ac24924,
VIs s09 eb1d0f31 / P5-1a 2482fe7b / P5-1 7f2582ae / 94ffff94 ("not hashed" if refused), `tools/**` (stagekit may be changing under a PARALLEL tooling card 160-e4-1: do not pin it, do not touch it); `OPEN:` lines.
