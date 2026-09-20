---
type: reference
status: current
date: 2026-09-15
tags: [teaching]
---

# LEARNING.md — what Claude did in LabVIEW, explained for you

**Audience: you (the human), not the next LLM.** The other docs — `STATUS.md`, `archive/WORKLOG.md`,
`STATUS.md` — exist so a fresh chat can resume work cold. *This* file exists so you can
catch up later on **what was done and, more importantly, why it works**. It is written to teach the
technique, not to log every click. Newest topic last.

---

## 1. VI Scripting — editing a block diagram with code instead of a mouse

### The problem it solves

Everything this project wants to do (add a parallel For Loop, drop the single-bead tracking kernel
inside it, rewire outputs) is an *edit to a block diagram*. The obvious way to automate that is to
drive the mouse: screenshot the screen, work out where things are, click. We tried that. It is slow,
and for some operations it **flatly does not work** — a whole session was lost trying to select a
structure's 1-pixel border by simulated click on a dense diagram. It never selected reliably.

### What VI Scripting is

LabVIEW has an official programmatic API — supported since LabVIEW 2010 — for **creating and editing
VI content from G code**. You write a little "driver" VI whose block diagram, when run, reaches into
*another* VI and adds/moves/wires objects there. No coordinates, no screenshots, no guessing.

It's off by default. Turn it on at:
`Tools ▸ Options ▸ VI Server ▸ "Show VI Scripting functions, properties and methods"`.
(On this machine that wrote `server.viscripting.showScriptingOperationsInEditor=True` into
`LabVIEW.ini`.) After that, a new **VI Scripting** palette appears under
`Functions ▸ Programming ▸ Application Control`.

### The single most useful discovery

**NI ships a complete, runnable VI Scripting example suite with LabVIEW**, and almost nobody notices
it. It lives at:

```
C:\Program Files\National Instruments\LabVIEW 2026\examples\Application Control\VI Scripting\
```

with folders for `Creating Objects`, `Creating VIs`, `Finding and Modifying Objects`,
`Moving Objects`, `Selecting Objects`, `Structures`, `Connector Pane`, `Managing References`.

