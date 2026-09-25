# c89-donor-census-hyp

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0232  in 16 / out 8530 / cache-create 80928 / cache-read 680214  (107s, 16 turn(s))
- **date:** 2026-09-26 01:59:27
- **outcome:** ANSWERED (111s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (failed prediction, log tools/bench/diag_c89_donor_census.log, script tools/bench/diag_c89_donor_census.py, card tools/bench/cards/task_89-2.json, result tools/bench/cards/result_89-2.json).

CLAIM (card 89-2's diagnosis, formed after the census): "A per-bead tick-count stamp helper VI (t0_stamp.vi: ring buffer of tick counts, written to a file once at the end, called at 5 points inside the frame loop of D1_s1_copy.vi) cannot be assembled from the existing scripting verbs in tools/gscript.py within a 75-minute card, because its body needs >= 10 primitives (Replace Array Subset, Quotient & Remainder, Write to Binary File, Initialize Array, Equal To 0?, Increment, Build Path, ...) that only `copy_by_index` (gscript.py:1549-1628, one LabVIEW restart per copied primitive) can create, plus a reentrancy setter (VI property 288) that no verb writes; so the in-VI instrumentation route is closed for this cycle."

PREDICTED (card 89-2): the donor census finds every needed primitive in a donor VI and the helper is buildable in one staged run.
OBSERVED: diag_c89_donor_census.log run 2 ended FAIL with first failing line "no donor for Open/Create/Replace File, Close File, Select" (the census encoded its verdict as a gate); run 1 was a TypeError on result_line (patched).

Already ruled out:
- `New VI Object` style-ring primitives: only the ring's own styles are creatable (skill rule 0.2); the primitives above are outside it (docs/toolkit-capabilities.md).
- vi.lib named-terminal VIs as substitutes: `High Resolution Relative Seconds.vi` is droppable (drop_subvi), but buffering/writing still needs array and file primitives.
- Editing D1_s1_copy.vi itself: forbidden by the card (headless read only).

Questions for the adversary: (1) the strongest reason the claim is wrong — e.g. a way to get the helper WITHOUT copying primitives (a vi.lib/express VI that already implements "append timestamps to a file" or "tick count to array", a `.vim`, `Write Delimited Spreadsheet.vi`, `Format Into File`, a Queue/DVR-based buffer built from creatable objects, a VI snippet/clipboard import, the `Merge VI` mechanism, or LabVIEW's own Profile Performance and Memory tool which needs no edit at all); (2) an alternative explanation of the FAIL (the census looked in the wrong donor set; the gate was a census verdict and not a build failure); (3) what would falsify the claim; (4) the cheapest discriminating test.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

I think the claim is wrong. The census tested one proposed body against the wrong set of donors, so it does not show the helper is unbuildable. The strongest reason is that a verb already in `tools/gscript.py` can build the stamp with no copied primitives at all.

## 1. Strongest reason: `build_clfn` removes the need for primitives

- **The verb exists.** `tools/gscript.py:2961-3008` places a Call Library Function Node (CLFN) fully by script. It sets the DLL, the function, the parameter list, the calling convention and `reentrant=True`, all in one LabVIEW session. It was built and used for the GPU path (2026-09-09).
- **A C compiler is already installed.** `tools/gpu/cuda/build.bat` and `tools/gpu/install_gpu_toolchain.ps1` are on disk.
- **A tiny DLL can do the whole body.** It would keep per-site static buffers, stamp with `QueryPerformanceCounter`, and write `site_<n>.bin` every 1024th call and on detach. Then `t0_stamp.vi` needs only a CLFN, two controls and the connector pane. No Replace Array Subset, Quotient & Remainder, Initialize Array, file primitives or Select.
- **The reentrancy setter may not be needed either.** The CLFN could be placed directly at each of the five sites, with no helper VI. A thread-safe CLFN runs in the caller's thread, and the DLL keeps per-site state, so property 288 would not need to be written.
- **It may also answer the Variant-cost question.** An "adapt to type" parameter takes the data wire as a pointer. That keeps the data dependency without the Variant coercion copy the brief wants measured. This is a design point, not something measured.

The claim lists only primitive-copying routes. It never considered CLFN, even though it is this project's own verified verb. Rule 5 names this error: "claims about our own tools are the ones you are most likely to be wrong about."

**Other gaps in the claim:**
- **"One restart per copied primitive" overstates the cost.** `copy_by_index` copies one object per call (`gscript.py:1596-1599`). The restart is per copy *session* (`:1571-1574`). And that one object can be a whole structure with everything inside it.
- **The file primitives are not needed.** The card's own result says Open and Close are avoidable (Write to Binary File takes a path) and Select can be replaced by a case (`result_89-2.json:19`).

## 2. Alternative explanation: the census searched too narrow a donor set

The census searched only two places (`diag_c89_donor_census.py:23-32`):
- `docs/wiki/subvi/*.json`, which the card itself says holds no primitive labels (0 of 14; run 1 printed all zeros).
- `main_vi_node_labels.json`, the main-VI lineage, where matches must equal the label string exactly.

It never looked in `vi.lib`. Stock vi.lib VIs very likely contain Open/Create/Replace File, Close File and Select; `Write Delimited Spreadsheet.vi` is the obvious candidate, though that was not opened here. `copy_by_index` accepts any donor path. So "no donor" means "not in the one VI we indexed", not "no donor exists".

The zero count for Select in a main VI with about 180 diagrams also looks like a label-string mismatch rather than a real absence. That is a guess: `Grep` over the JSON found no `"label": "…Select…"` key, and the stored label for that node was not checked.

The run-2 FAIL is only a list of 3 names the census did not find. No build was attempted (`result_89-2.json:13`).

## 3. What would falsify the claim

Either of these:
- A `claudeDev` test VI with one scripted CLFN calling a stub DLL function, which reaches ExecState 1 and saves by script.
- A vi.lib VI loaded read-only as a donor for `copy_by_index`, which yields Close File or Select.

The claim also fails as a statement about the route. The route is "in-VI instrumentation", and it stays open whenever any buildable stamp exists, whether or not it is the ring-buffer design the brief described.

## 4. Cheapest discriminating tests

- **Test A: no LabVIEW, about 1 minute.** Extend the census to parse `vi.lib\Utility\file.llb` and other vi.lib VIs for the three missing primitives. The project's offline reader can do this, or a `labview-vi-analysis` pass. Any hit refutes "no donor".
- **Test B: one LabVIEW run.** Call `build_clfn` on a scratch `claudeDev\t0_clfn_probe.vi` against a 10-line DLL exporting `void t0(int32 site)`. Pass means ExecState 1 and a stamped file after 3000 COM runs. That shows the helper fits in one staged run and needs no primitives. It is judgement's call whether a C DLL is acceptable as *instrumentation*; it changes no tracking maths, so rule 1a is not touched.

## Routes that do not work

- **Profile Performance and Memory** reports time per VI, not per node. It cannot time groups of inline primitives inside the frame loop.
- **Desktop Execution Trace Toolkit** timestamps subVI events without editing the code ([NI overview](https://www.ni.com/docs/en-US/bundle/labview-desktop-execution-trace-toolkit/page/overview.html)). Its user events come from "Generate User-Defined Trace Event", which NI's help calls a *function*, so it is probably a primitive and not a droppable vi.lib VI ([NI help](https://zone.ni.com/reference/en-XX/help/372641C-01/lvdettmerge/generateusertraceevent/)). I did not check whether LabVIEW 2026 supports the toolkit or whether it is installed here. Treat it as a candidate only.
- **Clipboard or Merge VI import** by scripting is a known workaround ([DMC](https://www.dmcinfo.com/blog/24641/programmatically-replace-labview-vis-using-vi-scripting/)). No verb for it exists here, so it is not cheaper than CLFN.

## What would change my mind

- `build_clfn` fails on a non-GPU DLL.
- The CLFN's per-call cost is larger than the group times being measured.
- Judgement rules that a DLL is not allowed as instrumentation.

Sources:
- [NI – Desktop Execution Trace Toolkit overview](https://www.ni.com/docs/en-US/bundle/labview-desktop-execution-trace-toolkit/page/overview.html)
- [NI – Generate User-Defined Trace Event function](https://zone.ni.com/reference/en-XX/help/372641C-01/lvdettmerge/generateusertraceevent/)
- [DMC – clipboard workaround for placing objects by scripting](https://www.dmcinfo.com/blog/24641/programmatically-replace-labview-vis-using-vi-scripting/)
- [LabVIEW Wiki – VI Scripting](https://labviewwiki.org/wiki/VI_Scripting)

## Sources

(extract from answer)

## What was done with it

Dispatched by card 89-3 (material, fable/low) because `guard_peer` blocked every bench run on the still-owed review
of `diag_c89_donor_census.log` (card 89-2; Jev ladder flipped 01:47 our-script-bug → 01:56 new-problem p=0.802,
`tools/bench/jev_gate.log`). Outcome ANSWERED (111 s, $1.02), which lifted the block. CONTENT NOT ACTED ON HERE — it
is a judgement question: the review says the 89-2 claim is wrong because `build_clfn` (`tools/gscript.py:2968`) +
a 10-line C DLL could stamp tick counts with NO copied primitives (§1), and the census never searched vi.lib as a
donor (§2). Cheapest tests it names: (A) census over `vi.lib\Utility\file.llb` offline, (B) one scratch CLFN probe
VI against a stub DLL. Put under `open` in `tools/bench/cards/result_89-3.json` for the judgement session: whether a
C DLL is acceptable as instrumentation (rule 1a untouched — it changes no tracking maths) and whether route 89-2 is
re-opened before or after the profiler legs of `tools/bench/profiler_run_plan_89.md`.

(Claude fills in)
