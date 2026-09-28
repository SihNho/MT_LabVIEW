r"""diag_c116d_decode - card 116-4 J2/J4, OFFLINE (no LabVIEW): decode the raw Wire.Joints[] reads of diag_c116d_j3.py.
JOINT LAYOUT, measured on the J1 scratch (tools/bench/diag_c116d_j1.log, OpLoopCast_v0 copy): each joint is
[[x, y], flags, n_neighbours, nb0, nb1, nb2, nb3] (nb = joint index or -1). flags & 0x1 = a terminal joint; flags & 0x100 =
LOOSE (set on every joint of w430 after its only sink was deleted; never set on w366, whose middle terminal joint (2 neighbours)
was deleted and re-joined). A wire is counted LOOSE when any joint carries 0x100 (one Error List item per wire object).
Prints the per-net table (net | role | before loose/joints/terminals | after loose/joints/terminals) and the sums vs the Error List
counts R1 24 (errorlist_expected_D1_l2_r1_20260928_055441.json) and scratch 22 (diag_c116b_scratch_el.log:114-116).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c116d_decode.log -- py tools/bench/diag_c116d_decode.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                               # noqa: E402
RAW = json.load(open(os.path.join(HERE, "diag_c116d_j3_raw.json"), encoding="utf-8"))          # attempt 1 (whole-graph sweep, 536 clean reads)
P2 = os.path.join(HERE, "diag_c116d_j3_raw2.json")                                              # attempt 2 (targets only, before + after)
if os.path.exists(P2):
    R2 = json.load(open(P2, encoding="utf-8"))
    for _ph in ("before", "after"):
        for _k, _v in R2[_ph].items():
            if _v and not _v["err"] and _v["echo"] == int(_k):
                RAW[_ph][_k] = _v
    RAW["coverage"] = {"attempt1": RAW["coverage"], "attempt2": R2["coverage"]}
    for _k, _v in R2["before"].items():                                                           # same bytes, same answer?
        a1 = json.load(open(os.path.join(HERE, "diag_c116d_j3_raw.json"), encoding="utf-8"))["before"].get(_k)
        if a1 and _v and not a1["err"] and a1["joints"] != _v["joints"]:
            print("REPRO MISMATCH w{0}: attempt-1 and attempt-2 before-reads differ".format(_k), flush=True)
PRED = json.load(open(os.path.join(HERE, "plan_l2r2_pred.json"), encoding="utf-8"))
NETS = json.load(open(os.path.join(HERE, "diag_c116d_nets.json"), encoding="utf-8"))
LOOSE, TERM = 0x100, 0x1


def dec(r):
    if not r:
        return None
    J = r["joints"] or []
    return {"n": len(J), "loose": sum(1 for j in J if int(j[1]) & LOOSE), "term": sum(1 for j in J if int(j[1]) & TERM),
            "pass": sum(1 for j in J if int(j[1]) & TERM and int(j[2]) >= 2), "flags": sorted(set(int(j[1]) for j in J))}


def role(w):
    tags = []
    if w in PRED["shared_sink_nets"]:
        tags.append("outer13")
    if w in NETS["pd230"]:
        tags.append("pd230")
    if w in PRED["stubs"]:
        tags.append("stub")
    return "+".join(tags) or "other"


B, A = RAW["before"], RAW["after"]
for ph, D in (("before", B), ("after", A)):
    keys = list(D)
    bad = [(i, k, D[k]["err"][:160], D[k]["echo"]) for i, k in enumerate(keys) if D[k] and (D[k]["err"] or D[k]["echo"] != int(k))]
    print("ERRREADS {0}: {1} of {2} reads bad; first 3 {3}; last {4}".format(ph, len(bad), len(keys), bad[:3], bad[-1:]), flush=True)
    for k in [k for _i, k, _e, _c in bad]:
        D[k] = None                                                                 # a bad read is no evidence
rows, G = [], {"pass": 0, "fail": 0}
for w in sorted(set(int(k) for k in B) | set(int(k) for k in A)):
    b, a = dec(B.get(str(w))), dec(A.get(str(w)))
    if (b and b["loose"]) or (a and a["loose"]) or role(w) != "other":
        rows.append((w, role(w), b, a))
fmt = lambda d: "-" if d is None else "L{0}/J{1}/T{2}/P{3} f{4}".format(d["loose"], d["n"], d["term"], d["pass"], d["flags"])   # noqa: E731
print("net | role | before loose/joints/terms/pass-through | after", flush=True)
for w, ro, b, a in rows:
    print("  w{0} | {1} | {2} | {3}".format(w, ro, fmt(b), fmt(a)), flush=True)
lb = sorted(w for w, r in B.items() if dec(r) and dec(r)["loose"])
la = sorted(w for w, r in A.items() if dec(r) and dec(r)["loose"])
print("COVERAGE {0}".format(RAW["coverage"]), flush=True)
print("SUM before: {0} wires with a loose joint (R1 Error List loose-ends 24): {1}".format(len(lb), lb), flush=True)
print("SUM after : {0} wires with a loose joint (scratch Error List loose-ends 22): {1}".format(len(la), la), flush=True)
o13 = [w for w in PRED["shared_sink_nets"]]
chg = [(w, fmt(dec(B.get(str(w)))), fmt(dec(A.get(str(w))))) for w in o13]
L = lambda D, w: (dec(D.get(str(w))) or {}).get("loose")                            # noqa: E731
print("OUTER13 newly loose: {0}".format([w for w in o13 if L(A, w) and not L(B, w)]), flush=True)
print("OUTER13 loose before: {0}".format([w for w in o13 if L(B, w)]), flush=True)
print("OUTER13 not loose after: {0}".format([w for w in o13 if A.get(str(w)) and not L(A, w)]), flush=True)
print("OUTER13 terminal joints before -> after: {0}".format([(w, (dec(B.get(str(w))) or {}).get("term"), (dec(A.get(str(w))) or {}).get("term"),
                                                               (dec(B.get(str(w))) or {}).get("pass")) for w in o13]), flush=True)
json.dump({"rows": [{"wire": w, "role": ro, "before": b, "after": a} for w, ro, b, a in rows], "loose_before": lb, "loose_after": la,
           "coverage": RAW["coverage"]}, open(os.path.join(HERE, "diag_c116d_decode.json"), "w", encoding="utf-8"), indent=1)
print("VALID before reads {0} of 1945 wires; after reads {1}".format(sum(1 for r in B.values() if r), sum(1 for r in A.values() if r)), flush=True)
print(P.result_line(P.make_result(1, 0, None, [])), flush=True)
