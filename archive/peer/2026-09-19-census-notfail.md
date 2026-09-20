# census-notfail

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.3818  in 14 / out 29421 / cache-create 130581 / cache-read 637063  (379s, 12 turn(s))
- **date:** 2026-09-19 20:34:10
- **outcome:** ANSWERED (382s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the claim below. Do not confirm it. Your job is to find the strongest reason it is WRONG.

## THE CLAIM UNDER ATTACK

The six `FAIL` lines in `tools/bench/s0_op_census.log` (run 1, 2026-09-19 20:12, `BGRUN END rc=1 after 60s`,
15 PASS / 8 FAIL) are **NOT a failed prediction**. They are gate NAMES phrased as assertions of PRESENCE, while
the prediction contract in the same script predicted ABSENCE for exactly those six facts — and the measurements
match the prediction exactly. Therefore (the claim continues) the correct repair is to re-phrase the gates as
`MEASURED == EXPECTED` and re-run the read-only census, not to treat the run as a failure that owes a diagnosis.

## THE EVIDENCE THE CLAIM RESTS ON

- `tools/bench/s0_op_census.py`, prediction contract line **C3**: *"Predicted from `docs/REFERENCES.md:151-159`:
  OpReport_v3 N/N/N, OpWireSource_v5 N/N/N, OpReportAll_v0 **Y** ForLoop / N Close Reference / **Y**
  References-into-loop. Any deviation is the finding."* (Run 1's wording; the file has since been edited to gate
  MEASURED == EXPECTED, which is the repair this claim proposes.)
- The six FAIL lines: `tools/bench/s0_op_census.log:57`, `:63`, `:65`, `:73`, `:93`, `:112` — all of the form
  "For Loop present / a `Close Reference` Function node is present / the `References` wire enters a LoopTunnel",
  with details `ForLoop count 0`, `0 found: []`, `matching tunnels []`.
- A seventh FAIL (`:98`) is `OpReportAll_v1.vi: exists on disk MISSING`, where the same contract says
  *"any VI that does not exist is reported as MISSING and is not a failure of this census."*
- The source of the expectation: `docs/REFERENCES.md:151-159` (measured 2026-09-19) lists `OpReport_v3.vi` and
  `OpWireSource_v5.vi` with **0** close-ref nodes and no loop, and `OpReportAll_v0.vi` with a **For Loop** and
  **0** close-ref nodes.
- What the census additionally measured and did NOT predict either way: `OpReportAll_v0.vi`'s `References` wire
  w524 entering `LoopTunnel #511` at IndexMode 1 with inner wire w421 (`:113-119`), and all three existing ops
  reading `ExecState` **1** COLD (`:55`, `:71`, `:104`).
- The census edited nothing: every md5 is identical before and after (`:122-132`), the route-B original included.

## ALREADY RULED OUT (do not spend your answer here)

1. "The census is broken / the ops really do have a loop." The same log prints the full node list per diagram
   (`:58-62`, `:74-92`, `:107-111`); `OpReportAll_v0` shows `For Loop #113` and body diagram `D[1]`, the other two
   show `diagrams: [(0, 3, '')]` only. The reader is the same `gscript.report`/`tunnels`/`node_terms_uid` fleet
   used everywhere else.
2. "rc=1 proves a failure." `tools/bgrun.py` prints `BGRUN INNER FAILURE: the command exited 0 but its output
   reported 17 failure(s)` — the process itself returned 0; rc=1 is bgrun's own scan of the word FAIL.
3. "A peer review was already archived for it." `archive/peer/2026-09-19-priorart-s0-gamma1.md` is claude in the
   `priorart` role and `guard_peer.py` explicitly refuses it as a discharge.

## WHAT I WANT FROM YOU

1. The strongest reason the claim is WRONG — including any reading under which these lines DO record a failed
   prediction that owes a diagnosis (for example: is "the prediction contract predicted absence" actually
   supported by the run-1 text, or is that a post-hoc reading of an ambiguous sentence?).
