# query-only: RON? FRF? SVO? POS? TMN? TMX? ERR? VEL? on COM3 - no motion, no settings written
$sp = New-Object System.IO.Ports.SerialPort 'COM3', 115200, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = 600; $sp.NewLine = "`n"; $sp.Open()
function Ask([string]$q) { $sp.DiscardInBuffer(); $sp.WriteLine($q); try { return $sp.ReadLine().Trim() } catch { return '' } }
foreach ($q in 'RON?', 'FRF?', 'SVO?', 'POS?', 'TMN?', 'TMX?', 'ERR?', 'VEL?') { Write-Output ("{0,-5} {1}" -f $q, (Ask $q)) }
$sp.Close(); $sp.Dispose()
