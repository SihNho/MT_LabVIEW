# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/brief_chat-PI1f.md
# ---
r"""pi_shots_20261019.py - card chat-PI1f: RAW Node.Get Image PNGs (Image Depth 24, no crop) of P6-1 and P6L for the PI.
Brief: tools/bench/cards/brief_chat-PI1f.md. Retry of chat-PI1e (result_chat-PI1e.json).

EXISTING FIRST (checked 2026-10-19): image = pi_shots_lib.get_image (claudeDev\OpGetImage_v0.vi b7c5667b, as built);
owner hop = build_d1_v0.owner_of (OpOwnerChain_v1; MEASURED limit: a FlatSequenceFrame owner returns uid 0,
docs/toolkit-capabilities.md:66) - bridged here by the FlatSequence census report_all('FlatSequence') + gscript.fs_frames
(OpFsDiagrams_v0: frame Diagram uids per FS), because a FlatSequence is a GObject, not a Node (toolkit-capabilities.md:627);
case frames = gscript.case_frames (OpCaseFrames_v1); subVI names = gscript.subvis per Diagram. Copy/load/shot helpers are
the same pattern as pi_shots_20261016.py (Copy, shot) - that script's main() runs unconditionally at import, so it is not
importable; the shared pieces it uses all live in pi_shots_lib (Rec, get_image, md5, restart, kill_and_verify).
NOT FOUND: any op that WRITES (or reads) MultiFrameStructure.Visible Frame 6363800 (grep of tools/*.py, tools/bench/*.py,
docs/vi-server-ids.json, claudeDev Op*.vi list: none). A new op would need an op-hygiene record under tools/bench/op_hygiene
(gscript.op_hygiene_check), outside this card's write globs, and the card says "no workaround". So this script SETS NO
visible frame: every Case on a chain is reported with its frame names, frame uids and the frame index that holds the
chain; gate V fails if any such Case exists (the image then shows whatever frame the file was saved with).

WHAT, on each of P6-1 (c2d9c13c) and P6L (54f7cd2f), byte copies in claudeDev\shots_20261016 (never saved, deleted):
  R  owner chains of the reader uids #30294 #30116 #30215 #30239 + seqlock reads #30300 #30119 #30216 #30240 #29719 #29724
     up to the top; innermost Node structure (While/For/Case/Event/Sequence) common to #30294 #30116 #30215 #30239 ->
     raw_R_<vi>_<uid>.png; loop 1.2 (While #10170 when it is on the #30239 chain, else the first While on it) ->
     raw_L12_<vi>.png; every Case on a reader chain -> raw_C_<vi>_<uid>.png; each reader node alone -> raw_N_<vi>_<uid>.png.
  W  (P6L) every WhileLoop -> raw_W_P6L_<uid>.png, with Bounds and the names of the subVI calls inside it (nested included).
  D  (P6L) writer FS #27509: in the FlatSequence census? its frames; owner chains of Locals #29175 #29380 #29312 #29683;
     the first Node structure above them -> raw_D_P6L_<uid>.png.
PREDICTION (gates): S0 source md5 == pins; S1 copy md5 == pins; E per shot: echo == uid, no op error; I raw image size ==
Bounds within 4 px; R1 the four Locals present in Traverse('Node') of each copy (absent -> FACT with what is there, gate
FAIL); R2 a common Node structure exists; V no Case on any reader chain whose frame could not be made visible (FAILS when a
Case is on a chain - no writer op, see above); W1 >= 1 WhileLoop in P6L; D1 the four writer Locals present; X sources md5
after == before; H handles recorded; G LabVIEW gone; K copies deleted.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/pi_shots_20261019.log -- py -u tools/bench/pi_shots_20261019.py
"""
import json, os, shutil, sys                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))                 # noqa: E702
import pi_shots_lib as L                                                             # noqa: E402
import gscript as g                                                                  # noqa: E402
from PIL import Image                                                                # noqa: E402
CD = g.CLAUDEDEV
SHOTDIR = os.path.join(CD, "shots_20261016")
SRC = {
    "P61": (os.path.join(CD, "D1_ring_p6_20261012_212645.vi"), "c2d9c13cb40c0a5cab7433896d1df157"),
    "P6L": (os.path.join(CD, "bench", "lean", "D1_ring_fxdP6L_20261016_115105.vi"), "54f7cd2f27175b3aa993a2e7630cff40"),
}
LOCALS = [30294, 30116, 30215, 30239]
SEQ = [30300, 30119, 30216, 30240, 29719, 29724]
WRITER_LOCALS = [29175, 29380, 29312, 29683]
NODE_STRUCT = ("WhileLoop", "ForLoop", "CaseStructure", "EventStructure", "Sequence", "StackedSequence", "TimedLoop")
s = L.Rec("pi_shots_20261019")
SHOTS = []


