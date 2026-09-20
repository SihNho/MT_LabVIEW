---
type: archive
status: history
date: 2026-09-17
tags: [status, relocated, cycle15, d1, route-b]
---

# STATUS.md narrative relocated 2026-09-17 (material/cycle15-d1-route-B-1), VERBATIM

Rule 4: STATUS.md reached 134 lines. Nothing is rewritten here - the text below is exactly what stood in
`STATUS.md`, moved so the live file stays under one screen. One line plus a pointer was left in its place.

## 1. LabVIEW lock history - the sessions BEFORE 2026-09-17 14:2x

```yaml
# 2026-09-17 13:5x-14:2x material/cycle15-d1-route-A-run-9: RELEASED. **§11r's reader was NOT BUILT — 0 of its
# 2-build budget spent** — its prior-art review (5 findings, 0 novel, all accepted) showed it is a COMPOSITION of
# `gscript.tunnels()` + `OpWireSource_v5` + an OFFLINE join. Runs: `d1_tunnel_chain.py` (no LabVIEW, 2/18) ·
# `diag_tunnelsource_onehop.log` 7/2, 111 s · `build_d1_v0_run9.log` **55/8, 203 s** (WIRED 35→**42**, FAILED
# 7→6, NO-ROUTE 24→**18**; v1 made 8 wires, **5 survived RBW**, 3 deleted). ExecState 0, NOTHING SAVED, working
# copy deleted in the run. Original md5 2a78e17c449c... before AND after EVERY run; LabVIEW restarted once
# (handles 30,384 → 33,848); no GUI, no hardware, no scratch left behind. Peers: priorart-tunnelsource-onehop
# (ANSWERED, disposed) · flatseq-tunnel-source-addressing r1 TIMEOUT / r2 agy ERROR / **r3 ANSWERED, disposed**.
# 2026-09-17 13:1x-13:4x material/cycle15-d1-route-A-last: RELEASED. LabVIEW restarted TWICE (bench_prep, 31,3xx
# -> ~34,000 each). ✅ `OpConnectNested_v1.vi` BUILT + SAVED (14,666 B, ExecState 1 warm AND cold) — the
# CROSS-DIAGRAM wire creator §11n called unbuildable. Runs: diag 10/0 · build run 1 rc=1 (Python TypeError in the
# recipe's own hook, no LabVIEW fact) · build run 2 31/1 · cold test 7/0. 3 scratches, ALL created and deleted in
# the same run, `claudeDev\SCRATCH*` verified empty. ORIGINAL never opened; md5 2a78e17c449cacdaf5da389818526859
# before AND after every run. Donor `OpConnectNested_v0` + NI example md5 unchanged. No GUI, no hardware.
# build_d1_v0 NOT run — §11p item 2 is blocked by its own prior-art review (see NEXT). Handles 31,270 -> 31,673.
# Earlier sessions, all RELEASED, originals md5 2a78e17c449... before AND after, no leftovers, no GUI, no hardware:
# open35-run-poison-fix (11/0) · d1-full-build-5 (OpConnectNested_v0 BUILT+SAVED, 14,234 B) · build-4
# (OpCreateConstOnTerm_v0 22/0, run 7 55/7) · build-3 (run 6 56/1) · phase-full-2 · run 5 53/0. -> archive/
# 2026-09-17-status-d1-full-build-{4,5}.md (the two newest relocated VERBATIM at the END of -5).
```

## 2. OPEN items 33 / 34 / 35 - closed, and their one-line pointer block

33 · 34 · 35 — ✅ CLOSED, **relocated VERBATIM to `archive/2026-09-17-status-d1-route-a-run9.md`**, one line each:
   `OpConnectNested_v1` BUILT + SAVED (14,666 B, warm AND cold) and now MEASURED in the real VI (run 9: 8 wires,
   **5 survive RBW**) · the acceptance gate is "the wire survives `remove_bad_wires_scripted`", not uid equality ·
   gscript's COM **poison flag** fixed + measured 11/0 (`test_run_poison.log`).

## 3. What the route-B-1 session added, in one place

* `OpConnectFromWire_v0.vi` BUILT + SAVED, 16,524 B, ExecState 1 (`tools/recipes/build_opconnectfromwire_v0.py`).
* `docs/d1-build-plan.md` gained **§11u** (the RBW gate is unsound; the `from-ctl` rows are two faults).
* `docs/d1-route-b-plan.md` revised: §1 ledger 63/82 routed, §4 mechanism table, §6 R1 disposition, §6 R2
  replaced, §7 S3w.
* Five peer exchanges, all ANSWERED and all dispositioned, plus the 2026-09-01 `opwireref-donor-plan-attack`
  disposition filled in after sixteen days.

## 4. OPEN 28f / 31 / 32 - relocated again 2026-09-17 (rule 4), VERBATIM

28f · 31 · 32 · 34 — **relocated VERBATIM to `archive/2026-09-17-status-open-28f-35.md`**, one line each:
28f. 🔴 run 7, PHASE "full" stage 1: 66 routable rows → **35 WIRED, 7 FAILED (5001), 24 NO-ROUTE** (17 `from-tunnel`),
   ExecState **0**, nothing saved ⇒ **N1/F1/F2 still NOT RUN** (they need a saved ExecState 1).
31. 🔴 retrospective still reviews the WRONG window (`retrospective.py:282-286`) — reproduced a THIRD time today,
   and the cause is now named: `guard_cycle.stamp()` = `min(ctime, mtime)`, so RE-ARCHIVING an existing slug
   keeps the OLD ctime and the gate never sees the new review. No cycle-16 plan document yet.
32. 🔴🔴 outcome review 2026-09-17: **six `OUTCOME-VIOLATION`s, SECOND consecutive time** ⇒ the work stops for a
   re-plan with the USER. Not answerable by a device. Zero new user-runnable deliverables.

## 5. OPEN 16 / 19-30 pointer block - relocated 2026-09-17 (rule 4), VERBATIM

16 · 19/25/26 · 20–23 · 27 · 28 · 28b · 28c/d/e · 29 · 30/30b/30c — ✅ CLOSED, relocated VERBATIM to
   `archive/2026-09-17-status-d1-full-build-5.md`: GPU kernel accepted for now · PLAN = REV 4 + §11c–§11h,
   transport = queues only · relocation MEASURED (`WhileLoop 3→6`, `Diagram 170→173`, 23 moves, 8 SRs, panel 114;
   **109 terminals / 24 uids**, source map **109/109**) · `OpCreateConstOnTerm_v0` 22/0 · `diag_d1_full_route`
   retired — ✅ **28c CLOSED 2026-09-17: the 1055 was the CALLER** (`diag_d1_full_route.py:265-273` never set the
   UID-addressed op's `UID 2`); `OpWireSource_v5` reproduced its published control first try · `OpStopFromNode_v0`
   T5 closed (0 → 387, ExecState 1) · §11h: the TIFF writer is not original, F1 uncapped.
