"""wiregraph_frame_loop.py - functional units of the frame loop (diagram 43) from the WIRE GRAPH, offline.

Positions mean nothing in this VI (Clean Up Diagram); wiring is intact. Inputs (all measured today):
  tools/bench/main_vi_nodeterms.json   every node of every diagram: per terminal (name, Is Source?, wire uid)
  tools/bench/main_vi_subvis.json      subVI identity per uid
  tools/bench/diagram_tree_main.json   structure uids, diagram owners
Graph: edge = wire uid shared by an OUTPUT terminal (Is Source? TRUE) of node A and an INPUT terminal of node B
(fan-out = the same wire uid on several inputs). A wire seen on only one side inside the diagram crosses the loop
boundary (the WhileLoop's own tunnels / shift registers) - listed as boundary edges. Nested structures are single
nodes whose tunnels appear as terminals (both sides). Then:
  1. backward slice from the kernel call #5058 (what feeds it), forward slice (what consumes it)
  2. weakly connected components after CUTTING plumbing wires (error clusters, VISA/session refnums, timers) - the
     cut classes are named in the output so over-cutting is visible; components are also given WITHOUT cuts
  3. labels per component from subVI identities + terminal names
Output: tools/bench/frame_loop_graph.json, docs/frame-loop-wire-graph.md.  No LabVIEW.
  py tools/bench/wiregraph_frame_loop.py [diagram]
"""
import json
import os
import re
import sys
import time
from collections import defaultdict, deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
K = sys.argv[1] if len(sys.argv) > 1 else "43"
NT = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
SV = json.load(open(os.path.join(HERE, "main_vi_subvis.json"), encoding="utf-8"))
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
KERNEL = 5058
CUT_RE = re.compile(r"error|VISA|session|refnum|handle|reference|millisecond|timer|Event Registration", re.I)
STRUCT_CLASS = {u: cls for cls, lst in TREE["structures"].items() for u in lst}
CLASS = {}
for cls in ("Global", "Local", "Property", "Invoke"):
    for u in NT["stats"].get(f"class_{cls}", []):
        CLASS[u] = cls


def node_label(nd):
    u = nd["uid"]
    ident = SV["by_uid"].get(str(u), {}).get("name")
    if ident:
        return f"subVI {ident}"
    if u in STRUCT_CLASS:
        return f"{STRUCT_CLASS[u]} (structure)"
    if u in CLASS:
        names = [t["name"] for t in nd["terms"] if t["name"] and t["name"] not in ("reference", "reference out", "error in (no error)", "error out")]
        return f"{CLASS[u]} [{', '.join(names[:4])}]"
    names = [t["name"] for t in nd["terms"] if t["name"]]
    return "node [" + ", ".join(names[:5]) + "]"


