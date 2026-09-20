---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# oploopcast-v1-t1-harness-par-no-loop

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (37s)
- **why asked:** failed T1 in test_oploopcast_v1.log (HARNESS_par has no For loop; the P=4 loop is in PARALLEL_kernel_v3.vi) + whether the instance count alone enables parallelism
- **verdict:** unverified

## Question

FAILED PREDICTION check (brief). tools/bench/test_oploopcast_v1.log (tools/bench/test_oploopcast_v1.py, op OpLoopCast_v1 = ForLoop-typed cast + 'Is Parallelism Enabled?' 6362004 + 'Number of Static Parallel Instances' 6362005): main VI 17/17 For loops read cleanly - parallelism enabled on NONE (prediction held), one loop (uid 22786) stores P=12 with parallelism disabled. T1 FAILED: I predicted HARNESS_par.vi (our CPU-parallel benchmark harness, 'P=4') reports a parallel For loop, but Traverse for GObjects class ForLoop on HARNESS_par returned 0 loops - the reader never ran there. MY EXPLANATION: test-design error - HARNESS_par is a thin harness that CALLS the parallel kernel subVI (PARALLEL_kernel_v3.vi lineage, built by gscript.build_kernel/loop_kernel with erdosmiller Create For Loop 'Number of Static Parallel Instances'=4), so the loop is one level down; the right positive control is loop_cast on that kernel VI itself. RISK I want attacked: erdosmiller's 'Number of Static Parallel Instances' input may set the instance COUNT without enabling parallelism ('Is Parallelism Enabled?' stays FALSE) - in which case our 'par' benchmarks (INDEX rows 24 etc.) may never have run in parallel; the discriminating test is the same reader on the kernel VI (expect enabled TRUE, P=4) and, if FALSE, the recorded seq-vs-par timings. QUESTIONS: (a) agree with the explanation and the discriminator; (b) in LabVIEW scripting, does writing 'Number of Static Parallel Instances' alone enable iteration parallelism, or must 'Is Parallelism Enabled?' be set separately (NI docs / LabVIEW Wiki)?

## Answer

Yes.

- **T1 failure is a test-design error**, assuming `HARNESS_par.vi` merely calls the kernel. A nonrecursive `Traverse for GObjects` on the harness diagram should not discover structures inside a subVI. Therefore, zero For Loops says nothing about the called kernel?셲 configuration.

- **The kernel VI is the correct positive control.** Read both properties on the actual `PARALLEL_kernel_v3.vi` lineage:
  - `Is Parallelism Enabled?` (`6362004`) ??expected `TRUE`
  - `Number of Static Parallel Instances` (`6362005`) ??expected `4`

- **Your risk is real: setting P alone does not enable parallelism.** The properties have separate documented responsibilities. `Is Parallelism Enabled?` explicitly enables/disables parallel loop iterations, whereas `Number of Static Parallel Instances` only specifies how many loop instances are used *for parallel loop iterations*. Neither NI nor the Wiki documents a side effect whereby writing the count turns parallelism on. [NI count-property documentation](https://www.ni.com/docs/id-ID/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/node/structure/loop/forloop/numstaticparinstances.html), [LabVIEW Wiki ForLoop property table](https://labviewwiki.org/wiki/ForLoop_class)

Consequently, the safe conclusion is: **the builder must explicitly write `Is Parallelism Enabled? = TRUE`; P=4 alone is insufficient.**

If the kernel reads `FALSE, 4`, the ?쐏ar??benchmark label is invalid unless timings independently prove another source of concurrency. The recorded seq-vs-par timings are then a useful forensic check, but not as decisive as the stored loop properties: modest differences could come from noise, compiler effects, or differing generated code. The strongest cheap check is the kernel reader result, followed by inspecting whether `build_kernel/loop_kernel` ever writes property `6362004`.

## Sources

(extract from answer)

## What was done with it

Retargeted T1 at PARALLEL_kernel_v3.vi: parallel_enabled TRUE, P = 4 (test_oploopcast_v1.log rerun, 7/7) - so the
erdosmiller builder does set 6362004 and the 'par' benchmarks are valid; the seq 8.15 / par 2.43 ms record agrees.
The warning that the count alone need not enable parallelism is recorded in docs/NAMES.md for any future builder.
Verdict: correct.
