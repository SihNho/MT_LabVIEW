# Brief 131-2 — gate-fp drain + device-failed fix of retrospective-cycle130 (offline tooling)

Decision in force: `docs/violation-decisions.md:1797-1817` (device-failed 2026-10-02 04:52). The gate-fp queue is DUE
(6 open; fp-24 blocks a card). This card drains the hook-side entries; the stage_prerun entries (fp-19/20/21) stay open
because card 131-1 runs stage_prerun concurrently — say so in each one's queue note, do not drain them.

## P1 — guard_peer offline classification (fp-22, fp-24)
Rule decided: a command is OFFLINE when every module it runs is in `protocol.OFFLINE_SELFTESTS` or is a stage_prerun
`--dry`/`--prerun`/self-test whose COM is stubbed; an import that merely REACHES `gscript` without calling COM does not make
it LabVIEW-touching. MEASURE it before switching it on: replay the recorded argvs of fp-16/17/18/22/24 (each must now
pass) and every LabVIEW launch recorded in `tools/bench/stage_runs.jsonl` (each must still be held). Report the counts.
Then drain fp-22 and fp-24 (`py tools/gate_fp.py drain --id ... --fixed <path:line> --selftest <name>`).

## P2 — fp-25 (guard_bash card_flags / peer_role_of on a read-only `md5sum` naming `tools/peer.ps1`)
Read-only commands (md5sum, grep, cat, ls, wc, head) are never a peer dispatch. Fix, self-test, drain.

## P3 — `tools/hooks/guard_cycle.py:40` BUILD_RE matches `\bpy` inside a `.py` extension (e.g. `cp a.py tools/recipes/b.py`)
Fix so only a python invocation in command position counts; self-test both forms.

## P4 — every edited hook's existing self-tests rerun; counts listed.

## Rules
Offline only. Never edit `tools/stage_prerun.py`, `tools/stagesim.py`, `tools/stagexec.py`, `tools/stagekit.py`,
plans `plan_ring_p3b*`, or P3b recipes (card 131-1 is live on them). A hook edit is followed immediately by its self-test;
never leave a hook broken between steps. Return at the first unexpected result. result/1 in
`tools/bench/cards/result_131-2.json`.
