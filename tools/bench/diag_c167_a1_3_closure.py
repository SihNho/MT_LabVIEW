# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-3.json
# ---
r"""diag_c167_a1_3_closure - card 167-a1-3 (brief_167-a1-3.md, PD404(c)(e) docs/d1/ring-p6.md:63-67,77-81): the P6-0 CLOSURE TABLE,
OFFLINE, stored json only. Writes tools/bench/p6_closure.json + .md. Facts only: classes by CITATION (no citation = U), no fix, no verdict.

Rows = union of (i) the 47 Error List items of p6_facts.json F1 (46 entries, one with count 2; node item -> the node's cdiff rows, wire
item -> its S1 sink terminal(s), item-only -> its own row), (ii) both `open_rows` lists of plan_ring_p5s02e.json (:12 and :319), (iii)
vigraph.computation_diff(S1, 7815af09) - frame-keyed graphs as every ring recipe's PB (stagekit.s1_frame_graph + vigraph.build4(...,
frame_keyed=True) on the stored read); the default-mode diff is computed beside it and its row set quoted.
Per row: sink (owner, terminal, loop by the owner chain), S1 source, P5 source (cdiff effective sources + the direct wire source), class
R/DISP/D/C/U + citation (file:line found by READING the cited file for a quoted string, never typed), the RBW wire it maps to
(p6_rbw_deleted.json) and whether its Error List item is gone after RBW (errorlist_D1_ring_p6rbw_*.json; text compared with
errorlist_check.norm_ocr; an item whose class still has an item left and whose uid is unread = 'unknown which item').

Prior art found before writing (CALLED, not copied): stagekit.s1_frame_graph; vigraph.build4 / computation_diff / effective_sources;
jev_candidates.node_labels_default / load (S1 default-mode graph); diag_c108c_graph.Graph (owners, struct_outer, cite = file:line of a
term_uid); errorlist_check.norm_ocr; protocol.input_md5_changes + prep_c156_a1_1_lib Gate/md5 via diag_c167_a1_3_hash.check.
Re-written here and REPORTED as duplicates (not importable, the shared module is outside this card's write globs): the json hand-off that
gives Graph a `graph_summary` (diag_c167_a1_2_crows.py:94-104 = diag_c166_a1_5_census.py:105-115) and the FS-frame step of the owner chain
(diag_c167_a1_2_crows.py:109-118,130-147 = diag_c166_a1_5_census.py:139-153).

PREDICTION CONTRACT (gates): B before-hashes equal (13 inputs, 7 VIs, no LabVIEW); E1 every one of the 47 EL items sits on >= 1 row;
E2 both open_rows lists have 24 (node, term) pairs and are equal as sets; E3 frame-keyed cdiff rows = 31 = end_cdiff_rows 26 + the 5 #376
rows the P5 scratch PB RECORDED (diag_c165_p5s02e_scratch.log:152-156) [measured by prep_c167_a1_3_explore.log]; E4 every row has one class
and every non-U class a resolved citation; E5 every cell has a source; A after-hashes equal.
UNPREDICTED (the facts this card exists for): counts per class, U list, rows whose EL item is gone after RBW.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/diag_c167_a1_3_closure.log -- py -u tools/bench/diag_c167_a1_3_closure.py"""
import collections, json, os, re, sys, types                                                # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K, vigraph as V, jev_candidates as JC, errorlist_check as EC             # noqa: E401,E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
import diag_c167_a1_3_hash as H                                                             # noqa: E402
import diag_c108c_graph as DG                                                               # noqa: E402

B = "tools/bench/"
GF, S1F = B + "graph_ring_p5s02e_20261012_173009.json", "docs/wiki/subvi/D1_s1_copy.json"
PLAN, FACTS, RBW, ELA, CROWS = (B + "plan_ring_p5s02e.json", B + "p6_facts.json", B + "p6_rbw_deleted.json",
                                B + "errorlist_D1_ring_p6rbw_20261012_191349.json", B + "p6_crows.json")
OUT_JS, OUT_MD, OUT_F = B + "p6_closure.json", B + "p6_closure.md", B + "diag_c167_a1_3_facts.md"
P4, P4C, P5D, P6D, IDX = "docs/d1/ring-p4.md", "docs/d1/ring-p4c.md", "docs/d1/ring-p5.md", "docs/d1/ring-p6.md", "docs/d1/INDEX.md"
SPLIT = "docs/d1-loop12-17-split-plan.md"
gate = L.Gate(fatal_default=False)


def line_of(path, must):
    """'path:N' of the first line of `path` containing `must` (the citation is found by READING the file), else None."""
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, ln in enumerate(f.read().split("\n"), 1):
            if must in ln:
                return "%s:%d" % (path, i)
    return None


def cite(path, must, label):
    w = line_of(path, must)
    return {"label": label, "at": w, "quote": must} if w else None


# ------------------------------------------------------------------------------------------------ before
print("== before", flush=True)
H.check(gate, "before")

