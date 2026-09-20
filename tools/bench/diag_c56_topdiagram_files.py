"""diag_c56_topdiagram_files.py - J1, cycle 56 material #4: WHICH diagram is the main VI's TOP-LEVEL diagram?

FILES ONLY. This script opens NO .vi, imports NO gscript, makes NO COM call and touches no hardware. It reads
three JSON caches that already exist on disk and prints what they do and do not say. It exists because dispatch 3
read `node_info(max_n=40) == []` and `diagram_tree_main.json` diagram "0" (owner '') as holding no real node, and
those two readings have two opposite interpretations:
  H1 the main VI's top-level diagram really holds zero addressable nodes;
  H2 the `VI -> Block Diagram -> Nodes[]` ladder HEAD returns an invalid/unloaded reference, so the whole
     Nodes[]-addressing family is broken at its first rung rather than "inapplicable to this VI".

PRIOR ART CHECKED BEFORE WRITING THIS (CLAUDE.md: check what already exists):
  - `tools/bench/diagram_tree_main.py` already built the diagram census -> `diagram_tree_main.json`. NOT rerun.
  - `tools/bench/sweep_nodeterms_main.py` already built the per-node terminal census -> `main_vi_nodeterms.json`.
    NOT rerun.
  - `tools/bench/reverse_census_walk.py` (cycle 55) already reconciled the two caches. This script does NOT redo
    that reconciliation; it asks a different question (which diagram is top level, and who owns #686 / #639).
  - `grep "^def " tools/gscript.py`: report / report_all / net_map / node_info / node_terms_uid already exist; no
    new verb is written here and no op VI is built.

PREDICTION CONTRACT (machine-checkable; every line is PASS/FAIL against the files, never against LabVIEW):
  J1  exactly ONE entry of diagram_tree_main.json["diagrams"] has owner '' or absent            -> report count
  J2  that entry's real-node count (uids minus the known junk uid 22963) is 0                   -> report
  J3  diagram_tree_main.json stores NO diagram UIDs at all (only owner CLASS strings)           -> expect True
  J4  diagram_tree_main.py contains NO code that identifies a top-level diagram                 -> grep, expect 0 hits
  J5  the owner-class census contains 'FlatSequenceFrame'                                       -> report the count
  J6  the per-object CLASS of each diagram is discarded by diagram_tree_main.py                  -> grep, expect True
  J7  Traverse index 19 (= Diagram #686) and 46 (= Diagram #639) node counts, from both caches  -> report
  J8  nodeterms' own diagram-"0" row holds 0 nodes                                              -> report
JUNK = 22963 is net_map's own Invoke node (measured, tools/bench/reverse_census_walk.log).

  py tools/bgrun.py --material --max-min 4 --log tools/bench/diag_c56_topdiagram_files.log -- py -u tools/bench/diag_c56_topdiagram_files.py
"""
import collections
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
JUNK = 22963
OUT = os.path.join(HERE, "diag_c56_topdiagram_files.json")
res = {"gates": [], "facts": {}}


def gate(label, ok, detail=""):
    res["gates"].append({"label": label, "ok": bool(ok), "detail": detail})
    print(f"  {'PASS' if ok else 'FAIL'}  {label}  {detail}", flush=True)


def fact(label, value):
    res["facts"][label] = value
    print(f"  FACT  {label}: {value}", flush=True)


