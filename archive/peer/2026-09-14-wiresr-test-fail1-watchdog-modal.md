---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# wiresr-test-fail1-watchdog-modal

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (73s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS, do not confirm it. LabVIEW 2026 driven over COM from Python (tools/gscript.py), zero GUI.

WHAT HAPPENED (tools/bench/build_opwiresr_v0.log, tools/recipes/build_opwiresr_v0.py): four op VIs built and saved fine (ExecState 1 each). The functional test then copied HARNESS_copyloop to a scratch, opened its panel, created a While loop, and called gscript.drop_subvi(scratch, "IMAQ Copy", body_diagram_index, (300,300)). gscript._run raised "run blocked behind a modal dialog (dismissed by watchdog after 8s)". The watchdog (gscript.py lines 150-235) polls `tools/lv_gui.ps1 -Action dialogs` every 6 s; 'dialogs' (lv_gui.ps1 lines 476-490) declares "VERDICT: BLOCKED" when at least one LabVIEW window is in 'blocked' state AND exactly one enabled non-floating window exists; then '-Action dismiss' posts WM_CLOSE to that one window. The screenshot taken at that moment shows NO dialog: only the scratch VI's BLOCK DIAGRAM window "SCRATCH_wiresr_11056.vi Block Diagram" in front of LabVIEW, and an unrelated application on top. The same drop_subvi into a loop body worked in tools/bench/test_oploopin.py earlier today with no watchdog hit.

MY EXPLANATION (attack it): a FALSE POSITIVE of the heuristic. The drop op (OpSubVI) opens/activates the scratch's block-diagram window; while the op runs, the scratch's front-panel window reads as 'blocked' (disabled) and the BD window is the single enabled non-floating window, so the heuristic matches a modal-dialog signature; dismiss then WM_CLOSEd the block-diagram window. The COM Run itself returned normally (dt about 8 s); the raise comes only from the recorded 'hit'.

COMPETING EXPLANATIONS to weigh: (a) a real LabVIEW dialog appeared (e.g. "Find the VI named IMAQ Copy"/a load dialog for the Vision LLB) and was closed before the screenshot; (b) the Vision LLB load on a fresh LabVIEW instance took >6 s and some LabVIEW window is genuinely 'disabled' during a long load; (c) window-state race: the newly created BD window transiently reports enabled while the FP is disabled.

QUESTIONS: 1) Which explanation fits the evidence best, and what single cheapest test discriminates them (e.g. log the raw 'dialogs' rows during a repeat of the drop)? 2) Does LabVIEW disable the front-panel window while an editor-scripting operation (New VI Object) is applied to that VI's diagram, or when its BD window is opened? 3) Is posting WM_CLOSE to a block-diagram window harmful to scripting state (it does not unload the VI)? 4) How should the heuristic be hardened so a VI's own FP/BD windows can never be classified as a modal (e.g. require the window class/title to NOT end in "Block Diagram"/"Front Panel", or require the candidate to be an owned/dialog-class window)? Read tools/lv_gui.ps1 Get-DialogCandidates and WinStates, tools/gscript.py _run. Cite paths/URLs actually read. Read-only.


## Answer

