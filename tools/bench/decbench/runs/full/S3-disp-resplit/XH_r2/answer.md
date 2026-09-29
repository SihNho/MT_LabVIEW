**No. The goal is right but the order is wrong: NEXT schedules again the detour that cycle 101's retrospective named as its most costly fault.**

**What should stay**
- The display loop is the user's own direction (`docs/d1-loop12-17-split-plan.md:1568-1575`), and it was judged GO (`:1667-1676`).
- The open question D-2026-09-27-01 recommends "yes" (`tools/bench/decisions_pending.json:164-170`). Go ahead on that assumption and flag it (rule 2c).
- Report one mismatch: `next.json:7` says `blocked_by: null`, but that open decision says it "blocks M8" (`decisions_pending.json:171-173`).
- The final act stays: one record-mode run of `stage_d1_disp.py` that produces `D1_s1_disp_<ts>.vi`.

**What is wrong with NEXT**
1. **Step 1 (measure the 214(b) half-wire rule first, `STATUS.md:58`) is not needed before the run.**
   - 214(c) already turns sourceless half-wire differences into WARN (`plan:1794-1797`).
   - Record mode logs each real difference and keeps going (`plan:1787`), so the run itself measures what happens to the half-wires on every move.
   - The retrospective's counterfactual is exactly this: the op-26 fix plus one record-mode run under the existing rule and 214(c) would have reached ops 26-47 about 13 minutes sooner (`archive/peer/2026-09-27-retrospective-cycle101.md:279,289`). NEXT schedules that detour again, and may add a LabVIEW move on a scratch copy.
2. **"Replay r5 k1–k25" cannot work as a gate.**
   - Only k0, 2–5, 12, 24 and 25 were real reads (`2026-09-27-c101-5-onlysource.md:103-104`; `stage_d1_disp_r5.log:133-228` "diff skipped").
   - r5's only real difference was the sourceless 11365 at k12 (`r5.log:249`), and 214(c) already covers it.
3. **It leaves out the thing that actually ends runs: verb crashes.**
   - r5 died inside op 26 on a script function that had never run in LabVIEW (`r5.log:456`). The dry run fakes `create`, and later ops use more functions that have never run (`retrospective:256`).
   - The op-26 fix has only been checked by a self-test (`retrospective:264`).
   - A crash is not a record-mode difference: it ends the run.

**What cycle 102 should do instead (one stage card, in this order)**
- (a) **Fix the tunnel-flip seed bug.** It is needed: in the simulation it cuts a real data edge, 11369→11270 (`onlysource.md:108`). That is not a sourceless difference, so it would still stop the save under 214(c).
- (b) **Settle `plan_disp.json`:** 7c432e1b vs b535071e (`plan:1800`).
- (c) **Check function coverage offline:** every function the 47 steps use must have a real run in some log. Each one that has never run, including `create_local_read` with its fix, gets run once on a dated scratch copy of S1, with a flat handle count.
- (d) **Add the 214(c) WARN rule,** then the dry run, the pre-run, and one record-mode run.
- (e) **Use the run's records to settle 214(b).** Model the half-wire rule only if a later step refers to one of those uids.

VERDICT: change NEXT
NEXT ACT: Fix the tunnel-flip seed bug, settle `plan_disp.json`, run every never-yet-run function in the 47 steps once on a scratch copy of S1, add the 214(c) WARN rule, then dry run, pre-run and one record-mode `stage_d1_disp.py` run that produces `D1_s1_disp_<ts>.vi`, reading the half-wire rule from that run's records instead of measuring it first.