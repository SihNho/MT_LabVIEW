# query-only: ASI current position and the controller's software limits (SL/SU) on COM4 - no motion, nothing set
$sp = New-Object System.IO.Ports.SerialPort 'COM4', 115200, ([System.IO.Ports.Parity]::None), 8, ([System.IO.Ports.StopBits]::One)
$sp.ReadTimeout = 800; $sp.NewLine = "`r"; $sp.Open()
function Ask([string]$q) { $sp.DiscardInBuffer(); $sp.WriteLine($q); try { return $sp.ReadLine().Trim() } catch { return '(no reply)' } }
foreach ($q in 'W X', 'W Y', 'W Z', 'SL X? Y? Z?', 'SU X? Y? Z?', 'UM X? Y? Z?', 'BU X', 'V') { Write-Output ("{0,-12} {1}" -f $q, (Ask $q)) }
$sp.Close(); $sp.Dispose()
