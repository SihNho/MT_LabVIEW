"""inspect_setindexmode.py - read OpSetIndexMode_v0's skeleton, so the tunnel-indicator op can be built from it.

WHY THIS OP IS THE RIGHT DONOR. OpCreateIndicator_v0 reaches its terminal the wrong way for our purpose -
VI -> Block Diagram -> Nodes[] -> Terminals[] - and today's probe proved a For Loop's Terminals[] does not expose
the auto-indexed OUTPUT tunnel (indices 0-7 create DANGLING indicators, no wire; 8+ nothing).

OpSetIndexMode_v0 reaches a tunnel the right way and is already proven in the fleet:
    Traverse('LoopTunnel', index) -> cast -> IndexMode WRITE property node
So the op that is missing is that same front half with `Terminal.Create Indicator` (6349C02) in place of the
IndexMode property node. This script reads the donor's actual object inventory so the build recipe can name
UIDs instead of guessing them.

RULE OBSERVED (CLAUDE.md, learned the hard way 2026-09-13): **never point an op at another op VI** - an op is a
RUNNING VI, LabVIEW refuses with error 6500 and can leave the op wedged, and `revert()` then fails with 6573.
So this inspects a FILE COPY, never the live op.

  py tools/bgrun.py --max-min 8 --log tools/bench/inspect_setindexmode.log -- py -u tools/recipes/inspect_setindexmode.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpSetIndexMode_v0.vi")
COPY = os.path.join(g.CLAUDEDEV, "SCRATCH_sim_inspect.vi")
g._run.__defaults__ = (6.0, 45.0)


def main():
    g._lv = None
    try:
        g.close_panel(COPY)
    except Exception:
        pass
    if os.path.exists(COPY):
        try:
            os.remove(COPY)
        except OSError:
            pass
    shutil.copyfile(SRC, COPY)
    g.open_panel(COPY)
    time.sleep(0.9)

    print("ExecState:", g.exec_state(COPY), flush=True)
    for cls in ("SubVI", "Property", "Invoke", "IndexArray", "Node", "Wire", "ControlTerminal",
                "Constant", "StringConstant", "Function"):
        try:
            objs = g.report(COPY, cls)
        except Exception as e:
            print(f"\n{cls}: EXC {str(e)[:120]}", flush=True)
            continue
        print(f"\n{cls}  n={len(objs)}", flush=True)
        for o in objs:
            print(f"    uid={o['uid']:<6} pos={str(o['pos']):<14} owner={o['owner']}", flush=True)

    print("\n--- front panel ---", flush=True)
    try:
        for row in g.fp_labels(COPY):
            print("   ", row, flush=True)
    except Exception as e:
        print("   EXC", str(e)[:150], flush=True)

    print("\n--- node styles (names of the primitives) ---", flush=True)
    try:
        for row in g.node_info(COPY):
            print("   ", row, flush=True)
    except Exception as e:
        print("   EXC", str(e)[:150], flush=True)

    try:
        g.close_panel(COPY)
        time.sleep(0.4)
        os.remove(COPY)
        print("\nscratch copy deleted", flush=True)
    except Exception as e:
        print("\nscratch cleanup:", str(e)[:120], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
