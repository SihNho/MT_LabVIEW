# assignbench report - stub_hit

tag stub_hit, par 8, reps 2, stub hit, cases 21, arms OM,OH,SM,SH, spent $0.00 (blind $0.00)

Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0 (dec_score). M1 = the ACTION line matches the known action (mechanical). blind = one Opus 5.5 high scorer cell per case. usd / min per arm-run.

## Per arm

| arm | model / effort | n | invalid | action match (M1 mech) | forbidden hit (mech) | blind mean | mech mean | usd / run | usd total | min / run |
|---|---|---|---|---|---|---|---|---|---|---|
| OM | claude-opus-5-5 / medium | 42 | 0 | 1.00 | 0.00 | 1.0 | 1.0 | 0.0 | 0.0 | 0.009 |
| OH | claude-opus-5-5 / high | 42 | 0 | 1.00 | 0.00 | 1.0 | 1.0 | 0.0 | 0.0 | 0.01 |
| SM | claude-sonnet-5-5 / medium | 42 | 0 | 1.00 | 0.00 | 1.0 | 1.0 | 0.0 | 0.0 | 0.01 |
| SH | claude-sonnet-5-5 / high | 42 | 0 | 1.00 | 0.00 | 1.0 | 1.0 | 0.0 | 0.0 | 0.009 |

## Action match by known action class (M1 mech, all reps)

| known action | cases | OM | OH | SM | SH |
|---|---|---|---|---|---|
| CLOSE | 3 | 1.00 (6) | 1.00 (6) | 1.00 (6) | 1.00 (6) |
| ESCALATE | 1 | 1.00 (2) | 1.00 (2) | 1.00 (2) | 1.00 (2) |
| HANDBACK | 6 | 1.00 (12) | 1.00 (12) | 1.00 (12) | 1.00 (12) |
| ISSUE | 6 | 1.00 (12) | 1.00 (12) | 1.00 (12) | 1.00 (12) |
| RETRY | 5 | 1.00 (10) | 1.00 (10) | 1.00 (10) | 1.00 (10) |

## Per case x arm (answered ACTION per rep ; blind score per rep ; usd mean ; min mean)

| case | known | OM | OH | SM | SH |
|---|---|---|---|---|---|
| A01-c130-review-owed | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 |
| A02-c130-fp24 | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 |
| A03-c131-peak-680 | HANDBACK | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 |
| A04-c131-close | CLOSE | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A05-c132-seq-block | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 |
| A06-c132-fp29 | ISSUE | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A07-c134-owner-absent | HANDBACK | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 |
| A08-c135-close | CLOSE | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A09-c137-lookup-twice | ISSUE | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A10-c137-select-array | HANDBACK | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 |
| A11-c139-x10-750 | HANDBACK | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 |
| A12-c140-rle-order | HANDBACK | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 |
| A13-c140-insert-vs-ras | HANDBACK | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.00 ; 0.0 |
| A14-c142-first-fail | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 |
| A15-c142-escalate | ESCALATE | ESCALATE/ESCALATE ; 1.00/1.00 ; $0.00 ; 0.0 | ESCALATE/ESCALATE ; 1.00/1.00 ; $0.00 ; 0.0 | ESCALATE/ESCALATE ; 1.00/1.00 ; $0.00 ; 0.0 | ESCALATE/ESCALATE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A16-c143-first | ISSUE | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A17-c143-el53 | ISSUE | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A18-c143-uidreuse | ISSUE | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A19-c143-value-stopall | ISSUE | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 | ISSUE/ISSUE ; 1.00/1.00 ; $0.00 ; 0.0 |
| A20-c143-why-scan | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 | RETRY/RETRY ; 1.00/1.00 ; $0.00 ; 0.0 |
| A21-c143-purpose-met | CLOSE | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 | CLOSE/CLOSE ; 1.00/1.00 ; $0.00 ; 0.0 |

## Mechanical vs blind disagreements (|diff| >= 0.5)

- A16-c143-first OM r1 B1 mech 1.0 blind 0.5
- A16-c143-first OM r2 B1 mech 1.0 blind 0.5
- A16-c143-first OH r1 B1 mech 1.0 blind 0.5
- A16-c143-first OH r2 B1 mech 1.0 blind 0.5
- A16-c143-first SM r1 B1 mech 1.0 blind 0.5
- A16-c143-first SM r2 B1 mech 1.0 blind 0.5
- A16-c143-first SH r1 B1 mech 1.0 blind 0.5
- A16-c143-first SH r2 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met OM r1 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met OM r2 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met OH r1 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met OH r2 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met SM r1 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met SM r2 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met SH r1 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met SH r2 B1 mech 1.0 blind 0.5

## Known answers (with evidence)

