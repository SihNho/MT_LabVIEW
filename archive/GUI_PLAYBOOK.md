---
type: narrative
status: historical
date: 2026-08-27
tags: [archive, gui]
---

# GUI Playbook — how to hit a LabVIEW target without ten tries

**Purpose:** every time a GUI target is finally found after misclicks, the reusable part gets written
here so the next session doesn't pay the same cost. This file is meant to make GUI control
**compound**. If you burn round-trips locating something, add it here before moving on.

Companion files: `tools/lv_gui.ps1` (the actions themselves + technique notes in its header),
`LEARNING.md` §3 (why GUI control is the fallback, not the standard).

---

## 0. FIRST PRINCIPLE — let LabVIEW tell you where the terminal is

> **VERIFIED 2026-08-26.** Hovering at screen `(630, 258)` over `New VI Object`'s left edge produced
> a tip strip reading **`style`** — LabVIEW named the terminal under the cursor, unprompted. The node
> simultaneously rendered small **coloured dots/diamonds on each terminal** (teal, orange, green),
> which are the snap targets and are far easier to see than the terminals themselves. This is not a
> theory; it is the cheapest reliable way to confirm a target before clicking.

**Do not compute a terminal's position and click blind. Hover near it and read LabVIEW's own
feedback.** This supersedes most of §3 below, which is now the *fallback* for when feedback is
ambiguous.

With Automatic Tool Selection on (the default), moving the cursor **near** a terminal makes LabVIEW:

- switch the cursor to the **wiring spool**,
- **highlight** the terminal it intends to connect, and
- show a **tip strip naming that terminal**.

That snap behaviour is why humans can wire a dense diagram without micro-precision — they get close
and let the application confirm the target before committing. Automation should do the same.

### The loop: hover → capture → verify → click

1. `move` **twice**: first to a nearby point, then to the target. A single teleporting `SetCursorPos`
   often does not make LabVIEW register hover state. Then wait **>= 2 s** before capturing — this
   two-step-plus-wait is what makes the tip strip appear, and skipping it is why a benchmark run
   concluded (wrongly) that the technique "didn't pan out".
2. `shot` (full-screen — tip strips are separate windows and `shotwin` misses them), then `crop`
   around the cursor at `-Scale 4`+. **Note: the mouse cursor glyph itself is NOT captured** (GDI
   `CopyFromScreen` does not composite it), so do not look for the pointer — look for the tip strip
   and the terminal dots, which *are* captured.
3. **Read what LabVIEW is telling you**: the tip strip text, which terminal is highlighted, and the
   **Context Help** window, which names the terminal under the cursor. Keep Context Help open
   (`Ctrl+H`, or `Help ▸ Show Context Help`) during any terminal work — it is a free oracle.
4. Click **only** once the feedback names the terminal you actually want. Otherwise nudge a few
   pixels and re-check.

### A negative signal is still information

Context Help reading **"No description available"** means *the cursor is not on a terminal*. That is a
correct, useful answer — treat it as "nudge and retry", not as a broken tool. Likewise a right-click
that produces **no menu at all** means you missed the node entirely.

### Wiring is click-click, NOT drag

To draw a wire: **click the source terminal, then click the destination terminal.** LabVIEW routes it
automatically. Do *not* press-glide-release — `drag` is the right primitive for **rubber-band
selection only**, not for making wires. Verify each end with the hover loop before clicking it, and
the snap radius absorbs the remaining error.

### Where snap does and doesn't help

Snap assists the **wiring tool**. A **right-click** to open a terminal's context menu has much less
tolerance — that is where the §3 arithmetic still earns its keep (aim 5 px *inside* the node's left
edge).

## 1. The coordinate law — never eyeball a click target

Two conversions, always applied in this order. Getting these wrong is the single biggest source of
wasted round-trips.

