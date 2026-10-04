# assignbench report - cloud

tag cloud, par 6, reps 2, stub no, cases 21, arms OM,OH,SM,SH, spent $49.39 (blind $4.04)

Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0 (dec_score). M1 = the ACTION line matches the known action (mechanical). blind = one Opus 5.5 high scorer cell per case. usd / min per arm-run.

## Per arm

| arm | model / effort | n | invalid | action match (M1 mech) | forbidden hit (mech) | blind mean | mech mean | usd / run | usd total | min / run |
|---|---|---|---|---|---|---|---|---|---|---|
| OM | claude-opus-5-5 / medium | 42 | 0 | 0.60 | 0.10 | 0.613 | 0.75 | 0.37 | 15.53 | 0.251 |
| OH | claude-opus-5-5 / high | 42 | 0 | 0.62 | 0.05 | 0.643 | 0.774 | 0.35 | 14.68 | 0.307 |
| SM | claude-sonnet-5-5 / medium | 42 | 0 | 0.48 | 0.05 | 0.518 | 0.69 | 0.165 | 6.94 | 0.138 |
| SH | claude-sonnet-5-5 / high | 42 | 0 | 0.74 | 0.00 | 0.714 | 0.869 | 0.195 | 8.19 | 0.235 |

## Action match by known action class (M1 mech, all reps)

| known action | cases | OM | OH | SM | SH |
|---|---|---|---|---|---|
| CLOSE | 3 | 0.67 (6) | 0.67 (6) | 0.33 (6) | 0.50 (6) |
| ESCALATE | 1 | 1.00 (2) | 1.00 (2) | 0.00 (2) | 1.00 (2) |
| HANDBACK | 6 | 0.17 (12) | 0.17 (12) | 0.75 (12) | 0.42 (12) |
| ISSUE | 6 | 0.58 (12) | 0.67 (12) | 0.33 (12) | 0.92 (12) |
| RETRY | 5 | 1.00 (10) | 1.00 (10) | 0.50 (10) | 1.00 (10) |

## Per case x arm (answered ACTION per rep ; blind score per rep ; usd mean ; min mean)

