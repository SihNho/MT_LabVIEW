r"""vigraph_g8_edges_74 - card 74-3. PURE PYTHON, no LabVIEW. The discriminating test named by the hypothesis review
archive/peer/2026-09-25-c74-vigraph-g8-keying.md section 4: build S1 and the rowD bed from diag_vigraph_check.load()'s
own inputs under THREE vigraph variants and print diff(S1,bed) minus fs edges for each, then list the added-set delta
between adjacent variants by terminal uid.
  VA = HEAD vigraph with dedupe_rows monkeypatched to identity (the 09-23 state: no dedupe, no DIAG_TERM)
  VB = HEAD vigraph (dedupe only; step 0 of the review: `git show HEAD:tools/vigraph.py` has dedupe_rows at :248,:280)
  VC = working-copy vigraph (dedupe + DIAG_TERM)
Existing tools found and reused: diag_vigraph_check.load (inputs), cdiff_blindspot_74.py's git-show import pattern.
PREDICTION (review's alternative): non-fs added VA 42, VB 39, VC 39; removed 15 and changed_sinks 9 in all three;
the 3 VA->VB edges carry an ordinal>0 key on a bed-duplicated term uid. Claim (a) instead predicts VB 42, VC 39.
    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/vigraph_g8_edges_74.log -- py -u tools/bench/vigraph_g8_edges_74.py"""
import importlib.util, json, os, subprocess, sys, tempfile, time                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)                 # noqa: E702
import vigraph as VC, protocol as P, diag_vigraph_check as D                         # noqa: E401,E402
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)  # noqa: E702


def fact(s):
    print("  FACT  " + s, flush=True)


def load_mod(name, rev):
    src = subprocess.run(["git", "show", rev + ":tools/vigraph.py"], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout
    p = os.path.join(tempfile.gettempdir(), name + ".py"); open(p, "w", encoding="utf-8").write(src)  # noqa: E702
    spec = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)  # noqa: E702
    return m


t0 = time.time()
VB = load_mod("vigraph_head74b", "HEAD")
VA = load_mod("vigraph_head74a", "HEAD")
VA.dedupe_rows = lambda terms: (list(terms), {"dropped": 0, "term_uids": [], "nonidentical": [], "disabled": True})
gate("S0 HEAD has dedupe_rows and no DIAG_TERM; working copy has DIAG_TERM",
     hasattr(VB, "dedupe_rows") and not hasattr(VB, "DIAG_TERM") and hasattr(VC, "DIAG_TERM"))
R = {}
for tag, V in (("VA", VA), ("VB", VB), ("VC", VC)):
    D.V = V                                                   # diag_vigraph_check.load uses its module-global V
    _r1, A = D.load(D.S1K)
    _rb, B = D.load(D.BEDK)
    d = V.diff(A, B)
    fsr = sum(1 for e in d["edges_removed"] if e[0] == "fs"); fsa = sum(1 for e in d["edges_added"] if e[0] == "fs")  # noqa: E702
    rest = {"edges_removed": d["counts"]["edges_removed"] - fsr, "edges_added": d["counts"]["edges_added"] - fsa,
            "changed_sinks": d["counts"]["changed_sinks"]}
    R[tag] = (V, A, B, d, rest)
    fact("{0}: diff counts {1}; non-fs {2}; dedupe S1 {3} bed {4}; edges S1 {5} bed {6}".format(
        tag, d["counts"], rest, A["method"]["dedupe"].get("dropped"), B["method"]["dedupe"].get("dropped"), len(A["edges"]), len(B["edges"])))
gate("P1 VA (no dedupe, no DIAG_TERM) non-fs added == 42", R["VA"][4]["edges_added"] == 42, R["VA"][4])
gate("P2 VB (HEAD, dedupe only) non-fs added == 39", R["VB"][4]["edges_added"] == 39, R["VB"][4])
gate("P3 VC (working, dedupe + DIAG_TERM) non-fs added == 39", R["VC"][4]["edges_added"] == 39, R["VC"][4])
gate("P4 removed 15 and changed_sinks 9 in all three", all(R[t][4]["edges_removed"] == 15 and R[t][4]["changed_sinks"] == 9 for t in R),
     [(t, R[t][4]) for t in R])


def ep(G, k):
    r = G["rows"][k]
    return {"key": k, "term_uid": r["term_uid"], "owner_uid": r.get("owner_uid"), "owner_class": r.get("owner_class"),
            "term_class": r.get("term_class"), "term_name": r["term_name"], "wire_uid": r.get("wire_uid")}


def uid_edges(G, kinds=("wire", "sr", "fs")):
    return set((k, G["rows"][a]["term_uid"], G["rows"][b]["term_uid"]) for k, a, b, _i in G["edges"] if k in kinds)


def added_nonfs(t):
    return set(tuple(e) for e in R[t][3]["edges_added"] if e[0] != "fs")


