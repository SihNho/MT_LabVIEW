r"""prep_c140_1_sessions - card 140-1 (PD319(c)), OFFLINE, no LabVIEW, no tool edit, no plan rewritten. Measures, never chooses.
Found before writing: the X10 model is stage_prerun.x10_model_peak (stage_prerun.py:2005-2026, coefficients memory_model.json); the
binder is stagexec bind_new / _bind_create (stagexec.py:891-967, 2329-2368); the checkpoint rule stagexec.py:2031-2037; the plan's
units are plan_ring_p4_v14_meta.json actions[].unit. No session/merge tool exists (meta 'sessions' = the v14 maker's per-unit cut).
PREDICTION: G1 step 1 X10 == 750.7 within 0.5; G2 step 1 R == 29 = {0, 39} | 28 BIND; G3 every 'new:' / 'of' use follows its creator
in v14 op order; G4 tables A and B: every session <= 675 and dependency-closed; G5 B total <= A total.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/prep_c140_1_sessions.log -- py -u tools/bench/prep_c140_1_sessions.py"""
import collections, json, os, sys                                                   # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(ROOT, "tools"))  # noqa: E702
import stagexec as SX, stage_prerun as SP, vigraph as V                            # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))             # noqa: E731
M = J("tools/bench/memory_model.json"); v = lambda k: float(M[k]["value"])         # noqa: E702,E731
P, META, S1 = J("tools/bench/plan_ring_p4_v14.json"), J("tools/bench/plan_ring_p4_v14_meta.json"), J("tools/bench/plan_ring_p4s1.json")
LIM, START, GROW = 675.0, 606.1, v("load_growth_mb_per_op")
G = []
def gate(lbl, ok, det=""):
    G.append((lbl, bool(ok))); print("GATE {0} {1} {2}".format("PASS" if ok else "FAIL", lbl, json.dumps(det, default=str)[:900]), flush=True)
k1 = [o["kind"] for o in SX.compile_plan(S1)]; B1 = set(k for k, x in enumerate(k1, 1) if x in SX.BIND_KINDS)
x1 = SP.x10_model_peak(k1, sorted({0, len(k1)} | B1), model=M, start_mb=START)
print("FACT formula peak = start + R*{0} + N*({1}+{2}) + {3}; fail_above_mb {4}; start {5}".format(v("read_mb"), v("edit_mb"), v("other_mb"), v("final_read_mb"), v("fail_above_mb"), START))
gate("G1 step 1 X10 peak reproduced", abs(x1["peak_mb"] - 750.7) <= 0.5, x1)
gate("G2 step 1 R 29 = {0, 39} | BIND", x1["R"] == 29 and len(B1) == 28 and 39 in B1, {"bind": sorted(B1), "N": x1["N"]})
A = P["actions"]; OPS = SX.compile_plan(P); NOP = len(OPS); act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
UNIT = dict((m["id"], m.get("unit")) for m in META["actions"]); STEPF = dict((s["n"], s["path"]) for s in P["finalized"]["step_files"])
st = {}                                                                             # step n -> (sym dict, {node: class} of negative nodes)
for n in sorted(STEPF):
    s = J(STEPF[n])["state"]
    st[n] = (dict(s.get("sym") or {}), dict((V.node_of(r), V.node_class(r)) for r in s["terminals"] if V.node_of(r) < 0))
CRE, NEWCLS = {}, {}                                                                # sym -> creating op; op -> created row classes
for k, o in enumerate(OPS, 1):
    sp, sn = st[o["acts"][0] - 1], st[o["acts"][-1]]
    for y in set(sn[0]) - set(sp[0]):
        CRE.setdefault(y, k)
    body = set(int(u) for y, u in sn[0].items() if "." in y and isinstance(u, int))   # bodies/frames: bound by the op return
    NEWCLS[k] = sorted(c for u, c in sn[1].items() if u not in sp[1] and u not in body)
def refs(x):
    if isinstance(x, str) and x.startswith("new:"): yield x
    elif isinstance(x, dict):
        for y in x.values(): yield from refs(y)
    elif isinstance(x, list):
        for y in x: yield from refs(y)
