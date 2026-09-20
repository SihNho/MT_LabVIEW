# p2_pi_softlimit_test.ps1 - USER-ORDERED live test (2026-09-18, user present: "40 넣어보면 확실하겠네").
# Sets the C-863.11's OWN soft limits in RAM (SPA 1 0x15 39.0 / SPA 1 0x30 0.0 - volatile, gone at power-cycle),
# verifies TMX?/TMN? read them back, and ONLY THEN sends MOV 1 40 expecting the controller to REFUSE it (ERR? 7,
# POS? unchanged). If TMX? does not read 39, no MOV is sent. No WPA (nothing persisted). One run, one port open.
param([string]$Port = 'COM3', [int]$Baud = 115200, [double]$Hi = 39.0, [double]$Lo = 0.0)
$ErrorActionPreference = 'Stop'
$sp = New-Object System.IO.Ports.SerialPort $Port, $Baud, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = 600; $sp.NewLine = "`n"
function Ask([string]$q) { $sp.DiscardInBuffer(); $sp.WriteLine($q); try { return $sp.ReadLine().Trim() } catch { return '' } }
function Num([string]$r) { if ($r -match '=\s*([-+0-9.eE]+)') { return [double]$Matches[1] } return $null }
$sp.Open()
try {
    Write-Output ("IDN  : {0}" -f (Ask '*IDN?'))
    Write-Output ("HLP has SPA: {0}" -f ((Ask 'HLP?') -match 'SPA'))
    Write-Output ("BEFORE POS?={0} TMN?={1} TMX?={2} SPA?0x15={3} SPA?0x30={4} ERR?={5}" -f (Ask 'POS?'), (Ask 'TMN?'), (Ask 'TMX?'), (Ask 'SPA? 1 0x15'), (Ask 'SPA? 1 0x30'), (Ask 'ERR?'))
    $sp.WriteLine(("SPA 1 0x15 {0}" -f $Hi)); Start-Sleep -Milliseconds 200
    $sp.WriteLine(("SPA 1 0x30 {0}" -f $Lo)); Start-Sleep -Milliseconds 200
    $err = Ask 'ERR?'
    $tmx = Num (Ask 'TMX?'); $tmn = Num (Ask 'TMN?')
    Write-Output ("AFTER SPA: ERR?={0} TMN?={1} TMX?={2} SPA?0x15={3} SPA?0x30={4}" -f $err, $tmn, $tmx, (Ask 'SPA? 1 0x15'), (Ask 'SPA? 1 0x30'))
    if ($null -eq $tmx -or [math]::Abs($tmx - $Hi) -gt 0.001) { Write-Output "ABORT: TMX? did not read $Hi - MOV 1 40 NOT sent"; exit 7 }
    $p0 = Num (Ask 'POS?')
    $sp.WriteLine('MOV 1 40'); Start-Sleep -Milliseconds 500
    $e1 = Ask 'ERR?'
    Start-Sleep -Seconds 2
    $p1 = Num (Ask 'POS?')
    Write-Output ("MOV 1 40 -> ERR?={0} (7 = PI_CNTR_POS_OUT_OF_LIMITS expected)  POS before={1} after={2}" -f $e1, $p0, $p1)
    if ($e1 -eq '7' -and [math]::Abs($p1 - $p0) -lt 0.01) { Write-Output "RESULT: REFUSED by the controller, axis did not move"; exit 0 }
    if ([math]::Abs($p1 - $p0) -ge 0.01) { $sp.WriteLine('HLT'); Write-Output "RESULT: AXIS MOVED - HLT sent"; exit 8 }
    Write-Output "RESULT: unexpected (ERR $e1, no motion)"; exit 9
}
finally { if ($sp.IsOpen) { $sp.Close() }; $sp.Dispose() }
