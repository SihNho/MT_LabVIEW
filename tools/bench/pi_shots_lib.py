# ---
# labview: build
# hardware: none
# ---
r"""pi_shots_lib - the helpers card chat-PI1's two scripts share (build_op_getimage_v0.py, pi_shots_20261016.py).

Why not stagekit.Stage: a script that imports stagekit and calls save is classed as a STAGE by guard_bash
(stage_prerun.is_vi_modifying, card chat-N1) and needs a plan this op build does not have (logged fp-106); the
established form for op builds is gscript + bench_prep + protocol directly (tools/bench/diag_c100_verbs_build.py:29-30).
Contents: a gate/fact recorder that ends in the C6 RESULT line, the node sweep / terminal pickers of
tools/bench/diag_swap_build.py:20-37 (# shortcut: copied there in 2026-09 too; a shared home in gscript is OPEN for the
judgement session - gscript.py is outside this card's write globs), LabVIEW restart / kill-and-verify, and
get_image() = the Python wrapper of claudeDev\OpGetImage_v0.vi (labels in tools/bench/pi_shots_20261016/opgetimage_v0_labels.json).
Self-test: `py tools/bench/pi_shots_lib.py --selftest` (offline: rect parsing + crop box arithmetic).
"""
import hashlib, json, os, subprocess, sys, time                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTDIR = os.path.join(HERE, "pi_shots_20261016")
LABELS = os.path.join(OUTDIR, "opgetimage_v0_labels.json")
STD = ("reference", "reference out", "error in (no error)", "error out", "error in")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


class Rec(object):
    """gate/fact recorder; finish() prints the summary and the C6 RESULT line and returns the exit code."""
    def __init__(self, name):
        self.name, self.passes, self.fails, self.facts, self.R, self.t0 = name, [], [], [], {}, time.time()
        self.arts = []

    def head(self, t):
        print("\n---------- %s" % t, flush=True)

    def gate(self, label, ok, detail="", fatal=False):
        (self.passes if ok else self.fails).append(label)
        print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)
        if not ok and fatal:
            raise StopRun(label)
        return bool(ok)

    def fact(self, line):
        self.facts.append(str(line)); print("  FACT  %s" % str(line)[:1500], flush=True)  # noqa: E702

    def finish(self, out_json):
        import protocol as P
        self.R.update({"passes": self.passes, "fails": self.fails, "facts": self.facts,
                       "elapsed_s": round(time.time() - self.t0, 1)})
        json.dump(self.R, open(out_json, "w", encoding="utf-8"), indent=1, default=str)
        print("=== GATES: %d pass / %d fail%s" % (len(self.passes), len(self.fails),
                                                  ("; failing: " + ", ".join(self.fails)) if self.fails else ""), flush=True)
        arts = [{"path": a, "md5": md5(a)} for a in self.arts + [out_json] if os.path.exists(a)]
        print(P.result_line(P.make_result(len(self.passes), len(self.fails), self.fails[0] if self.fails else None, arts)),
              flush=True)
        return 0 if not self.fails else 1


class StopRun(Exception):
    pass


def g():
    import gscript
    return gscript


def restart():
    """Kill + start LabVIEW (bench_prep.restart_labview, ~50 s) and drop gscript's cached references."""
    import bench_prep
    bench_prep.restart_labview(); g().reset(); time.sleep(3.0)                      # noqa: E702
    return bench_prep.labview_handles()


def handles():
    import bench_prep
    return bench_prep.labview_handles()


def kill_and_verify():
    """Stop LabVIEW WITHOUT saving anything (process kill) and return True when no LabVIEW.exe is left."""
    try:
        g().reset()
    except Exception:                                                                # noqa: BLE001
        pass
    subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
                   capture_output=True)
    time.sleep(6)
    return "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout


def sweep(t, diagram_index=0, max_n=80):
    """{node uid: (Nodes[] index, terminal rows)} of one diagram (gscript.node_terms_uid per index)."""
    out = {}
    for n in range(max_n):
        uid, rows = g().node_terms_uid(t, diagram_index, n)
        if not uid:
            break
        out[int(uid)] = (n, rows)
    return out


def term(by, uid, name=None, src=None, pick=None):
    for r in by[uid][1]:
        if (name is None or r["name"] == name) and (src is None or r["is_source"] == src) and (pick is None or pick(r)):
            return r
    return None


def tl(by, uid):
    return [(r["i"], r["name"], "OUT" if r["is_source"] else "IN") for r in by[uid][1]]


def rect(position, bounds):
    """(left, top, right, bottom) from GObject.Position (left, top) and GObject.Bounds. Bounds is taken as
    (width, height) when it has 2 fields and as (left, top, right, bottom) when it has 4 - whichever LabVIEW returns."""
    p, b = [int(v) for v in position], [int(v) for v in bounds]
    if len(b) == 2:
        return (p[0], p[1], p[0] + b[0], p[1] + b[1])
    if len(b) == 4:
        return tuple(b)
    raise ValueError("unexpected Bounds %r" % (bounds,))


def crop_box(struct_rect, node_rects, pad=40, img_size=None):
    """Crop box in IMAGE pixels: the union of node_rects (diagram coordinates) + pad, shifted by the structure's
    top-left, clipped to the image."""
    l = min(r[0] for r in node_rects) - pad; t = min(r[1] for r in node_rects) - pad  # noqa: E702
    rr = max(r[2] for r in node_rects) + pad; b = max(r[3] for r in node_rects) + pad  # noqa: E702
    box = [l - struct_rect[0], t - struct_rect[1], rr - struct_rect[0], b - struct_rect[1]]
    if img_size:
        box = [max(0, box[0]), max(0, box[1]), min(img_size[0], box[2]), min(img_size[1], box[3])]
    return tuple(box)


