# c87-errorlist-extras

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4531  in 20 / out 18949 / cache-create 103832 / cache-read 941743  (212s, 14 turn(s))
- **date:** 2026-09-26 00:37:08
- **outcome:** ANSWERED (216s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim (cycle 87 firefighter; failing log tools/bench/c87_errorlist_reverdict.log, script tools/bench/c87_errorlist_reverdict.py).

CONTEXT. The cycle-start Error List check (tools/errorlist_check.py) read 35 items from a scratch copy of the L2-A1
bed claudeDev\D1_l2_a1_20260925_235224.vi (ExecState 0 BY DESIGN: 9 sinks are left open for the next stage, listed as
`open_rows` in tools/bench/sim/l2a1/plan_l2a1.json). The checker licenses items derived from open rows (per-node
"not wired"/"unwired or bad terminal" and, class-level and UNCAPPED, the half-wire classes WIRE_CLASSES at
tools/errorlist_check.py:324). Cycle 87's verdict was MISMATCH with 35 extra because plan_for_bed() only looked in
tools/bench/, not tools/bench/sim/<stage>/ (patched). With the plan found: 10 licences, 24 items licensed, 11 extra
(tools/bench/c87_errorlist_reverdict.log:5-39):
  9 x "This wire is not connected to anything." (detail: "This is a completely unconnected wire.")
  1 x "You have connected an input of Less? to a right shift register. Change the input to an output, or add a
      source." (detail: "This wire is connected to two data sinks but zero sources.")
  1 x "Polymorphic terminal cannot accept this data type."

CLAIM under attack.
(1) The 9 fully-unconnected wires are open-row consequences: a move_in of a node into the loop body cuts BOTH ends of
    the wires that fed the now-open sinks, leaving fragments with no end at all, whereas "Wire has loose ends" is
    the one-end-cut case. So "isnotconnectedtoanything" belongs in WIRE_CLASSES (class-level, uncapped), like
    "wirehaslooseends" already is.
(2) The Less?-to-right-shift-register item is the sinks-only-wire class already licensed for "output loop tunnel to
    an input" (identical detail text "two data sinks but zero sources"); Less? is #11529 whose 'x' IS an open row.
    So "zerosources" belongs in WIRE_CLASSES.
(3) The one "Polymorphic terminal cannot accept this data type." item is NOT explained by any open row and must stay
    `extra` (MISMATCH with 1 extra), to be located by the read-only P2 check of PD194(a) (docs/d1-loop12-17-split-plan.md:990)
    on the five re-wired rows sr1_L0, sr2_L0, sr3_L0, tun1, tun2 (SelectorTunnel outer faces), or by a Selection List[]
    reader that does not exist yet.

Evidence you may read: tools/bench/c87_errorlist_reverdict.log, tools/bench/errorlist_D1_l2_a1_20260925_235224_20260926_001456.json
(items[] with raw/detail; the uid of each item is NOT read - uid_route says why), tools/bench/stage_d1_l2a1.json
"facts" (CDIFF ROW lines = the 9 open rows before/after; "RBW deleted [...]" = 29 bad wires removed on a scratch,
none on a re-wired sink), tools/errorlist_check.py:316-368, tools/lv_errorlist.py:1080-1100.

Already ruled out: an expected-errors file (none exists for this bed; expected_file null); the bed md5 changing
(unchanged 51d9b8a3...); OCR merging rows (n_reported 35 == items 35).

Questions: the strongest reason (1) or (2) is WRONG (e.g. a fully-unconnected wire that a stage-wired row LEFT
BEHIND rather than an open row); an alternative explanation for the polymorphic item that the open rows DO cover
(would that make (3) too strict, or is keeping it extra right); what would falsify each; and the cheapest
discriminating test that needs no new LabVIEW op.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: (1) is wrong about the cause, and (2) is wrong in a way that matters: licensing "zerosources" would probably hide a broken row that the stage wired itself. (3) is right to keep the item as extra, but it points at the wrong rows.** One more thing to know first: `WIRE_CLASSES` at `tools/errorlist_check.py:324-330` already contains both new classes, so this patch is live and is currently absorbing items.

## 1. Strongest reason the claim is wrong

**(2) The zero-sources wire is almost certainly on the `sr3_R` net, a row the stage wired itself.**
- Less?'s `x` (#11529) was originally fed through tunnel #11336 (`stage_d1_l2a1.json:858`: sources `10150 x+1 @11336/f1` and `9907 Value @11336/f0`).
- The plan's `sr3_R` row wires that same source, #11336 term 11346, into `SR3R.inner` (`plan_l2a1.json:268-276`).
- The bed did not do that terminal-to-terminal. It ran `connect_from_wire sink D[19].N[22].t14 <- w11253[0]` (`stage_d1_l2a1.json:776`). That attaches the new shift register's right face to the *existing wire*, not to terminal 11346.
- The error text "input of Less? connected to a right shift register … two data sinks but zero sources" is exactly this result: SR3R.inner and Less?.x sit on w11253, and 11346 is no longer on it.
- In the simulator, SR3R.inner has a source (11346). In the bed it has none. SR3's right face is not an open row, and CDIFF only checks the 9 listed sinks (`:850-858`), so nothing compared it.
- If this is right, SR3 carries no value into the next iteration. That is a computation change under rule 1a, not a by-design gap.
- A class-level, uncapped "zerosources" licence would hide this permanently, and on every later bed too.
- One more point: `P2 sr3_R` was only checked with "E1 + RBW (+CT) only" (`:828`), and the `sr3_L0` second pass crashed with `#10750 not in Diagram[21].Nodes[]` (`:829-830`). Nothing has verified SR3.

**(1) The fully-unconnected wires cannot come from open rows.**
- No open-row sink node was moved. The moved set is #5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 17487, 5634, 23541, 10739, 10929, 17272 (`:753-766`). The open-row nodes are 376, 2626, 5058, 5696, 6085, 9703, 10382, 11529. The two sets do not overlap.
- A wire that lost its source but still touches an unmoved open sink is still connected to that sink. LabVIEW reports that as "has no source" (4 items) or "loose ends" (14 items), never as "a completely unconnected wire".
- A wire with no end at all needs both endpoints detached. That happens when both nodes were moved. Seven `rw_*` rows reconnect exactly such pairs in the new body: 5634→10247, 10739→10950, 10929→10757, 10969→17272, 10950→9647, 17289→10950 and 17487→9647 (`plan_l2a1.json:366-485`). Their old wires stay behind, fully detached.
- So these 9 items are leftovers from the move list plus the re-wire rows. They are probably harmless, but the stated mechanism is wrong. Because the number is derivable, it can be capped instead of uncapped. The licence is also gated on `open_rows` being present (`:377`), which is the wrong condition.
- NI documents the two errors as separate wire states: [Wire has loose ends](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/wire-has-loose-ends.html) and [This wire is not connected to anything](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/wire-is-not-connected.html). The page body did not render for me. The local detail text ("This is a completely unconnected wire.") is the authority here. Loose wire fragments left by moves and deletions are a known LabVIEW behaviour ([NI forum](https://forums.ni.com/t5/LabVIEW/Invisible-wire-ever-see-this/td-p/1066448), [Remove Wire Loose Ends](https://labviewwiki.org/wiki/AbstractDiagram_class/Remove_Wire_Loose_Ends_method)).

## 2. Alternative explanation for the polymorphic item: open row #9703 is not actually open

- The bed's CDIFF shows #9703's `x` has a source after the stage: `23541|ControlTerminal|index|0@10978/f1`. Before, it was `10757|element` (`:856`). The simulator predicted it would be open (`plan_l2a1.json:585`).
- So in the bed, 9703.x is fed through tunnel 10978 by the `index` control that the stage moved in (mv_23541). This is a different, and probably differently typed, source from the original `element`.
- The counts support this. Four non-SubVI open nodes (2626, 9703, 10382, 11529) produced only **three** "Contains unwired or bad terminal" items (Not, BuildArray, Less?). Because `node_unwired` licences do not carry the node's identity (`:374`), the missing one shows up as `USED 0` on 11529 (log:24). The node that is actually silent is most likely 9703: it is not unwired, it is wired to the wrong thing, so LabVIEW reports the wire instead ([NI: Polymorphic terminal cannot accept this data type](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/polymorphic-terminal-cannot-accept-data-type.html), [forum example](https://forums.ni.com/t5/LabVIEW/Polymorphic-terminal-cannot-accept-this-data-type-error/td-p/4188757)).
- Verdict on (3): keeping it as **extra is right**. It must never be licensed, because it is evidence that the bed and the simulator disagree on an "open" row. But the P2 target list should start with **9703 / 10978 / 23541**, not the five SR/tunnel rows. The item is not grounds for a new Selection List[] reader until this cheaper check has run.

## 3. What would falsify each part

- **(1)** Count the base-graph wires (`graph_k_80_owners.json`) whose endpoints all lie in the moved set, allowing for branches. About 9 means "move-pair leftovers", not open rows. Finding a completely unconnected wire whose former endpoint is an open-row sink would support the claim.
- **(2)** Find which right shift register the Less? wire touches. If it is a pre-existing SR on another loop, and SR1R/SR2R/SR3R.inner each have a real source, my objection falls.
  - One caveat on "RBW deleted 29, none on a re-wired sink". If RBW removed the Less?–SR3R wire and that check still passed, the check cannot see `new:`-addressed sinks (SR faces, tunnels). That is plausible, but I have not verified it.
- **(3)** If 9703.x's source really has the same type as the original `element`, the 9703 theory fails, and the SR/tunnel rows become the suspects.

## 4. Additional finding

The existing `outputlooptunneltoaninput` licence may already be hiding 2 defective stage rows.
- Its two items say "output loop tunnel to an input of SubVI", with the same "zero sources" detail (json:232, :272).
- There are exactly two stage rows that wire tunnels into SubVI #5058: `rw_6007_5082` and `rw_6026_5164` (`wire_tunouter SelectorTunnel #5680/#6016 -> SubVI[17].t0/.t7`, `:793-794`).
- If the op connected an inner (sink) face, you get exactly this message. The same fix applies: tie the licence to a derived count, not to the class.

## 5. Cheapest discriminating test (no LabVIEW)

Run one offline script over the files already on disk:
1. From `graph_k_80_owners.json`, list every base wire whose every terminal is on a moved node. Compare that count with 9.
2. List each open-row sink's original source owner, and check whether it was moved (9703's goes through 10757 and 10978). This settles (1).
3. Open the saved Error List screenshots for the Less? item and for the polymorphic item (`show_error.bd_after` in `errorlist_…_001456.json`; each double-click fronts the diagram at the fault). Check whether the highlighted wire touches the new SR3 (at the loop 10170 border) and whether the polymorphic wire enters #9703.

These captures already exist. Checking them costs no new op and splits (2) and (3) directly.

Until this is done, I'd revert "zerosources" out of `WIRE_CLASSES`. "isnotconnectedtoanything" can stay, but capped by the move-pair count and with its stated reason corrected.

## Sources

(extract from answer)

## What was done with it

Dispatched in cycle 88 by material card 88-1 (`tools/bench/cards/task_88-1.json`, part C), foreground under bgrun
(`tools/bench/peer_c88-c87-errorlist-extras.log`, BGRUN END rc=0). Per the card, `tools/errorlist_check.py` was NOT
edited on this answer: whether to revert `zerosources` / cap `isnotconnectedtoanything` is left to the cycle-88
judgement session. The same card's part A (P2 read of the five re-wired rows) and part B (Error List after RBW on a
scratch) were extended to also READ the SR1R/SR2R/SR3R inner-face nets and #9703 'x' so the review's objections (2)
and the 9703 alternative are answered by measurement (`tools/bench/p2check_l2a1_88.json`).
