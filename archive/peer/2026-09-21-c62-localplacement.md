# c62-localplacement

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.0227  in 14 / out 36707 / cache-create 169426 / cache-read 635072  (472s, 12 turn(s))
- **date:** 2026-09-21 10:52:19
- **outcome:** ANSWERED (474s)
- **why asked:** MANDATORY failed-prediction review (CLAUDE.md §5). `tools/bench/diag_c62_s3b_build.py` step 3 predicted `ExecState` 1 after the Local was wired into `#10407` t0; the machine read **0**, so the row stopped and nothing was saved (`tools/bench/diag_c62_s3b_build.log`, `BGRUN END rc=1 after 104s`, 20 pass / 5 fail).
- **verdict:** unverified

## Question

# Failed prediction: a Local Variable created by `VI.Create:Local Variable` lands on the TOP-LEVEL diagram, and wiring it into a sink inside a While loop left the VI broken

## The prediction (written before the run, `tools/bench/diag_c62_s3b_build.py` docstring, step 3)

> `connect_nested_v1(Local SOURCE -> #10407 tN SINK)` — **`ExecState` 1 EXPECTED here**; a bare source terminal
> and a bare indicator are both legal, so once the Case selector's sink is fed the VI is legal again, and that
> is the row's guaranteed saved artefact.

## What was observed (`tools/bench/diag_c62_s3b_build.log`, `BGRUN END rc=1 after 104s`, 20 pass / 5 fail)

The target is a copy of `claudeDev\D1_s3a_focus_ind.vi` (a working copy of a large acquisition VI; the ORIGINAL
is never touched). All numbers below are read off the machine in that run.

1. cold open `ExecState` **1**; `#637` (WhileLoop) **59 terminals / 48 wired**; `ControlTerminal` census **116**.
2. `delete_object(target,'Wire', idx of uid 10799)` → `gone [10799]`, `ExecState` **1 → 0**. That one Wire object
   was a three-terminal net: `#10407` **t0** (Case-structure SELECTOR, name `''`, sink) · `#10686` **t0**
   `'x .and. y?'` (`And`, SOURCE) · front-panel indicator control **23555** `'Automatic Error Handling'` (sink).
   All three are now bare.
3. `OpCreateLocalRead_v0.vi` with `Write?` = False, bound to front-panel row 115 (`'Automatic Error Handling'`,
   indicator): error cluster `(False, 0, '')`, `Local` census **8 → 9**, new Local **#23507**. Read back with
   `node_terms`: **ONE** terminal, NAME `'Automatic Error Handling'` (hex
   `4175746f6d61746963204572726f722048616e646c696e67`), `is_source` **True = READ** — the rule-1a gate PASSED.
4. 🔴 **THE LOCAL'S OWNER, READ OFF THE MACHINE: `TopLevelDiagram` #536, diagram index 0, `Nodes[0]`.** The sink
   `#10407` is `Nodes[24]` of `Diagram #639`, traverse index 46, and `#639` is owned by `WhileLoop #637`.
5. `connect_nested_v1(target, sink_diag=46, sink_node=24, sink_term=0, src_diag=0, src_node=0, src_term=0)`
   (drives `OpConnectNested_v1.vi`, `Terminal.Connect Wire` 6349C03 with two independent diagram ladders):
   **`wire_delta` 3, op error column `''`**, i.e. the write reported success and made THREE wire segments —
   LabVIEW created the border tunnels itself, as this op's own documentation says it does.
6. Readbacks: `#10407` t0 `wire 0 → 23508`, all four error columns 0. Local #23507 t0 `wire 0 → 23601`,
   all four error columns 0. **The two uids differ** — expected for a cross-boundary wire in several segments,
   so this is not by itself evidence of failure.
7. 🔴 **`ExecState` = 0 at the save decision, so nothing was saved and the working copy was removed.**
   `ExecState` timeline for the row: `1` (cold open) → `0` (after the wire delete) → `0` (after the Local was
   created, unwired) → **`0` (after the connect)**.
