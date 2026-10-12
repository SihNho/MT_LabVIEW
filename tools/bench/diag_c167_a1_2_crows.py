# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-2.json
# ---
r"""diag_c167_a1_2_crows - card 167-a1-2 (brief_167-a1-2.md, PD404(f) docs/d1/ring-p6.md:82-86): the C rows, OFFLINE, stored json only.

For each F2 consumer (#1114 #2136 #29411 #12045 #3162 #1628 #30240 #29240 #10068) writes one row with: owner chain in the P5 final graph
(7815af09) and in S1 (D1_s1_copy.json), when it runs (every iteration of its loop / inside a case frame, with the case uid and the
selector's source), the P3a new-frame counter terminals on its diagram and whether it reads them, and the stored repeated-BufNum records.
Every cell carries a `source`. No LabVIEW, no VI opened: the seven VIs are only byte-hashed before and after.

Prior art found before writing (USED, not copied):
- tools/bench/diag_c108c_graph.py `Graph` (owners, struct_outer, through_down/up, walk): the shared bench graph walker. The P5 graph has no
  `graph_summary` key, which Graph.__init__ indexes, so Graph gets a json module whose loads() adds an empty one (same hand-off as
  diag_c166_a1_5_census.py:105-115; the shared file is not edited - card rule).
- tools/protocol.py input_md5_changes (card input pins), tools/bench/prep_c156_a1_1_lib.py Gate + md5 (gates / RESULT line).
- VI name list: tools/bench/diag_c166_a1_1_hash.py:21-24 (data copied, no logic).
- NOT importable, re-written here and reported as duplicates (facts): diag_c166_a1_5_census.py:139-153 diagram_chain (FS frame -> FS via
  fs_measured.fs_frames, FS outer diagram via FlatSequenceOuterTunnel faces) and :58-61 lv_running - that script runs at import.
S1 json holds no `owners` map (keys: file md5 bytes read fs_tunnel_pairs connector_pane* terminals wires severed_wires graph_summary
io_paths summary call_sites_in_main; prep_c167_a1_2_shape.log). S1 chains therefore name the S1 diagram uid from S1 terminal rows, and
each diagram->outer-diagram link is shown by an S1 object with terminal rows on both diagrams; the structure uid/class of each diagram is
taken from the P5 owners map (stated in the cell).

PREDICTION CONTRACT (gates):
  B1 card inputs at their md5; B2 the seven VIs at their pins; B3 no LabVIEW process.
  R1 9 consumer rows, all present in P5; R2 absent in S1 = {#29411, #30240}; R3 #29411's sink face is in case #22694 frame d27219 and the
  case selector's source is #26879 'x = y?' t27144; R4 no consumer's sink wire is a counter wire; R5 every cell has a source.
  A1 inputs and seven VIs unchanged after; A2 no LabVIEW process after.
Facts (no gate): #1114/#2136 on d639 (1.1 body); #12045 in FS #16543 frame d16565 on d639; #3162 in case #3191 frame d3292; #1628 on d686
outside every While; #30240/#29240/#10068 on d23166 (1.2 body) in P5 and #29240/#10068 on d639 in S1; stored A-leg steps_le0 = 0.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c167_a1_2_crows.log -- py -u tools/bench/diag_c167_a1_2_crows.py
"""
import collections, glob, json, os, re, subprocess, sys, types                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
import diag_c108c_graph as DG                                                               # noqa: E402

