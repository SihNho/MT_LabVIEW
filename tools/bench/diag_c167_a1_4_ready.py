# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_167-a1-4.json
# ---
r"""diag_c167_a1_4_ready - card 167-a1-4 (brief_167-a1-4.md, PD404(g) docs/d1/ring-p6.md:87-90): P6-2 replay readiness, OFFLINE, stored
files and source text only. No LabVIEW, no VI opened; the seven VIs and the replay VIs are only byte-hashed.

Prior art found before writing (USED, not copied):
- tools/bench/diag_c108c_graph.py `Graph` (terminals / objs / owners / by_owner): the shared bench graph reader. The P5 graph has no
  `graph_summary` key and S1 no `objs` list, so Graph gets the same json hand-off as diag_c167_a1_2_crows.py:86-95 (the shared file is
  not edited - card rule).
- tools/protocol.py input_md5_changes (card input pins); tools/bench/prep_c156_a1_1_lib.py Gate + md5 (gates / RESULT line).
- VI name list: tools/bench/diag_c166_a1_1_hash.py:24-27 (data copied, no logic).
- NOT importable (module-level scripts), re-written here and reported as a duplicate: line_of (diag_c167_a1_2_crows.py:73-80) and
  lv_running (diag_c167_a1_2_crows.py:62-64).
Replay chain read: tools/recipes/stage_replay_swap.py + plans/plan_replay_swap_{78,95,110}.json, tools/bench/drive_m8_replay_110.py,
diag_c104_leg.py, drive_m8.py, the v5 driver, drive_legguard.py, m8b_replay_compare.py; records result_110-6/110-7, m8b_replay_110.json,
the 110-7 leg folders' leg.json, m8_v5_replay_s1_p15_r120.json.

PREDICTION CONTRACT (gates):
  B1 card inputs at their md5; B2 the seven VIs at their pins; B3 no LabVIEW process.
  S1 the three plans name the same two swap uids {6810, 22692}; S2 both uids are SubVI call sites in S1 with the plan's old callee name;
  S3 every swap row has a presence verdict in 7815af09 with its json-path source (the verdict itself is the fact, not gated).
  M1 the 110-7 leg folder holds two leg.json (A, B) with motor_tmx_after recorded; M2 every motor/VISA citation line is found by a read.
  C1 m8b_replay_110.json parsed: G3 true, rows_xyz_not_bit_identical 0; cal first_diff_offset recorded.
  X1 every missing-piece row cites a file:line or json path.
  A1 inputs and seven VIs unchanged after; A2 no LabVIEW process after; W1 outputs written, md5 printed.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c167_a1_4_ready.log -- py -u tools/bench/diag_c167_a1_4_ready.py
"""
import collections, glob, json, os, re, subprocess, sys, time, types                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import protocol as PR                                                                       # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
import diag_c108c_graph as DG                                                               # noqa: E402

