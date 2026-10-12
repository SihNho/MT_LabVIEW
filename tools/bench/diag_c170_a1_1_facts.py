# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_170-a1-1.json
# ---
r"""diag_c170_a1_1_facts - card 170-a1-1 brief s.2-3 (PD409(d), docs/d1/ring-p6.md:260-269): facts F1-F6 for the P6-2 replay, OFFLINE.
Reads stored graphs and source text only; no LabVIEW, no .vi opened. Writes tools/bench/p6_replay_facts.md + .json.

Found before writing (CALLED, not copied): diag_c108c_graph.Graph (by_owner/by_wire/chain/pair; json hand-off as
diag_c167_a1_4_ready.py:111-122), prep_c168_hashlib.check + prep_c156_a1_1_lib.Gate/md5 (end re-hash, gates), the re-hash rows of
diag_c170_a1_1_hash.json (same card). Not importable (module-level scripts), so ONE small citation check `chk` is written here; its
siblings line_of/find_line live inline in diag_c167_a1_4_ready.py:84, diag_c167_a1_2_crows.py:73, diag_c166_a1_5_census.py:84,
diag_c164_a3_3_dw.py:49 (reported in the result's open list, not extracted: outside this card's write globs).

PREDICTION CONTRACT (each gate can fail):
 F1a #6810 SubVI in P6 directly in While #637 (1.1), terminal names == S1's; F1b P6 #5058 in While #10170 (1.2), 'Image In' from
     #29843 IndexArray; S1 #5058 'Image In' on #6810 'Image Out''s wire; F1c #22692 in P6 under For #22433/#21305, no While, every
     terminal's (name, wire partners) == S1's.
 F2a #26879 'x' on #6810 'current image number' wire, 'y' from LSR #27056, RSR #27039 on that wire, pair 27039->27056 in #637;
 F2b counter #27311 'x+1' on d27219 inside Case #22694; F2c #6810 'Buffer to extract' from LSR #5351, RSR #1117 from #1978 'x+1',
     pair 1117->5351, #1978 'x' from #1034 whose two inner faces carry #2179 ('current image number') and #1445 ('Buffer to extract');
 F2d get-buff wiki graph: #529 'Buffer Number In' on the 'Buffer to extract' control wire, 'Buffer Number Out' on 'current image number'.
 F3a #29724 'next discards' -> only RSR #29648, RSR outer face unwired, LSR #29655 inner -> only #29724 'discards' (pair in #10170);
 F3b no terminal named like 'discard' outside #29724; F3c indicator 'Total Lost Frames' (ControlTerminal) on d3292 in P6 and S1.
 F4a S1 cal write path #26615 'data' <- #26446; 'Date and time' <- #26428 <- #26411 date/time strings; prepend + byte order unwired;
 F4b the same rows in P6.  C every file:line citation found by a read.  A re-hash after == before; no LabVIEW process.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c170_a1_1_facts.log -- py -u tools/bench/diag_c170_a1_1_facts.py"""
import json, os, subprocess, sys, time, types                                              # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    _p in sys.path or sys.path.insert(0, _p)                                                # noqa: E701
import diag_c108c_graph as DG                                                               # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
import prep_c168_hashlib as HL                                                              # noqa: E402

B = "tools/bench/"
GF, S1F, GBF = B + "graph_ring_p6_20261012_212645.json", "docs/wiki/subvi/D1_s1_copy.json", "docs/wiki/subvi/get buff image-lost frames.json"
HJ = B + "diag_c170_a1_1_hash.json"
OUT_MD, OUT_JS = B + "p6_replay_facts.md", B + "p6_replay_facts.json"
gate = L.Gate(fatal_default=False)
_loads = json.loads


def _loads_gs(s):
    g = _loads(s)
    if isinstance(g, dict) and "terminals" in g:
        g.setdefault("graph_summary", {})
        g.setdefault("objs", [])
    return g


DG.json = types.SimpleNamespace(loads=_loads_gs)
P6, S1, GB = (DG.Graph(os.path.join(ROOT, p).replace("\\", "/")) for p in (GF, S1F, GBF))
P6RAW = _loads(open(GF, encoding="utf-8").read())


