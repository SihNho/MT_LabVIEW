---
type: peer-review
status: historical
date: 2026-09-18
tags: [peer-review, archive, labview]
disposition: legacy
legacy_note: closed as legacy 2026-09-25 by card chat-L1 (cutoff 2026-09-22; user 2026-09-25 lint order before runner resume)
---

# asi-soft-limits-sl-su

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-18 14:50:49
- **outcome:** ANSWERED (97s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

API FACT question (web search required). ASI (Applied Scientific Instrumentation) stage controller, serial ASCII
protocol (MS-2000 / Tiger command set; replies ':A'), axes X Y Z; WHERE/MOVE units are tenths of microns. Today the
stage sits at X=-18475 Y=-27744 (units) and the safe window is +-1.0 mm around that in X/Y; Z is free.

Question: can SOFTWARE LIMITS be set INSIDE the ASI controller so that any MOVE/MOVREL beyond them is refused or
clamped regardless of which host sends it?
1. Exact commands and syntax: SETLOW (SL) / SETUP (SU)? e.g. `SL X=-2.85 Y=-3.77`, `SU X=-0.85 Y=-1.77` - what UNITS
   do SL/SU take (mm? tenths of microns?) and how are they queried (`SL X? Y?`)?
2. Behaviour on an out-of-limit MOVE: refused with an error code (:N-?) or clamped to the limit? Does MOVREL behave
   the same? Does the limit apply to HOME (!) and joystick motion?
3. Volatile vs persistent: are SL/SU values lost at power-cycle unless saved with SAVESET (SS Z)? What else does SS Z
   save? Is there a way to save only these? What restores factory values (SS X?)?
4. Are the limits tied to the current coordinate zero (i.e. would HERE / ZERO / H shift them)?
5. Any differences between MS-2000 and Tiger (TG-1000) firmware for these commands.
Cite ASI's command documentation pages (asiimaging.com/docs/commands/...). No project files needed.


## Answer

Yes. `SETLOW`/`SETUP` create controller-side firmware limits, so ordinary serial `MOVE`/`MOVREL`, HOME, and manual joystick motion cannot continue through them. They protect against different hosts issuing motion commands, but they are configurable—not a tamper-proof or safety-rated interlock.

1. Commands, units, and your exact window

`SL` and `SU` use **millimetres**, regardless of the tenths-of-microns normally used by `MOVE`, `MOVREL`, and `WHERE`. Queries use `?` after each axis. [ASI SETLOW](https://docs.asiimaging.com/commands/setlow), [ASI SETUP](https://docs.asiimaging.com/commands/setup), [ASI command quick start](https://docs.asiimaging.com/command_quick_start)

Your coordinates and ±1.0 mm limits are:

| Axis | Current position | Lower limit | Upper limit |
|---|---:|---:|---:|
| X | −1.8475 mm | −2.8475 mm | −0.8475 mm |
| Y | −2.7744 mm | −3.7744 mm | −1.7744 mm |

Exact commands:

```text
SL X=-2.8475 Y=-3.7744
SU X=-0.8475 Y=-1.7744
```

Queries:

```text
SL X? Y?
SU X? Y?
```

Typical responses would be shaped like:

```text
:A X=-2.8475 Y=-3.7744
:A X=-0.8475 Y=-1.7744
```

Your rounded example (`-2.85`, etc.) is valid but moves the boundaries by up to 2.5 µm.

Important: ASI warns that on an axis configured with negative direction, the logical interpretation is reversed: the upper limit may need to be negative and the lower positive. Query the existing limits and confirm the stage’s coordinate/direction convention before relying on the numerical ordering. Also, `SL >= SU` is documented as causing incorrect operation. [ASI SETLOW notes](https://docs.asiimaging.com/commands/setlow), [ASI SETUP notes](https://docs.asiimaging.com/commands/setup)

2. What happens beyond a limit

The documentation describes a **motion stop/prohibition**, not rejection of the ASCII command:

- A correctly parsed `MOVE` or `MOVREL` normally receives `:A`; that only means the command was received, not that motion completed. The motor stops when a limit is encountered. [ASI MOVE](https://docs.asiimaging.com/commands/move), [ASI MOVREL](https://docs.asiimaging.com/commands/movrel)
- The MS-2000 operating documentation says that at a hardware or software limit, `U` or `L` appears and “further movement into the limit is prohibited.” This also describes manual-control operation. [ASI MS-2000 operation](https://docs.asiimaging.com/ms2000_operation)
- `HOME !` explicitly stops when it encounters either a hardware or firmware limit. Its default HOME target is far beyond positive travel, so the upper limit normally terminates it. [ASI HOME](https://docs.asiimaging.com/commands/home)

Therefore, the documented model is:

- The target command is generally **accepted with `:A`**, rather than refused with `:N-4` or another syntax error.
- Physical motion stops at the firmware boundary.
- ASI does **not clearly promise that the stored target is rewritten/clamped** to the limit value. Treat it as “motion stops on encountering the limit,” not as a guaranteed target-value clamp.
- `MOVREL` is subject to the same axis limit mechanism.
- HOME and joystick/knob movement are also limited.

`:N-*` codes are command/parser or operation errors; ASI does not document a special `:N-*` response for an otherwise valid target beyond SL/SU. [ASI error codes](https://docs.asiimaging.com/error_codes)

3. Persistence and `SAVESET`

The current SL/SU pages say the limits are **automatically remembered across power cycles** and do not require `SAVESET`. [ASI SETLOW](https://docs.asiimaging.com/commands/setlow), [ASI SETUP](https://docs.asiimaging.com/commands/setup)

There is an important MS-2000 legacy/persistence nuance:

- `SAVEPOS` says axis positions and soft-limit locations are normally saved during the controller’s power-down save operation.
- For MS-2000 firmware 6.1u and later, its note says limit settings are saved only if `SAVEPOS` is issued after `SAVESET Z`. This wording is awkward alongside the newer “automatically remembered” wording, so for an older MS-2000 I would not infer an exact required sequence without checking its firmware version with `VERSION` or asking ASI. [ASI SAVEPOS](https://docs.asiimaging.com/commands/savepos), [ASI SAVESET](https://docs.asiimaging.com/commands/saveset), [ASI VERSION](https://docs.asiimaging.com/commands/version)

`SS Z` is a **bulk save of current configurable parameters to flash**, not a limit-only save. Many commands whose pages say “Remembered: Using SS Z” are included; there is no documented `SAVESET` operation that saves only SL/SU. [ASI SAVESET](https://docs.asiimaging.com/commands/saveset)

The `SAVESET` meanings are:

```text
SS Z    save current parameter settings to flash
SS X    arrange to load factory defaults at the next power-up
SS Y    restore the previously saved settings after SS X
```

`SS X` is broad and should not be used merely to reset limits. On supported firmware, reset only an individual limit with:

```text
SL X-
SU X-
```

Likewise for Y. `SL axis-`/`SU axis-` restore that limit’s default; the operand syntax appeared in Tiger v2.8 and approximately 2013-era MS-2000 firmware. [ASI SETLOW](https://docs.asiimaging.com/commands/setlow), [ASI SETUP](https://docs.asiimaging.com/commands/setup)

4. Effect of HERE/ZERO

The boundaries are tied to **fixed physical stage locations**, not permanently to particular displayed coordinate numbers. When `HERE`, `ZERO`, or `H` changes the coordinate system, the controller adjusts the numerical SL/SU values so that the protected physical locations remain unchanged. [ASI SETLOW](https://docs.asiimaging.com/commands/setlow)

So zeroing the coordinates should not physically move the safe window. Query `SL` and `SU` afterward if software needs their new coordinate values.

5. MS-2000 versus Tiger

For normal motor axes, the essential behavior and units are the same:

- Both use `SL axis=<millimetres>` and `SU axis=<millimetres>`.
- On Tiger these are classified as **axis-specific** commands; the axis name routes the command. `MOVE`, `MOVREL`, and other common axis-specific commands are intentionally similar between the platforms. [ASI SETLOW](https://docs.asiimaging.com/commands/setlow), [ASI command quick start](https://docs.asiimaging.com/command_quick_start)
- `SL axis+` sets the lower limit to the current position; `SL axis-` restores its default. This requires Tiger v2.8 or later and roughly 2013-or-newer MS-2000 firmware. [ASI SETLOW](https://docs.asiimaging.com/commands/setlow)
- `SU axis+` is documented from Tiger v2.8; `SU axis-` restores its default. [ASI SETUP](https://docs.asiimaging.com/commands/setup)
- Use `SU`, not the old `SH` alias. `SH` was deprecated in MS-2000 v9.50 and Tiger v3.50. [ASI SETUP](https://docs.asiimaging.com/commands/setup)
- Tiger’s card-address prefix is required for card-addressed commands such as `SAVESET` (`1SS Z`), but SL/SU are axis-specific rather than card-addressed. [ASI SAVESET](https://docs.asiimaging.com/commands/saveset)

Bottom line: your proposed protection is the right controller-side mechanism for `MOVE`/`MOVREL`, including commands from another host. Use the exact millimetre bounds above, query them back, and do not treat the absence of an `:N-*` reply as evidence that an out-of-window target was allowed—the limit normally acts during motion.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
