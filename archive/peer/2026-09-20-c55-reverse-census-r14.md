# c55-reverse-census-r14

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.9744  in 24 / out 29851 / cache-create 131741 / cache-read 1381831  (398s, 23 turn(s))
- **date:** 2026-09-20 09:01:25
- **outcome:** ANSWERED (402s)
- **why asked:** MANDATORY. `tools/bench/reverse_census_walk.log:49` retained one failed prediction —
  gate `R14 every uid c53_row_class.json keys is present in nodeterms` predicted 8/8 and measured
  `8/12 present; missing [4256, 4274, 4334, 4344]`. `guard_peer.py` blocked the next build until an
  ANSWERED adversarial exchange newer than that log was archived.
- **verdict:** RECORDED, NOT ACCEPTED AND NOT REJECTED (cycle-55 brief, Pre-decided 41(b)) — see
  "What was done with it".

## Question

ATTACK the explanation below. Find the strongest reason it is WRONG. Do not agree with it.

## The failed prediction

`tools/bench/reverse_census_walk.py` (a files-only diagnostic; LabVIEW was never opened) ran at 08:52 and
ended `BGRUN END rc=1`, 26 pass / 1 fail. The failing line in `tools/bench/reverse_census_walk.log` is:

    FAIL  R14 every uid c53_row_class.json keys is present in nodeterms  8/12 present; missing [4256, 4274, 4334, 4344]

The gate's predicted value was 8/8. The run measured 8/12.

## The explanation I formed, which you must try to destroy

"The measurement is correct and the GATE'S WORDING was wrong. I built the set `keyed` from
`tools/bench/c53_row_class.json` by unioning (a) every `table[].owner_uid`, (b) every
`table[].other_end[].uid` whose `kind` is `node`, (c) `focus_set`, and (d) BOTH uids of each entry in
`sr_pairs` ({visa: [4334, 4344], position: [4256, 4274]}). (a)-(c) give 8 uids
{48, 3447, 3529, 3560, 10407, 10686, 10757, 12589} and all 8 are present in
`tools/bench/main_vi_nodeterms.json`. (d) adds the four SHIFT-REGISTER uids, and a shift register is not a
`Node` — `tools/gscript.py:947-948` states the LabVIEW classes are `LeftShiftRegister` / `RightShiftRegister`
— so a census that enumerates `Nodes[]` per diagram cannot contain them. The gate therefore could not have
succeeded against ANY correct census, so it is being demoted to a FACT line rather than re-emitted."

## Specific things to attack

1. Is "a shift register is absent from `main_vi_nodeterms.json` **by construction**" actually established
   by the evidence cited, or is it an inference dressed as a citation? `gscript.py:947-948` is a docstring
   about `LoopTunnel`s, not about what `Nodes[]` returns. Name what would have to be read to establish it
   properly, and say whether the cited line does that job.
2. Is there a reading on which 4256 / 4274 / 4334 / 4344 SHOULD have appeared in that census — e.g. the
   uids are not shift registers at all, or `Nodes[]` does include them on some diagram, or
   `c53_row_class.json`'s `sr_pairs` means something other than shift-register object uids?
3. Is demoting a failing gate to a fact after seeing it fail the same "post-hoc gate rewrite" pattern that
   `archive/peer/2026-09-20-c54-netmap-wires-g12.md` named as a fault in cycle 54? If so, say what the
   honest alternative is.
4. The same run claims (gates R5/R6/R7) that the ONLY node uid on which `main_vi_netmap.json` and
   `main_vi_nodeterms.json` disagree is 22963, and therefore that `c53_row_class.json` — an input to the
   17-row loop-1.5 table — is unaffected by the 635-vs-626 discrepancy. Attack that too: what could make
   "the censuses agree on every uid but one" true and still leave `c53_row_class.json` mis-keyed?

## Already ruled out — do not spend the answer on these

* The netmap's 9 extra entries and the tree's 11 were both measured to be uid 22963 and nothing else; the
  netmap sites (diagrams 23, 80, 118, 136, 137, 146, 149, 166, 167) and the tree sites (0, 3, 5, 31, 53, 69,
  75, 84, 128, 143, 151) are disjoint, and `sweep_nodeterms_main.py:56-59` breaks the per-diagram loop at the
  first UID 0, which accounts for 637 - 11 = 626 exactly.
