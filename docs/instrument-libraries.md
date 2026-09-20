---
type: reference
status: current
date: 2026-09-14
tags: [docs]
---

# Instrument libraries of the main VI — what drives what

> Document 1 of the system inventory (`docs/system-inventory-plan.md`), ordered by the user 2026-09-13:
> *"각 instrument library 확인하는게 필수겠다"*.
>
> **Status: FIRST PASS.** Everything here comes from a read-only byte scan of the running VI
> (`tools/bench/vi_inventory.py`, raw output in `docs/raw/main-vi-inventory.txt`) plus statements from the user.
> A byte scan recovers **names, not wiring** — it cannot say which subVI is called where, nor which port string
> actually reaches which session. Every row therefore carries its provenance, and the rows marked *inferred* are
> the ones the scripted inventory has to confirm.
>
> **The running code is the specification** (user, 2026-09-13: *"현재 가동되면 결국 그게 지금으로서는 최종"*).
> Where this document and anyone's memory disagree, the VI wins.

## The four instruments

## Driver attribution — settled from `instr.lib`, correcting an earlier guess

The user pointed at the SDK folder: *"insr.lib 인가? LabVIEW 2026 디렉토리 내부에 … 디펜던시 있는 기계 SDK들을
모아뒀어"*. That closed the question immediately, and **corrected an attribution I had made from VI names alone**.

