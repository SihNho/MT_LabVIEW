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
#               no verdict twice -> HOLD (evaluation 2026-10-14);
#   3. PLAN     lean_review.py: one Opus session (read + Write only, <= 25 min, <= $10) writes at most one task into
#               queue/next/: a same-tag retry after a FAIL (max 2 failures per tag), the plan's next step, or a revision
#               of a queued task.
# A FAILED cycle does not stop the run; what needs the user goes to questions_for_user.md (HOLD: / ASSUME: lines).
# A task whose start condition is not met (RESULT NOT-STARTED) gets no review and no plan.
# Cycles are counted by lean_review.py's own REVIEW lines; at run_limit.txt cycles it writes STOP and opens the
# evaluation discussion.
# Order: queue/next/*.md first (written by the plan step), then queue/*.md oldest first.
# Every cycle is wrapped by lean_cycle_hooks.py: START = motor limits set + PI reference move + readback (motor_gate
# --session start); END = LabVIEW closed and verified gone, then limits released + readback (--session end). A failed
# hook is a safety failure, not a task failure: it writes the STOP file and ends the run (no discussion). So does a review
# step that died without recording its cycle (exit code other than 0 or 1).
# It stops only: on the STOP file (the chat writes it when the user says stop or announces an experiment; the review step
# writes it at the run limit), after -MaxTasks cycles, on a failed cycle hook or a dead review step, or - waiting, not
# stopping - while the MAIN checkout's STATUS.md rig-state is not assembled.
# Mock queue (evaluation 2026-10-14, no LabVIEW, no motor): -Root <temp lean_bench copy> -Stub <dir with stub_hooks.py,
# stub_launch.py, fake.json> -Status <fake STATUS.md>; the real scripts are unchanged, only the three calls are replaced.
# Log: <root>/queue.log. Close this window to kill it (a running task's bgrun child keeps its 185-min deadline).
# ASCII only: Windows PowerShell 5.1 reads this file without a BOM.
param([int]$MaxTasks = 10, [string]$Root = '', [string]$Stub = '', [string]$Status = '')
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$wt = Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $here))
$main = Join-Path (Split-Path -Parent $wt) 'V6_ParallelLoop'
$base = $here; if ($Root) { $base = $Root }
$statusFile = Join-Path $main 'STATUS.md'; if ($Status) { $statusFile = $Status }
$q = Join-Path $base 'queue'; $nq = Join-Path $q 'next'; $run = Join-Path $q 'running'; $done = Join-Path $q 'done'
New-Item -ItemType Directory -Force $q, $nq, $run, $done | Out-Null
$log = Join-Path $base 'queue.log'
$stopFile = Join-Path $base 'STOP'
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
function StopRun($why) {
    Set-Content -Path $stopFile -Value ((Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + ' ' + $why) -Encoding ascii
    Say "RUN STOP: $why"
}
function RigOk {
    $s = Get-Content -Path $statusFile -Encoding UTF8 -TotalCount 400
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
function Hook($which, $tag) {
    # the child's output goes to the console (Out-Host), not into this function's return value
    if ($Stub) { & py (Join-Path $Stub 'stub_hooks.py') $which --tag $tag --root $base | Out-Host }
    else { & py (Join-Path $here 'lean_cycle_hooks.py') $which --tag $tag | Out-Host }
    return $LASTEXITCODE
}
$count = 0
Say "RUN START (worktree $wt, root $base, max $MaxTasks cycles$(if ($Stub) { ', MOCK stub ' + $Stub }))"
while ($true) {
    if (Test-Path $stopFile) { Say 'RUN STOP: STOP file present'; break }
    if ($count -ge $MaxTasks) { Say "RUN END: $count cycles done - user check, then start the next run"; break }
    $next = NextTask
    # the plan step fills the queue; empty after a cycle = nothing left this run (a run that starts empty waits for one)
    if (-not $next) { if ($count -gt 0) { Say "RUN END: queue empty after $count cycles - user check"; break }; Start-Sleep -Seconds 60; continue }
    if (-not (RigOk)) { Say "WAIT: STATUS rig-state is not assembled - $($next.Name) not started"; Start-Sleep -Seconds 300; continue }
    $tag = [IO.Path]::GetFileNameWithoutExtension($next.Name)
    $dst = Join-Path $run $next.Name
    Move-Item -Path $next.FullName -Destination $dst -Force
    $rel = 'tools/bench/lean_bench/queue/running/' + $next.Name
    $count++
    Say "CYCLE $count/$MaxTasks START $tag ($rel)"
    # cycle start: motor limits SET + PI reference move + readback (user: limits on at cycle start, off at cycle end)
    if ((Hook 'start' $tag) -ne 0) {
        Move-Item -Path $dst -Destination $next.FullName -Force
        StopRun "motor session start FAILED before $tag (newest motor_session_start_${tag}_*.log) - task put back, run stopped"
        Hook 'end' $tag | Out-Null
        break
    }
    if ($Stub) { & py (Join-Path $Stub 'stub_launch.py') --task $dst --tag $tag --root $base }
    else { & powershell -NoProfile -File (Join-Path $here 'launch_lean.ps1') -Task $rel -Tag $tag }
    $rc = $LASTEXITCODE
    # cycle end: LabVIEW closed + verified gone, then motor limits RELEASED + readback
    $erc = Hook 'end' $tag
    $doneName = $tag + '_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.md'
    Move-Item -Path $dst -Destination (Join-Path $done $doneName) -Force
    if ($erc -ne 0) { StopRun "cycle end hook FAILED after $tag (LabVIEW not gone or limits not released; see queue.log) - run stopped"; break }
    Say "CYCLE $count/$MaxTasks EXECUTE END $tag rc=$rc"
    if (Test-Path $stopFile) { Say "RUN STOP: STOP file present (no review for $tag)"; break }
    # steps 2 + 3: REVIEW (read-only Claude-GPT discussion, verdict) then PLAN (one session writes the next task)
    $rargs = @('--tag', $tag, '--task', (Join-Path $done $doneName), '--rc', $rc)
    if ($Stub) { $rargs += @('--root', $base, '--fake', (Join-Path $Stub 'fake.json')) }
    & py (Join-Path $here 'lean_review.py') @rargs
    $vrc = $LASTEXITCODE
    Say "CYCLE $count/$MaxTasks END $tag (review+plan rc=$vrc)"
    # 0 = recorded; 1 = the review crashed but recorded the cycle as HOLD; anything else = it died unrecorded
    if (($vrc -ne 0) -and ($vrc -ne 1)) { StopRun "review step for $tag died without recording the cycle (rc=$vrc) - run stopped"; break }
}
