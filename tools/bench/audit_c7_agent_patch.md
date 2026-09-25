---
type: note
status: current
date: 2026-09-26
tags: [card-90-2, agents, material]
---
# Replacement text for `.claude/agents/material*.md` (card 90-2, retrospective-cycle89 finding 1(b))

The material session's Edit on these three files was refused by the permission layer (harness config), so the
change is left here for whoever holds that permission. Replace `material.md` lines 53–57 and the identical block
at lines 48–52 of `material-fable-low.md` / `material-fable-medium.md` (the block starting `` `MATERIAL=1 py
tools/bgrun.py ...`` and ending `use the Edit/Write tools.`) with:

```
  `py tools/bgrun.py --material --max-min N --log tools/bench/<name>.log -- py -u <script>` (Bash or
  PowerShell, same form). **The `--material` flag is mandatory** — `tools/hooks/guard_bash.py` refuses any
  `tools/recipes/*.py` or `tools/bench/*.py` run without it, because a judgement session must delegate such runs
  to you rather than run them itself (CLAUDE.md §3). The older env-prefix form (`MATERIAL=1 py ...` /
  `$env:MATERIAL='1'; py ...`) is AUTO-DENIED by the permission layer under `claude -p` and can never run
  (measured 2026-09-18; retrospective-cycle89 finding 1(b)) — do not use it. Never patch files with a heredoc;
  use the Edit/Write tools.
```

Pass check afterwards: `grep -c "MATERIAL=1" .claude/agents/material*.md` = 0 for all three.
