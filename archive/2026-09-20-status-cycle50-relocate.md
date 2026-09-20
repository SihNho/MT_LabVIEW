---
type: archive
status: superseded
date: 2026-09-20
tags: [status-relocation, cycle50]
---

# 2026-09-20 — STATUS relocation, cycle 50

Relocated VERBATIM (CLAUDE.md rule 4 — copy, never rewrite) out of `STATUS.md` by the cycle-50 material
session. Nothing here was edited; the cycle-50 judgement session writes the replacement NEXT.

## §1 — cycle 49's NEXT, verbatim

## NEXT
🔧 **The runner lands its own retrospectives** (`cycle_runner.py land_retrospective()`, 2026-09-19 23:43): a `--cycle N` START in `retro.log` with no END is re-run by the runner process, which outlives the session, and logged `RETRO-LANDED` in `cycle_runner.log`. First firing `retro.log:389` → `:439`, `cycle_runner.log:56`. Repair of an existing device, not a new one.
🎉 **S1 IS DELIVERED (cycle 48) — `claudeDev\D1_s1_copy.vi` EXISTS**, md5 `3e3d23cefd3a334001aa9d6156bf1aee`,
474,202 B, 20 pass / 0 fail. The staged D1 chain has its first artefact; full record in the `owner_c48s1cd` lock key.
🔴 **FIRST ACT — ROUND-3 PRIOR-ART REVIEW ON THE EDITED RECIPE, THEN LAUNCH `--phases A` ONLY.** `tools/recipes/stage_d1_s2.py`
is written and carries all five round-2 fixes + Pre-decided 33's A5: **1956 lines, sha256 `789a5c965ded…743eda`**,
contract **A = 17 pass / 0 fail**. `guard_cycle.premature_build()` PASSES; only `tools/stop_record.py` blocks, and it
wants a review that post-dates these bytes. 🔴 **RELEASE IT BY CITING A DOCUMENT CHANGED AFTER THE REVIEW, NEVER BY
EDITING THE RECIPE** — an edit re-arms the gate for another paid round, which is what cost cycle 49 its launch
($9.54 over two rounds). `REFUTED:` needs no edit at all; a `FIXED:` may cite `docs/cycle27-plan.md`.
🔴 **DO NOT LAUNCH PHASES C/D — S2 CANNOT END LEGAL, on two independent MEASURED grounds.** Phase A's DATA artefact
`tools/bench/s2a_legality.json` is the next deliverable, not `D1_s2_loops.vi`: (1) **no built op places a constant
TRUE on a new While loop's conditional terminal**, re-derived over the COMPLETE 14-op writer table
(`OpConstValueN_v1`/`OpWireSource_v5` are READERS · `OpExitLoop_v0` makes indexed output tunnels · `OpBuildCase_v0`'s
Selector cannot be written · `OpForLoop_v0`/`OpWhileLoop_v0` leave it unwired · `OpExitWhile_v0` sources a PANEL
CONTROL, refused by Pre-decided 32(a)); (2) **`move_in` SEVERS wires** (`a5_lands_unwired=True`,
`docs/d1-route-b-plan.md:57-58`/`:67`), so the three land unwired and probably bare a Required input — which no built
op can read (33(c)). Net contract, when a shape is finally authorised: **SubVI 97 → 97 · WhileLoop 3 → 6 · Diagram
170 → 173**.
🔴 **SECOND ACT — THE REAL BLOCKER IS A DESIGN GAP, NOT TOOLING, AND IT NEEDS NO LabVIEW.**
`tools/recipes/build_d1_routeb_v7.py:131-135` + `docs/d1-route-b-plan.md:153`: the three sentinel `Equal?`s depend on
**inter-loop queue element types that were never designed**, so no new loop can be given a real stop condition and no
scaffold substitutes for one. Design those element types as a plan section, prior-art-reviewed once, before any
further S2 build. Zero LabVIEW, zero instrument, zero gate.
🟡 **Two one-liners carried from the cycle-48 retrospective (disposed):** set `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`
once in `tools/cycle_runner.py`'s spawn — a repair to an existing tool, not a device, and it closes the
background-kill class that stands at 17 cumulative occurrences; and give `tools/hash_probe.py` its one line in the plan.
✅ **Cycle 49's decisions are `docs/cycle27-plan.md` Pre-decided 31/32/33** — `#5058` is the **CPU** kernel, not the
GPU kernel (31(a), fatal gate C2k; the kernel swap is its own later stage) · branch 1 stands on node IDENTITY, not
wire preservation (33(b)) · 32(f)'s pass-through sentence is WRONG (33(a)). Both prior-art reviews and the cycle-48
retrospective are DISPOSED, and `docs/violation-decisions.md` carries the dated `DECISION: no-device` that
`guard_cycle` demanded before any launch.
🔴 **No new op, no new device, for any of it** (Pre-decided 2; user 2026-09-18 08:53).
🟡 **CHECK THE REVIEW GATES BEFORE THE BUILD, NOT AFTER THE REFUSAL.** `guard_peer` blocks on the newest
`*retrospective*.md` **and** the newest `*priorart*.md` lacking a real `## What was done with it` (≥80 chars once the
`(claude fills in)` placeholder is stripped — `guard_peer.py:237-242`).
🔴 **THE RETROSPECTIVE IS THE LAST THING YOU RUN, in the background: `py tools/bgrun.py --max-min 20 --log
tools/bench/retro.log -- py tools/retrospective.py --cycle <N>` with `run_in_background: true`, then write NEXT and
exit** (the runner lands it). `guard_bash.py:226-227` sets the retro-done mark on ANY `retrospective.py` in command
position — even a REFUSED one — after which `guard_session` refuses every dispatch (OPEN 54(a)). **Never run one
early, and never pay a previous cycle's retro debt up front.**
🔵 **Retired NEXT bullets RELOCATED VERBATIM (rule 4)**: cycle 49's → `archive/2026-09-20-status-cycle49-relocate.md`
§2/§3 (incl. the gate mechanism: a `FIXED:` line cannot move a stamped `released.sha256`; only a NEW prior-art record
supersedes) · cycle 48's → `…-cycle48-next-retired.md` §1–§5 · cycle 43–46's → `…-cycle46-relocate.md` §2–§5 and
`…-cycle45-relocate.md` §1/§2/§3/§4/§8/§9 — all unchanged and still current.
⚙️ Operating fact, keep: the ORIGINAL is readable via `py tools/bgrun.py --material … -- python -u <script>`;
`md5sum`, `lv_gui.ps1 -Action md5` and inline `py -c` are all refused.
- 🟢 **S0 IS CLOSED (cycle 45) — unrepaired traverse ops ACCEPTED on measurement** (three arms: traverse-only −0.1 MB
  · traverse+mutate +34.6 · mutate-only +34.5 ⇒ the drift is VI growth, G-A/G-B/G-C met on traverse-attributable
  drift; Pre-decided 25(iv)+27+28 BRANCH-A). Recorded in `docs/REFERENCES.md` §4a-bis + `docs/toolkit-capabilities.md`.
  ⚠️ `error 2`'s cause stays OPEN (21(b) amended); no repair built, every old op byte-identical.
