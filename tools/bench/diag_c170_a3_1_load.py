# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/task_170-a3-1.json
# ---
r"""diag_c170_a3_1_load - card 170-a3-1, PD411(b) lever (b), READ-ONLY: ONE-open session measuring LabVIEW's private MB after
loading replay_imaqdx_get_image_buf.vi (a89dafc1), the input the paced recipe opens, for memory_model.json load_by_vi.
PRIOR ART (same measurement, called not copied): diag_c136_1_graph.py:30-34 (Stage.start fresh -> discard_work ->
K.private_bytes -> 'MEM after load: X MB private'); Stage args of diag_c170_a2_3_graph.py:41-43 (scratch copy beside the input in
claudeDev\replay so relative links hold; deleted at close); diag_replay_lib.tail (LabVIEW gone).
PREDICTION: K1 input md5 a89dafc1; M1 MEM after load measured (> 0 MB); input md5 unchanged; scratch deleted; LabVIEW gone.
    py tools/bgrun.py --material --max-min 8 --log tools/bench/diag_c170_a3_1_load.log -- py -u tools/bench/diag_c170_a3_1_load.py"""
import os, sys                                                                           # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
K = L.K
BUF_MD5 = "a89dafc1db03feef7b528f0dd4fcc692"


def body(s):
    s.start(); s.discard_work()
    mb = round((K.private_bytes() or 0) / 1e6, 1)
    s.R["mem"] = {"after_load_mb": mb, "handles": K.mod("bench_prep").labview_handles()}
    s.fact("MEM after load: {0} MB private; handles {1}".format(mb, s.R["mem"]["handles"]))
    s.gate("M1 MEM after load measured ({0} MB private)".format(mb), mb > 0, mb)
    s.gate("I input md5 unchanged", K.md5(L.BUF) == BUF_MD5, K.md5(L.BUF))
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self)
        return K.Stage.summary(self)


if __name__ == "__main__":
    st = St(L.BUF, BUF_MD5, "diag_c170_a3_1_load", fresh=True, preload=False, deadline_min=6, reserve_s=90,
            work_dir=L.RP, pins=tuple(K.DEFAULT_PINS[:1]), task="170-a3-1 buf load",
            out_json=os.path.join(K.BENCH, "diag_c170_a3_1_load.json"))
    sys.exit(K.run(body, st))
