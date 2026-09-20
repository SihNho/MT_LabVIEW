---
type: archive
status: archived
date: 2026-09-18
tags: [status, narrative, motor, motor-gate, controller-limits, p2]
---

# Motor gate rework (2026-09-18 15:2x–15:4x) — STATUS relocation (rule 4)

## §1 The rework itself — the limits moved from our script into the controllers (user, present at the rig)

User decision, 15:2x: **the real limits are now in the controllers, not in our script.** Implemented:

- `tools/motor_gate.py` REWRITTEN. DELETED: the PI `0..39` numeric test, the ASI "within 1.0 mm of the anchor"
  radial test, every use of `tools/bench/motor_anchor.json`, the "fresh position read" requirement and
  `--sim-pos`. KEPT: the `rig-state:` check (실험중 ⇒ refuse all, unknown ⇒ refuse), command-class default-deny
  (every ASI home/origin/zero/save/reset — `!`, HOME, H/HERE, Z/ZERO, HM, AZ, SP, SS, `~`, `\`, MC, and now SL/SU
  writes; every PI GOH/FRF/FNL/FPL/DFH/RON/POS/SPA/WPA; all rotor motion), read-only queries pass, one route only.
  The refusal reason is now the real one: **a controller limit is ABSOLUTE, so shifting the coordinate zero would
  move the fence.**
- NEW `tools/bench/motor_limits.json` (user-editable): `pi.lo_mm 0.0 / hi_mm 39.0 / release_hi_mm 52.0`,
  `asi.sl {X -3.8475, Y -4.7744} / su {X 0.1525, Y -0.7744}` (ABSOLUTE mm, already in the ASI controller),
  `asi.release {sl -500, su 500}`, `tolerance 0.001`.
- NEW session hooks. `--session start` writes `SPA 1 0x15 <hi>` + `SPA 1 0x30 <lo>` and the ASI `SL`/`SU`, reads
  TMN?/TMX?/SPA? and `SL X? Y?` / `SU X? Y?` back, refuses (rc 3, no session file) unless everything matches the
  file within 0.001, and writes `tools/bench/motor_session.json` {started, limits_readback, limits_file,
  tolerance}. `--session end` writes the release values, verifies them and deletes the session file.
  `--execute` refuses unless the session file exists AND the sender's fresh readback — taken inside the same port
  open as the transmit, before it — matches the file; the gate re-checks that same readback line afterwards.
- `tools/motor_send_pi.ps1` and `tools/motor_asi_io.ps1` gained `limits-set` / `limits-release` modes and lost
  their private re-checks (PI's own `0..39`, ASI's own anchor-distance test), replaced by the readback-matches-file
  check. The PI poll now halts on `ExpectHi + 0.5` instead of a hardcoded 39.5; the ASI poll halts outside the
  SL/SU window. Never WPA, never SS Z.
- `tools/bench/selftest_motor_gate.py` DELETED, replaced by `tools/bench/selftest_motor_gate2.py` (no port,
  injected readbacks): **74/74 PASS, `BGRUN END rc=0`**, `tools/bench/selftest_motor_gate2.log`.
- `tools/hooks/guard_bash.py` needed NO change: no file name that its motor rules match has changed, the new
  self-test is covered by the existing `selftest_motor_gate` alternative, and the `p2_*.ps1` query scripts still
  pass (cases 19d/19e).

## §2 The live run, 15:37 — `tools/bench/motor_gate2_live.log`, 8/10 gates, 14 s

PASS: L1 session start (PI TMN 0 / TMX 39; ASI SL −3.847494/−4.774393, SU 0.152497/−0.774402) · L4 `MOV 1 0`
(already at 0) · L5 `M X=-16475` reached −16473 · L6 `M X=-18475` reached −18473 · L7 `HOME X` refused by the gate
(code 3, nothing sent) · L8 release (TMX 52, SL/SU ±500, session file deleted) · L9 re-arm (TMX 39, SL/SU back;
**the limits are LEFT ON, as the user wanted**) · L10 exactly five transmits reached a port.

FAIL: L2 `MOV 1 5` and L3 `MOV 1 40`. Both answered **`ERR? right after send = 5`** with `POS?` unchanged at
0.00000 — the sender's own "before" line reads `SVO?=1=1 FRF?=1=0`, i.e. **the axis is not referenced**, so the
controller rejects the move before the soft limit is ever consulted. The ERR-7 limit refusal was therefore not
re-demonstrated in this run (it was measured at 15:08 in `tools/bench/p2_pi_softlimit_test2.log`, with FRF=1).
The same ERR 5 appeared in the very first SPA run at 14:50 (`tools/bench/p2_pi_softlimit_test.log`), before any
of today's gate changes existed.

## §3 Relocated verbatim from STATUS.md's lock block (cycle-24 and earlier dispatch lines)

```
  prev_note:   # 13:3x: cycles 10 (firefighter, exited without running the recipe) and 11 (opus) KILLED by the user; their LabVIEW (pid 14440) closed; original md5 C39F36E0 unchanged.
  prev:      # free since cycle-24 firefighter dispatch 1 (material, 13:14-13:18, MEASUREMENT ONLY - lock taken over from the STALE cycle-23 dispatch-5 line, that cycle having been killed): diag_fstunnel_wireterms_panel run 2 = 12/12, rc=0, `tools/bench/diag_fstunnel_wireterms_panel_run2.log` (run 1 rc=1 NON-RESULT, own KeyError, `…_panel.log`). 🆕 **894 AND 1356 ARE NOT ORPHANS AT `_v1.py:403` - each has TWO terminals, one source, and the far end is a FRONT-PANEL object**: #894 = PN #145 `error out` T[3] (src) -> panel INDICATOR `error out 3` #825; #1356 = panel CONTROL `index 2` #1334 -> IndexArray #151 `index` T[2] (sink). Neither panel object is an endpoint of the recipe's six wire sites. `Wire.Is Broken?` at :442 has NO measured route for 894/1356/384 (no sink node terminal). ONE throwaway scratch created and DELETED, no original opened, nothing saved, handles 30,360->30,697, all 95 originals md5-identical BEFORE AND AFTER, no motor/serial/camera.
  prev2:      # free since cycle-23 dispatch 4 (12:32-12:40): diag_fstunnel_preclean_twins (11/14, rc=1 - gate P4 REFUTED, see below) + diag_fstunnel_orphan_timeline (8/9, rc=1, the one FAIL is the checker's own docstring). Three throwaway scratches created and DELETED, no original opened, nothing saved, handles 30,369->30,740, all 95 originals md5-identical BEFORE AND AFTER, no motor/serial/camera.
```

## §4 Relocated verbatim from STATUS.md's OPEN items 51 and 52

```
51. ✅ **CLOSED (cycle-24 firefighter, run 1):** the firefighter rewrite of `_v2.py` had already inverted A0a to expect `{}` on the fresh copy and added the A0h RBW-at-B4 repair; run 1 measured A0a `{}` twice, A0h `[894,1356]` twice, repair 0→1 twice, 38/38 gates. ✅ **b ALSO CLOSED** — cycle 25 corrected `docs/toolkit-capabilities.md`'s donor-orphan lines (§584 ff.); `doc_lint` names no fail/warn on that file.
52. ⚠️ **audit_cycle window clipping (cycle-23 retrospective, `device-failed`):** the cost audit counts a whole log whose mtime is in the window even when the log STARTED before it — 72 pre-window minutes imported from `tools/bench/cycle_5.log`; SECOND in the cycle-24 retrospective (10 min); **THIRD in cycle 26's — 23:23 and $13.7777 imported from `tools/bench/cycle_12.log:1`, true review time 7:43** (`archive/peer/2026-09-18-retrospective-cycle26.md:178-186`, `VIOLATION: device-failed`, threshold 1). 🔴 **JUDGEMENT (cycle 26): per-run clipping is a ~10-line REPAIR of an existing device, not a NEW device, so the 08:53 order does not forbid it — deferring it in cycle 23 read that order too widely. It is the FIRST item of the next cycle, and until it is done no `audit_cycle` cost line is quotable.** Related and now measured: `_v2` has NO stop record at all (`py tools/stop_record.py list` = 3 records, `_v0`/`_v1` RELEASED + `motor_wiring_check.py` STOPPED), consistent with its prior-art review emitting no machine verdict; verdict-emission in `prior_art_review.py` stays deferred.
```

## §5 Relocated verbatim from STATUS.md `## NEXT` — the four re-plan options and the "only after the user has answered" paragraph, both SUPERSEDED by the user answer of 14:2x ("D0, D1, D2 순서로 진행하면 좋을듯", docs/cycle27-plan.md)

```
🔴 **러너 정지됨 (9행 `STOP`) — 사용자 결정이 필요합니다. 세 번째 연속 성과 리뷰 실패(OPEN 32).**
2026-09-18 13:35 리뷰 7× `OUTCOME-VIOLATION` (`archive/peer/2026-09-18-outcome-review-20260918.md`): 누적
174 ops · 123 recipes · 235+ peer calls인데 실험에 쓸 수 있는 VI는 **0개**. 규칙(CLAUDE.md:450-453)상 답은 또
하나의 장치가 아니라 **사용자와의 재계획**입니다. **전문(코덱스가 작성) → `archive/prose/2026-09-18-replan-cycle26.md`.**
아래 넷 중 하나를 골라 9행 `STOP`을 지우고 러너를 다시 켜 주세요:
1. **(권고)** 2026-09-16에 이미 고르신 A안을 실제로 완성 — 원본 복사본 + 정지/종료 + 파일 저장, 프레임 루프와
   커널은 그대로(연산 변경 0 ⇒ 규칙 1a 위험 0, 무인 반복 가능, 이후 CPU/GPU 커널 교체가 들어갈 그릇이 됨).
2. 성과 리뷰의 최단 경로 — 원본 복사본에서 **트래킹 커널 호출만** CPU-병렬 커널로 교체, 픽스처 재생 + 라이브 90 Hz 5분.
3. GPU 먼저 — 기존 순서(GPU 먼저, CPU 나중)대로 GPU 트래킹 최상위 VI부터.
4. 인프라 계속 — `docs/cycle21-plan.md` 3단계(모터 리밋 체크 A, §A.1 읽기 전용 분석, 모터 구동 없음)부터.
**Then, ONLY after the user has answered.** Write the next plan file — `docs/cycle<N>-plan.md` with N = 27,
carrying `supersedes: [docs/cycle21-plan.md]` and a `## Pre-decided` section — for the option they chose, and set
`docs/cycle21-plan.md` to `superseded`: cycle 21 has **nothing left to run** — its step 2 closed in cycle 24's run 1, and its step 3
(motor-limit check A, `docs/motor-limit-assurance-plan.md` §A.1, read-only, no motor moves, SETTLED — do not
redesign it) is option 4's content, not a default. **If the answer is option 1**, the first build is: copy
`Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` into claudeDev (never touch the original; md5 before AND
after), add real stop/shutdown + the file writing, leave stages 0–3, the frame loop and every kernel untouched, and
run it unattended through the approved bead-pick GUI route (rule 1c', `tools/lv_gui.ps1 -Exception Approved
-Evidence "user 2026-09-17 bead-pick option 1"`). **No answer yet ⇒ do not start a cycle**; the `STOP` line is the
runner's handle (`tools/cycle_runner.py:54`, `^STOP\b` in the first 60 lines) and only the user removes it.
```
