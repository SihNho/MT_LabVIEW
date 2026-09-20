r"""S2 OF THE Pre-decided 22 STAGE CHAIN — three While loops on Diagram #686, then `move_in` for the three call
sites, then the conditional-terminal scaffold, then save. BRANCH 1 OF 30(e), FIXED BY 31(b), **ORDERED BY 32(b)**.
NO DELETE, NO RE-DROP, NO SCAFFOLD SUBVI, AND **`OpExitWhile_v0` IS REFUSED** (32(a)).

  MATERIAL=1 py tools/bgrun.py --material --max-min 30 --log tools/bench/stage_d1_s2_a.log \
      -- py -u tools/recipes/stage_d1_s2.py --phases A
  MATERIAL=1 py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_s2_cd.log \
      -- py -u tools/recipes/stage_d1_s2.py --phases CD

THE SPEC IS `docs/cycle27-plan.md` Pre-decided 30 (`:668-735`) **AS AMENDED BY 31 (`:737-793`), 32 (`:794-836`)
AND 33 (`:838-864`)**. NOTHING HERE IS RE-DERIVED.
=============================================================================================
31 disposes `archive/peer/2026-09-20-priorart-d1-s2-stage.md` (ANSWERED, eight slugs, no `novel`): all eight
findings ACCEPTED, none refuted. What it changed in THIS file, clause by clause:

  31(a) 🔴 **`#5058` IS THE CPU KERNEL `Track N beads four-fold over-kernel-v3.vi`, NOT `GPU_kernel_v1.vi`.**
        30(d)'s parenthesis was WRONG. Every label, comment and log string here carries the true name, and gate
        **C2k** READS the VI name at `#5058` on the artefact and FAILS THE STAGE if it is not that name.
        Swapping the CPU kernel for the GPU one is its own later stage with its own rule-1a argument; nothing
        in S2 assumes it has happened.
  31(b) **A1 IS SETTLED, NOT MEASURED**: `move_in` already lands nodes into loop bodies created in the SAME
        run — 21 landings, `tools/bench/build_d1_routeb_v7_run10.log:116-173` and `:70-76`,
        `docs/d1-build-plan.md:873`. So the branch is FIXED to `movein` and `select_branch()` reads nothing.
        Phase A still READS from that same log whether `#5058`/`#48`/`#376` were among the 21 or were
        EXCLUDED, and the reason v7 gave — recorded, NON-FATAL, for judgement (it is the only thing that can
        send S2 back to the delete-and-re-drop shape, and that is judgement's call, not this file's).
  31(c) said **A2 IS MOOT** under branch 1 (nothing is dropped, the three keep their wires) — 🔴 **WITHDRAWN
        BY Pre-decided 33(c)** (below): a move SEVERS the wires, so the relocated node lands unwired and
        Required-ness is load-bearing again. `a2_required_readable=False` still stands as a fact about the
        fleet; what is gone is the "moot".
  31(d) named `OpExitWhile_v0` as "the scaffold of record" — 🔴 **SUPERSEDED BY Pre-decided 32(a)** (below).
  31(e) 30(f)'s `True` is a requirement on the VALUE DELIVERED at the conditional terminal, not on the object
        being a literal constant; a route that can only deliver FALSE is REFUSED.

Pre-decided **32** (`docs/cycle27-plan.md:794-836`), cycle 49, 2026-09-20 — it answers the two `OPEN:` lines the
previous material session raised, and it is what this file now implements:

  32(a) 🔴 **`OpExitWhile_v0` MUST NOT be the S2 scaffold, and `SCAFFOLD_STOP_CONTROL = "stop (end)"` is
        OVERTURNED.** Measured: the op sources the conditional terminal from a FRONT-PANEL BOOLEAN CONTROL BY
        NAME (`tools/gscript.py:1083-1114`), so it delivers the operator's value — FALSE at load, the exact
        "instrument that hangs" 30(f) forbids — and it would add readers of an ORIGINAL front-panel control in
        three new places. **No original front-panel control is wired into a new loop by this file.** The name
        `SCAFFOLD_STOP_CONTROL` is never assigned and never read here — it survives only in comments that say
        why it was overturned, not as an identifier.
  32(b) **THE ORDER INSIDE THE STAGE IS: create the three loops -> `move_in` the three nodes -> scaffold the
        three conditional terminals -> save.** The body-node-addressed routes were unreachable only because an
        EMPTY body has no node to address; after `move_in` each new body holds its relocated node. Intermediate
        illegality inside the stage is EXPECTED AND PERMITTED — only the SAVE needs `ExecState != 0`
        (`gscript.py:2065-2071`, 29(d)), which is the whole reason 29(e)/30(b) make this one stage.
  32(c) **A3 IS A REAL MEASUREMENT OVER EVERY BUILT CANDIDATE**, not a one-op availability check: per candidate
        (i) its exact inputs, (ii) what it ADDRESSES (conditional terminal / body node terminal / panel-control
        name / diagram), (iii) whether the Boolean it delivers is a CONSTANT and whether that value can be set
        TRUE by that op or by another already-built op, (iv) the measured evidence line. Phase A still EDITS
        NOTHING, so every reading is taken from the op files, the op label JSONs, `gscript.py` and the archived
        measurement logs — and the candidate list is CHECKED FOR COMPLETENESS against a live scan of
        `docs/toolkit-capabilities.md`.
  32(d) **THE SELECTION RULE, APPLIED MECHANICALLY BY THIS FILE FROM A3's OWN TABLE** (judgement is already
        spent — the material session does NOT come back): (1) an op that puts a Boolean CONSTANT TRUE on the
        CONDITIONAL TERMINAL wins; (2) failing that, `OpCreateEqual_v0` -> `OpStopFromNode_v0`, and ONLY IF its
        delivered value is PROVABLY CONSTANT TRUE from `tools/bench/build_opsentinel_ops_run3.log` F5c/F6 — a
        comparison whose value is not provable from that record does NOT qualify; (3) nothing else. **If
        neither qualifies the stage STOPS after phase A and saves `tools/bench/s2a_legality.json`** (30(e)
        branch 4, 31(i)) — a legitimate end that leaves a file and hands judgement a measurement.
  32(e) v7's exclusion of `#5058`/`#48`/`#376` from its 21 `move_in` landings does NOT send S2 back to
        delete-and-re-drop: the cause v7 states is a bookkeeping preference about which wires route B wants cut
        later, not a finding that `move_in` fails on these nodes. **BRANCH 1 STANDS**; A1x is recorded, and it
        no longer carries a "this could send S2 back" rider.
  32(f) Rule 1a for this stage. ⚠️ **ITS FIRST SENTENCE IS WRONG AND IS CORRECTED BY 33(a) (below): a move
        SEVERS the node's wires, it does NOT turn them into tunnels, and NOTHING passes through.** What stands
        is the rest: **PHASE D RECORDS THE INDEXING STATE OF EVERY NEW TUNNEL** if any built op can read it
        (one can — `gscript.tunnels` / `OpTunnels_v0`), and SAYS SO PLAINLY IN THE LOG when the stage created
        no tunnel at all, which is what 33(a) expects.
  31(f) **A4 DROPS ITS TWO ExecState CHILD PROCESSES.** The pair is already recorded on this exact md5 at
        `tools/bench/stage_d1_s1_cd.log:153` (COLD 1) and `:155` (PRELOADED 1); the md5 gate already proves
        the file has not moved. The PRELOADED state is read anyway inside C/D, where the save route needs it.
  31(g) **PHASE C REUSES v7's ALREADY-PASSING STEP FUNCTIONS** (`build_d1_routeb_v7_run10.log:70-76`, `:106`).
        What is genuinely new is the STAGE BOUNDARY: copy from the S1 artefact, gate on its md5, save
        `D1_s2_loops.vi`.
  31(h) **THE NET CONTRACT: SubVI 97 -> 97 (nothing is created or destroyed at any point), WhileLoop 3 -> 6,
        Diagram 170 -> 173**, every comparison against the ORIGINAL, never a copy (29(g)).
  31(i) If the stage CANNOT END LEGAL it saves `tools/bench/s2a_legality.json` and SAYS SO. Never a broken
        VI, never `allow_broken=True`, never a new op (Pre-decided 2).

Pre-decided **33** (`docs/cycle27-plan.md:838-864`), cycle 49, 2026-09-20 — the ROUND-2 prior-art review
(`archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md`, five findings, all accepted) corrected 32(f) and re-opened
the stage boundary. It is what the current file implements:

  33(a) 🔴 **`move_in` SEVERS WIRES, IT DOES NOT TUNNEL THEM.** 32(f)'s "turns each crossing wire into a
        While-loop tunnel, so values pass through unchanged" is FALSE. MEASURED: route A's relocation left
        **109 CUT terminals over 24 uids** (`docs/d1-route-b-plan.md:57-58`, from `d1_rewire_sources.json`),
        of which **32 belong to `#5058` / `#48` / `#376`** (`:67`). The relocated node lands in the new body
        **UNWIRED**. The tunnel-indexing reading (`gscript.tunnels` / `OpTunnels_v0`, `gscript.py:941-978`)
        stays worth taking — it simply has NOTHING TO READ when no tunnel is created, and this file says that
        rather than implying a pass-through that does not happen.
  33(b) 32(e)'s CONCLUSION survives, its REASON does not: branch 1 preserves NO wires. It is right because it
        **keeps the node's IDENTITY** (uid, configuration, connector state) while delete-and-re-drop destroys
        and re-creates the call (SubVI 97 -> 94 -> 97).
  33(c) 🔴 **THE STAGE BOUNDARY IS RE-OPENED AND PHASE A IS WHAT CLOSES IT — so 31(c)'s "A2 is MOOT" is
        WITHDRAWN and A2 is LOAD-BEARING AGAIN.** If a moved node lands unwired, branch 1 meets the same wall
        29(e) named for delete-and-re-drop: bare Required inputs => `ExecState 0` => `gscript.save()` cannot
        reach `SaveInstrument` (`gscript.py:2065-2071`) => the stage cannot end legal WHATEVER is done to the
        conditional terminals. **A5 (new) answers, from already-measured files and without editing anything:
        does a `move_in`'d node land unwired, and does an unwired REQUIRED input on `#5058` / `#48` / `#376`
        follow from it?**
  33(d) If phase A shows S2 cannot end legal in ANY shape, the stage STOPS after A with
        `tools/bench/s2a_legality.json` (30(e) branch 4, 31(i)) and judgement re-cuts the boundary. Never
        `allow_broken=True`, never a new op (Pre-decided 2).

S1 IS DELIVERED: `claudeDev\D1_s1_copy.vi`, md5 `3e3d23cefd3a334001aa9d6156bf1aee`, 474,202 B, 20/0
(`tools/bench/stage_d1_s1_cd.log:115-346`). This stage starts FROM THAT FILE (30(c)) and ends at
`claudeDev\D1_s2_loops.vi`.

🔴 THE NET CONTRACT OVER THE STAGE IS **SubVI 97 -> 97 · WhileLoop 3 -> 6 · Diagram 170 -> 173** (30(a),
31(h)). Pre-decided 22's row "+3 loops +3 subVIs" describes v7's `s2d` DROPS, which branch 1 does not make;
**a gate asserting SubVI 100 would be WRONG**. `docs/d1-route-b-plan.md` §7's Diagram **174** counts a fourth
(pool) loop that is not built here — 173 is this stage's number (`build_d1_routeb_v7.py:78-83`).

PRIOR ART — checked before a line was written; everything below is REUSED, nothing is invented
-----------------------------------------------------------------------------------------------
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`:
  * **The whole skeleton is `tools/recipes/stage_d1_s1.py`** (30(c)): `main()`/`--phases` `:763-800`,
    `gate()` `:258-265`, `fact()` `:267-269`, `md5()` `:272-277`, `labview_pid()` `:280-290`,
    `version_bytes()` `:293-300`, `file_facts()` `:303-314`, `fresh()` `:317-330`, `class Preload` `:332-358`,
    `orig_gate()` `:369-373`, `cold_subvi_table()` `:377-405`, `compare_subvi_tables()` `:408-427`,
    `log_table_diff()` `:430-447`. **ONE substantive change**: S1's `:623-625` `shutil.copy2(ORIGINAL, TARGET)`
    becomes a copy from the **S1 ARTEFACT** (30(c)).
  * **The stage body is `build_d1_routeb_v7.py`'s own, re-cut** (31(g) — these steps have PASSED their gates in
    the real VI, `build_d1_routeb_v7_run10.log:70-76`): `s2()` `:788-812` (three `g.loop_in("while", …)` on
    Diagram #686 with the `new_since` gates and the `#637`-still-owns gates) and the `S3` move block
    `:955-966` (the owner-chain gate on a `move_in` landing). v7's `s1d()` `:754-784` and `s2d()` `:815-847`
    are **NOT re-cut**: branch 1 deletes nothing and drops nothing (31(b)).
  * `build_d1_v0`: `move_in` `:318-335`, `owner_of` `:338-354`, `diag_index` `:357-358`, `wmap` `:364-372`,
    `terms_of` `:375-380`, `bare_named_sinks` `:482-...`. `bench_prep.labview_handles`.
  * **Phase A4 reads NO ExecState** (31(f)): the pair is already recorded on this exact md5 at
    `tools/bench/stage_d1_s1_cd.log:153` (COLD 1) and `:155` (PRELOADED 1), and the md5 gate proves the file has
    not moved. `tools/bench/diag_d1_execstate_preload.py` is therefore NOT called from phase A; it stays
    imported only so its `ORIG`/`ROUTEB_PINNED_MD5` can be GATED against this file's own pins.
  * **Every SubVI table comes from the BUILT `tools/bench/s1_subvi_paths.py`** (`run_condition()` `:183-209`),
    exactly as S1's D5 did; the ACCEPTANCE REFERENCE IS THE ORIGINAL, never a copy (29(g)).
  * **The stage's REAL blocker is already named, with a better cause, in our own files** (round-2 review,
    `settled-already`): `tools/recipes/build_d1_routeb_v7.py:131-135` states IN ADVANCE that 1.2 / 1.5 / 1.7
    keep UNWIRED CONDITIONAL TERMINALS because the three sentinel `Equal?`s depend on **queue element types
    that were never designed**, so those runs "CANNOT PRODUCE `ExecState 1`"; and `docs/d1-route-b-plan.md:153`
    is where the intended scaffold was planned as `OpCreateEqual_v0` + `OpCreateConstOnTerm_v0` (3 sentinel
    `Equal?` + 3 sentinel literals −1). This file cites both wherever it reasons about the scaffold, instead of
    re-discovering the wall a sixth time.
  * **The scaffold is whatever A3's TABLE selects under 32(d)** — and `OpExitWhile_v0` is REFUSED (32(a)), so
    `gscript.exit_while` is NEVER called by this file. The candidates read (all already built, none created
    here; **14 of them, the full set the completeness scan names**): `OpCreateConstOnTerm_v0`
    (`build_opcreateconstonterm_v0.create_const_on_term` `:364`),
    `OpCreateConst_v0` / `OpCreateEqual_v0` (`build_opsentinel_ops.create_node` `:387-405`),
    `OpStopFromNode_v0` (its call shape at `build_opstopfromnode_v0.py:443-451`), `OpConnectNested_v0/v1`,
    `OpConnectFromWire_v0`, `OpConnect2_v0`. `OpLoopEndRef_v0` (`loop_end_ref`,
    `build_opstopfromnode_v0.py:340`) READS the conditional terminal before and after — that is gate C6.
  * **32(f)'s tunnel reader is the BUILT `gscript.tunnels` / `OpTunnels_v0`** (`gscript.py:941-978`,
    `docs/toolkit-capabilities.md` row `OpTunnels_v0`, `test_optunnels.log`): it returns `index_mode` per
    LoopTunnel, so the answer to "can any built op read it?" is YES and phase D reads it.
  * **NO NEW OP VI, NO NEW TOOL, NO NEW DEVICE** is created here (Pre-decided 2; user's standing order
    2026-09-18 08:53). If a gate cannot be met, the stage STOPS and saves its DATA artefact (31(i)) — that is
    never a licence to build an op.

PHASE A IS A RECORDING AND EDITS NOTHING (30(d) as amended by 31(b)/(c)/(f))
-----------------------------------------------------------------------------
It opens no VI for editing, copies nothing, saves nothing, and its only product is the DATA artefact
`tools/bench/s2a_legality.json` (+ this log). 31 collapsed three of its four questions into citations, because
the prior-art review found them already answered in our own files. What is left:

 A1  **SETTLED, NOT MEASURED** (31(b)). `move_in` already lands nodes into loop bodies created in the SAME run:
     21 landings, `tools/bench/build_d1_routeb_v7_run10.log:116-173`, the loops themselves at `:70-76`,
     `docs/d1-build-plan.md:873`. `a1_move_in_reaches_new_loop_bodies` is RECORDED TRUE **with that citation**;
     the P1/P2/P4 predicates are kept only as a cheap consistency echo (op on disk, `dest_diagram_index` in the
     signature, the class-agnostic sentence) and P3 now COUNTS the archived landings rather than deciding.
     **A1x — the one thing phase A still reads from the log**: were `#5058` / `#48` / `#376` among those 21, or
     were they EXCLUDED, and with what stated reason? An exclusion with a stated cause is the only thing that
     can send S2 back to the delete-and-re-drop shape, so it is RECORDED and reported NON-FATALLY. Acting on it
     is judgement's call (CLAUDE.md §3: a material session measures and does not take the result-dependent
     action).
     Recorded beside it, non-deciding: **a move SEVERS the moved object's wires** — MEASURED, 109 cut terminals
     over 24 uids (`docs/d1-route-b-plan.md:57-58`), 32 of them on these three (`:67`); `build_d1_v0.py:328-331`
     force-feeds a neutralised `error in`. ⚠️ `docs/s0-diff.md:46` is the **D22 error-neutraliser** row and does
     NOT say a move cuts wires; it was cited here for that and the citation is now corrected (33(a)). The cut
     rows are captured for S3w.
 A2  🔴 **NO LONGER MOOT — 31(c) IS WITHDRAWN BY 33(c), AND A2 IS LOAD-BEARING AGAIN.** A move severs the wires
     (33(a)), so the relocated node lands UNWIRED exactly as a freshly dropped one would, and Required-ness
     bites under branch 1 after all. `a2_required_readable` stays **False** — no built op reads the
     Required/Recommended/Optional flag, and building that reader is forbidden by Pre-decided 2 — so A2 READS
     the three connector panes and the live call-site terminals and hands them to **A5**, which is where the
     legality question is answered from already-measured files. The files that already bear on it are CITED,
     not probed: `docs/d1-route-b-plan.md:148`, `:154`, `:158-159`; `docs/d1-build-plan.md:523-536`;
     `docs/NAMES.md:564-565`. A2 still does not SELECT a shape by itself (the shape is 31(b)'s branch 1); what
     it feeds is A5's recording.
 A3  **A REAL MEASUREMENT OVER EVERY BUILT CANDIDATE (32(c)), THEN 32(d)'s SELECTION RULE APPLIED
     MECHANICALLY.** For each candidate the table carries: `inputs` (the op's actual control names, from its
     capability row and its own label JSON where one exists) · `addresses` (what the op can point at:
     `while-loop conditional terminal` / `body node terminal` / `panel control name` / `diagram`) ·
     `delivers_constant` + `value_can_be_TRUE` with the reason · `evidence` (file:line, grepped LIVE so the
     citation is machine-checked, never asserted). `writes_conditional_terminal` is NOT hand-set: it is derived
     from the op's own capability row (the row must name the conditional terminal AND be marked WRITER), and a
     live scan of `docs/toolkit-capabilities.md` for every WRITER row that names a conditional terminal or
     creates a constant is compared against the table so COMPLETENESS is checked by the machine too.
     `OpExitWhile_v0` is in the table and is marked **REFUSED by 32(a)** with its measured reason.
     🔴 **THE TABLE COVERS ALL 14 OPS THAT SCAN NAMES, NOT 10** (round-2 review, `contradicted` #2): the
     scan's WRITER rows are `docs/toolkit-capabilities.md:30, :31, :63, :64, :65, :66, :67` and the ops named
     in them are `OpBuildCase_v0 · OpConnect2_v0 · OpConnectNested_v0 · OpConstValueN_v1 ·
     OpCreateConstOnTerm_v0 · OpCreateConst_v0 · OpCreateEqual_v0 · OpExitLoop_v0 · OpExitWhile_v0 ·
     OpForLoop_v0 · OpLoopEndRef_v0 · OpStopFromNode_v0 · OpWhileLoop_v0 · OpWireSource_v5` (MEASURED by
     re-running the scan's own filter over the file, 2026-09-20). The six the table used to omit are measured
     here like the rest, and **`OpConstValueN_v1` and `OpWireSource_v5` are exactly the shapes 32(d) rule (1)
     looks for**, so the "no route delivers constant TRUE" prediction is RE-DERIVED from the full table below
     rather than carried over. The scan reads WHOLE LINES: `_grep`'s 400-character truncation used to hide
     rows `:63` `:64` `:67` from it entirely, which is why the old table looked complete and the gate still
     failed.
 A4  **THE STARTING STATE, md5 ONLY** (31(f)). `D1_s1_copy.vi`'s md5 against the pin, plus the two CITED
     ExecState readings (`stage_d1_s1_cd.log:153` COLD 1, `:155` PRELOADED 1). NO child process, NO LabVIEW
     restart, NO ExecState read: the PRELOADED state is read anyway inside C/D, where the save route needs it.
 A5  🔴 **NEW, 33(c): DOES A `move_in`'d NODE LAND UNWIRED, AND DOES AN UNWIRED *REQUIRED* INPUT FOLLOW?**
     Answered from ALREADY-MEASURED FILES only — phase A still edits nothing, opens nothing for editing and
     probes nothing. Part 1 is MEASURED and settles: a move severs the node's wires (109 cut terminals over 24
     uids, `docs/d1-route-b-plan.md:57-58`; 32 of them on `#5058` / `#48` / `#376`, `:67`), so the landing is
     UNWIRED. Part 2 is the one 33(c) re-opened, and this file reports what the fleet can and cannot say: no
     built op reads the Required/Recommended/Optional flag (A2), the ONE recorded route to it is a by-effect
     probe that DROPS the subVI and reads `ExecState` (`docs/NAMES.md:564-565`,
     `tools/recipes/build_harness_gpu2.py`) — an EDIT, which 30(d) forbids in phase A and Pre-decided 2 forbids
     building a reader for. So `a5_required_follows` is recorded as **UNKNOWN**, never as False, and
     `a5_stage_can_end_legal` is `None` (unknown) rather than True. The mechanical consequence is pre-decided:
     only an explicit **False** (a file that MEASURES an unwired Required input on one of the three) forces
     33(d)'s stop; UNKNOWN leaves the branch to 32(d)'s scaffold rule, and the open question goes to judgement
     with its evidence beside it.

THE SHAPE IS FIXED (31(b)); THE SCAFFOLD ROUTE IS SELECTED MECHANICALLY FROM A3's TABLE (32(d))
--------------------------------------------------------------------------------------------------
30(e) decided all four branches in advance and 31(b) fixes the SHAPE to **branch 1**:

  **movein** — `s2` (three While loops on Diagram #686) · `move_in` for `#5058` / `#48` / `#376` · THEN the
               30(f) scaffold on each new loop's conditional terminal (32(b)'s order) · then save.
               Contract: **SubVI 97 THROUGHOUT · WhileLoop 3 -> 6 · Diagram 170 -> 173** (31(h)).

The ONE thing still selected at run time is the SCAFFOLD ROUTE, and 32(d) makes that selection MECHANICAL, from
A3's own table, with no judgement left in it:

  rule (1)  an already-built op that puts a Boolean **constant TRUE** on the **conditional terminal** -> take it;
  rule (2)  else `OpCreateEqual_v0` -> `OpStopFromNode_v0`, **only if** `build_opsentinel_ops_run3.log` F5c/F6
            PROVES the delivered value is constant TRUE;
  rule (3)  else **STOP AFTER PHASE A** and save `tools/bench/s2a_legality.json` — 30(e)'s fourth branch, and a
            legitimate end (it leaves a file and hands judgement a measurement, not a guess).

30(e)'s `redrop_all` and `redrop_subset` remain NOT implemented (32(e) keeps branch 1), and v7's `s1d`/`s2d` are
not re-cut. `stop_after_a` IS implemented, because 32(d) rule (3) requires it: phases C and D are then SKIPPED —
not failed — and the run ends `0 fail` with the DATA artefact on disk.

HARD CONSTRAINTS THIS FILE HOLDS TO (each is a build failure if violated, not a style note)
---------------------------------------------------------------------------------------------
  * `allow_broken=True` is NEVER PASSED (a grep finds it only inside prose like this line and the C8 gate's
    own message — never in an argument list). Every save is `g.save(path)` with the default, so the `gui_save` divert
    (`gscript.py:2066-2067`) is impossible BY CONSTRUCTION (29(d), 30(g)).
  * A stage that cannot end legal **saves the DATA file and says so in this log** — it does not save a broken VI
    and it does not pretend it saved one (30(g), 31(i)).
  * The temporary conditional-terminal scaffold must deliver **`True`**, NEVER `False` (30(f) as read by
    31(e): the requirement is on the VALUE DELIVERED, not on the object being a literal constant).
  * 🔴 **`gscript.exit_while` IS NEVER CALLED and no ORIGINAL front-panel control is wired into a new loop**
    (32(a)). `SCAFFOLD_STOP_CONTROL` is never ASSIGNED and never READ here — it survives only inside these
    comments, which say why it was overturned.
  * **`#5058` is the CPU kernel `Track N beads four-fold over-kernel-v3.vi`** (31(a)) — gate C2k FAILS the
    stage if the artefact says otherwise, and no log line here names `GPU_kernel_v1.vi`.
  * `gscript.net_map` is BANNED (Pre-decided 17) and is not imported.
  * The ORIGINAL is only ever COPIED and opened READ-ONLY; **md5(ORIGINAL) is re-asserted after EVERY phase**
    and at the end (rule 1, fatal).
  * The S1 ARTEFACT is gated against md5 `3e3d23cefd3a334001aa9d6156bf1aee` BEFORE any edit, and is never
    written to: phase C works on a COPY of it (30(c)).
  * Every reference opened is closed; `g.ref_counts()` is printed at the END OF EVERY PHASE (CLAUDE.md §3).
  * **THE ONLY RESULT-DEPENDENT STEP IS 32(d)'s SELECTION RULE**, and it is written down in advance, applied by
    code, and reported: the SHAPE never branches (31(b)), only the scaffold route does, between the three
    outcomes 32(d) enumerates. Nothing else in this file reads a measurement to choose a code path.

PREDICTION CONTRACT (every number written before execution)
------------------------------------------------------------
 S0   md5(ORIGINAL) == `2a78e17c449cacdaf5da389818526859`.
 A0   md5(S1 artefact) == `3e3d23cefd3a334001aa9d6156bf1aee`, size 474202 B.
 A1   `a1_move_in_reaches_new_loop_bodies` RECORDED TRUE with its citation (31(b)); the echo predicates P1/P2/P4
      TRUE and P3 counts **21** archived `S3 … -> owner Diagram#… WhileLoop#…` PASS lines.
 A1x  `#5058` / `#48` / `#376` are **NOT** among those 21: v7 ran them through `s1d`/`s2d` instead
      (`build_d1_routeb_v7_run10.log:53-63`, `:90-106`). RECORDED; 32(e) has already ruled that this does NOT
      send S2 back to delete-and-re-drop, so it is a recording and not a rider any more.
 A2   three connector panes read without raising; `a2_required_readable` FALSE. **NOT moot** (33(c) withdraws
      31(c)); the readings feed A5.
 A3   **PREDICTED, FROM THE FILES READ WHILE WRITING THIS (so a different outcome is a FAILED PREDICTION and
      triggers the mandatory peer review, CLAUDE.md §5):**
        * the table carries **16** rows — the **14** the live completeness scan (whole lines) names, plus
          `OpConnectNested_v1` and `OpConnectFromWire_v0`, whose capability rows (`:68`, `:70`) match neither
          scan keyword — so `uncovered` is EMPTY and gate `A3-complete` PASSES (it FAILED before this round:
          the table held 10 and the scan named `OpForLoop_v0` / `OpWhileLoop_v0` that nothing covered, which
          made `main()` return 1 against a `0 FAIL` contract);
        * exactly **two** built ops write a While loop's conditional terminal — `OpExitWhile_v0`
          (`docs/toolkit-capabilities.md:31`) and `OpStopFromNode_v0` (`:63`); the other twelve do not;
        * `OpExitWhile_v0` is **REFUSED by 32(a)** (panel control by name, `gscript.py:1083-1114`);
        * `OpStopFromNode_v0`'s source is a **body node's `Terminals[]`**, so what it delivers is whatever that
          node delivers — a constant only if a constant can BE that source, and `Nodes[]` is MEASURED to
          EXCLUDE constants (`archive/2026-09-18-status-cycle19-flatseq.md:87`,
          `docs/frame-loop-wire-graph.md:460`, `docs/d1-build-plan.md:998`)
          (`OpCreateConst_v0`'s value is MEASURED EMPTY, `:65`; `OpCreateConstOnTerm_v0` carries its value but
          addresses a **body node terminal**, `:66`, never the conditional terminal);
        * the six candidates added in this round do not change that: `OpConstValueN_v1` (`:59`) and
          `OpWireSource_v5` (`:60`) are **READERS**, `OpExitLoop_v0` creates auto-indexed OUTPUT TUNNELS
          (`gscript.py:1721-1753`), `OpBuildCase_v0` creates a Case structure and its `Selector` cannot even be
          written (`docs/NAMES.md:482-494`), and `OpForLoop_v0` / `OpWhileLoop_v0` CREATE loops and leave the
          conditional terminal unwired by construction (`:30`);
        * ⇒ **rule (1) STILL has NO winner, re-derived over all 14**;
        * `build_opsentinel_ops_run3.log` F5c/F6 record the WIRE (`term 119, wire 0 -> 387`) and `ExecState 1`
          and **no value read-back at all** ⇒ the Equal?'s delivered value is **NOT provable** from that record
          ⇒ **rule (2) does not qualify**;
        * ⇒ **32(d) rule (3): `branch = stop_after_a`, phases C and D are SKIPPED, `s2a_legality.json` is the
          product of this run, and the run ends with 0 FAIL.** This is the predicted outcome of `--phases ACD`.
 A4   md5 matches the pin; the cited ExecState pair is (COLD 1, PRELOADED 1). NO ExecState is read here (31(f)).
 A5   33(c): `a5_lands_unwired` **TRUE**, MEASURED and cited (`docs/d1-route-b-plan.md:57-58`, `:67` — both
      greps non-empty, so the citation is machine-checked); `a5_required_follows` **UNKNOWN** (no built op
      reads the flag; the only recorded route is an EDIT, forbidden in phase A); `a5_stage_can_end_legal`
      **None**. Because it is UNKNOWN and not False, A5 does NOT itself force 33(d)'s stop — 32(d) rule (3)
      does, below — and the question is reported for judgement.
 C1   the S2 working copy on disk is byte-identical to the S1 ARTEFACT.
 C2k  the VI name at uid 5058 on the working copy is **`Track N beads four-fold over-kernel-v3.vi`** (31(a)).
      FATAL.
 C3   BEFORE census, GATED: Diagram 170 · Node 624 · Wire 1899 · WhileLoop 3 · SubVI 97 · Function 180
      (S1's own AFTER, `stage_d1_s1.py:241` + `build_d1_routeb_v7.py:72-75`). RECORDED, NOT GATED:
      LoopTunnel · ControlTerminal · Local — S1 never gated them after its deletions, so no number is pinned.
 C4   three loops created (+1 Diagram and +1 WhileLoop each); `#637` still exists and still owns `#6810`,
      `#22082`, `#12589`, `#11639`, `ControlTerminal #642` (v7 `s2` `:805-811`); **then** three `move_in`
      landings (32(b)'s order), each gated on `uid -> body Diagram -> WhileLoop`.
 C5   AFTER census: **WhileLoop 6 · Diagram 173 · SubVI 97** (31(h)).
 C6   **AFTER the moves** (32(b)): each new loop's conditional terminal reads a NON-ZERO `CondWireUID` on the
      SAME `CondTermUID` through `OpLoopEndRef_v0`, by the route 32(d) selected (30(f)) — **AND** that wire
      uid is the SAME uid the driving Comparison's own source terminal carries (wire identity on both ends,
      the project's standard proof), **AND** the whole VI reads `ExecState 1` before the save (C8). A non-zero
      `CondWireUID` ALONE is NOT accepted any more: a Boolean-ARRAY comparison wired onto a stop terminal is
      wired and wrong, and that is what the old gate would have passed (round-2 review, `already-failed`).
 C6s  the operand the scaffold compares is chosen by a PROVABILITY rule, never by ordinal: only a terminal
      listed in `PROVEN_SCALAR_BOOLEAN_OUTPUT` (measured, and EMPTY for all three nodes) qualifies, and a
      name-shaped array/cluster/error terminal is refused outright. `#5058`'s first named source terminal is
      **t3 `Bead is good? array out`** (`docs/frame-loop-wire-graph.md:171`) — an ARRAY, so `outs[0][1]` would
      have compared arrays and delivered a Boolean ARRAY.
 C6b  no PRE-EXISTING `ControlTerminal` was MOVED into a new loop body anywhere in the stage. Under 32(a) the
      scaffold cannot read a panel control at all, so this is now a check that nothing else did either.
 D6   32(f) as corrected by **33(a)**: the IndexMode of every LoopTunnel created by this stage, read with the
      BUILT `gscript.tunnels` (`OpTunnels_v0`). The answer to "can any built op read it" is **YES**, and the
      PREDICTED number of such tunnels is **ZERO** — a move severs wires instead of tunnelling them, so the
      log says plainly that nothing was created and nothing was read, and D6 contributes NO gate in that case.
 C8   **NEW, FATAL**: with the ORIGINAL preloaded, `exec_state(target)` is **1** BEFORE `g.save` is called.
      This is what catches a conditional terminal that is wired but wrong-typed; C9 is then only the save.
 C9   `g.save(target)` returns without raising => `claudeDev\D1_s2_loops.vi` EXISTS with its md5, size and
      version bytes in this log.
 D1   the artefact read COLD in a fresh instance — RECORDED, not gated (14a).
 D2   the artefact read with the ORIGINAL PRELOADED = **1**. FATAL; this is the stage's pass criterion.
 D5   the artefact's COLD SubVI table against **the ORIGINAL's** (29(g)), one condition per child process and
      per LabVIEW instance: 97 rows vs 98; the three relocated keys are gone from `Diagram #639` and reappear,
      **with the same node uid and the same path** (a move preserves both), inside the new loop bodies; zero
      rows into `claudeDev\background VIs_COPY\`; no empty name or path.
 D4/S6  md5(ORIGINAL) still equals the pin.
GATE COUNTS, written before the run (RE-COUNTED 2026-09-20 against the edited file, gate call by gate call):
  * `--phases A` (or `--phases ACD` ending at 32(d) rule (3), THE PREDICTED OUTCOME) reads **17 PASS / 0 FAIL**:
    S0 · A0 · A1x (nf) · A1 · A2×3 (nf) · A3-complete (nf) · A3-32a · A3 · A4-0a (nf) · A4-0b (nf) ·
    **A5-cut (nf)** · **A5-legality (nf)** · MD5-A · S6 (nf) · S6b (nf). Phases C and D are SKIPPED with a
    `PHASE C/D SKIPPED` fact and NO gate of their own — a skipped stage is not a failed one (32(d)).
  * `--phases ACD` if — contrary to the A3 prediction above — a route DOES qualify, adds the stage's own gates:
    phase C = C0 · C1a · C1 · C3 · C2k (5) · C4 loop-created ×3 · C4b · C4c (#637) · C4c ×5 (nf) (10) ·
    C4 move_in ×3 · C4 SubVI-unchanged (4) · per loop ×3 {route · named-output-at-all ·
    **C6s operand provably scalar-Boolean** · one-new-Comparison · Nodes[]-addressable · source-terminal · C6 ·
    **C6w wire identity**} = 8×3 (24) · C6b · C5 · **C8 ExecState 1** · C9 (4) · MD5-C (1) = **48**;
    phase D = D2 · D5-i (nf) · D5-ii (nf) · D5a-d (nf, 4) · D5 FATAL · MD5-D = **9** (D6 adds a tenth ONLY if a
    LoopTunnel was created, which 33(a) predicts will not happen). Total **17 + 48 + 9 = 74 PASS / 0 FAIL**.
    Counted from the file's own `gate(` call sites, not from memory. That branch is NOT predicted; if it is
    taken, the A3 prediction above was wrong and the failed-prediction review is owed before anything is built
    on it.
Rule 1: the ORIGINAL is only ever COPIED and opened READ-ONLY. Rule 1a: this stage adds three loops the original
does not have and relocates three of OUR OWN call sites; no per-bead maths and no original wire is changed.
No VI is run; no motor, no ASI and no camera is touched; no GUI action is taken.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g                                                              # noqa: E402
from bench_prep import labview_handles                                           # noqa: E402
import build_d1_v0 as D1                                                         # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index, wmap, terms_of            # noqa: E402
import s1_subvi_paths as T1                                                      # noqa: E402  (the BUILT census)
import diag_d1_execstate_preload as D1ES                                         # noqa: E402  (the BUILT helper)

# ---------------------------------------------------------------------------- constants, all measured
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"          # stage_d1_s1.py:227
CLAUDEDEV = g.CLAUDEDEV
BENCH = os.path.join(ROOT, "tools", "bench")

# 30(c): the INPUT is S1's artefact, gated against its md5 before any edit; the OUTPUT is D1_s2_loops.vi.
S1_ARTEFACT = os.path.join(CLAUDEDEV, "D1_s1_copy.vi")
S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"            # STATUS owner_c48s1cd; stage_d1_s1_cd.log:306
S1_SIZE = 474202
TARGET = os.path.join(CLAUDEDEV, "D1_s2_loops.vi")     # THE STAGE ARTEFACT

OUT_A = os.path.join(BENCH, "s2a_legality.json")       # 30(d): phase A's DATA artefact
OUT_READINGS = os.path.join(BENCH, "s2_stage_readings.json")

# v7 `:420-435`, unchanged
SIBLING_DIAG_UID = 686        # the FlatSequenceFrame diagram that HOLDS WhileLoop #637 ("diagram 19")
FRAME_LOOP_UID = 637
FRAME_BODY_UID = 639          # "diagram 43"
CTLTERM_STOP_UID = 642
STAY_ON_11 = [6810, 22082, 12589, 11639]

VILIB = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))     # ...\zz_LabView VI
# 🔴 31(a): uid 5058 is the **CPU** kernel. 30(d) called it `claudeDev\GPU_kernel_v1.vi` and that was WRONG
# (`docs/d1-route-b-plan.md:135`, `docs/d1-build-plan.md:287`, `docs/frame-loop-wire-graph.md:69`, and
# `gscript.subvis`' own docstring `:537`: "kernel uid 5058 = 'Track N beads four-fold over-kernel-v3.vi'").
# Swapping it for the GPU kernel is a LATER stage with its own rule-1a argument; S2 relocates what is there.
CPU_KERNEL = os.path.join(VILIB, "background VIs", "Track N beads four-fold over-kernel-v3.vi")
CPU_KERNEL_NAME = "Track N beads four-fold over-kernel-v3.vi"      # gate C2k reads this off the artefact
ASI_VI = os.path.join(VILIB, "Madcity", "ASI_adjust focus-subvi.vi")
SAVE_VI = os.path.join(VILIB, "background VIs", "save trace.vi")
RELOCATE = {"1.2": (5058, CPU_KERNEL, CPU_KERNEL_NAME),
            "1.5": (48, ASI_VI, "ASI_adjust focus-subvi.vi"),
            "1.7": (376, SAVE_VI, "save trace.vi")}
LOOP_LOCATIONS = {"1.2": (2600, 2600), "1.5": (2600, 3400), "1.7": (2600, 4200)}   # v7 `:793`

# 🔴 32(a): THERE IS NO `SCAFFOLD_STOP_CONTROL` IN THIS FILE ANY MORE, and `gscript.exit_while` is never called.
# The previous material session proceeded under the assumption that the main VI's own `"stop (end)"` control
# could source the three new conditional terminals; judgement OVERTURNED it: `OpExitWhile_v0` sources the
# terminal from a front-panel Boolean BY NAME (`tools/gscript.py:1083-1114`), which delivers the operator's
# value — FALSE at load, the "instrument that hangs" 30(f) forbids — and would add readers of an ORIGINAL
# control in three new places, i.e. the original's wiring rather than scaffolding. The scaffold route is now
# whatever A3's measured table selects under 32(d), and `exit_while` is in that table only to be REFUSED.
REFUSED_ROUTES = {"exit_while": "32(a): panel-control source, FALSE at load, and it would wire an ORIGINAL "
                                "front-panel control into three new loops"}

# 🔴 THE SCAFFOLD'S OPERAND IS NEVER CHOSEN BY ORDINAL (round-2 prior-art review, `already-failed`).
# `scaffold_loop` used to take `outs[0][1]`, the first NAMED source terminal of the relocated node. For
# `#5058` that is **t3 `Bead is good? array out`** (MEASURED, `docs/frame-loop-wire-graph.md:171`; the same
# name appears as a sink on `#5540` t3 at `:174`) — an ARRAY. `Equal?` on two array operands yields a Boolean
# ARRAY, and a Boolean array on a `Stop if True` terminal is a wired-and-wrong VI that the old C6 gate
# (`CondWireUID != 0`) would have passed. Two mechanical filters replace the ordinal:
#   (i)  NON_SCALAR_NAME_RE refuses an array/cluster/error/path/refnum-shaped NAME outright;
#   (ii) what survives must appear in PROVEN_SCALAR_BOOLEAN_OUTPUT[node uid] — terminals whose type is
#        MEASURED scalar Boolean.
# (ii) is EMPTY, and deliberately so: no built op reads a terminal's DATA TYPE (`gscript.node_terms` returns
# name / is_source / wire — `tools/gscript.py:870-924`; `gscript.conpane` returns {index: label} — `:2744-2768`),
# and Pre-decided 2 forbids building the reader. An empty list means the gate FAILS and the stage stops, which
# is the pre-decided honest end (30(g), 31(i)) — never a licence to guess a terminal.
NON_SCALAR_NAME_RE = (r"(?i)array|\[\s*\]|cluster|error|refnum|\bpath\b|image|string|list|buffer|table|"
                      r"\bLUT\b|profile|trace|matrix")
PROVEN_SCALAR_BOOLEAN_OUTPUT = {}      # {node uid: (terminal names,)} — MEASURED only; empty by measurement

# C3: what S1 LEFT. GATED set only — S1 gated SubVI/Function/Node/Wire (stage_d1_s1.py:241) and this stage's own
# contract pins Diagram 170 and WhileLoop 3 (30(a)). LoopTunnel / ControlTerminal / Local were NOT gated after
# S1's deletions, so nothing pins them and they are RECORDED instead of asserted.
BEFORE_S2 = dict(Diagram=170, Node=624, Wire=1899, WhileLoop=3, SubVI=97, Function=180)
RECORD_ONLY = ("LoopTunnel", "ControlTerminal", "Local")
AFTER_S2 = dict(WhileLoop=6, Diagram=173, SubVI=97)                               # 30(a), the NET contract

# 29(g): the ACCEPTANCE REFERENCE is the ORIGINAL's SubVI table, never a copy.
BG_COPY = os.path.join(CLAUDEDEV, "background VIs_COPY")
PIN_SUBVI_ROWS = 98                        # the ORIGINAL's row count (tools/bench/s1_subvi_paths.log)
TIFF_SUBVI_KEY = (FRAME_BODY_UID, 22700)   # the ONE SubVI row S1 already removed

# 32(c): the CANDIDATE SET A3 measures. Every one of these is ALREADY BUILT — nothing here is created, and
# Pre-decided 2 forbids building anything that is missing. `OpLoopEndRef_v0` is the READER that checks the
# scaffold's work (gate C6). `OpExitWhile_v0` is in the set only so the table records WHY it is refused.
OP_MOVEIN = D1.OPIN
OP_EXITWHILE = os.path.join(CLAUDEDEV, "OpExitWhile_v0.vi")
OP_EXITWHILE_LABELS = os.path.join(BENCH, "opexitwhile_labels.json")
OP_LOOP_END_REF = os.path.join(CLAUDEDEV, "OpLoopEndRef_v0.vi")
OP_CONST_ON_TERM = os.path.join(CLAUDEDEV, "OpCreateConstOnTerm_v0.vi")
OP_CONST_ON_TERM_LABELS = os.path.join(BENCH, "opcreateconstonterm_labels.json")
OP_STOP_FROM_NODE = os.path.join(CLAUDEDEV, "OpStopFromNode_v0.vi")
OP_STOP_FROM_NODE_LABELS = os.path.join(BENCH, "opstopfromnode_labels.json")
OP_CREATE_CONST = os.path.join(CLAUDEDEV, "OpCreateConst_v0.vi")
OP_CREATE_CONST_LABELS = os.path.join(BENCH, "opcreate_const_labels.json")
OP_CREATE_EQUAL = os.path.join(CLAUDEDEV, "OpCreateEqual_v0.vi")
OP_CREATE_EQUAL_LABELS = os.path.join(BENCH, "opcreate_equal_labels.json")
OP_LOOP_END_REF_LABELS = os.path.join(BENCH, "oploopendref_labels.json")
OP_CONNECT_NESTED_V0 = os.path.join(CLAUDEDEV, "OpConnectNested_v0.vi")
OP_CONNECT_NESTED_V1 = os.path.join(CLAUDEDEV, "OpConnectNested_v1.vi")
OP_CONNECT_FROM_WIRE = os.path.join(CLAUDEDEV, "OpConnectFromWire_v0.vi")
OP_CONNECT2 = os.path.join(CLAUDEDEV, "OpConnect2_v0.vi")
OP_TUNNELS = os.path.join(CLAUDEDEV, "OpTunnels_v0.vi")                     # 32(f)'s reader
SENTINEL_LOG = os.path.join(BENCH, "build_opsentinel_ops_run3.log")         # 32(d) rule (2)'s ONLY record
CONSTONTERM_LOG = os.path.join(BENCH, "build_opcreateconstonterm_v0.log")
CAPS = os.path.join(ROOT, "docs", "toolkit-capabilities.md")
GSCRIPT_PY = os.path.join(ROOT, "tools", "gscript.py")
D1PLAN = os.path.join(ROOT, "docs", "d1-build-plan.md")
ROUTEB = os.path.join(ROOT, "docs", "d1-route-b-plan.md")
S0DIFF = os.path.join(ROOT, "docs", "s0-diff.md")
RUN10 = os.path.join(BENCH, "build_d1_routeb_v7_run10.log")
# the three files that MEASURE "AbstractDiagram.Nodes[] excludes constants" (round-2 review, `unread-evidence`)
FWG = os.path.join(ROOT, "docs", "frame-loop-wire-graph.md")                # :171 (#5058 t3) and :460
FLATSEQ = os.path.join(ROOT, "archive", "2026-09-18-status-cycle19-flatseq.md")      # :87
NAMESMD = os.path.join(ROOT, "docs", "NAMES.md")                            # :482-494, :564-565
V7 = os.path.join(HERE, "build_d1_routeb_v7.py")    # :131-135 — the stage's REAL blocker, already named

g._run.__defaults__ = (6.0, 180.0)
passes, fails, facts = [], [], []
READINGS = {"original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
            "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5}, "A": {}, "C": {}, "D": {}}


class Stop(Exception):
    pass


# ---------------------------------------------------------------------------- helpers, copied from S1
def gate(name, ok, detail="", fatal=True):
    """Every gate in this file is FATAL by default: the first FAIL stops the chain and leaves its artefacts.
    (stage_d1_s1.py:258-265, verbatim.)"""
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def labview_pid():
    """`stage_d1_s1.py:280-290` verbatim — it only LABELS a reading with the instance it came from."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                           capture_output=True, text=True, timeout=90)
        return int((r.stdout or "").strip() or 0)
    except Exception:                                                             # noqa: BLE001
        return None