- ⚠️ **BINDING from the 4th outcome review** (`archive/peer/2026-09-19-outcome-review-20260919.md:153`, disposed
  `:171` — NOT a stop-and-re-plan, because the user's 17:4x staged-build order already was one): **every cycle must
  end with saved files and md5s in a log.** Cycle 48 met it with **`D1_s1_copy.vi`** (md5 `3e3d23ce…`); cycle 46 with
  `D1_s1arm_savetest.vi` + `s1_saveroute.json` + `s1_subvi_paths.json` + `s1_savedcopy_census.json`. **Three
  USER-ONLY decisions remain open and are NOT blockers**: OPEN 53's physical-zero question before any D1
  motor-moving run; schedule-or-descope requirement 1; place-or-descope the item at its `:126`.
💬 **FOR THE USER — a cost fact, not a fault** (cycle-47 retrospective finding 6(b), disposed): judgement-session
  spend dominates peer/review spend about **8 : 1** ($191.50 vs $23.94 in that window), and `audit_cycle`'s C4 bucket
  labels most of it "REVIEWS", which understates it. Only you can act on it; nothing is being changed on its account.
🟢 **CYCLE 46's MEASUREMENTS — full text in `docs/cycle27-plan.md` Pre-decided 29(a)–(j); do not restate them here.**
The two that bind every stage: `gscript.save()` reaches `SaveInstrument` ONLY at `ExecState != 0` (a stage artefact
saves ONLY under preload, `allow_broken=True` banned), and 🔴 `shutil.copy2(ORIGINAL, claudeDev\…)` SILENTLY RE-BINDS
22 SubVI calls into `claudeDev\background VIs_COPY\` and loses 8, while the COM-SAVED copy matches the ORIGINAL on
all 98 rows (`tools/bench/s1_subvi_paths.log`, 15/0) ⇒ **every stage gate compares to the ORIGINAL, never to a copy**
(29(g)). Repairs applied: `SAVE_ALLOWLIST = set()`, the stop-record command-position exemption.
🆕 **OPEN from cycle 46, all live:** (a) `claudeDev\background VIs_COPY\` = 94 `.vi`, an unmanaged duplicate hierarchy
on the build path (17 shared names md5-identical today, so nothing has computed differently YET); (b) `logclass.py`
counts `selftest_*.log` as a build (29(j)); (c) `gui_save`'s Ctrl+S bypasses `lv_gui.ps1`. **FLAGGED FOR THE USER
(rule 2c):** 29 narrows 16(b) to permit preload-then-save for `claudeDev` stage artefacts, and S0's ops were accepted
on a completed G-C (25(iv)/28) — judgement's reading of your own rules; only you may overturn them.
**Unchanged from cycle 34, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT
flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none.
