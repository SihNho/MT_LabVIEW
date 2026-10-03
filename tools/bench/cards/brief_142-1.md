# Brief 142-1 — build and RUN the first P4 subVI: slot selection (smallest Num > last)

User decision 2026-10-03 (`docs/d1/ring-p4b.md:94-103`): P4 is built WITH SUBVIs. Pure computation goes into small
subVIs, each built in its OWN file under claudeDev and RUN on known values before it is dropped into the bed. This card
builds the first one. The bed (`D1_ring_p3b2b_20261002_130007.vi`) and the P4 session-1 file
(`D1_ring_p4s01_20261002_232547.vi`) are NOT opened for editing and NOT saved.

## What the subVI contains (exactly the planned group of plan v17, nothing more)
Source: `tools/bench/plan_ring_p4_v17.json` (md5 e19d7e14…) actions `p4_gt_last` (Greater?, $work donor #11721),
`p4_f_min` (For loop), `p4_sel_mask` (Select, donor `DonorErrSel_MergeErrors.vi` uid 529), `p4_k_max` / `p4_k_max_found`
(I32 2147483647, donor `DonorI32Max_v0.vi` uid 127), `p4_amm` (Array Max & Min, $work donor #10969), `p4_lt_found`
(Less?, $work donor #10950), and the wires between them in v17 (read them from the plan; do not re-design). The
inputs that come from OUTSIDE this group in v17 become CONTROLS, the outputs consumed outside it become INDICATORS:
expected (verify against v17's wires and report any difference instead of guessing):
- controls: `Num` (1-D I32 array, from the local read `p4_lr_num_a`), `last` (I32, from shift register `SL1`)
- indicators: `min Num` (I32, Array Max & Min `min value`), `min slot` (I32, `min index`), `found` (Boolean, Less? output)
- function: masked[i] = Num[i] if Num[i] > last else 2147483647; min Num / min slot = min of masked and its first index;
  found = min Num < 2147483647.
Names: the file is `claudeDev\RingPickSlot_v0.vi`; control/indicator labels as above (plain English). Connector pane:
inputs left, outputs right; read the pane back after assigning (`conpane` / `conpane_assign`).

Donors from `$work` (the bed) may be taken from a BYTE COPY of the bed, or the same primitive taken from any donor whose
read-back class/label equals the plan's `prim` (the prim gate's rule). No local variables, no references, no shift
registers inside the subVI.

## How (existing tools; check `requires` first)
Start from a copy of `claudeDev\EMPTY_v0.vi` (toolkit-capabilities.md:34). One ≤120-line script on stagekit if the
pattern fits; otherwise a short gscript script. Save by COM (the VI must reach ExecState 1 — it is not a broken
intermediate). Close every reference (handle count flat ±100 across the script).

## Prediction contract (written BEFORE running; machine-checked by the script)
- ExecState 1 after build; node census on the subVI's diagram: Greater? 1, For loop 1, Select 1, I32 constant 2,
  Array Max & Min 1, Less? 1 (plus the 5 panel terminals); prim gate PASS on every created node.
- RUN on these vectors (set controls by COM, Run, read indicators); expected values computed by a Python reference of
  the function above in the same script, compared exactly:
  1. Num = 20 × -1, last = -1 → found False, min Num 2147483647, min slot 0
  2. Num = [0..19], last = 4 → 5, slot 5, True
  3. Num = [20,21,22,3,4,…,19], last = 5 → 6, slot 6, True
  4. same Num, last = 19 → 20, slot 0, True
  5. Num = [-1,21,22,3,…,19] (slot 0 being written), last = 20 → 21, slot 1, True
  6. same Num, last = 22 → found False, 2147483647
  7. Num = [0..19], last = 19 → found False
- Then close LabVIEW, open the SAVED file in a FRESH instance, run vectors 2 and 5 again: same outputs (the file on
  disk is what was verified). LabVIEW closed and verified gone at the end.

## Return
result/1: file path + md5, ExecState, census, conpane read-back, the 7+2 run results (got vs expected), handle counts,
peak MB. At the first result that differs from the prediction, finish the step (LabVIEW closed, files saved/cleaned),
record the facts and RETURN — do not diagnose and retry inside the card.
