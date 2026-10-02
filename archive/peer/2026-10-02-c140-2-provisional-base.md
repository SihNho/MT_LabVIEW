# c140-2-provisional-base

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.1338  in 42 / out 18895 / cache-create 149541 / cache-read 2797222  (216s, 34 turn(s))
- **date:** 2026-10-02 20:22:47
- **outcome:** ANSWERED (220s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (card 140-2, failing log tools/bench/prep_c140_2_s01_r2.log, script tools/bench/prep_c140_2_s01.py, gate RB).

FACTS: The session-1 plan tools/bench/plan_ring_p4_s01.json is built from tools/bench/plan_ring_p4_v14.json, whose top-level "base"
is {path: tools/bench/graph_ring_p3b2b_20261002_133824.json, md5 50595c62..., provisional: true, sim_of: {plan: tools/bench/plan_ring_p3b2b.json,
md5 ae6b6111...}} (flag present in v10..v14 and plan_ring_p4s1.json). stage_prerun.check_launch (tools/stage_prerun.py:4033-4039) refuses
any launch of a plan whose base is provisional and prescribes --rebase. In r2 the maker called stage_prerun.rebase(plan, that same graph):
REFUSED "BINDING: the created objects differ (name-free shape): FlatSequenceOuterTunnel x0 simulated vs x2 real, GrowableFunction x0 vs x2,
Local x0 vs x2 (twice), SelectorTunnel x0 vs x2" (prep_c140_2_s01_r2.log, RB line).

CLAIM: the provisional flag is STALE. The graph file is a REAL read of the saved bed: its own header says vi = claudeDev\D1_ring_p3b2b_20261002_130007.vi,
md5 395118775a52bc90073f4449b99f899d (= the bed), source "tools/bench/diag_c136_1_graph.py (read_live ...)". rebase() compares the
provisional graph (here the same real file) against the real graph after binding P3b-2b's simulated creations (negative uids), which do not
exist in a real read, hence "x0 simulated vs x2 real". So rebase cannot clear this flag, and the correct fix is for the session-1 maker to
drop provisional/sim_of from the copied base ONLY after verifying mechanically: graph md5 field == bed md5, source contains read_live, and
zero negative uids in the graph's terminal rows (owner/term/wire/frame); base path and md5 unchanged. The plan is then simulated on that
same real graph (as it already was, stagesim.simulate(S1IN, GRAPH)).

Questions: is there any way the base graph is NOT the real bed state (e.g. a graph read of a DIFFERENT file, or a later bed)? Does dropping
the flag lose any check that rebase would have done for session 1 (P3b-2b's created objects already exist in the real read)? Cheapest
discriminating test?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: I could not refute the core claim.** The flag is stale, and the refusal follows mechanically from it. But the fix as written has a check that proves nothing, and dropping the flag changes three behaviours, not one. The concrete gaps are below.

## 1. Strongest reason the claim is wrong, or at least under-specified

**The proposed check "graph md5 field == bed md5" is circular.**
- The graph's `md5` field is not measured into the JSON. `tools/bench/diag_c136_1_graph.py:20` reads `BEDM` from the plan input, and `:77` writes it into the header as-is.
- `source` is a string written by the same script (`:77-78`).
- So both checks pass for any file this script wrote, whatever was actually read. They cannot tell "a real read of the bed" from "a file that says it is one".
- The real evidence sits in the run log, not the header:
  - `diag_c136_1_graph.log:8`: K1 (stops the run on failure) checked the input md5 = 39511877 before the read (stagekit.py:372-375).
  - `:300`: WROTE … md5 **50595c62**, which equals `base.md5`.
  - `:307` and `:315`: input unchanged after the run.
  - `:331`: rc=0.

The maker should check those four, plus the bed's md5 now (`md5(claudeDev\D1_ring_p3b2b_20261002_130007.vi)` == 39511877, which is STATUS `current-bed:` and INDEX.md:26). Header string checks should not stand in for them.

"Zero negative uids" holds: my grep found none in terminal rows, `uid` fields or owner pairs. But that only shows the file is not a simulator output. It does not show which VI it describes.

## 2. Alternative explanation of the same evidence

"x0 simulated vs x2 real" does **not** prove the graph is the bed. `rebind` (stage_prerun.py:3237-3252) sets `sim_new` = negative-uid nodes in the provisional graph and `real_new` = terminals absent from plan b's base (the a-file graph). **Any** real read gives x0 simulated, including a read of another file or a later bed. The refusal only proves the provisional file holds no simulated objects. Identity has to come from the log evidence in §1.

There is a second, smaller hole: the "real read" is a hybrid. `fs_tunnel_pairs` is an input copied from `graph_qrt_pool_20260928.json` (diag_c136_1_graph.py:38-39, 78-79), which predates P3a and P3b. So P3b-2b's two new Flat Sequence outer tunnels have no measured pair entries. This is not caused by the fix. The same reader built the a-file graph that P3b-2 b was accepted on, and rebase's `carry_fs` would have added nothing here (the "provisional" graph has no negative FS entries). It matters only if session 1's two routes marked "nested" (routes 15/16, r2 log :76-77) go through those tunnels.

## 3. Does dropping the flag lose a check rebase would have done?

No, for session 1:
- **sim_of check** (:3573): moot. PD297 already ties the bed to plan b ae6b6111 (ring-p3b.md:411-412).
- **Binding:** has nothing to bind.
- **Remap:** `plan_ring_p4_s01.json` has 0 negative uids (grep).
- **Positive-uid existence:** covered by the simulation on the real graph (S01 final True, route PASS, r2 log :78-79).
- **Re-simulation:** the plan was already simulated on that graph.
- **carry_fs:** does nothing here.

Precedent supports this. PD287(c) (ring-p3b.md:267-270) finalized session b **directly on a real read** instead of rebasing from a simulated end.

But the flag gates three code paths, so dropping it **changes** behaviour:
- **Launch gate** (`:4033`): intended.
- **Which graph the dry run uses** (`:517`, then `find_graph` `:214-239`): it picks the plan's own base only if the header md5 equals the input md5 **and** the file md5 equals the pin. That should be the same file. Verify it in the dry log.
- **X10 memory start** (`:1997`): returns None today and will look up the measured load for 39511877 after the drop. **The X10 verdict can move**, so the earlier dry run, pre-run and X10 records are void (the plan md5 changes anyway).

**Risk to session 2:** `plan_ring_p4_s02*.json` pins `sim_of` = `sim/ring_p4_v14_ops1_16/plan_ring_p4_v14_ops1_16_in.json` md5 c51931f5. If the fix rewrites that file, or v14 itself, session 2's later rebase is refused at `:3573`. The drop must be applied **only** to the session-1 file the maker writes, and session 2's genuine provisional flag must stay.

## 4. What would falsify the claim

Any one of these:
- The bed's md5 now ≠ 39511877.
- `md5(graph_ring_p3b2b_20261002_133824.json)` ≠ the WROTE line at `diag_c136_1_graph.log:300`.
- A positive-control rebind (§5 step 2) failing to bind plan b's simulated creations onto this graph.

## 5. Cheapest test that separates the two (offline, seconds)

1. Hash two files: the bed (expect 39511877) and the graph file (expect 50595c62, same as log :300). Then grep the log's K1/H2 PASS lines.
2. **Positive control:** call `stage_prerun.rebind(before=<a-file graph 123012 rows>, prov=<stagesim end graph of plan b ae6b6111>, real=<133824 rows>)`. Expect every created object bound (outer tunnel ×2, GrowableFunction ×2, Local ×2 ×2, SelectorTunnel ×2).
   - PASS ⇒ 133824 is exactly the result of plan b on the a-file, i.e. the post-P3b-2b bed, so the flag is stale.
   - Shape mismatch ⇒ stop. The graph is not that state, or the simulator diverged.
3. After the drop, re-run the dry run and the pre-run. Confirm the dry log names `graph_ring_p3b2b_20261002_133824.json`, and record the new X10 start and peak.

What would change my mind: step 2 failing, or a session-1 route touching a P3b-2b Flat Sequence tunnel whose border shows UNMEASURED in this graph's `fs_measured.borders`.

No web search was needed. Every claim here is about this project's own code and logs, cited by file:line.

## Sources

(extract from answer)

## What was done with it

Disposed by the cycle-140 judgement session. ACCEPTED: the provisional flag on v14 was stale; session plans drop it with gate PV
(140-2's maker), and v15 was written without it (PD321(d), `docs/d1/ring-p4.md:390`). The risk to session 2 is moot: 140-P1's s02 plan
is superseded, because v16 puts the bed repair first and session 2 is re-cut and rebased on session 1's real graph (PD322(b)).
