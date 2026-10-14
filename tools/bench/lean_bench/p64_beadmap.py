# ---
# labview: none
# hardware: camera
# offline-args: --dry
# ---
r"""p64_beadmap - the bead-map picker of HOLD-4 = 2 (plan section 3 item 4; P6-4 preparation P-3). One camera snapshot (LabVIEW
closed) -> bead centres found in the image -> 15 picks as fractions of the 1280 x 1024 frame -> json + PNG for the user's check.
Every leg of a rate cell clicks the SAME 15 fractions (p64_leg.py --fracs-json -> drive_m8.FRACS_ALL[:15] -> v5.PICK_FRACS).
Reference beads stick poorly (user_notes.md:6): N (beads found) may be < 15 and loose beads may drift. Default (ASSUME, in
questions_for_user.md): fill up to 15 picks with the earlier ABBA's fixed fractions (drive_m8.FRACS_ALL, in order) that lie in
an empty field (>= SEP px from every candidate spot and every other pick), so the tracking load stays 15; N is reported.
With a second snapshot (--img2, a few seconds later), a bead that moved > DRIFT px or vanished is flagged drifting and NOT picked.
Finder (numpy only; a tethered bead in this bright field = a dark core inside a bright ring, preview of G:\m8_replay_frames):
  d = box-mean(r 24) - box-mean(r CORE) (dark disk > 0); spots = local maxima of d above THR robust sigmas, >= MERGE px apart,
  centre = centroid of the dark disk (r 8);
  per spot: core contrast, ring contrast (max of the radial profile at r 8..22 - background), roundness (elongation of the
  dark area, 1.0 = round; a fused doublet is elongated),
  nearest other spot, distance to the frame edge. bead = contrast >= THR, ring >= RING, roundness <= ROUND, nearest >= ISO
  (no doublets), inside the MARGIN. These numbers are the features option J would send to Jev as text.
    py tools/bench/lean_bench/p64_beadmap.py find --img <tif|png> [--img2 <second>] --out <json> [--png <preview>]
    py tools/bench/lean_bench/p64_beadmap.py snap --out <tif>     (RIG DAY ONLY: one IMAQdx frame; refuses while LabVIEW runs)
    py tools/bench/lean_bench/p64_beadmap.py --dry                (synthetic frames + one recorded real frame; no camera)"""
import hashlib, json, os, sys, tempfile, time                                             # noqa: E401
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, HERE); sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                      # noqa: E402
NPICK, THR, RING, ROUND, ISO, MARGIN, SEP, DRIFT = 15, 8.0, 6.0, 0.6, 40.0, 0.05, 40.0, 3.0
CORE, MERGE = 5, 20          # revised ~12:30 after the first real-frame run (report 3.5): a real bead = flat dark disk r ~8 + bright ring r ~11-13
ROUND = 1.2                  # revised ~12:31: roundness = elongation of the dark area (sqrt of the 2nd-moment eigenvalue ratio), not ring
                             # sectors; on f00000.tif single beads 1.00-1.13, fused doublets / triplets 1.27-1.48 (report 3.5)
# shortcut: SEP = 40 px is a guess at the VI's pick box (not read from the VI); upgrade when the ROI size is read from the panel.
REAL_FRAME = r"G:\m8_replay_frames\f00000.tif"


def fixed_fracs():
    """drive_m8's fixed fractions (FRACS6 + the filtered 5 x 4 grid), the earlier ABBA's picks first."""
    import drive_m8
    return [tuple(f) for f in drive_m8.FRACS_ALL]


def box(a, r):
    """Mean over a (2r+1)^2 box, edges by reflection (integral image)."""
    p = np.pad(a, r + 1, mode="reflect").astype(np.float64)
    s = p.cumsum(0).cumsum(1)
    k = 2 * r + 1
    out = s[k:, k:] - s[:-k, k:] - s[k:, :-k] + s[:-k, :-k]
    return (out / (k * k))[:a.shape[0], :a.shape[1]]


def local_max(a, r):
    """a == the max of its (2r+1)^2 neighbourhood (separable sliding max)."""
    w = np.lib.stride_tricks.sliding_window_view
    p = np.pad(a, r, mode="constant", constant_values=-np.inf)
    m = w(w(p, 2 * r + 1, axis=1).max(-1), 2 * r + 1, axis=0).max(-1)
    return a >= m


