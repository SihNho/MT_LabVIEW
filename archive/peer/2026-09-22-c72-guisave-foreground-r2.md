# c72-guisave-foreground-r2

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.6507  in 34 / out 43205 / cache-create 145216 / cache-read 2046814  (550s, 31 turn(s))
- **date:** 2026-09-22 00:54:45
- **outcome:** ANSWERED (554s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

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


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write/Bash are denied to this role, so this answer *is* the output (AGENTS.md: "Your output is your answer, nothing else"). Nothing was run, opened or edited.

---

# The claim is refuted by this project's own audit log: **no keystroke was dispatched at all.**

## 1. The single strongest reason the claim is wrong

`tools/lv_gui.ps1:631-641` writes a row to `tools/gui_actions.log` for **every** state-changing action — `click`, `clickprobe`, `keys` — and it does so *before* the `switch ($Action)` at `:644`. No row, no action. It is the one place in this project where "a keystroke happened" is a machine record rather than an inference.

`tools/gui_actions.log` holds 1800 rows and its **last row is `2026-09-18 18:12:14`** (`tools/gui_actions.log:1800`). There is nothing on 2026-09-21 or 2026-09-22. Run 4's save window is 2026-09-22 00:26 (stamp `00:22:34` + the `+230.0 s` at `build_d1_m3a1.log:2683`; both screenshots' taskbar clocks read 오전 12:26).

So **no Ctrl+S, no Ctrl+E and no click was dispatched in run 3 or run 4** — not into the home window, not into anything. The claim is a detailed account of where a keystroke landed, for a keystroke that was never sent. Premises (2)–(4) describe an event with no record.

The previous reviewer already named this exact falsifier — `archive/peer/2026-09-22-c71-run3.md:145-147`: *"A `keys … Key=^s` row in `tools\gui_actions.log` timestamped inside the run-3 save window … would put the failure back downstream of the keystroke."* The test was specified and not run; the new claim was built on top of the same unchecked assumption.

## 2. Alternative explanation — the `-Evidence` argument is never quoted, so `lv_gui.ps1` is never invoked

`tools/gscript.py:272-277`:

```python
cmd = ["powershell", ..., "-Command", "& '{}' {}".format(LV_GUI, " ".join(args))]   # no quoting
```

The sibling helper in the same fleet does it correctly — `tools/bench/bench_prep.py:26-31` quotes every non-alphanumeric argument — and bench_prep's calls are precisely the ones that *do* appear in the log (`gui_actions.log:1770-1775`, `bench prep: open GUIBENCH BD`).

Every `gui_save` call that carries `-Evidence` therefore reaches PowerShell as bare tokens:

| call site | what PowerShell gets |
|---|---|
| `gscript.py:2091` (`^s`) | `-Evidence gui_save: COM SaveInstrument hangs on broken VIs (skill com-driving.md)` |
| `gscript.py:2073-2074` (`^e`) | `… saves nothing (2026-08-30, 2026-09-15)` |
| `gscript.py:2052` (the **new** `clickprobe`) | `… before Ctrl+S (save repair 2026-09-22)` |

`-Evidence` binds only `gui_save:`; the remainder become surplus positional arguments, and `(skill com-driving.md)` is parsed as a sub-expression PowerShell tries to run as the command `skill`. Either failure mode ends the same way: `lv_gui.ps1` never reaches its logging line — exactly what the log shows. And `_lv_gui`'s return value is **discarded** at both `keys` sites, so it fails silently.

This fits every observation you have:

- **mtime never moved on any of the three candidates** — nothing was ever sent.
- **No modal dialog** — nothing reached LabVIEW to raise one.
- **The home window vanished between the captures** — `key esc` (`gscript.py:2096`) is the *only* keystroke in `gui_save` with no `-Evidence` argument, and `lv_gui.ps1:633` exempts it from the gate. It has no multi-word argument, so it is the one call that runs. Esc was delivered, to the foreground, which was the home window. The disappearance is evidence for my account, not yours.
- `focus`, `rect`, `windows`, `shot` carry no `-Evidence` and quote their `-Title`, so they worked — which is why "focused: …" was printed and both screenshots exist.

**The applied repair therefore cannot run, and worse, it will look like it confirms you.** `_fg_click` will get unparseable output, set `fg = "(unreadable probe: …)"`, and raise *"NO Ctrl+S DISPATCHED — foreground after the activating click was …"* (`gscript.py:2089`). That message will be read next cycle as proof of the foreground theory.

## 3. The two specific questions

**Does clickprobe-verified foreground guarantee delivery? No, for four independent reasons.** (a) It cannot execute (§2). (b) Foreground is sampled *before* `SendWait` and can change in between. (c) `SendKeys` uses a journal hook with a SendInput fallback and both are subject to UIPI/UAC — input injected toward a higher-integrity process is dropped with no error returned ([Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys.sendwait?view=windowsdesktop-10.0)). (d) The H5 mode is about LabVIEW's message pump, not about which window is foreground; a foreground reading does not measure a pump. Only the **effect** is a measurement.