# ------------------------------------------------------------------------------------------------ inputs
J = L.J
F1 = J(FACTS)["rows"]["F1"]
SH = J(FACTS)["f1_wire_shapes"]
PL = J(PLAN)
CR = J(CROWS)
RB = J(RBW)
EA = J(ELA)
GRAW, S1RAW = J(GF), J(S1F)
_loads = json.loads


def _loads_gs(s):                      # hand-off as diag_c167_a1_2_crows.py:94-104 (Graph indexes graph_summary / objs)
    g = _loads(s)
    if isinstance(g, dict) and "terminals" in g:
        g.setdefault("graph_summary", {})
        g.setdefault("objs", [])
    return g


DG.json = types.SimpleNamespace(loads=_loads_gs)
G5, G1 = DG.Graph(os.path.join(ROOT, GF).replace("\\", "/")), DG.Graph(os.path.join(ROOT, S1F).replace("\\", "/"))
S1LINES = G1.lines


def s1cite(tu):
    return "%s:%d" % (S1F, S1LINES[tu]) if tu in S1LINES else "%s terminals[term_uid=%s]" % (S1F, tu)


FSF = {int(d): int(fs) for fs, fr in GRAW["fs_measured"]["fs_frames"].items() for d in fr}
FS_OUT = {}
for _u, _ts in G5.by_owner.items():                    # FS outer diagram by its outer-tunnel faces (as diag_c167_a1_2_crows.py:109-118)
    if G5.cls.get(_u) == "FlatSequenceOuterTunnel":
        _ds = {t["frame_diagram"] for t in _ts}
        for _d in _ds:
            if _d in FSF:
                _o = sorted(x for x in _ds if FSF.get(x) != FSF[_d])
                if _o:
                    FS_OUT.setdefault(FSF[_d], _o[0])


def loop_of(D):
    """(loop name, chain text) of P5 diagram D: owners map + struct_outer, FS frames via fs_measured.fs_frames + FS outer faces."""
    chain, guard = [], 0
    while D is not None and guard < 40:
        guard += 1
        o = G5.owners.get(D)
        if o and o[1]:
            chain.append("d%d in %s#%d" % (D, o[0], o[1]))
            if o[0] == "WhileLoop":
                return DG.LOOPNAME.get(o[1], "while#%d" % o[1]), " < ".join(chain)
            D = G5.struct_outer.get(o[1])
        elif D in FSF:
            chain.append("d%d in FlatSequence#%d" % (D, FSF[D]))
            D = FS_OUT.get(FSF[D])
        else:
            chain.append("d%d (%s)" % (D, (o or ["top"])[0]))
            break
    return "outside every While", " < ".join(chain)


def tdesc(t):
    return "#%s %s '%s' t%s" % (t["owner_uid"], t["owner_class"], t["term_name"], t["term_uid"])


def direct_src(Gx, tu):
    """[(desc, cite)] of the source terminal(s) on the wire of sink term `tu` in graph Gx (DG.Graph); [] = unwired / no source."""
    t = Gx.term.get(tu)
    if not t or not t["wire_uid"]:
        return []
    return [tdesc(x) for x in Gx.by_wire[t["wire_uid"]] if x["is_source"]]


# ------------------------------------------------------------------------------------------------ (iii) computation_diff
lab = JC.node_labels_default()
S1f = K.s1_frame_graph(lab)
Gf = V.build4(GRAW["terminals"], GRAW["objs"], GRAW["loops"], lab, GRAW["fs_tunnel_pairs"], frame_keyed=True)
CD = V.computation_diff(S1f, Gf)
S1d = JC.load(JC.S1_KEY)
Gd = V.build4(GRAW["terminals"], GRAW["objs"], GRAW["loops"], lab, GRAW["fs_tunnel_pairs"])
CD0 = V.computation_diff(S1d, Gd)
rk = sorted(str(r["sink"]) for r in CD["rows"])
rk0 = sorted(str(r["sink"]) for r in CD0["rows"])
end26 = PL["finalized"]["end_cdiff_rows"]
print("FACT cdiff frame-keyed rows %d, default-mode rows %d; only frame-keyed %s; only default %s" % (
    len(rk), len(rk0), sorted(set(rk) - set(rk0)), sorted(set(rk0) - set(rk))), flush=True)
REC = [ln for ln in open(B + "diag_c165_p5s02e_scratch.log", encoding="utf-8", errors="replace").read().split("\n") if "RECORD PB " in ln]
rec_sinks = sorted(set(re.search(r"RECORD PB (.+?\|\d+): ", x).group(1) for x in REC))
gate("E3 frame-keyed cdiff rows %d = end_cdiff_rows %d + the %d RECORDED PB rows of diag_c165_p5s02e_scratch.log" % (len(rk), len(end26), len(rec_sinks)),
     set(rk) == set(end26) | set(rec_sinks) and not (set(end26) & set(rec_sinks)), {"extra": sorted(set(rk) - set(end26)), "recorded": rec_sinks})

