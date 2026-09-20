# priorart-priorart-cycle15-d1

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $3.2756  in 34 / out 32696 / cache-create 148709 / cache-read 1941967  (414s, 27 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (418s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: direction-change).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
---
type: plan
status: current
date: 2026-09-16
cycle: 15
kind: delivery
tags: [plan, delivery, runnable-vi]
supersedes: [docs/cycle14-plan.md]
decided_by: user 2026-09-16 ("A濡?吏꾪뻾?섏옄")
---

# Cycle 15 ??DELIVERY: the first runnable experimental VI

**Why this cycle is a delivery cycle.** Two outcome reviews in a row (2026-09-15, 2026-09-16) reached the same
verdict: zero runnable experimental VIs; the user would still run the original next week. CLAUDE.md's rule for a
repeated OUTCOME-VIOLATION is to stop and re-plan with the user. The user chose option A on 2026-09-16 ??build the
smallest runnable VI from what is already known ??and added the boundary: **"?ш린??以묎컙 怨쇱젙??肉?寃곌뎅?먮뒗 理쒖쥌
?ㅽ뀦?쇰줈 ?섍??쇳븿."** So this cycle is *ordering*, not a new goal; the seven-loop restructure (GPU top level as
default, CPU-parallel second) remains the destination. `docs/cycle14-plan.md` (the `Diagrams[]` op, 170/170
hierarchy, A4) is superseded; A3 stands at 112/170 and is resumed only if D1 needs a diagram it does not have.

## The product, D1

**A copy of the original VI** (`restructure_inside_a_copy_of_the_original` decision) in which **only the per-frame
tracking call is swapped** for the tracker that already has a passed numeric-acceptance record on the fixture, with
everything else ??live camera acquisition, bead picking, calibration, the original's file writer
(`save N xyz traces.vi`), its stop path and its instrument shutdown ??**left exactly as the original has it**.

That is the smallest thing that is (a) runnable live, (b) rule-1a checkable (same inputs ??same X/Y/Z on the
fixture, against the original), and (c) a real step toward the final restructure, because the tracker swap is the
core of it. It is deliberately NOT the reviewer's full slice (acquisition ??GPU tracker ??new writer ??new
stop/restart): a new writer and a new stop protocol are two more untested parts, and each is a place to be wrong.
They come next (D2), once D1 runs.

## Acceptance for D1 ??numeric and functional, stated before the build

| gate | what | level |
|---|---|---|
| N1 | On the recorded fixture (10,043 frames, 5 beads), D1's X/Y/Z equal the original's for the first 10,018 frames (before the first bead loss) to the tracker's recorded tolerance ??the same statement STATUS makes for the replay VIs, now for the runnable one | numeric, rule 1a |
| F1 | D1 runs live on the camera at 90 Hz with no beads (rig disassembled; camera allowed) for ??5 min, produces a data file through the original's writer, and the file reopens | functional |
| F2 | D1 stops through the original's stop path with no error 1122 / no orphaned camera session, and restarts clean | functional |
| F3 | The rotor path, if it is touched at all, uses **`SetCommand_signed.vi`** ??user decision 2026-09-16: the rotor is signed by nature, LabVIEW's serial path lost the sign, the fix is believed found; follow the hardware number with its sign | rule, user |

`ExecState == 1` counts for nothing here.

## Order of work