B = "tools/bench/"
CARD = B + "cards/task_167-a1-2.json"
GF = B + "graph_ring_p5s02e_20261012_173009.json"
S1F = "docs/wiki/subvi/D1_s1_copy.json"
FACTS_JSON = B + "p6_facts.json"
P3A_STAGE = B + "stage_d1_ring_p3a.json"
P1F = B + "p1_bufmode_121.json"
SPLIT = "docs/d1-loop12-17-split-plan.md"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
VIS = [("D1_ring_p5_20261010_172913.vi", "75773b0d"), ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"),
       ("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
       ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751"), ("D1_ring_p5s02c_20261010_125755.vi", "564d8cbe"),
       ("D1_ring_p5s02d_20261010_152518.vi", "6dcd5c3d")]
CONSUMERS = [1114, 2136, 29411, 12045, 3162, 1628, 30240, 29240, 10068]
OUT_MD, OUT_JS, OUT_FACTS = B + "p6_crows.md", B + "p6_crows.json", B + "diag_c167_a1_2_facts.md"
gate = L.Gate(fatal_default=False)


def lv_running():
    """True when the process list holds the LabVIEW image (tasklist read only; same test as diag_c166_a1_5_census.py:58-61)."""
    return ("lab" + "view") in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def hashes():
    card = json.load(open(CARD, encoding="utf-8"))
    return PR.input_md5_changes(card), {n: L.md5(os.path.join(CD, n)) for n, _ in VIS}


def line_of(path, must, start=1):
    """'path:N' of the first line >= start containing `must`, else None (every doc citation is found by a read)."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, ln in enumerate(f.read().split("\n"), 1):
            if i >= start and must in ln:
                return "%s:%d" % (path, i)
    return None


# ------------------------------------------------------------------ before
print("== before", flush=True)
bad0, vh0 = hashes()
gate("B1 card inputs at their md5", not bad0, bad0 or "all %d equal" % len(json.load(open(CARD))["inputs"]))
gate("B2 seven VIs at their pins", all(vh0[n].startswith(p) for n, p in VIS), json.dumps({n: vh0[n] for n, _ in VIS}))
gate("B3 no LabVIEW process at start", not lv_running())

# ------------------------------------------------------------------ graphs (shared walker)
_loads = json.loads


def _loads_gs(s):
    g = _loads(s)
    if isinstance(g, dict) and "terminals" in g:
        g.setdefault("graph_summary", {})
        g.setdefault("objs", [])          # S1 json has no objs list (classes then come from its terminal rows' owner_class)
    return g


DG.json = types.SimpleNamespace(loads=_loads_gs)
G = DG.Graph(os.path.join(ROOT, GF).replace("\\", "/"))
G1 = DG.Graph(os.path.join(ROOT, S1F).replace("\\", "/"))
RAW = _loads(open(GF, encoding="utf-8").read())
FSF = {int(d): int(fs) for fs, fr in RAW["fs_measured"]["fs_frames"].items() for d in fr}
FS_OUT = {}
for _u, _ts in G.by_owner.items():
    if G.cls.get(_u) == "FlatSequenceOuterTunnel":
        _ds = {t["frame_diagram"] for t in _ts}
        for _d in _ds:
            if _d in FSF:
                _o = sorted(x for x in _ds if FSF.get(x) != FSF[_d])
                if _o:
                    FS_OUT.setdefault(FSF[_d], _o[0])
CASE_FRAMES = collections.defaultdict(list)
for _d, (_c, _s) in G.owners.items():
    if _c == "CaseStructure":
        CASE_FRAMES[_s].append(_d)


def gsrc(what):
    return "%s %s" % (GF, what)


def s1src(term_uid):
    return "%s:%d" % (S1F, G1.lines[term_uid]) if term_uid in G1.lines else "%s terminals[term_uid=%s]" % (S1F, term_uid)


def p5_chain(D):
    """[{diagram, cls, struct, outer}] inner -> outer from P5 owners (+ FS frames via fs_measured / FS outer-tunnel faces)."""
    out, guard = [], 0
    while D is not None and guard < 40:
        guard += 1
        o = G.owners.get(D)
        if o and o[1]:
            nxt = G.struct_outer.get(o[1])
            out.append({"diagram": D, "cls": o[0], "struct": o[1], "outer": nxt}); D = nxt
        elif D in FSF:
            nxt = FS_OUT.get(FSF[D])
            out.append({"diagram": D, "cls": "FlatSequence", "struct": FSF[D], "outer": nxt}); D = nxt
        else:
            out.append({"diagram": D, "cls": G.cls.get(D, "?"), "struct": None, "outer": None}); break
    return out


def chain_txt(ch):
    parts = []
    for s in ch:
        if s["struct"] is None:
            parts.append("d%d %s" % (s["diagram"], s["cls"]))
        else:
            nm = " (%s)" % DG.LOOPNAME[s["struct"]] if s["struct"] in DG.LOOPNAME else (" (while#%d)" % s["struct"] if s["cls"] == "WhileLoop" else "")
            parts.append("d%d in %s#%d%s" % (s["diagram"], s["cls"], s["struct"], nm))
    return " < ".join(parts)


def loop_of(ch):
    for s in ch:
        if s["cls"] == "WhileLoop":
            return DG.LOOPNAME.get(s["struct"], "while#%d" % s["struct"])
    return "outside every While"


S1_DIAGS = collections.defaultdict(set)
for t in G1.terms:
    S1_DIAGS[t["owner_uid"]].add(t["frame_diagram"])


def s1_link(a, b):
    """first S1 object (uid, class, term_uid on a) with terminal rows on both diagrams a and b, else None."""
    for u in sorted(S1_DIAGS):
        if a in S1_DIAGS[u] and b in S1_DIAGS[u]:
            t = [x for x in G1.by_owner[u] if x["frame_diagram"] == a][0]
            return u, t["owner_class"], t["term_uid"]
    return None


def selector(case):
    """(selector obj uid, its outer sink terminal, [source ends via Graph.walk up]) of a P5 CaseStructure: the 'Tunnel'-class object whose
    terminal rows lie on a frame of the case and on the case's outer diagram."""
    frames = set(CASE_FRAMES.get(case, []))
    outer = G.struct_outer.get(case)
    for u, ts in sorted(G.by_owner.items()):
        if G.cls.get(u) != "Tunnel":
            continue
        ds = {t["frame_diagram"] for t in ts}
        if outer in ds and (ds & frames or G.struct_of_tunnel(u) == case):
            sink = [t for t in ts if t["frame_diagram"] == outer and not t["is_source"]]
            if sink:
                return u, sink[0], G.walk(sink[0], False, lambda n: False)
    # selector rows with no inner face: a 'Tunnel' on the outer diagram whose own uid is listed by the P3a record (case 22694 only)
    return None, None, []


def case_frame_names():
    """{case: {frame diagram: name}} from stored records that name frames (P3a stage record case_wired result)."""
    out = {}
    st = json.load(open(P3A_STAGE, encoding="utf-8"))
    for a in st.get("actions") or st.get("ops") or []:
        r = a.get("result") if isinstance(a, dict) else None
        if isinstance(r, dict) and r.get("case") and r.get("frames") and r.get("names"):
            out[r["case"]] = dict(zip(r["frames"], r["names"]))
    return out


FRAME_NAMES = case_frame_names()

# ------------------------------------------------------------------ P3a counter (PD246(c)): LSR #27258 inner face, walked down
P3A = {"lsr": 27258, "rsr": 27250, "case": 22694}
lsr_inner = [t for t in G.by_owner.get(P3A["lsr"], []) if t["is_source"] and t["term_class"] == "InnerTerminal"]
CNT_TERMS, CNT_WIRES, CNT_ENDS = {}, set(), []
if lsr_inner:
    # every terminal the counter value reaches through carriers (Graph.through_down), incl. carrier paths that end unwired
    # (Graph.walk returns only paths with a non-carrier end, so the pass-through to RSR #27250 would be dropped)
    q, seen = collections.deque([lsr_inner[0]]), set()
    while q:
        s = q.popleft()
        if s["term_uid"] in seen:
            continue
        seen.add(s["term_uid"]); CNT_TERMS[s["term_uid"]] = s
        if not s["wire_uid"]:
            continue
        CNT_WIRES.add(s["wire_uid"])
        for e in G.by_wire.get(s["wire_uid"], []):
            if e["is_source"] or e["term_uid"] in CNT_TERMS:
                continue
            CNT_TERMS[e["term_uid"]] = e
            nxt = G.through_down(e)
            if nxt:
                q.extend(x for x in nxt if x["term_uid"] not in seen)
            else:
                CNT_ENDS.append(e)
print("COUNTER lsr_inner %s; wires %s; ends %s" % ([t["term_uid"] for t in lsr_inner], sorted(CNT_WIRES),
      ["#%d %s '%s' t%d d%d" % (e["owner_uid"], e["owner_class"], e["term_name"], e["term_uid"], e["frame_diagram"]) for e in CNT_ENDS]), flush=True)
p3a_src = line_of(P3A_STAGE, '"detail": "DigitalNumericConstant[96] #27269 -> WhileLoop[4] #637.t27 (L register #27258 outer)"') or P3A_STAGE
pd246 = line_of(SPLIT, "A5 → the counter increments inside the new-frame (False) frame") or SPLIT

# ------------------------------------------------------------------ repeated BufNum: stored records
REP = []
for p in sorted(glob.glob(B + "t0_legs/*/*/leg.json")):
    p = p.replace("\\", "/")
    j = json.load(open(p, encoding="utf-8"))
    fa, m8 = j.get("facts") or {}, j.get("m8") or {}          # leg.json: facts.period_proxy_637, m8.dry / m8.source_md5
    px = fa.get("period_proxy_637") or {}
    if "steps_le0" not in px or m8.get("dry") is not False:
        continue
    _m = re.search(r"/leg\d+_([AB])_", p)
    arm = _m.group(1) if _m else "?(%s)" % p.split("/")[-2]
    REP.append({"leg": p, "arm": arm, "source_md5": m8.get("source_md5") or fa.get("source_md5"), "leg_kind": m8.get("leg"),
                "tra": px.get("file"), "steps": px.get("steps"), "steps_le0": px["steps_le0"], "steps_gt1": px.get("steps_gt1"),
                "src": line_of(p, '"steps_le0"'), "dry_src": line_of(p, '"dry": false')})
P1_ROWS = []
_p1 = json.load(open(P1F, encoding="utf-8"))
_dup_lines = [i for i, ln in enumerate(open(P1F, encoding="utf-8").read().split("\n"), 1) if '"duplicates"' in ln]
for k, r in enumerate(_p1["rows"]):
    if r["mode"] == "Last" and r["delay_ms"] in (0, 1):
        P1_ROWS.append("Last delay %d ms @%s Hz: duplicates %s of calls %s (%s:%d)" % (r["delay_ms"], r["set_hz"], r["duplicates"], r["calls"], P1F, _dup_lines[k]))
fic_buf = line_of(B + "frameidx_consumers.md", "BufNum")
A_REP = [r for r in REP if r["arm"] == "A" and r["source_md5"] == "3e3d23cefd3a334001aa9d6156bf1aee"]
REP_TXT = ("ORIGINAL (S1 byte copy 3e3d23ce, A legs, dry=false): " +
           "; ".join("%s rows-steps %s, steps_le0 %s, steps_gt1 %s (%s)" % (r["leg"].split("/")[-2], r["steps"], r["steps_le0"], r["steps_gt1"], r["src"])
                     for r in A_REP) +
           " - steps_le0 = tra col-0 'frame-number' steps <= 0 (diag_c104_leg.py:193 label; col-0 = BufNum not read). "
           "NOT the original: P1 C-API camera bench (p1_bufmode_121.py:1): " + "; ".join(P1_ROWS) +
           ". frameidx_consumers.md: %s." % ("BufNum named at " + fic_buf if fic_buf else "no BufNum line"))
REP_SRC = ", ".join([r["src"] for r in A_REP] + [line_of(P1F, '"duplicates": 100088') or P1F, line_of(SPLIT, "(i) P1 MEASURED") or SPLIT,
                     "tools/bench/diag_c104_leg.py:193"])

# ------------------------------------------------------------------ rows
F2 = json.load(open(FACTS_JSON, encoding="utf-8"))["rows"]["F2"]
f2_by = {}
for r in F2:
    m = re.match(r"#(\d+)", r.get("consumer") or "")
    if m and int(m.group(1)) in CONSUMERS and int(m.group(1)) not in f2_by:
        f2_by[int(m.group(1))] = r
ROWS = []
for c in CONSUMERS:
    f2 = f2_by.get(c)
    tu = int(re.search(r" t(\d+)", f2["sink_term"]).group(1))
    f2src = line_of(FACTS_JSON, '"consumer": "#%d ' % c)
    row = {"consumer": c, "class": G.cls.get(c), "sink_term": tu, "sink_name": G.term[tu]["term_name"] if tu in G.term else None,
           "origin": f2["origin"], "f2_source": f2src}
    # P5 chain
    t = G.term.get(tu)
    D = t["frame_diagram"]
    ch = p5_chain(D)
    row["p5"] = {"value": "%s | loop %s" % (chain_txt(ch), loop_of(ch)), "chain": ch, "diagram": D,
                 "source": gsrc("terminals[term_uid=%d].frame_diagram=%d; owners[%s]; fs_measured.fs_frames; struct_outer via tunnel faces "
                                "(diag_c108c_graph.py:48-54)" % (tu, D, ",".join(str(s["diagram"]) for s in ch)))}
    # S1 chain
    t1 = G1.term.get(tu)
    if t1 is None or t1["owner_uid"] != c:
        row["s1"] = {"value": "absent in S1 (no terminal row term_uid=%d / owner #%d)" % (tu, c), "source": "%s terminals[owner_uid=%d] = []" % (S1F, c)}
    else:
        D1 = t1["frame_diagram"]
        ch1 = p5_chain(D1)
        links = []
        for s in ch1:
            if s["outer"] is not None:
                lk = s1_link(s["diagram"], s["outer"])
                links.append("d%d->d%d %s" % (s["diagram"], s["outer"], "by S1 #%d %s (%s)" % (lk[0], lk[1], s1src(lk[2])) if lk else "NO S1 LINK"))
        row["s1"] = {"value": "S1 diagram d%d; chain %s | loop %s; links in S1: %s" % (D1, chain_txt(ch1), loop_of(ch1), "; ".join(links)),
                     "diagram": D1, "source": "%s (term_uid=%d frame_diagram=%d); structure uid/class per P5 owners map (S1 json has no owners)"
                     % (s1src(tu), tu, D1)}
    # when it runs
    cases = [s for s in ch if s["cls"] == "CaseStructure"]
    loopname = loop_of(ch)
    if not cases:
        if loopname == "outside every While":
            run = "outside every While: d%d (%s); not per-iteration of 1.1 and not in the new-frame case" % (D, chain_txt(ch))
        else:
            run = "every iteration of %s (no CaseStructure between d%d and the While; chain %s)" % (loopname, D, chain_txt(ch))
        row["runs"] = {"value": run, "source": row["p5"]["source"]}
    else:
        parts, srcs = [], []
        for s in cases:
            su, st_, ends = selector(s["struct"])
            fname = FRAME_NAMES.get(s["struct"], {}).get(s["diagram"])
            src_txt = "; ".join("#%d %s '%s' t%d" % (e["owner_uid"], e["owner_class"], e["term_name"], e["term_uid"]) for e, _ in ends if e) or "unread"
            parts.append("in CaseStructure #%d frame d%d (frame name %s) - selector %s t%s <- %s" % (
                s["struct"], s["diagram"], ("'%s' (%s)" % (fname, p3a_src)) if fname else "unread",
                ("Tunnel #%d" % su) if su else "unread", st_["term_uid"] if st_ else "?", src_txt))
            srcs.append(gsrc("owners[%d]=['CaseStructure',%d]; selector terminals[owner_uid=%s] w%s" % (s["diagram"], s["struct"], su, st_["wire_uid"] if st_ else "?")))
        row["runs"] = {"value": "only in a case frame of %s: %s" % (loopname, "; ".join(parts)), "source": "; ".join(srcs)}
    # P3a counter terminals on its diagram
    on_d = sorted((x for x in CNT_TERMS.values() if x["frame_diagram"] == D), key=lambda x: x["term_uid"])
    reads = t["wire_uid"] in CNT_WIRES
    row["counter"] = {"value": ("P5 d%d counter terminals: %s; consumer reads one: %s (its sink w%d)" % (
                                D, ", ".join("t%d (#%d %s '%s')" % (x["term_uid"], x["owner_uid"], x["owner_class"], x["term_name"]) for x in on_d) or "none on this diagram",
                                "YES" if reads else "no", t["wire_uid"])) + "; S1: no counter (#27258 absent in S1)",
                      "source": gsrc("terminals[owner_uid=27258] (LSR, %s; PD246(c) %s); Graph.walk down from LSR inner face" % (p3a_src, pd246))}
    row["counter_read"] = reads
    row["repeated_bufnum"] = {"value": REP_TXT, "source": REP_SRC}
    ROWS.append(row)
    print("ROW #%d | P5 %s | S1 %s | RUNS %s | CNT %s" % (c, row["p5"]["value"], row["s1"]["value"], row["runs"]["value"], row["counter"]["value"]), flush=True)
print("REPEATED-BUFNUM %s" % REP_TXT, flush=True)

# ------------------------------------------------------------------ gates on the rows
gate("R1 9 consumer rows, all present in P5", len(ROWS) == 9 and all(G.term.get(r["sink_term"]) for r in ROWS), [r["consumer"] for r in ROWS])
absent = sorted(r["consumer"] for r in ROWS if r["s1"]["value"].startswith("absent"))
gate("R2 absent in S1 == [29411, 30240]", absent == [29411, 30240], absent)
r29 = [r for r in ROWS if r["consumer"] == 29411][0]
gate("R3 #29411 in case #22694 frame d27219, selector <- #26879 'x = y?' t27144",
     r29["p5"]["diagram"] == 27219 and "CaseStructure #22694" in r29["runs"]["value"] and "#26879 Comparison 'x = y?' t27144" in r29["runs"]["value"],
     r29["runs"]["value"])
gate("R4 no consumer's sink wire is a counter wire", not any(r["counter_read"] for r in ROWS), [r["consumer"] for r in ROWS if r["counter_read"]])
gate("R5 every cell has a source", all(r[k].get("source") for r in ROWS for k in ("p5", "s1", "runs", "counter", "repeated_bufnum")))

# ------------------------------------------------------------------ outputs
for r in ROWS:
    for k in ("p5",):
        r[k].pop("chain", None)
doc = {"schema": "p6-crows/1", "card": "167-a1-2", "plan": "docs/d1/ring-p6.md:82-86 PD404(f)", "p5_graph": {"path": GF, "md5": L.md5(GF)},
       "s1": {"path": S1F, "md5": L.md5(S1F)}, "words": {"unread": "no stored read holds the value"},
       "p3a_counter": {"lsr": 27258, "rsr": 27250, "case": 22694, "lsr_inner": [t["term_uid"] for t in lsr_inner], "wires": sorted(CNT_WIRES),
                       "ends": ["#%d %s '%s' t%d d%d" % (e["owner_uid"], e["owner_class"], e["term_name"], e["term_uid"], e["frame_diagram"]) for e in CNT_ENDS],
                       "source": gsrc("terminals[owner_uid=27258]; %s; %s" % (p3a_src, pd246))},
       "repeated_bufnum_records": {"legs": REP, "p1_rows": P1_ROWS, "frameidx_consumers_bufnum": fic_buf}, "rows": ROWS}
with open(OUT_JS, "w", encoding="utf-8") as f:
    json.dump(doc, f, indent=1)


def cell(x):
    return str(x).replace("|", "/").replace("\n", " ")


md = ["---", "type: facts", "status: current", "date: 2026-10-12", "card: 167-a1-2", "---",
      "# C rows - consumers of `#644` i and of FrameIdx (PD404(f), `docs/d1/ring-p6.md:82-86`) - facts only, no fix, no verdict",
      "Written by `tools/bench/diag_c167_a1_2_crows.py` -> `diag_c167_a1_2_crows.log` (offline, stored json only, LabVIEW reads 0). "
      "Machine-readable with a `source` per cell: `tools/bench/p6_crows.json`. P5 final = `%s` (%s); S1 = `%s` (%s, no owners map: structure "
      "uid/class of an S1 diagram is taken from the P5 owners map, each S1 diagram link shown by an S1 object with rows on both diagrams). "
      "Loop names `tools/bench/diag_c108c_graph.py:15`. **unread** = no stored read holds the value." % (GF, L.md5(GF)[:8], S1F, L.md5(S1F)[:8]),
      "",
      "P3a new-frame counter (PD246(c) `%s`): LSR #27258 on While #637 (`%s`), inner face t%s; walked down (Graph.walk) to: %s; counter wires %s." % (
          pd246, p3a_src, ",".join(str(t["term_uid"]) for t in lsr_inner), "; ".join(doc["p3a_counter"]["ends"]), sorted(CNT_WIRES)),
      "",
      "| consumer | sink | owner chain P5 final | owner chain S1 | when it runs | P3a counter terminal on its diagram / read? | sources |",
      "|---|---|---|---|---|---|---|"]
for r in ROWS:
    md.append("| #%d %s | '%s' t%d (F2 `%s`) | %s | %s | %s | %s | P5: %s; S1: %s; runs: %s; counter: %s |" % (
        r["consumer"], r["class"], r["sink_name"], r["sink_term"], r["f2_source"], cell(r["p5"]["value"]), cell(r["s1"]["value"]),
        cell(r["runs"]["value"]), cell(r["counter"]["value"]), cell(r["p5"]["source"]), cell(r["s1"]["source"]), cell(r["runs"]["source"]),
        cell(r["counter"]["source"])))
md += ["", "## Repeated BufNum (same for every row; stored records only)", REP_TXT, "", "Sources: " + REP_SRC, ""]
with open(OUT_MD, "w", encoding="utf-8") as f:
    f.write("\n".join(md))

# ------------------------------------------------------------------ after
bad1, vh1 = hashes()
gate("A1 card inputs and seven VIs unchanged after", not bad1 and vh1 == vh0, bad1 or "equal")
gate("A2 no LabVIEW process at end", not lv_running())
arts = [{"path": p, "md5": L.md5(p)} for p in (OUT_MD, OUT_JS)]
fx = ["---", "type: facts", "status: current", "date: 2026-10-12", "card: 167-a1-2", "---",
      "# diag_c167_a1_2 facts (C rows, PD404(f)) - offline, LabVIEW reads 0",
      "- Outputs: %s" % "; ".join("`%s` %s" % (a["path"], a["md5"]) for a in arts),
      "- Gates: %d pass / %d fail; first fail: %s (log `tools/bench/diag_c167_a1_2_crows.log`)" % (gate.G["pass"], gate.G["fail"], gate.G["first"]),
      "- Hash before == after: card inputs (protocol.input_md5_changes) and the seven VIs %s" % ", ".join("%s %s" % (n, vh1[n][:8]) for n, _ in VIS),
      "- No LabVIEW process before or after (tasklist)."]
for r in ROWS:
    fx.append("- #%d: P5 %s; S1 %s; %s; counter read: %s" % (r["consumer"], r["p5"]["value"].split(" | ")[-1], "absent" if r["s1"]["value"].startswith("absent") else
              "d%d" % r["s1"]["diagram"], r["runs"]["value"][:150], "yes" if r["counter_read"] else "no"))
fx += ["- Repeated BufNum: A legs (S1 byte copy) steps_le0 = %s; P1 C-API bench Last rows: %s." % ([r["steps_le0"] for r in A_REP], len(P1_ROWS)),
       "- Duplicated logic (not importable, re-written here): diag_c166_a1_5_census.py:139-153 diagram_chain, :58-61 lv_running; "
       "Graph gets graph_summary via a json.loads hand-off (census:105-115).",
       "- Limits: S1 json has no owners map; tra col 0 = BufNum not read; WLC 'index i' use inside the subVI unmeasured (frameidx_consumers.md U1)."]
with open(OUT_FACTS, "w", encoding="utf-8") as f:
    f.write("\n".join(fx) + "\n")
arts.append({"path": OUT_FACTS, "md5": L.md5(OUT_FACTS)})
for a in arts:
    print("ARTEFACT %s %s" % (a["path"], a["md5"]), flush=True)
sys.exit(gate.result(arts))
