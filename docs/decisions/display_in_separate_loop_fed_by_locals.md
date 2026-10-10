---
name: display-in-separate-loop-fed-by-locals
description: "The user's 2026-09-26 design ruling — front-panel plots (Force vs Extension, and by extension other pure-display indicators) are drawn by a SEPARATE display loop on its own clock, fed by local variables written from the frame loop; never by an every-N-frames gate inside the frame loop"
metadata:
  pinned: false
type: decision
status: in-force
date: 2026-09-26
source: memory/display_in_separate_loop_fed_by_locals.md
---

# Plots live in their own display loop, fed by locals (user, 2026-09-26)

Cycle-94 timing showed the 'Force (pN) vs Extension (nm)' graph costing ~10 ms of every frame at 15 beads (not saved,
not driving motors). The judgement session proposed redrawing it every N frames (a Quotient & Remainder gate inside
the frame loop) and asked the user (D-2026-09-26-02). The user answered with a different design:

> "그래프 플롯 기능을 혹시 별도 루프로 두는 것은 어떤지? 로컬 변수에 데이터들은 다 입력하고 데이터 플롯은 별도 루프로" →
> "이대로 진행"

## How I apply it

- A display-only indicator is NOT gated inside the frame loop; the frame loop writes its data to a local variable and
  a separate display loop, on its own timer (panel control, ~10 Hz default), reads the locals and writes the
  indicators. This follows the earlier rulings: locals not queues for loop-to-loop signals (1c''), live display 10 Hz
  is enough but must be a runtime control (2026-09-14), and the seven-loop plan's display loop.
- It is a scheduling change only (rule 1a): the same arrays reach the indicator, later; saved data unchanged.
- Cost of the local-variable array write per frame is MEASURED before more indicators are moved into that loop.
- Recorded in `docs/d1-loop12-17-split-plan.md` Pre-decided 210; the N-gate work (fgate, PD205-209) was dropped.
- Pattern: when a judgement session offers a speed-up as a local patch, check whether the seven-loop design already
  has a home for it; the user prefers the structural answer over the quick gate.
