---
type: peer-review
status: historical
date: 2026-09-05
tags: [peer-review]
---

# m3-clicker-spec-attack

- **agent:** codex
- **date:** 2026-09-05
- **outcome:** ANSWERED (102s)
- **why asked:** plan review (work cycle step 1) of docs/m3-clicker-spec.md before building tools/lvclick.py.
- **verdict:** accepted in substance: single-point offset is not a transform (zoom/scroll/DPI) -> two-object calibration + Ctrl+0; extent probing dropped (GObject.Bounds exists but the reporter does not export it yet; registry sizes + header-colour check instead); palette offsets relative to the DETECTED popup rect, not the click point; menu verbs restricted to registered (class,item,effect) triples with caller verifiers; dialog rect SIZE checked before clicking; palette placement to be replaced by scripting (keystone op) — the verb stays a fallback.

## Question

REFUTE this design; find what will break, do not confirm. Read docs/m3-clicker-spec.md (project dir). Context: LabVIEW 2026 on Windows 10 at 1920x1080 driven from Python; object positions come from VI Server (GObject.Position, top-left, diagram coordinates); mouse/keyboard via SendInput (tools/lv_gui.ps1); the goal is a click layer whose targets are computed from data plus one calibrated window offset, with vision as fallback only. Attack specifically: (1) the viewport model screen = diagram + (L+11, T+37) - when does LabVIEW break it (scrolling, zoom, DPI scaling, toolbar/menu visibility, structures/subdiagrams, panes, Position of objects inside structures, negative diagram origin)? Is there a VI Server property that gives the diagram->window origin or the visible rect (e.g. Panel.Origin, Diagram.Origin, Window.Bounds, WindowBounds, PanelBounds, Scroll Position) so the offset can be READ instead of measured? Cite the property names if they exist. (2) pixel-probing a node extent (scan until canvas colour) - failure cases (selection halo, labels, overlapping wires, themes, diagram background colour changes, terminals drawn outside the icon). Is GObject.Bounds (read-only) available over ActiveX for Nodes so probing is unnecessary? (3) header-row grab for dragging Invoke/Property nodes - which pixel rows are safe on which node classes? (4) palette geometry as fixed offsets from the right-click point - when does the Functions palette open elsewhere (near screen edges, palette pinned, recently-used categories, Quick Drop)? Is there a VI Server way to place a node without the palette (e.g. New VI Object with a style ring code, or copying from a donor VI) that would make this verb unnecessary for most nodes? (5) context-menu item offsets - do menu contents/order change with node state (broken, wired, write mode) so an offset hits a different item? (6) dialog button offsets relative to the dialog rect - DPI/theme/font changes. Give for each a concrete failure scenario and the cheapest check the verb can do to detect it before clicking. Answer with sources (NI docs/forums URLs) where claims are about VI Server properties.

## Answer

The design is unsafe as specified. Its ?쐎ne calibrated offset??is not a stable transform, and several probes can validate the wrong object or wrong UI state. The clicker needs stronger preconditions and should replace palette operations with VI Scripting wherever possible.

## 1. Viewport model

`screen = diagram + (L+11, T+37)` fails in several ordinary states:

