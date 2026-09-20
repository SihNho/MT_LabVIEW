"""ref_cupy.py - CuPy (CUDA) port of ref_numpy.track_bead, batched over beads: every step is the VI's step, executed as
array operations on the GPU (cuFFT for the FFTs).  Float64 throughout except where the VI is single precision (the
cross-arm averages and the radial profile output).  Verified against ref_numpy (which is verified against the LabVIEW
kernel on the fixture) by tools/gpu/check_cupy.py.

Batch layout: B beads of one frame (or B = beads x frames): sub-images (B, 2h, 2h), starting x/y (B,) int, per-bead
calibration arrays padded to a common width (forget radius can differ per bead -> arrays are padded with zeros and a
per-bead length mask is applied).
"""
import numpy as np

try:
    import cupy as cp
except Exception as e:                       # pragma: no cover
    cp = None
    _import_error = e

from ref_numpy import Params, DEFAULT, QUAD_WEIGHTS, lv_round, lv_i32_div  # noqa: E402


def _xp():
    if cp is None:
        raise RuntimeError(f"CuPy not available: {_import_error}")
    return cp


# ------------------------------------------------------------------------------------------------ XY (batched) --
def average_xy_in_cross_b(sub, h, cross, arm):
    """sub: (B, 2h, 2h) float64 on GPU. Returns along-x, along-y profiles (B, cross), single-precision means."""
    xp = _xp(); half = lv_i32_div(cross, 2); arm2 = lv_i32_div(arm, 2)
    a = sub[:, h - arm2:h - arm2 + arm, h - half:h - half + cross]            # rows = arm, cols = cross -> mean over rows
    b = sub[:, h - half:h - half + cross, h - arm2:h - arm2 + arm]            # rows = cross, cols = arm -> mean over cols
    ax = (a.astype(xp.float32).sum(axis=1, dtype=xp.float32) / xp.float32(arm)).astype(xp.float64)
    ay = (b.astype(xp.float32).sum(axis=2, dtype=xp.float32) / xp.float32(arm)).astype(xp.float64)
    return ax, ay


def prep_avg_profile_b(prof, cross, n_end, window):
    xp = _xp()
    first = prof[:, :n_end].sum(axis=1)
    idx = cross - xp.arange(n_end)                                            # the VI's `cross - i`; i = 0 -> out of range -> 0
    valid = idx < cross
    last = (prof[:, xp.where(valid, idx, 0)] * valid[None, :]).sum(axis=1)
    base = (first + last) / (2 * n_end)
    return (prof - base[:, None]) * window[None, :]


def fit_parabola_b(corr, n_pts):
    """corr: (B, cross). Parabola through n_pts samples centred on each row's argmax -> vertex abscissa (B,)."""
    xp = _xp(); B, n = corr.shape
    k = xp.argmax(corr, axis=1)
    lo = k - int(np.floor(n_pts / 2))
    cols = lo[:, None] + xp.arange(n_pts)[None, :]
    ys = xp.take_along_axis(corr, cols, axis=1)                               # (B, n_pts)
    xs = cols.astype(xp.float64)
    # least squares y = a2 x^2 + a1 x + a0 per row (normal equations, 3x3)
    X = xp.stack([xs ** 2, xs, xp.ones_like(xs)], axis=2)                    # (B, n_pts, 3)
    XtX = xp.einsum("bni,bnj->bij", X, X); Xty = xp.einsum("bni,bn->bi", X, ys)
    c = xp.linalg.solve(XtX, Xty[..., None])[..., 0]                           # (B, 3): a2, a1, a0
    return -(c[:, 1] / c[:, 0]) / 2