def T(g, u, name):
    """the terminal of node u named `name` (first match) or {}"""
    return next((t for t in g.by_owner.get(u, []) if t["term_name"] == name), {})


def ends(g, t):
    """sorted (owner uid, term name) at the other ends of terminal t's wire ([] when unwired)"""
    return sorted((o["owner_uid"], o["term_name"]) for o in g.by_wire.get(t.get("wire_uid") or -1, []) if o["term_uid"] != t["term_uid"])


def gu(t):
    return "%s terminals[term_uid=%d]" % (GF, t["term_uid"]) if t else "%s (terminal absent)" % GF


def wl(path, g, t):
    """'path:line' of term t in an indented wiki graph"""
    return "%s:%s" % (path, g.lines.get(t["term_uid"], "?")) if t else "%s (terminal absent)" % path


CHK = []


def chk(path, n, must):
    """'path:n' after checking that line n holds `must` (every file:line below is read, not typed)."""
    try:
        ok = must in open(path, encoding="utf-8", errors="replace").read().split("\n")[n - 1]
    except (OSError, IndexError):
        ok = False
    CHK.append((path, n, must, ok))
    return "%s:%d" % (path, n)


assert chk(B + "diag_c170_a1_1_facts.py", 1, "# ---") == B + "diag_c170_a1_1_facts.py:1" and CHK.pop()[3] is True
lv = lambda: ("lab" + "view") in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()   # noqa: E731
gate("L0 no LabVIEW process at start", not lv())

# ---------------------------------------------------------------- F1
names = lambda g, u: sorted(t["term_name"] for t in g.by_owner.get(u, []))                  # noqa: E731
gate("F1a #6810 SubVI in P6 directly in While #637 (1.1); terminal names == S1", P6.cls.get(6810) == "SubVI" and P6.chain(6810) == [637]
     and names(P6, 6810) == names(S1, 6810), (P6.cls.get(6810), P6.chain(6810)))
ti6, ti1 = T(P6, 5058, "Image In"), T(S1, 5058, "Image In")
gate("F1b P6 #5058 in While #10170 (1.2), Image In <- #29843; S1 #5058 Image In <- #6810 'Image Out'", P6.chain(5058) == [10170]
     and ends(P6, ti6) == [(29843, "element")] and ends(S1, ti1) == [(6810, "Image Out")], (P6.chain(5058), ends(P6, ti6), ends(S1, ti1)))
c22 = P6.chain(22692)
same22 = all(ends(P6, t) == ends(S1, T(S1, 22692, t["term_name"])) for t in P6.by_owner[22692] if t["term_name"])
gate("F1c #22692 in P6 under For #22433/#21305, no While; (name, partners) == S1 per terminal", P6.cls.get(22692) == "SubVI"
     and 22433 in c22 and 21305 in c22 and not any(P6.cls.get(s) == "WhileLoop" for s in c22) and same22, (c22, same22))

# ---------------------------------------------------------------- F2
cin = T(P6, 6810, "current image number"); bte = T(P6, 6810, "Buffer to extract")
x, y = T(P6, 26879, "x"), T(P6, 26879, "y")
gate("F2a #26879 x on #6810 'current image number' wire; y <- LSR #27056; RSR #27039 on that wire; 27039->27056 in #637",
     x.get("wire_uid") == cin.get("wire_uid") and ends(P6, y) == [(27056, "current image number")]
     and (27039, "current image number") in ends(P6, cin) and 27056 in P6.pair.get(27039, []), (ends(P6, y), P6.pair.get(27039)))
gate("F2b counter #27311 'x+1' on d27219 inside Case #22694 in #637", P6.chain(27311) == [22694, 637]
     and T(P6, 27311, "x+1").get("frame_diagram") == 27219, P6.chain(27311))
