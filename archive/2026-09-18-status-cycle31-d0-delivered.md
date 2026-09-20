---
type: archive
status: archived
date: 2026-09-18
cycle: 31
tags: [status, d0, delivered, gui, narrative]
---

# Cycle 31 — D0 delivered. Narrative relocated verbatim from STATUS.md (rule 4)

## §1 — the user's live observation, VERBATIM from STATUS.md `## NEXT` lines 79-98

> 🔴 **USER OBSERVATION 2026-09-18 17:2x (watching the live D0 run of cycle 31, `drive_original_copy_v4.py`):** the
> three bead clicks landed (red circles on the image) but **the `Done Picking Beads?` Yes button was NOT hit** — the
> driver clicked (1114, 915), the button is at about (1178, 864) on screen (`tools/bench/p3_done_check.png`, 17:28).
> **User's diagnosis: the front panel was NOT MAXIMISED, so the panel origin/size differ from v3's derived rect** (v4
> STEP 7 reused v3's V6 offsets: rect (-6, 51, 1930, 1107)). Also: `Count` read 1 after 3 picks. **Next cycle:**
> (1) maximise the front panel window (or read its real rect with `lv_gui.ps1 -Action rect`) BEFORE deriving any
> click; (2) locate the Yes button from the live screenshot (its label text / red "Yes" box), never from another
> copy's offsets; (3) verify every click by a post-click readback (`Done Picking \nBeads?` value or `Count`) before
> the next step. Do not treat run1's pick stage as passed. **USER RULE 2026-09-18 17:5x — "GUI 컨트롤 중에는 반드시
> 캡처 이미지 비교하는게 필요할듯": EVERY GUI action = capture BEFORE (locate the target in that capture — colour/
> template match on the red Yes box, OCR of the label, or the control's live screen rect), act, capture AFTER and
> CONFIRM the expected change (button state / `Count` / a window) before the next step; no change ⇒ FAIL and stop.
> Derived or remembered coordinates are never clicked blind.** Add this to `docs/cycle27-plan.md` Pre-decided. Side fact from the same screen: the running copy shows
> `Max Travel Limit` = **39.000000** — the original VI reads the controller's `TMX?` at startup, so the controller
> limit set by `motor_gate.py --session start` reaches the original's own panel (`Max Trans Pos` still 40.94).
> **MEASURED 17:49 after the v4 run ended and LabVIEW was gone** (`tools/bench/p3_pi_query_after_d0.log`): `TMX?=39`,
> `TMN?=0`, `RON 0`, `FRF 1`, `POS 0` — **the original's startup did NOT overwrite the controller limits or the
> reference**. v4's G25 FAIL ("TMX?=None, gate exit 3") was the gate refusing while the VI still held COM3 — a
> port-busy false failure, not a limit change; read TMX? after the VI has released the port. v4's other two FAILs
> (R4 pick loop never ended; run2 never started) are both the missed Yes click above.

### §1a — what the measurement said about the user's proposed cause

The user's **remedy** was right and is now a standing rule (`docs/cycle27-plan.md` Pre-decided 9). Their proposed
**cause** was not what the machine reported: the front panel rect measured `(-6,51,1930,1107)`, size
`(1936,1056)`, delta `(0,0)` against v3's V6 rect — three independent times (v4 gate 7, the liveness run, v5) —
so the window was neither un-maximised nor moved. The fault was that the *click point inside* that identical
window had been inherited from a different VI, and control positions are not readable over our COM path
(`tools/bench/diag_d0_inventory.log:56`, gate B1: every panel row `class None pos None`). A window rect is not a
control position; that is why `gate 7` passed while verifying the wrong invariant.

## §2 — cycle 31's dispatch record

| # | agent | what | outcome |
|---|---|---|---|
| 1 | log-reader | facts from cycle-30's `diag_d0_inventory.log` + `diag_d0_trace_path.log` | 114 panel rows (60 CTL / 54 IND); `class`/`pos` `None` for all (B1 FAIL); save path/name are INDICATORS, so the destination arrives via a file dialog (`ReadWriteFile` uid 26615) |
| 2 | material | D0 prior-art review + guard probe | review already run by a sibling session at 16:58; **seven stop verdicts**; `tools/stop_record.py` hard-stopped `build_d0_harness_v0.py` |
| 3 | material | build + run `drive_original_copy_v4.py` on the 4.5 copy | 13 pass / 3 fail — the done click did not end the picking loop |
| 4 | material | mandatory hypothesis peer review + liveness measurement | peer **REFUTED** the frame-starvation hypothesis; click delivery **proven**; the pixel was wrong |
| 5 | material | build + run `drive_original_copy_v5.py` with LOCATED click points | **39 pass / 1 fail — D0's done-when MET on both legs** |
| 6 | material | `tmx_from` parser fix + retrospective | self-test 10/10; retrospective ANSWERED |

## §3 — the judgement calls made this cycle

1. **The D0 prior-art review was ACCEPTED IN FULL**, and `tools/recipes/build_d0_harness_v0.py` was ABANDONED and
   never created. The review's headline was correct: `tools/bench/drive_original_copy_v3.py` had already executed
   every clause of cycle27-plan Pre-decided 3 on a plain copy (16/16, rc=0, 2026-09-17). D0's remaining content
   was the retarget onto the 4.5 copy plus four deltas, so the work extended v3 rather than duplicating it.
   Disposition: seven `FIXED:` lines in `archive/peer/2026-09-18-priorart-d0-harness.md`.
2. **The hypothesis peer's refutation was ACCEPTED.** The judgement session had proposed that the picking loop was
   starved of camera frames, on the strength of three readings agreeing. The peer showed two of the three
   (`current image number` uid 34200, and the stop Booleans read inside `Diagram#639`) are **stage-4** signals that
   cannot be consumed during picking — so they were never evidence about the picking loop at all, and
   `p3_done_check.png` showed the diagram drawing bead markers and computing `Bead Pos X/Y` while it ran.
3. **Panel parameters are RECORDED, never SET.** The harness reads and logs all 60 controls and writes none: the
   values saved in the copy are the ones the user last used, and inventing values would be a computation change
   under rule 1a. This narrows cycle27-plan Pre-decided 3's "sets the panel parameters by VI Server" and is
   flagged for the user to overturn if they meant otherwise.
4. **Every click point is located on this VI's own panel** (now the user's rule, Pre-decided 9).

