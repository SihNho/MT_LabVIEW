"""apply_conpane.py - put TRACK_kernel_v1's `index` (the backend selector) ON its connector pane, then prove nothing broke.

Verified on a scratch copy first (build_opconpaneassign.py: terminal[5] became 'index', the other 13 assignments untouched,
file grew 17,059 -> 17,087 B). This applies the same operation to the real VI and re-checks it end to end.

  1. open the panel (a target loaded only by GetVIReference declines edits SILENTLY), assign front-panel object `index`
     to FREE terminal 5, save                         predict: terminal[5] == 'index', ExecState 1
  2. set the shipped default back to index = 0 (CPU), since the timing benchmark left it at 1
  3. restart LabVIEW, then run 20 frames through base + track and check the deviation against the LabVIEW reference
     predict: track deviation 0.00 (the CPU frame), i.e. the pane change did not disturb the call
  py tools/bgrun.py --max-min 25 --log tools/bench/apply_conpane.log -- py -u tools/bench/apply_conpane.py
"""
import os, subprocess, sys, time
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import gscript as g  # noqa: E402

TRACK = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi")
ASSIGN = os.path.join(g.CLAUDEDEV, "OpConPaneAssign_v0.vi"); READER = os.path.join(g.CLAUDEDEV, "OpConPane_v0.vi")
TERMINAL = 5
g._run.__defaults__ = (6.0, 45.0)


def run(args, timeout, tag):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=timeout, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"   {tag} rc {rc}", flush=True); return rc


def blank(vi):
    for l in ("Names", "Names 2"):
        try:
            vi.SetControlValue(l, [])
        except Exception:
            pass
    for l in ("Class Name", "Class Name 2"):
        try:
            vi.SetControlValue(l, "")
        except Exception:
            pass


def read_pane(tag):
    rd = g.op(READER); rd.SetControlValue("vi path", TRACK); blank(rd)
    out = {}
    for i in range(16):
        rd.SetControlValue("index", i)
        try:
            g._run(rd); out[i] = rd.GetControlValue("Text")
        except Exception:
            out[i] = "(FREE)"
    print(f"   pane {tag}: " + ", ".join(f"{i}:{v}" for i, v in out.items() if v != "(FREE)")
          + " | FREE " + str([i for i, v in out.items() if v == "(FREE)"]), flush=True)
    return out


def main():
    g._lv = None
    size0 = os.path.getsize(TRACK)
    g.open_panel(TRACK); time.sleep(0.8)
    labels = [l for _, l, _ in g.fp_labels(TRACK)]
    if "index" not in labels:
        print("STOP: no 'index' control", flush=True); return 3
    fp_i = labels.index("index")
    before = read_pane("before")
    if before.get(TERMINAL) != "(FREE)":
        print(f"STOP: terminal {TERMINAL} is not free (holds {before.get(TERMINAL)!r})", flush=True); return 3
    vi = g.op(ASSIGN)
    vi.SetControlValue("vi path", TRACK); vi.SetControlValue("index", fp_i); vi.SetControlValue("Terminal Index", TERMINAL)
    blank(vi)
    g._run(vi)
    print("   assign error out:", vi.GetControlValue("error out"), flush=True)
    print("   saved", g.save(TRACK), f"bytes (was {size0})", flush=True)
    after = read_pane("after")
    kept = all(after.get(i) == v for i, v in before.items() if v != "(FREE)")
    ok = after.get(TERMINAL) == "index" and kept and g.exec_state(TRACK) == 1
    print(f"   terminal[{TERMINAL}] = {after.get(TERMINAL)!r}; other assignments kept: {kept}; ExecState {g.exec_state(TRACK)}", flush=True)
    if not ok:
        print("STOP: pane assignment did not verify", flush=True); return 5
    print("   shipped default -> index 0 (CPU):", g.make_default(TRACK, {"index": 0}), "bytes", flush=True)
    g.close_panel(TRACK); time.sleep(0.5)
    del vi
    g._lv = None
    print("\n=== functional re-check after the pane change ===", flush=True)
    run([os.path.join(TOOLS, "lv_restart.py")], 400, "lv_restart")
    run(["-u", os.path.join(TOOLS, "bench", "run_timing.py"), "--n=20", "--harness=base", "--harness=track"], 1200, "run_timing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
