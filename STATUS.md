---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---
Chat 2026-09-26 01:4x: the chat STOP (cycle-88 boundary, to relaunch on card chat-M1 code) was REMOVED after cycle 88 ended and the runner relaunched on the new cycle_runner.py (judgement ladder, judge A/B, material Fable low). Not a user start; the user said "lint 검증 이후 러너 재개" (2026-09-25).

# STATUS — read this first. One screen. Detail is one layer down, never appended here. ⚠️ **ONE SESSION AT A TIME** — re-read `CLAUDE.md` + this. Narrative → **`archive/2026-09-19-status-cycle47-relocate.md` (latest — T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `…-cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
✅ **DELIVERED:** 🟢🟢 **D1 S3 loop 1.5 = `claudeDev\D1_s3_loop15.vi` md5 `1a11d92aacabf7ec844d65b8af19f39f`** (482,312 B; byte copy of `D1_s3b_m4b_20260924_004214.vi`, kept; `tools/bench/promote_d1_s3_loop15.log` 5/0; ExecState 1 warm+cold, `computation_diff(S1,·)` 0 rows; STRUCTURAL + graph-equivalent under ASSUMPTION A, NEVER RUN; `docs/connectivity-map-plan.md` Pre-decided 147) · D0 (cycle 31) · N1 ACCEPTED (cycle 34) · D1 **S1** `claudeDev\D1_s1_copy.vi` md5 `3e3d23ce…` · D1 **S2** `claudeDev\D1_s2_loops.vi` md5 `6ff19497…` · D1 **S3a** both halves (`…_boolcarrier_b3_20260921_010034.vi` md5 `dc14dd00…`, `ExecState` 1, `Is Broken?` False) · D1 **S3b rows 1 and 2**. 🔵 **THE CURRENT BED IS `claudeDev\D1_l2_a1_20260925_235224.vi`, md5 `51d9b8a3…` (L2-A1, accepted cycle 88, PD195(a); machine key `current-bed:` in ## NEXT). HISTORY: `claudeDev\D1_k_20260925_100155.vi`, md5 `6cf5b077…` (stage K, cycle 79, 2026-09-25; ExecState 0 by design) was the bed before it; `D1_s4_loop17.vi` md5 `4b621946…` (L7-R) is its input, kept; every other "bed" named below in this line is HISTORY (`D1_s3_loop15.vi` md5 `1a11d92a…` is kept as the S3 deliverable).** ✅ **M3a-1 DELIVERED (cycle-63 firefighter, run 5, 2026-09-22 01:0x): `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c…`, 22 gates pass / 0 fail, bytes DIFFER from the bed.** ✅ **M3a-2 DELIVERED AND INDEPENDENTLY VERIFIED (cycle 64, 2026-09-22 02:3x–02:5x): `claudeDev\D1_s3b_m3a2_20260922_023029.vi` md5 `3842f5e6f128226235dc78353f26ef44`, 303,823 B, 25 gates pass / 0 fail on the build and 15/0 on a separate read-only check anchored at the REGISTER UID. 🔵 EVERY NEXT STAGE STARTS FROM THAT FILE.** 🔴 **M3a-3b (ROW D) IS **NOT** DELIVERED — NO FILE. ⚠️ CORRECTED 2026-09-22 15:4x (prior-art `archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md` A3): the standing reason given here — *"its W1 gate measures that NO writer on disk can address a `FlatSequenceInnerTunnel` terminal sink (`tools/bench/c78_rowd_writer.log`)"* — HAS BEEN FALSE SINCE CYCLE 82. `OpFsInnerTunnelConnect_v1.vi`'s `Wire Source` half IS the FSIT `LeftTerm` property node (`tools/bench/build_d1_m3a3b_d3.log:28`, `term_uid=7488`/`uid_back=7468` on 20/20 calls at `:58-60`), and `tools/bench/diag_c86_norbw.log:87`/`:97` records it WRITING wire 25324 onto `#7488`. THE REAL REASON ROW D HAS NO FILE IS THAT NO RUN HAS YET SAVED ONE. 🟢 **CYCLE-86's MEASUREMENT OUTCOME, never recorded until now: `tools/bench/diag_c86_norbw.log` (14:46) answered plan entry 111a YES on a byte-identical scratch of the bed with Remove Bad Wires rebound to a raising guard — after `del_wire(7506)` `#7468` STILL RESOLVES (`uid_back=7468`, `:74`), `#7488` comes back BARE (`wire_a=0`, `:76`), the inner wire 7448 survives (`:77`), the connect then writes wire 25324 onto BOTH ends (`wire_delta 1`, `:87`/`:97`) and the net ends with ONE source owner `RightShiftRegister #23868`, `#4334` off, PD85 0, `Is Broken?` False (`:105-110`). It SAVED NOTHING and deleted its scratch (`:113`), and the log has NO `BGRUN END` (truncated mid-cell-B), so D5/D6/D7 were never reached.** THE BED IS STILL `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e…`, 306,951 B.** Both initial-value rows land the predicted source (`FlatSequenceInnerTunnel #4194` → LEFT `#23880`; `#3974` → LEFT `#23909`), the originals stay on their nets, `Wire.Is Broken?` False in a separate ordered pass, PD85 violations 0 on every walk. Still BROKEN BY DESIGN and NEVER RUN (34(f)); `ExecState` 0's cause is formally OPEN and is neither gated on nor reasoned from. The artefact is BROKEN BY DESIGN (uninitialised SRs — initial values are stage M3a-2) and is NEVER RUN (34(f)). Two root causes were repaired and MEASURED on the way: the identity reader `wire_source_owner` (history-echo, now error-checked + uid-echo-verified, acceptance `diag_c68_echo_accept.log` 8/0) and `gscript._lv_gui` (unquoted spaced args = PowerShell parse error, so NO Evidence-carrying GUI action had EVER dispatched — `archive/peer/2026-09-22-c72-guisave-foreground-r2.md`). The bed is byte-unchanged and all four md5 pins hold. S3-as-37(g)-defined is WITHDRAWN (cycle 53). **Read `docs/cycle27-plan.md` Pre-decided 84–90 BEFORE 78–83 (78/80/81/82 are WITHDRAWN)**, then 46, 42, 43, 44. Full chronicle VERBATIM → `archive/2026-09-21-status-cycle67-locknotes.md` §2; banner VERBATIM → `archive/2026-09-18-status-cycle36-relocate.md` §3; facts `…-cycle31-d0-delivered.md` §1–§5 (read **§4** before the first D1 click).
⚠️ **SUPERSEDED, NOT A BED — `claudeDev\D1_s3b_m3a3b_rowD_20260922_153612.vi`, md5 `c9d38bb194013ac7b916d073466078c7`, 307,093 B.** It is KEPT on disk (a real saved intermediate the user can open) but NO stage starts from it: it was saved carrying an unpurged second-pass junk `Invoke` (`Node` 636, `Diagram #686` 28 nodes). The Row-D bed is whatever the CLEAN re-run leaves — **tell the two apart by this md5, never by the timestamp** (the `_REJECTED_…` rename is refused by the permission layer, as it was for `D1_s3b_m3a3_20260922_075611.vi`). Written 2026-09-22 16:1x as prior-art `archive/peer/2026-09-22-priorart-c87b-rowd-clean.md` A1's release.
🆕 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 — EVERY GUI action is capture → locate → act → capture → confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.


## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **§A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. 🔴 **NEVER patch a file with a `py - <<'EOF'` heredoc** — one truncated **this file to 0 bytes** on 2026-09-17.
3. ⚠️ `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' … -TaskFile <f>"`, `-TimeoutSec >= 780`. 🆕 **2026-09-18 (user, TRIAL): codex's roles → claude roles** — failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` → fable/low thin; `outcome_review.py` → fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming · front panel open for edits · `guard_cycle`'s `FIXED:` release · `py_compile` tripping BUILD_RE · §11u unsound · §10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` §1**. ⚠️ `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` — quote both paths (cycle23-close §3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  relocated_c81: lock keys owner_c74m8s3/owner_c74m8/owner_c73l7r/owner_c72ff/relocated_c72/owner_step6/owner_step5b2/owner_step5b/owner_step4b/owner_step4/step4_delivered/owner/v1_delivered/purpose/step3_delivered/owner_s1s2/purpose_step1_delivered/purpose_s2_delivered/known_limit_s3/purpose_s1s2/relocated_c68 RELOCATED VERBATIM -> `archive/2026-09-25-status-cycle81-relocate.md` §1
```
🔵 **THE WHOLE CHAINED `purpose:` NARRATIVE ("PREVIOUS PURPOSE, unchanged and still true — …", cycles up to 64, 12,560 bytes on one line) RELOCATED VERBATIM (rule 4) → `archive/2026-09-22-status-cycle64-locknotes.md` §1** — nothing deleted, nothing rewritten; the `purpose:` key above now states only the CURRENT state.
🔵 **ALL 50 HISTORICAL LOCK-BLOCK ENTRIES (cycles 48–67: 48 `owner_*`/`lock_*` keys, the superseded `status:` line, and the `motor:` key) RELOCATED VERBATIM (rule 4) → `archive/2026-09-21-status-cycle67-locknotes.md` §1** — that file also carries the three older `lock_relocated_*` pointers (into `…-cycle5556-relocate.md`, `…-cycle54-relocate.md`, `…-cycle5153-relocate.md`, `…-cycle49-relocate.md`, `…-cycle48-lockkeys.md`). **Motor state, unchanged and still true:** limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU ±2 mm), ports closed. ⚠️ The motor clause quoted in this line is HISTORICAL; the live motor state is the rig-state line below.
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ≈31,500 handles; unique scratch name/run.