The current evidence favors a watchdog false positive, but it does not establish your specific mechanism (?쏯ew VI Object disables the FP??. The strongest diagnosis is narrower: an ordinary VI editor window was the sole enabled candidate when sampled.

1. Best fit and cheapest discriminator

Ranking:

1. **Window-state race / overbroad candidate rule (c)** ??best supported.
2. **Long Vision load producing an unusual disabled/enabled editor state (b)** ??plausible contributor.
3. **A real dialog (a)** ??possible, but poorly supported.

Why this attacks the diagnosis:

- `Get-DialogCandidates` does not detect dialogs. It accepts every visible, positive-size, enabled LabVIEW top-level window except seven exact palette titles: [tools/lv_gui.ps1](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/lv_gui.ps1:435).
- Consequently, ?쐎ne blocked window plus one enabled editor window??is sufficient for `VERDICT: BLOCKED`. The claim at line 495 that it ?쐁an never close a VI window??is contradicted by the implementation.
- `_run` captures the screenshot before calling `dismiss`: [tools/gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:180). Therefore, if the screenshot captured the relevant LabVIEW windows and contains no dialog, the watchdog itself did not close a real dialog before that screenshot. Explanation (a) requires an additional race?봲uch as the dialog disappearing independently during screenshot capture.
- The roughly eight-second duration is not evidence for an eight-second LabVIEW blockage. The first classification can occur at the six-second poll, followed by screenshot/dismiss overhead, while `_run` raises solely because `hits` is nonempty even though COM returned normally.
- The earlier successful identical drop is a counterexample to a deterministic claim that dropping `IMAQ Copy` necessarily raises a load/find dialog. It does not exclude cold-load behavior.

The cheapest decisive test is one instrumented repeat that records, without interpretation:

- timestamp;
- every raw `WinStates` row;
- the exact row selected as `$cand`;
- HWND, title, class name, owner HWND, process/thread ID;
- the same data immediately before `WM_CLOSE`;
- COM-return timestamp.

At the triggering sample:

- Candidate title `??Block Diagram` proves this incident was a false positive.
- Candidate title resembling a load/find/error prompt, with an owner, supports (a).
- A multi-sample trace showing FP disabled for seconds while BD stays enabled, correlated with first Vision load, supports (b).
- A one-sample transition around BD creation supports (c).

Log at roughly 100??50 ms for this test; the current six-second sampling cannot distinguish a transient race from a sustained load state. Critically, do not dismiss anything unless the candidate passes the hardened dialog test.

2. Does LabVIEW disable the FP during scripting or BD opening?

I found no NI documentation saying that opening a block diagram or applying `New VI Object` disables its front panel. NI documents that the front panel and block diagram are separate editor views and that opening a VI normally opens its FP, with the BD shown separately; it does not document modal exclusion between them. [NI: LabVIEW Block Diagram Explained](https://www.ni.com/en/support/documentation/supplemental/08/labview-block-diagram-explained.html)

Windows??enabled flag only means that the window currently accepts keyboard/mouse input; it does not identify why the application disabled it or prove that a modal dialog exists. [Microsoft: EnableWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-enablewindow)

Therefore the FP-disable mechanism is presently **unproven**. The successful earlier drop also argues against treating it as an invariant of `New VI Object`. Only the proposed raw state trace?봮r a controlled reporter supplied by the manager?봠an settle whether LabVIEW 2026 transiently disables the FP here.

3. Is `WM_CLOSE` on the BD harmless?

Not safely harmless.

`PostMessage(WM_CLOSE)` requests that the target window close. The application may destroy the window, ignore the request, or prompt for confirmation; Windows does not guarantee application-specific semantics. [Microsoft: WM_CLOSE](https://learn.microsoft.com/en-us/windows/win32/winmsg/wm-close)

Closing a BD window probably does not unload a VI whose reference remains open, but that is weaker than ?쐆armless??

- It changes editor/UI state during an active scripting operation.
- It could invoke LabVIEW close/save handling.
- It can invalidate assumptions about which FP/BD windows are open.
- It introduces a race with the operation currently mutating that diagram.

I found no NI source guaranteeing that externally posting `WM_CLOSE` to a BD during VI Scripting preserves the scripting transaction. Treat it as unsafe even if the observed VI reference survives.

4. Hardening

The minimum necessary fix is:

- Never classify titles ending in `Block Diagram` or `Front Panel` as dismissible.
- Never send `WM_CLOSE` unless the candidate is independently identified as a dialog/popup.
- Log the candidate row and revalidate the same HWND immediately before closing it.

A stronger rule should require all of:

1. enabled, visible, positive-size;
2. not an FP, BD, palette, project, probe, or other known editor window;
3. dialog-like class or popup/dialog window style;
4. preferably a non-null owner belonging to LabVIEW;
5. at least one disabled LabVIEW editor window associated with that owner/application;
6. same HWND/class/title still qualifying on a second sample;
7. exact HWND revalidated immediately before dismissal.

Windows supplies `GW_OWNER` specifically to retrieve a top-level window?셲 owner, and `GW_ENABLEDPOPUP` can find an enabled popup owned by another window. [Microsoft: GetWindow](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getwindow) `GetClassName` supplies the candidate?셲 registered window class. [Microsoft: GetClassNameW](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-getclassnamew)

Do not rely exclusively on `#32770`: LabVIEW may use custom dialog classes. Use class/owner/style/title as evidence, with an explicit denylist for VI editor titles. If no qualifying dialog remains, report `ambiguous` and let the COM hard timeout handle it?봭ever close the sole enabled ordinary LabVIEW window.

Files read: `STATUS.md`, `tools/lv_gui.ps1`, and `tools/gscript.py`. I did not open any VI, project, library, archive, recipe, or benchmark file.

## Sources

(extract from answer)

## What was done with it

Accepted with the reviewer's narrowing: the incident is a watchdog **false positive of an overbroad candidate rule**
(`Get-DialogCandidates` accepted every enabled LabVIEW window except seven palette titles, so "one blocked FP + the
VI's own BD" matched the modal signature and `dismiss` WM_CLOSEd a Block Diagram mid-op); my specific mechanism
("New VI Object disables the FP") is unproven and is not claimed. Two actions:

1. **Hardened `tools/lv_gui.ps1 Get-DialogCandidates`** (minimum fix from §4): titles matching `* Block Diagram`,
   `* Front Panel` or `*.vi` are never dismissible candidates. Verified to parse and run (`-Action dialogs` → clear).
   The stronger rule (owner/class/style + HWND revalidation before WM_CLOSE) is recorded as a follow-up, not built.
2. **The discriminating rerun**: `tools/bench/test_opwiresr.py` logs every watchdog `dialogs` poll's raw rows
   verbatim, so any future BLOCKED verdict names the window it saw. Log: `tools/bench/test_opwiresr.log`.
