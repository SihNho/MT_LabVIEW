---
type: archive
status: archived
date: 2026-09-18
tags: [status-narrative, cycle19, flat-sequence, motor-limits]
---

# STATUS narrative relocated 2026-09-18 (rule 4) — cycle 19's measurements, and cycle 18's block verbatim

STATUS.md reached 127 lines. Nothing here is rewritten; it is moved. STATUS keeps one line and a pointer.

## §1 Cycle 19 — MEASUREMENT ONLY (material session, read-only, 4 LabVIEW runs)

Rule-1 evidence, every run: `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` md5
`c39f36e0675339673b707c59f0784fee` and `Min_Track N beads V6_ParallelLoop.vi` md5
`2a78e17c449cacdaf5da389818526859`, identical **before and after**; the ASI/PI/Autonics driver VIs and both
Mercury `.llb` containers likewise. Nothing saved. No motor moved, no motor port opened,
`motor_gate.py --execute` never called (cycle19 Pre-decided 1). One scratch VI per run in `user.lib\claudeDev`,
deleted in the same run. Lock acquired 01:35, released 02:08.

### M1 — can the backward walk cross a flat-sequence frame?

The peer hypothesis (`archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md:57-62`) was **confirmed on
the machine, and it was about the wrong class for this site**.

| class | Traverse count on the V6 copy | property ids MEASURED (attach + data-terminal short name) |
|---|---:|---|
| `FlatSequenceInnerTunnel` | **518** | `1C3A9000` **LeftTerm** · `1C3A9001` **RightTerm** · `1C3A9002` **LeftFrame** · `1C3A9003` **RightFrame** |
| `FlatSequenceOuterTunnel` | **58** | `3195B800` **OuterTerminal** · `3195B801` **InnerTerminal** · `3195B802` **Frame** |
| `FlatSequence` | 21 | — |
| `FlatSequenceFrame` | **not a valid Traverse class name — error 1092** | — |

REFUSED with **error 1077** (= not a member of that class): `1C3A9004`, `1C3A9005`, `3195B803`; the Tunnel ids
`6356000` / `6356001` on the inner class (**so it does NOT inherit from `Tunnel`**); `634A002` on the outer
class; and `1C3A9000` on the OUTER class — the discriminator both review arms asked for, proving the two tunnel
classes are siblings, not parent/child. Both class strings `VI Server:FlatSequence{Inner,Outer}Tunnel` resolve
(positive control `632A813` → `UID`).

All 14 known `FlatSequenceInnerTunnel` uids resolve through `UID to GObject Reference.vi` with **no error**:
self-echo class `FlatSequenceInnerTunnel`, owner `FlatSequence` uid 681, cast class `FlatSequence`.

⚠️ **NOT measured: a LIVE READ of any of these properties on a real instance.** Attaching an id to a class
proves membership; it does not prove that a runtime reference casts to that class or that the returned Terminal
is connected and usable. Both dual arms insisted on this distinction. → STATUS OPEN 45.

### M2 — how far does the walk get, and what actually stops it

Start: diagram 10, `Nodes[1]`, uid **44036** = `ASI TG-1000.lvlib:Move Axis to Position.vi` (the startup move),
owner structure `FlatSequenceFrame`. Three wired inputs, each walked backwards through
`Wire.Terminals[]` + `Terminal.Is Source?`; every hop returned `err='' stage={}`:

| terminal | wire | hops | chain | stopped on |
|---|---:|---:|---|---|
| T[8] `Position [internal units]` | 44089 | **1** | → `FlatSequenceOuterTunnel` uid **43605** | the flat-sequence boundary object |
| T[9] `Axis` | 44104 | 1 | → `EnumConstant` uid 43955 | a constant (a true source) |
| T[10] `VISA in` | 44107 | **2** | → `SubVI` uid 43997 `Initialize.vi` → wire 44110 → `VISAResourceNameConstant` uid 43937 | a constant |

