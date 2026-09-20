# d0-bandpass-click-not-delivered

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-17
- **outcome:** ANSWERED (213s)
- **why asked:** failed prediction P6 in D0 v2 (`tools/bench/drive_original_copy_v2.log`, 91.6 s and again at
  410.1 s): one `lv_gui.ps1 -Action click -X 175 -Y 353` on the `choose bandpass v2.vi` subVI panel's "Yes"
  button had NO effect, although the identical click at the identical coordinate worked three times in the
  manual walk 20 minutes earlier (`tools/gui_actions.log`, 01:56:05/40/45).
- **verdict:** **REFUTED my explanation.** Static front-panel events are registered when the VI enters run
  mode and are QUEUED, so "the Event structure had not been entered yet" cannot swallow a delivered click;
  and a click deferred by a locked panel would be processed later, not lost — yet the panel was still
  unchanged 2 minutes on. So the click was never DELIVERED to that panel.

## Question

A PREDICTION OF OURS FAILED, twice in a row would be expensive, so attack my explanation before I rebuild.

READ THESE FILES IN THE REPO:
  tools/bench/drive_original_copy_v2.py        (the driver; function `bandpass_round`, and `click`/`focus` helpers)
  tools/bench/drive_original_copy_v2.log       (the run: lines at 63.7s, 66.0s, 66.8s, 91.6s)
  tools/lv_gui.ps1                             (the ONLY mouse/keyboard path; see class LVGui, methods Click, Focus, Find)
  tools/gui_actions.log                        (last ~12 rows, dated 2026-09-17 — the MANUAL walk that SUCCEEDED)

SETUP. A LabVIEW 2026 top-level VI (a plain file copy of a production main VI) is run over ActiveX
with Run(False) from a dedicated COM apartment. During its calibration stage it opens a SUBVI front
panel titled "choose bandpass v2.vi", which has a large Boolean button labelled "Yes" under the
caption "Selected?". The operator normally clicks that Yes once per bead.

WHAT WORKED (2026-09-17 01:56, MANUAL, recorded in tools/gui_actions.log):
  three clicks at the SAME absolute screen point X=175,Y=353, at 01:56:05, 01:56:40 and 01:56:45,
  each issued by `lv_gui.ps1 -Action click -X 175 -Y 353`, and the calibration advanced through all
  three beads and went on to open the "Save cal cluster file" dialog. So the coordinate, the tool
  and the mechanism are all PROVEN on this exact machine, screen resolution and VI.

WHAT FAILED (2026-09-17 02:12, the SAME machine, SAME resolution, SAME VI copy, 20 minutes later):
  the harness detected the window by title, measured its rect with `-Action rect` as
  left=29 top=72 right=1060 bottom=874 (so 175,353 is ~146 px inside the left edge and ~281 px below
  the top, and a screenshot confirms the Yes button occupies roughly x 113..237, y 325..382 — the
  click point is dead centre on the button), called `lv_gui.ps1 -Action focus -Title 'choose bandpass'`,
  slept 0.5 s, then issued ONE `-Action click -X 175 -Y 353`. lv_gui reported "click 175,353".
  The panel did NOT respond: 25 s later it was unchanged, and a diagnostic screenshot taken 2 MINUTES
  after the click still shows the same panel, still reading "Bead # 1", with the "Cal image with
  chosen filter" indicator still blank. No modal dialog is present; `-Action windows` lists
  "choose bandpass v2.vi", the main VI panel, and "LabVIEW".
  The one difference I can name from the successful manual walk is TIMING: the harness clicked 2.3 s
  after the window first appeared in the window list, whereas the human clicked at an unknown but
  certainly much later moment.

MY EXPLANATION, WHICH I WANT YOU TO REFUTE: the click arrived before the subVI's diagram was ready to
consume it — either the Event structure had not been entered yet, or a `SetForegroundWindow` +
click 0.5 s apart let the click be consumed by window activation instead of by the button — and the
fix is simply to retry the click (focus, move, dwell, click, verify, repeat up to N times) until the
panel advances.

