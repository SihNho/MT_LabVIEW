---
type: bench
status: current
date: 2026-10-06
card: chat-B7
---
# livebench: four arms, two live cycles each, in bench-only directories

The user asked on 2026-10-06 for four arms to be run in bench-only directories before anything is applied to the
original. The results will be compared with a ChatGPT (Codex CLI) arm later. The bench answers two questions:
(1) do the rule changes help, and (2) does the change of agent help.

**Only the STARTING state is the same for every arm.** Every arm starts from the same start VI, the same cycle-1 purpose
and the same runner state. After that, each arm's judgement may re-plan and set its own cycle-2 purpose. Nothing
forces or resets it. The user's words: "the session plan may change somewhat with the new rulings, go ahead anyway; I
will look at overall plan progress".

## Arms

| arm | commit | flow | extra |
|---|---|---|---|
| A | master `0fc16ea0` (S1 + early-error hooks E3 + purpose flow A1) | `--flow purpose` (Sonnet 5.5 high assignment session) | - |
| B | `0fc16ea0` | `--flow legacy` (the Opus judgement session dispatches cards itself, 6-dispatch cap) | - |
| A13 | master HEAD after card chat-F2 (+ chat-F3 records). **Fill `arms.json` `arms.A13.commit` first** | purpose | postconditions, test records, generated docs |
| A13K | same commit as A13 | purpose | `karpathy_principles.md` appended to `.claude/agents/material*.md` and `tools/bench/assign/assign_prompt.md` |

Karpathy text: `CLAUDE.md` of github.com/forrestchang/andrej-karpathy-skills. The repository README says the licence is
**MIT**. There is no LICENSE file at the root, and `CLAUDE.md` itself carries no licence line (both read 2026-10-06).
The arm gets a faithful paraphrase with attribution (`karpathy_principles.md`), not the verbatim text.

## Order

1. **A, then B now.** Their worktrees are set up (`setup_A.json`, `setup_B.json`).
2. **A13, then A13K** after chat-F2/F3 land. Steps: put the commit in `arms.json`, then
   `lb_setup.py setup A13 --commit <sha>` and the same for A13K. If F2 has moved a patch anchor, the setup stops with
   `anchor drift`. In that case, update `lb_setup.patches()` and run contain-dry again.
3. Run **one arm at a time**, because there is only one LabVIEW. `lb_run.py` refuses to start while `RUNNING.json`
   exists or while LabVIEW.exe is running.

## Stop and resume

On 2026-10-06 at 11:5x the user said tweezers will be used from about 14:00 on this PC: stop the bench and let it
continue later.

- **One runner process per cycle.** `lb_run` runs `cycle_runner.py --cycles 1` up to 2 times. Between cycles nothing
  is in flight. A cycle that has started is never killed; bgrun's `--max-min 300` is only a last resort.
- **RESUME record** `livebench/<arm>_state.json` (`livebench-state/1`) holds:
  - cycles finished, counted from the arm's own runner-log `CYCLE` lines after the start state's cycle 143, so it
    survives a crash;
  - the next cycle;
  - the last accepted VI (path and md5, from adopt/1);
  - the worktree HEAD.
  A second `lb_run.py run <arm>` continues from the next unfinished cycle. Once 2 cycles are finished, it only
  collects.
- **STOP SAFETY**, checked before every cycle by `lb_state.may_start_cycle`, which has a 7-case self-test. A cycle is
  not started when any of these holds:
  - the main or the arm STATUS `rig-state:` is anything other than 조립 (for example 실험중);
  - LabVIEW.exe is running;
  - with `--not-after HH:MM`, now + the cycle length would pass the cutoff. The cycle length is the arm's longest
    measured cycle, never less than 90 min (cycles 142/143 took 87/88 min).
  A refusal prints `RUN-STOPPED … (resumable)` and starts nothing.
