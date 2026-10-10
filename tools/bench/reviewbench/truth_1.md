# Truth for case 1 (scorer only - never shown to a reviewer)

## What the next judgement decided (PD398, `docs/d1/ring-p5c.md:73-103`, cycle 164 hand-back round 1)

- **Cause (accepted as fact):** with `frame: "True"` on BOTH ends, `w_k3pass` is neither a group wire
  (`tools/stagexec.py:896-897`: a group wire has no frame on either end) nor a case pass wire (`case_pass_wire` refuses a
  `src` frame, `tools/stagexec.py:6286-6288`), so the in-tunnel IK3 has no out-wire and compile stops
  (`tools/stagexec.py:901`). PD397(b) copied the shape of the adopted G/H/C7 pass wires (A33/A40/A52), but those are
  STANDALONE frame wires placed AFTER two complete tunnel groups; in K3/K4 the pass wire IS the in-tunnel's one out-wire.
  So the root error was the plan decision PD397(b) (wrong analogy), not a tool defect.
- **Decision:** in `plan_ring_p5s02r_in.json`, A69 `w_k3pass` and A79 `w_k4pass` DROP the `frame` key on `src` and KEEP
  `"frame": "True"` on `dst` - the shape card 156-a1-2 designed for exactly these rows
  (`tools/bench/selftest_c156_passwire.py:6-10`). Same wire, same faces, no computation change. No tool edit; no third
  shape; if compile refuses the dst-only shape, hand back. JSON compare: exactly 2 removed keys.
- **The test that decided it:** re-make the plan with the dst-only shape and compile it on the real p5s02c graph:
  compile ACCEPTS it, K3/K4 build as `connect_term_uid` `register_end_case_border` groups with `case_pass_wire` True
  (`tools/bench/diag_c164_a2_1_facts.md:14-17`; `tools/bench/prep_c164_a2_2_mk.log:34,134-135`).

## Which later card PASSED

- `164-a2-2` PASS: `plan_ring_p5s02d.json` 872822f3 = J+K3 (A53..A69), 17 rows, final True, route PASS, 0 UNROUTABLE.
- Step 4 adopted after round 3 (`tools/bench/cards/assign_result_164_3.json` PURPOSE_MET 17/17; `164-3-5` scratch 21/0).

## Not the cause / side issues

- The `STUB` non-fatal FAIL (K3f/K4f dst faces t8776/t24342 hold stub wires w10362/w25232) is a separate, later problem
  (handled in PD400/PD402); it is not why K3 failed to compile.
- A tool change to make compile accept frame-on-both-ends was NOT the chosen route (the judgement forbade a tool edit).

## Scoring hints

- "cause named = yes" needs: the both-ends frame shape makes the pass wire unusable as IK3's out-wire (group-wire rule +
  case_pass_wire src-frame refusal), i.e. the plan shape (PD397(b)) is wrong. "partial" = names the tool refusal only,
  or proposes to edit the tool as the primary fix.
- "test matches = yes" needs: change A69/A79 to dst-only frame (frameless src) and re-compile / check case_pass_wire True.
