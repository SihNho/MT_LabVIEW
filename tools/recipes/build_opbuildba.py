"""build_opbuildba.py - OpBuildBA_v0.vi: place a Build Array primitive (default: ONE input, not concatenating) on a target's
top-level diagram at 'location (0, 0)', using erdosmiller `Create Build Array.vi` (inputs: location, Diagram in, Inputs[],
Concatenate Inputs; output: appended array).  Cloned from OpBuildIA_v0 (build_opbuildia.py): swap the creator, drop the
'array' wire (Build Array has no source input to wire at creation), keep PN VI.Block Diagram -> 'Diagram in' and the
location control.  Needed 2026-09-08 to turn Omars ImageToArray's 2-D U8 image into the 3-D U8 the Saleh CLFN expects.
  py tools/bgrun.py --max-min 10 --log tools/bench/build_opbuildba.log -- py -u tools/recipes/build_opbuildba.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CREATOR = os.path.join(EM, "Create Build Array.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpBuildIA_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpBuildBA_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi"); TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_buildba_target.vi")
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def delete_wires_where(pred, label):
    gone = []
    while True:
        wires = g.report(OP, "Wire"); d = [i for i, o in enumerate(wires) if pred(o)]
        if not d:
            break
        gone.append((wires[d[0]]["uid"], wires[d[0]]["pos"])); g.delete_object(OP, "Wire", d[0])
    print(f"   {label}: deleted {gone}", flush=True); return gone


def main():
    g._lv = None
    for p in (OP, TGT):
        if os.path.exists(p):
            os.remove(p)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")                                       # every ladder op leaves a junk Invoke; purge before ExecState checks

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))
    subs = g.report(OP, "SubVI"); props = g.report(OP, "Property")
    print("baseline SubVIs", [(o["uid"], o["pos"]) for o in subs], "Property", [(o["uid"], o["pos"]) for o in props], "Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    ci = next(i for i, o in enumerate(subs) if o["pos"] == (900, 640))          # the Create Index Array creator (OpBuildIA recipe placed it there); NO net_map here
    cx, cy = subs[ci]["pos"]
    step("1 delete the creator SubVI", "ExecState 0", lambda: (g.delete_object(OP, "SubVI", ci), g.exec_state(OP)))
    step("2 remove its dangling wires", "6 wires", lambda: (g.remove_bad_wires_scripted(OP), g.count(OP, "Wire")))
    sub0 = g.uids(OP, "SubVI")
    step("3 drop Create Build Array.vi", "+1 SubVI", lambda: (g.drop_subvi(OP, CREATOR, 0, (cx, cy)), g.count(OP, "SubVI")))
    subs = g.report(OP, "SubVI"); ni = next((i for i, o in enumerate(subs) if o["uid"] not in sub0), None)
    if ni is None:
        print("STOP: creator not dropped", flush=True); return 3
    pi = [o["uid"] for o in g.report(OP, "Property")].index(min(props, key=lambda o: abs(o["pos"][0] - 700) + abs(o["pos"][1] - 380))["uid"])
    w4 = step("4 PN.Diagram -> creator Diagram in", "Wire +1", lambda: g.wire(OP, "Property", pi, "Diagram", "SubVI", ni, "Diagram in"))
    w5 = step("5 control location -> location (0, 0)", "Wire +1", lambda: g.wire_control(OP, ["location (0, 0)"], "SubVI", ni, ["location (0, 0)"]))
    if w4 is None or w5 is None:
        print("STOP: creator inputs not wired - NOT saving", flush=True); return 5
    n_cre = g.count(OP, "Node") - 1                                   # Nodes[] = creation order; the creator was dropped last (no junk yet)
    for t, want in ((5, "Inputs"),):                                  # t5 = Inputs (required); t6 is the output 'appended array' (probed 2026-09-08)
        w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n_cre, t)
        print(f"   creator t{t}: control {lab!r} wires {w0}->{g.count(OP, 'Wire')}", flush=True)
        if not (new and lab and lab.startswith(want) and g.count(OP, "Wire") > w0):
            print("STOP: unexpected terminal", flush=True); return 5
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "Invokes", g.count(OP, "Invoke"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    print("saved", g.save(OP), flush=True)
    if "--no-test" in sys.argv:
        return 0
    shutil.copyfile(TGT_SRC, TGT); g.report(TGT, "SubVI"); g.open_panel(TGT); time.sleep(0.8)
    before = g.uids(TGT, "Node"); tinv0 = g.uids(TGT, "Invoke")
    vi = g.op(OP); vi.SetControlValue("vi path", TGT); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0); vi.SetControlValue("location (0, 0)", [1300, 700])
    step("6 RUN OpBuildBA_v0 on a scratch target", "+1 non-Invoke Node near (1300,700)",
         lambda: (g._run(vi), [(o["uid"], o["class"], o["pos"]) for o in g.new_since(TGT, "Node", before) if o["uid"] not in {x["uid"] for x in g.new_since(TGT, "Invoke", tinv0)}]))
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
