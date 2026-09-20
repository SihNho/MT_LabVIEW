# t2-rsrc-format

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $2.1026  in 24 / out 10412 / cache-create 47049 / cache-read 442069  (192s, 15 turn(s))
- **date:** 2026-09-19 23:27:55
- **outcome:** ANSWERED (194s)
- **why asked:** T2 (STATUS NEXT second act, `docs/cycle27-plan.md` Pre-decided 29(h)) needs a
  block-level RSRC diff of `claudeDev\D1_s1arm_savetest.vi` against the ORIGINAL. The `.vi` container
  layout and its block idents are a factual question about a file format, so CLAUDE.md §5's mandatory
  external search applies. This session's own `WebSearch`/`WebFetch` are denied by the permission
  layer, so the search went down the ladder as `-Kind fact` (claude / fable-low / thin / web).
- **verdict:** CONFIRMED AGAINST THE MACHINE on the parts that drove the build; partly unsourced
  elsewhere, and recorded as unsourced rather than used.

## Question

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


## Answer

Research complete. Here are the answers, sourced.

## A. Container layout

Primary sources: pylabview's parser code ([LVrsrcontainer.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVrsrcontainer.py), [LVblock.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py)) and its wiki ([RSRC Format](https://github.com/mefistotelis/pylabview/wiki/RSRC-Format)). All multi-byte fields are **big-endian** u32s — confirmed by your own bytes only making sense that way (below).

**1. The four u32s, in order** (pylabview `RSRCHeader`): `rsrc_info_offset`, `rsrc_info_size`, `rsrc_data_offset`, `rsrc_data_size`. The full header is: 6-byte magic `RSRC\r\n`, u16 format version (0x0003), 4-byte type (`LVIN`), 4-byte creator (`LBVW`), then those four u32s — **32 bytes total**. Your file decodes as info_offset=0x72c30, info_size=0xcb5, data_offset=0x20 (data starts right after the header), data_size=0x72c10, and info_offset+info_size = 473,317 = file size, which is self-consistent.

**2. At `rsrc_info_offset`:** yes — a second, identical copy of the 32-byte RSRC header is repeated there ("two identical RSRC headers"; pylabview writes the second header at `rsrc_info_offset`). Note the wiki's Home rendering once says the second header is at the *data* offset — the code (`seek(rsrchead.rsrc_info_offset)`) and your file layout show it's the **info** offset.

**3. `BlockInfoListHeader`** (immediately after the repeated header), five u32s: `dataset_int1`, `dataset_int2`, `dataset_int3` (unknown; the wiki describes one as the RSRC-header size), `blockinfo_offset`, `blockinfo_size`. `blockinfo_offset` is **relative to `rsrc_info_offset`** — pylabview sets it to `sizeof(RSRCHeader) + sizeof(BlockInfoListHeader)` = 52, i.e. it counts from the repeated header, not from file start.