A copy now lives in `user.lib\claudeDev\NIScriptingExamples\` so we can modify it freely without
touching NI's originals. **The lesson: adapt a working example rather than hand-building a driver.**
Building one from scratch by clicking cost a whole session and still didn't run; cloning
`Adding Objects.vi` and changing one constant took minutes.

### How `New VI Object` works — the node that does the actual creating

This is the core function. Its job: *put a new object into some target VI.* Its terminals are unusual
because one of them is on **top** of the node, not the left:

| terminal | where | what to wire |
|---|---|---|
| `vi object class` | **top** edge | *what kind of thing* you want a reference to — a **VI Server Class constant** |
| `owner refnum` | left, 1st | the VI (or diagram) that will own the new object |
| `style` | left, 2nd | *which specific object* to drop, chosen from a huge alphabetical ring |
| `position` | left, 3rd | a cluster of two I32 — where on the diagram, e.g. {100, 200} |
| `error in` | left, bottom | normal error chain |
| `Path` | — | **leave unwired** (see the trap below) |
| `bounds` | — | **leave unwired** |

The example's own on-diagram instructions summarise it as: *"Determine the owner, class, style, and
location of the new object."* Four things. That is the whole idea.

**`class` vs `style` is the subtle part.** `class` decides the *datatype of the reference you get
back* (a For Loop refnum, a Function refnum...). `style` decides *what object is actually created*
(Subtract, For Loop, String Control...). They must agree. Set `class` by right-clicking the class
constant and using **`Select VI Server Class ▸`**, which opens the LabVIEW class hierarchy. For a For
Loop the path is:

```
Generic ▸ GObject ▸ Node ▸ Structure ▸ Loop ▸ ForLoop
```

Worth browsing that menu once — it is essentially a map of every object LabVIEW knows how to make.
`Node ▸ SubVI` is the branch we'll need for dropping the tracking kernel into a loop.

### Two errors, and what they teach

- **Error 1059 (0x423) "Unexpected file type."** Our hand-built driver wired the *target VI's own
  `.vi` path* into `New VI Object`'s `Path` input. That input is not "which VI am I editing" — it is
  for a **type definition (`.ctl`) or a LabVIEW class (`.lvclass`)**, used only when the object being
  created needs one. Handing it a `.vi` is literally an unexpected file type. **Fix: don't wire
  `Path` at all.** NI's working example leaves it empty.

- **Error 1057 (0x421) "Type mismatch: Object cannot be cast to the specified type."** After
  switching `class` to `ForLoop` but leaving `style` as `Subtract`, LabVIEW built a Subtract function
  and then tried to hand it back as a For Loop reference. Hence "cannot be cast". **The lesson is the
  general one: `class` and `style` are two halves of one decision.**

Both errors were *silent* at first — LabVIEW's `Simple Error Handler` dialog opens in a window titled
after the **VI's name**, not "Error", so it hid in plain sight in the window list. If a scripting run
seems to do nothing, go looking for that dialog.

### How to debug a scripting driver

The run produced a new VI but it was empty, with no visible complaint. Two things that resolved it:

1. **Check the run arrow.** A *solid* arrow means runnable; a *shattered/split* arrow means the VI is
   broken. That is how we proved `style` is genuinely **required** — deleting its constant instantly
   broke the arrow, while `Path` and `bounds` can stay unwired forever.
2. **Look for the error dialog by title.** See above.

### Where this leaves the project

VI Scripting is now **proven working on this machine**: a driver ran for real and programmatically
dropped a Subtract function onto a brand-new VI's block diagram. That retires the screenshot-and-click
approach for anything scriptable, and it is what makes the planned parallel-For-Loop rebuild
practical instead of painful.

---

## 2. Reading a `.vi` without opening LabVIEW

A `.vi` is a compiled binary (an `RSRC` container), and most of its interesting content is
**zlib-compressed inside the file**. `tools/decompress_vi.py` scans for zlib stream headers, inflates
everything it finds, and pulls printable strings out. That recovers control labels, string constants,
comments — and, usefully, the *contents of ring/enum constants*.

That last one paid off here: dumping strings from `Adding Objects.vi` printed the entire `style` ring
— thousands of entries, alphabetical, from `Absolute Value` to `While Loop` — which is how we knew
`For Loop`, `While Loop` and `Case Structure` were creatable before ever opening the VI.

**Its limit:** it cannot recover *wiring*. You get the nouns, never the verbs. Compiled x86-64 machine
code is embedded in those same streams and produces convincing-looking ASCII noise, so treat any
single string as a hint, not proof.

---

## 3. Why clicking is the wrong standard — and what to use instead

This is the most useful lesson of the day, and it is a **methodology** lesson rather than a LabVIEW
one.

Getting one ring constant changed from `Subtract` to `For Loop` took roughly **twenty round-trips**.
Not because it is hard, but because every single step costs a screenshot, a crop to magnify it, and a
visual read before the next click can even be aimed. When a target is 4 pixels tall — like the `style`
terminal on `New VI Object` — a 2-pixel aiming error costs the whole cycle again. Some steps failed
in ways that were invisible: keyboard shortcuts sent programmatically (`Ctrl+R`, `Ctrl+Z`) sometimes
never reached LabVIEW at all, so a step would silently not happen and the next screenshot looked
identical to the last.

**The fix is not to click better. It is to stop clicking.** The tiers, cheapest first:

1. **Parameterised driver, called from outside.** Build *one* scripting driver VI whose front panel
   has controls — target VI path, object class, style, position. Then drive it from PowerShell via
   **VI Server (ActiveX)** or **LabVIEW CLI**, setting those controls and running it. Every later edit
   becomes one command with zero screenshots. This is the standard to aim for: the GUI is touched
   *once*, to build the driver, and never again for routine work.
2. **Hand-edit a driver in the LabVIEW GUI** — only when the driver itself must change shape.
3. **Screenshot-and-click** — genuine last resort.

The general principle, worth carrying beyond this project: *when a task needs pixel precision on a
tiny target, that is a signal to change method, not to aim again.*

### Practical GUI-automation notes (for when tier 3 is unavoidable)

All of these live in `tools/lv_gui.ps1`, which now has `windows / focus / shot / shotwin / crop /
click / rclick / dclick / move / drag / wheel / key / keys / cursor / md5`.

- **Use `shot` (full screen), not `shotwin`, for anything involving a menu.** LabVIEW popup and
  dropdown menus are separate top-level windows and are invisible to a window-only capture.
- **Error dialogs hide in plain sight.** LabVIEW's `Simple Error Handler` dialog is titled after the
  *VI's name*, not "Error". A run that appears to do nothing may have a dialog sitting open.
- **Menus beat keyboard shortcuts.** `Edit ▸ Undo` clicked in the menu is reliable; `Ctrl+Z` sent
  programmatically often is not.
- **Ring dropdown type-ahead is unreliable; the mouse wheel works.** Scrolling a long list by wheel
  and reading the result is more dependable than typing a prefix.
- **`Create ▸ Constant` on a terminal is the right way to make a correctly-typed constant.** LabVIEW
  generates one that already matches the terminal's type, which sidesteps a whole class of type
  mismatch errors — you only have to set the *value*.

---

## 4. The thing that makes GUI control actually workable: LabVIEW snaps to terminals

This came from you, and it corrected a genuinely wrong approach on my part.

I had been treating a block diagram as a bitmap: compute where a terminal is, click that pixel, hope.
Terminals are ~4 pixels apart, so this failed constantly. Your question — *"how could people wire
them in such a micro-control manner?"* — is the right one, and the answer is that **people don't aim
precisely.** LabVIEW helps them.

With Automatic Tool Selection on, moving the cursor **near** a terminal makes LabVIEW switch to the
wiring tool, paint a coloured dot on each terminal of that node, highlight the one it intends to
grab, and show a **tip strip naming it**. Verified here: hovering the `New VI Object` node produced a
tip strip reading `style` — the exact terminal that had cost a dozen round-trips to find by
arithmetic.

So the correct method is **hover → capture → read what LabVIEW says → then click**, rather than
compute-and-hope. The application is a better oracle about its own state than any coordinate I can
derive from a screenshot. Two consequences fell out of this:

- **A negative signal is information.** Context Help showing "No description available" means *not on
  a terminal* — a correct answer telling you to nudge, which I had misread as a broken tool.
- **Wiring is click-then-click, not a drag.** You click the source terminal, then click the
  destination; LabVIEW routes the wire itself. Press-glide-release is for rubber-band *selection*.

The general lesson, and the reason this is written down: *when automating a GUI, use the
application's own feedback as the oracle.* Anything else is guessing with extra steps.

---

## 5. Turning a hard problem into a solved one: finding terminals by colour

Worth reading as a small case study in how to attack an automation problem.

The recurring pain was that node terminals are ~4 pixels apart, so clicking one meant cropping a
screenshot to 8x, reading coordinates by eye, and usually being 2 px out. Three benchmark runs all
lost most of their budget to this, and one failed outright because it skipped the verification step
to save calls.

The realisation: **a block diagram is not a photograph, it is a rendering with a strict colour code.**
Every wire type has an exact RGB value. So instead of *looking* at the picture, scan a single column
of pixels just left of a node and report where the colour changes. Each connected terminal announces
itself by its wire colour:

```
  250  #007F7F  teal   -> owner refnum (a refnum wire)
  258  #0000FF  blue   -> style        (a ring/numeric wire)
  265  #993300  brown  -> position     (a cluster wire)
  273  #7F7F00  olive  -> error in     (the error cluster)
```

That is now the `probe` action in `tools/lv_gui.ps1`. It reproduced a painstaking manual derivation
*exactly*, in one call instead of a dozen, with no visual interpretation and therefore nothing to get
wrong. Scanning just *inside* the node edge additionally reveals `#FF0000` — LabVIEW's red
required-input marker — so you can tell which inputs are mandatory without consulting any docs.