- **A01-c130-review-owed** (RETRY): RETRY 130-1 (same goal, from its step 3) with flags.peers widened to include `hypothesis`, so the owed hypothesis review of selftest_x10_c130_1.log can be dispatched inside the card. The block is a card-flag mismatch named by the hook, not a model or design problem. Evidence: tools/bench/cards/task_130-3.json:7; tools/bench/cards/task_130-3.json:5; tools/bench/cards/result_130-3.json:1.
- **A02-c130-fp24** (RETRY): RETRY 130-3 from its P1 with the owed review of card 130-2's failing log diag_c130_2_suite_gb.log done first (that log, not 130-3's own work, is what guard_peer blocked on), then the X10 self-test, re-cut and P3b-1 dry/prerun. Evidence: tools/bench/cards/task_130-4.json:7; tools/bench/cards/task_130-4.json:5; tools/bench/cards/result_130-4.json:1.
- **A03-c131-peak-680** (HANDBACK): HANDBACK: the measured peak 680.8 MB exceeds the 675 MB fail_above only through the final whole-VI read; whether to accept it / raise the threshold / re-cut is a memory-threshold decision for judgement. Judgement decided PD272 (fail_above 690, then S3/S4 and launch) and P3b-1 was then launched and read. Evidence: tools/bench/cards/task_131-4.json:5; tools/bench/cards/result_131-6.json:1.
- **A04-c131-close** (CLOSE): CLOSE: the purpose (P3b-1 scratch pin4 then ONE launch) is met - P3b-1 launched as D1_ring_p3b1_20261002_060910.vi and its full Error List read (53) by 131-6, 129 card-minutes used of 180. The next step (P3b-2 rebase tooling, moving the bed) needs judgement; the next cycle started from the P3b-1 file as bed. Evidence: tools/bench/cards/result_131-6.json:1; tools/bench/cards/cycle_132.json:9.
- **A05-c132-seq-block** (RETRY): RETRY 132-2 now (as 132-3): it was BLOCKED only because card 132-1 was editing tools/stage_prerun.py; 132-1 has returned, so the re-issue may run stage_prerun --dry/--prerun on the graph reader first. Evidence: tools/bench/cards/task_132-3.json:7; tools/bench/cards/task_132-3.json:5.
- **A06-c132-fp29** (ISSUE): ISSUE a card that first makes X10 model a 0-edit read-only reader (gate false positive fp-29: the check refuses the very run that would produce its meter), then runs the P3b-1 graph read and continues to the rebase. Judgement wrote it as PD277 (132-4); 132-4 then did the graph read with LabVIEW. Evidence: tools/bench/cards/task_132-4.json:5; tools/bench/cards/result_132-4.json:27.
- **A07-c134-owner-absent** (HANDBACK): HANDBACK: 134-3 returned by its own card rule (no inference) because FS 27509's diagram uid is absent from the measured graph; whether owners derived from measured border links (outer-face frame_diagram, 8/8 agree) count as 'measured' is a definition judgement must make. Judgement decided PD289(f) and 134-4 built on it. Evidence: tools/bench/cards/task_134-4.json:5; tools/bench/cards/result_134-4.json:1.
- **A08-c135-close** (CLOSE): CLOSE: the purpose (ONE launch of P3b-2, bed moves to the P3b-2 final) is met by 135-4 (PASS 13/0) and 135-5 (acceptance bookkeeping PASS 18/0), and the P4 offline facts are in. The next step (P4 routes) needed a new judgement design (PD295) - the next cycle started from it with the P3b-2 file as bed. Evidence: tools/bench/cards/result_135-5.json:1; tools/bench/cards/cycle_136.json:9.
- **A09-c137-lookup-twice** (ISSUE): ISSUE a scratch-VI verification card of the failing node lookup (constant/primitive created inside a NEW While body, each read method) - the same lookup failed in 136-3 and 137-1, and the standing rule makes the next LabVIEW act a scratch-VI check, not a third routes run. 137-3 did it (PASS 5/0) and found that node_labels cannot see constants; 137-5 then used read_terms. Evidence: tools/bench/cards/task_137-3.json:5; tools/bench/cards/result_137-3.json:1.
- **A10-c137-select-array** (HANDBACK): HANDBACK: 137-7 measured that Select rejects a Boolean ARRAY on s whatever t/f carry, so the P4 reader core ('Select with a Boolean-ARRAY s') must be redesigned - a design / rule-1a decision. Judgement replaced it with a For-loop + scalar Select + Array Min group (PD311(b), plan v8). Evidence: tools/bench/cards/result_137-7.json:26; tools/bench/cards/task_138-4.json:5.
- **A11-c139-x10-750** (HANDBACK): HANDBACK: the step-1 plan predicts 750.7 MB > 690 at 29 reads; splitting step 1 by memory vs changing the checkpoint set (and re-sizing steps 2-5 against X10) is a plan decision. Judgement's next act was PD319(c), an offline X10 session table of the whole plan before any cut. Evidence: tools/bench/cards/result_139-7.json:2; tools/bench/cards/task_140-1.json:5.
- **A12-c140-rle-order** (HANDBACK): HANDBACK (two competing explanations: plan order vs op behaviour) - judgement decided PD321: delete_wire w23255 before deleting #10171 (plan v15) and gate w23255's sinks; 140-3 (retry of 140-2) then passed op 3. A card that itself re-orders the plan this way also matches history. Evidence: tools/bench/cards/task_140-3.json:7; tools/bench/cards/task_140-3.json:5.
- **A13-c140-insert-vs-ras** (HANDBACK): HANDBACK (rule 1a): the extra Error List item shows the ring's per-slot write node is an Insert Into Array where Replace Array Subset is meant - a computation question, not a count to re-pin. Judgement had it measured (140-4: 5 bed nodes are Insert Into Array where PD246(c) says Replace Array Subset) and repaired them first in plan v16 (141-1). Evidence: tools/bench/cards/result_140-4.json:1; tools/bench/cards/task_141-1.json:5.
- **A14-c142-first-fail** (RETRY): RETRY 142-1 (failure 1 of the budget of 2): the run stopped on our own script's delete check (expected 1 object gone, got 2), not on a design question. 142-2 (retry) got past that step (16 gates vs 9). Evidence: tools/bench/cards/task_142-2.json:22; tools/bench/cards/result_142-2.json:1.
- **A15-c142-escalate** (ESCALATE): ESCALATE to Opus max (rung 1): the same card goal failed twice on Opus high (142-1, 142-2), so the failure budget is spent. 142-3 (escalation 1, Opus max) passed 87/0 on its first LabVIEW run. Evidence: tools/bench/cards/task_142-3.json:22; tools/bench/cards/result_142-3.json:1.
- **A16-c143-first** (ISSUE): ISSUE the session-2 LabVIEW card (prior-art review of the s02v18 recipe, ONE scratch on a byte copy of the s01 file, adopt on full PASS) and, beside it, an offline PREP card for the session-3 plan (provisional on stagesim's end of s02). Cycle 143 started exactly so (143-1 + 143-P1). Evidence: tools/bench/cards/task_143-1.json:3; tools/bench/cards/task_143-P1.json:3.
- **A17-c143-el53** (ISSUE): ISSUE a read-only card that loads the s02 scratch file in a fresh instance, reads its graph and identifies the 2 extra Error List items by uid (then the failed-prediction review). 143-2 did so: both items were the by-design session-boundary state (1.2 loop stop terminal, StopAll read Local), so s02 was adopted in 143-3; the S1 replay confirms 143-1 would have passed with the by-design rule. Evidence: tools/bench/cards/result_143-2.json:1; tools/bench/replay_s5.log:3.
- **A18-c143-uidreuse** (ISSUE): ISSUE an offline tooling card: the rebase refusal is a checker false failure (LabVIEW re-issued the deleted Comparison's terminal uid 23276 to the new Local) - make the rebase path key terminals by (uid, owner, name) / note uid re-use, then rebase s03 again. 143-4 did it and UID-REUSE was gone (REUSE-NOTED 23276); the S1 replay resolves it without a card. Evidence: tools/bench/cards/result_143-4.json:2; tools/bench/replay_s5.log:4.
- **A19-c143-value-stopall** (ISSUE): ISSUE (or retry with the fix): correct the s03 plan's Local terminal addresses from the simulator name 'value' to the measured name 'StopAll' by script, then rebase on the s02 graph. 143-5 did it and the rebase PASSed (plan da66a030); the S1 replay resolves it by position. Evidence: tools/bench/cards/result_143-5.json:27; tools/bench/replay_s5.log:6.
- **A20-c143-why-scan** (RETRY): RETRY the remaining s03 checks with our own pred script fixed (scan uids outside `why`/notes): the failure is our script tokenising prose, fully explained in the result. 143-6 did it and PASSed 8/0 (X10 676.4, EL 56, dry + prerun 16/0). Evidence: tools/bench/cards/task_143-6.json:3; tools/bench/cards/result_143-6.json:1.
- **A21-c143-purpose-met** (CLOSE): CLOSE: the purpose (P4 session 2 scratch adopted, session-3 prep beside it) is met - 143-3 ADOPTED the s02 file (84cac487) and 143-6 PASSed the session-3 prep 8/0 (dry + prerun). The session-3 LabVIEW card is the next cycle's first act; issuing it now is an acceptable extension, not required. Evidence: tools/bench/cards/result_143-3.json:13; tools/bench/cards/result_143-6.json:1; STATUS.md:62.
