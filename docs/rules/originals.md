---
type: rules
status: current
date: 2026-10-10
tags: [rules, originals, computation]
---

# Rules - originals and the original's computation

Restated briefly from the frozen full text `docs/rules/CLAUDE-full-2026-10-10.md` (the citation after each entry is
the frozen line range: full wording, the user's quote, the history). Coverage proof: `docs/rules/coverage.md`.

- **Read the rules before doing anything.** Every rule below binds every session and every card. *Mechanism:* the
  short core in `CLAUDE.md` / `AGENTS.md` points here; `docs/START.md` is the reading order. `docs/rules/CLAUDE-full-2026-10-10.md:8-9`
- **Rule 1 - never modify an original file, ever.** Covers every pre-existing `.vi`: the reference VI
  `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`, everything in `zz_LabView VI\background VIs\`, and any
  original opened for inspection. Copies are always fine; derived work goes to
  `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`, never over an original and never into the
  project folder. A `*` in a title bar is not a disk change - only an explicit Save is. A dirty original: close
  without saving, verify the on-disk checksum, continue; answer **Don't Save** to every prompt naming an original
  (opening a hierarchy in a newer LabVIEW relinks and dirties it; one Save rewrites it irreversibly in the newer
  format). After a session that opened originals, audit saved-version bytes offline: `19 00 80 00` = LV2019,
  `26 00 80 00` = LV2026. *Mechanism:* `.claude/settings.json` denies Edit/Write on `*.vi/*.ctl/*.lvlib/*.lvproj`;
  `audit_cycle.py` checks originals untouched; stagekit's version-byte check. `docs/rules/CLAUDE-full-2026-10-10.md:10-24`
- **Rule 1a - never change the original's COMPUTATION.** A behaviour-preserving refactor: only scheduling may change
  (shift registers -> auto-indexed tunnels, parallel instances); the per-bead maths, the parameters that reach it and
  the numbers out must be identical. A change of decomposition can be a change of computation - justify any kernel
  substitution as equivalent or check it numerically. Parameters arrive by the same route with the same values (a
  default fallback is a hidden computation change); whole-array parameters cross loop borders NON-indexed.
  Acceptance is NUMERIC (same inputs -> same X/Y/Z; `ExecState == 1` proves nothing). When a step cannot be shown
  computation-preserving: stop and ask the user. *Mechanism:* `computation_diff` in the stage simulator
  (`docs/rules/labview-execution.md`), numeric acceptance runs. `docs/rules/CLAUDE-full-2026-10-10.md:25-38`
- **Rule 1d - the main VI is in scope, read-only.** Read it when meaning requires it (semantic analysis over
  structure); never modify, never save; prefer headless COM reads over editor windows; read nested structures
  properly (a flat strings dump once hid calibration-cluster fields). `docs/rules/CLAUDE-full-2026-10-10.md:139-145`

Related decisions: `docs/decisions/preserve_the_original_computation.md`,
`docs/decisions/restructure_inside_a_copy_of_the_original.md`, `docs/decisions/user_owns_the_original_vi_state.md`.
