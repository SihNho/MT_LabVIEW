"""build_opreportall_v1.py - OpReportAll_v0.vi: report EVERY object of a class in ONE run, as ARRAYS.

THE PROBLEM, measured 2026-09-13:

    one op run against a SMALL target VI      10.4 ms
    one op run against the MAIN VI           960.8 ms      <- 92x, and it scales with TARGET size
    SetControlValue / GetControlValue          0.07 ms     <- COM is irrelevant

~990 ms of every run is FIXED - the `Open VI Reference` on a 473 KB VI with 98 subVI call sites. `report()` calls
the op ONCE PER OBJECT, so a 626-node sweep pays it 626 times: 601 s predicted, 618 s measured. Returning arrays
pays it ONCE: ~601 s -> ~1 s. The restructuring reads far more diagram than that, so this pays for itself
immediately - which is why the work order puts tooling first.

DONOR: OpReport_v3.vi - Open VI Reference -> Traverse (which ALREADY emits the whole `References` array and
`# of Refs`) -> Index Array (throws all but one away) -> Property(Position/UID/Class Name/Owner) ->
Property(Class Name of the owner). The array is already there; the donor just discards it. So: delete the Index
Array, put the property reads inside a For Loop fed by `References`, and auto-index the results out.

EVERY STEP USES AN OPERATION VERIFIED TODAY. The two that were unknown this morning:

  * `exit_loop(node_class="Property", [...])` creates the AUTO-INDEXED OUTPUT TUNNEL. Its docstring claimed the
    names must be on the node's CONNECTOR PANE; erdosmiller's `Get Outputs.vi` in fact enumerates a node's output
    terminals, so it works on a Property node. Verified: LoopTunnel 1->2, Wire +1, ExecState stays 1.
  * `tunnel_indicator(target, tunnel)` (OpTunnelInd_v0, built today) puts a correctly-typed indicator on that
    tunnel. Verified FUNCTIONALLY: the new indicator reads `()` over COM - an empty ARRAY, not `(0, 0)`.
    `create_indicator` cannot do this: a Tunnel is a GObject, not a Terminal, so it inherits no Terminal methods.

BUILD ORDER - tunnels before nodes. Nodes-first leaves the VI broken across more steps, which is what made an
earlier probe misdiagnose itself.

PROPERTY IDS, all from docs/vi-server-ids.json - none guessed:
    GObject.Position 632A800 · GObject.UID 632A813 · Generic.Class Name 6327803 · Generic.Owner 6327806
A GObject-class property node can expose all four, because GObject inherits Generic.

LABELS. LabVIEW names the new indicators itself ("Array", "Array 2", ...). Rather than build yet another op to
rename front-panel controls, the labels are DISCOVERED by diffing `fp_labels()` across each creation and written
out at the end, so `report_all()` can address them by name. Creation order is fixed by this script, so the map is
deterministic - but it is recorded from the machine, not assumed.

SAFETY: builds a NEW file. OpReport_v3.vi is never modified - if this fails, the working traversal is untouched.
Saves only when ExecState == 1.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opreportall_v1.log -- py -u tools/recipes/build_opreportall_v1.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
OP = os.path.join(g.CLAUDEDEV, "OpReportAll_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opreportall_labels.json")

P_POSITION = "632A800"      # GObject.Position
P_UID = "632A813"           # GObject.UID
P_CLASSNAME = "6327803"     # Generic.Class Name
P_OWNER = "6327806"         # Generic.Owner

# Output TERMINAL names are the property's SHORT name (docs/NAMES.md), and the short name is not always the
# property name with spaces. Read off the machine by net_map after run 1 failed step 9 with error 5001:
# `Position`, `UID` and `Owner` were right; **`Generic.Class Name` is spelled `ClassName` on the terminal** -
# no space. Note the contrast one diagram up: `Traverse for GObjects.vi` really does have a `Class Name` INPUT
# with a space, so the two spellings coexist in the same VI and neither can be inferred from the other.
T_POSITION, T_UID, T_CLASSNAME, T_OWNER = "Position", "UID", "ClassName", "Owner"

g._run.__defaults__ = (6.0, 90.0)
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
            f"Property={g.count(OP,'Property')} CtlTerm={g.count(OP,'ControlTerminal')} "
            f"Wire={g.count(OP,'Wire')} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def dump_names(why):
    print(f"\n-- net_map ({why}) - read the REAL terminal names here instead of guessing --", flush=True)
    for d in (0, 1):
        try:
            print(f"   diagram {d}:", flush=True)
            for row in g.net_map(OP, d, max_nodes=40, max_terms=24):
                print("     ", row, flush=True)
        except Exception as e:
            print(f"     diagram {d} EXC {str(e)[:160]}", flush=True)


def main():
    g._lv = None
    try:
        g.close_panel(OP)
        time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(OP):
        try:
            os.remove(OP)                  # never load the target before overwriting it
        except OSError as e:
            print(f"cannot replace {OP}: {e}", flush=True)
            return 1
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)                       # a target loaded only via GetVIReference declines edits SILENTLY
    time.sleep(1.0)
    print(snap("start:"), flush=True)

    # ORDER MATTERS. `Traverse.References` is ALREADY wired to the old Index Array, so wiring it into a loop would
    # need branch=True - or, far better, delete the consumer FIRST and the source is free.
    step("1 delete the OLD Index Array - frees Traverse.'References'", "IndexArray 1->0",
         lambda: (g.delete_object(OP, "IndexArray", 0), g.remove_bad_wires_scripted(OP), snap("after"))[2])
    step("2 delete the two OLD Property nodes (they read ONE element, not the array)", "Property 2->0",
         lambda: ([g.delete_object(OP, "Property", 0) for _ in range(g.count(OP, "Property"))],
                  g.remove_bad_wires_scripted(OP), snap("after"))[2])

    step("3 empty For Loop", "ForLoop 0->1; ExecState 0 is EXPECTED - an empty loop has no N",
         lambda: (g.for_loop(OP, (1400, 900)), snap("after"))[1])
    dias = step("4 find the loop body diagram", "one diagram owned by a ForLoop",
                lambda: [i for i, d in enumerate(g.report(OP, "Diagram")) if "For" in str(d.get("owner"))])
    if not dias:
        print("\nSTOP: no loop body diagram. Nothing saved.", flush=True)
        return 2
    body = dias[0]

    pn1 = step("5 Property(Position, UID, Class Name, Owner) INSIDE the loop body",
               "Property 0->1 - GObject inherits Generic, so one node carries all four",
               lambda: g.build_property(OP, "VI Server:GObject",
                                        [(P_POSITION, False), (P_UID, False),
                                         (P_CLASSNAME, False), (P_OWNER, False)],
                                        (1450, 950), diagram_index=body))
    if not pn1:
        print("\nSTOP: no property node. Nothing saved.", flush=True)
        return 3
    pn1_uid = pn1[-1]["uid"]

    def pidx(uid):
        return [o["uid"] for o in g.report(OP, "Property")].index(uid)

    step("6 wire Traverse.'References' -> that node's `reference` (CROSSES the loop boundary)",
         "LoopTunnel 0->1, Wire +2 (outside + inside segments), and ExecState 0->1 because the array supplies N",
         lambda: (g.wire(OP, "SubVI", 0, "References", "Property", pidx(pn1_uid), "reference"), snap("after"))[1])

    pn2 = step("7 Property(Class Name) on the OWNER, also inside the body",
               "Property 1->2 - this is what makes report()'s `owner` field",
               lambda: g.build_property(OP, "VI Server:Generic", [(P_CLASSNAME, False)],
                                        (1450, 1150), diagram_index=body))
    pn2_uid = pn2[-1]["uid"] if pn2 else None
    if pn2_uid is not None:
        step("8 wire PN1.'Owner' -> PN2.`reference` (both inside the body, so NO new tunnel)",
             "Wire +1, LoopTunnel unchanged",
             lambda: (g.wire(OP, "Property", pidx(pn1_uid), T_OWNER,
                             "Property", pidx(pn2_uid), "reference"), snap("after"))[1])

    # ---- the output side: auto-indexed tunnels, then a typed indicator on each ----
    before_tun = g.count(OP, "LoopTunnel")
    step("9 exit_loop: auto-indexed OUTPUT tunnels for Position, UID, Class Name",
         f"LoopTunnel {before_tun}->{before_tun + 3}",
         lambda: (g.exit_loop(OP, pidx(pn1_uid), [T_POSITION, T_UID, T_CLASSNAME], body,
                              node_class="Property"), snap("after"))[1])
    if pn2_uid is not None:
        step("10 exit_loop: the owner's Class Name",
             "LoopTunnel +1",
             lambda: (g.exit_loop(OP, pidx(pn2_uid), [T_CLASSNAME], body, node_class="Property"),
                      snap("after"))[1])

    if any(k == "exc" for _, k in STEPS):
        dump_names("a step missed its prediction - names are the usual cause")

    # Which tunnels are the new OUTPUT ones? Tunnel 0 is the input (created in step 6); the rest were just made.
    n_tun = g.count(OP, "LoopTunnel")
    print(f"\n== 11. tunnels now {n_tun}; indices 1..{n_tun - 1} should be the outputs", flush=True)

    label_map = {}
    meanings = [T_POSITION, T_UID, T_CLASSNAME, "Owner Class Name"]
    for k, tun in enumerate(range(1, n_tun)):
        before_labels = set(inds())
        try:
            g.set_index_mode(OP, tun, 1)
        except Exception as e:
            print(f"   tunnel {tun}: set_index_mode {str(e)[:120]}", flush=True)
        try:
            g.tunnel_indicator(OP, tun)
        except Exception as e:
            print(f"   tunnel {tun}: tunnel_indicator FAILED {str(e)[:180]}", flush=True)
            continue
        new_labels = [l for l in inds() if l not in before_labels]
        meaning = meanings[k] if k < len(meanings) else f"tunnel {tun}"
        print(f"   tunnel {tun} -> indicator {new_labels}  (expected to carry {meaning})", flush=True)
        for l in new_labels:
            label_map[l] = meaning

    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    print("label map (indicator label -> what it carries):", json.dumps(label_map, indent=2), flush=True)

    if es != 1:
        dump_names("BROKEN at the end")
        print("\nVERDICT: BROKEN - NOT SAVING. OpReport_v3 is untouched; the old path still works.", flush=True)
        return 4

    step("12 COM save", "the op is written to disk", lambda: g.save(OP))
    try:
        os.makedirs(os.path.dirname(MAP_OUT), exist_ok=True)
        with open(MAP_OUT, "w", encoding="utf-8") as f:
            json.dump(label_map, f, indent=2)
        print("label map written:", MAP_OUT, flush=True)
    except OSError as e:
        print("could not write the label map:", e, flush=True)

    print("\nVERDICT: OpReportAll_v0 assembled and saved - STRUCTURAL. It has not been CALLED yet.", flush=True)
    print("Next: call it on a real target, compare its arrays with report()'s per-object results, and TIME both.",
          flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
