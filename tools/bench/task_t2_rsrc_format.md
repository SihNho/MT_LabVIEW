# FACT QUESTION — the binary layout of a LabVIEW `.vi` (RSRC) container, and what its block idents mean

This is a pure file-format question. No project context is needed and none is attached. Answer from
public sources (pylabview / mefistotelis, the LAVA / NI forums, LabVIEW file-format reverse-engineering
write-ups, `lvrt` documentation) and **give the source URLs for every claim**.

## A. The container layout — exact field order, widths and endianness

A LabVIEW 2026 `.vi` begins with the ASCII bytes `RSRC\r\n\x00\x03`, then `LVIN`, then `LBVW`.
The next 16 bytes of one real file are:

```
00 07 2c 30   00 00 0c b5   00 00 00 20   00 07 2c 10
```

and the file is 473,317 bytes long (0x72c30 + 0xcb5 = 473,317).

1. Name each of those four u32 fields **in order** (offset/size of the info section, offset/size of the
   data section — say exactly which is which), and give the total size of this leading header.
2. What sits at `rsrc_info_offset`? (Is the 32-byte header repeated there?)
3. Give the **exact field list** of the structure that follows it — pylabview calls it
   `BlockInfoListHeader` — with each field's width, and say whether `blockinfo_offset` is absolute or
   relative to `rsrc_info_offset`.
4. Give the exact field list of the **block info list** itself: the count field (is the stored value
   `count` or `count - 1`?), then each block entry (`ident` 4 chars, a count field, an offset field) —
   and say what that offset is relative to.
5. Give the exact field list and **byte size** of `BlockSectionStart` (pylabview's name), including
   which field is the section's data offset and what it is relative to.
6. How is a single section's **data size** determined — is there a u32 length prefix at the start of the
   section data, and is that length inclusive or exclusive of the prefix itself?
7. Are block idents ever padded/non-ASCII, and can two blocks share an ident?

## B. The block idents — meaning only where you can source it

For each of these idents, say what the block holds **and give the URL you got it from**. If you cannot
source one, write `UNKNOWN — no source` rather than guessing:

`LVSR` · `BDPW` · `BDH` / `BDHb` / `BDHc` / `BDHP` · `FPH` / `FPHb` / `FPHc` · `VICD` · `DFDS` ·
`TM80` · `CONP` · `CPC2` · `LIvi` · `LIfp` · `LIbd` · `LIds` · `MUID` · `VCTP` · `BDSE` · `FPSE` ·
`STRG` · `icl8` · `LIBN` · `HLPT` · `RTSG` · `OBSG` · `HIST` · `VITS` · `SCSR` · `DTHP` · `PRT ` ·
`FTAB` · `CCSG` · `BNID` · `NUID` · `GCPR` · `VIMD`

## C. The question that actually matters

If a LabVIEW VI is opened and **re-saved with no edit at all**, which of those blocks would you
*expect* to change bytes purely as a side effect of the save (compiled-code regeneration, timestamps,
GUIDs, password/checksum blocks, link tables), and which ones would you expect to be byte-identical?
Mark each answer `sourced (<url>)` or `inference`.

## D. What would make this wrong

Name the strongest reason a parser built on your answer to part A could mis-parse a real LabVIEW 2026
`.vi` (version drift in the container, alignment/padding, compressed sections, zlib-wrapped blocks),
and the cheapest check a parser can run on itself to detect that it has mis-parsed.
