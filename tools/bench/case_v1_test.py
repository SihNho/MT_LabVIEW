"""case_v1_test.py - FUNCTIONAL test of OpBuildCase_v1 (selector + inputs given as control NAMES).

Prediction contract (OpBuildCase_v1 on a stripped scratch copy of PARALLEL_kernel_v3, Frames = 2,
`Control Names` = ['# of bead 4 packs'] (selector), `Control Names 2` = ['x,y,z array', 'Image In'] (input tunnels)):
  P1  the op RUNS without a modal dialog (v0 raised error 1055 from Connect Wire on an empty Selector refnum)
  P2  +1 CaseStructure, Diagram count +2 (one per frame)
  P3  Wire count +3: the selector wire and one wire per input tunnel
  P4  ExecState of the scratch == 1 (unused tunnels are legal)
  P5  the op's own `error out` indicators stay empty
Nothing is saved; the scratch VI is deleted at the end.
  py tools/bgrun.py --max-min 15 --log tools/bench/case_v1_test.log -- py -u tools/bench/case_v1_test.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi"); T = os.path.join(g.CLAUDEDEV, "SCRATCH_case_v1t.vi")
OP_CASE = os.path.join(g.CLAUDEDEV, "OpBuildCase_v1.vi")
SELECTOR = "# of bead 4 packs"; INPUTS = ["x,y,z array", "Image In"]


def main():
    import json
    frames_list = [json.loads(a) for a in sys.argv[1:]] or [2]      # ints, or JSON arrays of frame names
    rc = 0
    for fr in frames_list:
        print(f"\n######## Frames = {fr}", flush=True)
        rc = max(rc, one(fr))
    return rc


def one(FRAMES):
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(SRC, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
    while g.count(T, "Node"):
        try:
            g.delete_object(T, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(T)
    n0, d0, w0, c0 = g.count(T, "Node"), g.count(T, "Diagram"), g.count(T, "Wire"), g.count(T, "CaseStructure")
    print(f"stripped scratch: nodes {n0} diagrams {d0} wires {w0} cases {c0} ExecState {g.exec_state(T)}", flush=True)
    print("fp:", [l for _, l, _ in g.fp_labels(T)], flush=True)
    vi = g.op(OP_CASE)
    try:
        print("   Frames control default:", repr(vi.GetControlValue("Frames")), flush=True)
    except Exception as e:
        print("   Frames control unreadable:", str(e)[:80], flush=True)
    for lab, val in (("vi path", T), ("vi path 2", T), ("Class Name", "Terminal"), ("index", 0),
                     ("location (0, 0)", [400, 300]), ("Frames", FRAMES), ("Control Names", [SELECTOR]), ("Control Names 2", INPUTS)):
        try:
            vi.SetControlValue(lab, val); print(f"   set {lab} = {val!r}", flush=True)
        except Exception as e:
            print(f"   set {lab}: EXC {str(e)[:110]}", flush=True)
    t0 = time.time(); dialog = None
    try:
        g._run(vi)
    except Exception as e:
        dialog = str(e)[:200]
    print(f"P1 run: {time.time() - t0:.1f} s, {'NO dialog' if dialog is None else 'EXC ' + dialog}", flush=True)
    for lab in ("error out", "error out 2"):
        try:
            print(f"P5 {lab}: {vi.GetControlValue(lab)!r}"[:200], flush=True)
        except Exception as e:
            print(f"P5 {lab}: unreadable {str(e)[:80]}", flush=True)
    n1, d1, w1, c1 = g.count(T, "Node"), g.count(T, "Diagram"), g.count(T, "Wire"), g.count(T, "CaseStructure")
    es = g.exec_state(T)
    print(f"P2 cases {c0}->{c1} (expect +1), diagrams {d0}->{d1} (expect +2)", flush=True)
    print(f"P3 wires {w0}->{w1} (expect +{1 + len(INPUTS)}), nodes {n0}->{n1}", flush=True)
    print(f"P4 ExecState {es} (expect 1)", flush=True)
    cases = g.report(T, "CaseStructure")
    print("CaseStructure:", [(o["uid"], o["pos"]) for o in cases], flush=True)
    tun = g.report(T, "Tunnel") if c1 else []
    print("Tunnels:", [(o["uid"], o["pos"], o["owner"]) for o in tun], flush=True)
    ok = dialog is None and c1 == c0 + 1 and d1 == d0 + 2 and w1 == w0 + 1 + len(INPUTS) and es == 1
    print("\nRESULT:", "PASS" if ok else "FAIL", flush=True)
    g.close_panel(T); time.sleep(0.5)
    try:
        os.remove(T); print("scratch deleted", flush=True)
    except OSError as e:
        print("scratch NOT deleted:", e, flush=True)
    return 0 if ok else 5


if __name__ == "__main__":
    sys.exit(main())
