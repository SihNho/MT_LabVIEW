"""extract_clfn4.py - GPU_kernel_base.vi via move_out + deletion of the donor's structures FIRST (each delete recompiles the big VI: ~25 s; the 1000 s run was cut mid-way, not hung):
  1. donor copy GPU_donor_moved.vi: move_out(diagram 4, node 0 -> top level), Remove Bad Wires, label the CLFN, save
  2. copy_into(GPU_donor_moved.vi, "CLFN_DONOR", GPU_kernel_base.vi)  (Simple Move example: top-level label search)
  3. on GPU_kernel_base: controls on every input terminal, indicators on the outputs -> runnable -> save; terminal table.
  py tools/bgrun.py --max-min 25 --log tools/bench/extract_clfn2.log -- py -u tools/bench/extract_clfn4.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\GPU Track Algo (Saleh Lab)\GPU Tracking Demo_Fixed discretization error in lateral tracking\GPU Tracking\TrackBatchOfImagesWithGPU.vi"
MOVED = os.path.join(g.CLAUDEDEV, "GPU_donor_moved.vi"); DST = os.path.join(g.CLAUDEDEV, "GPU_kernel_base.vi")
OUT = os.path.join(HERE, "gpu_kernel_base_terminals.json")


def timed_delete(target, cls, index, what):
    t0 = time.time()
    try:
        g.delete_object(target, cls, index)
    except RuntimeError as e:
        if "expected 1 object gone" not in str(e):
            raise
    print(f"  deleted {what} ({time.time() - t0:.0f}s)", flush=True)


def main():
    for p in (MOVED, DST):
        if os.path.exists(p):
            os.remove(p)
    shutil.copyfile(SRC, DST); g.report(DST, "SubVI"); g.open_panel(DST); time.sleep(1.0)
    clfn = g.report(DST, "CallLibrary")[0]["uid"]; print("CLFN uid", clfn, "ExecState", g.exec_state(DST), flush=True)
    print("move_out ->", g.move_out(DST, 4, 0, (300, 300)), flush=True)
    g.remove_bad_wires_scripted(DST)
    # structures first (each takes its contents along)
    while True:
        st = g.report(DST, "Structure")
        if not st:
            break
        timed_delete(DST, "Structure", 0, f"Structure uid {st[0]['uid']} ({len(st)} left)")
    g.remove_bad_wires_scripted(DST)
    while True:
        objs = g.report(DST, "Node"); others = [i for i, o in enumerate(objs) if o["uid"] != clfn]
        if not others:
            break
        timed_delete(DST, "Node", others[0], f"Node uid {objs[others[0]]['uid']} ({len(others)} left)")
    g.remove_bad_wires_scripted(DST)
    while g.count(DST, "ControlTerminal"):
        timed_delete(DST, "ControlTerminal", 0, "ControlTerminal")
    g.remove_bad_wires_scripted(DST)
    cl = clfn
    print("stripped: nodes", g.count(DST, "Node"), "controls", g.count(DST, "ControlTerminal"), "wires", g.count(DST, "Wire"), "ExecState", g.exec_state(DST), flush=True)
    inv0 = g.uids(DST, "Invoke")
    nodes, _ = g.net_map(DST, 0, max_nodes=2, max_terms=48)
    terms = [(t, nm) for t, nm, w in nodes[0][2]]; print("CLFN terminals:", terms, flush=True)
    for o in g.new_since(DST, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(DST, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(DST, "Invoke", ids.index(o["uid"]))
    g.remove_bad_wires_scripted(DST)
    table = {}
    for t, nm in terms:
        fp0 = {l for _, l, _ in g.fp_labels(DST)}; w0 = g.count(DST, "Wire")
        new, label = g.create_control(DST, 0, t)
        if new and label and g.count(DST, "Wire") > w0:
            table[t] = {"name": nm, "kind": "CTRL", "label": label}; print(f"  t{t} {nm!r}: control {label!r}", flush=True); continue
        if new:
            ct = [o["uid"] for o in g.report(DST, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(DST, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(DST, "ControlTerminal")]
            g.remove_bad_wires_scripted(DST); fp0 = {l for _, l, _ in g.fp_labels(DST)}
        new = g.create_indicator(DST, 0, t); labs = [l for _, l, _ in g.fp_labels(DST) if l not in fp0]
        if new and labs:
            table[t] = {"name": nm, "kind": "IND", "label": labs[-1]}; print(f"  t{t} {nm!r}: indicator {labs[-1]!r}", flush=True)
        else:
            table[t] = {"name": nm, "kind": "none", "label": None}; print(f"  t{t} {nm!r}: nothing", flush=True)
    es = g.exec_state(DST); print("ExecState", es, "wires", g.count(DST, "Wire"), flush=True)
    json.dump(table, open(OUT, "w", encoding="utf-8"), indent=1)
    if es != 1:
        g.remove_bad_wires_scripted(DST); es = g.exec_state(DST); print("after Remove Bad Wires: ExecState", es, flush=True)
    if es == 1:
        print("saved", g.save(DST), flush=True); return 0
    print("STOP: broken - not saved", flush=True); return 3


if __name__ == "__main__":
    sys.exit(main())
