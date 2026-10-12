# ---
# labview: none
# hardware: none
# ---
"""Card 166-a1-5 (brief_166-a1-5.md, PD403(e) docs/d1/ring-p5c.md:273-282): P6 fact census F1..F5, OFFLINE, stored json only.

Writes tools/bench/p6_facts.json (rows, each with `source`) and tools/bench/p6_facts.md (tables). No LabVIEW, no VI opened:
the seven VIs are only byte-hashed before and after.

Prior art found before writing (and USED, not copied):
- tools/bench/diag_c108c_graph.py `Graph` (shared bench graph walker: owners/loop chain, first-non-carrier walk through
  tunnels / SR pairs / FS pairs / locals). The P5-final graph has no `graph_summary` key, which Graph.__init__ indexes, so this
  script hands Graph a json module whose loads() adds an empty `graph_summary` (no edit of the shared file; SubVI names are
  therefore not available - the stored graph holds class + terminal names only, frameidx_consumers.md U9).
- tools/bench/diag_c154_a1_2_census.py + frameidx_consumers.md (F2 on s09; its rows are cited for the counter column where the
  P5-final consumer uid is the same), tools/bench/diag_c153_a1_1_census*.py + p5_facts.md (layout precedent).
- No shared reader exists for: expected-file class counts per bed, wire-shape lineage across stored graphs, docstring census of
  tools. They are specific to this census and live here (card write globs allow no tools/*.py edit).

Prediction contract: inputs at their card md5; expected-file counts sum to 47 over 46 entries; 22 termless wires termless in
P5-final; #644 and FrameIdx rows exist; RingSeqCheck-shaped and RingPickSlot-shaped SubVIs found by terminal names; seven VI
md5s unchanged; no LabVIEW process before or after.
"""
import ast, collections, glob, hashlib, json, os, re, subprocess, sys, types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol                                   # noqa: E402
import diag_c108c_graph as DG                    # noqa: E402

B = "tools/bench/"
GF = B + "graph_ring_p5s02e_20261012_173009.json"
ELF = B + "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json"
XF = B + "errorlist_expected_D1_ring_p5_20261010_172913.json"
S1F = "docs/wiki/subvi/D1_s1_copy.json"
CDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SEVEN = ["75773b0d", "7f2582ae", "eb1d0f31", "94ffff94", "f9ae7751", "564d8cbe", "6dcd5c3d"]
PINS = {B + "cards/brief_166-a1-5.md": "78be2c34f9da405062c86c0e6319dcfb", "docs/d1/ring-p5c.md": "d62725b9e9ba1044dc77c35fe41d921a",
        "docs/script-writing.md": "0165fb24dc476b0b6fd863c96a346728", GF: "7815af0993bd8aeb1f14c7d3d76b0da1",
        ELF: "0c0664d8df07e47b8e63ac3278ed1daf", XF: "c94be128e4e8cb9275abf7bacb1fa192", B + "p5_facts.md": "1df5c37d7e214af604bcd079df218912"}
GATES = []


def gate(name, ok, detail=""):
    GATES.append((name, bool(ok)))
    print("GATE %s %s %s" % (name, "PASS" if ok else "FAIL", detail))


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lv_running():
    """True when the process list holds the LabVIEW image (a read of `tasklist`, nothing is launched)."""
    out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
    return ("lab" + "view") in out


def seven_vis():
    """{md5 prefix: [(file, md5)]} for every claudeDev D1_ring_p*.vi whose md5 starts with one of the seven pins (bytes only)."""
    fs = sorted(glob.glob(os.path.join(CDEV, "D1_ring_p*.vi")))
    got = {}
    for f in fs:
        m = md5(f)
        if m[:8] in SEVEN:
            got.setdefault(m[:8], []).append((os.path.basename(f), m))
    return got


def cite_line(path, line, must):
    """'path:line' when that line of the file contains `must` (a read check), else raises - every doc citation is verified."""
    with open(path, encoding="utf-8", errors="replace") as f:
        ls = f.read().split("\n")
    if line < 1 or line > len(ls) or must not in ls[line - 1]:
        raise SystemExit("CITE-FAIL %s:%d lacks %r" % (path, line, must))
    return "%s:%d" % (path, line)


def find_line(path, must, start=1):
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, ln in enumerate(f.read().split("\n"), 1):
            if i >= start and must in ln:
                return "%s:%d" % (path, i)
    return None


# ---------------------------------------------------------------- start invariants
print("== invariants before")
lv0 = lv_running(); gate("I0 no LabVIEW process at start", not lv0)
pin_bad = {p: md5(p) for p in PINS if md5(p) != PINS[p]}
gate("I1 card inputs at their md5", not pin_bad, json.dumps(pin_bad))
V0 = seven_vis()
print("SEVEN-BEFORE", json.dumps(V0))
gate("I2 seven VIs found by md5", len(V0) == 7, "found %s" % sorted(V0))

# ---------------------------------------------------------------- graph (shared walker)
_json_loads = json.loads


def _loads(s):
    g = _json_loads(s)
    if isinstance(g, dict) and "terminals" in g:
        g.setdefault("graph_summary", {})
    return g


DG.json = types.SimpleNamespace(loads=_loads)     # Graph.__init__ only calls json.loads
LOOPNAME = dict(DG.LOOPNAME)
G = DG.Graph(os.path.join(ROOT, GF).replace("\\", "/"))
RAW = _json_loads(open(GF, encoding="utf-8").read())
OBJ = {o["uid"]: o for o in RAW["objs"]}
OWN = {int(k): v for k, v in RAW["owners"].items()}
GN = "graph_ring_p5s02e_20261012_173009.json"


def gsrc(what):
    return "%s%s %s" % (B, GN, what)


# Graph.chain stops at a flat-sequence frame: this graph's owners hold ['FlatSequenceFrame', 0] for frames (no FS uid), so the
# frame -> FS map comes from fs_measured.fs_frames and the FS's outer diagram from its FlatSequenceOuterTunnel faces.
FSF = {int(d): int(fs) for fs, fr in (RAW.get("fs_measured") or {}).get("fs_frames", {}).items() for d in fr}
FS_OUT = {}
for _u, _ts in G.by_owner.items():
    if G.cls.get(_u) == "FlatSequenceOuterTunnel":
        _ds = {t["frame_diagram"] for t in _ts}
        for _d in _ds:
            if _d in FSF:
                _out = {x for x in _ds if FSF.get(x) != FSF[_d]}
                if _out:
                    FS_OUT.setdefault(FSF[_d], sorted(_out)[0])


def diagram_chain(D):
    """[(cls, uid)] of the structures enclosing diagram D, inner -> outer (Graph.owners + struct_outer, FS frames via FSF/FS_OUT)."""
    out, guard = [], 0
    while D is not None and guard < 60:
        guard += 1
        o = G.owners.get(D)
        if o and o[1]:
            out.append((o[0], o[1])); D = G.struct_outer.get(o[1])
        elif D in FSF:
            s = FSF[D]; out.append(("FlatSequence", s)); D = FS_OUT.get(s)
            if D is None:
                out.append(("UNRESOLVED-above-FS", s))
        else:
            break
    return out


def obj_chain(uid):
    """Enclosing structures of a wire / node uid, from the frame_diagram of one of its terminal rows; None when it has no
    terminal row (this graph's objs[].owner holds the owner CLASS name only, e.g. 'Diagram')."""
    ts = G.by_wire.get(uid)
    if ts:
        return diagram_chain(ts[0]["frame_diagram"])
    if uid in G.by_owner or uid in G.term:
        return diagram_chain(G.diag(uid))
    return None


