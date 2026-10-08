---
type: facts
status: current
date: 2026-10-08
card: 149-a1-1
---
# Card 149-a1-1 facts: the reader's packages were NOT removed - they live in the Claude app's MSIX-virtualised user site, which this runner's processes do not see; the 01:23 set needs numpy 2.2.6 (installed numpy 1.26.4) -> RETURN at step 2, nothing installed, no LabVIEW

## Step 1 - environment (offline probe `tools/bench/diag_c149_a1_1_env.py`, logs `diag_c149_a1_1_env.log`, `diag_c149_a1_1_env2.log`)
- `py` = `C:\Users\KimLab\AppData\Local\Programs\Python\Python310\python.exe` 3.10.9, the only interpreter (`py -0p`, env.log:3,16); no py.ini, no PYTHONPATH/PYTHONHOME/VIRTUAL_ENV (env.log:6-15).
  Same exe in every runner bgrun before and after (e.g. motor_session_start_cycle148.log:1, cycle149.log:1).
- Missing here: comtypes, rapidocr_onnxruntime, onnxruntime, cv2, winsdk, shapely, pyclipper (env.log:18-29); present: numpy 1.26.4, PIL 10.3.0, pywin32 312, PyYAML 6.0.1 (env.log:22-28,34-38).
- Global site-packages dir mtime 2026-09-07 21:29:40, NO entry modified since 2026-10-07 (env.log SITEDIR line) -> nothing was uninstalled from it.
- Real user site `C:\Users\KimLab\AppData\Roaming\Python\Python310\site-packages`: ABSENT (env.log SITEDIR line); pip cache: no wheels.
- The packages exist in `C:\Users\KimLab\AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python310\site-packages`
  (Claude desktop app MSIX LocalCache = where %APPDATA% writes from inside the app container land), NOT on this process's sys.path (env2.log:50).
  Installed 2026-09-23 05:25-05:39 (env2.log:51-65): comtypes 1.4.17, rapidocr_onnxruntime 1.4.4, onnxruntime 1.23.2, opencv_python 5.0.0.93,
  numpy 2.2.6, shapely 2.1.2, pyclipper 1.4.0, protobuf 7.36.2, flatbuffers 25.12.19, sympy 1.14.0, mpmath 1.3.0, coloredlogs 15.0.1,
  humanfriendly 10.0, pyreadline3 3.5.6, winsdk 1.0.0b10.
- What changed 01:23 -> 17:57: the runner supervisor was RE-LAUNCHED at 2026-10-08 12:31:40 (runner_supervisor.log:47-49); the 01:23 read ran
  under the launch of 2026-10-07 23:43:33 (runner_supervisor.log:4-6). Inference (not measured): the 23:43 launch ran inside the app container
  (user site = LocalCache dir), the 12:31 launch outside it. No pip/uninstall in tools/bench logs (grep `pip install`: none in this window).

## Step 2 - restore: NOT DONE (card rule "a restore would install a different version -> RETURN")
- At 01:23 the user site (LocalCache) preceded global site-packages, so the working OCR stack ran on numpy 2.2.6 (inference from sys.path order).
- opencv_python 5.0.0.93 METADATA: `Requires-Dist: numpy>=2; python_version >= "3.9"` (LocalCache ...\opencv_python-5.0.0.93.dist-info\METADATA:42);
  installed numpy is 1.26.4 -> restoring the 01:23 OCR set needs numpy 2.2.6 in place of / in front of 1.26.4 = an existing package changed.
- comtypes 1.4.17 alone (no deps) could be restored cleanly, but the 01:23 read got its 55 items from OCR (diag_c147_a1_1_el.log:20-26: UIA 0 items,
  MSAA 0 listitems, OCR rapidocr count 55), so comtypes alone would not make the read work. Nothing installed, upgraded or removed.

## Not done (RETURN): EL read of 569ffbf5, EL-ADVISORY, adopt, final EL expected, fresh load, graph, load_by_vi. LabVIEW never started by this card.
- memory_model.json, adopted_scratch.jsonl, s05 3f9ac26b / s04 95e408ff / s03 282301ca / bed 39511877 / scratch 569ffbf5, stagekit, stagexec,
  gscript, elrule: not opened, not written. Handles: n/a (no LabVIEW).

## Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c149_a1_1_env.log | probe, not a build/stage log (prediction met: imports missing) | - | facts recorded; returned | - |

OPEN: restore by (a) `py -m pip install --user --no-deps` of the exact 15-package LocalCache set incl. numpy 2.2.6 (shadows global 1.26.4 for
every non-app Python process), (b) relaunch the runner from inside the Claude app so the LocalCache site is visible again, or (c) another route?
