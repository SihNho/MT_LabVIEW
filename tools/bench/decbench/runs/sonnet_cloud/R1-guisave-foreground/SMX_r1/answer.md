The foreground-theft chain is not supported. A better-fitting cause sits upstream of it. This is from reading files only; I executed nothing.

**1. Strongest reason it is wrong: no keystroke was ever dispatched, so none could be misdelivered.**
- `lv_gui.ps1:631-641` appends an audit row for every non-Esc `keys`/`click`/`clickprobe` before the action runs.
- `tools/gui_actions.log` (1800 lines) ends 2026-09-18 18:12:14. It has 0 `gui_save` rows, for run 4 (2026-09-22) and for any other run.
- `gui_save`'s three state-changing calls pass multi-word `-Evidence` unquoted (`gscript.py:2028-2029, 2044-2045, 2049`). `_lv_gui` does `" ".join(args)` into one `-Command` string (`gscript.py:274-276`).
- The helper is `[CmdletBinding()]` with no catch-all parameter (`lv_gui.ps1:95-125`). The extra words ("open", "title-bar", "(H5)") should fail binding before the gate and log run.
- Callers that quote their evidence do appear in the log: `bench_prep.py:28-29` has 20 "bench prep" rows, and `drive_original_copy_v2.py:340` quotes with `'%s'`.
- The unquoted callers, `gui_save` and `remove_bad_wires` (`gscript.py:1667-1676`), have 0 rows.
- Ruled-out item (1) only tested `-Title` (`diag_c68_quote2.py:1-7`). `-Evidence` was never exercised.
- Focus works: `diag_c68_quote2.log:4-5` shows a real spaced title focusing. So `focus` and `rect` run, while `click`, `^e` and `^s` silently do not.
- The `Esc` call is exempt from the gate (`lv_gui.ps1:633`), so it is the only keystroke that lands.

**2. Alternative explanations of the same evidence**
- **B (primary):** the argument-splitting above. Which window holds the foreground is irrelevant.
- **D:** a modal opens after `^s` and the unconditional Esc (`gscript.py:2054`) cancels it. Ruled-out item (2) does not exclude this. The `VERDICT: clear` at `build_d1_m3a1.log:2017` comes from the pre-batch restart, about 228 s before the save (`:2678`). `diag_c68_guisave.py:129` would read dialogs between `^s` and Esc, but no `diag_c68_guisave` log exists in `tools/bench`.

**3. Weaknesses inside the claim's own chain**
- The run-4 PNGs are not in this checkout, so steps (1) and (5) cannot be checked.
- The "before" shot is taken before `g.save` (`build_d1_m3a1.py:678-682`), so before every `focus`. It cannot show the foreground at dispatch time.
- "Home window gone" cuts against "home window held the foreground". `Focus()` does an Alt tap, SW_RESTORE and `SetForegroundWindow` (`lv_gui.ps1:236-246`), and `gui_save` calls it at least three times (`gscript.py:2025-2026, 2032`). The claim needs every call to fail, yet the home window ends up gone.

**4. What would falsify the claim**
- A `keys` row with evidence starting `gui_save:` in `gui_actions.log` at 2026-09-22 00:2x.
- A measured foreground title of "LabVIEW" at dispatch. Neither exists.

**5. The proposed fix**
- `clickprobe` is itself state-changing (`lv_gui.ps1:631`) and needs `-Exception` and `-Evidence`.
- Called through `_lv_gui` with unquoted evidence, it should hit the same binding failure. Its output would be a binding error rather than the JSON the foreground check needs.
- So the fix would fail loudly instead of saving.
- Quote the evidence first, as `drive_original_copy_v2.py:340` does.
- Make `gui_save` check that each `keys` or `click` output starts with the expected `keys ` or `click ` instead of discarding it (`gscript.py:2028, 2044, 2049`).

**6. Cheapest discriminating test (no LabVIEW, no GUI, no keystroke)**
Run `_lv_gui("-Action","md5","-In","tools/gscript.py","-Evidence","gui_save: x y (H5)")`. If B is right, PowerShell prints a binding or "H5 not recognized" error. If the claim is right, it prints an md5 line.

**What would change my mind:** a `gui_save` row in the log, or the test printing a hash. One caveat: the checkout's log could be stale if it was not committed with the run. The earlier same-signature failure (`build_d1_routeb_v7_run10.log:367`, run 2026-09-19) also left no rows.

DEFECT: blocker - the claim assumes Ctrl+E/Ctrl+S were dispatched and misrouted, but the audit log and the unquoted `-Evidence` in `gscript.py:2029/2045/2049` indicate they were never sent, and the proposed `clickprobe` fix would fail the same way.