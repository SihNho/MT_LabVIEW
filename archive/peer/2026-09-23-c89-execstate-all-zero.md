# c89-execstate-all-zero

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $5.0784  in 48 / out 52069 / cache-create 193995 / cache-read 3295369  (712s, 38 turn(s))
- **date:** 2026-09-23 01:51:52
- **outcome:** ANSWERED (716s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# REFUTE THIS READING — a 4-arm factorial on a LabVIEW VI whose `ExecState` will not go to 1

You are an adversary. Your job is to find the strongest reason the reading below is WRONG. Do not
agree with it, do not summarise it back. If you think it survives, say what would falsify it and
name the cheapest test that would separate it from its best rival.

## The machine and the artefact

A LabVIEW 2026 VI is being restructured by VI Scripting over a COM/ActiveX client (Python). The
artefact under test is `claudeDev\D1_s3b_m3a3b_rowD_20260922_161040.vi` (md5 `0b845952…`, 306,977 B).
It was SAVED BROKEN BY DESIGN and has NEVER BEEN RUN. Its `VI.ExecState` reads 0 (broken). The
project's next stage requires `ExecState` 1. Nobody knows yet what keeps it at 0.

Two candidate causes were on the table:
  (i) three stray, unwired `Invoke` nodes left on the top-level block diagram `Diagram #686`;
  (ii) 11 broken wires that LabVIEW's own "Remove Bad Wires" (RBW) deletes.

## The 4-arm factorial that was run (each arm on its OWN dated scratch COPY of the bed, md5-asserted
equal to the bed before anything was touched; nothing saved; all scratches deleted)

| arm | mutation | predicted `ExecState` | measured |
|---|---|---|---|
| A0 | none (control) | 0 | **0** |
| A1 | delete the three stray `Invoke` nodes #4859, #24012, #24005 | 0 | **0** |
| A2 | Remove Bad Wires only | 0 | **0** |
| A3 | **both: the three deletes, THEN Remove Bad Wires** | **1** | **0 — THE FAILED PREDICTION** |

Supporting measurements, all of which passed their own gates:

* Per delete, BEFORE deleting: the target's asserted class was `Invoke`, it had exactly 6 terminals,
  **0** of them wired, the uid echo returned the same uid, and its owning diagram uid was `#686`.
  After each delete the Node census dropped by EXACTLY 1: 635 → 634 → 633 → 632.
* A2's RBW: `Wire` census 1920 → 1909; the removed wire-uid set was EXACTLY the independently
  measured baseline `[1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]`;
  **0 wires added**; the NODE census was 635 → 635 and `Diagram #686`'s node count 27 → 27, so RBW
  destroyed no node and no tunnel.
* A3's RBW removed the same 11-wire set (set-equal True), added none, and destroyed no node.

## THE READING YOU ARE ASKED TO ATTACK (written by the session that ran this)