# ------------------------------------------------------------------------------------------------ (ii) open_rows, both lists, equality
L12 = [(int(y["node"]), y["term"]) for y in PL["open_rows"]]
L319 = [(int(a), b) for a, b in PL["finalized"]["open_rows"]]
with open(PLAN, encoding="utf-8") as f:
    _pl = [i for i, ln in enumerate(f.read().split("\n"), 1) if '"open_rows": [' in ln]
ln12, ln319 = "%s:%d" % (PLAN, _pl[0]), "%s:%d" % (PLAN, _pl[1])
gate("E2 open_rows lists: %s %d pairs, %s %d pairs, equal as sets" % (ln12, len(L12), ln319, len(L319)),
     set(L12) == set(L319) and len(L12) == len(set(L12)) == 24 and len(L319) == 24, {"only_12": sorted(set(L12) - set(L319)), "only_319": sorted(set(L319) - set(L12))})
pairs_cd = sorted(set((int(s.split("|")[0]), s.split("|")[2]) for s in rk))
pairs_cd0 = sorted(set((int(s.split("|")[0]), s.split("|")[2]) for s in rk0))
EQ = {"open_rows_12": {"at": ln12, "n": len(L12)}, "open_rows_319": {"at": ln319, "n": len(L319)},
      "lists_equal": set(L12) == set(L319),
      "cdiff_frame_keyed": {"rows": len(rk), "pairs": len(pairs_cd), "only_cdiff": [list(p) for p in sorted(set(pairs_cd) - set(L12))],
                            "only_open": [list(p) for p in sorted(set(L12) - set(pairs_cd))], "equal": set(pairs_cd) == set(L12)},
      "cdiff_default": {"rows": len(rk0), "pairs": len(pairs_cd0), "only_cdiff": [list(p) for p in sorted(set(pairs_cd0) - set(L12))],
                        "only_open": [list(p) for p in sorted(set(L12) - set(pairs_cd0))], "equal": set(pairs_cd0) == set(L12)},
      "recorded_pb_rows": {"rows": rec_sinks, "at": "%s:%d-%d" % (B + "diag_c165_p5s02e_scratch.log", 152, 156) if len(rec_sinks) == 5 else "diag_c165_p5s02e_scratch.log RECORD PB lines"},
      "key": "(node, S1-side terminal name) pairs = stagekit.pb_check's pairs; a cdiff slot set per pair (#2626 'element' = 3 slots)"}
print("FACT equality %s" % json.dumps(EQ), flush=True)

# ------------------------------------------------------------------------------------------------ RBW + Error List after
DEL = {int(d["wire_uid"]): d for d in RB["deleted"]}
DEL_BY_TERM = collections.defaultdict(list)
for d in RB["deleted"]:
    for t in d["terminals_before"]:
        DEL_BY_TERM[int(t["term_uid"])].append(int(d["wire_uid"]))
AFTER_TXT = [EC.norm_ocr(it["raw"]) for it in EA["items"]]


def item_text(r):
    s = r["read_text"]
    return s[s.index("'") + 1: s.rindex("'")] if "'" in s else s


def gone_after(r):
    """'gone (...)' | 'unknown which item (...)' for F1 row r, by text against the RBW Error List."""
    k = EC.norm_ocr(item_text(r))
    n_same = sum(1 for a in AFTER_TXT if a == k)
    src = "%s items[].raw (n=%d) vs %s F1 item %s read_text (errorlist_check.norm_ocr)" % (ELA, len(AFTER_TXT), FACTS, r.get("item"))
    if n_same == 0:
        return {"value": "gone (0 items with this text left after RBW)", "gone": True, "source": src}
    return {"value": "unknown which item (%d item(s) with this text left after RBW, uid unread: %s)" % (n_same, EA.get("uid_route")),
            "gone": None, "source": src}


# ------------------------------------------------------------------------------------------------ rows
ROWS = collections.OrderedDict()


def row_for_term(tu, origin):
    """Row keyed by sink terminal uid (S1 terminal first, else P5)."""
    key = "t%d" % tu
    if key not in ROWS:
        t1, t5 = G1.term.get(tu), G5.term.get(tu)
        t = t1 or t5
        ROWS[key] = {"key": key, "sink_term": tu, "node": t["owner_uid"] if t else None, "sink": None, "cdiff": None, "open": [], "el": [],
                     "origin": []}
    ROWS[key]["origin"].append(origin)
    return ROWS[key]


CDROW = {}
for r in CD["rows"]:
    s = str(r["sink"])
    rr = S1f["rows"].get(s) or Gf["rows"].get(s)
    row = row_for_term(int(rr["term_uid"]), "cdiff")
    row["cdiff"] = {"sink": s, "class": r["class"], "before": r["before"], "after": r["after"], "default_mode_row": s in rk0}
    CDROW[s] = row
for lst, at in ((L12, ln12), (L319, ln319)):
    for (n, tm) in lst:
        hit = [row for s, row in CDROW.items() if int(s.split("|")[0]) == n and s.split("|")[2] == tm]
        if not hit:
            hit = [ROWS.setdefault("open:%d|%s" % (n, tm), {"key": "open:%d|%s" % (n, tm), "sink_term": None, "node": n, "sink": None,
                                                              "cdiff": None, "open": [], "el": [], "origin": ["open"]})]
        for row in hit:
            row["open"].append(at)
