# Brief for card 129-1 (cycle 129 judgement) — decisions: `docs/d1-loop12-17-split-plan.md` Pre-decided 261(d), 262(b), 263(b)

OFFLINE ONLY (no LabVIEW, no COM, no recipe launched). This is the unfinished remainder of card 128-5.

## 0. Time arithmetic (budget 50 min; the 60-min backstop refuses NEW bgruns after bind + 60)
- split + finalize both halves + predictions + two recipes: ~15 min (128-5 built the 70-action input and its replay in ~8 min)
- dry and prerun, each recipe in its OWN process (4 short runs): ~2 min
- `--scratch-required` on both recipes: ~1 min
- prior-art review(s), run concurrently, waited on in the foreground: ~10–13 min
- total ≈ 30–35 min, leaving ~15 min slack. Report your real minutes; `cost.minutes` must match bind → return.

## 1. Input (do not rebuild it)
`tools/bench/plan_ring_p3b_in.json` md5 `08fa224112606aedd4a15ec378268d88` = 70 actions (25 create + 16 wires + 14 crossings
+ 15 RLE), replays end to end on P3a with end cdiff 16 == P3a's (`plan_ring_p3b_make_c128_5.log` M0/M8/M8b/M11). Base = the
bed `claudeDev\D1_ring_p3a_20261001_180540.vi`, md5 `4dfa44aac8fb32f706b3eb792ee7d3cc`. How the unsplit plan was finalized
before: `tools/bench/plan_ring_p3b_make_c127_3.log`. `plan_ring_p3b.json` (4003eaa5), its `_pred` and
`tools/recipes/stage_d1_ring_p3b.py` are STALE: do not use, launch or delete them.

## 2. Split (PD261(d))
`plan_ring_p3b1.json` and `plan_ring_p3b2.json`, each ≤ 40 actions counting every create, wire, crossing and RLE row:
- dependency-closed — no P3b-1 row needs an object, terminal or wire made by a P3b-2 row;
- `IMAQ Copy` and ALL its guard rows (Unbundler #157 donor, Select #529 donor, I32 −1 constant and their wires,
  `element#0` → Select `s`, BufNum crossing → `f`, Select out → `Num(i)` element) in the SAME half;
- each RLE row in the half that creates its loose end;
- P3b-1 base = the P3a bed above (real). P3b-2 base = stagesim's END graph of P3b-1, `base.provisional: true`,
  `sim_of: {plan: plan_ring_p3b1.json, md5}` (the pipeline form; it is rebased after P3b-1's artefact exists).
- Equivalence check: P3b-1 then P3b-2 replayed in sequence reaches the same END graph as the unsplit 70-action replay
  (same end cdiff rows, same object/terminal/wire counts). Report both numbers.

## 3. Predictions per half (written to each half's `_pred` file)
- Error List after the half: total and per class, every NEW item named with the row that leaves it (start: P3a = 55 =
  54 + `w27378`'s loose end; RLE of `w27378` removes it).
- The read-back prediction PD262(b): after the Unbundler → Select wire, the bound Unbundler terminal reads back `status`;
  the P3b-1 recipe carries this as a gate that FAILS otherwise.
- Census: class deltas where `census_samples.json` (md5 205a7f23…) can derive them; a create row it cannot derive is
  listed as CENSUS-UNPREDICTED (PD261(c): the scratch run measures it; never type a number by hand).

## 4. Recipes
`tools/recipes/stage_d1_ring_p3b1.py` / `_p3b2.py` on stagekit, ≤ 120 lines each, inputs only — every row from the finalized
plan file (rule 8), modelled on `tools/recipes/stage_d1_ring_p3a.py` (md5 3aa685de…, the last clean ring launch).

## 5. Checks (out of process, one command per run)
`py tools/stage_prerun.py --dry <recipe>` then, separately, `--prerun <recipe>` for BOTH recipes; then
`py tools/stage_prerun.py --scratch-required <recipe>` for both (record exit code + line; P3b-1 gets a full scratch run
regardless, PD261(c)). A gate refusal you believe wrong: `py tools/gate_fp.py log ...` and return BLOCKED — no bypass.

## 6. Prior-art
Dispatch `tools/prior_art_review.py` for P3b-1 (new create classes Unbundler, Select from vi.lib byte copies). If P3b-2 is
NOT a proven pattern (no PROVEN-PATTERN from the gate logic), dispatch its review too, concurrently. Wait for ANSWERED and
return each verdict + archive path + verdict card. **Do NOT annotate the reviews and do NOT write REFUTED:/FIXED: lines** —
the judgement session does that (retrospective-cycle128 finding 7).

## 7. Return
`result/1` (also `tools/bench/cards/result_129-1.json`), validated: per-half action counts by kind, the cut boundary (the
first P3b-2 row and why it cannot move), the equivalence numbers, prediction file paths + md5, recipe md5s, the four
dry/prerun result lines, both `--scratch-required` lines, prior-art verdict(s). At the first unexpected result: finish the
step, record facts, return. A tool defect found on the way is recorded, not fixed (tool edits only where the split itself
needs them, self-tests green).
