r"""selftest_make_default - card 76-6, m8 plan Pre-decided 19(b): gscript.make_default (patched: op error checked, every
value read back after Make-Current-Default and after the save, RAISES on mismatch) on a scratch VI, then a COLD read in a
fresh LabVIEW. Existing verbs only (checked first): EMPTY_v0 copy, drop_subvi, create_control, diag_replay_lib.str_array_ctl.
Scratch = a work copy of EMPTY_v0 with IMAQ Create -> IMAQ ImageToArray (wired so the VI is not broken; nothing is RUN).
PREDICTION: S1 scalar control on IMAQ Create 'Border Size', numeric-array control on ImageToArray's rectangle input, and a
free String[] control exist; S2 make_default({scalar: 3, array: [1,2,3,4], String[]: 10044 frame paths}) returns without
raising; S3 fresh LabVIEW, cold read: all three equal (count 3/3); S4 a negative case: make_default with a label that is
not on the panel RAISES. Scratch deleted, LabVIEW gone.
    MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/selftest_make_default.log -- py -u tools/bench/selftest_make_default.py"""
import os, sys                                                                           # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g


def body(s):
    s.start(); W = s.work
    try:
        cells(s, W)
    finally:
        s.drop_scratch(W, "H4 self-test scratch")


def cells(s, W):
    ids = {}
    for k, p, xy in (("c", L.C_VI, (100, 300)), ("a", L.A_VI, (500, 300))):
        b = g.uids(W, "SubVI"); g.drop_subvi(W, p, 0, xy); ids[k] = [u for u in g.uids(W, "SubVI") if u not in b][0]
    sx = lambda k: L.fidx(W, "SubVI", ids[k])                                            # noqa: E731
    g.wire(W, "SubVI", sx("c"), "New Image", "SubVI", sx("a"), "Image")
    wt = L.walk(W, 0); s.fact("ImageToArray terms {0}".format([(r["name"], r["is_source"]) for r in wt[ids["a"]][2]]))
    labs = {}          # run 1 (05:15): ExecState 0 - IMAQ Create's 'Image Name' is REQUIRED; it gets a control too ("n")
    for k, node, pred in (("n", "c", lambda n: n == "Image Name"), ("c", "c", lambda n: n == "Border Size"),
                          ("a", "a", lambda n: "ectangle" in (n or ""))):
        wt = L.walk(W, 0); nm = L.tname(wt[ids[node]][2], pred, False)
        b = {l for _i, l, _d in g.fp_labels(W)}
        g.create_control(W, wt[ids[node]][0], L.term(wt[ids[node]][2], nm, False)["i"])
        labs[k] = [l for _i, l, _d in g.fp_labels(W) if l not in b][-1]
    labs["p"] = L.str_array_ctl(s, W, "S1p")
    s.fact("labels {0}".format(labs))
    s.gate("S1 four controls, scratch ExecState 1", len(set(labs.values())) == 4 and g.exec_state(W) == 1, labs, fatal=True)
    want = {labs["c"]: 3, labs["a"]: [1, 2, 3, 4], labs["p"]: L.frame_paths()}
    try:
        g.make_default(W, want); ok, e = True, None
    except Exception as ex:                                                              # noqa: BLE001
        ok, e = False, str(ex)[:300]
    s.gate("S2 make_default returned without raising (op error + in-memory read-back)", ok, e, fatal=True)
    try:
        g.make_default(W, {"no such control 76-6": 1}); neg = None
    except Exception as ex:                                                              # noqa: BLE001
        neg = str(ex)[:200]
    s.gate("S4 negative: an unknown label RAISES", neg is not None, neg)
    s.restart(); n = 0; got = {}
    with g.vi_ref(W) as v:
        for lab, x in want.items():
            y = v.GetControlValue(lab); got[lab] = y if not isinstance(y, (list, tuple)) else ("len", len(y), list(y[:1]))
            eq = (list(y) == list(x)) if isinstance(x, list) else float(y) == float(x)
            n += int(bool(eq))
    s.fact("cold read {0}".format(got)); s.R["cold_count"] = n
    s.gate("S3 cold read after save: {0}/3 values equal (scalar, numeric array, path String[] 10044)".format(n), n == 3, got)


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self)
        return K.Stage.summary(self)


if __name__ == "__main__":
    OLD = os.path.join(K.CLAUDEDEV, "selftest_make_default_20260925_051505.vi")          # run 1's leftover (stopped early)
    if os.path.exists(OLD):
        os.remove(OLD); print("removed run-1 leftover", OLD, flush=True)
    st = St(L.EMPTY, K.md5(L.EMPTY), "selftest_make_default", preload=False, deadline_min=10, pins=L.pins(), task="76-6",
            out_json=os.path.join(K.BENCH, "selftest_make_default.json"))
    sys.exit(K.run(body, st))
