---
card: 169-a1-3
status: current
date: 2026-10-12
---
# Brief 169-a1-3 (assignment 169-1) - PD406(e): post-save reads of the SAVED P6-1 file, retry of 169-a1-2 (script bug in the post script's own DN gate), Error List --role final, ONE load_by_vi entry

Plan: `docs/d1/ring-p6.md` PD406. Card 169-a1-2 (`tools/bench/diag_c169_a1_2_facts.md`) built and SAVED the file:
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p6_20261012_212645.vi`, md5 c2d9c13cb40c0a5cab7433896d1df157, 511194 B
(record `tools/bench/launch_c169_p6.json["saved"]`), all pre-save gates S-1..S-5 PASS. Its post-save read failed ONLY on the post script's own gate
"DN exactly one node removed": `diag_c169_a1_2_post.py:69-71` took every non-Wire object of 7815af09 absent from 57f33e7c, which includes the 3 Terminal
objects of #11261 (11267, 11270, 11273) -> [11261, 11267, 11270, 11273]. A script bug, not a machine claim (E5 passed with [11261]; jev_gate.log:7477 `our-script-bug`).
This card is the ONE retry. The saved file is read only. There is NO launch, NO scratch of the recipe, NO save. Do NOT edit `tools/recipes/stage_d1_ring_p6.py`
(its prior-art review is bound to its sha) or `tools/hooks/**`; no bypass variable.

## Steps (stop at the first unexpected result and RETURN with the facts)
1. **Hash first**: thin script `tools/bench/diag_c169_a1_3_hash.py` (same shape as `diag_c169_a1_2_hash.py`, card path + mode only) running `prep_c168_hashlib.check(<this card>, "before")`.
   Drift in a card input or in any of the 7 claudeDev VI pins = RETURN. The saved file md5 is checked by the post script (step 3) and in `facts`. `py tools/protocol.py requires <this card>` must PASS.
2. **Patch the DN gate** in `tools/bench/diag_c169_a1_2_post.py` (editor tool; patch in place, do not copy the file). Fix: the deleted NODES are the non-Wire objects of 7815af09 absent from 57f33e7c
   that are NOT owned by another absent object (a Terminal object belongs to its node: use the owner field the stored graph objects carry; read the graph JSON to see its name) -> expected `[11261]`.
   Rules `docs/script-writing.md` 10-15 apply: no new option; ONE `assert`-based self-check for the new selection that runs with the script (replay the two stored graphs: result == [11261]; and a one-row edge case:
   a graph pair with no difference gives []); an in-place `# shortcut:` comment if the fix has a known limit; the result facts carry one `skipped: ...` line. Header "evidence:" line names this card too. The post script's
   prediction contract line for DN is updated to what it now checks.
3. **Own dry and prerun** of the patched post script (`py tools/stage_prerun.py` per `docs/rules/labview-execution.md`; the 169-a1-2 forms are in `diag_c169_a1_2_post_dry2.log` / `diag_c169_a1_2_post_prerun2.log`, quote the
   commands from there; the `--graph` file for the dry is the one the earlier post dry used). Verdicts quoted. Then ONE run through
   `py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c169_a1_2_post.log -- py -u tools/bench/diag_c169_a1_2_post.py` (the previous log is kept first as `diag_c169_a1_2_post_run1.log`, copy by editor tool or `py` copy; do not delete it).
   Expect: ExecState on reload 1; DN [11261]; E5 ok; G1/FS1; graph `tools/bench/graph_ring_p6_20261012_212645.json` rewritten (it is the same bytes if the read is deterministic: quote old fbc7b7ee vs new md5); S-5 30 vs 30, both differences empty;
   every MEM line <= 675; saved md5 c2d9c13c unchanged; the read copy `scratch_c169_post_*.vi` deleted.
4. **Full Error List of the SAVED file**: `py tools/errorlist_check.py --vi "<saved path>" --role final` through bgrun (use its usage text; one LabVIEW client at a time, after step 3 returned and LabVIEW is gone by process listing).
   0 error items required; the file it writes is kept as the expected Error List `tools/bench/errorlist_expected_D1_ring_p6_20261012_212645.json` (name + md5 + class counts quoted; if it needs `--expected`, use the 168 read
   `tools/bench/errorlist_D1_ring_p6rbwd_20261012_205248.json` f71773bc, 0 items). The tool must not save the file (saved md5 re-checked after).
5. **`load_by_vi`**: ONE entry in `tools/bench/memory_model.json` keyed by the saved md5 c2d9c13cb40c0a5cab7433896d1df157 (`value` = the MEM-after-load line of step 3 [169-a1-2 measured 600.4 at `diag_c169_a1_2_post.log:27`; use the
   new run's own line], `vi`, `cite` file:line), same style as the existing `load_by_vi` entries; editor tool; nothing else in that file changes. Quote the new md5 of the file. Do this only if steps 3 and 4 PASS.
6. **Hygiene**: no scratch left in claudeDev except the saved file (names listed), refs opened == closed (all runs), `tasklist` shows NO LabVIEW, the 7 pinned VIs unchanged via `prep_c168_hashlib.check(<this card>, "after")`
   (inputs `memory_model.json` is expected to drift ONLY by step 5; `docs/script-writing.md` pinned at 3583b9f3), no original opened, no `tools/hooks/**` edit, STATUS/INDEX/plan untouched.
   Hook gate false positives: `py tools/gate_fp.py log ...` and go on.
7. **Facts** `tools/bench/diag_c169_a1_3_facts.md` (<= 50 lines, every number with a file:line): patch (file:line), self-check result, dry/prerun verdicts verbatim, post-save values (ExecState, DN, E5, graph md5, S-5, MEM), Error List
   (file + md5 + class counts), load_by_vi entry + memory_model md5, hygiene, a `skipped:` line.

## Not in this card
No bed move (next card), no STATUS/INDEX/plan edit, no fp drain (tooling card), no recipe edit, no launch, no save, no replay, no motor, no camera.
