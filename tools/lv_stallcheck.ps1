<#
    lv_stallcheck.ps1 — session-level stall detector for LabVIEW COM clients.

    WHY THIS EXISTS. Timeouts used to live inside gscript.py, wrapped around individual
    COM calls. That is only as good as Claude's memory: `Run` was guarded while `save`,
    `revert` and `CloseFrontPanel` were not, so a hang sat unnoticed for seven hours on
    2026-08-28 and again on 2026-08-29 — after Claude had reported that infinite waits
    were "structurally impossible". A guard that has to be remembered per call site is
    not a guard.

    So this runs from a PostToolUse hook instead: the harness invokes it after every
    shell command, whatever Claude did or forgot to wrap. It looks for python processes
    that have been alive past a threshold while using almost no CPU — the exact
    signature of a COM client blocked on a LabVIEW that will never answer — and reports
    them back into the transcript, together with whether a modal dialog is present.

    It only ever REPORTS. Nothing is killed: the diagnosis is the point, and deciding
    what to terminate stays a judgement call.

    Reads the hook's JSON payload on stdin (ignored) and prints a JSON object with a
    systemMessage when something looks stalled; silence otherwise.
#>
[CmdletBinding()]
param(
    [int]$StallSeconds = 150,
    [double]$IdleCpuSeconds = 5.0,
    # 2026-09-14 (peer attack, archive/peer/2026-09-14-stall-alert-wrappers-false-positive.md s2): $p.CPU is
    # LIFETIME processor time, so a client that had burned > 5 s could block forever and never be flagged. Each
    # hook run now also samples CPU per (pid, start time) into a state file and flags a process whose CPU grew
    # less than $IdleCpuDelta over the last >= $DeltaWindowSeconds - a recent-progress signature, not a lifetime one.
    [double]$IdleCpuDelta = 0.05,     # one accounting quantum of tolerance, not 0.5 s (a COM client burns ~0.15 s/min)
    [int]$DeltaWindowSeconds = 60,
    # A leaf whose bgrun job log was written this recently is making progress whatever its CPU says.
    [int]$LogFreshSeconds = 90,
    # TESTABILITY (2026-09-18, cycle 36). The two repairs below ship with a self-test, and a self-test must not
    # write into the live state file nor drop a real `stall_pid*.log` into tools/bench/ - that file is what
    # guard_peer.py blocks the next build on, so an unredirected test would BLOCK THE BUILD IT IS TESTING.
    # Empty = the production locations, unchanged.
    [string]$SamplePath = '',
    [string]$RecordPath = '',
    # -Explain prints ONE line per py/python process saying which test excluded it (or that it was named).
    # The watchdog's verdict used to be unauditable: it printed a conclusion and nothing about the leaves it
    # silently dropped, which is why "log stale" could be asserted for a leaf whose log was never consulted.
    # Off by default, so the PostToolUse hook's output is unchanged.
    [switch]$Explain
)

$ErrorActionPreference = 'Stop'
try { $null = [Console]::In.ReadToEnd() } catch { }

# Inside a benchmark cell this hook is WRONG: the cell's driver (matrix_run.py, idle while it
# waits on the cell) matches the stall signature exactly, and three cells on 2026-09-05 followed
# the "stop the task" advice by killing the driver (and two Haiku cells restarted LabVIEW).
if ($env:BENCH_CELL) { exit 0 }