EL_ITEMS = []
for r in F1:
    for k, ri in enumerate(r["read_index"]):
        iid = "EL[%d]" % ri
        it = {"id": iid, "item": r["item"], "class": r["class"], "uid": r["uid"], "kind": r["kind"], "source": r["source"][:160],
              "gone": gone_after(r)}
        EL_ITEMS.append(it)
        attached = []
        if r["kind"].startswith("node"):
            attached = [row for s, row in CDROW.items() if int(s.split("|")[0]) == int(r["uid"])]
        elif r["kind"] == "wire":
            sinks = [t for t in S1RAW["terminals"] if t["wire_uid"] == int(r["uid"]) and not t["is_source"]]
            attached = [row_for_term(int(t["term_uid"]), "el-wire") for t in sinks]
            if not attached:
                attached = [ROWS.setdefault("wire:%s" % r["uid"], {"key": "wire:%s" % r["uid"], "sink_term": None, "node": None, "sink": None,
                                                                   "cdiff": None, "open": [], "el": [], "origin": ["el-wire"]})]
        else:
            attached = [ROWS.setdefault("item:%s" % iid, {"key": "item:%s" % iid, "sink_term": None, "node": None, "sink": None, "cdiff": None,
                                                         "open": [], "el": [], "origin": ["el-item-only"]})]
        it["rows"] = [row["key"] for row in attached]
        for row in attached:
            row["el"].append(it)
gate("E1 the 47 EL items each sit on >= 1 row", len(EL_ITEMS) == 47 and all(it["rows"] for it in EL_ITEMS),
     {"items": len(EL_ITEMS), "no_row": [it["id"] for it in EL_ITEMS if not it["rows"]]})

# ------------------------------------------------------------------------------------------------ citations (read, never typed)
SR_LINES, IND_LINES = {}, {}
for p in ("plan_ring_p4_s07v18.json", "plan_ring_p4_s08v18.json"):
    with open(B + p, encoding="utf-8") as f:
        for i, ln in enumerate(f.read().split("\n"), 1):
            m = re.search(r"PD293\(b\) SR ([A-Z]) \(#(\d+)/#(\d+) on #10170, graph step_18\) new = ([^:]*): Select -> right SR inner", ln)
            if m:
                SR_LINES[m.group(1)] = {"uids": {int(m.group(2)), int(m.group(3))}, "new": m.group(4), "at": "%s%s:%d" % (B, p, i)}
            m = re.search(r"\| (PD[0-9]+\([a-z]\)(?:/PD[0-9]+\([a-z]\))*) ([^|]*?): Select -> indicator terminal t(\d+)", ln)
            if m:                                           # a Select written into an INDICATOR that a Local reads (PD298(d)/PD300(b) form)
                IND_LINES[int(m.group(3))] = {"pd": m.group(1), "what": m.group(2)[:90], "at": "%s%s:%d" % (B, p, i)}
print("FACT Select -> indicator lines %s" % json.dumps(IND_LINES), flush=True)
print("FACT PD293(b) SR lines %s" % json.dumps({k: {"uids": sorted(v["uids"]), "new": v["new"], "at": v["at"]} for k, v in SR_LINES.items()}), flush=True)
PD293B = cite(P4, "loop-1.2 shift register written by the tracking body takes `valid ? new : old`", "PD293(b)")


def sel_sr(sel_uid):
    """SR letter whose register uids take the output of Select `sel_uid` in the P5 graph (direct wire sinks), else None."""
    outs = [t for t in G5.by_owner.get(sel_uid, []) if t["is_source"]]
    sts = [x for t in outs if t["wire_uid"] for x in G5.by_wire[t["wire_uid"]] if not x["is_source"]]
    sinks = set(x["owner_uid"] for x in sts)
    for k, v in SR_LINES.items():
        if v["uids"] & sinks:
            return k, sorted(v["uids"] & sinks)
    for x in sts:
        if x["term_uid"] in IND_LINES:
            return "IND", [x["term_uid"]]
    return None, sorted(sinks)


def p5cite(tu):
    return G5.cite(tu) if tu in G5.lines else "%s terminals[term_uid=%s]" % (GF, tu)


def plan_act(p, aid):
    return cite(B + p, '"id": "%s"' % aid, "plan action %s" % aid)


