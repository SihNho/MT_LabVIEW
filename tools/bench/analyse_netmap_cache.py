"""analyse_netmap_cache.py - answer the inventory questions from the cached sweep, with uniqueness CHECKED.

THE CACHE: tools/bench/main_vi_netmap.json - all 170 diagrams of the main VI, 635 nodes, swept in 91.4 min
(2026-09-14). Read-only analysis; LabVIEW is not involved.

THE METHODOLOGICAL POINT, because the premise was challenged and the challenge was right.

Peer review rejected "a node carrying {Baseline Startpoint, Pos_degree, Ring, Numeric} IS the Autonics
SetCommand.vi call", on the grounds that connector labels are API conventions and could be duplicated by an
unrelated VI. That objection came with a condition attached:

    "...invalid unless you have independently proved that signature unique across every possible node in this VI."

With a COMPLETE inventory that condition is not an obstacle, it is an arithmetic check. So this script never
asserts identity - it COUNTS, and reports:

    exactly 1 match  -> unique within this VI. Identity is then supported by the corpus, not assumed.
    more than 1      -> ambiguous. Every match is printed and nothing is concluded.
    0                -> the terminal is not on any diagram, which is itself a finding.

What this still cannot do, stated so the output is not over-read: it cannot prove the matched node calls the
Autonics VI rather than some other VI with identical connector names. Uniqueness-in-corpus is weaker than
`SubVI.VI Path`, which remains the authoritative route and remains blocked by the class-cast problem.

  py tools/bench/analyse_netmap_cache.py
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "main_vi_netmap.json")

# Terminal names that would mark each thing we need to locate.
QUERIES = {
    "ROTOR - Autonics SetCommand.vi call": ["Baseline Startpoint", "Pos_degree"],
    "SHARED STATE - Trans position": ["Trans position"],
    "SHARED STATE - Rot position": ["Rot position"],
    "SHARED STATE - Focus position": ["Focus position"],
    "CAMERA - geometry": ["Width", "Height"],
    "STAGE - ASI move": ["Move Axis to Position", "Axis"],
    "SCHEDULE": ["CycleSchedule", "NumCol"],
}


def main():
    if not os.path.exists(CACHE):
        print("cache not found:", CACHE)
        return 1
    with open(CACHE, encoding="utf-8") as f:
        c = json.load(f)
    dg = c["diagrams"]
    print(f"cache: {len(dg)} diagrams, complete={c.get('complete')}, swept {c.get('started')}\n")

    # index: terminal name -> [(diagram, uid, all terminal names, wires)]
    index = defaultdict(list)
    n_nodes = 0
    for di, rec in dg.items():
        for uid, nd in rec.get("nodes", {}).items():
            n_nodes += 1
            names = [t for t, _w in nd["terms"]]
            for t in names:
                index[t].append((int(di), uid, names, nd["terms"]))
    print(f"{n_nodes} nodes indexed over {len(index)} distinct terminal names\n")

    for title, wanted in QUERIES.items():
        print(f"{'=' * 78}\n{title}\n   terminals sought: {wanted}")
        # a node matches only if it carries EVERY wanted terminal
        cands = {}
        for t in wanted:
            for di, uid, names, terms in index.get(t, []):
                cands.setdefault((di, uid), (names, terms))
        hits = [(k, v) for k, v in cands.items() if all(w in v[0] for w in wanted)]
        if not hits:
            print("   0 matches - not present on any diagram (a finding in itself)")
            singles = {t: len(index.get(t, [])) for t in wanted}
            print(f"   individually: {singles}")
            continue
        verdict = ("UNIQUE in this VI - identity supported by the corpus" if len(hits) == 1
                   else f"{len(hits)} matches - AMBIGUOUS, nothing concluded")
        print(f"   {len(hits)} match(es)  ->  {verdict}")
        for (di, uid), (names, terms) in sorted(hits):
            wired = [(t, w) for t, w in terms if w]
            print(f"      diagram {di:3d}  uid {uid:<6} owner={dg[str(di)]['owner']}")
            print(f"         terminals ({len(names)}): {names[:14]}")
            print(f"         WIRED     ({len(wired)}): {wired[:14]}")

    # The wiring question for the panel map: how many nodes have entirely unwired terminals?
    print(f"\n{'=' * 78}\nWIRING SUMMARY")
    tot = wired_nodes = 0
    for di, rec in dg.items():
        for uid, nd in rec.get("nodes", {}).items():
            tot += 1
            if any(w for _t, w in nd["terms"]):
                wired_nodes += 1
    print(f"   {wired_nodes}/{tot} nodes have at least one wired terminal "
          f"({tot - wired_nodes} fully unwired)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
