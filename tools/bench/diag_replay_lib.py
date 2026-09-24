r"""diag_replay_lib - helpers shared by diag_replay_standins.py and diag_replay_gbtest.py (card 76-5). No LabVIEW at import.
Every helper is a thin binding to a verb that already exists (checked first, docs/toolkit-capabilities.md + gscript):
walk/term = build_track_v6_core.walk/term (:84-96); str_array_ctl = its string_array_control (:144, NAMES.md:966 "free
String[] control from nothing"); copy_top = stagekit.copy_in (:779) WITHOUT its move_in (the node stays top level);
edges = diag_swap_measure.edges (:30); census = g.subvis per diagram (:549). Nothing here creates an op VI."""
import os, sys, json                                                                     # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                     # noqa: E402
g = K.g
RP = os.path.join(K.CLAUDEDEV, "replay")
BASE = os.path.join(RP, "replay_imaqdx_pane_base.vi"); BASE_MD5 = "65e999d9bd292a892512bc1caf57e0e4"
BUF, CAL = os.path.join(RP, "replay_imaqdx_get_image_buf.vi"), os.path.join(RP, "replay_get_image_cal.vi")
GBF = os.path.join(RP, "replay_get_buff_image.vi")
GB = os.path.join(K.CLAUDEDEV, "background VIs_COPY", "get buff image-lost frames.vi")
GB_ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs\get buff image-lost frames.vi"
GI = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Get Image.vi"
LIB = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\NI_Vision_Acquisition_Software.lvlib"
S1 = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
R_VI, C_VI, A_VI = [os.path.join(VIS, a, b) for a, b in (("Files.llb", "IMAQ ReadFile"), ("Basics.llb", "IMAQ Create"),
                                                           ("Basics.llb", "IMAQ ImageToArray"))]
S_VI = os.path.join(K.CLAUDEDEV, "StrToPath.vi"); EMPTY = os.path.join(K.CLAUDEDEV, "EMPTY_v0.vi")
GC = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Get Controls.vi"
FR = r"G:\m8_replay_frames"; MAN = os.path.join(FR, "frames_manifest.json"); N_FR = 10044


# card 77-4: tools/stage_prerun.py --dry runs a recipe with gscript STUBBED (every stub carries `_dry`). The readers
# below then see only the pane-base graph, so a lookup of a CREATED object finds nothing. In DRY only, the lookup
# helpers return a placeholder instead of raising; in a real run they raise exactly as before (no behaviour change).
DRY = bool(getattr(getattr(g, "wire", None), "_dry", False))
DUMMY = {"i": 0, "name": "", "is_source": False, "wire": 0, "uid": 0}


class _Walk(dict):
    def __missing__(self, k):
        if DRY:
            return (0, "", [])
        raise KeyError(k)


def new1(t, cls, before):
    """the ONE uid of class `cls` on `t` that is not in `before` (raises on 0 or >1; DRY: 0)"""
    n = sorted(x for x in g.uids(t, cls) if x not in before)
    if len(n) != 1:
        if DRY:
            return 0
        raise RuntimeError("new1 {0}: {1} new {2}".format(os.path.basename(str(t)), n, cls))
    return n[0]


def new_label(t, before, indicator):
    n = [l for _i, l, ind in g.fp_labels(t) if bool(ind) == bool(indicator) and l not in before]
    if not n:
        if DRY:
            return ""
        raise RuntimeError("new_label: no new {0}".format("indicator" if indicator else "control"))
    return n[-1]


def copy_to(s, cls, uid, dest_diag_uid, pos, tag):
    """copy_top + (dest_diag_uid) move_in into that diagram + junk purge = stagekit.copy_in:779 with DRY-safe lookups"""
    u = copy_top(s, cls, uid, tag)
    if dest_diag_uid is not None:
        di = diag_index(s.work, dest_diag_uid)
        s.move_in(u, di, tuple(pos)); s.junk_purge(tag + " after move_in", hints=[di, 0])
    return u


def pins():
    return (("vi.lib GI", GI, K.md5(GI)), ("lvlib", LIB, K.md5(LIB)), ("get-buff copy", GB, K.md5(GB)),
            ("get-buff orig", GB_ORIG, K.md5(GB_ORIG)), ("pane base", BASE, BASE_MD5), ("manifest", MAN, K.md5(MAN)),
            ("S1", S1, S1_MD5))


def walk(t, d=0):
    labels = {r["uid"]: r["label"] for r in g.node_labels(t, d)}
    out = _Walk()
    for n in range(80):
        u, rows = g.node_terms_uid(t, d, n)
        if not u:
            break
        out[int(u)] = (n, labels.get(u), rows)
    return out


def term(rows, name, source):
    return next((r for r in rows if r["name"] == name and bool(r["is_source"]) == bool(source)), dict(DUMMY) if DRY else None)


def tname(rows, pred, source):
    """the one terminal name satisfying pred(name) with the given direction (raises on 0 or >1)"""
    h = [r["name"] for r in rows if pred(r["name"]) and bool(r["is_source"]) == bool(source)]
    if len(h) != 1:
        if DRY:
            return ""
        raise RuntimeError("terminal pick: {0} hits in {1}".format(h, [(r["name"], r["is_source"]) for r in rows]))
    return h[0]


