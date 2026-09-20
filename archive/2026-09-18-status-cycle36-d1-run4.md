---
type: archive
status: archived
date: 2026-09-18
tags: [status, relocation, cycle36, d1, route-b]
supersedes: nothing
---

# STATUS narrative relocated at the close of cycle 36 (rule 4, STATUS was 153 lines)

Relocated VERBATIM by the cycle-36 MATERIAL session immediately after the D1 route-B v1 run 4 dispatch
returned (`tools/bench/build_d1_routeb_v1_run4.log`, `BGRUN END rc=1 after 1713s`), which is the point
STATUS NEXT (user, 2026-09-18 21:3x) allowed doc relocation to happen. Nothing is rewritten; STATUS keeps
one line and a pointer per item.

## §1 — STEP 0, the two one-line REPAIRS (NOT DONE in cycle 36: the user's order put the D1 dispatch first)

> 🔴 **STEP 0 — two one-line REPAIRS, or this session pays the same tax the last one did** (retrospective-cycle35,
> `VIOLATION: repeated-failure-class | loss_min=16 | loss_usd=5.78`, **DISPOSED**): cycle 35 spent its first 20
> minutes and $5.78 buying two paid reviews to clear two machinery faults whose repairs were already on file.
> (i) `tools/lv_stallcheck.ps1` — bind the command-line read to `(pid, CreationDate)` and skip leaves with no bgrun
> log, so a benign sleep-poller stops being labelled a STALLED LabVIEW client and `guard_peer` stops blocking the
> build; (ii) `tools/bgrun.py` — set `BGRUN_LOG`, the one line that makes `audit_cycle` A2/A3's self-exemption work
> (OPEN 42), and while in there fix (e) below. **Both are REPAIRS of existing devices, so Pre-decided 2 does NOT
> block them** — the same ground on which C7 was repaired this cycle. Each ships with its own test; an unverified
> patch to gate machinery is worse than the fault. Run `py tools/violations.py` first: if `repeated-failure-class`
> has reached 3, record a FINDING in `docs/violation-decisions.md` — the device threshold stays SUSPENDED (line 10),
> and a repair is not a device.

## §2 — STEP 1, the BASELINE `ExecState` read — ✅ **DONE AND RUN in cycle 36**

The one line was already restored in `tools/recipes/build_d1_routeb_v1.py` and run 4 executed it:
`S1 BASELINE ExecState of the untouched working copy = 0 — read COLD (no preload) … UNREAD`
(`tools/bench/build_d1_routeb_v1_run4.log:25`), and the preloaded re-read of the LIVE copy before the delete
returned **1** (`:337`). The original block, verbatim:

