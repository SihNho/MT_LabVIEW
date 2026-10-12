---
card: 169-a1-2
status: current
date: 2026-10-12
---
# Brief 169-a1-2 (assignment 169-1) - PD406(c)(d)(e): P6-1 re-issue of 169-a1-1 with the prior-art release: review, ONE scratch (the tool's rule), ONE launch, save only on the gates, post-save reads, ONE load_by_vi entry

Plan: `docs/d1/ring-p6.md` PD406 (lines 141-182). Card 169-a1-1 (`tools/bench/diag_c169_a1_1_facts.md`, result BLOCKED, no LabVIEW started) did the offline part and is accepted:
recipe `tools/recipes/stage_d1_ring_p6.py` 85f2615f (rows `rbw_method410` + `delete_object` BuildArray #11261 only, calls the shared functions), the extraction into `prep_c168_a1_2_lib.py` 93e3bffb
(`fs3_check`, `tunnels_read`, `fs4_check`, `cdiff_rowset_diff`, self-test 10/0), dry PASS-UNVERIFIED on exactly A0/A1/R1/D1 (`--graph` 7815af09 file), prerun 15/0 with X10 predicted 678.9 < 680 on the model as is,
`--scratch-required` rc 3. It stopped because `guard_cycle` (tools/hooks/guard_cycle.py:604) refuses a scratch/launch of a recipe with no prior-art review newer than the recipe, and 169-a1-1 had `flags.peers []`.
That hook is obeyed, not bypassed: this card carries `flags.peers ["priorart"]` and runs the review it names. Do NOT edit `tools/hooks/**`; do not set any bypass variable. A second refusal by a hook = RETURN BLOCKED with its text.

## Steps, in this order (stop at the first unexpected result and RETURN with the facts)
1. **Hash first**: write the thin script `tools/bench/diag_c169_a1_2_hash.py` (same shape as `diag_c169_a1_1_hash.py`; card path + mode only) and run `prep_c168_hashlib.check(<this card>, "before")`.
   Drift in a card input or any of the 7 claudeDev VI pins = RETURN. `py tools/protocol.py requires <this card>` must PASS. (Inputs include the recipe 85f2615f and the lib 93e3bffb as 169-a1-1 left them.)
2. **Prior-art review** (the guard_cycle release): `py tools/prior_art_review.py --plan-file <this brief> --slug priorart-c169-p6 --recipe tools/recipes/stage_d1_ring_p6.py` (use its usage text; it is a peer, give it
   `-TimeoutSec`/timeouts per `docs/peer-brief.md`; run it through bgrun if it takes more than 30 s). The review must be NEWER than the recipe: do not edit the recipe afterwards without re-running it. Quote the verdict
   and the archive file it wrote (`archive/peer/...`). Dispose of every objection in the review's disposition block as the earlier priorart cards did (`FIXED:` lines for the ones that are fixed; a fix to the recipe
   means the review must be re-run once; a second objection class = RETURN). A review that calls the recipe not novel / a duplicate of an existing shared function: use the function (docs/script-writing.md), re-run dry
   and prerun, and re-run the review once.
3. **Dry and prerun again only if the recipe or the lib changed in step 2**; otherwise quote the 169-a1-1 logs (`launch_c169_p6_dry.log`, `launch_c169_p6_prerun.log`, md5s). Verdict lines must stay: dry PASS-UNVERIFIED on exactly
   A0/A1/R1/D1; prerun X10 PASS on `memory_model.json` d12bcd3b unchanged; the dry uses `--graph tools/bench/graph_ring_p5s02e_20261012_173009.json`.
