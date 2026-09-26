"""card 104-3 (OFFLINE, no LabVIEW, no edit): why the finalize-time open_rows (21) and the recipe's E3 cdiff (6) differ on
the SAME simulated end. PRIOR ART: diag_c104_e3.py (recipe cdiff copied verbatim, dry ends) - re-used here; nothing new built.
F = the finalize producer exactly: V.computation_diff(SS.load_s1(P), SS.graph(step_57 state, labels={})) (stagesim.py:1132,
labels {} because diag_c103_resim.py:42 calls SS.simulate with no labels -> stagesim.py:1094).
E = stage_d1_disp.cdiff (stage_d1_disp.py:42-53): JC.from_parts(dry-end terminals, be objs, step-57 loops bound, node_labels_default(),
WIKI fs pairs). Ablations: F with node_labels_default(); E with labels {}. Per missing row: F's before/after sources with each
source node's class + default label + WAIT_LABEL hit, E's sources, and whether the row's node is in E's added/removed buckets.
Prediction: unknown (measurement). Output tools/bench/facts_c104c_e3.json."""
import copy
import json
import os
import sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T)
os.chdir(os.path.dirname(T))
import vigraph as V  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402
import jev_candidates as JC  # noqa: E402
import protocol  # noqa: E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))  # noqa: E731
BENCH = os.path.join(T, "bench")
PLAN = os.path.join(BENCH, "sim/disp/plan_disp.json")
P = J(PLAN)
A = P["actions"]
WIKI = J(JC.WIKI, P["context"]["s1_key"] + ".json")
LAB = JC.node_labels_default()
S1 = SS.load_s1(P)
st57 = J(P["finalized"]["last_step"]["path"])["state"]
pairs = lambda cd: sorted(set((V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]) for r in cd["rows"]))  # noqa: E731
want = sorted(set((int(r["node"]), r["term"]) for r in P["open_rows"]))


def egraph(x, objs, real, labels, fs):
    loops = copy.deepcopy(x.step(len(A))["state"]["loops"])
    ob = x.bind["obj"]
    for L in loops or []:
        L["right_uids"] = [ob.get(int(u), int(u)) for u in L.get("right_uids") or []]
        L["left_of"] = dict((str(ob.get(int(k), int(k))), [ob.get(int(y), int(y)) for y in (v if isinstance(v, list) else [v])])
                            for k, v in (L.get("left_of") or {}).items())
    return JC.from_parts({"terminals": real, "graph_summary": WIKI["graph_summary"]}, objs, loops, labels, fs, "diag_c104c")


def src_info(G, keys):
    out = []
    for k in keys or []:
        n = V.key_parts(k.split("@")[0])[0]
        lab = (LAB.get(n) or "")
        out.append({"key": k, "cls": S1["cls"].get(n) or G["cls"].get(n), "label": lab[:60],
                    "wait_label": any(w in lab.lower() for w in V.WAIT_LABEL), "sched_in_S1": V.is_scheduling(S1, n)})
    return out