def loop_name(chain):
    if chain is None:
        return "unread (objs[].owner = class name only; no terminal row)"
    for c, s in chain:
        if c == "WhileLoop":
            return LOOPNAME.get(s, "while#%d" % s)
    if chain and chain[-1][0] == "UNRESOLVED-above-FS":
        return "unresolved (chain stops above FS #%d)" % chain[-1][1]
    return "outside every While (top level)"


def node_loop(n):
    return loop_name(obj_chain(n))


def chain_txt(c):
    return " < ".join("%s#%d" % (k, s) for k, s in (c or []))


def node_rows(n):
    return sorted(G.by_owner.get(n, []), key=lambda t: t["term_uid"])


def short(t):
    return "#%s %s '%s' t%s" % (G.node(t), G.ncls(G.node(t)), t["term_name"], t["term_uid"])


def ends(t, down):
    """first non-carrier ends from terminal t (Graph.walk); [] when unwired."""
    r = G.walk(t, down, lambda n: False)
    return [(short(e), [int(p) for p in path]) for e, path in r if e is not None]


def node_report(n):
    """every terminal of node n: name, direction, wire, first non-carrier source (inputs) or sinks (outputs)."""
    rep = []
    for t in node_rows(n):
        rep.append({"term": t["term_name"], "term_uid": t["term_uid"], "dir": "out" if t["is_source"] else "in",
                    "wire": t["wire_uid"], "ends": ends(t, t["is_source"]) if t["wire_uid"] else []})
    return rep


ROWS = {"F1": [], "F2": [], "F3": [], "F4": [], "F5": []}


def row(f, **kw):
    assert "source" in kw, kw
    ROWS[f].append(kw)
    print(f, json.dumps(kw, default=str)[:1500])


# ---------------------------------------------------------------- lineage graphs (for dating) + S1
LINEAGE = ["graph_l2a1_bed_20260927.json", "graph_l2a2_20260927.json", "graph_l2a3_bed_20260927.json", "graph_l2b1_20260927.json",
           "graph_l2b2a_20260928.json", "graph_l2b2b_20260928.json", "graph_l2b3_20260928.json", "graph_l2r1_saved_20260928.json",
           "graph_l2r2_saved_20260928.json", "graph_qrt_pool_20260928.json", "graph_ring_p2b_20261001_154542.json",
           "graph_ring_p3a_20261001_190155.json", "graph_ring_p3b1_20261002_073225.json", "graph_ring_p3b2a_20261002_094927.json",
           "graph_ring_p3b2b_20261002_133824.json"] + ["graph_ring_p4s0%d_%s.json" % (i, s) for i, s in [
               (1, "20261002_234419"), (2, "20261003_112505"), (3, "20261007_205535"), (4, "20261007_223245"), (5, "20261008_013759"),
               (6, "20261008_192149"), (7, "20261008_224835"), (8, "20261009_033522"), (9, "20261009_062044")]] + [
           "graph_ring_p5s01a_20261009_103621.json", "graph_ring_p5s01_20261009_125622.json", "graph_ring_p5s02a_20261010_032547.json",
           "graph_ring_p5s02b_20261010_111905.json", "graph_ring_p5s02c_20261010_131658.json", "graph_ring_p5s02d_20261010_154830.json",
           GN]
LG = collections.OrderedDict()
S1 = _json_loads(open(S1F, encoding="utf-8").read())
print("S1 keys", sorted(S1.keys()))


def wire_index(g):
    w = collections.defaultdict(list)
    for t in g.get("terminals", []):
        if t.get("wire_uid"):
            w[t["wire_uid"]].append(t)
    objs = {o["uid"]: o["class"] for o in g.get("objs", [])} if g.get("objs") else None
    return w, objs


LG["S1 D1_s1_copy"] = (S1F,) + wire_index(S1)
for f in LINEAGE:
    p = B + f
    if not os.path.exists(p):
        print("LINEAGE missing", p); continue
    g = _json_loads(open(p, encoding="utf-8").read())
    if not isinstance(g, dict) or "terminals" not in g:
        print("LINEAGE no-terminals", p, type(g).__name__); continue
    LG[f.replace("graph_", "").replace(".json", "")] = (p,) + wire_index(g)
print("LINEAGE used", list(LG.keys()))


def wire_shape(widx, objs, w):
    ts = widx.get(w, [])
    ns, nk = sum(1 for t in ts if t["is_source"]), sum(1 for t in ts if not t["is_source"])
    if ts:
        return "src%d/sink%d" % (ns, nk)
    if objs is None:
        return "no-terminals (objs not stored)"
    return "termless" if w in objs else "absent"


def wire_history(w):
    """[(graph, shape)] compressed into runs."""
    runs = []
    for name, (p, widx, objs) in LG.items():
        s = wire_shape(widx, objs, w)
        if runs and runs[-1][1] == s:
            runs[-1][2] = name
        else:
            runs.append([name, s, name])
    return runs


def s1_feed(w):
    widx = LG["S1 D1_s1_copy"][1]
    ts = widx.get(w, [])
    src = ["#%s %s '%s' t%s" % (t["owner_uid"], t["owner_class"], t["term_name"], t["term_uid"]) for t in ts if t["is_source"]]
    snk = ["#%s %s '%s' t%s" % (t["owner_uid"], t["owner_class"], t["term_name"], t["term_uid"]) for t in ts if not t["is_source"]]
    return src, snk


# ---------------------------------------------------------------- per-bed Error List class series (expected files + reads)
def el_class_of(text):
    s = re.sub(r"[^a-z]", "", text.lower())
    if "looseends" in s:
        return "looseends"
    if "notconnectedtoanything" in s or "completelyunconnected" in s:
        return "notconnected"
    if "differenttypes" in s:
        return "twotypes"
    if "unwiredorbad" in s:
        return "unwiredinput"
    if "nosource" in s:
        return "nosource"
    return "other"


def _stamp(p):
    m = re.search(r"_(\d{8}_\d{6})", os.path.basename(p))
    return (m.group(1) if m else "", p)


EXPS = sorted((p for p in glob.glob(B + "errorlist_expected_D1_ring_p*.json") if "recipe_stale" not in p), key=_stamp)
EXP_SERIES = []
for p in EXPS:
    x = _json_loads(open(p, encoding="utf-8").read())
    c = collections.Counter()
    for e in x.get("expected", []):
        c[el_class_of(e.get("label", "") + " " + " ".join(e.get("norm_all", [])))] += e.get("count", 1)
    EXP_SERIES.append((os.path.basename(p), x.get("total"), dict(c)))
    print("EXP-SERIES", os.path.basename(p), x.get("total"), dict(c))
READS = sorted((p for p in glob.glob(B + "errorlist_D1_ring_p*.json") if not re.search(r"_(raw|reuse)\.json$", p)), key=_stamp)
TYPES_RE = re.compile(r"type of the source is (.+?)\.\s*The type of the sink is (.+?)\.?\s*$", re.S)
READ_SERIES = []
for p in READS:
    try:
        r = _json_loads(open(p, encoding="utf-8").read())
    except Exception as ex:                       # noqa: BLE001
        print("READ-SKIP", p, ex); continue
    its = r.get("items") or []
    c = collections.Counter(el_class_of(it.get("raw", "") + " " + it.get("reason", "")) for it in its)
    tt = []
    for it in its:
        if el_class_of(it.get("raw", "") + it.get("reason", "")) == "twotypes":
            m = TYPES_RE.search(it.get("detail") or "")
            tt.append((it.get("index"), "source %s -> sink %s" % m.groups() if m else "types not in detail"))
    READ_SERIES.append((os.path.basename(p), len(its), dict(c), tt))
    print("READ-SERIES", os.path.basename(p), len(its), dict(c), json.dumps(tt)[:700])


