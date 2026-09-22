# c76b-m3a3-run2-failpred

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.5981  in 40 / out 35130 / cache-create 139257 / cache-read 2469285  (455s, 35 turn(s))
- **date:** 2026-09-22 08:41:50
- **outcome:** ANSWERED (459s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION — D1 stage M3a-3, RUN 2 (2026-09-22 08:13), log tools/bench/build_d1_m3a3_run2.log

This is the SECOND run of tools/recipes/build_d1_m3a3.py. Run 1's failure was already reviewed
(archive/peer/2026-09-22-c75-m3a3-run1-failpred.md, ANSWERED, disposed). Run 2 repeats the SAME failing
prediction but adds a discriminator reading that run 1 did not have, so the question here is narrower.

## The prediction that failed (written before the read)

P0 ROW D's SINK RESOLVED: wire 7506 appears EXACTLY ONCE on `FlatSequence #681`'s terminal table.
Basis: docs/cycle27-plan.md Pre-decided 72 — "a tunnel is not a `Nodes[]` entry, but its terminal IS an entry
in its owning structure node's `Terminals[]`" — and the shift-register OUTER that WAS resolved on its owning
While-loop node in tools/bench/diag_c75b_loopterms.log.

## What run 2 actually read (tools/bench/build_d1_m3a3_run2.log, the P0 block)

- `FlatSequence #681 lives at: None` — 173 of 173 diagrams scanned, 14.8 s.
- `FlatSequence #681 LIVE: Diagram idx None, Nodes[None], label None, uid echo None, 0 terminal(s)`.
- NEW IN RUN 2, the discriminator: `#681 present in the FlatSequence census True, its owner column
  'TopLevelDiagram'`; and `owner_of(Diagram #681) = None`; and
  `RuntimeError: owner_of(#681) is not an answer: echoed 'Diagram'#681, errors 'error 1055: Property Node in
  OpOwnerChain_v1.vi'`.
- Row D was DEFERRED to a later stage M3a-3b. Wire 7506 was NOT deleted; nothing was improvised. Row C was
  completed and saved (26 gates pass / 2 fail, both fails being this deferral).

The reader in question is `find_node` (tools/recipes/build_d1_m3a1.py:541): it enumerates
`report_all('Diagram')` and then `g.node_labels(path, i)` per diagram, matching on uid.

## THE CLAIM YOU ARE ASKED TO REFUTE

"`FlatSequence #681` is reported by the census with owner column 'TopLevelDiagram', yet resolves to no
diagram's `Nodes[]` and answers `Diagram` to a class echo, because the uid #681 does not name the sequence
NODE at all — it names the sequence's own inner DIAGRAM (or a frame), so Pre-decided 72's rule is being
applied to the wrong object rather than being false."

Attack it. In particular:

1. Give the strongest reason the claim is wrong — e.g. a reason a genuine structure NODE could read
   `Nodes[] = None` over an ActiveX/COM VI-Scripting path while still being the node.
2. Give at least one alternative explanation that the readings above do NOT rule out. The `error 1055`
   (Property Node in OpOwnerChain_v1.vi) on the very call whose answer is being trusted is a candidate:
   say whether a 1055 makes the 'Diagram' echo untrustworthy rather than informative.
3. Say what observation would FALSIFY the claim, and name the CHEAPEST discriminating measurement that
   separates "wrong object" from "wrong reader" from "genuinely not a Nodes[] member". Read-only, one or two
   op calls; this project's artefact is broken by design and is never run, so `ExecState` is not evidence.
4. Is LabVIEW 1055 ("object reference is invalid") on a Property Node the expected error when a uid that IS
   live is cast to a class it does not belong to? Cite the vendor's own documentation if you can reach it.

## Already ruled out — do not spend the answer on these

- Not a naming/label error: the two Row-C addresses resolved LIVE and uid-echoed on the same run, and Row C
  completed and saved.
- Not a load/state problem: the target's own census read 634 nodes / 1920 wires in the same session, and the
  later calls on the same path succeeded.
- Not the artefact's brokenness: `ExecState` is 0 by design for every file in this chain, is not gated on and
  is not reasoned from.
- Not run 1's defect (`OpConnectNested_v2.vi` not on disk): that was fixed before run 2 by switching to
  `connect_nested_v1` plus a new on-disk-existence gate W0, and run 2 got past it.

## What will be done with your answer

Nothing is built on it in this session. It is archived as the review this failure owes, and the NEXT cycle's
judgement session decides M3a-3b from it. Do not propose a plan; propose the measurement.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## The claim is refuted — and by evidence the recipe itself already had

**1. The single strongest reason the claim is WRONG: its discriminator was never run on #681.**

`build_d1_m3a3.py:516-517` calls `OWNER_OF(TARGET, D686, strict=True)` — `D686 = 686`. The log says so verbatim: `owner_of(Diagram #686) = None`, `echoed 'Diagram'#686` (`build_d1_m3a3_run2.log:61-63`). The brief I was given substitutes **681 for 686** in all three quotations. No class echo of #681 was ever taken. And the echo that *was* taken is correct and uninformative: #686 is a known diagram (`stage_d1_s3a_focus_ind.py:207`, `cycle27-plan.md:1626-1628`), so "#686 answers `Diagram`" is a true statement about a different object.

Worse for the claim, #681's class **was** already measured cleanly, in the very file the recipe cites:

- `diag_c75_m3a3_rows.log:163` — `uid 7468 -> owner 'FlatSequence' uid 681 | 482 says 'FlatSequence' cast 'FlatSequence'`, **error column empty**. A successful `To More Specific Class` **to FlatSequence**, uid-echoed.
- `diag_c75_m3a3_rows.log:164` — `diag_index(#681) raised ValueError: 681 is not in list`. #681 is **absent from the Diagram census**, while the real frame diagram #686 sits in it at index 19.

Both readings say the same thing: **#681 is a FlatSequence node — not a diagram, not a frame.** The claim's core assertion is contradicted by measurements taken before run 2.

**2. The alternative the readings do not rule out — and which is independently confirmed: `FlatSequence` is not a `Node`, so it cannot be in any `Nodes[]`, ever.**

NI's own Darren Nattinger, on the scripting question of wiring to a Flat Sequence: *"the FlatSequence class does not inherit from Node. Here are the workarounds I can think of."* ([NI Forums](https://forums.ni.com/t5/LabVIEW/Scripting-Connect-a-Terminal-to-a-Flat-Sequence-Structure/td-p/2672239)) The hierarchy pages agree: FlatSequence is a direct child of **GObject** ([FlatSequence class](https://labviewwiki.org/wiki/FlatSequence_class)), while `Structure` — the parent of the loops — *is* a child of `Node` ([Node class](https://labviewwiki.org/wiki/Node_class)). The reason given is historical: the flat sequence's multi-frame tunnels didn't fit the Node wiring model, and reworking it "would be a substantial investment."

Your own whole-VI census confirms it at zero cost. In `tools/bench/main_vi_nodeterms.json`, `WhileLoop #637` is node n=4 (`:6421`) and `Global #7202` is n=8 (`:7253`) — matching `diag_c75_m3a3_rows.log:191-192`. **Not one of the five FlatSequence uids (#681, #12938, #43914, #25681, #28557) appears anywhere in that file.** The absence tracks the *class*, not #681, and not the top-level diagram — three of those are owner-`'Diagram'` nested sequences.

So P0's prediction was false **a priori**. Pre-decided 72's analogy was drawn from a shift register on a **WhileLoop**, and loops are `Structure → Node`. FlatSequence is the one documented exception, and the analogy was extended across exactly the class boundary where it breaks.

This also dissolves a standing anomaly: `cycle27-plan.md:2445-2447` records "this VI's top-level block diagram is **EMPTY** — `node_labels(top=0)` 0 rows **and** `node_info` 0 rows, two independent readers, whole-VI `count('Node')` 630." A top-level diagram that owns two Flat Sequences (#681, #12938) and nothing else Node-classed reads as legitimately empty to a `Nodes[]` reader. Two puzzles, one mechanism.

**3. On error 1055 — no, it is not the wrong-class error, and it is not evidence here.**

1055 is *"Object reference is invalid"* ([NI KB](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE), [General LabVIEW Error Codes](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/general-labview-error-codes.html)). The cast error is **1057**, *"Object cannot be typecast to the specified type"*, raised at `To More Specific Class` ([NI KB](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OwLSAU)) — which this project sees and names correctly elsewhere (`cycle27-plan.md:1031`). A live uid cast to a class it does not belong to yields **1057, not 1055**.

The 1055 in the log is the known, documented one: the recipe's own docstring predicts it — *"an owner chain TERMINATES SILENTLY at a `FlatSequenceFrame` (error 1055)"* (`build_d1_m3a3.py:477-478`, `docs/toolkit-capabilities.md:61`) — and the log shows exactly that shape, `owner 'FlatSequenceFrame' uid 0` with 1055 on the owner-uid read. It makes the *owner uid* unreadable; it does not make the `'Diagram'` self-echo untrustworthy, and it says nothing about #681 either way. Note also that in this codebase a bare 1055 is the routine "nothing there" signature, not a type complaint (`build_d1_m3a1.py:526,532`).

**4. What would falsify my explanation, and the cheapest test.**

Falsifier: **any** FlatSequence uid appearing in **any** diagram's `Nodes[]`. One hit and the hierarchy story collapses and #681 becomes genuinely special.

Cheapest discriminating measurement — read-only, existing verbs, no new code, and it separates all three branches at once:

> Run `find_node(TARGET, uid, hints, tag)` on **#43914** (FlatSequence, owner `'Diagram'`, nested) and on **#12938** (FlatSequence, owner `'TopLevelDiagram'`). Two sweeps, ~15 s each.

- **Both miss** → the miss tracks the *class*. FlatSequence ∉ Node is the cause, #681 is unremarkable, and the Nodes[] route does not exist for any flat sequence. (This is what `main_vi_nodeterms.json` already predicts — so consider running it only as confirmation.)
- **#43914 found, #12938 missed** → the miss tracks the *owner*; the top-level reader is blind and my explanation is wrong.
- **Both found** → the fault is specific to #681 and the claim gets its first actual support.

One-call companion worth adding, since `TOP = 0` is load-bearing and was measured on an earlier artefact: confirm `report_all(TARGET,'Diagram')` row 0 is still `{'class':'TopLevelDiagram','uid':536}` (`cycle27-plan.md:1627`), so "173 of 173 scanned" provably included the top level.

**What the evidence does not settle.** Whether a terminal-table route to #7468 exists *at all* over this COM path. The forum thread offers only indirect workarounds — drop a node inside the frame, wire to it, delete it; or swap to a Stacked Sequence, wire, swap back — both of which are *mutations of the original's structure*, so neither is free under rule 1a. That, not #681's identity, is M3a-3b's real question.

**Two process notes.** The brief's 681-for-686 substitution would have propagated into the next cycle's judgement, since that session reads the brief and not the log. And `find_node`'s per-diagram `scanned` rows (node counts, per-diagram errors) were dropped by `node_table` (`build_d1_m3a3.py:347-358`) before `dump()` — `build_d1_m3a3.json:816-824` keeps only nulls, so the one dataset that would have distinguished "reader blind" from "not a member" was discarded by the run that needed it.

Sources: [NI Forums — scripting a Flat Sequence](https://forums.ni.com/t5/LabVIEW/Scripting-Connect-a-Terminal-to-a-Flat-Sequence-Structure/td-p/2672239) · [FlatSequence class](https://labviewwiki.org/wiki/FlatSequence_class) · [Node class](https://labviewwiki.org/wiki/Node_class) · [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) · [Error 1055 (NI)](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE) · [Error 1057 at To More Specific Class (NI)](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OwLSAU) · [General LabVIEW Error Codes](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/general-labview-error-codes.html)

## Sources

(extract from answer)

## What was done with it

**ITS MEASUREMENT WAS RUN, EXACTLY AS NAMED, AND NOTHING WAS BUILT ON THE ANSWER** — cycle-68 MATERIAL session,
read-only, on a scratch COPY of the bed (`tools/bench/diag_c77_rowd_addr.py` → `tools/bench/diag_c77_rowd_addr.log`,
`…json`; bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e…` unchanged at both ends). Per finding, what
the machine said:

1. **The review's own "cheapest discriminating measurement" — BOTH MISS, so the miss tracks the CLASS.**
   `find_node` on **#43914** (nested) → `found None`, 173 of 173 diagrams, 635 nodes; on **#12938** (top-level) →
   `found None`, same census; and on **#681** itself → `found None`. The `FlatSequence` census lists 21 rows, and
   not one of those uids is in any diagram's `Nodes[]` (`diag_c77_rowd_addr.log`, the [B] block). This is the
   branch the review predicted from `main_vi_nodeterms.json`.
2. **Finding 1 (the brief substituted 681 for 686) is CONFIRMED, and the corrected read changes the answer**:
   `owner_of(#681)` = **`'TopLevelDiagram' #536`**, uid-echoed, error column empty — not `'Diagram'`. So #681 is a
   FlatSequence NODE owned by the TOP-LEVEL diagram, and Pre-decided 107's route ("read #681's table on
   `Diagram #686`, traverse idx 19") addresses it on a diagram that does not own it. #686's `Nodes[]` has 27 rows
   and #681 is absent from them.
3. **The claim the review was asked to refute stays REFUTED**: #681 answers `'FlatSequence'` to its own class echo
   (`diag_c75_m3a3_rows.log:163`) and `diag_index(#681)` raises `ValueError: 681 is not in list` again here.
4. **What the review said was unsettled is now MEASURED, and it is the opposite of a dead end**:
   `OpFsInnerTunnelTerm_v0` on **uid 7468** returns a terminal reference with EVERY error column empty —
   `LeftTerm #7488 wire #7506`, `RightTerm #7471 wire #7448`, `is_source False`, self/cast echo
   `'FlatSequenceInnerTunnel'#7468`. A control read on FSIT #123 of the same target also answers. So the row-D
   SINK is addressable today by uid, without any `Nodes[]` membership and without touching the original's
   structure.
5. `report_all(TARGET,'Diagram')` row 0 is still `TopLevelDiagram #536` (173 rows), so "173 of 173 scanned"
   provably included the top level — the companion check the review asked for.
6. The process note is acted on: this run KEEPS the per-diagram `scanned` rows (0 `node_labels` errors on every
   sweep), which is the dataset run 2 discarded.

No route decision was taken here — what M3a-3b does with (4) is the judgement session's call.

**JUDGEMENT DISPOSITION CLOSED 2026-09-22 (cycle 69 series) — CARRIED BY `docs/cycle27-plan.md` Pre-decided
104–111.** The call left open at (4) was taken:

- **The class explanation is ACCEPTED IN FULL and written into the project's capability record.** `FlatSequence`
  is a direct child of `GObject`, never of `Node`, so it is in no `Nodes[]` and a `Nodes[]` miss on one is never
  to be diagnosed as an ownership problem. Carried by **Pre-decided 110**; the same entry records that
  `diag_index(#681)` raises `ValueError: 681 is not in list` and is therefore not a membership test.
- **Pre-decided 107 is AMENDED, not withdrawn, by Pre-decided 109**: its prescribed route (#681's table on
  `Diagram #686`) is void because #681 is owned by `TopLevelDiagram #536`; its prohibition half stands. The
  replacement is the inner tunnel's OWN terminal table, read by uid with `OpFsInnerTunnelTerm_v0` — finding (4)
  above, adopted.
- **Row D's address pair built on (4) is Pre-decided 111**, and its acceptance is Pre-decided 106 unchanged
  (source identity, ordered idempotent second pass, never a wire-count delta).
- **What the review said was unsettled — whether a terminal-table route to #7468 can WRITE — was carried into a
  separate failed-prediction review** (`archive/peer/2026-09-22-c79-rowd-writer.md`) rather than answered here;
  its outcome is Pre-decided 115–118. The forum's indirect workarounds (drop a node in the frame and delete it;
  swap to a Stacked Sequence and back) stay REFUSED under rule 1a, as this review itself judged.
- **The process note is ACCEPTED and was acted on by the cycle-68 run** (the per-diagram `scanned` rows are kept,
  0 `node_labels` errors on every sweep); the brief's 681-for-686 substitution is corrected in the plan's own
  text at Pre-decided 109.
