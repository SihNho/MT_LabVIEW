r"""diag_c97_tools_t124.py - card 97-2: MEASURE the composed routes for T1 (nested case create), T2 (move nodes into a
case frame, wires kept) and T4 (control label + I32 default) on a SCRATCH fixture built here (For inside While, a chain
of three error-cluster subVIs in the For body). Nothing but scratch_c97_* files is edited; the fixture is deleted.

PRIOR ART (checked before writing): build_case (gscript.py:3173, top-level only, OpBuildCase_v1); move_in
(build_d1_v0.py:318, OpMoveIn_v0, uid-addressed; moved a For loop into a body in build_opconnectnested_v1 T3; SEVERS
wires, cycle27-plan.md:846-851); connect_nested_v1 (build_opconnectnested_v1.py:418, both ends by Diagram/Nodes/Terms
index, LabVIEW makes the border tunnels itself, toolkit-capabilities.md:73); allterms.read_terms (whole-VI terminal
table); owner_of (build_d1_v0.py:338); set_node_label (gscript.py:2952, OpSetLabel_v0); make_default
(gscript.py ~3120, OpMakeDefault_v0 + save). The fixture shape is build_opconnectnested_v1.test():457-500. No existing
small VI has For-inside-While with a node chain (diag_c97_tools_fixprobe.log:3-29). NO NEW OP VI IS BUILT HERE.
This file does not import stagekit (gscript-level diagnostic like build_opconnectnested_v1.test); it touches only
scratch_c97_* copies it creates and deletes.

PREDICTIONS (gates):
 F  fixture: 1 While, 1 For owned by the While body, 3 subVIs owned by the For body, 2 chain wires.
 T1 build_case on top level + move_in -> CaseStructure owner == the body diagram uid (For body AND While body); its 2
    frame Diagrams owned by the case. Negative: move_in to a Diagram index past the end leaves the owner unchanged.
 T2 E2 moved into frame 0 of the case in the For body; the 2 severed edges re-made with connect_nested_v1; the edge
    table (src uid:term -> sink uid:term) with NEW tunnels collapsed == the table before; census: only Tunnel-class
    objects (and wires) added. Negative: a node whose owner is NOT the case's owner diagram is refused before any edit.
 T4 an I32 control created from a For N terminal; set_node_label on its terminal (moved to a nested diagram, since
    OpSetLabel addresses Traverse('Diagram')) changes the PANEL label; a separate runnable fixture gets default 9 by
    make_default, read back after a close/reopen. Handles over 20 set_node_label calls flat (+-100).
"""
import json, os, shutil, subprocess, sys, time  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))  # noqa: E702
import gscript as g  # noqa: E402
import protocol as P  # noqa: E402
import allterms as A  # noqa: E402
import bench_prep as BP  # noqa: E402
import build_d1_v0 as B  # noqa: E402
import build_opconnectnested_v1 as CN  # noqa: E402
g._run.__defaults__ = (6.0, 120.0)
TS = time.strftime("%Y%m%d_%H%M%S")
FIX = os.path.join(g.CLAUDEDEV, "scratch_c97_fix_%s.vi" % TS)
FIX4 = os.path.join(g.CLAUDEDEV, "scratch_c97_fix4_%s.vi" % TS)
S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
OUT = os.path.join(HERE, "diag_c97_tools_t124.json")
CNL = json.load(open(CN.MAP_OUT, encoding="utf-8"))
PASS, FAIL, R = [], [], {"facts": []}


def gate(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)
    return ok


def fact(s):
    R["facts"].append(s); print("  FACT  " + str(s)[:400], flush=True)  # noqa: E702


def md5(p):
    import hashlib
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def didx(t, uid):
    return [int(o["uid"]) for o in g.report_all(t, "Diagram")].index(int(uid))


def nidx(t, di, uid):
    return [int(r["uid"]) for r in g.node_labels(t, di)].index(int(uid))