i1034 = sorted(ends(P6, t)[0] for t in P6.by_owner[1034] if not t["is_source"] and ends(P6, t))
s2179 = [t for t in P6.by_owner[2179] if not t["is_source"]]                                 # its outer (sink) face on d639
s1445 = [t for t in P6.by_owner[1445] if not t["is_source"]]
gate("F2c 'Buffer to extract' <- LSR #5351; RSR #1117 <- #1978 x+1; 1117->5351; #1978 x <- #1034 (frames fed by #2179 / #1445)",
     (5351, "LastBufferNumber") in ends(P6, bte) and ends(P6, T(P6, 1978, "x+1")) == [(1117, "LastBufferNumber")]
     and 5351 in P6.pair.get(1117, []) and ends(P6, T(P6, 1978, "x")) == [(1034, "LastBufferNumber")]
     and i1034 == [(1445, "LastBufferNumber"), (2179, "current image number")]
     and len(s2179) == 1 and s2179[0]["wire_uid"] == cin["wire_uid"] and len(s1445) == 1 and s1445[0]["wire_uid"] == bte["wire_uid"],
     (ends(P6, bte), i1034))
gbi, gbo = T(GB, 529, "Buffer Number In"), T(GB, 529, "Buffer Number Out")
gate("F2d get-buff: #529 BN In on 'Buffer to extract' control wire; BN Out on 'current image number' indicator wire",
     (3, "Buffer to extract") in ends(GB, gbi) and (3, "current image number") in ends(GB, gbo), (ends(GB, gbi), ends(GB, gbo)))

# ---------------------------------------------------------------- F3
nd, dc = T(P6, 29724, "next discards"), T(P6, 29724, "discards")
rsr_out = [t for t in P6.by_owner[29648] if t["is_source"]]
lsr_in = [t for t in P6.by_owner[29655] if t["is_source"]]
gate("F3a 'next discards' -> only RSR #29648 (outer face unwired); LSR #29655 inner -> only #29724 'discards'; 29648->29655 in #10170",
     ends(P6, nd) == [(29648, "")] and all(not t["wire_uid"] for t in rsr_out) and [ends(P6, t) for t in lsr_in] == [[(29724, "discards")]]
     and 29655 in P6.pair.get(29648, []), (ends(P6, nd), [t["wire_uid"] for t in rsr_out], [ends(P6, t) for t in lsr_in]))
disc_named = sorted({(t["owner_uid"], t["owner_class"], t["term_name"]) for t in P6.terms if "discard" in (t["term_name"] or "").lower()})
gate("F3b no terminal named like 'discard' outside #29724 (no indicator, no local)", all(o == 29724 for o, _c, _n in disc_named), disc_named)
tlf6 = [t for t in P6.terms if t["term_name"] == "Total Lost Frames" and t["owner_class"] == "Diagram"]
tlf1 = [t for t in S1.terms if t["term_name"] == "Total Lost Frames" and t["owner_class"] == "Diagram"]
gate("F3c indicator 'Total Lost Frames' on d3292 in P6 (loop 1.1) and S1", [t["frame_diagram"] for t in tlf6] == [3292]
     and [t["frame_diagram"] for t in tlf1] == [3292] and P6.loop(3162) == "1.1", ([t["term_uid"] for t in tlf6], [t["term_uid"] for t in tlf1]))

# ---------------------------------------------------------------- F4
def calpath(g):
    d = T(g, 26615, "data"); dt = T(g, 26446, "Date and time"); cs = [t for t in g.by_owner.get(26428, []) if not t["is_source"]]
    return {"data": ends(g, d), "dt": ends(g, dt), "concat_in": sorted(set(e for t in cs for e in ends(g, t) if e[0] != 26428)),
            "unwired": sorted(t["term_name"] for t in g.by_owner.get(26615, []) if not t["wire_uid"] and not t["is_source"])}


cp1, cp6 = calpath(S1), calpath(P6)
gate("F4a S1 cal write path: #26615 data <- #26446; 'Date and time' <- #26428; inputs #26411 date/time strings + #26136",
     (26446, "output cluster") in cp1["data"] and cp1["dt"] == [(26428, "concatenated string")]
     and cp1["concat_in"] == [(26136, ""), (26411, "date string"), (26411, "time string")]
     and "prepend array or string size? (T)" in cp1["unwired"] and "byte order (0:big-endian, network order)" in cp1["unwired"], cp1)
gate("F4b the same rows in P6", cp6 == cp1, cp6)

