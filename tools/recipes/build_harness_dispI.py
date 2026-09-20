r"""build_harness_dispI.py - HARNESS_dispI.vi: the IMAQ Image Display route (image reference wired straight into the
control's terminal - NI's documented normal way), to compare with the Picture route measured in
archive/bench-2026-09-14-display-path.

DONOR (copies are allowed; the original is never touched): NI's example
  C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision Acquisition\NI-IMAQdx\Basic Acquisition\Acquire Single Image (Snap).vi
whose panel holds exactly two objects (probed 2026-09-14): 'Image' (the Image Display indicator) and 'Camera Name'.
STEPS: copy -> open_panel -> delete every diagram node (+RBW) -> delete the 'Camera Name' terminal (keep 'Image') ->
drop IMAQ Create + IMAQ ReadFile -> controls Image Name / File Path -> wire_indicators(ReadFile 'Image Out' -> 'Image')
-> auto error handling OFF -> save iff every planned step succeeded and ExecState == 1 -> close the panel.
  py tools/bgrun.py --max-min 15 --log tools/bench/build_harness_dispI.log -- py -u tools/recipes/build_harness_dispI.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create")
R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile")
A_VI = os.path.join(VIS, "Basics.llb", "IMAQ ImageToArray")
SRC = r"C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision Acquisition\NI-IMAQdx\Basic Acquisition\Acquire Single Image (Snap).vi"
OP = os.path.join(g.CLAUDEDEV, "HARNESS_dispI.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "harness_dispI_labels.json")
g._run.__defaults__ = (6.0, 90.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def main():
    g._lv = None
    try:
        g.close_panel(OP); time.sleep(0.2)
    except Exception:
        pass
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for idx in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", idx, verify=False)
            g.remove_bad_wires_scripted(OP)

    def snap(tag=""):
        return f"{tag} Node={len(g.report_all(OP, 'Node'))} SubVI={len(g.report_all(OP, 'SubVI'))} Wire={len(g.report_all(OP, 'Wire'))} CtlTerm={len(g.report_all(OP, 'ControlTerminal'))} panel={[l for _i, l, _ in g.fp_labels(OP)]} ExecState={g.exec_state(OP)}"

    print(snap("donor copy:"), flush=True)
    labs0 = [(i, l, ind) for i, l, ind in g.fp_labels(OP)]
    if [l for _i, l, _ in labs0] != ["Image", "Camera Name"]:
        print(f"STOP: donor panel differs from the probe: {labs0}", flush=True); return 2
    # 1 clear every diagram node
    for _ in range(len(g.report_all(OP, "Node")) + 2):
        if not g.report_all(OP, "Node"):
            break
        try:
            g.delete_object(OP, "Node", 0, verify=False)
        except Exception:
            break
    g.remove_bad_wires_scripted(OP); purge()
    # 2 delete the 'Camera Name' terminal, keep 'Image': ControlTerminal Traverse order != panel order - delete one at a
    #   time and check the panel labels; revert (recopy) if the wrong one went.
    cts = g.report_all(OP, "ControlTerminal")
    done = False
    for i in range(len(cts) - 1, -1, -1):
        try:
            g.delete_object(OP, "ControlTerminal", i, verify=False)
        except Exception as e:
            print(f"   delete ControlTerminal[{i}]: {str(e)[:80]}", flush=True); continue
        g.remove_bad_wires_scripted(OP)
        labs = [l for _i, l, _ in g.fp_labels(OP)]
        if labs == ["Image"]:
            done = True; break
        print(f"   ControlTerminal[{i}] removed the wrong object (panel now {labs}) - restarting from a fresh copy", flush=True)
        try:
            g.close_panel(OP)
        except Exception:
            pass
        os.remove(OP); shutil.copyfile(SRC, OP); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(0.8)
        for _ in range(12):
            if not g.report_all(OP, "Node"):
                break
            try:
                g.delete_object(OP, "Node", 0, verify=False)
            except Exception:
                break
        g.remove_bad_wires_scripted(OP); purge()
    print(snap("cleared:"), flush=True)
    if not done:
        print("STOP: could not isolate the Image Display object. Nothing saved.", flush=True); return 3

    NODE = {}

    def drop(path, pos):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
        new = [u for u in g.uids(OP, "SubVI") if u not in before]
        assert len(new) == 1
        u = new[0]; n = None
        for cand in range(len(g.report_all(OP, "Node")) + 2):
            nu, rows = g.node_terms_uid(OP, 0, cand)
            if not nu:
                break
            if nu == u:
                n = cand; NODE[u] = (n, {r["name"]: (r["i"], r["is_source"], r["wire"]) for r in rows if r["name"]}); break
        assert n is not None
        print(f"   dropped {os.path.basename(path)} uid {u} Nodes[] {n}: {list(NODE[u][1].keys())}", flush=True)
        return u

    def sub_i(uid):
        return [o["uid"] for o in g.report_all(OP, "SubVI")].index(uid)

    uC = step("3 drop IMAQ Create", "+1", lambda: drop(C_VI, (100, 300)))
    uR = step("4 drop IMAQ ReadFile", "+1", lambda: drop(R_VI, (330, 300)))
    # run 1 (14:5x): wire_indicators raised 5001 - its contract (docstring) says the SOURCE terminal must already be
    # wired, because Wire Indicators.vi BRANCHES the indicator onto the existing wire. 'Image Out' had no consumer.
    # So the chain is disp1's (…-> IMAQ ImageToArray) and the Image Display branches off the Image Out wire; the
    # bench subtracts disp1, not disp0.
    uA = step("4b drop IMAQ ImageToArray (consumer of Image Out, = disp1's chain)", "+1", lambda: drop(A_VI, (560, 300)))
    if None in (uC, uR, uA):
        return 3
    step("5 C.New Image -> R.Image; R.Image Out -> A.Image; error chain", "Wire +4",
         lambda: ([g.wire(OP, "SubVI", sub_i(uC), "New Image", "SubVI", sub_i(uR), "Image"),
                   g.wire(OP, "SubVI", sub_i(uR), "Image Out", "SubVI", sub_i(uA), "Image"),
                   g.wire(OP, "SubVI", sub_i(uC), "error out", "SubVI", sub_i(uR), "error in (no error)"),
                   g.wire(OP, "SubVI", sub_i(uR), "error out", "SubVI", sub_i(uA), "error in (no error)")], snap("after"))[1])
    labels = {}

    def make_control(uid, term):
        n = NODE[uid][0]; ti = NODE[uid][1][term][0]
        fp0 = {l for _i, l, _ in g.fp_labels(OP)}; w0 = len(g.report_all(OP, "Wire"))
        g.create_control(OP, n, ti); purge()
        new = [l for _i, l, _ in g.fp_labels(OP) if l not in fp0]
        ok = bool(new) and len(g.report_all(OP, "Wire")) > w0
        print(f"   control on {term!r} -> {new} wired={ok} ExecState {g.exec_state(OP)}", flush=True)
        if not ok:
            raise RuntimeError(f"control on {term} not wired")
        return new[-1]
    labels["Image Name"] = step("6 control Image Name", "wired", lambda: make_control(uC, "Image Name"))
    labels["File Path"] = step("7 control File Path", "wired", lambda: make_control(uR, "File Path"))
    # Runs 1-2 (14:5x): Wire Indicators.vi raised 5001 for the Image Display even with the source wired, and so did the
    # peer's probe with another output -> the library's indicator-by-label lookup does not see a Vision Image Display
    # control (H1, archive/peer/2026-09-14-dispI-wire-indicators-5001.md). Route 2: OpWire_v1 (Wire Inputs.vi) with
    # the destination as a ControlTerminal by Traverse index and the sink terminal named after the label; the wrong
    # terminal raises 5001 / is declined; success is verified by EFFECT below (panel_wiring wire uid != 0).
    # Route 3 (peer, archive/peer/2026-09-14-opconnectctl-v0-plan.md): OpConnectCtl_v0 = Terminal.Connect Wire on the
    # panel object's own terminal (Panel.Controls[] -> Control.Terminal), source = ReadFile 'Image Out' by Nodes[] /
    # Terminals[] index. Verification ORDER: invoke error -> the display terminal gained a wire AND the ImageToArray
    # wire is still there -> ExecState 1 -> only then anything else.
    def route3():
        panel_i = next(i for i, l, _ in g.fp_labels(OP) if l == "Image")
        n_r, terms_r = NODE[uR]; ti = terms_r["Image Out"][0]
        w_before = {o["uid"] for o in g.report_all(OP, "Wire")}
        err = g.connect_ctl(OP, panel_i, n_r, ti)
        img = next((r for r in g.panel_wiring(OP) if r["label"] == "Image"), None)
        a_in = next((r for r in g.node_terms(OP, 0, NODE[uA][0]) if r["name"] == "Image"), None)
        print(f"   connect_ctl -> err={err!r}; Image terminal wire = {img and img['wire']}; ImageToArray.Image wire = {a_in and a_in['wire']}; "
              f"wires {len(w_before)} -> {len(g.report_all(OP, 'Wire'))}; ExecState {g.exec_state(OP)}", flush=True)
        if err or not (img and img["wire"]) or not (a_in and a_in["wire"]):
            raise RuntimeError(f"connect_ctl did not wire the display: err={err!r}")
        return img["wire"]
    step("8 connect_ctl: ReadFile 'Image Out' -> Image Display terminal (branch, Terminal.Connect Wire)", "wire on the Image terminal; ImageToArray wire kept; ExecState 1", route3)
    # verify by EFFECT: the panel object's terminal now carries a wire (panel_wiring reads Control.Terminal -> wire)
    pw = g.panel_wiring(OP)
    img = next((r for r in pw if r["label"] == "Image"), None)
    wired = bool(img and img["wire"])
    print(f"   panel wiring after the branch: {pw}", flush=True)
    es = g.exec_state(OP)
    if es != 1 or not wired or any(k == "exc" for _n, k in STEPS) or None in labels.values():
        print(f"\nVERDICT: BROKEN or INCOMPLETE (ExecState {es}, image wire {wired}, steps {STEPS}) - NOT SAVING.", flush=True); return 4
    labels["Image"] = "Image"
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump({"labels": labels, "donor": SRC}, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("steps:", STEPS, flush=True)
    print("\nVERDICT: HARNESS_dispI built and saved (structural) - run tools/bench/run_dispI_bench.py next", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