- `py tools/bench/livebench/lb_state.py status <arm> [--not-after HH:MM]` shows the state and whether a cycle may
  start. It writes nothing.
- **No arm was started on 2026-10-06** (user).

## First live launch (2026-10-06 12:07): it stopped in 31 s, and these are the fixes

The record is in `failed_launch_A_20261006_1207/`. Nothing ran: no LabVIEW, $0.

1. **ERRORLIST FAIL 'no bed: None'.** The worktree STATUS still named the main bed (`current-bed:
   D1_ring_p3b2b_...`), and that file is not in `claudeDev\bench\A`.
   - Fix: every arm's STATUS now carries `current-bed: D1_ring_p4s02_20261003_110001.vi`, which resolves to the byte
     copy in `claudeDev\bench\<arm>` (md5 84cac487).
   - The main repo's saved Error List read for that md5 (`errorlist_D1_ring_p4s02_20261003_110001_20261003_110836.json`
     + `_raw` + `errorlist_expected_…`) is byte-identical in the worktree.
   - `lb_setup.py hooks-check <arm>` runs the runner's own `errorlist_hook`, with `subprocess.run` made to raise so the
     GUI read cannot start. Result: verdict OK through REUSE in A and in B (`lb_hooks_A.log`, `lb_hooks_B.log`).
     `gates_due` also runs clean.
   - **Inherited due state is cleared** (chat decision 2026-10-06), identically in every arm, through each gate's own
     discharge record. No review is faked. `lb_setup.py clear-due <arm>` does this; `setup` does it for new arms.
     - Violations: a dated `DECISION: no-device` block per due slug in the worktree's `docs/violation-decisions.md`
       (device-failed, repeated-failure-class).
     - gate-fp: the worktree's open queue rows (fp-34) are set to `livebench-deferred`.
     - Outcome and retro-debt were due only because `git worktree add` stamps every file with the checkout time. Each
       worktree file that is byte-identical to main gets main's mtime back (13,133 files).
     - What was cleared is recorded in `start_state/manifest.json` `cleared_due`.
     - `hooks-check`: all four are not due in A and B (`lb_hooks_*.log`, 6/0).
     - The main repo still owes them separately.
2. **The POST gate 'main tree unchanged' failed** because other writers change main concurrently (chat-F2's commits,
   the chat's STATUS edits).
   - The gate now flags only main-tree paths this ARM could have caused (`lb_state.arm_caused`): a path a worktree
     fence logged, a `livebench_runner` log, or a basename carrying one of the arm's cycle numbers (>= 144).
   - Everything else is printed as INFO.
   - Self-test cases S8 to S10 (in `lb_state.py selftest`, 10/0).
   - The claudeDev-outside-bench check is unchanged.
3. **The worktree reaper edited inherited logs.** `bgrun_reap` marked two copies of MAIN-repo logs that the
   worktree inherited at its base commit as KILLED. Only the worktree copies were edited; main's files were
   untouched.
   - Patches R1/R2: the worktree's reaper skips every log listed in `.livebench/inherited_logs.json` (4,417 names,
     written at setup).
   - Dry `reap()` in worktree A: 0 scanned, 0 marked.
4. `lb_setup.py repair <arm>` applied 1 to 3 to A and B. It reset each worktree to its baseline, which drops the
   failed launch's runner lines. Each fix is committed in the worktree, and `setup_commit` is moved: A `0beeb250`,
   B `20f552bb`. New arms get all of it from `setup`.

## Line endings (chat, 2026-10-06 19:5x): the worktrees were CRLF, so every md5 pin broke

- **Cause.** The system git config sets `core.autocrlf=true` (`C:/Program Files/Git/etc/gitconfig`), so files git
  checked out into a worktree were CRLF. Main's working copies are mostly LF, because tools write them; main has
  7,154 LF and 4,222 CRLF .py/.json/.md files.
