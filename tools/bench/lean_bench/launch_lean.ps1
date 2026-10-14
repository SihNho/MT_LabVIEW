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
# cycle 3 (2026-10-14 03:17): a session ended its reply with "Waiting for the leg to end." and -p ended the whole session
# mid-leg (STATUS OPEN 54b: ending the turn ends the session). Say so in every prompt.
$prompt += " This is a NON-interactive session: the moment you end a reply, the session is over and the queue force-closes LabVIEW. After you start a background job, keep checking it with short foreground commands (e.g. sleep 25 then tail its log) until its BGRUN END line; never end a reply while anything you started is still running, and end only after the report and its RESULT line are written."
# the user's standing notes from the chat (user_notes.md) bind the execute session too, not only review and plan
if (Test-Path 'tools\bench\lean_bench\user_notes.md') { $prompt += " Also read tools/bench/lean_bench/user_notes.md: the user's standing notes; follow them, and if the task text contradicts a note, the note wins - say so in the report." }
py tools/bgrun.py --max-min 185 --log "tools/bench/lean_bench/session_$Tag.log" -- claude.exe -p --model claude-opus-5-5 --effort high --permission-mode acceptEdits --max-budget-usd 60 --output-format json $prompt
