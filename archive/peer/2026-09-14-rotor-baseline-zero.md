---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, rotor]
---

# rotor-baseline-zero

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (90s)
- **why asked:** See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
- **verdict:** see 'What was done with it' / STATUS.md 2026-09-14

## Question

ATTACK this reading of a LabVIEW instrument driver, do not confirm it. CONTEXT: magnetic-tweezers rig. The ROTOR is an Autonics motor on COM5 (NI-VISA alias 'Rotor', ASRL5::INSTR). Its driver is LabVIEW 2026 instr.lib\Autonics Motor\, containing exactly three VIs: Configure.vi, SetCommand.vi, Close.vi. SetCommand.vi front-panel terminals read from Panel.Controls[]: INPUTS 'VISA resource name', 'Ring' (items MovePos | MovePosRel | Get Position | SetSpeed), 'Numeric', 'Baseline Startpoint'; OUTPUTS 'Pos_degree', 'read buffer', 'read buffer 2', 'VISA resource name Out'. Internal diagram comments include 'Converting degree into pulse' and 'offset (0)' and 'Mos Position (Absolute)'. The saved DEFAULT of 'Baseline Startpoint' is 200.0. MY CLAIM, which I want attacked: 'Baseline Startpoint' is the software zero-offset - the user types negative degrees (they report -7200 deg = 20 turns and also -14400 deg = 40 turns actually moving the rotor), a pulse count cannot be negative, so the driver adds a baseline before converting degrees to pulses; and 200.0 is a midpoint expressed in TURNS (200 turns = 72000 deg), so +/-14400 deg maps to 160..240 turns, all positive. FIND WHY THIS IS WRONG: (a) what do Autonics motion controllers (PMC-1HS/2HS, PMC-4B-PCI, AiC/AiS series, MD5-HF14 etc) actually accept over serial - absolute position in pulses, can it be negative, what is the position range and is there a documented origin/home offset? (b) is 'Baseline Startpoint' more plausibly something else entirely - a speed ramp start, an acceleration baseline, a home-search start point? (c) could 200.0 be degrees, pulses, turns, or a percentage? (d) is it likely the MAIN VI overrides this default anyway, making the 200.0 irrelevant? Cite Autonics manuals or NI forum threads. Note I have NOT yet traced what the main VI wires into this terminal.

## Answer

The central premise is wrong: Autonics controllers can represent and command negative positions. A ?쐏ulse count cannot be negative??confuses physical pulse edges?봶hich are unsigned events?봶ith a signed position coordinate or signed displacement.

### Strongest counterevidence

The serial-capable PMC-1HS/2HS explicitly supports:

- absolute and incremental positioning;
- a signed position range of **??,388,608 to +8,388,607**;
- pulse scaling.

