---
type: archive
status: archived
date: 2026-09-18
tags: [status-narrative, cycle21, fstunnel, motor-limit-A1]
---

# Cycle 21 — the wire-semantics measurement and the ORIGINAL's §A.1 sweep (relocated from STATUS.md, rule 4)

Nothing here is deleted; STATUS keeps one line per item and points at this file.

## §1 The STATUS paragraph this replaces, VERBATIM (written after the two failed recipe runs, before the measurement)

> 🔴 **CYCLE 21 — STEP 1 DONE; STEP 2 RAN FOR THE FIRST TIME AND FAILED TWICE, IDENTICALLY. Verification level of
> the tunnel op: still NONE.** No gate refused the launch. Both runs die at `build_opfstunnelterm_v0.py:392` →
> `gscript.py:1330` `wire … count 40→40, 0 new tunnel(s), expected 41` (TMSC cast-out → PN_A `reference`); gates
> 7/8, only "no unhandled exception" failing; B4/B5/L1/L2/L3/I2/T2/L4 never executed and `OpFsInnerTunnelTerm_v0`
> never built. Logs `tools/bench/build_opfstunnelterm_v0{,_run2}.log`. **The new PN_A was issued uid 145 — the uid
> of a node deleted 7 log lines earlier** (`:46` vs `:53`) — and is addressed by uid afterwards. Material's budget
> 2/2 spent; the mandatory `-Dual` review is out (`tools/bench/peer_fstunnel_wire_fail.log`).

## §2 The cycle-20 lock record this replaces, VERBATIM

> \# CYCLE 20: held 03:15-03:17 (ONE read-only run, rc=0/54s) + 03:23-03:52 (LabVIEW NEVER STARTED). No build, no
> \# scratch VI, no motor/serial/camera, nothing saved; md5 before AND after EVERY run 3state c39f36e0…, V6
> \# 2a78e17c…; handles 30,325→30,541. Earlier cycles' lock records → the cycle19-flatseq archive §4.

Full cycle-20 close narrative: `archive/2026-09-18-status-cycle20-close.md`.

## §3 What was MEASURED on 2026-09-18 09:22 (`tools/bench/diag_fstunnel_wire_semantics.log`, `BGRUN END rc=0 after 77s`, 8/8 gates)

Read-only diagnostic on a scratch copy of the donor; no op built, nothing saved, scratch created and deleted in
the same run; both originals and the donor byte-identical before and after.

State reproduced identically to the failing run (`Terms[] PN 145 | Index Array 151 | TMSC 1044 | sinks
[157, 1319, 1326]`; seed `reference 4` → `target class` wire 1457; PN_A re-issued uid 145).

| reading | BEFORE the call | AFTER the call |
|---|---|---|
| TMSC #1044 `specific class reference` (OUTPUT) `.wire` | **384** | **384** |
| PN_A #145 `reference` (INPUT) `.wire` | **0** (`wire_err` 1055 = bare) | **384** |
| diagram Wire count | 40 | 40 |
| ExecState | — | 0 (expected: the back half is still bare) |

The residual wire #384 that was already on the cast's output before the call has exactly ONE terminal:
`Terms[0] source=True owner 'Function' uid 1044 recip w384` — i.e. a source-only stub owned by the TMSC itself,
left behind by the donor deletes (the recipe deletes `w_terms`, `el_w`, `w_targetclass`, never the cast-output
wire). Adding PN_A as a sink to that existing Wire object changes no object count, which is why `gscript.wire`'s
`before+1..before+1+crossings` test (`tools/gscript.py:1324-1333`) fires.

`gscript.wire(..., branch=True)` returned 40 and raised nothing. `branch=True` asserts NOTHING extra: at
`tools/gscript.py:1325` the guard reads `if not branch and not (lo <= after <= hi)`, so the flag only SKIPS the
count check; the LabVIEW-error raise at `:1320-1321` still applies in both modes.

140 `branch=True` call sites already exist under `tools/` (e.g. `tools/recipes/build_opfstunnelterm_v0.py:401`
and `:415` — the very next two wires in the same recipe — `build_opcaseframes_v0.py:125,129`,
`build_keystone.py:92-97`, `build_d1_routeb_v0.py:1207`).

## §4 `docs/motor-limit-assurance-plan.md` §A.1 item 1 — the ORIGINAL's own read-only node/terminal sweep