## HARDWARE — permission follows the RIG STATE. Current: **조립 / ASSEMBLED** (machine key `rig-state:` below)
분해 = motors ✅ ASI ✅ camera ✅ · **조립 ← WE ARE HERE (user 2026-09-23 14:2x "실험 마침")** = camera ✅, motors/ASI ONLY through `tools/motor_gate.py` inside the envelope, LabVIEW allowed · 실험중 = ❌ ❌ ❌ and no LabVIEW use (was the state 12:3x–14:2x; header corrected 2026-09-23 23:4x by the cycle-68 material session). ⚠️ ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** · magnet full travel · camera 1280×1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** → the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
🆕 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ⇒ TMN 0 / TMX 39 (RAM, **never WPA**) · ASI `SL/SU` absolute mm X −3.8475…0.1525, Y −4.7744…−0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without the session file (tools/bench/motor_session.json, present ONLY while a session is open) **and** a fresh matching readback.
The gate still refuses 실험중, every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 85/85, 2026-09-24; FAIL-exit self-test 10/10).
rig-state: 조립   <!-- 2026-09-24 20:xx USER GRANT: "당분간 내가 말하기 전까지는 모터 접속 허용함. 다만 원점 확인 및 모터 리밋, 두 가지는 꼭 확인 필요" — motors (PI, rotor, ASI) may be driven by the gate AND by a running main VI while the rig stays assembled, until the user withdraws it; PI reference + verify at session start and limits set/released with readback are never skipped; "사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것 (특히 카메라가 계속 Acquisition 하면 기계에 좋지 않으니)" = runner end hook closes LabVIEW and verifies the process is gone. Earlier: 2026-09-23 14:2x user: "실험 마침. 다시 세션 들어가도 무관함" — rig stays assembled; motors/ASI only through motor_gate inside the envelope, LabVIEW allowed. Before: 실험중 13:43 ("지금 실험중이야") — limits RELEASED and read back (PI 0..52, ASI ±500, `tools/bench/motor_session_end_20260923c.log`), PI referenced at 0 (FNL, 13:36), servo on; no motor/ASI/camera/LabVIEW use until the user says otherwise. Earlier 13:3x, on the user's order ("너가 한번 PI 모터 움직여볼래? 0으로 이동, 5초 정지, 30으로 이동, 5초 정지, 0으로 이동"): PI test moves through the gate to diagnose "PI doesn't respond to the main VI". Before that: 실험중, restored 2026-09-23 13:11 after ONE `motor_gate.py --session end` on the user's order ("게이트로 해줘"): limits RELEASED and read back — PI TMN 0 / TMX 52, ASI SL/SU ±500 mm, position unchanged (`tools/bench/motor_session_end_20260923.log`). Set 실험중 2026-09-23 12:3x on the user's words ("내가 곧 실험을 시작하니 … LabVIEW 활용은 하지 말도록") — no motor, no ASI, no camera, and NO LabVIEW use at all until the user announces otherwise. Previous: 조립, set 2026-09-17 23:0x on the user's words ("실험 1차로 끝났는데, 리그는 유지되는 중" + "조립 상태에서도 이 범위 안이면 모터 허용함") · the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 분해 / 조립 / 실험중. Keep it at the start of the line, unquoted. -->

