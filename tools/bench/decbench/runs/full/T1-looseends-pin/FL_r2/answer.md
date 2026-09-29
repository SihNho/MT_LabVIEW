**Verdict: the pin is wrong, not the build.** I could not identify from this checkout which 2 wires account for the shortfall; the cause below is the best-supported hypothesis.

**What the evidence shows**

- The edit did exactly what was simulated: 11 stub wires lost, 0 added (`tools/bench/diag_c116b_scratch.log:279`), census LoopTunnel −13 / Wire −11 (`:283`), and all 13 shared nets kept their uid, source and kept sinks (`:284`).
- Only the "loose ends" class differs: read 22, pinned 24; no-source 1, not-connected 20 and other 10 all match (`tools/bench/diag_c116b_scratch_el.log:114`), with no item outside R1's licence classes (`:115`).
- The pin is pure arithmetic, never measured: 24 − 11 + 13 − 2 = 24 (`tools/bench/plan_l2r2_make.log:44`). It assumes each of the 13 shared nets gains one new item when its tunnel sink is deleted, and that the 2 already-loose nets (25438, 25461) stay loose.
- The shortfall is exactly 2 and falls in the class "PD230 dangling branches where a retired SR sink was cut": R1 7, used 5 (`diag_c116b_scratch_el.log:113`), while the other loose class is full at 17 of 17 (`:112`). This attribution is weak, because every loose item carries identical text (`:42-82`).

**Most likely root cause**

On nets 25438 and 25461 the dangling branch that was already loose in R1 is the same branch that led to the retired tunnel (#5752, #5569; `plan_l2r2_make.log:37-38`). Deleting the tunnel removed that branch, so those two nets stopped being loose. The pin counted them as "still loose, no new item" (net 0) when the true effect was −1 each.

**Most plausible alternative**

Tunnels #2294 and #3644 are the only two with no inner stub (inner wire 0, `plan_l2r2_make.log:26-27`). Their nets 25225 and 25238 have several kept sinks (`diag_c116b_scratch.log:284`). Deleting those tunnels may have left no dangling segment, giving +11 rather than +13 new loose nets. This also yields exactly 22.

**Cheapest discriminating test**

No new build is needed. The Error List reader already double-clicked all 53 items to their locations (`diag_c116b_scratch_el.log:88`, gate `every_item_dclicked` at `:97`) and wrote a per-item file (`:89`), which is not in this checkout. Map the 22 loose items to wire uids and check membership of the two pairs:

| Result | Confirms |
|---|---|
| 25438 and 25461 absent, 25225 and 25238 present | root cause |
| 25225 and 25238 absent, 25438 and 25461 present | alternative |

If the saved file does not carry wire uids, one read-only Error List pass on a fresh scratch copy that records the highlighted wire's uid gives the same answer.

In both cases the fix is to correct the pin formula and re-pin to 22 / total 53, not to change the recipe.

ROOT CAUSE: The pinned count of 24 came from an unmeasured formula that treated the two already-loose nets 25438 and 25461 as staying loose, whereas deleting their tunnels most likely removed the dangling branch itself, giving 22.
TEST: Map the 22 "loose ends" items in the existing scratch Error List read to wire uids and check whether 25438/25461 (root cause) or 25225/25238 (alternative) are the ones missing.