GF = SS.graph(st57, {})
F0 = V.computation_diff(S1, GF)
F1 = V.computation_diff(S1, SS.graph(st57, LAB))
st, ff, ex = SX.dry_run(PLAN, log=lambda *_a: None)
objs, real = ex.be.st["objs"], ex.be.read()
GE = egraph(ex, objs, real, LAB, WIKI["fs_tunnel_pairs"])
E0 = V.computation_diff(S1, GE)
E1 = V.computation_diff(S1, egraph(ex, objs, real, {}, WIKI["fs_tunnel_pairs"]))
E2 = V.computation_diff(S1, egraph(ex, objs, real, {}, st57.get("fs_pairs")))
tk = lambda rows: sorted((r["term_uid"], r["wire_uid"], r["term_name"], bool(r["is_source"]), r["term_class"]) for r in rows)  # noqa: E731
R = {"dry": st, "dry_ff": (ff or "")[:200], "want_n": len(want),
     "F0_finalize_labels_empty": {"n_rows": len(F0["rows"]), "pairs": pairs(F0), "eq_want": pairs(F0) == want},
     "F1_finalize_labels_default": {"n_rows": len(F1["rows"]), "pairs": pairs(F1)},
     "E0_recipe": {"n_rows": len(E0["rows"]), "pairs": pairs(E0), "added": [(a["node"], a["class"]) for a in E0["computation_nodes_added"]],
                   "removed": [(a["node"], a["class"]) for a in E0["computation_nodes_removed"]]},
     "E1_recipe_labels_empty": {"n_rows": len(E1["rows"]), "pairs": pairs(E1), "eq_want": pairs(E1) == want},
     "E2_recipe_labels_empty_simfs": {"n_rows": len(E2["rows"]), "pairs": pairs(E2), "eq_want": pairs(E2) == want},
     "F0_added": [(a["node"], a["class"]) for a in F0["computation_nodes_added"]],
     "F0_removed": [(a["node"], a["class"]) for a in F0["computation_nodes_removed"]],
     "terminals_dry_end_eq_step57": tk(real) == tk(st57["terminals"]), "n_terms": [len(real), len(st57["terminals"])],
     "fs_pairs_eq": (st57.get("fs_pairs") or []) == (WIKI["fs_tunnel_pairs"] or []),
     "labels_n": len(LAB), "rows": []}
missing = sorted(set(want) - set(pairs(E0)))
R["missing_n"] = len(missing)
added_nodes = set(a["node"] for a in E0["computation_nodes_added"])
removed_nodes = set(a["node"] for a in E0["computation_nodes_removed"])
for fr in F0["rows"]:
    n, term = V.key_parts(fr["sink"])[0], V.key_parts(fr["sink"])[2]
    if (n, term) not in missing:
        continue
    k = fr["sink"]
    sE = sorted(V.effective_sources(GE, k)) if k in GE["rows"] else None
    sS = sorted(V.effective_sources(S1, k)) if k in S1["rows"] else None
    R["rows"].append({"node": n, "term": term, "sink": k, "plan_why": next(r["why"] for r in P["open_rows"] if (int(r["node"]), r["term"]) == (n, term)),
                      "F_before_S1": src_info(GF, fr["before"]), "F_after_sim": src_info(GF, fr["after"]),
                      "E_sources": sE, "S1_sources": sS, "E_eq_S1": sE == sS,
                      "in_E_added": n in added_nodes, "in_E_removed": n in removed_nodes,
                      "E_src_nodes_added": sorted(set(V.key_parts(x)[0] for x in (sE or [])) & added_nodes),
                      "node_label": (LAB.get(n) or "")[:60]})
R["matching6"] = [dict(pair=(V.key_parts(r["sink"])[0], V.key_parts(r["sink"])[2]), before=r["before"], after=r["after"]) for r in E0["rows"]]
json.dump(R, open(os.path.join(BENCH, "facts_c104c_e3.json"), "w", encoding="utf-8"), indent=1, default=str)
for k in ("dry", "want_n", "missing_n", "terminals_dry_end_eq_step57", "n_terms", "fs_pairs_eq", "labels_n"):
    print(k, R[k], flush=True)
for k in ("F0_finalize_labels_empty", "F1_finalize_labels_default", "E0_recipe", "E1_recipe_labels_empty", "E2_recipe_labels_empty_simfs"):
    print(k, json.dumps(R[k], default=str)[:700], flush=True)
print("F0 added/removed", R["F0_added"][:20], R["F0_removed"][:20], flush=True)
for r in R["rows"]:
    print("ROW", json.dumps(r, default=str)[:900], flush=True)
ok = len(R["rows"]) == len(missing)
print(protocol.result_line(protocol.make_result(int(ok), int(not ok), None if ok else "row dump incomplete",
                                                [{"path": "tools/bench/facts_c104c_e3.json", "md5": SS.md5_file(os.path.join(BENCH, "facts_c104c_e3.json"))}])))