def first_exp_naming(uid):
    for p in EXPS:
        if re.search(r'"uid": %d\b' % uid, open(p, encoding="utf-8").read()):
            return os.path.basename(p)
    return None


# ================================================================ F1 - the 47 items
print("== F1")
X = _json_loads(open(XF, encoding="utf-8").read())
E = _json_loads(open(ELF, encoding="utf-8").read())
XL = open(XF, encoding="utf-8").read().split("\n")


def exp_line(item):
    for i, ln in enumerate(XL, 1):
        if ln.strip() == '"item": %d,' % item:
            return "%s:%d" % (XF, i)
    return XF


nsum = 0
for e in X["expected"]:
    cnt = e.get("count", 1); nsum += cnt
    item = e.get("item")
    cls = e.get("class") or el_class_of(e.get("label", ""))
    obj = e.get("object") or {}
    uid = obj.get("uid")
    reads = e.get("read_index", [])
    src_e = exp_line(item) if item is not None else find_line(XF, "new in P5-2b, measured")
    rd = "; ".join("%s items[%d] '%s'" % (ELF, i, E["items"][i]["raw"]) for i in reads)
    base = {"item": item, "count": cnt, "class": cls, "read_index": reads, "read_text": rd}
    if obj.get("kind") == "wire" and uid:
        hist = wire_history(uid)
        shape_final = hist[-1][1]
        chain = obj_chain(uid)
        runs = " | ".join("%s..%s: %s" % (a, c, s) for a, s, c in hist)
        # 'present since' = first graph of the final run, if it is not the first lineage entry
        since = hist[-1][0]
        changed = ("shape '%s' first seen in %s; previous stored graph %s had '%s'" % (shape_final, since, hist[-2][2], hist[-2][1])
                   if len(hist) > 1 else "same shape in every stored graph incl. S1")
        src_, snk_ = s1_feed(uid)
        wts = G.by_wire.get(uid, [])
        srcnode = [short(t) for t in wts if t["is_source"]]
        row("F1", **base, uid=uid, kind="wire", final_shape=shape_final,
            owner_diagram=OBJ.get(uid, {}).get("owner"), chain=chain_txt(chain) if chain is not None else None, loop=loop_name(chain),
            final_source=srcnode, present_since=since, changed=changed, lineage=runs, s1_source=src_, s1_sinks=snk_,
            first_expected_naming=first_exp_naming(uid), producing=(e.get("clears_by") or {}).get("cause"),
            source="%s (entry); %s objs[uid=%d].owner + owners; lineage terminals[wire_uid=%d] in %d stored graphs; S1 %s terminals[wire_uid=%d]"
                   % (src_e, GN, uid, uid, len(LG), S1F, uid))
    elif obj.get("kind") == "node" and uid:
        rep = node_report(uid)
        s1rows = sorted([t for t in S1["terminals"] if t["owner_uid"] == uid], key=lambda t: t["term_uid"])
        s1feed = []
        for t in s1rows:
            if t["is_source"]:
                continue
            s, _ = s1_feed(t["wire_uid"]) if t["wire_uid"] else ([], [])
            s1feed.append({"term": t["term_name"], "term_uid": t["term_uid"], "s1_wire": t["wire_uid"], "s1_source": s})
        chain = obj_chain(uid)
        hist = []
        for name, (p, widx, objs) in LG.items():
            hist.append((name, "present" if (objs is None or uid in objs) else "absent"))
        row("F1", **base, uid=uid, kind="node " + str(G.ncls(uid)), owner_diagram=OBJ.get(uid, {}).get("owner"), chain=chain_txt(chain),
            loop=loop_name(chain), terminals=rep, unwired_inputs=[r["term"] + " t%d" % r["term_uid"] for r in rep if r["dir"] == "in" and not r["wire"]],
            unwired_outputs=[r["term"] + " t%d" % r["term_uid"] for r in rep if r["dir"] == "out" and not r["wire"]],
            s1_inputs=s1feed, present_since="S1 (node uid present in every stored graph: %s)" % all(h[1] == "present" for h in hist),
            producing=(e.get("clears_by") or {}).get("cause"), first_expected_naming=first_exp_naming(uid),
            source="%s (entry); %s terminals[owner_uid=%d]; %s terminals[owner_uid=%d]" % (src_e, GN, uid, S1F, uid))
    else:
        why = obj.get("evidence") or e.get("label")
        since = ("not dated: no per-item uid read of any bed (errorlist uid_route: %s)"
                 % E["items"][reads[0]]["show_error"]["uid_route"][:60]) if reads else "not dated"
        if cls == "twotypes" and reads:
            m = TYPES_RE.search(E["items"][reads[0]].get("detail") or "")
            txt = "source %s -> sink %s" % m.groups() if m else None
            hit = [nm for nm, n_, c_, tt_ in READ_SERIES if txt and any(x[1] == txt for x in tt_)]
            since += ("; the same detail text '%s' is in %d of %d stored EL reads, first %s (text match, not a uid match)"
                      % (txt, len(hit), len(READ_SERIES), hit[0] if hit else None))
        row("F1", **base, uid="unread", kind=obj.get("kind") or "item-only (new in P5-2b)", owner_diagram="unread", loop="unread",
            present_since=since,
            producing=(e.get("clears_by") or {}).get("cause") or e.get("label"), evidence=why,
            source="%s (entry); %s items[%s].show_error.uid == null" % (src_e, ELF, reads))
gate("F1a expected counts sum to 47", nsum == 47, "sum %d over %d entries" % (nsum, len(X["expected"])))
gate("F1b one F1 row per expected entry", len(ROWS["F1"]) == len(X["expected"]))
# wire-shape census of the final graph (context for the 21+2 loose ends)
shapes = collections.Counter()
srconly, sinkonly, termless = [], [], []
for o in RAW["objs"]:
    if o["class"] != "Wire":
        continue
    ts = G.by_wire.get(o["uid"], [])
    ns, nk = sum(1 for t in ts if t["is_source"]), sum(1 for t in ts if not t["is_source"])
    k = "termless" if not ts else ("source-only" if nk == 0 else ("sink-only" if ns == 0 else "src+sink"))
    shapes[k] += 1
    {"source-only": srconly, "sink-only": sinkonly, "termless": termless}.get(k, []).append(o["uid"])
print("WIRE-SHAPES", dict(shapes), "source-only", srconly, "sink-only", sinkonly)
nc = sorted(r["uid"] for r in ROWS["F1"] if r["class"] == "notconnected")
gate("F1c the 22 not-connected uids are termless wires in P5-final", nc and set(nc) <= set(termless), "nc %d termless %d" % (len(nc), len(termless)))
F1_WIRES = {"shapes": dict(shapes), "source_only": srconly, "sink_only": sinkonly, "termless": sorted(termless),
            "source": gsrc("objs[class=Wire] x terminals[wire_uid]")}

# ================================================================ F2 - #644 i and FrameIdx consumers
print("== F2")
FC = B + "frameidx_consumers.md"
FCL = open(FC, encoding="utf-8").read().split("\n")


def prior_row(uids):
    """last line of frameidx_consumers.md (s09 table comes after the original's) whose first cell names one of uids
    (the consumer or a carrier on the way); (cite, its COUNTER cell, the uid matched)."""
    for uid in uids:
        hits = [i for i, ln in enumerate(FCL, 1) if ln.startswith("| #%d " % uid)]
        if hits:
            return "%s:%d" % (FC, hits[-1]), FCL[hits[-1] - 1].split("|")[4].strip(), uid
    return None, None, None