The transferable lesson: when GUI automation feels like it needs superhuman precision, look for a
**deterministic signal already present in what is being rendered** — a colour code, a tip strip, a
status glyph — and read that instead of trying to aim better. Precision problems often dissolve into
lookup problems.

---

## 6. Terminology: what "driver VI" means (and what it does not)

A **driver VI** here has **nothing to do with a hardware driver.** It is simply *a LabVIEW VI whose
job is to edit another LabVIEW VI.*

VI Scripting is "G code that writes G code", so VIs split into two roles:

| role | what it does | examples in this project |
|---|---|---|
| **driver VI** | performs the edit. You press Run on *this* one | `ScriptDriver_DropForLoop.vi`, `KernelBuilder_v1.vi`, and NI's own `Adding Objects.vi` |
| **target VI** | receives the edit. It is the deliverable | the parallelised tracking kernel |

The relationship is the same as a macro and the document it edits: the macro is the driver, the
document is the target.

### Why one is needed at all

The lv-scripting library's `Create For Loop.vi`, `Create SubVI.vi` and friends are **functions** — they
cannot run on their own. Something has to call them in the right order with the right parameters, and
the VI holding that calling code *is* the driver.

```
[KernelBuilder_v1.vi]        <- driver: the VI you press Run on
   |  Open VI Reference      -> open the target
   |  Create For Loop        -> P = 4, auto-indexing on
   |  Create SubVI           -> place Track 1 kernel inside the loop
   |  Diagram > CleanUp      -> tidy
   |  Save Instrument        -> persist
   v
[parallel tracking kernel.vi]  <- target: the deliverable
```

`Example 8 - For Loops.vi` is itself a driver — running it produced `Untitled 14`, a target VI
containing a parallel For Loop with a `P` terminal.

So **"we still need to build the driver"** means: the individual parts are all verified, but the
script that assembles them for *our* purpose has not been written yet. `KernelBuilder_v1.vi` already
exists as a clone of a working driver, so it is a retarget rather than a build from scratch.

## 7. Why errors must be *wired*, and why a closed VI ignores your edits (2026-08-28)

Two rules of LabVIEW's runtime shaped a whole day of work, and both are invisible until they bite.

**Rule A — an unwired `error out` is a landmine.** When a node finishes with an error and nothing is
wired to its `error out`, LabVIEW "helpfully" pops a modal dialog (automatic error handling). For a
human that is a feature; for automation it is a deadlock, because the dialog freezes the VI *and*
every COM call from outside until someone clicks Continue. The fix is not to handle errors better —
it is to make sure **every error out goes somewhere**. Where the chain ends, park it in
`Clear Errors.vi`: that VI eats the incoming error and never produces one of its own, so the chain
has a true dead end. (An unwired error *in* is harmless — inputs default to "no error".)
`OpWire_v1.vi` got exactly this treatment: one error chain threading all seven nodes, ending in two
Clear Errors sinks. Before: a typo'd terminal name froze LabVIEW behind a dialog. After: the same
typo returns in 0.03 s as "wire count unchanged".

**Rule B — a VI opened "by reference" is not fully in memory.** `Open VI Reference` from COM loads
enough of a VI to *read* its diagram (our reporter works fine) and even to *drop objects onto it* —
but requests to **create wires are silently ignored**: no error, no dialog, the wire simply never
appears. The VI must be fully loaded in edit state first, which `OpenFrontPanel` guarantees. And the
mirror-image trap: **closing that panel before saving throws every edit away** — LabVIEW unloads
the VI and reverts to the bytes on disk, silently. A completed 8-wire build evaporated this way
once. The working order is burned into `gscript.py` now:

```
open_panel(target)  ->  edit  ->  verify (counts/uids)  ->  save(target)  ->  close_panel(target)
```

One more habit both rules reinforce: **verify by counting, never by absence-of-error.** A clean
error cluster after an edit proves only that no error was *raised* — the silent-decline behaviours
above are exactly why the fleet re-counts wires and diffs object uid sets after every mutation.

## 8. Clicking without looking: coordinates from data, verbs that check themselves (2026-09-05)

**The problem.** Some LabVIEW edits still need the mouse (palette placement, a context-menu item,
a dialog button). The expensive way is "screenshot → model reads it → click → screenshot → …":
about 1.5 min and four screenshots per action when a large model does it, and $0.26–0.30 per
action even with the cheapest model that gets it right (opus-low / sonnet-low, benchmark §8).

**The idea.** LabVIEW already *tells* you where everything is: VI Server reports each object's
diagram position (`GObject.Position`), and Windows tells you where the diagram window is. So a
click target is arithmetic — `screen = diagram + (window.left + 11, window.top + 37)` on this
machine — and a *verb* is: compute the point, do the input, then **read the effect back over
COM** (did the node move by (100, 50)? did exactly one new Index Array appear? did the VI break
because a read-only property was switched to write? did the Find window vanish?). No screenshot is
taken on the happy path; the verb returns a small dict with `ok` and what it measured.

**What can go wrong, and the checks that catch it** (from an adversarial review, see
`docs/m3-clicker-spec.md` §7):
- The offset is not a general transform: zoom, scrolling, DPI and a hidden toolbar all break it.
  So `calibrate()` verifies on *two* far-apart objects that each sits under its computed point —
  identified by its header colour (Invoke nodes are cyan `CCFFFF`, Property nodes yellow
  `FFFFCC`), read with a 12-pixel colour probe — and refuses otherwise.
- Pixels are only meaningful on the top window: `OpenFrontPanel` raises the front panel over the
  diagram, and a probe then reads the panel's grey. Focus the diagram first, then probe.
- The Functions palette does not always open at the same place (screen edges flip it), so item
  offsets are stored relative to the *popup window's rect*, which is read from the window list,
  not to the click point.