`tools/bench/sweep_nodeterms_3state.py` → `tools/bench/sweep_nodeterms_3state.log`, `BGRUN END rc=0 after 975s`,
5/5 gates, output `tools/bench/orig_3state_nodeterms.json`. The ORIGINAL's panel was never opened; md5
`c39f36e0675339673b707c59f0784fee` before AND after.

* **170 diagrams / 622 nodes / 3,304 terminals**, every diagram read without an error (170/170 clean).
* Owners: CaseStructure 76 · FlatSequenceFrame 57 · ForLoop 17 · Sequence 11 · EventStructure 5 · WhileLoop 3 ·
  top 1.
* Class census on the ORIGINAL: SubVI 97 · Property 106 · Wire 1,898 · LoopTunnel 132 ·
  FlatSequenceInnerTunnel 518 · FlatSequenceOuterTunnel 58 · CaseStructure 37 · ForLoop 17 · Sequence 4 ·
  WhileLoop 3 · Global 7 · Local 8 · Invoke 1. `LocalVariable` is not a scripting class here — it raised
  error 1092.
* **ORIGINAL vs V6 row diff (the recorded finding §A.1 item 8 asks for):** 170 vs 170 diagrams, 622 vs 626 nodes,
  3,304 vs 3,328 terminals. Exactly **ONE diagram differs — d43, the frame loop: 71 nodes (ORIGINAL) vs 75 (V6)**,
  same owner `WhileLoop`. Every other diagram matches in node count and owner.

Not done here, and deliberately not started: §A.1's later items (forward reachability from the 3 coerces,
control Data-Entry ranges, the 3 comparator mutation negatives).

## §5 STATUS OPEN items 48/48a, 49 and 50, VERBATIM (relocated 2026-09-18; 49 and 50 are ✅ settled/fixed)

> 48/48a. ✅ **RELEASED + REWRITTEN, 🔴 NEVER RUN** — recipe builds BOTH classes (`OpFsTunnelTerm_v0` FSOT +
>    `OpFsInnerTunnelTerm_v0` FSIT `:137`), T2 face test `:739`, `resolve()` reused `:617`, L1 gates
>    `owner_uid`+`errs` `:657`; release 4/4 (`tools/bench/c20_release_probe.log`), launch gate **ALLOW**. Blocked
>    only by the STOP. Pre-release body (4 findings verbatim · shared-uid measurement · **uids name NO VI — the uid
>    space is SHARED between the two originals; the CACHES are what is keyed to V6**) →
>    `archive/2026-09-18-status-cycle20-open48.md`. 44+45 RETIRED.
> 49. ✅ **`-Dual` REVIEW DISPATCHED AND ARCHIVED, BOTH ARMS ANSWERED** (`archive/peer/2026-09-18-retro-window-semantics-{codex,opus}.md`; `tools/bench/peer_retro_window_semantics.log`, `BGRUN END rc=0 after 621s`). Both arms: membership IS by time window (`tools/retrospective.py:287/289/309`, logs filtered `:364-368`) and `violations.py:172` counts only existing files — but **both REFUTE "only a LABEL"** (N reaches the window via default slug → `exclude_slug`, `:328`→`:223`; picks the C7 plan, `audit_cycle.py:325-327`; fallback `:293-297`) **and REFUTE "can only understate"** (direction indeterminate; v1 saturation + overlapping reviews inflate). ✅ **JUDGEMENT SETTLED, cycle 21:** (i) **cycle 20 gets NO retrospective of its own** — by the measured rule the cycle-21 run's `start` is the newest retrospective archive and `end` = now, so it already covers cycle 20's unreviewed tail *and* cycle 21; a separate `--cycle 20` run would only move `start` forward and SHRINK that window. (ii) **`violations.py`'s 8 is NOT re-derived** — no live decision rests on it (the user closed round 3 `DECISION: no-device`), 7 of the 8 are v1-format hits from cycles 7–13 and v1 is known-saturated (CLAUDE.md:322-323), and re-deriving is device work Pre-decided 1 forbids. FINDING for whoever next argues a threshold: count v2-only first. (iii) the `--dry-run` triple-N discriminator is **not skipped** — the close-of-cycle retrospective prints that same window line for free. Pre-review text → `archive/2026-09-18-status-cycle21-superseded-next.md`.
> 50. ✅ FIXED — `archive/peer/2026-09-18-priorart-fstunnel-reader.md:314-319` now states the four findings were accepted and fixed and the releases are valid; frontmatter date line byte-identical, 4/4 `FIXED:` still validate (`guard_cycle.fixed_citations`, rejected=[]).