class Copy(object):
    def __init__(c, key):
        src, pin = SRC[key]
        c.key, c.src, c.pin = key, src, pin
        c.path = os.path.join(SHOTDIR, "%s_%s" % (key, os.path.basename(src)))
        shutil.copyfile(src, c.path)
        s.gate("S1 %s copy md5 == pin %s" % (key, pin[:8]), L.md5(c.path) == pin, L.md5(c.path), fatal=True)
        g.ensure_loaded(c.path)
        c.rows = g.report_all(c.path, "Node")
        c.order = [int(o["uid"]) for o in c.rows]
        c.cls = dict((int(o["uid"]), str(o["class"])) for o in c.rows)
        s.fact("%s loaded: %d Nodes (Traverse order)" % (key, len(c.order)))
        c.own, c.fs_of_diag, c.fs = {}, {}, []
        g._c97_paths()
        import build_d1_v0 as B
        c.B = B

    def census_fs(c):
        """{frame Diagram uid: FlatSequence uid} over every FlatSequence (the bridge over the FlatSequenceFrame hop)."""
        c.fs = [int(o["uid"]) for o in g.report_all(c.path, "FlatSequence")]
        frames = {}
        for f in c.fs:
            r = g.fs_frames(c.path, f)
            frames[f] = r["frames"]
            for d in r["frames"]:
                c.fs_of_diag[int(d)] = f
        s.fact("%s FlatSequence census: %d FS, %d frame diagrams" % (c.key, len(c.fs), len(c.fs_of_diag)))
        return frames

    def owner(c, uid):
        if uid not in c.own:
            cls, ou = c.B.owner_of(c.path, int(uid), strict=False)
            c.own[uid] = (str(cls), int(ou or 0))
        return c.own[uid]

    def chain(c, uid, n=20):
        """[(class, uid), ...] from #uid's owner upward to the top; a FlatSequenceFrame hop (uid 0) is bridged by the census."""
        out, u = [], int(uid)
        for _ in range(n):
            cls, ou = c.owner(u)
            if cls == "FlatSequenceFrame" and not ou and u in c.fs_of_diag:
                out.append(("FlatSequenceFrame", 0)); f = c.fs_of_diag[u]; out.append(("FlatSequence", f)); u = f  # noqa: E702
                continue
            out.append((cls, ou))
            if not ou or cls in ("", "POISON", "TopLevelDiagram"):
                break
            u = ou
        return out

    def shot(c, uid, png):
        if uid not in c.order:
            s.gate("E %s #%s in Traverse('Node')" % (c.key, uid), False, "absent")
            return None
        r = L.get_image(c.path, uid, png, cls="Node", index=c.order.index(uid))
        ok = r["echo"] == uid and not (r["err_png"] or r["err_pn"] or r["err_echo"]) and r.get("rect")
        s.gate("E %s #%s echo %s, errors '%s|%s|%s'" % (c.key, uid, r["echo"], r["err_png"][:60], r["err_pn"][:60],
                                                       r["err_echo"][:60]), ok)
        if not ok:
            return None
        im = Image.open(png); w, h = r["bounds"][0], r["bounds"][1]                   # noqa: E702
        if len(r["bounds"]) == 4:
            w, h = r["bounds"][2] - r["bounds"][0], r["bounds"][3] - r["bounds"][1]
        s.gate("I %s #%s image %s == Bounds %sx%s within 4 px" % (c.key, uid, im.size, w, h),
               abs(im.size[0] - w) <= 4 and abs(im.size[1] - h) <= 4)
        r["size"], r["mode"] = im.size, im.mode
        return r


