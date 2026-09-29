"""Stand-in for `claude.exe -p` in decbench dry mode (card chat-B1). Reads the prompt on stdin, prints a
`--output-format json` envelope. Fixtures: hit (an answer built from the case's must_hit item texts), miss, ratelimit
(an is_error rate-limit envelope on DECBENCH_ATTEMPT 1, a hit answer afterwards - exercises the re-queue), scorer
(a blind-scorer JSON giving every label 1 on M*, 0 on F*, 0.5 on B*). Logs one fake call to MATBENCH_LOG.
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def env(result, is_error=False):
    return {"type": "result", "subtype": "error" if is_error else "success", "is_error": is_error, "result": result,
            "duration_ms": 10, "total_cost_usd": 0.0, "num_turns": 1, "modelUsage": {"stub": {}}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    a = ap.parse_args()
    prompt = sys.stdin.buffer.read().decode("utf-8", "replace")
    lg = os.environ.get("MATBENCH_LOG")
    if lg:
        with open(lg, "a", encoding="utf-8") as f:
            f.write(json.dumps({"tool": "Read", "decision": "ALLOW", "cmd": "stub"}) + "\n")
    time.sleep(0.2)
    fx = a.fixture
    if fx == "scorer":
        labels = sorted(set(re.findall(r"=== ANSWER ([A-Z]) ===", prompt)))
        ids = re.findall(r"^([MFB]\d+) \[", prompt, re.M)
        out = {lab: {i: (1 if i[0] == "M" else 0 if i[0] == "F" else 0.5) for i in ids} for lab in labels}
        print(json.dumps(env(json.dumps(out))))
        return 0
    if fx == "ratelimit" and os.environ.get("DECBENCH_ATTEMPT") == "1":
        print(json.dumps(env("API Error: 429 rate limit exceeded (stub)", is_error=True)))
        return 1
    if fx == "miss":
        print(json.dumps(env("I cannot determine this.\nVERDICT: keep NEXT\nDEFECT: none - stub")))
        return 0
    cases = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))["cases"]
    wt = os.path.basename(os.getcwd())
    c = next((x for x in cases if x["id"] == wt), cases[0])
    txt = "\n".join(it["text"] for it in c["rubric"]["must_hit"])
    print(json.dumps(env(txt + "\nVERDICT: change NEXT\nDEFECT: major - stub")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
