---
type: facts
status: current
date: 2026-10-02
---
# Card 140-5 facts: 1-D Replace Array Subset donor `claudeDev\DonorRAS1D_v0.vi` - PASS on attempt 2 (22/0)
Run 2: `diag_c140_5_run.py` (md5 fb9ef7067bf27664d7c84bb1bf3b9e98) -> `diag_c140_5_run2.log` (BGRUN END rc=0 after 73 s, 22 pass / 0 fail).
Run 1: `diag_c140_5_run.log` 15/1 - create_control_nested refuses a top-level node (gscript.py:4149); JEV-LADDER our-script-bug p=0.834,
NEXT-ACTION "patch the script and rerun" (jev_gate.log:4188). Patch: index/new/out via create_control / create_indicator by node index.
## Donor
- **DonorRAS1D_v0.vi md5 e8a9417ce4b75d27e8fd2f172a5dc9cd** (run2.log:34,39), saved by script, ExecState 1 (run2.log:33).
- **RAS node uid #175**, label 'Replace Array Subset' (node_labels, run2.log:29-30), class GrowableFunction (run2.log:29). Not 'Insert Into Array'.
- Terminals[] in order: array t182, output array t185, new element/subarray t188, index t191 (run2.log:29).
- Built by copying 2-D RAS #23206 from a bed byte copy (5 terminals, run2.log:9); wiring a 1-D I32 control to `array` ADAPTED it to
  4 terminals; index (col) t194 disappeared, index (row) t191 became `index` (run2.log:20-21).
- Panel: array #150 (I32 1-D control), index #194, new #236, out #252 (only indicator) (run2.log:27-28).
- Type sigs: array/output array 1-D, index I32 '0005000300', new I32 (run2.log:31).
- Also on the diagram (not part of the donor's use): For loop #43 (N=20, I32 0 const #138) -> Greater? #156.y; Greater?.x is fed from the
  same `array` control (the route that creates a 1-D I32 control, as 139-3). Copy RAS by uid 175 only.
## Run (ONE)
- array 0..19, index 3, new 99 -> out [0,1,2,99,4..19], length 20 (run2.log:35-36).
## Terminal map Insert Into Array #29157 (census:184-187) -> 1-D RAS
- array->array, index->index, new element/subarray->same, output array->same; unmatched: none (run2.log:32). Order differs:
  IIA array/output array/index/new element; RAS array/output array/new element/index (by Terminals[] index, connect by NAME).
## Cleanup
- LabVIEW gone (run2.log:37), bed byte copy deleted (run2.log:38), bed md5 unchanged (run2.log:39). scratch_verify/ras1d_c140_5_213817.json.
