---
type: reference
status: current
date: 2026-09-17
tags: [motor, census, safety, limits]
---

# Motion call-site census — measured by REACHABILITY TO A SERIAL WRITE

Step 1 of `docs/motor-limit-assurance-plan.md` §D's build order. Tool `tools/motor_census.py` (a READER —
no VI run, nothing saved, no serial port opened). **Run 3 is the valid one**:
`tools/bench/motor_census_run3.log`, `BGRUN END rc=0 after 169s`, **7/7 gates** (P1 PI · P2 ASI · P3 md5 ·
P5 every site has a kind · P6 undecided 0 · P7 motion total still 41 · P8 per-callee counts unchanged).
Output `tools/bench/motor_census_3state-ORIGINAL.json`, `…_v6-workingcopy.json`, `…_all.json`.
Run 2 (`motor_census_run2.log`, 3/3) produced the same reachability result and is superseded only in its
BUCKET LABELS; run 1 is superseded outright (see the two dead routes at the end).

**Rule 1 evidence:** `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` md5
`c39f36e0675339673b707c59f0784fee` and `Min_Track N beads V6_ParallelLoop.vi` md5
`2a78e17c449cacdaf5da389818526859`, identical before and after every run. No LabVIEW process existed
before the work and none after it.

## How a call site is classified

| | |
|---|---|
| PRIMARY | the called subVI's own hierarchy contains a **serial WRITE node**. Measured. |
| CROSS-CHECK | the name list `MOV/VEL/GOH/Move Axis to Position/Move Axis Relative/SetCommand(_signed)` |
| `both` | reachable **and** on the name list |
| `reachability` | reachable, **not** on the name list → reported as **UNCLASSIFIED**, never dropped |
| `name` | on the name list, no serial write found anywhere → **NAME_ONLY** (run 2: zero) |
| `unknown` | the reachability test could not complete (error 1040) → emitted as **`ASSUMED_MOTION`, in scope** (decision 2) — **never read as "no"** |

## THE TWO CYCLE-1 DECISIONS — read these, do not re-derive them

Decided by the **cycle-1 judgement session, 2026-09-17**, on the two questions the previous material session
returned. Check A's builder (and the `motor-limit-checker` agent) reads them HERE.

**DECISION 1 — the partition is not query-vs-command, it is “CAN THIS CALL CHANGE MOTOR STATE?”.** The flat
`motion` flag is replaced by a `kind` on every call site:

| kind | means | in scope for A/B/C + the approved fixed clamp (plan `## Pre-decided` 2) |
|---|---|---|
| `COMMAND` | can change position / velocity / motor state: `MOV.vi`, `VEL.vi`, `GOH.vi`, ASI `Move Axis to Position.vi`, ASI `Move Axis Relative.vi`, `SetCommand.vi` / `SetCommand_signed.vi`, **and the three lab VIs the reachability test caught** — `Motor control v5_No Recording.vi`, `ASI_adjust focus-subvi.vi`, `check N bead pos v3-kimlab.vi` | **YES** |
| `QUERY` | transmits but cannot change motor state: `POS?`, `TMN?`, `TMX?`, ASI `Get Current Position` | **NO** — kept in the census because it is serial traffic and CLAUDE.md rule 1c cares where serial sits |
| `CONFIGURE` | Autonics `Configure.vi`, ASI `Initialize.vi`, `Mercury_GCS_Configuration_Setup.vi` | **YES, default-deny** — a configure call can home an axis or set a soft limit. Whether it actually does is NOT measured; only a recorded measurement may demote it |

**Callee on none of the lists ⇒ `COMMAND` (in scope). A site is never defaulted OUT of scope.**

**DECISION 2 — `UNKNOWN` is abolished.** A call site whose callee's hierarchy cannot be traversed (the
error-1040 vi.lib VIs) is emitted as **`ASSUMED_MOTION`, counted IN SCOPE**, with the reason recorded (which
VI, which error) in `assumed_reason`. Same default-deny principle as `tools/motor_gate.py`. A site leaves
`ASSUMED_MOTION` only by a **recorded measurement**, never by assumption. §D.4 says “a checker that misses one
is not used”, so the plan does not accept “inconclusive” — and with this rule the census states mechanically
that **zero sites are undecided**. (`ASI Initialize.vi` d10/d88 and `Mercury_GCS_Configuration_Setup.vi` d91
are on the `CONFIGURE` name list as well; untraversability wins the label, and both labels are in scope, so
nothing turns on the order.)

## The count table — original, run 3

