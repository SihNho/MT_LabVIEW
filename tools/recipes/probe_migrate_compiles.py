r"""probe_migrate_compiles.py - step 0a, attempt 3, and a DIFFERENT test from the two void ones.

WHY THE FIRST TWO RUNS PROVED NOTHING (measured, not guessed - docs/NAMES.md):
  * a newly created Diagram lands at Traverse index **0**, not at the end. The old probe used
    `count("Diagram") - 1`, so `drop_subvi` put the subVI on a pre-existing diagram, silently. The gate then
    passed on a WHOLE-VI SubVI count that never looked at where the object landed.
  * run 2 reused the same scratch path, so LabVIEW served run 1's cached in-memory VI as the "fresh" baseline.
  * `while_loop()` returns elapsed SECONDS, not a UID.
The plan reviewer (archive/peer/2026-09-15-probe0a-run1-two-gate-fails.md) called all three before the measurement
and specified the test below: identify by UID, verify arrival by listing the diagram, wire the real border
connection into a NAMED terminal, wire the conditional, and require ExecState == 1 BEFORE any cleanup - because
"does the migrated configuration compile" is the question, and reversibility is a separate, weaker one.

PREDICTION CONTRACT:
  H1 panel controls enumerate, and a Boolean control exists to drive the conditional terminal
  H2 while_loop(tunnels=["File Path"]) adds exactly one WhileLoop uid and one Diagram uid
  H3 the new body's Traverse index is 0            <- the measured claim, re-checked here
  H4 StrToPath.vi appears in the subVI listing OF THAT BODY (not in a whole-VI count)
  H5 some route connects the border tunnel to StrToPath's `string` terminal; the probe tries the candidates and
     reports which one worked, and the gate is on the RESULT - `string` ends up on a wire - not on the call
  H6 after exit_while wires the conditional, ExecState == 1  <- the real question
A miss on H5 or H6 means the in-copy migration route is not yet usable and the finding goes to the user, not to
another repair-and-rerun.

Scratch only: a UNIQUE copy under claudeDev per run, deleted at the end. No original is opened; no hardware.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_migrate_compiles.log -- py -u tools/recipes/probe_migrate_compiles.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DONOR = os.path.join(CLAUDEDEV, "HARNESS_copyloop.vi")
DROPPEE = os.path.join(CLAUDEDEV, "StrToPath.vi")
SCRATCH = os.path.join(CLAUDEDEV, f"SCRATCH_migrate_{int(time.time())}.vi")
SINK_TERM = "string"          # measured: StrToPath's connector terminals are `string` (in) and `path` (out)

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)


def body_wires(body_index):
    """The body diagram's net map, so terminal connectivity is READ rather than assumed."""
    try:
        return g.net_map(SCRATCH, diagram_index=body_index, max_nodes=60, max_terms=30)
    except Exception as e:
        print(f"  net_map(body) raised: {e}", flush=True)
        return ({}, {})


def sink_is_wired(body_index):
    nodes, _ = body_wires(body_index)
    for _, (uid, _lbl, terms) in nodes.items():
        for _i, nm, w in terms:
            if nm == SINK_TERM and w:
                return True, f"uid {uid}.{nm} on wire {w}"
    return False, "no node on the body carries a wired `string` terminal"


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    shutil.copy2(DONOR, SCRATCH)
    print(f"scratch = {os.path.basename(SCRATCH)}", flush=True)
    try:
        print(f"  start ExecState = {g.exec_state(SCRATCH)}", flush=True)

        # H1 - what controls exist? The conditional terminal needs a Boolean by LABEL.
        bools = []
        try:
            pw = g.panel_wiring(SCRATCH)
            print(f"  panel_wiring -> {str(pw)[:900]}", flush=True)
            for item in (pw if isinstance(pw, list) else pw.get("controls", [])):
                s = str(item)
                if "Bool" in s:
                    bools.append(item)
        except Exception as e:
            print(f"  panel_wiring raised: {e}", flush=True)
        gate("H1 a Boolean control is available for the conditional terminal", bool(bools), str(bools)[:200])

        # H2/H3 - create the destination loop and identify its body BY UID
        wl_before, dg_before = set(g.uids(SCRATCH, "WhileLoop")), list(g.uids(SCRATCH, "Diagram"))
        g.while_loop(SCRATCH, (40, 400), tunnels=["File Path"])
        wl_after, dg_after = set(g.uids(SCRATCH, "WhileLoop")), list(g.uids(SCRATCH, "Diagram"))
        new_wl = sorted(wl_after - wl_before)
        new_dg = [u for u in dg_after if u not in dg_before]
        gate("H2 exactly one WhileLoop and one Diagram were added",
             len(new_wl) == 1 and len(new_dg) == 1, f"loop {new_wl}, diagram {new_dg}")
        if len(new_dg) != 1:
            raise RuntimeError("cannot identify the new body; stopping before it addresses the wrong diagram")
        body_index = dg_after.index(new_dg[0])
        gate("H3 the new body's Traverse index is 0", body_index == 0,
             f"index {body_index} of {len(dg_after)} (uid {new_dg[0]})")

        # H4 - drop, then VERIFY ARRIVAL on that diagram
        g.drop_subvi(SCRATCH, DROPPEE, body_index, (60, 40))
        landed, listing = False, ""
        try:
            sv = g.subvis(SCRATCH, body_index)
            listing = str(sv)[:400]
            landed = "StrToPath" in listing
        except Exception as e:
            listing = f"subvis() raised: {e}"
        gate("H4 StrToPath.vi is ON THE NEW BODY (listed, not counted)", landed, listing)

        # H5 - the border connection into a NAMED terminal. Try the candidate routes; gate on the result.
        wired, how = sink_is_wired(body_index)
        if not wired:
            for label, fn in (
                ("wire(LoopTunnel->string)",
                 lambda: g.wire(SCRATCH, "LoopTunnel", 0, "", "SubVI", 0, SINK_TERM)),
                ("connect2(body, sink 0, src 0)",
                 lambda: g.connect2(SCRATCH, body_index, 0, SINK_TERM, 1, "")),
            ):
                try:
                    fn()
                    print(f"  route {label}: call returned", flush=True)
                except Exception as e:
                    print(f"  route {label}: {e}", flush=True)
                wired, how = sink_is_wired(body_index)
                if wired:
                    how = f"{how}   via {label}"
                    break
        gate("H5 StrToPath's `string` terminal ends up on a wire", wired, how)

        # H6 - THE QUESTION: does the migrated configuration compile?
        if bools:
            lbl = bools[0] if isinstance(bools[0], str) else str(bools[0])
            try:
                g.exit_while(SCRATCH, lbl, body_index)
                print(f"  exit_while({lbl!r}) returned", flush=True)
            except Exception as e:
                print(f"  exit_while({lbl!r}) raised: {e}", flush=True)
        final = g.exec_state(SCRATCH)
        gate("H6 the migrated state COMPILES (ExecState == 1, before any cleanup)", final == 1, str(final))
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("scratch deleted", flush=True)
            except Exception as e:
                print(f"scratch NOT deleted: {e}", flush=True)

    print(f"\n=== 0a attempt 3: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
