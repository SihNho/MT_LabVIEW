**Short answer: the saved VI is almost certainly not defective. The L4 handles gate was measuring the wrong thing for this stage. It treated each new operation's one-time load cost as if it were a leak.**

**Why it is not a leak in the VI**
- The handle count belongs to the LabVIEW process, not to the file. Every check on the file itself passed: cdiff matches R2's 16 rows (`stage_d1_qrt_pool.log:231`), 7 new wires and none lost (`:226`), and the Error List is 53, the same as R2 (`result_119-4.json:24`).
- Once the work VI was closed, handles fell back to 34139 (`stage_d1_qrt_pool.log:247`), close to the 33962 measured just after the restart (`:29`). That means the roughly 12,000 handles held while the VI was open were given back. VI Server references opened and closed were 9/9, with 0 still open (`:245`).

**Why the gate failed**
- The ±100 "steady state from k1" rule assumes every operation's VI has already been loaded by the first operation. That assumption is written down at `diag_c113c_scratch.py:56-57` ("first op call (the op VI's first load)"). It held for R2, which passed with k1 at 45755 and the end at 45730 (`stage_d1_l2r2.log:298-299`).
- This pool stage calls seven different operations. Every jump in the handle count happens the first time a new operation is called:
  - k2 drop_subvi +26
  - k3 create_primitive_nested +81
  - k6 queue_node +28
  - k8 enqueue +30
  - k9 wire_const +32
  - k11 connect_nested_v1 +59
  - k13 connect_from_wire +75

  These add up to about 331, which accounts for the +322.
- Repeat calls to an operation that was already loaded stay flat: k4 −1, k5 0, k7 +2, k10 −5, k12 −4 (`stage_d1_qrt_pool.log:41-218`).
- The k13 jump of +75 matches the first-call cost measured earlier for OpConnectFromWire_v0 + OpWireSource_v5, which was 74 (`diag_c97_tools_handles.log:35`). In that same earlier test, 20 repeated calls stayed within ±1 (`:125,:128`).
- The plan itself says handles are to be recorded, not gated (`d1-loop12-17-split-plan.md:521`, 176(a)). Card rule 114 says a jump on first load comes back as an open question and the gate's reference point is never shifted to hide it (`:2021`). The card's L4 line turned a recorded number into a gate (`task_119-4.json:32`). The recipe already logged it only as "PH … RECORDED" (`stage_d1_qrt_pool.log:233`).

**The main alternative to rule out**
The two biggest jumps (k11 and k13) come from the two connect operations. Both of them create and then delete a leftover Invoke Node (`:176-186`, `:204-216`). So a real per-call leak in that create-and-delete step is possible.

There is also one number I cannot explain. After closing, this run ended at 34139, while R2 ended at 32064 (`stage_d1_l2r2.log:321`). That residual of about 2,000 handles is not accounted for by anything above.

**The cheapest test that separates the two**
Do not re-open the saved VI: it is broken by design, and broken VIs are never loaded headless (`stage_d1_qrt_pool.log:241`). Instead, use one byte copy of R2 as a scratch VI in a fresh LabVIEW:
1. Call each of the seven operations once, to load them.
2. Call connect_nested_v1 and connect_from_wire 20 times each, idempotently, including the Invoke Node create-and-delete, the same way as `diag_c97_tools_handles.log:124-128`.
3. Read the handle count after closing.

If the cause is first-load cost, the handle count stays within ±100 across the 20 calls. If there is a leak, it grows by roughly 30–75 per call.

ROOT CAUSE: Every operation's first call loads its VI, a one-time cost of about +26 to +81 handles; this stage uses seven different operations, so the "steady state from k1" gate added up seven load costs (+322) and called it a leak, while repeat calls stayed within ±5 and handles returned to about the restart level once the VI was closed.
TEST: On a byte copy of R2 in a fresh LabVIEW, call each of the seven operations once, then call connect_nested_v1 and connect_from_wire 20 times each; a count flat within ±100 confirms first-load cost, and steady growth of about 30–75 per call would mean a real leak in the Invoke Node create-and-delete.