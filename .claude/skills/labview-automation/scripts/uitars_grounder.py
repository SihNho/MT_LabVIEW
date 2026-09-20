#!/usr/bin/env python3
r"""
uitars_grounder.py — LOCAL GUI grounding for LabVIEW with UI-TARS-1.5-7B via Ollama.

WHAT THIS IS
    A "where do I click?" oracle that runs entirely on this machine — no subscription, no API
    key, no data leaving the rig. Give it a LabVIEW window title and a plain-language target
    ("the N terminal of the For Loop", "the right border of the numeric constant") and it
    returns an absolute screen coordinate, ready for `lv_gui.ps1`.

    UI-TARS-1.5-7B scores 61.6% on ScreenSpot-Pro (GUI grounding) versus 23.4% for OpenAI's
    computer-use agent — grounding is exactly the residual failure mode on this project
    (5 px terminal stubs, top-edge terminals). It is Apache-2.0 and Qwen2.5-VL based.

ROLE IN THE ARCHITECTURE
    Claude (planner)  -> "click the N terminal of the For Loop in window X"
    THIS (grounder)   -> screen coordinate (x, y)   [local, ~1-3 s on an RTX 2060]
    lv_gui.ps1        -> performs the click (still the ONLY thing that touches the mouse)

    It does NOT run an autonomous loop. One question, one coordinate. Claude keeps all
    judgement; the grounder only replaces the crop-and-squint step. That keeps every safety
    property of the existing workflow intact — nothing here can save, run, or open a VI.

THE COORDINATE CONTRACT (the part that must be exactly right)
    UI-TARS is Qwen2.5-VL based and outputs ABSOLUTE PIXEL coordinates in the space of the
    image *after* Qwen's `smart_resize` (dimensions rounded to a multiple of 28, area clamped
    to [min_pixels, max_pixels]). To map back:
        orig_x = model_x * orig_w / resized_w
        orig_y = model_y * orig_h / resized_h
    then screen = window_rect.left/top + orig.  We capture ONE window (shotwin), never the
    full screen, so a wrong-window click is impossible by construction.
    Source: ByteDance UI-TARS README_coordinates.md (see REFERENCES).

    Ollama performs the resize itself, so we replicate smart_resize locally purely to know
    the resized dimensions the model saw. If a future Ollama changes its preprocessing, the
    `--calibrate` mode will expose it: it asks the model to point at a synthetic marker at a
    known position and reports the error.

REFERENCES
    UI-TARS (ByteDance-Seed), Apache-2.0 — https://github.com/bytedance/UI-TARS
    Model: ByteDance-Seed/UI-TARS-1.5-7B — https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B
    GGUF + mmproj by mradermacher — https://huggingface.co/mradermacher/UI-TARS-1.5-7B-GGUF
    Coordinate guide — https://github.com/bytedance/UI-TARS/blob/main/README_coordinates.md
    Prompt template (GROUNDING) — https://github.com/bytedance/UI-TARS/blob/main/codes/ui_tars/prompt.py
    Ollama (MIT) — https://github.com/ollama/ollama ; /api/generate with base64 `images`.

USAGE
    py tools\uitars_grounder.py --window "Untitled 9 Block Diagram" --target "the N terminal of the For Loop"
    py tools\uitars_grounder.py --window "Untitled 9 Block Diagram" --calibrate
    Add --click to perform the click via lv_gui.ps1 after grounding (still refuses protected windows).
"""
from __future__ import annotations

import sys as _sys
for _n in ("stdout", "stderr"):
    _s = getattr(_sys, _n)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")   # console is cp949

import argparse
import base64
import json
import math
import re
import subprocess
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OLLAMA_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "ui-tars-1.5-7b"
PROTECTED = ["Min_Track N beads 4.5", "Min_Track N beads 4.6", "3StateClamping", "4ParallelLoop"]

# Qwen2.5-VL smart_resize constants (from the UI-TARS coordinate guide)
IMAGE_FACTOR = 28
MIN_PIXELS = 100 * 28 * 28
MAX_PIXELS = 16384 * 28 * 28

