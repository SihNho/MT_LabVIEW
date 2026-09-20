# serial_roundtrip_asi.ps1 - measure one serial round trip to the ASI TG-1000 stage controller, WITHOUT moving anything.
#
# WHY THIS EXISTS. The per-frame budget table in docs/camera-acquisition-facts.md carries one number that is an
# EXTRAPOLATION rather than a measurement: "one serial round trip = 2.56 ms". That figure was measured on the PI motor
# (COM3, GCS queries). The serial path that sits on the frame loop is the ASI stage on COM4, and it is a different
# animal in three ways that all affect latency:
#   * a different controller and protocol (ASI Tiger TG-1000, not PI GCS);
#   * the LabVIEW driver's `Send Serial Command.vi` serialises the port with a NAMED SEMAPHORE, so two callers block
#     each other - the relevant cost is not always one exchange;
#   * it reads by BYTE COUNT rather than by termination character, so a reply shorter than requested blocks until the
#     VISA timeout (5000 ms default per Mercury_comm.vi's help) instead of returning early.
# Measuring it replaces the extrapolation with a fact, and the frame-loop analysis already showed this path is paid
# only while a focus key is held - so what this quantifies is the size of the intermittent spike, not a constant cost.
#
# SAFETY - the reason this file ships DISARMED.
# This controller drives a microscope stage on a rig that CLAUDE.md rule 1b singles out as able to physically break
# itself. A command that looks like a query but isn't would be unrecoverable, so:
#
#   * `$SAFE` is EMPTY until an external source confirms each command is strictly query-only. The script REFUSES to
#     transmit while it is empty. Fill it only from the archived peer answer
#     (archive/peer/2026-09-12-asi-tiger-readonly-commands.md), never from memory or guesswork.
#   * `$FORBIDDEN` is checked against every command before it is sent, as a second independent gate: any command whose
#     text contains a blacklisted token aborts the whole run rather than that one command.
#   * DTR and RTS are left at the .NET defaults (deasserted) so opening the port cannot reset or home a device.
#   * The port is closed in a finally block so LabVIEW can claim it afterwards.
#
# Usage (only after $SAFE is filled in):
#   & .\tools\bench\serial_roundtrip_asi.ps1 -Port COM4 -Baud 115200 -Count 50
param(
    [string]$Port = 'COM4',            # COM4 = ASI on the Sunix card; COM3 is PI (docs/motion-path-audit.md)
    [int]$Baud = 115200,
    [int]$Count = 50,
    [int]$ReadTimeoutMs = 500,
    [switch]$IUnderstandTheRisk
)

# ARMED with exactly ONE command, from the archived external confirmation
# (archive/peer/2026-09-12-asi-tiger-readonly-commands.md, codex, 2026-09-12).
#
# `/` is STATUS. It returns `B` if anything addressed is busy and `N` otherwise - no motion, no settings change, no
# flash write. It was chosen over WHERE / BUILD / VERSION for a second reason that matters on THIS rig: its reply data
# is exactly one character, so the total frame is 3 bytes (`B|N` + CR + LF). Every other candidate has a
# variable-length reply, and the LabVIEW driver here reads by BYTE COUNT rather than by terminator - a short reply
# would block until the VISA timeout. Fixed length removes that failure mode from the measurement.
#
# Deliberately NOT whitelisted even though they are read-only: `WHERE`/`W`, `BUILD`/`BU`, `VERSION`/`V`, `RDSBYTE`/`RB`
# (variable-length replies), and `INFO`, `WHO`, `CDATE`, `RDSTAT` (informational but unnecessary - unconfirmed stays
# forbidden). Note `BU` is only safe in its bare form: `BU Y=#`, `BU Y-`, `BU Z=#`, `BU Z+`, `BU Z-` all WRITE, and
# `BU Y` data can then be saved to flash. That is exactly the "looks like a query, isn't" trap this gate exists for.
$SAFE = @('/')

