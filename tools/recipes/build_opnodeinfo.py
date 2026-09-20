"""build_opfplabels.py — OpNodeInfo_v0.vi: report the LABEL text and Style code of block-diagram node
`index` (tabbing order) of any VI: VI -> Front Panel (23D) -> Panel.Controls[] (6348801) -> Index Array ->
Control.Label (6332005) / Control.Indicator (6332007) -> Text.Text (632D800) -> indicators 'Text' and
'Indicator' on the op, placed by OpCreateIndicator_v0. Zero GUI (spec §29). Built from OpWire_v1.

Run through the deadline runner (bgrun --max-min 8): tools/recipes/build_opfplabels.py [--no-test]

Steps (prediction contract per step):
  1. copy OpWire_v1 -> OpFPLabels_v0; delete SubVIs 216, 262, 124, 170; Functions 683, 788; Constants 755, 834;
     IndexArray 327; every wire except 106 (vi path -> Open VI Reference) and 1066 (index -> IA308)
  2. PN1 VI.Front Panel (420,300) <- OpenVIRef 'vi reference'; PN2 Panel.Controls[] (520,300) <- PN1 output
     (name probed: 'Panel' / 'Front Panel' / 'FP'); IA308.array <- PN2 'Controls[]'
  3. PN3 Control [Label, Indicator] (700,300) <- IA308.element; PN4 Text.Text (850,300) <- PN3 'Label'
  4. indicators: OpCreateIndicator_v0 on the op: PN4 terminal 4 -> 'Text'; PN3 terminal 5 -> 'Indicator'
     (a 2-property PN: reference, reference out, error in, error out, Label, Indicator — verified by reading
     GetControlValue afterwards; discovery mode sweeps and reports without saving if a stray appears)
  5. ExecState 1 -> COM save; test: list the front panel of Load and prep N cal images.vi
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi")
BG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
TEST_VI = os.path.join(BG, "Load and prep N cal images.vi")
KEEP = {106, 1066}
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def readable(name):
    try:
        g.op(OP).GetControlValue(name); return True
    except Exception:
        return False


def main():
    g._lv = None
    if os.path.exists(OP):
        try:
            g.close_panel(OP)
        except Exception:
            pass
    shutil.copyfile(SRC, OP)
    g.open_panel(OP); time.sleep(1.0)

    def strip():
        for cls, uid in (("SubVI", 216), ("SubVI", 262), ("SubVI", 124), ("SubVI", 170),
                         ("Function", 683), ("Function", 788), ("Constant", 755), ("Constant", 834), ("IndexArray", 327)):
            g.delete_object(OP, cls, idx(cls, uid))
        while True:
            ws = g.report(OP, "Wire")
            d = [i for i, o in enumerate(ws) if o["uid"] not in KEEP]
            if not d:
                break
            g.delete_object(OP, "Wire", d[0])
        return [(o["uid"], o["pos"]) for o in g.report(OP, "Wire")], g.exec_state(OP)
    step("1 strip to skeleton", "Wires [106,1066]; ExecState 0", strip)
    ovr = idx("Function", 43)

    pn1 = step("2a PN VI.Front Panel", "+1 Property", lambda: g.build_property(OP, "VI Server:VI", [("23C", False)], (420, 300)))
    if not pn1:
        return 2
    u1 = pn1[0]["uid"]
    step("2b OpenVIRef -> PN1.reference", "accepted", lambda: g.wire(OP, "Function", ovr, "vi reference", "Property", idx("Property", u1), "reference", branch=True))
    pn2 = step("2c PN Panel.Controls[]", "+1 Property", lambda: g.build_property(OP, "VI Server:Diagram", [("6375809", False)], (520, 300)))
    if not pn2:
        return 2
    u2 = pn2[0]["uid"]

    def fp_out():
        for term in ("Diagram",):
            try:
                return term, g.wire(OP, "Property", idx("Property", u1), term, "Property", idx("Property", u2), "reference")
            except Exception as e:
                print(f"   {term!r}: {str(e)[:80]}", flush=True)
        return None
    if not step("2d PN1 output -> PN2.reference", "one name accepted", fp_out):
        return 2

    def ctrls_out():
        for term in ("Nodes[]",):
            try:
                return term, g.wire(OP, "Property", idx("Property", u2), term, "IndexArray", idx("IndexArray", 308), "array")
            except Exception as e:
                print(f"   {term!r}: {str(e)[:80]}", flush=True)
        return None
    if not step("2e PN2.Controls[] -> IA308.array", "accepted", ctrls_out):
        return 2

    pn3 = step("3a PN Control [Label, Indicator]", "+1 Property", lambda: g.build_property(OP, "VI Server:Node", [("6359001", False), ("6359009", False)], (700, 300)))
    if not pn3:
        return 3
    u3 = pn3[0]["uid"]
    step("3b IA308.element -> PN3.reference (Control-typed)", "Wire +1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", 308), "element", "Property", idx("Property", u3), "reference"))
    pn4 = step("3c PN Text.Text", "+1 Property", lambda: g.build_property(OP, "VI Server:Text", [("632D800", False)], (850, 300)))
    if not pn4:
        return 3
    u4 = pn4[0]["uid"]
    step("3d PN3.Label -> PN4.reference", "Wire +1", lambda: g.wire(OP, "Property", idx("Property", u3), "Label", "Property", idx("Property", u4), "reference"))
    print("   ExecState before indicators", g.exec_state(OP), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: broken before indicators", flush=True); return 3

    n = g.count(OP, "Node")                 # creation order: ..., PN3 = n-2, PN4 = n-1
    forced = dict(a.split("=")[1].split(",") for a in sys.argv if a.startswith("--terms="))  # unused placeholder
    t_text = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--text-term=")), 4))
    t_ind = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--ind-term=")), 5))
    new = g.create_indicator(OP, n - 1, t_text)
    print(f"   PN4 terminal {t_text}: new {[(o['uid'], o['pos']) for o in new]} 'Text' readable={readable('Text')}", flush=True)
    if not (new and readable("Text")):
        print("STOP: 'Text' indicator not made; rerun with --text-term=N", flush=True); return 4
    new = g.create_indicator(OP, n - 2, t_ind)
    print(f"   PN3 terminal {t_ind}: new {[(o['uid'], o['pos']) for o in new]} 'Indicator' readable={readable('Style')}", flush=True)
    if not (new and readable("Style")):
        print("STOP: 'Style' indicator not made; rerun with --ind-term=N (not saving)", flush=True); return 4
    es = g.exec_state(OP)
    print("assembled Wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 5
    step("5 COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    vi = g.op(OP)
    vi.SetControlValue("vi path", TEST_VI); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", ""); vi.SetControlValue("index 2", 0)
    print("block-diagram nodes of", os.path.basename(TEST_VI), flush=True)
    for i in range(60):
        vi.SetControlValue("index", i)
        try:
            g._run(vi)
        except RuntimeError as e:
            print(f"   [{i}] end ({str(e)[:40]})", flush=True); break
        print(f"   [{i}] style={vi.GetControlValue('Style')!r} label={vi.GetControlValue('Text')!r}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
