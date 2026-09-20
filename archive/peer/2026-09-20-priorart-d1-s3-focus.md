# priorart-d1-s3-focus

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.7788  in 48 / out 28237 / cache-create 218610 / cache-read 3772994  (374s, 31 turn(s))
- **date:** 2026-09-20 06:05:28
- **outcome:** ANSWERED (378s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: cycle-start).

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
# PLAN ??D1 STAGE S3: the 1.5 FOCUS node set moves into loop a and is re-wired, in ONE saved stage

Recipe under review: `tools/recipes/stage_d1_s3_focus.py`
(954 lines, 28 `gate(` sites, sha256 `253212c547b94b779ecc803b24ccfe8b327de6c579fac154502823ec0cdcc646`;
AST + import check `tools/bench/c53_astcheck.log`, rc 0).
**It has NOT been launched.** No `.vi` has been opened this cycle; no COM call has been made.

## 1. What the stage is, and who decided it

`docs/cycle27-plan.md` Pre-decided **37(g)** (`:1116-1125`) decides: S3 = `claudeDev\D1_s3_loop15.vi` ??the WHOLE
1.5 FOCUS node set moved into loop a and re-wired, **one script, one `g.save()`**, `allow_broken` False.
**37(h)** (`:1126-1131`) assigns loop a = `WhileLoop #23032`, body `Diagram #23058`, and says in terms: "cite this
line, never re-derive it". The recipe cites it.

Start file: `claudeDev\D1_s2_loops.vi`, md5 `6ff19497f2309e007a214660bb64b911`, 475,707 B (Pre-decided 37(a);
verified twice ??`tools/bench/stage_d1_s2_loops.log` 35/0 and `tools/bench/verify_d1_s2.{log,json}` 23/0).

The set (all on `Diagram #639`, `WhileLoop #637`'s body ??**not `#686`**, 37(f) `:1106-1108`, measured
`tools/bench/diag_movein_set.log:41`, `:50`):

| object | what | evidence |
|---|---|---|
| `CaseStructure #10407` | the autofocus case | `docs/d1-build-plan.md:305` |
| `#48` | `ASI_adjust focus-subvi.vi` | `docs/d1-build-plan.md:306` |
| `#3529` / `#3560` / `#3447` | three **ControlReferenceConstants** | `docs/d1-build-plan.md:330-332` |
| `#4334/#4344` | shift register ??**the VISA session** | `docs/d1-build-plan.md:360` |
| `#4256/#4274` | shift register ??`position [internal units]` | `docs/d1-build-plan.md:359` |

## 2. What the recipe does, phase by phase (a census + readings JSON is written after every phase)

0. Files only, no LabVIEW: ORIGINAL md5 pin, S2 md5/size pin, fresh LabVIEW instance, copy ??`D1_s3_loop15.vi`.
1. Baseline census (Diagram 173 / WhileLoop 6 / SubVI 97 / Comparison 17 / LoopTunnel 135 / Wire 1905); loop-a
   identity **by ownership traversal** (`#23058` ??`#23032` ??`#686`); each set member's owner and
   **wired-terminal** count; the 17 `"dest": "1.5"` rows of `tools/bench/d1_rewire_sources.json` loaded and
   classified **by measuring each named source's owner**, not from a table in the script.
2. Five `move_in` calls, **one node per call** ??`build_d1_v0.py:318`, NOT in `gscript.py` ??each followed by a
   re-read of the moved node by uid.
3. Two shift registers created on loop a with the BUILT `gscript.add_shift_reg` `:673` and read back by uid.
4. Re-wiring in batches of ??12 rows (there are 9 wirable jobs ??one batch), each job through the BUILT
   `OpConnectNested_v1` (`build_opconnectnested_v1.connect_nested_v1` `:418`) or `gscript.wire_sr` `:713`.
