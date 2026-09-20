# Driving LabVIEW over ActiveX/COM (LabVIEW Automation skill)

Watchdogs, marshalling, silent failures, error 2, save discipline, branch counting.


## Drive LabVIEW from outside via ActiveX/COM — kills the run/verify GUI loop

With **Tools > Options > VI Server**: TCP/IP ✓ (note the PORT — this rig used **3364**, not the
3363 default) and ActiveX ✓, an external Python script can set a VI's front-panel controls, run it
synchronously, and read values back — no window focus, no Run-button clicks, no completion polling,
no screenshots. Verified working (LabVIEW 2026, pywin32):

```python
from win32com.client import dynamic   # MUST be dynamic — see below
import pythoncom
lv = dynamic.Dispatch("LabVIEW.Application")            # attaches to the RUNNING instance
vi = lv.GetVIReference(r"C:\...\Driver.vi", "", False, 0)
vi.SetControlValue("Number of Static Parallel Instances", 4)   # by FP LABEL
print(vi.GetControlValue("Inputs Indexing?"))                  # tuples for arrays
ole = vi._oleobj_; dispid = ole.GetIDsOfNames(0, "Run")
ole.Invoke(dispid, 0, pythoncom.DISPATCH_METHOD, 0)            # synchronous run (blocks)
```

Traps that cost real time: (1) plain `Dispatch`/`EnsureDispatch` load the typed "LabVIEW 8.0 Type
Library" wrapper whose Application interface LACKS `GetVIReference` — and once gencache is
populated even plain `Dispatch` returns it; always `dynamic.Dispatch`. (2) `vi.Run` resolves as a
None-valued property under dynamic dispatch — invoke by DISPID with `DISPATCH_METHOD`. (3)
PowerShell's COM binder fails on the same interfaces (empty `Version`, null refs) — use Python.
(4) A COM `Run` also SIDESTEPPED an intermittent multi-minute idle hang that plagued GUI-initiated
runs of the same VI. (5) `LabVIEWCLI.exe -OperationName RunVI` connects (with `-PortNumber`) but
failed with error 1031 on a driver whose connector pane is wired — the COM route has no such
constraint.

This pairs with the design rule: **driver-VI inputs belong on the front panel as controls** (user
directive) — `SetControlValue` addresses controls by label, so config lives one script call away
instead of behind diagram surgery. A reusable CLI wrapper lives at `tools/kb_com.py` in the V6
project (portable pattern; copy and adapt).

Migrating existing diagram constants: right-click the constant → **Change to Control** (for an
ARRAY constant, right-click its INDEX box to get the array-level menu). A constant that was born
via a terminal's Create > Constant inherits the terminal's name as the new control's label — so
the COM-visible names come out meaningful ("Control Names", "vi path", …) rather than "String 2".
One more menu-blocker besides Context Help: a floating **Search Results** window also swallows
right-clicks — close such tool windows before context-menu work. A synchronous COM `Run` doubles
as an error check: an error-handler dialog would block it, so a prompt return means a clean run.

### Verify generated code over COM, never by screenshot

The same interface answers the question screenshots were being used for — *is the code I just
generated legal?* Invoke members by DISPID as above:

| member | dispid | use |
|---|---|---|
| `ExecState` | 557 | **0 = BROKEN** (shattered run arrow), 1 = idle/runnable, 2/3 = running |
| `SaveInstrument` | 1002 | persist in-memory scripted edits to disk |
| `Abort` | — | stop a run; see the base-VI caveat below |
| `FPWinOpen` | 534 | settable — **closes a zombie error dialog** that ignores clicks |
| `CloseFrontPanel` / `OpenFrontPanel` / `FPState` | 1061 / 1080 / 608 | window control |
| `ExportVIStrings` | 1000 | dump documentation and connector names to text |
| `GetPanelImage`, `Revert`, `GetLockState`, `SaveForPrevious` | 1016, 1018, 1021, 1024 | occasional |

**Not available:** `IsBroken`, `GetSubVIs`, `CallsList`, `MethodNames`; `AllVIsInMemory` fails with
0x408 "VI Server access denied". Guard `SaveInstrument` behind a path check so it can never be
pointed at an original VI.

