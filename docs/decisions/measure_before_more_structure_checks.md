---
name: measure_before_more_structure_checks
description: "2026-10-17 - after a big-VI edit, once one structural comparison shows no unlisted wiring change, go to the numeric test (replay X/Y/Z identity + legs); don't let reviews re-run structural comparisons cycle after cycle"
metadata:
  node_type: memory
  type: feedback
  originSessionId: 352cf43e-6115-43ef-a77e-e8ccfae2d90c
  modified: 2026-10-16T16:20:19.833Z
---

User 2026-10-17 asked "지금 같은 테스트 반복하고 있는거임?" after the P-L copies (built 10-16 12:31) went through three structural-comparison cycles (gate FAIL, tunnel diagnosis, cold full compare) with no measurement; the user then chose "1" = straight to measurement.

**Why:** rule 1a's acceptance is NUMERIC (same inputs -> bit-identical X/Y/Z, own frame numbers). Each review tightened the structural rule a little, each session fell slightly short, and the measurement kept slipping - repetition with no new conclusion. The chat should have pushed for measurement right after the tunnel diagnosis.

**How to apply:** after a big-VI edit, accept ONE structural comparison that shows no wiring change outside the change list (plus approved tidy-ups); then the next cycle measures (replay identity + the frame-rate legs). If a review asks for another structural pass with no new risk named, bring the user the "measure now vs. more structure" choice at once, with measuring as the recommendation. Related: [[fast_decision_cycles_are_the_goal]].
