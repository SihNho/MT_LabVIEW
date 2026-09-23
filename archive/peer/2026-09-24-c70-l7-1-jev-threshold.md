# c70-l7-1-jev-threshold

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2837  in 14 / out 9878 / cache-create 117546 / cache-read 728596  (105s, 11 turn(s))
- **date:** 2026-09-24 03:36:07
- **outcome:** ANSWERED (109s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION — attack the hypothesis below. Read-only.

Facts:
- Two runs of tools/recipes/stage_d1_l7_1.py failed gate P2a.
  - Run 1: tools/bench/stage_d1_l7_1.log lines 124-126 — acc_init row, single candidate, Jev p=0.582 (threshold 0.75).
  - Run 2: tools/bench/stage_d1_l7_1_r2.log lines 85-90 — err_R row, 4 candidates, best p=0.742 (it was 0.756 in run 1); margin to the runner-up >= 0.57 both times.
- Jev pair scoring: tools/jev_pairs.py. Gate/threshold: tools/recipes/stage_d1_l7_1.py.
- Plan: docs/d1-loop12-17-split-plan.md, ## Pre-decided items 168 and 169.
- Prior-art review r2: archive/peer/2026-09-24-priorart-c70-l7-1-r2.md (its remedy: "fix the intent line").

Hypothesis under attack:
"The failures are Jev score spread around a fixed 0.75 threshold on rows whose answer is already fixed by the original S1 edge; the remedy is Pre-decided 168 (S1-mapped rule rows, Jev only as an argmax check, stop on disagreement) and 169 (split into L7-1a save / L7-1b wire)."

Answer:
1. The strongest reason this hypothesis is wrong. In particular: does the low p signal a REAL mismatch — a wrong terminal name, wrong face/side, a defective intent line (cf. the r2 prior-art remedy), or a candidate table missing the true pair? Check the intent/candidate text in the logs and the recipe against the S1 edge.
2. Is Pre-decided 168 a rule-1a risk (CLAUDE.md rule 1a: the original's computation must not change) or a disguised threshold lowering that would let a genuinely wrong wiring row through?
3. What observation would falsify the hypothesis?
4. The cheapest discriminating test runnable OFFLINE (no LabVIEW), e.g. re-scoring err_R and acc_init N times via tools/jev_pairs.py with the current vs a corrected intent line, and what result would separate "score spread" from "real mismatch".


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

I've finished reading the logs, the decision records and the recipe, and I'm writing up the review now.

# Review: the "score spread" explanation for the P2a failures

**Verdict: the hypothesis is only half right.** For `err_R` it holds. For `acc_init` it is wrong: that score is low for a fixed reason in how the question is worded. The same wording also means `err_init` passed at 0.848 for a reason that has nothing to do with whether the wire is correct. Pre-decided 168 is acceptable under rule 1a, but only if a check that actually stops the run is added (point 2). It is not a lower threshold in disguise. The Jev check it keeps, though, adds almost no protection.

I did no web search. Every claim below concerns this project's own records, and I cite them by file and line.

## 1. The strongest reason the claim is wrong

**The `acc_init` score is not scatter; it is the same every time.**
- Its mean was 0.582 over 5 samples, and the gap between the highest and lowest sample was 0.08 (`tools/bench/decision_l7_1_init.json:94-95`). The threshold is 0.75, which is more than twice that scatter away. Random variation cannot explain it.
- The row Jev scored was `#781 'initialized array'` → `#24187 'total data array out'` (OuterTerminal). By that point the body rows had already been wired, so the new LEFT register's outer terminal had taken the name of `#376`'s *output*.
- The intent line (`decision_l7_1_init.json:6`) never tells Jev the sink will carry that name. So Jev saw a source called "initialized array" feeding a sink named after a different node's output, and it doubted the pair. That is a correct reaction to a misleading question.
- **The control case is `err_init`:** `#4910 'error out'` → `#24133 'error out'` scored 0.848 with a scatter of only 0.02 (`:17,35-36`). Its two ends have the same name only by coincidence. Nothing else distinguishes `err_init` from `acc_init`.
- **Conclusion:** on a row with a single candidate, Jev's PAIR score measures whether the names match, not whether the wire is correct. The pass at 0.848 was worth no more than the fail at 0.582.
- This is the r2 prior-art remedy ("fix the intent line"). It is also the w7337 case that PD 165 cites itself (p 0.464, stale terminal name).

**`err_R` really is scatter.** Run 1 scored 0.756 with a scatter of 0.10 (`decision_l7_1_body.json:37-38`), and run 2 scored 0.742. The correct pair ranks first by a margin of 0.57 or more, and the other candidates score 0.10–0.18. So the true pair is in the candidate list, and the terminal and side are correct. For this row the hypothesis holds.

**Alternative explanation for the evidence as a whole:** there are two different failures here, not one:
- `err_R`: random scatter around the threshold.
- `acc_init`: a PAIR question that cannot handle a register renamed after the wire it carries.

The hypothesis treats both as scatter, so the question defect stays in the system. The next single-candidate row whose names happen to match will pass for the wrong reason, as `err_init` did.

## 2. Is PD 168 a rule-1a risk, or a lower threshold in disguise?

- **Not a lower threshold.** The wire's endpoints come from facts: the S1 edge's source uid and terminal, plus the stage's own old→new register mapping. Reproducing the S1 source is exactly what rule 1a asks for. Running Jev as a first-place check and stopping when it disagrees is at least as strict as a plain rule row.
- **But the Jev check guards almost nothing.** In every row it runs on, Jev varies only which `#376` terminal is used. The register end is fixed by the recipe, and its inner terminals are all named `''`. So Jev cannot catch the mistake that matters, an err/acc register swap or a wrong left/right pairing from `add_sr`. That error is caught only by the `computation_diff` gate (PB, recipe line 102) and by the second-pass `Is Broken?` check.
- **The real rule-1a risk:** PB is **not fatal**. `s.gate(...)` defaults to `fatal=False` (`tools/stagekit.py:186`), and the recipe saves the artefact on lines 111-113 regardless of whether PB passed. Once 168 removes the p-gate, a wrongly wired L7-1b would be saved as the stage output with only a FAIL line in the log. **Condition for accepting 168: make PB `fatal=True` before the save in L7-1b.**
- PD 169 (split into L7-1a / L7-1b) is simply what "split and save" rule 3 requires. There is nothing to attack in it.

## 3. What would falsify the hypothesis

Re-ask `acc_init` with an intent line that names the live sink terminal. Something like: "…the NEW accumulator LEFT register's outer terminal, which now reads 'total data array out' because the register carries #376's accumulator".
- If p rises to about 0.8 or more with little scatter, the low score came from the question, not from scatter. That falsifies the hypothesis for this row.
- In the same test, blank the sink name on the `err_init` candidate (`''` instead of `'error out'`). If p falls well below 0.848, that confirms the coincidental name match inflated it.

## 4. Cheapest discriminating test (no LabVIEW; about 60 Jev calls, roughly $0.005)

Rebuild the candidate dictionaries from the `exec` and `row_key` fields in `decision_l7_1_init.json` and `decision_l7_1_body.json`. `write_record` was passed `cands=[]`, so `sink_state`, `scope` and `borders` were not saved and must be filled in by hand to match the logged candidate text. Then call `jev_pairs.ask_pair(line, c, n=10)` for each case:

| # | case | if it's scatter | if it's a question defect |
|---|---|---|---|
| a | `err_R`, current line, n=20 | mean ≈ 0.75 ± 0.05 | — |
| b | `acc_init`, current line | stays ≈ 0.58 | stays ≈ 0.58 |
| c | `acc_init`, corrected line | stays ≈ 0.58 | rises to ≥ 0.8 |
| d | `err_init`, sink name blanked | stays ≈ 0.85 | drops a lot |
| e | negative: `#4910 'error out'` → acc LEFT register, sink named `'total data array out'` | — | should be low; if high, Jev only matches names and adds nothing |

**How to read the outcome:**
- If (a) centres on 0.75 while (c) rises and (e) stays low, `err_R` is scatter and `acc_init` is a question defect. Then 168 is fine for `err_R`, but the intent-line template must also be fixed.
- If (c) does not rise and (d) does not drop, the hypothesis holds as stated.

What would change my mind: (c) staying at about 0.58 while (d) stays at about 0.85. Then name matching would not be the cause, and I would accept the scatter explanation for both rows.

## Sources

(extract from answer)

## What was done with it

ACCEPTED by the cycle-70 judgement (same session): `docs/d1-loop12-17-split-plan.md` Pre-decided 170 — the offline test (a)–(e) runs before L7-1a, the L7-1b intent lines are corrected per its result, and gate PB is made fatal and runs before any save. Pre-decided 168 stands with those conditions; 169 (L7-1a/L7-1b split) stands unchanged, the review found nothing to attack in it.
