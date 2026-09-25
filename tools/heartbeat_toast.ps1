# heartbeat_toast.ps1 - Windows toast for the cycle runner's HEARTBEAT (card chat-H1, 2026-09-25).
# Launched DETACHED by tools/cycle_runner.py (never waited on). Text arrives in env HB_TITLE / HB_BODY so no quoting
# survives into a command line. BurntToast when installed, else the WinRT toast API under PowerShell's own AppId.
# No Add-Type, no window, no mouse/keyboard - it only shows a notification.
$ErrorActionPreference = 'SilentlyContinue'
$title = $env:HB_TITLE; if (-not $title) { $title = 'cycle runner' }
$body = $env:HB_BODY; if (-not $body) { $body = '' }
if (Get-Module -ListAvailable -Name BurntToast) {
    Import-Module BurntToast
    New-BurntToastNotification -Text $title, $body
    exit 0
}
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
$esc = { param($s) [System.Security.SecurityElement]::Escape($s) }
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml("<toast><visual><binding template='ToastGeneric'><text>$(& $esc $title)</text><text>$(& $esc $body)</text></binding></visual></toast>")
$appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show([Windows.UI.Notifications.ToastNotification]::new($xml))
