# read_motor_anchor.ps1 - READ-ONLY. Establish the ANCHOR that tools/motor_gate.py measures every future move
# against, and write it to tools/bench/motor_anchor.json.
#
# NO MOTION COMMAND IS SENT. The command lists below are hardcoded query-only sets, each one already proven on this
# rig by an existing script, and every command is re-checked against a forbidden-token list before it is transmitted:
#   ASI  COM4 115200 8N1, CR out / CRLF in  - tools/bench/serial_roundtrip_asi.ps1 +
#                                             archive/peer/2026-09-12-asi-tiger-readonly-commands.md (codex)
#   PI   COM3 115200 8N1, LF                - tools/bench/serial_roundtrip.ps1 ($SAFE = *IDN? POS? ERR? TMN? TMX?)
#   ports/aliases: docs/instrument-libraries.md:167-169
#
# WHY IT IS OUTSIDE THE GATE: tools/motor_gate.py refuses everything while the anchor file is missing, so the file
# that creates the anchor cannot go through it. It is therefore query-only by construction and is named on
# guard_bash.py's read-only allow-list.
#
# The user's LabVIEW may hold these ports. That is not an error to work around: if a port is busy the fact is
# printed and the anchor is NOT written. Nothing is killed, nothing is retried in a loop.
#
#   & .\tools\bench\read_motor_anchor.ps1
param(
    [string]$AsiPort = 'COM4',
    [string]$PiPort = 'COM3',
    [int]$Baud = 115200,
    [int]$ReadTimeoutMs = 400
)

$ErrorActionPreference = 'Continue'
$OutFile = Join-Path $PSScriptRoot 'motor_anchor.json'

# Second, independent gate: no command containing any of these is ever transmitted, whatever the lists above say.
$FORBIDDEN = @('MOVE', 'MOVREL', 'SPIN', '@', 'MULTIMV', 'MM', 'VECTOR', 'VE', 'SCAN', 'SN', 'NR', 'NV',
    'HOME', '!', 'ZERO', 'HERE', 'SETHOME', 'HM', 'AZERO', 'AZ', 'HALT', '\',
    'SAVESET', 'SS', 'SAVEPOS', 'SP', 'SAVE', 'RESET', '~', 'MOTCTRL', 'MC',
    'MOV ', 'MVR', 'GOH', 'FRF', 'FNL', 'FPL', 'DFH', 'SVO', 'VEL ', '=')

function Test-Safe([string]$cmd) {
    foreach ($bad in $FORBIDDEN) {
        if ($cmd.ToUpper().Contains($bad.ToUpper())) {
            Write-Output "ABORT: command '$cmd' contains blacklisted token '$bad'."
            exit 3
        }
    }
}

function Invoke-Port([string]$Port, [string[]]$Cmds, [string]$NewLine) {
    $res = [ordered]@{ port = $Port; baud = $Baud; opened = $false; error = ''; replies = [ordered]@{} }
    $sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
    $sp.ReadTimeout = $ReadTimeoutMs
    $sp.WriteTimeout = 1000
    $sp.NewLine = $NewLine
    try {
        $sp.Open()
        $res.opened = $true
        Write-Output "opened $Port"
        Start-Sleep -Milliseconds 150
        foreach ($cmd in $Cmds) {
            Test-Safe $cmd
            $sp.DiscardInBuffer(); $sp.DiscardOutBuffer()
            $lines = New-Object System.Collections.Generic.List[string]
            try {
                $sp.WriteLine($cmd)
                for ($k = 0; $k -lt 3; $k++) {
                    $line = $sp.ReadLine()
                    $clean = ($line -replace '[^\x20-\x7e]', '')
                    if ($clean.Trim().Length -gt 0) { $lines.Add($clean.Trim()) }
                }
            }
            catch { }
            $res.replies[$cmd] = ($lines -join ' | ')
            Write-Output ("  {0,-8} -> '{1}'" -f $cmd, ($lines -join ' | '))
            Start-Sleep -Milliseconds 30
        }
    }
    catch {
        $res.error = $_.Exception.Message
        Write-Output "  $Port NOT READ: $($_.Exception.Message)"
    }
    finally {
        if ($sp.IsOpen) { $sp.Close() }
        $sp.Dispose()
        if ($res.opened) { Write-Output "closed $Port" }
    }
    return $res
}