def shape_from_graph(n, sink_name):
    """what the graph shows the consumer does with the value: by terminal names only (no function names in this graph)."""
    names = [t["term_name"] for t in G.by_owner.get(n, [])]
    if "x-y*floor(x/y)" in names:
        return "Quotient & Remainder, value on '%s' (terminals %s)" % (sink_name, names)
    if any(x.endswith("?") and "=" in x for x in names):
        return "comparison %s, value on '%s'" % ([x for x in names if x.endswith("?")], sink_name)
    if "x-y" in names:
        return "subtract x-y, value on '%s'" % sink_name
    if G.ncls(n) == "IndexArray":
        return "Index Array, value on '%s'" % sink_name
    return "class %s, value on '%s' (terminals %s)" % (G.ncls(n), sink_name, names)


def imm(t):
    """the other ends of terminal t's own wire (one hop, no carrier walk)."""
    if not t["wire_uid"]:
        return ["UNWIRED"]
    return [short(x) for x in G.by_wire.get(t["wire_uid"], []) if x["term_uid"] != t["term_uid"] and x["is_source"] != t["is_source"]]


i644 = [t for t in G.terms if t["owner_uid"] == 644 or t["term_uid"] == 644]
print("ROWS-644", [(t["term_uid"], t["owner_uid"], t["owner_class"], t["term_name"], t["is_source"], t["wire_uid"], t["frame_diagram"]) for t in i644])
fidx = [t for t in G.terms if t["term_name"] == "FrameIdx"]
print("ROWS-FrameIdx", [(t["term_uid"], t["owner_uid"], t["owner_class"], t["is_source"], t["wire_uid"], t["frame_diagram"]) for t in fidx])
gate("F2a #644 rows present", bool(i644)); gate("F2b FrameIdx rows present", bool(fidx))
seen = set()


def f2_consumers(origin, st, depth=0):
    """one F2 row per first non-carrier sink of source terminal st; an Index Array's 'element' is followed one level."""
    for e, path in G.walk(st, True, lambda n: False):
        if e is None:
            row("F2", origin=origin, start="t%d" % st["term_uid"], consumer="UNWIRED", source=gsrc("terminals[term_uid=%d]" % st["term_uid"]))
            continue
        n = G.node(e)
        if (origin, n, e["term_uid"]) in seen:
            continue
        seen.add((origin, n, e["term_uid"]))
        outs = ["%s -> %s" % (t["term_name"], [x[0] for x in ends(t, True)][:6]) for t in node_rows(n) if t["is_source"] and t["wire_uid"]]
        pr, pc, pu = prior_row([n] + [int(p) for p in path])
        row("F2", origin=origin, start="t%d w%s" % (st["term_uid"], st["wire_uid"]), consumer="#%d %s" % (n, G.ncls(n)),
            sink_term="'%s' t%d w%s" % (e["term_name"], e["term_uid"], e["wire_uid"]), via=["#%d %s" % (p, G.ncls(p)) for p in path],
            loop=node_loop(n), chain=chain_txt(obj_chain(n)),
            inputs=["'%s' <- %s" % (t["term_name"], imm(t)) for t in node_rows(n) if not t["is_source"]],
            outputs=outs, computes=shape_from_graph(n, e["term_name"]), counter_prior=pc, prior=pr, prior_uid=pu,
            source=gsrc("Graph.walk down from t%d; consumer terminals[owner_uid=%d]" % (st["term_uid"], n)) + ("; prior %s" % pr if pr else ""))
        if G.ncls(n) == "IndexArray" and depth == 0:
            for t in node_rows(n):
                if t["is_source"] and t["wire_uid"]:
                    f2_consumers("%s -> #%d '%s'" % (origin, n, t["term_name"]), t, depth + 1)


for origin, starts in (("#644 i", [t for t in i644 if t["is_source"]]), ("FrameIdx read", [t for t in fidx if t["is_source"]])):
    for st in {t["term_uid"]: t for t in starts}.values():
        f2_consumers(origin + " (t%d, %s)" % (st["term_uid"], node_loop(G.node(st))), st)
# FrameIdx writers (sinks) for completeness
for t in fidx:
    if not t["is_source"]:
        row("F2", origin="FrameIdx write/terminal (sink)", start="t%d" % t["term_uid"], consumer="#%s %s" % (t["owner_uid"], t["owner_class"]),
            fed_by=[x[0] for x in ends(t, False)], loop=node_loop(G.node(t)), source=gsrc("terminals[term_uid=%d]" % t["term_uid"]))
# #376 frame index (PD374(b) record counter) - what feeds it now
r376 = [t for t in G.by_owner.get(376, []) if t["term_name"] == "frame index"]
for t in r376:
    row("F2", origin="#376 'frame index' (PD374(b) record counter input)", start="t%d w%s" % (t["term_uid"], t["wire_uid"]),
        consumer="#376 %s" % G.ncls(376), fed_by=[x for x in ends(t, False)], loop=node_loop(376),
        source=gsrc("terminals[term_uid=%d]" % t["term_uid"]))

# ================================================================ F3 - item 6 void->I32; #2626 names vs S1
print("== F3")
tt_items = [it for it in E["items"] if el_class_of(it.get("raw", "")) == "twotypes"]
nvoidi32 = 0
for it in tt_items:
    m = TYPES_RE.search(it.get("detail") or "")
    st_ = m.groups() if m else ("?", "?")
    nvoidi32 += int(st_[0].strip().lower() == "void" and "32-bit integer" in st_[1])
    row("F3", part="a", what="P5-final twotypes read item", read_index=it["index"], text=it["raw"], source_type=st_[0], sink_type=st_[1],
        uid=it["show_error"].get("uid"), source="%s items[%d].detail" % (ELF, it["index"]))
row("F3", part="a", what="items in the 47 whose detail reads source 'void' -> sink 32-bit integer (item 6's text)", count=nvoidi32,
    of=len(tt_items), source="%s items[].detail (regex %s)" % (ELF, TYPES_RE.pattern))
tt_exp = [e for e in X["expected"] if e.get("class") == "twotypes"]
for e in tt_exp:
    row("F3", part="a", what="expected entry for it", item=e["item"], object=e["object"], cause=e["clears_by"].get("cause"),
        source=exp_line(e["item"]))
for name, n, c, tt in READ_SERIES:
    if tt:
        row("F3", part="a", what="twotypes items in a stored EL read", read=name, n_items=n, twotypes=tt, source=B + name + " items[].detail")
v6 = find_line(B + "diag_c149_a1_3_facts.md", "item 6 \"source void -> sink long [I32]\"")
row("F3", part="a", what="item 6 origin (s06)", text="s06 item 6 'source void -> sink long [I32]': no s05/predicted counterpart; wire unidentified",
    source=v6 or "tools/bench/diag_c149_a1_3_facts.md (line not found)")
row("F3", part="a", what="item 6 gone at s07", text="s07 EL 50, item 6 'source void -> sink I32' GONE",
    source=cite_line("docs/d1/ring-p4c.md", 361, "item 6"))
row("F3", part="a", what="types in P5-final graph", text="terminal rows carry no type field (keys %s)" % sorted(RAW["terminals"][0].keys()),
    source=gsrc("terminals[0] keys"))