def term(t, di, uid, name_part, src):
    _u, rows = g.node_terms_uid(t, di, nidx(t, di, uid))
    hits = [r for r in rows if bool(r["is_source"]) == src and name_part in (r["name"] or "")]
    return hits[0]["i"]


def owner(t, uid):
    return B.owner_of(t, int(uid), strict=False)


def edges(t, collapse=()):
    rows, _s = A.read_terms(t)
    byw = {}
    for r in rows:
        if r["wire_uid"]:
            byw.setdefault(r["wire_uid"], []).append(r)
    E = set()
    for rs in byw.values():
        for s in [r for r in rs if r["is_source"]]:
            for k in [r for r in rs if not r["is_source"]]:
                E.add((s["owner_uid"], s["term_name"], k["owner_uid"], k["term_name"]))
    cl = set(collapse)
    for _ in range(6):                                   # a tunnel owner is a pass-through: src->T + T->sink = src->sink
        tun = [e for e in E if e[2] in cl]
        if not tun:
            break
        for e in tun:
            E.discard(e)
            for f in [f for f in E if f[0] == e[2]]:
                E.discard(f); E.add((e[0], e[1], f[2], f[3]))  # noqa: E702
    return E, rows


def census(t):
    return dict((c, g.count(t, c)) for c in ("CaseStructure", "Diagram", "SubVI", "Tunnel", "LoopTunnel", "Wire", "ControlTerminal"))


def fixture():
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi"), FIX); time.sleep(0.4)  # noqa: E702
    g.report_all(FIX, "SubVI"); g.open_panel(FIX); time.sleep(0.6)  # noqa: E702
    d0 = g.uids(FIX, "Diagram"); g.while_loop(FIX, (300, 300))  # noqa: E702
    DW = g.new_since(FIX, "Diagram", d0)[0]["uid"]; W = sorted(g.uids(FIX, "WhileLoop"))[0]  # noqa: E702  (uids() is a SET)
    d1 = g.uids(FIX, "Diagram"); g.loop_in("for", FIX, didx(FIX, DW), (40, 40))  # noqa: E702
    DF = g.new_since(FIX, "Diagram", d1)[0]["uid"]; F = sorted(g.uids(FIX, "ForLoop"))[0]  # noqa: E702
    E = []
    for x in (40, 240, 440):
        s0 = g.uids(FIX, "SubVI"); g.drop_subvi(FIX, CN.NUMVI, didx(FIX, DF), (x, 60))  # noqa: E702
        E.append(g.new_since(FIX, "SubVI", s0)[0]["uid"])
    di = didx(FIX, DF)
    for a, b in ((E[0], E[1]), (E[1], E[2])):
        CN.connect_nested_v1(FIX, di, nidx(FIX, di, b), term(FIX, di, b, "error in", False),
                             di, nidx(FIX, di, a), term(FIX, di, a, "error out", True), CNL)
    return W, DW, F, DF, E