# ---------------------------------------------------------------- facts text
rh = json.load(open(HJ, encoding="utf-8"))
C = {  # file:line citations, each read back by chk()
    "standin_rule": chk(B + "diag_replay_standins.py", 9, "frame = paths[k mod 10044] = f(k mod 10044) (PD18(a)); buf: BN Out = BN In"),
    "buf_saved_a9": chk(B + "stage_replay_78.log", 81, "BN Out on BN In's wire"),
    "buf_md5": chk(B + "stage_replay_78.log", 85, "a89dafc1db03feef7b528f0dd4fcc692"),
    "gbf_swap": chk(B + "stage_replay_78.log", 93, "G2 replace clean; callee diff == #529 -> buf only; wire-edge diff 0"),
    "gbf_md5": chk(B + "stage_replay_78.log", 94, "842ecad9a6674a5060ebb3d5522751a9"),
    "gbf_recipe": chk("tools/recipes/stage_replay_standins.py", 86, "shutil.copyfile(L.GB, L.GBF)"),
    "case_sel": chk(B + "stage_d1_ring_p3a.json", 119, "selector <- #26879.'x = y?' on Diagram #639"),
    "case_false": chk(B + "stage_d1_ring_p3a.json", 136, '"False"'),
    "case_frames": chk(B + "stage_d1_ring_p3a.json", 140, "27219"),
    "seqcheck": chk("docs/d1/ring-p4b.md", 140, "valid = n1==n2 AND"),
    "seqcheck2": chk("docs/d1/ring-p4b.md", 141, "next discards = valid ? discards : discards+1"),
    "ilost": chk(B + "drive_original_copy_v2.py", 132, 'I_LOST = "Total Lost Frames"'),
    "l11loop": chk(B + "drive_original_copy_v5.py", 497, "while time.time() - t0 < RUN_S:"),
    "l11lost": chk(B + "drive_original_copy_v5.py", 506, "getv(d0.I_LOST)"),
    "m8lost": chk(B + "drive_m8.py", 113, "lost = m.group(1)"),
    "m8lostout": chk(B + "drive_m8.py", 128, '"total_lost_frames": lost'),
    "legA_lost": chk(B + "t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json", 437, '"lost": "0"'),
    "legB_lost": chk(B + "t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json", 469, '"lost": "0"'),
    "v5_cleanup": chk(B + "drive_original_copy_v5.py", 688, "dn, db = d0.delete_tiffs(RUN_DIR)"),
    "v2_deltif": chk(B + "drive_original_copy_v2.py", 418, '(".tif", ".tiff")'),
    "v5_l9": chk(B + "drive_original_copy_v5.py", 78, "the save dialog takes an ABSOLUTE path under"),
    "m8_rundir": chk(B + "drive_m8.py", 75, 'run_dir = os.path.join(HERE, "m8_out"'),
    "m8_copy": chk(B + "drive_m8.py", 72, "copy = os.path.join("),
    "m8_rmcopy": chk(B + "drive_m8.py", 123, "os.remove(copy)"),
    "m8_v5json": chk(B + "drive_m8.py", 82, 'v5.D0_JSON = d0.D0_JSON = os.path.join(OUTD, "m8_v5_%s%s%s.json"'),
    "m8_clicks": chk(B + "drive_m8.py", 83, "_clicks.json"),
    "m8_shots": chk(B + "drive_m8.py", 78, 'm.SHOTS = os.path.join(HERE, "m8_shots")'),
    "m8_json": chk(B + "drive_m8.py", 136, 'jp = os.path.join(OUTD, "m8_%s%s%s.json"'),
    "legA_files": chk(B + "t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json", 673, "cal001 (857376 B)"),
    "legA_tra": chk(B + "t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json", 674, "tra001-000 (1706560 B)"),
    "legA_tiffs": chk(B + "t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json", 678, '"count": 0'),
    "legB_files": chk(B + "t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json", 703, "cal001 (857376 B)"),
    "legB_tra": chk(B + "t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json", 704, "tra001-000 (3282880 B)"),
    "plans": chk("tools/recipes/stage_replay_swap.py", 22, 'PLANS = {"78": "plans/plan_replay_swap_78.json"'),
    "plan_arg": chk("tools/recipes/stage_replay_swap.py", 24, 'PLAN_TAG = sys.argv[sys.argv.index("--plan") + 1]'),
    "drv_sj": chk(B + "drive_m8_replay_110.py", 19, 'SJ = json.load(open(os.path.join(HERE, "stage_replay_swap_110.json")'),
    "drv_pin": chk(B + "drive_m8_replay_110.py", 20, 'PIN = {"S1replay": (os.path.join(RP, "D1_s1_replay_20260925_075422.vi"), "126f84975fca9f6124432a7e4decd0c8")'),
    "drv_disp": chk(B + "drive_m8_replay_110.py", 21, '"dispreplay": (DISP, SJ["copies"]["disp"]["md5"])'),
    "drv_runs": chk(B + "drive_m8_replay_110.py", 22, "NPICK, RUN_S, TS = 15, 120"),
    "drv_leg": chk(B + "drive_m8_replay_110.py", 41, '"diag_c104_leg.py"), "--src", src, "--picks", str(NPICK)'),
    "drv_card": chk(B + "drive_m8_replay_110.py", 80, '"card": "110-7"'),
    "drv_index": chk(B + "drive_m8_replay_110.py", 86, "Card 110-7 (110-6 route"),
    "leg_args": chk(B + "diag_c104_leg.py", 22, 'SRC = os.path.normpath(A[A.index("--src") + 1])'),
    "leg_runs": chk(B + "diag_c104_leg.py", 23, 'RUN_S = A[A.index("--run-s") + 1] if "--run-s" in A else "120"'),
    "leg_kind": chk(B + "diag_c104_leg.py", 33, '"--leg", "replay_s1", "--src", SRC'),
    "leg_json": chk(B + "diag_c104_leg.py", 176, 'm8p = os.path.join(HERE, "m8_replay_s1_p%d_r%d%s.json"'),
    "m8_kinds": chk(B + "drive_m8.py", 68, 'if LEG in ("replay_s1", "replay_s3"):'),
    "m8_srcmd5": chk(B + "drive_m8.py", 69, "smd5 = md5(src)"),
    "m8_runs": chk(B + "drive_m8.py", 36, 'RUN_S_ARG = float(A[A.index("--run-s") + 1]) if "--run-s" in A else 35.0'),
    "m8_runs2": chk(B + "drive_m8.py", 85, "v5.RUN_S = RUN_S_ARG"),
    "m8_m7": chk(B + "drive_m8.py", 121, 'G["M7 bed md5 unchanged"] = md5(BED) == BED_MD5'),
    "v5_noend": chk(B + "drive_original_copy_v5.py", 52, "`--session end` is NEVER called"),
    "cmp_main": chk(B + "m8b_replay_compare.py", 31, "def main(a1, a3, out):"),
    "legA_frames": chk(B + "t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json", 438, '"frames_delta": 4081'),
    "s1_6810": chk(S1F, 89810, '"node_uid": 6810'),
    "s1_22692": chk(S1F, 90152, '"node_uid": 22692'),
}
p = lambda t: gu(t)                                                                           # noqa: E731
F = {}
F["f1"] = {"verdict": "FACT", "cites": [C["s1_6810"], C["s1_22692"], p(T(P6, 6810, "Buffer to extract")), wl(S1F, S1, T(S1, 6810, "Buffer to extract")), p(ti6), wl(S1F, S1, ti1),
                                        p(T(P6, 22692, "Buffer Number In")), wl(S1F, S1, T(S1, 22692, "Buffer Number In"))],
           "parts": {"present_by_uid": "FACT", "callee_name_in_P6": "NOT-DETERMINED (the P6 graph has no graph_summary.subvi_calls; same uid + same terminal names as S1 only)",
                     "calls_per_tracked_frame_P6": "NOT-DETERMINED (run-time ratio of 1.1 to 1.2 iterations)"},
           "text": ("#6810 (S1 callee 'get buff image-lost frames.vi', %s) and #22692 (S1 callee 'IMAQdx Get Image.vi') are SubVI nodes in P6 by uid with "
                    "the same terminal names as S1; the P6 graph stores no SubVI names, so the P6 callee is NOT-DETERMINED by name. "
                    "#6810 sits directly on d639 of While #637 (loop 1.1, no Case): one call per 1.1 iteration in P6 and in S1. "
                    "S1: tracker #5058 is on the same d639 and its 'Image In' is #6810's 'Image Out' wire -> 1 call per tracked frame. "
                    "P6: #5058 is on d23166 of While #10170 (loop 1.2), 'Image In' from #29843 IndexArray (ring slot read): #6810 runs every 1.1 "
                    "iteration whether or not 1.2 reads that frame, so calls per tracked frame = 1.1 iterations / 1.2 tracked reads (>= 1), a run-time "
                    "number the graph cannot give. #22692 is under For #22433 / Sequence #21590 / For #21305 in the calibration flat-sequence frames "
                    "(session path to d26117 'CamSessionOut'), no While: 0 calls per tracked frame in P6 and S1 (identical terminals and partners); "
                    "calls per calibration = the two For counts, unread.") % C["s1_6810"]}
