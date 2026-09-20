---
type: status-archive
status: archived
date: 2026-09-19
tags: [hand-off, cycle42, d1, route-b, run10, error2]
---

# Cycle 42 — route-B run 10, and the review that refuted the cycle's own diagnosis

Relocated from `STATUS.md` (rule 4) at the close of cycle 42. Nothing here is rewritten; the live
one-line pointers stay in STATUS's lock block and NEXT.

## §1 — v7 was cut, repaired and launched (material steps 1 and 2)

**Step 1, ~06:5x.** `tools/recipes/build_d1_routeb_v7.py` cut from v6's bytes (v6 md5
`cb96a4df0ef71325880ff63aed47e8b9` VERIFIED before the cut, sha256 `8dbb1e69ef83…`, 181,152 B, 2607 lines).
First cut: sha256 `d808e10ce4c1…`, md5 `c30f8ade3ce3a23645d2c779a9edcac1`, 189,071 B, **2699 lines**,
`ast.parse` + `py_compile` OK. Diff vs v6: **+92 / −0 lines, 2 INSERT hunks, no existing line touched** —
`v7:308-330` docstring (the run-10 R1–R5 contract) and `v7:2170-2238` the E3 block. `gate()` sites 52 → 54.

E3 = Pre-decided 20 exactly: after the S3w ledger line and before the census,
`g.save(TARGET, allow_broken=True)` → `close_panel` → `g.reset()` (proxies released while the instance lives)
→ subprocess `tools/lv_restart.py` (the path this recipe already used at `v6:2447` and `v6:2496`;
`bench_prep.restart_labview` rejected — no COM-liveness wait) → `g.reset()` + `build_d1_v0._WALKS.clear()` →
`g.lv().Version` → `g.ensure_loaded(TARGET)`, then the EXISTING four-bucket census, unchanged in logic.
**No fallback**: on any exception `_CENSUS_FRESH=False` and a new gate FAILS (rc=1).

**The prior-art gate stopped run 10, as it stopped run 9.**
`archive/peer/2026-09-19-priorart-d1-routeb-run10.md` (ANSWERED, opus/high, **$5.6462**, 469 s; log
`tools/bench/priorart_d1_routeb_run10.log` `BGRUN END rc=0 after 470s`) = **NOT NOVEL, 7 findings / 6 slugs**.
The DIRECTION survived — *"nothing in these files has tried, refuted or decided against phasing a route-B build
across two LabVIEW instances"* — the MECHANISM did not:

| finding | slug | claim |
|---|---|---|
| F2 | `contradicted` | the skill's law (`SKILL.md:39-41`, `com-driving.md:497-499`) is **"after error 2, restart FIRST — a Ctrl+S in that state writes a STALE file"**, and E3 saves FIRST; run 9 emitted 11 `error 2` rows before the insertion point. The md5 gate compares the file with itself; a stale write would print ~51 **BARE** = a manufactured wiring catastrophe |
| F5 | `already-measured` | the census matches a PRE-restart diagram INDEX against a POST-restart one (`v7:1238-1240` vs `:2318-2319`); UIDs are the safe key |
| F1 | `already-measured` | cold `GetVIReference` on a broken-saved VI = a measured **>8-min recompile spin**, and `ensure_loaded` reaches exactly that call |
| F4 | `already-failed` | `gui_save` of a broken target has failed twice on the two signals it still trusts (focus return string; mtime alone) |
| F3 | `refuted-already` | "no keystroke save of a broken intermediate" was adopted 2026-09-15 |
| F6 | `already-built` | checkpoint→reopen→continue already exists (`build_gpu_kernel.py:140-148` + `finish_gpu_kernel.py:24-27`) with two guards v7 omitted |
| F7 | `unread-evidence` | the LabVIEW skill is cited nowhere in Pre-decided 20, STATUS NEXT or v7's own prior-art block |

Reviewer's own note: *"F2 and F5 are the two I would not release on argument alone."*

