"""build_harness_copyloop.py - HARNESS_copyloop.vi: N repeated IMAQ Copy A->B inside ONE Run (steady-state copy cost).

Peer reviews: archive/peer/2026-09-14-imaq-copy-handoff-plan.md (the cell) and …copyloop-forloop-tunnels-plan.md
(the mechanism: N comes from an AUTO-INDEXED 2D U8 array control 'rows' - rows = N x 1 from Python, 0 rows = the loop
runs 0 times = baseline T(0); per-copy cost = (T(N) - T(0)) / N). GO/NO-GO GATE (peer): build the EMPTY loop with
`for_loop(tunnels=['<label>'], indexing=[True])` first and require reporter evidence - one new LoopTunnel with
IndexMode 1 (tunnels()) and ExecState 1 - before adding anything; a clean return alone proves nothing.

Base: a copy of HARNESS_copy1 (IMAQ Create A -> ReadFile -> Create B -> IMAQ Copy A->B, all wired, controls
Image Name / Image Name 2 / File Path). Steps:
  1  copy, open_panel
  2  the array control: drop Flatten Pixmap.vi, create_control on its '8-bit pixmap' input, delete the Flatten node
     (+RBW); the 2D U8 control stays, unwired                                                   ExecState 1
  3  GATE: for_loop(tunnels=[that label], indexing=[True]) -> exactly one new LoopTunnel, IndexMode 1, its outer wire
     on the control's terminal (panel_wiring), ExecState 1 (a loop with an indexed input needs no N)
  4  drop IMAQ Copy INSIDE the body; wire outer Copy 'Image Dst Out' -> inner 'Image Dst' (orders outer before loop) and
     ReadFile 'Image Out' -> inner 'Image Src' (branch=True: already wired to the outer copy)     ExecState 1
  5  auto error handling OFF; save iff every step ok
  py tools/bgrun.py --max-min 15 --log tools/bench/build_harness_copyloop.log -- py -u tools/recipes/build_harness_copyloop.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

LV = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib"
F_VI = os.path.join(LV, "picture", "pixmap.llb", "Flatten Pixmap.vi")
K_VI = os.path.join(r"C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision", "Management.llb", "IMAQ Copy")
SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copy1.vi")
OP = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "harness_copyloop_labels.json")
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
        return (f"{tag} SubVI={len(g.report_all(OP, 'SubVI'))} ForLoop={len(g.report_all(OP, 'ForLoop'))} "
                f"LoopTunnel={len(g.report_all(OP, 'LoopTunnel'))} Wire={len(g.report_all(OP, 'Wire'))} "
                f"panel={[l for _i, l, _ in g.fp_labels(OP)]} ExecState={g.exec_state(OP)}")

    NODE = {}

    def drop(path, pos, diagram=0):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, diagram, pos)
        new = [u for u in g.uids(OP, "SubVI") if u not in before]
        assert len(new) == 1, f"drop: {len(new)} new"
        u = new[0]; n = None
        for cand in range(len(g.report_all(OP, "Node")) + 4):
            nu, rows = g.node_terms_uid(OP, diagram, cand)
            if not nu:
                break
            if nu == u:
                n = cand; NODE[u] = (n, {r["name"]: (r["i"], r["is_source"], r["wire"]) for r in rows if r["name"]}); break
        assert n is not None
        print(f"   dropped {os.path.basename(path)} uid {u} diagram {diagram} Nodes[] {n}: {list(NODE[u][1].keys())}", flush=True)
        return u

    def sub_i(uid):
        return [o["uid"] for o in g.report_all(OP, "SubVI")].index(uid)

    print(snap("base:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: base copy not runnable.", flush=True); return 2
    # existing nodes by terminal signature (base = HARNESS_copy1)
    for cand in range(12):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            break
        NODE[nu] = (cand, {r["name"]: (r["i"], r["is_source"], r["wire"]) for r in rows if r["name"]})
    uR = next(u for u, (n, t) in NODE.items() if "Image Out" in t and "File Path" in t)
    uK = next(u for u, (n, t) in NODE.items() if "Image Dst Out" in t)
    print(f"   ReadFile uid {uR}; outer IMAQ Copy uid {uK}", flush=True)

    # 2 the 2D U8 array control
    uF = step("2a drop Flatten Pixmap.vi (only to obtain a 2D U8 control)", "+1", lambda: drop(F_VI, (100, 700)))
    if not uF:
        return 3
    fp0 = {l for _i, l, _ in g.fp_labels(OP)}
    step("2b create_control on Flatten '8-bit pixmap'", "a 2D U8 array control appears",
         lambda: (g.create_control(OP, NODE[uF][0], NODE[uF][1]["8-bit pixmap"][0]), purge())[0])
    rows_label = next((l for _i, l, _ in g.fp_labels(OP) if l not in fp0), None)
    print(f"   array control label: {rows_label!r}", flush=True)
    if not rows_label:
        print("STOP: no array control created.", flush=True); return 3
    step("2c delete the Flatten node (+RBW) - the control stays", "SubVI -1, ExecState 1",
         lambda: (g.delete_object(OP, "SubVI", sub_i(uF), verify=False), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    if g.exec_state(OP) != 1 or rows_label not in [l for _i, l, _ in g.fp_labels(OP)]:
        print("STOP: control lost or VI broken after deleting Flatten.", flush=True); return 3

    # 3 GATE: the empty loop with the indexed input from the control
    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    step("3a for_loop(tunnels=[rows_label], indexing=[True])", "ForLoop +1, LoopTunnel +1 (indexed input from the control)",
         lambda: (g.for_loop(OP, (700, 700), tunnels=[rows_label], indexing=[True]), snap("after"))[1])
    new_t = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
    evidence = None
    for o in new_t:
        t = g.tunnels(OP, o["i"])
        print(f"   new LoopTunnel index {o['i']} uid {o['uid']}: {t}", flush=True)
        evidence = t
    ctl = next((r for r in g.panel_wiring(OP) if r["label"] == rows_label), None)
    print(f"   array control terminal after for_loop: {ctl}", flush=True)
    gate = (len(new_t) == 1 and evidence and evidence["index_mode"] == 1 and not evidence["out_is_source"]
            and ctl and ctl["wire"] and ctl["wire"] == evidence["out_wire"] and g.exec_state(OP) == 1)
    print(f"   GATE (one indexed input tunnel wired from the control, ExecState 1): {'PASS' if gate else 'FAIL'}", flush=True)
    if not gate:
        print("STOP: the Control Names route did not produce the indexed tunnel - mechanism NOT available; nothing saved.", flush=True)
        return 4
    body = next(i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner")))

    # 4 the inner copy
    uKi = step("4a drop IMAQ Copy inside the loop body", "+1 SubVI in the body", lambda: drop(K_VI, (760, 760), body))
    if not uKi:
        return 3
    step("4b outer Copy 'Image Dst Out' -> inner 'Image Dst' (orders outer copy before the loop)", "tunnel +1, ExecState 0 or 1",
         lambda: (g.wire(OP, "SubVI", sub_i(uK), "Image Dst Out", "SubVI", sub_i(uKi), "Image Dst"), snap("after"))[1])
    step("4c ReadFile 'Image Out' -> inner 'Image Src' (branch: already feeds the outer copy)", "tunnel +1, ExecState 1",
         lambda: (g.wire(OP, "SubVI", sub_i(uR), "Image Out", "SubVI", sub_i(uKi), "Image Src", branch=True), snap("after"))[1])
    es = g.exec_state(OP)
    if es != 1 or any(k == "exc" for _n, k in STEPS):
        print(f"\nVERDICT: BROKEN or INCOMPLETE (ExecState {es}, steps {STEPS}) - NOT SAVING.", flush=True); return 4
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump({"labels": {"rows": rows_label, "Image Name": "Image Name", "Image Name B": "Image Name 2", "File Path": "File Path"}}, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("\nVERDICT: HARNESS_copyloop built and saved (structural) - run tools/bench/run_copyloop_bench.py next", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
