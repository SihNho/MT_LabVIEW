# c60-ia-count-gate

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.5990  in 16 / out 34202 / cache-create 227460 / cache-read 808101  (447s, 14 turn(s))
- **date:** 2026-09-21 07:31:50
- **outcome:** ANSWERED (449s)
- **why asked:** `guard_peer` owed a hypothesis review for the ONE failing gate of cycle 60 attempt 2's run 1 (`tools/bench/diag_s3b_l0_localname.log`, `BGRUN END rc=1 after 112s`, 17 pass / 1 fail): `R0_a3 exactly ONE IndexArray ... 3 IndexArray(s); element None`. The claim put up for attack was that this is a defect in the GATE (copied from a donor with one Index Array), that the right one is named unambiguously by the wiring the same run measured, and that widening the selector is "the whole repair".
- **verdict:** unverified

## Question

ATTACK the claim below. It is the explanation formed under pressure for the ONE failing gate in
`tools/bench/diag_s3b_l0_localname.log` (run 1, `BGRUN END rc=1 after 112s`, 17 pass / 1 fail). Your job is
to find the strongest reason it is WRONG, to name an alternative explanation, to say what would falsify it,
and to name the CHEAPEST discriminating test. Do not confirm it.

Files you may read (read-only): `tools/bench/diag_s3b_l0_localname.log`, `tools/bench/diag_s3b_l0_localname.py`
(the diagnostic itself; the function at issue is `_r0_body()`), `tools/bench/diag_s3b_l0_localname.json`,
`tools/recipes/build_opnodelabels_v0.py` (the donor's own builder), `tools/gscript.py`
(`node_labels` :587, `report` :455, `build_property` :2194, `wire` :1340, `connect_terminals` :2410,
`loop_cast` :626), `docs/cycle27-plan.md` Pre-decided 49.

== THE FAILING GATE, VERBATIM FROM THE LOG
  FAIL  R0_a3 exactly ONE IndexArray on the copy's diagram, carrying a terminal named `element`  3 IndexArray(s); element None

== THE CLAIM UNDER ATTACK
"R0_a3 is a defect in the GATE, not a fact about the donor. The gate was copied from cycle 60 attempt 1,
whose donor `OpFPLabels_v0.vi` happens to carry exactly one Index Array; the donor of record here,
`OpNodeLabels_v0.vi`, carries THREE (uids 239, 236, 308), so `ia_uid` was left None, no terminal table was
read, and `element` reported None BY CONSTRUCTION - the machine was never asked anything. The same run's own
shape dump names the right one unambiguously: `Traverse for GObjects.vi` (uid 124) has a SOURCE terminal
`References` on wire 600, and Index Array uid 308 has `array` on wire 600 and `element` on wire 605, which
feeds `To More Specific Class` uid 683. Replacing the count test with 'the IndexArray whose `array` terminal
carries the Traverse node's `References` wire' is the whole repair, and the build should then proceed to the
measurement it exists for: wire that `element` into a `VI Server:Local` property node reading
`Local.Control Name` 6355400, and read ExecState."

== WHAT THE BUILD IS FOR (context, not part of the claim)
The deliverable is `claudeDev\OpLocalName_v0.vi`, a ONE-PROPERTY READER of a Local Variable's binding. No
reader of a Local's binding exists in this fleet at all. The known hazard, written into the script before the
run: `Traverse for GObjects.vi` returns GENERIC GObject references, and every class-specific property node in
the donor is fed by a TYPED source (`Node.Terminals[]` -> Terminal; `Terminal.Wire` -> Wire) or through
`To More Specific Class`, whose `target class` type comes from a wire no node on that diagram produces
(a panel object or a constant). `tools/gscript.py:2415` says "Type mismatches make a broken wire".

== ALREADY RULED OUT (do not spend your answer on these)
1. "The donor is the wrong file / was modified": `OpNodeLabels_v0.vi` md5 `376ff12569008ebac25a524e0887030b`
   before AND after the run, and the copy opened at `ExecState` 1 before any edit (gate R0_a1 PASS).
2. "Nothing was measured": the run dumped all 13 top-level nodes with full terminal tables (gate R0_a2 PASS)
   and that dump is where the wire numbers above come from.
3. "The originals were touched": gates T1/T2/T3/Z1 all PASS, four md5 pins unchanged before and after, refs
   3 opened / 3 closed / 0 live, and the unsaved copy was removed.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role, as it should be — so the review is the answer below. One correction to my opening line: the proposed selector **is** unique on this donor (IA 308 `array`=600; IA 236 `array`=884; IA 239 `array`=485 — `diag_s3b_l0_localname.log:33,36,38`), so that half of the claim survives. The refutation is elsewhere.

---

# 1. The strongest reason the claim is wrong

**"R0_a3 is a defect in the GATE, not a fact about the donor" is false on this project's own record — and the claim's own cited evidence is the proof against it.**

The claim cites, as corroboration, that `element` (wire 605) "feeds `To More Specific Class` uid 683". That is precisely the fact that kills the next step it proposes. The donor's builder states the shape in one line:

> `tools/recipes/build_opnodelabels_v0.py:11-12` — *"DONOR: OpNetInfo_v1 (as OpSubVIs_v1): Traverse 'Diagram' by `index` -> IA -> **TMSC -> Diagram** -> PN Nodes[] -> **the vestigial per-node chain** (index 2 / index 3 stay 0)."*

Both the cast **and** the two extra Index Arrays are recorded there, in advance, in a file the diagnostic cites in its own "WHAT ALREADY EXISTED" block (`diag_s3b_l0_localname.py:39-43`). So the run's stop message — *"the donor of record is not the shape its builder recorded"* (`log:47`) — is factually wrong. The donor is exactly the shape its builder recorded. What dropped the `TMSC` step is the diagnostic's own one-line donor summary at `diag_s3b_l0_localname.py:40-43` ("Traverse `Class Name` by `index` -> Index Array -> ... -> property -> string indicators"). The brief mis-described a donor whose description it had open.

And the type rule makes the proposed measurement unbuildable as stated. `element` is a **generic GObject** reference — the subVI is literally named `Traverse for GObjects.vi` — and `Local` sits two classes below it: **Generic → GObject → Node → Local** ([LabVIEW Wiki, VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)). NI's own guidance and every forum answer on this say a class-specific property node requires `To More Specific Class` first ([NI: Getting object by having GObject Refnum values](https://forums.ni.com/t5/LabVIEW/Getting-object-by-having-GObject-Refnum-values/td-p/1332738), [NI: Typecasting References](https://forums.ni.com/t5/LabVIEW/Typecasting-References/td-p/3289976)). The donor demonstrates the rule four times over: **every** property node in it is fed by an already class-typed reference — PN 235 ← TMSC output 645, PN 237 ← `Nodes[]` element 464, PN 241 ← `Terms[]` element 572, PN 242 ← `Wire` output 620 (`log:34-41`). The one place a generic reference enters, the donor spends a TMSC node on it.

So "replacing the count test … is the whole repair" is wrong: it repairs the thermometer. The structural blocker — a generic reference cannot reach a `VI Server:Local` property — is untouched, and it is the hazard the script itself wrote down before the run (`diag_s3b_l0_localname.py:65-69`).

**The claim also ignores prior art the project already paid for** (CLAUDE.md's fourth review layer). `tools/gscript.py:626-635`:

> *"Cast-free seed: the op's TMSC 'target class' is fed by a ForLoop-refnum **CONTROL** created from erdosmiller Create For Loop.vi's typed output (NI: TMSC accepts any wire of the target type). … plan review `archive/peer/2026-09-14-loopcast-typed-terminal-seed-plan.md`"*

The fleet solved this exact problem twice (`OpLoopCast_v0`, `OpWhileCast_v0`). The real open question is not the gate; it is **where a Local-typed seed comes from**.

# 2. An alternative explanation of the same evidence

**The donor of record is simply the wrong donor, and R0_a3 is the first place the run touched that.**

`OpNodeLabels_v0` is a **Diagram-cast ladder** copied from `OpNetInfo_v1`: its one Traverse-fed Index Array exists only to feed a TMSC hard-cast to **Diagram**, and the other two index property outputs (`Nodes[]`, `Terms[]`), not the Traverse output. Nothing in it was ever designed to read a property off a raw Traverse element. Under this reading the count `3` is true, documented, and informative — 1 + 2 vestigial — and the gate, crude as its wording was, reported a real fact: *this donor does not support a one-property read on a Traverse-selected object*, which is the exact question `diag_s3b_l0_localname.py:62-64` instructed the run to answer.

This alternative predicts a **second** defect the claim does not consider. The wrapper drives this donor with `TRAVERSE_CLASS = "Local"` (`diag_s3b_l0_localname.py:185, 652`) through a TMSC whose target class is **Diagram**. `tools/gscript.py:634` records what the project already measured about that: *"A seed casts only its own class (test_oploopcast.log T3: the ForLoop seed on a WhileLoop ref → **error 1055** downstream)"*. So even with a perfect wire, every `local_name()` call would drive the donor's ladder into a cast error, and R1_b2's "Control Name for every pre-existing Local" would be contaminated. The claim's "proceed to the measurement it exists for" assumes a reader this donor cannot be.

**What the evidence does not settle:** nothing measured so far distinguishes (a) LabVIEW *breaking* the `element → reference` wire from (b) LabVIEW *re-adapting* the property node's class to the wired GObject reference — which would drop the `Control Name` row and leave `ExecState` at 1. Run 1 never reached the wire, so both are live.

# 3. What would falsify me / confirm the claim

A single reading: `R0_a4` resolves `VI Server:Local`, `R0_a5/a6` show a `Control Name` **source** row, `R0_a7`'s wire lands with an empty error column, and **`R0_a8` reads `ExecState` 1 with the `Control Name` row still present in `terminals_after`**. That would mean the element wire is not generic in the way I argue (or LabVIEW re-adapts benignly), the donor's TMSC is incidental to this build, and the count test really was the only blocker.

Note the trap: `ExecState 1` **alone** does not falsify me. If the node re-adapted its class, the row disappears and the reader reads a GObject property under a `Local` label — a false pass. `R0_a7` only checks that `reference` carries a non-zero wire uid (`diag_s3b_l0_localname.py:565-567`); nobody checks that the property row survived.

# 4. The cheapest discriminating test

Do not rebuild, do not substitute a donor. Run the already-patched R0, **stop after the wire**, and take three readings in this order — order is load-bearing (`docs/NAMES.md:905`, and `:912-925`: reading `Is Broken?` perturbs the target, so an `ExecState` taken *after* it is worthless):

1. **`ExecState`** immediately after the `element → reference` wire — gate `R0_a8` exactly as written.
2. **`Control Name` row still in `wr["terminals_after"]`** — already captured at `diag_s3b_l0_localname.py:556-560`, just never asserted. Free.
3. **`Wire.Is Broken?` 6371004 on that new wire's uid** (built and measured, `docs/NAMES.md:902-911`) — it names *which* wire broke, where `ExecState` only says something did.

| reading | settles |
|---|---|
| `ExecState` 0 + `Is Broken? True` on the new wire | generic→Local is illegal — my alternative; the donor question is closed without another build |
| `ExecState` 1 + `Control Name` row intact | the claim stands; I am refuted |
| `ExecState` 1 + `Control Name` row gone | the node re-adapted — a false pass either story would have swallowed |

One run, no save, no new op, no donor substitution. The provenance half of the question needs no run at all — it is already settled by putting `build_opnodelabels_v0.py:11` beside `diag_s3b_l0_localname.py:40-43`.

And if the reading goes against the claim, the constructive route is named above, not improvised: seed a TMSC with a Local-typed reference in the `loop_cast` pattern. A candidate seed is already on disk — `OpCreateLocal_v0.vi`'s Invoke exposes a `Create Local` **source** terminal (`diag_s3b_l0_localname.log:61`, i=5 `is_source True`), which is a Local-typed output. Whether it can serve as a type-only seed is itself a measurement, not an assumption.

**Sources:** [VI Server Class Hierarchy — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) · [Local class/Control Name property — LabVIEW Wiki](https://labviewwiki.org/wiki/Local_class/Control_Name_property) · [Control class/Create.Local Variable method — LabVIEW Wiki](https://labviewwiki.org/wiki/Control_class/Create.Local_Variable_method) · [NI: Getting object by having GObject Refnum values](https://forums.ni.com/t5/LabVIEW/Getting-object-by-having-GObject-Refnum-values/td-p/1332738) · [NI: Typecasting References](https://forums.ni.com/t5/LabVIEW/Typecasting-References/td-p/3289976) · [LAVA: GObject To More Specific Class from Class ID](https://lavag.org/topic/13549-gobject-to-more-specific-class-from-class-id/)

## Sources

(extract from answer)

## What was done with it

**RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), by cycle 60 attempt 2's material session, 2026-09-21.**
Nothing in it selects a route, and no route was selected. What follows says exactly what was and was not acted on.

**NOT ACTED ON — everything that would change the build.** (a) Its §2 reading that *"the donor of record is simply
the wrong donor"* is a DONOR SUBSTITUTION, and the brief forbids substituting a donor or designing a different op;
that judgement belongs to the judgement session. (b) Its §1/§4 constructive route — seed a `To More Specific Class`
with a Local-typed reference in the `loop_cast` pattern, candidate seed `OpCreateLocal_v0.vi`'s Invoke terminal
i=5 `Create Local` (SOURCE) — is a DESIGN, and was NOT built, NOT prototyped and NOT probed. (c) Its §4 third
reading, `Wire.Is Broken?` 6371004 on the new wire, was NOT implemented: on this fleet that reader only answers
when it is ORDERED after a `Terminal.Connect Wire` (`docs/NAMES.md:902-911`), i.e. it means new construction
inside the op, which is exactly the kind of improvisation the brief rules out. (d) Its correction that the
diagnostic's own donor summary (`diag_s3b_l0_localname.py:40-43`) drops the `TMSC` step that
`build_opnodelabels_v0.py:11-12` records is ACCURATE and is RECORDED here; the script's stop message
*"the donor of record is not the shape its builder recorded"* is withdrawn as a sentence and no document was
edited on the strength of it.

**ACTED ON — one thing, and it is a READING the run already captured and simply never asserted.** §4 reading 2:
the `Control Name` row must still be present in `wr["terminals_after"]` after the `element -> reference` wire.
The diagnostic already re-reads the property node's full terminal table immediately after the wire
(`diag_s3b_l0_localname.py`, the `R0_a7` block); the only change is that a gate now asserts the row survived, so
the three-way table the review draws — `ExecState 0` / `ExecState 1` with the row intact / `ExecState 1` with the
row GONE (a silent class re-adaptation, i.e. a false pass either story would have swallowed) — is distinguishable
from the log. No new call, no new op, no new verb, no route.

**ALSO RECORDED:** the review's own opening correction, that the selector this run adopted IS unique on this donor
(IA 308 `array`=600 · IA 236 `array`=884 · IA 239 `array`=485, `tools/bench/diag_s3b_l0_localname.log:33,36,38`),
so the gate repair itself is not in dispute; the review's attack is aimed at what comes AFTER the gate.
