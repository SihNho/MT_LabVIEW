"""inspect_imaqdx.py - read the connector panes of the IMAQdx VIs the camera harness will need.

The work cycle forbids mid-run name discovery: every terminal name a build uses must be resolved at planning time. This
reads the panes of the acquisition VIs found on 2026-09-12 inside
`C:\\Program Files\\NI\\LVAddons\\niimaqdx\\1\\vi.lib\\vision\\driver\\IMAQdx.llb` so the harness recipe can be written
against facts.

What the harness has to answer, now that the user has cleared all four instruments for operation while the rig is
disassembled:
  1. the camera's real ceiling at the 2x2 binning it runs today - 90 Hz is normal and 150 Hz is wanted, but the sensor
     reads 62 fps at full resolution, so the ceiling may be below the target and no software change can pass it;
  2. the acquisition cost on its own, with no tracking and no display, which is term A of the A+B+W budget;
  3. whether the display destabilises frames because of its draw cost or because it is wired to follow the camera's
     buffer SEQUENCE (`Buffer Number Mode` = Next) rather than taking the newest frame (`Last`).

`IMAQdx Configure Grab` also carries the host ring depth, which is the jitter margin: with 64 GB of RAM a deep ring is
almost free, and a shallow one turns any hiccup into lost frames.

READ-ONLY: opens no camera, acquires nothing, modifies nothing.
  py tools/bgrun.py --max-min 20 --log tools/bench/inspect_imaqdx.log -- py -u tools/bench/inspect_imaqdx.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

LLB = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb"
TARGETS = ["IMAQdx Open Camera.vi", "IMAQdx Configure Grab.vi", "IMAQdx Configure Acquisition.vi",
           "IMAQdx Get Image.vi", "IMAQdx Get Image2.vi", "IMAQdx Grab.vi",
           "IMAQdx Stop Acquisition.vi", "IMAQdx Close Camera.vi",
           "IMAQdx Calculate Frames per Second.vi", "IMAQdx Get Buffer Difference.vi",
           "IMAQdx Enumerate Attributes.vi", "IMAQdx Enumerate Cameras.vi"]
g._run.__defaults__ = (6.0, 45.0)


def main():
    g._lv = None
    for name in TARGETS:
        p = os.path.join(LLB, name)
        print(f"\n{'=' * 78}\n== {name}", flush=True)
        try:
            labs = g.fp_labels(p)
        except Exception as e:
            print("   fp_labels failed:", str(e)[:160], flush=True); continue
        ctrls = [l for _, l, ind in labs if not ind]
        inds = [l for _, l, ind in labs if ind]
        print(f"   controls ({len(ctrls)}): {ctrls}", flush=True)
        print(f"   indicators ({len(inds)}): {inds}", flush=True)
    print("\nDONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
