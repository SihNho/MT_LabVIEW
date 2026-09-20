---
type: archive
status: history
date: 2026-09-16
tags: [status-narrative, cycle-11, gate, a1, camera]
---

# Session narrative, 2026-09-16 pm — opening the gate, A1's first run, and the delete regression

Moved out of STATUS.md under CLAUDE.md rule 4 (STATUS reached 220 lines against a ~100-line threshold). The live
state stays in STATUS; everything below is the reasoning that produced it, kept verbatim.

2. ✅ **The PRIOR-ART layer of the gate is OPEN (2026-09-16 14:2x), and rev6 was NOT dispatched.** All 13 of rev5's
   findings were opened and **accepted — none was argued with**; six were already discharged by that afternoon's
   edits, the other seven were fixed here (plan rows 1.1 / 1.2 / 1.3, **new 1.9 stop-and-shutdown**, **new Phase A9
   diagram 87 / uid 9775** and **A10 bead-free initialisation**, two new 2A rows, plus banners in
   `restructure-plan-4.6.md:42` and `rotor-scheduler-design.md:74-75`). The `REFUTED:` lines and a per-finding table
   are at the end of `archive/peer/2026-09-16-priorart-master-plan-rev5.md`; they say *"the cited text is no longer
   on disk"*, not *"the reviewer was wrong"*. One correction worth carrying: 1.3's earlier fix had released the
   2026-09-12 peer correction by calling locals *"the user's decision"* — `rotor-scheduler-design.md:72-75` was
   opened and **the user's sentence is only the parallel-loop one**; the transport is an open decision again.
   ⚠️ **Gate hole recorded, not fixed:** `guard_cycle.py` advises *"if the review is right, change the plan"* but
   accepts only `REFUTED:`; a `FIXED:` release form is the obvious repair and is the user's call.
2b. 🔴 **THE BUILD IS STILL BLOCKED, and now by the VIOLATION counter — this is the session's headline.** The
   cycle-10 retrospective ran at 14:28 (`archive/peer/2026-09-16-retrospective-cycle10.md`, accepted in full,
   disposition written) and returned **seven VIOLATION slugs**. Six of them are now at **4 occurrences across
   cycles 7·8·9·10 — the same six faults, four cycles running**. Its headline number: the cycle bought **six
   reviews, 48 min 40 s and $28.5530** of a plan that changed under every reviewer and **never launched
   `OpOwnerChain_v0`, the reader it was declared for**.
   All six are re-answered on cycle 10's own evidence in **`docs/violation-decisions.md` → "Round 2"** (2 devices,
   4 reasoned no-devices, plus a checkable commitment: **the next recipe this project runs is A1**).
   ✅ **The date-comparison bug is FIXED, on the user's instruction** (*"타임스탬프 비교로 고친다"*, 2026-09-16).
   `violations.py` compared decision dates as *date strings*, so `"2026-09-16" > "2026-09-16"` was false and a
   same-day answer could never discharge a slug — ordering, which was the stated intent, is not representable in a
   bare date. A decision heading may now carry `HH:MM` and is compared as a timestamp; a retrospective's stamp
   comes from its **filename date only, never its mtime** (annotating a review touches the file, and an mtime
   stamp would make diligent annotation re-block the build — the trap `guard_cycle.stamp()` already documents).
   The block was reported and left standing until the user decided: regrading a gate while it blocks your own
   build is the `rule-evaded` slug itself.
   ✅ **Both round-2 devices are BUILT and tested, not promised.** (1) `guard_peer.py` now refuses a new
   `priorart`/`retrospective` dispatch while the newest archived review of that kind is undisposed — verified to
   block on an undisposed file and to pass otherwise. (2) `audit_cycle.py` gained **C4/C5**: review wall-clock and
   cost, separate from builds. First run: **builds 6 min 55 s, reviews 76 min 7 s — reviews are 91 % of the
   window**, the number the audit could not see before. Cost still prints UNKNOWN rather than 0, because our peer
   logs carry no cost line; making them do so is the obvious follow-up.
