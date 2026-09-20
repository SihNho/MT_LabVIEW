---
type: archive
status: archived
date: 2026-09-19
cycle: 41
tags: [status, for-the-user, relocated]
---

# `STATUS.md` → `### FOR THE USER` items 1, 4, 4a and 5 — relocated VERBATIM

Relocated by the cycle-41 judgement session on 2026-09-19, under CLAUDE.md rule 4 (narrative is never rewritten,
only moved down a layer) and in answer to retrospective-cycle41's **L3** finding — that `STATUS.md` had grown to
178 lines and that the previous session's defence, "line-count is the wrong meter for it", was *a rationale for
breaking rule 4 rather than a repair of it*. That is accepted. The four items below are moved out **word for word**;
nothing is edited, shortened or re-phrased. Each carries a short outcome note added here, not in the original text.

`STATUS.md` keeps the items that are still live calls on the user: **1a** and **1b** (both are preconditions on D1
acceptance), **2** (`wait_logs.py`), **3** (cycle 34) and **6** (cycle 41).

---

## Item 1 — the `TEMP_SINK_AUTHORISED` flag call ✅ RESOLVED, and it paid off

> 1. 🔄 **I REVERSED HALF OF MY OWN "off permanently" CALL, on measurement.** Cycle 35 said both route-B flags stay False for good. Run 4 confirmed the shift-register half exactly as decided, so `SR_QUEUE_AUTHORISED` stays off for good. But the `Z/dZ` half rested on a "reorder the wire" plan that the machine has now refuted twice — it has no by-index route, and it was aimed at the wrong cut. So `TEMP_SINK_AUTHORISED` goes **True for that one row, as a test**. It builds nothing new: the path is already written and uses only ops we built weeks ago. Say so if you would rather `Z/dZ` stayed unwired than see that flag on.

**Outcome (run 9, 2026-09-19).** The test succeeded and the question is closed. `Z/dZ` t0 passes its gate at
`_wddelta == 1`, with source identity True, `Is Broken? False` and the sink reading back w29238
(`tools/bench/build_d1_routeb_v6_run9.log:360`, `:464`); `docs/cycle27-plan.md` Pre-decided 19 is now
machine-confirmed rather than decided from a code read. `SR_QUEUE_AUTHORISED` remains False for good, as decided.

## Item 4 — the three cycle-39 calls ✅ ALL THREE CONFIRMED by later runs

> 4. 🆕 **Cycle 39 — `Z/dZ` is WIRED and the wire is now MEASURED, not argued.** Your flag call in item 1 paid off:
> the source control's own wire 29238 IS the sink wire, exactly one reciprocal source terminal, `Is Broken? False`.
> Three calls of mine this cycle you may want to overturn: (a) I **retired a gate** that had failed three runs in a
> row — it demanded `Z/dZ` be wired BEFORE the `#403` reparent, which is the route your own Pre-decided 13a
> replaced, so it was asserting a plan we no longer follow; (b) I **deleted the VI-wide remove-broken-wires call
> from inside the wiring loop** and put nothing back, because run 5 accidentally proved the point (it never reached
> that call and everything wired), and because a reaper that deletes 96 wires mid-build is deleting wires the
> original has — the opposite of the "don't change the computation" rule; (c) when a peer told us to use `net_map`
> for a safer per-diagram count, I **refused its own advice** on measurement — `net_map` calls that same reaper
> internally, so following it would have fired the thing we were removing, twice per row. And one I deliberately did
> NOT do: `logclass` miscounts waiter logs as builds, which is what blocked run 8, and I left it alone rather than
> build past your "no more 장치" order. Say if you would rather that one were just fixed.

**Outcome.** (a) and (c) stand unchallenged. (b) is now **confirmed by replication, 2 × 2**: the two runs with the
in-loop reaper (6 and 7) lost `#2222`'s terminals; the two without it — run 8 (`…v5_run8.log:411-413`) and run 9
(`…v6_run9.log:464-468`) — wired every one. `docs/cycle27-plan.md` Pre-decided 17 records this, and the scratch-copy
K1 separator that had been queued to settle it was **retired without running**, since it would only confirm what two
builds already replicate. The `logclass` item stays deliberately unfixed under the user's 2026-09-18 08:53 order and
is carried in `STATUS.md`'s "Still owed" block.

## Item 4a — the one-line watchdog repair ✅ DONE AND PROVEN

> 4a. You told me to stop building 장치. While you were away I approved a one-line change to the existing watchdog script — the one that is supposed to notice when LabVIEW has frozen. It has fired six times and been wrong all six times; the latest false alarm was 2026-09-19 04:16, on a job that finished normally at 04:28. Each false alarm blocks the next build until a paid peer review clears it, which has cost $6.16 so far. The change makes the script write its blocking record only when it actually finds a stuck dialog box, and its self-test now passes 8 of 8. I read your order as "stop building NEW machinery", not "leave a broken one breaking things", and I scheduled the fix after the main build launched, never before it. If I read your order wrong, this is the call to overturn.

**Outcome (cycle 41).** The follow-up question gemini raised against that repair — whether the sentinel string
`NOT WRITTEN - …` stays truthy in PowerShell and so fools a later test — was censused and **closed with no defect
and no change**: every consumer of `$record` after `tools/lv_stallcheck.ps1:273` is either behind the same branch
that sets the sentinel or is pure string interpolation, and no truthiness test exists anywhere. The only residue is
cosmetic: `:291` can print `STALL RECORD written: NOT WRITTEN - …`.

## Item 5 — the cycle-40 report ✅ SUPERSEDED by item 6 (cycle 41)

> 5. The main build (run 8) ran 30 minutes and every prediction written down beforehand was wrong. I first called that good news because the four rows the predictions named all improved, but a paid review ($4.48) showed the run went backwards overall — 54 wired rows became 53, and 9 failed rows became 12. I had judged the run by only the rows the predictions happened to name; that mistake is now written into the status file. The genuinely useful result: the test that had failed the "Z/dZ" connection four runs in a row was itself wrong — it demanded the wire count come back unchanged after a temporary helper part is deleted, but the whole purpose of that step is to leave exactly one new wire behind. I did not take the reviewer's word for it; I confirmed in our own code that the connection is made — it checks out by identity, is not broken, and reads back as the same wire. Second: the one measurement the run existed to produce could not be read, because the command that lists every wire hits the same LabVIEW memory error that crashes the run; the next run will read the individual connection points instead, which is cheaper and tells us more. The old "too many open handles" explanation for that error is dead — runs were healthy at 51,349 handles and crashed at 35,555. Four saved "crash copies" turned out byte-for-byte identical to the untouched original and were cleared out. The cycle's own review found no violations: "this cycle was run well and was worth its cost." Nothing blocks the next step. One other call you may want to overturn: to clear a gate blocked by a trivial typo in a test, I spent a cheap Gemini review instead of a $4.50 Opus one.

**Outcome.** Its plan for the next run was carried out and its prediction about the census was **half right**: reading
the individual connection points is indeed cheaper, but it did not work either — the same `error 2` killed all five
diagram listings in run 9, so the measurement is still unread. That is what makes `error 2` itself the target of
run 10 (`docs/cycle27-plan.md` Pre-decided 20). The still-open Gemini-versus-Opus review-cost call is carried by
item 6's successor discussion, not by this item.