PD374B = cite(P5D, "'frame index' into `#376` = 1.7's RECORD COUNTER", "PD374(b)")
PD374D_T5 = cite(P5D, "t5 ← the dequeued element", "PD374(d)/(a) queue element")
PD374D_MOVE = cite(P5D, "the not-timed-out frame holds `#376` (MOVED in)", "PD374(d)")
PD374D_OUT = cite(P5D, "so the values that leave 1.7 for `#6384` / `#2048` are those of the LAST real `#376` call", "PD374(d)")
PD379B = cite(P5D, "GAP K3/K4 — the two new SRs for `#376` t3 / t4 are kept", "PD379(b)")
PD366D = cite(P4C, "`element` ← the x-y chain (t2832), `element` ← TransPos (t4160), `element` ← RotPos (t4165)", "PD366(d)")
PD295A = cite(P4, "it is a per-frame value of loop 1.1 that must travel with its frame: a FIFTH per-slot array", "PD295(a)")
PD255E = cite(IDX, "PD255(e)/PD257(a) Per-slot `TransPos`", "PD255(e)/PD257(a)")
PD233F = cite(IDX, "PD233(f)(1)(2) Each result carries its own frame's values (now via the per-slot arrays", "PD233(f)(1)")
PD295B = cite(P4, "**(b) `#11608` and `#1359` feed the Force-vs-Extension DISPLAY only**", "U12/PD210 via PD295(b)")
B1359 = cite(SPLIT, "the #1359 output (Bundler #11310 array)", "#11310 = #1359's output")
DEF_D = cite(P6D, "D = carries no data: a termless wire, or a loose-end branch whose sinks", "PD404(c) D")
R_TAB = {
    "376|Terminal|current frame data array in|0": [PD374D_T5, plan_act("plan_ring_p5s02a.json", "w_el7_376")],
    "376|Terminal|frame index|0": [PD374B, plan_act("plan_ring_p5s02c.json", "w_c7_fi")],
    "376|Terminal|cal cluster path|0": [PD374D_MOVE, plan_act("plan_ring_p5s02a.json", "w_in1_376")],
    "376|Terminal|file size|0": [PD374D_MOVE, plan_act("plan_ring_p5s02a.json", "w_in2_376")],
    "376|Terminal|selected path|0": [PD374D_MOVE, plan_act("plan_ring_p5s02b.json", "w_in3_376")],
    "376|Terminal|error in|0": [PD374D_MOVE, plan_act("plan_ring_p5s02b.json", "w_g376")],
    "376|Terminal|total data array in|0": [PD374D_MOVE, plan_act("plan_ring_p5s02b.json", "w_h376")],
    "2048|Terminal|array|0": [PD374D_OUT],
    "6384|Terminal|error in|0": [PD374D_OUT],
    "2048|Terminal|length|0": [PD379B, plan_act("plan_ring_p5s02e.json", "w_k3f")],
    "6384|Terminal|actual # data points|0": [PD379B, plan_act("plan_ring_p5s02e.json", "w_k3f")],
    "6384|Terminal|file # to append|0": [PD379B, plan_act("plan_ring_p5s02e.json", "w_k4f")],
    "2626|Terminal|array|0": [PD366D, PD293B, plan_act("plan_ring_p4_s07v18.json", "p4_rbB_sel_t4168")],
    "2626|Terminal|element|0": [PD366D, PD295A, plan_act("plan_ring_p4_s06v18.json", "p4_w_bd_row")],
    "2626|Terminal|element|1": [PD366D, PD255E, plan_act("plan_ring_p4_s06v18.json", "p4_w_tp_row")],
    "2626|Terminal|element|2": [PD366D, PD255E, plan_act("plan_ring_p4_s06v18.json", "p4_w_rp_row")],
    "5058|Terminal|Image In|0": [PD233F, plan_act("plan_ring_p4_s05v18.json", "p4_w_img_trk")],
    "10757|Terminal|array|0": [PD293B, plan_act("plan_ring_p4_s07v18.json", "p4_rbA_sel_t10871")],
    "28083|Terminal|Magnet position|0": [PD255E, cite(B + "plan_ring_p4_s06v18.json", "(-> #28083 Magnet position, facts_c117_qrt.md:17)", "plan action into #9503 -> #28083")],
}
DISP_TAB = {"11261|Terminal|element|0": [PD295B], "11261|Terminal|array|0": [PD295B, B1359]}
DISP_TERM = {8323: [PD295B, cite(SPLIT, "11363 (← Bundler #11310) → BuildArray #11261 → **indicator #8323 'Force (pN) vs Extension (nm)'**", "#11261 -> #8323")],
             17272: [cite(B + "plan_ring_p4_s06v18.json", "#10969 -> indicator 'min value' t17272 only", "PD298(d) display-only")],
             28786: [cite(B + "plan_ring_p4_s07v18.json", "'Extension (nm) vs Time (Frame #)' graph t28786 (display)", "PD298(d) display")]}
CROW = {}
with open(CROWS, encoding="utf-8") as f:
    _cl = f.read().split("\n")
for c in CR["rows"]:
    ln = next(i for i, t in enumerate(_cl, 1) if t.strip() == '"consumer": %d,' % c["consumer"])
    CROW[(int(c["consumer"]), int(c["sink_term"]))] = {"label": "PD404(c) C: p6_crows row #%d (%s)" % (c["consumer"], c["origin"]), "at": "%s:%d" % (CROWS, ln),
                                                         "quote": '"consumer": %d' % c["consumer"]}


