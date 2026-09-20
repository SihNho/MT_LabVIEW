# c56-transport-verbs-unreachable

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.1928  in 30 / out 46445 / cache-create 201481 / cache-read 1868318  (598s, 31 turn(s))
- **date:** 2026-09-20 22:02:32
- **outcome:** ANSWERED (600s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Failed prediction, cycle 56: REFUTE this claim

A diagnostic (`tools/bench/diag_s56_transport2.py`, log `tools/bench/diag_s56_transport2.log`, `BGRUN END rc=1
after 102s`, 13 gates pass / 5 fail: `L1`, `L2`, `I0`, `I1`, `I2b`) predicted that at least one of two transport
constructions would succeed on a scratch copy of the project's main VI. Both failed. The claim written from that
failure is below. **Your job is to REFUTE it**, not to confirm it. Attack the framing first, the details second.

## THE CLAIM UNDER ATTACK (attack it; do not agree with it)

> "With the op fleet as it stands, neither of the two transport constructions Pre-decided 45(c) needs is reachable,
> so a new op VI is unavoidable:
> (i) no verb can create a front-panel object on the main VI — `create_indicator` / `create_control` address
>     `VI -> Block Diagram -> Nodes[]`, which reads EMPTY on this VI, and `New VI Object`'s style input is a typed
>     ring that scripting cannot retarget (`docs/stage2-assembly-step-b.md:34`);
> (ii) no verb can place a Local Variable or write `Local.Control Name` (property ID 6355400) — there is no generic
>     property writer in `tools/gscript.py`, only `set_index_mode`, `set_auto_error_handling`, `set_node_label`;
> (iii) `wire_indicators` — the remedy `docs/NAMES.md:280-282` names for reaching inside a structure — returns
>     `error 5001 ... Control File # Saved not found` for an indicator the SAME RUN read on the SAME VI, so the one
>     verb that addresses a panel object by label does not work here."

## EVIDENCE — read these files yourself (read-only; you have Read/Glob/Grep and web search)

- `tools/bench/diag_s56_transport2.log` — the 5 failing gates. Key lines: `:42-44` (`node_info(max_n=40)` returned
  `[]`; `node_terms_uid(target, 0, i)` read `node_uid 0` for i=0,1,2), `:46-47` (gate P1: the same call now raises
  `RuntimeError: run blocked behind a modal dialog`), `:56` (the 5001 `wire_indicators` failure).
- `tools/bench/diag_s3a_ind_transport.log` — the earlier run: `create_indicator` returned an EMPTY ControlTerminal
  list on 20 consecutive calls with `exception None`; watchdog screenshots showed
  `Error 1055 ... Object reference is invalid` raised inside `OpCreateIndicator_v0.vi`'s own Property Node.
- `docs/NAMES.md:278-282` and `docs/NAMES.md:474-475` — the documented scope of the four verbs and the
  `wire_indicators(... node_class='Function', diagram_index=frame)` remedy.
- `docs/toolkit-capabilities.md` — the full op/verb inventory (108 `Op*.vi` exist in `claudeDev`).
- `tools/gscript.py` — the Python wrapper layer (`create_control` ~:2360, `create_indicator` ~:2385,
  `connect_terminals` ~:2407, `connect2` ~:2633, `wire_indicators`, `set_index_mode`, `set_node_label`).
- `tools/bench/diagram_tree_main.json`, `tools/bench/main_vi_nodeterms.json` — the VI's diagram/node census:
  626 real nodes on 169 structure-owned diagrams; diagram `"0"` holds no real node.

## ALREADY RULED OUT (do not propose these three)

1. The top-level `create_indicator` route was tried and hit the EMPTY `Nodes[]` (20 calls, error 1055 in the
   screenshots) — proposing "just call `create_indicator` on the VI" is not an answer.
2. `connect_terminals` / `connect2` both require a TOP-LEVEL end (Pre-decided 42(f)); the target terminals live on
   `Diagram #686`/`#639`, which are not the top-level diagram.
3. Tunnelling between the two loops is banned BY NAME (Pre-decided 38(g)): it would make autofocus run once after
   acquisition instead of per schedule tick, which is a rule-1a (computation-preserving) violation.

## WHAT TO ANSWER, in this order

1. **The strongest reason the claim is WRONG.** Be concrete and cite a file:line.
2. **Any EXISTING verb in our own inventory** (`docs/toolkit-capabilities.md`, `tools/gscript.py`, the 108
   `Op*.vi`) that (a) reaches a front-panel TERMINAL that sits inside a structure, or (b) COPIES / DUPLICATES an
   existing object. Relevant fact: the VI already holds **8 `Local` objects** — uids 2991, 4277, 11574, 3160, 3097,
   2143, 16942, 25805, every one with owner `Diagram`. If duplicating one of those is reachable with an existing
   verb, say exactly which verb and which LabVIEW method/property it wraps.
3. **The likeliest cause of the `error 5001 ... Control File # Saved not found`** given that the control provably
   EXISTS (the same run's `panel_wiring` read it on the same VI in the same phase, panel row 7, uid 6, wire 0).
   Consider at least: label string mismatch (leading/trailing whitespace, embedded newline, case), the label being
   the CAPTION rather than the LABEL, the indicator being inside a tab/cluster so its lookup name is qualified,
   `Wire Indicators.vi` searching only the top-level diagram's terminals, and a stale/unsaved panel state.
4. **An ALTERNATIVE EXPLANATION of the whole failure pattern** that does not end in "a new op VI is unavoidable".
5. **What would FALSIFY the claim**, and **the cheapest discriminating test for each** of (i), (ii), (iii) —
   each test must be runnable as a read-mostly diagnostic on a scratch copy, and must name the specific verb,
   argument and expected reading.

Answer in plain prose with file:line citations. Do not propose running hardware; the rig is ASSEMBLED.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is not supported by the run that produced it.** Three of the five failing gates cannot bear the weight put on them, and the one genuinely new machine reading (the 5001) has a cheaper explanation than "the verb does not work here".

## 1. The strongest reason the claim is wrong

**Gates L1 and L2 made zero calls.** `tools/bench/diag_s56_transport2.log:24-27` says so twice, verbatim: *"Building one is a NEW OP VI, which this brief forbids (Pre-decided 2). **0 calls were made.**"* Those two gates did not measure reachability — they read the op inventory and restated the brief's own prohibition. A gate whose FAIL is produced by a policy in its own prompt is not evidence about the machine, and the conclusion "neither transport construction is reachable" rests on it for half its content.

The other half is worse than un-measured: it is measured against a documented workaround that was never tried. `docs/NAMES.md:474-475` already states that `create_indicator`/`create_control` cannot reach nodes inside frames, and `docs/NAMES.md:476-478` gives the fleet's answer for exactly the case at hand — **a front-panel object with no node to hang it on**: *"`build_index_array` (unwired IA) → `create_control` on its `index` terminal (label `index`, I32) → delete the IA → the control stays on the pane, unwired, VI runnable."* The same trick is recorded as **proven** a second time at `docs/stage2-assembly-step-b.md:49-50` (`create_control` on `Get Controls.vi`'s `Control Names` terminal, helper node then deleted, *"gate: the control persists by UID"*). The top-level `Nodes[]` being empty is a starting condition the fleet already knows how to remove — `build_index_array` (`tools/gscript.py:2322-2345`) puts a node on the top-level diagram in one call. I0/I1 swept an empty array twenty times instead.

And the claim's own citation, read in full, says the opposite of what it is quoted for. `docs/toolkit-capabilities.md:274` reads *"creating front-panel objects **from nothing** | no op. `create_control` / `create_indicator` work **from a node terminal**"* — a statement about free-standing creation, not about this VI. Meanwhile `tools/gscript.py:1406-1412` contradicts `docs/stage2-assembly-step-b.md:34` outright: *"'the fleet cannot create front-panel objects' is a statement about THIS FLEET, not about LabVIEW … We never built that op because the ring's style codes were unreadable; `RingConstant.Strings And Values[]` (confirmed 2026-09-01) **removes that blocker**."* The diag log calls `stage2-assembly-step-b.md:34` a measurement (`:24` "measured why"); that line is a **peer review's opinion** (*"The review killed B0"*), with no measurement cited, and a 2026-09-03 note in the code says its premise expired.

## 2. Existing verbs the claim missed

**(b) Copying / duplicating — two of them.** `copy_into(donor, label, target)` (`tools/gscript.py:1399-1445`) copies any GObject by label across VIs; its docstring states its original purpose was *"to give an Op an `error out` indicator"* — i.e. this verb's demonstrated job is transplanting a **front-panel indicator** into another VI. `copy_by_index(donor, cls, index, target)` (`:1479-1558`) is the by-index copier, and it wraps `GObject.Move` with **`duplicate` = True** (`:1527`, `vi.SetControlValue(lab["duplicate"], True)`); the class is a free string (`:1526`), so `cls='Local'` is a legal argument **today**, against the 8 Locals at Traverse indices 0–7 (`diag_s56_transport2.log:23`). Donor and target only have to be different files (`:1510`), and `D1_s2_loops.vi` and the scratch are byte-identical copies (`:14`, `:35`) — the call is available as the files sit.

**(a) Reaching a terminal inside a structure — already built and already probed.** `move_in(target, uid, dest_diagram_index, position)` at `tools/recipes/build_d1_v0.py:318` relocates an object **by UID** into any diagram (`Class Name`="Diagram", `index`=dest), lifted *"verbatim"* from `probe_move_ctlterm_v0.py:160-178` — a probe whose name is literally "move a ControlTerminal". `owner_of` (`:338`) reads which Diagram owns a given uid and `diag_index` (`:357`) converts that uid to the Traverse index the ops want; `tools/recipes/build_d1_routeb_v0.py:448` records the measured fact *"a ControlTerminal's Owner is its DIAGRAM (measured, `probe_move_ctlterm_v0.log:47`)"*. The previous diag even ran a route called **"B-movedin (move_in first = True)"** (`diag_s3a_ind_transport.log:63`), so the session knew. Add `move_out` (`tools/gscript.py:2677-2689`, `GObject.Move` with owner = `VI.Block Diagram`) and `build_invoke`/`build_property`, both of which already take a `diagram_index` (`:2159`, `:2194`) — node placement inside a structure is not the gap.

**On (ii) specifically, the property the claim names is not on the critical path.** LabVIEW creates a local from the control itself: `Control` class method **Create:Local Variable, ID 6331C02**, *"Creates a local variable for the control and returns a reference to it"*, LabVIEW 2018+, **no scripting-licence authentication** ([LabVIEW Wiki](https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method)). The Local is born bound, so `Local.Control Name` 6355400 never has to be written, and `New VI Object`'s style ring is not involved. If an op is ultimately needed it is one Invoke node via `build_invoke(cls="VI Server:Control", method_id="6331C02")` — the fleet's routine construction, not the open-ended "new op VI" the claim implies.

## 3. The 5001 — most likely a wrong argument, not a broken verb

NI reserves **5000–9999 for user-defined errors and guarantees no NI product returns a code in that range** ([Ranges of LabVIEW Error Codes](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/ranges-of-labview-error-codes.html)). So 5001 is erdosmiller's *own* "name not found" code — this project documents the sibling at `.claude/skills/labview-automation/references/com-driving.md:140` (*"`Get Outputs.vi` fails with error 5001, 'Output &lt;name&gt; not found'"*).

The decisive fact is the library's scope, and it is recorded only in `archive/` (I opened it because the active doc states the remedy without the contract — that is itself a doc defect). `archive/2026-08-29-status-sweep-opexitloop-opwireind.md:33-35`, Context Help read off the machine: *"Outputs is an array of terminals to wire to the input terminals of the indicators selected with `Indicator Names` **on Diagram in**."* `tools/gscript.py:1787-1788` feeds `Diagram in` from `Class Name 2 = "Diagram"`, `index 2 = diagram_index`. The failing call passed **`diagram_index=46` = Diagram #639, the loop body that owns the *source* node** (`diag_s56_transport2.log:49`). The successful uses at `docs/NAMES.md:470-473` omit `diagram_index` — i.e. **0, the top-level diagram**, where the pane indicator's terminal lives. So the library did exactly what it documents: it searched the diagram it was handed. `docs/NAMES.md:280-282` is the trap — it presents `diagram_index=frame` as the way to reach *inside a structure*, when that argument scopes the **indicator lookup**, not the source (the source is already addressed by the Traverse index, `Function[102]`).

Ranking the brief's candidates: (1) **wrong `Diagram in`** — best supported, explains everything, costs one repeat call; (2) **label-string mismatch** — a live class here, not hypothetical: `archive/2026-09-17-status-d1-route-a-run9.md:23` and `archive/2026-09-17-status-d1-full-build-4.md:74` record **six** 5001s from `Get Controls.vi` on this same VI with *"2 names carry newlines"*, `archive/2026-08-31-status-full-assembly-narrative.md:869` records *"the single-line spelling 5001'd; second confirmed two-line label"*, and `docs/d1-build-plan.md:762` still carries it as an **open** question. The run had a verbatim label reader in hand (`diag_s56_transport2.log:21-22`, uid 34200 read *"(VERBATIM, repr)"*) and took the test string from a JSON file instead (`:54`); (3) caption-vs-label and tab/cluster qualification — possible but weakened, since `panel_wiring` walks `Panel.Controls[]` and is explicitly *"Not recursive: tab pages / cluster elements are not rows"* (`tools/gscript.py:834`), yet lists `File # Saved` as a row. Note that "the same run read it" proves the **control** exists on the **panel**; the library needs its **terminal** on the **diagram** it was given. Different object spaces — that mismatch is the whole error.

## 4. Alternative explanation of the whole pattern

**This is an addressing failure, not a capability gap.** Every verb that failed was pointed at the wrong address space on the first VI whose 626 nodes all live inside 169 structure diagrams: `create_indicator` at a top-level `Nodes[]` the VI genuinely leaves empty, `wire_indicators` at a diagram that does not own the indicator's terminal. The three tools that fix exactly this — manufacture a top-level node (`build_index_array`), find the owning diagram (`owner_of`/`diag_index`), relocate an object into a chosen diagram (`move_in`) — are on disk, were written for this VI, and none was called. A second reading, less charitable and also consistent: the run was built to confirm a conclusion its brief already contained (Pre-decided 2), which is why the two gates about reachability are phrased as inventory questions and answered without touching LabVIEW.

## 5. Falsifiers and the cheapest discriminating tests

**Cheapest overall — run this one first (≈3 calls, no new op, read-mostly):** repeat the identical `wire_indicators` call with `diagram_index` = `diag_index(target, owner_of(target, 6)[1])` instead of 46. Read first: `owner_of(scratch, 6)` → expect `('Diagram', <uid>)`; if that uid is the top-level diagram the construction implies a loop tunnel and is disqualified by 38(g) *on semantics, not on capability* — which by itself refutes (iii)'s framing, since Test I was probing a route route-L does not need. **Falsifies (iii)** if the 5001 disappears (any other outcome, including a broken wire, is a different finding).

**(i) falsified if** a front-panel indicator appears on a copy of the main VI with existing verbs. Test: `build_index_array(scratch, (100,100))` → `node_info(scratch, max_n=40)` (predict: 1 entry where `:42-43` read `[]`) → `create_indicator(scratch, 0, 2)` (predict: 1 new ControlTerminal and a non-empty label; `create_control(scratch, 0, 1)` gives the I32 `index` variant) → `delete_object(scratch, 'IndexArray', ...)` → `exec_state` 1 and the ControlTerminal count 114 → 115. The claim predicts the census stays empty or the creation is refused.

**(ii) falsified if** `copy_by_index(D1_s2_loops.vi, 'Local', 0, <scratch>)` returns a non-empty `added` and the `Local` count goes 8 → 9 (`diag_s56_transport2.log:23` is the before-reading). Cheap precursor, pure read: for each of the 8 Locals, `owner_of` → `diag_index` → `node_terms(scratch, diag, node)` and print the terminal name — on a variable node the terminal name is the bound control's name (`tools/gscript.py:873` already handles the global-variable case). **If any of the 8 is already bound to `current image number`, route L needs no new op at all**, and that is a read-only question the run never asked.

**What the evidence does not settle, and I will not pretend it does:** whether a duplicated `Local` keeps its donor's binding across the copy protocol; whether `build_index_array` behaves on a 475 KB VI with 169 diagrams (it has only been used on small VIs); and where `File # Saved`'s ControlTerminal actually lives. All three are single reads.

**What would change my mind:** the (i) test failing with a machine-side refusal (a real 1055 from `build_index_array` or from `create_indicator` on a non-empty `Nodes[]`), plus the Local-binding read showing no reachable route and `copy_by_index(cls='Local')` erroring. Then "one new op, `build_invoke` with 6331C02" would be the honest conclusion — which is still a much smaller claim than the one under review.

Sources: [Ranges of LabVIEW Error Codes](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/ranges-of-labview-error-codes.html) · [Control class/Create.Local Variable method — LabVIEW Wiki](https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method) · [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)

## Sources

(extract from answer)

## What was done with it

**RECORDED IN FULL, NEITHER ACCEPTED NOR REJECTED — Pre-decided 41(b). Cycle 56 material dispatch #4, 2026-09-20
22:0x. NOTHING WAS ACTED ON:** no gate redesigned, no measurement rebuilt, nothing re-run, no op built, no
`diagram_index` changed, `tools/gscript.py` not touched, no `.vi` opened and no COM call made in this dispatch.
The exchange exists because `guard_peer.py` blocked the next build over `tools/bench/diag_s56_transport2.log`'s
five failing gates (`L1`, `L2`, `I0`, `I1`, `I2b`); it is now archived, ANSWERED, newer than that log, from
`-Agent claude -Role hypothesis` (opus / effort max / web), and it names the log, so the D3 conditions are met.

**Its verdict, in its own order, recorded as claims about our files — not as facts about the machine:**

1. **The claim is judged unsupported.** `L1` and `L2` "made zero calls" (`diag_s56_transport2.log:24-27`, quoted
   verbatim by the reviewer), so those two FAILs restate the brief's own Pre-decided 2 prohibition rather than
   measure reachability.
2. **A documented workaround was never tried:** `docs/NAMES.md:476-478` — `build_index_array` (unwired IA) →
   `create_control` on its `index` terminal → delete the IA → the control persists, VI runnable; recorded a second
   time as proven at `docs/stage2-assembly-step-b.md:49-50`. `build_index_array` is `tools/gscript.py:2322-2345`.
3. **Two of our own citations are read as saying the opposite of what they were quoted for:**
   `docs/toolkit-capabilities.md:274` is about creating panel objects *from nothing*, and `tools/gscript.py:1406-1412`
   says in writing that "the fleet cannot create front-panel objects" is a statement about THIS FLEET, with
   `RingConstant.Strings And Values[]` (2026-09-01) naming the style-ring blocker as removed — while
   `docs/stage2-assembly-step-b.md:34`, cited by the diagnostic as a measurement, is a peer review's opinion.
4. **Existing verbs it names, unverified on this target:** `copy_into` (`tools/gscript.py:1399-1445`, copies a
   GObject by label across VIs, original purpose transplanting an `error out` INDICATOR); `copy_by_index`
   (`:1479-1558`, wraps `GObject.Move` with `duplicate = True` at `:1527`, class a free string at `:1526`, so
   `cls='Local'` is a legal argument today against the 8 Locals); `move_in` (`tools/recipes/build_d1_v0.py:318`,
   relocates by UID into any diagram), `owner_of` (`:338`), `diag_index` (`:357`), `move_out`
   (`tools/gscript.py:2677-2689`), and `build_invoke`/`build_property`, which already take a `diagram_index`
   (`:2159`, `:2194`).
5. **On (ii) it redirects the route entirely:** `Control` class method **Create:Local Variable, ID 6331C02**
   (LabVIEW 2018+, no scripting-licence authentication, labviewwiki) makes the Local BORN BOUND, so
   `Local.Control Name` 6355400 never has to be written and `New VI Object`'s style ring is not involved.
6. **On the 5001 it offers a cheaper cause than "the verb does not work here":** NI reserves 5000–9999 for
   user-defined codes, so 5001 is erdosmiller's own "name not found"; `archive/2026-08-29-status-sweep-opexitloop-opwireind.md:33-35`
   records Context Help saying `Indicator Names` are looked up **on `Diagram in`**, which `tools/gscript.py:1787-1788`
   feeds from `diagram_index` — and the failing call passed `46` = `Diagram #639`, the body that owns the SOURCE
   node, not the diagram that owns the indicator's terminal. Its ranking: (1) wrong `Diagram in`; (2) label-string
   mismatch (it cites six earlier 5001s on this same VI with "2 names carry newlines" —
   `archive/2026-09-17-status-d1-route-a-run9.md:23`, `archive/2026-09-17-status-d1-full-build-4.md:74`,
   `archive/2026-08-31-status-full-assembly-narrative.md:869`, still open at `docs/d1-build-plan.md:762`);
   (3) caption/tab-cluster qualification, weakened because `panel_wiring` is non-recursive (`tools/gscript.py:834`)
   and still listed the row. It also draws the panel/diagram distinction explicitly: the run proved the CONTROL
   exists on the PANEL, while the library needs its TERMINAL on the DIAGRAM it was handed.
7. **Its alternative explanation of the whole pattern:** "an addressing failure, not a capability gap", plus a
   second, less charitable reading — that the run was built to confirm a conclusion its own brief already
   contained.
8. **Its three discriminating tests, recorded and NOT RUN:** (iii) repeat the identical `wire_indicators` call with
   `diagram_index = diag_index(target, owner_of(target, 6)[1])`; (i) `build_index_array(scratch,(100,100))` →
   `node_info(max_n=40)` (predicts 1 entry where the log read `[]`) → `create_indicator(scratch, 0, 2)` → delete the
   IA → `ControlTerminal` 114 → 115 with `exec_state` 1; (ii) `copy_by_index(D1_s2_loops.vi, 'Local', 0, scratch)`
   with `Local` 8 → 9, preceded by a pure-read pass asking whether any of the 8 existing Locals is ALREADY bound to
   `current image number`. Its own falsifier: an (i) test that fails with a machine-side refusal.
9. **What it says it cannot settle:** whether a duplicated `Local` keeps its binding across the copy protocol;
   whether `build_index_array` behaves on a 475 KB / 169-diagram VI; and where `File # Saved`'s ControlTerminal
   actually lives.

**Cost:** `$4.1928`, in 30 / out 46,445 / cache-create 201,481 / cache-read 1,868,318, 598 s, 31 turns; bgrun
`BGRUN END rc=0 after 600s`, log `tools/bench/peer_c56_transport_unreachable.log`.

⚠️ **Every item above is a HYPOTHESIS about our own tools, and two models agreeing is not confirmation
(CLAUDE.md §5).** Whether any of it is adopted — in particular whether the `wire_indicators` `diagram_index`
reading is right, whether `copy_by_index(cls='Local')` is attempted, and whether `create_indicator` after
`build_index_array` is worth one run — is a JUDGEMENT decision and is deliberately left undone here.
