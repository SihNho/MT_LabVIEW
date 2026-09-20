import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 45.0)
OP = os.path.join(g.CLAUDEDEV, "OpBuildBA_v0.vi"); TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi"); TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_buildba_target.vi")
n0 = g.count(OP, "Invoke"); t0 = time.time()
while g.count(OP, "Invoke"):
    g.delete_object(OP, "Invoke", 0)
print(f"deleted {n0} Invokes in {time.time() - t0:.0f} s; Node {g.count(OP, 'Node')} Wire {g.count(OP, 'Wire')} ExecState {g.exec_state(OP)}", flush=True)
g.remove_bad_wires_scripted(OP); es = g.exec_state(OP); print("after RBW: Wire", g.count(OP, "Wire"), "ExecState", es, flush=True)
if es != 1:
    print("STOP: still broken", flush=True); sys.exit(3)
print("saved", g.save(OP), flush=True)
if os.path.exists(TGT):
    os.remove(TGT)
shutil.copyfile(TGT_SRC, TGT); g.report(TGT, "SubVI"); g.open_panel(TGT); time.sleep(0.8)
before = g.uids(TGT, "Node"); inv0 = g.uids(TGT, "Invoke")
vi = g.op(OP); vi.SetControlValue("vi path", TGT); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", [1300, 700])
g._run(vi)
new = [o for o in g.new_since(TGT, "Node", before) if o["uid"] not in {x["uid"] for x in g.new_since(TGT, "Invoke", inv0)}]
print("new non-Invoke nodes on scratch:", [(o["uid"], o["class"], o["pos"]) for o in new], "| junk Invokes added:", len(g.new_since(TGT, "Invoke", inv0)), flush=True)
if new:
    nodes, _ = g.net_map(TGT, 0, max_nodes=80, max_terms=6)
    for n, (uid, _, terms) in nodes.items():
        if uid == new[0]["uid"]:
            print("Build Array terminals:", terms, flush=True)
try:
    g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
except Exception as e:
    print("scratch cleanup:", str(e)[:80], flush=True)
