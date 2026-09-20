---
type: plan
status: current
date: 2026-09-16
tags: [documentation, lint, ingest, cycle-discipline]
---

# Documents are LINTED by code and INGESTED by a model, every cycle

The rule is already in `CLAUDE.md` §4 ("Documents are LINTED by code and INGESTED by a model every cycle",
user 2026-09-16: *"특정 주기마다 .md 파일들 ingest 및 lint 하는 규약 필요해보임"*, cadence *"주 단위보다는 싸이클 단위
혹은 실제 실행 단위가 적절해보임"*). This page is the build plan for the missing pieces, and nothing more: no new
review layer, no index (measured and rejected — `tools/bench/priorart_scores.md`).

**Corrected after the prior-art review** (`archive/peer/2026-09-16-priorart-doc-lint.md`). The first draft said
"nothing implements it", which is false and the review proved it: `tools/audit_cycle.py`'s **A4** already checks
review dispositions (with the same file list), **A7** is already a documentation lint (archive→active wikilink
direction), and `tools/frontmatter.py` already writes and detects frontmatter. What is genuinely missing is the
**citation check** — every cited project path and `file:line` in the active docs actually existing — plus the
model-read half. So the build is smaller than the draft implied, and the pieces it duplicates are cited, reused or
switched off rather than rewritten.

## 1. The rule, as CLAUDE.md §4 already states it

| layer | what | model | when |
|---|---|---|---|
| **lint** | `tools/doc_lint.py` — frontmatter valid; every cited path / `file:line` exists; STATUS ≤ ~100 lines; one `status: current` plan; `supersedes:` targets not still current; review dispositions not placeholders; unmarked decision sentences (warn) | none (a `.py`) | every cycle close, run by `audit_cycle` |
| **ingest — changed docs** | the claude peer as rule/consistency auditor over the cycle's changed files (audit C7 list): contradictions between them and with the active docs | **Sonnet** | every cycle close |
| **ingest — all active docs** | same audit over all of `docs/` + STATUS + CLAUDE.md | **Opus** | every 5 cycles (same rhythm as the outcome review) |
| **resolving** which document is right | — | judgement session | when the ingest reports a contradiction |

## 2. `tools/doc_lint.py` — no model, no judgement, exit code only on hard faults

Checks, each printing `PASS` / `WARN` / `FAIL` with `file:line`:

1. **Frontmatter present and valid** on `docs/*.md`, `STATUS.md`, `CLAUDE.md`, `archive/peer/*.md`
   (`---` block, `type:`, `status:`, `date:` parseable). WARN.
2. **Every cited project-relative path and `file:line` in the ACTIVE docs** (`docs/`, `STATUS.md`, `CLAUDE.md`)
   exists on disk — dangling citations are reported. FAIL. *This is the check the project actually needs:*
   `GLOSSARY.md` carried a wrong meaning, `STATUS.md` a superseded work order, and one file's summary line
   contradicted its own section 44 lines above — all of them citations nobody re-opened.
3. **`STATUS.md` ≤ 110 lines** (CLAUDE.md §4's "~100" with a margin, so the check does not cry wolf at 101). WARN.
4. **At most one `status: current` per plan family** (`docs/cycle*-plan.md`). FAIL — two current cycle plans is the
   state that makes every downstream window ambiguous.
5. **`supersedes:` targets are not still `status: current`.** WARN.
6. **`archive/peer/*.md` dispositions are not the placeholder** (`## What was done with it` missing, empty or
   `(Claude fills in)`). FAIL **when `doc_lint` runs standalone**, and **OFF** (`--skip-dispositions`) when it runs
   inside `audit_cycle`, because A4 already owns that condition. One condition must not have two FAIL sources —
   the prior-art review's `already-built` finding.
7. **Unmarked decision sentences** — a sentence containing `decided` / `결정` / `MEASURED` / `측정` with no
   `DECIDED:` / `MEASURED:` / `DECISION:` mark on the line. WARN only, and deliberately: this is the one check
   that would produce hundreds of hits and must never gate anything.

`exit 1` **only** on a FAIL: a dangling citation, a placeholder disposition, or more than one current plan.
Everything else is WARN and informational. Wired into `tools/audit_cycle.py` as a new section printing `L`-lines,
so it runs at every cycle close without a second command to remember.

## 3. `tools/doc_ingest.py` — the model half

"Ingest" means **a model reads the documents and reports what contradicts what** — it is not an index, and it does
not rewrite anything. It reports; the judgement session resolves.

- **Which files.** The audit's C7 list for the cycle window (files modified in the window), plus `STATUS.md` and
  `CLAUDE.md` always. `--full` instead reads all of `docs/` + `STATUS.md` + `CLAUDE.md`.
- **The task, fixed text:** *read these files; list every pair of statements that contradict each other or
  contradict CLAUDE.md/STATUS.md; cite `file:line` for both sides; no recommendations.* Facts only — a
  recommendation from this layer is judgement the session did not ask for.
- **Dispatch path:** `tools/peer.ps1 -Agent claude -Role ingest -Kind fact -Model sonnet -Slug ingest-<date>`, run
  under `tools/bgrun.py` like every other unattended dispatch. `--full --model opus` for the 5-cycle pass, matching
  the outcome review's rhythm. **`-Role ingest`, not a fourth `-Kind`** — `-Role` already distinguishes claude-peer
  jobs (`prior_art_review.py` passes `-Role priorart`), and `peer.ps1` already defines the RULE AND CONSISTENCY
  AUDITOR preamble and already pins that role to sonnet. The prior-art review's `helper-exists` finding.
- **Archive:** `archive/ingest/`, added to `peer.ps1` the way `archive/prose/` was (2026-09-16). It must be
  **invisible** to `guard_peer.py`, `guard_cycle.py`, `prior_art_review.py`, `violations.py`, `outcome_review.py`
  **and `audit_cycle.py`** — the draft omitted the last one, and it is the dangerous one: audit **A3** is satisfied
  by *any* `archive/peer/*.md` newer than a failing log, so an ingest pass landing there would have discharged the
  failed-prediction audit for every failing log in the window, and **A4** would then have demanded a disposition
  for it. All six glob `archive/peer/` only (verified 2026-09-16); the one deliberate exception is audit **A7**,
  which walks `archive/**` to check wikilink direction and should see ingest notes too.
- **Log classification:** `doc_ingest`, `doc_lint` and `ingest_` are registered in `tools/logclass.py` as
  **machinery, not builds** — before the first run, not after the fifth false positive. Four dispatchers have
  already broken this project by having an unregistered log name (`tools/logclass.py:9-17`), and this one quotes
  documents **verbatim**, including their own `FAIL` and `STOP at gate` lines, which `audit_cycle`'s `FAILURE_RE`
  would otherwise charge to the cycle as build failures.
- **Output:** the contradiction count on stdout, and the contradiction list in the archive.

## 4. First run

The first `doc_ingest` run targets **every file changed today, 2026-09-16** (window `2026-09-16 00:00` → now),
because that is the day STATUS was cut from 526 lines, CLAUDE.md gained the §3 and §4 sections, the retrospective
was rewritten, and two sessions edited the active documents concurrently. If contradictions exist anywhere, they
are there.

## 5. The standing delivery debt, recorded not discharged

The prior-art review fired `refuted-already` against this plan: the outcome review of 2026-09-15
(`archive/peer/2026-09-15-outcome-review-20260915.md:227`, `OUTCOME-VIOLATION: tooling-over-delivery`) says the
project's next problem is not missing tooling, and `CLAUDE.md` §5 says that verdict is answered by a **delivery
cycle**, not by another device. It was refuted on the record — this work is a standing rule the user gave on
2026-09-16, a day later, and its cycle contains no LabVIEW work at all — but **the debt itself is not discharged
by that**. `STATUS.md` still reads "168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and zero
runnable experimental VIs", and no delivery cycle is recorded since. The outcome review is due again
(`guard_cycle.py`: "6 cycle retrospectives since the last one, every 5"), and this paragraph exists so the next one
sees that the debt was noticed and deliberately not paid here.

## 6. What this plan deliberately does NOT do

- No index of any kind (measured: 6.5/8 recall without, 5.0/8 with — `tools/bench/priorart_scores.md`).
- No reformatting of the 169 existing documents to feed anything.
- No new gate that can block a build. `doc_lint` exits 1 inside `audit_cycle`; `doc_ingest` only reports.
- No resolution of the contradictions it finds — that is judgement work, by the table above.
