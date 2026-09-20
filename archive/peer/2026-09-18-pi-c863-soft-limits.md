# pi-c863-soft-limits

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-18 14:45:52
- **outcome:** ANSWERED (236s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API FACT question (web search required). Controller: Physik Instrumente C-863.11 Mercury (IDN reply
'(c)2013 Physik Instrumente(PI) Karlsruhe, C-863.11,0,1.3.0.7'), GCS 2.0 over serial, one axis '1'. Measured today:
TMN? = 0, TMX? = 52, so the controller's travel range is 0..52 mm, but the rig is only safe for 0..39 mm.

Question: can a SOFT LIMIT (upper and lower position limit) be set INSIDE the C-863.11 controller itself, so that
any MOV beyond it is refused/clamped by the controller regardless of which software sends it (LabVIEW, PIMikroMove,
our scripts)? Specifically:
1. Do the GCS commands NLM / PLM (or SPA parameters 0x15 "max position" / 0x30 "min position", or others) exist on
   the C-863.11 firmware 1.3.x, and what exact syntax sets the limits for axis 1 (e.g. `PLM 1 39.0`, `NLM 1 0.0`)?
2. Does setting them need the command level CCL 1 with the password (`CCL 1 advanced`)? Are they volatile (lost at
   power-cycle) unless written with WPA (`WPA 100`)? What does WPA overwrite?
3. Behaviour: is a MOV beyond the limit refused with an error (ERR? code) or clamped? Does TMN?/TMX? change to
   reflect them?
4. Can the same be set from PI's own GUI (PIMikroMove) or the PI GCS DLL / Python (pipython) as an alternative to
   raw serial?
5. Any caveats: interaction with reference switch (FRF), servo, or the 40.94 mm value LabVIEW uses.
Cite PI's C-863 user manual / GCS commands manual pages or URLs. No project files needed.


## Answer

Yes. The C-863.11 can enforce a controller-side `0…39 mm` window for closed-loop motion. For this controller, the documented interface is through parameters `0x15` and `0x30`, not the generic `PLM`/`NLM` commands.

### 1. Commands and exact syntax

Use:

```text
SPA 1 0x15 39.0
SPA 1 0x30 0.0
```

Then verify:

```text
SPA? 1 0x15
SPA? 1 0x30
TMN? 1
TMX? 1
```

Expected final queries:

```text
1=0.000...
1=39.000...
```

For the C-863:

- `0x15` = maximum commandable position in the positive direction.
- `0x30` = minimum commandable position in the negative direction.
- `TMX?` reports the limit defined by `0x15`.
- `TMN?` reports the limit defined by `0x30`.
- These limits apply to closed-loop moves and follow the current position-zero coordinate system. [C-863 manual, “Travel Range and Soft Limits”](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

`NLM` and `PLM` are generic GCS/DLL commands, but they are not included in the C-863.11 command list in the model-specific manual. The generic DLL manual explicitly says a DLL function is usable only when the controller supports the corresponding command. Therefore I would not use `NLM 1 0` or `PLM 1 39` on this firmware; use `SPA` instead. A harmless definitive check on the actual unit is whether `HLP?` lists `NLM` or `PLM`. [PI GCS DLL manual: `PI_NLM`](https://www.physikinstrumente.com/en/?downloadEnded=1&downloadFileUid=1309&downloadUid=1445&type=5600), [PI GCS DLL manual: `PI_PLM`](https://www.physikinstrumente.com/en/?downloadEnded=1&downloadFileUid=1309&downloadUid=1445&type=5600)

### 2. Command level and persistence

`CCL 1 advanced` is not required for `0x15` or `0x30` on the documented C-863 parameter set. Do not confuse the CCL password `advanced` with the nonvolatile-memory password `100`. The latter belongs to `WPA`/`SEP`. [PI C-863 parameter documentation](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f), [PI GCS DLL command-level documentation](https://www.physikinstrumente.com/en/?downloadEnded=1&downloadFileUid=1309&downloadUid=1445&type=5600)

`SPA` changes RAM only. Its values are lost on power-cycle, reboot, or an `RPA` restore. To persist only these two parameters, use the targeted form:

```text
WPA 100 1 0x15
WPA 100 1 0x30
```

The C-863 accepts only one parameter per targeted `WPA` command. Avoid bare:

```text
WPA 100
```

unless intentionally saving the entire current parameter set: with no item/parameter arguments it copies every parameter covered by password `100` from RAM into nonvolatile memory, potentially preserving unrelated experimental PID, velocity, acceleration, stage-scaling, and other settings. PI also warns that EEPROM write cycles are limited. [C-863 `WPA` documentation](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

Persistent values can be checked without rebooting:

```text
SEP? 1 0x15
SEP? 1 0x30
```

### 3. Out-of-range behavior

It is refused, not clamped. For example, after setting `0…39`, this:

```text
MOV 1 40.94
ERR?
```

should leave the axis stationary and return:

```text
7
```

Error `7` is `PI_CNTR_POS_OUT_OF_LIMITS`. The C-863 manual’s own out-of-range `MOV` example explicitly says the axis does not move. [C-863 `MOV` example and error behavior](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

`TMN? 1` and `TMX? 1` will immediately reflect the active RAM values. They can also shift if the coordinate zero is changed—for example by `DFH`—because `0x15`/`0x30` are relative to the current zero. [C-863 `TMN?`/`TMX?` and `DFH` documentation](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

### 4. PIMikroMove, DLL, and PIPython

PIMikroMove can do this without raw serial:

1. Open the expanded Single Axis Window.
2. Add parameters `0x15` and `0x30` using “Select parameters…”.
3. Enter `39.0` and `0.0` in the active-value fields.
4. Verify operation.
5. Use `C-863 > Save parameters to non-volatile memory` and password `100`.

Be aware that this GUI save operation is described as saving the updated parameter set, so targeted raw `WPA` commands are preferable when you want to guarantee that only these two parameters are committed. [C-863 PIMikroMove parameter procedure](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

The GCS DLL equivalents are `PI_SPA()` and targeted `PI_WPA()`. Although the DLL also exposes `PI_NLM()` and `PI_PLM()`, that does not mean every controller implements those commands. [PI GCS DLL `PI_SPA` and `PI_WPA`](https://www.physikinstrumente.com/en/?downloadEnded=1&downloadFileUid=1309&downloadUid=1445&type=5600)

With PIPython, the least ambiguous controller-specific method is:

```python
pidevice.send("SPA 1 0x15 39.0")
pidevice.send("SPA 1 0x30 0.0")

pidevice.send("WPA 100 1 0x15")
pidevice.send("WPA 100 1 0x30")
```

PIPython supports both wrapped GCS methods and sending textual GCS commands; its normal error checking queries `ERR?` and raises `GCSError`. [Official PIPython repository](https://github.com/PI-PhysikInstrumente/PIPython)

### 5. Important caveats

- The `0x15`/`0x30` limits protect closed-loop commands such as `MOV`, `MVR`, `GOH`, and `STE`. They are not the appropriate protection for open-loop `SMO` motion. The separate parameters `0x07000000` and `0x07000001` stop motion at limits in both open- and closed-loop operation, but do so abruptly and are intended principally for open-loop protection. [C-863 description of both soft-limit pairs](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

- Reducing `0x15`/`0x30` inside the physical end switches prevents using those end switches for `FNL`/`FPL` reference moves. `FRF` using the reference switch remains the intended method, provided its assigned reference position (`0x16`) lies inside the new window. Reference moves require servo-on. [C-863 referencing restrictions](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

- If LabVIEW continues issuing `MOV 1 40.94`, the controller will reject it with error 7; it will not silently substitute `39`. LabVIEW must therefore handle that error or have its own maximum changed consistently.

- Loading or selecting a stage definition in PI software can load stage-database parameters into volatile controller memory, including the normal travel parameters. Recheck `TMN?`/`TMX?` after changing or reloading the stage configuration. [C-863 stage-database behavior](https://device.report/m/6166469034393f2ff298a2efbd5ebbbafaf59e98c22333169363c27049d60a4f)

Bottom line: use `SPA 1 0x15 39.0` and `SPA 1 0x30 0.0`, verify through `TMN?`/`TMX?`, then persist each parameter separately with targeted `WPA 100` commands. This gives controller-side rejection of any closed-loop `MOV` above 39 mm, independent of which host application sent it.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