8. At the stop: `#10686` t0 `'x .and. y?'` wire **0** (`wire_err` 1055 = bare); panel control 23555 wire **0**
   (`wire_err` 1055 = bare); `#10407` t0 wire **23508**.

No `Wire.Is Broken?` was read at any point (it is measured to perturb `ExecState` in this project, so the ordered
pass is only ever run after a save; the row never reached a save).

## Already ruled out

- **Not the binding**: the Local's own terminal reads back with the exact label it was created from and
  `is_source` True (READ), which is the direction the sink requires.
- **Not a silent decline of the write**: `wire_delta` 3, op error `''`, and both ends report non-zero wires
  with zero error columns.
- **Not "the differing wire uids mean the wire is wrong"**: `OpConnectNested_v1`'s own record says a
  cross-boundary connection is several segments and the sink and source uids differ.
- **Not a perturbing read**: no `Is Broken?` call happened anywhere in this run before the reading.

## The claim you are asked to REFUTE

**CLAIM:** the `ExecState` 0 after step 5 is caused by the two OTHER terminals that the same Wire delete left
bare — the source `#10686` t0 `'x .and. y?'` and the front-panel indicator control 23555 — and NOT by anything
about the Local, the cross-diagram connection or the tunnels LabVIEW created; i.e. the sequence would read
`ExecState` 1 if the indicator were re-fed before the state is sampled.

Give the strongest reason this claim is WRONG. In particular:

