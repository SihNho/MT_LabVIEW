"""patch_opbuildcase.py - OpBuildCase_v0 pops an error dialog on every run: erdosmiller `Create Case Structure.vi` always tries
to Connect Wire the `Selector` terminal, and with no valid terminal refnum (COM cannot supply one) that returns error 1055.
The Case Structure itself IS created first, so the only problem is the UNWIRED `error out`, which LabVIEW's automatic error
handling turns into a modal dialog that blocks the run.

Fix (the fleet's standard error-visibility topology): put an INDICATOR on the creator's `error out`, so the error is consumed
and readable instead of thrown at the screen.  Then the op is usable for the backend-selector VI.
  py tools/bgrun.py --max-min 15 --log tools/bench/patch_opbuildcase.log -- py -u tools/recipes/patch_opbuildcase.py
"""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpBuildCase_v0.vi")
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
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

    existing = {l for _, l, _ in g.fp_labels(OP)}
    if any(l.lower().startswith("error out") for l in existing):
        print("already has an error-out indicator:", [l for l in existing if l.lower().startswith("error out")], flush=True)
    done = None
    for n in range(g.count(OP, "Node") - 1, -1, -1):                        # the creator was dropped last
        for t in range(0, 14):
            fp0 = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
            new = g.create_indicator(OP, n, t); purge()
            labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
            if new and labs and g.count(OP, "Wire") > w0 and labs[-1].lower().startswith("error out"):
                done = (n, t, labs[-1]); print(f"   indicator {labs[-1]!r} on Nodes[{n}] t{t} (wires {w0} -> {g.count(OP, 'Wire')})", flush=True)
                break
            if new:
                del_terms(new)
        if done:
            break
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("patched:", done, "| wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if not done or es != 1:
        print("STOP: not saving", flush=True); return 4
    print("saved", g.save(OP), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