**a) Window-relative → screen.** `shotwin` prints the window rect as **`left, top, right, bottom`** —
NOT width/height. (It now prints those names explicitly; older notes claiming `L,T,W,H` were wrong and
cost a benchmark run several calls. Width = right - left.) A `shotwin` image's pixel `(ix, iy)` is at
screen:

```
screen_x = L + ix
screen_y = T + iy
```

**b) Crop → real.** `crop -Left ox -Top oy -Scale s` produces an image where pixel `(cx, cy)` maps
back to the *source image* as:

```
real_x = ox + cx / s
real_y = oy + cy / s
```

**Rule: never read a coordinate off a 1:1 screenshot for anything smaller than ~15 px.** Crop at
`-Scale 5` or higher and compute. Eyeballing is reliably 2-5 px off, which is more than the height of
a node terminal.

## 2. Block diagram window furniture — fixed offsets from the window origin

Verified 2026-08-26 on LabVIEW 2026 at 1920x1080, default toolbar. Add these to the window's `(L, T)`:

| target | offset from window origin |
|---|---|
| **Run arrow** | `(+70, +66)` |
| Run-continuously | `(+92, +66)` |
| Abort (stop) | `(+118, +66)` |
| **Highlight Execution** (bulb) | `(+166, +66)` |
| `File` menu | `(+25, +41)` |
| **`Edit` menu** | `(+58, +41)` |
| `View` menu | `(+95, +41)` |
| `Tools` menu | `(+220, +41)` |

So on a window at `23,41`, the run arrow is at screen `(93, 107)`. This has been re-derived at least
three times — use the table.

**Reading the run arrow tells you the VI's state, and it is worth one crop:**
`crop -Left L+37 -Top T+51 -Width 130 -Height 30 -Scale 8`

- **solid outlined arrow** → runnable
- **shattered / split arrow** → VI is broken (a required input is unwired)
- **filled dark arrow + toolbar controls vanish** → currently running

That distinction is how you prove an input is required without reading any documentation: delete its
constant and look at the arrow.

## 2a. QUICK DROP — place a node by NAME (WORKS FOR PRIMITIVES; UNRELIABLE FOR LIBRARY VIs)

> **Honest status (corrected 2026-08-26).** Quick Drop placed the **built-in primitive**
> `Open VI Reference` first try. It then **failed three times in a row** to place
> **`Create SubVI.vi`**, a member of an installed *library* (`LV-Scripting.lvlib`) - the Quick Drop
> window opened and listed the VI correctly, Enter was pressed, a click followed, and **no node
> appeared** (the VI was verified unmodified afterwards, so nothing was silently broken).
> Retried with the whole sequence in one command, at three different canvas positions. Still nothing.
>
> **Leading hypothesis:** Quick Drop places palette *primitives* reliably, but placing a **library
> `.vi`** may need something extra (the library present in the palette, or a different gesture).
> **Do not assume Quick Drop works for library VIs.** For those, prefer **copy-paste of an existing
> node from a working diagram** — e.g. `Create SubVI.vi` is already wired in NI/lv-scripting's
> `Example 5 - SubVIs.vi`, so `Ctrl+C` there and `Ctrl+V` into the target is likely cheaper and
> is known to work for LabVIEW nodes.
>
> One success is not verification. This was written up as "VERIFIED" after a single trial and that
> was wrong — the same mistake made earlier with the `wire` primitive.
>
> **RESOLVED — use the library's own palette for library VIs.** `Create SubVI.vi` placed **first try**
> via right-click canvas -> `Erdos Miller` (2 clicks, it is a category) -> `LV-Scripting` (2 clicks)
> -> `Create SubVI` (1 click, leaf) -> click canvas. An installed VIPM library registers its own
> palette entry at the bottom of the Functions palette, and that is the intended, reliable route.
> Quick Drop remains the fast path for **primitives** only.

For a built-in primitive it costs ~4 calls versus 7-9 for palette navigation.

