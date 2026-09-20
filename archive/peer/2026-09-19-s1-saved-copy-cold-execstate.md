# s1-saved-copy-cold-execstate

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.2400  in 38 / out 40340 / cache-create 182420 / cache-read 2472237  (586s, 34 turn(s))
- **date:** 2026-09-19 22:09:38
- **outcome:** ANSWERED (590s)
- **why asked:** MANDATORY failed-prediction review (CLAUDE.md §5). `tools/recipes/stage_d1_s1.py` gate B predicted the saved copy would read `ExecState` (cold 0, preloaded 1) like a pristine byte copy; it read (cold 1, preloaded 1). Task file `tools/bench/task_s1_savedcopy.md`; dispatch log `tools/bench/peer_s1_savedcopy.log`.
- **verdict:** ANSWERED — accepted as a HYPOTHESIS, not as fact (CLAUDE.md §5: a peer answer is a hypothesis). Its discriminating tests T0/T1/T2 are UNRUN; the only measurement taken since is the nine-class structural census (delta 0), which is blind to the link table it accuses.

## Question

# A failed prediction about LabVIEW `SaveInstrument` on an unedited copy of a large VI

Environment: LabVIEW 2026 (26.3.1f1) on Windows 10, driven over the exported ActiveX/COM
`LabVIEW.Application` interface from Python (pywin32). The VI under test is a 473 KB top-level
acquisition/tracking VI with 98 subVI calls, 170 diagrams, 626 nodes.

## PREDICTION (contract B in `tools/recipes/stage_d1_s1.py`)

A COM `SaveInstrument` save of an **UNEDITED byte copy** of the main VI, made in a LabVIEW instance
where the **ORIGINAL was preloaded read-only**, would leave the saved file reading `ExecState`
(cold 0, preloaded 1) — the same pair as a pristine byte copy — because a prior measurement
established that a cold read measures subVI **LINKAGE** and nothing in the VI was edited.

"cold" = the file is opened by `GetVIReference` in a freshly restarted LabVIEW with nothing else
loaded. "preloaded" = the ORIGINAL is first held resident read-only by `GetVIReference` in that
same instance, then the copy is opened and its `ExecState` read.

## OBSERVED (`tools/bench/stage_d1_s1.log`, four readings in four separate LabVIEW instances, pids 14028 / 21224 / 25544 / 21584)

- saved copy `D1_s1arm_savetest.vi`: cold **1** (`:36`), preloaded **1** (`:68`)
- pristine byte copy `D1_s1ctl_bytecopy.vi`: cold **0** (`:57`), preloaded **1** (`:79`)
- the save: `g.save()` → `SaveInstrument` returned 475,141 in 0.28 s, no exception (`:14-15`);
  bytes 473,317 → 475,141 (**+1,824**); md5 `2a78e17c…` → `e0112963…`; LabVIEW saved-version bytes
  `26 00 80 00` at offset 36 **UNCHANGED** (`:10`, `:17`); the ORIGINAL is byte-identical
  afterwards (`:85`).
- the copy lives in `…\LabVIEW 2026\user.lib\claudeDev\`, i.e. a **DIFFERENT directory** from the
  original it was copied from.
- Verbatim from the same log, the diagnostic the script took at the ONE cold `ExecState 0` reading
  (`:59-64`), which is the pristine-control leg:

```
    --- ExecState 0: MEASURE BEFORE CLOSING
    FACT SUBVI RESOLUTION: 7 calls over the first 8 of 170 diagrams; 4 with empty name/path or a path not on disk
        UNRESOLVED Diagram[3] uid 30804 name='MOV.vi'  path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\General command.llb\MOV.vi'
        UNRESOLVED Diagram[4] uid 4620  name='GOH.vi'  path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\Limits.llb\GOH.vi'
        UNRESOLVED Diagram[5] uid 5403  name='VEL.vi'  path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\General command.llb\VEL.vi'
        UNRESOLVED Diagram[5] uid 5497  name='POS?.vi' path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\General command.llb\POS?.vi'
