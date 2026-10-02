# c137-p3-mkv5-stepcount

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.6206  in 32 / out 14340 / cache-create 122359 / cache-read 1774025  (160s, 25 turn(s))
- **date:** 2026-10-02 15:30:06
- **outcome:** ANSWERED (164s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failed offline gate in tools/bench/prep_c137_p3_mkv5.log (script tools/bench/prep_c137_p3_mkv5.py, card 137-P3, result tools/bench/cards/result_137-P3.json).

Failed prediction: "v5 per-build-step counts <= 40 (v3 meta cut)" - measured step 3 = 43 (prep_c137_p3_mkv5.log:26-27).

Claim formed by the card (result_137-P3.json facts 1, 4; open 2):
1. v5 = v4 (163 actions) + 4 inserted actions (tunnels p4_t_fd / p4_t_dt on While #10170 and inner wires p4_w_fd_in / p4_w_dt_in); the 2 crossing wires p4_x_fd / p4_x_dt only changed dst/why. 161 actions unchanged.
2. Both crossings belong to build step 3 (unit U12 'C sinks', plan_ring_p4_v3_meta.json:2078-2111), so step 3 goes 39 -> 43, above the 40-row cap per ring build step (CLAUDE.md split rule 2, decision D-2026-10-01-01).
3. Therefore the failure is a plan-partition budget overflow, not a defect of the plan content; the fix is a re-cut of the step boundaries (e.g. dropping the 2 now-redundant RLE rows -> 41, still > 40; or a unit re-cut U10+U11 | U12..U14B | rest -> 26/40/33, prep_c137_p3_facts.md:29-30).

Also in the same card: the stagesim replay stopped at step 104 (wire_remove_loose_ends p4_rle_x_fd: "`of` 'p4_x_fd' names no earlier crossing row", stagesim.py:1950-1952) because act_wires is only set by FS-border connects (stagesim.py:1865, :1928).

Questions: Is the counting itself right (does the v3 meta cut assign the new tunnel + inner-wire actions to step 3, or should tunnels on #10170 belong to another unit)? Is the 43 an artefact of counting inserted actions that the executor merges? Is the RLE-row stop at step 104 evidence that the 4 inserted actions are the wrong form (pool crossing form vs branch), which would change the count rather than the cut? Name the cheapest offline discriminating check.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**No. The overflow is not the real fault. v5 has a content defect in its action order: the real executor should reject it at action 102, and the RLE stop in the simulator is the visible part of the same mistake.**

### 1. Strongest reason the claim is wrong: v5 breaks the executor's tunnel rule
- `stagexec.compile_plan` requires the two actions right after a `tunnel` to be one wire into it and one wire out of it (`tools/stagexec.py:676-685`). It turns those three actions into one operation (`:699`); otherwise it stops with "tunnel … must be followed by exactly one wire into it and one out of it".
- In v5 the order is: tunnel `p4_t_fd` → wire `p4_x_fd` → RLE `p4_rle_x_fd` → inner wire `p4_w_fd_in` (`plan_ring_p4_v5.json:1463-1498`). The same pattern repeats for `p4_t_dt`.
- That ordering was a deliberate choice: "Inner wire placed AFTER the crossing's RLE so each (wire, RLE) pair stays adjacent" (`prep_c137_p3_facts.md:24`).
- So the executor should stop at action 102. Fact 1 ("161 actions unchanged") is literally true, but two of those "unchanged" actions are wrong: the RLE existed only to clean up the stub that `connect_term_uid` leaves when it crosses a loop border (PD306(b), `docs/d1/ring-p4.md:180-182`). Once the plan uses an explicit tunnel, that reason is gone.
- The simulator's tunnel step (`stagesim.py:1224-1238`) does not check this adjacency. "Replay passed steps 102–103" therefore says nothing about whether the executor would accept the plan.

### 2. Your three questions
- **Is the counting right?** Yes, assigning all four new actions to step 3 is correct. The tunnel and its two wires are one unit for the executor, and the inner wire's target `#10068` only enters the loop body in step 3 (`p4_mv_10068`, `plan_ring_p4_v3_meta.json:2030-2039`). Moving the tunnels to step 2, next to `p4_t_pool`, is not possible.
- **Is 43 an artefact of counting actions the executor merges?** Yes. In executor operations, the old single `connect_term_uid` becomes a single tunnel operation, so step 3 stays at 39 operations, and 37 once the RLEs go.
  - The 40 cap's unit is not fixed in the docs: "edit operations" (`docs/d1/INDEX.md:51`), "actions" (`d1-loop12-17-split-plan.md:2941`), "rows" (`CLAUDE.md:520`).
  - The rule also says "≤ ~40", and PD306(c) already accepts 41 (`ring-p4.md:183`). The gate's hard `<= 40` (`prep_c137_p3_mkv5.py:139`) is stricter than the rule it checks.
- **Does the RLE stop at step 104 mean the form is wrong?** Yes, partly. The two RLEs are left over from the old cross-border wiring. They are what the simulator stops on, and they are the extra actions that break the executor rule. Removing them changes the count (43 → 41 actions) and also fixes the order. It does not change the step boundaries.

### 3. Alternative explanation of the same evidence
Step 3 is not too big. The plan carries two leftover RLE actions, and the gate counts plan actions where the executor counts merged operations. Corrected, step 3 is 41 actions, which the user's "~40" and PD306(c) already allow, or 37 executor operations.

### 4. What would falsify my reading
If `compile_plan` accepts v5 as written (no stop at action 102), my main point is wrong. The reason would be some code path I did not see that lets a tunnel's wires sit apart.

### 5. Cheapest discriminating test (offline, no LabVIEW, seconds)
Run `tools.stagexec.compile_plan` (`stagexec.py:639`) on:
- (a) `plan_ring_p4_v5.json` as it is, and
- (b) v5 with `p4_rle_x_fd` and `p4_rle_x_dt` removed.

Then count the operations per meta step for (b).

**Prediction:** (a) stops at action 102 with the tunnel-group message; (b) compiles, with 37 operations in step 3. This also tells PD306(d)'s v6 replay to check `compile_plan`, not just the simulator.

A few limits on this review:
- I did not run anything; the predictions come from reading the code.
- I made no claims about LabVIEW itself, so no web citations were needed. Every claim is about this project's files, cited by `file:line`.
- The plan-mode write to the plan file was refused (`Write` is disabled in this session), so this reply is the whole review.

## Sources

(extract from answer)

## What was done with it

Cycle 137 judgement, 2026-10-02 (PD307(b), `docs/d1/ring-p4.md`):
- **ACCEPTED:** the two RLEs are leftovers of the `connect_term_uid` form and also break `compile_plan`'s tunnel-group adjacency
  (`stagexec.py:676-685`); v6 drops them (already PD306(b)) and card 137-4 now runs the §5 test: `compile_plan` on v5 as-is (predicted
  stop at action 102) and on v6 (predicted compile, 37 ops in step 3).
- **ACCEPTED:** a stagesim replay is not executor acceptance; every plan replay card from now also runs `compile_plan` (PD307(b)).
- **NOTED, not changed now:** the cap's unit (actions vs merged ops) is unfixed in the docs; PD306(c) keeps counting ACTIONS (the stricter
  unit) with "~40"; the prep gate's hard `<= 40` stays advisory.
