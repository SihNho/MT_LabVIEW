r"""d0_locate - find click targets ON A SCREENSHOT TAKEN IN THIS RUN, never from stored offsets.

WHY THIS EXISTS (the rule it implements)
  `archive/peer/2026-09-18-d0v4-picking-loop-frozen.md` is ACCEPTED: the v4 driver clicked
  (1114,915) for `Done Picking \nBeads?` because that point was hand-recorded on a DIFFERENT VI
  (the V6 copy, md5 2a78e17c..., `drive_original_copy_v2.py:138`), and on the 4.5 copy the button
  is ~65 px right and ~52 px up from there.  v4's gate 7 compared WINDOW RECTS, which say nothing
  about where a control sits inside a panel, so the gate passed while the thing it guards was
  wrong.  Control positions are NOT readable over our COM path - no traverse class returns a panel
  uid (`tools/bench/diag_d0_inventory.log:56`, gate B1 FAIL; every panel row in
  `tools/bench/d0_inventory.json` carries `class None pos None`) - so THE SCREENSHOT IS THE
  MEASUREMENT.  User rule, 2026-09-18 17:5x: "GUI 컨트롤 중에는 반드시 캡처 이미지 비교하는게
  필요할듯" (`docs/cycle27-plan.md` Pre-decided 9).

PRIOR ART CHECKED BEFORE WRITING IT
  - `tools/uitars_grounder.py` - a VLM (UI-TARS) grounder.  It needs Ollama running, answers in
    natural language, and its own calibration notes record that it needs a two-stage zoom pass to
    hit LabVIEW terminals.  Not deterministic, not usable inside an unattended bgrun gate.
  - `tools/lv_gui.ps1 -Action crop` - crops a PNG for a human to look at; it finds nothing.
  - `tools/lvclick.py`, `tools/bench/drive_original_copy_v{2,3,4}.py` - all carry HARD-CODED
    screen points.  That is the defect this module removes.
  - `docs/toolkit-capabilities.md` lists no image-analysis op.
  So nothing here duplicates an existing tool.

WHAT IT MEASURES
  locate_red_yes_button(png, rect) - a LabVIEW classic push button whose caption is RED text.
      Both buttons D0 must press are of this kind: `Done Picking \nBeads?` ("Yes", caption 25x12
      px, button 46x29) on the main panel, and `Selected?` ("Yes", caption 39x19, button 118x67)
      on each `choose bandpass` panel.  Test: red glyph run of a plausible size -> a dark neutral
      border (<=110) found on all four sides -> a light neutral face (150..245) over >=80 % of the
      non-caption pixels.
  template_score(png, box, ref) - mean |pixel difference| against a stored patch of the SAME
      button captured earlier from THIS VI's own panel.  IDENTITY check only: it decides WHICH of
      several red-captioned buttons is the one we want; it never supplies a coordinate.
  locate_image_display(png, rect) - the IMAQ display the bead picks land in: the large block of
      NEUTRAL MID-GREY (30..110).  The XY graph above it is black with a green grid (fails the
      neutral test) and the secondary display is pure black (fails the >=30 test).

MEASURED ON `tools/bench/p3_done_check.png` (a full-screen capture of Track_D0_copy_20260918.vi's
own running panel, 2026-09-18 17:28), search rect (0,51,1920,1080):
    Done `Yes` button   box (1155,848)-(1200,876)  centre (1177,862)  caption 25x12  score 0.00
    next-best candidate                            centre (1175,511)                 score 19.16
    image display       box (297,451)-(937,963) = 640x512 = the 1280x1024 camera at half scale
    the v4 point actually clicked, for contrast:   (1114,915) - 63 px left, 53 px below centre
"""
import os

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REF_DONE = os.path.join(HERE, "ref_done_yes_button.png")   # 46x29, cut from p3_done_check.png


def load(png):
    return np.asarray(Image.open(png).convert("RGB")).astype(np.int16)


def _clip(rect, w, h):
    l, t, r, b = rect
    return max(0, int(l)), max(0, int(t)), min(w, int(r)), min(h, int(b))


# ------------------------------------------------------------------ red captions
def red_mask(a):
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    return (r >= 120) & ((r - g) >= 60) & ((r - b) >= 60)


