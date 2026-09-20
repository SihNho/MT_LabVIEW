"""read_asi_focus.py - does the frame loop pay for a serial round trip on EVERY iteration, or only when a key is held?

This is the highest-value open question left after the camera work, because it decides whether 150 Hz is reachable in
the current structure at all:

  the measured per-frame budget at 150 Hz is **6.00 ms**;
  one serial round trip (measured on the PI motor) is **2.56 ms**, i.e. 43 % of it;
  and `ASI_adjust focus-subvi.vi` sits **directly on the frame loop's body** (uid 48 on diagram 43), so it is CALLED
  every single iteration.

Called is not the same as transacts. The VI's `+Inc reference`, `-Inc reference` and `Focus inc reference` inputs are
**control references**, which is the shape of a VI that acts only when a button or key says so, and the motion audit
already found it holds a fixed `Wait (ms)` inside a case frame plus five or more property-node `Value` accesses. If the
VISA calls sit inside that case, the cost is intermittent and 150 Hz stays reachable; if they sit on the body, the loop
cannot hold 150 Hz no matter how the rest is arranged.

What this reads, per diagram of the VI: every node's terminal names, flagged for the three cost shapes - VISA traffic
(`Get Current Position.vi`, `Move Axis to Position.vi`, `VISA in/out`), a fixed `Wait` (`milliseconds to wait`), and
UI-thread property access (`Value`). Then it reports, for each, WHICH diagram it is on and what owns that diagram -
a node on diagram 0 runs unconditionally, a node inside a CaseStructure frame does not.

ORIGINALS ARE NEVER TOUCHED: the VI is copied into claudeDev first and the copy is read, per CLAUDE.md rule 1.
  py tools/bgrun.py --max-min 20 --log tools/bench/read_asi_focus.log -- py -u tools/bench/read_asi_focus.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\Madcity\ASI_adjust focus-subvi.vi"
DST = os.path.join(g.CLAUDEDEV, "READ_ASI_focus.vi")
OUT = os.path.join(HERE, "asi_focus_anatomy.json")
FLAGS = {
    "VISA / serial": ("visa", "resource name"),
    "fixed Wait": ("milliseconds to wait", "millisecond timer"),
    "UI-thread Value": ("value",),
    "position": ("position",),
    "control reference": ("reference",),
}
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    if not os.path.exists(SRC):
        print("SOURCE MISSING:", SRC, flush=True); return 3
    if os.path.exists(DST):
        os.remove(DST)                       # never load the target before overwriting it (corrupt-VI modal)
    shutil.copyfile(SRC, DST)
    time.sleep(0.3)

    owners = {}
    n_dia = g.count(DST, "Diagram")
    print(f"{os.path.basename(SRC)} -> copy in claudeDev; {n_dia} diagrams\n", flush=True)
    subs = {o["uid"] for o in g.report(DST, "SubVI")}
    structs = {}
    for cls in ("WhileLoop", "ForLoop", "CaseStructure", "Sequence", "FlatSequenceFrame", "EventStructure"):
        try:
            for o in g.report(DST, cls):
                structs[o["uid"]] = cls
        except Exception:
            pass
    for d in range(n_dia):
        try:
            owners[d] = g.report(DST, "Diagram")[d].get("owner", "?")
        except Exception:
            owners[d] = "?"

    out = {}
    for d in range(n_dia):
        try:
            nodes, _ = g.net_map(DST, diagram_index=d, max_nodes=80, max_terms=20)
        except Exception as e:
            print(f"diagram {d}: FAILED {str(e)[:100]}", flush=True); continue
        rows = []
        for _, (uid, lbl, terms) in nodes.items():
            names = [nm for _, nm, _ in terms if nm]
            low = " | ".join(names).lower()
            hits = sorted({tag for tag, keys in FLAGS.items() if any(k in low for k in keys)})
            kind = "SubVI" if uid in subs else structs.get(uid, "primitive/other")
            rows.append({"uid": uid, "kind": kind, "terms": names, "flags": hits})
        out[str(d)] = {"owner": owners.get(d, "?"), "nodes": rows}
        mark = "  <== UNCONDITIONAL (top-level diagram)" if owners.get(d) in ("", "TopLevelDiagram") else ""
        print(f"=== diagram {d}  owner {owners.get(d, '?')!r}  {len(rows)} nodes{mark}", flush=True)
        for r in rows:
            flag = ("   [" + ", ".join(r["flags"]) + "]") if r["flags"] else ""
            print(f"   {r['kind']:<16} uid {r['uid']:<6} {r['terms'][:10]}{flag}", flush=True)

    print(f"\n{'=' * 78}\nVERDICT INPUTS", flush=True)
    for d, info in out.items():
        visa = [r for r in info["nodes"] if "VISA / serial" in r["flags"]]
        wait = [r for r in info["nodes"] if "fixed Wait" in r["flags"]]
        if visa or wait:
            top = info["owner"] in ("", "TopLevelDiagram")
            print(f"   diagram {d} (owner {info['owner']!r}, {'UNCONDITIONAL' if top else 'inside a structure'}): "
                  f"{len(visa)} VISA node(s), {len(wait)} fixed Wait(s)", flush=True)
    print("\n   A VISA node on the TOP-LEVEL diagram means the frame loop transacts every iteration -> 2.56 ms of a\n"
          "   6.00 ms budget, and 150 Hz is out of reach without moving it. A VISA node only inside a CaseStructure\n"
          "   frame means the cost is intermittent and 150 Hz stays reachable.", flush=True)

    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    try:
        g.close_panel(DST)
    except Exception:
        pass
    time.sleep(0.3)
    try:
        os.remove(DST)                       # scratch targets are created and deleted in the same operation
    except OSError:
        pass
    print("\nwritten to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