def creator(r):
    for c in (r, r.split(".")[0], r.split(".")[0][:-1]):
        if c in CRE: return CRE[c]
    return None
USE, bad = collections.defaultdict(set), []                                         # creator op -> using ops
for n, a in enumerate(A, 1):
    k = act2op[n]; cs = [creator(r) for r in refs(dict((x, y) for x, y in a.items() if x not in ("as", "why")))]
    if a.get("of"): cs.append(act2op[next(i for i, b in enumerate(A, 1) if b["id"] == a["of"])])
    for c in cs:
        (bad.append((a["id"], c)) if c is None or c > k else USE[c].add(k)) if c != k else None
gate("G3 every 'new:'/'of' use follows its creator in v14 op order", not bad, bad[:8])
BIND = [k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS]
def ivl(k, hi): return (k, min([u - 1 for u in USE.get(k, ()) if u > k] + [hi]))
def stab(iv):                                                                       # minimal interval point cover (greedy by right end)
    pts = []
    for lo, hi in sorted(iv, key=lambda t: t[1]):
        if not pts or pts[-1] < lo: pts.append(hi)
    return pts
def amb(grp):                                                                       # current binder: one new object per class per read
    c = collections.Counter(x for k in grp for x in set(NEWCLS[k])); within = set(x for k in grp for x, n in collections.Counter(NEWCLS[k]).items() if n > 1)
    return sorted(x for x, n in c.items() if n > 1 and not (x in SX.MULTI_BORDER_CLS and x in within and len([k for k in grp if x in NEWCLS[k]]) == 1))
def merged(a, b):                                                                   # reads inside (a, b]: merged, ambiguous groups split back
    bs = [k for k in BIND if a < k <= b]; pts = sorted(set(stab([ivl(k, b) for k in bs])) | {b}); out, prev = set(), a
    for p in pts:
        grp = [k for k in bs if prev < k <= p]
        out |= set(grp) if amb(grp) else {p}; prev = p
    return out
def peak(a, b, mode, grow):                                                         # ops a+1..b in one Executor run (from a fresh load)
    reads = {a, b} | (set(k for k in BIND if a < k <= b) if mode == "A" else merged(a, b))
    s0 = START + grow * a
    return round(s0 + len(reads) * v("read_mb") + (b - a) * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1), len(reads), s0
def table(mode, grow, lim=LIM):
    out, a = [], 0
    while a < NOP:
        b = a + 1
        while b < NOP and peak(a, b + 1, mode, grow)[0] <= lim: b += 1
        pk, R_, s0 = peak(a, b, mode, grow); ids = [A[n - 1]["id"] for k in range(a + 1, b + 1) for n in OPS[k - 1]["acts"]]
        out.append({"session": len(out) + 1, "ops": [a + 1, b], "first": ids[0], "last": ids[-1], "actions": len(ids), "N": b - a, "R": R_,
                    "start_mb": round(s0, 1), "peak_mb": pk, "ok": pk <= lim, "kinds": dict(collections.Counter(OPS[k - 1]["kind"] for k in range(a + 1, b + 1))),
                    "cut_forced_by": A[OPS[b]["acts"][0] - 1]["id"] if b < NOP else None,
                    "unit_split": (UNIT.get(ids[-1]) if b < NOP and UNIT.get(ids[-1]) == UNIT.get(A[OPS[b]["acts"][0] - 1]["id"]) else None),
                    "uses_cut": sorted(set(A[OPS[u - 1]["acts"][0] - 1]["id"] for c in range(a + 1, b + 1) for u in USE.get(c, ()) if u > b))})
        a = b
    return out
TA, TB = table("A", 0.0), table("B", 0.0)
stall = lambda T: {"sessions_ok": len([r for r in T if r["ok"]]), "first_failing_session_ops": next((r["ops"] for r in T if not r["ok"]), None)}   # noqa: E731
for nm, T in (("A", TA), ("B", TB)):
    for r in T:
        print("{0} s{1:02d} ops {2} {3}..{4} acts {5} N {6} R {7} peak {8} kinds {9} cut_by {10} unit_split {11} cross_uses {12}".format(
            nm, r["session"], r["ops"], r["first"], r["last"], r["actions"], r["N"], r["R"], r["peak_mb"], r["kinds"], r["cut_forced_by"], r["unit_split"], len(r["uses_cut"])))
