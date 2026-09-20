"""write_implicit_pn_section.py - offline: join main_vi_node_labels.json (OpNodeLabels_v0 sweep) with the Value census
(main_vi_nodeterms.json) and APPEND the attribution section to docs/main-vi-panel-map.md. Prints the per-object table
and the answers to the open attribution questions (Rot Speed and the five terminal-less objects).
  py tools/bench/write_implicit_pn_section.py
"""
import json
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
DOC = os.path.join(ROOT, "docs", "main-vi-panel-map.md")
NL = json.load(open(os.path.join(HERE, "main_vi_node_labels.json"), encoding="utf-8"))
NT = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
PANEL = json.load(open(os.path.join(HERE, "main_vi_panel_wiring.json"), encoding="utf-8"))["rows"]
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
OWNERS = TREE.get("owners", {})

direction = {}      # uid -> READ / WRITE (Value terminal is a source => the node READS the object)
for di, dg in NT["diagrams"].items():
    for nd in dg["nodes"]:
        for t in nd["terms"]:
            if t["name"] == "Value":
                direction[nd["uid"]] = "READ" if t["is_source"] else "WRITE"

per_obj = defaultdict(lambda: {"READ": 0, "WRITE": 0, "diagrams": set(), "uids": []})
for uid, row in NL["implicit"].items():
    lab = row["label"]; d = per_obj[lab]
    d[direction.get(int(uid), "?")] += 1; d["diagrams"].add(row["diagram"]); d["uids"].append(int(uid))

panel = {r["label"]: r for r in PANEL if r.get("label")}
bare = [r["label"] for r in PANEL if r.get("label") and not r.get("wire")]
lines = []
lines.append("\n## Implicit `Value` property nodes → panel objects — MEASURED 2026-09-14 (`OpNodeLabels_v0`, 88/88)\n")
lines.append("Source `tools/bench/main_vi_node_labels.json` (`test_opnodelabels.py` T3: every one of the 88 implicit `Value` nodes "
             "returned a non-empty label that is a panel label; direction from the `Value` terminal's `Is Source?` in the "
             "terminal sweep). An implicit property node's header is its `Node.Label` (peer + LabVIEW Wiki), read headless with "
             "the panel closed — the never-displayed caveat did not bite. **This closes the 'bound object not readable' gap.**\n")
lines.append("| panel object | kind | terminal wired | implicit `Value` READ | WRITE | diagrams |")
lines.append("|---|---|---|---:|---:|---|")
for lab in sorted(per_obj, key=lambda s: (-(per_obj[s]["READ"] + per_obj[s]["WRITE"]), s)):
    d = per_obj[lab]; p = panel.get(lab, {})
    kind = "indicator" if p.get("indicator") else "control"
    wired = "yes" if p.get("wire") else "**no**"
    lines.append(f"| `{lab!s}` | {kind} | {wired} | {d['READ']} | {d['WRITE']} | {', '.join(str(x) for x in sorted(d['diagrams']))} |")
n_obj = len(per_obj)
lines.append(f"\n{n_obj} distinct panel objects are reached by implicit `Value` nodes "
             f"({sum(d['READ'] for d in per_obj.values())} READ / {sum(d['WRITE'] for d in per_obj.values())} WRITE rows).")
newly = [b for b in bare if b in per_obj]
still = [b for b in bare if b not in per_obj]
lines.append(f"\n**Bare-terminal objects now attributed through an implicit `Value` node:** {', '.join('`' + b + '`' for b in newly) or 'none'}.  ")
lines.append(f"**Bare-terminal objects still without a `Value` node** (control reference / event registration / legacy): "
             f"{', '.join('`' + b + '`' for b in still) or 'none'}.")
with open(DOC, "a", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("\n".join(lines))
print("\nRot Speed candidates:", [k for k in per_obj if "Rot" in k and "Speed" in k])
