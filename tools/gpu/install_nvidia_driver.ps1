# install_nvidia_driver.ps1 - installs GeForce Game Ready 616.64 WHQL (downloaded + Authenticode-verified 2026-09-07)
# silently, display driver only, NO reboot. Needs elevation: right-click > "Run with PowerShell" and accept the UAC prompt,
# or from an admin PowerShell:  powershell -ExecutionPolicy Bypass -File tools\gpu\install_nvidia_driver.ps1
$d = 'C:\Users\KimLab\Downloads\nvidia_616.64'
$f = Join-Path $d '616.64-desktop-win10-win11-64bit-international-dch-whql.exe'
if (-not (Test-Path $f)) { throw "installer missing: $f (re-download: https://us.download.nvidia.com/Windows/616.64/616.64-desktop-win10-win11-64bit-international-dch-whql.exe)" }
$sig = Get-AuthenticodeSignature $f
if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch 'NVIDIA Corporation') { throw "signature check failed: $($sig.Status)" }
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Start-Process powershell -Verb RunAs -ArgumentList @('-ExecutionPolicy','Bypass','-File',$PSCommandPath); exit }
New-Item -ItemType Directory -Force (Join-Path $d 'log') | Out-Null
$p = Start-Process -FilePath $f -ArgumentList @('-s','-n','Display.Driver',"-log:$d\log",'-loglevel:6') -Wait -PassThru
"installer exit code: $($p.ExitCode)  (0 = ok, 1 = ok but reboot needed)"
Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' } | Select-Object Name,DriverVersion | Format-List
Read-Host 'done - press Enter'
