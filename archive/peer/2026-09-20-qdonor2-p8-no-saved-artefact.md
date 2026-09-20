# qdonor2-p8-no-saved-artefact

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.4815  in 32 / out 39276 / cache-create 243600 / cache-read 1857362  (518s, 27 turn(s))
- **date:** 2026-09-20 04:58:39
- **outcome:** ANSWERED (522s)
- **why asked:** MANDATORY failed-prediction review (CLAUDE.md §5) — gate `P8` of `tools/bench/diag_qdonor2_stage.log` predicted at least one staged step would leave a SAVED artefact and none did, because step 1 alone took the scratch from ExecState 1 to 0.
- **verdict:** ACCEPTED; its discriminating test was run the same session and **refuted the hypothesis under review** (`es_c` = 0, `tools/bench/diag_qdonor2_ia.log:26`). See "What was done with it".

## Question

# FAILED PREDICTION — gate P8, `tools/bench/diag_qdonor2_stage.log` (2026-09-20 04:46, LabVIEW 2026 VI Scripting over ActiveX/COM)

## What was predicted
`P8  at least one step left a SAVED artefact distinct from D1_s1_copy.vi.`
The script applies seven edits to a scratch copy of a large real VI, one at a time, reading `VI.ExecState` after
each and calling `save()` whenever ExecState == 1 (saving a broken VI is banned in this project).

## What was observed
- The untouched scratch (byte-identical copy of the source VI) reads **ExecState 1**.
- **Step 1 alone drives it to ExecState 0** and it never returns to 1 through steps 2–7. Step 1 is:
  place ONE unwired **Index Array** primitive on the VI's TOP-LEVEL block diagram (`gscript.build_index_array`,
  erdosmiller `Create Index Array.vi`). The op reported no error. The node arrives UNWIRED because the library's
  `array` input raised error 1304 for every terminal tried, which is documented behaviour of our wrapper.
- Therefore no step ever saved; 11 gates passed, P8 failed; nothing else in the run failed.
- Earlier the same night, a different script made the same seven edits plus two more in one batch and also ended
  ExecState 0 with the save refused — consistent, but it took no per-step reading, so it attributed nothing.

## The explanation formed under pressure (attack this)
"An Index Array primitive with an unwired `array` input is a BROKEN node, so the whole VI reads ExecState 0 from
step 1 onward; our own note `docs/NAMES.md:476-478` already prescribes DELETING the Index Array after using it as
a terminal donor ('delete the IA → the control stays on the pane, unwired, VI runnable'), and the script simply
never deleted it. The fix is to delete the helper node before reading ExecState."

## Already ruled out (do not re-propose these)
1. Not the later edits: the per-step readings show ExecState was already 0 immediately after step 1, before the
   control creation, the `move_in`s, the dropped subVI and the queue node.
2. Not a pre-broken source: the same scratch read ExecState 1 in the same instance seconds earlier, and the source
   file's md5 is unchanged at both ends of the run.
3. Not a save-path defect: `save()` was never reached — it is only called when ExecState == 1.

## What I want from you
1. The strongest reason the explanation above is WRONG.
2. At least one ALTERNATIVE cause of "ExecState 0 immediately after dropping one unwired Index Array on the
   top-level diagram of a large VI" that the three ruled-out items do not cover — e.g. anything specific to how
   this primitive is created by VI Scripting, to required vs optional terminals on Index Array, to a VI that was
   already in a particular compile/recompile state, or to reading ExecState while another VI is held resident.
3. What observation would FALSIFY the explanation.
4. The single CHEAPEST discriminating test between your alternative and mine, expressed as something a script can
   read back (a count, a class, an ExecState, an error string) — not as a comparison of options.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, so the review is here rather than in the plan file.

# Review — the claim is wrong in scope and wrong in placement, even though its physics is probably right

## 1. Strongest reason the claim is WRONG

**The prescribed fix contradicts the line it cites, and executing it would make step 2 raise.**

`docs/NAMES.md:476-477` prescribes the donor pattern in this order: `build_index_array` (unwired IA) → `create_control` on its `index` terminal → **then** delete the IA → "the control stays on the pane, unwired, VI runnable." The deletion comes **after** the control exists, because the IA exists only to donate the terminal the control is made from. The claim's fix — delete it "before reading ExecState", i.e. at the end of step 1 — removes the donor before step 2 uses it, and `tools/bench/diag_qdonor2_stage.py:152-156` then raises `"the new IndexArray is not on the top-level Nodes[] walk"`.

That line is a cleanup step being read as a causal diagnosis. It says nothing about ExecState while the IA sits there; it describes a three-move pattern whose *end state* is runnable.

