r"""lv_errorlist - read EVERY item of LabVIEW's Error List window for a BROKEN VI. READ-ONLY.

docs/connectivity-map-plan.md STEP 2, Pre-decided 138: "Errors of a broken VI are read from the GUI
Error List, keyboard-opened, every item (scrolling if capture), count-checked; COM cannot list them
(`VI.Get Errors` absent from the exported interface, 2026-09-18)."

WHAT ALREADY EXISTS (checked before a line was written - `grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`, `grep -i "error ?list|OCR|pywinauto"`):
  * NOTHING reads the Error List. No prior art at all: the string "Error List" appears in
    `.claude/skills/.../gui-recipes.md` only as the run-button trap warning.
  * `gscript.gui_save()` (tools/gscript.py:2022) holds the PROVEN keystroke idiom this file reuses
    verbatim in `_focus_vi_window()`: focus by title -> title-bar `clickprobe` -> believe the
    keystroke ONLY when the MEASURED foreground carries that title -> Esc afterwards.
  * `gscript._lv_gui()` (:282) is the single dispatcher to `tools/lv_gui.ps1`; its args are quoted.
  * `tools/lv_gui.ps1` gate (:631): `keys` is state-changing and needs -Exception + -Evidence, which
    is logged to `tools/gui_actions.log`; `-Action key -Key esc` is the ONE diagnostic exemption.

METHOD (the brief's order):
  (A) UI AUTOMATION.  comtypes + UIAutomationCore.  LabVIEW ships no native UIA provider, but the
      MSAA->UIA bridge surfaces whatever LabVIEW exposes through IAccessible, so whether the list
      items are visible AT ALL is a MEASUREMENT, printed as `uia_items_exposed` in the JSON.
      Items are read from the tree, so scroll position cannot hide one.
  (B) CAPTURE + OCR, which is what actually works.  MEASURED 2026-09-23 (run 1,
      `tools/bench/errorlist_test.log`): the Error List is FULLY owner-drawn - 0 win32 children, a
      7-element UIA tree holding only the title-bar chrome, 1 MSAA object (the window itself), 0
      rows by either route.  So the capture IS the measurement.  `shotwin` PNG -> LOCATE the panels
      on that capture by colour (dialog grey vs panel; LabVIEW's selection blue #0078E5) -> OCR.
      Engine, measured per row against the known truth on the bed's own capture:
        * Windows.Media.Ocr (winsdk; the only installed recognizer language is 'ko'):
          "lnvoke NOde", "connected tO anythinq", "Wire hA<KO>" - 3/41, 37/39, 56/60, 0/25 chars.
        * rapidocr-onnxruntime (PP-OCR English): every row verbatim - "Block Diagram Errors",
          "This wire connects one or more data sinks but has no source.", "Wire: Wire has loose
          ends", and the count line "14 errors and warnings".
      RapidOCR is therefore the engine; winsdk stays as the no-model-files fallback and reports
      itself as unreliable for Latin.  If neither is installed the captures are still written and
      `fallback_ocr` says "unavailable" - the text is never silently dropped.

EVERY GUI ACT IS capture -> locate -> act -> capture -> confirm (pinned rule, STATUS line 12):
  * locate = the window is found by TITLE through lv_gui's LabVIEW-pid-scoped Find, and the
    foreground is MEASURED with `clickprobe` before any keystroke; no remembered coordinate is
    ever clicked (the only click this file makes is on a title bar whose rect was just read).
  * confirm = Ctrl+L is believed only when a NEW top-level window appears; each {DOWN} is believed
    only when the UIA selection or the detail text CHANGES; Esc is believed only when the window is
    gone.  Every act is recorded in the returned dict under "gui_acts".

THE VI IS NEVER RUN AND NEVER SAVED.  Nothing here calls Run, Save or any mutator; the only COM this
module touches is `gscript.open_panel` to put the VI in memory, and every COM call happens BEFORE the
Error List is up (an open LabVIEW dialog blocks COM - skill com-driving.md).
"""
import ctypes
import hashlib
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import gscript as g                                                                # noqa: E402

BENCH = os.path.join(HERE, "bench")
SHOTS = os.path.join(BENCH, "errorlist_shots")
EVIDENCE = "user 2026-09-23 error list via GUI"
ERRWIN_RE = re.compile(r"error\s*list", re.I)

# UIA pattern ids (uiautomationcore.h) - named, never inlined.
PAT_VALUE, PAT_SELECTIONITEM, PAT_SELECTION, PAT_TEXT, PAT_LEGACY = 10002, 10010, 10001, 10014, 10018
CT = {50000: "Button", 50003: "ComboBox", 50004: "Edit", 50005: "Hyperlink", 50006: "Image",
      50007: "ListItem", 50008: "List", 50009: "Menu", 50011: "MenuItem", 50018: "ScrollBar",
      50019: "Slider", 50020: "Text", 50021: "ToolBar", 50022: "ToolTip", 50023: "Tree",
      50024: "TreeItem", 50025: "Custom", 50026: "Group", 50027: "Thumb", 50028: "DataGrid",
      50029: "DataItem", 50030: "Document", 50031: "SplitButton", 50032: "Window", 50033: "Pane",
      50036: "Table"}
LISTISH = (50008, 50023, 50028, 50036)          # List, Tree, DataGrid, Table
ITEMISH = (50007, 50024, 50029)                 # ListItem, TreeItem, DataItem
TEXTISH = (50020, 50004, 50030)                 # Text, Edit, Document


# ---------------------------------------------------------------- win32 window census (read-only)
def lv_pid():
    import win32process
    import win32gui
    pids = set()

    def cb(h, _):
        if win32gui.IsWindowVisible(h):
            try:
                pids.add(win32process.GetWindowThreadProcessId(h)[1])
            except Exception:                                                      # noqa: BLE001
                pass
    win32gui.EnumWindows(cb, None)
    import subprocess
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe", "/FO", "CSV", "/NH"],
                         capture_output=True, text=True, timeout=30).stdout
    m = re.findall(r'"LabVIEW\.exe","(\d+)"', out)
    return int(m[0]) if m else None


def top_windows(pid=None):
    """[(hwnd, title, class, (l,t,r,b))] for every visible top-level window (of `pid` if given)."""
    import win32gui
    import win32process
    rows = []

    def cb(h, _):
        if not win32gui.IsWindowVisible(h):
            return
        try:
            p = win32process.GetWindowThreadProcessId(h)[1]
        except Exception:                                                          # noqa: BLE001
            return
        if pid and p != pid:
            return
        rows.append((h, win32gui.GetWindowText(h), win32gui.GetClassName(h),
                     win32gui.GetWindowRect(h)))
    win32gui.EnumWindows(cb, None)
    return rows


def child_windows(hwnd):
    """Win32 CHILD hwnds - the measurement of whether the dialog is owner-drawn (no children)."""
    import win32gui
    kids = []

    def cb(h, _):
        try:
            kids.append((h, win32gui.GetClassName(h), win32gui.GetWindowText(h),
                         win32gui.GetWindowRect(h)))
        except Exception:                                                          # noqa: BLE001
            pass
        return True
    try:
        win32gui.EnumChildWindows(hwnd, cb, None)
    except Exception:                                                              # noqa: BLE001
        pass
    return kids


