"""ucbench stub cell (card chat-B3 dry run) - stands in for claude.exe; prints stream-json like `claude -p --verbose`.

  --fixture single : init (no Workflow), answer = CLAIM 1 (the task's first key ref) + CLAIM 2 (false)
  --fixture uc     : same answer, plus one top-level Workflow tool_use and 2 sub-agent rows in MATBENCH_LOG
  --fixture scorer : {"key": {"K1": [1], other: []}, "extra": {"2": "not_real"}}
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def emit(o):
    print(json.dumps(o, ensure_ascii=False), flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", required=True)
    a = ap.parse_args()
    prompt = sys.stdin.read()
    tools = ["Read", "Grep", "Glob", "Bash"] + (["Workflow"] if a.fixture == "uc" else [])
    emit({"type": "system", "subtype": "init", "tools": tools})
    if a.fixture == "scorer":
        sec = prompt.split("KEY -", 1)[1].split("THE ANSWER'S CLAIMS", 1)[0]
        ids = re.findall(r"^(K\d+):", sec, re.M)
        ans = json.dumps({"key": {k: ([1] if i == 0 else []) for i, k in enumerate(ids)}, "extra": {"2": "not_real"}})
    else:
        doc = json.load(open(os.path.join(HERE, "tasks.json"), encoding="utf-8"))
        t = next(t for t in doc["tasks"] if t["question"] in prompt)
        ans = "CLAIM 1: %s\nCLAIM 2: the moon is cheese | EVIDENCE: nowhere.md:1\nCLAIMS: 2" % t["key"][0]["ref"]
        if a.fixture == "uc":
            emit({"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Workflow", "input": {}}]}})
            log = os.environ.get("MATBENCH_LOG")
            if log:
                os.makedirs(os.path.dirname(log), exist_ok=True)
                with open(log, "a", encoding="utf-8") as f:
                    for aid in ("stub-a1", "stub-a2"):
                        f.write(json.dumps({"tool": "Read", "agent_id": aid, "decision": "ALLOW"}) + "\n")
    emit({"type": "result", "subtype": "success", "is_error": False, "result": ans, "total_cost_usd": 0.0,
          "num_turns": 1, "modelUsage": {"stub": {"inputTokens": 1, "outputTokens": 1}}})
    return 0


if __name__ == "__main__":
    sys.exit(main())