def radial(f, y, x, rmax=26):
    """Radial profile (mean per integer radius 0..rmax) and the 8-sector means at the ring radius window."""
    h, w_ = f.shape
    y0, y1, x0, x1 = max(0, y - rmax), min(h, y + rmax + 1), max(0, x - rmax), min(w_, x + rmax + 1)
    yy, xx = np.mgrid[y0:y1, x0:x1]
    rr = np.hypot(yy - y, xx - x)
    ri = rr.astype(int)
    sub = f[y0:y1, x0:x1]
    prof = np.array([sub[ri == k].mean() if np.any(ri == k) else np.nan for k in range(rmax + 1)])
    return prof, sub, rr, np.arctan2(yy - y, xx - x)


def find(img, img2=None):
    """Spots and beads of one frame (+ drift vs a second frame). Returns {shape, sigma, spots, beads, rejected}."""
    f = np.asarray(img, dtype=np.float64)
    bg = box(f, 24)
    d = bg - box(f, CORE)
    med = np.median(d)
    sig = 1.4826 * np.median(np.abs(d - med)) or 1.0
    z = (d - med) / sig
    ys, xs = np.nonzero(local_max(z, 10) & (z >= THR))
    order = np.argsort(-z[ys, xs])
    spots = []
    h, w_ = f.shape
    for i in order:
        y, x = int(ys[i]), int(xs[i])
        if all((y - s["y"]) ** 2 + (x - s["x"]) ** 2 >= MERGE ** 2 for s in spots):
            y0, y1, x0, x1 = max(0, y - 8), min(h, y + 9), max(0, x - 8), min(w_, x + 9)   # centre = centroid of the dark disk
            wgt = np.clip(bg[y0:y1, x0:x1] - f[y0:y1, x0:x1], 0, None)
            yy, xx = np.mgrid[y0:y1, x0:x1]
            cy, cx = (int(round((wgt * yy).sum() / wgt.sum())), int(round((wgt * xx).sum() / wgt.sum()))) if wgt.sum() > 0 else (y, x)
            spots.append({"y": cy, "x": cx, "contrast": round(float(z[y, x]), 2)})
    for s in spots:
        prof, sub, rr, th = radial(f, s["y"], s["x"])
        b0 = bg[s["y"], s["x"]]
        k = 8 + int(np.nanargmax(prof[8:23]))
        s["ring_r"] = k
        s["ring"] = round(float(prof[k] - b0), 2)                                         # grey levels above the local background
        y0, y1, x0, x1 = max(0, s["y"] - 16), min(h, s["y"] + 17), max(0, s["x"] - 16), min(w_, s["x"] + 17)   # dark-area shape
        wgt = np.clip(bg[y0:y1, x0:x1] - f[y0:y1, x0:x1] - 15.0, 0, None)
        yy, xx = np.mgrid[y0:y1, x0:x1]
        if wgt.sum() > 0:
            my, mx = (wgt * yy).sum() / wgt.sum(), (wgt * xx).sum() / wgt.sum()
            cov = np.cov(np.vstack([(yy - my).ravel(), (xx - mx).ravel()]), aweights=wgt.ravel() + 1e-12)
            ev = np.linalg.eigvalsh(cov)
            s["roundness"] = round(float(np.sqrt(ev[1] / max(ev[0], 1e-9))), 3)          # 1.0 = round dark disk; a doublet ~1.5-2
        else:
            s["roundness"] = None
        others = [np.hypot(s["y"] - o["y"], s["x"] - o["x"]) for o in spots if o is not s]
        s["nearest"] = round(float(min(others)), 1) if others else None
        s["fx"], s["fy"] = round(s["x"] / float(w_), 4), round(s["y"] / float(h), 4)
        why = []
        if s["ring"] < RING:
            why.append("ring")
        if s["roundness"] is None or s["roundness"] > ROUND:
            why.append("round")
        if s["nearest"] is not None and s["nearest"] < ISO:
            why.append("doublet")
        if not (MARGIN <= s["fx"] <= 1 - MARGIN and MARGIN <= s["fy"] <= 1 - MARGIN):
            why.append("edge")
        s["bead"], s["reject"] = not why, why
    beads = [s for s in spots if s["bead"]]
    if img2 is not None:
        sp2 = find(img2)["spots"]
        for b in beads:
            dd = [np.hypot(b["y"] - o["y"], b["x"] - o["x"]) for o in sp2]
            b["drift_px"] = round(float(min(dd)), 2) if dd else None
            b["drifting"] = b["drift_px"] is None or b["drift_px"] > DRIFT
    rej = {}
    for s in spots:
        for r in s["reject"]:
            rej[r] = rej.get(r, 0) + 1
    return {"shape": [h, w_], "sigma": round(float(sig), 3), "spots": spots, "beads": beads, "rejected": rej}