## Where things stand — the three ✅ lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` §4
✅ tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ⚠️ **do NOT re-run the recipe, run 1 is the record**) · ✅ the "ZERO runnable experimental VIs" gap is BROKEN — `tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice · ✅ N1 accepted ⇒ the GPU kernel is cleared for D1. **Order is D0 → D1 → D2** (`docs/cycle27-plan.md` Pre-decided 1). Prose VERBATIM → `archive/2026-09-21-status-cycle67-locknotes.md` §3; earlier → `archive/2026-09-18-status-cycle22-close.md` §2.

## OPEN — **items 1–40 VERBATIM in `archive/2026-09-17-status-runner-build.md` §2**; the five CLOSED items (32 · 55 · 56 · 51/52/52a · 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` §5, which forwards to `…2026-09-18-status-cycle36-relocate.md` §5–§9. ⚠️ Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. 🟡 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` §10 NOT AUTHORISED. ✅ the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history → `archive/2026-09-19-status-cycle40-close.md` §2.
53. 🔴 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** — i.e. that 0–39 still fences the intended physical window. VERBATIM → `archive/2026-09-18-status-cycle36-relocate.md` §9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. 🔴 **TWO RULES YOU MUST FOLLOW, reasoning relocated → `archive/2026-09-19-status-cycle40-close.md` §3.** (a) **The retrospective is the LAST thing a session runs** — `guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** — a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. 🟡 **LIVE PART ONLY** — 42 ⚠️ undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (⚠️ A4 counts a whole DAY, so it charges the previous cycle's files to this one — retrospective-cycle40 F4) · 46 ✅ **CLOSED 2026-09-23 — FALSE PREMISE**: `SetCommand_signed.vi` IS on disk (`claudeDev\SetCommand_signed.vi`, md5 `ec87a265…`, hardware-verified 2026-09-14); the "no disk" claim was a search-scope artefact. The real remaining item is the stage-2 repoint of the nine rotor call sites (Pre-decided 133) · **47 🔴 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ✅ CLOSED. Full text → `archive/2026-09-19-status-cycle40-close.md` §4.
57. 🟡 **NEEDS JUDGEMENT RATIFICATION (cycle 68, material):** `guard_peer.py` now (a) formats its refusal through a drive-safe `_rel()` — the same helper `guard_cycle.py:518` has carried since 2026-09-17; without it the hook RAISED instead of refusing when the failing log sat on another drive (`tools/bench/jev_discharge.log:21-26`, rc=99) — and (b) skips a failing log whose LAST `BGRUN START` command is a **Jev script**, the other half of the user's 2026-09-22 "Jev는 면제" exemption (until now wired only into `RUNNER_RE`, the COMMAND side, so a Jev self-test bundle's fixture text — `STOP:`/`FAIL` by construction — armed the gate against every other run). Scoped by the COMMAND, never the filename. Self-test `tools/bench/selftest_guard_peer_jev.py` **17 pass / 0 fail**, two new cases: C7 (a newer Jev log does not become the blocking log) and C7b (a non-Jev build that merely MENTIONS a Jev script still gates).
58. 🟡 **FOR THE USER — three known limits of the new autofocus loop (loop 1.5) in `D1_s3_loop15.vi`** (decision: `docs/connectivity-map-plan.md` Pre-decided 147(b)). The new loop starts an autofocus when the "focus now" signal switches from off to on. (1) If **Frame rate** is set to 1 the signal is on every frame, so the new loop focuses once instead of every frame. (2) If you run the VI again without reopening it, the first autofocus can be skipped when the previous run stopped on a focus frame. (3) If loop 1.5 falls more than one frame (~11 ms) behind, that one scheduled autofocus is skipped; focus values are not saved data. Tell us if any of these matters for your experiments.

