# priorart-doc-lint

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $2.5619  in 32 / out 22152 / cache-create 126614 / cache-read 1483582  (295s, 27 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (298s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
---
type: plan
status: current
date: 2026-09-16
tags: [documentation, lint, ingest, cycle-discipline]
---

# Documents are LINTED by code and INGESTED by a model, every cycle

The rule is already in `CLAUDE.md` 짠4 ("Documents are LINTED by code and INGESTED by a model every cycle",
user 2026-09-16: *"?뱀젙 二쇨린留덈떎 .md ?뚯씪??ingest 諛?lint ?섎뒗 洹쒖빟 ?꾩슂?대낫??*, cadence *"二??⑥쐞蹂대떎???몄씠???⑥쐞
?뱀? ?ㅼ젣 ?ㅽ뻾 ?⑥쐞媛 ?곸젅?대낫??*). Nothing implements it. This page is the build plan for the two missing pieces,
and nothing more: no new review layer, no index (measured and rejected ??`tools/bench/priorart_scores.md`).

## 1. The rule, as CLAUDE.md 짠4 already states it

| layer | what | model | when |
|---|---|---|---|
| **lint** | `tools/doc_lint.py` ??frontmatter valid; every cited path / `file:line` exists; STATUS ??~100 lines; one `status: current` plan; `supersedes:` targets not still current; review dispositions not placeholders; unmarked decision sentences (warn) | none (a `.py`) | every cycle close, run by `audit_cycle` |
| **ingest ??changed docs** | the claude peer as rule/consistency auditor over the cycle's changed files (audit C7 list): contradictions between them and with the active docs | **Sonnet** | every cycle close |
| **ingest ??all active docs** | same audit over all of `docs/` + STATUS + CLAUDE.md | **Opus** | every 5 cycles (same rhythm as the outcome review) |
| **resolving** which document is right | ??| judgement session | when the ingest reports a contradiction |

## 2. `tools/doc_lint.py` ??no model, no judgement, exit code only on hard faults

Checks, each printing `PASS` / `WARN` / `FAIL` with `file:line`:

1. **Frontmatter present and valid** on `docs/*.md`, `STATUS.md`, `CLAUDE.md`, `archive/peer/*.md`
   (`---` block, `type:`, `status:`, `date:` parseable). WARN.
2. **Every cited project-relative path and `file:line` in the ACTIVE docs** (`docs/`, `STATUS.md`, `CLAUDE.md`)
   exists on disk ??dangling citations are reported. FAIL. *This is the check the project actually needs:*
   `GLOSSARY.md` carried a wrong meaning, `STATUS.md` a superseded work order, and one file's summary line
   contradicted its own section 44 lines above ??all of them citations nobody re-opened.
3. **`STATUS.md` ??110 lines** (CLAUDE.md 짠4's "~100" with a margin, so the check does not cry wolf at 101). WARN.
4. **At most one `status: current` per plan family** (`docs/cycle*-plan.md`). FAIL ??two current cycle plans is the
   state that makes every downstream window ambiguous.
5. **`supersedes:` targets are not still `status: current`.** WARN.
6. **`archive/peer/*.md` dispositions are not the placeholder** (`## What was done with it` missing, empty or
   `(Claude fills in)`). FAIL ??the same condition `audit_cycle` A4 reports, here with the file list.
7. **Unmarked decision sentences** ??a sentence containing `decided` / `寃곗젙` / `MEASURED` / `痢≪젙` with no
   `DECIDED:` / `MEASURED:` / `DECISION:` mark on the line. WARN only, and deliberately: this is the one check
   that would produce hundreds of hits and must never gate anything.

`exit 1` **only** on a FAIL: a dangling citation, a placeholder disposition, or more than one current plan.
Everything else is WARN and informational. Wired into `tools/audit_cycle.py` as a new section printing `L`-lines,
so it runs at every cycle close without a second command to remember.

## 3. `tools/doc_ingest.py` ??the model half

"Ingest" means **a model reads the documents and reports what contradicts what** ??it is not an index, and it does
not rewrite anything. It reports; the judgement session resolves.

- **Which files.** The audit's C7 list for the cycle window (files modified in the window), plus `STATUS.md` and
  `CLAUDE.md` always. `--full` instead reads all of `docs/` + `STATUS.md` + `CLAUDE.md`.
- **The task, fixed text:** *read these files; list every pair of statements that contradict each other or
  contradict CLAUDE.md/STATUS.md; cite `file:line` for both sides; no recommendations.* Facts only ??a
  recommendation from this layer is judgement the session did not ask for.
- **Dispatch path:** `tools/peer.ps1 -Agent claude -Model sonnet -Kind fact -Slug ingest-<date>`, run under
  `tools/bgrun.py` like every other unattended dispatch. `--full --model opus` for the 5-cycle pass, matching the
  outcome review's rhythm.
- **Archive:** `archive/ingest/`, added to `peer.ps1` exactly the way `archive/prose/` was (`-Kind prose`,
  2026-09-16). It must be **invisible** to `guard_peer.py`, `prior_art_review.py` and `violations.py` ??all three
  glob `archive/peer/` only ??so an ingest pass can never lift a failed-prediction gate or be counted as a review.
- **Output:** the contradiction count on stdout, and the contradiction list in the archive.

## 4. First run

The first `doc_ingest` run targets **every file changed today, 2026-09-16** (window `2026-09-16 00:00` ??now),
because that is the day STATUS was cut from 526 lines, CLAUDE.md gained the 짠3 and 짠4 sections, the retrospective
was rewritten, and two sessions edited the active documents concurrently. If contradictions exist anywhere, they
are there.

## 5. What this plan deliberately does NOT do

- No index of any kind (measured: 6.5/8 recall without, 5.0/8 with ??`tools/bench/priorart_scores.md`).
- No reformatting of the 169 existing documents to feed anything.
- No new gate that can block a build. `doc_lint` exits 1 inside `audit_cycle`; `doc_ingest` only reports.
- No resolution of the contradictions it finds ??that is judgement work, by the table above.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-16
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Cycle 11??3 narrative relocated 2026-09-16 (rule 4; STATUS had reached 526 lines) to
**`archive/2026-09-16-status-cycles-11-13-narrative.md`**, unchanged. Open it only when a line here is ambiguous.
?좑툘 **ONE SESSION AT A TIME** ??two ran concurrently on 2026-09-16 and both edited the active docs. Check for a
live session, and **re-read `CLAUDE.md` and this file from disk** rather than trusting a summary.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`docs/cycle10-plan.md` is superseded ??it is that plan's Phase A).
   Settled decisions that must not be re-opened: **`docs/decisions.md`**. Current cycle plan: `docs/cycle14-plan.md`.
2. ??**Prior-art gate layer is live and its hole is fixed** ??`guard_cycle.py` accepts `REFUTED:` and
   `FIXED: <slug> - <path>:<line> - <what changed>` (5/5 tested; both forms in `CLAUDE.md` 짠"Review has THREE layers").
3. ??**Retrospectives for cycles 10??3 DONE and disposed.** 11 and 12 fired ALL NINE slugs, 13 fired six. That
   saturation is what `tools/retrospective.py` **v2** (2026-09-16) exists to fix; v1 frozen at
   `tools/retrospective_v1.py`; numbers in `tools/bench/retro_v2_comparison.md`.
4. ??**SOLVED ??scripting EDITS are silently declined until the target's FRONT PANEL has been opened** (not
   "until the diagram is loaded" ??refuted). Fixed by `ensure_loaded()` in `tools/gscript.py`, guarding 26 mutating
   wrappers; readers untouched. Measurement tables ??narrative archive, item 3.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# last held material/cycle13-A3b, 2026-09-16 20:10-20:11: diag_flatseq_diagrams_attach.py (END rc=0, 33 s, 5/0).
# MAIN VI NEVER OPENED (scratch copy of EMPTY_v0, deleted in the same run, gate Z); no op saved; pid 17996 exited.
# Earlier holders: archive/2026-09-16-status-cycles-11-13-narrative.md
```
**Never assume an instance exited** (measured: pid 14352 did not): `tasklist | grep -i labview`, kill strays.
Fresh instances ??1,500 handles; unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (user, 2026-09-16; CLAUDE.md rule 1b). **Only the user announces a state
change**; never infer one, and do not ask per incident inside a declared state.
Instruments: rotor counter **0** 쨌 magnet motor full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`. **A camera session open RESETS ROI *and* exposure** ??the acquisition loop must apply the
contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**; fixture work is unaffected
(10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand
**Stage 1 (analysis) CLOSED** ??`docs/`: `instrument-libraries`, `main-vi-subvi-identity`, `main-vi-panel-map`,
`main-vi-state`, `main-vi-startup`, `frame-loop-wire-graph`, `rotor-sign-diagnosis`. Raw: `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS**, cycles 1??3 (`docs/stage2-plan.md`). `Track_v6_CPU_core_v0.vi` 69/69 PASS 쨌
`Track_v6_CPU_queue_v0.vi` 162/162 PASS. **Say it exactly:** bit-identical to the reference for the **first 10,018
frames only** (before the first bead loss), and both are **replay** artefacts ??recorded TIFFs, `FOR` loops, no
live acquisition, no stop protocol.
**THE GAP (outcome review, 2026-09-15):** 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and
**zero runnable experimental VIs**.

## OPEN

1. ?윞 **Is the PERIODIC auto-reset gated by `Auto-Reset`?** Measured on the wire side: `ForLoop#1359`'s ten
   terminals carry **no** `Auto-Reset` (wire 9806) and zero panel-control sources ??**not gated at the wire level**.
   Not final ??a `Value` property read inside #1359 could still gate it; one read closes it (cycle 14 짠5). Tables ??narrative archive, OPEN 1.
2. ?윟 **Autofocus path CLOSED** ??the switch that stops the piezo is `Auto-Focus` (uid 24266);
   `CaseStructure #10407` fires every 25 frames ??3.6 Hz. `docs/camera-acquisition-facts.md`.
2c. ?윟 **uid 9775 READS camera geometry; the size the VI WRITES is the front-panel display area, not the ROI** ??
   the 1280횞1024 budget basis is safe. Do NOT widen to "the VI does not set frame size" (codex refuses it);
   residual test: `Property Items[] ??Is Write` over the 106 Property nodes.
3. **Archived reviews lacking frontmatter/annotation** ??audit A4 last read **81/106 annotated**; the bulk
   `frontmatter.py` pass is safe now, the annotations are judgement work (cycle 14 짠6).
4. `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it**.
5. **Startup drives instruments** (ASI on diagrams 10/88, PI on 1/3/4/5 ??`main-vi-startup.md:22-33`). Allowed
   while apart; a hard blocker at assembly. Excise node-by-node in the build log, not wholesale (rule 1a).
6??. ??RESOLVED ??bgrun's failure regex narrowed (11/11) and it now skips the inner-failure scan for REVIEW logs;
   the `premature-build` and `scope-creep` devices are built and tested. ??narrative archive.
9. ?윟 **A2 DONE** ??owner semantics for all six structure classes (54/54). `FlatSequence` is the one exception
   (owner uid 0, error 1055). `docs/diagram-hierarchy.md`. ??narrative archive for the three judgement calls taken.
10. ?윟 **A3 MEASURED for the 112 clean diagrams** (100 agree / 0 disagree; `tools/bench/diagram_tree_a3.json`).
   Left: exactly the **57 `FlatSequenceFrame` diagrams**, and they ARE reachable ??`FlatSequence.Diagrams[]` =
   **3578BC00** measured attaching. ?윞 Walking it needs ONE new op VI: the judgement call cycle 13's STOP condition reserved. ??narrative archive, OPEN 10.
11. ?윞 **Retrospective v2 BUILT and MEASURED, NOT ADOPTED as the gate** (`guard_cycle.py` accepts either form).
   v1 fired 9/9/6 slugs on cycles 11/12/13; v2 fired **2/2/1** with three *different* top faults and loss figures,
   and its DEVICE EFFECT question found a broken device (`audit_cycle.py:191`'s cost regex never matches
   `COST: $??, hiding $20.42 in cycle 11 alone). **Five OPEN judgement calls: `tools/bench/retro_v2_comparison.md` 짠7.**

## NEXT

?뵶 **CYCLE 14 IS BLOCKED AT ITS FIRST BUILD BY TWO SLUGS** ??`judgement-in-material` (4, threshold 3) and
`device-failed` (2, threshold 1, new). `guard_cycle.py` refuses the `OpFlatSeqDiagrams_v0` recipe build until a
judgement session writes dated `DECISION:` blocks in `docs/violation-decisions.md`. ?좑툘 The v2 comparison archives
feed this tally ??whether they should is OPEN-B. Nothing else in cycle 14 is blocked.
**Plan, written and reviewed: `docs/cycle14-plan.md`** ??짠3 the `Diagrams[]` op design (donor must be `OpSubVIs_v1`:
`Diagrams[]` needs a FlatSequence-typed ref ??a `To More Specific Class` is mandatory and TMSC cannot be scripted),
짠4 A3 ??170/170, 짠5 OPEN 1's last read, 짠6 A4.

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md` settled decisions** 쨌 `docs/NAMES.md` verified strings 쨌
`docs/toolkit-capabilities.md` API 쨌 `docs/restructure-plan-4.6.md` target 쨌 `docs/pre-rig-master-plan.md` the plan 쨌
`docs/diagram-hierarchy.md` A2/A3 쨌 the reasoning behind all of it in `archive/2026-09-16-status-cycles-11-13-narrative.md`,
`...-status-session-gate-and-autofocus.md`, `...-status-cycles-8-10-narrative.md` 쨌 `archive/` history (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

# PRIOR-ART REVIEW — `docs/doc-lint-plan.md` (trigger: new-op)

Nothing was built, run, edited or locked. Findings only.

## PART A — THE DIRECTION

### A1 SETTLED ALREADY — **no finding, deliberately**
The direction is settled *in the plan's favour*: `CLAUDE.md` §4 ("Documents are LINTED by code and INGESTED by a model every cycle") is the user's own 2026-09-16 instruction, and the plan cites it correctly. Two undocumented precedents exist for the practice — `archive/WORKLOG.md:109` (*"the markdown set was linted and restructured: STATUS.md was cut back from ~700 lines"*) and `archive/2026-08-31-status-full-assembly-narrative.md:10` (*"Last updated: 2026-08-30 (ingest/lint for a fresh session)"*) — both manual, neither a tool. I do not fire the slug; it would block work the user ordered.

### A2 REFUTED ALREADY — **fires**
Building two more process tools is what the outcome layer ruled against six days ago, and the plan never mentions it.

- `archive/peer/2026-09-15-outcome-review-20260915.md:227` — *"The project has enough knowledge and components. Its next problem is not missing tooling; it is failure to cross the boundary from replay proof to experiment product."*
- same file `:182` — *"They should, however, be asked **now**, before another tooling cycle."*
- same file `:230` — `OUTCOME-VIOLATION: tooling-over-delivery`
- `CLAUDE.md` §5 — *"An `OUTCOME-VIOLATION` is NOT answered by building a device … the next cycle becomes a **delivery** cycle."*

Still applies: `STATUS.md` still states the gap as current ("…two replay VIs and **zero runnable experimental VIs**"), and cycles 11–14 were each tooling cycles (`docs/cycle14-plan.md:9` builds `OpFlatSeqDiagrams_v0`). Nothing in the record shows the owed delivery cycle ran.

**Scope:** this does not say the lint is wrong. It says a standing verdict that stops tooling work is undischarged and unaddressed here. Release route: `REFUTED:` citing `CLAUDE.md` §4 (a user order outranks a peer verdict), or `FIXED:` pointing at where the delivery cycle is recorded.

### A3 CONTRADICTED — **fires, three ways**

**(i) "Nothing implements it" is false** — plan `docs/doc-lint-plan.md:12`. Against it:
- `tools/audit_cycle.py:170-182` — A4 already implements plan check **6** verbatim, *including* the file list the plan offers as its addition (`:182` prints `blank: {blank[:6]}…`).
- `tools/audit_cycle.py:193-205` — A7 is already a documentation lint (archive→active wikilink direction).
- `tools/frontmatter.py:19-21,101-104` — already writes and detects frontmatter, i.e. check **1**'s half.

**(ii) The dispatch line defeats the invisibility requirement three lines below it.** Plan `:58` says `-Kind fact`; `:61-63` demands `archive/ingest/`, invisible to the gates. `tools/peer.ps1:429` — `$archDir = if ($Kind -eq 'prose') { $proseDir } else { $peerDir }`, with `:79` `[ValidateSet('review','fact','prose')]`. As written, `-Kind fact` archives into `archive\peer\`.

**(iii) The exclusion list is incomplete.** Plan `:62` names `guard_peer.py`, `prior_art_review.py`, `violations.py` — and omits `tools/audit_cycle.py`, which globs the same directory twice: `:134` (A4 will demand a disposition for it) and `:165`, where A3 is satisfied by **any** `archive/peer/*.md` newer than the failing log. Combined with (ii), an ingest pass silently discharges the failed-prediction audit for every failing log in the window.

### A4 UNREAD EVIDENCE — **fires**
`tools/logclass.py` — the one classifier deciding whether a new dispatcher's bgrun log counts as a build. The plan runs `doc_ingest` under `bgrun` (`:58-60`) and never names it. See B2. Secondarily `archive/peer/2026-09-15-outcome-review-20260915.md` (A2).

## PART B — THE ARTIFACT

### B1 ALREADY BUILT — **fires**
Plan check **6** (`:38-39`) = `tools/audit_cycle.py:170-182` — same condition, same FAIL semantics (`audit_cycle.py:315-321` exits 1 on it), same file list. It is failing right now: `tools/bench/retro_cycle13.log:12` — `FAIL A4 … 81/106 annotated`. Duplicating it gives one condition two FAIL sources.

### B2 ALREADY FAILED — **fires**
A new review dispatcher whose log is unregistered in the classifier has broken this project **four times**: `tools/logclass.py:9-17` lists them; `tools/hooks/guard_peer.py:85-89` records the sharpest — *"`priorart_test_run1.log` blocked the next run because the reviewer had CITED `build_opgeterrors.log`'s 'STOP: not saved / rc=5'."* `tools/logclass.py:46-54` shows the registered prefixes (`peer_`, `retro`, `outcome_review`, `prior_?art`, `audit_cycle`, `violations`) — **no ingest or lint term**. `doc_ingest` is the fifth dispatcher, and its output is contradictions quoted verbatim from documents, so `FAILURE_RE` (`audit_cycle.py:62`: `STOP at gate|VERDICT: BROKEN|FAIL`) will match it.

Same class: check **2** (dangling citations, **FAIL**) repeats the shape of the checker that already cried wolf — `tools/audit_cycle.py:170-173`: *"matching the whole file reported 66 false violations on its first run (2026-09-15) — a checker that cries wolf gets ignored, which is worse than not having it."* And check **7**'s hundreds of WARN lines land inside the retrospective's evidence block, because `tools/retrospective.py:346` embeds audit stdout verbatim into the peer's task.

### B3 HELPER EXISTS — **fires**
- check 1 → `tools/frontmatter.py:115-116` (`--dry-run` already lists every `.md` lacking frontmatter).
- check 2's path resolution → `tools/hooks/guard_cycle.py:130-137` already resolves a project-relative citation and reports *"cited path does not exist under the project"*.
- the whole model half → `tools/peer.ps1:181` already defines the **RULE AND CONSISTENCY AUDITOR** preamble and `:250` already pins it to sonnet for this exact role; `tools/prior_art_review.py:124-175` is the dispatcher scaffolding (plan-file → task file → `peer.ps1` → archive). A role mechanism also already exists — `prior_art_review.py:170` passes `-Role priorart` — so distinguishing the ingest needs no new `-Kind`.
- it has been run before: `archive/peer/2026-09-15-cycle8-plan-rule-audit.md:51` — *"you are this project's rule and consistency auditor"*.

### B4 ALREADY MEASURED — **no finding**
The no-index question is measured and the plan cites it correctly (`tools/bench/priorart_scores.md`). The §4 first run is only *partly* pre-swept — `archive/2026-09-16-status-cycles-8-10-narrative.md:69,:165` record that a 2026-09-16 lint pass already added superseding banners and removed a stale block — but that pass was manual and not contradiction-systematic, so the run is not redundant. No slug.

## State facts (no slug attached)
- Four cycle plans are `status: current` today (`docs/cycle11-plan.md:3`, `cycle12`, `cycle13`, `cycle14`), so check **4** FAILs on its first run.
- `supersedes:` exists in two files and is empty in both (`docs/cycle11-plan.md:8`), so check **5** is a no-op today.
- `tools/retrospective.py:294-296` ignores `audit_cycle`'s return code, so the plan's "no new gate" claim does hold.

---

PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-built
PRIOR-ART: already-failed
PRIOR-ART: helper-exists

## Sources

(extract from answer)

## What was done with it

Six verdicts, all disposed. Five were right and the work changed; one is refuted on the record, with the citation
opened. The review cost $2.5619 / 298 s (`tools/bench/priorart_doc_lint.log`).

| verdict | disposition |
|---|---|
| `refuted-already` | **REFUTED** — see below |
| `contradicted` (i)(ii)(iii) | **FIXED** — plan corrected; `-Role ingest` + `archive\ingest\` routing added to `peer.ps1`; `audit_cycle.py` added to the exclusion list |
| `unread-evidence` | **FIXED** — `tools/logclass.py` read and amended |
| `already-built` | **FIXED** — `doc_lint`'s disposition check is off inside `audit_cycle` (`--skip-dispositions`); A4 keeps the FAIL |
| `already-failed` | **FIXED** — `doc_ingest`/`doc_lint`/`ingest_` registered as machinery **before** the first run; L2's matcher tightened after it produced 545 false positives on its first pass, exactly the crying-wolf failure the review cited |
| `helper-exists` | **FIXED** — reused `-Role`, the existing auditor preamble, C7, `cycle_window()` and `prior_art_review.py`'s dispatch shape; nothing re-implemented |

REFUTED: refuted-already - archive/peer/2026-09-15-outcome-review-20260915.md:227 and CLAUDE.md:379 both address how Claude should spend a LabVIEW TOOLING cycle, dated 2026-09-15; they do not cover work the user ordered on 2026-09-16 and wrote into CLAUDE.md:343 as a standing per-cycle rule. Detail below.

**The refutation in full** — `archive/peer/2026-09-15-outcome-review-20260915.md:227` says *"The project has
enough knowledge and components. Its next problem is not missing tooling"*, and `CLAUDE.md` §5 says an
`OUTCOME-VIOLATION` is answered by a delivery cycle, not by a device. Opened both. Neither covers this case, for a
dated reason: the outcome review is **2026-09-15**, and the instruction this plan implements is the user's own,
given **2026-09-16** — *"특정 주기마다 .md 파일들 ingest 및 lint 하는 규약 필요해보임"* — and written into
`CLAUDE.md` §4 as a standing rule with a cadence (`CLAUDE.md:343-356`). A peer verdict about how Claude should
spend a cycle does not survive the user ordering the work the next day; if it did, no user instruction could ever
be executed after an outcome review. Two further limits of the citation: the verdict's own scope line is
*"tooling-over-delivery"* about **LabVIEW op-building**, which is what cycles 11–14 were, and this task was
delegated as a no-LabVIEW documentation cycle running in parallel with none of that; and `:182` of the same file
asks for the delivery questions *"now, before another tooling cycle"* — which is a claim on the **next LabVIEW
cycle**, and is recorded here rather than discharged. The delivery debt is real and stays open; it is not
discharged by this refutation and should be the subject of the next outcome review.

FIXED: contradicted - docs/doc-lint-plan.md:15 - the "nothing implements it" claim is replaced by a paragraph naming A4, A7 and frontmatter.py, and the dispatch/archive/exclusion lines now say -Role ingest, archive/ingest/ and audit_cycle.py.
FIXED: unread-evidence - tools/logclass.py:60 - logclass was read and amended; doc_ingest, doc_lint and ingest_ are registered as machinery so their logs are never scanned as builds.
FIXED: already-built - tools/doc_lint.py:317 - the disposition check is switchable and audit_cycle calls it with --skip-dispositions, so A4 remains the single FAIL source for that condition.
FIXED: already-failed - tools/logclass.py:60 - the fifth dispatcher is registered before its first run rather than after the false positive, which is what broke the previous four.
FIXED: helper-exists - tools/peer.ps1:94 - ingest is a -Role on the existing auditor preamble, not a fourth -Kind; C7, cycle_window() and prior_art_review.py's dispatch shape are reused rather than rebuilt.