### The object-listing reporter — how to select a node deterministically

`Traverse for GObjects` finds every object of a class but **does not specify its ordering**, so
"take the Nth" is not a selector — it is a guess that returns a clean error cluster whether it was
right or wrong. That failure mode is silent and expensive.

The fix is a tiny **read-only reporter VI** that answers *what is object N?*:

```
vi path → Open VI Reference → Traverse for GObjects (Class Name control, BD constant)
        → References → Index Array (index control) → GObject Property Node
                                                       ├ Position   → indicator (cluster Left/Top)
                                                       └ Class Name → indicator (string)
```

Call it once per index — the traverse's own `# of Refs` output says how many there are — and the
*caller* picks the object it wants by position or class. Measured at **0.06 s per call**, so
enumerating a few dozen objects is free. Two design points that matter:

- **No loop is needed inside the VI.** The obvious design puts a For Loop and a property node in the
  reporter to return arrays; taking an `index` argument instead keeps the G code trivial and moves
  the judgement into the calling script, which is where it belongs.
- **Position is knowable in advance.** Creation ops like `Create For Loop.vi` take a `location`, so
  the caller always knows where its own structure is and can select "the ForLoop at (4000,300)".

**Caveat — position does not prove ownership.** Objects on a subdiagram report coordinates in a space
whose origin is not simply the parent diagram's `Position`, so "is this subVI inside that loop?"
cannot be answered by comparing coordinates. Use the GObject **`UID`** and **`Owner`** properties
instead: read each object's UID, read its `Owner`'s UID through a second property node, and
containment becomes an exact integer match.

**Identify what an Op just created by UID set difference, never by position.** Snapshot the uids of
the class before the call and diff after. Two things defeat position matching, and they bit together
in one real build: an object placed inside a subdiagram **does not report the coordinates you asked
for** (requested (4060,360), reported (8061,661)), and a *pre-existing* object may sit closer to the
requested location than the new one — in that case the target VI already had a subVI at (4001,301)
while the loop was being built at (4000,300), so "nearest to where I asked" confidently returned the
wrong node from an otherwise perfect run.

**Owner is a class name, not an identity.** `owner=Diagram` says only "inside some structure";
unrelated subVIs sitting in Case Structure subdiagrams report exactly the same thing. Do not let it
stand in for containment.

### Property Nodes on scripting refnums — two things that will bite

- **A Property Node dropped from Quick Drop is an `Application` node,** not a generic one. Wiring a
  GObject refnum into it produces a **broken wire, not an auto-adapt**. Fix it *first* via right-click
  > `Select Class > VI Server > Generic > GObject` — and note the same submenu-first-entry rule as
  VI Server Class constants: `GObject` is both a category row and its own first entry.
- **The reference input is the TOP-left terminal; `error in` is the one below it.** They are ~9 px
  apart and both are small, so an unverified click lands on `error in` and the refnum wire breaks
  with a class conflict that looks like a class problem but is an aiming problem. Hover the node
  first and measure the diamonds (see THE WIRING PROTOCOL).
- Changing the class does **not** repair a wire that broke under the old class. Run
  `Edit > Remove Broken Wires` and draw it again. `Ctrl+B` frequently does not arrive — use the menu.
- A property row's own output terminal sits at the right edge **of that row**; right-click it and
  check the menu header says `Help For <PropertyName>` before choosing `Create > Indicator`. Extra
  rows come from `Add Element` on the same menu, and each new row duplicates the previous property
  until you click it and pick another.

### Wire a diagram from outside LabVIEW — the report → wire → verify loop

Once a wiring Op exists, editing a diagram needs no mouse at all. The Op takes a *target VI path*,
so **the VI you are building is just another target** — including a half-built tool VI. One measured
cycle:

1. **Report** the target's nodes with the object-listing reporter → each node's class, index,
   position, UID.
2. **Wire** by calling the wiring Op over COM with `(source class, source index, source terminal
   name)` and `(dest class, dest index, dest terminal name)`. Measured at **0.05 s per wire**.
