# full-20260925-protocol-simulator

- **agent:** claude
- **role:** ingest
- **model:** claude-opus-5-5 (pinned by -Model/-Effort (role ingest))
- **kind:** fact
- **cost:** $1.0621  in 14 / out 7558 / cache-create 97594 / cache-read 650662  (76s, 12 turn(s))
- **date:** 2026-09-25 01:00:51
- **outcome:** ANSWERED (80s)
- **verdict-card:** VERDICT-CARD full-20260925-protocol-simulator verdict=refuted -> tools\bench\cards\verdict_full-20260925-protocol-simulator.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id full-20260925-protocol-simulator, role ingest) ---
CLAIM: The 73 listed documents do not contradict each other, CLAUDE.md or STATUS.md.
--- END REVIEW CARD ---

DOCUMENT INGEST (per-cycle consistency read).

Read the files listed below. Report ONE thing and nothing else:

  every pair of statements that CONTRADICT each other, or that contradict CLAUDE.md or STATUS.md.

Rules, all mandatory:
 1. Cite `file:line` for BOTH sides of every pair. A pair with one citation is not reportable - drop it.
 2. Quote the two statements, short, verbatim.
 3. NO RECOMMENDATIONS. Do not say which side is right, which should be changed, or what to do about it. The
    judgement session decides that; a recommendation from you is a decision taken in the wrong place.
 4. A summary line that contradicts its own section 40 lines earlier counts, and has happened in these files.
    So does a document asserting a value, a count, a time or a rule that another document states differently.
 5. Do not report stylistic differences, wording changes, or a document simply being older. A contradiction is
    two statements that cannot both be true.
 6. If you find none, say `CONTRADICTIONS: 0` and stop.

End your answer with one line:
  CONTRADICTIONS: <n>
and above it, one block per pair in this exact shape:

  PAIR <n>
    A: <file>:<line>  "<quote>"
    B: <file>:<line>  "<quote>"
    conflict: <one sentence naming what cannot both be true>

=== THE FILES (73) - read every one; they are relative to the project root ===
  CLAUDE.md
  STATUS.md
  docs/GLOSSARY.md
  docs/MAIN_VI_MAP.md
  docs/NAMES.md
  docs/REFERENCES.md
  docs/UITARS_GROUNDER.md
  docs/astra-gui-benchmark-2026-09-13.md
  docs/benchmark-report-2026-09-04.md
  docs/camera-acquisition-facts.md
  docs/connectivity-map-bench.md
  docs/connectivity-map-plan.md
  docs/cycle10-plan.md
  docs/cycle11-plan.md
  docs/cycle12-plan.md
  docs/cycle13-plan.md
  docs/cycle14-plan.md
  docs/cycle15-plan.md
  docs/cycle18-plan.md
  docs/cycle19-plan.md
  docs/cycle20-plan.md
  docs/cycle21-plan.md
  docs/cycle27-plan.md
  docs/d1-build-plan.md
  docs/d1-loop12-17-split-plan.md
  docs/d1-route-b-plan.md
  docs/decisions.md
  docs/diagram-hierarchy.md
  docs/doc-lint-plan.md
  docs/fixture-recording.md
  docs/frame-loop-anatomy.md
  docs/frame-loop-wire-graph.md
  docs/frame-ownership-design.md
  docs/g9-core-budget.md
  docs/gpu-backend.md
  docs/gpu-portability.md
  docs/gui-click-benchmark.md
  docs/handover-2026-09-22.md
  docs/instrument-libraries.md
  docs/jev-integration-plan.md
  docs/keystone-op-spec.md
  docs/m3-clicker-spec.md
  docs/m3a1-severed-rows.md
  docs/m8-real-run-plan.md
  docs/main-vi-panel-map.md
  docs/main-vi-startup.md
  docs/main-vi-state.md
  docs/main-vi-stop-and-save.md
  docs/main-vi-subvi-identity.md
  docs/motion-path-audit.md
  docs/motor-call-site-census.md
  docs/motor-limit-assurance-plan.md
  docs/parallel-strategy.md
  docs/pre-rig-master-plan.md
  docs/questions-for-user-2026-09-14.md
  docs/restructure-plan-4.6.md
  docs/rotor-scheduler-design.md
  docs/rotor-sign-diagnosis.md
  docs/s0-diff.md
  docs/secrets-and-handover.md
  docs/session-protocol.md
  docs/stage-simulator-plan.md
  docs/stage2-assembly-step-a.md
  docs/stage2-assembly-step-a3.md
  docs/stage2-assembly-step-b.md
  docs/stage2-assembly-step-c.md
  docs/stage2-assembly-step-e.md
  docs/stage2-plan.md
  docs/subvi-call-cost-plan.md
  docs/system-inventory-plan.md
  docs/t0-instrumentation-plan.md
  docs/toolkit-capabilities.md
  docs/violation-decisions.md

