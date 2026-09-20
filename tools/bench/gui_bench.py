"""gui_bench.py — LIVE click benchmark, method M3 (coordinates from data, zero screenshots).

Target: claudeDev\\GUIBENCH_v0.vi (copy of OpFP_v0), block diagram window at a fixed rect.
Calibration (one screenshot read once, 2026-09-04): screen = diagram + (11, 41) for this window
rect (0,4)-(1400,904) at scroll origin. Everything else below is arithmetic + COM verification.

  py tools\\bench\\gui_bench.py m3 [--trials 3]

Micro-ops:
  U1 move   drag the Invoke node by (+100,+50)      verify: report() position delta
  U2 place  palette -> Index Array at diagram (1100,600)   verify: new IndexArray uid + position
  U4 menu   right-click PN 'Position' row -> Change To Write  verify: ExecState 1 -> 0
Reset between trials: gscript.revert(target) (reload from disk; window stays).
Results -> tools/bench/gui_results.jsonl: seconds, gated actions, screenshots (0), success, px error.
"""
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

PROJECT = os.path.dirname(os.path.dirname(HERE))
TARGET = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
RESULTS = os.path.join(HERE, "gui_results.jsonl")
LOG = os.path.join(PROJECT, "tools", "gui_actions.log")
OFF = (11, 41)                       # diagram -> screen, calibrated once
EV = "live click bench M3 (user: 실행 2026-09-04)"
BD_TITLE = "GUIBENCH_v0.vi Block Diagram"

# node geometry from report() (top-left) + icon sizes read at calibration
INVOKE_UID, INVOKE_TL, INVOKE_SZ = 538, (1044, 350), (92, 35)
PN_UID, PN_TL = 610, (1213, 350)
PN_ROW_CENTER_D = (PN_TL[0] + 27, PN_TL[1] + 22)        # the 'Position' item row
MENU_CHANGE_TO_WRITE = (68, 187)                        # offset from the right-click point (measured)
PLACE_RCLICK = (1150, 500)                              # screen; palette geometry verified for this spot
PAL_ARRAY, PAL_INDEX_ARRAY = (1310, 235), (1519, 300)
PLACE_TARGET_D = (1100, 600)


def lv(*args):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& .\\tools\\lv_gui.ps1 " + " ".join(a if a.replace("-", "").replace(".", "").isalnum()
                                                else f'"{a}"' for a in args)]
    r = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, timeout=60)
    if r.returncode != 0:
        raise RuntimeError(f"lv_gui {args}: {r.stdout.strip()} {r.stderr.strip()[:200]}")
    return r.stdout.strip()


def gated(action, **kw):
    args = ["-Action", action]
    for k, v in kw.items():
        args += [f"-{k}", str(v)]
    args += ["-Exception", "Approved", "-Evidence", EV]
    return lv(*args)


def s(d):                      # diagram -> screen
    return d[0] + OFF[0], d[1] + OFF[1]


def log_lines():
    try:
        return sum(1 for _ in open(LOG, encoding="utf-8", errors="replace"))
    except FileNotFoundError:
        return 0


def prep():
    lv("-Action", "focus", "-Title", BD_TITLE)      # focus now taps Esc itself
    time.sleep(0.3)
    # The first mouse-down after (re)activation is sometimes swallowed by window activation
    # (U1 trial 1 after the header fix: delta (0,0)). A harmless click on empty canvas absorbs it.
    gated("click", X=OFF[0] + 1300, Y=OFF[1] + 750)
    time.sleep(0.2)


