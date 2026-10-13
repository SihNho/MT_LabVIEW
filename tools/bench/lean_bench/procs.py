# ---
# labview: none
# hardware: none
# ---
"""procs - list python/LabVIEW processes with parent pid and command line (read-only)."""
import subprocess
ps = ("Get-CimInstance Win32_Process | Where-Object { $_.Name -match 'python|py.exe|LabVIEW' } | "
      "ForEach-Object { '{0} {1} {2}' -f $_.ProcessId, $_.ParentProcessId, $_.CommandLine }")
print(subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True, errors="replace").stdout)
