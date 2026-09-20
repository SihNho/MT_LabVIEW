"""run_fixture_compare.py — functional acceptance of the parallel kernel on the recorded fixture (rule 1a).

For each recorded frame: HARNESS_compare.vi runs PARALLEL_kernel_v3 and the four-fold kernel on the SAME
image, cal clusters, windows and state; the driver
  (1) asserts v3 == four-fold bit-for-bit (x,y,z array out, Bead is good? array out, pos in cal image out),
  (2) compares both with the .tra row of that frame (x,y in pixels, z as recorded) -> max abs deviation,
  (3) feeds the four-fold outputs back as the next frame's inputs (x,y,z array / good flags / cal position),
      which is what the main VI's shift registers do.
Nothing touches an instrument: the harness loads TIFFs and calls the kernels only.

  py tools/bgrun.py --max-min 60 --log tools/bench/fixture_compare.log -- py -u tools/bench/run_fixture_compare.py [--n=200] [--every=1] [--start=0]

Outputs: tools/bench/fixture_compare_results.jsonl (one line per frame) + a summary line.
"""
import json
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

DATA = r"G:\Data\SiHyeong\20260906 Kimlab - 50bp 16X WT 90Hz 1p2 Ramp_Newbatch\test"
CAL = os.path.join(DATA, "cal002")
TRA = os.path.join(DATA, "tra002-000")
HARNESS = os.path.join(g.CLAUDEDEV, "HARNESS_compare.vi")
LOADER = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
LABELS = json.load(open(os.path.join(HERE, "harness_compare_labels.json")))
OUT = os.path.join(HERE, "fixture_compare_results.jsonl")
g._run.__defaults__ = (6.0, 120.0)


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return type(default)(v) if v is not None else default


def read_tra():
    b = open(TRA, "rb").read()
    n = struct.unpack("<I", b[:4])[0]
    rest = b[4 + n:]
    vals = struct.unpack("<%dd" % (len(rest) // 8), rest)
    rows = [vals[1 + 18 * i:1 + 18 * (i + 1)] for i in range((len(vals) - 1) // 18)]
    return {int(r[0]): r for r in rows}


def main():
    N = arg("n", 200); EVERY = arg("every", 1); START = arg("start", 0)
    tra = read_tra()
    frames = sorted(tra)[START::EVERY][:N]
    g._lv = None
    ld = g.op(LOADER); ld.SetControlValue("file (use dialog)", CAL); g._run(ld)
    nb = int(ld.GetControlValue("# of beads")); xyz0 = list(ld.GetControlValue("x,y,(blankz) array"))
    print("loader:", nb, "beads, cross size", ld.GetControlValue("cross size"), "xyz0", xyz0[:6], flush=True)
    C = LABELS["controls"]; O = LABELS["outputs"]
    vi = g.op(HARNESS)
    vi.SetControlValue(C["Image Name"], "harness")
    vi.SetControlValue(C["# of bead 4 packs"], nb // 4)
    vi.SetControlValue(C["4 pack remainder"], nb % 4)
    state = {"xyz": xyz0, "good": [True] * nb, "pos": [0] * nb}
    n_ok = n_bad = 0; worst = 0.0; worst_frame = None; t_run = []
    with open(OUT, "a") as f:
        f.write(json.dumps({"session": time.strftime("%Y-%m-%d %H:%M:%S"), "frames": len(frames), "every": EVERY, "start": START}) + "\n")
        for k, fr in enumerate(frames):
            vi.SetControlValue(C["File Path"], os.path.join(DATA, f"img{fr:05d}.tif"))
            vi.SetControlValue(C["x,y,z array"], state["xyz"])
            vi.SetControlValue(C["Bead is good? array in"], state["good"])
            vi.SetControlValue(C["pos in cal image in"], state["pos"])
            t0 = time.time()
            try:
                g._run(vi)
            except Exception as e:
                print(f"frame {fr}: run failed: {str(e)[:120]}", flush=True); n_bad += 1; continue
            dt = time.time() - t0; t_run.append(dt)
            v3 = {n: list(vi.GetControlValue(O[f"v3|{n}"])) for n in ("x,y,z array out", "Bead is good? array out", "pos in cal image out")}
            ff = {n: list(vi.GetControlValue(O[f"ff|{n}"])) for n in ("x,y,z array out", "Bead is good? array out", "pos in cal image out")}
            same = all(v3[n] == ff[n] for n in v3)
            row = tra[fr]
            dev = max(abs(ff["x,y,z array out"][3 * b + c] - row[3 + 3 * b + c]) for b in range(nb) for c in range(3))
            if not same:
                n_bad += 1
            else:
                n_ok += 1
            if dev > worst:
                worst, worst_frame = dev, fr
            f.write(json.dumps({"frame": fr, "same": same, "dt": round(dt, 4), "v3": v3["x,y,z array out"], "ff": ff["x,y,z array out"],
                                "tra": list(row[3:3 + 3 * nb]), "good": ff["Bead is good? array out"], "pos": ff["pos in cal image out"], "dev_vs_tra": dev}) + "\n")
            if k < 5 or k % 50 == 0 or not same:
                print(f"frame {fr}: same={same} dt={dt * 1000:.0f} ms  v3[:3]={[round(x, 3) for x in v3['x,y,z array out'][:3]]} tra[:3]={[round(x, 3) for x in row[3:6]]} dev_vs_tra={dev:.4f} good={ff['Bead is good? array out']} pos={ff['pos in cal image out']}", flush=True)
            state = {"xyz": ff["x,y,z array out"], "good": ff["Bead is good? array out"], "pos": ff["pos in cal image out"]}
    print(f"SUMMARY frames={len(frames)} identical={n_ok} different={n_bad} worst_dev_vs_tra={worst:.5f} at frame {worst_frame} "
          f"mean_run={sum(t_run) / max(1, len(t_run)) * 1000:.0f} ms", flush=True)
    return 0 if n_bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
