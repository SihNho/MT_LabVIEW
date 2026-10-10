# Truth for case 3 (scorer only - never shown to a reviewer)

## What the next judgement decided (PD402, `docs/d1/ring-p5c.md:206-232`, cycle 165 hand-back round 2)

- **Cause, read from the code:** the Executor's base PRIME pass (`tools/stagexec.py:2620-2642`) address-proves AT BASE
  every plan end whose base row has a wire, through `Addr.triple`. t8776 / t24342 still hold the stubs w10362 / w25232 at
  base, so `_triple` raises at `:1934` ("INNER face of LoopTunnel ... only the outer face's owner route is measured")
  BEFORE the plan's own `delete_wire` rows run. In a real launch the same pass raises "PRIME ... stop before op 1".
  Card 165-1-1's self-test checked compile and the per-step route (where `loop_inner_face_sink` works on the post-delete
  read), not PRIME. So: the per-step route was fine; the base-time check ignores that the plan deletes the stub first.
- **Fix (stagexec only, narrow):** PRIME skips an end only when ALL hold: LoopTunnel InnerTerminal sink; its base wire uid
  is the `wire_uid` of a `delete_wire` op EARLIER in the plan than the action using the end; that op is a checkpoint.
  Logged (`PRIME-SKIP`). Everything else primed as before.
- **The test that decided it:** self-test on graph 2a5fa0c4: the step-5 plan finalizes in SB REALSIM with route PASS and
  0 UNROUTABLE; the real-backend PRIME does not raise for the two ends; negatives still refuse: (n1) same connect without
  the `delete_wire`; (n2) `delete_wire` of another wire; (n3) the `delete_wire` placed AFTER the connect; (n4) a wired
  SelectorTunnel / FS inner face. Stored plans compile and dry byte-equal.

## Which later card PASSED

- `165-3-1` PASS 6/0 (`stagexec.prime_deleted_face_skip`, stagexec 6ea6637f -> 1d5309f4, self-test
  `tools/bench/selftest_c165_prime.py`); `165-3-2` / `165-3-3` PASS (plan_ring_p5s02e final); `165-3-4` scratch PASS
  20/0 with `PRIME-SKIP end #8776 ... w10362 is deleted by checkpointed op 1` (`tools/bench/diag_c165_p5s02e_scratch.log:64`)
  and #24342 (:65); file adopted as P5 final 75773b0d (its later Error List 47 vs 49 mismatch is a separate issue).

## Not the cause

- The outer-face rewrite (route A70/A80 to the tunnels' outer faces) was rejected earlier (PD400(a), rule 1a).
- `loop_inner_face_sink` itself was not wrong; the per-step route of w_k3f / w_k4f was `connect_term_uid`.

## Scoring hints

- "cause named = yes": a base-time (pre-op-1) address check proves the inner-face end while the stub wire is still
  there, i.e. it runs before the plan's own stub `delete_wire`; it must be ordered/skipped for ends whose base wire the
  plan deletes earlier. "partial" = says "the face is still wired at base so _triple refuses" without locating the
  base/PRIME (pre-delete) ordering as the defect, or proposes a broader relaxation (any inner face).
- "test matches = yes": make the base check skip/defer such ends (or evaluate after the delete checkpoint) and re-run the
  SB REALSIM / PRIME on 2a5fa0c4 expecting route PASS, plus negatives (no delete_wire, delete after connect) still refusing.
