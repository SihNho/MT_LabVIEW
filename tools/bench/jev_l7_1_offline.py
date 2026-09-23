r"""jev_l7_1_offline - cycle 71 (runner 70), Pre-decided 170(a): the review's OFFLINE Jev test (a)-(e)
(archive/peer/2026-09-24-c70-l7-1-jev-threshold.md section 4). Pure Python + Jev, NO LabVIEW, no model decision.
Rows are REBUILT from tools/bench/decision_l7_1_body.json / decision_l7_1_init.json (exec + row_key); the fields
write_record did not keep (sink_state, scope, borders) are filled to match the logged candidate text: every
case is same-diagram, borders 0, sink free. The bed-side term rows (#376 / #4910 / #781, incl. subVI name for the
wiki line) come from the bed terminal table graph_s3_loop15_20260924.json exactly as l7_1_predict.py builds it;
#376 is placed on body #23405 (post-move). New-SR ends are hand rows (class/term as logged, subvi None).
Each case = jev_pairs.ask_pair(line, cand, n) -> per-sample values; for multi-candidate cases (a) every candidate
is asked (the same 4 as run 1) so "top == S1-mapped pair" and the margin are measured per sample index.
PRIOR ART: jev_pairs.ask_pair / pair_state, jev_candidates.from_parts / term_row, l7_1_predict.py graph build -
all used unchanged; nothing new built.
PREDICTION (from the review, recorded not gated): (a) mean ~0.75 +-0.05; (b) ~0.58; (c) >=0.8 if question defect;
(d) drops well below 0.848 if name match inflated it; (e) low (<0.5) if Jev judges more than names.
    MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/jev_l7_1_offline.log -- py -u tools/bench/jev_l7_1_offline.py"""
import json, os, statistics as st, sys                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import jev_candidates as JC, jev_pairs as JP, vigraph as V                          # noqa: E401,E402
B = lambda f: json.load(open(os.path.join(HERE, f), encoding="utf-8"))              # noqa: E731
GR, WIKI = B("graph_s3_loop15_20260924.json"), json.load(open(os.path.join(HERE, "..", "..", "docs", "wiki", "subvi", JC.BED_KEY + ".json"), encoding="utf-8"))
G = JC.from_parts({"terminals": GR["terminals"], "graph_summary": WIKI["graph_summary"]}, GR["objs"], B("graph_loops_m4b_20260924.json")["loops"],
                  JC.node_labels_default(), WIKI["fs_tunnel_pairs"], "bed")
BODY = dict((d["id"], d) for d in B("decision_l7_1_body.json")["decisions"])
INIT = dict((d["id"], d) for d in B("decision_l7_1_init.json")["decisions"])
ILINE = B("decision_l7_1_init.json")["intent"]


def bed_term(uid, name, src=True, diagram=None):
    ks = [k for k in V.terminals(G, node=uid, is_source=src) if G["rows"][k]["term_name"] == name]
    assert len(ks) == 1, (uid, name, ks)
    t = JC.term_row(G, ks[0])
    if diagram:
        t["diagram"] = diagram
    return t


def sr(uid, cls, term, tc, diagram):
    return {"uid": uid, "term": term, "term_class": tc, "owner_class": cls, "diagram": diagram, "subvi": None}


def cand(s, d):
    return {"src": s, "dst": d, "sink_state": "free", "scope": "same", "borders": 0}


# (a) err_R: #376 outputs -> new error RIGHT SR #24083 inner (run 1's 4 candidates); S1-mapped = 'error out'
A_LINE = B("decision_l7_1_body.json")["intent"][0]
A_C = [cand(bed_term(376, p["row_key"]["src_term"], True, 23405), sr(24083, "RightShiftRegister", "", "InnerTerminal", 23405))
       for p in BODY["err_R"]["evidence"]["pairs"]]
