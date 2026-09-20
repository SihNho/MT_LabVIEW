"""stitch_shiftregs_measured.py - offline: join the measured shift registers of the frame loop
(tools/bench/main_vi_shiftregs.json, OpShiftRegs_v0) with the terminal sweep (main_vi_nodeterms.json, diagram 43 body,
diagram 19 parent) and the node labels (main_vi_node_labels.json), and APPEND a MEASURED section to
docs/frame-loop-wire-graph.md: per right register - name, the body node/terminal that feeds it each frame (inner sink
wire), the parent-side consumer of the final value (outer source wire), and how many of the body's half-edges this
resolves. Idempotent by marker.
  py tools/bench/stitch_shiftregs_measured.py
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "frame-loop-wire-graph.md")
SR = json.load(open(os.path.join(HERE, "main_vi_shiftregs.json"), encoding="utf-8"))
NT = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
NL = json.load(open(os.path.join(HERE, "main_vi_node_labels.json"), encoding="utf-8"))
LABEL = {r["uid"]: r["label"].replace("\n", "\\n") for rows in NL["diagrams"].values() for r in rows}
BODY, PARENT = "43", "19"
MARK = "## Per-frame STATE carriers — MEASURED (OpShiftRegs_v0, right registers, 2026-09-14 15:3x)"


def terms(diagram):
    out = defaultdict(list)          # wire uid -> [(node uid, term index, term name, is_source)]
    for nd in NT["diagrams"][diagram]["nodes"]:
        for t in nd["terms"]:
            if t["wire"]:
                out[t["wire"]].append((nd["uid"], t["i"], t["name"], t["is_source"]))
    return out


def who(entries, want_source):
    return "; ".join(f"#{u} {LABEL.get(u, 'node')} t{i} `{n}`" for u, i, n, s in entries if s == want_source) or "—"


body, parent = terms(BODY), terms(PARENT)
half = {w for w, es in body.items() if len({s for _u, _i, _n, s in es}) == 1}   # only sources or only sinks seen in the body
regs = SR["registers"]
lines = ["", MARK, "",
         "Source `tools/bench/main_vi_shiftregs.json` (`test_opshiftregs.py`): `Loop.Shift Registers[]` of the frame loop (WhileLoop "
         "uid 637) lists its **14 RIGHT registers**. Each has one inside terminal (sink: what the body writes into the "
         "register every frame) and one outside terminal (source: the final value after the loop). The register's name is "
         "its inside terminal's name. The LEFT side (initial value in, body-side source) is v1 (`Left Registers[]`).", "",
         "| # | register (inside terminal name) | uid | fed each frame by (body, wire) | final value consumed by (diagram 19, wire) |",
         "|---:|---|---:|---|---|"]
resolved = set()
for k, r in enumerate(regs):
    inn = r["inside"][0] if r["inside"] else {"name": "", "wire": 0}
    w_in, w_out = inn["wire"], r["out"]["wire"]
    if w_in in half:
        resolved.add(w_in)
    feed = f"{who(body.get(w_in, []), True)} (wire {w_in})" if w_in else "—"
    cons = f"{who(parent.get(w_out, []), False)} (wire {w_out})" if w_out else "— (final value unused)"
    lines.append(f"| {k} | `{inn['name'] or '(unnamed)'}` | {r['uid']} | {feed} | {cons} |")
lines += ["", f"Of the body's {len(half)} half-edge wires, {len(resolved)} are now explained as **writes into a right shift "
          f"register** (wires {sorted(resolved)}); the remaining ones are reads from left registers / tunnels and are the "
          f"target of v1. Final values that leave the loop: {sum(1 for r in regs if r['out']['wire'])} of {len(regs)}."]
text = open(DOC, encoding="utf-8").read()
if MARK not in text:
    with open(DOC, "a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
print("\n".join(lines).encode("ascii", "replace").decode())
