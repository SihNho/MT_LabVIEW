"""camera_ceiling.py - what per-frame processing budget can the rig afford before it loses frames?

This drives NI's own `Acquire Every Image.vi`, copied into claudeDev, because it already is the experiment: it acquires
EVERY buffer in sequence (the mode that must keep up with the camera), injects a settable per-frame delay, and reports
`Acquired Frame Rate`, `Processing Frame Rate`, `Images Behind` and `Images Missed`.

Sweeping `Simulated Processing Delay (ms)` answers the question the whole loop-multiplication argument rests on:

  delay 0 ms    -> the camera's CEILING at the current 2x2 binning. The user wants 150 Hz and runs 90 Hz today, but the
                   sensor does 62 fps at full resolution, so the ceiling may sit below the target, in which case no
                   software change can reach it and the goal itself has to move.
  delay ~2.5 ms -> stands in for the measured CPU-parallel tracking kernel.
  delay ~7 ms   -> kernel plus the estimated t0 of 4.7 ms, i.e. today's whole per-frame cost.

The frame at which `Images Missed` leaves zero IS the budget. No part of the main VI is involved, so none of its
complexity can confound the answer.

RUN MODEL: the example loops until its `Stop` button goes true, so it is started ASYNCHRONOUSLY (`Run(False)`), sampled,
then stopped. `Stop` is set true in a finally block, and the VI is never left running.

HARDWARE: camera only. The user cleared all instruments on 2026-09-12 while the rig is disassembled; this touches
nothing but the camera anyway.
  py tools/bgrun.py --max-min 30 --log tools/bench/camera_ceiling.log -- py -u tools/bench/camera_ceiling.py [seconds]
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = (r"C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision Acquisition\NI-IMAQdx"
       r"\Basic Acquisition\Acquire Every Image.vi")
DST = os.path.join(g.CLAUDEDEV, "CAMBENCH_every_image.vi")
OUT = os.path.join(HERE, "camera_ceiling_results.json")
SECONDS = float(sys.argv[1]) if len(sys.argv) > 1 else 6.0
DELAYS = [int(x) for x in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0, 1, 2, 3, 4, 5, 6, 7, 8, 10, 12]
READ = ["Acquired Frame Rate", "Processing Frame Rate", "Images Behind", "Images Missed", "Buffer Number"]
g._run.__defaults__ = (6.0, 60.0)


def cell(vi, delay, seconds):
    """Start the example, let it settle, sample the counters, stop it. Returns the sampled dict."""
    vi.SetControlValue("Simulated Processing Delay (ms)", float(delay))
    vi.SetControlValue("Stop", False)
    samples = []
    try:
        vi.Run(False)                      # asynchronous: the VI loops until Stop goes true
        t0 = time.time()
        time.sleep(min(2.0, seconds / 3))  # let the frame-rate averages settle before sampling
        while time.time() - t0 < seconds:
            row = {}
            for name in READ:
                try:
                    row[name] = vi.GetControlValue(name)
                except Exception:
                    pass
            samples.append(row)
            time.sleep(0.5)
    finally:
        try:
            vi.SetControlValue("Stop", True)
        except Exception:
            pass
        for _ in range(40):                # wait for the loop to actually exit
            time.sleep(0.25)
            try:
                if int(vi.ExecState) in (0, 1):
                    break
            except Exception:
                break
    return samples


def main():
    g._lv = None
    if os.path.exists(DST):
        os.remove(DST)
    shutil.copyfile(SRC, DST)
    g.open_panel(DST, activate=False); time.sleep(1.0)
    vi = g.lv().GetVIReference(DST, "", False, 0)
    try:
        cam = vi.GetControlValue("Camera Name")
    except Exception as e:
        cam = None; print("   Camera Name unreadable:", str(e)[:120], flush=True)
    print("copied NI example ->", os.path.basename(DST), flush=True)
    print("default Camera Name:", repr(cam), flush=True)
    # cam1, NOT cam0 - measured 2026-09-12 by enumerating through niimaqdx.dll (tools/bench/imaqdx_ctypes.py).
    # An empty or wrong name is what popped the modal dialog that blocked the two earlier runs of this harness, so the
    # name is a verified constant here rather than a guess, and it is ALWAYS written - the previous version only wrote
    # it when the read came back falsy, and an IMAQdx Session control reads back as the TUPLE ('', 0), which is truthy.
    # That one bug is why the harness ran with no camera at all and sat behind a modal dialog until the watchdog killed it.
    CAM = "cam1"
    ok = False
    for form in (CAM, (CAM, 0)):     # the control is an IMAQdx Session; accept either the plain name or the refnum pair
        try:
            vi.SetControlValue("Camera Name", form)
            back = vi.GetControlValue("Camera Name")
            ok = CAM in (back if isinstance(back, str) else str(back))
            print(f"   set Camera Name <- {form!r}; reads back {back!r}  {'OK' if ok else 'NOT APPLIED'}", flush=True)
            if ok:
                break
        except Exception as e:
            print(f"   Camera Name <- {form!r} refused: {str(e)[:120]}", flush=True)
    if not ok:
        # Refuse to run rather than repeat the failure: with no camera name the example opens a modal dialog that
        # blocks every later COM call until LabVIEW is killed, which has now cost two runs and ~40 minutes.
        print("   ABORT: the camera name did not take. Not starting the example - it would open a modal dialog.", flush=True)
        try:
            g.close_panel(DST)
        except Exception:
            pass
        return 5
    for name in ("Number of Images", "Overwrite Mode", "Percent of Images Reserved by Driver"):
        try:
            print(f"   default {name}: {vi.GetControlValue(name)!r}", flush=True)
        except Exception:
            pass

    rows = []
    for delay in DELAYS:
        print(f"\n==== Simulated Processing Delay = {delay} ms", flush=True)
        try:
            samples = cell(vi, delay, SECONDS)
        except Exception as e:
            print("   cell failed:", str(e)[:200], flush=True)
            break
        if not samples:
            print("   no samples", flush=True); continue
        last = samples[-1]
        acq = [s.get("Acquired Frame Rate") for s in samples if isinstance(s.get("Acquired Frame Rate"), (int, float))]
        pro = [s.get("Processing Frame Rate") for s in samples if isinstance(s.get("Processing Frame Rate"), (int, float))]
        row = {"delay_ms": delay,
               "acquired_fps": round(sum(acq) / len(acq), 1) if acq else None,
               "processing_fps": round(sum(pro) / len(pro), 1) if pro else None,
               "images_behind": last.get("Images Behind"),
               "images_missed": last.get("Images Missed"),
               "buffer_number": last.get("Buffer Number"),
               "samples": len(samples)}
        rows.append(row)
        print("   " + json.dumps(row), flush=True)
        json.dump(rows, open(OUT, "w", encoding="utf-8"), indent=1)
        if isinstance(row["images_missed"], (int, float)) and row["images_missed"] > 0:
            print("   ^^ frames are being lost at this delay", flush=True)

    print("\n==== SUMMARY  (delay -> acquired / processing fps, behind, missed)", flush=True)
    for r in rows:
        print(f"   {r['delay_ms']:>3} ms | acq {str(r['acquired_fps']):>7} | proc {str(r['processing_fps']):>7} | "
              f"behind {r['images_behind']} | missed {r['images_missed']}", flush=True)
    try:
        g.close_panel(DST)
    except Exception:
        pass
    print("\nresults ->", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
