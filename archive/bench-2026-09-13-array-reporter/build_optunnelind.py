"""build_optunnelind.py - OpTunnelInd_v0.vi: create a correctly-typed INDICATOR wired to a loop TUNNEL.

THE MISSING OP. OpReportAll_v0 needs its auto-indexed output tunnels to end in ARRAY indicators, because a COM
caller reads results with GetControlValue(label). Everything else is already built and verified:

    exit_loop(node_class="Property", ["Position"])   ->  the auto-indexed OUTPUT tunnel   (verified 2026-09-13)
    set_index_mode(target, tunnel_index, 1)          ->  force auto-indexing              (op exists since 08-31)
    <MISSING>                                        ->  an indicator ON that tunnel

WHY create_indicator DOES NOT DO THIS, measured today rather than assumed. `OpCreateIndicator_v0` addresses
VI -> Block Diagram -> Nodes[] -> Terminals[], and a sweep of a For Loop's Terminals[0..13] produced DANGLING
indicators for 0-7 (a front-panel object appeared but NO new wire) and nothing for 8+. The peer review explained
it exactly: `ForLoop.Terminals[]` are the loop's own infrastructure terminals, and **a Tunnel is a GObject, not a
Terminal**, so it inherits no Terminal methods. The documented route adds one hop:

    Tunnel.Outside Terminal   property 6356001   ->  Terminal ref
    Terminal.Create Indicator method   6349C02   ->  the indicator, wired

DONOR: OpSetIndexMode_v0, because its front half is already exactly right and proven -
`Traverse('LoopTunnel', index) -> IndexArray -> To More Specific Class`. Only the tail differs: the donor writes
IndexMode there; this op reads Outside Terminal and invokes Create Indicator. Inventory read from a FILE COPY
(never point an op at a live op - error 6500):

    SubVI 124  Traverse for GObjects      IndexArray 308            Function 683  To More Specific Class
    Property 220  IndexMode WRITE  <- deleted here      ControlTerminal 1056  the value control, also unused now

INDEX MODE IS NOT ASSUMED. NI says For Loop output tunnels normally default to indexing when created by wiring,
but "normally" is not a contract, and the datatype of the indicator depends on it entirely. The caller sets it
explicitly with the existing set_index_mode op before calling this one.

SAFETY: builds a NEW file; OpSetIndexMode_v0 is never modified. Saves only if ExecState == 1.
  py tools/bgrun.py --max-min 15 --log tools/bench/build_optunnelind.log -- py -u tools/recipes/build_optunnelind.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpSetIndexMode_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpTunnelInd_v0.vi")
OUTSIDE_TERMINAL = "6356001"      # Tunnel.Outside Terminal (read)
CREATE_INDICATOR = "6349C02"      # Terminal.Create Indicator
CAST_UID = 683                    # To More Specific Class, from the donor inventory
PROP_UID = 220                    # the donor's IndexMode WRITE property node - deleted

# TERMINAL NAMES, read off the machine by net_map after v1 failed BOTH wires with error 5001 (name not found).
# Both of my guesses were wrong, and in the same way: LabVIEW uses the SHORT name, not the documentation's.
#     guessed "specific class reference out"  ->  actually `specific class reference`
#     guessed "Outside Terminal"              ->  actually `Outer Term`
# This is exactly what docs/NAMES.md exists for; the names are pinned here rather than re-guessed.
T_CAST_OUT = "specific class reference"
T_OUTER = "Outer Term"
g._run.__defaults__ = (6.0, 60.0)

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


def idx(cls, uid):
    """Index of `uid` within report(cls) - the ops address by INDEX, but UIDs are what survive edits."""
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def snap(tag=""):
    return (f"{tag} Property={g.count(OP,'Property')} Invoke={g.count(OP,'Invoke')} "
            f"Wire={g.count(OP,'Wire')} ExecState={g.exec_state(OP)}")


def main():
    g._lv = None
    try:
        g.close_panel(OP)
    except Exception:
        pass
    if os.path.exists(OP):
        try:
            os.remove(OP)              # never load the target before overwriting it
        except OSError as e:
            print(f"cannot replace {OP}: {e}", flush=True)
            return 1
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)                   # a target loaded only via GetVIReference declines edits SILENTLY
    time.sleep(1.0)
    print(snap("start:"), flush=True)

    # 1. strip the donor's tail: the IndexMode WRITE property node and the wires it orphans.
    step("1 delete the donor's IndexMode property node",
         "Property 1->0, then ExecState 0 until the replacement is wired (broken is EXPECTED here)",
         lambda: (g.delete_object(OP, "Property", idx("Property", PROP_UID)),
                  g.remove_bad_wires_scripted(OP), snap("after"))[2])

    # 2. Tunnel.Outside Terminal (READ) - the hop that create_indicator was missing.
    prop = step("2 Property(Tunnel.Outside Terminal) READ",
                "Property 0->1",
                lambda: g.build_property(OP, "VI Server:Tunnel", [(OUTSIDE_TERMINAL, False)], (740, 250)))
    if not prop:
        print("\nSTOP: could not create the Outside Terminal property node - is the class name right?", flush=True)
        print("Try 'VI Server:LoopTunnel'. Nothing has been saved.", flush=True)
        return 2
    prop_uid = prop[-1]["uid"] if isinstance(prop, list) else None

    # 3. the cast's LoopTunnel output feeds it. LoopTunnel IS-A Tunnel, so a Tunnel-class property node accepts it.
    step("3 wire To More Specific Class -> the property node's `reference`",
         "Wire +1",
         lambda: g.wire(OP, "Function", idx("Function", CAST_UID), T_CAST_OUT,
                        "Property", idx("Property", prop_uid), "reference"))

    # 4. Terminal.Create Indicator on that terminal.
    inv = step("4 Invoke(Terminal.Create Indicator)",
               "Invoke 0->1",
               lambda: g.build_invoke(OP, "VI Server:Terminal", CREATE_INDICATOR, (900, 250)))
    if not inv:
        print("\nSTOP: no Invoke node. Nothing saved.", flush=True)
        return 3
    inv_uid = inv[-1]["uid"]

    # COUNT AUDIT. v1's end-of-run snapshot read `Invoke=75` while net_map showed only 7 nodes on the diagram -
    # the signature of a creator that SPRAYED objects, which is exactly how the earlier `Control.Value` attempt
    # failed (Node count 8 -> 224, node present but with no usable terminal). Measure it here rather than
    # discovering it after a save.
    n_inv = g.count(OP, "Invoke")
    print(f"   Invoke count now {n_inv} (expected 1). net_map node list follows if this looks sprayed.",
          flush=True)
    if n_inv > 3:
        print("   !! SPRAY SUSPECTED - dumping the diagram before going further", flush=True)
        try:
            for row in g.net_map(OP, 0, max_nodes=40, max_terms=20):
                print("   ", row, flush=True)
        except Exception as e:
            print("   net_map EXC", str(e)[:200], flush=True)

    step("5 wire the property's `Outer Term` -> the Invoke's `reference`",
         "Wire +1; a wrong terminal NAME is declined SILENTLY, so the wire count is the check",
         lambda: g.wire(OP, "Property", idx("Property", prop_uid), T_OUTER,
                        "Invoke", idx("Invoke", inv_uid), "reference"))

    # The error chain: without it the property node's own error reaches an unwired `error out` and LabVIEW pops
    # the automatic-error-handling dialog on EVERY call, which is how ops end up hanging a batch for 8 s a time.
    step("5a wire the property's `error out` -> the Invoke's `error in (no error)`",
         "Wire +1 - keeps the two nodes ordered and carries the error forward",
         lambda: g.wire(OP, "Property", idx("Property", prop_uid), "error out",
                        "Invoke", idx("Invoke", inv_uid), "error in (no error)"))
    step("5b silence automatic error handling on THIS op",
         "the Invoke's unwired `error out` can no longer raise a modal dialog per call",
         lambda: (g.set_auto_error_handling(OP, False), "auto error handling off")[1])

    # Names are the usual silent-failure mode, so dump them whenever anything above missed.
    if any(k == "exc" for _, k in STEPS):
        print("\n-- terminal names on the top-level diagram (diagnosis for a silent name mismatch) --", flush=True)
        try:
            for row in g.net_map(OP, 0, max_nodes=40, max_terms=20):
                print("   ", row, flush=True)
        except Exception as e:
            print("   net_map EXC", str(e)[:200], flush=True)

    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    if es != 1:
        print("\nVERDICT: BROKEN - NOT SAVING. The file on disk is still the untouched donor copy.", flush=True)
        return 4

    step("6 COM save", "the op is written to disk", lambda: g.save(OP))
    print("\nVERDICT: OpTunnelInd_v0 assembled and runnable (STRUCTURAL only - it has not been CALLED yet).",
          flush=True)
    print("Next: call it against a scratch VI that has a real auto-indexed output tunnel, and read the new", flush=True)
    print("indicator's VALUE over COM - an empty tuple () proves an ARRAY, a 2-tuple proves it stayed scalar.",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