F["f2"] = {"verdict": "EVERY", "cites": [p(x), p(y), p(cin), p(bte), p(T(P6, 1978, "x+1")), p(T(P6, 27311, "x+1")), wl(GBF, GB, gbi), wl(GBF, GB, gbo),
                                         C["case_sel"], C["case_false"], C["case_frames"], C["standin_rule"], C["buf_saved_a9"], C["gbf_swap"]],
           "text": ("New frame in P6 = Case #22694 frame 'False' (d27219), selector #26879 'x = y?' with x = #6810 'current image number' and y = the "
                    "previous iteration's value (LSR #27056 <- RSR #27039 on the same wire); d27219 holds the P3a counter #27311 'x+1' (ring write). "
                    "replay_get_buff_image.vi (842ecad9) = get-buff copy with #529 swapped to the buf stand-in, wire edges unchanged; in it 'Buffer Number In' "
                    "= the 'Buffer to extract' input and 'Buffer Number Out' = the 'current image number' output, and the stand-in wires BN Out = BN In. "
                    "In P6 1.1, 'Buffer to extract' = LSR #5351 <- RSR #1117 <- #1978 'x+1', #1978 'x' = #1034 (one frame carries #6810 'current image number', "
                    "the other 'Buffer to extract'). Under the stand-in both frames give current(i+1) = current(i) + 1, so x != y on every 1.1 iteration and "
                    "EVERY stand-in frame is classed new and counted (first iteration: constant #27095 vs the start value, both unread). Whether 1.2 then "
                    "tracks every ring frame is a run-time count (F3), not shown by the graph.")}
