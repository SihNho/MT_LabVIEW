# p2_pi_softlimit_test2.ps1 - discriminating step after test 1 returned ERR 5 (servo off / unreferenced) instead of
# the expected 7 (out of limits). Reads SVO?/FRF?; if the servo is off, switches it ON (SVO 1 1 - configuration,
# no motion); re-reads TMN?/TMX? (must still be 0/39 or abort); then sends MOV 1 40 again expecting ERR 7 and no
# motion. Then sends MOV 1 38.5 (inside the window, inside the user's envelope) expecting motion, then MOV 1 0 back.
param([string]$Port = 'COM3', [int]$Baud = 115200)
$ErrorActionPreference = 'Stop'
$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = 600; $sp.NewLine = "`n"
function Ask([string]$q) { $sp.DiscardInBuffer(); $sp.WriteLine($q); try { return $sp.ReadLine().Trim() } catch { return '' } }
function Num([string]$r) { if ($r -match '=\s*([-+0-9.eE]+)') { return [double]$Matches[1] } return $null }
function Settle([double]$target, [int]$maxS) {
    $t0 = Get-Date; $last = $null; $still = 0
    while (((Get-Date) - $t0).TotalSeconds -lt $maxS) {
        Start-Sleep -Milliseconds 400; $p = Num (Ask 'POS?')
        if ($null -eq $p) { continue }
        if ($p -gt 39.5) { $sp.WriteLine('HLT'); Write-Output "HALT: $p"; return $p }
        if ($null -ne $last -and [math]::Abs($p - $last) -lt 0.0005) { $still++ } else { $still = 0 }
        $last = $p; if ($still -ge 3) { break }
    }
    return $last
}
$sp.Open()
try {
    Write-Output ("state: SVO?={0} FRF?={1} ERR?={2} POS?={3} TMN?={4} TMX?={5}" -f (Ask 'SVO?'), (Ask 'FRF?'), (Ask 'ERR?'), (Ask 'POS?'), (Ask 'TMN?'), (Ask 'TMX?'))
    if ((Ask 'SVO?') -match '=0') { $sp.WriteLine('SVO 1 1'); Start-Sleep -Milliseconds 300; Write-Output ("SVO 1 1 sent -> SVO?={0} ERR?={1}" -f (Ask 'SVO?'), (Ask 'ERR?')) }
    if ((Ask 'FRF?') -notmatch '=1') { Write-Output 'ABORT: axis not referenced - no move attempted'; exit 7 }
    $tmx = Num (Ask 'TMX?'); if ($null -eq $tmx -or [math]::Abs($tmx - 39.0) -gt 0.001) { Write-Output "ABORT: TMX?=$tmx not 39 - no move attempted"; exit 7 }
    $p0 = Num (Ask 'POS?')
    $sp.WriteLine('MOV 1 40'); Start-Sleep -Milliseconds 500; $e1 = Ask 'ERR?'; Start-Sleep -Seconds 2; $p1 = Num (Ask 'POS?')
    Write-Output ("MOV 1 40   -> ERR?={0} (expect 7)  POS {1} -> {2}" -f $e1, $p0, $p1)
    if ([math]::Abs($p1 - $p0) -ge 0.01) { $sp.WriteLine('HLT'); Write-Output 'RESULT: AXIS MOVED on 40 - HLT'; exit 8 }
    $sp.WriteLine('MOV 1 38.5'); $e2 = Ask 'ERR?'; $p2 = Settle 38.5 30
    Write-Output ("MOV 1 38.5 -> ERR?={0} (expect 0)  settled POS={1} (expect 38.5)" -f $e2, $p2)
    $sp.WriteLine('MOV 1 0'); $e3 = Ask 'ERR?'; $p3 = Settle 0 30
    Write-Output ("MOV 1 0    -> ERR?={0}  settled POS={1}" -f $e3, $p3)
    if ($e1 -eq '7' -and $null -ne $p2 -and [math]::Abs($p2 - 38.5) -lt 0.01 -and [math]::Abs($p3) -lt 0.01) { Write-Output 'RESULT: controller soft limit CONFIRMED (40 refused with 7, 38.5 moved, back at 0)'; exit 0 }
    Write-Output 'RESULT: see lines above'; exit 9
}
finally { if ($sp.IsOpen) { $sp.Close() }; $sp.Dispose() }
