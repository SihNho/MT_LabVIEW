---
type: reference
status: current
date: 2026-09-15
tags: [evaluation, prior-art]
---

# Prior-art reviewer — scores

Scored against `tools/bench/priorart_testset.md` (five failures that actually happened on 2026-09-15, with the
answer that was already on disk at the time). The plan under review is a synthetic one that commits all five:
`priorart_test_plan.txt`. A hit requires naming the FILE, not just the topic.

| run | index variant | model / effort | hits | cost | tokens (in / out / cache-create / cache-read) | wall | log |
|---|---|---|---|---|---|---|---|
| 1 | monolithic index, 84,067 chars (~21k tokens) IN THE PROMPT | opus / high | **5 / 5** | **$2.9149** | 22 / 18,416 / 170,953 / 1,489,746 | 228 s, 18 turns | `priorart_test_run1.log` |
| 2 | **NONE** (control) | opus / high | **5 / 5** | **$2.6154** | 32 / 15,533 / 126,829 / 1,917,230 | 240 s, 26 turns | `priorart_bench.log` |
| 3 | sharded (root+by-name ~3.5k in prompt, shards on disk) | opus / high | (void — transport) | $2.5325 | 28 / 16,566 / 128,027 / 1,675,935 | 227 s | `priorart_bench.log` |
| 4 | sharded, **same config as 3**, after the encoding fix | opus / high | **5 / 5**, citations verified | **$2.7616** | 24 / 19,502 / 155,409 / 1,439,644 | 249 s, 24 turns | `priorart_test_run4.log` |

Run 3 is logged as a NON-RESULT: the cell quoted Korean from STATUS.md, PowerShell decoded the cell's stdout with
the console code page, and the JSON envelope broke at character 5520. Verdict slugs were salvageable by regex but
their citations were not, so it cannot be scored. Fixed in `peer.ps1` (UTF-8 forced inside the job's runspace, and
the envelope taken as the last line that parses rather than first-brace-to-last-brace).

## THE FINDING: at this sample size the index makes no measurable difference

Runs 3 and 4 are the **same configuration** and differ by **$0.23**. That run-to-run variance is LARGER than the
spread between configurations ($2.62 … $2.91). So the honest reading is:

- **All three scorable arms got 5/5**, including the one with no index at all. `opus` at high effort finds these
  five by searching the repository itself.
- **The monolithic 21k index was the worst of the three** — most expensive, fewest verdicts. Loading a long listing
  into the prompt bought nothing.
- **The sharded index cannot be shown to help or hurt** on this evidence. An earlier reading of "-13%" was noise.

### What this kills

**The premise for reformatting 169 documents.** The coverage report identified them as yielding no facts to the
index — but the index is not what produces the hits, so rewriting documents to feed it is not justified by any
number we have. Do not start that work on this basis.

### What it leaves standing

- The reviewer itself: **5/5 three times over, with citations**, plus unplanted finds each time (a same-day peer
  refutation the plan ignored, an already-written recipe, and a real contradiction between `STATUS.md` and
  `docs/NAMES.md` that was fixed on the spot).
- The sharded index is kept because it is already built, costs nothing to maintain, is readable by a person, and
  emits the coverage report — not because it was shown to pay for itself.
- Cost of a review: **~$2.6–2.9, ~4 minutes, ~20-26 reading turns.**

---

# Test set II (HARD, split by index coverage) — the index CREATES A BLIND SPOT

`tools/bench/priorart_testset_hard.md`, 8 items: **A1-A4** whose answers are carried in the index with substance,
**B1-B4** whose answers live only in old, unannotated peer exchanges. Two arms, two repeats each, opus/high.
Scored by whether the run cited the answer's file anywhere in its response (the same rule for every arm).

