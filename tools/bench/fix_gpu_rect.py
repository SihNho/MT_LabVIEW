"""fix_gpu_rect.py - HARNESS_gpu.vi: create a control on Omars IMAQ ImageToArray's 'Optional Rectangle' terminal (its default
rectangle yields an EMPTY pixel array - the DLL saw image 0x0), save, record the label in harness_gpu_labels.json."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi"); LABELS = os.path.join(HERE, "harness_gpu_labels.json")
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
print("ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
subs = g.report(OP, "SubVI"); print("SubVIs:", [(o["uid"], o["pos"]) for o in subs], flush=True)
inv0 = g.uids(OP, "Invoke")
nodes, _ = g.net_map(OP, 0, max_nodes=8, max_terms=4)
order = [(n, uid) for n, (uid, _, _) in nodes.items()]; print("Nodes[]:", order, flush=True)
i2a_uid = [o["uid"] for o in subs if o["pos"][0] >= 480][0]                    # dropped at (500, 300) by build_harness_gpu
n_i2a = [n for n, uid in order if uid == i2a_uid][0]; print("I2A node index", n_i2a, "uid", i2a_uid, flush=True)
label = None
for t in range(0, 10):
    fp0 = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
    new, lab = g.create_control(OP, n_i2a, t)
    print(f"  t{t}: new {[(o['uid'], o['pos']) for o in new]} label {lab!r} wires {w0}->{g.count(OP, 'Wire')}", flush=True)
    if new and lab and "rectangle" in lab.lower() and g.count(OP, "Wire") > w0:
        label = lab; break
    if new:
        ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
        g.remove_bad_wires_scripted(OP)
for o in g.new_since(OP, "Invoke", inv0):
    ids = [x["uid"] for x in g.report(OP, "Invoke")]
    if o["uid"] in ids:
        g.delete_object(OP, "Invoke", ids.index(o["uid"]))
g.remove_bad_wires_scripted(OP)
es = g.exec_state(OP); print("ExecState", es, "wires", g.count(OP, "Wire"), "rect control", label, flush=True)
if es != 1 or not label:
    print("STOP: not saving", flush=True); sys.exit(3)
print("saved", g.save(OP), flush=True)
lab = json.load(open(LABELS)); lab["controls"]["Optional Rectangle"] = label; json.dump(lab, open(LABELS, "w"), indent=1); print("labels updated", flush=True)
