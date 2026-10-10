---
type: rules
status: current
date: 2026-10-10
tags: [rules, review, peers, retrospective]
---

# Rules - reviews, peers and research

Restated briefly from `docs/rules/CLAUDE-full-2026-10-10.md` (cited ranges = full wording and quotes). The peers'
own brief: `docs/peer-brief.md`.

## Retrospective (cycle layer)

- **Cadence (acceleration, 2026-09-28):** the retrospective runs every 3rd cycle, in any cycle that saved no new build
  step, or when a violation slug is at threshold-1 - decided by `tools/retro_due.py`. The same approval: (1) pipeline -
  one LabVIEW card plus one offline prep card at once (`stage_prerun.py --rebase` before launch); (2) no prior-art review
  for a build step on a PROVEN pattern; (3) gate false positives go to `tools/bench/gate_fp_queue.jsonl`
  (`tools/gate_fp.py`), drained in batches, never by an env bypass; (4) up to ~25 rows per step on a proven pattern.
  **Run mode disabled (2026-09-29):** always PERFORMANCE; no self-imposed 5-hour/weekly usage gates anywhere; the
  platform usage-limit protocol still applies. `docs/rules/CLAUDE-full-2026-10-10.md:443-461`
- **Why:** a peer only sees a framing Claude wrote; the cycle itself is reviewed from the machine's record. Step 1:
  `py tools/audit_cycle.py` - mechanical compliance (bgrun discipline, runs terminated, failing logs reviewed, reviews
  annotated, originals untouched, GUI actions recorded, cost lines). `docs/rules/CLAUDE-full-2026-10-10.md:462-470`
- **Step 2: `py tools/retrospective.py --cycle N` (v2, 2026-09-16)** - a FIXED question set (repeated failure, missing
  tool, inference over measurement, rule compliance, ordering, unreported facts, judgement in material) plus a device
  effect question from `docs/violation-decisions.md`, with the audit, the cycle's build logs and the rules attached;
  Claude writes neither the questions nor the evidence. **Output contract:** the ONE most costly structural fault (at
  most two) as `VIOLATION: <slug> | loss_min=<n> | loss_usd=<n or ?> | evidence=<file:line>`; `VIOLATION: none` is
  legitimate; slugs from the known list (`repeated-failure-class`, `tool-not-built`, `inference-over-measurement`,
  `rule-evaded`, `wrong-ordering`, `unreported-fact`, `scope-creep`, `premature-build`, `judgement-in-material`,
  `device-failed` - threshold 1). `py tools/violations.py` counts slugs across retrospectives, from the files.
  `docs/rules/CLAUDE-full-2026-10-10.md:471-487`
- **At 3 of the same slug the next cycle builds the mechanical device for it first**; only the user may lower the
  threshold. The 2026-09-18 no-new-device order is LIFTED (2026-09-24): a judgement session may decide a tool is
  necessary and a material session builds it under every existing rule; deliverable-first still holds. Jev devices
  behind existing decision points are allowed, each measured on a labelled set first, advisory first; Jev scripts are
  exempt from the failed-prediction and material gates. **Jev review ladder:** a failed prediction goes first to Jev
  (our-script-bug / already-reviewed-class / new-problem); only new-problem (or no key / unknown band) owes the
  hypothesis review. **One review per row per cycle:** a failed prediction on the same script (`_vN` stripped) with an
  answered adversary review archived in the last 6 h is discharged by it (`RULE-SAME-ROW`). `tools/stagekit.py` is the
  stage-script library: every new stage/diagnostic is a <= 120-line file on it. `docs/rules/CLAUDE-full-2026-10-10.md:488-494`
- **Step 4:** `tools/hooks/guard_cycle.py` refuses the next RECIPE build while the previous cycle's logs have no newer
  retrospective or a slug is at threshold. `docs/rules/CLAUDE-full-2026-10-10.md:495-497`

## Peers (rule 5)

- **Peers advise, Claude manages.** Read-only research sub-agents, briefed by `docs/peer-brief.md`. **Dispatch only
  through `tools/peer.ps1`** (it enforces read-only, bounds every call, classifies the outcome, archives the exchange).
  Screenshots and reporter text may be attached; **never `.vi` files**. Attach a ~3-line "already ruled out" block for
  diagnostic questions. **A peer answer is a hypothesis** - confirm against the machine or vendor files; two models
  agreeing is not confirmation. Call them before expensive builds and when a diagnosis will drive real work; no
  approval, no call limit; on quota exhaustion degrade to working without that peer, never to waiting.
  `docs/rules/CLAUDE-full-2026-10-10.md:649-661`
- **Three review layers** - hypothesis (every failed prediction, `guard_peer.py`), cycle (retrospective,
  `guard_cycle.py`), **outcome** ("did any of it move the deliverable?", every 5 cycles or 7 days, against
  `project-requirements/`). The outcome reviewer must not share our priors (thin prompt; fable/medium `-Role outcome`
  as fallback). An `OUTCOME-VIOLATION` is NOT answered by building a device: the next cycle becomes a delivery cycle;
  once the user has answered a repeated verdict, the same verdict again does not stop the runner (only a changed verdict
  does). **From 2026-10-09 the outcome review IS a Claude-GPT discussion** (`outcome_review.py` = fallback,
  `--outcome-by review`). **Steering card:** a repeated verdict emits a `steer/1` card (tied to `docs/goalmap.json`);
  the judgement session follows it or refuses with evidence; two refusals of one item stop the runner and go to
  `decisions_pending.json`. **Retry cap:** one stage's LabVIEW runs per cycle are capped (`stage_prerun.py`
  `RETRY_CAP`, start 2); more needs a judgement card. `docs/rules/CLAUDE-full-2026-10-10.md:662-692`