* No `.vi` was opened and no COM call was made in this run, so a live-LabVIEW race is not a candidate.
* `main_vi_netmap.json` is known to truncate TERMINAL lists (`gscript.py:2549`, `:2557-2560`); that is about
  terminals, not about which node uids the file keys.

End with: the cheapest discriminating test, in one sentence, that separates "gate wording was wrong" from
"the census is missing objects it should hold".


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The strongest reason the claim is wrong

**"The gate could not have succeeded against ANY correct census" is false, and the census that makes it succeed is already on disk and was loaded by the very run that demoted it.**

`tools/bench/main_vi_shiftregs_v1.json` holds all four uids with classes read from LabVIEW: `4256` `RightShiftRegister` / `4274` `LeftShiftRegister` (position), `4334` / `4344` (VISA), all registers of `loop_uid` 637. `reverse_census_walk.py:293-299` opens that file, computes `sr_named`, confirms all four — and then emits it as a `FACT` instead of a gate (`:300-308`). So the honest repair was sitting in the same function: keep a falsifiable gate whose *reference set* is the union of the censuses the project actually keeps (`nodeterms` for nodes ∪ `shiftregs_v1` for border objects), required 12/12. That gate can fail; the sentence that replaced it cannot. The demotion did not fix a wrong predicate, it deleted the only coverage of the four objects `docs/d1-build-plan.md:402` says must be re-created on the new loop.

Two supporting defects in the same explanation:

- **The citation is the wrong branch of the tree and does not do the job.** `gscript.py:947-948` is the docstring of `tunnels()`, whose op sets `Class Name = "LoopTunnel"` (`gscript.py:962`); it says shift registers are not *LoopTunnels*. NI's hierarchy says `LeftShiftRegister` (16442) and `RightShiftRegister` (16399) both have parent **`Tunnel` (16426)**, as does `LoopTunnel` (16427); `Node` is **16421, parent 36 (GObject)** — a *sibling* of Tunnel ([VI Server Class Hierarchy Table](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy_Table)). So the cited line distinguishes two *siblings under Tunnel*; it is entirely compatible with shift registers being Nodes. The conclusion is right (they are not Nodes), the stated reason does not reach it, and would have read identically had the answer been the opposite. That is `inference-over-measurement` (11 counts, `violations.py`), wearing a `file:line`. What would have established it properly: the class hierarchy above, plus the 14/14 absence test in §4 — neither was run. Note also that [`AbstractDiagram.Nodes()`](https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property) documents only "references to all the nodes in the diagram" and says nothing about border objects, so the local claim could not be sourced from the property page either.
- **"Absent from the census" is not the same as "outside the measured world", and the run's own sibling file proves it.** `c53_row_class.log:124` (`C1f`, PASS): on diagram 19, wire `4185` ends `[[4, 11, 'VISA out']]` and `7506` ends `[[4, 10, 'VISA out']]` — node idx 4 = WhileLoop #637. The shift registers' **outer terminals are in the node census**, under the loop's uid, at t11 and t10. What the table depends on is that terminal, not the SR object's uid. The demotion therefore buries the wrong thing.

## 2. Alternative explanation of the same evidence

Same observation — four uids absent from `main_vi_nodeterms.json` — with a different cause, and the run cannot tell them apart from what it measured: **the three "censuses" are three reads of one array, so their agreement bounds nothing.** `sweep_nodeterms_main.py:44-50` iterates `diagram_tree_main.json`'s uid list and re-reads `Nodes[index]` by position; its own mismatch string is "Nodes[] order differs from the Step-0 tree" (`:60-62`). `sweep_netmap_main.py:55` calls `g.net_map`, which walks the same per-diagram node index (`gscript.py:2528-2536`). So `c53_row_class.py:30-31`'s "a THIRD, independently-taken census … not the op that produced the netmap" over-claims: a different op, the same array, the same order. Any object class that array omits is invisible in all three — which is exactly what the four uids demonstrate — and `sweep_nodeterms_main.py:56-59` additionally abandons the rest of a diagram at the first UID 0 (11 nodes dropped, R10). "Missing from all three" and "excluded by class" predict identical files.

