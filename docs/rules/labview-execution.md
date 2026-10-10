---
type: rules
status: current
date: 2026-10-10
tags: [rules, labview, gui, scripts, stages]
---

# Rules - executing LabVIEW work: GUI gate, references, timeouts, stages, scripts

Restated briefly from `docs/rules/CLAUDE-full-2026-10-10.md` (cited ranges = full wording and quotes). LabVIEW
technique itself: `docs/labview/SKILL.md`.

## GUI, recovery, authority

- **GUI only where scripting is VERIFIED unreachable** (2026-08-31). *Mechanism:* `tools/lv_gui.ps1` refuses
  click/rclick/dclick/drag/wire/keys without `-Exception VerifiedImpossible|NegativeSearch|Approved` plus `-Evidence`,
  and logs each authorized act to `tools/gui_actions.log`. The verified-impossible list names operation CLASSES; each
  use must also show no scriptable alternative. Cost/time is never a reason. Refuse laundering: a too-narrow negative
  search, "only opening it to look", "via GUI if needed" plan clauses (every GUI act individually enumerated in the
  peer-reviewed plan). One execution path at a time. `docs/rules/CLAUDE-full-2026-10-10.md:192-200`
- **Failed batch => RECOVERY_LOCKED.** On an unpredicted result in a scripted batch, state-changing GUI is OFF;
  only diagnostics (screenshots, window lists, reporter reads, Esc). Write a recovery packet (prediction,
  observation, evidence, competing explanation, cheapest discriminating test), get a SUCCESSFUL peer review, resume
  as a NEW batch. Recipes state prediction contracts before execution. `docs/rules/CLAUDE-full-2026-10-10.md:201-208`
- **Save authority:** files under `user.lib\claudeDev` may be saved autonomously, never originals. **Restart
  authority:** restart/kill LabVIEW whenever it is the right fix, no per-incident approval; save valuables first.
  `docs/rules/CLAUDE-full-2026-10-10.md:209-212`

## Reference hygiene and timeouts

- **Close every VI Server reference, and PROVE it by handle count** (2026-09-06). Whoever opens a reference closes
  it (op VIs wire `Close Reference` on every ref; Python releases cached refs on exit and never abandons a COM call).
  `tools/bench/handle_audit.py` attributes growth; `bench_prep.py` reads the handle count before every batch and
  restarts above `HANDLE_LIMIT`; a new op is accepted only if 20 runs leave the count flat (+/-100). Baseline: ~31,500
  handles one minute after a fresh LabVIEW 2026 start - judge growth, not the absolute number. Responsiveness:
  `lv_gui.ps1 -Action ping`. A batch that killed a client is followed by a handle read; a jump = non-result + restart.
  `docs/rules/CLAUDE-full-2026-10-10.md:213-232`
- **Unattended runs: silence is not progress - mechanical.** `tools/hooks/guard_bash.py` refuses a backgrounded
  LabVIEW command unless it runs through `py tools/bgrun.py --max-min N --log <file> -- <cmd>` (kills the tree at the
  deadline, always writes `BGRUN END|TIMEOUT`); foreground LabVIEW commands need a timeout <= 30 s; gscript's
  `_run/_invoke` watchdog caps Run/Invoke. The PROCESS deadline of bgrun is the guarantee. While anything unattended
  runs, a heartbeat checks the process list and the log's age; no new line for longer than one cell = a failure to
  diagnose. `docs/rules/CLAUDE-full-2026-10-10.md:264-279`

## Readers, stages, splitting

- **When a diagnosis is GUESSED twice, build the reader.** The second time a failure class is explained by inference
  rather than read from the machine, the next build is the READER for it. `Wire.Is Broken?` (6371004) is built, but
  only inside the connect ops (use their read-back); `VI.Get Errors` (method 452) is unbuilt and probably unreachable
  over COM. `docs/rules/CLAUDE-full-2026-10-10.md:498-506`
- **Stages are SIMULATED and PRE-RUN OFFLINE before LabVIEW touches them** (2026-09-24). (1) every stage script is
  DRY-RUN first (COM stubbed); (2) an offline PRE-RUN: every row decided, every terminal addressable, rows == plan
  rows; (3) error-cluster/accumulator chains copied from S1 (`RULE-CHAIN-S1`); (4) a failed run invalidates pre-run
  records; (5) every cycle starts by reading the LabVIEW Error List through the GUI, each item double-clicked to its
  location; (6) a move's cut set and reconnect table computed before and checked after; (7) the whole stage simulated
  action by action, finalized at `computation_diff` 0, executed once with a per-step comparison; (8) row content only
  from the finalized plan file. Python computes, Jev picks per-row mechanisms, the LLM designs and takes
  low-confidence rows. *Mechanism:* launch gate in `guard_bash.py` (1/2/4/7), `cycle_runner.py` `errorlist_hook` (5),
  stagekit gates (3/6/7/8); design `docs/stage-simulator-plan.md`. `docs/rules/CLAUDE-full-2026-10-10.md:507-526`
