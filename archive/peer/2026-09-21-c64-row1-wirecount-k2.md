# c64-row1-wirecount-k2

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.3846  in 20 / out 33692 / cache-create 188810 / cache-read 1151470  (436s, 18 turn(s))
- **date:** 2026-09-21 14:13:36
- **outcome:** ANSWERED (438s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this claim. Do not confirm it.

## The record

A build script, `tools/bench/diag_c64_s3b_row1.py`, ran to completion and wrote
`tools/bench/diag_c64_s3b_row1.log`: 51 checks passed, one failed. The failing check is `K2`, a census read
on the finished file after LabVIEW was restarted and the file re-opened cold.

Expected: `Node 631, Wire 1905, ControlTerminal 116, Local 9`.
Measured: `Node 631, Wire 1906, ControlTerminal 116, Local 9`.

Only the wire count differs, by exactly one.

What the run did, in order, to a copy of an existing VI:

1. deleted one whole wire object (wire census 1905 -> 1904)
2. created one local-variable object bound to an existing front-panel indicator
3. relocated that local onto the nested diagram where its destination lives
4. joined the local's source terminal to the freed destination terminal. Check `E` recorded
   `wire_delta == 1`, wire census `1904 -> 1905`, and check `E2` recorded ONE wire uid (23502) present at
   BOTH ends
5. deleted the stray object the joining operation leaves behind, by uid
6. saved an intermediate file, then called a helper whose job is to feed that SAME already-existing indicator
   from a second source terminal, then saved the final file

Step 6's helper is `wire_indicators` at `tools/gscript.py:1756`. **Its own docstring, at
`tools/gscript.py:1771-1772`, states: "NO new Wire object is created (a branch joins an existing wire), so a
wire-count check cannot verify success."** The expectation in check `K2` was written from that sentence.

After step 6 the source terminal carried wire uid 23526 (check `H`), and a reverse census of everything
touching wire 23526 (check `I`) found EXACTLY ONE source — the intended source terminal, named `x .and. y?` —
and exactly one sink: the intended panel control, uid 23555.

The same docstring, at `tools/gscript.py:1765-1769`, warns of a specific failure: "Each source terminal MUST
ALREADY BE WIRED: WI branches the indicator onto the wire attached to the source terminal. An UNWIRED source
makes it extend an unrelated wire instead -> 'This wire connects more than one data source' and the target
breaks."

The finished file opens cold at execution state 1 (check `K`), and a later ordered read of the new
destination wire reports it not broken (check `L`).

## THE CLAIM YOU MUST TRY TO DESTROY

"`K2` failed because the EXPECTATION was mis-written, not because anything is wrong with the artefact.
`wire_indicators` created one new wire object here rather than branching an existing one; the documented
'no new Wire object' sentence is what is wrong. The count 1906 = 1905 - 1 (deleted) + 1 (the join) + 1 (the
indicator feed) is the correct number, and the file is sound."

## Already ruled out (do not spend your answer on these)

- "The file is broken" as a blanket claim: it opens cold at execution state 1 after a full restart, and the
  four md5-pinned originals are byte-unchanged.
- "The extra wire is the deleted one coming back": the deleted wire's uid is 10799; the two wires involved
  after the edits are 23502 and 23526, both newly minted.
- "A reference leak or a stray object": references opened 23, closed 23, live 0; the one stray object the
  joining operation left was located, its full terminal table read, and it was deleted by uid.

## What I want back

1. The strongest reason the claim is WRONG — in particular, any reading in which a wire count of 1906 is
   evidence that the indicator was fed by EXTENDING AN UNRELATED WIRE (the documented failure) rather than by
   a legitimate new connection.
2. A DIFFERENT explanation of the same +1 that I have not considered.
3. What observation would falsify the claim.
4. The cheapest discriminating test that separates your explanation from mine — runnable, not an argument.

Be concrete about what "branch" means in LabVIEW's scripting object model: does joining a terminal that is
already wired add a Wire object or not, and can a single logical net be represented by more than one Wire
object? If the answer is that a net of one source and one sink should be exactly one Wire object, say what
the second one is.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, and the brief forbids editing anyway — so the review is the answer.

---

# The claim is wrong, and the docstring is not the thing to fix

## 1. Strongest reason it is WRONG

**"NO new Wire object is created" has already been measured TRUE on this exact source terminal, with this exact op, feeding this exact indicator.** `docs/cycle27-plan.md:1728-1730`, the S3a run:

> `wire_indicators` **wired**: target wire **0 → 10799**, whole-VI `Wire` delta **0** (a branch onto the existing net), `#10686` t0 `'x .and. y?'` **3/3 wired before and after**

Delta **0**. And this run's own baseline re-measures the object model independently: wire uid **10799 sits at three terminals at once** — source `#10686` t0 (`log:108`), sink `#10407` t0 (`log:99`), sink panel control 23555 (`log:115`). One Wire object, one source, two sinks — the branch, already in the bed this run started from. That matches the external model: [labviewwiki's Wire class](https://labviewwiki.org/wiki/Wire_class) gives Wire a single `Terminals[]` property ("References the terminals connected by this wire"), not a source/sink pair; NI: one data source, many readers ([Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-TT/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)). A net of 1 source + N sinks is **one** Wire object; it splits into more only across a structure boundary — which is why gate `E2` bothered to certify "no tunnel" (`log:200`).

**So what happened is not a documentation error.** Step [2] of this very run **deleted wire 10799** (`log:120-121`) — the wire the branch was supposed to join — and nothing re-wired `#10686` t0 afterwards (the only new wire, 23502, has the Local and `#10407` as its two ends, `log:199-200`). When `wire_indicators` ran at step [8], the source terminal was **bare**, so the precondition at `gscript.py:1765-1767` ("Each source terminal MUST ALREADY BE WIRED") was **false — falsified four minutes earlier by this run's own step 2**.

The expectation was written by **carrying a conditional's consequent across the run's own destruction of its antecedent**. Editing the docstring would delete a true sentence *and* the warning that explains the result.

**On your specific question — is 1906 evidence of the "extend an unrelated wire" failure?** No, and the census is not what rules it out. Extending an unrelated wire adds **no** Wire object (the existing one gains terminals), so a pure extend predicts delta **0**. What +1 alone cannot exclude is a new wire resolving onto a foreign net — two data sources, VI breaks. That is excluded by **ExecState 1** (`log:448`, cold `log:395`), not by the census and not by gate I.

Two gates are weaker than the run treats them:
- `t3_separator` scans only diagram #639's nodes plus panel rows (`diag_c64_s3b_row1.py:533-552`) — **a second source on any other diagram is invisible to it.** Gate I would have PASSED on a two-source net.
- The ordered `Is Broken?` ran on wire **23502** only (`log:421-422`). Wire **23526**, the one under dispute, was **never asked**.

One of my own candidates is dead and I'll say so: the +1 is **not** a save/reload artefact — `log:377` shows `Wire: 1906` in memory immediately after the call, before any save.

## 2. A different explanation of the same +1

The +1 is the signature of a **topology change**, not of a helper misbehaving: one net (1 source, 2 sinks) destroyed and rebuilt as **two nets with two different sources**. The new second source changes *when* a value is read.

- Before: Case `#10407`'s **selector** t0 ← `x .and. y?` directly, same wire as the indicator.
- After: selector ← wire 23502 ← **Local read of `'Automatic Error Handling'`** (`log:402,411`), while the indicator is written by `x .and. y?` over 23526 (`log:306`).

All three sit on **the same diagram #639** — And Nodes[25] (`log:304`), Case Nodes[24] (`log:400`), Local Nodes[73] (`log:409`) — and **no wire orders the local read against the indicator write.** The Local has no input dependency; the And node has two. Per NI, you have no control over which is serviced first, and a local read is generally among the *first* things executed regardless of position ([dataflow vs local variables](https://forums.ni.com/t5/LabVIEW/dataflow-vs-local-variables/td-p/1463660), [Race condition](https://labviewwiki.org/wiki/Race_condition)). So the selector plausibly reads the previous pass's value every pass, and the default on the first.

`#10407` is the autofocus case fed by `10686 'x .and. y?'` (`docs/camera-acquisition-facts.md:189`, schedule `:272,:320`) and it **drives the ASI focus axis** (`:206`). The loop-split transport is a decision already taken (`cycle27-plan.md:1584-1594`) — but that decision was about crossing a **loop boundary**, and here the boundary does not exist yet: writer and reader are on one diagram, so the local buys nothing and costs the ordering. **"The file is sound" is the half of the claim nothing in this run can support** — its own banner says STRUCTURAL, NEVER FUNCTIONAL (`log:4,:62`).

## 3. What would falsify the claim

- *"The doc is wrong" half*: read `#10686` t0's wire **between step [2] and step [8]**. `0` ⇒ precondition violated, docstring stands. A **non-zero** wire there would mean WI branched *and* still added a Wire object — that is the only observation that rescues the claim.
- *"The artefact is sound" half*: any evidence the selector's value or timing differs from the original — or simply confirmation that no dataflow path exists between the indicator write and the local read.

## 4. Cheapest discriminating test

**Test A (the discriminator).** Cold-open `claudeDev\D1_s3b_row1a_20260921_135932.vi` (md5 `c7094f98…`, `log:290-292`) — saved *after* delete+connect, *before* `wire_indicators` — and read `#10686`'s terminal table (diagram #639, Nodes[25]) plus the Wire census. Verbs already exist (`g.node_terms_uid` `gscript.py:925`, `g.count` `:1005`); no original touched; the file is already on disk because of the 2026-09-19 "every stage leaves a file" rule.

| reading | verdict |
|---|---|
| `t0 wire == 0`, `Wire == 1905` | source was bare → docstring stands, `1906` is correct for what was built — **my explanation** |
| `t0 wire != 0` | WI branched and still added a wire → docstring wrong — **your explanation** |

**Test B (close the hole).** Ordered `Is Broken?` on wire **23526**, and list `Wire.Terminals[]` for 23502 and 23526 to confirm no object appears in both.

## 5. Fix this, not the docstring

K2's expected census came from a helper's docstring instead of from the net topology being built. The run already diffs the **Node** census after *every* op (`log:459-463`) but keeps only a whole-run Wire expectation (`diag_c64_s3b_row1.py:150`, used `:1115-1120`). Carrying **Wire** through the existing `census_and_purge` would have surfaced this at step [8] as "+1, as designed" instead of at K2 as a failure — no new tool.

**Verdict: REFUTED as diagnosed, CONFIRMED as arithmetic.** 1906 is the right number; the reason given for it is wrong; and "the file is sound" is unsupported. What would change my mind is Test A returning a non-zero wire on `#10686` t0 in the step-7 artefact.

Sources: [labviewwiki Wire class](https://labviewwiki.org/wiki/Wire_class) · [NI: Using Wires](https://www.ni.com/docs/en-TT/bundle/labview/page/using-wires-to-link-block-diagram-objects.html) · [NI: dataflow vs local variables](https://forums.ni.com/t5/LabVIEW/dataflow-vs-local-variables/td-p/1463660) · [labviewwiki Race condition](https://labviewwiki.org/wiki/Race_condition) · [NI: Scripting wire into existing wire](https://forums.ni.com/t5/LabVIEW/Scripting-Wire-object-into-existing-wire/td-p/4014923) (checked — does not address branch-vs-new-object; not used as evidence)

## Sources

(extract from answer)

## What was done with it

Classified **ANSWERED, and the review WON on the measurement** — cycle 64 material #5, 2026-09-21 14:4x.

**THE REVIEW'S OWN DISCRIMINATING TEST (its section 4, Test A) WAS RUN, AND IT SETTLES THE DISPUTE AGAINST
ME.** `tools/bench/diag_c64_row1_testa.{py,log,json}` (read-only: `g.save` is neither imported nor called;
static gate `tools/bench/c64f_astcheck.log` **ASTCHECK OK 12/12**). Cold-opening the STEP-7 artefact
`claudeDev\D1_s3b_row1a_20260921_135932.vi` in a freshly restarted LabVIEW:

> `*** TEST A READING: #10686 t0 wire = 0 ; Wire census = 1905 ***`  (`diag_c64_row1_testa.log:38-39`)

That is the review's arm, exactly as it predicted. **My explanation is REFUTED by measurement, not by
argument**: `wire_indicators`' docstring sentence "NO new Wire object is created" is TRUE, and the +1 happened
because step [2] of the build deleted wire 10799 and thereby left the source terminal `#10686` t0 **bare**, so
the helper's documented precondition (`tools/gscript.py:1765-1767`) was false when it ran and it minted a new
wire instead of branching. `tools/gscript.py` was NOT edited; the docstring stands untouched.

**SO K2 IS A MIS-WRITTEN EXPECTATION, AND THE MISTAKE IS NAMED PROPERLY.** Not "the doc is wrong" but: the
expectation carried a conditional's consequent across the run's own destruction of its antecedent. 1906 =
1905 − 1 (deleted) + 1 (the join, wire 23502) + 1 (the indicator feed, wire 23526) is the correct count for
what was actually built.

**ACCEPTED AS A FINDING, NOT REPAIRED HERE (it is the judgement session's call).** The review's section 5
proposes carrying the **Wire** census through `census_and_purge` alongside the Node census, so a delta shows
up at its own step as "+1, as designed" instead of at the end as a failure. No new tool, no new verb. Recorded
for the judgement session; not built inside this dispatch, which was a deliverable build.

**PARTLY MEASURED, AND HONESTLY INCOMPLETE — Test B.** The review's second finding is real: the build's
`t3_separator` scans only diagram #639's nodes plus the panel rows, so a second data source on any other
diagram would have been invisible to gate `I`. Test B re-censused the nets across EVERY diagram of the
finished artefact and **ran out of time**: `BGRUN TIMEOUT killed after 1321s (limit 22.0 min)`. What it did
read, before the kill, is on record: wire **23502**'s net over **103 of 173 diagrams / 450 nodes** has
**exactly ONE source** — the Local `#23499 'Automatic Error Handling'`, `is_source True`, Diagram idx 46
(`#639`) Nodes[73] (`diag_c64_row1_testa.log:46,:49`). Wire **23526**'s whole-VI net was **never scanned**.
The per-node `node_terms_uid` cost (~1.3 s across 450 nodes) is what exhausted the budget. **This is reported
as INCOMPLETE and was NOT retried** (material failure budget); the remaining question — does wire 23526 have
exactly one source across the whole VI — is open, and `Is Broken?` on 23526 was likewise never asked.

**ESCALATED, NOT DECIDED HERE — and it is the important half.** The review's section 2 is not about wire
counts at all: it observes that the Case selector is now fed by a **Local read** of `'Automatic Error
Handling'` while the indicator is written by `x .and. y?` **on the same diagram #639**, with **no dataflow
edge ordering the read against the write**, so the selector may read the previous iteration's value; and that
`#10407` drives the ASI focus axis. If that is right it is a **rule-1a question** (the original's computation),
not a cosmetic one — and rule-1a calls are explicitly outside a material session's authority. It is the
dispatch's `OPEN:` item, stated with the evidence beside it. Nothing was changed on the strength of it, and
the artefacts stay exactly as saved. The run's own banner already says what its verification level is:
**STRUCTURAL, NEVER FUNCTIONAL (34(f))** — so "the file is sound" was never claimed by the run, and the
review is right that this dispatch cannot support it.
