"""stitch_frame_loop_border.py - name the frame loop's border: which tunnels carry what in and out of diagram 43.

Offline. Inputs: main_vi_tunnels.json (every LoopTunnel: outer wire, inner wire(s), directions, IndexMode),
main_vi_nodeterms.json (per-terminal wires of every node), main_vi_subvis.json (identity), frame_loop_graph_43.json
(the half-edges), diagram_tree_main.json. A tunnel belongs to loop 43 iff its INNER wire is a wire of a diagram-43
node's terminal (or its outer wire is a diagram-19 node's wire and the inner one is a 43 half-edge). For each such
tunnel: direction (outer Is Source? FALSE = INPUT to the loop), the parent-side source node (diagram 19) and the
body-side consumer/producer nodes, with terminal names - i.e. "what enters the frame loop and from where". Writes
a section into docs/frame-loop-wire-graph.md (marker-delimited) and tools/bench/frame_loop_border.json.
  py tools/bench/stitch_frame_loop_border.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TN = json.load(open(os.path.join(HERE, "main_vi_tunnels.json"), encoding="utf-8"))["tunnels"]
NT = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
SV = json.load(open(os.path.join(HERE, "main_vi_subvis.json"), encoding="utf-8"))
G = json.load(open(os.path.join(HERE, "frame_loop_graph_43.json"), encoding="utf-8"))
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
K, PARENT = "43", "19"
DOC = os.path.join(ROOT, "docs", "frame-loop-wire-graph.md")
BEGIN, END = "<!-- border-section:begin -->", "<!-- border-section:end -->"


def wire_index(k):
    """wire uid -> [(node uid, terminal name, is_source)] for diagram k."""
    idx = {}
    for nd in NT["diagrams"][k]["nodes"]:
        for t in nd["terms"]:
            if t["wire"]:
                idx.setdefault(t["wire"], []).append((nd["uid"], t["name"], t["is_source"]))
    return idx


def label(u):
    ident = SV["by_uid"].get(str(u), {}).get("name")
    return f"subVI {ident}" if ident else f"#{u}"


def main():
    w43, w19 = wire_index(K), wire_index(PARENT)
    half = {b["wire"]: b for b in G["boundary"]}
    border = []
    for t in TN:
        inner = [w for w in t["in_wires"] if w]
        if not (any(w in w43 for w in inner) or (t["out_wire"] in w19 and any(w in half for w in inner))):
            continue
        direction = "INPUT" if not t["out_is_source"] else "OUTPUT"
        outer_nodes = w19.get(t["out_wire"], [])
        inner_nodes = [n for w in inner for n in w43.get(w, [])]
        border.append({"tunnel_uid": t["uid"], "direction": direction, "index_mode": t["index_mode"],
                       "outer_wire": t["out_wire"], "inner_wires": inner,
                       "outer_side": [(u, nm, src) for u, nm, src in outer_nodes],
                       "inner_side": [(u, nm, src) for u, nm, src in inner_nodes],
                       "half_edges_resolved": [w for w in inner if w in half]})
    resolved = {w for b in border for w in b["half_edges_resolved"]}
    unresolved = [b for w, b in half.items() if w not in resolved]
    out = {"diagram": int(K), "parent": int(PARENT), "border": border,
           "half_edges_total": len(half), "resolved_by_looptunnels": len(resolved), "unresolved": unresolved}
    with open(os.path.join(HERE, "frame_loop_border.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)

    ins = [b for b in border if b["direction"] == "INPUT"]; outs = [b for b in border if b["direction"] == "OUTPUT"]
    L = [BEGIN, "", "## The loop border, named (LoopTunnel census `OpTunnels_v0`, 2026-09-14)", "",
         f"{len(border)} LoopTunnels belong to the frame loop ({len(ins)} inputs, {len(outs)} outputs); they explain "
         f"{len(resolved)} of the {len(half)} half-edges. The {len(unresolved)} left are shift registers (not LoopTunnels — "
         "the loop's per-frame state), the loop's own `i`/conditional terminals, or wires to tunnels of nested structures "
         "(see the unresolved list). Direction: outer terminal is a sink → the tunnel feeds the loop (INPUT).", "",
         "### Inputs (what the frame loop consumes from its parent, diagram 19)", "",
         "| tunnel | index mode | comes from (diagram 19 node · terminal) | used inside by (diagram 43 node · terminal) |",
         "|---:|---|---|---|"]
    for b in ins:
        src = "; ".join(f"{label(u)} · `{nm}`" for u, nm, s in b["outer_side"] if s) or "(no source node on 19: a further tunnel/shift register/constant)"
        dst = "; ".join(f"{label(u)} · `{nm}`" for u, nm, s in b["inner_side"] if not s) or "(no consumer node in 43: feeds a nested structure or unused)"
        L.append(f"| {b['tunnel_uid']} | {'auto-index' if b['index_mode'] else 'plain'} | {src} | {dst} |")
    L += ["", "### Outputs (what leaves the frame loop)", "", "| tunnel | index mode | produced inside by | consumed on diagram 19 by |", "|---:|---|---|---|"]
    for b in outs:
        src = "; ".join(f"{label(u)} · `{nm}`" for u, nm, s in b["inner_side"] if s) or "(no producer node in 43)"
        dst = "; ".join(f"{label(u)} · `{nm}`" for u, nm, s in b["outer_side"] if not s) or "(no consumer on 19)"
        L.append(f"| {b['tunnel_uid']} | {'auto-index' if b['index_mode'] else 'plain'} | {src} | {dst} |")
    L += ["", f"### Still unresolved half-edges ({len(unresolved)})", "", "| wire | side inside 43 | node · terminal | name |", "|---:|---|---|---|"]
    for b in unresolved:
        L.append(f"| {b['wire']} | {b['side']} | " + "; ".join(f"{label(u)} t{i}" for u, i, _n in b["nodes"]) + f" | `{b['name']}` |")
    L += ["", f"_Generated {time.strftime('%Y-%m-%d %H:%M')} by tools/bench/stitch_frame_loop_border.py._", "", END]
    block = "\n".join(L)
    text = open(DOC, encoding="utf-8").read()
    if BEGIN in text and END in text:
        pre, rest = text.split(BEGIN, 1); _o, post = rest.split(END, 1); text = pre + block + post
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    open(DOC, "w", encoding="utf-8").write(text)
    print(f"frame loop border: {len(border)} tunnels ({len(ins)} in / {len(outs)} out); half-edges {len(resolved)}/{len(half)} resolved; "
          f"{len(unresolved)} unresolved -> {DOC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