def picks(found, fixed):
    """15 picks: the stable beads (most contrast first, at most 15), then fixed fractions in an empty field. Returns (picks, kinds, n)."""
    h, w_ = found["shape"]
    stable = [b for b in found["beads"] if not b.get("drifting")]
    stable.sort(key=lambda b: -b["contrast"])
    P_, K = [(b["fx"], b["fy"]) for b in stable[:NPICK]], ["bead"] * min(NPICK, len(stable))
    taken = [(b["x"], b["y"]) for b in found["spots"]] + [(fx * w_, fy * h) for fx, fy in P_]
    for fx, fy in list(fixed) + [(0.1 + 0.8 * i / 9.0, 0.1 + 0.8 * j / 9.0) for j in range(10) for i in range(10)]:
        if len(P_) >= NPICK:
            break
        if all(np.hypot(fx * w_ - x, fy * h - y) >= SEP for x, y in taken):
            P_.append((round(fx, 4), round(fy, 4))); K.append("fill"); taken.append((fx * w_, fy * h))   # noqa: E702
    return P_, K, len(stable)


def preview(img, found, P_, K, png):
    """RGB preview at half scale: green circle = picked bead, yellow = bead not picked / drifting, blue = rejected spot, red cross = fill."""
    a = np.asarray(img, dtype=np.uint8)
    rgb = np.stack([a] * 3, -1).copy()
    h, w_ = a.shape

    def circ(x, y, r, col):
        t = np.linspace(0, 2 * np.pi, 120)
        for rr in (r, r + 1):
            xs, ys = (x + rr * np.cos(t)).astype(int), (y + rr * np.sin(t)).astype(int)
            ok = (xs >= 0) & (xs < w_) & (ys >= 0) & (ys < h)
            rgb[ys[ok], xs[ok]] = col
    picked = set((round(fx, 4), round(fy, 4)) for (fx, fy), k in zip(P_, K) if k == "bead")
    for s in found["spots"]:
        col = (0, 255, 0) if (s["fx"], s["fy"]) in picked else (255, 255, 0) if s["bead"] else (0, 128, 255)
        circ(s["x"], s["y"], 22, col)
    for (fx, fy), k in zip(P_, K):
        if k == "fill":
            x, y = int(fx * w_), int(fy * h)
            rgb[max(0, y - 12):y + 13, max(0, x - 1):x + 2] = (255, 0, 0)
            rgb[max(0, y - 1):y + 2, max(0, x - 12):x + 13] = (255, 0, 0)
    Image.fromarray(rgb).resize((w_ // 2, h // 2)).save(png)


def run_find(img_path, img2_path=None, out=None, png=None):
    img = np.asarray(Image.open(img_path))
    img2 = np.asarray(Image.open(img2_path)) if img2_path else None
    fd = find(img, img2)
    P_, K, n = picks(fd, fixed_fracs())
    r = {"schema": "p64-beadmap/1", "img": img_path, "img_md5": hashlib.md5(open(img_path, "rb").read()).hexdigest(), "img2": img2_path,
         "shape": fd["shape"], "N_spots": len(fd["spots"]), "N_found": len(fd["beads"]), "N": n,
         "N_drifting": sum(1 for b in fd["beads"] if b.get("drifting")), "picks_frac": P_, "pick_kind": K,
         "n_fill": K.count("fill"), "rejected": fd["rejected"], "beads": fd["beads"],
         "params": {"THR": THR, "RING": RING, "ROUND": ROUND, "ISO": ISO, "MARGIN": MARGIN, "SEP": SEP, "DRIFT": DRIFT}, "png": png}
    if png:
        preview(img, fd, P_, K, png)
    if out:
        json.dump(r, open(out, "w", encoding="utf-8"), indent=1)
    return r


def snap(out):
    """RIG DAY ONLY (not run in P-3): one frame from the first IMAQdx camera, LabVIEW closed (the camera is single-owner).
    Mirrors tools/bench/camera_copy_cost.py:56-117 (enumerate, open, configure 1 x 10 buffers, start, get Last, stop, close)."""
    import drive_legguard as LG
    if LG.lv_running():
        raise SystemExit("REFUSED: LabVIEW is running (it owns the camera) - close it first")
    import ctypes as C, imaqdx_limits as L                                                # noqa: E401
    n = C.c_uint32(0); L.dx.IMAQdxEnumerateCameras(None, C.byref(n), C.c_uint32(1))       # noqa: E702
    if not n.value:
        raise SystemExit("no camera")
    arr = (L.CameraInformation * n.value)(); L.dx.IMAQdxEnumerateCameras(arr, C.byref(n), C.c_uint32(1))   # noqa: E702
    sess = C.c_uint32(0)
    if L.dx.IMAQdxOpenCamera(arr[0].InterfaceName, C.c_uint32(0), C.byref(sess)):
        raise SystemExit("open failed")
    try:
        w, h = L.get(sess, L.A + "ImageFormatControl::Width"), L.get(sess, L.A + "ImageFormatControl::Height")
        size = L.get(sess, L.A + "TransportLayerControl::PayloadSize")
        buf, act = C.create_string_buffer(size), C.c_uint32(0)
        assert not L.dx.IMAQdxConfigureAcquisition(sess, C.c_uint32(1), C.c_uint32(10)), "ConfigureAcquisition failed"
        try:
            assert not L.dx.IMAQdxStartAcquisition(sess), "StartAcquisition failed"
            time.sleep(0.5)
            assert not L.dx.IMAQdxGetImageData(sess, buf, C.c_uint32(size), C.c_uint32(1), C.c_uint32(0), C.byref(act)), "GetImageData failed"
        finally:
            L.dx.IMAQdxStopAcquisition(sess); L.dx.IMAQdxUnconfigureAcquisition(sess)     # noqa: E702
        Image.fromarray(np.frombuffer(buf.raw[:w * h], dtype=np.uint8).reshape(h, w)).save(out)
        return {"out": out, "w": w, "h": h, "buffer": act.value}
    finally:
        L.dx.IMAQdxCloseCamera(sess)


def synth(beads, seed=1, shape=(1024, 1280)):
    """A flat field + noise with tethered-bead-like spots (dark core r 4, bright ring r 12) at the given (x, y)."""
    g = np.random.default_rng(seed)
    f = 108 + 4 * g.standard_normal(shape)
    yy, xx = np.mgrid[0:shape[0], 0:shape[1]]
    for x, y in beads:
        r = np.hypot(yy - y, xx - x)
        f += -45 * np.exp(-(r / 4.0) ** 2) + 30 * np.exp(-((r - 12) / 2.0) ** 2)
    return np.clip(f, 0, 255).astype(np.uint8)


# self-check: one synthetic bead is found within 2 px
_s = find(synth([(400, 300)]))
assert len(_s["beads"]) == 1 and abs(_s["beads"][0]["x"] - 400) <= 2 and abs(_s["beads"][0]["y"] - 300) <= 2


def dry():
    G, R = {}, {}
    fixed = fixed_fracs()
    six = [(200, 200), (500, 260), (900, 230), (330, 640), (760, 700), (1080, 820)]
    tmp = tempfile.mkdtemp(prefix="p64bead_")
    paths = {}
    for tag, b, seed in (("six", six, 1), ("six_moved", six[:5] + [(1088, 820)], 2), ("empty", [], 3)):
        paths[tag] = os.path.join(tmp, tag + ".png"); Image.fromarray(synth(b, seed)).save(paths[tag])   # noqa: E702
    r6 = run_find(paths["six"])
    R["six"] = {k: r6[k] for k in ("N_spots", "N_found", "N", "n_fill", "pick_kind")}
    found = sorted((b["x"], b["y"]) for b in r6["beads"])
    G["B six beads: N 6, centres within 2 px, 6 bead + 9 fill picks"] = (r6["N"] == 6 and len(found) == 6 and
                                                                        all(abs(x - X) <= 2 and abs(y - Y) <= 2 for (x, y), (X, Y) in zip(found, sorted(six)))
                                                                        and r6["pick_kind"].count("fill") == 9 and len(r6["picks_frac"]) == 15)
    pts = [(fx * 1280, fy * 1024) for fx, fy in r6["picks_frac"]]
    G["B picks >= SEP apart and fill >= SEP from every spot"] = all(np.hypot(a[0] - b[0], a[1] - b[1]) >= SEP for i, a in enumerate(pts) for b in pts[i + 1:])
    rd = run_find(paths["six"], paths["six_moved"])
    R["drift"] = {k: rd[k] for k in ("N_found", "N_drifting", "N", "n_fill")}
    G["B one bead moved 8 px: flagged drifting, N 5, fill 10"] = rd["N_drifting"] == 1 and rd["N"] == 5 and rd["n_fill"] == 10
    re_ = run_find(paths["empty"])
    R["empty"] = {k: re_[k] for k in ("N_spots", "N", "n_fill")}
    G["B empty frame: N 0, picks == drive_m8's 15 fixed fractions"] = re_["N"] == 0 and [tuple(p) for p in re_["picks_frac"]] == [(round(a, 4), round(b, 4)) for a, b in fixed[:15]]
    png = os.path.join(tempfile.gettempdir(), "p64_beadmap_dry_real.png")
    rr = run_find(REAL_FRAME, out=os.path.join(tempfile.gettempdir(), "p64_beadmap_dry_real.json"), png=png)
    R["real"] = {k: rr[k] for k in ("N_spots", "N_found", "N", "n_fill", "rejected", "png")}
    G["B recorded real frame: >= 15 beads, 15 bead picks, 0 fill"] = rr["N"] >= 15 and rr["n_fill"] == 0
    f = np.asarray(Image.open(REAL_FRAME)).astype(np.float64)                             # N < 15 on real pixels: keep 8 single beads,
    keep = set((b["x"], b["y"]) for b in sorted(rr["beads"], key=lambda b: -b["contrast"])[:8])   # every other spot blended into the
    yy, xx = np.mgrid[0:f.shape[0], 0:f.shape[1]]
    w = np.ones(f.shape)
    for b in [s for s in find(np.asarray(Image.open(REAL_FRAME)))["spots"] if (s["x"], s["y"]) not in keep]:
        w = np.minimum(w, np.clip((np.hypot(yy - b["y"], xx - b["x"]) - 22) / 12.0, 0, 1))
    sparse = (w * f + (1 - w) * box(f, 40)).clip(0, 255).astype(np.uint8)                # local background (soft edge r 22..34)
    paths["sparse"] = os.path.join(tmp, "sparse.png"); Image.fromarray(sparse).save(paths["sparse"])   # noqa: E702
    rs = run_find(paths["sparse"], png=os.path.join(tempfile.gettempdir(), "p64_beadmap_dry_sparse.png"))
    R["real_sparse8"] = {k: rs[k] for k in ("N_spots", "N", "n_fill", "pick_kind", "png")}
    G["B real frame with 8 beads left: N 8, 8 bead + 7 fill picks, all >= SEP apart"] = (
        rs["N"] == 8 and rs["n_fill"] == 7 and len(rs["picks_frac"]) == 15 and
        all(np.hypot((a[0] - b[0]) * 1280, (a[1] - b[1]) * 1024) >= SEP for i, a in enumerate(rs["picks_frac"]) for b in rs["picks_frac"][i + 1:]))
    for f_ in paths.values():
        os.remove(f_)
    os.rmdir(tmp)
    return G, R


if __name__ == "__main__":
    av = sys.argv[1:]
    arg = lambda k, d=None: av[av.index(k) + 1] if k in av else d                        # noqa: E731
    if "--dry" in av:
        G, R = dry()
        print("DRY %s" % json.dumps(R, default=str), flush=True)
    elif av and av[0] == "snap":
        print(json.dumps(snap(arg("--out"))), flush=True); G = {"S snapshot saved": True}   # noqa: E702
    else:
        r = run_find(arg("--img"), arg("--img2"), arg("--out"), arg("--png"))
        print(json.dumps({k: v for k, v in r.items() if k != "beads"}, default=str), flush=True)
        G = {"F 15 picks": len(r["picks_frac"]) == NPICK}
    for k, v in G.items():
        print("GATE %-70s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    bad = [k for k, v in G.items() if not v]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None)), flush=True)
    sys.exit(1 if bad else 0)
