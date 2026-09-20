"""build_gpu_kernel.py - GPU_kernel_v1.vi: the GPU backend as a DROP-IN for the tracking kernel — same connector pane as
PARALLEL_kernel_v3.vi, so the main VI's single kernel call site (MAIN_VI_MAP.md §3b: node index 39, uid 5058) can take either.

Built from a COPY of PARALLEL_kernel_v3.vi (the pane and all 13 front-panel objects come with the copy; the diagram is replaced):

  Image In ──> IMAQ GetImagePixelPtr ──Pixel Pointer out──> CLFN.pixel_ptr
           └─> IMAQ GetImageSize      └─LineWidth(Pixels)─> CLFN.line_width_bytes
                 X/Y Resolution ─────────────────────────> CLFN.width / .height
  x,y,z array ─────────────────> CLFN.xyz_in  and (branch) CLFN.xyz_out      (the DLL reads every input before writing outputs,
  Bead is good? array in ──────> CLFN.good_in and (branch) CLFN.good_out      so in/out may share a buffer - mt2.inc)
  pos in cal image in ─────────> CLFN.idx_out
  new controls: cal path (empty => DLL falls back to MT_GPU_CAL / mt_track_cal.txt), nb (0 => calibration bead count),
                status (empty), status_len (0 => the DLL writes no status), flags (0), Function (GetImagePixelPtr, required)
  CLFN outputs ─> the EXISTING pane indicators (temporary indicator to create the wire, then wire_indicators branches the pane
                  indicator onto it, then the temporary one is deleted).

  py tools/bgrun.py --max-min 25 --log tools/bench/build_gpu_kernel.log -- py -u tools/recipes/build_gpu_kernel.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g  # noqa: E402
import clfn_params as cp  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
PTR_VI = os.path.join(VIS, "Basics.llb", "IMAQ GetImagePixelPtr"); SIZE_VI = os.path.join(VIS, "Basics.llb", "IMAQ GetImageSize")
SRC = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi"); OP = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1.vi")
DLL = os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll")
# the LabVIEW-facing entry: good_in/good_out are "Adapt to Type" so the kernel's BOOLEAN array control wires straight in
# (an explicit U8-array parameter makes a BAD wire - measured, tools/bench/bool_wire_probe.log)
FN = "mt2_track_simple_b"
FLAT = open(os.path.join(os.path.dirname(HERE), "bench", "paraminfo_mt2_b.hex")).read().strip()
g._run.__defaults__ = (6.0, 60.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); STEPS.append((name, True)); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); STEPS.append((name, False)); return None


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    fp0 = [(i, l, ind) for i, l, ind in g.fp_labels(OP)]
    print("copy: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "fp objects", len(fp0), "ExecState", g.exec_state(OP), flush=True)
    inv0 = g.uids(OP, "Invoke"); RANK = {}

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))

    def sub_i(uid):
        return [o["uid"] for o in g.report(OP, "SubVI")].index(uid)

    def cls_i(cls, uid):
        return [o["uid"] for o in g.report(OP, cls)].index(uid)

    def drop(path, pos):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
        new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]; assert len(new) == 1, f"drop {os.path.basename(path)}: {len(new)}"
        RANK[new[0]["uid"]] = g.count(OP, "Node") - 1
        return new[0]["uid"]

    def del_terms(new):
        ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
        g.remove_bad_wires_scripted(OP)

    def control_at(uid, wanted, max_terms=16):
        """control on the terminal of node `uid` whose auto-label starts with `wanted`; returns the label"""
        n = RANK[uid]
        for t in range(max_terms):
            w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
            if new and lab and lab.lower().startswith(wanted.lower()) and g.count(OP, "Wire") > w0:
                return lab
            if new:
                del_terms(new)
        return None

    # 0. strip the CPU diagram; the front panel (pane) is untouched
    while g.count(OP, "Node"):
        try:
            g.delete_object(OP, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(OP); purge()
    fp1 = g.fp_labels(OP)
    print("diagram stripped: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "fp objects", len(fp1), "ExecState", g.exec_state(OP), flush=True)
    if len(fp1) != len(fp0):
        print("STOP: front-panel objects were lost with the diagram", flush=True); return 3
    # 1. image chain
    uP = step("drop IMAQ GetImagePixelPtr", "+1 SubVI", lambda: drop(PTR_VI, (400, 200)))
    uS = step("drop IMAQ GetImageSize", "+1 SubVI", lambda: drop(SIZE_VI, (400, 420)))
    if None in (uP, uS):
        return 4
    step("control 'Image In' -> GetImagePixelPtr.Image", "+1 wire",
         lambda: g.wire_control(OP, ["Image In"], "SubVI", sub_i(uP), ["Image"]))
    step("control 'Image In' -> GetImageSize.Image (branch)", "accepted",
         lambda: g.wire_control(OP, ["Image In"], "SubVI", sub_i(uS), ["Image"], branch=True))
    fn_ctl = step("control on GetImagePixelPtr.Function (required input)", "label 'Function'", lambda: control_at(uP, "Function"))
    # 2. the CLFN
    purge(); res = step("build_clfn mt2_track_simple", "+1 CallLibrary, 30 terms, no errors",
                        lambda: g.build_clfn(OP, (900, 300), DLL, FN, FLAT))
    if not res:
        return 5
    uK = res[0]; purge(); RANK[uK] = g.count(OP, "Node") - 1
    ki = lambda: cls_i("CallLibrary", uK)
    step("P.Pixel Pointer out -> CLFN.pixel_ptr", "+1", lambda: g.wire(OP, "SubVI", sub_i(uP), "Pixel Pointer out", "CallLibrary", ki(), "pixel_ptr"))
    step("P.LineWidth(Pixels) -> CLFN.line_width_bytes", "+1", lambda: g.wire(OP, "SubVI", sub_i(uP), "LineWidth(Pixels)", "CallLibrary", ki(), "line_width_bytes"))
    step("S.X Resolution -> CLFN.width", "+1", lambda: g.wire(OP, "SubVI", sub_i(uS), "X Resolution", "CallLibrary", ki(), "width"))
    step("S.Y Resolution -> CLFN.height", "+1", lambda: g.wire(OP, "SubVI", sub_i(uS), "Y Resolution", "CallLibrary", ki(), "height"))
    # 3. pane controls -> CLFN inputs (xyz and good go to BOTH the in and the out parameter: the DLL may share the buffer)
    step("'x,y,z array' -> CLFN.xyz_in", "+1", lambda: g.wire_control(OP, ["x,y,z array"], "CallLibrary", ki(), ["xyz_in"]))
    step("'x,y,z array' -> CLFN.xyz_out (branch)", "accepted", lambda: g.wire_control(OP, ["x,y,z array"], "CallLibrary", ki(), ["xyz_out"], branch=True))
    w_before = g.count(OP, "Wire")
    step("'Bead is good? array in' -> CLFN.good_in (BOOL array into an Adapt-to-Type parameter)", "+1",
         lambda: g.wire_control(OP, ["Bead is good? array in"], "CallLibrary", ki(), ["good_in"]))
    g.remove_bad_wires_scripted(OP)
    if g.count(OP, "Wire") <= w_before:
        print("STOP: the boolean wire is still rejected (removed as a bad wire) - Adapt to Type did not take", flush=True); return 8
    step("'Bead is good? array in' -> CLFN.good_out (branch)", "accepted",
         lambda: g.wire_control(OP, ["Bead is good? array in"], "CallLibrary", ki(), ["good_out"], branch=True))
    step("'pos in cal image in' -> CLFN.idx_out", "+1", lambda: g.wire_control(OP, ["pos in cal image in"], "CallLibrary", ki(), ["idx_out"]))
    # 4. the remaining CLFN inputs as new controls (defaults are the intended values: empty path, nb 0, status_len 0, flags 0)
    made = {}
    for want in ("cal_path", "nb", "status", "status_len", "flags"):
        lab = control_at(uK, want, max_terms=40); made[want] = lab
        print(f"   control {want}: {lab!r}", flush=True)
    # 4b. CHECKPOINT: everything above is ~10 min of scripted work; save it so the output-wiring stage can be probed on a copy
    purge(); g.remove_bad_wires_scripted(OP); es_ctrl = g.exec_state(OP)
    print("\nafter inputs+controls: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es_ctrl, flush=True)
    CKPT = os.path.join(g.CLAUDEDEV, "GPU_kernel_v1_partial.vi")
    try:
        print("checkpoint saved", g.save(OP, allow_broken=True), "->", os.path.basename(CKPT), flush=True)
        shutil.copyfile(OP, CKPT)
    except Exception as e:
        print("checkpoint save:", str(e)[:160], flush=True)
    if "--stop-after-inputs" in sys.argv:
        return 0
    # 5. CLFN outputs -> the EXISTING pane indicators (temp indicator makes the wire, then branch the pane indicator onto it)
    OUT = [("xyz_out", "x,y,z array out"), ("good_out", "Bead is good? array out"), ("idx_out", "pos in cal image out")]
    for param, ind in OUT:
        n = RANK[uK]; done = False
        for t in range(0, 40):
            fpa = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
            new = g.create_indicator(OP, n, t); purge(); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fpa]
            if not new or not labs or g.count(OP, "Wire") <= w0:
                if new:
                    del_terms(new)
                continue
            if not labs[-1].lower().startswith(param.lower()):
                del_terms(new); continue
            print(f"   temp indicator {labs[-1]!r} on {param} t{t}: ExecState {g.exec_state(OP)}", flush=True)
            try:
                # NOTE the two index spaces: create_indicator takes the Nodes[] index, wire_indicators (OpWireInd traverses for
                # `Class Name`) takes the index WITHIN THAT CLASS - passing the Nodes[] index gave error 1055 at its TMSC.
                g.wire_indicators(OP, cls_i("CallLibrary", uK), [param], [ind], node_class="CallLibrary")
                done = True; print(f"   {param} -> {ind!r} OK (ExecState {g.exec_state(OP)})", flush=True)
            except Exception as e:
                print(f"   {param} -> {ind!r}: EXC {str(e)[:200]} (ExecState now {g.exec_state(OP)})", flush=True)
            del_terms(new)                                                  # the branch to the pane indicator survives
            print(f"   after deleting the temp indicator: wires {g.count(OP, 'Wire')} ExecState {g.exec_state(OP)}", flush=True)
            break
        if not done:
            print(f"   could not wire {param} to {ind!r} - continuing to collect the other outcomes", flush=True)
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    labels = {"Function": fn_ctl, **made}
    print("\nassembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es, "\nNEW CONTROLS", labels, flush=True)
    print("steps failed:", [n for n, ok in STEPS if not ok], flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 7
    print("saved", g.save(OP), flush=True)
    json.dump(labels, open(os.path.join(os.path.dirname(HERE), "bench", "gpu_kernel_labels.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