`C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\` holds, among others:

```
ASI TG-1000        Mercury (PI GCS)        Autonics Motor        PZ-2150XYFT        CONEX
```

| subVI seen in the main VI | lives in | instrument |
|---|---|---|
| **`Configure.vi`, `SetCommand.vi`, `Close.vi`** | **`Autonics Motor\`** — the folder contains exactly these three | **ROTOR** |
| `MOV.vi`, `VEL.vi`, `GOH.vi`, `POS?.vi` | **`Mercury\GCS_LabVIEW\Low Level\General command.llb`** | magnet / Z motor |
| `Mercury_GCS_Configuration_Setup.vi` | `Mercury\GCS_LabVIEW\` | magnet / Z motor |
| `Initialize.vi`, `Move Axis to Position.vi`, `Move Axis Relative.vi`, `Get Current Position.vi` | `ASI TG-1000\Public\` | translation stage |

**What I had wrong:** `Configure.vi` and `Close.vi` were listed under the ASI stage and `SetCommand.vi` under PI,
purely because the names sounded like initialisation and command-sending. ASI TG-1000 has **no `Configure.vi` and
no `SetCommand.vi`** — those two names exist nowhere in `instr.lib` except the Autonics folder, so they are
unambiguous, and they are the rotor's.

**Why `MOV.vi` seemed to be missing:** it is inside a **`.llb`**, a single file holding many VIs, so a filename
search cannot see it. `find -name "MOV.vi"` returned nothing across the whole LabVIEW tree and briefly looked
like evidence of absence; a content search of the `.llb` files found it at once. Recorded because the same trap
will recur with any LabVIEW driver library.

## The rotor's command interface — `Autonics Motor\SetCommand.vi`

Read from the VI's own `Panel.Controls[]` (READ ONLY; the driver VI was never saved):

| # | terminal | direction | note |
|---|---|---|---|
| 0 | `VISA resource name` | **in** | the rotor's session — `ASRL5::INSTR`, alias `Rotor` |
| 1 | `Ring` | **in** | the operation: `MovePos` · `MovePosRel` · `Get Position` · `SetSpeed` |
| 4 | `Numeric` | **in** | the value the operation acts on |
| **8** | **`Baseline Startpoint`** | **in** | **this is the zero** — see below |
| 2 | `error in (no error)` | in | |
| 6 | `Pos_degree` | **out** | the position **in degrees** |
| 10 / 7 | `read buffer` / `read buffer 2` | out | the raw controller replies |
| 5 | `VISA resource name Out` | out | |
| 3 | `error out` | out | |

Internal comments in the same VI: **`Converting degree into pulse`**, `offset (0)`, `Mos Position (Absolute)`.

So the rotor is a **pulse-driven Autonics motor**, and `SetCommand.vi` is where degrees are converted to pulses.

### Where the rotor's zero lives — OPEN, and a claim of mine has been withdrawn

The user's recollection was: *"컨트롤러 절대좌표가 **아마** 음수를 지원 안해줬을거임. 그래서 임의로 중간지점을
내가 0으로 잡은 것 같은데"* — offered with "아마" and "기억이 정확하지 않으니까", i.e. explicitly uncertain.

I built on it as if it were settled and wrote that `Baseline Startpoint` **is** the zero, because "a pulse count
cannot be negative". **That is wrong, and the adversarial peer review (`archive/peer/2026-09-14-rotor-baseline-zero.md`)
dismantled it:**

1. **Autonics controllers do command negative positions.** The *serial* family — the relevant one here — is
   specified over **−8,388,608 … +8,388,607**
   ([PMC-1HS-232](https://www.autonics.com/in/model/PMC-1HS-232), [PMC-2HS-USB](https://www.autonics.com/in/model/PMC-2HS-USB)).
2. **The premise confused two different things.** Physical pulse *edges* are unsigned events; a *position
   coordinate* is signed. The controller expresses the sign as **pulse direction (CW/CCW)**, not as negative
   pulses. So there is nothing for a positive baseline to fix.
3. **"200 = turns" was the weakest part of all.** Nothing marks the unit; the companion input is named merely
   `Numeric`; the adjacent comment says *"Converting degree into pulse"*, so the local unit is **degrees**; and a
   200-turn midpoint would impose an arbitrary ±200-turn limit on a controller whose signed range is vastly
   larger. If the value is positional at all, **200 degrees is the more parsimonious reading**. And `offset (0)`
   reads more naturally as a zero offset than as a hidden 72,000° translation.

My earlier citation of the **PMC-4B-PCI** is also withdrawn: the user states this rig is **not** the 4B model,
and it is a PCI board while this rotor sits on a **USB serial port** (COM5 = FTDI FT232R, VID_0403/PID_6001 —
a generic chip that identifies nothing about the controller).

**Model: still unverified.** `PMC-1HS-232` / `PMC-2HS-USB` fit "serial", "not 4B", and an FTDI virtual COM port,
so they are the leading candidates — *candidates*, because guessing the model is precisely what went wrong once
already in this section.

**RESOLVED 2026-09-14: `Baseline Startpoint` is NOT on the connector pane, so the main VI never passes it.**

A full sweep of all 170 diagrams (`tools/bench/main_vi_netmap.json`, 635 nodes) finds **9 rotor call sites**, on
diagrams 24, 28, 32 ×2, 103, 107, 111 ×2 and 115. Every one exposes the **same seven** terminals:

```
error out · Pos_degree · VISA resource name Out · error in (no error) · Numeric · Ring · VISA resource name
```

`Baseline Startpoint` is absent from all nine — and the sweep **does** report unwired terminals (`Pos_degree` is
unwired at 8 of the 9 sites, `VISA resource name Out` at most of them), so its absence means it is **not a
connector-pane terminal at all**, not merely unconnected.

Cross-check from the driver's own panel: `SetCommand.vi` has **11** front-panel objects but only **7** appear at
a call site. The four that never leave the VI are `Baseline Startpoint`, `read buffer`, `read buffer 2` and
`*(type *) &x` — internal working values.

**Therefore the rotor's zero is fixed at the driver's saved default, `Baseline Startpoint = 200.0`**, and no
caller can change it. The unit is still not established (the peer argued degrees is the most parsimonious given
the neighbouring *"Converting degree into pulse"*); what IS established is that it is a constant of the driver,
identical at every call site.

One call site differs, and it is the read: **diagram 115, uid 34890** is the only one where `Pos_degree` is
**wired** — i.e. the only place the rotor's position is actually read back. The other eight only command.

**Other facts, unchanged:**

- `SetCommand.vi` converts degrees to pulses (its own comment).
- The user drives the rotor to **−7200°** (20 turns) and **−14400°** (40 turns) in practice.

**Method note.** Peer review had rejected "terminal names identify a subVI" because connector labels can repeat
across unrelated VIs — with the condition *"unless you have independently proved that signature unique across
every possible node in this VI"*. A complete sweep turns that condition into arithmetic, and the analysis
(`tools/bench/analyse_netmap_cache.py`) reports match counts rather than asserting identity: 1 match is called
unique-in-corpus, more than 1 is called ambiguous and concludes nothing. The method was validated independently:
it located the camera geometry node at **diagram 87 uid 9775**, which is exactly the node found on 2026-09-12 by
a completely different route (a 106-property-node census cross-referenced by UID), with the same `Height`-before-
`Width` terminal order that an offline byte scan had also shown. Three independent methods, one answer.

**What is NOT established, and is not to be guessed:** what `Baseline Startpoint` means, what unit `200.0` is in,
whether the main VI overrides it, and therefore where the zero is. A peer review was dispatched specifically to
attack this reading (`archive/peer/2026-09-14-rotor-baseline-zero.md` — the exchange is dated **09-14**, not 09-13;
path corrected 2026-09-16, `doc_lint` L2 dangling citation).

### And this does not block the work — the configuration is carried over, not re-derived

The user's instruction on this, 2026-09-13: *"애초에 configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야?
확실히 모르잖아."*

Correct, and it makes the open question harmless. The rotor row of the scheduler does **not** need the semantics
of `Baseline Startpoint`. It needs to call `SetCommand.vi` **exactly as the working `Send to Rot` path already
does** — same subVI, same `Baseline Startpoint` source, same `Ring` setting — with only the commanded value
coming from the schedule instead of the panel. That is correct by construction and leaves the unknown constant
unknown *and unchanged*, which is what rule 1a requires anyway.

So the trace that still matters is narrow and it is about **copying**, not understanding: which source feeds
`Baseline Startpoint` and `Ring` on the existing call, so the new call can be fed identically.

Also to correct in `docs/rotor-scheduler-design.md`: that document treats `Pos_degree` as the input the schedule
writes. **`Pos_degree` is an OUTPUT.** The value goes in through `Numeric`.

## The four instruments

| instrument | hardware | driver VIs found in the file | **port on THIS machine** | provenance |
|---|---|---|---|---|
| **Camera** | JAI SP-5000M-USB, IMAQdx name `cam1`, serial `000014FB0067A270` | `IMAQdx Open Camera.vi` ×3, `IMAQdx Configure Grab.vi` ×3, `IMAQdx Grab.vi` ×3, `IMAQdx Get Image.vi` ×6, `IMAQdx Stop Acquisition.vi` ×3, `IMAQdx Close Camera.vi` ×3 | — (IMAQdx name, not a COM port) | re-measured 2026-09-14 via the C API |
| **Magnet / Z motor** | **PI M-126.PD1** (Mercury GCS) | `MOV.vi` ×12, `VEL.vi` ×9, `GOH.vi` ×7, `Mercury_GCS_Configuration_Setup.vi` ×6 | **`ASRL3::INSTR` = COM3**, NI MAX alias **`PI`** (SUNIX COM Port) | NI-VISA enumeration + `instr.lib`, 2026-09-14 |
| **Translation stage / piezo** | ASI TG-1000 | `Initialize.vi` ×4, `Move Axis to Position.vi` ×9, `Move Axis Relative.vi` ×3, `Get Current Position.vi` ×7, `Max Trans Pos.vi` ×7 | **`ASRL4::INSTR` = COM4**, NI MAX alias **`ASI_Piezo`** (SUNIX COM Port) | NI-VISA enumeration + the 2026-09-12 round-trip measurement on COM4, which agrees |
| **Rotor** | **Autonics motor, pulse-driven** | **`Configure.vi` ×6, `SetCommand.vi` ×11, `Close.vi` ×6** — the whole `Autonics Motor` library | **`ASRL5::INSTR` = COM5**, NI MAX alias **`Rotor`** (USB Serial Port) | `instr.lib` + `Pos_degree` found inside `Autonics Motor\SetCommand.vi`; matches the user's *"로터는 별도의 입력으로 움직임. ASI도 아니고 PI도 아님"* |
| *(unassigned)* | — | — | `ASRL6::INSTR` = COM6, alias `COM6` (USB Serial Port) | NI-VISA enumeration |

Three distinct NI MAX aliases — `PI`, `ASI_Piezo`, `Rotor` — independently confirm the user's statement that the
rotor is a third device with its own input.

## CORRECTION: the four port strings in the VI are NOT this machine's configuration

The first pass of this document listed the motor as COM4/COM5 and the rotor as COM3/COM2, taken from strings in
the file, and called them "per-room configuration pairs". **That was wrong**, and the user caught it in one line:

> *"로터에 컴포트 두개가 잡힐 수가 없지. 다시 확인해보라고..."*

A device has one port. What the strings actually are becomes clear from **where they sit** — the byte scan's flat
alphabetical list hid it, but a context dump shows all four consecutive in one block, interleaved with two
interface names:

```
[3460] '"WUSB'                     <- interface option A
[3461] 'M-126.PD1, COM4 9600'
[3462] 'Rot, COM3 9600'
[3463] 'RS-232'                    <- interface option B
[3464] 'M-126.PD1, COM5 115200'
[3465] 'Rot, COM2 115200'
```

So they are the **item list of a selection ring** — two interface options, each naming one motor port and one
rotor port. Not two ports per device.

And the cross-check the user asked for (*"필요하면 NI Max 들어가서도 확인해서 LabVIEW 상수하고 비교해보도록 하고"*)
settles it: **none of those four strings is an alias on this machine.** NI-VISA reports `PI`, `ASI_Piezo`, `Rotor`
and `COM6`. The ring's labels therefore describe some other machine or an earlier setup — they are exactly the
kind of legacy leftover the user warned about — and reading them as the live configuration was the error.

The front-panel note *"Parameters that we need to change for each imaging room"* does list `Com port/rate`, so a
per-room selection genuinely exists; that note explains why a ring is there, not what it currently holds.

**Still open, and it is a diagram read, not an inference:** which value the configuration section's constants
actually pass to each VISA session — the alias (`Rotor`), a raw resource (`ASRL5::INSTR`), or a port string. The
user has said these are constants in the configuration code; `OpReportSubVI_v0` is being built to locate that
section, after which the constants get read directly.

## Method note, because this mistake is worth not repeating

A **sorted list of extracted strings destroys the adjacency that carries the meaning.** Four names that look like
four configurations turned out to be two, the moment their order was preserved. Any future byte-scan finding gets
its context dumped (`tools/bench/vi_string_context.py`) before it is written into a document, and anything about
instrument identity gets cross-checked against the machine (`tools/bench/visa_aliases.py`) rather than against
the file alone.

## Camera state, re-measured 2026-09-14

```
cam1  1280 x 1024, binning 2x2, 90.00 Hz          <- FULL frame right now, not halved
WidthMax  2560 / binning 2 = 1280
HeightMax 2048 / binning 2 = 1024
FrameRateRaw period 4033..8000000 us  ->  CEILING 247.95 Hz   (floor 0.125 Hz)
Width  range (8, 1280, 8)     Height range (8, 1024, 2)
```

Unchanged from 2026-09-12, and it resolves an apparent contradiction: the front panel displays `Width 640`,
`Height 512`, but **`Width` and `Height` are INDICATORS** (`docs/main-vi-panel-map.md`), so they show what the
*last run* ended with, not what the code sets. `IMAQdxOpenCamera` resets the ROI, so each run starts full-frame.
No conflict, and nothing to restore.

**Open:** the panel's `Frame rate` is a CONTROL holding **25**, while the camera runs at **90 Hz**. Either it is
not the camera's frame rate, or it is not wired to the camera. Not guessed either way.

**A non-result, logged rather than dropped:** the full 80-attribute dump (`imaqdx_ctypes.py`) hung and was killed
by its 8-minute deadline after printing only `DeviceVendorName`. The targeted reader (`imaqdx_limits.py`)
returned everything above in 10 s. The half-finished attribute list was discarded, not used.

## The rotor — what is known and what is not

**Known (user):** the rotor is driven by a separate input of its own; it is neither the ASI library nor the PI
library. Its configuration is in the main VI's startup section.

**Known (byte scan + front panel):** `RotationVISA` is a front-panel refnum indicator (tab index 100), so the
rotor holds its **own VISA session**, separate from the stage's and the motor's. Related panel objects:
`Rot step (turns)` (16), `Rot pos (deg)` (18), `Auto-reset zero` (40), `Current pos rot?` (45), `1 L-Turn` (70),
`1 R-Turn` (71), `Rot Step (deg) ` (72), `Rot \nSpeed` (73), `Send to Rot` (74), `TurnOff` (104).

**Not known, and not to be guessed:**
- which VI or raw VISA write actually sends the rotor command;
- the command syntax;
- **where zero is** — see `docs/rotor-scheduler-design.md`. The user's reasoning stands: the controller's
  absolute coordinate probably cannot go negative, yet `−7200` is typed and the rotor turns 20 times, so the main
  VI must add an offset, and that offset *is* the zero.

**The decisive test, and it is the user's own suggestion** (*"자체 dll에서 주는 값을 믿는게 가장 확실하지 않나?"*):
read the position the controller itself reports and compare it with what `Rot pos (deg)` displays. The difference
is the offset. A 360° turn afterwards separates a pure offset from an offset-plus-scale. No wire tracing needed to
get the number — the trace is only needed afterwards, to know which node to move during the restructuring.

## Full subVI list — 58 names

Grouped by role. Counts are occurrences in the file, **not call-site counts** — a byte scan cannot count calls.

**Camera / image:** `IMAQdx Open Camera` · `IMAQdx Configure Grab` · `IMAQdx Grab` · `IMAQdx Get Image` ·
`IMAQdx Stop Acquisition` · `IMAQdx Close Camera` · `get buff image-lost frames.vi`

**Tracking kernel:** `Track N beads four-fold over-kernel-v3.vi` · `check N bead pos v3-kimlab.vi` ·
`choose bandpass v2.vi` · `make both cosine bandpass.vi` · `rect coord from center.vi`

**Calibration:** `calibration- generate 1 I of r, reentrant.vi` · `calibration- generate 2 I of r, reentrant.vi` ·
`build cal image.vi` · `prep cal image.vi` · `proc cal image-make bandpass.vi` · `exp-ref management.vi`

**Motion:** `MOV.vi` · `SetCommand.vi` · `VEL.vi` · `GOH.vi` · `Mercury_GCS_Configuration_Setup.vi` ·
`Move Axis to Position.vi` · `Move Axis Relative.vi` · `Get Current Position.vi` · `Configure.vi` ·
`Initialize.vi` · `Close.vi` · `Max Trans Pos.vi` · `ASI_adjust focus-subvi.vi` ·
`Motor control v5_No Recording.vi` · `SiHyeong Modified Motor control v5_No Recording.vi`

**Shared state:** `Global motor pos.vi` ×9 — the VI Global the restructuring's one-writer-per-field contract is
built on.

**Force / physics:** `Magnet2Force v3_for M270.vi` · `WLC function sub.vi`

**Display:** `Draw Circle by Radius.vi` · `Draw Flattened Pixmap.vi` · `Draw Grayed Out Rect.vi` ·
`Draw Text at Point.vi` · `Flatten Pixmap.vi` · `grayscale color table.vi` · `N bead plot Z.vi` ·
`N bead plot dZ.vi` · `Set Cursor.vi` · `Set Cursor (Icon Pict).vi`

**Filtering:** `FIR Filter.vi` · `FIR Filter (DBL).vi` · `Median Filter.vi` ·
`Smoothing Filter Coefficients.vi` (`3filter.llb`)

**File / error:** `save N xyz traces.vi` · `save trace.vi` · `Simple Error Handler.vi`

Note `Motor control v5_No Recording.vi` and `SiHyeong Modified Motor control v5_No Recording.vi` both appear —
a lab-member-modified variant alongside the base. Which one is actually wired is a question for the scripted
inventory; **the presence of a name proves nothing about use**, and the user has said outright that unwired
legacy leftovers exist in this VI.

## What the next pass must add

1. **Call sites** — which diagram each subVI is called from, so the instruments can be attributed to loops.
2. **Which port string is live**, and what the startup configuration block actually sets.
3. **The rotor's command path** — the VI or VISA write behind `Send to Rot`, and the offset applied to
   `Rot pos (deg)`.

These need `OpReportSubVI_v0` (`SubVI.VI Name` 635E401 / `VI Path` 635E403 as arrays), which is the first tool in
`docs/system-inventory-plan.md`.

### Measured 2026-09-14 19:5x on the driver copy (INDEX row 31) — facts that were unreadable this morning

- `Ring` 2 = **Get Position** (the only frame with a VISA Read); the reply `POS hhhhhhhh[CR]` is trimmed to its 8 hex
  digits (String Subset window [4, 8]) and parsed by `Hexadecimal String To Number` — U32 by default, hence the sign
  bug; fixed on `claudeDev\SetCommand_signed.vi` (parse, then Type Cast the number to the signed type).
- Scale **k = 0.72 °/pulse = 500 pulses per turn**; `Pos_degree = k·pulses − 360·Baseline Startpoint`, so
  **`Baseline Startpoint` is in TURNS** (default 200 = a +100 000-pulse offset in the controller coordinate).
- `PAB` moves take a signed decimal pulse count (manual); the position range is ±8 388 607 pulses = ±16 777 turns.
- **Hardware facts 20:2x (`tools/bench/hw_rotor_read.log`, query only, no motion):** the controller is a **two-axis
  PMC-2HS** — the reply is `POS 000186A0,00000000[CR]` (X = 100 000 pulses = exactly the +200-turn baseline, Y = 0);
  the driver's substring [4, 8] takes the X field. **The first VISA Read after `Configure.vi` times out (2 s, empty)
  whichever VI asks, and the late reply is consumed by the next read** — an ordering artefact of opening the port:
  issue one dummy query (or a flush) after Configure before trusting a read. After that, `SetCommand_signed.vi` and
  the original read identical values on the real rotor.
- **20:22:** signed read accepted on hardware (`CLL X`, `PIC ±10`, INDEX row 31). `claudeDev\RAWCMD_rotor.vi` sends any
  raw command string over the alias; the rotor's active counter is now **0** (the +200-turn convention is gone until
  `PIC 100000` restores it — only needed if the original main VI runs again).
