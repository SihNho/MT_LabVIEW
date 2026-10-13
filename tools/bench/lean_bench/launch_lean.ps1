# ---
# labview: none
# hardware: none
# ---
# Lean-rules session launcher (discussion lean-rules-01, user approval in chat 2026-10-13).
# Starts ONE Opus session in this worktree (lean hooks: tools/hooks/guard_lean.py), bounded by bgrun 185 min and $60.
# Usage: powershell -NoProfile -File <this file> [-Task tools/bench/lean_bench/task_p63.md] [-Tag p63]
# ASCII only: Windows PowerShell 5.1 reads this file without a BOM.
param([string]$Task = 'tools/bench/lean_bench/task.md', [string]$Tag = 'p62')
$wt = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)))
Set-Location $wt
if (-not (Test-Path $Task)) { Write-Output "task file not found: $Task"; exit 2 }
"LEAN START $Tag " + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') | Out-File -Encoding ascii "tools\bench\lean_bench\start_$Tag.txt"
$prompt = "Lean-rules session. Read CLAUDE.md (the lean rules for this worktree), then $Task, and do the task yourself in this one session. Hard limit 180 minutes from now and 60 USD. Write the report the task names and end with its RESULT line."
py tools/bgrun.py --max-min 185 --log "tools/bench/lean_bench/session_$Tag.log" -- claude.exe -p --model claude-opus-5-5 --effort high --permission-mode acceptEdits --max-budget-usd 60 --output-format json $prompt