# ---------------------------------------------------------------- UI Automation (method A)
class UIA(object):
    def __init__(self):
        import comtypes.client as cc
        import pythoncom
        pythoncom.CoInitialize()
        self.mod = cc.GetModule("UIAutomationCore.dll")
        self.u = cc.CreateObject(self.mod.CUIAutomation, interface=self.mod.IUIAutomation)
        self.walker = self.u.RawViewWalker

    def from_hwnd(self, hwnd):
        return self.u.ElementFromHandle(ctypes.c_void_p(int(hwnd)))

    def focused(self):
        try:
            return self.u.GetFocusedElement()
        except Exception:                                                          # noqa: BLE001
            return None

    def _pat(self, el, pid_, iface):
        try:
            p = el.GetCurrentPattern(pid_)
            return p.QueryInterface(getattr(self.mod, iface)) if p else None
        except Exception:                                                          # noqa: BLE001
            return None

    def value(self, el):
        p = self._pat(el, PAT_VALUE, "IUIAutomationValuePattern")
        try:
            return p.CurrentValue if p else None
        except Exception:                                                          # noqa: BLE001
            return None

    def text(self, el):
        p = self._pat(el, PAT_TEXT, "IUIAutomationTextPattern")
        try:
            return p.DocumentRange.GetText(-1) if p else None
        except Exception:                                                          # noqa: BLE001
            return None

    def legacy(self, el):
        p = self._pat(el, PAT_LEGACY, "IUIAutomationLegacyIAccessiblePattern")
        if not p:
            return None
        out = {}
        for k in ("CurrentName", "CurrentValue", "CurrentRole", "CurrentState", "CurrentChildId",
                  "CurrentDefaultAction", "CurrentDescription"):
            try:
                out[k[7:].lower()] = getattr(p, k)
            except Exception:                                                      # noqa: BLE001
                out[k[7:].lower()] = None
        return out

    def selected(self, el):
        p = self._pat(el, PAT_SELECTIONITEM, "IUIAutomationSelectionItemPattern")
        try:
            return bool(p.CurrentIsSelected) if p else None
        except Exception:                                                          # noqa: BLE001
            return None

    def select(self, el):
        p = self._pat(el, PAT_SELECTIONITEM, "IUIAutomationSelectionItemPattern")
        if not p:
            return False
        p.Select()
        return True

    def set_focus(self, el):
        try:
            el.SetFocus()
            return True
        except Exception:                                                          # noqa: BLE001
            return False

    def node(self, el):
        """One element as a plain dict - everything we can read about it."""
        def s(fn, d=None):
            try:
                return fn()
            except Exception:                                                      # noqa: BLE001
                return d
        r = s(lambda: el.CurrentBoundingRectangle)
        ct = s(lambda: int(el.CurrentControlType), 0)
        return {"name": s(lambda: el.CurrentName), "class": s(lambda: el.CurrentClassName),
                "ct": ct, "ct_name": CT.get(ct, str(ct)),
                "aid": s(lambda: el.CurrentAutomationId),
                "rect": [r.left, r.top, r.right, r.bottom] if r else None,
                "offscreen": s(lambda: bool(el.CurrentIsOffscreen)),
                "value": self.value(el), "text": self.text(el), "legacy": self.legacy(el),
                "selected": self.selected(el)}

    def tree(self, el, depth=0, maxdepth=14, out=None, path="0"):
        """Full RawView tree as a flat list of dicts with a path - scroll cannot hide a row."""
        out = [] if out is None else out
        d = self.node(el)
        d["depth"], d["path"] = depth, path
        d["_el"] = el
        out.append(d)
        if depth >= maxdepth:
            return out
        try:
            c = self.walker.GetFirstChildElement(el)
        except Exception:                                                          # noqa: BLE001
            return out
        i = 0
        while c and i < 400:
            self.tree(c, depth + 1, maxdepth, out, "{0}.{1}".format(path, i))
            try:
                c = self.walker.GetNextSiblingElement(c)
            except Exception:                                                      # noqa: BLE001
                break
            i += 1
        return out


# ---------------------------------------------------------------- MSAA / IAccessible (route A2)
# An owner-drawn list often exposes its rows as IAccessible CHILD IDs of ONE object, which the
# MSAA->UIA bridge does NOT surface as separate UIA elements. So the UIA tree returning 0 items is
# not yet evidence that the rows are unreadable - this route asks oleacc directly, per hwnd.
MSAA_ROLE = {33: "list", 34: "listitem", 35: "outline", 36: "outlineitem", 41: "statictext",
             42: "text", 43: "pushbutton", 10: "window", 9: "client", 8: "pane"}


def msaa_rows(hwnd, max_children=400):
    """[{childid, name, value, role, role_name, state, rect}] for hwnd's client object. [] if none."""
    from ctypes import POINTER, byref, oledll
    import comtypes.client as cc
    mod = cc.GetModule("oleacc.dll")
    IAcc = mod.IAccessible
    p = POINTER(IAcc)()
    try:
        oledll.oleacc.AccessibleObjectFromWindow(int(hwnd), 0xFFFFFFFC, byref(IAcc._iid_), byref(p))
    except Exception:                                                              # noqa: BLE001
        return []
    if not p:
        return []
    out = []

    def one(acc, cid):
        def s(fn, d=None):
            try:
                return fn()
            except Exception:                                                      # noqa: BLE001
                return d
        role = s(lambda: int(acc.accRole(cid)), -1)
        r = s(lambda: acc.accLocation(cid))
        return {"childid": cid, "name": s(lambda: acc.accName(cid)),
                "value": s(lambda: acc.accValue(cid)),
                "description": s(lambda: acc.accDescription(cid)),
                "role": role, "role_name": MSAA_ROLE.get(role, str(role)),
                "state": s(lambda: int(acc.accState(cid)), -1), "rect": list(r) if r else None}

    def walk(acc, depth, prefix):
        if depth > 6:
            return
        try:
            n = int(acc.accChildCount)
        except Exception:                                                          # noqa: BLE001
            return
        for i in range(1, min(n, max_children) + 1):
            rec = one(acc, i)
            rec["path"] = "{0}.{1}".format(prefix, i)
            rec["depth"] = depth
            out.append(rec)
            kid = None
            try:
                kid = acc.accChild(i)
            except Exception:                                                      # noqa: BLE001
                kid = None
            if kid:
                try:
                    walk(kid.QueryInterface(IAcc), depth + 1, rec["path"])
                except Exception:                                                  # noqa: BLE001
                    pass
    out.append(dict(one(p, 0), path="0", depth=0))
    walk(p, 1, "0")
    return out


