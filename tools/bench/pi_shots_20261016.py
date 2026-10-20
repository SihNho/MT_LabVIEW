# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/brief_chat-PI1.md
# ---
r"""pi_shots_20261016.py - card chat-PI1c step 3: PNG crops (native scale, Image Depth 24) of the key block-diagram
regions of three VIs for the PI, through claudeDev\OpGetImage_v0.vi (pi_shots_lib.get_image). Brief: brief_chat-PI1.md.

EXISTING FIRST: the op and its wrapper are this card's own (tools/recipes/build_op_getimage_v0.py, pi_shots_lib.get_image);
crop arithmetic pi_shots_lib.rect / crop_box (self-tested). d0_locate.save_crop upsamples (scale=4) - not used (native).
Sources are opened ONLY as byte copies in claudeDev\shots_20261016\ (rule 1); nothing is run except the op; copies are
never saved (LabVIEW is killed at the end) and deleted; source md5 before and after.

WHAT (UIDs read from the VI, never assumed - each shot checks the op's UID echo):
  A  ORIGINAL 2f048e3a (card chat-PI1e, brief_chat-PI1e.md: #22700 DROPPED - it came from a working-copy doc): the
     frame loop = the WhileLoop that OWNS both #6810 and #5058, found by the owner chain (build_d1_v0.owner_of =
     OpOwnerChain_v1, uid -> owner class/uid, walked up to the first WhileLoop); different loops -> fatal, both chains
     reported. Optional members = subVI calls whose name says save / plot / pixmap / draw / write / graph / trace / file
     (names: gscript.subvis over every Traverse 'Diagram'), owned by that loop. Only members whose owner chain up to the
     loop crosses NO Case / Event / Stacked-Sequence frame are used for the crop (a member in another frame is not drawn);
     the others are listed as notes. A1 = #6810 + #5058 + the nearest visible members while the box stays <= 1800 x 1100,
     grown to >= 1400 x 900 around its centre for context; A2 = the remaining visible members (tiled if larger).
  B  P6-1 c2d9c13c: loop 1.2 While #10170; the reader region = Locals BufDiff #30294 TransPos #30116 RotPos #30215
     FrameIdx #30239 + IndexArrays #30300 #30119 #30216 #30240, pick RingPickSlot #29719, n2 Flat Sequence #29721,
     RingSeqCheck #29724 (lean_report_p6fix.md section 1).
  C  CURRENT 15c664e3: the same uids in While #10170 (after the fix); uids not found are listed, not guessed.
  D  CURRENT: loop 1.1 writer Flat Sequence #27509, whole structure.
PREDICTION (gates): S0 sources md5 == pins; S1 copies md5 == pins; per shot E echo == uid and no op error; I raw image
size vs the structure's Bounds (MEASURED, gated equal within 4 px so the crop offset = the structure's top-left holds);
P each crop file is 24-bit RGB, <= 1800 x 1100 (larger regions are split into tiles, never shrunk); A owner chains of
#6810 and #5058 reach the SAME WhileLoop; B/C/D every listed uid is found (else fatal + the structure's Traverse
neighbours class/uid/pos listed, no guessing); X sources md5 after ==
before; H handles at the end vs after-restart (recorded); G LabVIEW gone; K copies deleted.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/pi_shots_20261016.log -- py -u tools/bench/pi_shots_20261016.py
"""
import json, os, shutil, sys, time, tempfile                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(os.path.dirname(HERE)))     # noqa: E702
import pi_shots_lib as L                                                             # noqa: E402
import gscript as g                                                                  # noqa: E402
from PIL import Image                                                                # noqa: E402
TR = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
CD = g.CLAUDEDEV
SHOTDIR = os.path.join(CD, "shots_20261016")
SRC = {
    "orig": (os.path.join(TR, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi"), "2f048e3a18de3b5e3ca8368f6a24dae0"),
    "p61": (os.path.join(CD, "D1_ring_p6_20261012_212645.vi"), "c2d9c13cb40c0a5cab7433896d1df157"),
    "cur": (os.path.join(CD, "bench", "lean", "D1_ring_p6latest_20261014_010104.vi"), "15c664e3eed1c580e05b13e42c86566f"),
}
READER = [30294, 30116, 30215, 30239, 30300, 30119, 30216, 30240, 29719, 29721, 29724]
MAXW, MAXH, PAD = 1800, 1100, 40
TMP = os.path.join(tempfile.gettempdir(), "pi_shot_node.png")
s = L.Rec("pi_shots_20261016")
SHOTS = []


def tiles(box):
    """Split a crop box into tiles <= MAXW x MAXH (native scale, no shrinking)."""
    l, t, r, b = box
    nx, ny = -(-(r - l) // MAXW), -(-(b - t) // MAXH)
    w, h = -(-(r - l) // nx), -(-(b - t) // ny)
    return [(l + i * w, t + j * h, min(r, l + (i + 1) * w), min(b, t + (j + 1) * h)) for j in range(ny) for i in range(nx)]


class Copy(object):
    def __init__(s2, key):
        src, pin = SRC[key]
        s2.key, s2.src = key, src
        s2.path = os.path.join(SHOTDIR, "%s_%s" % (key, os.path.basename(src)))
        shutil.copyfile(src, s2.path)
        s.gate("S1 %s copy md5 == pin %s" % (key, pin[:8]), L.md5(s2.path) == pin, L.md5(s2.path), fatal=True)
        g.ensure_loaded(s2.path)
        s2.rows = g.report_all(s2.path, "Node")
        s2.order = [int(o["uid"]) for o in s2.rows]
        s.fact("%s loaded: %d Nodes (Traverse order)" % (key, len(s2.order)))

    def shot(s2, uid, png):
        if uid not in s2.order:
            return None
        r = L.get_image(s2.path, uid, png, cls="Node", index=s2.order.index(uid))
        ok = r["echo"] == uid and not (r["err_png"] or r["err_pn"] or r["err_echo"]) and r.get("rect")
        s.gate("E %s #%s echo %s, errors '%s|%s|%s', rect %s" % (s2.key, uid, r["echo"], r["err_png"][:60], r["err_pn"][:60],
                                                               r["err_echo"][:60], r.get("rect")), ok)
        return r if ok else None


def grow(box, min_w, min_h, img_size):
    """Grow a crop box around its centre to at least min_w x min_h (clipped to the image; never shrinks)."""
    l, t, r, b = box
    w, h = max(r - l, min(min_w, img_size[0])), max(b - t, min(min_h, img_size[1]))
    cx, cy = (l + r) // 2, (t + b) // 2
    l2 = min(max(0, cx - w // 2), img_size[0] - w); t2 = min(max(0, cy - h // 2), img_size[1] - h)  # noqa: E702
    return (l2, t2, l2 + w, t2 + h)


def neighbours(c, st_rect, limit=80):
    """Traverse('Node') objects whose Position lies inside a structure's rect: (class, uid, pos) - reported, never used."""
    R = st_rect
    return [(o["class"], int(o["uid"]), tuple(o["pos"])) for o in c.rows
            if R[0] <= o["pos"][0] <= R[2] and R[1] <= o["pos"][1] <= R[3]][:limit]


def struct_image(c, label, struct_uid):
    raw = os.path.join(L.OUTDIR, "raw_%s_%s_%s.png" % (label, c.key, struct_uid))
    st = c.shot(struct_uid, raw)
    s.gate("%s structure #%s found and imaged" % (label, struct_uid), bool(st), "missing from Traverse('Node') or op error",
           fatal=True)
    im = Image.open(raw); sw, sh = st["rect"][2] - st["rect"][0], st["rect"][3] - st["rect"][1]  # noqa: E702
    s.fact("%s raw %s: image %s mode %s vs Bounds %sx%s (rect %s)" % (label, os.path.basename(raw), im.size, im.mode, sw, sh, st["rect"]))
    s.gate("I %s raw image size == structure Bounds within 4 px" % label, abs(im.size[0] - sw) <= 4 and abs(im.size[1] - sh) <= 4,
           (im.size, (sw, sh)), fatal=True)
    return st, im, raw


def region(c, label, struct_uid, nodes, desc, img=None, min_size=None, notes=None):
    st, im, raw = img or struct_image(c, label, struct_uid)
    rects, missing = [], []
    for u in nodes:
        r = st if u == struct_uid else c.shot(u, TMP)
        (rects.append(r["rect"]) if r else missing.append(u))
    if missing:
        s.fact("%s Traverse neighbours inside #%s (class, uid, pos): %s" % (label, struct_uid, neighbours(c, st["rect"])))
    s.gate("%s every listed uid found in %s" % (label, c.key), not missing, missing, fatal=True)
    box = L.crop_box(st["rect"], rects, pad=PAD, img_size=im.size)
    if min_size:
        box = grow(box, min_size[0], min_size[1], im.size)
    parts = tiles(box)
    for k, tb in enumerate(parts):
        name = "%s%s.png" % (desc[0], "" if len(parts) == 1 else "_part%d" % (k + 1))
        out = os.path.join(L.OUTDIR, name)
        crop = im.convert("RGB").crop(tb); crop.save(out)                             # noqa: E702
        s.gate("P %s %s %sx%s <= %sx%s, RGB" % (label, name, crop.size[0], crop.size[1], MAXW, MAXH),
               crop.size[0] <= MAXW and crop.size[1] <= MAXH and crop.mode == "RGB")
        SHOTS.append({"file": name, "source": c.src, "source_md5": SRC[c.key][1], "copy": c.path, "struct_uid": struct_uid,
                      "struct_rect": st["rect"], "raw": os.path.basename(raw), "raw_size": im.size, "uids": nodes,
                      "uids_missing": missing, "node_rects": rects, "crop_box": tb, "px": crop.size, "description": desc[1],
                      "notes": list(notes or [])})
        s.arts.append(out)


KEYWORDS = ("save", "plot", "pixmap", "draw", "write", "graph", "trace", "file")
FRAMED = ("CaseStructure", "EventStructure", "StackedSequence")
_OWN = {}


def owner_of(c, uid):
    """(owner class, owner uid) of #uid on copy c - OpOwnerChain_v1 via build_d1_v0.owner_of (non-strict), cached."""
    k = (c.path, int(uid))
    if k not in _OWN:
        g._c97_paths()
        import build_d1_v0 as B
        cls, ou = B.owner_of(c.path, int(uid), strict=False)
        _OWN[k] = (str(cls), int(ou or 0))
    return _OWN[k]


def chain(c, uid, stop_uid=None, n=14):
    """Owner chain of #uid upward: [(class, uid), ...] ending at the first WhileLoop (stop_uid None) or at #stop_uid,
    or at TopLevelDiagram / an empty answer."""
    out, u = [], int(uid)
    for _ in range(n):
        cls, ou = owner_of(c, u)
        out.append((cls, ou))
        if not ou or cls in ("", "POISON", "TopLevelDiagram") or (stop_uid is None and cls == "WhileLoop") or ou == stop_uid:
            break
        u = ou
    return out


def greedy(seed_rects, cands):
    """Add candidates (uid, rect) nearest-first to seed_rects while the padded union stays <= MAXW x MAXH.
    Returns (taken uids, left (uid, rect))."""
    rs, taken, left = list(seed_rects), [], []
    cx = sum((r[0] + r[2]) / 2.0 for r in rs) / len(rs); cy = sum((r[1] + r[3]) / 2.0 for r in rs) / len(rs)  # noqa: E702
    for u, r in sorted(cands, key=lambda x: abs((x[1][0] + x[1][2]) / 2.0 - cx) + abs((x[1][1] + x[1][3]) / 2.0 - cy)):
        tr = rs + [r]
        w = max(q[2] for q in tr) - min(q[0] for q in tr) + 2 * PAD; h = max(q[3] for q in tr) - min(q[1] for q in tr) + 2 * PAD  # noqa: E702
        if w <= MAXW and h <= MAXH:
            rs.append(r); taken.append(u)                                            # noqa: E702
        else:
            left.append((u, r))
    return taken, left


def part_a(c):
    """Crop A (brief_chat-PI1e.md): the While owning #6810 and #5058, plus the visible save/plot subVI calls."""
    ch = {u: chain(c, u) for u in (6810, 5058)}
    s.fact("A owner chain #6810: %s" % ch[6810]); s.fact("A owner chain #5058: %s" % ch[5058])  # noqa: E702
    w = [x[-1][1] if x and x[-1][0] == "WhileLoop" else None for x in (ch[6810], ch[5058])]
    s.gate("A #6810 and #5058 owned by the SAME WhileLoop", w[0] is not None and w[0] == w[1], w, fatal=True)
    W = w[0]
    framed_req = {u: [x for x in ch[u][:-1] if x[0] in FRAMED] for u in ch}
    notes = ["#%s sits inside %s (frame shown in the image is the one LabVIEW last displayed)" % (u, f) for u, f in framed_req.items() if f]
    # subVI names over every Diagram (SubVIs[] is per diagram, not recursive - gscript.subvis docstring)
    dias = g.report_all(c.path, "Diagram")
    names = {}
    for i, d in enumerate(dias):
        rows, err = g.subvis(c.path, i, strict=False)
        for r in rows:
            names[int(r["uid"])] = (r["name"], int(d["uid"]), d["class"])
    s.fact("A subVI calls named over %d diagrams: %d" % (len(dias), len(names)))
    s.R["A_subvi_names"] = dict((str(k), v) for k, v in names.items())
    s.fact("A names of #6810 / #5058: %s / %s" % (names.get(6810), names.get(5058)))
    cand = [(u, v) for u, v in names.items() if u not in (6810, 5058) and any(k in v[0].lower() for k in KEYWORDS)]
    vis, hidden, outside = [], [], []
    for u, (nm, du, dcls) in cand:
        cc = [(dcls, du)] + chain(c, du, stop_uid=W)
        if not any(x[1] == W for x in cc):
            outside.append((u, nm))
        elif any(x[0] in FRAMED for x in cc[:-1]) or dcls in FRAMED:
            hidden.append((u, nm, [x for x in cc if x[0] in FRAMED]))
        else:
            vis.append((u, nm))
    s.fact("A save/plot members in While #%s, visible (no frame on the chain): %s" % (W, vis))
    s.fact("A save/plot members in While #%s inside a Case/Event/Stacked frame (not used for the crop): %s" % (W, hidden))
    s.fact("A save/plot calls outside While #%s: %s" % (W, outside))
    s.R["A"] = {"while": W, "chains": dict((str(k), v) for k, v in ch.items()), "visible": vis, "framed": hidden, "outside": outside}
    img = struct_image(c, "A", W)
    req = [c.shot(u, TMP) for u in (6810, 5058)]
    s.gate("A #6810 and #5058 imaged (rects)", all(req), [bool(r) for r in req], fatal=True)
    vr = []
    for u, nm in vis:
        r = c.shot(u, TMP)
        if r:
            vr.append((u, r["rect"]))
    taken, left = greedy([r["rect"] for r in req], vr)
    nm = dict((u, n) for u, n in vis)
    notes_h = notes + ["in a frame, not cropped: %s" % ", ".join("#%s %s" % (u, n) for u, n, _f in hidden)] if hidden else notes
    region(c, "A1", W, [6810, 5058] + taken,
           ("A1_original_frame_loop", "ORIGINAL frame loop While #%s: camera buffer #6810 (%s) and tracking kernel #5058 (%s) in ONE loop, with %s"
            % (W, (names.get(6810) or ("?",))[0], (names.get(5058) or ("?",))[0],
               ", ".join("#%s %s" % (u, nm[u]) for u in taken) or "no save/plot call within the crop size")),
           img=img, min_size=(1400, 900), notes=notes_h)
    if left:
        t2, left2 = greedy([left[0][1]], left[1:])
        a2 = [left[0][0]] + t2
        region(c, "A2", W, a2, ("A2_original_frame_loop_save", "ORIGINAL frame loop While #%s (same loop as A1): save / plot calls %s"
                                % (W, ", ".join("#%s %s" % (u, nm[u]) for u in a2))), img=img, min_size=(1400, 900),
               notes=(["not in A1/A2 (crop size): %s" % ", ".join("#%s %s" % (u, nm[u]) for u, _r in left2)] if left2 else []))


def main():
    os.makedirs(SHOTDIR, exist_ok=True); os.makedirs(L.OUTDIR, exist_ok=True)       # noqa: E702
    before = {k: L.md5(p) for k, (p, _m) in SRC.items()}
    s.gate("S0 sources md5 == pins", all(before[k] == SRC[k][1] for k in SRC), before, fatal=True)
    s.R["md5_before"] = before
    s.head("[0] restart LabVIEW"); h0 = L.restart(); s.fact("handles after restart %s" % h0)  # noqa: E702
    s.R["handles_start"] = h0
    s.head("[A] original frame loop")
    c = Copy("orig")
    part_a(c)
    s.head("[B] P6-1 loop 1.2 reader")
    c = Copy("p61")
    region(c, "B", 10170, READER, ("B_p6-1_reader_before_fix", "P6-1 loop 1.2 (While #10170) ring reader: Locals BufDiff/TransPos/RotPos/FrameIdx + IndexArrays read OUTSIDE the seqlock (pick #29719 = n1, Flat Sequence #29721 / RingSeqCheck #29724 = n2)"))
    s.head("[C,D] current")
    c = Copy("cur")
    region(c, "C", 10170, READER, ("C_current_reader_after_fix", "CURRENT loop 1.2 (While #10170) after the fix: the four Locals + IndexArrays inside a new frame of Flat Sequence #29721, between n1 and n2"))
    region(c, "D", 27509, [27509], ("D_current_writer_loop11", "CURRENT loop 1.1 ring WRITER: Flat Sequence #27509, frames d27641 | d32464 | d27722 (Num=-1 | slot arrays | Num=BufNum)"))
    json.dump(SHOTS, open(os.path.join(L.OUTDIR, "shots.json"), "w", encoding="utf-8"), indent=1, default=list)
    s.arts.append(os.path.join(L.OUTDIR, "shots.json"))
    s.R["shots"] = [x["file"] for x in SHOTS]
    try:
        s.fact("H handles at end %s (after restart %s); refs %s" % (L.handles(), h0, g.ref_counts()))
    except Exception:                                                                # noqa: BLE001
        pass


try:
    main()
except L.StopRun as e:
    s.fact("STOPPED at gate: %s" % e)
except Exception as e:                                                               # noqa: BLE001
    import traceback; traceback.print_exc(); s.gate("the run completed without an unhandled exception", False, str(e)[:200])  # noqa: E702
s.gate("G LabVIEW gone at exit (killed, nothing saved)", L.kill_and_verify())
left = []
if os.path.isdir(SHOTDIR):
    for f in os.listdir(SHOTDIR):
        try:
            os.remove(os.path.join(SHOTDIR, f))
        except Exception:                                                            # noqa: BLE001
            left.append(f)
    try:
        os.rmdir(SHOTDIR)
    except Exception:                                                                # noqa: BLE001
        left.append(SHOTDIR)
s.gate("K copies deleted", not left, left)
after = {k: L.md5(p) for k, (p, _m) in SRC.items()}
s.gate("X sources md5 after == pins", all(after[k] == SRC[k][1] for k in SRC), after)
sys.exit(s.finish(os.path.join(L.OUTDIR, "pi_shots_20261016.json")))