def main():
    T = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
    print("=== diagram_tree_main.json", flush=True)
    fact("top-level JSON keys", list(T.keys()))
    fact("vi", T["vi"])
    fact("n owners / n diagram rows", (len(T["owners"]), len(T["diagrams"])))
    cen = collections.Counter(T["owners"])
    fact("owner-class census", dict(cen))
    fact("structures (class -> count)", {k: len(v) for k, v in T["structures"].items()})
    gate("J5 'FlatSequenceFrame' appears in the owner-class census",
         "FlatSequenceFrame" in cen, f"count={cen.get('FlatSequenceFrame')}")

    # ---- (a) every diagram entry whose owner is the VI itself / empty / absent -------------------
    print("\n=== (a) diagram rows with owner empty or absent", flush=True)
    empties = []
    for k in sorted(T["diagrams"], key=int):
        d = T["diagrams"][k]
        ow = d.get("owner", "<absent>")
        if ow in ("", None, "<absent>"):
            u = d.get("uids")
            real = [x for x in (u or []) if x != JUNK]
            empties.append({"index": int(k), "owner": ow, "n_uids": (len(u) if u is not None else None),
                            "uids": u, "n_real": len(real), "real_uids": real[:8]})
            print(f"    idx {k}: owner={ow!r} n_uids={len(u) if u is not None else None} uids={u} "
                  f"real(minus junk {JUNK})={real}", flush=True)
    fact("(a) rows with empty/absent owner", empties)
    gate("J1 exactly one diagram row has an empty/absent owner", len(empties) == 1, f"n={len(empties)}")
    gate("J2 that row's real-node count (junk 22963 removed) is 0",
         bool(empties) and empties[0]["n_real"] == 0,
         f"n_real={empties[0]['n_real'] if empties else 'n/a'}")

    # any VI-class owner string at all?
    vi_like = sorted({o for o in T["owners"] if o and re.search(r"VirtualInstrument|TopLevel|VI$", o)})
    fact("owner strings that look like the VI itself", vi_like)

    # ---- (e) how do the sweep scripts DECIDE what the top-level diagram is? ----------------------
    print("\n=== (e) what the sweep scripts decide", flush=True)
    src_tree = open(os.path.join(HERE, "diagram_tree_main.py"), encoding="utf-8").read()
    src_sweep = open(os.path.join(HERE, "sweep_nodeterms_main.py"), encoding="utf-8").read()
    has_uid_store = bool(re.search(r'st\["diagrams"\]\[str\(k\)\]\s*=\s*\{[^}]*"uid"', src_tree))
    gate("J3 diagram_tree_main.py stores NO per-diagram UID", not has_uid_store,
         "stored fields are owner + uids(of the NODES on it) only")
    top_hits = [ln for ln in src_tree.splitlines()
                if re.search(r"top.?level|TopLvlDiag|TopLevelDiagram", ln, re.I)]
    gate("J4 diagram_tree_main.py contains no top-level identification", not top_hits,
         f"hits={top_hits}")
    cls_kept = bool(re.search(r'st\["owners"\]\s*=\s*\[d\["class"\]', src_tree))
    gate("J6 diagram_tree_main.py discards each Diagram object's own CLASS",
         not cls_kept, 'it keeps only d["owner"] (diagram_tree_main.py:52)')
    fact("(e) the line that builds the index", [ln.strip() for ln in src_tree.splitlines()
                                                if 'st["owners"]' in ln or "g.report(WORK" in ln])
    fact("(e) the line that reads each diagram's nodes",
         [ln.strip() for ln in src_tree.splitlines() if "g.net_map(WORK" in ln])
    fact("(e) sweep_nodeterms_main.py's diagram source",
         [ln.strip() for ln in src_sweep.splitlines() if "TREE[" in ln and "diagrams" in ln][:4])

    # ---- (c)/(d) the two diagrams of interest ---------------------------------------------------
    print("\n=== (b)(c)(d) Traverse index 19 (= Diagram #686) and 46 (= Diagram #639)", flush=True)
    for k, claim in (("19", "Diagram #686"), ("46", "Diagram #639")):
        d = T["diagrams"].get(k, {})
        u = d.get("uids") or []
        real = [x for x in u if x != JUNK]
        fact(f"tree idx {k} ({claim})", {"owner": d.get("owner"), "n_uids": len(u), "n_real": len(real),
                                         "first_real": real[:10]})

    N = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
    print("\n=== main_vi_nodeterms.json", flush=True)
    fact("nodeterms stats", {k: v for k, v in N["stats"].items() if not isinstance(v, list)})
    for k in ("0", "19", "46"):
        d = N["diagrams"].get(k)
        if d is None:
            fact(f"nodeterms idx {k}", "ABSENT"); continue
        fact(f"nodeterms idx {k}", {"owner": d["owner"], "n_nodes": len(d["nodes"]),
                                    "uids": [n["uid"] for n in d["nodes"]][:12]})
    gate("J8 nodeterms row '0' holds 0 nodes",
         len((N["diagrams"].get("0") or {"nodes": [1]})["nodes"]) == 0,
         f"n={len((N['diagrams'].get('0') or {'nodes': []})['nodes'])}")
    for cls in ("Local", "LocalVariable", "Global", "Property", "Invoke"):
        if f"class_{cls}" in N["stats"]:
            fact(f"nodeterms class_{cls}", N["stats"][f"class_{cls}"])

    M = json.load(open(os.path.join(HERE, "main_vi_netmap.json"), encoding="utf-8"))
    print("\n=== main_vi_netmap.json", flush=True)
    fact("netmap keys", list(M.keys()))
    for k in ("0", "19", "46"):
        dd = M["diagrams"].get(k) or {}
        nodes = dd.get("nodes", {})
        fact(f"netmap idx {k}", {"keys": list(dd.keys()), "n_nodes": len(nodes),
                                 "node_uids": list(nodes.keys())[:12]})

    npass = sum(1 for g_ in res["gates"] if g_["ok"])
    print(f"\nGATES {npass} pass / {len(res['gates']) - npass} fail", flush=True)
    json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
    print("wrote", OUT, flush=True)
    return 0 if npass == len(res["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
