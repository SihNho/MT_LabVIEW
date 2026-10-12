# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/task_170-a3-1.json
# ---
r"""stage_replay_paced60 - card 170-a2-3 (docs/d1/ring-p6.md PD410(d)): the PACED stand-in pair under claudeDev\replay.
(1) replay_imaqdx_get_image_buf_paced60.vi = replay_imaqdx_get_image_buf.vi (a89dafc1) + ONE Wait (ms) whose only input is a
diagram constant 60 (typed by the sink), no other wire: the call lasts >= 60 ms, no pixel / computation changes.
(2) replay_get_buff_image_paced60.vi = replay_get_buff_image.vi (842ecad9) with ONLY its buf callee swapped to (1).
FOUND FIRST (CALLED, not copied): the Wait donor OpWaitDonor_v0 #163 (facts_c100_oplabels.json donors "Wait (ms)");
diag_replay_lib.copy_to (OpMoveByIndex_v0 copy, top level, UID guard); gscript.create_const_loop_term 'for_n' (OpCreateConstTop_v0
on a top-level node terminal, 77-4 - the verb of stage_replay_standins.const_top:20-27, whose gate reads nothing in its own
statement and so FAILS a dry run under DRY_RULE 3 (diag_c170_a2_3_dry.log); the verb is called here with the read inside the
gate); gscript.replace_object + diag_replay_lib.census/edges (the [G] swap of stage_replay_standins.py:85-94);
diag_replay_lib.tail (fixtures restored, LabVIEW gone); stagekit.Stage (start/save/restart/close). stage_d1_m4b's
from_decision const_row needs a WhileLoop body; this Wait is top level. Rows/values/names: tools/bench/diag_c170_a2_3_plan.json.
No VI is run.
PREDICTION: P0 outputs absent; A0 donor md5; A1 one new Function (the Wait); A2 const 60 on 'milliseconds to wait' (op errors
empty, one new Constant, sink wired); A3 wire edges: none removed, exactly ONE added = const -> Wait, the Wait wired only on
that sink; A4 census Function +1 Constant +1 Wire +1; B1 ExecState 1 warm -> saved (S1-S3) -> B2 copied to (1);
G1 exactly one callee of the get-buff copy is the buf stand-in; G2 replace clean, callee diff == that node -> (1) only,
wire-edge diff 0 after the uid remap, ExecState 1 warm, saved; COLD (fresh LabVIEW): C1 both ExecState 1, VI.Name without a
library; C4 pane per slot == the unpaced file's; C2 (1) holds the Wait + constant text '60' and the same single const -> Wait
edge; C3 get-buff cold census == warm; I both inputs' md5 unchanged; N only the 2 new .vi in claudeDev\replay.
card 170-a3-1 (the retry, PD411(b)): every edit (copy, const, replace, get-buff save) runs as ONE Stage._op through op() so
stage_prerun X10 models it (x10_edit: N = ops, start = memory_model load_by_vi[a89dafc1] + op-0).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/launch_c170_paced60.log -- py -u tools/recipes/stage_replay_paced60.py --unverified-card tools/bench/cards/task_170-a3-1.json"""
import json, os, shutil, sys                                                             # noqa: E401
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench"))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
P = json.load(open(os.path.join(K.BENCH, "diag_c170_a2_3_plan.json"), encoding="utf-8"))
D, T, V, I = P["donor"], P["terms"], P["values"], P["inputs"]
PB, PG = os.path.join(L.RP, P["outputs"]["buf"]), os.path.join(L.RP, P["outputs"]["gbf"])
WIKI, CLS = K.mod("wiki_build"), ("Function", "Constant", "Wire")
nrm = os.path.normcase


def only_const_edge(add, rem, cu, wu, tname):
    """True iff no edge was removed and the ONE added edge runs from constant #cu into #wu's `tname` (edge tuples of
    diag_replay_lib.edges: (src uid, src term, dst uid, dst term))."""
    return not rem and len(add) == 1 and [(a[0], a[2], a[3]) for a in add] == [(cu, wu, tname)]


assert [only_const_edge({(5, "", 7, "t")}, set(), 5, 7, "t"), only_const_edge({(5, "", 7, "t"), (7, "o", 9, "x")}, set(), 5, 7, "t"),
        only_const_edge({(5, "", 7, "t")}, {(1, "a", 2, "b")}, 5, 7, "t")] == [True, False, False]


