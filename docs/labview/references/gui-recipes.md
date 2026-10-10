# GUI automation recipes (LabVIEW Automation skill)

When scripting cannot reach: the three laws, probe colours, Context Help, Quick Drop, class picker, wiring clicks, resize, z-order, UI-TARS, model choice.


## GUI automation — when you must click

Use `scripts/lv_gui.ps1` (bundled). Actions: `windows focus shot shotwin crop click rclick dclick
move drag wheel hover probe wire key keys cursor md5`.

### The three laws

1. **`focus` FIRST, then re-`shotwin`, then click.** A rect check alone is NOT sufficient: `shotwin`
   uses `PrintWindow`, which reports a window's rect even when it is **completely hidden behind
   another**. A provably-in-rect coordinate can land on a different VI entirely.
2. **`screen = image + (left, top)`**; for crops, **`real = origin + crop_px / scale`**. Never read a
   coordinate for anything under ~15 px off a 1:1 screenshot — crop at 5x+ and compute.
3. **Never eyeball a terminal — `probe` it.** A block diagram is a strict colour code, so scan a line
   of pixels instead of looking at a picture.

**First principle behind all three: let LabVIEW tell you where the terminal is.** It *snaps* to a
terminal when the cursor is merely near one, and it names what it snapped to in a tip strip. So the
reliable loop is **hover → capture → read the tip strip → click**, not coordinate arithmetic aimed at
a 4 px target. A hover that names the wrong terminal is a cheap, unambiguous miss; a click that hits
the wrong terminal is an expensive, ambiguous one. A negative result is still information — a hover
that names nothing means you are outside every hot zone, so move, rather than repeating the click.

### Window furniture — fixed offsets, and reading the run arrow

Add these to a block-diagram window's `(L, T)`. Verified on LabVIEW 2026 at 1920×1080 with the
default toolbar; **re-derive them on a different version or DPI** — but do not re-derive them every
session, which has happened at least three times.

| target | offset from window origin |
|---|---|
| **Run arrow** | `(+70, +66)` |
| Run continuously | `(+92, +66)` |
| Abort | `(+118, +66)` |
| **Highlight Execution** (bulb) | `(+166, +66)` |
| `File` menu | `(+25, +41)` |
| `Edit` menu | `(+58, +41)` |
| `View` menu | `(+95, +41)` |
| `Tools` menu | `(+220, +41)` |

**The run arrow is a free state read**, worth one crop
(`crop -Left L+37 -Top T+51 -Width 130 -Height 30 -Scale 8`):

- **solid outlined arrow** → runnable
- **shattered / split arrow** → broken (a required input is unwired)
- **filled dark arrow, toolbar controls vanish** → currently running

This is also how you test whether an input is *required* without reading documentation: delete its
constant and look at the arrow.

### `probe` — find terminals by colour, deterministically

Scan a 1-px column just left of a node. Every *connected* terminal appears as its wire's colour:

| colour | datatype |
|---|---|
| `#007F7F` teal | refnum |
| `#0000FF` blue | numeric / enum / ring |
| `#993300` brown | cluster |
| `#7F7F00` olive with black | error cluster |
| `#CCFFFF` | VI Scripting node body fill |
| `#FF0000` | **required-input marker** (scan just *inside* the node edge) |
| `#FFFFCC` | `N` / `i` terminal interior |

Unconnected terminals draw nothing, so interpolate them from the connected rows and the node box.

### Identifying nodes and wires — Context Help beats pixel forensics

