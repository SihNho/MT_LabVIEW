"""verify.py — parent-side, programmatic pass/fail for one benchmark run.

The benchmarked subagent only BUILDS and SAVES. Verification happens here, in the parent, so that
no run can grade itself and every run is judged identically (project rule: verify generated LabVIEW
by scripting, not by screenshots — a screenshot is evidence for the human, never the judge).

  py tools\\bench\\verify.py <RUN_ID> [--keep]

Checks, in order (first failure wins, and each failure has a distinct reason code):
  LOADS      the file exists and LabVIEW can load it
  EXECSTATE  ExecState == 1 (unbroken)
  RUNS       the VI runs to completion within a timeout
  SHAPE      `result` is 10 rows x 10 columns
  VALUES     result[r][c] == r*10 + c for all r, c
  WHILELOOP  the diagram actually contains a While loop (guards against a model that just
             writes a constant array and skips the loop entirely)

Deletes the scratch VI afterwards unless --keep (project rule: scratch targets are created and
deleted in the same operation, never accumulated as numbered leftovers).
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

RESULTS = os.path.join(HERE, "results.jsonl")


def verify(run_id):
    path = os.path.join(g.CLAUDEDEV, f"BENCH_{run_id}.vi")
    out = {"run_id": run_id, "path": path, "pass": False, "reason": None}

    if not os.path.exists(path):
        out["reason"] = "LOADS: file does not exist"
        return out
    out["bytes"] = os.path.getsize(path)

    try:
        g.open_panel(path)                      # never cold-load a possibly-broken VI headless
        vi = g.lv().GetVIReference(path, "", False, 0)
    except Exception as e:
        # A COM timeout / dead server here is the TOOLCHAIN failing, not the model - this
        # session saw menu-state COM wedges and a LabVIEW hang. Tag it INFRA so it is never
        # tallied against the cell; the harness re-runs INFRA cells after a LabVIEW restart.
        msg = str(e)
        infra = any(k in msg for k in ("did not return", "RPC", "not running", "-2147023170"))
        out["reason"] = ("INFRA: " if infra else "LOADS: ") + msg
        out["infra"] = infra
        return out

    state = int(vi.ExecState)
    out["exec_state"] = state
    if state != 1:
        out["reason"] = f"EXECSTATE: {state} (broken)"
        return out

    # WHILELOOP — structural honesty check, before running anything
    try:
        out["while_loops"] = g.count(path, "WhileLoop")
    except Exception as e:
        out["while_loops"] = None
        out["reason"] = f"WHILELOOP: could not traverse ({e})"
        return out
    if not out["while_loops"]:
        out["reason"] = "WHILELOOP: diagram contains no While loop"
        return out

    t0 = time.time()
    try:
        g._invoke(vi, "Run", hard_timeout_s=120.0)
    except Exception as e:
        msg = str(e)
        # A While loop that never stops (model error) and a wedged COM server (infra) both
        # surface as a timeout here; separate them by whether LabVIEW still answers.
        try:
            g.lv().Version
            alive = True
        except Exception:
            alive = False
        out["infra"] = not alive
        out["reason"] = (f"INFRA: {msg}" if not alive
                         else f"RUNS: {msg} (LabVIEW responsive - loop likely never stops)")
        return out
    out["run_seconds"] = round(time.time() - t0, 2)

    try:
        val = vi.GetControlValue("result")
    except Exception as e:
        out["reason"] = f"SHAPE: no indicator named 'result' ({e})"
        return out

    rows = list(val) if val is not None else []
    out["shape"] = [len(rows), len(list(rows[0])) if rows else 0]
    if out["shape"] != [10, 10]:
        out["reason"] = f"SHAPE: {out['shape']}, expected [10, 10]"
        return out

    bad = []
    for r, row in enumerate(rows):
        for c, v in enumerate(list(row)):
            if int(v) != r * 10 + c:
                bad.append([r, c, int(v), r * 10 + c])
    if bad:
        out["first_mismatches"] = bad[:5]
        out["reason"] = f"VALUES: {len(bad)} of 100 elements wrong"
        return out

    out["pass"] = True
    out["reason"] = "all checks passed"
    return out


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    run_id = sys.argv[1]
    keep = "--keep" in sys.argv

    result = verify(run_id)
    result["verified_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

    if not keep:
        path = result["path"]
        try:
            g.close_panel(path)
        except Exception:
            pass
        try:
            if os.path.exists(path):
                os.remove(path)
                result["cleaned_up"] = True
        except Exception as e:
            result["cleaned_up"] = f"FAILED: {e}"

    with open(RESULTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(result, ensure_ascii=False) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
