# c134-5-el-classrange

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0142  in 16 / out 6864 / cache-create 91166 / cache-read 737648  (82s, 15 turn(s))
- **date:** 2026-10-02 11:57:58
- **outcome:** ANSWERED (85s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (card 134-5, failing log tools/bench/diag_c134_5_el.log, script tools/bench/diag_c134_5_el.py).

CLAIM: gate E2 of diag_c134_5_el.py ("every class within [lo, hi] and none outside the range file") failed because of a key-normalisation bug in OUR judging script, not because the Error List of the scratch-b final file differs from the predicted class range. The script counted items with errorlist_check.class_counts(items) (plain norm(), errorlist_check.py:471-478), while the range file tools/bench/errorlist_expect_p3b2ab.json keys its classes with OCR-alias-folded keys (e.g. 'youhayeconnected...', 'subyitracknbeads...oyerkernely3yireguired...'), i.e. errorlist_check.norm_ocr. Folding the read's keys the same way, by hand from the FACT line of diag_c134_5_el.log: 'thiswireisnotconnectedtoanvthing' 2 + '...anything' 18 = 20 (range 20..20); 'subvl...' 1 -> 'subyi...' (1..1); the three 'youhave...' classes 1 each -> 'youhaye...' (1..1 each); wirewirehaslooseends 20 (18..21); buildarray 3, looptunnel 3, datasinks 1 unchanged. Total 51 in 49..52 (E1 PASS). So with ocr=True every class is inside its range.

Evidence: the read itself is complete and clean: tools/bench/errorlist_c134_5_scratch_b.log:162-163 (51 items / window N 51, every item double-clicked, 11/0 read gates); its verdict file tools/bench/errorlist_scratch_c134_5_ring_p3b2b_20261002_112928_20261002_113807.json. The 'missing 2' there is versus P3b-1's 53-item expected list, which the recipe wrote as a placeholder (stage_d1_ring_p3b2b.py:83-92); the step's range is 49..52 (errorlist_expect_p3b2ab.json total_lo/hi). The scratch run itself passed 20/0 (stage_d1_ring_p3b2b_scratch_c134_5.log:360).

Already ruled out: the read missed items (N 51 == items 51); a new error class (every read class maps onto a range class after folding).
Fix proposed: diag_c134_5_el.py counts with class_counts(items, ocr=True) and folds the range keys with norm_ocr (already edited, not yet run).

Questions: Is norm_ocr really the normalisation the range file was built with (check tools/bench/plan_ring_p3b_split_p3b2.py / errorlist_expect_p3b2.py and errorlist_check.norm_ocr)? Could folding hide a real class difference (two distinct classes collapsing into one)? What is the cheapest test that separates "script bug" from "real Error List difference"?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim mostly holds. E2 failed because the two sides were spelled differently, not because of a count. But "the Error List does not differ from the prediction" is a stronger statement than this gate can support.**

**Checked and true**
- The range file uses the OCR-folded keys. The keys in `errorlist_expect_p3b2ab.json` come from `E1["per_class_read"]` (`plan_ring_p3b_split_p3b2.py:294`). That table was written as `class_counts(items, ocr=True)` (`stage_d1_ring_p3b1_el.py:122,139`). So both the range file and the P3b-1 expected file use `norm_ocr` keys (`errorlist_expected_D1_ring_p3b1_20261002_060910.json:124-133`), and the first run compared plain `norm()` counts against them (`diag_c134_5_el.log:6` against `:8`).
- The arithmetic holds. With `OCR_ALIASES = (("vl","vi"),("v","y"))` (`errorlist_check.py:322`), the 10 classes in the read collapse to exactly the 9 range keys. The only merge is `anvthing`→`anything`, giving 18+2=20 (range 20..20). Every other class lands inside its range, and the total of 51 is in 49..52.
- Folding hides nothing in this read. The two `anvthing` items carry the same detail text as the real class, "This is a completely unconnected wire." (scratch verdict json lines 658-660 and 1080-1082). `Subvl` shows up in the detail text too, which marks it as an OCR misreading of `SubVI`.

**1. Strongest reason the claim is wrong:** passing E2 shows the class counts match, not that the Error List matches. The loose-ends range is 18..21, four wide. If one loose end the plan predicted disappeared and an unplanned one appeared on another wire, the gate would still pass, because the Error List items carry no uid (`errorlist_expect_p3b2.py:8-9`). The verdict file can't settle it either: it records `"missing": [null, null]` (scratch json :5467-5470), so it doesn't say *which* two entries from P3b-1's list of 53 are gone. "Loose ends 22→20, so the two missing are the two debited" is an inference, not a reading.

**2. Alternative explanation of the same evidence:** two of the three two-sided lost wires each carried a dangling loose end, and the plan intended that. The alternative is that a different pair of loose ends changed, swapping one for another and netting −2. The first run's FAIL is a script bug either way, so the FAIL itself doesn't separate these two. Only an item-level comparison could, and the reader doesn't record one.

**3. What would falsify the claim:** a read class that still has no range key after folding, or any folded class falling outside [lo, hi]. Neither happens here.

**Problems in the proposed fix (`diag_c134_5_el.py:36-38`):**
- The `fold` lambda builds a `dict()` from the range keys. If two range keys ever fold to the same key, the later bound silently **overwrites** the earlier one instead of adding to it. Today the fold changes nothing, because the keys are already folded, so the bug is dormant.
- The docstring at `:4` still says "the same norm() keys the range file uses". The comment at `:34` contradicts it.

**4. Cheapest test that separates "script bug" from "real Error List difference":** run the edited `diag_c134_5_el.py` as it stands. It is offline and takes about 1 second. Then, in the same offline step, list the P3b-1 expected entries that no item in the new read matches, using `_hit` with its OCR fallback, and print their labels and cite strings.
- If E2 passes and both unmatched entries are re-pinned loose-ends entries (`stage_d1_ring_p3b1_el.py:133-135`), the claim stands at class level.
- If E2 passes but an unmatched entry belongs to another class, there is a real difference that the class gate hides.

What would change my mind: one of those two unmatched entries turning out not to be a loose-ends entry.

## Sources

(extract from answer)

## What was done with it

Card 134-5 (material, 2026-10-02 12:0x). Class: our-script-bug, confirmed by the review at class level (range keys are
`class_counts(items, ocr=True)` keys, `plan_ring_p3b_split_p3b2.py:294`, `stage_d1_ring_p3b1_el.py:122,139`).
- Accepted: `tools/bench/diag_c134_5_el.py` now counts with `class_counts(items, ocr=True)`; the review's two nits fixed in
  the same edit (range-key fold SUMS on collision instead of overwriting; docstring says norm_ocr). Re-run once as the
  card's own offline checker (`tools/bench/diag_c134_5_el2.log`) — not a LabVIEW rerun.
- Accepted as a limit, NOT tested in this card (card chat-P2: no diagnosis inside the card): a class-level pass does not
  prove item-level identity — the verdict file records `missing: [null, null]`, so which two of P3b-1's 53 entries vanished is
  not read. The review's item-level test (list unmatched P3b-1 expected entries via `_hit` with OCR fallback) is put to the
  judgement session as an OPEN question in `tools/bench/cards/result_134-5.json`.
