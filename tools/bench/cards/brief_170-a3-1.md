---
card: 170-a3-1
status: current
date: 2026-10-13
---
# Brief 170-a3-1 (assignment 170-3, the ONE retry of 170-a2-3) - re-hash, then build the paced stand-in pair (PD411(b))

Read first: `docs/d1/ring-p6.md` PD410(d) and PD411(b); `tools/bench/cards/brief_170-a2-3.md` (the build, UNCHANGED - steps 1-6 apply as written);
`tools/bench/cards/brief_170-a2-5.md` (launch-gate release, same method); `tools/bench/cards/result_170-a2-3.json`; `tools/bench/diag_c170_a2_3_facts.md`.

## Step 0 - re-hash (offline, before any LabVIEW). Drift = RETURN BLOCKED with the differing file, no LabVIEW.
md5 (first 8 hex) must equal: bed `claudeDev\D1_ring_p6_20261012_212645.vi` c2d9c13c; graph `tools/bench/graph_ring_p6_20261012_212645.json` fbc7b7ee;
S1 `claudeDev\D1_s1_copy.vi` 3e3d23ce; S1 replay `claudeDev\replay\D1_s1_replay_20260925_075422.vi` 126f8497;
stand-ins `replay\replay_get_buff_image.vi` 842ecad9, `replay\replay_get_image_cal.vi` afce0d04, `replay\replay_imaqdx_get_image_buf.vi` a89dafc1;
frame manifest of `G:\m8_replay_frames` 9055d98a (find the manifest file via `tools/bench/p6_replay_facts.md`); compare `tools/bench/m8b_replay_compare.py` c2efe10d;
also 75773b0d (`D1_ring_p5_20261010_172913.vi`) and 7f2582ae (P5-1 file named in `docs/d1/ring-p5c.md`/INDEX) unchanged. Use `hashlib` via ONE shared helper if `stagekit` has one; quote each hash in the facts file.

## Release the launch gates (as brief_170-a2-5)
1. `check_launch` PD287(a): this card names the stub-only gates in `rules` ("DRY-UNVERIFIED-OK: A1; A2; A3; A4; B1; G2; C1; C2"); the launch passes `--unverified-card tools/bench/cards/task_170-a3-1.json`.
   Use the label prefixes the dry printed (`diag_c170_a2_3_dry.log:122`); do not relabel a refused gate as a row.
2. Prerun X10 (UNMEASURED at `diag_c170_a2_3_prerun.log:44`). DO NOT edit `stage_prerun.py`, any hook, or any limit/coefficient. Levers, in order, stopping at the first that makes
   `py tools/stage_prerun.py --prerun tools/recipes/stage_replay_paced60.py` PASS on the model as is:
   (a) move the recipe's edits onto stagekit's `Stage._op` (a shared function) so X10 has an op count to model (`stage_prerun.py:68-75`; `stage_d1_m4b.py` `from_decision` rows are the pattern); re-run `--dry` and `--prerun`;
   (b) PD411(b): add `load_by_vi` entries to `tools/bench/memory_model.json` - AT MOST ONE PER VI THE RECIPE OPENS (a89dafc1, 842ecad9). Each entry is a MEASURED load: take MEM-after-load from a log line
   (the build's own first read or a one-open read-only session; say which), cite the log line next to the entry, model the format of PD408's c2d9c13c 603.7 MB entry (`memory_model.json` `load_by_vi`).
   Touch nothing else in the model (`fail_above_mb`, MEMSTOP, coefficients unchanged); the pass check is a JSON diff showing ONLY new `load_by_vi` keys; quote the new md5.
   If X10 still refuses after (a) and (b): RETURN BLOCKED with the verdict text. There is no third lever, no gate-to-row change, no bypass variable.
3. The recipe edit may need a prior-art review (guard_cycle: a recipe edited after its newest prior-art review). This card's `flags.peers` includes `priorart`: if guard_cycle refuses, run the review it names
   (`py tools/prior_art_review.py ...` as the refusal prints it) and release with the FIXED: line it asks for; if it still refuses, RETURN BLOCKED with the text.

## Build, gates and hygiene
Exactly `brief_170-a2-3.md` steps 1-6: both paced files, ExecState 1 warm AND cold, census checks, inputs a89dafc1 / 842ecad9 unchanged, refs balanced (live 0), `tasklist` shows no LabVIEW, 8 pinned VIs unchanged.
Facts: update `tools/bench/diag_c170_a2_3_facts.md` (<= 40 lines, every number with file:line), including the X10 PASS verdict quoted verbatim and, per new load_by_vi entry, the measured MB with its log line.

## Not in this card
No P6 replay copy, no plan literal, no leg, no compare, no hook/stage-tool/plan/STATUS/INDEX edit. A new unexpected result = RETURN with the facts (this is the retry; it is spent).
