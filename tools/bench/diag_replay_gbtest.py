r"""diag_replay_gbtest - card 76-5 pass lines 4-7 (m8 plan PD16(b), PD17(e'), PD18(a)): the get-buff copy with ONLY #529 ->
replay_imaqdx_get_image_buf.vi (gscript.replace_object, PD15), then RUN tests of it and of the cal stand-in through two
scratch harnesses (IMAQ Create -> VUT -> IMAQ ImageToArray, the chain of build_harness_display.py:145-156).
Readers reused: wiki_build.read_live + diag_swap_measure.edges (P6 of 75-4), g.subvis census, g.conpane/fp_labels.
PREDICTION: G1 before: #529 calls IMAQdx Get Image.vi; G2 replace no error; callee census diff == exactly #529 -> buf
stand-in; wire-edge diff after remap new->529 == empty; ES 1; scripted save; G3 pane per slot (label, direction) ==
source; G4 COLD ES 1 in a fresh LabVIEW. T1 fresh load, get-buff b=8217 then 8218: U8 pixel md5 == f00000 then f00001
(frame's SOURCE file read by PIL), image number == b, Missed frames? TRUE; T2 new LabVIEW, b=5 -> f00000; T3 new LabVIEW,
cal stand-in 3 calls -> f00000/1/2, Buffer Number Out 0,1,2. Pixel md5 is gated on the array as read OR its transpose
(ImageToArray's axis order is reported, not assumed).
    py tools/bgrun.py --material --max-min 45 --log tools/bench/replay_vis_76d_test.log -- py -u tools/bench/diag_replay_gbtest.py"""
import os, sys, json, hashlib                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
import numpy as np                                                                       # noqa: E402
from PIL import Image                                                                    # noqa: E402
K, g = L.K, L.g
WB, PRE = K.mod("wiki_build"), L.pins()
MAN = json.load(open(L.MAN, encoding="utf-8"))
h = lambda a: hashlib.md5(np.ascontiguousarray(a).tobytes()).hexdigest()                 # noqa: E731
WANT = [h(np.asarray(Image.open(os.path.join(MAN["source_dir"], MAN["frames"][i]["source"])))) for i in range(3)]


def harness(s, tag, vut):
    H = s.scratch("h" + tag, source=L.EMPTY); g.open_panel(H); ids = {}
    for k, p, xy in (("c", L.C_VI, (100, 300)), ("v", vut, (400, 300)), ("a", L.A_VI, (700, 300))):
        b = g.uids(H, "SubVI"); g.drop_subvi(H, p, 0, xy); ids[k] = [u for u in g.uids(H, "SubVI") if u not in b][0]
    wt = L.walk(H, 0); vr = wt[ids["v"]][2]; sx = lambda k: L.fidx(H, "SubVI", ids[k])  # noqa: E731
    s.fact("{0} VUT terms {1}".format(tag, [(r["name"], r["is_source"]) for r in vr]))
    g.wire(H, "SubVI", sx("c"), "New Image", "SubVI", sx("v"), "Image In")          # run 1: "mage" also hit 'current image number'
    g.wire(H, "SubVI", sx("v"), "Image Out", "SubVI", sx("a"), "Image")
    lab = {}
    for k, pred, src in (("c", lambda n: n == "Image Name", False), ("v", lambda n: "uffer" in n, False),
                         ("a", lambda n: n == "Image Pixels (U8)", True), ("v", lambda n: n and n not in ("Image Out", "Session Out"), True),
                         ("c", lambda n: n.startswith("error out"), True), ("a", lambda n: n.startswith("error out"), True)):
        wt = L.walk(H, 0)
        for r in [r for r in wt[ids[k]][2] if pred(r["name"]) and bool(r["is_source"]) == src and not r["wire"]]:
            b = {l for _i, l, _d in g.fp_labels(H)}
            (g.create_indicator if src else g.create_control)(H, L.walk(H, 0)[ids[k]][0], r["i"])
            lab[(k, r["name"])] = [l for _i, l, _d in g.fp_labels(H) if l not in b][-1]
    s.fact("{0} harness labels {1}".format(tag, lab)); s.gate("{0} harness ExecState 1".format(tag), g.exec_state(H) == 1, fatal=True)
    g.save(H); return H, lab


