ATTACK this claim about the run-4 gui_save failure in tools/bench/build_d1_m3a1.log (stamp 20260922_002234,
`FAIL H no mutator call was REFUSED BY THE MACHINE`, refusal = g.save(WORK, allow_broken=True) ->
"gui_save(WORK_C68M3A1_20260922_002234.vi): file mtime did not move after Ctrl+S on every candidate window").

CLAIM (the diagnosis that is about to drive the next build): the Ctrl+E and Ctrl+S keystrokes never reached
the VI's windows because they were dispatched while a DIFFERENT window held the Windows foreground — the
LabVIEW 2026 "Getting Started" home window (title exactly "LabVIEW"), left up by the fresh LabVIEW restart
that this run performs. Chain: (1) the run restarts LabVIEW, the home window opens and holds foreground —
the run's own before-save screenshot tools/bench/m3a1_save_before_20260922_002234.png shows it in FRONT of
the WORK VI's Front Panel; (2) lv_gui.ps1 'focus' (lines 682-688) calls [LVGui]::Focus and prints
"focused: <title>" WITHOUT verifying the window became foreground; (3) lv_gui.ps1 'keys' (lines 793-798) is
SendKeys::SendWait, which types into whatever IS foreground; (4) the VI had ONLY a Front Panel window, and
Ctrl+S on a Front Panel saves nothing (project finding 2026-08-30/2026-09-15, recorded in gui_save), so the
BD-opening Ctrl+E that went to the home window was the load-bearing loss; (5) the after screenshot
(m3a1_save_after_20260922_002234.png) shows the home window GONE — consistent with gui_save's own Esc
closing it mid-sequence — and no modal dialog anywhere, so the raise's stated cause ("a modal dialog blocks
the save") was invented, exactly as archive/peer/2026-09-22-c71-run3.md Failure-2 §5 said.

FIX ALREADY APPLIED (attack this too): tools/gscript.py gui_save now (a) replaces the blind H5 title-bar
`click` with `clickprobe` and parses its JSON `fg_after_click.title`, sending Ctrl+E/Ctrl+S ONLY when that
measured foreground title contains the candidate window's title (one retry), (b) raises with the OBSERVED
per-candidate record plus the window list at entry, never an invented cause.

ALREADY RULED OUT: (1) the double-quote -Title form — tools/bench/diag_c68_quote2.log shows both quote
forms focus a real spaced title; (2) a modal dialog — the run's restart printed "VERDICT: clear", the after
screenshot shows none; (3) an unwritable target — WORK is a fresh shutil.copy2 under claudeDev, the same
path the run had just mutated over COM.

Name the strongest reason this diagnosis is wrong, an alternative explanation that fits the same evidence
(both screenshots, mtime never moving on ANY of the three candidates, no dialog), what would falsify the
claim, and the cheapest discriminating test. In particular: does the clickprobe-verified foreground fix
actually guarantee delivery, or can LabVIEW's UI loop still swallow SendWait keystrokes with the right
window foreground (the H5 failure mode)? And would the FP-candidate Ctrl+S (after the home window closed)
have saved the VI if it were dirty — i.e. is "FP Ctrl+S saves nothing" actually true in LabVIEW 2026, or is
the real cause that the VI was NOT dirty in the editor's eyes by save time?
