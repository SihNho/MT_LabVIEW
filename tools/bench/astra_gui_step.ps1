param([string]$Action,[int]$X,[int]$Y,[int]$X2,[int]$Y2,[string]$Key,[string]$Title,[int]$Width,[int]$Height)
$ErrorActionPreference='Stop'
$p=@{Action=$Action;Exception='Approved';Evidence='User-authorized Astra direct GUI benchmark 2026-09-13'}
foreach($k in @('X','Y','X2','Y2','Key','Title','Width','Height')) {if($PSBoundParameters.ContainsKey($k)) {$p[$k]=$PSBoundParameters[$k]}}
if ($Action -ne 'observe') { & .\tools\lv_gui.ps1 @p }
& .\tools\lv_gui.ps1 -Action shot -Out .\tools\bench\astra_gui_screen.png
