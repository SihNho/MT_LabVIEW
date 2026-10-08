# ---
# labview: none
# hardware: none
# ---
r"""diag_c150_a1_3_probe - card 150-a1-3 (OFFLINE, no LabVIEW, measurement only). Why `stage_prerun --rebase` of s07 onto the real s06 graph
is refused at stage_prerun.py:3849 (BINDING name-free shape: BuildArray 0 vs 1, LoopTunnel 2 vs 3), and the PD364(c) 14-action fallback rebase.
Existing tools checked: stage_prerun.rebase / rebind / _terms / plan_named_uids (read-only import), vigraph.dedupe_rows / node_of / node_class.
This file RE-COMPUTES rebind's first steps (stage_prerun.py:3803-3849) verbatim to name the unmatched objects; it changes no tool.
Parts: S7 = s07 (30-action plan) on s06; S6 = the same comparison for the earlier s05 -> s06 rebase (s06's _in plan, still provisional);
FB = byte copy prov148 -> plan_ring_p4_s07v18_fb150.json, then stage_prerun.rebase() on it with out_root = tools/bench/diag_c150_a1_3_sim
(same function the CLI calls at stage_prerun.py:4972; out_root keeps every write inside this card's globs).
PREDICTION CONTRACT: L inputs load; S7 counters reproduce the refusal (BuildArray 0/1, LoopTunnel 2/3); S6 counters equal (that rebase passed);
  FB the copy is byte-identical to prov148 before the call; FB-RESULT reported (pass or refusal, no prediction on which).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c150_a1_3_probe.log -- py -u tools/bench/diag_c150_a1_3_probe.py"""
import collections, hashlib, json, os, shutil, sys                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stage_prerun as SPR, vigraph as V                                                  # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
S07 = os.path.join(B, "plan_ring_p4_s07v18.json")
S07P = os.path.join(B, "plan_ring_p4_s07v18_prov148.json")
S07FB = os.path.join(B, "plan_ring_p4_s07v18_fb150.json")
S06 = os.path.join(B, "plan_ring_p4_s06v18.json")
S06IN = os.path.join(B, "plan_ring_p4_s06v18_in.json")
S06LIC = os.path.join(B, "plan_ring_p4_s06v18_licence.json")
CMAP6 = os.path.join(B, "creation_map", "plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl")
G6 = os.path.join(B, "graph_ring_p4s06_20261008_192149.json")
G5 = os.path.join(B, "graph_ring_p4s05_20261008_013759.json")
OUT = os.path.join(B, "diag_c150_a1_3_sim")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                            # noqa: E731
ab = lambda p: p if os.path.isabs(p) else os.path.join(ROOT, p)                           # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1500]), flush=True)


def jl(p):
    return json.load(open(p, encoding="utf-8"))


def compare(tag, plan_path, graph_path, classes=("BuildArray", "LoopTunnel")):
    """rebind's first steps, stage_prerun.py:3803-3849, verbatim; prints the unmatched nodes in detail."""
    plan = jl(plan_path)
    b = plan.get("base") or {}
    so = b.get("sim_of") or {}
    dn = jl(ab(so["plan"]))
    bn = (dn.get("finalized") or {}).get("base") or dn.get("base") or {}
    print("{0} PLAN {1} md5 {2}; base {3} prov={4}; sim_of {5} {6}; N's base (before) {7}".format(
        tag, os.path.relpath(plan_path, ROOT), md5(plan_path), b.get("path"), b.get("provisional"), so.get("plan"), so.get("md5"),
        bn.get("path")), flush=True)
    gb, before = SPR._terms(ab(bn["path"]))
    gp, prov = SPR._terms(ab(b["path"]))
    gr, real = SPR._terms(graph_path)
    before, prov, real = V.dedupe_rows(before)[0], V.dedupe_rows(prov)[0], V.dedupe_rows(real)[0]
    tkey = lambda r: (r["term_uid"], r.get("owner_uid"), str(r.get("term_name") or ""))   # noqa: E731
    old_t = set(tkey(r) for r in before)
    sim_new, real_new = collections.OrderedDict(), collections.OrderedDict()
    for r in prov:
        if V.node_of(r) < 0:
            sim_new.setdefault(V.node_of(r), []).append(r)
    for r in real:
        if tkey(r) not in old_t:
            real_new.setdefault(V.node_of(r), []).append(r)
    dirk = lambda r: (r.get("term_class", ""), bool(r["is_source"]))                      # noqa: E731
    shape = lambda rows: (V.node_class(rows[0]), tuple(sorted(dirk(r) for r in rows)))     # noqa: E731
    cs = collections.Counter(shape(v) for v in sim_new.values())
    cr = collections.Counter(shape(v) for v in real_new.values())
    print("{0} COUNTS before {1} prov {2} real {3}; sim_new nodes {4}; real_new nodes {5}".format(
        tag, len(before), len(prov), len(real), len(sim_new), len(real_new)), flush=True)
    bad = [k for k in sorted(set(cs) | set(cr), key=str) if cs.get(k, 0) != cr.get(k, 0)]
    for k in bad:
        print("{0} SHAPE-DIFF sim {1} real {2} key {3}".format(tag, cs.get(k, 0), cr.get(k, 0), k), flush=True)
    bo, ro, po = SPR._obj_id(gb), SPR._obj_id(gr), SPR._obj_id(gp)
    bnodes = set(V.node_of(r) for r in before)
    bterm = dict((r["term_uid"], r) for r in before)
    for side, dct in (("SIM", sim_new), ("REAL", real_new)):
        for n, rows in dct.items():
            if V.node_class(rows[0]) not in classes and shape(rows) not in bad:
                continue
            print("{0} {1}-NEW node #{2} class {3} shape-in-diff {4} node-in-before {5} obj real {6} obj before {7} obj prov {8}".format(
                tag, side, n, V.node_class(rows[0]), shape(rows) in bad, n in bnodes, ro.get(n), bo.get(n), po.get(n)), flush=True)
            for r in rows:
                o = bterm.get(r["term_uid"])
                why = ("uid absent from before" if o is None else "before had owner {0} name {1!r}".format(o.get("owner_uid"), o.get("term_name")))
                print("{0}   term {1} name {2!r} tclass {3} src {4} wire {5} owner {6} frame {7} | {8}".format(
                    tag, r["term_uid"], r.get("term_name"), r.get("term_class"), r.get("is_source"), r.get("wire_uid"), r.get("owner_uid"),
                    r.get("frame_diagram"), why), flush=True)
            if side == "REAL" and n in bnodes:
                allr = [x for x in real if V.node_of(x) == n]
                oldr = [x for x in before if V.node_of(x) == n]
                print("{0}   node #{1}: real rows {2} / before rows {3}; real terms {4}; before terms {5}".format(
                    tag, n, len(allr), len(oldr), sorted((x["term_uid"], x.get("term_name")) for x in allr),
                    sorted((x["term_uid"], x.get("term_name")) for x in oldr)), flush=True)
    return cs, cr, bad, real_new, sim_new


