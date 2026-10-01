r"""diag_c126_7_facts - card 126-7 (OFFLINE, read-only, no LabVIEW, no COM): PD255(e)(f) graph facts from files only.
(e) which of #30117/#3097 (Trans Pos) and #4580/#3160 (Rot pos) feeds the per-frame result path: every terminal row of the four
    nodes, then a forward trace (wire -> sink owner -> its source terminals -> ...) up to DEPTH hops, on the bed graph AND on the
    original-derived graphs that exist on disk; each row printed with its 1-based line in the dump when the dump is one-row-per-line.
(f) #6810 (IMAQ node whose BufNum/Image Out P3b reads): every terminal row incl. 'error in'/'error out' wiring; the bed VI's
    automatic-error-handling setting read from any file that records it (no LabVIEW).
PREDICTION: #30117/#4580 Value each feed a chain that reaches the record build (#11608 / #2626); #3097/#3160 locals do not; #6810's
error terminals are listed (wired or not); no file records the auto-error-handling flag of the bed (-> reported as NOT FOUND).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c126_7_facts.log -- py -u tools/bench/diag_c126_7_facts.py"""
import collections, glob, json, os, re, sys    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, vigraph as V    # noqa: E402,E401
DEPTH, NODES, TARGET = 8, (30117, 3097, 4580, 3160), (11608, 2626)
facts = []


def fact(s):
    facts.append(s)
    print("FACT", s, flush=True)


def lines_of(path):
    """{term_uid: [1-based line numbers]} when the dump has one terminal row per line (else {})."""
    out = collections.defaultdict(list)
    for n, ln in enumerate(open(path, encoding="utf-8"), 1):
        m = re.search(r'"term_uid":\s*(\d+)', ln)
        if m and '"owner_uid"' in ln:
            out[int(m.group(1))].append(n)
    return out


def trace(path):
    G = json.load(open(path, encoding="utf-8"))
    T = V.dedupe_rows(G["terminals"])[0]
    cls = dict((int(o["uid"]), o["class"]) for o in G["objs"])
    LN = lines_of(path)
    by_owner, by_wire = collections.defaultdict(list), collections.defaultdict(list)
    for r in T:
        by_owner[r["owner_uid"]].append(r)
        if r["wire_uid"]:
            by_wire[r["wire_uid"]].append(r)
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    print("== {0}  rows {1}  one-row-per-line {2}".format(rel, len(T), bool(LN)), flush=True)
    res = {}
    for u in NODES:
        rows = by_owner.get(u, [])
        print("  #{0} class {1}: {2}".format(u, cls.get(u), [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"], r["frame_diagram"],
                                                              LN.get(r["term_uid"])) for r in rows]), flush=True)
        seen, frontier, hit, hops = {u}, [u], None, []
        for d in range(DEPTH):
            nxt = []
            for n in frontier:
                for r in by_owner.get(n, []):
                    if not (r["is_source"] and r["wire_uid"]):
                        continue
                    for k in by_wire[r["wire_uid"]]:
                        if not k["is_source"] and k["owner_uid"] not in seen:
                            seen.add(k["owner_uid"])
                            nxt.append(k["owner_uid"])
                            hops.append((d + 1, n, r["wire_uid"], k["owner_uid"], cls.get(k["owner_uid"]), k["term_name"], LN.get(k["term_uid"])))
                            if k["owner_uid"] in TARGET and hit is None:
                                hit = (d + 1, k["owner_uid"])
            frontier = nxt
        print("  trace #{0}: hit {1}; first hops {2}".format(u, hit, hops[:12]), flush=True)
        res[u] = {"class": cls.get(u), "rows": len(rows), "hit": hit, "n_reached": len(seen) - 1}
    return G, T, by_owner, LN, rel, res


graphs = [os.path.join(B, "graph_ring_p3a_20261001_190155.json")]
for pat in ("graph_qrt_pool_20260928.json", "graph_original*.json", "graph_orig*.json", "wiki_graph*.json"):
    graphs += [g for g in glob.glob(os.path.join(B, pat)) if g not in graphs]
summ = {}
for g in graphs:
    try:
        G, T, by_owner, LN, rel, res = trace(g)
    except Exception as e:     # noqa: BLE001
        print("  SKIP {0}: {1}".format(g, e), flush=True)
        continue
    summ[rel] = res
    fact("(e) {0}: {1}".format(rel, dict((u, (r["class"], r["hit"], r["n_reached"])) for u, r in res.items())))
    e6810 = by_owner.get(6810, [])
    fact("(f) {0} #6810 rows: {1}".format(rel, [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"], LN.get(r["term_uid"])) for r in e6810
                                                if "error" in r["term_name"].lower() or r["term_name"] in ("Image Out", "current image number")]))
# (f) auto error handling: any recorded file that names it
hits = []
for pat in ("tools/bench/*.json", "tools/bench/*.log", "docs/*.md", "docs/wiki/**/*.json"):
    for f in glob.glob(os.path.join(ROOT, pat), recursive=True):
        try:
            txt = open(f, encoding="utf-8", errors="ignore").read()
        except OSError:
            continue
        for m in re.finditer(r"(?i)(auto(matic)?[ _-]?error[ _-]?handl\w*|DebuggingEnabled|AutoErrorHandling)", txt):
            ln = txt.count("\n", 0, m.start()) + 1
            hits.append("{0}:{1}: {2}".format(os.path.relpath(f, ROOT).replace("\\", "/"), ln, txt[max(0, m.start() - 60):m.end() + 60].replace("\n", " ")))
print("AUTOERR hits {0}".format(len(hits)), flush=True)
for h in hits[:40]:
    print("  AUTOERR", h[:260], flush=True)
fact("(f) auto-error-handling mentions in files: {0}".format(len(hits)))
print(P.result_line(P.make_result(len(facts), 0, None)), flush=True)
