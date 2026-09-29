# brief chat-P4 — speed idea E: MEASURE where a build step's time goes (user 2026-09-29: "측정 후 효과 있으면 적용")

Measurement only. No code change to tools, no LabVIEW, no runner start.

Known from the previous chat (docs/chat-handoff.md §4 item 3): one build step (one row executed by
`tools/stagexec.py` / `tools/stagekit.py` during a stage launch) takes 24–43 s, while the scripting operation
itself (the op VI call) takes 0.3–2 s. The idea: the per-step graph checks (graph read before/after, terminal
table diff, computation_diff, Is Broken? reads, handle reads, …) could be batched once per group of rows instead
of per row.

Measure, from EXISTING logs and code only:
1. Pick the last 3 passing stage launches (e.g. cycles 117 R2, 119 pool, 121 P2a — find their build logs under
   `tools/bench/`). For each, per step: total seconds, and the split into (a) the op call, (b) each named check,
   (c) anything else (COM marshalling, waits, logging). Use the log timestamps; where the log is too coarse, say so
   and read the code path to name which calls run per step.
2. Which of those checks are required PER STEP for correctness (a later row depends on the checked result, or
   the check localises a failure to its row) and which could run once per batch without losing that. Cite the code
   line for each.
3. An upper-bound estimate: seconds saved per step and per 15-row stage if the batchable checks ran once.

Return `result/1`: facts with numbers and file:line citations, and one `open:` line. Do NOT decide whether to apply
it and do NOT write a patch — the chat decides.