def _ix(lst, v):
    if DRY and v not in lst:
        return 0
    return lst.index(v)


def fidx(t, cls, uid):
    return _ix([int(o["uid"]) for o in g.report_all(t, cls)], int(uid))


def diag_index(t, uid):
    return _ix([int(o["uid"]) for o in g.report_all(t, "Diagram")], int(uid))


def donor_class(uid):
    if DRY:                                  # the dry graph is the pane base, not the donor S1
        return "Function"
    for c in ("Function", "Node"):
        if int(uid) in [int(o["uid"]) for o in g.report_all(g.MOVE_SRC, c)]:
            return c
    return None


def copy_top(s, cls, uid, tag):
    """stagekit.copy_in:779 minus move_in: OpMoveByIndex_v0 duplicate=True with the UID guard; the copy stays top level."""
    idx = fidx(g.MOVE_SRC, cls, uid); before = set(int(o["uid"]) for o in g.report_all(s.work, cls))
    lab = json.load(open(os.path.join(K.BENCH, "opmovebyindex_labels.json"), encoding="utf-8")); s.node_mark(tag)
    vi = g.op(g.OP_MOVE_INDEX)
    for k, v in (("class_name", cls), ("index", int(idx)), ("duplicate", True), ("traverse_target", 1)):
        vi.SetControlValue(lab[k], v)
    g._run(vi); sel = int(vi.GetControlValue(lab["selected_uid"]))
    new = sorted(set(int(o["uid"]) for o in g.report_all(s.work, cls)) - before)
    s.gate("{0} copy #{1}: UID guard and exactly one new {2}".format(tag, uid, cls), sel == int(uid) and len(new) == 1,
           (sel, new), fatal=True)
    s.junk_purge(tag); return new[0] if new else 0                                   # DRY: the fatal gate did not raise


def str_array_ctl(s, t, tag):
    before_sub = g.uids(t, "SubVI"); g.drop_subvi(t, GC, 0, (200, 700))
    u = new1(t, "SubVI", before_sub); wt = walk(t, 0)
    b = {l for _i, l, ind in g.fp_labels(t) if not ind}
    g.create_control(t, wt[u][0], term(wt[u][2], "Control Names", False)["i"])
    label = new_label(t, b, False)
    g.delete_object(t, "Wire", fidx(t, "Wire", pwire(t, label)), verify=False)
    g.delete_object(t, "SubVI", fidx(t, "SubVI", u), verify=False); g.remove_bad_wires_scripted(t)
    s.gate("{0} free String[] control {1!r}".format(tag, label), pwire(t, label) == 0, fatal=True)
    return label


def pwire(t, label):
    """the wire uid on panel object `label` (panel_wiring; raises if absent; DRY: 0)"""
    pw = {r["label"]: r for r in g.panel_wiring(t)}
    if label not in pw:
        if DRY:
            return 0
        raise KeyError(label)
    return pw[label]["wire"]


def pidx(t, label):
    return _ix([l for _i, l, _ind in g.fp_labels(t)], label)


def pane_dirs(t):
    """{slot: (label, is_indicator)} over the connector pane (label + direction; K3 of 76-4)"""
    fp = {l: ind for _i, l, ind in g.fp_labels(t)}
    return dict((int(k), (v, fp.get(v))) for k, v in g.conpane(t).items())


def edges(live, remap):
    own = lambda r: remap.get(r["owner_uid"], r["owner_uid"])                        # noqa: E731
    by = {}
    for r in live["terminals"]:
        if r["wire_uid"]:
            by.setdefault(r["wire_uid"], []).append(r)
    return set((own(a), a["term_name"], own(b), b["term_name"]) for rs in by.values() for a in rs if a["is_source"]
               for b in rs if not b["is_source"])


def census(t):
    out = {}
    for d in range(len(g.report_all(t, "Diagram"))):
        for x in g.subvis(t, d):
            out[int(x["uid"])] = x["path"]
    return out


def tail(s, fxl=None, bad=()):
    """once per run, just before the RESULT line: Moving-Objects pair restored and proven (stagekit.fixtures_check),
    LabVIEW killed and verified gone (card: 'LabVIEW gone'; CLAUDE.md 1b grant: every run ends with LabVIEW closed)."""
    if getattr(s, "_tail_done", False):
        return
    s._tail_done = True
    import subprocess, time                                                              # noqa: E401
    if fxl is not None:
        K.mod("bench_prep").restart_labview(); g.reset(); g.restore_move_fixtures()
        s.gate("H8 Moving-Objects pair restored to its .ORIG.bak, listing unchanged", K.fixtures_check(bad, fxl))
    g.reset()
    subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
                   capture_output=True)
    time.sleep(6)
    s.gate("H9 LabVIEW gone", "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True,
                                                                  errors="replace").stdout)
    s.dump()


def frame_paths():
    return [os.path.join(FR, "f{0:05d}.tif".format(i)) for i in range(N_FR)]
