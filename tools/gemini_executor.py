#!/usr/bin/env python3
"""
gemini_executor.py — a low-latency GUI *executor* for LabVIEW, driven by Gemini computer-use.

ROLE IN THE ARCHITECTURE (user's proposal, 2026-08-26)
    Claude (planner)  ->  decides WHAT to do and hands over one bounded sub-task
    Gemini (executor) ->  looks at the screen and performs the next one-or-two GUI actions
    lv_gui.ps1        ->  the ONLY thing that touches the mouse/keyboard, for both of them

    Gemini never drives the machine directly. Every action it proposes is translated into a
    `lv_gui.ps1` call, so it inherits the hard-won mechanics: window-rect coordinate law,
    `focus`-before-click, deterministic `probe`/`wire`. That is deliberate — the measured
    bottleneck on this project was round-trips and coordinate-frame errors, not model IQ.

WHY THE CAPTURE IS A WINDOW, NOT THE SCREEN
    Gemini returns coordinates normalised to 0..999 over whatever image it was shown.
    We show it ONE LabVIEW window (via `shotwin`, which also prints the window rect), and
    denormalise against that window's rect:  screen = rect.left + x/1000 * rect.width.
    Showing the full screen instead would re-create exactly the wrong-window misclicks that
    cost several benchmark runs. It also makes each round-trip cheaper (smaller image).

SAFETY (non-negotiable, independent of model)
    * Never runs unless a LabVIEW window title matches --window (no blind clicking).
    * Refuses to act on any window whose title contains a protected name (see PROTECTED).
    * Honors Gemini's `safety_decision: require_confirmation` by STOPPING, never auto-acking.
    * Keyboard actions are allow-listed: no Ctrl+S / Save / File menu / Alt+F4 ever.
    * Hard step cap (--max-steps) and a per-run action log for audit.
    The ASI piezo stage, acquisition start, magnet moves, force settings and data overwrites
    are human-confirmed operations on this rig and are NOT reachable through this tool.

REFERENCES
    Gemini Computer Use docs — https://ai.google.dev/gemini-api/docs/computer-use
    google-genai SDK (Apache-2.0) — https://github.com/googleapis/python-genai
    Google's reference agent (browser-only, Apache-2.0) — https://github.com/google/computer-use-preview
    Desktop action set, request/response shapes and 0..999 normalisation are taken from the
    official docs above; no code was copied from the reference repo.

USAGE
    set GEMINI_API_KEY=...            (never commit it; never put it in this file)
    py tools\gemini_executor.py --window "Untitled 9 Block Diagram" ^
        --task "Place a numeric constant on empty canvas left of the For Loop" ^
        --model gemini-3.5-flash-lite --max-steps 12 --dry-run
    Drop --dry-run to actually execute. Start with --dry-run: it prints every action Gemini
    WOULD take, with denormalised coordinates, without touching LabVIEW.
"""
from __future__ import annotations

import io as _io
import sys as _sys

# This machine's console is cp949 (Korean locale). Gemini's text and this file's docstring
# contain characters outside cp949, and a UnicodeEncodeError on print() would kill a run
# mid-loop. Force UTF-8 on stdout/stderr before anything is printed.
for _stream in ("stdout", "stderr"):
    _s = getattr(_sys, _stream)
    if hasattr(_s, "reconfigure"):
        _s.reconfigure(encoding="utf-8", errors="replace")

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LV_GUI = PROJECT_ROOT / "tools" / "lv_gui.ps1"
LOG_DIR = PROJECT_ROOT / "tools" / "gemini_runs"

# Windows whose titles must never be acted on, whatever Gemini says. Substring match,
# case-insensitive. The original VIs are the ones that matter; add more freely.
PROTECTED = [
    "Min_Track N beads 4.5",
    "Min_Track N beads 4.6",
    "3StateClamping",
    "4ParallelLoop",
]

# Keys / hotkeys Gemini may press. Everything else is refused. Deliberately excludes
# ctrl+s (save), alt+f4 (close), ctrl+q, and anything that opens the File menu.
ALLOWED_KEYS = {"enter", "esc", "escape", "tab", "delete", "del", "home", "end",
                "space", "backspace", "up", "down", "left", "right"}
