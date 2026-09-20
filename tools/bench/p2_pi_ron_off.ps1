# p2_pi_ron_off.ps1 - restore the ORIGINAL VI's own operating mode (Autoreference? = 0): reference mode OFF and the
# current physical position DEFINED as 0 (RON 1 0 ; POS 1 0). Configuration only - no motion. Prints state after.
$sp = New-Object System.IO.Ports.SerialPort 'COM3', 115200, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = 600; $sp.NewLine = "`n"; $sp.Open()
function Ask([string]$q) { $sp.DiscardInBuffer(); $sp.WriteLine($q); try { return $sp.ReadLine().Trim() } catch { return '' } }
Write-Output ("before: RON?={0} FRF?={1} POS?={2}" -f (Ask 'RON?'), (Ask 'FRF?'), (Ask 'POS?'))
$sp.WriteLine('RON 1 0'); Start-Sleep -Milliseconds 300
Write-Output ("RON 1 0 -> RON?={0} ERR?={1}" -f (Ask 'RON?'), (Ask 'ERR?'))
$sp.WriteLine('POS 1 0'); Start-Sleep -Milliseconds 300
Write-Output ("POS 1 0 -> POS?={0} FRF?={1} ERR?={2} TMN?={3} TMX?={4}" -f (Ask 'POS?'), (Ask 'FRF?'), (Ask 'ERR?'), (Ask 'TMN?'), (Ask 'TMX?'))
$sp.Close(); $sp.Dispose()