# ---------------------------------------------------------------- GUI acts (gated + confirmed)
def _md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def shot(tag, acts):
    """Full-screen capture. Read-only, needs no gate. Returns (path, md5)."""
    os.makedirs(SHOTS, exist_ok=True)
    p = os.path.join(SHOTS, "{0}_{1}.png".format(time.strftime("%H%M%S"), tag))
    g._lv_gui("-Action", "shot", "-Out", p)
    m = _md5(p) if os.path.exists(p) else None
    acts.append({"act": "shot", "tag": tag, "path": p, "md5": m})
    return p, m


def _fg_click(title, acts):
    """gscript.gui_save's `_fg_click`, verbatim in shape: title-bar clickprobe, MEASURED foreground."""
    m = re.search(r"left=(-?\d+) top=(-?\d+) right=(-?\d+)",
                  g._lv_gui("-Action", "rect", "-Title", '"%s"' % title))
    if not m:
        return False, "(no rect for %r)" % title
    L, T, R = (int(x) for x in m.groups())
    fg = "(no probe ran)"
    for _try in (1, 2):
        pj = g._lv_gui("-Action", "clickprobe", "-Title", '"%s"' % title,
                       "-X", str(min(L + 300, R - 120)), "-Y", str(T + 10),
                       "-Exception", "Approved", "-Evidence", EVIDENCE)
        line = next((l for l in pj.splitlines() if l.lstrip().startswith('{"probe"')), "")
        try:
            pr = json.loads(line)
        except Exception:                                                          # noqa: BLE001
            pr = {}
        fg = ((pr.get("fg_after_click") or {}).get("title")) or "(unreadable: %s)" % pj.strip()[:110]
        acts.append({"act": "clickprobe", "title": title, "x": min(L + 300, R - 120), "y": T + 10,
                     "foreground_after": fg, "confirmed": title in fg})
        if title in fg:
            return True, fg
        time.sleep(0.5)
    return False, fg


def _focus_vi_window(vi_path, acts):
    """Front the VI's own window and MEASURE it. Returns (title, foreground_text) or (None, why)."""
    name = os.path.basename(vi_path)
    tried = []
    for title in ("%s Block Diagram" % name, "%s Front Panel" % name, name):
        out = g._lv_gui("-Action", "focus", "-Title", '"%s"' % title)
        if "focused" not in out:
            tried.append("%r: no such window" % title)
            continue
        time.sleep(0.8)
        ok, fg = _fg_click(title, acts)
        if ok:
            return title, fg
        tried.append("%r: foreground stayed %r" % (title, fg))
    return None, " | ".join(tried)


def ensure_foreground(wtitle, hwnd, acts, tag):
    """The dialog must BE the foreground before any keystroke; SendKeys goes to whatever is.

    Fronting is done with `lv_gui.ps1 -Action activate` (added 2026-09-23), which is `focus` minus
    the Alt tap and minus the VK_ESCAPE that closes this dialog, and the result is CONFIRMED here
    with a read-only `GetForegroundWindow()` rather than trusted from the call's return."""
    import win32gui
    fg = win32gui.GetForegroundWindow()
    if fg == hwnd:
        acts.append({"act": "foreground check", "tag": tag, "confirmed": True})
        return True
    out = g._lv_gui("-Action", "activate", "-Title", '"%s"' % wtitle,
                    "-Exception", "Approved", "-Evidence", EVIDENCE)
    time.sleep(0.3)
    fg = win32gui.GetForegroundWindow()
    ok = fg == hwnd
    acts.append({"act": "activate", "tag": tag, "confirmed": ok,
                 "fg_title": win32gui.GetWindowText(fg) if fg else None,
                 "out": out.strip()[:140]})
    return ok


def send_keys(key, acts, tag, wait_ms=900):
    out = g._lv_gui("-Action", "keys", "-Key", key, "-WaitMs", str(wait_ms),
                    "-Exception", "Approved", "-Evidence", EVIDENCE)
    acts.append({"act": "keys", "key": key, "tag": tag, "out": out.strip()[:80]})
    return out


# ---------------------------------------------------------------- method B: capture + OCR
# MEASURED 2026-09-23 (tools/bench/errorlist_test.log, run 1): LabVIEW's Error List is FULLY
# owner-drawn - 0 win32 child windows, a 7-element UIA tree holding only the title-bar chrome, and a
# single MSAA object (the window). So method A cannot see a row, and the capture IS the measurement.
# OCR engine choice, measured on the saved capture of the bed, per row against the known truth:
#   Windows.Media.Ocr (winsdk, the ONLY installed recognizer language is 'ko'): "lnvoke NOde",
#     "connected tO anythinq", "Wire hA국" - 3/41, 37/39, 56/60, 0/25 characters right.
#   rapidocr-onnxruntime (PP-OCR, English): every row verbatim at scale 3 - "Block Diagram Errors",
#     "This wire connects one or more data sinks but has no source.", "Wire: Wire has loose ends".
# So RapidOCR is the engine; the Windows one is kept as the fallback because it needs no model files.
SEL_BLUE = (0, 120, 229)        # LabVIEW's list selection fill, sampled off the capture
_OCR = None


def ocr_engine():
    """(callable, name). RapidOCR if installed, else Windows.Media.Ocr, else (None, 'unavailable')."""
    global _OCR
    if _OCR is not None:
        return _OCR
    try:
        from rapidocr_onnxruntime import RapidOCR
        import numpy as np
        eng = RapidOCR()

        def run(img):
            res, _ = eng(np.array(img.convert("RGB")))
            return [(t, float(c), min(p[1] for p in b), max(p[1] for p in b),
                     min(p[0] for p in b)) for b, t, c in (res or [])]
        _OCR = (run, "rapidocr-onnxruntime")
        return _OCR
    except Exception as e:                                                         # noqa: BLE001
        pass
    try:
        import asyncio
        from winsdk.windows.globalization import Language
        from winsdk.windows.graphics.imaging import BitmapDecoder
        from winsdk.windows.media.ocr import OcrEngine
        from winsdk.windows.storage import StorageFile, FileAccessMode
        eng = (OcrEngine.try_create_from_language(Language("ko"))
               or OcrEngine.try_create_from_user_profile_languages())

        async def _go(p):
            f = await StorageFile.get_file_from_path_async(p)
            s = await f.open_async(FileAccessMode.READ)
            d = await BitmapDecoder.create_async(s)
            r = await eng.recognize_async(await d.get_software_bitmap_async())
            return [(ln.text, 0.0,
                     min(w.bounding_rect.y for w in ln.words),
                     max(w.bounding_rect.y + w.bounding_rect.height for w in ln.words),
                     min(w.bounding_rect.x for w in ln.words)) for ln in r.lines if ln.words]

        def run(img):
            os.makedirs(SHOTS, exist_ok=True)
            p = os.path.abspath(os.path.join(SHOTS, "_ocr_tmp.png"))
            img.convert("RGB").save(p)
            return asyncio.run(_go(p))
        _OCR = (run, "winsdk Windows.Media.Ocr (ko recognizer - Latin text is UNRELIABLE)")
        return _OCR
    except Exception:                                                              # noqa: BLE001
        _OCR = (None, "unavailable (no rapidocr-onnxruntime, no winsdk, no tesseract)")
        return _OCR


