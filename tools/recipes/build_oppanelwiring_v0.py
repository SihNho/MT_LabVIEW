"""build_oppanelwiring_v0.py - OpPanelWiring_v0.vi: every top-level front-panel object of a VI, with its diagram
terminal's wiring state, as arrays in ONE run - cast-free.

WHY. docs/main-vi-panel-map.md lists the main VI's 114 panel objects but its "wiring" column is empty: which of them
are live (terminal wired on the diagram) and which are legacy leftovers the user warned about ("프론트 패널에 남아있지만
실제로 와이어링 안되어 있거나 사용하지 않는 부분들이 있을 수 있지"). The cast-free route Control.Terminal 6332006 ->
Terminal[Is Source? 634A003, Connected Wire 634A000] compiled today (probe_castfree5.log; names 'Terminal',
'IsSource', 'Wire'); the array-op pattern shipped as OpSubVIs_v1 the same morning.

DONOR: OpFPLabels_v0.vi (tools/recipes/build_opfplabels.py): Open VI Reference -> VI.Front Panel 23D ->
Panel.Controls[] 6348801 -> Index Array(index) -> Control[Label, Indicator] -> Text.Text -> indicators 'Text',
'Indicator'. The Controls[] node's array output is the loop's input once its old consumers are deleted.

OUTPUT ARRAYS (one row per panel object, aligned): label text, Indicator flag, control UID, terminal IsSource,
connected-wire UID (0 = unwired = orphaned; the iteration's GObject.UID node errors on Not-A-Refnum and its
auto-indexed output takes the type default - to be CONFIRMED by the functional test, see peer review).

STEPS (prediction per step; a miss prints 'exc' and stops before saving):
  1  copy donor -> OpPanelWiring_v0.vi, open_panel, donor md5           ExecState 1
  2  net_map diagram 0: Controls[]-node, the Index Array, Control[Label,Indicator] node, Text node
  3  delete Text node, Control node, Index Array (downstream first) + Remove Bad Wires     ExecState 1
  4  for_loop, body diagram
  5  PN1 Control[Label, Terminal, Indicator, UID] inside body; terminals checked by net_map
  6  wire Controls[]-node 'Controls[]' -> PN1 'reference' (crosses the loop)         LoopTunnel +1, ExecState 1
  7  PN2 Text[Text] <- PN1 'Label'; PN3 Terminal[IsSource, ConnectedWire] <- PN1 'Terminal'; PN4 GObject[UID] <- PN3 'Wire'
  8  exit_loop PN2['Text'], PN1['Indicator','UID'], PN3['IsSource'], PN4['UID'] -> 5 tunnels -> index mode 1 -> indicators
  9  auto error handling OFF; ExecState 1 -> save; label map -> tools/bench/oppanelwiring_labels.json
  py tools/bgrun.py --max-min 20 --log tools/bench/build_oppanelwiring_v0.log -- py -u tools/recipes/build_oppanelwiring_v0.py
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
OP = os.path.join(g.CLAUDEDEV, "OpPanelWiring_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "oppanelwiring_labels.json")

P_LABEL, P_TERMINAL, P_INDICATOR, P_UID = "6332005", "6332006", "6332007", "632A813"
P_TEXT, P_ISSRC, P_CONNW = "632D800", "634A003", "634A000"
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
            f"Property={len(g.report_all(OP, 'Property'))} IndexArray={len(g.report_all(OP, 'IndexArray'))} "
            f"Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def pidx(uid):
    return [o["uid"] for o in g.report_all(OP, "Property")].index(uid)


def terms_of(uid, diagram):
    return next(([t for _ti, t, _w in terms if t] for _i, (u, _l, terms) in
                 g.net_map(OP, diagram, max_nodes=80, max_terms=24)[0].items() if u == uid), None)


def main():
    g._lv = None
    try:
        g.close_panel(OP)
        time.sleep(0.4)
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

    walk = g.net_map(OP, 0, max_nodes=80, max_terms=24)[0]
    by_uid = {u: [t for _ti, t, _w in terms if t] for _i, (u, _l, terms) in walk.items()}
    for u, names in by_uid.items():
        print(f"   node uid {u}: {names}", flush=True)
    ctrls = next((u for u, n in by_uid.items() if "Controls[]" in n), None)
    ctl_pn = next((u for u, n in by_uid.items() if "Label" in n and "Indicator" in n), None)
    txt_pn = next((u for u, n in by_uid.items() if "Text" in n and "reference" in n), None)
    ia_rows = g.report_all(OP, "IndexArray")
    print(f"   Controls[]-node {ctrls}; Control[Label,Indicator] node {ctl_pn}; Text node {txt_pn}; IndexArray rows {len(ia_rows)}",
          flush=True)
    if ctrls is None or ctl_pn is None or txt_pn is None or len(ia_rows) != 1:
        print("STOP: donor chain not recognised. Nothing saved.", flush=True)
        return 2

    step("3 delete Text node, Control node, Index Array (downstream first) + RBW", "Property 4->2, IndexArray 1->0, ExecState 1",
         lambda: ([g.delete_object(OP, "Property", pidx(txt_pn)), g.delete_object(OP, "Property", pidx(ctl_pn)),
                   g.delete_object(OP, "IndexArray", 0), g.remove_bad_wires_scripted(OP)], snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after freeing Controls[]. Nothing saved.", flush=True)
        return 3

    step("4 empty For Loop", "ForLoop 0->1; ExecState 0 EXPECTED", lambda: (g.for_loop(OP, (1500, 250)), snap("after"))[1])
    dias = [i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner"))]
    if len(dias) != 1:
        print(f"STOP: loop body not unique: {dias}. Nothing saved.", flush=True)
        return 3
    body = dias[0]

    # Peer (archive/peer/2026-09-14-oppanelwiring-v0-plan.md s2): property-node rows execute top-to-bottom and a
    # failing row stops the later ones, so `Terminal` (the row that can fail on an odd object) must NOT share a node
    # with the metadata rows - it gets its own node fed from PN1's `reference out`.
    pn1 = step("5 PN1 Control[Label, Indicator, UID] inside body (metadata only, cannot be poisoned)", "Property +1",
               lambda: g.build_property(OP, "VI Server:Control", [(P_LABEL, False), (P_INDICATOR, False), (P_UID, False)],
                                        (1550, 300), diagram_index=body))
    if not pn1:
        return 3
    pn1_uid = pn1[-1]["uid"]
    got = step("5-check PN1 terminals", "data terminals == Label, Indicator, UID",
               lambda: [t for t in terms_of(pn1_uid, body) if t not in GENERIC])
    if not got or set(got) != {"Label", "Indicator", "UID"}:
        print(f"STOP: PN1 rows are {got}. Nothing saved.", flush=True)
        return 3
    step("6 wire Controls[]-node 'Controls[]' -> PN1 'reference' (crosses the loop)", "LoopTunnel +1, Wire +2, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(ctrls), "Controls[]", "Property", pidx(pn1_uid), "reference"), snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after the loop input. Nothing saved.", flush=True)
        return 3
    # (first run 11:0x: PN1b was created BEFORE this check with its required `reference` unwired -> ExecState 0 by
    # construction, a recipe-order error, not a LabVIEW finding; build_oppanelwiring_v0.log run 1.)
    pn1b = step("6b PN1b Control[Terminal] inside body (the risky row, on its own node)", "Property +1; ExecState 0 until 7d2",
                lambda: g.build_property(OP, "VI Server:Control", [(P_TERMINAL, False)], (1550, 420), diagram_index=body))
    if not pn1b:
        return 3
    pn1b_uid = pn1b[-1]["uid"]

    pn2 = step("7a PN2 Text[Text] inside body", "Property +1",
               lambda: g.build_property(OP, "VI Server:Text", [(P_TEXT, False)], (1800, 250), diagram_index=body))
    pn3 = step("7b PN3 Terminal[IsSource, ConnectedWire] inside body", "Property +1",
               lambda: g.build_property(OP, "VI Server:Terminal", [(P_ISSRC, False), (P_CONNW, False)], (1800, 420),
                                        diagram_index=body))
    pn4 = step("7c PN4 GObject[UID] inside body (the wire's UID)", "Property +1",
               lambda: g.build_property(OP, "VI Server:GObject", [(P_UID, False)], (2050, 420), diagram_index=body))
    if not (pn2 and pn3 and pn4):
        return 3
    pn2_uid, pn3_uid, pn4_uid = pn2[-1]["uid"], pn3[-1]["uid"], pn4[-1]["uid"]
    step("7d PN1.Label -> PN2.reference", "Wire +1",
         lambda: (g.wire(OP, "Property", pidx(pn1_uid), "Label", "Property", pidx(pn2_uid), "reference"), snap("after"))[1])
    step("7d2 PN1.reference out -> PN1b.reference", "Wire +1",
         lambda: (g.wire(OP, "Property", pidx(pn1_uid), "reference out", "Property", pidx(pn1b_uid), "reference"), snap("after"))[1])
    step("7e PN1b.Terminal -> PN3.reference", "Wire +1",
         lambda: (g.wire(OP, "Property", pidx(pn1b_uid), "Terminal", "Property", pidx(pn3_uid), "reference"), snap("after"))[1])
    step("7f PN3.Wire -> PN4.reference", "Wire +1, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(pn3_uid), "Wire", "Property", pidx(pn4_uid), "reference"), snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after the inner hops. Nothing saved.", flush=True)
        for row in g.net_map(OP, body, max_nodes=20, max_terms=24)[0].items():
            print("   body node:", row, flush=True)
        return 3

    tun_before = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    plan = [(pn2_uid, ["Text"]), (pn1_uid, ["Indicator", "UID"]), (pn3_uid, ["IsSource"]), (pn4_uid, ["UID"])]
    meanings = ["Text", "Indicator", "ControlUID", "IsSource", "WireUID"]
    for k, (u, outs) in enumerate(plan):
        step(f"8.{k} exit_loop {outs} on Property uid {u}", f"LoopTunnel +{len(outs)}",
             lambda u=u, outs=outs: (g.exit_loop(OP, pidx(u), outs, body, node_class="Property"), snap("after"))[1])
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True)
        return 4
    # Peer s1: do not encode "unwired" only as UID 0 - carry the two risky nodes' own error status out explicitly
    # (arrays of error clusters). Optional: if exit_loop refuses 'error out', the UID-0 semantics stay and the
    # functional test's constructed orphan (T2) decides whether they hold.
    n_before_err = len(g.report_all(OP, "LoopTunnel"))
    for u, tag in ((pn1b_uid, "TermErr"), (pn4_uid, "WireErr")):
        try:
            g.exit_loop(OP, pidx(u), ["error out"], body, node_class="Property")
            meanings.append(tag)
            print(f"   optional: error out of {tag} node tunnelled", flush=True)
        except Exception as e:
            print(f"   optional: error out of {tag} not tunnelled ({str(e)[:100]})", flush=True)
    n_err_tuns = len(g.report_all(OP, "LoopTunnel")) - n_before_err
    out_tuns = [o["i"] for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun_before]
    print(f"\n== 8x. output tunnels by census = indices {out_tuns} (expect {5 + n_err_tuns}, in exit_loop order)", flush=True)
    label_map = {}
    for k, tun in enumerate(out_tuns):
        before_labels = set(inds())
        try:
            g.set_index_mode(OP, tun, 1)
        except Exception as e:
            print(f"   tunnel {tun}: set_index_mode {str(e)[:120]}", flush=True)
        try:
            g.tunnel_indicator(OP, tun)
        except Exception as e:
            print(f"   tunnel {tun}: tunnel_indicator FAILED {str(e)[:180]}", flush=True)
            continue
        new_labels = [l for l in inds() if l not in before_labels]
        meaning = meanings[k] if k < len(meanings) else f"tunnel {tun}"
        print(f"   tunnel {tun} -> indicator {new_labels}  (carries {meaning})", flush=True)
        for l in new_labels:
            label_map[l] = meaning

    step("9 auto error handling OFF", "no dialogs for unwired terminals", lambda: g.set_auto_error_handling(OP, False))
    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    print("label map:", json.dumps(label_map), flush=True)
    if es != 1 or len(label_map) < 5:
        print(f"\nVERDICT: BROKEN (ExecState {es}, {len(label_map)} array indicators) - NOT SAVING.", flush=True)
        return 4
    step("10 COM save", "written to disk", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor OpFPLabels_v0.vi md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    print("\nVERDICT: OpPanelWiring_v0 BUILT and SAVED (structural only - run tools/bench/test_oppanelwiring.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
