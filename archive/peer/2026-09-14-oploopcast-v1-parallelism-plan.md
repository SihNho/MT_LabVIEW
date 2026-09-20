---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# oploopcast-v1-parallelism-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (50s)
- **why asked:** plan review before OpLoopCast_v1 (ForLoop parallelism properties on the 17 For loops of the main VI)
- **verdict:** unverified

## Question

PLAN REVIEW (brief; one paragraph). We hold a ForLoop-typed cast (OpLoopCast_v0: TMSC seeded by a ForLoop refnum control; 17/17 For loops of the main VI resolved, tools/bench/test_oploopcast.log). PLAN OpLoopCast_v1 = copy of v0 + two single-property nodes on the TMSC output (branch): ForLoop 'Is Parallelism Enabled?' 6362004 (bool) and 'Number of Static Parallel Instances' 6362005 (I32), each with a scalar indicator + its error out; wrapper adds {parallel_enabled, static_instances}. Test: sweep the 17 For loops of the main VI; PREDICTION: parallelism enabled on 0 loops (the original is sequential; the restructure plan's G9 assumes P is unused) - any loop with P enabled is a finding. Also the two While-loop-only properties are not touched. ATTACK: (a) are these two properties readable on a VI opened by reference only (edit-time, not running) - any 'must have the P terminal visible' precondition; (b) does 'Number of Static Parallel Instances' return 0 or 1 when parallelism is disabled (what should the test expect); (c) any reason a For loop with a conditional terminal or with feedback (shift registers) reports parallelism differently. Cite LabVIEW Wiki / NI.

## Answer

Plan is sound, with one correction: treat `parallel_enabled` as the decisive assertion and `static_instances` as descriptive data, not as an expected `0` or `1`. Both are VI Scripting properties of the `ForLoop` object; NI documents the static-instance property as read/write, remotely accessible, unavailable only in the Run-Time Engine, and merely not *settable* while running, so an edit-time VI opened by reference is sufficient?봭o visible `P` terminal prerequisite is documented, although reading loads the block diagram and front panel ([NI](https://www.ni.com/docs/id-ID/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/structure/loop/forloop/numstaticparinstances.html), [LabVIEW Wiki](https://labviewwiki.org/wiki/ForLoop_class/Number_of_Static_Parallel_Instances_property)). The static count is stored compile-time configuration and can remain meaningful even when parallelism is disabled; neither NI nor the Wiki specifies a disabled-state sentinel, so record the observed I32 and do not fail on its value ([NI](https://www.ni.com/docs/id-ID/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/structure/loop/forloop/numstaticparinstances.html)). A conditional terminal is incompatible with parallel iteration, so such a loop should report disabled; shift registers/feedback do not redefine the property, although iteration-dependent feedback generally prevents valid parallel execution and certain compiler-recognized reduction patterns are exceptions ([NI conditional-loop documentation](https://www.ni.com/en/support/documentation/supplemental/07/configuring-labview-for-loops-to-exit-conditionally.html), [NI Community discussion](https://forums.ni.com/t5/LabVIEW/Parallelism-with-Shift-Register/td-p/4469242)). Thus sweep all 17, require both property reads to succeed, flag every `parallel_enabled=true`, and retain `static_instances` verbatim; do not infer effective compiler parallelizability from the static count alone.

## Sources

(extract from answer)

## What was done with it

Built and tested as advised (parallel_enabled decisive, instances descriptive): main VI 0/17 enabled, one loop with a
stored P=12 while disabled (exactly the 'meaningful even when disabled' case the reviewer described);
PARALLEL_kernel_v3 TRUE / 4 (test_oploopcast_v1.log 7/7). Verdict: correct.
