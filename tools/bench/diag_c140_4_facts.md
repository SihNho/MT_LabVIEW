---
type: facts
status: current
date: 2026-10-02
---
# Card 140-4 facts: ring array-write nodes, intended vs real (offline, no LabVIEW). Census: `prep_c140_4_census.log` 8/0
## 1. Census: every ring array-write action, P3a..P4 v15. REAL == INTENDED for 0 of 6
P3a has none (`plan_ring_p3a.json` prims: Wait, Equal?, Increment, Quotient & Remainder, constants). Every row: prim "Replace Array Subset",
donor `$work` #29157, launch read-back class GrowableFunction, label **'Insert Into Array'**, bed terminals array / output array / index /
new element/subarray, all 4 wired in the bed graph (`prep_c140_4_census.log` line given per row).
| action (plan:line) | bed uid, frame | label read-back | bed graph | REAL==INTENDED |
|---|---|---|---|---|
| p3b_ras_num3 (`plan_ring_p3b1.json:214`) | #27928, 27722 | `stage_d1_ring_p3b1.log:149,155` | census:4-8 | NO |
| p3b_ras_num1 (`plan_ring_p3b2a.json:93`) | #28916, 27641 | `launch_p3b2_c135_a.log:89,95` | census:10-14 | NO |
| p3b_ras_transpos (`plan_ring_p3b2a.json:198`) | #29048, 32464 | `launch_p3b2_c135_a.log:168,174` | census:16-20 | NO |
| p3b_ras_rotpos (`plan_ring_p3b2b.json:93`) | #29265, 32464 | `launch_p3b2_c135_b.log:97,103` | census:22-26 | NO |
| p3b_ras_frameidx (`plan_ring_p3b2b.json:174`) | #29316, 32464 | `launch_p3b2_c135_b.log:167,173` | census:28-32 | NO |
| p4_ras_bufdiff (`plan_ring_p4_v15.json:227`) | scratch #29489 only (not in bed, census:34) | `diag_c140_3_scratch.log:219,225` | - | NO |
- The donor was a work copy each time: P3b-1 `D1_ring_p3b1_20261002_060910.vi` (`stage_d1_ring_p3b1.log:146`), P3b-2a `..._p3b2a_20261002_122043.vi`
  (`launch_p3b2_c135_a.log:86,165`), P3b-2b `..._p3b2b_20261002_130007.vi` (`launch_p3b2_c135_b.log:94,164`); op request 'Replace Array Subset' each time.
  So 5 bed nodes are Insert Into Array where the plan says Replace Array Subset; #29048/#29265/#29316 share index wire w28367 (census:19,25,31).
## 2. Replace Array Subset donors
- The original (`main_vi_node_labels.json`) has **23 Replace Array Subset** nodes, all in the bed graph and all wired (census:37, 39-176). **All are 2-D**
  (5 terminals): 20 have index (row)+index (col) (e.g. #23206, census:45-50), #8634 and #29625 have disabled index (row)+index (col) (census:39-44,165-170),
  #31401 has index (row)+disabled index (col) (census:171-176). **No 1-D Replace Array Subset (4 terminals) exists in the original or the bed.**
- Insert Into Array in the original: #29157 (1-D, 4 terminals, frame 29629, census:183-187) and #21554 (2-D, census:177-182). Both wire their index from w31440.
- The Error List line (`errorlist_scratch_c140_3_..._205859.json:316`, "output loop tunnel to an input of Replace Array Subset") gives no uid: UNMEASURED.
- No claudeDev donor VI holding a Replace Array Subset was found: no `*labels*.json` registry entry (grep), no plan donor. The NI-scripting-library VI
  `vi.lib\Erdos Miller\LV-Scripting\Create Replace Array Subset.vi` exists on disk (glob). It is UNMEASURED here (`vi-scripting.md:146`).
## 3. Terminal map (Insert Into Array 1-D -> Replace Array Subset)
- IIA 1-D #29157: array, index, new element/subarray, output array (census:184-187). RAS measured (2-D only): array, new element/subarray, output array,
  index (row), index (col) (census:46-50). By name: array->array, output array->output array, new element/subarray->same.
  **FLAG: 'index' has no measured counterpart** (RAS has index (row)/(col)); 1-D RAS terminal names are UNMEASURED (no 1-D node exists to read).
## 4. Node-swap tools
- Replace in place: `gscript.replace_object` (`tools/gscript.py:3388`, GObject.Replace by Path). It is measured only for subVI -> subVI (all 9 wires kept,
  `docs/m8-real-run-plan.md:225`; `build_kswap_88.log:17`). It takes a VI path, so **a primitive -> primitive swap is NOT measured** and has no route.
- Delete + create + reconnect: `delete_object` (`stagexec.py:3009`, measured `diag_c140_3_scratch.log:76-78`), then `create_primitive_nested`
  (`gscript.py:4782`; needs a RAS donor, and **none in 1-D is measured** (item 2)), then 4 x `connect_term_uid` (`stagexec.py:2953`, measured on these nodes
  `launch_p3b2_c135_b.log:240,270`). After the delete, the bed's existing wires to the node would be dangling (wire deletes `stagexec.py:3005`, measured).
## 5. Item 52 image
- `bd_210806_after11.png`: view scrolled (`bd_changed: true`, errorlist json :545) to an empty region; top-left, a structure cut off by the window edge with a
  dashed purple selection outline (about x 10-105, y 80-115); no icon or label readable. **Selected node NOT identifiable** (UNMEASURED).
