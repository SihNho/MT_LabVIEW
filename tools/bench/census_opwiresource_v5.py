r"""census_opwiresource_v5.py - read OpWireSource_v5's own diagram, so OpOwnerChain_v0 can be cut from it.

WHY. docs/diagram-hierarchy.md now says in writing that every ancestry chain stops at the same missing link: a
diagram's owning STRUCTURE is known, but the diagram that structure itself lives on is not, and position matching
cannot supply it in this VI (structures sit tens of pixels apart; 41 of 170 diagrams are unresolved). The reader
that supplies it is `OpOwnerChain_v0`: a UID in, its owner's UID and class out.

OpWireSource_v5 ALREADY contains that chain - `UID to GObject Reference.vi` -> ... -> `Generic.Owner` 6327806 ->
`ClassName` + cast(GObject) -> `UID` - with a Wire cast and a `Wire.Terms[]` / Index Array / `Is Source?` /
`Connected Wire` section in front of it. OpOwnerChain is that VI with the front section removed and the reference
routed straight into the Owner node. Deleting nodes and re-wiring are both proven operations (step 0a).

This census is the name-resolution pass the work cycle demands BEFORE the recipe is written: every node, its label
and its terminals, so the surgical edit addresses real objects instead of guessed indices - the mistake that cost
step 0a three runs.

READ-ONLY: OpWireSource_v5.vi is opened by reference and traversed. Nothing is created, modified or saved.
  py tools/bgrun.py --max-min 10 --log tools/bench/census_opwiresource_v5.log -- py -u tools/bench/census_opwiresource_v5.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SRC = os.path.join(CLAUDEDEV, "OpWireSource_v5.vi")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    if not os.path.exists(SRC):
        print("STOP: OpWireSource_v5.vi not found", flush=True)
        return 3
    print(f"{os.path.basename(SRC)}  ExecState {g.exec_state(SRC)}", flush=True)

    # `PropertyNode` / `InvokeNode` are NOT VI Server class names - they raise error 1092 in Traverse for GObjects
    # (measured 2026-09-16, tools/bench/diag_autofocus_panel.log; hierarchy in docs/NAMES.md). The real names are
    # `Property` and `Invoke`, and this file's own log line 11 has recorded the 1092 since it was first run.
    for cls in ("Diagram", "SubVI", "Property", "Invoke", "IndexArray", "Function", "ControlTerminal"):
        try:
            objs = g.report_all(SRC, cls)
            print(f"\n== {cls}: {len(objs)}", flush=True)
            for o in objs[:40]:
                print(f"   i={o['i']:3} uid={o['uid']:6} class={o['class']:22} owner={o['owner']:16} pos={o['pos']}",
                      flush=True)
        except Exception as e:
            print(f"\n== {cls}: raised {e}", flush=True)

    print("\n== panel controls ==", flush=True)
    try:
        for c in g.panel_wiring(SRC):
            print(f"   {c}", flush=True)
    except Exception as e:
        print(f"   panel_wiring raised: {e}", flush=True)

    print("\n== top-level diagram net map (nodes -> terminals -> wires) ==", flush=True)
    try:
        nodes, nets = g.net_map(SRC, diagram_index=0, max_nodes=80, max_terms=30)
        for k in sorted(nodes):
            uid, lbl, terms = nodes[k]
            print(f"   node {k:3} uid {uid:6} {lbl!r}", flush=True)
            for ti, nm, w in terms:
                print(f"        t{ti:<3} {nm!r:38} wire {w}", flush=True)
    except Exception as e:
        print(f"   net_map raised: {e}", flush=True)
    g._lv = None
    return 0


if __name__ == "__main__":
    sys.exit(main())
