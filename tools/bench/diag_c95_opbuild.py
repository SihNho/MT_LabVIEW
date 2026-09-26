r"""diag_c95_opbuild.py - card 95-4 (retry of 95-2): OpForLoopParSet_v0.vi, the WRITER for an EXISTING ForLoop's parallelism.
WHY HERE AND NOT tools/recipes/build_opforlooppar_v0.py: the card's pre-decided route is "the SAME gate path cycle 92 used" -
cycle 92 built its writer op OpCLFNThreadSet_v0 from tools/bench/diag_c92b_anythread.py. guard_cycle.py refused the recipe path
at 13:3x (4 slugs DUE, incl. device-failed from retrospective-cycle94, no decision block yet - a judgement item). This file is
NOT hidden from the launch gate: it imports stagekit and saves, so stage_prerun's classifier gates it and it carries its own
dry + prerun PASS records (graph tools/bench/graph_oploopcast_v0_c95.json, plan tools/bench/par1359_95_opplan.json).
PRIOR ART CHECKED (docs/toolkit-capabilities.md:27,34; `grep "^def " tools/gscript.py`; ls tools/recipes): only READERS exist
(OpLoopCast_v1 parallel_enabled/static_instances) and OpForLoopIn_v0 sets P on a NEW loop only. Shape = build_oploopcast_v1.py
(PN on the donor TMSC's output branch) + diag_c92b_anythread.py:90-105 (write PN, control on its one data sink, write
`error out` -> read PN `error in`, so the read runs strictly after the write). ROWS ONLY FROM THE FINALIZED PLAN (no uid,
terminal name, property id or position is typed here).
PREDICTION: A donor ES 1 + TMSC echo; B1-B5 no error; PN_W exactly 1 data sink, PN_R exactly 2 data outs; B6-B9 one new
panel object each; ES recorded after every row, gated 1 once assembled; scripted save; COLD ES 1 in a fresh LabVIEW.
A half-built op never stays on disk: the work copy is a scratch until the save lands.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c95_opbuild.log -- py -u tools/bench/diag_c95_opbuild.py"""
import json, os, subprocess, sys, time                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))  # noqa: E702
import stagekit as K                                                                     # noqa: E402
g = K.g
PL = json.load(open(os.path.join(K.BENCH, "par1359_95_opplan.json"), encoding="utf-8"))
T, ROWS, TM = PL["terms"], dict((r["id"], r) for r in PL["decisions"]), int(PL["tmsc"]["uid"])  # noqa: E702
SRC, LABELS = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), os.path.join(g.CLAUDEDEV, PL["labels_out"])  # noqa: E702
DRY = bool(getattr(g.report_all, "_dry", False))
g._run.__defaults__ = (6.0, 120.0)
s = K.Stage(SRC, PL["input"]["md5"], "par1359_95_build", work_name=PL["output"], preload=False, deadline_min=18.0,
            reserve_s=150.0, out_json=os.path.join(K.BENCH, "par1359_95_build.json"), task="95-4")
INV0 = set()


def idx(cls, uid):
    order = [o["uid"] for o in g.report_all(s.work, cls)]
    return order.index(uid) if uid in order else None


def node_of(uid):
    for c in range(80):
        nu, rows = g.node_terms_uid(s.work, 0, c)
        if nu == uid:
            return c, rows
        if not nu:
            break
    return None, []


def term_i(rows, name, src=None):
    return next((r["i"] for r in rows if r["name"] == name and (src is None or bool(r["is_source"]) == src)), None)


def purge():
    """diag_c92b_anythread.py:76-81: every scripting op may mint a stray Invoke in the target - delete the new ones."""
    junk = [u for u in g.uids(s.work, "Invoke") if u not in INV0]
    if junk:
        order = [o["uid"] for o in g.report_all(s.work, "Invoke")]
        for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
            g.delete_object(s.work, "Invoke", i, verify=False)
        g.remove_bad_wires_scripted(s.work)
    return junk


def step(rid, fn):
    rec = s._op("{0} {1}".format(ROWS[rid]["action"], rid), fn, ROWS[rid]["what"])
    junk, err2 = s.safe("purge after " + rid, purge)
    s.fact("{0}: stray Invokes deleted {1!r}".format(rid, junk))
    s.gate("E {0} no error ({1})".format(rid, ROWS[rid]["what"][:60]), not rec["err"] and not err2, rec["err"][:99] + err2, fatal=True)
    s.es(rid)
    return rec["result"]


def labels():
    return set((lab, ind) for _i, lab, ind in g.fp_labels(s.work))