- **Prior art (fourth layer)** - "has this already been done here?" (`prior_art_review.py`, gated by
  `guard_cycle.py`; not required on a PROVEN pattern). Any verdict other than `novel` stops the work; two releases,
  written into the review file with a citation: `REFUTED: <slug> - <file>:<line> says X, which does not cover Y
  because ...` and `FIXED: <slug> - <path>:<line> - <what changed>` (path exists, changed after the review, line under
  `## What was done with it`). An assertion is not a refutation; a promise is not a fix; `CYCLE_GUARD_OFF` is never the
  answer. `docs/rules/CLAUDE-full-2026-10-10.md:693-708`
- **Peers are asked to REFUTE - mechanical:** `peer.ps1 -Kind review` refuses confirm-bait and appends the adversarial
  set (strongest reason it is wrong, alternative explanation, what would falsify it, cheapest discriminating test);
  `-Kind fact` exempts pure API facts. `docs/rules/CLAUDE-full-2026-10-10.md:709-715`
- **Who may discharge a failed prediction:** an ANSWERED codex or gemini exchange, or an ANSWERED `-Agent claude
  -Role hypothesis` exchange (D3 amended 2026-09-18); no other claude role; a TIMEOUT/QUOTA/ERROR exchange never.
  *Mechanism:* `guard_peer.py`. `docs/rules/CLAUDE-full-2026-10-10.md:716-720`

## Research and verification

- **External search is MANDATORY** for every factual question about a tool, API, error or capability - by a peer or
  by Claude, never skipped. Trigger: about to write "X is not possible", "our tools cannot reach that", "so we fall
  back to GUI" - stop and search; claims about our own tools are factual claims. `docs/rules/CLAUDE-full-2026-10-10.md:721-730`
- **A failed prediction (predicted X, observed not-X) triggers peer review, all three parts:** multi-agent search
  asked to attack, monitoring of the dispatch (a failed/timed-out call told you nothing), and the devil's-advocate
  pass. A recurring error alert is a failed prediction too (`tools/lv_stallcheck.ps1` writes `STALL:` records;
  `guard_peer.py` blocks the next build until a newer review is archived); a second appearance of any error class gets
  the same treatment. The gate reads build logs only, not `tools/bench/peer_*.log`. Your own successful test does not
  discharge it. `docs/rules/CLAUDE-full-2026-10-10.md:731-750`
- **Devil's advocate before a diagnosis or plan drives real work** (and at every "impossible", before expensive
  construction, before destructive steps): name an alternative cause, what would falsify the hypothesis, run the
  cheapest separator; a peer adversary is asked to refute. If the user is raising the objections, the pass is not
  running. `docs/rules/CLAUDE-full-2026-10-10.md:751-760`
- **Name the level of verification:** structural (well-formed, `ExecState == 1`) is not functional (right numbers with
  real data). A never-run build is not verified; state the level in STATUS and every summary. `docs/rules/CLAUDE-full-2026-10-10.md:761-768`
- **The research ladder:** codex (`gpt-5.6-sol`/medium, selectable, no longer default); agy/gemini = first arm of
  `-Kind fact` with no `-Agent` from 2026-10-01 (`gemini-3.1-pro-high`, 600 s, falls back to the claude fact role; an
  answer that drives an expensive build is re-checked with `-Agent claude -Kind fact`); claude: `-Role` decides model,
  web and brief (audit/ingest Sonnet, priorart Opus 5.5 medium, hypothesis Opus 5.5 high + web, fact/outcome/prose
  thin). THIN = `--safe-mode` (no CLAUDE.md, skills, hooks, MCP). One peer per question; fallback claude -> Claude's own
  research; "no peer available" never means experimenting without research. `docs/rules/CLAUDE-full-2026-10-10.md:769-789`
- **Codex's roles moved to Claude sub-sessions (2026-09-18):** `-Kind fact`/`-Kind prose` without `-Agent` -> claude
  fact/prose roles; `outcome_review.py` -> claude outcome role; failed-prediction review -> `-Agent claude -Role
  hypothesis` SINGLE arm (`-Dual` stays available). Check routing with `-DryRun`. `docs/rules/CLAUDE-full-2026-10-10.md:790-810`
- **(history) hypothesis reviews moved to an Opus/max claude peer (2026-09-17)**, built with `-Dual`; superseded
  2026-09-18 by the single claude arm; `-Dual` remains the right call when a claim about our own tools needs a second
  opinion that does not share our priors. `docs/rules/CLAUDE-full-2026-10-10.md:811-833`
- **Archive every peer exchange** to `archive/peer/YYYY-MM-DD-<slug>.md`; copy direction-changing conclusions into an
  active doc. Exception to rule 4: check `archive/peer/` for the same question before re-asking. `docs/rules/CLAUDE-full-2026-10-10.md:834-840`
- **Claude-GPT live discussions** (2026-10-09): on a topic the user gives and starts, both write each round at once
  and critique until they converge; a program writes each round into a Google Doc; the user steps in through the chat;
  Gemini fact-checks on request. How: `docs/debate.md`. `docs/rules/CLAUDE-full-2026-10-10.md:841-848`

Related decisions: `docs/decisions/review_structure_has_three_layers.md`,
`docs/decisions/prior_art_review_is_the_fourth_peer.md`, `docs/decisions/devils_advocate_before_acting_on_a_diagnosis.md`,
`docs/decisions/codex_roles_move_to_claude.md`, `docs/decisions/claude_gpt_debate_live_gdoc.md`.