**Why it stopped — measured, not inferred** (`tools/bench/probe_walk_stop_control.log`, 3/3). Diagram 10's
**live** `Nodes[]` is exactly `[(43997,'Initialize.vi'), (44036,'Move Axis to Position.vi')]`, identical to the
cached census — so the cache is not short. All three stop objects are **absent from `Nodes[]`** yet
**Traverse-visible** (58 / 14 / 3 of their classes) and UID-addressable. The `EnumConstant` is the oracle: a
constant is obviously in the VI, and it too is outside `Nodes[]`.

**So the barrier is the probe's `Diagram[d].Nodes[n]` ADDRESSING, not LabVIEW.** LabVIEW handed back the
boundary object cleanly on the first hop. What is missing is a UID-addressed reader.

### M3 — where do the limits live? Not in the motion subVIs

Read-only label scan of each callee's OWN diagrams (`Node.Label` 6359001 via `gscript.node_labels`), then a
sensitivity check because "0 matches" is worthless if the method cannot see primitives.

| subVI | diagrams | node rows | non-empty labels | limiting constructs |
|---|---:|---:|---:|---|
| `MOV.vi` (PI) | 7 | 11 | 11 (100 %) | **0** |
| `VEL.vi` (PI) | 13 | 32 | 32 (100 %) | **0** |
| `GOH.vi` (PI) | 5 | 13 | 13 (100 %) | **0** |
| `TMX?.vi` (PI) | 5 | 18 | 18 (100 %) | 1 — the control label `Maximum travel limit`, i.e. the QUERY's own output, not a coerce |
| ASI `Move Axis to Position.vi` | 5 | 9 | 9 (100 %) | **0** |
| ASI `Move Axis Relative.vi` | 5 | 9 | 9 | **0** |
| Autonics `SetCommand.vi` (rotor) | 6 | 26 | 26 (100 %) | **0** |
| `Max Trans Pos.vi` (lab) | 1 | **0** | 0 | **0 — the diagram has no nodes at all** |
| `Motor control v5_No Recording.vi` (lab) | 18 | 35 | 35 | **0** |
| `ASI_adjust focus-subvi.vi` (lab, frame loop) | 9 | 13 | 13 | **0** |

**The scan is fully sensitive**: every primitive reports its own name — the dumps contain `Not Equal?`, `Not`,
`And`, `Multiply`, `Index Array`, `Compound Arithmetic`, `Type Cast`, `VISA Write`, `PI Send String.vi`. An
`In Range and Coerce` or `Max & Min` would have been seen. Caveat that remains: `Nodes[]` excludes constants
and control terminals, and an implicit coercion **dot** is not a node.

`Max Trans Pos.vi` holding no nodes is consistent with the STATUS banner's `Max Trans Pos` = 40.94 — it returns
a constant, and the **coerce is in the CALLER's diagram**, not in this subVI.

