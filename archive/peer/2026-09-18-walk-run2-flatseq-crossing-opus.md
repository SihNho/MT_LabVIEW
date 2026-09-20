# walk-run2-flatseq-crossing-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.7678  in 18 / out 32390 / cache-create 151462 / cache-read 772515  (441s, 15 turn(s))
- **date:** 2026-09-18 02:03:58
- **outcome:** ANSWERED (445s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS CLAIM. It is the conclusion a measurement run produced, and it will shape how a motor-safety
wiring check ("check A") is built, so a wrong reading here is expensive.

THE RUN. `tools/bench/probe_flatseq_walk.py`, log `tools/bench/probe_flatseq_walk_run2.log`, 9 of 9 gates pass,
read-only, nothing saved, both originals' md5 unchanged. LabVIEW 2026 VI Scripting over COM.

WHAT IT MEASURED (all first-hand, all in that log)
  A. `report_all(V6_working_copy, "FlatSequenceInnerTunnel")` returns **518 objects** (log:39). So Traverse for
     GObjects DOES enumerate that class.
  B. On a scratch VI, a Property Node whose class string is `VI Server:FlatSequenceInnerTunnel` accepts
     1C3A9000 -> data terminal short name `LeftTerm`, 1C3A9001 -> `RightTerm`, 1C3A9002 -> `LeftFrame`,
     1C3A9003 -> `RightFrame` (log:49-52). 1C3A9004, 1C3A9005, and the Tunnel-class ids 6356000 / 6356001 are
     each REFUSED with error 1077 from `Create Property Node.vi` (log:53-56).
  C. All 14 known FlatSequenceInnerTunnel uids resolve through `UID to GObject Reference.vi`: self-echo class
     `FlatSequenceInnerTunnel`, owner `FlatSequence` uid 681, cast class `FlatSequence`, NO error (log:60-73).
  D. A backward wire walk from block diagram 10, Nodes[1] (uid 44036 = the ASI `Move Axis to Position.vi`
     startup call site), reading `Wire.Terminals[]` + `Terminal.Is Source?`:
       - terminal 8 `Position [internal units]`, wire 44089: ONE hop, Terms[0] is the source, err '',
         reciprocal wire 44089, owner = **`FlatSequenceOuterTunnel` uid 43605** (log:79-83).
       - terminal 9 `Axis`, wire 44104: one hop to `EnumConstant` uid 43955 (log:86-90).
       - terminal 10 `VISA in`, wire 44107: TWO hops - `SubVI` uid 43997 (`Initialize.vi`), then wire 44110 to
         `VISAResourceNameConstant` uid 43937 (log:93-102).
     In every case the walk stopped with the message "owner uid N of class C is NOT a node on any of the 170
     cached diagrams - the walk cannot address it as Diagram[d].Nodes[n]".

THE CLAIM UNDER ATTACK (three parts - attack whichever is weakest)
  1. "The backward walk CAN cross a flat-sequence frame boundary. LabVIEW returned the boundary object cleanly
     (`FlatSequenceOuterTunnel` uid 43605, no error); the only thing that stopped the walk is OUR OWN
     addressing scheme, which indexes objects as Diagram[d].Nodes[n] and therefore cannot name an object that
     is not in a diagram's Nodes[] array. Switching the walk to UID-addressed references removes the stop."
  2. "Because the four class-specific property ids attach to the class and all 14 instances resolve by UID, a
     one-op reader (UID -> To More Specific Class(FlatSequenceInnerTunnel) -> LeftTerm/RightTerm) would let the
     walk continue THROUGH a flat-sequence tunnel to the wire on the other side."
  3. "For a motor-safety check that must trace every value arriving at a motion call site back to its origin,
     the flat sequence is therefore not a hard barrier - it is a missing reader."

WHAT IS ALREADY RULED OUT (do not re-raise without a new reason)
  - Not a path or load problem: an open control `count(V6,'Diagram')` returned 170 in the same run (log:37),
    and the V6 copy's md5 was verified equal to the one the cached census was taken from (log:28).
  - Not an instrumentation default: the previous run's ambiguous "NO terminals at all" line was fixed - every
    `Wire.Terminals[]` iteration now prints its own error clusters, and the hops above printed err='' stage={}.
  - Not a stale uid: the seed wires come from a cached census of the same file, md5 verified equal.

WHAT I WANT FROM YOU
  1. The single strongest reason claim 1 is WRONG - in particular, whether `FlatSequenceOuterTunnel` uid 43605
     being the SOURCE of wire 44089 is even the right reading, and whether an OUTER tunnel of a flat sequence
     can be followed to the value that feeds it from the enclosing diagram at all.
  2. An alternative explanation for what was observed, and specifically: is there a documented relationship
     between `FlatSequenceOuterTunnel` and `FlatSequenceInnerTunnel` (ids, properties, short names) that the
     walk would need, given that B measured only the INNER tunnel class? Name the property ids if they exist.
  3. Name what would FALSIFY claim 2 - i.e. an observation showing that reading `LeftTerm`/`RightTerm` on a
     real instance does NOT yield a usable Terminal reference, even though the ids attach to the class.
  4. The CHEAPEST discriminating test, given that building a new scripting op costs a whole cycle here.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, so the review is delivered here as text (which is what `peer.ps1` archives anyway). Nothing was built, run, opened or edited; no LabVIEW lock taken.

---

# Failed-prediction review — "the flat sequence is not a barrier, it is a missing reader"

**Verdict: claim 1 survives only in its narrow form. Claims 2 and 3 do not — the run characterised the wrong class.**

## 1. The single strongest reason the claim is wrong

**The object that blocked the walk is not the class that was measured, and the two are siblings that share nothing.**

The ASI walk stopped on **`FlatSequenceOuterTunnel` uid 43605** (`probe_flatseq_walk_run2.log:79,83`). Measurements B and C are entirely about **`FlatSequenceInnerTunnel`**. Per the vendor-community property tables:

| class | inheritance (verbatim) | its complete property set |
|---|---|---|
| `FlatSequenceInnerTunnel` | `Generic → GObject → FlatSequenceInnerTunnel` | 1C3A9000 Left Terminal · 1C3A9001 Right Terminal · 1C3A9002 Left Frame · 1C3A9003 Right Frame |
| `FlatSequenceOuterTunnel` | `Generic > GObject > FlatSequenceOuterTunnel` | **3195B800 Outer Terminal · 3195B801 Inner Terminal · 3195B802 Frame** |

Neither derives from `Tunnel` — which is exactly why 6356000/6356001 were refused (`:55-56`). That measurement was correct; it was taken on the class that was not in the way. The two classes share no property id, no short name, and not even an id block (`1C3A9xxx` vs `3195Bxxx`).

So **claim 2's reader — `UID → To More Specific Class(FlatSequenceInnerTunnel) → LeftTerm/RightTerm` — applied to uid 43605 fails at the cast.** Claim 3 then generalises from a reader that does not apply to the case claim 1 observed.

Worth naming because it is the expensive part: **`3195B801` has been in this project's own files with its wiki URL since 2026-09-14.** `archive/peer/2026-09-14-optunnels-v0-plan.md:45` says verbatim *"do not use the unrelated `FlatSequenceOuterTunnel.Inner Terminal`, ID `3195B801`"*. I found that by content grep, not by browsing `archive/`, and I verified it against the live wiki rather than trusting the archived peer answer.

### Brief Q1 — is "43605 is the SOURCE of wire 44089" the right reading?

The reading is true but **directionally undetermined**, which is the part that matters. `FlatSequenceOuterTunnel` has two faces. The run never read `Outer Terminal`, never read `Inner Terminal`, never read `Frame`, and never read the source terminal's own UID or its `Terminal.Diagram` (634A002 — already in use by `OpTunnelRead_v0`, `docs/toolkit-capabilities.md:71`).

- Source = **inner** face ⇒ node 44036 is inside a frame; the continuation is `Outer Terminal` 3195B800 out to the enclosing diagram. (So the answer to your second half is yes — an outer tunnel *can* be followed to what feeds it from outside.)
- Source = **outer** face ⇒ 43605 is an OUTPUT tunnel, 44036 sits *outside* the sequence downstream of it, and the continuation is `Inner Terminal` 3195B801 *into* the frame. The origin is inside, not outside.

A reader that hardcodes one side is right half the time and **silently returns a wrong origin** the other half. For a motor-safety trace that is worse than stopping. Also note `Frame` is **singular** — one outer tunnel belongs to one frame — unlike `Tunnel.Inside Terminals[]`, so `OpTunnelRead_v0`'s frame-disambiguation pattern does not transfer.

## 2. Alternative explanation — nothing flat-sequence-specific was observed

The STOP message is not evidence about flat sequences at all. The **identical** message fires at `:90` for `EnumConstant` uid 43955 and at `:102` for `VISAResourceNameConstant` uid 43937 — objects that unambiguously *are* nodes on a diagram. The predicate is `idx.get(ou) is None` (`tools/bench/probe_flatseq_walk.py:444-448`) against `main_vi_nodeterms.json`, a cache of **626 nodes over 170 diagrams** (`:76`) for a VI containing 518 `FlatSequenceInnerTunnel` objects alone (`:39`).

The message therefore means *"not in our JSON"*, not *"not a node"* — and **it cannot distinguish a flat-sequence boundary from an ordinary constant.** Under this alternative the run observed one short cache and three objects that fell out of it; the tunnel happened to be one. A FlatSequence reader would not have changed the other two stops, which undercuts claim 3's "it is a missing reader" directly.

Secondary: reaching the boundary object is not crossing it. Every property read that would *constitute* a crossing has zero measurements behind it.

## 3. What would falsify claim 2 (brief Q3)

Error 1077 means *"you use a property ID that is not in the AllProps list"* — a **class-registry lookup at build time**. It says nothing about a read on a live instance. Your own log proves the gap exists: `:81` shows a Property Node inside `OpWireSource_v5.vi` that built fine and returned **error 1055** at run time.

Claim 2 is falsified by any one of:

- **(a)** `To More Specific Class` GObject → `FlatSequenceInnerTunnel` raises **1057** on a live uid. *This has never been attempted.* `OpOwnerChain_v1`'s `cast_class` returned `'FlatSequence'` for all 14 rows (`:60-73`) — that is a cast of the **owner**, not of the tunnel (`probe_flatseq_walk.py:291-303`). The cast claim 2 rests on has executed zero times.
- **(b)** The read yields a Terminal reference whose `Terminal.Connected Wire` (634A000) is empty or errors 1055 — property read succeeds, walk still cannot continue.
- **(c)** The far face's `Connected Wire` returns **the same wire uid** you arrived on; the hop does not advance. One "the hop does not advance" row is already on record (`docs/d1-build-plan.md:738`).
- **(d)** The far terminal's source is another inner tunnel with no termination rule — raised as A3-ii and still unanswered (`docs/d1-build-plan.md:813-820`).

Every one of these leaves 1C3A9000/1C3A9001 "attaching to the class" exactly as measured while claim 2 is false.

**Precedent that should worry check A specifically:** `OpOwnerChain_v1` is *measured* to **terminate silently at a `FlatSequenceFrame`** (`docs/toolkit-capabilities.md:49`, quoted at `docs/d1-build-plan.md:834`), a class present in the main VI. In a motor-safety trace a silent termination reads as "no other source".

## 4. Cheapest discriminating test — no new op, no build, one recipe

Both mechanisms already exist in the run that just passed 9/9. Two parameter changes:

**T1 — class table (~80 s, 0 builds).** Rerun `m1()` unchanged with `FSIT_CLASS = "VI Server:FlatSequenceOuterTunnel"` and `M1_IDS = [632A813 ctrl, 6327803 ctrl, 3195B800, 3195B801, 3195B802, 3195B803, 1C3A9000]`.
*Prediction contract:* 3195B800/801/802 ATTACH and print their data-terminal short names (`docs/NAMES.md` needs these — gscript wires by short name); 3195B803 and 1C3A9000 REFUSE with 1077. If 1C3A9000 attaches, my sibling model is wrong and claim 2 partly survives. Scratch VI in `claudeDev`, deleted after — identical safety profile to the run that already passed.

**T2 — the half that actually decides (same recipe).** The walk already holds the source Terminal reference for wire 44089. Read `GObject.UID` 632A813 on it; then on uid 43605 read 3195B800 and 3195B801 and take each one's UID. Whichever matches names the face you are standing on; the other is the continuation. That one comparison settles direction, the live cast and the live read together — and it separates the claim from §2, because a failed cast or read makes "missing reader" wrong for a different reason than claim 3 gives.

**Free negative control for §2:** make the STOP predicate distinguish *in the VI but absent from the cache* from *genuinely not a node*. The `EnumConstant` at `:90` is the oracle — it must come back "in the VI, not in the cache."

## Where I could be wrong

Claim 1's narrow form — LabVIEW returned the boundary object without error, and `Diagram[d].Nodes[n]` addressing is what stopped the walk — I am not disputing. What would change my mind on the rest: T1 showing 1C3A9000/1C3A9001 attaching to `VI Server:FlatSequenceOuterTunnel`, **plus** T2 showing a live read on 43605 returning a Terminal whose `Connected Wire` is a different wire on a different diagram.

As it stands the evidence does not distinguish "a flat-sequence boundary is crossable" from "one cached JSON is short" — and it contains no measurement at all of the class that did the blocking.

**Sources:** [FlatSequenceOuterTunnel class](https://labviewwiki.org/wiki/FlatSequenceOuterTunnel_class) · [FlatSequenceInnerTunnel class](https://labviewwiki.org/wiki/FlatSequenceInnerTunnel_class) · [Outer Terminal property](https://labviewwiki.org/wiki/FlatSequenceOuterTunnel_class/Outer_Terminal_property) · [NI: error 1077 = ID not in AllProps](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Can-t-get-or-set-all-available-properties/td-p/4030544) · [VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)

## Sources

(extract from answer)

## What was done with it

**ACCEPTED. Its central objection was correct — the run had measured the WRONG CLASS — and both prescribed
tests were run the same session** (material, cycle 19, 2026-09-18). Neither needed a build.

**T1 — `tools/bench/probe_flatseq_outer.log`, 5/5 gates, 46 s.** The review's prediction contract was met
exactly, and the short names `docs/NAMES.md` needs are now MEASURED rather than undocumented:

| id on `VI Server:FlatSequenceOuterTunnel` | predicted | MEASURED |
|---|---|---|
| `3195B800` Outer Terminal | ATTACH | **ATTACHED, short name `OuterTerminal`** |
| `3195B801` Inner Terminal | ATTACH | **ATTACHED, `InnerTerminal`** |
| `3195B802` Frame | ATTACH | **ATTACHED, `Frame`** |
| `3195B803` | REFUSE 1077 | **error 1077** |
| `1C3A9000` (inner-tunnel `LeftTerm`) | REFUSE 1077 | **error 1077** — the two classes are distinct, exactly as the review said, so the run-2 census does NOT transfer |
| `634A002` `Terminal.Diagram` | — | error 1077 (no Terminal inheritance) |

Traverse counts on the V6 working copy: `FlatSequenceOuterTunnel` **58**, `FlatSequenceInnerTunnel` **518**,
`FlatSequence` **21**; `FlatSequenceFrame` is not a valid Traverse class name (error 1092).

**The "free negative control" — run, and it settles §2's ambiguity: `tools/bench/probe_walk_stop_control.log`,
3/3.** Diagram 10's **live** `Nodes[]` is `[(43997,'Initialize.vi'), (44036,'Move Axis to Position.vi')]`,
identical to the cache — so the cache is NOT short, and "absent from the cache" really does mean "absent from
`Nodes[]`". The `EnumConstant` oracle behaved as the review predicted it must: uid 43955 is **not** in
`Nodes[]` yet **is** Traverse-visible (14 of that class), and so are 43605 (58) and 43937 (3). So the walk's
stop is an artefact of `Diagram[d].Nodes[n]` addressing, and every object it stopped on is reachable by UID.

**NOT done, and reported to the judgement session as the one open question:** T2's live read of `3195B800` /
`3195B801` on uid 43605. That needs a UID → `To More Specific Class(FlatSequenceOuterTunnel)` → property
reader, i.e. a new op — a build, which this measurement-only cycle was told not to make. So claim 1's narrow
form stands **measured**; claim 2 ("a one-op reader would let the walk continue through") remains
**unverified**, and the review is right that the ids attaching to a class is not the same as a live read
returning a usable Terminal.

Also recorded: the review's finding that `3195B801` has been in this project's files since 2026-09-14
(`archive/peer/2026-09-14-optunnels-v0-plan.md:45`) — a prior-art fact, not disposed of here.

(Claude fills in)
