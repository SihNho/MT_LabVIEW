# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/brief_chat-PI2.md
# ---
r"""pi_shots_ops.py - card chat-PI2: whole block-diagram PNGs (24-bit, native size) of the seven Op VIs for the PI deck.

EXISTING FIRST: image = pi_shots_lib.get_bd_image (claudeDev\OpGetBDImage_v0.vi, built by
tools/recipes/build_op_getbdimage_v0.py, VI.Block Diagram: Get Image Scaled 42C); blank check = pi_shots_lib.png_stats;
node classes = gscript.report_all(copy, 'Node'); subVI names = gscript.subvis(copy, i) per Traverse('Diagram') index i
(the walk of tools/bench/pi_shots_20261019.py:195-203); Rec / md5 / restart / kill_and_verify = pi_shots_lib.
Byte copies go to claudeDev\shots_20261016\ops\shot_<name>.vi: the `shot_` prefix keeps the VI NAME different from the
originals, which gscript itself may hold in memory (OpReport_v3 = gscript.OP_REPORT, gscript.py:80) - two VIs of one
name cannot be in memory at once. The copies are loaded with gscript.ensure_loaded (as in pi_shots_20261019.py), never
edited or saved; LabVIEW is KILLED at the end (nothing saved) and the copies deleted.
Retry rule (card chat-PI2 / lesson chat-PI1f): an op that errors or gives a blank PNG is retried ONCE in a fresh
LabVIEW, then the script reports.

PREDICTION (gates): S0 every source md5 == the card pin; S1 every copy md5 == pin; E per Op: op error ''; I per Op: PNG
exists, mode RGB (24-bit), not blank, both sides > 0; X sources md5 after == before; H handles at end vs after the first
restart recorded (gate: end <= start + 1000, i.e. back near the baseline with only small VIs loaded); G LabVIEW gone;
K copies deleted. Output: tools/bench/pi_shots_20261016/op_<name>.png + ops.json.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/pi_shots_ops.log -- py -u tools/bench/pi_shots_ops.py
"""
import collections, json, os, shutil, sys                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))                 # noqa: E702
import pi_shots_lib as L                                                             # noqa: E402
import gscript as g                                                                  # noqa: E402
CD = g.CLAUDEDEV
OPSDIR = os.path.join(CD, "shots_20261016", "ops")
OPS = [("OpReport_v3", "0743701a249b6ac20a5dab9ee676c09c"), ("OpWireSource_v5", "5dc45a04ea5d809f5ca57e9309ed59c5"),
       ("OpMoveIn_v0", "b9107c75c76cf2828bef9915660b2716"), ("OpConnectNested_v1", "b7a1bb56cefe2b4632125e6bda0d7221"),
       ("OpCreateLocalRead_v0", "f695d97a36ae127cd2dd3ca6b1fc1089"), ("OpForLoopParSet_v0", "868e1f42004a1c3c5a9997c3c822899d"),
       ("OpGetImage_v0", "b7c5667bf86ed58b4751d8c10a45da48")]
s = L.Rec("pi_shots_ops")
OUT = {}


def src(n):
    return os.path.join(CD, n + ".vi")


def copy_of(n):
    return os.path.join(OPSDIR, "shot_%s.vi" % n)


