"""case_probe.py - can the fleet build the backend-selector VI?  Before assembling TRACK_kernel_v1 (a Case Structure choosing
PARALLEL_kernel_v3 or GPU_kernel_v1), three unknowns are tested on a scratch copy of the kernel:

  1. OpBuildCase_v0 places a Case Structure; how many Diagram objects does the VI then have, and what does its `Frames` control do
     (2 frames wanted: 0 = CPU, 1 = GPU)?
  2. can a subVI be dropped INSIDE a case frame (drop_subvi with that frame's diagram_index)?
  3. does wiring a TOP-LEVEL front-panel control to a node inside the frame work - i.e. does the tunnel get created for us?
     (wire_control's `src_diagram_index` is the control side; the sink is inside the structure.)

Nothing is saved; the scratch VI is deleted.
  py tools/bgrun.py --max-min 15 --log tools/bench/case_probe.log -- py -u tools/bench/case_probe.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SRC = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi"); T = os.path.join(g.CLAUDEDEV, "SCRATCH_case.vi")
OP_CASE = os.path.join(g.CLAUDEDEV, "OpBuildCase_v0.vi"); KERN = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3.vi")
if os.path.exists(T):
    os.remove(T)
shutil.copyfile(SRC, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
while g.count(T, "Node"):
    try:
        g.delete_object(T, "Node", 0)
    except RuntimeError as e:
        if "expected 1 object gone" not in str(e):
            raise
        break
g.remove_bad_wires_scripted(T)
inv0 = g.uids(T, "Invoke")


def purge():
    for o in g.new_since(T, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(T, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(T, "Invoke", ids.index(o["uid"]))


print("stripped: nodes", g.count(T, "Node"), "diagrams", g.count(T, "Diagram"), "ExecState", g.exec_state(T), flush=True)
# 1. place the Case Structure
vi = g.op(OP_CASE)
vi.SetControlValue("vi path", T); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0)
vi.SetControlValue("location (0, 0)", [400, 300])
for lab, val in (("Frames", 2), ("Selector", 0), ("Inputs", [])):
    try:
        vi.SetControlValue(lab, val); print(f"   set {lab} = {val!r}", flush=True)
    except Exception as e:
        print(f"   set {lab}: {str(e)[:110]}", flush=True)
before = g.uids(T, "CaseStructure")
try:
    g._run(vi)
except Exception as e:
    print("case op run:", str(e)[:200], flush=True)
purge()
new = g.new_since(T, "CaseStructure", before)
print("CaseStructure created:", [(o['uid'], o['pos']) for o in new], "| diagrams now", g.count(T, "Diagram"),
      "| ExecState", g.exec_state(T), flush=True)
if not new:
    print("STOP: no case structure", flush=True); sys.exit(3)
# 2. drop a subVI inside each frame (diagram_index 1.. are the frames; 0 is the top level)
for di in (1, 2, 3):
    before_s = g.uids(T, "SubVI")
    try:
        g.drop_subvi(T, KERN, di, (450 + 60 * di, 330))
        made = g.new_since(T, "SubVI", before_s)
        print(f"   drop into diagram {di}: {'OK ' + str([o['uid'] for o in made]) if made else 'no subVI'}", flush=True)
    except Exception as e:
        print(f"   drop into diagram {di}: EXC {str(e)[:140]}", flush=True)
    purge()
print("after drops: SubVIs", g.count(T, "SubVI"), "diagrams", g.count(T, "Diagram"), "ExecState", g.exec_state(T), flush=True)
# 3. wire a top-level control into the node inside the frame
subs = g.report(T, "SubVI")
if subs:
    w0 = g.count(T, "Wire")
    try:
        r = g.wire_control(T, ["x,y,z array"], "SubVI", 0, ["x,y,z array"])
        print(f"   control -> subVI inside the frame: {r} | wires {w0} -> {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
    except Exception as e:
        print(f"   control -> subVI inside the frame: EXC {str(e)[:200]} | wires {w0} -> {g.count(T, 'Wire')}", flush=True)
    g.remove_bad_wires_scripted(T)
    print(f"   after remove_bad_wires: wires {g.count(T, 'Wire')} ExecState {g.exec_state(T)}", flush=True)
try:
    g.close_panel(T); os.remove(T); print("scratch removed", flush=True)
except Exception as e:
    print("cleanup:", str(e)[:80], flush=True)