- Context-menu contents depend on node state, so a menu verb only exists for registered
  (class, item, verifier) triples — `Property / Change To Write / ExecState 1→0` — never "click
  187 px below and hope".
- Dialog buttons are offsets inside the dialog's rect, and the rect's size must match the
  registered size before clicking (a rewrapped or translated dialog refuses).

**Where the numbers live.** `docs/gui-geometry.json` — per machine, data not code. An unknown
entry makes the verb return `ok: False, reason: "no geometry for …"`; that is the signal to fall
back to the vision executor once, measure, and write the offset into the registry so the next
call is arithmetic again. The registry grows by use; the clicks shrink.

**API** (`tools/lvclick.py`): `calibrate(target)`, `focus_bd(vp)`,
`move_node(vp, target, uid, cls, dx, dy)`, `place_from_palette(vp, target, item, cls, x, y)`,
`node_menu(vp, target, uid, cls, row, item)`, `dialog_button(title, button, open_with, bd)`.
Verification batch: `tools/bench/m3v1_verify.py` (3 trials × 4 verbs on `GUIBENCH_v0.vi`).

## 9. The keystone: making a *typed* Invoke Node from Python (2026-09-06)

**Why it matters.** Every scripting node we ever needed (Property Node, Invoke Node) had been placed
by hand: palette, class picker, method picker. `OpBuildInvoke_v0.vi` ends that for Invoke Nodes:
`gscript.build_invoke(target, "VI Server:Terminal", "6349C03", (500, 600))` puts a **Term / Connect
Wire** node, parameter rows and all, on any VI's diagram. It was built from a copy of an existing op
plus the erdosmiller `Create Invoke Node.vi`, wired by script except for two branch wires the user
approved as a one-time GUI exception (a branch cannot be made by the fleet's `Wire Inputs`).

**Two things that were not in any manual and cost most of the day:**
1. *Wires broke for type reasons, not click reasons.* Five "failed" branch clicks were actually
   LabVIEW refusing a Generic refnum on a Diagram-typed input; LabVIEW's **Error List (Ctrl+L)**
   said so in one line. Read the error list before blaming coordinates.
2. *A library VI can fail silently.* `Create Invoke Node.vi` has automatic error handling off and
   we had not wired its error out, so "class not applied" produced no dialog. Its diagram showed
   the mechanism: with a valid `reference` it writes the object's bare class name (`Diagram`) into
   the node's class property, which LabVIEW 2026 rejects (it wants `VI Server:Diagram`); with
   `reference` unwired it uses the caller's string. Hence the op deliberately leaves `reference`
   unwired, takes the class as `VI Server:<Class>`, and the method as its **Unique ID**
   (`6349C02` Create Indicator, `6349C03` Connect Wire) because the library calls Set Method with
   "allow alternate names = false".

**Facts you can reuse:** string wires are drawn *dotted* pink (not broken); a single click selects
one wire segment and Delete removes only that segment (handy for undoing a branch); LabVIEW renames
a pasted control whose label already exists (`Class Name 2` → `Class Name 3`), which is how the op
got its third string input without any front-panel clicking.

**Still open:** the skeleton's leftover `Create SubVI` branch pops one error-7 dialog per run (the
COM watchdog dismisses it; removing the nodes needs a GUI delete), a method-ID inventory
(`Invoke.All Supported Methods`) for the reporter, and the Property-Node twin.

## §10 (2026-09-06) — 타입이 있는 참조를 "사다리"로 얻기: 클래스 상수 없이, 클릭 없이

VI 스크립팅에서 특정 클래스의 Property/Invoke 노드를 쓰려면 그 클래스 타입의 와이어가 필요합니다. 스크립트로 만든
참조는 전부 Generic/GObject라서 지금까지는 To More Specific Class + 클래스 상수(GUI로만 바꿀 수 있음)가 필요했습니다.
오늘 찾은 방법은 다운캐스트를 아예 하지 않는 것입니다. 모든 op가 이미 가진 타입 참조(Open VI Reference → VI)에서
출발해, 출력이 이미 타입을 가진 속성들만 따라 내려갑니다: VI → Block Diagram → Nodes[] → Index Array → Node →
Terminals[] → Index Array → Terminal. 그 Terminal 참조로 Create Control / Create Indicator / Connect Wire를 호출합니다.
이 사다리로 OpBuildIA_v0, OpCreateControl_v1(만든 컨트롤의 라벨까지 돌려줌), OpCreateIndicator_v0, OpConnect_v0,
OpMove_v0를 전부 스크립트만으로 만들었습니다(3b 단계 GUI 클릭 0회). 배운 사실: Nodes[]는 생성 순서(uid 순서 아님),
Property Node 출력 단자 이름은 속성의 짧은 이름(`Diagram`, `Terms[]`), 이미 연결된 싱크에 Connect Wire를 하면
VI가 깨짐(소스 분기는 괜찮음). 파이썬 API: `gscript.build_index_array / create_control / create_indicator /
connect_terminals / move_object / delete_object`.

## §11 (2026-09-07) — 병렬 커널 수치 검증: 무엇을, 어떻게 확인했나

검증 기준(규칙 1a)은 "같은 입력 → 같은 X/Y/Z"입니다. 저장된 프레임(img*.tif), cal002, tra002-000이 그 재료입니다.
1. **입력 재구성은 랩 코드로**: cal 파일은 `Load and prep N cal images.vi`(파일 대화상자만 경로 컨트롤로 바꾼 사본
   HARNESS_loadcal)가 읽고, 코사인 윈도우는 `make both cosine bandpass.vi`가 cross length(120)로 만듭니다. 파이썬은
   숫자·경로만 넘깁니다(클러스터 배열은 COM으로 못 넘김 → LabVIEW 안에서 흐르게 함).
2. **오라클**: 원본 four-fold 커널이 기록된 .tra 값을 소수점 그대로 재현하면(편차 0.0000) 입력 재구성이 정확하다는
   증거입니다. 이게 먼저 성립했습니다.