- In LabVIEW, is an **unwired front-panel indicator terminal** on a block diagram a broken-VI condition, or a
  legal one? Is an **unwired output terminal of a primitive** (`And`'s `x .and. y?`) a broken-VI condition?
- Does wiring a **Local Variable that sits on the top-level block diagram** into a terminal **inside a While
  loop** through automatically created tunnels produce a legal VI at all, or does that construction itself have
  a defect (for example: a tunnel on a loop border whose other side is unwired, or a Local read that LabVIEW
  refuses to route across a structure border)?
- Is there an alternative explanation that fits ALL eight observations above better?

Name what would FALSIFY your explanation, and name the CHEAPEST discriminating test — one that can be run
read-only or on a throwaway scratch copy, with the verbs this project already has:
`delete_object`, `connect_nested_v1` (`OpConnectNested_v1.vi`), `wire_indicators` (`OpWireInd_v0.vi`, branches an
EXISTING indicator onto the wire already attached to a source terminal), `OpCreateLocalRead_v0.vi`,
`node_terms_uid`, `node_labels`, `panel_wiring`, `report_all`, `count`, `exec_state`.
There is no verb in this fleet that deletes ONE BRANCH of a Wire object, and `create_indicator` /
`connect_ctl` are both measured out on this VI (they address the TOP-LEVEL `Nodes[]`, which is empty here).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role (read-only peer), so the review is delivered here directly.

---

# Failed-prediction review — C62 S3b row 1

**Verdict: the claim is refuted at its premise.** Not "unlikely" — the cause it names cannot produce `ExecState 0` in this VI, and the run's own data proved that before the delete ever happened.

## 1. The strongest reason the claim is wrong

**The bed VI opens at `ExecState 1` with eleven bare terminals on the While loop alone.**

`tools/bench/diag_c62_s3b_build.log:19` — cold open `ExecState = 1`. Six lines later, `:25` — `#637: 59 terminals, 48 WIRED`. The table at `:24` names the eleven: indices 2, 20, 24, 28, 40, 43, 44, 46, 48, 51, 57, every one `'wire': 0, 'errs': [0,0,0,1055]` — the *identical signature* the brief uses to call the And output and the indicator "bare". Ten of them are `is_source True`. Indices 43 and 44 are the two sides of the **same** border object, **both** unwired — a completely dead tunnel — in a VI reading 1.

In this VI, on this reader, a bare terminal breaks nothing. The claim's mechanism is contradicted by evidence the run collected in its own first ten lines.

That matches LabVIEW: an unwired front-panel terminal is a **warning**, whose error-list text is "The terminal for this Front Panel control or indicator is unwired" ([NI forum](https://forums.ni.com/t5/LabVIEW/Unwired-Front-Panel-Terminal-Warnings/td-p/334343), [NI debugging docs](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html)). An unwired primitive **output** is legal; only an unwired **required input** breaks a VI ([NI, Block Diagram Explained](https://www.ni.com/en/support/documentation/supplemental/08/labview-block-diagram-explained.html)). That asymmetry is the entire story of step 2 — the Case **selector** is a required input, which is why the delete broke the VI. The other two ends never mattered.

Also: `1055` is *Object reference is invalid* — the reader failing to get a wire ref. The brief reads a reader's error code as a brokenness verdict.

## 2. The "already ruled out" list contains a statement the log contradicts

> *"Not a perturbing read: no `Is Broken?` call happened anywhere in this run before the reading."*

**False.** `diag_c62_s3b_build.log:51`, inside step 3, above the save point:

```
[op stdout]       op readback {'UID': 10407, 'Name': '', 'UID 2': 0, 'Is Broken?': False}
```

`docs/NAMES.md:903-905`: "`OpConnectNested_v0/v1` and `OpConnectFromWire_v0` **all carry the reader already**." The recipe never called `Is Broken?`; the writer op it called *contains* it.

`docs/NAMES.md:920-926` is a red-flagged rule from one cycle ago: **"NEVER READ `Is Broken?` ABOVE A SAVE POINT"** — cycle 61 built a correct op, read `Is Broken?` before finishing, read its save gate as `ExecState` **0**, threw the build away, and **the identical construction with the read moved below the save saved at 1 and reopened cold at 1**. Same signature, one cycle later, new recipe name.

Gate `Z_1e` — "no `Wire.Is Broken?` was read above any save" — **PASSED** (`:88`). It checks the recipe's own calls and is blind to the op's embedded property node, so it certified the exact condition that was violated.

## 3. Alternatives that fit all eight observations

**Alt-A — the `ExecState 0` is a poisoned reading, not a verdict.** Everything above, plus `NAMES.md:926-929` saying the mechanism is unsettled ("the connect itself, the property node's own execution, or a stale/uncommitted compile state; nothing here distinguishes them"). Externally corroborated: VI Server reporting "bad" for a VI that is not ([NI forum](https://forums.ni.com/t5/LabVIEW/VI-state-indicates-VIis-broken-when-it-is-not/td-p/374104), [LAVA](https://lavag.org/topic/16660-how-to-get-actual-vi-execution-state/)); scripting forces a recompile ([LabVIEW Wiki](https://labviewwiki.org/wiki/VI_Scripting)).

**Alt-B — the construction is genuinely defective, and the topology is deeper than the brief says.** `#637`'s owner is **Diagram #686** (`:23`), diagram index 19 — *not* the top level (#536 = index 0). Top-level → #639 crosses **two** structure borders, and `wire_delta` **3** (`:52`) is exactly three segments for two crossings. A legal result therefore needs **two new tunnels**, one on `#637` (59 → 60 terminals). If the connect instead hung the Local's source on an existing *output* tunnel's outside terminal — `#637` offers ten bare sources — the inner net gets two drivers, which `NAMES.md:935-939` measured as `Is Broken? True`, and `#637`'s count stays 59. Both ends would still report non-zero wires with zero error columns, exactly as at `:54` and `:56`. LabVIEW does auto-create the tunnel when `Connect Wire` crosses a border ([NI, Wiring Structures](https://www.ni.com/docs/en-US/bundle/labview/page/wiring-structures.html)); nothing guarantees it picked a *new* one.

**Checked and eliminated, so I am not offering it:** an orphaned tunnel from the delete. Wire 10799 appears nowhere in `#637`'s 59-terminal table (`:24`), and a Wire object belongs to one diagram — which is why this crossing needed three. Both the And (`:31`, Nodes[25]) and the Case (`:28`, Nodes[24]) sit on Diagram #639, so all three ends of 10799 were on #639 and no border object was orphaned.

## 4. What would falsify each

- **The claim dies** if `wire_indicators` re-feeds the indicator and `ExecState` still reads 0. The recipe's own step 4 (`diag_c62_s3b_build.py:29-32`) would have tested it — the stop-on-0 at step 3 fired first.
- **Alt-A dies** if a cold reopen of an unconditionally-saved copy reads 0.
- **Alt-B dies** if the post-connect `#637` census reads 60/50.

## 5. Cheapest discriminating test — one scratch run, existing verbs only

The run deleted the working copy and kept no step-3 artefact (`:70`), so nothing on disk can be read. On a throwaway copy of `D1_s3a_focus_ind.vi`, repeat steps 1–3 verbatim, then:

1. `node_terms_uid(#637)` — **this is the `<S>_k` gate that was written (`diag_c62_s3b_build.py:63`, "no tunnel, no border object") and never reached.** One read; it may settle everything.
2. **Save unconditionally**, dropping the `ExecState == 1` precondition (`…py:28`).
3. Restart LabVIEW, cold reopen, `exec_state`.

| `#637` after connect | cold `ExecState` | conclusion |
|---|---|---|
| 60 / 50 | **1** | **Alt-A** — always legal, the reading was poisoned. Claim wrong |
| 60 / 50 | 0 | genuinely bad wire despite tunnels; then `wire_indicators` + re-read — if *that* reaches 1, the claim was right |
| 59 / 48 | either | **Alt-B** — three segments, two borders, no border object |

## 6. Where the evidence does not decide

Between Alt-A and Alt-B **this run does not distinguish**, and I won't pretend otherwise. Alt-A has a measured in-project counterfactual but is not deterministic — the same op wired 63 route-B rows with `Is Broken? FALSE` throughout (`docs/d1-route-b-plan.md:84`). Alt-B is arithmetically consistent with `wire_delta 3` but rests on a census nobody took. What *is* settled is that the claim's own mechanism is dead.

## 7. The fix worth more than this row

Gate `Z_1e` must assert against the **op's readback**, not the recipe's call list. As written it will keep passing every time `OpConnectNested_v1` reads `Is Broken?` above a save — the failure class cycle 61 already paid for, recurring here under a new recipe name.

**Sources:** [NI — Unwired Front Panel Terminal Warnings](https://forums.ni.com/t5/LabVIEW/Unwired-Front-Panel-Terminal-Warnings/td-p/334343) · [NI — Debugging Techniques](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html) · [NI — Block Diagram Explained](https://www.ni.com/en/support/documentation/supplemental/08/labview-block-diagram-explained.html) · [NI — Wiring Structures](https://www.ni.com/docs/en-US/bundle/labview/page/wiring-structures.html) · [NI — VI state indicates VI is broken when it is not](https://forums.ni.com/t5/LabVIEW/VI-state-indicates-VIis-broken-when-it-is-not/td-p/374104) · [LAVA — How To Get Actual VI Execution State?](https://lavag.org/topic/16660-how-to-get-actual-vi-execution-state/) · [LabVIEW Wiki — VI Scripting](https://labviewwiki.org/wiki/VI_Scripting) · [NI — Broken run arrow with no errors](https://forums.ni.com/t5/LabVIEW/Broken-run-arrow-with-no-errors/td-p/456652?profile.language=en)

## Sources

(extract from answer)

## What was done with it

Written by the cycle-62 material dispatch #3 that asked the question. This is a MATERIAL session: it disposes
the review against the machine's record and does **not** decide the route. Four of the review's points are
checkable from the run's own log and are dealt with one by one; its proposed BUILD is deliberately not run.

**(1) ACCEPTED, AND IT KILLS THE CLAIM — a bare terminal does not break this VI, and the run proved it before
the delete.** Checked in `tools/bench/diag_c62_s3b_build.log:19` (cold open `ExecState` **1**) against `:25`
(`#637: 59 terminals, 48 WIRED` — eleven bare, the same `'wire': 0, 'errs': [0,0,0,1055]` signature the task
calls "bare"). The claim I wrote — *"ExecState 0 is caused by the two other terminals the Wire delete left
bare"* — is **REFUTED**, and the asymmetry the review gives (an unwired required INPUT breaks a VI; an unwired
primitive OUTPUT or front-panel terminal does not) also explains, consistently, why deleting wire 10799 took
`ExecState` 1 → 0 at all: `#10407` t0 is the Case structure's **selector**, a required input.

**(2) ACCEPTED AS A FACT ABOUT OUR OWN TOOLING, AND IT IS THE MOST COSTLY THING IN THIS REVIEW — an
`Is Broken?` READ DID HAPPEN ABOVE THE SAVE POINT, INSIDE THE WRITER OP.** Verified verbatim in this run's log,
`diag_c62_s3b_build.log:51`, printed by the op's own stdout during step 3:
`op readback {'UID': 10407, 'Name': '', 'UID 2': 0, 'Is Broken?': False}`. My task file's "already ruled out"
line — *"no `Is Broken?` call happened anywhere in this run before the reading"* — was true of the recipe's own
calls and **false of the run**, because `OpConnectNested_v1.vi` carries the reader internally. Gate `Z_1e`
("no `Wire.Is Broken?` was read above any save") PASSED at `:88` while that read had occurred, so **the gate as
written cannot see the condition it claims to enforce**. Recorded, not repaired: patching the gate (or the op)
is outside this dispatch's scope, which names one diagnostic and forbids new verbs and edits to
`tools/gscript.py`. It is carried to `OPEN:` for judgement, together with the review's §7.

**(3) ACCEPTED AS A GAP IN MY OWN ORDERING, NOT AS A DIAGNOSIS — the `#637` census that would separate the two
surviving explanations was written as gate `<S>_k` and never reached.** In `tools/bench/diag_c62_s3b_build.py`
the post-connect `loop637_counts` call sits AFTER the step-3 save decision, so the stop-on-0 fired first and the
count after the connect was never taken. The review's Alt-A (a poisoned `ExecState` reading) and Alt-B (the
connect hung the Local on an existing output tunnel instead of creating a new one, leaving `#637` at 59/48 and
the inner net with two drivers) are therefore **both still live, and this run does not separate them** — the
review says so itself in its §6 and I am not resolving it by argument.

**(4) NOT RUN, AND DELIBERATELY: the review's §5 discriminating test requires SAVING UNCONDITIONALLY, i.e.
dropping the `ExecState == 1` save precondition this dispatch was given.** That is a route decision, and the
brief is explicit that a step whose `ExecState` is not what the sequence expects STOPS the row with no second
construction. So no probe, no re-run, no cast, no splice, no patch was made on the strength of this review.
Its one-read half (`node_terms_uid(#637)` immediately after the connect, before any save decision) is the
cheapest part and is carried to `OPEN:` as the measurement judgement may want next; this session did not take
it, because taking it means re-running the construction the brief stopped.

**(5) RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)):** the review's topology claim that `#637`'s owner is
`Diagram #686` (index 19) and that a top-level → `#639` connection therefore crosses **two** structure borders,
which it reads as consistent with the measured `wire_delta` **3**. The `wire_delta` is measured
(`:52`); the two-border reading is the review's inference from a line of this run's own diagram output and was
not independently re-measured here.

**(6) RECORDED FOR THE RETROSPECTIVE, NOT SELF-ADJUDICATED:** the review's §2 asserts this is the SAME failure
class cycle 61 paid for (`docs/NAMES.md:920-926`, "never read `Is Broken?` above a save point"), recurring under
a new recipe name. Whether that is `repeated-failure-class` is the retrospective's call, not this session's.
