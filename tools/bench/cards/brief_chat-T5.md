# Brief chat-T5 - fix the last two tool faults every bench arm hit (user 2026-10-07: "1번 진행")

Basis: tools/bench/livebench/report_4arms.md (faults 1 and 5); faults 2-4 were fixed by chat-T3/T4 (PD347/348).
OFFLINE ONLY - another experiment starts within the hour; never start LabVIEW, keep CPU light.

## Fault 1 - Error List predictor double count (55 measured vs 56 predicted at P4 session 3, in all four arms)
tools/elrule.py keys the one '' sink of a created While body as BOTH cond and input (no continue after C,
elrule.items ~:58-68 as measured by arm A13's card 144-3), and the two 'Shift Register: unwired from inside the loop'
items are a text class the rule does not know. Every arm fixed this inside its worktree (V6_bench\A, A13, A13K - the
cycle-144 elrule cards/PDs). Review those fixes, port ONE correct rule to main: re-derived predictions must equal the
measured counts for s01 (51), s02 (53) and s03 (55 - from the bench arms' recorded Error List reads), no other count
changes; self-test on those recordings.

## Fault 5 - Terminal vs ParameterTerminal class name (s04 stage stopped at op 2 'p4_wait' in arms B and A13)
The simulator names a created Function node's terminals class 'Terminal'; real LabVIEW reports 'ParameterTerminal'
(V6_bench\A13 and B logs: diag_c144_p4s04v18_scratch.log E1 BINDING lines). Measure from the recorded real graphs
(bench arms' graph JSONs / scratch logs, and tools/bench/fn_records runs) which classes LabVIEW really reports per
created node kind; make the simulator emit the measured class (or make binding compare class families explicitly from a
measured table - never a loose 'any terminal' match). Self-test: the B/A13 op-2 case binds; a genuinely different class
still refuses.

## Do / limits
Existing self-tests green or explained (the 3 known HEAD failures c133_1, uidreuse_c143_4, c106e stay as they are). PD in
docs/d1/tooling.md + INDEX; commit by explicit path. Edit tool only. labview none, hardware none. Return one result/1 and
say what a real LabVIEW run should confirm later.
