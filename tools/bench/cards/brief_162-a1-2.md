---
card: 162-a1-2
status: current
date: 2026-10-10
---
# Brief 162-a1-2 - RETRY of 162-a1-1 (BLOCKED before launch by the launch gate); the ONE LabVIEW card

Read `tools/bench/cards/brief_162-a1-1.md` (and through it brief_161-b3-1 ...) and `tools/bench/diag_c162_a1_1_facts.md` (md5 b52d5f48e74a212be248adeed72335b7). This brief is brief_162-a1-1 with ONLY the deltas below.
Card 162-a1-1 read all inputs equal, `--scratch-required` rc 3, and then `check_launch` on the full scratch command REFUSED for two true reasons (its facts sections 3-4). Nothing was launched, no LabVIEW opened.

## Deltas against brief_162-a1-1
1. **Label prefix:** the card rule is now `DRY-UNVERIFIED-OK: CEN2 new-object census` (a true prefix of the gate label, `stage_prerun.py:4980`).
2. **The scratch recipe gets its own dry + prerun, OFFLINE, before the launch.** Cause 2 of the refusal: `stage_d1_ring_p5s02b_scratch.py` (md5 3f6fb898, sha256 2235182c68b8) has no prerun PASS record. Run, as the gate text says,
   `--dry` and `--prerun` of `tools/recipes/stage_d1_ring_p5s02b_scratch.py` exactly as the earlier pair shape p5s02a did (look at `tools/bench/` logs of the p5s02a scratch prerun for the command form). This is OFFLINE (COM stubbed, no LabVIEW) and EDITS NOTHING in the recipe. It is
   part of this card because the gate demands it, not a redo of the main recipe's PB / X10 / dry / prerun (those stay as accepted). If the dry is PASS-UNVERIFIED again, the only unnamed gates must be the CEN2 label above; any other unnamed gate = RETURN with facts.
3. **Launch log name = the recipe's own constant**, `tools/bench/diag_c161_p5s02b_scratch.log` (`stage_d1_ring_p5s02b_scratch.py:29`; the METER lines are read back from that exact file at `stagekit.py:2836`, so a different `--log` would make GATE MEM FAIL). No recipe edit.
   First confirm that file does not exist (a stale file would feed stale METER lines; if it exists, move it aside with a dated name, never delete). After the run, make a byte COPY named `tools/bench/diag_c162_p5s02b_scratch.log` and quote both md5s in the facts, so the name in the purpose exists.
   Report this in the facts as a stated deviation from the literal log name, with the reason.
4. **`check_launch` is run on the FULL command** (not on a bare path - a bare path returns a vacuous ALLOW, facts section 3): `py tools/bgrun.py --material --max-min 50 --unverified-card tools/bench/cards/task_162-a1-2.json --log tools/bench/diag_c161_p5s02b_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py`. It must ALLOW before the launch; any other result = RETURN with the text.
5. **guard_peer:** the newest failing log `diag_c162_a1_1_discrim.log` is the designed-FAIL discriminating test of the already archived review `archive/peer/2026-10-10-c162-a1-1-checklaunch.md`. If `guard_peer` blocks on it, dispatch one `-Agent claude -Role hypothesis` review that names that log (flags.peers); do not use `PEER_GUARD_OFF`, do not edit `tools/hooks/**`.
6. Everything else as brief_162-a1-1: ONE scratch, any BLOCK gate FAIL or peak > 675 = RETURN with facts (no adopt, no second run, copy kept unloaded), the `memory_model.json` single `load_by_vi` entry after adoption, Error List vs 79ec3207, graph json + md5, the pred census, originals hashed unchanged,
   LabVIEW closed and verified gone. Facts file: `tools/bench/diag_c162_a1_2_facts.md` (<= 45 lines); helper scripts `diag_c162_a1_2_*` / `prep_c162_a1_2_*`.