def find_avg_profile_center_b(prof, window_h, start, half, n_pts=5):
    """prof (B, cross) prepped profiles; start (B,) int; returns new centre (B,), shift (B,)."""
    xp = _xp(); cross = 2 * half
    F = xp.fft.fft(prof, axis=1) * window_h[None, :]
    F2 = F * F
    k = 2 * np.pi / cross
    i = xp.arange(cross); a = xp.where(i > half, i - cross, i).astype(xp.float64)

    def corr(S):
        return xp.roll(xp.abs(xp.fft.ifft(S, axis=1)), half, axis=1)

    def shift(S, d):
        return xp.abs(S) * xp.exp(1j * (xp.angle(S) + k * d[:, None] * a[None, :]))

    P1 = fit_parabola_b(corr(F2), n_pts)
    r1 = xp.rint(P1); d1 = P1 - r1
    G1 = shift(F2, d1)
    P2 = fit_parabola_b(corr(G1), n_pts); out1 = P2 - r1
    G2 = shift(G1, out1)
    P3 = fit_parabola_b(corr(G2), n_pts); out2 = P3 - r1
    sh = (P1 + out1 + out2 - half) / 2
    return start.astype(xp.float64) + sh, sh


# ------------------------------------------------------------------------------------------------- Z (batched) --
def radial_profile_b(sub, xc, yc, half):
    """sub (B, S, S); xc, yc (B,) sub-image coordinates. Returns (B, half) single-precision-rounded profiles.
    Same pixel set and weights as the VI (row loop over the chord, bilinear radius binning)."""
    xp = _xp(); cross = 2 * half; B = sub.shape[0]
    x0 = (xp.ceil(xc) - half).astype(int); y0 = (xp.ceil(yc) - half).astype(int)
    cx = half + (xc - xp.ceil(xc)); cy = half + (yc - xp.ceil(yc))
    i = xp.arange(cross)[None, :, None]; j = xp.arange(cross)[None, None, :]
    dy = cy[:, None, None] - i; c = xp.sqrt(half * half - dy * dy)
    N = xp.ceil(2 * c); j0 = xp.ceil(cx[:, None, None] - c)
    inside = (j >= j0) & (j < j0 + N)                                          # the VI's chord range per row
    rows = (y0[:, None, None] + i); cols = (x0[:, None, None] + j)
    win = sub[xp.arange(B)[:, None, None], rows, cols]                         # (B, cross, cross)
    r = xp.sqrt((cx[:, None, None] - j) ** 2 + dy * dy)
    rf = xp.floor(r); fr = r - rf; rfi = rf.astype(int)
    w1 = xp.where(inside & (rfi < half), 1 - fr, 0.0); w2 = xp.where(inside & (rfi + 1 < half), fr, 0.0)
    idx1 = xp.clip(rfi, 0, half); idx2 = xp.clip(rfi + 1, 0, half)
    s = xp.zeros((B, half + 1)); w = xp.zeros((B, half + 1))
    bi = xp.broadcast_to(xp.arange(B)[:, None, None], r.shape)
    xp.add.at(s, (bi, idx1), w1 * win); xp.add.at(w, (bi, idx1), w1)
    xp.add.at(s, (bi, idx2), w2 * win); xp.add.at(w, (bi, idx2), w2)
    out = s[:, :half] / w[:, :half]
    return out.astype(xp.float32).astype(xp.float64)


def prep_i_of_r_b(rad, half, forget, cosband):
    """rad (B, half); forget (B,) int; cosband (B, >=2*half-1). Returns corkscrew (B, half) padded: element r for
    r >= forget (r < forget is masked to 0) so that per-bead lengths differ only by a mask."""
    xp = _xp(); B = rad.shape[0]; n = 2 * half - 1
    mir = xp.concatenate([rad[:, 1:][:, ::-1], rad], axis=1).astype(xp.complex128)
    out = xp.fft.ifft(xp.fft.fft(mir, axis=1) * cosband[:, :n], axis=1)
    cork_full = out[:, half - 1:]                                              # r = 0 .. half-1
    r = xp.arange(half)[None, :]
    mask = r >= forget[:, None]
    return xp.where(mask, cork_full, 0), mask


def fit_prep_to_cal_b(prep, real_pad, mask):
    """prep (B, half) masked; real_pad (B, S, half) padded so column r-forget of the VI array sits at column r."""
    xp = _xp()
    d = (((real_pad - prep[:, None, :]) ** 2) * mask[:, None, :]).sum(axis=2)
    return xp.argmin(d, axis=1)


