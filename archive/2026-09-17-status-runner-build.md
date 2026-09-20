---
type: archive
status: historical
date: 2026-09-17
tags: [status-narrative, cycle-runner, session-guard]
---

# STATUS narrative relocated 2026-09-17 evening (rule 4: verbatim, never rewritten)

## §0 — this session: the CYCLE RUNNER was built (material session, no LabVIEW, experiment running)

Brief: CLAUDE.md §3 item 2 "Session = one cycle — ENFORCED BY A RUNNER" (user, 2026-09-17, "2번으로 가자.
Opus max"). The rig was running a real experiment throughout, so nothing started LabVIEW.exe, no instrument was
touched, and every self-test used dummy commands (`py -c "print('dry')"`, synthetic hook JSON in a temp dir).

Built and self-tested:
- `tools/hooks/guard_session.py` — PreToolUse (Agent|Task). Refuses the 9th `material`/`log-reader` dispatch of a
  session, and refuses ANY such dispatch once that session has run `tools/retrospective.py`. State:
  `tools/bench/session_<session_id>.json` = `{"dispatches": n, "retro_done": bool}`. `BENCH_CELL` ⇒ exit 0.
  Registered in `.claude/settings.json` under PreToolUse matcher `Agent|Task`.
- `tools/hooks/guard_bash.py` — one addition: `RETRO_RE` (command position; `retrospective_v1.py` deliberately
  cannot match) records `retro_done` for the session and always allows the command.
- `tools/cycle_runner.py` — spawns one fresh `claude -p --model opus --effort max --output-format json
  --permission-mode acceptEdits` per cycle THROUGH `tools/bgrun.py` (`--max-min`, default 180), prompt from
  `tools/cycle_prompt.md`; appends `CYCLE n | start | end | exit | cost | last NEXT line` to
  `tools/bench/cycle_runner.log`; stops on a STATUS `STOP` marker (exit 0), two non-zero sessions in a row or a
  byte-identical NEXT twice (exit 3, notice APPENDED to STATUS), and sleeps to renewal+2 min on a usage limit,
  then RERUNS the same cycle. Flags verified against `claude --help`, not guessed.
- `tools/logclass.py` — `cycle_` registered as machinery at birth, so a judgement session's transcript is never
  read as a build log (the historical `cycle3_toolkit.log` is unaffected: the underscore is required).
- `tools/doc_lint.py` — new L8 WARN: the `status: current` cycle plan must carry a `## Pre-decided` section.
- `.claude/agents/material.md` — apply the plan's `## Pre-decided` answers; one `OPEN:` block per session.

Self-tests: `tools/bench/selftest_guard_session.log` **14/14**, `tools/bench/selftest_cycle_runner.log` **7/7**,
both `BGRUN END rc=0`. `py tools/doc_lint.py` → 1 FAIL (L6, the pre-existing 39 undisposed archives), 5 WARN
(L1, L2c, L3, L7 pre-existing; L8 new and correct — `docs/cycle15-plan.md` has no `## Pre-decided` section).

The stall gate that had to be lifted first: `tools/bench/stall_pid25164_181319.log` was
`tools/bench/preexperiment_guard.py` sleeping 42 min by design (it finished `BGRUN END rc=0 after 2520s`).
Reviewed `-Dual`: `archive/peer/2026-09-17-stall-preexperiment-sleep-codex.md` (ANSWERED 170 s) and
`…-sleep-opus.md` (ANSWERED 452 s). Both refuse the "false positive" framing — at 18:17 the watchdog could not
tell this from a hang, and the defect is a 42-min silent sleep under a 50-min deadline on a safety backstop.
Their remedy (a heartbeat file; drop the CPU delta) is a fleet-wide design change ⇒ judgement, not built.

## §1 — the LabVIEW lock block's run-3 narrative (verbatim from STATUS.md, lines 39–47)

```
# 2026-09-17 16:4x-18:4x material/cycle15-route-B-3: RELEASED, and **EVERY LabVIEW.exe KILLED at 18:4x**
# (`Stop-Process -Name LabVIEW -Force`; verified "NO LabVIEW.exe REMAINS") on the user's notice that an
# experiment starts within the hour. **INSTRUMENTS UNTOUCHED FOR THE WHOLE SESSION** — no camera, no PI, no
# rotor, no magnet, no ASI, no GUI: every run was headless COM scripting on COPIES. F1 and F2 were never run.
# Run 3 = **84 pass / 3 fail, 540 s, ledger UNCHANGED at 63 WIRED / 0 FAILED / 3 NO-ROUTE, ExecState 0,
# NOTHING SAVED** — `Track_v6_D1_GPU.vi` still does not exist and claudeDev holds no scratch leftover.
# ORIGINAL md5 2a78e17c449cacdaf5da389818526859 verified before AND after every run AND after the kill.
# Handles 34,230 → restart → 33,908. Runs + full narrative VERBATIM ->
# `archive/2026-09-17-status-d1-route-b-3.md` §1. Earlier sessions likewise RELEASED -> …-route-b-2.md §1.
```

## §2 — the OPEN block (verbatim from STATUS.md, lines 64–98)

```
## OPEN — one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md` (+ `…-d1-phase-full-…` §0c)
1–3, 5, 9–12 — **archive §9**: PERIODIC auto-reset ungated · autofocus CLOSED (3.6 Hz) · 27 undisposed peer
   archives · startup drives instruments · A2 54/54, A3 112/170 · doc lint 2/4/3. **18 CLOSED by §11h.**
   13/14/15b/17b: ✅ stop measured (`#637` term **648 ← w3457 ← #11639**) · 🔴 `bgrun --detach` misses an
   orphaned grandchild · 🔴 v3's R11 scored the *restart*, so the stop is unproven.
16 · 19–23 · 25–29 · 28b–28f · 30/30b/30c — ✅ ALL CLOSED; text in `…-d1-full-build-5.md`,
   `…-d1-route-b-1.md` §4/§5, `…-status-open-28f-35.md`. Headlines: relocation MEASURED (`WhileLoop 3→6`,
   `Diagram 170→173`, source map **109/109**) · `OpCreateConstOnTerm_v0` 22/0 · 28c was the CALLER never
   setting `UID 2` · §11h: the TIFF writer is not original, F1 uncapped.
32. 🔴🔴 **outcome review: six `OUTCOME-VIOLATION`s, SECOND consecutive time ⇒ the work stops for a re-plan
   with the USER.** Not answerable by a device.
31. ✅ **CLOSED 2026-09-17** — `tools/bench/selftest_stamp_window.log` **15/0**, all three wrong windows covered.
   The stated cause (`stamp()`) was REFUTED; the real ones were `cycle_window()`'s
   `end = dispatch_time(retro_archive(n))` and `--since-hours` being silently ignored. Full text +
   the residue for judgement (revert `stamp()`? E4-2/E4-3 need a recorded closure timestamp) in
   `archive/2026-09-17-status-d1-route-b-3.md` §2.
33–37 — ✅ ALL CLOSED; VERBATIM in `…-d1-route-b-1.md` §2 and `…-route-b-2.md` §2/§3. Headlines:
   `OpConnectNested_v1` built+saved (its "survives RBW" gate RETIRED by §11u) · COM poison fixed 11/0 · the 16
   `from-tunnel` rows are WIRED, every one `Wire.Is Broken? FALSE` · ⚠️ **a `GObject.Move` costs nothing**
   (`Wire 1902→1902`, `LoopTunnel 132→132`) but afterwards EVERY terminal of a moved structure reads
   `is_source` FALSE **including OUTPUT tunnels** — address those rows by INDEX, never by `is_source`.
38. 🔴 **Run 3 changed NOTHING: 63 WIRED / 0 FAILED / 3 NO-ROUTE, ExecState 0, nothing saved**
   (`build_d1_routeb_v0_run3.log`, 84/3, 540 s). BOTH brief decisions were **stopped by the prior-art review
   the brief itself ordered** (`…-priorart-routeb-run3-{codex,opus}.md`, 12 findings, 0 novel), every stopping
   fact confirmed from our own files. **Numbers + the open question: `docs/d1-route-b-plan.md` §11 / §11a** —
   read that, not this line. `SR_QUEUE_AUTHORISED = False`, `TEMP_SINK_AUTHORISED = False`.
   ⚠️ **`Z/dZ` is NOT a wire problem**: the build's own S3-ct reparent of `ControlTerminal #403` zeroes the wire
   (`run3.log:163`, measured in `probe_move_ctlterm_v0.log:134`), and `#2222` **t5** `'Correction Factor'` WIRED
   from an equally-reparented control in the same run (`:369`) — **the variable is the sink's NAME**, and the
   blocker is a reorderable ordering DECISION (`d1-route-b-plan.md:193-194`). `…-zdz-wirecut-opus.md`.
39. 🔴 `VI.Get Errors` 452 **NOT built** — its own `-Dual` prior-art review stopped it on
   `docs/d1-build-plan.md:859-860` ("no diagnostic before F1/F2"), opened and not refutable. Plan kept at
   `d1-route-b-plan.md` §10, NOT AUTHORISED. Run 3's narrowed census: **56 bare named inputs**, still no verdict.
40. ✅ `-Dual` + role `hypothesis`: today **9 of 10 arms ANSWERED** at `-TimeoutSec 780-900`; the one loss was at
   the 180 s default. `peer.ps1` now writes `- **date:** yyyy-MM-dd HH:mm:ss` in every archive header.
```

## §3 — STATUS lock-block narrative, relocated VERBATIM 2026-09-17 22:1x (rule 4, STATUS was 120 lines)

```
# 2026-09-17 18:4x: EVERY LabVIEW.exe KILLED and verified gone; ORIGINAL md5 2a78e17c449cacdaf5da389818526859
# unchanged; `Track_v6_D1_GPU.vi` still does not exist. 20:0x material/cycle-runner: NO LabVIEW AT ALL
# (experiment running) — python + docs only. Run-3 and kill narrative VERBATIM ->
# `archive/2026-09-17-status-runner-build.md` §1 (+ `…-status-d1-route-b-3.md` §1).
# 2026-09-17 ~20:5x: PC LOST POWER (PSU replaced by the user). Checked after reboot, no LabVIEW touched: nothing
# of ours was running at the cut (last bench write 20:07, all self-tests already ended), no zero-byte files,
# STATUS intact. LabVIEW pid 16988 (started 20:56:37) is the USER's — not ours. Rig state NOT re-announced.
```

Addendum measured 2026-09-17 22:03 by the motor-gate session: the LabVIEW instance now running is **pid 13480**
(not 16988 — the PC was rebooted after the PSU replacement), and it **holds COM3 and COM4**: both ports answered
`ACCESS DENIED` to a read-only open from `tools/bench/read_motor_anchor.ps1`. Nothing was killed or retried.
