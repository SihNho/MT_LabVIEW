# ---
# labview: none
# hardware: none
# ---
# Lean task QUEUE runner (option b, user 2026-10-13). The USER starts this; one start = one RUN of at most -MaxTasks cycles
# (default 10; user 2026-10-13: 10 cycles per run, the user checks after each run and starts the next). A cycle = one task
# file, in three steps (user 2026-10-13: execute agent -> review agent (discussion) -> plan):
#   1. EXECUTE  launch_lean.ps1: one Opus session, <= 185 min, <= $60, lean hooks (motor hook, originals, LabVIEW limits);
#   2. REVIEW   lean_review.py: one read-only Claude-GPT discussion (<= 40 min) re-computes the acceptance from the raw
#               output files and checks the safety records -> VERDICT PASS/FAIL (PASS needs the session's PASS too);
#   3. PLAN     lean_review.py: one Opus session (read + Write only, <= 25 min, <= $10) writes at most one task into
#               queue/next/: a same-tag retry after a FAIL (max 2 failures per tag) or the plan's next step.
# A FAILED cycle does not stop the run; what needs the user goes to questions_for_user.md for the 10-cycle check.
# A task whose start condition is not met (RESULT NOT-STARTED) gets no review and no plan.
# Order: queue/next/*.md first (written by the plan step), then queue/*.md oldest first.
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
function Say($m) {
    # run 1 (2026-10-13/14): Add-Content lost every line after the first cycle started (the file was also open in other
    # processes: tail -F watchers, Python appenders), so the run-limit counter read 0. Open with FileShare.ReadWrite and
    # retry a few times; a line that still cannot be written goes to the console only.
    $l = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' | ' + $m
    for ($i = 0; $i -lt 5; $i++) {
        try {
            $fs = New-Object IO.FileStream($log, [IO.FileMode]::Append, [IO.FileAccess]::Write, [IO.FileShare]::ReadWrite)
            $b = [Text.Encoding]::UTF8.GetBytes($l + "`r`n"); $fs.Write($b, 0, $b.Length); $fs.Close(); break
        } catch { Start-Sleep -Milliseconds 200 }
    }
    Write-Output $l
}
function RigOk {
    $s = Get-Content -Path (Join-Path $main 'STATUS.md') -Encoding UTF8 -TotalCount 400
    $line = $s | Where-Object { $_ -match '^rig-state:' } | Select-Object -First 1
    # the assembled state is the Korean word for assembled; compared by its UTF-8 bytes so this file stays ASCII
    $assembled = [System.Text.Encoding]::UTF8.GetString([byte[]](0xEC,0xA1,0xB0,0xEB,0xA6,0xBD))
    return ($line -ne $null) -and ($line -match ('^rig-state:\s*' + $assembled))
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
    Say "CYCLE $count/$MaxTasks EXECUTE END $tag rc=$rc"
    if (Test-Path (Join-Path $here 'STOP')) { Say "RUN STOP: STOP file present (no review for $tag)"; break }
    # steps 2 + 3: REVIEW (read-only Claude-GPT discussion, verdict) then PLAN (one session writes the next task)
    & py (Join-Path $here 'lean_review.py') --tag $tag --task ('tools/bench/lean_bench/queue/done/' + $doneName) --rc $rc
    Say "CYCLE $count/$MaxTasks END $tag (review+plan rc=$LASTEXITCODE; record lean_review_$tag.md)"
}