def version_bytes(path):
    """CLAUDE.md §1's saved-version audit WITHOUT assuming an offset (`stage_d1_s1.py:293-300`)."""
    with open(path, "rb") as f:
        head = f.read(64)
    hits = [{"offset": m.start(), "bytes": " ".join("%02x" % b for b in m.group(0))}
            for m in re.finditer(rb"(?s).\x00\x80\x00", head)]
    return {"head64_hex": " ".join("%02x" % b for b in head), "version_candidates": hits}


def file_facts(tag, path):
    rec = {"path": path, "exists": os.path.exists(path)}
    if rec["exists"]:
        rec["md5"] = md5(path)
        rec["size"] = os.path.getsize(path)
        rec.update(version_bytes(path))
        fact(f"{tag}: {os.path.basename(path)} md5 {rec['md5']} size {rec['size']} B; "
             f"version candidates {rec['version_candidates']}")
    else:
        fact(f"{tag}: {os.path.basename(path)} IS NOT ON DISK")
    return rec


def fresh(tag):
    """A FRESH LabVIEW instance (standing restart authority), then rebind every cached proxy
    (`stage_d1_s1.py:317-330` verbatim)."""
    g.reset()
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                            capture_output=True, text=True, timeout=600)
        fact(f"{tag}: lv_restart rc={rc.returncode}: {(rc.stdout or '').strip().splitlines()[-1:]}")
    except Exception as e:                                                        # noqa: BLE001
        fact(f"{tag}: lv_restart FAILED ({type(e).__name__}: {e}) — every reading in this phase is weaker for it")
    g.reset()
    fact(f"{tag}: LabVIEW handles after the restart: {labview_handles()} (fresh-instance baseline ~31,500)")