# (b) #2626
fin = node_rows(2626)
s1r = sorted([t for t in S1["terminals"] if t["owner_uid"] == 2626], key=lambda t: t["term_uid"])
fin_in = [t for t in G.by_owner.get(2626, []) if not t["is_source"]]
s1_in = [t for t in S1["terminals"] if t["owner_uid"] == 2626 and not t["is_source"]]
print("2626-READ-ORDER final", [(t["term_uid"], t["term_name"], t["is_source"], t["wire_uid"]) for t in G.by_owner.get(2626, [])])
print("2626-READ-ORDER S1", [(t["term_uid"], t["term_name"], t["is_source"], t["wire_uid"]) for t in S1["terminals"] if t["owner_uid"] == 2626])
s1_by_uid = {t["term_uid"]: t for t in S1["terminals"] if t["owner_uid"] == 2626}
for k, t in enumerate(fin_in):
    s = s1_by_uid.get(t["term_uid"])
    s1k = s1_in[k] if k < len(s1_in) else None
    fsrc = [x[0] for x in ends(t, False)]
    ssrc = s1_feed(s["wire_uid"])[0] if s and s["wire_uid"] else []
    row("F3", part="b", pos=k, term_uid=t["term_uid"], final_name=t["term_name"], final_wire=t["wire_uid"], final_source=fsrc,
        s1_name_same_uid=s["term_name"] if s else "uid not in S1", s1_name_same_pos=s1k["term_name"] if s1k else None,
        s1_source=ssrc, name_equal=(s is not None and s["term_name"] == t["term_name"]),
        source="%s terminals[owner_uid=2626] read order; %s terminals[owner_uid=2626]" % (gsrc(""), S1F))
for t in [t for t in G.by_owner.get(2626, []) if t["is_source"]]:
    s = s1_by_uid.get(t["term_uid"])
    row("F3", part="b", pos="out", term_uid=t["term_uid"], final_name=t["term_name"], final_wire=t["wire_uid"],
        final_sinks=[x[0] for x in ends(t, True)] if t["wire_uid"] else "UNWIRED", s1_name_same_uid=s["term_name"] if s else None,
        s1_sinks=s1_feed(s["wire_uid"])[1] if s and s["wire_uid"] else [], name_equal=(s is not None and s["term_name"] == t["term_name"]),
        source=gsrc("terminals[owner_uid=2626]") + "; " + S1F)
row("F3", part="b", what="PD366(d) wording of the P6 check", text="element <- x-y chain (t2832), element <- TransPos (t4160), element <- RotPos (t4165), array <- x,y,z chain (t4168)",
    source=cite_line("docs/d1/ring-p4c.md", 339, "t2832"))

# ================================================================ F4 - overload path as built
print("== F4")
by_node_names = collections.defaultdict(set)
for t in G.terms:
    by_node_names[G.node(t)].add(t["term_name"])


def pick(pred):
    return sorted(n for n, ns in by_node_names.items() if pred(ns, n))


IN_N, OUT_N = collections.defaultdict(set), collections.defaultdict(set)
for t in G.terms:
    (OUT_N if t["is_source"] else IN_N)[G.node(t)].add(t["term_name"])


def has(names, prefix):
    return any(x.startswith(prefix) for x in names)


def queue_node(n):
    return has(IN_N[n], "queue") or has(OUT_N[n], "queue out")


SEL = collections.OrderedDict()
SEL["RingSeqCheck-shaped SubVI (n1,n2,Latest)"] = pick(lambda ns, n: {"n1", "n2", "Latest"} <= ns)
SEL["RingPickSlot-shaped SubVI (Num,last,min slot)"] = pick(lambda ns, n: {"Num", "last", "min slot"} <= ns)
SEL["queue: in 'element' + out 'timed out?' (Enqueue-shaped)"] = pick(lambda ns, n: queue_node(n) and "element" in IN_N[n] and "timed out?" in OUT_N[n])
SEL["queue: out 'element' + out 'timed out?' (Dequeue-shaped)"] = pick(lambda ns, n: queue_node(n) and "element" in OUT_N[n] and "timed out?" in OUT_N[n])
SEL["queue: out 'overflow element' (Lossy-Enqueue-shaped)"] = pick(lambda ns, n: queue_node(n) and has(OUT_N[n], "overflow element"))
SEL["queue: in 'force destroy?...' (Release-shaped)"] = pick(lambda ns, n: queue_node(n) and has(IN_N[n], "force destroy?"))
SEL["queue: out 'remaining elements', no 'force destroy?' (Flush-shaped)"] = pick(
    lambda ns, n: queue_node(n) and has(OUT_N[n], "remaining elements") and not has(IN_N[n], "force destroy?"))
SEL["queue: in 'max queue size...' or 'create if not found?' (Obtain-shaped)"] = pick(
    lambda ns, n: has(IN_N[n], "max queue size") or has(IN_N[n], "create if not found"))
SEL["queue: out 'elements in queue' (Status-shaped)"] = pick(lambda ns, n: queue_node(n) and any("elements in queue" in x for x in OUT_N[n]))
SEL["queue: any other node with a 'queue' in / 'queue out' out"] = pick(lambda ns, n: queue_node(n))
_classified = set(x for k, v in SEL.items() if k.startswith("queue:") and "any other" not in k for x in v)
SEL["queue: any other node with a 'queue' in / 'queue out' out"] = [n for n in SEL["queue: any other node with a 'queue' in / 'queue out' out"]
                                                                  if n not in _classified]
for lab in ("Latest", "Num", "last", "records final (1.2 to 1.7)", "Total Lost Frames", "LastBufferNumber", "discards", "StopAll"):
    SEL["terminal/local named '%s'" % lab] = pick(lambda ns, n, lab=lab: lab in ns and G.ncls(n) in ("Local", "ControlTerminal", "?", "Property", "PropertyItem")
                                                   or (lab in ns and n in G.term and G.term[n]["term_class"] == "ControlTerminal"))
F4N = collections.OrderedDict()
for lab, ns in SEL.items():
    print("F4-SEL", lab, ns)
    for n in ns:
        F4N.setdefault(n, []).append(lab)
for n, labs in F4N.items():
    row("F4", node="#%d %s" % (n, G.ncls(n)), matched=labs, loop=node_loop(n), chain=chain_txt(obj_chain(n)), terminals=node_report(n)
        if n not in G.term else [{"term": G.term[n]["term_name"], "dir": "out" if G.term[n]["is_source"] else "in", "wire": G.term[n]["wire_uid"],
                                  "ends": ends(G.term[n], G.term[n]["is_source"])}],
        source=gsrc("terminals[owner_uid=%d] (selected by terminal names: %s)" % (n, "; ".join(labs))))
# shift registers (both sides) whose first non-carrier neighbours include RingSeqCheck, a queue node or an 'x+1' node
rsc = set(SEL["RingSeqCheck-shaped SubVI (n1,n2,Latest)"])
qn = set(x for k, v in SEL.items() if k.startswith("queue:") for x in v)
inc = set(n for n in by_node_names if "x+1" in OUT_N[n])
cnt_srs = []
for L in RAW["loops"]:
    for r, ls in (L.get("left_of") or {}).items():
        near = set()
        for u in [int(r)] + [int(x) for x in ls]:
            for t in G.by_owner.get(u, []):
                for e, path in G.walk(t, t["is_source"], lambda n: False):
                    if e is not None:
                        near.add(G.node(e))
        why = [k for k, s in (("RingSeqCheck", rsc), ("queue node", qn), ("x+1 node", inc)) if s & near]
        if why:
            cnt_srs.append((L["loop_uid"], int(r), [int(x) for x in ls], why, sorted((rsc | qn | inc) & near)))
for lu, r, ls, why, hit in cnt_srs:
    for u in [r] + ls:
        row("F4", node="#%d %s" % (u, G.ncls(u)), matched=["SR pair R#%d/L%s on loop #%d (%s) next to %s %s" % (r, ls, lu, LOOPNAME.get(lu, "while#%d" % lu), why, hit)],
            loop=LOOPNAME.get(lu, "while#%d" % lu), terminals=node_report(u), source=gsrc("loops[loop_uid=%d].left_of['%d'] + terminals[owner_uid=%d]" % (lu, r, u)))
