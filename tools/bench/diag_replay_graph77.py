r"""diag_replay_graph77 - card 77-4, READ-ONLY. (1) The offline graph JSON of the pane base (65e999d9) that
tools/stage_prerun.py needs for the dry run / pre-run of tools/recipes/stage_replay_standins.py (find_graph keys on md5);
same shape and reader as p0_c69_census.py:36-41 (wiki_build.read_live on a dated copy). (2) The IMAQdx mode enum #581 in
a scratch copy of the get-buff copy, read with build_opcreateconstonterm_v0.read_const (m8 plan PD20(c) last-but-one).
Nothing is saved; no VI is run except op VIs; copies deleted.
PREDICTION: K1 base md5; G1 graph >0 terminals and objs, written; E1 #581 read with err '' (value RECORDED, not predicted).
    py tools/bgrun.py --material --max-min 12 --log tools/bench/replay_graph77.log -- py -u tools/bench/diag_replay_graph77.py"""
import json, os, sys                                                                     # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
C = K.mod("build_opcreateconstonterm_v0")


def body(s):
    s.start(); lv = K.mod("wiki_build").read_live(s.work, fs_pairs=[])
    out = os.path.join(K.BENCH, "graph_replay_pane_base_77.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"vi": L.BASE, "md5": L.BASE_MD5, "terminals": lv["terminals"], "objs": lv["objs"], "secs": lv["secs"]}, f)
    s.gate("G1 pane-base graph written ({0} terminals, {1} objs)".format(len(lv["terminals"]), len(lv["objs"])),
           lv["terminals"] and lv["objs"], out)
    s.R["objs"] = [(o["uid"], o["class"]) for o in lv["objs"]]
    sc = s.scratch("gb", source=L.GB)
    cs = [(o["uid"], o["class"]) for o in g.report_all(sc, "Constant") if int(o["uid"]) == 581]
    r = C.read_const(sc, 581); s.R["mode581"] = {"report_all": cs, "read": r}
    s.gate("E1 #581 read, err ''", not r.get("err"), r)
    s.fact("MODE581 {0} {1}".format(cs, r))
    s.drop_scratch(sc, "E1"); s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self)
        return K.Stage.summary(self)


if __name__ == "__main__":
    st = St(L.BASE, L.BASE_MD5, "replay_graph77", fresh=True, preload=False, deadline_min=10, reserve_s=120,
            pins=tuple(K.DEFAULT_PINS[:1]) + L.pins(), task="77-4 graph + #581",
            out_json=os.path.join(K.BENCH, "replay_graph77.json"))
    sys.exit(K.run(body, st))