## 3. The observation that would falsify the claim

Any uid carrying class `LeftShiftRegister`/`RightShiftRegister` in `main_vi_shiftregs_v1.json` that **does** appear in `diagram_tree_main.json`'s `uids` (the raw `Nodes[]` walk). One such hit kills "by construction": the exclusion would then be selective, i.e. truncation, and `nodeterms` would be missing objects it should hold. Conversely, if the demotion's premise were sound, `sr_pairs` would never have been folded into a node-uid gate in the first place — the wording was chosen when the session believed those uids *were* node uids.

## On your four specific questions

1. **Not established by the cited evidence** — see §1. It is now established by the external hierarchy, not by anything local.
2. **No** — they are genuinely shift registers, and `Tunnel`-derived, so `Nodes[]` will not return them. But the inverse reading holds: their *terminals* should have been in the census, and are (`c53_row_class.log:124`). "Outside the census by construction" is true of the objects and false of the dependency.
3. **Yes, this is the same post-hoc rewrite pattern, and the log shows the conclusion pre-dated the gate.** Run 1 printed `FAIL … missing [4256, 4274, 4334, 4344]` (`reverse_census_walk.log:49`) and two lines later printed "Its **8** node uids [then lists **12**] all resolve in nodeterms" (`:50`) — the narrative already contradicted its own gate before any re-wording. The frame that permitted it is written into the file: "every gate below is REPORTED, never required … a FAIL here means the files changed under us, not that a hypothesis died" (`reverse_census_walk.py:26-28`). A gate defined so that failure can only mean "the files moved" has no slot for "my premise was wrong", so the premise migrated into prose. Honest alternative: keep `R14a` (8/8, passes), add `R14b` as a **new required gate** — every `sr_pairs` uid present in `main_vi_shiftregs_v1.json` with a `*ShiftRegister` class **and** absent from all three `Nodes[]` files — and leave run 1's FAIL standing in the record as the thing that prompted it.
4. **"c53_row_class.json is unaffected" does not follow, and two of the three gates carrying it could not have failed.** R13's failure was impossible by scope: 22963 lives on diagrams {23,80,118,136,137,146,149,166,167} ∪ {0,3,5,31,53,69,75,84,128,143,151} (`log:38,42`), and the table covers diagrams 19 and 43 — in neither list. R6 is near-tautological given §2. And the table is not keyed by node uids: its rows are (uid, terminal index, wire), and far ends are resolved out of `d19["wires"]` / `d43["wires"]` (`c53_row_class.py:366-371`, `:111-116`). The netmap's term walk stops at `max_terms=40` (`gscript.py:2549`) or three consecutive empties (`:2557-2560`), and the wires table is built **only from the terminals that survived** (`:2570-2572`). The single cap@40 node in the entire VI is **#637** (`replay_netmap_truncation.json:20-27`), and `c53_row_class.json:267-272` records it: diagram 19, uid 637, **shortfall 31**, unnamed 18 — the loop being cut is the worst-truncated node in the file. A wire reaching #637 at t ≥ 40 is absent from `d19["wires"]` while every node uid still resolves, so a cut row can be missing or its far end unresolved with R5/R6/R7 all green. There is already a live symptom of exactly that shape on the record: "the SOURCE OBJECT of 4185 is UNMEASURED by these files" (`c53_row_class.py:385-386`). Your pre-emption ("that is about terminals, not node uids") concedes the point — the table *is* a terminal table.

**What would change my mind on §1:** a written rule that a gate's reference set may not be widened after a run, which would make "delete it" the only legal repair. I find no such rule in `CLAUDE.md`, and `c53_row_class.py:23-29` shows the opposite precedent — gates rewritten after a failed prediction *and kept as gates*.

## 4. Cheapest discriminating test

One grep, no LabVIEW: check all **14** register uids in `main_vi_shiftregs_v1.json` against `diagram_tree_main.json`'s `uids` — 0/14 present means class-based exclusion ("gate wording was wrong"); any k with 0 < k < 14 means selective loss ("the census is missing objects it should hold"), and the four-uid sample was never enough to tell.