F["f3"] = {"verdict": {"discards": "NOT READABLE", "lost": "READABLE"},
           "cites": [p(nd), p(dc), gu(rsr_out[0]) if rsr_out else GF, gu(lsr_in[0]) if lsr_in else GF, C["seqcheck"], C["seqcheck2"],
                     gu(tlf6[0]) if tlf6 else GF, wl(S1F, S1, tlf1[0]) if tlf1 else S1F, C["ilost"], C["l11loop"], C["l11lost"], C["m8lost"],
                     C["m8lostout"], C["legA_lost"], C["legB_lost"]],
           "text": ("Ring discards: #29724 'next discards' -> RSR #29648 only; its outer face (loop exit) is unwired; LSR #29655 (start constant #29662) "
                    "-> #29724 'discards' only; no indicator, local, or file carries it (no other terminal named 'discard'). A leg cannot read it: "
                    "NOT READABLE. Per RingSeqCheck's accepted arithmetic the count rises only on an invalid read (valid = n1==n2 AND n1>last), so a "
                    "frame overwritten before 1.2 reads it (n1 > last+1, still valid) is not counted. S1 lost frames: indicator 'Total Lost Frames' "
                    "on d3292 (Case #3191 in loop 1.1, fed by #3162 'x-y'), present in P6 too; the v5 leg reads it by label once at the end of RUN_S, "
                    "before the stop, into the L11 detail -> drive_m8 'total_lost_frames' -> leg.json 'lost' (110-7: '0' both legs): READABLE. No "
                    "saved file carrying it was found (save trace.vi #376 has no lost-frames input).")}
