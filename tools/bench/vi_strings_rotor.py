"""vi_strings_rotor.py - find the ROTOR ZERO OFFSET in the main VI, by reading the file's own strings.

WHY. The rotor row of the scheduler holds ABSOLUTE degrees, so `-7200` has to be measured from somewhere. Asked
where zero is, the user said (2026-09-13):

    "내 기억이 정확하다면 컨트롤러 절대좌표가 아마 음수를 지원 안해줬을거임. 그래서 임의로 중간지점을 내가 0으로
     잡은 것 같은데, 이게 정확하다면 main vi 코드 상에 분명 잡혀있을 수 밖에 없음."

That is the decisive observation, and it turns a question for the user into a search in the code: if the
controller's absolute coordinate cannot go negative, yet the user types negative values, then SOMETHING in the main
VI adds an offset before the command goes out. That offset is the zero, and it is a number sitting in the diagram.

STRATEGY - cheapest first, and this file is the cheap one. LabVIEW stores control labels, string constants and
property names as literal text inside the VI's zlib-compressed streams, so a read of the FILE can tell us which
rotor-related names exist at all, before any LabVIEW session is spent. The authoritative follow-up is the COM scan
(which constant is wired to which terminal); this one costs nothing and narrows where to look.

CAVEAT, from the skill and worth repeating because it has burned this project before: compiled machine code in the
same streams produces convincing ASCII noise, so **one string is a hint, never proof**. A run of related names is
much stronger than any single hit.

READ-ONLY in the strictest sense: opened 'rb', never written, LabVIEW not involved - safe on the original as well
as the working copy (CLAUDE.md rule 1: reading bytes is not modifying).

  py tools/bench/vi_strings_rotor.py [path-to-vi]
"""
import re
import sys
import zlib

DEFAULT = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
           r"\Min_Track N beads V6_ParallelLoop.vi")

# Terms that would appear near a rotor offset. Deliberately broad: a miss here costs a grep, a false negative
# costs a wrong design decision.
PATTERNS = [
    r"[Rr]ot\w*", r"MOV\b", r"MVR\b", r"MovePos\w*", r"Pos_?degree", r"[Dd]egree",
    r"[Oo]ffset", r"[Zz]ero", r"[Tt]urn", r"[Aa]ngle", r"[Ss]pin", r"[Tt]wist",
    r"[Aa]bsolute", r"[Rr]elative", r"7200", r"3600", r"1800",
]
RX = re.compile("|".join(f"({p})" for p in PATTERNS))
PRINTABLE = re.compile(rb"[\x20-\x7e]{4,}")


def streams(data):
    """Every inflatable zlib stream in the file, plus the raw bytes themselves."""
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
    print(f"{path}\n{len(data):,} bytes\n", flush=True)

    seen = {}
    n_streams = 0
    for name, blob in streams(data):
        n_streams += 1
        for m in PRINTABLE.finditer(blob):
            s = m.group().decode("ascii", "replace")
            if RX.search(s):
                seen.setdefault(s, []).append(name)

    print(f"{n_streams} streams scanned, {len(seen)} distinct matching strings\n", flush=True)
    # Short, name-like strings first: a control label is what we are after, not a sentence of machine noise.
    for s in sorted(seen, key=lambda x: (len(x), x)):
        if len(s) > 90:
            continue
        where = seen[s]
        print(f"  {s!r:60}  x{len(where)}", flush=True)

    print("\n--- longer hits (more likely noise, shown for completeness) ---", flush=True)
    for s in sorted(seen, key=lambda x: (len(x), x)):
        if len(s) <= 90:
            continue
        print(f"  {s[:150]!r}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
