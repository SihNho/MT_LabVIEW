# ---
# labview: none
# hardware: none
# ---
# Lean task QUEUE runner (option b, user 2026-10-13). The USER starts this once; it runs the task files the chat puts in
# tools/bench/lean_bench/queue/ one at a time, oldest first, each through launch_lean.ps1 (one Opus session, <= 185 min,
# <= $60, lean hooks). It never starts a task while:
#   - tools/bench/lean_bench/STOP exists (the chat writes it when the user says stop or announces an experiment), or
#   - the MAIN checkout's STATUS.md `rig-state:` line is not the assembled state (assembled, not in use).
# A task file moves queue/ -> queue/running/ -> queue/done/. Idle: checks every 60 s. Log: tools/bench/lean_bench/queue.log
# Stop it: create the STOP file, or close this window (a running task's bgrun child keeps its own 185-min deadline).
# ASCII only: Windows PowerShell 5.1 reads this file without a BOM.
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$wt = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $here))
$main = Join-Path (Split-Path -Parent $wt) 'V6_ParallelLoop'
$q = Join-Path $here 'queue'; $run = Join-Path $q 'running'; $done = Join-Path $q 'done'
New-Item -ItemType Directory -Force $q, $run, $done | Out-Null
$log = Join-Path $here 'queue.log'
function Say($m) { $l = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' | ' + $m; Add-Content -Path $log -Value $l -Encoding UTF8; Write-Output $l }
function RigOk {
    $s = Get-Content -Path (Join-Path $main 'STATUS.md') -Encoding UTF8 -TotalCount 400
    $line = $s | Where-Object { $_ -match '^rig-state:' } | Select-Object -First 1
    # the assembled state is the Korean word for assembled; compared by its UTF-8 bytes so this file stays ASCII
    $assembled = [System.Text.Encoding]::UTF8.GetString([byte[]](0xEC,0xA1,0xB0,0xEB,0xA6,0xBD))
    return ($line -ne $null) -and ($line -match ('^rig-state:\s*' + $assembled))
}
Say "QUEUE START (worktree $wt)"
while ($true) {
    if (Test-Path (Join-Path $here 'STOP')) { Say 'QUEUE STOP: STOP file present'; break }
    $next = Get-ChildItem -Path $q -Filter '*.md' -File | Sort-Object LastWriteTime | Select-Object -First 1
    if (-not $next) { Start-Sleep -Seconds 60; continue }
    if (-not (RigOk)) { Say "WAIT: main STATUS rig-state is not assembled - $($next.Name) not started"; Start-Sleep -Seconds 300; continue }
    $tag = [IO.Path]::GetFileNameWithoutExtension($next.Name)
    $dst = Join-Path $run $next.Name
    Move-Item -Path $next.FullName -Destination $dst -Force
    $rel = 'tools/bench/lean_bench/queue/running/' + $next.Name
    Say "TASK START $tag ($rel)"
    & powershell -NoProfile -File (Join-Path $here 'launch_lean.ps1') -Task $rel -Tag $tag
    Say "TASK END $tag rc=$LASTEXITCODE"
    Move-Item -Path $dst -Destination (Join-Path $done $next.Name) -Force
}