gate("G4 tables A and B: every session <= 675; every use follows its creator (G3) so prefixes are dependency-closed", all(r["ok"] for r in TA + TB), [len(TA), len(TB)])
gate("G5 B total <= A total", len(TB) <= len(TA), [len(TA), len(TB)])
p1 =sorted(set(stab([ivl(k, 39) for k in BIND if k <= 39])) | {39})
pw = sorted(set(stab([ivl(k, NOP) for k in BIND])) | {NOP}); grp = lambda pts, hi: [[k for k in BIND if (pts[i - 1] if i else 0) < k <= p] for i, p in enumerate(pts)]   # noqa: E731
S1BIND = [{"op": k, "id": A[OPS[k - 1]["acts"][0] - 1]["id"], "kind": OPS[k - 1]["kind"], "classes": NEWCLS[k], "interval": list(ivl(k, 39)),
           "first_use": (A[OPS[min(USE[k]) - 1]["acts"][0] - 1]["id"] if USE.get(k) else None), "first_use_op": min(USE[k]) if USE.get(k) else None,
           "binder": ("op return _bind_create stagexec.py:2329-2368" if OPS[k - 1].get("route") in ("while", "for", "case", "case_wired", "fs_create", "fs_frame")
                      else "bind_new class->term key stagexec.py:891-967" + (" + track_new :2119-2127" if OPS[k - 1]["kind"] == "add_sr" else "")
                      + (" + bind_fs_tunnel/bind_case_faces :2116-2117" if OPS[k - 1]["kind"] in ("connect_term_uid", "tunnel") else ""))} for k in BIND if k <= 39]
out = {"card": "140-1", "model": {"start_mb": START, "start_rule": "constant 606.1 = 600.2 bed load + 5.9 op-0 read for EVERY session (brief item 4); variant grow = +"
       "{0} MB per applied op (memory_model load_growth_mb_per_op)".format(GROW), "limit": LIM, "read": v("read_mb"), "edit+other": v("edit_mb") + v("other_mb"), "final": v("final_read_mb")},
       "v14": {"actions": len(A), "ops": NOP, "bind_ops": len(BIND)}, "step1_x10": x1, "step1_binds": S1BIND,
       "merge": {"step1_reads": [0] + p1, "step1_groups": [{"read": p, "binds": g_, "ambiguous": amb(g_)} for p, g_ in zip(p1, grp(p1, 39))],
                 "v14_reads": [0] + pw, "v14_groups": [{"read": p, "binds": g_, "ambiguous": amb(g_)} for p, g_ in zip(pw, grp(pw, NOP))]},
       "table_A": TA, "table_B": TB, "totals": {"A": len(TA), "B": len(TB), "A_grow": stall(table("A", GROW)), "B_grow": stall(table("B", GROW)),
       "grow_empty_session_over_675_after_op": next(a for a in range(NOP + 1) if START + GROW * a + 2 * v("read_mb") + v("edit_mb") + v("other_mb") + v("final_read_mb") > LIM),
       "A_690": len(table("A", 0.0, 690.0)), "B_690": len(table("B", 0.0, 690.0))}}
json.dump(out, open(os.path.join(ROOT, "tools/bench/diag_c140_1_sessions.json"), "w", encoding="utf-8"), indent=1, default=str)
print("FACT totals", out["totals"], "| step1 merged reads", len(out["merge"]["step1_reads"]), "| v14 merged reads", len(out["merge"]["v14_reads"]),
      "| ambiguous groups s1", sum(1 for x in out["merge"]["step1_groups"] if x["ambiguous"]), "v14", sum(1 for x in out["merge"]["v14_groups"] if x["ambiguous"]))
nf = sum(1 for _l, ok in G if not ok)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if nf else "PASS", "gates": {"pass": len(G) - nf, "fail": nf},
                              "first_fail": next((l for l, ok in G if not ok), None), "artefacts": [{"path": "tools/bench/diag_c140_1_sessions.json"}]}))
sys.exit(1 if nf else 0)
