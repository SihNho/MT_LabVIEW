# Card 77-4 plan: rebuild the three replay VIs by a stage recipe (m8 plan PD18-PD20, docs/m8-real-run-plan.md:223-274)

Recipe: `tools/recipes/stage_replay_standins.py` (120 lines, stagekit Stage, dry PASS + pre-run 7/0), rows/values/terminal
names from `tools/bench/plans/plan_replay_77.json`. Offline graph of the input: `tools/bench/graph_replay_pane_base_77.json`.

What it builds, all from a copy of `claudeDev\replay\replay_imaqdx_pane_base.vi` (md5 65e999d9, the unowned
IMAQdx Get Image pane, 76-4) in the NI Moving-Objects target (copy_by_index precondition):
1. `replay_imaqdx_get_image_buf.vi`: paths String[] control (default = 10,044 hardlinked frames `G:\m8_replay_frames\fNNNNN.tif`),
   For loop with **N = 1 diagram constant** (gscript.create_const_loop_term 'for_n', measured cold in 77-3/77d 16/0),
   uninitialised shift register + Increment (copied from S1 #1978) in the body, Decrement + Quotient&Remainder (S1 donors)
   at top level, **Q&R.y = 10044 diagram constant** (same verb on a top-level node terminal - NOT measured for this case:
   77d measured only an empty For loop's N; OpCreateConstOnTerm_v0 named by PD20(c) cannot reach a top-level node, so this
   route deviates from PD20(c) wording and is decided by gates A8 (fatal) and cold C2), Index Array -> StrToPath ->
   IMAQ ReadFile (Image In -> Image, Image Out -> Image Out), **error in -> ReadFile -> error out** (PD19(c)),
   Session In -> Session Out, Buffer Number In -> Buffer Number Out. Frame = f(k mod 10044), k = own call count.
2. `replay_get_image_cal.vi`: same, Buffer Number Out = k (Decrement output).
3. `replay_get_buff_image.vi`: copy of `claudeDev\background VIs_COPY\get buff image-lost frames.vi` with ONLY #529 replaced by
   (1) through gscript.replace_object (75-4); gates: callee diff == #529 only, wire-edge diff 0 after the uid remap.
Then a fresh LabVIEW: ExecState 1, constants text '1'/'10044' (read_const), path default 10,044 entries, pane per slot.
The functional tests (PD18(a): pixel-array md5 vs PIL read of the source frame) run afterwards in a separate harness
script reusing `tools/bench/diag_replay_gbtest.py`'s harness/call.

Changes vs the 76-5 build (`tools/bench/diag_replay_standins.py`): panel-default scalars (N via an auto-indexed 1-element
String[], Q&R.y control) replaced by diagram constants, because 76-5/76-6 measured those defaults lost at save/load.