# UI-TARS GROUNDING template (verbatim structure from codes/ui_tars/prompt.py)
GROUNDING_PROMPT = (
    "You are a GUI agent. You are given a task and your action history, with screenshots. "
    "You need to perform the next action to complete the task.\n\n"
    "## Output Format\n"
    "Action: ...\n\n"
    "## Action Space\n"
    "click(point='<point>x1 y1</point>')\n\n"
    "## User Instruction\n"
    "{instruction}"
)

_POINT_RE = re.compile(r"<point>\s*(-?\d+)\s+(-?\d+)\s*</point>|\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)")


# ----------------------------------------------------------------------------- lv_gui bridge
def lv(*args: str) -> str:
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& .\\tools\\lv_gui.ps1 " + " ".join(_q(a) for a in args)]
    r = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"lv_gui.ps1 failed: {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def _q(a: str) -> str:
    return a if re.fullmatch(r"[A-Za-z0-9_\-\.\\:]+", a) else '"' + a.replace('"', '`"') + '"'


@dataclass
class Rect:
    left: int; top: int; right: int; bottom: int
    @property
    def w(self): return self.right - self.left
    @property
    def h(self): return self.bottom - self.top


_RECT_RE = re.compile(r"left=(-?\d+)\s+top=(-?\d+)\s+right=(-?\d+)\s+bottom=(-?\d+)")


def capture(title: str, png: Path) -> Rect:
    for bad in PROTECTED:
        if bad.lower() in title.lower():
            raise SystemExit(f"REFUSED: '{title}' matches protected pattern '{bad}'")
    lv("-Action", "focus", "-Title", title)
    time.sleep(0.6)
    out = lv("-Action", "shotwin", "-Title", title, "-Out", str(png))
    m = _RECT_RE.search(out)
    if not m:
        raise RuntimeError(f"no rect in: {out}")
    return Rect(*map(int, m.groups()))


# ----------------------------------------------------------------------------- coordinate contract
def smart_resize(h: int, w: int, factor=IMAGE_FACTOR, min_pixels=MIN_PIXELS, max_pixels=MAX_PIXELS):
    """Replicates Qwen2.5-VL's smart_resize so we know the dimensions the model grounded on."""
    def r(x): return round(x / factor) * factor
    def c(x): return math.ceil(x / factor) * factor
    def f(x): return math.floor(x / factor) * factor
    hb, wb = max(factor, r(h)), max(factor, r(w))
    if hb * wb > max_pixels:
        beta = math.sqrt((h * w) / max_pixels)
        hb, wb = f(h / beta), f(w / beta)
    elif hb * wb < min_pixels:
        beta = math.sqrt(min_pixels / (h * w))
        hb, wb = c(h * beta), c(w * beta)
    return hb, wb


def model_to_screen(mx: int, my: int, rect: Rect, seen_w: float | None = None,
                    seen_h: float | None = None) -> tuple[int, int]:
    """Map model pixel coords -> screen.

    EMPIRICAL FINDING (2026-08-26, Ollama 0.32.15, qwen2vl arch): Ollama does NOT use Qwen's
    published smart_resize. It enforces its own minimum pixel budget and UPSCALES small
    windows (a 1000x700 capture became ~1086x760; a 1400x900 one was left ~as-is). The model
    grounds in that upscaled space, so dividing by Qwen's smart_resize dims left a systematic
    +8..+10% bias. The reliable source of truth is the image token count Ollama reports in
    every /api/generate response: seen_pixels = image_tokens * 28 * 28, aspect preserved.
    When (seen_w, seen_h) are supplied they are used; otherwise fall back to smart_resize.
    """
    if seen_w and seen_h:
        rw, rh = seen_w, seen_h
    else:
        rh, rw = smart_resize(rect.h, rect.w)
    ox = int(round(mx * rect.w / rw))
    oy = int(round(my * rect.h / rh))
    return rect.left + ox, rect.top + oy


def seen_dims_from_tokens(image_tokens: int, w: int, h: int) -> tuple[float, float]:
    """Dimensions the model actually saw, inferred from Ollama's image token count
    (each token = one 28x28 patch after the 2x2 merge). Aspect ratio is preserved."""
    px = image_tokens * IMAGE_FACTOR * IMAGE_FACTOR
    seen_h = math.sqrt(px * h / w)
    seen_w = px / seen_h
    return seen_w, seen_h