def make(rid, uid, term):
    n, rows = node_of(uid)
    t, before = term_i(rows, term), labels()
    fn = g.create_control if ROWS[rid]["kind"] == "control" else g.create_indicator
    step(rid, lambda: fn(s.work, n, t))
    new = sorted(labels() - before)
    s.gate("L {0} {1} on {2!r}: exactly one new panel object".format(rid, ROWS[rid]["kind"], term), len(new) == 1, repr(new), fatal=True)
    return new[0][0] if new else "<unread {0}>".format(rid)


def body(_):
    s.start(); s.discard_work()                                       # a scratch until the save lands  # noqa: E702
    s.gate("A donor copy ExecState 1", s.es("donor") == 1, fatal=True)
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=[])          # whole-VI terminal table, by uid
    tr = [(r["term_name"], bool(r["is_source"]), r["owner_class"]) for r in lv["terminals"] if int(r["owner_uid"]) == TM]
    s.gate("A2 plan TMSC #{0} ({1}) carries ONE source {2!r}".format(TM, PL["tmsc"]["class"], T["cast_out"]),
           [x for x in tr if x == (T["cast_out"], True, PL["tmsc"]["class"])] == [(T["cast_out"], True, PL["tmsc"]["class"])], repr(tr), fatal=True)
    s.census(("Property", "Wire", "ControlTerminal", "Invoke"), "donor")
    INV0.update(g.uids(s.work, "Invoke"))
    w = int(step("B1", lambda: g.build_property(s.work, PL["prop_class"], [(PL["write_prop"], True)], tuple(PL["pos"]["pn_w"]))[-1]["uid"]) or 0)
    tc = PL["tmsc"]["class"]
    step("B2", lambda: g.wire(s.work, tc, idx(tc, TM), T["cast_out"], "Property", idx("Property", w), T["ref_in"], branch=True))
    r = int(step("B3", lambda: g.build_property(s.work, PL["prop_class"], [(p, False) for p in PL["read_props"]], tuple(PL["pos"]["pn_r"]))[-1]["uid"]) or 0)
    step("B4", lambda: g.wire(s.work, "Property", idx("Property", w), T["ref_out"], "Property", idx("Property", r), T["ref_in"]))
    step("B5", lambda: g.wire(s.work, "Property", idx("Property", w), T["err_out"], "Property", idx("Property", r), T["err_in"]))
    _n, wrows = node_of(w)
    _n, rrows = node_of(r)
    sink = [x["name"] for x in wrows if not x["is_source"] and x["name"] not in PL["std_terms"]]
    outs = [x["name"] for x in rrows if x["is_source"] and x["name"] not in PL["std_terms"]]
    s.fact("PN_W #{0} terminals {1!r}".format(w, [(x["i"], x["name"], x["is_source"], x["wire"]) for x in wrows]))
    s.fact("PN_R #{0} terminals {1!r}".format(r, [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rrows]))
    s.gate("B PN_W has exactly one data SINK", len(sink) == 1, repr(sink), fatal=True)
    s.gate("B' PN_R has exactly two data outputs", len(outs) == 2, repr(outs), fatal=True)
    pick = {"$sink0": (sink + [None])[0], "$out0": (outs + [None])[0], "$out1": (outs + [None, None])[1]}
    lab = json.load(open(os.path.join(K.BENCH, PL["labels_in"]), encoding="utf-8"))
    for rid in ("B6", "B7", "B8", "B9"):
        term = pick.get(ROWS[rid]["term"]) or T.get(ROWS[rid]["term"])
        lab[make(rid, w if ROWS[rid]["node"] == "pn_w" else r, term)] = ROWS[rid]["meaning"]
    step("B10", lambda: g.set_auto_error_handling(s.work, False))
    s.census(("Property", "Wire", "ControlTerminal", "Invoke"), "assembled")
    s.gate("C assembled ExecState 1", s.es("assembled") == 1, fatal=True)
    s.fact("LABEL MAP {0}".format(json.dumps(lab)))
    md = s.save()
    s.gate("D saved by script, md5 recorded", bool(md), repr(md), fatal=True)
    with open(LABELS, "w", encoding="utf-8") as f:
        json.dump(lab, f, indent=2)
    s.scratches.remove(s.work)                                        # saved: no longer a scratch
    s.restart()
    s.gate("D2 op ExecState 1 COLD (fresh LabVIEW)", s.es("cold") == 1)
    s.R["labels"], s.R["pn_w"], s.R["pn_r"], s.R["op_md5"] = lab, str(w), str(r), md


rc = K.run(body, s)
if not DRY:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4.0)   # noqa: E702
    print("LabVIEW gone at exit:", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), flush=True)
sys.exit(rc)
