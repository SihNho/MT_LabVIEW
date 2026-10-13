r"""p63_diag_wait - lean task P6-3 diagnostic (build runs 2/3 stopped at ExecState 0 after the Wait edit). On a SCRATCH byte copy of
the P6 replay copy (never saved, deleted at the end): D1 read stability (edges read twice, no edit); D2 Wait (ms) alone on d23166 ->
ExecState now / +5 s / +20 s + edge diff; D3 the control on its input -> ExecState; D4 when ExecState is still not 1, the full
Error List (errorlist_check functions, live session, as diag_c167_a1_1_rbw.el_read). Facts only.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/lean_bench/p63_diag_wait.log -- py -u tools/bench/lean_bench/p63_diag_wait.py"""
import json, os, sys, time                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
IN, IN_MD5 = os.path.join(LEAN, "D1_ring_p6_replay_20261013_135743.vi"), "09a23608c223a9a31ea6ca3638c1241c"
BODY12 = 23166


def E(p):
    return L.edges(WB.read_live(p, fs_pairs=[]), {})


def el(s, W):
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE))))
    import errorlist_check as EC
    EC._lv_imports()
    out = os.path.join(HERE, "p63_diag_wait_errorlist.json")
    R = {"errors": []}
    try:
        g.open_panel(W); time.sleep(1.0)                                                  # noqa: E702
        R["block_diagram_open"] = EC.open_diagram(W, R)
        r = EC.E.read(W, out.replace(".json", "_raw.json"), log=lambda t: print(t, flush=True), on_item=EC.make_on_item(W, R))
        R.update({k: r.get(k) for k in ("n_reported", "items", "categories")})
    except Exception as e:                                                             # noqa: BLE001
        R["errors"].append("%s: %s" % (type(e).__name__, str(e)[:200]))
    json.dump(R, open(out, "w", encoding="utf-8"), indent=1, default=str)
    for it in (R.get("items") or [])[:20]:
        s.fact("EL item %r" % ({k: it.get(k) for k in ("raw", "detail", "object", "reason")},))
    s.fact("EL n_reported %r errors %r" % (R.get("n_reported"), R["errors"]))


def body(s):
    s.start(); W = s.work; s.scratches.append(W)
    s.fact("D0 ExecState %r" % s.es("open"))
    e0 = E(W); e0b = E(W)
    s.fact("D1 read twice, no edit: equal %s (+%d -%d)" % (e0 == e0b, len(e0b - e0), len(e0 - e0b)))
    wu = g.create_primitive_nested(W, BODY12, "Wait (ms)", (20354, 11728))
    s.fact("D2 Wait #%d; ExecState now %r" % (wu, s.es("wait now")))
    time.sleep(5); s.fact("D2 ExecState +5 s %r" % s.es("wait +5"))                      # noqa: E702
    time.sleep(15); es2 = s.es("wait +20"); s.fact("D2 ExecState +20 s %r" % es2)        # noqa: E702
    e1 = E(W)
    s.fact("D2 edge diff after Wait only: +%r -%r" % (sorted(e1 - e0), sorted(e0 - e1)))
    if es2 != 1:
        el(s, W)
        return
    t = 1
    rec = g.create_control_nested(W, wu, t, value=100)
    s.fact("D3 control %r" % rec)
    time.sleep(3); es3 = s.es("control +3"); s.fact("D3 ExecState %r" % es3)              # noqa: E702
    e2 = E(W)
    s.fact("D3 edge diff vs start: +%r -%r" % (sorted(e2 - e0), sorted(e0 - e2)))
    if es3 != 1:
        el(s, W)


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    st = St(IN, IN_MD5, "p63_diag_wait", preload=False, deadline_min=28, work_dir=LEAN,
            work_name="scratch_p63_diag_wait_%s.vi" % time.strftime("%Y%m%d_%H%M%S"), pins=tuple(K.DEFAULT_PINS[:1]),
            task="lean-p6-3", out_json=os.path.join(HERE, "p63_diag_wait.json"))
    sys.exit(K.run(body, st))