def record(c, png, uid, what, frames_note, extra=None):
    r = c.shot(uid, png)
    row = {"file": os.path.basename(png), "source": c.src, "source_md5": c.pin, "uid": uid, "class": c.cls.get(uid),
           "position": r and r["position"], "bounds": r and r["bounds"], "size": r and r["size"], "mode": r and r["mode"],
           "case_frames_made_visible": [], "case_frames_note": frames_note, "content": what}
    row.update(extra or {})
    SHOTS.append(row)
    if r:
        s.arts.append(png)
    return r


def cases_on(c, ch):
    """Every CaseStructure on a chain with the Diagram just below it = the frame that holds the chain."""
    out = []
    for k, (cls, u) in enumerate(ch):
        if cls == "CaseStructure" and k > 0:
            d = ch[k - 1][1]
            fr = g.case_frames(c.path, u)
            idx = fr["frames"].index(d) if d in fr["frames"] else None
            out.append({"case": u, "frame_diagram": d, "frame_index": idx, "names": fr["names"], "frames": fr["frames"],
                        "err": fr["err"]})
    return out


def part_r(c):
    s.head("[R] %s reader chains" % c.key)
    have = [u for u in LOCALS + SEQ if u in c.order]
    miss = [u for u in LOCALS + SEQ if u not in c.order]
    s.fact("%s reader uids present %s, absent %s" % (c.key, have, miss))
    if miss:
        lo = [(int(o["uid"]), str(o["class"])) for o in c.rows if str(o["class"]) == "Local"]
        s.fact("%s Locals present (uid, class): %s" % (c.key, lo[:120]))
    s.gate("R1 %s the four reader Locals present" % c.key, all(u in c.order for u in LOCALS), miss)
    ch = {u: c.chain(u) for u in have}
    for u in have:
        s.fact("%s chain #%s (%s): %s" % (c.key, u, c.cls.get(u), ch[u]))
    s.R.setdefault("chains", {})[c.key] = dict((str(k), v) for k, v in ch.items())
    loc = [u for u in LOCALS if u in ch]
    common = None
    if loc:
        sets = [set(x[1] for x in ch[u] if x[0] in NODE_STRUCT) for u in loc]
        for cls, u in ch[loc[-1]]:
            if cls in NODE_STRUCT and all(u in st for st in sets):
                common = u; break                                                    # noqa: E702
    s.gate("R2 %s innermost common Node structure of %s" % (c.key, loc), common is not None, common)
    cs = {}
    for u in have:
        for x in cases_on(c, ch[u]):
            cs[x["case"]] = x
    s.fact("%s Cases on reader chains: %s" % (c.key, list(cs.values())))
    s.R.setdefault("cases", {})[c.key] = list(cs.values())
    s.gate("V %s no Case on a reader chain (no Visible Frame writer op exists - frames NOT set)" % c.key, not cs,
           ["case #%s needs frame %s %r" % (k, v["frame_index"], v["names"][v["frame_index"]] if v["frame_index"] is not None and v["frame_index"] < len(v["names"]) else None) for k, v in cs.items()])
    note = ("no Case on the chain" if not cs else
            "NOT SET (no Visible Frame writer): " + "; ".join("case #%s holds the chain in frame %s" % (k, v["frame_index"]) for k, v in cs.items()))
    if common:
        record(c, os.path.join(L.OUTDIR, "raw_R_%s_%s.png" % (c.key, common)), common,
               "%s innermost Node structure containing Locals %s (+ seqlock reads)" % (c.key, loc), note)
    l12 = 10170 if any(u == 10170 for _cl, u in ch.get(30239, [])) else next((u for cl, u in ch.get(30239, []) if cl == "WhileLoop"), None)
    s.fact("%s loop 1.2 = While #%s" % (c.key, l12))
    if l12:
        record(c, os.path.join(L.OUTDIR, "raw_L12_%s.png" % c.key), l12, "%s loop 1.2 While #%s whole" % (c.key, l12), note)
    for k in cs:
        record(c, os.path.join(L.OUTDIR, "raw_C_%s_%s.png" % (c.key, k)), k,
               "%s Case #%s on a reader chain (frames %r)" % (c.key, k, cs[k]["names"]), note)
    for u in have:
        record(c, os.path.join(L.OUTDIR, "raw_N_%s_%s.png" % (c.key, u)), u, "%s reader node #%s alone" % (c.key, u), "n/a")