ALLOWED_HOTKEYS = {"ctrl+e", "ctrl+b", "ctrl+z", "ctrl+space", "ctrl+h", "ctrl+a"}

DEFAULT_MODEL = "gemini-3.5-flash-lite"
ESCALATION_MODEL = "gemini-3.7-flash"


# --------------------------------------------------------------------------------------
# lv_gui.ps1 bridge — the only path to the mouse/keyboard
# --------------------------------------------------------------------------------------

def lv(*args: str, timeout: int = 60) -> str:
    """Run `& .\tools\lv_gui.ps1 -Action ...` from the project root and return stdout."""
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& .\\tools\\lv_gui.ps1 " + " ".join(_ps_quote(a) for a in args)]
    r = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"lv_gui.ps1 failed: {' '.join(args)}\n{r.stderr.strip()}")
    return r.stdout.strip()


def _ps_quote(a: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_\-\.\\:]+", a):
        return a
    return '"' + a.replace('"', '`"') + '"'


@dataclass
class Rect:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def width(self) -> int:
        return self.right - self.left

    @property
    def height(self) -> int:
        return self.bottom - self.top


_RECT_RE = re.compile(r"left=(-?\d+)\s+top=(-?\d+)\s+right=(-?\d+)\s+bottom=(-?\d+)")


def capture_window(title: str, out_png: Path) -> Rect:
    """shotwin the target window; parse the self-describing rect it prints."""
    out = lv("-Action", "shotwin", "-Title", title, "-Out", str(out_png))
    m = _RECT_RE.search(out)
    if not m:
        raise RuntimeError(f"could not parse window rect from: {out}")
    return Rect(*map(int, m.groups()))


def denorm(rect: Rect, x: int, y: int) -> tuple[int, int]:
    """Gemini's 0..999 image coords -> absolute screen coords for THIS window."""
    sx = rect.left + round(x / 1000.0 * rect.width)
    sy = rect.top + round(y / 1000.0 * rect.height)
    return sx, sy


def window_is_safe(title: str) -> None:
    lowered = title.lower()
    for bad in PROTECTED:
        if bad.lower() in lowered:
            raise SystemExit(f"REFUSED: '{title}' matches protected pattern '{bad}'.")
    titles = lv("-Action", "windows")
    if title not in titles:
        raise SystemExit(f"REFUSED: no open LabVIEW window titled '{title}'.\nOpen windows:\n{titles}")


# --------------------------------------------------------------------------------------
# Action translation: Gemini function_call -> lv_gui.ps1
# --------------------------------------------------------------------------------------

class Refused(Exception):
    pass


