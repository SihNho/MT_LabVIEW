<#
    lv_gui.ps1 — GUI automation helpers for driving LabVIEW on this machine.

    Why this exists: every screenshot/click used to be pasted as a fresh multi-hundred-line
    Add-Type blob. That was slow, repetitive, and impossible to put on a permission allowlist
    (every command string was unique). This script gives those operations a stable, named
    entry point that CAN be allowlisted — see .claude/settings.json.

    ALWAYS invoke it from the project root as:   & .\tools\lv_gui.ps1 -Action <name> ...
    (that exact prefix is what the permission allowlist matches).

    Read CLAUDE.md before using this to touch LabVIEW. In particular: never save an original
    VI, and only act while STATUS.md's labview-lock says `acquired`.

    Actions
      windows                                     list visible LabVIEW window titles
      dialogs                                     find a modal dialog BLOCKING LabVIEW without a
                                                  screenshot: prints every visible window with its
                                                  enabled flag. Exactly one ENABLED while the rest
                                                  are blocked == an open modal, even one hidden
                                                  behind other windows. Run this whenever a COM
                                                  Run/Save/Abort hangs - it is almost always this.
      dismiss                                     post WM_CLOSE to that single blocking dialog.
                                                  Refuses unless the blocked/enabled pattern is
                                                  unambiguous, so it cannot close a VI window.
      focus     -Title <substr>                   bring a LabVIEW window to the foreground
      shot      -Out <png>                        full-screen capture (sees popup menus)
      shotwin   -Title <substr> -Out <png>        single-window capture (misses popup menus)
      shotwin   -Hwnd <n> -Out <png>              same, one exact hwnd (untitled / any process), no focus
      crop      -In <png> -Out <png> -Left -Top -Width -Height [-Scale n]
                                                  magnify a region of an existing capture
      click     -X n -Y n                         left click
      clickprobe -Title <substr> -X n -Y n        DIAGNOSTIC: one click EXACTLY like `click`, with the
                                                  Windows input state read around it, as ONE JSON line.
                                                  Built 2026-09-17 after codex pointed out that `click`
                                                  reports success when its FUNCTION RETURNS, not when a
                                                  control receives the message (mouse_event has no return
                                                  value, Focus discards SetForegroundWindow's, and Windows
                                                  may eat the activating click - MA_ACTIVATEANDEAT):
                                                  archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md
                                                  Records: SetForegroundWindow's RETURN + last error,
                                                  GetForegroundWindow before/after (hwnd+title),
                                                  WindowFromPoint at the click point AND at the real press
                                                  point (x+1,y) with its GA_ROOT, GUITHREADINFO of the
                                                  target's thread (active/focus/capture/menuowner/flags)
                                                  before and after, and whether the target's title or rect
                                                  changed within 500 ms. NO RETRY LOOP - one click, one
                                                  record; gating a retry is the caller's job.
      rclick    -X n -Y n                         right click (LabVIEW menus open on mouse-DOWN)
      dclick    -X n -Y n                         double click
      move      -X n -Y n                         hover only, no click (triggers tooltips)
      wheel     -X n -Y n -Notches n             scroll wheel at X,Y (+ = up, - = down)
      movewin   -Title <substr> [-X -Y -Width -Height]
                                                  move/resize a window on screen. LabVIEW often opens
                                                  diagram windows off-screen; this fixes it reliably
                                                  (title-bar double-click to maximise is not reliable).
      hover     -X n -Y n -Out <png> [-Scale n]  ONE-CALL hover-and-verify: jiggles the cursor,
                                                  waits for LabVIEW's tip strip, captures full
                                                  screen + an auto-zoomed crop around the cursor.
                                                  Use this before EVERY terminal click.
      probe     -X n -Y n -Y2 n                   colour-run scan down a column (or -X2 for a row).
                                                  Finds node terminal rows with no eyeballing.
      wire      -X n -Y n -X2 n -Y2 n             draw a wire: click source, then click dest.
      drag      -X n -Y n -X2 n -Y2 n             press at X,Y, glide to X2,Y2, release. Use for
                                                  rubber-band selection (start on EMPTY canvas).
      key       -Key <name>                       tap a key: enter esc tab delete alt
      keys      -Key <sendkeys>                   arbitrary combo via SendKeys, e.g. "^e" (Ctrl+E),
                                                  "^r" (run), "^c"/"^v", "%f" (Alt+F). Focus first.
      cursor                                      report current cursor position
      md5       -In <file>                        MD5 of a file (original-VI safety checks)

    Notes learned the hard way (2026-08-25) — read these before driving LabVIEW blind:

      - LabVIEW's dialogs render LATE. A capture taken ~500ms after a click can show stale
        state; the Options dialog took >1.5s to appear. Use -WaitMs, and confirm via `windows`
        rather than trusting one screenshot.
      - Popup/dropdown menus are separate top-level windows and do NOT appear in `shotwin`
        (PrintWindow) output. Use `shot` for anything involving a menu.
      - Context menus open on mouse-DOWN, not mouse-up. `rclick` already holds the button
        longer for this reason. To pick an item from one, right-click to open it, then `click`
        the item — do not try to drag-release in one motion.
      - A single click on a just-refocused window often only activates the pane instead of
        hitting what's under the cursor. Space two separate clicks ~500-800ms apart after a
        focus change. Do NOT use a fast double-click as a substitute — LabVIEW reads that as
        its own gesture (e.g. opening a label-edit box on a structure).
      - Reading coordinates off a displayed screenshot by eye is consistently a few pixels off,
        which is enough to miss thin targets. `crop` at high -Scale first and compute the real
        coordinate from the crop origin.
      - Structure BORDERS do not hit-test reliably on a dense diagram — a whole session was lost
        to this (both buttons, several zoom levels, two input APIs, exact border row located by
        pixel sampling). Plain objects (constants, wires) select fine. Build new structures in
        empty canvas instead of trying to select an existing border. See STATUS.md.
      - Prefer VI Scripting over any of the above where the operation is scriptable — it needs
        no coordinates, no waiting, and no visual interpretation. See CLAUDE.md §3.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('windows', 'dialogs', 'dismiss', 'focus', 'activate', 'shot', 'shotwin', 'rect', 'ping', 'crop', 'click', 'clickprobe', 'rclick', 'dclick', 'move', 'movewin', 'hover', 'probe', 'wire', 'drag', 'wheel', 'key', 'keys', 'cursor', 'md5')]
    [string]$Action,

    [int]$X = 0,
    [int]$Y = 0,
    [string]$Out = '',
    [string]$In = '',
    [string]$Title = '',
    [string]$Key = '',
    [int]$Left = 0,
    [int]$Top = 0,
    [int]$Width = 0,
    [int]$Height = 0,
    [int]$Scale = 4,
    [int]$X2 = 0,
    [int]$Notches = 0,
    [string]$Zoom = '',
    [int]$Y2 = 0,
    [int]$WaitMs = 0,
    # shotwin only (card 105-2, 2026-09-27): capture this exact hwnd by PrintWindow(flag 2) - read-only, no focus,
    # works for untitled windows (e.g. a modal LVDChild) and for windows of any process.
    [long]$Hwnd = 0,

    # --- GUI authorization gate (2026-08-31, peer-reviewed design) -------------------------
    # State-changing actions REQUIRE a structured exception + evidence. Free text is not a
    # credential: -Exception must be one of the enum values, -Evidence names the record
    # (skill section, archive/peer file, or approval id). Diagnostic actions pass freely.
    [ValidateSet('', 'VerifiedImpossible', 'NegativeSearch', 'Approved')]
    [string]$Exception = '',
    [string]$Evidence = ''
)

