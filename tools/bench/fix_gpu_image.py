"""fix_gpu_image.py - HARNESS_gpu.vi: the Saleh CLFN's 'Array of Images' is a 3-D U8 array, so ImageToArray's 2-D output was
dropped as a bad wire at build time (t24 unwired -> image 0x0).  Place a 1-input Build Array (OpBuildBA_v0) and wire by NAME
(no net_map: its per-terminal calls leave hundreds of junk Invokes): I2A 'Image Pixels (U8)' -> BA input, BA 'appended array'
-> CLFN 'Array of Images'.  Purge the few junk Invokes, Remove Bad Wires, verify the wire count held, save."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "HARNESS_gpu.vi"); OP_BA = os.path.join(g.CLAUDEDEV, "OpBuildBA_v0.vi")
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
print("ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), "Invokes", g.count(OP, "Invoke"), flush=True)
inv0 = g.uids(OP, "Invoke"); before = g.uids(OP, "Node")
subs = g.report(OP, "SubVI"); i_i2a = next(i for i, o in enumerate(subs) if o["pos"][0] >= 480)      # Omars ImageToArray, dropped at (500, 300)
vi = g.op(OP_BA); vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", [640, 300])
g._run(vi)
junk = {o["uid"] for o in g.new_since(OP, "Invoke", inv0)}
new = [o for o in g.new_since(OP, "Node", before) if o["uid"] not in junk]; print("new nodes:", [(o["uid"], o["class"], o["pos"]) for o in new], flush=True)
if len(new) != 1:
    print("STOP: Build Array not placed", flush=True); sys.exit(2)
ba_uid, ba_cls = new[0]["uid"], new[0]["class"]; i_ba = [o["uid"] for o in g.report(OP, ba_cls)].index(ba_uid)
w0 = g.count(OP, "Wire"); done = None
for term in ("element", "array", "element 0", "array 0"):
    try:
        r = g.wire(OP, "SubVI", i_i2a, "Image Pixels (U8)", ba_cls, i_ba, term); done = term; print(f"I2A.Image Pixels (U8) -> BA.{term!r}: {r}", flush=True); break
    except Exception as e:
        print(f"   BA input {term!r}: {str(e)[:100]}", flush=True)
if done is None:
    print("STOP: Build Array input name unknown", flush=True); sys.exit(3)
print("BA.appended array -> CLFN.Array of Images:", g.wire(OP, ba_cls, i_ba, "appended array", "CallLibrary", 0, "Array of Images"), flush=True)
w1 = g.count(OP, "Wire")
for o in g.new_since(OP, "Invoke", inv0):
    ids = [x["uid"] for x in g.report(OP, "Invoke")]
    if o["uid"] in ids:
        g.delete_object(OP, "Invoke", ids.index(o["uid"]))
g.remove_bad_wires_scripted(OP); es = g.exec_state(OP); w2 = g.count(OP, "Wire")
print("wires", w0, "->", w1, "-> after RBW", w2, "| ExecState", es, "Invokes", g.count(OP, "Invoke"), flush=True)
if es != 1 or w2 != w1 or w1 != w0 + 2:
    print("STOP: image wires rejected - NOT saving", flush=True); sys.exit(4)
print("saved", g.save(OP), flush=True)