def grep_uids(tag, uids):
    for p in (S06, S06IN, S06LIC, CMAP6):
        txt = open(p, encoding="utf-8").read()
        for u in sorted(uids):
            hits = []
            for i, ln in enumerate(txt.splitlines(), 1):
                if str(u) in ln and any(not c.isdigit() for c in (ln[ln.find(str(u)) - 1:ln.find(str(u))] or " ")):
                    hits.append(i)
            if hits:
                print("{0} GREP {1} uid {2} lines {3}".format(tag, os.path.relpath(p, ROOT), u, hits[:12]), flush=True)


try:
    for p in (S07, S07P, S06, S06IN, G6, G5, CMAP6):
        print("IN {0} md5 {1}".format(os.path.relpath(p, ROOT), md5(p)), flush=True)
    gate("L inputs load", True)
    cs, cr, bad, rn7, sn7 = compare("S7", S07, G6)
    exp = {"BuildArray": (0, 1), "LoopTunnel": (2, 3)}
    got = dict((k[0], (cs.get(k, 0), cr.get(k, 0))) for k in bad)
    gate("S7 counters reproduce the refusal", got == exp, got)
    grep_uids("S7", set(n for n, rows in rn7.items() if V.node_class(rows[0]) in exp)
              | set(r["term_uid"] for rows in rn7.values() for r in rows if V.node_class(rows[0]) in exp))
    # the s06 actions that create/touch BuildArray / LoopTunnel / name them
    d6 = jl(S06)
    for i, a in enumerate(d6.get("actions") or []):
        s = json.dumps(a)
        if any(w in s for w in ("BuildArray", "Build Array", "LoopTunnel", "Tunnel", "tunnel")):
            print("S6ACT #{0} {1}".format(i, s[:400]), flush=True)
    for i, ln in enumerate(open(CMAP6, encoding="utf-8").read().splitlines(), 1):
        print("CMAP6 {0} {1}".format(i, ln[:400]), flush=True)
    p7, pp = jl(S07)["base"], jl(S07P)["base"]
    print("BASES s07 {0} | prov148 {1}".format(json.dumps(p7)[:300], json.dumps(pp)[:300]), flush=True)
    # S6: the earlier s05 -> s06 comparison (s06's _in plan carries the provisional base it was rebased from)
    d6in = jl(S06IN)
    if (d6in.get("base") or {}).get("provisional"):
        c6s, c6r, bad6, _r6, _s6 = compare("S6", S06IN, G5)
        gate("S6 counters equal (that rebase passed)", not bad6, bad6)
    else:
        print("S6 _in base not provisional: {0}".format(json.dumps(d6in.get("base"))[:300]), flush=True)
    # FB: PD364(c) fallback on a byte copy
    shutil.copyfile(S07P, S07FB)
    gate("FB copy byte-identical to prov148", md5(S07FB) == md5(S07P), md5(S07FB))
    os.makedirs(OUT, exist_ok=True)
    lines = []
    try:
        ok, why = SPR.rebase(S07FB, G6, log=lambda s: (lines.append(s), print("FBLOG " + str(s)[:600], flush=True)), out_root=OUT)
    except Exception as e:                                                                   # noqa: BLE001
        ok, why = False, "rebase raised {0}: {1}".format(type(e).__name__, str(e)[:300])
    print("FB-RESULT ok={0} | {1}".format(ok, why), flush=True)
    print("FB plan md5 now {0} (prov148 {1})".format(md5(S07FB), md5(S07P)), flush=True)
    gate("FB-RESULT reported", True, "ok={0}".format(ok))
except Exception as e:                                                                       # noqa: BLE001
    import traceback
    traceback.print_exc()
    gate("probe ran", False, repr(e))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
