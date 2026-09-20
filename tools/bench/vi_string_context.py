"""vi_string_context.py - show WHERE a string sits in a .vi and what surrounds it.

WHY. A flat list of extracted strings invites exactly the mistake it just caused. The scan found

    'M-126.PD1, COM4 9600'   'M-126.PD1, COM5 115200'   'Rot, COM3 9600'   'Rot, COM2 115200'

and I wrote them up as "per-room configuration pairs". The user's correction was immediate and obviously right:

    "로터에 컴포트 두개가 잡힐 수가 없지. 다시 확인해보라고..."

A device has ONE port. So the four strings are not four configurations - they are more likely the cached item
list of a VISA resource-name control's dropdown (which shows every aliased serial resource NI-MAX knows about,
including stale ones from other setups), or NI-MAX aliases, or constants in different branches. A flat list
cannot tell those apart. Their NEIGHBOURS can: items of one ring sit together in one stream, in order.

So this prints, for each target string, the stream it lives in, its byte offset, and the strings immediately
before and after it. That is evidence about structure, not another guess.

It still does not prove which is WIRED - only the scripted read of the configuration constants does that. This
just stops the next hypothesis from being invented out of a sorted list.

READ-ONLY: opened 'rb', never written, no LabVIEW.
  py tools/bench/vi_string_context.py [pattern] [path-to-vi]
"""
import re
import sys
import zlib

DEFAULT = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
           r"\Min_Track N beads V6_ParallelLoop.vi")
PRINTABLE = re.compile(rb"[\x20-\x7e]{3,}")
NEIGHBOURS = 6


def streams(data):
    yield "raw@0", data
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
    pat = sys.argv[1] if len(sys.argv) > 1 else r"COM\d|Rot,|M-126|VISA|Baud|[Pp]ort"
    path = sys.argv[2] if len(sys.argv) > 2 else DEFAULT
    rx = re.compile(pat)
    with open(path, "rb") as f:
        data = f.read()
    print(f"pattern {pat!r}\n{path}\n", flush=True)

    for sname, blob in streams(data):
        found = []
        items = [(m.start(), m.group().decode("ascii", "replace")) for m in PRINTABLE.finditer(blob)]
        for idx, (off, s) in enumerate(items):
            if rx.search(s):
                found.append(idx)
        if not found:
            continue
        print(f"\n{'=' * 78}\n{sname}   ({len(blob):,} bytes, {len(items)} strings, {len(found)} matching)",
              flush=True)
        shown = set()
        for idx in found:
            lo, hi = max(0, idx - NEIGHBOURS), min(len(items), idx + NEIGHBOURS + 1)
            if all(i in shown for i in range(lo, hi)):
                continue
            print(f"\n  --- around string #{idx} (offset {items[idx][0]}) ---", flush=True)
            for i in range(lo, hi):
                mark = ">>" if i == idx else "  "
                s = items[i][1]
                print(f"  {mark} [{i:5d}] {s[:110]!r}", flush=True)
                shown.add(i)
    return 0


if __name__ == "__main__":
    sys.exit(main())