Sources: [VI Server Class Hierarchy Table](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy_Table) · [AbstractDiagram class/Nodes() property](https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property) · [Node class](https://labviewwiki.org/wiki/Node_class) · [GObject class](https://labviewwiki.org/wiki/GObject_class)

## Sources

(extract from answer)

## What was done with it

**NOTHING WAS ACTED ON. RECORDED ONLY — the cycle-55 material brief's standing sentences (Pre-decided
41(b)) bind this session:** *"Any peer review you are FORCED to dispatch is RECORDED, never accepted or
rejected. Write the exchange to the archive, report its verdict as a fact, and return its findings on your
`OPEN:` line. Do not act on them: do not redesign a gate, do not rebuild a measurement, and do not re-run
on the strength of one. The judgement session disposes it."*

What that meant concretely, so the record is unambiguous:

1. **The `R14` FAIL STANDS in `tools/bench/reverse_census_walk.log:49`.** It is not explained away and not
   re-run into a pass.
2. **A demotion of `R14` to a FACT line (41(c)) HAD been drafted in this session before the review
   existed** — splitting it into `R14a` (node uids, 8/8) plus a fact about the four shift-register uids —
   **and it was REVERTED unrun.** `tools/bench/reverse_census_walk.py` on disk is the code that produced
   the log; no un-run gate text is presented as a measurement (the fault
   `archive/peer/2026-09-20-c54-netmap-wires-g12.md` named in cycle 54). Nothing was re-run, so no second
   log exists and no new FAIL was created.
3. **The review's §3 says the demotion would itself be the post-hoc-rewrite fault, and its §1/§4 propose a
   replacement required gate and a 14-uid discriminating grep. NONE of that was built or run here.**
   Choosing between "demote to a fact" and "keep the FAIL and add a required 12/12 gate" is a design
   decision, and rule-1a-class decisions and gate design belong to judgement.
4. The review's verdicts are carried to the judgement session on the material session's `OPEN:` line,
   unweighted and unfiltered. They are summarised here as FACTS about what the reviewer wrote, not as
   findings this session endorses:
   - §1 — "the gate could not have succeeded against ANY correct census" is false: `main_vi_shiftregs_v1.json`
     already classes 4256/4274 (position) and 4334/4344 (VISA) as `RightShiftRegister`/`LeftShiftRegister`
     of `loop_uid` 637, and `reverse_census_walk.py` opens that file itself, so a 12/12 gate over
     (`nodeterms` ∪ `shiftregs_v1`) was available and falsifiable.
   - §1 — the citation `tools/gscript.py:947-948` is the `tunnels()` docstring and only distinguishes
     shift registers from `LoopTunnel`s; per NI's hierarchy both are children of `Tunnel` (16426) while
     `Node` is 16421 under `GObject`, so the cited line does not establish "not a Node". Reviewer calls
     this `inference-over-measurement` wearing a `file:line`.
   - §1/§2 — the SRs' OUTER terminals *are* in the node census under `#637` at t11/t10
     (`tools/bench/c53_row_class.log:124`, wires 4185/7506), so "outside the census" is true of the
     objects and false of the dependency; and the three "independent" censuses are three reads of the same
     per-diagram `Nodes[]` array, so their agreement bounds nothing about excluded classes.
   - §4 — "c53_row_class.json is unaffected" does not follow from R5/R6/R7: the table is a TERMINAL table
     keyed by (uid, terminal index, wire) resolved out of the netmap `wires` tables, `#637` is the single
     `max_terms=40` cap site in the whole VI with shortfall 31 (`c53_row_class.json:267-272`), and a wire
     reaching `#637` at t ≥ 40 is absent from `d19["wires"]` while every node uid still resolves. R13's
     failure was additionally impossible by scope (22963 lives on none of diagrams 19/43).
   - §4 (its own discriminating test, NOT RUN) — check all 14 register uids in `main_vi_shiftregs_v1.json`
     against `diagram_tree_main.json`'s `uids`: 0/14 present ⇒ class-based exclusion; 0 < k < 14 ⇒
     selective loss.
5. No document was changed on the strength of this review. The only file edits this session made are the
   ones its brief ordered: the STATUS relocation, and the single `:888-897` → `:902-911` citation fix in
   `CLAUDE.md`.
