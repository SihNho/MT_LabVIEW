# ---
# labview: none
# hardware: none
# evidence: tools/bench/mutation_table_p5.md
# ---
r"""prep_c158_a3_1_rescore - card 158-a3-1 (PD386(d)): RE-SCORE the 158-a2-4 gate mutation table with the PD386 gates.
CALLED, not copied: tools/bench/diag_c158_a2_4_mut.py (461d4f3a) is executed from its own source via ast in two parts - everything before
its row loop (`cnt = collections.Counter()`: inputs, mutation builders, CASES, reference graphs, `score`), then the loop and the table
writer - with three names replaced in between: OUTJ / OUTM -> mutation_table_p5_rescore.json / .md (mutation_table_p5.* untouched) and
`score` -> score386 = the original score for CD / CDF / E1 / INV, and TD / D from stagekit.term_identity_pairs, PB from
stagekit.pb_check_bound (sim end re-keyed = the unmutated graph, no bindings, no plan moves: nothing is recordable as a tag row).
A gate that passes only because it RECORDED something (a source-only stub, an unwired key on a stub, a tag row) is scored RECORD.
Its trailing RESULT print and sys.exit are not executed; this script compares old vs new per row and prints its own RESULT.
PREDICTION CONTRACT: R1 the original's P1-P5 hold (M0 passes, graph md5 6716c499 before and after); R2 every INVARIANT row that blocked
before still blocks (a newly passing invariant row = RETURN, row ids printed); R3 every row whose net moved BLOCK -> RECORD/PASS is a
REPRESENTATION row; R4 mutation_table_p5.json / .md md5 unchanged (2d9fd051 / 72e54d23).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/prep_c158_a3_1_rescore.log -- py -u tools/bench/prep_c158_a3_1_rescore.py"""
import ast
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "diag_c158_a2_4_mut.py")
_tree = ast.parse(open(SRC, encoding="utf-8").read(), SRC)
_cut = next(i for i, n in enumerate(_tree.body) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "cnt" for t in n.targets))
_gaps = max(i for i, n in enumerate(_tree.body) if isinstance(n, ast.Expr) and "GAPS" in ast.dump(n))
D = {"__file__": SRC, "__name__": "diag_c158_a2_4_mut_rescore"}
exec(compile(ast.Module(body=_tree.body[:_cut], type_ignores=[]), SRC, "exec"), D)
K, V, OLDJ = D["K"], D["V"], D["OUTJ"]
old_md5 = {"json": K.md5(D["OUTJ"]), "md": K.md5(D["OUTM"])}
old = K.jload(D["OUTJ"])
D["OUTJ"], D["OUTM"] = os.path.join(K.BENCH, "mutation_table_p5_rescore.json"), os.path.join(K.BENCH, "mutation_table_p5_rescore.md")
_score = D["score"]


def score386(S):
    g, det, _net = _score(S)
    ti = K.term_identity_pairs(D["T0"], D["T0"], S["terminals"], bind=D["BIND"])
    g["TD"] = "BLOCK" if not ti["td_ok"] else ("RECORD" if ti["unwired_recorded"] else "PASS")
    det["TD"] = {"unwired": len(ti["unwired"]), "unwired_recorded": len(ti["unwired_recorded"]), "lost": len(ti["lost"]), "moved": len(ti["moved"]), "gone": len(ti["gone"])}
    g["D"] = "BLOCK" if not ti["d_ok"] else ("RECORD" if ti["stubs"]["sim_only"] or ti["stubs"]["real_only"] else "PASS")
    det["D"] = dict(ti["pairs"], stubs_sim_only=len(ti["stubs"]["sim_only"]), stubs_real_only=len(ti["stubs"]["real_only"]))
    GFm = D["build"](S, True)
    pb = K.pb_check_bound(D["S1f"], GFm, D["GF0"], D["GF0"], D["PRED"], D["OPEN"], {}, (), V)
    g["PB"] = "BLOCK" if not pb["ok"] else ("RECORD" if pb["recorded"] else "PASS")
    det["PB"] = {"eq_diff": len(pb["eq_diff"]), "blocked": len(pb["blocked"]), "recorded": len(pb["recorded"]), "first": pb["eq_diff"][:2]}
    net = "BLOCK" if "BLOCK" in g.values() else ("RECORD" if "RECORD" in g.values() else "PASS")
    return g, det, net