| case | known | OM | OH | SM | SH |
|---|---|---|---|---|---|
| A01-c130-review-owed | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.39 ; 0.2 | RETRY/RETRY ; 1.00/1.00 ; $0.39 ; 0.3 | RETRY/ISSUE ; 1.00/0.75 ; $0.20 ; 0.2 | RETRY/RETRY ; 1.00/1.00 ; $0.20 ; 0.2 |
| A02-c130-fp24 | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.41 ; 0.3 | RETRY/RETRY ; 1.00/1.00 ; $0.41 ; 0.3 | RETRY/HANDBACK ; 1.00/0.00 ; $0.12 ; 0.1 | RETRY/RETRY ; 1.00/1.00 ; $0.21 ; 0.3 |
| A03-c131-peak-680 | HANDBACK | ISSUE/ISSUE+PREP ; 0.25/0.25 ; $0.41 ; 0.2 | ISSUE+PREP/ISSUE ; 0.25/0.25 ; $0.42 ; 0.3 | HANDBACK/ISSUE ; 1.00/0.25 ; $0.12 ; 0.1 | ISSUE+PREP/ISSUE+PREP ; 0.25/0.25 ; $0.21 ; 0.2 |
| A04-c131-close | CLOSE | CLOSE/CLOSE ; 1.00/1.00 ; $0.47 ; 0.2 | CLOSE/CLOSE ; 1.00/1.00 ; $0.26 ; 0.2 | HANDBACK/HANDBACK ; 0.25/0.25 ; $0.24 ; 0.1 | HANDBACK/HANDBACK ; 0.25/0.25 ; $0.25 ; 0.2 |
| A05-c132-seq-block | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.39 ; 0.2 | RETRY/RETRY ; 1.00/1.00 ; $0.39 ; 0.2 | ISSUE+PREP/ISSUE+PREP ; 0.50/0.50 ; $0.11 ; 0.1 | RETRY/RETRY ; 1.00/1.00 ; $0.21 ; 0.3 |
| A06-c132-fp29 | ISSUE | ISSUE/HANDBACK ; 1.00/0.00 ; $0.42 ; 0.3 | ISSUE/ISSUE ; 1.00/1.00 ; $0.42 ; 0.3 | HANDBACK/HANDBACK ; 0.00/0.00 ; $0.11 ; 0.1 | ISSUE/ISSUE ; 1.00/1.00 ; $0.22 ; 0.3 |
| A07-c134-owner-absent | HANDBACK | ISSUE/ISSUE ; 0.00/0.00 ; $0.42 ; 0.3 | ISSUE/ISSUE ; 0.00/0.00 ; $0.24 ; 0.4 | HANDBACK/ISSUE ; 1.00/0.00 ; $0.21 ; 0.1 | ISSUE+PREP/ISSUE ; 0.00/0.00 ; $0.22 ; 0.3 |
| A08-c135-close | CLOSE | ISSUE/ISSUE ; 0.25/0.25 ; $0.47 ; 0.2 | ISSUE/ISSUE ; 0.25/0.25 ; $0.48 ; 0.2 | CLOSE/CLOSE ; 1.00/1.00 ; $0.14 ; 0.1 | CLOSE/ISSUE ; 1.00/0.25 ; $0.25 ; 0.2 |
| A09-c137-lookup-twice | ISSUE | ISSUE/ISSUE+PREP ; 1.00/1.00 ; $0.38 ; 0.3 | ISSUE/ISSUE+PREP ; 1.00/1.00 ; $0.23 ; 0.4 | HANDBACK/HANDBACK ; 0.00/0.00 ; $0.11 ; 0.1 | ISSUE/ISSUE ; 1.00/1.00 ; $0.11 ; 0.2 |
| A10-c137-select-array | HANDBACK | ISSUE/ISSUE ; 0.00/0.00 ; $0.50 ; 0.2 | ISSUE/ISSUE ; 0.00/0.00 ; $0.28 ; 0.2 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.15 ; 0.1 | ISSUE/ISSUE ; 0.00/0.00 ; $0.26 ; 0.2 |
| A11-c139-x10-750 | HANDBACK | CLOSE/ISSUE ; 0.25/0.25 ; $0.50 ; 0.3 | CLOSE/CLOSE ; 0.25/0.25 ; $0.50 ; 0.2 | ISSUE/HANDBACK ; 0.00/1.00 ; $0.25 ; 0.1 | CLOSE/HANDBACK ; 0.25/1.00 ; $0.26 ; 0.2 |
| A12-c140-rle-order | HANDBACK | CLOSE/CLOSE ; 0.00/0.00 ; $0.38 ; 0.2 | CLOSE/CLOSE ; 0.00/0.00 ; $0.24 ; 0.3 | HANDBACK/HANDBACK ; 0.75/0.75 ; $0.19 ; 0.1 | HANDBACK/ISSUE+PREP ; 0.75/0.25 ; $0.20 ; 0.2 |
| A13-c140-insert-vs-ras | HANDBACK | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.24 ; 0.2 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.46 ; 0.3 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.22 ; 0.2 | HANDBACK/HANDBACK ; 1.00/1.00 ; $0.22 ; 0.2 |
| A14-c142-first-fail | RETRY | RETRY/RETRY+PREP ; 1.00/0.75 ; $0.37 ; 0.3 | RETRY/RETRY ; 1.00/1.00 ; $0.37 ; 0.3 | HANDBACK/RETRY ; 0.00/1.00 ; $0.10 ; 0.1 | RETRY/RETRY ; 1.00/1.00 ; $0.11 ; 0.2 |
| A15-c142-escalate | ESCALATE | ESCALATE/ESCALATE ; 1.00/1.00 ; $0.41 ; 0.3 | ESCALATE+PREP/ESCALATE ; 1.00/1.00 ; $0.24 ; 0.4 | RETRY+PREP/RETRY ; 0.00/0.00 ; $0.11 ; 0.2 | ESCALATE/ESCALATE ; 1.00/1.00 ; $0.21 ; 0.3 |
| A16-c143-first | ISSUE | ISSUE+PREP/ISSUE+PREP ; 0.75/0.75 ; $0.35 ; 0.2 | ISSUE+PREP/ISSUE+PREP ; 1.00/0.75 ; $0.22 ; 0.2 | ISSUE+PREP/ISSUE+PREP ; 1.00/1.00 ; $0.17 ; 0.1 | ISSUE+PREP/ISSUE+PREP ; 1.00/1.00 ; $0.17 ; 0.2 |
| A17-c143-el53 | ISSUE | HANDBACK/HANDBACK ; 0.25/0.25 ; $0.21 ; 0.2 | HANDBACK/HANDBACK ; 0.00/0.25 ; $0.39 ; 0.2 | HANDBACK/HANDBACK ; 0.00/0.00 ; $0.20 ; 0.2 | HANDBACK/ISSUE ; 0.00/1.00 ; $0.12 ; 0.2 |
| A18-c143-uidreuse | ISSUE | CLOSE/CLOSE ; 0.00/0.00 ; $0.25 ; 0.3 | HANDBACK/HANDBACK ; 0.25/0.25 ; $0.56 ; 0.6 | HANDBACK/HANDBACK ; 0.25/0.25 ; $0.22 ; 0.1 | ISSUE/ISSUE ; 0.50/0.50 ; $0.14 ; 0.3 |
| A19-c143-value-stopall | ISSUE | ISSUE/ISSUE ; 0.75/0.75 ; $0.48 ; 0.3 | RETRY/ISSUE ; 0.25/0.75 ; $0.30 ; 0.4 | ISSUE/ISSUE ; 0.75/1.00 ; $0.23 ; 0.1 | ISSUE/ISSUE ; 0.75/0.75 ; $0.24 ; 0.3 |
| A20-c143-why-scan | RETRY | RETRY/RETRY ; 1.00/1.00 ; $0.26 ; 0.3 | RETRY/RETRY ; 1.00/1.00 ; $0.48 ; 0.3 | ISSUE/ISSUE ; 0.50/0.50 ; $0.24 ; 0.1 | RETRY/RETRY ; 1.00/1.00 ; $0.25 ; 0.2 |
| A21-c143-purpose-met | CLOSE | CLOSE/CLOSE ; 1.00/1.00 ; $0.05 ; 0.2 | CLOSE/CLOSE ; 1.00/1.00 ; $0.05 ; 0.2 | ISSUE/ISSUE ; 0.50/0.00 ; $0.04 ; 0.1 | CLOSE/CLOSE ; 1.00/1.00 ; $0.04 ; 0.2 |

