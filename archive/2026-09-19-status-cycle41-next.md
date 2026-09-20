---
type: archive
status: archived
date: 2026-09-19
tags: [status-relocation, cycle41, run9]
---

# STATUS NEXT narrative from cycle 41 (run 9), relocated VERBATIM

Rule 4 relocation by the cycle-42 material session (step 2), 2026-09-19 07:3x, after run 10 superseded it.
Nothing is rewritten; the text below is exactly the block that stood in `STATUS.md` under `## NEXT` between the
run-10 launch instructions and the `✅ DONE IN EARLIER CYCLES` pointer, plus the `🟢 DECIDED cycle 41` block.

## §1 — run 9, E1, P2, the prior-art gate, `error 2`, and what cycle 41 closed

⚠️ **RUN 9 RAN, CRASHED `rc=1` BEFORE S5 — AND NO PREDICTION MISSED.** Lead with the crash, never with the gate
score: retrospective-cycle41 F6(a) found the earlier "80 PASS / 0 FAIL" headline is the sentence that gets quoted,
and it is the same fault class as cycle 40's "judged run 8 by the rows its predictions named". The run never reached
S5, so **it produced no VI**. `tools/bench/build_d1_routeb_v6_run9.log`, `BGRUN END rc=1 after 1817s`
(`:509`), 80 PASS / 0 FAIL gates, ledger `:363` **66 attempted / 54 WIRED / 11 FAILED / 1 NO-ROUTE** — run 8's
regression is REVERSED (WIRED 53 → 54, FAILED 12 → 11). Original md5 `2a78e17c…` UNCHANGED `:13`/`:494`; nothing
saved, nothing run. ExecState S1 cold 0 = UNREAD `:37`, live copy PRELOADED 1 `:491`. No failed-prediction review
is owed.
✅ **E1 SETTLED THE `Z/dZ` ROUTE ON THE MACHINE** — t0 **PASSES J2** at `_wddelta == 1` (`:360`), logged WIRED
(`:464`): identity True (w29238 is both the control's own wire and the sink wire, exactly one reciprocal source
terminal), Diagram[24] delta `(31,32,1)`, `Is Broken? False`, sink read back 29238. **`#2222` t0/t2/t3/t4/t5 ALL
WIRED** (`:464-:468`, `Is Broken? FALSE` on t3 and t4).
🔴 **BUT P2 DID NOT PASS — IT WAS UNTESTED, AND THAT DISTINCTION IS THIS CYCLE'S MAIN RESULT.** The census printed
`CENSUS: 0 survived / 0 bare / 51 unread of 51 claimed` (`:365`) because all five `diag_index` calls raised
`report_all(Diagram) … error 2` (`:364`). So `BARE = 0` is **VACUOUS** and **route B's `WIRED 54` is STILL an
attempt count**, exactly as after run 8. Do not quote it as survival (Pre-decided 18 as amended).
✅ **THE PRIOR-ART GATE PAID FOR ITSELF** — `archive/peer/2026-09-19-priorart-d1-routeb-run9.md` (NOT NOVEL,
opus/high, $4.2179, 5 findings, all accepted, applied and released with `FIXED:` lines). B2 predicted that the
census as first cut would print a confident `0 survived / 51 gone` when its own walks died; B4 that uid inequality
is not wire death on cross-boundary wires. Run 9 hit B2's failure exactly — and reported **51 UNREAD** instead of a
phantom wiring catastrophe. Contract now in Pre-decided 18.
🔴 **`error 2` IS NOW THE WHOLE BLOCKER.** Run 9: **11 ledger rows** (`:473-:483`, 10 × `report_all(Diagram)` +
1 × `report_all(WhileLoop)`), **5 more** inside the census's `diag_index` (`:364`), and the terminal
`count(LoopTunnel)` crash in `settle_index_modes` (`:486`, `:508`) that makes rc=1 — so **no route-B run has ever
reached S5, and none has ever produced a saved D1 VI.** Every victim across runs 8 and 9 is a **traverse**
(`Traverse for GObjects.vi`), whatever the class. **Never attribute it to a handle count**: healthy at
51,349 / 51,353, crashed at 35,551 / 35,555 (`archive/peer/2026-09-19-routeb-run8-predictions.md` Q3). The live
hypothesis — cumulative allocation failure inside one instance — is UNCONFIRMED and run 10 is its test.
✅ **CLOSED THIS CYCLE — do not re-open:** Pre-decided **19** (`Z/dZ`) is machine-confirmed · Pre-decided **17** is
confirmed by replication 2 × 2 (runs 6/7 with the in-loop reaper lost `#2222`'s terminals; runs 8/9 without it
wired every one) and **the K1 scratch-copy separator is RETIRED** — it would only confirm what two builds already
replicate · Pre-decided **18** is amended with the four-bucket census contract. Run 8's narrative →
`archive/2026-09-19-status-cycle39-run8.md` §7; cycle-39 chain → `archive/2026-09-19-status-cycle39-judgement.md`.
🔧 **THE STALL WATCHDOG REPAIR IS DONE AND PROVEN — do not redo it.** `tools/lv_stallcheck.ps1:273` now writes the
gating `stall_pid*.log` ONLY when the dialog check returns `VERDICT: BLOCKED`; self-test
`tools/bench/repair_c40_stall_selftest.log` **8 PASS / 0 FAIL**. Its discharge review went to **gemini, not
opus** — `archive/peer/2026-09-19-stall-selftest-c39-g78b.md` (ANSWERED) — because an assertion-string bug does
not warrant a $4.5 arm and gemini is an authorised discharging agent. Gemini's Q1 ("the repair removed a
capability") is REFUTED by that 8/0 run: `flagged` flipped False → True with `lv_stallcheck.ps1` untouched.
⚠️ **ONE THING LEFT — one read, no new device**: gemini's Q2, that `$record` set to the sentinel string
`NOT WRITTEN - …` stays TRUTHY in PowerShell. Census every consumer of `$record` after `:273` for a truthy test
or a path API (`Test-Path`/`Get-Item`/`Remove-Item` would throw on the `:` in the sentinel); fix only if one is
found.
✅ **RETROSPECTIVE-CYCLE40 IS IN AND FULLY DISPOSED** — `archive/peer/2026-09-19-retrospective-cycle40.md`
(ANSWERED, 239 s), **`VIOLATION: none`**: "this cycle was run well and was worth its cost … I found no structural
fault that changed what the cycle cost, produced, or whether it produced anything." Its findings were acted on in
the same cycle: the stale crash-copy pointer is deleted from NEXT (F2b/F6), Pre-decided 18 is amended (F2a), the
watchdog figure is corrected to 0 of **6** (F6), and the $4.48 run-8 review — archived undisposed when the audit
ran — now carries its full disposition (F4). `py tools/violations.py --due` therefore has nothing new to raise.

