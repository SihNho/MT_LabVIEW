"""build_opconstvalue.py - OpConstValue_v0.vi: READ the VALUE of a diagram constant by script.

WHY THIS OP EXISTS. Three separate questions are currently blocked on the same missing capability - nothing in the op
fleet can read a constant's value, so every number that is wired as a diagram constant in the main VI is invisible:

  1. `ASI_adjust focus-subvi.vi` holds a fixed `Wait (ms)` inside a case frame (docs/motion-path-audit.md §1), and that
     VI is called on EVERY iteration of the frame loop (uid 48, directly on diagram 43's body). A fixed wait inside the
     frame loop is a hard cap on frame rate, and its constant has never been read.
  2. `IMAQdx Configure Grab`'s `Number of Buffers` is the main VI's ring depth, listed as unknown in
     docs/camera-acquisition-facts.md. NI's own example defaults to 10; what this rig asks for is unknown.
  3. The camera geometry constants behind the user's "first run halves the image" report.

API, from a peer search on 2026-09-12 (archive/peer/2026-09-12-read-constant-value-scripting.md), NOT yet confirmed on
this machine - that confirmation is what step 5 is for:
  Constant.Value = property ID **634AC00**, readable, returns an **LV Variant**.
  Class hierarchy: DigitalNumericConstant (16390) -> NumericConstant (16389) -> Constant (16386).
  Traverse returns statically generic refs, so a `To More Specific Class` downcast to `Constant` is required before the
  property node will accept the reference.

DESIGN CHOICE worth stating, because it removes the hardest part: the variant is NOT decoded inside LabVIEW. Wiring it
straight to a **Variant indicator** lets ActiveX marshal it to a COM VARIANT, which Python reads as a plain number or
string through GetControlValue. That avoids needing `Variant To Data` (which would need a type constant per datatype)
or `Variant To Flattened String` - i.e. it avoids placing any primitive that might not be in New VI Object's style
ring, which is the failure mode that has cost whole sessions before (skill: error 1054).

DONOR: OpReport_v3.vi, which already is `vi path -> Open VI Reference -> Traverse for GObjects(Class Name) -> refs[] ->
Index Array[index] -> read class/uid/pos/owner`. Everything up to and including the Index Array is reused untouched;
only the tail changes.

PREDICTION CONTRACT (each step states what must be observed; a miss stops the batch under the RECOVERY_LOCKED rule):
  1. copy OpReport_v3 -> OpConstValue_v0                       predict: file exists, ExecState 1, Property count == donor's
  2. locate the Index Array and its `element` terminal          predict: exactly 1 IndexArray node
  3. place `To More Specific Class`, wire IA.element -> its input, and a String constant "Constant" -> its class input
                                                               predict: +1 node, ExecState may be 0 until step 4 wires on
  4. PN = Property(class "Constant", ["Value"] id 634AC00) <- the downcast output; Value -> new Variant indicator
                                                               predict: +1 Property, ExecState 1
  5. CONFIRM ON THE MACHINE, which is the whole point: build a scratch VI holding known constants (an I32 = 12345, a
     DBL = 3.25, a String = "hello"), run OpConstValue_v0 over it, and require the values to come back EXACTLY.
     A peer's API answer is a hypothesis; this step is what turns it into a fact.  predict: 3/3 exact matches

DONOR FOR THE DOWNCAST - **UNRESOLVED, and the first thing to settle before running this.** A `To More Specific Class`
is a primitive, and primitives outside New VI Object's style ring must be COPIED from a VI that already has one
(skill: error 1054). An offline byte scan of claudeDev found the STRING "To More Specific Class" in four files:

    DONOR_Ex3_PrimitiveFunctions.vi
    DONOR_Ex1_GetControlsWireIndicators.vi
    Ex6_WhileLoops_COPY.vi
    ScriptDriver_DropForLoop.vi

**but reading their diagrams did not find the node.** DONOR_Ex3's two diagrams hold 12 + 4 nodes and none has the
signature of a downcast; the one that looked promising - terminals `['error out', 'error in (no error)', 'reference']` -
is `Close Reference`, which has exactly those three. So the byte hit is a string in a type descriptor or menu table, not
a node. This is the same error a peer review caught earlier the same day in the camera work: **a string in the file is
a hint, never proof of a structure**, exactly as the skill warns ("compiled machine code in the same streams produces
convincing ASCII noise"). Do not repeat it.

Before this recipe can run, ONE of these must be established:
  (a) find a VI that demonstrably contains the node (search by terminal signature, not by string), or
  (b) check whether `New VI Object`'s style ring carries `To More Specific Class` after all - it was never tested, and
      the verified-impossible list only covers primitives actually tried, or
  (c) find out whether the downcast is needed at all: erdosmiller's Traverse returns GObject refs and LabVIEW allows
      upcast but not downcast, so a `Constant` property node should reject a GObject wire - but that is reasoning, not
      a measurement, and the cheapest test is to build the property node and look at the wire.

`g.copy_into(donor, label, target)` needs the node to carry a LABEL; `prepare=` can call `g.set_node_label` on the
substituted copy first, and it takes a diagram index, so a node on a nested diagram is reachable.

STATUS: NOT YET RUN - this file is the plan, written while LabVIEW was busy with the camera diagram scan. It is listed
here so the next session can execute it as one batch rather than re-deriving it.

  py tools/bgrun.py --max-min 25 --log tools/bench/build_opconstvalue.log -- py -u tools/recipes/build_opconstvalue.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConstValue_v0.vi")
SCRATCH = os.path.join(g.CLAUDEDEV, "CONSTTEST_v0.vi")
CONST_VALUE_ID = "634AC00"                 # Constant.Value - peer-sourced, confirmed by step 5 and nowhere else
g._run.__defaults__ = (6.0, 45.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   observed: {obs}", flush=True)
        STEPS.append((name, True))
        return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True)
        STEPS.append((name, False))
        return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def main():
    g._lv = None
    # NEVER touch the target through VI Server before overwriting it: GetVIReference LOADS the VI, and a copyfile under
    # a loaded VI produces the modal "changed on disk ... resulting in a corrupt VI", which blocks every COM call until
    # LabVIEW is killed (measured 2026-09-10, cost one full watchdog period).
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)                      # a target loaded only through GetVIReference declines every edit SILENTLY
    time.sleep(0.8)

    print("donor counts:", {c: g.count(OP, c) for c in ("Property", "IndexArray", "SubVI", "Node")}, flush=True)
    print("\nNOT IMPLEMENTED BEYOND THIS POINT - see the module docstring. The remaining steps are 3, 4 and 5 of the\n"
          "prediction contract, and they need the `To More Specific Class` donor node identified first: it is a\n"
          "primitive, so it is placed by copy_into() from a VI that already has one, never by New VI Object (error\n"
          "1054 - the style ring does not carry it).", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