```
1. click empty canvas            (focus the diagram)
2. keys "^ "                     (Ctrl+Space -> Quick Drop opens; it is its own top-level window)
3. keys "Open VI Reference"      (type the node name; the search field already has focus)
4. key enter                     (selects the highlighted match)
5. click <where you want it>     <-- REQUIRED. Enter alone places NOTHING.
```

**Step 5 is the trap.** On the first attempt Enter was pressed without a following click and *no node
appeared anywhere* - easy to misread as "Quick Drop doesn't work". The object is armed on the cursor
after Enter and only lands when you click.

Verify with a `crop` at the click point: a freshly dropped node shows its terminals as small coloured
diamonds.

Quick Drop matches loosely and lists alternatives (typing `Open VI Reference` also offers
`Open VI Object Reference` and `Create Open VI Reference.vi`), so **check the highlighted first entry
in a capture before pressing Enter** if the name is ambiguous.

## 2b. Windows that open OFF-SCREEN — use `movewin`

LabVIEW repeatedly opened block-diagram windows partly or wholly off-screen (observed twice at
`top=915` on a 1080-tall display). A title-bar double-click to maximise is **unreliable** - it worked
once and silently failed twice.

```
& .\tools\lv_gui.ps1 -Action movewin -Title "<window>" -X 0 -Y 0 -Width 1900 -Height 1030
```

Deterministic, and it prints the resulting rect plus the coordinate conversion. Do this before any
click work on a newly opened diagram, rather than discovering half your targets are below the screen.

## 3. Node terminal rows — manual fallback (prefer §3a `probe`, then §0 hover-verify)

Node input terminals sit on the node's left edge and are only ~4 px apart at 100% zoom. Use this to
get *close*, then confirm with §0's hover loop before clicking. Do **not** guess:

1. `shotwin` the diagram, then `crop` the node at `-Scale 5`+.
2. Find the node's box edges in crop pixels; convert to real with the crop law above.
3. Terminals sit at roughly these fractions of the node's height, top to bottom, and the **wires
   already attached are the giveaway** — an attached wire marks its row exactly. Locate the known
   rows from their wires, then interpolate the unknown one between them.

Worked example — `New VI Object`, node box screen `(625, 245)`-`(657, 278)`, height ~33 px:

| terminal | fraction | screen y |
|---|---|---|
| `owner refnum` | ~0.33 | 250 (teal wire visible here) |
| `style` | ~0.50 | **258-259** |
| `position` | ~0.62 | 267 (brown cluster wire visible here) |
| `error in` | ~0.85 | 274 (error wire visible here) |

**Right-click 3-5 px INSIDE the node's left edge, not on it.** `x = left_edge + 5` worked;
`x = left_edge + 2` silently produced no menu at all. A right-click that produces no menu means you
missed — re-aim inward, don't retry the same point.

## 3a. BEST METHOD — find terminals by colour with `probe` (no eyeballing at all)

**VERIFIED 2026-08-26.** This replaces cropping-and-squinting entirely. One call, deterministic
output, no image interpretation.

Scan a 1-pixel column just **left of** a node's left edge. Every *connected* terminal shows up as its
wire's colour; the gaps are background. Example on `New VI Object` (node left edge at screen x=625):

```
& .	ools\lv_gui.ps1 -Action probe -X 622 -Y 240 -Y2 285
```
```
  240-249  (10px)  #FFFFFF
  250-250  (1px)   #007F7F   <- owner refnum   (teal = refnum wire)
  251-257  (7px)   #FFFFFF
  258-258  (1px)   #0000FF   <- style          (blue = numeric/ring wire)
  259-264  (6px)   #FFFFFF
  265-267  (3px)   #993300   <- position       (brown = cluster wire)
  268-272  (5px)   #FFFFFF
  273-275  (3px)   #7F7F00   <- error in       (olive = error cluster)
```

Those y values match a painstaking manual derivation **exactly**, at a cost of one call instead of a
dozen. Scan a column just *inside* the edge (x = left_edge + 2) to see the node body and its markers:

```
  247-256  #CCFFFF   node body (VI Scripting nodes are pale cyan)
  257-258  #FF0000   <- RED REQUIRED-INPUT MARKER, on the `style` row
  259-276  #CCFFFF
```

### Wire colour → datatype (verified unless noted)

| colour | meaning |
|---|---|
| `#007F7F` teal | **refnum** (VI / Diagram / GObject reference) |
| `#0000FF` blue | **numeric**, enum or ring |
| `#993300` brown | **cluster** (drawn ~3 px thick, often with a lighter centre) |
| `#7F7F00` olive (with black) | **error cluster** |
| magenta / pink | **string** *(seen, exact hex not yet captured)* |
| `#CCFFFF` | VI Scripting **node body** fill |
| `#FF0000` | **required-input marker** on a node's input row |

### Method

1. `shotwin` the target window — it prints `left=.. top=..` and the exact conversion.
2. Locate the node's left edge roughly (one crop is fine, or reuse a known position).
3. `probe -X <edge-2> -Y <above> -Y2 <below>` — read the terminal rows straight off.
4. Optionally `probe -X <edge+2> ...` to see which rows carry the red required marker.
5. Click or wire using those exact y values.

**Unconnected terminals are invisible to this scan** (nothing is drawn there), so use the connected
rows plus the node's box to interpolate, or probe inside the edge for the markers.

## 3b. Wiring — VERIFIED end-to-end, 2 calls total

**Verified 2026-08-26** on `Untitled 9`: a numeric constant wired to a For Loop's `N` terminal,
producing a **solid (unbroken) blue wire**. LabVIEW routes the elbow itself.

```
# 1. find both endpoints exactly - no eyeballing
& .\tools\lv_gui.ps1 -Action probe -X 605 -Y 332 -X2 640      # row through the constant
  615-616  #0000FF   <- constant's LEFT border
  627-628  #0000FF   <- constant's RIGHT border = its OUTPUT terminal

& .\tools\lv_gui.ps1 -Action probe -X 890 -Y 307 -X2 925      # row through the N terminal
  900-901  #0000FF   <- N box left border
  902-913  #FFFFCC   <- N box interior (pale yellow)
  914-915  #0000FF   <- N box right border      => centre x = 908

# 2. draw it - click source, then click destination
& .\tools\lv_gui.ps1 -Action wire -X 628 -Y 332 -X2 908 -Y2 307
```

**Two calls.** The same operation done by cropping and eyeballing consumed an entire 40-call benchmark
budget and still failed. This is the whole argument for building composite actions.

### Rules

- **Wiring is click-source-then-click-destination.** Never a drag.
- **`wire` can leave the wire dangling in rubber-band mode, silently.** Seen twice in one benchmark
  run: `wire` returned normally, `probe` read all white, and yet LabVIEW was holding a **pending
  rubber-band wire** the whole time. Recovery: a single plain `click` at the destination terminal
  commits it instantly. **The tell:** a *dashed line already present before you click* is a
  wire-in-progress, not a broken wire — do not "fix" it by starting over.
  (`wire`'s timings were hardened afterwards: it now approaches each terminal before clicking and
  skips the +1px jiggle that could nudge off a small terminal. Verify with `probe` regardless.)
- **There are TWO silent `wire` failure modes — tell them apart before recovering, because the wrong
  recovery makes things worse:**

  | symptom after `wire` | what happened | recovery |
  |---|---|---|
  | probe all white, and a **dashed line is visible** | wire started, still in rubber-band mode | a single plain `click` on the destination terminal commits it |
  | probe all white, and a screenshot shows an object **selected (marching ants)** | the wire **never started** — both clicks resolved to the positioning tool | **re-aim the SOURCE** 2-3 px outside the border. Do *not* click the destination: that just selects the destination object. |

- **A freshly placed object stays selected / in edit mode.** Click once on empty canvas to commit and
  deselect before probing, or the selection handles distort what `probe` reads.