`SetCommand_signed.vi` (CLAUDE.md rule 1b, the rotor's signed variant) **does not exist on disk**: nowhere under
`G:\Codes\LabVIEW_Codes\MinLab`, and `instr.lib\Autonics Motor\` holds only `Close.vi`, `Configure.vi`,
`SetCommand.vi`.

### M4 — which VI is the census keyed to

`docs/motor-call-site-census.md`'s **97 sites / 43 in scope** come from
`tools/bench/motor_census_3state-ORIGINAL.json`, whose `target.vi` is
`…\2. Tracking\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` (md5 `c39f36e0675339673b707c59f0784fee`) —
i.e. **keyed to the 3StateClamping ORIGINAL**. A parallel `motor_census_v6-workingcopy.json` holds 98 sites,
also 43 in scope (the extra is the inserted `IMAQ Write TIFF File 2`), with the SAME uids — site 44036 is
byte-identical in both files except for `owner_vi`.

**But the cached node/terminal census is keyed to the V6 WORKING COPY, not the original**:
`tools/bench/main_vi_nodeterms.json` (704 KB, `vi` = `…\Min_Track N beads V6_ParallelLoop.vi`, 170 diagrams,
626 nodes) and `tools/bench/d1_step0_census.json` (`md5: 2a78e17c449cacdaf5da389818526859`). No cached
node/terminal census keyed to the 3StateClamping original exists on disk. So **the 43 site IDENTITIES are
stated for the original, while every terminal/wire index a check-A walk would use is cached only for V6.**

### Runs and logs

| log | gates | note |
|---|---|---|
| `tools/bench/probe_flatseq_offline{,2,3}.log` | — | offline, no LabVIEW; M4 + the walk's seeds |
| `tools/bench/probe_flatseq_walk.log` | 4/6 | **run 1, invalid** — three wrong path constants; two of its passing gates were vacuous |
| `tools/bench/probe_flatseq_walk_run2.log` | **9/9** | M1 inner-class census, M2 walk, M3 scan |
| `tools/bench/probe_flatseq_outer.log` | **5/5** | outer-class census + M3 sensitivity |
| `tools/bench/probe_walk_stop_control.log` | **3/3** | the negative control that settles M2's stop reason |
| `tools/bench/peer_fsit_props.log` | ANSWERED | codex `-Kind fact`, the class tables |
| `tools/bench/peer_walk_run1_dual.log` | ANSWERED ×2 | mandatory failed-prediction review of run 1 |
| `tools/bench/peer_walk_run2_dual.log` | ANSWERED ×2 | the review that caught the wrong-class error |

## §2 Cycle 18 — relocated verbatim from STATUS.md

🆕 **CYCLE 18: the STOP RECORD + LAUNCH GATE is BUILT and PROVEN — `device-failed` DISCHARGED** (`violations.py`
= "0 slug(s) awaiting a response"). `tools/stop_record.py` + `guard_bash.py:156` / `guard_cycle.py:462`; **refusal
by PATH, release qualified by HASH**; fail-closed; **`prior_art_review.py` now REFUSES without `--recipe`**;
29/29 self-test gates. Full text → `archive/2026-09-18-status-cycle18-stopgate.md` §1; decision →
`docs/violation-decisions.md` round 6.
🆕 **`doc_ingest` contradiction RESOLVED (judgement): CLAUDE.md:49's 조립 row was stale, STATUS was right.** Both
sources are the user's; the 2026-09-17 evening envelope decision is LATER and NARROWS (one gateway + enforced
envelope), so it amends the 2026-09-16 table. CLAUDE.md rule 1b now carries the amended row + the why.
**P1 step 1 (CENSUS) IS CLOSED** — `tools/motor_census.py` → `docs/motor-call-site-census.md`: 97 sites, **IN
SCOPE 43, undecided 0**, originals' md5 unchanged. 🔴 **Rule 1c fact: `ASI_adjust focus-subvi.vi` (COMMAND) is
called on diagram 43 = the FRAME LOOP** — the ORIGINAL already puts serial traffic on the frame acquisition path.
Recorded, nothing changed. Numbers → `archive/2026-09-18-status-cycle18-stopgate.md` §2.
**Stage 1 CLOSED**; **Stage 2** `…CPU_core_v0` 69/69 · `…_queue_v0` 162/162 — bit-identical for the **first
10,018 frames only**, both **replay**. **THE GAP:** 174 ops, 123 recipes, 235 peers → **zero runnable
experimental VIs** (`archive/2026-09-18-status-cycle1-census.md` §2).

## §3 Cycle 19 CLOSE-OUT — the prior-art release, verified (relocated from STATUS's OPEN 44/45, 2026-09-18)

STATUS's OPEN 44 and OPEN 45 read, verbatim, before they were retired:

> 44. 🔴 **CHECK A IS STOPPED BY ITS OWN PRIOR-ART GATE — judgement only.** The check-A tool (`motor_wiring_check`
>    under `tools/`, never built) carries a standing stop record (`archive/peer/2026-09-18-priorart-check-a-wiring.md`,
>    `released: null`) and `guard_bash` refuses every command naming that path. Review disposed 2026-09-18; the
>    `FIXED:`/`REFUTED:` release is the judgement session's to write.
> 45. 🔴 **judgement only — build the UID-addressed tunnel reader, or not?** Cycle 19 measured that the ids attach
>    and the instances resolve, but **that is not a live read** (both dual arms). One op (`UID → TMSC(FlatSequence*
>    Tunnel) → OuterTerminal/InnerTerminal`) finishes check A's backward trace. Reviews:
>    `archive/peer/2026-09-18-walk-run2-flatseq-crossing-{codex,opus}.md`, ANSWERED + disposed.

Both are answered. 44: the judgement session wrote four `FIXED:` lines into the review
(`archive/peer/2026-09-18-priorart-check-a-wiring.md`:365-368) and redesigned check A as
`docs/motor-limit-assurance-plan.md` §A.1. 45: `docs/cycle20-plan.md` step 2 builds the reader.

MEASURED 2026-09-18 02:21 (`tools/bench/c19_close_release_probe.log`, `BGRUN END rc=0`, 10/10 predictions HIT,
read-only — `tools/bench/stop_records.json` byte-identical before and after, `released` still `null`):

* `guard_cycle.released_slugs()` releases **all four** verdict slugs, **0 rejected lines**.
* `stop_record._released(record)` → **`ok=True`**, first line
  `FIXED: unread-evidence - docs/motor-limit-assurance-plan.md:69 - …`. **The release is valid.**
* The same-day question: `review_time()` reads `- **date:** 2026-09-18 01:12:34` and returns
  `frontmatter date+time 2026-09-18 01:12`, NOT midnight. The comparison the code performs is
  `if fm <= rt: reject` (`tools/hooks/guard_cycle.py`:147); the plan's mtime is 2026-09-18 02:17:05 > 01:12:34,
  so **the same-day change is accepted** — and would have been accepted even at midnight basis.
* `stop_record.check_command("py tools/motor_wiring_check.py --all")` → **REFUSE**, verbatim head:
  *"this recipe has a released stop record, but the file itself cannot be read, so the release cannot be matched
  to any bytes … unreadable: tools/motor_wiring_check.py"*. The recipe has never been written; the gate allows
  and stamps its hash on the first launch after the file exists. `guard_bash` refuses any shell command naming
  that path for the same reason (`tools/hooks/material_marker.log`, two `REFUSED STOPPED-RECIPE` entries).
* NEGATIVE PROOF on a throwaway fixture (temp dir, deleted in the same run; the real store never written), per
  cycle 19/20 Pre-decided "a gate that passes only its happy path is not accepted" — all three REFUSED:
  (a) `FIXED:` citing a nonexistent path → *"cited path does not exist under the project"*;
  (b) `FIXED:` citing `AGENTS.md` (mtime 2026-09-15 14:33, before the review) → *"NOT after the review"*;
  (c) `FIXED:` placed above `## What was done with it` → *"a FIXED line sits ABOVE … only that section releases"*.
  Control: the SAME line moved inside the section releases (`ok=True`), so (c) is about PLACEMENT, not the line.

`SetCommand_signed.vi`: glob `**/SetCommand*.vi` under `G:\Codes\LabVIEW_Codes\MinLab` → **0 hits**;
`C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\` holds only `Close.vi`,
`Configure.vi`, `SetCommand.vi`. CLAUDE.md rule 1b says the new VI uses `SetCommand_signed.vi`. → STATUS OPEN 46.

## §4 The lock-block narrative, relocated verbatim from STATUS.md (2026-09-18)

```
# Cycle-19 M1/M2/M3 probes held it 01:35-02:08 (4 runs), released. READ-ONLY: both originals' md5 unchanged
# before AND after every run (3state c39f36e0…, V6 2a78e17c…); nothing saved, no motor, no serial port, one
# scratch VI in claudeDev per run, deleted in the same run.
# Cycle-17 census runs held it 23:29-23:41 / 23:49-23:53, released it. MEASURED before AND after: NO LabVIEW.exe;
# nothing run/saved, no port opened, both originals' md5 unchanged. ("pid 13480 holds COM3+COM4" was STALE.)
```
