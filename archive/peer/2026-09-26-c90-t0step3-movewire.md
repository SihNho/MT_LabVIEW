# c90-t0step3-movewire

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.1434  in 36 / out 26673 / cache-create 137582 / cache-read 2219939  (309s, 26 turn(s))
- **date:** 2026-09-26 04:47:15
- **outcome:** ANSWERED (312s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (failed prediction, card 90-5, log tools/bench/diag_c90_t0_step3.log, script tools/bench/diag_c90_t0_step3.py, run 1).

CONTEXT: step 3 of PD196(d) (docs/d1-loop12-17-split-plan.md:1049-1105) instruments a byte copy of claudeDev\D1_s1_copy.vi with
t0stamp CLFN nodes (gscript.build_clfn, top level only) moved into nested diagrams by stagekit.move_in (OpMoveIn_v0 = GObject.Move
by uid). Each CLFN needs param1 `site` (t6) = an I32 constant and param2 `any` (t8) = a BRANCH of an existing wire
(OpConnectFromWire_v0).

OBSERVED (diag_c90_t0_step3.log:24-30, 32-53, 196-199):
 - S00: the constant was created on the CLFN's t6 while the CLFN was TOP LEVEL (gscript.create_const_loop_term 'for_n', uid #23090,
   err ''), then move_in(CLFN #22968 -> Diagram[43]) and move_in(const #23090 -> Diagram[43]) both returned err ''. Afterwards the
   CLFN's t6 wire reads 0 and the Tunnel/LoopTunnel/SelectorTunnel censuses are unchanged (468/132/146 before and after).
 - S02..S20 (7 While-body sites): CLFN moved first, then OpCreateConstOnTerm_v0 (WhileLoop[i].Diagram.Nodes[n].Terms[6]) created
   the constant in place, t6 wire non-zero. connect_from_wire(sink t8 <- Wire(site wire).Terms[source]) returned err '' and
   Is Broken? False but Wire count delta 0 (my gate expected +1).
 - E1 ExecState 0 at the end; computation_diff(S1, new) rows 0, removed 0, added 25 = CallLibrary + DigitalNumericConstant + 9 Invoke.

MY EXPLANATION (the claim to attack):
 1. GObject.Move of the two ends one at a time DROPS the wire between a top-level constant and a node once the node crosses into a
    nested diagram (no tunnel is auto-created by scripting, unlike a GUI drag); so a typed constant must be created IN PLACE with
    Terminal.Create Constant addressed through the owning Loop (WhileLoop or ForLoop [i].Diagram.Nodes[n]). A case FRAME cannot be
    addressed this way (CaseStructure has Diagrams[], no Loop.Diagram), so sites 6/7/14/15 are skipped in run 2.
 2. Wire delta 0 on connect_from_wire is the expected BRANCH outcome (skill law: a successful branch adds no Wire object); the right
    gate is the sink terminal's wire uid == the site wire (read by node_terms).
 3. ExecState 0 came from the 9 leftover junk `Invoke` nodes (unwired `reference` - docs/NAMES.md:307-313) minted by build_clfn /
    the creators, which run 1 purged only after connect_from_wire; run 2 purges after every creator.

ALREADY RULED OUT: the moves themselves erroring (err '' on both, node found on Diagram[43] uid echo); tunnels being created (censuses
equal); OpCreateConstOnTerm_v0 failing on While bodies (7/7 created, t6 wired).

Give: the strongest reason any of 1-3 is wrong; an alternative explanation for t6 wire 0 after the moves and for ExecState 0; what
would falsify each; the cheapest discriminating test. Also: is there ANY scripting route (VI Server method on Terminal / Diagram /
CaseStructure frame) to put a typed, wired constant on a node inside a case frame with the ops this project owns
(docs/toolkit-capabilities.md rows 69-71)?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: parts of all three claims are wrong. Claim 2 holds, but for evidence the claim never cited. Claim 3 names the wrong source for the junk and never measured the cause. Claim 1 was inferred without any measurement, and its main conclusion, that case frames are unreachable, is false.**

## 1. Strongest reason the claim is wrong: claim 3 blames the wrong op

The 9 leftover `Invoke` nodes come from `move_in`, one per call. Neither `build_clfn` nor the constant creators left them:

- **`build_clfn` cleans up after itself.** It deletes its own junk Invoke (`tools/gscript.py:3002-3005`).
- **Constants are not in the node census.** The census counts `report_all('Node')` (`tools/recipes/build_d1_m3a1.py:487-492`). The main VI's census by class has no numeric-constant class (`docs/NAMES.md:341-344`). So a new constant adds 0 rows.
- **The arithmetic matches exactly if each move adds one node:**
  - Site 0: 625 before move 1 → 626 before move 2 (`diag_c90_t0_step3.log:26,28`). That is +1 with nothing but a move in between.
  - Site 0's second move, plus site 2's CLFN build: 626 → 628 at `:33`.
  - Site 2's move plus its constant: 628 → 629 at `:33→37`. Move +1, constant 0.
  - Site 8: 629 after purge → 630 at `:60` (CLFN build only).
  - The scratch run shows it too: 625 → 627 across one move plus one build (`diag_c90_t0_place.log:28,34`).
  - Nine `move_in` calls (2 at site 0, 1 at each of 7 sites) = 9 Invokes, which is exactly `added 25 = 8 CLFN + 8 constants + 9 Invoke` (`:198`).
- **This was seen before.** `docs/cycle27-plan.md:2562` records "the same junk `Invoke` cycle 62's `move_in` purged (#9317)".

Run 2's purges will probably catch these anyway, but by accident. The "after const" purge compares against the census taken *before* the move (`tools/stagekit.py:552-568`). That makes it only as reliable as the claim that no constant is ever counted as a node.

The cause is also unmeasured. The ExecState timeline has only two readings: 1 after open, 0 after all sites (`t0_sites_s1_step3.json:10-31`). Every per-connect reading was 0, and each was taken while that connect's own junk still existed. Nobody ever read ExecState with zero junk present.

## 2. Alternative explanations

**For ExecState 0 (other things present when E1 was read):**
- **(a)** Site 0's CLFN is still in Diagram[43] with t6 **and** t8 unwired. Its constant is left orphaned.
- **(b)** A type the Call Library node refuses to adapt. t8 is "Adapt to Type" with the Constant flag, passed by value (`diag_c90_t0_step3.py:54-55`). NI documents that Adapt to Type breaks the node for some data types, e.g. an array of strings inside a cluster ([NI forum](https://forums.ni.com/t5/LabVIEW/Call-Library-Function-Adapt-Interface-to-Data-Breaking/td-p/3832312), [NI KB](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L0sSAE)). The display-body wires (w19372/19465/19468/19429) could carry image references or clusters. `Is Broken? False` describes the *wire*, not whether the node accepts the type.

**For t6 reading 0 after the site-0 moves:**
- Nothing ever showed that t6 was wired *before* the moves. Gate S00.2 checks only the returned uid and err (`:25`).
- `OpCreateConstTop_v0` has been measured only on a For loop's N terminal (`docs/NAMES.md:320-323`). "Any top-level node terminal works too" is a docstring claim (`gscript.py:2640`).
- So "the constant was never wired to a CLFN parameter" has not been ruled out.
- Even if it was wired, the run cannot tell which of the two moves dropped the wire.
- The claim also says "no tunnel is auto-created by scripting". That is true only of `Move`. `Terminal.Connect Wire` across a boundary *does* create tunnels: the NI forum says "the tunnel will automatically be connected for you" ([NI forum](https://forums.ni.com/t5/LabVIEW/Programmatically-creating-a-tunnel-with-LV-scripting/td-p/1830745)), and it was measured here as `LoopTunnel 0 → 2` (`docs/toolkit-capabilities.md:73`).
- The LabVIEW Wiki page for `GObject.Move` says nothing about wires ([labviewwiki](https://labviewwiki.org/wiki/GObject_class/Move_method)).

## 3. What would falsify each claim

- **Claim 1:** reading the top-level t6 wire right after `create_const_loop_term` gives 0. The fault is then the creator, not `Move`. Or: case-frame sites succeed through the route in section 5.
- **Claim 2:** already settled in its favour. The connect op's own readback is `UID 2` = the sink terminal's wire, and it equals the site wire at all 7 sites (5859, 541, 19372, 19465, 19468, 19429, 34066; `t0_sites_s1_step3.json:66,91,116,141,166,191,216`). The branch landed. Cite this, not "delta 0 is expected".
- **Claim 3:** after deleting every new Invoke that has no wired terminal, ExecState is still 0.

## 4. Cheapest discriminating test

One scratch run with no rebuild and about 8 LabVIEW calls:

1. **Site 0 only:**
   - `create_const_loop_term` → read t6 at top level with `node_terms(W, 0, n)`.
   - Move the CLFN → read t6.
   - Move the constant → read t6.
   - Take a node census around each move.

   This settles when (or whether) the wire existed and dropped, and confirms that each `move_in` adds 1 Invoke.
2. **Replay run 1's 7 While-body sites, then bisect ExecState:**
   - Delete the new zero-wired Invokes (expect 9) → read ExecState.
   - If it is 0: delete site 0's CLFN → read ExecState.
   - If still 0: delete one site CLFN at a time → read ExecState after each. The site that turns it to 1 names the refused Adapt-to-Type type.

## 5. Case frames are reachable with ops the project already owns

"A case frame cannot be addressed" is only true of `OpCreateConstOnTerm_v0`'s `Loop.Diagram` route. The `Traverse('Diagram')[i]` route addresses frames. This run's own `find_node`, `node_terms` and `connect_from_wire` all index by Diagram number, and the frame sites 76, 75 and 132 are in that same index space.

Route with existing ops:
1. `OpCreateConstTop_v0` on the top-level CLFN's t6. The constant comes out typed I32 with its value set.
2. `move_in` the CLFN and then the constant into Diagram[frame]. The wire drops, as run 1 showed, and the junk from each move is purged.
3. `OpConnectNested_v0` (or `_v1` with both indices set to the same diagram) on Diagram[frame]: sink = CLFN t6, source = constant t0.
4. Read the value back with `OpConstValueN_v1`.

No tunnel is created, so rule 1a is safe. One caveat: `_v0` is verified for wire identity but not for ExecState (`toolkit-capabilities.md:72`).

`OpCreateConst_v0` is **not** a usable route: it produces an empty-valued `Constant` (`toolkit-capabilities.md:69-70`).

A cleaner alternative is a new op, which the standing tool permission allows: `OpCreateConstOnTerm_v0` with its ladder head swapped for `OpConnectNested_v0`'s `Traverse('Diagram')[i] → To More Specific Class → Nodes[]` sink ladder.

## Side hazard: purged uids are reused

After every purge, the next new CLFN gets the uid of the Invoke just deleted, 6 times in a row:
- #23402 at `:40` → `:59`
- #23477 at `:67` → `:81`
- #23898 at `:89` → `:103`
- #23910 at `:111` → `:125`
- #24309 at `:133` → `:147`
- #24513 at `:155` → `:173`

Any cached uid set, such as `new_since` or the "still present" checks, can alias across a purge.

## Sources

(extract from answer)

## What was done with it

Read by the card 90-5 material session (fable/low) at 04:48, after its 70-min budget was nearly spent; NO second LabVIEW
run was launched on it. Accepted as facts, applied to `tools/bench/diag_c90_t0_step3.py` before any rerun:
- §1 the 9 junk Invokes are `move_in`'s (one per call, census arithmetic `diag_c90_t0_step3.log:26-37`), not `build_clfn`'s
  — the script's docstring said "build_clfn / the creators"; run 2's `junk_purge` after every `_op` still deletes them (the
  mark is taken before each move), so the code stands and only the attribution was wrong.
- §3 claim 2 is settled by the op's own `UID 2` readback (= the site wire at all 7 sites) — run 2's gate reads t8 through
  `node_terms` (the same fact by another reader); cite `UID 2` too.
- §2(a)/(b) + §4 step 2 (bisect ExecState 0: purge the zero-wired Invokes, then delete site 0's CLFN, then one CLFN at a
  time — an Adapt-to-Type refusal on a display-body wire is a live alternative) — NOT run; it is the next cheapest test.
- §5 case frames ARE reachable (`OpCreateConstTop_v0` at top level → move both → `OpConnectNested_v0/_v1` on Diagram[frame]
  const t0 → CLFN t6, no tunnel) — a design choice for the judgement session (run 2 as written SKIPS sites 6/7/14/15).
- Side hazard (purged uids reused by the next CLFN, 6 times) noted; run 2 addresses nodes by uid echo after each find_node.
Left for judgement: whether to rerun the patched script (13 sites) or first add the §5 route (17 sites); whether the §4
bisect runs before either. Rule 1a is unaffected (stamps read time only).