def clusters(mask, gap=6):
    """Connected components of a boolean mask, over the True coordinates only (a few thousand)."""
    ys, xs = np.nonzero(mask)
    boxes = []
    for (x, y) in zip(xs.tolist(), ys.tolist()):
        hit = None
        for c in boxes:
            if (c[0] - gap <= x <= c[2] + gap) and (c[1] - gap <= y <= c[3] + gap):
                hit = c
                break
        if hit is None:
            boxes.append([x, y, x, y, 1])
        else:
            hit[0] = min(hit[0], x); hit[1] = min(hit[1], y)
            hit[2] = max(hit[2], x); hit[3] = max(hit[3], y)
            hit[4] += 1
    changed = True
    while changed:
        changed = False
        for i in range(len(boxes)):
            for j in range(len(boxes) - 1, i, -1):
                a, b = boxes[i], boxes[j]
                if (a[0] - gap <= b[2] and b[0] - gap <= a[2]
                        and a[1] - gap <= b[3] and b[1] - gap <= a[3]):
                    a[0] = min(a[0], b[0]); a[1] = min(a[1], b[1])
                    a[2] = max(a[2], b[2]); a[3] = max(a[3], b[3]); a[4] += b[4]
                    boxes.pop(j)
                    changed = True
    return boxes


def _neutral(px, lo, hi):
    r, g, b = int(px[0]), int(px[1]), int(px[2])
    return lo <= r <= hi and abs(r - g) <= 14 and abs(g - b) <= 14 and abs(r - b) <= 14


def button_around(a, cx, cy, maxd=90):
    """Walk out from (cx,cy) to the first dark neutral pixel on each side. (l,t,r,b) or None."""
    h, w = a.shape[0], a.shape[1]
    got = {}
    for name, (dx, dy) in (("l", (-1, 0)), ("r", (1, 0)), ("t", (0, -1)), ("b", (0, 1))):
        x, y, d, found = cx, cy, 0, None
        while d < maxd:
            x += dx; y += dy; d += 1
            if not (0 <= x < w and 0 <= y < h):
                break
            if _neutral(a[y, x], 0, 110):
                found = (x, y)
                break
        if found is None:
            return None
        got[name] = found
    return (got["l"][0], got["t"][1], got["r"][0], got["b"][1])


def face_is_light(a, box, red, need=0.80):
    l, t, r, b = box
    if r - l < 18 or b - t < 12:
        return False, "box %dx%d too small" % (r - l, b - t)
    light = tot = 0
    for y in range(t + 2, b - 1):
        for x in range(l + 2, r - 1):
            if red[y, x]:
                continue
            tot += 1
            if _neutral(a[y, x], 150, 245):
                light += 1
    if tot == 0:
        return False, "no non-caption pixels"
    return (light / float(tot)) >= need, "light-grey face %.2f of %d px" % (light / float(tot), tot)


