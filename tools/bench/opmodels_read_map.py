r"""opmodels_read_map - card chat-S1 step A2. READ-ONLY, on dated scratch COPIES:
 (a) the bed claudeDev\D1_s4_loop17.vi (4b621946...): node -> diagram map = gscript.node_labels on EVERY Traverse 'Diagram'
     index (Nodes[] uids per diagram, in creation order = the index a writer op takes), plus build_d1_v0.owner_of for every
     Diagram whose owner class is WhileLoop/ForLoop (loop uid -> body diagram uid) -> tools/bench/opmodels/bed_s4_map.json
 (b) the saved L7-1a artefact claudeDev\D1_l7_1a_20260924_035656.vi (34aaadf1..., = S3 bed + move #376 + 2 SR pairs) :
     allterms.read_terms + report_all GObject -> tools/bench/opmodels/bed_l7_1a.json, so the move model is checked against
     the TERMINAL-level after-state, not only the uid-edge diff printed in stage_d1_l7_1a.log.
Step B's targets are chosen offline from these files. No mutation, no VI run, no original opened.
PRIOR ART: opmodels_read_bed.py (step A, 12/0), stagekit, gscript.node_labels, build_d1_v0.owner_of - unchanged.
PREDICTION: 173 diagrams mapped, every one read without error; sum of Nodes[] over diagrams within 5 % of the non-terminal
node count; 23 loop bodies resolved (6 While + 17 For); #23041 -> body #23405; L7-1a dump > 5000 terms; files left [].
    MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/opmodels_read_map.log -- py -u tools/bench/opmodels_read_map.py"""
import json, os, sys, time                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, allterms as A                                  # noqa: E401,E402

BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_s4_loop17.vi"), "4b621946492da3d2fbb96b6053e715ec"
L71A, L71A_MD5 = os.path.join(K.CLAUDEDEV, "D1_l7_1a_20260924_035656.vi"), "34aaadf14091ee156e0950725de48bdf"
OUT = os.path.join(K.BENCH, "opmodels")
PINS = tuple(K.DEFAULT_PINS) + (("S4 loop17 bed", BED, BED_MD5), ("L7-1a file", L71A, L71A_MD5))


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work()                                                    # noqa: E702
    h0 = K.mod("bench_prep").labview_handles(); s.fact("HANDLES after open {0!r}".format(h0))  # noqa: E702
    B = K.mod("build_d1_v0")
    diags = g.report_all(s.work, "Diagram")
    t0, nodes, bad = time.time(), {}, []
    for d in diags:
        rows, err = g.node_labels(s.work, d["i"], strict=False)
        nodes[str(d["uid"])] = {"i": d["i"], "owner_class": d["owner"], "nodes": [r["uid"] for r in rows],
                                "labels": [r["label"] for r in rows], "err": err}
        if err:
            bad.append((d["uid"], err))
    s.fact("NODE MAP: {0} diagrams, {1} Nodes[] rows, {2:.1f} s, errors {3}".format(
        len(diags), sum(len(v["nodes"]) for v in nodes.values()), time.time() - t0, bad[:5]))
    s.gate("M1 every diagram's Nodes[] read without error", not bad, bad[:5])
    loops = {}
    for d in diags:
        if d["owner"] in ("WhileLoop", "ForLoop", "TimedLoop"):
            o, e = s.safe("owner_of #{0}".format(d["uid"]), lambda u=d["uid"]: B.owner_of(s.work, u))
            loops[str(d["uid"])] = {"loop_class": d["owner"], "owner": o}
    s.fact("LOOP BODIES: {0}".format(loops))
    ok = any(v["owner"] and v["owner"][1] == 23041 for k, v in loops.items() if k == "23405")
    s.gate("M2 body #23405 is owned by WhileLoop #23041", ok, loops.get("23405"))
    with open(os.path.join(OUT, "bed_s4_map.json"), "w", encoding="utf-8") as f:
        json.dump({"file": os.path.basename(BED), "md5": BED_MD5, "diagrams": diags, "nodes": nodes, "loops": loops},
                  f, default=str)
    sc = s.scratch("l71a", source=L71A)
    terms, dt = A.read_terms(sc)
    objs = g.report_all(sc, "GObject")
    with open(os.path.join(OUT, "bed_l7_1a.json"), "w", encoding="utf-8") as f:
        json.dump({"file": os.path.basename(L71A), "md5": L71A_MD5, "terms": terms, "objs": objs}, f, default=str)
    s.gate("M3 L7-1a dump: > 5000 terminal rows", len(terms) > 5000, (len(terms), round(dt, 1)))
    s.drop_scratch(sc, "H4 l71a")
    s.fact("HANDLES end of work {0!r} (open {1!r})".format(K.mod("bench_prep").labview_handles(), h0))


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "opmodels_read_map", preload=False, deadline_min=22, pins=PINS)
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
