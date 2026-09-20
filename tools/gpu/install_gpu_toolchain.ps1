# install_gpu_toolchain.ps1 - ONE elevated run (one UAC prompt) that installs, silently and without rebooting:
#   1. NVIDIA GeForce driver 616.64 (display driver only)            C:\Users\KimLab\Downloads\nvidia_616.64\
#   2. Visual Studio 2022 Build Tools, C++ workload (MSVC 14.x)       C:\Users\KimLab\Downloads\gpu_toolchain\vs_BuildTools.exe
#   3. CUDA Toolkit 12.6.3 (nvcc, runtime, cuFFT/cuBLAS + dev, NVRTC, VS integration; NO driver, NO Nsight)
# Approved by the user 2026-09-07 ("dll 만들기 위한 권한을 허가할테니"). Logs: C:\Users\KimLab\Downloads\gpu_toolchain\log\
# Run:  powershell -ExecutionPolicy Bypass -File tools\gpu\install_gpu_toolchain.ps1   (it re-launches itself elevated)
$ErrorActionPreference = 'Continue'
$root = 'C:\Users\KimLab\Downloads\gpu_toolchain'
$log = Join-Path $root 'log'; New-Item -ItemType Directory -Force $log | Out-Null
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) { Start-Process powershell -Verb RunAs -ArgumentList @('-ExecutionPolicy', 'Bypass', '-File', $PSCommandPath); exit }
Start-Transcript -Path (Join-Path $log 'toolchain_transcript.txt') -Append | Out-Null
function Step($name, $exe, $argv) {
    "=== $name : $exe $argv   ($(Get-Date -Format 'HH:mm:ss'))" | Tee-Object -FilePath (Join-Path $log 'steps.txt') -Append
    $p = Start-Process -FilePath $exe -ArgumentList $argv -Wait -PassThru
    "=== $name exit $($p.ExitCode)   ($(Get-Date -Format 'HH:mm:ss'))" | Tee-Object -FilePath (Join-Path $log 'steps.txt') -Append
    return $p.ExitCode
}
# 1. driver (skip if already >= 616)
$drv = (Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' }).DriverVersion
"current NVIDIA driver: $drv" | Tee-Object -FilePath (Join-Path $log 'steps.txt') -Append
$nvexe = 'C:\Users\KimLab\Downloads\nvidia_616.64\616.64-desktop-win10-win11-64bit-international-dch-whql.exe'
if ($drv -notmatch '^32\.0\.16\.' -and (Test-Path $nvexe)) {
    $sig = Get-AuthenticodeSignature $nvexe
    if ($sig.Status -eq 'Valid' -and $sig.SignerCertificate.Subject -match 'NVIDIA Corporation') {
        Step 'driver 616.64' $nvexe @('-s', '-n', 'Display.Driver', "-log:$log\nvidia", '-loglevel:6')
    } else { "driver installer signature NOT valid ($($sig.Status)) - skipped" | Tee-Object -FilePath (Join-Path $log 'steps.txt') -Append }
}
# 2. VS Build Tools (C++ workload)
$vs = Join-Path $root 'vs_BuildTools.exe'
Step 'VS Build Tools' $vs @('--quiet', '--wait', '--norestart', '--nocache', '--add', 'Microsoft.VisualStudio.Workload.VCTools', '--includeRecommended')
# 3. CUDA Toolkit 12.6.3 (no driver)
$cuda = Join-Path $root 'cuda_12.6.3_561.17_windows.exe'
Step 'CUDA 12.6.3' $cuda @('-s', '-n', 'nvcc_12.6', 'cudart_12.6', 'cufft_12.6', 'cufft_dev_12.6', 'cublas_12.6', 'cublas_dev_12.6', 'nvrtc_12.6', 'nvrtc_dev_12.6', 'thrust_12.6', 'cuobjdump_12.6', 'nvdisasm_12.6', 'visual_studio_integration_12.6', 'nvml_dev_12.6')
"driver after: $((Get-CimInstance Win32_VideoController | Where-Object { $_.Name -match 'NVIDIA' }).DriverVersion)" | Tee-Object -FilePath (Join-Path $log 'steps.txt') -Append
"nvcc: $(Test-Path 'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6\bin\nvcc.exe')  cl: $(Get-ChildItem 'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\*\bin\Hostx64\x64\cl.exe' -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty FullName)" | Tee-Object -FilePath (Join-Path $log 'steps.txt') -Append
"ALL DONE $(Get-Date -Format 'HH:mm:ss')" | Tee-Object -FilePath (Join-Path $log 'steps.txt') -Append
Stop-Transcript | Out-Null