3. 🔴 **A1 RAN — first time ever — and FAILED 3 of 5 build gates** (`tools/bench/build_opownerchain_v0.log`,
   15:13, 180 s). It is no longer "written, never launched"; the `"PropertyNode"`/1092 fix held and the copy
   started at ExecState 1 (B1 ✅), ended at ExecState 1 and **was saved** (B5 ✅, claudeDev). What failed:

   | gate | observed |
   |---|---|
   | **B2** rewire R1 lands | node 241 `reference` = wire **1208**, expected the pre-measured **1081** |
   | **B3** rewire R2 lands | node 241 `Owner` = wire **0**; consumers `{163: 751, 1221: 751, 482: 1444}` |
   | **B4** wire-only nodes gone | six deletes reported **success** — yet counts are **identical before and after** (`Property 12→12, SubVI 2→2, IndexArray 2→2`) and the walk still sees the nodes |

   ⚠️ **B4 is the serious one and it is not a LabVIEW question**: an operation reported success while nothing
   moved — the same family as the `unreported-fact` device. `#1044` also failed as `"SubVI"`; it is a
   *To More Specific Class* primitive, so the class string is simply wrong.
   ✅ **The read landed and it is decisive — `tools/bench/diag_ownerchain_state.log`, and it changes the question.**
   The SAVED `OpOwnerChain_v0.vi` is **the donor's topology, unchanged**: all six "deleted" nodes are still
   enumerated, `241.reference = 318`, `241.Owner = 0`, and `163 / 1221 / 482` all still read **751** — every one of
   them the donor's original value, not the 1208 / 1444 the build observed mid-run. Counts 12/2/2/19 match the
   donor. The file WAS written (md5 differs, mtime 15:16) but at the **same 18 163 bytes**, i.e. saved with no
   structural change.

   **So the diagnosis is not "which rewire was wrong" — it is that NOTHING the build did reached the file.** Two
   separable defects, and neither is a LabVIEW-semantics question:
   - **Deletes never took effect even in memory** (count stayed 12 immediately after each "deleted #…"), yet
     `delete_object(..., verify=False)` reported success. Verification was explicitly switched off at the call site.
   - **Connects DID take effect in memory** (B2 saw 1208, B3 saw 1444) **and were gone by save time.** So a change
     applied through one VI reference did not survive to the save.

   🔴 **ROOT CAUSE FOUND, and it is a TOOL REGRESSION, not an A1 design problem**
   (`tools/bench/diag_save_persists.log`, 29 s, decisive). Cleanest possible test — copy the donor, delete **one**
   object with `verify=True`:

   ```
   RuntimeError: delete_object(Property[3]): expected 1 object gone, got 0
   ```

   **`gscript.delete_object` / `OpDelete_v0` no longer deletes anything.** The op's Run returns with no error and
   the object is still there — a **silent no-op**. Saving was never the question (that hypothesis died here), and
   A1's six "deleted #…" lines were produced only because the recipe passed **`verify=False`**, switching off the
   one check that would have caught it. That is textbook `unreported-fact`, the slug this same day got a device for.
   ⚠️ **Assume every `verify=False` delete since this regression began did nothing.** `delete_object` was used to
   build ~168 ops and worked then, so this is a regression with an unknown start date — `build_keystone.log`,
   `build_timing.log`, `donor_clfn_probe2.log`, `fixture_probe.log` are the other logs that call it.

   **Peer review dispatched** (`tools/bench/peer_delete_noop.log`, codex): under what conditions does Generic.Delete
   return without error and delete nothing? Hypotheses: the reference is not opened editable / wrong method for
   these classes / the diagram is effectively read-only.

   The B2/B3 review **landed and is disposed** (`archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md`).
   Its finding, **verified in our own files**: `gscript.py:2084` and `vi-scripting.md:603,:623` all say
   *"Connect Wire on an already-wired SINK re-routes and breaks the VI — only wire unwired sinks"*, and the recipe
   wired **four** already-wired sinks. Both my hypotheses were refuted; a branch should PRESERVE the wire uid, so
   1208 was an uncontrolled replacement, and 1444 is most likely a source-less fragment.

   **The A1 fix, when the delete path works again:** delete the wire-only front section FIRST (that removes wires
   318 and 751 and leaves all four sinks unwired), then connect; and `#1044` is a *To More Specific Class*
   primitive, enumerated only under `Node`, never `SubVI`. A1 has used **1 of its 2 failures** — do not spend the
   second until `delete_object` is fixed and proven on a scratch VI.

**Do not** start hardware work before Phase A — the user's standing instruction: *"지도 작성이 우선되는게 맞음.
내 지시였음."*


## The camera / uid 9775 item, as it stood in STATUS