$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

if (-not ('LVGui' -as [type])) {
    Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Text;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Drawing;
using System.Drawing.Imaging;

public class LVGui {
    [DllImport("user32.dll")] public static extern bool EnumWindows(EnumWindowsProc cb, IntPtr p);
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
    [DllImport("user32.dll")] public static extern int GetWindowTextLength(IntPtr h);
    [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
    [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
    [DllImport("user32.dll", SetLastError = true)] public static extern bool SetForegroundWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(POINT p);
    [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr h, uint flags);
    [DllImport("user32.dll")] public static extern bool IsWindow(IntPtr h);
    [DllImport("user32.dll")] public static extern bool GetGUIThreadInfo(uint tid, ref GUITHREADINFO gti);
    [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
    [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
    [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int ht, bool repaint);
    [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags);
    [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT p);
    [DllImport("user32.dll")] public static extern bool IsWindowEnabled(IntPtr h);
    [DllImport("user32.dll")] public static extern IntPtr PostMessage(IntPtr h, uint msg, IntPtr w, IntPtr l);
    [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint idAttach, uint idAttachTo, bool fAttach);
    [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
    [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();

    public delegate bool EnumWindowsProc(IntPtr h, IntPtr p);
    public struct RECT { public int Left, Top, Right, Bottom; }
    public struct POINT { public int X, Y; }

    [StructLayout(LayoutKind.Sequential)]
    public struct GUITHREADINFO {
        public int cbSize;
        public int flags;
        public IntPtr hwndActive, hwndFocus, hwndCapture, hwndMenuOwner, hwndMoveSize, hwndCaret;
        public RECT rcCaret;
    }

    const uint LEFTDOWN = 0x0002, LEFTUP = 0x0004, RIGHTDOWN = 0x0008, RIGHTUP = 0x0010, WHEEL = 0x0800;
    const byte VK_ALT = 0x12;

    // Enumerate visible titled windows. pid 0 = all processes.
    public static List<string> Titles(uint pid) {
        var outp = new List<string>();
        EnumWindows((h, p) => {
            uint wpid; GetWindowThreadProcessId(h, out wpid);
            if ((pid == 0 || wpid == pid) && IsWindowVisible(h)) {
                int n = GetWindowTextLength(h);
                if (n > 0) { var sb = new StringBuilder(n + 1); GetWindowText(h, sb, sb.Capacity); outp.Add(sb.ToString()); }
            }
            return true;
        }, IntPtr.Zero);
        return outp;
    }

    // Every visible window of the process, with its enabled flag. When a modal dialog is up it is
    // the ONLY enabled one and every VI window is disabled - that is how an invisible blocking
    // dialog is found without looking at a screenshot. Format: "enabled|hwnd|l,t,r,b|title".
    public static List<string> WinStates(uint pid) {
        var outp = new List<string>();
        EnumWindows((h, p) => {
            uint wpid; GetWindowThreadProcessId(h, out wpid);
            if ((pid == 0 || wpid == pid) && IsWindowVisible(h)) {
                int n = GetWindowTextLength(h);
                var sb = new StringBuilder(n + 1);
                if (n > 0) GetWindowText(h, sb, sb.Capacity);
                RECT r; GetWindowRect(h, out r);
                outp.Add(string.Format("{0}|{1}|{2},{3},{4},{5}|{6}",
                    IsWindowEnabled(h) ? "ENABLED" : "blocked", h.ToInt64(),
                    r.Left, r.Top, r.Right, r.Bottom, sb.ToString()));
            }
            return true;
        }, IntPtr.Zero);
        return outp;
    }

    public static void CloseWin(IntPtr h) { PostMessage(h, 0x0010, IntPtr.Zero, IntPtr.Zero); }

    public static IntPtr Find(uint pid, string sub) {
        IntPtr hit = IntPtr.Zero;
        EnumWindows((h, p) => {
            uint wpid; GetWindowThreadProcessId(h, out wpid);
            if ((pid == 0 || wpid == pid) && IsWindowVisible(h)) {
                int n = GetWindowTextLength(h);
                if (n > 0) {
                    var sb = new StringBuilder(n + 1); GetWindowText(h, sb, sb.Capacity);
                    if (sb.ToString().Contains(sub)) { hit = h; return false; }
                }
            }
            return true;
        }, IntPtr.Zero);
        return hit;
    }

    // Tapping Alt releases Windows' foreground lock so SetForegroundWindow actually works -
    // but a bare Alt tap also puts LabVIEW's menu bar into keyboard-navigation mode, which eats
    // the next Ctrl-combo as a mnemonic and blocks COM while the menu loop is active
    // (2026-09-01/04). So: tap Alt, focus, then tap Esc to leave menu mode before returning.
    // ⚠️ THAT ESC DISMISSES ANY DIALOG THAT CLOSES ON ESC. Measured 2026-09-23 on LabVIEW's Error
    // List (Ctrl+L): one Focus() call and the window is GONE - `rect`/`shotwin` then report "No
    // LabVIEW window whose title contains 'Error list'". `ClickProbe` below copies this activation
    // and has the same effect. Use `-Action activate` (Activate(), no Alt, no Esc) on such windows.
    public static void Focus(IntPtr h) {
        keybd_event(VK_ALT, 0, 0, UIntPtr.Zero);
        keybd_event(VK_ALT, 0, 2, UIntPtr.Zero);
        ShowWindow(h, 9);
        SetForegroundWindow(h);
        System.Threading.Thread.Sleep(300);
        keybd_event(0x1B, 0, 0, UIntPtr.Zero);   // VK_ESCAPE down
        System.Threading.Thread.Sleep(40);
        keybd_event(0x1B, 0, 2, UIntPtr.Zero);   // VK_ESCAPE up
        System.Threading.Thread.Sleep(150);
    }

    // Activate a window WITHOUT the Alt tap and WITHOUT the Esc tap, for dialogs that close on Esc
    // (added 2026-09-23 after Focus()/ClickProbe() were measured dismissing LabVIEW's Error List).
    // The foreground lock is defeated the documented way instead: attach this thread's input queue
    // to the current foreground window's thread for the duration of the SetForegroundWindow call.
    // Returns one JSON line so the caller can VERIFY rather than trust a void return.
    public static string Activate(IntPtr h) {
        uint dummy;
        IntPtr fgBefore = GetForegroundWindow();
        uint fgTid = (fgBefore == IntPtr.Zero) ? 0 : GetWindowThreadProcessId(fgBefore, out dummy);
        uint myTid = GetCurrentThreadId();
        bool attached = false;
        if (fgTid != 0 && fgTid != myTid) attached = AttachThreadInput(myTid, fgTid, true);
        ShowWindow(h, 9);                       // SW_RESTORE - never minimise, never hide
        BringWindowToTop(h);
        bool sfw = SetForegroundWindow(h);
        int sfwErr = Marshal.GetLastWin32Error();
        System.Threading.Thread.Sleep(250);
        if (attached) AttachThreadInput(myTid, fgTid, false);
        IntPtr fgAfter = GetForegroundWindow();
        return "{\"activate\":" + WinJson(h)
             + ",\"alive\":" + (IsWindow(h) ? "true" : "false")
             + ",\"rect\":" + RectJson(h)
             + ",\"attached\":" + (attached ? "true" : "false")
             + ",\"sfw\":" + (sfw ? "true" : "false") + ",\"sfw_err\":" + sfwErr
             + ",\"fg_before\":" + WinJson(fgBefore)
             + ",\"fg_after\":" + WinJson(fgAfter)
             + ",\"ok\":" + ((fgAfter == h) ? "true" : "false") + "}";
    }

    public static void Tap(byte vk) {
        keybd_event(vk, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(50);
        keybd_event(vk, 0, 2, UIntPtr.Zero);
    }

    // The tiny pre-move + settle is what makes LabVIEW register hover state before the press.
    public static void Click(int x, int y, bool right, bool dbl) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(120);
        SetCursorPos(x + 1, y);
        System.Threading.Thread.Sleep(120);
        uint down = right ? RIGHTDOWN : LEFTDOWN;
        uint up = right ? RIGHTUP : LEFTUP;
        mouse_event(down, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(right ? 150 : 80);
        mouse_event(up, 0, 0, 0, UIntPtr.Zero);
        if (dbl) {
            System.Threading.Thread.Sleep(80);
            mouse_event(down, 0, 0, 0, UIntPtr.Zero);
            System.Threading.Thread.Sleep(60);
            mouse_event(up, 0, 0, 0, UIntPtr.Zero);
        }
    }

    // --- clickprobe: the READER for "was the click DELIVERED?" ----------------------------
    // 2026-09-17. `click` above prints its own arguments back: mouse_event has no return value,
    // so "click 175,353" only ever meant "the function returned". This method performs the SAME
    // click (same pre-move, same dwell, same LEFTDOWN/LEFTUP) and reads the Windows input state
    // around it, so a failed click can be attributed instead of guessed. One click, no retry.
    static string J(string s) {
        if (s == null) return "null";
        var sb = new StringBuilder("\"");
        foreach (char c in s) {
            if (c == '"' || c == '\\') sb.Append('\\').Append(c);
            else if (c == '\n') sb.Append("\\n");
            else if (c == '\r') sb.Append("\\r");
            else if (c == '\t') sb.Append("\\t");
            else if (c < 32) sb.Append("\\u").Append(((int)c).ToString("x4"));
            else sb.Append(c);
        }
        return sb.Append('"').ToString();
    }

    static string TitleOf(IntPtr h) {
        if (h == IntPtr.Zero) return null;
        int n = GetWindowTextLength(h);
        var sb = new StringBuilder(n + 1);
        if (n > 0) GetWindowText(h, sb, sb.Capacity);
        return sb.ToString();
    }

    static string WinJson(IntPtr h) {
        return "{\"hwnd\":" + h.ToInt64() + ",\"title\":" + J(TitleOf(h)) + "}";
    }

    static string RectJson(IntPtr h) {
        RECT r;
        if (h == IntPtr.Zero || !GetWindowRect(h, out r)) return "null";
        return "[" + r.Left + "," + r.Top + "," + r.Right + "," + r.Bottom + "]";
    }

    static string GtiJson(uint tid) {
        var gi = new GUITHREADINFO();
        gi.cbSize = Marshal.SizeOf(typeof(GUITHREADINFO));
        bool ok = GetGUIThreadInfo(tid, ref gi);
        return "{\"ok\":" + (ok ? "true" : "false") + ",\"tid\":" + tid
             + ",\"flags\":" + gi.flags
             + ",\"hwndActive\":" + gi.hwndActive.ToInt64()
             + ",\"hwndFocus\":" + gi.hwndFocus.ToInt64()
             + ",\"hwndCapture\":" + gi.hwndCapture.ToInt64()
             + ",\"hwndMenuOwner\":" + gi.hwndMenuOwner.ToInt64()
             + ",\"hwndMoveSize\":" + gi.hwndMoveSize.ToInt64()
             + ",\"hwndCaret\":" + gi.hwndCaret.ToInt64() + "}";
    }

    static string PointJson(int x, int y, IntPtr target) {
        POINT p; p.X = x; p.Y = y;
        IntPtr w = WindowFromPoint(p);
        IntPtr root = (w == IntPtr.Zero) ? IntPtr.Zero : GetAncestor(w, 2 /*GA_ROOT*/);
        return "{\"x\":" + x + ",\"y\":" + y + ",\"hwnd\":" + w.ToInt64()
             + ",\"title\":" + J(TitleOf(w))
             + ",\"root\":" + root.ToInt64()
             + ",\"root_title\":" + J(TitleOf(root))
             + ",\"is_target\":" + ((w == target) ? "true" : "false")
             + ",\"root_is_target\":" + ((root == target) ? "true" : "false") + "}";
    }

    public static string ClickProbe(IntPtr h, int x, int y) {
        uint pid; uint tid = GetWindowThreadProcessId(h, out pid);
        string title0 = TitleOf(h);
        string rect0 = RectJson(h);
        string fgPre = WinJson(GetForegroundWindow());
        string gtiPre0 = GtiJson(tid);

        // Activate exactly as Focus() does - but KEEP SetForegroundWindow's verdict.
        keybd_event(VK_ALT, 0, 0, UIntPtr.Zero);
        keybd_event(VK_ALT, 0, 2, UIntPtr.Zero);
        ShowWindow(h, 9);
        bool sfw = SetForegroundWindow(h);
        int sfwErr = Marshal.GetLastWin32Error();
        System.Threading.Thread.Sleep(300);
        keybd_event(0x1B, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(40);
        keybd_event(0x1B, 0, 2, UIntPtr.Zero);
        System.Threading.Thread.Sleep(150);
        IntPtr fgAfterSfwH = GetForegroundWindow();
        string fgAfterSfw = WinJson(fgAfterSfwH);
        bool fgIsTarget = (fgAfterSfwH == h);

        // The press point is x+1 because Click() jiggles before pressing - probe BOTH.
        string wfpXY = PointJson(x, y, h);
        string wfpPress = PointJson(x + 1, y, h);
        string gtiPre = GtiJson(tid);

        // ---- the click, identical to Click(x, y, false, false) ----
        var sw = System.Diagnostics.Stopwatch.StartNew();
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(120);
        SetCursorPos(x + 1, y);
        System.Threading.Thread.Sleep(120);
        IntPtr fgAtDownH = GetForegroundWindow();
        mouse_event(LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(80);
        mouse_event(LEFTUP, 0, 0, 0, UIntPtr.Zero);
        long clickMs = sw.ElapsedMilliseconds;

        string gtiPost = GtiJson(tid);
        string fgPost = WinJson(GetForegroundWindow());
        string wfpPost = PointJson(x + 1, y, h);
        System.Threading.Thread.Sleep(500);
        bool alive = IsWindow(h);
        string title1 = alive ? TitleOf(h) : null;
        string rect1 = alive ? RectJson(h) : "null";
        string gtiSettled = GtiJson(tid);

        var o = new StringBuilder();
        o.Append("{\"probe\":\"clickprobe\",\"ts\":").Append(J(DateTime.Now.ToString("yyyy-MM-dd HH:mm:ss.fff")));
        o.Append(",\"target\":{\"hwnd\":").Append(h.ToInt64()).Append(",\"title\":").Append(J(title0));
        o.Append(",\"rect\":").Append(rect0).Append(",\"tid\":").Append(tid).Append(",\"pid\":").Append(pid).Append("}");
        o.Append(",\"click_xy\":[").Append(x).Append(",").Append(y).Append("]");
        o.Append(",\"press_xy\":[").Append(x + 1).Append(",").Append(y).Append("]");
        o.Append(",\"fg_before\":").Append(fgPre);
        o.Append(",\"gti_before_focus\":").Append(gtiPre0);
        o.Append(",\"setforegroundwindow\":{\"ret\":").Append(sfw ? "true" : "false")
         .Append(",\"lasterror\":").Append(sfwErr).Append("}");
        o.Append(",\"fg_after_sfw\":").Append(fgAfterSfw);
        o.Append(",\"fg_after_sfw_is_target\":").Append(fgIsTarget ? "true" : "false");
        o.Append(",\"wfp_click_xy\":").Append(wfpXY);
        o.Append(",\"wfp_press_xy\":").Append(wfpPress);
        o.Append(",\"gti_before_click\":").Append(gtiPre);
        o.Append(",\"fg_at_buttondown\":").Append(WinJson(fgAtDownH));
        o.Append(",\"fg_at_buttondown_is_target\":").Append((fgAtDownH == h) ? "true" : "false");
        o.Append(",\"click_ms\":").Append(clickMs);
        o.Append(",\"gti_after_click\":").Append(gtiPost);
        o.Append(",\"fg_after_click\":").Append(fgPost);
        o.Append(",\"wfp_after_click\":").Append(wfpPost);
        o.Append(",\"after_500ms\":{\"alive\":").Append(alive ? "true" : "false")
         .Append(",\"title\":").Append(J(title1)).Append(",\"rect\":").Append(rect1)
         .Append(",\"title_changed\":").Append((title1 != title0) ? "true" : "false")
         .Append(",\"rect_changed\":").Append((rect1 != rect0) ? "true" : "false")
         .Append(",\"gti\":").Append(gtiSettled).Append("}");
        o.Append("}");
        return o.ToString();
    }

    // Move/resize a window. LabVIEW frequently opens diagram windows partly or wholly
    // off-screen (seen twice on 2026-08-26 at top=915 on a 1080-tall display), and a
    // title-bar double-click to maximise is unreliable. This is deterministic.
    public static string MoveWin(IntPtr h, int x, int y, int w, int ht) {
        MoveWindow(h, x, y, w, ht, true);
        System.Threading.Thread.Sleep(400);
        RECT r; GetWindowRect(h, out r);
        return "moved -> left=" + r.Left + " top=" + r.Top + " right=" + r.Right + " bottom=" + r.Bottom
             + "  -> screen = image + (" + r.Left + "," + r.Top + ")";
    }

    // Wheel scroll. Positive Notches scrolls up/away, negative scrolls down/toward you.
    // Works on whatever is under the cursor, so position first.
    public static void Wheel(int x, int y, int notches) {
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(150);
        for (int i = 0; i < System.Math.Abs(notches); i++) {
            mouse_event(WHEEL, 0, 0, (uint)(notches > 0 ? 120 : -120), UIntPtr.Zero);
            System.Threading.Thread.Sleep(60);
        }
        System.Threading.Thread.Sleep(150);
    }

    // Rubber-band / wire drag. LabVIEW only tracks a drag if it sees intermediate motion
    // between the press and the release, so this glides in steps rather than teleporting.
    public static void Drag(int x1, int y1, int x2, int y2) {
        SetCursorPos(x1, y1);
        System.Threading.Thread.Sleep(150);
        mouse_event(LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(120);
        int steps = 14;
        for (int i = 1; i <= steps; i++) {
            SetCursorPos(x1 + (x2 - x1) * i / steps, y1 + (y2 - y1) * i / steps);
            System.Threading.Thread.Sleep(25);
        }
        System.Threading.Thread.Sleep(150);
        mouse_event(LEFTUP, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(150);
    }

    // --- Composite actions -------------------------------------------------
    // These exist because the 2026-08-26 benchmark showed the COST IS ROUND-TRIPS, not
    // model skill: the hover-verify loop took 3-4 calls, so agents skipped it to save
    // budget, and skipping it is precisely what made wiring fail. Each of these collapses
    // a whole loop into one call.

    // Hover with the two-step jiggle + settle that LabVIEW needs to raise a tip strip,
    // then capture full screen AND an auto-zoomed crop around the cursor.
    public static string Hover(int x, int y, string path, string zoomPath, int scale, int sw, int sh) {
        SetCursorPos(x - 40, y - 30);
        System.Threading.Thread.Sleep(250);
        SetCursorPos(x, y);
        System.Threading.Thread.Sleep(2200);
        ShotScreen(path, sw, sh);
        int cw = 340, ch = 150;
        int ox = x - 150; if (ox < 0) ox = 0;
        int oy = y - 60;  if (oy < 0) oy = 0;
        if (ox + cw > sw) cw = sw - ox;
        if (oy + ch > sh) ch = sh - oy;
        using (var src = new Bitmap(path))
        using (var dst = new Bitmap(cw * scale, ch * scale)) {
            using (var g = Graphics.FromImage(dst)) {
                g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor;
                g.PixelOffsetMode = System.Drawing.Drawing2D.PixelOffsetMode.Half;
                g.DrawImage(src, new Rectangle(0, 0, cw * scale, ch * scale),
                                 new Rectangle(ox, oy, cw, ch), GraphicsUnit.Pixel);
            }
            dst.Save(zoomPath, ImageFormat.Png);
        }
        return "hovered " + x + "," + y + " | zoom origin " + ox + "," + oy + " scale " + scale
             + "  -> real = origin + crop_px/" + scale;
    }

    // Sample a 1-pixel line and report runs of constant colour. This finds node terminals
    // WITHOUT any visual interpretation: with the wiring tool engaged LabVIEW paints each
    // terminal as a distinctly coloured dot, so a colour scan down a node's left edge
    // reports every terminal row exactly.
    public static string Probe(int x1, int y1, int x2, int y2) {
        bool col = (x2 == x1 || x2 == 0);
        int n = col ? (y2 - y1 + 1) : (x2 - x1 + 1);
        if (n < 2) return "(probe needs a range: give -X -Y -Y2 for a column, or -X -Y -X2 for a row)";
        var sb = new StringBuilder();
        sb.AppendLine(col ? ("column x=" + x1 + " from y=" + y1 + " to " + y2)
                          : ("row y=" + y1 + " from x=" + x1 + " to " + x2));
        using (var bmp = new Bitmap(col ? 1 : n, col ? n : 1))
        using (var g = Graphics.FromImage(bmp)) {
            g.CopyFromScreen(x1, y1, 0, 0, new Size(col ? 1 : n, col ? n : 1));
            Color prev = col ? bmp.GetPixel(0, 0) : bmp.GetPixel(0, 0);
            int start = col ? y1 : x1;
            for (int i = 1; i < n; i++) {
                Color c = col ? bmp.GetPixel(0, i) : bmp.GetPixel(i, 0);
                if (c.ToArgb() != prev.ToArgb()) {
                    int end = (col ? y1 : x1) + i - 1;
                    sb.AppendLine("  " + start + "-" + end + "  (" + (end - start + 1) + "px)  #"
                        + prev.R.ToString("X2") + prev.G.ToString("X2") + prev.B.ToString("X2"));
                    prev = c; start = (col ? y1 : x1) + i;
                }
            }
            int last = col ? y2 : x2;
            sb.AppendLine("  " + start + "-" + last + "  (" + (last - start + 1) + "px)  #"
                + prev.R.ToString("X2") + prev.G.ToString("X2") + prev.B.ToString("X2"));
        }
        return sb.ToString();
    }

    // LabVIEW wiring is click-source then click-destination (NOT a drag).
    // The destination click must APPROACH the terminal first (so LabVIEW snaps/highlights it)
    // and must NOT use Click()'s +1px jiggle, which can nudge off a small terminal and leave
    // the wire dangling in rubber-band mode. That failure was silent - probe read all white
    // while a pending wire was actually in flight - so the timings here are deliberate.
    public static void Wire(int x1, int y1, int x2, int y2) {
        SetCursorPos(x1 - 20, y1);
        System.Threading.Thread.Sleep(200);
        SetCursorPos(x1, y1);
        System.Threading.Thread.Sleep(400);          // let LabVIEW arm the wiring tool on the source
        mouse_event(LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(90);
        mouse_event(LEFTUP, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(600);
        SetCursorPos((x1 + x2) / 2, (y1 + y2) / 2);  // drag the rubber band across
        System.Threading.Thread.Sleep(250);
        SetCursorPos(x2 - 12, y2);
        System.Threading.Thread.Sleep(250);
        SetCursorPos(x2, y2);
        System.Threading.Thread.Sleep(500);          // settle ON the destination terminal
        mouse_event(LEFTDOWN, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(90);
        mouse_event(LEFTUP, 0, 0, 0, UIntPtr.Zero);
        System.Threading.Thread.Sleep(600);
    }

    public static void Move(int x, int y) { SetCursorPos(x, y); System.Threading.Thread.Sleep(150); }

    public static string Cursor() { POINT p; GetCursorPos(out p); return p.X + "," + p.Y; }

    public static void ShotScreen(string path, int w, int h) {
        using (var bmp = new Bitmap(w, h)) {
            using (var g = Graphics.FromImage(bmp)) { g.CopyFromScreen(0, 0, 0, 0, new Size(w, h)); }
            bmp.Save(path, ImageFormat.Png);
        }
    }

    // UI responsiveness probe: SendMessageTimeout(WM_NULL) measures how long the window's thread
    // takes to service a message - the direct metric behind "(응답 없음)". 2026-09-06.
    [DllImport("user32.dll", CharSet = CharSet.Auto)]
    public static extern IntPtr SendMessageTimeout(IntPtr h, uint msg, IntPtr w, IntPtr l, uint flags, uint timeoutMs, out IntPtr result);
    public static string Ping(IntPtr h, uint timeoutMs) {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        IntPtr res;
        IntPtr ok = SendMessageTimeout(h, 0x0000, IntPtr.Zero, IntPtr.Zero, 0x0002 /*SMTO_ABORTIFHUNG*/, timeoutMs, out res);
        sw.Stop();
        return (ok == IntPtr.Zero ? "HUNG" : "ok") + " " + sw.ElapsedMilliseconds + "ms";
    }

    // Window rect without a capture (for tools/lvclick.py viewport calibration).
    public static string Rect(IntPtr h) {
        RECT r; GetWindowRect(h, out r);
        return "left=" + r.Left + " top=" + r.Top + " right=" + r.Right + " bottom=" + r.Bottom;
    }

    public static string ShotWindow(IntPtr h, string path) {
        RECT r; GetWindowRect(h, out r);
        int w = r.Right - r.Left, ht = r.Bottom - r.Top;
        using (var bmp = new Bitmap(w, ht)) {
            using (var g = Graphics.FromImage(bmp)) {
                IntPtr hdc = g.GetHdc();
                PrintWindow(h, hdc, 2);
                g.ReleaseHdc(hdc);
            }
            bmp.Save(path, ImageFormat.Png);
        }
        // Self-describing on purpose: a bare "23,41,1019,569" was misread as width/height
        // during the 2026-08-26 benchmark and cost real round-trips. Screen = image + (left, top).
        return "left=" + r.Left + " top=" + r.Top + " right=" + r.Right + " bottom=" + r.Bottom
             + " (w=" + w + " h=" + ht + ")  -> screen = image + (" + r.Left + "," + r.Top + ")";
    }
}
'@
}

function Get-LVPid {
    $p = Get-Process -Name LabVIEW -ErrorAction SilentlyContinue
    if (-not $p) { throw "LabVIEW is not running." }
    return [uint32]$p.Id
}

# Enabled windows that could be a blocking modal. Floating palettes (Context Help, the Functions
# and Controls palettes, Quick Drop, Search) stay enabled while a modal is up, so they must be
# excluded or every verdict reads "ambiguous"; so must the zero-size bookkeeping windows.
$script:FloatingTitles = @('Context Help', 'Functions', 'Controls', 'Tools Palette',
                           'Quick Drop', 'Search Palettes', 'Navigation Window')
function Get-DialogCandidates([string[]]$rows) {
    $rows | Where-Object { $_ -like 'ENABLED|*' } | Where-Object {
        $p = $_ -split '\|'
        $r = $p[2] -split ','
        $w = [int]$r[2] - [int]$r[0]; $h = [int]$r[3] - [int]$r[1]
        # 2026-09-14 23:1x (peer: archive/peer/2026-09-14-wiresr-test-fail1-watchdog-modal.md): a VI's OWN editor
        # window is never a modal dialog. With only the palette denylist, "one blocked FP + the VI's just-opened BD"
        # matched the modal signature and 'dismiss' WM_CLOSEd a Block Diagram mid-scripting-op (build_opwiresr_v0.log).
        ($w -gt 0 -and $h -gt 0) -and ($script:FloatingTitles -notcontains $p[3]) -and
        ($p[3] -notlike '* Block Diagram') -and ($p[3] -notlike '* Front Panel') -and ($p[3] -notlike '*.vi')
    }
}

function Resolve-Out([string]$p) {
    if ([string]::IsNullOrWhiteSpace($p)) { throw "-Out is required for action '$Action'." }
    $dir = Split-Path -Parent $p
    if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force $dir | Out-Null }
    if ([System.IO.Path]::IsPathRooted($p)) { return $p }
    return (Join-Path (Get-Location).Path $p)
}

if ($WaitMs -gt 0) { Start-Sleep -Milliseconds $WaitMs }

# --- authorization gate -------------------------------------------------------------------
# 'clickprobe' IS state-changing - it really clicks - so it passes the SAME gate as 'click' and is
# logged the same way. Being a diagnostic does not exempt it (2026-09-17).
# 'activate' changes the z-order and the input focus, so it passes the same gate and is logged -
# being the *gentler* way to front a window does not make it a diagnostic (added 2026-09-23).
$stateChanging = @('click','clickprobe','rclick','dclick','drag','wire','keys','key','activate')
if ($stateChanging -contains $Action) {
    $diagnosticKey = ($Action -eq 'key' -and $Key -in @('esc','escape'))
    if (-not $diagnosticKey) {
        if (-not $Exception -or -not $Evidence) {
            Write-Output "REFUSED: state-changing GUI action '$Action' requires -Exception (VerifiedImpossible|NegativeSearch|Approved) and -Evidence <record>. Rule: GUI only where scripting is VERIFIED unreachable (CLAUDE.md 3)."
            exit 9
        }
        $logLine = "{0}`t{1}`t{2}`t{3}`tX={4},Y={5},X2={6},Y2={7},Key={8}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $Action, $Exception, $Evidence, $X, $Y, $X2, $Y2, $Key
        Add-Content -Path (Join-Path $PSScriptRoot 'gui_actions.log') -Value $logLine -Encoding utf8
    }
}

switch ($Action) {

    'windows' {
        $titles = [LVGui]::Titles((Get-LVPid))
        if ($titles.Count -eq 0) { Write-Output "(LabVIEW running, no titled visible windows)" }
        else { $titles | ForEach-Object { Write-Output $_ } }
    }

    'dialogs' {
        # Find a modal dialog that is blocking LabVIEW, WITHOUT a screenshot. A blocked VI window
        # plus exactly one enabled non-floating window == an open modal, possibly hidden behind
        # other windows.
        $rows = [LVGui]::WinStates((Get-LVPid))
        $rows | ForEach-Object { Write-Output $_ }
        $cand = @(Get-DialogCandidates $rows)
        $blocked = @($rows | Where-Object { $_ -like 'blocked|*' })
        if ($blocked.Count -gt 0 -and $cand.Count -eq 1) {
            Write-Output "VERDICT: BLOCKED by 1 modal dialog -> run '-Action dismiss'"
        } elseif ($blocked.Count -eq 0) {
            Write-Output "VERDICT: clear (no modal dialog)"
        } else {
            Write-Output "VERDICT: ambiguous ($($cand.Count) dialog candidates, $($blocked.Count) blocked) - inspect before dismissing"
        }
    }

    'dismiss' {
        # Post WM_CLOSE to the single blocking dialog. Refuses unless the pattern is unambiguous,
        # so it can never close a VI window by accident.
        $rows = [LVGui]::WinStates((Get-LVPid))
        $cand = @(Get-DialogCandidates $rows)
        $blocked = @($rows | Where-Object { $_ -like 'blocked|*' })
        if ($blocked.Count -eq 0) { throw "Nothing is blocked; there is no modal dialog to dismiss." }
        if ($cand.Count -ne 1) { throw "$($cand.Count) dialog candidates - not unambiguous. Run '-Action dialogs' and handle it manually." }
        $parts = $cand[0] -split '\|'
        [LVGui]::CloseWin([IntPtr][int64]$parts[1])
        Write-Output "posted WM_CLOSE to $($parts[1]) rect=$($parts[2]) title='$($parts[3])'"
    }

    'focus' {
        if (-not $Title) { throw "-Title is required for 'focus'." }
        $h = [LVGui]::Find((Get-LVPid), $Title)
        if ($h -eq [IntPtr]::Zero) { throw "No LabVIEW window whose title contains '$Title'." }
        [LVGui]::Focus($h)
        Write-Output "focused: $Title"
    }

    'activate' {
        # Front a window WITHOUT the Alt tap and WITHOUT the Esc tap that 'focus' and 'clickprobe'
        # both send - the only safe way to front a dialog that CLOSES ON ESC (LabVIEW's Error List).
        # Prints one JSON line carrying the measured foreground, so the caller verifies by effect.
        if (-not $Title) { throw "-Title is required for 'activate'." }
        $h = [LVGui]::Find((Get-LVPid), $Title)
        if ($h -eq [IntPtr]::Zero) { throw "No LabVIEW window whose title contains '$Title'." }
        Write-Output ([LVGui]::Activate($h))
    }

    'shot' {
        $path = Resolve-Out $Out
        $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        [LVGui]::ShotScreen($path, $b.Width, $b.Height)
        Write-Output "saved $path ($($b.Width)x$($b.Height))"
    }

    'shotwin' {
        if ($Hwnd -ne 0) {
            $path = Resolve-Out $Out
            $h = [IntPtr]$Hwnd
            if (-not [LVGui]::IsWindow($h)) { throw "No window with hwnd $Hwnd." }
            $rect = [LVGui]::ShotWindow($h, $path)
            Write-Output "saved $path (hwnd $Hwnd, window rect $rect)"
            break
        }
        if (-not $Title) { throw "-Title or -Hwnd is required for 'shotwin'." }
        $path = Resolve-Out $Out
        $h = [LVGui]::Find((Get-LVPid), $Title)
        if ($h -eq [IntPtr]::Zero) { throw "No LabVIEW window whose title contains '$Title'." }
        $rect = [LVGui]::ShotWindow($h, $path)
        Write-Output "saved $path (window rect $rect)"
    }

    'crop' {
        if (-not $In) { throw "-In is required for 'crop'." }
        if ($Width -le 0 -or $Height -le 0) { throw "-Width and -Height must be positive." }
        $path = Resolve-Out $Out
        $src = [System.Drawing.Image]::FromFile((Resolve-Path $In).Path)
        try {
            $dw = $Width * $Scale
            $dh = $Height * $Scale
            $bmp = New-Object System.Drawing.Bitmap($dw, $dh)
            $g = [System.Drawing.Graphics]::FromImage($bmp)
            try {
                # NearestNeighbor keeps 1px LabVIEW wires and terminals crisp when magnified.
                $g.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
                $g.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::Half
                $dst = New-Object System.Drawing.Rectangle(0, 0, $dw, $dh)
                $srcRect = New-Object System.Drawing.Rectangle($Left, $Top, $Width, $Height)
                $g.DrawImage($src, $dst, $srcRect, [System.Drawing.GraphicsUnit]::Pixel)
            } finally { $g.Dispose() }
            $bmp.Save($path, [System.Drawing.Imaging.ImageFormat]::Png)
            $bmp.Dispose()
        } finally { $src.Dispose() }
        Write-Output "saved $path (${Width}x${Height} at $Left,$Top magnified ${Scale}x)"
    }

    'click'  { [LVGui]::Click($X, $Y, $false, $false); Write-Output "click $X,$Y" }

    'clickprobe' {
        if (-not $Title) { throw "-Title is required for 'clickprobe' (the window the click is MEANT for)." }
        $h = [LVGui]::Find((Get-LVPid), $Title)
        if ($h -eq [IntPtr]::Zero) { throw "No LabVIEW window whose title contains '$Title'." }
        Write-Output ([LVGui]::ClickProbe($h, $X, $Y))
    }

    'rclick' { [LVGui]::Click($X, $Y, $true,  $false); Write-Output "rclick $X,$Y" }
    'dclick' { [LVGui]::Click($X, $Y, $false, $true);  Write-Output "dclick $X,$Y" }
    'move'   { [LVGui]::Move($X, $Y);                  Write-Output "move $X,$Y" }

    'wheel' {
        [LVGui]::Wheel($X, $Y, $Notches)
        if ($WaitMs -gt 0) { Start-Sleep -Milliseconds $WaitMs }
        Write-Output "wheel $Notches at $X,$Y"
    }

    'movewin' {
        if (-not $Title) { throw "-Title is required for 'movewin'." }
        $h = [LVGui]::Find((Get-LVPid), $Title)
        if ($h -eq [IntPtr]::Zero) { throw "No LabVIEW window matching '$Title'." }
        $wx = if ($Width  -gt 0) { $Width  } else { 1900 }
        $wy = if ($Height -gt 0) { $Height } else { 1000 }
        Write-Output ([LVGui]::MoveWin($h, $X, $Y, $wx, $wy))
    }

    'hover' {
        if (-not $Out) { throw "-Out <png> is required for 'hover'." }
        $zoom = if ($Zoom) { $Zoom } else { [IO.Path]::Combine([IO.Path]::GetDirectoryName($Out), [IO.Path]::GetFileNameWithoutExtension($Out) + "_zoom.png") }
        $sc = if ($Scale -gt 0) { $Scale } else { 4 }
        $b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
        Write-Output ([LVGui]::Hover($X, $Y, $Out, $zoom, $sc, $b.Width, $b.Height))
        Write-Output "full: $Out"
        Write-Output "zoom: $zoom"
    }

    'probe' {
        Write-Output ([LVGui]::Probe($X, $Y, $X2, $Y2))
    }

    'wire' {
        [LVGui]::Wire($X, $Y, $X2, $Y2)
        Write-Output "wire $X,$Y -> $X2,$Y2"
    }

    'drag' {
        [LVGui]::Drag($X, $Y, $X2, $Y2)
        if ($WaitMs -gt 0) { Start-Sleep -Milliseconds $WaitMs }
        Write-Output "drag $X,$Y -> $X2,$Y2"
    }

    'key' {
        # apps = the dedicated context-menu key (VK_APPS): opens the right-click menu of the
        # current selection - the reliable fallback when an injected right-click opens nothing.
        $codes = @{ enter = 0x0D; esc = 0x1B; escape = 0x1B; tab = 0x09; delete = 0x2E; del = 0x2E; alt = 0x12; apps = 0x5D; f10 = 0x79 }
        $k = $Key.ToLower()
        if (-not $codes.ContainsKey($k)) { throw "Unknown -Key '$Key'. Known: $($codes.Keys -join ', ')" }
        [LVGui]::Tap([byte]$codes[$k])
        Write-Output "key $k"
    }

    'keys' {
        if (-not $Key) { throw "-Key is required for 'keys' (SendKeys syntax, e.g. '^e')." }
        [System.Windows.Forms.SendKeys]::SendWait($Key)
        if ($WaitMs -gt 0) { Start-Sleep -Milliseconds $WaitMs }
        Write-Output "keys $Key"
    }

    'cursor' { Write-Output ([LVGui]::Cursor()) }

    'ping' {
        # Responsiveness of every visible LabVIEW window (or one -Title): "ok <ms>" / "HUNG".
        $pid_ = Get-LVPid
        $rows = [LVGui]::WinStates($pid_)
        foreach ($r in $rows) {
            $parts = $r -split '\|', 4
            $t = $parts[3]
            if ($Title -and ($t -notlike "*$Title*")) { continue }
            $h = [IntPtr]::new([int64]$parts[1])
            Write-Output ("{0}  {1}" -f ([LVGui]::Ping($h, 3000)), $t)
        }
    }

    'rect' {
        if (-not $Title) { throw "-Title is required for 'rect'." }
        $h = [LVGui]::Find((Get-LVPid), $Title)
        if ($h -eq [IntPtr]::Zero) { throw "No LabVIEW window whose title contains '$Title'." }
        Write-Output ([LVGui]::Rect($h))
    }

    'md5' {
        if (-not $In) { throw "-In is required for 'md5'." }
        $h = Get-FileHash -Algorithm MD5 -LiteralPath $In
        Write-Output "$($h.Hash.ToLower())  $($h.Path)"
    }
}