3. **Verify** by re-running the reporter for class **`Wire`** and checking the count went up by one.
   Wire count is the cheapest proof a scripted wire actually landed; never assume from a clean run.

**Terminal names are the one thing you cannot guess**, and a wrong name is not silent: lv-scripting's
`Get Outputs.vi` fails with **error 5001, "Output <name> not found"**. That makes a safe probe — set
the destination name array **empty** so nothing is wired, and run with a candidate source name. Read
the real names once from **Context Help** (hover the node) and write them down; they never change:

| node | inputs | outputs |
|---|---|---|
| `New VI Object` | `auto wire?`, `vi object class`, `owner refnum`, `style`, `location`, `error in (no error)`, `path`, `bounds` | `object refnum`, `error out` |
| `To More Specific Class` | `target class`, `reference`, `error in` | **`specific class reference`**, `error out` |

**The gap to plan around:** a wiring Op built on `Get Outputs` / `Wire Inputs` handles **node → node
only**. Front-panel control and indicator terminals are class `Terminal`, not `Node`, so they are
invisible to it — traversing for `Node` does not return them. Wiring those needs `Get Controls.vi`
(names → control terminals) paired with `Conditionally Connect Wire.vi` (the single-wire primitive
that joins two terminals).

### Wiring node outputs to indicators: `Wire Indicators.vi` (contract verified 2026)

erdosmiller **`Wire Indicators.vi`** closes the node→indicator half of that gap in one call —
inputs `Diagram in`, `Outputs` (array of source-terminal refnums, i.e. exactly `Get Outputs.vi`'s
output), `Indicator Names` (string array, **required**), error pair. Its contract, learned the
hard way on LabVIEW 2026:

- It **selects EXISTING indicators by label** ("indicators selected with Indicator Names on
  Diagram in" — its own Context Help) and **branches each onto the wire already attached to the
  source terminal**. Nothing is created — **no new Wire object appears, so a wire-count check
  cannot verify success**; verify with ExecState and, end-to-end, by reading the indicator.
- **The source terminal must already be wired.** Given an unwired source it extends an unrelated
  wire instead → "This wire connects more than one data source" and the target breaks.
- The useful production pattern: branch a node's already-sunk `error out` (chain ends in
  `Clear Errors.vi`) onto an `error out` indicator — the indicator receives the error value while
  the sink still prevents the dialog, so swallowed 5001s become readable data.
- Class hierarchy fact that makes one cast constant suffice: **TopLevelDiagram inherits Diagram**
  (`Generic ▸ GObject ▸ AbstractDiagram ▸ Diagram ▸ TopLevelDiagram`), and `Traverse for GObjects`
  with Class Name `Diagram` returns the top-level diagram too.

**A running Op cannot edit its own VI** — asking an Op to modify `<itself>.vi` is a **silent
no-op** (clean return, ExecState 1, nothing changed). To apply an Op to its own file, file-copy
the Op and run the copy against the original.

### Growing an expandable primitive (Decimate 1D Array, Interleave, Build Array…)

**There is no scripting API for terminal count.** `GObject.Bounds` is read-only and NI documents no
`Add Terminal` / terminal-count property for primitive classes (peer-researched 2026-08-29 against
NI docs and forums). The documented editor routes are right-click a terminal → `Add Output` /
`Add Input`, or drag the node's bottom border. Since injected right-clicks open nothing on this
LabVIEW build, **the border drag is the route that works** — and it is reliable once you know that
LabVIEW draws real resize handles:

1. **Place** the node with Quick Drop (it is a palette primitive, so Quick Drop is reliable):
   click canvas → `View ▸ Quick Drop` → type the exact name → `Enter` → click the drop point.
2. **Select** it with a plain click on its body. Two **blue square resize handles** appear at the
   top-centre and bottom-centre of the node — zoom (`crop -Scale 8`) to read their exact pixels
   rather than computing them.
3. **Drag the bottom handle downward.** One terminal ≈ **8 px** of travel, but the gesture
   overshoots: a 16 px drag added **two** outputs. Drag back up 8 px to remove one. Iterate against
   the count rather than trying to land it in one move.
