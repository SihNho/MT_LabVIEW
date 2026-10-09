# ---
# labview: none
# hardware: none
# ---
# Start a Claude-GPT discussion (rounds mode) on a topic file, DETACHED through WMI so an app restart does not kill it.
# Usage (from the project root):
#   powershell -NoProfile -File tools/debate_start.ps1 -Slug <short-name> -Topic <topic .md file>
#   powershell -NoProfile -File tools/debate_start.ps1 -Slug <short-name> -Worker      (internal: the detached part)
# Writes tools/bench/debate/<slug>/ (topic.md copy, relay/, run.log). Prints the Google Doc link when it appears.
# ASCII only: Windows PowerShell 5.1 reads this file without a BOM. Guide: docs/debate.md
param([Parameter(Mandatory = $true)][string]$Slug, [string]$Topic = '', [switch]$Worker, [switch]$Stub)
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
$d = Join-Path 'tools\bench\debate' $Slug
if ($Worker) {
    $env:PYTHONPATH = Join-Path $env:USERPROFILE 'AppData\Local\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python310\site-packages'
    $env:GOOGLE_OAUTH_CLIENT_FILE = Join-Path $env:USERPROFILE '.config\debate\client_secret.json'
    $env:PYTHONIOENCODING = 'utf-8'
    $extra = @(); if ($Stub) { $extra = @('--stub', '--stub-secs', '3') }   # -Stub: launch-path test, no model calls
    py -W ignore -u tools\debate_gdoc.py run --mode rounds --topic "$d\topic.md" --dir "$d\relay" --poll 10 @extra *> "$d\run.log"
    exit $LASTEXITCODE
}
if (-not (Test-Path $Topic)) { Write-Output "topic file not found: $Topic"; exit 2 }
if (Test-Path "$d\relay\state.json") { Write-Output "slug '$Slug' already has a discussion; pick a new slug"; exit 2 }
New-Item -ItemType Directory -Force $d | Out-Null
Copy-Item $Topic "$d\topic.md" -Force
# the GPT side reads the code base from its own worktree: bring it to the latest commit first
$wt = Join-Path (Split-Path -Parent $root) 'V6_debate'
if (-not (Test-Path $wt)) { git worktree add --detach $wt HEAD 2>&1 | Out-Null } else { git -C $wt checkout --detach master 2>&1 | Out-Null }
$self = $MyInvocation.MyCommand.Path
$r = Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{
    CommandLine = "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File `"$self`" -Slug $Slug -Worker$(if ($Stub) { ' -Stub' })"
    CurrentDirectory = $root }
Write-Output "started (wmi rc=$($r.ReturnValue)) dir=$d"
for ($i = 0; $i -lt 30; $i++) {
    Start-Sleep -Seconds 1
    $l = Get-Content "$d\run.log" -Encoding Unicode -ErrorAction SilentlyContinue | Where-Object { $_ -match '^(DOC|ERROR)' } | Select-Object -First 1
    if ($l) { Write-Output $l; break }
}
