"""extract_clfn.py - GPU_kernel_base.vi: the Saleh-lab Call Library Function Node alone, at top level, with a control on
every input terminal and an indicator on every output terminal (so the VI is runnable and COM-saveable).
Steps: copy the donor VI -> move the CLFN out of its loop (OpMoveOut_v0) -> delete every other node and every front-panel
object -> Remove Bad Wires -> create controls/indicators on the CLFN terminals -> save -> print the terminal table.
  py tools/bgrun.py --max-min 20 --log tools/bench/extract_clfn.log -- py -u tools/bench/extract_clfn.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\GPU Track Algo (Saleh Lab)\GPU Tracking Demo_Fixed discretization error in lateral tracking\GPU Tracking\TrackBatchOfImagesWithGPU.vi"
DST = os.path.join(g.CLAUDEDEV, "GPU_kernel_base.vi")
OUT = os.path.join(HERE, "gpu_kernel_base_terminals.json")


def main():
    if os.path.exists(DST):
        os.remove(DST)
    shutil.copyfile(SRC, DST); g.report(DST, "SubVI"); g.open_panel(DST); time.sleep(1.0)
    clfn = g.report(DST, "CallLibrary")[0]["uid"]; print("CLFN uid", clfn, "ExecState", g.exec_state(DST), flush=True)
    # locate: Traverse Diagram index 4, Nodes[0] (v3_structure-style read, 2026-09-08 05:47)
    nodes, _ = g.net_map(DST, 4, max_nodes=3, max_terms=2)
    assert nodes[0][0] == clfn, nodes
    print("move_out ->", g.move_out(DST, 4, 0, (300, 300)), flush=True)
    top, _ = g.net_map(DST, 0, max_nodes=40, max_terms=2)
    print("top-level node uids after move:", [v[0] for v in top.values()], flush=True)
    assert clfn in [v[0] for v in top.values()], "CLFN not at top level after move"
    g.remove_bad_wires_scripted(DST)
    # delete everything else
    while True:
        objs = g.report(DST, "Node"); others = [i for i, o in enumerate(objs) if o["uid"] != clfn]
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
    print("stripped: nodes", g.count(DST, "Node"), "controls", g.count(DST, "ControlTerminal"), "wires", g.count(DST, "Wire"), "CallLibrary", len(g.report(DST, "CallLibrary")), flush=True)
    # terminals (the CLFN is now Nodes[0] of the top level; net_map would add a junk Invoke - use it once, then purge)
    inv0 = g.uids(DST, "Invoke")
    nodes, _ = g.net_map(DST, 0, max_nodes=2, max_terms=48)
    terms = [(t, nm) for t, nm, w in nodes[0][2]]
    print("CLFN terminals:", terms, flush=True)
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
        if new:                                                    # unwired control = output terminal: remove, make an indicator
            ct = [o["uid"] for o in g.report(DST, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(DST, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(DST, "ControlTerminal")]
            g.remove_bad_wires_scripted(DST); fp0 = {l for _, l, _ in g.fp_labels(DST)}
        new = g.create_indicator(DST, 0, t); labs = [l for _, l, _ in g.fp_labels(DST) if l not in fp0]
        if new and labs:
            table[t] = {"name": nm, "kind": "IND", "label": labs[-1]}; print(f"  t{t} {nm!r}: indicator {labs[-1]!r}", flush=True)
        else:
            table[t] = {"name": nm, "kind": "none", "label": None}; print(f"  t{t} {nm!r}: nothing created", flush=True)
    es = g.exec_state(DST); print("ExecState", es, "wires", g.count(DST, "Wire"), flush=True)
    if es != 1:
        g.remove_bad_wires_scripted(DST); es = g.exec_state(DST); print("after Remove Bad Wires: ExecState", es, flush=True)
    json.dump(table, open(OUT, "w", encoding="utf-8"), indent=1)
    if es == 1:
        print("saved", g.save(DST), flush=True); return 0
    print("STOP: still broken - not saved (table written)", flush=True); return 2


if __name__ == "__main__":
    sys.exit(main())