- **Effect.** Every md5-pinned record differed. Arm A lost cycle-1 round 3 and cycle-2 round 1 to
  `selftest_c134_1_dry` T2a (`V6_bench/A/tools/bench/cards/result_145-b1-2.json`).
- **Fix, per worktree only** (`lb_setup.set_eol_config`, `sync_bytes`):
  - `extensions.worktreeConfig=true` and `git config --worktree core.autocrlf=input`. Git then never writes CRLF in
    the worktree, and a CRLF working file still compares clean against its LF blob. Main's effective `core.autocrlf`
    stays `true`, and main's checkout is untouched.
  - Why not `autocrlf=false`: main's CRLF-on-disk files would then show as modified, and the runner would commit them
    as whole-file changes.
  - `sync_bytes` copies main's working-copy bytes over every tracked file whose content equals main's up to line
    endings. Files the setup changed, or that main changed after the base commit, keep their content and take main's
    line-ending style.
  - It then rebuilds the index from HEAD (`read-tree` + refresh), because the index cached the CRLF sizes.
  - GATE: every main-equal file is byte-identical (B: 17,220 files, 212 recipes, 0 mismatches), and git status is
    clean.
  - New arms are checked out with `--no-checkout`, then configured, then populated.
- **B was repaired** (`lb_setup.py repair B`). It has not run.
- **A is NOT touched** while its cycle 2 runs. After A's cycle 2 ends, the chat runs:

  ```
  py tools/bgrun.py --material --max-min 30 --log tools/bench/livebench/lb_reset_A.log -- py -u tools/bench/livebench/lb_setup.py reset-arm A --yes
  ```

  - Without `--yes` it only prints the plan.
  - It refuses while `RUNNING.json` names A, or while LabVIEW runs.
  - It keeps run 1 as evidence:
    - worktree `V6_bench/A_run1_<stamp>` (git worktree move), branch `bench/A_run1_<stamp>`;
    - `claudeDev\bench\A_run1_<stamp>`;
    - `livebench/run1_A_<stamp>/` (A_state, A.json, setup_A.json, logs).
  - Then it runs `setup A` from `0fc16ea0`: the same start VI, the same purpose, A_state 0/2, every fix (bed, Error List
    copies, due clear with mtime restore, both fences, ignored sim files, line endings). After that it runs
    `hooks-check A`.

## How to run (from the main project root)

```
# offline (labview none) - already done for A and B
py tools/bgrun.py --material --max-min 10 --log tools/bench/livebench/lb_setup_<arm>.log -- py -u tools/bench/livebench/lb_setup.py setup <arm>
py tools/bgrun.py --material --max-min 20 --log tools/bench/livebench/lb_contain_<arm>.log -- py -u tools/bench/livebench/lb_setup.py contain-dry <arm> [--counterfactual]
py tools/bgrun.py --material --max-min 30 --log tools/bench/livebench/lb_stub_<arm>.log -- py -u tools/bench/livebench/lb_setup.py stub <arm>
# live (labview build, hardware motor) - a card with those flags, one arm at a time
py tools/bgrun.py --material --max-min 420 --log tools/bench/livebench/lb_run_<arm>.log -- py -u tools/bench/livebench/lb_run.py run <arm> [--not-after HH:MM]
py tools/bench/livebench/lb_run.py collect <arm>      # re-collect only
```

## What each arm is

- **Worktree** `G:\...\2. Tracking\V6_bench\<arm>` on branch `bench/<arm>`, outside the project folder. The runner's
  per-cycle `git add -A` commits land on that branch only.
