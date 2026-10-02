# Card 137-4 facts (offline, 2026-10-02; no tools/*.py edited, no LabVIEW). Inputs: plan v5 91f6476e, graph p3b2b 50595c62
Script `tools/bench/prep_c137_4_mkv6.py`, log `tools/bench/prep_c137_4_mkv6.log` (`BGRUN END rc=1 after 167s`, `:185`).

## 1. v6 = v5 minus the 2 RLE actions (pass 1)
- Output `tools/bench/plan_ring_p4_v6.json` md5 **99586b731001d2345b8def062152d5d2** (`log:6`); 165 actions (v5 167).
- Removed: v5 #104 `p4_rle_x_fd` (of p4_x_fd), v5 #108 `p4_rle_x_dt` (of p4_x_dt) (`log:4-5`).
- Gates (`log:7-10`): v6 = v5 - 2; every remaining action identical to v5 (list equality); no top-level key changed;
  re-read equals built. `stage` still `ring_p4_v3`, `final` false (unchanged from v5).
- Step counts (v3 meta cut, `plan_ring_p4_v3_meta.json` per-action `step`): **{1:33, 2:35, 3:41, 4:36, 5:20}**,
  no action without a meta step (`log:11`); step 3 = 41 > 40 still.

## 2. stagesim replay of v6 on the bed graph (pass 2)
- `stagesim.simulate(v6, graph, out_root=plan_out=tools/bench/sim/ring_p4_v6)`; BASE-FLIPS 6 on [9503, 10177, 29777] (`log:13`).
- Steps 102-109 now: 102 tunnel TFD1 ok, 103 wire p4_x_fd ok, 104 wire p4_w_fd_in ok (cdiff 20->19), 105 tunnel TDT1,
  106 p4_x_dt, 107 p4_w_dt_in ok (`log:115-120`) - the v5 stop at p4_rle_x_fd is passed.
- Step 158 `decide` p4_dec_reseed: "ok cands=1 provisional" (`log:171`); 161 / 163 RLEs ok (provisional).
- **Last step reached 163. Stop: step 164 `wire` id `p4_x_n2_out`** (`log:177-178`): "wire new:IAN1.element ->
  new:EQ2.y: source on diagram -92, sink on diagram 23166 - a border needs a tunnel/register action first",
  raised at `tools/stagesim.py:1366-1367`. final=False, end_cdiff_rows=None, candidates 19, last cdiff 23 (`log:176`).
- Re-written plan `tools/bench/sim/ring_p4_v6/plan_ring_p4_v3.json` md5 6b5f2a21a490a21211e94c1d47964b3e (`log:178`).

## 3. Class of the stop (pass 3; no fix)
- Class: wire from a node on a PLAN-MADE Flat Sequence frame (IAN1 on `new:FS4.f0`, `plan_ring_p4_v6.json:647-652`) to a
  node OUTSIDE that FS (EQ2 on body 23166) = FS frame -> enclosing diagram EXIT. stagesim handles the inbound direction
  only (`stagesim.py:1364-1365` `_fs_border_wire`: `ld and not lf`) and frame-to-frame (`:1362-1363`); outbound falls to
  `:1366`. (This is OPEN (c) of `prep_c137_p3_facts.md:51-52`.)
- Every v6 action of the same class: **only p4_x_n2_out** (v6 #164, `plan_ring_p4_v6.json:2220-2226`). Static scan:
  FS4.f0 holds LRN5, IAN1, IAZ1 (`:634`, `:651`, `:908`); wires with a src among them: p4_w_n2_arr (LRN5 -> IAN1, same
  frame, `:2184-2190`) and p4_x_n2_out. Its RLE p4_rle_x_n2_out (v6 #165, `:2227-2232`) is the last action, not replayed.

## 4. stagexec.compile_plan (pass 5; `stagexec.py:639`)
- **v5 as-is: STOP** at action 102: "tunnel new:TFD1 must be followed by exactly one wire into it and one out of it"
  (`log:180`; `stagexec.py:678-685` looks only 2 actions ahead; v5 has the RLE between wire and inner wire).
- **v6: STOP** at action 158: "op 'decide' has no real executor (decide is not executable)" (`log:181`,
  `stagexec.py:742-743`) - actions 1-157 compiled without a stop, incl. both new tunnel groups; no op count (raises).
  Same stop on the sim-rewritten v6 plan (`log:183`). The only `decide` in v6 is p4_dec_reseed (v6 #158,
  `plan_ring_p4_v6.json:2170-2183`, 3 options, PD298(d), "Counted as 8 ops").

OPEN: (a) p4_x_n2_out (FS4 frame -> body exit) has no stagesim row - which route? (b) p4_dec_reseed must be resolved to
real actions before compile_plan passes - which option? (c) step 3 = 41 > 40 - which re-cut?