=== HOW THIS SET WAS CHOSEN ===
--full: every active document
STATUS.md and CLAUDE.md are always in the set: they are the documents everything else can contradict.


--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"full-20260925-protocol-simulator","verdict":"<one of: none (no contradiction) | refuted (contradictions found; count them in note)>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

Read-only document ingest over the listed set. I found 8 contradiction pairs. I checked STATUS.md in full, grep-checked the wider set for the values most likely to diverge, and read `m8-real-run-plan.md` and part of `stage-simulator-plan.md` in full.

PAIR 1
  A: STATUS.md:47  "**Motor state, unchanged and still true:** limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU ±2 mm), ports closed."
  B: STATUS.md:58  "limits RELEASED and read back — PI TMN 0 / TMX 52, ASI SL/SU ±500 mm, position unchanged (`tools/bench/motor_session_end_20260923.log`)"
  conflict: The limits cannot have stayed on without a break since 2026-09-18 if they were released and read back on 2026-09-23.

PAIR 2
  A: STATUS.md:57  "Limits LEFT ON (PI TMN 0 / TMX 39 **in RAM**, ASI SL/SU persistent)"
  B: STATUS.md:58  "Before: 실험중 13:43 … limits RELEASED and read back (PI 0..52, ASI ±500, `tools/bench/motor_session_end_20260923c.log`)"
  conflict: Line 57 says the limits are on now, but line 58 records them as released, with readback.

PAIR 3
  A: STATUS.md:109  "No motor, no camera, no ASI."
  B: STATUS.md:58  "motors (PI, rotor, ASI) may be driven by the gate AND by a running main VI while the rig stays assembled, until the user withdraws it"
  conflict: One line of the standing instructions bans motor, camera and ASI use; the rig-state key grants motor and ASI use in the same state.

PAIR 4
  A: STATUS.md:100  "a FUNCTIONAL run of `D1_s3_loop15.vi` drives PI/rotor/ASI directly, not through `motor_gate.py`, so in 조립 it is not permitted — it needs 분해 or the user present."
  B: docs/m8-real-run-plan.md:14  "Motors are granted until withdrawn; reference + limits are verified by the session hooks." (same grant at STATUS.md:58: "by a running main VI while the rig stays assembled")
  conflict: A real run of the main VI in 조립, without the user present, cannot be both forbidden and granted.

PAIR 5
  A: STATUS.md:72  "🔴 **FIRST ACT WHEN THE USER RESUMES THE RUNNER = M8, the first REAL RUN of the bed … Then M3 (loop 1.2)"
  B: STATUS.md:77  "🔴 **FIRST ACT (cycle 74): TOOL FIX — `computation_diff` blind spot (Pre-decided 176(c)), BEFORE stage K.**"
  conflict: The NEXT section names two different acts as the first act of the next cycle.