## NEXT
🟡 **CARRY (from the 2026-09-25 verification review `archive/peer/2026-09-25-hyp-lintverify-20260925.md`, not blocking): card flags are checked only on the top-level command (a child process could reach LabVIEW under labview=none); a stage run launched outside bgrun is not counted by the retry cap; a bgrun record failure is only logged (`tools/bgrun.py:219-220`). Close in a tooling cycle, deliverable-first.**
current-bed: D1_l2_a1_20260925_235224.vi
<!-- ^ machine key read by tools/errorlist_check.py current_bed_text(); without it the bed is chosen by mtime among D1_*.vi names in this file, and the newer D1_s1_kswap_* would silently take over (review archive/peer/2026-09-26-c88-reuse-stalepin.md). Change it only when a new bed is accepted. -->
🔴🔴🔴 **FIRST ACT (cycle 95) = `docs/d1-loop12-17-split-plan.md` Pre-decided 202(f), then 202(d): turn on loop-iteration parallelism for ForLoop #1359 (diagram #7911) in a copy of S1.**
- **Step 0 (PD202(f); retrospective-cycle94 `device-failed`, accepted):** fix `tools/stage_prerun.py --dry` crashing with `KeyError 'terminals'` on `tools/bench/graph_s1_20260924.json`. This is the 5th crash on record (`prerun_records.jsonl:17,24,33,65`).
  - Pass: the dry run completes on that graph, the earlier crashers re-run clean, and there is a self-test with a negative case.
  - Never pass a refusing launch gate by hiding the script from its classifier again (94-3 did this).
- Step 1: a read-only precondition check on a scratch copy. The loop body #7911 must contain no Feedback Node, no local or global variable write and no shift register. Record whether Median Filter.vi and FIR Filter (DBL).vi are reentrant.
- Step 2: `claudeDev\D1_s1_par1359_<ts>.vi` is a byte copy of `D1_s1_copy.vi` with ONLY #1359's parallelism enabled, at LabVIEW's default instance count (record P).
  - There is no recorded writer for an EXISTING loop's parallelism: `docs/toolkit-capabilities.md` has only the reader `OpLoopCast_v1` `parallel_enabled`. Put it in the card's `requires`. If it is missing, build it first.
  - Gates: ExecState 1 warm and cold; `computation_diff(S1,·)` 0 rows; read-back True on #1359 and unchanged on the other 16 For loops; saved by script.