def classify(row):
    """(class, [citations], also[], note) for one row - first of C, R, DISP, D applies; none = U."""
    found = []
    s = row["cdiff"]["sink"] if row["cdiff"] else None
    tu, node = row["sink_term"], row["node"]
    if node is not None and tu is not None and (int(node), int(tu)) in CROW:
        found.append(("C", [CROW[(int(node), int(tu))]], ""))
    if s in R_TAB:
        found.append(("R", R_TAB[s], ""))
    elif s and row["cdiff"]["after"]:
        sels = sorted(set(int(a.split("|")[0]) for a in row["cdiff"]["after"] if "|s? t:f|" in a))
        if sels:
            cs, notes = [], []
            for su in sels:
                k, hit = sel_sr(su)
                if k == "IND":
                    il = IND_LINES[hit[0]]
                    cs.append({"label": "%s Select -> indicator terminal t%d (%s), read by a Local (#%d's output)" % (il["pd"], hit[0], il["what"], su),
                               "at": il["at"], "quote": "Select -> indicator terminal t%d" % hit[0]})
                elif k:
                    cs += [] if PD293B in cs else [PD293B]
                    cs.append({"label": "PD293(b) SR %s Select -> right SR inner (#%d's output feeds register(s) %s)" % (k, su, hit),
                               "at": SR_LINES[k]["at"], "quote": "SR %s ... Select -> right SR inner" % k})
                else:
                    notes.append("Select #%d output sinks %s match no PD293(b) SR line" % (su, hit))
            if not notes:
                found.append(("R", cs, ""))
            else:
                row["sel_note"] = notes
    if s in DISP_TAB:
        found.append(("DISP", DISP_TAB[s], ""))
    if tu in DISP_TERM:
        found.append(("DISP", DISP_TERM[tu], ""))
    wires = [it for it in row["el"] if it["kind"] == "wire"]
    for it in wires:
        w = int(it["uid"])
        if w in SH["termless"]:
            found.append(("D", [DEF_D, {"label": "wire %d termless in the P5 graph" % w, "at": "%s f1_wire_shapes.termless" % FACTS, "quote": str(w)}], ""))
        elif w in SH["source_only"] and tu is not None and direct_src(G5, tu):
            found.append(("D", [DEF_D, {"label": "wire %d source-only; its S1 sink t%d is fed elsewhere in P5 by %s" % (w, tu, direct_src(G5, tu)),
                                        "at": p5cite(tu), "quote": "term_uid %d" % tu}], ""))
    if not found and row["key"].startswith("wire:"):
        w = int(row["key"].split(":")[1])
        if w in SH["termless"]:
            found.append(("D", [DEF_D, {"label": "wire %d termless in the P5 graph" % w, "at": "%s f1_wire_shapes.termless" % FACTS, "quote": str(w)}], ""))
    order = {"C": 0, "R": 1, "DISP": 2, "D": 3}
    found = [f for f in found if all(c and c.get("at") for c in f[1])] + [("BADCITE", [c for c in f[1] if not (c and c.get("at"))], f[0])
                                                                          for f in found if not all(c and c.get("at") for c in f[1])]
    good = sorted([f for f in found if f[0] in order], key=lambda f: order[f[0]])
    bad = [f for f in found if f[0] == "BADCITE"]
    if not good:
        return "U", [], [], bad
    cls = good[0][0]
    also = sorted(set(f[0] for f in good[1:] if f[0] != cls), key=lambda c: order[c])
    return cls, good[0][1], also, bad


BADCITES = []
for row in ROWS.values():
    tu = row["sink_term"]
    t5, t1 = (G5.term.get(tu), G1.term.get(tu)) if tu is not None else (None, None)
    t = t1 or t5
    if t:
        lp = loop_of(t5["frame_diagram"]) if t5 else ("absent from the P5 graph", "")
        row["sink"] = {"value": "#%s %s, t%s '%s'" % (t["owner_uid"], t["owner_class"], tu, t["term_name"]), "loop": lp[0], "chain": lp[1],
                       "source": "%s; %s; loop: %s owners/fs_measured (diag_c108c_graph.Graph.struct_outer)" % (
                           s1cite(tu) if t1 else "S1: absent", p5cite(tu) if t5 else "P5: absent", GF)}
    elif row["key"].startswith("open:"):
        row["sink"] = {"value": "node #%s '%s' (no cdiff row, no terminal read)" % (row["node"], row["key"].split("|", 1)[1]), "loop": "unread", "chain": "",
                       "source": "%s" % ln12}
    elif row["key"].startswith("wire:"):
        row["sink"] = {"value": "wire %s: no S1 terminal row (sink unread)" % row["key"][5:], "loop": "unread", "chain": "",
                       "source": "%s terminals[wire_uid=%s] (none)" % (S1F, row["key"][5:])}
    else:
        it = row["el"][0]
        row["sink"] = {"value": "item-only (%s, class %s): uid unread" % (it["id"], it["class"]), "loop": "unread", "chain": "", "source": it["source"]}
    cd = row["cdiff"]
    row["s1_source"] = {"effective": cd["before"] if cd else None, "direct": direct_src(G1, tu) if tu is not None else None,
                        "source": ("computation_diff row '%s' before (vigraph.effective_sources, frame-keyed)" % cd["sink"] if cd else "") +
                        ("; direct: %s" % s1cite(tu) if tu is not None and tu in G1.term else "") or "unread (no sink terminal)"}
    row["p5_source"] = {"effective": cd["after"] if cd else None, "direct": direct_src(G5, tu) if tu is not None else None,
                        "source": ("computation_diff row '%s' after" % cd["sink"] if cd else "") +
                        ("; direct: %s" % p5cite(tu) if tu is not None and tu in G5.term else "") or "unread (no sink terminal)"}
    cls, cits, also, bad = classify(row)
    BADCITES += [(row["key"], b) for b in bad]
    row["class"], row["citation"], row["also"] = cls, cits, also
    w_el = sorted(set(int(it["uid"]) for it in row["el"] if it["kind"] == "wire" and int(it["uid"]) in DEL))
    w_t = sorted(set(DEL_BY_TERM.get(tu, []))) if tu is not None else []
    row["rbw"] = {"value": sorted(set(w_el + w_t)) or "none",
                  "detail": ["w%d %s (%s)" % (w, DEL[w]["tag"], "termless" if DEL[w]["termless"] else "%d src / %d sink" % (DEL[w]["n_src"], DEL[w]["n_sink"]))
                             for w in sorted(set(w_el + w_t))],
                  "source": "%s deleted[] (wire_uid = the row's EL wire, or terminals_before term_uid = the sink t%s)" % (RBW, tu)}
    gs = [it["gone"]["gone"] for it in row["el"]]
    row["el_gone"] = {"value": ("no EL item" if not row["el"] else "; ".join("%s: %s" % (it["id"], it["gone"]["value"]) for it in row["el"])),
                      "all_gone": (None if not row["el"] else (True if all(g is True for g in gs) else (None if any(g is None for g in gs) else False))),
                      "source": row["el"][0]["gone"]["source"] if row["el"] else "no EL item on this row"}