def call(s, H, lab, tag, b=None):
    vi = g.op(H); vi.SetControlValue(lab[("c", "Image Name")], "replay76_" + tag)
    if b is not None:
        vi.SetControlValue([v for (k, n), v in lab.items() if k == "v" and "uffer" in n and n in ("Buffer to extract", "Buffer Number In")][0], int(b))
    g._run(vi)
    v = vi.GetControlValue(lab[("a", "Image Pixels (U8)")])
    # card 78-2: np.array(v, dtype=uint8) kept only COLUMN 0 of the 1024x1280 frame (replay_test78.log shape (1024,);
    # diag_replay_slice78.log: that md5 == col0 of f0000k for k = 0,1,2). Each row arrives as its own COM array
    # (bytes-like for U8), so every row is converted explicitly and the row type is on the FACT line.
    rt = type(v[0]).__name__ if len(v) else None
    a = np.array([np.frombuffer(bytes(r), dtype=np.uint8) if isinstance(r, (bytes, bytearray, memoryview))
                  else np.asarray(r, dtype=np.uint8) for r in v]) if len(v) else np.array([], dtype=np.uint8)
    s.fact("{0} pixel read: {1} rows of {2}, array {3}".format(tag, len(v), rt, a.shape))
    out = dict((n, vi.GetControlValue(v)) for (k, n), v in lab.items() if k == "v" and not n.startswith("Buffer to") and n != "Buffer Number In")
    out.update(("err " + k, str(vi.GetControlValue(v))[:120]) for (k, n), v in lab.items() if n.startswith("error"))
    r = {"shape": a.shape, "md5": h(a), "md5_T": h(a.T), "out": out}; s.fact("CALL {0} b={1}: {2}".format(tag, b, r)); return r


def body(s):
    s.start(); T = s.work
    c0 = L.census(T); s.gate("G1 #529 calls IMAQdx Get Image.vi", str(c0.get(529, "")).endswith("IMAQdx Get Image.vi"), c0, fatal=True)
    E0 = L.edges(WB.read_live(T, fs_pairs=[]), {})
    r = g.replace_object(T, 529, L.BUF); nu = r["new_uid"]; s.fact("replace_object -> {0}".format(r))
    c1 = L.census(T); dd = dict((k, (c0.get(k), c1.get(k))) for k in set(c0) | set(c1) if c0.get(k) != c1.get(k))
    s.gate("G2a replace: no error, new uid", not r.get("err_replace") and not r.get("err") and nu > 0, r, fatal=True)
    s.gate("G2b callee census diff == exactly #529 -> buf stand-in", set(dd) <= {529, nu} and os.path.normcase(str(c1.get(nu))) == os.path.normcase(L.BUF), dd)
    E1 = L.edges(WB.read_live(T, fs_pairs=[]), {nu: 529})
    s.gate("G2c wire-edge diff after remap == empty ({0} edges)".format(len(E0)), E0 == E1, {"rem": sorted(E0 - E1), "add": sorted(E1 - E0)})
    s.save(); pa, pb = L.pane_dirs(L.GB), L.pane_dirs(T)
    s.gate("G3 pane per slot (label, direction) == source get-buff", pa == pb, (pa, pb))
    H1, l1 = harness(s, "gb", T); H2, l2 = harness(s, "cal", L.CAL)
    s.restart(); s.gate("G4 get-buff copy ES 1 COLD", g.exec_state(T) == 1)
    im = lambda o: next((v for n, v in o["out"].items() if "image number" in n), None)                # noqa: E731
    ms = lambda o: next((v for n, v in o["out"].items() if "issed" in n), None)                       # noqa: E731
    for i, b in enumerate((8217, 8218)):
        o = call(s, H1, l1, "gb", b)
        s.gate("T1 get-buff b={0} -> f{1:05d} pixels (md5 or transpose), image number == b, Missed TRUE".format(b, i),
               WANT[i] in (o["md5"], o["md5_T"]) and im(o) == b and ms(o) is True, (o["md5"], o["md5_T"], WANT[i], im(o), ms(o)))
    s.restart(); o = call(s, H1, l1, "gb", 5)
    s.gate("T2 fresh load get-buff b=5 -> f00000", WANT[0] in (o["md5"], o["md5_T"]), (o["md5"], WANT[0], im(o), ms(o)))
    s.restart()
    for i in range(3):
        o = call(s, H2, l2, "cal"); bo = next((v for n, v in o["out"].items() if n.startswith("Buffer Number Out")), None)
        s.gate("T3 cal call {0} -> f{0:05d}, Buffer Number Out {0}".format(i), WANT[i] in (o["md5"], o["md5_T"]) and bo == i, (o["md5"], WANT[i], bo))
    s.R["gbf"] = {"path": T, "md5": K.md5(T)}; s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self)
        return K.Stage.summary(self)


if __name__ == "__main__":
    st = St(L.GB, K.md5(L.GB), "replay_vis_76d_test", preload=False, deadline_min=40, work_dir=L.RP,
            work_name=os.path.basename(L.GBF), pins=tuple(K.DEFAULT_PINS[:1]) + PRE, task="76-5",
            out_json=os.path.join(K.BENCH, "replay_vis_76d_test.json"))
    sys.exit(K.run(body, st))