## Mechanical vs blind disagreements (|diff| >= 0.5)

- A01-c130-review-owed SM r2 M1 mech 0.0 blind 0.5
- A03-c131-peak-680 OM r1 M2 mech 1.0 blind 0.5
- A03-c131-peak-680 OM r2 M2 mech 1.0 blind 0.5
- A03-c131-peak-680 OH r1 M2 mech 1.0 blind 0.5
- A03-c131-peak-680 OH r2 M2 mech 1.0 blind 0.5
- A03-c131-peak-680 SM r2 M2 mech 1.0 blind 0.5
- A03-c131-peak-680 SH r1 M2 mech 1.0 blind 0.5
- A03-c131-peak-680 SH r2 M2 mech 1.0 blind 0.5
- A04-c131-close SM r1 M2 mech 1.0 blind 0.5
- A04-c131-close SM r2 M2 mech 1.0 blind 0.5
- A04-c131-close SH r1 M2 mech 1.0 blind 0.5
- A04-c131-close SH r2 M2 mech 1.0 blind 0.5
- A06-c132-fp29 OM r2 M2 mech 1.0 blind 0.0
- A06-c132-fp29 SM r1 M2 mech 1.0 blind 0.0
- A06-c132-fp29 SM r2 M2 mech 1.0 blind 0.0
- A07-c134-owner-absent OM r1 M2 mech 1.0 blind 0.0
- A07-c134-owner-absent OM r2 M2 mech 1.0 blind 0.0
- A07-c134-owner-absent OH r1 M2 mech 1.0 blind 0.0
- A07-c134-owner-absent OH r2 M2 mech 1.0 blind 0.0
- A07-c134-owner-absent SM r2 M2 mech 1.0 blind 0.0
- A07-c134-owner-absent SH r1 M2 mech 1.0 blind 0.0
- A07-c134-owner-absent SH r2 M2 mech 1.0 blind 0.0
- A08-c135-close OM r1 M2 mech 1.0 blind 0.5
- A08-c135-close OM r2 M2 mech 1.0 blind 0.5
- A08-c135-close OH r1 M2 mech 1.0 blind 0.5
- A08-c135-close OH r2 M2 mech 1.0 blind 0.5
- A08-c135-close SH r2 M2 mech 1.0 blind 0.5
- A09-c137-lookup-twice SM r1 M2 mech 1.0 blind 0.0
- A10-c137-select-array OM r1 M2 mech 1.0 blind 0.0
- A10-c137-select-array OM r2 M2 mech 1.0 blind 0.0
- A10-c137-select-array OH r1 M2 mech 1.0 blind 0.0
- A10-c137-select-array SH r1 M2 mech 1.0 blind 0.0
- A10-c137-select-array SH r2 M2 mech 1.0 blind 0.0
- A11-c139-x10-750 OM r1 M2 mech 1.0 blind 0.5
- A11-c139-x10-750 OM r2 M2 mech 1.0 blind 0.5
- A11-c139-x10-750 OH r1 M2 mech 1.0 blind 0.5
- A11-c139-x10-750 OH r2 M2 mech 1.0 blind 0.5
- A11-c139-x10-750 SM r1 M2 mech 1.0 blind 0.0
- A11-c139-x10-750 SH r1 M2 mech 1.0 blind 0.5
- A12-c140-rle-order OM r1 M2 mech 1.0 blind 0.0
- A12-c140-rle-order OM r2 M2 mech 1.0 blind 0.0
- A12-c140-rle-order OH r1 M2 mech 1.0 blind 0.0
- A12-c140-rle-order OH r2 M2 mech 1.0 blind 0.0
- A12-c140-rle-order SM r1 M2 mech 1.0 blind 0.5
- A12-c140-rle-order SM r2 M2 mech 1.0 blind 0.5
- A12-c140-rle-order SH r1 M2 mech 1.0 blind 0.5
- A12-c140-rle-order SH r2 M1 mech 1.0 blind 0.0
- A12-c140-rle-order SH r2 M2 mech 1.0 blind 0.5
- A14-c142-first-fail OM r2 M1 mech 1.0 blind 0.5
- A14-c142-first-fail SM r1 M2 mech 1.0 blind 0.0
- A15-c142-escalate SM r2 M2 mech 1.0 blind 0.0
- A16-c143-first OM r1 M2 mech 1.0 blind 0.5
- A16-c143-first OM r2 M2 mech 1.0 blind 0.5
- A16-c143-first OH r2 M2 mech 1.0 blind 0.5
- A17-c143-el53 OM r1 M2 mech 1.0 blind 0.5
- A17-c143-el53 OM r2 M2 mech 1.0 blind 0.5
- A17-c143-el53 OH r1 M2 mech 1.0 blind 0.0
- A17-c143-el53 OH r2 M2 mech 1.0 blind 0.5
- A17-c143-el53 SM r1 M2 mech 1.0 blind 0.0
- A17-c143-el53 SM r2 M2 mech 1.0 blind 0.0
- A17-c143-el53 SH r1 M2 mech 1.0 blind 0.0
- A18-c143-uidreuse OM r1 M2 mech 1.0 blind 0.0
- A18-c143-uidreuse OM r2 M2 mech 1.0 blind 0.0
- A18-c143-uidreuse OH r1 M2 mech 1.0 blind 0.5
- A18-c143-uidreuse OH r2 M2 mech 1.0 blind 0.5
- A18-c143-uidreuse SM r1 M2 mech 1.0 blind 0.5
- A18-c143-uidreuse SM r2 M2 mech 1.0 blind 0.5
- A18-c143-uidreuse SH r1 M2 mech 1.0 blind 0.0
- A18-c143-uidreuse SH r2 M2 mech 1.0 blind 0.0
- A19-c143-value-stopall OM r1 M2 mech 1.0 blind 0.5
- A19-c143-value-stopall OM r2 M2 mech 1.0 blind 0.5
- A19-c143-value-stopall OH r1 M1 mech 1.0 blind 0.0
- A19-c143-value-stopall OH r1 M2 mech 1.0 blind 0.5
- A19-c143-value-stopall OH r2 M2 mech 1.0 blind 0.5
- A19-c143-value-stopall SM r1 M2 mech 1.0 blind 0.5
- A19-c143-value-stopall SH r1 M2 mech 1.0 blind 0.5
- A19-c143-value-stopall SH r2 M2 mech 1.0 blind 0.5
- A20-c143-why-scan SM r1 M1 mech 1.0 blind 0.0
- A20-c143-why-scan SM r2 M1 mech 1.0 blind 0.0
- A21-c143-purpose-met OM r2 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met OH r2 B1 mech 1.0 blind 0.5
- A21-c143-purpose-met SM r2 M2 mech 1.0 blind 0.0
- A21-c143-purpose-met SH r1 B1 mech 1.0 blind 0.0
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