**And the fix cannot make P8 pass even if moved to the right place.** The claim explains one step of seven and never asks whether the other six leave a savable state. By this project's own rule — `tools/gscript.py:1988-1989`, *"copying a fresh primitive into a target ALWAYS leaves it briefly broken: the primitive's required inputs are not wired yet"* — step 4 (`drop_subvi`, dropped unwired) and step 7 (Obtain Queue) are the same shape of edit. Unless each is shown to end fully wired, deleting the IA buys zero saved artefacts. **P8 was unsatisfiable by construction**, and that is what this run actually demonstrated. The explanation is also not new: it is already in `tools/gscript.py:1986-1989`, which is why `gui_save()` exists — and the script explicitly disabled that route (`diag_qdonor2_stage.py:13`).

## 2. Alternative cause the three ruled-out items do not cover

**This project has a measured, unexplained case of an op run taking a scratch from ExecState 1 → 0 while adding nothing broken.** `docs/NAMES.md:912-921` (cycle 23, 2026-09-18): *"READING `Is Broken?` PERTURBS THE TARGET … a B4 scratch whose ExecState was **1** immediately before … wire delta 0 — and ExecState afterwards read **0**" (`tools/bench/diag_fstunnel_rbwvictims.log:169-170`), with *"OPEN — the mechanism is not settled … could be the connect itself, the property node's own execution, or a stale/uncommitted compile state."*

Step 1 is that family of operation. `build_index_array` does not merely place a node: it opens the panel, reads `VI.Block Diagram` (23C) — the first documented diagram load of this scratch in this instance — and runs erdosmiller's creator, which **attempts a `Connect Wire` and fails with 1304** (`docs/keystone-op-spec.md:379-381`). Ruled-out item 2 ("it read 1 seconds earlier") is the same reading pattern as the cycle-23 case, so it does not exclude this.

Two smaller ones the record also cannot exclude:
- **Step 1 may have created more than the IA.** `build_index_array` checks only that one new *IndexArray* appeared (`tools/gscript.py:2342-2344`), and no Wire/Constant baseline was taken — the census is end-of-run only (`diag_qdonor2_stage.py:216-219`). So "one unwired node" and "one unwired node + one bad wire" are indistinguishable here; the project has a scripted connect that landed a bad wire surviving Remove Bad Wires (`tools/gscript.py:1294-1295`).
- **"edit error None" is not evidence of a clean edit.** OpBuildIA_v0 sinks the library's `error out` into Clear Errors (`docs/keystone-op-spec.md:377-378`) and the wrapper swallows modal-dialog `RuntimeError`s (`tools/gscript.py:2337-2341`). It means only that no Python exception escaped.

## 3. Against my own alternative — reported, not buried

`tools/bench/stage_d1_s2_loops.log:11,104,107`: stage 2 started from a byte-identical copy of `D1_s1_copy.vi`, edited it **with the ORIGINAL preloaded**, read `exec_state = 1` and saved 475,707 B. So "the first diagram load / the resident ORIGINAL surfaces latent brokenness" is **refuted** for this copy — don't spend a cycle on it. Only the narrow version survives: an op run of the 1304-connect family perturbing compile state, which stage 2 never exercised.

## 4. What would falsify the claim

Run step 1, then **delete the new IndexArray and re-read ExecState**. Claim true → back to **1**. Claim false → stays **0** with the alleged cause removed. Nothing in the run tested reversibility.

## 5. Cheapest discriminating test — one scratch, no VI run, no save, no new op

```
es_a = g.exec_state(SCRATCH)                       # expect 1
c_b4 = {c: g.count(SCRATCH, c) for c in ("Wire","Constant","IndexArray","Function","ControlTerminal")}
g.build_index_array(SCRATCH, Q.IA_AT)
c_af = <same census>
es_b = g.exec_state(SCRATCH)                       # observed 0
g.delete_object(SCRATCH, "IndexArray", <index of the new uid>, verify=True)
es_c = g.exec_state(SCRATCH)
```

| readback | claim | alternative |
|---|---|---|
| `c_af − c_b4` | `IndexArray +1`, nothing else | another class also moves (+1 Wire / +1 Constant) |
| `es_c` | **1** | **0** — the IA was not the (only) cause |

Three extra op runs on a throwaway scratch. It is the only reading that changes the next cycle: `es_c == 1` ⇒ the donor pattern is viable and the staging becomes savable by moving the delete between steps 2 and 3; `es_c == 0` ⇒ dropping a donor on the top-level diagram is a dead end and the stage needs a different decomposition.

## 6. Two facts in the same log that went unreported

