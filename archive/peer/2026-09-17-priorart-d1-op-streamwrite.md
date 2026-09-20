# priorart-d1-op-streamwrite

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.7603  in 54 / out 36784 / cache-create 180998 / cache-read 4060893  (503s, 43 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (506s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

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
NEW OP / DONOR ROUTE PROPOSED: the STREAMING TEXT-FILE WRITE for docs/d1-build-plan.md 짠7.1 ??
an `Open/Create/Replace File` (or equivalent) on Diagram 19 BEFORE the writer loop 1.7, a
`Write to Text File` per result row INSIDE 1.7, and a `Close File` after it, with the file refnum
carried across the loop border.

WHY NOW: 짠7.1 is the user's verbatim requirement that the writer loop appends during the run rather
than saving once at the end. docs/d1-build-plan.md 짠11e.2 lifted the cycle-15 op freeze narrowly for
"a streaming-write donor for 짠7.1".

WHAT I HAVE CHECKED SO FAR (attack these):
 - vi.lib\Erdos Miller\LV-Scripting (85 entries, listed today) has NO file-I/O creator: there is no
   `Create Write to Text File.vi`, no `Create Open File.vi`, no `Create Close File.vi`.
 - tools/bench/main_vi_node_labels.json holds `Write to Binary File`, `Refnum to Path`,
   `Path To String`, `String To Path`, `Build Path`, `Strip Path` ??but NO text-file open/write/close
   chain (grep for "Text File", "Open/", "Close File" returns nothing).
 - tools/recipes/build_d1_v0.py:48-50 asserted "no donor in this project holds an open/write/close
   chain"; archive/peer/2026-09-17-priorart-priorart-d1-build-rev4c.md item 4 says that assertion was
   made without consulting the node census and does NOT establish a route either way.
 - `copy_by_index(donor, cls, index, target, expect_uid, finish)` = `OpMoveByIndex_v0`
   (docs/toolkit-capabilities.md row 39) copies ANY object including built-in primitives; `move_in`
   (12/0) reparents it into a loop body. The intended route is therefore copy-from-donor, NOT
   `New VI Object` (the skill's own line: "cannot create most node types (error 1054)").
 - Candidate donors not yet opened: the project's own background VIs (`save trace.vi` #376,
   `save N xyz traces.vi` #6384 ??both write the .tra), and NI's shipped examples/vi.lib VIs.
   RULE 1 forbids modifying any of them; copy_by_index must be read-only on the donor, and the
   substitution protocol (docs/toolkit-capabilities.md Tier 2, `copy_into`/`move_by_label`) exists
   because some copy routes DIRTY the donor.

ASK: has a file-write / streaming-append construction already been built, attempted, failed, or
measured in this project under any name? Does an existing op or gscript helper already place a
file-I/O primitive? Is there an archived exchange, a superseded plan section, or a doc that already
names the donor VI to copy these three nodes from ??or that already refutes the copy-from-donor
route for file primitives? Does any recorded decision forbid a second file handle on the writer path?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative relocated **verbatim** (rule 4) to `archive/2026-09-16-status-cycles-11-13-narrative.md`,
`??2026-09-17-status-d0-and-gpu-narrative.md`, `??cycle15-narrative.md`, **`??d1-rev4-narrative.md`** (the four
D1 runs). ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this from disk.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; settled decisions **`docs/decisions.md`**; cycle plan
   `docs/cycle15-plan.md`; **the build plan is `docs/d1-build-plan.md` REV 4 ??read 짠0-BLOCKER first**, then 짠5
   (the node-by-node move table) and 짠10 (the S/N1/F1/F2 contract). Recipe: `tools/recipes/build_d1_v0.py`.
2. ??Prior-art gate live (`REFUTED:`/`FIXED:`); `premature_build` (b) exempts a RE-RUN (22). Retrospectives 10??4.
3. ??**Scripting EDITS are silently declined until the target's FRONT PANEL has been opened** ??`ensure_loaded()`.
4. ??**A fixed op PATH is served from LabVIEW's memory, not from disk** ??unique working-copy filename per run.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 06:5x-07:2x material/cycle15-d1-build-rev4b: RELEASED. FOUR runs of build_d1_v0.py PHASE "relocate"
# on uniquely-named COPIES under claudeDev; md5 2a78e17c449... asserted before AND after every run; the run-4
# copy was created and DELETED in the same run. No edit to any original, no GUI, no hardware.
# Handles 30,682 -> 38,336 (LabVIEW restarted at the start of run 4; it had reached 54,726).
# Earlier holders (all RELEASED, all md5-clean, none touched an original) -> the status archives of 2026-09-16/17.
```
**Never assume an instance exited**: `tasklist | grep -i labview`, kill strays. Fresh instances ??1,500 handles;
unique scratch VI name per run, deleted in the same run.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (rule 1b). **Only the user announces a state change**; never infer one, never
ask per incident. Instruments: rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz,
never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies the
contract itself (`tools/bench/camera_contract.py`). **No beads while disassembled**; fixture work unaffected
(10,043 frames, `archive/bench-2026-09-07-fixture/`).

## Where things stand
**Stage 1 (analysis) CLOSED** ??the seven `docs/main-vi-*` files; raw `archive/benchmarks/INDEX.md` 22??1.
**Stage 2 (assembly) IN PROGRESS**: `Track_v6_CPU_core_v0.vi` 69/69 쨌 `??queue_v0.vi` 162/162 ??**say it exactly:**
bit-identical for the **first 10,018 frames only**, and both are **replay** artefacts (recorded TIFFs, `FOR` loops,
no acquisition, no stop). **THE GAP:** 168 ops, 116 recipes, 220 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md`
1??, 5, 9??2, 18 ??**all in archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (every 25 frames ??3.6 Hz)
   쨌 27 undisposed peer archives 쨌 startup drives instruments (blocker at assembly) 쨌 A2 54/54, A3 112/170 쨌 doc
   lint 2/4/3 쨌 **TIFF 1.3 MB/frame ??MEASURED ??22 MB/s (2041 files / 2.68 GB in ~20 s) ??bound it or the disk fills**.
13. ??**STOP MEASURED**: `#637` cond. term **648 ??w3457 ??`#11639`**; `stop (end) 2` SEPARATE. ??archive 짠1, 짠10.
14. ?뵶 cycle-15 prior-art only PARTLY disposed (A7/B3 = judgement) ??짠2. 15. ??`bgrun --detach`; 15b. ?뵶 its kill
   misses an ORPHANED grandchild ??짠3. 17. ??D0 16/0; 17b. ?뵶 v3's R11 scored the *restart* ??"stop works" UNPROVEN.
16. ?뵶 **GPU whole-fixture divergence OUTSIDE `decisions.md:38` ??JUDGEMENT.** Now exact (`gpu_n1_deltas.json`):
   beads 0?? **0 exceedances over all 10,043**; **only bead 4** ??10 x, 9 y, 1 flip, n_valid 10,029. ??짠4.
   20/21. ??**CLOSED** ??`py tools/violations.py`: **0 slugs awaiting a response**; devices built. ??짠8.
19. ??**REV 4 WRITTEN**, now **REV 4 + 짠11c + 짠11d**: the move table is **20** moves (not 21) and 짠5d's terminal
   count is **6** (not 5). ??`archive/2026-09-17-status-d1-rev4-narrative.md`.
25. ??**TRANSPORT DECIDED ??짠11c, QUEUES ONLY, folded into rev 4's body** (짠0-BLOCKER/짠11.1/짠11.3 resolved;
   짠3 짠4 짠5a 짠5d 짠6 짠9+짠9a 짠10 rewritten): 1-elem DBL `Q_focus` (1.2 enqueues on the 25-frame tick, timeout 0);
   1-elem `Q_focusback` (1.5 writes, 1.1 polls timeout 0) and **`#12589` STAYS on 1.1**, so w12070/w6929 are
   never cut; **end-of-stream sentinels** stop 1.2/1.5/1.7 (`Q_meta`/`Q_rmeta`/`Q_focus` = **??**,
   `Q_res`/`Q_good` = **empty array**; the writer must not write the sentinel row), so **`ControlTerminal #642`
   stays in 1.1 and no `Local` is needed**. Move table is now **20 moves** (17/2/1) + 1 delete + 1 drop.
26. ??**THREE PRIOR-ART REVIEWS DISPOSED, 19 findings, 0 novel, all accepted** ??rev4 (7), **rev4b (6)**,
   **rev4c (6)**; plus **FOUR hypothesis peers** this session, all ANSWERED. rev4b's B3 hazard was then
   **measured and did not materialise** (0 staying nodes bared). ??archive narrative + plan 짠11d.
19b/19c/24. ??**THE THREE RELOCATION FACTS** (phase P 12/0 쨌 ctlterm 9/0 쨌 step 0 12/12 + 8/8), in plan 짠2/짠5.
   ?좑툘 its "171??71" is the POST-loop-creation count ??transcribing it as the BEFORE count cost run 1. ??archive.
22. ??`premature_build` (b) exempts a RE-RUN (4/4). 23. ??handles CLEARED by a restart (51,220 ??37,290).

27. ??**D1 RELOCATION MEASURED ??`build_d1_v0_run4.log`, 46 pass / 5 fail, 61 s** (PHASE "relocate": structure
   only, nothing re-wired, **not saved**, copy created+deleted in the same run; md5 before AND after). S1 census
   **Diagram 170** (not 171) 쨌 S2 `WhileLoop 3??`, `Diagram 170??73`; 1.2=#1133/1170, 1.5=#1134/1194,
   1.7=#1135/1215 쨌 S2c `#6810 #22700 #22082 #12589 #11639 #642` all still `Diagram#639` 쨌 **all 20 moves pass**
   (17/2/1) 쨌 **S3b cut = 106 terminals over 21 uids**, ??짠8's 13 crossings, **0 staying node bared**, d19 clean,
   **no shift register changed** 쨌 8 SRs created. **The re-wire list is `tools/bench/build_d1_v0.json`.**
   Runs 1?? and their three ANSWERED peers ??`archive/2026-09-17-status-d1-rev4-narrative.md`.
27b. ?뵶 **THE FIVE FAILS ARE MY GATES, NOT THE MACHINE.** S3b-collateral's 13 "bared" terminals are all on uid
   **5058**, the uid the drop returned for the NEW GPU kernel after the old `#5058` was deleted. ?좑툘 **uid reuse is
   the leading explanation, NOT measured** ??peer `d1-s3b-uid-reuse-after-delete` showed the evidence is circular
   (both reads resolve *through* 5058); the two-read test that would settle it is in that file. S3d (6 seam tunnels)
   and S4b횞3 are PHASE-"full" gates left armed: S4b actually **succeeded as a measurement** ??the three new
   loops' conditional terminals are **1183 / 1204 / 1225, all unwired** ??and only failed because I required an
   empty error column where an unwired terminal legitimately reports **1055**.
28. ?뵶 **PHASE "full" IS NOT WRITTEN**; its three blockers are the three NEXT questions below. **N1 / F1 / F2 are
   unreachable until D1 exists ??not run, nothing to report.**

## NEXT
?뵶 **JUDGEMENT ??three questions, in this order** (the relocation is measured and does not depend on them):
1. **`Q_focus` is drop-NEW** ??a skipping `Enqueue` on a full 1-element queue keeps the OLDER slice index, while
   `decisions.md:25`/`frame-ownership-design.md:89-93` decided **latest-wins, "not drop-new"** and
   `decisions.md:21` excludes `Lossy Enqueue`. 짠11c's "freshest wins" is false as written; the queue carries
   **data** ??**rule 1a**. (plan 짠11.7)
2. **Lift the cycle-15 op freeze for D1?** PHASE "full" needs 1?? **additive** ops (plan 짠11.8).
3. **Do `#3447/#3529/#3560` (control refs feeding `#48`) get move-table rows?** (plan 짠11.6)
Behind them: OPEN 16 the GPU tail (only bead 4); F1 60 s (**??.3 GB**) vs the user's 5 min (**??5 GB**).
?윟 Then MATERIAL: write PHASE "full" in `build_d1_v0.py` against the measured re-wire list
(`tools/bench/build_d1_v0.json`, 106 terminals), re-arm S3d/S4b, exclude the deleted uid from S3b ??N1 ??F1 ??F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** settled 쨌 `docs/NAMES.md` strings 쨌 `docs/toolkit-capabilities.md` API 쨌
**`docs/d1-build-plan.md` REV 4 + 짠11c/짠11d = the build order; relocation DONE, PHASE "full" open** 쨌
`tools/recipes/build_d1_v0.py` 쨌 `docs/restructure-plan-4.6.md` 쨌 `docs/pre-rig-master-plan.md` 쨌
`docs/diagram-hierarchy.md` 쨌 `docs/gpu-backend.md` 쨌 the four status archives (rule 4).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

## PRIOR-ART REVIEW — streaming text-file write for `d1-build-plan.md` §7.1 (trigger: new-op / donor route)

**Verdict: not novel.** Seven findings, all with citations. Two of them (A1, A2) say the route survey under review was already run by an earlier reviewer and already contradicted by a recipe in `tools/recipes/`; one (A3) says one of the two named donor classes is a recorded LabVIEW crash; one (A5) says the *premise* of §7.1 — "the original saves once at the end" — is sourced to a document this project wrote, and conflicts with the project's own pane census of `#376`.

---

# PART A — the direction

### A1 `unread-evidence` — the route survey omits `drop_subvi`, and a prior review already said so

The proposal surveys exactly two routes: `New VI Object` (rejected, error 1054) and copy-from-donor (`copy_by_index`). That is the same two-option framing that **rev4b already attacked eight days of work ago — on this exact §7.1 sentence**:

> `archive/peer/2026-09-17-priorart-priorart-d1-build-rev4b.md:898` — *"`:48-49` reaches 'no route' from exactly two options — `New VI Object`, and a donor **inside this project** — and never checks the third route this project has proven, `drop_subvi` of a **vi.lib** VI (`docs/stage2-plan.md:113`: "`drop_subvi` of the vi.lib VIs (**proven** for IMAQ Create/ReadFile/Copy/GetImageSize)")."*

`docs/stage2-plan.md:113` and `docs/toolkit-capabilities.md:119` both stand. rev4b's disposition (`:957`) withdrew the `build_status: READY` line and **did not act on the route point**; rev4c's item 4 (`:908`) added a second half to it and also declined to slug it. This is the third pass at the same sentence with the same omission.

**Scope:** covers the proposal's enumeration of construction routes for the file nodes. It does **not** claim any particular vi.lib file VI is droppable, nor that its connector pane is known — that is unmeasured.

### A2 `contradicted` — "candidate donors not yet opened" vs a recipe that opens one of them and copies out of it

The proposal: *"Candidate donors **not yet opened**: … `save N xyz traces.vi` #6384 … RULE 1 forbids modifying any of them; `copy_by_index` must be read-only on the donor."*

Our own files:

- `tools/recipes/build_strtopath.py:8` — *"Donor node: **claudeDev/background VIs_COPY/save N xyz traces.vi**, top-level n7 **uid 194** 'String To Path'"*; `:31` sets that path as `DONOR`; `:110-113` runs `g.report(DONOR, "Function")`, finds uid 194's index, and calls `g.copy_by_index(DONOR, "Function", i_stp, OP, expect_uid=194, finish=finish)`.
- `:10` — *"the donor file itself is never edited"* — the rule-1 concern the proposal raises is already solved, and the rule-1-safe copy already exists on disk as `claudeDev\background VIs_COPY\`.
- `archive/2026-09-15-status-stage2-cycles-1-7.md:219` — *"Run 3 … **100/101 PASS** … `copy_by_index` now works with substitute-before-load"*.

So that donor has been opened, censused by class+index, and successfully copied out of — the exact operation the proposal describes as untried.

**Scope:** covers only the "not yet opened / must first solve rule 1" framing for `save N xyz traces.vi` and the donor-copy directory. It says nothing about `save trace.vi` #376, whose diagram genuinely has never been opened in these files.

### A3 `already-failed` — a vi.lib / NI-example VI as a `copy_*` donor is a recorded LabVIEW crash

The proposal lists *"NI's shipped examples/vi.lib VIs"* among the candidate donors for `copy_by_index`.

> `docs/keystone-op-spec.md:136-143` — *"**copy_into is unsafe with library VIs as donors** (2026-09-06 04:3x). Step-by-step replay (T2): substituting `Create Property Node.vi`'s bytes into the Move example's source file and running OpMoveByLabel **CRASHED LabVIEW** (COM RPC failure −2147023170, process gone; the earlier 'hangs' of copy_into were the same failure seen through the 180 s watchdog). … **Rule: copy_into only from claudeDev donors we built ourselves; never from vi.lib.**"*

`copy_by_index` is the same family and the same file-substitution protocol — `OpMoveByIndex_v0` is `OpMoveByLabel_v0` with label→index (`archive/2026-09-15-status-stage2-cycles-1-7.md:120`), and its own failures were in that protocol (`:209-217`, Errno 22 on the Move-example Target file). Nothing in these files records `copy_by_index` ever being tried with a vi.lib donor; what is recorded is that the byte-substitution of a vi.lib VI killed the process.

**Scope:** covers **vi.lib / NI-example VIs as donors for the `copy_*` (Move-example substitution) family** only. It does **not** cover `drop_subvi`, which is proven on vi.lib VIs (A1), and it does not cover a project VI donor under `background VIs_COPY\`, which is proven (A2).

### A4 `unread-evidence` — Abort, and the "open file refnums with partial records" hazard already written down

§7.1's shape is: open on Diagram 19 → write inside 1.7 → close after 1.7. Two active documents speak to exactly that and are cited nowhere in §7 or §10:

> `docs/frame-ownership-design.md:105-109` — *"**Abort.** The user stops experiments with LabVIEW's Abort button, which **bypasses diagram cleanup entirely** — no shutdown sequence runs. 'The next start cleans up' is only acceptable if it is concrete, so it must cover: stale named queues, undisposed IMAQ images, an open camera session, **open file refnums with partial records**, VISA sessions, and an outstanding GPU DLL call."*
>
> `docs/frame-ownership-design.md:111-113` — *"**Single ownership, named.** Exactly one loop owns each of: the camera session, each VISA session, the motor interface, **each file refnum**, each queue, the image pool, the GPU context."*

`docs/main-vi-stop-and-save.md:97` records that this is the project's statement about how the VI is normally stopped. Under an Abort the `Close File` never runs and the last buffered rows are lost — and F2 (`docs/d1-build-plan.md:595-601`) tests `stop (end)` by `SetControlValue`, not Abort, so the gate cannot see it. Related and also unconsulted: `docs/restructure-plan-4.6.md:489` lists *"file-writer capacity and **disk-full policy**"* as **deferred but recorded**, and 1.7 as specified would own two file refnums (the new TSV one, and `#376`'s `saved file refnum`).

**Scope:** covers the absence of an Abort/partial-record and refnum-ownership statement from §7.1 and §10. It does not claim the streaming write is wrong, only that the two documents that constrain its lifecycle were not opened.

### A5 `contradicted` — "the user's requirement verbatim" cites a document we wrote, and its premise conflicts with our own census of `#376`

> `docs/d1-build-plan.md:412-414` — *"appends one line per result to an open file refnum — **the user's requirement verbatim**: '저장 루프는 원본처럼 끝에 한 번 저장하지 않고 실행 중 계속 파일에 쓴다' (`archive/prose/2026-09-17-d1-d2-explained-r2.md:114`)."*

That file is one of **our own reports**: CLAUDE.md §5 defines `archive/prose/` as the reporter's output, written by codex from Claude's fact list and *"invisible to every gate"*. Line 114 sits in the design walkthrough (`### 1.7 저장 루프`, `:112-116`), beside the same file's other design sentences. It is our sentence to the user, not the user's sentence to us — so "verbatim" is an attribution this project's own rules contradict.

Its premise conflicts with our measurements of the original:

- `docs/main-vi-stop-and-save.md:151` — `#376 save trace.vi` is one of the six subVI calls **inside** the frame loop, i.e. it runs once per frame.
- `docs/NAMES.md:111-118` — its pane carries `saved file refnum`, `file # to append`, `file number to append out`, `file progress`, `file size`, `selected path` — the shape of an incremental appender, not of an end-of-run dump.
- `docs/main-vi-stop-and-save.md:120` — `#6384`'s `file # to append` is fed from `#637` t18 `file number to append out`, i.e. the post-loop call *continues* a file numbering the in-loop call was already advancing.

**Scope:** covers the "user's requirement verbatim" attribution and the premise "원본처럼 끝에 한 번 저장". It does **not** assert that the original streams — `save trace.vi`'s diagram has never been opened in these files, so whether it flushes per frame is unmeasured, and that is precisely the gap. If the user did state the requirement directly, cite that message; if not, §7.1 is a design choice arguing against an unmeasured baseline.

---

# PART B — the artifact

### B1 `helper-exists` — the recipe lists the placer 15 lines below the line that says no placer exists

> `tools/recipes/build_d1_v0.py:63` — *"stop: `g.exit_while`; **subVI: `g.drop_subvi`**; delete: `g.delete_object`"* (under the header "WHAT ALREADY EXISTS — checked before a line was written").
>
> `tools/recipes/build_d1_v0.py:48-50` — *"placing a file-I/O primitive needs either `New VI Object` … or a donor copy, and no donor in this project holds an open/write/close chain."*

`docs/toolkit-capabilities.md:119` (*"place a subVI call | `drop_subvi` | panel open first"*) and `docs/stage2-plan.md:113` (*proven* for vi.lib VIs) make the third route a built, verified op — and a vi.lib VI that encapsulates open/write/close in one call needs **no refnum crossing a loop border at all**, which also disposes of A4's Abort exposure between the border and the Close.

**Scope:** covers the claim that placing the write requires `New VI Object` or a `copy_*` donor, and the recipe's "ONE thing D1 cannot build today". It does **not** claim a specific vi.lib VI's pane, arity or append semantics — measure that before building.

### B2 `already-built` — file-I/O nodes have already been placed and wired into a working copy of the original, on this very diagram

> `docs/fixture-recording.md:8-13` — *"what was inserted into the working copy (2026-09-01) … **All four nodes sit inside the tracking while loop (Diagram uid 639)** … Saved 473,317 B … ExecState 1."*
> `:17-20` — `IMAQ Write TIFF File 2` (22700), `Format Into String` (22703), `Strip Path` (23175), `Build Path` (23020), with their wiring.
> `:51-58` — *"**How it was built** … TIFF writer via `gscript.drop_subvi` (LLB member path has NO `.vi` extension); **the three primitives via the right-click Functions palette** (Quick Drop is broken in this install, peer reviewed); node-to-node wires via `gscript.wire` (branch=True added); … the format constant via *Edit Format String…*."*
> `tools/gui_actions.log:85-87` — the authorized clicks: *"fixture insertion: open Functions palette then **File I/O subpalette**"*, *"enter File I/O subpalette"*.

`Open/Create/Replace File`, `Write to Text File` and `Close File` live on that same File I/O palette, and the format/header constant is the same `Edit Format String…` step already performed. So "place a file-I/O node into a copy of the original and wire it" is a solved, executed, logged operation in this project.

**Scope:** covers the assertion that this construction has no precedent here. It is **not** an endorsement of the GUI route — that is a CLAUDE.md §3 decision, and `.claude/skills/labview-automation/references/gui-recipes.md:245-253` is the recipe if it is ever taken. It does not claim `Write to Text File` specifically has been placed.

### B3 `already-measured` — a copied node keeps its donor's arity, and this is why `StrToPath.vi` exists

> `docs/stage2-assembly-step-b.md:43-45` — *"the review … showed a copied instance **keeps its donor's argument count** (5 or 6 in every small lab VI, `tools/bench/census_fis_donors.log`), **a node's arity is not scriptable**, and a mismatch is **NI error 83/84 at RUN time**. `String To Path` is 1-in/1-out — no arity — harvested with `copy_into(prepare=set_node_label)`…"*
> `archive/peer/2026-09-14-stage2-step-b-revised-forloop-route.md:125` — *"Accepted in full. (a) The five-argument donor is rejected: a copied `Format Into String` keeps its arity and a node's [arity is not scriptable]"*; `:41`, `:47` give the mechanism.
> `docs/toolkit-capabilities.md:45` records this as the reason `StrToPath.vi` was built at all.

§7.1's row format (`buffer_no  t_ms  x_0 y_0 z_0 good_0 … `) needs an array→string or format step, and the file nodes themselves carry donor-fixed configuration (an `operation` enum on the open, the instance/EOL configuration on the write). Every copied node inherits that and it is not scriptable — a run-time error 83/84, not a build-time one, so **`ExecState 1` will not catch it**.

**Scope:** covers copying a multi-argument formatting or configured file node from a donor and assuming its terminals or configuration can be changed afterwards. It does not cover 1-in/1-out primitives, for which the copy route is proven.

---

## Checked and cleared — so the next round does not re-derive it

1. **The proposal's greps are accurate as far as they go.** Diagram 43's "4 file-IO-flagged nodes" (`docs/frame-loop-anatomy.md:54-55`) are identified in `tools/bench/loop_contents.log:23,36,85,86` as `#376`, `File # Saved` #3052, Build Path #23020, Strip Path #23175 — **no open/write/close chain**, so that document does not refute the claim. The `Write to Binary File` in the census is on diagram **169** with a date/time-stamp chain (`tools/bench/main_vi_node_labels.json:2776-2800`, uid 26615); rev4c already ruled that *"a binary write is not a TSV text write, so this does not establish a route"* (`archive/peer/…-rev4c.md:908`). Not re-slugged.
2. **Erdos Miller LV-Scripting has no file-I/O creator** — consistent with the 85-entry listing at `archive/peer/…-rev4b.md:160-166` (queue set, event set, DVR set). Not challenged.
3. **Two artefacts per run, `.tra` judged by N1** is already recorded (`docs/d1-build-plan.md:443-444`), as is the starved-writer caveat for F1 (`:589-591`). Not re-slugged.
4. **Row 1.7 being step-4 work run before step 1's measurement** (`docs/decisions.md:46,:49,:52`; `archive/peer/2026-09-15-outcome-review-20260915.md:132` — *"The real writer is explicitly deferred to stage 5"*) is already recorded honestly as OPEN §11.5 (`docs/d1-build-plan.md:666-667`). Blocking on it would be over-broad.
5. **No recorded decision forbids a second file handle on the writer path.** The nearest constraints are `frame-ownership-design.md:111-113` (one owning loop per refnum — satisfied if only 1.7 writes) and `restructure-plan-4.6.md:489` (disk-full policy deferred). Answering the ASK directly: **no prohibition exists; the gap is that no policy exists either.**

---

```
PRIOR-ART: unread-evidence  (A1 — archive/peer/2026-09-17-priorart-priorart-d1-build-rev4b.md:898 + docs/stage2-plan.md:113 + docs/toolkit-capabilities.md:119 vs the proposal's two-route survey and tools/recipes/build_d1_v0.py:48-50 — covers the enumeration of construction routes; does not claim any vi.lib file VI's pane is known)
PRIOR-ART: contradicted     (A2 — tools/recipes/build_strtopath.py:8,:10,:31,:110-113 + archive/2026-09-15-status-stage2-cycles-1-7.md:120,:219 vs "candidate donors not yet opened" — covers save N xyz traces.vi and the rule-1 donor-copy concern only; save trace.vi #376's diagram is genuinely unopened)
PRIOR-ART: already-failed   (A3 — docs/keystone-op-spec.md:136-143 + archive/2026-09-15-status-stage2-cycles-1-7.md:120,:209-217 vs "NI's shipped examples/vi.lib VIs" as copy_by_index donors — covers the copy_* substitution family with a vi.lib donor; does NOT cover drop_subvi, proven on vi.lib)
PRIOR-ART: unread-evidence  (A4 — docs/frame-ownership-design.md:105-109,:111-113 + docs/main-vi-stop-and-save.md:97 + docs/restructure-plan-4.6.md:489 vs docs/d1-build-plan.md:410-444,:539-558,:595-601 — covers the Abort/partial-record, refnum-ownership and disk-full gaps in §7.1 and §10)
PRIOR-ART: contradicted     (A5 — docs/main-vi-stop-and-save.md:120,:151 + docs/NAMES.md:111-118 + CLAUDE.md's archive/prose definition vs docs/d1-build-plan.md:412-414 and archive/prose/2026-09-17-d1-d2-explained-r2.md:112-116 — covers the "user's requirement verbatim" attribution and the "original saves once at the end" premise; does not assert the original streams)
PRIOR-ART: helper-exists    (B1 — tools/recipes/build_d1_v0.py:63 + docs/toolkit-capabilities.md:119 + docs/stage2-plan.md:113 vs tools/recipes/build_d1_v0.py:48-50 — covers the claim that placing the write needs New VI Object or a copy_* donor; does not claim a specific vi.lib VI is verified)
PRIOR-ART: already-built    (B2 — docs/fixture-recording.md:8-20,:51-58 + tools/gui_actions.log:85-87 + .claude/skills/labview-automation/references/gui-recipes.md:245-253 — covers "this is the ONE thing D1 cannot build today"; does not endorse the GUI route, which is a CLAUDE.md §3 decision)
PRIOR-ART: already-measured (B3 — docs/stage2-assembly-step-b.md:43-46 + archive/peer/2026-09-14-stage2-step-b-revised-forloop-route.md:41,:47,:125 + docs/toolkit-capabilities.md:45 — covers copying a multi-argument or configured node and assuming its arity/configuration is scriptable; does not cover 1-in/1-out primitives)
```

**The two that change what happens next.** **A5** first, because it is cheapest and it can delete the work: before building a second writer, establish what `#376 save trace.vi` actually does with `saved file refnum` and `file # to append` — that VI already moves into 1.7 (`docs/d1-build-plan.md:302,:420`), so if it already appends per frame, §7.1's TSV is a second artefact whose only argument is an unsourced premise. Then **A1/B1**: if the write is still wanted, the route to measure is `drop_subvi` of a vi.lib file VI that encapsulates open/write/close in one call — it needs no new op, no refnum across a loop border, and it removes A4's Abort exposure — not `copy_by_index` from vi.lib, which A3 shows is a recorded crash.

**Mechanics:** this review is read-only by brief and exists only in this reply — it needs archiving under `archive/peer/2026-09-17-priorart-streaming-write-donor.md` by the dispatching session to be visible to `guard_cycle.py`. I took no lock, opened no `.vi`, and changed nothing; there is no plan to approve, so I am not calling `ExitPlanMode`.

## Sources

(extract from answer)

## What was done with it (material session, 2026-09-17 07:5x — cycle 15, D1 phase full)

**All eight findings ACCEPTED. 0 novel. No citation refuted. The verdict STOPPED the build**, and correctly:
the route this session had already *measured* is the one A3 records as a crash, and A5 attacks the premise that
the artefact is needed at all. **No streaming-write op or donor copy was built.**

| # | verdict | disposition |
|---|---|---|
| **A1** | `unread-evidence` | **ACCEPTED.** The proposal's route survey ran `copy_by_index` against `New VI Object` and omitted `drop_subvi`, which a prior review had already named. Folded into B1. |
| **A2** | `contradicted` | **ACCEPTED.** "Candidate donors not yet opened" is false for `save N xyz traces.vi` — `tools/recipes/build_strtopath.py` opens it and copies uid 160 out of it. `save trace.vi` **#376**'s diagram is genuinely unopened, and that is now the open item (see A5). |
| **A3** | `already-failed` | **ACCEPTED, and it kills the route this session had just measured.** I had censused the NI example `examples\File IO\Text (ASCII)\Write to Text File and Read from Text File.vi` (`tools/bench/diag_filewrite_donor2.log`) and found all three nodes on its Case frames — `Open/Create/Replace File` #194/#508, `Write to Text File` #108/#1097/#1186/#1249/#5370, `Close File` #414/#2039 — and the whole-VI `report_all('Node')` index space `copy_by_index` addresses. **That measurement stands as a fact about the example and is recorded; the ROUTE built on it does not**, because a vi.lib / NI-example VI as a `copy_*` donor is a recorded LabVIEW crash. Not attempted. |
| **A4** | `unread-evidence` | **ACCEPTED, escalated.** Abort/partial-record exposure, refnum ownership and the disk-full policy are written down and are in **no** gate of plan §10. A material session may not add a data-safety policy to the plan; recorded as an OPEN item for judgement. |
| **A5** | `contradicted` | **ACCEPTED, escalated — it can delete the work.** §7.1's "the user's requirement verbatim" cites `archive/prose/2026-09-17-d1-d2-explained-r2.md`, a document we wrote, and its premise ("the original saves once at the end") conflicts with our own census of `#376`, whose terminals include `saved file refnum` (t8), `file # to append out` (t4) and `file progress` (t3) — all measured again this session in run 4's cut list. `#376` already moves into 1.7 (plan §5a/§7.2). **If it already appends per frame, the TSV is a second artefact with no sourced requirement.** The cheap measurement A5 asks for — open `#376 save trace.vi` read-only and read what it does with `saved file refnum` — is material work and is the next step; **the decision that follows it is judgement**, so it is not pre-empted here. |
| **B1** | `helper-exists` | **ACCEPTED.** `g.drop_subvi` is listed in the recipe's own "what already exists" block 15 lines below the line claiming no placer exists. Measured this session: `vi.lib\Utility\file.llb` ships `Open File+.vi`, `Close File+.vi`, `Write File+ (string).vi` and `Write Characters To File.vi` (`tools/bench/diag_filewrite_donor.log`, 4/4 present). A **one-call** file VI placed by `drop_subvi` needs no new op, no copy, and no refnum across a loop border — and it removes A4's Abort exposure. This is the route to measure **if** A5 leaves a requirement standing. |
| **B2** | `already-built` | **ACCEPTED.** "This is the ONE thing D1 cannot build today" (`build_d1_v0.py:48-50`) is **withdrawn** — file-I/O nodes have already been placed and wired into a working copy of the original. The route recorded there is a **GUI** one, and CLAUDE.md §3 makes using it a decision no material session takes; it is named, not used. |
| **B3** | `already-measured` | **ACCEPTED.** A copied node keeps its donor's arity — the reason `StrToPath.vi` exists. Reinforces A3: the copy route is the wrong one for a multi-argument file primitive. |

**Net effect.** The streaming write is **not blocked by a missing capability** and **not built**. Two things must
happen first, in this order, and the second is not mine: (1) MATERIAL — open `#376 save trace.vi` read-only and
measure what it does with `saved file refnum` / `file # to append`; (2) JUDGEMENT — decide, on that measurement,
whether §7.1's TSV is still a requirement, and if it is, whether it is the `drop_subvi` one-call route (B1) with a
stated Abort/disk-full policy (A4). Recorded in `STATUS.md` under OPEN.