3. **비교**: HARNESS_compare가 프레임마다 두 커널을 같은 입력으로 돌리고, 파이썬이 (a) v3 == four-fold 비트 단위 비교,
   (b) 둘 다 .tra와 비교, (c) four-fold 출력을 다음 프레임 상태로 되먹임(메인 VI의 시프트 레지스터 역할)합니다.
4. **진단 요령**: v3가 틀렸을 때 "어느 입력이 안 들어가나"는 민감도 테스트로 찾았습니다 — v3 출력이 four-fold에
   시작좌표 0을 넣은 결과와 정확히 같았으므로 starting x/y만 빠진 것. 이후 OpNetInfo로 루프 안 단자를 읽어
   'starting x 1'/'starting y 1' UNWIRED를 확인하고, OpConnect2로 루프 경계를 넘는 배선 2개를 넣고 터널을 자동
   인덱싱으로 바꿨습니다. 결과: 20/20 프레임 동일, 전 프레임 검증 진행 중.
5. **밤새 배운 LabVIEW 운용 규칙**: 재시작 직후 뜨는 작은 창은 닫지 말 것(WM_CLOSE → 이후 COM 호출 전부 멈춤);
   Node.Label/Style 읽기는 TMSC/클래스 상수가 있는 VI에서 LabVIEW를 죽임; 실행 중 죽은 클라이언트는 리포터 VI를
   점유하므로 재시작; erdosmiller 생성 VI를 품은 op는 실행마다 대상에 쓰레기 Invoke 노드를 남기니 바로 삭제.

## §12 (2026-09-14) — 캐스트 없이 VI의 구조를 읽는 법: "이미 타입이 있는 참조"를 따라가기

VI Scripting에서 가장 자주 막히는 지점은 **타입**입니다. `Traverse for GObjects`는 모든 객체를 GObject 참조로 돌려주는데,
`SubVI.VI Name`이나 `Terminal.Is Source?` 같은 속성 노드는 그 클래스의 참조가 들어와야 컴파일됩니다. 캐스트(`To More
Specific Class`)는 클래스 상수가 필요하고, 그 상수는 스크립트로 만들 수 없었습니다(§10).

이날의 해법은 우회가 아니라 **관찰**이었습니다: LabVIEW의 컨테이너 속성들은 이미 타입이 있는 배열을 돌려줍니다.
- `AbstractDiagram.SubVIs[]` → SubVI 참조 배열 → `VI Name`/`VI Path` (호출하는 VI가 무엇인지)
- `Panel.Controls[]` → Control 참조 배열 → `Label`, `Indicator`, `Terminal` → `Terminal.Connected Wire` (패널 객체가 배선됐는지)
- `Node.Terminals[]` → Terminal 참조 배열 → `Name`, `Is Source?`, `Connected Wire` (단자 이름·방향·와이어)
- `Tunnel.Inside Terminals[]` / `Outside Terminal` → 루프 경계의 안팎 와이어
배열을 For 루프에 자동 인덱싱으로 넣고 결과를 자동 인덱싱 터널로 꺼내면(§OpReportAll 패턴), COM에서 한 번의 Run으로
전체 배열을 읽습니다. 이렇게 하루에 만든 리더가 `subvis`, `panel_wiring`, `node_terms`, `tunnels`(tools/gscript.py)입니다.

배우고 기록한 규칙 세 가지:
1. **속성 노드 한 개에 여러 행을 넣지 말 것.** 행은 위에서 아래로 실행되고, 앞 행이 오류를 내면 뒤 행은 기본값(0, FALSE)을
   내놓습니다. "배선 안 됨(0)"과 "읽기 실패(0)"가 구분되지 않습니다. 속성마다 노드를 하나씩, 각자의 error out을 함께 꺼냅니다.
2. **단자 이름은 기계가 찍어준 문자열 그대로 쓸 것.** `Is Broken?`은 노드에서 `Broken?`, `Terminals[]`는 `Terms[]`,
   `ImageToArray`의 출력은 `Image Pixels (U8)`입니다. 추측한 이름 하나가 빌드 한 번을 날립니다.
3. **쓰레기 Invoke는 "열린" 대상에만 떨어집니다.** 참조로만 연 VI(패널을 열지 않음)는 편집을 조용히 거절하므로 메인 VI를
   읽기만 할 때는 오염되지 않습니다. 빌드 대상은 항상 패널을 열기 때문에 거기서만 퍼지가 필요합니다.

같은 날 측정으로 닫은 질문들(archive/benchmarks/INDEX.md 22–24): 이미지 표시 경로는 그림 구성 2.7 ms + **패널이 보일 때
그리기 6.5 ms**(150 Hz 예산 6 ms 초과 → 표시 루프는 분리·간축), 참조-안전 복사(`IMAQ Copy`)는 프레임당 ≤0.4 ms, 물리
코어 하나를 빼도 추적 커널은 +0.3 %(G9 통과). 글로벌 변수는 메인 VI 안에서 7곳 모두 **쓰기**만 — 읽는 곳이 이 계층에
없다는 사실은 사용자만 답할 수 있는 질문으로 남겼습니다.

## §13 (2026-09-14 오후) — "이름 없는 것"에 이름 붙이기: 루프의 N 단자와 암시적 프로퍼티 노드

두 가지가 오후에 풀렸습니다. 둘 다 "스크립트로는 못 한다"고 아침에 적어 둔 항목이었고, 둘 다 **외부 검색 → 피어 공격 →
한 번의 판별 실험**으로 끝났습니다.

