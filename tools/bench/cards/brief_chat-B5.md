# brief chat-B5 — ULTRACODE PILOT: one run, measure its cost (user 2026-09-29: "1회 실험으로 비용 판단 먼저 해보도록")

Rig 실험중: NO LabVIEW / GUI / hardware; never touch the user's LabVIEW process. Runner stays stopped.

Context: B4 (card chat-B4) was stopped mid-run by the chat; no ultracode run finished. The user now wants ONE
ultracode run first, to judge cost, before a new mixed bench (known-answer tasks + shadow runs in real cycles; all three
kinds — survey, troubleshooting, decision) is designed.

## Do exactly this
1. Run the existing ucbench task **L1** (doc contradiction audit, base 1d4caf8, key 9, lock already PASS —
   re-verify the lock/leak check only) with arm **UC** (`--effort ultracode`), **ONE repeat, nothing else running
   concurrently** (`--par 1`). Same cap as B4 (60 min). If ucbench.py cannot select a single task/arm, add the flags
   (minimal patch) rather than running the full matrix.
2. Record for that run: usd (envelope), wall minutes, number of sub-agents and Workflow calls, total tokens (main +
   sub-agents), 5-hour/weekly usage impact is NOT measurable by us — skip it.
3. Blind-score (uc_score, Opus 5.5 high scorer, arm hidden) FIVE L1 answers: the new UC answer and the four finished
   single-session answers already on disk (`tools/bench/ucbench/runs/full/L1/{SH_r1,SH_r2,SXH_r1,SXH_r2}/answer.md`).
   Report recall (mechanical and blind), precision, false claims, and "extra real findings" (claims outside the key
   judged real) per answer.
4. Write `tools/bench/ucbench/pilot_uc_L1.md` (facts only) and return result/1: the cost/time/agents numbers first,
   then the five-answer score table, `open:` for the chat. No recommendation.