5. The rows this stage cannot wire are re-read and REPORTED, never wired.
6. Per-node **wired-terminal** acceptance gates.
7. `ExecState` in-instance with the ORIGINAL preloaded (34(l)), then the ONE `g.save()`.
8. Child-process COLD/PRELOADED re-read of the saved file; the SubVI **TABLE** against the ORIGINAL (29(g),
   S1's built instrument `stage_d1_s1.py:377`/`:408`); `WhileLoop` still 6; ORIGINAL/S1/S2 md5s unchanged.

## 3. The five constraints the recipe is built to honour

1. **`move_in` is one node per call and SEVERS every wire on the moved node, in either order** ??37(d) `:1093-1100`,
   measured `tools/bench/diag_movein_set.log:75`, `:86`, `:101`.
2. **A wire count can never detect a cut** ??37(e) `:1101-1105`: the whole-VI `Wire` census held 1905 ??1905 ??
   1905 while both ends of wire 4833 went bare and uid 4833 stayed in the list. So **every re-wiring gate counts
   WIRED TERMINALS**, and the `Wire` / `LoopTunnel` deltas are printed with **no** predicted value.
3. **Every address is a uid or an exact name, re-read immediately before use** (34(h) `:927-935`) and **every
   report re-reads by uid or by ownership traversal, never by array index** (37(b) `:1080-1086`). Measured
   justification: `#48`'s `Nodes[]` index drifted 11 ??10 when `#3529` left the same diagram
   (`tools/bench/diag_movein_set.log:41` vs `:66`).
4. **A value beside a non-zero error column is UNREAD** (Pre-decided 14 `:147-150`; 35(d)(1) `:1014-1016`). The
   recipe's `term_state()` scores the four per-terminal error columns, with the one documented exception
   `gscript.py:874` names (a bare terminal legitimately returns `conn_err`/`wire_err` 1055). No gate accepts UNREAD.
5. **Gate output is the documented `  FAIL  ` / `  PASS  ` form** ??37(i) `:1132-1139`; the bolded form is what
   blinded `guard_peer.py:73`. The AST check asserts zero occurrences of the bolded form in this file.

Also binding and honoured: ?뵶 **NO VI IS RUN** (34(f) `:904-907`); **no new op, no new device** (Pre-decided 2;
user 2026-09-18 08:53); no motor, no ASI, no camera, no GUI action; the ORIGINAL, `D1_s1_copy.vi` and
`D1_s2_loops.vi` are never written and their md5s are gated at the end.

## 4. ?뵶 THREE ARITHMETIC CONFLICTS THE RECIPE STATES BEFORE THE RUN

These are in the recipe's own prediction contract, section "(X1)/(X2)/(X3)". They are stated here because a
prior-art reviewer is exactly the right reader for them.

- **(X1) `CaseStructure #10407` cannot return to its pre-move wired-terminal count in this stage.** Of its 7 cut
  rows (`tools/bench/d1_rewire_sources.json:1749-1918`), four are internal to the 1.5 set or its two shift
  registers; **three are not** ??t0 (the SELECTOR, w10799) ??`#10686`, `action "cross-loop:1.2->1.5"` (`:1773`);
  t1 `# slices in stack` (w9635) ??LoopTunnel `#9641` of `#637`, `action "from-tunnel"` (`:1789`); t2 (w10990) ??
  `#10757` t1 `element` (`:1818`). `#10686` and `#10757` are 1.2 nodes this stage does not move, so they stay
  inside `WhileLoop #637`. `docs/d1-build-plan.md:250` says 1.5 is "woken by the 1-element `Q_focus`", and the
  queue path is DEFERRED BEHIND S3 by Pre-decided 36 (`:1024-1060`). 37(g)'s supporting sentence "**none** of its
  sources stays on `#686`" is an argument about `#48`'s seven rows; it is accurate for `#48` and does not cover
  `#10407`. So gate `W-10407` is **predicted to fail at 4 of 7**.
- **(X2) `ExecState` is therefore predicted 0, not 1, and the save predicted refused.** A Case Structure with a
  bare selector is a broken VI; so is a shift register left with a bare inside terminal ??which is what `#637`'s
  own `#4334/#4344` and `#4256/#4274` become once `#10407` and `#48` leave, since 37(g) names no deletion of the
  old pair. Same wall as cycle 52 (`tools/bench/diag_movein_set.log:101` onward).
- **(X3) The SubVI table key contains the DIAGRAM uid** (`stage_d1_s1.py:389` keys `(diagram_uid, node_uid)`), so
  moving the SubVI `#48` necessarily re-keys it `(639, 48)` ??`(23058, 48)`. "the ORIGINAL minus exactly
  `(639, 22700)`, missing 0 / extra 0 / changed 0" is unsatisfiable by construction for any stage that moves a
  SubVI. The recipe runs BOTH comparisons: the brief-literal one as an OBSERVATION, and a MOVE-AWARE one (with
  `#48` re-keyed to the owner this run actually MEASURES) as the FATAL gate.

## 5. What is deliberately NOT in this stage

- No queue of any kind (Pre-decided 36 defers the donor/queue path behind S3).
- No deletion of the old `#637` shift-register pair (37(g) names none; `delete_object` on a shift register is
  unverified here).
- No import of `tools/recipes/build_d1_routeb_v7.py` ??34(i) (`:936-939`) says the next build is a SHORT script
  and that re-arming those bytes is what cost cycle 49 its launch. v7 is cited, not reused.
- Nothing is run: `NO VI IS RUN` is printed by the recipe and asserted in its close-out.

## 6. The question for this review

Has this direction, this artefact, or any part of this machinery already been decided, tried, refuted, built,
measured or written down in this repository ??and in particular, is any of (X1)/(X2)/(X3) already answered
somewhere I have not read?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
?럦 **D0 IS DELIVERED** (cycle 31) 쨌 **N1 IS ACCEPTED** (cycle 34) 쨌 **D1 STAGE S1 IS DELIVERED** (cycle 48 ??`claudeDev\D1_s1_copy.vi`, md5 `3e3d23ce??, 20/0) 쨌 **D1 STAGE S2 IS DELIVERED** (cycle 51, ACCEPTED cycle 52 ??`claudeDev\D1_s2_loops.vi`, md5 `6ff19497??, COLD/PRELOADED ExecState 1) **??S3 is next.** Banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.
## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released   # cycle 52 material round 3 finished; handles back at 34,191
  owner_c52m3: # ??**RELEASED 2026-09-20 05:2x ??cycle 52 material ROUND 3, TWO DIAGNOSTICS, BOTH COMPLETE, FACTS ONLY (no boundary chosen, no donor chosen, no stage written). Both under `tools/bench/`, both on DATED SCRATCH copies of `claudeDev\D1_s2_loops.vi`; NO VI WAS RUN (34(f)), no new op, no motor/ASI/camera/GUI. ORIGINAL `2a78e17c??, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? ALL byte-unchanged after both runs.** AST+import OK `tools/bench/c52r3_astcheck.log`. ?럦 **(A) `tools/bench/diag_movein_set.py` ??`.log`/`.json`, `BGRUN END rc=1 after 101s` (rc=1 = bgrun's INNER-FAILURE flag on gate P6, which was MY OWN mis-stated gate, not a machine fault), 13 pass / 1 fail.** **A1: `move_in` TAKES ONE NODE PER CALL.** It is NOT in `tools/gscript.py` (which has only `move_out` `:2674` / `move_object` `:2299`); it is `build_d1_v0.py:318` `move_in(target, uid, dest_diagram_index, position)`, writing ONE `int` to the op control **`UID 3`** (`:332`) ??read back from `OpMoveIn_v0.vi` itself, whose `UID 3` round-trips as a scalar `int`, not a sequence. ?좑툘 Its echoed `UID` output is NOT the moved object (both calls echoed **23035**, loop a's scaffold Comparison). ?뵶 **A2: THE INTERNAL WIRE DOES NOT SURVIVE ??VERDICT `SEVERED`.** Measured on the real pair `#3529 '- Inc (PgDn)' t0` ??`#48 '-Inc reference' t0`, wire **4833**: BEFORE, both nodes sit on **Diagram #639** (WhileLoop #637's BODY ??*not* `#686`; that is what P6 got wrong), `#48` has 7/7 terminals wired, `#3529` is a **`ControlReferenceConstant`** with 1/1 wired, and w4833 reads 2 terminals (source `#3529`, sink `#48`). After move 1 (SOURCE `#3529` ??body Diagram **#23058** of loop a): `#3529` goes **1 wired ??0**, `#48` STAYS on `#639` still 7/7, w4833 now reads ONE terminal (the `#48` sink, no source). After move 2 (SINK `#48` ??the same body): `#48` goes **7 wired ??0**, w4833 reads **0** terminals. Order used: source first, then sink. ?좑툘 **The whole-VI `Wire` count never moves (1905 ??1905 ??1905) and uid 4833 is still IN the Wire list** ??`move_in` DETACHES terminals, it does not delete Wire objects, so a Wire census can never detect this. **A3: ExecState 0 after the moves** (in-instance, ORIGINAL preloaded, 34(l)); `g.save()` refused ??`RuntimeError: refusing to save a BROKEN VI`, `allow_broken` stayed False, `gui_save` never called ??so **the scratch `claudeDev\DIAG_moveinset_20260920_051804.vi` is still byte-identical to S2 (`6ff19497??, 475707 B): NO SAVED ARTEFACT for this shape.** Refs 5/5/0; handles 33,967 ??60,237. ??**(B) `tools/bench/diag_donor_census.py` ??`.log`/`.json`, `BGRUN END rc=0 after 134s`, 14 pass / 0 fail ??a PURE READ that mutated nothing (census identical before/after, scratch md5 unchanged).** ?뵶 **B1's data-type column is NOT MEASURABLE BY THE BUILT FLEET**: no op reads `Terminal.DataType` (`node_terms:870` = name/is_source/wire; `report_all:488` = class/uid/pos/owner; `node_info:2459` = `Node.Style`, TOP-LEVEL nodes only, and `#686` is not top level), and a reader would be a NEW OP (forbidden, Pre-decided 2). What IS measured: **`Diagram #686` holds 24 `Nodes[]`** (21 originals + the three S2 loops), every named output terminal listed in the JSON; `#637` exposes **17** named outputs (matching `diag_s2_scaffold.json:124-193`). ?럦 **B3: 18 of the 24 nodes are INDEPENDENT of `#637`** ??`[8486, 7201, 781, 250, 6951, 6409, 8953, 9342, 9179, 28124, 27605, 28670, 25380, 25091, 25149, 23032, 10170, 23041]`; the 6 that are not are `#637` itself plus `#2048`, `#7202`, `#194`, `#1628`, `#6384`. The wire?뭩ource map (32 sourced wires) was spot-checked 6/6 against `OpWireSource_v5`. **B2: all five of 짠9's `A` rows name `#637` as the donor and `#637` is by definition not independent of itself**; `Q_free`/`Q_work`/`Q_focus` still have no `(node, named output terminal)` pair on `#686` at all. Refs 0/0/0; handles 30,932 ??34,191 (each run restarts its own instance).
  owner_c52m2: # ??**RELEASED 2026-09-20 05:0x ??cycle 52 material, Pre-decided 35(b) ROUND 2. THREE READ-ONLY-INTENT DIAGNOSTICS on dated SCRATCH copies of `D1_s1_copy.vi`; NO VI WAS RUN (34(f)), no new op, no motor/ASI/camera/GUI. ORIGINAL `2a78e17c??, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? ALL unchanged after every run.** ?럦 **(1) `tools/bench/diag_queue_donor2.py` ??`.log` / `.json`, `BGRUN END rc=0 after 120s`, 16 pass / 0 fail ??BOTH unmeasured shapes are now MEASURED and BOTH ARE REFUSED.** **SHAPE 1 (front-panel control donor) ??the control IS creatable and its terminal CAN be put on Diagram #686, but `queue_node` still refuses it.** `create_control`'s ladder is TOP-LEVEL only (measured, not cited: the top-level diagram is **`TopLevelDiagram` #536**, Traverse[0]; round 1's attempt passed a Diagram-#686 `Nodes[]` index, the wrong address space). Scalar route `build_index_array` ??`create_control` on `index` ??**ControlTerminal #23124 label `index`**; non-scalar route `drop_subvi(Error Cluster From Error Code.vi)` ??`create_control` on `error in (no error)` ??**ControlTerminal #23493**; both BORN on `TopLevelDiagram` #536, and **`move_in` relocated BOTH to Diagram #686 (owner re-read by uid = `Diagram` #686, no error)**. ?뵶 But on #686 **neither appears in `AbstractDiagram.Nodes[]` and neither exposes ANY named source terminal (`out_name` = [])**, and `queue_node('obtain')` refuses both with **`error 1057: To More Specific Class in OpQueueObtain_v0.vi`** ??the SAME refusal round 1 got for a diagram constant. **SHAPE 2 (type the queue from its own input) ??the premise cannot be reached.** The `Obtain Queue` only exists because a donor typed it (baseline #8486 `x+1` ??Function **#23079**, Diagram #686 Nodes[23]), and its `element data type` input **arrives ALREADY WIRED (wire 8518)**. `OpCreateConstOnTerm_v0` with `Class Name='Diagram'[19]` on that terminal: op `error out` EMPTY but **invoke error `1055: Invoke Node in OpCreateConstOnTerm_v0.vi`, created uid 0, Constant delta 0**. The `FlatSequenceFrame` variant was NOT attemptable ??`report_all('FlatSequenceFrame')` fails **`error 1092 ??Traverse Initialization Failed`**, so #686's owner has no Traverse index. **POSITIVE CONTROL on a real loop body WORKED** (WhileLoop #637[1] body Nodes[14] #6104 Terminals[2]: created **#23716**, terminal wire 0 ??23745, no error) ??so the refusal is the op's `Loop.Diagram` downcast, i.e. **INTRINSIC to the container class, not the call**. **SHAPE 3 (dependency):** the one ACCEPTED donor **#8486 `x+1`** takes its single fed input `x` from wire **7478**, whose source is **`FlatSequenceInnerTunnel` #896, owner `FlatSequence` #681** ??**NOT WhileLoop #637**; the `#637` outer-terminal shape depends on the frame loop totally by construction. ?좑툘 **(2) NO SAVABLE ARTEFACT EXISTS FOR THIS SHAPE.** `tools/bench/diag_qdonor2_stage.py` (`BGRUN INNER FAILURE`, 11/1, the fail being gate P8) replayed the shape-1 edits one at a time: the untouched scratch reads **ExecState 1**, and **step 1 alone ??`build_index_array`, one unwired Index Array on the top-level diagram ??takes it to 0**, never returning through steps 2??, so `g.save()` was never reachable. **(3) The mandatory failed-prediction review `archive/peer/2026-09-20-qdonor2-p8-no-saved-artefact.md` (claude/hypothesis, opus max, ANSWERED, $4.4815, 522 s) is ACCEPTED and its discriminating test was RUN: `tools/bench/diag_qdonor2_ia.py` ??`.log`/`.json`, `BGRUN END rc=0 after 116s`, 11/0.** Census delta across `build_index_array` = `{IndexArray +1, Node +1}` and nothing else (the "stray wire" sub-alternative REFUTED), but **`es_c` = 0**: `es_a` 1 ??IA ??0 ??`create_control` (#23070 `index`) ??0 ??**delete the Index Array ??still 0**. ?뵶 **So my own explanation ("the unwired Index Array broke it; delete it") is REFUTED on its own falsification criterion, and the review's alternative stands ??an op run of the 1304-`Connect Wire` family perturbs compile state (the cycle-23 family, `docs/NAMES.md:912-921`), and P8 was unsatisfiable by construction anyway.** Every scratch is therefore still byte-identical to S1 on disk (`DIAG_qdonor2_044137.vi`, `DIAG_qdonor2s_044639.vi`, `DIAG_qdonor2ia_050052.vi`, all md5 `3e3d23ce??, 474202 B). Refs 5/5/0, 11/11/0, 11/11/0 live in the three runs. ?좑툘 Handles 33,978 ??63,656 / 34,172 ??63,590 / 33,976 ??63,544 (each run restarts its own instance; **LabVIEW restarted again at the end of the session**). ?뵶 **RE-SPLIT TRIGGER FIRED (CLAUDE.md "Big or blocked work is SPLIT??, clause 3): the same stage failed twice at the same place and left no artefact, so the next cycle's FIRST act is a DECOMPOSITION PLAN ??that plan is a design decision and was deliberately NOT written by this material session.**
  owner_c52m1: # ??**RELEASED 2026-09-20 04:2x ??cycle 52 material, TWO READ-ONLY measurements, BOTH COMPLETE. NOTHING WAS BUILT ON ANY ARTEFACT, NO VI WAS RUN (34(f)), no motor/ASI/camera/GUI.** ?럦 **(1) `tools/bench/verify_d1_s2.py` ??`tools/bench/verify_d1_s2.log` / `.json`, `BGRUN END rc=0 after 825s`, 23 pass / 0 fail ??THE S2 ARTEFACT IS VERIFIED, cycle 51's two unrun gates included.** `claudeDev\D1_s2_loops.vi` md5 `6ff19497f2309e007a214660bb64b911` / 475707 B; census re-read FROM THE SAVED FILE = Diagram 173 쨌 WhileLoop 6 쨌 SubVI 97 쨌 Comparison 17 쨌 LoopTunnel 135 쨌 Wire 1905 (S1 = 170/3/97/14/132/1899); child-process **ExecState COLD 1 / PRELOADED 1** (cycle 51's G12, now run); **COLD SubVI TABLE 97 rows vs the ORIGINAL's 98, EXACTLY the ORIGINAL minus (639, 22700), 0 missing / 0 extra / 0 changed, 0 rows into `background VIs_COPY`, 0 empty** (cycle 51's G15, now run, 29(g) satisfied). ?뵶 **LOOP IDENTITY SETTLED ??the cycle-51 worry about `WhileLoop #10170` is REFUTED: S1 holds WhileLoops {637, 15173, 25380} and S2 holds {637, 15173, 25380, **10170, 23032, 23041**}, so #10170 is NEW** (a new object reusing a low uid, `tools/gscript.py:2353-2356`). All three new loops are owned by `Diagram #686`; ownership read from `loop_end_ref`'s echoed `LoopUID` **and** `owner_of`, never by array index: #23080 ??Diagram#23058 ??WhileLoop#23032 쨌 #23246 ??Diagram#23166 ??WhileLoop#10170 쨌 #23456 ??Diagram#23405 ??WhileLoop#23041, each driven by one of the three new Comparisons {23035, 10171, 23042} on the matching wire {23145, 23310, 23489}; all three A3 re-reads **READ** (err/errs empty). The three shared loops are byte-for-byte unchanged (637: #648/w3457 쨌 15173: #15276/w19456 쨌 25380: #25410/w1737, identical in both files). ??**(2) `tools/bench/diag_queue_donor.py` ??same-named log/json, `BGRUN END rc=0 after 154s`, 12 pass / 0 fail (Pre-decided 35(b), FACTS ONLY ??no donor picked, no queue stage written).** TWO built ops place a constant (`OpCreateConst_v0.vi` 12412 B, `OpCreateConstOnTerm_v0.vi` 17330 B). On a scratch copy of S1: `queue_node('obtain')` **ACCEPTS** a node's named output terminal (#8486 `x+1` ??`Obtain Queue` #23032) **and a WhileLoop's outer named terminal** (#637 `current image number` ??#23038), and **REFUSES a diagram constant ??`error 1057: To More Specific Class in OpQueueObtain_v0.vi`**: the constant `OpCreateConst_v0` placed (#23258, class `Constant`, owner Diagram#686) is **not in `AbstractDiagram.Nodes[]` and exposes NO named source terminal**. `create_control` produced no ControlTerminal on the one unwired named input found (#250 t2 `error in (no error)`), so that shape is **NOT MEASURED**. Scratch `claudeDev\DIAG_qdonor_042234.vi`, md5 `cbdc6cfcc260bad4c79b7b47a6c339c5`, 475834 B, ExecState 1, saved. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859`, `D1_s1_copy.vi` `3e3d23ce?? and `D1_s2_loops.vi` `6ff19497?? all unchanged after both runs; refs 6 opened / 6 closed / 0 live in each. ?좑툘 Handles 34,281 before ??60,234 after run 2 (each child restarts its own instance; LabVIEW restarted at the end of the session).
  owner_c51m2: # ??**RELEASED 2026-09-20 04:0x by the cycle-52 material session. WHAT ACTUALLY HAPPENED: the build RAN and SAVED its artefact** ??`claudeDev\D1_s2_loops.vi` md5 `6ff19497f2309e007a214660bb64b911`, 475707 B, with G8/G8w/G8s/G9/G10/G11 PASS (Diagram 173, WhileLoop 6, SubVI 97, Comparison 17, LoopTunnel 135, Wire 1905; ExecState 1 before the save) ??and then **the session exited at 03:55 and killed its own child mid-verification**: the post-save gates **G12 (child COLD/PRELOAD ExecState) and G15 (the SubVI TABLE acceptance gate) NEVER RAN**, and `tools/bench/stage_d1_s2_loops.log` simply stops inside the cold re-read. That is OPEN 54(b). The recipe is NOT re-run; cycle 52 verifies the file it left. Original record follows. ??cycle 51 material pass 2: the two ACCEPTED prior-art fixes are IN `tools/recipes/stage_d1_s2_loops.py` (437 lines, AST+import OK `tools/bench/c51m2_astcheck.log`, 25 gate sites) ??**A3** every conditional-terminal readback goes through `cond_read()` (`:177`), which scores `OpLoopEndRef_v0`'s four error columns and reports **UNREAD** as a third outcome no gate accepts, on all three loops plus the final by-uid re-read; **A4** the SubVI COUNT is demoted to an observation (G8s) and the acceptance gate is S1's COLD SubVI **TABLE** vs the ORIGINAL (`:350`, `cold_subvi_table`/`compare_subvi_tables`, FATAL G15). Contract also now gates **LoopTunnel 132 ??135** FATAL and REPORTS **Wire 1899 ??1905**. Both `FIXED:` release lines written under `## What was done with it` in `archive/peer/2026-09-20-priorart-d1-s2-loops.md`. Launching `tools/bench/stage_d1_s2_loops.log`.
  owner_c51m1: # ??**RELEASED 2026-09-20 03:4x ??LabVIEW WAS NEVER TOUCHED: no `.vi` opened, no COM call, no GUI action, no motor/ASI/camera.** Cycle 51 material, D1 stage S2 (Pre-decided 34) WRITTEN BUT **NOT LAUNCHED**: `tools/recipes/stage_d1_s2_loops.py`, **311 lines, sha256 `7eb482beab051629d0e8b8c7bf7e0a3c51750aafbf6c1eee658d625c3583d993`**, AST OK (`tools/bench/c51_astcheck.log`, 19 gate sites) ??three While loops on `Diagram #686` at (2600,2600)/(2600,3400)/(2600,4200), each scaffolded `OpCreateEqual_v0`(operand BY NAME `#8486 'x+1'`) ??`OpStopFromNode_v0`, ONE `g.save()`, no `move_in`/queue/re-wiring/new op, no VI run. ?뵶 **THE PRIOR-ART LAUNCH GATE REFUSES IT**: `archive/peer/2026-09-20-priorart-d1-s2-loops.md` (ANSWERED, opus/high, **$4.7775, 530 s**, log `tools/bench/priorart_d1-s2-loops.log`) returned `PRIOR-ART: contradicted` + `PRIOR-ART: unread-evidence` ??(A3) the imported `LOOP_END_REF` readback drops `OpLoopEndRef_v0`'s `err`/`errs` columns that Pre-decided 14 (`docs/cycle27-plan.md:147-150`) requires be reported UNREAD, and (A4) the stage gates SubVI by class COUNT where 29(g) (`docs/cycle27-plan.md:629-641`) makes the ORIGINAL's SubVI **table** the acceptance reference (the built FATAL instrument is `stage_d1_s1.py:182-188`/`:377-400`). One review round only; **the `REFUTED:`/`FIXED:` release is the judgement session's call, not a material session's.** ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after (`tools/bench/c51_facts.log`); S1 artefact `3e3d23ce?? 474202 B untouched; `claudeDev\D1_s2_loops.vi` does **NOT** exist; refs opened 0 / closed 0 / live 0.
  owner_c50m1: # ??**RELEASED 2026-09-20 03:1x ??cycle-50 material session, Pre-decided 34(j) DIAGNOSTIC `tools/bench/diag_s2_scaffold.py` (NOT a recipe, never under `tools/recipes/`), log `tools/bench/diag_s2_scaffold.log`, readings `tools/bench/diag_s2_scaffold.json`, `BGRUN END rc=1 after 246s` (rc=1 = bgrun's INNER-FAILURE flag on gate G12, not a crash). GATES 13 pass / 1 fail.** ?럦 **READING 1 = ExecState 1**: on a scratch copy of `D1_s1_copy.vi`, ONE new While loop on `Diagram #686` (WhileLoop **#23032**, body Diagram **#23058**) scaffolded by `OpCreateEqual_v0` + `OpStopFromNode_v0` reads **ExecState 1** with the ORIGINAL preloaded and **SAVES**: `claudeDev\DIAG_s2scaffold_030829.vi`, md5 **`eddb3e15e5b0aa673fc2bf59eadd67e2`**, **475,422 B**. Operand: node **#8486 `x+1`** (Function, Nodes[0] of #686) ??the brief's pre-selected `#637 'frame index'` is NOT a named source terminal there (#637's outer feed is an UNNAMED tunnel), so the pre-decided census-order walk took the first scalar-shaped name on the first attempt. Conditional terminal **#23080, wire 0 ??23145**, same uid the Comparison **#23035** sources. ?뵶 **READING 2 = ExecState 0** after `move_in #48` (7 terminals, all 7 wired, SEVERED by the move) into that body ??`g.save()` refused (`RuntimeError: refusing to save a BROKEN VI`), `allow_broken` never set, `gui_save` never called; the on-disk file is still reading 1's bytes. Child-process re-reads of that saved file: COLD **1**, PRELOADED **1**. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after; refs opened 8 / closed 8 / live 0; handles 34278 ??34140 (30976 after the run's own restart). NO VI WAS RUN (34(f)); no motor, no ASI, no camera, no GUI action.
  owner_c49s3: # ??**RELEASED ??LabVIEW WAS NEVER TOUCHED. No .vi opened, no COM call, no GUI action, no peer, no review, no launch.** Cycle 49 material pass 2: `tools/recipes/stage_d1_s2.py` now carries all FIVE round-2 prior-art fixes plus Pre-decided 33's A5 ??**1956 lines, sha256 `789a5c965ded3942d45f149868bd40571e6519941c33d58b8f1c291674743eda`** (was `71f12e121f95`). A3's table 10 ??**16 rows covering all 14 ops the completeness scan names** (the scan now reads WHOLE lines: at `_grep`'s 400-char truncation it saw 5 ops, MEASURED `tools/bench/c49s3_capscan.log`); the six added ops are all READERS/CREATORS, so **32(d) rule (1) still has no winner and `stop_after_a` stands**. Dead citations replaced (`docs/s0-diff.md:46` was the D22 row; `a move CUTS` matched nothing) by `docs/d1-route-b-plan.md:57-58` + `:67`; the absence-assertion at the `OpStopFromNode_v0` row replaced by the three files that MEASURE "Nodes[] excludes constants"; the scaffold operand no longer picked by ordinal (`#5058` t3 is `Bead is good? array out`, an ARRAY ??`docs/frame-loop-wire-graph.md:171`) and C6 is now C6s+C6/C6w+**C8 FATAL ExecState 1 before the save**; v7's own advance statement (`build_d1_routeb_v7.py:131-135`) cited as the stage's real blocker. Contract re-counted from the file's own `gate(` sites: **A 17 쨌 ACD-full 74**. Verified by `tools/bench/c49s3_astcheck2.log` (AST OK) and `c49s3_citecheck.log` (23/23 citation greps match, 0 EMPTY). ?뵶 THE RECIPE WAS NOT LAUNCHED (round 3 runs next cycle).
  owner_c49s2: # ??**RELEASED ??LabVIEW WAS NEVER TOUCHED THIS CYCLE.** Cycle 49 material: `tools/recipes/stage_d1_s2.py` now implements Pre-decided **32** (scaffold AFTER `move_in`; `OpExitWhile_v0` REFUSED and `SCAFFOLD_STOP_CONTROL` deleted; A3 rebuilt as a measured table over 10 candidate ops + 32(d)'s selection rule; `stop_after_a` branch; 32(f) tunnel-IndexMode read in phase D), AST-checked, sha256 `71f12e121f95`. ?뵶 **THE RUN NEVER LAUNCHED: the prior-art LAUNCH GATE refuses the edited bytes** ??verbatim refusal + the measured mechanism in `archive/2026-09-20-status-cycle49-relocate.md` 짠2. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after (`tools/bench/c49_facts.log`); S1 artefact untouched (`3e3d23ce??, 474202 B); `D1_s2_loops.vi` does NOT exist; refs opened 0 / closed 0 / live 0; handles 34276. No motor, no ASI, no camera, no GUI action.
  owner_c48s1cd: # ??RELEASED ??cycle 48's S1 delivery record RELOCATED VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle49-relocate.md` 짠1. Summary: S1 phases C+D 20 pass / 0 fail, `BGRUN END rc=0 after 679s`, `claudeDev\D1_s1_copy.vi` md5 `3e3d23cefd3a334001aa9d6156bf1aee` 474202 B, ORIGINAL md5 unchanged, D5 FATAL PASS.
  lock_history: # ?뵷 **FIVE LOCK KEYS RELOCATED VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle48-lockkeys.md` 짠1?벬?** ??`owner_c47s1` (cycle 47's REFUSED S1 launch; ?좑툘 superseded in fact by `owner_c48s1cd` above, and its "the ORIGINAL cannot be read" claim is FALSE), `owner_c47t2` (T2's offline RSRC block diff: 45 blocks, 43 identical, only `LIvi`/`LIbd` +920 B), `owner_c46s1cd`, `owner_c46_closed` (the three released cycle-46 keys) and the previous `lock_history` (eight older keys). Four of the five were already pointers into the cycle-36/39/44/45/46/47 relocation files.
  motor:     # limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed; an 18:13 D0 run then moved the magnet to 30 mm and they held. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠2; detail ??`archive/2026-09-18-status-cycle34-n1.md` 짠1.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without `tools/bench/motor_session.json` **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 74/74).
??The 15:37 run (8/10, L4 a FALSE PASS) is SUPERSEDED by the 16:0x retest ??`??cycle29-retro-trap.md` 짠7. Limits LEFT ON (PI TMN 0 / TMX 39 **in RAM**, ASI SL/SU persistent); **an 18:13 D0 run then moved the magnet to 30 mm and they held**.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1 (lock block above). **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Earlier: `archive/2026-09-18-status-cycle22-close.md` 짠2 쨌 `?쫈ycle20-close.md` 짠1?벬? 쨌 `?쫈ycle21-wire-semantics.md` 짠9/짠9a/짠10 쨌 `?쫈ycle19-flatseq.md`.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; the five CLOSED items (32 쨌 55 쨌 56 쨌 51/52/52a 쨌 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` 짠5, which forwards to `??026-09-18-status-cycle36-relocate.md` 짠5?벬?. ?좑툘 Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.

## NEXT
?럦 **D1 STAGE S2 IS DELIVERED AND ACCEPTED** ??`claudeDev\D1_s2_loops.vi`, md5 `6ff19497f2309e007a214660bb64b911`, 475,707 B; `ExecState` COLD **1** / PRELOADED **1** re-read from the SAVED file; census Diagram 173 쨌 WhileLoop 6 쨌 SubVI 97 쨌 Comparison 17 쨌 LoopTunnel 135 쨌 Wire 1905; SubVI **TABLE** = the ORIGINAL minus the required `(639, 22700)` TIFF row, missing 0 / extra 0 / changed 0. **Rule 1a intact**: the three new loops are exactly `{10170, 23032, 23041}` (`#10170` is NEW, reusing a freed low uid ??`tools/gscript.py:2353-2356`), and every pre-existing loop's conditional terminal and wire are identical in S1 and S2. Level: **STRUCTURAL** ??no VI was run (34(f)). Evidence: cycle 51's own `tools/bench/stage_d1_s2_loops.log` **35/0** (G15 FATAL PASS) **and** cycle 52's independent `tools/bench/verify_d1_s2.{log,json}` **23/0** ??two separate runs, same numbers. Record `docs/cycle27-plan.md` Pre-decided **37(a)??c)**.
?뵶 **ONE THING IS OWED BEFORE THE S3 BUILD: the mandatory peer review of the P6 failed prediction** (`tools/bench/diag_movein_set.log:57`, `  **FAIL**  P6` ??the gate asserted `#48` is on `Diagram #686`, the machine said `#639`). Cycle 52's Pre-decided 37(f) ruled it not owed; the cycle-52 retrospective overruled that and **the ruling is withdrawn** ??judgement does not excuse a mechanical rule. Dispatch `-Agent claude -Role hypothesis` first; it is cheap and it bears on S3 directly, since P6's subject is where `#48` actually lives.
??**NOTHING ELSE GATES THE S3 BUILD.** `py tools/violations.py` (run 2026-09-20 05:3x): **0 slugs awaiting a response** ??`device-failed` answered 05:34 and `repeated-failure-class` 03:56, both no-device under the 2026-09-18 08:53 suspension; `py tools/doc_lint.py` L2 PASS (1248 citations, none dangling), L3 71/110 lines, L4/L8 PASS. Cycle 52's retrospective covers cycles 51 **and** 52, so `guard_cycle`'s retro requirement is discharged for both.
?뵶 **FIRST ACT ??BUILD S3 AS Pre-decided 37(g) DEFINES IT: `claudeDev\D1_s3_loop15.vi` = the WHOLE 1.5 FOCUS node set moved into loop a `#23032` (body `#23058`, 37(h)) AND re-wired, ONE script, ONE save.** The set is `CaseStructure #10407` + `#48 ASI_adjust focus-subvi.vi` + `#3529` + `#3560` + `#3447` + shift registers `#4334/#4344` (VISA) and `#4256/#4274` (position) ??all on **`Diagram #639`**, the frame-loop body, **not `#686`** (37(f)); `#3529` is a `ControlReferenceConstant`. Start from `D1_s2_loops.vi`, gate against the ORIGINAL (29(g)), re-wire in batches of 10??5 rows from `tools/bench/d1_rewire_sources.json`, census + readings JSON per phase, one `g.save()` with `allow_broken` False. **Pass criteria, all measurable, none invented:** per moved node, the **count of WIRED TERMINALS returns to its pre-move value** (recorded per node before the first `move_in`; never a Wire count ??37(e)); SubVI **TABLE** still = ORIGINAL minus `(639, 22700)`; `WhileLoop` still 6; `ExecState` 1 before the save and **COLD 1 / PRELOADED 1** on the saved file. The `LoopTunnel` delta is whatever the border crossings require ??**measure it, do not predict it.**
?뵶 **`move_in` IS ONE NODE PER CALL AND SEVERS EVERY WIRE ON THE MOVED NODE, IN EITHER ORDER (37(d)) ??AND A WIRE COUNT CAN NEVER DETECT A CUT (37(e)).** Measured: the `Wire` census held **1905 ??1905 ??1905** while both ends of wire 4833 went unwired and uid 4833 stayed in the Wire list. **Every re-wiring gate counts WIRED TERMINALS, never wires.** This is the likeliest silent killer behind v3?뭭7, and it retires 34(e)'s "one node per stage": the 1.5 set has no smaller legal unit than itself.
?뵶 **SECOND ACT ??REPAIR `guard_peer`'s BLIND SPOT, BOTH ENDS (37(i)).** `FAILURE_RE` (`tools/hooks/guard_peer.py:73`) matches the documented `  FAIL  ` but not the `  **FAIL**  ` the cycle-50/52 diagnostics print (`tools/bench/diag_movein_set.log:57`), so a failing run passed the mandatory-review gate unseen. Make the diagnostics emit `  FAIL  ` **and** widen the regex to `\*{0,2}FAIL`, then self-test against that log and a passing one. A repair of an existing gate, not a new device (recorded `docs/violation-decisions.md`, `## device-failed ??2026-09-20 05:34`). **Same act, same fault class:** `DEC_RE` (`tools/violations.py:94`) silently ignores a malformed decision header, so at least two blocks in that file register no decision at all ??re-head them, but only with the count change measured first, since it can clear or re-arm a due slug.
?윞 **THE QUEUE PATH IS ANSWERED AS FAR AS THE FLEET CAN ANSWER IT, AND IT WAITS BEHIND S3 (Pre-decided 36).** `queue_node('obtain')` accepts only a real NODE: a diagram constant, a **scalar** ControlTerminal and a **cluster** ControlTerminal moved onto `#686` are all measured REFUSED (`error 1057`), and `OpCreateConstOnTerm_v0` is loop-body-only by an intrinsic `Loop.Diagram` downcast (`error 1055`; positive control inside `#637` passed). **No built op reads `Terminal.DataType`**, so the next donor step is a **trial census** over the 18 `#686` nodes independent of `#637` (36(c)/(d)). **No queue stage is written before it.**
?뵶 **EVERY ADDRESS IS A uid OR AN EXACT NAME, RE-READ IMMEDIATELY BEFORE USE (34(h)) ??AND EVERY STAGE REPORT RE-READS BY uid OR BY OWNERSHIP TRAVERSAL, NEVER BY INDEX.** `stage_d1_s2_loops.py`'s closing report broke the second half and printed a pre-existing loop's uid beside a new loop's conditional terminal; the build itself was correct (37(b)). Index-addressing remains the strongest rival explanation for the ten v3?뭭7 deaths.
?뵶 **NO INTERMEDIATE ARTEFACT IS EVER RUN** (34(f)) ??a scaffolded loop runs once, a sentinel loop with no producer blocks forever. Both are legal to SAVE; neither is legal to RUN. **No new op, no new device** (Pre-decided 2; user 2026-09-18 08:53). **The retrospective is the LAST thing a session runs**, in the background: `py tools/bgrun.py --max-min 20 --log tools/bench/retro.log -- py tools/retrospective.py --cycle <N>`. Never run one early and never pay a previous cycle's retro debt up front (OPEN 54(a)).
?뵶 **NEVER READ A LOG FOR A VERDICT BEFORE ITS TERMINAL LINE IS PRESENT (37(j)) ??cycle 52 learned this the expensive way.** Cycle 51's build was NOT killed: `tools/bench/stage_d1_s2_loops.log` is **300 lines, last written 04:06**, ending `35 pass / 0 fail` 쨌 `BGRUN END rc=0 after 776s` with G15 FATAL PASS. Cycle 52 read its tail at 03:56 while it was still being written (12,978 B, mtime 03:55), inferred "killed mid-verification", and spent an 825 s re-verification on gates that were passing as it read. **`BGRUN END`/`TIMEOUT` is the only proof a run finished.** 54(b) *was* breached at 03:55:17 ??a session exited with a child running ??but bgrun's breakaway detach rescued the work; **still hold the turn open until the child lands**, because the rescue is a mechanism covering for a broken rule, not the rule working.
?윞 **Two `doc_lint` items left open deliberately**: `L6`'s 48 blank dispositions are ALL pre-2026-09-15 ??the three reviews of 2026-09-20 are disposed; `L2b` `docs/NAMES.md:1022` points past the end of `docs/toolkit-capabilities.md`. Neither gates anything.
?뮠 **FOR THE USER ??three facts, not faults.** (1) Judgement-session spend still dominates review spend ??8 : 1 and `audit_cycle`'s C4 understates it ??7횞 (cycle 49: real **$61.07**, `tools/bench/cycle_runner.log:62`, against an audited $9.54); only you can act on that. (2) **Two D1 stages are now on disk and openable** ??`claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` ??but **neither may be RUN**: they are structural intermediates (34(f)). (3) The queue half of D1 needs a donor the toolkit cannot currently type; that is now measured and bounded (Pre-decided 36), waiting behind the move stages rather than stuck.
- ?뵷 **Cycle 50's NEXT relocated VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle52-relocate.md` 짠1**, with 짠2 recording what cycle 52 measured against it. ?좑툘 **NEXT RELOCATION OWED: the four cycle-52 lock keys** (`owner_c52m1/m2/m3` + the released `owner_c51m2`) are now the bulk of this file by volume ??STATUS is 71 LINES but they are paragraph-length; move them verbatim at the next cycle's close. Also: **cycle 49's NEXT ??`archive/2026-09-20-status-cycle50-relocate.md` 짠1.** Earlier ones: `archive/2026-09-20-status-cycle49-relocate.md` 짠2/짠3 쨌 `archive/2026-09-20-status-cycle48-lockkeys.md` 쨌 `archive/2026-09-19-status-cycle46-relocate.md` 짠2?벬? ??all unchanged and still current.
- ?숋툘 **Operating facts, keep:** the ORIGINAL is readable via `py tools/bgrun.py --material ??-- python -u <script>`; `tools/hash_probe.py` is the read-only md5/sha256/size probe (34(k)); and an UNSAVED in-memory edit can be read ONLY in-instance under `Preload` ??the child-process `ExecState` read applies to files on disk (34(l)).
- ?좑툘 **BINDING from the 4th outcome review:** every cycle must end with saved files and md5s in a log. Cycle 50 met it with `claudeDev\DIAG_s2scaffold_030829.vi` (`eddb3e15e5b0aa673fc2bf59eadd67e2`) and `tools/bench/diag_s2_scaffold.json`. **Three USER-ONLY decisions remain open and are NOT blockers**: OPEN 53's physical-zero question before any D1 motor-moving run; schedule-or-descope requirement 1; place-or-descope the item at its `:126`.
- ?윟 **Cycle 46's measurements are `docs/cycle27-plan.md` Pre-decided 29(a)??j); do not restate them here.** The two that bind every stage: `gscript.save()` reaches `SaveInstrument` ONLY at `ExecState != 0` (`allow_broken=True` banned), and `shutil.copy2(ORIGINAL, claudeDev\??` SILENTLY RE-BINDS 22 SubVI calls and loses 8 ??**every stage gate compares to the ORIGINAL, never to a copy** (29(g)).
- ?넅 **OPEN from cycle 46, all live:** (a) `claudeDev\background VIs_COPY\` = 94 `.vi`, an unmanaged duplicate hierarchy on the build path; (b) `logclass.py` counts `selftest_*.log` as a build; (c) `gui_save`'s Ctrl+S bypasses `lv_gui.ps1`. **Unchanged from cycle 34, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none.
## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

I have read the recipe, the plan sections it cites, the measured JSON behind (X1), both prior route recipes, their ten run logs, and the three archived peer exchanges on this stage. Here is the review.

---

# PRIOR-ART REVIEW — `tools/recipes/stage_d1_s3_focus.py` @ sha256 `253212c5…`

Nothing was built, edited, run or locked; no `.vi` was opened; no LabVIEW was touched.

---

## PART A — THE DIRECTION

### A1 — SETTLED ALREADY. The three "unwirable" rows are not a new conflict: the project decided in **code** that `cross-loop` rows are not wired by a move stage, and has said so in every run log since run 2

`(X1)` presents its three rows as an arithmetic conflict discovered against the brief. The classification and its consequence were fixed long before:

> `tools/recipes/build_d1_v0.py:943` — `REWIRE_ACTIONS = ("same-loop", "from-kernel", "from-const", "from-sr", "to-sr", "from-ctl", "from-tunnel")` — **`cross-loop` is absent by construction.**
> `tools/recipes/build_d1_v0.py:976-977` — *"F1 rows to re-wire: {len(rows)} (the other … are source-side, from-stay or cross-loop - queue endpoints, **the stage after this one**)"*, repeated at `tools/recipes/build_d1_routeb_v5.py:1117-1118` and printed by every run, e.g. `tools/bench/build_d1_routeb_v0_run3.log:313` — *"S3w rows to connect: 66 (the other 43 are source-side, from-stay or cross-loop = queue endpoints)"*.

And the *content* of (X1) — each of `#10407`'s non-internal inputs, by name, with its provenance — is `docs/d1-build-plan.md` §6, written before route B existed:

> `docs/d1-build-plan.md:407-408` — *"The other inputs are NOT kernel-derived (`focus_other_inputs`, 9 rows): **t0 selector ← `#10686 And` (the schedule, evaluated in 1.2)**; **t1 `# slices in stack` ← LoopTunnel #9641, IndexMode 0, loop-invariant**"*; `:404-406` — t2 is the measured **1-DBL** `Q_focus` payload; `docs/d1-build-plan.md:554` names `Q_focus` as its carrier.

**What this covers:** the claim that (X1) is a conflict between the brief and the measured files. It is not — it is the project's own decided split, and the consequence is that **gate `W-10407` ("the wired-terminal count returns to its pre-move value") was never a sound acceptance criterion for a move stage**, for the same reason route A's ledger counts 66 rows and not 109. The pass criterion to write is *the 4 internal rows return; the `cross-loop` rows are reported as queue endpoints*, which is what 37(g) should have said.

**What this does NOT cover:** it does not say the *stage* is wrong, and it does not touch (X2) or (X3).

### A2 — REFUTED ALREADY. The one prior review that authorised building loop 1.5 on its own made that conditional on the queues existing, and Pre-decided 36 removes the condition

The atomic-1.5 boundary comes from `archive/peer/2026-09-20-d1-s2-boundary-recut.md`. Its answer 4 is the source of "loop 1.5 is buildable alone" — and it says why:

> `archive/peer/2026-09-20-d1-s2-boundary-recut.md:118` — *"**On the dependency you flagged — it does not exist at build time.** **All eight Obtains sit at top level on `Diagram #686`** … So 1.5's Dequeue takes its refnum from an Obtain that exists whether or not 1.2 does … **Loop `#48` is fully buildable with `#5058`'s loop absent.**"*

Against that, this cycle's own decision:

> `docs/cycle27-plan.md:1059` (Pre-decided 36(d)) — the donor trial census *"is **not on the critical path — no queue stage is written before it, and it waits behind S3**."*

So the premise the boundary rests on (the eight Obtains are already on `#686`) is false for S3: no Obtain exists, no Dequeue can be made, and the three rows (X1) names are precisely the endpoints that premise was about. The same review's own falsifier and cheapest test were run and came back the wrong way for this shape: `:133` predicted *"Step 4 → if still 1, the loop and its re-wiring are separable … if **0**, CLAIM B's bare-Required premise is confirmed empirically for `#48`"* — measured **0** (cycle 50, `docs/cycle27-plan.md:951`-area reading 2; cycle 52 `tools/bench/diag_movein_set.log:101`).

Route A's recipe records what the transport choice buys, and it is exactly the three rows S3 defers:

> `tools/recipes/build_d1_v0.py:155` — `TRANSPORT = "queue"`; `:424-425` — *"The choice settles **1.5's wake-up, the reverse crossing AND the stop read** in the three new loops **at once**, and it is JUDGEMENT."*

**Still applies?** Yes. Nothing since 2026-09-20 has put an Obtain on `#686`.

### A3 — CONTRADICTED (two, both with both sides quotable)

**(a) 37(g)'s justification for making S3 atomic is that a part-moved set leaves no file — and this stage predicts it leaves no file.**

> `docs/cycle27-plan.md:1120-1122` — *"(d) severs every wire whichever order is used, and **an intermediate at `ExecState` 0 cannot be saved — so a part-moved set leaves no file, which the split rule forbids outright.** The stage is atomic because the machine makes it so."*

against the recipe's own contract:

> `tools/recipes/stage_d1_s3_focus.py:149-151` — *"G15 `ExecState` == 1 immediately before the save … **PREDICTED 0**"* / *"G16 ONE `g.save()` … **PREDICTED REFUSED.**"*

The premise (atomic ⇒ savable) and the conclusion (atomic, and unsavable) cannot both stand. And the rule they both cite is unambiguous: `CLAUDE.md:383` — *"**A step is not done until it has left a file.**"* The trigger is already armed, by the machine, in STATUS's own `owner_c52m2` key (*"RE-SPLIT TRIGGER FIRED … the next cycle's FIRST act is a DECOMPOSITION PLAN"*), and `CLAUDE.md:388-392` says that plan is the next cycle's first act and that *"a full-length retry under a new file name … is forbidden"*. A 954-line single-save stage whose contract predicts three FATAL failures is the shape that rule was written against.

**(b) `#10407` t6 is not "internal". The measured file gives that wire a second end on a node this plan leaves behind.**

> `tools/recipes/stage_d1_s3_focus.py:95` — *"Four are internal to the 1.5 set or its two shift registers (… t6 → SR `#4256`)."*

against

> `tools/bench/d1_rewire_sources.json:1892-1917` — row `uid 10407, i 6`, wire **9113**, `"other_ends": [{"kind":"node","diagram":"43","uid":12589,"i":1,…}]`, `action "to-sr"`.
> `docs/d1-build-plan.md:307` — *"`12589` … **stays 1.1** (§11c) … t1 ← `#10407` t6 w9113 (**the reverse crossing**) … the crossing becomes `Q_focusback`"*; `:264` puts `#12589` on **stop path A** into `#11639` → `#637`'s conditional terminal.

So wiring t6 into the new register restores one of that wire's two ends; the other end is a documented queue crossing on the original loop's **stop path**, and the stage severs it. That is a fourth unwirable row, an additional bare terminal on `#637` that (X2) does not count, and a rule-1a exposure on a path this stage does not otherwise touch.

### A4 — UNREAD EVIDENCE. `docs/d1-build-plan.md` §6 and route B run 3's ledger

The plan cites `docs/d1-build-plan.md:250, :305-306, :330-332, :359-360` — the *move table* rows — and never §6 `:396-421`, **the section that specifies row 1.5** and names every input (X1) re-derives, including `:402-403` (*"Both SR pairs are re-created on the new loop"*, which is what the recipe does) and `:418` (*"A refnum crossing a loop border auto-creates its tunnel"*, which bears directly on G13's un-predicted `LoopTunnel` delta).

Second: `docs/d1-route-b-plan.md:79` / `tools/bench/build_d1_routeb_v0_run3.log:532` — **`S3w ledger: attempted 66, WIRED 63, FAILED 0, NO-ROUTE 3`**, measured on the real working copy, covering these rows. A stage whose new contribution is a re-wiring pass should state what that pass already measured.

---

## PART B — THE ARTEFACT

### B1 — ALREADY BUILT (reported as a FINDING, **no slug**)

The move of this exact set is not new: route B moved `#10407` + `#3529`/`#3560`/`#3447` into 1.5 (`docs/d1-route-b-plan.md:166-167`), and the landings passed in the real VI (`tools/bench/build_d1_routeb_v7_run10.log:116-176`, as verified at `archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1195`). The recipe cites v7 and declines to import it, which `docs/cycle27-plan.md:936-939` (34(i)) requires. No slug: the reuse question is already disposed.

### B2 — ALREADY FAILED. The last step of this stage is the step with a 3-for-3 failure record, and the plan predicts the same outcome without changing the cause

- Cycle 50: one loop + `move_in #48` → `ExecState` 0, `g.save()` refused (`docs/cycle27-plan.md:951`-area; the diagnostic's own reading 2).
- Cycle 52: `#3529` then `#48` moved → `ExecState` 0, save refused verbatim, **the scratch stayed byte-identical to S2** — `tools/bench/diag_movein_set.log:101` onward.
- Run 10: the save itself diverted to `gui_save` and died — `docs/cycle27-plan.md:451-453` (*"The E3 save diverted to `gui_save` and died … so no restart, no reopen and no fresh-instance census ever happened"*).

The new plan's answer to this is a SALVAGE `g.save()` after a FATAL gate (`tools/recipes/stage_d1_s3_focus.py:163-165`), which by `gscript.save`'s own predicate cannot succeed at `ExecState` 0 — i.e. it repeats the cause rather than addressing it. What would address it is not in this stage: the queue endpoints (A2), or a boundary that ends at a legal state.

### B3 — HELPER EXISTS. `#10407` t1 is a `from-tunnel` row, and the built writer for that class wired 16 of them with a clean sink rule

The plan reports t1 as unwirable (`tools/recipes/stage_d1_s3_focus.py:97`, `tools/bench/d1_rewire_sources.json:1789` `action "from-tunnel"`, `outer_wire 9649`). The project has a built, saved, ExecState-1 op for exactly that class, and it has already been used on the real VI:

> `docs/toolkit-capabilities.md:70` — `OpConnectFromWire_v0.vi`, *"**the only writer whose SOURCE need not be a node** — what the 16 `FlatSequenceInnerTunnel` / `LeftShiftRegister` from-tunnel rows need"*; T1 measured *"branched an OUTER-diagram wire's source terminal into a node **inside a NEW While loop body** — op error `''`, sink wire 0 → 229, `Is Broken? FALSE`, `LoopTunnel 0 → 1`"*.
> `docs/d1-route-b-plan.md:107-109` — run 3 *"used for **16 from-tunnel rows**, `SINK RULE 16 OK / 0 REFUSED / 0 BAD`, every wire `Is Broken? FALSE`"* (`tools/bench/build_d1_routeb_v0_run3.log:365,:367-368,:380,:532`).

`from-tunnel` is also inside `REWIRE_ACTIONS` (`tools/recipes/build_d1_v0.py:943`), i.e. the project classifies it as re-wirable. The recipe's imported writers are `connect_nested_v1` and `wire_sr` only (`:36-42`); `OpConnectFromWire_v0` is neither used nor excluded on measured grounds. Its known defect (`T2c2`, `docs/toolkit-capabilities.md:70`) was diagnosed as a **stale terminal index**, not an op fault — and this recipe re-reads indices at every call site (`:349-351`, `:407`), which is the condition under which it worked in run 3.

### B4 — ALREADY MEASURED (reported as a FINDING, **no slug**, same citation as A4)

"Do the 1.5 rows re-wire in the real VI?" is measured: 63 WIRED / 0 FAILED / 3 NO-ROUTE, and none of the three NO-ROUTE rows is a 1.5 row (`docs/d1-route-b-plan.md:86`, `tools/bench/build_d1_routeb_v0_run3.log:532`). Route B's deaths were at `error 2` and at the save, not at these wires.

---

## What is genuinely NOT covered — say so plainly, so it is not hunted for

- **(X3) is novel.** I found no file that notes the SubVI table key carries the diagram uid, and therefore none that notes a moved SubVI necessarily re-keys. `tools/recipes/stage_d1_s1.py:389` does key `(diagram_uid, node_uid)`; `:729` passes `{TIFF_SUBVI_KEY}` as the expected-missing set; and 29(g)/37(c) were both written for stages that moved **no** SubVI (S1 deleted one, S2 moved none), so the case never arose. A grep over `docs/`, `archive/` and `tools/` for `re-key|rekey|diagram_uid` returns only census generators. **The move-aware comparison at `:807-840` is the right fix and it is new work, not prior art.**
- **The old `#637` shift-register pair being left bare** ((X2)'s second half) is also uncovered: `docs/d1-build-plan.md:402-403` says both pairs are *re-created* on the new loop, `docs/d1-route-b-plan.md:156` says registers are *"created fresh, never moved"*, and **no document names a deletion of the old pair**. Whether a bare inside terminal breaks the VI is unmeasured here; that is a hypothesis question, not a prior-art one.

---

## MACHINE-READABLE

```
PRIOR-ART: settled-already
PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-failed
PRIOR-ART: helper-exists
```

**Citations, one per finding, for the disposition:**

- `settled-already` — `tools/recipes/build_d1_v0.py:943` + `:976-977` (and `build_d1_routeb_v5.py:1117-1118`, `tools/bench/build_d1_routeb_v0_run3.log:313`) vs `tools/recipes/stage_d1_s3_focus.py:93-106`; content already at `docs/d1-build-plan.md:404-410`
- `refuted-already` — `archive/peer/2026-09-20-d1-s2-boundary-recut.md:118` (+ `:133`) vs `docs/cycle27-plan.md:1059`
- `contradicted` (no-file) — `docs/cycle27-plan.md:1120-1122` vs `tools/recipes/stage_d1_s3_focus.py:149-151`, against `CLAUDE.md:383` and `:388-392`
- `contradicted` (t6 is not internal) — `tools/recipes/stage_d1_s3_focus.py:95` vs `tools/bench/d1_rewire_sources.json:1892-1917` and `docs/d1-build-plan.md:307`, `:264`
- `unread-evidence` — `docs/d1-build-plan.md:396-421` (§6) and `tools/bench/build_d1_routeb_v0_run3.log:532`
- `already-failed` — `tools/bench/diag_movein_set.log:101` + `docs/cycle27-plan.md:451-453` vs `tools/recipes/stage_d1_s3_focus.py:163-165`
- `helper-exists` — `docs/toolkit-capabilities.md:70` and `docs/d1-route-b-plan.md:107-109` vs `tools/recipes/stage_d1_s3_focus.py:36-42`, `:97`

**The one sentence I would put to the judgement session:** the most consequential finding is not (X1) — it is that 37(g) made the stage atomic *because* an unsavable intermediate is forbidden, and this stage's own contract predicts an unsavable intermediate; on the project's own rule that makes S3-as-written a step that cannot be done, and the decomposition plan the machine already triggered is still owed.

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL, AND THE BUILD IS NOT RELEASED — cycle 53 judgement session, 2026-09-20.**

🔴 **No `REFUTED:` and no `FIXED:` line is written here, deliberately.** Those two releases exist to
let a *blocked build run*. This build is not being released, unblocked or re-armed: the stage it
encodes is **withdrawn**. Writing `FIXED:` to clear a gate on a stage I have decided not to build
would be the "a promise is not a fix" laundering CLAUDE.md §5 names. The STOP RECORD armed on sha
`253212c547b9` stays armed, and it is correct.

**Findings, each accepted, with what it changed.**

- **A1 `settled-already` — accepted, and it convicts my own pass criterion.** `cross-loop` rows are
  queue endpoints excluded by construction (`tools/recipes/build_d1_v0.py:943`, `:976-977`;
  `tools/bench/build_d1_routeb_v0_run3.log:313`). So *"per moved node, the count of WIRED TERMINALS
  returns to its pre-move value"* — written by me into STATUS `## NEXT` and into the recipe as gate
  `W-10407` — **was never a sound acceptance criterion for a move stage**, because two of `#10407`'s
  rows cannot be restored until a stage that does not yet exist has run. Withdrawn; Pre-decided 38
  replaces it with a criterion split by row class.
- **A2 `refuted-already` — accepted.** The authorisation for "loop 1.5 is buildable alone"
  (`archive/peer/2026-09-20-d1-s2-boundary-recut.md:118`) rested on *"all eight Obtains sit at top
  level on `Diagram #686`"*, a premise Pre-decided 36(d) removed when the queue path was deferred
  behind S3. The authorisation did not survive its premise and I did not notice.
- **A3(a) `contradicted` — accepted, and it is the cycle's governing finding.** A stage whose own
  contract states `PREDICTED 0` / `PREDICTED REFUSED` (`tools/recipes/stage_d1_s3_focus.py:149-151`)
  is a step that predicts it will leave no file, which `CLAUDE.md:383` forbids outright and
  `:388-392` answers with a decomposition. That the material session wrote the prediction down
  honestly is what made this catchable.
- **A3(b) `contradicted` — accepted in substance, corrected in label.** The row is real and §6 names
  **no construction verb** for it. But its measured action is `to-sr`, not `cross-loop`: `#10407` t6
  `position [internal units]` is a **source**, far end `#12589` t1, kept on row 1.1 by §11c
  (`docs/d1-build-plan.md:398`). It is an unnamed row, not a fourth crossing.
- **A4 `unread-evidence` — accepted.** `docs/d1-build-plan.md:396-421` §6 is the section that
  specifies row 1.5 and it had not been read. `:402-403` is verified. ⚠️ `:418` does **not**
  "specify" refnum border tunnels in the sense the review implies — it states that a refnum crossing
  a loop border auto-creates its tunnel, and `:419` then says this is *"a route the plan never named
  … flagged (§11.6), **not patched**"*. So §6 leaves the refnum crossings open, which strengthens
  the finding rather than weakening it.
- **B2 `already-failed` — accepted.** The SALVAGE save at `:163-165` cannot succeed at `ExecState` 0;
  it repeats cycle 50's and cycle 52's cause. Removed from the re-cut.
- **B3 `helper-exists` — accepted.** `OpConnectFromWire_v0.vi` is the only built writer whose SOURCE
  need not be a node (`docs/toolkit-capabilities.md:70`; 16 from-tunnel rows at
  `docs/d1-route-b-plan.md:107-109`). `#10407` t1 is a from-tunnel row and the recipe imported only
  `connect_nested_v1`/`wire_sr`. Pre-decided 38 requires it.
- **X3 the reviewer calls novel and right, and I agree:** the move-aware SubVI-table comparison at
  `:807-840`. The `(diagram_uid, node_uid)` key (`tools/recipes/stage_d1_s1.py:389`) re-keys when a
  SubVI is moved, so "ORIGINAL minus exactly `(639, 22700)`, missing 0 / extra 0" — my wording in
  STATUS `## NEXT` — is unsatisfiable for any stage that moves `#48`. That is a defect in the
  acceptance instrument, not in the build, and it would have failed every future move stage.

**DISPOSITION.** `tools/recipes/stage_d1_s3_focus.py` is **NOT launched** and is **kept unlaunched**
for its measurement code — the X3 comparison above — exactly as `tools/recipes/stage_d1_s2.py` was
kept. It is not re-armed on these bytes. The reviewer's closing sentence, *"the decomposition plan
the machine already triggered is still owed"*, is upheld: cycle 52's re-split trigger was answered
with a full-length single-stage retry, which clause 3 of CLAUDE.md's split rule forbids by name. The
decomposition is written as **Pre-decided 38**.
