ACTION: HANDBACK
CARD: -
REASON: The P3b-2 chain is stuck on two gate questions, and settling either one is a rule decision, not material work.
(1) Card 132-3 is blocked by fp-29. X10 has refused UNMEASURED since card 130-1 (`tools/stage_prerun.py:1984-1987`). That refusal also catches the read-only graph reader, which has 0 wire/delete/RLE ops (prerun.log:17). The P3a twin of this reader only passed because the old X10 rule gave it a WARN (`diag_c125_graph_p3a_prerun.log:20-21`).
(2) The graph read is what P3b-2 `--rebase` needs. Once the rebase runs, the dry would bind against the real graph. That could make fp-21 (132-1's FAIL, unbound negative uids on the provisional base) unnecessary to fix, but that is not settled until the rebase is tried.
(3) Card 132-1 also left three other judgement questions open: how to pin the 50..52 Error List range, the fp-21 approach, and whether to accept the c106e E1 re-pin and the fs_border-only scope of the name gate.
Only 35 of 180 minutes are used, but a retry under the current X10 would fail the same way.
HANDBACK-QUESTION: Should X10 let a read-only reader through (0 edit ops in the dry plan → WARN, not UNMEASURED FAIL; fp-29 drained that way), so the P3b-1 graph read can run and P3b-2 can be rebased on the real graph? Or should the meter for this run come from somewhere else, for example the P3a read's measured memory?