def op_move():
    # Grab the node by its HEADER row ("Term"), not its centre: the centre of an Invoke Node is
    # the method field, and a mouse-down there opens the method chooser instead of dragging
    # (M3 U1 trials 1-3, 2026-09-04: delta (0,0)/(13,0)).
    c = s((INVOKE_TL[0] + INVOKE_SZ[0] // 2, INVOKE_TL[1] + 8))
    gated("drag", X=c[0], Y=c[1], X2=c[0] + 100, Y2=c[1] + 50)
    time.sleep(0.5)
    pos = [o for o in g.report(TARGET, "Invoke") if o["uid"] == INVOKE_UID][0]["pos"]
    dx, dy = pos[0] - INVOKE_TL[0], pos[1] - INVOKE_TL[1]
    err = ((dx - 100) ** 2 + (dy - 50) ** 2) ** 0.5
    return err <= 6, {"delta": [dx, dy], "px_error": round(err, 1)}


def op_place():
    before = g.uids(TARGET, "IndexArray")
    gated("rclick", X=PLACE_RCLICK[0], Y=PLACE_RCLICK[1]); time.sleep(0.9)
    gated("click", X=PAL_ARRAY[0], Y=PAL_ARRAY[1]); time.sleep(0.8)
    gated("click", X=PAL_ARRAY[0], Y=PAL_ARRAY[1]); time.sleep(1.0)
    gated("click", X=PAL_INDEX_ARRAY[0], Y=PAL_INDEX_ARRAY[1]); time.sleep(0.7)
    t = s(PLACE_TARGET_D)
    gated("click", X=t[0], Y=t[1]); time.sleep(0.7)
    lv("-Action", "key", "-Key", "esc")
    new = g.new_since(TARGET, "IndexArray", before)
    if len(new) != 1:
        return False, {"new": new}
    pos = new[0]["pos"]
    # palette drops the icon centred on the click; the reporter gives the top-left (~16x16 icon)
    err = ((pos[0] + 8 - PLACE_TARGET_D[0]) ** 2 + (pos[1] + 8 - PLACE_TARGET_D[1]) ** 2) ** 0.5
    return err <= 12, {"pos": pos, "px_error": round(err, 1)}


def op_menu():
    es0 = g.exec_state(TARGET)
    p = s(PN_ROW_CENTER_D)
    gated("rclick", X=p[0], Y=p[1]); time.sleep(1.0)
    gated("click", X=p[0] + MENU_CHANGE_TO_WRITE[0], Y=p[1] + MENU_CHANGE_TO_WRITE[1]); time.sleep(0.8)
    es1 = g.exec_state(TARGET)
    return (es0 == 1 and es1 == 0), {"exec_before": es0, "exec_after": es1}


def op_dialog():
    """Ctrl+F opens Find; its Cancel button sits at a fixed screen position for this window
    layout (measured 2026-09-01/04: Cancel at (958,716) when the dialog opens centred). PASS =
    'Find' window listed after the keystroke and gone after the click."""
    lv("-Action", "focus", "-Title", BD_TITLE); time.sleep(0.3)
    gated("keys", Key="^f", WaitMs=1500)
    wins1 = lv("-Action", "windows")
    opened = "Find" in wins1
    if opened:
        gated("click", X=958, Y=716); time.sleep(0.8)
    wins2 = lv("-Action", "windows")
    closed = "Find" not in wins2
    if not closed:
        lv("-Action", "key", "-Key", "esc")
    return opened and closed, {"opened": opened, "closed": closed}


OPS = {"U1_move": op_move, "U2_place": op_place, "U4_menu": op_menu, "U5_dialog": op_dialog}


def trial(name, fn, k):
    g.revert(TARGET); time.sleep(0.8)
    prep()
    l0, t0 = log_lines(), time.time()
    ok, info = fn()
    rec = {"method": "M3", "op": name, "trial": k, "ok": ok, "seconds": round(time.time() - t0, 1),
           "gated_actions": log_lines() - l0, "screenshots_taken": 0, "screenshots_read": 0,
           **info, "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(RESULTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps(rec, ensure_ascii=False), flush=True)
    return rec


def main():
    n = int(sys.argv[sys.argv.index("--trials") + 1]) if "--trials" in sys.argv else 3
    only = sys.argv[sys.argv.index("--ops") + 1].split(",") if "--ops" in sys.argv else None
    g._lv = None
    g.open_panel(TARGET)
    for name, fn in OPS.items():
        if only and name not in only:
            continue
        for k in range(1, n + 1):
            try:
                trial(name, fn, k)
            except Exception as e:
                print(json.dumps({"method": "M3", "op": name, "trial": k, "ok": False,
                                  "error": str(e)[:200]}), flush=True)
                lv("-Action", "key", "-Key", "esc")
    g.revert(TARGET)


if __name__ == "__main__":
    main()
