---
name: prior-art-review-is-the-fourth-peer
description: "The user's 2026-09-15 addition to the review structure — a reviewer whose only job is \"has this already been analysed, built, measured or refuted in our own files?\", because most remaining errors are re-deriving or re-building what the project already had"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-16T09:50:36.083Z
type: decision
status: in-force
date: 2026-09-16
source: memory/prior_art_review_is_the_fourth_peer.md
---

# The fourth review: "have we already done this?"

On 2026-09-15, after watching a day of failures, the user named the pattern:

> *"이전 에러 요소중 또한 상당한 부분이 이미 분석한 부분을 놓치거나 혹은 동일한 코드 만들거나 같은 실수가
> 반복되는 것 같음… 기존 분석한 도큐먼트 및 코드를 참조하여 현재의 방향을 피어리뷰 하는 세션이 필요하지
> 않은지"*

They were right, and the evidence was all from that single day:

- Step 0a failed **three times** deriving a Traverse index by hand, while `fidx()`, `new_since()` and
  `loop_diagram()` all already existed — one of them with a docstring that says *"Use this, NOT position
  matching, to identify what a mutating Op just created."*
- I named "can we move a node between diagrams?" as the project's central risk while
  `docs/toolkit-capabilities.md` already said, in a heading, *"the build route is clear, and 'move a node' was
  never needed"*.
- I quoted `camera-acquisition-facts.md` line 183 to justify an ordering while **line 139 of the same file**
  answered the opposite question directly.
- I nearly rebuilt `VI.Get Errors`, which the same file records as having FAILED twice.
- I stated what `GLOSSARY.md` said about `Limit of Program` without opening it; it said something else.

None of these are reasoning failures. They are **failures to look**, and no existing review catches them: the
hypothesis review attacks a diagnosis, the cycle retrospective attacks how a cycle was run, and the outcome review
attacks whether the work reaches the goal. Nobody asks the cheapest question of all — *has this already been done?*

## The agreed design (user, 2026-09-15, decided point by point in discussion)

| choice | decision |
|---|---|
| scope | **ONE unified review** covering both "is this direction already settled or refuted?" and "is this artifact already built?" — same reviewer, same evidence, one question set |
| when it fires | **cycle start · direction change · any new op or tool being created.** The third matters: `OpOwnerChain_v0` was invented mid-cycle and a cycle-start-only trigger would have missed it |
| reviewer | the **claude peer**, because the job requires reading `archive/` as well as the active docs — and that is an explicit **exception to rule 4** ("do not read archive/ in normal work"), which must be stated in the brief or the cell will avoid the archive on its own |
| dispatch path | **`tools/peer.ps1 -Agent claude -Model opus`**, NOT a separate subagent definition. Being archived and gated is what makes a review count; clean effort control is not worth losing that |
| model | **opus** for this role (the rule/consistency audit stays on sonnet). One missed prior-art hit costs a whole build cycle — the first run found four defects, one of them a repeat of a recorded failure |
| session | **separate from the rule/consistency audit.** The two read almost disjoint file sets: the audit reads CLAUDE.md and the current docs, prior-art reads logs, the archive and the code |
| verdict power | **it actually stops the work.** A warning is not enough — an outcome review's "do not build that reader" was overridden hours later by my own judgement |
| the override | **only by citation — in one of two forms.** `REFUTED:` (the review is wrong): open the cited file and show in writing that it does not cover this case, not "I think otherwise". `FIXED: <slug> - <path>:<line> - <what changed>` (**added 2026-09-16**; the review is right and the work already changed): releases only if the path exists, was changed after the review, and the line sits under "What was done with it". Both are archived so the next reviewer can check them. A promise is not a fix |
| budget | **no cap** — a cap would have cut the most valuable review of the day. Instead the dispatch count and wall clock per cycle are **measured in the audit**, so the retrospective can see if reviewing becomes the work (2026-09-15: 12 dispatches, ~1 h) |
| cost tracking | **the user's condition for accepting the archive permission**: *"아카이브 열람 가능 때문에 생기는 토큰 소모가 얼마나 되는지 걱정… 토큰 사용량 추적해서 나중에 다시 리비전 필요할듯."* Letting a reviewer read `archive/` (345 files) is the expensive half of this design, so **record per-review token usage and revisit the design on that data** rather than on impressions. The dispatch itself is what must carry the number — `claude -p --output-format json` reports usage, so the claude peer's archive entry records it |

What bounds the worst case, and is worth keeping if this is ever re-tuned: the reviewer is handed a machine-built
**index** (document names, recipe names, gscript function names, archived peer slugs — the slugs are descriptive
sentences), so it opens only what looks relevant instead of reading the archive end to end. If the measured cost is
still too high, tighten that index before removing the archive permission — the permission is what makes the review
catch superseded decisions at all.

## MEASURED AND SETTLED, 2026-09-15/16: **no index.** Do not build one again.

An index was built for this reviewer — first one flat file, then sharded by subject and classified by the kind of
statement — and then benchmarked against a test set of eight real prior-art items, split by whether the index
carried the answer. Two arms, two repeats, opus/high. The result inverted the design:

| arm | group A (answer IS in the index) | group B (answer only in old, unannotated files) | cost |
|---|---|---|---|
| **no index** | 3.0 / 4 | **3.5 / 4** | **$2.94** |
| sharded index | **4.0 / 4** | **1.0 / 4** | $3.60 |

**The index helps on what it contains and cripples everything else.** Both indexed runs scored exactly 1/4 on the
old material; both control runs scored 3/4 and 4/4. Handed an index, the cell treats it as the evidence base and
stops searching `archive/`; handed nothing, it searches and finds the half-forgotten exchanges — which are the
whole reason this review exists. Total recall: **6.5/8 without, 5.0/8 with**, and 22 % cheaper without.

The user's decision: **run with no index, and delete the one that was built.** `docs/index/` and
`tools/build_prior_art_index.py` are gone; the numbers survive in `tools/bench/priorart_scores.md` and the two test
sets beside it. A future session that reaches for "let's give the reviewer an index" should read that file first —
this was measured, not argued.

Two things that died with it: the plan to reformat 169 documents so they would feed the index (feeding the index
would have deepened the blind spot), and the assumption that annotation presence is what matters — of the 54 peer
exchanges older than 2026-09-08, 25 were "annotated" with single words like `adopted`, which occupy an index line
and say nothing.

## What the fourth review is

A dispatcher that, before a build or a change of direction is committed, hands a peer **the plan plus a
machine-gathered inventory of what the project already owns** (the `docs/` list, `archive/benchmarks/INDEX.md`
rows, every public function in `gscript.py`, the recipe filenames, the archived peer slugs) and asks only:

1. Has this been **built** already, under another name?
2. Has this been **measured or answered** already, in a doc or a log?
3. Has this been **tried and failed** already — and is the failure recorded?
4. Does an existing **helper** already do it, so the new code is redundant?
5. Which of my cited facts are **contradicted elsewhere** in our own files?

It ends in machine-readable verdicts (`already-built`, `already-measured`, `already-failed`, `helper-exists`,
`novel`) so repeats can be counted the way `violations.py` counts process faults.

The user's own framing matters: they noted the judgement structure had *already* improved enough to catch these
mistakes the same day — so this is not a rescue, it is removing a cost that is now the dominant one.