class Preload:
    """`tools/bench/p2_open_copy.py:22-28` verbatim (`stage_d1_s1.py:332-358`): hold the ORIGINAL resident
    READ-ONLY for the duration of a phase. No panel on the original, nothing run, nothing saved. The single COM
    proxy is dropped in `__exit__` — the only name that ever holds it."""

    def __init__(self, tag):
        self.tag = tag
        self.app = None
        self.vi = None

    def __enter__(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        self.app = dynamic.Dispatch("LabVIEW.Application")
        self.vi = self.app.GetVIReference(ORIGINAL, "", False, 0)
        fact(f"{self.tag}: ORIGINAL resident READ-ONLY (LabVIEW {self.app.Version}), its own ExecState "
             f"{int(self.vi.ExecState)}; nothing opened on it, nothing saved")
        return self

    def __exit__(self, *exc):
        self.vi = None
        self.app = None
        fact(f"{self.tag}: preload references released; refs {g.ref_counts()}")
        return False


def dump():
    """Both artefacts are re-written in `main`'s `finally`, so a fatal gate still leaves everything measured up
    to that point on disk (30(g): a stage that cannot end legal still leaves its DATA file)."""
    with open(OUT_A, "w", encoding="utf-8") as f:
        json.dump({k: READINGS[k] for k in ("original", "s1_artefact", "A")}, f, indent=1, default=str)
    with open(OUT_READINGS, "w", encoding="utf-8") as f:
        json.dump(READINGS, f, indent=1, default=str)


def orig_gate(phase):
    """Rule 1, after EVERY phase: the ORIGINAL's md5 still equals the pin. FATAL. (`stage_d1_s1.py:369-373`.)"""
    m = md5(ORIGINAL)
    READINGS.setdefault("md5_after_phase", {})[phase] = m
    gate(f"MD5-{phase} original md5 unchanged after phase {phase}", m == ORIG_MD5, m)


# ---------------------------------------------------------------------------- 29(g): SubVI tables
def cold_subvi_table(tag, target):
    """ONE COLD SubVI-path census of `target`, in ITS OWN CHILD PROCESS and its OWN fresh LabVIEW instance.
    Nothing is read here: this CALLS the BUILT `tools/bench/s1_subvi_paths.py` `run_condition()` (`:183-209`).
    (`stage_d1_s1.py:377-405` verbatim.)"""
    res = T1.run_condition(tag, target)
    rows = res.get("rows", []) or []
    keyed = {(r["diagram_uid"], r["node_uid"]): (r["name"], r["path"]) for r in rows}
    bg = sorted(k for k, v in keyed.items() if str(v[1]).lower().startswith(BG_COPY.lower()))
    empty = sorted(k for k, v in keyed.items() if not str(v[0]).strip() or not str(v[1]).strip())
    rec = {"tag": tag, "target": target, "status": res.get("status"), "child_rc": res.get("child_rc"),
           "n_rows": len(rows), "n_keys": len(keyed), "n_diagrams": res.get("n_diagrams"),
           "n_diagram_errors": len(res.get("diagram_errors", []) or []),
           "into_background_vis_copy": len(bg), "background_vis_copy_keys": bg[:12],
           "empty_rows": len(empty), "empty_keys": empty[:12],
           "restart_rc": res.get("restart_rc"), "ref_counts": res.get("ref_counts"),
           "handles_after_restart": res.get("handles_after_restart"), "handles_end": res.get("handles_end"),
           "child_json": f"tools/bench/s1_paths_{tag}.json"}
    fact(f"{tag}: COLD SubVI census of {os.path.basename(target)} — status {rec['status']!r} rc {rec['child_rc']!r}; "
         f"{rec['n_rows']} rows / {rec['n_keys']} distinct keys over {rec['n_diagrams']!r} diagrams, "
         f"{rec['n_diagram_errors']} diagram errors; into 'background VIs_COPY' {rec['into_background_vis_copy']}; "
         f"empty name-or-path {rec['empty_rows']}; child refs {rec['ref_counts']!r}; "
         f"handles {rec['handles_after_restart']!r} -> {rec['handles_end']!r}; json {rec['child_json']}")
    return keyed, rec


def compare_subvi_tables(got, reference, expect_missing):
    """`got` must be `reference` MINUS `expect_missing`, key-for-key, in BOTH name and path. The ACCEPTANCE
    REFERENCE IS THE ORIGINAL'S TABLE (29(g)). (`stage_d1_s1.py:408-427` verbatim.)"""
    expected = {k: v for k, v in reference.items() if k not in expect_missing}
    missing = sorted(set(expected) - set(got))
    extra = sorted(set(got) - set(expected))
    changed = sorted(k for k in (set(expected) & set(got)) if got[k] != expected[k])
    not_deleted = sorted(k for k in expect_missing if k in got)
    absent_from_reference = sorted(k for k in expect_missing if k not in reference)
    return {"n_reference": len(reference), "n_expected": len(expected), "n_got": len(got),
            "missing": missing, "extra": extra, "changed": changed, "not_deleted": not_deleted,
            "expected_key_absent_from_reference": absent_from_reference,
            "equal": not (missing or extra or changed or not_deleted or absent_from_reference),
            "changed_detail": [{"key": list(k), "reference": list(expected[k]), "got": list(got[k])}
                               for k in changed],
            "missing_detail": [{"key": list(k), "reference": list(expected[k])} for k in missing],
            "extra_detail": [{"key": list(k), "got": list(got[k])} for k in extra]}


def log_table_diff(label, cmp_):
    """The FULL diff, printed line by line, only when a comparison fails (`stage_d1_s1.py:430-447`)."""
    print(f"  --- {label}: FULL DIFF (reference = the ORIGINAL's COLD SubVI table)", flush=True)
    print(f"      reference rows {cmp_['n_reference']} · expected after this stage {cmp_['n_expected']} · "
          f"got {cmp_['n_got']}", flush=True)
    for k in cmp_["not_deleted"]:
        print(f"      NOT-RELOCATED key {k} is still on its old diagram", flush=True)
    for k in cmp_["expected_key_absent_from_reference"]:
        print(f"      BAD-KEY       key {k} does not exist in the ORIGINAL's table at all", flush=True)
    for d in cmp_["missing_detail"]:
        print(f"      MISSING       key {d['key']}  reference name={d['reference'][0]!r} "
              f"path={d['reference'][1]!r}", flush=True)
    for d in cmp_["extra_detail"]:
        print(f"      EXTRA         key {d['key']}  got name={d['got'][0]!r} path={d['got'][1]!r}", flush=True)
    for d in cmp_["changed_detail"]:
        print(f"      CHANGED       key {d['key']}\n"
              f"                      reference name={d['reference'][0]!r} path={d['reference'][1]!r}\n"
              f"                      got       name={d['got'][0]!r} path={d['got'][1]!r}", flush=True)


# ============================================================================== PHASE A — MEASUREMENT ONLY
def _grep(path, pattern, flags=re.I, limit=6, width=400):
    """Every line of `path` matching `pattern`, as `{"line": n, "text": …}`. Read-only, and the ONLY way this
    file turns a document into a machine-checkable predicate — the citation is recorded with its line number so
    the next reader can open it.

    ⚠️ `width` TRUNCATES the recorded text (400 chars keeps the log readable). Any caller that then SEARCHES
    the returned text — A3's completeness scan does — must pass a width big enough to hold the whole row:
    `docs/toolkit-capabilities.md`'s rows run to several thousand characters, and at 400 the scan silently
    missed rows `:63` `:64` `:67` and the six ops named only in them (MEASURED 2026-09-20)."""
    out = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for i, ln in enumerate(f, 1):
                if re.search(pattern, ln, flags):
                    out.append({"line": i, "text": ln.rstrip()[:width]})
                    if len(out) >= limit:
                        break
    except OSError as e:
        out.append({"line": 0, "text": f"<unreadable: {type(e).__name__}: {e}>"})
    return out


def a1_move_in():
    """A1 (31(b)) — SETTLED, NOT MEASURED. `move_in` already lands nodes into loop bodies created in the SAME
    run; this RECORDS that answer with its citation. The one thing still READ from the archive is A1x: were the
    three call sites among those landings, or were they EXCLUDED, and why."""
    print("\n--- A1: RECORD the settled answer (31(b)), and read A1x out of v7 run 10", flush=True)
    rec = {"settled_by": "docs/cycle27-plan.md Pre-decided 31(b), cycle 49, 2026-09-20",
           "citation": ["tools/bench/build_d1_routeb_v7_run10.log:116-173 (the 21 landings)",
                        "tools/bench/build_d1_routeb_v7_run10.log:70-76 (the loops they landed in, created in "
                        "the SAME run)",
                        "docs/d1-build-plan.md:873"],
           "a1_move_in_reaches_new_loop_bodies": True,
           "measured_here": False}
    # --- the cheap consistency echo. It CANNOT overturn 31(b); it only says the fleet still looks like this.
    rec["P1_opmovein_on_disk"] = {"path": OP_MOVEIN, "exists": os.path.isfile(OP_MOVEIN)}
    try:
        import inspect
        params = list(inspect.signature(move_in).parameters)
    except Exception as e:                                                        # noqa: BLE001
        params = [f"<{type(e).__name__}: {e}>"]
    rec["P2_dest_diagram_index"] = {"signature": params, "ok": "dest_diagram_index" in params,
                                    "callee": "tools/recipes/build_d1_v0.py:318-335"}
    pass_rows = _grep(RUN10, r"^\s*PASS\s+S3 #\d+ -> \d+\.\d+\s+owner Diagram#\d+ .*WhileLoop#\d+", limit=64)
    rec["P3_archived_landings"] = {"log": "tools/bench/build_d1_routeb_v7_run10.log",
                                   "n_pass_lines_found": len(pass_rows), "sample": pass_rows[:3],
                                   "expected": 21, "deciding": False}
    p4 = _grep(D1PLAN, r"move_in.*UID to GObject Reference|class never enters", limit=3)
    rec["P4_class_agnostic_citation"] = {"doc": "docs/d1-build-plan.md", "hits": p4, "ok": bool(p4)}
    fact(f"A1 SETTLED by 31(b): a1_move_in_reaches_new_loop_bodies = True, cited not measured. Echo: "
         f"OpMoveIn_v0 on disk {rec['P1_opmovein_on_disk']['exists']} · dest_diagram_index "
         f"{rec['P2_dest_diagram_index']['ok']} · {len(pass_rows)} archived S3 landing PASS lines (want 21) · "
         f"class-agnostic citation {rec['P4_class_agnostic_citation']['ok']}")

    # --- A1x: were #5058 / #48 / #376 among the 21, or EXCLUDED with a stated reason? (31(b), the only read.)
    moved_uids = sorted({int(m.group(1)) for r_ in pass_rows
                         for m in [re.search(r"S3 #(\d+)", r_["text"])] if m})
    three = sorted(int(v[0]) for v in RELOCATE.values())
    among = sorted(set(three) & set(moved_uids))
    excluded = sorted(set(three) - set(moved_uids))
    reason = _grep(RUN10, r"^===\s*S1d:.*#5058", limit=2) + _grep(RUN10, r"^===\s*S2d:", limit=2)
    plan_reason = _grep(ROUTEB, r"re-DROPPED fresh|dropped fresh|not moved", limit=4)
    rec["A1x_the_three_in_v7_run10"] = {
        "question": "31(b): were #5058 / #48 / #376 among the 21 move_in landings, or EXCLUDED?",
        "n_landed_uids": len(moved_uids), "landed_uids": moved_uids,
        "the_three": three, "among_the_21": among, "excluded": excluded,
        "v7_stated_reason_lines": reason, "plan_lines": plan_reason,
        "deciding_here": False,
        "for_judgement": "31(b): an exclusion WITH A STATED CAUSE is the only thing that can send S2 back to "
                         "the delete-and-re-drop shape. A material session measures and does not take the "
                         "result-dependent action (CLAUDE.md §3), so this is RECORDED and reported, the branch "
                         "stays `movein` as 31(b) fixes it, and the call is judgement's."}
    fact(f"A1x the three call sites {three}: among the 21 move_in landings = {among}; EXCLUDED = {excluded}. "
         f"v7's stated reason: {[r_['text'] for r_ in reason]}")
    gate("A1x the three call sites' treatment in v7 run 10 is RECORDED (non-fatal — acting on it is judgement's)",
         True, f"among {among}, excluded {excluded}", fatal=False)

    # RECORDED, NOT DECIDING — what a move does to wires. 🔴 33(a): the two citations that used to sit here
    # were DEAD. `docs/s0-diff.md:46` is the D22 ERROR-NEUTRALISER row (it says `move_in` force-feeds a
    # neutralised `error in`, which is true and is NOT the claim), and `_grep(D1PLAN, "a move CUTS")` matched
    # NOTHING anywhere in `docs/`, so it shipped empty. The real, MEASURED evidence that a move severs wires is
    # route A's own re-wire ledger.
    cut_109 = _grep(ROUTEB, r"109 cut terminals|cut_terminals 109", limit=2)
    cut_32 = _grep(ROUTEB, r"rows belonging to `#5058`", limit=2)
    neutraliser = _grep(S0DIFF, r"`move_in` does the same", limit=2)
    rec["wire_behaviour"] = {
        "move_in": {"claim": "a move SEVERS the moved object's wires; the node lands in the new body UNWIRED, "
                             "and moving it back does not restore them",
                    "measured_citations": {
                        "docs/d1-route-b-plan.md:57-58 (109 cut terminals over 24 uids, from "
                        "d1_rewire_sources.json)": cut_109,
                        "docs/d1-route-b-plan.md:67 (32 of those 109 belong to #5058 / #48 / #376)": cut_32,
                        "docs/s0-diff.md:46 — the D22 row, cited ONLY for the neutralised `error in` "
                        "(build_d1_v0.py:328-331), which is all it says": neutraliser},
                    "note": "the cut rows are captured into the S3w re-wire list by `movein_three`",
                    "supersedes": "32(f)'s 'turns each crossing wire into a While-loop tunnel … values pass "
                                  "through unchanged', which 33(a) marks FALSE"}}
    fact(f"A1 33(a) a move SEVERS wires — MEASURED: {[r['text'][:120] for r in cut_109]} | "
         f"{[r['text'][:120] for r in cut_32]}. No tunnel is created by a move, so phase D's 32(f) reading is "
         f"predicted to find ZERO new LoopTunnels.")
    gate("A1 the settled answer is recorded with its citation (31(b))",
         rec["a1_move_in_reaches_new_loop_bodies"] is True,
         f"a1_move_in_reaches_new_loop_bodies = {rec['a1_move_in_reaches_new_loop_bodies']}, cited "
         f"{rec['citation'][0]}")
    return rec


def a2_conpanes():
    """A2 — 🔴 **NOT MOOT. 31(c) IS WITHDRAWN BY 33(c).** A `move_in` severs the node's wires (33(a)), so a
    relocated node lands UNWIRED exactly as a freshly dropped one would and Required-ness bites under branch 1
    too. The panes and the live call-site terminals are READ (read-only) and handed to **A5**, which is where
    33(c)'s legality question is answered from already-measured files. A2 still selects no SHAPE — 31(b) fixed
    that to branch 1 — but it is no longer a recording that decides nothing."""
    print("\n--- A2: LOAD-BEARING AGAIN (33(c) withdraws 31(c)'s 'moot') — the panes feed A5", flush=True)
    rec = {"vis": {}, "call_sites": {}}
    for row, (uid, path, label) in RELOCATE.items():
        r = {"row": row, "uid": uid, "path": path, "exists": os.path.isfile(path)}
        try:
            r["conpane"] = {str(k): v for k, v in g.conpane(path).items()}
            r["n_terminals"] = len(r["conpane"])
            r["n_free"] = sum(1 for v in r["conpane"].values() if v in (None, ""))
            r["error"] = None
        except Exception as e:                                                    # noqa: BLE001
            r["conpane"], r["n_terminals"], r["n_free"] = None, None, None
            r["error"] = f"{type(e).__name__}: {e}"
        rec["vis"][row] = r
        fact(f"A2 {row} #{uid} {label}: on disk {r['exists']}; connector pane "
             f"{r['n_terminals']} terminals, {r['n_free']} free; error {r['error']!r}; {r['conpane']}")
        gate(f"A2 {row} the connector pane of {label} was READ", r["error"] is None and r["conpane"] is not None,
             str(r["error"]), fatal=False)
    # the call-site view: what the node carries TODAY on the frame body of the S1 artefact.
    try:
        d43 = diag_index(S1_ARTEFACT, FRAME_BODY_UID)
        wmap(S1_ARTEFACT, d43, fresh=True)
        for row, (uid, _p, label) in RELOCATE.items():
            t = terms_of(S1_ARTEFACT, d43, uid)
            rows = [{"i": i, "name": nm, "is_source": bool(src), "wire": w} for i, (nm, src, w) in sorted(t.items())]
            rec["call_sites"][row] = {"uid": uid, "diagram_uid": FRAME_BODY_UID, "diagram_index": d43,
                                      "n_terminals": len(rows), "n_wired": sum(1 for r_ in rows if r_["wire"]),
                                      "terminals": rows}
            fact(f"A2 {row} #{uid} {label} at its CALL SITE on Diagram#{FRAME_BODY_UID}[{d43}]: {len(rows)} "
                 f"terminals, {sum(1 for r_ in rows if r_['wire'])} wired")
    except Exception as e:                                                        # noqa: BLE001
        rec["call_sites"]["error"] = f"{type(e).__name__}: {e}"
        fact(f"A2 the call-site terminal read FAILED ({type(e).__name__}: {e}) — recorded, not fatal; the "
             f"connector-pane read above is the part 30(e) branches on")
    # 31(c): the fail-closed reading stays TRUE as a statement about the fleet, and is NO LONGER LOAD-BEARING.
    rec["required_readers_searched"] = {
        "docs/toolkit-capabilities.md": _grep(CAPS, r"Required\?|Terminal Required|Recommended|data type of a terminal",
                                              limit=6),
        "gscript.conpane": "tools/gscript.py:2744-2768 — returns {terminal index: control label}, None for a FREE "
                           "terminal, and nothing else",
        "gscript.node_terms": "tools/gscript.py:870-924 — returns name / is_source / wire, no type and no "
                              "Required flag",
        "the only recorded route": "a BY-EFFECT probe that DROPS the subVI and reads ExecState "
                                   "(docs/NAMES.md:564-565, tools/recipes/build_harness_gpu2.py) — an EDIT, "
                                   "which 30(d) forbids in phase A. Building the reader is forbidden by "
                                   "Pre-decided 2"}
    # 31(c): the files that ALREADY answer requiredness for the input that matters — CITED, not probed.
    rec["already_answered_by"] = {
        "docs/d1-route-b-plan.md:148": _grep(ROUTEB, r"diagram index.*loop body is legal", limit=1),
        "docs/d1-route-b-plan.md:154,158-159": _grep(ROUTEB, r"typed by the sink|already wired", limit=3),
        "docs/d1-build-plan.md:523-536": _grep(D1PLAN, r"None exists on `?#?5058|REQUIRED.*Function", limit=3),
        "docs/NAMES.md:564-565": "the by-effect requiredness measurement of 2026-09-09"}
    rec["a2_required_readable"] = False
    rec["a2_moot_under_branch_1"] = False          # 🔴 33(c): 31(c)'s "moot" is WITHDRAWN
    rec["a2_moot_withdrawn_by"] = ("docs/cycle27-plan.md Pre-decided 33(c), cycle 49, 2026-09-20 — a move "
                                   "severs wires (33(a)), so the relocated node lands UNWIRED and "
                                   "Required-ness bites under branch 1 as well")
    rec["a2_selects_a_branch"] = False             # the SHAPE is 31(b)'s; A2 feeds A5, it does not branch
    rec["a2_feeds"] = "A5 (33(c)): the legality question is answered there, from already-measured files"
    fact("A2 NOT MOOT any more (33(c) withdraws 31(c)): a move severs wires, so the three land UNWIRED and "
         "Required-ness is load-bearing again. `a2_required_readable` is still False — no built op reads the "
         "flag and Pre-decided 2 forbids building the reader — so the panes read here are handed to A5 rather "
         "than used to select anything. The files that already bear on it are cited in `already_answered_by`.")
    return rec


def _op_row(name, vi_path, labels_path, inputs, addresses, writes_cond_term_claim, delivers_constant,
            value_can_be_true, why, evidence_greps, python_api=None):
    """One row of A3's table (32(c)): exact inputs · what it ADDRESSES · whether the Boolean it delivers is a
    CONSTANT and whether that value can be set TRUE by this op or by another already-built op · the measured
    evidence line, GREPPED LIVE so the citation is checked rather than asserted.

    `writes_cond_term_claim` is only the hand-written claim; the value the selection rule uses is
    `writes_conditional_terminal`, DERIVED below from the op's own capability row.

    ⚠️ The derivation is a KEYWORD heuristic (row marked WRITER **and** naming a conditional terminal) and it
    has a MEASURED false positive: `OpWhileLoop_v0`'s row names the conditional terminal as the thing it
    LEAVES UNWIRED (`docs/toolkit-capabilities.md:30`), so `derived` comes back True while the claim is False.
    The disagreement is recorded in `claim_matches_capability_row` rather than hidden, and it cannot select a
    route, because 32(d) rule (1) also requires `delivers_constant` AND `value_can_be_TRUE`."""
    cap = _grep(CAPS, re.escape(name), limit=2)
    cap_text = " ".join(r["text"] for r in cap)
    derived = bool(re.search(r"conditional terminal", cap_text, re.I)) and bool(
        re.search(r"WRITER", cap_text))
    row = {"op": name, "path": vi_path, "on_disk": os.path.isfile(vi_path),
           "labels_json": labels_path, "labels_present": bool(labels_path) and os.path.isfile(labels_path),
           "python_api": python_api,
           "inputs": inputs,
           "addresses": addresses,
           "writes_conditional_terminal": derived,
           "writes_conditional_terminal_claimed": writes_cond_term_claim,
           "delivers_constant": delivers_constant,
           "value_can_be_TRUE": value_can_be_true,
           "why": why,
           "capability_row": cap,
           "evidence": {k: _grep(p, pat, limit=2) for k, (p, pat) in (evidence_greps or {}).items()},
           "refused_by_32a": name == "OpExitWhile_v0"}
    row["claim_matches_capability_row"] = (derived == writes_cond_term_claim)
    return row


def a3_conditional_terminal():
    """A3 (30(d) as rewritten by **32(c)**) — a REAL MEASUREMENT over every built candidate, then **32(d)'s
    selection rule applied mechanically**. Phase A still edits nothing: every reading comes from the op files on
    disk, their label JSONs, `gscript.py` and the archived measurement logs.

    32(a) is enforced here, not merely noted: `OpExitWhile_v0` carries `refused_by_32a=True` and can never be
    selected, whatever the rest of its row says."""
    print("\n--- A3: the candidate table (32(c)), then 32(d)'s selection rule", flush=True)
    rec = {"measured_by": "docs/cycle27-plan.md Pre-decided 32(c)/(d), cycle 49, 2026-09-20",
           "phase_a_edits_nothing": True, "candidates": []}

    rec["candidates"].append(_op_row(
        "OpExitWhile_v0", OP_EXITWHILE, OP_EXITWHILE_LABELS,
        inputs="vi path · Class Name/index (the body node whose outputs become tunnels) · Names · "
               "Class Name 2='Diagram'/index 2 = the loop BODY diagram · Names 2 · <stop_names> = [the "
               "FRONT-PANEL BOOLEAN CONTROL'S NAME]",
        addresses="panel control name (Get Controls -> Index Array -> erdosmiller `Exit While Loop.vi` "
                  "`Stop Condition`) + the loop body diagram",
        writes_cond_term_claim=True,
        delivers_constant=False,
        value_can_be_true=False,
        why="32(a), MEASURED at tools/gscript.py:1083-1114: the source is a front-panel Boolean control BY "
            "NAME, so what arrives at the conditional terminal is the OPERATOR'S value — FALSE at load. No "
            "built op can make a panel control deliver a proven constant TRUE. REFUSED, and refusal is "
            "independent of availability.",
        evidence_greps={"gscript_source": (GSCRIPT_PY, r"front-panel Boolean control labelled"),
                        "test_log": (os.path.join(BENCH, "test_opexitwhile.log"), r"ExecState|PASS")},
        python_api="gscript.exit_while (NEVER CALLED BY THIS FILE — 32(a))"))

    rec["candidates"].append(_op_row(
        "OpStopFromNode_v0", OP_STOP_FROM_NODE, OP_STOP_FROM_NODE_LABELS,
        inputs="vi path · Class Name='WhileLoop'/index = the loop · index 3 = body `Nodes[]` index · "
               "index 4 = that node's `Terminals[]` index -> error out 7",
        addresses="while-loop conditional terminal (SINK, via `WhileLoop.Loop End Ref` 6362C00) sourced from a "
                  "BODY NODE's terminal (`Loop.Diagram` -> `Nodes[]` -> IA -> `Node.Terms[]` -> IA)",
        writes_cond_term_claim=True,
        delivers_constant=False,
        value_can_be_true=False,
        why="it delivers WHATEVER THE SOURCE NODE'S TERMINAL DELIVERS. A constant would have to BE that source, "
            "i.e. be addressable as a body `Nodes[]` index — and **`Nodes[]` is MEASURED TO EXCLUDE "
            "CONSTANTS**: `archive/2026-09-18-status-cycle19-flatseq.md:87` states it outright as the caveat on "
            "a fully sensitive scan, `docs/frame-loop-wire-graph.md:460` classifies 8 of the frame loop's 83 "
            "wires as constant-fed BY ELIMINATION for that reason, and `docs/d1-build-plan.md:998` records the "
            "consequence — `Terminal.Create Constant` 6349C00 exists precisely because a constant cannot be "
            "addressed the way a node can. (This row used to say 'nothing measured in this project shows …', "
            "an assertion of ABSENCE over three files that measure it; round-2 review, `unread-evidence`.) The "
            "one built op that creates a VALUE-CARRYING constant (`OpCreateConstOnTerm_v0`) creates it already "
            "wired to a node terminal and returns a UID, not a `Nodes[]` index. So `delivers_constant` is "
            "FALSE ON MEASUREMENT, not merely unproven, and under 32(d) it is not TRUE either way.",
        evidence_greps={"capability_measured_write": (CAPS, r"term 119, wire 0"),
                        "run3_log": (os.path.join(BENCH, "build_opstopfromnode_v0_run3.log"),
                                     r"T3 the conditional terminal is now WIRED"),
                        "nodes_exclude_constants_1": (FLATSEQ, r"`Nodes\[\]` excludes constants"),
                        "nodes_exclude_constants_2": (FWG, r"constants are not Nodes\[\]"),
                        "nodes_exclude_constants_3": (D1PLAN, r"Create Constant.{0,6}6349C00")},
        python_api="no gscript wrapper; call shape at tools/recipes/build_opstopfromnode_v0.py:443-451"))

    rec["candidates"].append(_op_row(
        "OpCreateConstOnTerm_v0", OP_CONST_ON_TERM, OP_CONST_ON_TERM_LABELS,
        inputs="vi path · Class Name='WhileLoop'/index = the loop · index 3 = body `Nodes[]` index · "
               "index 4 = that node's `Terminals[]` index · Value = the literal -> UID 4, error out 8",
        addresses="a BODY NODE's terminal (`Terminal.Create Constant` 6349C00 invoked on "
                  "`WhileLoop[i].Diagram.Nodes[n].Terminals[t]`) — NOT the conditional terminal",
        writes_cond_term_claim=False,
        delivers_constant=True,
        value_can_be_true=True,
        why="the ONE op whose constant provably carries its value: measured -1 read back through "
            "OpConstValueN_v1, Representation 3, terminal wire 0 -> 176, scratch ExecState 1. Its value input "
            "is real, so TRUE is settable. But it addresses a BODY NODE'S TERMINAL: it cannot put anything on "
            "the conditional terminal, so it fails 32(d) rule (1)'s first condition.",
        evidence_greps={"capability_row_measurement": (CAPS, r"value read back \*\*`-1`"),
                        "build_log": (CONSTONTERM_LOG, r"ExecState|value")},
        python_api="tools/recipes/build_opcreateconstonterm_v0.py:364 create_const_on_term(...)"))

    rec["candidates"].append(_op_row(
        "OpCreateConst_v0", OP_CREATE_CONST, OP_CREATE_CONST_LABELS,
        inputs="vi path · Class Name 2='Diagram'/index 2 = the BODY diagram · location · Type (VARIANT) · "
               "Value (VARIANT)",
        addresses="a diagram (it places a free-standing constant; its `Terminal` output is NOT returned, so the "
                  "constant is placed UNWIRED)",
        writes_cond_term_claim=False,
        delivers_constant=True,
        value_can_be_true=False,
        why="MEASURED FAILURE of the value channel: the VARIANT route produced class `Constant` with an EMPTY "
            "value — it does NOT carry the -1 it was given (same run as OpCreateConstOnTerm_v0's success). A "
            "constant whose value cannot be set cannot be set TRUE, and it is placed unwired with no route to "
            "any sink.",
        evidence_greps={"capability_contrast": (CAPS, r"produced class \*\*`Constant`\*\* with an \*\*EMPTY\*\*"),
                        "sentinel_log": (SENTINEL_LOG, r"F4 REPORTED")},
        python_api="tools/recipes/build_opsentinel_ops.py:387 create_node('const', ...)"))

    rec["candidates"].append(_op_row(
        "OpCreateEqual_v0", OP_CREATE_EQUAL, OP_CREATE_EQUAL_LABELS,
        inputs="vi path · Class Name/index/Names=[x source terminal] · Class Name 2='Diagram'/index 2 = the "
               "BODY diagram · Names 2=[y source terminal] · location",
        addresses="a diagram (it places one `Equal?` Comparison node, both operands wired from OUTPUT TERMINALS "
                  "of one existing node)",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="a comparison of two runtime values is not a constant. It is 32(d) rule (2)'s first half only, and "
            "rule (2) is decided by the F5c/F6 provability check below, not by this row.",
        evidence_greps={"capability_row": (CAPS, r"OpCreateEqual_v0"),
                        "f5_log": (SENTINEL_LOG, r"F5b|F5c")},
        python_api="tools/recipes/build_opsentinel_ops.py:387 create_node('equal', ...)"))

    for nm, pth, lab, addr in (
            ("OpConnectNested_v0", OP_CONNECT_NESTED_V0, os.path.join(BENCH, "opconnectnested_labels.json"),
             "two terminals addressed by `Nodes[]`/`Terminals[]` index on ONE nested diagram"),
            ("OpConnectNested_v1", OP_CONNECT_NESTED_V1, os.path.join(BENCH, "opconnectnested_v1_labels.json"),
             "sink and source `Nodes[]`/`Terminals[]` on DIFFERENT diagrams"),
            ("OpConnectFromWire_v0", OP_CONNECT_FROM_WIRE, os.path.join(BENCH, "opconnectfromwire_v0_labels.json"),
             "sink `Nodes[]`/`Terminals[]`; SOURCE = an existing WIRE's uid + a terminal index on it"),
            ("OpConnect2_v0", OP_CONNECT2, None,
             "sink on a nested diagram by index; SOURCE top-level")):
        rec["candidates"].append(_op_row(
            nm, pth, lab,
            inputs="see the capability row (all are `Terminal.Connect Wire` 6349C03 wrappers)",
            addresses=addr,
            writes_cond_term_claim=False,
            delivers_constant=False,
            value_can_be_true=False,
            why="every one of these addresses its SINK through a node's `Terminals[]`, and the conditional "
                "terminal is exactly 'the thing no node's Terminals[] can reach' "
                "(docs/toolkit-capabilities.md, the OpLoopEndRef_v0 row). They cannot write it at all.",
            evidence_greps={"capability_row": (CAPS, re.escape(nm))}))

    rec["candidates"].append(_op_row(
        "OpLoopEndRef_v0", OP_LOOP_END_REF, OP_LOOP_END_REF_LABELS,
        inputs="vi path · Class Name='WhileLoop' · index -> CondTermUID / IsSource / CondWireUID",
        addresses="while-loop conditional terminal — READ ONLY",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="a READER, not a writer. It is how gate C6 checks whatever the selected route did.",
        evidence_greps={"capability_row": (CAPS, r"OpLoopEndRef_v0")},
        python_api="tools/recipes/build_opstopfromnode_v0.py:340 loop_end_ref(target, loop_index)"))

    # ---- THE SIX THE TABLE USED TO OMIT (round-2 review, `contradicted` #2). The completeness scan names 14
    # ops; the table carried 10, so `uncovered` was non-empty, gate A3-complete FAILED, `fails` grew and
    # `main()` returned 1 against a `0 FAIL` contract. Each of the six is measured here on the same four
    # columns as the rest. 🔴 TWO of them are the shapes 32(d) rule (1) looks for — a value-carrying constant
    # (`OpConstValueN_v1`) and a wire-source writer (`OpWireSource_v5`) — so rule (1) is RE-DERIVED over the
    # full table, not carried over from the incomplete one. Both turn out to be READERS.
    rec["candidates"].append(_op_row(
        "OpConstValueN_v1", os.path.join(CLAUDEDEV, "OpConstValueN_v1.vi"),
        os.path.join(BENCH, "opconstvaluen_v1_labels.json"),
        inputs="vi path · Class Name · index · size? -> value bytes, `Text`, `Representation`, the fed wire's "
               "`UID` (docs/toolkit-capabilities.md:59)",
        addresses="a DiagramNumericConstant addressed by Traverse class+index — READ ONLY",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="it is the project's numeric-constant READER: `Constant.Value` 634AC00 on a "
            "`DigitalNumericConstant`-typed node plus `NumText`/`Representation`. It WRITES NOTHING — it is "
            "how `OpCreateConstOnTerm_v0`'s -1 was read back (`:66`). It appears in the completeness scan only "
            "because rows `:65`/`:66` name it as the reader; it cannot put a value anywhere, so it cannot "
            "satisfy 32(d) rule (1).",
        evidence_greps={"capability_row": (CAPS, r"OpConstValueN_v1"),
                        "read_back": (CAPS, r"value read back \*\*`-1`")},
        python_api="tools/recipes/build_opconstvalue_v1b.py decode_flat (READER)"))

    rec["candidates"].append(_op_row(
        "OpWireSource_v5", os.path.join(CLAUDEDEV, "OpWireSource_v5.vi"),
        os.path.join(BENCH, "opwiresource_v5_labels.json"),
        inputs="vi path · wire `UID` (and `UID 2`, the UID-addressed cast input) · `term index` -> per "
               "terminal: `Is Source?`, reciprocal wire, owner class + owner `UID`, cast-output class",
        addresses="an existing WIRE, by UID — READ ONLY (`UID to GObject Reference.vi` -> cast(`Wire`) -> "
                  "`Wire.Terms[]`)",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="a READER: it answers WHICH OBJECT DRIVES A WIRE (`docs/toolkit-capabilities.md:60`). It creates "
            "nothing and connects nothing, so it cannot deliver a value to a conditional terminal. It is "
            "USEFUL to this stage as a CHECKER — gate C6w reads the scaffold wire's source back with it — and "
            "that is the only role it has here. ⚠️ its caller must set `UID 2`, and "
            "`build_opwiresource_v5.read_terminal` hard-codes the ORIGINAL as `vi path` (`:60`), so the target "
            "is passed explicitly.",
        evidence_greps={"capability_row": (CAPS, r"OpWireSource_v5"),
                        "remeasured_ok": (CAPS, r"RE-MEASURED 2026-09-17 and the op is NOT defective")},
        python_api="tools/recipes/build_opwiresource_v5.py read_terminal (READER; pass the target explicitly)"))

    rec["candidates"].append(_op_row(
        "OpExitLoop_v0", os.path.join(CLAUDEDEV, "OpExitLoop_v0.vi"), None,
        inputs="vi path · Class Name/index = the node inside the loop · Names = its OUTPUT terminal names · "
               "Class Name 2='Diagram'/index 2 = the loop body · Names 2 (`gscript.py:1721-1753`)",
        addresses="a node inside a loop body — it creates AUTO-INDEXED OUTPUT TUNNELS on the loop border",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="erdosmiller `Exit For Loop.vi`: it makes output tunnels, it does not touch a conditional terminal "
            "and it creates no constant. It is in the completeness scan only as the DONOR named in the "
            "`OpCreateEqual_v0` row (`:64`). Measured 2026-08-29: three tunnels + three wires in 0.26 s.",
        evidence_greps={"gscript_source": (GSCRIPT_PY, r"Drives OpExitLoop_v0"),
                        "capability_mention": (CAPS, r"donor `OpExitLoop_v0`")},
        python_api="gscript.exit_loop (tools/gscript.py:1721)"))

    rec["candidates"].append(_op_row(
        "OpBuildCase_v0", os.path.join(CLAUDEDEV, "OpBuildCase_v0.vi"), None,
        inputs="vi path · Class Name/index (Traverse anchor) · location · `Frames` · `Selector` and `Inputs` "
               "(REFNUM controls) — `docs/NAMES.md:484-485`",
        addresses="a diagram: it creates a CASE STRUCTURE (erdosmiller `Create Case Structure.vi`)",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="it builds a Case structure, not a Boolean source, and it is the op the 1055 modal killed: "
            "**never SetControlValue on `Selector`** — writing 0 into that terminal refnum makes the creator "
            "call `Connect Wire` with an invalid reference and a modal dialog blocks the run "
            "(`docs/NAMES.md:487-494`), which is why `OpCreateEqual_v0` fetches its operands INSIDE the op "
            "(`:64`). Superseded by `OpBuildCase_v1`. It cannot write a conditional terminal.",
        evidence_greps={"names_row": (NAMESMD, r"OpBuildCase_v0 \(erdosmiller"),
                        "selector_trap": (NAMESMD, r"Never SetControlValue on `Selector`")},
        python_api="none in gscript; see docs/NAMES.md:482-494"))

    rec["candidates"].append(_op_row(
        "OpWhileLoop_v0", os.path.join(CLAUDEDEV, "OpWhileLoop_v0.vi"), None,
        inputs="target · location · tunnels=[EXISTING PANEL CONTROL labels] · indexing (`:30`)",
        addresses="the TOP-LEVEL diagram: it CREATES a While loop with input tunnels from panel controls",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="its own capability row says it plainly: *'Conditional terminal left unwired -> wire a stop via "
            "the next op'* (`:30`). It is a loop CREATOR, and it leaves exactly the hole this scaffold has to "
            "fill; it cannot fill it. (This stage creates its loops with `loop_in` / `OpWhileLoopIn_v0`, "
            "`:34`, because the loops go on Diagram #686, not the top level.)",
        evidence_greps={"capability_row": (CAPS, r"Conditional terminal left unwired")},
        python_api="gscript.while_loop"))

    rec["candidates"].append(_op_row(
        "OpForLoop_v0", os.path.join(CLAUDEDEV, "OpForLoop_v0.vi"), None,
        inputs="target · location · tunnels · indexing (superseded by `OpForLoop_v1`, `:55`)",
        addresses="the TOP-LEVEL diagram: it CREATES a For loop",
        writes_cond_term_claim=False,
        delivers_constant=False,
        value_can_be_true=False,
        why="a FOR loop has no conditional terminal at all, and this op creates no constant. It is named in "
            "the scan only inside the `OpWhileLoop_v0` row, as the creator that LACKED the `Inputs` fed from "
            "`Get Controls` (`:30`). It cannot satisfy any clause of 32(d).",
        evidence_greps={"capability_row": (CAPS, r"which OpForLoop_v0 lacked")},
        python_api="gscript.for_loop / OpForLoop_v1"))

    # ---- COMPLETENESS, CHECKED BY THE MACHINE (32(c): "and anything else in docs/toolkit-capabilities.md that
    # writes a While loop's conditional terminal or creates a constant"). Scan every capability row that is
    # marked WRITER and names a conditional terminal or a created constant, and diff it against the table.
    # 🔴 `width=100000`: at `_grep`'s default 400 the scan saw only the head of each row, missed `:63` `:64`
    # `:67` entirely and named 5 ops instead of 14 (MEASURED 2026-09-20). The scan must read WHOLE LINES.
    scan = [r for r in _grep(CAPS, r"WRITER", limit=60, width=100000)
            if re.search(r"conditional terminal|Create Constant|CREATE[ _]CONST|creates? a constant", r["text"],
                         re.I)]
    scan_ops = sorted({m.group(0) for r in scan for m in re.finditer(r"Op[A-Za-z0-9_]+_v\d", r["text"])})
    table_ops = sorted({c["op"] for c in rec["candidates"]})
    uncovered = [o for o in scan_ops if o not in table_ops]
    rec["completeness_scan"] = {"doc": "docs/toolkit-capabilities.md",
                                "writer_rows_naming_condterm_or_constant": [r["line"] for r in scan],
                                "ops_named_in_those_rows": scan_ops, "ops_in_the_table": table_ops,
                                "uncovered_by_the_table": uncovered}
    fact(f"A3 completeness scan of docs/toolkit-capabilities.md: WRITER rows naming a conditional terminal or a "
         f"created constant are at lines {[r['line'] for r in scan]}; ops named there {scan_ops}; ops in the "
         f"table {table_ops}; UNCOVERED {uncovered}")
    gate("A3-complete every WRITER row of the capability file that names a conditional terminal or a created "
         "constant is represented in A3's table (32(c))", not uncovered, f"uncovered {uncovered}", fatal=False)

    # ---- 32(d) rule (2): the delivered value must be PROVABLY constant TRUE from THIS record, nowhere else.
    f5c = _grep(SENTINEL_LOG, r"\bF5c\b", limit=4)
    f6 = _grep(SENTINEL_LOG, r"\bF6\b", limit=4)
    both = f5c + f6
    proof = [r for r in both if re.search(r"value[^.]{0,40}\b(true|TRUE)\b|reads? TRUE|constant TRUE|"
                                          r"Boolean value", r["text"])]
    rec["rule2_provability"] = {
        "record": "tools/bench/build_opsentinel_ops_run3.log",
        "F5c_lines": f5c, "F6_lines": f6,
        "lines_that_would_prove_a_constant_TRUE_value": proof,
        "provably_constant_true": bool(proof),
        "reading": "32(d)(2) admits OpCreateEqual_v0 -> OpStopFromNode_v0 ONLY IF the delivered value is "
                   "provably constant TRUE FROM THIS RECORD. F5c records the WIRE (cond terminal 119 -> 119, "
                   "wire 0 -> 387) and F6 records ExecState 1; neither reads the Boolean's VALUE back. A "
                   "comparison whose value is not provable from that record does not qualify."}

    # ---- THE BLOCKER IS NOT NEW, AND OUR OWN FILES NAME A BETTER CAUSE FOR IT (round-2 review,
    # `settled-already`). Recorded beside the table so nobody re-derives it a sixth time.
    rec["scaffold_blocker_already_named"] = {
        "tools/recipes/build_d1_routeb_v7.py:131-135": _grep(V7, r"STATED IN ADVANCE, NOT DISCOVERED "
                                                                 r"AFTERWARDS|sentinel `Equal\?`s depend", limit=3),
        "docs/d1-route-b-plan.md:153": _grep(ROUTEB, r"3 sentinel `Equal\?` \+ 3 sentinel literals", limit=2),
        "reading": "v7 SAID IN ADVANCE that 1.2 / 1.5 / 1.7 keep UNWIRED CONDITIONAL TERMINALS and therefore "
                   "'CANNOT PRODUCE ExecState 1' — and the cause it gives is deeper than 'no op reaches the "
                   "terminal': the three sentinel `Equal?`s depend on QUEUE ELEMENT TYPES THAT WERE NEVER "
                   "DESIGNED (an undesigned row carried in STATUS NEXT). `docs/d1-route-b-plan.md:153` is "
                   "where the scaffold was planned as `OpCreateEqual_v0` + `OpCreateConstOnTerm_v0` (3 "
                   "sentinel `Equal?` + 3 sentinel literals −1). So a scaffold built out of a comparison "
                   "between two runtime values was ALREADY known not to end legal here; that is the same wall "
                   "32(d) rule (2)'s provability test refuses to walk into, reached from the other side.",
        "deciding_here": False}
    fact("A3 the blocker is NOT new: build_d1_routeb_v7.py:131-135 states in advance that these three loops "
         "keep unwired conditional terminals and cannot reach ExecState 1, because the sentinel Equal?s depend "
         "on queue element types that were never designed; docs/d1-route-b-plan.md:153 is where that scaffold "
         "was planned. RECORDED, not acted on (CLAUDE.md §3).")

    # ---- 32(d), applied mechanically. Nothing here is a judgement call; the rule is quoted beside the code.
    rule1 = [c for c in rec["candidates"]
             if c["writes_conditional_terminal"] and not c["refused_by_32a"]
             and c["delivers_constant"] and c["value_can_be_TRUE"]]
    rule2_ok = bool(rec["rule2_provability"]["provably_constant_true"]) and all(
        os.path.isfile(p) for p in (OP_CREATE_EQUAL, OP_STOP_FROM_NODE))
    if rule1:
        rec["a3_selected_route"] = rule1[0]["op"]
        rec["a3_rule_applied"] = "32(d)(1) — an op that puts a Boolean CONSTANT TRUE on the conditional terminal"
    elif rule2_ok:
        rec["a3_selected_route"] = "equal_stopfromnode"
        rec["a3_rule_applied"] = "32(d)(2) — OpCreateEqual_v0 -> OpStopFromNode_v0, its value provable from " \
                                 "build_opsentinel_ops_run3.log F5c/F6"
    else:
        rec["a3_selected_route"] = None
        rec["a3_rule_applied"] = "32(d)(3) — neither qualifies: the stage STOPS after phase A and saves " \
                                 "tools/bench/s2a_legality.json (30(e) branch 4, 31(i))"
    rec["a3_route_exists"] = rec["a3_selected_route"] is not None
    rec["rule1_candidates_that_qualified"] = [c["op"] for c in rule1]

    for c in rec["candidates"]:
        fact(f"A3 {c['op']}: on disk {c['on_disk']}, labels {c['labels_present']} | ADDRESSES {c['addresses']} "
             f"| writes-cond-term {c['writes_conditional_terminal']} (claim {c['writes_conditional_terminal_claimed']}, "
             f"agrees {c['claim_matches_capability_row']}) | delivers constant {c['delivers_constant']} | "
             f"value can be TRUE {c['value_can_be_TRUE']}"
             + (" | REFUSED BY 32(a)" if c["refused_by_32a"] else "")
             + f" | INPUTS {c['inputs']} | {c['why']}")
    fact(f"A3 rule (2) provability from build_opsentinel_ops_run3.log F5c/F6: "
         f"{rec['rule2_provability']['provably_constant_true']} — F5c {[r['text'] for r in f5c]}; "
         f"F6 {[r['text'] for r in f6]}")
    fact(f"A3 32(d) SELECTION: rule-1 qualifiers {rec['rule1_candidates_that_qualified']}; rule-2 ok "
         f"{rule2_ok} => selected route {rec['a3_selected_route']!r} ({rec['a3_rule_applied']})")
    gate("A3-32a OpExitWhile_v0 is refused and is not the selected route",
         rec["a3_selected_route"] != "exit_while",
         f"selected {rec['a3_selected_route']!r}")
    gate("A3 the 32(d) selection rule was applied mechanically over the whole candidate table (>= 14 rows, the "
         "full set the completeness scan names) and its outcome is recorded",
         "a3_rule_applied" in rec and len(rec["candidates"]) >= 14,
         f"{len(rec['candidates'])} candidates; outcome {rec['a3_rule_applied']}")
    return rec


def a4_start_state():
    """A4 (31(f)) — **md5 ONLY.** The ExecState pair is already recorded on this exact md5 at
    `tools/bench/stage_d1_s1_cd.log:153` (COLD 1) and `:155` (PRELOADED 1), and the md5 gate at A0 already
    proves the file has not moved. No child process, no LabVIEW restart, no ExecState read here; the PRELOADED
    state is read anyway inside C/D, where the save route needs it (29(d))."""
    print("\n--- A4: the starting state — md5 only, the ExecState pair CITED (31(f))", flush=True)
    rec = {"file": READINGS["s1_artefact"].get("file"),
           "execstate_cited_not_measured": True,
           "cold": {"value": 1, "citation": "tools/bench/stage_d1_s1_cd.log:153"},
           "preloaded": {"value": 1, "citation": "tools/bench/stage_d1_s1_cd.log:155"},
           "why_not_remeasured": "31(f) `already-measured`: the pair was taken on THIS md5 "
                                 f"({S1_MD5}), and the A0 md5 gate proves the file has not moved. Re-taking it "
                                 "costs two child processes and two LabVIEW restarts for a value already on "
                                 "disk.",
           "helper_left_uncalled": "tools/bench/diag_d1_execstate_preload.py (imported only for its pins)"}
    gate("A4-0a the reused helper preloads THIS ORIGINAL",
         os.path.normcase(os.path.abspath(D1ES.ORIG)) == os.path.normcase(os.path.abspath(ORIGINAL)),
         f"helper ORIG {D1ES.ORIG!r}", fatal=False)
    gate("A4-0b the reused helper pins the same ORIGINAL md5", D1ES.ROUTEB_PINNED_MD5 == ORIG_MD5,
         f"{D1ES.ROUTEB_PINNED_MD5} vs {ORIG_MD5}", fatal=False)
    fact(f"A4 (cold, preloaded) = (1, 1), CITED from stage_d1_s1_cd.log:153/:155 on md5 {S1_MD5}; NOT "
         f"re-measured (31(f)). Phase D re-reads the PRELOADED state of the SAVED artefact, which is the "
         f"reading that decides this stage.")
    return rec


def a5_landing_legality(A):
    """A5 (Pre-decided **33(c)**) — **DOES A `move_in`'d NODE LAND UNWIRED, AND DOES AN UNWIRED *REQUIRED*
    INPUT ON `#5058` / `#48` / `#376` FOLLOW FROM IT?**

    Answered from ALREADY-MEASURED FILES ONLY. This function opens no VI, edits nothing, drops nothing and
    probes nothing: 30(d) keeps phase A read-only and Pre-decided 2 forbids building the reader that would
    settle part 2. It takes A2's pane census as its input (33(c) makes A2 load-bearing again).

    Part 1 is MEASURED and settles: route A's relocation left 109 CUT terminals over 24 uids
    (`docs/d1-route-b-plan.md:57-58`, from `d1_rewire_sources.json`), of which 32 belong to these three
    (`:67`). A move severs; the landing is UNWIRED.

    Part 2 is UNKNOWN and is recorded as UNKNOWN, never as False: no built op reads the
    Required/Recommended/Optional flag (A2), and the one recorded route is a BY-EFFECT probe that drops the
    subVI and reads `ExecState` (`docs/NAMES.md:564-565`, `tools/recipes/build_harness_gpu2.py`) — an EDIT.
    Only an explicit False (a file that MEASURES an unwired Required input on one of the three) forces 33(d)'s
    stop; UNKNOWN leaves the branch to 32(d)'s scaffold rule and goes to judgement as an open question."""
    print("\n--- A5: 33(c) — does a moved node land UNWIRED, and does a bare REQUIRED input follow?", flush=True)
    a2 = A.get("A2") or {}
    cut_109 = _grep(ROUTEB, r"109 cut terminals|cut_terminals 109", limit=2)
    cut_32 = _grep(ROUTEB, r"rows belonging to `#5058`", limit=2)
    neutralised = _grep(S0DIFF, r"`move_in` does the same", limit=1)
    v7_unwired = _grep(V7, r"UNWIRED CONDITIONAL TERMINALS|CANNOT PRODUCE `ExecState 1`", limit=2)
    required_probe = _grep(NAMESMD, r"is REQUIRED\*\* — the VI stays broken|required-input probe", limit=2)
    gpu_extras = _grep(D1PLAN, r"None exists on `#5058`", limit=2)
    wired_now = {row: (a2.get("call_sites", {}).get(row) or {}).get("n_wired")
                 for row in sorted(RELOCATE)}
    rec = {
        "question": "33(c): does a `move_in`'d node land unwired, and does an unwired Required input on "
                    "#5058 / #48 / #376 follow from that?",
        "answered_from": "already-measured files only; phase A edits nothing (30(d))",
        # ---- part 1: MEASURED, and it settles
        "a5_lands_unwired": True,
        "a5_lands_unwired_evidence": {
            "docs/d1-route-b-plan.md:57-58 — 109 cut terminals over 24 uids (d1_rewire_sources.json)": cut_109,
            "docs/d1-route-b-plan.md:67 — 32 of those 109 belong to #5058 / #48 / #376": cut_32,
            "docs/s0-diff.md:46 — the move force-feeds a neutralised `error in` "
            "(build_d1_v0.py:328-331); that is ALL this row says": neutralised},
        "wired_terminals_at_the_call_sites_today": wired_now,
        # ---- part 2: UNKNOWN, and it stays UNKNOWN
        "a5_required_follows": "UNKNOWN",
        "a5_required_readable_by_any_built_op": bool(a2.get("a2_required_readable")),
        "a5_required_evidence": {
            "the only recorded route is an EDIT": "a by-effect probe that DROPS the subVI and reads ExecState "
                                                  "(docs/NAMES.md:564-565, "
                                                  "tools/recipes/build_harness_gpu2.py) — forbidden in phase "
                                                  "A by 30(d), and building a reader is forbidden by "
                                                  "Pre-decided 2",
            "docs/NAMES.md:564-565 — the ONE Required input measured in this hierarchy": required_probe,
            "and it is NOT on #5058's pane": gpu_extras,
            "note": "`IMAQ GetImagePixelPtr`'s `Function` ring is REQUIRED, but it lives INSIDE the GPU "
                    "kernel and `docs/d1-build-plan.md:526` records that none of the GPU kernel's six extra "
                    "pane inputs exists on `#5058` at all. Nothing measured names a Required input on the "
                    "three panes this stage moves — and 'nothing names it' is NOT a measurement that there is "
                    "none, which is exactly why this stays UNKNOWN."},
        "v7_said_these_loops_cannot_reach_execstate_1": v7_unwired,
        # ---- the consequence, pre-decided by 33(c)/(d); this function takes no result-dependent action
        "a5_stage_can_end_legal": None,
        "a5_forces_stop_after_a": False,
        "for_judgement": "33(c)/(d): if the stage cannot end legal in ANY shape, S2 stops after phase A with "
                         "tools/bench/s2a_legality.json and judgement re-cuts the boundary. Part 2 is "
                         "UNREADABLE by this fleet, so this session records UNKNOWN and takes no "
                         "result-dependent action (CLAUDE.md §3). What is already certain and does NOT need "
                         "part 2: a move leaves the node unwired, so S2 cannot restore the 32 cut rows — they "
                         "are S3w's work under either route (33(b))."}
    fact(f"A5 part 1 MEASURED: a move SEVERS wires, so a moved node lands UNWIRED — "
         f"{[r['text'][:110] for r in cut_109]} | {[r['text'][:110] for r in cut_32]}. Wired terminals at the "
         f"three call sites TODAY (A2's read): {wired_now}")
    fact(f"A5 part 2 UNKNOWN: no built op reads Required/Recommended/Optional, and the only recorded route is "
         f"an EDIT (docs/NAMES.md:564-565). a5_stage_can_end_legal = None; it does NOT force 33(d)'s stop, and "
         f"it is reported to judgement. v7's own advance statement about these loops: "
         f"{[r['text'][:110] for r in v7_unwired]}")
    gate("A5-cut 33(c) part 1: the node lands UNWIRED after a move, recorded with LIVE-GREPPED measured "
         "citations (docs/d1-route-b-plan.md:57-58 and :67)",
         rec["a5_lands_unwired"] is True and bool(cut_109) and bool(cut_32),
         f"109-cut hits {len(cut_109)}, 32-row hits {len(cut_32)}", fatal=False)
    gate("A5-legality 33(c) part 2 is recorded as UNKNOWN (never as False) and takes no result-dependent "
         "action; 33(d)'s stop is forced only by an explicit False",
         rec["a5_required_follows"] == "UNKNOWN" and rec["a5_stage_can_end_legal"] is None
         and rec["a5_forces_stop_after_a"] is False,
         f"required_follows={rec['a5_required_follows']}, can_end_legal={rec['a5_stage_can_end_legal']}",
         fatal=False)
    return rec


def phase_a():
    """30(d) as amended by 31(b)/(c)/(f), and by **33(c)** which adds A5 and withdraws A2's 'moot':
    A RECORDING THAT EDITS NOTHING. It copies nothing, opens nothing for
    editing, saves nothing, and its only product is `tools/bench/s2a_legality.json` + this log."""
    print("\n=== PHASE A: RECORD what 31 settled, read A1x. NOTHING IS EDITED, NOTHING IS SAVED.", flush=True)
    fresh("A0")
    READINGS["s1_artefact"]["file"] = file_facts("A0 the S1 artefact, read-only", S1_ARTEFACT)
    gate("A0 the S1 artefact on disk matches its pinned md5 and size",
         READINGS["s1_artefact"]["file"].get("md5") == S1_MD5
         and READINGS["s1_artefact"]["file"].get("size") == S1_SIZE,
         f"{READINGS['s1_artefact']['file'].get('md5')} / {READINGS['s1_artefact']['file'].get('size')} B "
         f"(want {S1_MD5} / {S1_SIZE} B)")
    READINGS["A"]["A1"] = a1_move_in()          # 31(b): reads only archived files, no LabVIEW
    dump()
    with Preload("A-pre"):
        READINGS["A"]["A2"] = a2_conpanes()
        dump()
    READINGS["A"]["A3"] = a3_conditional_terminal()
    dump()
    READINGS["A"]["A4"] = a4_start_state()
    READINGS["A"]["A5"] = a5_landing_legality(READINGS["A"])      # 33(c): the re-opened boundary question
    dump()
    READINGS["A"]["branch"] = select_branch(READINGS["A"])
    fact(f"A DECISION (Pre-decided 30(e), applied mechanically, no judgement in this session): "
         f"branch = {READINGS['A']['branch']['branch']!r} — {READINGS['A']['branch']['why']}")
    dump()
    fact(f"A the DATA artefact is written to {OUT_A}")
    fact(f"A refs at phase end: {g.ref_counts()}; handles {labview_handles()}")
    orig_gate("A")


# ============================================================================== 31(b): THE BRANCH IS FIXED
def select_branch(A):
    """31(b) fixes the SHAPE (`movein`) and 32(e) keeps it; the ONE thing decided at run time is whether a
    scaffold route qualified under **32(d)**. If none did, the branch is `stop_after_a` — 30(e)'s fourth
    branch — and phases C/D are SKIPPED, not failed (32(d): "a legitimate end ... it leaves a file, which is
    what the user's binding rule of 2026-09-19 asks of every cycle").

    🔴 **33(c)/(d) adds ONE more pre-decided stop**: if **A5** returns `a5_stage_can_end_legal is False` — an
    explicit measured False, never an UNKNOWN — the stage stops after A whatever A3 selected, because a bare
    Required input means `ExecState 0` and `gscript.save()` cannot reach `SaveInstrument` at all
    (`gscript.py:2065-2071`). UNKNOWN does NOT stop it: it is reported to judgement and 32(d)'s rule decides.

    A1 is settled, not measured (31(b)); A2 is load-bearing again (33(c)) but still selects no SHAPE."""
    a3 = A.get("A3") or {}
    a5 = A.get("A5") or {}
    route = a3.get("a3_selected_route")
    legal = a5.get("a5_stage_can_end_legal")        # True / False / None(UNKNOWN)
    branch = "movein" if (route and legal is not False) else "stop_after_a"
    if route and legal is False:
        route = None                                # 33(d): the scaffold is irrelevant if nothing can save
    return {"branch": branch, "handled": sorted(RELOCATE) if branch == "movein" else [],
            "scaffold_route": route,
            "a5_stage_can_end_legal": legal,
            "a5_required_follows": a5.get("a5_required_follows"),
            "rule_applied": a3.get("a3_rule_applied"),
            "rule1_qualifiers": a3.get("rule1_candidates_that_qualified"),
            "why": ("30(e) bullet 1, FIXED BY Pre-decided 31(b) and kept by 32(e): `move_in` already lands "
                    "nodes into loop bodies created in the SAME run (21 landings, "
                    "build_d1_routeb_v7_run10.log:116-173 and :70-76; docs/d1-build-plan.md:873). S2 = three "
                    "While loops on Diagram #686, then `move_in` for #5058 / #48 / #376, THEN the 30(f) "
                    "scaffold on each new conditional terminal (32(b)'s order), then save. "
                    f"Scaffold route selected by 32(d): {route!r}."
                    if route else
                    "32(d) rule (3): no already-built op puts a Boolean CONSTANT TRUE on a While loop's "
                    "conditional terminal, and OpCreateEqual_v0 -> OpStopFromNode_v0's delivered value is not "
                    "provable from build_opsentinel_ops_run3.log F5c/F6. The stage therefore STOPS AFTER PHASE "
                    "A and saves tools/bench/s2a_legality.json (30(e) branch 4, 31(i)). No VI is edited, "
                    "nothing is saved under claudeDev, and no op is invented to get past the gate "
                    "(Pre-decided 2)."),
            "contract": {"SubVI": [97, 97], "WhileLoop": [3, 6], "Diagram": [170, 173]}}


# ============================================================================== PHASE C — THE STAGE
def scaffold_loop(tag, row, loop_uid, body_uid, route):
    """30(f): the temporary conditional-terminal scaffold — **run AFTER `move_in` (32(b))**, so the body
    already holds its relocated node and the body-node-addressed routes are reachable.

    🔴 32(a): `OpExitWhile_v0` / `gscript.exit_while` is REFUSED and is never called from here; no ORIGINAL
    front-panel control is wired into a new loop. The route is whatever A3's table selected under 32(d), and
    this function implements exactly the routes 32(d) can select — anything else is a FATAL gate rather than an
    improvisation (Pre-decided 2: no new op)."""
    from build_opstopfromnode_v0 import loop_end_ref as LOOP_END_REF, walk as WALK
    loop_index = [o["uid"] for o in g.report_all(TARGET, "WhileLoop")].index(loop_uid)
    body_index = diag_index(TARGET, body_uid)
    before = LOOP_END_REF(TARGET, loop_index)
    fact(f"{tag} BEFORE: conditional terminal #{before.get('cond_term_uid')}, wire "
         f"{before.get('cond_wire_uid')} (0 is EXPECTED — an unwired conditional terminal IS a broken VI)")
    gate(f"{tag} the scaffold route is one this file implements ({route!r})", route == "equal_stopfromnode",
         f"a3_selected_route = {route!r}. 32(d) can select only a rule-(1) constant-TRUE-on-the-conditional-"
         f"terminal op (none is built) or `equal_stopfromnode`; 32(a) refuses `exit_while`. STOPPING rather "
         f"than improvising (Pre-decided 2: no new op).")

    # ---- 32(d)(2): OpCreateEqual_v0 inside the body, then OpStopFromNode_v0 from its Boolean output.
    from build_opsentinel_ops import create_node as CREATE_NODE
    with open(OP_CREATE_EQUAL_LABELS, encoding="utf-8") as f:
        eq_labels = json.load(f)
    with open(OP_STOP_FROM_NODE_LABELS, encoding="utf-8") as f:
        sfn_labels = json.load(f)
    node_uid = RELOCATE[row][0]
    src_i = [o["uid"] for o in g.report_all(TARGET, "SubVI")].index(node_uid)
    terms = terms_of(TARGET, body_index, node_uid)
    outs = [(i, nm) for i, (nm, src, _w) in sorted(terms.items()) if src and nm and nm != "error out"]
    gate(f"{tag} the relocated node #{node_uid} offers a named output terminal at all",
         bool(outs), f"outputs {outs}")
    # 🔴 THE OPERAND IS CHOSEN BY A PROVABILITY RULE, NEVER BY ORDINAL (round-2 review, `already-failed`).
    # `outs[0][1]` took the FIRST named source terminal: for #5058 that is t3 `Bead is good? array out`
    # (`docs/frame-loop-wire-graph.md:171`), an ARRAY — so `Equal?` would compare two arrays and deliver a
    # Boolean ARRAY, which is wired and WRONG on a stop terminal. Two filters, both mechanical:
    #   (i)  a terminal whose NAME is array/cluster/error/path-shaped is refused outright, and
    #   (ii) what remains must be in PROVEN_SCALAR_BOOLEAN_OUTPUT — the MEASURED list of terminals whose type
    #        is known scalar Boolean. That list is EMPTY: no built op reads a terminal's DATA TYPE
    #        (`gscript.node_terms` returns name / is_source / wire only, `gscript.py:870-924`; `g.conpane`
    #        returns {index: label}, `:2744-2768`), and Pre-decided 2 forbids building the reader.
    # So this gate FAILS rather than guessing — the honest end 30(g)/31(i) prescribe, not an improvisation.
    refused = [(i, nm) for i, nm in outs if re.search(NON_SCALAR_NAME_RE, nm)]
    candidates = [(i, nm) for i, nm in outs
                  if (i, nm) not in refused and nm in PROVEN_SCALAR_BOOLEAN_OUTPUT.get(node_uid, ())]
    fact(f"{tag} C6s operand selection on #{node_uid}: named source terminals {outs}; refused as "
         f"array/cluster/error/path-shaped {refused}; PROVEN scalar-Boolean for this node "
         f"{sorted(PROVEN_SCALAR_BOOLEAN_OUTPUT.get(node_uid, ()))}; qualifying {candidates}")
    gate(f"{tag} C6s the compared operand is PROVABLY a scalar Boolean (never picked by ordinal — "
         f"`outs[0]` here is {outs[0] if outs else None!r})", bool(candidates),
         f"no terminal of #{node_uid} is in PROVEN_SCALAR_BOOLEAN_OUTPUT, which is EMPTY because no built op "
         f"reads a terminal's data type and Pre-decided 2 forbids building that reader. Comparing an ARRAY "
         f"terminal (e.g. #5058 t3 `Bead is good? array out`, docs/frame-loop-wire-graph.md:171) would put a "
         f"Boolean ARRAY on the stop terminal: wired and wrong. STOPPING (30(g)/31(i)).")
    op_name = candidates[0][1]
    t0 = time.time()
    cmp0 = g.uids(TARGET, "Comparison")
    err = CREATE_NODE("equal", eq_labels, TARGET, body_index, (120, 120), src_cls="SubVI", src_index=src_i,
                      src_names=[op_name, op_name])
    new_cmp = g.new_since(TARGET, "Comparison", cmp0)
    fact(f"{tag} OpCreateEqual_v0 on body Diagram#{body_uid}[{body_index}] from #{node_uid}'s {op_name!r} "
         f"(x and y are the SAME terminal, so the comparison is value == itself): op error {err!r}; new "
         f"Comparison {[o['uid'] for o in new_cmp]}")
    gate(f"{tag} exactly one new Comparison node in the body", len(new_cmp) == 1 and not err,
         f"{len(new_cmp)} new, error {err!r}")
    cmp_uid = new_cmp[0]["uid"]
    w = WALK(TARGET, body_index)
    gate(f"{tag} the new Comparison #{cmp_uid} is addressable as a body Nodes[] index", cmp_uid in w,
         f"body Nodes[] uids {sorted(w)}")
    node_i, _lab, rows = w[cmp_uid]
    bools = [r["i"] for r in rows if r["is_source"]]
    gate(f"{tag} the Comparison has a source terminal to drive the stop", bool(bools), f"rows {rows}")
    vi = g.op(OP_STOP_FROM_NODE)
    vi.SetControlValue(sfn_labels["vi_path"], TARGET)
    vi.SetControlValue(sfn_labels["loop_class"], "WhileLoop")
    vi.SetControlValue(sfn_labels["loop_index"], int(loop_index))
    vi.SetControlValue(sfn_labels["index_node"], int(node_i))
    vi.SetControlValue(sfn_labels["index_term"], int(bools[0]))
    g._run(vi)
    sfn_err = g._err(vi, sfn_labels["connect_err"]) or ""
    dt = time.time() - t0
    fact(f"{tag} OpStopFromNode_v0(loop[{loop_index}], body Nodes[{node_i}], Terminals[{bools[0]}]) "
         f"error out {sfn_err[:180]!r}")
    after = LOOP_END_REF(TARGET, loop_index)
    fact(f"{tag} AFTER: conditional terminal #{after.get('cond_term_uid')}, wire {after.get('cond_wire_uid')}")
    gate(f"{tag} C6 the conditional terminal is now WIRED (non-zero CondWireUID), on the SAME terminal",
         after.get("cond_wire_uid") and after.get("cond_term_uid") == before.get("cond_term_uid"),
         f"term {before.get('cond_term_uid')} -> {after.get('cond_term_uid')}, "
         f"wire {before.get('cond_wire_uid')} -> {after.get('cond_wire_uid')}")
    # 🔴 C6w — A NON-ZERO CondWireUID IS NOT ENOUGH (round-2 review, `already-failed`). The old gate accepted
    # "wired", so a Boolean-ARRAY comparison bolted onto a `Stop if True` terminal would have PASSED it. The
    # cheap, already-built check is WIRE IDENTITY: read the driving Comparison's own terminals again and
    # require the SAME wire uid on both ends — the project's standard proof that a connection is real
    # (`docs/toolkit-capabilities.md:35`, `:67`). The TYPE half is enforced BEFORE the write by C6s, and the
    # whole-VI half by C8 (`ExecState 1` with the ORIGINAL preloaded, FATAL, before `g.save`): a wired but
    # wrong-typed conditional terminal fails there and the stage stops instead of saving.
    cond_wire = after.get("cond_wire_uid")
    try:
        cmp_terms = terms_of(TARGET, body_index, cmp_uid)
        cmp_src_wires = sorted({wv for _i, (_nm, src_, wv) in cmp_terms.items() if src_ and wv})
    except Exception as e:                                                        # noqa: BLE001
        cmp_terms, cmp_src_wires = {"error": f"{type(e).__name__}: {e}"}, []
    fact(f"{tag} C6w the driving Comparison #{cmp_uid}'s source-side wires {cmp_src_wires}; the conditional "
         f"terminal carries wire {cond_wire}")
    gate(f"{tag} C6w the conditional terminal's wire is the SAME uid the driving Comparison #{cmp_uid} "
         f"sources (a wired terminal is not yet a correct one)",
         bool(cond_wire) and cond_wire in cmp_src_wires,
         f"cond wire {cond_wire}, Comparison source wires {cmp_src_wires}, terminals {cmp_terms}")
    return {"loop_uid": loop_uid, "body_uid": body_uid, "route": route, "row": row,
            "compared_terminal": op_name, "comparison_uid": cmp_uid, "seconds": round(dt, 2),
            "operand_candidates": candidates, "operands_refused_by_name": refused,
            "cond_term_uid": after.get("cond_term_uid"), "cond_wire_uid": cond_wire,
            "comparison_source_wires": cmp_src_wires,
            "create_equal_error": err, "stop_from_node_error": sfn_err}


def make_loops():
    """v7 `s2()` `:788-812`, re-cut: three fresh While loops on Diagram #686, each gated by `new_since`."""
    print("\n--- C4 s2: three fresh While loops on Diagram #686", flush=True)
    sib_i = diag_index(TARGET, SIBLING_DIAG_UID)
    fact(f"C4 Diagram#{SIBLING_DIAG_UID} (holder of WhileLoop#{FRAME_LOOP_UID}) is Traverse index {sib_i} — "
         f"re-read here, never cached (Pre-decided 21(d))")
    loops = {}
    for row in sorted(LOOP_LOCATIONS):
        dg0, wl0 = g.uids(TARGET, "Diagram"), g.uids(TARGET, "WhileLoop")
        g.loop_in("while", TARGET, sib_i, LOOP_LOCATIONS[row])
        nd, nw = g.new_since(TARGET, "Diagram", dg0), g.new_since(TARGET, "WhileLoop", wl0)
        gate(f"C4 loop {row} created (exactly +1 Diagram and +1 WhileLoop)", len(nd) == 1 and len(nw) == 1,
             f"+{len(nd)} diagrams, +{len(nw)} while loops")
        loops[row] = {"loop": nw[0]["uid"], "body": nd[0]["uid"]}
        fact(f"C4 {row}: WhileLoop #{nw[0]['uid']}, body Diagram #{nd[0]['uid']}")
    gate("C4b WhileLoop 3 -> 6 and Diagram 170 -> 173",
         g.count(TARGET, "WhileLoop") == AFTER_S2["WhileLoop"] and g.count(TARGET, "Diagram") == AFTER_S2["Diagram"],
         f"WhileLoop {g.count(TARGET, 'WhileLoop')}, Diagram {g.count(TARGET, 'Diagram')}")
    gate("C4c #637 still exists", FRAME_LOOP_UID in [o["uid"] for o in g.report_all(TARGET, "WhileLoop")])
    for uid in STAY_ON_11 + [CTLTERM_STOP_UID]:
        try:
            _c, ou = owner_of(TARGET, uid)
            gate(f"C4c #{uid} still owned by the frame loop body", ou == FRAME_BODY_UID, f"owner {ou}",
                 fatal=False)
        except Exception as e:                                                    # noqa: BLE001
            gate(f"C4c #{uid} still owned by the frame loop body", False, f"UNRESOLVED READ: {str(e)[:120]}",
                 fatal=False)
    return loops


def movein_three(loops, handled, d43):
    """30(e) bullet 1, fixed by 31(b): `move_in` the three into the new loop bodies. The uid is PRESERVED by a
    move (`build_d1_v0.move_in` `:318-335` returns it and v7 `:955-966` gates the owner chain on it), so the
    SubVI table key changes diagram and keeps its node uid AND its path — which is what D5d checks.

    v7's `s1d` (delete) and `s2d` (re-drop) are NOT re-cut here: branch 1 deletes nothing and drops nothing."""
    print(f"\n--- C4 move_in: relocate {handled} into the new loop bodies (no delete, no re-drop)", flush=True)
    new_keys, cut = {}, []
    for row in handled:
        uid, _path, label = RELOCATE[row]
        t = terms_of(TARGET, d43, uid)
        wired = [(uid, i, nm, bool(src), w) for i, (nm, src, w) in t.items() if w]
        cut.extend(wired)
        fact(f"C4 move_in #{uid} {label} -> {row}: {len(t)} terminals, {len(wired)} wired BEFORE the move "
             f"(a move SEVERS them — MEASURED, docs/d1-route-b-plan.md:57-58 (109 cut terminals over 24 uids) "
             f"and :67 (32 of them on these three); 33(a). They enter the re-wire list for S3w, and NO tunnel "
             f"is created by the move)")
        body_uid, loop_uid = loops[row]["body"], loops[row]["loop"]
        move_in(TARGET, uid, diag_index(TARGET, body_uid), (60, 60))
        try:
            _c, ou = owner_of(TARGET, uid)
            _c2, ou2 = owner_of(TARGET, ou) if ou else (None, None)
            ok = (ou == body_uid and ou2 == loop_uid)
        except Exception as e:                                                    # noqa: BLE001
            ou = ou2 = f"<{str(e)[:50]}>"
            ok = False
        gate(f"C4 move_in #{uid} ({label}) -> {row}", ok,
             f"owner Diagram#{ou} (want {body_uid}); owner(owner) WhileLoop#{ou2} (want {loop_uid})")
        new_keys[row] = (body_uid, uid)
    gate(f"C4 move_in SubVI is UNCHANGED at {BEFORE_S2['SubVI']} (a move creates and destroys nothing)",
         g.count(TARGET, "SubVI") == BEFORE_S2["SubVI"], f"SubVI {g.count(TARGET, 'SubVI')}")
    return new_keys, cut


def phase_c():
    """The stage itself, on a COPY of the S1 artefact (30(c)). ONE shape — 31(b)'s branch 1, kept by 32(e) —
    in **32(b)'s order: loops -> `move_in` -> scaffold -> save**. The only run-time selection is the scaffold
    ROUTE, made in phase A by 32(d)'s rule and merely applied here. 31(g): the construction steps are v7's,
    already passed in the real VI; what is NEW is the stage boundary (copy from the S1 artefact, gate on its
    md5, save `D1_s2_loops.vi`). Intermediate illegality is expected: only the SAVE needs `ExecState != 0`."""
    print("\n=== PHASE C: S2 PROPER — loops on #686, the three call sites relocated, the copy SAVED", flush=True)
    with open(OUT_A, encoding="utf-8") as f:
        A = json.load(f)["A"]
    br = A.get("branch") or select_branch(A)
    READINGS["C"]["branch"] = br
    fact(f"C0 branch from {OUT_A}: {br['branch']!r}, handled {br.get('handled')}; {br['why']}")
    gate("C0 the branch is `movein`, the one 31(b) fixed and the only one this file implements",
         br["branch"] == "movein", br["branch"])

    fresh("C0b")
    READINGS["s1_artefact"]["file_at_c"] = file_facts("C1 the S1 artefact, read-only, as phase C finds it",
                                                      S1_ARTEFACT)
    gate("C1a the S1 artefact still matches its pinned md5 BEFORE any edit (30(c))",
         READINGS["s1_artefact"]["file_at_c"].get("md5") == S1_MD5,
         str(READINGS["s1_artefact"]["file_at_c"].get("md5")))
    if os.path.exists(TARGET):
        os.remove(TARGET)
    shutil.copy2(S1_ARTEFACT, TARGET)          # 30(c): the ONE substantive change from S1's skeleton (:623-625)
    READINGS["C"]["copy"] = file_facts("C1 the S2 working copy", TARGET)
    gate("C1 the S2 working copy on disk is byte-identical to the S1 ARTEFACT",
         READINGS["C"]["copy"].get("md5") == S1_MD5, str(READINGS["C"]["copy"].get("md5")))

    with Preload("C2"):
        g.open_panel(TARGET)                   # required before ANY scripting edit
        time.sleep(1.0)
        got = {c: g.count(TARGET, c) for c in BEFORE_S2}
        rec_only = {c: g.count(TARGET, c) for c in RECORD_ONLY}
        READINGS["C"]["before_census"] = dict(got, **{f"recorded_{k}": v for k, v in rec_only.items()})
        fact(f"C3 BEFORE census (GATED): {got}")
        fact(f"C3 BEFORE census (RECORDED, not gated — S1 never pinned them): {rec_only}")
        gate("C3 the copy matches what S1 left (Diagram 170 · Node 624 · Wire 1899 · WhileLoop 3 · SubVI 97 · "
             "Function 180)", all(got[c] == BEFORE_S2[c] for c in BEFORE_S2),
             f"{ {c: (BEFORE_S2[c], got[c]) for c in BEFORE_S2 if got[c] != BEFORE_S2[c]} } (empty = all match)")

        d43 = diag_index(TARGET, FRAME_BODY_UID)
        wmap(TARGET, d43, fresh=True)
        fact(f"C4 frame body #{FRAME_BODY_UID} reads Traverse index {d43} — re-read, never cached across a "
             f"mutation (Pre-decided 21(d))")

        # ---- C2k (31(a)): #5058 IS THE CPU KERNEL. A stage that relocates a node must know what it is moving,
        # and 30(d)'s parenthesis named the wrong VI. Read the name off the artefact with the BUILT census op.
        kern = {}
        try:
            rows = g.subvis(TARGET, d43)
            kern = next((r for r in rows if int(r.get("uid", -1)) == RELOCATE["1.2"][0]), {})
        except Exception as e:                                                    # noqa: BLE001
            kern = {"error": f"{type(e).__name__}: {e}"}
        READINGS["C"]["kernel_at_5058"] = kern
        fact(f"C2k uid {RELOCATE['1.2'][0]} on Diagram#{FRAME_BODY_UID}[{d43}] reads name "
             f"{kern.get('name')!r}, path {kern.get('path')!r}")
        gate(f"C2k the node at uid {RELOCATE['1.2'][0]} is the CPU kernel {CPU_KERNEL_NAME!r} (31(a): 30(d) "
             f"called it GPU_kernel_v1.vi and that was WRONG; swapping the kernel is a LATER stage)",
             str(kern.get("name", "")).strip().lower() == CPU_KERNEL_NAME.lower(),
             f"name {kern.get('name')!r} path {kern.get('path')!r}")

        # ---- the stage. 31(b): ONE shape. 🔴 32(b)'s ORDER: loops -> move_in -> scaffold -> save. Intermediate
        # illegality (three loops with unwired conditional terminals) is EXPECTED AND PERMITTED inside the
        # stage; only the SAVE needs ExecState != 0 (gscript.py:2065-2071, 29(d)).
        handled = list(br.get("handled") or [])
        ct_before = {o["uid"] for o in g.report_all(TARGET, "ControlTerminal")}
        tun_before = g.uids(TARGET, "LoopTunnel")
        loops = make_loops()

        new_keys, cut = movein_three(loops, handled, d43)
        READINGS["C"]["loops"] = loops
        READINGS["C"]["relocated_keys"] = {k: list(v) for k, v in new_keys.items()}
        READINGS["C"]["rewire_rows_captured"] = cut
        fact(f"C4 {len(cut)} wired terminals captured for S3w's re-wire list; relocated keys {new_keys}")

        # C6: a new While loop with an UNWIRED conditional terminal is a compile-time break (Pre-decided
        # 16(a)), so each loop is scaffolded NOW — after its body has received its relocated node (32(b)).
        route = (A.get("A3") or {}).get("a3_selected_route")
        scaffold = [scaffold_loop(f"C6 {row}", row, loops[row]["loop"], loops[row]["body"], route)
                    for row in sorted(loops)]
        READINGS["C"]["scaffold"] = scaffold

        # C6b: rule 1a's bound. Under 32(a) the scaffold cannot read a panel control at all, so this now checks
        # that NOTHING in the stage moved a pre-existing ControlTerminal into a new loop body.
        ct_after = {o["uid"] for o in g.report_all(TARGET, "ControlTerminal")}
        moved_ct = []
        for uid in sorted(ct_before):
            try:
                _c, ou = owner_of(TARGET, uid)
            except Exception:                                                     # noqa: BLE001
                ou = None
            if ou in {loops[r]["body"] for r in loops}:
                moved_ct.append((uid, ou))
        READINGS["C"]["controlterminals"] = {"before": len(ct_before), "after": len(ct_after),
                                             "new": sorted(ct_after - ct_before),
                                             "pre_existing_now_in_a_new_body": moved_ct}
        fact(f"C6b ControlTerminal {len(ct_before)} -> {len(ct_after)}; new {sorted(ct_after - ct_before)}; "
             f"pre-existing ones now inside a NEW loop body: {moved_ct}")
        gate("C6b no PRE-EXISTING ControlTerminal was MOVED into a new loop body anywhere in this stage "
             "(rule 1a; and 32(a) means the scaffold never reads a panel control at all)", not moved_ct,
             f"{moved_ct}")

        # 32(f): every tunnel this stage created, for phase D's indexing read.
        tun_after = g.new_since(TARGET, "LoopTunnel", tun_before)
        READINGS["C"]["new_tunnels"] = [o["uid"] for o in tun_after]
        fact(f"C7 32(f): LoopTunnel {len(tun_before)} -> {g.count(TARGET, 'LoopTunnel')}; NEW tunnel uids "
             f"{[o['uid'] for o in tun_after]} — their IndexMode is read in phase D with the BUILT "
             f"gscript.tunnels / OpTunnels_v0")

        c1 = {c: g.count(TARGET, c) for c in AFTER_S2}
        READINGS["C"]["after_census"] = c1
        gate("C5 the NET contract holds: WhileLoop 6 · Diagram 173 · SubVI 97 (NOT 100 — 30(a))",
             c1 == AFTER_S2, f"{c1} (want {AFTER_S2})")

        es = g.exec_state(TARGET)
        READINGS["C"]["exec_state_preloaded"] = es
        fact(f"C8 exec_state(target) with the ORIGINAL PRELOADED = {es}")
        # 🔴 C8 IS A FATAL GATE, not a fact (round-2 review, `already-failed`): this is where a conditional
        # terminal that is WIRED BUT WRONG-TYPED — a Boolean ARRAY from an array comparison, say — shows up.
        # `gscript.save()` reaches `SaveInstrument` only at `ExecState != 0` (`gscript.py:2065-2071`), so
        # letting a 0 through to C9 turns a type error into a save error and invites the banned `gui_save`
        # divert. Failing here leaves the DATA artefact and no VI, which is what 30(g)/31(i) prescribe.
        gate("C8 the working copy reads ExecState 1 with the ORIGINAL PRELOADED, BEFORE any save is attempted "
             "(a wired-but-wrong-typed conditional terminal fails HERE)", es == 1,
             f"exec_state = {es!r}; 0 means broken — gscript.save() cannot reach SaveInstrument "
             f"(gscript.py:2065-2071) and allow_broken=True is banned (29(d))")
        t0 = time.time()
        err = None
        try:
            size = g.save(TARGET)               # DEFAULT allow_broken=False — no divert to gui_save, by design
        except Exception as e:                                                    # noqa: BLE001
            size, err = None, f"{type(e).__name__}: {e}"
        dt = time.time() - t0
        READINGS["C"]["save"] = {"seconds": round(dt, 2), "returned_bytes": size, "exception": err}
        fact(f"C9 g.save(target) took {dt:.2f} s and returned {size!r}; exception = {err!r}")
        gate("C9 g.save(target) returned without raising", err is None, str(err))
        try:
            g.close_panel(TARGET)
        except Exception as e:                                                    # noqa: BLE001
            fact(f"C9b close_panel(target) raised {type(e).__name__}: {e}")
    READINGS["C"]["artefact"] = file_facts("C9 THE STAGE ARTEFACT", TARGET)
    fact(f"C refs at phase end: {g.ref_counts()}; handles {labview_handles()}")
    orig_gate("C")


# ============================================================================== PHASE D — VERIFY
def phase_d():
    """The saved artefact re-read in a FRESH instance under BOTH conditions, then its COLD SubVI table against
    the ORIGINAL's (29(g)) — one condition per child process and per LabVIEW instance."""
    print("\n=== PHASE D: VERIFY the saved artefact in a fresh instance, COLD and PRELOADED", flush=True)
    fresh("D0")
    READINGS["D"]["artefact"] = file_facts("D0 the artefact as phase C left it", TARGET)
    cold = g.exec_state(TARGET)
    READINGS["D"]["exec_state_cold"] = cold
    fact(f"D1 COLD exec_state({os.path.basename(TARGET)}) = {cold} — labelled COLD and, by Pre-decided 14a, "
         f"UNREAD as a verdict on legality")
    with Preload("D2"):
        pre = g.exec_state(TARGET)
        READINGS["D"]["exec_state_preloaded"] = pre
        fact(f"D2 PRELOADED exec_state({os.path.basename(TARGET)}) = {pre}")
    gate("D2 the PRELOADED reading of the saved artefact is 1", READINGS["D"].get("exec_state_preloaded") == 1,
         f"cold {cold}, preloaded {READINGS['D'].get('exec_state_preloaded')}")
    dump()

    # ---- D6 (32(f)): the indexing state of every tunnel this stage created. A built op CAN read it —
    # `gscript.tunnels` / `OpTunnels_v0` returns `index_mode` per LoopTunnel — so this is a reading, not a
    # "nothing can read it" note. If the stage created no tunnel, the log says exactly that.
    new_tuns = list(READINGS["C"].get("new_tunnels") or [])
    d6 = {"reader": "gscript.tunnels / OpTunnels_v0 (tools/gscript.py:941-978) — IndexMode is returned per "
                    "LoopTunnel, so 32(f)'s 'if any built op can read it' is YES",
          "new_tunnel_uids": new_tuns, "rows": [], "error": None}
    if not new_tuns:
        fact("D6 32(f): this stage created NO new LoopTunnel, so there is no indexing state to read. The "
             "reader exists (gscript.tunnels / OpTunnels_v0); it simply has nothing to read here.")
    else:
        try:
            with Preload("D6"):
                order = [o["uid"] for o in g.report_all(TARGET, "LoopTunnel")]
                for u in new_tuns:
                    if u not in order:
                        d6["rows"].append({"uid": u, "note": "not present in the SAVED artefact"})
                        continue
                    r = g.tunnels(TARGET, order.index(u))
                    d6["rows"].append(r)
                    fact(f"D6 32(f) tunnel #{u}: IndexMode {r.get('index_mode')} "
                         f"(0 = NOT auto-indexing, i.e. the value passes through unchanged), outer "
                         f"{r.get('out_name')!r} wire {r.get('out_wire')}, inner wires {r.get('in_wires')}")
        except Exception as e:                                                    # noqa: BLE001
            d6["error"] = f"{type(e).__name__}: {e}"
            fact(f"D6 32(f) the tunnel read FAILED ({d6['error']}) — recorded, not fatal")
        modes = [r.get("index_mode") for r in d6["rows"] if "index_mode" in r]
        d6["all_index_mode_zero"] = bool(modes) and all(m == 0 for m in modes)
        gate("D6 32(f) every tunnel this stage created is recorded with its IndexMode", bool(d6["rows"]),
             f"{len(d6['rows'])} rows, modes {modes}", fatal=False)
    READINGS["D"]["tunnel_indexing"] = d6
    dump()

    print("\n=== D5: the SAVED ARTEFACT's COLD SubVI table against the ORIGINAL's COLD SubVI table", flush=True)
    g.reset()
    s2_tbl, s2_rec = cold_subvi_table("D5a-S2COPY-COLD", TARGET)
    orig_tbl, orig_rec = cold_subvi_table("D5b-ORIG-COLD", ORIGINAL)
    # What this stage moved: S1's TIFF key is already gone, and every handled row left Diagram #639 for a new
    # loop body. So the EXPECTED table is the ORIGINAL minus those keys, PLUS exactly the relocated keys.
    relocated = {tuple(v) for v in (READINGS["C"].get("relocated_keys") or {}).values()}
    handled = list((READINGS["C"].get("branch") or {}).get("handled") or [])
    expect_missing = {TIFF_SUBVI_KEY} | {(FRAME_BODY_UID, RELOCATE[r][0]) for r in handled}
    cmp_d = compare_subvi_tables(s2_tbl, orig_tbl, expect_missing)
    # the relocated rows appear as EXTRA keys by construction; they are accepted only if they are EXACTLY the
    # keys phase C recorded, and only if their name and path match the row the ORIGINAL had for that subVI.
    extra = set(cmp_d["extra"])
    unexplained_extra = sorted(extra - relocated)
    unaccounted_reloc = sorted(relocated - extra)
    same_callee = []
    for r in handled:
        old_key, new_key = (FRAME_BODY_UID, RELOCATE[r][0]), tuple(READINGS["C"]["relocated_keys"][r])
        same_callee.append({"row": r, "old_key": list(old_key), "new_key": list(new_key),
                            "original_row": list(orig_tbl.get(old_key, ("<absent>", "<absent>"))),
                            "artefact_row": list(s2_tbl.get(new_key, ("<absent>", "<absent>"))),
                            "path_matches": (orig_tbl.get(old_key, (None, None))[1]
                                             == s2_tbl.get(new_key, (None, None))[1])})
    READINGS["D"]["subvi_census"] = {"s2_artefact": s2_rec, "original": orig_rec}
    READINGS["D"]["subvi_compare_s2_vs_original"] = cmp_d
    READINGS["D"]["expected_missing_keys"] = [list(k) for k in sorted(expect_missing)]
    READINGS["D"]["relocated_rows"] = same_callee
    READINGS["D"]["unexplained_extra"] = unexplained_extra
    fact(f"D5 row counts: S2 artefact {s2_rec['n_rows']} vs ORIGINAL {orig_rec['n_rows']} (expected "
         f"{PIN_SUBVI_ROWS - 1} vs {PIN_SUBVI_ROWS}); keys expected to leave Diagram #{FRAME_BODY_UID}: "
         f"{sorted(expect_missing)}; keys expected to appear inside the new loop bodies: {sorted(relocated)}")
    if cmp_d["missing"] or cmp_d["changed"] or cmp_d["not_deleted"] or unexplained_extra:
        log_table_diff("D5 S2 artefact vs ORIGINAL", cmp_d)
        for k in unexplained_extra:
            print(f"      UNEXPLAINED-EXTRA key {k} — phase C did not record relocating anything there", flush=True)
    gate(f"D5-i the ORIGINAL's COLD SubVI table has {PIN_SUBVI_ROWS} rows",
         orig_rec["n_rows"] == PIN_SUBVI_ROWS, f"{orig_rec['n_rows']} rows", fatal=False)
    gate(f"D5-ii the S2 artefact's COLD SubVI table has {PIN_SUBVI_ROWS - 1} rows",
         s2_rec["n_rows"] == PIN_SUBVI_ROWS - 1, f"{s2_rec['n_rows']} rows", fatal=False)
    ok_a = not (cmp_d["missing"] or cmp_d["changed"] or cmp_d["not_deleted"]
                or cmp_d["expected_key_absent_from_reference"] or unexplained_extra or unaccounted_reloc)
    ok_b = s2_rec["into_background_vis_copy"] == 0
    ok_c = s2_rec["empty_rows"] == 0
    ok_d = all(r["path_matches"] for r in same_callee)
    gate("D5a every surviving row is the ORIGINAL's, key-for-key in BOTH name and path, and the only new keys "
         "are exactly the rows phase C relocated", ok_a,
         f"missing={len(cmp_d['missing'])} changed={len(cmp_d['changed'])} "
         f"not_relocated={cmp_d['not_deleted']} unexplained_extra={unexplained_extra} "
         f"unaccounted_relocations={unaccounted_reloc}", fatal=False)
    gate("D5b ZERO rows of the S2 table point into claudeDev\\background VIs_COPY\\", ok_b,
         f"{s2_rec['into_background_vis_copy']} rows, first keys {s2_rec['background_vis_copy_keys']}",
         fatal=False)
    gate("D5c no row of the S2 table has an empty name or an empty path", ok_c,
         f"{s2_rec['empty_rows']} rows, first keys {s2_rec['empty_keys']}", fatal=False)
    gate("D5d each relocated row still calls the SAME VI on disk as the ORIGINAL did", ok_d,
         f"{same_callee}", fatal=False)
    dump()
    gate("D5 FATAL the saved S2 artefact's SubVI table is accepted against the ORIGINAL (a AND b AND c AND d)",
         ok_a and ok_b and ok_c and ok_d, f"a={ok_a} b={ok_b} c={ok_c} d={ok_d}")
    dump()
    fact(f"D3 every phase's readings, md5s, sizes and version bytes written to {OUT_READINGS}")
    fact(f"D refs at phase end: {g.ref_counts()}; handles {labview_handles()}")
    orig_gate("D")                              # D4


# ============================================================================== main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass
    ap = argparse.ArgumentParser(description="S2 stage (Pre-decided 30 as amended by 31). Phases are "
                                             "selectable; A EDITS NOTHING and C reads A's DATA artefact.")
    ap.add_argument("--phases", default="A",
                    help="any subset of ACD, run in that fixed order. Default A. `--phases A` is the "
                         "recording and edits nothing (30(d), 31(b)/(c)/(f)); `--phases CD` runs the stage "
                         "proper and REQUIRES tools/bench/s2a_legality.json from a previous A run; "
                         "`--phases ACD` does both in one process.")
    args = ap.parse_args()
    sel = [ch for ch in "ACD" if ch in args.phases.upper()]
    if not sel:
        print(f"--phases {args.phases!r} selects nothing (expected a subset of ACD)", flush=True)
        return 2
    if "C" in sel and "A" not in sel and not os.path.isfile(OUT_A):
        print(f"--phases {args.phases!r} needs {OUT_A}, which does not exist. Run `--phases A` first: 30(d) "
              f"says phase A is written and run BEFORE phases C/D exist.", flush=True)
        return 2
    t0 = time.time()
    g.reset()
    print(f"stage_d1_s2: PHASES {''.join(sel)} (of ACD)", flush=True)
    print(f"stage_d1_s2: ORIGINAL    {ORIGINAL}", flush=True)
    print(f"stage_d1_s2: S1 ARTEFACT {S1_ARTEFACT}  (md5 pin {S1_MD5})", flush=True)
    print(f"stage_d1_s2: TARGET      {TARGET}", flush=True)
    READINGS["original"]["file"] = file_facts("S0 the ORIGINAL, read-only", ORIGINAL)
    gate("S0 original md5 BEFORE equals the pin", READINGS["original"]["file"].get("md5") == ORIG_MD5,
         str(READINGS["original"]["file"].get("md5")))
    fact(f"S0 handles at entry: {labview_handles()} (0 = LabVIEW not started yet); refs {g.ref_counts()}")
    try:
        for ch in sel:
            # 32(d) rule (3), applied between phases: if phase A's mechanical selection found no qualifying
            # scaffold route, the stage STOPS after A. C and D are SKIPPED — not failed — and the DATA
            # artefact is the product of the run (30(e) branch 4, 31(i)).
            if ch in "CD":
                br = (READINGS.get("A") or {}).get("branch")
                if br is None and os.path.isfile(OUT_A):
                    with open(OUT_A, encoding="utf-8") as f:
                        br = (json.load(f).get("A") or {}).get("branch")
                if br and br.get("branch") == "stop_after_a":
                    fact(f"PHASE {ch} SKIPPED — 32(d) rule (3): {br.get('rule_applied')}. {br['why']} The "
                         f"stage ends here with its DATA artefact and NO VI is edited or saved. This is a "
                         f"pre-decided legitimate end, not a failure.")
                    continue
            {"A": phase_a, "C": phase_c, "D": phase_d}[ch]()
    except Stop as e:
        fact(f"STOP at a fatal gate: {e} — the chain stops here and every artefact written so far STAYS ON "
             f"DISK. 30(g): a stage that cannot end legal saves its DATA file and SAYS SO; it does not save a "
             f"broken VI and does not pretend it saved one.")
    except BaseException as e:                                                    # noqa: BLE001
        fact(f"CRASH {type(e).__name__}: {e} — every artefact written so far STAYS ON DISK")
        raise
    finally:
        try:
            dump()
        except Exception as e:                                                    # noqa: BLE001
            fact(f"the JSON artefacts could not be written ({type(e).__name__}: {e})")
        m = md5(ORIGINAL)
        gate("S6 original md5 AFTER the whole run", m == ORIG_MD5, m, fatal=False)
        m1 = md5(S1_ARTEFACT) if os.path.exists(S1_ARTEFACT) else None
        gate("S6b the S1 ARTEFACT md5 AFTER the whole run (this stage only ever COPIES it)", m1 == S1_MD5,
             str(m1), fatal=False)
        for tag, p in (("S1 INPUT", S1_ARTEFACT), ("S2 ARTEFACT", TARGET)):
            fact(f"FINAL {tag}: {os.path.basename(p)} on disk = {os.path.exists(p)}"
                 + (f", md5 {md5(p)}, {os.path.getsize(p)} B" if os.path.exists(p) else ""))
        fact(f"FINAL DATA artefact: {OUT_A} on disk = {os.path.exists(OUT_A)}")
        fact(f"FINAL refs: {g.ref_counts()} (`live` should be 0); handles {labview_handles()}")
    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== stage_d1_s2 (phases {''.join(sel)}): {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
