"""diagram_tree_main.py - Step 0, phase 2: which While loop holds what, on the main VI working copy.

Runs only after tools/bench/diagram_tree_validate.py passes, because the tree reconstruction leans on Traverse ordering
and that assumption has to be proven on VIs whose structure we built ourselves first.

The question this answers, from docs/MAIN_VI_MAP.md §4.1, still open since 2026-08-30: the main VI has 3 While loops and
97 SubVI nodes, and we do not know which loop contains which. Everything in docs/t0-instrumentation-plan.md depends on it,
because measuring a VI that runs once per clamp cycle as if it ran every frame is wasted work. The anchor is known: the
tracking kernel is called at exactly ONE node, uid 5058.

Method: for every Diagram index, `net_map` lists the node UIDs on that diagram (its first per-node field is the UID,
confirmed in the motion audit), and `report("Diagram")` gives that diagram's owning structure CLASS. Together they give
diagram -> {owner class, node uids}. The diagram holding uid 5058 is then the tracking call's home, and the loop that
encloses it is the frame loop.

CRASH TOLERANCE: the main VI has about 170 diagrams and 1898 wires, and LabVIEW died once already during this session's
inspections. Every diagram's result is appended to the JSON checkpoint as soon as it is read, and a rerun skips whatever
is already recorded, so an interrupted walk resumes instead of restarting.

READ-ONLY: the working copy is opened and traversed, never modified, never saved, never run. No hardware is touched.
  py tools/bgrun.py --max-min 55 --log tools/bench/diagram_tree_main.log -- py -u tools/bench/diagram_tree_main.py
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

WORK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
OUT = os.path.join(HERE, "diagram_tree_main.json")
KERNEL_UID = 5058                     # the single tracking call site, MAIN_VI_MAP §3b
g._run.__defaults__ = (6.0, 60.0)


def load():
    if os.path.exists(OUT):
        try:
            return json.load(open(OUT, encoding="utf-8"))
        except Exception:
            pass
    return {"vi": WORK, "diagrams": {}, "owners": [], "subvis": {}, "structures": {}}


def main():
    g._lv = None
    if not os.path.exists(WORK):
        print("STOP: working copy not found:", WORK, flush=True); return 3
    st = load()
    print("target:", WORK, flush=True)
    print("resuming with", len(st["diagrams"]), "diagram(s) already recorded", flush=True)

    if not st["owners"]:
        dias = g.report(WORK, "Diagram")
        st["owners"] = [d["owner"] for d in dias]
        st["subvis"] = {str(o["uid"]): o["pos"] for o in g.report(WORK, "SubVI")}
        for cls in ("WhileLoop", "ForLoop", "CaseStructure", "Sequence", "EventStructure"):
            st["structures"][cls] = [o["uid"] for o in g.report(WORK, cls)]
        json.dump(st, open(OUT, "w", encoding="utf-8"), indent=1)
    n = len(st["owners"])
    print(f"diagrams: {n} | owners: {dict((o, st['owners'].count(o)) for o in set(st['owners']))}", flush=True)
    print(f"SubVI nodes: {len(st['subvis'])} | structures: " +
          ", ".join(f"{k} {len(v)}" for k, v in st["structures"].items()), flush=True)

    t0 = time.time()
    for k in range(n):
        if str(k) in st["diagrams"]:
            continue
        try:
            nodes, _ = g.net_map(WORK, diagram_index=k, max_nodes=120, max_terms=16)
            uids = [uid for uid, _lbl, _t in nodes.values()]
        except Exception as e:
            print(f"   diagram {k:3}: FAILED {str(e)[:110]}", flush=True)
            st["diagrams"][str(k)] = {"owner": st["owners"][k], "uids": None, "error": str(e)[:200]}
            json.dump(st, open(OUT, "w", encoding="utf-8"), indent=1)
            if "RPC" in str(e) or "server" in str(e).lower():
                print("   LabVIEW appears to be gone - stopping so a rerun can resume", flush=True); return 4
            continue
        st["diagrams"][str(k)] = {"owner": st["owners"][k], "uids": uids}
        json.dump(st, open(OUT, "w", encoding="utf-8"), indent=1)
        mark = "   <<< TRACKING CALL SITE" if KERNEL_UID in uids else ""
        print(f"   diagram {k:3} owner={st['owners'][k]:<18} {len(uids):3} node(s){mark}", flush=True)
        if time.time() - t0 > 3300:
            print("   time budget reached; rerun to resume", flush=True); return 1

    # --- report -------------------------------------------------------------------------------
    print("\n===== RESULT", flush=True)
    home = [k for k, v in st["diagrams"].items() if v.get("uids") and KERNEL_UID in v["uids"]]
    print("tracking call site uid %d is on diagram(s): %s" % (KERNEL_UID, home), flush=True)
    for k in home:
        print("   that diagram is owned by:", st["diagrams"][k]["owner"], flush=True)
    whiles = [k for k, v in st["diagrams"].items() if v.get("owner") == "WhileLoop"]
    print("WhileLoop-owned diagrams:", whiles, flush=True)
    subs = set(int(u) for u in st["subvis"])
    for k in whiles:
        u = st["diagrams"][k].get("uids") or []
        print(f"   While diagram {k}: {len(u)} nodes, of which {len([x for x in u if x in subs])} are subVI calls", flush=True)
    empty = [k for k, v in st["diagrams"].items() if v.get("uids") == []]
    failed = [k for k, v in st["diagrams"].items() if v.get("uids") is None]
    print(f"empty diagrams: {len(empty)} | failed: {failed}", flush=True)
    print("checkpoint written to", OUT, flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