def part_w(c):
    s.head("[W] P6L every While loop")
    wl = [int(o["uid"]) for o in g.report_all(c.path, "WhileLoop")]
    s.gate("W1 P6L has WhileLoops", bool(wl), wl)
    dias = g.report_all(c.path, "Diagram")
    inside = dict((w, []) for w in wl)
    for i, d in enumerate(dias):
        rows, err = g.subvis(c.path, i, strict=False)
        if not rows:
            continue
        ups = set(u for cl, u in [("Diagram", int(d["uid"]))] + c.chain(int(d["uid"])) if cl == "WhileLoop")
        for r in rows:
            for w in ups:
                if w in inside:
                    inside[w].append((int(r["uid"]), r["name"]))
    for w in wl:
        nm = sorted(set(n for _u, n in inside[w]))
        s.fact("P6L While #%s chain %s; subVI calls %d, names %s" % (w, c.chain(w), len(inside[w]), nm))
        record(c, os.path.join(L.OUTDIR, "raw_W_P6L_%s.png" % w), w, "P6L While #%s whole" % w, "not applicable",
               {"subvi_calls": inside[w], "owner_chain": c.chain(w)})
    s.R["W"] = dict((str(w), inside[w]) for w in wl)


def part_d(c, frames):
    s.head("[D] P6L writer Flat Sequence #27509")
    s.fact("P6L #27509 in the FlatSequence census: %s; frames %s" % (27509 in c.fs, frames.get(27509)))
    miss = [u for u in WRITER_LOCALS if u not in c.order]
    s.gate("D1 P6L writer Locals present", not miss, miss)
    ch = dict((u, c.chain(u)) for u in WRITER_LOCALS if u in c.order)
    for u, x in ch.items():
        s.fact("P6L writer chain #%s: %s" % (u, x))
    fsch = c.chain(27509) if 27509 in c.fs else []
    s.fact("P6L FS #27509 chain: %s" % fsch)
    s.R["D"] = {"fs_in_census": 27509 in c.fs, "frames": frames.get(27509), "chains": dict((str(k), v) for k, v in ch.items()),
                "fs_chain": fsch}
    first = None
    for u, x in ch.items():
        f = next((v for cl, v in x if cl in NODE_STRUCT), None)
        first = first or f
        if f != first:
            s.fact("P6L writer Local #%s's first Node structure #%s differs from #%s" % (u, f, first))
    s.gate("D2 P6L first Node structure above the writer Locals", first is not None, first)
    if first:
        cs = {}
        for u in ch:
            for x in cases_on(c, ch[u]):
                cs[x["case"]] = x
        note = "no Case between" if not [1 for x in cs.values()] else "NOT SET: %s" % list(cs.values())
        record(c, os.path.join(L.OUTDIR, "raw_D_P6L_%s.png" % first), first,
               "P6L loop 1.1 writer: Node structure #%s that owns Flat Sequence #27509 (frames %s)" % (first, frames.get(27509)), note)


def main():
    os.makedirs(SHOTDIR, exist_ok=True); os.makedirs(L.OUTDIR, exist_ok=True)       # noqa: E702
    before = dict((k, L.md5(p)) for k, (p, _m) in SRC.items())
    s.gate("S0 sources md5 == pins", all(before[k] == SRC[k][1] for k in SRC), before, fatal=True)
    s.head("[0] restart LabVIEW"); h0 = L.restart(); s.fact("handles after restart %s" % h0)  # noqa: E702
    s.R["handles_start"] = h0
    for key in ("P61", "P6L"):
        c = Copy(key)
        frames = c.census_fs()
        s.fact("%s #29721 in FS census: %s frames %s" % (key, 29721 in c.fs, frames.get(29721)))
        part_r(c)
        if key == "P6L":
            part_w(c)
            part_d(c, frames)
        json.dump(SHOTS, open(os.path.join(L.OUTDIR, "shots_raw.json"), "w", encoding="utf-8"), indent=1, default=list)
    s.arts.append(os.path.join(L.OUTDIR, "shots_raw.json"))
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
if SHOTS:
    json.dump(SHOTS, open(os.path.join(L.OUTDIR, "shots_raw.json"), "w", encoding="utf-8"), indent=1, default=list)
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
after = dict((k, L.md5(p)) for k, (p, _m) in SRC.items())
s.gate("X sources md5 after == pins", all(after[k] == SRC[k][1] for k in SRC), after)
sys.exit(s.finish(os.path.join(L.OUTDIR, "pi_shots_20261019.json")))
