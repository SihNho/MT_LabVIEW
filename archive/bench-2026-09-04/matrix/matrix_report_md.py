"""matrix_report_md.py — render the GUI-executor matrix (protocol v2 rows) as Markdown.

  py tools/bench/matrix_report_md.py            # prints the tables
  py tools/bench/matrix_report_md.py --json     # also dumps a compact JSON summary

Rows come from matrix_results.jsonl (one per attempt). Only protocol "v2-verify_op" rows without an
`invalid` tag enter the main table; invalid/v1 rows are listed separately as non-results. The pass
denominator is always 12 (4 ops x 3 trials) — a cell that stopped early shows e.g. 3/12.
"""
import io
import json
import os
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")   # cp949 console

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "matrix_results.jsonl")
MODELS = ["haiku", "sonnet", "opus", "fable"]
EFFORTS = ["low", "medium", "high", "xhigh", "max"]
EXPECTED = 12


def load():
    return [json.loads(l) for l in open(OUT, encoding="utf-8") if l.strip()]


def note(r):
    try:
        return json.loads(r.get("note") or "{}")
    except Exception:
        return {}


def cell_key(r):
    parts = r["cell"].replace("bench-gui-", "").split("-")
    return parts[0], parts[1]


def main():
    rows = load()
    valid = [r for r in rows if r.get("protocol") == "v2-verify_op" and not r.get("invalid")]
    invalid = [r for r in rows if r not in valid]
    by = defaultdict(list)
    for r in valid:
        by[cell_key(r)].append(r)

    print("## Model x effort matrix (protocol v2, verified by verify_op.py; n = attempts per cell)\n")
    print("| model | effort | pass /12 | U1 | U2 | U4 | U5 | min | cost $ | turns | out tok | GUI acts | n |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    summary = []
    for m in MODELS:
        for e in EFFORTS:
            rs = by.get((m, e), [])
            if not rs:
                print(f"| {m} | {e} | - | | | | | | | | | | 0 |")
                continue
            n = len(rs)
            avg = lambda f: sum(f(r) for r in rs) / n
            p = avg(lambda r: r["pass"])
            ops = [avg(lambda r, k=k: r["per_op"].get(k, 0)) for k in ("U1_move", "U2_place", "U4_menu", "U5_dialog")]
            mins = avg(lambda r: r["seconds"]) / 60
            cost = avg(lambda r: note(r).get("cost_usd") or 0)
            turns = avg(lambda r: r["tool_uses"])
            out_tok = avg(lambda r: note(r).get("output_tokens") or 0)
            acts = avg(lambda r: note(r).get("gated_actions_logged") or 0)
            fmt = lambda x: f"{x:.0f}" if n == 1 else f"{x:.1f}"
            print(f"| {m} | {e} | {fmt(p)}/{EXPECTED} | {fmt(ops[0])} | {fmt(ops[1])} | {fmt(ops[2])} | {fmt(ops[3])} | "
                  f"{mins:.1f} | {cost:.2f} | {fmt(turns)} | {out_tok:.0f} | {fmt(acts)} | {n} |")
            summary.append({"model": m, "effort": e, "pass": p, "minutes": mins, "cost_usd": cost, "turns": turns, "n": n})
    print("\nPass = trial verified over COM by verify_op.py (position delta / new node / ExecState / window list); "
          "the cell cannot mark its own trial. cost $ = list-price API cost reported by `claude -p`; "
          "min = wall time of the cell run; turns = num_turns; GUI acts = gated lv_gui actions logged in the run window.\n")
    if invalid:
        print("## Non-results (excluded from the table)\n")
        print("| cell | protocol | why |")
        print("|---|---|---|")
        for r in invalid:
            why = r.get("invalid") or r.get("note") or ""
            if why.startswith("{"):
                why = "protocol " + str(r.get("protocol"))
            print(f"| {r['cell']} | {r.get('protocol', '')} | {why[:110]} |")
    if "--json" in sys.argv:
        print("\n```json\n" + json.dumps(summary, indent=1) + "\n```")


if __name__ == "__main__":
    main()