def ocr_lines(img, scale=3, invert=False, pad=10):
    """[(text, conf, y0, y1, x0)] in the ORIGINAL image's coordinates. [] when no engine."""
    from PIL import Image, ImageOps
    run, _name = ocr_engine()
    if run is None or img.width < 4 or img.height < 4:
        return []
    im = img.convert("RGB")
    if invert:
        im = ImageOps.invert(im)
    im = im.resize((im.width * scale, im.height * scale), Image.LANCZOS)
    c = Image.new("RGB", (im.width + 2 * pad, im.height + 2 * pad), (255, 255, 255))
    c.paste(im, (pad, pad))
    out = []
    for t, conf, y0, y1, x0 in run(c):
        out.append((t, conf, (y0 - pad) / scale, (y1 - pad) / scale, (x0 - pad) / scale))
    return sorted(out, key=lambda r: r[2])


def _runs(mask, thresh=0.3):
    """Maximal y-runs where `mask` (a per-row fraction) exceeds `thresh`."""
    out, y, n = [], 0, len(mask)
    while y < n:
        if mask[y] > thresh:
            s = y
            while y < n and mask[y] > thresh:
                y += 1
            out.append((s, y - 1))
        else:
            y += 1
    return out


def layout(img):
    """LOCATE the dialog's parts ON THE CAPTURE (never from remembered offsets).

    Returns {selections, bands, errors_band, details_band, count_band}. `selections` are the
    selection-blue y-runs; `bands` the white list/text panels read down one interior column."""
    import numpy as np
    a = np.array(img.convert("RGB")).astype(int)
    h, w = a.shape[0], a.shape[1]
    x0, x1 = int(w * 0.10), int(w * 0.92)
    d = np.abs(a[:, x0:x1, :] - np.array(SEL_BLUE)).sum(axis=2)
    sels = _runs((d < 60).mean(axis=1), 0.30)
    # A panel row is one that is NOT the dialog's grey background.  Measured on the first capture:
    # grey fraction is exactly 1.0 outside the panels and 0.0 inside, so the test is unambiguous -
    # whereas "white" alone split the errors list at the blue selection row AND cut the Details
    # pane's first text line off the top of its band ((423,645) instead of (411,645)).
    grey = (np.abs(a[:, x0:x1, :] - 240).max(axis=2) < 8).mean(axis=1)
    bands = [(s, e) for s, e in _runs(1.0 - grey, 0.5) if e - s > 40]
    lay = {"selections": sels, "bands": bands, "errors_band": None, "details_band": None,
           "count_band": None, "size": [w, h]}
    # The errors list is the white band that CONTAINS the lowest selection run; Details is the
    # next band below it; the "N errors and warnings" label sits just above the errors band.
    if sels and bands:
        sy = sels[-1][0]
        for i, (s, e) in enumerate(bands):
            if s - 4 <= sy <= e + 4:
                lay["errors_band"] = (s, e)
                lay["details_band"] = bands[i + 1] if i + 1 < len(bands) else None
                lay["count_band"] = (max(0, s - 26), s - 2)
                break
    return lay


def _trim(img):
    """Crop away fully-white rows - the Details pane is mostly empty and OCR of empty is waste."""
    import numpy as np
    a = np.array(img.convert("RGB")).astype(int)
    rows = np.where(~(a > 246).all(axis=2).all(axis=1))[0]
    if not len(rows):
        return None
    return img.crop((0, max(0, rows[0] - 2), img.width, min(img.height, rows[-1] + 3)))


def _cap(wtitle, acts, tag, hwnd=None):
    """shotwin of the Error List -> (image, path, (screen_left, screen_top)).

    The window rect is re-read on EVERY capture, so an image coordinate can be converted to a screen
    coordinate even if the dialog is moved: PrintWindow's bitmap is exactly the window rect (measured:
    rect (463,242,1462,942) -> a 999x700 PNG), so screen = (left, top) + image."""
    from PIL import Image
    import win32gui
    os.makedirs(SHOTS, exist_ok=True)
    p = os.path.join(SHOTS, "errwin_{0}_{1}.png".format(time.strftime("%H%M%S"), tag))
    g._lv_gui("-Action", "shotwin", "-Title", '"%s"' % wtitle, "-Out", p)
    if not os.path.exists(p):
        return None, None, None
    org = None
    if hwnd:
        try:
            r = win32gui.GetWindowRect(hwnd)
            org = (r[0], r[1])
        except Exception:                                                          # noqa: BLE001
            org = None
    acts.append({"act": "shotwin", "tag": tag, "path": p, "md5": _md5(p), "origin": org})
    return Image.open(p).convert("RGB"), p, org


def _sel_in(lay, eb):
    """The selection-blue run that lies inside the errors band, or None."""
    for s in reversed(lay["selections"] or []):
        if eb[0] - 4 <= s[0] <= eb[1] + 4:
            return s
    return None


