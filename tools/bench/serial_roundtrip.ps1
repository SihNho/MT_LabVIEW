# serial_roundtrip.ps1 - measure one serial query round trip to the PI motor controller, WITHOUT moving anything.
#
# Why: every latency number in docs/motion-path-audit.md so far is arithmetic, not measurement. At 115200 the wire time
# for a ~20-byte exchange is about 1.7 ms and the Sunix RX FIFO trigger adds about 0.35 ms, but the controller's own
# turnaround is unknown and decides whether host-side tuning is worth anything at all.
#
# SAFETY, non-negotiable:
#   * ONLY read-only GCS queries are ever transmitted - see $SAFE below. No MOV, no GOH, no VEL, no SVO, nothing that
#     actuates. The motor cannot move in response to anything this script sends.
#   * ONLY the port given by -Port is opened (COM3 = the PI motor per docs/MAIN_VI_MAP.md). The ASI stage's port is
#     never touched; the piezo is a forbidden instrument.
#   * Handshake lines are left at the .NET defaults (DTR and RTS deasserted) so opening the port cannot reset a device.
#   * The port is closed in a finally block even if the run throws, so LabVIEW can claim it afterwards.
#
# Usage: & .\tools\bench\serial_roundtrip.ps1 -Port COM3 -Baud 115200 -Count 50
param(
    [string]$Port = 'COM3',
    [int]$Baud = 115200,
    [int]$Count = 50,
    [int]$ReadTimeoutMs = 500
)

$SAFE = @('*IDN?', 'POS?', 'ERR?', 'TMN?', 'TMX?')     # read-only queries only

Write-Output "port=$Port baud=$Baud count=$Count readTimeout=${ReadTimeoutMs}ms"
Write-Output "safe query set: $($SAFE -join ', ')"

$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = $ReadTimeoutMs
$sp.WriteTimeout = 1000
$sp.NewLine = "`n"
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
            } catch [TimeoutException] {
                $sw.Stop(); $timeouts++
            } catch {
                $sw.Stop(); $timeouts++
            }
            Start-Sleep -Milliseconds 5
        }
        if ($replies -gt 0) {
            $sorted = $times | Sort-Object
            $med = $sorted[[int]($sorted.Count / 2)]
            $min = $sorted[0]; $max = $sorted[$sorted.Count - 1]
            $p95 = $sorted[[int]([Math]::Floor($sorted.Count * 0.95))]
            Write-Output ("{0,-6} replies {1}/{2}  median {3:N2} ms  min {4:N2}  p95 {5:N2}  max {6:N2}  sample reply: '{7}'" -f `
                $cmd, $replies, $Count, $med, $min, $p95, $max, $sample)
        } else {
            Write-Output ("{0,-6} NO REPLY in {1} attempts (all timed out at {2} ms)" -f $cmd, $Count, $ReadTimeoutMs)
        }
    }
} catch {
    Write-Output "ERROR: $($_.Exception.Message)"
} finally {
    if ($sp.IsOpen) { $sp.Close() }
    $sp.Dispose()
    Write-Output "closed $Port"
}
