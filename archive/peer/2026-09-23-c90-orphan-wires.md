# c90-orphan-wires

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.3842  in 20 / out 48885 / cache-create 146451 / cache-read 1234633  (633s, 20 turn(s))
- **date:** 2026-09-23 03:16:54
- **outcome:** ANSWERED (637s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION, cycle 68 (LabVIEW 2026 26.3.1f1, VI Scripting over ActiveX/COM, read-only measurements
on dated scratch COPIES). Attack the claim below. You have read access to the project directory; open any
file named here.

THE FAILED PREDICTION. The judgement session predicted that all 11 wires LabVIEW's Remove Bad Wires removes
from `claudeDev\D1_s3b_m3a3b_rowD_20260922_161040.vi` (md5 0b84595245dd650c0e8fd3f57104782c, 306,977 B)
would each read back BOTH of their predicted terminal endpoints: 11 agrees / 0 disagrees / 0 unread.
MEASURED: 4 agrees / 0 disagrees / 7 unread (`tools/bench/diag_c90_live_endpoints.log:99`).

THE CLAIM UNDER ATTACK (this is what you must try to REFUTE):
"Seven of the eleven wires Remove Bad Wires removes from
`D1_s3b_m3a3b_rowD_20260922_161040.vi` hold ZERO terminal rows because they are empty husks of rows M3a-1
already re-wired with new wires; therefore deleting those seven drops no data path and is NOT a rule-1a
computation change, and M3a-4's repair is only the FOUR wires that still hold one live endpoint."

THE MACHINE EVIDENCE (all under the project root; read them, do not take my summary on trust):
1. `tools/bench/diag_c90_live_endpoints.log` + `tools/bench/m3a4_live_endpoints.json` (14 gates pass / 0 fail,
   BGRUN END rc=0 after 114s). Every terminal row of each of the 11 read OFF THE WIRE with `OpWireSource_v5`
   (`Wire.Terms[]` 6371003 -> `Is Source?` 634A003), never via `wmap`/`Diagram.Nodes[]`.
   FOUR wires return exactly ONE terminal row each:
     w1731  SRC LeftShiftRegister #4344 | w3947 SRC LeftShiftRegister #4274
     w9635  SRC LoopTunnel #9641        | w7337 SINK RightShiftRegister #4334
   SEVEN return ZERO rows with an owner: 1893, 2819, 4833, 7388, 11232, 23502, 23540.
   The positive control (wires 23804, 23811) returned TWO owner rows each and put `error 1055` at exactly one
   index past the last real row - so "zero rows" is not a reader ceiling.
2. `tools/bench/diag_c90b_coverage.log` + `tools/bench/m3a4_replacement_coverage.json` (16 gates pass / 0 fail,
   BGRUN END rc=0 after 115s), run today. It enumerated M3a-1's SEVEN replacement wires from the LAST block of
   M3a-1's own log and read every terminal row of each on the live bed:
     w23804 SRC SubVI... #3529 -> SINK SubVI #48        (log :2946)
     w23811 SRC #3560              -> SINK SubVI #48        (:2966)
     w23820 SRC #3447              -> SINK SubVI #48        (:2986)
     w23829 SRC SubVI #48          -> SINK SelectorTunnel #11220  (:3006; M3a-1's log calls the sink "#10407 t3")
     w23838 SRC SubVI #48          -> SINK SelectorTunnel #11348  (:3026; M3a-1's log: "#10407 t5")
     w23847 SRC Local #23499       -> SINK Tunnel #10429          (:3046; M3a-1's log: "#10407 t0")
     w23856 SRC Local #23523       -> SINK SelectorTunnel #10978  (:3066; M3a-1's log: "#10407 t2")
   CORRESPONDENCE TABLE against the offline prediction in `tools/bench/m3a1_severed_rows.json`:
     zero-row w1893 predicted #3447 -> #48   : covered by w23820
     zero-row w2819 predicted #3560 -> #48   : covered by w23811
     zero-row w4833 predicted #3529 -> #48   : covered by w23804
     zero-row w7388  predicted #48    -> #10407 : NOT COVERED (the replacement's sink reads #11220/#11348)
     zero-row w11232 predicted #48    -> #10407 : NOT COVERED (same)
     zero-row w23502 predicted #23499 -> #10407 : NOT COVERED (replacement w23847 sink reads Tunnel #10429)
     zero-row w23540 predicted #23523 -> #10407 : NOT COVERED (replacement w23856 sink reads #10978)
     one-row  w1731 (#4344->#48), w3947 (#4274->#48), w7337 (#10407->#4334), w9635 (#9641->#10407): all NOT COVERED
   COUNTS: zero-row covered 3 of 7 ; one-row covered 0 of 4.
   Negative control: never-allocated uid 999983 returned 1 row, 0 owners, uid echo 7448 (MISMATCH, caught).
   Positive controls w25324 (#23868 -> #7468) and w7448 (#7468 -> #29815) each returned 2 owner rows.
3. `tools/bench/diag_c89_wirebirth.log` - a bisection across 10 saved stage artefacts places all 11 broken
   wires at stage M3a-1 and nowhere earlier (rows 1-6 remove 0; rows 7-10 remove the identical set
   [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]).
4. `tools/bench/build_d1_m3a1.log:2754` - M3a-1's own section header: "37(d) severs every wire on the moved
   object"; `:2926` - the Wire census is UNCHANGED at 1907 across the seven `move_in` calls, i.e. wires were
   severed, not deleted.
5. `CLAUDE.md` rule 1a (behaviour-preserving refactor: the per-bead maths, the parameters that reach it and
   the numbers that come out must be identical; a change of decomposition can be a change of computation).

THREE COUNTER-READINGS THIS SESSION ALREADY HAS IN MIND - go PAST them, do not stop at them:
 (i)  `Wire.Terms[]` may simply not enumerate some terminal class, so "zero rows" would not mean "no
      endpoints". (Known: it does enumerate LeftShiftRegister, RightShiftRegister, LoopTunnel, SelectorTunnel,
      Tunnel, SubVI and Local terminals in the runs above; it does NOT enumerate a front-panel control's
      terminal through the NODE route - `tools/bench/diag_c89_wirebirth.log:85`.)
 (ii) A LabVIEW wire can exist as fragments / branch segments, so an "empty" `Wire` object may still be one
      segment of a net that does carry data.
 (iii) Owner-pair correspondence can be coincidental when `SubVI #48` and `CaseStructure #10407` each have
      many terminals, so "covered by w23820" may be matching the wrong pair of terminals.

WHAT I WANT FROM YOU
 A. The strongest reason the claim is WRONG, argued from LabVIEW's object model and from the files above.
 B. An ALTERNATIVE explanation of the 7 zero-row wires that is consistent with every number above.
 C. What observation would FALSIFY the claim.
 D. For EACH of (i), (ii), (iii) separately: the CHEAPEST discriminating test runnable over ActiveX/COM VI
    Scripting on a scratch copy, read-only if possible - name the property/method and the expected readings
    under each hypothesis. Terminal-name is NOT a readable column of our `OpWireSource_v5` route.
 E. Specifically: is there a LabVIEW property/method that answers "which net / signal does this Wire object
    belong to" or "list this wire's segments / branches" (e.g. anything on the Wire class besides Terms[],
    Is Broken?, or the diagram's SignalIndex), and can it be reached from the ActiveX `VirtualInstrument`
    interface? Search externally; absence in what we happen to have looked at is not evidence of absence.
 F. Whether the 4 NOT-COVERED zero-row rows (predicted sink #10407 vs measured sink #11220/#11348/#10429/
    #10978) are evidence AGAINST the claim, or an artefact of the offline table naming the structure instead
    of its per-case tunnel - and the cheapest read that settles which.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. The single strongest reason the claim is WRONG

**The claim's coverage premise — that each of the seven husks was a two‑endpoint net — cannot be read from the bed, and the offline table it rests on is a census that is known to drop wired terminals and is already stale at three of `#10407`'s seven rows.**

A zero‑terminal wire tells you nothing about how many terminals it *used to have*. So "covered by w23820" is an assertion about the past, sourced from `tools/bench/c53_row_class.log`'s 17‑row table — and that table has three documented defects that bear directly on this:

- **It under‑reports wired terminals by construction.** `c53_row_class.log:81-82`: gate G2c FAIL — "the per-node SHORTFALL equals that node's UNNAMED-terminal count … **unnamed-AND-WIRED terminals in `main_vi_nodeterms.json`: 156** (every one invisible in the netmap `terms` array)". A net whose third endpoint was an unnamed wired terminal looks exactly like a covered two‑endpoint husk.
- **It is measured on the ORIGINAL VI's netmap, not on this bed** — `docs/m3a1-severed-rows.md:63-64` says so explicitly. Three of `#10407`'s seven rows have since changed: t0 and t2 became Local‑fed rows (w23502/w23540, absent from c53 entirely), and **t6's live net is `23963`, not the `9113` the row inventory names** (`docs/cycle27-plan.md:2887`).
- **Fan‑out on this exact case structure has already nearly cost a data path.** `docs/cycle27-plan.md:2840-2841`: "`#10407` t6 has **TWO** sinks in the original, on net 9113: `RightShiftRegister #4256` AND `Q_focusback SelectorTunnel #12673`", and `docs/violation-decisions.md:890` records that near‑miss as a caught `unread-evidence` violation. Fan‑out is normal in this VI — `archive/peer/2026-09-17-priorart-d1-full-route-rev3.md:243` shows net 3268 with one source and **five** sinks, all enumerated by this same reader.

Each replacement wire was measured with exactly **two** owner rows (`m3a4_replacement_coverage.json`, all seven records). If any of the seven husks was a 1‑source/2‑sink net, the replacement under‑connects it, the live read can never show it, and rule 1a is broken silently. The dispatch contains no evidence either way — and "the measurement does not distinguish these two cases" is the honest verdict on the claim's central premise.

Second, smaller, but not cosmetic: **the claim is scoped to the wrong set.** Rule 1a is a statement about the 17 severed terminal rows (`c53_row_class.log:86-105`), not about wire objects. The two sets differ in both directions — three cut‑row wires (10799, 10990, 9113) are not among the 11, and two of the 11 (23502, 23540) are not in the cut census. A row whose wire was *deleted or re‑pointed* rather than left broken leaves no bad wire at all, and no amount of reading RBW's list will ever see it.

## 2. Alternative explanation of the same evidence

**The row count is fully determined by how many of a wire's endpoints sat on a MOVED node. Replacement has nothing to do with it.**

The moved set is `{3529, 3560, 3447, 48, 10407, 23499, 23523}` (`tools/bench/m3a1_severed_rows.json` "moves"; `docs/m3a1-severed-rows.md:32-38`). Cross it against the predicted endpoints:

| wire | endpoints | in moved set | rows read |
|---|---|---|---|
| 1893, 2819, 4833 | #3447/#3560/#3529 ↔ #48 | **both** | 0 |
| 7388, 11232 | #48 ↔ #10407 | **both** | 0 |
| 23502, 23540 | #23499/#23523 ↔ #10407 | **both** | 0 |
| 1731, 3947 | LSR #4344/#4274 ↔ #48 | one | 1 — *and the surviving row is always the unmoved end* |
| 7337, 9635 | #10407 ↔ RSR #4334 / LoopTunnel #9641 | one | 1 — same |

**11 of 11, no exceptions**, and it predicts the pattern from facts that existed *before any replacement wire was drawn*. `docs/m3a1-severed-rows.md:27` closes it: "19 wired terminals were severed; **0 remain wired**" — the detachment is two‑sided and happened at move time.

The consequence is what matters: **row count carries zero information about coverage**, and the claim uses row count as its repair criterion. Its own table proves the two are independent — 3 of 7 zero‑row wires match a replacement by owner pair, 4 do not, and 0 of 4 one‑row wires do. So "they are empty *because* the rows were already re‑wired" is post‑hoc attribution. If M3a‑4's four‑wire repair set turns out correct, it is correct by coincidence, not by the stated reasoning — and the same reasoning applied to a husk that was *never* replaced would delete a live row without a murmur.

## 3. What would FALSIFY the claim

**Read the seven wires on the artefact that still holds them intact.** `diag_c89_wirebirth.log` already bisected the ten saved stage artefacts and found rows 1–6 remove zero bad wires — so the pre‑M3a‑1 file has all 11 wires unbroken and enumerable. Run the identical `OpWireSource_v5` walk (n=8) on that file, read‑only, fresh instance.

- **Any of the seven returning ≥ 3 terminal rows falsifies the claim**: that net had a fan‑out the two‑terminal replacements do not reproduce, and deleting the husk *does* drop a data path.
- **Any of the seven returning a pair different from the offline table** falsifies the correspondence table wholesale.
- All seven returning exactly the two rows the table names would confirm the premise **from the machine** instead of from a stale census — at which point I would accept the claim.

This is also the project's own staged‑build pattern: the earlier file exists precisely so the next step can start from it.

## 4. Cheapest discriminating tests, per counter‑reading

### (i) "`Wire.Terms[]` may not enumerate some terminal class" — **already dead; do not spend a run on it**

Three things in the record kill it:

- **A broken wire does enumerate.** `docs/NAMES.md:1052-1053` — w1231, `Is Broken? True`, returned two owner rows (`SelectorTunnel #5680` + `LoopTunnel #2497`), confirmed at `archive/peer/2026-09-17-cfw-t2c2-broken-wire.md:46`.
- **The `Terms[]` property's own error column was CLEAN on every zero‑row read.** `opwiresource_v5_labels.json:4` maps `errT → "error out 3"`, and `build_opconnectfromwire_v0.py:439-440` includes it in `err_keys`; it never appears in any error string, while the six *downstream* columns all read 1055. That is "the array was read successfully and index 0 is past its end", not "the read failed".
- **The signature is identical to a known ceiling.** Healthy control w23804 at i=2 gives exactly `errO/errU/errG/errS/errWU/errCO = 1055`, errT clean (`m3a4_live_endpoints.json:496-505`) — the same shape as every husk's i=0 row.
- Every class involved in the seven predictions (`ControlReferenceConstant`, `SubVI`, `Local`, case tunnels) is enumerated by this reader elsewhere in the same two runs.

The surviving version of (i) is not "broken wires read empty" but "wires whose terminals were detached read empty" — which is trivially true and is the thing under dispute, not a reader defect.

### (ii) "a wire may be one segment/branch of a net" — **externally refuted; a cheap read remains, but it is third priority**

The complete documented Wire class ([LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class)) is 6371000–637100E plus methods 6370C00–6370C0D. `Terminals[]` **6371003** is "*References the terminals connected by this wire*", and branches are not separate objects — they are **`Joints[]` 6371005**, "*an array of all joints of the wire, which includes intersections, bends, and end points*". There is no Segments, Net or Signal property. **A net is ONE Wire object**, so there is no second object holding the other half.

- **Test:** a one‑property op for `Joints[]` **6371005**, built the way `Wire.Is Broken?` 6371004 was (`docs/NAMES.md:992`: "it never needed a new op"). Read joint counts for the 7 husks, the 4 one‑row wires, and a healthy control.
- **Readings:** husk ≥ 2 joints ⇒ a *drawn* dangling segment (RBW removes something visible on the diagram); 0 joints ⇒ a degenerate shell. Neither changes the data‑flow conclusion — which is exactly why this ranks below (iii) and the falsifier.

### (iii) "owner‑pair correspondence may be coincidental" — **the live one; the decisive test is node‑side and already built**

The terminal index was **requested** at build time (`m3a4_replacement_coverage.json` `src_term`/`sink_term`, from the M3a‑1 log) and **never read back**. Nothing in this dispatch can tell a correct landing from a swap between `#10407` t3 (`Outgoing Handle`) and t5 (`Out position`) — same two objects, wrong terminals, and every gate still passes. That is textbook rule 1a: "*Parameters must arrive by the same route*".

- **Test:** `Stage.wired_terminals(48)` and `Stage.wired_terminals(10407)` on the current bed — `tools/stagekit.py:354` → `build_d1_m3a1.node_view`, the same route that produced the `7 → 0` before/after counts. Per terminal print `Terminal.Connected Wire` **634A000** → UID **and `Terminal.Name` 634A004** (`docs/NAMES.md:371`). The brief's "terminal name is not a readable column" is true of `OpWireSource_v5` only; on the node route the name reader exists and is built.
- **Expected under the claim:** `#48` t0→23804, t1→23811, t2→23820, t3→0, t4→0, t5→23838, t6→23829; `#10407` t0→23847, t1→0, t2→23856, t3→23829, t4→0, t5→23838, t6→23963.
- **Expected under "coincidental":** any swap, any replacement sitting on a terminal whose `Name` differs from the offline table's, or any of the seven old uids (1893, 2819, 4833, 7388, 11232, 23502, 23540) still appearing on a live terminal — which would mean the husks are *not* husks and RBW is cutting a live link.

This one read subsumes (iii), F, and the "which rows still need repair" question, and it is the only read here that speaks to rule 1a directly. It was available in the module `diag_c90b` already imported, and was not used.

## 5. (E) Is there a "which net / list the segments" property, and can COM reach it?

**No net/signal/segment enumerator exists.** The full Wire surface ([LabVIEW Wiki, Wire class](https://labviewwiki.org/wiki/Wire_class)) is:

| | |
|---|---|
| **properties** | 6371000 Breakpoint? (dep.) · 6371001 Probe · 6371002 Description · **6371003 Terminals[]** · **6371004 Is Broken?** · **6371005 Joints[]** · 6371006 Wire Width · 6371007 Is Break Point Set · 6371008 Source Addressing Mode · 6371009 Data Offset · 637100A Is Hidden · 637100B Breakpoint Status · 637100C Signal State · 637100D Label · 637100E Value |
| **methods** | 6370C00/01 Attach/Remove Probe · 6370C02–04 Create Constant/Control/Indicator (*not implemented*) · 6370C05 Clean Up Wire · 6370C06 Insert Node · 6370C07 Copy Probes · **6370C08 Remove Loose Ends** · 6370C09 Insert Node By Ref (*not impl.*) · **6370C0A Get Error List** · 6370C0B Delete Joint · 6370C0C Attach Sampling Probe · **6370C0D Disconnect Terminal** |

Nearest things to what you asked for: **`Joints[]` 6371005** (geometry, incl. branch intersections) and **`Get Error List` 6370C0A** — the latter already recorded in `docs/NAMES.md:1051` as private, output `Error List`, and **unbuilt**. Note `Remove Loose Ends` 6370C08 exists as a Wire method: "loose end" is a first‑class LabVIEW state, which is corroborating evidence for the husk model.

Reachability is not in doubt: these are property/method nodes built by short name inside LabVIEW and driven over COM, the identical route `Wire.Is Broken?` took. `docs/NAMES.md:425-427` explicitly records that the narrow exported `VirtualInstrument` ActiveX surface "was **the wrong surface, not proof of absence**".

Given the project's own "when a diagnosis is GUESSED twice, build the reader" rule, **`Get Error List` 6370C0A is the reader this cycle has been circling**: it answers *why each of these 11 is bad* from the machine, instead of from a move story reconstructed three stages later.

## 6. (F) Are the four NOT‑COVERED rows evidence against the claim?

**Mostly an artefact of the matching key — with one anomaly that is not, and must be read before this is closed.**

The coverage script held the tunnel *index* and matched on the *owner uid* instead; a tunnel object's uid can never equal the structure uid that owns it, so those four could only ever come out "NOT COVERED". The indices reproduce the offline table exactly:

| husk | offline row (`c53_row_class.log`) | replacement | log indices |
|---|---|---|---|
| 11232 | #48 t6 `Outgoing Handle` → #10407 t3 `Outgoing Handle` (:102, :92) | 23829 | src 6 / sink 3 ✔ |
| 7388 | #48 t5 `Out position` → #10407 t5 `Out position` (:101, :94) | 23838 | src 5 / sink 5 ✔ |
| 23502 | #23499 t0 → #10407 t0 | 23847 | src 0 / sink 0 ✔ |
| 23540 | #23523 t0 `index` → #10407 t2 `index` | 23856 | src 0 / sink 2 ✔ |

**The anomaly:** w23847's measured sink reads class **`Tunnel` #10429**, while the other three read **`SelectorTunnel`** (#10978, #11348, #11220). Every case‑structure tunnel this project has logged reads `SelectorTunnel` — `docs/cycle27-plan.md:365`, `:2841`, `:2961`; `docs/stage2-assembly-step-e.md:144`; and `archive/peer/2026-09-15-case-frame-reader-property-ids.md:77` states flatly "the measured tunnels are `SelectorTunnel`". A bare `Tunnel` in that slot is the odd one out, on the one row whose original wire (10799) was a cross‑loop row replaced by a Local. `Tunnel` is also the *parent* class ([LabVIEW Wiki, Tunnel class](https://labviewwiki.org/wiki/Tunnel_class): children `ConditionalTunnel`, `LeftShiftRegister`, `LoopTunnel`, `RegionTunnel`, `RightShiftRegister`), so the read is consistent with a tunnel belonging to some *other* structure.

**Cheapest read that settles it:** `Generic.Owner` **6327806** → cast(GObject) → `UID` on 10429, 10978, 11220, 11348 — the same owner chain `OpWireSource_v5` already runs per terminal (`docs/NAMES.md:942-945`, `:1125-1126`). Expect `10407` for all four. If #10429's owner is not #10407, w23847 landed on a different structure's tunnel and w23502's row is genuinely uncovered.

---

## Verdict

I do **not** believe the claim as written.

- ✅ "The seven hold zero terminal rows" — **measured, and the reader is sound for it.** Counter‑reading (i) is refuted by the record, not by argument.
- ❌ "…**because** they are empty husks of rows M3a‑1 already re‑wired" — the causal clause is wrong. Emptiness is explained 11/11 by *both endpoints having been on moved nodes* and is independent of whether a replacement exists.
- ❌ "…therefore deleting those seven drops no data path and is not a rule‑1a change" — **not established.** It requires each husk to have had exactly the two endpoints the offline table names (unreadable from an empty wire; the census is known to omit 156 wired terminals and is stale at three of #10407's rows) and each replacement to have landed on the same *terminal* (requested at build time, never read back).
- ⚠️ "M3a‑4's repair is only the FOUR" — plausibly the right set, derived from the wrong variable.

**What would change my mind**, in cost order: (1) the pre‑M3a‑1 artefact read showing exactly two terminals on each of the seven husk‑nets; (2) the node‑side census of `#48`/`#10407` on the current bed matching c53's names and wires terminal‑for‑terminal; (3) `Generic.Owner` on 10429/10978/11220/11348 all returning 10407. With those three, the claim's conclusion stands on measurement instead of on a story about which wires happen to be empty.

**Sources:** [Wire class — LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class) · [Tunnel class — LabVIEW Wiki](https://labviewwiki.org/wiki/Tunnel_class) · [GObject class — LabVIEW Wiki](https://labviewwiki.org/wiki/GObject_class) · [Category:VI Scripting Property — LabVIEW Wiki](https://labviewwiki.org/wiki/Category:VI_Scripting_Property) · [Scripting property/method concepts](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/scripting_property_method.html) · [NI: VI Scripting — case structure tunnels](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Nested-Case-Structure/td-p/3712057)

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL** by the cycle-68 judgement session, 2026-09-23. Four decisions, and nothing beyond them.

**1. The causal clause is WITHDRAWN.** "The seven are empty husks *because* M3a-1 already re-wired those
rows" is wrong, and the review's own explanation replaces it: emptiness is explained **11/11 by BOTH
endpoints sitting on moved objects**. The four wires that still return one row each keep that end on a
**NON-moved border object** — `#4344`, `#4274`, `#9641`, `#4334` — while the seven zero-row wires had both
ends on moved nodes. "Already re-wired" was never the variable. Dispatch 3's own correspondence count —
**3 of the 7 have a replacement, and 0 of the 4 do** — is consistent with the review's account and
inconsistent with the clause now withdrawn.

**2. "Deleting the seven drops no data path" is NOT established, so NONE OF THE 11 IS DELETED.** The claim
required each husk to have had exactly the two endpoints the offline table names (unreadable from an empty
wire) and each replacement to have landed on the same *terminal* (requested at build time, never read
back). Neither is in evidence. **CLAUDE.md rule 1a stands: all 11 are RE-WIRED, not deleted.**

**3. The offline cross-file table `tools/bench/m3a1_severed_rows.json` is RETIRED as an input to M3a-4.**
It is kept only as the prediction that was tested. Its stale and omitted terminal rows — the census is
known to omit 156 wired terminals and is stale at three of `#10407`'s rows — are the reason.

**4. Its three cheapest tests were RUN IN THE SAME CYCLE**, as dispatch 4's TASK 1 / TASK 2 / TASK 3, in
the review's own cost order: (1) the pre-sever read of the 11 wires read whole on the CLEAN artefact;
(2) the node-side terminal census of `#48` / `#10407` on both artefacts; (3) `Generic.Owner` on
10429 / 10978 / 11220 / 11348. Evidence: **`tools/bench/diag_c90c_rowtable.log`** (diagnostic
`tools/bench/diag_c90c_rowtable.py` + `tools/bench/c90c_rows.py`, 120 lines each, on `tools/stagekit.py`)
and the authoritative per-row artefact **`tools/bench/m3a4_row_table.json`**, in which every cell carries
its own `log:line` and any cell the machine did not yield is marked `unread` with its raw error.