- Step 3, rule 1a: run S1 and the copy on the same recorded frames through the replay path. X/Y/Z and the Bundler #11310 output must be bit-identical, otherwise stop.
- Step 4: ABBA at 15 picks, 120 s, panel normal (A = S1, B = the copy). Record lost frames and the #637 period.
  - Also log, per leg, the number of foreign `claude`/`node` processes and a CPU sample.
  - Cycle 94's numbers were taken while a 40-cell benchmark ran on the same machine, so they are load-uncontrolled (PD202(f)).
  - If A15 comes in well below 4,277 lost frames / 16.7 ms, re-take the slope before quoting it.
  - 🟡 FOR THE CHAT: do not start benchmarks on this PC while a cycle is running legs.
- User decision **D-2026-09-26-01** (loop-level timers only) is still OPEN; the work proceeds under its recommendation.
- Machine copy: `tools/bench/next.json`.

🟢 **CYCLE 94 (PD202): THE PER-BEAD LEVER IS NAMED.**
- 94-1 passed 65/0 (INDEX 55, `tools/bench/t0_step4v2_94.json`). Six legs ran, and every one registered all its picks on the first try.
  - Lost frames: A11 1,672 · B11 2,137 / 1,588 · A15 4,277 · B15 4,049 / 4,070. The stamps do not perturb at 11 or 15 picks.
  - The tracking loop #637 is compute-bound at 11 and 15 picks (period 13.1 / 16.7 ms, against the 11.1 ms camera period). Its period grows **+972 µs/bead**.
  - Site 4, the output of ForLoop #1359, grows **+760 µs/bead**. The kernel (#5058) grows only +188.
- 94-3 passed 32/0. #1359 has 0 shift registers, gets its count from auto-indexing, and has parallelism OFF.
  - Each iteration processes one history row: ring insert #8634, then Median #29009 and FIR #28233.
  - Its cost rises as the history ring fills: at 15 picks it goes from 1.3 ms to about 10 ms.
- ⇒ The change is scheduling only (PD202(c)). Changing the filter maths would need the user's decision.
- Carry: `stage_prerun --dry` crashed with `KeyError 'terminals'` on `graph_s1_20260924.json` (PD202(e)).

🟢 **CYCLE 93 (PD200).**
- **The stamps' ~110 lost frames are EXPLAINED AND FIXED.**
- The hypothesis review (`archive/peer/2026-09-26-c93-h1-stamp-array-copy.md`, accepted) refuted the array-copy candidate.
- The cause: `t0stamp` v1 ran `FlushFileBuffers` inside `stamp()` every 1024 calls. Six sites flushed in the same iteration.
- Offline check: in the old B legs, the top-10 periods are exactly at iterations k·1024−1, at 108–212 ms.
- `t0stamp` v2 has no I/O in `stamp()`. It is in place (`b35b398d…`); v1 is kept as `claudeDev\t0stamp_v1.dll`.
- ABBA at 8 picks: unstamped **14 / 19** against stamped v2 **24 / 43**, under the limit of 53 ⇒ **the instrument is CLEARED** (INDEX 54, `tools/bench/m8_flushfree8_93.json`). The clearance is thin: B still loses about 2× A, with a 24-vs-43 spread and n = 2.
- The scalar-only build is cancelled.