1. **Measure before building** (this cycle's first material session; facts only, no build):
   a. Which trackers hold a **passed** numeric-acceptance record today, at what tolerance, against which reference
      (`archive/benchmarks/INDEX.md` rows 40??1 for the CPU queue tracker; `docs/gpu-backend.md` for the GPU
      one). The choice between them is a judgement made on that table ??GPU is the intended default, but D1 uses
      whichever is *proven now*.
   b. How the original actually stops, closes instruments and writes its file ??`docs/main-vi-state.md` and
      `main-vi-startup.md` do not say (log-reader, 2026-09-16: two matching lines in 211). Read the main VI
      headlessly: the stop Boolean's terminal and every node that reads it; the call site of `save N xyz
      traces.vi` and what feeds it; the camera-close / VISA-close nodes and which diagram owns them.
   c. The exact call site of the per-frame tracker in diagram 43 (already in `frame-loop-anatomy.md`; confirm uid
      and terminal names with `node_terms`).
2. Prior-art review (`--trigger direction-change`) on this plan, disposed.
3. Build recipe for D1 ??one script, prediction contract N1/F1/F2/F3, on a copy in `user.lib\claudeDev`; the
   original untouched (md5 before/after).
4. Run N1 offline (fixture), then F1/F2 live (camera only; no motors are needed for D1).
5. Hand D1 to the user with the four gate values. Then D2 (writer + stop protocol of the seven-loop design).

## Frozen while D1 is built (outcome review Q7, adopted)

No new general-purpose op VIs, no hierarchy completion beyond what D1 needs, no lint/annotation cleanup, no new
benchmark themes, no display polish, no review-framework changes.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-16
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

Cycle 11??3 narrative relocated 2026-09-16 (rule 4; STATUS had reached 526 lines) to
**`archive/2026-09-16-status-cycles-11-13-narrative.md`**, unchanged. Open it only when a line here is ambiguous.
?좑툘 **ONE SESSION AT A TIME** ??two ran concurrently on 2026-09-16 and both edited the active docs. Check for a
live session, and **re-read `CLAUDE.md` and this file from disk** rather than trusting a summary.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`docs/cycle10-plan.md` is superseded ??it is that plan's Phase A).
   Settled decisions that must not be re-opened: **`docs/decisions.md`**. Current cycle plan: `docs/cycle14-plan.md`.
2. ??**Prior-art gate layer is live and its hole is fixed** ??`guard_cycle.py` accepts `REFUTED:` and
   `FIXED: <slug> - <path>:<line> - <what changed>` (5/5 tested; both forms in `CLAUDE.md` 짠"Review has THREE layers").
3. ??**Retrospectives for cycles 10??3 DONE and disposed.** 11 and 12 fired ALL NINE slugs, 13 fired six. That
   saturation is what `tools/retrospective.py` **v2** (2026-09-16) exists to fix; v1 frozen at
   `tools/retrospective_v1.py`; numbers in `tools/bench/retro_v2_comparison.md`.
4. ??**SOLVED ??scripting EDITS are silently declined until the target's FRONT PANEL has been opened** (not
   "until the diagram is loaded" ??refuted). Fixed by `ensure_loaded()` in `tools/gscript.py`, guarding 26 mutating
   wrappers; readers untouched. Measurement tables ??narrative archive, item 3.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# last held material/cycle13-A3b, 2026-09-16 20:10-20:11: diag_flatseq_diagrams_attach.py (END rc=0, 33 s, 5/0).
# MAIN VI NEVER OPENED (scratch copy of EMPTY_v0, deleted in the same run, gate Z); no op saved; pid 17996 exited.
# Earlier holders: archive/2026-09-16-status-cycles-11-13-narrative.md
```
**Never assume an instance exited** (measured: pid 14352 did not): `tasklist | grep -i labview`, kill strays.
Fresh instances ??1,500 handles; unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (user, 2026-09-16; CLAUDE.md rule 1b). **Only the user announces a state
change**; never infer one, and do not ask per incident inside a declared state.
Instruments: rotor counter **0** 쨌 magnet motor full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`. **A camera session open RESETS ROI *and* exposure** ??the acquisition loop must apply the
contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**; fixture work unaffected (10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand
**Stage 1 (analysis) CLOSED** ??`docs/`: `instrument-libraries`, `main-vi-subvi-identity`, `main-vi-panel-map`, `main-vi-state`, `main-vi-startup`, `frame-loop-wire-graph`, `rotor-sign-diagnosis`. Raw: `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS**, cycles 1??3 (`docs/stage2-plan.md`). `Track_v6_CPU_core_v0.vi` 69/69 PASS 쨌
`Track_v6_CPU_queue_v0.vi` 162/162 PASS. **Say it exactly:** bit-identical to the reference for the **first 10,018
frames only** (before the first bead loss), and both are **replay** artefacts ??recorded TIFFs, `FOR` loops, no
live acquisition, no stop protocol.
**THE GAP (outcome review, 2026-09-15):** 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and
**zero runnable experimental VIs**.

## OPEN

1. ?윞 **Is the PERIODIC auto-reset gated by `Auto-Reset`?** Measured on the wire side: `ForLoop#1359`'s ten
   terminals carry **no** `Auto-Reset` (wire 9806) and zero panel-control sources ??**not gated at the wire level**.
   Not final ??a `Value` property read inside #1359 could still gate it; one read closes it (cycle 14 짠5). Tables ??narrative archive, OPEN 1.
2. ?윟 **Autofocus path CLOSED** ??the switch that stops the piezo is `Auto-Focus` (uid 24266);
   `CaseStructure #10407` fires every 25 frames ??3.6 Hz. `docs/camera-acquisition-facts.md`.
2c. ?윟 **uid 9775 READS camera geometry; the size the VI WRITES is the front-panel display area, not the ROI** ??
   the 1280횞1024 budget basis is safe. Do NOT widen to "the VI does not set frame size" (codex refuses it);
   residual test: `Property Items[] ??Is Write` over the 106 Property nodes.
3. ?윞 **Peer-archive dispositions** ??39 pre-2026-09-15 closed as `disposition: legacy` (`tools/mark_legacy_dispositions.py`,
   4/4 gates; doc_lint L6 skips them); **26 dated ??09-15 are real debt**. L1: 54 of 324 docs still lack frontmatter.
4. `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it**.
5. **Startup drives instruments** (ASI on diagrams 10/88, PI on 1/3/4/5 ??`main-vi-startup.md:22-33`). Allowed
   while apart; a hard blocker at assembly. Excise node-by-node in the build log, not wholesale (rule 1a).
6??. ??RESOLVED ??bgrun's failure regex narrowed (11/11), REVIEW logs skip the inner-failure scan, and the
   `premature-build` / `scope-creep` devices are built and tested. ??narrative archive.
9. ?윟 **A2 DONE** ??owner semantics for all six structure classes (54/54); `FlatSequence` the one exception
   (owner uid 0, error 1055). `docs/diagram-hierarchy.md`. ??narrative archive for the three judgement calls.
10. ?윟 **A3 MEASURED for the 112 clean diagrams** (100 agree / 0 disagree; `tools/bench/diagram_tree_a3.json`).
   Left: exactly the **57 `FlatSequenceFrame` diagrams**, and they ARE reachable ??`FlatSequence.Diagrams[]` =
   **3578BC00** measured attaching. ?윞 Walking it needs ONE new op VI: the judgement call cycle 13's STOP condition reserved. ??narrative archive, OPEN 10.
11. ??**Retrospective v2 ADOPTED; its five OPEN items A?밇 are all closed** ??dispositions in
   `tools/bench/retro_v2_comparison.md` 짠7. `violations.py --due` is **empty, rc=0**; cycle 11's review cost reads
   **$0.0000 ??$19.6411** after the regex repair; the cycle window is now **previous retrospective ??this cycle's
   retrospective dispatch** (cycle 11 = `14:33:20 .. 19:08:16`, which the plan-mtime window started at 17:38:44).
12. ??**Document lint + ingest BUILT, and the first backlog is CLEARED** (`docs/doc-lint-plan.md`).
   `tools/doc_lint.py` runs inside `audit_cycle` as L-lines; `tools/doc_ingest.py` dispatches the sonnet
   consistency read to `archive/ingest/` (invisible to all six gates; `-Role ingest`, registered in `logclass.py`).
   **doc_lint 3 fail/3 warn/3 pass ??1 fail/3 warn/5 pass**: L2 and L4 fixed, only L6's 26 post-09-15 dispositions
   left. The ingest's **7 contradictions: 6 resolved in the docs, 1 left to the user** (PAIR 4, rotor `SetCommand`).

## NEXT

?윟 **Slug block cleared** (`violations.py --due` empty, rc=0) and the **OUTCOME REVIEW is RUN and disposed** ??
`archive/peer/2026-09-16-outcome-review-20260916.md`, ANSWERED 241 s, **7 OUTCOME-VIOLATION slugs**.
?뵶 **JUDGEMENT NEEDED before the next recipe build:** CLAUDE.md turns that into a **delivery** cycle, which
contradicts `docs/cycle14-plan.md` (짠3 `Diagrams[]` op, 짠4 A3 ??170/170, 짠5 OPEN 1's read, 짠6 A4).

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md` settled decisions** 쨌 `docs/NAMES.md` verified strings 쨌
`docs/toolkit-capabilities.md` API 쨌 `docs/restructure-plan-4.6.md` target 쨌 `docs/pre-rig-master-plan.md` the plan 쨌
`docs/diagram-hierarchy.md` A2/A3 쨌 the reasoning in `archive/2026-09-16-status-cycles-11-13-narrative.md` and its
two siblings (session-gate-and-autofocus, cycles-8-10) 쨌 `archive/` history (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled in this session, so the review is delivered here in full. **12 findings, zero `novel`.** The two that matter most are A1 and A2: the plan's product is the one construction method `docs/decisions.md` explicitly excludes, and it is the inverse of the option the user actually chose.

---

# PART A — THE DIRECTION

## A1 `settled-already` + `contradicted` — a hot-path-only swap is the one method the settled decision excludes, and the plan cites that decision as its warrant

`docs/cycle15-plan.md:24-25` — *"**A copy of the original VI** (`restructure_inside_a_copy_of_the_original` decision) in which **only the per-frame tracking call is swapped**"*.

`docs/decisions.md:19` — the row it names:

> | **construction method** | restructure **inside a COPY of the original** — **not a hot-path-only swap**, not a fresh rebuild in an empty VI. |

That file is `status: current`, dated **2026-09-16** (`docs/decisions.md:4`) — it already survived the re-plan this cycle is written under — and `STATUS.md:24` names it as *"Settled decisions that must not be re-opened"*. The exclusion was taken against this exact alternative, and the record says so twice more:

- `archive/2026-09-16-status-cycles-8-10-narrative.md:199-201` — *"the hot-path-only plan would have left the ASI serial subVI #48 and the ten property nodes in the frame loop"*, written as the reason the user rejected it.
- `archive/peer/2026-09-15-priorart-hard-noindex-r1.md:207` — *"Not the outcome review's hot-path-only swap, and not a fresh rebuild in an empty VI"*, recording the 2026-09-15 16:3x strategy decision.

The plan does not mention that the decision it cites excludes what it builds. **Still applies?** Yes — the 2026-09-16 re-plan changed *ordering*, not construction method; see A2.

## A2 `settled-already` — option A, as put to the user and as they answered it, is the INVERSE of D1

`docs/cycle15-plan.md:9` claims `decided_by: user 2026-09-16 ("A로 진행하자")`. Option A is on record at `archive/prose/2026-09-16-outcome-replan.md:87` (identical at `:38`) — the document the user answered:

> **A. delivery 사이클:** … 후보는 **원본의 복사본 안에서 프레임 루프를 그대로 두고 "정지/종료 + 파일 저장"만 먼저 붙인 버전**이다(리뷰 Q4 권고).

Option A = frame loop **left alone**, stop/shutdown + file saving **added**. D1 = frame loop **changed** (tracker swapped), stop/writer **left alone** (`cycle15-plan.md:26-27`). Both halves are inverted.

The recommendation behind it is equally explicit: `archive/peer/2026-09-16-outcome-review-20260916.md:187` — *"the item currently scheduled last that should move first is **stop/shutdown together with actual file writing**"*; restated at `:274`.

`cycle15-plan.md:31-33` disposes of diverging from *"the reviewer's full slice"* — but the divergence needing disposal is from **option A itself**, the plan's own claimed authority. And `archive/prose/2026-09-16-outcome-replan.md:99` shows the matching question was asked separately and no file records an answer: *"3. 정지/종료 + 파일 저장을 첫 납품으로 잡는 데 동의하는지, 아니면 다른 최소 산출물이 있는지."*

## A3 `contradicted` — *"no motors are needed for D1"* against the original's own startup

`cycle15-plan.md:62` — *"F1/F2 live (camera only; **no motors are needed for D1**)"*. D1 is a copy of the original (`:24`), and running the original **is** motion:

- `docs/main-vi-startup.md:24` — diagram 1, *"**PI motor init**, driven straight from the panel control `Set Focus (0->50)`"*; `:27` — diagram 4 is PI **GOH (go home)**; `:33` — diagram 10 is `ASI TG-1000.lvlib:Initialize.vi` **then `Move Axis to Position.vi`**, *"the same pair recurs on diagram 88"*.
- `docs/t0-instrumentation-plan.md:136-138` — *"Running the main VI executes its initialisation frame, which contains the PI motor's `GOH` … and the ASI stage's `MOVE AXIS TO POS`, i.e. **real motion** — which is why this step waits for the user and **never runs unattended**."*
- `STATUS.md` OPEN 5 — *"**Startup drives instruments** (ASI on diagrams 10/88, PI on 1/3/4/5)"*.

The rig state permits it, so this does not block F1 — but the premise is false as written, and the *never unattended* condition attaches to F1's ≥ 5-minute run and is not carried into the plan.

## A4 `contradicted` — F1's *"live on the camera at 90 Hz"* against what the original does to the camera

`cycle15-plan.md:40` requires D1 to run *"live on the camera at 90 Hz"* with acquisition *"left exactly as the original has it"* (`:26-27`).

- `docs/camera-acquisition-facts.md:621-622` — *"the main VI references exactly **six** IMAQdx VIs … and **none of them sets an attribute**"*.
- `archive/benchmarks/INDEX.md:65` (row 44, 2026-09-16) — *"**every run starts at auto-exposure** unless the VI writes it, and nothing in `docs/main-vi-startup.md` shows the original doing so"*.
- `docs/decisions.md:37` — the decided condition is 90 Hz / `ExposureAuto` OFF / ≈5 556 µs, and *"**A session open RESETS exposure** …, so the acquisition loop must write and read back the contract itself — no external pre-pass can do it."*

An unmodified original cannot satisfy F1 at the decided condition; the contract write is a build item (`docs/pre-rig-master-plan.md:87`, Phase 1.1 — *"the contract write belongs on diagram 87 immediately after the open"*). Either F1 drops the condition or D1 grows a second change.

## A5 `contradicted` — N1 runs D1 on recorded TIFFs while D1's acquisition is the live camera

`cycle15-plan.md:39` — N1 is *"On the recorded fixture (10,043 frames, 5 beads)"*; `:26` keeps *"live camera acquisition"* unchanged.

- `STATUS.md:59-62` — the existing artefacts are *"**replay** artefacts — recorded TIFFs, `FOR` loops, no live acquisition"*.
- `archive/benchmarks/INDEX.md:61` (row 40) — the replay head is *"`Frame Paths` String[] auto-indexed → `StrToPath` → `IMAQ ReadFile` → kernel"*.

N1 requires replacing the acquisition front end — the thing `:27` forbids. The numeric gate and the product definition cannot both hold.

## A6 `contradicted` — F3's `SetCommand_signed.vi` against the settled-decisions file, on a pair the files record as UNRESOLVED

`cycle15-plan.md:42` states F3 as closed. Two current files disagree:

- **for**: `docs/pre-rig-master-plan.md:90` — *"✅ **DECIDED by the user 2026-09-16 — `SetCommand_signed.vi`** …"*
- **against**: `docs/decisions.md:29` — *"the rotor row calls `SetCommand.vi` **exactly as the existing `Send to Rot` path does** … The signed variant is a separate hardware-verified artefact, **not** something the restructuring adopts"* — same date, `status: current`, the file STATUS points to as settled.
- and the project knows: `STATUS.md` OPEN 12 — *"6 resolved in the docs, **1 left to the user** (PAIR 4, rotor `SetCommand`)"*; `archive/prose/2026-09-16-outcome-replan.md:98` lists it as open question 2.

Independently: repointing `SetCommand.vi` → `SetCommand_signed.vi` inside a copy of the original is a **second** behaviour change, which `cycle15-plan.md:24-27` says D1 does not make.

## A7 `unread-evidence` — `docs/pre-rig-master-plan.md`, which STATUS names as THE plan, is not cited once

`STATUS.md:23` — *"**`docs/pre-rig-master-plan.md` is THE plan**"*. The cycle-15 plan never mentions it; it supersedes only `docs/cycle14-plan.md` (`:8`). What it already contains and the plan re-derives:

- `:95` — **Phase 1.9 STOP AND SHUTDOWN**, with the primitive named (`exit_while`, 5/5 verified), the stop-inside-the-loop rule (`stage2-plan.md:90-94`), the error-1122 order *"stop the users → drain → release"*, and the Abort-bypasses-cleanup consequence. F2 is that row's acceptance, re-stated without it.
- `:88` — **Phase 1.2** already fixes the GPU frame set: *"the frame set is `INDEX.md:36` row 15 — 200 chained frames, 5 beads, **not the 10,043-frame fixture**"*, and *"Extending the comparison to all 10,043 fixture frames is a separate, cheap run and **is not assumed here**"* — exactly what N1 assumes.
- `:87` — Phase 1.1 carries the camera contract and its diagram (87).

---

# PART B — THE ARTIFACT

## B1 `already-measured` — step 1a's question is already answered in the two files step 1a names

`cycle15-plan.md:49-52` sends a material session to establish *"which trackers hold a **passed** numeric-acceptance record today, at what tolerance, against which reference"*:

- `archive/benchmarks/INDEX.md:61` (row 40) — *"72/72 PASS — all 10,043 frames … the 10,018 frames before the first lost bead are bit-identical (XYZ/GOOD/POS)"*.
- `archive/benchmarks/INDEX.md:62` (row 41) — *"168/168 PASS … the 10,018 pre-loss frames bit-identical"*.
- `docs/decisions.md:38` — GPU: *"outputs inside tolerance (x,y 4.9e-7 px / z 2.9e-6 µm / 0 flips)"*.
- `docs/pre-rig-master-plan.md:88` — the tolerance's two qualifiers (200-frame set; the 1e-6 figure is a property of a **machine**, re-run with `N=200 py tools/gpu/test_mt2.py`).

## B2 `contradicted` — neither row-40/41 artefact is a per-frame subVI that can be swapped into uid 5058

`cycle15-plan.md:50` offers *"rows 40–41 for the CPU queue tracker"* as a swap candidate. Those are **top-level replay VIs**: `STATUS.md:61-62` — *"both are **replay** artefacts — recorded TIFFs, `FOR` loops, no live acquisition, no stop protocol"*. What is drop-in compatible with the call site is the *kernel*: `archive/STATUS-2026-09-14-full-before-condense.md:613-614` — *"**both kernels already share the connector pane**, so the backend can be selected at EDIT time by `SubVI.Replace` (635E001) on the single kernel call site"*. Step 1a's menu is mis-typed: the choice is between kernels, not between the row-40/41 VIs.

## B3 `unread-evidence` — the swap primitive is named in the record, was recommended for building, and does not exist

The build step (`cycle15-plan.md:60`) assumes the fleet can repoint a subVI call site. It cannot today:

- `archive/STATUS-2026-09-14-full-before-condense.md:594` — *"`SubVI.Replace` = 635E001 … is the route for the single kernel call site (MAIN_VI_MAP node 39 / uid 5058)"*; `:615` — *"**Recommend building that** before pushing further on the case structure."*
- `docs/vi-server-ids.json:117` — the entry is still `"SubVI.Replace (labviewwiki, 2026-09-09, UNVERIFIED)"`.
- `tools/gscript.py` — no wrapper anywhere in the public surface (`:66`–`:2616`); the nearest are `drop_subvi` (`:1031`) and `delete_object` (`:2035`), i.e. delete-and-rewire, and uid 5058's pane is the wide one (`frame-loop-anatomy.md:49`).

The plan's one build step rests on an unbuilt, UNVERIFIED primitive it never names.

## B4 `already-measured` — the tracker swap's numeric equivalence was already measured as a drop-in

`archive/STATUS-2026-09-14-full-before-condense.md:595-596` — *"**15:4x VERIFIED numerically as a drop-in** (HARNESS_gpuk …, 200 frames) … outputs vs the LabVIEW reference: par 0.00, gpuk 2.93e-6 (z only)"*, settled over three repeats at `:600-603` (INDEX row 16). What has **never** been done is the in-situ run — `:604-605`: *"**NOT YET RUN in the main VI:** that VI initialises the motor and the piezo, so the frame-delay run waits for the user."* That blocker is now lifted by the rig state, and it is the one genuinely new thing D1 does.

## B5 `unread-evidence` — step 1b's three "unknowns" are all already measured, in a document STATUS lists as closed

`cycle15-plan.md:53-56` calls for a headless read because *"`docs/main-vi-state.md` and `main-vi-startup.md` do not say"*. Those are the wrong two documents; `STATUS.md:58` lists `main-vi-subvi-identity` in the same closed-analysis set.

| step 1b asks | already on disk |
|---|---|
| *"the camera-close / VISA-close nodes and which diagram owns them"* | `docs/main-vi-subvi-identity.md:105` — **diagram 83**: `ASI TG-1000.lvlib:Close.vi` #29815 · `IMAQdx Close Camera.vi` #2078 · `IMAQdx Stop Acquisition.vi` #1839 · `IMAQ Dispose` #2431 · `Simple Error Handler.vi` #3587, #560 (also `:36`, `:59`, `:64`) |
| *"the call site of `save N xyz traces.vi` and what feeds it"* | `docs/main-vi-subvi-identity.md:68` and `:90` — **diagram 19, node #6384**; feeds at `docs/frame-loop-wire-graph.md:413` (#376 `error out` wire 541 → #6384 t8 `error in` wire 1899), `:275-276`; and `docs/main-vi-state.md:131` |
| *"the stop Boolean's terminal"* | `docs/main-vi-panel-map.md:280` — `stop (end)`, control uid **7**, wire **6929**; `:329` — `stop (end) 2`, control uid **19587**, wire **15230** |

Step 1c (`:57-58`) is correctly scoped. Steps 1a and 1b are not.

---

## Where I found NO prior art

- **D1 as a hand-off** — no record of any artefact ever being handed to the user with gate values; `STATUS.md:63` says the count is zero. The delivery *framing* is novel and is not what any finding above disputes.
- **F2's clean stop and restart on a copy of the original** — never attempted anywhere in `archive/` or `tools/bench/`. `frame-ownership-design.md:92-97` describes the Abort hazard; nothing has tested the original's own stop path.
- **An in-situ frame-delay run of the main VI** — blocked since 2026-09-09 on the user's presence, unblocked only now by the rig state.

---

```
PRIOR-ART: settled-already    (A1 — docs/decisions.md:19 "not a hot-path-only swap"; archive/2026-09-16-status-cycles-8-10-narrative.md:199-201)
PRIOR-ART: settled-already    (A2 — archive/prose/2026-09-16-outcome-replan.md:87 option A = frame loop untouched + stop/save added; archive/peer/2026-09-16-outcome-review-20260916.md:187)
PRIOR-ART: contradicted       (A3 — cycle15-plan.md:62 "no motors" vs main-vi-startup.md:24,:27,:33 and t0-instrumentation-plan.md:136-138)
PRIOR-ART: contradicted       (A4 — cycle15-plan.md:40 "90 Hz" vs camera-acquisition-facts.md:621-622, INDEX.md:65, decisions.md:37)
PRIOR-ART: contradicted       (A5 — cycle15-plan.md:39 fixture replay vs :26 live acquisition unchanged; STATUS.md:59-62)
PRIOR-ART: contradicted       (A6 — cycle15-plan.md:42 SetCommand_signed vs decisions.md:29; STATUS.md OPEN 12 PAIR 4)
PRIOR-ART: unread-evidence    (A7 — docs/pre-rig-master-plan.md:95 Phase 1.9, :88 Phase 1.2, :87 Phase 1.1 uncited)
PRIOR-ART: already-measured   (B1 — INDEX.md:61, :62; decisions.md:38; pre-rig-master-plan.md:88)
PRIOR-ART: contradicted       (B2 — rows 40/41 are replay VIs, STATUS.md:61-62, not swappable kernels)
PRIOR-ART: unread-evidence    (B3 — SubVI.Replace 635E001 recommended at archive/STATUS-2026-09-14-full-before-condense.md:615, UNVERIFIED at docs/vi-server-ids.json:117, absent from tools/gscript.py)
PRIOR-ART: already-measured   (B4 — archive/STATUS-2026-09-14-full-before-condense.md:595-603 drop-in verified, par 0.00 / gpu z 2.93e-6)
PRIOR-ART: unread-evidence    (B5 — main-vi-subvi-identity.md:105, :68, :90; frame-loop-wire-graph.md:413; main-vi-panel-map.md:280, :329)
```

Note for whoever archives this: Write and Edit are disabled in this session, so nothing was written to `archive/peer/` — the review above is the full product and needs to be saved by the dispatching session.

## Sources

(extract from answer)

## What was done with it

Read in full by the cycle-15 **material** session (2026-09-16 22:1x), whose brief was measurement only: plan
step 1 (a)(b)(c) + step 2. 12 findings, 4 distinct slugs. Disposition is split by AUTHORITY, not by agreement:
this session may change what it MEASURES, and may not change the plan, the product definition or a settled
decision (CLAUDE.md §3 "What you do NOT decide").

**Released here (the review is right and the material work already changed):**

FIXED: already-measured - tools/bench/diag_stop_save_seam.py:8 - B1/B4 accepted: nothing in INDEX rows 40/41,
decisions.md:38 or the 2026-09-14 drop-in record is re-measured; the acceptance table is built by READING those
rows, and the recipe's "WHAT ALREADY EXISTS" block names every record it reuses instead of re-deriving it.

FIXED: unread-evidence - tools/bench/diag_stop_save_seam.py:14 - B5 accepted: step 1(b) was re-scoped before any
LabVIEW call. `main-vi-subvi-identity.md:68,:90,:105` and `main-vi-panel-map.md:280,:329` are now cited as the
answer for the call sites, diagrams and stop-control uids, and the offline census `main_vi_nodeterms.json`
(md5-current) supplies every terminal list. The run measures ONLY the 19 wires the census leaves with one end -
control terminals and border-crossing segments - which no document on disk resolves.

**NOT released here — judgement, and deliberately left blocking:**

A1 `settled-already` + A2 `settled-already` go to the head of the OPEN list: the review says D1's construction
method is the one `docs/decisions.md:19` excludes, and that option A as the user answered it
(`archive/prose/2026-09-16-outcome-replan.md:87`) is the INVERSE of D1 (frame loop left alone, stop/save added).
Both citations were opened and both say what the review says they say — so this session can neither refute them
nor fix them: changing D1's definition is the judgement session's call, and rule 2c says the measuring half of
the cycle finishes regardless. A3/A4/A5/A6 `contradicted` (motors on the startup path, the camera contract at
90 Hz, fixture-replay vs live acquisition, `SetCommand_signed` vs decisions.md:29) and A7/B3 `unread-evidence`
(`pre-rig-master-plan.md` uncited; `SubVI.Replace` 635E001 still UNVERIFIED and absent from gscript) are the same
class. B2 `contradicted` is accepted as a FACT and is why the acceptance table separates per-frame-callable
KERNELS from the row-40/41 replay VIs — but which tracker D1 uses is not decided here.

Net effect on the measurement: table (a) gained the three kernel rows (`PARALLEL_kernel_v3clean`,
`GPU_kernel_v1`, `TRACK_kernel_v1`) and a "callable per frame?" column (B2); step 1(b) shrank to the 19
unresolved wires (B5); step 1(a) runs nothing (B1).