4. **Verify by data, never by eye:** the reporter lists each terminal as a `Terminal` GObject whose
   **owner is the node's class**, so `[r for r in report(vi,'GObject') if r['owner']=='Unbundler']`
   counts them exactly. Decimate 1D Array with 3 outputs = **4 terminals** (1 input + 3 outputs),
   its outputs 8 px apart in diagram coordinates.

**Class names are not what you expect.** `Decimate 1D Array` reports as class **`Unbundler`**, not
`Function` — a traverse for `Function` misses it entirely, which looks exactly like "the node was
never placed". When a freshly placed node does not appear in the class you expected, traverse
`Node` (or `GObject`) and find it by position before concluding the placement failed.

**A node with unwired required inputs makes the VI BROKEN**, so a donor VI holding freshly placed
primitives cannot be saved by `gscript.save()` (it refuses broken VIs). Either wire the node
immediately, or place primitives directly into the real target instead of staging them in a donor.

### Wiring INTO a structure: the border-crossing wire auto-creates the tunnel

Proven on LabVIEW 2026: give `Create SubVI.vi` (or any Conditionally-Connect-Wire-based wiring)
a **source terminal OUTSIDE a loop and a sink INSIDE it** and LabVIEW **creates the tunnel
automatically** — auto-indexed for array sources, plain for scalars (its normal wiring defaults).
This is the reliable way to feed a generated loop body: wire front-panel control terminals
(`Get Controls.vi`) straight to the inner subVI's named inputs and let the tunnels make
themselves. Two related traps:

- **`Create For Loop.vi`'s `Inputs` OUTPUT arrived empty at runtime** in this rig's fused op
  (root cause not pinned; its own Connect-Wire tunnel path also never fired) — if inner-tunnel
  refs from Create For Loop are needed downstream, verify they are non-empty before trusting
  them, or bypass with the border-crossing pattern above.
- **A For Loop's `N` terminal reports as class `Tunnel`** (and `P` adds another when parallelism
  is configured). Counting "Tunnel +1" does NOT prove a data tunnel was made — data tunnels
  report as `LoopTunnel`. This masked a months-long silent no-op here.

**GUI wire deletion: a single click selects one SEGMENT, and Delete removes only that segment**,
leaving broken remnants and an unchanged Wire count while the VI silently breaks. After any GUI
wire deletion, run `Edit ▸ Remove Broken Wires` and verify by counts/ExecState. (Double-click
selects the branch, triple-click the whole tree — but the click-verify-delete-cleanup sequence
with a single segment plus cleanup is the deterministic route.)

**For GUI wiring, use a dedicated wire primitive, not raw click pairs.** Two click-click attempts
failed here (one left a pending rubber band that blocked all COM until Esc); a scripted gesture
with approach-and-settle motions (`lv_gui.ps1 -Action wire`: approach the source from the left,
pause to let LabVIEW arm the wiring tool, click, drag the band via a midpoint, settle ON the
destination, click) landed the same wire first try.

### A modal dialog can deadlock LabVIEW — break it by closing the *enabled* window

An unhandled error inside a running VI raises a **modal dialog**, and from that moment every COM call
that needs the root loop (`Run`, `Abort`, `SaveInstrument`) hangs; only cheap property reads still
answer, which makes LabVIEW look healthy. Worse, calling `Abort` to recover pops a second
*Resetting VI* progress dialog that is **application-modal**, so it disables the first dialog's own
`Continue`/`Stop` buttons — clicks on them do nothing, and there is no visual cue that they are dead.

**Diagnose it by asking Windows, not by looking** — `scripts/lv_gui.ps1 -Action dialogs` does this:
it enumerates the LabVIEW process's visible top-level windows with `IsWindowEnabled`, and when VI
windows are *blocked* while exactly one other window is *enabled*, that one is the modal.
`-Action dismiss` then posts `WM_CLOSE` to it (clicking its ✕ is unreliable; the posted message is
not), and refuses to act unless the pattern is unambiguous, so it can never close a VI window.
Round trip is two calls and no screenshot. Two details matter: floating windows (Context Help, the
palettes, Quick Drop) stay enabled while a modal is up and must be excluded or every verdict reads
"ambiguous"; and closing a *Resetting VI* progress dialog re-enables the error dialog underneath it,
which then responds to a normal click.

