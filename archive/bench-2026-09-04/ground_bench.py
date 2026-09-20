"""ground_bench.py — OFFLINE grounding benchmark: which pointer finds LabVIEW targets best?

Runs WITHOUT LabVIEW. Inputs are screenshots already on disk plus a ground-truth table; each
grounder is asked "where is <target>?" and scored on pixel error, hit-within-tolerance, latency
and cost. This is the t4 comparison (user, 2026-09-04): UI-TARS (free/local) vs Claude vs GPT,
because a cheaper pointer that misses costs more in retries than a paid one that hits.

Dataset: tools/bench/ground_truth.jsonl, one line per target:
  {"id": "...", "image": "<png path>", "target": "<plain-language description>",
   "gt": [x, y], "tol": 4|10|15, "kind": "terminal|node|palette|menu|dialog",
   "gt_source": "com|log|manual"}
  gt for diagram objects comes from COM report() + the window offset (arithmetic, exact);
  for palette/menu/dialog items from clicks that verifiably succeeded (tools/gui_actions.log).

Grounders (adapters):
  uitars  -> tools/uitars_grounder.py (local Ollama; zoom two-pass)          cost: 0
  gpt     -> `codex exec -i <image> "<prompt>"` (ChatGPT login; no API key)  cost: subscription
  claude  -> answered by a Claude subagent reading the image; the harness records the answer
             passed in via --answer (the runner cannot spawn Claude itself)  cost: subagent_tokens

  py tools\\bench\\ground_bench.py run --grounder uitars|gpt [--ids a,b,c]
  py tools\\bench\\ground_bench.py record --grounder claude --id <id> --answer x,y --seconds N --tokens T
  py tools\\bench\\ground_bench.py report

Results append to tools/bench/ground_results.jsonl. Headline per grounder and per kind:
hit rate within tolerance, median px error, median seconds, cost per hit.
"""
import json
import os
import re
import subprocess
import sys
import time
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
GT = os.path.join(HERE, "ground_truth.jsonl")
RESULTS = os.path.join(HERE, "ground_results.jsonl")
UITARS = os.path.join(os.path.dirname(HERE), "uitars_grounder.py")

PROMPT = ("This is a screenshot of a LabVIEW window ({w}x{h} pixels). Locate: {target}. "
          "Reply with ONLY the pixel coordinate of its center as 'x,y' in image pixels.")


def load_gt(ids=None):
    rows = [json.loads(l) for l in open(GT, encoding="utf-8") if l.strip() and not l.startswith("#")]
    return [r for r in rows if not ids or r["id"] in ids]


