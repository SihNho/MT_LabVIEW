# p2_asi_set_limits.ps1 - USER-ORDERED 2026-09-18 ("지금 값을 기준으로 +- 2mm 넣어줘"): write ASI controller software
# limits (SL/SU, mm, ABSOLUTE coordinates, persistent across power cycles) at the current X/Y +-2 mm. Z untouched.
# Reads the position first, computes the window from the LIVE reading, writes, reads back. No motion command.
# Undo: SL X=-500 Y=-500 ; SU X=500 Y=500 (the values read on 2026-09-18 14:5x before this change).
param([double]$HalfMm = 2.0)
$sp = New-Object System.IO.Ports.SerialPort 'COM4', 115200, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = 800; $sp.NewLine = "`r"; $sp.Open()
function Ask([string]$q) { $sp.DiscardInBuffer(); $sp.WriteLine($q); try { return $sp.ReadLine().Trim() } catch { return '(no reply)' } }
function Where1([string]$a) { $r = Ask "W $a"; if ($r -match ':A\s+(-?\d+(?:\.\d+)?)') { return [double]$Matches[1] } return $null }
try {
    $x = Where1 'X'; $y = Where1 'Y'
    if ($null -eq $x -or $null -eq $y) { Write-Output 'ABORT: position read failed'; exit 6 }
    $xm = $x / 10000.0; $ym = $y / 10000.0
    Write-Output ("current X={0:n4} Y={1:n4} mm   old SL: {2}   old SU: {3}" -f $xm, $ym, (Ask 'SL X? Y?'), (Ask 'SU X? Y?'))
    $slx = $xm - $HalfMm; $sly = $ym - $HalfMm; $sux = $xm + $HalfMm; $suy = $ym + $HalfMm
    $c1 = ("SL X={0:n4} Y={1:n4}" -f $slx, $sly); $c2 = ("SU X={0:n4} Y={1:n4}" -f $sux, $suy)
    Write-Output ("{0} -> {1}" -f $c1, (Ask $c1))
    Write-Output ("{0} -> {1}" -f $c2, (Ask $c2))
    Write-Output ("readback SL: {0}" -f (Ask 'SL X? Y?'))
    Write-Output ("readback SU: {0}" -f (Ask 'SU X? Y?'))
    Write-Output ("position after (must be unchanged): X={0} Y={1}" -f (Where1 'X'), (Where1 'Y'))
}
finally { $sp.Close(); $sp.Dispose() }