**"Ctrl+S on a Front Panel saves nothing" is false as stated.** Ctrl+S is the File»Save accelerator, and the File menu is on both windows — it is visible in the run's own before-capture. NI's Quick Reference Card lists Ctrl-S = Save with no window qualifier ([373353c.pdf](https://download.ni.com/support/manuals/373353c.pdf), [LabVIEW Wiki](https://labviewwiki.org/wiki/Keyboard_shortcut)). What this project actually measured is the narrower line at `docs/keystone-op-spec.md:229` — *"Ctrl+S is a no-op for scripted edits"* — which records an outcome, not a mechanism. The Ctrl+E step, and the "load-bearing loss" in your chain, exist only because those two were conflated.

**Was the VI dirty? Nobody measured it, and the evidence does not settle it.** Scripting edits do set the indicator — NI: *"An asterisk (\*) appears by the VI title to indicate that changes have been made using VI Server"* ([NI forum](https://forums.ni.com/t5/LabVIEW/vi-thinks-it-needs-to-be-saved/td-p/415713?profile.language=en)) — and the state is readable over VI Server as `Modifications:VI Modifications Bitset` / `Modifications:Block Diagram Mods Bitset` ([NI forum](https://forums.ni.com/t5/LabVIEW/unsaved-changes/td-p/2661731)). Neither screenshot resolves a trailing asterisk at 1920×1080, so I will not claim it either way.

Note also that the one measurement that would have closed this was thrown away: `tools/recipes/build_d1_m3a1.py:695-697` *asserts* the scratch is byte-identical to the bed without hashing it, and gate H then deletes the file (`build_d1_m3a1.log:2690`).

## 4. What falsifies each

- **The claim** is falsified by the absence above; it would be revived by a `keys …Key=^s` row in `tools/gui_actions.log` inside 2026-09-22 00:24–00:27.
- **My alternative** is falsified if `lv_gui.ps1` runs normally when handed `_lv_gui`'s exact unquoted string and a new log row appears. Then the keystroke really was sent and eaten, and the foreground story is back in play.

## 5. Cheapest discriminating test — about two seconds, no LabVIEW state touched

Replay `_lv_gui`'s exact string construction against the **read-only** `windows` action:

```
py -c "import subprocess;a=['-Action','windows','-Exception','Approved','-Evidence','gui_save: COM SaveInstrument hangs on broken VIs (skill com-driving.md)'];r=subprocess.run(['powershell','-NoProfile','-ExecutionPolicy','Bypass','-Command',\"& 'tools\\lv_gui.ps1' \"+' '.join(a)],capture_output=True,text=True);print('OUT',r.stdout);print('ERR',r.stderr)"
```

A window list ⇒ my alternative is dead and the foreground theory survives. A PowerShell error (`The term 'skill' is not recognized`, or a positional-parameter binding failure) ⇒ confirmed, and no `gui_save` keystroke has ever left Python. It sends no input and changes nothing.

## 6. What the next build should be, if the test comes back my way

1. **Quote in `_lv_gui`** (`gscript.py:272-277`) with `bench_prep.py:26-31`'s idiom — the correct version already exists in this repo.
2. **Make the silence impossible**: `_lv_gui` raises on a non-zero exit or on `REFUSED`, and `gui_save` asserts a *fresh* `gui_actions.log` row before believing a keystroke was sent. That gate, not a screenshot, is the delivery proof.
3. **Build the dirty-bit reader** (`Modifications:*Bitset`) before the next Ctrl+S attempt — CLAUDE.md's own rule: the second time a failure class is explained by inference rather than read from the machine, the next build is the reader. It separates "keystroke never arrived" from "nothing to save" from "saved after the mtime check".
4. **Stop deleting the scratch on the failure path** — hash it instead.

I do not believe the claim holds. What would change my mind is the test in §5 returning a normal window list together with a `keys` row appearing in `tools/gui_actions.log`.

**Sources:** [SendKeys.SendWait — Microsoft Learn](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys.sendwait?view=windowsdesktop-10.0) · [SendKeys class](https://learn.microsoft.com/en-us/dotnet/api/system.windows.forms.sendkeys?view=windowsdesktop-8.0) · [LabVIEW Quick Reference Card](https://download.ni.com/support/manuals/373353c.pdf) · [LabVIEW Wiki — Keyboard shortcut](https://labviewwiki.org/wiki/Keyboard_shortcut) · [NI forum — VI thinks it needs to be saved](https://forums.ni.com/t5/LabVIEW/vi-thinks-it-needs-to-be-saved/td-p/415713?profile.language=en) · [NI forum — unsaved changes / Modifications bitsets](https://forums.ni.com/t5/LabVIEW/unsaved-changes/td-p/2661731)

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-22 00:5x by the cycle-70 firefighter session, all four points acted on:

1. **The alternative (§2) was CONFIRMED by running §5's discriminating test verbatim** (scratchpad
   `qtest.py`): `_lv_gui`'s exact command shape with the spaced/parenthesized `-Evidence` exited RC 1 with
   `The term 'skill' is not recognized` — a PowerShell parse error, so no Evidence-carrying GUI action from
   gscript ever dispatched. The foreground claim is DEAD as the proximate cause, exactly as §1 argued.
2. **FIXED: `tools/gscript.py` `_lv_gui` now single-quotes every arg** that is not pre-quoted (spaces,
   parens, quotes, backticks). Re-running the same probe through the patched wrapper returned the window
   list (`DISPATCHED OK`) — §4's falsifier for the alternative did NOT fire, the fix is live.
3. **The gui_save clickprobe-foreground repair is KEPT**, not as the diagnosis (refuted) but because it
   turns `focus`'s unverified "focused" into a measured foreground before every Ctrl+S, and its raise now
   reports the OBSERVED per-candidate record — §2's warning that an unreachable probe would fake-confirm
   the foreground theory is moot now the probe actually dispatches.
4. **The dirty-bit reader (§6.3) is DEFERRED, not declined**: run 5's mtime check plus the now-real
   `gui_actions.log` rows separate "keystroke never left Python" from "dispatched but saved nothing". If
   run 5 shows `keys Key=^s` rows and STILL no mtime move, the `Modifications:*Bitset` reader is the next
   build under CLAUDE.md's reader rule.