1. **For 루프의 N을 스크립트로 배선하기.** erdosmiller `Create For Loop`의 `Control Names`는 기존 컨트롤을 루프에 묶어 주지
   않습니다(측정: 루프는 생기고 터널은 0). 대신 빈 For 루프 노드의 `Node.Terminals[]`를 읽으면 항목이 **딱 하나, 이름은
   빈 문자열, sink, 미배선** — 그것이 N(카운트 터널의 바깥 단자)입니다. 여기에 I32 소스(`IMAQ GetImageSize`의 `Y Resolution`)를
   `Terminal.Connect Wire`로 이으면 실행 가능 상태(0→1)가 됩니다. 검증은 ExecState만으로 하지 않고 **양쪽 단자에 같은 wire
   uid가 붙었는지**까지 확인합니다(피어 지적: Connect Wire는 끊어진 선도 만들 수 있음). 정식 경로 `ForLoop:Loop Count →
   Tunnel:Outside Terminal`은 ForLoop 타입 참조가 필요해서(캐스트 씨앗 부재) 아직 못 씁니다.
   이 덕에 "한 번의 Run 안에서 1024번 복사" 셀이 생겼고, `IMAQ Copy`의 **정상 상태 비용은 0.05 ms**(첫 복사 0.4 ms는 할당
   비용)로 측정됐습니다. N=1280으로 두 번째 점을 찍어 선형성도 확인했습니다.
2. **암시적 `Value` 프로퍼티 노드는 어느 컨트롤에 묶였나.** 정답 속성 `Property.Linked Control`은 Property 타입 참조를
   요구합니다(캐스트 필요). 캐스트 없는 우회는 `Node.Label → Text.Text`: 암시적 노드의 **머리글이 곧 라벨**이고 그 라벨이
   묶인 컨트롤의 이름입니다(LabVIEW Wiki). 위키의 "라벨이 한 번은 표시된 적 있어야 한다"는 주의는 사람이 저장한 VI에서는
   문제가 되지 않았습니다 — 패널을 닫은 채 88개 전부가 패널 라벨로 읽혔습니다. 덤으로 subVI 노드의 라벨은 파일 이름,
   프리미티브의 라벨은 종류 이름(`Index Array`, `Increment`)이라 **모든 노드에 이름이 생겼습니다**(frame-loop-wire-graph.md
   재주석). 아침의 "`Rot \nSpeed`는 유일한 legacy 후보"는 **철회** — 회전 명령 프레임 두 곳에서 읽힙니다.

교훈: (a) "속성이 없다"가 아니라 "그 속성을 볼 타입이 없다"인 경우가 대부분이고, 그때는 **부모 클래스에 있는 다른 속성**
(GObject/Node의 `Label`, `Terminals[]`)이 같은 정보를 다른 형태로 갖고 있는지 먼저 찾을 것. (b) 2026-09-07의 "Node.Label/Style
읽기가 LabVIEW를 죽인다"는 기록은 626개 노드 전수 읽기로 **좁혀졌습니다** — 라벨 단독은 안전, 용의자는 `Style` 또는
TMSC/클래스 상수 노드. 오래된 금지 규칙도 반증 실험의 대상입니다.

## §14 (2026-09-14 저녁) — 캐스트 씨앗, 시프트 레지스터, 그리고 "병렬이 켜져 있었나"

1. **캐스트 씨앗을 GUI 없이 얻는 법.** `To More Specific Class`의 `target class` 입력은 클래스 상수만이 아니라 **그 타입의
   아무 배선**이나 받습니다(NI 문서). 그러니 원하는 클래스의 refnum 컨트롤 하나면 됩니다. NI가 배포하는 예제
   (`examples\Application Control\VI Scripting\Structures\VI Scripting with Structures - For Loop.vi`)에는 ForLoop 클래스 상수가
   프로퍼티 노드 다섯 개에 배선돼 있습니다. 예제의 스크래치 사본에서 그 배선을 지우고, 프로퍼티 노드의 `reference` **입력**에
   `Terminal.Create Control`을 걸면 ForLoop refnum 컨트롤이 생깁니다(출력 단자에 거는 것은 문서화되지 않은 도박 — 피어 지적).
   나머지 노드를 지워 사본을 실행 가능하게 만들어 COM으로 저장하고(깨진 VI는 COM 저장이 안 됨), `copy_into`로 컨트롤을 op에
   옮겨 TMSC에 배선합니다. 이 씨앗은 **자기 클래스만** 캐스트합니다: ForLoop 씨앗을 WhileLoop 참조에 쓰면 아래로 1055가
   번집니다. 그래서 For용·While용 op가 각각 있습니다. 아침에 "사용자 계실 때 GUI 한 번"으로 미뤄 둔 항목이 이렇게 닫혔습니다.
2. **프레임 루프의 상태는 이제 전부 측정값입니다.** `Loop.Shift Registers[]`는 **오른쪽** 레지스터를 돌려줍니다(피어의 추정
   "왼쪽 14개"는 측정으로 뒤집힘). 오른쪽의 안쪽 단자 = 매 프레임 본문이 써 넣는 값(sink), 바깥 단자 = 루프가 끝난 뒤의 최종값.
   왼쪽은 `RightShiftRegister.Left Registers[]`로 갑니다(초기값 입력, 본문이 읽는 source). 14쌍, 중첩(stacked) 없음, 13개 초기화.
   본문의 한쪽만 보이던 배선 83개가 모두 설명됐습니다(터널 29·레지스터 22·중첩 구조 7·패널 단자 17, 상수 8은 소거법).
3. **작은 규칙 두 개가 두 번의 빌드를 날렸습니다.** (a) 구조를 하나 만들면 Traverse의 `Diagram` 인덱스가 밀립니다 — 새
   다이어그램은 **UID**로 찾고 노드가 그 안에 들어갔는지 확인한 뒤 배선할 것. (b) 같은 op에 `index`가 배선된 Index Array가
   둘이면 위치·순서가 아니라 **`array` 배선의 UID**로 고를 것. 둘 다 "예측 실패 → 피어 공격 → 판별 실험" 루틴으로 30분 안에
   잡혔습니다.
