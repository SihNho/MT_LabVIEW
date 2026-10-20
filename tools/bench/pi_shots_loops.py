# ---
# labview: build
# hardware: none
# evidence: tools/bench/cards/brief_chat-PI3.md
# ---
r"""pi_shots_loops.py - card chat-PI2b (brief chat-PI3): whole While-loop PNGs of the CURRENT VI (P6L 54f7cd2f) for the
original-vs-now slide. A byte copy of P6L is the ONLY VI under study loaded, in a FRESH LabVIEW (lesson chat-PI1f: P6L
Get Image gave 'error 1: Write PNG File.vi' / blank PNGs in a session that had P6-1 loaded first).

EXISTING FIRST: image = pi_shots_lib.get_image (claudeDev\OpGetImage_v0.vi b7c5667b, Node.Get Image 6358C01); blank
check = pi_shots_lib.png_stats; Rec / md5 / restart / kill_and_verify = pi_shots_lib; owner hop = build_d1_v0.owner_of
(as pi_shots_20261019.py:86-90). The Copy/shot pattern of pi_shots_20261019.py:53-127 is not importable (its main()
runs at import); this script only CALLS the shared functions (copy + md5 gate + ensure_loaded + report_all + get_image),
no logic block is copied. pi_shots_lib is not edited (its bytes are pinned by the prior-art NOVEL record).

WHAT: raw_W_P6L_<uid>.png for While #637 (camera 1.1 + ring writer), #10170 (tracking 1.2), #23041 (saving 1.7),
#23032 (ASI focus), #25380 (motor), #1175 (display 1.6, 3594 x 32756). Retry per brief: an error or blank image ->
once with Image Depth 8 -> once in another fresh LabVIEW (P6L copy reloaded) -> report. #1175 still failing after that:
image the largest Node structure DIRECTLY inside it (owner = a Diagram owned by #1175) instead, and say so.
PREDICTION (gates): S0 source md5 == pin; S1 copy md5 == pin; per loop E op errors '' and echo == uid, I image size ==
Bounds within 4 px, B not blank (PIL getextrema); X source md5 after == pin; G LabVIEW gone; K copy deleted.
Output: tools/bench/pi_shots_20261016/raw_W_P6L_<uid>.png + loops_p6l.json (uid, role, Bounds, file, blank, depth, try).
CARD chat-PI3 (review 2026-10-19-pi-shots-ops-handles "What was done with it"): LabVIEW HandleCount logged after
restart, after load() and before/after EVERY Get Image call (rows h_before / h_after, also beside any Write PNG error).
While #637 is shot THREE times in a row first. Pre-registered leak rule: d2 = h(after 637 shot 2) - h(after shot 1),
d3 = h(after shot 3) - h(after shot 2); LEAK = d2 > 50 AND d3 > 50 (steady rise per shot) -> gate L FAILS, no further
shot (#1175 never attempted), clean exit. Otherwise (flat, |d| <= 50, or mixed) the first-shot rise is load cost; go on.
Order after that: #10170, #23041, #23032, #25380, #1175 last. The +1000 end threshold of pi_shots_ops.py is NOT used.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/pi_shots_loops.log -- py -u tools/bench/pi_shots_loops.py
"""
import json, os, shutil, sys                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))                 # noqa: E702
import pi_shots_lib as L                                                             # noqa: E402
import gscript as g                                                                  # noqa: E402
CD = g.CLAUDEDEV
SHOTDIR = os.path.join(CD, "shots_20261016")
SRC = os.path.join(CD, "bench", "lean", "D1_ring_fxdP6L_20261016_115105.vi")
PIN = "54f7cd2f27175b3aa993a2e7630cff40"
COPY = os.path.join(SHOTDIR, "P6L_" + os.path.basename(SRC))
LOOPS = [(637, "camera loop 1.1 + ring writer"), (10170, "tracking loop 1.2"), (23041, "saving loop 1.7"),
         (23032, "ASI focus loop"), (25380, "motor loop"), (1175, "display loop 1.6")]
STRUCT = ("WhileLoop", "ForLoop", "CaseStructure", "EventStructure", "Sequence", "StackedSequence", "FlatSequence",
          "TimedLoop")
s = L.Rec("pi_shots_loops")
ROWS = {}
ST = {}
HL = []                                                                              # (label, LabVIEW HandleCount)
LEAK_D = 50                                                                          # handles per shot, see docstring


