"""build_optunnels_v0.py - OpTunnels_v0.vi: the `index`-th LoopTunnel of a VI - its own UID, IndexMode, the OUTER
terminal (name / Is Source? / connected-wire UID) and the INNER terminal(s) as arrays (one per frame) - in ONE run.

WHY. docs/frame-loop-wire-graph.md: 83 of the frame loop's 156 wires are half-edges because a loop's tunnels are
not in AbstractDiagram.Nodes[]. A tunnel's outer wire lives in the parent diagram and its inner wire in the loop
body, so (outer uid, inner uid) per tunnel stitches the two and names the loop's inputs/outputs.

API (peer review archive/peer/2026-09-14-optunnels-v0-plan.md, labviewwiki): Tunnel.Outside Terminal 6356001
(short name on this machine 'Outer Term', docs/NAMES.md), Tunnel.Inside Terminals[] 6356000 (array, one per frame),
LoopTunnel.Index Mode 6356C00, GObject.UID 632A813; Terminal.Name 634A004 / Is Source? 634A003 / Connected Wire
634A000. Shift registers are sibling classes (LeftShiftRegister/RightShiftRegister) - NOT covered by v0.

DONOR: OpSetIndexMode_v0.vi - Traverse('LoopTunnel', index) -> Index Array -> To More Specific Class(LoopTunnel) ->
[IndexMode WRITE PN, deleted]. Same front half OpTunnelInd_v0 was built from.

STEPS (prediction per step; a miss prints 'exc'/'STOP', nothing saved):
  1  copy, open_panel, donor md5                                              ExecState 1
  2  delete the donor's IndexMode WRITE PN (found by its sink terminal 'IndexMode') + RBW   ExecState 1
  3  PN_T LoopTunnel[Outer Term, InsideTerms[], IndexMode, UID] <- TMSC 'specific class reference'; rows checked
  4  outer chain: PN_ON Terminal[Name] <- 'Outer Term'; PN_OS[Is Source?] <- ON.ref out; PN_OC[Connected Wire]
     <- OS.ref out; PN_OW GObject[UID] <- OC.'Wire'                                        ExecState 1
  5  for_loop; PN_IN Terminal[Name] inside <- PN_T 'InsideTerms[]' (crosses); PN_IS, PN_IC, PN_IW chained;
     exit_loop Name / IsSource / UID + error outs of PN_IC, PN_IW -> index mode 1 -> array indicators
  6  scalar indicators (Terminal.Create Indicator via Nodes[]/Terminals[] indices from a walk): ON.Name, OS.IsSource,
     OW.UID, OC.error out, OW.error out, T.IndexMode, T.UID  -> labels discovered by diff
  7  auto error handling OFF; ExecState 1 -> save; labels -> tools/bench/optunnels_labels.json
  py tools/bgrun.py --max-min 25 --log tools/bench/build_optunnels_v0.log -- py -u tools/recipes/build_optunnels_v0.py
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpSetIndexMode_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpTunnels_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "optunnels_labels.json")
P_OUTER, P_INSIDE, P_IDXMODE, P_UID = "6356001", "6356000", "6356C00", "632A813"
P_NAME, P_ISSRC, P_CONNW = "634A004", "634A003", "634A000"
T_CAST_OUT = "specific class reference"
GENERIC = {"reference", "reference out", "error in (no error)", "error out", "error in"}
g._run.__defaults__ = (6.0, 120.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def snap(tag=""):
    return (f"{tag} ForLoop={len(g.report_all(OP, 'ForLoop'))} LoopTunnel={len(g.report_all(OP, 'LoopTunnel'))} "
            f"Property={len(g.report_all(OP, 'Property'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def pidx(uid):
    return [o["uid"] for o in g.report_all(OP, "Property")].index(uid)


def fidx(uid):
    return [o["uid"] for o in g.report_all(OP, "Function")].index(uid)


def walk(diagram=0):
    nodes, _ = g.net_map(OP, diagram, max_nodes=80, max_terms=24)
    return {u: (n, [(ti, t, w) for ti, t, w in terms]) for n, (u, _l, terms) in nodes.items()}


def pn(cls, props, pos, body=0):
    r = g.build_property(OP, cls, [(p, False) for p in props], pos, diagram_index=body)
    return r[-1]["uid"] if r else None


def main():
    g._lv = None
    try:
        g.close_panel(OP); time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(OP):
        os.remove(OP)
    donor_md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)
    time.sleep(1.0)
    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: donor copy not runnable. Nothing saved.", flush=True)
        return 2

    w = walk()
    for u, (n, terms) in w.items():
        print(f"   node uid {u} n {n}: {[t for _ti, t, _w in terms if t]}", flush=True)
    write_pn = next((u for u, (n, terms) in w.items() if any(t == "IndexMode" for _ti, t, _w in terms)), None)
    cast = next((u for u, (n, terms) in w.items() if any(t == T_CAST_OUT for _ti, t, _w in terms)), None)
    print(f"   IndexMode WRITE PN {write_pn}; To More Specific Class {cast}", flush=True)
    if write_pn is None or cast is None:
        print("STOP: donor chain not recognised. Nothing saved.", flush=True)
        return 2
    step("2 delete the IndexMode WRITE PN + RBW", "Property -1, ExecState 1",
         lambda: (g.delete_object(OP, "Property", pidx(write_pn)), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after removing the write node. Nothing saved.", flush=True)
        return 3

    t_uid = step("3 PN_T LoopTunnel[Outer Term, InsideTerms[], IndexMode, UID]", "Property +1",
                 lambda: pn("VI Server:LoopTunnel", [P_OUTER, P_INSIDE, P_IDXMODE, P_UID], (740, 250)))
    if not t_uid:
        return 3
    step("3b TMSC 'specific class reference' -> PN_T.reference", "Wire +1, ExecState 1",
         lambda: (g.wire(OP, "Function", fidx(cast), T_CAST_OUT, "Property", pidx(t_uid), "reference"), snap("after"))[1])
    t_rows = step("3c PN_T rows (walk)", "4 data terminals", lambda: [t for _ti, t, _w in walk()[t_uid][1] if t and t not in GENERIC])
    if not t_rows or len(t_rows) != 4:
        print(f"STOP: PN_T rows {t_rows}. Nothing saved.", flush=True)
        return 3
    T_OUT, T_INS, T_IDX, T_TUID = t_rows          # order as created: Outer Term, InsideTerms[], IndexMode, UID
    print(f"   PN_T terminal names: outer={T_OUT!r} inside={T_INS!r} indexmode={T_IDX!r} uid={T_TUID!r}", flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after PN_T. Nothing saved.", flush=True)
        return 3

    on = step("4a PN_ON Terminal[Name]", "Property +1", lambda: pn("VI Server:Terminal", [P_NAME], (950, 250)))
    if not on:
        return 3
    step("4b PN_T.outer -> PN_ON.reference", "Wire +1, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(t_uid), T_OUT, "Property", pidx(on), "reference"), snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: Outer Term does not feed a Terminal-class node. Nothing saved.", flush=True)
        return 3
    os_ = step("4c PN_OS Terminal[Is Source?]", "Property +1", lambda: pn("VI Server:Terminal", [P_ISSRC], (1150, 250)))
    oc = step("4d PN_OC Terminal[Connected Wire]", "Property +1", lambda: pn("VI Server:Terminal", [P_CONNW], (1350, 250)))
    ow = step("4e PN_OW GObject[UID]", "Property +1", lambda: pn("VI Server:GObject", [P_UID], (1550, 250)))
    if not (os_ and oc and ow):
        return 3
    step("4f ON.ref out -> OS.ref; OS.ref out -> OC.ref; OC.Wire -> OW.ref", "Wire +3, ExecState 1",
         lambda: ([g.wire(OP, "Property", pidx(on), "reference out", "Property", pidx(os_), "reference"),
                   g.wire(OP, "Property", pidx(os_), "reference out", "Property", pidx(oc), "reference"),
                   g.wire(OP, "Property", pidx(oc), "Wire", "Property", pidx(ow), "reference")], snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: outer chain broken. Nothing saved.", flush=True)
        return 3

    step("5a empty For Loop", "ForLoop +1; ExecState 0 EXPECTED", lambda: (g.for_loop(OP, (740, 600)), snap("after"))[1])
    dias = [i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner"))]
    if len(dias) != 1:
        print(f"STOP: loop body not unique {dias}. Nothing saved.", flush=True)
        return 3
    body = dias[0]
    inn = step("5b PN_IN Terminal[Name] inside body", "Property +1", lambda: pn("VI Server:Terminal", [P_NAME], (800, 650), body))
    if not inn:
        return 3
    step("5c PN_T.InsideTerms[] -> PN_IN.reference (crosses the loop)", "LoopTunnel +1, Wire +2, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(t_uid), T_INS, "Property", pidx(inn), "reference"), snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: InsideTerms[] does not auto-index into a Terminal node. Nothing saved.", flush=True)
        return 3
    is_ = step("5d PN_IS Terminal[Is Source?] inside", "Property +1", lambda: pn("VI Server:Terminal", [P_ISSRC], (1000, 650), body))
    ic = step("5e PN_IC Terminal[Connected Wire] inside", "Property +1", lambda: pn("VI Server:Terminal", [P_CONNW], (1200, 650), body))
    iw = step("5f PN_IW GObject[UID] inside", "Property +1", lambda: pn("VI Server:GObject", [P_UID], (1400, 650), body))
    if not (is_ and ic and iw):
        return 3
    step("5g inner chain wires", "Wire +3, ExecState 1",
         lambda: ([g.wire(OP, "Property", pidx(inn), "reference out", "Property", pidx(is_), "reference"),
                   g.wire(OP, "Property", pidx(is_), "reference out", "Property", pidx(ic), "reference"),
                   g.wire(OP, "Property", pidx(ic), "Wire", "Property", pidx(iw), "reference")], snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: inner chain broken. Nothing saved.", flush=True)
        return 3
    tun_before = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    meanings = ["InName", "InIsSource", "InWireUID"]
    for u, outs in ((inn, ["Name"]), (is_, ["IsSource"]), (iw, ["UID"])):
        step(f"5h exit_loop {outs}", "LoopTunnel +1", lambda u=u, outs=outs: (g.exit_loop(OP, pidx(u), outs, body, node_class="Property"), snap("after"))[1])
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True)
        return 4
    for u, tag in ((ic, "InConnErr"), (iw, "InWireErr")):
        try:
            g.exit_loop(OP, pidx(u), ["error out"], body, node_class="Property"); meanings.append(tag)
        except Exception as e:
            print(f"   optional: {tag} not tunnelled ({str(e)[:80]})", flush=True)
    out_tuns = [o["i"] for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun_before]
    label_map = {}
    for k, tun in enumerate(out_tuns):
        before = set(inds())
        try:
            g.set_index_mode(OP, tun, 1)
        except Exception as e:
            print(f"   tunnel {tun}: set_index_mode {str(e)[:100]}", flush=True)
        try:
            g.tunnel_indicator(OP, tun)
        except Exception as e:
            print(f"   tunnel {tun}: tunnel_indicator FAILED {str(e)[:150]}", flush=True)
            continue
        new = [l for l in inds() if l not in before]
        meaning = meanings[k] if k < len(meanings) else f"tunnel {tun}"
        print(f"   tunnel {tun} -> {new} (carries {meaning})", flush=True)
        for l in new:
            label_map[l] = meaning

    # 6 scalar indicators on the top diagram, by Nodes[]/Terminals[] indices from ONE walk
    w = walk()
    want = [(on, "Name", "OutName"), (os_, "IsSource", "OutIsSource"), (ow, "UID", "OutWireUID"),
            (oc, "error out", "OutConnErr"), (ow, "error out", "OutWireErr"), (t_uid, T_IDX, "IndexMode"), (t_uid, T_TUID, "TunnelUID")]
    for u, tname, meaning in want:
        n, terms = w[u]
        ti = next((ti for ti, t, _w in terms if t == tname), None)
        if ti is None:
            print(f"   indicator for {meaning}: terminal {tname!r} not found on uid {u}", flush=True)
            continue
        before = set(inds())
        try:
            g.create_indicator(OP, n, ti)
        except Exception as e:
            print(f"   indicator for {meaning}: EXC {str(e)[:120]}", flush=True)
            continue
        new = [l for l in inds() if l not in before]
        print(f"   {meaning}: node {n} terminal {ti} ({tname!r}) -> indicator {new}", flush=True)
        for l in new:
            label_map[l] = meaning
    step("7 auto error handling OFF", "silent on unwired terminals", lambda: g.set_auto_error_handling(OP, False))
    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    print("label map:", json.dumps(label_map), flush=True)
    need = {"InName", "InIsSource", "InWireUID", "OutName", "OutIsSource", "OutWireUID", "IndexMode", "TunnelUID"}
    if es != 1 or not need <= set(label_map.values()):
        print(f"\nVERDICT: BROKEN or incomplete (ExecState {es}, have {sorted(set(label_map.values()))}) - NOT SAVING.", flush=True)
        return 4
    step("8 COM save", "written to disk", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor OpSetIndexMode_v0.vi md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    print("\nVERDICT: OpTunnels_v0 BUILT and SAVED (structural only - run tools/bench/test_optunnels.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