def local_writers(name):
    """every Local / terminal row that WRITES the front-panel object `name` (is_source False), with its loop and one-hop source."""
    return ["#%d %s in %s <- %s" % (G.node(t), t["owner_class"], node_loop(G.node(t)), imm(t)) for t in G.terms
            if t["term_name"] == name and not t["is_source"] and t["owner_class"] in ("Local", "Diagram") and t["wire_uid"]]


RSC_IN = {}
for n in rsc:
    for t in node_rows(n):
        if not t["is_source"] and t["term_name"]:
            one = imm(t)
            loc = [x for x in G.by_wire.get(t["wire_uid"], []) if x["is_source"] and x["owner_class"] == "Local"] if t["wire_uid"] else []
            fso = [x for x in G.by_wire.get(t["wire_uid"], []) if x["is_source"] and x["owner_class"] == "FlatSequenceOuterTunnel"] if t["wire_uid"] else []
            inner = ["t%d <- %s" % (y["term_uid"], imm(y)) for x in fso for y in G.by_owner.get(x["owner_uid"], []) if not y["is_source"]]
            RSC_IN[t["term_name"]] = {"one_hop": one, "first_non_carrier": [x[0] for x in ends(t, False)][:3] if t["wire_uid"] else [],
                                      "local_writers": local_writers(loc[0]["term_name"]) if loc else None,
                                      "through_FS_outer_tunnel": inner or None}
    for t in node_rows(n):
        if t["is_source"] and t["term_name"] == "valid":
            RSC_IN["valid ->"] = [x[0] for x in ends(t, True)]
row("F4", node="RingSeqCheck_v0 arithmetic (its build record)", matched=["doc"],
    text="valid = n1==n2 AND n1>last; next last = valid ? n1 : Latest-1; next discards = valid ? discards : discards+1",
    source=cite_line("docs/d1/ring-p4b.md", 140, "valid = n1==n2") + "; " + cite_line("docs/d1/ring-p4b.md", 141, "next discards"))
for n in qn:
    for c, s in (obj_chain(n) or []):
        if c == "CaseStructure":
            sel = [t for t in G.by_owner.get(s, [])]
            row("F4", node="case #%d around queue node #%d" % (s, n), matched=["enclosing CaseStructure"],
                text=("rows owned by the case: %s" % ["'%s' %s w%s <- %s" % (t["term_name"], "out" if t["is_source"] else "in", t["wire_uid"], imm(t)) for t in sel])
                if sel else "no terminal row is owned by the case in this graph: its selector source is unread",
                source=gsrc("terminals[owner_uid=%d]" % s))
CLAUSES = [
    ("U8", "Overload, acquisition -> tracking: discard the backlog and take the newest frame (latest-wins).", "docs/user-rules.md", 33, "U8"),
    ("U9", "No corruption: image memory and its buffer number change together and the consumer verifies them.", "docs/user-rules.md", 34, "U9"),
    ("U11", "Frame rules priority: (1) no corruption, (2) latest-wins, (3) sequential fallback.", "docs/user-rules.md", 36, "U11"),
    ("STATUS-2026-09-28 (1)", "NO CORRUPTION: image and buffer number change together, consumer verifies.", "STATUS.md", 131, "NO CORRUPTION"),
    ("STATUS-2026-09-28 (2)", "LATEST-WINS: discard the queued backlog, read the newest frame; a gap recorded by the buffer number is fine.", "STATUS.md", 131, "LATEST-WINS"),
    ("STATUS-2026-09-28 (3)", "FALLBACK: one sequential loop if (1)+(2) cannot be made provably safe.", "STATUS.md", 131, "FALLBACK"),
    ("STATUS-2026-09-28 planned", "'full Q_work => skip the newest read' (PD233/234) named as violating (2); pool structure may stay.", "STATUS.md", 131, "Q_work"),
]


def nodes_for(*labs):
    return ["#%d" % n for lab in labs for n in SEL.get(lab, [])]


BUILT = {
    "U8": ("1.1 -> 1.2 (ring): RingPickSlot-shaped %s; RingSeqCheck-shaped %s inputs %s, 'valid' -> %s; 1.2 -> 1.7 (queue): Enqueue-shaped %s, "
           "Dequeue-shaped %s, Lossy-Enqueue-shaped %s, Flush-shaped %s, Status-shaped %s, Release-shaped %s, Obtain-shaped %s, other queue nodes %s")
          % (nodes_for("RingPickSlot-shaped SubVI (Num,last,min slot)"), nodes_for("RingSeqCheck-shaped SubVI (n1,n2,Latest)"),
             {k: RSC_IN.get(k) for k in ("Latest", "last", "discards")}, RSC_IN.get("valid ->"),
             nodes_for("queue: in 'element' + out 'timed out?' (Enqueue-shaped)"), nodes_for("queue: out 'element' + out 'timed out?' (Dequeue-shaped)"),
             nodes_for("queue: out 'overflow element' (Lossy-Enqueue-shaped)"),
             nodes_for("queue: out 'remaining elements', no 'force destroy?' (Flush-shaped)"), nodes_for("queue: out 'elements in queue' (Status-shaped)"),
             nodes_for("queue: in 'force destroy?...' (Release-shaped)"),
             nodes_for("queue: in 'max queue size...' or 'create if not found?' (Obtain-shaped)"),
             nodes_for("queue: any other node with a 'queue' in / 'queue out' out")),
    "U9": "RingSeqCheck-shaped %s inputs n1 <- %s, n2 <- %s (seqlock pair); the write side of Num/image in 1.1 is listed in the 'Num' rows above; "
          "whether 1.1 writes Num and the image together is not read by this census" % (
              nodes_for("RingSeqCheck-shaped SubVI (n1,n2,Latest)"), RSC_IN.get("n1"), RSC_IN.get("n2")),
    "U11": "no node is selected for this clause by terminal names (it orders U9, U8 and the fallback); the U9 and U8 rows list what is built",
}
for cid, text, path, line, must in CLAUSES:
    key = cid.split(" ")[0] if cid.startswith("U") else None
    built = BUILT.get(key) if key else {
        "STATUS-2026-09-28 (1)": BUILT["U9"], "STATUS-2026-09-28 (2)": BUILT["U8"], "STATUS-2026-09-28 (3)": BUILT["U11"],
        "STATUS-2026-09-28 planned": "Q_work / pool nodes: not selected by this census's terminal-name search (no 'Q_work' terminal name: %s)"
        % ("Q_work" in " ".join(t["term_name"] for t in G.terms))}[cid]
    row("F4", clause=cid, clause_text=text, built_as=built, source=cite_line(path, line, must) + "; nodes: rows above (" + GN + ")")

# ================================================================ F5 - replay / ABBA tools
print("== F5")


def tool_facts(p):
    try:
        src = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        return None
    try:
        doc = ast.get_docstring(ast.parse(src)) or ""
    except SyntaxError:
        doc = "(does not parse)"
    hdr = {k: v for k, v in re.findall(r"^# (labview|hardware): *(\S+)", src, re.M)}
    args = sorted(set(re.findall(r"add_argument\(\s*['\"](--?[\w-]+)", src)))
    d1 = re.sub(r"\s+", " ", doc)
    cmp_ = [s.strip() for s in re.split(r"(?<=[.;])\s+", d1) if re.search(r"(?i)compar|identical|\bvs\b|lost frames|X/Y/Z|join", s)][:3]
    return {"md5": md5(p), "lines": src.count("\n") + 1, "scope": hdr, "args": args, "doc": d1[:300], "compares": cmp_,
            "names_ring_vi": bool(re.search(r"D1_ring|ring_p[3-6]", src))}