def main():
    nodes = NT["diagrams"][K]["nodes"]
    by_uid = {nd["uid"]: nd for nd in nodes}
    src = defaultdict(list)     # wire -> [(uid, term index, name)]
    snk = defaultdict(list)
    for nd in nodes:
        for t in nd["terms"]:
            if not t["wire"]:
                continue
            (src if t["is_source"] else snk)[t["wire"]].append((nd["uid"], t["i"], t["name"]))
    wires = set(src) | set(snk)
    # Peer (archive/peer/2026-09-14-wiregraph-frame-loop-plan.md) s1: prove "wire uid = logical net" before slicing.
    # Histogram: sources per wire (must be 1; >1 = reporter/direction anomaly) and sinks per wire (fan-out shares
    # the uid iff >1 appears). A singleton (one side only) is an UNRESOLVED HALF-EDGE, not a proven boundary.
    hist = {"sources>1": [w for w in wires if len(src.get(w, [])) > 1],
            "fanout_sinks>=2": sum(1 for w in wires if len(snk.get(w, [])) >= 2),
            "max_sinks": max((len(v) for v in snk.values()), default=0),
            "source_only": sum(1 for w in wires if w in src and w not in snk),
            "sink_only": sum(1 for w in wires if w in snk and w not in src)}
    print("wire histogram:", hist, flush=True)
    edges = []              # (wire, from uid, to uid, name, cut?)
    boundary = []           # unresolved half-edges
    for w in sorted(wires):
        s, k_ = src.get(w, []), snk.get(w, [])
        name = next((n for _u, _i, n in s + k_ if n), "")
        cut = bool(CUT_RE.search(name))
        if s and k_:
            for su, si, sn in s:
                for ku, ki, kn in k_:
                    if su != ku:
                        edges.append((w, su, ku, name, cut))
        else:
            boundary.append({"wire": w, "side": "source only" if s else "sink only",
                             "nodes": [(u, i, n) for u, i, n in (s or k_)], "name": name, "cut": cut})
    adj_all = defaultdict(set); adj_cut = defaultdict(set)
    fwd = defaultdict(set); bwd = defaultdict(set)
    for w, a, b, name, cut in edges:
        adj_all[a].add(b); adj_all[b].add(a)
        if not cut:
            adj_cut[a].add(b); adj_cut[b].add(a); fwd[a].add(b); bwd[b].add(a)

    def components(adj):
        seen, comps = set(), []
        for nd in nodes:
            u = nd["uid"]
            if u in seen:
                continue
            comp, dq = [], deque([u]); seen.add(u)
            while dq:
                x = dq.popleft(); comp.append(x)
                for y in adj[x]:
                    if y not in seen:
                        seen.add(y); dq.append(y)
            comps.append(sorted(comp))
        return sorted(comps, key=len, reverse=True)

    def slice_(start, nbrs):
        seen, dq = {start}, deque([start])
        while dq:
            x = dq.popleft()
            for y in nbrs[x]:
                if y not in seen:
                    seen.add(y); dq.append(y)
        seen.discard(start)
        return sorted(seen)

    comps_cut = components(adj_cut)
    comps_all = components(adj_all)
    back = slice_(KERNEL, bwd) if KERNEL in by_uid else []
    fore = slice_(KERNEL, fwd) if KERNEL in by_uid else []
    kernel_inputs = []
    if KERNEL in by_uid:
        for t in by_uid[KERNEL]["terms"]:
            if t["name"] and not t["is_source"]:
                feeders = [(u, n) for u, _i, n in src.get(t["wire"], [])]
                kernel_inputs.append({"terminal": t["name"], "wire": t["wire"],
                                      "from": [(u, node_label(by_uid[u])) for u, _n in feeders] if t["wire"] else "unwired/boundary"})
        kernel_outputs = [{"terminal": t["name"], "wire": t["wire"],
                           "to": [(u, node_label(by_uid[u])) for u, _i, _n in snk.get(t["wire"], [])]}
                          for t in by_uid[KERNEL]["terms"] if t["name"] and t["is_source"]]
    else:
        kernel_outputs = []

    out = {"diagram": int(K), "owner": NT["diagrams"][K]["owner"], "nodes": len(nodes), "wires": len(wires), "wire_histogram": hist,
           "edges": [{"wire": w, "from": a, "to": b, "name": n, "cut": c} for w, a, b, n, c in edges],
           "boundary": boundary, "cut_rule": CUT_RE.pattern,
           "components_after_cut": [{"size": len(c), "uids": c, "labels": [node_label(by_uid[u]) for u in c]} for c in comps_cut],
           "components_no_cut": [{"size": len(c), "uids": c} for c in comps_all],
           "kernel": {"uid": KERNEL, "inputs": kernel_inputs, "outputs": kernel_outputs,
                      "backward_slice": [(u, node_label(by_uid[u])) for u in back],
                      "forward_slice": [(u, node_label(by_uid[u])) for u in fore]}}
    with open(os.path.join(HERE, f"frame_loop_graph_{K}.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    L = [f"# Frame loop (diagram {K}) — functional units from the wire graph (measured 2026-09-14, offline)", "",
         f"Source: `tools/bench/main_vi_nodeterms.json` (every terminal's wire and direction), `main_vi_subvis.json` "
         f"(callee identity), `diagram_tree_main.json` (structures). {len(nodes)} nodes, {len(wires)} wire uids, "
         f"{len(edges)} directed edges, {len(boundary)} unresolved half-edges (a wire seen on one side only inside the "
         f"diagram: the loop's own tunnels/shift registers, a tunnel object outside Nodes[], or a fan-out branch — not "
         f"proven to be the loop border). Positions were never used. Generated by `tools/bench/wiregraph_frame_loop.py`.",
         "", f"**Wire-uid = logical net, checked (peer s1):** wires with more than one source: {len(hist['sources>1'])} "
             f"(expected 0); wires with ≥2 sinks (fan-out sharing one uid): {hist['fanout_sinks>=2']} (max sinks "
             f"{hist['max_sinks']}); source-only {hist['source_only']}, sink-only {hist['sink_only']}. Nested structures' "
             "tunnels appear as terminals of the structure node with BOTH sides (outer wire on the source-flagged entry, "
             "inner wire on the sink-flagged entry) — observed on the case structure #5540 feeding the kernel; per-case "
             "inner wires are NOT separated here (a case's output tunnel may have a different inner wire per case).",
         "", f"**Plumbing cut before componentising** (regex `{CUT_RE.pattern}` on the wire's terminal name): "
             f"{sum(1 for e in edges if e[4])} of {len(edges)} edges. Without the cut the diagram is "
             f"{len(comps_all)} component(s) (sizes {[len(c) for c in comps_all][:6]}); with it, {len(comps_cut)}.",
         "", f"## The tracking kernel call (#{KERNEL}) — what feeds it, what consumes it", "",
         "| input terminal | wire | fed by |", "|---|---:|---|"]
    for r in kernel_inputs:
        L.append(f"| `{r['terminal']}` | {r['wire']} | {r['from'] if isinstance(r['from'], str) else '; '.join(f'#{u} {l}' for u, l in r['from']) or '(boundary: tunnel / shift register)'} |")
    L += ["", "| output terminal | wire | consumed by |", "|---|---:|---|"]
    for r in kernel_outputs:
        L.append(f"| `{r['terminal']}` | {r['wire']} | {'; '.join(f'#{u} {l}' for u, l in r['to']) or '(boundary)'} |")
    L += ["", f"Backward slice (everything upstream of the kernel through data wires, {len(back)} nodes): " +
              "; ".join(f"#{u} {l}" for u, l in out['kernel']['backward_slice']),
          "", f"Forward slice ({len(fore)} nodes): " + "; ".join(f"#{u} {l}" for u, l in out['kernel']['forward_slice']),
          "", "## Components after the plumbing cut (candidate functional units)", ""]
    for i, c in enumerate(comps_cut):
        L.append(f"### unit {i} — {len(c)} node(s)")
        L.append("")
        for u in c:
            L.append(f"- #{u} {node_label(by_uid[u])}")
        L.append("")
    L += ["## Boundary wires (cross the WhileLoop's border: tunnels / shift registers)", "",
          "| wire | side inside | node, terminal | name | plumbing? |", "|---:|---|---|---|---|"]
    for b in boundary:
        L.append(f"| {b['wire']} | {b['side']} | " + "; ".join(f"#{u} t{i}" for u, i, _n in b["nodes"]) +
                 f" | `{b['name']}` | {'cut' if b['cut'] else ''} |")
    L += ["", "## Reading this", "",
          "A component is a *candidate* unit: nodes joined by data wires other than error clusters, refnums and "
          "timers. Two units joined only by an error wire were deliberately separated; a unit that is really two "
          "features joined by a real data wire stays one here — the cut rule is the only judgement in this file and "
          "it is printed above. Nested structures are single nodes; their bodies are other diagrams (see the tree).",
          "", f"_Generated {time.strftime('%Y-%m-%d %H:%M')}._", ""]
    doc = os.path.join(ROOT, "docs", f"frame-loop-wire-graph.md" if K == "43" else f"wire-graph-diagram-{K}.md")
    open(doc, "w", encoding="utf-8").write("\n".join(L))
    print(f"diagram {K}: {len(nodes)} nodes, {len(wires)} wires, {len(edges)} edges ({sum(1 for e in edges if e[4])} cut), "
          f"{len(boundary)} boundary; components no-cut {[len(c) for c in comps_all][:8]}, after cut {[len(c) for c in comps_cut][:12]}")
    print(f"kernel backward slice {len(back)} nodes, forward {len(fore)} -> {doc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
