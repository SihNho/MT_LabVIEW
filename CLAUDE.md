# LEAN-RULES BENCH - the rules for THIS worktree only (discussion tools/bench/debate/lean-rules-01, user 2026-10-13)

You are ONE Opus session doing the whole task yourself: plan, write scripts, run them, read results, fix, repeat.
There is no judgement / assignment / material split, no task cards, no hand-backs, no hand-back limit, no per-card
re-hash, no dry-run or pre-run gate, no memory pre-prediction, no mandatory peer review, no document layering.
The rule files in docs/rules/ and the plan in docs/d1/ are REFERENCE (facts, past findings, tool usage), not gates.

## Kept - these are hard (hooks enforce 1, 3, 4, 6)
1. **Motors / rig (rule 1b).** Rig state = 조립 (assembled, not in use). Every motion command ONLY through
   `py tools/motor_gate.py`. Start your LabVIEW work with `py tools/motor_gate.py --session start` (limits SET + read
   back) and end it with `--session end` (RELEASED + read back), both quoted in your report. The ASI is not special.
   No experiment is running; if the user's STATUS says 실험중, stop at once.
2. **Originals (rule 1).** Never modify a pre-existing .vi (the reference VI, `zz_LabView VI\background VIs\`, anything
   opened for inspection). Save only under `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\`
   (gscript.save refuses outside claudeDev). Answer Don't Save to any prompt naming an original.
3. **Never edit *.vi / *.ctl / *.lvlib / *.lvproj as files**, never patch files with a shell heredoc (use Edit/Write).
4. **LabVIEW execution:** LabVIEW-touching commands run backgrounded through `py tools/bgrun.py --max-min N --log <f> -- <cmd>`
   (material runs: `--material`) or with a timeout <= 30 s. One LabVIEW client at a time (you are the only one now).
   Close every VI Server reference you open. The RUN-TIME memory stop stays: MEMSTOP 695 MB private
   (`tools/bench/memory_model.json` memstop_mb, read by stagexec; LabVIEW error 2 was measured at 704.8 MB, PD328 in
   docs/d1/tooling.md). The 680 MB PRE-run prediction gate (X10) is NOT required in this arm. End with LabVIEW CLOSED and verified gone (`tasklist | grep -i labview`).
5. **Computation identity (rule 1a)** is the ACCEPTANCE, checked once at the end: same recorded inputs -> X/Y/Z
   bit-identical per frame (criterion D-2026-10-12-01/02 in tools/bench/decisions_pending.json). Never "simplify" the
   original's maths. Loop rules 1c / 1c'' are product requirements (no serial/VISA on the frame path; control signals by
   local variable).
6. **Never route around a refusal** of the hooks above; never set a *_GUARD_OFF variable. Secrets only in env vars.

## Your task
The task file named in your prompt (under `tools/bench/lean_bench/`). Write the report it names and end with one line
`RESULT {...}`.