**Help > Show Context Help, then hover** is the deterministic identifier for anything ambiguous:
hovering a subVI node shows its qualified name and full connector map (every terminal name + which
are required); hovering a WIRE shows the wire's name and data type (e.g. "Diagram out (Diagram
Refnum)"). Two same-coloured refnum wires are indistinguishable to `probe`, but one hover each names
them. The floating window relocates away from the cursor — capture full screen and search for it.
Ten seconds of hover replaces whole sessions of wire-tracing by eye. (Verified: identified
lv-scripting's `Create For Loop.vi` and told three parallel teal wires apart on LabVIEW 2026.)

### Wiring small icon-only nodes — make the terminals visible first

An icon-only subVI node (~30 px) draws NO terminal stubs, and its terminal hot-zones are 1-3 px —
blind clicks at computed coordinates fail silently. Fix: right-click the node → **Visible Items >
Terminals** — the icon then renders its connector pane as **chunky coloured rectangles** (~8x9 px
each) that identify terminals by wire-colour AND give a big click target. Wires started/ended on a
pattern rectangle landed first try after stub-clicks had failed four times.

Two more reliable idioms:
- **Reverse-direction wiring:** when one end is tiny and the other is big (e.g. a Static VI
  Reference — its whole icon is the output terminal), START the wire at the small terminal and END
  anywhere on the big node's icon. LabVIEW snaps the landing to the only compatible terminal.
- **Create > Constant on a terminal** (right-click it) works on installed-library subVI terminals
  too, and yields a correctly-typed constant already wired — including complex types like string
  arrays. Never build such constants from the palette.

**Editing a string-array constant's elements:** double-click the element, Ctrl+A, type. **Never
press Enter to commit** — inside a string it inserts a newline that silently corrupts the value
(fatal for name-matching APIs); commit by clicking empty canvas. A narrow element renders its
content as blank/scrolled, so **verify with the hover tip strip**, which shows the full value.
Grow the array by incrementing the index display and typing into the fresh element.

### Z-order is not what `focus` says — verify the foreground title before every risky click

Bringing a window forward and then clicking can still hit a DIFFERENT window: another window can
re-raise between the focus call and the click, and several windows often share coordinates (e.g.
every block diagram parked at (0,0)). This nearly closed an original experiment VI: a File>Close
aimed at a scratch VI landed on the original's menu (the save dialog named the original — it was
READ before answering, and **Cancel** chosen; always read a save dialog's VI NAME before clicking).
Standing rules: (1) before menu/toolbar clicks, capture a thin strip of the title bar and CONFIRM
the window name; (2) never blind-click title-bar X buttons when windows overlap — use File>Close on
a title-verified window; (3) keep any original VI's window MINIMIZED while automating near it.

### More display-state truths

- **Scripted edits do NOT set the edited VI's window-title `*` dirty flag** (verified: a scripting
  run added a whole loop; the title stayed clean). Never use the asterisk to decide whether a
  scripting run changed a VI — verify by content, or better, create at a KNOWN `location` (wire the
  `location` input of Create-structure VIs) so the result is where you expect it.
- **Trust Context Help over byte-level string extraction for terminal names.** Byte extraction of
  a `.vi` got 2 of 11 terminal names wrong ("image in" vs the real `image`; "Bead 1 is good" vs
  `Bead 1 is good? out`); a name-based wiring API fails silently-ish on such mismatches. Also,
  **Get Controls-style label lookup fails with error 1055 downstream** when the label doesn't match
  exactly — and a label that RENDERS on two lines may contain a real newline; check with the
  element's right-click **'₩' Codes Display** before typing it as a name.
- **Editing array-constant elements: type the INDEX digits directly** (double-click the index
  display, type the number, Enter — numeric Enter is safe) — the tiny index increment/decrement
  arrows frequently ignore clicks. The Data Operations > Delete Element submenu works but the menu
  pops up OR down unpredictably: capture the open menu, locate the row, hover it, capture the
  submenu, then click — never click blind offsets into a context menu.

### Navigating a huge diagram under automation

Scrollbar thumb drags, track clicks, and arrow-button clicks are UNRELIABLE from synthetic input
(work sometimes, silently no-op other times); mouse wheel scrolls only vertically. What works
deterministically:
- **View > Zoom Out / Zoom In / Actual Size** (via the menu, not Ctrl+± which may not arrive) to
  fit content; LabVIEW 2026 has real diagram zoom.