F["f4"] = {"verdict": "NOT-DETERMINED",
           "cites": [wl(S1F, S1, T(S1, 26615, "data")), wl(S1F, S1, T(S1, 26446, "Date and time")), wl(S1F, S1, T(S1, 26428, "concatenated string")),
                     wl(S1F, S1, T(S1, 26411, "date string")), wl(S1F, S1, T(S1, 26411, "time string")), wl(S1F, S1, T(S1, 26411, "date format (0)")),
                     wl(S1F, S1, T(S1, 26411, "want seconds? (F)")), wl(S1F, S1, T(S1, 26446, "input cluster")),
                     wl(S1F, S1, T(S1, 26615, "prepend array or string size? (T)")), wl(S1F, S1, T(S1, 26615, "byte order (0:big-endian, network order)"))],
           "text": ("ORIGINAL cal write path (S1 = byte copy 3e3d23ce): #26615 ReadWriteFile 'data' <- #26446 NamedBundler 'output cluster'; its "
                    "'Date and time' <- #26428 'concatenated string' of #26411 'date string' + #26136 (constant, value unread) + #26411 'time string'; "
                    "#26411 takes 'date format (0)' <- EnumConstant #26145, 'want seconds? (F)' <- BooleanConstant #26126, 'seconds (now)' <- #26406. "
                    "#26615 'prepend array or string size? (T)' and 'byte order' are unwired (defaults). So the field is one flattened string (length "
                    "prefix + text) inside the cluster typed by ClusterConstant #26159 'input cluster'. Offset and length are NOT-DETERMINED: the "
                    "graph holds neither the cluster's element order/types nor the constants' values, and the elements bundled with it include arrays "
                    "(x,y pos, cal image, bandpass/forget, exp/ref) whose size varies per run. To read: the type of ClusterConstant #26159 (and "
                    "#26136, #26126, #26145 values) in claudeDev\\D1_s1_copy.vi (a LabVIEW read of the original's copy), then parse each .cal "
                    "with it. Same rows in P6.")}
F["f5"] = {"verdict": "FACT", "cites": [C["m8_rundir"], C["v5_l9"], C["m8_copy"], C["m8_rmcopy"], C["m8_v5json"], C["m8_clicks"], C["m8_shots"],
                                        C["m8_json"], C["leg_json"], C["legA_files"], C["legA_tra"], C["legA_tiffs"], C["legB_files"], C["legB_tra"],
                                        C["v5_cleanup"], C["v2_deltif"]],
           "text": ("VI-written, in run_dir tools/bench/m8_out/replay_s1_<ts>/: the cal file (save dialog of #26615, path typed under run_dir) and "
                    "tra*; in the 110-7 replay legs exactly cal001 (857376 B) + tra001-000 (A 1706560 B, B 3282880 B), TIFFs 0. Driver-written: the "
                    "run copy <src>_run_<ts>.vi beside the replay VIs (deleted by drive_m8 at end), m8_v5_replay_s1_p<N>_r<S>.json, its _clicks.json, "
                    "m8_replay_s1_p<N>_r<S>.json, screenshots in tools/bench/m8_shots, leg.json in the leg's --out dir. v5 cleanup deletes only "
                    "*.tif/*.tiff in run_dir (none in 110-7); cal and tra are kept. What the P6 copy writes is NOT measured until a P6 leg runs.")}