4. **원본에는 병렬 루프가 없습니다.** For 루프 17개 모두 `Is Parallelism Enabled?` = FALSE(한 개는 P=12를 저장한 채 꺼져 있음).
   우리가 스크립트로 만든 `PARALLEL_kernel_v3`는 TRUE/P=4 — erdosmiller의 인스턴스 수 입력이 두 속성을 다 씁니다. NI는 두
   속성을 따로 문서화하므로 다른 빌더를 쓸 땐 6362004를 명시적으로 써야 합니다. 이 확인 덕에 "par" 벤치마크 수치(seq 8.15 ms
   → par 2.43 ms)가 진짜 병렬 실행이었다는 것이 저장된 속성으로도 뒷받침됩니다.

## §15 (2026-09-14 밤) — 로터 읽기 부호: 진단에서 하드웨어 검증까지

원본 드라이버 `SetCommand.vi`는 컨트롤러 응답 `POS hhhhhhhh`(8자리 hex, 32-bit 2의 보수)를 `Hexadecimal String To Number`로
파싱하는데, 이 프리미티브의 `default` 입력은 비워 두면 **U32**라 음수가 거대한 양수로 읽힙니다. 흔한 오해 두 가지가 리뷰에서
걸러졌습니다: (1) default에 I32를 물리면 된다 — 아닙니다, NI 문서상 범위 초과는 **최대값으로 포화**합니다; (2) 옆에 있던 Type
Cast가 부호를 복원한다 — 문자열의 ASCII **바이트**를 재해석할 뿐이라 파싱이 아닙니다. 맞는 방법은 U32로 파싱한 **숫자**를 Type
Cast로 I32에 재해석하는 것이고, 사본 `SetCommand_signed.vi`에 그렇게 넣었습니다. 검증은 두 단계: 하드웨어 없이 응답 문자열을
주입해 원본과 비트 단위 비교(양수 10개 동일, 음수 3개 복원, 16/16), 그리고 실제 컨트롤러에서 `CLL X`(카운터 클리어, 이동 없음)
→ `PIC -10` → 수정본 −7.2°·원본 +3.09×10⁹° → `PIC +10` 복귀. 부수 측정: 0.72°/펄스(500펄스/회전), `Baseline Startpoint`는
회전수 단위(200 = +100 000펄스 오프셋), Get Position = Ring 2, 첫 VISA 읽기는 포트 열자마자 타임아웃(한 번 버리고 읽을 것).
도구 쪽 교훈: 최상위 Nodes[] 전용 op는 케이스 프레임 안을 못 만지고(이름 기반 `wire()`를 쓸 것), 덮어쓸 파일을 COM으로 먼저
건드리면(`close_panel`) "changed on disk" 모달이 뜨며, 컨트롤을 구조 안으로 배선하면 Wire 객체가 +2입니다.

## §16 (2026-09-14 밤 ~ 09-15 새벽) — 스크립트로 만든 루프가 원본과 "비트 단위로 같은 숫자"를 내기까지

**무엇을 했나.** 스테이지 2의 첫 조립물 `Track_v6_CPU_core_v0.vi`: For 루프 하나가 픽스처 프레임을 돌며
`IMAQ ReadFile → PARALLEL_kernel_v3clean`을 호출하고, 커널의 세 상태(x,y,z / 비드 유효 플래그 / 캘리브레이션 위치)를
**시프트 레지스터**로 다음 프레임에 넘긴다. 결과: 1·2·200 프레임에서 XYZ/GOOD/POS가 2026-09-07 기준값과
**완전히 동일**(float 정확 비교), 루프 안에서 프레임당 6.1 ms (COM으로 한 프레임씩 돌리던 기준 드라이버는 18–23 ms).

**왜 시프트 레지스터가 "빠진 원시 요소"였나.** 원본 VI의 프레임 루프는 이전 프레임의 x,y를 다음 프레임의 시작점으로
쓴다(피드백). 그 피드백이 없으면 숫자가 기준값과 달라진다. 그런데 스크립트 도구함에는 루프의 *입력 터널*과 *출력 터널*을
만드는 op만 있었고 시프트 레지스터를 **만드는** op가 없었다(읽는 op만 있었다). 이번 밤에 세 가지가 추가됐다:
`Loop.Add Shift Register`(6361000, 공개 메서드)로 레지스터를 만들고, `Terminal.Connect Wire`(6349C03, **싱크 쪽에서
호출**, `Wire Source`가 소스)로 좌·우 단자를 각각 잇고, 타입이 있는 참조는 캐스트 없이 `Loop.Diagram → Nodes[] →
Terminals[]` 체인으로 도달한다. While 루프 씨앗과 For 루프 씨앗은 서로 캐스트가 안 되므로(1055) op를 두 벌 만들었다.

**이 밤에 배운 함정 — 모두 "예측이 틀려서" 피어 리뷰를 거친 것들.**
1. **경계를 넘는 와이어는 와이어 객체가 둘**이다(터널 바깥쪽 하나, 안쪽 하나). 양 끝 uid가 같다는 게이트는 경계
   와이어에 쓰면 안 되고, "새 터널 정확히 하나 + 바깥 uid = 소스, 안쪽 uid = 싱크 + 방향 + 오류 없음"으로 검사한다.
2. **배열을 For 루프 안으로 이름으로 wiring하면 LabVIEW의 편집기 기본값대로 자동 인덱싱이 켜진 채 들어온다.**
   캘리브레이션 클러스터 배열이 "프레임마다 클러스터 하나"로 들어갈 뻔했다 — 규칙 1a(연산 불변)를 깨는 조용한 오류.
   IndexMode == 0 게이트가 잡았고, `set_index_mode(0)`로 뒤집은 뒤 안쪽 와이어가 살아 있음을 다시 읽어 확인했다.
3. **필수 입력이 하나라도 비면 VI는 조용히 깨진다**(ExecState 0). `IMAQ Create`의 `Image Name`이 그것이었다.
   구조 게이트 57개가 다 통과해도 마지막 ExecState 하나가 0이면 아무것도 저장하지 않는다.