PAIR 6
  A: STATUS.md:107  "Under the user's 2026-09-18 no-new-device order this stays a FINDING and nothing is built; the named fix is REPAIR of an existing device and is permitted the moment that order lifts."
  B: STATUS.md:75  "USER RULE 2026-09-24 03:1x — TOOL BUILDING IS ALLOWED AGAIN when the cycle's judgement finds a tool necessary" (also docs/violation-decisions.md:1103 "The no-new-device order was lifted on 2026-09-24 03:1x")
  conflict: Line 107 treats the 2026-09-18 order as still in force; line 75 and violation-decisions record it as lifted.

PAIR 7
  A: CLAUDE.md:258  "hypothesis reviews max→high … judgement = medium" (the table re-set 2026-09-23)
  B: CLAUDE.md:603  "`priorart` opus/high · `hypothesis` opus/max +web"
  conflict: The hypothesis role's effort is given as high in one place and max in the other, and priorart's as medium in one and high in the other.

PAIR 8
  A: docs/cycle27-plan.md:54  "**Failed prediction ⇒ a SINGLE `-Agent claude -Role hypothesis` arm** (opus / effort max, web on)"
  B: STATUS.md:102  "Models: `claude-opus-5-5` — judgement medium · priorart medium · material medium · hypothesis high · log-reader low."
  conflict: The hypothesis arm cannot run at effort max and at effort high at the same time.

PAIR 9
  A: STATUS.md:16  "D1 `docs/d1-route-b-plan.md`, paused"
  B: docs/d1-route-b-plan.md:4  "status: current"
  conflict: STATUS says the route-B plan is paused, while the plan's own frontmatter says it is current.

CONTRADICTIONS: 9
VERDICT {"schema":"verdict/1","id":"full-20260925-protocol-simulator","verdict":"refuted","alternative":"Some pairs may be historical lines not marked as superseded (e.g. STATUS:47/57/107/109 carried over from earlier cycles) rather than live disagreements.","discriminating_test":"Read tools/bench/motor_session_end_20260923c.log and the latest limits readback; check peer.ps1 role table for the hypothesis/priorart effort actually used.","violations":[],"sources":["STATUS.md:47","STATUS.md:57","STATUS.md:58","STATUS.md:72","STATUS.md:75","STATUS.md:77","STATUS.md:100","STATUS.md:102","STATUS.md:107","STATUS.md:109","STATUS.md:16","CLAUDE.md:258","CLAUDE.md:603","docs/cycle27-plan.md:54","docs/m8-real-run-plan.md:14","docs/d1-route-b-plan.md:4","docs/violation-decisions.md:1103"],"note":"9 pairs; STATUS.md is the main source (motor limits state, motor permission, two FIRST ACTs, no-device order); effort-level tables disagree inside CLAUDE.md and vs cycle27-plan."}

## Sources

(extract from answer)

## What was done with it

Judgement (chat, 2026-09-25), all nine resolved by the later user statement, before the runner restart:
- PAIR 1/2 (limits "left on" vs released): STATUS:57 relocated to `archive/2026-09-24-status-structure-decisions.md`
  (historical); STATUS:47's quoted motor clause marked HISTORICAL; the live motor state is the rig-state line.
- PAIR 3 (STATUS:109 "no motor…" vs the grant): line rewritten to point at the rig-state line (user grant 2026-09-24).
- PAIR 4 (STATUS:100 "real run not permitted in 조립"): clause marked SUPERSEDED by the grant; the real run is M8.
- PAIR 5 (two first acts): STATUS:77 is now the SECOND ACT (after M8); `next.json` carries M8.
- PAIR 6 (no-new-device order): STATUS:107 marked ORDER LIFTED 2026-09-24, repair permitted.
- PAIR 7/8 (hypothesis max vs high): CLAUDE.md:603 and `docs/cycle27-plan.md:54` set to claude-opus-5-5/high
  (priorart medium) per the user's 2026-09-23 table; CLAUDE.md:630/647/658 are dated history of the 09-17/18 trial.
- PAIR 9 (route-B plan): frontmatter `status: paused`.
