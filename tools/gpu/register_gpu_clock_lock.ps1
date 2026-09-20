# register_gpu_clock_lock.ps1 - run ONCE from an elevated PowerShell: creates a logon task (highest privileges) that re-applies
# the SM clock lock after every reboot, because `nvidia-smi -lgc` does not persist. (RTX 2060: memory clock lock unsupported.)
$action = New-ScheduledTaskAction -Execute "C:\Windows\System32\nvidia-smi.exe" -Argument "-lgc 1365,1905"
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive -RunLevel Highest
Register-ScheduledTask -TaskName "GPU clock lock (LabVIEW tracking)" -Action $action -Trigger $trigger -Principal $principal -Force
Write-Output "registered: nvidia-smi -lgc 1365,1905 at logon (highest privileges). Remove with: Unregister-ScheduledTask -TaskName 'GPU clock lock (LabVIEW tracking)'"