**Step 2 — the cycle-42 judgement disposition.** F1/F2/F5/F6/F7 ACCEPTED and applied **inside the single E3
edit** (they make the block correct rather than adding a second change); F3/F4 REFUTED on the ground that v7
saves over COM with `g.save`, not by keystroke. 🔴 **That refutation was WRONG — see §3.** Repaired v7: sha256
`960452920708…`, md5 `aac4f909cb7ce7246e2aad4b6fbc7134`, **2818 lines**, `py_compile` OK
(`tools/bench/v7_syntax_c42.log`). Diff vs v6 +251/−40 in 4 hunks; vs the reviewed bytes +119 lines, all inside
the docstring, the E3 block and the census. Stop record re-armed on the NEW sha and RELEASED
(`tools/stop_record.py list` → `960452920708 RELEASED`); all 7 release lines accepted verbatim.
Launch: `py tools/bgrun.py --material --max-min 60 --log tools/bench/build_d1_routeb_v7_run10.log -- py -u tools/recipes/build_d1_routeb_v7.py`.

## §2 — RUN 10 RAN 06:55:08 → 07:25:43 and FAILED at the E3 save

`tools/bench/build_d1_routeb_v7_run10.log`, `BGRUN END rc=1 after 1835s` (`:514`), **80 PASS / 1 FAIL**.

🔴 **R1, R2 and R5 ALL MISSED — the save never happened.** `g.save(TARGET, allow_broken=True)` saw ExecState 0
and diverted to `gui_save` (`gscript.py:2065-2067`), which raised `file mtime did not move after Ctrl+S on every
candidate window` (`:367`, `gscript.py:2043`). So: no save, no restart, no fresh instance, `_md5_saved` never
taken, reopen never timed, zero of the four parked diagram UIDs resolved (`:369`, post-restart indices
`[None]×5`). The single FAIL is the new fresh-instance/proven-intact gate (`:368`).

🟢 **THE REPAIRED CONTRACT HELD.** `CENSUS: 0 survived / 0 bare / 51 unread of 51 claimed` (`:370`), split
`EXACT 0, SEGMENTED 0, BARE 0, UNREAD 51` (`:371`). **A save that never landed printed ZERO bare rows** rather
than a wiring catastrophe — the second cycle running in which the honest-null contract turned a broken
measurement into an honest gap.

R3 and R4 HELD: ledger `:363` **66 attempted / 54 WIRED / 11 FAILED / 1 NO-ROUTE**, all 11 FAILED carrying
`error 2` (`:478-:488`, 10 × `report_all(Diagram)` + 1 × `report_all(WhileLoop)`) — identical in name and order
to run 9's. `Z/dZ` t0 PASSES J2 with per-diagram delta +1 (`:360`) and is WIRED (`:469`); `#2222` t0/t2/t3/t4/t5
all WIRED (`:469-:473`). Terminal crash unchanged: `count(LoopTunnel)` in `settle_index_modes` (`:491`, `:513`).
**S5 WAS NEVER REACHED — no D1 VI was saved**; the working copy is renamed aside to
`claudeDev\SCRATCH_routeb_065508_crash_072542.vi`. Original md5 `2a78e17c…` UNCHANGED before (`:13`) and after
(S6b PASS). Handles 31,106 → 50,441.

## §3 — the mandatory failed-prediction review, and what it refuted

`archive/peer/2026-09-19-routeb-run10-error2-class.md` — ANSWERED, claude/hypothesis opus effort max,
**$5.5451** (in 44 / out 43,345 / cache-create 276,487 / cache-read 3,064,901; 639 s, 40 turns). Task text
`tools/bench/task_routeb_run10_error2_class.md`. Three claims were put up to be refuted; two were.

- **CLAIM 2 REFUTED as a selection artefact.** The judgement session's census — "`report_all(Diagram)` is
  0-for-21 across three runs, it has never once succeeded" — was produced by counting only lines that PRINT
  `error 2`, an instrument that can only observe failures. The successes are at `run10.log:39` (nine successful
  `count()` calls incl. `count(Diagram)=170`, `count(Node)=626`, `count(LoopTunnel)=132`, `count(WhileLoop)=3`),
  `:44`, `:69`, `:352`, `:354`, and ~29 `move_in` calls at `:150-167`. True record: **`report_all(Diagram)`
  succeeds ~30× and then stops — a temporal signature.** The proposed "call it as the first operation" test
  *"is not decisive, and you have already run it eight times"* (`:44` is exactly that call).
- **The named rival cause: a leaked GObject refnum per matched object** inside `report_all`/`count`
  (`com-driving.md:305-312`; `docs/REFERENCES.md:126` records the `Close Reference` that was REMOVED).
