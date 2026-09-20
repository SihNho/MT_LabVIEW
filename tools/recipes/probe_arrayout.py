"""probe_arrayout.py - HOW does an AUTO-INDEXED OUTPUT tunnel + ARRAY indicator get built by script?

THE ONE REMAINING GAP in OpReportAll_v0 (tools/recipes/build_opreportall.py). Steps 1-7 are verified: For Loop,
`wire()` across the boundary auto-creates the INPUT tunnel and resolves N, Property nodes are CREATED inside the body
via `build_property(diagram_index=body)`. Only the OUTPUT side is unproven.

WHY STATUS.md's stated blocker is probably stale. It says "no donor exists ... front-panel object creation is the
fleet's weak spot". But `OpCreateIndicator_v0.vi` HAS existed since 2026-09-06 (`gscript.create_indicator`,
Terminal.Create Indicator 6349C02), and Create-Indicator-on-a-terminal lets LABVIEW choose the datatype - which is
exactly what is wanted, since an auto-indexed tunnel's type is an array of the wire's type. No free-standing
front-panel object ever needs to be created. What is genuinely unknown is only ADDRESSABILITY: these ops address
things as Nodes[i].Terminals[j], and a LoopTunnel is not a Node.

So this probe answers three addressability questions, cheapest and highest-value first, and CHANGES NOTHING that
matters: it works on a scratch copy that is deleted at the end (CLAUDE.md rule "create and delete scratch targets"),
and it never touches an original or a live op. Per CLAUDE.md every step states a PREDICTION so a failure is
machine-checkable rather than a matter of opinion.

  Q3  does `exit_loop()` work on a PROPERTY node?      <- if yes, step 8 is ONE call and already auto-indexed
  Q1  are a ForLoop's TUNNELS reachable as its Terminals[]?   <- if yes, create_indicator straight off the tunnel
  Q2  what does create_indicator on a node INSIDE a loop produce - which diagram, which datatype?

Each is independent: a failure of one does not invalidate the others, so all three run regardless.

  py tools/bgrun.py --max-min 20 --log tools/bench/probe_arrayout.log -- py -u tools/recipes/probe_arrayout.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
PROBE = os.path.join(g.CLAUDEDEV, "PROBE_arrayout.vi")
POSITION_ID = "632A800"          # GObject.Position, verified 2026-09-06
g._run.__defaults__ = (6.0, 60.0)

RESULTS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   OBSERVED: {obs}", flush=True)
        RESULTS.append((name, "ok", str(obs)[:300]))
        return obs
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        RESULTS.append((name, "exc", str(e)[:300]))
        return None


def snap(tag=""):
    return (f"{tag} ForLoop={g.count(PROBE,'ForLoop')} LoopTunnel={g.count(PROBE,'LoopTunnel')} "
            f"Property={g.count(PROBE,'Property')} CtlTerm={g.count(PROBE,'ControlTerminal')} "
            f"Wire={g.count(PROBE,'Wire')} ExecState={g.exec_state(PROBE)}")


def fresh():
    """Rebuild the probe target up to the END OF STEP 7 - the exact state OpReportAll_v0 is stuck at.

    Reused before every question so the three answers are independent: a question that wedges the target cannot
    contaminate the next one.
    """
    try:
        g.close_panel(PROBE)       # LabVIEW holds the file open; the delete below fails otherwise
        time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(PROBE):
        try:
            os.remove(PROBE)
        except OSError as e:
            print(f"   (could not remove probe file: {e}) - continuing on the existing copy", flush=True)
    shutil.copyfile(SRC, PROBE)
    time.sleep(0.3)
    g.open_panel(PROBE)            # a target loaded only via GetVIReference declines edits SILENTLY
    time.sleep(0.8)
    g.delete_object(PROBE, "IndexArray", 0)
    g.remove_bad_wires_scripted(PROBE)
    for _ in range(g.count(PROBE, "Property")):
        g.delete_object(PROBE, "Property", 0)
    g.remove_bad_wires_scripted(PROBE)
    g.for_loop(PROBE, (1400, 900))
    body = [i for i, d in enumerate(g.report(PROBE, "Diagram")) if "For" in str(d.get("owner"))]
    if not body:
        raise RuntimeError("no loop body diagram")
    body = body[0]
    g.build_property(PROBE, "VI Server:GObject", [(POSITION_ID, False)], (1450, 950), diagram_index=body)
    pidx = g.count(PROBE, "Property") - 1
    g.wire(PROBE, "SubVI", 0, "References", "Property", pidx, "reference")
    return body, pidx


def loop_node_index():
    """Index of the ForLoop within Nodes[] (CREATION order, which is what the ops address by)."""
    nodes = g.report(PROBE, "Node")
    for i, n in enumerate(nodes):
        if "For" in str(n.get("class", "")) or "For" in str(n.get("ClassName", "")):
            return i, n
    return None, nodes


def main():
    g._lv = None
    report_path = os.path.join(os.path.dirname(HERE), "bench", "probe_arrayout_results.txt")

    # ---------------- Q3: does exit_loop work on a Property node? ----------------
    # exit_loop drives erdosmiller `Exit For Loop.vi`, which internally uses `Get Outputs.vi`. Its docstring says
    # the names must be CONNECTOR-PANE terminals, which a Property node has none of - but `Get Outputs` may simply
    # enumerate a node's output terminals, in which case "Position" is a legal name and this is the whole answer.
    # exit_loop CHECKS the tunnel count itself and raises on a silent no-op, so a wrong guess is loud, not silent.
    print("\n############ Q3: exit_loop on a Property node ############", flush=True)
    body, pidx = step("Q3 setup: rebuild to end-of-step-7",
                      "ForLoop=1 LoopTunnel=1 Property=1 ExecState=1 (input tunnel supplies N)",
                      lambda: (fresh(), print("   ", snap("state:"), flush=True))[0]) or (None, None)
    if body is not None:
        step("Q3 exit_loop(Property, ['Position'])",
             "IF Get Outputs enumerates node terminals: LoopTunnel 1->2, auto-indexed, ExecState stays 1. "
             "IF it needs a connector pane: RuntimeError 'expected 1 new tunnels, got 0'",
             lambda: (g.exit_loop(PROBE, pidx, ["Position"], body, node_class="Property"), snap("after"))[1])

    # ---------------- Q1: are a ForLoop's tunnels reachable as Terminals[]? ----------------
    # create_indicator addresses Nodes[node_index].Terminals[terminal_index]. A ForLoop IS a Node. If LabVIEW
    # exposes its tunnels in Terminals[], Create Indicator on the OUTPUT tunnel yields the ARRAY indicator directly
    # and nothing else is needed. Sweeping a few indices is cheap (~0.15 s each) and the op is a no-op on a wired
    # or out-of-range terminal, so a miss costs nothing.
    print("\n############ Q1: ForLoop.Terminals[] ############", flush=True)
    body, pidx = step("Q1 setup: rebuild to end-of-step-7", "same state as Q3 setup",
                      lambda: (fresh(), print("   ", snap("state:"), flush=True))[0]) or (None, None)
    if body is not None:
        li, node = step("Q1 find the ForLoop in Nodes[]", "one node whose class contains 'For'",
                        loop_node_index) or (None, None)
        if li is not None:
            for t in range(0, 6):
                step(f"Q1 create_indicator(ForLoop node {li}, terminal {t})",
                     "a new ControlTerminal means tunnels ARE addressable; none means they are not",
                     lambda t=t, li=li: (g.create_indicator(PROBE, li, t), snap(f"t={t}"))[1])

    # ---------------- Q2: create_indicator on a node INSIDE the loop ----------------
    # The fallback path. Two things must be learned, not assumed: WHICH DIAGRAM the new indicator terminal lands on
    # (inside the loop = scalar, last value wins; outside = the tunnel was made for us), and WHAT DATATYPE it got.
    # If it lands inside, the follow-up question is whether move_out() to the top-level diagram converts the
    # connection into an auto-indexed tunnel or merely breaks the wire (its docstring warns of the latter).
    print("\n############ Q2: create_indicator on the Property node inside the loop ############", flush=True)
    body, pidx = step("Q2 setup: rebuild to end-of-step-7", "same state as Q3 setup",
                      lambda: (fresh(), print("   ", snap("state:"), flush=True))[0]) or (None, None)
    if body is not None:
        nodes = g.report(PROBE, "Node")
        pn = [i for i, n in enumerate(nodes) if "Propert" in str(n.get("class", "")) + str(n.get("ClassName", ""))]
        print(f"   Property node indices within Nodes[]: {pn}", flush=True)
        target_node = pn[-1] if pn else pidx
        for t in range(0, 4):
            step(f"Q2 create_indicator(Property node {target_node}, terminal {t})",
                 "ControlTerminal +1 on SOME diagram; the interesting part is WHICH diagram and what type",
                 lambda t=t, tn=target_node: (g.create_indicator(PROBE, tn, t), snap(f"t={t}"))[1])
        # `report()` returns only class/uid/pos/owner (owner is a CLASS NAME, not a diagram index), so
        # "which diagram" is read from the LoopTunnel count instead: an indicator created OUTSIDE the loop forces a
        # tunnel (LoopTunnel +1); one created INSIDE does not. snap() carries that count on every line above.
        step("Q2 inventory of every ControlTerminal (class/uid/pos/owner)",
             "position is meaningful on THIS VI - we built it; only the MAIN VI was Cleaned Up",
             lambda: [(c["uid"], c["class"], c["pos"], c["owner"]) for c in g.report(PROBE, "ControlTerminal")])
        step("Q2 node inventory, to read those positions against the loop's extent",
             "the ForLoop's own position, so inside-vs-outside can be judged",
             lambda: [(n["i"], n["class"], n["pos"]) for n in g.report(PROBE, "Node")])

    # ---------------- summary ----------------
    print("\n################ SUMMARY ################", flush=True)
    lines = []
    for name, kind, obs in RESULTS:
        line = f"[{kind}] {name}\n      {obs}"
        print(line, flush=True)
        lines.append(line)
    try:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print(f"\nwritten: {report_path}", flush=True)
    except OSError as e:
        print(f"could not write results file: {e}", flush=True)

    # scratch targets are created and deleted in the same operation (CLAUDE.md rule 4)
    try:
        if os.path.exists(PROBE):
            os.remove(PROBE)
            print("scratch PROBE_arrayout.vi deleted", flush=True)
    except OSError as e:
        print(f"scratch file still open in LabVIEW, delete next session: {e}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
