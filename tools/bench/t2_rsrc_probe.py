#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
T2 PROBE -- read-only hex dump of a .vi's RSRC INFO SECTION, so the block table is MEASURED
instead of guessed.  Run 1 of `t2_rsrc_blockdiff.py` self-detected a mis-parse (checks C5/C6
FAIL: 12 of 110 payloads outside the data region, absurd coverage), so the layout of the
per-block section table is read off the bytes here before the parser is changed again.

Read-only: opens the ORIGINAL 'rb', prints, writes tools/bench/t2_rsrc_probe.log.  No LabVIEW.
"""
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ARM = os.path.join(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev",
                   "D1_s1arm_savetest.vi")

lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def hexdump(data, base, n, tag):
    say("--- %s  (abs offset %d = 0x%x, %d bytes)" % (tag, base, base, n))
    for i in range(0, n, 16):
        chunk = data[base + i:base + i + 16]
        if not chunk:
            break
        h = " ".join("%02x" % b for b in chunk)
        a = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        say("  %08x  %-47s  %s" % (base + i, h, a))


def probe(path, tag):
    with open(path, "rb") as fh:
        data = fh.read()
    say("=" * 100)
    say("%s : %s" % (tag, path))
    say("size %d B  md5 %s" % (len(data), hashlib.md5(data).hexdigest()))
    info_off, info_size, data_off, data_size = struct.unpack(">4I", data[16:32])
    say("header: info_off=%d info_size=%d data_off=%d data_size=%d" % (info_off, info_size, data_off, data_size))
    hexdump(data, 0, 64, "FILE HEADER")
    hexdump(data, info_off, 96, "INFO SECTION START (repeat of header + BlockInfoListHeader)")
    bil = struct.unpack(">5I", data[info_off + 32:info_off + 52])
    say("BlockInfoListHeader u32s: %s   (candidate blockinfo_offset = %d -> abs %d)"
        % (list(bil), bil[3], info_off + bil[3]))
    bi = info_off + bil[3]
    hexdump(data, bi, 160, "BLOCK INFO LIST (count u32 then 12B entries)")
    n = struct.unpack(">I", data[bi:bi + 4])[0]
    say("raw count field = %d  (so n_blocks = %d if count-1 convention)" % (n, n + 1))
    say()
    say("BLOCK ENTRIES, raw:")
    say("  %3s %-6s %10s %10s   %s" % ("#", "ident", "u32_b", "u32_c", "abs of u32_c rel to bi / bi+4"))
    for b in range(n + 1):
        p = bi + 4 + b * 12
        ident = data[p:p + 4].decode("latin-1")
        u1, u2 = struct.unpack(">2I", data[p + 4:p + 12])
        say("  %3d %-6s %10d %10d   %10d %10d" % (b, ident, u1, u2, bi + u2, bi + 4 + u2))
    end_of_entries = bi + 4 + (n + 1) * 12
    say()
    say("end of 12B entries = abs %d ; info section ends at %d ; %d bytes remain"
        % (end_of_entries, info_off + info_size, info_off + info_size - end_of_entries))
    hexdump(data, end_of_entries, 256, "BYTES RIGHT AFTER THE ENTRY TABLE (section-start records?)")
    say()
    hexdump(data, data_off, 64, "DATA REGION START")
    return data


def main():
    probe(ORIGINAL, "ORIGINAL (LEFT)")
    probe(ARM, "SAVED ARM (RIGHT)")
    out = os.path.join(HERE, "t2_rsrc_probe.log")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print("ARTEFACT %s  %d B" % (out, os.path.getsize(out)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