A_OK = [p["row_key"]["src_term"] for p in BODY["err_R"]["evidence"]["pairs"]].index("error out")
ACC_OUT = sr(24187, "LeftShiftRegister", "total data array out", "OuterTerminal", 686)
ERR_OUT = sr(24133, "LeftShiftRegister", "error out", "OuterTerminal", 686)
S781, S4910 = bed_term(781, "initialized array"), bed_term(4910, "error out")
C_LINE = ("Initialize Array #781 output 'initialized array' - the value that initialises the ORIGINAL accumulator "
          "register #51 - initialises the NEW accumulator LEFT shift register #24187 of loop 1.7 (WhileLoop #23041) "
          "through its OUTER terminal. That register carries save trace.vi #376's output 'total data array out' "
          "(#376 -> right register #24150 -> left register #24187), so its terminals now read 'total data array out'.")
CASES = [("a", "err_R as-is", A_LINE, A_C, A_OK, 12),
         ("b", "acc_init CURRENT line", ILINE[1], [cand(S781, ACC_OUT)], 0, 10),
         ("c", "acc_init CORRECTED line", C_LINE, [cand(S781, ACC_OUT)], 0, 10),
         ("d", "err_init sink name blanked", ILINE[0], [cand(S4910, dict(ERR_OUT, term=""))], 0, 10),
         ("e", "NEGATIVE #4910 'error out' -> acc LEFT outer (corrected acc line)", C_LINE, [cand(S4910, ACC_OUT)], None, 10)]
print(__doc__, flush=True)
print("  FACT  corrected intent line (c)/(e), exact text: {0!r}".format(C_LINE), flush=True)
table, calls = [], 0
for cid, lab, line, cands, ok_i, n in CASES:
    print("---------- ({0}) {1}  n={2}  candidates={3}".format(cid, lab, n, len(cands)), flush=True)
    print("  INTENT {0!r}".format(line))
    vals = []
    for i, c in enumerate(cands):
        p, sp, err = JP.ask_pair(line, c, n=n)
        v = (sp or {}).get("values", []) if isinstance(sp, dict) else []
        calls += n
        vals.append(v)
        print("  CAND  [{0}] {1}  p={2} values={3} err={4}".format(i, JP.pair_state(line, c)["candidate"], p, [round(x, 3) for x in v], err), flush=True)
    t = vals[ok_i if ok_i is not None else 0]
    m = min(len(x) for x in vals)
    tops = [max(range(len(vals)), key=lambda j: vals[j][k]) for k in range(m)] if len(vals) > 1 else []
    marg = [vals[ok_i][k] - max(vals[j][k] for j in range(len(vals)) if j != ok_i) for k in range(m)] if len(vals) > 1 else []
    row = {"case": cid, "label": lab, "n": len(t), "mean": round(st.mean(t), 3) if t else None, "min": round(min(t), 3) if t else None,
           "max": round(max(t), 3) if t else None, "sd": round(st.pstdev(t), 3) if len(t) > 1 else None,
           "top_is_s1": "{0}/{1}".format(sum(1 for x in tops if x == ok_i), len(tops)) if tops else ("n/a (1 cand)" if ok_i is not None else "n/a (negative)"),
           "margin_mean": round(st.mean(marg), 3) if marg else (round(st.mean(t), 3) if t and ok_i is not None else None),
           "margin_min": round(min(marg), 3) if marg else None}
    table.append(row)
    print("  ROW   {0}".format(row), flush=True)
print("---------- TABLE (Pre-decided 170(a) measurement)")
print("  case | label | n | mean p | min | max | sd | top==S1-mapped | margin mean (min)")
for r in table:
    print("  ({case}) | {label} | {n} | {mean} | {min} | {max} | {sd} | {top_is_s1} | {margin_mean} ({margin_min})".format(**r))
print("  FACT  jev calls {0}, est ${1:.4f}".format(calls, calls * JP.COST_PER_CALL))
json.dump(table, open(os.path.join(HERE, "jev_l7_1_offline.json"), "w", encoding="utf-8"), indent=1)
ok = all(r["n"] and r["n"] >= 10 for r in table)
print("=== GATES: {0} pass / {1} fail  (every case >= 10 answered samples)".format(int(ok), int(not ok)))
sys.exit(0 if ok else 1)
