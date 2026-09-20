"""probe_arrayout2.py - the corrected follow-up to probe_arrayout.py.

WHAT THE FIRST PROBE ESTABLISHED (tools/bench/probe_arrayout2.log, 2026-09-13):

  Q3  `exit_loop(node_class="Property", ["Position"])` WORKS.  LoopTunnel 1->2, Wire +1, ExecState stays 1.
      So erdosmiller's `Get Outputs.vi` enumerates a node's OUTPUT TERMINALS, not only connector-pane names -
      gscript.exit_loop's docstring ("must be terminals on the node's CONNECTOR PANE") is too narrow; it was
      written for SubVI nodes. The AUTO-INDEXED OUTPUT TUNNEL is therefore ONE CALL, and STATUS.md's
      "blocked: no donor exists" is stale.

  Q2  create_indicator on the Property node inside the loop wires only at terminal 3, and creates the
      indicator INSIDE the body (LoopTunnel unchanged) - a scalar, last-value-wins. Not what is wanted.

  Q1  WAS MALFORMED, and is re-asked here. It swept the ForLoop's Terminals[] for an indicator to hang on the
      OUTPUT tunnel - but ran BEFORE any output tunnel existed, so it could only ever miss. Its six "hits" were
      indicators that appeared with NO new wire, i.e. dangling junk. That is itself worth knowing:
      **create_indicator never fails loudly - it creates SOMETHING either way** - so the acceptance test for a
      real hit must be `ControlTerminal +1 AND Wire +1`, never `ControlTerminal +1` alone.

THIS PROBE asks the question in the right order:

  1. build to end-of-step-7  (For Loop, Property inside, input tunnel, ExecState 1)
  2. exit_loop -> the auto-indexed OUTPUT tunnel now EXISTS
  3. sweep create_indicator over the ForLoop's Terminals[], WIDER (0..13), scoring each by (CtlTerm +1 AND Wire +1)
  4. for any real hit, prove the indicator is an ARRAY - which is the whole point, since an array indicator is
     also the proof that the tunnel auto-indexed.

Step 4 matters because ExecState 1 says nothing about the datatype (CLAUDE.md: "structural is not functional").
The proof used is `OpFPLabels_v0` if it can report the control's type, else the front-panel object count plus the
control's own label - stated as a limitation rather than glossed.

SAFETY: scratch copy, deleted at the end. No original, no live op is touched.
  py tools/bgrun.py --max-min 20 --log tools/bench/probe_arrayout3.log -- py -u tools/recipes/probe_arrayout2.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
PROBE = os.path.join(g.CLAUDEDEV, "PROBE_arrayout2.vi")
POSITION_ID = "632A800"
g._run.__defaults__ = (6.0, 60.0)

HITS = []


def snap():
    return dict(ForLoop=g.count(PROBE, "ForLoop"), LoopTunnel=g.count(PROBE, "LoopTunnel"),
                Property=g.count(PROBE, "Property"), CtlTerm=g.count(PROBE, "ControlTerminal"),
                Wire=g.count(PROBE, "Wire"), ExecState=g.exec_state(PROBE))


def build_to_step7():
    try:
        g.close_panel(PROBE)
        time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(PROBE):
        try:
            os.remove(PROBE)
        except OSError as e:
            print(f"   (cannot remove scratch: {e})", flush=True)
    shutil.copyfile(SRC, PROBE)
    time.sleep(0.3)
    g.open_panel(PROBE)
    time.sleep(0.8)
    g.delete_object(PROBE, "IndexArray", 0)
    g.remove_bad_wires_scripted(PROBE)
    for _ in range(g.count(PROBE, "Property")):
        g.delete_object(PROBE, "Property", 0)
    g.remove_bad_wires_scripted(PROBE)
    g.for_loop(PROBE, (1400, 900))
    body = [i for i, d in enumerate(g.report(PROBE, "Diagram")) if "For" in str(d.get("owner"))][0]
    g.build_property(PROBE, "VI Server:GObject", [(POSITION_ID, False)], (1450, 950), diagram_index=body)
    pidx = g.count(PROBE, "Property") - 1
    g.wire(PROBE, "SubVI", 0, "References", "Property", pidx, "reference")
    return body, pidx


def main():
    g._lv = None

    print("== 1-2. build to step 7, then exit_loop to create the OUTPUT tunnel", flush=True)
    body, pidx = build_to_step7()
    print("   after step 7:", snap(), flush=True)

    # `exit_loop` checks the tunnel count itself and raises on a silent no-op, so this is self-verifying.
    g.exit_loop(PROBE, pidx, ["Position"], body, node_class="Property")
    base = snap()
    print("   after exit_loop:", base, flush=True)
    if base["LoopTunnel"] < 2:
        print("STOP: no output tunnel - the Q3 result did not reproduce", flush=True)
        return 1

    # Which Nodes[] index is the ForLoop? (creation order, which is what create_indicator addresses by)
    nodes = g.report(PROBE, "Node")
    print("   nodes:", [(n["i"], n["class"], n["pos"]) for n in nodes], flush=True)
    li = next((n["i"] for n in nodes if n["class"] == "ForLoop"), None)
    if li is None:
        print("STOP: no ForLoop in Nodes[]", flush=True)
        return 1

    print(f"\n== 3. sweep create_indicator over ForLoop Nodes[{li}].Terminals[0..13]", flush=True)
    print("   SCORING: a real hit is ControlTerminal +1 AND Wire +1. CtlTerm alone = a dangling indicator,", flush=True)
    print("   which is what every one of probe 1's six 'hits' turned out to be.", flush=True)
    prev = base
    for t in range(0, 14):
        try:
            g.create_indicator(PROBE, li, t)
        except Exception as e:
            print(f"   t={t:2d}  EXC {str(e)[:120]}", flush=True)
            continue
        now = snap()
        d_ctl = now["CtlTerm"] - prev["CtlTerm"]
        d_wire = now["Wire"] - prev["Wire"]
        verdict = "HIT (wired)" if (d_ctl >= 1 and d_wire >= 1) else ("dangling" if d_ctl >= 1 else "nothing")
        print(f"   t={t:2d}  CtlTerm {d_ctl:+d}  Wire {d_wire:+d}  ExecState={now['ExecState']}   -> {verdict}",
              flush=True)
        if verdict == "HIT (wired)":
            HITS.append((t, now))
        prev = now

    print(f"\n== 4. result: {len(HITS)} wired hit(s): {[t for t, _ in HITS]}", flush=True)
    if HITS:
        # THE DATATYPE IS THE WHOLE POINT, and ExecState 1 does not establish it (CLAUDE.md: structural is not
        # functional). `fp_labels` reports label + is_indicator but NOT type, so the type is read FUNCTIONALLY
        # instead: COM `GetControlValue` returns the control's actual value, and for a never-run VI the defaults
        # discriminate cleanly -
        #     Position as a SCALAR cluster of two I32  ->  (0, 0)
        #     Position AUTO-INDEXED into an ARRAY       ->  ()          (an empty array)
        # so an empty tuple is positive evidence of array-ness, and a 2-tuple is positive evidence against it.
        try:
            labels = g.fp_labels(PROBE)
            print("   front-panel objects (index, label, is_indicator):", labels, flush=True)
        except Exception as e:
            labels = []
            print(f"   (fp label read unavailable: {str(e)[:150]})", flush=True)
        try:
            ref = g.lv().GetVIReference(PROBE, "", False, 0)
            for _i, lab, is_ind in labels:
                if not is_ind or not lab:
                    continue
                try:
                    v = ref.GetControlValue(lab)
                except Exception as e:
                    print(f"   {lab!r:34} <unreadable: {str(e)[:60]}>", flush=True)
                    continue
                kind = ("ARRAY (empty)" if isinstance(v, tuple) and len(v) == 0 else
                        "array-of-N" if isinstance(v, tuple) and v and isinstance(v[0], tuple) else
                        "scalar/cluster")
                print(f"   {lab!r:34} value={v!r:24} -> {kind}", flush=True)
        except Exception as e:
            print(f"   (value read unavailable: {str(e)[:150]}) - ARRAY-NESS REMAINS UNPROVEN", flush=True)
    else:
        print("   No wired hit. The output tunnel is not reachable as a ForLoop terminal; the next candidate is", flush=True)
        print("   reading exit_loop's own returned tunnel refs (erdosmiller Exit For Loop emits them).", flush=True)

    print("\n   final:", snap(), flush=True)

    try:
        g.close_panel(PROBE)
        time.sleep(0.4)
        if os.path.exists(PROBE):
            os.remove(PROBE)
            print("scratch PROBE_arrayout2.vi deleted", flush=True)
    except Exception as e:
        print(f"scratch not deleted ({str(e)[:120]}) - remove next session", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