> 🔴 **STEP 1 — ONE LINE OF CODE, before any further 9-minute run. Restore the BASELINE `ExecState` read into
> route B's `s1()`**: `tools/recipes/build_d1_v0.py:461` has it, `build_d1_routeb_v0.py:302-316` dropped it. Then
> run route B with the two constructions above. **Why it comes first:** a cold-opened claudeDev copy reads
> **ExecState 0 while byte-identical to an original that reads 1** — measured on BOTH originals
> (`tools/bench/diag_d0_execstate_preload.log` 9/9 rc=0; `…/diag_d1_execstate_preload.log` 7/7 rc=0 on route B's own
> `Min_Track N beads V6_ParallelLoop.vi`, md5 = the recipe's pinned `ORIG_MD5` at `:173`) — and route B never
> preloads, so its S5 gate (`:1289`, `gscript.py:1920-1921`) has been reading **subVI linkage**. The baseline read
> separates "born 0" from "the build made it 0" inside the recipe's own instance, costs nothing, and makes the
> recipe self-diagnosing. ⚠️ **Do NOT add a preload to the build** — it can cross-link and `g.save(TARGET)`
> (`:1291`) would write that; preload is for read-only diagnostics only. Run 3's ExecState 0 was **over-determined**
> (unwired conditional terminals from the skipped `s1q`/S4b), so this does not mean run 3 succeeded — it means the
> gate could not tell. Reasoning, the three accepted corrections and the rivals still unexcluded: **Pre-decided 14 /
> 14a / 16**; review `archive/peer/2026-09-18-execstate-linkage.md` (ANSWERED, opus/max, $2.8794, **DISPOSED**).

## §3 — the two 📌 blocks and the "Small, owed, not gates" list (all still owed; none done in cycle 36)

> 📌 **Before the first D1 click or stop read `archive/2026-09-18-status-cycle31-d0-delivered.md` §4** — nine measured
> facts D1 would otherwise re-derive (stop Booleans in `Diagram#639`; control positions unreadable over COM; …).

> 📌 **Owed from retrospective-cycle35, cheap, do them in STEP 0's runner.** (i) **THIS FILE IS ~130 LINES** against
> the ~100 rule — relocate the cycle-31/34 narrative to `archive/` **before** adding anything new to it. (ii) The
> stall reviewer's four sub-second falsification probes F1–F4 (`tools/bench/peer_stall_c35.log:50-53`) were never
> run; run them before any further review of that class. (iii) LabVIEW held **~57,800 handles** during the Count
> runs (`diag_count_indicator_run2.log:59`) against the ~31,500 fresh baseline and no line remarks on it — measure
> it, do not pass over it (CLAUDE.md reference hygiene). (iv) A sub-session that finds it needs a NEW tool reports
> the need and stops; it does not build it (finding 7, `tools/wait_logs.py`).

> **Small, owed, not gates.** (a)(b) ✅ **DONE cycle 35** — `tmx_from` rule 4 deleted + docstring + pin case
> (`tools/bench/tmx_selftest3.log:19`, 17 pass / 0 fail, rc=0), and `audit_cycle` C7 repointed at the
> `status: current` plan via the new `doc_lint.current_plans()` (`tools/bench/audit_c35.log:23` names
> `docs/cycle27-plan.md`). (e) 🆕 **`bgrun`'s "always writes `BGRUN END|TIMEOUT`" guarantee FAILED on 4 logs**
> (`diag_fstunnelterm_v2_panelcost`, `p2_open_copy`, `prose_cycle25`, `wait_runner_exit`) — 4th occurrence of the
> OPEN-54 class, and it is a **repair of an existing device**, so Pre-decided 2 does not block it.
> (c) `tmx_sendmode_probe.log` rc=1 is a throwaway
> fixture, **no hypothesis review owed**; never `CYCLE_GUARD_OFF`. (d) `doc_lint` L6/A4 — archived reviews still
> blank. ⚠️ `.claude/agents/material.md:26-29` still mandates the DEAD `MATERIAL=1` prefix and cannot be edited from
> a cycle session, so **every material brief must carry**
> `py tools/bgrun.py --material --max-min N --log tools/bench/<name>.log -- py -u <script>` (cycles 26/28/35 all
> tripped on this — do not redo the repair).

## §5 — the two cycle-35 dispatch blocks, relocated VERBATIM from STATUS

> ✅ **Dispatch 1 DONE (cycle 35, read-only) — `Count` is NOT an indicator: it is CONTROL uid 28051** (`is_source`
> True) driving w30530 into `Equal?` #29111 term `x` and `SelectorTunnel` #31929 of `CaseStructure` #28709, on
> Diagram #15795 inside `Sequence` #15649 inside **`EventStructure` #15544**; WRITTEN by two implicit `Property`
> nodes labelled `Count` (`Value` = SINK): #32191 on Diagram #12960 and #30688 on Diagram #28741. Table, the 8
> Locals and the two measured limits → **`docs/NAMES.md` §`Count`**; `tools/bench/diag_count_indicator_run4.log`
> 16/0 rc=0. Meaning settled — **Pre-decided 15**: a control the event structure writes, **never a bead count**, so
> no harness may gate on it and D1 must not "fix" it; v5's red-marker counting stands. ✅ That run's alarming
> side-note — the D0 copy reading **ExecState 0 on disk** — was chased the same cycle and is a READING artefact, not
> damage: the file is byte-identical to the original and reads 1 under preload, so **D0's delivery record stands**.

> ✅ **Dispatch 2 DONE — and D1's blockers are decided, not open.** `SR_QUEUE_AUTHORISED` and `TEMP_SINK_AUTHORISED`
> stay **False permanently** — the answer is "no", not "not yet" (**`docs/cycle27-plan.md` Pre-decided 13**),
> because `docs/cycle15-plan.md` Pre-decided 1/2/3 (`:118-129`, still authoritative by its own frontmatter `:5-7`)
> already decide all three NO-ROUTE rows: `#1359`/`#29874`'s shift registers **MOVE WITH THEIR NODES** into loop 1.2
> (`add_shift_reg` + `wire_sr`, `index_mode 1` kept), and `Z/dZ` → `#2222` t0 is **REORDERED** before the S3-ct
> reparent of `ControlTerminal #403`. A build needing either flag True is the wrong build.

⚠️ Cycle 36's run 4 MEASURED that the second half of Dispatch 2's disposition **cannot be executed as written** —
see §4's `S3-zdz` rows. The registers half held; the `Z/dZ` REORDER did not.

## §4 — the cycle-36 run-4 facts, in full (STATUS keeps only the lock line)

| item | measured |
|---|---|
| log | `tools/bench/build_d1_routeb_v1_run4.log`, `BGRUN END rc=1 after 1713s` |
| gates | **80 PASS / 1 FAIL**, then a crash |
| S1 baseline `ExecState` | **0, read COLD ⇒ UNREAD** (`:25`) — Pre-decided 14a |
| S3w ledger | **NEVER PRODUCED** — the run died inside `s3w` |
| S5 `ExecState` | **never reached** |
| preloaded re-read (Pre-decided 14) | **FIRED BEFORE THE DELETE**: the ORIGINAL resident read-only reads `ExecState 1`, and the LIVE working copy `SCRATCH_routeb_221324.vi` reads **`ExecState 1` PRELOADED** (`:336-337`) |
| the only FAIL | `**FAIL** S3-zdz 'Z/dZ' -> #2222 t0 is wired BEFORE the #403 reparent (cycle15 Pre-decided 3)  sink wire 0` (`:164`) |
| why it failed | `S3-zdz NOT ATTEMPTED — the ControlTerminal is #403 and its node index on Diagram[56] is None. OpConnectNested_v1 addresses Diagram[].Nodes[].Terminals[] (build_opconnectnested_v1.py:418-420), so a ControlTerminal that does not appear in that diagram's Nodes[] has no by-index route. MEASURED, not inferred.` (`:163`) |
| the crash | `RuntimeError: count(LoopTunnel) on SCRATCH_routeb_221324.vi: error 2: Invoke Node in TRef Traverse.vi->VI Scripting - Traverse.lvlib:Traverse for GObjects.vi->OpReport_v3.vi` at `settle_index_modes()` (`:348-353`) — **error 2 = memory full**; the skill's rule is restart FIRST |
| Pre-decided 13 rows 1+2 | ✅ both registers created MOVED WITH THEIR NODES: `#26032` (`#1359`, reader t1 / writer t2) and `#26082` (`#29874`, reader t3 / writer t5) (`:315-316`). ⚠️ Neither carries the original's `Initialize Array` initial value (`#8953` w9051 / `#28124` w29122) — the recipe reports this rather than silently changing it, and v0 wires no initial value for any of its 8 registers either |
| F0 source map | 109/109 resolved, `{'cross-loop': 5, 'from-stay': 11, 'from-tunnel': 18, 'to-sr': 12, 'from-sr': 8, 'same-loop': 16, 'source-side': 27, 'from-ctl': 7, 'from-const': 5}` (`:321`) |
| original md5 | `2a78e17c449cacdaf5da389818526859` **before (`:4`) and after (`:340`) — UNCHANGED**; also unchanged across the preloaded read (`:338`) |
| working copy | deleted (`a broken VI is never written`) |
| handles | 0 (no LabVIEW at start) → 51,284 with the copy open (`:26`) → 30,682 after `lv_restart` (`:335`) → 49,062 at the end (`:341`) |
| instance left | the error-2 instance was killed; a fresh LabVIEW 26.3.1f1 was started by `tools/lv_restart.py` |

## §6 — the run-4 LOCK-BLOCK prose, relocated VERBATIM at the close of cycle 37

Relocated by the cycle-37 MATERIAL session (dispatch 4, cycle-close bookkeeping, 2026-09-19). Nothing is
rewritten: this is the exact text that stood in the `status:` line of `STATUS.md`'s `labview-lock` block, after
run 5's own prose and introduced there by the words "Prior text:". `STATUS.md` keeps one line and a pointer.

> Prior text: 🆕 **D1 ROUTE-B v1 RUN 4 RAN, cycle-36 MATERIAL, 2026-09-18 22:13→22:42** — `tools/bench/build_d1_routeb_v1_run4.log`, `BGRUN END rc=1 after 1713s`, **80 PASS / 1 FAIL** + a crash. **S1 BASELINE ExecState = 0 read COLD ⇒ UNREAD** (`:25`); the S3w ledger was NEVER produced and S5 never ran, because `s3w → settle_index_modes → g.count(LoopTunnel)` raised **`error 2` (memory full)** at `:353`. ✅ Pre-decided 13 rows 1+2 HELD: both shift registers were created MOVED WITH THEIR NODES (`#26032` for `#1359`, `#26082` for `#29874`, `:315-316`; neither carries the original's `Initialize Array` initial value — reported, not silently changed). 🔴 Row 3 FAILED — **the ONLY FAIL line**, `:164`. ✅ **`preload_reread()` FIRED BEFORE THE DELETE (Pre-decided 14) and the LIVE working copy read `ExecState 1` PRELOADED** (`:337`) against the cold baseline 0 — so the cold gate is again shown to be reading linkage. Original md5 `2a78e17c449cacdaf5da389818526859` **UNCHANGED before and after** (`:4`, `:340`); working copy deleted. Handles 0 → 51,284 (copy open) → 30,682 (post-restart) → 49,062. ⚠️ The error-2 instance was killed and a fresh LabVIEW 26.3.1f1 is up (`tools/lv_restart.py`). Prior text: cycle-35 dispatches 3+4 (read-only) finished 20:17 / 20:25, LabVIEW left killed, originals' md5 unchanged. MEASURED on BOTH originals: a byte-identical claudeDev copy reads **ExecState 0 COLD / 1 with the ORIGINAL preloaded read-only** ⇒ the linkage artefact belongs to the READING INSTANCE, not the file (`tools/bench/diag_d0_execstate_preload.log` 9/0 rc=0; `tools/bench/diag_d1_execstate_preload.log` 7/0 rc=0). Prose VERBATIM (md5s, handle counts, per-dispatch detail) → `archive/2026-09-18-status-cycle36-relocate.md` §1.

⚠️ NOT relocated, deliberately: the `✅ RETROSPECTIVE-CYCLE36 IS IN` block and the `🔴 D1 ROUTE-B v1 RUN 4 IS THE
CYCLE-36 BUILD LOG` block both sit inside `STATUS.md`'s `## NEXT` section, and this dispatch's brief said to
leave `## NEXT` alone — the judgement session rewrites it after the retrospective.