def read_by_capture(R, wtitle, acts, log, max_steps=80, hwnd=None, on_item=None):
    """METHOD B. Walk the list one row at a time; each step: capture -> LOCATE the highlighted row by
    COLOUR on that capture -> OCR that row and the Details pane -> act -> capture -> CONFIRM the
    selection moved exactly one row.

    Stepping mechanism, in the brief's order and decided by MEASUREMENT, not by preference:
      1. keyboard {DOWN}, after the dialog's foreground has been MEASURED with a title-bar
         clickprobe (gscript.gui_save's idiom).  Run 2 measured keystrokes reaching NOTHING - four
         consecutive captures byte-identical (md5 26699694) - because the Front Panel, not the
         dialog, held the foreground, so the probe is now mandatory.
      2. if {DOWN} still does not move the highlight, CLICK the next row, whose rectangle is derived
         from the highlight's own position and height on the live capture (never a remembered
         coordinate) and whose effect is confirmed on the next capture.
      3. at the bottom of the visible band, mouse-wheel over the list; the wheel's direction and
         step are measured from how far the highlight moves, never assumed."""
    run, engine_name = ocr_engine()
    R["ocr_engine"] = engine_name
    R["fallback_ocr"] = engine_name
    if run is None:
        R["errors"].append("no OCR engine; captures kept, text not extracted")
        log("  OCR: {0} - captures kept, NO text extracted".format(engine_name))
        return
    log("  OCR engine: {0}".format(engine_name))
    img, _p, org = _cap(wtitle, acts, "b0", hwnd)
    if img is None:
        R["errors"].append("shotwin produced no capture")
        return
    lay = layout(img)
    R["layout"] = {k: v for k, v in lay.items()}
    log("  layout: bands={0} selections={1} errors_band={2} details_band={3}".format(
        lay["bands"], lay["selections"], lay["errors_band"], lay["details_band"]))
    if not lay["errors_band"]:
        R["errors"].append("could not locate the errors band on the capture")
        return
    if R.get("n_reported") is None and lay["count_band"]:
        cb = lay["count_band"]
        for t, _c, _y0, _y1, _x in ocr_lines(img.crop((0, cb[0], img.width, cb[1])), scale=4):
            m = re.search(r"(\d+)\s*errors?\s*and\s*warnings?", t, re.I)
            if m:
                R["n_reported"], R["n_reported_from"] = int(m.group(1)), t.strip()
                break
    log("  window's own count: {0!r} (from {1!r})".format(R["n_reported"], R.get("n_reported_from")))
    R["method"] = "capture+OCR ({0}); UIA/MSAA expose no rows".format(engine_name)

    eb = lay["errors_band"]
    n_want = R.get("n_reported") or 0
    headers, band_prev = [], None
    org = org or (0, 0)

    def click_img(ix, iy, tag, origin):
        """Click an IMAGE coordinate that was located on the capture just taken."""
        sx, sy = origin[0] + int(ix), origin[1] + int(iy)
        g._lv_gui("-Action", "click", "-X", str(sx), "-Y", str(sy),
                  "-Exception", "Approved", "-Evidence", EVIDENCE)
        acts.append({"act": "click", "tag": tag, "image_xy": [int(ix), int(iy)],
                     "screen_xy": [sx, sy]})
        time.sleep(0.35)

    def grab(tag):
        i, p, o = _cap(wtitle, acts, tag, hwnd)
        if i is None:
            return None, None, None, None, None
        la = layout(i)
        b = la["errors_band"] or eb
        return i, p, la, b, _sel_in(la, b)

    # --- make the dialog the MEASURED foreground before any keystroke (run 2's failure) ----------
    # ⚠️ NEITHER `-Action focus` NOR `-Action clickprobe` MAY BE USED ON THIS DIALOG. `[LVGui]::Focus`
    # and `[LVGui]::ClickProbe` both tap Alt, activate, then send VK_ESCAPE to leave LabVIEW's menu
    # mode - and Esc is exactly how the Error List closes. Runs 3 and 4 measured it: after either
    # call, `-Action rect` and `-Action shotwin` on 'Error list' report "No LabVIEW window whose
    # title contains 'Error list'". `-Action activate` is that activation minus the Alt and the Esc.
    fg_ok = ensure_foreground(wtitle, hwnd, acts, "before reading")
    R["dialog_foreground"] = fg_ok
    log("  dialog is the measured foreground: {0}".format(fg_ok))

    # --- decide the stepping mechanism BY MEASUREMENT: one {DOWN}, then look -----------------
    img, path, lay, eb, sel = grab("b0b")
    if sel is None:
        R["errors"].append("no highlighted row in the errors band")
        return
    pitch = max(12, sel[1] - sel[0] + 1)
    ensure_foreground(wtitle, hwnd, acts, "mechanism probe")
    send_keys("{DOWN}", acts, "mechanism probe", wait_ms=450)
    img2, path2, lay2, eb2, sel2 = grab("probe")
    mode = "keys" if (sel2 and sel2[0] != sel[0]) else "click"
    acts.append({"act": "confirm", "tag": "{DOWN} moves the highlight", "confirmed": mode == "keys"})
    R["step_mode"] = mode
    log("  stepping mechanism: {0} (highlight {1} -> {2} after one {{DOWN}})".format(
        mode, sel, sel2))
    if mode == "keys":
        img, path, lay, eb, sel = img2, path2, lay2, eb2, sel2
        # {DOWN} already consumed one row; go back up so row 0 is not skipped.
        ensure_foreground(wtitle, hwnd, acts, "back to the first row")
        send_keys("{UP}", acts, "back to the first row", wait_ms=350)
        img, path, lay, eb, sel = grab("b0c")
        if sel is None:
            sel = sel2

    wheel_dir, row_ord = -1, 0
    for step in range(max_steps):
        if img is None or sel is None:
            break
        y0, y1 = sel
        # ONE OCR of the whole band, then pick the line sitting on the highlight. Measured better
        # than OCRing the inverted single-row strip, which loses word spaces
        # ("InvokeNodeInvokeNode':Invalidmethod" vs "Invoke Node 'Invoke Node': Invalid method").
        band = ocr_lines(img.crop((20, eb[0], img.width - 30, eb[1])), scale=3)
        band_now = [t for t, _c, _a, _b, _x in band]
        on = [(t, x) for t, _c, a, b, x in band if y0 - 6 <= eb[0] + (a + b) / 2.0 <= y1 + 6]
        txt = " ".join(t for t, _x in on).strip()
        xs = [x for _t, x in on] or [999]
        det_img = img.crop((20, lay["details_band"][0], img.width - 30,
                            lay["details_band"][1])) if lay["details_band"] else None
        det_img = _trim(det_img) if det_img is not None else None
        detail = " ".join(t for t, _c, _y0, _y1, _x in ocr_lines(det_img, scale=3)).strip() \
            if det_img is not None else None
        overlap = (band_prev is None) or bool(set(band_prev) & set(band_now))
        acts.append({"act": "confirm", "tag": "step %d band overlaps the previous capture" % step,
                     "confirmed": overlap})
        band_prev = band_now
        # A CATEGORY row ("Block Diagram Errors") is drawn unindented with a bullet; an error row is
        # indented ~40 px further. Measured on the capture: header x~18, items x~40 (crop-relative).
        is_header = min(xs) < 30
        obj, reason = _split(txt)
        # `row_index` counts EVERY row the walk selected, category headers included, so a later
        # `Show Error` pass can address the same row without re-deriving it from the text (which
        # repeats: "This wire is not connected to anything." occurs 8x on the bed).
        rec = {"index": len(R["items"]), "row_index": row_ord, "vi": R["vi_name"],
               "object": obj, "reason": reason,
               "raw": txt, "detail": detail, "detail_path": "capture+OCR",
               "selection_route": mode, "rect": [0, y0, img.width, y1], "offscreen": False,
               "uia_path": None, "capture": path, "band_overlap_ok": overlap,
               "screen_rect": [org[0], org[1] + y0, org[0] + img.width, org[1] + y1]}
        row_ord += 1
        if is_header:
            rec["index"] = None
            headers.append(rec)
            log("   category: {0!r}".format(txt[:70]))
        else:
            R["items"].append(rec)
            log("   item {0:>2}: object={1!r} reason={2!r} detail={3!r}".format(
                rec["index"], obj[:40], reason[:70], (detail or "")[:70]))
            # 2026-09-24 (tools/errorlist_check.py, user decision 5): an optional per-item hook, called while
            # the row is the highlighted one; the walk re-fronts the dialog itself before its next keystroke.
            if on_item is not None:
                try:
                    on_item(rec, acts)
                except Exception as e:                                             # noqa: BLE001
                    rec["on_item_error"] = "{0}: {1}".format(type(e).__name__, str(e)[:160])
        if n_want and len(R["items"]) >= n_want:
            log("  reached the window's own count of {0} items".format(n_want))
            break

        # --- advance exactly one row, and CONFIRM it moved -----------------------------------
        # 2026-09-24 (card chat-C2): (a) the dialog is RE-FRONTED before every wheel and every click - an
        # `on_item` double-click fronts the block diagram, which then sits over the list, and run
        # errorlist_check_s4_r1 clicked the DIAGRAM twice (gui_actions.log 18:08:14/18:08:22) and stopped at
        # 2 of 15; (b) a retry never re-records the row (that run recorded item 0 twice); (c) the wheel
        # direction is flipped inside the step, not by `continue` (which re-recorded the row too).
        target = y0 + pitch
        if target + pitch - 1 > eb[1] - 2:            # no room: scroll first, measure the step
            s2 = None
            for _wtry in (1, 2):
                ensure_foreground(wtitle, hwnd, acts, "step %d before wheel" % step)
                g._lv_gui("-Action", "wheel", "-X", str(org[0] + img.width // 2),
                          "-Y", str(org[1] + (eb[0] + eb[1]) // 2), "-Notches", str(wheel_dir))
                acts.append({"act": "wheel", "tag": "step %d scroll" % step, "notches": wheel_dir})
                time.sleep(0.45)
                img, path, lay, eb, s2 = grab("s{0}_{1}".format(step, _wtry))
                if s2 is not None and s2[0] != y0:
                    break
                wheel_dir = -wheel_dir                # direction measured, never assumed
            if s2 is None or s2[0] == y0:
                log("  the list will not scroll further - end of the list")
                break
            acts.append({"act": "confirm", "tag": "step %d list scrolled" % step, "confirmed": True,
                         "rows": round((y0 - s2[0]) / float(pitch), 2)})
            y0, sel = s2[0], s2
            target = y0 + pitch
            if target + pitch - 1 > eb[1] - 2:
                break
        moved, s3 = False, None
        for _try in (1, 2):
            ensure_foreground(wtitle, hwnd, acts, "step %d try %d" % (step, _try))
            if mode == "keys":
                send_keys("{DOWN}", acts, "step %d" % step, wait_ms=300)
            else:
                click_img(img.width // 6, target + pitch // 2, "step %d select the next row" % step, org)
            img, path, lay, eb, s3 = grab("b{0}_{1}".format(step + 1, _try))
            moved = bool(s3 and s3[0] == target)
            acts.append({"act": "confirm", "tag": "step %d highlight moved one row down" % step,
                         "confirmed": moved, "want_y": target, "got_y": s3[0] if s3 else None})
            if moved:
                break
        if not moved:
            log("  the highlight stopped moving - end of the list")
            break
        sel = s3
    R["categories"] = headers


# ---------------------------------------------------------------- the reader
def _split(raw):
    """Error-list row text -> (object, reason). LabVIEW rows read '<object>: <reason>' when they
    name an object and are a bare sentence otherwise; the raw text is ALWAYS kept verbatim."""
    t = (raw or "").strip()
    m = re.match(r"^([^:]{1,80}):\s+(.*)$", t, re.S)
    return (m.group(1).strip(), m.group(2).strip()) if m else ("", t)


def read(vi_path, out_json=None, maxdepth=14, dump_tree=True, log=print, on_item=None):
    """Open the Error List for `vi_path` (already in memory), read every item, close it.

    Returns the record; also written to `out_json`. The VI is never run and never saved."""
    name = os.path.basename(vi_path)
    R = {"vi": vi_path, "vi_name": name, "stamp": time.strftime("%Y-%m-%d %H:%M:%S"),
         "method": None, "uia_items_exposed": None, "n_reported": None, "items": [],
         "gui_acts": [], "fallback_ocr": None, "no_vi_was_run": True, "errors": []}
    acts = R["gui_acts"]
    pid = lv_pid()
    R["labview_pid"] = pid
    before = top_windows(pid)
    R["windows_before"] = [[t, c] for _h, t, c, _r in before]
    log("  windows before Ctrl+L: {0!r}".format(R["windows_before"]))

    # --- capture -> locate -> act -> capture -> confirm, act 1: Ctrl+L ---------------------
    shot("before_ctrl_l", acts)
    title, fg = _focus_vi_window(vi_path, acts)
    R["focused_title"], R["foreground"] = title, fg
    if not title:
        R["errors"].append("could not front the VI window: %s" % fg)
        return _finish(R, out_json, log)
    log("  fronted {0!r} (measured foreground {1!r})".format(title, fg))
    send_keys("^l", acts, "open error list", wait_ms=1500)

    hw, t0 = None, time.time()
    while time.time() - t0 < 20:
        for h, t, c, r in top_windows(pid):
            if ERRWIN_RE.search(t or "") and (h, t) not in [(x[0], x[1]) for x in before]:
                hw = (h, t, c, r)
                break
        if hw:
            break
        time.sleep(0.5)
    if not hw:                     # no title match: accept ANY window that was not there before
        for h, t, c, r in top_windows(pid):
            if h not in [x[0] for x in before]:
                hw = (h, t, c, r)
                break
    shot("after_ctrl_l", acts)
    if not hw:
        R["errors"].append("Ctrl+L opened no new window - NOT CONFIRMED")
        acts.append({"act": "confirm", "tag": "ctrl+l", "confirmed": False})
        return _finish(R, out_json, log)
    hwnd, wtitle, wclass, wrect = hw
    R["window"] = {"hwnd": hwnd, "title": wtitle, "class": wclass, "rect": list(wrect)}
    acts.append({"act": "confirm", "tag": "ctrl+l", "confirmed": True, "new_window": wtitle})
    log("  Error List window: hwnd={0} title={1!r} class={2} rect={3}".format(
        hwnd, wtitle, wclass, wrect))
    g._lv_gui("-Action", "shotwin", "-Title", '"%s"' % wtitle,
              "-Out", os.path.join(SHOTS, "errwin_%s.png" % time.strftime("%H%M%S")))
    R["win32_children"] = [[c, t] for _h, c, t, _r in child_windows(hwnd)][:60]
    log("  win32 CHILD windows of the dialog: {0}".format(len(R["win32_children"])))

    # --- method A: UI Automation ------------------------------------------------------------
    try:
        _read_uia(R, hwnd, maxdepth, dump_tree, acts, log)
    except Exception as e:                                                         # noqa: BLE001
        R["errors"].append("UIA: {0}: {1}".format(type(e).__name__, str(e)[:200]))
        log("  UIA RAISED {0}: {1}".format(type(e).__name__, str(e)[:200]))

    # --- route A2: MSAA child-ids, always censused; used as ITEMS when UIA exposed none --------
    try:
        _read_msaa(R, hwnd, acts, log)
    except Exception as e:                                                         # noqa: BLE001
        R["errors"].append("MSAA: {0}: {1}".format(type(e).__name__, str(e)[:200]))
        log("  MSAA RAISED {0}: {1}".format(type(e).__name__, str(e)[:200]))

    # --- method B: capture + OCR, used when no accessibility route exposed a row ---------------
    if not R["items"]:
        try:
            read_by_capture(R, wtitle, acts, log, hwnd=hwnd, on_item=on_item)
        except Exception as e:                                                     # noqa: BLE001
            R["errors"].append("capture+OCR: {0}: {1}".format(type(e).__name__, str(e)[:200]))
            log("  capture+OCR RAISED {0}: {1}".format(type(e).__name__, str(e)[:200]))

    # --- close with Esc, confirm the window is gone ------------------------------------------
    g._lv_gui("-Action", "key", "-Key", "esc")
    time.sleep(0.8)
    gone = not any(h == hwnd for h, _t, _c, _r in top_windows(pid))
    if not gone:
        # `focus` here is FINE (and is itself a second Esc): closing is the goal - see the warning in
        # read_by_capture about why the same call must never be made while reading.
        g._lv_gui("-Action", "focus", "-Title", '"%s"' % wtitle)
        time.sleep(0.4)
        g._lv_gui("-Action", "key", "-Key", "esc")
        time.sleep(0.8)
        gone = not any(h == hwnd for h, _t, _c, _r in top_windows(pid))
    if not gone:
        # RECOVERY ONLY. A LabVIEW dialog left up blocks every later COM call (skill com-driving.md),
        # so the window is closed by WM_CLOSE and the act is written to tools/gui_actions.log by hand
        # (lv_gui.ps1 `dismiss` refuses unless it measures LabVIEW as blocked, which it is not here).
        import win32con
        import win32gui
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
        time.sleep(1.0)
        gone = not any(h == hwnd for h, _t, _c, _r in top_windows(pid))
        acts.append({"act": "WM_CLOSE (recovery, Esc did not close)", "confirmed": gone})
        with open(os.path.join(HERE, "gui_actions.log"), "a", encoding="utf-8") as f:
            f.write("{0}\tWM_CLOSE\tApproved\t{1}\tErrorList recovery hwnd={2} gone={3}\n".format(
                time.strftime("%Y-%m-%d %H:%M:%S"), EVIDENCE, hwnd, gone))
    shot("after_esc", acts)
    acts.append({"act": "key esc", "tag": "close error list", "confirmed": gone})
    R["closed_with_esc"] = gone
    log("  Esc closed the Error List: {0}".format(gone))
    # Offline, after the dialog is closed: no LabVIEW, no GUI - only the captures on disk.
    try:
        refine_rows(R, log)
    except Exception as e:                                                         # noqa: BLE001
        R["errors"].append("refine_rows: {0}: {1}".format(type(e).__name__, str(e)[:160]))
    return _finish(R, out_json, log)


def _read_uia(R, hwnd, maxdepth, dump_tree, acts, log):
    u = UIA()
    tree = u.tree(u.from_hwnd(hwnd), maxdepth=maxdepth)
    R["uia_tree_size"] = len(tree)
    if dump_tree:
        log("  --- UIA tree ({0} elements) ---".format(len(tree)))
        for d in tree:
            log("   {0}{1} [{2}] name={3!r} cls={4!r} aid={5!r} val={6!r} sel={7}".format(
                "  " * d["depth"], d["path"], d["ct_name"], (d["name"] or "")[:90],
                d["class"], d["aid"], (d["value"] or "")[:60], d["selected"]))
    R["uia_tree"] = [{k: v for k, v in d.items() if k != "_el"} for d in tree]

    items = [d for d in tree if d["ct"] in ITEMISH]
    lists = [d for d in tree if d["ct"] in LISTISH]
    R["uia_items_exposed"] = bool(items)
    R["uia_lists"] = [{"path": d["path"], "ct": d["ct_name"], "name": d["name"]} for d in lists]
    log("  UIA: {0} list-ish container(s), {1} item element(s) exposed".format(len(lists), len(items)))

    # "N errors" - any element whose text carries the count.
    for d in tree:
        for s in (d["name"], d["value"], d["text"]):
            m = re.search(r"(\d+)\s+error", s or "", re.I)
            if m:
                R["n_reported"] = int(m.group(1))
                R["n_reported_from"] = (s or "").strip()[:160]
                break
        if R["n_reported"] is not None:
            break
    log("  window's own count: {0!r} (from {1!r})".format(R["n_reported"], R.get("n_reported_from")))

    if not items:
        R["method"] = "UIA-no-items (owner-drawn list) -> capture kept, OCR unavailable"
        return

    # The errors list = the list-ish container with the most item descendants.
    def kids_of(dl):
        return [d for d in tree if d["path"].startswith(dl["path"] + ".") and d["ct"] in ITEMISH]
    best = max(lists, key=lambda d: len(kids_of(d))) if lists else None
    rows = kids_of(best) if best and kids_of(best) else items
    R["errors_list_path"] = best["path"] if best else None
    R["method"] = "UIA"

    # Focus the list by keyboard so {DOWN} lands there; fall back to UIA Select (recorded).
    focus_ok = u.set_focus(best["_el"]) if best else False
    acts.append({"act": "uia SetFocus", "tag": "errors list", "confirmed": bool(focus_ok)})

    prev_detail = None
    for i, d in enumerate(rows):
        raw = d["name"] or d["value"] or d["text"] or ""
        route = "tree"
        if i == 0:
            moved = _select_first(u, d, acts)
        else:
            moved = _step_down(u, d, acts, i)
        route = moved
        detail, dpath = _detail(u, hwnd, maxdepth, exclude=[x["path"] for x in rows])
        if detail == prev_detail and i:
            acts.append({"act": "confirm", "tag": "item %d detail changed" % i, "confirmed": False})
        else:
            acts.append({"act": "confirm", "tag": "item %d detail changed" % i, "confirmed": True})
        prev_detail = detail
        obj, reason = _split(raw)
        R["items"].append({"index": i, "vi": R["vi_name"], "object": obj, "reason": reason,
                           "raw": raw, "detail": detail, "detail_path": dpath,
                           "selection_route": route, "rect": d["rect"],
                           "offscreen": d["offscreen"], "uia_path": d["path"]})
        log("   item {0:>2}: object={1!r} reason={2!r} detail={3!r}".format(
            i, obj[:40], reason[:70], (detail or "")[:70]))


def _msaa_all(hwnd):
    """MSAA census of the dialog AND every win32 child hwnd, tagged by the hwnd it came from."""
    rows = []
    for h, cls, txt, _r in [(hwnd, "(top)", "", None)] + [(k[0], k[1], k[2], k[3])
                                                          for k in child_windows(hwnd)]:
        for rec in msaa_rows(h):
            rec["hwnd"], rec["hwnd_class"], rec["hwnd_text"] = h, cls, txt
            rows.append(rec)
    return rows


def _read_msaa(R, hwnd, acts, log):
    rows = _msaa_all(hwnd)
    R["msaa_rows"] = rows[:300]
    listitems = [r for r in rows if r["role"] == 34]
    if R.get("n_reported") is None:
        for r in rows:
            for s in (r["name"], r["value"], r["description"]):
                m = re.search(r"(\d+)\s+error", s or "", re.I)
                if m:
                    R["n_reported"] = int(m.group(1))
                    R["n_reported_from"] = (s or "").strip()[:160]
                    break
            if R.get("n_reported") is not None:
                break
    R["msaa_items_exposed"] = bool(listitems)
    log("  MSAA: {0} accessible object(s); {1} with role=listitem; roles seen {2!r}".format(
        len(rows), len(listitems), sorted({r["role_name"] for r in rows})[:12]))
    for r in rows[:40]:
        log("   msaa {0} [{1}] hwnd={2} name={3!r} value={4!r} state={5}".format(
            r["path"], r["role_name"], r["hwnd"], (r["name"] or "")[:80],
            (r["value"] or "")[:50], r["state"]))
    if R["items"] or not listitems:
        return
    # UIA exposed no items; the rows ARE here, so read them through MSAA with keyboard stepping.
    R["method"] = "MSAA (IAccessible child-ids); UIA exposed no items"
    prev = None
    for i, r in enumerate(listitems):
        if i:
            send_keys("{DOWN}", acts, "item %d" % i, wait_ms=350)
        elif any(r2["state"] & 0x2 for r2 in listitems):     # STATE_SYSTEM_SELECTED
            pass
        else:
            send_keys("{HOME}", acts, "item 0", wait_ms=350)
        after = _msaa_all(hwnd)
        det = _msaa_detail(after, hwnd)
        acts.append({"act": "confirm", "tag": "item %d detail changed" % i,
                     "confirmed": det != prev or i == 0})
        prev = det
        raw = r["name"] or r["value"] or ""
        obj, reason = _split(raw)
        R["items"].append({"index": i, "vi": R["vi_name"], "object": obj, "reason": reason,
                           "raw": raw, "detail": det, "detail_path": "msaa",
                           "selection_route": "keys-down", "rect": r["rect"],
                           "offscreen": None, "uia_path": r["path"]})
        log("   item {0:>2}: object={1!r} reason={2!r} detail={3!r}".format(
            i, obj[:40], reason[:70], (det or "")[:70]))


def _msaa_detail(rows, _hwnd):
    """Longest non-listitem text in the MSAA census = the detail pane."""
    best = ""
    for r in rows:
        if r["role"] == 34:
            continue
        for s in (r["value"], r["name"], r["description"]):
            if s and len(s) > len(best):
                best = s
    return best.strip() or None


def _select_first(u, d, acts):
    if u.select(d["_el"]):
        acts.append({"act": "uia Select", "tag": "item 0", "confirmed": True})
        return "uia-select"
    send_keys("{HOME}", acts, "item 0", wait_ms=500)
    return "keys-home"


def _step_down(u, d, acts, i):
    """Keyboard first (the brief): {DOWN}. Confirm by the item's own IsSelected."""
    send_keys("{DOWN}", acts, "item %d" % i, wait_ms=400)
    if u.selected(d["_el"]):
        acts.append({"act": "confirm", "tag": "item %d selected by {DOWN}" % i, "confirmed": True})
        return "keys-down"
    if u.select(d["_el"]):
        acts.append({"act": "uia Select", "tag": "item %d ({DOWN} did not select)" % i,
                     "confirmed": True})
        return "uia-select"
    return "unselected"


def _detail(u, hwnd, maxdepth, exclude):
    """The detail pane = the longest text/value outside the item rows, re-read after each move."""
    tree = u.tree(u.from_hwnd(hwnd), maxdepth=maxdepth)
    best, bpath = "", None
    for d in tree:
        if d["ct"] not in TEXTISH and d["ct"] not in (50025, 50026):
            continue
        if any(d["path"].startswith(p) for p in exclude):
            continue
        for s in (d["value"], d["text"], d["name"]):
            if s and len(s) > len(best):
                best, bpath = s, d["path"]
    return (best.strip() if best else None), bpath


def refine_rows(R, log=print):
    """Re-read each row from the capture in which it is NOT highlighted. OFFLINE - no LabVIEW.

    RapidOCR reads a white-on-blue LabVIEW list row with its word spaces collapsed
    ("Thiswireisnotconnectedtoanything"); the SAME row, one step later, is drawn unselected and
    reads verbatim ("This wire is not connected to anything"). Every row except the last one is
    therefore re-read from item i+1's capture, one pitch above that capture's highlight - which is
    robust to the list having scrolled in between, because the walk always moves exactly one row.

    A replacement is accepted ONLY when the two readings agree with whitespace removed, so a
    mis-located row can never be substituted for the real one."""
    from PIL import Image

    def norm(s):
        """Alphanumerics only. The two readings of one row differ in SPACES and in the trailing
        period ('Thiswireisnotconnectedtoanything' vs 'This wire is not connected to anything.'),
        so comparing on whitespace alone rejected 12 of 13 correct refinements."""
        return re.sub(r"[^0-9a-z]", "", (s or "").lower())

    def row_text(cap, want_y):
        if not cap or not os.path.exists(cap):
            return None
        img = Image.open(cap).convert("RGB")
        lay = layout(img)
        eb = lay.get("errors_band")
        if not eb:
            return None
        band = ocr_lines(img.crop((20, eb[0], img.width - 30, eb[1])), scale=3)
        on = [t for t, _c, a, b, _x in band
              if want_y - 5 <= eb[0] + (a + b) / 2.0 <= want_y + 21]
        return " ".join(on).strip() or None

    items = R.get("items") or []
    fixed = 0
    for i, it in enumerate(items):
        old = it.get("raw") or ""
        pitch = max(12, it["rect"][3] - it["rect"][1] + 1)
        cands = []
        if i + 1 < len(items):                    # the row, one step later, drawn UNSELECTED
            nxt = items[i + 1]
            cands.append((nxt.get("capture"), nxt["rect"][1] - pitch))
        if i:                                     # and one step earlier, if the list did not scroll
            prv = items[i - 1]
            if prv["rect"][1] + pitch == it["rect"][1]:
                cands.append((prv.get("capture"), it["rect"][1]))
        for cap, y in cands:
            cand = row_text(cap, y)
            if cand and norm(cand) == norm(old):
                if cand != old:
                    it["raw_selected_ocr"] = old
                    it["raw"] = cand
                    it["object"], it["reason"] = _split(cand)
                    it["refined_from"] = cap
                    fixed += 1
                it["raw_refined"] = True
                break
        else:
            it["raw_refined"] = False
    R["rows_refined"] = fixed
    R["rows_unrefined"] = [it["index"] for it in items if not it.get("raw_refined")]
    log("  refine_rows: {0} row(s) re-read unselected; not refined: {1!r}".format(
        fixed, R["rows_unrefined"]))
    return R


def _finish(R, out_json, log):
    R["item_count"] = len(R["items"])
    if out_json:
        os.makedirs(os.path.dirname(out_json), exist_ok=True)
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(R, f, indent=1, ensure_ascii=False, default=str)
        log("  JSON -> {0}  ({1} items)".format(out_json, R["item_count"]))
    return R


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    vi = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        BENCH, "errorlist_{0}_{1}.json".format(
            re.sub(r"\W+", "_", os.path.splitext(os.path.basename(vi))[0])[:40],
            time.strftime("%Y%m%d")))
    g.open_panel(vi)
    r = read(vi, out)
    print(json.dumps({k: r[k] for k in ("method", "uia_items_exposed", "n_reported", "item_count")},
                     indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
