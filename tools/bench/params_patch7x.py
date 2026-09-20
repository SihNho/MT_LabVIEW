"""params_patch7x.py - OpCLFNParams_v0: the Flatten node's `type string (7.x only)` output is populated only when its
`convert 7.x data` input is TRUE -> add a boolean control on that input, save, run with it TRUE and print the 7.x type
descriptor (I16[] -> JSON tools/bench/paraminfo_td.json) plus the data string of the EMPTY global.  Same LabVIEW, one client."""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 45.0)
OP = os.path.join(g.CLAUDEDEV, "OpCLFNParams_v0.vi")
labs = json.load(open(os.path.join(HERE, "opclfnparams_labels.json")))
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(0.8)
inv0 = g.uids(OP, "Invoke")


def purge():
    for o in g.new_since(OP, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(OP, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(OP, "Invoke", ids.index(o["uid"]))


fl = g.report(OP, "FlattenString"); assert len(fl) == 1, fl
nodes = [o["uid"] for o in g.report(OP, "Node")]; n = nodes.index(fl[0]["uid"])
print("Flatten node index", n, "of", len(nodes), flush=True)
ctl = None
for t in range(12):
    w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
    print(f"  t{t}: {lab!r} new={len(new) if new else 0} wire+{g.count(OP, 'Wire') - w0}", flush=True)
    if new and lab and "convert" in lab.lower() and g.count(OP, "Wire") > w0:
        ctl = lab; break
    if new:
        ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
        for o in new:
            if o["uid"] in ct:
                g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
        g.remove_bad_wires_scripted(OP)
purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
print("control", ctl, "ExecState", es, flush=True)
if not ctl or es != 1:
    print("STOP: not saved", flush=True); sys.exit(6)
print("saved", g.save(OP), flush=True)
labs["convert"] = ctl; json.dump(labs, open(os.path.join(HERE, "opclfnparams_labels.json"), "w"), indent=1)
vi = g.op(OP); vi.SetControlValue(labs["binary string"], ""); vi.SetControlValue(labs["operation"], 0); vi.SetControlValue(ctl, True)
try:
    g._run(vi)
except Exception as e:
    print("run:", str(e)[:200], flush=True)
td = vi.GetControlValue(labs["type string"]); ds = vi.GetControlValue(labs["data string"]); err = vi.GetControlValue(labs["error out"])
td = list(td) if td is not None else []
print("error out", err, "\ndata string", ds.encode("latin-1").hex() if isinstance(ds, str) else ds, "\ntype string I16 x", len(td), td[:80], flush=True)
json.dump(td, open(os.path.join(HERE, "paraminfo_td.json"), "w"))
print("td saved", flush=True)