def phase_in_neighborhood_b(cork, index, ampl_pad, cork_pad, mask, n=5):
    xp = _xp(); B = cork.shape[0]
    rows = index[:, None] - 2 + xp.arange(n)[None, :]                          # (B, n)
    A = ampl_pad[xp.arange(B)[:, None], rows]; C = cork_pad[xp.arange(B)[:, None], rows]   # (B, n, half)
    w = xp.abs(cork)[:, None, :] * A * mask[:, None, :]
    th = xp.angle(cork[:, None, :] / xp.where(C == 0, 1, C))
    return (w * th).sum(axis=2) / w.sum(axis=2)


def quad_fit_phase_b(phases, index, n=5):
    xp = _xp(); B = phases.shape[0]
    xs = phases; ys = xp.asarray(np.arange(n) - np.floor(n / 2))
    X = xp.stack([xs ** 2, xs, xp.ones_like(xs)], axis=2)                      # (B, n, 3)
    W = xp.asarray(QUAD_WEIGHTS[:n])
    XtWX = xp.einsum("bni,n,bnj->bij", X, W, X); XtWy = xp.einsum("bni,n,n->bi", X, W, ys)
    c = xp.linalg.solve(XtWX, XtWy[..., None])[..., 0]
    return index.astype(xp.float64) + c[:, 2]


# ---------------------------------------------------------------------------------------------------- driver --
class CalPack:
    """per-bead calibration padded to a common (S, half) layout on the GPU: column r holds the VI's column r - forget."""

    def __init__(self, cals, half):
        xp = _xp(); B = len(cals); S = int(cals[0]["n_slices"])
        self.forget = xp.asarray([int(c["forget_radius"]) for c in cals])
        self.z_step = xp.asarray([float(c["z_step"]) for c in cals])
        self.cosband = xp.asarray(np.stack([np.asarray(c["cosband"], dtype=complex)[:2 * half - 1] for c in cals]))
        real = np.zeros((B, S, half)); ampl = np.zeros((B, S, half)); cork = np.zeros((B, S, half), dtype=complex)
        for b, c in enumerate(cals):
            f = int(c["forget_radius"]); L = half - f
            real[b, :, f:f + L] = c["real"][:, :L]; ampl[b, :, f:f + L] = c["ampl"][:, :L]; cork[b, :, f:f + L] = c["cork"][:, :L]
        self.real = xp.asarray(real); self.ampl = xp.asarray(ampl); self.cork = xp.asarray(cork)


def track_beads_gpu(image, x_in, y_in, cross, win_rs, win_h, pack, p=DEFAULT):
    """image: (H, W) numpy uint8/float; x_in, y_in: (B,) ints; returns dict of numpy arrays x, y, z, index (B,)."""
    xp = _xp(); B = len(x_in)
    h = lv_round(cross * p.k_half); half = lv_i32_div(cross, 2); n_end = lv_i32_div(cross, p.k_end)
    img = xp.asarray(np.asarray(image, dtype=np.float64))
    xi = xp.asarray(np.asarray(x_in, dtype=int)); yi = xp.asarray(np.asarray(y_in, dtype=int))
    rr = yi[:, None, None] - h + xp.arange(2 * h)[None, :, None]; cc = xi[:, None, None] - h + xp.arange(2 * h)[None, None, :]
    sub = img[rr, cc]                                                          # (B, 2h, 2h)
    ax, ay = average_xy_in_cross_b(sub, h, cross, p.arm)
    wrs = xp.asarray(win_rs); wh = xp.asarray(win_h)
    px = prep_avg_profile_b(ax, cross, n_end, wrs); py = prep_avg_profile_b(ay, cross, n_end, wrs)
    x_new, sx = find_avg_profile_center_b(px, wh, xi, half, p.n_pts)
    y_new, sy = find_avg_profile_center_b(py, wh, yi, half, p.n_pts)
    rad = radial_profile_b(sub, h + sx, h + sy, half)
    cork, mask = prep_i_of_r_b(rad, half, pack.forget, pack.cosband)
    prep = xp.real(cork)
    idx = fit_prep_to_cal_b(prep, pack.real, mask)
    ph = phase_in_neighborhood_b(cork, idx, pack.ampl, pack.cork, mask)
    zi = quad_fit_phase_b(ph, idx)
    return {"x": cp.asnumpy(x_new), "y": cp.asnumpy(y_new), "z": cp.asnumpy(zi * pack.z_step), "index": cp.asnumpy(idx), "z_index": cp.asnumpy(zi)}
