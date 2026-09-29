# brief chat-B2 — decbench: three case swaps, re-lock, FULL RUN, report (user 2026-09-29: "벤치 설계 및 실행해보도록", "다중 병렬로 돌려도 문제 없을 것 같은데")

Rig 실험중: no LabVIEW / GUI / hardware (a LabVIEW process of the user's experiment may be running — never touch it).
Input state: card chat-B1 PASS (`tools/bench/cards/result_chat-B1.json`, artefacts under `tools/bench/decbench/`).

## Chat's decisions on B1's open items
1. **T2 → replace** (smoke saturated: 5/5 arms 1.0). New troubleshooting case with a machine-settled root cause that
   is NOT stated in the failing log itself. Candidates: cycle 116 `guard_peer` blocked by the card's own baseline check
   (116-1); cycle 118's `read_const_value` returning void for non-String constants (118-2); a stall/handle incident
   with an archived root cause. Choose the one whose smoke answer is least likely to be a single-grep find.
2. **S3 → replace** (its answer is a user rule made after base; not derivable). New steering case whose right next
   act follows from the files AT base (rules + evidence), e.g. a cycle whose NEXT repeated a failing full-length
   retry when CLAUDE.md's split-and-save rule already required a decomposition plan, or an outcome verdict the next
   plan ignored.
3. **R3 → replace** (duplicates S1). New review case = the chat's own erroneous synthesis of 2026-09-29, reviewed at
   base = current HEAD (report_v1.md exists there). Claim text to review (give it verbatim as "a summary to review"):
   - "On matbench v1, effort changed the score only on T1 and T3; only T1 exceeded repeat noise."
   - "Judgement A/B: high 2.17 vs medium 1.57 PASS/cycle at $37.18 vs $38.24 per cycle, so high is also cheaper."
   - "Fable 5.1 low scored 5/5 at $17.59 against Opus high 8/10 at $15.24, so Fable costs about the same."
   Known defects: T2 also changed with effort (report_v1.md:8/:27, :34 names only T5/T6 as unchanged); the per-cycle
   cost includes material spend and cycles 89–91 ran Fable-low material (.claude/agents/material.md:8-10) so the cost
   comparison is confounded; 5 cells vs 10 cells totals — per cell Fable low $3.52 ≈ 2.3× Opus high $1.52.
   Leak check: these sentences must not be on disk in the worktree.
4. Rubric: tighten B2's regex; the blind scorer KEEPS the answer key (answer-key grading) and never sees arm/model;
   answers shuffled.
5. Then `--lock` again (all 10 rubrics md5-pinned, leak 10/10) — the full run starts only from a PASS lock.

## Full run
All 10 cases × 5 arms × 2 repeats, `--par 10`, worktree ops serialized, rate-limit cells invalid and re-run from the
start (a partial cell never enters the table; usage-limit rule: at a limit error, record the resume point, stop, and
return BLOCKED with the renewal time — the chat schedules the resume). Record per arm-run score (mech + blind),
minutes, usd, turns, tool calls.

## Report (`tools/bench/decbench/report_v1.md`)
- Per category (steering / troubleshooting / peer review) × arm: mean blind score, mean mech score, usd and minutes
  per case, and repeat spread (r1 vs r2).
- Peer review: defect hit rate on R1–R3 and false-alarm result on R4 (clean) separately.
- Which cases discriminate (between-arm range > within-repeat range), as matbench v1 did.
- Mech vs blind disagreements listed.
- No recommendation — facts only; the chat judges.
Return result/1 (≤ 10 facts, the table's key numbers, `open:` for what the chat must decide).
