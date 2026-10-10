# Truth for case 2 (scorer only - never shown to a reviewer)

## What the next judgement decided (PD399, `docs/d1/ring-p5c.md:105-138`, cycle 164 hand-back round 2)

- **Prior-art review accepted as RIGHT on both counts:** J deletes #23042 / #23501 with w23460 and w23519 still attached,
  which is not the settled P4 form (PD321(b)/PD323(a)); and "`delete_object` has no passing launch yet" was false.
- **But the correct application differs from the reviewer's literal suggestion** (measured, `diag_c164_a2_4_facts.md`
  §Wires): w23460 runs from #23501's inner face t23505 to #23042 only, so it is removed by `delete_wire` BEFORE the
  deletes. w23519 has 4 sinks and only t23514 is on #23501, so it must NOT be deleted (that would cut the live sinks on
  #23417, #23172, #7201); after `delete_object #23501` it gets `wire_remove_loose_ends` (keeps 3 sinks, so the P4 whole-wire
  1055 hazard cannot occur). New J order: A53 `delete_wire` w23489, NEW `delete_wire` w23460, A54 `delete_object` #23042,
  A55 `delete_object` #23501, NEW `wire_remove_loose_ends` w23519, A56..A60 unchanged.
- **The discriminating test the judgement adopted:** gates from graph 3d5196ab before use (w23460 endpoints are a subset
  of #23042 and #23501 terminals; w23519 keeps >= 1 sink outside both nodes), and the stagesim end graph must show w23460
  gone and w23519 with sinks exactly {t23450, t23241, t7606}. Any other result = hand back.
- **K3f/K4f (the other failing card, UNROUTABLE inner faces #8776/#24342):** step 4 = J + K3 only (the prefix stops
  before K3f because no tool route reaches an inner LoopTunnel face, `stagexec.py:1930`); K3f/K4/K4f become step 5;
  first an OFFLINE facts card measures the K3f/K4f design, what sits on t8776/t24342 (stubs w10362/w25232), and whether
  any adopted stage ever wired an inner tunnel face. An outer-face rewrite is a rule-1a question, NOT assumed equivalent.
  make_step_plan lacking a routability check (`prep_plan_flow_lib.py:171`) is carried as a tool fix, not done.

## Which later card PASSED

- `164-3-6` PASS (plan 97837e2a final True, 15 ops), `164-3-5` scratch PASS 21/0 (peak 652.6 <= 675), `164-3-2` PASS
  (K3f/K4f facts), `164-3-7` PASS; step 4 adopted (`assign_result_164_3.json` PURPOSE_MET 17/17). PD400 records the real
  graph 2a5fa0c4: w23460 absent, w23519 sinks {t23450, t23241, t7606} == the stagesim prediction.

## Scoring hints

- "cause named = yes": J's deletes leave attached wires (w23460 must be deleted first; w23519 is a shared multi-sink
  wire that must survive, cleaned by RLE) AND/OR K3f/K4f inner-face unroutable => split the prefix at J+K3.
  Naming only "follow the prior art: delete_wire 23519 and 23460" is at best partial: deleting w23519 would cut 3 live
  sinks - count it as a WRONG factual/actionable claim if asserted as the fix.
- "test matches = yes": list w23460 / w23519 sinks on graph 3d5196ab and check the stagesim end graph (w23460 gone,
  w23519 sinks = the 3 outside sinks). "partial" = only one of the two.