def op(s, verb, fn, detail=""):
    """card 170-a3-1 (PD411(b) lever (a)): run fn as ONE stagekit Stage._op (so stage_prerun X10 counts it, x10_edit) and
    re-raise what fn raised, so the run stops exactly as the direct call did. Returns fn's result."""
    rec = s._op(verb, fn, detail)
    if rec["err"] and s._last_exc is not None:
        raise s._last_exc
    return rec["result"]


assert op(type("F", (), {"_last_exc": None, "_op": lambda self, v, fn, d="": {"result": fn(), "err": ""}})(), "v", lambda: 7) == 7


def finfo(p):
    """{path, md5, bytes} of p ({path} only when absent: a dry run redirects every copy into %TEMP%)."""
    return dict(path=p, md5=K.md5(p), bytes=os.path.getsize(p)) if os.path.exists(p) else {"path": p}


def body(s):
    s.gate("P0 the two outputs do not exist yet", not (os.path.exists(PB) or os.path.exists(PG)), (PB, PG), fatal=True)
    rp0 = sorted(os.listdir(L.RP)); s.start(); W, R = s.work, s.R
    s.gate("A0 the Wait donor's md5 == the plan's pin", K.md5(D["path"]) == D["md5"], K.md5(D["path"]), fatal=True)
    shutil.copyfile(D["path"], g.MOVE_SRC)
    if not L.DRY:                    # a dry run redirects the copy into %TEMP%: MOVE_SRC is only checkable for real
        s.gate("A0b MOVE_SRC holds the Wait donor's bytes", K.md5(g.MOVE_SRC) == D["md5"], K.md5(g.MOVE_SRC), fatal=True)
    n0 = dict((c, s.count(c)) for c in CLS); E0 = L.edges(WIKI.read_live(W, fs_pairs=[]), {})
    wu = op(s, "copy_top", lambda: L.copy_to(s, D["cls"], D["uid"], None, None, "A1 wait"), "{0} #{1}".format(D["cls"], D["uid"]))
    wt = L.walk(W, 0); c0 = g.uids(W, "Constant")
    o = op(s, "create_const_loop_term", lambda: g.create_const_loop_term(W, "for_n", wt[wu][0], V["wait_ms"], term_index=L.term(wt[wu][2], T["wait_ms"], False)["i"]), "#{0} {1!r}".format(wu, V["wait_ms"]))
    cu = L.new1(W, "Constant", c0); R["wait_uid"], R["const_uid"], R["const_op"] = wu, cu, o
    s.gate("A2 const {0} on #{1}.{2!r}: op errors empty, one new constant, sink wired".format(V["wait_ms"], wu, T["wait_ms"]), not o.get("inv_err") and not o.get("err") and cu and L.term(L.walk(W, 0)[wu][2], T["wait_ms"], False)["wire"], o, fatal=True)
    E1 = L.edges(WIKI.read_live(W, fs_pairs=[]), {}); s.fact("A3 edges added {0} removed {1}".format(sorted(E1 - E0), sorted(E0 - E1)))
    s.gate("A3 edges: none removed, ONE added = const #{0} -> Wait #{1}; the Wait wired only on that sink".format(cu, wu), all(([(r["name"], r["is_source"]) for r in L.walk(W, 0)[wu][2] if r["wire"]] == [(T["wait_ms"], False)], only_const_edge(L.edges(WIKI.read_live(W, fs_pairs=[]), {}) - E0, E0 - L.edges(WIKI.read_live(W, fs_pairs=[]), {}), cu, wu, T["wait_ms"]), L.term(L.walk(W, 0)[wu][2], T["wait_ms"], False)["wire"])), (wu, cu), fatal=True)
    want = [n0[c] + 1 for c in CLS]  # dry: the gate's LAST read must be a graph read outside this file (stage_prerun taint is per statement)
    s.gate("A4 census delta Function +1, Constant +1, Wire +1", list(map(s.count, CLS)) == want, (n0, want))
    s.gate("B1 paced buf ExecState 1 warm", s.es("B1 warm") == 1, fatal=True)
    m = s.save()
    shutil.copyfile(W, PB); R["paced_buf"] = finfo(PB)
    if not L.DRY:
        s.gate("B2 paced buf saved and copied (md5 == the saved work)", m and R["paced_buf"].get("md5") == m, R["paced_buf"], fatal=True)
    s.head("[G] get-buff copy: replace ONLY the buf callee by the paced file")
    shutil.copyfile(L.GBF, PG); c0 = L.census(PG)
    old = [u for u, p in c0.items() if nrm(str(p)) == nrm(L.BUF)] or ([0] if L.DRY else [])
    s.gate("G1 exactly one callee of the get-buff copy is the buf stand-in", len(old) == 1, c0, fatal=True)
    E0g = L.edges(WIKI.read_live(PG, fs_pairs=[]), {}); r = op(s, "replace_object", lambda: g.replace_object(PG, old[0], PB), "gbf #{0}".format(old[0])); nu = r["new_uid"]
    c1 = L.census(PG); dd = dict((u, (c0.get(u), c1.get(u))) for u in set(c0) | set(c1) if c0.get(u) != c1.get(u)); R["swap"] = {"op": r, "old_uid": old[0], "diff": dd}
    s.gate("G2 replace clean; callee diff == #{0} -> paced only; wire-edge diff 0 after remap ({1} edges); ES 1 warm".format(old[0], len(E0g)), all((not (r["err"] or r["err_replace"]), nu, set(dd) <= {old[0], nu}, nrm(str(c1.get(nu))) == nrm(PB), E0g == L.edges(WIKI.read_live(PG, fs_pairs=[]), {nu: old[0]}), g.exec_state(PG) == 1)), (r, dd), fatal=True)
    op(s, "save_gbf", lambda: g.save(PG), "paced get-buff"); R["paced_gbf"] = finfo(PG)
    s.fact("SAVED paced buf {0}; paced get-buff {1}".format(R["paced_buf"], R["paced_gbf"])); s.dump()
    s.head("[C] COLD: fresh LabVIEW, both files opened cold")
    s.restart()
    for tag, p, ref in (("buf", PB, L.BUF), ("gbf", PG, L.GBF)):
        with g.vi_ref(p) as v:
            nm = str(v.Name)
        s.gate("C1 {0} ExecState 1 COLD, VI.Name {1!r} has no library".format(tag, nm), all((":" not in nm, g.exec_state(p) == 1)))
        s.gate("C4 {0} pane per slot == the unpaced file's".format(tag), L.pane_dirs(ref) == L.pane_dirs(p), (L.pane_dirs(ref), L.pane_dirs(p)))
    cv = K.mod("build_opcreateconstonterm_v0").read_const(PB, cu); R["cold_const"] = cv
    s.gate("C2 paced buf COLD: Wait #{0} present, const #{1} text '60', its one edge const -> Wait".format(wu, cu), all((str(cv.get("text")).strip() == str(int(V["wait_ms"])), not cv.get("err"), only_const_edge(set(e for e in L.edges(WIKI.read_live(PB, fs_pairs=[]), {}) if wu in (e[0], e[2])), set(), cu, wu, T["wait_ms"]), wu in g.uids(PB, "Function"))), cv)
    s.gate("C3 paced get-buff COLD callee census == warm", L.census(PG) == c1, c1)
    s.gate("I both inputs' md5 unchanged", K.md5(L.BUF) == I["buf"] and K.md5(L.GBF) == I["gbf"], (K.md5(L.BUF), K.md5(L.GBF)))
    new = sorted(set(os.listdir(L.RP)) - set(rp0)); R["replay_new"] = new
    if not L.DRY:                    # the dry run writes nothing into claudeDev\replay
        s.gate("N only the 2 new .vi in claudeDev\\replay", new == sorted(P["outputs"].values()) and not set(rp0) - set(os.listdir(L.RP)), new)
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, FXL, (D["md5"], I["buf"], self.R.get("paced_buf", {}).get("md5", "")))
        return K.Stage.summary(self)


if __name__ == "__main__":
    g.restore_move_fixtures(); FXL = K.fixture_listing()
    pins = tuple(K.DEFAULT_PINS[:1]) + L.pins() + tuple((n, os.path.join(K.CLAUDEDEV, n), m) for n, m in P["pins"]) + (("wait donor", D["path"], D["md5"]),)
    st = St(L.BUF, I["buf"], "stage_replay_paced60", preload=False, deadline_min=25, work_dir=os.path.dirname(g.MOVE_DST),
            work_name=os.path.basename(g.MOVE_DST), pins=pins, task="170-a3-1",
            out_json=os.path.join(K.BENCH, "diag_c170_a2_3_build.json"))
    sys.exit(K.run(body, st))
