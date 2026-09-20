"""build_oploopcast_v0.py - OpLoopCast_v0.vi: a ForLoop-TYPED reference to the `index`-th For loop of a VI, cast-free,
and through it the loop's N wire and shift registers.

THE SEED. To More Specific Class needs a 'target class' of the wanted type; we cannot make a class-specifier
constant (docs/toolkit-capabilities.md 'the one missing seed'). But 'target class' is a refnum INPUT: any refnum
WIRE of the wanted class types it. erdosmiller `Create For Loop.vi` has a ForLoop-typed output terminal, and
`Terminal.Create Control` makes a control OF THE TERMINAL'S TYPE - so: drop the VI, create a control from that
output, delete the VI (the control stays), wire the control into 'target class'. Plan review:
archive/peer/2026-09-14-loopcast-typed-terminal-seed-plan.md.

DONOR: OpSetIndexMode_v0.vi (Traverse(Class Name, index) -> Index Array -> TMSC(LoopTunnel) -> IndexMode WRITE PN).
STEPS (prediction each; a miss prints EXC/STOP and nothing is saved):
  1  copy, open_panel; delete the IndexMode WRITE PN (+RBW)                                   ExecState 1
  2  walk diagram 0: TMSC = Function with 'target class' + 'specific class reference'; W = its target-class wire
  3  drop Create For Loop.vi; its terminals printed; the ForLoop-typed OUTPUT chosen by name (STOP if ambiguous)
  4  create_control on that terminal -> seed control label L                                  new control
  5  delete the Create For Loop node (+RBW); L still on the panel                             ExecState 1
  6  delete wire W (Wire index by uid)                                                        ExecState 0 or 1
  7  wire_control([L] -> TMSC 'target class')                                                 ExecState 1
  8  PN_U GObject[UID] <- TMSC out (loop UID); PN_LC ForLoop[Loop Count 6362000] <- TMSC out (branch);
     PN_OT Tunnel[Outside Terminal 6356001] <- PN_LC out; PN_CW Terminal[Connected Wire 634A000] <- PN_OT out;
     PN_W GObject[UID] <- PN_CW 'Wire'; PN_SR Loop[Shift Registers[] 6361402] <- TMSC out (branch) -> For loop ->
     PN_SU GObject[UID] inside -> exit_loop -> array indicator (shift-register UIDs)
  9  scalar indicators: PN_U.UID, PN_W.UID, PN_LC.error out, PN_CW.error out, PN_SR.error out
 10  auto error handling OFF; ExecState 1 -> save; labels -> tools/bench/oploopcast_labels.json
Run-time inputs: 'Class Name' = 'ForLoop' (or 'WhileLoop'), 'index' = Traverse index of the loop.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_oploopcast_v0.log -- py -u tools/recipes/build_oploopcast_v0.py
"""
import hashlib
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpSetIndexMode_v0.vi")
# argv[1]: 'ForLoop' (default) -> OpLoopCast_v0 (seed from NI's For Loop example; N-wire chain + shift registers)
#          'WhileLoop'          -> OpWhileCast_v0 (seed from NI's While Loop example; shift registers only - a
#                                  ForLoop-typed seed cannot cast a WhileLoop ref: test_oploopcast.log T3, error 1055)
CLASS = sys.argv[1] if len(sys.argv) > 1 else "ForLoop"
EXDIR = r"C:\Program Files\National Instruments\LabVIEW 2026\examples\Application Control\VI Scripting\Structures"
EX = os.path.join(EXDIR, {"ForLoop": "VI Scripting with Structures - For Loop.vi",
                          "WhileLoop": "VI Scripting with Structures - While Loop.vi"}[CLASS])
