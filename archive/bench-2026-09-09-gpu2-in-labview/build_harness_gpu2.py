"""build_harness_gpu2.py - HARNESS_gpu2.vi: OUR GPU interface (user 2026-09-09: not the Saleh node) - one CLFN per frame,
raw IMAQ pixel pointer, DBL in/out, no image copies.  Built with ZERO GUI from a cleared FPTARGET_v0 copy:
  IMAQ Create ('Image Name' ctrl) -> IMAQ ReadFile ('File Path' ctrl) -> IMAQ GetImagePixelPtr -> CLFN mt2_track_simple
  (gscript.build_clfn: Params global -> Pre globals -> NI Create.vi + attribute sets, 15 parameters from tools/gpu/clfn_params.py)
  GetImagePixelPtr.'Pixel Pointer out' -> CLFN.pixel_ptr ; 'LineWidth(Pixels)' -> CLFN.line_width_bytes (U8 image: 1 B/px)
  every other CLFN input = front-panel control (cal_path, width, height, nb, xyz_in, good_in, xyz_out/idx_out/good_out buffers,
  status buffer, status_len, flags), every output = indicator (one pass over the node's terminals, labels = parameter names).
Prediction contract: ExecState 1; wires = 2 (image chain) + 2 (pointer/linewidth) + 2 (error chain) + controls/indicators.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_harness_gpu2.log -- py -u tools/recipes/build_harness_gpu2.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create"); R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile"); P_VI = os.path.join(VIS, "Basics.llb", "IMAQ GetImagePixelPtr")
SRC = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu2.vi")
DLL = os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"); FN = "mt2_track_simple"      # NO space in the file name: a scripted CLFN on 'GPU Tracking.dll' is broken (probe I/J/K 2026-09-09)
FLAT = open(os.path.join(os.path.dirname(HERE), "bench", "paraminfo_mt2.hex")).read().strip()
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
    inv0 = g.uids(OP, "Invoke")

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))

    RANK = {}                                                       # uid -> Nodes[] index = CREATION order (junk Invokes purged before every drop);
                                                                    # a Traverse("Node") report is NOT in Nodes[] order (2026-09-09: t2 of the wrong node)

    def node_index(uid):
        return RANK[uid]

    def sub_i(uid):
        return [o["uid"] for o in g.report(OP, "SubVI")].index(uid)

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

    BREAKERS = []

    def guarded(new, lab, what, es_before):
        """RELATIVE guard: a scripted CLFN's argument inputs act as REQUIRED until wired (probe 2026-09-09 13:0x), so the VI is
        broken until the last input gets its control - only a 1 -> 0 transition marks a breaker (deleted); 0 -> 0 is kept."""
        es = g.exec_state(OP)
        if es == 1 or es_before != 1:
            return lab
        del_terms(new); es2 = g.exec_state(OP); BREAKERS.append((what, lab, es2)); print(f"   BREAKS: {what} {lab!r} -> ExecState 1 -> {es} (removed -> {es2})", flush=True)
        return None

    def control_at(uid, t):
        """control on terminal t of node uid if it is an unwired INPUT (and does not break a runnable VI) -> label, else None"""
        n = node_index(uid); es0 = g.exec_state(OP); w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
        if new and g.count(OP, "Wire") > w0:
            return guarded(new, lab, f"control t{t}", es0)
        if new:
            del_terms(new)
        return None

    def indicator_at(uid, t):
        n = node_index(uid); es0 = g.exec_state(OP); fp0 = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
        new = g.create_indicator(OP, n, t); purge(); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
        if new and labs and g.count(OP, "Wire") > w0:
            return guarded(new, labs[-1], f"indicator t{t}", es0)
        if new:
            del_terms(new)
        return None

    # 0. clear the base
    while g.count(OP, "Node"):
        try:
            g.delete_object(OP, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(OP)
    while g.count(OP, "ControlTerminal"):
        g.delete_object(OP, "ControlTerminal", 0)
    g.remove_bad_wires_scripted(OP); purge()
    print("base cleared: nodes", g.count(OP, "Node"), "ExecState", g.exec_state(OP), flush=True)
    # 1. image chain
    uC = step("drop IMAQ Create", "+1", lambda: drop(C_VI, (100, 300)))
    uR = step("drop IMAQ ReadFile", "+1", lambda: drop(R_VI, (320, 300)))
    uP = step("drop IMAQ GetImagePixelPtr", "+1", lambda: drop(P_VI, (540, 300)))
    if None in (uC, uR, uP):
        return 2
    ws = lambda su, st, du, dt, br=False: g.wire(OP, "SubVI", sub_i(su), st, "SubVI", sub_i(du), dt, branch=br)
    step("C.New Image -> R.Image", "+1", lambda: ws(uC, "New Image", uR, "Image"))
    step("R.Image Out -> P.Image", "+1", lambda: ws(uR, "Image Out", uP, "Image"))
    step("C.error out -> R.error in", "+1", lambda: ws(uC, "error out", uR, "error in (no error)"))
    step("R.error out -> P.error in", "+1", lambda: ws(uR, "error out", uP, "error in (no error)"))
    print("   ExecState after image chain (File Path still unwired = required?):", g.exec_state(OP), flush=True)
    # 1b. harness controls on IMAQ Create / ReadFile FIRST (ReadFile's File Path is required: the VI is broken until it is wired)
    labels = {}; outs = {}
    for uid, nm, t in ((uC, "Image Name", 2), (uR, "File Path", 7)):
        n = node_index(uid); w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
        print(f"   control {nm!r}: {lab!r} wired={g.count(OP, 'Wire') > w0} ExecState {g.exec_state(OP)}", flush=True)
        if lab != nm:
            print("STOP: control label mismatch", flush=True); return 4
        labels[nm] = lab
    if g.exec_state(OP) != 1:
        # a REQUIRED input is unwired somewhere in the chain (2026-09-09: still broken with Image Name + File Path wired ->
        # suspect IMAQ GetImagePixelPtr).  Probe: give each unwired input of P (then R, then C) a control; keep the ones that
        # turn ExecState to 1, delete the rest.
        for uid, name in ((uP, "GetImagePixelPtr"), (uR, "ReadFile"), (uC, "Create")):
            for t in range(0, 14):
                if g.exec_state(OP) == 1:
                    break
                n = node_index(uid); w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
                if new and g.count(OP, "Wire") > w0:
                    es = g.exec_state(OP); print(f"   required-input probe {name} t{t}: control {lab!r} -> ExecState {es}", flush=True)
                    if es == 1:
                        labels[lab] = f"{name} t{t}"; break
                    del_terms(new)
                elif new:
                    del_terms(new)
            if g.exec_state(OP) == 1:
                break
        print("   ExecState after required-input probe:", g.exec_state(OP), "controls", labels, flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: image chain broken before the CLFN", flush=True); return 4
    # 2. the CLFN (our interface)
    purge(); res = step("build_clfn mt2_track_simple (15 params)", "+1 CallLibrary, 30 terms, no errors", lambda: g.build_clfn(OP, (900, 300), DLL, FN, FLAT))
    if not res:
        return 3
    uK = res[0]; purge(); RANK[uK] = g.count(OP, "Node") - 1; print("   RANK", RANK, "nodes", g.count(OP, "Node"), flush=True)
    print("   ExecState after CLFN build:", g.exec_state(OP), flush=True)
    w = lambda su, st, dt, br=False: g.wire(OP, "SubVI", sub_i(su), st, "CallLibrary", [o["uid"] for o in g.report(OP, "CallLibrary")].index(uK), dt, branch=br)
    step("P.Pixel Pointer out -> CLFN.pixel_ptr", "+1", lambda: w(uP, "Pixel Pointer out", "pixel_ptr"))
    print("   ExecState after pixel_ptr wire:", g.exec_state(OP), flush=True)
    step("P.LineWidth(Pixels) -> CLFN.line_width_bytes", "+1", lambda: w(uP, "LineWidth(Pixels)", "line_width_bytes"))
    g.remove_bad_wires_scripted(OP); print("   ExecState after pointer wires:", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
    # 3. error indicator on GetImagePixelPtr
    for t in range(0, 12):
        lab = indicator_at(uP, t)
        if lab and lab.lower().startswith("error out"):
            outs["error out"] = lab; print("   P error out indicator:", lab, flush=True); break
        if lab:
            outs["P " + lab] = t                                        # other GetImagePixelPtr outputs: harmless extra indicators
    # 4. one pass over the CLFN terminals: unwired inputs -> controls, outputs -> indicators (labels = parameter names)
    misses = 0
    for t in range(0, 40):
        lab = control_at(uK, t)
        if lab:
            labels[lab] = t; print(f"   CLFN t{t}: control {lab!r}", flush=True); continue
        lab = indicator_at(uK, t)
        if lab:
            outs[lab] = t; print(f"   CLFN t{t}: indicator {lab!r}", flush=True); misses = 0; continue
        misses += 1; print(f"   CLFN t{t}: (wired or none)", flush=True)
        if t >= 30 and misses >= 3:
            break
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es, "\nCONTROLS", labels, "\nOUTPUTS", outs, "\nBREAKERS", BREAKERS, flush=True)
    need = ("cal_path", "width", "height", "nb", "xyz_in", "good_in", "xyz_out", "idx_out", "good_out", "status", "status_len", "flags", "Image Name", "File Path")
    missing = [n for n in need if n not in labels]
    if es != 1 or missing:
        print("STOP: broken or missing controls", missing, "- NOT saving", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    json.dump({"controls": labels, "outputs": outs}, open(os.path.join(os.path.dirname(HERE), "bench", "harness_gpu2_labels.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