## §4 — measured facts about this VI to carry into D1 (not guesses; each has a log behind it)

- **Locating a control**: `tools/bench/d0_locate.py` (template match on a reference patch) found the done button
  at box (1155,848)–(1200,876), centre **(1177,862)**, score 0.00 against a next-best of 28.35 among 7
  shape-passing candidates. The three `choose bandpass` Yes buttons located live at (174,352), box
  (116,319)–(233,385). Evidence crops: `tools/bench/d0_evidence_v5/`. Use it for EVERY click.
- **Control positions are NOT readable over our COM path** — `tools/bench/diag_d0_inventory.log:56` (gate B1):
  traverse classes `Control`/`Panel`/`Boolean`/`Path`/`Numeric` all return 0, `GObject` returns 9,996 objects of
  which **0 are panel uids**, and every row in `d0_inventory.json` is `class None pos None`. So the screenshot is
  the measurement, and a window-rect comparison is not a substitute.
- **The stop controls live in the frame loop.** `stop (end)` uid 7 and `stop (end) 2` uid 19587 are read inside
  `Diagram#639`, the frame-loop body. A VI-Server write to them means nothing until the experiment loop is
  running — where a single write idles the VI in **1.0 s with no re-arm and no Abort**, both legs. v4's
  "written True, never consumed" reading was taken during picking and proved nothing.
- **`current image number` uid 34200 is the frame loop's index**, so it reads 0 for the whole of stages 0–3. It is
  not an acquisition-liveness signal during picking.
- **There is no save-path and no save-name CONTROL.** `Cal File Path` 27930, `Track File Path` 28450 and
  `File # Saved` 6 are INDICATORS; the destination arrives through a **file dialog** (`ReadWriteFile` uid 26615,
  terminal `prompt (Choose or enter file path)`), answered by v2's `answer_save_dialog`.
- **Read `TMX?` only after LabVIEW has exited.** While the VI runs it owns COM3/COM4 and the gate refuses with
  "액세스가 거부" — a port-busy false red, not a limit change (v4 gate 92, liveness gate 93; both re-read clean
  afterwards).
- **The original's startup does not overwrite the controller limits or the reference** — measured 17:49:
  `TMX?=39`, `TMN?=0`, `RON 0`, `FRF 1`, `POS 0`. The running copy's panel shows `Max Travel Limit` = 39.000000,
  i.e. the VI reads `TMX?` at startup, so the gate's limit reaches the VI's own panel.
- **Unexplained, and possibly relevant to D1**: `Count` reads 1 after 3 registered picks, in v4 and v5 alike, even
  though the VI drew all three red markers (retrospective-cycle31 F6).
- **Panel parameters**: all 60 controls are READ and logged, none written (judgement §3.3 above).

## §5 — STATUS.md's D0 banner, RELOCATED VERBATIM 2026-09-18 19:1x (rule 4; STATUS had reached 118 lines)

Moved by cycle-34 material dispatch A. Nothing rewritten, nothing deleted; STATUS keeps one line and a pointer here.

> 🎉 **D0 IS DELIVERED (cycle 31, 18:08–18:13) — the first runnable experimental deliverable this project has had.**
> `tools/bench/drive_original_copy_v5.py` = **39 pass / 1 fail**, both legs: picks → done button → all three `choose
> bandpass` panels → save dialog → experiment loop (**frames 8326→10856, lost 5**) → stop by the VI's OWN control in
> **1.0 s, no Abort** → `tra001-000` 285,369 B + `cal001` 171,552 B; then the whole thing again. Original md5
> `c39f36e0…` identical before and after; copy never saved. The one red (gate 93) was a PARSER false red, **now
> FIXED** (self-test 10/10). ⚠️ **The VI moved the PI magnet 0 → 30.000 mm under its own control, inside the 0–39
> envelope, and the limits held** (Pre-decided 4's assumption, measured true). Narrative + the user's live
> observation → `archive/2026-09-18-status-cycle31-d0-delivered.md`; earlier banners → `…-cycle26-stop.md`.
> 🆕 **USER RULE 17:5x, now `docs/cycle27-plan.md` Pre-decided 9 — EVERY GUI action is capture → locate → act →
> capture → confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.
