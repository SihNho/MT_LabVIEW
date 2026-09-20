"""build_harness_display.py - HARNESS_disp{0..3}.vi: the main VI's display route on the recorded fixture, stage by stage.

    disp0  IMAQ Create -> IMAQ ReadFile(File Path)                                   (loader only = the base)
    disp1  + IMAQ ImageToArray                                                        (the copy)
    disp2  + Flatten Pixmap.vi                                                        (array -> picture data)
    disp3  + Draw Flattened Pixmap.vi -> Picture indicator                            (picture -> panel object)
Timed from Python (tools/bench/run_display_bench.py: one Run per frame, perf_counter, base-subtracted - the pattern
of every accepted benchmark row), in two named conditions: panel CLOSED (construction cost) and panel OPEN
(representative; the user runs the experiment with the panel visible). Peer review archive/peer/2026-09-14-display-
path-harness-plan.md: 'IMAQdx Get Image' is NOT in this chain (a file replaces acquisition), the IMAQ Image Display
control is NOT measured (no donor control in the fleet), Tick Count is not used.

BUILD: disp3 is built fully on a cleared FPTARGET_v0 copy (the HARNESS_gpu2 pattern: drop vi.lib VIs, wire by the
terminal names READ OFF EACH NODE after the drop, controls/indicators by Terminal.Create Control/Indicator); then
disp2/1/0 are disk copies of disp3 with the tail deleted (delete_object + Remove Bad Wires), each saved iff ExecState 1.
Prediction per step; a miss prints 'exc'/'STOP' and nothing is saved.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_harness_display.log -- py -u tools/recipes/build_harness_display.py
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
LV = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib"
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create")
R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile")
A_VI = os.path.join(VIS, "Basics.llb", "IMAQ ImageToArray")
F_VI = os.path.join(LV, "picture", "pixmap.llb", "Flatten Pixmap.vi")
D_VI = os.path.join(LV, "picture", "picture.llb", "Draw Flattened Pixmap.vi")
SRC = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi")
OUT = {k: os.path.join(g.CLAUDEDEV, f"HARNESS_disp{k}.vi") for k in range(4)}
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "harness_display_labels.json")
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
    OP = OUT[3]
    for p in OUT.values():
        try:
            g.close_panel(p); time.sleep(0.2)
        except Exception:
            pass
        if os.path.exists(p):
            os.remove(p)
    for p in (C_VI, R_VI, A_VI, F_VI, D_VI, SRC):
        # a VI inside an .llb is not a filesystem entry (run 1 stopped here): check the container instead
        cont = p.split(".llb")[0] + ".llb" if ".llb" in p else p
        if not os.path.exists(cont):
            print(f"STOP: missing {cont}", flush=True); return 2
    shutil.copyfile(SRC, OP); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for idx in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", idx, verify=False)
            g.remove_bad_wires_scripted(OP)

    def sub_i(uid):
        return [o["uid"] for o in g.report_all(OP, "SubVI")].index(uid)

    def snap(tag=""):
        return f"{tag} SubVI={len(g.report_all(OP, 'SubVI'))} Wire={len(g.report_all(OP, 'Wire'))} CtlTerm={len(g.report_all(OP, 'ControlTerminal'))} ExecState={g.exec_state(OP)}"

    # 0 clear the base target completely (nodes, then panel terminals)
    n0 = len(g.report_all(OP, "Node"))
    for _ in range(n0 + 2):
        if not g.report_all(OP, "Node"):
            break
        try:
            g.delete_object(OP, "Node", 0, verify=False)
        except Exception:
            break
    g.remove_bad_wires_scripted(OP)
    for _ in range(40):
        if not g.report_all(OP, "ControlTerminal"):
            break
        g.delete_object(OP, "ControlTerminal", 0, verify=False)
    g.remove_bad_wires_scripted(OP); purge()
    print("base cleared:", snap(), flush=True)

    NODE = {}          # uid -> (Nodes[] index, {terminal name: (index, is_source, wire)})

    def drop(path, pos):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, pos)
        new = [u for u in g.uids(OP, "SubVI") if u not in before]
        assert len(new) == 1, f"drop {os.path.basename(path)}: {len(new)} new"
        u = new[0]
        # terminal names READ from the node itself with node_terms (OpNodeTerms_v0): the walker stops after three
        # unassigned pane slots and reported Draw Flattened Pixmap.vi with NO terminals (run 2); node_terms returns
        # the whole Terminals[] array. Nodes[] index found by uid (creation order, junk purged before every drop).
        n = None
        for cand in range(len(g.report_all(OP, "Node")) + 2):
            nu, rows = g.node_terms_uid(OP, 0, cand)
            if not nu:
                break
            if nu == u:
                n = cand; NODE[u] = (n, {r["name"]: (r["i"], r["is_source"], r["wire"]) for r in rows if r["name"]})
                break
        assert n is not None, f"drop {os.path.basename(path)}: uid {u} not found in Nodes[]"
        print(f"   dropped {os.path.basename(path)} uid {u} Nodes[] {n}: {list(NODE[u][1].keys())}", flush=True)
        return u

    def tname(u, *cands):
        names = NODE[u][1]
        for c in cands:
            if c in names:
                return c
        for c in cands:
            hit = [nm for nm in names if c.lower() in nm.lower()]
            if len(hit) == 1:
                return hit[0]
        raise RuntimeError(f"no terminal among {cands} on uid {u}: {list(names)}")

    def ws(su, st, du, dt):
        return g.wire(OP, "SubVI", sub_i(su), st, "SubVI", sub_i(du), dt)

    uC = step("1 drop IMAQ Create", "+1 SubVI", lambda: drop(C_VI, (100, 300)))
    uR = step("2 drop IMAQ ReadFile", "+1 SubVI", lambda: drop(R_VI, (330, 300)))
    uA = step("3 drop IMAQ ImageToArray", "+1 SubVI", lambda: drop(A_VI, (560, 300)))
    uF = step("4 drop Flatten Pixmap.vi", "+1 SubVI", lambda: drop(F_VI, (790, 300)))
    uD = step("5 drop Draw Flattened Pixmap.vi", "+1 SubVI", lambda: drop(D_VI, (1020, 300)))
    if None in (uC, uR, uA, uF, uD):
        print("STOP: a drop failed. Nothing saved.", flush=True); return 3
    step("6 image chain wires", "Wire +4",
         lambda: ([ws(uC, tname(uC, "New Image"), uR, tname(uR, "Image")),
                   ws(uR, tname(uR, "Image Out"), uA, tname(uA, "Image")),
                   ws(uC, "error out", uR, "error in (no error)"),
                   ws(uR, "error out", uA, "error in (no error)")], snap("after"))[1])
    step("7 ImageToArray -> Flatten Pixmap -> Draw Flattened Pixmap", "Wire +2 (+ error chain where present)",
         lambda: ([ws(uA, tname(uA, "Image Pixels (U8)"), uF, tname(uF, "8-bit pixmap")),
                   ws(uF, tname(uF, "image data"), uD, tname(uD, "image data"))], snap("after"))[1])
    # optional error chain into Flatten/Draw if they have error terminals
    for su, du in ((uA, uF), (uF, uD)):
        try:
            if "error out" in NODE[su][1] and "error in (no error)" in NODE[du][1]:
                ws(su, "error out", du, "error in (no error)")
        except Exception as e:
            print(f"   (error chain {su}->{du} skipped: {str(e)[:80]})", flush=True)

    # controls on the required inputs: Image Name (Create), File Path (ReadFile); indicator on Draw's 'new picture'
    labels = {}

    def make(uid, term, kind):
        n = NODE[uid][0]; ti = NODE[uid][1][term][0]
        fp0 = {l for _i, l, _ in g.fp_labels(OP)}; w0 = len(g.report_all(OP, "Wire"))
        (g.create_control if kind == "control" else g.create_indicator)(OP, n, ti); purge()
        new = [l for _i, l, _ in g.fp_labels(OP) if l not in fp0]
        ok = bool(new) and len(g.report_all(OP, "Wire")) > w0
        print(f"   {kind} on {term!r} (node {n} t{ti}) -> {new} wired={ok} ExecState {g.exec_state(OP)}", flush=True)
        if not ok:
            raise RuntimeError(f"{kind} on {term} not wired")
        return new[-1]
    labels["Image Name"] = step("8 control Image Name (IMAQ Create)", "control wired", lambda: make(uC, tname(uC, "Image Name"), "control"))
    labels["File Path"] = step("9 control File Path (IMAQ ReadFile)", "control wired", lambda: make(uR, tname(uR, "File Path"), "control"))
    labels["Picture"] = step("10 indicator on Draw Flattened Pixmap 'new picture'", "Picture indicator wired",
                             lambda: make(uD, tname(uD, "new picture", "picture"), "indicator"))
    es = g.exec_state(OP)
    print("\n" + snap("disp3 assembled:"), "labels", labels, flush=True)
    if es != 1 or None in labels.values():
        # required-input probe: give every unwired input of D, F, A a control until runnable (gpu2 lesson)
        print("   disp3 not runnable - probing required inputs", flush=True)
        for uid in (uD, uF, uA, uR, uC):
            for term, (ti, _s, w) in list(NODE[uid][1].items()):
                if g.exec_state(OP) == 1:
                    break
                if w or term.startswith("error") or term in ("New Image", "Image", "Image Out", "image data", "new picture"):
                    continue
                try:
                    lab = make(uid, term, "control")
                    if g.exec_state(OP) == 1:
                        labels[f"required:{term}"] = lab; print(f"   REQUIRED input found: {term!r} on uid {uid}", flush=True)
                        break
                    # not the breaker: remove that control again
                    ct = g.report_all(OP, "ControlTerminal")
                    g.delete_object(OP, "ControlTerminal", len(ct) - 1, verify=False); g.remove_bad_wires_scripted(OP)
                except Exception as e:
                    print(f"   probe {term!r}: {str(e)[:80]}", flush=True)
        es = g.exec_state(OP)
    if es != 1 or any(k == "exc" for _n, k in STEPS) or None in labels.values():
        # run 2 saved a disp3 whose tail was never wired because only ExecState was checked: every planned step
        # must have succeeded and every planned control/indicator must exist before anything is saved
        print(f"\nVERDICT: BROKEN or INCOMPLETE (ExecState {es}, steps {STEPS}, labels {labels}) - NOT SAVING.", flush=True); return 4
    step("11 auto error handling OFF + save disp3", "saved", lambda: (g.set_auto_error_handling(OP, False), g.save(OP))[1])
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump({"labels": labels, "nodes": {"create": uC, "readfile": uR, "imagetoarray": uA, "flatten": uF, "draw": uD}}, f, indent=2)

    # disp2/1/0: copies with the tail deleted
    tails = {2: [uD], 1: [uD, uF], 0: [uD, uF, uA]}
    for k in (2, 1, 0):
        dst = OUT[k]
        shutil.copyfile(OP, dst); g.report_all(dst, "SubVI"); g.open_panel(dst); time.sleep(0.8)
        for u in tails[k]:
            ids = [o["uid"] for o in g.report_all(dst, "SubVI")]
            if u in ids:
                g.delete_object(dst, "SubVI", ids.index(u), verify=False)
        g.remove_bad_wires_scripted(dst)
        # a dangling Picture indicator terminal is legal; leave it
        esk = g.exec_state(dst)
        print(f"   disp{k}: SubVI={len(g.report_all(dst, 'SubVI'))} Wire={len(g.report_all(dst, 'Wire'))} ExecState={esk}", flush=True)
        if esk == 1:
            g.set_auto_error_handling(dst, False); g.save(dst)
        else:
            print(f"   disp{k} BROKEN - not saved", flush=True)
    print("steps:", STEPS, flush=True)
    print("\nVERDICT: HARNESS_disp3..0 built (structural) - run tools/bench/run_display_bench.py next", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
