"""record_claude.py — score a Claude subagent's grounding answers, raw AND size-calibrated.

  py tools\\bench\\record_claude.py <grounder-name> <answers.jsonl> <seconds> <tokens>

Claude reads large screenshots in a downscaled coordinate space (Anthropic's vision resizes
images over ~1.15 MP), so a naive reading of its "x,y" is off by a constant factor per image
size. A real executor would calibrate that once (as uitars_grounder.py does for Ollama). We
therefore record two variants:
  <name>      raw answers, scored as-is
  <name>_cal  answers multiplied by a per-image-size scale fitted by least squares over all
              targets of that size (one scalar per size class; the fit uses the ground truth,
              so it is an UPPER bound on what a one-time calibration would achieve)
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from ground_bench import load_gt, score, append, image_size  # noqa: E402


def main():
    name, ans_path, seconds, tokens = sys.argv[1], sys.argv[2], float(sys.argv[3]), int(sys.argv[4])
    answers = {}
    for line in open(ans_path, encoding="utf-8"):
        line = line.strip()
        if line.startswith("{"):
            d = json.loads(line)
            answers[d["id"]] = (d.get("x"), d.get("y"))
    rows = load_gt()
    n = len(rows)
    per_query = {"seconds": round(seconds / n, 1), "tokens": tokens // n}

    # per-size calibration scale: minimise sum |s*a - gt|^2  ->  s = sum(a.gt)/sum(a.a)
    by_size = {}
    for r in rows:
        a = answers.get(r["id"])
        if not a or a[0] is None:
            continue
        sz = image_size(r["image"])
        num, den = by_size.get(sz, (0.0, 0.0))
        num += a[0] * r["gt"][0] + a[1] * r["gt"][1]
        den += a[0] * a[0] + a[1] * a[1]
        by_size[sz] = (num, den)
    scale = {sz: (num / den if den else 1.0) for sz, (num, den) in by_size.items()}
    print("calibration scale per image size:", {f"{w}x{h}": round(s, 3) for (w, h), s in scale.items()})

    for r in rows:
        a = answers.get(r["id"])
        sz = image_size(r["image"])
        for variant, ans in ((name, a), (name + "_cal", None if not a or a[0] is None else
                                         (round(a[0] * scale[sz]), round(a[1] * scale[sz])))):
            ans = None if not ans or ans[0] is None else (int(ans[0]), int(ans[1]))
            err, hit = score(r, ans)
            append({"grounder": variant, "id": r["id"], "kind": r["kind"], "answer": ans,
                    "gt": r["gt"], "tol": r["tol"], "px_error": err, "hit": hit,
                    **per_query, "at": time.strftime("%Y-%m-%d %H:%M:%S")})
    print(f"recorded {n} targets x 2 variants for {name}")


if __name__ == "__main__":
    main()
