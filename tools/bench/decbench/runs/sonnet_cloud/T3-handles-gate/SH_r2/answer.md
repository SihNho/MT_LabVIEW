**Most likely cause: the saved VI is not defective. The L4 gate was applied to a stage it wasn't built for.** The +322 comes from object-creating ops, which allocate handles for the new nodes, constants and wires. I haven't proven that there is no leak. The log argues against one but doesn't rule it out.

**Where the growth sits**
- It lands on the creating ops, not spread across all of them (`stage_d1_qrt_pool.log`, METER lines). k1, which creates the For loop, adds +85 at line 50. k3, k6, k8, k9, k11 and k13 add +79, +27, +29, +33, +58 and +75. The read-only or pure-wire ops k4, k5, k7, k10 and k12 add 0 to +2.
- k13 shows the same pattern. Its connect op creates the junk Invoke node and then purges it, at lines 200-217.
- Each +N is followed by `read` deltas near 0, so there is no per-op drift.
- The references are balanced: opened 9, closed 9, live 0 (`stage_d1_qrt_pool.log:243`).

**Why the R2 comparison doesn't carry over**
- R2's HF gate was flat at ±100 (`stage_d1_l2r2.log:298-299`), but R2 only deleted objects (`task_119-4.json:78` and the card's open question).
- The ±100 gate comes from the op-hygiene rule: 20 repeated calls of one op must leave handles flat. `docs/cycle27-plan.md:409` says that gate alone is blind to VI Server refnums.
- The recipe has no HF gate. The result says "no HF gate in recipe", so the card's L4 line is a criterion nothing in the recipe enforces.

**Evidence against a leak**
- After the work, handles read 34139 (`stage_d1_qrt_pool.log:247`), against 33962 after the restart (`:29`). The +177 over a fresh process is small.
- The 45.6k level is the bed's open-load level, which `docs/REFERENCES.md:231` documents as +20k. So the +648 from open to before-save (`:233`) vanishes when the VI closes.
- Closing a VI releases the handles that creation allocated. That is consistent with the +322, but it doesn't prove it.

**Plausible alternative:** a real leak from an op that creates and then purges, such as the k13 junk-Invoke purge or the k1 "NEW NODE NOT DELETED" shape. The refnum counter is blind to leaks inside LabVIEW, so 9/9 does not rule this out. The k13 +75 is the largest single step and involves a purge.

**Cheapest discriminating test:** repeat the +322 measurement on the same ops without adding objects. Take an R2 byte copy, add the same create ops and then delete each new object. Take one handle reading 3 to 4 minutes after the creates and another after the deletes, with the VI still open. If a create-only run on an R2 copy matches +322 and the post-delete reading falls back near R2's baseline, handles track live objects and there is no leak. If handles stay elevated after deleting the new objects, or the +322 appears again on a second identical run, it's a real leak and the stage needs `handle_audit`.

The result's own handle readings are more reliable than inferring from the log. The restart-to-exit numbers (`:29` to `:257`) give the same answer for free.

ROOT CAUSE: The +322 handles are the normal allocation of ~15 object-creating ops (nodes, constants, wires) in a create stage, which L4's ±100 steady-state criterion, designed for repeated-op hygiene and absent from the recipe, doesn't fit; the 9/9 refs and the return to ~34.1k after close argue against a leak.
TEST: In one LabVIEW session on an R2 byte copy, run only the same create ops and then delete those same objects, reading handles after each phase, to see whether the +322 returns to the R2 baseline once the objects are gone.