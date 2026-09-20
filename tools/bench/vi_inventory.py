"""vi_inventory.py - first-pass inventory of a .vi: every subVI it names, every port/protocol string, every label.

PURPOSE. The user's 2026-09-13 direction is to understand and DOCUMENT the system before building, starting with
the instrument libraries: *"본격적으로 메인 작업 시작하기 전에 각 instrument library 확인하는게 필수겠다"*. This is
the cheapest first cut - it needs no LabVIEW session at all, so it runs while the scripted inventory is still
being built, and it produces the raw list the instrument document is written from.

WHAT IT IS AND IS NOT. LabVIEW stores subVI paths, control labels and string constants as literal text inside the
VI's zlib-compressed streams, so this recovers NAMES. It recovers **no wiring** - it cannot say which subVI is
called where, whether a control is connected, or what the configuration block sets. Those need the scripted
inventory (docs/system-inventory-plan.md). Treated as more than a name list, this file would mislead.

And the standing caveat, which has already caught this project once: compiled machine code in the same streams
produces convincing ASCII, so a lone string is a hint, not proof. A `.vi` extension or a coherent group is strong;
a single odd word is not.

READ-ONLY in the strictest sense: opened 'rb', never written, LabVIEW not involved - safe on originals
(CLAUDE.md rule 1: reading bytes is not modifying).

  py tools/bench/vi_inventory.py [path-to-vi] > docs/raw/<name>-inventory.txt
"""
import os
import re
import sys
import zlib

DEFAULT = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
           r"\Min_Track N beads V6_ParallelLoop.vi")

PRINTABLE = re.compile(rb"[\x20-\x7e]{3,}")
VI_NAME = re.compile(r"[A-Za-z0-9 _\-.,()+&#'\[\]]+\.vi\b")
# Serial / instrument configuration: COM ports, baud rates, VISA resource names, GPIB.
PORT = re.compile(r"\b(COM\d+|ASRL\d+(::INSTR)?|GPIB\d*::\d+|TCPIP\d*::[\w.]+)\b", re.I)
BAUD = re.compile(r"\b(1200|2400|4800|9600|19200|38400|57600|115200|230400)\b")


def streams(data):
    yield "raw", data
    for i in range(len(data) - 1):
        if data[i] != 0x78:
            continue
        try:
            out = zlib.decompressobj().decompress(data[i:])
        except zlib.error:
            continue
        if len(out) > 64:
            yield f"zlib@{i}", out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    with open(path, "rb") as f:
        data = f.read()
    print(f"# Inventory of {os.path.basename(path)}")
    print(f"# {path}")
    print(f"# {len(data):,} bytes\n")

    subvis, ports, bauds, texts = {}, {}, {}, set()
    for _name, blob in streams(data):
        for m in PRINTABLE.finditer(blob):
            s = m.group().decode("ascii", "replace")
            texts.add(s)
            for v in VI_NAME.findall(s):
                v = v.strip()
                subvis[v] = subvis.get(v, 0) + 1
            for p in PORT.findall(s):
                p0 = p[0] if isinstance(p, tuple) else p
                ports[p0.upper()] = ports.get(p0.upper(), 0) + 1
            if len(s) < 80:
                for b in BAUD.findall(s):
                    bauds.setdefault(b, set()).add(s)

    print(f"## SubVIs named in the file ({len(subvis)})\n")
    for v in sorted(subvis, key=str.lower):
        print(f"  {subvis[v]:3d}x  {v}")

    print(f"\n## Ports / VISA resources ({len(ports)})\n")
    for p in sorted(ports):
        print(f"  {ports[p]:3d}x  {p}")

    print(f"\n## Baud-rate-looking numbers, with the string they sat in ({len(bauds)})\n")
    for b in sorted(bauds, key=int):
        for s in sorted(bauds[b])[:6]:
            print(f"  {b:>6}  in  {s!r}")

    print("\n## Short label-like strings (<= 40 chars), which is most of the front panel\n")
    labels = sorted({t for t in texts if 2 < len(t) <= 40 and not t.startswith("$")}, key=str.lower)
    for t in labels:
        print(f"  {t!r}")
    print(f"\n# {len(labels)} label-like strings, {len(texts)} strings total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
