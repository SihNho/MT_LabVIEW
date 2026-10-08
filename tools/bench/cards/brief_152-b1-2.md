---
card: 152-b1-2
status: current
date: 2026-10-09
---
# Brief 152-b1-2 - RETRY of 152-b1-1: the same ONE scratch crossing (PD369(d)), case built inside a NESTED Diagram

Why: 152-b1-1 returned FAIL 26/1 before any crossing. Its graph read is DONE and accepted (`diag_c152_b1_1_facts.md` section 1: #30179 = LoopTunnel of a WhileLoop, inner source = SubVI `RingPickSlot_v0` pane 'min slot', outer net has FIVE IndexArray.index sinks, FS #29721 frame has 0 border tunnels).
The run failed because OUR script put the Flat Sequence on the TOP-LEVEL diagram: `struct_copy_nested` accepts only `('Diagram', uid)` as owner (`gscript.py:5064`), the new FS #204 was owned by `('TopLevelDiagram', 3)` (`diag_c152_b1_1_cross.log:61-63`). The classifier reading is `our-script-bug`.
This card is `brief_152-b1-1.md` again; read it first (steps 1, 4, 5 and the report stand). The graph read (step 2) is NOT repeated: cite `diag_c152_b1_1_graph4.log` lines.

## Changes against brief_152-b1-1.md (decided by the judgement side; do not re-decide)
1. **Nest the case.** In s08 the loop, the IndexArray sink and the FS all sit on `Diagram #23166`, which is the body of an outer WhileLoop #10170 (`diag_c152_b1_1_facts.md` section 1(a), (d)). Mirror that: scratch VI = an OUTER While loop; on ITS body `Diagram` put (i) the inner While with SubVI `RingPickSlot_v0`
   and an output LoopTunnel (as 152-b1-1 already built: `diag_c152_b1_1_cross.log:51-59`), (ii) the IndexArray `IA_o` wired to the tunnel's outer face (the one other sink), (iii) a 1-frame Flat Sequence (made by `struct_copy_nested` onto the OUTER body diagram, owner class `Diagram`) holding IndexArray `IA_f`.
   The crossing is `connect_term_uid(IA_f.index, outer face)`, exactly as 152-b1-1 planned. Reuse the 152-b1-1 script, plan, dry and prerun logs as the starting point (copy to `diag_c152_b1_2_*`, names, pins and the nesting only; say which lines changed).
2. **No stage-tool edit.** `gscript.struct_copy_nested` is NOT changed; if the nesting also fails for a reason in a stage tool, RETURN with the log line (that would be a repeated tool function: the next step is a scratch verification of that function, not a third run).
3. **One sink, not five.** Keep the ONE other sink PD369(d) lists; the FIVE-sink fact is a note for the report, and you may state whether the extra sinks could change a source-driven name (prediction only, do not build them).
4. **Launch contract unchanged from 152-b1-1** (stage input = P3b2b bed as the launch contract, `diag_c152_b1_1_facts.md` section 2); the same write globs apply with `b1_2`.
5. ONE scratch launch; the first unexpected result is REPORTED with its log line. Do not re-run inside this card.

## Report `tools/bench/diag_c152_b1_2_facts.md` (<= 40 lines)
As brief_152-b1-1: the scratch case as built (nesting), every face name before/after as a table (source LoopTunnel faces, the other sink's faces, the created FS border tunnel's outer and inner faces), census delta, `Is Broken?`, BGRUN END rc, handles before/after, scratch deleted, pins unchanged, LabVIEW gone, `OPEN:` line. Facts only.
