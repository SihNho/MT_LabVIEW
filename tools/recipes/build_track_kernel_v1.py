"""build_track_kernel_v1.py - TRACK_kernel_v1.vi: ONE kernel subVI with a `backend` selector (0 = CPU-parallel, 1 = GPU).

User (2026-09-09): "최종적으로는 subvi를 만들어서 내가 셋팅에 따라 cpu parallel 혹은 gpu를 쓸건지 정할 수 있으면 좋겠어".
Computation-preserving by construction: frame 0 IS PARALLEL_kernel_v3, frame 1 IS GPU_kernel_v1 (both verified against the
reference); this VI only routes the pane controls/indicators through a Case Structure.

Built on a SCRATCH copy of PARALLEL_kernel_v3 (same connector pane), promoted to TRACK_kernel_v1.vi only if ExecState == 1:
  1  strip the diagram (delete every Node)                                   predict: nodes 0, ExecState 1
  2  selector control: OpBuildIA_v0 (unwired Index Array) -> create_control on its `index` terminal -> delete the IA
                                                                             predict: fp gains 'index' (I32), ExecState 1
  3  build_case(selector='index', inputs=[], frames ['0, Default','1'])       predict: +1 case, diagrams 1->3, wires +1
  4  drop PARALLEL_kernel_v3 into diagram 1, GPU_kernel_v1 into diagram 2    predict: SubVIs 2
  5  wire_control each of the 10 pane controls -> node A (frame 1)           predict: +2 wires each (tunnel auto-created)
     then -> node B (frame 2)                                                measure: +2 (new tunnel) or +1 (tunnel reused)
  6  outputs: per frame, create_indicator on the node's output (temp indicator + tunnel), wire_indicators the PANE indicator
     onto that wire, delete the temp                                         measure: wires, ExecState after each
  7  ExecState == 1 -> save -> copy to TRACK_kernel_v1.vi; else scratch deleted, nothing promoted
Frame identity (which diagram index is '0, Default') is NOT proven here - the functional check is MT_GPU_LOG: lines appear
only when the GPU frame runs (tools/bench/track_v1_check.py, next).
  py tools/bgrun.py --max-min 25 --log tools/bench/build_track_kernel_v1.log -- py -u tools/recipes/build_track_kernel_v1.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

PAR = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi"); GPU = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1.vi")
T = os.path.join(g.CLAUDEDEV, "SCRATCH_track.vi"); OUT = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi")
PANE = json.load(open(os.path.join(os.path.dirname(HERE), "bench", "kernel_pane.json"), encoding="utf-8"))
INPUTS = [o["label"] for o in PANE if not o["indicator"]]
OUTPUTS = [o["label"] for o in PANE if o["indicator"]]
g._run.__defaults__ = (6.0, 60.0)


def W():
    return g.count(T, "Wire")


def main():
    g._lv = None
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(PAR, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
    inv0 = g.uids(T, "Invoke")

    def purge():
        for o in g.new_since(T, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(T, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(T, "Invoke", ids.index(o["uid"]))

    def del_terms(new):
        ct = [o["uid"] for o in g.report(T, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(T, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(T, "ControlTerminal")]
        g.remove_bad_wires_scripted(T)

    def labels():
        return [l for _, l, _ in g.fp_labels(T)]

    def sub_i(uid):
        return [o["uid"] for o in g.report(T, "SubVI")].index(uid)
    # 1. strip
    while g.count(T, "Node"):
        try:
            g.delete_object(T, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(T)
    print(f"1 stripped: nodes {g.count(T, 'Node')} wires {W()} ExecState {g.exec_state(T)} | inputs {len(INPUTS)} outputs {len(OUTPUTS)}", flush=True)
    # 2. selector control via a throw-away Index Array
    g.build_index_array(T, (250, 120)); purge()
    n_ia = g.count(T, "Node") - 1; sel = None
    for t in range(4):
        new, lab = g.create_control(T, n_ia, t); purge()
        if new and lab and lab.lower().startswith("index"):
            sel = lab; break
        if new:
            del_terms(new)
    ids = [x["uid"] for x in g.report(T, "IndexArray")]
    if ids:
        g.delete_object(T, "IndexArray", 0)
    g.remove_bad_wires_scripted(T)
    print(f"2 selector control {sel!r}: nodes {g.count(T, 'Node')} wires {W()} ExecState {g.exec_state(T)} fp {labels()}", flush=True)
    if sel is None:
        print("STOP: no selector control", flush=True); return 3
    # 3. case
    d0 = g.count(T, "Diagram"); w0 = W()
    case = g.build_case(T, (400, 200), sel, [])
    print(f"3 case {case['uid']} @ {case['pos']}: diagrams {d0}->{g.count(T, 'Diagram')} wires {w0}->{W()} ExecState {g.exec_state(T)}", flush=True)
    # 4. kernels into the frames
    b = g.uids(T, "SubVI"); g.drop_subvi(T, PAR, 1, (480, 260)); purge(); A = g.new_since(T, "SubVI", b)[0]["uid"]
    b = g.uids(T, "SubVI"); g.drop_subvi(T, GPU, 2, (480, 260)); purge(); B = g.new_since(T, "SubVI", b)[0]["uid"]
    print(f"4 kernels: A(CPU) uid {A} B(GPU) uid {B} | SubVIs {g.count(T, 'SubVI')} ExecState {g.exec_state(T)}", flush=True)
    # 5. inputs
    for tag, uid in (("A", A), ("B", B)):
        for lab in INPUTS:
            w = W()
            try:
                g.wire_control(T, [lab], "SubVI", sub_i(uid), [lab], branch=True)
                print(f"5 {tag} {lab!r}: wires {w}->{W()}", flush=True)
            except Exception as e:
                print(f"5 {tag} {lab!r}: EXC {str(e)[:150]} | wires {w}->{W()}", flush=True)
        print(f"5 {tag} done: wires {W()} ExecState {g.exec_state(T)}", flush=True)
    # 6. outputs: wire_indicators straight from the node inside the frame to the PANE indicator. Wire Indicators.vi crosses the
    # frame border like Wire Inputs.vi does (case_out_probe A: +2 wires = tunnel + inner wire); its ExecState raise is expected
    # until the same output is wired in BOTH frames (an output tunnel unwired in one case breaks the VI), so it is caught and the
    # verdict is taken from the counts and the final ExecState. (create_indicator cannot reach nodes inside frames: its ladder
    # walks the TOP-LEVEL Nodes[] only - 2026-09-10.)
    for out in OUTPUTS:
        for tag, uid in (("A", A), ("B", B)):
            w = W()
            try:
                g.wire_indicators(T, sub_i(uid), [out], [out], node_class="SubVI")
                print(f"6 {tag} {out!r}: wires {w}->{W()} ExecState 1", flush=True)
            except Exception as e:
                print(f"6 {tag} {out!r}: wires {w}->{W()} ExecState {g.exec_state(T)} ({str(e)[:90]})", flush=True)
    purge(); g.remove_bad_wires_scripted(T); es = g.exec_state(T)
    print(f"\nassembled: nodes {g.count(T, 'Node')} wires {W()} tunnels {g.count(T, 'Tunnel')} diagrams {g.count(T, 'Diagram')} ExecState {es}\nfp: {labels()}", flush=True)
    if es != 1:
        print("STOP: scratch discarded, nothing promoted", flush=True)
        g.close_panel(T); time.sleep(0.5); os.remove(T); return 5
    print("saved scratch", g.save(T), flush=True)
    g.close_panel(T); time.sleep(0.5); shutil.copyfile(T, OUT); os.remove(T)
    print("TRACK_kernel_v1.vi written (", os.path.getsize(OUT), "bytes ) - STRUCTURAL only; functional check next", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