**4. Block info list:** first a u32 `blockinfo_count` storing **count − 1** (pylabview: `tot_blockinfo_count = binfhead.blockinfo_count + 1`, and comments "means the same as len(sections) − 1"). Then per block a 12-byte `BlockHeader`: `ident` (4 raw bytes), `count` (u32, also stored as sections−1 per the wiki's "count (+1)"), `offset` (u32) — the offset to that block's array of section-start records, relative to the start of the block-info area within the info section (per the wiki, offsets are relative to their own region, not the file).

**5. `BlockSectionStart`** — **20 bytes**: `section_idx` (i32), `name_offset` (u32, offset to the section's text name, −1/0xFFFFFFFF if none), `int3` (u32, unknown), `data_offset` (u32), `int5` (u32, unknown). `data_offset` is **relative to `rsrc_data_offset`**: pylabview computes `block_pos = rsrc_data_offset + section.start.data_offset`.

**6. Section data size:** yes, each section's data begins with a **u32 length prefix**, and it is **exclusive** of the prefix itself — pylabview's `BlockSectionData` holds only `('size', c_uint32)` and "stores only size of the raw data which follows."

**7. Idents:** they are 4 raw bytes (`c_ubyte * 4`), so they *can* be space-padded (`PRT `, `BDH ` in old versions) or contain arbitrary bytes; in practice they're printable ASCII. Each ident appears **once** in the block list — multiplicity is expressed via a block's `count` of sections, not by duplicate idents ([pylabview code](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py), [wiki Blocks page](https://github.com/mefistotelis/pylabview/wiki/Blocks)).

## B. Block idents

Sources: **[W]** = [pylabview wiki Blocks](https://github.com/mefistotelis/pylabview/wiki/Blocks), **[C]** = [pylabview LVblock.py comments](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py), **[H]** = [VI Explorer / hmilch.net source-code page](https://www.hmilch.net/h/labview_source.php), **[L]** = [mefistotelis's LAVA posts](https://lavag.org/profile/63044-mefistotelis/content/page/2/), **[R]** = [Ryan Pacini, LabVIEW VI File Format](https://ryanpacini.com/posts/vifileformat/).

- `LVSR` — "LabVIEW Save Record": saved version u32, file flags, protection info; input to the password hash [W][R][H]
- `BDPW` — "Block Diagram Password": three MD5 hashes (password hash, hash1 over password+LIBN+LVSR(+salt since LV2012), hash2 additionally over the BDHc heap) [W][H]
- `BDH `/`BDHb`/`BDHc`/`BDHP` — Block Diagram Heap, in successive heap encodings; b/c are compressed forms; binary-tree object hierarchy [W][H]
- `FPH `/`FPHb`/`FPHc` (and `FPHP`) — Front Panel Heap, same format as the BD heap with panel object types [W][H]
- `VICD` — VI Compiled Data: "the actual assembly, and list of 'patches'" (imports + relocation), incl. `InitCodePtrsProc` [L]
- `DFDS` — "Default Fill of Data Space": flattened default values loaded into the data space [C][L]
- `TM80` — Type Map: selects the subset of VCTP types forming the Data Space and assigns `tmFlags`; successor of DSTM in LV≥8 [L]
- `CONP` — Connector Pane type map: TypeID of the VI's Function-type terminal descriptor [C]
- `CPC2` — "Connector Pane Content Type v2" [C]
- `LIvi` — "LinkObj Refs for VI": dependency links between this VI and others [C][L]
- `LIfp` — "LinkObj Refs for Front Panel" [C]
- `LIbd` — "LinkObj Refs for Block Diagram" [C]
- `LIds` — "LinkObj Refs for Data Space" [C]
- `MUID` — "Map Unique Identifier — UID of LoadRefMap object" [C]
- `VCTP` — "VI Consolidated Types": central table of all TypeDescriptors (LV≥8); other blocks reference TypeIDs into it [L][H]
- `BDSE` — "Block Diagram Size Estimate" [C]
- `FPSE` — "Front Panel Size Estimate" [C]
- `STRG` — String description / description list (VI description text) [C][W]
- `icl8` — 8-bit icon bitmap ("icon large 8-bit"; siblings icl4, ICON) [W][H]
- `LIBN` — "Library Names": owning library qualified names; salted into the password hash [W][H]
- `HLPT` — "Help Tag" (help-file link) [C][W]
- `RTSG` — UNKNOWN — no source
- `OBSG` — UNKNOWN — no source
- `HIST` — revision History [W]
- `VITS` — "Persistent VI Tags as an array of name and data clusters" [H]
- `SCSR` — UNKNOWN — no source
- `DTHP` — UNKNOWN — no reliable description source (it exists as a parsed block in pylabview-family tooling, but I found no sourced statement of its contents)
- `PRT ` — Print Settings (note trailing space in the ident) [W]
- `FTAB` — Font Table [W]
- `CCSG` — UNKNOWN — no source
- `BNID` — UNKNOWN — no source
- `NUID` — UNKNOWN — no source
- `GCPR` — UNKNOWN — no source
- `VIMD` — UNKNOWN — no source (not listed in the wiki's Blocks page)

## C. Resave with no edit — what changes

The one directly relevant sourced statement: mefistotelis reports that a VI recreated/resaved is "in most cases, identical to the original," except that LabVIEW's multithreaded saver can emit the names section in pseudo-random order — sourced ([LAVA](https://lavag.org/profile/63044-mefistotelis/content/page/2/)). Everything per-block below is **inference** from what each block holds, except where marked:

**Expect to change:**
- `HIST` — a save appends/bumps the revision count even with no edit — inference (it is the revision history [W])
- `MUID`, `BNID`, `NUID`, `RTSG`, `OBSG`, `CCSG`, `SCSR` — ID/GUID/signature-flavored blocks plausibly regenerate per save — inference (contents unsourced)
- `BDPW` — changes iff any hashed input (LVSR/LIBN/BDHc bytes) changed; otherwise identical — inference from the sourced hash recipe ([hmilch](https://www.hmilch.net/h/labview_source.php))
- `LVSR` — changes if the saving LabVIEW version/flags differ from the stored ones; identical when resaved by the same version — inference
- `VICD` — changes if the compiler recompiles (different LabVIEW/patch level, or separate-compiled-code settings); a same-version resave without recompile should leave it identical — inference
- `BDHc`/`FPHc` — the heap bytes should be logically identical, but zlib recompression is not guaranteed byte-stable across versions — inference (zlib coding for LV≥8 is sourced from [LVblock.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py))
- Container-level: section ordering / name-table ordering may shuffle even when every section's bytes are unchanged — sourced ([LAVA](https://lavag.org/profile/63044-mefistotelis/content/page/2/))

**Expect byte-identical:** `CONP`, `CPC2`, `VCTP`, `TM80`, `DFDS`, `DTHP`, `STRG`, `icl8`, `FTAB`, `PRT `, `HLPT`, `LIBN`, `VITS`, `BDSE`, `FPSE`, `LIvi`/`LIfp`/`LIbd`/`LIds` (link blocks stay identical unless dependencies moved on disk), `VIMD`, `GCPR` — all inference, backed generally by the sourced "mostly identical" observation.

## D. What would make a parser wrong, and the cheap self-check

The strongest risk is **assuming the section payload is the u32-prefixed raw bytes**: since LabVIEW 8.0 many sections (heaps, VICD, and others) are **zlib-compressed inside the section**, with their own uncompressed-size framing, and which blocks are compressed is version-dependent — a parser keyed to one LabVIEW version silently reads garbage payloads for another (sourced: [LVblock.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py) sets `BLOCK_CODING.ZLIB` conditionally on version ≥ 8.0.0). Secondary risks: the off-by-one `count−1` encodings, offsets being region-relative rather than absolute, and 4-byte alignment padding between sections.

Cheapest self-checks: (1) verify the invariants your own file already exhibits — the 32-byte header at `rsrc_info_offset` must be byte-identical to the one at offset 0, and `rsrc_info_offset + rsrc_info_size` (or data offset+size+info size) must equal the file length; (2) for every section, check `rsrc_data_offset + data_offset + 4 + size` stays within `rsrc_data_offset + rsrc_data_size` and that consecutive sections tile the data region with only 0–3 padding bytes between them — any gap or overlap means you've mis-parsed; (3) for a suspected zlib section, check the payload starts with `78` (zlib header) and inflates to the declared uncompressed size.

Sources: [pylabview repo](https://github.com/mefistotelis/pylabview) · [LVrsrcontainer.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVrsrcontainer.py) · [LVblock.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py) · [wiki: RSRC Format](https://github.com/mefistotelis/pylabview/wiki/RSRC-Format) · [wiki: Blocks](https://github.com/mefistotelis/pylabview/wiki/Blocks) · [mefistotelis on LAVA](https://lavag.org/profile/63044-mefistotelis/content/page/2/) · [hmilch.net VI Explorer source notes](https://www.hmilch.net/h/labview_source.php) · [Ryan Pacini, LabVIEW VI File Format](https://ryanpacini.com/posts/vifileformat/)

One caveat: my claims are sourced against pylabview, whose format knowledge tops out around LabVIEW 2014–2020; I found no public reverse-engineering of LabVIEW 2026 specifically, so container-level claims for 2026 rest on the format's observed stability (your file's header decodes exactly per the pylabview layout, which is good evidence it still holds).

## Sources

- https://github.com/mefistotelis/pylabview
- https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVrsrcontainer.py
- https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVblock.py
- https://github.com/mefistotelis/pylabview/wiki/RSRC-Format
- https://github.com/mefistotelis/pylabview/wiki/Blocks
- https://lavag.org/profile/63044-mefistotelis/content/page/2/
- https://www.hmilch.net/h/labview_source.php
- https://ryanpacini.com/posts/vifileformat/

## What was done with it

**Used to CONFIRM a layout that had already been measured, not to supply one.** The first parser run
(`tools/bench/t2_rsrc_blockdiff.py`, run 1) mis-parsed and said so — its own self-checks C5/C6 failed
(12 of 110 payloads outside the data region; coverage 9.7 GB of a 470 kB region), so its tables were
printed `UNTRUSTED` and never reported. The correction was then read off the bytes with
`tools/bench/t2_rsrc_probe.py` → `tools/bench/t2_rsrc_probe.log`, **before** this answer arrived.
The two agree on every point that mattered:

| claim | measured in `t2_rsrc_probe.log` | this answer |
|---|---|---|
| leading header | 32 B, four BE u32 = info_off / info_size / data_off / data_size | same (§A.1) |
| header repeated at `rsrc_info_offset` | yes, byte-identical | same (§A.2) |
| `BlockInfoListHeader` | 5 × u32, `blockinfo_offset` = 52, relative to `rsrc_info_offset` | same (§A.3) |
| counts | stored as `count − 1` (44 → 45 blocks) | same (§A.4) |
| section-start record | **20 bytes**, 4th u32 = data offset relative to `rsrc_data_offset` | same (§A.5) |
| payload framing | u32 length prefix, exclusive of itself (LVSR 160 B at abs 36 → RTSG at data_off+164) | same (§A.6) |

Run 1's bug was exactly the pair this answer warns about in §D: a region-relative offset treated as
relative to the wrong base (`BI+4` instead of `BI`) and a wrong record size (24 B instead of 20 B).

Three things were taken from the answer and are now in the artefacts:

1. **The name of the 2nd u32** of `BlockSectionStart` (`name_offset`, `0xFFFFFFFF` = no name) — the
   measurement saw `ff ff ff ff` on 130 of 131 records but could not name it. Recorded in
   `tools/bench/t2_rsrc_blockdiff.log` appendix §C.
2. **§D's self-check** ("consecutive sections tile the data region with only 0–3 padding bytes") — the
   script's C7 had demanded EXACT tiling, which failed on both files by the same 101 bytes. C7 now
   measures the gap histogram instead (`{0:86, 1:11, 2:15, 3:20}`, max 3, identical on both sides) and
   all self-checks PASS, so the tables are `TRUSTED`.
3. **§E's zlib caveat** — some sections are zlib-compressed inside the section since LV 8.0, so an
   identical sha256 proves the stored bytes are identical while a differing sha256 does not by itself
   separate a content change from a recompression. Written into the log as a bound on what the diff
   means; nothing is interpreted here.

**What was NOT used.** §B's `UNKNOWN — no source` entries (`RTSG`, `SCSR`, `DTHP`, `BNID`, `NUID`,
`GCPR`) and §C's per-block "expect to change" list are the answer's own inference, explicitly labelled
as such. Both differing blocks in this diff (`LIvi`, `LIbd`) fall on §C's *"expect byte-identical"*
side, i.e. the answer's prediction for them is contradicted by the measurement — recorded, not
resolved, because what it means for rule 1a is the judgement session's call and T2 was a measurement
task. No block meaning is asserted in any artefact that this exchange did not source; the log lists
sourced and unsourced idents separately. The caveat that pylabview's knowledge stops around LabVIEW
2014–2020 with no public LabVIEW 2026 work is why the self-checks, not the source, are what the
tables rest on.