| run | A1 | A2 | A3 | A4 | B1 | B2 | B3 | B4 | **A** | **B** | cost | turns |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no index, r1 | O | O | O | O | O | O | O | O | **4/4** | **4/4** | $3.0848 | 29 |
| no index, r2 | . | O | . | O | O | O | . | O | 2/4 | **3/4** | $2.7984 | 29 |
| sharded index, r1 | O | O | O | O | . | . | . | O | **4/4** | **1/4** | $3.5748 | 28 |
| sharded index, r2 | O | O | O | O | . | . | . | O | **4/4** | **1/4** | $3.6250 | 30 |
| | | | | | | | | | | | | |
| **mean, no index** | | | | | | | | | 3.0/4 | **3.5/4** | **$2.94** | 29 |
| **mean, sharded** | | | | | | | | | **4.0/4** | **1.0/4** | **$3.60** | 29 |

## The result

1. **The index works on what it contains.** 4/4 on group A in both runs, against 3/4 and variable without it.
2. **The index makes the reviewer WORSE at everything else.** Group B: **1/4 in both indexed runs, 3/4 and 4/4
   without.** Both repeats agree inside each arm, and the gap is large. Given an index, the cell anchors to it and
   stops searching the archive; given nothing, it searches and finds the old material.
3. **And it costs 22 % more** — $3.60 vs $2.94, with both indexed runs above both control runs.

Total recall is what matters, and the control wins it: **6.5 / 8 versus 5.0 / 8, for less money.**

This inverts the design. The index was built to stop prior art being missed; measured, it causes prior art to be
missed — precisely the old, half-forgotten kind that is the whole reason for this review. **Do not ship it as the
default.** And the document-reformat plan is doubly dead: feeding more material into the index would deepen the
blind spot rather than close it.

## What to try next, cheaply

The blind spot may be a prompt problem rather than an index problem. The index is presented as the evidence base,
so the cell treats it as complete. One line could change that: *"this index covers PART of the corpus — 148 of 226
archived exchanges are represented by slug only — so search `archive/` directly for anything it does not
mention."* Two runs ($7) would show whether that recovers group B while keeping group A at 4/4. Until then the
**control configuration (no index) is the default**, because it has the better total recall and the lower cost.

### What would actually settle it

More runs per arm (the variance demands it), or a harder test set: these five items are recent and well recorded.
Prior art that is old, scattered, or recorded only in passing is where an index should matter — and is not tested.

## Run 1 — what it caught

All five planted items, each with a citation:

| item | verdict line |
|---|---|
| T1 serial-ordering contradiction | `contradicted (camera-acquisition-facts.md:140,169 vs :195-198)` |
| T2 "move a node" already resolved | `settled-already (probe_migrate_v3.log:12, STATUS.md:283)` |
| T3 `VI.Get Errors` failed twice | `already-failed (build_opgeterrors.log:1-18; toolkit-capabilities.md:147,244)` |
| T4 wire 751's third consumer | `already-failed (orphaned node 482 — build_opwiresource_v5.log:35-39)` + `contradicted (census_opwiresource_v5.log:161,183,221)` |
| T5 helpers already exist | `helper-exists (new_since / loop_diagram / subvis — docs/NAMES.md:526-532)` |

**And four findings nobody planted**, which is the more interesting half:

- `refuted-already` — the ASI-first ordering had already been refuted by a peer review **the same day**
  (`restructure-in-copy-plan.md:11-16,93`), which the plan ignored;
- `unread-evidence` — the plan ignored the prior-art review already archived for that very build;
- `already-built` — `build_opownerchain_v0.py` already exists, written and corrected but never run;
- `contradicted (STATUS.md:321 vs docs/NAMES.md:518-522)` — **a real defect in my own documents**: NAMES.md had
  been corrected to say there is no rule about where a new Diagram lands, while STATUS.md still asserted the
  falsified "index 0" claim. Fixed on the spot.

## What run 1 does NOT establish

**The index's own contribution is unmeasured.** The cell ran 18 turns and read files directly, so the hits may owe
little to the 21k-token index. The control is the same plan and model with the index withheld: if the score holds
and the cost drops, the index is not paying for itself; if the score falls, it is. **Run that before reformatting
any documents** — otherwise a large rewrite would be justified by a number nobody has.

Note on caching: `cache-read` of 1.49 M shows the cell reuses its context heavily ACROSS ITS OWN TURNS, even though
nothing is cached between dispatches (each `claude -p` is a fresh process). So cost scales with how many turns of
reading the reviewer does, not with the prompt size alone.