> "The three stray nodes and the 11 bad wires are each eliminated as the cause of `ExecState` 0,
> therefore a THIRD cause exists that produces no broken wire — most plausibly a REQUIRED TERMINAL
> LEFT UNWIRED (for example a While Loop's conditional terminal)."

## DISCLOSURE THE REVIEWER MUST WEIGH (stated by the session against itself)

The run performed **NO POSITIVE CONTROL**. Nothing in it demonstrates that `ExecState` responds to a
scripted mutation *within the same run*, through the same code path. So the four zeros are also
consistent with a single stale, cached or lazily-recompiled `ExecState` reading that would have
returned 0 no matter what was done to the diagram. The `ExecState` read is a plain COM property read
on a VI reference opened in the same client; no explicit recompile/`Mass Compile` was requested
between mutation and read, and the read happened within a second or so of the mutation.

## ALREADY RULED OUT — do not re-propose these

* `VI.Get Errors` (method 452) is ABSENT from the exported `VirtualInstrument` ActiveX interface on
  this installation, so the Error List cannot be read over this COM path. Telling us to "just read
  the error list" is not available.
* `Diagram.Nodes[]` cannot enumerate a `Tunnel`- or `ShiftRegister`-class terminal, so a node-side
  sweep for the offending object has likelihood ratio 1 — it cannot see the classes most likely to
  be at fault.
* `Wire.Is Broken?` (property 6371004) reports WIRE state only and is blind to "a required terminal
  is unwired". It already reports False on the ordered pass over this artefact.

## ALSO TRUE, measured this cycle by an INDEPENDENT route

* `#4344`, `#4274`, `#4334` are real shift registers on `WhileLoop #637`
  (reg1 RIGHT `#4256` / LEFT `#4274`; reg2 RIGHT `#4334` / LEFT `#4344`).
* `LoopTunnel #9641` is real, owner `#637`.
* `Diagram #639` owns NO `WhileLoop`. Every loop (`#23041`, `#10170`, `#23032`, `#25380`, `#637`) is
  owned by `Diagram #686` except `#15173`, which is on `Diagram #15041`.
* All 11 broken wires sit on `Diagram #639` — zero on `#686`, zero on the new loop's body `#23058` —
  while their endpoint owners sit on `WhileLoop #637`. That ownership discrepancy is itself unexplained.

## What to return

1. The STRONGEST reason the reading above is wrong.
2. An ALTERNATIVE explanation of the four zeros that the run's own evidence does not exclude.
3. What observation would FALSIFY the reading (be specific about the property/method and the
   expected value).
4. The CHEAPEST DISCRIMINATING TEST — one that can be run read-only, in one scripted run, on a
   scratch copy, with no GUI and no saving, and that separates your alternative from the reading.

Weigh in particular whether the missing positive control makes arms A1/A2/A3 uninformative rather
than merely weak, and whether "a third cause exists" is even licensed by four identical readings.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**REFUTED.** Arm A3 could not have returned `ExecState` 1 even if the two candidate causes had been the whole story — so its failure is a property of the prediction, not evidence about the diagram, and no third cause is licensed. The reading's own candidate ("a required terminal left unwired") is not a discovery either: it is written in the cycle plan, before the run.

---

## 1. The strongest reason the reading is WRONG

**Remove Bad Wires is a delete, not a repair — and on *this* artefact it provably swaps a broken-wire error for an unwired-terminal error at the same site.**

- The method the fleet calls (`Block Diagram.Remove Bad Wires`, 410, `tools/gscript.py:2604-2617`) is documented as *"Removes all the broken wires on the block diagram of the VI"* — the scripting equivalent of Edit▸Remove Broken Wires. It deletes; it repairs nothing. ([LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method))
- The fleet says it in reverse: `tools/gscript.py:2361` — *"Wires attached to the object are left broken: call remove_bad_wires() afterwards if the VI must run."*
- Where those 11 wires actually land, from the project's own independent pass (`tools/bench/diag_c88_brokenwires.log:66-87`): all 11 owned by `Diagram #639`, and four terminate on border objects of `WhileLoop #637` — `w1731 SRC LeftShiftRegister#4344` (:67), `w3947 SRC LeftShiftRegister#4274` (:73), **`w7337 SINK RightShiftRegister#4334`** (:77), `w9635 SRC LoopTunnel#9641` (:81).
- `w7337` is decisive. `docs/cycle27-plan.md:3225` records `#4334`'s **INSIDE** terminal as sitting **on wire 7337** — and 7337 is in the RBW-deleted set. Delete it and that sink is bare, which is a named LabVIEW block-diagram error: *"Shift register: unwired from inside the loop"* ([NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/shift-register-unwired-from-inside-loop.html)) — the exact class `docs/cycle27-plan.md:3170-3173` already names for `#4256`/`#4334`.

A required sink cannot be un-broken by deleting the wire that feeds it. So for any arm whose repair set is {delete 3 unwired nodes, delete broken wires}, `ExecState` 1 was unreachable a priori.

Two smaller collapses inside the sentence:
- *"each eliminated as the cause"* — causes are not exclusive. Removing two of three errors leaves a VI broken. The arms license only "not **jointly sufficient**".
- *"therefore a THIRD cause exists"* — `docs/cycle27-plan.md:3107-3114`: *"`ExecState` 0 IS ALREADY EXPLAINED THREE TIMES OVER … was already 0 at step 02, after the FIRST node move … **`ExecState` 0 is the expected state of this stage, not a fault to diagnose**."* The named candidate is Pre-decided 89 + 96 verbatim.

## 2. Alternative explanations the evidence does not exclude

**Alt-1 (primary):** cause (ii) explains A2 and A3 completely — not by surviving, but by being *replaced*. One cause, two costumes.

**Alt-2 (secondary):** the reader has never been shown to move 0 → 1 headlessly. The disclosure gets this half-wrong in both directions: 1 → 0 **is** demonstrated in-run through the same `g.exec_state` path (`diag_s58_boolcarrier_run1.log:39`=1 → `:78`=0 after `delete_object`; again `:118→:157`, `:197→:236`). But I found **no** log in `tools/bench/*.log` where a mutation moved it 0 → 1 — every `=1` is a VI that was already 1 and stayed 1 (`cycle59_s3a_recipe.log:44-324`, `diag_c60_castseed_probe.log:19-79`, `diag_c61_localdir.log:56-116`). Marking broken is cheap; clearing requires a successful recompile, and nothing here ever saves or runs the VI. A3 tested the only direction with zero demonstrated sensitivity.

**Never in the candidate set at all:** NI lists three causes of a broken VI — a broken wire, a required terminal unwired, and **a broken subVI / connector pane edited after placement** ([Correcting Broken VIs](https://www.ni.com/docs/en-US/bundle/labview/page/correcting-broken-vis.html)). 97 SubVIs, third class unmeasured.

## 3. Supporting claims the machine's record does not support

- *"RBW destroyed no node and no tunnel."* The gate measured the `Node` census and `Diagram #686`'s node list only (`diag_c89_execstate_factorial.py:93-106`). `LoopTunnel` is a separate traverse class (A0: `'LoopTunnel': 138`, log `:26`) and was never re-censused — on the run whose own gate text warns "RBW is on record deleting a TUNNEL in this project". This also contradicts the brief's "already ruled out" item: tunnels cannot be both invisible to a node census and covered by one.
- *"A node-side sweep has LR 1."* True of `Diagram.Nodes[]`, false of the fleet: `report_all("LoopTunnel")` gives 138 rows with `owner_of` (log `:42-43`), and `shift_reg_left` returns each register's OUTER/INSIDE terminals **with `wire` or `'bare'`** (`diag_c73_m3a2_rows.log:29-38`, `:117`). The reader for the reading's own hypothesis exists and was not used.
- *"`Wire.Is Broken?` already reports False on the ordered pass."* One wire, not a pass: `build_d1_m3a3b_rowD_clean.log:127-129` reads it for wire **25324** only; on the 11 that matter it is `NOT READABLE` (`diag_c88_brokenwires.log:67-87`, gate G3 4/11 FAIL).
- The register enumeration is capped at `range(8)` (`diag_c89_execstate_factorial.py:128`) and returned 8 pairs for `#637` (`diag_c89_p2_all.log:49-56`) while the plan records **14** (`docs/cycle27-plan.md:3170`).
- A0 ran on a work copy whose panel was never open (6649 at log `:164`); A1–A3 ran on scratches put through `ensure_loaded` (`stagekit.py:417`). The control differs in a second variable.

## 4. Uninformative, or merely weak?

**A2 is redundant** (same bytes, same result already in `build_d1_m3a3b_d3.log:276-277` and `build_d1_m3a3b_rowD.log:212`; the script's docstring `:20-22` admits it). **A1 is weak but sound.** **A3 is uninformative, not weak** — its mutation cannot remove the class it targets, and its prediction points where the instrument has never moved. P(read=0 | any hypothesis) ≈ 1 ⇒ likelihood ratio 1. Four identical readings from an instrument with no demonstrated response in the tested direction license "nothing changed the reading", not "a third cause exists".

## 5. What would falsify the reading

- **F1** (kills "third cause"): `shift_reg_left(#637 reg1, reg2)` before/after RBW — `#4334` INSIDE `wire=7337 → 'bare'` (and `#4344`/`#4274`/`#9641` losing 1731/3947/9635) ⇒ A2/A3 explained by cause (ii) alone.
- **F2** (kills Alt-2): on a known-good VI, delete a wire into a required input (expect 1→0), re-wire with `connect2`, read `exec_state` with no save. **1** ⇒ the reader clears headlessly; **0** ⇒ every "eliminated" inference this cycle is void.
- **F3** (kills the reading's candidate): a full terminal census of `#639`/`#686`/`#23058` + all ~14 registers of `#637` showing **no** bare sink after deletes+RBW ⇒ the live class is a broken subVI / connector pane instead.

## 6. Cheapest discriminating test — one run, two cells, nothing saved

One `bgrun`, ≈5 min, two dated scratches, both deleted; no GUI, no save, no original touched; every function already exists.

- **Cell A (~2 min) — the positive control in the direction that matters.** Scratch of a small VI known at `ExecState` 1 (`OpLoopCast_v0.vi`, `diag_c60_castseed_probe.log:19`): read (expect 1) → delete one wire into a required input → read (expect 0) → re-create it with `connect2` → read. **The third read is the whole test.**
- **Cell B (~3 min) — the substitution test on the bed.** One md5-asserted scratch: census `shift_reg_left` over **all** registers of `#637` (`range(16)`, not 8) + `LoopTunnel #9641`, recording `wire`/`'bare'`; run `remove_bad_wires_scripted`; repeat the census plus a `report_all("LoopTunnel")` count. Alt-1 predicts ≥1 terminal flips wired → bare (`#4334` INSIDE first). The reading predicts none flips and the pre-RBW bare set already names the offending sink.

Cell B's "before" pass **is** the direct search for the reading's own third cause — and it is the FACT step `docs/cycle27-plan.md:3173-3175` already ordered.

**What would change my mind:** Cell A returning 1 *and* Cell B showing no wired→bare transition. Then the zeros would be real eliminations — though the "third cause" would still be Pre-decided 89's, not a new one.

Sources:
- [VI class/Block Diagram.Remove Bad Wires method — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method)
- [Shift register: unwired from inside the loop — NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/shift-register-unwired-from-inside-loop.html)
- [Correcting Broken VIs — NI](https://www.ni.com/docs/en-US/bundle/labview/page/correcting-broken-vis.html)
- [VI class/Execution.State property — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Execution.State_property)
- [Contains unwired or bad terminal — NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/unwired-or-bad-terminal.html)
- [Troubleshooting Broken Wires — NI](https://www.ni.com/docs/en-US/bundle/labview-nxg-g-programming-api-overview/page/troubleshooting-broken-wires.html)

*(Note: `Write` is disabled in this session, so the plan file could not be created — this answer is the deliverable. NI's `ni.com/docs` pages geo-redirect to a navigation shell for me; the "Correcting Broken VIs" wording above comes from the search index of that page, not from a body fetch, and the two error-page citations rest on their titles in NI's block-diagram error bundle.)*

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN PART, and three of its claims were MEASURED the same hour** by the cycle-67 material
dispatch 3, `tools/bench/diag_c89_bareterms.py` → `tools/bench/diag_c89_bareterms.log`
(14 pass / 0 fail, `BGRUN END rc=0 after 127s`). Read-only on a dated work COPY of the bed; the bed's
md5 and all five pins hold at both ends; `THE FILES THIS RUN LEFT ON DISK: []`.

1. **§2 Alt-2, first half — SETTLED AGAINST the review's "disclosure gets this half-wrong" only in the
   1 → 0 direction, which the review itself already conceded.** The positive control the factorial
   lacked was run: a scratch of `OpFsInnerTunnelConnect_v1.vi` (md5 `5b4e5f0f…`) read `ExecState` **1**;
   deleting `w383` ('error in (no error)' into #43 t4) left it **1**; deleting `w106` ('vi path' into
   #43 t6 — a REQUIRED input) took it to **0** within 0.00 s of the mutation returning, and a second
   read 6 s later still read **0** (`diag_c89_bareterms.log:27-41`). So `g.exec_state` — the same code
   path the factorial used — DOES respond to a scripted mutation in-run, and the factorial's four
   zeros are NOT a stale reading. **The review's stronger point stands untouched: nothing yet shows
   the reader moving 0 → 1 headlessly.** Its Cell A's third step (re-wire with `connect2`, read again)
   was NOT run here and remains the open half.
2. **§1 / the reading's own candidate — REFUTED IN THE MEASURED SCOPE.** All **six** While loops on
   the bed have a WIRED conditional terminal (uid echo OK on every row, every error column empty):
   #23041 term 23456 ← w23489 · #10170 term 23246 ← w23310 · #23032 term 23080 ← w23145 ·
   #25380 term 25410 ← w1737 · #637 term 648 ← w3457 · #15173 term 15276 ← w19456
   (`diag_c89_bareterms.log:47-52`). "A While Loop's conditional terminal left unwired" is dead as a
   candidate. And the bare-input census found **ZERO** bare input terminals anywhere it looked:
   `Diagram #23058` (8 nodes, every terminal listed, `:61-93`), `#10407` (7 terminals, 7 wired) and
   `Global #7202` (1 terminal, wired). This is consistent with — and does not test — the review's
   Alt-1, whose bare sink is a SHIFT-REGISTER inside terminal that only appears AFTER RBW deletes
   `w7337`, a class no node-terminal census can see.
3. **§3's ownership point — CLOSED.** `Diagram #639` is owned by `WhileLoop #637` and `Diagram #23058`
   by `WhileLoop #23032` (`owner_of`, uid-echoed, `:54-59`). So "all 11 broken wires sit on `#639`
   while their endpoint owners sit on `#637`" was never a discrepancy: `#639` IS `#637`'s body diagram.

NOT ACTED ON, and left for the judgement session: §5 F2 / §6 Cell A's re-wire step (the 0 → 1
direction), §6 Cell B (the `shift_reg_left` before/after-RBW substitution test with `range(16)`, not
8), the un-censused `LoopTunnel` class after RBW, and the third NI cause (a broken subVI / connector
pane across 97 SubVIs). Those are design calls, not material work. No rule-1a judgement was taken and
nothing on the bed was changed.
