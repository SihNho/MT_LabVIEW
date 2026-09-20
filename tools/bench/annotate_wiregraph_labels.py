"""annotate_wiregraph_labels.py - offline: name the anonymous nodes of docs/frame-loop-wire-graph.md with the labels
measured by OpNodeLabels_v0 (tools/bench/main_vi_node_labels.json). '#1469 Property [Value]' becomes
'#1469 Property `CycleSchedule`.Value [Value]'; '#1978 node [x+1, x]' becomes '#1978 Increment [x+1, x]'. SubVI
mentions already carry the file name and are left alone. Idempotent (a line already annotated is skipped).
  py tools/bench/annotate_wiregraph_labels.py
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(os.path.dirname(os.path.dirname(HERE)), "docs", "frame-loop-wire-graph.md")
NL = json.load(open(os.path.join(HERE, "main_vi_node_labels.json"), encoding="utf-8"))
label = {}
for rows in NL["diagrams"].values():
    for r in rows:
        label[r["uid"]] = r["label"].replace("\n", "\\n")
implicit = {int(u) for u in NL["implicit"]}

text = open(DOC, encoding="utf-8").read()
n_prop = n_node = 0


def prop(m):
    global n_prop
    uid = int(m.group(1)); lab = label.get(uid)
    if not lab:
        return m.group(0)
    n_prop += 1
    kind = "implicit" if uid in implicit else "explicit"
    return f"#{uid} Property `{lab}`.{m.group(2)} ({kind})"


def node(m):
    global n_node
    uid = int(m.group(1)); lab = label.get(uid)
    if not lab:
        return m.group(0)
    n_node += 1
    return f"#{uid} {lab} ["


text2 = re.sub(r"#(\d+) Property \[(Value|[^\]]+)\](?! \()", prop, text)
text2 = re.sub(r"#(\d+) node \[", node, text2)
if text2 != text:
    with open(DOC, "w", encoding="utf-8") as f:
        f.write(text2)
print(f"annotated {n_prop} property mentions and {n_node} anonymous nodes in {os.path.basename(DOC)}")
