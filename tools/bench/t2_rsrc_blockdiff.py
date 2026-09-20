#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
T2 -- OFFLINE, READ-ONLY, block-level RSRC diff of a no-edit COM save against the ORIGINAL.

STATUS NEXT's SECOND ACT / `docs/cycle27-plan.md` Pre-decided 29(h).  Cycle 47, material session.

WHAT THIS IS
------------
Cycle 46 made the first COM save of a copy of the main VI with NO diagram edit at all
(`claudeDev\\D1_s1arm_savetest.vi`, md5 e0112963cc1b9e3be29d2bb053ba9029, 475,141 B, from an
ORIGINAL of md5 2a78e17c449cacdaf5da389818526859, 473,317 B).  The file grew by 1,824 bytes and its
md5 changed, so *something* was rewritten.  This script measures WHICH PARTS -- it parses both files
as RSRC containers and reports, per resource block, the bytes that are identical, the bytes that
differ, and the blocks present on only one side.

IT DOES NOT JUDGE.  It writes no verdict about rule 1a, about whether the save is safe, or about
what a differing block implies.  That is the judgement session's call.

PRIOR ART -- checked before writing a line (CLAUDE.md, "Reuse before you author")
--------------------------------------------------------------------------------
  * `grep -ri "RSRC|LVSR|BDPW|VICD|saved.version"` over `tools/` returns exactly ONE piece of
    .vi-binary code in the whole project: `tools/recipes/stage_d1_s1.py:293 version_bytes(path)`,
    which reads the first 64 bytes and scans them for a `?? 00 80 00` run (CLAUDE.md rule 1's
    saved-version audit: `19 00 80 00` = LV2019, `26 00 80 00` = LV2026).  Its outputs are in
    `tools/bench/s1_saveroute.json` and `tools/bench/s1_stage_readings.json`.
  * There is NO block parser, NO RSRC header reader and NO .vi differ anywhere under `tools/`.
    `tools/recipes/build_opconstvalue_v1b.py:54` unpacks a `>Ii` -- that is a LabVIEW *flattened
    variant* header, not a file container, and does not apply.
  * REUSED: `version_bytes()`'s exact convention (first 64 bytes, every `?? 00 80 00` run with its
    offset) is re-implemented here as `version_bytes()` byte-for-byte in behaviour, so this script's
    numbers are directly comparable with the two JSON files above.  It is NOT imported, because
    importing `stage_d1_s1` pulls in `gscript`, which opens a COM connection to LabVIEW -- and this
    task must touch no LabVIEW at all.
  * EXTENDED: everything from the 32-byte header onwards (info section, block info list, per-block
    section table, per-section payloads) is new.