def labels():
    return json.load(open(LABELS, encoding="utf-8"))


OP_PATH = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\OpGetImage_v0.vi"


def get_image(target, uid, png_path, depth=24, bg=0xFFFFFF, cls="Node", index=None):
    """Run OpGetImage_v0 (card chat-PI1c) on object #uid of `target` (must be LOADED): Traverse(`cls`)[index] ->
    TMSC(Node seed) -> Node.Get Image 6358C01 (Image Depth `depth`, Background Color `bg`) -> Write PNG File.vi to
    `png_path`; plus GObject Position/Bounds and a GObject.UID echo on the same Node reference.
    `index` defaults to gscript._uid_index(target, cls, uid) (report_all order = the op's Traverse order).
    Returns {echo, position, bounds, rect, err_png, err_pn, err_echo, index}; the CALLER checks echo == uid."""
    G = g(); L = labels(); c, ind = L["controls"], L["indicators"]                   # noqa: E702
    if index is None:
        index = G._uid_index(target, cls, uid)
    vi = G.op(OP_PATH)
    vi.SetControlValue("vi path", target)
    if "vi path 2" in L.get("all_controls", []):
        vi.SetControlValue("vi path 2", target)
    vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", int(index))  # noqa: E702
    if "index 2" in L.get("all_controls", []):
        vi.SetControlValue("index 2", 0)
    vi.SetControlValue(c["Image Depth"], int(depth)); vi.SetControlValue(c["BG Color"], int(bg))  # noqa: E702
    vi.SetControlValue(c["png_path"], png_path)
    G._run(vi)
    out = {"index": int(index), "echo": int(vi.GetControlValue(ind["UID"]) or 0),
           "position": tuple(vi.GetControlValue(ind["Position"])), "bounds": tuple(vi.GetControlValue(ind["Bounds"])),
           "err_png": G._err(vi, ind["png_err"]) or "", "err_pn": G._err(vi, ind["pn_err"]) or "",
           "err_echo": G._err(vi, ind["echo_err"]) or ""}
    try:
        out["rect"] = rect(out["position"], out["bounds"])
    except Exception as e:                                                           # noqa: BLE001
        out["rect"] = None; out["rect_err"] = str(e)                                 # noqa: E702
    return out


BD_OP_PATH = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\OpGetBDImage_v0.vi"
BD_LABELS = os.path.join(OUTDIR, "opgetbdimage_v0_labels.json")


def get_bd_image(target, png_path, depth=24):
    """Run OpGetBDImage_v0 (card chat-PI2) on `target`: Open VI Reference(vi path) -> VI.Block Diagram: Get Image
    Scaled 42C (Image Depth `depth`, Maximum Width/Height UNWIRED = the actual size) -> Write PNG File.vi to `png_path`.
    The donor's own Traverse branch (OpReport_v3) still runs and is ignored. Returns {err_png} ('' = no error)."""
    G = g(); L = json.load(open(BD_LABELS, encoding="utf-8")); c, ind = L["controls"], L["indicators"]  # noqa: E702
    vi = G.op(BD_OP_PATH)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(c["Image Depth"], int(depth))
    vi.SetControlValue(c["png_path"], png_path)
    G._run(vi)
    return {"err_png": G._err(vi, ind["png_err"]) or ""}


def png_stats(path):
    """{size, mode, blank, extrema} of a PNG; blank = every channel is a single value (an all-white / all-one-colour image)."""
    from PIL import Image
    im = Image.open(path); im.load()                                                 # noqa: E702
    ex = im.convert("RGB").getextrema()
    return {"size": list(im.size), "mode": im.mode, "blank": all(lo == hi for lo, hi in ex), "extrema": [list(e) for e in ex]}


# The typed-seed op builder (class B, retarget, uid_echo) is NOT copied here: build_op_getimage_v0.py imports it from
# tools/bench/diag_c100_verbs_build.py:67-166 (main-guarded at :560), per archive/peer/2026-10-16-priorart-op-getimage-v2.md B3.


def _selftest():
    assert rect((10, 20), (100, 50)) == (10, 20, 110, 70)
    assert rect((10, 20), (10, 20, 110, 70)) == (10, 20, 110, 70)
    assert crop_box((100, 100, 1000, 800), [(200, 300, 260, 340), (500, 150, 520, 170)], pad=40) == (60, 10, 460, 280)
    assert crop_box((100, 100, 1000, 800), [(110, 105, 120, 110)], pad=40, img_size=(900, 700)) == (0, 0, 60, 50)
    import tempfile
    from PIL import Image
    d = tempfile.mkdtemp(); p1, p2 = os.path.join(d, "w.png"), os.path.join(d, "c.png")  # noqa: E702
    Image.new("RGB", (30, 20), (255, 255, 255)).save(p1)
    im = Image.new("RGB", (30, 20), (255, 255, 255)); im.putpixel((3, 4), (0, 0, 0)); im.save(p2)  # noqa: E702
    a, b = png_stats(p1), png_stats(p2)
    assert a["blank"] and a["size"] == [30, 20] and a["mode"] == "RGB" and not b["blank"], (a, b)
    os.remove(p1); os.remove(p2); os.rmdir(d)                                       # noqa: E702
    print("selftest pi_shots_lib 5/0")


if __name__ == "__main__" and "--selftest" in sys.argv:
    _selftest()