def shot(n, pin, attempt):
    c = copy_of(n)
    if not os.path.exists(c):
        shutil.copyfile(src(n), c)
    s.gate("S1 %s copy md5 == pin (attempt %d)" % (n, attempt), L.md5(c) == pin, L.md5(c)[:8])
    g.ensure_loaded(c)
    png = os.path.join(L.OUTDIR, "op_%s.png" % n)
    if os.path.exists(png):
        os.remove(png)
    r = L.get_bd_image(c, png)
    st = L.png_stats(png) if os.path.exists(png) else None
    ok = not r["err_png"] and st is not None and st["mode"] == "RGB" and not st["blank"] and min(st["size"]) > 0
    s.fact("%s attempt %d: err '%s' png %s" % (n, attempt, r["err_png"][:200], st))
    rec = {"file": src(n), "copy": c, "source_md5": pin, "png": png, "attempt": attempt, "err": r["err_png"], "png_stats": st}
    if ok:
        rec["png_md5"] = L.md5(png)
        try:
            cls = collections.Counter(str(o["class"]) for o in g.report_all(c, "Node"))
            rec["node_classes"] = dict(sorted(cls.items()))
        except Exception as e:                                                       # noqa: BLE001
            rec["node_classes_err"] = str(e)[:200]
        try:
            names = []
            for i, _d in enumerate(g.report_all(c, "Diagram")):
                rows, _err = g.subvis(c, i, strict=False)
                names += [r2["name"] for r2 in (rows or [])]
            rec["subvis"] = sorted(set(names))
        except Exception as e:                                                       # noqa: BLE001
            rec["subvis_err"] = str(e)[:200]
        s.fact("%s nodes %s subVIs %s" % (n, rec.get("node_classes"), rec.get("subvis")))
    OUT[n] = rec
    return ok


def main():
    os.makedirs(OPSDIR, exist_ok=True)
    before = dict((n, L.md5(src(n))) for n, _p in OPS)
    s.gate("S0 sources md5 == pins", all(before[n] == p for n, p in OPS), before, fatal=True)
    s.head("[0] restart LabVIEW"); h0 = L.restart(); s.fact("handles after restart %s" % h0)  # noqa: E702
    s.R["handles_start"] = h0
    bad = []
    for n, pin in OPS:
        s.head("[1] %s" % n)
        try:
            ok = shot(n, pin, 1)
        except Exception as e:                                                       # noqa: BLE001
            s.fact("%s attempt 1 raised %s" % (n, str(e)[:300])); ok = False        # noqa: E702
        if not ok:
            bad.append((n, pin))
    h1 = L.handles(); s.R["handles_after_pass1"] = h1                                # noqa: E702
    if bad:
        s.head("[2] retry %s in a fresh LabVIEW" % [n for n, _p in bad])
        s.fact("handles after restart %s" % L.restart())
        for n, pin in bad:
            try:
                shot(n, pin, 2)
            except Exception as e:                                                   # noqa: BLE001
                s.fact("%s attempt 2 raised %s" % (n, str(e)[:300]))
    for n, _p in OPS:
        r = OUT.get(n, {})
        st = r.get("png_stats")
        s.gate("E %s op error ''" % n, bool(r) and not r.get("err"), r.get("err", "no record")[:200])
        s.gate("I %s PNG RGB, not blank, size %s" % (n, st and st["size"]),
               bool(st) and st["mode"] == "RGB" and not st["blank"] and min(st["size"]) > 0, st)
    h2 = L.handles(); s.R["handles_end"] = h2                                        # noqa: E702
    s.fact("H handles start %s / after pass 1 %s / end %s; refs %s" % (h0, h1, h2, g.ref_counts()))
    s.gate("H handles at end <= start + 1000 (%s -> %s)" % (h0, h2), h2 is not None and h0 is not None and h2 <= h0 + 1000)
    json.dump(OUT, open(os.path.join(L.OUTDIR, "ops.json"), "w", encoding="utf-8"), indent=1, default=list)
    s.arts.append(os.path.join(L.OUTDIR, "ops.json"))
    s.arts += [r["png"] for r in OUT.values() if os.path.exists(r["png"])]


try:
    main()
except L.StopRun as e:
    s.fact("STOPPED at gate: %s" % e)
except Exception as e:                                                               # noqa: BLE001
    import traceback; traceback.print_exc(); s.gate("the run completed without an unhandled exception", False, str(e)[:200])  # noqa: E702
s.gate("G LabVIEW gone at exit (killed, nothing saved)", L.kill_and_verify())
after = dict((n, L.md5(src(n))) for n, _p in OPS)
s.gate("X sources md5 after == pins", all(after[n] == p for n, p in OPS), after)
shutil.rmtree(OPSDIR, ignore_errors=True)
s.gate("K copies deleted (%s)" % OPSDIR, not os.path.exists(OPSDIR))
sys.exit(s.finish(os.path.join(L.OUTDIR, "pi_shots_ops.json")))
