# ---
# labview: none
# hardware: none
# ---
"""Codex PreToolUse hook for the FIXED GPT bench cell (card chat-X10; user 2026-10-11 "진행해").

The cell folder ..\\V6_bench\\gpt_cell is re-checked-out per matbench task, but its .codex/hooks.json stays byte-identical
and points HERE, in the main tree, so the user trusts it ONCE with /hooks and a GPT inside the cell cannot edit the
guard (cell_guard refuses writes outside the cell and %TEMP%). Two layers, both must allow:
  1. tools/bench/matbench/cell_guard.py --codex  - the replay card's rules, identical to the Claude cells
  2. tools/hooks/adapt_codex.py                  - the project's common guard (guardcore)
Deny = the Codex deny JSON on stdout with exit 0 (exit 2 fails OPEN on Windows); any error here is a deny (fail closed).
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
CELL = os.environ.get("MATBENCH_GPT_CELL") or os.path.join(os.path.dirname(MAIN), "V6_bench", "gpt_cell")


def deny(why):
    sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                                        "permissionDecisionReason": why}}))
    return 0


def layer(cmd, raw, env):
    p = subprocess.run(cmd, input=raw, capture_output=True, text=True, encoding="utf-8", env=env, timeout=180)
    return (p.stdout or "").strip(), p.returncode


def main():
    raw = sys.stdin.read()
    try:
        env = dict(os.environ, MATBENCH_WT=CELL, MATBENCH_LOG=os.path.join(CELL, ".matbench", "calls.jsonl"))
        out, rc = layer([sys.executable, os.path.join(HERE, "cell_guard.py"), "--codex", MAIN], raw, env)
        if rc != 0 or '"deny"' in out:
            return deny(json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"] if out else
                        "matbench cell_guard exit %d (fail closed)" % rc)
        out, rc = layer([sys.executable, os.path.join(MAIN, "tools", "hooks", "adapt_codex.py")], raw, dict(os.environ))
        if rc != 0:
            return deny("adapt_codex exit %d (fail closed)" % rc)
        if out:
            sys.stdout.write(out)
        return 0
    except Exception as e:      # noqa: BLE001
        return deny("codex_cell_hook error %s: %s (fail closed)" % (type(e).__name__, e))


if __name__ == "__main__":
    sys.exit(main())
