# ---
# labview: none
# hardware: none
# ---
# Lean-rules bench arm launcher (discussion lean-rules-01, user approval in chat 2026-10-13).
# Starts ONE Opus session in this worktree (lean hooks: tools/hooks/guard_lean.py), bounded by bgrun 185 min and $60.
# ASCII only: Windows PowerShell 5.1 reads this file without a BOM.
$wt = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)))
Set-Location $wt
"LEAN START " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Out-File -Encoding ascii tools\bench\lean_bench\start.txt
$prompt = 'Lean-rules bench arm. Read CLAUDE.md (the lean rules for this worktree), then tools/bench/lean_bench/task.md, and do the task yourself in this one session. Hard limit 180 minutes from now and 60 USD. Write tools/bench/lean_bench/lean_report.md and end with its RESULT line.'
py tools/bgrun.py --max-min 185 --log tools/bench/lean_bench/session.log -- claude.exe -p --model claude-opus-5-5 --effort high --permission-mode acceptEdits --max-budget-usd 60 --output-format json $prompt