2. An ALTERNATIVE explanation of the six FAIL lines.
3. What would FALSIFY the claim — something readable from the files.
4. The CHEAPEST DISCRIMINATING TEST between the claim and your alternative.
5. Separately: a named hazard in the repair itself — re-running the corrected census APPENDS to the same log, so
   only the last run counts for `tools/hooks/guard_peer.py:111-116`. Say plainly whether that is record-keeping
   hygiene or evidence-hiding, and what would make it the latter.

Read-only: do not modify any file, do not open a `.vi`, do not take the LabVIEW lock.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The strongest reason the claim is WRONG

**The claim defends six gate names and never reads the sentence three lines above them — which is a prediction, was stated before the run, and is false.**

`tools/bench/s0_op_census.log:10-12` (= `s0_op_census.py:9-11`), the census's entire justification for existing:

> `s0_hygiene_probe.py` … "does NOT report ForLoop / Close Reference / tunnel IndexMode per op. Those three are what this census adds; **nothing here re-measures the probe**."

The probe, run 2 h 40 m earlier the same day (`s0_hygiene_probe_run2.log:1`, 17:32 vs 20:12):

- `:9` `OpReport_v3.vi: 5 nodes, **0 close-ref-like**` · `:15` same for OpWireSource_v5 · `:41` `KernelBuilder_v1.vi: 18 nodes, **1 close-ref-like**`
- `:36` `#113  ForLoop  'For Loop'` — the For Loop, reported, per op
- `:65-68` — **gates already carrying the exact polarity the claim proposes to "repair" into the new file**: `PASS P1 OpReport_v3.vi has NO Close Reference []` ×3, and `PASS P2 KernelBuilder_v1.vi HAS a Close Reference donor node [('Function','Close Reference',157)]`

So two of the three "new" facts were already measured, already gated with correct polarity, and already carried a **positive control** that the census dropped. Only the tunnel IndexMode table and ExecState-COLD were new — and run 1 already produced both (`log:114-118`, `:55/:71/:104`).

That reframes everything. The finding is not "six names were inverted." It is: a census was written to re-measure what the fleet had measured hours earlier, asserting in its own header that it was not doing so — and the claim's repair is to **spend a LabVIEW kill/restart plus a second run** re-deriving `docs/REFERENCES.md:151-159`, which is itself derived from that probe (`REFERENCES.md:151-152` cites `s0_hygiene_probe.log`). `EXPECT` is a re-read of the same instrument's prior output: it cannot fail and it cannot confirm. The corrected re-run will print 23/23 PASS **by construction** and tell the project nothing.

Two further defects in the claim's own bookkeeping:

- **It cannot count its evidence.** The log says `15 PASS / 8 FAIL` (`:140`). The claim enumerates six plus the MISSING one = seven. It omits `:95` — `FAIL C3c OpWireSource_v5.vi … matching tunnels []`. A claim that the record holds no failure, written by the session that wrote the record, dropping one record while listing them.
- **The contract does not exonerate `:98` the way the claim says.** C1 (`log:24-25`) names three VIs; `OpReportAll_v1` is in `TARGETS` (`s0_op_census.py:55`) but not in the contract, so nothing was predicted about it either way — and the machine-readable record disagrees with the prose: `s0_op_census.json:267-270` → `{"name": "C1 OpReportAll_v1.vi: exists on disk", "pass": false}`.

## 2. Alternative explanation of the same FAIL lines

**Not "absence phrased as presence" — the gate idiom was inherited wholesale from a BUILD recipe and never re-derived for a measurement.** `s0_op_census.py:16-17`: `fresh()/mem()/com_preflight()` are "cut from `tools/recipes/build_s0_closeref_v3.py:201-249` (the same bytes)". In a builder, `X present` is the *correct* gate — the builder just created X. Copied into a census, every gate asserts presence regardless of expectation.

This explains what polarity alone does not:

- the positive control vanished: `KernelBuilder_v1.vi` sits in `GATED` (`:56`), is md5-read twice, is in the same instance — and is excluded from `TARGETS` (`:55`);
- a **proven** detector was swapped for an **unproven** one on a false premise. `s0_op_census.py:204` says the triple is used "not by a label (primitives are unlabeled)". `docs/NAMES.md:249-252` records the opposite — a primitive's `Node.Label` reads as its type name — and the probe printed `'Close Reference'`, `'Index Array'`, `'Open VI Reference'` as labels (`s0_hygiene_probe_run2.log:10-14`, `:58`).

**What I checked and could not sustain:** I suspected `g.report_all(path,"Function")` was under-reporting and blinding C3b. It is not. `function_uids` = `[43]` / `[43,1044,1221]` / `[43]` (`s0_op_census.json:21-23`, `:56-60`, `:117-119`) matches the probe's class column exactly — `Index Array` is class `IndexArray`, not `Function` ([LabVIEW Wiki](https://labviewwiki.org/wiki/IndexArray_class): IndexArray inherits from GrowableFunction; see also the [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)). The Function filter is sound. What remains unproven is only `names == CR_TERMS` — **never once executed against a node that should match.**

## 3. What would FALSIFY the claim (readable from the files)

- Any run-1 FAIL whose measurement does not match the letter in the run-1 contract (`log:31-32`). `:98` is already that case — an untested target, not a predicted absence.
- Any evidence that C3b's detector cannot fire. Then three FAILs are instrument failures, not measurements, and re-gating them to `EXPECT=False` certifies a null from an instrument never shown able to produce a hit.
- **Falsifies my alternative:** run C3b against `KernelBuilder_v1.vi` and get `1 found: [{uid:157…}]`. Then the detector is proven and only polarity + duplication remain.

## 4. Cheapest discriminating test

