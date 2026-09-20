"""build_keystone_invoke.py — OpBuildInvoke_v0.vi: create an INVOKE NODE on a target diagram, class =
the target VI itself (VI-class reference), method = a string set from Python. Zero clicks, no
copy_into: every part is an existing op (drop_subvi, wire, wire_control) on a copy of OpWire_v1.

Run through the deadline runner:
  py tools/bgrun.py --max-min 12 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_keystone_invoke.py [--no-test]

Design (docs/keystone-op-spec.md, plan v3 — after codex 2026-09-06): the created node's class follows
the referenced OBJECT, so a VI reference (Open VI Reference's `vi reference` output, already on the
skeleton) yields a VI-class Invoke node; `Create Invoke Node.vi`'s `ID String` is wired from the
existing string control `Class Name` (chain A's Traverse then errors harmlessly into its own sink);
`Diagram in` comes from chain B (Class Name 2 = "Diagram"); the creator's error chain is taken from
Open VI Reference's error out, not from chain A. First use: method "Create from Data Type" — the VI
method that makes a front-panel control from a data type — which is what the Property-node keystone
needs for its `Properties` control.
Prediction contract: ExecState 1 after wiring (else STOP, no save); functional test: +1 Invoke on
a scratch copy of GUIBENCH_v0 with method text present in the reporter's class list.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import lvclick as c  # noqa: E402

EM = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
CREATOR = os.path.join(EM, "Create Invoke Node.vi")
SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpBuildInvoke_v0.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_buildinvoke_target.vi")
g._run.__defaults__ = (6.0, 60.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def title_click(title):
    try:
        L, T, R, B = c.rect(title)
        c.act("click", X=min(L + 300, R - 120), Y=T + 10); time.sleep(0.4)
    except Exception as e:
        print("   title click skipped:", str(e)[:80], flush=True)


def main():
    g._lv = None
    for p in (OP, TGT):
        if os.path.exists(p):
            try:
                g.close_panel(p)
            except Exception:
                pass
    shutil.copyfile(SRC, OP)
    g.open_panel(OP); time.sleep(1.0); title_click("OpBuildInvoke_v0.vi Front Panel")
    print("baseline ExecState", g.exec_state(OP), flush=True)

    # discovery: the Open VI Reference node — find it among all nodes by position (left of Traverse)
    nodes = g.report(OP, "Node")
    cands = [o for o in nodes if 250 <= o["pos"][0] <= 470 and 230 <= o["pos"][1] <= 300]
    print("   nodes near the vi-path chain:", [(o["class"], o["uid"], o["pos"]) for o in cands], flush=True)
    ovr = next((o for o in cands if "Open" in o["class"] or "VIRef" in o["class"] or "Ref" in o["class"]), None)
    if ovr is None and cands:
        ovr = cands[0]
    if ovr is None:
        print("STOP: Open VI Reference node not found", flush=True); return 2
    ovr_cls = ovr["class"]
    ovr_i = [o["uid"] for o in g.report(OP, ovr_cls)].index(ovr["uid"])
    print("   Open VI Reference ->", ovr_cls, "index", ovr_i, flush=True)

    sub0 = g.uids(OP, "SubVI")
    step("drop_subvi(Create Invoke Node.vi)", "+1 SubVI, ExecState 0", lambda: (g.drop_subvi(OP, CREATOR, 0, (875, 620)), g.exec_state(OP)))
    subs = g.report(OP, "SubVI")
    ci = next((i for i, o in enumerate(subs) if o["uid"] not in sub0), None)
    sinks = [i for i, o in enumerate(subs) if o["pos"] in ((980, 470), (980, 540))]
    ias = g.report(OP, "IndexArray")
    i327 = next(i for i, o in enumerate(ias) if o["uid"] == 327)
    print("   creator index", ci, "sinks", sinks, flush=True)

    step("IA327.element -> Diagram in", "branch accepted", lambda: g.wire(OP, "IndexArray", i327, "element", "SubVI", ci, "Diagram in", branch=True))

    def ref():
        for term in ("vi reference", "reference", "VI reference"):
            try:
                return term, g.wire(OP, ovr_cls, ovr_i, term, "SubVI", ci, "reference", branch=True)
            except Exception as e:
                print(f"   {term!r}: {str(e)[:100]}", flush=True)
        return None
    step("OpenVIRef.vi reference -> reference", "connected with one name", ref)
    # 'Class Name' is already wired to chain A's Traverse -> this is a BRANCH (count stays 26)
    step("control 'Class Name' -> ID String (branch)", "branch accepted", lambda: g.wire_control(OP, ["Class Name"], "SubVI", ci, ["ID String"], branch=True))
    step("OpenVIRef.error out -> creator error in (no error)", "branch accepted",
         lambda: g.wire(OP, ovr_cls, ovr_i, "error out", "SubVI", ci, "error in (no error)", branch=True))
    for si in sinks:
        r = step(f"creator error out -> sink {si}", "connected", lambda si=si: g.wire(OP, "SubVI", ci, "error out", "SubVI", si, "error in (no error)", branch=True))
        if r is not None:
            break
    es = g.exec_state(OP)
    print("\nassembled ExecState", es, flush=True)
    if es != 1:
        print("STOP: still broken (a required input unwired: check location / ID String); NOT saving", flush=True)
        return 3
    step("COM save", "size > 0", lambda: g.save(OP))
    if "--no-test" in sys.argv:
        return 0

    shutil.copyfile(TGT_SRC, TGT)
    g.open_panel(TGT); time.sleep(0.8); title_click("SCRATCH_buildinvoke_target.vi Front Panel")
    before = g.uids(TGT, "Invoke")
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT)
    vi.SetControlValue("Class Name", "Create from Data Type"); vi.SetControlValue("index", 0); vi.SetControlValue("Names", [])
    vi.SetControlValue("Class Name 2", "Diagram"); vi.SetControlValue("index 2", 0); vi.SetControlValue("Names 2", [])
    step("RUN OpBuildInvoke_v0 on scratch GUIBENCH copy", "+1 Invoke (VI class, method Create from Data Type)",
         lambda: (g._run(vi), g._err(vi), [(o["uid"], o["pos"]) for o in g.new_since(TGT, "Invoke", before)], g.exec_state(TGT)))
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
