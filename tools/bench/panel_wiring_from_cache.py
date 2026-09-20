"""panel_wiring_from_cache.py - is each front-panel object actually WIRED on the diagram? Live vs leftover.

Fills the column document 2 (docs/main-vi-panel-map.md) was missing. No LabVIEW involved - this joins two
things already on disk:

    tools/bench/find_rotor_controls.log   the 114 front-panel objects, label + control/indicator (Panel.Controls[])
    tools/bench/main_vi_netmap.json       all 170 diagrams: every node's terminals and which wire each carries

A front-panel object's block-diagram terminal shows up in the sweep as a node whose single terminal is named
with the object's label. If that terminal carries a wire id, the object is LIVE; if the terminal exists with no
wire, it is ORPHANED; if no such terminal exists on any diagram, the object may be hidden, unlabelled on the
diagram, or the sweep may have missed it - reported as NOT FOUND rather than guessed either way.

Why this matters (user, 2026-09-13): the main VI is the working spec, but it carries legacy leftovers -
*"프론트 패널에 남아있지만 실제로 와이어링 안되어 있거나 사용하지 않는 부분들이 있을 수 있지"*. Presence on the panel
proves nothing about use; a wire does.

Confidence, stated: LIVE is a measurement (a wire id was read from LabVIEW). ORPHANED is a measurement too.
NOT FOUND is an absence in a complete sweep and is NOT the same as orphaned.

  py tools/bench/panel_wiring_from_cache.py
"""
import json
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "main_vi_netmap.json")
PANEL_LOG = os.path.join(HERE, "find_rotor_controls.log")
ROW = re.compile(r"^\s+(\d+) (CTL|IND) '(.*)'$")


def main():
    with open(CACHE, encoding="utf-8") as f:
        c = json.load(f)
    # every (label -> [(diagram, uid, wire)]) for single-terminal nodes, which is what a panel terminal looks like
    term_index = defaultdict(list)
    for di, rec in c["diagrams"].items():
        for uid, nd in rec.get("nodes", {}).items():
            terms = nd["terms"]
            if len(terms) == 1:
                name, wire = terms[0]
                term_index[name].append((int(di), uid, wire, rec["owner"]))

    panel = []
    with open(PANEL_LOG, encoding="utf-8", errors="replace") as f:
        in_list = False
        for line in f:
            if "full label list" in line:
                in_list = True
                continue
            if not in_list:
                continue
            m = ROW.match(line.rstrip("\n"))
            if m:
                idx, kind, lab = int(m.group(1)), m.group(2), m.group(3)
                lab = lab.encode("utf-8").decode("unicode_escape") if "\\n" in lab else lab
                panel.append((idx, kind, lab))
    print(f"{len(panel)} front-panel objects; {len(term_index)} single-terminal node names in the sweep\n")

    live, orphan, missing, multi = [], [], [], []
    for idx, kind, lab in panel:
        hits = term_index.get(lab, [])
        if not hits:
            missing.append((idx, kind, lab))
        elif len(hits) > 1:
            multi.append((idx, kind, lab, hits))
        else:
            di, uid, wire, owner = hits[0]
            (live if wire else orphan).append((idx, kind, lab, di, uid, wire, owner))

    print(f"LIVE (terminal found, WIRED)         : {len(live)}")
    print(f"ORPHANED (terminal found, NO wire)   : {len(orphan)}")
    print(f"MULTIPLE terminals with this label   : {len(multi)}")
    print(f"NOT FOUND on any diagram             : {len(missing)}\n")

    print("=" * 78 + "\nORPHANED - present on the panel, terminal exists, nothing wired to it")
    for idx, kind, lab, di, uid, wire, owner in orphan:
        print(f"   {idx:3d} {kind} {lab!r:40} diagram {di:3d} uid {uid}  ({owner})")

    print("\n" + "=" * 78 + "\nNOT FOUND - no single-terminal node carries this label (hidden? unlabelled? missed?)")
    for idx, kind, lab in missing:
        print(f"   {idx:3d} {kind} {lab!r}")

    print("\n" + "=" * 78 + "\nMULTIPLE - the same label on more than one terminal (locals? duplicates?)")
    for idx, kind, lab, hits in multi:
        w = sum(1 for _d, _u, wire, _o in hits if wire)
        print(f"   {idx:3d} {kind} {lab!r:40} {len(hits)} terminals, {w} wired: "
              f"{[(d, u, bool(wire)) for d, u, wire, _o in hits]}")

    print("\n" + "=" * 78 + "\nLIVE - wired (diagram, uid, wire)")
    for idx, kind, lab, di, uid, wire, owner in live:
        print(f"   {idx:3d} {kind} {lab!r:40} diagram {di:3d} uid {uid:<6} wire {wire}")

    out = os.path.join(HERE, "panel_wiring.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"live": live, "orphaned": orphan, "not_found": missing,
                   "multiple": [(i, k, l, h) for i, k, l, h in multi]}, f, ensure_ascii=False, indent=1)
    print(f"\nwritten: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
