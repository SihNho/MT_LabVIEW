---
type: archive
status: archived
date: 2026-09-19
tags: [status-narrative, cycle38, d1-route-b, run6]
---

# Cycle-38 STATUS narrative, relocated verbatim (rule 4)

## §1 — the lock-block `status:` prose written by cycle-38 dispatches 1-3, BEFORE run 6 launched

Relocated verbatim from `STATUS.md` on 2026-09-19 by the cycle-38 dispatch-4 MATERIAL session, after run 6
actually launched and ran (so the "NEVER LAUNCHED" line below is superseded as a state, but is kept as the
record of what the two gates did and why).

> 🔴 **RUN 6 NEVER LAUNCHED — `tools/stop_record.py` (the prior-art LAUNCH GATE) REFUSED it, 2026-09-19 cycle-38 MATERIAL: the run-5 review `archive/peer/2026-09-18-priorart-d1-routeb-run5.md` is `released for sha 76e1252e3de3`, and the cycle-38 P1/P2/P3/P4 patches moved `build_d1_routeb_v2.py` to sha `5620e626a95d`. `stop_record._released():318-331` compares the ALREADY-STAMPED release sha to the file on disk, so adding a seventh `FIXED:` line to that review cannot release it — only a NEW prior-art record over the edited bytes can (`:214-231`), and disposing its verdict is judgement's call. LabVIEW was never opened; nothing acquired the lock. Previous: **D1 ROUTE-B v2 RUN 5 RAN, cycle-37 MATERIAL, 2026-09-18 23:50 → 2026-09-19 00:18** — `tools/bench/build_d1_routeb_v2_run5.log`, `BGRUN END rc=1 after 1668s`, **80 PASS / 1 FAIL** (`:165`, the same `S3-zdz` row as run 4) then the SAME `error 2` crash at `:406`. ✅ **S3w LEDGER SURVIVED** (`:338`): attempted 66, WIRED 57, FAILED 6, NO-ROUTE 3 — the 6 FAILED are all `report_all(Diagram) error 2` (`:396-401`). ✅ **`Z/dZ` reached the temp sink WELL-FORMED** (`Equal? #10104`, census `{0:('x = y?',True,0),1:('y',False,0),2:('x',False,0)}`, `:332`) and died one step later at **error 5001 `Get Controls.vi`** (`:402`) — cause MEASURED, written up with the candidate fix in `docs/d1-route-b-plan.md` §11a. ✅ S1 baseline `ExecState` 0 COLD ⇒ UNREAD (`:26`); the LIVE copy read **1 PRELOADED** (`:411`). ✅ Original md5 `2a78e17c449cacdaf5da389818526859` UNCHANGED (`:4`, `:414`). ⚠️ The crash copy was RENAMED ASIDE, not deleted: `…\claudeDev\SCRATCH_routeb_235020_crash_001808.vi` (`:413`) — delete it in the next run's S0. 🔴 **THE HANDLE COMPARISON IS WITHDRAWN AS UNMEASURED — it is NOT a refutation.** `tools/bench/bench_prep.py:64-71` reads the KERNEL handle count, which cannot see VI Server refnums, GDI or USER objects, and run 4's 51,284 and run 5's 38,824 were read from **two different LabVIEW processes**; the comparison never measured what it claimed. **The `error 2` cause is OPEN.** The leading unexcluded mechanism, named by `archive/peer/2026-09-19-zdz-wirecontrol-5001.md`, is **refnum-class exhaustion from unclosed `Traverse for GObjects` arrays** — sticky and monotonic, which fits `…run5.log:396-401` then `:406`. LabVIEW is now pid 7412, up 00:17, 34,143 handles. ⚠️ A THIRD stall record of the known class fired ON THE BUILD CLIENT during the run, `tools/bench/stall_pid3792_235020.log:1`. Cycle-37 and run-4 lock prose VERBATIM → `archive/2026-09-18-status-cycle37-run5.md` §6-§10 · `archive/2026-09-18-status-cycle36-d1-run4.md` §6.

## §2 — how the two launch gates were actually released, 2026-09-19 dispatch 4

1. `tools/stop_record.py`: released already by dispatch 3 — the NEW prior-art record armed over the corrected
   bytes was stamped for `tools/recipes/build_d1_routeb_v3.py` sha `ec1e9aca72f4`, measured ALLOW True.
2. `tools/hooks/guard_cycle.py` `premature-build`: released by a FIFTH `FIXED:` line written under
   `## What was done with it` in `archive/peer/2026-09-19-priorart-d1-routeb-run6.md`, citing
   `tools/recipes/build_d1_routeb_v3.py:415` — v3 is the byte-copy carrying this review's four disposed
   findings and exists because of them. No gate, hook or record store was edited; `CYCLE_GUARD_OFF` was
   never set. The launch then ran with no hook refusal.
3. Recorded in the same review file, NOT as a release line: the crash copy
   `SCRATCH_routeb_235020_crash_001808.vi` measures md5 `2a78e17c449cacdaf5da389818526859`, 473,317 B,
   mtime 2026-09-01 12:07:59 — byte-identical to the ORIGINAL, so it carries none of run 5's 57 wires and
   F1's "fixture for the run-5 discriminators" claim is refuted by measurement; F1's rule (never destroy
   unmeasured evidence with a blanket glob) stands and is applied.
