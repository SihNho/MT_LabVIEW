# c68-p6d-stray-invoke

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0573  in 16 / out 7314 / cache-create 88036 / cache-read 702976  (98s, 14 turn(s))
- **date:** 2026-09-24 00:06:53
- **outcome:** ANSWERED (101s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Failed prediction P6d (cycle 68, tools/bench/q_m4_iterlocal.log) - attack the explanation

Context: LabVIEW 2026 VI Scripting over COM, on a dated scratch copy of a VI whose ExecState is 1 on open.
Steps (all by scripted op VIs, never run the target VI):
1. `OpCreateLocalRead_v0` with Write?=True creates a WRITE Local for indicator 'current image number' on the
   top-level diagram -> ExecState 0 (an unwired write Local; expected).
2. `OpMoveIn_v0` moves the Local into a While-loop body diagram (#639). Node census 633 -> 634 across the
   move (one extra node appears).
3. `OpConnectFromWire_v0` branches wire 3268 (source = the loop's iteration terminal #644) onto the Local's
   input. Op errors empty, `Wire.Is Broken?` False, wire delta 0. Node census rises by one again.
Prediction P6d: ExecState 1 after step 3. Observed run 1: ExecState 0 (`q_m4_iterlocal.log:78`).

Run 2 (`tools/bench/q_m4_iterlocal_run2.log`), identical steps plus a purge after step 2 and after step 3 that
deletes any NEW node with ZERO wired terminals (the fleet's documented 'stray Invoke' each OpMoveIn/OpConnect*
call mints, `tools/stagekit.py:513-524`): each purge deleted exactly one 6-terminal, 0-wired node (census
634 -> 633, `run2.log:52-55`, `:103-106`); ExecState after the final purge = 1 (`run2.log:107`); Remove Bad Wires
on the result removed 0 wires, ExecState 1 (`:114`). Control arm: an unwired READ Local on the same indicator ->
ExecState 0 (`:120`).

Our explanation: run 1's ExecState 0 was caused by the unpurged stray Invoke node(s) minted by the op calls
(an unwired Invoke method node with a required refnum input breaks the VI), i.e. a defect of our script's
omitted cleanup, not of the wiring. The next build (a boolean shift register + Not + And + Wait on the same
body, via move_in/connect ops) relies on "purge after every move_in/connect => ExecState reflects only the
intended edit".

Already ruled out: the connect itself (Is Broken? False, RBW removes 0, ExecState 1 once the strays are gone).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** the claim is plausible, but the evidence does not settle it. Run 2 shows that ExecState changes when the stray Invoke is deleted. It does not show that the stray Invoke is what breaks the VI. Don't build the shift-register step on "ExecState only reflects the intended edit" until the test below has run. (Nothing was run or edited; the plan file could not be written because Write is disabled in this session.)

### 1. Strongest reason the claim may be wrong
The causal link rests on one observation: ExecState was 0 after connect (`q_m4_iterlocal_run2.log:92`), the stray was deleted (`:104`), and ExecState read 1 (`:107`). But the delete is itself a scripted edit, and it could trigger a recompile. So the ExecState read taken immediately after the connect op could have been stale, and any edit might have cleared it.
- The earlier evidence doesn't separate these either. The 75-junk-Invoke measurement at `tools/gscript.py:2634-2636`, `2697` purged the strays **and** ran Remove Bad Wires, so it cannot say which of the two restored ExecState 1.
- Outside sources say ExecState can report a VI as bad when it isn't, until it is recompiled ([NI forum](https://forums.ni.com/t5/LabVIEW/VI-state-indicates-VIis-broken-when-it-is-not/td-p/374104)), and that scripting edits force a recompile ([LabVIEW Wiki, VI Scripting](https://labviewwiki.org/wiki/VI_Scripting)).

### 2. Alternative explanation
The broken state is recomputed lazily, and the delete only happened to trigger that recomputation. One more detail makes me doubt that the op creates a genuinely new node each time:
- The stray has **uid 23459 both times** (`run2.log:43`, `:94`).
- That uid is **lower** than the Local created earlier in the same run (23475, `:30`).

A reused or pre-allocated uid fits "a helper object the op reuses" at least as well as "one new junk node per call". The mechanism the claim states is also not quite right: a generic Invoke Node's `reference` input is not always required, since it defaults to the current VI for the Application and VI classes ([Invoke Node doc](https://rajsite.github.io/unofficial-lvdocs/glang/Invoke_Node.html)). If the stray does break the VI, the likelier reason is that it has no method selected ([NI forum](https://forums.ni.com/t5/LabVIEW/invoke-nodes-no-methods/td-p/484601)). The stray's two `Method` terminals fit that (`:101-102`).

### 3. What would falsify the claim
- With the stray still present, re-reading ExecState after a delay, or after a neutral edit, gives 1.
- Or: deliberately leaving one unwired, unconfigured Invoke on a copy that reads ExecState 1 keeps ExecState at 1.

### 4. Cheapest test that separates the two
Use one scratch copy. Run connect_from_wire, leave the stray in place, then read ExecState four times:
1. Immediately after the connect.
2. After waiting 2 s.
3. After a neutral edit: move an unrelated label by 1 px.
4. After deleting the stray.

If ExecState goes 0 → 0 → 0 → 1, the claim holds. If it turns 1 at step 2 or 3, the cause is a stale read.

Reverse arm on a fresh copy that reads ExecState 1: `move_in` an **existing, already-wired** node, then read ExecState before and after purging that op's stray. If ExecState reads 0 while the stray is present, that confirms the stray breaks the VI.

**What would change my mind:** 0 → 0 → 0 → 1 in the four-read test, plus ExecState 0 → 1 in the reverse arm. With both, I'd accept "purge after every move_in/connect" as the rule for the next build.

## Sources

(extract from answer)

## What was done with it

Cycle 68 material, 2026-09-24 00:1x. Asked because guard_peer armed on `tools/bench/q_m4_iterlocal.log` (P6d); the
Jev ladder returned no verdict and the discharge scored p=0.618 (< 0.80), so this review was owed.
- §1/§2 ACCEPTED as stated: run 2 shows ExecState moves 0 -> 1 across the purge, not that the stray is the cause
  (stale read after the connect is not excluded). No rule is written from run 2 alone.
- §4 ACCEPTED IN PART, folded into the M4a build as RECORDED ROWS, not gates: after M4a's first connect the
  ExecState is read immediately, after a 2 s wait, and after the purge (`tools/recipes/stage_d1_m4a.py`,
  rows `P6D-R1..R3`). The "neutral label move" and the reverse arm are NOT run (no scripted label mover in the
  fleet; the reverse arm is a separate diagnostic) — left to judgement.
- The M4a acceptance does NOT depend on the causal claim: it gates ExecState 1 AFTER all purges, Remove Bad
  Wires removing 0, and `Is Broken?` False on an ordered second pass; the purge deletes only NEW nodes with zero
  wired terminals, which is harmless whichever explanation holds.
- §2's uid observation (#23459 on both purges, lower than the Local #23475) is RECORDED as a fact; not acted on.
