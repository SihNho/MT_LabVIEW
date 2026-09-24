# chatS1-sim-l7-split

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.3956  in 26 / out 9267 / cache-create 114900 / cache-read 1454809  (106s, 16 turn(s))
- **date:** 2026-09-24 22:20:35
- **outcome:** ANSWERED (110s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failure in tools/bench/sim_l7_split.log (script tools/bench/sim_l7_split.py, the pure-Python stage
simulator replaying loop 1.7's split; gate "C5 L7-R: simulated uid-edges == recorded reference up to new-uid naming (diff count 22)").

CLAIM: the 22 differences are NOT an error of the simulator's op models (move / wire / tunnel / delete). They are a
REPRESENTATION mismatch between the two graphs being compared: every printed only_ref edge (only_sim is empty) has as its
SOURCE node a loop BODY Diagram uid (13404, 15266, 16621, 21577, 22532, 22847, 25290 - bodies of ForLoops 13390/16557/21305/
22433/22786/25272 and WhileLoop 15173, per tools/bench/opmodels/bed_s4_map.json "loops"), i.e. a Diagram-owned terminal
(iteration / loop-count style terminals). None of them touches #376, loop 1.7 (#23041/#23405) or any node the plan edits.
Steps up to L7-1 (step 18) compare with diff 0, and C6 (computation_diff rows) PASSES at L7-R. So the fault is in how the
L7-R reference graph was built (a different reader / loops table - stage_d1_l7_r.py lg() uses graph_loops_m4b_20260924.json
and wiki_build.read_live on the live file) versus the simulator's base graph, i.e. a bug in OUR comparison inputs, and the fix
is to build reference and base with the same reader (or exclude Diagram-owned source terminals symmetrically), not to change
an op model.

Already ruled out: (1) the move model - C3/C4 pass and a separate terminal-level check of the L7-1a move against the saved
artefact reproduces its 16-edge cut set; (2) new-uid naming - only_sim is empty, so it is not a renaming artefact.

Read the log, the script and the reference files it loads. Say what would falsify the claim and name the cheapest
discriminating test (e.g. whether those 22 edges exist in the S3 base graph the simulator started from, and whether the
recorded L7-R reference was built with Diagram-owned terminals keyed differently).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is wrong.** The 22 differences come from the simulator's own `remove_bad_wires` model reacting to duplicate terminal rows in the base graph. The reference and the base are not two different readings.

**1. Strongest reason it is wrong: the reference was built from the simulator's own base graph.**
- In `tools/bench/sim_l7_split.py:97-102`, every reference set starts from `E3 = S.uid_edges(G3)`. `G3` is `graph_s3_loop15_20260924.json`, the same graph the simulator starts from.
- Only `PRED["removed"]` and `PRED["added"]` came from `stage_d1_l7_r.py`'s reader and loops table.
- An `only_ref` edge with `only_sim` empty therefore means: the edge was in the base, the recorded run did not list it as removed, and the simulator deleted it.
- The step list shows which step did it. The diff is 0 at L7-1 (step 18). Step 45 `remove_bad_wires` then removed 16 wires (`tools/bench/sim/l7_split/summary.json:5524-5540`):
  - 4 are #376 half-wires: 1581, 3268, 3629, 4517.
  - 12 are not: 13486, 16880, 19372, 23614, 25186, 25404, 25478, 26025, 28924, 31169, 31193, 34066.
- The claim lists the op models as "move / wire / tunnel / delete". It leaves out `remove_bad_wires`, which is the op that did the deleting.

**2. What actually happens.**
- The S3 graph file stores each loop body's Diagram-owned source terminal twice. I checked four of the wires:

  | wire | source terminal | its body Diagram |
  |---|---|---|
  | 13486 | 13410 | 13404 |
  | 16880 | 16636 | 16621 |
  | 19372 | 15273 | 15266 |
  | 34066 | 25406 | 25392 |

- `op_remove_bad_wires` (`tools/stagesim.py:565-577`) counts raw rows. It finds two sources on each of these wires (`n_src == 2`) and deletes the wire.
- `uid_edges` collects edges into a set, so the duplicate is invisible everywhere else. That is why steps 1-44 agree.
- The recorded LabVIEW run says its Remove Broken Wires "removed no live uid edge" (the model_evidence field cites `stage_d1_l7_r_r2.log`). So the model deletes 12 live wires that LabVIEW kept.
- Side note: the log prints only the first 8 of the 22 edges. Wire 34066's source is body #25392, which is not among the seven bodies the claim lists. The pattern still holds.

**3. The C6 PASS does not show that the computation is unchanged.** When a sink is fed by a loop-index style Diagram terminal, its effective sources come out as an empty list (`summary.json:327-328`: `frame index`, fed by 639, has `effective: []`). Losing such a wire therefore probably changes nothing in `computation_diff` (`tools/vigraph.py:697-718`). C6 looks blind to this class of wire, which makes it weak supporting evidence for the claim.

**4. What would falsify my explanation:**
- the 12 wires have exactly one source row each in the S3 graph file, or
- running remove-bad-wires on deduplicated rows still leaves the diff at 22.

**Why the proposed fixes would do harm:**
- "Build reference and base with the same reader" changes nothing, because they already share `E3`.
- "Exclude Diagram-owned source terminals from both sides" hides a real simulator defect. On any future plan, the simulator would delete every loop-index wire at the remove-bad-wires step, and C6 would not catch it.

**Cheapest test that separates the two explanations (pure Python, read-only, no LabVIEW):**
1. Count the rows per `term_uid` in the S3 graph file's `terminals`. For example, 13410 appears twice.
2. Re-run the replay with `op_remove_bad_wires` counting sources over unique `term_uid`s.
3. Compare the result:
   - **The claim predicts** C5 at L7-R stays at 22.
   - **My explanation predicts** C5 goes to 0, and `removed_wires` shrinks to 1581, 3268, 3629, 4517.

The fix then belongs in the simulator (deduplicate rows in `base_state` or in the remove-bad-wires model), plus a look at why the reader emits Diagram-owned terminals twice. The comparison inputs don't need to change.

I did not run anything, and I did no web search: every point here rests on this project's own files. Two things are unverified. I checked the duplicate rows for 4 of the 12 wires, not all 12. And the "no live edge" line in `stage_d1_l7_r_r2.log` is taken from the model_evidence field; I did not open the log itself. Plan mode also blocked writing the plan file, so this reply is the whole review.

## Sources

(extract from answer)

## What was done with it

ANSWERED — the material session's claim was REFUTED by the review and the refutation held: the C5 failure of
`sim_l7_split.log` was not a stagesim rule error but duplicate terminal rows (29 Diagram-owned uids returned twice
by `allterms.read_terms`, `:60`). Fixed at the SOURCE under card chat-S2b: `tools/vigraph.py` dedupes rows on
`term_uid` at load (first wins, count logged), stagesim's base state uses the same rows; the map bench numbers were
shown unchanged and `sim_l7_split` then reached uid-edge diff 0 at every checkpoint (`tools/bench/sim_l7_split.log`,
commit 45387a7). Same finding as `archive/peer/2026-09-24-chat-s2-rbw.md`.

SAME-ROW: sim_l7_split.log (2026-09-24 22:23:42)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.
