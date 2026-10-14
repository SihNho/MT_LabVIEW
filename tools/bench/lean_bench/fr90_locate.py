r"""fr90_locate - the IMAQ display locator for LIVE legs (d0_locate.py is NOT edited). Task fr90 smoke S0 attempt 1 (04:07) failed
at v5 L2 because d0_locate.locate_image_display only accepts mid-grey pixels (mean 30..110); the live field today is brighter, so
the band it found was 196 x 3 px (out_p64/fr90/s0/legs/leg1_B_a1/leg_child.log:175). This wrapper:
  1. calls the original; if it returns a box, that box is used unchanged;
  2. otherwise re-runs the SAME band method with the grey ceiling raised (110 -> 160, 200, 230, in that order) and accepts the first
     box whose size is the camera image at the panel's scale: aspect 1280/1024 within 3 % and width 560..720 px (the display was
     640 x 512 in every earlier capture: d0_locate's v3 rect (232,500)-(873,1013), drive_original_copy_v5.py:39-40).
No click is derived from anything else; picks stay fractions of the located box (v5 L3).
Retry 1 (C2): whichever locator gave the box, it is used only if every side is within +-5 px of the recorded display rect
(232,500)-(873,1013); otherwise (or if nothing was found) the locator returns None, so v5 stops before any pick (leg FAIL).
The box, the locator and the check are printed (leg_child.log) and are v5 L2's detail text.
    py tools/bench/lean_bench/fr90_locate.py <png> [l t r b]     (offline test on a saved capture)"""
import os, sys                                                                            # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import d0_locate as L                                                                     # noqa: E402
_orig = L.locate_image_display


def _band_box(png, rect, vmax):
    a = L.load(png)
    h, w = a.shape[0], a.shape[1]
    l, t, r, b = L._clip(rect, w, h)
    sub = a[t:b, l:r]
    R, G, B = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
    v = (R + G + B) / 3.0
    m = ((np.abs(R - G) <= 14) & (np.abs(G - B) <= 14) & (np.abs(R - B) <= 14) & (v >= 30) & (v <= vmax))

    def band(cnt, thr):
        best, i = None, 0
        while i < len(cnt):
            if cnt[i] >= thr:
                j = i
                while j + 1 < len(cnt) and cnt[j + 1] >= thr:
                    j += 1
                if best is None or (j - i) > (best[1] - best[0]):
                    best = (i, j)
                i = j + 1
            else:
                i += 1
        return best
    tc, tr = int(0.25 * m.shape[0]), int(0.25 * m.shape[1])
    cb, rb = band(m.sum(axis=0), tc), band(m.sum(axis=1), tr)
    if cb is None or rb is None:
        return None
    return (l + cb[0], t + rb[0], l + cb[1], t + rb[1])


REC_RECT, TOL = (232, 500, 873, 1013), 5                                                 # task fr90 retry 1, C2: the recorded display rect


def box_check(box):
    """C2: every side of `box` within +-TOL px of REC_RECT. Returns (ok, text)."""
    if not box:
        return False, "no box"
    d = [int(b) - r for b, r in zip(box, REC_RECT)]
    return all(abs(x) <= TOL for x in d), "box %s vs recorded %s: side offsets %s (tol +-%d)" % (tuple(box), REC_RECT, d, TOL)


def _locate(png, rect, minw, minh):
    box, why = _orig(png, rect, minw, minh)
    if box:
        return box, "original", why
    tried = []
    for vmax in (160, 200, 230):
        bx = _band_box(png, rect, vmax)
        tried.append((vmax, bx))
        if bx:
            bw, bh = bx[2] - bx[0] + 1, bx[3] - bx[1] + 1
            if 560 <= bw <= 720 and abs((bw / float(bh)) / 1.25 - 1.0) <= 0.03:
                return bx, "fr90 fallback", ("original: %s; grey ceiling %d -> box %s = %dx%d px (aspect %.3f)"
                                             % (why, vmax, bx, bw, bh, bw / float(bh)))
    return None, "none", "original: %s; fr90 fallback found no camera-shaped box: %s" % (why, tried)


def locate_image_display(png, rect, minw=200, minh=150):
    """The box only if the C2 check passes; otherwise None (v5 then returns before any pick: leg FAIL)."""
    box, who, why = _locate(png, rect, minw, minh)
    ok, txt = box_check(box)
    line = "[fr90 locate] locator=%s; %s; C2 %s; %s" % (who, txt, "PASS" if ok else "FAIL -> no pick", why)
    print(line, flush=True)
    return (box, line) if ok else (None, line)


if __name__ == "__main__":
    png = sys.argv[1]
    rect = tuple(int(x) for x in sys.argv[2:6]) if len(sys.argv) > 5 else (0, 51, 1920, 1080)
    print("ORIGINAL", _orig(png, rect))
    print("FR90    ", locate_image_display(png, rect))