_bt = [r["term_uid"] for r in json.load(open(os.path.join(D.WIKI, D.BEDK + ".json"), encoding="utf-8"))["terminals"]]
_st = [r["term_uid"] for r in json.load(open(os.path.join(D.WIKI, D.S1K + ".json"), encoding="utf-8"))["terminals"]]
DUPB = set(u for u, c in __import__("collections").Counter(_bt).items() if c > 1)
DUPS = set(u for u, c in __import__("collections").Counter(_st).items() if c > 1)
fact("duplicated term uids: bed {0}, S1 {1}, bed-only {2}".format(len(DUPB), len(DUPS), sorted(DUPB - DUPS)))
for x, y in (("VA", "VB"), ("VB", "VC")):
    gone, new = sorted(added_nonfs(x) - added_nonfs(y)), sorted(added_nonfs(y) - added_nonfs(x))
    fact("DELTA {0}->{1}: added edges gone {2}, newly added {3}".format(x, y, len(gone), len(new)))
    for tag, s, t in (("GONE", gone, x), ("NEW", new, y)):
        V, A, B = R[t][0], R[t][1], R[t][2]
        s1u, s1keys = uid_edges(A), set((k, a, b) for k, a, b, _i in A["edges"])
        for e in s:
            a, b = ep(B, e[1]), ep(B, e[2])
            u = (e[0], a["term_uid"], b["term_uid"])
            # the same physical edge in the other variant's bed graph (by term uid) and its key there
            other = R[y if tag == "GONE" else x]
            ok = [(k, a2, b2) for k, a2, b2, _i in other[2]["edges"] if k == e[0] and other[2]["rows"][a2]["term_uid"] == u[1]
                  and other[2]["rows"][b2]["term_uid"] == u[2]]
            s1ep = [(ep(A, a2), ep(A, b2)) for k, a2, b2, _i in A["edges"] if k == e[0] and A["rows"][a2]["term_uid"] == u[1]
                    and A["rows"][b2]["term_uid"] == u[2]]
            fact("  {0} [{1}] {2} -> {3}".format(tag, e[0], V.show(e[1]), V.show(e[2])))
            fact("     bed src {0} | bed sink {1}".format(a, b))
            fact("     key in {0}: {1}; in {0} S1 key-set: {2}".format(y if tag == "GONE" else x, ok, [o in set((k, a2, b2) for k, a2, b2, _i in other[1]["edges"]) for o in ok]))
            fact("     S1 edge with identical term-uid endpoints: {0}; S1 endpoints {1}; src/sink uid bed-duplicated: {2}/{3}".format(
                u in s1u, s1ep[:2], a["term_uid"] in DUPB, b["term_uid"] in DUPB))
# P5/P6 re-stated in UID SPACE (run 1 stated them per key and failed on multiplicity: VA keys each duplicated sink row
# as its own edge; review archive/peer/2026-09-25-c74-g8-edges.md section 4 steps 1-3).
def uspace(t):
    V, A, B, d, _r = R[t]
    u = lambda G, k: G["rows"][k]["term_uid"]                                       # noqa: E731
    rem = set((e[0], u(A, e[1]), u(A, e[2])) for e in d["edges_removed"] if e[0] != "fs")
    add = set((e[0], u(B, e[1]), u(B, e[2])) for e in d["edges_added"] if e[0] != "fs")
    chg = set((u(A, c["sink"]), tuple(sorted(u(A, x) for x in c["before"])), tuple(sorted(u(B, x) for x in c["after"]))) for c in d["changed_sinks"])
    return rem, add, chg


U = dict((t, uspace(t)) for t in R)
for t in U:
    fact("UID-SPACE {0}: removed {1}, added {2} distinct pairs, changed_sinks {3}".format(t, *[len(s) for s in U[t]]))
gate("P5 uid-space removed / added / changed_sinks sets are IDENTICAL in VA, VB, VC",
     U["VA"] == U["VB"] == U["VC"], [(a, b, [len(s) for s in U[a]], [len(s) for s in U[b]], [sorted(x ^ y)[:4] for x, y in zip(U[a], U[b])])
                                      for a, b in (("VA", "VB"), ("VB", "VC")) if U[a] != U[b]])
gate("P5b uid-space counts 15 removed / 37 added / 9 changed (42 - 6 + 3 = 39 keys, 3 wires once each)",
     [len(s) for s in U["VC"]] == [15, 37, 9], [len(s) for s in U["VC"]])
VCB = R["VC"][2]
dt = dict((r["term_uid"], (r["node"], r["key"], r["is_source"], r["wire_uid"], VCB["cls"].get(r["node"]))) for r in VCB["rows"].values() if r["term_uid"] in (23073, 23225, 23444))
fact("VC bed rows 23073/23225/23444 (node, key, is_source, wire_uid, class): {0}".format(dt))
gate("P6 VC rows 23073, 23225, 23444 are unwired DiagramTerminal source nodes",
     len(dt) == 3 and all(v[2] and not v[3] and v[4] == VC.DIAG_TERM for v in dt.values()), dt)
fact("elapsed {0:.1f}s".format(time.time() - t0))
nf = sum(1 for _l, ok in GATES if not ok)
print(P.result_line(P.make_result(len(GATES) - nf, nf, next((l for l, ok in GATES if not ok), None))), flush=True)
sys.exit(1 if nf else 0)
