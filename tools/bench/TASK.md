---
type: reference
status: current
date: 2026-09-04
tags: []
---

# Benchmark task — identical prompt for every (model, effort) run

This text is handed VERBATIM to each benchmarked subagent. Do not tailor it per model: any
difference in wording invalidates the comparison. The only substitution is `{{RUN_ID}}`.

---

Build a LabVIEW VI from scratch that counts 100 iterations and reports them as a 10x10 array.

**Target file (yours alone — do not touch any other VI):**
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\BENCH_{{RUN_ID}}.vi`

**Requirements**

1. The VI contains a **While loop** that stops itself after exactly **100 iterations** — the stop
   condition must come from the loop's own iteration terminal, not from a timeout or a front-panel
   button.
2. The 100 iteration numbers (0..99, in order) end up in a **10x10 two-dimensional array
   indicator** on the front panel, named exactly `result`. Row-major: element [r][c] must equal
   `r*10 + c`.
3. The VI must be **saved to disk** at the path above and must be **runnable** (unbroken run arrow
   / `ExecState == 1`).

**Ground rules (the project's standing rules apply in full — read `CLAUDE.md` first)**

- Never modify, save, or close-with-save any pre-existing VI. Your target file is the only thing
  you may write. If a save dialog names anything else, answer Don't Save.
- Do not operate any hardware: no motor, no piezo stage, no camera. This task needs none.
- Scripting first. GUI clicking is permitted ONLY where scripting is verified unreachable, and it
  is gated by `tools/lv_gui.ps1` (state-changing actions need `-Exception` + `-Evidence`).
- Useful starting points: `tools/gscript.py` (the op fleet — docstrings are contracts),
  `docs/NAMES.md` (verified terminal/label strings), and the `labview-automation` skill.
- LabVIEW is a single shared instance. Leave it running and responsive when you finish.

**When you are done**, reply with exactly these lines and nothing else:

```
BUILT: <full path>
EXECSTATE: <0 or 1>
NOTES: <one line: the approach you took, or where you got stuck>
```

Do not run the VI yourself and do not claim the array is correct — a separate verifier checks that.
If you cannot finish, still emit the three lines with whatever you achieved.
