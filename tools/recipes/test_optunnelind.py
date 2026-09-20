"""test_optunnelind.py - does OpTunnelInd_v0 actually produce an ARRAY indicator? FUNCTIONAL test.

The build recipe proved only that the op ASSEMBLES (ExecState 1). CLAUDE.md is explicit that structural is not
functional, and here the distinction is the entire result: an indicator that came out SCALAR would look identical
to one that came out an ARRAY in every count-based check, and would silently give OpReportAll_v0 the wrong
datatype - the exact bug class this whole task exists to avoid.

PROTOCOL
  1. build a scratch VI to end-of-step-7   (For Loop, Property inside, input tunnel, ExecState 1)
  2. exit_loop                             -> the auto-indexed OUTPUT tunnel
  3. set_index_mode(tunnel, 1)             -> force auto-indexing rather than trusting the default
  4. tunnel_indicator(tunnel)              -> the op under test
  5. read the new indicator's VALUE over COM

STEP 5 IS THE ACTUAL TEST. `fp_labels` reports a label and an is-indicator flag but no datatype, so the type is
read functionally. On a never-run VI the defaults discriminate cleanly:

      Position as a SCALAR cluster of two I32   ->  (0, 0)        <- FAILURE: the tunnel did not auto-index
      Position AUTO-INDEXED into an ARRAY       ->  ()            <- SUCCESS: an empty array

Both tunnels are tried, because which LoopTunnel index is the OUTPUT one is not established - the input tunnel
was created first, but index order is an assumption until measured, and mislabelling them would make a pass look
like a fail.

SAFETY: scratch copy, deleted at the end. No original and no live op is edited.
  py tools/bgrun.py --max-min 15 --log tools/bench/test_optunnelind.log -- py -u tools/recipes/test_optunnelind.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_tunnelind_target.vi")
POSITION_ID = "632A800"
g._run.__defaults__ = (6.0, 60.0)


def snap(tag=""):
    return (f"{tag} LoopTunnel={g.count(TGT,'LoopTunnel')} CtlTerm={g.count(TGT,'ControlTerminal')} "
            f"Wire={g.count(TGT,'Wire')} ExecState={g.exec_state(TGT)}")


def build_target():
    try:
        g.close_panel(TGT)
        time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(TGT):
        try:
            os.remove(TGT)
        except OSError as e:
            print(f"   (cannot remove scratch: {e})", flush=True)
    shutil.copyfile(SRC, TGT)
    time.sleep(0.3)
    g.open_panel(TGT)
    time.sleep(0.9)
    g.delete_object(TGT, "IndexArray", 0)
    g.remove_bad_wires_scripted(TGT)
    for _ in range(g.count(TGT, "Property")):
        g.delete_object(TGT, "Property", 0)
    g.remove_bad_wires_scripted(TGT)
    g.for_loop(TGT, (1400, 900))
    body = [i for i, d in enumerate(g.report(TGT, "Diagram")) if "For" in str(d.get("owner"))][0]
    g.build_property(TGT, "VI Server:GObject", [(POSITION_ID, False)], (1450, 950), diagram_index=body)
    pidx = g.count(TGT, "Property") - 1
    g.wire(TGT, "SubVI", 0, "References", "Property", pidx, "reference")
    g.exit_loop(TGT, pidx, ["Position"], body, node_class="Property")
    return body, pidx


def read_indicator_values(known_before):
    """Every indicator's COM value, flagged as array or not. `known_before` are labels that already existed."""
    out = []
    try:
        ref = g.lv().GetVIReference(TGT, "", False, 0)
    except Exception as e:
        print(f"   cannot open a VI reference to read values: {str(e)[:160]}", flush=True)
        return out
    for _i, lab, is_ind in g.fp_labels(TGT):
        if not is_ind or not lab:
            continue
        try:
            v = ref.GetControlValue(lab)
        except Exception as e:
            out.append((lab, "<unreadable>", str(e)[:60], lab in known_before))
            continue
        if isinstance(v, tuple) and len(v) == 0:
            kind = "ARRAY (empty)"
        elif isinstance(v, tuple) and v and isinstance(v[0], tuple):
            kind = f"ARRAY of {len(v)}"
        else:
            kind = "scalar/cluster"
        out.append((lab, repr(v)[:40], kind, lab in known_before))
    return out


def main():
    g._lv = None

    print("== 1-2. build the target and create the auto-indexed OUTPUT tunnel", flush=True)
    body, pidx = build_target()
    print("   ", snap("ready:"), flush=True)
    n_tun = g.count(TGT, "LoopTunnel")
    if n_tun < 2:
        print("STOP: expected 2 tunnels (one in, one out), got", n_tun, flush=True)
        return 1

    before_labels = {lab for _i, lab, ind in g.fp_labels(TGT) if ind}
    print(f"   indicators already present: {sorted(before_labels)}", flush=True)

    results = []
    for tun in range(n_tun):
        print(f"\n== 3-4. tunnel {tun}: set_index_mode(1), then tunnel_indicator()", flush=True)
        try:
            g.set_index_mode(TGT, tun, 1)
            print("   index mode set to 1 (auto-index)", flush=True)
        except Exception as e:
            # An INPUT tunnel is already auto-indexing; a refusal here is informative, not fatal.
            print(f"   set_index_mode: {str(e)[:160]}", flush=True)
        try:
            new = g.tunnel_indicator(TGT, tun)
            print(f"   OP RETURNED: {[(o['uid'], o['pos']) for o in new]}", flush=True)
            print("   ", snap("after:"), flush=True)
            results.append((tun, "created+wired"))
        except Exception as e:
            print(f"   FAILED: {str(e)[:220]}", flush=True)
            print("   ", snap("after:"), flush=True)
            results.append((tun, f"failed: {str(e)[:80]}"))

    print("\n== 5. THE ACTUAL TEST - datatype of every indicator, read over COM", flush=True)
    print("   (label, value, verdict, existed_before)", flush=True)
    arrays_new = []
    for row in read_indicator_values(before_labels):
        print("   ", row, flush=True)
        if not row[3] and "ARRAY" in str(row[2]):
            arrays_new.append(row[0])

    print("\n################ VERDICT ################", flush=True)
    print("per-tunnel:", results, flush=True)
    if arrays_new:
        print(f"PASS - OpTunnelInd_v0 produced a NEW ARRAY indicator: {arrays_new}", flush=True)
        print("This is the piece OpReportAll_v0 was missing. FUNCTIONAL, not merely structural.", flush=True)
        rc = 0
    else:
        print("FAIL - no new ARRAY indicator. Either the op did not wire, or the tunnel was not", flush=True)
        print("auto-indexing so the indicator came out scalar. Nothing downstream should be built on this yet.",
              flush=True)
        rc = 2

    print("\n" + snap("final:"), flush=True)
    try:
        g.close_panel(TGT)
        time.sleep(0.4)
        os.remove(TGT)
        print("scratch target deleted", flush=True)
    except Exception as e:
        print("scratch cleanup:", str(e)[:120], flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
