"""extract_clfn3.py - GPU_kernel_base.vi via move_out + copy_into (mass deletion inside the donor copy hung LabVIEW):
  1. donor copy GPU_donor_moved.vi: move_out(diagram 4, node 0 -> top level), Remove Bad Wires, label the CLFN, save
  2. copy_into(GPU_donor_moved.vi, "CLFN_DONOR", GPU_kernel_base.vi)  (Simple Move example: top-level label search)
  3. on GPU_kernel_base: controls on every input terminal, indicators on the outputs -> runnable -> save; terminal table.
  py tools/bgrun.py --max-min 25 --log tools/bench/extract_clfn2.log -- py -u tools/bench/extract_clfn3.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\GPU Track Algo (Saleh Lab)\GPU Tracking Demo_Fixed discretization error in lateral tracking\GPU Tracking\TrackBatchOfImagesWithGPU.vi"
MOVED = os.path.join(g.CLAUDEDEV, "GPU_donor_moved.vi"); DST = os.path.join(g.CLAUDEDEV, "GPU_kernel_base.vi")
OUT = os.path.join(HERE, "gpu_kernel_base_terminals.json")


def prepare(src):
    g.report(src, "SubVI"); g.open_panel(src); time.sleep(1.0)
    clfn = g.report(src, "CallLibrary")[0]["uid"]; print("prepare: CLFN uid", clfn, flush=True)
    print("prepare: move_out ->", g.move_out(src, 4, 0, (300, 300)), flush=True)
    g.remove_bad_wires_scripted(src)
    top, _ = g.net_map(src, 0, max_nodes=3, max_terms=2); n = [v[0] for v in top.values()].index(clfn)
    print("prepare: set_node_label ->", g.set_node_label(src, 0, n, "CLFN_DONOR"), "ExecState", g.exec_state(src), flush=True)


def main():
    if os.path.exists(DST):
        os.remove(DST)
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), DST)
    added = g.copy_into(SRC, "CLFN_DONOR", DST, prepare=prepare); print("copy_into added:", added, flush=True)
    g.report(DST, "SubVI"); g.open_panel(DST); time.sleep(1.0)
    print("target CallLibrary:", g.report(DST, "CallLibrary"), "nodes", g.count(DST, "Node"), flush=True)
    # wipe the base's own nodes (FPTARGET has a few) except the CLFN, then terminals
    cl = g.report(DST, "CallLibrary")[0]["uid"]
    while True:
        objs = g.report(DST, "Node"); others = [i for i, o in enumerate(objs) if o["uid"] != cl]
        if not others:
            break
        try:
            g.delete_object(DST, "Node", others[0])
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
    g.remove_bad_wires_scripted(DST)
    while g.count(DST, "ControlTerminal"):
        g.delete_object(DST, "ControlTerminal", 0)
    g.remove_bad_wires_scripted(DST)
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
