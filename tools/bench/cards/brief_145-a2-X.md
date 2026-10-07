---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a2-X — OFFLINE facts for X11 (PD351(d)): Build Array #2626 open row (read-only, no re-cut)

PD351(d): the s05 plan wires inputs on Build Array `#2626` (`p4_w_tp_row` / `p4_w_rp_row`) while `(2626, array)` is an OPEN row whose
licence names only `plan_l2b1.json`. This is a judgement item; this card only reports FACTS, with `file:line` for each. No plan, pred,
recipe or tool is edited; nothing is launched.

## Questions (answer each with file:line)
1. In `tools/bench/plan_ring_p4_v18.json` (2ea6cafa): which action(s) / op id(s) CLOSE the open row (2626, array) — i.e. wire or consume
   the Build Array `#2626` output — and in which P4 session (by the s04 plan = ops 79..97, and the v18 op ranges after it) does that op fall?
   If v18 never closes it, say so.
2. What do v18 ops 118 and 119 wire on `#2626` (terminal names, sources, sinks, action ids)?
3. What exactly does `tools/bench/plan_l2b1_licence.json` (efbc8bcc) license (which rows, which plan, which reason), and where in
   `plan_l2b1.json` is `(2626, array)` produced?
4. State, as a fact, whether `plan_l2b1_licence.json` covers `(2626, array)` as it is used by ops 118/119 — yes / no / partly, with the
   exact lines. **No licence = no re-cut:** do not propose or make a plan change; the judgement session decides.
5. Which gate / check (`stage_prerun.py` / `stagekit` / `stagesim` line) raises or would raise the open-row refusal for (2626, array),
   and what text it prints (quote one line).

## Never
- edit any plan, pred, recipe, stage tool; launch anything; touch LabVIEW, the camera or a motor; read `archive/`.

Facts file: `tools/bench/diag_c145_a2_x_facts.md` (answers 1-5, each with file:line).