## §6 The 2026-09-18 08:53 user-decision block, VERBATIM

> ✅ **USER DECISION 2026-09-18 08:53 — "장치는 더 민들지 말고 계속 진행".** The runner's 04:0x STOP (wrong-ordering
> 8/3 round 3 + OPEN 32) is ANSWERED: `docs/violation-decisions.md` round-3 block `DECISION: no-device`, the gate is
> released, the runner restarts. **STANDING ORDER FOR EVERY CYCLE UNTIL THE USER SAYS OTHERWISE: build NO further
> process device (gate, hook, record store, lock, launcher). A retrospective naming one is a FINDING, not a task.**
> The STOP narrative is verbatim in `archive/2026-09-18-status-cycle20-close.md`.

## §7 The "MEASURED, keep" property-id paragraph, VERBATIM (relocated from STATUS.md 2026-09-18 09:5x, rule 4)

## §8 RELOCATED VERBATIM from STATUS.md's lock comment 2026-09-18 11:0x (rule 4; STATUS was at 110 lines)

```
# CYCLE 22 (MEASURE-ONLY, 10:28): c22_gate_probe rc=0/0s = read-only re-run of c20_release_probe + guard-hook reads; no LabVIEW/motor/serial/camera, stop_records.json untouched (mtime 03:34), nothing launched or released.
# CYCLE 21: 10:17-10:21 peer_fstunnel_wirechecked rc=0/239s (peer dispatch + file reads only, NO LabVIEW opened;
# stop_records.json untouched, nothing launched). 09:49 c21_release_probe rc=0/0s (read-only). 09:22-09:56 rc=0 -
# diag_fstunnel_wire_semantics 77s 8/8 (LabVIEW pid 2468->15280, handles 30,356->31,027) and
# sweep_nodeterms_3state 975s 5/5 (READ-ONLY, the ORIGINAL's panel never opened); 08:59-09:0x TWO runs of
# build_opfstunnelterm_v0.py rc=1/91s + rc=1/92s, IDENTICAL failure. Every scratch created+deleted in-run, nothing
# saved, md5 before AND after each: 3state c39f36e0…, V6 2a78e17c…, donor 5dc45a04…; no motor/serial/camera and
# motor_gate --execute never called.
```

> 🆕 **MEASURED, keep: on `VI Server:FlatSequenceOuterTunnel` the ids `6356001` / `6356000` / `7CC75C00` (`Tunnel.*`,
> `OuterTerminal.Tunnel`) are ALL refused, error 1077** — that class does not expose `Tunnel`'s properties; only the
> FlatSequence-specific ids (`3195B800/1/2`, `1C3A9000-3`) apply. Cycle 20's shipped `guard_cycle.fixed_claim()` and
> the OPEN 42 bgrun measurement → the cycle-20 archive; cycle 19 → `archive/2026-09-18-status-cycle19-flatseq.md`.

## §9 RELOCATED VERBATIM from STATUS.md's lock comment 2026-09-18 11:2x (rule 4; STATUS was at 110 lines)