def parse_xy(text):
    m = re.search(r"(-?\d+)\s*[, ]\s*(-?\d+)", text or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def image_size(path):
    from PIL import Image
    with Image.open(path) as im:
        return im.size


def ask_gpt(row):
    w, h = image_size(row["image"])
    t0 = time.time()
    # `-i` is variadic, so the prompt must NOT follow it as an argument - feed it via stdin
    # (codex exec reads the prompt from stdin when none is given; verified 2026-09-04).
    import shutil
    codex = shutil.which("codex") or shutil.which("codex.cmd") or "codex.cmd"   # npm shim on Windows
    out = subprocess.run([codex, "exec", "--skip-git-repo-check", "-i", row["image"]],
                         input=PROMPT.format(w=w, h=h, target=row["target"]),
                         capture_output=True, text=True, timeout=240, shell=codex.endswith(".cmd"))
    text = (out.stdout or "").strip().splitlines()
    ans = parse_xy(text[-1] if text else "")
    # codex exec prints "tokens used\n<N>" - keep it as the cost figure (subscription quota)
    m = re.search(r"tokens used\s*\n\s*([\d,]+)", out.stdout or "")
    tokens = int(m.group(1).replace(",", "")) if m else None
    return ans, time.time() - t0, {"raw_tail": text[-3:], "tokens": tokens}


def ask_uitars(row):
    # uitars_grounder.py works on a live WINDOW; for an offline image we call its model
    # directly. If it exposes no image entry point yet, this adapter reports 'unsupported' so
    # the gap is visible in the results instead of silently skipped.
    t0 = time.time()
    try:
        out = subprocess.run([sys.executable, UITARS, "--image", row["image"],
                              "--target", row["target"]],
                             capture_output=True, text=True, timeout=240)
        ans = parse_xy((out.stdout or "").strip().splitlines()[-1] if out.stdout else "")
        return ans, time.time() - t0, {"stderr_tail": (out.stderr or "")[-200:]}
    except Exception as e:
        return None, time.time() - t0, {"error": f"unsupported/failed: {e}"}


# "Would the click have landed?" — ground truth is a verified click POINT, but menu rows and
# dialog buttons are wide, so any x inside the item is a hit. Per-kind horizontal slack:
X_SLACK = {"menu": 80, "dialog": 30, "palette": 18}


def score(row, ans):
    if not ans:
        return None, False
    dx, dy = ans[0] - row["gt"][0], ans[1] - row["gt"][1]
    err = (dx * dx + dy * dy) ** 0.5
    xt = X_SLACK.get(row["kind"], row["tol"])
    hit = abs(dx) <= xt and abs(dy) <= row["tol"]
    return round(err, 1), hit


def append(rec):
    with open(RESULTS, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


def cmd_run(args):
    grounder = args[args.index("--grounder") + 1]
    ids = args[args.index("--ids") + 1].split(",") if "--ids" in args else None
    ask = {"gpt": ask_gpt, "uitars": ask_uitars, "uitars_warm": ask_uitars, "uitars_fast": ask_uitars}[grounder]
    for row in load_gt(ids):
        ans, secs, extra = ask(row)
        err, hit = score(row, ans)
        rec = {"grounder": grounder, "id": row["id"], "kind": row["kind"], "answer": ans,
               "gt": row["gt"], "tol": row["tol"], "px_error": err, "hit": hit,
               "seconds": round(secs, 1), "tokens": None, **extra,
               "at": time.strftime("%Y-%m-%d %H:%M:%S")}
        append(rec)
        print(json.dumps(rec, ensure_ascii=False))


def cmd_record(args):
    g = lambda k, d=None: args[args.index(k) + 1] if k in args else d
    row = load_gt([g("--id")])[0]
    ans = parse_xy(g("--answer", ""))
    err, hit = score(row, ans)
    rec = {"grounder": g("--grounder", "claude"), "id": row["id"], "kind": row["kind"],
           "answer": ans, "gt": row["gt"], "tol": row["tol"], "px_error": err, "hit": hit,
           "seconds": float(g("--seconds", 0)), "tokens": int(g("--tokens", 0)),
           "at": time.strftime("%Y-%m-%d %H:%M:%S")}
    append(rec)
    print(json.dumps(rec, ensure_ascii=False))


def cmd_report(args):
    rows = [json.loads(l) for l in open(RESULTS, encoding="utf-8") if l.strip()]
    # keep only the LATEST record per (grounder, id) and re-score with the current rule
    latest = {}
    for r in rows:
        latest[(r["grounder"], r["id"])] = r
    rows = list(latest.values())
    for r in rows:
        r["px_error"], r["hit"] = score(r, tuple(r["answer"]) if r.get("answer") else None)
    by = {}
    for r in rows:
        by.setdefault((r["grounder"], r["kind"]), []).append(r)
        by.setdefault((r["grounder"], "ALL"), []).append(r)
    print(f"{'grounder':8} {'kind':9} {'n':>3} {'hit%':>5} {'med px':>7} {'med s':>6} {'tokens/hit':>10}")
    for (gr, kind), rs in sorted(by.items()):
        hits = [r for r in rs if r["hit"]]
        errs = [r["px_error"] for r in rs if r["px_error"] is not None]
        toks = [r["tokens"] for r in rs if r.get("tokens")]
        print(f"{gr:8} {kind:9} {len(rs):3d} {100*len(hits)/len(rs):5.0f} "
              f"{statistics.median(errs) if errs else float('nan'):7.1f} "
              f"{statistics.median(r['seconds'] for r in rs):6.1f} "
              f"{(sum(toks)/max(1,len(hits))) if toks else 0:10.0f}")


if __name__ == "__main__":
    a = sys.argv[1:]
    {"run": cmd_run, "record": cmd_record, "report": cmd_report}[a[0]](a[1:])