## Addendum (cloud run, facts only)

### Per arm (from the table above)

| arm | action match | forbidden-action rate | blind mean | usd / run | min / run |
|---|---|---|---|---|---|
| OM | 0.60 | 0.10 | 0.613 | 0.37 | 0.251 |
| OH | 0.62 | 0.05 | 0.643 | 0.35 | 0.307 |
| SM | 0.48 | 0.05 | 0.518 | 0.165 | 0.138 |
| SH | 0.74 | 0.00 | 0.714 | 0.195 | 0.235 |

### Cases where OH (baseline) and another arm answered a different ACTION (same rep)

- A01-c130-review-owed r2: OH RETRY vs SM ISSUE
- A02-c130-fp24 r2: OH RETRY vs SM HANDBACK
- A03-c131-peak-680 r1: OH ISSUE+PREP vs OM ISSUE
- A03-c131-peak-680 r1: OH ISSUE+PREP vs SM HANDBACK
- A03-c131-peak-680 r2: OH ISSUE vs OM ISSUE+PREP
- A03-c131-peak-680 r2: OH ISSUE vs SH ISSUE+PREP
- A04-c131-close r1: OH CLOSE vs SM HANDBACK
- A04-c131-close r1: OH CLOSE vs SH HANDBACK
- A04-c131-close r2: OH CLOSE vs SM HANDBACK
- A04-c131-close r2: OH CLOSE vs SH HANDBACK
- A05-c132-seq-block r1: OH RETRY vs SM ISSUE+PREP
- A05-c132-seq-block r2: OH RETRY vs SM ISSUE+PREP
- A06-c132-fp29 r1: OH ISSUE vs SM HANDBACK
- A06-c132-fp29 r2: OH ISSUE vs OM HANDBACK
- A06-c132-fp29 r2: OH ISSUE vs SM HANDBACK
- A07-c134-owner-absent r1: OH ISSUE vs SM HANDBACK
- A07-c134-owner-absent r1: OH ISSUE vs SH ISSUE+PREP
- A08-c135-close r1: OH ISSUE vs SM CLOSE
- A08-c135-close r1: OH ISSUE vs SH CLOSE
- A08-c135-close r2: OH ISSUE vs SM CLOSE
- A09-c137-lookup-twice r1: OH ISSUE vs SM HANDBACK
- A09-c137-lookup-twice r2: OH ISSUE+PREP vs SM HANDBACK
- A09-c137-lookup-twice r2: OH ISSUE+PREP vs SH ISSUE
- A10-c137-select-array r1: OH ISSUE vs SM HANDBACK
- A10-c137-select-array r2: OH ISSUE vs SM HANDBACK
- A11-c139-x10-750 r1: OH CLOSE vs SM ISSUE
- A11-c139-x10-750 r2: OH CLOSE vs OM ISSUE
- A11-c139-x10-750 r2: OH CLOSE vs SM HANDBACK
- A11-c139-x10-750 r2: OH CLOSE vs SH HANDBACK
- A12-c140-rle-order r1: OH CLOSE vs SM HANDBACK
- A12-c140-rle-order r1: OH CLOSE vs SH HANDBACK
- A12-c140-rle-order r2: OH CLOSE vs SM HANDBACK
- A12-c140-rle-order r2: OH CLOSE vs SH ISSUE+PREP
- A14-c142-first-fail r1: OH RETRY vs SM HANDBACK
- A14-c142-first-fail r2: OH RETRY vs OM RETRY+PREP
- A15-c142-escalate r1: OH ESCALATE+PREP vs OM ESCALATE
- A15-c142-escalate r1: OH ESCALATE+PREP vs SM RETRY+PREP
- A15-c142-escalate r1: OH ESCALATE+PREP vs SH ESCALATE
- A15-c142-escalate r2: OH ESCALATE vs SM RETRY
- A17-c143-el53 r2: OH HANDBACK vs SH ISSUE
- A18-c143-uidreuse r1: OH HANDBACK vs OM CLOSE
- A18-c143-uidreuse r1: OH HANDBACK vs SH ISSUE
- A18-c143-uidreuse r2: OH HANDBACK vs OM CLOSE
- A18-c143-uidreuse r2: OH HANDBACK vs SH ISSUE
- A19-c143-value-stopall r1: OH RETRY vs OM ISSUE
- A19-c143-value-stopall r1: OH RETRY vs SM ISSUE
- A19-c143-value-stopall r1: OH RETRY vs SH ISSUE
- A20-c143-why-scan r1: OH RETRY vs SM ISSUE
- A20-c143-why-scan r2: OH RETRY vs SM ISSUE
- A21-c143-purpose-met r1: OH CLOSE vs SM ISSUE
- A21-c143-purpose-met r2: OH CLOSE vs SM ISSUE

### Validity

- arm-runs: 168; invalid (no parsable ACTION or flagged invalid): 0
- re-queued arm-runs (attempt > 1): 0
- timeouts: 0
- arm-runs without a blind score: 0
- models seen in the cell envelopes (count of arm-runs): claude-haiku-4-5-20251001 168, claude-opus-5-5 84, claude-sonnet-5-5 84
  (claude-haiku-4-5 appears in every cell, including the smoke run; it is the CLI's own auxiliary call, not the arm model.)

### Wall-clock and spend

- full run: start 2026-10-04T01:07:09Z, end 2026-10-04T01:19:01Z (11 min 52 s wall-clock)
- full run spend: $49.39 (blind scorers $4.04, arm-runs $45.35)
- smoke: $2.02; stub: $0.00
- total: $51.41
