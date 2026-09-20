r"""probe_relocate_route.py - step 0a of the delivery cycle: can work be moved from one loop to another
INSIDE ONE VI, using only operations the fleet has already proven?

WHY THIS RUNS FIRST. The whole in-copy restructuring method rests on an operation nobody has performed:
taking work that lives in the main VI's frame loop and making it live in a different loop instead. The plan
review (archive/peer/2026-09-15-cycle8-plan-attack.md) was blunt: every step so far has been READ-ONLY, and
"spending several cycles cataloguing 170 diagrams before testing the indispensable mutation primitive is
backwards". So this is tested before the catalogue, on scrap.

WHAT IT DOES NOT TEST, deliberately. `GObject.Move` with an `owner` input - relocating an existing node into
another diagram - is NOT used. docs/toolkit-capabilities.md already recorded that "move a node" was never
needed: a node can be BUILT directly inside a loop's diagram, and wiring across the border creates the tunnel.
This probe therefore tests the route we would actually take: CREATE the destination loop, DROP the same subVI
into it, WIRE across the border, DELETE the original. If that works, relocation is unnecessary and the
method stands on primitives with a track record.

PREDICTION CONTRACT (stated before the run; a miss is a failed prediction and triggers a peer review):
  G1 a copy of HARNESS_copyloop opens and reports a starting census; ExecState is whatever it is - recorded
  G2 a NEW While loop is created on the top-level diagram        -> WhileLoop count +1, a new Diagram appears
  G3 StrToPath.vi is dropped INSIDE that new loop's diagram      -> SubVI count +1, and it sits on the new diagram
  G4 the loop is created WITH an input tunnel from the `File Path` control -> LoopTunnel +1
  G5 the ORIGINAL copy of that subVI elsewhere is deleted        -> SubVI count back to the starting value
  G6 deleting the scratch loop again restores the VI             -> ExecState back to 1
Failure of G2/G3/G4 kills the in-copy method as specified and forces a rethink; failure of G5 only means
deletion needs a different call.

RUN 1 (17:55, 5 pass / 2 fail) failed on two gates, BOTH of them defects in this probe rather than in the toolkit,
and both are repaired above:
  * G4 wired after the fact with a guessed source spec (`Terminal`[0], empty terminal name) and got error 1057
    "To More Specific Class". The PROVEN route on this very harness is `while_loop(tunnels=[...])`, which creates
    the loop with the tunnel already made from a named front-panel control (INDEX row 32 used `File Path`, on
    HARNESS_copyloop).
  * G6 asserted `ExecState == 1` while `gscript.while_loop`'s own docstring states the opposite: a new While loop's
    conditional terminal is UNWIRED, so the VI is legitimately broken until a stop is wired. Predicting against a
    documented fact is the `inference-over-measurement` habit the cycle-8 retrospective had just named. The gate now
    asks the question that actually matters - are our edits REVERSIBLE - by deleting the loop and checking recovery.

READ-ONLY WITH RESPECT TO EVERY ORIGINAL. Only a scratch copy under claudeDev is touched, it is created at the
start and deleted at the end, and no original and no hardware is involved.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_relocate_route.log -- py -u tools/recipes/probe_relocate_route.py
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
SCRATCH = os.path.join(CLAUDEDEV, "SCRATCH_relocate_0a.vi")

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)


def census(tag):
    c = {k: g.count(SCRATCH, k) for k in ("WhileLoop", "SubVI", "Wire", "LoopTunnel", "Diagram")}
    try:
        c["ExecState"] = g.exec_state(SCRATCH)
    except Exception as e:
        c["ExecState"] = f"err {e}"
    print(f"  census {tag}: {c}", flush=True)
    return c


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    for p in (DONOR, DROPPEE):
        if not os.path.exists(p):
            print(f"STOP: missing {p}", flush=True)
            return 3
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(DONOR, SCRATCH)
    print(f"scratch = {SCRATCH}", flush=True)

    try:
        t0 = time.time()
        start = census("start")
        gate("G1 scratch opens and reports a census", start["Diagram"] >= 1, str(start["Diagram"]))

        # G2 + G4 - the destination loop, created WITH its border tunnel (the proven route, INDEX row 32)
        loop_uid = g.while_loop(SCRATCH, (40, 400), tunnels=["File Path"])
        after_loop = census("after while_loop")
        gate("G2 a new While loop exists", after_loop["WhileLoop"] == start["WhileLoop"] + 1,
             f"{start['WhileLoop']} -> {after_loop['WhileLoop']}, uid {loop_uid}")
        gate("G2b a new Diagram appeared", after_loop["Diagram"] == start["Diagram"] + 1,
             f"{start['Diagram']} -> {after_loop['Diagram']}")
        gate("G4 a border tunnel was created from the named control",
             after_loop["LoopTunnel"] > start["LoopTunnel"],
             f"{start['LoopTunnel']} -> {after_loop['LoopTunnel']}")

        # G3 - the same subVI, built INSIDE the new loop rather than moved into it.
        # The new loop's body is the newest Diagram; Traverse order is per-op, so address it by index = last.
        body_index = after_loop["Diagram"] - 1
        g.drop_subvi(SCRATCH, DROPPEE, body_index, (60, 40))
        after_drop = census("after drop_subvi")
        gate("G3 the subVI was dropped", after_drop["SubVI"] == after_loop["SubVI"] + 1,
             f"{after_loop['SubVI']} -> {after_drop['SubVI']} on diagram index {body_index}")

        # G5 - remove the ORIGINAL work. Deleting the subVI we just dropped would prove nothing, so delete
        # index 0, i.e. whatever the donor already had.
        deleted = False
        try:
            g.delete_object(SCRATCH, "SubVI", 0, verify=False)
            deleted = True
        except Exception as e:
            print(f"  delete_object raised: {e}", flush=True)
        after_del = census("after delete")
        gate("G5 an existing subVI was deleted", after_del["SubVI"] == after_drop["SubVI"] - 1,
             f"{after_drop['SubVI']} -> {after_del['SubVI']} (call ok={deleted})")

        # G6 - REVERSIBILITY, not "is it runnable". A scripted While loop's conditional terminal is unwired by
        # design, so ExecState 0 here is expected and says nothing. What matters is whether our edits can be
        # undone: delete the loop we added and the VI should recover.
        try:
            g.delete_object(SCRATCH, "WhileLoop", 0, verify=False)
        except Exception as e:
            print(f"  delete_object(WhileLoop) raised: {e}", flush=True)
        try:
            g.remove_bad_wires_scripted(SCRATCH)
        except Exception as e:
            print(f"  remove_bad_wires_scripted raised: {e}", flush=True)
        final = census("final")
        gate("G6 deleting the scratch loop restores the VI", final["ExecState"] == 1, str(final["ExecState"]))
        print(f"\nelapsed {time.time() - t0:.1f}s", flush=True)
    finally:
        try:
            g._lv = None
        except Exception:
            pass
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("scratch deleted", flush=True)
            except Exception as e:
                print(f"scratch NOT deleted: {e}", flush=True)

    print(f"\n=== 0a RESULT: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
