"""verify_op.py — machine-side reset + verification for the GUI-executor benchmark cells.

The cell does the GUI act; THIS script decides pass/fail from COM/window state and writes the trial
line. A cell cannot mark its own trial as passed (protocol v2, 2026-09-05: under v1 the haiku cells
replied with self-written lines, some of them fabricated).

  py tools/bench/verify_op.py revert  <method> <op> <trial>       # before each trial: revert VI,
                                                                  # focus BD, snapshot baseline, start clock
  py tools/bench/verify_op.py u5open  <method> <op> <trial>       # U5 only: between Ctrl+F and Cancel —
                                                                  # records whether a Find window is open now
  py tools/bench/verify_op.py verify  <method> <op> <trial> [--shots N] [--gated N] [--note "..."]
                                                                  # after the act: COM check -> appends line

Ops: U1_move U2_place U4_menu U5_dialog (rules identical to gui_bench.py / EXECUTOR_TASK.md).
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
STATE = os.path.join(HERE, ".verify_state.json")
BD_TITLE = "GUIBENCH_v0.vi Block Diagram"
INVOKE_UID, INVOKE_TL = 538, (1044, 350)
PLACE_TARGET_D = (1100, 600)


def lv(*args):
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& .\\tools\\lv_gui.ps1 " + " ".join(a if a.replace("-", "").replace(".", "").isalnum()
                                                else f'"{a}"' for a in args)]
    r = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, timeout=60)
    return r.stdout.strip()


def load_state():
    try:
        return json.load(open(STATE, encoding="utf-8"))
    except Exception:
        return {}


def save_state(st):
    json.dump(st, open(STATE, "w", encoding="utf-8"))


g._run.__defaults__ = (6.0, 45.0)      # fail fast: a hung Run costs 45 s here, not 180 s


def com_retry(label, fn):
    """Three COM Runs hung on 2026-09-05 right after OpenFrontPanel(activate=True) with no delay.
    Retry once after Esc + a canvas click (both known to unstick LabVIEW's UI loop)."""
    try:
        return fn()
    except RuntimeError as e:
        sys.stderr.write(f"[verify_op] {label}: {str(e)[:80]} -> Esc+click, retry\n")
        lv("-Action", "key", "-Key", "esc")
        lv("-Action", "click", "-X", "1311", "-Y", "791", "-Exception", "Approved",
           "-Evidence", "verify_op COM retry click")
        time.sleep(1.0)
        g._lv = None
        return fn()


def do_revert(method, op, trial):
    g._lv = None
    # Open the panel only if it is not already open: bench_prep opens it once per cell, and
    # OpenFrontPanel(activate) on an already-open VI re-activates the FRONT PANEL window (which
    # then covers the diagram) — and is the one step every hung verify_op run had just done.
    if "GUIBENCH_v0.vi Front Panel" not in lv("-Action", "windows"):
        g.open_panel(TARGET)
        time.sleep(1.5)
    com_retry("revert", lambda: g.revert(TARGET))
    time.sleep(0.6)
    lv("-Action", "focus", "-Title", BD_TITLE)
    time.sleep(0.3)
    # One click on empty canvas after focus, exactly as gui_bench.prep does: every COM Run that
    # followed focus WITHOUT a click from a non-foreground state hung (3x, 2026-09-05), while
    # focus+click never did. The click also absorbs the swallowed first mouse-down.
    lv("-Action", "click", "-X", "1311", "-Y", "791", "-Exception", "Approved",
       "-Evidence", "verify_op revert: canvas click after focus (COM-hang guard)")
    time.sleep(0.3)
    st = {"method": method, "op": op, "trial": trial, "t0": time.time(),
          "index_uids": sorted(com_retry("uids", lambda: g.uids(TARGET, "IndexArray"))),
          "exec0": com_retry("exec_state", lambda: g.exec_state(TARGET)),
          "invoke_pos": [o for o in com_retry("report Invoke", lambda: g.report(TARGET, "Invoke"))
                         if o["uid"] == INVOKE_UID][0]["pos"],
          "u5_opened": None}
    save_state(st)
    print(json.dumps({"reverted": True, "op": op, "trial": trial, "exec_state": st["exec0"],
                      "bd_in_front": lv("-Action", "windows").splitlines()[:1]}))


def do_u5open(method, op, trial):
    st = load_state()
    wins = lv("-Action", "windows")
    st["u5_opened"] = any(w.strip().startswith("Find") for w in wins.splitlines())
    save_state(st)
    print(json.dumps({"find_open_now": st["u5_opened"]}))


def do_verify(method, op, trial, shots, gated, note):
    st = load_state()
    if st.get("method") != method or st.get("op") != op or int(st.get("trial", -1)) != trial:
        info = {"ok": False, "reason": f"no matching revert for {method} {op} {trial} (state={st.get('op')},{st.get('trial')})"}
        ok = False
    else:
        g._lv = None
        if op == "U1_move":
            pos = [o for o in g.report(TARGET, "Invoke") if o["uid"] == INVOKE_UID][0]["pos"]
            dx, dy = pos[0] - st["invoke_pos"][0], pos[1] - st["invoke_pos"][1]
            err = ((dx - 100) ** 2 + (dy - 50) ** 2) ** 0.5
            ok, info = err <= 6, {"delta": [dx, dy], "px_error": round(err, 1)}
        elif op == "U2_place":
            now = [o for o in g.report(TARGET, "IndexArray") if o["uid"] not in st["index_uids"]]
            if len(now) != 1:
                ok, info = False, {"new_nodes": len(now)}
            else:
                pos = now[0]["pos"]
                err = ((pos[0] + 8 - PLACE_TARGET_D[0]) ** 2 + (pos[1] + 8 - PLACE_TARGET_D[1]) ** 2) ** 0.5
                ok, info = err <= 12, {"pos": pos, "px_error": round(err, 1)}
        elif op == "U4_menu":
            es = g.exec_state(TARGET)
            ok, info = (st["exec0"] == 1 and es == 0), {"exec_before": st["exec0"], "exec_after": es}
        elif op == "U5_dialog":
            wins = lv("-Action", "windows")
            closed = not any(w.strip().startswith("Find") for w in wins.splitlines())
            ok = bool(st.get("u5_opened")) and closed
            info = {"opened": st.get("u5_opened"), "closed": closed}
            if not closed:
                lv("-Action", "key", "-Key", "esc")
        else:
            ok, info = False, {"reason": f"unknown op {op}"}
    rec = {"method": method, "op": op, "trial": trial, "ok": bool(ok),
           "seconds": round(time.time() - float(st.get("t0", time.time())), 1),
           "gated_actions": gated, "screenshots_taken": shots, "screenshots_read": shots,
           **info, "note": note, "verified_by": "verify_op", "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(RESULTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    st["op"] = None; save_state(st)          # one verify per revert
    print(json.dumps(rec, ensure_ascii=False))


def main():
    a = sys.argv[1:]
    if len(a) < 4:
        print(__doc__); return 2
    cmd, method, op, trial = a[0], a[1], a[2], int(a[3])
    shots = int(a[a.index("--shots") + 1]) if "--shots" in a else 0
    gated = int(a[a.index("--gated") + 1]) if "--gated" in a else 0
    note = a[a.index("--note") + 1] if "--note" in a else ""
    if cmd == "revert":
        do_revert(method, op, trial)
    elif cmd == "u5open":
        do_u5open(method, op, trial)
    elif cmd == "verify":
        do_verify(method, op, trial, shots, gated, note)
    else:
        print(__doc__); return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