OP = os.path.join(g.CLAUDEDEV, {"ForLoop": "OpLoopCast_v0.vi", "WhileLoop": "OpWhileCast_v0.vi"}[CLASS])
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_loopcast_seed_{os.getpid()}.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", {"ForLoop": "oploopcast_labels.json", "WhileLoop": "opwhilecast_labels.json"}[CLASS])
P_UID, P_LOOPCOUNT, P_OUTER, P_CONNW, P_SHIFTREGS = "632A813", "6362000", "6356001", "634A000", "6361402"
T_CAST_OUT = "specific class reference"
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
    return (f"{tag} SubVI={len(g.report_all(OP, 'SubVI'))} Function={len(g.report_all(OP, 'Function'))} "
            f"Property={len(g.report_all(OP, 'Property'))} Wire={len(g.report_all(OP, 'Wire'))} "
            f"ForLoop={len(g.report_all(OP, 'ForLoop'))} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def ctls():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if not is_ind and lab]


def idx(cls, uid):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def walk(diagram=0, max_nodes=60):
    return g.net_map(OP, diagram, max_nodes=max_nodes, max_terms=24)[0]


def node_terms_of(uid, diagram=0):
    for cand in range(60):
        nu, rows = g.node_terms_uid(OP, diagram, cand)
        if not nu:
            return None, None
        if nu == uid:
            return cand, rows
    return None, None


def make_indicator(uid, term_name, diagram=0):
    n, rows = node_terms_of(uid, diagram)
    t = next(r["i"] for r in rows if r["name"] == term_name)
    before = set(inds())
    g.create_indicator(OP, n, t)
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

    # 1 delete the IndexMode WRITE PN
    w0 = walk()
    pn_w = next((u for _n, (u, _l, terms) in w0.items() if any(t == "IndexMode" and not_src for _ti, t, _w in terms for not_src in [True])
                 and u in {o["uid"] for o in g.report_all(OP, "Property")}), None)
    print(f"   IndexMode WRITE PN uid {pn_w}", flush=True)
    if pn_w is None:
        print("STOP: donor's IndexMode PN not found.", flush=True); return 2
    step("1 delete IndexMode PN + RBW", "Property -1, ExecState 1",
         lambda: (g.delete_object(OP, "Property", idx("Property", pn_w)), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after deleting the write PN.", flush=True); return 2

    # 2 the TMSC and its target-class wire
    purge(); w1 = walk()
    tmsc = next(((u, terms) for _n, (u, _l, terms) in w1.items()
                 if any(t == "target class" for _ti, t, _w in terms) and any(t == T_CAST_OUT for _ti, t, _w in terms)), None)
    if tmsc is None:
        print("STOP: TMSC not found.", flush=True); return 2
    tmsc_uid, tmsc_terms = tmsc
    W = next(w for _ti, t, w in tmsc_terms if t == "target class")
    print(f"   TMSC uid {tmsc_uid}; 'target class' wire uid {W}", flush=True)
    if not W:
        print("STOP: TMSC target class already unwired in the donor?", flush=True); return 2

    # 3 THE SEED (attempt 2, peer archive/peer/2026-09-14-loopcast-seed-from-ni-example.md): NI's example
    # 'VI Scripting with Structures - For Loop.vi' = one ForLoop class constant (uid 183) wired (one wire) to five
    # ForLoop property nodes (LpCounter, LpCount, HasConditionalTerm, Diagram, LpEndRef; probe_example_forloop.log).
    # On a SCRATCH copy: delete that wire, Terminal.Create Control on the LpCount node's 'reference' INPUT (the
    # documented Create-Control-on-input operation; the control takes the terminal's ForLoop refnum type), then
    # copy_into(scratch, label, OP) moves the labelled control onto the op. copy_into byte-substitutes files, so the
    # op is saved and closed first and reopened after.
    step("3-save op before copy_into", "saved, panel closed", lambda: (g.save(OP), g.close_panel(OP)))
    shutil.copyfile(EX, S); time.sleep(0.3); g.open_panel(S); time.sleep(0.8)
    inv0s = g.uids(S, "Invoke")

    def purge_s():
        junk = [u for u in g.uids(S, "Invoke") if u not in inv0s]
        if junk:
            order = [o["uid"] for o in g.report_all(S, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(S, "Invoke", i, verify=False)
    # the seed node = a property node whose 'reference' input is wired (from the class constant); ForLoop: the
    # LpCount node (probe_example_forloop.log); WhileLoop: the first such property node of the While example.
    n_lc = None; w_ref = 0; u_lc = None
    prop_uids = {o["uid"] for o in g.report_all(S, "Property")}
    for cand in range(12):
        nu, rows = g.node_terms_uid(S, 0, cand)
        if not nu:
            break
        names = {r["name"]: r for r in rows}
        print(f"   example node {cand} uid {nu}: {[(r['i'], r['name'], r['wire']) for r in rows]}", flush=True)
        if nu in prop_uids and "reference" in names and names["reference"]["wire"]:
            if CLASS == "ForLoop" and "LpCount" not in names:
                continue
            if n_lc is None:
                n_lc = cand; w_ref = names["reference"]["wire"]; u_lc = nu
    print(f"   scratch example: seed property node Nodes[] {n_lc} uid {u_lc}, its 'reference' wire {w_ref}", flush=True)
    if n_lc is None or not w_ref:
        print("STOP: LpCount node / its reference wire not found on the example copy. Nothing saved.", flush=True); os.remove(S); return 3
    wires_s = [o["uid"] for o in g.report_all(S, "Wire")]
    step("3b delete the class-constant wire on the scratch", "Wire -1 (the five reference inputs become unwired)",
         lambda: (g.delete_object(S, "Wire", wires_s.index(w_ref)), len(g.report_all(S, 'Wire')))[1])
    c0 = {l for _i, l, ind in g.fp_labels(S) if not ind}
    r3 = step("3c create_control on LpCount node 'reference' (input, ForLoop-typed)", "one new CONTROL on the scratch panel",
              lambda: g.create_control(S, n_lc, 0))
    purge_s()
    new_c = [l for _i, l, ind in g.fp_labels(S) if not ind and l not in c0]
    print(f"   create_control returned {r3}; new controls {new_c}", flush=True)
    if len(new_c) != 1:
        print("STOP: no unique seed control created on the scratch - recorded, nothing saved.", flush=True)
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S); return 3
    seed = new_c[0]
    # the other four property nodes now have unwired (required) reference inputs = broken VI; a broken VI cannot be
    # saved over COM (and a GUI save is forbidden) - delete them, keep LpCount PN <- seed control, then COM-save.
    others = [o["uid"] for o in g.report_all(S, "Property") if o["uid"] != u_lc]
    step("3d delete the four other property nodes on the scratch + RBW", f"Property 5->1, ExecState 1 ({len(others)} deleted)",
         lambda: ([g.delete_object(S, "Property", [o["uid"] for o in g.report_all(S, "Property")].index(u), verify=False) for u in others],
                  g.remove_bad_wires_scripted(S), g.exec_state(S))[2])
    purge_s()
    if g.exec_state(S) != 1:
        print("STOP: scratch not runnable after trimming (seed control not wired to LpCount?). Nothing saved.", flush=True)
        try:
            g.close_panel(S)
        except Exception:
            pass
        os.remove(S); return 3
    g.save(S)
    try:
        g.close_panel(S)
    except Exception:
        pass
    c0op = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    r3e = step("3e copy_into(scratch, seed, op)", "one new GObject on the op; the seed label on its panel",
               lambda: g.copy_into(S, seed, OP))
    os.remove(S)
    g.open_panel(OP); time.sleep(0.8)
    new_op = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in c0op]
    print(f"   op panel new controls: {new_op}; {snap('after')}", flush=True)
    if seed not in new_op:
        print("STOP: seed control did not arrive on the op. Nothing saved.", flush=True); return 3
    seed_is_ind = False
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: op broken after copy_into (unexpected). Nothing saved.", flush=True); return 3

    # 6 delete the class-constant wire W
    wires = [o["uid"] for o in g.report_all(OP, "Wire")]
    if W not in wires:
        print("STOP: wire W not in the Wire census.", flush=True); return 3
    step("6 delete the TMSC target-class wire", "Wire -1", lambda: (g.delete_object(OP, "Wire", wires.index(W)), snap("after"))[1])

    # 7 seed -> target class
    if seed_is_ind:
        print("STOP: the seed is an INDICATOR (sink) - cannot source 'target class'; need the control variant. Nothing saved.", flush=True); return 3
    step("7 wire_control seed -> TMSC 'target class'", "Wire +1, ExecState 1",
         lambda: (g.wire_control(OP, [seed], "Function", idx("Function", tmsc_uid), ["target class"]), snap("after"))[1])
    purge()
    if g.exec_state(OP) != 1:
        print("STOP: not runnable with the seed as target class (claim refuted or wire declined). Nothing saved.", flush=True)
        n, rows = node_terms_of(tmsc_uid); print("   TMSC terminals:", [(r['i'], r['name'], r['wire']) for r in rows], flush=True)
        return 4

    # 8 the typed chain
    def pn(cls, pid, pos, diagram=0):
        r = g.build_property(OP, cls, [(pid, False)], pos, diagram_index=diagram); purge(); return r[-1]["uid"]
    u_U = step("8a PN_U GObject[UID] <- TMSC out", "Property +1", lambda: pn("VI Server:GObject", P_UID, (900, 650)))
    step("8a-wire", "Wire +1", lambda: (g.wire(OP, "Function", idx("Function", tmsc_uid), T_CAST_OUT, "Property", idx("Property", u_U), "reference", branch=True), snap("after"))[1])
    u_LC = u_CW = u_W = None
    if CLASS == "ForLoop":
        u_LC = step("8b PN_LC ForLoop[Loop Count] <- TMSC out (branch)", "Property +1 (class ForLoop accepted)", lambda: pn("VI Server:ForLoop", P_LOOPCOUNT, (900, 800)))
        if not u_LC:
            print("STOP: ForLoop-class property node not creatable. Nothing saved.", flush=True); return 4
        step("8b-wire", "Wire +1, ExecState 1 (the cast output IS ForLoop-typed)",
             lambda: (g.wire(OP, "Function", idx("Function", tmsc_uid), T_CAST_OUT, "Property", idx("Property", u_LC), "reference", branch=True), snap("after"))[1])
        if g.exec_state(OP) != 1:
            print("STOP: ForLoop property node rejects the cast output - the seed did not type the TMSC. Nothing saved.", flush=True); return 4
        n, rows = node_terms_of(u_LC); t_lc = next(r["name"] for r in rows if r["i"] == 4)
        print(f"   PN_LC data terminal name: {t_lc!r}", flush=True)
        u_OT = step("8c PN_OT Tunnel[Outside Terminal] <- PN_LC out", "Property +1", lambda: pn("VI Server:Tunnel", P_OUTER, (1200, 800)))
        step("8c-wire", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", u_LC), t_lc, "Property", idx("Property", u_OT), "reference"), snap("after"))[1])
        n, rows = node_terms_of(u_OT); t_ot = next(r["name"] for r in rows if r["i"] == 4)
        u_CW = step("8d PN_CW Terminal[Connected Wire] <- PN_OT out", "Property +1", lambda: pn("VI Server:Terminal", P_CONNW, (1500, 800)))
        step("8d-wire", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", u_OT), t_ot, "Property", idx("Property", u_CW), "reference"), snap("after"))[1])
        n, rows = node_terms_of(u_CW); t_cw = next(r["name"] for r in rows if r["i"] == 4)
        u_W = step("8e PN_W GObject[UID] <- PN_CW 'Wire'", "Property +1", lambda: pn("VI Server:GObject", P_UID, (1800, 800)))
        step("8e-wire", "Wire +1", lambda: (g.wire(OP, "Property", idx("Property", u_CW), t_cw, "Property", idx("Property", u_W), "reference"), snap("after"))[1])
    u_SR = step("8f PN_SR Loop[Shift Registers[]] <- TMSC out (branch)", "Property +1 (class Loop accepted)", lambda: pn("VI Server:Loop", P_SHIFTREGS, (900, 950)))
    step("8f-wire", "Wire +1", lambda: (g.wire(OP, "Function", idx("Function", tmsc_uid), T_CAST_OUT, "Property", idx("Property", u_SR), "reference", branch=True), snap("after"))[1])
    n, rows = node_terms_of(u_SR); t_sr = next(r["name"] for r in rows if r["i"] == 4)
    step("8g For loop", "ForLoop +1", lambda: (g.for_loop(OP, (1300, 950)), snap("after"))[1])
    body = next(i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner")))
    u_SU = step("8h PN_SU GObject[UID] inside", "Property +1", lambda: pn("VI Server:GObject", P_UID, (1350, 1000), body))
    step("8h-wire (crosses the loop)", "LoopTunnel +1, ExecState 1",
         lambda: (g.wire(OP, "Property", idx("Property", u_SR), t_sr, "Property", idx("Property", u_SU), "reference"), snap("after"))[1])
    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    step("8i exit_loop PN_SU ['UID']", "LoopTunnel +1", lambda: (g.exit_loop(OP, idx("Property", u_SU), ["UID"], body, node_class="Property"), snap("after"))[1])
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True); return 4
    label_map = {}
    for tun in [o["i"] for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]:
        before = set(inds()); g.set_index_mode(OP, tun, 1); g.tunnel_indicator(OP, tun)
        for l in [l for l in inds() if l not in before]:
            label_map[l] = "ShiftRegUIDs"
    # 9 scalar indicators
    wanted = [(u_U, "UID", "LoopUID"), (u_W, "UID", "NWireUID"), (u_LC, "error out", "LoopCountErr"),
              (u_CW, "error out", "ConnWireErr"), (u_SR, "error out", "ShiftRegsErr")]
    wanted = [w for w in wanted if w[0]]
    for uid, term, meaning in wanted:
        try:
            label_map[make_indicator(uid, term)] = meaning
        except Exception as e:
            print(f"   indicator {meaning}: EXC {str(e)[:150]}", flush=True)
    label_map[seed] = "seed"
    step("10 auto error handling OFF", "no dialog", lambda: g.set_auto_error_handling(OP, False))
    purge(); es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True); print("label map:", json.dumps(label_map), flush=True)
    if es != 1 or len([k for k, v in label_map.items() if v != "seed"]) != len(wanted) + 1:
        print(f"\nVERDICT: BROKEN (ExecState {es}, labels {label_map}) - NOT SAVING.", flush=True); return 4
    step("11 COM save", "written", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"\nVERDICT: {os.path.basename(OP)} BUILT and SAVED (structural only - run tools/bench/test_oploopcast.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