- **Setup commit** "livebench setup arm X" on top of the arm's base commit. It contains:
  - The start state from `start_state/`, frozen once from the main working tree by `lb_setup.py snapshot`:
    STATUS.md, next.json, cycle_runner.log (last cycle 143), judge_ladder.json, the retro-seen list and the
    heartbeat. `motor_session.json` is removed, as it is absent in the main tree.
  - STATUS STOP markers neutralised, plus a one-line arm banner.
  - The git-IGNORED stagesim step files the start state needs (`arms.json` `ignored_inputs`: ring_p4 s03v18,
    s03v18a, v18, s02v18, s02v18a: 112 files). They are byte-copied, not committed. Without them, the worktree's dry
    run of the cycle-1 recipe stopped with "21 step file(s) missing" (first contain-dry), while the main tree's dry
    passed.
  - `.claude/settings*.json` hook paths re-pointed to the worktree (11 hooks).
  - The patches below.
  - The write fence `.livebench/sitecustomize.py`, and the shell fence `.livebench/guard_fence.py`. For A and B the
    shell fence was added by `lb_setup.py fence <arm>` in a second worktree commit. `setup_<arm>.json` `setup_commit`
    = that commit, which is the metrics baseline.
  - Memory: `lb_run` copies the main project's Claude memory into the worktree's project key by default (chat decision:
    the arms see MEMORY.md as live cycles do).
- **next.json** is the fixed cycle-1 purpose, the same for every arm: "P4 session 3 (plan_ring_p4_s03v18.json
  da66a030): ONE scratch on a byte copy of D1_ring_p4s02_20261003_110001.vi, adopt on full PASS…" (md5 in
  `start_state/manifest.json`).
