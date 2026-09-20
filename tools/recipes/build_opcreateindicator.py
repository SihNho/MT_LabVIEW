"""build_opcreateindicator.py — OpCreateIndicator_v0.vi: create a front-panel INDICATOR wired to terminal t of
Nodes[n] on a target (Terminal.Create Indicator, 6349C02). Same ladder as OpCreateControl_v0; only the
Invoke differs. Zero GUI (spec §26).

Run through the deadline runner:
  py tools/bgrun.py --max-min 6 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_opcreateindicator.py [--no-test]

Steps:
  1. copy OpCreateControl_v0 -> OpCreateIndicator_v0; delete its Invoke + the 2 wires (x>=620, y>=440) -> ExecState 1
  2. build_invoke Terminal.Create Indicator (6349C02) at (700,450); wire IA327.element -> reference;
     error out -> Clear Errors 369 -> ExecState 1 -> COM save
  3. test on a scratch copy of GUIBENCH_v0: node 1 (Traverse 124), terminal t swept 0..7: report which t give a
     new ControlTerminal (output terminals) — contract: at least one.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpCreateControl_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpCreateIndicator_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_ci_target.vi")
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def main():
    g._lv = None
    for p in (OP, TGT):
        if os.path.exists(p):
            try:
                g.close_panel(p)
            except Exception:
                pass
    shutil.copyfile(SRC, OP)
    g.open_panel(OP); time.sleep(1.0)

    def strip():
        g.delete_object(OP, "Invoke", 0)
        while True:
            ws = g.report(OP, "Wire")
            d = [i for i, o in enumerate(ws) if o["pos"][0] >= 620 and o["pos"][1] >= 440]
            if not d:
                break
            g.delete_object(OP, "Wire", d[0])
        return g.count(OP, "Wire"), g.exec_state(OP)
    step("1 strip the Create Control invoke", "Wires 8, ExecState 1", strip)
    if g.exec_state(OP) != 1:
        print("STOP: broken after strip", flush=True); return 1
    inv = step("2 build_invoke Terminal.Create Indicator", "+1 Invoke", lambda: g.build_invoke(OP, "VI Server:Terminal", "6349C02", (700, 450)))
    if not inv:
        return 2
    ui = inv[0]["uid"]
    step("2a IA327.element -> reference", "Wire +1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", 327), "element", "Invoke", idx("Invoke", ui), "reference"))
    step("2b error out -> Clear Errors 369", "Wire +1", lambda: g.wire(OP, "Invoke", idx("Invoke", ui), "error out", "SubVI", idx("SubVI", 369), "error in (no error)"))
    es = g.exec_state(OP)
    print("assembled Wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 3
    step("2c COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    hits = []
    for t in range(8):
        before = g.uids(TGT, "ControlTerminal")
        vi.SetControlValue("index", 1); vi.SetControlValue("index 2", t)
        t0 = time.time()
        try:
            g._run(vi)
        except Exception as e:
            print(f"   t={t}: run {str(e)[:60]}", flush=True)
        new = g.new_since(TGT, "ControlTerminal", before)
        print(f"   t={t}: {time.time() - t0:.2f}s new {[(o['uid'], o['pos']) for o in new]}", flush=True)
        if new:
            hits.append((t, new[0]["pos"]))
    print("HITS (Traverse 124 output terminals)", hits, "target ExecState", g.exec_state(TGT), flush=True)
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