| kind | n (3StateClamping ORIGINAL) | n (V6 working copy) | in scope |
|---|---:|---:|---|
| `COMMAND` | **31** | 31 | ✅ |
| `QUERY` | 9 | 9 | ❌ |
| `CONFIGURE` | 1 | 1 | ✅ |
| `ASSUMED_MOTION` | 11 | 11 | ✅ |
| `NONE` (measured: reaches no serial write) | 45 | 46 | ❌ |
| **IN-SCOPE TOTAL** | **43** | **43** | |
| **undecided** | **0** | **0** | |

(`motor_census_run3.log:97-104` and `:233-240`. The V6 copy's one extra `NONE` is the inserted
`IMAQ Write TIFF File 2`.) COMMAND 31 = SetCommand 9 + MOV 7 + VEL 4 + ASI Move Axis to Position 4 + GOH 2 +
`ASI_adjust focus-subvi` 2 + ASI Move Axis Relative 1 + `Motor control v5_No Recording` 1 +
`check N bead pos v3-kimlab` 1.

## How a serial write is recognised

A VISA Write is identified **by its node LABEL**. Its VI Scripting class is the generic `Function`
(`tools/bench/visa_class_probe.log:14`), and an offline byte/zlib scan of a `.vi` finds no "VISA Write"
string even in `SetCommand.vi`, which holds five — so neither class-Traverse nor a byte scan works.

## The original — 170 diagrams, 97 call sites, 41 MOTION, 41/41 decided, NAME_ONLY 0, undecided 0

The 41 motion sites and every per-callee count are **unchanged from run 2** — decisions 1 and 2 only add the
`kind` column (gates P7/P8).

| n | callee | device | rule | **kind** | diagrams |
|---:|---|---|---|---|---|
| 9 | `SetCommand.vi` | rotor | both | **COMMAND** | 24, 28, 32, 32, 103, 107, 111, 111, 115 |
| 7 | `MOV.vi` | PI | both | **COMMAND** | 3, 36, 40, 69, 121, 125, 129 |
| 5 | `ASI …Get Current Position.vi` | ASI | reachability | QUERY | 12, 73, 90, 146, 148 |
| 4 | `VEL.vi` | PI | both | **COMMAND** | 5, 69, 91, 129 |
| 4 | `ASI …Move Axis to Position.vi` | ASI | both | **COMMAND** | 10, 88, 151, 167 |
| 2 | `GOH.vi` | PI | both | **COMMAND** | 4, 91 |
| 2 | `POS?.vi` | PI | reachability | QUERY | 5, 117 |
| 2 | `ASI_adjust focus-subvi.vi` | (lab VI) | reachability | **COMMAND** | **43 (= the FRAME LOOP)**, 99 |
| 1 | `ASI …Move Axis Relative.vi` | ASI | both | **COMMAND** | 73 |
| 1 | `TMN?.vi` | PI | reachability | QUERY | 91 |
| 1 | `TMX?.vi` | PI | reachability | QUERY | 91 |
| 1 | `Configure.vi` (Autonics) | rotor | reachability | **CONFIGURE** | 92 |
| 1 | `Motor control v5_No Recording.vi` | (lab VI) | reachability | **COMMAND** | 20 |
| 1 | `check N bead pos v3-kimlab.vi` | (lab VI) | reachability | **COMMAND** | 16 |

Owning structure per site is in the JSON (`owner_structure`, `structure_uid`) and printed in the log —
e.g. d3 CaseStructure uid 30804 `MOV.vi`, d10 FlatSequenceFrame uid 44036 ASI `Move Axis to Position.vi`.

**The V6 working copy is the same census**: 98 call sites (the one extra is the inserted
`IMAQ Write TIFF File 2`, memory `tiff_writer_is_a_fixture_insertion_not_original`), same 41 motion sites,
same 14 UNCLASSIFIED, same uids.

### Against the plan's provisional counts
`MOV.vi ×7` and `VEL.vi ×4` are **exact**; the plan's "`GOH`, ASI `Move Axis to Position.vi`, rotor
`SetCommand*`" resolve to 2 / 4 / 9, plus one `Move Axis Relative.vi` the plan did not name. The counts in
`docs/instrument-libraries.md:167-169` (MOV ×12, VEL ×9, GOH ×7) count FILES ON DISK, not call sites.

## Only FOUR VIs in the whole hierarchy hold a serial write

`ASI TG-1000 …\Send Serial Command.vi` (1) · Autonics `Configure.vi` (1) · Autonics `SetCommand.vi` (5) ·
`PI Send String.vi` (3). Everything else is motion **only** by reaching one of these. This agrees with
`docs/motion-path-audit.md:58-74` and is the fact check A's backward trace should rest on.

