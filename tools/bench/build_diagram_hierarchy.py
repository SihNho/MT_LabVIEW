r"""build_diagram_hierarchy.py - the main VI's DIAGRAM HIERARCHY, which the user asked for by name.

("문서화가 충분히 되지 않은 것 같은데, 다이어그램 계층 구조 확실히 준비하도록." - 2026-09-15)

WHAT IS MISSING TODAY. `tools/bench/diagram_tree_main.json` has, for each of the 170 diagrams, its owning structure
CLASS and the node uids on it - but no PARENT LINK. So nobody can say what is nested inside what, and in particular
nobody can say which loop encloses the 11 PI motor / rotor call sites (`MOV.vi` x7, `VEL.vi` x4, plus POS?/TMN?/
TMX?/GOH and `Magnet2Force` x2). The requirement calls motor READING a frame-rate bottleneck, so that is not a
detail. My earlier answer - "the 6 subVIs on diagram 43" - counted only the frame loop's BODY, not its 10 nested
Case structures, 4 For loops and 1 Event structure.

METHOD, and why it needs no new op. `gscript.loop_diagram` already rests on a measurement from 2026-08-28: a For
loop's body Diagram reports its position at exactly `loop_pos + (10, 22)`, with the runner-up diagram 21x farther
away. This generalises the same idea to every structure class and, crucially, VERIFIES it instead of assuming it:
each diagram is matched to the nearest structure of its own owner class, and a match is accepted only when the
runner-up is at least MARGIN times farther. Anything ambiguous is reported as UNRESOLVED rather than guessed -
that is the whole difference from the three failed attempts at step 0a, which all guessed an index.

If too many diagrams come back unresolved, the fallback is the reader `OpOwnerChain_v0` (a node's `Generic.Owner`
is its frame Diagram; that Diagram's `Owner` is the structure - measured, docs/NAMES.md:823). Build that only if
this measurement says it is needed.

READ-ONLY. The main VI is opened by reference and traversed; nothing is created, modified or saved. No hardware.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_diagram_hierarchy.log -- py -u tools/bench/build_diagram_hierarchy.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
OUT = os.path.join(HERE, "diagram_hierarchy.json")
STRUCT_CLASSES = ["WhileLoop", "ForLoop", "CaseStructure", "Sequence", "EventStructure"]
MARGIN = 3.0          # the runner-up must be this many times farther for a match to be accepted


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    if not os.path.exists(MAIN):
        print("STOP: main VI not found", flush=True)
        return 3

    dias = g.report_all(MAIN, "Diagram")
    print(f"diagrams: {len(dias)}", flush=True)
    structs = {}
    for cls in STRUCT_CLASSES:
        objs = g.report_all(MAIN, cls)
        structs[cls] = objs
        print(f"  {cls:16} {len(objs)}", flush=True)

    # Run 2 resolved 100/170 and left 70 owned by `FlatSequenceFrame`, a class that was simply missing from the
    # list above - flat sequences were never catalogued (`diagram_tree_main.json`'s `structures` has no entry for
    # them either). Rather than GUESS the structure's class name, derive candidates from the owner string and ask
    # the machine which one exists. Guessing a name is what cost step 0a three runs.
    owner_classes = {d.get("owner") or "" for d in dias}
    for oc in sorted(owner_classes):
        if not oc or oc in structs:
            continue
        cands = [oc, oc[:-5] if oc.endswith("Frame") else oc + "Frame",
                 oc.replace("Frame", "Structure"), oc.replace("Frame", "")]
        for cand in dict.fromkeys(c for c in cands if c):
            try:
                objs = g.report_all(MAIN, cand)
            except Exception as e:
                print(f"  probe class {cand!r}: {e}", flush=True)
                continue
            if objs:
                structs[oc] = objs          # keyed by the OWNER string, which is what the match looks up
                print(f"  owner {oc!r} -> class {cand!r}: {len(objs)}", flush=True)
                break
        else:
            print(f"  owner {oc!r}: no class found among {cands}", flush=True)

    # Which diagram does each STRUCTURE live on? A structure is a node, and report_all gives its position in its
    # own parent diagram's space - so this is resolved in the second pass, after diagram->structure is known.
    resolved, unresolved = {}, []
    for d in dias:
        owner_cls = d.get("owner") or ""
        cands = structs.get(owner_cls, [])
        if not cands:
            unresolved.append((d["uid"], owner_cls, "no structure of that class"))
            continue
        # key= on the distance only: two structures at the same distance would otherwise make Python compare the
        # dicts themselves and raise. (`gscript.loop_diagram` has the same shape and has simply never hit a tie.)
        scored = sorted(((abs(c["pos"][0] - d["pos"][0]) + abs(c["pos"][1] - d["pos"][1]), c) for c in cands),
                        key=lambda x: x[0])
        best_dist, best = scored[0]
        if len(scored) > 1 and scored[1][0] < max(best_dist, 1) * MARGIN:
            unresolved.append((d["uid"], owner_cls,
                               f"ambiguous: nearest {best_dist}, runner-up {scored[1][0]}"))
            continue
        resolved[d["uid"]] = {"diagram_uid": d["uid"], "diagram_index": d["i"], "owner_class": owner_cls,
                              "owner_uid": best["uid"], "distance": best_dist}

    print(f"\nresolved {len(resolved)} / {len(dias)}   unresolved {len(unresolved)}", flush=True)
    for u, c, why in unresolved[:25]:
        print(f"  UNRESOLVED diagram {u} (owner {c}): {why}", flush=True)

    json.dump({"vi": MAIN, "resolved": list(resolved.values()),
               "unresolved": [{"diagram_uid": u, "owner_class": c, "why": w} for u, c, w in unresolved]},
              open(OUT, "w", encoding="utf-8"), indent=1)
    print(f"\nwritten to {OUT}", flush=True)
    print("NOTE: this is diagram -> owning STRUCTURE. Turning that into diagram -> PARENT DIAGRAM needs the "
          "structure's own home diagram, which is the next pass once these matches are trusted.", flush=True)
    g._lv = None
    return 0 if len(unresolved) * 4 <= len(dias) else 1      # >25% unresolved = the method is not good enough


if __name__ == "__main__":
    sys.exit(main())