def execute(action: str, args: dict, rect: Rect, dry: bool) -> str:
    """Translate one Gemini action into lv_gui.ps1 calls. Returns a short description."""
    def xy() -> tuple[int, int]:
        return denorm(rect, int(args["x"]), int(args["y"]))

    if action in ("click", "double_click", "right_click", "move"):
        sx, sy = xy()
        verb = {"click": "click", "double_click": "dclick", "right_click": "rclick", "move": "move"}[action]
        desc = f"{verb} @ screen({sx},{sy})  [norm {args.get('x')},{args.get('y')}]"
        if not dry:
            lv("-Action", verb, "-X", str(sx), "-Y", str(sy))
        return desc

    if action == "drag_and_drop":
        sx, sy = xy()
        dx, dy = denorm(rect, int(args["destination_x"]), int(args["destination_y"]))
        desc = f"drag ({sx},{sy}) -> ({dx},{dy})"
        if not dry:
            lv("-Action", "drag", "-X", str(sx), "-Y", str(sy), "-X2", str(dx), "-Y2", str(dy))
        return desc

    if action == "scroll":
        sx, sy = xy()
        direction = str(args.get("direction", "down")).lower()
        mag = int(args.get("magnitude", 3))
        notches = mag if direction == "up" else -mag
        desc = f"wheel {notches} @ ({sx},{sy})"
        if not dry:
            lv("-Action", "wheel", "-X", str(sx), "-Y", str(sy), "-Notches", str(notches))
        return desc

    if action == "type":
        text = str(args.get("text", ""))
        if any(tok in text.lower() for tok in ("^s", "%f", "%{f4}")):
            raise Refused(f"type refused (contains a forbidden control sequence): {text!r}")
        desc = f"type {text!r}" + (" + Enter" if args.get("press_enter") else "")
        if not dry:
            lv("-Action", "keys", "-Key", text)
            if args.get("press_enter"):
                lv("-Action", "key", "-Key", "enter")
        return desc

    if action == "press_key":
        key = str(args.get("key", "")).lower()
        if key not in ALLOWED_KEYS:
            raise Refused(f"press_key refused: {key!r} not in allow-list")
        desc = f"key {key}"
        if not dry:
            if key in ("enter", "esc", "escape", "tab", "delete", "del"):
                lv("-Action", "key", "-Key", key)
            else:
                lv("-Action", "keys", "-Key", "{" + key.upper() + "}")
        return desc

    if action == "hotkey":
        combo = "+".join(str(k).lower() for k in args.get("keys", []))
        if combo not in ALLOWED_HOTKEYS:
            raise Refused(f"hotkey refused: {combo!r} not in allow-list")
        sendkeys = combo.replace("ctrl+", "^").replace("space", " ")
        desc = f"hotkey {combo}"
        if not dry:
            lv("-Action", "keys", "-Key", sendkeys)
        return desc

    if action == "wait":
        secs = min(float(args.get("seconds", 1.0)), 5.0)
        if not dry:
            time.sleep(secs)
        return f"wait {secs}s"

    if action == "take_screenshot":
        return "screenshot (will be taken automatically)"

    raise Refused(f"unsupported action {action!r}")


# --------------------------------------------------------------------------------------
# Gemini loop
# --------------------------------------------------------------------------------------

SYSTEM_HINTS = """You are operating the LabVIEW 2026 block-diagram editor on Windows, one window at a time.
The image you see is ONE LabVIEW window; coordinates you return are normalised 0..999 over that image.

Rules that come from hard experience on this machine:
- A single click right after the window gains focus often only activates it. Click empty canvas once, then act.
- Wiring is CLICK source terminal, then CLICK destination terminal. Never drag to wire.
- Start a wire 2-3 px OUTSIDE a constant's right border, never on the border pixels.
- If you see the CONTROLS palette you are on a FRONT PANEL, not the block diagram. Stop and say so.
- A palette category needs TWO clicks; a leaf item needs ONE, then a click on the canvas to drop.
- Menus are more reliable than keyboard shortcuts.
- NEVER save, never open the File menu, never close windows, never run the VI.
- If the task is done, or you are unsure, say so in text instead of guessing with a click.
Perform at most ONE or TWO actions per turn, then request a screenshot.
"""


