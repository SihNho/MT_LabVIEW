r"""p63_build_s1gap - lean task P6-3, optional S1 leg on the gapped frame numbers: a byte copy of the S1 replay copy
replay\D1_s1_replay_20260925_075422.vi (126f8497, read-only) whose ONE call of replay\replay_get_buff_image.vi (the frame source
of P6-2's S1 leg) is replaced by the gap wrapper built by p63_build.py (path + md5 from p63_build.json). Saved only under
claudeDev\bench\lean. Gates as stage_replay_swap A2-A6 + a cold ExecState; LabVIEW killed and verified gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/lean_bench/p63_build_s1gap.log -- py -u tools/bench/lean_bench/p63_build_s1gap.py"""
import json, os, sys, time                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
IN, IN_MD5 = os.path.join(L.RP, "D1_s1_replay_20260925_075422.vi"), "126f84975fca9f6124432a7e4decd0c8"
OLD = "replay_get_buff_image.vi"
B = json.load(open(os.path.join(HERE, "p63_build.json"), encoding="utf-8"))["copies"]["gap_wrapper"]
GW, GW_MD5 = B["path"], B["md5"]
TS = time.strftime("%Y%m%d_%H%M%S")


def body(s):
    s.start(); P = s.work
    c0 = L.census(P)
    u = [k for k, v in c0.items() if os.path.basename(str(v)).lower() == OLD]
    s.gate("S0 exactly one call of %s" % OLD, len(u) == 1, c0, fatal=True)
    u = u[0]
    s.gate("S1 ExecState 1 before", s.es("before") == 1, fatal=True)
    E0 = L.edges(WB.read_live(P, fs_pairs=[]), {})
    r = g.replace_object(P, u, GW); s.fact("replace_object #%d -> gap wrapper: %r" % (u, r))
    s.gate("S2 replace: no error, new uid", not (r["err"] or r["err_replace"] or r["err_uid"]) and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]
    c1 = L.census(P); dd = dict((k, (c0.get(k), c1.get(k))) for k in set(c0) | set(c1) if c0.get(k) != c1.get(k))
    s.gate("S3 callee diff == exactly #%d -> gap wrapper" % u, set(dd) == {u, nu} and os.path.normcase(str(c1.get(nu))) == os.path.normcase(GW), dd)
    E1 = L.edges(WB.read_live(P, fs_pairs=[]), {nu: u})
    s.gate("S4 wire-edge diff 0 after remap (%d edges)" % len(E0), E0 == E1, (sorted(E0 - E1)[:6], sorted(E1 - E0)[:6]))
    s.gate("S5 ExecState 1 after", s.es("after") == 1, fatal=True)
    g.save(P); g.reset()
    m = K.md5(P); s.fact("SAVED %s md5 %s" % (P, m))
    s.R["copy"] = {"path": P, "md5": m, "old_uid": u, "new_uid": nu, "callee_diff": dict((str(k), v) for k, v in dd.items()), "edges": len(E0)}
    s.restart()
    s.gate("C1 ExecState 1 COLD", g.exec_state(P) == 1)
    g.reset()
    s.gate("C2 md5 unchanged by the cold load", K.md5(P) == m)
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + (("S1 replay copy", IN, IN_MD5), ("gap wrapper", GW, GW_MD5))
    st = St(IN, IN_MD5, "p63_build_s1gap", preload=False, deadline_min=28, work_dir=LEAN, work_name="D1_s1_replay_gap_%s.vi" % TS,
            pins=pins, task="lean-p6-3", out_json=os.path.join(HERE, "p63_build_s1gap.json"))
    sys.exit(K.run(body, st))