## §2 — the `🟢 DECIDED cycle 41` block

🟢 **DECIDED cycle 41, do not chase it:** `doc_lint` now reports ONE new L2 dangling — `STATUS.md:61` naming
`tools/recipes/build_d1_routeb_v7.py`, which run 10 has not cut yet (`doc_lint.py:182` exempts forward references
only in `*-plan.md`). **Leave it.** Naming the exact file the next cycle must cut is what NEXT is for, the reference
self-clears the moment run 10 cuts v7, and widening the exemption to STATUS would be building machinery to silence a
warning that is correct. ✅ Also cycle 41: gemini's Q2 `$record` census is CLOSED with **no defect and no change** —
every consumer in `tools/lv_stallcheck.ps1` after `:273` is either behind the same branch that sets the sentinel
(`:273`, `:285`, `:286`) or pure interpolation (`:291`); there is no truthiness test anywhere. The only effect is
cosmetic: `:291` can print `STALL RECORD written: NOT WRITTEN - …`. ✅ `doc_ingest --cycle 41` named three citation
contradictions and all three are FIXED (`CLAUDE.md:55` ASI envelope now points at this banner instead of restating
"~1 mm"; `CLAUDE.md:353` cites the 장치 order by DATE; `docs/cycle27-plan.md:84`'s stale "STATUS OPEN 54" pointer
dropped).
