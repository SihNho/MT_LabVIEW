# selftest-fact-role

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.6380  in 2 / out 4 / cache-create 31889 / cache-read 0  (3s, 1 turn(s))
- **date:** 2026-09-18 16:07:54
- **outcome:** ANSWERED (4s)
- **why asked:** SELF-TEST, not a research question: the one real call of `tools/bench/peer_roles_selftest.py`
  section C, proving the new default `-Kind fact` route (claude / role fact / fable / low / `--safe-mode`) dispatches,
  answers and reports a cost line. User's decision 2026-09-18 (TRIAL): codex's roles move to claude sub-sessions.
- **verdict:** route works

## Question

Reply with the single word OK and cite nothing.

## Answer

OK

## Sources

(extract from answer)

## What was done with it

The COST LINE was the product, not the answer. **$0.6380 · in 2 / out 4 / cache-create 31,889 / cache-read 0 ·
3 s · 1 turn**, against the full-context opus/max arm of 2026-09-17 (`$1.8621`, cache-create **158,866**, 70 s,
11 turns — CLAUDE.md section 5). `--safe-mode` cut the fixed context by **5.0x** (158,866 → 31,889 cache-creation
tokens), which is what the thin roles were built for; the residual 31,889 is the cell's own base system prompt and
tool definitions and no flag reaches it. Recorded in `tools/bench/peer_roles_selftest.log` (16 PASS / 0 FAIL,
`BGRUN END rc=0 after 7s`). No project file was read by the cell and nothing was built from this exchange.
