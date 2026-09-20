"""main_vi_camera_values.py - read the main VI's camera-related control VALUES, without running it.

The byte scan (tools/bench/vi_strings_camera.py) established the shape of the configuration step without LabVIEW:
the main VI calls only six IMAQdx VIs - Open Camera, Configure Grab, Get Image, Grab, Stop Acquisition, Close Camera -
and NONE of them sets an attribute. The geometry is written by an **IMAQdx property node**, identifiable in the file
bytes by the terminal names `Width&2` / `Height&2` sitting immediately before the literal `IMAQdx`; separately there
are front-panel numeric controls literally labelled `Width` and `Height` (stored as `DigNum (strict)`) read through
`Value` property nodes.

Two consequences worth stating, because they kill two hypotheses:
  * **Binning is never written by the main VI** - the string does not appear anywhere in the file. So the halving
    cannot be the classic GenICam "write Width, then set binning, camera divides the width" ordering bug, which was
    the leading explanation before this scan.
  * The camera itself does not persist the halved state either: a fresh `IMAQdxOpenCamera` read back the full
    1280 x 1024 minutes after another read had found 640 x 512.

What is left is simply **what number the property node is given**. This reads the front-panel values for every
camera-ish control. It does not run the VI, so these are the saved/current values the first run would use.

READ-ONLY: GetVIReference + GetControlValue only. Never runs, never saves, never modifies. No hardware.
  py tools/bench/main_vi_camera_values.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
KEYS = ("width", "height", "binning", "offset", "camera", "cam", "frame", "rate", "exposure", "buffer", "roi",
        "pixel", "nm", "calib", "bin")


def main():
    g._lv = None
    labs = g.fp_labels(WORK, max_n=400)
    print(f"{len(labs)} front-panel objects", flush=True)
    hits = [(uid, lbl, ind) for uid, lbl, ind in labs if any(k in lbl.lower() for k in KEYS)]
    print(f"{len(hits)} camera-related\n", flush=True)
    vi = g.lv().GetVIReference(WORK, "", False, 0)
    for uid, lbl, ind in hits:
        try:
            v = vi.GetControlValue(lbl)
        except Exception as e:
            v = f"(unreadable: {str(e)[:70]})"
        kind = "indicator" if ind else "CONTROL  "
        print(f"   {kind} {lbl!r:<46} = {v!r}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