- Diagram zoom is not represented. LabVIEW 2026 supports arbitrary block-diagram zoom through Ctrl-wheel and menu commands; ?쏷oggle Zoom??also recenters around the mouse. At non-100% zoom the mapping needs a scale factor as well as translation. [NI: block-diagram zoom](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LipSAE)
- Scrolling changes the visible diagram origin without changing `GObject.Position`. NI documents that object position remains unchanged while its owning pane scrolls. [NI: GObject.Position](https://www.ni.com/docs/ja-JP/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/position.html)
- A negative diagram origin is legitimate. Returning to `(0,0)` merely scrolls the origin into the upper-left; diagrams can have objects at negative coordinates. [NI discussion of block-diagram origin](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Adjust-Pane-Origin-for-Block-Diagram/idi-p/4038527)
- Windows DPI scaling can make VI Server logical pixels, window-query coordinates, SendInput absolute coordinates, and screenshot pixels disagree unless every process is using the same DPI-awareness mode.
- Hiding the toolbar, changing menu visibility, maximising/restoring, switching themes, or changing title-bar metrics changes the client-area inset while preserving the outer window rectangle.
- Structures introduce separate diagrams/subdiagrams. A contained object?셲 position belongs to its owner?셲 coordinate space; treating it as top-level diagram coordinates is invalid.
- Split panes or embedded editing surfaces make ?쐎ne viewport per window??false.

The proposed probe does not detect these reliably. At the wrong transform it can land on a wire, label, structure border, selection highlight, or another node and still see ?쐍ot canvas-white.??
Property answer:

- `Front Panel Window:Window Bounds` gives outer-window screen geometry. It includes title/menu/borders and therefore does not solve the inset. [NI Window Bounds instructions](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIETCA4&l=en-MY)
- `Front Panel Window:Panel Bounds` gives the interior panel rectangle in global screen coordinates, excluding title bar, menu, toolbar and scrollbars?봟ut it is specifically a front-panel property, not documented as a block-diagram client rectangle. [LabVIEW VI-property listing](https://www.labviewwiki.org/wiki/VI_class)
- `Pane.Origin` is the documented scrolling origin for front-panel panes. NI describes each pane as having its own Origin after multi-pane support was added. It is not evidence that the top-level block-diagram viewport exposes the same public property. [NI: programmatic panel scrolling](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P6wgSAC&l=en-US)
- Public properties include `Block Diagram Window:OS Window` and `Block Diagram Window:Window`; those may provide an HWND/window reference, but the published listing does not expose a public `Block Diagram Window:Origin`, `Visible Rect`, or `Panel Bounds`. [VI property listing](https://www.labviewwiki.org/wiki/VI_class)

Thus I would not claim there is a documented ActiveX-readable BD origin. The practical authoritative route is likely `Block Diagram Window:OS Window` plus Win32 client geometry, but scroll and zoom still require independent detection.

Cheapest pre-click check:

1. Require Actual Size (`Ctrl+0`), then verify at least two separated objects, not one.
2. Compare their screen displacement with their reported diagram displacement. Reject unless scale is exactly 1 and both yield the same offset.
3. Require the targets to have the same owner/top-level diagram reference.
4. Confirm the foreground HWND and client rectangle immediately before `SendInput`.

Two points detect zoom and most false offsets; one point cannot.

## 2. Pixel-probed extent

Scanning until the canvas colour is fundamentally ambiguous:

- A visible label is part of the object?셲 bounding rectangle and may start above or left of the presumed icon origin.
- Wires crossing or leaving a node prevent the scan from returning to background.
- A neighbouring or overlapping object merges colour runs.
- Selection outlines, breakpoint glyphs, coercion dots, retained-value annotations, execution highlighting and hover feedback alter the scan.
- Node terminals can protrude beyond the central icon.
- Structures have non-solid interiors, and many nodes contain pixels matching the canvas.
- Diagram background colour is configurable; anti-aliasing and theme colours make exact equality brittle.
- `GObject.Position` describes the top-left of the full visible bounding rectangle, including a visible label?봭ot necessarily the icon-body corner. [NI: GObject.Position](https://www.ni.com/docs/ja-JP/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/position.html)

Yes: `GObject.Bounds` exists, is read-only, remotely accessible, and returns width and height of the maximum bounding area. It should be available through ActiveX once the returned object reference exposes the generic GObject property. [GObject.Bounds property](https://labviewwiki.org/wiki/GObject_class/Bounds_property)

Use `Position + Bounds`; remove `node_box()` probing. But note that those describe the full visible extent, possibly including labels, so they still do not identify a draggable body/header.

Cheapest check: read `Position` and `Bounds` twice, ensure they are stable and plausible, and verify the intended grab point lies inside the bounding rectangle and not on another reported object. If the verb needs icon-only geometry, it needs class-specific scripting properties or vision?봭ot a colour run.

## 3. ?쏦eader row at y+8??
There is no universal safe row.

- Invoke and Property Nodes can have captions, class headers, one or many method/property rows, and class-dependent controls.
- A short node can make `y+8` coincide with its only chooser row.
- With a visible label, `Position.Top + 8` may be in the label rather than the node.
- Expanded subVIs, Express VIs, structures, formula/script nodes, constants and terminals do not share an Invoke/Property-node header convention.
- Zoom/DPI changes the screen row even if the diagram offset were meaningful.
- Automatic tool selection depends on cursor location, so the same physical click can select, operate or wire according to the hit region. [NI block-diagram tools overview](https://www.ni.com/en/support/documentation/supplemental/08/labview-block-diagram-explained.html)

I would register safe drag geometry by exact scripting class and presentation state, not merely ?쏧nvoke/Property.??For any unrecognised class/state, refuse.

Cheapest check: move the mouse without pressing, capture a very small patch around the candidate, and require it to match the calibrated drag-zone exemplar for that exact class/state. After mouse-down but before moving materially, verify no chooser/menu window appeared; release immediately if one did. The safer alternative is the VI Scripting `Move` method, which also supports duplication. [NI scripting changes](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-2010-Scripting-Changes/ta-p/3521934)

## 4. Fixed palette geometry

Offsets from the right-click point break when:

- The submenu would extend beyond the right or bottom monitor edge, so Windows/LabVIEW opens it leftward or upward.
- The click occurs on another monitor or near a taskbar/work-area boundary.
- The Functions palette is pinned, floating, resized, switched between category/icon/list/search views, or configured differently.
- Palette contents differ because of installed modules, user palettes, favourites, recently used items, or localisation.
- A palette item is absent or appears in another category in a different LabVIEW installation.
- The context click lands on an object rather than true canvas and opens its shortcut menu.
- Quick Drop or a modal/tool state is active.

Quick Drop is itself a separate placement workflow, so assuming a palette always opens is unsound. LabVIEW?셲 documented palette interaction only establishes that objects may be selected from the Functions palette, not stable geometry. [NI block-diagram overview](https://www.ni.com/en/support/documentation/supplemental/08/labview-block-diagram-explained.html)

Yes, VI Scripting should replace this verb for most objects:

- `New VI Object` creates an object using a class/style, then the returned reference can configure its more-specific properties.
- Invoke Nodes can be created and then assigned a class and method programmatically. [NI forum example](https://forums.ni.com/t5/LabVIEW/LabVIEW-VI-scripting-finding-out-quot-new-VI-object-quot/m-p/3932054)
- Where a style is missing or obscure, copying/moving a known donor object is the recommended practical technique. The scripting `Move` method supports duplication. [NI style discussion](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Input-for-style-in-quot-New-VI-Object-quot/function/m-p/3267356), [NI scripting changes](https://forums.ni.com/t5/LabVIEW-APIs-Documents/LabVIEW-2010-Scripting-Changes/ta-p/3521934)

Cheapest check if palette clicking remains: after right-click, detect the actual popup rectangle and direction, then validate each submenu using its visible text or image before clicking. A registry of offsets alone cannot safely detect palette flipping.

## 5. Context-menu offsets

Menu rows are state-dependent. ?쏞hange To Write??can disappear or be replaced when:

- The property is already write mode.
- A property is read-only.
- The node or VI is locked/running/reserved.
- The selected row differs from the intended row.
- The node is broken or unresolved.
- The node class changes which operations are valid.
- Multiple objects are selected.
- LabVIEW version, installed toolkit or UI language changes the menu.

The dangerous case is not merely failure: the stored `+187` can hit a different enabled command.

The default verifier, ?쏣xecState change,??is also inappropriate. Changing a Property Node row from read to write normally changes diagram configuration, not VI execution state; an unrelated execution-state transition could create a false success.

Cheapest check: after opening the menu, identify the command by text/accessible menu ID and verify it is enabled. Never click a row solely by Y offset. Before opening it, read the row?셲 current direction/property identity through its specific scripting reference; if it already satisfies the goal, return idempotent success. Afterward verify that same scripting property, not `ExecState`.

## 6. Dialog-relative button offsets

Dialog-relative offsets fail with:

- DPI scaling or moving LabVIEW between monitors with different DPI.
- Windows text scaling, localisation or substituted fonts.
- Theme changes and different common-dialog implementations.
- Dialog resizing, wrapped explanatory text or additional warning controls.
- A same-title dialog with different contents.
- Buttons reordering or changing width because translated labels are longer.

The window rect only proves that some top-level window has that title; it does not prove the button is at the registered coordinate.

Cheapest check: locate the button through UI Automation/Win32 child controls by role plus caption and require exactly one enabled match. If that is unavailable, inspect a small screenshot of the dialog and use vision every time?봡ialog clicks are too infrequent to justify blind offsets. After clicking, require disappearance of the exact HWND, not merely a changed window-title list.

## Minimum redesign

The acceptable boundary would be:

- Use `GObject.Position + GObject.Bounds`; eliminate canvas-run extent probing.
- Use scripting `Move`, `New VI Object`, specific-node properties, and donor duplication for all supported classes.
- Treat GUI interaction as a last resort for operations genuinely absent from scripting.
- Establish the viewport from two or more landmarks, require 100% zoom, same owner diagram, stable foreground HWND and stable client rect.
- Resolve menus/buttons by semantic identity, never row offsets.
- Refuse nested subdiagrams until their coordinate transform is independently demonstrated.

As written, the 8/9 acceptance threshold is especially weak: it explicitly accepts a destructive wrong click roughly 11% of the time. For a click layer controlling an editor, a verb should either establish all preconditions and verify the exact semantic mutation, or decline to click.

## Sources

(extract from answer)

## What was done with it

spec revised (docs/m3-clicker-spec.md §1-§6 'after review'), lvclick.py rewritten accordingly; residual risks recorded in §6.
