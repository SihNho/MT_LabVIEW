"""stitch_shiftregs_left.py - offline: join the LEFT side of the frame loop's shift registers
(tools/bench/main_vi_shiftregs_v1.json, OpShiftRegs_v1) with the terminal sweep (diagram 43 body, 19 parent) and the
node labels, and APPEND the closing section to docs/frame-loop-wire-graph.md: per register - initial value source
(parent side of the left outside terminal), what reads it each frame (body sinks on the left inside wire), stacked
lefts, and the half-edge accounting (right-side writes + left-side reads). Idempotent by marker.
  py tools/bench/stitch_shiftregs_left.py
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "frame-loop-wire-graph.md")
SR = json.load(open(os.path.join(HERE, "main_vi_shiftregs_v1.json"), encoding="utf-8"))
NT = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
NL = json.load(open(os.path.join(HERE, "main_vi_node_labels.json"), encoding="utf-8"))
LABEL = {r["uid"]: r["label"].replace("\n", "\\n") for rows in NL["diagrams"].values() for r in rows}
BODY, PARENT = "43", "19"
MARK = "## Per-frame STATE carriers — MEASURED, LEFT side (OpShiftRegs_v1, 2026-09-14)"


def terms(diagram):
    out = defaultdict(list)
    for nd in NT["diagrams"][diagram]["nodes"]:
        for t in nd["terms"]:
            if t["wire"]:
                out[t["wire"]].append((nd["uid"], t["i"], t["name"], t["is_source"]))
    return out


def who(entries, want_source):
    return "; ".join(f"#{u} {LABEL.get(u, 'node')} t{i} `{n}`" for u, i, n, s in entries if s == want_source) or "—"


body, parent = terms(BODY), terms(PARENT)
half = {w for w, es in body.items() if len({s for _u, _i, _n, s in es}) == 1}
regs = SR["registers"]
lines = ["", MARK, "",
         "Source `tools/bench/main_vi_shiftregs_v1.json` (`test_opshiftregs_v1.py`): for each right register, "
         "`RightShiftRegister.Left Registers[]` (stacked lefts listed in order). Left OUTSIDE terminal = the initial value "
         "(sink; unwired = uninitialised, LabVIEW keeps the last value across runs); left INSIDE terminal = the source the "
         "body reads every frame. This closes the shift-register half of the loop border by measurement; the name-pairing "
         "section above is superseded.", "",
         "| # | register | initial value from (diagram 19, wire) | read each frame by (body, wire) | stacked lefts |",
         "|---:|---|---|---|---:|"]
resolved_r, resolved_l = set(), set()
for k, r in enumerate(regs):
    name = r["inside"][0]["name"] if r["inside"] else ""
    if r["inside"] and r["inside"][0]["wire"] in half:
        resolved_r.add(r["inside"][0]["wire"])
    cells_init, cells_read = [], []
    for j, l in enumerate(r["lefts"]):
        w_o = l["out"]["wire"]; w_i = l["inside"][0]["wire"] if l["inside"] else 0
        if w_i in half:
            resolved_l.add(w_i)
        tag = f"[{j}] " if len(r["lefts"]) > 1 else ""
        cells_init.append(f"{tag}{who(parent.get(w_o, []), True)} (wire {w_o})" if w_o else f"{tag}— (uninitialised)")
        cells_read.append(f"{tag}{who(body.get(w_i, []), False)} (wire {w_i})" if w_i else f"{tag}—")
    lines.append(f"| {k} | `{name or '(unnamed)'}` | {'<br>'.join(cells_init)} | {'<br>'.join(cells_read)} | {len(r['lefts'])} |")
lines += ["", f"Half-edge accounting for the body (diagram 43): {len(half)} one-sided wires; explained by right-register "
          f"writes: {len(resolved_r)}; by left-register reads: {len(resolved_l)}; by LoopTunnel census (section 'The loop "
          f"border, named'): see there; still open after both: {len(half) - len(resolved_r | resolved_l)} (tunnels, structure-side "
          f"terminals of nested cases, fan-out branches)."]
text = open(DOC, encoding="utf-8").read()
if MARK not in text:
    with open(DOC, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
print("\n".join(lines).encode("ascii", "replace").decode())