gate("E4 every row has one class; every non-U class has resolved citations (file:line read from the file)",
     all(r["class"] in ("R", "DISP", "D", "C", "U") for r in ROWS.values()) and all(r["class"] == "U" or all(c.get("at") for c in r["citation"]) for r in ROWS.values())
     and not BADCITES, {"bad_citations": [(k, str(b)[:200]) for k, b in BADCITES]})
nosrc = [r["key"] for r in ROWS.values() if not (r["sink"] and r["sink"].get("source") and r["s1_source"]["source"] and r["p5_source"]["source"]
                                                    and r["rbw"]["source"] and r["el_gone"]["source"])]
gate("E5 every cell has a source", not nosrc, nosrc or "all %d rows" % len(ROWS))

# ------------------------------------------------------------------------------------------------ counts + outputs
CNT = collections.Counter(r["class"] for r in ROWS.values())
U_ROWS = [r["key"] for r in ROWS.values() if r["class"] == "U"]
C_ROWS = [r["key"] for r in ROWS.values() if r["class"] == "C"]
GONE_ROWS = [r["key"] for r in ROWS.values() if r["el_gone"]["all_gone"] is True]
UNK_ROWS = [r["key"] for r in ROWS.values() if r["el"] and r["el_gone"]["all_gone"] is None]
ITEMS_GONE = sum(1 for it in EL_ITEMS if it["gone"]["gone"] is True)
ITEMS_UNK = [it["id"] for it in EL_ITEMS if it["gone"]["gone"] is None]
SUM = {"rows": len(ROWS), "per_class": dict(CNT), "U_rows": U_ROWS, "C_rows": C_ROWS, "DISP_count": CNT.get("DISP", 0),
       "rows_el_gone_after_rbw": len(GONE_ROWS), "rows_el_unknown": UNK_ROWS, "rows_without_el_item": sum(1 for r in ROWS.values() if not r["el"]),
       "el_items_gone": ITEMS_GONE, "el_items_unknown": ITEMS_UNK, "el_items": len(EL_ITEMS)}
print("FACT summary %s" % json.dumps(SUM), flush=True)
OUT = {"schema": "p6-closure/1", "card": "167-a1-3", "plan": "docs/d1/ring-p6.md:63-67,77-81 PD404(c)(e)",
       "inputs": {"p5_graph": {"path": GF, "md5": L.md5(GF)}, "s1": {"path": S1F, "md5": L.md5(S1F)}, "plan": {"path": PLAN, "md5": L.md5(PLAN)},
                  "facts": {"path": FACTS, "md5": L.md5(FACTS)}, "rbw": {"path": RBW, "md5": L.md5(RBW)}, "el_after": {"path": ELA, "md5": L.md5(ELA)},
                  "crows": {"path": CROWS, "md5": L.md5(CROWS)}},
       "cdiff_call": "vigraph.computation_diff(stagekit.s1_frame_graph(node_labels_default), vigraph.build4(P5 terminals, objs, loops, labels, "
                     "fs_tunnel_pairs, frame_keyed=True)); default mode: jev_candidates.load(S1) vs build4(..., frame_keyed=False)",
       "classes": "PD404(c): C, R, DISP, D in that order; no citation = U; 'also' = the other classes that apply",
       "equality": EQ, "summary": SUM, "el_items": EL_ITEMS,
       "rows": [dict((k, v) for k, v in r.items() if k != "el") for r in ROWS.values()],
       "row_el": {r["key"]: [it["id"] for it in r["el"]] for r in ROWS.values()}}
