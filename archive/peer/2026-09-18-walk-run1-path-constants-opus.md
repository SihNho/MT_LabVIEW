# walk-run1-path-constants-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.2463  in 18 / out 32529 / cache-create 197865 / cache-read 771327  (458s, 21 turn(s))
- **date:** 2026-09-18 01:49:50
- **outcome:** ANSWERED (462s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS CLAIM. It is a post-hoc explanation of a failed prediction and it will decide whether the next run
is a simple rerun or a real investigation.

CONTEXT — LabVIEW 2026 VI Scripting driven from Python/COM. The probe script is
`tools/bench/probe_flatseq_walk.py`; its run-1 log is `tools/bench/probe_flatseq_walk.log`
(BGRUN END rc=0 after 43s, 4 of 6 gates pass).

WHAT WAS PREDICTED AND WHAT HAPPENED
  C2 predicted `gscript.report_all(V6, "FlatSequenceInnerTunnel")` returns >= 14 objects.
     OBSERVED: it raised `error 7: Open VI Reference in OpReportAll_v0.vi<APPEND>`.
  C5 predicted a backward wire walk from block-diagram 10, Nodes[1] (uid 44036, the ASI
     `Move Axis to Position.vi` call site), terminal 8 `Position [internal units]`, wire 44089,
     makes at least one hop.
     OBSERVED: for all three seed wires (44089, 44104, 44107) the walk printed
     `hop 1: wire <n> returned NO terminals at all` and stopped with zero hops.
  Also observed in the same run: 14 reads of `OpOwnerChain_v1` on FlatSequenceInnerTunnel uids
     (5818, 2886, 5183, …) each returned `error 7: Open VI Reference in OpOwnerChain_v1.vi<APPEND>`
     followed by `error 1055: To More Specific Class in UID to GObject Reference.vi`.
  And: `MOV.vi`, `VEL.vi`, `GOH.vi` and `Max Trans Pos.vi` were all reported "NOT ON DISK".

THE CLAIM UNDER ATTACK
  "Every one of those failures is explained by two wrong PATH CONSTANTS in the probe script, and nothing
   about LabVIEW, VI Scripting, the ops, or the FlatSequenceInnerTunnel class is implicated:
     (a) the script pointed at `…\2. Tracking\V6_ParallelLoop\Min_Track N beads V6_ParallelLoop.vi`, but the
         V6 working copy actually sits one directory up at `…\2. Tracking\Min_Track N beads V6_ParallelLoop.vi`
         (confirmed by `tools/bench/main_vi_nodeterms.json` line 2 and by
         `tools/bench/motor_census_v6-workingcopy.json` field target.vi). LabVIEW error 7 is 'file not found',
         so every read of that path failed before touching any object;
     (b) `MOV.vi`/`VEL.vi`/`GOH.vi` were existence-checked with `os.path.exists` on a path INSIDE an .llb
         (`…\General command.llb\MOV.vi`). An .llb is a single file, so that test is always False even though
         LabVIEW can open the VI by that path.
   Therefore C2 and C5 were never actually tested, the correct action is to fix the two constants and rerun,
   and no further diagnosis is warranted."

WHAT HAS ALREADY BEEN RULED OUT (do not re-suggest these without a new reason)
  - Not a stale/killed LabVIEW: the run began with no LabVIEW process, `fresh()` started pid 16624 and the COM
    preflight agreed twice (16 wires); the property-node work in the SAME run and the SAME session succeeded
    (six property ids attached on a scratch VI, four refused with error 1077).
  - Not a broken op: `OpReportAll_v0`, `OpOwnerChain_v1` and `OpWireSource_v5` are all on disk and all three
    failures carry `Open VI Reference`, i.e. the failure is at reference-open time, not inside the op's logic.
  - Not a permissions/rig issue: the run opened no serial port and moved no motor.

WHAT I WANT FROM YOU
  1. The strongest reason the claim is WRONG — in particular, any way `error 7 Open VI Reference` on a path that
     really does not exist could COEXIST with, or MASK, a second independent defect that would still make C2 or
     C5 fail after the path is fixed.
  2. An alternative explanation for the `hop 1: wire 44089 returned NO terminals at all` result specifically —
     e.g. anything about `Wire.Terminals[]` (6371003), `Terminal.Is Source?` (634A003), or a wire that lives on
     a FLAT SEQUENCE frame's diagram, that would produce zero readable terminals even with the right VI path.
     Note wires 44089/44104/44107 were read out of a CACHED census taken days earlier on the same file; say
     whether a cached wire UID can go stale while the file's md5 is unchanged.
  3. The observation that would FALSIFY the claim.
  4. The cheapest test that separates "wrong path only" from "wrong path AND something else".



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

No LabVIEW lock taken, nothing built, nothing edited, nothing run. Review follows.

---

# REFUTATION — "two wrong path constants, just rerun"

## 1. The single strongest reason the claim is WRONG

**The wrong path did not merely prevent C2 and C5 from being tested — it silently disabled the rule-1 integrity gate, and that gate reported PASS.** The claim's frame ("the measurement never happened, so nothing else is implicated") stops one question too early: it never asks what *else* the bad path switched off.

`probe_flatseq_walk.py:108-116` — `md5()` returns the **string** `f"ERR {e}"` on failure. `main()` then compares snapshots by string equality (`:496-498`). For the V6 working copy, before and after were both `"ERR [Errno 2] No such file or directory: …"` (`probe_flatseq_walk.log:7` and `:102`) — equal strings — so:

```
PASS C1 every pre-existing .vi md5 unchanged  | []          (log:110)
```

passed **without ever hashing the file it exists to protect**, and the same vacuous pass covered MOV/VEL/GOH and `Max Trans Pos.vi`. Four of the nine rule-1 files were never checked and the gate certified them unchanged.

The same defect is in the other passing gate. `:475-478`:

```python
all(... for v in RESULTS["m3"].values() if v.get("exists"))
```

The `if v.get("exists")` filter **excludes exactly the entries that failed**. C6 "every motion subVI opened and reported ≥1 diagram" PASSED while printing four `None`s inside its own detail line (`log:98`). So the headline "4 of 6 gates pass" is wrong: two gates were measured (C3, C4), two passed vacuously (C1, C6), two failed. Fixing `V6 = …` repairs none of this.

This is not academic for the next run. Run 1 never opened MOV/VEL/GOH/TMX?. **Run 2 is the first run that loads third-party PI Mercury driver VIs out of two LLBs into LabVIEW 2026** — precisely the relink-and-dirty hazard CLAUDE.md rule 1 is written about — and it does so behind a `md5()` that returns a value equal to itself on failure. The claim calls that "a rerun".

**Additionally, the claim miscounts its own causes.** There were **three** wrong path constants, not two. `Max Trans Pos.vi` is not in an LLB, so explanation (b) does not cover it. The log's path (`log:14`, `log:94`) is `…\MinLab\zz_LabView VI\zz_LabView VI\DY\Background VIs\…` — `zz_LabView VI` is **doubled**. The file exists at the single-segment path (Glob: `G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\DY\Background VIs\Max Trans Pos.vi`). `probe_flatseq_walk.py:72` already carries the corrected `LAB`, and the run-1 post-mortem in the docstring (`:31-38`) does not mention it.

And the script has been edited more than the claim admits: run 1 printed **two** `SetCommand_signed candidate` lines (`log:96-97`) against one entry in `SIGNED_HINTS` (`:91`), and `M3_VIS` now holds **ten** entries (`:76-87`) while the log shows only **seven** VIs attempted. So run 2 is not a rerun of run 1's experiment — at least three independent things changed. Calling it a rerun is how a changed variable goes unnoticed.

**Finally, "nothing about the ops is implicated" is false on the log's own text.** Fourteen times (`log:36-49`):

```
error 7: Open VI Reference in OpOwnerChain_v1.vi<APPEND> error 1055: To More Specific Class in UID to GObject Reference.vi
```

Error 1055 is "Object reference is invalid" ([NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE)). Had `OpOwnerChain_v1` serialised its error cluster, `UID to GObject Reference.vi` would have received error 7 on error-in and returned it unchanged — a conforming LabVIEW VI does nothing when error-in is set. It could not have *generated* a new 1055. So the downcast **ran anyway**, on a reference the previous node had failed to produce: the op's error chain is not serialised. Its outputs after an upstream failure are indeterminate rather than absent, which makes `error out` the only trustworthy thing it emits — and that is exactly the value the M2 walk throws away (next section). The path revealed this; it did not cause it.

## 2. Alternative explanation for `hop 1: wire 44089 returned NO terminals at all`

**That string is not a measurement. It is the probe's default whenever the op fails to overwrite the poison at `term_index = 0` — for any reason at all.**

`wire_source()` (`:301-336`) poisons the outputs, runs the op, captures `err`, builds `r`, and then at `:332`:

```python
if r["owner_uid"] == 0 and not r["is_source"] and r["owner_class"] in ("POISON", ""):
    break
```

The break fires **before** `out.append(r)`, so `r["err"]` is discarded — never printed, never stored. `src is None` then produces the string at `:352`. At least five mutually exclusive causes emit it byte-identically:

1. **error 7, path missing** — the claim's story; outputs never written.
2. **`Wire.Terminals[]` returned an empty array** → `Index Array` on an empty array yields the default element **with no error** → the downcast then errors 1055 → discarded.
3. **The uid did not resolve to a Wire object** (wrong VI, or the NI-documented UID-reuse case) → 1055 → discarded.
4. **Terminal 0 exists but `Is Source?` / `Class Name` failed to read** → poison survives.
5. **A `SetControlValue` label mismatch** left the op reading the previous iteration's inputs.

Cause 1 is *sufficient* — I traced it and it holds. It is nowhere near *necessary*. The decisive consequence: **after the path is fixed, causes 2–5 print the same line**, so a plain rerun cannot discharge C5 in either direction. (Caveat, stated as inference not measurement: cause 2 assumes `OpWireSource_v5` indexes `Terminals[]` with the Index Array primitive. I cannot confirm that — AGENTS.md forbids me opening the `.vi`. Ask for reporter output on that op if it matters.)

**On your cached-UID sub-question — the seeds are sound, and I can say so from the files.** `main_vi_nodeterms.json:2` names the **correct** working-copy path; node uid 44036 is at `:4188`; wires 44089/44104/44107 are its terminals at `:4291/:4303/:4315`. So the seeds were not hand-copied. And LabVIEW UIDs are documented as persistent: *"A UID is always associated with the same object, even after you save the VI… UIDs are unique, and persist for the lifetime of the object, across saves, compiles, VI copies"* ([LabVIEW Wiki](https://labviewwiki.org/wiki/GObject_class/UID_property)). Unchanged md5 therefore makes silent drift unlikely — **but** the same page carries NI's caveat that a *deleted* object's UID may be reassigned, with the advice to validate by also reading Class Name, which the walk does not do at the point it breaks. And your premise is not actually established by this run: run 1 has **no** md5 of the working copy at all. The nearest recorded hash is `motor_census_v6-workingcopy.json:5` = `2a78e17c449cacdaf5da389818526859` (taken 2026-09-17 23:49). Comparing against it is a real check nobody has run.

**One repeat you should know about.** The `.llb` sub-claim is mechanically right — an LLB is a single file, so `os.path.exists` on an internal path is always False, and I confirmed both `General command.llb` and `Limits.llb` really are at the hardcoded location. But this is **not a one-file typo: the same false test already fired in the previous probe of the same cycle.** `probe_flatseq_offline2.log:18-24` shows `MOV.vi exists=False MOV.vi` and `SetCommand.vi exists=False SetCommand.vi` — with the bare **basename** as the path, because the census stores callees as names, not paths (`probe_flatseq_offline2.py:47-50,59`). `SetCommand.vi` demonstrably exists (md5 `d8b7a775…`, `log:13`) and Q3 called it absent. So the walk's M3 paths were **hand-written guesses**, not census-derived as its docstring claims (`:11-17`), and "existence-checked something that was never a path" is a `repeated-failure-class`, not a constant.

## 3. The observation that would FALSIFY the claim

Run 2 with all three constants fixed and `os.path.isfile` confirming each target:

- **C5 still prints `NO terminals at all`** → falsified; the path was not the only cause.
- **C2 still raises error 7** on a path `isfile()` confirms → falsified; error 7 here is not "file not found" (it also fires on qualified-name/library-structure problems — [NI forums](https://forums.ni.com/t5/LabVIEW/Error-7-occurred-at-Open-VI-Reference/td-p/2778322)).
- **C2 returns a number but < 14, or 0** → "never tested" is confirmed, but the implied "the class is fine" is refuted and `d1-build-plan.md:735` comes back into play. Note `probe_flatseq_instances.json` is **not** a traverse result — it is mined from a prior wire walk's hops (`probe_flatseq_offline2.py:62-77`), so "14" is a lower bound of convenience, not an independent prediction.
- **Confirming outcome:** C2 ≥ 14 and C5 ≥ 1 hop with *only* the constants changed. Even then it shows cause 1 was sufficient, not that 2–5 are absent — those three wires simply would not exercise them.

## 4. Cheapest discriminating test

**Step 0 — seconds, pure Python, no LabVIEW, before spending a COM run:** `isfile(V6)`; `md5(V6) == "2a78e17c449cacdaf5da389818526859"` (`motor_census_v6-workingcopy.json:5`); `isfile` on both LLBs and on the de-doubled `Max Trans Pos.vi`. I have already done three of these — the LLBs and `Max Trans Pos.vi` exist. **The md5 comparison is the one still open**, and it is the only thing that currently substantiates "the file's md5 is unchanged".

**Step 1 — the actual discriminator, one line, no new op, same 43 s:** move `out.append(r)` **above** the break at `probe_flatseq_walk.py:332` and print `r["err"]` and `r["owner_class"]` on every iteration *including the breaking one*. That converts the ambiguous default into a reading:

| what `err` says on the breaking iteration | verdict |
|---|---|
| contains `error 7` | wrong path only — claim confirmed |
| contains `1055` | uid didn't resolve / `Terminals[]` empty — **a second defect, independent of the path** |
| empty, outputs still `POISON` | the op ran clean and returned nothing — the FlatSequence/`Terminals[]` hypothesis is live |

Three mutually exclusive outcomes, zero extra cost. Without it, run 2 is not an experiment — it re-runs an instrument that cannot report its own failure mode, and either result brings you back here.

**Step 2 — same run, free, and do not skip it:** make `md5()` return a sentinel that does **not** compare equal to itself (or track `exists` separately), and make C6 count filtered-out entries as failures. Otherwise the run that first loads third-party LLB VIs into LabVIEW 2026 can again report PASS for files it never touched.

## Where I still think the claim holds, and what would change my mind

**"The wrong V6 path is sufficient to produce every observed failure"** — I believe this; I traced the mechanism through `wire_source`'s break and it is sound. **"Therefore nothing else is implicated and no further diagnosis is warranted"** — this does not follow, and the log contradicts it in four places (C1 vacuous, C6 vacuous, the op's unserialised error chain, the third wrong constant). What would change my mind is the Step-1 instrumented run showing `error 7` on the breaking iteration for all three seed wires, C2 ≥ 14, and C6 passing with all seven — sorry, all **ten** — M3 entries actually opened. That is one run away and costs one line more than the rerun the claim proposes.

**Sources:**
- [GObject class/UID property — LabVIEW Wiki](https://labviewwiki.org/wiki/GObject_class/UID_property)
- [Error 1055 from a Property or Invoke Node — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE)
- [Error 7 occurred at Open VI Reference — NI Community](https://forums.ni.com/t5/LabVIEW/Error-7-occurred-at-Open-VI-Reference/td-p/2778322)
- [Error 7 at Open VI Reference for a Stand-Alone Application — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8MGSA0)

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL, and every named fix was applied before the next run** (material session, cycle 19,
2026-09-18). The review REFUSED the claim "two wrong constants, nothing else implicated" and it was right on
all four counts. Applied to `tools/bench/probe_flatseq_walk.py`, then re-run as
`tools/bench/probe_flatseq_walk_run2.log` (**9/9 gates**, 82 s):

1. **C1 was vacuous** — `md5()` returned the same `"ERR [Errno 2] …"` string before and after, so the rule-1
   gate certified four files it never hashed. `md5()` now returns `ERR#<seq>`, which cannot compare equal to
   itself; C1 can no longer pass on an unhashable file.
2. **C6 was vacuous** — its `if v.get("exists")` filter excluded exactly the failing rows. C6 now requires
   `len(RESULTS["m3"]) == len(M3_VIS)` and an integer diagram count for **every** entry; run 2 reports all ten.
3. **The decisive fix.** `wire_source()` discarded the breaking iteration together with its error, so five
   different causes printed one string. Every iteration is now appended and printed with all eight stage error
   clusters. Run 2's answer came back as a *reading*: `Terms[0] src=True owner 'FlatSequenceOuterTunnel' uid
   43605 … err='' stage={}` — cause 1 (wrong path) confirmed, causes 2–5 excluded by the empty error.
4. **Three wrong constants, not two** — `Max Trans Pos.vi` had `zz_LabView VI` doubled; fixed, and the file
   opened in run 2 (1 diagram). The docstring's claim that the M3 paths were census-derived was also wrong and
   is corrected in place: they are resolved by Glob against the disk, because the census stores callee NAMES.
5. Steps 0 and 1 were both run: `C0a` isfile on every target, `C0b` `md5(V6)=2a78e17c449cacdaf5da389818526859`
   equal to `motor_census_v6-workingcopy.json`, and the open control `count(V6,'Diagram') = 170` — so run 2's
   later reads are attributable to the object, not to the path.

The one point NOT acted on is the request for reporter output on `OpWireSource_v5`'s internals: run 2's clean
`err=''` on a successful hop made it unnecessary. The `repeated-failure-class` observation (the same
`os.path.exists`-on-a-non-path mistake in `probe_flatseq_offline2.py`) is reported to the judgement session as
a fact, not disposed of here.

(Claude fills in)
