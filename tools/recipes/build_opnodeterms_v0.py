"""build_opnodeterms_v0.py - OpNodeTerms_v0.vi: every terminal of ONE node (diagram `index`, Nodes[] `index 2`) as
arrays in ONE run - Name, Is Source?, connected-wire UID (0 = unwired), plus the Terminal node's own error out.

WHY. (1) The read/write DIRECTION of the main VI's global-variable nodes (`Global motor pos.vi`: Trans / Rot /
Focus position; docs/main-vi-state.md places them, direction "still NOT established"): a global node whose data
terminal Is Source? = TRUE is a READ, FALSE a WRITE - cast-free (Node.Terminals[] is typed Terminal). (2) A junk-free,
one-run-per-node replacement for net_map's per-terminal walk.

DONOR: OpNetInfo_v1.vi (tools/recipes/build_opnetinfo.py): ... -> PN Diagram.Nodes[] -> IA_n[index 2] ->
PN Node[Terminals[]] -> IA_t[index 3] -> PN Terminal[Name, Connected Wire] -> PN Wire[UID, Is Broken?] -> Clear Errors;
PN Node[Label, Style] <- IA_n.element (branch) -> PN Text.Text; and the erdosmiller creator (deleted cleanly from a copy
this morning: OpSubVIs_v1 step 2b). The Node[Terminals[]] output ('Terms[]', docs/NAMES.md) becomes the loop input
once IA_t and everything after it are deleted.

STEPS (prediction per step; a miss prints 'exc'/'STOP' and nothing is saved):
  1  copy donor -> OpNodeTerms_v0.vi, open_panel, donor md5                    ExecState 1
  2  net_map diagram 0; delete the creator (terminal signature Inputs/Outputs/ID String)   ExecState 1 after RBW
  3  identify: Terminals[]-node (terminal 'Terms[]' or 'Terminals[]'), the IA consuming it, the Terminal[Name,
     Connected Wire] PN, the Wire[UID, Is Broken?] PN; delete Wire PN, Terminal PN, that IA (downstream first) + RBW
  4  for_loop; body diagram
  5  PN_T Terminal[Name 634A004, Is Source? 634A003, Connected Wire 634A000] inside body; rows checked by net_map
  6  wire Terminals[]-node output -> PN_T 'reference' (crosses the loop)         LoopTunnel +1, ExecState 1
  7  PN_W GObject[UID] inside body <- PN_T 'Wire'                                ExecState 1
  8  exit_loop PN_T ['Name','IsSource'], PN_W ['UID'], + 'error out' of PN_T and PN_W (explicit error columns)
  9  auto error handling OFF; ExecState 1 -> save; labels -> tools/bench/opnodeterms_labels.json
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opnodeterms_v0.log -- py -u tools/recipes/build_opnodeterms_v0.py
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

SRC = os.path.join(g.CLAUDEDEV, "OpNetInfo_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpNodeTerms_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opnodeterms_labels.json")
P_NAME, P_ISSRC, P_CONNW, P_UID = "634A004", "634A003", "634A000", "632A813"
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
            f"SubVI={len(g.report_all(OP, 'SubVI'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def pidx(uid):
    return [o["uid"] for o in g.report_all(OP, "Property")].index(uid)


def walk(diagram=0):
    nodes, nets = g.net_map(OP, diagram, max_nodes=80, max_terms=24)
    return {u: [(t, w) for _ti, t, w in terms] for _i, (u, _l, terms) in nodes.items()}


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

    w = walk()
    sub_uids = {o["uid"] for o in g.report_all(OP, "SubVI")}
    for u, terms in w.items():
        print(f"   node uid {u}{' (SubVI)' if u in sub_uids else ''}: {[t for t, _w in terms if t]}", flush=True)
    cands = [u for u, terms in w.items() if u in sub_uids and any(t in ("Inputs", "Outputs", "ID String") for t, _w in terms)
             and not any(t == "GObject Refs" for t, _w in terms)]
    if len(cands) != 1:
        print(f"STOP: creator not identified uniquely: {cands}. Nothing saved.", flush=True)
        return 2
    ci = [o["uid"] for o in g.report_all(OP, "SubVI")].index(cands[0])
    step("2 delete the creator SubVI + RBW", "SubVI -1, ExecState 1",
         lambda: (g.delete_object(OP, "SubVI", ci), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after creator removal. Nothing saved.", flush=True)
        return 3

    # 3 identify the Terminals[] chain by terminal names and wire uids
    w = walk()
    terms_node = next((u for u, terms in w.items() if any(t in ("Terms[]", "Terminals[]") for t, _w in terms)), None)
    if terms_node is None:
        print("STOP: no Node.Terminals[] node found. Nothing saved.", flush=True)
        return 2
    t_out = next((t, wid) for t, wid in w[terms_node] if t in ("Terms[]", "Terminals[]"))
    term_pn = next((u for u, terms in w.items() if any(t == "Name" for t, _w in terms) and any(t in ("Wire", "ConnectedWire") for t, _w in terms)), None)
    # Wire.Is Broken? shows on the node as 'Broken?' (read off the machine, build_opnodeterms_v0.log run 1 - the
    # first matcher guessed 'IsBroken' and stopped the build; docs/NAMES.md).
    wire_pn = next((u for u, terms in w.items() if any(t == "UID" for t, _w in terms)
                    and any(t in ("Broken?", "IsBroken", "IsBroken?", "Is Broken?") for t, _w in terms)), None)
    ia_rows = g.report_all(OP, "IndexArray")
    # the IA fed by Terms[]: its 'array' terminal carries the same wire uid as the Terms[] output
    ia_t = next((u for u, terms in w.items() if u in {o["uid"] for o in ia_rows}
                 and any(t == "array" and wid == t_out[1] and wid for t, wid in terms)), None)
    print(f"   Terminals[]-node {terms_node} output {t_out}; IA_t {ia_t}; Terminal PN {term_pn}; Wire PN {wire_pn}; IAs {len(ia_rows)}",
          flush=True)
    if None in (term_pn, wire_pn, ia_t):
        print("STOP: chain not recognised. Nothing saved.", flush=True)
        return 2
    step("3 delete Wire PN, Terminal PN, IA_t (downstream first) + RBW", "Property -2, IndexArray -1, ExecState 1",
         lambda: ([g.delete_object(OP, "Property", pidx(wire_pn)), g.delete_object(OP, "Property", pidx(term_pn)),
                   g.delete_object(OP, "IndexArray", [o["uid"] for o in g.report_all(OP, "IndexArray")].index(ia_t)),
                   g.remove_bad_wires_scripted(OP)], snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after freeing Terms[]. Nothing saved.", flush=True)
        return 3

    step("4 empty For Loop", "ForLoop +1; ExecState 0 EXPECTED", lambda: (g.for_loop(OP, (1500, 900)), snap("after"))[1])
    dias = [i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner"))]
    if len(dias) != 1:
        print(f"STOP: loop body not unique: {dias}. Nothing saved.", flush=True)
        return 3
    body = dias[0]
    # Peer (archive/peer/2026-09-14-opnodeterms-v0-plan.md s4, the strongest defect): rows of ONE property node run
    # top-to-bottom and an early error suppresses the later rows, so a terminal whose Name read fails would come
    # back as IsSource FALSE / wire 0 - indistinguishable from an unwired sink. Each property gets its OWN node with
    # its own (unwired) error chain: PN_N[Name] -> PN_S[Is Source?] -> PN_C[Connected Wire] -> PN_W[UID], chained by
    # `reference out`. PN_N is the ONLY body node until the loop input exists (recipe-order lesson of 11:0x).
    pnn = step("5 PN_N Terminal[Name] inside body", "Property +1",
               lambda: g.build_property(OP, "VI Server:Terminal", [(P_NAME, False)], (1550, 950), diagram_index=body))
    if not pnn:
        return 3
    pnn_uid = pnn[-1]["uid"]
    got = step("5-check PN_N terminals", "data terminals == ['Name']",
               lambda: [t for t, _w in walk(body)[pnn_uid] if t and t not in GENERIC])
    if got != ["Name"]:
        print(f"STOP: PN_N rows are {got}. Nothing saved.", flush=True)
        return 3
    step("6 wire Terminals[]-node output -> PN_N 'reference' (crosses the loop)", "LoopTunnel +1, Wire +2, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(terms_node), t_out[0], "Property", pidx(pnn_uid), "reference"), snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after the loop input. Nothing saved.", flush=True)
        return 3
    pns = step("7a PN_S Terminal[Is Source?] inside body", "Property +1",
               lambda: g.build_property(OP, "VI Server:Terminal", [(P_ISSRC, False)], (1750, 950), diagram_index=body))
    pnc = step("7b PN_C Terminal[Connected Wire] inside body", "Property +1",
               lambda: g.build_property(OP, "VI Server:Terminal", [(P_CONNW, False)], (1950, 950), diagram_index=body))
    pnw = step("7c PN_W GObject[UID] inside body", "Property +1",
               lambda: g.build_property(OP, "VI Server:GObject", [(P_UID, False)], (2150, 950), diagram_index=body))
    if not (pns and pnc and pnw):
        return 3
    pns_uid, pnc_uid, pnw_uid = pns[-1]["uid"], pnc[-1]["uid"], pnw[-1]["uid"]
    step("7d PN_N.reference out -> PN_S.reference", "Wire +1",
         lambda: (g.wire(OP, "Property", pidx(pnn_uid), "reference out", "Property", pidx(pns_uid), "reference"), snap("after"))[1])
    step("7e PN_S.reference out -> PN_C.reference", "Wire +1",
         lambda: (g.wire(OP, "Property", pidx(pns_uid), "reference out", "Property", pidx(pnc_uid), "reference"), snap("after"))[1])
    step("7f PN_C.Wire -> PN_W.reference", "Wire +1, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(pnc_uid), "Wire", "Property", pidx(pnw_uid), "reference"), snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after the inner chain. Nothing saved.", flush=True)
        for row in walk(body).items():
            print("   body node:", row, flush=True)
        return 3

    tun_before = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    meanings = ["Name", "IsSource", "WireUID"]
    step("8.0 exit_loop ['Name'] on PN_N", "LoopTunnel +1",
         lambda: (g.exit_loop(OP, pidx(pnn_uid), ["Name"], body, node_class="Property"), snap("after"))[1])
    step("8.1 exit_loop ['IsSource'] on PN_S", "LoopTunnel +1",
         lambda: (g.exit_loop(OP, pidx(pns_uid), ["IsSource"], body, node_class="Property"), snap("after"))[1])
    step("8.2 exit_loop ['UID'] on PN_W", "LoopTunnel +1",
         lambda: (g.exit_loop(OP, pidx(pnw_uid), ["UID"], body, node_class="Property"), snap("after"))[1])
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True)
        return 4
    for u, tag in ((pnn_uid, "NameErr"), (pns_uid, "SrcErr"), (pnc_uid, "ConnErr"), (pnw_uid, "WireErr")):
        try:
            g.exit_loop(OP, pidx(u), ["error out"], body, node_class="Property")
            meanings.append(tag)
        except Exception as e:
            print(f"   optional: error out of {tag} not tunnelled ({str(e)[:100]})", flush=True)
    out_tuns = [o["i"] for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun_before]
    print(f"\n== 8x. output tunnels by census = {out_tuns} (expect {len(meanings)})", flush=True)
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
    step("9 auto error handling OFF", "silent on unwired terminals", lambda: g.set_auto_error_handling(OP, False))
    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    print("label map:", json.dumps(label_map), flush=True)
    if es != 1 or len(label_map) < 3:
        print(f"\nVERDICT: BROKEN (ExecState {es}, {len(label_map)} arrays) - NOT SAVING.", flush=True)
        return 4
    step("10 COM save", "written to disk", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor OpNetInfo_v1.vi md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    print("\nVERDICT: OpNodeTerms_v0 BUILT and SAVED (structural only - run tools/bench/test_opnodeterms.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
