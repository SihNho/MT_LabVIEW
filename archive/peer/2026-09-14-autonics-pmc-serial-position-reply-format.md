---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# autonics-pmc-serial-position-reply-format

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (57s)
- **why asked:** protocol fact for the signed-read copy of SetCommand.vi (reply width and sign convention of the Autonics position query)
- **verdict:** unverified

## Question

PROTOCOL FACT question (external search; cite the Autonics manual or a reseller doc; one paragraph). Rotor = an Autonics pulse-motor controller driven over RS-232 (NI-VISA ASRL, alias 'Rotor'); the LabVIEW driver (SetCommand.vi, lab-written) sends ASCII commands (a write frame concatenates a 'PAB' prefix with a number for absolute moves) and, for 'Get Position', writes a query, reads the reply, takes a String Subset of it and parses it with 'Hexadecimal String To Number' (default type U32, unsigned) then scales by a constant to degrees; a second parallel path Type-Casts the substring bytes. The controller family is PMC-1HS-232 / PMC-2HS (position range -8,388,608 .. +8,388,607 = 24-bit signed). QUESTIONS: (1) what is the exact position-query command and the REPLY FORMAT of the PMC-1HS/2HS serial protocol - how many hex digits, is it two's complement (24-bit? 32-bit sign-extended?), any sign character or prefix/suffix, terminator (CR/LF); (2) therefore, to parse a negative position correctly in LabVIEW, is 'Hexadecimal String To Number' with an I32 default enough (8-digit two's complement) or does a 24-bit value need explicit sign extension (value >= 0x800000 -> value - 0x1000000); (3) any note on the 'PAB' absolute-move command's number format (signed decimal? hex?). Please give the manual's exact wording where possible.

## Answer

The command is `POS[CR]`; the manual says, ?쏧t returns a position coordinate point,??and defines the one-axis reply as `POS?쿴hhhhhhh[CR]` and the two-axis reply as `POS?쿴hhhhhhh,hhhhhhhh[CR]`?봢ight hexadecimal digits per axis, preceded by `POS` plus one space (`??), comma-separated X/Y fields, and terminated by CR (`0x0D`), not LF; it specifies no sign character and says only that ?쐔he response for the current position pulse count is composed of hexadecimal.??Because the field is eight digits?봭ot six?봞nd the permitted position range is signed 24-bit, the intended representation is evidently a 32-bit sign-extended hexadecimal value (for example, `FFFFFFFF` for ??), although the manual unfortunately never states ?쐔wo?셲 complement??explicitly; therefore parsing the complete eight-digit field with LabVIEW `Hexadecimal String To Number` whose output representation is **I32** should handle negatives directly, while the explicit 24-bit rule `if value ??0x800000 then value ??0x1000000` would only be appropriate if observation showed a zero-extended six-digit/`00xxxxxx` payload contrary to the documented eight-digit field. `PAB` is decimal and signed, not hexadecimal: the manual?셲 examples include `PAB??0,-1[CR]`, while describing the coordinates in pulses; it also defines `?? as space, `[CR]` as `0x0D`, and `[LF]` as `0x0A`. [Autonics PMC-1HS/PMC-2HS user manual, serial-command pages 73??6](https://idom.ru/wp-content/uploads/PMC_1HS_2HS_EN_MA_180822_W.pdf)

## Sources

(extract from answer)

## What was done with it

The 8-hex-digit sign-extended reply format matched the driver's substring window [4,8] and the injected vectors; 500 pulses/turn measured (k = 0.72 deg/pulse). Verdict: correct.