def load():
    shutil.copyfile(SRC, COPY)
    s.gate("S1 P6L copy md5 == pin", L.md5(COPY) == PIN, L.md5(COPY), fatal=True)
    g.ensure_loaded(COPY)
    rows = g.report_all(COPY, "Node")
    ST["order"] = [int(o["uid"]) for o in rows]
    ST["cls"] = dict((int(o["uid"]), str(o["class"])) for o in rows)
    s.fact("P6L copy loaded: %d Nodes" % len(ST["order"]))
    h = L.handles(); HL.append(("after load", h)); s.fact("HANDLES after load %s" % h)  # noqa: E702


def shot(uid, png, depth):
    """One OpGetImage_v0 call; returns (ok, row)."""
    if uid not in ST["order"]:
        return False, {"uid": uid, "err": "absent from Traverse('Node')"}
    if os.path.exists(png):
        os.remove(png)
    hb = L.handles()
    r = L.get_image(COPY, uid, png, depth=depth, cls="Node", index=ST["order"].index(uid))
    ha = L.handles(); HL.append(("shot #%s depth %s" % (uid, depth), ha))            # noqa: E702
    row = {"uid": uid, "class": ST["cls"].get(uid), "depth": depth, "echo": r["echo"], "position": r["position"],
           "bounds": r["bounds"], "err": "|".join(x for x in (r["err_png"], r["err_pn"], r["err_echo"]) if x),
           "h_before": hb, "h_after": ha}
    s.fact("HANDLES shot #%s depth %s: %s -> %s (%+d)%s" % (uid, depth, hb, ha, ha - hb,
                                                          ("  WITH ERROR: " + row["err"][:300]) if row["err"] else ""))
    if row["err"] or r["echo"] != uid or not os.path.exists(png):
        return False, row
    st = L.png_stats(png)
    b = [int(v) for v in r["bounds"]]
    w, h = (b[2] - b[0], b[3] - b[1]) if len(b) == 4 else (b[0], b[1])
    row.update({"file": os.path.basename(png), "size": st["size"], "mode": st["mode"], "blank": st["blank"],
                "bounds_wh": [w, h], "size_ok": abs(st["size"][0] - w) <= 4 and abs(st["size"][1] - h) <= 4})
    return (not st["blank"] and row["size_ok"]), row


def take(uid, role, attempt):
    png = os.path.join(L.OUTDIR, "raw_W_P6L_%s.png" % uid)
    for depth in (24, 8):
        ok, row = shot(uid, png, depth)
        row.update({"role": role, "try": attempt})
        s.fact("P6L #%s (%s) try %s depth %s -> ok %s %s" % (uid, role, attempt, depth, ok,
                                                           dict((k, row.get(k)) for k in ("err", "echo", "bounds", "size", "mode", "blank"))))
        ROWS[uid] = row
        if ok:
            return True
    return False


def inner_largest(top):
    """Node structures whose owner is a Diagram owned by #top; imaged, the largest non-blank kept."""
    g._c97_paths()
    import build_d1_v0 as B
    kids = []
    for u in ST["order"]:
        if ST["cls"].get(u) not in STRUCT:
            continue
        _c1, d = B.owner_of(COPY, u, strict=False)
        if not d:
            continue
        _c2, o = B.owner_of(COPY, int(d), strict=False)
        if int(o or 0) == top:
            kids.append(u)
    s.fact("structures directly inside #%s: %s" % (top, [(u, ST["cls"].get(u)) for u in kids]))
    best = None
    for u in kids:
        png = os.path.join(L.OUTDIR, "raw_W_P6L_%s_inner_%s.png" % (top, u))
        ok, row = shot(u, png, 24)
        s.fact("inner #%s -> ok %s %s" % (u, ok, dict((k, row.get(k)) for k in ("err", "bounds", "size", "blank"))))
        if ok and (best is None or row["size"][0] * row["size"][1] > best[1]["size"][0] * best[1]["size"][1]):
            if best:
                os.remove(os.path.join(L.OUTDIR, best[1]["file"]))
            best = (u, row)
        elif os.path.exists(png):
            os.remove(png)
    return best


