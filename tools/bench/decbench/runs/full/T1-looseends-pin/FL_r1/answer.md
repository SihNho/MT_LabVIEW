**The build is not at fault; the pinned prediction (24) is a counting error in the offline model, and the evidence only supports that at the level of inference, not measurement.**

**What the record shows**

- The edit did exactly what was simulated: 11 stub wires lost, 0 added (`tools/bench/diag_c116b_scratch.log:279`); census LoopTunnel −13, Wire −11 (`:283`); all 13 shared nets kept their uid, source and kept sinks (`:284`).
- The Error List read is reliable: the window's own count is 53 and all 53 items were read (`tools/bench/diag_c116b_scratch_el.log:27`, `:83`), with no item outside R1's classes (`:115`).
- Only the "loose ends" class moved: 22 read vs 24 pinned, every other class equal (`diag_c116b_scratch_el.log:114`, `:116`).
- The shortfall sits in the "PD230 dangling branches" class: R1 had 7, only 5 are matched now (`diag_c116b_scratch_el.log:113`), while the other loose class stays at 17 (`:112`).

**Root cause (inferred)**

The pin is `24 − 11 + 13 − 2` (`tools/bench/plan_l2r2_make.log:44`). Observed 22 = 24 − 11 + 9, so only 9 of the 13 shared nets produced a *new* loose-ends item, not 11.

LabVIEW reports one "loose ends" item per wire, so a net that was already loose in R1 adds nothing when it loses a tunnel sink. The plan generator found only two such nets, [25438, 25461] (`plan_l2r2_make.log:44`). R1 actually carried 7 dangling-branch items (`diag_c116b_scratch_el.log:113`), and a dangling branch has no terminal, so the terminal-table graph the generator reads (`plan_l2r2_make.log:26-38`) cannot see it. Two more of the 13 shared nets were most likely already loose in R1.

**Most plausible alternative**

Deleting a tunnel made LabVIEW remove the branch that led to it on two nets, leaving no loose end there. Nets 25225 and 25238 are the natural suspects: their tunnels #3644 and #2294 had no inner stub (`plan_l2r2_make.log:26-27`). This would mean the simulator's model of `delete_object` is wrong, which is a tool defect rather than a pin error.

**Cheapest discriminating test**

No new build is needed. Use the R1 Error List read that already exists (each item was double-clicked to its location, as in `diag_c116b_scratch_el.log:97`) and map R1's 24 loose-ends items to wire uids, then intersect with the 13 shared nets listed at `diag_c116b_scratch.log:284`.

- Intersection of 4 nets: the pin undercounted; correct it to 22/53 and launch.
- Intersection of 2 nets (only 25438, 25461): the alternative holds; check 25225 and 25238 in the scratch read for a missing loose-ends item.

I did not open the R1 read file itself, so which two nets are involved is unverified.

ROOT CAUSE: The pin assumed only 2 of the 13 shared nets were already loose in R1, but LabVIEW counts one loose-ends item per wire and two further shared nets most likely already carried terminal-less dangling branches invisible to the plan generator's graph, so 9 rather than 11 new items appeared.
TEST: Map the 24 loose-ends items of the existing R1 Error List read to wire uids and intersect them with the 13 shared nets — 4 hits confirms the pin error, 2 hits points to tunnel deletion removing its branch on nets 25225 and 25238.