Two lines, **no extra run** — it rides on the re-run the claim already wants: add `"KernelBuilder_v1.vi"` to `TARGETS` (`:55`) and `"KernelBuilder_v1.vi": (False, True, False)` to `EXPECT` (`:63-65`). Expected from `s0_hygiene_probe_run2.log:41,58,68` and `REFERENCES.md:159`: ForLoop **0** (its loop references are SubVIs `Create/Exit For Loop.vi`, `:49-50`, not a structure), Close Reference **1** (#157), no Traverse ⇒ no tunnel. If C3b prints `0 found: []` there, the triple detector is blind and three FAILs are instrument failures.

Cheaper still, and it should come first: **do not re-run at all.** Every fact this census can produce is already in run 1's log and JSON. Note also that `MAX_AGE_S = 6*3600` (`guard_peer.py:75`) — the gate self-expires at ~02:12 regardless. If the re-run's motive is the gate, that motive is void.

## 5. The hazard in the repair — plainly

**As designed, last-run-wins is hygiene; here it would be evidence-hiding.** `guard_peer.py:114-116` deliberately reads only after the final `BGRUN START`, and `FAILURE_RE` (`:73`) matches `^\s*FAIL\b` — so run 1's `   FAIL …` lines arm it now, and a 23-PASS re-run disarms it. Three things make that the latter here:

1. The hook's premise is that the re-run is the **same measurement** passing (`:111-113`). This re-run changes the **predicates** so the same measurements print PASS. The hook reads text; it cannot separate "we fixed it" from "we moved the pass line."
2. **The log appends, but the JSON does not.** `OUT` is a fixed path opened `"w"` (`s0_op_census.py:53`, `:311`). A re-run destroys `s0_op_census.json` — including the `gates` array, the only machine-readable record of run 1's eight false gates (`:222-315`). This directory is not a git repository; there is no recovery.
3. The replacement evidence carries the verdict on the thing it replaces: `s0_op_census.py:58-62` characterises run 1 as a phrasing artefact, and `print(__doc__)` (`:263`) puts that characterisation at the top of the new log. The party under review authors the record that supersedes the record under review.

Make it hygiene by: writing `s0_op_census_run2.json` and leaving run 1's JSON intact; citing run 1's block in the new header rather than characterising it; and including the positive control so the re-run measures something run 1 could not.

**Separately, a false line the claim leans on:** bgrun's `17 failure(s)` (`log:149`) is not a failure count — 8 inline FAILs + 8 echoed in the summary (`:141-148`) + the `=== 15 PASS / 8 FAIL ===` header = 17. Any script printing a summary block inflates it. "Already ruled out #2" cites that line while the line is itself miscounting.

**Where the evidence does not settle the question:** I cannot tell from these files whether the triple-matcher works, because nothing in run 1 or the probe ever ran *this* matcher against a matching node — the probe found #157 by a different route. That is exactly why the KernelBuilder control is the test, not an extra.

**Does the claim survive?** Its narrow factual core does — run 1's contract text at `log:31-32` really does predict N/N/N, N/N/N, Y/N/Y, and six of the eight FAILs really are predicted absences. What does not survive is the conclusion drawn from it: "therefore no diagnosis is owed, re-run it." A diagnosis is owed for the false `WHAT ALREADY EXISTS` claim, and the re-run is the one action that adds cost while removing the record. What would change my mind: the probe's P1/P2 gates turning out to post-date the census, or `s0_hygiene_probe_run2.log:65-68` proving to be a different measurement than C3b.

Sources: [IndexArray class — LabVIEW Wiki](https://labviewwiki.org/wiki/IndexArray_class) · [VI Server Class Hierarchy — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

## Sources

(extract from answer)

## What was done with it

Annotated 2026-09-19 21:0x by the cycle-45 material session (act 2), which dispatched it because
`tools/hooks/guard_peer.py` armed on `tools/bench/s0_op_census.log`. **The review is ACCEPTED on every point that
is a fact about this session's own work; nothing design-level was decided here.**

1. **ACCEPTED AND FIXED — the false `WHAT ALREADY EXISTS` claim (section 1).** Run 1's header said the probe
   "does NOT report ForLoop / Close Reference / tunnel IndexMode per op … nothing here re-measures the probe".
   `tools/bench/s0_hygiene_probe_run2.log:9`, `:15`, `:36`, `:41`, `:65-68` show that was false, and that the
   probe already gated those facts with the CORRECT polarity. The header in `tools/bench/s0_op_census.py` now
   carries that correction verbatim, marked as a correction, with the probe's line numbers. **Only the per-tunnel
   IndexMode table and the COLD ExecState readings were new** — and run 1 produced both.
2. **ACCEPTED AND APPLIED — the cheapest discriminating test (section 4).** `KernelBuilder_v1.vi` is now in
   `TARGETS` with `EXPECT = (False, True, False)`, so the `Close Reference` detector is run against a node that
   MUST match (#157). Without it the three nulls certified an instrument never shown able to fire.
3. **ACCEPTED AND APPLIED — the evidence-hiding hazard (section 5).** Run 2 writes
   `tools/bench/s0_op_census_run2.json`; **run 1's `s0_op_census.json` is not touched** (it was opened `"w"` on a
   fixed path, which would have destroyed run 1's machine-readable gate array). The log appends, so run 1's whole
   block stays above run 2's `BGRUN START`.
4. **ACCEPTED AND APPLIED — the label claim (section 2).** Run 1's comment "primitives are unlabeled" contradicted
   `docs/NAMES.md:249-252`. Both detectors (terminal triple AND node label) now run, and a new gate C3d fails if
   they disagree.
5. **ACCEPTED — the miscounts.** `:98` (`OpReportAll_v1.vi` MISSING) was an UNPREDICTED target, not a predicted
   absence; it is now recorded rather than gated, as is the donor's ExecState. The claim's own enumeration missed
   `:95`, and bgrun's "17 failure(s)" double-counts the summary block.
6. **NOT ACTED ON, left to judgement:** the review's "do not re-run at all" (section 4, second paragraph) and its
   observation that `guard_peer.MAX_AGE_S` self-expires at ~02:12. Run 2 went ahead **only because points 2 and 4
   make it measure something run 1 could not** — the detector's positive control — not to clear the gate.

**Nothing in this exchange touched S0's design, the γ1 question, or the prior-art review of
`tools/recipes/build_s0_gamma1.py`, which stays UNDISPOSED for judgement.**

(Claude fills in)