2c. 🟢 **uid 9775 on startup diagram 87 READS the camera geometry — it does not write it. CLOSED 2026-09-16 14:2x,
   MEASURED** (`tools/bench/diag_9775_direction.log`, main VI md5 unchanged, 37 s). Both `Height` (wire 32937) and
   `Width` (32938) have uid 9775 itself as their **source**, so both terminals are OUTPUTS; the single sink on each
   is a `Diagram`-owned terminal (uid 13236), i.e. a front-panel indicator. **So the copy does not set the frame
   size and the plan's 1280×1024 assumption is safe** — the panel's 640×512 is a stale display of a previous
   session's ROI. Prior-art rev4 A5 / rev5 A9, open across two reviews on a position-proximity sweep that is
   **invalid on a Clean-Up'd diagram**; an op we already had (`OpWireSource_v5`) answered it in 37 s.
   **And the other half of the user's memory is confirmed too** (*"카메라 프레임 읽어오기 → 이후 IMAQ 화면 사이즈
   셋팅"*): **diagram 97 writes a size, and it is the FRONT-PANEL DISPLAY's, not the camera's** — panel
   `Height`/`Width` read back (30445/30471) → bundle (30512) → **÷ 2** (constant uid 27664) → `Image Area Size`
   (30118) and `Draw Area Size` (30422). Found offline in dumps already on disk. That is why no ROI test ever saw
   it, and it is **not** an explanation for the still-unexplained fresh-session 640×512 ROI reading.
   ⚠️ **Do not widen it to "the VI does not set frame size"** — the codex review
   (`archive/peer/2026-09-16-uid9775-read-not-write-codex.md`, annotated) confirms the narrow claim and refuses the
   wide one. Residual test, cheap: `Property Items[] → Is Write` across the 106 Property nodes. (The gemini
   dispatch timed out at 180 s and told us nothing — this question needs `-TimeoutSec 480`.)

## The delete investigation in full, as it stood in STATUS (moved 2026-09-16 15:4x)

3. 🔴 **A1 RAN for the first time and FAILED 3/5 gates — root cause is in the DELETE TOOL, not in A1's design.**
   On a clean donor copy, deleting ONE object with `verify=True` gives `expected 1 object gone, got 0`
   (`tools/bench/diag_save_persists.log`). A1 only reported six successful deletes because it passed
   `verify=False`; the saved VI is the donor topology, unchanged (`diag_ownerchain_state.log`).
   **MEASURED, in two runs, after the peer review refused my first framing** (review archived + annotated):
   - `OpDelete_v0` exposes `error out`, and on a valid failing delete it reads **clean** (`diag_delete_error.log`).
   - But the **control** settles what that means (`diag_delete_error_control.log`): given inputs that *cannot*
     succeed (index 999999; class `NoSuchClassXYZ`), `error out` **still** reads `(False, 0, '')`. **It is a DEAD
     indicator** — so the clean read proves nothing, and the op must be **rebuilt with the Invoke Node's error
     wired out** before any claim about why delete fails. That is now a measured reason to rebuild, not a guess.
   - The control also exposed a **second defect**: LabVIEW's real signal for a refused delete is a **modal
     dialog**, and `delete_object` contained `if "modal dialog" not in str(e): raise` — it caught exactly that
     signal and carried on. ✅ **Fixed in `tools/gscript.py`**: swallow removed, `error out` now read like every
     neighbouring wrapper, docstring states that `verify=False` cannot tell you whether anything was deleted.
     ⚠️ `net_map`'s purge calls it `verify=False` inside `except Exception: pass`, so **no caller anywhere had
     positive evidence that delete works** — "purged N junk Invokes" counts attempts, not deletions.
   ⚠️ **Assume every `verify=False` delete since the regression did nothing** —
   also in `build_keystone.log`, `build_timing.log`, `donor_clfn_probe2.log`, `fixture_probe.log`.
   Peer review out: `tools/bench/peer_delete_noop.log`. **A1 has 1 of its 2 failures left — do not spend it until**
   **`delete_object` is fixed and proven on a scratch VI.** The A1 fix itself is settled by the archived B2/B3
   review: **deletes first, then connects, only into UNWIRED sinks** (`gscript.py:2084` and `vi-scripting.md:603`
   both already said so), and `#1044` is class `Node`, not `SubVI`.
   Full narrative: `archive/2026-09-16-status-gate-a1-delete-regression.md`.
