# c58-delete-execstate0

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.6322  in 24 / out 29707 / cache-create 202637 / cache-read 1589576  (379s, 23 turn(s))
- **date:** 2026-09-21 00:27:18
- **outcome:** ANSWERED (381s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this claim. Do not confirm it.

## The failed prediction

`tools/bench/diag_s58_boolcarrier_run1.log` (`BGRUN END rc=1 after 229s`, 51 pass / 9 fail) predicted gate
`B3b ExecState after the delete == 1` and measured **0 on all three candidates** (log lines 79, 158, 237). The
same three-gate pattern repeats per candidate: `B3b` 0, then `B4d` 0 after the `move_in`, then `B5` no save.
No candidate reached the wire test, so the run's actual question — which builder gives a BOOLEAN-typed carrier —
is unanswered.

## The claim under attack

> **Cause:** `delete_object` on the `Property` carrier leaves a DANGLING WIRE — the wire that
> `Terminal.Create Indicator` had just made between the carrier's Boolean output terminal and the new front-panel
> indicator — and a broken wire holds the VI at `ExecState` 0.
>
> **Why the Index Array carrier did not do this** (cycle 57, `tools/bench/diag_s57_typepair.log`, 35 pass / 0
> fail): the indicator there was created from `IndexArray.Terminals[2]`, the `index` **input** terminal, while
> this run followed its own selection rule and created from a **SOURCE** terminal (`PanelLoaded` / `Def Err
> Handling` / `Broken?`).
>
> **Evidence offered:** C1's new panel row read `'wire': 23586` while the carrier still stood
> (`diag_s58_boolcarrier_run1.log:71`), and after the `move_in` the same row read `'wire': 0, 'wire_err': 1055`
> (`:97`) — i.e. a wire existed, then the terminal ended up with none, while `ExecState` stayed 0 throughout.
>
> **Remedy asserted to be correct, sufficient and NOT a design change:** call
> `gscript.remove_bad_wires_scripted(target)` (`tools/gscript.py:2486`, `VI.'Block Diagram:Remove Bad Wires'`
> 410 via `OpRemoveBadWires_v0`) ONCE, immediately after the delete, only when the delete left `ExecState != 1`.
> The justification for calling it "not a design change" is that `delete_object`'s OWN docstring prescribes it in
> writing at `tools/gscript.py:2242-2243`: *"Wires attached to the object are left broken: call
> remove_bad_wires() afterwards if the VI must run."*
>
> **Consequence asserted:** with that one step added and nothing else changed, run 2 will reach `ExecState` 1,
> save the artefact at the legal point (rule 47(e)), and the wire test will run; and the created indicator will
> still carry the carrier terminal's BOOLEAN type, because a front-panel indicator's type is fixed at creation
> and does not depend on its source wire surviving.

## What you must do

1. The **strongest reason the claim is wrong**. Is "dangling wire" actually established by this log, or merely
   consistent with it? Could `ExecState` 0 have a different cause that `remove_bad_wires` cannot touch — an
   orphaned/typeless front-panel terminal, the indicator itself being broken, a leftover from `build_property`,
   or something about a Property Node specifically?
2. An **alternative explanation** that survives the same evidence, and the observable that separates it.
3. Attack the "**not a design change**" defence specifically. Does a docstring sentence make the call
   equivalent-preserving here? Could `remove_bad_wires_scripted` remove MORE than the stub on a 1,905-wire VI,
   and would the run be able to tell? (The script reports the whole-VI `Wire` count before and after; say
   whether that is sufficient to detect over-removal, and if not, what is.)
4. Attack the **type-survival** clause: is there any reason a Boolean indicator created from a Property Node's
   read terminal would NOT stay Boolean once its source wire is removed and it is moved to another diagram?
5. **What would falsify** the claim, and the **cheapest discriminating test** run 2 could carry.
6. Is `remove_bad_wires_scripted` the right verb at all, or is the real answer that the carrier should not be
   deleted in that order — or that a SOURCE terminal was the wrong choice and cycle 57's SINK-terminal carrier is
   what made its delete clean?

## Files you may read (read-only; this project's directory)

- `tools/bench/diag_s58_boolcarrier_run1.log` and `tools/bench/diag_s58_boolcarrier_run1.json` — run 1.
- `tools/bench/diag_s58_boolcarrier.py` — the script (it already carries run 2's added step B3c).
- `tools/bench/diag_s57_typepair.log` / `.py` — cycle 57's clean 35/0 run with the Index Array carrier.
- `tools/gscript.py` — `delete_object` :2240, `remove_bad_wires` :1629 (GUI) and `remove_bad_wires_scripted`
  :2486, `create_indicator` :2388, `build_property` :2194, `move_in` via `tools/recipes/build_d1_v0.py`.
- `docs/vi-server-ids.json`, `docs/NAMES.md`, `STATUS.md`, `docs/cycle27-plan.md` Pre-decided 47.

## Already ruled out (do not spend your answer on these)

- "The candidates were not Boolean": all three placed, and the machine read their terminal tables and the
  created labels back — `'Metrics:Front Panel Loaded'`, `'Automatic Error Handling'`, `'Is Broken?'`.
- "The gate threshold was wrong": `B3b` asserts `ExecState == 1`, which is what a saveable VI reads.
- "Use the GUI Ctrl+B": this run performs no GUI action; only the scripted verb is in question.
- "Just save the broken VI": `allow_broken` stays False by rule; that is not on the table.

## Output contract

Plain text. No file writes. Lead with `VERDICT: REFUTED — <what specifically does not hold>` or
`VERDICT: SURVIVES — <the narrowest statement that survives>`, then the six numbered answers.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

VERDICT: REFUTED — the "dangling wire" is not established by this log, and the one piece of evidence offered for it (`'wire': 0, 'wire_err': 1055`) is, by gscript's own docstring and by cycle 57's clean run, the signature of a **bare** terminal at `ExecState 1`, not a broken one. The remedy's nearest measured precedent on this machine is a **failure**, and the "not a design change" defence collapses against a measurement this project already made.

---

**1. The single strongest reason the claim is wrong**

The claim's evidence says the opposite of what it is read to say. `tools/gscript.py:829-830` defines the reading verbatim:

> "`wire` = the connected wire's UID, **0 when the terminal is bare (then wire_err == 1055 and term_err == 0: the terminal exists, nothing is wired to it)**."

So `{'wire': 0, 'term_err': 0, 'wire_err': 1055}` is the documented signature of an **unwired** terminal. And cycle 57 — the 35/0 run held up as the clean contrast — produced *exactly that same row*: `diag_s57_typepair.log:116` and `:140` read `{'label': 'index', …, 'wire': 0, 'term_err': 0, 'wire_err': 1055}` while `ExecState` read **1** (`:112`, `:128`, `:135`, `:143`), the VI saved 476,209 bytes (`:146`) and cold-reopened at `ExecState 1` (`:153`). A reading that is identical in the broken run and the whole run cannot be the mechanism that distinguishes them. Calling it "MEASURED, not inferred" inverts it: what was measured is that the indicator terminal ended up with **no wire attached** — which is evidence *against* a stub hanging off it.

Compounding this, the ExecState timeline has a hole exactly where the attribution is made. Run 1 reads `ExecState` at `A BEFORE` = 1 (`:39`) and then **not again until after the delete** = 0 (`:78`). Three mutations sit in that gap: `build_property` placed the node, `create_indicator` created and wired the indicator, `delete_object` removed the node. The log does not license attributing 1→0 to the third one. (Two citations in the claim also do not land in `_run1.log` — its `:71` is the newline line and `:97` is the B5 banner; the wire rows are `:72` and `:95`. Two similarly-named logs exist; the citation needs pinning to one file.)

**2. Alternatives that survive the same evidence**

- **Alt-A — `create_indicator` broke it, not the delete.** Nothing in run 1 excludes this. Prior art removes the third candidate: `tools/bench/diag_bdloaded_reader.log:10` reads `[after build_property] ExecState 1` with the *same* builder and the *same* 291/292 pair as C1, and `:11` records the gate "the VI is broken while the new PN's `reference` is bare (expected)" **FAILING** — the bare-reference node leaves the VI whole. So B1 is innocent and the break is pinned to B2 **or** B3, unseparated.
- **Alt-B — the delete removed node *and* wire, and the VI is at 0 for a reason with no wire in it.** This project has that failure mode written down twice: `archive/2026-09-17-status-cycle15-narrative.md:88` — "**no broken wire, nothing for Remove Bad Wires, ExecState 0**" — and `docs/d1-build-plan.md:451`, "with *no broken wire and nothing for Remove Bad Wires* — a silent bare terminal". `remove_bad_wires` cannot touch either.
- **Separating observable:** the whole-VI `Wire` count across B1→B2→B3. If it goes 1905 → 1906 → **1905**, the wire died with the node, there is no stub, and RBW is the wrong verb. If it stays 1906 with uid 23586 alive, the claim's mechanism is real. Run 1 took the census once, at `A before everything` (`:38`), and never again.

**3. The "not a design change" defence — it does not hold**

A docstring states what a verb does; it does not establish that applying it to a 1,905-wire derivative of the user's production VI is behaviour-preserving. The sentence quoted even says "if the VI must run" — a runnability hint, not a locality proof.

The defence is contradicted by this project's own measurement: `archive/2026-09-17-status-d1-route-b-2.md:45` — "deleting t1's wire + **`remove_bad_wires_scripted` DELETES THE TUNNEL**, so every higher index drops by one and the map goes 7 → 6 terminals," closed by a 39/0 diagnostic. RBW has been measured here removing a **LoopTunnel** — a structural object, not a wire. Externally, NI documents method 410 as "Removes **all** the broken wires on the block diagram of the VI" with no scope caveat, and LabVIEW users report Ctrl+B "clears broken wires for all cases of a selected case structure" and warn that users "may not know that they just changed the function of their code." Under CLAUDE.md rule 1a that is a computation-change hazard, not a housekeeping call.

**Is the before/after `Wire` count sufficient to detect over-removal? No, three ways.** (a) It counts, it does not name — 1906→1905 looks perfect whether the stub or a pre-existing wire went. (b) The known over-removal mode here deletes a **tunnel**, which a `Wire` count cannot see at all. (c) `docs/d1-build-plan.md:819` reported "3 of 8 wires deleted by Remove Bad Wires" and `:19` **withdraws** it — "the gate measured uid identity" — i.e. this project has already been burned once by the wrong detector. Sufficient detector: the **Wire uid set difference** (`set(g.uids(target,"Wire"))` before minus after, printed) **plus the full class census** including `LoopTunnel`, `ControlTerminal`, `Function`, `SubVI`, `Property`, `IndexArray`. Both helpers already exist in the script (`census()`, `g.uids`) — no new tooling.

One more: `remove_bad_wires_scripted` swallows the modal-dialog exception (`tools/gscript.py:2494-2498`) — precisely the anti-pattern this project stripped out of `delete_object` (`:2264-2272`) and `create_indicator` (`:2399-2402`). A refused RBW returns normally. B3c's gate reads ExecState so the gate stays honest, but the log narrative "RBW ran" would not be.

**4. The type-survival clause**

Probably true, but it is stated as a known when it is a prediction, and the run cannot check it — 47(j): no reader in this fleet returns a terminal's data type. An FP indicator does own its datatype and RBW removes wires, so a Boolean indicator should stay Boolean once bare and once moved. Two caveats: "RBW only removes wires" is already false locally (the tunnel above), so "the indicator cannot be touched" is not guaranteed by the verb's description; and passing B3c tells you nothing about type — after a successful RBW the artefact is in *exactly* cycle 57's shape, a bare indicator, and cycle 57's bare indicator read `Is Broken? = True` when wired. Only B7 answers the run's question. The consequence sentence bundles a repair prediction with a type prediction and only the first is anything RBW could deliver.

**5. What would falsify the claim, and the cheapest discriminating test**

Falsifiers, any one of which kills it: `ExecState` reads 0 after B2, before any delete; or the `Wire` count returns to its pre-B2 value after the delete (no stub exists); or RBW runs and the count is unchanged with `ExecState` still 0. That third one is **already on disk in adjacent cases** — `diag_bdloaded_reader.log:15` `[after remove_bad_wires] ExecState 0`, `:26` "reader still broken (ExecState 0, reference wire 467)", summarised as settled at `docs/toolkit-capabilities.md:596-598` ("`remove_bad_wires` does not clear it"); and `tools/bench/broken_probe2.log:7` "after Remove Bad Wires: wires 16 -> 16 ExecState 0".

**Cheapest discriminating test — three `g.exec_state()` calls and four `g.count(target,"Wire")` calls, plus one `set(g.uids(target,"Wire"))` snapshot. No mutation, no new op, seconds.** Read `(ExecState, Wire)` after B1, after B2, after B3. `ExecState` 0 at B1 ⇒ the node. 0 at B2 ⇒ `create_indicator`. Wire back to baseline at B3 ⇒ no stub, RBW is the wrong verb and run 2 would burn another 229 s reproducing three identical FAILs. Only if uid 23586 is still alive at B3 has the claim earned its mutation — and then RBW should run with the uid-set diff above, not a count. This is what "when a diagnosis is GUESSED twice, build the reader" asks for, and it is strictly cheaper and safer than the proposed whole-VI mutation.

**6. Is `remove_bad_wires_scripted` the right verb at all?**

No — the ordering is the defect, and your own logs show why. Cycle 57's delete was clean because its indicator was **never wired**: `diag_s57_typepair.log:108` created it on `Nodes[0].Terminals[2]`, the `index` **input**, and `:116` shows the row already bare at creation — two sinks cannot be wired together. Cycle 58 created on a SOURCE, so LabVIEW wired it (`:72`, wire 23586). That contrast is real, and it argues for changing the route, not for adding a whole-VI repair verb at the end of it.

Two better routes, both judgement calls rather than mine to pick:

- **Don't delete the carrier before the save.** Move and save with the carrier standing, wire the indicator to `#10686`, and delete the carrier last — the indicator is never sourceless, so no stub can exist. This also fixes the more expensive failure in run 1, which is not the ExecState reading at all: `:301` reads `ARTEFACTS ON DISK: []`. Under CLAUDE.md's "a step is not done until it has left a file", three candidates × zero files is the real cost of run 1, and moving the save earlier is the fix for it.
- **Address the nested terminal directly.** `OpCreateConstOnTerm_v0` already reaches a nested diagram's node terminal (`Class Name`='WhileLoop'/`index` = the loop, `index 3` = body `Nodes[]` index, `index 4` = that node's `Terminals[]` index — `docs/toolkit-capabilities.md:66`). A Create-Indicator analogue on that donor pattern deletes the entire carrier → create → delete → move dance, and with it this whole failure class.

If the B1/B2/B3 readings come back showing uid 23586 alive after the delete, I am wrong about the mechanism and the claim's cause stands — though its sufficiency would still be open, given `diag_bdloaded_reader.log:15`. Nothing short of those readings changes my mind, because run 1 simply does not contain the measurement the claim is built on.

Sources:
- [VI class/Block Diagram.Remove Bad Wires method — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method)
- [Remove ONLY broken wires in visible cases/sequences/structures — NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Remove-ONLY-broken-wires-in-visible-cases-sequences-structures/idi-p/1011653)
- [hotkey to remove only broken wires with no connection — NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/broken-wires-hotkey-to-remove-only-broken-wires-with-no/idi-p/951765)
- [Create Indicator method — NI LabVIEW API Reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/terminal/createindicator.html)

## Sources

(extract from answer)

## What was done with it

**RECORDED, NEITHER ACCEPTED NOR REJECTED (Pre-decided 41(b)). NO FINDING OF IT WAS ACTED ON AS A DECISION.**
Choosing what to take from a review is a JUDGEMENT act (CLAUDE.md §3); this is a material session. Dispatched
because `guard_peer.py` blocked run 2 over `tools/bench/diag_s58_boolcarrier_run1.log`, first failure line
`FAIL  C1 B3b ExecState after the delete == 1  0 (PREDICTED RISK (v))`. The block is lifted by this exchange
(claude / hypothesis, opus effort max + web, **ANSWERED 381 s, `$3.6322`**, in 24 / out 29,707 / cache-create
202,637 / cache-read 1,589,576, 23 turns; `BGRUN END rc=0 after 381s`, runner log
`tools/bench/peer_c58_delete_execstate0.log`).

**Verdict in one line:** `REFUTED — the "dangling wire" is not established by this log, and the one piece of
evidence offered for it ('wire': 0, 'wire_err': 1055) is, by gscript's own docstring and by cycle 57's clean
run, the signature of a BARE terminal at ExecState 1, not a broken one.`

**ONE THING IT SAID WAS ACTED ON, AND IT WAS A REMOVAL, NOT AN ADOPTION.** Before this review existed, run 2
carried a step `B3c` that called `gscript.remove_bad_wires_scripted` after the delete. **That step was DELETED
from the script before run 2 launched.** The reason is not "the reviewer says so" but the rule it cites: this
project has already MEASURED `remove_bad_wires_scripted` removing a **LoopTunnel** as well as wires
(`archive/2026-09-17-status-d1-route-b-2.md:45`, closed by a 39/0 diagnostic), NI documents method 410 as
removing *all* broken wires with no scope caveat, and a whole-VI mutation with a structural-removal precedent on
a derivative of the user's production VI is a **rule-1a hazard**. Accepting that risk is judgement's call, not a
material session's — so the mutation was withdrawn and nothing replaced it. **No repair of any kind is attempted
in run 2; `remove_bad_wires_scripted` is not called and the GUI route at `gscript.py:1629` is not called.**

**What run 2 does add is READINGS, and they are the brief's own.** The brief's phase-B step list already asks
for `ExecState` to be reported at each step; run 1 read it at `A BEFORE` (1) and then not again until after the
delete (0), with three mutations in the gap — so it could not name which one broke the VI, and the cause it
printed was an INFERENCE. Run 2's `B3d` reads `ExecState`, the whole-VI `Wire` count and the whole-VI `Wire`
**uid set** after EACH of `build_property`, `create_indicator` and `delete_object`. Three verbs already in the
fleet, no new tooling, no mutation. That this coincides with the review's §5 is noted rather than concealed; it
is also what CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader" requires independently.

**Everything else it raised is RECORDED AND NOT ACTED ON, for judgement:**
- §1 `tools/gscript.py:829-830` defines `wire == 0` with `wire_err == 1055`, `term_err == 0` as the **bare**
  signature, and `diag_s57_typepair.log:116,:140` shows cycle 57's clean 35/0 run producing *the same row* at
  `ExecState` 1 — so that row cannot distinguish the broken run from the whole one. It also corrects two of my
  line citations (the wire rows are `run1.log:72` and `:95`, not `:71`/`:97`).
- §2 Alt-A: `create_indicator`, not the delete, may be the breaker — and `tools/bench/diag_bdloaded_reader.log:10`
  already reads `ExecState 1` after `build_property` with the SAME 291/292 pair, with its "the VI is broken while
  the PN's reference is bare" gate FAILING, which clears `build_property` but leaves B2 and B3 unseparated.
  Alt-B: a break with **no broken wire at all** is documented twice here
  (`archive/2026-09-17-status-cycle15-narrative.md:88`; `docs/d1-build-plan.md:451`), and RBW cannot touch it.
- §3 a whole-VI `Wire` COUNT is an insufficient over-removal detector three ways (it does not name; it cannot see
  a tunnel; `docs/d1-build-plan.md:819` was withdrawn at `:19` for exactly this) — hence the uid SET in `B3d`.
  It also notes `remove_bad_wires_scripted` swallows the modal-dialog exception (`gscript.py:2494-2498`), the
  anti-pattern stripped from `delete_object` and `create_indicator`. **`gscript.py` was NOT patched.**
- §4 type survival is a PREDICTION, not a known — 47(j) means the run cannot check it — and a successful repair
  would only reproduce cycle 57's shape, whose bare indicator read `Is Broken? True`. Only `B7` answers.
- §6 its two proposed ROUTES — (a) do not delete the carrier before the save, so the indicator is never
  sourceless; (b) an `OpCreateConstOnTerm_v0`-shaped op that addresses a NESTED node's terminal directly, which
  is 47(i) route 2 — are **NOT TAKEN**. It names as run 1's real cost `ARTEFACTS ON DISK: []` against the user's
  2026-09-19 rule. Both are judgement's to dispose.
- Its own falsifier, stated by the reviewer: if uid 23586 is alive after the delete, its mechanism reading is
  wrong and mine stands. `B3d` reads exactly that and settles nothing by argument.
