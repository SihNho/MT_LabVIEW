# Prior-art question, card 138-4: For loop with auto-index tunnels inside a plan-made While body (P4 reader, PD311(b))

Plan file: tools/bench/plan_ring_p4_v8.json md5 059b5296 (v7 01ab0893 + this re-cut, actions 26/29/53-62 new;
maker tools/bench/prep_c138_4_mkv8.py, log tools/bench/prep_c138_4_mkv8.log).
Deviation from PD311(b)'s wording: Greater? stays OUTSIDE the For on the arrays (v7 p4_gt_last unchanged) and its Boolean
array is auto-indexed in, because compile_plan's tunnel group (stagexec.py:685-694) cannot chain `last` through two tunnels.
Decision cited: docs/d1/ring-p4.md:226-244 (PD311 (a) Select takes a scalar s only; (b) the redesign; (d) name 's? t:f').

New structure class on this build path (the P4 ring reader, loop 1.2 body #23166, plan-made While W1):
1. `create ForLoop` FMN1 on W1's body (a plan-made While body), count terminal N UNWIRED (count from auto-indexed inputs).
2. Three EXPLICIT plan `tunnel` actions with `indexing: true` on that plan-made For:
   - IN  TFN1: the local read 'Num' (I32[20], already wired to Greater?.x) -> Num[i] -> Select.t
   - IN  TFB1: Greater?(Num array, last) Boolean[20] -> b[i] -> Select.s (scalar)
   - OUT TFS1: Select 's? t:f' -> I32[20] -> Array Max & Min.array (on W1's body)
3. Two `const_donor` DigitalNumericConstants I32 2147483647 (KMX1 on the For body -> Select.f; KMX2 on W1's body -> Less?.y).
   No claudeDev donor VI holding I32 2147483647 exists today (DonorSRInit_v0 #134 U32 max, #248 I32 0; DonorRingConst_v0 #249 I32 -1).

What I want to know (has this been done / measured / refuted here already?):
- Has a plan `tunnel` action with `indexing: true` on a plan-made ForLoop ever run through stagexec, and what IndexMode did
  the real tunnel get? (stagexec applies `index_mode_fix` only inside `if lost:` at stagexec.py:2104-2109.)
- Has a For loop with an UNWIRED N and only auto-indexed inputs been built by our scripting anywhere (plan_disp DLF1?), and
  did it compile (ExecState) or break?
- Has Select with a scalar Boolean s fed by an auto-indexed Boolean array tunnel been built before?
- Is there an existing donor VI / op that makes an I32 constant of a chosen value (not DBL), so a new donor VI is not needed?
- Was Greater? on (I32 array, I32 scalar) followed by an auto-indexed For already used in the original VI or a prior stage
  (a precedent this re-cut could copy instead)?
