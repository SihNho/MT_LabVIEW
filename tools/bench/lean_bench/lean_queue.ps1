# ---
# labview: none
# hardware: none
# ---
# Lean task QUEUE runner (option b, user 2026-10-13). The USER starts this; one start = one RUN of at most -MaxTasks cycles
# (default 10; user 2026-10-13: 10 cycles per run, the user checks after each run and starts the next). A cycle = one task
# file through launch_lean.ps1 (one Opus session, <= 185 min, <= $60, lean hooks: motor hook, originals, LabVIEW limits).
# Order: queue/next/*.md first (retries written by a failure discussion), then queue/*.md oldest first.
# A FAILED cycle does not stop the run (user 2026-10-13: a failed cycle is discussed to set the direction, not stopped):
#   - report RESULT is NOT-STARTED (its start condition was not met)  -> logged SKIP, no discussion, next task;
#   - any other non-PASS (or rc != 0) -> lean_discuss.py: one read-only Claude-GPT discussion (<= 40 min). Agreed actions
#     -> a retry task with the same tag in queue/next/ (runs next). No agreed action, a question only the user can answer,
#     or a tag's third failure -> the tag is skipped and the reason goes to questions_for_user.md for the 10-cycle check.
# Every cycle is wrapped by lean_cycle_hooks.py: START = motor limits set + PI reference move + readback (motor_gate
# --session start); END = LabVIEW closed and verified gone, then limits released + readback (--session end). A failed
# hook is a safety failure, not a task failure: it writes the STOP file and ends the run (no discussion).
# It stops only: after -MaxTasks cycles (the user's check), on a failed cycle hook, on the STOP file (the chat writes it when the user says stop or
# announces an experiment), or - waiting, not stopping - while the MAIN checkout's STATUS.md rig-state is not assembled.
# Log: tools/bench/lean_bench/queue.log. Close this window to kill it (a running task's bgrun child keeps its 185-min deadline).
# ASCII only: Windows PowerShell 5.1 reads this file without a BOM.
param([int]$MaxTasks = 10)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$wt = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $here))
$main = Join-Path (Split-Path -Parent $wt) 'V6_ParallelLoop'
$q = Join-Path $here 'queue'; $nq = Join-Path $q 'next'; $run = Join-Path $q 'running'; $done = Join-Path $q 'done'
New-Item -ItemType Directory -Force $q, $nq, $run, $done | Out-Null
$log = Join-Path $here 'queue.log'
function Say($m) { $l = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' | ' + $m; Add-Content -Path $log -Value $l -Encoding UTF8; Write-Output $l }
function RigOk {
    $s = Get-Content -Path (Join-Path $main 'STATUS.md') -Encoding UTF8 -TotalCount 400
    $line = $s | Where-Object { $_ -match '^rig-state:' } | Select-Object -First 1
    # the assembled state is the Korean word for assembled; compared by its UTF-8 bytes so this file stays ASCII
    $assembled = [System.Text.Encoding]::UTF8.GetString([byte[]](0xEC,0xA1,0xB0,0xEB,0xA6,0xBD))
    return ($line -ne $null) -and ($line -match ('^rig-state:\s*' + $assembled))
}
function ResultOf($tag) {
    # -> 'PASS', 'NOT-STARTED', or 'OTHER' (missing report / no RESULT line / FAIL / INCOMPLETE ...)
    $rep = Join-Path $here ('lean_report_' + $tag + '.md')
    if (-not (Test-Path $rep)) { return 'OTHER' }
    $r = Get-Content -Path $rep -Encoding UTF8 | Where-Object { $_ -match '^\s*`?RESULT\s*\{' } | Select-Object -Last 1
    if ($r -eq $null) { return 'OTHER' }
    $k = '"' + [regex]::Escape($tag) + '"\s*:\s*"'
    if ($r -match ($k + 'PASS"')) { return 'PASS' }
    if ($r -match ($k + 'NOT-STARTED"')) { return 'NOT-STARTED' }
    return 'OTHER'
}
function NextTask {
    $n = Get-ChildItem -Path $nq -Filter '*.md' -File | Sort-Object LastWriteTime | Select-Object -First 1
    if ($n) { return $n }
    return (Get-ChildItem -Path $q -Filter '*.md' -File | Sort-Object LastWriteTime | Select-Object -First 1)
}
$count = 0
Say "RUN START (worktree $wt, max $MaxTasks cycles)"
while ($true) {
    if (Test-Path (Join-Path $here 'STOP')) { Say 'RUN STOP: STOP file present'; break }
    if ($count -ge $MaxTasks) { Say "RUN END: $count cycles done - user check, then start the next run"; break }
    $next = NextTask
    if (-not $next) { Start-Sleep -Seconds 60; continue }
    if (-not (RigOk)) { Say "WAIT: main STATUS rig-state is not assembled - $($next.Name) not started"; Start-Sleep -Seconds 300; continue }
    $tag = [IO.Path]::GetFileNameWithoutExtension($next.Name)
    $dst = Join-Path $run $next.Name
    Move-Item -Path $next.FullName -Destination $dst -Force
    $rel = 'tools/bench/lean_bench/queue/running/' + $next.Name
    $count++
    Say "CYCLE $count/$MaxTasks START $tag ($rel)"
    # cycle start: motor limits SET + PI reference move + readback (user: limits on at cycle start, off at cycle end)
    & py (Join-Path $here 'lean_cycle_hooks.py') start --tag $tag
    if ($LASTEXITCODE -ne 0) {
        Move-Item -Path $dst -Destination $next.FullName -Force
        $why = "motor session start FAILED before $tag (tools/bench/lean_bench/motor_session_start_$tag.log) - task put back, run stopped"
        Set-Content -Path (Join-Path $here 'STOP') -Value ((Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ' + $why) -Encoding ascii
        & py (Join-Path $here 'lean_cycle_hooks.py') end --tag $tag
        Say "RUN STOP: $why"; break
    }
    & powershell -NoProfile -File (Join-Path $here 'launch_lean.ps1') -Task $rel -Tag $tag
    $rc = $LASTEXITCODE
    # cycle end: LabVIEW closed + verified gone, then motor limits RELEASED + readback
    & py (Join-Path $here 'lean_cycle_hooks.py') end --tag $tag
    if ($LASTEXITCODE -ne 0) {
        $why = "cycle end hook FAILED after $tag (LabVIEW not gone or limits not released; see queue.log) - run stopped"
        Set-Content -Path (Join-Path $here 'STOP') -Value ((Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ' + $why) -Encoding ascii
        Say "RUN STOP: $why"
        Move-Item -Path $dst -Destination (Join-Path $done ($tag + '_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.md')) -Force
        break
    }
    $doneName = $tag + '_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.md'
    Move-Item -Path $dst -Destination (Join-Path $done $doneName) -Force
    $res = ResultOf $tag
    Say "CYCLE $count/$MaxTasks END $tag rc=$rc result=$res"
    if (($rc -eq 0) -and ($res -eq 'PASS')) { continue }
    if ($res -eq 'NOT-STARTED') { Say "SKIP ${tag}: start condition not met (no discussion)"; continue }
    if (Test-Path (Join-Path $here 'STOP')) { Say "RUN STOP: STOP file present (no discussion for $tag)"; break }
    Say "DISCUSS START $tag (failed cycle; the run goes on after it)"
    & py (Join-Path $here 'lean_discuss.py') --tag $tag --task ('tools/bench/lean_bench/queue/done/' + $doneName) --rc $rc
    if ($LASTEXITCODE -eq 0) { Say "DISCUSS END ${tag}: retry queued in queue/next/$tag.md" }
    else { Say "DISCUSS END ${tag}: skipped (reason in questions_for_user.md)" }
}
