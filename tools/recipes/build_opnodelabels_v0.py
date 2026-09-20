"""build_opnodelabels_v0.py - OpNodeLabels_v0.vi: the LABEL TEXT of every node on ONE diagram, as arrays, cast-free.

WHY. 88 implicit `Value` property nodes in the main VI are bound to panel objects whose identity no terminal names
(docs/main-vi-panel-map.md). Peer (archive/peer/2026-09-14-implicit-property-node-linked-object.md): the authoritative
`Property.Linked Control` 636F806 needs a Property-typed reference (no cast available); the cast-free fallback is
`Node.Label` 6359001 -> `Text.Text` 632D800 - an implicit node's header IS its label (LabVIEW Wiki), with the caveat
"the label must have been displayed at least once".
RISK (docs/keystone-op-spec.md s30): a node_info op reading Node.Label + Node.Style crashed LabVIEW on op VIs holding
TMSC / class-specifier constants; never isolated. This op reads Label only; the main VI has neither node class.

DONOR: OpNetInfo_v1 (as OpSubVIs_v1): Traverse 'Diagram' by `index` -> IA -> TMSC -> Diagram -> PN Nodes[] -> the
vestigial per-node chain (index 2 / index 3 stay 0). The creator subVI is deleted from the copy (step 2b, proven).

STEPS (prediction each; a miss prints EXC and nothing is saved):
  1  copy donor -> OpNodeLabels_v0.vi, open_panel                       ExecState 1
  2  net_map diagram 0 -> the node carrying 'Nodes[]'; 2b delete the creator subVI      ExecState 1
  3  for_loop at (1500, 250); body diagram                                ForLoop 1, one body
  4  PN_N Node[Label, UID] inside body (class VI Server:Node)             Property +1; terminals Label, UID
  5  PN_X Text[Text] inside body; PN_N 'Label' -> PN_X 'reference'        Property +1, Wire +1
  6  Nodes[]-node 'Nodes[]' -> PN_N 'reference' (branch: feeds IA_n too)  LoopTunnel +1, ExecState 1
  7  exit_loop PN_X['Text'], PN_N['UID']; index mode 1; tunnel indicators 2 array indicators (labels by diff)
  8  error indicator on the Nodes[]-node's 'error out' if unwired
  9  auto error handling OFF; ExecState 1 -> save; label map -> tools/bench/opnodelabels_labels.json
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opnodelabels_v0.log -- py -u tools/recipes/build_opnodelabels_v0.py
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

DONOR = "OpNetInfo_v1.vi"
SRC = os.path.join(g.CLAUDEDEV, DONOR)
OP = os.path.join(g.CLAUDEDEV, "OpNodeLabels_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opnodelabels_labels.json")
P_LABEL = "6359001"     # Node.Label   -> Text refnum (terminal 'Label' expected)
P_UID = "632A813"       # GObject.UID  -> 'UID'
P_TEXT = "632D800"      # Text.Text    -> 'Text'
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


def body_terms(uid, body):
    return next(([t for _ti, t, _w in terms if t and t not in ("reference", "reference out", "error in (no error)", "error out")]
                 for _i, (u, _l, terms) in g.net_map(OP, body, max_nodes=20, max_terms=24)[0].items() if u == uid), None)


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
        print("STOP: donor copy not runnable. Nothing saved.", flush=True); return 2

    walk0 = g.net_map(OP, 0, max_nodes=80, max_terms=24)[0]
    found = next(((u, terms) for _i, (u, _l, terms) in walk0.items() if any(t == "Nodes[]" for _ti, t, _w in terms)), None)
    if found is None:
        print("STOP: no Nodes[] node. Nothing saved.", flush=True); return 2
    nodes_uid, nodes_terms = found
    nodes_wired = any(t == "Nodes[]" and w for _ti, t, w in nodes_terms)
    err_wired = any(t == "error out" and w for _ti, t, w in nodes_terms)
    print(f"   Nodes[]-node uid {nodes_uid}; 'Nodes[]' already wired: {nodes_wired}; 'error out' wired: {err_wired}", flush=True)

    # 2b creator deletion (identity by terminal signature, as OpSubVIs_v1)
    sub_rows = g.report_all(OP, "SubVI"); sub_uids = {o["uid"]: o for o in sub_rows}
    cands = [u for _n, (u, _l, terms) in walk0.items() if u in sub_uids
             and any(t in [x for _ti, x, _w in terms] for t in ("Inputs", "Outputs", "Method Name", "Method ID", "Property Names"))
             and "GObject Refs" not in [x for _ti, x, _w in terms]]
    print(f"   creator candidates: {cands}", flush=True)
    if len(cands) == 1:
        ci = [o["uid"] for o in sub_rows].index(cands[0])
        step("2b delete the creator SubVI from the COPY", "SubVI gone, ExecState 1 after RBW",
             lambda: (g.delete_object(OP, "SubVI", ci), g.remove_bad_wires_scripted(OP), snap("after"))[2])
        if cands[0] in {o["uid"] for o in g.report_all(OP, "SubVI")} or g.exec_state(OP) != 1:
            print("STOP: creator not removable cleanly. Nothing saved.", flush=True); return 3
    else:
        print("STOP: creator not identified uniquely (v1 donor should give exactly one). Nothing saved.", flush=True); return 3

    step("3 empty For Loop", "ForLoop 0->1; ExecState 0 EXPECTED (no N yet)", lambda: (g.for_loop(OP, (1500, 250)), snap("after"))[1])
    dias = [i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner"))]
    if len(dias) != 1:
        print(f"STOP: loop body not unique: {dias}. Nothing saved.", flush=True); return 3
    body = dias[0]

    pn_n = step("4 PN_N Node[Label, UID] inside body", "Property +1",
                lambda: g.build_property(OP, "VI Server:Node", [(P_LABEL, False), (P_UID, False)], (1550, 300), diagram_index=body))
    if not pn_n:
        return 3
    n_uid = pn_n[-1]["uid"]
    got = step("4-check PN_N terminals", "data terminals == ['Label', 'UID']", lambda: body_terms(n_uid, body))
    if got is None or set(got) != {"Label", "UID"}:
        print(f"STOP: PN_N rows are {got}. Nothing saved.", flush=True); return 3

    pn_x = step("5a PN_X Text[Text] inside body", "Property +1",
                lambda: g.build_property(OP, "VI Server:Text", [(P_TEXT, False)], (1800, 300), diagram_index=body))
    if not pn_x:
        return 3
    x_uid = pn_x[-1]["uid"]
    step("5b PN_N 'Label' -> PN_X 'reference'", "Wire +1",
         lambda: (g.wire(OP, "Property", pidx(n_uid), "Label", "Property", pidx(x_uid), "reference"), snap("after"))[1])

    step("6 Nodes[]-node 'Nodes[]' -> PN_N 'reference' (crosses the loop; branch)", "LoopTunnel +1, Wire +2, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(nodes_uid), "Nodes[]", "Property", pidx(n_uid), "reference", branch=nodes_wired),
                  snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after the loop input. Nothing saved.", flush=True)
        for row in g.net_map(OP, body, max_nodes=20, max_terms=24)[0].items():
            print("   body node:", row, flush=True)
        return 3

    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    step("7a exit_loop PN_X ['Text']", "LoopTunnel +1", lambda: (g.exit_loop(OP, pidx(x_uid), ["Text"], body, node_class="Property"), snap("after"))[1])
    step("7b exit_loop PN_N ['UID']", "LoopTunnel +1", lambda: (g.exit_loop(OP, pidx(n_uid), ["UID"], body, node_class="Property"), snap("after"))[1])
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True); return 4
    out_tuns = [o["i"] for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
    print(f"\n== 7c output tunnels by census = indices {out_tuns}", flush=True)
    label_map = {}
    for k, tun in enumerate(out_tuns):
        before = set(inds())
        try:
            g.set_index_mode(OP, tun, 1)
        except Exception as e:
            print(f"   tunnel {tun}: set_index_mode {str(e)[:120]}", flush=True)
        try:
            g.tunnel_indicator(OP, tun)
        except Exception as e:
            print(f"   tunnel {tun}: tunnel_indicator FAILED {str(e)[:180]}", flush=True); continue
        new = [l for l in inds() if l not in before]
        meaning = ["Text", "UID"][k] if k < 2 else f"tunnel {tun}"
        print(f"   tunnel {tun} -> indicator {new} (carries {meaning})", flush=True)
        for l in new:
            label_map[l] = meaning

    err_label = None
    if not err_wired:
        n_nodes = next((n for n, (u, _l, _t) in g.net_map(OP, 0, max_nodes=80, max_terms=24)[0].items() if u == nodes_uid), None)
        if n_nodes is not None:
            before = set(inds())
            step("8 indicator on Nodes[]-node terminal 3 (error out)", "one new indicator, ExecState 1",
                 lambda: (g.create_indicator(OP, n_nodes, 3), snap("after"))[1])
            new = [l for l in inds() if l not in before]
            if len(new) == 1 and g.exec_state(OP) == 1:
                err_label = new[0]
            print(f"   error indicator: {new}", flush=True)
    else:
        print("   Nodes[]-node error out already wired - no error indicator (rows empty + err unknown => caller checks length)", flush=True)

    step("9 auto error handling OFF", "no dialog", lambda: g.set_auto_error_handling(OP, False))
    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True); print("steps:", STEPS, flush=True); print("label map:", json.dumps(label_map), flush=True)
    if es != 1 or len(label_map) != 2:
        print(f"\nVERDICT: BROKEN (ExecState {es}, {len(label_map)} array indicators) - NOT SAVING.", flush=True); return 4
    if err_label:
        label_map[err_label] = "error"
    step("10 COM save", "written", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor {DONOR} md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("\nVERDICT: OpNodeLabels_v0 BUILT and SAVED (structural only - run tools/bench/test_opnodelabels.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
