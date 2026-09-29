# brief chat-B4 — ucbench FULL RUN (user 2026-09-29: "이걸 벤치해보자. 사실 이게 핵심이거든")

Rig 실험중: no LabVIEW / GUI / hardware; never touch the user's LabVIEW process. Input: card chat-B3 PASS
(`tools/bench/cards/result_chat-B3.json`, `tools/bench/ucbench/`).

## Chat's decisions on B3's open items
1. **L3 hardened:** the key becomes (slug, cycle) pairs with per-slug counts (~110 items), computed by the BASE's own
   tools as before; recall/precision on pairs; count accuracy reported separately. Re-lock (leak PASS) before the run.
2. **Add arm S-XH** = one `claude-opus-5-5` session at effort **xhigh**, same prompt/tools/cap. Reason: UC runs at
   `--effort ultracode` (xhigh + Workflow), so UC vs S-XH isolates the orchestration effect. Arms: S-H, S-XH, S-MX, UC.
3. **No smoke re-run**; the guard fix is self-tested (13/0). Go to the full run. A cell broken by a guard/rate-limit
   error is invalid and re-run from the start (never partial).

## Run
2 reps × 3 tasks × 4 arms = 24 runs (+ blind scorer cells), `--par` as B3 proposed (raise for 4 arms if the 5-hour
limit allows), `--cap-min 60`, `--guard-usd 450`. Usage-limit rule: record the resume point and return BLOCKED with
the renewal time.

## Report `tools/bench/ucbench/report_v1.md` — facts only, no recommendation
- Per task × arm: recall, precision, false claims, usd, wall minutes, sub-agent count, tokens; r1 vs r2 spread.
- UC vs S-XH (orchestration effect) and UC vs S-MX (cost-matched alternative) called out per task.
- Which tasks discriminate (between-arm range > within-repeat range).
- Items found ONLY by UC and items found only by single sessions (ids), to see what kind of item fan-out catches.
Return result/1 (≤ 10 facts, key numbers, `open:`).
