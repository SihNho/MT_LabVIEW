"""build_opclfnpre.py - OpCLFNPre_v0.vi: sets the import wizard's FUNCTIONAL GLOBALS that NI's Call Library Node\\Method\\Create.vi
consumes (it applies them to the node it creates; with them empty its internal Function Name set fails, error 1077, 2026-09-09):
  VI\\Block Diagram\\Attribute\\{Function Name, Path, Calling Convention, Reentrant, Parameter Info}.vi  (operation ring + value)
  Call Library Node\\Attribute\\Function Dec.vi  (operation + String)
The op is a flat VI: one SubVI per FGV, every input terminal given a front-panel control (label probe), no wiring between
them (FGVs, no error terminals).  It must be RUN in the same LabVIEW session, in the same Python process (g.op keeps it
loaded) right before OpCLFNBuild_v0, so the globals still hold the values when Create.vi reads them.
  py tools/bgrun.py --max-min 12 --log tools/bench/build_opclfnpre.log -- py -u tools/recipes/build_opclfnpre.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

BD = r"C:\Program Files\National Instruments\LabVIEW 2026\resource\importtools\sharedlib\VI\Block Diagram"
FGVS = [os.path.join(BD, "Attribute", n + ".vi") for n in ("Function Name", "Path", "Calling Convention", "Reentrant", "Parameter Info")] + \
       [os.path.join(BD, "Call Library Node", "Attribute", "Function Dec.vi")]
SRC = os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpCLFNPre_v0.vi")
g._run.__defaults__ = (6.0, 45.0)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))
    # clear FPTARGET's own nodes so Nodes[] starts empty (creation order = our drops)
    while g.count(OP, "Node"):
        try:
            g.delete_object(OP, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(OP)
    while g.count(OP, "ControlTerminal"):
        g.delete_object(OP, "ControlTerminal", 0)
    g.remove_bad_wires_scripted(OP)
    print("base cleared: nodes", g.count(OP, "Node"), "ExecState", g.exec_state(OP), flush=True)
    table = {}
    for k, path in enumerate(FGVS):
        purge(); before = g.uids(OP, "SubVI"); g.drop_subvi(OP, path, 0, (200 + 220 * k, 300))
        new = [o for o in g.report(OP, "SubVI") if o["uid"] not in before]; assert len(new) == 1, path
        n = g.count(OP, "Node") - 1; labs = []
        for t in range(0, 16):                                          # Terminals[] = ALL connector-pane slots (empty ones too): the 3 real ones can sit at 8..11
            w0 = g.count(OP, "Wire"); created, lab = g.create_control(OP, n, t)
            if created and lab and g.count(OP, "Wire") > w0:
                labs.append(lab); continue
            if created:
                ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
                for o in created:
                    if o["uid"] in ct:
                        g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
                g.remove_bad_wires_scripted(OP)
        table[os.path.basename(path)] = labs; print(f"  {os.path.basename(path)}: controls {labs}", flush=True)
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("assembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es, "TABLE", table, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    print("saved", g.save(OP), flush=True)
    import json; json.dump(table, open(os.path.join(os.path.dirname(HERE), "bench", "opclfnpre_labels.json"), "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
