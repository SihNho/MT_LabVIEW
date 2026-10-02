I'm checking the claim against the code and logs. Doing that turned up a documented alternative cause.

**1. Strongest reason the claim is wrong.** It treats a foreground-window loss as the cause. The code and logs don't isolate that cause, and the repo already records another reason Ctrl+S fails.
- Several repo docs say gui_save's Ctrl+S is "a no-op for scripted edits" (`docs/keystone-op-spec.md:229`, `.claude/skills/labview-automation/references/gui-recipes.md:280`).
- gui_save was written for the broken-VI case (`tools/gscript.py:1999-2010`), and it has failed at "seven logged sites" and later "eight" (`docs/cycle27-plan.md:459`, `:604`).
- Those failures include run 10, which hit it on a scratch VI (`tools/bench/build_d1_routeb_v7_run10.log:367`). That is a path with no relationship to the home window left behind by this run's restart.
- The same failure on the same VI class in runs 1 and 3 of this recipe (`build_d1_m3a1.log:1967`, `:2685`) points to something systematic. A foreground race would more likely succeed sometimes.

**2. Alternative explanations of the same evidence.**
- **(a) Save refused for the in-memory state.** The VI is at ExecState 0 with scripted edits (`build_d1_m3a1.log:2682`). LabVIEW may simply not write it, or write nothing that moves the mtime. Another possibility is an operation that finishes without moving the mtime.
- **(b) The mtime check is the failing part.** mtime is read from a path that may differ from where LabVIEW wrote, or the filesystem timestamp resolution is coarse. The claim doesn't rule this out.
- **(c) The keystroke did land but Ctrl+S was eaten.** `Focus()` taps Alt and then Esc (`tools/lv_gui.ps1:236-247`). The code comments say this leaves LabVIEW in menu mode (`gscript.py:2050-2053`), and the file's own comment notes SendKeys '^s' leaves the File menu active.

**3. Weakness in the chain itself.**
- Step 2 is true: `focus` prints "focused" unconditionally (`lv_gui.ps1:682-687`).
- But gui_save tries up to three candidate windows, each with its own `Focus()` call and Alt-tap (`gscript.py:2031-2049`). The claim needs foreground to fail on all three, and it needs the home window to be the only foreground holder each time.
- Step 4 ("the BD-opening Ctrl+E was the load-bearing loss") is unverified. If Ctrl+E had landed, there is no evidence the Ctrl+S would have saved.
- I could not open the before/after screenshots. The PNGs are not in the checkout, so step 1 (home window in front) rests on the log's description, which I can't verify.

**4. What would falsify the claim.**
- A gui_save success on a fresh restart with the home window up.
- A failure with the target window confirmed foreground (via `clickprobe`).
- A failure on a VI that was never edited in memory.

**5. Cheapest discriminating test.** Re-run gui_save on a trivial copy in a fresh instance. Do it once with the home window closed first and once with it left open, and run the unmodified-VI save as a control. Log `GetForegroundWindow` and the mtime before and after each Ctrl+S. If saves fail with the target confirmed foreground, the claim is dead.

**On the proposed fix.** It is worth doing, but as a diagnostic rather than a repair. A foreground gate would fail loudly, which is what STATUS.md:54 asked for. It would not make the save work if (a) or (c) is the cause, so the build should not be planned on the assumption that it does.

DEFECT: major - The claim presents an untested foreground-race as the established cause while the repo documents Ctrl+S failing on scripted-edit and broken VIs, and gui_save failing at eight logged sites.