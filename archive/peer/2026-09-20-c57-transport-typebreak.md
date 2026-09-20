# c57-transport-typebreak

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.7974  in 16 / out 44946 / cache-create 227327 / cache-read 708732  (567s, 18 turn(s))
- **date:** 2026-09-20 23:29:10
- **outcome:** ANSWERED (568s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this claim. Do not confirm any part of it.

## The failed prediction (the thing you are reviewing)

`tools/bench/diag_s57_ctmove_wire.py` (log `tools/bench/diag_s57_ctmove_wire.log`, `BGRUN END rc=1 after 123s`,
GATES 27 pass / 2 fail) predicted an EMPTY error column from `wire_indicators`. Instead, verbatim from
`diag_s57_ctmove_wire.log:83-84`:

```
  FACT  P5a wire_indicators(Function[102], ['x .and. y?'] -> ['index'], diagram_index=46) error VERBATIM
        'RuntimeError: wire_indicators: target BROKEN after wiring - a source terminal was probably unwired
         (WI then extends an unrelated wire; revert the target)'
  FAIL  P5a wire_indicators returned an EMPTY error column
```

## THE CLAIM YOU MUST ATTACK

> **The S3a transport route is SOUND and the only thing that failed is TYPE.** Every transport verb worked:
> the indicator was created on the top-level diagram, `move_in` reparented it TOP-LEVEL -> NESTED `Diagram #639`
> (never tried before), and `wire_indicators` FOUND it by label at the nested diagram's live index and branched
> the source's wire onto it — `:85` the target's wire uid went **0 -> 10799**, the source's own wire, with the
> whole-VI `Wire` count unchanged at 1905 (a branch creates no Wire object, `tools/gscript.py:1771-1772`).
> The connection is simply MISMATCHED: the indicator the 46(a) route produces is `'index'`, the Index Array's
> **numeric** `index` terminal, and the source `#10686` t0 `'x .and. y?'` is a **Boolean** — so `ExecState` went
> 1 -> 0 and the ordered second pass read `Is Broken? = True` on wire 10799. `wire_indicators`' own message
> ("a source terminal was probably unwired") is MISLEADING here: `#10686` t0 was measured wired 3/3 before and
> after. **Therefore the 5001 story is closed, no new op VI is needed, and what remains is only to create an
> indicator of the RIGHT TYPE.**

## What is actually on the machine (facts from this one run, not argument)

* Target: a dated scratch of `claudeDev\D1_s2_loops.vi` (md5 `6ff19497…`), LabVIEW 2026, VI Scripting over COM.
* `:20-32` LIVE indices, re-resolved, nothing cached: `diag_index(#639)=46`, `diag_index(#536)=0`,
  `diag_index(#686)=19`, `owner_of(#639)=('WhileLoop',637)`, `owner_of(#10686)=('Diagram',639)`,
  `#10686` at Traverse `Function` index 102 of 183.
* `:36-48` create at top level: `node_info` 0 -> 1 entry `[(0,'Index Array','Index Array')]`; IndexArray #23486
  owner `('TopLevelDiagram',536)`; `create_indicator(Nodes[0].Terminals[2])` -> ControlTerminal **#23541**,
  census 114 -> 115; `delete_object` removed #23486; **ExecState 1** after the delete. All error columns `''`.
* `:51-59` the new panel row READ off the machine (never retyped):
  `{'label': 'index', 'indicator': True, 'uid': 23525, 'is_source': False, 'wire': 0, 'term_err': 0,
  'wire_err': 1055}`; utf-8 hex `696e646578`; no newline; not a duplicate.
  `owner_of(#23541) = ('TopLevelDiagram', 536)`.
* `:64-73` `move_in(#23541 -> Diagram #639 @ index 46, position (120,4000))` error `''`;
  `owner_of(#23541)` went `('TopLevelDiagram',536)` -> **`('Diagram',639)`**; ControlTerminal census 115 -> 115;
  panel rows 115 -> 115; **ExecState still 1** after the move. It left ONE junk `Invoke` (uid **23486** — the
  uid the deleted IndexArray had just released), purged in the same run, error `''`.
* `:79-92` 37(e) grain: `#10686` 3 terminals / 3 wired BEFORE and AFTER; `#637` 59 terminals / 48 wired BEFORE
  and AFTER — **no tunnel and no border object appeared**.
* `:85-87` the effect: target wire **0 -> 10799**, whole-VI Wire count 1905 -> 1905, `ExecState` **1 -> 0**.
* `:102-104` ordered second pass (42(b), an idempotent re-connect of the EXISTING `#10686` t0 -> `#10407` t0
  net, `wire_delta 0`, op error column `''`): **`Is Broken? = True` on wire uid 10799**.
* `:96-99` no save: `ExecState 0`, `g.save()` NOT ATTEMPTED, `allow_broken` False, `gui_save` never called.
  The scratch was deleted because nothing was saved — **there is no artefact on disk from this run**.
* Cycle 55 calibrated the instrument: `Is Broken?` read **False** on a type-MATCHED connection and **True** on a
  type-MISMATCHED one, on the same VI, but only on a second ordered pass.

## Already ruled out — do not spend your answer here

1. "The label was wrong / retyped": it was read off the machine by `panel_wiring` in the same run, hex `696e646578`.
2. "The source was unwired": `#10686` t0 `'x .and. y?'` read wire 10799, is_source True, 3/3 wired, before and after.
3. "Build a new op VI": forbidden this cycle by a standing decision; answers needing one are inert here.

## What I want from you

1. The single strongest reason the claim above is WRONG.
2. An alternative explanation of `ExecState 1 -> 0` and `Is Broken? = True` that is NOT a type mismatch —
   in particular, address whether branching a source wire onto a terminal that sits on the SAME diagram as
   the source but INSIDE a While loop whose border the wire does not cross can break for a structural reason;
   and whether the `'wire_err': 1055` already present on the new panel row at `:51` (BEFORE any wiring) matters.
3. What observation would FALSIFY the claim.
4. The cheapest discriminating test, using only verbs that already exist in this fleet
   (`tools/gscript.py` + `tools/recipes/build_d1_v0.py`'s `move_in` / `owner_of` / `diag_index`) — and say
   whether any existing verb can produce an indicator of a CHOSEN type at all, or whether `create_indicator`'s
   type is always dictated by the terminal it is created from.
5. Say explicitly whether "the 5001 story is closed" follows from this run, given that this run never
   re-attempted the two indicators (`'File # Saved'` uid 6, `'Image'`) that produced the 5001s in cycle 56.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this session, so the review is here rather than in a file — which matches the brief's "your output is your answer, nothing else."

---

# REFUTED on the load-bearing half

The TYPE diagnosis is probably correct. That is the problem: it was knowable before the run, and it is not what the run was for. **"The transport route is SOUND" is not supported by this run, and "the 5001 story is closed" does not follow at all.**

## 1. The single strongest reason the claim is WRONG

**The run held a saveable artefact at `diag_s57_ctmove_wire.log:70` and spent it on a connection it could have predicted would break the VI — so the one measurement that proves transport soundness was never taken.**

| line | state |
|---|---|
| `:70` | `ExecState AFTER the move (and the junk purge) = 1` — **reparented, legal, saveable** |
| `:82` | `ExecState BEFORE wire_indicators = 1` — still saveable |
| `:87` | `ExecState = 0` |
| `:96-97` | `g.save()` **NOT ATTEMPTED** |
| `:111`,`:117` | `saved: False`, `bytes: None`, md5 `6ff19497…` — **byte-identical to the input at `:10`** |

"Sound", for a scripted structural edit, means *it survives serialisation and reload*. `owner_of(#23541) = ('Diagram', 639)` at `:69` is an **in-memory** read of the live object graph taken seconds after the Move. Prior art says the save has **never** been reached after a `move_in` — `docs/cycle27-plan.md:1099-1100`: *"`ExecState` 0 afterwards; the save was refused."*

This is the exact signature the standing rule exists to stop (CLAUDE.md, *"A step is not done until it has left a file"*, written 2026-09-19 after ten attempts left copies byte-identical to the original). `:117` md5 == `:10` md5. The claim reads that as success.

**Subsidiary:** the corroborating evidence is this project's own documented non-evidence. `docs/cycle27-plan.md:1101-1105`, in red, on this same VI and this same number: *"**A WIRE COUNT CAN NEVER DETECT A CUT** … the census stayed **1905 → 1905 → 1905** … Any stage gated on a Wire delta would have reported all green with its wires cut."* `1905 → 1905` is compatible with a branch, a cut, and nothing happening. It should not be in the argument.

## 2. An alternative explanation that is not a type mismatch

**2a — the instrument cannot separate them, and its only archived positive calibration is the structural case.** `docs/NAMES.md:908-909`: `Is Broken?` measured **`False` on a good wire** and **`True` on a two-source wire**. Cycle 55 added a type calibration. It fires for both — sensitivity, never specificity. The claim uses a one-bit detector documented to respond to the competing hypothesis as evidence for its own. And the structural break it was calibrated on is exactly what `wire_indicators` predicts, `tools/gscript.py:1766-1768`: *"…extend an unrelated wire instead → **'This wire connects more than one data source'** and the target breaks."*

**2b — a concrete non-type mechanism.** Wire 10799 is not an ordinary wire: `docs/camera-acquisition-facts.md:178` shows it is **`CaseStructure #10407`'s t0 selector wire**, terminating on a *structure border sink*. `tools/gscript.py:2415`: *"an already-wired **SINK is not safe (LabVIEW re-routes and the VI breaks)**."* If WI's branch re-`Connect Wire`s over that net, the re-route breaks it structurally — and the fingerprint is identical: target `.Wire` = 10799, count unchanged, ExecState 0, `Is Broken?` True. **This run does not distinguish the two.**

**2c — your specific question: can a same-diagram branch inside a While loop break structurally?** On the measured facts, **no**, and the run's own gate is why: `#637` reads 59 terminals / 48 wired before and after (`:81`,`:89`,`:92`) — no tunnel, no border object. Both endpoints owned by `Diagram #639`. A control terminal inside a While loop is legal LabVIEW. I will not invent a rule that forbids it. Two things are left *open* rather than excluded: the terminal was placed at **(120, 4000)** and the run never read `#637`'s bounds or the terminal's post-move position (an object owned by a diagram but drawn outside its frame is an inconsistent state, and I found no NI source saying `Move` clips or auto-grows); and **`#10407`'s wired-terminal count was never taken** — the one node at the far end of the wire under test, and wired-terminal counts are the only cut detector `docs/cycle27-plan.md:1101` accepts.

**2d — `wire_err: 1055` at `:51`: no, it does not matter.** `tools/gscript.py:829-830` documents it: *"0 when the terminal is bare (then `wire_err == 1055` and `term_err == 0`)"*. It is LabVIEW's generic *"Object reference is invalid"* from reading `Connected Wire` off a bare terminal. Row `:74` still shows it after the move, correctly. Drop it. ⚠️ Do not conflate it with the *other* 1055 in this op family — `tools/gscript.py:2378-2380` records 20 `OpCreate{Control,Indicator}_v0.vi` calls whose dialogs said 1055 while the wrapper reported success. Different thing.

**2e — I am not disputing the type mismatch.** `docs/camera-acquisition-facts.md:189-191` traces `#10686 'x .and. y?'` to `#3057 'x = 0?'`, so the source is Boolean — established **independently of this run**. (The run never measured it; LabVIEW's And is polymorphic and goes bitwise on integers, so the terminal name alone proves nothing.) The mismatch is real *and was in the docs before the script ran*. It is not a finding of this run; it is a design fault of this run, and calling it "the only thing that failed" inverts that.

## 3. What would falsify the claim

1. Repeat create → `move_in` → **stop**; `g.save()` fails at ExecState 1, **or** the saved file reloads with `owner_of(#23541) != ('Diagram', 639)`, or at ExecState 0.
2. Identical route, branch onto a **type-matched** sink, and ExecState still goes 0.
3. `#10407`'s wired-terminal count changes across `wire_indicators`, or wire 10799 ends with a terminal set other than `{#10686 t0, #10407 t0, #23541}`.
4. Re-run `wire_indicators` with a deliberately **wrong** `diagram_index` and `'index'` still resolves.

## 4. Cheapest discriminating test — and the type answer

**Can any existing verb make an indicator of a chosen type? No.** `create_indicator` is `Terminal.Create Indicator` 6349C02 (`tools/gscript.py:2388-2390`) — type comes from the donor terminal, no type argument. The **only** node-creation verb is `build_index_array` (`:2322`), one class only. And `node_info`/`create_indicator` address **top-level** `Nodes[]` only (`:2467`, *"Sub-diagram nodes are not listed"*) — which is why 46(a) exists. So reachable types today = an Index Array's terminals: `index` (numeric). Boolean is reachable only by wiring the Index Array's `array` input first with `connect_terminals` (`:2326-2328`) to retype `element` — which needs a Boolean-array source on the **top-level** diagram that nobody has shown exists. **So "just create one of the RIGHT TYPE" is not free, and "no new op VI is needed" is unestablished.**

**Arm A — the test that matters. Same script, delete PHASE 5, add the save.** create → `create_indicator` → delete IA → `move_in` (position chosen from `#637`'s *measured* bounds) → purge junk Invoke → ExecState → **`g.save()`** → close LabVIEW → reopen → re-read `owner_of`, ExecState, census, panel row. Strictly *shorter* than the run being reviewed, and the only version that can leave the artefact the standing rule demands. Add two free reads: `#637` bounds, and `#10407` wired-terminal count before/after.

**Arm B — only if A passes.** On the *reloaded* file, branch onto a type-matched sink. Note `docs/NAMES.md:912-921`: the `Is Broken?` read itself perturbs the target and the mechanism is **OPEN** — treat any post-read ExecState as suspect, never put it on a success path.

**Arm C — 30 seconds, answers §5.** Re-run `wire_indicators` for `'index'` with `diagram_index=0` while the terminal sits on Diagram 639. If it still resolves, `index 2` never scoped the lookup and "found it at the nested diagram's live index" means something other than what the claim says.

## 5. Is the 5001 story closed? **No — three independent reasons**

1. **Different failure stage.** 5001 here is a *name-lookup* failure and it is **swallowed** — `tools/gscript.py:1773`, *"a swallowed 5001 (bad name) is still a silent no-op."* Cycle 56's 5001s were WI failing to **resolve** `'File # Saved'` and `'Image'`. This run failed at the **post-condition** check (`:1794-1797`) on a label that resolved fine and was verified unique the same run (`:55`,`:57`). The 5001 path was never exercised.
2. **Different population.** `'File # Saved'` (uid 6) and `'Image'` are **pre-existing, already-wired** panel objects. `create_indicator` cannot produce them; relocating them means `move_in` on a *wired* terminal — and `docs/cycle27-plan.md:1093-1100` is red-flagged: **`move_in` severs every wire on the moved node** (`#3529` 1→0 wired, `#48` 7→0, w4833 left with zero terminals). `#23541` had **zero** wires, so this run exercised the one case where that hazard cannot appear.
3. **The fleet is blind to the rest of the dependency.** `tools/gscript.py:830`: *"locals and Value property nodes are not seen here."* Replacing uid 6 changes its identity while nothing in this fleet can observe whether a local or property node still reads it.

## If I am wrong

Show me a **saved and reloaded** VI in which a top-level-created `ControlTerminal` `move_in`-ed to a nested diagram survives with `owner_of == ('Diagram', 639)` and ExecState 1. I found none in `docs/`, `tools/bench/` or the plans, and `docs/cycle27-plan.md:1099-1100` says the save has always been refused. Produce that file and the transport route is sound — §4's type finding and §5's three reasons still stand independently.

**Sources:** [NI — Error 1055 from a Property or Invoke Node](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE) · [NI — Manipulating Data Bitwise](https://www.ni.com/en/support/documentation/supplemental/06/manipulating-data-bitwise.html) · [NI — Polymorphic Functions](https://www.physik.uzh.ch/local/teaching/SPI301/LV-2015-Help/lvconcepts.chm/Polymorphic_Functions.html)

## Sources

(extract from answer)

## What was done with it

**RECORDED, NEITHER ACCEPTED NOR REJECTED (Pre-decided 41(b)). NOTHING IN IT WAS ACTED ON.** This is a material
session (cycle 57 dispatch 3); accepting or rejecting a review is a judgement act and is not taken here.

Why it was dispatched: gate `P5a` of `tools/bench/diag_s57_ctmove_wire.py` predicted an EMPTY error column from
`wire_indicators` and measured `RuntimeError: wire_indicators: target BROKEN after wiring …`
(`tools/bench/diag_s57_ctmove_wire.log:83-84`; the run ended `BGRUN END rc=1 after 123s`, GATES 27 pass / 2 fail,
failing `P5a` and `P6`). A failed prediction, so CLAUDE.md §5 and `tools/hooks/guard_peer.py` require the review
before any next build. `-Agent claude -Role hypothesis` (opus / effort max / web), **ANSWERED 568 s, `$3.7974`**,
in 16 / out 44,946 / cache-create 227,327 / cache-read 708,732, 18 turns; `BGRUN END rc=0 after 569s`, log
`tools/bench/peer_c57_transport_typebreak.log`. Dispatched under `bgrun`, never `.vi`-attached.

Its verdict in one line: **`REFUTED on the load-bearing half`** — it does NOT dispute the type mismatch
(`docs/camera-acquisition-facts.md:189-191` already traced `#10686 'x .and. y?'` to `#3057 'x = 0?'`, so the
Boolean source was known BEFORE the run), but it refuses the inference "therefore the transport is proven and the
5001 story is closed", on four grounds: (1) the run held a saveable artefact at `:70` (`ExecState 1` right after
the move) and spent it on a connection that could have been predicted to break, so the one measurement that would
prove transport soundness — a SAVED, reloaded file — was never taken; (2) `Is Broken?` is a one-bit detector with
sensitivity but no specificity (`docs/NAMES.md:908-909` calibrates it `True` on a TWO-SOURCE wire too), and
`tools/gscript.py:1766-1768` predicts exactly that structural break for `wire_indicators`; (3) a concrete non-type
mechanism it names — wire 10799 is `CaseStructure #10407`'s **t0 selector** wire terminating on a structure-border
sink (`docs/camera-acquisition-facts.md:178`), and `tools/gscript.py:2415` records that an already-wired SINK is
not safe because LabVIEW re-routes and the VI breaks, giving a fingerprint identical to the one observed; (4)
`1905 -> 1905` is not evidence, because `docs/cycle27-plan.md:1101-1105` already records in red that a wire count
can never detect a cut. It answers two of the brief's sub-questions squarely: `wire_err: 1055` on the bare
terminal is the documented bare-terminal signature (`tools/gscript.py:829-830`) and **does not matter**; and a
same-diagram branch inside a While loop does **not** break structurally on these facts (`#637` 59/48 unchanged),
though it flags two unread quantities — `#637`'s bounds versus the terminal's post-move position (120, 4000), and
`#10407`'s wired-terminal count, never taken. On the type question it answers: **no existing verb can create an
indicator of a CHOSEN type** — `create_indicator` is `Terminal.Create Indicator` 6349C02 with no type argument,
`build_index_array` is the only node-creation verb, and top-level `Nodes[]` is the only addressable head, so the
reachable type today is the Index Array's numeric `index`. It proposes three arms (A: the same script minus
phase 5, plus the save and a cold reopen; B: a type-matched sink on the reloaded file; C: a 30-second re-call at
`diagram_index=0` to test whether the index scoped the lookup at all) and says the 5001 story is **not** closed,
because this run never re-attempted `'File # Saved'` (uid 6) or `'Image'`.

**None of that was acted on.** No arm was run; nothing was re-run; `tools/bench/diag_s57_ctmove_wire.py` was not
edited after the run; `allow_broken` was not set and no save was forced; no op VI was built; `gscript.py` was not
patched; `docs/cycle27-plan.md` and `docs/NAMES.md` were not edited and Pre-decided 46 stands as written; STATUS's
`## NEXT` was not touched. Whether to adopt arm A (and with it the judgement that this cycle's artefact-less
outcome must be repaired before another wiring attempt), how to weigh mechanism (3) against the type reading, and
what either implies for 46(d)'s candidate order, are judgement's calls and are returned as `OPEN:` lines.