That is stated directly in Autonics??specifications for both the [PMC-1HS-232](https://www.autonics.com/in/model/PMC-1HS-232) and [PMC-2HS](https://www.autonics.com/in/model/PMC-2HS-USB). Thus `-7200째` can be converted to a negative controller coordinate without adding any positive baseline.

The PMC-4B-PCI likewise supports absolute/incremental positioning and signed coordinates from **??,147,483,648 to +2,147,483,647** per axis. [Autonics PMC-4B-PCI specifications](https://www.autonics.com/kr/model/PMC-4B-PCI).

Internally, the controller realizes the sign through pulse direction?봲uch as CW versus CCW?봭ot through ?쐍egative electrical pulses.??The MD5-HF14 is only a pulse-input motor driver, accepting separate CW/CCW inputs; it is not itself a COM-port positioning controller. [Autonics MD5-HF14 specifications](https://www.autonics.com/glb/model/MD5-HF14-AO). Autonics describes the PMC controller as the positioning device used with pulse-input stepper/servo systems, while MD5 is the downstream driver. [PMC-1HS/2HS manual](https://s3.iautomatica.ru/uf/3cb/fujhb1pl558c4ozmuf7n1uuim22u67km/PMC-1_2HS_EN_User_DRW170814AF_20190424_W.pdf).

Therefore:

```text
signed coordinate ?묿 pulses
        ??controller selects negative direction
        ??driver receives N physical pulses on CCW/direction input
```

There is no need for a 200-turn bias.

### Why ??00 turns??is particularly weak

Nothing supplied establishes that `Baseline Startpoint` is measured in turns. In fact, several clues argue against it:

- The companion motion argument is named `Numeric`, not ?쐔urns.??- The diagram says ?쏞onverting degree into pulse,??suggesting the local engineering unit is degrees.
- A value of `200.0` carries no unit metadata merely because it is a LabVIEW DBL.
- The documented PMC position ranges are already signed, so a midpoint translation is unnecessary.
- A 200-turn midpoint would permit only 짹200 turns before crossing zero, despite the controller having vastly larger signed ranges. It would be an arbitrary software restriction with no evident controller rationale.

The claimed mapping also requires an unobserved formula such as:

```text
command pulses = (Baseline Startpoint + requested_degrees / 360) 횞 pulses_per_turn
```

The comments you have?붴쏞onverting degree into pulse,???쐎ffset (0),??and ?쏮os Position (Absolute)?앪봡o not establish that formula. In particular, ?쐎ffset (0)??may actually suggest a zero offset rather than a hidden 72,000째 translation.

If `200.0` is positional, **200 degrees** is more parsimonious than 200 turns because the adjacent command conversion explicitly mentions degrees. If it is 200 pulses, its angular meaning depends entirely on the configured pulse resolution: MD5-family systems can use resolutions as fine as 125,000 pulses/revolution, while AiS models expose several selectable PPR values. [Autonics MD5 series](https://www.autonics.com/in/series/MD5), [Autonics AiS example specifications](https://www.autonics.com/in/model/AiS-42LA-B). Consequently, ??00 pulses??has no fixed physical angle without hardware settings.

A percentage interpretation has the least support: Autonics position commands, initial speeds, acceleration parameters, and pulse scaling use pulses, pps, rates, or time?봭ot a generic percentage in the documented motion interface.

### Is it a speed-ramp parameter?

This is a credible competing hypothesis, but not established.

PMC controllers have a documented **Start Speed**/initial-speed parameter used at the beginning and end of acceleration/deceleration. It is expressed through a speed multiplier and ultimately in pulses per second. The documented configuration includes start speed, drive speed, acceleration rate, and deceleration rate. [PMC-1HS/2HS manual](https://s3.iautomatica.ru/uf/3cb/fujhb1pl558c4ozmuf7n1uuim22u67km/PMC-1_2HS_EN_User_DRW170814AF_20190424_W.pdf). Another Autonics manual describes Start Speed as the start/end speed of an acceleration drive, with a selectable value of 1??,000 and a factory default of 50?봭ot 200. [Autonics PMC manual](https://idom.ru/wp-content/uploads/PMC-2HSN_2HSP_EN_User_180821_W.pdf).

Thus 200 could plausibly be a locally chosen starting speed or ramp-related value. However, two details weaken that interpretation:

- `SetSpeed` already exists as a distinct Ring command.
- ?쏝aseline Startpoint??is not Autonics??documented term for Start Speed.

A home-search interpretation is weaker still. Autonics controllers do have automatic home-search functionality, but their documentation treats home search, origin coordinates, home-search speed, and direction as explicit parameters?봭ot as a generic ?쐀aseline startpoint.??[Autonics PMC-4B-PCI series](https://www.autonics.com/pe/series/PMC-4B-PCI), [PMC-1HS/2HS manual](https://www.autonics.com/in/model/PMC-1HS-232). Unless the relevant SetCommand case contains an origin/home command, the name alone does not support that reading.

A mundane explanation deserves more weight: `200.0` may be a developer?셲 test value, an old apparatus-specific calibration value, or an optional fallback whose meaning can only be established from the dataflow.

### The saved default may be irrelevant

Yes?봵ery likely, if the main VI wires that terminal.

LabVIEW connector-pane inputs receive values from the calling VI. Saved control defaults matter when a recommended/optional input is left unwired; required inputs must be wired. NI explicitly describes unwired subVI inputs as taking their default values and recommends making inputs required when their defaults are not generally valid. [NI terminal requirements](https://www.ni.com/docs/ar-IQ/csh?context=lvcore_lvhowto_specifying_required_recomm), [NI instrument-driver connector guidelines](https://www.ni.com/en/support/downloads/instrument-drivers/tools-resources/instrument-driver-guidelines/icon-and-connector-panes.html). NI even documents detecting an unwired input by comparing its received value to an improbable saved default. [NI: Check Whether a SubVI Input Is Wired](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L20SAE&l=en-US).

So the saved `200.0` proves only the control?셲 saved fallback value. It does not prove that 200 reaches the executing code in the actual application.

### Bottom line

Your interpretation fails first on its necessary premise: Autonics position coordinates can be negative. The observed successful negative moves actually support direct signed-coordinate or signed-displacement operation, not a hidden positive baseline.

Current likelihood ranking:

1. Main VI supplies a runtime value, making saved `200.0` irrelevant.
2. Apparatus-specific positional reference/calibration, probably in degrees or converted units.
3. Ramp/start-speed-related parameter.
4. Stale developer test default.
5. A 200-turn midpoint introduced because negative pulse positions are impossible?봠ontradicted by Autonics specifications.

The cheapest decisive evidence is a reporter listing for the `MovePos` and `MovePosRel` cases showing:

- every wire/source feeding `Baseline Startpoint`;
- arithmetic immediately before degree-to-pulse conversion;
- exact formatted VISA command strings;
- connector-pane required/recommended/optional status;
- the main VI?셲 wire into this terminal.

Until that trace exists, assigning ?쐔urns??to `200.0` is unsupported, and the reason proposed for the offset is demonstrably false.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