# ----------------------------------------------------------------------------- Ollama
def ollama_ground(model: str, png: Path, instruction: str, timeout: int = 120) -> tuple[str, float, int]:
    """Returns (response_text, seconds, image_tokens). image_tokens is derived from
    prompt_eval_count minus the text prompt's own tokens, measured once per call by a
    text-only dry request — cheap, and it makes the coordinate mapping self-calibrating."""
    body = {
        "model": model,
        "prompt": GROUNDING_PROMPT.format(instruction=instruction),
        "images": [base64.b64encode(png.read_bytes()).decode("ascii")],
        "stream": False,
        "options": {"temperature": 0.0, "num_predict": 64},
    }
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    dt = time.time() - t0
    total = int(data.get("prompt_eval_count") or 0)
    text_tokens = _text_prompt_tokens(model, body["prompt"])
    image_tokens = max(0, total - text_tokens)
    return data.get("response", ""), dt, image_tokens


_TEXT_TOKEN_CACHE: dict[tuple[str, str], int] = {}


def _text_prompt_tokens(model: str, prompt: str) -> int:
    """Token count of the text prompt alone (no image), cached per (model, prompt)."""
    key = (model, prompt)
    if key in _TEXT_TOKEN_CACHE:
        return _TEXT_TOKEN_CACHE[key]
    body = {"model": model, "prompt": prompt, "stream": False, "options": {"num_predict": 1}}
    req = urllib.request.Request(f"{OLLAMA_URL}/api/generate", data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        n = int(json.loads(resp.read().decode("utf-8")).get("prompt_eval_count") or 0)
    _TEXT_TOKEN_CACHE[key] = n
    return n


def parse_point(text: str) -> tuple[int, int] | None:
    m = _POINT_RE.search(text)
    if not m:
        return None
    g = [x for x in m.groups() if x is not None]
    return int(g[0]), int(g[1])


# ----------------------------------------------------------------------------- modes
ZOOM = 3          # magnification for the second pass
ZOOM_BOX = 300    # side of the square region (in window px) cropped around the coarse guess


def ground_two_stage(model: str, png: Path, rect: Rect, target: str) -> tuple[tuple[int, int], dict]:
    """Coarse pass on the whole window, then a ZOOMx crop around that guess, re-grounded.

    EMPIRICAL (2026-08-26): on a 1000x700 LabVIEW window the 1x pass missed a 5 px 'N'
    terminal by ~60 px; the same query on a 3x crop landed within (0,+3) px of probe truth.
    Small targets are a resolution problem, not a model problem — so zoom.
    """
    from PIL import Image
    raw1, dt1, tok1 = ollama_ground(model, png, target)
    p1 = parse_point(raw1)
    info = {"coarse_raw": raw1.strip(), "coarse_s": dt1}
    if p1 is None:
        return None, info
    sw, sh = seen_dims_from_tokens(tok1, rect.w, rect.h)
    cx = p1[0] * rect.w / sw            # coarse guess in window pixels
    cy = p1[1] * rect.h / sh
    info["coarse_win"] = (round(cx), round(cy))

    img = Image.open(png)
    half = ZOOM_BOX // 2
    x0 = int(max(0, min(cx - half, rect.w - ZOOM_BOX)))
    y0 = int(max(0, min(cy - half, rect.h - ZOOM_BOX)))
    crop = img.crop((x0, y0, x0 + ZOOM_BOX, y0 + ZOOM_BOX)).resize((ZOOM_BOX * ZOOM, ZOOM_BOX * ZOOM), Image.LANCZOS)
    zp = png.with_name(png.stem + "_zoom.png")
    crop.save(zp)

    raw2, dt2, tok2 = ollama_ground(model, zp, target)
    p2 = parse_point(raw2)
    info.update({"fine_raw": raw2.strip(), "fine_s": dt2, "crop_origin": (x0, y0)})
    if p2 is None:
        return (rect.left + round(cx), rect.top + round(cy)), info
    zw, zh = seen_dims_from_tokens(tok2, ZOOM_BOX * ZOOM, ZOOM_BOX * ZOOM)
    fx = x0 + (p2[0] * (ZOOM_BOX * ZOOM) / zw) / ZOOM
    fy = y0 + (p2[1] * (ZOOM_BOX * ZOOM) / zh) / ZOOM
    return (rect.left + round(fx), rect.top + round(fy)), info


def ground(args) -> int:
    png = PROJECT_ROOT / "tools" / "uitars_runs" / f"{time.strftime('%Y%m%d-%H%M%S')}.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    rect = capture(args.window, png)
    if args.zoom:
        pt_screen, info = ground_two_stage(args.model, png, rect, args.target)
        print(f"window rect: {rect}")
        print(f"coarse ({info['coarse_s']:.1f}s): {info['coarse_raw']!r} -> window {info.get('coarse_win')}")
        if pt_screen is None:
            print("NO POINT PARSED"); return 1
        if "fine_raw" in info:
            print(f"fine   ({info['fine_s']:.1f}s): {info['fine_raw']!r}  (crop origin {info['crop_origin']}, x{ZOOM})")
        sx, sy = pt_screen
        print(f"-> screen ({sx}, {sy})")
    else:
        raw, dt, itok = ollama_ground(args.model, png, args.target)
        pt = parse_point(raw)
        sw, sh = seen_dims_from_tokens(itok, rect.w, rect.h)
        print(f"window rect: {rect}   captured {rect.w}x{rect.h}, model saw ~{sw:.0f}x{sh:.0f} ({itok} image tokens)")
        print(f"model ({dt:.1f}s): {raw.strip()!r}")
        if pt is None:
            print("NO POINT PARSED")
            return 1
        sx, sy = model_to_screen(pt[0], pt[1], rect, sw, sh)
        print(f"model point {pt} -> screen ({sx}, {sy})")
    if args.click:
        lv("-Action", "click", "-X", str(sx), "-Y", str(sy))
        print("clicked")
    return 0


def calibrate(args) -> int:
    """Draw a marker at a known spot on the captured window image and ask the model to point at it.
    Reports pixel error — this is how we verify the coordinate contract against THIS Ollama build."""
    from PIL import Image, ImageDraw
    png = PROJECT_ROOT / "tools" / "uitars_runs" / "calib_src.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    rect = capture(args.window, png)
    img = Image.open(png).convert("RGB")
    errs = []
    for (fx, fy) in ((0.25, 0.30), (0.70, 0.60), (0.50, 0.85)):
        tx, ty = int(rect.w * fx), int(rect.h * fy)
        marked = img.copy()
        d = ImageDraw.Draw(marked)
        d.ellipse((tx - 9, ty - 9, tx + 9, ty + 9), fill=(255, 0, 255), outline=(0, 0, 0), width=2)
        mp = png.with_name(f"calib_{int(fx*100)}_{int(fy*100)}.png")
        marked.save(mp)
        raw, dt, itok = ollama_ground(args.model, mp, "the solid magenta circle")
        pt = parse_point(raw)
        if pt is None:
            print(f"target ({tx},{ty}): NO POINT  raw={raw.strip()!r}")
            continue
        sw, sh = seen_dims_from_tokens(itok, rect.w, rect.h)
        sx, sy = model_to_screen(pt[0], pt[1], rect, sw, sh)
        ex, ey = sx - (rect.left + tx), sy - (rect.top + ty)
        errs.append(math.hypot(ex, ey))
        print(f"target img({tx},{ty})  model{pt}  seen~{sw:.0f}x{sh:.0f}  -> screen({sx},{sy})  err=({ex:+d},{ey:+d}) px  {dt:.1f}s")
    if errs:
        print(f"mean error {sum(errs)/len(errs):.1f} px over {len(errs)} targets "
              f"(a 5 px terminal needs mean error <= ~4 px to be useful)")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--window", required=True)
    p.add_argument("--target", help="what to find, in plain language")
    p.add_argument("--model", default=DEFAULT_MODEL)
    p.add_argument("--click", action="store_true", help="click the grounded point via lv_gui.ps1")
    p.add_argument("--zoom", action="store_true", default=True,
                   help="two-stage: coarse pass, then re-ground on a 3x crop (default ON; needed for small terminals)")
    p.add_argument("--no-zoom", dest="zoom", action="store_false", help="single-pass only")
    p.add_argument("--calibrate", action="store_true", help="verify the coordinate contract with synthetic markers")
    a = p.parse_args()
    if a.calibrate:
        return calibrate(a)
    if not a.target:
        p.error("--target is required unless --calibrate")
    return ground(a)


if __name__ == "__main__":
    _sys.exit(main())
