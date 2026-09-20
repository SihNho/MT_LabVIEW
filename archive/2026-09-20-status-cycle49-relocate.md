---
type: archive
status: archived
date: 2026-09-20
tags: [status, relocation, cycle49]
supersedes: []
---

# STATUS relocation — cycle 49 (rule 4: nothing is deleted, only moved)

Relocated VERBATIM by the cycle-49 material session, because STATUS.md had reached 113 lines (threshold ~110).
Nothing here is rewritten; STATUS keeps one line and a pointer for each item.

## §1 — the `owner_c48s1cd` lock key (cycle 48's S1 delivery record), VERBATIM

```yaml
  owner_c48s1cd: # ✅ **RELEASED — S1 PHASES C+D RAN AND PASSED: 20 pass / 0 fail, `BGRUN END rc=0 after 679s`** (`tools/bench/stage_d1_s1_cd.log:115` START 2026-09-20 00:08:09 → `:346`). **THE DELIVERABLE EXISTS: `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi`, md5 `3e3d23cefd3a334001aa9d6156bf1aee`, 474202 B** (`:306`; md5 re-confirmed independently by `certutil`). ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` **BEFORE (`:119`) and AFTER (`:303`)**, gates MD5-C `:147` / MD5-D `:302` also unchanged. Gate **D5 FATAL PASS** `:299`: S1 97 rows vs ORIGINAL 98 (`:294`/`:295`), `missing=0 extra=0 changed=0` (`:296`), 0 rows into `background VIs_COPY` (`:297`), 0 empty name-or-path (`:298`), the one removed key `(diagram 639, node 22700)` = IMAQ Write TIFF File 2 (`:293`). ExecState of the artefact: **COLD = 1** (`:153`, recorded not gated, Pre-decided 14a) · **PRELOADED = 1** (`:155`, gated, PASS `:157`). Refs `opened 9 / closed 9 / live 0` (`:307`); handles 34303. No motor, no ASI, no camera. ⚠️ The log is APPEND-mode: lines 1–114 are cycle 47's killed 23:51:58 attempt (preserved separately as `tools/bench/stage_d1_s1_cd_prev2351.log`); this run is lines 115–346.
```

## §2 — the cycle-49 launch-gate refusal, VERBATIM (kept here so STATUS needs only a pointer)

The S2 recipe was edited to implement `docs/cycle27-plan.md` Pre-decided 32, and the prior-art LAUNCH GATE then
refused the run (`tools/stop_record.py`, hook output, 2026-09-20 01:3x):

```
BLOCKED by tools/stop_record.py (the prior-art LAUNCH GATE, docs/cycle18-plan.md Pre-decided 2): this recipe was RELEASED for different bytes than the ones on disk now.
  recipe      : tools/recipes/stage_d1_s2.py
  review      : archive/peer/2026-09-20-priorart-d1-s2-stage.md
  verdict     : settled-already, refuted-already, contradicted, unread-evidence, already-built, already-failed, helper-exists, already-measured
  reviewed sha: 3e9025596187
  released for sha 3be69ba52b89, on disk now 71f12e121f95 - a changed hash means UNREVIEWED, not released. Re-saving a
  recipe does not clear its record (docs/cycle18-plan.md Pre-decided 2). Get the edited recipe reviewed,
  or cite the edit with a fresh FIXED: line in a review that post-dates it.
```

Measured about the mechanism, from the code and the store (not inferred):

* `tools/bench/stop_records.json` holds 21 records; the one for this recipe was created 2026-09-19T16:02:07Z and
  **stamped `released.sha256 = 3be69ba52b89…` at 2026-09-19T16:24:11Z**, i.e. at whatever bytes were on disk when
  the release first passed — already different from the `reviewed_sha256 3e90255961…`.
* `tools/stop_record.py:354-384`: once `released` is stamped, ANY later byte change refuses. Adding another
  `FIXED:` line to the SAME review does **not** move that stamp (`_released` only validates slugs, `:273-303`).
* The ONE mechanism that clears it is **supersession** (`:361-377`): a LATER record for the same recipe path
  makes the old one skip. A later record is written only by a NEW prior-art review
  (`tools/prior_art_review.py --recipe …`), and that new record then refuses in its own right until its own
  findings carry valid `FIXED:`/`REFUTED:` lines.

## §3 — the two cycle-49 NEXT bullets about the S2 recipe and the launch gate, VERBATIM

Relocated by the cycle-49 material pass 2 (rule 4; STATUS was at 111 lines). Both are superseded in their
NUMBERS by that pass — the recipe is now 1956 lines, sha256 `789a5c965ded3942d45f149868bd40571e6519941c33d58b8f1c291674743eda`,
and its A3 table covers 14 scan-named ops — but the MECHANISM paragraph below is still true and is why the next
cycle runs round 3 rather than appending another `FIXED:` line.

```
🔴 **THE S2 RECIPE IS WRITTEN AND IMPLEMENTS 32; THE RUN IS BLOCKED BY THE PRIOR-ART LAUNCH GATE** (cycle 49,
`archive/2026-09-20-status-cycle49-relocate.md` §2 for the verbatim refusal). `tools/recipes/stage_d1_s2.py`
(sha256 `71f12e121f95`) now: scaffolds AFTER `move_in` (32(b)); REFUSES `OpExitWhile_v0` and no longer names any
original front-panel control (32(a)); A3 is a measured table over 10 candidate ops with 32(d)'s selection rule
applied mechanically (32(c)/(d)); phase D reads every new tunnel's IndexMode with `OpTunnels_v0` (32(f)). Net
contract unchanged: **SubVI 97 → 97 · WhileLoop 3 → 6 · Diagram 170 → 173**.
⚠️ **MEASURED about the gate, so the next session does not re-derive it**: the record's `released.sha256` is
stamped at first release and **a new `FIXED:` line in the SAME review cannot move it** (`tools/stop_record.py:354-384`,
`:273-303`). The only mechanism that clears it is **supersession** — a LATER record for the same recipe path, which
only `tools/prior_art_review.py --recipe tools/recipes/stage_d1_s2.py` writes, and which then refuses in its own
right until its own findings are disposed. **Which of those to spend the next cycle on is judgement's call.**
```