def body():
    gate("K S1 md5 before", md5(S1) == S1_MD5, md5(S1))
    BP.restart_labview(); g.reset(); time.sleep(3)  # noqa: E702
    h0 = BP.labview_handles(); fact("handles after restart %r" % h0)
    W, DW, F, DF, E = fixture()
    fact("fixture W#%s body#%s F#%s body#%s E=%r ES=%s" % (W, DW, F, DF, E, g.exec_state(FIX)))
    gate("F For is owned by the While body", owner(FIX, F)[1] == DW, owner(FIX, F))
    gate("F 3 subVIs owned by the For body", all(owner(FIX, e)[1] == DF for e in E), [owner(FIX, e) for e in E])
    E0, _r = edges(FIX)
    chain = {(E[0], "error out", E[1]), (E[1], "error out", E[2])}
    gate("F chain wires present", chain <= set((a, b, c) for a, b, c, _d in E0), sorted(E0))
    tl = [int(o["uid"]) for o in g.report_all(FIX, "Diagram")]
    fact("Traverse('Diagram') uids %r (TopLevelDiagram included? %s)" % (tl, 3 in tl))
    # ---- selector control: an I32 control on a TOP-LEVEL temporary For loop's N (for_loop + create_control)
    f0 = g.uids(FIX, "ForLoop"); g.for_loop(FIX, (1400, 300))  # noqa: E702
    FT = g.new_since(FIX, "ForLoop", f0)[0]["uid"]
    info = g.node_info(FIX)
    fact("top-level nodes %r" % (info,))
    lab0 = set(l for _i, l, _d in g.fp_labels(FIX))
    ni = [t[0] for t in info if "For Loop" in str(t[1])][-1]
    fact("top-level node index of FT#%s = %r" % (FT, ni))
    g.create_control(FIX, ni, 0)
    newlab = sorted(set(l for _i, l, _d in g.fp_labels(FIX)) - lab0)
    gate("T4a one new I32 control from For N", len(newlab) == 1, newlab)
    SEL = newlab[0] if newlab else None
    # ---- T1: build_case on the top level, then move_in into (a) the For body (b) the While body
    cases = {}
    for tag, D in (("for", DF), ("while", DW)):
        c0, dg0 = g.uids(FIX, "CaseStructure"), g.uids(FIX, "Diagram")
        cs = g.build_case(FIX, (1400, 700 if tag == "for" else 1100), SEL)["uid"]
        frames = [o["uid"] for o in g.new_since(FIX, "Diagram", dg0)]
        r = B.move_in(FIX, cs, didx(FIX, D), (300, 150))
        g.remove_bad_wires_scripted(FIX)
        oc = owner(FIX, cs)
        fo = [owner(FIX, f) for f in frames]
        cases[tag] = (cs, frames)
        fact("T1 %s: case #%s move_in returned %r; owner %r; frames %r owners %r" % (tag, cs, r, oc, frames, fo))
        gate("T1 %s-body case owner == Diagram#%s" % (tag, D), oc[1] == D, oc)
        gate("T1 %s-body case has 2 frame Diagrams owned by it" % tag, len(frames) == 2 and all(x[1] == cs for x in fo), fo)
    cs_bad = cases["while"][0]
    ob = owner(FIX, cs_bad); n = len(g.report_all(FIX, "Diagram"))
    B.move_in(FIX, cs_bad, n + 5, (10, 10))
    gate("T1 NEG move_in to Diagram index past the end leaves the owner unchanged", owner(FIX, cs_bad) == ob, (ob, owner(FIX, cs_bad)))
    # ---- T2: move E2 into frame 0 of the For-body case, re-make the severed edges, compare tables
    cs, frames = cases["for"]
    fr = frames[0]
    before_c = census(FIX); T0 = set(g.uids(FIX, "Tunnel"))
    Eb, _r = edges(FIX)
    cut = [e for e in Eb if E[1] in (e[0], e[2])]
    fact("T2 cut set (edges touching E2#%s): %r" % (E[1], sorted(cut)))
    ok_owner = owner(FIX, E[1])[1] == owner(FIX, cs)[1]
    gate("T2 precondition: E2 and the case share an owner diagram", ok_owner, (owner(FIX, E[1]), owner(FIX, cs)))
    B.move_in(FIX, E[1], didx(FIX, fr), (60, 60))
    gate("T2 E2 now owned by frame #%s" % fr, owner(FIX, E[1])[1] == fr, owner(FIX, E[1]))
    for (su, st, ku, kt) in cut:
        ds, dk = owner(FIX, su)[1], owner(FIX, ku)[1]
        di_s, di_k = didx(FIX, ds), didx(FIX, dk)
        r = CN.connect_nested_v1(FIX, di_k, nidx(FIX, di_k, ku), term(FIX, di_k, ku, kt, False),
                                 di_s, nidx(FIX, di_s, su), term(FIX, di_s, su, st, True), CNL)
        fact("T2 reconnect #%s:%s -> #%s:%s -> (wire delta, ES, err) %r" % (su, st, ku, kt, r))
    newT = set(g.uids(FIX, "Tunnel")) - T0
    Ea, _r = edges(FIX, collapse=newT)
    after_c = census(FIX)
    fact("T2 new tunnels %r; census before %r after %r" % (sorted(newT), before_c, after_c))
    gate("T2 edge table (new tunnels collapsed) == table before", Ea == Eb, {"missing": sorted(Eb - Ea), "extra": sorted(Ea - Eb)})
    diffc = dict((k, after_c[k] - before_c[k]) for k in before_c if after_c[k] != before_c[k])
    gate("T2 census: only Tunnel (+Wire) counts changed", set(diffc) <= {"Tunnel", "Wire"} and diffc.get("Tunnel", 0) >= 1, diffc)
    ok_neg = owner(FIX, E[0])[1] == owner(FIX, cases["while"][0])[1]
    gate("T2 NEG E1 (owner For body) vs the While-body case: owner check refuses (no edit made)", not ok_neg,
         (owner(FIX, E[0]), owner(FIX, cases["while"][0])))
    # ---- T4 label: move the control terminal into the While body (a Traverse('Diagram') member), write its label
    ct = [int(o["uid"]) for o in g.report_all(FIX, "ControlTerminal")]
    fact("ControlTerminals %r" % ct)
    if ct:
        B.move_in(FIX, ct[-1], didx(FIX, DW), (20, 300))
        di = didx(FIX, DW)
        hs = []
        for k in range(20):
            g.set_node_label(FIX, di, nidx(FIX, di, ct[-1]), "gate N %d" % k)
            hs.append(BP.labview_handles())
        labs = [l for _i, l, _d in g.fp_labels(FIX)]
        gate("T4 panel label now 'gate N 19'", "gate N 19" in labs, labs)
        gate("T4 20 set_node_label calls: handles flat +-100", max(hs) - min(hs) <= 100, (min(hs), max(hs)))
    R["es_fix_end"] = g.exec_state(FIX)
    # ---- T4 default value on a RUNNABLE fixture: EMPTY + top-level For whose N is a new I32 control
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi"), FIX4); time.sleep(0.4)  # noqa: E702
    g.report_all(FIX4, "SubVI"); g.open_panel(FIX4); time.sleep(0.6)  # noqa: E702
    g.for_loop(FIX4, (300, 300))
    n4 = [t[0] for t in g.node_info(FIX4) if "For Loop" in str(t[1])][-1]
    l0 = set(l for _i, l, _d in g.fp_labels(FIX4)); g.create_control(FIX4, n4, 0)  # noqa: E702
    nl = sorted(set(l for _i, l, _d in g.fp_labels(FIX4)) - l0)
    es4 = g.exec_state(FIX4); fact("FIX4 new control %r ES %s" % (nl, es4))  # noqa: E702
    if nl and es4 == 1:
        g.make_default(FIX4, {nl[0]: 9})
        g.close_panel(FIX4); BP.restart_labview(); g.reset(); time.sleep(3)  # noqa: E702
        with g.vi_ref(FIX4) as v:
            got = v.GetControlValue(nl[0])
        gate("T4 default 9 read back after save + LabVIEW restart", int(got) == 9, got)
    else:
        gate("T4 runnable default-value fixture", False, (nl, es4))


try:
    body()
except Exception as e:  # noqa: BLE001
    import traceback
    traceback.print_exc(); FAIL.append("EXC %s" % str(e)[:120])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    for p in (FIX, FIX4):
        for _k in range(4):
            try:
                if os.path.exists(p):
                    os.remove(p)
                break
            except OSError:
                time.sleep(2)
    gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("H LabVIEW gone", gone); gate("H scratch deleted", not os.path.exists(FIX) and not os.path.exists(FIX4))  # noqa: E702
    gate("H S1 md5 unchanged", md5(S1) == S1_MD5)
    R["pass"], R["fail"] = PASS, FAIL
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(PASS), len(FAIL), FAIL))
    print(P.result_line({"status": "PASS" if not FAIL else "FAIL", "gates": {"pass": len(PASS), "fail": len(FAIL)},
                         "first_fail": FAIL[0][:180] if FAIL else None, "artefacts": []}))