- **Start the wire 2-3 px OUTSIDE the constant's right border, never ON it.** A click landing exactly
  on the border pixels resolves to the **positioning tool** (it selects/moves the object) instead of
  the wiring spool, and the whole `wire` call then does nothing wire-related. Probe the row to find
  the right-hand `#0000FF` border run, then aim ~3 px further right, in the snap zone.
  (An earlier version of this example aimed straight at the border and happened to work once — do not
  rely on that.)
- **A structure's `N`/`i` terminal is a small box with a `#FFFFCC` interior.** Probe a row through it
  and click the centre of the interior.
- **Check the result colour.** Solid = connected. Dashed with a red X = LabVIEW rejected it; that is a
  *dataflow* verdict, not a misclick — re-check whether the connection is even legal (see §7) before
  retrying.

## 4. Recorded menu paths (expensive to discover, cheap to follow)

- **Set a VI Server Class constant** (the `vi object class` input of `New VI Object`):
  right-click the constant → `Select VI Server Class ▸`, then:
  - **For Loop** → `Generic ▸ GObject ▸ Node ▸ Structure ▸ Loop ▸ ForLoop`
  - While Loop → `... ▸ Structure ▸ Loop ▸ WhileLoop`
  - Case Structure → `... ▸ Structure ▸ MultiFrameStructure ▸ ...`
  - **SubVI** → `Generic ▸ GObject ▸ Node ▸ SubVI` *(needed for dropping the tracking kernel)*
  Submenus open on **hover**; move onto the parent item, wait ~2 s, then `shot` (full-screen — a
  window capture cannot see menus).

- **Make a correctly-typed constant for a terminal:** right-click the terminal → `Create ▸ Constant`.
  LabVIEW generates one that already matches the terminal's type, so you only set the *value*. This
  sidesteps an entire class of type-mismatch errors and is almost always better than hand-picking a
  constant from the palette.

- **Undo:** `Edit` menu → `Undo <action>` (top item, at window offset ~`(+98, +63)`).
  Do **not** rely on `Ctrl+Z` — see below.

## 5. Reliability rules

- **Menus beat keyboard shortcuts.** Programmatically sent `Ctrl+R`, `Ctrl+Z`, `Ctrl+S` frequently
  never reach LabVIEW, and the failure is *silent* — the next screenshot just looks unchanged.
  Clicking a real menu item or toolbar button is dependable. When a shortcut appears to do nothing,
  suspect the shortcut before suspecting your logic.
- **A click right after `focus` often only activates the window.** Click once on empty canvas, wait
  ~600 ms, then click the real target.
- **`shot` (full screen) for anything involving a menu**; popup menus are separate top-level windows
  and are invisible to `shotwin`'s `PrintWindow` capture.
- **Ring/enum dropdowns: use `wheel`, not type-ahead.** Type-ahead in LabVIEW's long style ring
  scrolls somewhere near the prefix but does not reliably land on the item. `wheel -Notches -8`
  moves ~8 items; screenshot and click the item directly.
- **Structure borders do not hit-test** on a dense diagram — a whole session was lost proving this.
  Build in empty canvas, or create structures via VI Scripting instead.
- **Error dialogs are titled after the VI's name**, not "Error". A run that appears to do nothing may
  have a modal dialog open under an innocuous title. Check `windows` output for an unexpected entry.

## 6. Wanted next (not yet built)

- A `probe` action in `lv_gui.ps1` that samples pixel colours down a vertical line and prints the
  runs, so node terminal rows can be located **programmatically** instead of by cropping and eye.
  Now even more attractive than when first written: with the wiring tool active LabVIEW paints each
  terminal as a **distinctly coloured dot**, so a colour scan down the node's left edge would find
  every terminal row exactly, with no visual interpretation at all.
- A `hover -X n -Y n` convenience that hovers, waits, captures full-screen and auto-crops around the
  cursor — the §0 loop is 3 calls today and should be 1.
