"""lvclick.py — M3 clicker: GUI verbs whose targets come from COM data, each self-verifying.

Spec: docs/m3-clicker-spec.md (§7 = post-review design). Geometry: docs/gui-geometry.json.
Built on gscript.py (COM reads/reverts) and lv_gui.ps1 (input, windows, probe, rect).

    import lvclick as c
    vp = c.calibrate(target)                         # two-object check; raises if scale != 1
    c.focus_bd(vp)
    c.move_node(vp, target, 538, "Invoke", 100, 50)
    c.place_from_palette(vp, target, "Array/Index Array", "IndexArray", 1100, 600)
    c.node_menu(vp, target, 610, "Property", 0, "Change To Write")
    c.dialog_button("Find", "Cancel", open_with="^f", bd=vp)

Every verb returns a dict with "ok" and what it measured; nothing is inferred from screenshots.
Every state-changing input goes through lv_gui's gate (-Exception Approved -Evidence EVIDENCE).
Unknown geometry -> {"ok": False, "reason": "no geometry ..."}: the caller escalates to the
vision executor and records what it measured back into gui-geometry.json.
"""
import json
import os
import re
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
GEOM_PATH = os.path.join(PROJECT, "docs", "gui-geometry.json")
import gscript as g  # noqa: E402  (same folder)

EVIDENCE = "M3 clicker toolkit (user: 시작 2026-09-05)"


def geom():
    return json.load(open(GEOM_PATH, encoding="utf-8"))


def save_geom(d):
    json.dump(d, open(GEOM_PATH, "w", encoding="utf-8"), indent=2, ensure_ascii=False)


# --- lv_gui plumbing --------------------------------------------------------------------------

def lv(*args, timeout=60):
    q = lambda a: a if a.replace("-", "").replace(".", "").replace("^", "").isalnum() else f'"{a}"'
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& .\\tools\\lv_gui.ps1 " + " ".join(q(str(a)) for a in args)]
    r = subprocess.run(cmd, cwd=PROJECT, capture_output=True, text=True, timeout=timeout)
    if r.returncode != 0:
        raise RuntimeError(f"lv_gui {args[:2]}: {(r.stdout + r.stderr).strip()[:300]}")
    return r.stdout.strip()


def act(action, **kw):
    """Gated input action (click/rclick/drag/keys) — always logged by lv_gui."""
    args = ["-Action", action]
    for k, v in kw.items():
        args += [f"-{k}", str(v)]
    if action in ("click", "rclick", "dclick", "drag", "wire", "keys"):
        args += ["-Exception", "Approved", "-Evidence", EVIDENCE]
    return lv(*args)


def windows():
    return [w for w in lv("-Action", "windows").splitlines() if w.strip()]


def toplevel():
    """[(enabled, hwnd, (l,t,r,b), title)] for every visible window of the LabVIEW process —
    includes untitled popups (palette, context menus). Parsed from `-Action dialogs`."""
    out = []
    for line in lv("-Action", "dialogs").splitlines():
        m = re.match(r"(ENABLED|blocked)\|(\d+)\|(-?\d+),(-?\d+),(-?\d+),(-?\d+)\|(.*)$", line)
        if m:
            out.append((m.group(1) == "ENABLED", int(m.group(2)),
                        tuple(int(m.group(i)) for i in range(3, 7)), m.group(7)))
    return out


def rect(title):
    m = re.search(r"left=(-?\d+) top=(-?\d+) right=(-?\d+) bottom=(-?\d+)", lv("-Action", "rect", "-Title", title))
    if not m:
        raise RuntimeError(f"rect: cannot parse for '{title}'")
    return tuple(int(x) for x in m.groups())


def probe_runs(x, y, x2=None, y2=None):
    """[(start, end, 'RRGGBB'), ...] along a row (x..x2 at y) or a column (y..y2 at x)."""
    args = ["-Action", "probe", "-X", x, "-Y", y] + (["-X2", x2] if x2 is not None else ["-Y2", y2])
    runs = []
    for line in lv(*args).splitlines()[1:]:
        m = re.match(r"\s*(-?\d+)-(-?\d+)\s+\(\d+px\)\s+#([0-9A-F]{6})", line)
        if m:
            runs.append((int(m.group(1)), int(m.group(2)), m.group(3)))
    return runs


def dominant_rgb(runs):
    tally = {}
    for a, b, rgb in runs:
        tally[rgb] = tally.get(rgb, 0) + (b - a + 1)
    return max(tally, key=tally.get) if tally else None


# --- viewport -----------------------------------------------------------------------------------

class Viewport:
    def __init__(self, title, L, T, dx, dy):
        self.title, self.L, self.T, self.dx, self.dy = title, L, T, dx, dy

    def s(self, x, y):
        """diagram -> screen"""
        return x + self.L + self.dx, y + self.T + self.dy

    def __repr__(self):
        return f"Viewport({self.title!r}, L={self.L}, T={self.T}, dx={self.dx}, dy={self.dy})"


