"""reconcile_frame_loop_halfedges.py - offline: account for EVERY one-sided wire of the frame loop body (diagram 43)
with the measured sources: shift registers (main_vi_shiftregs{,_v1}.json), LoopTunnels (main_vi_tunnels.json: inner
wires of every tunnel), and nested structures (a wire whose only body-side end is a structure node's own terminal =
that structure's tunnel, inner side unseen here). Appends the accounting section to docs/frame-loop-wire-graph.md.
  py tools/bench/reconcile_frame_loop_halfedges.py
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "frame-loop-wire-graph.md")
NT = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
TUN = json.load(open(os.path.join(HERE, "main_vi_tunnels.json"), encoding="utf-8"))["tunnels"]
SR0 = json.load(open(os.path.join(HERE, "main_vi_shiftregs.json"), encoding="utf-8"))["registers"]
SR1 = json.load(open(os.path.join(HERE, "main_vi_shiftregs_v1.json"), encoding="utf-8"))["registers"]
NL = json.load(open(os.path.join(HERE, "main_vi_node_labels.json"), encoding="utf-8"))
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
LABEL = {r["uid"]: r["label"].replace("\n", "\\n") for rows in NL["diagrams"].values() for r in rows}
STRUCT = {u for cls, us in TREE["structures"].items() for u in us}
BODY = "43"
MARK = "## Half-edge accounting of the frame loop body — MEASURED (2026-09-14 15:5x)"

body = defaultdict(list)
for nd in NT["diagrams"][BODY]["nodes"]:
    for t in nd["terms"]:
        if t["wire"]:
            body[t["wire"]].append((nd["uid"], t["i"], t["name"], t["is_source"]))
half = {w: es for w, es in body.items() if len({s for _u, _i, _n, s in es}) == 1}
reg_w = {r["inside"][0]["wire"] for r in SR0 if r["inside"]} | {l["inside"][0]["wire"] for r in SR1 for l in r["lefts"] if l["inside"]}
tun_in = {w: t for t in TUN for w in t["in_wires"] if w}
tun_out = {t["out_wire"]: t for t in TUN if t["out_wire"]}
PANEL = json.load(open(os.path.join(HERE, "main_vi_panel_wiring.json"), encoding="utf-8"))["rows"]
panel_w = {r["wire"]: r for r in PANEL if r.get("wire")}
cats = defaultdict(list)
for w, es in sorted(half.items()):
    only_sinks = all(not s for _u, _i, _n, s in es)
    if w in reg_w:
        cats["shift register (measured)"].append(w)
    elif w in tun_in:
        cats["frame-loop tunnel, inner side (LoopTunnel census)"].append(w)
    elif all(u in STRUCT for u, _i, _n, _s in es):
        cats["nested structure's own tunnel (case/loop inside the body; inner side lives in its sub-diagram)"].append(w)
    elif w in tun_out:
        cats["a nested loop's tunnel, outer side (LoopTunnel census)"].append(w)
    elif w in panel_w:
        kind = "indicator" if panel_w[w].get("indicator") else "control"
        cats[f"front-panel {kind} terminal (panel_wiring census; terminals are not Nodes[])"].append(w)
    elif only_sinks:
        cats["fed by a CONSTANT (inferred by elimination: sink-only, no node / tunnel / panel source; constants are not Nodes[] — 301 in the VI)"].append(w)
    else:
        cats["unexplained"].append(w)
lines = ["", MARK, "",
         f"{len(half)} one-sided wires in diagram 43 (a wire seen with only sources or only sinks among the body's nodes), "
         "attributed by MEASURED objects — shift registers (`OpShiftRegs_v0/v1`), the LoopTunnel census (`OpTunnels_v0`, all "
         "132 tunnels of the VI), and the structure census (`diagram_tree_main.json`):", "",
         "| explanation | wires | count |", "|---|---|---:|"]
for k, ws in cats.items():
    lines.append(f"| {k} | {', '.join(str(w) for w in ws)} | {len(ws)} |")
unex = cats.get("unexplained", [])
if unex:
    lines += ["", "Unexplained wires and the terminals that touch them:"]
    for w in unex:
        lines.append(f"- wire {w}: " + "; ".join(f"#{u} {LABEL.get(u, 'node')} t{i} `{n}` ({'src' if s else 'sink'})" for u, i, n, s in half[w]))
lines += ["", f"Result: {len(half) - len(unex)} of {len(half)} explained by measurement; {len(unex)} left."]
text = open(DOC, encoding="utf-8").read()
if MARK in text:
    text = text[:text.index(MARK)].rstrip("\n") + "\n"
with open(DOC, "w", encoding="utf-8") as f:
    f.write(text + "\n".join(lines) + "\n")
print("\n".join(lines).encode("ascii", "replace").decode())