- A `rect -Title X` action, so a window's origin can be fetched without taking a screenshot first.

## 7. Palette and dataflow notes (from the 2026-08-26 benchmark)

- **A palette CATEGORY needs TWO clicks; a LEAF ITEM needs ONE.** Two clicks on a leaf (`For Loop`,
  `Numeric Constant`) would drop a stray second object.
- **Palette geometry does not follow the click point.** Moving a right-click by (-50, +150) shifted the
  palette -50 px in x but **0 px in y**. Never extrapolate palette coordinates from a previous open —
  re-crop it each time.
- **A Functions-palette category needs TWO clicks at the same coordinate.** The first click only
  highlights/hover-selects the category (`Structures`, `Numeric`, ...); the second actually descends
  into it. Budget two clicks per palette level. Discovered the expensive way, twice in one run.
- **The first right-click on empty canvas sometimes silently opens nothing.** Capture to confirm the
  palette actually appeared before aiming at it, rather than clicking into a palette that isn't there.
- **Dataflow makes some wires illegal, and LabVIEW shows this as a dashed wire with a red X.**
  A broken wire is not necessarily a misclick — check whether the connection is even legal before
  retrying it. In particular a value produced **inside** a For Loop can never feed **that same loop's
  `N` terminal**, because `N` must be resolved before the loop begins executing. The count wired to
  `N` must come from outside the loop.

## 8. Opening the Functions palette — and the single best diagnostic in this file

A whole 40-call benchmark run (Haiku 4.5) was lost here without placing a single object, so this
section exists to make sure it never happens again.

### FIRST: `focus` the window. A correct rect is NOT enough.

**The rect check alone is insufficient, and this caused a rule-adjacent near-miss.** `shotwin` uses
`PrintWindow`, which happily captures and reports the rect of a window that is **completely hidden
behind another**. So a coordinate can be provably inside the target's rect and still land on whatever
is on top of it — in one benchmark run, a click aimed at a scratch VI landed on a *different VI
entirely* and opened its label context menu.

**Always: `focus -Title ...` -> re-`shotwin` -> then click.** Never click on the strength of a rect
you fetched before focusing. And note the palette diagnostic below will NOT catch this case: an
occluded-window misclick gives you neither palette, but some stranger's context menu.

### If you get the CONTROLS palette, you are on the FRONT PANEL

This is the diagnostic. LabVIEW shows:

- **Functions palette** — only on a **Block Diagram**
- **Controls palette** — only on a **Front Panel**

So "I right-clicked and got the Controls palette" does not mean the palette is being awkward. It means
**you clicked the wrong window.** Stop clicking and re-check which window your coordinate actually
falls in. Every VI has *two* windows with near-identical titles (`Untitled 10 Front Panel` and
`Untitled 10 Block Diagram`), they overlap on screen, and a `-Title` substring match can focus one
while your coordinates land on the other.

### Reliable procedure

1. `shotwin -Title "<name> Block Diagram" -Out <png>` — this both confirms the window exists **and**
   prints its rect self-describingly.
2. Check your intended click is inside that rect: `left <= x < right` and `top <= y < bottom`.
3. Click once on empty canvas inside it (a click after `focus` often only activates the window),
   wait ~600 ms, then `rclick`.
4. `shot` (FULL screen — a window capture cannot see a palette) and confirm the palette appeared and
   that it says **Functions**, not Controls.

Menu fallback if right-click keeps failing: **`View ▸ Functions Palette`** on the block diagram
window. Menus are more reliable than sent shortcuts (§5).

### Budget the palette honestly

Placing one object costs roughly: rclick + confirm capture + 2 clicks per palette level (§7) +
place/drag + verify ≈ **7-9 calls**. Two objects plus a verified wire is therefore ~20 calls before
anything goes wrong. Front-load the `probe` calls for both wire endpoints *before* spending clicks —
Sonnet's run 3 ran out of budget precisely because it left verification until last and then skipped it.

