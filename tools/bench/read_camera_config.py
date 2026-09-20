"""read_camera_config.py - get the camera name and grab settings from the user's OWN code, not by guessing.

The NI example's `Camera Name` control reads back as the tuple ('', 0), i.e. an IMAQdx Session control rather than a
plain string, and running it empty popped a modal error. The user's point stands: the main VI already opens this camera,
so the name and the configuration are in their code and in NI MAX, and there is nothing to guess.

This reads, from the working copy: every front-panel control whose label looks camera-related together with its current
value, and the `IMAQdx Open Camera` / `Configure Grab` call sites with whatever feeds them. Read-only; the camera is not
opened here.
  py tools/bgrun.py --max-min 20 --log tools/bench/read_camera_config.log -- py -u tools/bench/read_camera_config.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
KEYS = ("camera", "imaqdx", "session", "cam", "grab", "buffer", "width", "height", "binning", "exposure",
        "frame", "roi", "pixel", "acquis")
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    print("target:", WORK, flush=True)
    labs = g.fp_labels(WORK)
    print(f"front-panel objects: {len(labs)}", flush=True)
    vi = g.lv().GetVIReference(WORK, "", False, 0)
    print("\n=== camera-related front-panel objects and their current values ===", flush=True)
    for i, lab, ind in labs:
        if not lab or not any(k in lab.lower() for k in KEYS):
            continue
        try:
            val = vi.GetControlValue(lab)
            val = (str(val)[:90] + "...") if len(str(val)) > 90 else val
        except Exception as e:
            val = f"(unreadable: {str(e)[:50]})"
        print(f"   [{i:3}] {'IND ' if ind else 'CTRL'} {lab!r} = {val!r}", flush=True)
    print("\n=== ALL front-panel labels, for context ===", flush=True)
    print("   " + ", ".join(repr(l) for _, l, _ in labs), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
