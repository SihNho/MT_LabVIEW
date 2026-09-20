"""probe_builder_artifact.py - what does ONE build_property call leave on the target, and does v0 do it too?

MEASURED (tools/bench/probe_castfree4.log), identically for two questioned properties AND a control:
    pristine 1/9  ->  build_property 0/9  ->  wire 0/10  ->  Remove Bad Wires 0/10  ->  delete node 0/9
Removing everything intentionally added does not restore the VI, so the builder leaves another mutation.
Peer review in flight: archive/peer/2026-09-14-builder-leaves-artifact.md.

This probe MEASURES the artifact instead of guessing it, with the one reader that does see new objects
(report_all, a class traversal): counts per class at each step, for BOTH builder versions -
    v1 = OpBuildPN_v1 (creator error + Outputs exposed; current gscript default)
    v0 = OpBuildPN_v0 (yesterday's builder)
- so "v1 introduced it" vs "the creator always did it" is decided by the diff, and the class that grows names
the artifact. Note Traverse classes that have been validated: Constant, DigitalNumericConstant, NumericConstant,
StringConstant, Invoke, Property, Wire, Node, Terminal, ControlTerminal, Diagram, SubVI, Function, IndexArray.

Scratch deleted, nothing saved.
  py tools/bgrun.py --max-min 12 --log tools/bench/probe_builder_artifact.log -- py -u tools/recipes/probe_builder_artifact.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_artifact.vi")
V0 = os.path.join(g.CLAUDEDEV, "OpBuildPN_v0.vi")
V1 = os.path.join(g.CLAUDEDEV, "OpBuildPN_v1.vi")
CLASSES = ["Node", "Property", "Invoke", "Wire", "Constant", "DigitalNumericConstant", "StringConstant",
           "Terminal", "ControlTerminal", "Diagram", "SubVI", "Function", "IndexArray", "GObject"]
g._run.__defaults__ = (6.0, 120.0)


def census(tag):
    row = {}
    for c in CLASSES:
        try:
            row[c] = len(g.report_all(S, c))
        except Exception:
            row[c] = "?"
    es = g.exec_state(S)
    print(f"   {tag:36} ExecState={es}  " + " ".join(f"{c}={row[c]}" for c in CLASSES), flush=True)
    return es, row


def diff(a, b):
    return {c: (a[c], b[c]) for c in CLASSES if a[c] != b[c]}


def run(builder_path, label):
    print(f"\n######## {label}: {os.path.basename(builder_path)} ########", flush=True)
    g.OP_BUILD_PN = builder_path
    try:
        g.close_panel(S)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(S):
        try:
            os.remove(S)
        except OSError:
            pass
    shutil.copyfile(SRC, S)
    g.open_panel(S)
    time.sleep(0.9)
    e0, c0 = census("pristine")
    if e0 != 1:
        print("   INVALID: donor not runnable", flush=True)
        return
    new = g.build_property(S, "VI Server:GObject", [("632A800", False)], (1300, 300))[-1]["uid"]
    e1, c1 = census("after build_property (control prop)")
    print(f"      objects ADDED by the builder: {diff(c0, c1)}", flush=True)
    g.remove_bad_wires_scripted(S)
    e2, c2 = census("after Remove Bad Wires")
    g.delete_object(S, "Property", [o["uid"] for o in g.report(S, "Property")].index(new))
    g.remove_bad_wires_scripted(S)
    e3, c3 = census("after deleting the new node + RBW")
    print(f"      objects still differing from pristine: {diff(c0, c3)}", flush=True)
    print(f"   VERDICT ({label}): {'target RESTORED to runnable' if e3 == 1 else 'target stays BROKEN'}; "
          f"leftover classes {list(diff(c0, c3).keys()) or 'none'}", flush=True)
    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
    except Exception as e:
        print("   cleanup:", str(e)[:80], flush=True)


def run_netmap_only():
    """docs/keystone-op-spec.md s33: OpNetInfo runs drop an untyped junk Invoke on the TARGET, and an Invoke with
    no method is enough to break a VI. Every ladder probe called net_map (node_with_terminal) right after its
    pristine ExecState read - so the breakage may never have been the builder's. Measure exactly that."""
    print("\n######## net_map ONLY (no build): does the walker itself break the target? ########", flush=True)
    try:
        g.close_panel(S)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(S):
        try:
            os.remove(S)
        except OSError:
            pass
    shutil.copyfile(SRC, S)
    g.open_panel(S)
    time.sleep(0.9)
    e0, c0 = census("pristine")
    g.net_map(S, 0, max_nodes=40, max_terms=10)
    e1, c1 = census("after ONE net_map call")
    print(f"      objects ADDED by net_map: {diff(c0, c1)}", flush=True)
    junk = g.new_since(S, "Invoke", [])
    g.remove_bad_wires_scripted(S)
    e2, c2 = census("after Remove Bad Wires")
    for o in g.report_all(S, "Invoke"):
        try:
            g.delete_object(S, "Invoke", [x["uid"] for x in g.report(S, "Invoke")].index(o["uid"]))
        except Exception as ex:
            print("      delete junk Invoke failed:", str(ex)[:80], flush=True)
    g.remove_bad_wires_scripted(S)
    e3, c3 = census("after deleting Invoke(s) + RBW")
    print(f"   VERDICT (net_map only): {'net_map BREAKS the target and purging Invokes RESTORES it' if (e1 == 0 and e3 == 1) else 'see rows'}",
          flush=True)
    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
    except Exception as e:
        print("   cleanup:", str(e)[:80], flush=True)


def main():
    g._lv = None
    keep = g.OP_BUILD_PN
    try:
        run_netmap_only()
        g._lv = None
        run(V1, "v1 (current)")
        g._lv = None
        run(V0, "v0 (yesterday's)")
    finally:
        g.OP_BUILD_PN = keep
    print("\nscratch deleted", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
