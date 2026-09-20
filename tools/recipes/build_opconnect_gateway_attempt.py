"""build_opconnect.py — OpConnect_v0.vi: wire any two terminals of a target VI by Traverse index
(erdosmiller `Conditionally Connect Wire.vi`: `Terminal in` = sink, `Wire Source` = source, both plain
refnums fed from Traverse("Terminal") chains — no typed reference, no Nodes[] ordering). Built entirely by
script from OpWire_v1 (docs/keystone-op-spec.md §23–§24).

Run through the deadline runner:
  py tools/bgrun.py --max-min 8 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_opconnect.py [--no-test]

OpWire_v1 skeleton (inventory 2026-09-06 19:1x): chain A = controls vi path(96) / Class Name(363) / index(1056)
-> Traverse 124 (495,281) -> IA308 (605,284) -> TMSC 683 + class const 755 -> SubVI 216 (725,281);
chain B = Class Name 2(526) / index 2(1098) -> Traverse 170 (495,451) -> IA327 (605,454) -> TMSC 788 +
const 834 -> SubVI 262 (875,451) [Wire Inputs, Names 2 (1002)]; Names (926) -> SubVI 216; sinks Clear
Errors 369 (980,470) / 370 (980,540); error out indicator 533 at (0,75). 26 wires, ExecState 1.

Steps (prediction contract per step):
  1. copy OpWire_v1 -> OpConnect_v0; delete SubVIs 216, 262; Functions 683, 788 (TMSCs); Constants 755, 834
  2. delete every wire with x >= 598, plus uids 386/390 (Traverse error-out wires to the deleted TMSCs, 2 px from the refs wires) (everything right of the two Index Arrays' inputs: their element wires start ~626, class-constant wires ~609/631) or the error-out wire
     (x<30, y<120) -> ExecState 1 (chains intact, sinks unwired)
  3. drop_subvi(Conditionally Connect Wire.vi) at (900, 450)
  4. wire IA308.element -> 'Terminal in' (sink) ; IA327.element -> 'Wire Source' (source);
     creator 'error out' -> Clear Errors 369 'error in (no error)'
  5. ExecState 1 -> COM save; else STOP
  6. test on a scratch copy of GUIBENCH_v0: sink = the unwired IndexArray 534's array input (975,350),
     source = the Traverse 124 output terminal (the one feeding IA308) -> Wires +1
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CREATOR = os.path.join(EM, "Conditionally Connect Wire.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnect_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_connect_target.vi")
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def del_uid(cls, uid):
    i = [o["uid"] for o in g.report(OP, cls)].index(uid)
    return g.delete_object(OP, cls, i)


def delete_wires_where(pred, label):
    gone = []
    while True:
        wires = g.report(OP, "Wire")
        d = [i for i, o in enumerate(wires) if pred(o)]
        if not d:
            break
        gone.append((wires[d[0]]["uid"], wires[d[0]]["pos"]))
        g.delete_object(OP, "Wire", d[0])
    print(f"   {label}: deleted {gone}", flush=True)
    return gone


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
    print("baseline Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)

    def strip():
        for cls, uid in (("SubVI", 216), ("SubVI", 262), ("Function", 683), ("Function", 788), ("Constant", 755), ("Constant", 834)):
            del_uid(cls, uid)
        return [(o["uid"], o["pos"]) for o in g.report(OP, "SubVI")], g.exec_state(OP)
    step("1 delete the name-based wiring stage (2 SubVIs, 2 TMSCs, 2 class constants)", "SubVIs left: 369, 370, 170, 124; ExecState 0", strip)
    step("2 delete wires right of the Index Arrays + the error-out wire", "ExecState 1",
         lambda: (delete_wires_where(lambda o: o["pos"][0] >= 598 or (o["pos"][0] < 30 and o["pos"][1] < 120) or o["uid"] in (386, 390), "dangling"), g.exec_state(OP)))
    if g.exec_state(OP) != 1:
        print("STOP: broken after strip; not saving", flush=True); return 2
    w0 = g.count(OP, "Wire")

    sub0 = g.uids(OP, "SubVI")
    step("3 drop Conditionally Connect Wire.vi", "+1 SubVI", lambda: g.drop_subvi(OP, CREATOR, 0, (900, 450)))
    subs = g.report(OP, "SubVI")
    ni = next((i for i, o in enumerate(subs) if o["uid"] not in sub0), None)
    if ni is None:
        print("STOP: creator not dropped", flush=True); return 3
    si = next(i for i, o in enumerate(subs) if o["uid"] == 369)
    ias = [o["uid"] for o in g.report(OP, "IndexArray")]
    a308, a327 = ias.index(308), ias.index(327)
    step("4a IA308.element -> Terminal in (sink)", "Wire +1", lambda: g.wire(OP, "IndexArray", a308, "element", "SubVI", ni, "Terminal in"))
    step("4b IA327.element -> Wire Source", "Wire +1", lambda: g.wire(OP, "IndexArray", a327, "element", "SubVI", ni, "Wire Source"))
    step("4c creator error out -> Clear Errors 369", "Wire +1", lambda: g.wire(OP, "SubVI", ni, "error out", "SubVI", si, "error in (no error)"))
    es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "(was", w0, ") ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 4
    step("5 COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    terms = g.report(TGT, "Terminal")
    sink = next(i for i, o in enumerate(terms) if o["pos"] == (975, 350))                     # IA534 array input (unwired)
    # source = the 'Names' string-array control terminal (679,240) (a source terminal of array type)
    srcs = [i for i, o in enumerate(terms) if o["owner"] == "ControlTerminal" and abs(o["pos"][0] - 679) <= 12 and abs(o["pos"][1] - 240) <= 12]
    srcs += [i for i, o in enumerate(terms) if o["owner"] == "SubVI" and o["pos"] == (511, 281)]
    print("target: sink", sink, terms[sink], "source candidates", [(i, terms[i]["pos"]) for i in srcs], flush=True)
    b_w = g.count(TGT, "Wire")
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT)
    vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", sink); vi.SetControlValue("Names", [])
    vi.SetControlValue("Class Name 2", "Terminal"); vi.SetControlValue("index 2", srcs[0]); vi.SetControlValue("Names 2", [])
    t0 = time.time()
    step(f"6 RUN OpConnect_v0: Terminal[{srcs[0]}] -> Terminal[{sink}]", "Wires +1; target ExecState 1 (IA534 now has an array)",
         lambda: (g._run(vi), f"{time.time() - t0:.2f}s", f"Wires {b_w}->{g.count(TGT, 'Wire')}", "ExecState", g.exec_state(TGT), "err", g._err(vi)))
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