abba = []
for p in sorted(glob.glob("tools/*.py") + glob.glob("tools/bench/*.py") + glob.glob("tools/recipes/*.py")):
    try:
        if "ABBA" in open(p, encoding="utf-8", errors="replace").read():
            abba.append(p.replace("\\", "/"))
    except OSError:
        pass
replay = sorted(set(p.replace("\\", "/") for p in glob.glob("tools/**/*replay*.py", recursive=True)))
named = ["tools/bench/drive_original_copy_v5.py", "tools/bench/m8b_replay_compare.py", "tools/recipes/stage_replay_swap.py",
         "tools/bench/drive_m8_replay_110.py"]
me = os.path.basename(__file__).replace("\\", "/")
FRAME_RE = re.compile(r"(?i)m8|X/Y/Z|frames?\b|tra rows|lost|replay copy|picks")
skipped = []
for p in sorted(set(named + abba + replay)):
    if p.endswith(me):
        continue
    f = tool_facts(p)
    tags = [k for k, v in (("named", p in named), ("ABBA", p in abba), ("replay", p in replay)) if v]
    if f is None:
        row("F5", tool=p, status="missing", tags=tags, source="os.path.exists(%s) False" % p)
    elif tags == ["replay"] and not FRAME_RE.search(f["doc"]):
        skipped.append(p)                         # a 'replay' of logs / plans / gates, not of recorded frames
    else:
        row("F5", tool=p, status="exists", tags=tags, **f, source="%s:1 (docstring / scope header / add_argument)" % p)
row("F5", tool="replay*.py files whose docstring names no frame / X/Y/Z / m8 / picks (log, plan or gate replays)", status="listed, not frame tools",
    files=skipped, source="tools/**/*replay*.py docstrings (regex %s)" % FRAME_RE.pattern)
ring = [r["tool"] for r in ROWS["F5"] if r.get("names_ring_vi")]
row("F5", tool="frame replay / ABBA tool whose source names a D1 ring bed (D1_ring / ring_p3..p6)", status="exists" if ring else "missing",
    files=ring, source="source text of the F5 tools above (regex D1_ring|ring_p[3-6])")
row("F5", tool="PD224(c)/(d) recorded-frame replay", status="record",
    text="m8b replay: replay copy vs S1 replay copy, 15 picks, X/Y/Z bit-identical over 4,443 common rows; (d) accepted the display-loop VI on it",
    source=cite_line("docs/d1-loop12-17-split-plan.md", 1914, "m8b_replay_110.json") + "; " + cite_line("docs/d1-loop12-17-split-plan.md", 1915, "ACCEPTED at the FUNCTIONAL level"))
row("F5", tool="PD374(f) P6 acceptance wording", status="record", text="Rule-1a acceptance is P6: recorded-frame replay, X/Y/Z AND the saved files bit-identical with the original (PD238(f))",
    source=cite_line("docs/d1/ring-p5.md", 69, "recorded-frame"))
pat = re.compile(r"(?i)test[ _]delay|frame[ _-]?number[ _-]?gap|frame[ _-]gap|bufnum[ _-]?gap|overload[ _-]test")
hits = []
for p in glob.glob("tools/**/*.py", recursive=True):
    if os.path.basename(p) == me:
        continue
    try:
        if pat.search(open(p, encoding="utf-8", errors="replace").read()):
            hits.append(p)
    except OSError:
        pass
for test, line_must in (("steer_158 test 1: frame-number-gap test", "번호 간격 시험"), ("steer_158 test 2: execution order with a test delay in loop 1.2", "실행 순서")):
    row("F5", tool=test, status="missing" if not hits else "candidates", candidates=hits,
        text="no file under tools/**/*.py matches %s" % pat.pattern if not hits else "files matching %s" % pat.pattern,
        source=cite_line(B + "cards/steer_158.json", 8, line_must) + "; " + cite_line("docs/d1/runner.md", 57, "frame-number-gap test")
        + "; search tools/**/*.py")

# ---------------------------------------------------------------- outputs
lv1 = lv_running(); gate("I3 no LabVIEW process at end", not lv1)
V1 = seven_vis()
gate("I4 seven VIs unchanged", V0 == V1, json.dumps(V1))
for f in ROWS:
    gate("R-%s every row has a source" % f, all(r.get("source") for r in ROWS[f]), "%d rows" % len(ROWS[f]))
ua = [(f, i) for f in ROWS for i, r in enumerate(ROWS[f]) if "unread" in json.dumps(r, default=str)]
nd = [(f, i) for f in ROWS for i, r in enumerate(ROWS[f]) if "not dated" in json.dumps(r, default=str)]
OUT = {"schema": "p6-facts/1", "card": "166-a1-5", "plan": "docs/d1/ring-p5c.md:273-282 PD403(e)", "graph": GF, "graph_md5": PINS[GF],
       "el_read": ELF, "expected": XF, "s1": S1F, "lineage": list(LG.keys()), "exp_series": EXP_SERIES,
       "read_series": [(a, b, c) for a, b, c, d in READ_SERIES], "f1_wire_shapes": F1_WIRES, "seven_vis": V1,
       "rows": ROWS, "marked_unread": ua, "marked_not_dated": nd, "producer": "tools/bench/diag_c166_a1_5_census.py"}
with open(B + "p6_facts.json", "w", encoding="utf-8") as f:
    json.dump(OUT, f, indent=1, default=str, ensure_ascii=False)
print("COUNTS", {k: len(v) for k, v in ROWS.items()}, "unread", len(ua), "not-dated", len(nd))


def cell(x, n=220):
    s = x if isinstance(x, str) else json.dumps(x, default=str, ensure_ascii=False)
    s = s.replace("|", "/").replace("\n", " ")
    return s if len(s) <= n else s[:n - 3] + "..."


def table(rows, cols, n=220):
    out = ["| " + " | ".join(c for c, _ in cols) + " |", "|" + "---|" * len(cols)]
    for r in rows:
        out.append("| " + " | ".join(cell(f(r) if callable(f) else r.get(f, ""), n) for _, f in cols) + " |")
    return out


L = ["---", "type: facts", "status: current", "date: 2026-10-12", "card: 166-a1-5", "---",
     "# P6 fact census F1..F5 (PD403(e), docs/d1/ring-p5c.md:273-282) - facts only, no design, no verdict",
     "Written by `tools/bench/diag_c166_a1_5_census.py` -> `diag_c166_a1_5_census.log` (offline, stored json only; **LabVIEW reads 0**). "
     "Machine-readable rows with `source` per row: `tools/bench/p6_facts.json`.",
     "Inputs: P5 final graph `%s` (%s, read from bed 75773b0d), its Error List read `%s` (0c0664d8, 47 items), expected `%s` (c94be128), "
     "S1 = `%s` (byte copy of the original, md5 3e3d23ce)." % (GF, PINS[GF][:8], ELF, XF, S1F),
     "Words: **unread** = no stored read holds the value (never inferred); **not dated** = the dating needs a read that does not exist. "
     "Graph limits that apply to every row: objs[].owner holds the owner CLASS only ('Diagram'), so a wire without terminals has no "
     "location; no SubVI names, no types (frameidx_consumers.md U9). Loop names: 637 = 1.1, 10170 = 1.2, 23032 = 1.5, 23041 = 1.7 "
     "(`tools/bench/diag_c108c_graph.py:15`); others are written while#uid.",
     "Lineage used for dating (file-name order; each file's bed identity from its name only): " + ", ".join(LG.keys()) + ".", ""]