🟢 **CYCLE 92 (PD199).**
- **The UI-thread hypothesis is REFUTED.**
  - All 12 stamps were UI thread (`Any Thread?` False; `build_clfn`'s `reentrant=True` does not set it).
  - An any-thread copy was built: `claudeDev\D1_s1_t0at_20260926_090833.vi`, md5 `30a15c67…`, 12/12 True warm and cold, cdiff 0 rows with 24 added.
  - ABBA at 8 picks: unstamped **20 / 22** lost against any-thread stamped **130 / 131** (UI-thread stamped was 138 / 144). So the instrument is NOT cleared (INDEX 53, `m8_anythread8_92.json`).
- ✅ **The harness capture fix works.** LabVIEW's own `LVDChild` held the mouse capture before pick 1 in 3 of 4 legs. One title-bar click released it, and all 4 legs registered 8/8 picks.
- ✅ **New ops:** `OpCLFNThread_v0.vi` (reader) and `OpCLFNThreadSet_v0.vi` (writer), documented in `docs/toolkit-capabilities.md` and `docs/NAMES.md`.
- ✅ **The bgrun reaper is built** (92-4 PASS 18/0). bgrun now writes a `BGRUN PID` line. `tools/bgrun_reap.py` marks a dead run's log `BGRUN KILLED`, and it runs at every bgrun start and in the runner's cycle-end hook. This closes retrospective-cycle90's `device-failed`. Pre-92-4 logs stay listed as "unfinished" and are never closed by hand (PD199(g)).

🟢 **CYCLE 91 (PD198).**
- ✅ **Step 3 is DONE.** `claudeDev\D1_s1_t0_20260926_055551.vi`, md5 `25ea4f7d…`: 12 While-body stamps, with ExecState 1 read after every site. `computation_diff` is 0 rows with 24 added. It was saved by script, and the smoke run wrote 12 stamp files.
- ✅ **Step 4 ran** (`tools/bench/t0_step4_91.json`, INDEX row 51).
  - Only **site 4 grows with bead count**: the For #7911 output, which carries Median #29009 + FIR #28233.
  - It adds +255 µs/bead (panel normal) and +173 µs/bead (minimized).
  - ⚠️ The 8-pick cell is frame-bound (11.14 ms against the camera's 11.11 ms), so "the kernel does not grow" is WITHDRAWN (retrospective-cycle91 finding 3). At 15 picks, site 4 fires 12.6 ms after `i` and the kernel 8.4 ms after it.
  - This is only a candidate lever until the instrument is cleared (PD198(c)).
- Also owed in the first act: log the capture window's class before pick 1 (a read, not a GUI act; asked by both reviews). With the reaper card: capture the quit dialog before taskkill (`archive/peer/2026-09-26-c91-t0step3c-quit.md`).
- 🟡 **FOR THE USER:** `.claude/agents/material*.md` still prescribe the refused `MATERIAL=1` prefix, and the permission layer refused the edit. The replacement text is in `tools/bench/audit_c7_agent_patch.md`; apply it.

🟢/🔴 **CYCLE 90 (PD197).**
- ✅ **The stamp tool is DONE.** `claudeDev\t0stamp.dll` md5 `1ea78380…`, self-test 4/0 outside LabVIEW. Scratch `claudeDev\t0stamp_scratch_20260926_040425.vi` md5 `5e4fd1f0…`: ExecState 1; 0.30 µs per stamp, 1.40 µs with a 1024×1280 U16 branch (no copy); handles flat; the negative case (site 64) is caught (`diag_c90_t0stamp_scratch_r3.log` 21/0).
- ✅ **Stamp-site table:** `tools/bench/t0_sites_s1.json`. `check N bead pos`, `save N xyz traces` and `grayscale color table` run ONCE, outside every While loop, so they are not per-frame costs.
- 🔴 **Step 3 failed twice** (90-5 fable/low, 90-6 fable/medium; no file). The While-body route works: sites 0 and 2 are ExecState 1. `OpCreateConstOnTerm_v0` refuses a ForLoop owner (1055), and a reader index shift caused run 2's failure (patched, not rerun). There are 4 answered reviews under `archive/peer/2026-09-26-c90-*`.
- ✅ `audit_cycle` C7 now reads the plan named in `next.json` (self-test 8/0, 90-2). INDEX row 50 was added for the cycle-89 panel legs.

🟢 **CYCLE 89 DONE (PD196).**
- In-VI bracketing and a LabVIEW-primitive stamp helper are unreachable with our verbs (89-1, 89-2).
- The profiler cannot be scripted, and its GUI route failed its liveness test twice, so it was dropped (89-3, 89-4).
- **Display is a minor lever.** 15 picks, unmodified S1, panel minimized via COM, ABBA order: ctl 3,434 / 3,603 lost against min 2,616 / 3,286, about −16 %. At 8 picks the two are equal (16 / 15). Roughly 30 % loss remains, so the main per-bead cost is neither display nor the kernel.
- ✅ The firefighter trigger now skips a recipe whose newest run passed (`tools/cycle_runner.py:401` `newest_run_passed`). Self-tests: ff 5/5, runner 10/10, ladder 11/11 (89-6). This closes retrospective-cycle88's `device-failed`.

🟢 **CYCLE 88 DONE.**
- **Bed = `claudeDev\D1_l2_a1_20260925_235224.vi` md5 `51d9b8a3…`** (195(a)). The read-only P2 check passed 5/5 (`tools/bench/p2check_l2a1_88.json`). This is structural; the file has never been run.
- **Error List MISMATCH explained** (195(b)): all 11 extras disappear under Remove Bad Wires, and those 29 wires include none on a re-wired sink.
  - Cycle 87's uncapped licence classes were reverted.
  - An explicit `tools/bench/errorlist_expected_D1_l2_a1_20260925_235224.json` (35 items, exact counts) now replaces the derived licences for this bed.
  - Offline re-verdict: OK 0/0. Self-tests 18/0 and 5/5, including a negative case.
  - Reviews: `archive/peer/2026-09-26-c87-errorlist-extras.md`, `…-c88-reuse-stalepin.md`.
- **Kernel swap: `claudeDev\D1_s1_kswap_20260926_004935.vi` md5 `e77b8d58…`** (ExecState 1; rule 1a on INDEX rows 12/17/40). At 15 picks, 120 s, it lost **3,410 / 3,490** frames against **3,776** for the same-session S1 control (cycle 83: 3,331 / 3,161). ⇒ no lever (195(c)); `archive/benchmarks/INDEX.md` row 49.
- Open, not blocking: `errorlist_check.compare():407` prints `missing` as None for norm_all entries (the verdict is still correct).

🟢 **CYCLE 86 DONE: THE L2-A1 FILE EXISTS.** Stage run 1 (card 86-5, 594 s) saved `D1_l2_a1_20260925_235224.vi` by gui_save. ExecState is 0 by design.
- E1: 42/42 ops match the simulator.
- PB cdiff equals exactly the 9 open rows.
- RBW: 29 bad wires, none on a re-wired sink.
- Peak memory 638 MB, no error 2.
- 5 P2 FAILs: the recipe's reader could not address SelectorTunnel sinks (`stage_d1_l2a1.py:90`). Review `archive/peer/2026-09-26-hyp-l2a1-p2-86-5.md` refuted a build fault.

How the run was made possible (PD192 → 193):
- stagexec now meters private MB and handles per op and per read (md5 `0d131139…`, self-test 59/0).
- Most of cycle 85's handle growth was the VI LOAD: 33,987 → 45,631 handles.
- Error 2 recurred right after act 45 when there was a whole-VI read after every op: reads added +140 MB, edits +1.7 MB, and it failed at 695 MB.
- With 9 reads there was no error 2, so act 45 is not the cause. Whether it is the reads or accumulated memory is still OPEN (prior-art amendment).
- The recipe now reads only at checkpoints {0,15,19,23,27,28,40,41,42}, with MEMSTOP 700.
- The prerun needs `--graph tools/bench/sim/l2a1/graph_k_80_owners.json` (194(c)).
- The outcome review ran again: the same 4 verdicts, not a stop (user 2026-09-23). All 7 items in `decisions_pending.json` are ANSWERED; the "4 open questions" line below is stale.
🟡 **CYCLE 85 DONE (cycle 84 never ran: weekly usage limit).** No stage run was launched.
- The separator returned 5001, so the old 1057 came from the source cast (PD191).
- Three new ops were built, each self-tested with a negative case and handle-flat:
  - `ops\OpConstWire_v1.vi` `c978863c…`, for op 35.
  - `OpCtlSinkWire_v1.vi` `ce9f2088…`, for R41.
  - `OpTunOuterWire_v1.vi` `093b0539…`, for R45/46.
- stagexec md5 `4186fcb4…`, self-test 50/0. The dry run lists every unroutable row, and a uid-reuse guard was added.
- Dry run 42/42 with 0 unroutable; pre-run 8/0.
- On a real scratch, acts 1–44 had diff 0. After act 45, `report_all` raised **LabVIEW error 2 (memory full)** (`tools/bench/unroutable_l2a1_85.log:562`; review `archive/peer/2026-09-25-hyp-unroutable-err2-85.md`).
- D1_k is unchanged.
⬇ Older (cycle 84 plan, now done up to step 2's dry/pre-run):
✅ **CYCLE 83 (firefighter, fable/low) = the PD188(d) load measurement RAN — INDEX row 48, `tools/bench/m8_load_83.json`, 8 real legs 8/0, LabVIEW closed after each.** Total Lost Frames S1 copy vs `D1_s3_loop15.vi`, 120 s at ~89 frames/s (~10,680 frames): **8 picks 16 vs 12** (repeat 12 vs 14) · **15 picks 3,331 vs 3,493** (repeat 3,161 vs 3,269). Frame loss goes from ~0.1 % to ~⅓ between 8 and 15 beads on BOTH VIs ⇒ **the per-bead tracking cost (loop 1.2, M3) is the lever; the loop-1.5 split is neutral at this load.**
- ⚠️ **150 Hz was NOT reached**: the driver wrote 150 Hz to the camera between legs, but EVERY `IMAQdxOpenCamera` reloads the camera file (`…\NI-IMAQdx\Data\JAI Corporation SP-5000M-USB (…).icd`, 90 Hz) — measured `tools/bench/diag_camrate_persist83b.log` 4/0 after the failed-prediction review `archive/peer/2026-09-25-hyp-camrate83.md` (accepted; `camera-acquisition-facts.md:642` corrected). The "150 Hz" cells are 90 Hz repeats. Real 150 Hz needs a VI-side setting or an `.icd` change → **user decision D-2026-09-25-05**.
- ✅ (stale as of cycle 86: all ANSWERED in `decisions_pending.json`) The user had 4 open questions: D-2026-09-25-02 (`.cal` scope), -03 (autofocus limits, OPEN 58), -04 (a supervised S3 run with beads), **-05 (how to reach 150 Hz)**.
- Owed before the constant-source op (violation-decisions 16:10): make the stagexec dry run report EVERY unroutable row.

▶ **THE L2-A1 run from the bed `claudeDev\D1_k_20260925_100155.vi` md5 `6cf5b077…`, Pre-decided 188(c) + 189:**
1. Op 35 needs a verb for a bare constant source: `#10739 → #10950 'y'` and `#10929 → #10757 'index'`.
   - First run the review's cheap separator (`archive/peer/2026-09-25-hyp-constsrc82.md:84-86`): is OpWire_v1's 1057 the source cast or the destination cast?
   - Then build the smaller op: either the fixed cast, or `Constant.Terminal` (634AC04) + `Terminal.Connect Wire` (6349C03), with the source taken by uid through report_all(class).
   - Gate: the new wire's only source is owned by the constant uid, and `Is Broken?` is False. Self-test it with a negative case.
   - Route it in `tools/stagexec.py` (md5 `3e2b1527…`, self-test 34/0), in both the real Addr and SimReader.
2. Then run dry → pre-run on all 42 ops (no offline stop) → run 1. The recipe is `tools/recipes/stage_d1_l2a1.py` md5 `e589dc74…`. The stageplan is `tools/bench/sim/l2a1/stageplan_l2a1.json` md5 `329d89ee…`. The pass criteria are 187(c)'s. Save `D1_l2_a1_<ts>.vi`.
3. Use `bgrun --max-min 60`: `Stage.close` takes about 20 min after the work (188(e)).
🟡 **CYCLE 82 = no L2-A1 artefact, and no real stage run. The tools the run needs were built and measured on scratch copies; D1_k is unchanged.**
- **Reader parity at PRIME** (187(a)) is built and accepted. It turned up 231 SimReader-only entries before the fit and 0 after, and the 173-diagram holdout is also 0. Run 3's stop is now caught offline.
- **Nested ControlTerminal source** (187(b)) is routed through `gscript.wire_control`. Both rows were measured correct on a scratch at op 31. The dry run now has ops 1–34 at diff 0.
- **Op 35 (bare constant source) is BLOCKED.** OpWire_v1 gives 1057 and wire_control gives 5001 (`tools/bench/constsrc_l2a1_82.log:511-533`). The new op is decided in 188(c).
- **Outcome review ran** (`archive/peer/2026-09-25-outcome-review-20260925.md`): tooling-over-delivery, ordering-stale, goal-requirement-not-advanced, decision-starved. It wrote `steer_82.json`.
- `docs/violation-decisions.md` 14:28 records two decisions:
  - `repeated-failure-class`: the parity device, BUILT.
  - `device-failed`: `audit_cycle` C7 should read the plan named in next.json, not the first `current` plan. This repair is owed after the deliverable.
- Owed tools, not ahead of the deliverable:
  - When L2-A1 resumes, FIRST make the stagexec dry run report EVERY unroutable row, not just the first (`docs/violation-decisions.md` 16:10).
  - Per-phase stamps in `stagekit.close`, to find where the ~20 min goes.
  - The `audit_cycle` C7 repair above.
  - `guard_card` accepts any `cd <dir> &&` before `stagexec.py selftest` (review `archive/peer/2026-09-25-hyp-selftest-elreuse-81.md`).
  - `selftest_launch_gate.py` fails 20/8 (C2-C6, M4-M6).
  - `selftest_cycle_runner.py` needs `--dry-run`.
  - Option (c) of Pre-decided 184 (offline addressing of ends the stage itself wires).
- Fact: there is NO read-only `Wire.Is Broken?` op. The reader exists only inside connect ops (`docs/NAMES.md:1081-1089`), so CLAUDE.md's "BUILT" means only that.
🔵 **CYCLES 68–80 DONE records, old FIRST ACT paragraphs and carries RELOCATED VERBATIM → `archive/2026-09-25-status-cycle81-relocate.md` §2** (card 81-1). Still-live items there, one line each:
- 🟡 FOR THE USER: `.claude/settings.json` guard_session matcher `Agent|Task` → `Agent|Task|SendMessage` (only you can apply it); `git commit` at cycle close needs your approval-list entry (§2).
- 🔴 Rule: desk-check PREDICTED VALUES, not only gates → Pre-decided 132 (§2).
- 🟡 Carries not ahead of the deliverable: cp949 print helper in stagekit, audit A1 vs `jev_gate.log`, bgrun END guarantee under a tree kill (§2).
- ⚠️ Per-session cap 180 min: write `## NEXT` by minute 150; every new stage/diagnostic ≤120 lines on stagekit (§2).
- Still the user's to overturn: N1 on the pre-bead-loss window, bead-4 FLIP mask, harness records 60 controls and sets none, `background VIs_COPY` untouched (§2).

## Where to look — **`docs/handover-2026-09-22.md` (새 세션은 이것부터)** · `CLAUDE.md` · `docs/secrets-and-handover.md` (API keys, 사용자 교체 체크리스트) · `docs/jev-integration-plan.md` (Jev 삽입 자리, 2026-09-22) · **`docs/decisions.md`** · `docs/NAMES.md` · **`docs/toolkit-capabilities.md`** · **`docs/motor-call-site-census.md`** (P1) · **`docs/d1-route-b-plan.md`** = the build order · `tools/recipes/build_d1_routeb_v0.py`.

## RUNNER STOPPED history (2026-09-22 09:58, 2026-09-24 07:29, 2026-09-25 01:02, 2026-09-25 10:30) → `archive/2026-09-25-status-cycle81-relocate.md` §3
