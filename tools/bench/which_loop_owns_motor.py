r"""which_loop_owns_motor.py - the user's question, answered from the hierarchy as far as it currently reaches.

THE QUESTION (user, 2026-09-15): "ASI보다 더 빈번하게 PI motor 및 rotor communication이 들어갈텐데 왜 이 부분은
제외하는가" - which loop encloses the main VI's PI motor / rotor call sites? The requirement calls motor READING a
frame-rate bottleneck, and my earlier answer ("motor control is already its own loop") rested on the three loop
BODIES only, never on where the 11 call sites actually sit.

Call sites, from docs/main-vi-subvi-identity.md (diagram INDEX, uid):
  MOV.vi   3 (#30804) · 36 (#26739) · 40 (#26085) · 69 (#1779) · 121 (#16184) · 125 (#31870) · 129 (#30780)
  VEL.vi   5 (#5403) · 69 (#21046) · 91 (#14196) · 129 (#17164)
  POS?/TMN?/TMX?/GOH  5, 91      Magnet2Force v3_for M270.vi  42, 74      ASI moves  10, 73, 88, 151, 167

`tools/bench/diagram_hierarchy.json` (129 of 170 diagrams resolved by verified position matching) is keyed by
diagram UID, while the call sites are known by diagram INDEX, so this joins them through report_all's `i`/`uid` and
walks each call site upward to the enclosing While loop. Where a chain runs into one of the 41 unresolved
diagrams it STOPS and says so - a partial answer that names its own gap, rather than a guess.

READ-ONLY: report_all on the main VI, nothing else. No hardware.
  py tools/bgrun.py --max-min 15 --log tools/bench/which_loop_owns_motor.log -- py -u tools/bench/which_loop_owns_motor.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
HIER = os.path.join(HERE, "diagram_hierarchy.json")
SITES = {3: "MOV.vi", 5: "VEL.vi + POS?", 36: "MOV.vi", 40: "MOV.vi", 42: "Magnet2Force", 69: "MOV.vi + VEL.vi",
         74: "Magnet2Force", 91: "VEL.vi + TMN?/TMX?/GOH", 121: "MOV.vi", 125: "MOV.vi", 129: "MOV.vi + VEL.vi",
         10: "ASI move", 73: "ASI move", 88: "ASI move", 151: "ASI move", 167: "ASI move",
         43: "(the FRAME loop body itself, for reference)", 20: "(the motor loop body)", 99: "(display/UI body)"}


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    hier = json.load(open(HIER, encoding="utf-8"))
    by_dia = {r["diagram_uid"]: r for r in hier["resolved"]}
    unresolved = {u["diagram_uid"] for u in hier["unresolved"]}

    dias = g.report_all(MAIN, "Diagram")
    idx2uid = {d["i"]: d["uid"] for d in dias}
    uid2idx = {d["uid"]: d["i"] for d in dias}

    # every structure's uid -> the diagram it LIVES on, so an owner uid can be turned into the next diagram up
    home = {}
    for cls in ("WhileLoop", "ForLoop", "CaseStructure", "Sequence", "EventStructure", "FlatSequence"):
        try:
            for o in g.report_all(MAIN, cls):
                home[o["uid"]] = cls
        except Exception as e:
            print(f"  report_all({cls}) raised: {e}", flush=True)

    print(f"hierarchy: {len(by_dia)} resolved, {len(unresolved)} unresolved, {len(dias)} diagrams\n", flush=True)
    for i in sorted(SITES):
        uid = idx2uid.get(i)
        if uid is None:
            print(f"diagram {i:4}  {SITES[i]:42} -> no such diagram index", flush=True)
            continue
        chain, cur, stopped = [], uid, ""
        for _hop in range(12):
            if cur in unresolved:
                stopped = f"UNRESOLVED diagram {cur}"
                break
            rec = by_dia.get(cur)
            if rec is None:
                stopped = f"diagram {cur} not in the hierarchy (top level?)"
                break
            owner_uid, owner_cls = rec["owner_uid"], rec["owner_class"]
            chain.append(f"{owner_cls}#{owner_uid}")
            if owner_cls == "WhileLoop":
                stopped = "REACHED A WHILE LOOP"
                break
            # step up: the owning structure lives on some diagram; find it by the structure's own uid
            nxt = None
            for d in dias:
                r = by_dia.get(d["uid"])
                if r and r["owner_uid"] == owner_uid and d["uid"] != cur:
                    continue
            # the structure's home diagram is not directly available; stop and report the gap honestly
            if nxt is None:
                stopped = stopped or "cannot step above this structure without the structure->home-diagram link"
                break
            cur = nxt
        print(f"diagram {i:4} (uid {uid:6})  {SITES[i]:42} -> {' < '.join(chain) if chain else '(none)'}"
              f"   [{stopped}]", flush=True)
    g._lv = None
    return 0


if __name__ == "__main__":
    sys.exit(main())
