"""build_opbuildcase_v1c.py - stage 2 of OpBuildCase_v1, on a SCRATCH COPY, copied back only if it ends runnable.

Facts from tools/bench/case_v1_inspect.log (2026-09-10): the reporter's SubVI order is NOT Nodes[] order; by position the
creator (`Create Case Structure.vi`) is the SubVI at (900,640) (SubVI class index 1), the node at (1050,640) is a Clear Errors
sink (wiring to its 'Inputs' gave 5001), Get Controls #1 sits at (790,820). `delete_by_label` needs the connector pane
(5005), so the two refnum controls are removed as ControlTerminal objects found by POSITION and verified by the label set.

Steps: copy -> delete the `Selector`/`Inputs` control terminals (verified via fp_labels) -> remove bad wires -> drop
Get Controls #2 (+ 'Control Names 2' control, Diagram in) -> GC2.'Control Terminals' -> creator.'Inputs' ->
Index Array (OpBuildIA_v0, arrives UNWIRED) <- GC1.'Control Terminals' wired by name into IA.'array' -> IA.element ->
creator.'Selector' -> ExecState 1 -> save scratch -> copy over OpBuildCase_v1.vi.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opbuildcase_v1c.log -- py -u tools/recipes/build_opbuildcase_v1c.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
GETCTL = os.path.join(EM, "Get Controls.vi")
OP = os.path.join(g.CLAUDEDEV, "OpBuildCase_v1.vi"); T = os.path.join(g.CLAUDEDEV, "SCRATCH_case_v1.vi")
OP_IA = os.path.join(g.CLAUDEDEV, "OpBuildIA_v0.vi")
g._run.__defaults__ = (6.0, 60.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); STEPS.append((name, True)); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); STEPS.append((name, False)); return None


def main():
    g._lv = None
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(OP, T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(1.0)
    print("scratch: nodes", g.count(T, "Node"), "wires", g.count(T, "Wire"), "ExecState", g.exec_state(T), flush=True)
    inv0 = g.uids(T, "Invoke")

    def purge():
        for o in g.new_since(T, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(T, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(T, "Invoke", ids.index(o["uid"]))

    def sub_i(uid):
        return [o["uid"] for o in g.report(T, "SubVI")].index(uid)

    def labels():
        return [l for _, l, _ in g.fp_labels(T)]
    subs = g.report(T, "SubVI")
    creator = min(subs, key=lambda o: abs(o["pos"][0] - 900) + abs(o["pos"][1] - 640))
    gc1 = min(subs, key=lambda o: abs(o["pos"][0] - 790) + abs(o["pos"][1] - 820))
    print("creator", creator["uid"], creator["pos"], "| GC1", gc1["uid"], gc1["pos"], flush=True)
    # 1. remove the two refnum controls: ControlTerminals left of the creator, verified by the label set
    want = {"Selector", "Inputs"}
    for target in sorted(want):
        cts = g.report(T, "ControlTerminal")
        cand = sorted([o for o in cts if o["pos"][0] < creator["pos"][0] and abs(o["pos"][1] - creator["pos"][1]) < 140],
                      key=lambda o: abs(o["pos"][0] - creator["pos"][0]))
        done = False
        for o in cand:
            before = set(labels()); cts_now = [x["uid"] for x in g.report(T, "ControlTerminal")]
            if o["uid"] not in cts_now:
                continue
            g.delete_object(T, "ControlTerminal", cts_now.index(o["uid"])); purge()
            gone = before - set(labels())
            print(f"   deleted ControlTerminal {o['uid']} @ {o['pos']} -> labels gone {sorted(gone)}", flush=True)
            if gone == {target}:
                done = True; break
            if gone and gone != {target}:
                print(f"STOP: deleted the wrong control {sorted(gone)} - scratch discarded", flush=True); return 4
        if not done:
            print(f"STOP: could not find the {target!r} terminal by position", flush=True); return 4
    g.remove_bad_wires_scripted(T)
    print("   after removing the refnum controls: wires", g.count(T, "Wire"), "ExecState", g.exec_state(T), "labels", labels(), flush=True)
    # 2. Get Controls #2 for the input tunnels
    def drop(path, pos):
        purge(); before = g.uids(T, "SubVI"); g.drop_subvi(T, path, 0, pos)
        new = [o for o in g.report(T, "SubVI") if o["uid"] not in before]; assert len(new) == 1
        return new[0]["uid"]
    gc2 = step("drop Get Controls #2", "+1 SubVI", lambda: drop(GETCTL, (gc1["pos"][0], gc1["pos"][1] + 160)))
    if gc2 is None:
        return 3
    step("PN.Diagram -> GC2.'Diagram in' (branch)", "accepted",
         lambda: g.wire(T, "Property", 0, "Diagram", "SubVI", sub_i(gc2), "Diagram in", branch=True))
    n_gc2 = g.count(T, "Node") - 1
    lab2 = step("control on GC2.'Control Names'", "label 'Control Names 2'", lambda: _ctl(T, n_gc2, "Control Names", purge))
    step("GC2.'Control Terminals' -> creator.'Inputs'", "+1 wire",
         lambda: g.wire(T, "SubVI", sub_i(gc2), "Control Terminals", "SubVI", sub_i(creator["uid"]), "Inputs"))
    # 3. Index Array on GC1.'Control Terminals' -> creator.'Selector'
    # OpBuildIA_v0 places the Index Array UNWIRED by design (its library `array` input fails with 1304 for every terminal,
    # docs/keystone-op-spec.md §24) - the 2026-09-10 "which source terminal" hunt (6 candidates, all ExecState 0) was chasing
    # an input that was never connected. Wire GC1.'Control Terminals' -> IA.'array' by NAME afterwards, then element -> Selector.
    made = None
    w0 = g.count(T, "Wire")
    ia = step("build Index Array (arrives unwired)", "+1 IndexArray",
              lambda: g.build_index_array(T, (gc1["pos"][0] + 170, gc1["pos"][1] - 70))[0]["uid"])
    purge()
    if ia is not None:
        ia_i = [x["uid"] for x in g.report(T, "IndexArray")].index(ia)
        w1 = step("GC1.'Control Terminals' -> IA.'array'", f"wires {w0} -> {w0 + 1}",
                  lambda: g.wire(T, "SubVI", sub_i(gc1["uid"]), "Control Terminals", "IndexArray", ia_i, "array"))
        w2 = step("IA.'element' -> creator.'Selector'", f"wires -> {w0 + 2}",
                  lambda: g.wire(T, "IndexArray", ia_i, "element", "SubVI", sub_i(creator["uid"]), "Selector"))
        g.remove_bad_wires_scripted(T)
        es_ia = g.exec_state(T); wn = g.count(T, "Wire")
        print(f"   after IA wiring: wires {wn} (expected {w0 + 2}), ExecState {es_ia}", flush=True)
        if es_ia == 1 and wn == w0 + 2:
            made = ("Control Terminals", ia)
        else:
            print("   DIAG: IA wiring did not yield a runnable VI - scratch will be discarded", flush=True)
    purge(); g.remove_bad_wires_scripted(T); es = g.exec_state(T)
    print("\nassembled: nodes", g.count(T, "Node"), "wires", g.count(T, "Wire"), "ExecState", es, "\nlabels:", labels(),
          "\nIndex Array:", made, "\nsteps failed:", [n for n, ok in STEPS if not ok], flush=True)
    if es != 1 or made is None or not lab2:
        print("STOP: scratch discarded, OpBuildCase_v1 unchanged", flush=True); return 5
    print("saved scratch", g.save(T), flush=True)
    g.close_panel(T); time.sleep(0.5)
    shutil.copyfile(T, OP); os.remove(T)
    print("OpBuildCase_v1.vi updated from the scratch (", os.path.getsize(OP), "bytes )", flush=True)
    return 0


def _ctl(T, n, wanted, purge, max_terms=14):
    for t in range(max_terms):
        w0 = g.count(T, "Wire"); new, lab = g.create_control(T, n, t); purge()
        if new and lab and lab.lower().startswith(wanted.lower()) and g.count(T, "Wire") > w0:
            return lab
        if new:
            ct = [o["uid"] for o in g.report(T, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(T, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(T, "ControlTerminal")]
            g.remove_bad_wires_scripted(T)
    return None


if __name__ == "__main__":
    sys.exit(main())