try {
    $now = Get-Date
    $suspects = @()
    $cmdlines = @{}
    $parents = @{}      # every ParentProcessId that has a LIVE child
    $procs = @{}        # pid -> Win32_Process row (for the ancestor walk to the bgrun --log)
    $created = @{}      # pid -> Win32_Process CreationDate: the second half of the (pid, CreationDate) identity
    $live = @{}; $suspectKeys = @()
    $stateFile = if ($SamplePath) { $SamplePath } else { Join-Path $PSScriptRoot 'bench\.stall_samples.txt' }
    $prev = @{}
    try {
        if (Test-Path $stateFile) {
            foreach ($ln in [IO.File]::ReadAllLines($stateFile)) {
                $f = $ln -split '\|'
                if ($f.Count -ge 4) { $prev[('{0}|{1}' -f $f[2], $f[3])] = $ln }
            }
        }
    } catch { }
    try {
        Get-CimInstance Win32_Process -ErrorAction Stop | ForEach-Object {
            $parents[[int]$_.ParentProcessId] = $true
            $procs[[int]$_.ProcessId] = $_
            $created[[int]$_.ProcessId] = $_.CreationDate
            if ($_.Name -eq 'python.exe' -or $_.Name -eq 'py.exe') { $cmdlines[[int]$_.ProcessId] = [string]$_.CommandLine }
        }
    } catch { }

    # REPAIR 1 of 2 (2026-09-18, cycle 36; stall reviewer point (c), tools/bench/peer_stall_c35.log:38).
    # The command line used to come from a SEPARATE, non-atomic enumeration keyed on ProcessId ALONE, while the
    # age/CPU measurement is keyed on (Id, StartTime). Windows recycles a freed PID almost immediately, and
    # Microsoft's own Win32_Process documentation says to disambiguate with CreationDate for exactly this reason,
    # so nothing tied the `cmd pid ...` text in a stall record to the process whose age and CPU were measured.
    # Every command-line read now goes through this: it returns the text only when the PAIR (pid, CreationDate)
    # matches the measured start time, and $null - "not identified" - otherwise. It never returns another
    # process's text. Tolerance 2 s because .NET's Process.StartTime and WMI's CreationDate are two clocks
    # rounding the same instant, not one value read twice.
    function Get-BoundCmdLine([int]$ProcId, [DateTime]$Started) {
        if (-not $cmdlines.ContainsKey($ProcId)) { return $null }
        $c = $created[$ProcId]
        if (-not $c) { return $null }
        if ([math]::Abs((([DateTime]$c) - $Started).TotalSeconds) -gt 2) { return $null }
        return $cmdlines[$ProcId]
    }

    function Say-Why([int]$ProcId, [string]$Reason) {
        if ($Explain) { Write-Output ('EXPLAIN pid {0}: {1}' -f $ProcId, $Reason) }
    }

    foreach ($p in (Get-Process py, python -ErrorAction SilentlyContinue)) {
        if (-not $p.StartTime) { Say-Why $p.Id 'skip - no readable StartTime'; continue }
        $cl = Get-BoundCmdLine ([int]$p.Id) $p.StartTime
        # Long-lived by design, never a stalled COM client: the matrix driver and its launcher.
        if ($cl -and ($cl -like '*matrix_run*' -or $cl -like '*run_matrix*')) { Say-Why $p.Id 'skip - matrix driver'; continue }
        # REPAIR (2026-09-19, cycle 37, judgement's call - deliberately NARROWER than the reviewer's proposal).
        # A `tools/wait_logs.py` LEAF HOLDS NO LabVIEW CLIENT AT ALL, so "STALLED LabVIEW client" can never be a
        # true sentence about it and NO threshold can make the test meaningful there: the script opens files and
        # sleeps, by construction burning no CPU and writing nothing until its tick ends. Two of the four records
        # this class produced were waiters - stall_pid18476_232310.log:3 and stall_pid1556_002547.log:3 - and the
        # second fired AFTER cycle 37's freshness clause, correctly, because the job it watched was a `claude -p`
        # peer cell that is alive and silent for its whole 640 s, leaving every log on the waiter's command line
        # stale. $LogFreshSeconds is NOT raised and no liveness probe is added: a waiter is excluded by WHAT IT
        # IS, not by how fast something it watches moves.
        #
        # TWO CORRECTIONS THE REVIEW OF THIS CLAUSE FORCED (archive/peer/2026-09-19-stall-waitlogs-c37b.md,
        # ANSWERED, opus/max). Both are FACTS, not opinions, and neither is answered here - the design question
        # they open is the judgement session's:
        #   (1) The sentence that used to stand here - "the other two records are real build clients ... so the
        #       class the rule exists for keeps firing" - IS FALSE. The reviewer resolved the job named on line 1
        #       of every record: stall_pid11424_221324 -> build_d1_routeb_v1_run4.log `END rc=1 after 1713s`
        #       under a 30-min limit, and stall_pid3792_235020 -> build_d1_routeb_v2_run5.log `END rc=1 after
        #       1668s` under a 40-min limit. NEITHER client was killed at its deadline; run 4's went on writing
        #       PASS lines for 905 s after being accused (build_d1_routeb_v1_run4.log:340-353). So those two are
        #       ALSO false positives, and this watchdog has no confirmed true positive on record. This clause
        #       therefore takes precision from 0/4 to 0/2 - it does not restore a working test.
        #   (2) Because this skip runs BEFORE the freshness clause at :200-211, it makes that clause UNREACHABLE
        #       for the only leaf class it was written for, and falsifies its stated guarantee at :192
        #       ("a waiter sleeping on a genuinely dead job still fires"). That guarantee is now gone.
        # The reviewer's own proposal - write the gating stall_pid*.log ONLY when the dialog check at :257
        # returns `VERDICT: BLOCKED` (all four records say "no modal dialog", so it writes zero of them) - is a
        # DESIGN CHANGE and was deliberately NOT made by the material session that wrote this clause.
        if ($cl -and $cl -like '*wait_logs.py*') { Say-Why $p.Id 'skip - tools/wait_logs.py waiter (holds no LabVIEW client)'; continue }
        # 2026-09-14: a WRAPPER (py.exe launcher, bgrun.py, peer dispatch) is idle by construction while its
        # child works - it matched the stall signature on every long probe and produced false "STALLED"
        # alerts while the real client (its grandchild) was burning CPU. Only LEAF processes can stall.
        if ($parents.ContainsKey([int]$p.Id)) { Say-Why $p.Id 'skip - wrapper (has a live child)'; continue }
        # 2026-09-14 10:58 (record stall_pid9272_105613.log, reviewed): a VI-Server COM client sits blocked in
        # LabVIEW's Run call and burns ~2.5 ms CPU per op run, so 0.4 s of CPU over 163 s was a HEALTHY sweep that
        # wrote a log line every second. Progress, not CPU, is the signal: if the bgrun log of this process's job
        # was written within $LogFreshSeconds, the client is working - skip it.
        $logFile = $null; $anc = $p.Id; $ancStart = $p.StartTime
        for ($hop = 0; $hop -lt 6 -and $anc; $hop++) {
            $row = $procs[[int]$anc]
            if (-not $row) { break }
            $rowStart = $row.CreationDate
            # The same (pid, CreationDate) bind as Get-BoundCmdLine, applied to the walk: hop 0 must BE the
            # process that was measured, and a genuine ancestor always starts BEFORE its child - a "parent"
            # whose CreationDate is later is a recycled PID, and following it would read some unrelated
            # process's command line as this job's runner.
            if ($hop -eq 0) {
                if (-not $rowStart -or [math]::Abs((([DateTime]$rowStart) - $p.StartTime).TotalSeconds) -gt 2) { break }
            } elseif ($rowStart -and $ancStart -and (([DateTime]$rowStart) -gt (([DateTime]$ancStart).AddSeconds(2)))) {
                break
            }
            if ($rowStart) { $ancStart = $rowStart }
            if ($row.CommandLine -match 'bgrun\.py.*?--log\s+("([^"]+)"|(\S+))') {
                $logFile = if ($matches[2]) { $matches[2] } else { $matches[3] }; break
            }
            $anc = $row.ParentProcessId
        }
        # REPAIR 2 of 2 (2026-09-18, cycle 36). A LEAF WITH NO bgrun JOB LOG IS NOT SOMETHING THIS WATCHDOG CAN
        # SPEAK ABOUT. It only ever enumerated py/python and never tested for a COM reference, so a bare
        # `python -c` waiter - e.g. the loop that polls cycle_runner.log for RUNNER STOP - was labelled a
        # "STALLED LabVIEW client", wrote a stall_pid*.log, and through guard_peer.py BLOCKED the next build
        # until a review was archived: cycle 35 paid $5.78 and ~16 min for exactly that (retrospective-cycle35,
        # `repeated-failure-class`). Worse, the freshness branch below was SKIPPED for such a leaf while :112
        # still emitted the words "log stale" as a hard-coded literal - the record asserted a log check that had
        # never run (stall reviewer, peer_stall_c35.log:40). Every real client this watchdog exists for is
        # launched through bgrun - CLAUDE.md makes it the ONLY allowed way to background a LabVIEW command - so
        # "no bgrun --log among my ancestors" means "not the thing under watch". Skip, do not accuse.
        if (-not $logFile) { Say-Why $p.Id 'skip - no bgrun --log among its ancestors (not a job this watchdog watches)'; continue }
        $logAge = $null
        $lf = if ([IO.Path]::IsPathRooted($logFile)) { $logFile } else { Join-Path (Split-Path $PSScriptRoot -Parent) $logFile }
        if (Test-Path $lf) {
            $logAge = ($now - (Get-Item $lf).LastWriteTime).TotalSeconds
            if ($logAge -lt $LogFreshSeconds) { Say-Why $p.Id ('skip - job log {0} written {1:N0}s ago (progress)' -f $logFile, $logAge); continue }
        }
        # REPAIR (2026-09-19, cycle 37): LIVENESS WAS READ FROM THE WRONG FILE. The block above measures the
        # ANCESTOR's `bgrun --log`. For a client that is where progress appears; for a WAITER (tools/wait_logs.py)
        # it is where progress NEVER appears - the waiter prints only after its loop ends, while the file it is
        # watching grows the whole time. That file's name sits on the LEAF's own bound command line and is already
        # printed on line 3 of every stall record, so the watchdog had the live file in hand and measured the dead
        # one: stall_pid18476_232310.log (23:26) fired on a healthy waiter and, through guard_peer.py, blocked the
        # next build - the third cycle running. Minimal clause named by the reviewer
        # (archive/peer/2026-09-18-stall-waitlogs-c37.md, section 5): flag only if EVERY log path on the leaf's own
        # command line is ALSO stale beyond $LogFreshSeconds. Coverage is unchanged for real clients -
        # stall_pid11424_221324.log:3 and stall_pid3792_235020.log:3 name no .log on their command lines, so the
        # clause is vacuous for them - and a waiter sleeping on a genuinely dead job still fires, because then both
        # logs are stale. A named path that is not on disk counts as stale: absence is not progress.
        # Two candidate patterns, because a log path can appear either as its own token
        # (`... wait_logs.py --seconds 1020 tools/bench/x.log`) or inside a quoted argument. A single
        # '"([^"]+\.log)"|(\S+\.log)' does NOT work: on a quoted `-c "...script text... C:\...\x.log"` the first
        # alternative matches the WHOLE quoted blob and consumes the real path with it (self-test run 1,
        # tools/bench/repair_c37_selftest.log: G1 failed, the fresh leaf was flagged). Anything that is not a file
        # simply fails Test-Path below, so over-collecting candidates is free.
        if ($cl) {
            $freshOwn = $null
            $cands = @()
            foreach ($m in [regex]::Matches($cl, '[^\s"'']+\.log')) { $cands += $m.Value }
            foreach ($m in [regex]::Matches($cl, '"([^"]+\.log)"')) { $cands += $m.Groups[1].Value }
            foreach ($cand in $cands) {
                $cp = if ([IO.Path]::IsPathRooted($cand)) { $cand } else { Join-Path (Split-Path $PSScriptRoot -Parent) $cand }
                if (-not (Test-Path $cp)) { continue }
                $cAge = ($now - (Get-Item $cp).LastWriteTime).TotalSeconds
                if ($cAge -lt $LogFreshSeconds) { $freshOwn = ('{0} written {1:N0}s ago' -f $cand, $cAge); break }
            }
            if ($freshOwn) { Say-Why $p.Id ('skip - a log on its own command line is fresh: ' + $freshOwn); continue }
        }
        $age = ($now - $p.StartTime).TotalSeconds
        $key = '{0}|{1}' -f $p.Id, $p.StartTime.ToString('yyyyMMddHHmmss')
        $cpu = [double]$p.CPU
        $live[$key] = ('{0}|{1}|{2}' -f $cpu, $now.ToString('o'), $key)
        if ($age -lt $StallSeconds) { Say-Why $p.Id ('skip - only {0:N0}s old (< {1}s)' -f $age, $StallSeconds); continue }
        # 2026-09-14 14:3x (4 false positives, 0 true stalls; review archive/peer/2026-09-14-stall-record-matrix-silent-
        # block.md): the LIFETIME-CPU predicate is dropped - a VI-Server COM client legitimately burns ~2.5 ms per op
        # run. A stall is now: alive AND its job log stale (checked above) AND no CPU progress over the last
        # >= $DeltaWindowSeconds (delta <= $IdleCpuDelta). No baseline sample yet -> not a stall (wait for one).
        $why = $null
        if ($prev.ContainsKey($key)) {
            $parts = $prev[$key] -split '\|'
            $dcpu = $cpu - [double]$parts[0]
            $dt = ($now - [DateTime]::Parse($parts[1])).TotalSeconds
            # The log age is now a MEASURED number on the line, not the literal word "stale": a leaf that reached
            # here has a bgrun job log (repair 2), so the claim is checkable from the record itself.
            if ($dt -ge $DeltaWindowSeconds -and $dcpu -le $IdleCpuDelta) {
                $ageTxt = if ($null -ne $logAge) { ('{0:N0}s' -f $logAge) } else { 'not on disk' }
                $why = ('job log {0} last written {1}, CPU +{2:N2}s in the last {3:N0}s' -f $logFile, $ageTxt, $dcpu, $dt)
            }
            if (-not $why) { Say-Why $p.Id ('skip - CPU +{0:N2}s over {1:N0}s (needs dt >= {2}s and dcpu <= {3})' -f $dcpu, $dt, $DeltaWindowSeconds, $IdleCpuDelta) }
        } else {
            Say-Why $p.Id ('skip - no baseline CPU sample yet for key {0}' -f $key)
        }
        if ($why) { $suspects += ('pid {0} alive {1:N0}s, {2}' -f $p.Id, $age, $why); $suspectKeys += $key; Say-Why $p.Id ('NAMED - ' + $why) }
    }
    # Persist this run's samples (only processes still alive; a sample is kept, not replaced, until the window
    # has elapsed so the delta is measured over >= $DeltaWindowSeconds and not over back-to-back hook runs).
    try {
        $keep = @()
        foreach ($k in $live.Keys) {
            if ($prev.ContainsKey($k)) {
                $parts = $prev[$k] -split '\|'
                if (($now - [DateTime]::Parse($parts[1])).TotalSeconds -lt $DeltaWindowSeconds) { $keep += $prev[$k]; continue }
            }
            $keep += $live[$k]
        }
        [IO.File]::WriteAllLines($stateFile, [string[]]$keep)
    } catch { }
    if (-not $suspects) { exit 0 }

    $dialog = 'unknown'
    try {
        $out = & (Join-Path $PSScriptRoot 'lv_gui.ps1') -Action dialogs 2>&1 | Out-String
        $dialog = if ($out -match 'VERDICT: BLOCKED') { 'MODAL DIALOG PRESENT - run lv_gui.ps1 -Action dismiss' }
                  elseif ($out -match 'VERDICT: clear') { 'no modal dialog - LabVIEW busy or two clients contending' }
                  else { 'dialog check inconclusive' }
    } catch { }

    # 2026-09-14 (user: "이런 에러들도 반복되는 것 같으니 피어리뷰 반드시 필요하겠어. 규율에 적용하도록"):
    # a stall is a FAILED PREDICTION ("this client finishes") and is gated like one. Write a record under
    # tools/bench/ carrying a `STALL:` line; tools/hooks/guard_peer.py treats it as a failing log and blocks the
    # next build until archive/peer/ holds a review newer than it. One file per stall EVENT (leaf pid + its
    # start time), written ONCE on the transition into the stalled state - the peer attack (s3) showed that
    # rewriting it on every hook run made a completed review older than the record again, wedging the loop.
    $record = 'none'
    try {
        $leaf = ($suspects[0] -replace '^pid (\d+).*$', '$1')
        $start = ($suspectKeys[0] -split '\|')[1]
        $record = if ($RecordPath) { $RecordPath } else { Join-Path $PSScriptRoot ('bench\stall_pid{0}_{1}.log' -f $leaf, $start.Substring(8)) }
        if ($dialog -notlike 'MODAL DIALOG PRESENT*') { $record = 'NOT WRITTEN - the dialog check did not return VERDICT: BLOCKED (repair 2026-09-19, cycle 39, judgement-authorised: the gating record is written ONLY on a confirmed modal dialog; precision of this watchdog was 0/6 and every false record cost a paid peer review to clear)' } elseif (-not (Test-Path $record)) {
            $lines = @(('STALL: {0:yyyy-MM-dd HH:mm:ss} {1}' -f $now, ($suspects -join '; ')), ('dialog: ' + $dialog))
            for ($i = 0; $i -lt $suspects.Count; $i++) {
                $kp = $suspectKeys[$i] -split '\|'
                $spid = [int]$kp[0]
                # BOUND to (pid, CreationDate). When the pair does not match, the record says so instead of
                # printing whatever process now holds that PID.
                $bound = $null
                try { $bound = Get-BoundCmdLine $spid ([DateTime]::ParseExact($kp[1], 'yyyyMMddHHmmss', $null)) } catch { }
                if ($bound) { $lines += ('cmd pid {0} (started {1}): {2}' -f $spid, $kp[1], $bound) }
                else { $lines += ('cmd pid {0} (started {1}): NOT IDENTIFIED - no Win32_Process row with a matching CreationDate (PID recycled or process gone)' -f $spid, $kp[1]) }
            }
            [IO.File]::WriteAllLines($record, [string[]]$lines)   # UTF-8 WITHOUT BOM (Set-Content -Encoding utf8 adds one in PS 5.1)
        } else { $record = "$record (already recorded at first sight; not rewritten)" }
    } catch { $record = 'could not be written' }

    $msg = "STALLED LabVIEW client(s): " + ($suspects -join '; ') + ". $dialog. " +
           "Do not wait: diagnose now (screenshot, dialogs) and stop the task. " +
           "STALL RECORD written: $record - the next build is BLOCKED by guard_peer.py until a peer review newer than it is archived (CLAUDE.md: a stall is a failed prediction)."
    @{ systemMessage = $msg } | ConvertTo-Json -Compress
} catch {
    exit 0   # a broken watchdog must never break the session
}
