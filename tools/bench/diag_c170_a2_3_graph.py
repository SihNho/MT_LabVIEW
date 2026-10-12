# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/task_170-a2-3.json
# ---
r"""diag_c170_a2_3_graph - card 170-a2-3, READ-ONLY. The offline graph JSON of replay_imaqdx_get_image_buf.vi (a89dafc1)
that tools/stage_prerun.py needs for the dry run / pre-run of tools/recipes/stage_replay_paced60.py (find_graph keys on the
Stage input md5; none existed: grep of tools/bench/*.json for a89dafc1 found no graph_*). Same reader and shape as
tools/bench/diag_replay_graph77.py:17-21 (wiki_build.read_live on a scratch copy); helpers from diag_replay_lib (called).
The scratch copy lives beside the input (claudeDev\replay, same relative links) and is deleted by Stage.close (H4).
PREDICTION: K1 input md5 a89dafc1; G1 graph > 0 terminals and objs, written; H2/H3/H4/H5 hygiene; H9 LabVIEW gone.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c170_a2_3_graph.log -- py -u tools/bench/diag_c170_a2_3_graph.py"""
import json, os, sys                                                                     # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
K = L.K
BUF_MD5 = "a89dafc1db03feef7b528f0dd4fcc692"
OUT = os.path.join(K.BENCH, "diag_c170_a2_3_graph_buf.json")


def body(s):
    s.start(); s.scratches.append(s.work)
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=[])
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"vi": L.BUF, "md5": BUF_MD5, "terminals": lv["terminals"], "objs": lv["objs"], "secs": lv["secs"]}, f)
    s.gate("G1 buf graph written ({0} terminals, {1} objs)".format(len(lv["terminals"]), len(lv["objs"])),
           lv["terminals"] and lv["objs"], OUT)
    s.fact("GRAPH {0} md5 {1}".format(OUT, K.md5(OUT))); s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self)
        return K.Stage.summary(self)


if __name__ == "__main__":
    st = St(L.BUF, BUF_MD5, "diag_c170_a2_3_graph", fresh=True, preload=False, deadline_min=8, reserve_s=90,
            work_dir=L.RP, pins=tuple(K.DEFAULT_PINS[:1]), task="170-a2-3 buf graph",
            out_json=os.path.join(K.BENCH, "diag_c170_a2_3_graph_stage.json"))
    sys.exit(K.run(body, st))
