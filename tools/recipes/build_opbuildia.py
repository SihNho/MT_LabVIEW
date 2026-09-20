"""build_opbuildia.py — OpBuildIA_v0.vi: place an Index Array primitive on a target's top-level diagram,
already wired from ANY terminal the reporter can address (Traverse class "Terminal", index k), using
erdosmiller `Create Index Array.vi`. Built entirely by script from OpBuildPN_v0 (step 3b ladder,
docs/keystone-op-spec.md §21–§23).

Run through the deadline runner:
  py tools/bgrun.py --max-min 8 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_opbuildia.py [--no-test]

Verified 2026-09-06 (in-memory probes): `array` accepts a GObject-typed wire; `Diagram in` is REQUIRED.
So the diagram must come from a source independent of the Traverse chain (which now addresses the
terminal): a VI-class Property Node `Block Diagram` (ID from docs/vi-server-ids.json, key "VI.Block Diagram")
fed by Open VI Reference's typed VI wire. The TMSC(Diagram) chain becomes dead weight and is removed.

Steps (prediction contract per step):
  1. copy OpBuildPN_v0 -> OpBuildIA_v0; delete the creator SubVI -> ExecState 0
  2. delete the creator's 4 wires (x >= TMSC x+20, or the error-out wire at (x<30,y<120)) -> ExecState 1
  3. delete the TMSC (rightmost Function) and its two wires (class constant -> TMSC; IA308.element -> TMSC),
     then the class constant -> ExecState 1
  4. drop_subvi(Create Index Array.vi) at (900, 640)
  5. build_property(op, "VI Server:VI", [(BLOCK_DIAGRAM_ID, False)], (700, 380)); wire Open VI Reference
     'vi reference' -> PN reference (branch); wire PN 'Block Diagram' -> creator 'Diagram in'
  6. wire IA308.element -> creator 'array'; wire_control 'location (0, 0)' -> 'location (0, 0)'
  7. ExecState 1 -> COM save; else STOP (nothing saved)
  8. test on a scratch copy of GUIBENCH_v0: Class Name="Terminal", index=k (first IndexArray-owned terminal),
     -> +1 IndexArray near (1300,700) and +1 Wire
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CREATOR = os.path.join(EM, "Create Index Array.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpBuildPN_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpBuildIA_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_buildia_target.vi")
IDS = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "vi-server-ids.json")
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def block_diagram_id():
    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("VI.Block Diagram", "VI:Block Diagram") and isinstance(v, str):
                    return v
                r = walk(v)
                if r:
                    return r
        return None
    v = walk(json.load(open(IDS, encoding="utf-8")))
    if not v:
        raise SystemExit("STOP: docs/vi-server-ids.json has no 'VI.Block Diagram' entry")
    return v


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
    bd_id = block_diagram_id()
    g._lv = None
    for p in (OP, TGT):
        if os.path.exists(p):
            try:
                g.close_panel(p)
            except Exception:
                pass
    shutil.copyfile(SRC, OP)
    g.open_panel(OP); time.sleep(1.0)
    subs = g.report(OP, "SubVI"); fns = g.report(OP, "Function")
    print("baseline SubVIs", [(o["uid"], o["pos"]) for o in subs], "Functions", [(o["uid"], o["pos"]) for o in fns],
          "Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    ci = max(range(len(subs)), key=lambda i: subs[i]["pos"][0])
    ti = max(range(len(fns)), key=lambda i: fns[i]["pos"][0])
    tmsc = fns[ti]; tx, ty = tmsc["pos"]
    ovr = min(fns, key=lambda o: o["pos"][0])                      # Open VI Reference = leftmost Function

    step("1 delete the creator SubVI", "1 SubVI gone; ExecState 0", lambda: (g.delete_object(OP, "SubVI", ci), g.exec_state(OP)))
    step("2 delete the creator's wires", "4 wires; ExecState 1",
         lambda: (delete_wires_where(lambda o: o["pos"][0] >= tx + 20 or (o["pos"][0] < 30 and o["pos"][1] < 120), "creator wires"), g.exec_state(OP)))
    if g.exec_state(OP) != 1:
        print("STOP: broken after creator cleanup", flush=True); return 2

    def drop_tmsc():
        i = [o["uid"] for o in g.report(OP, "Function")].index(tmsc["uid"])
        g.delete_object(OP, "Function", i)
        # its wires: class constant -> target class (starts ~x 617,y 250) and IA308.element -> reference (~626,280)
        delete_wires_where(lambda o: tx - 40 <= o["pos"][0] < tx + 20 and ty - 40 <= o["pos"][1] <= ty + 30, "TMSC wires")
        cs = [i for i, o in enumerate(g.report(OP, "Constant")) if o["class"] == "ClassSpecifierConstant"]
        if cs:
            g.delete_object(OP, "Constant", cs[0])
        return g.count(OP, "Wire"), g.exec_state(OP)
    step("3 delete TMSC + its wires + class constant", "Wires 6, ExecState 1", drop_tmsc)
    if g.exec_state(OP) != 1:
        print("STOP: broken after TMSC removal", flush=True); return 3
    w0 = g.count(OP, "Wire")

    sub0 = g.uids(OP, "SubVI")
    step("4 drop Create Index Array.vi", "+1 SubVI; ExecState 0", lambda: (g.drop_subvi(OP, CREATOR, 0, (900, 640)), g.exec_state(OP)))
    subs = g.report(OP, "SubVI")
    ni = next((i for i, o in enumerate(subs) if o["uid"] not in sub0), None)
    if ni is None:
        print("STOP: creator not dropped", flush=True); return 4

    pn = step("5a build_property VI.Block Diagram", "+1 Property at (700,380)",
              lambda: g.build_property(OP, "VI Server:VI", [(bd_id, False)], (700, 380)))
    if not pn:
        return 5
    pi = [o["uid"] for o in g.report(OP, "Property")].index(pn[0]["uid"])
    oi = [o["uid"] for o in g.report(OP, "Function")].index(ovr["uid"])

    def vi_ref():
        for term in ("vi reference", "VI reference", "reference"):
            try:
                return term, g.wire(OP, "Function", oi, term, "Property", pi, "reference", branch=True)
            except Exception as e:
                print(f"   {term!r}: {str(e)[:90]}", flush=True)
        return None
    step("5b OpenVIRef.vi reference -> PN.reference (branch)", "accepted", vi_ref)
    step("5c PN.Block Diagram -> creator Diagram in", "Wire +1",
         lambda: g.wire(OP, "Property", pi, "Diagram", "SubVI", ni, "Diagram in"))
    ia = [o["uid"] for o in g.report(OP, "IndexArray")].index(308)
    step("6a IA308.element -> creator array", "Wire +1", lambda: g.wire(OP, "IndexArray", ia, "element", "SubVI", ni, "array"))
    step("6b control location -> location (0, 0)", "Wire +1", lambda: g.wire_control(OP, ["location (0, 0)"], "SubVI", ni, ["location (0, 0)"]))
    es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "(was", w0, ") ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    step("7 COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    terms = g.report(TGT, "Terminal")
    ia_terms = [(i, o) for i, o in enumerate(terms) if o["owner"] == "IndexArray"]
    print("target terminals", len(terms), "IndexArray-owned:", [(i, o["uid"], o["pos"]) for i, o in ia_terms][:6], flush=True)
    k = ia_terms[0][0] if ia_terms else 0
    b_ia = g.uids(TGT, "IndexArray"); b_w = g.count(TGT, "Wire")
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", k)
    vi.SetControlValue("location (0, 0)", [1300, 700])
    t0 = time.time()
    step(f"8 RUN OpBuildIA_v0: IA wired from Terminal[{k}]", "+1 IndexArray near (1300,700); Wires +1",
         lambda: (g._run(vi), f"{time.time() - t0:.2f}s", [(o["uid"], o["pos"]) for o in g.new_since(TGT, "IndexArray", b_ia)],
                  f"Wires {b_w}->{g.count(TGT, 'Wire')}", "target ExecState", g.exec_state(TGT)))
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