def node_pos(target, uid, cls):
    hits = [o for o in g.report(target, cls) if o["uid"] == uid]
    if not hits:
        raise RuntimeError(f"node {uid} ({cls}) not found on {os.path.basename(target)}")
    return tuple(hits[0]["pos"])


def _header_ok(vp, cls, x, y):
    """The class's header colour must dominate a 12-px probe on the header row at (x, y)."""
    spec = geom()["classes"].get(cls)
    if not spec:
        return False, f"no class geometry for {cls}"
    fw, fy = spec["grab"]
    sx, sy = vp.s(x + 2, y + fy)
    dom = dominant_rgb(probe_runs(sx, sy, x2=sx + 12))
    return dom == spec["header_rgb"], f"probe at {(sx, sy)} = {dom}, expected {spec['header_rgb']}"


def calibrate(target, title=None):
    """Viewport from the BD window rect + registered (dx, dy), VERIFIED on two registered
    objects: both must show their class header colour at the computed screen position (scale
    exactly 1 and identical offset), else raise — that is how a scrolled/zoomed/other-DPI window
    is caught before any click. `title` defaults to '<vi name> Block Diagram'."""
    gm = geom()
    name = os.path.basename(target)
    title = title or f"{name} Block Diagram"
    # Pixels are only meaningful on the TOP window: OpenFrontPanel(activate) raises the front
    # panel over the diagram and a probe then reads the panel's grey (first batch run).
    lv("-Action", "focus", "-Title", title)
    time.sleep(0.4)
    if windows()[:1] != [title]:
        raise RuntimeError(f"calibrate: '{title}' is not the top window ({windows()[:1]})")
    L, T, R, B = rect(title)
    vp = Viewport(title, L, T, gm["viewport"]["dx"], gm["viewport"]["dy"])
    objs = gm["calibration_objects"].get(name)
    if not objs or len(objs) < 2:
        raise RuntimeError(f"calibrate: no two calibration objects registered for {name}")
    g._lv = None
    for cls, uid in objs[:2]:
        x, y = node_pos(target, uid, cls)
        ok, why = _header_ok(vp, cls, x, y)
        if not ok:
            raise RuntimeError(f"calibrate FAILED on {cls} {uid} at diagram {(x, y)}: {why} — "
                               f"window scrolled/zoomed/other DPI, or offsets wrong")
    return vp


def focus_bd(vp):
    """Focus + one click on registered empty canvas: clears menu mode and absorbs the swallowed
    first mouse-down after activation. Returns True if the BD is the top window afterwards."""
    lv("-Action", "focus", "-Title", vp.title)
    time.sleep(0.3)
    cx, cy = geom()["canvas_click"]
    sx, sy = vp.s(cx, cy)
    act("click", X=sx, Y=sy)
    time.sleep(0.2)
    return windows()[:1] == [vp.title]


# --- verbs ---------------------------------------------------------------------------------------

def move_node(vp, target, uid, cls, dx, dy, tol=6):
    spec = geom()["classes"].get(cls)
    if not spec:
        return {"ok": False, "reason": f"no class geometry for {cls} — measure header colour/size and add to gui-geometry.json"}
    x, y = node_pos(target, uid, cls)
    ok, why = _header_ok(vp, cls, x, y)
    if not ok:
        return {"ok": False, "reason": "grab point is not on the node header: " + why}
    fw, fy = spec["grab"]
    gx, gy = vp.s(x + int(spec["size"][0] * fw), y + fy)
    act("drag", X=gx, Y=gy, X2=gx + dx, Y2=gy + dy)
    time.sleep(0.5)
    nx, ny = node_pos(target, uid, cls)
    ddx, ddy = nx - x, ny - y
    err = ((ddx - dx) ** 2 + (ddy - dy) ** 2) ** 0.5
    return {"ok": err <= tol, "delta": [ddx, ddy], "px_error": round(err, 1), "grab": [gx, gy]}


def _popup_after(before):
    """The visible LabVIEW windows that appeared since `before` (palette / context menu)."""
    seen = {h for _, h, _, _ in before}
    return [w for w in toplevel() if w[1] not in seen]


