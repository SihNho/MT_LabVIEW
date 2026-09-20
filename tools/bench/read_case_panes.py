"""read_case_panes.py - the exact connector-pane names of the erdosmiller case VIs, needed to build OpBuildCase_v1
(which must supply `Selector` / `Inputs` as refnums obtained INSIDE the op from control NAMES, the OpWireCtl pattern).

Drops each VI on a scratch diagram and probes its terminals with create_control / create_indicator, printing the auto-labels
(= terminal names).  Nothing is saved.
  py tools/bgrun.py --max-min 20 --log tools/bench/read_case_panes.log -- py -u tools/bench/read_case_panes.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
VIS = [os.path.join(EM, n) for n in ("Create Case Structure.vi", "Case Next Frame.vi",
                                     "Exit Multi Frame Structure.vi", "Exit Structure.vi")]
T = os.path.join(g.CLAUDEDEV, "SCRATCH_panes.vi")
if os.path.exists(T):
    os.remove(T)
shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
while g.count(T, "Node"):
    try:
        g.delete_object(T, "Node", 0)
    except RuntimeError as e:
        if "expected 1 object gone" not in str(e):
            raise
        break
g.remove_bad_wires_scripted(T)
while g.count(T, "ControlTerminal"):
    g.delete_object(T, "ControlTerminal", 0)
g.remove_bad_wires_scripted(T)
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


for k, path in enumerate(VIS):
    if not os.path.exists(path):
        print(f"\n== {os.path.basename(path)}: NOT FOUND", flush=True); continue
    purge(); g.drop_subvi(T, path, 0, (200 + 300 * k, 300)); purge()
    n = g.count(T, "Node") - 1
    print(f"\n== {os.path.basename(path)} (Nodes[{n}])", flush=True)
    for t in range(0, 16):
        w0 = g.count(T, "Wire"); new, lab = g.create_control(T, n, t); purge()
        if new and lab and g.count(T, "Wire") > w0:
            print(f"   t{t:2d} IN  {lab!r}", flush=True); del_terms(new); continue
        if new:
            del_terms(new)
        fp0 = {l for _, l, _ in g.fp_labels(T)}; w0 = g.count(T, "Wire")
        new = g.create_indicator(T, n, t); purge(); labs = [l for _, l, _ in g.fp_labels(T) if l not in fp0]
        if new and labs and g.count(T, "Wire") > w0:
            print(f"   t{t:2d} OUT {labs[-1]!r}", flush=True); del_terms(new); continue
        if new:
            del_terms(new)
try:
    g.close_panel(T); os.remove(T); print("\nscratch removed", flush=True)
except Exception as e:
    print("cleanup:", str(e)[:80], flush=True)
