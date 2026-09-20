"""vi_strings_camera.py - pull the camera attribute names straight out of the .vi file, with no LabVIEW at all.

A LabVIEW property node stores the names of the properties it touches as literal strings inside the VI's compressed
block-diagram streams, IN THE ORDER THE TERMINALS APPEAR - and for an IMAQdx property node those names are the GenICam
attribute paths, e.g. `CameraAttributes::ImageFormatControl::BinningHorizontal`. Order is the whole question behind the
user's "first run halves the image": a property node executes its terminals top to bottom, so writing Width before
Binning lets the camera divide the width by the new binning factor and produce exactly half.

This is the cheap parallel route to the COM diagram scan. The COM scan is authoritative (it knows which node is which
and what constant is wired where); this one costs nothing, runs while the other is blocked on loading the main VI, and
either confirms the attribute set or shows there is no IMAQdx property node at all.

Caveat from the skill: compiled machine code in the same streams produces convincing ASCII noise, so a single string is
a hint, not proof. A whole ordered RUN of GenICam paths is much stronger than any one of them.

READ-ONLY in the strictest sense: the file is opened 'rb' and never written. LabVIEW is not involved, so this is safe
to run against the ORIGINAL as well as the working copy (CLAUDE.md rule 1 - reading bytes is not modifying).
  py tools/bench/vi_strings_camera.py [path-to-vi]
"""
import re, sys, zlib

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
PATH = sys.argv[1] if len(sys.argv) > 1 else WORK
# GenICam attribute paths, plus the IMAQdx VI names that would appear if the config uses Set Attribute rather than a
# property node. \x20-\x7e keeps it to printable ASCII so compiled-code noise cannot masquerade as a long path.
PAT = re.compile(rb"(?:CameraAttributes|AcquisitionAttributes|CameraInformation)::[\x20-\x7e]{3,90}")
IMAQ = re.compile(rb"IMAQdx[\x20-\x7e]{0,60}\.vi")


def streams(blob):
    """Every zlib stream in the file, inflated. LabVIEW stores block-diagram content compressed; offsets are not
    documented, so scan for the 0x78 header bytes and try each one."""
    out = [(0, blob)]                                   # the raw file too: some strings are stored uncompressed
    for m in re.finditer(rb"\x78[\x01\x5e\x9c\xda]", blob):
        try:
            d = zlib.decompressobj().decompress(blob[m.start():])
        except zlib.error:
            continue
        if len(d) > 64:
            out.append((m.start(), d))
    return out


def main():
    blob = open(PATH, "rb").read()
    print(f"{PATH}\n   {len(blob):,} bytes", flush=True)
    seen_order, seen = [], set()
    imaq = set()
    n_streams = 0
    for off, data in streams(blob):
        n_streams += 1
        for m in PAT.finditer(data):
            s = m.group().decode("latin-1")
            if s not in seen:
                seen.add(s); seen_order.append((off, m.start(), s))
        for m in IMAQ.finditer(data):
            imaq.add(m.group().decode("latin-1"))
    print(f"   {n_streams} streams scanned (1 raw + {n_streams - 1} inflated)", flush=True)

    print(f"\n=== GenICam attribute paths found, IN FILE ORDER ({len(seen_order)}) ===", flush=True)
    for off, pos, s in seen_order:
        mark = "  <== GEOMETRY" if any(k in s.lower() for k in
                                       ("width", "height", "binning", "offsetx", "offsety", "pixelformat")) else ""
        print(f"   stream@{off:<9} +{pos:<7} {s}{mark}", flush=True)
    if not seen_order:
        print("   NONE - the configuration does not name attributes as literal strings in this file "
              "(they may sit in a subVI, or be selected by a property node's binary item ids)", flush=True)

    print(f"\n=== IMAQdx VIs referenced ({len(imaq)}) ===", flush=True)
    for s in sorted(imaq):
        print("   ", s, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
