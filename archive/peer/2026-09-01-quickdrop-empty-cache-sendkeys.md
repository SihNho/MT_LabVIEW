---
type: peer-review
status: historical
date: 2026-09-01
tags: [peer-review]
disposition: legacy
---

# quickdrop-empty-cache-sendkeys

- **agent:** codex
- **date:** 2026-09-01
- **outcome:** ANSWERED (73s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

LabVIEW 2026 Quick Drop (Ctrl+Space) automation problem, need web sources (forums.ni.com, NI docs). Symptoms: first Quick Drop invocation in a fresh LabVIEW instance shows a completely EMPTY list box, and text sent via Windows SendKeys to the Quick Drop search field never appears (field stays blank), even after clicking the field first and waiting 5 seconds. Questions: (1) How long does the Quick Drop name cache take to build on first use, and does the dialog accept typed input while the cache is building? (2) Is there a way to pre-build or persist the Quick Drop cache (options, config token, menu item) so it is warm at startup? (3) Known issues with SendKeys/synthetic keystrokes reaching the Quick Drop search box - does it require real keyboard focus, and is there a reliable programmatic alternative? Already ruled out: the dialog IS open and visible (screenshot-verified); Enter after typing places nothing because the field is empty. Attack the hypothesis 'wait longer and it will work' - what else explains a permanently empty Quick Drop list?

## Answer

The evidence argues against ?쐗ait longer and it will work.??Cache construction can block Quick Drop for seconds, but it does not explain a dialog that remains empty and refuses all text indefinitely.

1. Cache-build time and input behavior

NI does not document a fixed maximum cache-build time. It depends on palette size, add-ons, disk/antivirus activity, and compiled-object state.

The best concrete measurement I found is a 2026 NI forum investigation using Process Monitor:

- About 0.2 seconds loading Quick Drop resources/checking its object cache.
- About 0.2 seconds scanning `.mnu` palette files.
- About 6 seconds reading roughly 2,000 VIs.
- During the stall, Quick Drop stopped accepting characters, and characters typed during the freeze were lost?봭ot queued for later processing. [NI forum investigation](https://forums.ni.com/t5/LabVIEW/Quick-drop-bug-undesired-behavior-Window-unresponsive-after/m-p/4479056)

An older report explains why: while Quick Drop says ?쏱opulating list,??it blocks in a property-node call that retrieves all palette object names. [NI Quick Drop Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Cancel-load-for-Quick-Drop-Palette-Search-etc/idi-p/1459390)

Therefore:

- A normal cold start may take several seconds, potentially longer on a large installation.
- Input may be ignored/lost while LabVIEW is blocked.
- There is no sourced basis for a particular safe timeout such as 5, 10, or 30 seconds.
- If the dialog remains responsive enough to click but its text control never reflects input, that is more suggestive of focus/input routing or a broken Quick Drop/palette state than ordinary cache construction.

NI?셲 normal documented behavior is that the dialog initially contains all palette VIs and narrows that list as characters are typed. A permanently blank initial list is therefore abnormal. [NI Quick Drop documentation](https://www.ni.com/en/support/documentation/supplemental/08/boost-labview-productivity-with-quick-drop.html)

2. Warming or persisting the cache

The supported pre-warming option is:

`Tools 쨩 Options 쨩 Controls/Functions Palettes 쨩 Loading 쨩 Load palettes during launch`

An NI employee specifically recommends this so palette information is loaded before Quick Drop is first used; the tradeoff is slower LabVIEW startup. [NI forum recommendation](https://forums.ni.com/t5/LabVIEW/Quick-drop-bug-undesired-behavior-Window-unresponsive-after/m-p/4479056)

That is stronger than trying to persist a Quick Drop-specific cache. I found no NI documentation for a public ?쐀uild Quick Drop cache??menu command or supported INI token dedicated to persisting its generated name list.

Quick Drop object shortcuts are persisted in `LabVIEW.ini`, but those are aliases, not the palette-name cache. [NI Quick Drop documentation](https://www.ni.com/en/support/documentation/supplemental/08/boost-labview-productivity-with-quick-drop.html)

Useful maintenance suggestions from the same NI forum thread are:

- Update LabVIEW to the latest patch.
- Mass compile `<LabVIEW>\resource\dialog\QuickDrop`.
- Disable Quick Drop?셲 ?쏣nable relevancy-based search??option while diagnosing.
- Check antivirus interference with LabVIEW, `vi.lib`, and add-on directories.  
  [NI forum thread](https://forums.ni.com/t5/LabVIEW/Quick-drop-bug-undesired-behavior-Window-unresponsive-after/m-p/4479056)

Those are troubleshooting measures, not documented cache APIs.

3. SendKeys and reliable automation

I found no NI source promising that Quick Drop supports Windows `SendKeys`, UI Automation, `WM_CHAR`, or any other external synthetic-input mechanism. NI documents human keyboard interaction only. [NI Quick Drop documentation](https://www.ni.com/en/support/documentation/supplemental/08/boost-labview-productivity-with-quick-drop.html)

Windows `SendKeys` targets the active application/control. Microsoft explicitly says the target application must first be activated and that the active control receives the characters. [Microsoft SendKeys guidance](https://learn.microsoft.com/en-us/dotnet/desktop/winforms/input-keyboard/how-to-simulate-events)

Thus merely seeing the Quick Drop window?봮r even clicking what looks like the search field?봡oes not prove that its actual text/combo-box control owns keyboard focus. A stronger diagnostic is:

1. Open Quick Drop manually.
2. Physically type one character.
3. If physical typing works but SendKeys does not, cache state is not the primary failure; injection/focus/integrity is.
4. If physical typing also fails, inspect Quick Drop?셲 execution state and installation rather than extending the delay.

If using `SendInput`, the injector and LabVIEW must also have compatible integrity levels: Windows blocks injection into a higher-integrity process through UIPI, and the API does not clearly report UIPI as the reason. [Microsoft `SendInput` documentation](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-sendinput)

For deterministic construction, bypass Quick Drop. VI Scripting is expressly intended to create block-diagram objects and wires programmatically, and NI?셲 examples include ?쏡rop Add Function.vi,??which creates a primitive without driving Quick Drop?셲 UI. [NI VI Scripting overview and examples](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-Scripting/ta-p/3535340)

Likely explanations for a permanently empty list

In descending diagnostic value:

- Empty or misconfigured Functions/Controls palettes. Quick Drop obtains its objects from the palettes; NI documents that visible palette categories determine palette contents. [NI Functions reference](https://www.ni.com/docs/en-AS/bundle/labview-api-ref/page/menus/default/root-mnu.html) An NI case tied empty palettes/Quick Drop failure to an incorrect palette directory and missing palette categories. [NI forum case](https://forums.ni.com/t5/LabVIEW/empty-functions-palatte-quick-drop-issues/td-p/2917336)
- Quick Drop resource or compiled-object-cache corruption. NI forum guidance recommends patching and mass-compiling the Quick Drop resource directory when launch is abnormal. [NI forum guidance](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/New-gesture-to-create-Unbundle-By-Name-node-Ctrl-double-click/idi-p/4363369)
- An incompatible IDE extension or modified Quick Drop resource. One reported failure was caused by LVSpeak; repairing it had also damaged `QuickDropWindow.vi`. [NI forum report](https://forums.ni.com/t5/LabVIEW-APIs-Documents/Quick-Drop-Keyboard-Shortcut-Create-Object-from-Terminal/ta-p/3508433)
- The wrong palette context or all categories hidden. NI documents that LabVIEW initially uses an abridged palette and that visible categories can be changed. [NI Functions Palette documentation](https://www.ni.com/docs/pl-PL/bundle/labview-api-ref/page/environment/functions_palette.html)
- Focus or synthetic-input routing failure, especially if physical keys work.
- Integrity-level mismatch when injecting input.
- Antivirus or add-on scanning causing a temporary block?봟ut this should eventually resolve, unlike a stable empty responsive dialog.

Bottom line: enable ?쏬oad palettes during launch,??then verify that the ordinary Functions palette is populated and that one physical keystroke appears in Quick Drop. Those two tests cheaply distinguish cold-cache delay from palette corruption and synthetic-input failure. For production automation, VI Scripting is the reliable programmatic alternative; Quick Drop plus SendKeys has no documented automation contract.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
