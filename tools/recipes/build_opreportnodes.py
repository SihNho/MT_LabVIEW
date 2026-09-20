"""build_opreportnodes.py - OpReportNodes_v0.vi: every node of ONE diagram, WITH ITS NAME, as arrays.

THE POINT. The inventory needs names, and `report_all` gives none. The obvious route - `Traverse('SubVI')` into a
`SubVI.VI Name` property node - is BLOCKED, and that is now measured rather than suspected:

    Traverse returns GObject-typed references. A SubVI-class property node fed one goes to ExecState 0.
    (tools/bench/build_opreportsubvi2.log, 2026-09-14: wire correct, node broken.)

The fix cannot be a `To More Specific Class` cast, because the cast needs a class-specifier constant set to
`SubVI`, and setting one needs a ClassSpecifierConstant-class property node, which needs a cast. A circle.

**`Nodes[]` breaks the circle**: `AbstractDiagram.Nodes[]` (6375809) returns **Node**-typed references directly,
so a Node-class property node accepts them with no cast at all. And `Node.Label` carries what we want - probed
2026-09-14 on OpReport_v3:

    (1, 'Unknown', 'Traverse for GObjects.vi')      <- Style is 'Unknown' for a subVI; LABEL is the VI name

DONOR: OpSetLabel_v0, whose ladder is already exactly right and, unlike OpNodeInfo_v0, takes a **diagram index**
so every sub-diagram can be reached, not just the top level:

    Open VI Ref -> Traverse('Diagram') -> Index Array -> To More Specific Class(Diagram)
                -> Nodes[] -> Index Array -> Node -> PN Node.Label -> PN Text.Text

The donor WRITES Text.Text; this op reads. So its two per-node property nodes are deleted and rebuilt inside a
For Loop fed by `Nodes[]`, exactly the transformation that produced OpReportAll_v0.

UIDS ARE DISCOVERED, NOT HARD-CODED. The last two builds were derailed by identifying nodes positionally or by
`report()[0]` (which is not creation order, and returned the node I had just made - the op then wired itself to
itself and the failure looked like a LabVIEW limitation). Here every node is found by the TERMINAL NAMES net_map
reports, which is a structural fact rather than an ordering assumption.

  py tools/bgrun.py --max-min 25 --log tools/bench/build_opreportnodes.log -- py -u tools/recipes/build_opreportnodes.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpSetLabel_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpReportNodes_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opreportnodes_labels.json")

P_LABEL = "6359001"      # Node.Label   -> a Text refnum
P_STYLE = "6359009"      # Node.Style
P_TEXT = "632D800"       # Text.Text
T_LABEL, T_STYLE, T_TEXT = "Label", "Style", "Text"

g._run.__defaults__ = (6.0, 120.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   OBSERVED: {obs}", flush=True)
        STEPS.append((name, "ok"))
        return obs
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:260]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def snap(tag=""):
    return (f"{tag} ForLoop={g.count(OP,'ForLoop')} LoopTunnel={g.count(OP,'LoopTunnel')} "
            f"Property={g.count(OP,'Property')} IndexArray={g.count(OP,'IndexArray')} "
            f"CtlTerm={g.count(OP,'ControlTerminal')} Wire={g.count(OP,'Wire')} ExecState={g.exec_state(OP)}")


def find_node_with_terminal(diagram, term_name):
    """UID of the node on `diagram` that has a terminal literally named `term_name`.

    Structural identification - the alternative (index order, or position) is what broke the last two builds.
    """
    nodes, _wires = g.net_map(OP, diagram, max_nodes=40, max_terms=24)
    for _i, (uid, _lbl, terms) in nodes.items():
        for _ti, tname, _w in terms:
            if tname == term_name:
                return uid
    return None


def wire_on_terminal(diagram, uid, term_name):
    """The wire id attached to `term_name` of node `uid`, or 0 if unwired."""
    nodes, _wires = g.net_map(OP, diagram, max_nodes=40, max_terms=24)
    for _i, (u, _lbl, terms) in nodes.items():
        if u != uid:
            continue
        for _ti, tname, w in terms:
            if tname == term_name:
                return w
    return 0


def consumer_of_wire(diagram, wire_id, cls_terminal="array"):
    """UID of the node whose `cls_terminal` sits on `wire_id`.

    Needed because the donor has THREE Index Arrays and only ONE of them consumes `Nodes[]`. Run 1 of this
    recipe picked "the last uid in report order" and deleted the diagram-selecting Index Array instead, which
    orphaned the cast and left the VI broken with every step still reporting 'ok' - a silent wrong target is
    exactly the failure mode structural identification exists to prevent.
    """
    nodes, _wires = g.net_map(OP, diagram, max_nodes=40, max_terms=24)
    for _i, (u, _lbl, terms) in nodes.items():
        for _ti, tname, w in terms:
            if tname == cls_terminal and w == wire_id and w != 0:
                return u
    return None


def delete_by_uid(cls, uid):
    uids = [o["uid"] for o in g.report(OP, cls)]
    if uid in uids:
        g.delete_object(OP, cls, uids.index(uid))
        return True
    return False


def orphan_index_arrays():
    """Index Arrays whose `array` input is unwired - leftovers that keep the VI broken."""
    nodes, _wires = g.net_map(OP, 0, max_nodes=40, max_terms=24)
    out = []
    for _i, (u, _lbl, terms) in nodes.items():
        arr = [w for _ti, tname, w in terms if tname == "array"]
        el = [w for _ti, tname, w in terms if tname == "element"]
        if arr and el and arr[0] == 0:
            out.append(u)
    return out


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def dump(why):
    print(f"\n-- net_map ({why}) --", flush=True)
    for d in range(0, 3):
        try:
            print(f"   diagram {d}:", flush=True)
            for row in g.net_map(OP, d, max_nodes=40, max_terms=24):
                print("     ", row, flush=True)
        except Exception as e:
            print(f"     diagram {d}: {str(e)[:120]}", flush=True)


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
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)
    time.sleep(1.0)
    print(snap("start:"), flush=True)

    nodes_pn = find_node_with_terminal(0, "Nodes[]")
    print(f"the node carrying `Nodes[]` is uid {nodes_pn}", flush=True)
    if nodes_pn is None:
        dump("cannot find the Nodes[] property node in the donor")
        return 2

    # 1. free `Nodes[]` by deleting the Index Array THAT CONSUMES IT - identified by the wire, not by position
    #    in a list. The donor has three Index Arrays; run 1 deleted "the last uid" and removed the
    #    diagram-selecting one instead, which orphaned the cast. Every step still said 'ok'.
    nodes_wire = wire_on_terminal(0, nodes_pn, "Nodes[]")
    victim = consumer_of_wire(0, nodes_wire, "array")
    print(f"`Nodes[]` is wire {nodes_wire}; the Index Array consuming it is uid {victim}", flush=True)
    if victim is None:
        dump("cannot identify the Index Array that consumes Nodes[]")
        return 2
    step(f"1 delete Index Array {victim} (the one on wire {nodes_wire})", "IndexArray -1",
         lambda: (delete_by_uid("IndexArray", victim), g.remove_bad_wires_scripted(OP), snap("after"))[2])

    # The donor's Node.Label / Text.Text pair must go: they read ONE node and they WRITE the text.
    keep = {nodes_pn}
    doomed = [o["uid"] for o in g.report(OP, "Property") if o["uid"] not in keep]
    print(f"property nodes to delete: {doomed} (keeping {sorted(keep)})", flush=True)
    for uid in doomed:
        cur = [o["uid"] for o in g.report(OP, "Property")]
        if uid in cur:
            step(f"2 delete donor property node {uid}", "Property -1",
                 lambda i=cur.index(uid): (g.delete_object(OP, "Property", i),
                                           g.remove_bad_wires_scripted(OP), snap("after"))[2])

    step("3 empty For Loop", "ForLoop 0->1; ExecState 0 expected until N is supplied",
         lambda: (g.for_loop(OP, (1500, 900)), snap("after"))[1])
    dias = step("4 find the loop body diagram", "one diagram owned by a ForLoop",
                lambda: [i for i, d in enumerate(g.report(OP, "Diagram")) if "For" in str(d.get("owner"))])
    if not dias:
        dump("no loop body")
        return 3
    body = dias[0]

    pn_node = step("5 Property(Node.Label, Node.Style) INSIDE the loop body",
                   "Property +1 - a NODE-class node, which `Nodes[]` elements satisfy with NO cast",
                   lambda: g.build_property(OP, "VI Server:Node", [(P_LABEL, False), (P_STYLE, False)],
                                            (1550, 950), diagram_index=body))
    if not pn_node:
        dump("no Node property node")
        return 4
    pn_node_uid = pn_node[-1]["uid"]

    def pidx(uid):
        return [o["uid"] for o in g.report(OP, "Property")].index(uid)

    step("6 wire `Nodes[]` -> that node's `reference` (CROSSES the loop boundary)",
         "LoopTunnel 0->1, Wire +2, ExecState -> 1 because the array now supplies N",
         lambda: (g.wire(OP, "Property", pidx(nodes_pn), "Nodes[]",
                         "Property", pidx(pn_node_uid), "reference"), snap("after"))[1])

    pn_text = step("7 Property(Text.Text) INSIDE the body - Node.Label returns a Text REFNUM, not a string",
                   "Property +1",
                   lambda: g.build_property(OP, "VI Server:Text", [(P_TEXT, False)],
                                            (1550, 1150), diagram_index=body))
    pn_text_uid = pn_text[-1]["uid"] if pn_text else None
    if pn_text_uid is not None:
        step("8 wire Node.`Label` -> the Text node's `reference`",
             "Wire +1, LoopTunnel unchanged (both inside the body)",
             lambda: (g.wire(OP, "Property", pidx(pn_node_uid), T_LABEL,
                             "Property", pidx(pn_text_uid), "reference"), snap("after"))[1])

    before_tun = g.count(OP, "LoopTunnel")
    step("9 exit_loop: auto-indexed tunnel for Node.Style", "LoopTunnel +1",
         lambda: (g.exit_loop(OP, pidx(pn_node_uid), [T_STYLE], body, node_class="Property"), snap("after"))[1])
    if pn_text_uid is not None:
        step("10 exit_loop: auto-indexed tunnel for the label Text", "LoopTunnel +1",
             lambda: (g.exit_loop(OP, pidx(pn_text_uid), [T_TEXT], body, node_class="Property"),
                      snap("after"))[1])

    # Deleting the donor's per-node property nodes leaves Index Arrays with nothing feeding them. An Index Array
    # whose `array` input is unwired is BROKEN, and that alone holds ExecState at 0 while every step reports ok.
    orphans = orphan_index_arrays()
    if orphans:
        step(f"10a delete {len(orphans)} orphaned Index Array(s) {orphans}",
             "IndexArray count drops; these are donor leftovers with no `array` input",
             lambda: ([delete_by_uid("IndexArray", u) for u in orphans],
                      g.remove_bad_wires_scripted(OP), snap("after"))[2])

    if any(k == "exc" for _, k in STEPS):
        dump("a step missed its prediction")

    n_tun = g.count(OP, "LoopTunnel")
    label_map = {}
    meanings = ["Style", "Label text"]
    print(f"\n== 11. array indicators for tunnels {before_tun}..{n_tun - 1}", flush=True)
    for k, tun in enumerate(range(before_tun, n_tun)):
        before_labels = set(inds())
        try:
            g.set_index_mode(OP, tun, 1)
        except Exception as e:
            print(f"   tunnel {tun}: set_index_mode {str(e)[:110]}", flush=True)
        try:
            g.tunnel_indicator(OP, tun)
        except Exception as e:
            print(f"   tunnel {tun}: tunnel_indicator FAILED {str(e)[:180]}", flush=True)
            continue
        new_labels = [l for l in inds() if l not in before_labels]
        meaning = meanings[k] if k < len(meanings) else f"tunnel {tun}"
        print(f"   tunnel {tun} -> {new_labels}  ({meaning})", flush=True)
        for l in new_labels:
            label_map[l] = meaning

    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    print("label map:", json.dumps(label_map, indent=2), flush=True)
    if es != 1:
        dump("BROKEN at the end")
        print("\nVERDICT: BROKEN - NOT SAVING. OpSetLabel_v0 is untouched.", flush=True)
        return 5

    step("12 silence automatic error handling", "no modal dialog on a node whose property errors",
         lambda: (g.set_auto_error_handling(OP, False), "off")[1])
    step("13 COM save", "written to disk", lambda: g.save(OP))
    try:
        with open(MAP_OUT, "w", encoding="utf-8") as f:
            json.dump(label_map, f, indent=2)
        print("label map written:", MAP_OUT, flush=True)
    except OSError as e:
        print("could not write the label map:", e, flush=True)
    print("\nVERDICT: OpReportNodes_v0 assembled and saved - STRUCTURAL, not yet called.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
