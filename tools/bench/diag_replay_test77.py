r"""diag_replay_test77 - card 77-4 PD18(a) functional tests of the three replay VIs saved by
tools/recipes/stage_replay_standins.py (hashes from tools/bench/replay_vis_77.json). REUSED, not rewritten:
diag_replay_gbtest.harness / call / WANT (IMAQ Create -> VUT -> IMAQ ImageToArray scratch harness; WANT = md5 of the
U8 array of the SOURCE file of f00000..f00002 read by PIL from the manifest). Only replay VIs + their harness run.
PREDICTION: P0 the three VIs' md5 == replay_vis_77.json; T1 fresh LabVIEW, get-buff b=8217 then 8218 -> f00000 then
f00001 (md5 of the array or its transpose), current image number == b, Missed frames? TRUE; T2 fresh LabVIEW b=5 ->
f00000; T3 fresh LabVIEW, cal 3 calls -> f00000/1/2, Buffer Number Out 0,1,2; H the three VIs unchanged after.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/replay_test77.log -- py -u tools/bench/diag_replay_test77.py"""
import json, os, sys                                                                     # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
import diag_replay_gbtest as GT                                                          # noqa: E402
K, g = L.K, L.g
VIS = json.load(open(os.path.join(K.BENCH, "replay_vis_77.json"), encoding="utf-8"))
MINE = tuple((k, VIS[k]["path"], VIS[k]["md5"]) for k in ("buf", "cal", "gbf"))


def body(s):
    s.start(); s.discard_work()
    s.gate("P0 the three replay VIs == replay_vis_77.json", all(K.md5(p) == m for _k, p, m in MINE), MINE, fatal=True)
    H1, l1 = GT.harness(s, "gb", L.GBF); H2, l2 = GT.harness(s, "cal", L.CAL)
    im = lambda o: next((v for n, v in o["out"].items() if "image number" in n), None)                # noqa: E731
    ms = lambda o: next((v for n, v in o["out"].items() if "issed" in n), None)                       # noqa: E731
    s.restart()
    for i, b in enumerate((8217, 8218)):
        o = GT.call(s, H1, l1, "gb", b)
        s.gate("T1 get-buff b={0} -> f{1:05d} pixels, image number == b, Missed TRUE".format(b, i),
               GT.WANT[i] in (o["md5"], o["md5_T"]) and im(o) == b and ms(o) is True, (o["md5"], o["md5_T"], GT.WANT[i], im(o), ms(o)))
    s.restart(); o = GT.call(s, H1, l1, "gb", 5)
    s.gate("T2 fresh load get-buff b=5 -> f00000", GT.WANT[0] in (o["md5"], o["md5_T"]), (o["md5"], GT.WANT[0], im(o), ms(o)))
    s.restart()
    for i in range(3):
        o = GT.call(s, H2, l2, "cal"); bo = next((v for n, v in o["out"].items() if n.startswith("Buffer Number Out")), None)
        s.gate("T3 cal call {0} -> f{0:05d}, Buffer Number Out {0}".format(i), GT.WANT[i] in (o["md5"], o["md5_T"]) and bo == i, (o["md5"], GT.WANT[i], bo))
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self)
        return K.Stage.summary(self)


if __name__ == "__main__":
    lo = os.path.join(K.CLAUDEDEV, "replay_graph77_20260925_061109.vi")          # left by diag_replay_graph77 run 1 (H6)
    if os.path.exists(lo):                     # archive/peer/2026-09-25-replay-graph77-h6.md s4: delete only if unchanged
        lm = K.md5(lo); print("  FACT  leftover {0} md5 {1} (input {2}) -> {3}".format(os.path.basename(lo), lm, L.BASE_MD5,
              "deleted" if lm == L.BASE_MD5 else "KEPT, differs"), flush=True)
        if lm == L.BASE_MD5:
            os.remove(lo)
    st = St(L.BASE, L.BASE_MD5, "replay_test77", preload=False, deadline_min=26, reserve_s=150,
            pins=tuple(K.DEFAULT_PINS[:1]) + L.pins() + MINE, task="77-4 PD18(a)",
            out_json=os.path.join(K.BENCH, "replay_test77.json"))
    sys.exit(K.run(body, st))