**Run `-Action dialogs` the moment any COM call hangs.** It is almost always this, and the cost of
checking is nil compared with the cost of the wrong diagnosis.

**A blocked VI also blocks the editor, not just COM.** While one VI sits in `ExecState = 2` waiting
on a dialog, LabVIEW's **menus stop opening** and shell-opening a `.vi` does nothing — yet
`GetVIReference` + `FPWinOpen = True` still loads and shows another VI perfectly. So when the GUI
seems dead, try COM before concluding LabVIEW has hung.

**Do not reach for a restart, and do not blame your tooling.** Every "wedged VI" observed here —
including two that survived toolbar Stop, `Ctrl+.`, COM `Abort`, and a killed COM client — turned out
to be *a modal dialog nobody could see*, sometimes behind other windows, sometimes reachable only
after closing the `Resetting VI` dialog on top of it. The enabled-window scan finds it every time,
and dismissing it returns the VI to `ExecState = 1` immediately. Killing the COM client mid-`Run`
does **not** by itself wedge a VI; that was a false diagnosis, and acting on it costs a LabVIEW
restart that fixes nothing you could not fix in two calls.

The cure is upstream: **never let a scripting VI raise a dialog.** Chain `error in`/`error out`
through every node into an `error out` indicator. `Owner` is a common offender — it is valid on an
ordinary object but fails with **error 1055** on a `TopLevelDiagram`, whose owner is the VI, not a
GObject.

**`Ignore Errors inside Node` is not enough on its own.** Setting it on a Property Node (right-click,
✓ appears in the menu) stops the failure from *wedging* the VI — after an error the VI returns to
`ExecState = 1` instead of hanging in state 2 — but the automatic error dialog **still appears**.
Only a wired error chain removes it.

### File-substitution ops DESTROY unsaved in-memory edits — order the two kinds of edit

The fleet has two incompatible families of operation, and mixing them silently loses work:

| family | ops | how it works |
|---|---|---|
| **in-memory** | drop a subVI, wire, set a property | edits LabVIEW's loaded copy; nothing on disk until `save()` |
| **file-substitution** | `copy_into`, `move_by_label`, `delete_by_label` | byte-copies the target *file* into the Move example's fixed static refs, runs, **saves**, and copies the result **back over the target file** |

So a substitution op **overwrites the target file from disk state**, and the loaded in-memory copy
then diverges — the next `revert` (or reload) throws the in-memory work away. Observed: a node drop
plus a wire vanished because a `copy_into` ran afterwards; the copied control survived (it went
through the file) while the scripted edits did not.

**The rule: do all substitution ops FIRST, or `save()` immediately before each one.** After any
substitution op, treat the loaded copy as stale and re-read. A clean order for building an Op VI is:
file-level surgery (delete nodes, copy in controls) → save → in-memory work (drop, wire) → save.

### Error 2 from a scripting node means LabVIEW is out of memory — save, then restart

Symptom: every scripting call starts failing with **error 2** ("Memory is full"), from whichever
node runs first — `Traverse for GObjects` in one VI, a Property Node in another. The give-away that
it is *not* your target is that the failure follows the **reporter**, not the file: a VI that
reported fine minutes earlier now fails identically.

Cause: this is the leaked-references rule coming due. Op VIs that deliberately skip
`Close Reference`, plus loading large VIs and their whole dependency trees repeatedly, accumulate
until the process cannot allocate. Observed on LabVIEW 2026 at ~770 MB private bytes — low for a
64-bit process, so do not wait for a dramatic number before suspecting it; a restart dropped it to
~410 MB and every call worked again.

**Recovery order matters: SAVE FIRST, then restart.** Scripted edits live only in memory, so a
restart discards them — and `SaveInstrument` still works in this state (it saved a 72 KB target
fine while every traverse was failing). Check `ExecState == 1` first, since a broken VI cannot be
saved. Then kill and relaunch, and cold-verify counts from disk before continuing.

### Saving a BROKEN VI: use the GUI, and expect the file to shrink

