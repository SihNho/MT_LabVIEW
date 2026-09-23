r"""jev_chain.py - connectivity-map plan STEP 5, layer 1: build a subVI-level chain Y -> ... -> Z one link at a time.

The LLM (or user) states the intent at subVI level ("A's result must reach B"). Python lists the candidates -
every subVI call node on the same diagram scope (the Y node's frame diagram and its descendants, from the
tools/jev_candidates.py diagram tree) - and Jev answers ONE noul per candidate: "is subVI X the next link after Y
toward Z?". Code takes the best p; a best inside jev's unknown band (0.30..0.70) or two candidates >= 0.70 BRANCH
(each branch recorded, none followed further by code) and the record marks the step "llm". Kept small on purpose
(brief 2026-09-23: the first use, M3a-4, has a known chain; the labelled set is what matters).

Ground truth for measurement is computed by `true_next()` from the graph, not by a model: X is the next link after
Y toward Z iff X is a DIRECT subVI successor of Y (a data path from one of Y's outputs to one of X's inputs that
passes through no other subVI call) AND (X is Z, or Z is reachable from X). vigraph's `thru` edges over-approximate
a primitive's input->output flow; that approximation is inherited and named.

PRIOR ART CHECKED (2026-09-23): tools/vigraph.py (reach4/terminals, read-only), docs/frame-loop-wire-graph.md (the
functional units the labelled set is checked against), tools/jev_pairs.py (same record shape and thresholds file).
"""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev  # noqa: E402
import jev_candidates as JC  # noqa: E402
import jev_pairs as JP  # noqa: E402
import vigraph as V  # noqa: E402

CHAIN_Q = {
    "type": "noul",
    "instructions": (
        "A LabVIEW block diagram is read as a chain of subVI calls along the data flow. `from` is the subVI call "
        "where the chain currently stands, `toward` is the subVI call the chain must end at, and `candidate` is "
        "ONE other subVI call on the same diagram scope, each with its call-node uid, file name and its connector-"
        "pane terminals (label and direction) from the project's wiki. Decide whether the candidate is the NEXT "
        "subVI on the data path: it consumes something `from` produces with no other subVI in between, AND it lies "
        "on the way to `toward` (or is `toward` itself)."),
    "criteria": {
        "true": "The candidate directly consumes an output of `from` and leads on to `toward` (or is it).",
        "false": ("The candidate is not directly downstream of `from`, or it is downstream but does not lead to "
                  "`toward`, or it runs in parallel / upstream."),
    },
}


def subvi_nodes_in_scope(G, root_diagram):
    """SubVI call nodes whose terminals sit on `root_diagram` or on any diagram below it in the tree."""
    out = []
    for u, name in G["subvi_name"].items():
        ds = set(int(r.get("frame_diagram") or 0) for r in G["by_node"].get(u, ()))
        if any(root_diagram in JC._ancestors(G["tree"], d) for d in ds if d):
            out.append(u)
    return sorted(out)


def direct_successors(G, y):
    """SubVI nodes reached from y's outputs without passing THROUGH another subVI node."""
    subs = set(G["subvi_name"])
    stack = [k for k in V.terminals(G, node=y, is_source=True)]
    seen, hit = set(stack), set()
    while stack:
        cur = stack.pop()
        for _kind, nxt, _i in G["out"].get(cur, ()):
            node = V.key_parts(nxt)[0]
            if node in subs and node != y:
                hit.add(node)
                continue                        # stop at the first subVI on this path
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return hit


def reaches(G, a, b):
    return b in set(V.key_parts(k)[0] for k in V.reach4(G, [a]))


def true_next(G, y, z, x):
    return x in direct_successors(G, y) and (x == z or reaches(G, x, z))


def subvi_line(G, u):
    name = G["subvi_name"].get(u, "?")
    rec = JP.subvi_record(name)
    pane = ", ".join("{0} ({1})".format(p["label"], p["direction"]) for p in (rec or {}).get("connector_pane", [])[:16])
    return "#{0} {1!r}; pane: {2}{3}".format(u, name, pane or "(not in the wiki)",
                                            ("; summary: " + rec["summary"]) if rec and rec.get("summary") else "")


def ask_link(G, y, z, x, n=None):
    return jev.ask_n({"from": subvi_line(G, y), "toward": subvi_line(G, z), "candidate": subvi_line(G, x)},
                     {"next_link": CHAIN_Q}, n=n, purpose="step5-chain")


def build_chain(G, y, z, root_diagram, max_steps=8, n=None, th=None):
    """Follow Jev one step at a time. Returns {steps:[{at, scored, chosen, action}], reached, jev_calls}."""
    th = th or JP.thresholds()
    cands = subvi_nodes_in_scope(G, root_diagram)
    steps, at, calls, seen = [], y, 0, {y}
    for _ in range(max_steps):
        scored = []
        for x in cands:
            if x in seen:
                continue
            p, spread, err = ask_link(G, at, z, x, n=n)
            calls += (spread or {}).get("n", 0) if spread else jev.samples()
            scored.append({"x": x, "p": p, "err": err})
        ok = sorted([s for s in scored if s["p"] is not None], key=lambda s: -s["p"])
        many = [s for s in ok if s["p"] >= jev.UNKNOWN_HI]
        if not ok or ok[0]["p"] < th["chain"]["act"] or len(many) >= 2 or not th["chain"].get("acts"):
            steps.append({"at": at, "scored": scored, "chosen": None, "action": "llm",
                          "branches": [s["x"] for s in ok if s["p"] > jev.UNKNOWN_LO]})
            return {"steps": steps, "reached": False, "jev_calls": calls}
        x = ok[0]["x"]
        steps.append({"at": at, "scored": scored, "chosen": x, "action": "link", "p": ok[0]["p"]})
        seen.add(x)
        if x == z:
            return {"steps": steps, "reached": True, "jev_calls": calls}
        at = x
    return {"steps": steps, "reached": False, "jev_calls": calls}


def scope_counts(G, root):
    c = collections.Counter(G["subvi_name"][u] for u in subvi_nodes_in_scope(G, root))
    return dict(c)