json.dump(OUT, open(OUT_JS, "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)


def cell(x, n=150):
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, default=str)
    return s.replace("|", "\\|").replace("\n", " ")[:n]


md = ["---", "type: facts", "status: current", "date: 2026-10-12", "card: 167-a1-3", "---",
      "# P6-0 closure table (PD404(c)(e), `docs/d1/ring-p6.md:63-67,77-81`) - facts only, classes by citation, no fix, no verdict",
      "Written by `tools/bench/diag_c167_a1_3_closure.py` (offline, stored json; LabVIEW reads 0). Machine rows with every cell's `source`: "
      "`tools/bench/p6_closure.json`. Rows = 47 EL items (F1) + both `open_rows` lists + frame-keyed `computation_diff(S1, 7815af09)`.", "",
      "## Set equality: open_rows vs computation_diff", "",
      "- open_rows list 1 at `%s`: %d (node, term) pairs; list 2 at `%s`: %d pairs; equal as sets: %s." % (ln12, len(L12), ln319, len(L319), EQ["lists_equal"]),
      "- frame-keyed cdiff: %d rows = %d pairs; only in cdiff: %s; only in open_rows: %s; equal: %s." % (
          len(rk), len(pairs_cd), EQ["cdiff_frame_keyed"]["only_cdiff"], EQ["cdiff_frame_keyed"]["only_open"], EQ["cdiff_frame_keyed"]["equal"]),
      "- the cdiff-only rows = the PB rows RECORDED by the P5 scratch (`%s`): %s." % (EQ["recorded_pb_rows"]["at"], rec_sinks),
      "- default-mode cdiff (not frame-keyed): %d rows = %d pairs; only in cdiff: %s; only in open_rows: %s; equal: %s." % (
          len(rk0), len(pairs_cd0), EQ["cdiff_default"]["only_cdiff"], EQ["cdiff_default"]["only_open"], EQ["cdiff_default"]["equal"]), "",
      "## Counts", "",
      "- rows %d; per class %s; DISP count %d (PD404(b)); rows without an EL item %d." % (len(ROWS), dict(CNT), CNT.get("DISP", 0), SUM["rows_without_el_item"]),
      "- EL items gone after RBW: %d of 47; unknown which item: %s. Rows whose EL item(s) are all gone after RBW: %d; rows with an unknown item: %d." % (
          ITEMS_GONE, ITEMS_UNK, len(GONE_ROWS), len(UNK_ROWS)),
      "- C rows: %s" % C_ROWS, "- U rows (%d):" % len(U_ROWS)]
for k in U_ROWS:
    r = ROWS[k]
    md.append("  - `%s` %s | %s | S1 %s | P5 %s" % (k, cell(r["sink"]["value"], 90), r["sink"]["loop"], cell(r["s1_source"]["effective"] or r["s1_source"]["direct"], 110),
                                                 cell(r["p5_source"]["effective"] or r["p5_source"]["direct"], 110) + (" | %s" % r["sel_note"] if r.get("sel_note") else "")))
md += ["", "## Table", "",
       "| row | sink | loop | S1 source | P5-final source | class | citation | also | RBW wire | EL item(s) -> after RBW |", "|---|---|---|---|---|---|---|---|---|---|"]
for r in ROWS.values():
    md.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        r["key"], cell(r["sink"]["value"], 80), r["sink"]["loop"], cell(r["s1_source"]["effective"] or r["s1_source"]["direct"], 120),
        cell(r["p5_source"]["effective"] or r["p5_source"]["direct"], 120), r["class"],
        cell("; ".join("%s `%s`" % (c["label"], c["at"]) for c in r["citation"]) or "none", 300), ",".join(r["also"]) or "-",
        cell(r["rbw"]["detail"] or "none", 120), cell(r["el_gone"]["value"], 200)))
md += ["", "Sources per cell: `p6_closure.json` rows[].{sink,s1_source,p5_source,citation,rbw,el_gone}.source. Words: 'unknown which item' = an item of the",
       "same text is still in the RBW Error List and no item uid is read (`%s`)." % EA.get("uid_route")]
open(OUT_MD, "w", encoding="utf-8").write("\n".join(md) + "\n")
gate("O outputs written", os.path.isfile(OUT_JS) and os.path.isfile(OUT_MD), {"json": L.md5(OUT_JS), "md": L.md5(OUT_MD)})
print("FACT %s md5 %s ; %s md5 %s" % (OUT_JS, L.md5(OUT_JS), OUT_MD, L.md5(OUT_MD)), flush=True)

# ------------------------------------------------------------------------------------------------ after
print("== after", flush=True)
H.check(gate, "after")
sys.exit(gate.result([{"path": OUT_JS, "md5": L.md5(OUT_JS)}, {"path": OUT_MD, "md5": L.md5(OUT_MD)}]))
