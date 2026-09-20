"""camera_dump.py - ask the camera directly: name, binning, geometry, and the frame-rate ceiling.

Open questions this settles, all of which have so far been inference:
  * the camera's IMAQdx NAME - the examples' `Camera Name` is an IMAQdx Session control that reads back as ('', 0), and
    the main VI holds it as a block-diagram constant that does not survive string extraction;
  * what binning and geometry the camera is ACTUALLY in - the main VI shows Width 640 / Height 512 where 2x2 binning
    should give 1280x1024, the main VI contains no binning attribute at all (only `Width`/`Height`, both indicators),
    and the user reports the size halves on the first run and comes back on the second, which is the signature of a
    value being read a step before the configuration it belongs to;
  * the maximum acquisition frame rate at the current settings, which is the ceiling the whole 150 Hz question rests on.

`IMAQdx Enumerate Cameras` needs no session, so the name comes first and everything else follows from it.
Camera only. Attributes are READ, never written.
  py tools/bgrun.py --max-min 20 --log tools/bench/camera_dump.log -- py -u tools/bench/camera_dump.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EX = r"C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision Acquisition\NI-IMAQdx"
ENUM_SRC = os.path.join(EX, "Design Patterns", "Enumerate and Select Camera.vi")
ATTR_SRC = os.path.join(EX, "Camera Attributes", "Getting Started with Attributes.vi")
ENUM = os.path.join(g.CLAUDEDEV, "CAMDUMP_enumerate.vi")
ATTR = os.path.join(g.CLAUDEDEV, "CAMDUMP_attributes.vi")
g._run.__defaults__ = (6.0, 45.0)

KEYS = ("binning", "width", "height", "offset", "pixelformat", "acquisitionframerate", "framerate",
        "sensor", "decimation", "reverse", "exposure", "payload", "devicemodel", "devicevendor")


def fresh(src, dst):
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(src, dst)
    g.open_panel(dst, activate=False); time.sleep(0.8)
    return g.lv().GetVIReference(dst, "", False, 0)


def main():
    g._lv = None
    # --- 1. the camera name, from the enumeration example's Interfaces control -----------------
    print("=== camera enumeration ===", flush=True)
    name = None
    vi = fresh(ENUM_SRC, ENUM)
    for lab in ("Interfaces",):
        try:
            v = vi.GetControlValue(lab)
            print(f"   {lab} = {v!r}", flush=True)
            if isinstance(v, (tuple, list)) and v:
                name = v[0] if isinstance(v[0], str) else None
            elif isinstance(v, str):
                name = v
        except Exception as e:
            print(f"   {lab}: {str(e)[:120]}", flush=True)
    del vi
    try:
        g.close_panel(ENUM)
    except Exception:
        pass
    print("   camera name from the example:", repr(name), flush=True)

    # --- 2. the full attribute dump -----------------------------------------------------------
    print("\n=== attribute dump ===", flush=True)
    vi = fresh(ATTR_SRC, ATTR)
    for cand in ([name] if name else []) + ["cam0", "cam1"]:
        if not cand:
            continue
        try:
            vi.SetControlValue("Camera Name", cand)
        except Exception as e:
            print(f"   set Camera Name={cand!r}: {str(e)[:110]}", flush=True); continue
        try:
            vi.SetControlValue("Show Only Camera Attributes", False)
            vi.SetControlValue("Visibility", 2)      # advanced, to include the frame-rate limits
        except Exception:
            pass
        try:
            vi.SetControlValue("Stop", False)
            vi.Run(False)
            time.sleep(3.0)
            n = vi.GetControlValue("Number of Attributes")
            txt = vi.GetControlValue("Initial Attribute Settings")
            vi.SetControlValue("Stop", True); time.sleep(1.5)
        except Exception as e:
            print(f"   run with {cand!r} failed: {str(e)[:160]}", flush=True)
            try:
                vi.SetControlValue("Stop", True)
            except Exception:
                pass
            continue
        print(f"   camera {cand!r}: Number of Attributes = {n!r}", flush=True)
        if txt:
            lines = str(txt).splitlines()
            print(f"   dump has {len(lines)} lines; the ones that matter:", flush=True)
            for ln in lines:
                if any(k in ln.lower() for k in KEYS):
                    print("      " + ln.strip()[:150], flush=True)
            out = os.path.join(HERE, "camera_attributes_dump.txt")
            open(out, "w", encoding="utf-8").write(str(txt))
            print("   full dump ->", out, flush=True)
            break
    try:
        g.close_panel(ATTR)
    except Exception:
        pass
    print("\nDONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