def main():
    os.makedirs(SHOTDIR, exist_ok=True); os.makedirs(L.OUTDIR, exist_ok=True)       # noqa: E702
    s.gate("S0 P6L source md5 == pin", L.md5(SRC) == PIN, L.md5(SRC), fatal=True)
    s.head("[0] fresh LabVIEW, only the P6L copy"); h0 = L.restart(); s.fact("handles after restart %s" % h0)  # noqa: E702
    HL.append(("after restart", h0))
    load()
    s.head("[1a] While #637 three times in a row (leak check)")
    ok637, h637 = [], []
    for k in (1, 2, 3):
        ok637.append(take(LOOPS[0][0], LOOPS[0][1], 1))
        h637.append(L.handles())
        s.fact("HANDLES after #637 shot %d: %s" % (k, h637[-1]))
    d2, d3 = h637[1] - h637[0], h637[2] - h637[1]
    ST["h637"] = {"after_load": HL[1][1] if len(HL) > 1 else None, "after_shots": h637, "d2": d2, "d3": d3,
                  "ok": ok637}
    leak = d2 > LEAK_D and d3 > LEAK_D
    s.gate("L #637 x3: no steady handle rise per shot (d2 %+d, d3 %+d, leak if both > %d)" % (d2, d3, LEAK_D),
           not leak, ST["h637"], fatal=True)
    s.head("[1] While loops, try 1")
    bad = ([] if ok637[-1] else [LOOPS[0]]) + [(u, r) for u, r in LOOPS[1:] if not take(u, r, 1)]
    if bad:
        s.head("[2] another fresh LabVIEW for %s" % [u for u, _r in bad])
        s.fact("handles after restart %s" % L.restart())
        load()
        bad = [(u, r) for u, r in bad if not take(u, r, 2)]
    if any(u == 1175 for u, _r in bad):
        s.head("[3] #1175 still failing: the largest structure directly inside it")
        best = inner_largest(1175)
        if best:
            row = dict(best[1]); row.update({"role": "display loop 1.6 - LARGEST INNER structure #%s instead of the whole "
                                             "loop (whole loop failed)" % best[0], "inner_of": 1175})
            ROWS["1175_inner"] = row
            bad = [(u, r) for u, r in bad if u != 1175]
            s.arts.append(os.path.join(L.OUTDIR, row["file"]))
    for u, r in LOOPS:
        row = ROWS.get(u, {})
        okw = row.get("err") == "" and not row.get("blank", True) and row.get("size_ok")
        if u == 1175 and "1175_inner" in ROWS and not okw:
            s.gate("W #1175 replaced by inner #%s (not blank, size == Bounds)" % ROWS["1175_inner"]["uid"], True)
            continue
        s.gate("W P6L #%s (%s): no error, not blank, size == Bounds" % (u, r), bool(okw),
               dict((k, row.get(k)) for k in ("err", "size", "bounds_wh", "blank", "depth", "try")))
        if okw:
            s.arts.append(os.path.join(L.OUTDIR, row["file"]))
    json.dump(ROWS, open(os.path.join(L.OUTDIR, "loops_p6l.json"), "w", encoding="utf-8"), indent=1, default=list)
    s.arts.append(os.path.join(L.OUTDIR, "loops_p6l.json"))
    try:
        s.fact("H handles at end %s (after first restart %s); refs %s" % (L.handles(), h0, g.ref_counts()))
    except Exception:                                                                # noqa: BLE001
        pass


try:
    main()
except L.StopRun as e:
    s.fact("STOPPED at gate: %s" % e)
except Exception as e:                                                               # noqa: BLE001
    import traceback; traceback.print_exc(); s.gate("the run completed without an unhandled exception", False, str(e)[:200])  # noqa: E702
ROWS["_handles"] = {"series": HL, "h637": ST.get("h637"), "leak_d": LEAK_D}
s.fact("HANDLE SERIES %s" % HL)
if ROWS:
    json.dump(ROWS, open(os.path.join(L.OUTDIR, "loops_p6l.json"), "w", encoding="utf-8"), indent=1, default=list)
s.gate("G LabVIEW gone at exit (killed, nothing saved)", L.kill_and_verify())
left = []
if os.path.exists(COPY):
    try:
        os.remove(COPY)
    except Exception:                                                                # noqa: BLE001
        left.append(COPY)
try:
    if os.path.isdir(SHOTDIR) and not os.listdir(SHOTDIR):
        os.rmdir(SHOTDIR)
except Exception:                                                                    # noqa: BLE001
    pass
s.gate("K P6L copy deleted", not left, left)
s.gate("X P6L source md5 after == pin", L.md5(SRC) == PIN, L.md5(SRC))
sys.exit(s.finish(os.path.join(L.OUTDIR, "pi_shots_loops.json")))