`gscript.save()` refuses a broken VI and `SaveInstrument` blocks on one, but **File ▸ Save from the
menu saves it fine** — which is what rescues an unsaved mid-assembly state when scripting has just
died (see the error-2 note above). Two things to expect:

- **The file gets much smaller** — a 72 KB target saved as 31 KB. That is not data loss: a broken
  VI has no compiled object code, and the compiled code is most of a `.vi`'s bulk. Verify by
  reloading from disk and counting objects; the diagram comes back complete, and the size returns
  once the VI is fixed and saved again.
- **Floating windows steal the menu bar.** The Navigation window opened at (0,0) covered the block
  diagram's own menu bar, so a click on "File" landed in the navigator instead. Move or close
  floating windows before menu work — the same hazard as Context Help swallowing right-clicks.

### Killing LabVIEW queues a "Select Files to Recover" dialog for the next start

Force-killing the process is a legitimate restart (and the cure for the memory error above), but it
counts as an abnormal shutdown, so **the next launch opens a modal `Select Files to Recover`
dialog** listing autosaved backups — and it blocks every COM call until it is answered. Two
practical notes:

- **Read the list before answering.** It names the original file paths. In one case the only entry
  was a scratch VI that had been deliberately deleted hours earlier, so `Cancel` ("move backup files
  to the archives directory") was obviously right. Never answer it blind — it is the one dialog that
  can resurrect stale versions of real work.
- **It answers slowly.** `-Action dismiss` (WM_CLOSE), a focused click on `Cancel`, and `Esc` all
  appeared to do nothing, and the window was still listed on the next two checks — then it closed on
  its own a call or two later. Do not escalate by hammering it; issue one action, wait, re-check.

### Do NOT brute-force a primitive's terminal names — it crashed LabVIEW

Name-based wiring works beautifully for subVIs, whose terminal names are their control labels. For
**primitives it is a dead end**: their terminals are documented by description ("elements 0, n, 2n,
…") rather than by a label you can pass to `Get Outputs`. A loop that fed seven candidate spellings
to the wiring op **crashed LabVIEW 2026 outright** (it restarted into a splash screen stuck at
"Finishing initialization"). This is the same family as the banned `style`-code sweep: feeding
guessed identifiers to scripting nodes is what NI warns can take the process down.

So: **wire primitives through the GUI**, or wire only subVIs by name. And if a primitive really must
be addressed programmatically, get its true terminal names from Context Help first — never by
iterating guesses.

**Plan the geometry before you place anything.** GUI wiring needs both endpoints on screen at once,
and diagram zoom cannot rescue a long span (a 4 px terminal at 33 % zoom is ~1 px). Measure the
source's position with the reporter *first*, then create the structure near it — `Create For Loop`
takes a `location`, so this is free. Building at a convenient-looking empty spot and only then
discovering the source terminal is 5,000 px away costs the whole assembly.

### Placing a node at a chosen spot on a huge diagram

Quick Drop places at the click point, so the view must already be where you want the node — and
the failure is silent: on a big VI the view scrolls back between steps, and the placement click
lands somewhere else entirely (once inside an unrelated structure, once nowhere at all). The
sequence that works:

1. **Navigate first** with `View ▸ Navigation Window`, clicking the thumbnail region you want.
2. **Screenshot the diagram** and confirm the target area is on screen and empty.
3. `View ▸ Quick Drop` → type the name → **screenshot to confirm the item is highlighted** → Enter.
4. **Screenshot again** to confirm the view has not moved, then click the empty spot.
5. **Verify by data**: `report` the node's class and check `owner == 'TopLevelDiagram'` when it must
   sit outside every structure. `owner == 'Diagram'` means it landed inside something.
6. Do not follow up with a "click empty canvas to deselect" — that click started a rubber band that
   blocked every COM call until Esc. Move the mouse away instead.

### Scripted edits live in memory — save the target, or they evaporate

A scripting driver edits the target VI **in LabVIEW's memory**. Nothing reaches disk until something
calls `SaveInstrument` on *the target* (not on the driver). Restart LabVIEW and every unsaved edit is
gone, silently and with no warning, because the target was never marked in a way you would notice.

This was verified the hard way: a build target that had received a scripted For Loop and two subVI
drops turned out, after a restart, to be **byte-identical to its pristine source** — the whole
assembly had only ever existed in memory. Two consequences worth designing around:

- **Put the save in the runner**, so every command script ends by persisting its target.
- **Re-running an assembly is only idempotent because of this.** Against a freshly loaded file it
  starts clean; against a still-loaded one it appends duplicates. Check what is already in the target
  with a reporter rather than assuming.

### Four COM traps worth knowing before you hit them

- **`SaveInstrument` blocks forever on a BROKEN VI.** Saving a VI whose run arrow is shattered (a
  half-built driver, say) can leave the COM client waiting indefinitely — measured at 20 minutes with
  the client burning 0.1 s of CPU, i.e. blocked rather than working. Crucially this is *not* a wedged
  root loop: other processes' property reads keep answering instantly the whole time, and no dialog
  window appears. Check `ExecState` first and **save broken VIs from the GUI instead**. Killing the
  blocked client is safe and let the save complete in one observed case.

- **An ARRAY-OF-CLUSTER control needs an explicit `VARIANT`; a plain Python list fails SILENTLY.**
  `SetControlValue('Properties', [('IndexMode', True)])` raises nothing and does nothing, because
  pywin32 sees a sequence of equal-length sequences and marshals it as a **2-D SAFEARRAY**
  (`cDims=2`). LabVIEW wants a **1-D SAFEARRAY of VARIANTs whose elements are themselves 1-D
  SAFEARRAYs of VARIANTs** (`cDims=1`, one inner array per cluster, fields in tab order). On a
  dimension mismatch LabVIEW's coercion discards the write but still returns `S_OK`, so COM reports
  success. Wrap it explicitly and it round-trips:

  ```python
  import pythoncom
  from win32com.client import VARIANT
  V = pythoncom.VT_ARRAY | pythoncom.VT_VARIANT
  row = VARIANT(V, [VARIANT(pythoncom.VT_BSTR, "IndexMode"),
                    VARIANT(pythoncom.VT_BOOL, True)])
  vi.SetControlValue("Properties", VARIANT(V, [row]))
  vi.GetControlValue("Properties")      # -> (('IndexMode', True),)
  ```

  Verified on LabVIEW 2026: the plain list leaves `()`, the VARIANT form reads back
  `(('IndexMode', True),)`. `gencache.EnsureDispatch` does **not** help — `SetControlValue`'s IDL
  signature is `(BSTR, VARIANT)`, so the value stays weakly typed either way.
  Mechanism and code from a Gemini research dispatch, 2026-08-30, citing
  [NI: Converting Data Between ActiveX and LabVIEW](https://www.ni.com/docs/en-US/bundle/labview/page/lvconcepts/converting_data_between_activex_and_labview.html)
  and [NI forum: How to send an array of clusters from python to labview](https://forums.ni.com/t5/LabVIEW/How-to-send-an-array-of-clusters-from-python-to-labview/td-p/4172422);
  archived at `archive/peer/2026-08-30-...-activex-cluster-array-setcontrolvalue.md`.
  `gscript.cluster_array(rows)` wraps this.

  **The trap this set:** `()` was read as proof the write was impossible, and a working design was
  abandoned for a day. Then a property node *did* appear from an empty array — a property node
  always carries one default row — which looked like proof the write had worked. **Both readings
  were wrong, and both felt conclusive.** A silent-failure symptom deserves a peer search before it
  is allowed to change a plan.

- **`SendKeys "^s"` leaves the File MENU ACTIVATED, and an active menu blocks ALL COM.** The menu
  bar's `File` renders highlighted afterwards; while it is active LabVIEW's UI thread is modal, so
  the next COM call — even a trivial property read — hangs until the watchdog fires. This was
  mistaken twice for a wedged LabVIEW and cost a process restart. **Always send `Esc` after any
  SendKeys accelerator**, whether or not the action appeared to work. A hang whose screenshot shows
  a highlighted menu title needs `Esc`, not a restart.
- **A VI's Front Panel and Block Diagram windows both match a substring title search**, and
  `Ctrl+S` sent to the Front Panel may do nothing while the Block Diagram window takes it. Target
  `"<name>.vi Block Diagram"` explicitly, and sleep ~0.8 s after focusing — `SetForegroundWindow`
  needs a moment before keystrokes are accepted.
- **Refnum controls cannot be read at all.** `GetControlValue` raises for a refnum regardless of the
  name given, so it cannot be used to discover a refnum terminal's name (35 candidate names on
  `Set Name.vi` produced 0 hits while `Name` and both error terminals read fine).
- **A dangling `Open VI Reference` still executes.** Deleting the node an Op's second path input fed
  leaves that `Open VI Reference` orphaned but live, and it raises **error 7 ("File not found")** at
  runtime with a blank path — which looks like the *first* path input failed. Either delete the
  orphan or set its path control to any valid VI. `ExecState == 1` does not catch this: the VI is
  legal, it just fails when run.
- **`SetControlValue` is runtime-only.** Values set over COM vanish when the VI unloads from memory.
  To persist a driver's configuration: set the values, then **`Edit > Make Current Values Default`**
  in the GUI, then save. This costs a debugging round every time it is forgotten.
- **ActiveX cannot dispatch parallel clones.** `GetVIReference(path, "", False, 0x40)` requests a
  reentrant-run reference, but every ActiveX caller receives **the same base VI** regardless of the
  VI's reentrancy setting. Proven: a second job overwrote the first's front-panel control values, and
  its `Run` failed 0x3E8 "not in a state compatible". Real parallel dispatch needs a G-native
  `Start Asynchronous Call` launcher. Serialise instead — scripting edits queue through LabVIEW's
  root loop anyway.
- **`Abort` on a clone reference does nothing across threads**, but `Abort` on the **base VI**
  reference from a fresh process releases hung clones instantly (it also aborts sibling jobs).

### Make errors return as data, never as a dialog

A `Simple Error Handler` in a driver VI is actively harmful for unattended runs: its modal dialog
holds `Run` hostage indefinitely, and the window is titled after the *VI* —
`[Details Display Dialog.vi] Front Panel` — so it is easy to miss in a window list. Delete it and
wire an **`error out` cluster indicator** instead. In one case this turned apparently random 20–74
minute "hangs" into a 1.0 s run returning the error as a value; the hangs had been perfectly
deterministic all along.

**Hang triage rule:** on any suspected hang, enumerate windows *first* and look for a `[*.vi]`-titled
dialog. Give every scripted run a watchdog that aborts on timeout — the edits made before the hang
usually survive.


## Wire-count arithmetic lies about branches — and three more hard-won rules (2026-08-31)

- **A branch does not create a Wire object.** One wire owns every segment and sink, so wiring an
  already-connected source to a new destination leaves the Wire count unchanged. Any "+1 wire"
  verification misreads a successful branch as a silent failure — it did, twice, while the branch
  was in fact made. Verify a branch by its EFFECT: a required input becoming fed flips
  `ExecState` 0→1, which is unforgeable. (`Wire Inputs.vi` also *refuses* to branch — but the
  Create SubVI wiring path branches happily, and a GUI click-click branch is normal LabVIEW.)
- **Never cold-load a broken-saved VI headless.** `GetVIReference` on a saved-broken target
  (compiled code stripped) can send LabVIEW into a 100%-CPU recompile spin that never returns —
  8+ minutes before the kill. `OpenFrontPanel` first: the same VI loaded in 16 s. Related:
  `GetVIReference` itself is typically called OUTSIDE any watchdog — it hangs its caller forever,
  so a stuck client with an idle-looking LabVIEW may be sitting in exactly that call.
- **A Ctrl+S issued while LabVIEW is in error-2 (memory full) state writes a STALE file** — the
  mtime moves, the content is the previous save. Work was lost to a "successful" save. After any
  error 2: restart LabVIEW first, save after.
- **Quick Drop discipline:** verify the foreground window by its TITLE PIXELS immediately before
  the Ctrl+Space (focus's return value is not evidence — typed text has ended up in another
  application). Then: `Ctrl+Space` → type the palette name → `Enter` → click the drop location →
  `Esc`, and confirm by object count over COM, not by eye.
