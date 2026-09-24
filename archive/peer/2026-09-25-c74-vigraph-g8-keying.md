# c74-vigraph-g8-keying

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1754  in 18 / out 12031 / cache-create 96580 / cache-read 810294  (136s, 17 turn(s))
- **date:** 2026-09-25 01:32:05
- **outcome:** ANSWERED (140s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed prediction in tools/bench/vigraph_check.log (script tools/bench/diag_vigraph_check.py).

Context (card 74-2 result, tools/bench/cards/result_74-2.json): tools/vigraph.py was patched so a Diagram-owned `Terminal`
SOURCE row (e.g. loop `i` #644, owner Diagram #639) becomes its own graph node (term_uid, class DiagramTerminal) instead of
being keyed on its owner node 639 (a SCHEDULING owner that effective_sources walked through to {}). See tools/vigraph.py:237-241,298,310.
After the patch, gate G8 (vigraph_check.log:707) failed: diff(S1, Row-D bed) minus flat-sequence edges was predicted 15/42/9
(removed/added/changed_sinks, the step-4 baseline) and measured 15/39/9 - three fewer ADDED edges. All other gates pass:
G1a diff(S1,S1) empty, G4 cdiff(S1,bed) 0 rows, G12a/b/c (every wired diagram-owned Terminal source is now an edge source;
#376 'frame index' effective source == #644; a synthetic drop gives exactly 1 cdiff row).

CLAIM (a): the old keying put diagram-owned source and sink Terminal rows into one ordinal group per owner node, so 3 of the
42 "added" edges were ordinal-shift artefacts of that grouping; the new keying removes them, 15/39/9 is the correct count,
and DIFF_BEFORE in diag_vigraph_check.py should be re-baselined to 15/39/9.
COMPETING (b): three real added edges now collide with S1 keys under the new keying (the patch hides real differences).

Say which is more likely from the code (tools/vigraph.py diff / key functions, tools/bench/diag_vigraph_check.py G8), what
would falsify (a), and the cheapest discriminating test (e.g. list the 3 edges present in the old-key added set and absent
in the new one, by term uid - tools/bench/cdiff_blindspot_74.py was written for this and never ran).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim is not supported, and its most likely mechanism is wrong.** The drop from 42 to 39 added edges is better explained by a different change: `dedupe_rows` (added 2026-09-24). G8 has not run since that change landed. The 74-2 keying patch is not the likely cause, and neither is (b), a collision. The re-baseline to 15/39/9 is probably the right number, but not for reason (a).

### 1. Strongest reason (a) is wrong: two changes happened between the last pass and the failing run
- The last G8 PASS was 2026-09-23 17:07 (`tools/bench/vigraph_check.log:598`). The next G8 run was the failing one, 2026-09-25 01:17 (`vigraph_check.log:606-707`). No G8 run sits in between.
- The only diff counts saved in between agree with the old baseline and predate dedupe. `graph_diff_s1_bed_20260924.json:506-510` reads 16/43/9, and `graph_bed_20260924.json` has no `"dedupe"` key in its `method`, which it has carried since dedupe was added (`vigraph.py:348`).
- `dedupe_rows` (`tools/vigraph.py:260-278`, called at `:292`) went in on 2026-09-24 22:23 (`tools/bench/dedupe_check_s2b.log:21-41`). So the failing run was the first G8 run with dedupe **and** the first with the DIAG_TERM patch. The claim credits all of the change to the patch without separating the two.

### 2. Alternative explanation, with numbers already on disk
`dedupe_check_s2b.log:24,26` measured this before and after dedupe:
- **S1:** 23 duplicated rows dropped; edges went from 7541 to 7515, 26 fewer.
- **Rowd bed:** 29 duplicated rows dropped; edges went from 7611 to 7582, 29 fewer.
- Every dropped duplicate had been making an extra "phantom" key with ordinal above 0.

The bed's duplicate list contains uids that S1's does not: 23073, 23080, 23225, 23246, 23444, 23456 (`:7` against `:5`). Those are almost certainly the bed's new diagram terminals, and their phantom edges exist only in the bed. Under the old code, `diff` (`vigraph.py:669-706`) therefore counted them as **added**. Removing them lowers "added" and leaves "removed" alone. That matches the observation: 15 removed and 9 changed sinks unchanged, 42 added down to 39. The bed lost 3 more edges than S1 (29 − 26 = 3), which is the size of the shortfall.

Caveat: 29 − 26 counts every edge kind, `thru` included, and `diff` ignores `thru`. So the matching 3 is strong evidence, not proof.

Why (a)'s mechanism fits worse:
- A pure ordinal shift within an owner's group happens in both graphs. When it misaligns keys it normally creates removed/added *pairs*, so removed should have moved too, and it stayed at 15.
- The patch only moves source rows owned by a diagram. Its fixed per-row key (`term_uid`, then `|0`) cannot merge two distinct source rows, so it cannot remove an added edge unless an old-key ordinal misalignment was pairing it with a removed one. Nothing in the evidence shows such a pair.

Why (b) is weak: under the new key, the source is identified by `term_uid`. A bed edge can match an S1 edge only if the terminal uid **and** the sink key are identical, which makes it the same physical edge. Hiding a real difference would need LabVIEW to reuse a uid for a different object across the S1→bed copy. That is possible but nothing points to it. Of the two keyings, the old one (diagram / name / ordinal) is the one that can collide.

Note: "bed gains 3 DiagramTerminal nodes" (`vigraph_check.log:677`) is also a 3. It is a node count, not an edge-set delta. It is a coincidence to rule out, not evidence for (a).

### 3. What would falsify (a)
Take `vigraph.py` at git HEAD, which should already contain dedupe but not DIAG_TERM, and run it on the same S1/rowD inputs.
- If HEAD already gives non-fs 15/39/9, the patch contributed 0 to the shift and (a) is false.
- (a) survives only if HEAD gives 15/42/9 and the working copy gives 15/39/9, and the 3 edges then turn out to be source-side edges owned by a diagram.
- (b) is supported only if the new-key "added" set is missing an edge whose (source uid, sink uid) pair is **not** in S1's uid-space edge set.

### 4. Cheapest test to tell them apart
- **Step 0, no run needed:** confirm `dedupe_rows` is in HEAD's `vigraph.py`. If it is not, OLD vs NEW mixes both changes and needs a third arm with dedupe but no DIAG_TERM.
- **Blocker:** `tools/bench/cdiff_blindspot_74.py` cannot run as written. Line 103 starts with `: no terminal table on disk ...")`, a broken line that is a SyntaxError. It needs fixing before section D, which computes DIFF OLD/NEW counts and DIFF-DELTA by terminal uid, is worth dispatching.
- **Better still, run the smallest version of that test:** build S1 and the rowD bed with `diag_vigraph_check.load()`'s inputs under three variants:
  1. HEAD minus dedupe (the 09-23 state)
  2. HEAD (dedupe only)
  3. the working copy (dedupe + DIAG_TERM)

  Print `diff(...)["counts"]` minus fs edges for each, then list the added-set delta between each adjacent pair as (source uid, source owner class, name) → sink. This is pure Python and never touches LabVIEW.
- **Prediction under my alternative:** variant 1 gives 42, variant 2 gives 39, variant 3 gives 39. The 3 edges between variants 1 and 2 have phantom keys (ordinal above 0) on bed-only duplicated uids from the 230xx range.

The re-baseline is legitimate once that test gives the number its real cause. The gate comment should name dedupe, the patch, or both, with the uid list, not the ordinal-group story. If variant 2 still gives 42, I'm wrong and (a) becomes the leading explanation again.

No outside source was needed; every claim above is about this project's own code and logs and is cited by file and line.

## Sources

(extract from answer)

## What was done with it

ACCEPTED (cycle 74 judgement). The review's mechanism (`dedupe_rows`, not the DIAG_TERM keying) was MEASURED by card
74-3: non-fs diff(S1,bed) VA (HEAD, dedupe off) 15/42/9, VB (HEAD) 15/39/9, VC (working) 15/39/9, uid-space sets
identical across all three (`tools/bench/vigraph_g8_edges_74.log:95-98,162-165`). Decision: G8's DIFF_BEFORE is
re-baselined to 15/39/9 with the attribution "dedupe_rows (2026-09-24) collapsed 3 double-counted sink rows"; the
DIAG_TERM patch in `tools/vigraph.py` (md5 35c68499…) is KEPT — it closes the Pre-decided 176(c) blind spot
(cdiff(S1,S4) = [w4517, w3268], `tools/bench/cdiff_blindspot_74.log`).
