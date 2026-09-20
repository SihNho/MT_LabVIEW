"""case_v1_inspect.py - identify the nodes of OpBuildCase_v1 before finishing it.

Stage 2 failed three ways and each needs a fact:
  * `delete_by_label` needs the label on the CONNECTOR PANE (error 5005) -> the refnum controls must be removed by deleting the
    ControlTerminal object (or better: delete their WIRE and leave the control)
  * wiring to the creator's `Inputs` gave 5001 (name not found) -> the node picked as "the creator" (rightmost SubVI) is
    probably the wrong one
  * `report("Terminal")["owner"]` is not the node uid -> the Index Array source terminal must be found another way

This prints, for every SubVI on the diagram, the terminal NAMES that create_control reports (probe controls are deleted again),
so the creator (the node owning `Selector` / `Inputs` / `Frames`) is identified beyond doubt.  Read-only apart from the probes.
  py tools/bgrun.py --max-min 20 --log tools/bench/case_v1_inspect.log -- py -u tools/bench/case_v1_inspect.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
OP = os.path.join(g.CLAUDEDEV, "OpBuildCase_v1.vi")
g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
print("op: nodes", g.count(OP, "Node"), "SubVIs", g.count(OP, "SubVI"), "wires", g.count(OP, "Wire"),
      "ExecState", g.exec_state(OP), flush=True)
inv0 = g.uids(OP, "Invoke")


def purge():
    for o in g.new_since(OP, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(OP, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(OP, "Invoke", ids.index(o["uid"]))


def del_terms(new):
    ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
    for o in new:
        if o["uid"] in ct:
            g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
    g.remove_bad_wires_scripted(OP)


subs = g.report(OP, "SubVI")
print("SubVIs (class index, uid, pos):", [(i, o["uid"], o["pos"]) for i, o in enumerate(subs)], flush=True)
nodes = g.report(OP, "Node")
print("Nodes (uid, class, pos):", [(o["uid"], o["class"], o["pos"]) for o in nodes], flush=True)
# terminal names per node, by Nodes[] index (create_control's index space)
for n in range(len(nodes)):
    names = []
    for t in range(0, 12):
        w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t); purge()
        if new and lab and g.count(OP, "Wire") > w0:
            names.append((t, lab)); del_terms(new)
        elif new:
            del_terms(new)
    print(f"  Nodes[{n}] uid {nodes[n]['uid']} {nodes[n]['class']} @ {nodes[n]['pos']}: unwired inputs {names}", flush=True)
print("\nfp:", [l for _, l, _ in g.fp_labels(OP)], flush=True)
print("final ExecState", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
