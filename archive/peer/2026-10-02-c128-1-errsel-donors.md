# c128-1-errsel-donors

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0051  in 14 / out 5926 / cache-create 94623 / cache-read 647729  (68s, 16 turn(s))
- **date:** 2026-10-02 00:02:09
- **outcome:** ANSWERED (71s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** guard_peer blocked card 128-1 on card 127-5's failed prediction (diag_c127_5_errsel.log D1); JEV-LADDER new-problem p=0.682, hypothesis review owed
- **verdict:** unverified

## Question

ATTACK this claim about a failed LabVIEW diagnostic. Read-only; cite file:line.

FAILURE: tools/bench/diag_c127_5_errsel.log (script tools/bench/diag_c127_5_errsel.py, plan tools/bench/diag_c127_5_errsel_plan.json), gate D1 at log line 31:
  FAIL  D1 donors found: Unbundle None | Select None
Predicted (script docstring :8): both donors found. Seven NI example VIs were byte-copied into claudeDev and read with allterms.read_terms(<copy>, OP_ALLTERMS_V1) (script :26-28, :31-51); every copy reported NamedUnbundler [] and Select-signature [] (log :24-30). The per-candidate allterms row COUNT was not logged.

CLAIM (card 127-5's reading, result_127-5.json): none of those seven shipped examples contains an Unbundle By Name or a Select node, so there is no donor route; the next step is another donor source (other vi.lib files, a fact peer, or the GUI class).

Questions: (1) strongest reason this claim is wrong - e.g. allterms.read_terms returned ZERO rows for every copy (copy never opened / wrong path / op reads only top-level diagram, not nested frames/loops / owner_class string for Unbundle By Name is not 'NamedUnbundler' / select_sig in the plan does not match Select's real terminal names 's','t','f','s? t: f'), so 'no node' and 'empty read' are not separated; (2) an alternative explanation; (3) what would falsify it; (4) the cheapest discriminating test (preferably offline: read tools/allterms.py and the plan's select_sig / candidates list, compare with docs/NAMES.md or census_samples.json for the real class names).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

I've finished the read-only review. The claim does not hold: half of it comes from a bug in the matching code, and the other half is not settled by the evidence.

## 1. Strongest reason the claim is wrong: the Select search could never have matched
The plan looks for a Select node by this set of terminal names: `["f","s","s? t: f","t"]`, with a space after the colon (`tools/bench/diag_c127_5_errsel_plan.json:18`). The script requires an exact match of the sorted name list (`diag_c127_5_errsel.py:42`).

This project has already read a real Select node with the same reader, OpAllTerms. Its output terminal is **`"s? t:f"`, with no space** (`docs/wiki/subvi/Omar's Draw Flattened Pixmap.json:153`). The node's other terminals are `f`, `s` and `t` (owner 533, `:163, :173, :183`), and its owner_class is `"Function"`, not a Select class (`:157`). So `Select-signature []` on all seven copies is what this code returns whatever the files contain. "No Select in these examples" was never measured.

The same mistyped name is in `tools/bench/diag_c123_ring_p3_routes.py:27`. That means the earlier fact "Select: 0 hits in the bed", which this script's docstring cites (`diag_c127_5_errsel.py:4`) as the reason a donor was needed, is probably the same false negative. A Select may already be in the working VI.

## 2. Alternative explanation for the Unbundle half
The class string is right: the reader does label Unbundle By Name `"NamedUnbundler"` (`docs/wiki/subvi/choose bandpass v2 (prior).json:4499`, and `docs/NAMES.md:342` counts 12 of them). So `NamedUnbundler []` is either a true absence or an empty read, and the log cannot tell which:
- **Empty read:** the script never logged how many rows each copy returned (`diag_c127_5_errsel.py:39-43`). `read_terms` only raises when the op reports an error (`tools/allterms.py:80-82`); a run that returns zero rows passes silently. Not one candidate's row count is on record.
- **True absence is plausible too.** Current NI examples often wire the error cluster straight into the loop's stop terminal, so they contain no Unbundle By Name. No candidate was chosen because it was known to contain one (`plan.json:8-17`). The earlier successful donor search (`diag_c103_wait_donor.py:44-52`) found nodes by label and class, not by this terminal signature.
- Nested diagrams are not the cause. The reader returns `frame_diagram` for rows inside structures (`Omar's...json:118`), and it returned 5,811 rows on the bed (`allterms.py:7`).

## 3. What would falsify the claim
- Any candidate copy where a node owns exactly the terminals `{s, t, f, "s? t:f"}` would falsify the Select half. That is likely: "Comparison Functions.vi" and "Case Structure - Selector Data Types.vi" are plausible places for a Select. I have not checked these files.
- Any candidate with a `NamedUnbundler` row would falsify the Unbundle half.
- A candidate that returns **0 rows** in total would show the reader failed, not that the node is absent.

## 4. Cheapest test that separates the two
- **Offline, no LabVIEW, done here:** correct `select_sig` to `["f","s","s? t:f","t"]`, using the name measured at `Omar's...json:153`. Then search the bed's saved terminal tables (any `allterms_*.json` or `docs/wiki` dump of the D1 bed) for owners with that set, and for `owner_class == "NamedUnbundler"` (16 are expected on the bed, per `d1-loop12-17-split-plan.md:2818`). If they are there, the donor is already in the working VI and the NI-example search is not needed at all.
- **One LabVIEW run, only if the offline search finds nothing:** rerun the D1 candidate loop alone with the corrected name. For each candidate, log the total row count, a count of rows by `owner_class`, and every terminal name containing `"?"`. This puts the empty-read case and the true-absence case on record separately.

**Verdict:** the Select half of "no donor route" is refuted, because the matcher has a typo. The Unbundle half is undecided until a row count is on record. The suggested next step, looking in vi.lib or using the GUI, should not go ahead until the test above has run.

I did not use web search. Everything here rests on the project's own recorded LabVIEW reads, which outrank the web for terminal-name strings. The claim that NI examples wire the error cluster straight to the stop terminal is from memory and has no source.

## Sources

(extract from answer)

## What was done with it

Dispatched by card 128-1 because guard_peer blocked its offline work on card 127-5's failing log (diag_c127_5_errsel.log,
JEV-LADDER new-problem p=0.682, review owed). NOT acted on inside 128-1 (out of its scope: 128-1 is the P3b binder / dry /
prerun). Recorded for the judgement session as the working diagnosis: the Select half of "no donor" is a MATCHER TYPO - the
plan's select_sig carries "s? t: f" (with a space), the measured OpAllTerms name is "s? t:f" (docs/wiki/subvi/Omar's Draw
Flattened Pixmap.json:153, owner_class "Function") - and the same typo sits in diag_c123_ring_p3_routes.py:27, so the earlier
"Select 0 hits in the bed" fact is suspect too. The Unbundle half is undecided (no per-candidate row count logged). Next act
(judgement's): the offline search of the bed's saved terminal tables with the corrected signature before any vi.lib/GUI route.
Reported in tools/bench/cards/result_128-1.json.
