"""build_opconnectctl_v0.py - OpConnectCtl_v0.vi: wire a NODE's terminal to a FRONT-PANEL object's terminal by script.

WHY. erdosmiller's Wire Indicators / Wire Inputs cannot address a Vision IMAQ Image Display control (5001 twice,
2026-09-14; a ControlTerminal is a Terminal, not a Node). Terminal.Connect Wire on the control's own terminal can
(archive/peer/2026-09-14-dispI-controlterminal-route.md). Inputs: vi path, `index` (panel object, Panel.Controls[]
order = fp_labels order), `index 2` (node, Nodes[] order), `index 3` (terminal, Node.Terminals[] order). Output: the
invoke's error out.

DONOR: OpFPLabels_v0 (Open VI Reference -> VI.Front Panel 23D -> Panel.Controls[] 6348801 -> IA(`index`) ->
Control[Label, Indicator] -> Text.Text). Added:
  A  PN_CT Control[Terminal 6332006] <- Control node 'reference out'                 (the SINK, cast-free)
  B  source chain: PN_BD VI.Block Diagram 23C <- Open VI Reference 'vi reference' (branch); PN_N Nodes[] 6375809;
     IA_n; PN_T Node.Terminals[] 6359000; IA_t                                        (the SOURCE, cast-free)
  C  Invoke Terminal.Connect Wire 6349C03: reference <- PN_CT 'Terminal', 'Wire Source' <- IA_t.element
  D  controls on IA_n.index / IA_t.index (create_control), indicator on the invoke's error out
  E  auto error handling OFF; ExecState 1 -> save; labels -> tools/bench/opconnectctl_labels.json
Same construction rules as today's ops: names read off the machine, save only when every step succeeded.
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opconnectctl_v0.log -- py -u tools/recipes/build_opconnectctl_v0.py
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

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnectCtl_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opconnectctl_labels.json")
P_TERMINAL, P_BD, P_NODES, P_TERMS, M_CONNECT = "6332006", "23C", "6375809", "6359000", "6349C03"
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
    return (f"{tag} Property={len(g.report_all(OP, 'Property'))} Invoke={len(g.report_all(OP, 'Invoke'))} "
            f"IndexArray={len(g.report_all(OP, 'IndexArray'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def ctls():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if not is_ind and lab]


def pidx(uid):
    return [o["uid"] for o in g.report_all(OP, "Property")].index(uid)


def iidx(uid):
    return [o["uid"] for o in g.report_all(OP, "IndexArray")].index(uid)


def walk():
    """uid -> (Nodes[] index, [(ti, name, wire)]) via node_terms_uid (no walker heuristics)."""
    out = {}
    for n in range(80):
        u, rows = g.node_terms_uid(OP, 0, n)
        if not u:
            break
        out[u] = (n, [(r["i"], r["name"], r["wire"]) for r in rows])
    return out


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
    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: donor copy not runnable.", flush=True); return 2
    w = walk()
    for u, (n, terms) in w.items():
        print(f"   node uid {u} n {n}: {[t for _i, t, _w in terms if t]}", flush=True)
    names_of = lambda u: [t for _i, t, _w in w[u][1] if t]
    ovr = next((u for u in w if "vi reference" in names_of(u)), None)
    ctl_pn = next((u for u in w if "Label" in names_of(u) and "Indicator" in names_of(u)), None)
    print(f"   Open VI Reference {ovr}; Control[Label, Indicator] node {ctl_pn}", flush=True)
    if ovr is None or ctl_pn is None:
        print("STOP: donor chain not recognised.", flush=True); return 2
    fidx = lambda u: [o["uid"] for o in g.report_all(OP, "Function")].index(u)

    # A the sink: Control[Terminal] from the Control node's reference out
    ct = step("A1 PN_CT Control[Terminal]", "Property +1", lambda: g.build_property(OP, "VI Server:Control", [(P_TERMINAL, False)], (900, 450))[-1]["uid"])
    if not ct:
        return 3
    step("A2 Control node 'reference out' -> PN_CT.reference", "Wire +1, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(ctl_pn), "reference out", "Property", pidx(ct), "reference"), snap("after"))[1])
    # B the source chain
    bd = step("B1 PN_BD VI.Block Diagram", "Property +1", lambda: g.build_property(OP, "VI Server:VI", [(P_BD, False)], (420, 650))[-1]["uid"])
    if not bd:
        return 3
    step("B2 Open VI Reference 'vi reference' -> PN_BD.reference (branch)", "ExecState 1",
         lambda: (g.wire(OP, "Function", fidx(ovr), "vi reference", "Property", pidx(bd), "reference", branch=True), snap("after"))[1])
    pn_n = step("B3 PN_N AbstractDiagram.Nodes[]", "Property +1", lambda: g.build_property(OP, "VI Server:AbstractDiagram", [(P_NODES, False)], (600, 650))[-1]["uid"])
    ia_n = step("B4 IA_n", "IndexArray +1", lambda: g.build_index_array(OP, (760, 650))[-1]["uid"])
    pn_t = step("B5 PN_T Node.Terminals[]", "Property +1", lambda: g.build_property(OP, "VI Server:Node", [(P_TERMS, False)], (900, 650))[-1]["uid"])
    ia_t = step("B6 IA_t", "IndexArray +1", lambda: g.build_index_array(OP, (1060, 650))[-1]["uid"])
    if None in (pn_n, ia_n, pn_t, ia_t):
        return 3
    step("B7 chain wires: BD.Diagram -> N.ref; N.Nodes[] -> IA_n.array; IA_n.element -> T.ref; T.Terms[] -> IA_t.array", "Wire +4, ExecState 1",
         lambda: ([g.wire(OP, "Property", pidx(bd), "Diagram", "Property", pidx(pn_n), "reference"),
                   g.wire(OP, "Property", pidx(pn_n), "Nodes[]", "IndexArray", iidx(ia_n), "array"),
                   g.wire(OP, "IndexArray", iidx(ia_n), "element", "Property", pidx(pn_t), "reference"),
                   g.wire(OP, "Property", pidx(pn_t), "Terms[]", "IndexArray", iidx(ia_t), "array")], snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: source chain broken.", flush=True); return 3
    # C the invoke
    inv = step("C1 Invoke Terminal.Connect Wire", "Invoke +1", lambda: g.build_invoke(OP, "VI Server:Terminal", M_CONNECT, (1250, 550))[-1]["uid"])
    if not inv:
        return 3
    inv_i = lambda: [o["uid"] for o in g.report_all(OP, "Invoke")].index(inv)
    step("C2 PN_CT.Terminal -> Invoke.reference (sink); IA_t.element -> 'Wire Source'", "Wire +2",
         lambda: ([g.wire(OP, "Property", pidx(ct), "Terminal", "Invoke", inv_i(), "reference"),
                   g.wire(OP, "IndexArray", iidx(ia_t), "element", "Invoke", inv_i(), "Wire Source")], snap("after"))[1])
    # D controls on the two IA index terminals, indicator on the invoke's error out
    w = walk()
    labels = {}
    for u, meaning in ((ia_n, "index_node"), (ia_t, "index_terminal")):
        n, terms = w[u]; ti = next(ti for ti, t, _w in terms if t == "index")
        before = set(ctls())
        g.create_control(OP, n, ti)
        new = [l for l in ctls() if l not in before]
        print(f"   control on IA(uid {u}).index -> {new}", flush=True)
        if new:
            labels[meaning] = new[-1]
    n_inv, terms = w[inv]; ti = next(ti for ti, t, _w in terms if t == "error out")
    before = set(inds()); g.create_indicator(OP, n_inv, ti)
    new = [l for l in inds() if l not in before]
    print(f"   indicator on Invoke.error out -> {new}", flush=True)
    if new:
        labels["error"] = new[-1]
    step("E auto error handling OFF", "silent", lambda: g.set_auto_error_handling(OP, False))
    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), "labels", labels, "steps", STEPS, flush=True)
    if es != 1 or any(k == "exc" for _n, k in STEPS) or set(labels) != {"index_node", "index_terminal", "error"}:
        print(f"\nVERDICT: BROKEN or INCOMPLETE (ExecState {es}) - NOT SAVING.", flush=True); return 4
    g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    print("\nVERDICT: OpConnectCtl_v0 BUILT and SAVED (structural) - functional test = tools/recipes/build_harness_dispI.py step 8", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
