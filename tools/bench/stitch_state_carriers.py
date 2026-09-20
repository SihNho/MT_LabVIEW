"""stitch_state_carriers.py - the frame loop's per-frame STATE carriers (shift registers), paired by name (heuristic).

Offline. Shift registers are not LoopTunnels and have no cast-free reader yet. What IS measured:
  * outer side: the WhileLoop node (#637) on diagram 19 lists every border object's OUTER terminal in node_terms
    (main_vi_nodeterms.json) - a shift register shows as a name with a sink (initial value from 19) and/or a source
    (final value out to 19);
  * inner side: diagram 43's unresolved half-edges (frame_loop_border.json) - a wire seen on one side only inside
    the loop, with the producing/consuming node and terminal.
Pairing rule (HEURISTIC, stated in the output): group both sides by terminal NAME; inner source-only = the left
register feeding the body, inner sink-only = the right register receiving the next frame's value; outer sink =
initial value, outer source = final value. Names are the wire's source-terminal names, so a carrier whose value is
produced by a differently named terminal will pair imperfectly - the table shows the raw sides so that is visible.
Writes a section into docs/frame-loop-wire-graph.md and tools/bench/frame_loop_state.json.
  py tools/bench/stitch_state_carriers.py
"""
import json
import os
import sys
import time
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
NT = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
B = json.load(open(os.path.join(HERE, "frame_loop_border.json"), encoding="utf-8"))
SV = json.load(open(os.path.join(HERE, "main_vi_subvis.json"), encoding="utf-8"))
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
LOOP_UID = 637            # the frame loop's WhileLoop node on diagram 19 (tree: WhileLoop uids; body = diagram 43)
DOC = os.path.join(ROOT, "docs", "frame-loop-wire-graph.md")
BEGIN, END = "<!-- state-section:begin -->", "<!-- state-section:end -->"


def label(u):
    ident = SV["by_uid"].get(str(u), {}).get("name")
    return f"subVI {ident}" if ident else f"#{u}"


def main():
    loop = next(nd for nd in NT["diagrams"]["19"]["nodes"] if nd["uid"] == LOOP_UID)
    known_tunnel_outer = {b["outer_wire"] for b in B["border"]}
    outer = defaultdict(lambda: {"init": [], "final": []})
    for t in loop["terms"]:
        if t["wire"] in known_tunnel_outer:
            continue                                   # plain LoopTunnels are already named
        outer[t["name"]]["final" if t["is_source"] else "init"].append(t["wire"])
    inner = defaultdict(lambda: {"feeds_body": [], "from_body": []})
    node_terms43 = {nd["uid"]: nd for nd in NT["diagrams"]["43"]["nodes"]}
    for h in B["unresolved"]:
        # side 'source only' = the body node is the SOURCE -> the wire goes into a right register (from_body);
        # 'sink only' = the body node consumes -> fed by a left register (feeds_body)
        key = "from_body" if h["side"] == "source only" else "feeds_body"
        inner[h["name"]][key].append((h["wire"], [(u, i) for u, i, _n in h["nodes"]]))
    names = sorted(set(outer) | set(inner), key=lambda s: (s == "", s.lower()))
    rows = []
    for nm in names:
        o, i = outer.get(nm, {"init": [], "final": []}), inner.get(nm, {"feeds_body": [], "from_body": []})
        kind = ("shift register" if (i["feeds_body"] and i["from_body"]) else
                "loop terminal / tunnel side" if not (i["feeds_body"] or i["from_body"]) else "one-sided (see raw)")
        rows.append({"name": nm, "kind": kind, "outer_init_wires": o["init"], "outer_final_wires": o["final"],
                     "inner_feeds_body": i["feeds_body"], "inner_from_body": i["from_body"]})
    with open(os.path.join(HERE, "frame_loop_state.json"), "w", encoding="utf-8") as f:
        json.dump({"loop_uid": LOOP_UID, "pairing": "by terminal name (heuristic)", "rows": rows}, f, indent=1, ensure_ascii=False)

    srs = [r for r in rows if r["kind"] == "shift register"]
    L = [BEGIN, "", "## Per-frame STATE carriers (shift registers) — paired by terminal name, HEURISTIC", "",
         f"Shift registers are not `LoopTunnel`s and have no cast-free reader yet (OPEN). What is measured: the loop node "
         f"#{LOOP_UID}'s own terminals on diagram 19 (outer side: initial value in / final value out) and the body's "
         f"unresolved half-edges (inner side: which node feeds the right register, which node reads the left one). The two "
         f"sides are matched by NAME here — {len(srs)} names show both an inner producer and an inner consumer and are "
         "listed as state carriers; the raw sides are kept so a mis-pairing is visible. Names are the wire's source terminal "
         "names (a wire fed by `x,y,z array out` keeps that name), so a carrier is named after what produces it.", "",
         "| name | kind | initial value from diagram 19 (wire) | final value to 19 (wire) | inside: read by (left reg.) | inside: written by (right reg.) |",
         "|---|---|---|---|---|---|"]
    for r in rows:
        if r["kind"] == "loop terminal / tunnel side" and not (r["outer_init_wires"] or r["outer_final_wires"]):
            continue
        feeds = "; ".join(f"{label(u)} t{i}" for _w, nodes in r["inner_feeds_body"] for u, i in nodes) or ""
        frm = "; ".join(f"{label(u)} t{i}" for _w, nodes in r["inner_from_body"] for u, i in nodes) or ""
        L.append(f"| `{r['name']}` | {r['kind']} | {', '.join(map(str, r['outer_init_wires'])) or '—'} | "
                 f"{', '.join(str(w) for w in r['outer_final_wires']) or '—'} | {feeds or '—'} | {frm or '—'} |")
    L += ["", "**Reading this for the restructuring:** every row of kind *shift register* is state that crosses frame "
              "boundaries inside the frame loop today; in the rebuilt seven-loop design each must live in exactly one loop "
              "(rule: one writer). The bead-good/xyz carriers feed the kernel through the state case #5540; `LastBufferNumber` "
              "is the frame-loss detector's memory; the error and session carriers are plumbing.",
          "", f"_Generated {time.strftime('%Y-%m-%d %H:%M')} by tools/bench/stitch_state_carriers.py._", "", END]
    block = "\n".join(L)
    text = open(DOC, encoding="utf-8").read()
    if BEGIN in text and END in text:
        pre, rest = text.split(BEGIN, 1); _o, post = rest.split(END, 1); text = pre + block + post
    else:
        text = text.rstrip("\n") + "\n\n" + block + "\n"
    open(DOC, "w", encoding="utf-8").write(text)
    print(f"{len(rows)} named border objects; {len(srs)} paired as shift registers -> {DOC}")
    for r in srs:
        print("   SR", repr(r["name"]), "init", r["outer_init_wires"], "final", r["outer_final_wires"],
              "reads", [label(u) for _w, n in r["inner_feeds_body"] for u, _i in n][:3], "writes", [label(u) for _w, n in r["inner_from_body"] for u, _i in n][:3])
    return 0


if __name__ == "__main__":
    sys.exit(main())
