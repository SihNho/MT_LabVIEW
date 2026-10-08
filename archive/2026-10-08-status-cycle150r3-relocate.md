---
type: archive
date: 2026-10-08
source: STATUS.md ## NEXT (cycle 150 hand-back 2 judgement)
---
# STATUS relocation, cycle 150 hand-back 2 — verbatim, nothing rewritten

## §1 — the cycle-150 ROUND 2 purpose paragraph (replaced in STATUS by the round-3 paragraph, PD366)

🟢🟢 **CYCLE 150 PURPOSE, ROUND 2 (judgement 2026-10-08, hand-back 1; `tools/bench/next.json`; `docs/d1/ring-p4c.md` PD365; round 0 → `archive/2026-10-08-status-cycle150r2-relocate.md` §1):** round 1 re-cut s07 at the measured s06 load (`tools/bench/plan_ring_p4_s07v18.json` 10a4f59a, v18 ops 136..165, 30 actions, MAIN 678.8) and moved STATUS to 110 lines, but `stage_prerun.py --rebase` REFUSED it: `rebind` keys old terminals by NAME (`tools/stage_prerun.py:3829`), so the renames LabVIEW made in s06 on #2626/#9503 (licensed) made two old nodes look new (`tools/bench/diag_c150_a1_3_facts.md`). **First act = ONE tooling card, ALONE: `rebind`'s old-terminal key made name-free (uid, owner, term class, direction; a renamed old terminal becomes a RENAMED-OLD info line) + new `tools/bench/selftest_rebind_c150.py` (R1 refuses on the old code, binds after).** Then s07 rebased on `graph_ring_p4s06_20261008_192149.json`, pred/recipes regenerated, licence `plan_ring_p4_s07v18_licence.json` written by script → ONE scratch on a new byte copy of s06 → adopt as `D1_ring_p4s07_*.vi` → full Error List (item 6?) + graph read + `load_by_vi` → ALONE: the review-parser device on `violations.py`, `cycle_runner.py`, `audit_cycle.py` (the `tools/hooks/guard_peer.py` site and PD361(c)(1) go to the gate-fp queue for the chat: no runner card edits hooks) → s08 made, not run. **For the chat's chat-T6 merge:** cycle 150 changes the main tree's `stage_prerun.py` (`rebind` key only) and those three parser sites; keep both sides.
