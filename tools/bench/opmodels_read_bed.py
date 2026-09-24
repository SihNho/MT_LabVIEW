r"""opmodels_read_bed - card chat-S1 step A (docs/stage-simulator-plan.md "Op effect models", build order 3).
READ-ONLY dumps, on dated scratch COPIES, of (a) the current bed claudeDev\D1_s4_loop17.vi (4b621946...) and (b) the S3 bed
claudeDev\D1_s3_loop15.vi (1a11d92a..., the input of L7-1a, for the move-model check against stage_d1_l7_1a.log). Per file:
allterms.read_terms (every terminal), report_all('GObject'), report_all('Diagram'). Written to
tools/bench/opmodels/bed_<tag>.json. The targets of step B are chosen OFFLINE from these files (split rule: every step leaves
a file). No mutation, no VI run, no original opened (preload=False).
PRIOR ART: stagekit.Stage (start/scratch/discard_work/close) + allterms.read_terms + gscript.report_all, unchanged. No new op.
PREDICTION: K1/K3 pass; 2 JSON files written; each has > 5000 terminal rows and > 100 Diagram rows; S3 dump holds #376
owned-terminals (12) and D4 bed holds #376 too; refs opened == closed; files left [] ; pins hold.
    MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/opmodels_read_bed.log -- py -u tools/bench/opmodels_read_bed.py"""
import json, os, sys, time                                                         # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, allterms as A                                  # noqa: E401,E402

BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_s4_loop17.vi"), "4b621946492da3d2fbb96b6053e715ec"
S3, S3_MD5 = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f"
OUT = os.path.join(K.BENCH, "opmodels")
PINS = tuple(K.DEFAULT_PINS) + (("S3 loop15 bed", S3, S3_MD5), ("S4 loop17 bed", BED, BED_MD5))


def dump(s, path, tag):
    t0 = time.time()
    terms, dt = A.read_terms(path)
    objs = g.report_all(path, "GObject")
    diags = g.report_all(path, "Diagram")
    rec = {"file": os.path.basename(path), "tag": tag, "read_terms_s": round(dt, 1), "terms": terms, "objs": objs,
           "diagrams": diags, "exec_state": s.es("dump " + tag, path), "read_s": round(time.time() - t0, 1)}
    fn = os.path.join(OUT, "bed_{0}.json".format(tag))
    with open(fn, "w", encoding="utf-8") as f:
        json.dump(rec, f, default=str)
    n376 = sum(1 for r in terms if r["owner_uid"] == 376)
    s.fact("DUMP {0}: {1} terms, {2} GObjects, {3} Diagrams, #376 terminals {4}, {5:.1f} s -> {6}".format(
        tag, len(terms), len(objs), len(diags), n376, rec["read_s"], fn))
    s.gate("D {0} dump sizes plausible (terms > 5000, Diagram > 100, #376 has 12 terminals)".format(tag),
           len(terms) > 5000 and len(diags) > 100 and n376 == 12, (len(terms), len(diags), n376))


def body(s):
    print(__doc__, flush=True)
    os.makedirs(OUT, exist_ok=True)
    s.start(); s.discard_work()                                                    # noqa: E702
    s.fact("HANDLES after open {0!r}".format(K.mod("bench_prep").labview_handles()))
    dump(s, s.work, "s4_loop17")
    sc = s.scratch("s3", source=S3)
    dump(s, sc, "s3_loop15")
    s.drop_scratch(sc, "H4 s3")


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "opmodels_read_bed", preload=False, deadline_min=18, pins=PINS)
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
