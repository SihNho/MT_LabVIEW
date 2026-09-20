"""find_rotor_controls.py - is `Auto-reset zero` a real front-panel control, and where is it?

The byte scan (tools/bench/vi_strings_rotor.py) found the NAME four times, but a string in a .vi is a hint, not
proof - compiled code in the same streams produces convincing ASCII. `Panel.Controls[]` is proof: it enumerates the
front panel's actual objects.

Prints every front-panel object whose label looks rotor- or zero-related, with its TABBING INDEX, so the control can
then be located on screen. Read-only: the working copy is opened but never edited or saved.

  py tools/bench/find_rotor_controls.py
"""
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
        r"\Min_Track N beads V6_ParallelLoop.vi")
RX = re.compile(r"rot|zero|angle|turn|degree|deg\b|cal ", re.I)
g._run.__defaults__ = (6.0, 300.0)


def main():
    g._lv = None
    print("reading the working copy's front panel (read-only)...", flush=True)
    t0 = time.time()
    rows = g.fp_labels(MAIN, max_n=400)
    print(f"{len(rows)} front-panel objects in {time.time() - t0:.1f} s\n", flush=True)

    hits = [(i, lab, ind) for i, lab, ind in rows if lab and RX.search(lab)]
    print(f"== {len(hits)} rotor/zero-related front-panel objects ==", flush=True)
    for i, lab, ind in hits:
        print(f"   index {i:3d}  {'IND' if ind else 'CTL'}  {lab!r}", flush=True)

    exact = [(i, lab, ind) for i, lab, ind in rows if lab and lab.strip().lower().startswith("auto-res")]
    print(f"\n== exact 'Auto-reset zero' matches: {len(exact)} ==", flush=True)
    for row in exact:
        print("   ", row, flush=True)
    if not exact:
        print("   NOT on the front panel - so the string is either a diagram-only label,", flush=True)
        print("   a subVI's control, or byte noise. That distinction matters and is not glossed.", flush=True)

    print("\n== full label list (for context) ==", flush=True)
    for i, lab, ind in rows:
        print(f"   {i:3d} {'IND' if ind else 'CTL'} {lab!r}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