```

(The same four names are also listed as resolved `subVI` entries in the same dump, i.e. the entries
exist but their stored paths do not point at files on disk. No equivalent dump exists for the other
three readings, because the script only takes it on an `ExecState 0`.)

## ALREADY RULED OUT — do not spend the answer on these

- It is **not a version upgrade**: the saved-version bytes are unchanged (`26 00 80 00`, offset 36).
- It is **not an edit**: no scripting call touched the diagram — the phase only copies, opens, reads
  and saves.
- It is **not instance contamination**: each of the four readings is its own child process and its
  own LabVIEW pid, verified distinct.

## THE QUESTIONS

1. What does LabVIEW actually rewrite when `SaveInstrument` is invoked on an **unedited** VI that
   was loaded with its subVI hierarchy resolvable, and does that plausibly explain a later **COLD**
   `ExecState` of 1?
2. Is there any mechanism by which the saved file could now **depend on, or have inherited state
   from, the in-memory ORIGINAL** — a cross-linking hazard that was asserted in this project's
   planning documents but never measured?
3. Could this save have changed the VI's **COMPUTATION** in any way (this project's rule 1a forbids
   that absolutely), and what is the **cheapest test that discriminates** "the save repaired a link
   table broken by the directory move" from "the save wrote something that can change behaviour"?
4. What would **falsify** the benign reading?

Answer each of the four explicitly. Name the cheapest discriminating test concretely enough that it
can be run over the same COM interface or offline on the bytes.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, so the review is the answer itself.

---

# Failed-prediction review — `SaveInstrument` on an unedited copy of the main VI

**Verdict: the linkage *mechanism* in the framing survives; the *diagnosis* and the word "repair" do not.**

## 1. The single strongest reason the claim is WRONG

**The diagnostic that names the cause of cold `ExecState 0` flags LLB membership, not link failure — and the four VIs it names are links the healthy ORIGINAL itself carries.**

The test is `tools/bench/diag_d1_execstate_preload.py:132`:

```python
if (not row["name"]) or (not row["path"]) or (not os.path.exists(row["path"])):
```

- `C:\...\instr.lib\Mercury\GCS_LabVIEW\Low Level\General command.llb` and `...\Limits.llb` are real **`.llb` FILES** on this disk (I listed them). LabVIEW addresses a VI inside an LLB as `C:\example.llb\color.vi`, but the LLB is a *container file*, not a directory — so `os.path.exists()` on such a path is **always False**, whether or not the VI is inside.
- **The internal control is in the same dump.** `Simple Error Handler.vi` sits at `vi.lib\Utility\error.llb\Simple Error Handler.vi` and was **not** flagged — because in LabVIEW 2026 `vi.lib\Utility\error.llb` is a real **directory** of loose `.vi` files (40 listed). The flag tracks "is the container a genuine `.llb` file?" with **5/5 agreement, zero residual**.
- `POS?.vi` cannot exist as a Windows file at all — `?` is an illegal NTFS filename character.
- **The clincher:** `tools/bench/main_vi_subvis.json:17,24,31,36` records those same four paths as the **ORIGINAL's own resolved subVI links** (`:2` — the census was taken on `G:\...\Min_Track N beads V6_ParallelLoop.vi`), and the ORIGINAL reads `ExecState 1` (`tools/bench/stage_d1_s1.log:12`). Paths in a working VI's link table are healthy links.

Two defects compound it:

- **Selection on the dependent variable.** `diag_d1_execstate_preload.py:121` runs the dump only `if res["execstate"] == 0:`. It was collected *exclusively* in the failing condition, so it cannot discriminate anything. The same four rows appear in the 2026-09-18 run (`diag_d1_execstate_preload.log:16-19`) — deterministic, exactly as "it flags LLB members" predicts.
- **7 % sample.** `:127` caps at the first 8 of 170 diagrams; 7 calls out of 98. The other 91 were never examined.

And the causal story is internally inconsistent: subVI paths are stored **relative to the caller, except symbolic roots** (`<vilib>`, `<userlib>`, `<instrlib>`). The four named VIs live under `<instrlib>` — precisely the links a directory move **cannot** break.

## 2. Alternative explanation of the same evidence

**The save did not repair a broken link table. It CONVERTED search-resolved links into absolute links to whatever was resident — and the cross-linking bait is sitting in the save directory.**

- LabVIEW's default search order begins `<topvi>\*` (recursive), then `<foundvi>`, `<vilib>\*`, `<userlib>\*`, `<instrlib>\*`.
- `<topvi>` for both test files **is `claudeDev`**, and `C:\...\user.lib\claudeDev\background VIs_COPY\` holds same-named copies of ~87 of the hierarchy's project subVIs (`tools/gscript.py:60`; `tools/bench/census_path_donors.log:2`).
- "LabVIEW loads the first subVI it finds by that name into memory and informs the user about the modified links" — so a **cold** claudeDev copy binds preferentially to `background VIs_COPY\`, not to `G:\...\background VIs\`.
- Under **preload**, the ORIGINAL's real hierarchy is already in memory by qualified name and wins. Phase A loaded the arm under preload (`tools/recipes/stage_d1_s1.py:320-321`), so every project call bound to the real G: file, and `SaveInstrument` persisted those. NI's forum answer: saving the caller afterwards "will also save a new relative file path."
- **Quantitative support the compiled-code story does not make:** +1,824 B over ~90 project subVI calls ≈ **20 B/call** — about the length difference between `..\..\background VIs\X.vi` and `G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs\X.vi`.

This also names a cause for cold `0` unrelated to the PI VIs: the original calls `G:\...\zz_LabView VI\DY\Background VIs\Max Trans Pos.vi` (`main_vi_subvis.json:118`) and `G:\...\SiHyeong Modified\Motor control v5_No Recording.vi` (`:130`), and **neither has a twin in `background VIs_COPY\`** (I checked). Those cannot resolve cold, by search or otherwise.

Second, cheaper alternative to exclude: **A3 and B-i are not the same measurement.** Phase A did `open_panel` + `sleep(1.0)` before reading (`stage_d1_s1.py:321-323`); the phase-B child does a bare `GetVIReference` then reads `.ExecState` on the next line — no panel, no settle (`diag_d1_execstate_preload.py:115-116`). n = 1 per cell.

## 3. The four questions, explicitly

**Q1 — what does `SaveInstrument` rewrite, and does it explain cold 1?** Compiled code (unless separated) *and* the linker records, written as the paths of the subVIs **actually linked in memory at save time**. Yes, it explains cold 1 — by **re-binding**, not repair. A compiled-code refresh alone cannot make a VI that could not find its subVIs suddenly find them.

**Q2 — could the file have inherited state from the in-memory ORIGINAL?** **Yes, and it is the same mechanism as Q1.** Not the hypothetical hazard the plan called "NEVER MEASURED" — the bait is in the save directory. The arm's dependency graph is now pinned to whatever was resident; the same recipe run *without* the preload would pin it to `background VIs_COPY\`.

**Q3 — could the save have changed COMPUTATION?** The dichotomy in the question is false — link-table rewriting **is** the behaviour-changing act when the binding differs. Three live mechanisms, none excluded by the current evidence: (a) subVI re-binding; (b) typedef re-instantiation on load, persisted on save; (c) polymorphic/Express regeneration.

**Q4 — what would falsify the benign reading?** Any of: a row in ARM(cold) pointing into `background VIs_COPY\`; ARM(cold) differing from ORIGINAL(cold) on any of the 98 rows; a `DFDS` or `VCTP` delta in the byte census; a numeric difference on the fixture.

## 4. Cheapest discriminating test

**T1 — full path census (primary; ~10 min, read-only over COM, no new tool).** Three fresh instances: ARM cold, CTL cold, ORIGINAL cold. Run `subvis()` over all 170 diagrams; diff the three 98-row (name, path) tables.

| result | conclusion |
|---|---|
| ARM(cold) == ORIGINAL(cold) on all 98 rows | the save wrote the original's own bindings — benign reading earned |
| any ARM row inside `background VIs_COPY\` | the artefact is cross-linked; rule 1a is in play |
| any CTL(cold) row inside `background VIs_COPY\` | **every cold measurement this chain took on a claudeDev copy read the wrong hierarchy** (run 6's census included) |
| CTL(cold) unresolved rows | the real cause of `ExecState 0` — predicted: `Max Trans Pos.vi`, `Motor control v5_No Recording.vi` |

**T0 — free rider (one line, existing tool).** Move the dump out of `diag_d1_execstate_preload.py:121`'s `execstate == 0` guard and make `:132` LLB-aware (`os.path.exists(p) or os.path.exists(longest .llb prefix)`). If the same four PI rows appear in the **ExecState-1** conditions too, the stated cause of cold-0 is dead.

**T2 — offline byte census (no LabVIEW lock).** Both files are still on disk (`stage_d1_s1.log:87` — gate B stopped the chain before B4's delete), and CTL is byte-identical to the ORIGINAL. Parse each RSRC block directory (pylabview `readRSRC.py`) and diff block names/sizes/hashes. Delta confined to `VICD` + `LIvi`/`LIbd`/`LIfp`/`LIds` with `BDHb`/`BDHP`/`FPHb`/`DFDS`/`VCTP` identical ⇒ no source and no default data changed. A `VCTP`/`DFDS` move ⇒ typedef re-instantiation ⇒ rule 1a.

## 5. What would change my mind

T1 returning ARM(cold) identical to ORIGINAL(cold) on all 98 rows **and** T2 showing no heap/`DFDS`/`VCTP` delta. Even then it is not a no-op: the artefact would be *absolutely* linked where the original is *relatively* linked, and the chain should record that rather than call it nothing.

**What the evidence does not settle:** whether `MOV.vi`/`GOH.vi`/`VEL.vi`/`POS?.vi` are genuinely resolved on the copy. The measurement taken cannot distinguish "resolved" from "missing" for any LLB member. It does not need to — the ORIGINAL carries those same paths and is not broken — but they should not be recorded as resolved either.

---

**Sources:** [ExecState — NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi/execstate.html) · [ExecState Property (ActiveX)](https://documentation.help/NI-ActiveX-LabView/ExecState.html) · [LabVIEW Library (LLB) — Wiki](https://labviewwiki.org/wiki/LabVIEW_Library) · [Extract Files from an LLB — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P8XESA0) · [Symbolic path — Wiki](https://labviewwiki.org/wiki/Symbolic_Path) · [SubVIs calling: absolute or relative paths? — NI](https://forums.ni.com/t5/LabVIEW/SubVIs-calling-Absolute-or-relative-paths/td-p/936910) · [Modifying Default Search Paths for SubVIs — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9BOSA0) · [Another VI with the Same Name in Memory — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OjgSAE) · [Preventing Cross-Linking in LabVIEW](https://scienceandwires.wordpress.com/2012/08/27/how-to-prevent-cross-linking-issues-in-labview/) · [Project Explorer best practices — NI](https://ni.com/tutorial/6200/en) · [LabVIEW re-saves VIs I haven't changed — NI](https://forums.ni.com/t5/LabVIEW/LabVIEW-re-saves-vi-files-even-though-I-haven-t-changed-them/td-p/4205819) · [Separating Compiled Code from VIs — NI](https://www.ni.com/docs/en-US/bundle/labview/page/separating-compiled-code-from-vis-and-other-file-types.html) · [pylabview RSRC Format](https://github.com/mefistotelis/pylabview/wiki/RSRC-Format)

## Sources

(extract from answer)

## What was done with it

**Classified ANSWERED (590 s, $4.2400) by the cycle-46 act-4 MATERIAL session. NOT acted on — every finding here
is a judgement call and is handed up unchanged.** What the material session did do, and nothing more:

1. **Ran the one measurement its brief named**, which is independent of this review and was written before it
   landed: `tools/bench/s1_savedcopy_census.py` → `tools/bench/s1_savedcopy_census.log` (`BGRUN END rc=0 after
   74s`, 7 PASS / 0 FAIL, artefact `tools/bench/s1_savedcopy_census.json`). Saved arm `D1_s1arm_savetest.vi` vs
   the ORIGINAL, one fresh instance with the ORIGINAL preloaded read-only, **all nine pinned classes delta 0**
   (Diagram 170 · Node 626 · Wire 1902 · LoopTunnel 132 · ControlTerminal 114 · WhileLoop 3 · Local 8 · SubVI 98 ·
   Function 181). This **neither confirms nor refutes** §2: object counts are blind to link-table contents, which
   is exactly why the review names T1/T2 instead. It does establish that the +1,824 B is not objects.
2. **Recorded the capability and the open question** in `docs/toolkit-capabilities.md` (new subsection before
   "Harness frictions measured in cycle 22"), citing this file.
3. **Recorded the result in `STATUS.md`'s lock block** (`owner_c46m4`), including the rule-1a status the review
   states — **NOT excluded** — and the three tests it names (T1 98-row subVI path census · T0 free rider on
   `diag_d1_execstate_preload.py:121`/`:132` · T2 offline RSRC block diff).

**Explicitly NOT done, and left for the judgement session:** running T0/T1/T2; changing any gate in
`tools/recipes/stage_d1_s1.py`; amending `docs/cycle27-plan.md` Pre-decided 14a or 16(b); deciding whether the
saved arm may be used as a stage artefact; touching `diag_d1_execstate_preload.py`'s `os.path.exists` test or its
`execstate == 0` guard (the review calls both defective — that is a design change, CLAUDE.md §3).
