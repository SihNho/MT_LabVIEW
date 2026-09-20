"""make_agents.py — emit one .claude/agents/bench-<model>-<effort>.md per matrix cell.

Per-subagent `model:` and `effort:` are settable in agent-definition frontmatter (verified against
the Claude Code docs 2026-09-03). Extended thinking is NOT per-subagent — it is inherited from this
session, so it is a controlled constant across the whole matrix, not a variable.

  py tools\\bench\\make_agents.py frontier    # 6 cells, ~1 h of LabVIEW
  py tools\\bench\\make_agents.py grid        # 20 cells, ~3 h of LabVIEW
  py tools\\bench\\make_agents.py clean       # remove generated definitions

`ultracode` is a MODE, not an effort level (the real ladder is low/medium/high/xhigh/max), so it
cannot be expressed in `effort:` frontmatter. Cells naming it are emitted at `xhigh` — the
reasoning level it runs at — and flagged in the file so the results table does not silently
claim to have measured ultracode itself.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
AGENTS = os.path.join(PROJECT, ".claude", "agents")
TASK = os.path.join(HERE, "TASK.md")
GUI_TASK = os.path.join(HERE, "EXECUTOR_TASK.md")

MODELS = ["haiku", "sonnet", "opus", "fable"]
EFFORTS = ["low", "medium", "high", "xhigh", "max"]

# The informative diagonal: find the cheapest cell that passes, not the whole surface.
# ADAPTIVE RULE (2026-09-03 review): after these six, generate and run ONE more cell that is one
# effort step cheaper than the cheapest passing cell (e.g. sonnet@medium passed -> run
# sonnet@low). Repeat until the cheaper neighbour fails. That neighbour, not this fixed list,
# is what pins the frontier.
FRONTIER = [
    ("haiku", "medium"), ("haiku", "max"),
    ("sonnet", "medium"), ("sonnet", "max"),
    ("opus", "low"), ("fable", "low"),
]

TEMPLATE = """---
name: bench-{model}-{effort}
description: Benchmark cell — build the 100-iteration / 10x10-array VI. Model {model}, effort {effort}. Dispatched only by the benchmark harness; never pick this agent for real work.
model: {model}
effort: {effort}
---

You are one cell of a controlled benchmark. Another cell is running the identical task on a
different model and effort level, so **do not improvise the task, negotiate its scope, or ask
questions** — a deviation makes the comparison meaningless. Work the task as written, and stop
when it is done or you are genuinely stuck.

Your run id is `{run_id}`; substitute it wherever the task says `{{{{RUN_ID}}}}`.

The task follows verbatim.

---

{task}
"""


def write_cells(cells, gui=False):
    os.makedirs(AGENTS, exist_ok=True)
    if gui:      # GUI-executor matrix: same EXECUTOR_TASK.md for every cell, only model/effort vary
        task = open(GUI_TASK, encoding="utf-8").read().strip()
        prefix = "bench-gui"
    else:
        task = open(TASK, encoding="utf-8").read().split("---\n", 2)[-1].strip()
        prefix = "bench"
    written = []
    for model, effort in cells:
        run_id = f"{model}_{effort}"
        body = TEMPLATE.format(model=model, effort=effort, run_id=run_id, task=task)
        body = body.replace("name: bench-", f"name: {prefix}-", 1)
        path = os.path.join(AGENTS, f"{prefix}-{model}-{effort}.md")
        open(path, "w", encoding="utf-8").write(body)
        written.append(os.path.basename(path))
    return written


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "frontier"
    if mode == "clean":
        removed = []
        if os.path.isdir(AGENTS):
            for f in sorted(os.listdir(AGENTS)):
                if (f.startswith("bench-")) and f.endswith(".md"):
                    os.remove(os.path.join(AGENTS, f))
                    removed.append(f)
        print(f"removed {len(removed)} definitions")
        return
    gui = "--gui" in sys.argv
    cells = FRONTIER if mode == "frontier" else [(m, e) for m in MODELS for e in EFFORTS]
    written = write_cells(cells, gui=gui)
    print(f"{mode}: wrote {len(written)} agent definitions to .claude/agents/")
    for w in written:
        print("  " + w)
    print("\nRun order is SERIAL - LabVIEW is a single shared instance. After each cell:")
    print("  py tools\\\\bench\\\\verify.py <model>_<effort>")
    print("and record subagent_tokens / duration_ms / tool_uses from the completion notification.")


if __name__ == "__main__":
    main()
