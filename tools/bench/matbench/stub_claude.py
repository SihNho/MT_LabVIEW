"""Stand-in for `claude.exe -p` in matbench dry mode (selftest_matbench.py). Runs with cwd = the replay worktree.

Fixture <name> = tools/bench/matbench/fixtures/<name>.json, a result/1 card whose id is replaced by --card-id. It is
written where a real cell writes it (tools/bench/cards/result_<id>.json) and printed inside a `--output-format json`
envelope. A fixture carrying "_sleep_s" sleeps that long first (the timeout case). Also logs one fake call to
.matbench/calls.jsonl so the dispatch counter is exercised.
"""
import argparse
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--card-id", required=True)
    ap.add_argument("--fixture", required=True)
    a = ap.parse_args()
    t0 = time.time()
    fx = json.load(open(os.path.join(HERE, "fixtures", a.fixture + ".json"), encoding="utf-8"))
    time.sleep(float(fx.pop("_sleep_s", 0)))
    fx["id"] = a.card_id
    os.makedirs(os.path.join("tools", "bench", "cards"), exist_ok=True)
    with open(os.path.join("tools", "bench", "cards", "result_%s.json" % a.card_id), "w", encoding="utf-8") as f:
        json.dump(fx, f, ensure_ascii=False, indent=1)
    os.makedirs(".matbench", exist_ok=True)
    with open(os.path.join(".matbench", "calls.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps({"tool": "Agent", "decision": "ALLOW", "cmd": "stub"}) + "\n")
    print(json.dumps({"type": "result", "subtype": "success", "is_error": False, "result": json.dumps(fx),
                      "duration_ms": int((time.time() - t0) * 1000), "total_cost_usd": 0.0, "num_turns": 1,
                      "modelUsage": {"stub": {}}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