- **Big or blocked work is SPLIT into steps that each SAVE an intermediate artefact** (2026-09-19), everything ahead
  included (EMCCD sync, display). A step is not done until it has left a file under `claudeDev` with its md5; the next
  stage starts from that file (fresh LabVIEW instance when it scripts). `docs/rules/CLAUDE-full-2026-10-10.md:527-537`
- **Granularity:** one saved artefact per natural stage (copy -> structures -> moves -> re-wiring in batches of 10-15
  rows -> census -> final save), not one script per wire; up to ~25 rows on a PROVEN pattern (>= 2 passing launches,
  `stage_prerun.proven_pattern`, X14); ring-buffer P3b/P4/P5 up to ~40 rows per step, each with a full scratch run on
  a byte copy first (D-2026-10-01-01); in-between files of a step that LabVIEW memory forces into several sessions do
  not count toward the cap and are deleted once the step's file is accepted (D-2026-10-02-02/04).
  `docs/rules/CLAUDE-full-2026-10-10.md:538-547`
- **Re-splitting is triggered, not felt:** the same stage failing twice at the same place, or ending without a saved
  artefact => the next cycle's first act is a one-page decomposition plan (sub-steps, file names, pass criteria),
  prior-art-reviewed once, then executed step by step; a full-length retry under a new file name (`_v8`) is forbidden
  (`cycle_runner.py` counts renamed recipes as the same). A new large stage starts with its step and file list in the
  plan. `docs/rules/CLAUDE-full-2026-10-10.md:548-554`
- **A broken-by-design intermediate may be saved by GUI Ctrl+S** (2026-09-22) through `gui_save` with
  `-Exception Approved -Evidence "user 2026-09-22 broken-intermediate save"` (COM `SaveInstrument` hangs on a broken
  VI); never run, never cold-loaded headless; never for originals or the final deliverable. `docs/rules/CLAUDE-full-2026-10-10.md:555-555`
- **At most 6 consecutive broken intermediates** (2026-09-29); then the chain must reach `ExecState` 1 and RUN once.
  Counting starts at ring P2b. Mechanical launch-gate enforcement is owed. `docs/rules/CLAUDE-full-2026-10-10.md:556-561`
- **Reference hygiene is a precondition:** an op that traverses without `Close Reference` is repaired before a staged
  build uses it (20 calls, handle count flat +/-100). `docs/rules/CLAUDE-full-2026-10-10.md:562-564`
- **The work cycle (2026-08-31):** plan and peer-review the plan; write the WHOLE build as one long script with every
  name resolved from `docs/NAMES.md`; execute as a batch; read the report, revise; repeat. No mid-run name discovery.
  `docs/rules/CLAUDE-full-2026-10-10.md:565-572`

## Tooling and scripts

- **Hooks are the mechanical rules** (`.claude/settings.json`): `answer_first.py`, `guard_bash.py` and the others.
  Prose rules fade after compaction; code rules do not - when a rule is broken twice, move it into a hook. Hook commands
  use forward-slash paths. Project hooks also run inside every `claude -p` cell spawned here; gate advisory hooks on an
  env var the spawner sets (`BENCH_CELL`). `docs/rules/CLAUDE-full-2026-10-10.md:573-584`
- **Every script declares its scope** (2026-10-04, PD338): header `# --- / # labview: none|read|build / # hardware:
  none|camera|motor / [# offline-args / # evidence] / # ---` (new files at the TOP; old files at the end so citations
  stay valid). It must be TRUE. *Mechanism:* `tools/hooks/guard_write.py` checks at write time (header, compile,
  honesty vs LabVIEW imports, JSON schema, md5 pins, release slugs); launch gates judge the command by the header
  against the card's flags; a prep card on an unbuilt base returns `WAITING`. `docs/rules/CLAUDE-full-2026-10-10.md:585-597`
- **Scripts call shared functions, never copy them** (2026-10-09): rules in `docs/script-writing.md`, read by every
  material and assignment session; enforced by the written rule and by briefs that ask for calls, not by length.
  `docs/rules/CLAUDE-full-2026-10-10.md:598-602`
- **Patch files with the Edit/Write tools, never a `py - <<'EOF'` heredoc** (heredocs are for read-only one-liners).
  All screenshot/window/mouse/keyboard/checksum operations go through `tools/lv_gui.ps1` (never inline `Add-Type`),
  pre-approved only as `& .\tools\lv_gui.ps1 -Action ...` from the project root. `.claude/settings.json` denies
  Edit/Write on `*.vi`, `*.ctl`, `*.lvlib`, `*.lvproj`. `docs/rules/CLAUDE-full-2026-10-10.md:603-613`