def run(args: argparse.Namespace) -> int:
    if not args.dry_run and not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
        print("ERROR: set GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment first.", file=sys.stderr)
        return 2

    window_is_safe(args.window)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%d-%H%M%S")
    run_dir = LOG_DIR / stamp
    run_dir.mkdir()
    log_path = run_dir / "actions.jsonl"

    def log(rec: dict) -> None:
        rec["t"] = time.time()
        with log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    lv("-Action", "focus", "-Title", args.window)
    time.sleep(0.8)

    # --- dry-run without an API key: just prove the capture/denorm path works ---
    if args.dry_run and not (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")):
        rect = capture_window(args.window, run_dir / "step00.png")
        print(f"[dry-run, no API key] captured {args.window}: {rect}")
        for nx, ny in ((0, 0), (500, 500), (999, 999)):
            print(f"  norm({nx},{ny}) -> screen{denorm(rect, nx, ny)}")
        print("Capture + denormalisation path OK. Set GEMINI_API_KEY to run the model loop.")
        return 0

    from google import genai  # imported late so --dry-run works without the package

    client = genai.Client()
    model = args.model
    prev_id = None
    pending_result = None
    stats = {"steps": 0, "actions": 0, "refused": 0, "model_wait_s": 0.0, "escalations": 0}

    for step in range(1, args.max_steps + 1):
        shot = run_dir / f"step{step:02d}.png"
        rect = capture_window(args.window, shot)
        img_b64 = base64.b64encode(shot.read_bytes()).decode("ascii")

        if pending_result is None:
            inputs = [
                {"type": "text", "text": SYSTEM_HINTS + "\nTASK: " + args.task},
                {"type": "image", "data": img_b64, "mime_type": "image/png"},
            ]
        else:
            pending_result["result"].append({"type": "image", "data": img_b64, "mime_type": "image/png"})
            inputs = [pending_result]

        t0 = time.time()
        interaction = client.interactions.create(
            model=model,
            input=inputs,
            tools=[{"type": "computer_use", "environment": "desktop",
                    "enable_prompt_injection_detection": True}],
            **({"previous_interaction_id": prev_id} if prev_id else {}),
        )
        wait = time.time() - t0
        stats["model_wait_s"] += wait
        stats["steps"] += 1
        prev_id = getattr(interaction, "id", None)

        outputs = getattr(interaction, "outputs", None) or getattr(interaction, "output", None) or []
        calls = [o for o in outputs if _get(o, "type") == "function_call"]
        texts = [_get(o, "text") for o in outputs if _get(o, "type") == "text"]

        for t in texts:
            if t:
                print(f"[gemini] {t}")
                log({"step": step, "text": t})

        if not calls:
            print(f"Step {step}: no action proposed — model considers the task done or is unsure.")
            break

        call = calls[0]
        name = _get(call, "name")
        cargs = _get(call, "arguments") or {}
        call_id = _get(call, "id")
        intent = cargs.get("intent", "")
        safety = cargs.get("safety_decision") or {}

        if safety.get("decision") == "require_confirmation":
            print(f"STOP: Gemini flagged this action as needing human confirmation.\n"
                  f"  action={name} args={cargs}\n  reason={safety.get('explanation')}")
            log({"step": step, "stopped": "require_confirmation", "action": name, "args": cargs})
            return 3

        try:
            desc = execute(name, cargs, rect, args.dry_run)
            stats["actions"] += 1
            print(f"Step {step} ({wait:.1f}s): {name:13s} {desc}   -- {intent}")
            log({"step": step, "action": name, "args": cargs, "did": desc, "wait_s": wait})
            result_text = json.dumps({"ok": True, "window": args.window})
        except Refused as e:
            stats["refused"] += 1
            print(f"Step {step}: REFUSED {name}: {e}")
            log({"step": step, "refused": str(e), "action": name, "args": cargs})
            result_text = json.dumps({"ok": False, "refused": str(e)})
            if stats["refused"] >= 3:
                print("Too many refused actions; stopping.")
                break

        time.sleep(args.settle)
        pending_result = {"type": "function_result", "name": name, "call_id": call_id,
                          "result": [{"type": "text", "text": result_text}]}

        if args.escalate and step == args.escalate and model != ESCALATION_MODEL:
            model = ESCALATION_MODEL
            stats["escalations"] += 1
            print(f"-- escalating to {model} for the remaining steps --")

    print("\nSUMMARY:", json.dumps(stats, indent=2))
    print(f"log: {log_path}")
    return 0


def _get(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--window", required=True, help="exact LabVIEW window title to operate on")
    p.add_argument("--task", required=True, help="one bounded GUI sub-task, in plain language")
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"default {DEFAULT_MODEL}")
    p.add_argument("--max-steps", type=int, default=12)
    p.add_argument("--settle", type=float, default=1.2, help="seconds to wait after each action before re-capturing")
    p.add_argument("--escalate", type=int, default=0,
                   help=f"after this many steps switch to {ESCALATION_MODEL} (0 = never)")
    p.add_argument("--dry-run", action="store_true", help="print proposed actions; do not touch LabVIEW")
    return run(p.parse_args())


if __name__ == "__main__":
    sys.exit(main())
