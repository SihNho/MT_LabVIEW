# execstate-linkage

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.8794  in 22 / out 27646 / cache-create 150025 / cache-read 1014079  (420s, 23 turn(s))
- **date:** 2026-09-18 20:29:47
- **outcome:** ANSWERED (421s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Claim under attack: a LabVIEW VI-Server `ExecState` reading taken on a copy of a large VI placed outside its
original folder measures SUBVI LINKAGE, not the legality of the edits made to that copy — so a build recipe that
reads `ExecState` without first loading the original into the same LabVIEW instance cannot distinguish "my edits
broke the VI" from "this copy's subVIs did not resolve".
Evidence: three BYTE-IDENTICAL files (md5 c39f36e0675339673b707c59f0784fee, 471,257 B) read ExecState 0 when
opened cold in a fresh LabVIEW 2026 instance, and ExecState 1 in the same instance when the original was opened
read-only first (tools/bench/diag_d0_execstate_preload.log, 9 gates pass, rc=0).
What we are about to do on the strength of it: a 9-minute build run (tools/recipes/build_d1_routeb_v0.py) ended
`ExecState 0` and was attributed to its own skipped build steps (its docstring at :131-135 predicted exactly that
in advance); that run never preloaded the original — the gate is g.exec_state(TARGET) at :1289, i.e.
GetVIReference(...).ExecState on a live instance (tools/gscript.py:1920-1921). We intend to declare that
attribution unsupported and re-run the build with the original preloaded before believing any ExecState result.
Already ruled out: (1) file damage — the three files are byte-identical and the original itself reads 1; (2) one
damaged copy — a copy made fresh during the same run behaves identically; (3) unresolved subVI paths visible to
our readers — 7 subVI calls returned well-formed names and paths, and 4 apparent "missing" ones were members
inside .llb containers.
Attack this. In particular: what else makes a cold-opened copy read 0 while a preloaded one reads 1; and what
would make the PRELOADED reading the wrong one — e.g. the preload masking a genuine break by supplying in-memory
subVIs that the saved VI would not resolve on its own. Name the cheapest test that separates "linkage" from "the
edits are legal".


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

I have what I need. Here is the review.

---

# Failed-prediction review — "ExecState on a cold copy measures subVI linkage, not edit legality"

**Verdict: the mechanism is probably real, but the conclusion drawn from it is wrong, and the action planned on it is the wrong action.** I could not refute cold-0/preload-1 — I found it already recorded in this project before the diagnostic ran. What I can refute is "therefore the D1 attribution is unsupported" and "therefore re-run with a preload."

My own opening shot died on contact: I expected the preloaded `ExecState 1` to be the *original's*, since LabVIEW cannot hold two same-named VIs in memory. The copies are `Track_D0_copy_20260918.vi` and `SCRATCH_execstate_201132.vi`, and `VI.Name` on the reference reads back the copy in both preloaded arms (`tools/bench/diag_d0_execstate_preload.log:45,84`). No collision. Withdrawn.

## 1. The single strongest reason the claim is WRONG

**The D1 attribution never rested on `ExecState` in the first place, so a confound in `ExecState` cannot unsupport it.** The run's own ledger says:

- S1q **was not executed** — `build_d1_routeb_v0.py:1255-1257` ("route B's plan §2b does not name which terminal types the eight queues take").
- S4b/S4s **were skipped** — `:1274-1275` ("the three sentinel `Equal?`s and their -1 literals need the queues of S1q").
- Therefore rows 1.2 / 1.5 / 1.7 are three new While loops with **no sentinel to wire a conditional terminal to**, and S4 logged `conditional terminal 1224 / 3952 / 5058, wire 0` (`tools/bench/build_d1_routeb_v0.log:407-409`).

An unwired conditional terminal is a compile-time broken-VI condition in LabVIEW, not a judgement call ([NI: "Conditional terminal is not wired"](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/conditional-terminal-is-not-wired.html)). The recipe predicted exactly this **before** the run, in writing: `build_d1_routeb_v0.py:131-135`, "⚠️ STATED IN ADVANCE, NOT DISCOVERED AFTERWARDS: THESE CANNOT PRODUCE `ExecState 1`."

So the defensible finding is **`ExecState 0` was over-determined** — it could not *confirm* the attribution, because a cold-loaded copy would read 0 anyway. That is a much weaker statement than "the attribution is unsupported," and only the weaker one follows from the evidence. The plan acts on the stronger one.

*(Honesty on my own evidence: those three S4 rows carry `errs 'error 1055: Property Node in OpLoopEndRef_v0.vi'`, so `wire 0` there may be a failed read rather than a measured absence — worth noting, and it is a separate defect. The ledger argument does not need the read: a sentinel never created cannot have been wired.)*

## 2. Alternative explanations of the same cold-0 / preload-1 evidence

**(a) The preload is cross-linking, not resolution — and this is the masking the brief asked about.** On disk a VI remembers dependencies by path; in memory it tracks them by linker identity, unique by *qualified name*, and LabVIEW "loads the first subVI it finds by that name" ([NI: Avoiding Incorrect Dependencies](https://www.ni.com/docs/en-US/bundle/labview/page/avoiding-incorrect-dependencies.html); [Eyes on VIs: VI Linkages and Cross-linking](http://www.eyesonvis.com/blog/2006/11/vi-linkages-and-cross-linking.html)). For a byte-identical D0 copy this is benign. For the D1 target it is not: that build **drops three fresh subVIs** (`build_d1_routeb_v0.py:292-293`) and **ends in `g.save(TARGET)`** at `:1291`. A preloaded build would measure legality against the original's in-memory hierarchy and then save the relinked result. That is a hazard the plan adds, not one it removes.

**(b) The search flag, not the preload.** Every loader in the fleet calls `GetVIReference(path, "", False, 0)` — options = 0 (`tools/gscript.py:1921`, `:213`, `:1199`). The documented bit that lets LabVIEW hunt for missing subVIs is **0x10** ([NI forum, "Open VI Reference Option: Prompt user to find missing subVIs"](https://forums.ni.com/t5/LabVIEW/quot-Open-VI-Reference-quot-Option-quot-Prompt-user-to-find/td-p/175363)), and LAVA names this exact failure: *"When using Open VI Reference without the proper search flag enabled, LV won't locate missing subVIs that the IDE would find automatically"* ([LAVA: Why is my VI Bad?](https://lavag.org/topic/14744-why-is-my-vi-bad/)). Under this alternative the preload is one of several ways to make the search unnecessary, and it was adopted without comparing it to a one-argument change.

**(c) This project's own ops flip ExecState 1 → 0.** `docs/NAMES.md:898-911`, measured 2026-09-18: an *idempotent* connect plus an `Is Broken?` read took a scratch VI from 1 to 0, and the note says plainly the mechanism is unsettled. Route B ran dozens of `OpConnectNested_v1` / `OpConnectFromWire_v0` calls, each carrying that reader (`build_d1_routeb_v0.log:335-397`, every row "ExecState 0"). The claim does not mention this candidate at all.

**(d) Load/compile settling.** The preloaded arm reads the copy's `ExecState` after a full hierarchy load has already completed; the cold arm reads it immediately after `GetVIReference`. One repeat read after a delay would exclude this for free; it was not taken. I rank this lowest, but it is unexcluded.

**Two scope problems worth stating.** The diagnostic measured `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`; route B's original is a **different file**, `Min_Track N beads V6_ParallelLoop.vi`, md5 `2a78e17…` (`build_d1_routeb_v0.py:172`). Same folder, not the same measurement. And "already ruled out (3)" is thin: the subVI probe covered **7 calls over the first 8 of 170 diagrams** on a VI with ~97 SubVIs, and the 4 "unresolved" rows are an artefact of `os.path.exists` on a path *inside* an `.llb` (an `.llb` is a file, not a directory) — the script's own test at `diag_d0_execstate_preload.py:140`. That item neither supports nor refutes linkage; it is simply unmeasured.

**Prior art:** `tools/recipes/build_d1_v0.py:457-460` already says *"the record splits 3-3 on PRELOAD — 1 whenever the ORIGINAL hierarchy is `GetVIReference`'d before the copy is opened, 0 whenever it is not — and the controlled pair has not been run."* Running the controlled pair was right. Treating its result as new grounds to overturn the D1 attribution is not.

## 3. What would FALSIFY the claim

- A copy opened **cold**, options 0, fresh instance, reading **ExecState 1** → location/linkage is not what sets 0.
- Operationally decisive: a preloaded re-run of `build_d1_routeb_v0.py` that **still reads 0 at S5**. On the ledger that is the *expected* outcome — S1q is still an undesigned row — which means the planned rerun cannot change the verdict and the "believe ExecState once preloaded" policy is falsified by its own first trial.
- For the masking half: if in the preloaded arm the copy's callees report paths under the ORIGINAL's folder, or names the copy never referenced, the preloaded reading is the cross-linked one and is the *wrong* measurement to trust.

## 4. Cheapest discriminating test

**T1 — put the baseline `ExecState` read back into route B's S1. One line, zero LabVIEW time, zero risk.** `build_d1_v0.py:461` already prints `ExecState of the fresh copy` immediately after `shutil.copy2` + `open_panel`; route B's own `s1()` (`build_d1_routeb_v0.py:302-316`) dropped it, which is why that log has **no ExecState before the first wiring op at :335**. With it, "the copy was born 0 (linkage)" and "the build made it 0 (edits)" separate on the right file, in the run that matters, with no preload — and since the log already prints ExecState after every wiring op, you get the flip point for free.

**T2 — name the mechanism:** in both D0 arms, after the ExecState read, enumerate [`Application: All VIs In Memory`](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/application/allvisinmemory.html) and diff the sets, plus read each callee's `VI.Path`. Different sets ⇒ linkage, and you learn *which* subVIs. Identical sets with different ExecState ⇒ linkage is **not** the difference and (c)/(d) take over. Verify the ActiveX short name before use — the ActiveX surface is not identical to the VI-Server one, and this project has already been bitten by assuming it is.

**T3 — one argument, no preload:** re-read with `GetVIReference(path, "", False, 0x10)` in an otherwise cold instance. Returning 1, or popping a "Find the VI named…" modal that *names* a subVI, settles it and names the culprit. ⚠️ that modal blocks — bgrun with a deadline and a dialog sweeper only, never on the unattended path.

**On the planned action:** do not spend the 9-minute preloaded rerun yet. It cannot produce a different verdict while S1q is undesigned, and it attaches a cross-link-then-save hazard to a recipe that ends in `g.save`. Add T1; keep any preload as a *diagnostic* arm that never precedes a save.

**Where I still agree with you:** a cold `ExecState` read on a copy outside its original folder is not a clean legality signal, and gating a build on it is unsound. That part I could not break, and the evidence for it is good. What I am attacking is the inference from there to "the D1 attribution is unsupported," and the remedy.

Sources: [Execution:State](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/execstate.html) · [Conditional terminal is not wired](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/conditional-terminal-is-not-wired.html) · [Avoiding Incorrect Dependencies](https://www.ni.com/docs/en-US/bundle/labview/page/avoiding-incorrect-dependencies.html) · [Another VI with the Same Name in Memory](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OjgSAE) · [VI Linkages and Cross-linking](http://www.eyesonvis.com/blog/2006/11/vi-linkages-and-cross-linking.html) · [Why is my VI Bad? (LAVA)](https://lavag.org/topic/14744-why-is-my-vi-bad/) · [Open VI Reference 0x10 option](https://forums.ni.com/t5/LabVIEW/quot-Open-VI-Reference-quot-Option-quot-Prompt-user-to-find/td-p/175363) · [Application: All VIs In Memory](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/application/allvisinmemory.html) · [GetVIReference (ActiveX)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/application/getvireference.html)

I took no lock, ran nothing, and wrote no files — this review is the whole output.

## Sources

(extract from answer)

## What was done with it

**DISPOSED 2026-09-18 by the cycle-35 judgement session — ACCEPTED on all three attacks, and it changed the plan
the same hour.** The review did what a review is for: it did NOT refute the mechanism (cold-0 / preload-1 is real,
and gating a build on a cold `ExecState` is unsound — reproduced on route B's own original,
`tools/bench/diag_d1_execstate_preload.log:13,:33`, 7/7, rc=0), and then attacked the two things I had actually
got wrong.

1. **"The attribution was unsupported" — WITHDRAWN.** The peer is right that run 3's `ExecState 0` was
   **over-determined**: `s1q` unexecuted (`tools/recipes/build_d1_routeb_v0.py:1255-1257`) and S4b/S4s skipped
   (`:1274-1275`) leave three While loops with unwired conditional terminals, a compile-time break that owes
   nothing to any gate. What the measurement kills is the *gate's* power to discriminate, not the explanation.
   `docs/cycle27-plan.md` Pre-decided 16 was rewritten to say so. One thing the peer could not have known and
   which cuts the other way: those conditional-terminal readings carry `error 1055: Property Node in
   OpLoopEndRef_v0.vi` (`tools/bench/build_d1_routeb_v0_run3.log:416-418`), so by Pre-decided 14 they are UNREAD
   too — recorded in 16(a). Neither side is settled; that is exactly why point 3 matters.
2. **"Re-run the build with a preload" — DROPPED as the remedy.** The cross-linking hazard the peer names is real
   and is made worse by `g.save(TARGET)` at `:1291`; a preload can also MASK a break by supplying in-memory subVIs
   the saved VI would not resolve alone. Preload is now confined to read-only diagnostics that never save
   (Pre-decided 16(b)), and its three unexcluded rivals (`GetVIReference` options `0` vs `0x10`, our own ops
   measured flipping 1 → 0 at `docs/NAMES.md:898-911`, load/compile settling) are recorded there.
3. **T1 ADOPTED as the next cycle's first act.** Restoring the baseline `ExecState` read into route B's `s1()`
   (`tools/recipes/build_d1_v0.py:461` has it; `build_d1_routeb_v0.py:302-316` dropped it) is one line, needs no
   preload, and separates "born 0" from "the build made it 0" inside the recipe's own instance. It is written into
   Pre-decided 16(c) and is the first line of STATUS `## NEXT`, ahead of any further 9-minute run — which is also
   the peer's explicit advice.

Nothing in the review was rejected. Cost $2.8794 (in 22 / out 27,646 / cache-create 150,025 / cache-read
1,014,079, 23 turns, 421 s) against a 9-minute build run it prevented and a wrong sentence it removed from the
plan.
