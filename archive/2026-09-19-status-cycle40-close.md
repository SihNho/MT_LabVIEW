---
type: archive
status: archived
date: 2026-09-19
cycle: 40
tags: [status, relocation, open-items]
---

# Relocated from STATUS.md at the close of cycle 40

Rule 4: nothing here is rewritten, only moved. STATUS had reached 160 lines; these blocks are narrative and
carried explanation, not "what to do next". STATUS keeps a one-line pointer to each.

## §1 — the "DONE IN EARLIER CYCLES" pointer block (verbatim)

✅ **DONE IN EARLIER CYCLES — do NOT redo; pointers only.** Cycle-35 dispatches 1+2 (`Count` = CONTROL uid 28051,
never a bead count) → `archive/2026-09-18-status-cycle37-run5.md` §1 · run 4, its review and judgement's four
answers → §2, run 4's own measurements → `archive/2026-09-18-status-cycle36-d1-run4.md` §4 · STEP 0 machinery
repairs 5/0 (⚠️ (e) NOT closed: external kills reach no in-process handler) → §3 · STEP 1's baseline `ExecState`
read, fired at `…run4.log:25` · retrospective-cycle36, both violations `DECISION: no-device` → §4.

## §2 — OPEN 38/39/41, the route-B flag and NO-ROUTE history (verbatim)

38/39/41. 🟡 **DECIDED cycle 35 — the flags are no longer an open question: both stay False PERMANENTLY** (Pre-decided 13), and the 3 NO-ROUTE rows follow `docs/cycle15-plan.md` Pre-decided 1/2/3. Run 3 was 63 WIRED / 0 FAILED / 3 NO-ROUTE at ExecState 0, but that ExecState was read **cold and therefore measures subVI linkage** (Pre-decided 14a/16, two independent controls); it was equally **over-determined** by the skipped `s1q`/S4b, so run 3 is neither exonerated nor convicted until the baseline read lands — **`docs/d1-route-b-plan.md` §11/§11a**, archive §3 · `VI.Get Errors` 452 NOT built (prior-art stopped it, `docs/d1-build-plan.md:859-860`; §10 NOT AUTHORISED) · **judgement only — the stall watchdog's liveness test**, both arms ANSWERED and REFUSING "false positive", remedy not built (`archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`).

⚠️ Superseded in part by cycle 36/37's Pre-decided 13a (`TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only) and
by cycle 40's Pre-decided 19 (`Z/dZ` IS wired; the gate was inverted). The stall-watchdog line is CLOSED by cycle
40's repair (`tools/lv_stallcheck.ps1:273`, self-test 8/0).

## §3 — OPEN 54, the `retro_done` trap and the orphaned-background-job rule (verbatim)

54. 🔴 **`retro_done` is armed by an INTENTION, not by an answer** — `guard_bash.py:226-227` marks the session closed the instant a `retrospective.py` command is typed, while the gate it mirrors, `guard_cycle.newest_retrospective()`, requires an **ANSWERED** archive; nothing ever clears the mark (`{"dispatches":0,"retro_done":true}` in **3 of 17** session files). **Repair NAMED, deliberately NOT BUILT**: `guard_session` should read `guard_cycle`'s own predicate. ⚠️ The "over-trigger / gate deadlock" reading was REFUTED — `retrospective.py:299` "END IS ALWAYS NOW"; **the retrospective is the LAST thing a session runs**, and a measurement dispatch never waits on one. 🆕 THE SAME TRAP WITH A DIFFERENT MOUTH — **a `claude -p` session CANNOT "take results as they arrive"**: cycle 33 ended its turn on two backgrounded hypothesis peers, both paid opus/max cells were killed at 600 s with no `COST:` line, cycle 33 closed with no retrospective, and cycle 34 spent $5.88 re-asking. **THE RULE: dispatch in the FOREGROUND and wait — and when something must run in the background, HOLD THE TURN OPEN until it lands.** An orphan detector is deliberately NOT built (Pre-decided 2). VERBATIM → `archive/2026-09-18-status-cycle36-relocate.md` §10; reviews `archive/peer/2026-09-18-retro-closes-session.md` + `archive/peer/2026-09-18-retrospective-cycle34.md`.

## §4 — OPEN 42/43/46/47 (verbatim)

42/43/46/47. **VERBATIM in `archive/2026-09-18-status-cycle20-open-items.md`** — 42 ⚠️ 39 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed · 43 ✅ `guard_cycle.fixed_claim()` FIXED (step 1, T1–T6 + B1/B2) · 46 ⚠️ `SetCommand_signed.vi` is on NO disk · **47 🔴 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry; opus reads `device-failed`, threshold 1.** · 48/48a/49/50 ✅ ALL FOUR CLOSED, verbatim in `archive/2026-09-18-status-cycle22-close.md` §3.

## §5 — cycle 40's own record

One cycle, four dispatches, 65 minutes, `VIOLATION: none`.

- **Run 8** — `tools/bench/build_d1_routeb_v5_run8.log`, launched 03:58:14, `BGRUN END rc=1 after 1822s`,
  80 PASS / 0 FAIL gates. Ledger `:363` 66 attempted / 53 WIRED / 12 FAILED / 1 NO-ROUTE. Every recorded
  prediction missed. Original md5 `2a78e17c449cacdaf5da389818526859` unchanged, `:13` and `:440`.
- **`archive/peer/2026-09-19-routeb-run8-predictions.md`** — the mandatory failed-prediction review
  (claude/hypothesis, opus/max, ANSWERED, $4.4847, 678 s). Fully disposed in its own
  `## What was done with it`; produced Pre-decided 19 and the Pre-decided 18 amendment.
- **`archive/peer/2026-09-19-stall-selftest-c39-g78b.md`** — gemini, ANSWERED, discharging the `guard_peer`
  record left by the watchdog self-test's first run. Its Q1 was refuted by the 8/0 re-run; its Q2 (the
  `$record` sentinel stays truthy in PowerShell) is the one open thread, carried in STATUS NEXT.
- **`archive/peer/2026-09-19-retrospective-cycle40.md`** — ANSWERED, 239 s, `VIOLATION: none`, fully disposed.
- **`archive/prose/2026-09-19-for-user-c40.md`** — the `FOR THE USER` items 4a and 5, written by the prose role
  (fable/low, thin) from a fact list, per CLAUDE.md §3.