D["score"] = score386
exec(compile(ast.Module(body=_tree.body[_cut:_gaps + 1], type_ignores=[]), SRC, "exec"), D)
res, ok = D["res"], list(D["ok"])
print("== R1 the original's P1-P5 contract:", all(ok), flush=True)
ob = dict((r["id"], r) for r in old["rows"])
cmp, inv_lost, moved_bad, moved = [], [], [], []
for r in res["rows"]:
    o = ob.get(r["id"])
    ch = dict((k, (o["gates"][k], r["gates"][k])) for k in r["gates"] if o and o["gates"].get(k) != r["gates"][k])
    cmp.append({"id": r["id"], "class": r["class"], "old_net": o and o["net"], "new_net": r["net"], "changed_gates": ch})
    if r["class"] == "invariant" and o and o["net"] == "BLOCK" and r["net"] != "BLOCK":
        inv_lost.append(r["id"])
    if o and o["net"] != r["net"]:
        moved.append(r["id"])
        if r["class"] != "representation" and r["net"] != "BLOCK":
            moved_bad.append(r["id"])
    print("CMP {0:6s} {1:15s} {2} -> {3} {4}".format(r["id"], r["class"], o and o["net"], r["net"], ch), flush=True)
res["rescore"] = {"card": "158-a3-1", "decided": "PD386(d)", "old_table": {"json": "tools/bench/mutation_table_p5.json", "md5": old_md5["json"]},
                  "gates_new": {"TD": "stagekit.term_identity_pairs td_ok (stub-aware)", "D": "stagekit.term_identity_pairs d_ok (pair-keyed)",
                                "PB": "stagekit.pb_check_bound (real == sim re-keyed; tag rows recordable)"},
                  "rows": cmp, "invariant_blocked_before_not_now": inv_lost, "net_moved": moved, "net_moved_non_representation": moved_bad}
with open(D["OUTJ"], "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, default=str)
with open(D["OUTM"], encoding="utf-8") as f:
    md = f.read().splitlines()
md = [("card: 158-a3-1 (re-score of 158-a2-4)" if x == "card: 158-a2-4" else x) for x in md]
md.insert(6, "RE-SCORE (card 158-a3-1, PD386(d)) by prep_c158_a3_1_rescore.py: TD/D = stagekit.term_identity_pairs, PB = stagekit.pb_check_bound; "
             "RECORD = passes only by recording. Original table: mutation_table_p5.md (unchanged).")
md += ["", "Re-score vs 158-a2-4: invariant rows that blocked and no longer block: " + (", ".join(inv_lost) or "none")
       + "; rows whose net moved: " + (", ".join(moved) or "none") + "; of those not representation: " + (", ".join(moved_bad) or "none") + "."]
with open(D["OUTM"], "w", encoding="utf-8") as f:
    f.write("\n".join(md) + "\n")
g4 = K.md5(OLDJ) == old_md5["json"] == "2d9fd0513a5490b91ea191872708275a" and K.md5(D["OUTM"].replace("_rescore", "")) == "72e54d232a7b087372f1a37d0f87ebf1"
gates = [("R1 original contract P1-P5", all(ok)), ("R2 no invariant row stopped blocking {0}".format(inv_lost), not inv_lost),
         ("R3 every moved net is a representation row {0}".format(moved_bad), not moved_bad), ("R4 mutation_table_p5.* unchanged", g4)]
for lab, v in gates:
    print("GATE {0} | {1}".format("PASS" if v else "FAIL", lab), flush=True)
nf = sum(1 for _l, v in gates if not v)
print(D["protocol"].result_line({"status": "PASS" if not nf else "FAIL", "gates": {"pass": len(gates) - nf, "fail": nf},
                                 "first_fail": next((lab for lab, v in gates if not v), None),
                                 "artefacts": [{"path": "tools/bench/mutation_table_p5_rescore.json", "md5": K.md5(D["OUTJ"])},
                                               {"path": "tools/bench/mutation_table_p5_rescore.md", "md5": K.md5(D["OUTM"])}]}), flush=True)
sys.exit(1 if nf else 0)