FORMAT SOURCE -- external search is MANDATORY (CLAUDE.md sec.5)
--------------------------------------------------------------
This session's own WebSearch/WebFetch tools are denied by the permission layer, so the search was
dispatched down the ladder as `tools/peer.ps1 -Kind fact -Slug t2-rsrc-format`
(task: `tools/bench/task_t2_rsrc_format.md`).  Whatever that exchange returns is pasted, with its
source URLs, into `tools/bench/t2_rsrc_blockdiff.log` and archived under `archive/peer/`.
The layout this parser assumes, stated so it can be refuted:

    off  0  8B  'RSRC\\r\\n\\x00\\x03'
    off  8  4B  file type     ('LVIN' for a VI)
    off 12  4B  file creator  ('LBVW')
    off 16  4B  u32 BE  rsrc_info_offset        (measured: 0x72c30 on the ORIGINAL)
    off 20  4B  u32 BE  rsrc_info_size          (measured: 0xcb5; 0x72c30+0xcb5 = 473,317 = filesize)
    off 24  4B  u32 BE  rsrc_data_offset        (measured: 32)
    off 28  4B  u32 BE  rsrc_data_size          (measured: 0x72c10 = 470,032)
    at rsrc_info_offset: the same 32-byte header again, then
        5 x u32 BE: int1, int2, int3, blockinfo_offset, blockinfo_size   (offset REL to info_offset)
    at rsrc_info_offset + blockinfo_offset:   (call this address BI)
        u32 BE  n_blocks_minus_1
        n_blocks x { 4B ident, u32 n_sections_minus_1, u32 section_table_offset REL TO BI }
    at BI + section_table_offset:
        n_sections x 20B BlockSectionStart { u32 idx, u32 int2, u32 int3, u32 data_offset, u32 int5 }
    at rsrc_data_offset + data_offset:
        u32 BE payload_size, then payload_size bytes   (the prefix is NOT counted in payload_size)

    RUN 1 GOT THE LAST TWO LINES WRONG and its own self-checks C5/C6 caught it (12 of 110 payloads
    outside the data region, coverage 9.7 GB of a 470 kB region), so its tables were printed
    UNTRUSTED and are not a measurement.  The correction was READ OFF THE BYTES, not guessed --
    `tools/bench/t2_rsrc_probe.py` -> `tools/bench/t2_rsrc_probe.log`:
      * section_table_offset is relative to BI itself, not to BI+4: LVSR's 544 lands on 470660,
        which is exactly BI+4+45*12, the first byte after the 12-byte entry table.
      * the record is 20 bytes, not 24: consecutive blocks' offsets step 544, 564, 584, 604, 624,
        and TM80's 18 sections occupy 644..1004, i.e. 18*20.
      * the 4th u32 is the data offset: RTSG's is 164, and LVSR's payload is 160 B at abs 36, so
        32+4+160 = 196 = data_off+164 -- the blocks tile the data region exactly.
      * the 1st u32 is the section index (TM80's run 0,1,2,3,...); the 2nd is 0xffffffff on most
        blocks and 0 on the first.

SELF-CHECK, because a mis-parse must not be reported as a measurement (part D of the fact task):
  C1 magic  C2 info_offset+info_size == filesize  C3 data_offset+data_size == info_offset
  C4 every ident printable ASCII  C5 every payload inside the data region
  C6 payloads + their 4-byte prefixes tile the data region with no overlap
Any check that fails is printed as **FAIL** and written into the JSON as `selfcheck`; the run then
reports what it could parse and flags the tables as UNTRUSTED rather than pretending.

SAFETY
------
Both files are opened 'rb' ONLY.  Nothing is written except `tools/bench/t2_rsrc_blockdiff.json`
and `tools/bench/t2_rsrc_blockdiff.log`.  The ORIGINAL's md5 is taken BEFORE and AFTER the whole
run and both are printed (rule 1).  No LabVIEW, no COM, no lock, no motor, no camera, no GUI.

PREDICTION CONTRACT (CLAUDE.md sec.3 -- recipes state predictions before execution)
-----------------------------------------------------------------------------------
  P1  Both files parse with self-checks C1..C7 all PASS.
  P2  Both sides expose the SAME set of block idents (no one-sided blocks).
  P3  At least one block differs in bytes (the file grew 1,824 B and the md5 changed).
  P4  The ORIGINAL's md5 is 2a78e17c449cacdaf5da389818526859 before AND after.
A failed P1/P2/P3 is a failed prediction and triggers the sec.5 review; P4 failing is a rule-1 alarm.
"""
import hashlib
import json
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))            # ...\V6_ParallelLoop
BENCH = HERE

# --- the two inputs.  LEFT is resolved from the RECIPE's OWN CONSTANTS, not typed from memory. ---
def recipe_constants():
    """Read ORIGINAL / ORIG_MD5 / ARM out of tools/recipes/stage_d1_s1.py WITHOUT importing it
    (importing pulls in gscript -> COM -> LabVIEW).  Returns (orig_path, orig_md5_pin, arm_path)."""
    src = os.path.join(ROOT, "tools", "recipes", "stage_d1_s1.py")
    ns = {}
    with open(src, "r", encoding="utf-8", errors="replace") as fh:
        for ln in fh:
            s = ln.strip()
            if s.startswith("ORIGINAL = os.path.join(os.path.dirname(ROOT),"):
                name = s.split('"')[1]
                ns["ORIGINAL"] = os.path.join(os.path.dirname(ROOT), name)
            elif s.startswith("ORIG_MD5 = "):
                ns["ORIG_MD5"] = s.split('"')[1]
            elif s.startswith("ARM = os.path.join(CLAUDEDEV,"):
                ns["ARM_NAME"] = s.split('"')[1]
    ns.setdefault("CLAUDEDEV", r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev")
    ns["ARM"] = os.path.join(ns["CLAUDEDEV"], ns["ARM_NAME"])
    ns["RECIPE"] = src
    return ns


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def version_bytes(data):
    """PRIOR ART, reused verbatim in behaviour from tools/recipes/stage_d1_s1.py:293 -- the first 64
    bytes as hex and every `?? 00 80 00` run found in them, with its offset."""
    head = data[:64]
    cands = []
    for i in range(len(head) - 3):
        if head[i + 1] == 0x00 and head[i + 2] == 0x80 and head[i + 3] == 0x00 and head[i] != 0x00:
            cands.append({"offset": i, "bytes": " ".join("%02x" % b for b in head[i:i + 4])})
    return {"head64_hex": " ".join("%02x" % b for b in head), "version_candidates": cands}


U32 = ">I"


class ParseError(Exception):
    pass


def parse_rsrc(data, label):
    """Return (record, checks).  Never raises on a malformed file -- it records the failure."""
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        return bool(ok)

    rec = {"label": label, "size": len(data), "blocks": [], "sections": [], "parsed": False}
    rec.update(version_bytes(data))

    magic_ok = data[:8] == b"RSRC\r\n\x00\x03"
    chk("C1 magic RSRC\\r\\n\\x00\\x03", magic_ok, repr(data[:8]))
    if not magic_ok:
        return rec, checks
    rec["file_type"] = data[8:12].decode("latin-1")
    rec["file_creator"] = data[12:16].decode("latin-1")
    info_off, info_size, data_off, data_size = struct.unpack(">4I", data[16:32])
    rec["header"] = {"rsrc_info_offset": info_off, "rsrc_info_size": info_size,
                     "rsrc_data_offset": data_off, "rsrc_data_size": data_size}

    chk("C2 info_offset+info_size == filesize", info_off + info_size == len(data),
        "%d+%d vs %d" % (info_off, info_size, len(data)))
    chk("C3 data_offset+data_size == info_offset", data_off + data_size == info_off,
        "%d+%d vs %d" % (data_off, data_size, info_off))
    if info_off + 32 + 20 > len(data):
        chk("C0 info section inside file", False, "info_off=%d" % info_off)
        return rec, checks

    rec["info_header_repeats"] = (data[info_off:info_off + 32] == data[0:32])
    bil = struct.unpack(">5I", data[info_off + 32:info_off + 52])
    rec["blockinfo_list_header"] = {"int1": bil[0], "int2": bil[1], "int3": bil[2],
                                    "blockinfo_offset": bil[3], "blockinfo_size": bil[4]}
    bi_base = info_off + bil[3]
    if bi_base + 4 > len(data):
        chk("C0b blockinfo inside file", False, "bi_base=%d" % bi_base)
        return rec, checks

    n_blocks = struct.unpack(U32, data[bi_base:bi_base + 4])[0] + 1
    rec["n_blocks"] = n_blocks
    if not chk("C0c block count sane (1..512)", 1 <= n_blocks <= 512, str(n_blocks)):
        return rec, checks

    idents_ok = True
    spans = []          # (start, end, "IDENT#idx") over the DATA region, for the tiling check
    for b in range(n_blocks):
        p = bi_base + 4 + b * 12
        ident_raw = data[p:p + 4]
        n_sec = struct.unpack(U32, data[p + 4:p + 8])[0] + 1
        sec_tbl = struct.unpack(U32, data[p + 8:p + 12])[0]
        ident = ident_raw.decode("latin-1")
        if not all(32 <= c < 127 for c in ident_raw):
            idents_ok = False
        brec = {"ident": ident, "ident_hex": " ".join("%02x" % c for c in ident_raw),
                "n_sections": n_sec, "section_table_offset": sec_tbl, "sections": []}
        for s in range(n_sec):
            q = bi_base + sec_tbl + s * 20        # REL TO BI, 20-byte records (measured, see docstring)
            if q + 20 > len(data):
                brec["sections"].append({"error": "section start table out of range at %d" % q})
                continue
            sec_idx, i2, i3, d_off, i5 = struct.unpack(">i4I", data[q:q + 20])
            i4 = None
            abs_off = data_off + d_off
            if abs_off + 4 > len(data):
                brec["sections"].append({"error": "payload prefix out of range at %d" % abs_off})
                continue
            payload_len = struct.unpack(U32, data[abs_off:abs_off + 4])[0]
            start, end = abs_off + 4, abs_off + 4 + payload_len
            inside = (end <= data_off + data_size)
            payload = data[start:end] if end <= len(data) else b""
            srec = {"ident": ident, "section_idx": sec_idx,
                    "start_abs": start, "payload_len": payload_len,
                    "sha256": hashlib.sha256(payload).hexdigest(),
                    "inside_data_region": inside,
                    "hdr_ints": {"int2": i2, "int3": i3, "int4": i4, "int5": i5},
                    "data_offset_rel": d_off}
            brec["sections"].append(srec)
            rec["sections"].append(srec)
            spans.append((abs_off, end, "%s#%d" % (ident, sec_idx), inside))
        # aggregate over the block's sections, in stored order
        blob = b"".join(data[s["start_abs"]:s["start_abs"] + s["payload_len"]]
                        for s in brec["sections"] if "start_abs" in s)
        brec["total_payload"] = len(blob)
        brec["sha256"] = hashlib.sha256(blob).hexdigest()
        brec["first_offset"] = min([s["start_abs"] for s in brec["sections"] if "start_abs" in s],
                                   default=-1)
        rec["blocks"].append(brec)

    chk("C4 all idents printable ASCII", idents_ok)
    chk("C5 every payload inside the data region", all(sp[3] for sp in spans),
        "%d of %d inside" % (sum(1 for sp in spans if sp[3]), len(spans)))

    spans_sorted = sorted(spans)
    overlap = [(spans_sorted[i][2], spans_sorted[i + 1][2])
               for i in range(len(spans_sorted) - 1) if spans_sorted[i][1] > spans_sorted[i + 1][0]]
    covered = sum(sp[1] - sp[0] for sp in spans_sorted)
    chk("C6 payloads tile the data region, no overlap", not overlap,
        "overlaps=%s covered=%d of data_size=%d" % (overlap[:3], covered, data_size))
    # C7 -- run 2 showed BOTH files short by exactly the same 101 bytes with zero overlaps, which is
    # inter-section ALIGNMENT PADDING, not a mis-parse.  So C7 does not demand exact tiling (that
    # demand was wrong); it MEASURES every gap and fails only if some gap is >= 4 bytes, i.e. if real
    # payload is unaccounted for.  The gap histogram is printed so the claim is data, not assertion.
    gaps = []
    cursor = data_off
    for st, en, tag, _ in spans_sorted:
        gaps.append(st - cursor)
        cursor = en
    gaps.append((data_off + data_size) - cursor)
    big = [g for g in gaps if g >= 4 or g < 0]
    chk("C7 all inter-section gaps are 4-byte alignment padding (0..3)", not big,
        "n_gaps=%d total_pad=%d max=%d offenders=%s" % (len(gaps), sum(gaps), max(gaps), big[:5]))
    rec["data_region_coverage"] = {"covered_bytes": covered, "data_size": data_size,
                                   "uncovered": data_size - covered,
                                   "gap_histogram": {str(v): gaps.count(v) for v in sorted(set(gaps))}}
    rec["parsed"] = True
    return rec, checks


def key_of(block):
    return block["ident"]


def main():
    t0 = time.time()
    C = recipe_constants()
    left_path, right_path = C["ORIGINAL"], C["ARM"]
    lines = []

    def say(s=""):
        print(s, flush=True)
        lines.append(s)

    say("T2 -- OFFLINE RSRC BLOCK-LEVEL DIFF   (read-only; no LabVIEW, no COM, no lock)")
    say("started %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    say("recipe constants read from %s" % C["RECIPE"])
    say("  LEFT  (ORIGINAL) = %s   [pinned md5 %s]" % (left_path, C["ORIG_MD5"]))
    say("  RIGHT (no-edit COM save) = %s" % right_path)
    say()

    for p in (left_path, right_path):
        if not os.path.isfile(p):
            # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): guard_peer's FAILURE_RE anchor cannot see the bold form.
            say("FAIL input missing: %s" % p)
            return 2

    orig_md5_before = md5_of(left_path)
    right_md5_before = md5_of(right_path)
    say("ORIGINAL md5 BEFORE : %s   (pin %s)  -> %s"
        % (orig_md5_before, C["ORIG_MD5"], "MATCH" if orig_md5_before == C["ORIG_MD5"] else "**MISMATCH**"))
    say("RIGHT    md5 BEFORE : %s" % right_md5_before)

    with open(left_path, "rb") as fh:
        ldata = fh.read()
    with open(right_path, "rb") as fh:
        rdata = fh.read()
    say("sizes: LEFT %d B   RIGHT %d B   delta %+d B" % (len(ldata), len(rdata), len(rdata) - len(ldata)))
    say()

    lrec, lchk = parse_rsrc(ldata, "ORIGINAL")
    rrec, rchk = parse_rsrc(rdata, "SAVED")
    say("SELF-CHECKS (a mis-parse must not be reported as a measurement)")
    for side, chks in (("LEFT ", lchk), ("RIGHT", rchk)):
        for c in chks:
            say("  %s  %s  %s%s" % (side, "PASS" if c["ok"] else "**FAIL**", c["check"],
                                    ("   " + c["detail"]) if c["detail"] else ""))
    trusted = all(c["ok"] for c in lchk + rchk) and lrec["parsed"] and rrec["parsed"]
    say("  => tables are %s" % ("TRUSTED" if trusted else "**UNTRUSTED (a self-check failed)**"))
    for side, rec in (("LEFT ", lrec), ("RIGHT", rrec)):
        say("  %s  gap histogram (bytes of padding -> how many gaps): %s"
            % (side, rec.get("data_region_coverage", {}).get("gap_histogram")))
    say()

    for side, rec in (("LEFT  ORIGINAL", lrec), ("RIGHT SAVED   ", rrec)):
        h = rec.get("header", {})
        say("%s : type=%s creator=%s  info_off=%d info_size=%d data_off=%d data_size=%d  blocks=%s"
            % (side, rec.get("file_type"), rec.get("file_creator"), h.get("rsrc_info_offset", -1),
               h.get("rsrc_info_size", -1), h.get("rsrc_data_offset", -1), h.get("rsrc_data_size", -1),
               rec.get("n_blocks")))
        say("%s : version candidates %s" % (side, rec.get("version_candidates")))
    say()

    lmap = {key_of(b): b for b in lrec["blocks"]}
    rmap = {key_of(b): b for b in rrec["blocks"]}
    say("PER-BLOCK TABLE -- LEFT (ORIGINAL), %d blocks" % len(lrec["blocks"]))
    say("  %-6s %5s %10s %10s  %s" % ("ident", "n_sec", "offset", "size", "sha256"))
    for b in lrec["blocks"]:
        say("  %-6s %5d %10d %10d  %s" % (b["ident"], b["n_sections"], b["first_offset"],
                                          b["total_payload"], b["sha256"]))
    say()
    say("PER-BLOCK TABLE -- RIGHT (SAVED), %d blocks" % len(rrec["blocks"]))
    say("  %-6s %5s %10s %10s  %s" % ("ident", "n_sec", "offset", "size", "sha256"))
    for b in rrec["blocks"]:
        say("  %-6s %5d %10d %10d  %s" % (b["ident"], b["n_sections"], b["first_offset"],
                                          b["total_payload"], b["sha256"]))
    say()

    same, diff, only_l, only_r = [], [], [], []
    for k in sorted(set(lmap) | set(rmap)):
        if k in lmap and k in rmap:
            (same if lmap[k]["sha256"] == rmap[k]["sha256"] else diff).append(k)
        elif k in lmap:
            only_l.append(k)
        else:
            only_r.append(k)

    say("SET 1 -- PRESENT ON BOTH AND BYTE-IDENTICAL : %d" % len(same))
    for k in same:
        say("  %-6s  %d B  %s" % (k, lmap[k]["total_payload"], lmap[k]["sha256"]))
    say()
    say("SET 2 -- PRESENT ON BOTH AND DIFFERENT : %d" % len(diff))
    for k in diff:
        lb, rb = lmap[k], rmap[k]
        say("  %-6s  LEFT  %8d B  n_sec=%d  %s" % (k, lb["total_payload"], lb["n_sections"], lb["sha256"]))
        say("  %-6s  RIGHT %8d B  n_sec=%d  %s" % ("", rb["total_payload"], rb["n_sections"], rb["sha256"]))
        say("  %-6s  delta %+d B" % ("", rb["total_payload"] - lb["total_payload"]))
        for ls, rs in zip(lb["sections"], rb["sections"]):
            if "sha256" in ls and "sha256" in rs and ls["sha256"] != rs["sha256"]:
                say("           section %d: %d B %s  ->  %d B %s"
                    % (ls["section_idx"], ls["payload_len"], ls["sha256"][:16],
                       rs["payload_len"], rs["sha256"][:16]))
    say()
    say("SET 3 -- PRESENT ON ONE SIDE ONLY : LEFT-only %d %s ; RIGHT-only %d %s"
        % (len(only_l), only_l, len(only_r), only_r))
    for k in only_l:
        say("  LEFT-only  %-6s %d B %s" % (k, lmap[k]["total_payload"], lmap[k]["sha256"]))
    for k in only_r:
        say("  RIGHT-only %-6s %d B %s" % (k, rmap[k]["total_payload"], rmap[k]["sha256"]))
    say()

    tot_l = sum(b["total_payload"] for b in lrec["blocks"])
    tot_r = sum(b["total_payload"] for b in rrec["blocks"])
    say("TOTALS: identical=%d  different=%d  left-only=%d  right-only=%d ; payload bytes %d -> %d (%+d)"
        % (len(same), len(diff), len(only_l), len(only_r), tot_l, tot_r, tot_r - tot_l))
    say()

    # PREDICTION CONTRACT
    preds = [
        ("P1 both parse, self-checks C1..C7 all PASS", trusted),
        ("P2 same set of block idents on both sides", not only_l and not only_r),
        ("P3 at least one block differs", len(diff) > 0),
    ]
    say("PREDICTION CONTRACT")
    for name, ok in preds:
        # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): guard_peer's FAILURE_RE anchor cannot see the bold form.
        say("  %s  %s" % ("PASS" if ok else "FAIL", name))

    out_json = os.path.join(BENCH, "t2_rsrc_blockdiff.json")
    payload = {
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "left": {"path": left_path, "md5_pin": C["ORIG_MD5"], "md5_before": orig_md5_before},
        "right": {"path": right_path, "md5_before": right_md5_before},
        "selfchecks": {"left": lchk, "right": rchk, "trusted": trusted},
        "left_table": lrec, "right_table": rrec,
        "sets": {"identical": same, "different": diff, "left_only": only_l, "right_only": only_r},
        "predictions": {n: bool(o) for n, o in preds},
    }
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)

    orig_md5_after = md5_of(left_path)
    right_md5_after = md5_of(right_path)
    say("ORIGINAL md5 AFTER  : %s   -> %s"
        % (orig_md5_after, "UNCHANGED" if orig_md5_after == orig_md5_before else "**CHANGED -- RULE 1 ALARM**"))
    say("RIGHT    md5 AFTER  : %s   -> %s"
        % (right_md5_after, "UNCHANGED" if right_md5_after == right_md5_before else "**CHANGED**"))
    say("P4 ORIGINAL md5 == pin, before AND after : %s"
        % ("PASS" if orig_md5_before == orig_md5_after == C["ORIG_MD5"] else "**FAIL**"))
    say()
    say("ARTEFACT %s  md5 %s  %d B" % (out_json, md5_of(out_json), os.path.getsize(out_json)))
    say("elapsed %.1f s" % (time.time() - t0))

    out_log = os.path.join(BENCH, "t2_rsrc_blockdiff.log")
    with open(out_log, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("ARTEFACT %s  md5 %s  %d B" % (out_log, md5_of(out_log), os.path.getsize(out_log)))
    return 0 if all(o for _, o in preds) and orig_md5_after == C["ORIG_MD5"] else 1


if __name__ == "__main__":
    sys.exit(main())