def place_from_palette(vp, target, item, cls, x, y, tol=12):
    gm = geom()
    pal = gm["palette"]
    entry = pal["items"].get(item)
    if not entry:
        return {"ok": False, "reason": f"no palette geometry for '{item}' — measure it (vision) and add to gui-geometry.json"}
    before_uids = g.uids(target, cls)
    before_win = toplevel()
    px, py = pal["rclick_point"]
    act("rclick", X=px, Y=py); time.sleep(0.9)
    popup = _popup_after(before_win)
    if not popup:
        lv("-Action", "key", "-Key", "esc")
        return {"ok": False, "reason": "no palette popup appeared after the right-click"}
    pl, pt, pr, pb = popup[0][2]
    if entry.get("rel") == "rclick":                       # one-time migration to popup-relative
        entry["steps"] = [dict(st, offset=[px + st["offset"][0] - pl, py + st["offset"][1] - pt]) for st in entry["steps"]]
        entry["rel"] = "popup"; pal["popup_size"] = [pr - pl, pb - pt]; save_geom(gm)
    elif pal.get("popup_size") and (abs(pr - pl - pal["popup_size"][0]) > 3 or abs(pb - pt - pal["popup_size"][1]) > 3):
        lv("-Action", "key", "-Key", "esc")
        return {"ok": False, "reason": f"palette popup size {(pr-pl, pb-pt)} differs from registered {pal['popup_size']}"}
    for st in entry["steps"]:
        ox, oy = st["offset"]
        for _ in range(st.get("clicks", 1)):
            act("click", X=pl + ox, Y=pt + oy); time.sleep(0.8)
    tx, ty = vp.s(x, y)
    act("click", X=tx, Y=ty); time.sleep(0.7)
    lv("-Action", "key", "-Key", "esc")
    new = g.new_since(target, cls, before_uids)
    if len(new) != 1:
        return {"ok": False, "new_nodes": len(new), "popup_rect": [pl, pt, pr, pb]}
    cx, cy = pal["drop_center_offset"]
    nx, ny = new[0]["pos"]
    err = ((nx + cx - x) ** 2 + (ny + cy - y) ** 2) ** 0.5
    return {"ok": err <= tol, "uid": new[0]["uid"], "pos": [nx, ny], "px_error": round(err, 1),
            "popup_rect": [pl, pt, pr, pb]}


VERIFIERS = {
    "exec_state_1_to_0": lambda target, es0: (lambda es1: (es0 == 1 and es1 == 0, {"exec_before": es0, "exec_after": es1}))(g.exec_state(target)),
}


def node_menu(vp, target, uid, cls, row, item):
    """Right-click a node's item row, click a REGISTERED menu item, run its registered verifier."""
    gm = geom()
    spec = gm["classes"].get(cls, {})
    ent = gm["menus"].get(cls, {}).get(item)
    if not ent or ent.get("verify") not in VERIFIERS:
        return {"ok": False, "reason": f"no registered (class,item,verifier) for {cls}/'{item}' — measure it (vision) and add to gui-geometry.json"}
    x, y = node_pos(target, uid, cls)
    ok, why = _header_ok(vp, cls, x, y)
    if not ok:
        return {"ok": False, "reason": "node not at computed position: " + why}
    rcx, rcy = spec.get("row_center", [27, 22])
    qx, qy = vp.s(x + rcx, y + rcy + spec.get("row_pitch", 18) * row)
    es0 = g.exec_state(target)
    before_win = toplevel()
    act("rclick", X=qx, Y=qy); time.sleep(1.0)
    if not _popup_after(before_win):
        lv("-Action", "key", "-Key", "esc")
        return {"ok": False, "reason": "no context menu appeared after the right-click"}
    act("click", X=qx + ent["offset"][0], Y=qy + ent["offset"][1]); time.sleep(0.8)
    ok, info = VERIFIERS[ent["verify"]](target, es0)
    return {"ok": bool(ok), **info}


def dialog_button(title, button, open_with=None, bd=None, wait_ms=1500):
    """Optionally open a dialog with a key combo on the BD, then click a registered button inside
    the dialog's own rect (size-checked). Verified by the window list before/after."""
    gm = geom()
    ent = gm["dialogs"].get(title, {})
    off = ent.get(button)
    if not off:
        return {"ok": False, "reason": f"no dialog geometry for {title}/{button} — measure it (vision) and add to gui-geometry.json"}
    if open_with:
        lv("-Action", "focus", "-Title", bd.title); time.sleep(0.3)
        act("keys", Key=open_with, WaitMs=wait_ms)
    if not any(w.startswith(title) for w in windows()):
        return {"ok": False, "opened": False}
    L, T, R, B = rect(title)
    size = [R - L, B - T]
    if ent.get("size") is None:
        ent["size"] = size; save_geom(gm)
    elif abs(size[0] - ent["size"][0]) > 3 or abs(size[1] - ent["size"][1]) > 3:
        lv("-Action", "key", "-Key", "esc")
        return {"ok": False, "opened": True, "reason": f"dialog size {size} differs from registered {ent['size']}"}
    act("click", X=L + off[0], Y=T + off[1]); time.sleep(0.8)
    closed = not any(w.startswith(title) for w in windows())
    if not closed:
        lv("-Action", "key", "-Key", "esc")
    return {"ok": closed, "opened": True, "closed": closed, "rect": [L, T, R, B]}
