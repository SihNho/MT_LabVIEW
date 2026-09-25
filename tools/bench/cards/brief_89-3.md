# Brief 89-3 (cycle 89 judgement): per-subVI time with LabVIEW's own profiler, measure the route only

Decisions on results 89-1 and 89-2 (both FAIL at B0, no LabVIEW touched):
- **Both instrumentation routes are closed for this cycle.** A flat-sequence wrap needs a verb that moves live nodes
  into frames. The stamp helper needs 10 or more primitives that only `copy_by_index` can make, a staged build of
  several cycles. Escalating 89-2 to Fable medium would not create the missing verbs, so it is not escalated.
- **New route: the built-in profiler (Tools » Profile » Performance and Memory).** It reports time per subVI in situ,
  on the UNMODIFIED `D1_s1_copy.vi`. Every group of `docs/t0-instrumentation-plan.md:96-104` is a subVI: the kernel,
  `check N bead pos`, the filters, the Draw*/Flatten Pixmap VIs, the plots and the save VIs. Nothing is built, and
  rule 1a is untouched.

## This card MEASURES the route and PREPARES the run. It does not run a leg.
1. **Is the profiler scriptable?** External search is MANDATORY (CLAUDE.md §5): NI docs and forums, VI Server
   Application/VI methods, private methods, the `LabVIEW.ini` tokens, and the `vi.lib` / `resource` VIs that back the
   Profile window. Local check: grep `docs/vi-server-ids.json` and our census files. Report every route with evidence
   (URL or file:line). If no scripted route exists, write the negative search record that
   `lv_gui.ps1 -Exception NegativeSearch -Evidence <record>` would cite: `tools/bench/diag_c89_profiler_search.md`.
2. **Can the profiler's result be read as a file?** Its Save to file: format and columns (VI time, # runs, average,
   longest, sub-VI time). And does profiling need a VI setting (debugging enabled) that `D1_s1_copy.vi` has? Read that
   property headless; do not change it.
3. **Write the run plan `tools/bench/profiler_run_plan_89.md`:**
   - EVERY GUI act (window, menu path, button, dialog), each as capture → locate → act → capture → confirm, with its
     predicted observable. Use the scripted route instead wherever one exists.
   - How it combines with the `drive_m8` leg: profiler Start before the VI runs, Snapshot and Save after 120 s, then the
     VI stops. Two legs, at 15 picks and at 8 picks, 90 Hz.
   - The overhead of profiling itself: how you will state it. Compare lost frames with the uninstrumented S1 references
     3,776 (cycle 88) and 3,331/3,161 (cycle 83).
4. Get the plan peer-reviewed ADVERSARIALLY (`peer.ps1 -Agent claude -Role hypothesis`, refute framing). Archive the
   review. Annotate its disposition in the plan file.

Do not open LabVIEW for anything except a headless property read in step 2. No leg is run in this card.