4. **`--scratch-required` rc 3 => ONE scratch first** (PD406(c), purpose item 2: that is the tool's rule): launch
   `py tools/bgrun.py --material --max-min 45 --log tools/bench/launch_c169_p6_scratch.log --unverified-card tools/bench/cards/task_169-a1-2.json -- py -u tools/recipes/stage_d1_ring_p6.py --scratch`
   (one LabVIEW client; `labview-lock` per `docs/rules/labview-execution.md`; hardware none). The `--scratch` run is the same rows and gates on a copy that is never saved. Quote ExecState before / after RBW / after delete, every MEM line (<= 675),
   S-1..S-5 PASS/FAIL with evidence and both S-5 differences. The scratch is deleted at close; LabVIEW gone by process listing; `check_launch` / `--scratch-required` re-run and quoted (it should now exit 0).
   Any scratch gate FAIL (including S-1..S-5, which are real gates in the recipe) = RETURN with the Error List and graph in `facts`; no second scratch, no repair, no launch.
5. **ONE launch**: `py tools/bgrun.py --material --max-min 60 --log tools/bench/launch_c169_p6.log --unverified-card tools/bench/cards/task_169-a1-2.json -- py -u tools/recipes/stage_d1_ring_p6.py`.
   Byte copy of 75773b0d named `claudeDev\D1_ring_p6_<ts>.vi`; RBW, delete #11261, ExecState after each, every MEM line <= 675; saved by `Stage.save()` (scripted route, cold re-open check) ONLY if ExecState 1, Error List 0 items,
   F-S3, F-S4 and PD406(b) all pass (all are gates inside the recipe); otherwise the copy is deleted and the Error List returned. Quote md5 of the saved file, size, and that 75773b0d is unchanged.
6. **Post-save reads from the SAVED bytes** - the build run has no memory room for a second whole-VI read (X10 678.9), so run them in a SECOND session: write `tools/bench/diag_c169_a1_2_post.py` (scope header
   `# labview: build`, `RESULT` line; CALL `prep_c168_a1_2_lib`, `prep_c167_a1_1_graphlib.read_graph`, `stagekit.e5_check`, `gscript.exec_state`, `errorlist_check` functions - no paste), give it its OWN dry and prerun
   (quote them). It must not save the file. Prefer reading the saved file itself; if `Stage` can only open a copy, use a dated byte copy named `scratch_c169_post_*.vi`
   (deleted at close) and say so, and then the saved file's md5 is simply re-checked unchanged. It reports: ExecState 1 on reload; graph `tools/bench/graph_ring_p6_<ts>.json` + md5 + the `e5_check` line (base 7815af09, deleted_nodes [11261], deleted_wires the 22 termless F1 uids);
   PD406(b) S-5 re-checked on that graph (`cdiff_rowset_diff` vs 57f33e7c, both differences empty); MEM-after-load line. Then the full Error List `py tools/errorlist_check.py --vi <saved file> --role final`
   (0 error items; the file it writes is kept as the expected Error List `tools/bench/errorlist_expected_D1_ring_p6_<ts>.json`; name and md5 quoted; if it needs `--expected` give the 168 read f71773bc, 0 items).
   The saved file's md5 must be equal before and after these reads (the post-save session does not save). Any FAIL: the saved file STAYS on disk, is NOT adopted, and the card RETURNS the facts.
7. **`load_by_vi`**: ONE entry in `tools/bench/memory_model.json` keyed by the saved file's md5 (`value` = the MEM-after-load line of step 6, `vi`, `cite` file:line), same style as `memory_model.json:38-...`; editor tool; nothing else
   in that file changes. Quote the new md5 of the file.
8. **Hygiene**: work/scratch copies other than the saved file deleted (names listed), VI Server references opened == closed, handle counts quoted, `tasklist` shows NO LabVIEW, the 7 pinned VIs unchanged via
   `prep_c168_hashlib.check(<this card>, "after")`, no original opened, no `tools/hooks/**` edit. Hook gate false positives: `py tools/gate_fp.py log ...` and go on.
9. **Facts** `tools/bench/diag_c169_a1_2_facts.md` (<= 60 lines, every number with a file:line): review verdict + file, scratch result, the three ExecState values of the launch, MEM lines, S-1..S-5 with evidence, saved path + md5 + size,
   post-save ExecState / graph (file + md5 + e5 line) / S-5 / Error List (file + md5 + class counts), load_by_vi entry + memory_model md5, dry/prerun/scratch-required verdicts verbatim, hygiene.

## Not in this card
No bed move (card 169-a1-3 moves `current-bed:` and the INDEX), no STATUS/INDEX/plan edit, no fp drain (card 169-a1-4), no replay, no motor, no camera. Script rules: `docs/script-writing.md`.
