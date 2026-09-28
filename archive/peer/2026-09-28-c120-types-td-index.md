# c120-types-td-index

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2139  in 22 / out 10325 / cache-create 87953 / cache-read 998873  (128s, 16 turn(s))
- **date:** 2026-09-28 15:23:48
- **outcome:** ANSWERED (132s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed prediction in tools/bench/diag_c120_types.log (script tools/bench/diag_c120_types.py, card 120-2).

CONTEXT. A new read-only op VI OpTermDataType_v0 reads Terminal.Data Type (634A008, a Variant) and exports it as the bytes of
Flatten To String(variant) (a U8 array plus a lowercase-hex string; both agreed on every read). tools/gscript.py
parse_type_descriptors() parses those bytes: U32 version, I32 nTDs, nTDs x (I16 len, I16 code, body), I16 index count, I16 indices
(layout recorded in docs/NAMES.md:1153-1155). Two gates failed: "K K_DBL top TD = Array of DBL (NAMES.md:37)" and "K K_I32 top TD =
Array of I32 (NAMES.md:41)" (diag_c120_types.log:49-50). All 9 reads themselves passed (uid echo, hex == u8, no error; :31-48);
the 2000-call hygiene probe passed (:24-25); loop i read as I32 (:35,:51).

RAW (from the log):
  K_DBL t5124 'x,y,z array out': TD list [DBL, Array]; top Array TD = 001c 4040 0001 ffffffff 0000 0f 'x,y,z array out'
  K_I32 t5171 'pos in cal image out': TD list [I32, Array]; top Array TD = 0022 4040 0001 ffffffff 0000 14 'pos in cal image out' 00
  F5 t11614 output cluster: TD list [DBL, Array, DBL, Array, Cluster]; top Cluster TD = 000a 0050 0002 0001 0003

THE CLAIM. The op and the bytes are right; the failure is OUR PARSER: it read the Array's element as an INLINE TD at the bytes after
the dimension sizes (giving codes 0x78 'x' and 0x70), but in a flattened variant the Array TD holds an I16 INDEX into the TD list
after ndims x I32 (here 0000 -> TD 0 = DBL / I32), and a Cluster TD holds I16 n then n x I16 indices (F5: elements TD 1 and TD 3).
The fix is parser-only (gscript.py parse_type_descriptors + _td_canon); re-parsing the recorded bytes offline should give
Array1D<DBL>, Array1D<I32>, I32, and Cluster{Array1D<DBL>,Array1D<DBL>} for F5.

Give: the strongest reason this claim is wrong; an alternative explanation of the bytes (e.g. is 0000 something other than an
element index - flags, a typedef index, a dimension field?); what would falsify the index reading; the cheapest discriminating test.
Cite NI documentation on flattened type descriptors (LabVIEW "Type Descriptors" / "Flattened Data") where you can.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: I tried to refute the claim and could not. The bytes support it, the claim holds, and two small corrections are listed below.** The parser in `tools/gscript.py:4312-4322` and the gates in `tools/bench/diag_c120_types.py:76-80` are already written to the index reading, so the fix still needs its offline check before anyone relies on it.

## 1. Strongest reason the claim could be wrong

The log alone does not separate the explanations. In K_DBL, K_I32 and R0 the element field is `0000` and the element TD is at position 0. A reserved or flags field that is always `0000` fits those bytes just as well, as does an "element = the TD just before" rule, or a "TD 0" rule. The claim was built from cases that cannot tell these apart.

## 2. Alternative explanations tested against the full recorded bytes

The full F5 bytes are in `tools/bench/facts_c120_types.json:132`:

```
0005 000a 00                          TD0 DBL
000c 0040 0001 ffffffff 0000          TD1 Array  -> 0000
000b 400a 00 05'Value'                TD2 DBL 'Value'
000c 0040 0001 ffffffff 0002          TD3 Array  -> 0002
000a 0050 0002 0001 0003              TD4 Cluster {1,3}
0001 0004                             top = TD4
```

- **"`0000` is a reserved or flags field":** falsified. TD3 carries `0002`.
- **"Element is always TD 0":** falsified by the same byte.
- **"Element is an inline TD" (the old parser):** impossible. R0's Array TD is 12 bytes long (`000c00400001ffffffff0000`, `facts_c120_types.json:204`). After 2+2+2+4 bytes only 2 remain, and an inline DBL TD needs at least 5 bytes (`0005 000a 00`). The old parser was following the LabVIEW 7.x layout, where the element TD is inline. That page is kept by NI as legacy help ([NI: Type Descriptors in LabVIEW 7.x and Earlier](https://zone.ni.com/reference/en-XX/help/371361R-01/lvconcepts/old_type_descriptors/)). LabVIEW 8 and later use a different layout ([LAVA: LabVIEW 8.0 type descriptors](https://lavag.org/topic/2719-flatten-to-string-labview-80-type-descriptors/)).
- **"Element is the TD just before":** this one survives. F5 is still consistent with it, because TD1→TD0 and TD3→TD2 both point to the preceding TD. It is weak, though. A positional rule would not need an explicit field, and the field's value matches the position exactly.
- **External confirmation:** pylabview, an independent reverse-engineered LabVIEW file-format parser, reads an index for LabVIEW 8.0.0.1 and later. Its `TDObjectArray` reads U16 ndims, then ndims × U32 (top 8 bits are flags, low 24 bits are the size; `ffffffff` means variable), then `parseRSRCIndexedTD` for the element. `TDObjectCluster` reads a count and then that many indexed TDs ([pylabview LVdatatype.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVdatatype.py)). This is not NI documentation. I could not open NI's own article on the flattened variant format ([knowledge.ni.com kA03q000000YGQrCAO](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQrCAO&l=en-US)) because of a certificate error, so NI's text is not checked.

## 3. What would falsify the index reading

- An Array whose element field names a TD that is not the one immediately before it, and whose canon then comes out wrong.
- An Array TD longer than 6 + 4·ndims + 2 bytes plus its label.

## 4. Cheapest discriminating test

1. **Offline, no LabVIEW:** run `parse_type_descriptors` on the recorded `bytes_hex` in `facts_c120_types.json` (lines 132, 188, 252, 291). Expect `Cluster{Array1D<DBL>,Array1D<DBL>}`, `Array1D<DBL>`, `Array1D<DBL>`, `Array1D<I32>`. Also check that TD3's `elem_index` is 2.
2. **To separate "index" from "the TD just before":** read one terminal whose element TD is not adjacent to its Array TD. A cluster `{DBL a, I32 b, Array of DBL}` is a good candidate, because the TD list is likely to put the Array's element away from it. Adjacency could not have produced such a result. This needs one op call on a scratch VI.

## Residual risks (none of them flips the verdict)

- **Variable-size index field.** pylabview reads the index and the cluster count with a variable-size reader: 2 bytes, or 4 if bit 15 is set ([LVmisc.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVmisc.py)). Our parser always reads a fixed I16. That is harmless below 32768 TDs.
- **Two-dimensional arrays are untested.** The ndims × I32 step has only been seen with ndims = 1.
- **`docs/NAMES.md:1166-1167` is slightly wrong.** The padding is on the Pascal label (padded to even length), not on the TD. K_I32's TD0 is 47 bytes: 4 + 1 (`prop1`) + 41-byte label + 1 pad. The `00` byte after a numeric code is pylabview's `prop1` field. Both are harmless to `canon`, because the TD length field already skips them. They only matter if someone extracts labels by position.

## Sources

(extract from answer)

## What was done with it

Accepted (card 120-2 material). The parser is fixed to the index reading (tools/gscript.py parse_type_descriptors: Array ->
`elem_index`, Cluster -> `elems`; `_td_canon` builds the label-free type string) and the gates of tools/bench/diag_c120_types.py
now compare `canon`. The peer's test 1 was run OFFLINE first: tools/bench/diag_c120_parsecheck.log re-parses the recorded
bytes of run 1 -> 9/9 PASS (K_DBL Array1D<DBL>, K_I32 Array1D<I32>, F3 I32, R0 Array1D<DBL>, F5 Cluster{Array1D<DBL>,Array1D<DBL>}).
Then diag_c120_types.py is re-run once. Test 2 (a non-adjacent element TD) and the variable-size index / 2-D array risks are not
measured here; they are reported as open, not assumed.
