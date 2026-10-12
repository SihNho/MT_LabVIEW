# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/task_170-a3-4.json
# ---
r"""diag_c170_a3_4_callees - card 170-a3-4 step 1, READ-ONLY. The SubVI callee names per node uid of the P6 bed
claudeDev\D1_ring_p6_20261012_212645.vi (c2d9c13c), read from a BYTE COPY (Stage work copy beside the bed in claudeDev,
same relative links; never saved; deleted by Stage.close). FOUND FIRST: diag_replay_lib.census (g.subvis per Diagram, the
SAME reader stage_replay_swap.py A2 uses at launch, :41) and diag_c170_a2_3_graph.py (Stage shape, called helpers). No new
reader. Output tools/bench/graph_ring_p6_callees_<ts>.json = {vi, md5, source, graph_summary: {subvi_calls: [{node_uid,
subvi_name, path}]}} in wiki_build's subvi_calls row shape (wiki_build.py:290). It carries NO terminals/objs on purpose, so
stage_prerun.find_graph (:265-284) keeps resolving md5 c2d9c13c to graph_ring_p6_20261012_212645.json (fbc7b7ee unedited).
Pins: the bed (input) + plan 170's extra_pins (card hygiene list).
PREDICTION: K1 input md5 c2d9c13c; G1 census > 0 calls; G2 #6810 -> 'get buff image-lost frames.vi';
G3 #22692 -> 'IMAQdx Get Image.vi'; hygiene (scratch deleted, pins unchanged, refs balanced); LabVIEW gone.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c170_a3_4_callees.log -- py -u tools/bench/diag_c170_a3_4_callees.py"""
import json, os, sys, time                                                               # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
K = L.K
PLAN = json.load(open(os.path.join(K.BENCH, "plans", "plan_replay_swap_170.json"), encoding="utf-8"))
BED, BED_MD5 = os.path.join(K.CLAUDEDEV, PLAN["input"]["vi"].split("\\", 1)[1]), PLAN["input"]["md5"]
WANT = dict((int(r["uid"]), r["old_callee"]) for r in PLAN["swaps"])
OUT = os.path.join(K.BENCH, "graph_ring_p6_callees_{0}.json".format(time.strftime("%Y%m%d_%H%M%S")))


def body(s):
    s.start(); s.scratches.append(s.work)
    c = L.census(s.work)
    rows = [{"node_uid": u, "subvi_name": os.path.basename(str(p)), "path": str(p)} for u, p in sorted(c.items())]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"vi": BED, "md5": BED_MD5, "source": "diag_c170_a3_4_callees.py: diag_replay_lib.census on a byte copy",
                   "graph_summary": {"subvi_calls": rows}}, f, indent=0)
    s.gate("G1 callee census of the bed copy has calls ({0})".format(len(rows)), len(rows) > 0, OUT)
    for u, want in sorted(WANT.items()):
        s.gate("G{0} #{1} calls {2}".format(2 if u == 6810 else 3, u, want), os.path.basename(str(c.get(u, ""))) == want, c.get(u))
    s.fact("GRAPH {0} md5 {1}".format(OUT, K.md5(OUT))); s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self)
        return K.Stage.summary(self)


if __name__ == "__main__":
    st = St(BED, BED_MD5, "diag_c170_a3_4_callees", fresh=True, preload=False, deadline_min=16, reserve_s=120,
            work_dir=K.CLAUDEDEV, pins=tuple(K.DEFAULT_PINS[:1]) + tuple((a, os.path.join(K.CLAUDEDEV, b), m) for a, b, m in PLAN["extra_pins"]),
            task="170-a3-4 P6 callee graph", out_json=os.path.join(K.BENCH, "diag_c170_a3_4_callees_stage.json"))
    sys.exit(K.run(body, st))