4. **내장 프리미티브는 라벨로도 이름으로도 찾을 수 없다**(`Open VI Object Reference` 1054 ×3). 그래서 "참조로 복사"하는
   op(`OpMoveByIndex_v0`: Traverse → Index Array → `Move(Duplicate)`, 선택된 객체의 UID를 돌려주는 가드 포함)를
   만들었고, 그 첫 사용이 `String To Path` 하나짜리 서브VI `StrToPath.vi`다. 깨진 중간 상태를 저장하지 않도록,
   복사 직후 같은 메모리 안에서 필수 입력을 이어 "실행 가능"해진 뒤 한 번만 COM 저장한다.
5. **파일 경로 조합(`Format Into String`)은 포기했다.** 복사된 노드는 도너의 입력 개수(5~6개)를 그대로 가져오고 노드의
   단자 수는 스크립트로 못 바꾼다. 대신 파이썬이 전체 경로 문자열 배열을 넘기고 루프가 자동 인덱싱으로 하나씩 꺼낸다 —
   더 단순하고, 픽스처의 124개 프레임 번호 공백도 저절로 처리된다.

**검증 수준을 정확히 말하면.** 구조 게이트(객체 수·uid·터널 위상)는 "잘 만들어졌다"만 말한다. 숫자가 같다는 것은
1프레임(초기값이 커널에 도달), 2프레임(오른쪽 레지스터 피드백이 작동), 200프레임(누적) 세 단계의 정확 비교로만
확인됐고, 10,043프레임 전체는 별도 배치로 돌렸다(결과는 INDEX 40행). 첫 비드 유실 이후는 원본의 리시드 Case(계획 항목 3)가
아직 없으므로 비교 대상이 아니다 — 그것이 다음 조각이다.

## §17 (2026-09-15 새벽) — 큐로 묶인 세 개의 루프: "왜 While이 아니라 For인가"

**결과.** `Track_v6_CPU_queue_v0.vi`: 이미지 8장을 만들어 `Q_free`에 넣는 풀 루프, `Q_free`에서 이미지를 꺼내 프레임을
읽고 `Q_img`에 넣는 획득 루프, `Q_img`에서 꺼내 커널을 돌리고(시프트 레지스터 3개) 결과 큐에 넣은 뒤 이미지를 `Q_free`로
돌려주는 추적 루프, 결과를 모으는 싱크 루프 — 네 루프가 큐만으로 이어져 병렬로 돈다. 200프레임까지 XYZ/GOOD/POS가
기준값과 비트 동일하고, 프레임 식별자(경로 문자열)가 `Frame Paths`와 정확히 정렬되며, 8장이 모두 풀로 돌아온다.

**첫 설계는 리뷰에서 기각됐다.** 추적 루프를 While로 두고 "`Q_img` dequeue가 타임아웃되면 끝"으로 세우려 했다. 반박은
세 가지였다: (1) 타임아웃은 "생산자가 끝났다"의 증거가 아니라 "T 동안 비어 있었다"의 증거다 — 첫 TIFF가 늦게 읽히면
추적 루프가 먼저 죽고 나머지가 영원히 기다린다. (2) While의 조건 단자는 **반복이 끝난 뒤** 평가되므로 타임아웃된
반복에서도 본문은 기본값(빈 이미지)으로 한 번 더 실행된다 — Case 구조 없이는 막을 수 없다. (3) "슬롯 8개 > 큐 깊이 7이니
`Q_img`는 절대 가득 차지 않는다"는 내 불변식은 거꾸로였다(생산자가 여덟 번째 슬롯을 쥔 채 큐가 꽉 찰 수 있다).

**리플레이에서는 N을 안다 — 그래서 전부 For 루프.** 세 루프가 같은 N번 정확히 돌면 종료 신호도 타임아웃도 Case도
필요 없고, 블로킹 호출(-1)이면 "프레임 유실"은 틀린 숫자가 아니라 **행(hang)** 으로 나타난다 — bgrun의 마감이 그것을 잡는다.
안전성 주장은 조건부로 적었다: "오류가 없는 경로에서, 세 루프가 정확히 N번 돌 때 순환 대기가 없다." 종료(teardown)도
데이터 의존으로 순서를 세웠다: 각 큐의 `queue out`을 **그 큐를 마지막으로 쓰는 루프**를 통해 내보내고, 그 선이 도달해야
Release가 실행된다(Merge Errors 없이 만든 조인). 라이브 카메라(스텝 D)에서는 While + 종료 토큰 + Case가 불가피하다.

**풀을 정수 슬롯이 아니라 이미지 참조의 큐로 바꾼 이유.** Index Array를 루프 안에 놓는 op가 없었고, 슬롯 번호 대신
이미지 참조 자체를 큐로 돌리면 배열도 인덱싱도 필요 없다. 소유권 규칙은 그대로다: `Q_free`에서 꺼낸 쪽만 그 버퍼에 쓴다.
IMAQ 이미지 와이어는 **가변 버퍼의 참조**라서, 커널이 다 읽기 전에 획득 루프가 같은 버퍼를 덮어쓰면 안 된다 — 추적 루프가
이미지를 `Q_free`로 돌려주는 Enqueue를 결과 Enqueue의 오류 체인 **끝**에 두어 "커널 완료 → 결과 발행 → 반환" 순서를
데이터 의존으로 강제했다(리뷰가 이 happens-before를 요구했다).

**이번 밤의 도구 교훈 셋.** ① 파이썬이 예제 VI 파일에 바이트를 덮어쓰는 "치환 프로토콜"은 LabVIEW가 그 VI를 **로드한 뒤**에
하면 Errno 22로 실패한다(메커니즘은 미확정 — "메모리 맵" 가설은 리뷰에서 기각됨) → 로드 전에 치환, 그 다음 revert.
② 단자 이름은 바이트 단위로 정확해야 한다: `'timeout'`이 아니라 `'timeout in ms (-1)'` — 추측 하나가 9분 배치 하나.
③ 루프 노드의 `Terminals[]`는 터널 바깥 단자들을 이름으로 나열한다 — 루프의 출력을 다른 노드처럼 이름으로 이을 수 있다.