def locate_red_yes_button(png, rect, wmin=15, wmax=60, hmin=8, hmax=32, maxd=90):
    """(best, candidates) - `best` is the largest red caption that passed every test."""
    a = load(png)
    h, w = a.shape[0], a.shape[1]
    l, t, r, b = _clip(rect, w, h)
    full_red = red_mask(a)
    cands = []
    for (x0, y0, x1, y1, n) in clusters(red_mask(a[t:b, l:r])):
        cw, ch = x1 - x0 + 1, y1 - y0 + 1
        sx0, sy0, sx1, sy1 = x0 + l, y0 + t, x1 + l, y1 + t
        row = {"caption_box": (sx0, sy0, sx1, sy1), "caption_size": (cw, ch), "red_px": n,
               "caption_centre": ((sx0 + sx1) // 2, (sy0 + sy1) // 2)}
        cands.append(row)
        if not (wmin <= cw <= wmax and hmin <= ch <= hmax):
            row["reject"] = "caption %dx%d outside %d..%dx%d..%d" % (cw, ch, wmin, wmax, hmin, hmax)
            continue
        box = button_around(a, row["caption_centre"][0], row["caption_centre"][1], maxd)
        if box is None:
            row["reject"] = "no dark border within %d px on all 4 sides" % maxd
            continue
        row["button_box"] = box
        good, why = face_is_light(a, box, full_red)
        row["face"] = why
        if not good:
            row["reject"] = "face: " + why
            continue
        row["centre"] = ((box[0] + box[2]) // 2, (box[1] + box[3]) // 2)
        row["button_size"] = (box[2] - box[0] + 1, box[3] - box[1] + 1)
    good = [c for c in cands if "centre" in c]
    good.sort(key=lambda c: -c["red_px"])
    return (good[0] if good else None), cands


def template_score(png, box, ref_png=REF_DONE):
    if not os.path.isfile(ref_png):
        return None, "no reference patch at %s" % ref_png
    a = Image.open(png).convert("RGB").crop((box[0], box[1], box[2] + 1, box[3] + 1))
    rf = Image.open(ref_png).convert("RGB")
    resized = rf.size != a.size
    if resized:
        rf = rf.resize(a.size, Image.NEAREST)
    d = np.abs(np.asarray(a).astype(np.int16) - np.asarray(rf).astype(np.int16))
    return float(d.mean()), ("mean|diff| over %dx%d vs %s%s"
                             % (a.size[0], a.size[1], os.path.basename(ref_png),
                                " (RESIZED - size mismatch)" if resized else ""))


def pick_by_template(png, rect, ref_png=REF_DONE, max_score=12.0, ratio=0.5,
                     caption_ref=(25, 12), caption_tol=4, **kw):
    """The disambiguator.  Returns (winner_or_None, why, candidates).

    Several red-captioned buttons exist on the main panel (measured: 6 pass the shape tests on
    p3_done_check.png).  The winner is the one whose PIXELS match the stored patch of the button
    we mean; the runner-up must be at least `ratio` worse, so an ambiguous screen fails loudly
    instead of clicking the wrong control.
    """
    _, cands = locate_red_yes_button(png, rect, **kw)
    scored = []
    for c in cands:
        if "centre" not in c:
            continue
        cw, ch = c["caption_size"]
        if abs(cw - caption_ref[0]) > caption_tol or abs(ch - caption_ref[1]) > caption_tol:
            c["reject"] = "caption %dx%d not within +-%d of the reference %s" % (cw, ch,
                                                                                 caption_tol,
                                                                                 caption_ref)
            continue
        s, why = template_score(png, c["button_box"], ref_png)
        c["template_score"], c["template_why"] = s, why
        if s is not None:
            scored.append((s, c))
    if not scored:
        return None, ("no candidate survived shape+caption filtering (%d red clusters examined)"
                      % len(cands)), cands
    scored.sort(key=lambda t: t[0])
    best_s, best = scored[0]
    second = scored[1][0] if len(scored) > 1 else None
    if best_s > max_score:
        return None, ("best template score %.2f > %.2f at %s - the button on screen is not the "
                      "one the reference patch was cut from"
                      % (best_s, max_score, best["centre"])), cands
    if second is not None and best_s > ratio * second:
        return None, ("AMBIGUOUS: best %.2f at %s vs second %.2f - not separated by the %.0f%% "
                      "margin" % (best_s, best["centre"], second, ratio * 100)), cands
    return best, ("template score %.2f (next %s); %s" % (best_s, second, best.get("template_why"))), cands


# ------------------------------------------------------------------ the image display
def locate_image_display(png, rect, minw=200, minh=150):
    a = load(png)
    h, w = a.shape[0], a.shape[1]
    l, t, r, b = _clip(rect, w, h)
    sub = a[t:b, l:r]
    R, G, B = sub[:, :, 0], sub[:, :, 1], sub[:, :, 2]
    v = (R + G + B) / 3.0
    m = ((np.abs(R - G) <= 14) & (np.abs(G - B) <= 14) & (np.abs(R - B) <= 14)
         & (v >= 30) & (v <= 110))

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
        return None, "no mid-grey band (cols=%s rows=%s, thresholds %d/%d)" % (cb, rb, tc, tr)
    box = (l + cb[0], t + rb[0], l + cb[1], t + rb[1])
    if (box[2] - box[0]) < minw or (box[3] - box[1]) < minh:
        return None, "band %s smaller than %dx%d" % (box, minw, minh)
    return box, "mid-grey band %s = %dx%d px" % (box, box[2] - box[0] + 1, box[3] - box[1] + 1)


def count_red_markers(png, rect, wmin=8, wmax=45, hmin=8, hmax=45):
    """The bead markers the VI draws at each pick.  Used as the post-click READBACK for the picks."""
    a = load(png)
    h, w = a.shape[0], a.shape[1]
    l, t, r, b = _clip(rect, w, h)
    out = []
    for (x0, y0, x1, y1, n) in clusters(red_mask(a[t:b, l:r])):
        cw, ch = x1 - x0 + 1, y1 - y0 + 1
        if wmin <= cw <= wmax and hmin <= ch <= hmax:
            out.append(((x0 + l, y0 + t, x1 + l, y1 + t), (cw, ch), n))
    return out


def save_crop(png, box, out, pad=16, scale=4):
    im = Image.open(png).convert("RGB")
    c = im.crop((max(0, box[0] - pad), max(0, box[1] - pad),
                 min(im.width, box[2] + pad + 1), min(im.height, box[3] + pad + 1)))
    c = c.resize((c.width * scale, c.height * scale), Image.NEAREST)
    c.save(out)
    return out


if __name__ == "__main__":
    import sys
    png = sys.argv[1]
    rect = tuple(int(x) for x in sys.argv[2:6]) if len(sys.argv) > 5 else (0, 51, 1920, 1080)
    w, why, cands = pick_by_template(png, rect)
    print("DONE BUTTON:", w and w["centre"], "|", why)
    print("candidates passing shape:", sum(1 for c in cands if "centre" in c))
    print("IMAGE DISPLAY:", locate_image_display(png, rect))