Write-Output "read_motor_anchor: QUERY ONLY, no motion command exists in this file."
Write-Output ("LabVIEW processes now: " + ((Get-Process -Name LabVIEW -ErrorAction SilentlyContinue | ForEach-Object { $_.Id }) -join ',' ))

# ASI: '/' is STATUS (fixed 1-char reply); 'W X'/'W Y'/'W Z' are WHERE, position in TENTHS OF MICRONS.
$asi = Invoke-Port -Port $AsiPort -Cmds @('/', 'W X', 'W Y', 'W Z') -NewLine "`r"
# PI: GCS queries only.
$pi = Invoke-Port -Port $PiPort -Cmds @('*IDN?', 'POS?', 'TMN?', 'TMX?') -NewLine "`n"

function Get-Num([string]$reply) {
    if (-not $reply) { return $null }
    $m = [regex]::Match($reply, '[-+]?\d+(\.\d+)?')
    if ($m.Success) { return [double]$m.Value }
    return $null
}
# ASI WHERE replies look like ':A 12345.6'; the leading ':A' has no digits, so the first number is the position.
$ax = Get-Num $asi.replies['W X']
$ay = Get-Num $asi.replies['W Y']
$az = Get-Num $asi.replies['W Z']
# PI POS? replies look like '1=12.345000'; take the number AFTER '='.
function Get-PiNum([string]$reply) {
    if (-not $reply) { return $null }
    $m = [regex]::Match($reply, '=\s*([-+]?\d+(\.\d+)?)')
    if ($m.Success) { return [double]$m.Groups[1].Value }
    return Get-Num $reply
}
$ppos = Get-PiNum $pi.replies['POS?']
$ptmn = Get-PiNum $pi.replies['TMN?']
$ptmx = Get-PiNum $pi.replies['TMX?']

$anchor = [ordered]@{
    schema       = 'motor_anchor/1'
    timestamp    = (Get-Date).ToString('yyyy-MM-dd HH:mm:ss')
    why          = 'ANCHOR = the hardware position as it was NOW (user 2026-09-17). FIXED across sessions; re-read only when the user says so.'
    rig_state    = 'assembled (as given in the task brief; STATUS.md is the authority)'
    asi          = [ordered]@{
        port = $asi.port; baud = $asi.baud; alias = 'ASI_Piezo / ASRL4::INSTR'
        unit = 'native = 0.1 um (tenth of a micron); 1.0 mm = 10000 units'
        x_units = $ax; y_units = $ay; z_units = $az
        x_mm = $(if ($null -ne $ax) { $ax / 10000.0 } else { $null })
        y_mm = $(if ($null -ne $ay) { $ay / 10000.0 } else { $null })
        z_mm = $(if ($null -ne $az) { $az / 10000.0 } else { $null })
        raw = $asi.replies; error = $asi.error
    }
    pi           = [ordered]@{
        port = $pi.port; baud = $pi.baud; alias = 'PI / ASRL3::INSTR'
        unit = 'native = mm'
        position_mm = $ppos; tmn_mm = $ptmn; tmx_mm = $ptmx
        raw = $pi.replies; error = $pi.error
    }
    envelope     = [ordered]@{
        asi_xy_limit_mm = 1.0; asi_z = 'no limit'; pi_min_mm = 0.0; pi_max_mm = 39.0
    }
}

if (($null -ne $ax) -and ($null -ne $ay) -and ($null -ne $ppos)) {
    $anchor | ConvertTo-Json -Depth 6 | Out-File -FilePath $OutFile -Encoding utf8
    Write-Output "ANCHOR WRITTEN: $OutFile"
    Write-Output ("  ASI x={0} y={1} z={2} units (= {3} / {4} mm)" -f $ax, $ay, $az, ($ax / 10000.0), ($ay / 10000.0))
    Write-Output ("  PI  pos={0} mm  TMN={1}  TMX={2}" -f $ppos, $ptmn, $ptmx)
    exit 0
}
else {
    Write-Output 'ANCHOR NOT WRITTEN: at least one of ASI x, ASI y, PI POS? did not return a number.'
    Write-Output ("  ASI x={0} y={1} z={2}; ASI error='{3}'" -f $ax, $ay, $az, $asi.error)
    Write-Output ("  PI  pos={0}; PI error='{1}'" -f $ppos, $pi.error)
    Write-Output '  (a busy port is recorded as a FACT - nothing is killed and nothing is retried)'
    exit 6
}