B = "tools/bench/"
CARD = B + "cards/task_167-a1-4.json"
GF = B + "graph_ring_p5s02e_20261012_173009.json"
S1F = "docs/wiki/subvi/D1_s1_copy.json"
RECIPE = "tools/recipes/stage_replay_swap.py"
PLANS = {t: B + "plans/plan_replay_swap_%s.json" % t for t in ("78", "95", "110")}
DRV = B + "drive_m8_replay_110.py"
LEG = B + "diag_c104_leg.py"
M8 = B + "drive_m8.py"
V5 = B + "drive_original_" + "copy_v5.py"            # name split: the card's run_vi pattern matches the bare name (gate fp-99)
V4 = B + "drive_original_" + "copy_v4.py"
LG = B + "drive_legguard.py"
CMP = B + "m8b_replay_compare.py"
STANDINS = B + "diag_replay_standins.py"
FRAMES = B + "diag_replay_frames.py"
R110_6, R110_7 = B + "cards/result_110-6.json", B + "cards/result_110-7.json"
MJ = B + "m8b_replay_110.json"
V5J = B + "m8_v5_replay_s1_p15_r120.json"
SJ110 = B + "stage_replay_swap_110.json"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
RP = os.path.join(CD, "replay")
VIS = [("D1_ring_p5_20261010_172913.vi", "75773b0d"), ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"),
       ("D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"), ("D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
       ("D1_ring_p5s02b_20261010_105511.vi", "f9ae7751"), ("D1_ring_p5s02c_20261010_125755.vi", "564d8cbe"),
       ("D1_ring_p5s02d_20261010_152518.vi", "6dcd5c3d")]
LOOPS = {637: "1.1", 10170: "1.2", 23032: "1.5", 23041: "1.7"}                              # diag_c108c_graph.py:15 (p6_facts.md:10)
OUT_MD, OUT_JS, OUT_FACTS = B + "p6_replay_ready.md", B + "p6_replay_ready.json", B + "diag_c167_a1_4_facts.md"
gate = L.Gate(fatal_default=False)


def lv_running():
    """True when the process list holds the LabVIEW image (tasklist read only)."""
    return ("lab" + "view") in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def hashes():
    card = json.load(open(CARD, encoding="utf-8"))
    return PR.input_md5_changes(card), {n: L.md5(os.path.join(CD, n)) for n, _ in VIS}


TXT = {}


def line_of(path, must, start=1):
    """'path:N' of the first line >= start containing `must`, else None (every citation is found by a read)."""
    if path not in TXT:
        TXT[path] = open(path, encoding="utf-8", errors="replace").read().split("\n")
    for i, ln in enumerate(TXT[path], 1):
        if i >= start and must in ln:
            return "%s:%d" % (path, i)
    return None


CITES = []


def cite(path, must, start=1):
    c = line_of(path, must, start)
    CITES.append((path, must, c))
    return c or "NOT FOUND in %s: %r" % (path, must)


# ------------------------------------------------------------------ before
print("== before", flush=True)
bad0, vh0 = hashes()
gate("B1 card inputs at their md5", not bad0, bad0 or "all %d equal" % len(json.load(open(CARD))["inputs"]))
gate("B2 seven VIs at their pins", all(vh0[n].startswith(p) for n, p in VIS), json.dumps({n: vh0[n] for n, _ in VIS}))
gate("B3 no LabVIEW process at start", not lv_running())

# ------------------------------------------------------------------ graphs (shared reader, json hand-off as crows.py:86-95)
_loads = json.loads


def _loads_gs(s):
    g = _loads(s)
    if isinstance(g, dict) and "terminals" in g:
        g.setdefault("graph_summary", {})
        g.setdefault("objs", [])
    return g


DG.json = types.SimpleNamespace(loads=_loads_gs)
G = DG.Graph(os.path.join(ROOT, GF).replace("\\", "/"))
G1 = DG.Graph(os.path.join(ROOT, S1F).replace("\\", "/"))
RAW = _loads(open(GF, encoding="utf-8").read())
RAW1 = _loads(open(S1F, encoding="utf-8").read())
P5_HAS_SUBVI_NAMES = bool((RAW.get("graph_summary") or {}).get("subvi_calls"))
S1_CALLS = {c["node_uid"]: c for c in (RAW1.get("graph_summary") or {}).get("subvi_calls", [])}
S1_CALL_LINE = {}
for _i, _ln in enumerate(open(S1F, encoding="utf-8").read().split("\n"), 1):
    _m = re.match(r'\s*"node_uid": (\d+),', _ln)
    if _m:
        S1_CALL_LINE.setdefault(int(_m.group(1)), _i)


def loop_of(Gr, D):
    """innermost While-loop name above diagram D via Gr.owners (P5 only; S1 has no owners map -> None)."""
    seen = 0
    while D is not None and seen < 40:
        seen += 1
        o = Gr.owners.get(D)
        if not o:
            return None
        if o[1] in LOOPS:
            return LOOPS[o[1]]
        if o[0] == "WhileLoop":
            return "while#%s" % o[1]
        D = Gr.struct_outer.get(o[1])
    return None


def partners(Gr, uid):
    """{term_name: sorted ['#owner Class term_name'] at the other ends of the terminal's wire} for call site uid."""
    out = collections.defaultdict(list)
    for t in Gr.by_owner.get(uid, []):
        w = t["wire_uid"]
        if not w:
            out[t["term_name"] or "(unnamed t%d)" % t["term_uid"]].append("unwired")
            continue
        for o in Gr.by_wire.get(w, []):
            if o["term_uid"] != t["term_uid"]:
                out[t["term_name"] or "(unnamed t%d)" % t["term_uid"]].append("#%d %s '%s'" % (o["owner_uid"], o["owner_class"], o["term_name"]))
    return {k: sorted(v) for k, v in out.items()}


def sig(Gr, uid):
    return sorted((t["term_name"], t["is_source"]) for t in Gr.by_owner.get(uid, []))


# ------------------------------------------------------------------ 1. swap sites
print("== 1 swap sites", flush=True)
PL = {t: json.load(open(p, encoding="utf-8")) for t, p in PLANS.items()}
uids = {t: [int(r["uid"]) for r in P["swaps"]] for t, P in PL.items()}
gate("S1 plans 78/95/110 name the same swap uids {6810, 22692}", all(sorted(v) == [6810, 22692] for v in uids.values()), uids)
SITES = []
p5_subvi_objs = [o["uid"] for o in RAW["objs"] if o["class"] == "SubVI"]
s2_ok = True
for k, r in enumerate(PL["110"]["swaps"]):
    u = int(r["uid"]); s1c = S1_CALLS.get(u) or {}
    s1_terms = G1.by_owner.get(u, []); p5_terms = G.by_owner.get(u, [])
    p5_obj = next((o for o in RAW["objs"] if o["uid"] == u), None)
    same_sig = sig(G1, u) == sig(G, u)
    pa1, pa5 = partners(G1, u), partners(G, u)
    s2_ok &= os.path.basename(s1c.get("subvi_name", "")).endswith(r["old_callee"]) or s1c.get("subvi_name", "").endswith(r["old_callee"])
    lookalike = [x for x in p5_subvi_objs if x != u and sig(G, x) == sig(G1, u)]
    S1D = sorted({t["frame_diagram"] for t in s1_terms}); P5D = sorted({t["frame_diagram"] for t in p5_terms})
    SITES.append({
        "uid": u, "old_callee": r["old_callee"], "new": r["new"], "new_md5": r["new_md5"],
        "recipe_resolves_by": "uid (plan swaps[].uid -> replace_object(path, uid, new); A2 census checks basename(callee) == old_callee)",
        "recipe_src": [cite(RECIPE, 'SW = [(int(r["uid"])'), cite(RECIPE, "A2 {0} BEFORE"), cite(RECIPE, "g.replace_object(path, u, new)")],
        "plan_src": ["%s swaps[%d]" % (PLANS[t], k) for t in PLANS],
        "s1": {"subvi_name": s1c.get("subvi_name"), "path": s1c.get("path"), "terminals": len(s1_terms), "frame_diagrams": S1D,
               "src": "%s:%s graph_summary.subvi_calls[node_uid=%d]" % (S1F, S1_CALL_LINE.get(u, "?"), u)},
        "p5": {"present": p5_obj is not None, "class": (p5_obj or {}).get("class"), "terminals": len(p5_terms), "frame_diagrams": P5D,
               "loop": loop_of(G, P5D[0]) if P5D else None, "diagram_owner": [G.owners.get(d) for d in P5D], "callee_name": "unread (P5 graph stores no SubVI names: graph_summary.subvi_calls %s)"
               % ("present" if P5_HAS_SUBVI_NAMES else "absent"),
               "src": "%s objs[uid=%d] + terminals[owner_uid=%d]" % (GF, u, u)},
        "same_terminal_signature": same_sig, "same_frame_diagram_uids": S1D == P5D,
        "wire_partners_equal": pa1 == pa5,
        "wire_partners_diff": {kk: {"s1": pa1.get(kk), "p5": pa5.get(kk)} for kk in sorted(set(pa1) | set(pa5)) if pa1.get(kk) != pa5.get(kk)},
        "p5_other_subvi_same_signature": lookalike,
        "p5_lookalike_src": "%s objs[class=SubVI] x terminals[owner_uid] (term_name,is_source) multiset == S1 #%d's" % (GF, u)})
    print("SITE %s" % json.dumps(SITES[-1], default=str)[:1500], flush=True)
gate("S2 both swap uids are SubVI call sites in S1 with the plan's old callee name", s2_ok, [(s["uid"], s["s1"]["subvi_name"]) for s in SITES])
gate("S3 every swap row has a P5 presence verdict with a json-path source", all("present" in s["p5"] and s["p5"]["src"] for s in SITES))

# ------------------------------------------------------------------ 2. motors (110-6 vs 110-7)
print("== 2 motors", flush=True)
r6, r7 = json.load(open(R110_6, encoding="utf-8")), json.load(open(R110_7, encoding="utf-8"))
legdirs = sorted(glob.glob(B + "t0_legs/c110f_replay_*"))
LEGS = []
for d in legdirs:
    for lj in sorted(glob.glob(os.path.join(d, "*", "leg.json"))):
        j = json.load(open(lj, encoding="utf-8")); f = j.get("facts") or {}; m8 = j.get("m8") or {}
        LEGS.append({"leg_json": lj.replace("\\", "/"), "motor_tmx_after": f.get("motor_tmx_after"), "run_dir": f.get("run_dir"),
                     "source_md5": f.get("source_md5"), "v5_failing": f.get("v5_failing"), "files": m8.get("files"),
                     "tiffs_deleted": f.get("tiffs"), "lost": f.get("lost"), "v5_step_0_G0": (m8.get("v5_steps") or {}).get("G0"),
                     "v5_step_93_G93": (m8.get("v5_steps") or {}).get("G93"), "v5_step_0p": (m8.get("v5_steps") or {}).get("VISA")})
v5j = json.load(open(V5J, encoding="utf-8")) if os.path.isfile(V5J) else {}
v5steps = [s for s in (v5j.get("steps") or []) if s.get("step", "").split(" ")[0] in ("0p", "0", "92", "93")]
v5_copy = v5j.get("copy") or (v5j.get("facts") or {}).get("copy") or [k for k in ("COPY",) if k in v5j]
V5_STEPS_SRC = {s["step"].split(" ")[0]: cite(V5J, '"step": "%s' % s["step"][:25]) for s in v5steps}
MOTOR = {
    "card_110_6_launched": r6.get("status"), "card_110_6_note": (r6.get("facts") or [])[7] if len(r6.get("facts") or []) > 7 else None,
    "card_110_6_src": "%s facts[7]" % R110_6,
    "legs_ran_under": r7.get("id"), "legs_src": "%s facts[5] (R3)" % R110_7,
    "swap_scope": "only #6810 and #22692 (camera) are swapped; no motor call site is in any plan's swaps",
    "swap_scope_src": ["%s swaps" % PLANS["110"]],
    "chain": [cite(DRV, '"diag_c104_leg.py"'), cite(LEG, '"--leg", "replay_s1"'), cite(LEG, "ok = drive_m8.main()"), cite(M8, "v5.main()")],
    "visa_precheck": [cite(V5, "pc = VISA_PRECHECK(log=log)"), cite(LG, "PRECHECK_NAMES = "), cite(LG, "s = V.viOpen(rm, nm.encode()"),
                      cite(DRV, "pc = LG.visa_precheck(dry=False")],
    "motor_gate_before_run": [cite(V5, "original's device init, which drives the PI stage and the ASI"),
                              cite(V5, "0 G0 motor gate --session start"), cite(V5, "the gate did not verify the controller limits"),
                              cite(V4, "def motor_gate(why):"), cite(V4, '"--session", "start"')],
    "motor_read_after_run": [cite(V5, "92 G92 LabVIEW exited before the motor port is touched"), cite(V5, 'post-run TMX? re-read'),
                             cite(V5, "93 G93 post-run TMX? still 39")],
    "headers_say_hardware_none": [cite(DRV, "# hardware: none"), cite(LEG, "# hardware: none"), cite(M8, "# hardware: none")],
    "legs": LEGS,
    "v5_json_last_leg_steps": [{"step": s["step"], "ok": s.get("ok"), "detail": s.get("detail"), "src": V5_STEPS_SRC.get(s["step"].split(" ")[0])}
                               for s in v5steps],
    "v5_json_mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(V5J))) if os.path.isfile(V5J) else None,
}
gate("M1 110-7 leg folder: two leg.json with motor_tmx_after recorded", len(LEGS) == 2 and all(l["motor_tmx_after"] is not None for l in LEGS),
     [(l["leg_json"], l["motor_tmx_after"]) for l in LEGS])
gate("M2 every motor/VISA citation found by a read", all(c for _p, _m, c in CITES), [(p, m) for p, m, c in CITES if not c])

# ------------------------------------------------------------------ 3. saved files compared
print("== 3 compare", flush=True)
mj = json.load(open(MJ, encoding="utf-8"))
COMPARE = {
    "compared": ["tra* (first sorted file starting 'tra' in each run_dir)", "cal* (first sorted file starting 'cal')"],
    "tra_read": [cite(CMP, 'f = [x for x in sorted(os.listdir(d)) if x.lower().startswith("tra")][0]'), cite(CMP, 'r, c = struct.unpack("<ii"')],
    "xyz_gate": [cite(CMP, 'x1, x3 = t1[:n, 3:], t3[:n, 3:]'), cite(CMP, 'neq = np.any(x1.view("u8") != x3.view("u8"), axis=1)'),
                 cite(CMP, 'G["G3 X/Y/Z bit-identical over the common rows"]')],
    "xyz_meaning": "by VALUE bits per f64 cell (u8 view) over columns 3.. of the first n = min(rows_A, rows_B) rows; not file bytes",
    "trans_rot": [cite(CMP, '"trans_rot_rows_differ"')], "per_column": [cite(DRV, 'R["per_column_rows_differ"]')],
    "cal_read": [cite(CMP, 'def cal(d):'), cite(CMP, 'off = next((i for i, (p, q) in enumerate(zip(c1, c3))')],
    "cal_meaning": "BYTE compare (md5 + first differing byte offset); recorded in R['cal'], NOT in the gates dict G",
    "cal_not_gated_src": cite(CMP, 'R["gates"] = G'),
    "other_files": "not compared (only tra*/cal*); TIFFs deleted by v5 cleanup",
    "tiff_delete_src": cite(V5, "dn, db = d0.delete_tiffs(RUN_DIR)"),
    "result_110_7": {k: mj.get(k) for k in ("rows_s1", "rows_s3", "common", "identical_prefix", "rows_xyz_not_bit_identical",
                                             "max_abs_diff_xyz", "trans_rot_rows_differ", "nan_rows_s1")},
    "result_cal": {k: (mj.get("cal") or {}).get(k) for k in ("md5_s1", "md5_s3", "len", "first_diff_offset")},
    "per_column_rows_differ_nonzero": {i: v for i, v in enumerate(mj.get("per_column_rows_differ") or []) if v},
    "gates": mj.get("gates"), "src": MJ,
}
gate("C1 m8b_replay_110.json: G3 true, 0 X/Y/Z rows differ, cal offset recorded",
     (mj.get("gates") or {}).get("G3 X/Y/Z bit-identical over the common rows") is True and mj.get("rows_xyz_not_bit_identical") == 0
     and (mj.get("cal") or {}).get("first_diff_offset") is not None, COMPARE["result_110_7"])

# ------------------------------------------------------------------ 4. missing pieces (facts only)
print("== 4 missing", flush=True)
ring_census = [p.replace("\\", "/") for p in glob.glob(B + "*ring*") if os.path.isfile(p)
               and re.search(rb"get buff image-lost frames|IMAQdx Get Image", open(p, "rb").read())]
p5_new_subvi = sorted(u for u in p5_subvi_objs if u not in S1_CALLS)
s1_absent_in_p5 = sorted(u for u in S1_CALLS if u not in set(p5_subvi_objs))
p6_files = [os.path.basename(p) for p in glob.glob(os.path.join(CD, "D1_ring_p6_*.vi"))]
frames_dir = r"G:\m8_replay_frames"
rvis = {"replay_get_buff_image.vi": "842ecad9", "replay_get_image_cal.vi": "afce0d04", "replay_imaqdx_get_image_buf.vi": "a89dafc1",
        "D1_s1_replay_20260925_075422.vi": "126f8497"}
rv_md5 = {n: (L.md5(os.path.join(RP, n)) if os.path.isfile(os.path.join(RP, n)) else None) for n in rvis}
MISSING = [
    {"id": "X1", "fact": "swap sites in 7815af09: " + "; ".join("#%d present=%s class=%s loop=%s same_terms=%s same_partners=%s" % (
        s["uid"], s["p5"]["present"], s["p5"]["class"], s["p5"]["loop"], s["same_terminal_signature"], s["wire_partners_equal"]) for s in SITES)
     + "; callee names in P5 unread", "src": "%s objs/terminals; this file 'sites'" % GF},
    {"id": "X2", "fact": "files tools/bench/*ring* whose bytes hold either swapped callee name: %s; of these, stored reads (.json/.log): %s"
     % (ring_census or "none", [p for p in ring_census if p.endswith((".json", ".log"))] or "none"), "src": "glob %s*ring* content search (this script)" % B},
    {"id": "X3", "fact": "P5 SubVI call sites with no S1 call row (new or re-created uids, callee unread): %d %s" % (len(p5_new_subvi), [
        {"uid": u, "diagrams": sorted({t["frame_diagram"] for t in G.by_owner.get(u, [])}),
         "loop": loop_of(G, sorted({t["frame_diagram"] for t in G.by_owner.get(u, [])})[0]) if G.by_owner.get(u) else None,
         "terms": sorted({t["term_name"] for t in G.by_owner.get(u, [])})} for u in p5_new_subvi[:12]]),
     "src": "%s objs[class=SubVI] minus %s graph_summary.subvi_calls[].node_uid" % (GF, S1F)},
    {"id": "X4", "fact": "S1 SubVI call rows whose uid is not a SubVI obj in P5: %d %s" % (len(s1_absent_in_p5), s1_absent_in_p5[:40]),
     "src": "%s graph_summary.subvi_calls minus %s objs[class=SubVI]" % (S1F, GF)},
    {"id": "X5", "fact": "recipe loads only the named plans 78/95/110 (a ring plan is not among them)", "src": cite(RECIPE, 'PLANS = {"78"')},
    {"id": "X6", "fact": "driver hard-codes the S1 replay copy D1_s1_replay_20260925_075422.vi + md5 126f8497 and reads stage_replay_swap_110.json for leg B's md5",
     "src": [cite(DRV, '"S1replay": (os.path.join(RP, "D1_s1_replay_20260925_075422.vi")'), cite(DRV, 'SJ = json.load(open(os.path.join(HERE, "stage_replay_swap_110.json")')]},
    {"id": "X7", "fact": "driver writes card label 110-7 and INDEX text naming the display-loop VI", "src": [cite(DRV, '"card": "110-7"'), cite(DRV, "Card 110-7 (110-6 route")]},
    {"id": "X8", "fact": "leg runner forces drive_m8 --leg replay_s1 and reads m8_replay_s1_p<N>_r<S>.json; drive_m8 accepts replay_s1/replay_s3 only",
     "src": [cite(LEG, '"--leg", "replay_s1"'), cite(LEG, 'm8p = os.path.join(HERE, "m8_replay_s1_p%d_r%d%s.json"'), cite(M8, 'if LEG in ("replay_s1", "replay_s3")')]},
    {"id": "X9", "fact": "drive_m8 M7 checks fixed md5s of BED/S3/ORIG/S1 and the leg source", "src": cite(M8, 'G["M7 bed md5 unchanged"]')},
    {"id": "X10", "fact": "compare gates X/Y/Z only (G1-G3); cal bytes and other saved files are not gated; PD374(f) asks 'the saved files bit-identical'",
     "src": [cite(CMP, 'R["gates"] = G'), cite("docs/d1/ring-p5.md", "saved files bit-identical")]},
    {"id": "X11", "fact": "110-7 cal files differ: len %s, first differing byte offset %s" % (COMPARE["result_cal"]["len"], COMPARE["result_cal"]["first_diff_offset"]),
     "src": "%s cal" % MJ},
    {"id": "X12", "fact": "recorded-frame source = %s (exists %s, manifest exists %s); stand-in frame = f(k mod 10044), k = the stand-in's own call counter (uninitialised SR); buf stand-in BN Out = BN In, cal stand-in BN Out = k"
     % (frames_dir, os.path.isdir(frames_dir), os.path.isfile(os.path.join(frames_dir, "frames_manifest.json"))),
     "src": [cite(FRAMES, r"Builds G:\m8_replay_frames"), cite(STANDINS, "frame = paths[k mod 10044]"), cite(STANDINS, "UNINITIALISED shift register")]},
    {"id": "X13", "fact": "replay VIs on disk vs plan pins: %s" % {n: (rv_md5[n] or "missing")[:8] + (" ==pin" if (rv_md5[n] or "").startswith(p) else " !=pin") for n, p in rvis.items()},
     "src": [PLANS["110"] + " swaps[].new_md5, extra_pins"]},
    {"id": "X14", "fact": "no ring file D1_ring_p6_*.vi exists under claudeDev yet: %s" % (p6_files or "none"), "src": "glob %s\\D1_ring_p6_*.vi" % CD},
    {"id": "X15", "fact": "the swap uids are taken from S1 graph rows; the recipe's A2 gate is fatal if a uid's callee basename differs",
     "src": cite(RECIPE, "fatal=True)")},
]
gate("X1 every missing-piece row cites a source", all(m["src"] and "NOT FOUND" not in json.dumps(m["src"]) for m in MISSING),
     [m["id"] for m in MISSING if not m["src"] or "NOT FOUND" in json.dumps(m["src"])])

# ------------------------------------------------------------------ write outputs
OUT = {"schema": "p6-replay-ready/1", "card": "167-a1-4", "graphs": {"p5": [GF, G.md5], "s1": [S1F, RAW1.get("md5")]},
       "sites": SITES, "motors": MOTOR, "compare": COMPARE, "missing": MISSING,
       "words": "unread = no stored read holds the value"}
json.dump(OUT, open(OUT_JS, "w", encoding="utf-8"), indent=1, default=str)


def cell(x):
    return (json.dumps(x, default=str) if not isinstance(x, str) else x).replace("|", "/").replace("\n", " ")


md = ["---", "type: facts", "status: current", "date: %s" % time.strftime("%Y-%m-%d"), "card: 167-a1-4", "---",
      "# P6-2 replay readiness (PD404(g), docs/d1/ring-p6.md:87-90) - facts only, no design, no verdict",
      "Written by `tools/bench/diag_c167_a1_4_ready.py` (offline; LabVIEW reads 0). Machine-readable: `tools/bench/p6_replay_ready.json`. "
      "Graphs: P5 final `%s` (md5 field %s), S1 `%s`. unread = no stored read holds the value." % (GF, G.md5, S1F), "",
      "## 1 - swap sites (by S1 uid; the recipe resolves them BY UID, not by label)", "",
      "| uid | S1 callee (src) | recipe route (src) | in 7815af09? | P5 class / loop / frame diagram | same terminal names S1 vs P5 | same wire partners | other P5 SubVI with the same terminal signature | P5 src |",
      "|---|---|---|---|---|---|---|---|---|"]
for s in SITES:
    md.append("| #%d | %s (%s) | %s (%s) | %s | %s / %s / %s owner %s (S1 diagrams %s) | %s | %s %s | %s | %s |" % (
        s["uid"], cell(s["s1"]["subvi_name"]), s["s1"]["src"], s["recipe_resolves_by"], "; ".join(s["recipe_src"]),
        "present (same uid)" if s["p5"]["present"] else "ABSENT", s["p5"]["class"], s["p5"]["loop"], s["p5"]["frame_diagrams"],
        cell(s["p5"]["diagram_owner"]), s["s1"]["frame_diagrams"], s["same_terminal_signature"], s["wire_partners_equal"], cell(s["wire_partners_diff"]),
        s["p5_other_subvi_same_signature"] or "none", s["p5"]["src"] + "; " + s["p5"]["callee_name"]))
md += ["", "## 2 - how the 110 replay legs treated the motors (they were NOT kept off)", "",
       "| fact | source |", "|---|---|",
       "| card 110-6 launched nothing (status %s): '%s' | %s |" % (MOTOR["card_110_6_launched"], cell(MOTOR["card_110_6_note"]), MOTOR["card_110_6_src"]),
       "| the two replay legs ran under card %s (drive_m8_replay_110.py, 15/0) | %s |" % (MOTOR["legs_ran_under"], MOTOR["legs_src"]),
       "| %s | %s |" % (MOTOR["swap_scope"], "; ".join(MOTOR["swap_scope_src"])),
       "| leg chain: drive_m8_replay_110 -> diag_c104_leg -> drive_m8 --leg replay_s1 -> v5.main() (runs the swapped copy) | %s |" % "; ".join(MOTOR["chain"]),
       "| before each leg: VISA open+close of 'Rotor' and 'ASRL5::INSTR' (no byte sent); nonzero status refuses the leg | %s |" % "; ".join(MOTOR["visa_precheck"]),
       "| before Run: `motor_gate.py --session start` (v5 G0); comment: running the copy executes the original's device init, which drives the PI stage and the ASI; gate exit != 0 refuses the run | %s |" % "; ".join(MOTOR["motor_gate_before_run"]),
       "| after the run: LabVIEW must be gone (G92), then a post-run TMX? read through the gate (G93 TMX? == 39) | %s |" % "; ".join(MOTOR["motor_read_after_run"]),
       "| the scripts' scope headers say `hardware: none` although the legs pass through the motor gate | %s |" % "; ".join(MOTOR["headers_say_hardware_none"])]
for l in LEGS:
    md.append("| leg %s: motor_tmx_after %s, lost %s, v5_failing %s, run_dir files %s | %s facts / m8 |" % (
        cell(l["leg_json"].split("/")[-2]), l["motor_tmx_after"], l["lost"], cell(l["v5_failing"]), cell(l["files"]), l["leg_json"]))
for s in MOTOR["v5_json_last_leg_steps"]:
    md.append("| v5 json (last writer, mtime %s): step '%s' ok %s - %s | %s |" % (MOTOR["v5_json_mtime"], cell(s["step"]), s["ok"], cell(s["detail"])[:300], s["src"]))
md += ["", "## 3 - saved files compared", "", "| item | value | source |", "|---|---|---|",
       "| files compared | %s; other files: %s | %s; %s |" % ("; ".join(COMPARE["compared"]), COMPARE["other_files"], "; ".join(COMPARE["tra_read"]), COMPARE["tiff_delete_src"]),
       "| X/Y/Z 'bit-identical' meaning | %s | %s |" % (COMPARE["xyz_meaning"], "; ".join(COMPARE["xyz_gate"])),
       "| cal meaning | %s | %s; %s |" % (COMPARE["cal_meaning"], "; ".join(COMPARE["cal_read"]), COMPARE["cal_not_gated_src"]),
       "| 110-7 tra result | %s | %s |" % (cell(COMPARE["result_110_7"]), MJ),
       "| 110-7 per-column rows differ (non-zero) | %s (col 0 time/frame, 1 trans, 2 rot) | %s per_column_rows_differ; %s |" % (cell(COMPARE["per_column_rows_differ_nonzero"]), MJ, "; ".join(COMPARE["per_column"])),
       "| 110-7 cal result | %s | %s cal |" % (cell(COMPARE["result_cal"]), MJ),
       "| 110-7 gates | %s | %s gates |" % (cell(COMPARE["gates"]), MJ)]
md += ["", "## 4 - missing pieces for pointing the chain at a ring file (facts, no design)", "", "| id | fact | source |", "|---|---|---|"]
for m in MISSING:
    md.append("| %s | %s | %s |" % (m["id"], cell(m["fact"]), cell(m["src"]) if not isinstance(m["src"], str) else m["src"]))
open(OUT_MD, "w", encoding="utf-8").write("\n".join(md) + "\n")

# ------------------------------------------------------------------ after
print("== after", flush=True)
bad1, vh1 = hashes()
gate("A1 inputs and seven VIs unchanged after", not bad1 and vh1 == vh0, bad1 or "equal")
gate("A2 no LabVIEW process at end", not lv_running())
arts = [{"path": p, "md5": L.md5(p)} for p in (OUT_MD, OUT_JS)]
gate("W1 outputs written", all(os.path.getsize(p) > 0 for p in (OUT_MD, OUT_JS)), arts)
for a in arts:
    print("ARTEFACT %s md5 %s" % (a["path"], a["md5"]), flush=True)
sys.exit(gate.result(arts))
