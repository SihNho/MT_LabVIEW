"""m3v1_verify.py — batch verification of tools/lvclick.py on GUIBENCH_v0.vi (spec §5).

  py tools/bench/m3v1_verify.py [--trials 3] [--ops move,place,menu,dialog]

Prediction contract (stated before running): move 3/3 (px_error 0), place 3/3 (px_error ~6),
menu 3/3 (ExecState 1->0), dialog 3/3 (Find opened then closed); zero screenshots; each verb
< 15 s. Results -> tools/bench/gui_results.jsonl with method "M3v1" (same schema as the bench).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g       # noqa: E402
import lvclick as c       # noqa: E402

TARGET = os.path.join(g.CLAUDEDEV, "GUIBENCH_v0.vi")
RESULTS = os.path.join(HERE, "gui_results.jsonl")
LOG = os.path.join(os.path.dirname(HERE), "gui_actions.log")


def log_lines():
    try:
        return sum(1 for _ in open(LOG, encoding="utf-8", errors="replace"))
    except FileNotFoundError:
        return 0


OPS = {
    "move":   ("U1_move",   lambda vp: c.move_node(vp, TARGET, 538, "Invoke", 100, 50)),
    "place":  ("U2_place",  lambda vp: c.place_from_palette(vp, TARGET, "Array/Index Array", "IndexArray", 1100, 600)),
    "menu":   ("U4_menu",   lambda vp: c.node_menu(vp, TARGET, 610, "Property", 0, "Change To Write")),
    "dialog": ("U5_dialog", lambda vp: c.dialog_button("Find", "Cancel", open_with="^f", bd=vp)),
}


def main():
    n = int(sys.argv[sys.argv.index("--trials") + 1]) if "--trials" in sys.argv else 3
    only = sys.argv[sys.argv.index("--ops") + 1].split(",") if "--ops" in sys.argv else list(OPS)
    g._lv = None
    # Open the panel only if it is not already open: OpenFrontPanel(activate) followed by an
    # lv_gui focus (Alt tap) hung the next COM Run twice today (calibrate, verify_op) — the
    # matrix ran hang-free once verify_op stopped calling open_panel on an open VI.
    if "GUIBENCH_v0.vi Front Panel" not in c.windows():
        g.open_panel(TARGET); time.sleep(1.5)
    vp = c.calibrate(TARGET)
    print("calibrated:", vp, flush=True)
    for key in only:
        opname, fn = OPS[key]
        for k in range(1, n + 1):
            g.revert(TARGET); time.sleep(0.8)
            c.focus_bd(vp)
            l0, t0 = log_lines(), time.time()
            try:
                res = fn(vp)
            except Exception as e:
                res = {"ok": False, "error": str(e)[:200]}
                c.lv("-Action", "key", "-Key", "esc")
            rec = {"method": "M3v1", "op": opname, "trial": k, "ok": bool(res.get("ok")),
                   "seconds": round(time.time() - t0, 1), "gated_actions": log_lines() - l0,
                   "screenshots_taken": 0, "screenshots_read": 0,
                   **{kk: v for kk, v in res.items() if kk != "ok"},
                   "at": time.strftime("%Y-%m-%d %H:%M:%S")}
            with open(RESULTS, "a", encoding="utf-8") as fh:
                fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            print(json.dumps(rec, ensure_ascii=False), flush=True)
    g.revert(TARGET)


if __name__ == "__main__":
    main()