F["f6"] = {"verdict": "FACT", "cites": [C["plans"], C["plan_arg"], C["drv_sj"], C["drv_pin"], C["drv_disp"], C["drv_runs"], C["drv_leg"], C["drv_card"],
                                        C["drv_index"], C["leg_args"], C["leg_runs"], C["leg_kind"], C["leg_json"], C["m8_kinds"], C["m8_srcmd5"],
                                        C["m8_runs"], C["m8_runs2"], C["m8_m7"], C["v5_noend"], C["cmp_main"], C["standin_rule"], C["legA_frames"]],
           "text": ("X5 plan literal: stage_replay_swap.py loads only PLANS {78, 95, 110}, picked by --plan <tag>; a P6 plan needs a new entry there "
                    "(a recipe edit). X6/X7 driver pins: drive_m8_replay_110.py hard-codes leg A (S1 replay copy 126f8497) and takes leg B's md5 only "
                    "from stage_replay_swap_110.json copies.disp; --disp <path> takes leg B's path; it writes card '110-7' and an INDEX row naming the "
                    "display-loop VI. X8 leg kind: diag_c104_leg.py takes --src <any vi> --picks N --run-s S --out <dir> and always runs drive_m8 "
                    "--leg replay_s1, so both legs write m8_replay_s1_p<N>_r<S>.json (leg.json in --out keeps each); drive_m8 accepts replay_s1/"
                    "replay_s3 and reads the md5 from --src itself. X9: drive_m8 M7 needs BED/S3/ORIG/S1 + src md5 unchanged. Run length: --run-s "
                    "seconds only (diag_c104_leg -> drive_m8 -> v5.RUN_S); NO frame-count parameter exists; the stand-in serves paths[k mod 10044] "
                    "(110-7 leg A: frames_delta 4081 in 120 s). Compare: m8b_replay_compare.main(dir_a, dir_b, out). v5 runs motor_gate --session "
                    "start itself and never --session end. The shared pieces that take a P6 copy as a parameter today: diag_c104_leg --src, "
                    "drive_m8 --src, m8b_replay_compare.main; the 110 wrapper's pins and the PLANS literal do not.")}
d_word = F["f3"]["verdict"]["discards"]; l_word = F["f3"]["verdict"]["lost"]
HANDBACK = "HANDBACK-GATE: F2=%s F3=discard %s; lost %s -> %s" % (F["f2"]["verdict"], d_word, l_word,
                                                                 "HANDBACK" if F["f2"]["verdict"] == "NONE" or d_word == "NOT READABLE" else "PROCEED")
gate("C every file:line citation found by a read (%d)" % len(CHK), all(c[3] for c in CHK), [c[:3] for c in CHK if not c[3]])

OUT = {"schema": "p6-replay-facts/1", "card": "170-a1-1", "graphs": {"p6": [GF, P6.md5], "s1": [S1F, S1.md5], "get_buff": [GBF, GB.md5]},
       "rehash": rh["rehash"], "drift": rh["drift"], **F, "handback_gate": HANDBACK}
json.dump(OUT, open(OUT_JS, "w", encoding="utf-8"), indent=1)
md = ["---", "type: facts", "status: current", "date: %s" % time.strftime("%Y-%m-%d"), "card: 170-a1-1", "---",
      "# P6-2 replay facts F1-F6 (PD409(d), docs/d1/ring-p6.md:260-269) - facts only, no decision",
      "Written by `tools/bench/diag_c170_a1_1_facts.py` (offline, LabVIEW reads 0). Re-hash by `diag_c170_a1_1_hash.py` -> "
      "`tools/bench/diag_c170_a1_1.log`. Machine-readable: `tools/bench/p6_replay_facts.json`. P6 graph cites are graph uids (single-line json).", "",
      "## 1 - re-hash (drift first): %s" % ("NO DRIFT" if not rh["drift"] else "DRIFT " + ", ".join(rh["drift"])), "",
      "| row | expected | measured | status |", "|---|---|---|---|"]
md += ["| %s | %s | %s | %s |" % (r["row"], r["expected"], r["measured"], r["status"]) for r in rh["rehash"]]
for k in ("f1", "f2", "f3", "f4", "f5", "f6"):
    v = F[k]["verdict"]
    md += ["", "## %s - %s" % (k.upper(), json.dumps(v) if isinstance(v, dict) else v), "", F[k]["text"], ""]
    if F[k].get("parts"):
        md += ["- part %s: %s" % (a, b) for a, b in F[k]["parts"].items()]
    md += ["- cite: %s" % c for c in F[k]["cites"]]
md += ["", HANDBACK]
open(OUT_MD, "w", encoding="utf-8").write("\n".join(md) + "\n")

r_end = HL.check("tools/bench/cards/task_170-a1-1.json", "card 170-a1-1 end", gate,
                 pins=[(x_["row"][3:], x_["expected"]) for x_ in rh["rehash"] if x_["row"].startswith("VI ")])
gate("A no LabVIEW process at end", not lv())
print("FACT %s" % HANDBACK, flush=True)
sys.exit(gate.result([{"path": p_, "md5": L.md5(p_)} for p_ in (OUT_MD, OUT_JS)]))
