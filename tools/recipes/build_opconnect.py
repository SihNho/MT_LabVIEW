"""build_opconnect.py — OpConnect_v0.vi: wire terminal tb of node nb (source) into terminal ta of node na (sink)
on a target VI with Terminal.Connect Wire (6349C03), both terminals addressed by the script-only ladder
(VI -> Block Diagram -> Nodes[] -> IA -> Terminals[] -> IA -> Terminal). Built from OpCreateControl_v0
(ladder A: controls index / index 2) plus a second ladder B whose Index Arrays are placed by OpBuildIA_v0
and whose index controls are minted by OpCreateControl_v0 on the op itself. Zero GUI (spec §25).
(The earlier attempt through erdosmiller Conditionally Connect Wire.vi is kept as
build_opconnect_gateway_attempt.py — its inputs are Terminal-typed, so it needs the same ladder.)

Run through the deadline runner:
  py tools/bgrun.py --max-min 10 --log tools/bench/build_keystone.log -- py -u tools/recipes/build_opconnect.py [--no-test]

Steps (prediction contract per step):
  1. copy OpCreateControl_v0 -> OpConnect_v0; delete its Invoke (Create Control) and the two wires with
     x >= 620 and y >= 440 (IA327.element -> reference, error out -> Clear Errors) -> ExecState 1
  2. ladder B: build_index_array at (520,600) [IAb1], build_property Node.Terminals[] at (700,600) [PNb],
     build_index_array at (850,600) [IAb2]; wire PN2.Nodes[] -> IAb1.array (branch), IAb1.element -> PNb.reference,
     PNb.Terms[] -> IAb2.array -> ExecState 1 (IA index inputs are optional)
  3. index controls for IAb1 / IAb2: run OpCreateControl_v0 on the op itself with node index = rank of the IA's
     uid among Node uids (Nodes[] = creation order hypothesis), terminal 1; the new ControlTerminal must land
     within 90 px of the IA (else STOP). Labels are LabVIEW auto-names (probed afterwards).
  4. build_invoke Terminal.Connect Wire at (1000,450); wire IA327.element -> reference (sink), IAb2.element ->
     'Wire Source', error out -> Clear Errors 369 -> ExecState 1 -> COM save
  5. test on a scratch copy of GUIBENCH_v0: sink = IndexArray 534 (975,350) terminal 0 ('array'); source = Traverse
     124 (node rank 1), terminal index swept 0..7 until Wires +1; report ExecState after the hit.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpCreateControl_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnect_v0.vi")
OP_CC = os.path.join(g.CLAUDEDEV, "OpCreateControl_v1.vi")   # v1 reports the new control's label on its Text indicator
TGT_SRC = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_connect_target.vi")
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def idx(cls, uid, target=None):
    return [o["uid"] for o in g.report(target or OP, cls)].index(uid)


def node_rank(uid, target=None):
    return sorted(o["uid"] for o in g.report(target or OP, "Node")).index(uid)


def create_control(target, node_index, term, expect_near):
    """OpCreateControl_v0 on `target`: control for terminal `term` of Nodes[node_index]; verify placement.
    Nodes[] is CREATION order (uid rank failed 2026-09-06 20:0x: uids 90/98 were reused for new nodes)."""
    before = g.uids(target, "ControlTerminal")
    vi = g.op(OP_CC)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("index", node_index); vi.SetControlValue("index 2", term)
    g._run(vi)
    new = g.new_since(target, "ControlTerminal", before)
    ok = len(new) == 1 and abs(new[0]["pos"][0] - expect_near[0]) <= 90 and abs(new[0]["pos"][1] - expect_near[1]) <= 90
    label = vi.GetControlValue("Text")
    return ok, [(o["uid"], o["pos"]) for o in new], label


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
    print("baseline Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), "Invokes", [(o["uid"], o["pos"]) for o in g.report(OP, "Invoke")], flush=True)

    def strip():
        g.delete_object(OP, "Invoke", 0)
        gone = []
        while True:
            ws = g.report(OP, "Wire")
            d = [i for i, o in enumerate(ws) if o["pos"][0] >= 620 and o["pos"][1] >= 440]
            if not d:
                break
            gone.append((ws[d[0]]["uid"], ws[d[0]]["pos"])); g.delete_object(OP, "Wire", d[0])
        return gone, g.count(OP, "Wire"), g.exec_state(OP)
    step("1 delete Create Control invoke + its 2 wires", "2 wires gone; Wires 8; ExecState 1", strip)
    if g.exec_state(OP) != 1:
        print("STOP: broken after strip", flush=True); return 1

    props = g.report(OP, "Property")
    pn2 = next(o for o in props if abs(o["pos"][0] - 520) < 30)          # Diagram.Nodes[]
    ia_b1 = step("2a build_index_array IAb1 (520,600)", "+1 IndexArray", lambda: g.build_index_array(OP, (520, 600)))
    pnb = step("2b build_property Node.Terminals[] (700,600)", "+1 Property", lambda: g.build_property(OP, "VI Server:Node", [("6359000", False)], (700, 600)))
    ia_b2 = step("2c build_index_array IAb2 (850,600)", "+1 IndexArray", lambda: g.build_index_array(OP, (850, 600)))
    if not (ia_b1 and pnb and ia_b2):
        return 2
    u_b1, u_pb, u_b2 = ia_b1[0]["uid"], pnb[0]["uid"], ia_b2[0]["uid"]
    step("2d PN2.Nodes[] -> IAb1.array (branch)", "accepted", lambda: g.wire(OP, "Property", idx("Property", pn2["uid"]), "Nodes[]", "IndexArray", idx("IndexArray", u_b1), "array", branch=True))
    step("2e IAb1.element -> PNb.reference", "Wire +1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", u_b1), "element", "Property", idx("Property", u_pb), "reference"))
    step("2f PNb.Terms[] -> IAb2.array", "Wire +1", lambda: g.wire(OP, "Property", idx("Property", u_pb), "Terms[]", "IndexArray", idx("IndexArray", u_b2), "array"))
    print("   ladder B assembled: Wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: broken after ladder B", flush=True); return 3

    n_nodes = g.count(OP, "Node")          # IAb1, PNb, IAb2 were created last, in that order
    r1 = step(f"3a control for IAb1.index (Nodes[{n_nodes - 3}], terminal 2 = 'index')", "1 new ControlTerminal within 90 px of (520,600); label 'index 3'",
              lambda: create_control(OP, n_nodes - 3, 2, (520, 600)))
    r2 = step(f"3b control for IAb2.index (Nodes[{n_nodes - 1}], terminal 2)", "1 new ControlTerminal within 90 px of (850,600); label 'index 4'",
              lambda: create_control(OP, n_nodes - 1, 2, (850, 600)))
    if not (r1 and r1[0] and r2 and r2[0]):
        print("STOP: index controls not placed as predicted (Nodes[] order hypothesis?) - NOT saving", flush=True); return 4
    print("   ExecState after controls", g.exec_state(OP), flush=True)

    inv = step("4 build_invoke Terminal.Connect Wire (1000,450)", "+1 Invoke", lambda: g.build_invoke(OP, "VI Server:Terminal", "6349C03", (1000, 450)))
    if not inv:
        return 5
    ui = inv[0]["uid"]
    step("4a IA327.element -> reference (sink)", "Wire +1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", 327), "element", "Invoke", idx("Invoke", ui), "reference"))
    step("4b IAb2.element -> Wire Source", "Wire +1", lambda: g.wire(OP, "IndexArray", idx("IndexArray", u_b2), "element", "Invoke", idx("Invoke", ui), "Wire Source"))
    step("4c error out -> Clear Errors 369", "Wire +1", lambda: g.wire(OP, "Invoke", idx("Invoke", ui), "error out", "SubVI", idx("SubVI", 369), "error in (no error)"))
    es = g.exec_state(OP)
    print("\nassembled Wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 6
    step("4d COM save", "size > 0", lambda: g.save(OP))
    names = [r1[2], r2[2]]           # labels reported by OpCreateControl_v1: node b index, terminal b index
    vi = g.op(OP)
    for n in names:
        vi.GetControlValue(n)         # raises if the reported label is not addressable
    print("   new index control names:", names, flush=True)
    if "--no-test" in sys.argv or len(names) < 2:
        return 0

    shutil.copyfile(TGT_SRC, TGT); g.open_panel(TGT); time.sleep(0.8)
    sink_rank = 11; src_rank = 1                 # Nodes[] creation order on GUIBENCH_v0 (sweep 2026-09-06: n=11 -> IA534, n=1 -> Traverse 124)
    print("target: sink IA534 rank", sink_rank, "source Traverse124 rank", src_rank, "Wires", g.count(TGT, "Wire"), "ExecState", g.exec_state(TGT), flush=True)
    vi = g.op(OP)
    vi.SetControlValue("vi path", TGT); vi.SetControlValue("Names", []); vi.SetControlValue("Names 2", [])
    vi.SetControlValue("Class Name", ""); vi.SetControlValue("Class Name 2", "")
    vi.SetControlValue("index", sink_rank); vi.SetControlValue("index 2", 0)          # sink: IA534 terminal 0 (array)
    hit = None
    for tb in range(8):
        vi.SetControlValue(names[0], src_rank); vi.SetControlValue(names[1], tb)
        b_w = g.count(TGT, "Wire"); t0 = time.time()
        try:
            g._run(vi)
        except Exception as e:
            print(f"   tb={tb}: run {str(e)[:60]}", flush=True)
        nw = g.count(TGT, "Wire")
        print(f"   tb={tb}: {time.time() - t0:.2f}s Wires {b_w}->{nw} ExecState {g.exec_state(TGT)} err={g._err(vi)}", flush=True)
        if nw > b_w:
            hit = tb; break
    print("HIT source terminal", hit, "target ExecState", g.exec_state(TGT), flush=True)
    try:
        g.close_panel(TGT); os.remove(TGT); print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