## The 14 UNCLASSIFIED — this is the hole §D.4 exists to close

Reachable, not on any name list. Three of them are **lab VIs**, i.e. the wrappers a name-based checker
would have missed entirely: `Motor control v5_No Recording.vi` (d20), `ASI_adjust focus-subvi.vi`
(d43 — inside the frame loop — and d99), `check N bead pos v3-kimlab.vi` (d16). The rest are the PI and
ASI query VIs (`POS?`, `TMN?`, `TMX?`, ASI `Get Current Position`) and Autonics `Configure.vi`: a *query*
still transmits, so reachability marks it. **That judgement is now made** — decision 1 splits these 14 into
3 lab VIs `COMMAND` + Autonics `Configure.vi` `CONFIGURE` (**all four IN scope**) and 9 PI/ASI queries
`QUERY` (**out of scope for A/B/C**, kept on record as serial traffic under rule 1c).

## The 11 ASSUMED_MOTION — decision 2: untraversable, so IN SCOPE (never "no")

`ASI …Initialize.vi` (d10, d88), `Mercury_GCS_Configuration_Setup.vi` (d91), `Simple Error Handler.vi` ×3
(d1, d83 ×2), `Set Cursor (Icon Pict).vi` ×4 (d15, d17, d97, d145), `Draw Text at Point.vi` (d137). Cause:
their hierarchies reach vi.lib VIs whose diagram Traverse refuses with **error 1040** (`Property Node
(arg 1) in TRef Traverse.vi`) — no readable block diagram — so 23 of 130 VIs could not be decided and the
result propagates up. The per-site `assumed_reason` in the JSON names the VI that actually refused:
`Error Code Database.vi` (below both `Simple Error Handler` and ASI `Initialize`),
`Set Cursor (Icon Pict).vi` itself, `Get Text Rect.vi` (below `Draw Text at Point`) and
`Mercury_GCS_Configuration_Setup.vi` itself — `motor_census_run3.log:105-115`.

The two ASI `Initialize.vi` sites matter most: `docs/main-vi-startup.md:33` puts one of them beside the
startup move. **Demotion rule:** any of these 11 leaves `ASSUMED_MOTION` only when a measurement is recorded
(e.g. `VI.Get Errors`, a vendor source read, or a different traversal that returns a diagram) — never by a
session judging that "a cursor VI obviously cannot move a motor".

## Rule 1c FACT — the ORIGINAL already has a serial call on the FRAME ACQUISITION PATH

`ASI_adjust focus-subvi.vi` (`…\zz_LabView VI\Madcity\ASI_adjust focus-subvi.vi`, uid 48) is called on
**diagram 43 — the frame loop** (the loop this project restructures; `motor_census_run3.log:81`-class row,
`docs/main-vi-subvi-identity.md` d43). It is `kind = COMMAND` (it reaches a serial WRITE and it is an ASI
focus adjuster, i.e. it can move the piezo), so **the original VI issues VISA traffic from inside the frame
acquisition loop** — exactly the hazard CLAUDE.md rule 1c names ("no VISA/serial call may sit anywhere on the
frame acquisition path"). Its second call site is d99.

**Nothing was changed about it.** This is a measured fact recorded for later judgement: it tells the
restructure that the focus-adjust path must be moved off the frame loop (rule 1c) and it tells check A that a
COMMAND site lives inside the loop with the tightest time budget. It is not this cycle's work.

## Limits — what the census does NOT say

It does **not** trace the position input backwards; that is check A. The only limit fact it records is
diagram-level co-occurrence: `Max Trans Pos.vi` (the original's limit source) appears on diagrams **19 and
87 only**, so **no motion call site shares a diagram with it** — including the startup ASI move on diagram 10
that the plan flags (`docs/main-vi-startup.md:33`). That is weak evidence of an unbounded path, not proof:
a coerce can live on another diagram and arrive by wire.

## Two routes that do NOT work — do not retry them

1. **Offline byte/zlib scan** for "VISA Write": absent from `SetCommand.vi`'s bytes although it holds five.
2. **`VI.Callees`** as the call-graph source: it returns NAMES (and `.ctl` typedefs), `GetVIReference` on a
   bare name does not resolve, and `count(Diagram)` then dies with error 1445/7. This broke census run 1
   (`tools/bench/motor_census.log`, **SUPERSEDED — do not cite its numbers**): 72 of 126 VIs errored, 109
   UNKNOWN, and MOV/VEL/GOH/Move Axis to Position were reported as name-list-only. Use `subvis(vi, d)` per
   diagram, which returns the real `VI Path`.