# Never send anything containing these. Expanded 2026-09-12 from the peer answer - the first draft of this list was
# missing RESET (~), SPIN (@), MULTIMV (MM), VECTOR (VE), SCAN (SN/NR/NV), SETHOME (HM), AZERO (AZ), MOTCTRL (MC) and
# SAVEPOS (SP). SAVEPOS is the worst of them: bare `SP` halts the axes, writes positions to flash, and leaves the
# controller unresponsive until it is power-cycled.
$FORBIDDEN = @(
    'MOVE', 'MOVREL', 'SPIN', '@', 'MULTIMV', 'MM', 'VECTOR', 'VE', 'SCAN', 'SN', 'NR', 'NV',   # motion
    'HOME', '!', 'ZERO', 'HERE', 'SETHOME', 'HM', 'AZERO', 'AZ',                                # homing / origin
    'HALT', '\',                                                                                # stops actuators
    'SAVESET', 'SS', 'SAVEPOS', 'SP', 'SAVE',                                                   # persists to flash
    'RESET', '~', 'MOTCTRL', 'MC',                                                              # reset / motor enable
    'M ', 'R ', 'H ', 'Z ',                                                                     # single-letter forms
    'SPEED', 'ACCEL', 'SETLOW', 'SETUP', 'AA', 'CUSTOM', 'LOAD', 'UNLOAD', '=')                 # anything that writes

Write-Output "port=$Port baud=$Baud count=$Count readTimeout=${ReadTimeoutMs}ms"

if ($SAFE.Count -eq 0) {
    Write-Output ''
    Write-Output 'REFUSING TO TRANSMIT: the safe-command list is empty.'
    Write-Output 'This is the designed state, not a bug. Fill $SAFE only from the archived external confirmation'
    Write-Output '  archive/peer/2026-09-12-asi-tiger-readonly-commands.md'
    Write-Output 'and only with commands that source states are strictly query-only for a TG-1000. Nothing is sent'
    Write-Output 'to a stage controller on this rig on the strength of a remembered command set.'
    exit 2
}
foreach ($cmd in $SAFE) {
    foreach ($bad in $FORBIDDEN) {
        if ($cmd.ToUpper().Contains($bad.ToUpper())) {
            Write-Output "ABORT: command '$cmd' contains blacklisted token '$bad'."
            exit 3
        }
    }
}
if (-not $IUnderstandTheRisk) {
    Write-Output 'Pass -IUnderstandTheRisk to actually transmit. (Second gate: the list being filled is not consent.)'
    exit 4
}

Write-Output "safe query set: $($SAFE -join ', ')"
$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = $ReadTimeoutMs
$sp.WriteTimeout = 1000
$sp.NewLine = "`r"                     # TG-1000 terminator - CONFIRM against the peer answer before trusting this
try {
    $sp.Open()
    Write-Output "opened $Port"
    Start-Sleep -Milliseconds 200
    $sp.DiscardInBuffer(); $sp.DiscardOutBuffer()

    foreach ($cmd in $SAFE) {
        $times = New-Object System.Collections.Generic.List[double]
        $replies = 0; $timeouts = 0; $sample = ''
        for ($i = 0; $i -lt $Count; $i++) {
            $sp.DiscardInBuffer()
            $sw = [System.Diagnostics.Stopwatch]::StartNew()
            try {
                $sp.WriteLine($cmd)
                $line = $sp.ReadLine()
                $sw.Stop()
                $times.Add($sw.Elapsed.TotalMilliseconds)
                $replies++
                if ($sample -eq '') { $sample = ($line -replace '[^\x20-\x7e]', '.') }
            } catch {
                $sw.Stop(); $timeouts++
            }
            Start-Sleep -Milliseconds 5
        }
        if ($replies -gt 0) {
            $sorted = $times | Sort-Object
            $med = $sorted[[int]($sorted.Count / 2)]
            $p90 = $sorted[[int]($sorted.Count * 0.9)]
            Write-Output ("{0,-8} replies {1,3}/{2}  timeouts {3,3}  median {4,7:N3} ms  min {5,7:N3}  p90 {6,7:N3}  max {7,7:N3}  reply '{8}'" -f `
                    $cmd, $replies, $Count, $timeouts, $med, $sorted[0], $p90, $sorted[-1], $sample)
        }
        else {
            Write-Output ("{0,-8} NO REPLY in {1} attempts - wrong baud, wrong terminator, or wrong port" -f $cmd, $Count)
        }
    }
}
finally {
    if ($sp.IsOpen) { $sp.Close() }
    Write-Output "closed $Port"
}
