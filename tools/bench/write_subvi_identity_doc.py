"""write_subvi_identity_doc.py - docs/main-vi-subvi-identity.md from tools/bench/main_vi_subvis.json (no LabVIEW).

The document answers "which VI does call site X (uid) on diagram D call" for the whole main VI - the gap every
2026-09-14 document left open. Two views: per diagram (with the diagram's owner structure from the Step-0 tree) and
per callee (call count, diagrams). Mismatches against the cache are listed verbatim; none are hidden.
  py tools/bench/write_subvi_identity_doc.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SRC = os.path.join(HERE, "main_vi_subvis.json")
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "docs", "main-vi-subvi-identity.md")


def main():
    d = json.load(open(SRC, encoding="utf-8"))
    dias = d["diagrams"]
    n_sites = sum(len(v) for v in dias.values())
    lines = [
        "# Main VI — subVI identity per call site (measured 2026-09-14)",
        "",
        f"Source: `tools/bench/main_vi_subvis.json`, produced by `tools/bench/sweep_subvis_main.py` running `OpSubVIs_v1` "
        f"(`gscript.subvis`) once per diagram over all {len(TREE['diagrams'])} diagrams of "
        f"`{os.path.basename(d['vi'])}`. Every row is a machine read of `AbstractDiagram.SubVIs[]` → `SubVI.VI Name` / "
        f"`VI Path` / `GObject.UID` — no inference, no label reading. Cross-checked per diagram against the Step-0 "
        f"diagram tree (`diagram_tree_main.json`): **{len(d['mismatches'])} mismatches** (listed at the end).",
        "",
        f"**{n_sites} call sites, {len(d['callees'])} distinct callees.** Diagram index = Traverse `Diagram` order "
        "(0 = top level), the same index `net_map`, the netmap cache and the diagram tree use; a subVI inside a "
        "structure belongs to that structure's own diagram (SubVIs[] is not recursive). Node positions carry no "
        "meaning (the diagram was Cleaned Up) — group by diagram and by wire graph, never by coordinates.",
        "",
        "## By callee (call count → diagrams)",
        "",
        "| calls | callee | diagrams (uid) |",
        "|---:|---|---|",
    ]
    for name, uids in sorted(d["callees"].items(), key=lambda kv: (-len(kv[1]), kv[0].lower())):
        where = ", ".join(f"{d['by_uid'][str(u)]['diagram']} (#{u})" for u in uids)
        lines.append(f"| {len(uids)} | `{name}` | {where} |")
    lines += ["", "## By diagram", "", "| diagram | owner structure | call sites (callee #uid) |", "|---:|---|---|"]
    for k in sorted(dias, key=int):
        rows = dias[k]
        if not rows:
            continue
        owner = TREE["diagrams"][k]["owner"] or "top level"
        lines.append(f"| {k} | {owner} | " + "; ".join(f"`{r['name']}` #{r['uid']}" for r in rows) + " |")
    empty = [k for k in sorted(dias, key=int) if not dias[k]]
    lines += ["", f"Diagrams with no subVI call ({len(empty)}): " + ", ".join(empty), "",
              "## Paths (distinct callees → where the file lives)", "", "| callee | path |", "|---|---|"]
    seen = {}
    for k in dias:
        for r in dias[k]:
            seen.setdefault(r["name"], r["path"])
    for name in sorted(seen, key=str.lower):
        lines.append(f"| `{name}` | `{seen[name]}` |")
    lines += ["", "## Mismatches against the cache", ""]
    if d["mismatches"]:
        for m in d["mismatches"]:
            lines.append(f"- diagram {m.get('diagram')}: {json.dumps(m, ensure_ascii=False)}")
    else:
        lines.append("None — every diagram's UID set equals the Step-0 tree's (diagram uids ∩ subVI uids).")
    lines += ["", f"_Generated {time.strftime('%Y-%m-%d %H:%M')} by tools/bench/write_subvi_identity_doc.py._", ""]
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"wrote {OUT}: {n_sites} sites, {len(d['callees'])} callees, {len(d['mismatches'])} mismatches")
    return 0


if __name__ == "__main__":
    sys.exit(main())
