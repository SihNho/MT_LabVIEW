"""inspect_imaqdx_examples.py - pick the acquisition harness base from NI's shipped IMAQdx examples.

Building a camera harness node by node would be days of scripting. NI ships examples that already answer our questions
almost exactly, so the cheap move is to copy one and drive it:

  Acquire Every Image.vi        - the loop that must KEEP UP with the camera. Its achieved rate is the ceiling at the
                                  current 2x2 binning, which decides whether the wanted 150 Hz is even reachable before
                                  any software work is justified (the sensor does 62 fps at full resolution).
  Acquire Most Recent Image.vi  - the `Last` buffer mode, i.e. the decoupled display the user's frame instability points
                                  at. Comparing the two IS the experiment.
  Parallel Processing.vi        - acquisition and processing in separate loops, the pattern the main VI already uses.

This reads their front panels so the harness recipe knows which controls to set and which indicators to read. Whether
the IMAQdx Session control accepts a plain camera-name string over COM is the one unknown that decides how the harness
is driven, and it is listed here rather than assumed.

READ-ONLY: copies are inspected in claudeDev and deleted; no camera is opened and nothing is acquired.
  py tools/bgrun.py --max-min 20 --log tools/bench/inspect_imaqdx_examples.log -- py -u tools/bench/inspect_imaqdx_examples.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EX = r"C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision Acquisition\NI-IMAQdx"
TARGETS = [
    ("Acquire Every Image", os.path.join(EX, "Basic Acquisition", "Acquire Every Image.vi")),
    ("Acquire Every Image (Optimized)", os.path.join(EX, "Basic Acquisition", "Acquire Every Image (Optimized Performance).vi")),
    ("Acquire Most Recent Image", os.path.join(EX, "Basic Acquisition", "Acquire Most Recent Image.vi")),
    ("Parallel Processing", os.path.join(EX, "Design Patterns", "Parallel Processing.vi")),
]
g._run.__defaults__ = (6.0, 45.0)


def main():
    g._lv = None
    for label, src in TARGETS:
        print(f"\n{'=' * 78}\n== {label}\n   {src}", flush=True)
        if not os.path.exists(src):
            print("   MISSING", flush=True); continue
        dst = os.path.join(g.CLAUDEDEV, "EXAMPLE_" + os.path.basename(src))
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copyfile(src, dst)
        try:
            counts = {c: g.count(dst, c) for c in ("Node", "SubVI", "Diagram", "WhileLoop", "CaseStructure", "Wire")}
            print("   objects:", {k: v for k, v in counts.items() if v}, flush=True)
            labs = g.fp_labels(dst)
            print("   controls:", [l for _, l, ind in labs if not ind], flush=True)
            print("   indicators:", [l for _, l, ind in labs if ind], flush=True)
        except Exception as e:
            print("   failed:", str(e)[:160], flush=True)
        finally:
            try:
                g.close_panel(dst)
            except Exception:
                pass
            time.sleep(0.3)
            try:
                os.remove(dst)
            except OSError:
                pass
    print("\nDONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
