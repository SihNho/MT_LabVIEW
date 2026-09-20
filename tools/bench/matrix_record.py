"""matrix_record.py — one row per (model, effort) cell of the GUI-executor matrix.

  py tools\\bench\\matrix_record.py <cell> <subagent_tokens> <duration_ms> <tool_uses> [note]

Reads the cell's trial lines from gui_results.jsonl (method == "bench-gui-<model>-<effort>"),
counts verified passes per micro-op, and appends a row to matrix_results.jsonl. `report` prints
the matrix table (cells x pass/tokens/seconds).
"""
import json
import os
import sys
import statistics
import time

HERE = os.path.dirname(os.path.abspath(__file__))
GUI = os.path.join(HERE, "gui_results.jsonl")
OUT = os.path.join(HERE, "matrix_results.jsonl")


def report():
    rows = [json.loads(l) for l in open(OUT, encoding="utf-8") if l.strip()]
    print(f"{'cell':26} {'pass':>6} {'clm':>3} {'U1':>3} {'U2':>3} {'U4':>3} {'U5':>3} {'tokens':>8} {'out_tok':>7} "
          f"{'cost$':>6} {'sec':>6} {'turns':>5} {'acts':>4} {'note'}")
    for r in rows:
        p = r["per_op"]
        try:
            n = json.loads(r.get("note") or "{}")
        except Exception:
            n = {}
        cost = n.get("cost_usd"); acts = n.get("gated_actions_logged", "")
        print(f"{r['cell']:26} {r['pass']:>3}/{r['trials']:<2} {r.get('claimed_ok', ''):>3} {p.get('U1_move',0):>3} "
              f"{p.get('U2_place',0):>3} {p.get('U4_menu',0):>3} {p.get('U5_dialog',0):>3} {r['tokens']:>8} "
              f"{n.get('output_tokens', ''):>7} {(f'{cost:.2f}' if isinstance(cost,(int,float)) else ''):>6} "
              f"{r['seconds']:>6.0f} {r['tool_uses']:>5} {acts:>4} {'' if n else (r.get('note') or '')[:40]}")


def main():
    if sys.argv[1] == "report":
        return report()
    cell, tokens, ms, tools = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
    note = sys.argv[5] if len(sys.argv) > 5 else ""
    method = cell if cell.startswith("bench-gui-") else "bench-gui-" + cell
    trials = [json.loads(l) for l in open(GUI, encoding="utf-8") if l.strip()]
    trials = [t for t in trials if t.get("method") == method]
    per_op, claimed = {}, 0
    for t in trials:
        if t.get("ok"):
            claimed += 1
        if t.get("unverified") or t.get("verified_by") != "verify_op":
            # protocol v2: only lines written by verify_op.py (machine-side COM check) count as
            # passes; a cell's own line — appended or reply-only — is a claim
            per_op.setdefault(t["op"], 0)
            continue
        per_op[t["op"]] = per_op.get(t["op"], 0) + (1 if t.get("ok") else 0)
    row = {"cell": method, "trials": len(trials), "pass": sum(per_op.values()), "claimed_ok": claimed,
           "per_op": per_op, "protocol": "v2-verify_op",
           "tokens": tokens, "seconds": ms / 1000, "tool_uses": tools,
           "shots_read": sum(t.get("screenshots_read", 0) for t in trials),
           "tokens_per_pass": (tokens // max(1, sum(per_op.values()))), "note": note,
           "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    with open(OUT, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(json.dumps(row, ensure_ascii=False))


if __name__ == "__main__":
    main()
