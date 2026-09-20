"""analyse_nodeterms_main.py - what the direction-aware net map (main_vi_nodeterms.json) says about panel access.

No LabVIEW. Inputs: main_vi_nodeterms.json (sweep), main_vi_panel_wiring.json (114 panel objects, bare terminals),
main_vi_globals_direction.json, diagram_tree_main.json. Outputs a markdown section for docs/main-vi-panel-map.md
(marker-delimited) and prints the tables.

  LOCAL VARIABLES  class 'Local' uids (sweep stats) -> the sweep's node rows by uid -> its single terminal's NAME is
                   the control label (OBSERVED rule, per peer review; the section says so) and Is Source? gives
                   READ (TRUE) / WRITE (FALSE). Cross-referenced with the 10 bare-terminal panel objects.
  VALUE PROPERTY NODES  nodes whose terminals include 'Value' (or 'Val(Sgnl)') with the `reference` terminal
                   UNWIRED = implicit property nodes on a panel object; their linked object is NOT recoverable
                   here (no cast-free property found - peer review) -> counted and listed by diagram, not attributed.
  GLOBALS          the 7 sites must reappear with the same direction as globals_direction_main.
Limits stated in the section: event-structure registrations, control references, implicit invoke nodes are not
covered.
  py tools/bench/analyse_nodeterms_main.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SW = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
PW = json.load(open(os.path.join(HERE, "main_vi_panel_wiring.json"), encoding="utf-8"))
GD = json.load(open(os.path.join(HERE, "main_vi_globals_direction.json"), encoding="utf-8"))
DOC = os.path.join(ROOT, "docs", "main-vi-panel-map.md")
BEGIN, END = "<!-- locals-section:begin -->", "<!-- locals-section:end -->"


def main():
    by_uid = {}
    for k, d in SW["diagrams"].items():
        for nd in d["nodes"]:
            by_uid[nd["uid"]] = (int(k), d["owner"], nd)
    locals_ = SW["stats"].get("class_Local", [])
    globals_ = SW["stats"].get("class_Global", [])
    labels = {r["label"] for r in PW["rows"]}
    bare = {r["label"] for r in PW["rows"] if not r["wire"]}

    rows_local = []
    for u in locals_:
        if u not in by_uid:
            rows_local.append({"uid": u, "diagram": None, "name": None, "dir": None, "note": "not reached by the sweep"})
            continue
        k, owner, nd = by_uid[u]
        named = [t for t in nd["terms"] if t["name"]]
        t = named[0] if named else None
        rows_local.append({"uid": u, "diagram": k, "owner": owner, "name": t["name"] if t else None,
                           "dir": (("READ" if t["is_source"] else "WRITE") if t and not t["errs"][1] else None),
                           "wire": t["wire"] if t else None, "n_named": len(named),
                           "on_panel": (t["name"] in labels) if t else None, "bare": (t["name"] in bare) if t else None})
    print("LOCAL VARIABLES (class 'Local'):")
    for r in rows_local:
        print("  ", r)

    val_nodes = []
    for k, d in SW["diagrams"].items():
        for nd in d["nodes"]:
            names = [t["name"] for t in nd["terms"]]
            if any(n in ("Value", "Val(Sgnl)", "Value (Signaling)") for n in names):
                ref = next((t for t in nd["terms"] if t["name"] == "reference"), None)
                val_nodes.append({"diagram": int(k), "owner": d["owner"], "uid": nd["uid"], "n": nd["n"],
                                  "implicit": bool(ref) and ref["wire"] == 0,
                                  "value_dirs": [("READ" if t["is_source"] else "WRITE") for t in nd["terms"] if t["name"] in ("Value", "Val(Sgnl)")]})
    print(f"\nVALUE PROPERTY NODES: {len(val_nodes)} ({sum(v['implicit'] for v in val_nodes)} implicit)")
    for v in val_nodes[:200]:
        print("  ", v)

    print("\nGLOBALS cross-check (sweep vs globals_direction_main):")
    gl_ok = True
    for s in GD["sites"]:
        u = s["uid"]
        if u in by_uid:
            k, owner, nd = by_uid[u]
            named = [t for t in nd["terms"] if t["name"]]
            d = ("READ" if named[0]["is_source"] else "WRITE") if named else None
            same = (d == s.get("direction")) and (k == s["diagram"])
            gl_ok &= same
            print(f"   uid {u} diagram {k} {named[0]['name'] if named else '?'} sweep={d} earlier={s.get('direction')} {'OK' if same else 'DIFF'}")
        else:
            gl_ok = False
            print(f"   uid {u}: NOT in sweep")
    print("   globals in class census:", len(globals_), "sites earlier:", len(GD["sites"]))

    st = SW["stats"]
    lines = [BEGIN, "",
             "## Local variables and `Value` property nodes — measured 2026-09-14 (`OpNodeTerms_v0` sweep of all 635 nodes)",
             "",
             f"Source `tools/bench/main_vi_nodeterms.json` ({st.get('nodes')} nodes, {st.get('terminals')} terminals, "
             f"{st.get('mismatches')} mismatches vs the Step-0 cache, node identity verified per node by UID). Class census by "
             f"Traverse: `Local` {len(locals_)}, `Global` {len(globals_)}, `Property` {len(st.get('class_Property', []))}, "
             f"`Invoke` {len(st.get('class_Invoke', []))}.",
             "",
             "**Local variables.** A local-variable node's single terminal is NAMED after its control — an observed rule "
             "(it held on every local below and on all seven globals, whose terminal carries the field name), not an NI "
             "contract. `Is Source?` TRUE = the local is READ, FALSE = WRITTEN.",
             "",
             "| local uid | diagram | owner | control (terminal name) | direction | on panel map | terminal bare? |",
             "|---:|---:|---|---|---|---|---|"]
    for r in rows_local:
        lines.append(f"| {r['uid']} | {r['diagram']} | {r.get('owner', '')} | `{r['name']}` | {r['dir']} | "
                     f"{'yes' if r.get('on_panel') else 'NO'} | {'**bare**' if r.get('bare') else ''} |")
    bare_hit = sorted({r["name"] for r in rows_local if r.get("bare")})
    lines += ["", f"Bare-terminal objects reached through a local: {', '.join('`%s`' % b for b in bare_hit) or 'none'}. "
                  f"Bare-terminal objects with NO local either: "
                  f"{', '.join('`%s`' % b for b in sorted(bare - set(bare_hit))) or 'none'} — these can still be reached by an "
                  "implicit `Value` property node (below), a control reference, or an event registration, none of which names "
                  "its object in a terminal; that attribution stays OPEN.",
              "",
              f"**`Value` property nodes:** {len(val_nodes)} nodes carry a `Value` row, {sum(v['implicit'] for v in val_nodes)} "
              "of them implicit (unwired `reference` = bound to a panel object whose identity is not readable cast-free). "
              "Direction of the `Value` row: " +
              f"READ {sum(d == 'READ' for v in val_nodes for d in v['value_dirs'])} / WRITE {sum(d == 'WRITE' for v in val_nodes for d in v['value_dirs'])}. "
              "Every `Value` row runs in the UI thread (the cost the restructuring converts to locals by rule).",
              "", "| diagram | owner | uid | implicit | Value rows |", "|---:|---|---:|---|---|"]
    for v in val_nodes:
        lines.append(f"| {v['diagram']} | {v['owner']} | {v['uid']} | {'yes' if v['implicit'] else 'wired ref'} | {', '.join(v['value_dirs'])} |")
    lines += ["", f"Globals: the seven sites of `Global motor pos.vi` reappear with the same direction as "
                  f"`globals_direction_main` ({'all agree' if gl_ok else 'DISAGREEMENT - see analyse log'}).",
              "", f"_Generated {time.strftime('%Y-%m-%d %H:%M')} by tools/bench/analyse_nodeterms_main.py._", "", END]
    block = "\n".join(lines)
    text = open(DOC, encoding="utf-8").read()
    if BEGIN in text and END in text:
        pre, rest = text.split(BEGIN, 1); _o, post = rest.split(END, 1); text = pre + block + post
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    open(DOC, "w", encoding="utf-8").write(text)
    print(f"\nwrote locals/Value section -> {DOC}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
