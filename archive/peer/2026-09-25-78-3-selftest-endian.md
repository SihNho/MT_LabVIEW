# 78-3-selftest-endian

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1317  in 24 / out 9511 / cache-create 79247 / cache-read 1019072  (131s, 18 turn(s))
- **date:** 2026-09-25 07:53:09
- **outcome:** ANSWERED (135s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed prediction in an OFFLINE Python self-test (no LabVIEW involved).

Script: tools/bench/m8b_replay_compare.py (new, card 78-3). Log: tools/bench/m8b_replay_selftest78.log.
Prediction: gate "G1 both tra parse" PASS when the script reads a tra file (tools/bench/m8_out/s1_20260925_063401/tra001-000)
as: text header ending at b"not in z!)", then two I32 dims, then f64 row-major data, with dims product == data length.
Observed: G1 FAIL; dims read as [-1207107584, 201326592] (tools/bench/m8b_replay_selftest78.json).

Claim: the dims (and the f64 data) are LITTLE-endian, not big-endian as the first version assumed.
-1207107584 = 0xB80D0000 whose byte-reversal is 0x00000DB8 = 3512, and 201326592 = 0x0C000000 -> 12; 3512 rows x 12
cols matches the tra header "actual data points/nominal: 3512/2000000" and drive_m8.tra_rows' earlier count
(tools/bench/m8_s1_p3.json:110-112: data_bytes 337160 = 3512*96 + 8). The fix is "<ii" and "<f8".

Already ruled out: file truncation (size matches 3512*96+8 exactly); a different column count (12 = time,trans,rot + 3 beads x xyz).
Question: is there any reason the DATA block could be big-endian while the dims are little-endian (LabVIEW's
Write to Binary File defaults to big-endian, so a little-endian dims prefix is itself surprising)? What is the cheapest
check that distinguishes "<f8" from ">f8" for the data block, e.g. the time column being monotonic and finite?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict:** The dims are little-endian, and that part is proven: the bytes `B8 0D 00 00 0C 00 00 00` give 3512 × 12 only when read as `<ii`, and no offset shift makes them big-endian. The data block's byte order has not been measured. `<f8` was inferred from the dims, and the self-test cannot catch it if that inference is wrong. I found no known way for one write to produce little-endian dims with big-endian data, so the claim probably holds. It should still be checked from the file bytes before anything relies on it.

**1. Strongest reason it could be wrong.** The fix changes two things, but the evidence covers only one. `"<ii"` is proven. `"<f8"` is borrowed from it, not measured. The comparison gate (G3 in `m8b_replay_compare.py:33`) compares raw bytes (`view("u8")`). That gives the same answer whichever byte order is used, so it would pass even with the wrong order. Two reported facts do depend on it: `nan_rows_s1` (line 40) and `max_abs_diff_xyz` (line 38). A big-endian NaN (`7F F8 00…`) read as `<f8` becomes a tiny finite number (about 3e-319). A run with no beads would then report `nan_rows = 0` without any error.

Also, the self-test used the **same file** for both runs (`m8b_replay_selftest78.json:3` and `:11`), so G3 would pass trivially. The comparison has not been tested at all yet.

**2. Alternative explanation of the same evidence.** The data block could be big-endian while the dims are little-endian. There are two ways this could happen:
- **Forum folklore:** a search summary cited forum posts saying the "prepend size" bytes are always written big-endian, whatever byte order is chosen. Others say they follow the chosen order. The pages I fetched state neither, so this is unsourced. It would also predict the opposite split: big-endian dims with little-endian data. Your file shows little-endian dims.
- **Two separate writes:** the size prefix and the data might come from different write calls.

The project's own diagram dump argues against both:
- `docs/wiki/subvi/save N xyz traces.json` shows the writer is **one** `Write to Binary File` node (uid 228, lines 1039-1043).
- Its data input is **one cluster** from a Bundler (uid 525, lines 946-955). The cluster holds the header string from Format Into String (lines 729-737) and the `data array` (lines 933-944).
- Byte order is set by **one explicitly wired constant** (EnumConstant 149, wire 274, lines 754-764).

In a single cluster write, the string length, the array dims and the doubles are all serialised in one pass. A split would need a mechanism that nobody has shown.

**3. What would prove the claim wrong.** Any of these:
- In the 8-byte data words, the sign/exponent byte (typically `0x3F`–`0x41`, `0xBF`–`0xC1`, or `0x7F` for NaN) shows up at byte position 0 rather than position 7.
- Under `<f8`, the time column is not monotonic, or its step is not plausible.
- Under `<f8`, the translation column falls outside roughly 0–39 mm.

**4. Cheapest test that separates the two** (read-only Python, no LabVIEW):
- **(a) Check the header's length prefix.** The header region is 337593 − 337160 = 433 bytes. If the file is one cluster, the first 4 bytes are the string length, 429 (= 0x1AD). Little-endian gives `AD 01 00 00`; big-endian gives `00 00 01 AD`. This is a third size field, independent of the dims, written by the same node. It also confirms that `k+10` is the exact data offset.
- **(b) Count byte values by position.** Split the 337160 − 8 data bytes into 8-byte words and count values at position 0 and at position 7. The position where `0x3F`–`0x41`/`0xBF`–`0xC1` cluster is the exponent byte. This needs no assumptions about the values.
- **(c) Only then look at values:** time increasing with a steady step, and translation in the plausible range.

Do **not** use "finite" as the test. Byte-swapped doubles are almost always finite, and all-zero columns look the same in either byte order.

The authoritative cross-check would be the **value** of the byte-order constant in the lab's own `tra` reader (`load N bead trace-module.json:1752-1761`, EnumConstant 156) or in the writer (EnumConstant 149). The dump records that each is wired, but not what it is set to. Reading it would take a headless COM read of a copy, which costs more than (a) and (b).

**What would change my mind:** (a) showing `00 00 01 AD`, or (b) finding the exponent byte at position 0.

Sources:
- [NI forum: Help/Guidance on writing to Binary Files to be read by other languages](https://forums.ni.com/t5/LabVIEW/Help-Guidance-on-writing-to-Binary-Files-to-be-read-by-other/td-p/4422937) (flattened array/string = I32 size + contents; says nothing about byte order of the size bytes)
- [NI forum: Writing to binary file adds empty spaces with prepend size](https://forums.ni.com/t5/LabVIEW/Writing-to-binary-file-automatically-adds-s-empty-spaces-when/td-p/4315254) (no explicit byte-order statement)
- [LabVIEW Wiki: Write Binary File function](https://labviewwiki.org/wiki/Write_Binary_File_function) (a stub, no byte-order detail)
- [LAVA: Write to Binary File Cluster Size](https://lavag.org/topic/19255-write-to-binary-file-cluster-size-x-post-to-ni-forums/) (search result: sizes inside clusters are always written)
- [comp.lang.labview: Is LabVIEW handling big endianness automatically?](https://comp.lang.labview.narkive.com/JjbvQkI5/is-labview-handling-automatically-big-endianness)

## Sources

(extract from answer)

## What was done with it

Cycle-78 judgement, 2026-09-25. **ACCEPTED, applied.** The review's discriminating tests (a)(b) were added to the
comparer self-test G1 and pass. The tra layout is fixed as LE I32 dims + LE f64 with the header length prefix (429)
checked, and the negative control (live S1@3 vs S3@3, INDEX row 46) reports all 3,512 rows different
(`tools/bench/m8b_replay_selftest78c.log`). So the comparer is not vacuous, and its PASS on the replay pair
(10,310/10,310 bit-identical) stands. Ruling: `docs/m8-real-run-plan.md` PD23.

SAME-ROW: m8b_replay_selftest78b.log (2026-09-25 07:54:05)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.

SAME-ROW: m8b_replay_selftest78c.log (2026-09-25 07:54:21)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.

SAME-ROW: drive_m8_replay_s1_78.log (2026-09-25 08:10:42)
  This later failure of the SAME script was released without buying a new peer review: one review per row per cycle (CLAUDE.md, user 2026-09-22). The review above is the evidence; this line records which re-run was charged to it.
