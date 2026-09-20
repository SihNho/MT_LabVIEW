# routeb-run8-predictions

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.4847  in 26 / out 46958 / cache-create 245666 / cache-read 1510842  (676s, 25 turn(s))
- **date:** 2026-09-19 04:44:02
- **outcome:** ANSWERED (678s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

D1 route-B run 8 (`tools/bench/build_d1_routeb_v5_run8.log`, `BGRUN END rc=1 after 1822s`, 80 PASS / 0 FAIL gates) was a one-line discriminator and EVERY prediction on record missed. Attack the framing below; do not confirm it.

THE CHANGE UNDER TEST (K1): `tools/recipes/build_d1_routeb_v5.py:1760` deleted the VI-wide `remove_bad_wires_scripted(target)` that v4 called from INSIDE the S3w row loop (v4 `:1669`), putting nothing in its place. K2 made the post-delete wire-count gate PER-DIAGRAM (`:520` `diagram_wire_count()`, `:1613`, `:1842`). K3 added a survival census of the ledger's uids after the S3w ledger line (`:1130`, `:2036`, `:2120`).

PREDICTIONS ON RECORD (STATUS.md NEXT, written by the cycle-39 judgement session): t3/t4 leave NO-ROUTE · t5 leaves FAILED · `Z/dZ` t0 stays wired at w29238 · per-diagram Wire delta 0.

OBSERVED in run 8:
- `#2222` t3 WIRED (`:411`, w29180, Is Broken? FALSE), t4 WIRED (`:412`, w29347), t5 WIRED (`:413`, w29406, `reparented=True`, attempts `[(24,'no error',29406)]`), t2 WIRED (`:410`). Run 7 had t3/t4 NO-ROUTE and t5 FAILED.
- `Z/dZ` t0 FAILED (`:418`) on reading (b) ONLY: PER-DIAGRAM Diagram[24] 31 -> 32, delta +1; VI-wide logged beside it 1937 -> 1938, delta +1. (a) source identity True (the control's own wire 29238 == the sink wire 29238, exactly 1 reciprocal source terminal, self-echo ('Diagram',567), expected ControlTerminal uid 403), (c) `Is Broken? False`, (d) sink wire read back 29238.
- Ledger `:363`: attempted 66 / WIRED 53 / FAILED 12 / NO-ROUTE 1 (run 7: 66/54/9/3; run 6: 55/7/4; run 5: 57/6/3). ELEVEN of the twelve FAILED rows carry `error 2` (`:419-:429`); the twelfth is `Z/dZ`'s J2 gate. The single NO-ROUTE (`:430`) is `#10407 t1 '# slices in stack' <- from-tunnel 9641, w9649 has 0 source terminals, not 1: []`.
- K3's SURVIVAL CENSUS — the measurement this run existed to produce — is UNREAD (`:364`): `report_all(Wire)` raised `error 2: ... Traverse for GObjects.vi->OpReportAll_v0.vi | <APPEND> | Method Name: Class Operator:Traverse (Traverse Failed)` after 50 uids had been claimed.
- `error 2` still crashes the run in `settle_index_modes` (`:432`, `:454`, `count(LoopTunnel)`), handles 35,555 immediately before (`:431`); handles before the run 31,130, after 50,709. Victim rows went 6 in run 7 -> 11 in run 8, and the victim CLASS widened: 10 `report_all(Diagram)` + 1 `report_all(WhileLoop)` (`:423`), plus `report_all(Wire)` at `:364`.
- ExecState: S1 baseline 0 COLD (`:37`, logged UNREAD); the live copy PRELOADED 1 (`:437`). Original md5 unchanged, `:13` and `:440`. REFS final `{'opened':31,'closed':31,'live':0,'cached_op_vis':25}` (`:442`).

ALREADY RULED OUT — do not re-propose:
- `gscript.net_map` as a wire-counting instrument: it calls `remove_bad_wires_scripted(target)` internally (`tools/gscript.py:2507-2516`, `:2568-2588`), so it re-fires the very reaper K1 removed, twice per row.
- "a constant cannot explain a change", applied to `error 2`: that was cycle 39's reading and run 8 falsifies it (6 -> 11 victims, new victim classes).
- `live: 0` in the REFS line as evidence that refnums are balanced: `_REF_CLOSED` increments unconditionally in `vi_ref`'s `finally` (`tools/gscript.py:251-259`), so it is a tautology.

QUESTIONS:
Q1. Every miss is in the direction of MORE wired rows — which is what K1's own diagnosis implied and the recorded predictions denied. Give the strongest case that the recorded predictions were the correct null and that run 8's improvement has a cause OTHER than removing the in-loop reaper. Name that cause, and name the cheapest test that separates it from "the reaper was eating the build's own scaffolding".
Q2. The `Z/dZ` per-diagram delta is +1, not 0, across a bracket that creates one `Equal?` node, wires it, reads it, and deletes it. What single wire would a CORRECT cleanup leave behind? Is +1 evidence of a leak, of the sink wire itself being counted inside the bracket, or of the count being taken at the wrong boundary? Answer against `build_d1_routeb_v5.py:520`, `:1613`, `:1842`.
Q3. `error 2` (Traverse Failed) now hits `report_all(Wire)`, `report_all(Diagram)`, `report_all(WhileLoop)` and `count(LoopTunnel)`, always above ~35.5k handles, and grew 6 -> 11 victims when the only intended change was deleting a reaper. What is the causal chain, and is the handle count a cause, a symptom, or a coincidence? Search externally for LabVIEW VI-Scripting `Class Operator:Traverse (Traverse Failed)` / error 2 and say what the vendor's own material attributes it to.
Q4. Name the ONE cheapest read-only measurement that would make a surviving-wire census readable — or prove it unreadable over this COM path — given that `report_all(Wire)` is the call that dies. Four preserved crash copies are on disk, newest `...\claudeDev\SCRATCH_routeb_035814_crash_042836.vi`.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

No. The framing does not survive the run's own log.

---

# 1. The single strongest reason the claim is WRONG

**Run 8 is being read as an improvement. Measured on the ledger it is a regression, and the regression has an exact shape that K1 alone predicts backwards.**

| | run 7 (v4) | run 8 (v5) |
|---|---|---|
| WIRED | **54** | **53** |
| FAILED | 9 | **12** |
| NO-ROUTE | 3 | 1 |
| `error 2` victims | 6 | **11** |

The three rows gained are all on node `#2222` (`:411`–`:413`). The rows lost are exactly four, and they are *contiguous and identifiable*: run 7 wired `#8885 t2`, `#9833 t0`, `#9833 t2`, `#11261 t1` (`build_d1_routeb_v4_run7.log:416-419`); in run 8 those same four rows are the first four `error 2` victims (`run8.log:419-422`). Run 8's WIRED list stops at `#8885 t1` (`:417`); run 7's ran four rows further. 54 − 4 + 3 = 53. Nothing here is noise.

So **the traverse-exhaustion frontier moved four rows EARLIER in run 8** — and K1, on its own, predicts the opposite. Deleting `remove_bad_wires_scripted(TARGET)` removes *three* machine round-trips per bracket, not one: the Remove Bad Wires invoke, plus the `count(target,"Wire")` and `exec_state(target)` that function returns (`tools/gscript.py:2490`). A run that does strictly less scripting work should reach *more* rows before the resource runs out. It reached fewer.

Therefore run 8 is **not** the "one-line discriminator" its own comment insists it is (`build_d1_routeb_v5.py:1770`: *"ONE LINE, and the discriminator's value depends on it staying one line"*). At minimum K2 added a forced full re-walk of Diagram[24] inside the bracket — `diagram_wire_count(tdi, fresh=True)` at `:1613`, which v4 did not do at all — and that walk is `node_labels` + `node_terms_uid` per node over a ~30-node diagram (`:539`, `tools/recipes/build_track_v6_core.py:84-92`). The brief's own "already ruled out" list bans `net_map` for being destructive, then hands the gate an instrument whose cost was never counted.

**And the headline sentence is false as written.** "Every miss is in the direction of MORE wired rows" is true only of `#2222`. Across the ledger the run wired one row fewer and failed three rows more. That selection is the framing's load-bearing error.

---

# 2. Q1 — the strongest case that the recorded predictions were the correct null

The predictions were written for a build in which nothing but the reaper changed. That build was not run. Here is the case, and the alternative cause, in the order the evidence supports:

### The reaper story predicts a uniform effect on `#2222`, and run 7 shows a ragged one

`build_d1_routeb_v4_run7.log:274-280` lists **seven** cut terminals on `#2222` — t0, t1, t2, t3, t4, t5, t6 — every one of them unwired at the moment the bracket fired. If a VI-wide Remove Bad Wires inside the row loop deleted the dangling wires and LabVIEW then dropped the now-wireless tunnels, all of the still-unwired ones should have gone together. They did not:

- `t2` — cut (`:276`), still unwired when the bracket ran, and **WIRED afterwards** at `D[24].N[20].T[2]` (`:411`).
- `t6 'X out'` — cut (`:280`), and **still resolvable by name afterwards**: `#6104 t0` wired `CaseStructure[3].'X out' -> IndexArray[9].'array'` (`:413`).
- `t3`, `t4` — `'<no such terminal>'` (`:429-430`).
- `t5` — present enough to be looked up, absent enough that `Wire Inputs.vi` reported `Input Correction Factor not found` (STATUS.md:21).

`t2` and `t6` survive, `t3`/`t4`/`t5` do not, and the node index is identical in both runs (`D[24].N[20]` at run 7 `:411` and run 8 `:410`), so this is not an index shift either. **No wire-deleting mechanism is selective by terminal index.** The vendor's own description of the method is that it "removes all the broken wires on the block diagram" and nothing else ([LabVIEW Wiki, Block Diagram:Remove Bad Wires](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method)); tunnel auto-removal when the last wire goes is real but is a *uniform* consequence, community-reported, not a documented selective one ([NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-Delete-Passthrough-Wires-when-a-Linked-Tunnel-is/idi-p/2421080)).

### The alternative cause, named

**`#2222`'s terminal census was never read on either side of the reaper.** K1's diagnosis rests entirely on a correlation over five runs whose recipes differ in dozens of places (v2→v3→v4→v5), plus the `−96` VI-wide Wire delta — which, as §3 below shows, was measured against the wrong null. The competing explanation is that whatever removed t3/t4/t5 is something *else* in the S1d/S3 → S3w interval that v5 also happens to have changed or re-ordered, and the reaper is a bystander that was, separately and genuinely, deleting ~97 wires.

That matters because the two stories license different rules. Pre-decided 17 as written — *"no VI-wide remove-broken-wires inside a row loop"* — is safe only under the reaper story. If the agent is anything else, or if it is the reaper but the real predicate is "before every cut tunnel is re-wired", then S5, the save, `net_map`, and the first Ctrl+B the user presses will all reproduce it, and the rule as worded will not stop them.

### Cheapest test that separates them

One bracket, read-only, on the throwaway copy the recipe already builds, at the S3 post-cut state and using ops already in the fleet:

```
terms_of(copy, 24, 2222, fresh=True)   →  count(copy,'Tunnel'), count(copy,'Wire')
remove_bad_wires_scripted(copy)
terms_of(copy, 24, 2222, fresh=True)   →  count(copy,'Tunnel'), count(copy,'Wire')
```

Three ops either side. If t3/t4/t5 vanish from the census and the Tunnel count drops, K1's mechanism is confirmed **and Pre-decided 17 must be re-worded from "inside a row loop" to "anywhere between the first cut and the last rewire"**. If the census is unchanged across the call, K1 removed the wrong line and the `−97` wires are a separate (real) problem. Either way it costs one bracket and settles three cycles of inference.

---

# 3. Q2 — the `+1` is the wire the row was built to create. The gate is inverted.

**A correct cleanup leaves behind exactly ONE wire: `w29238` itself.**

Read the bracket boundaries as the code actually places them:

- `:1613` `_wcd_before = diagram_wire_count(tdi, fresh=True)` and `:1614` `_wct_before = g.count(TARGET,"Wire")` — taken **before** `create_equal` at `:1616`.
- The branch is only reached under `if not zw` (`:1597`) — i.e. **the control carries no wire at all**. Corroborated: `run7.log:179` (`#2222` t0 = `('', False, 0)`, `#403` on Diagram[56] is `Nodes[None]` with terminals `[]`) and `:201` (after the reparent, t0 carries wire 0, *was 0 before it*).
- `g.wire_control(...)` at `:1668` then creates a **brand-new** wire — `w29238`, which did not exist before the bracket.
- `OpConnectFromWire_v0` at `:1751` **branches that same net**: same uid back (`run8.log:356`, `wire 29238`), so no second wire object.
- Deleting the `Equal?` removes its segment; the net survives on the branch (`:358`, `:360` (d) = 29238).

Net effect of a *fully successful* bracket: **+1 wire**, on Diagram[24] and VI-wide. Run 8 measured `(31, 32, +1)` per-diagram and `(1937, 1938, +1)` VI-wide (`:418`) — **both instruments agreeing on the success signature.** `_b_ok = (_wddelta == 0)` at `:1842` is therefore the wrong predicate; it should be `== 1`. A delta of 0 would have meant the row did nothing.

Answering your three options directly: it is **neither a leak nor a boundary error nor double-counting of the sink wire**. It is the one wire the bracket exists to produce, and the count is taken at the right boundary — the *expected value* at that boundary is wrong.

The consequence propagates backwards and is the more serious half: **the comment at `:1601-1605` that defines the null ("Every write in the bracket is a BRANCH off an existing net or the removal of the node that carried it, so the expected delta is 0") is factually false about the first write, and it was equally false in v4.** So run 7's `−96` was scored against a null of 0 when the correct null was `+1`: the reaper's real damage is **−97 wires**, and, more importantly, the reading that *justified K1* came from an instrument whose specification was wrong. The gate failed run 7 for the right reason by accident and failed run 8 for the wrong reason.

---

# 4. Q3 — `error 2` is **"Memory is full"**, and the handle count is neither cause nor symptom. It is a panel-state indicator.

### What the vendor attributes it to

LabVIEW **error 2 = "Memory is full" (Hex 0x2)**, and NI's own material attributes it overwhelmingly to *reference allocation failing*, not to a full machine — it is the canonical error from Open VI Reference, Obtain Notifier/Queue, .NET Constructor Node and Open/Create/Replace File ([NI: Error 2: Memory is Full when Opening a New Reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU), [NI: Memory Is Full Error in LabVIEW](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9mtSAC)). NI and LAVA both note it is routinely raised when no memory shortage exists ([LAVA: "Error 2: Memory is full — but it isn't"](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/), [NI forum](https://forums.ni.com/t5/LabVIEW/Error-2-Possible-reason-s-LabVIEW-Memory-is-full/td-p/3569198)). `<b>Class Operator:Traverse</b> (Traverse Failed)` is the scripting library's `<APPEND>` on top of that code: `Traverse for GObjects.vi` returns a plain boolean success flag and appends its own text when the traverse returns FALSE ([NI: Traverse for GObjects VI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html), [LabVIEW Wiki: Class Operator.Traverse](https://labviewwiki.org/wiki/Generic_class/Class_Operator.Traverse_method)). The Traverse method carries one vendor caution worth having in this project's file: *"Do not attempt to modify code in traverse callbacks. This changes the stack the traverse operation is iterating through and can cause LabVIEW to crash."* There is also a documented class of "Traverse fails for this class name" bugs, with the workaround of traversing `GObject` and filtering in G ([NI forum: VI Scripting: Error Ring](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Error-Ring/td-p/3957513)) — relevant because the victims here are `Wire`, `Diagram`, `WhileLoop`, `LoopTunnel`, i.e. the traverse is being asked for a class each time.

### The handle count: your own logs refute it

The premise "always above ~35.5k handles" does not survive reading two lines further up the same files:

| | run 7 | run 8 |
|---|---|---|
| fresh instance, no panel | 31,128 (`:17`) | 31,130 (`:17`) |
| **S1, working copy open — run healthy for hundreds of ops after this** | **51,349** (`:38`) | **51,353** (`:38`) |
| at the `error 2` crash | 35,551 (`:432`) | 35,555 (`:431`) |
| after `lv_restart` | 30,692 (`:436`) | 30,690 (`:435`) |

**Both runs executed normally at ~51.3k handles and then failed at ~35.5k.** Opening one front panel costs ~20k handles; the number is dominated by panel state, not by leakage. And the two crash readings match to four counts because they are taken at *the same syntactic point in the script* (`settle_index_modes`, immediately before `g.count(TARGET,'LoopTunnel')`), not at the same resource level — one fixed probe compared across runs is not a pattern. So: **handle count is a coincidence with respect to `error 2`**, and the "35.5k threshold" is an artifact of where the probe is placed. It should stop being quoted as evidence in either direction. (The `after` figures, 51,328 / 50,709 "before 31,128 / 31,130", straddle an `lv_restart` and are not one process's growth at all.)

### The causal chain the evidence does support

1. Every op in this fleet begins with a class Traverse; each returns a reference array inside LabVIEW.
2. Some LabVIEW-internal allocation for that traverse fails and surfaces as code 2, "memory is full" — the same code the reference-opening primitives raise.
3. It is **cumulative within one instance and one target**: the victims are always the tail of the row list, and a restart clears it.
4. **6 → 11 victims is a change in *when* exhaustion arrives, not in *what* fails.** The failing call sites are the same. Run 8 reached it four rows sooner, consistent with run 8 doing more traverse work per row (K2's forced fresh walk at `:1613`) and/or carrying ~97 more live wire objects through every later traverse because the reaper no longer removes them.

That last clause is the one the framing must not keep waving away. The brief asserts `error 2` is *"a SEPARATE, UNSOLVED fault and run 8 does not address it."* **Run 8 did not merely fail to address it — run 8 made it worse, and K1 is a candidate cause.** Cycle 39's "a constant cannot explain a change" is refuted, as you say; but the replacement is not "two independent faults". It is one resource fault whose arrival time is a function of how much traverse work the run does first — which is exactly the variable K1 and K2 both moved.

---

# 5. Q4 — the cheapest readable survival census, and why the crash copies cannot provide it

### First: the crash copies are worthless for this

Run 8's own S0 measured the preserved copy: `SCRATCH_routeb_235020_crash_001808.vi`, **md5 `2a78e17c449cacdaf5da389818526859`** (`run8.log:6`) — byte-identical to the untouched original (`:13`). The recipe only saves at S5, and no run has reached S5. The working copy on disk was byte-identical to the original at S1z (`:36`) and the crash rename (`:439`) copies that unsaved file. **So all four "crash copies" are the pristine original**, carrying none of the build's 50-odd claimed wires. A `report_all(Wire)` on one would return the original's wires and report **all 50 claimed uids GONE** — a total false positive that would look like a spectacular finding. Verify with one `md5` before anyone runs anything against them.

### The one measurement to build

**Do not census `Wire` at all. Re-read the claimed terminals.**

`report_all(TARGET,'Wire')` enumerates ~1,938 objects to answer a question about ~50, and it answers a *weaker* question than the one asked: a surviving wire uid proves an object exists somewhere, not that it still sits on the row's terminal. The recipe already records `(diagram, node, terminal)` for every WIRED row, and `wmap` already returns the wire uid on every terminal of every node (`build_d1_routeb_v5.py:539-540`). So:

> For each claimed row, assert `wmap(TARGET, d)[node][2][t]['wire'] == claimed_uid`, using the cached walk.

Cost: at most one walk per diagram actually touched (20, 21, 24, 56) — most already cached at that point — instead of one VI-wide Traverse over the largest class on the VI. Strictly cheaper, strictly more probative, no new op, and it degrades gracefully: a diagram that raises leaves its rows `UNREAD` rather than killing the whole census as `:364` did.

If you additionally want to know whether `report_all(Wire)` is *capable* over this COM path: run it once on a **fresh instance against a fresh copy of the original** at ~31.5k handles, before any edits. One call, read-only, no build. Success there proves the call is fine and the failure is accumulated state; failure there proves a capability limit. That is the only thing the preserved copies are good for — and note it is the same test either way, because those copies *are* the original.

---

# 6. What would falsify what I have said

- **On §1**: if a run with K1 applied and K2's `:1613` fresh walk removed still loses those same four rows to `error 2`, my "run 8 changed more than one thing" reading is weakened and K1's second-order cost (97 extra live wires per traverse) becomes the remaining candidate. If such a run reaches *further* than run 7, my claim that the frontier moved for an uncontrolled reason is refuted outright.
- **On §2**: a `terms_of(copy,24,2222)` census showing all five unwired cut tunnels disappearing together across a single `remove_bad_wires_scripted` call would refute the raggedness argument — it would mean `t2` and `t6` were already wired when the reaper fired, and I would withdraw the objection and instead press for Pre-decided 17 to be re-worded as above.
- **On §3**: a run that fails with `error 2` while handles are *below* the S1 figure and *rising monotonically from the run's start* would restore handles as a gauge. Nothing in runs 7 or 8 does that.
- **On §5**: an md5 on `SCRATCH_routeb_035814_crash_042836.vi` that differs from `2a78e17c...` would mean that copy really is a post-edit snapshot, and the crash-copy route becomes viable.

---

# 7. The cheapest discriminating test overall

If only one thing is run next, run **the bracket census from §2** — `terms_of(#2222)` + `count('Tunnel')` + `count('Wire')` either side of a single `remove_bad_wires_scripted` on the S3-state throwaway. It is three ops on each side of one call, it needs no new op VI, no gate change and no build of the deliverable, and it simultaneously:

1. settles whether the reaper removes **tunnels** or only wires (which decides whether Pre-decided 17 is correctly worded or dangerously narrow);
2. gives the `−97` its true composition;
3. and — because it is taken at a fixed, early point in a fresh instance — produces a `Wire`/`Tunnel` count at a handle level where `error 2` has never fired, which is the control §3 needs.

Two things I would fix by inspection before any of that, because both are one line and both are currently producing wrong verdicts: `_b_ok = (_wddelta == 0)` at `build_d1_routeb_v5.py:1842` should be `== 1`, with the comment at `:1601-1605` corrected; and the survival census at `:2125` should re-read terminals rather than call `report_all(TARGET,'Wire')`.

**What would change my mind:** a per-terminal census across the reaper showing uniform tunnel loss on `#2222`, plus a controlled run isolating K1 from K2 that moves the `error 2` frontier *later*. Those two together would make run 8's reading sound. Neither has been taken, and until they are, the run's honest summary is: *one node improved, four rows were lost to a resource fault the run made worse, the gate that failed was mis-specified, and the census that was supposed to make any of it checkable did not execute.*

**Sources:** [NI — Error 2: Memory is Full when Opening a New Reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU) · [NI — Memory Is Full Error in LabVIEW](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9mtSAC) · [NI forum — Error 2 Memory is full](https://forums.ni.com/t5/LabVIEW/Error-2-Possible-reason-s-LabVIEW-Memory-is-full/td-p/3569198) · [LAVA — Error 2: Memory is full, but it isn't](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/) · [NI — Traverse for GObjects VI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html) · [LabVIEW Wiki — Class Operator.Traverse](https://labviewwiki.org/wiki/Generic_class/Class_Operator.Traverse_method) · [LabVIEW Wiki — Block Diagram:Remove Bad Wires](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method) · [NI forum — VI Scripting: Traverse fails for a class name](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Error-Ring/td-p/3957513) · [NI Idea Exchange — tunnels and their wires](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-Delete-Passthrough-Wires-when-a-Linked-Tunnel-is/idi-p/2421080)

I took no lock, opened no VI, built nothing and ran nothing; every local claim above is a read of `tools/bench/build_d1_routeb_v{4,5}_run{7,8}.log`, `tools/recipes/build_d1_routeb_v5.py`, `tools/gscript.py` and `STATUS.md`.

## Sources

(extract from answer)

## What was done with it

Disposed in full by the cycle-40 judgement session, 2026-09-19. All four answers accepted; two became binding
plan items.

- **Q1 — "run 8 was a REGRESSION, not an improvement": ACCEPTED, and it corrects this session's own reading.**
  WIRED 54 → 53, FAILED 9 → 12, NO-ROUTE 3 → 1; the three gained rows are all `#2222` while four rows run 7 had
  wired fell to `error 2`. Judging the run by `#2222` — the rows the recorded predictions happened to name — is
  what made a regression look like progress, and that is written into STATUS NEXT as the cycle's framing error.
  Also accepted: run 8 was **not** the one-line discriminator it was billed as, because K2's `fresh=True` re-walk
  at `:1613` adds traverse work per row. The K1 separator you propose (`terms_of` + counts →
  `remove_bad_wires_scripted` → repeat) is carried in STATUS NEXT as UNRUN, to run after run 9 launches; it is
  what would settle Pre-decided 17, which is NOT re-worded until then.
- **Q2 — the inverted null at `:1842`: ACCEPTED, and CONFIRMED against our own code rather than on your word**
  (CLAUDE.md §5: a peer answer is a hypothesis). Read of `build_d1_routeb_v5.py`: the before-count at `:1613` is
  taken while the control is still bare (`if not zw`, `:1597`); `wire_control` `:1668` CREATES w29238;
  `OpConnectFromWire_v0` `:1751` only BRANCHES that net at delta 0; `delete_object` `:1774` leaves w29238
  standing (`build_d1_routeb_v5_run8.log:358`). The correct null is **+1**. Now binding as
  `docs/cycle27-plan.md` **Pre-decided 19**, and run 9's edit E1. Consequence recorded there: **`Z/dZ` t0 was
  ALREADY WIRED in run 8** and the gate, not the machine, failed it.
- **Q3 — the handle premise: ACCEPTED as REFUTED.** Both runs healthy at 51,349 / 51,353 handles and crashed at
  35,551 / 35,555, so `error 2` is never again to be attributed to a handle count; STATUS NEXT says so. Your
  causal chain (cumulative allocation failure in one instance, cleared by restart) is recorded as UNCONFIRMED —
  to be tested, not assumed — and K1/K2 are recorded as candidate causes of the 6 → 11 worsening.
- **Q4 — do not census `Wire` at all: ACCEPTED**, now `docs/cycle27-plan.md` Pre-decided 18 as amended and run 9's
  edit E2. Your side finding that the four preserved crash copies are byte-identical to the untouched original
  **closes a carried item**: the Q-B3 "read-only 5-step pass over a preserved crash copy" is retired and its
  pointer is removed from STATUS, because a session following it would have "found" all ~50 claimed wires gone.
  Nothing deletes the copies; they are simply not evidence.
- **Not acted on:** the `str(e)[:70]` truncation at eight recipe sites and the `_REF_CLOSED` tautology in
  `vi_ref`'s `finally` (`tools/gscript.py:251-259`) stay recorded as unverified side claims. The second one is
  already used as a standing caveat — `live: 0` in a REFS line is not evidence that refnums are balanced.

(Claude fills in)
