# Brief 97-4 — stage the display-rate-gated copy of S1 (plan Pre-decided 205(e) 2 + 206(b)(c)(f)(g))

Source: byte copy of `claudeDev\D1_s1_copy.vi` (md5 `3e3d23ce…`). Target: `claudeDev\D1_s1_fgate_<ts>.vi`, saved BY SCRIPT.
Uids and sets below are from `tools/bench/f1359_gate_facts_97.json`; resolve any uid the plan file needs from that
file or the graph, never by re-typing (CLAUDE.md "Stages are SIMULATED" 8).

Objects to create/move (this list IS the expected cdiff, besides tunnels LabVIEW makes):
1. New I32 front-panel control, label `Force graph: update every N frames`, default 9 (`set_control_label`, OpLabelSet_v0).
2. On diagram 639 (#637 body): Quotient & Remainder (x = #637's `i` #644 via wire w3268 → connect_from_wire; y = the new
   control's terminal), `Equal To 0?` on the remainder → boolean `upd`. Donors via stagekit copy_in (`stagekit.py:779`).
3. Case **A** inside diagram 7911 (#1359 body) (`gscript.case_in`), selector = `upd` through a NON-indexed #1359 input
   tunnel. Move into its ` True ` frame EXACTLY the 206(b) set: #8741, #8764, #8775, #8795, #27716, #28180, #28233, #29009,
   #11310 (and the `Exp Baseline` terminal #8476 if it sits in 7911, by the T3 route). Frame named ` True ` is read AFTER the
   boolean is wired. Every output tunnel of A set `use default if unwired` (`tunnel_use_default`).
4. Case **B** on diagram 639, selector = `upd`. Move into its ` True ` frame ONLY BuildArray #11261 and #8323's terminal.
   #11576 / #11608 stay OUTSIDE. The False frame of B is empty.
5. Nothing else is touched. Magnet2Force #28083, #8566, #8634 and the SR chain 9227 → #9018 → #9025 stay where they are.

Stage discipline: stagekit file ≤ 120 lines under `tools/recipes/stage_d1_fgate.py`; plan file under
`tools/bench/plans/`; dry run → offline pre-run → ONE real run (RETRY_CAP 2); MEMSTOP 700 MB private bytes; bgrun
`--max-min 45`.

Gates after the run (read-back, not from the recipe's own intent):
- ExecState 1 warm and after a cold reload.
- `computation_diff(S1, fgate)`: list every row; it must equal the objects in 1–4 plus the tunnels, and every moved edge must
  keep the same source uid:terminal → sink uid:terminal (through tunnels).
- A and B selector sources are the same `upd` wire; the gated nodes' owner is A's / B's ` True ` frame.
- The new control's label and default (9) read back.
- md5 + size of the saved file; S1 md5 unchanged; LabVIEW gone.
