---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# hex-string-to-number-signed-default

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (56s)
- **why asked:** API fact before designing the signed-read copy of SetCommand.vi (does an I32 default make Hexadecimal String To Number parse two-complement?)
- **verdict:** unverified

## Question

API FACT question (external search, cite NI docs; one paragraph + a yes/no). LabVIEW 2026 primitive 'Hexadecimal String To Number' (Programming > String > Number/String Conversion). Measured on a copy of a vendor driver (tools/bench/probe_setcommand.log): its 'default' input is UNWIRED and the terminal reads 'default (0uL)' - i.e. the primitive's built-in default type is U32, so a controller reply like 'FFFFFFF6' (two's complement -10) parses as 4294967286. QUESTIONS: (1) confirm the built-in default type of 'default' for Hexadecimal String To Number is U32 ('0uL') in current LabVIEW (and that Decimal String To Number's is I32) - cite; (2) if an I32 constant 0 is wired to 'default', does 'FFFFFFF6' come out as -10 (bit reinterpretation / wrap), as the max I32, or as an error? NI's help text for this primitive about overflow/out-of-range and about negative hex strings ('-A'); (3) same for an I16 default with a 4-digit reply 'FFF6' - does it give -10; (4) is the 'Type Cast' primitive applied to the raw reply STRING (x = string, type = a numeric constant) a valid alternative to get a signed integer from ASCII hex text? (I believe NOT: Type Cast reinterprets the string's BYTES, not its hex meaning - the ASCII bytes of 'FFF6' cast to I32 give 0x46464636, so that parallel path in the driver cannot be a correct signed parse; please confirm or refute). Context: we plan a signed-read copy of the driver; the acceptance test will be a pure-LabVIEW parse test with strings like FFFFFFF6 before any hardware.

## Answer

**No.** Current NI documentation identifies Hexadecimal String To Number?셲 unwired output/default as **U32**, while Decimal String To Number defaults to **I32** ([NI Hexadecimal String To Number](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/hexadecimal-string-to-number.html), [NI Decimal String To Number](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/decimal-string-to-number.html)); wiring an **I32** default does not reinterpret `FFFFFFF6` as two?셲-complement ??0: because the parsed positive hexadecimal value exceeds I32 range, the primitive saturates to **I32 maximum, 2147483647**, without producing an error, and likewise `FFF6` with an **I16** default yields **32767**, not ??0?봳he documented rule is that an out-of-range input returns that representation?셲 maximum ([NI Hexadecimal String To Number](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/hexadecimal-string-to-number.html)). NI?셲 help also says negative hexadecimal strings are not permitted, so textual `-A` is not the supported way to obtain ??0 ([NI discussion quoting the help?셲 negative-hex rule](https://forums.ni.com/t5/LabVIEW/Hexadecimal-string-to-number-Minus-sign-hyphen-vs-en-dash-for/td-p/4033868)). Type Cast on the raw ASCII string is also **not** a hexadecimal parser: it preserves and reinterprets the underlying bytes ([NI Type Cast explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DcZ9SAK&l=en-US)), so ASCII `FFFF`/`FFF6` becomes the character-byte pattern??FFF6` as I32 is `0x46464636`, not ??0. For the signed driver copy, parse as **U32/U16 first, then Type Cast that numeric value to I32/I16** (or explicitly subtract \(2^{32}\)/\(2^{16}\) when the sign bit is set); your pure-LabVIEW acceptance cases should require `FFFFFFF6 ????0` and `FFF6 ????0`.

## Sources

(extract from answer)

## What was done with it

Decisive: the design avoided the I32 default and used U32 parse -> Type Cast; measured -10 pulses -> -7.2 deg. Verdict: correct.
