# c90-sites-p2-treegap

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0932  in 18 / out 10340 / cache-create 90482 / cache-read 812419  (114s, 14 turn(s))
- **date:** 2026-09-26 04:11:53
- **outcome:** ANSWERED (118s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failed prediction P2 in tools/bench/diag_c90_t0_sites_offline.py (log tools/bench/diag_c90_t0_sites_offline.log, run 1 at 04:07:41):

CLAIM: "P2 (every stamp site's diagram-ancestor chain ends at the top-level diagram #536) failed ONLY because the chain builder `jev_candidates.diagram_tree` (tools/jev_candidates.py:102-119) derives parent links solely from the inner/outer `frame_diagram` of tunnel-class objects listed in TREE_OWNERS = (LoopTunnel, Tunnel, SelectorTunnel, LeftShiftRegister, RightShiftRegister). Flat-sequence / stacked-sequence frames are not in that set, so every chain stops at a sequence-frame diagram (#686 owner Sequence, #15041, #3121) instead of reaching #536. The 17 site rows themselves (node uid, frame diagram, holding While loop resolved through shift-register inner frames, case frames between node and loop, wired output terminal + wire uid) are unaffected: their holding-loop attribution uses graph_loops_s1 shift registers, not the chain end. Therefore the expectation was the script's error (fix: accept a chain end whose diagram owner is Sequence/FlatSequenceFrame), and nothing about D1_s1_copy.vi or the wiki record is wrong."

Evidence to check: docs/wiki/subvi/D1_s1_copy.json (terminals rows carry owner_class/frame_diagram), tools/bench/graph_objs_s1_20260923.json (diagram uid -> owner class: #686 owner 'Sequence'), tools/bench/t0_sites_s1.json (the table written by run 1), tools/jev_candidates.py TREE_OWNERS, tools/vigraph.py build4 (fs edges come from fs_tunnel_pairs, not from the tree).

Already ruled out: (1) missing frame_diagram on a site - every site had one (P5 rows==sites passed, all 17 chains non-empty); (2) a wrong loop attribution - the three While loops #25380/#637/#15173 resolved to bodies #25392/#639/#15266 (P4 passed) and #644 is the frame loop's `i` (P3 passed after the name filter fix).

Questions: strongest reason the claim is wrong; an alternative explanation (e.g. is a chain that stops at #686 hiding a CASE frame between a site and its loop that the 'runs every iteration' column would then miss?); what would falsify it; the cheapest discriminating test on the offline files.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim is wrong. The chain-gap diagnosis is right, but "the 17 site rows are unaffected" and "nothing is wrong" are not.**

## 1. Strongest reason it is wrong
The rows depend on the chain body, not only on its end. For #16788 (Draw Circle by Radius) and #16827 (Draw Text at Point), `t0_sites_s1.json` has `holding_loop 16557, every-iter True, case-frames []` (`diag_c90_t0_sites_offline.log:63,65`). Their chain, though, is `[16621, 16303, 15266, 15041]` (log:81), and the owners in `graph_objs_s1_20260923.json` are:
- #16621 is a ForLoop body (line 62293).
- #16303 is a **CaseStructure** frame (line 61942).
- #15266 is the body of the While loop #15173 (line 54067).

`holding` is the first chain entry found in `loop_of_body` (`diag_c90_t0_sites_offline.py:88`). `loop_of_body` holds every loop that has a shift register, and For loop #16557 has one (`graph_loops_s1_20260924.json:85-88`). So the "holding loop" becomes the inner For loop. The case frame #16303 between the draw calls and the display While loop is never checked. Relative to #15173, these two sites do **not** run every iteration, yet the table says they do.

The same rule gives the opposite answer elsewhere. The kernel, Median and FIR sites sit in For bodies #29894 and #7911 (lines 26752, 36589), and those loops have no shift registers. They are skipped, and the holding loop becomes While #637. So `holding_loop` means "innermost loop that happens to have a shift register", which is sometimes a For loop and sometimes a While loop. The `runs_every_iteration` column is therefore ill-defined for exactly the question the stamp-site table exists to answer.

## 2. Alternative explanation of the same evidence
P2 failed because of the tree gap, and that part is correct: TREE_OWNERS (`jev_candidates.py:55`) has no sequence-tunnel class. The wiki does record 1,152 FlatSequence/Sequence-owned terminal rows, so the data to bridge the gap exists and the tree ignores it.

The relaxed gate at `diag_c90_t0_sites_offline.py:107-113` now accepts **any** chain that ends at a sequence frame. That makes P2 unable to fail for the class of error it was meant to catch.

On your specific question: a chain truncated at #686, #15041 or #3121 cannot make `every-iter` falsely **True**. Where a loop was found, every diagram below it was walked through tunnels. The risk runs the other way: a sequence frame between a node and its loop stops the chain before the loop, so `holding` becomes None. That leaves three rows unproven by the tree:
- #6216 and #5987, both on #3121
- #6384, on #686

Their "loop None" rests only on an argument from position:
- #3121 sits at y=588, while the top-level FlatSequence #681 sits at y=102 and #686 at y=136. That suggests #3121 is a frame of a **nested** sequence, not a direct frame on #536.
- There are 20 FlatSequence/Sequence objects, most of them owned by "Diagram" (nested), not by #536.

This is inference, not measurement.

A minor point: the claim says #686's owner is "Sequence". The file says `FlatSequenceFrame` (line 16213), and #3121 and #15041 are the same. SEQ_OWNERS covers all of these, but the evidence was cited wrongly.

## 3. What would falsify the claim
Any one of these, from a correct walk:
- A row whose relation to its enclosing **While** loop differs from the table. #16788/#16827 already qualify if case #16303 lies inside #15266, and the chain says it does.
- A chain extended through sequence tunnels that does not reach #536.
- A chain whose extension passes through a While body above #3121 or #686.

## 4. Cheapest discriminating test (offline, no LabVIEW)
1. Bridge the gap: for the sequence-tunnel terminal rows in `docs/wiki/subvi/D1_s1_copy.json` (or `rec["fs_tunnel_pairs"]`), add parent links from inner `frame_diagram` to outer `frame_diagram`. This is the same vote logic as `diagram_tree`. Then re-run the chains and assert that every one ends at #536.
2. Define the holding loop as the innermost **WhileLoop** ancestor, using `objs[a]["owner"] == "WhileLoop"` rather than `loop_of_body`, and list every CaseStructure/EventStructure frame between the node and that While body.

- **Claim holds:** every chain reaches #536, no While loop appears above #3121 or #686, and all 17 rows keep their values.
- **Claim is refuted:** #16788 and #16827 come back `case_frames=[16303]`, `runs_every_iteration=False` against #15173. The case frame already appears in the run-1 chains, so I expect this outcome.

What would change my mind: evidence that "holding loop = innermost loop with a shift register, For loops included" is the intended meaning for PD196(d) step 3. In that case the column is misnamed rather than wrong, and that should be written down. Web search was not needed here, since every point above is decided by this project's own files.

## Sources

(extract from answer)

## What was done with it

ACCEPTED (material session, card 90-4, 2026-09-26 04:1x). The claim's "17 rows unaffected" was wrong: run 1's holding-loop rule was "innermost loop with a shift register", which gave #16788/#16827 the For loop #16557 and hid case frame #16303.
FIXED: c90-sites-p2-treegap - tools/bench/diag_c90_t0_sites_offline.py:88-91 - holding loop = innermost WhileLoop-owned ancestor (objs owner), inner For bodies reported separately, case frames counted up to the While body; new gate P6 asserts the review's falsifier (#16788/#16827 -> case_frames [16303], every-iter False); rows whose chain stops at a sequence frame with no While body above are flagged `loop_proven_by_tree: false` and their owner chain is MEASURED on the machine by tools/bench/diag_c90_t0_place.py (build_d1_v0.owner_of walk from #3121/#686/#15041 to the top level).
Not done: bridging the tree through sequence tunnels (test 1) - the FSIT rows' `frame_diagram` is known to be wrong for half of them (vigraph.py:405-408), so the machine owner walk was used instead. Evidence citation corrected: #686/#3121/#15041 are owned by `FlatSequenceFrame`, not `Sequence`.
