# ATTACK this claim — a static gate failed and I am about to proceed anyway

## The claim you must try to REFUTE

> "`tools/bench/c63_astcheck.log` line `FAIL  3 allow_broken=True is never passed  1 site(s)` is an
> AUTHORISED, information-free failure. The one site is `g.save(T2_FILE, allow_broken=True)` inside
> `tools/bench/diag_c63_connect_perturb.py`, which is the deliberate subject of the measurement. Proceeding
> to run that diagnostic is therefore safe and no rule is evaded."

Context, in full, so you can attack the premise and not only the conclusion:

- `tools/bench/c60c_astcheck.py` is a STATIC gate (AST only, touches no LabVIEW). Its gate 3 refuses any
  script that passes `allow_broken=True`; gate 2 refuses `gui_save` being imported or called. Gate 2 PASSED;
  gate 3 FAILED with exactly 1 site. Every other gate (1, 4, 4b, 5×3, 6, 7, 8, 9) PASSED.
- `tools/gscript.py:2062-2077` — `save(target, allow_broken=False)`: if `exec_state(target) == 0` it either
  raises `refusing to save a BROKEN VI - SaveInstrument blocks forever on one`, or, with `allow_broken=True`,
  diverts to `gui_save()` (`tools/gscript.py:1982-2044`), which focuses the VI's Block Diagram window and
  sends Ctrl+S. `gui_save` is guarded three ways: the path must be inside `claudeDev`, the focused window's
  title must carry the target's own file name, and the save is only believed if the file's mtime moves.
- WHY the diagnostic does this: cycle 62 measured that `OpConnectNested_v1.vi` drives `ExecState` 1 → 0 on an
  UNCHANGED VI after a ZERO-CHANGE idempotent connect (`tools/bench/diag_c62_negctrl.log:24-31`;
  `wire_delta` 0, `Wire` census 1905 → 1905, op error column `''`). Two explanations are open: the op
  perturbs only the READING, or it genuinely breaks the VI. `save()`'s broken-VI refusal makes the cheapest
  separator — "save unconditionally and judge by the COLD reopen" — unreachable, which is why
  `allow_broken=True` is the measurement.
- The run is bounded by `py tools/bgrun.py --material --max-min 25`, which kills the process tree at the
  deadline, so the stated hazard ("SaveInstrument blocks forever") is bounded at the PROCESS level.
- The file written is a fresh scratch copy `claudeDev\DIAG_c63_t2_<stamp>.vi`; the bed
  `claudeDev\D1_s3a_focus_ind.vi` (md5 `eef91c1d91f16b034707e4d1285ca8cb`) is pinned FATAL and never written;
  the project ORIGINAL (md5 `2a78e17c449cacdaf5da389818526859`) is pinned FATAL before and after.

## Already ruled out (do not spend your answer on these)

1. "Edit the gate / rename the argument / wrap the call so the AST cannot see it" — explicitly forbidden by
   the task brief, and it is the laundering pattern CLAUDE.md names. Not on the table.
2. "Set `CYCLE_GUARD_OFF` / `PEER_GUARD_OFF`" — never permitted in this project. Not on the table.
3. "Do not measure at all" — the whole cycle exists to settle this question; the alternative is another
   build on an unreadable `ExecState`, which is what cost cycles 61 and 62.

## What I want from you

1. The STRONGEST reason the claim above is WRONG — specifically, a way in which `save(..., allow_broken=True)`
   → `gui_save` → Ctrl+S can do damage or produce a MISLEADING reading that the three guards and bgrun's
   deadline do not cover. Consider at least: Ctrl+S landing in the wrong window; a modal dialog swallowing
   the keystroke; LabVIEW writing a VI without compiled code (the docstring says a broken VI's file SHRINKS)
   and what that does to a later COLD reopen's `ExecState`; and whether a mtime move can be true while the
   diagram content written is stale.
2. An ALTERNATIVE EXPLANATION of the cycle-62 reading (`ExecState` 1 → 0 after a zero-change connect) that
   this T1/T2 design would NOT distinguish — i.e. a third possibility beyond "perturbs the reading" and
   "really breaks the VI".
3. What would FALSIFY the claim, and the CHEAPEST discriminating test — one I can run in the same
   diagnostic, without building an op and without editing `tools/gscript.py`.
4. Whether a COLD reopen reading `ExecState` 1 would in fact be sound evidence that the op only perturbed the
   reading, or whether some third mechanism could produce a cold 1 on a VI that is genuinely broken in
   memory (and vice versa: a cold 0 on a VI that was fine).

Answer against the files in this project directory; you may read them. Do not ask me to confirm anything.