f1 = ROWS["F1"]
L += ["## F1 - the 47 Error List items (46 expected entries; one entry has count 2)",
      "Class counts: %s. Wire shapes in the P5 final graph: %s; source-only %s; termless = the 22 'not connected' uids (gate F1c)."
      % (dict(collections.Counter(r["class"] for r in f1 for _ in range(r["count"]))), F1_WIRES["shapes"], F1_WIRES["source_only"]), ""]
L += table(f1, [("item", "item"), ("EL read idx", "read_index"), ("class", "class"), ("uid", "uid"),
                ("loop (P5 final)", "loop"), ("present since / change", lambda r: r.get("changed") or r.get("present_since")),
                ("S1: fed by -> sinks", lambda r: ("no terminal row in S1 (S1 json stores terminals only: absent or termless is unread)"
                                                   if "s1_source" in r and not r["s1_source"] and not r["s1_sinks"] else
                                                   "%s -> %s" % (r.get("s1_source"), r.get("s1_sinks"))) if "s1_source" in r
                 else (r.get("s1_inputs") if "s1_inputs" in r else "unread")),
                ("producing step (expected file's cause)", "producing"), ("source", "source")], 260)
n26 = next((r for r in f1 if r["uid"] == 2626), None)
if n26:
    L += ["", "- #2626 (item 9) in the P5 final: loop %s (%s); unwired inputs %s, unwired outputs %s; inputs fed by %s (%s)."
          % (n26["loop"], n26["chain"], n26["unwired_inputs"], n26["unwired_outputs"],
             [(t["term"], t["ends"]) for t in n26["terminals"] if t["dir"] == "in"], gsrc("terminals[owner_uid=2626]"))]
L += ["- Error List class counts per stored EL read (dating context for the item-only rows; files in bed order):"]
L += table([{"read": a, "n": b, "classes": c} for a, b, c, d in READ_SERIES], [("read", "read"), ("items", "n"), ("classes", "classes")], 200)
L += ["- The same per expected file:"]
L += table([{"exp": a, "total": b, "classes": c} for a, b, c in EXP_SERIES], [("expected file", "exp"), ("total", "total"), ("classes", "classes")], 200)
L += ["", "## F2 - consumers of `#644` i and of `FrameIdx` in the P5 final (PD374(g) text: `docs/d1/ring-p5.md:94-97`)",
      "Walk = `diag_c108c_graph.Graph.walk` (first non-carrier sink; tunnels, SR pairs, FS pairs, locals passed through). "
      "'computes' = what the consumer's terminal names show; 'counter (s09 census)' = the COUNTER cell of the same uid "
      "(consumer or a carrier on the way) in `tools/bench/frameidx_consumers.md`; no cell = no prior row, the graph shape column stands alone.", ""]
L += table(ROWS["F2"], [("origin", "origin"), ("consumer", "consumer"), ("sink term", "sink_term"), ("via", "via"), ("loop", "loop"),
                        ("computes (graph)", "computes"), ("outputs", "outputs"), ("counter (s09 census)", "counter_prior"),
                        ("fed by", "fed_by"), ("source", "source")], 240)
L += ["", "## F3 - open P6 obligations measured on the P5 final", "### (a) item 6 void -> I32 (PD363, `docs/d1/ring-p4c.md:177-187`)", ""]
runs3 = []
for r in [r for r in ROWS["F3"] if r["part"] == "a" and "read" in r]:
    key = json.dumps(sorted(x[1] for x in r["twotypes"]))
    if runs3 and runs3[-1]["key"] == key:
        runs3[-1]["last"] = r["read"]; runs3[-1]["n"] += 1
    else:
        runs3.append({"key": key, "first": r["read"], "last": r["read"], "n": 1})
f3a = [r for r in ROWS["F3"] if r["part"] == "a" and "read" not in r] + [
    {"what": "twotypes detail texts, stored EL reads %s .. %s (%d reads)" % (x["first"], x["last"], x["n"]), "read": "", "text": x["key"],
     "source": "tools/bench/errorlist_D1_ring_*.json items[].detail (each read file; rows in p6_facts.json F3)"} for x in runs3]
L += table(f3a, [("what", "what"), ("read / item", lambda r: r.get("read") or r.get("read_index") or r.get("item")),
                                                        ("value", lambda r: next(v for v in (
                                                            r.get("twotypes"),
                                                            ("source %s -> sink %s" % (r["source_type"], r["sink_type"])) if r.get("source_type") else None,
                                                            ("%s of %s" % (r["count"], r["of"])) if "of" in r else None,
                                                            r.get("text"), r.get("object"), r.get("cause"), "") if v)),
                                                        ("source", "source")], 300)
L += ["", "### (b) `#2626` input names, P5 final vs S1 (PD366(d), `docs/d1/ring-p4c.md:338-341`)", ""]
L += table([r for r in ROWS["F3"] if r["part"] == "b" and "pos" in r],
           [("pos", "pos"), ("term", "term_uid"), ("P5-final name", "final_name"), ("S1 name (same term uid)", "s1_name_same_uid"),
            ("equal", "name_equal"), ("P5-final fed by / sinks", lambda r: r.get("final_source") or r.get("final_sinks")),
            ("S1 fed by / sinks", lambda r: r.get("s1_source") or r.get("s1_sinks")), ("source", "source")], 200)
L += ["- " + next(r for r in ROWS["F3"] if r["part"] == "b" and "what" in r)["text"] + " (" +
      next(r for r in ROWS["F3"] if r["part"] == "b" and "what" in r)["source"] + ")"]
L += ["", "## F4 - the overload path as built (nodes selected by terminal names; no verdict)", ""]
L += table([r for r in ROWS["F4"] if "node" in r], [("node", "node"), ("selected as", "matched"), ("loop", "loop"), ("chain", "chain"),
                                                    ("terminals: name dir wire -> ends", lambda r: r.get("text") or [
                                                        "%s %s w%s -> %s" % (t["term"], t["dir"], t["wire"], [e[0] for e in t["ends"]][:4])
                                                        for t in r.get("terminals", []) if t["wire"] or t["term"]]),
                                                    ("source", "source")], 420)
L += ["", "### F4 clauses, each listed against what is built (facts only)", ""]
L += table([r for r in ROWS["F4"] if "clause" in r], [("clause", "clause"), ("text", "clause_text"), ("built as", "built_as"), ("source", "source")], 700)
L += ["", "## F5 - replay / ABBA tools: what exists, what is missing", ""]
L += table(ROWS["F5"], [("tool", "tool"), ("status", "status"), ("tags", "tags"), ("scope", "scope"),
                        ("what it compares (docstring)", lambda r: r.get("compares") or r.get("text") or r.get("files")),
                        ("doc head", "doc"), ("source", "source")], 260)
L += ["", "## Marked rows", "- rows holding 'unread': %d (%s)" % (len(ua), ", ".join("%s#%d" % x for x in ua)),
      "- rows holding 'not dated': %d (%s)" % (len(nd), ", ".join("%s#%d" % x for x in nd)),
      "- Seven VIs hashed before == after (bytes only, never opened): %s" % json.dumps(V1)]
with open(B + "p6_facts.md", "w", encoding="utf-8") as f:
    f.write("\n".join(L) + "\n")
print("MD lines", len(L))
gate("O1 md written <= 400 lines", len(L) <= 400, "%d lines" % len(L))
ok = all(g[1] for g in GATES)
print(protocol.result_line({"status": "PASS" if ok else "FAIL", "gates": {"pass": sum(g[1] for g in GATES), "fail": sum(not g[1] for g in GATES)},
                            "first_fail": next((g[0] for g in GATES if not g[1]), None),
                            "artefacts": [{"path": B + "p6_facts.json", "md5": md5(B + "p6_facts.json")},
                                          {"path": B + "p6_facts.md", "md5": md5(B + "p6_facts.md")}]}))
