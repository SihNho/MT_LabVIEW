r"""allterms_s2 - STEP 1 / sub-step S2: the ONE GUI act - two `To More Specific Class` nodes dropped
INSIDE the For-loop body by Quick Drop, keyboard only.

WHY GUI AT ALL (judgement decision, chat 2026-09-23 07:xx, `VerifiedImpossible TMSC-in-loop`; every
grounds machine-checked, none inferred):
  * TMSC has no scripted creator (skill rule-0 #1, and the fleet has no op for it).
  * `loop_in`/`for_loop` create an EMPTY loop (`tools/gscript.py:1195,1250`) - nothing can be enclosed.
  * `copy_by_index` has NO destination-diagram parameter (`tools/gscript.py:1519`).
  * NO donor exists: all 26 op VIs owning a Function node and a loop, 54 body diagrams, 0 TMSC in a body
    (`tools/bench/diag_allterms_donor2.log:150-153`).
  * the subVI-root cast route ended ExecState 0 (`tools/bench/diag_allterms_retarget2.log:114`), and the
    same wall stopped class `Local` on 2026-09-21 (`docs/cycle27-plan.md:2220-2222`).
`move_in` into the body is the F-side route Pre-decided 139 forbids, so the node must be BORN there.

HOW THE TARGET IS LOCATED - BY THE MACHINE, NOT BY A REMEMBERED COORDINATE (pinned rule, 2026-09-18):
  a drop is placed at the mouse, so screen -> diagram is CALIBRATED by dropping ONE probe TMSC at a
  chosen canvas point and READING ITS POSITION BACK (`report('Function')`). That gives the constant
  offset D. Every later point is computed from D and the loop's own measured box, a full-screen capture
  is taken BEFORE and AFTER every drop, and each drop is CONFIRMED THREE WAYS: the `Quick Drop` window
  appears and then disappears (`-Action windows`), `Function` count +1, and the new uid is ON THE BODY
  DIAGRAM (`node_labels(work, 1)`, one op run). A drop that lands on the root diagram is DELETED.

THE ARTEFACT IS BROKEN BY DESIGN: a TMSC with unwired `reference`/`target class` is a broken VI, and the
wiring is S3. So it is saved through `gui_save` under the 2026-09-22 broken-intermediate permission and is
NEVER RUN (34(f)).

PREDICTION CONTRACT
  B1 the loop moves to (120, 560) and ExecState stays 1
  B2 the calibration probe drops, is readable, and yields an offset D
  B3 exactly TWO TMSC nodes end up owned by the BODY diagram (uid 272)
  B4 every probe that landed on the root diagram is deleted; Function returns to base+2
  B5 ExecState 0 (BY DESIGN) and the gui_save moves the file's mtime and md5

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/allterms_s2.log -- py -u tools/bench/allterms_s2.py
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpAllTerms_v0_s1.vi")
SRC_MD5 = "ca44b62fbe428282719e4733e2cea785"
OUT = "OpAllTerms_v0_s2.vi"
BODY_DIAGRAM_INDEX = 1
BODY_DIAGRAM_UID = 272
LOOP_AT = (200, 180)          # where the loop's TOP-LEFT is put ON SCREEN (canvas starts at y~85)
SHOTS = os.path.join(K.BENCH, "allterms_shots")
EV = ("chat 2026-09-23 TMSC-in-loop: diag_allterms_cast/retarget2/donor2, cycle27-plan:2220")
QD = "To More Specific Class"
# Offsets from the loop's top-left, in DIAGRAM units. The loop's measured box on the donor is
# (1400,900)-(~2930,~2110), i.e. ~1530 x ~1210, with its only contents in the far bottom-right corner
# (property nodes at x>=2845, y>=1851), so the whole upper-left interior is empty.
CANDIDATES = [(160, 140), (160, 260), (420, 140), (420, 260), (700, 140), (700, 260)]
BD = {"title": ""}                                  # set in main() once the window exists


def shot(s, tag):
    p = os.path.join(SHOTS, "{0}_{1}.png".format(time.strftime("%H%M%S"), tag))
    g._lv_gui("-Action", "shot", "-Out", p)
    s.R.setdefault("shots", []).append({"tag": tag, "path": p, "exists": os.path.exists(p)})
    return p


def windows():
    return g._lv_gui("-Action", "windows")


def unwedge(s, tag=""):
    """A REAL mouse click on the block-diagram window's TITLE BAR.

    RUN 1 MEASURED WHY THIS IS MANDATORY, not decorative: after Ctrl+Space / type / Enter with no real
    click anywhere, the Quick Drop window closed and the node WAS placed (capture
    `tools/bench/allterms_shots/061628_calib_after.png`), but the very next COM call - `report_all` -
    never returned in 180 s and poisoned the module (`tools/bench/allterms_s2.log:31-46`). That is the
    skill's H5 law: after programmatic activation and keystrokes LabVIEW's UI loop blocks COM until a
    real mouse click lands; `gui_save` already clicks the title bar for exactly this reason
    (`tools/gscript.py:2063`). `-Action move` is a hover, not a click, so run 1 never delivered one."""
    g._lv_gui("-Action", "click", "-X", "400", "-Y", "10",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    time.sleep(0.6)
    s.R.setdefault("unwedge_clicks", []).append(tag)


def front(s, title):
    """Front a window WITHOUT Esc (`activate`, added 2026-09-23) and BELIEVE ONLY ITS MEASURED
    foreground - `"ok":true` means GetForegroundWindow() == that window after the call."""
    out = g._lv_gui("-Action", "activate", "-Title", '"{0}"'.format(title),
                    "-Exception", "VerifiedImpossible", "-Evidence", EV)
    s.fact("activate({0!r}) -> {1}".format(title, out.strip()[:260]))
    return '"ok":true' in out.replace(" ", "")


def quick_drop(s, xy, tag):
    """ONE Quick Drop at screen `xy`. capture -> locate (the mouse is MOVED there and the move is
    captured) -> act -> capture -> confirm. Returns the new Function uid, or None."""
    before = set(g.uids(s.work, "Function"))
    # Every COM call can change which window is in front, so the foreground is re-established and
    # RE-MEASURED immediately before the keystroke - never assumed to have survived.
    s.gate("QD[{0}] the Block Diagram is the measured foreground at the keystroke".format(tag),
           front(s, BD["title"]), BD["title"])
    unwedge(s, tag + "_pre")
    g._lv_gui("-Action", "move", "-X", str(xy[0]), "-Y", str(xy[1]))
    shot(s, tag + "_before")
    g._lv_gui("-Action", "keys", "-Key", "^ ", "-WaitMs", "1200",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    opened = False
    for _ in range(12):
        if "Quick Drop" in windows():
            opened = True
            break
        time.sleep(1.5)
    s.gate("QD[{0}] the Quick Drop window OPENED after Ctrl+Space".format(tag), opened,
           "windows: {0}".format(" / ".join(windows().split("\n"))[:160]))
    if not opened:
        return None
    g._lv_gui("-Action", "keys", "-Key", QD, "-WaitMs", "1200",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    g._lv_gui("-Action", "key", "-Key", "enter", "-WaitMs", "1500",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    time.sleep(1.5)
    closed = "Quick Drop" not in windows()
    shot(s, tag + "_after")
    unwedge(s, tag + "_post")             # MANDATORY before the next COM call - see unwedge()'s note
    new = [u for u in g.uids(s.work, "Function") if u not in before]
    s.gate("QD[{0}] the Quick Drop window CLOSED and exactly ONE Function appeared".format(tag),
           closed and len(new) == 1, "closed={0!r} new={1!r}".format(closed, new))
    return new[0] if len(new) == 1 else None


def on_body(s, uid):
    rows, _e = s.safe("node_labels(body)", lambda: g.node_labels(s.work, BODY_DIAGRAM_INDEX), [])
    return uid in [r["uid"] for r in (rows or [])]


def pos_of(s, uid):
    rows, _e = s.safe("report(Function)", lambda: g.report(s.work, "Function"), [])
    return next((tuple(o["pos"]) for o in (rows or []) if o["uid"] == uid), None)


def drop_function(s, uid):
    rows, _e = s.safe("report(Function)", lambda: g.report(s.work, "Function"), [])
    idx = next((i for i, o in enumerate(rows or []) if o["uid"] == uid), None)
    if idx is None:
        return False
    s.safe("delete_object(Function,{0})".format(idx), lambda: g.delete_object(s.work, "Function", idx))
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(s.work))
    return uid not in set(g.uids(s.work, "Function"))


def main(s):
    if not os.path.isdir(SHOTS):
        os.makedirs(SHOTS)
    s.start()
    p = s.work
    base_fn = s.count("Function")
    s.fact("Function count at entry: {0}".format(base_fn))

    s.head("[B1b] the block-diagram window, fronted without Esc and sized to a fixed rect")
    g.open_panel(p, activate=True)
    time.sleep(1.5)
    name = os.path.basename(p)
    bd = "{0} Block Diagram".format(name)
    BD["title"] = bd
    if bd not in windows():
        front(s, "{0} Front Panel".format(name))
        time.sleep(0.8)
        g._lv_gui("-Action", "keys", "-Key", "^e", "-WaitMs", "1500",
                  "-Exception", "VerifiedImpossible", "-Evidence", EV)
        time.sleep(1.2)
    g._lv_gui("-Action", "movewin", "-Title", '"{0}"'.format(bd),
              "-X", "0", "-Y", "0", "-Width", "1900", "-Height", "1030")
    time.sleep(0.8)
    ok_front = front(s, bd)
    if not ok_front:
        # FALLBACK, the gui_save route: a REAL title-bar click. `clickprobe` also taps Esc, which a
        # block diagram ignores (it is only fatal to the Error List dialog, STATUS purpose_errorlist).
        m = g._lv_gui("-Action", "rect", "-Title", '"{0}"'.format(bd))
        s.fact("rect({0!r}) -> {1}".format(bd, m.strip()[:160]))
        g._lv_gui("-Action", "clickprobe", "-Title", '"{0}"'.format(bd), "-X", "400", "-Y", "10",
                  "-Exception", "VerifiedImpossible", "-Evidence", EV)
        time.sleep(0.6)
        ok_front = front(s, bd)
    s.fact("windows now: {0}".format(" / ".join(windows().split("\n"))[:240]))
    s.gate("B1b the Block Diagram window exists and is the measured foreground", ok_front,
           "title {0!r}".format(bd), fatal=True)
    unwedge(s, "bd_opened")
    shot(s, "bd_opened")

    s.head("[B2] CALIBRATION - one probe drop whose position is READ BACK")
    probe_xy = (900, 600)
    u = quick_drop(s, probe_xy, "calib")
    s.gate("B2a the calibration probe exists", u is not None, "uid {0!r}".format(u), fatal=True)
    ppos = pos_of(s, u)
    s.gate("B2b its diagram position is readable", ppos is not None, "pos {0!r}".format(ppos),
           fatal=True)
    D = (ppos[0] - probe_xy[0], ppos[1] - probe_xy[1])
    s.R["calibration"] = {"probe_screen": probe_xy, "probe_diagram": ppos, "D": D,
                          "probe_uid": u, "probe_on_body": on_body(s, u)}
    s.fact("CALIBRATION: screen {0!r} -> diagram {1!r}; D = diagram - screen = {2!r}".format(
        probe_xy, ppos, D))

    kept = []
    if s.R["calibration"]["probe_on_body"]:
        kept.append(u)
        s.fact("the calibration probe itself landed on the BODY diagram - kept as TMSC #1")
    else:
        s.gate("B2c the stray calibration probe is deleted", drop_function(s, u), "uid {0}".format(u))

    s.head("[B1] BRING THE LOOP TO THE MOUSE, instead of hunting for the loop")
    # RUN 1's REAL DEFECT, now measured: the window was scrolled to diagram origin ~(1520,1310)
    # (the capture shows the loop's CONTENTS, not its top-left corner), so every candidate computed
    # from a FIXED loop position mapped to a negative screen coordinate. With D measured, the loop is
    # simply MOVED so its top-left lands on a chosen visible screen point - one scripted call, no
    # scrolling, no vision.
    want = (LOOP_AT[0] + D[0], LOOP_AT[1] + D[1])
    newpos, _e = s.safe("move_object(ForLoop,0)", lambda: g.move_object(p, "ForLoop", 0, want))
    es = s.es("after the loop move")
    # ExecState is RECORDED, not gated: if the calibration probe was kept, a TMSC with an unwired
    # `reference` is already on the diagram and 0 is the CORRECT reading (broken by design).
    s.gate("B1 the loop's top-left is at diagram {0!r} = screen {1!r}".format(want, LOOP_AT),
           tuple(newpos or ()) == want, "pos {0!r} ExecState {1!r} (recorded, not gated)".format(
               newpos, es), fatal=True)
    shot(s, "loop_moved")

    s.head("[B3] the real drops - candidates are the loop's on-screen top-left plus an offset")
    for k, (dx, dy) in enumerate(CANDIDATES):
        if len(kept) >= 2:
            break
        if s.left_s() < 180:
            s.fact("deadline reserve reached - no further candidate tried")
            break
        xy = (LOOP_AT[0] + dx, LOOP_AT[1] + dy)
        if not (10 < xy[0] < 1890 and 120 < xy[1] < 1010):
            s.fact("candidate {0!r} maps off-canvas to {1!r} - skipped".format((dx, dy), xy))
            continue
        s.fact("candidate {0}: loop_screen+{1!r} -> screen {2!r}".format(k, (dx, dy), xy))
        u2 = quick_drop(s, xy, "cand{0}".format(k))
        if u2 is None:
            continue
        if on_body(s, u2):
            kept.append(u2)
            s.fact("candidate {0} uid {1} is ON THE BODY DIAGRAM (uid {2})".format(k, u2,
                                                                                   BODY_DIAGRAM_UID))
        else:
            s.fact("candidate {0} uid {1} landed on the ROOT diagram at {2!r} - deleting".format(
                k, u2, pos_of(s, u2)))
            s.gate("B4 stray root drop {0} deleted".format(u2), drop_function(s, u2), "")

    s.R["tmsc_uids"] = kept
    s.fact("TMSC uids on the body diagram: {0!r}".format(kept))
    s.gate("B3 exactly TWO To More Specific Class nodes are on the BODY diagram", len(kept) == 2,
           "kept {0!r}".format(kept))
    end_fn = s.count("Function")
    s.gate("B4 Function count is base+{0} ({1} -> {2}) - no stray drop left behind".format(
        len(kept), base_fn, end_fn), end_fn == base_fn + len(kept),
        "base {0} end {1}".format(base_fn, end_fn))
    shot(s, "final")

    s.head("[B5] SAVE the broken-by-design intermediate")
    s.save(broken_ok=True, cold_check=False)


S = K.Stage(SRC, SRC_MD5, "allterms_s2", fresh=True, preload=False, work_name=OUT,
            deadline_min=22.0, reserve_s=150.0,
            out_json=os.path.join(K.BENCH, "allterms_s2.json"),
            task="S2 of OpAllTerms_v0: two To More Specific Class nodes placed INSIDE the For-loop body "
                 "by GUI Quick Drop (keyboard only), located by a calibrated screen->diagram mapping "
                 "measured in this run, confirmed by node_labels on the body diagram.")
sys.exit(K.run(main, S))
