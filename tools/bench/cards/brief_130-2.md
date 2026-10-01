# Brief 130-2 — tooling debt (offline, beside 130-1)

Decisions applied: `docs/violation-decisions.md` 2026-10-02 02:57 (stop-record predicate, fp-22) and 01:01 (card_clock →
`protocol.py validate`); PD266(d)/PD267(c) in `docs/d1-loop12-17-split-plan.md:2954-2973`. Card 130-1 is live at the same
time and OWNS `tools/stage_prerun.py`, `tools/stagesim.py`, `tools/stagexec.py`, all `plan_ring_p3b*` files and the P3b
recipes — never edit those here (fp-19/20/21 are stage_prerun items and wait for a later card).

Items (each independent; do them in this order, ~8 min each, total ≤ 50 min):
1. **fp-22 — stop record** (`tools/hooks/guard_bash.py:248` and the predicate feeding it): a recipe path counts as a
   LAUNCH only in python command position (`py …/tools/recipes/x.py`, `py tools/bgrun.py … -- py -u …/x.py`), never as an
   argument (`md5sum`, `grep`, `gate_fp.py log --cmd "…"`). Log fp-22 with `tools/gate_fp.py log` (the 129-8 `md5sum`
   case, `tools/hooks/material_marker.log` 2026-10-02 02:42:47), fix, self-test (extend `selftest_stoprecord_*` or a new
   one: the md5sum, grep and gate_fp-log forms PASS through; a real launch is still recorded), then drain fp-22.
2. **Drain fp-15, fp-16, fp-17, fp-18** (`py tools/gate_fp.py list` for their records). Each: fixed (path:line +
   self-test) or closed as NOT a false positive with the reason. fp-17's record text is just "3229" — read its full entry
   and say what it was.
3. **card_clock into `protocol.py validate`**: a result card whose clock is UNMEASURED → WARN, MISMATCH → FAIL; self-test
   on three synthetic result cards (OK, UNMEASURED, MISMATCH) plus `selftest_card_clock` still green.
4. **`docs/ring-buffer-design.md:23-24`**: mark superseded by PD238(c) (`docs/d1-loop12-17-split-plan.md:2256`) on those
   lines, nothing rewritten.
5. **gemini fact arm** (`tools/peer.ps1`): an EMPTY answer is not ANSWERED — fall back to the claude fact arm, as on
   error/timeout. Evidence of the bug: `tools/bench/peer_c129_6_undo.log:6-24`. Test without spending a real call
   (DryRun or a stubbed agent).

Every edited hook/tool: its existing self-tests rerun and listed with counts. Return at the first unexpected result.