```
# CYCLE 22 (10:50-10:53): build_opfstunnelterm_v1.py RUN 1 = `BGRUN END rc=1 after 162s`, gates 12/16
# (tools/bench/build_opfstunnelterm_v1_run1.log) - all SIX wire_checked sites PASS (the :392 failure is GONE), B4
# still ExecState 0 after the back half is re-fed ⇒ neither op saved, NO live read ran. 10:50 c22_v1_gate_probe
# rc=0/0s READ-ONLY: both launch gates ALLOW, store mtime unchanged, v0's record 2 untouched (released sha
# 0cc9f6ca…). LabVIEW pid 15280→15868, handles 30,353→30,387; scratch created+deleted in-run (P0 PASS); md5 BEFORE
# AND AFTER identical - 3state c39f36e0…, V6 2a78e17c…, donor 5dc45a04…; no motor/serial/camera, `motor_gate
# --execute` never called. Cycle 21/22-probe lock lines RELOCATED VERBATIM →
# archive/2026-09-18-status-cycle21-wire-semantics.md §8 (§2 = the cycle-21 detail); cycle-20 close →
# archive/2026-09-18-status-cycle20-close.md.
```

## §10 RELOCATED VERBATIM from STATUS.md's "Where things stand" 2026-09-18 11:2x (rule 4; STATUS was at 115 lines). Superseded in part by cycle 22's RUN 1 — the patch IS compiled and run.

```
🔴 **CYCLE 21 — STEP 1 DONE; STEP 2 (`build_opfstunnelterm_v0.py`) FAILED TWICE at `:392`→`gscript.py:1330`;
tunnel op verification level still NONE.** The 09:22 measurement (the cast output already held a RESIDUAL
source-only wire **#384**; after `wire(…, branch=True)` BOTH terminals read #384, count 40→40 ⇒ **the connection
SUCCEEDS, `gscript.wire`'s count test is the false negative**) and §A.1 item 1 (ORIGINAL read-only, 170 diagrams /
622 nodes / 3,304 terminals → `tools/bench/orig_3state_nodeterms.json`; vs-V6 diff = d43 only, 71 vs 75 nodes) are
IN FULL → `archive/2026-09-18-status-cycle21-wire-semantics.md` §1/§3/§4.
🆕 **09:52 PATCHED: the recipe's six wire sites now run through a LOCAL `wire_checked`** (branch computed from the
SOURCE terminal's own `.wire`; both terminals then asserted **equal and non-zero**; `gscript.py` untouched) ⇒ **its
sha changed, so the prior-art LAUNCH GATE now REFUSES every command naming it** (released for `0cc9f6ca3599`, on
disk `5a0df5089373`; `released_slugs` still 4/4, `fixed_claim` (True,True) — `tools/bench/c21_release_probe.log`);
`py -m py_compile` is refused too ⇒ **the patch is UNCOMPILED and unrun**. Ids `6356001`/`6356000`/`7CC75C00` all
1077-refused on the OUTER class → same archive §7; cycle 19 → `archive/2026-09-18-status-cycle19-flatseq.md`.
```

### §9a D1, the identity of the B4 "unwired sinks" — MEASURED 2026-09-18 11:1x

`tools/bench/diag_fstunnel_orphans.py` (new, READ-ONLY: no op built, no VI saved; a pid-stamped scratch copy of
the donor, created and deleted in-run) → `tools/bench/diag_fstunnel_orphans.log`, `BGRUN END rc=0 after 90s`,
gates 8/8, raw `tools/bench/diag_fstunnel_orphans.json`. It reads the three nodes in TWO states: the untouched
donor copy (`fresh`) and the same scratch after `build_one('OUT')`'s edit sequence up to B4 (`at_b4`).

| uid | ClassName | style / label | the sinks the failing run named | created by the recipe? |
|---|---|---|---|---|
| 43 | Function | `Open VI Reference` | T2 `password ("")`, T3 `type specifier VI Refnum (for type only)`, T5 `options`, T7 `application reference (local)` — all wire 0 | NO — in the fresh donor copy |
| 124 | SubVI | `Traverse for GObjects.vi` | T4 EMPTY, T5 `Other Refnum`, T6 `Traverse Generated Code (F)`, T9 EMPTY — all wire 0 | NO — in the fresh donor copy |
| 990 | SubVI | `UID to GObject Reference.vi` | T1/T4/T5/T6/T7/T9 all EMPTY, all wire 0 | NO — in the fresh donor copy |

- **The fresh donor copy is ExecState 1 (LEGAL) with those very sinks at wire 0** (log :20, :63) — 19 nodes, uids
  `[43, 124, 145, 151, 157, 163, 167, 241, 307, 310, 482, 990, 1044, 1186, 1221, 1319, 1326, 1329, 1554]`.
  The terminal lists are IDENTICAL in `fresh` and `at_b4` (log :23-62 vs :107-146); only 990's Nodes[] index moves
  (9 → 7) because two nodes were deleted. uid is stable, the Nodes[] index is not.
- **None of the three is a Property or an Invoke node** — `report_all` returns them only as SubVI/Function
  (log :24, :35, :50), so the "which property items are selected / is one blank" question does not apply. No
  reader for a Property Node's selected ITEMS exists in the fleet either (`docs/toolkit-capabilities.md:185` is
  the id only); it was not needed.
- The recipe's own objects are pn_a 145, pn_b 148, pn_a_uid 151, pn_b_uid 154, pn_b_cw 168, pn_b_cwu 169 and the
  control `reference 4` (log :101; recipe lines :451/:481/:484/:487/:492/:495/:455). The scratch reproduced the
  failure (ExecState 0, log :102). Handles 30,318 → 30,979; md5 before = after on all three files.