ALREADY RULED OUT (do not spend your answer on these):
  * Wrong coordinates / window moved: the rect was measured at click time and the screenshot shows
    the Yes button centred on the click point.
  * Wrong window: only one window matches "choose bandpass"; `Find` takes the first visible LabVIEW
    window whose title contains the substring.
  * LabVIEW blocked behind a modal: `-Action dialogs` reported no modal, and a second COM apartment
    was answering ExecState/GetControlValue calls throughout (7 successful calls logged).
  * A VI-Server shortcut: we know SetControlValue raises no Value Change event, so it cannot replace
    a click on a control the diagram waits on with an event.

GIVE ME:
 1. The strongest reason my explanation is WRONG or incomplete for LabVIEW 2026 specifically. In
    particular: is it actually true that a LabVIEW front-panel Boolean can silently swallow a
    synthetic mouse_event click, and what are the DOCUMENTED conditions under which an injected
    click (SetCursorPos + mouse_event LEFTDOWN/LEFTUP with no intervening motion, which is what
    lv_gui.ps1's Click does — read it) is not delivered to the control? Consider at least: the
    button's mechanical action (latch when released vs switch), a click landing during the panel's
    own redraw, LabVIEW's "lock front panel until the event case completes", the foreground-window
    lock (Windows refusing SetForegroundWindow from a background process) and whether a click into a
    non-foreground window is consumed by activation.
 2. An ALTERNATIVE explanation that fits the SAME evidence — including the fact that the identical
    click at the identical coordinate worked three times 20 minutes earlier, and that the panel is
    still unresponsive two minutes later rather than catching up on a buffered click.
 3. The observation that would FALSIFY my explanation.
 4. Whether a bounded RETRY loop is the right fix at all, or whether it risks double-accepting (e.g.
    a second click landing on the NEXT bead's panel and skipping a bead) — and if so, what
    per-iteration evidence should gate each retry, given that the only progress signals available to
    an external harness are the window list, the window rect, and a screenshot.
 5. The CHEAPEST discriminating test that separates my explanation from your alternative, runnable
    from PowerShell/Python outside LabVIEW without editing the VI.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Your explanation is wrong in its main LabVIEW mechanism: **a static Event structure does not need to have been entered before it can receive the click.** LabVIEW registers static front-panel events when the VI enters run mode and queues them until the Event structure handles them. NI explicitly says its event queue prevents loss of user events. Therefore, “the Event structure had not been entered yet, so the click was silently swallowed” is not a valid explanation unless this VI uses late **dynamic** registration—something the supplied evidence does not establish. [NI’s 2026 event documentation](https://www.ni.com/en/support/documentation/supplemental/06/event-driven-programming-in-labview.html), [NI discussion of static registration timing](https://forums.ni.com/t5/LabVIEW/Event-structure-not-clearing-the-Queue-after-it-exits-the-SubVI/td-p/3041157).

### 1. What can actually discard or defer this click

- **Mechanical action:** Latch When Released requires press and release within the control, then remains asserted until the diagram reads the terminal. Switch actions persist instead. None of these actions arbitrarily discards a correctly delivered down/up pair. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999b.pdf). Your helper actually moves from `(175,353)` to `(176,353)` before button-down, but performs no motion between down and up, so mechanical action does not explain this miss unless ownership/capture changed. See [lv_gui.ps1](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/lv_gui.ps1:226).

- **Redraw:** ordinary Windows repainting is not a documented click-loss condition. Mouse input is queued, while `WM_PAINT` is normally dispatched only when higher-priority queued messages are gone. [Microsoft WM_PAINT documentation](https://learn.microsoft.com/en-us/windows/win32/gdi/wm-paint), [message-queue documentation](https://learn.microsoft.com/en-us/windows/win32/winmsg/about-messages-and-message-queues).

- **“Lock front panel”:** LabVIEW defers front-panel interactions and later processes them in order; it does not normally throw them away. Thus, a click still having no effect two minutes later means either the locking event never completed—a persistent UI/dataflow deadlock—or the click never reached this front panel. It does not support a brief “not ready yet” interval. [NI lock-panel explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MlVSAU), [NI description of buffered interactions](https://forums.ni.com/t5/LabVIEW/Unexpected-effect-of-Lock-Front-Panel-in-Event-Structure/td-p/1546832).

- **Foreground/activation:** this is genuinely possible, but the harness did not measure it. `SetForegroundWindow` can return zero under documented foreground-lock conditions, and Windows can activate an inactive window while discarding the initiating mouse message via `MA_ACTIVATEANDEAT`. [SetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setforegroundwindow), [WM_MOUSEACTIVATE](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-mouseactivate). Your `Focus` ignores the return value and never calls `GetForegroundWindow`; see [lv_gui.ps1](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/lv_gui.ps1:207).

- **Synthetic-input delivery:** `mouse_event` merely inserts synthetic mouse input and has no return value; Microsoft has superseded it with `SendInput`. A low-level mouse hook can identify and suppress injected input. I found no NI documentation saying LabVIEW 2026 itself rejects injected clicks—and the three successful calls prove this installation normally accepts them. [mouse_event](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event), [low-level mouse hook behavior](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelmouseproc).

So `lv_gui` printing `click 175,353` proves only that its function returned, not that the Yes control received either mouse message.

### 2. Strong alternative explanation

The strongest alternative is a **z-order/foreground race**, not calibration readiness.

The stored 02:12 screenshot has the bandpass panel on top, while the later diagnostic capture has the main VI covering it even though the bandpass HWND still exists: [stuck screenshot](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/d0_shots_v2/20260917_021053_bandpass_stuck_run1_1.png), [later screenshot](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/d0_shots_v2/diag_bandpass_now.png). Therefore z-order was unstable during this run.

`Find` proves only that a visible titled HWND exists; the rectangle proves only where that HWND would be. Neither proves that the HWND was foreground or topmost at button-down. Windows normally routes mouse input to the window under the cursor unless another window owns mouse capture. [Microsoft mouse-input routing](https://learn.microsoft.com/en-gb/windows/win32/inputdev/about-mouse-input).

That fits all evidence:

- The manual clicks worked when the subVI was stably foreground.
- The harness left roughly 0.5 seconds after `Focus` for the main VI or subVI to re-raise.
- A click delivered to the main panel or consumed during activation creates no queued bandpass event, so nothing “catches up” later.
- The existing automation notes already warn that a just-refocused click can merely activate a pane and that foreground title pixels must be verified; see [lv_gui.ps1](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/lv_gui.ps1:65).

A second plausible alternative is a persistent front-panel lock/deadlock. That would defer the click indefinitely, rather than swallow it because the Event structure was briefly not ready.

### 3. Observation that would falsify your explanation

This would falsify both branches of your explanation:

> At least 10 seconds after the panel appears, verify immediately before button-down that `GetForegroundWindow()` is the bandpass HWND, `WindowFromPoint(176,353)` belongs to that HWND, and no window has mouse capture or menu mode; the injected click still fails, but an immediate physical click at the same point succeeds.

The delay rules out “too early”; the HWND checks rule out activation consumption. Windows exposes foreground, active, focus, capture, and menu state through `GetForegroundWindow` and `GetGUIThreadInfo`. [GetForegroundWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getforegroundwindow), [GUITHREADINFO](https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-guithreadinfo).

### 4. Do not use an ungated retry loop

Blind retries are unsafe. LabVIEW can buffer interactions while a panel is locked, and this subVI apparently reuses the same title, HWND location, and Yes coordinate for successive beads. A delayed first click plus a scheduled retry could accept bead 1 and then land on bead 2.

Treat every screenshot state as a transaction token:

1. Before clicking, require the bandpass title, expected rectangle, foreground HWND, and screenshot/OCR showing the expected `Bead # n`.
2. Issue exactly one click for that token.
3. Do not click again until one of these occurs:
   - the bandpass window is absent continuously for a settling interval;
   - the fixed `Bead #` ROI changes from `n` to `n+1`;
   - the Save dialog appears.
4. If the screenshot remains byte-/template-equivalent, allow one retry only after re-verifying foreground, `WindowFromPoint`, capture, menu mode, and the same bead number.
5. Once `Bead # n+1` appears, invalidate every pending retry for `n`.

Also fix the accounting bug: [bandpass_round](/G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/bench/drive_original_copy_v2.py:509) increments `answered` even when `closed=False`.

### 5. Cheapest discriminating test

On the existing stuck panel, run one external PowerShell/Python probe that, in the same process and immediately around one click, logs:

`bandpass HWND → SetForegroundWindow return → GetForegroundWindow → WindowFromPoint(176,353) → GUITHREADINFO hwndCapture/menu flags → mouse down/up → same values afterward`.

Do it once immediately and once after 10 seconds, with no retry loop. If the foreground/point check is wrong, the z-order alternative wins. If the verified late click advances, your timing/activation explanation survives. If the verified late click still fails but a physical click succeeds, your explanation is falsified and the injected-input path is the problem.

## Sources

(extract from answer)

## What was done with it

**Accepted in full; it stopped the rebuild I was about to write.** Four things are carried forward.

1. **My mechanism is dead.** "The subVI's Event structure was not ready, so the click was swallowed" is not a
   LabVIEW behaviour: static events are registered at run-mode entry and queued, and a locked panel *defers*
   interaction rather than discarding it. Either explanation predicts the click arriving late — but the panel
   was byte-identical 2 minutes later (`tools/bench/d0_shots_v2/20260917_021053_bandpass_stuck_run1_1.png`
   vs `.../diag_bandpass_now.png`). **So the question is no longer "why was it ignored" but "did it ever
   reach that window".**
2. **`lv_gui` prints `click 175,353` when its function RETURNS, not when a control receives the message.**
   `mouse_event` has no return value, `Focus` discards `SetForegroundWindow`'s return and never reads
   `GetForegroundWindow`, and Windows may activate a background window while EATING the initiating mouse
   message (`WM_MOUSEACTIVATE` → `MA_ACTIVATEANDEAT`). Our own GUI tool therefore has **no evidence channel
   for "the click landed"** — this is the project's "when a diagnosis is guessed twice, build the READER"
   case, and the reader is named in §5 of the answer: one probe logging, around a single click, the
   `SetForegroundWindow` return, `GetForegroundWindow`, `WindowFromPoint(x,y)`, and `GUITHREADINFO`'s
   `hwndCapture` / menu flags, before and after. **NOT built here** — see below.
3. **A blind retry loop is REFUSED, and the reason is specific to this VI**: the panel reuses the same title,
   position and Yes coordinate for every bead, so a late first click plus a scheduled retry can accept bead 1
   and then land on bead 2. Any retry must be gated on a transaction token (foreground HWND + WindowFromPoint
   + no capture/menu + the `Bead # n` ROI unchanged), and every pending retry for *n* is invalidated the
   moment `Bead # n+1` appears.
4. **A real code defect it found by reading our source**: `bandpass_round`
   (`tools/bench/drive_original_copy_v2.py`) increments `answered` even when `closed=False`, which is why the
   log reads "1/3 answered" for a panel that was never answered at all. Left unfixed **on purpose** — the
   material session's failure budget (2) was spent on this exact failure twice, so the next build is a
   judgement call, not a patch made under pressure.

**Not adopted, and why:** codex reads the two screenshots as showing the main VI covering the bandpass panel
in the later capture. It does not — the bandpass panel is on top in both. That weakens its *evidence* for an
unstable z-order but not the *mechanism*, which is documented independently; the probe in §5 is what would
settle it.