- **Edit > Find and Replace → Search for: Objects → Add → VIs by Name… → pick the subVI → Find.**
  The Search Results window counts every instance per VI (an instant "how many did my script
  create" oracle) and its Go To / Ctrl+G jump the diagram view to each instance.
- A running VI is identified by its FP window title LOSING the " Front Panel" suffix; an
  execution-highlighted run of a short scripting chain completes in seconds and paints the flow.

Also: **an open Context Help window can block ALL right-click context menus** on diagrams — if
rclick menus stop appearing, close Context Help from the Help menu. And menu-item coordinates are
not stable across invocations of the same menu — capture-then-click every time; two attempts to hit
File>Close landed on Close All (dialog listing every dirty VI incl. originals → answer **Cancel**).

### The run-button trap

The broken-run-arrow button ("List Errors") and the Run button are THE SAME PIXELS. The moment the
last error is fixed, a click intended to re-open the Error list **runs the VI**. Before clicking,
zoom the arrow (solid vs shattered) — or accept the run. Conversely this makes a cheap oracle:
wire, then check the arrow crop; solid = types matched, shattered = open Error list for the exact
missing-terminal names. The Error list dialog does not auto-refresh reliably — close and reopen it.

### lv-scripting structure-context model (Erdos Miller)

`Create <Structure>.vi`'s **Diagram out is the structure's OWN inner diagram**, not the diagram it
was created on; everything chained until the matching `Exit <Structure>.vi` is created INSIDE the
structure (stated in Example 6's annotations, execution-verified on 2026). To drop a subVI inside a
created loop, feed `Create SubVI.vi`'s `Diagram in` from `Create For Loop.vi`'s Diagram out — NOT
from the VI's top-level Diagram property (that lands the subVI at top level). `Create SubVI.vi`
with `Input Names` + `Inputs` (the loop's inner-tunnel refs from Create For Loop's Inputs-out)
wires tunnels to the subVI **by terminal name**, in array order; a type mismatch draws the wire
anyway and leaves it broken, so name-matching can be smoke-tested with wrong-typed tunnels.


## Local GUI grounding with UI-TARS (optional, free)

For "where is X?" questions, **UI-TARS-1.5-7B** (Apache-2.0, Qwen2.5-VL) runs locally via Ollama on a
6 GB GPU at Q4_K_M and grounds LabVIEW terminals to within a few px — **but only with a two-stage
zoom**: a 1× pass misses 5 px targets by ~60 px; re-grounding on a 3× crop around the coarse guess
lands within 1–3 px. Two gotchas that cost real time: (1) Ollama **upscales small images** rather than
applying Qwen's `smart_resize`, so derive the scale from Ollama's image-token count
(`tokens × 28²` pixels, aspect preserved) instead of assuming; (2) community Ollama tags of this model
are **text-only** — you need a GGUF **plus** its `mmproj` projector, imported with two `FROM` lines.
Keep it as a *grounder* the planner consults, never an autonomous agent, and confirm with a pixel
probe before wiring.

**Scope limit, measured (2026-08-26 pipeline benchmark):** its reliable domain is **large,
unambiguous window chrome** — Run arrow, menus, buttons — where a plain 1× pass lands within ~4 px
in ~2 s. On diagram objects that are *semantically confusable* (a For Loop's `N` box vs a nearby
small numeric constant — both small blue squares) it grounded the wrong object **4 of 4 attempts**,
across both zoom modes and two phrasings; the zoom pass cannot fix wrong-object grounding, and on
one dead-on coarse hit the fine pass actively *degraded* it. Division of labour: grounder at 1× for
chrome, `probe` for anything a wire will touch.


## Model choice for GUI work

Benchmarked on one task at a 40-call cap: **Haiku 0/3 (failure)**, **Sonnet 2/3 (partial)**,
**Opus 3/3 in 31 calls (success)**, **Fable 3/3 at the cap**. Use the strongest available model for
GUI driving. Retrying a weak model costs more than one strong run, and a failed run has negative
value because the fallback is a human doing the work.


## Two GUI operations that have no scripting path, and exactly how to drive them

Both were needed to finish an Op VI on 2026-08-31, and both wasted calls until the precise
technique was found. **Both leave LabVIEW in a modal-ish state that blocks every subsequent COM
call** — send `Esc` afterwards, always, or the next property read hangs for the full watchdog.

### Setting a VI Server class-specifier constant

1. **Click empty canvas first to deselect.** Clicking the constant while anything is selected does
   nothing — the picker only opens from a clean selection state. This alone cost several attempts.
2. Click the constant → a dropdown appears (`Generic ▶ / Project / ProjectItem ▶ / Scene ▶ /
   Variable`).
3. **Hover, never click, to descend.** Clicking an entry that has a submenu arrow *expands* it
   rather than selecting it, and a stray `Esc` then throws the whole chain away.
4. **The first item of each submenu is the parent class itself.** `Generic ▶` opens with `Generic`,
   `GObject ▶` with `GObject`, and so on — that entry is what you click to select.
5. Useful paths: **Diagram** = `Generic ▶ GObject ▶ AbstractDiagram ▶ Diagram ▶ Diagram`;
   terminals live under `GObject ▶ Terminal ▶`; loop tunnels under `GObject ▶ Tunnel ▶`.

### Wiring a control terminal to a subVI input by hand

Click the source terminal, then click the destination — a press-drag-release also starts the wire
but is no more reliable. What actually matters is **where the second click lands: the node's LEFT
EDGE, on the terminal's own row — not the middle of the icon.** The "drop anywhere on the icon and
LabVIEW snaps to the only compatible terminal" idiom did **not** work here; three attempts aimed at
the icon body failed silently, and the first attempt at the left edge succeeded.

Estimate terminal rows from the node's height: inputs are stacked top-to-bottom in connector-pane
order down the left edge (for a 32 px node, roughly 4 px, 12 px, 28 px from the top for a
three-input VI). Verify by the object count afterwards — `Wire` +1 and `ExecState` going to 1 is
the proof, not the screenshot.



## focus taps Alt — ALWAYS send Esc after focus, before any keys (2026-09-01)

`lv_gui.ps1 -Action focus` taps the Alt key to defeat Windows' foreground lock. In LabVIEW an
Alt tap with no companion key puts the MENU BAR into keyboard-navigation mode. Symptoms, all
observed in one session: the next Ctrl-combo is eaten as a menu mnemonic (`^e` opens the Edit
menu, `^f` opens the File menu, `^s` does nothing), text typed into Quick Drop never appears,
menus highlight on click but do not drop down, and **COM blocks entirely** (the active menu loop
holds LabVIEW's UI thread; every VI-server call times out). The state also survives most clicks.

**Recipe: `focus` → `key esc` → then `keys`/clicks.** Esc leaves menu mode instantly — it is
also the approved unblock when COM starts timing out with no modal dialog visible.

## Placing primitives when Quick Drop is broken — the right-click palette works

Quick Drop in this install shows a permanently empty list and ignores input (peer-reviewed:
abnormal palette/QD state, not a cache warm-up; archive/peer/2026-09-01-quickdrop-empty-cache-
sendkeys.md). The right-click **Functions palette is fully populated** and places primitives
fine: rclick empty canvas → click a category icon TWICE (first click only selects it; second
opens the flyout) → click the function → click the canvas spot. Verify by uid-diff via the
reporter, never by eye. Placement clicks land in the visible viewport; convert screen→diagram
coords with an anchor node jumped to via Ctrl+F (below).

## Ctrl+F ▸ Objects ▸ VIs by Name — jump-to-node as a coordinate anchor

Find (objects mode) → Select Object ▸ `VIs by Name...` → pick from the in-memory list → OK →
Find: LabVIEW scrolls to AND selects the instance. Uncheck "Ignore VIs in vi.lib" first for
vi.lib/LVAddons nodes. Type-ahead in the list breaks at spaces — type a unique prefix, then
`{DOWN}` to the exact row. The selected node's known diagram position + its screen position give
the screen→diagram offset for palette placements and hover targets.

## Verified-impossible entry 3 (2026-09-06): branching an existing wire by the fleet

erdosmiller `Wire Inputs.vi` cannot branch from an already-wired source: it attaches a second
source and breaks the diagram ("more than one data source"; 3/3 on OpBuildInvoke_v0, capture in
the session log; same failure recorded for Wire Indicators 08-29). The native `Diagram.Connect
Wire` op does not exist in the fleet and cannot be built without a branch. **User exception
(2026-09-06 "예외 허용. 마저 진행"): one GUI branch-wire session per op build** — lvclick/lv_gui
`wire` from the new node's input terminal (position from COM + hover-verified tip strip) to the
existing wire, verified by ExecState / bad-wire count. Every such act is logged in gui_actions.log
with Evidence "keystone bootstrap (user: 예외 허용 2026-09-06)". Retire this entry when a Connect
Wire op exists.

**Exception extension (user, 2026-09-06 "1~3번 스텝 논스톱으로 진행해보자"):** during the keystone
bootstrap (steps 1-3: Invoke-op cleanup, Property-op twin, tool replacement) GUI node deletion
(click node → Delete → Ctrl+B) and terminal context-menu `Create > Control` are allowed once per
op build, each act logged with Evidence "keystone step N ... (user: 1~3 논스톱 2026-09-06)".
Scripted alternatives are known-broken: delete_by_label/copy_into rely on the substitution
protocol whose gui_save is a no-op for scripted edits (spec §13). Retire when OpDelete/OpCreateControl
keystone ops exist.

**Correction to entry 3 (2026-09-06 17:5x):** erdosmiller `Wire Inputs.vi` CAN branch from an
already-wired source when the destination's type accepts the wire — OpDelete_v0's `reference` was
branched from an Index Array `element` wire that already fed To More Specific Class (count stayed
8, node re-typed to GObj, ExecState 1, delete verified). The 3/3 "branch breaks the diagram" cases
of the morning were all TYPE mismatches (Generic → Diagram-typed input; VI ref → GObject input).
Rule now: branch by script first (`wire(..., branch=True)`), read the Error List if ExecState
drops, and use the GUI branch only for a click-only target. Entry 3 narrows to "type-incompatible
targets cannot be fixed by wiring at all".

## "The click did nothing" is usually a bad PROGRESS TEST, not a lost click (2026-09-17, MEASURED)

A click tool reports success when **its own function returns** — `mouse_event` has no return value — so
`click x,y` is never evidence that a control received anything. Two things follow, and the second is the one that
actually cost this project a cycle.

**1. Build the reader before the theory.** `lv_gui.ps1 -Action clickprobe -Title <substr> -X n -Y n` performs the
*same* click as `-Action click` and returns one JSON line with `SetForegroundWindow`'s return + last error,
`GetForegroundWindow` before / after the activation / at button-down, `WindowFromPoint` at the click point **and at
the real press point (x+1, y — `Click()` jiggles before pressing)** with its `GA_ROOT`, `GUITHREADINFO`
(`hwndActive/hwndFocus/hwndCapture/hwndMenuOwner/flags`) before and after, and the target's `IsWindow`/title/rect
500 ms later. It is state-changing, so it passes the same `-Exception`/`-Evidence` gate as `click` and is logged.

**2. A LabVIEW subVI panel is DESTROYED and RECREATED, reusing the same window title.** Measured on
`choose bandpass v2.vi`: one click killed hwnd `19728546` **within 500 ms**, and hwnd `19794082` with the byte-
identical title took its place. A harness whose progress test is *"is a window with this title still present?"*
reads that successful click as a lost one — twice, in our case, costing a peer review and a rebuild.
**The token is the HWND, never the title.** Gate a click on the clicked hwnd dying (`after_500ms.alive == false`),
and never retry on a title match: the successor panel sits at the same rect with the same button coordinate, so a
"retry" can answer the *next* item instead of re-answering this one.