- **Handles 30,694 → 63,590 in 106 s** (`diag_qdonor2_stage.log:9,39`) — +32,896 against the ~31,500 fresh-start baseline, while P9 reports **zero** live VI Server refs. Something outside the ref ledger is consuming handles; late readings in that run deserve less trust than early ones.
- **The run left no artefact for the third attempt at this stage.** By CLAUDE.md's own trigger ("the same stage failing twice at the same place … the next cycle's FIRST act is a decomposition plan"), the decomposition is due now, ahead of further cause-hunting.

## Verdict

The claim's physics is probably right — an unwired required input does break a VI, and that is already written into this toolchain. Its diagnosis is wrong in scope (one of at least three independently-breaking steps) and its fix is wrong in placement (it breaks step 2). What would change my mind on the narrow causal point is `es_c == 1` in §5.

Sources: [Index Array function (LabVIEW Wiki)](https://labviewwiki.org/wiki/Index_Array_function) — note it does **not** document required/optional status for the array terminal; [NI forum "Unwired or bad terminal"](https://forums.ni.com/t5/LabVIEW/Unwired-or-bad-terminal/td-p/2772804) — NI staff: the dataflow requirement "can never be met", so "the VI will not compile and run"; [Execution.State property (ID 22D)](https://labviewwiki.org/wiki/VI_class/Execution.State_property) — 0 Bad / 1 Idle, **"Loads the block diagram into memory: No"**; [VI Scripting (LabVIEW Wiki)](https://labviewwiki.org/wiki/VI_Scripting) — "scripting requires recompiling the VI and may break it"; [NI forum "broken VI, but is good when opened"](https://forums.ni.com/t5/LabVIEW/broken-VI-but-is-good-when-opened/td-p/4272389) — programmatic broken-ness with an intact VI.

## Sources

(extract from answer)

## What was done with it

**ACCEPTED, and its discriminating test was RUN THE SAME SESSION — the review WINS on the decisive reading.**
`tools/bench/diag_qdonor2_ia.py` → `tools/bench/diag_qdonor2_ia.log` / `.json`, `BGRUN END rc=0 after 116s`,
**11 pass / 0 fail**, section 5 executed verbatim on a fresh scratch copy of `D1_s1_copy.vi`
(`claudeDev\DIAG_qdonor2ia_050052.vi`), plus the two additions section 1 implies (the `create_control` BEFORE the
delete, per `docs/NAMES.md:476-478`, and a save wherever ExecState read 1):

- **Discriminator 1 — census delta across `build_index_array` = `{'IndexArray': +1, 'Node': +1}`**
  (`diag_qdonor2_ia.log:17`; `Node` is the superclass count of the same object, so `Wire`, `Constant`, `Function`,
  `ControlTerminal` and `SubVI` were all unmoved). This one went the CLAIM's way: the op created exactly one
  object and no stray wire. The "step 1 may have created more than the IA" sub-alternative is **REFUTED**.
- **Discriminator 2 — `es_c` = 0** (`diag_qdonor2_ia.log:26-27`). `es_a` 1 → `build_index_array` → `es_b` 0 →
  `create_control` (ControlTerminal #23070, label `index`, no error) → `es_b2` 0 → `delete_object(IndexArray
  #22968)` (no error, count 48 → 47) → **`es_c` 0**. Deleting the alleged cause does NOT restore ExecState 1.
  **The claim I put up is REFUTED on its own falsification criterion (section 4), and the review's ALTERNATIVE —
  an op run of the 1304-`Connect Wire` family perturbing compile state, the cycle-23 family at
  `docs/NAMES.md:912-921` — is the surviving explanation.**
- The review's section-1 point that **P8 was unsatisfiable by construction** is accepted without further test:
  every one of the seven staged edits lands something unwired, so no ordering of them could have saved.
- `move_in(ControlTerminal #23070 → Diagram #686)` still SUCCEEDED (owner `TopLevelDiagram`#536 → `Diagram`#686,
  no error) and ExecState stayed 0, so **no save was attempted at any point** (`allow_broken` never set,
  `gui_save` never called). Consequence recorded for Pre-decided 35(b): on this copy the front-panel-control
  donor route cannot produce a savable artefact, independently of whether `queue_node` would accept it — and
  round 2 measured that it does NOT accept it either (`error 1057: To More Specific Class in
  OpQueueObtain_v0.vi`, `tools/bench/diag_queue_donor2.log:49,56`).
- Section 6's unreported facts are both carried into STATUS: the handle rise (30,689 → 63,544 in this run too,
  with `ref_counts` live 0 — an instance restart is the only remedy the fleet has) and the **re-split trigger**
  (same stage failed twice at the same place ⇒ the next cycle's first act is a decomposition plan, not a third
  attempt). **The decomposition itself is NOT written here — it is a design decision reserved for the judgement
  session** (CLAUDE.md §3; the material session reports and stops).
- Nothing in the plan documents was edited on the strength of this review.