- **LabVIEW outputs** go to `claudeDev\bench\<arm>\` only.
  - `lb_run` byte-copies the start VI there first: `D1_ring_p4s02_20261003_110001.vi`, md5 `84cac487…`.
  - Op VIs, donors and the pinned plan base are still READ from the claudeDev root. They are read-only and md5-pinned.
- **Patches** live in the worktree only. They are anchor-checked, compile-checked and listed in `setup_<arm>.json`:
  - `gscript.CLAUDEDEV_OUT` = env `LIVEBENCH_CLAUDEDEV`. `save`/`gui_save` are fenced to it, and the hygiene scratch
    goes there.
  - `gscript.PROJECT` = the worktree, so `lv_gui.ps1` and the GUI log stay in the worktree. `ORIGINAL` still names
    the main original.
  - stagekit: the Stage work copy, `scratch()` and the H6 listing use the arm folder.
  - stagexec: `adopt` accepts the arm folder, and a bare reference name looks in the arm folder first.
  - errorlist_check: the bed lookup and the Error List scratch use the arm folder.
  - stage_prerun: the launch gate requires the work copy in the arm folder.
  - wiki_build: its scratch goes to the arm folder.
- **The write fence** is a Python audit hook loaded in every Python process of the arm through PYTHONPATH.
  - It REFUSES any file write under the claudeDev root outside `bench\<arm>`, and any write into the main project.
  - It allows writes to gscript's Moving Objects fixture, which gscript restores itself.
  - Every classified write is logged to `<worktree>/tools/bench/livebench_writes.jsonl`.
- **The shell write fence** `.livebench/guard_fence.py` is registered FIRST in the worktree's PreToolUse
  Bash|PowerShell hooks. It is in the worktree only, never in the main repo (chat decision 2026-10-06).
  - It REFUSES (exit 2) a Bash/PowerShell command that writes into the claudeDev root outside `bench\<arm>` (another
    arm's folder included) or into the main project.
  - What counts as a write: output redirects; the destination of cp/Copy-Item/robocopy; any path of
    rm/mv/Remove-Item/Set-Content/Out-File/New-Item/mkdir/…; git write subcommands on main; `[IO.File]` writes.
  - Reads pass, and so does copying FROM the root INTO the arm folder.
  - Refusals are logged with `event: shell`, and lb_collect counts them (`containment.shell_refused`).
  - Self-test (`py .livebench/guard_fence.py --selftest`): 11 refuse + 8 allow + 2 hook-protocol cases, 21/0 in A and
    21/0 in B (`lb_fence_A.log`, `lb_fence_B.log`).
  - It cannot resolve shell variables. The Python fence and `lb_run`'s before/after snapshots of the claudeDev root
    and the main tree (checked after every cycle) remain the backstop.
- **Runner**: `cycle_runner.py --cycles 2 [--flow legacy]`, run from the worktree with no supervisor. The motor-limit,
  Error List and LabVIEW-close hooks stay on.

## Metrics: `livebench/<arm>.json` (schema `livebench/1`; the same schema for a future Codex arm)

**PRIMARY: `plan_progress`.** This is progress on the WHOLE project plan in `docs/goalmap.json` (R1..R9, M1..M11), not
only the ring buffer. All of it is read mechanically:
- `goalmap_changes` and `goalmap_current`: requirement and milestone status at the setup commit versus the end.
- `per_cycle`: each cycle's purpose (act and goal ids from the assign cards, or from the runner's NEXT line), plus
  `purpose_met` and `delivered`.
- `replans`: a cycle whose goal ids differ from the previous one. A re-plan toward another milestone is allowed. It
  counts if it advances the goal map.
- `cards_by_goal`: PASS and other cards per goal id, from each card's `advances`/`unblocks`.
- `critical_path`: M3, M8, M4, M5, M6, M7, M11, M9, M10, with start and end status and PASS cards for each.
  `next_open_milestone` is the first of these that is not done.
- `m3_detail`, the detail under M3:
  - P4 v18 ops adopted, of 190 (baseline 58 = s01 24 + s02 34).
  - P4 sessions adopted, of 6 (baseline 2).
  - Adoptions per ring step (P4/P5/P6), with each adopted file's gates (pass and log_fails, required gates).
  - Plan-file diff (`plan_*.json`, `docs/d1`, goalmap) against the start.

**Secondary:**
- Per cycle: wall time, exit code, runner $, assignment rounds, hand-backs and their trigger, and the hook lines.
- `usd`: every `claude -p` envelope in the worktree's logs (deduplicated by session_id) plus the `**cost:**` lines in
  `archive/peer`.
- `cards`: tasks issued in the window, by status (PASS/FAIL/WAITING/BLOCKED/NO-RESULT), first_fail classes, retries
  and escalations.
- `early_catches`, read from the arm's Claude transcripts (`~/.claude/projects/<mangled worktree>`): guard_write
  `WRITE-CHECK` and `BLOCKED by tools/hooks/guard_*.py` by class, plus `guard_card.log` REFUSE lines.
- `labview_runs`: bgrun launches whose script declares `labview: read|build`, plus Error List hook runs.
- `saved_vis` with md5s.
- `changes_outside_claudedev`: files and lines by area, tools created, recipes created.
- `containment`: fence log, refusals, and the before/after snapshots.

A source that does not exist for an agent is reported as `null` in `sources`, never as 0. For example, a Codex arm
has no Claude transcripts.

## Evidence so far (card chat-B7)

- `stub_A.json`: the whole runner ran 2 cycles on arm A's setup, with stub sessions, a fake claudeDev root in %TEMP%,
  and no LabVIEW or motor. All 54 gates passed (`lb_stub_A.log`, rerun with the shell fence installed). The stub worktree was removed afterwards.
- `contain_A.json` / `contain_B.json` (`lb_contain_A.log` 10/0, `lb_contain_B.log` 8/0): `stage_prerun.dry` of
  `stage_d1_ring_p4_s03v18_scratch.py` in each worktree PASSES.
  - The Stage work copy and its save resolve to `claudeDev\bench\<arm>\D1_ring_p4s03_<ts>.vi`.
  - `gscript.CLAUDEDEV_OUT` is the arm folder.
  - No write resolves elsewhere under claudeDev or into the main project.
  - The counterfactual dry on the unpatched main tree puts the same work copy in the claudeDev ROOT, which shows the
    patch is what moves it.
- `lb_state.py selftest` 10/0. `lb_state.py status A|B --not-after 13:40`: 0/2 cycles finished, next cycle 1.