- **`error 2` = LabVIEW's generic "Memory is full"** (NI KB kA00Z0000019KhWSAU). No documented NI limit on a
  VI-wide Diagram traverse; the only documented class-specific Traverse failure is the Error Ring class.
  Alternative enumerator offered: `AbstractDiagram.All Objects[]` recursed down from `VI.Block Diagram` —
  UID-keyed, no VI-wide traverse. **The right meter is LabVIEW private bytes (~770 MB, `com-driving.md:310`),
  never the handle count**; this project's standing handle-based refutation is *"a category error, not a
  refutation"*.
- **Discriminating tests, verbatim.** (1) *"in `gscript.report_all`/`count`'s exception path, on the first
  `error 2` only, log four things before re-raising — (a) a retry of the same call, (b) `report_all('SubVI')`,
  (c) `count('WhileLoop')`, (d) handles and LabVIEW private bytes"*. (2) *"`for i in range(200):
  report_all(TARGET,'Diagram')` on the pristine copy in a clean instance, logging `i` and private bytes."*
- **CLAIM 1 — mechanism CONFIRMED, conclusion OVERREACHED.** `run10.log:367` is `gui_save` raising and
  `SaveInstrument` was never attempted; but "the copy was NOT broken" is barred by Pre-decided 16b — the
  defensible form is *"the gate was UNREAD"*. Also a **fourth failure mode**: mtime did not move at all, while
  `com-driving.md:497-499` predicts a stale write WITH mtime moving, so v7's new stale-write detector
  (`v7:2280-2284`) was never exercised. On `SaveInstrument` the skill holds BOTH `com-driving.md:314-317`
  ("still works in this state… while every traverse was failing") and `:400-405` ("blocks forever on a BROKEN
  VI, 20 min"); the reviewer says decide on asymmetry — a bounded 300 s loud failure beats `gui_save`'s silent
  stale write — so `gscript.py:2068` is *"not the safer knowledge"*.
- **CLAIM 3 — the index key REFUTED, worse than the archived +1.** `FRAME_BODY_UID=639` reads Traverse index
  **43** at `run10.log:44` and **56** at `:352`/`:354` — **+13 inside one instance, no restart**.
- **(e) the process question.** Of the six other release lines in the prior-art file, `:492`
  (`FIXED: already-measured`, the parked-UID census) **rests on the same unread-callee error** — it resolves
  UIDs *with* `report_all(Diagram)` at `v7:2265`/`v7:2328`, which `run10.log:369` already shows returning
  `[None]×5`. `:494` overstates ("reuses" → re-implements inline, cites in a comment). `:491`, `:493`, `:495`
  hold (`:491`'s gate was never exercised). Reviewer's proposed rule: **a prior-art claim about our own tools
  must quote the callee.**

**The correction is in the record.** `archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499` carries a
`CORRECTION` line stating that the `REFUTED: already-failed` release was wrong, that F4 was RIGHT, and that the
refutation was made from a call-site summary without reading the callee — the error CLAUDE.md names under
*"claims about our own tools are factual claims, the ones you are most likely to be wrong about"*. The seven
release lines at `:491-497` are left untouched beside it.

## §4 — cycle-close machinery

- `py tools/audit_cycle.py` (`tools/bench/audit_cycle42.log`): 5 pass / 3 fail — **A1** `motor_gate.log` has no
  BGRUN line; **A2** unfinished `['diag_fstunnelterm_v2_panelcost.log','p2_open_copy.log','prose_cycle25.log']`;
  **A4** 65/75 annotated, 6 blank. A3 PASS (37 failing logs, none unreviewed), **A5 PASS** — original md5
  `2a78e17c449c…`, mtime 2026-09-01 12:07. 90 build logs / 103 peer logs / 75 archived reviews in 24 h.
  C7 lists 122 files not named in `docs/cycle27-plan.md`.
- `py tools/doc_ingest.py --cycle 42` (ANSWERED, $0.7964, 129 s, `archive/ingest/2026-09-19-ingest-2026-09-19.md`):
  **2 contradictions, both the same one** — STATUS's cycle-42 lock entries asserted "F3/F4 refuted in the review
  file" while the run-10 record in the same block confirmed F4's premise. Resolved by relocating those entries
  here and correcting them; STATUS no longer carries both sides.
- `py tools/violations.py --due`: nothing due.
- `doc_lint`: L2 PASS (917 citations, none dangling); L3 WARN on STATUS's length; L6 FAIL 49 blank dispositions
  (39 pre-2026-09-15 skipped as `legacy`) — both long-standing.
