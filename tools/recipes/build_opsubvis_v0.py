"""build_opsubvis_v0.py - OpSubVIs_v0.vi: every subVI call on ONE diagram, as arrays, in ONE run - cast-free.

WHY. The documentation gaps (docs/main-vi-panel-map.md, main-vi-state.md, main-vi-startup.md) all reduce to "which
VI does node X call". The cache tools/bench/main_vi_netmap.json knows node UIDs and terminal names but not callee
identity; Node.Label was rejected as an identity by peer review (a user label, not the callee). The cast-free route
`AbstractDiagram.SubVIs[]` 6375802 -> SubVI-class property node `VI Name` 635E401 / `VI Path` 635E403 was proven to
COMPILE today (tools/bench/probe_castfree5.log, ExecState 1, terminal names read off the machine: 'SubVIs[]',
'VIName', 'VIPath'). This turns it into an op that returns arrays (the OpReportAll_v0 pattern, 380x faster than
per-object reads).

DONOR: OpNodeInfo_v0.vi - Open VI Reference -> Traverse 'Diagram' by `index` -> Index Array -> Nodes[] property node
-> (per-node / per-terminal readers driven by `index 2` / `index 3`). The front half gives us the diagram reference
typed as Diagram; the Nodes[]-node's unwired `reference out` is where the new chain starts (proven in the ladder).
The old per-node chain is LEFT IN PLACE (vestigial; `index 2`/`index 3` stay 0) - deleting it is a risk with no
benefit for v0.

STEPS (each with a prediction; a miss prints 'exc' and the build stops before saving):
  1  copy donor -> OpSubVIs_v0.vi, open_panel                     ExecState 1
  2  net_map diagram 0 -> uid of the node carrying 'Nodes[]'      found
  3  build_property AbstractDiagram [SubVIs[]]                    Property +1, ExecState 0 (unwired reference)
  4  wire Nodes[]-node 'reference out' -> SubVIs[]-node 'reference'   Wire +1, ExecState 1
  5  for_loop at (1500, 250)                                      ForLoop 0->1 (ExecState 0: empty loop has no N)
  6  body diagram index (owner contains 'For')                    exactly one
  7  build_property inside body, class SubVI, [VI Name, VI Path, GObject.UID]   Property +1
       fallback on creator error: SubVI [VI Name, VI Path] + a GObject [UID] node fed from its 'reference out'
  8  wire SubVIs[]-node 'SubVIs[]' -> inner 'reference' (crosses the loop)   LoopTunnel +1, Wire +2, ExecState 1
  9  exit_loop(inner, ['VIName','VIPath','UID'])                  LoopTunnel +3
 10  set_index_mode(1) + tunnel_indicator on each output tunnel   3 new array indicators; labels discovered by diff
 11  set_auto_error_handling(False)                               (an empty diagram must not pop a dialog)
 12  ExecState 1 -> save; label map -> tools/bench/opsubvis_labels.json

Never touches the donor (copied first). Saves only when ExecState == 1. Functional test is a separate script:
tools/bench/test_opsubvis.py (expected values stated there).
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opsubvis_v0.log -- py -u tools/recipes/build_opsubvis_v0.py
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

# v0 (2026-09-14 10:4x) used donor OpNodeInfo_v0 and FAILED functionally (tools/bench/test_opsubvis.log): that
# donor's `index` is a NODE index in the TOP-LEVEL diagram - it never selects a diagram - so the op read diagram 0
# only (scratch passed because its subVIs are on diagram 0; main VI diagram 43 came back empty, no error).
# v1: donor OpNetInfo_v1 (Traverse 'Diagram' by `index` -> Index Array -> To More Specific Class -> Diagram), the
# op behind net_map, which selects diagrams correctly. Its known cost (spec s33): an erdosmiller creator that drops
# one junk Invoke on the TARGET per run - callers purge (gscript wrapper). Select with argv: `v1` (default) or `v0`.
VER = (sys.argv[1] if len(sys.argv) > 1 else "v1").lower()
DONOR = {"v0": "OpNodeInfo_v0.vi", "v1": "OpNetInfo_v1.vi"}[VER]
SRC = os.path.join(g.CLAUDEDEV, DONOR)
OP = os.path.join(g.CLAUDEDEV, f"OpSubVIs_{VER}.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", f"opsubvis_{VER}_labels.json")

P_SUBVIS = "6375802"    # AbstractDiagram.SubVIs[]
P_VINAME = "635E401"    # SubVI.VI Name      -> terminal 'VIName'
P_VIPATH = "635E403"    # SubVI.VI Path      -> terminal 'VIPath'
P_UID = "632A813"       # GObject.UID        -> terminal 'UID'
T_SUBVIS, T_VINAME, T_VIPATH, T_UID = "SubVIs[]", "VIName", "VIPath", "UID"
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
            f"Property={len(g.report_all(OP, 'Property'))} Wire={len(g.report_all(OP, 'Wire'))} "
            f"ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def pidx(uid):
    return [o["uid"] for o in g.report_all(OP, "Property")].index(uid)


def main():
    g._lv = None
    try:
        g.close_panel(OP)
        time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(OP):
        try:
            os.remove(OP)
        except OSError as e:
            print(f"cannot replace {OP}: {e}", flush=True)
            return 1
    donor_md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()       # peer point (e): prove the donor untouched
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)
    time.sleep(1.0)
    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: donor copy not runnable. Nothing saved.", flush=True)
        return 2

    found = step("2 find the Nodes[]-node (net_map, self-purging)", "one node carries a 'Nodes[]' terminal",
                 lambda: next((u, terms) for _i, (u, _l, terms) in g.net_map(OP, 0, max_nodes=80, max_terms=24)[0].items()
                              if any(t == "Nodes[]" for _ti, t, _w in terms)))
    if found is None:
        print("STOP: no Nodes[] node. Nothing saved.", flush=True)
        return 2
    nodes_uid, nodes_terms = found
    ref_out_wired = any(t == "reference out" and w for _ti, t, w in nodes_terms)
    print(f"   Nodes[]-node uid {nodes_uid}; 'reference out' already wired: {ref_out_wired} -> branch={ref_out_wired}",
          flush=True)

    if VER == "v1":
        # Peer (archive/peer/2026-09-14-opsubvis-v1-donor-netinfo.md s2): before accepting a per-run purge on the
        # TARGET, try to remove the junk-dropping erdosmiller creator from the op COPY itself, with an identity test:
        # report the candidate (uid/class/owner/terminals) from the same walk, delete by that uid's SubVI index,
        # re-report, and require ExecState 1 after Remove Bad Wires. Any doubt -> keep it (runtime purge stays).
        walk0 = g.net_map(OP, 0, max_nodes=80, max_terms=24)[0]
        sub_rows = g.report_all(OP, "SubVI")
        sub_uids = {o["uid"]: o for o in sub_rows}
        cands = []
        for n, (u, _l, terms) in walk0.items():
            if u in sub_uids:
                names = [t for _ti, t, _w in terms if t]
                print(f"   SubVI node uid {u} (Nodes[] {n}, owner {sub_uids[u]['owner']}): {names}", flush=True)
                if any(t in names for t in ("Inputs", "Outputs", "Method Name", "Method ID", "Property Names")) \
                        and "GObject Refs" not in names:
                    cands.append(u)
        print(f"   creator candidates (by terminal signature): {cands}", flush=True)
        if len(cands) == 1:
            cu = cands[0]
            ci = [o["uid"] for o in sub_rows].index(cu)
            gone = step("2b delete the creator SubVI from the COPY", f"SubVI uid {cu} gone (1), ExecState 1 after RBW",
                        lambda: (g.delete_object(OP, "SubVI", ci), g.remove_bad_wires_scripted(OP), snap("after"))[2])
            still = cu in {o["uid"] for o in g.report_all(OP, "SubVI")}
            print(f"   creator uid {cu} still present after delete: {still}", flush=True)
            if still or g.exec_state(OP) != 1:
                print("STOP: creator not removable cleanly - rerun with the runtime-purge design (keep creator). "
                      "Nothing saved.", flush=True)
                return 3
        else:
            print("   creator not identified uniquely - keeping it (runtime purge protocol applies)", flush=True)

    sv = step("3 Property(SubVIs[]) on AbstractDiagram", "Property +1; ExecState 0 (reference unwired)",
              lambda: g.build_property(OP, "VI Server:AbstractDiagram", [(P_SUBVIS, False)], (1300, 300)))
    if not sv:
        return 3
    sv_uid = sv[-1]["uid"]
    step("4 wire Nodes[]-node 'reference out' -> SubVIs[]-node 'reference'", "Wire +1, ExecState 1",
         lambda: (g.wire(OP, "Property", pidx(nodes_uid), "reference out", "Property", pidx(sv_uid), "reference",
                         branch=ref_out_wired),
                  snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after the SubVIs[] node (ladder result not reproduced). Nothing saved.", flush=True)
        return 3

    # Peer point (d): with automatic error handling off, "valid empty diagram" and "SubVIs[] errored, outputs left
    # default" look identical from the arrays alone. Expose the SubVIs[] node's own `error out` (terminal 3 of a
    # property node: reference, reference out, error in, error out) as an indicator, BEFORE the loop exists so the
    # Nodes[] index is read from the same walk that found the node. A source terminal - not the sink trap of 09-14.
    err_label = None
    n_sv = step("4b Nodes[] index of the SubVIs[] node", "found by uid in the walk",
                lambda: next(n for n, (u, _l, _t) in g.net_map(OP, 0, max_nodes=80, max_terms=24)[0].items() if u == sv_uid))
    if n_sv is not None:
        before_labels = set(inds())
        step("4c indicator on SubVIs[]-node terminal 3 (error out)", "ControlTerminal +1, ExecState stays 1",
             lambda: (g.create_indicator(OP, n_sv, 3), snap("after"))[1])
        new_err = [l for l in inds() if l not in before_labels]
        print(f"   error indicator label(s): {new_err}", flush=True)
        if len(new_err) == 1 and g.exec_state(OP) == 1:
            err_label = new_err[0]
        else:
            print("STOP: error-out indicator did not land cleanly. Nothing saved (rerun after inspection).", flush=True)
            return 3

    step("5 empty For Loop", "ForLoop 0->1; ExecState 0 EXPECTED (no N yet)",
         lambda: (g.for_loop(OP, (1500, 250)), snap("after"))[1])
    dias = step("6 loop body diagram", "exactly one diagram owned by a ForLoop",
                lambda: [i for i, d in enumerate(g.report_all(OP, "Diagram")) if "For" in str(d.get("owner"))])
    if not dias or len(dias) != 1:
        print("STOP: loop body not found uniquely. Nothing saved.", flush=True)
        return 3
    body = dias[0]

    inner = step("7 Property(VI Name, VI Path, UID) on class SubVI INSIDE the body",
                 "Property +1 (GObject.UID accepted on a SubVI-class node, as Generic.Class Name is on OpReportAll's GObject node)",
                 lambda: g.build_property(OP, "VI Server:SubVI", [(P_VINAME, False), (P_VIPATH, False), (P_UID, False)],
                                          (1550, 300), diagram_index=body))
    uid_node = None
    if not inner:
        print("   fallback 7b: SubVI [VI Name, VI Path] + a separate GObject [UID] node", flush=True)
        STEPS.pop()                                   # the fallback decides, not the first attempt
        inner = step("7b Property(VI Name, VI Path) on class SubVI INSIDE the body", "Property +1",
                     lambda: g.build_property(OP, "VI Server:SubVI", [(P_VINAME, False), (P_VIPATH, False)],
                                              (1550, 300), diagram_index=body))
        if not inner:
            print("STOP: no inner property node. Nothing saved.", flush=True)
            return 3
        uid_node = step("7c Property(UID) on class GObject INSIDE the body, fed from the SubVI node's 'reference out'",
                        "Property +1, Wire +1",
                        lambda: g.build_property(OP, "VI Server:GObject", [(P_UID, False)], (1550, 500),
                                                 diagram_index=body))
    inner_uid = inner[-1]["uid"]
    # Peer point (b): ExecState alone cannot show that all three rows attached - read the node's terminals now.
    want = {T_VINAME, T_VIPATH} | (set() if uid_node else {T_UID})
    got = step("7-check inner node terminals (net_map of the body)", f"data terminals == {sorted(want)}",
               lambda: next(([t for _ti, t, _w in terms if t and t not in
                              ("reference", "reference out", "error in (no error)", "error out")]
                             for _i, (u, _l, terms) in g.net_map(OP, body, max_nodes=20, max_terms=24)[0].items()
                             if u == inner_uid), None))
    if got is None or set(got) != want:
        print(f"STOP: inner node rows are {got}, wanted {sorted(want)}. Nothing saved.", flush=True)
        return 3
    if uid_node:
        uid_uid = uid_node[-1]["uid"]
        step("7d wire inner 'reference out' -> UID node 'reference'", "Wire +1",
             lambda: (g.wire(OP, "Property", pidx(inner_uid), "reference out", "Property", pidx(uid_uid), "reference"),
                      snap("after"))[1])

    step("8 wire SubVIs[]-node 'SubVIs[]' -> inner 'reference' (CROSSES the loop boundary)",
         "LoopTunnel +1, Wire +2, ExecState 1 (the array supplies N)",
         lambda: (g.wire(OP, "Property", pidx(sv_uid), T_SUBVIS, "Property", pidx(inner_uid), "reference"),
                  snap("after"))[1])
    if g.exec_state(OP) != 1:
        print("STOP: not runnable after the loop input (SubVIs[] not auto-indexing as SubVI refs?). Nothing saved.",
              flush=True)
        for row in g.net_map(OP, body, max_nodes=20, max_terms=24)[0].items():
            print("   body node:", row, flush=True)
        return 3

    tun_uids_before = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    before_tun = len(tun_uids_before)
    outs = [T_VINAME, T_VIPATH] + ([] if uid_node else [T_UID])
    step(f"9 exit_loop for {outs}", f"LoopTunnel {before_tun}->{before_tun + len(outs)}",
         lambda: (g.exit_loop(OP, pidx(inner_uid), outs, body, node_class="Property"), snap("after"))[1])
    if uid_node:
        step("9b exit_loop for ['UID'] on the GObject node", "LoopTunnel +1",
             lambda: (g.exit_loop(OP, pidx(uid_uid), [T_UID], body, node_class="Property"), snap("after"))[1])
    if any(k == "exc" for _, k in STEPS):
        print("\nSTOP: a step missed its prediction. Nothing saved.", flush=True)
        return 4

    # Peer (archive/peer/2026-09-14-opsubvis-v0-plan.md): do not trust fixed tunnel indices - the output tunnels
    # are the LoopTunnel uids that did not exist before exit_loop, mapped back to Traverse indices.
    tun_rows = g.report_all(OP, "LoopTunnel")
    out_tuns = [o["i"] for o in tun_rows if o["uid"] not in tun_uids_before]
    print(f"\n== 10. tunnels now {len(tun_rows)}; output tunnels by census = indices {out_tuns}", flush=True)
    label_map = {}
    meanings = [T_VINAME, T_VIPATH, T_UID]
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
        print(f"   tunnel {tun} -> indicator {new_labels}  (expected to carry {meaning})", flush=True)
        for l in new_labels:
            label_map[l] = meaning

    step("11 auto error handling OFF", "no dialog on an empty diagram / invalid ref",
         lambda: g.set_auto_error_handling(OP, False))
    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    print("label map:", json.dumps(label_map), flush=True)
    if es != 1 or len(label_map) != 3:
        print(f"\nVERDICT: BROKEN (ExecState {es}, {len(label_map)} array indicators) - NOT SAVING.", flush=True)
        return 4
    if err_label:
        label_map[err_label] = "error"
    step("12 COM save", "written to disk", lambda: g.save(OP))
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    same = hashlib.md5(open(SRC, "rb").read()).hexdigest() == donor_md5
    print(f"donor {DONOR} md5 unchanged: {same}", flush=True)
    print(f"\nVERDICT: OpSubVIs_{VER} BUILT and SAVED (structural only - run tools/bench/test_opsubvis.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
