"""build_opshiftregs_v1.py - OpShiftRegs_v1.vi = OpShiftRegs_v0 + the LEFT side of the `index 2`-th right register:
RightShiftRegister.Left Registers[] 6357800 (1-D array, stacked lefts) -> (a) a loop giving every left's UID,
(b) the `index 3`-th left: class name, OUTSIDE terminal (initial value, sink; wire 0 = uninitialised) and INSIDE
terminals (source into the body). Peer: archive/peer/2026-09-14-opshiftregs-v0-elements-are-right-registers.md -
GATE = the RightShiftRegister-class node accepts the Index Array element (ExecState 1); if it breaks, a typed seed is
needed (recorded, nothing saved).

STEPS (prediction each; a miss prints EXC/STOP and nothing is saved):
  1  copy OpShiftRegs_v0 -> OpShiftRegs_v1, open_panel                              ExecState 1
  2  locate IA (the Index Array fed by Shift Registers[]) and its element terminal
  3  PN_LR RightShiftRegister[Left Registers[]] <- IA.element (branch)               Property +1, ExecState 1 (GATE)
  4  loop A (uid-identified body) <- PN_LR array; PN_LU GObject[UID] inside; exit_loop -> LeftUIDs array
  5  IA2 = build_index_array; connect IA2.array <- PN_LR data (branch); control on IA2.index -> 'index 3'
  6  PN_LC2 GObject[Class Name] <- IA2.element; PN_LO Tunnel[Outside Terminal] <- LC2 out; LON/LOS/LOC/LOW chain
  7  PN_LI Tunnel[Inside Terminals[]] <- LO out; loop B (uid-identified) <- LI array; LIN/LIS/LIC/LIW inside;
     exit_loop Name/IsSource/UID -> arrays
  8  scalar indicators: LC2.ClassName, LOW.UID, LON.Name, LOS.IsSource, LR.error out, LO.error out, LI.error out
  9  auto error handling OFF; ExecState 1 -> save; labels (v0 map + new) -> tools/bench/opshiftregs_v1_labels.json
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opshiftregs_v1.log -- py -u tools/recipes/build_opshiftregs_v1.py
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

SRC = os.path.join(g.CLAUDEDEV, "OpShiftRegs_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpShiftRegs_v1.vi")
MAP_IN = os.path.join(os.path.dirname(HERE), "bench", "opshiftregs_labels.json")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opshiftregs_v1_labels.json")
P_CLASSNAME, P_UID = "6327803", "632A813"
P_OUTER, P_INSIDE, P_LEFTREGS = "6356001", "6356000", "6357800"
P_NAME, P_ISSRC, P_CONNW = "634A004", "634A003", "634A000"
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
    return (f"{tag} IndexArray={len(g.report_all(OP, 'IndexArray'))} ForLoop={len(g.report_all(OP, 'ForLoop'))} "
            f"LoopTunnel={len(g.report_all(OP, 'LoopTunnel'))} Property={len(g.report_all(OP, 'Property'))} "
            f"Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def ctls():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if not is_ind and lab]


def idx(cls, uid):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def node_terms_of(uid, diagram=0):
    for cand in range(80):
        nu, rows = g.node_terms_uid(OP, diagram, cand)
        if not nu:
            return None, None
        if nu == uid:
            return cand, rows
    return None, None


def data_term(uid, diagram=0):
    _n, rows = node_terms_of(uid, diagram)
    return next(r["name"] for r in rows if r["i"] == 4)


def pn(cls, pid, pos, diagram=0):
    r = g.build_property(OP, cls, [(pid, False)], pos, diagram_index=diagram)
    return r[-1]["uid"] if r else None


def make_indicator(uid, term_name, diagram=0):
    n, rows = node_terms_of(uid, diagram)
    t = next(r["i"] for r in rows if r["name"] == term_name)
    before = set(inds()); g.create_indicator(OP, n, t)
    new = [l for l in inds() if l not in before]
    assert len(new) == 1, f"indicator on {term_name}: {new}"
    return new[0]


def new_loop(pos, tag):
    """for_loop at pos; returns (body_index_fn, loop_uid) with the body identified by DIAGRAM UID (NAMES.md rule)."""
    dia0 = {d["uid"] for d in g.report_all(OP, "Diagram")}; loops0 = {o["uid"] for o in g.report_all(OP, "ForLoop")}
    step(f"{tag} For loop (top level)", "ForLoop +1", lambda: (g.for_loop(OP, pos), snap("after"))[1])
    nd = [d for d in g.report_all(OP, "Diagram") if d["uid"] not in dia0]
    nl = [u for u in {o["uid"] for o in g.report_all(OP, "ForLoop")} if u not in loops0]
    print(f"   new diagram {[(d['uid'], d.get('owner')) for d in nd]}, new loop {nl}", flush=True)
    assert len(nd) == 1 and len(nl) == 1, "new loop/body not unique"
    buid = nd[0]["uid"]
    return (lambda: next(i for i, d in enumerate(g.report_all(OP, "Diagram")) if d["uid"] == buid)), nl[0]


def main():
    g._lv = None
    try:
        g.close_panel(OP); time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(OP):
        os.remove(OP)
    donor_md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(OP)

    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: donor copy not runnable.", flush=True); return 2

    # 2 the IA fed by Loop.Shift Registers[] - by WIRE identity (run 1 picked the donor's Traverse IA, whose 'index'
    # is wired too, and fed a GObject element to the RightShiftRegister node: build_opshiftregs_v1.log 17:25).
    props = {o["uid"] for o in g.report_all(OP, "Property")}
    data_wires = {}
    for cand in range(80):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            break
        if nu in props:
            d = [r for r in rows if r["i"] == 4]
            if d:
                data_wires[nu] = (d[0]["name"], d[0]["wire"])
    print(f"   top-level property nodes (data terminal, wire): {data_wires}", flush=True)
    sr = [(u, n, w) for u, (n, w) in data_wires.items() if "shift" in n.lower() or "reg" in n.lower()]
    if len(sr) != 1:
        print(f"STOP: Shift Registers[] node not unique: {sr}", flush=True); return 2
    sr_wire = sr[0][2]
    ia_uid = n_ia = None
    for u in [o["uid"] for o in g.report_all(OP, "IndexArray")]:
        n, rows = node_terms_of(u)
        names = {r["name"]: r for r in rows}
        print(f"   IndexArray uid {u} Nodes[] {n}: {[(r['i'], r['name'], r['wire']) for r in rows]}", flush=True)
        if names.get("array", {}).get("wire") == sr_wire:
            ia_uid, n_ia = u, n
    print(f"   Shift Registers[] wire {sr_wire} -> IA uid {ia_uid}", flush=True)
    if ia_uid is None:
        print("STOP: the Index Array on Shift Registers[] not found.", flush=True); return 2

    u_lr = step("3 PN_LR RightShiftRegister[Left Registers[]]", "Property +1 (class accepted by the creator)",
                lambda: pn("VI Server:RightShiftRegister", P_LEFTREGS, (1550, 1700)))
    if not u_lr:
        print("STOP: RightShiftRegister-class property node not creatable - recorded.", flush=True); return 3
    step("3-wire IA.element -> PN_LR.reference (branch)", "Wire +0/+1, ExecState 1 = GATE (element typed RightShiftRegister)",
         lambda: (g.wire(OP, "IndexArray", idx("IndexArray", ia_uid), "element", "Property", idx("Property", u_lr), "reference", branch=True), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: GATE failed - the element is not accepted as RightShiftRegister (typed seed needed). Nothing saved.", flush=True); return 4
    T_LR = data_term(u_lr)
    print(f"   PN_LR data terminal {T_LR!r}", flush=True)

    # 4 loop A: every left's UID
    bodyA, loopA = new_loop((1550, 1900), "4a")
    u_lu = step("4b PN_LU GObject[UID] inside loop A", "Property +1", lambda: pn("VI Server:GObject", P_UID, (1600, 1950), bodyA()))
    assert u_lu in [r["uid"] for r in g.node_labels(OP, bodyA())], "PN_LU not in loop A"
    tunA0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    step("4c PN_LR array -> PN_LU.ref (crosses)", "LoopTunnel +1, ExecState 1",
         lambda: (g.wire(OP, "Property", idx("Property", u_lr), T_LR, "Property", idx("Property", u_lu), "reference"), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: loop A not runnable.", flush=True); return 3
    step("4d exit_loop PN_LU ['UID']", "LoopTunnel +1", lambda: (g.exit_loop(OP, idx("Property", u_lu), ["UID"], bodyA(), node_class="Property"), snap("after"))[1])
    label_map = json.load(open(MAP_IN, encoding="utf-8"))
    for o in [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tunA0]:
        t = g.tunnels(OP, o["i"])
        if t.get("out_is_source"):
            before = set(inds()); g.set_index_mode(OP, o["i"], 1); g.tunnel_indicator(OP, o["i"])
            for l in [l for l in inds() if l not in before]:
                label_map[l] = "LeftUIDs"; print(f"   loop A output -> {l!r} = LeftUIDs", flush=True)

    # 5 IA2 on Left Registers[] with control 'index 3'
    ia2 = step("5a build_index_array", "IndexArray +1", lambda: g.build_index_array(OP, (1550, 2200)))
    if not ia2:
        return 3
    ia2_uid = ia2[-1]["uid"]; purge()
    n_ia2, rows2 = node_terms_of(ia2_uid)
    t_arr = next(r["i"] for r in rows2 if r["name"] == "array"); t_ix = next(r["i"] for r in rows2 if r["name"] == "index")
    n_lr, lr_rows = node_terms_of(u_lr); t_lr_i = next(r["i"] for r in lr_rows if r["name"] == T_LR)
    step("5b connect IA2.array <- PN_LR data (branch)", "branched, ExecState 1", lambda: g.connect_terminals(OP, n_ia2, t_arr, n_lr, t_lr_i))
    purge()
    c0 = set(ctls())
    step("5c create_control on IA2.index", "one new control", lambda: g.create_control(OP, n_ia2, t_ix))
    purge()
    idx3 = [l for l in ctls() if l not in c0]
    print(f"   left index control: {idx3}", flush=True)
    if len(idx3) != 1 or g.exec_state(OP) != 1:
        print("STOP: index 3 control / ExecState.", flush=True); return 3
    label_map[idx3[0]] = "index3"

    # 6 the left's class + outside chain
    u_lc2 = step("6a PN_LC2 GObject[Class Name] <- IA2.element", "Property +1", lambda: pn("VI Server:GObject", P_CLASSNAME, (1800, 2200)))
    step("6a-wire", "Wire +1", lambda: (g.wire(OP, "IndexArray", idx("IndexArray", ia2_uid), "element", "Property", idx("Property", u_lc2), "reference"), snap("after"))[1])
    u_lo = step("6b PN_LO Tunnel[Outside Terminal] <- LC2 out", "Property +1, ExecState 1", lambda: pn("VI Server:Tunnel", P_OUTER, (2050, 2200)))
    step("6b-wire", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", u_lc2), "reference out", "Property", idx("Property", u_lo), "reference"), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: left element not accepted by a Tunnel node.", flush=True); return 3
    T_LO = data_term(u_lo)
    u_lon = step("6c PN_LON Terminal[Name]", "Property +1", lambda: pn("VI Server:Terminal", P_NAME, (2300, 2200)))
    step("6c-wire LO.outer -> LON.ref", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", u_lo), T_LO, "Property", idx("Property", u_lon), "reference"), snap("after"))[1])
    u_los = step("6d PN_LOS Terminal[Is Source?]", "Property +1", lambda: pn("VI Server:Terminal", P_ISSRC, (2550, 2200)))
    u_loc = step("6e PN_LOC Terminal[Connected Wire]", "Property +1", lambda: pn("VI Server:Terminal", P_CONNW, (2800, 2200)))
    u_low = step("6f PN_LOW GObject[UID]", "Property +1", lambda: pn("VI Server:GObject", P_UID, (3050, 2200)))
    if not (u_lon and u_los and u_loc and u_low):
        return 3
    step("6g LON -> LOS -> LOC -> LOW wires", "Wire +3, ExecState 1",
         lambda: ([g.wire(OP, "Property", idx("Property", u_lon), "reference out", "Property", idx("Property", u_los), "reference"),
                   g.wire(OP, "Property", idx("Property", u_los), "reference out", "Property", idx("Property", u_loc), "reference"),
                   g.wire(OP, "Property", idx("Property", u_loc), "Wire", "Property", idx("Property", u_low), "reference")], snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: left outer chain broken.", flush=True); return 3

    # 7 the left's inside terminals (loop B)
    u_li = step("7a PN_LI Tunnel[Inside Terminals[]] <- LO ref out", "Property +1", lambda: pn("VI Server:Tunnel", P_INSIDE, (2050, 2400)))
    step("7a-wire", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", u_lo), "reference out", "Property", idx("Property", u_li), "reference"), snap("after"))[1])
    T_LI = data_term(u_li)
    bodyB, loopB = new_loop((2300, 2400), "7b")
    u_lin = step("7c PN_LIN Terminal[Name] inside loop B", "Property +1", lambda: pn("VI Server:Terminal", P_NAME, (2350, 2450), bodyB()))
    assert u_lin in [r["uid"] for r in g.node_labels(OP, bodyB())], "PN_LIN not in loop B"
    tunB0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    step("7d PN_LI array -> PN_LIN.ref (crosses)", "LoopTunnel +1, ExecState 1",
         lambda: (g.wire(OP, "Property", idx("Property", u_li), T_LI, "Property", idx("Property", u_lin), "reference"), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: loop B not runnable after the array input.", flush=True); return 3
    u_lis = step("7e PN_LIS inside", "Property +1", lambda: pn("VI Server:Terminal", P_ISSRC, (2550, 2450), bodyB()))
    u_lic = step("7f PN_LIC inside", "Property +1", lambda: pn("VI Server:Terminal", P_CONNW, (2750, 2450), bodyB()))
    u_liw = step("7g PN_LIW inside", "Property +1", lambda: pn("VI Server:GObject", P_UID, (2950, 2450), bodyB()))
    if not (u_lis and u_lic and u_liw):
        return 3
    step("7h inner chain wires", "Wire +3, ExecState 1",
         lambda: ([g.wire(OP, "Property", idx("Property", u_lin), "reference out", "Property", idx("Property", u_lis), "reference"),
                   g.wire(OP, "Property", idx("Property", u_lis), "reference out", "Property", idx("Property", u_lic), "reference"),
                   g.wire(OP, "Property", idx("Property", u_lic), "Wire", "Property", idx("Property", u_liw), "reference")], snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: left inner chain broken.", flush=True); return 3
    tunB1 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    meanings = ["LeftInName", "LeftInIsSource", "LeftInWireUID"]
    for u, outs in ((u_lin, ["Name"]), (u_lis, ["IsSource"]), (u_liw, ["UID"])):
        step(f"7i exit_loop {outs}", "LoopTunnel +1", lambda u=u, outs=outs: (g.exit_loop(OP, idx("Property", u), outs, bodyB(), node_class="Property"), snap("after"))[1])
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True); return 4
    for k, o in enumerate([o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tunB1]):
        before = set(inds())
        try:
            g.set_index_mode(OP, o["i"], 1); g.tunnel_indicator(OP, o["i"])
        except Exception as e:
            print(f"   tunnel {o['i']}: {str(e)[:120]}", flush=True); continue
        for l in [l for l in inds() if l not in before]:
            label_map[l] = meanings[k] if k < 3 else f"tunnel {o['i']}"; print(f"   loop B output -> {l!r} = {label_map[l]}", flush=True)
    for uid, term, meaning in ((u_lc2, data_term(u_lc2), "LeftClassName"), (u_low, "UID", "LeftOutWireUID"), (u_lon, data_term(u_lon), "LeftOutName"),
                               (u_los, data_term(u_los), "LeftOutIsSource"), (u_lr, "error out", "LeftRegsErr"), (u_lo, "error out", "LeftOuterErr"),
                               (u_li, "error out", "LeftInsideErr")):
        try:
            label_map[make_indicator(uid, term)] = meaning
        except Exception as e:
            print(f"   indicator {meaning}: EXC {str(e)[:150]}", flush=True)
    step("9 auto error handling OFF", "no dialog", lambda: g.set_auto_error_handling(OP, False))
    purge(); es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True); print("label map:", json.dumps(label_map), flush=True)
    need = {"LeftUIDs", "index3", "LeftClassName", "LeftOutWireUID", "LeftOutName", "LeftOutIsSource", "LeftInName", "LeftInIsSource", "LeftInWireUID"}
    if es != 1 or not need <= set(label_map.values()):
        print(f"\nVERDICT: BROKEN (ExecState {es}, missing {need - set(label_map.values())}) - NOT SAVING.", flush=True); return 4
    step("10 COM save", "written", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("\nVERDICT: OpShiftRegs_v1 BUILT and SAVED (structural only - run tools/bench/test_opshiftregs_v1.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
