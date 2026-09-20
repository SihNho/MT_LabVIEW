"""build_opshiftregs_v0.py - OpShiftRegs_v0.vi: the `index 2`-th shift register of the `index`-th loop (Traverse
`Class Name` = WhileLoop / ForLoop) - its runtime class name, UID, OUTSIDE terminal (name / Is Source? / wire UID) and
INSIDE terminals (arrays, one per frame) - the Tunnel-only census the peer asked for as v0
(archive/peer/2026-09-14-opshiftregs-v0-plan.md). Pairing (LeftShiftRegister.Right Shift Register) is v1.

DONOR: OpWhileCast_v0.vi (Traverse -> IA -> TMSC seeded WhileLoop -> PN_U GObject[UID], PN_SR Loop[Shift Registers[]]
-> For loop -> PN_SU GObject[UID] -> 'Array' = ShiftRegUIDs). Everything is KEPT (the UID array stays useful); the
new chain branches from PN_SR's array output through a new Index Array driven by a new `index 2` control.

STEPS (prediction each; a miss prints EXC/STOP and nothing is saved):
  1  copy, open_panel                                                              ExecState 1
  2  build_index_array (top level); connect_terminals IA.array <- PN_SR data (branch)  IndexArray +1, ExecState 1
  3  create_control on IA.index -> label (expected 'index 2')                       new control
  4  PN_CN GObject[Class Name 6327803] <- IA.element                                Property +1
  5  PN_OT Tunnel[Outside Terminal 6356001] <- PN_CN ref out                       ExecState 1 iff element is a Tunnel
  6  PN_ON Terminal[Name] <- OT out; PN_OS[Is Source?] <- ON; PN_OC[Connected Wire] <- OS; PN_OW GObject[UID] <- OC.Wire
  7  PN_IT Tunnel[Inside Terminals[] 6356000] <- PN_OT ref out
  8  for_loop (top level); PN_IN Terminal[Name] inside <- PN_IT array (crosses); PN_IS, PN_IC, PN_IW chained;
     exit_loop Name / IsSource / UID (+ error outs of IC, IW) -> index mode 1 -> array indicators
  9  scalar indicators: CN.ClassName, OW.UID, ON.Name, OS.IsSource, OT.error out, OC.error out, IT.error out
 10  auto error handling OFF; ExecState 1 -> save; labels -> tools/bench/opshiftregs_labels.json
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opshiftregs_v0.log -- py -u tools/recipes/build_opshiftregs_v0.py
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

SRC = os.path.join(g.CLAUDEDEV, "OpWhileCast_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpShiftRegs_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opshiftregs_labels.json")
P_CLASSNAME, P_UID = "6327803", "632A813"
P_OUTER, P_INSIDE = "6356001", "6356000"
P_NAME, P_ISSRC, P_CONNW = "634A004", "634A003", "634A000"
GENERIC = ("reference", "reference out", "error in (no error)", "error out")
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
    for cand in range(60):
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

    # the donor's PN_SR = the top-level Property node whose data terminal is not 'UID'
    props = {o["uid"] for o in g.report_all(OP, "Property")}
    sr_uid = n_sr = t_sr = None
    for cand in range(40):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            break
        if nu in props:
            d = [r for r in rows if r["i"] == 4]
            print(f"   top-level PN uid {nu} Nodes[] {cand} data terminal {d[0]['name'] if d else None!r}", flush=True)
            if d and d[0]["name"] != "UID":
                sr_uid, n_sr, t_sr = nu, cand, d[0]["name"]
    if sr_uid is None:
        print("STOP: PN_SR not found.", flush=True); return 2
    print(f"   PN_SR uid {sr_uid} Nodes[] {n_sr} data terminal {t_sr!r}", flush=True)

    ia = step("2a build_index_array (top level)", "IndexArray +1", lambda: g.build_index_array(OP, (1300, 1150)))
    if not ia:
        return 3
    ia_uid = ia[-1]["uid"]; purge()
    n_ia, ia_rows = node_terms_of(ia_uid)
    print(f"   IA Nodes[] {n_ia} terminals {[(r['i'], r['name'], r['is_source']) for r in ia_rows]}", flush=True)
    t_arr = next(r["i"] for r in ia_rows if r["name"] == "array"); t_el = next(r["i"] for r in ia_rows if r["name"] == "element")
    t_ix = next(r["i"] for r in ia_rows if r["name"] == "index")
    n_sr2, sr_rows = node_terms_of(sr_uid); t_sr_i = next(r["i"] for r in sr_rows if r["name"] == t_sr)
    step("2b connect_terminals IA.array <- PN_SR data (branch)", "(0, 1): branched, ExecState 1",
         lambda: g.connect_terminals(OP, n_ia, t_arr, n_sr2, t_sr_i))
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after IA.array wire.", flush=True); return 3
    c0 = set(ctls())
    r3 = step("3 create_control on IA.index", "one new control (label 'index 2')", lambda: g.create_control(OP, n_ia, t_ix))
    purge()
    idx2 = [l for l in ctls() if l not in c0]
    print(f"   index control label(s): {idx2}", flush=True)
    if len(idx2) != 1:
        print("STOP: index control not created uniquely.", flush=True); return 3
    IDX2 = idx2[0]

    u_cn = step("4 PN_CN GObject[Class Name] <- IA.element", "Property +1", lambda: pn("VI Server:GObject", P_CLASSNAME, (1550, 1150)))
    if not u_cn:
        return 3
    step("4-wire", "Wire +1", lambda: (g.wire(OP, "IndexArray", idx("IndexArray", ia_uid), "element", "Property", idx("Property", u_cn), "reference"), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after PN_CN.", flush=True); return 3
    u_ot = step("5 PN_OT Tunnel[Outside Terminal] <- PN_CN ref out", "Property +1, ExecState 1 (element is a Tunnel subclass)",
                lambda: pn("VI Server:Tunnel", P_OUTER, (1800, 1150)))
    if not u_ot:
        return 3
    step("5-wire", "Wire +1, ExecState 1", lambda: (g.wire(OP, "Property", idx("Property", u_cn), "reference out", "Property", idx("Property", u_ot), "reference"), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: Shift Registers[] elements are NOT accepted by a Tunnel-class node (element type not a Tunnel) - recorded, nothing saved.", flush=True); return 4
    T_OUT = data_term(u_ot)
    u_on = step("6a PN_ON Terminal[Name]", "Property +1", lambda: pn("VI Server:Terminal", P_NAME, (2050, 1150)))
    step("6a-wire OT.outer -> ON.ref", "Wire +1, ExecState 1", lambda: (g.wire(OP, "Property", idx("Property", u_ot), T_OUT, "Property", idx("Property", u_on), "reference"), snap("after"))[1])
    u_os = step("6b PN_OS Terminal[Is Source?]", "Property +1", lambda: pn("VI Server:Terminal", P_ISSRC, (2300, 1150)))
    u_oc = step("6c PN_OC Terminal[Connected Wire]", "Property +1", lambda: pn("VI Server:Terminal", P_CONNW, (2550, 1150)))
    u_ow = step("6d PN_OW GObject[UID]", "Property +1", lambda: pn("VI Server:GObject", P_UID, (2800, 1150)))
    if not (u_on and u_os and u_oc and u_ow):
        return 3
    step("6e ON -> OS -> OC -> OW wires", "Wire +3, ExecState 1",
         lambda: ([g.wire(OP, "Property", idx("Property", u_on), "reference out", "Property", idx("Property", u_os), "reference"),
                   g.wire(OP, "Property", idx("Property", u_os), "reference out", "Property", idx("Property", u_oc), "reference"),
                   g.wire(OP, "Property", idx("Property", u_oc), "Wire", "Property", idx("Property", u_ow), "reference")], snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: outer chain broken.", flush=True); return 3
    u_it = step("7 PN_IT Tunnel[Inside Terminals[]] <- PN_OT ref out", "Property +1", lambda: pn("VI Server:Tunnel", P_INSIDE, (1800, 1350)))
    if not u_it:
        return 3
    step("7-wire", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", u_ot), "reference out", "Property", idx("Property", u_it), "reference"), snap("after"))[1])
    T_INS = data_term(u_it)
    # Run 1 (build_opshiftregs_v0.log 15:2x): the new body was picked by INDEX difference and the inner node landed
    # in the donor's OLD loop (Traverse re-ordered the diagrams) - the new loop stayed empty -> ExecState 0.
    # Identify the new body by its Diagram UID and verify by census that the new loop gets the tunnel.
    dia_uids0 = {d["uid"] for d in g.report_all(OP, "Diagram")}
    loops0 = {o["uid"] for o in g.report_all(OP, "ForLoop")}
    step("8a For loop (top level)", "ForLoop +1", lambda: (g.for_loop(OP, (2050, 1350)), snap("after"))[1])
    new_dias = [(i, d) for i, d in enumerate(g.report_all(OP, "Diagram")) if d["uid"] not in dia_uids0]
    new_loop = [u for u in {o["uid"] for o in g.report_all(OP, "ForLoop")} if u not in loops0]
    print(f"   new diagram(s) {[(i, d['uid'], d.get('owner')) for i, d in new_dias]}; new loop {new_loop}", flush=True)
    if len(new_dias) != 1 or len(new_loop) != 1:
        print("STOP: new loop body / loop not unique.", flush=True); return 3
    body = new_dias[0][0]; body_uid = new_dias[0][1]["uid"]

    def body_index():
        return next(i for i, d in enumerate(g.report_all(OP, "Diagram")) if d["uid"] == body_uid)
    u_in = step("8b PN_IN Terminal[Name] inside the NEW body", "Property +1; the node is listed in that diagram",
                lambda: pn("VI Server:Terminal", P_NAME, (2100, 1400), body_index()))
    in_body = [r["uid"] for r in g.node_labels(OP, body_index())]
    print(f"   nodes in the new body: {in_body} (PN_IN {u_in} in it: {u_in in in_body})", flush=True)
    if u_in not in in_body:
        print("STOP: PN_IN did not land in the new loop's body - recorded, nothing saved.", flush=True); return 3
    tun_in0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    step("8c PN_IT array -> PN_IN.ref (crosses)", "LoopTunnel +1, ExecState 1", lambda: (g.wire(OP, "Property", idx("Property", u_it), T_INS, "Property", idx("Property", u_in), "reference"), snap("after"))[1])
    purge()
    # peer (…fail1-loop-body-index.md): inspect the new tunnel's indexing instead of assuming it (alternative a)
    new_t = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun_in0]
    for o in new_t:
        t = g.tunnels(OP, o["i"])
        print(f"   new input tunnel index {o['i']} uid {o['uid']} owner {o.get('owner')}: {t}", flush=True)
        if t.get("index_mode") != 1:
            print("   index mode != 1 -> set_index_mode(1) and re-check ExecState", flush=True)
            g.set_index_mode(OP, o["i"], 1)
    if g.exec_state(OP) != 1:
        print(f"STOP: still ExecState 0 after the loop input (new tunnels {[(o['i'], o['uid']) for o in new_t]}) - recorded.", flush=True); return 3
    body = body_index()
    u_is = step("8d PN_IS inside", "Property +1", lambda: pn("VI Server:Terminal", P_ISSRC, (2300, 1400), body_index()))
    u_ic = step("8e PN_IC inside", "Property +1", lambda: pn("VI Server:Terminal", P_CONNW, (2500, 1400), body_index()))
    u_iw = step("8f PN_IW inside", "Property +1", lambda: pn("VI Server:GObject", P_UID, (2700, 1400), body_index()))
    if not (u_is and u_ic and u_iw):
        return 3
    step("8g inner chain wires", "Wire +3, ExecState 1",
         lambda: ([g.wire(OP, "Property", idx("Property", u_in), "reference out", "Property", idx("Property", u_is), "reference"),
                   g.wire(OP, "Property", idx("Property", u_is), "reference out", "Property", idx("Property", u_ic), "reference"),
                   g.wire(OP, "Property", idx("Property", u_ic), "Wire", "Property", idx("Property", u_iw), "reference")], snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: inner chain broken.", flush=True); return 3
    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    meanings = ["InName", "InIsSource", "InWireUID"]
    for u, outs in ((u_in, ["Name"]), (u_is, ["IsSource"]), (u_iw, ["UID"])):
        step(f"8h exit_loop {outs}", "LoopTunnel +1", lambda u=u, outs=outs: (g.exit_loop(OP, idx("Property", u), outs, body, node_class="Property"), snap("after"))[1])
    for u, tag in ((u_ic, "InConnErr"), (u_iw, "InWireErr")):
        try:
            g.exit_loop(OP, idx("Property", u), ["error out"], body, node_class="Property"); meanings.append(tag)
        except Exception as e:
            print(f"   optional: {tag} not tunnelled ({str(e)[:80]})", flush=True)
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True); return 4
    # inherit the donor's labels (ShiftRegUIDs array, LoopUID, ShiftRegsErr, seed) - the wrapper reads them too
    with open(os.path.join(os.path.dirname(HERE), "bench", "opwhilecast_labels.json"), encoding="utf-8") as f:
        label_map = json.load(f)
    out_tuns = [o["i"] for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
    for k, tun in enumerate(out_tuns):
        before = set(inds())
        try:
            g.set_index_mode(OP, tun, 1)
        except Exception as e:
            print(f"   tunnel {tun}: set_index_mode {str(e)[:100]}", flush=True)
        try:
            g.tunnel_indicator(OP, tun)
        except Exception as e:
            print(f"   tunnel {tun}: tunnel_indicator FAILED {str(e)[:150]}", flush=True); continue
        for l in [l for l in inds() if l not in before]:
            label_map[l] = meanings[k] if k < len(meanings) else f"tunnel {tun}"
            print(f"   tunnel {tun} -> {l!r} = {label_map[l]}", flush=True)
    for uid, term, meaning in ((u_cn, data_term(u_cn), "ClassName"), (u_ow, "UID", "OutWireUID"), (u_on, data_term(u_on), "OutName"),
                               (u_os, data_term(u_os), "OutIsSource"), (u_ot, "error out", "OuterErr"), (u_oc, "error out", "OutConnErr"),
                               (u_it, "error out", "InsideErr")):
        try:
            label_map[make_indicator(uid, term)] = meaning
        except Exception as e:
            print(f"   indicator {meaning}: EXC {str(e)[:150]}", flush=True)
    label_map[IDX2] = "index2"
    step("10 auto error handling OFF", "no dialog", lambda: g.set_auto_error_handling(OP, False))
    purge(); es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True); print("label map:", json.dumps(label_map), flush=True)
    need = {"InName", "InIsSource", "InWireUID", "ClassName", "OutWireUID", "OutName", "OutIsSource", "index2"}
    if es != 1 or not need <= set(label_map.values()):
        print(f"\nVERDICT: BROKEN (ExecState {es}, missing {need - set(label_map.values())}) - NOT SAVING.", flush=True); return 4
    step("11 COM save", "written", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("\nVERDICT: OpShiftRegs_v0 BUILT and SAVED (structural only - run tools/bench/test_opshiftregs.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
