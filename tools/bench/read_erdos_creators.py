"""read_erdos_creators.py - do the erdosmiller creator VIs already expose an "allow private" input?

THE CHEAPEST STEP of the fix for private members. Our builders (`OpBuildInvoke_v0`, `OpBuildPN_v0`) wrap
erdosmiller's `Create Invoke Node.vi` / `Create Property Node.vi`, and those wrappers are where the ordinary
`Set Method` (6370002) would be called instead of `Set Method (Allow Private)` (6370003).

If the erdosmiller VI already HAS an input for this - an `allow private?` boolean, or an `Allow Alternate
Names?` flag, or a method-ID string terminal we are feeding wrongly - then the fix is one op parameter, not a
rebuild of the keystone. That is worth 30 seconds before designing anything.

If it does NOT, the terminal list still tells us exactly what the wrapper accepts, which is what a corrected
builder has to reproduce.

READ-ONLY: vendor library VIs under vi.lib, opened and read, never saved (CLAUDE.md rule 1).

  py tools/bench/read_erdos_creators.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

LIB = os.path.join(r"C:\Program Files\National Instruments\LabVIEW 2026",
                   "vi.lib", "Erdos Miller", "LV-Scripting")
VIS = ["Create Invoke Node.vi", "Create Property Node.vi", "Create Constant.vi"]
g._run.__defaults__ = (6.0, 180.0)


def main():
    g._lv = None
    print(f"library: {LIB}\n", flush=True)
    for nm in VIS:
        path = os.path.join(LIB, nm)
        print(f"--- {nm}  (READ ONLY, never saved) ---", flush=True)
        if not os.path.exists(path):
            print("   not present", flush=True)
            continue
        try:
            rows = g.fp_labels(path, max_n=40)
        except Exception as e:
            print(f"   fp_labels EXC {str(e)[:200]}", flush=True)
            continue
        try:
            ref = g.lv().GetVIReference(path, "", False, 0)
        except Exception:
            ref = None
        for i, lab, ind in rows:
            val = ""
            if ref is not None and lab:
                try:
                    val = repr(ref.GetControlValue(lab))[:60]
                except Exception:
                    val = "<unreadable>"
            print(f"   {i:2d} {'IND' if ind else 'CTL'} {lab!r:34} = {val}", flush=True)
        print("", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