## 9. Object geometry cheat-sheet (verified)

- **For Loop's `N` box sits at exactly `(left_edge, top_edge)`** of the structure — the very corner.
- **A constant's output stub is at the vertical CENTRE of its right border.** Probe the *column*
  through the constant to find that centre, not just a row — aiming near the corner misses.
- `N`/`i` terminal boxes have a **`#FFFFCC`** interior; click the interior's centre.

## 11. Nodes with TOP-edge terminals — probe the top row, not the left

Some nodes carry terminals on their **top** edge as well as the left (e.g. lv-scripting's
`Create SubVI.vi`: `VI Reference` and `location` are both on top). A left-edge column probe will
never find them, and wiring to the wrong top stub gives *"You have connected two terminals of
different types"* rather than an obvious miss.

Probe a **row** 1-2 px above the node's top edge; each top terminal shows as its wire colour
(`#007F7F` refnum, `#993300` cluster). Then hover the specific stub to confirm by tip strip.
Context Help's connector diagram shows which terminals are top vs left — read it first.

**When a wire misbehaves, click the broken run arrow.** The Error List names the exact terminal and
the exact problem (`required input 'VI Reference' is not wired`, `connected two terminals of
different types`). It is far cheaper than screenshot forensics.

## 9. Selection, clicks and menus — traps found during Op-VI surgery (2026-08-27)

These cost real time while cutting `KernelBuilder_v1.vi` down into single-purpose Op VIs. All of them
produce *plausible-looking* screenshots, which is what makes them expensive.

**Clicking a small boolean constant TOGGLES it.** The operate tool is active over a boolean, so a
click meant to select it silently flips `True`↔`False` instead — and the diagram still looks right.
Select booleans with a **rubber-band drag started on empty canvas**, never by clicking them.

**A drag issued immediately after focusing a window is eaten by the activation click.** Click once on
empty canvas first, then drag. Otherwise the rubber band never starts and nothing is selected — which
looks identical to a rubber band that selected nothing.

**Error wires pass *through* node bodies.** A click in the middle of a node may select the node (what
you wanted) or the wire crossing it (what you did not). Zoom in and verify what is selected before
pressing Delete.

**Freshly placed objects stay selected** — click empty canvas to commit before probing or deleting.

**A property node's header row packs two outputs about 4 px apart** — `refnum out` at y≈564 and
`error out` at y≈570–574 in one measured case. Hover for the tip strip before wiring; the colours are
no help because both are refnum-ish.

**Reverse "end-on-icon" wiring can land on an INPUT.** Finishing a wire by clicking anywhere on a
node's icon is a big, forgiving target, but LabVIEW may resolve it to the nearest terminal, which can
be an input such as the type specifier. Hover-verify the **source** stub, then wire forward.

**Floating LabVIEW tool windows eat context menus.** An open **Context Help** or **Search Results**
window can block right-click menus from appearing at all. If right-clicks stop working, close those
windows from the Help / View menus first — this is not a click-accuracy problem.

**Menu row coordinates are unstable between invocations.** Aiming at `File > Close` hit `Close All`
twice because the rows had shifted by ~27 px since the previous capture. **Always capture the open
menu and click measured coordinates**, every time. On any Close-All save dialog listing an original
VI, choose **Cancel**.

**`Edit > Make Current Values Default` is how COM-set values persist.** `SetControlValue` over
ActiveX is runtime-only: the values are correct while the VI is in memory and silently revert once it
unloads. Set values → Make Current Values Default → Save.

**Diagram navigation that actually works:** scrollbar clicks/drags and the wheel are unreliable on
some windows. **View > Zoom Out/In** (menu) works, and **Edit > Find and Replace → Search for Objects
→ Add → VIs by Name → Find** opens a Search Results window that both *counts* instances and jumps to
them (Ctrl+G) — the instance-counting oracle when verifying what a scripted build actually created.
