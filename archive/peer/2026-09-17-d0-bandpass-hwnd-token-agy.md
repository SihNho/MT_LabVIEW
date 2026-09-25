---
type: peer-review
status: historical
date: 2026-09-17
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# d0-bandpass-hwnd-token-agy

- **agent:** gemini
- **model:** (agy default, not readable) (agy built-in default)
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (229s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

A PREDICTION OF OURS FAILED, and the new reading INVERTS the previous diagnosis. Attack the new reading before it drives a rebuild. You have no file access, so every fact you need is inlined below.

SETUP. A LabVIEW 2026 top-level VI is run over ActiveX (Run(False)) on Windows 10. During its calibration stage it opens a subVI front panel titled exactly "choose bandpass v2.vi", carrying a Boolean button labelled "Yes" under the caption "Selected?". An external Python/PowerShell harness clicks that Yes with SetCursorPos + mouse_event LEFTDOWN/LEFTUP (no intervening motion), after SetForegroundWindow.

HISTORY. Twice the harness concluded the click was NOT DELIVERED, because its progress test - "is a visible window whose title contains 'choose bandpass' still present?" - kept returning true minutes after the click. A previous reviewer refuted our "the subVI's Event structure was not ready yet" explanation (static front-panel events are registered at run-mode entry and QUEUED; a locked panel defers rather than discards) and prescribed a probe recording the Windows input state around exactly one click.

WHAT THE PROBE MEASURED (one click, no retry, panel up >= 12 s beforehand):
  SetForegroundWindow returned TRUE
  GetForegroundWindow after activation == 19728546 == the bandpass panel HWND
  GetForegroundWindow at button-down == the same HWND
  WindowFromPoint(176,353) and its GA_ROOT == the same HWND
  GUITHREADINFO before the click: hwndCapture=0, hwndMenuOwner=0, flags=0
  press duration 345 ms
  AFTER the click: GetForegroundWindow == 19794082, whose title is ALSO exactly "choose bandpass v2.vi"
  500 ms after the click: IsWindow(19728546) == FALSE (the clicked window no longer exists)
A screenshot 30 s later shows the successor window still displaying "Bead # 1", but now POPULATED - the "Cal image" indicator has two red cursor lines, "Cal image with chosen filter" has data, and two XY graphs (delta phi vs z, phi vs z) are present - whereas the FIRST panel had been blank in the earlier failed run.

MY NEW READING, WHICH I WANT YOU TO REFUTE: the click was always delivered and effective. Neither hypothesis (a foreground/z-order race eating the click, or a delivered-but-deferred click behind a locked panel) is true. The defect was our PROGRESS PREDICATE: a title-based window test cannot distinguish "this panel closed" from "a successor panel with the same title opened". The fix is to make the HWND the token - a click counts only when the clicked HWND is destroyed - and to stop assuming exactly one Yes per bead, driving the loop from the machine instead (keep answering distinct HWNDs until the "Save cal cluster file" dialog appears, capped).

ALREADY RULED OUT (do not spend your answer on these): wrong coordinate or wrong window (WindowFromPoint at the real press point returned the target HWND itself); LabVIEW blocked behind a modal (a second COM apartment answered ExecState/GetControlValue throughout); using VI-Server SetControlValue instead of a click (it raises no Value Change event).

GIVE ME:
 1. The strongest reason this new reading is WRONG or incomplete. Specifically for LabVIEW: can a subVI front panel window be DESTROYED and RECREATED as a NEW HWND for reasons OTHER than the diagram advancing past the control read - for example a reentrant subVI's per-call panel, "Show front panel when called / Close afterwards if originally closed", a panel re-open inside a loop for the SAME iteration, or a redraw that recreates the window - so that HWND death does NOT prove the Yes Boolean was read?
 2. An alternative explanation of the SAME evidence, including why the successor panel still reads "Bead # 1" while being populated with filtered data, and why the first panel was blank.
 3. The observation that would FALSIFY my new reading.
 4. Whether "keep clicking distinct HWNDs until the Save dialog appears, capped at 12" can double-accept or skip a bead, and what per-iteration evidence an EXTERNAL harness should gate each click on, given it can read: the window list, each window's HWND and rect, screenshots, and VI-Server GetControlValue on the MAIN VI's front-panel indicators (e.g. a "Count" control and a "current image number" indicator).
 5. The cheapest discriminating test, runnable from Python/PowerShell without editing the VI.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is **refuted**. Your new reading correctly identifies that HWND death tracks individual window lifecycles, but draws an invalid conclusion: **HWND death does not equal bead calibration acceptance, and title persistence was not a lost-click phantom—it was a second, distinct dialog stage for the same bead.**

---

### 1. The Strongest Reason the Claim is WRONG

**Equating HWND destruction to calibration progress mistakes a subVI execution boundary for an application state transition.** 

In LabVIEW, when a subVI is configured with [Show front panel when called / Close afterwards if originally closed](https://www.ni.com/docs/en-US/bundle/labview/page/subvi-node-setup-dialog-box.html), the LabVIEW runtime invokes the Win32 `CreateWindowEx` upon subVI call entry and `DestroyWindow` upon subVI exit. 

HWND death proves only that **one execution of `choose bandpass v2.vi` completed**. It does **not** prove that Bead #1 was accepted, nor that the diagram advanced to the next bead. Specifically:
* **SubVIs called in multi-stage workflows or retry loops destroy and recreate HWNDs for the same iteration:** If the top-level VI calls `choose bandpass v2.vi` twice per bead—once for ROI/bandpass parameter input and once for post-calculation calibration verification—each call allocates a fresh Win32 HWND. The destruction of the first HWND marks only the completion of parameter submission, not bead acceptance.
* **Programmatic panel toggling:** A VI calling `Front Panel: Close` followed by `Front Panel: Open` via VI Server invoke nodes destroys its Win32 window (`IsWindow` becomes `FALSE`) and creates a new HWND mid-execution without reading the Boolean control.
* **Exit on error or timeout:** If the subVI exits via an error pass-through, abort, or an Event Structure timeout, the window closes (destroying the HWND) without the "Yes" terminal ever latching `TRUE`.

Treating HWND death as a generic acceptance token and blindly clicking successive HWNDs fundamentally misinterprets the underlying state machine.

---

### 2. Alternative Explanation of the Same Evidence

**`choose bandpass v2.vi` is a Two-Stage Interactive Calibration Handshake per bead (Parameter Input $\to$ Quality Verification).**

1. **Stage 1 (HWND 19728546 – Parameter Setup):** 
   The top-level VI calls `choose bandpass v2.vi` for Bead #1 with raw/default inputs. The graphs (`delta phi vs z`, `phi vs z`) and "Cal image with chosen filter" are **blank** because the CPU-intensive radial profile and phase calibration calculations across the Z-stack have not been run yet. The caption `"Selected?"` with `"Yes"` prompts: *"Are these bandpass parameters chosen?"*
2. **The First Click:**
   Your probe delivered the click to HWND 19728546. The subVI read the control and exited. Because "Close afterwards if originally closed" was active, LabVIEW destroyed HWND 19728546 (`IsWindow == FALSE`).
3. **Computation & Stage 2 (HWND 19794082 – Quality Control):**
   The top-level diagram took the parameters from Stage 1, ran the bandpass filter and phase calculations for Bead #1 across the Z-stack, and called `choose bandpass v2.vi` a **second time** for Bead #1, passing in the calculated cursor lines, filtered image, and phase curves. LabVIEW allocated HWND 19794082. The successor panel still read **"Bead # 1"** because Bead #1 had not yet been accepted—it was now waiting for the operator to inspect the curves and confirm quality.
4. **Why the earlier run appeared hung:**
   The earlier harness clicked once, expected the window title to vanish permanently, saw `choose bandpass v2.vi` still present minutes later, and concluded the click failed. In reality, the click **succeeded**, Stage 1 closed, and Stage 2 opened and sat indefinitely waiting for its **second** click.

---

### 3. The Observation That Would FALSIFY the Claim

Any of the following observations will decisively falsify the claim that HWND 1 accepted Bead #1:

1. **Main VI indicator does not increment after HWND 1:** 
   Querying the main VI’s bead index (e.g., `Count`, `Current Bead`, or `current image number`) via VI Server [`GetControlValue`](https://www.ni.com/docs/en-US/bundle/labview/page/vi-server-reference.html) before the click and immediately after HWND 19728546 dies. If the indicator remains `1` while HWND 19794082 is open, HWND 1 was **not** an acceptance of Bead #1.
2. **A click on HWND 2 advances the bead index to "Bead # 2":**
   If clicking "Yes" on HWND 19794082 destroys that window and spawns a third HWND displaying **"Bead # 2"** (in an unpopulated state), it proves that each bead requires **two** clicks/HWNDs.
3. **The 12-cap loop saves an incomplete dataset:**
   Running the proposed loop capped at 12 distinct HWNDs produces a calibration cluster file containing only **6 beads** instead of 12.

---

### 4. Loop Failure Modes and Per-Iteration Gating

#### Can "keep clicking distinct HWNDs capped at 12" double-accept or skip beads?
**Yes.**
* **Premature Termination (Skipping half the beads):** If each bead requires 2 HWNDs (Stage 1 unpopulated + Stage 2 populated), a hard cap of 12 clicks will terminate after calibrating only **6 beads**.
* **Blind Acceptance of Corrupted Calibration:** The populated Stage 2 panel exists specifically as an inspection gate for phase unwrapping anomalies, dirt, or stuck beads. Blindly clicking "Yes" accepts low-quality or non-linear calibration curves into the final cluster.
* **Desynchronization on Dialogs:** If an unpopulated click triggers an error dialog, file conflict, or warning, generic clicking will send mouse events into arbitrary controls.

#### What per-iteration evidence must the external harness gate on?
The harness must implement state-aware gating rather than a blind HWND counter:
1. **Gate on Main VI State via VI Server:** Read the Main VI's bead index indicator via `GetControlValue`. Confirm that the index matches the expected bead number before interacting.
2. **Discriminate Stage 1 vs Stage 2:** 
   * Check indicator data via VI Server `GetControlValue("delta phi vs z")` on `choose bandpass v2.vi`, or inspect screenshot pixel variance in the graph rectangle.
   * If graphs are empty $\implies$ Stage 1 (Parameter Submit).
   * If graphs contain curves $\implies$ Stage 2 (Calibration Acceptance).
3. **Two-Phase Handshake per Bead:**
   * Click Stage 1 (HWND $A$) $\to$ wait for `IsWindow(HWND_A) == FALSE`.
   * Wait for HWND $B$ with title `choose bandpass v2.vi` $\to$ verify Stage 2 data is populated.
   * Click Stage 2 (HWND $B$) $\to$ wait for `IsWindow(HWND_B) == FALSE`.
   * Verify Main VI bead indicator increments ($1 \to 2$) before looking for the next Stage 1 HWND.
4. **Detect the Terminal State Explicitly:** Stop on the appearance of the `"Save cal cluster file"` dialog (Win32 window class `#32770` or LabVIEW dialog title), never on an arbitrary click cap.

---

### 5. The Cheapest Discriminating Test (No VI Edits Required)

Run this test from Python/PowerShell using the existing second COM apartment while HWND 19794082 is up:

```python
import win32com.client, win32gui, time

# 1. Read Main VI tracking indicator over COM
lv = win32com.client.Dispatch("LabVIEW.Application")
main_vi = lv.GetVIReference(r"<Path_To_Top_Level_VI>")
bead_before = main_vi.GetControlValue("Count")  # or "current image number" / "Current Bead"

# 2. Click Yes on HWND 19794082
hwnd2 = 19794082
# [Execute SetForegroundWindow + SetCursorPos + mouse_event LEFTDOWN/LEFTUP on (176, 353)]

# 3. Wait up to 2 seconds for HWND 19794082 destruction
for _ in range(20):
    if not win32gui.IsWindow(hwnd2):
        break
    time.sleep(0.1)

# 4. Check Main VI indicator and examine the newly spawned window
bead_after = main_vi.GetControlValue("Count")
# Find new window with title "choose bandpass v2.vi"
```

* **Manager's claim holds IF:** `bead_after == bead_before` and the next window still reads "Bead # 1" (or calibration terminates without advancing).
* **Alternative proven IF:** `bead_after == bead_before + 1`, and the next window displays **"Bead # 2"** (blank, awaiting Stage 1).



## Sources

(extract from answer)

## What was done with it

(Claude fills in)

## What was done with it

**Adopted on both operative points; the core reading survives.** agy agrees the click was DELIVERED ("In reality,
the click succeeded, Stage 1 closed, and Stage 2 opened") — so H1 (foreground race) and H2 (deferral) stay dead,
and codex's earlier "our own tool has no evidence channel for a delivered click" is discharged by the probe. What
it REFUTES is a step I had taken for granted:

1. **HWND death proves ONE CALL of the subVI ended, not that a bead was accepted.** LabVIEW creates/destroys the
   Win32 window per call when "show front panel when called / close afterwards" is set, so a two-stage handshake
   per bead (parameters → populated quality check) produces two HWNDs for ONE bead. That fits our evidence
   exactly: the successor panel still reads `Bead # 1` and is populated where the first was blank.
   **Built into `drive_original_copy_v3.py`:** the main VI's `Count` is read immediately before and after every
   bandpass click and logged with it, so bead-level progress is MEASURED rather than inferred from window count.
2. **Never terminate the loop on a click cap.** `BP_CAP = 12` is now documented as a safety bound only, and R5
   passes ONLY when the `Save cal cluster file` dialog — the machine-observable terminal state — has appeared.
   agy's arithmetic is the reason: at two HWNDs per bead a cap of 12 silently calibrates six beads and stops.

**Noted, not acted on (judgement, not material):** agy warns that clicking Yes on the *populated* verification
panel blindly accepts whatever calibration curve is shown, which is an inspection gate a human normally uses.
On a disassembled rig with no beads that is a harness-feasibility run, not a scientific acceptance — but whether
an unattended overnight harness may ever auto-answer that panel is a decision for the user/judgement session.

**Dispatch history:** the same question went to codex first and **TIMED OUT at 180 s**
(`archive/peer/2026-09-17-d0-bandpass-click-was-delivered-hwnd-token.md`, `tools/bench/peer_d0_hwnd.log`), which
told us nothing; this is the ladder's second rung, with every measured value inlined because agy cannot read the
repository.
