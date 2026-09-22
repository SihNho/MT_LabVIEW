r"""allterms_s2 - STEP 1 / sub-step S2: the ONE GUI act - two `To More Specific Class` nodes dropped
INSIDE the For-loop body by Quick Drop, keyboard only. RUN 3: also the DISCRIMINATING TEST.

WHY GUI AT ALL (judgement decision, chat 2026-09-23 07:xx, `VerifiedImpossible TMSC-in-loop`; every
grounds machine-checked, none inferred): TMSC has no scripted creator (skill rule-0 #1); `loop_in` /
`for_loop` create an EMPTY loop (`tools/gscript.py:1195,1250`); `copy_by_index` has NO destination-diagram
parameter (`:1519`); NO donor exists - 26 op VIs, 54 body diagrams, 0 TMSC in a body
(`tools/bench/diag_allterms_donor2.log:150-153`); the subVI-root cast route ended ExecState 0
(`diag_allterms_retarget2.log:114`) as class `Local` did on 2026-09-21 (`docs/cycle27-plan.md:2220-2222`).
`move_in` is the F-side route Pre-decided 139 forbids, so the node must be BORN in the body.

WHAT RUNS 1 AND 2 SETTLED, so run 3 does not re-litigate it:
  * Quick Drop WORKS, keyboard only: Ctrl+Space opens a window titled `Quick Drop` (visible to
    `-Action windows`), typing the name + Enter closes it and DROPS THE NODE AT THE MOUSE - the same
    130x90 screen region is blank before and carries the TMSC icon after (`allterms_shots/z_*_crop.png`).
  * A REAL mouse click must land before the next COM call, or that call hangs 180 s and poisons the
    module (run 1, rc=1 after 208 s; the skill's H5 law). A title-bar click removes it entirely.
  * The node was STILL absent from `uids(work,'Function')`. NOT a class error: a TMSC's Traverse class IS
    `Function` (`tools/bench/allterms_tmscclass.log`, 4/0, uid 683 of `OpLoopCast_v0.vi` seen by `report`,
    `report_all('Function')` and `report_all('Node')`).

RUN 3 IS THE DISCRIMINATOR between the two hypotheses, and it is ONE drop long:
  (a) UNCOMMITTED-WHILE-SELECTED -> a click on EMPTY canvas commits it; the census then sees it.
  (b) STALE VI REFERENCE         -> only save + close + re-open refreshes what VI Server traverses.
The empty canvas point is LOCATED IN THE CAPTURE, mechanically: a 41x41 box whose pixels are all one
colour (`uniform_box`), never a remembered coordinate. The deselect is CONFIRMED by the drop region
CHANGING between the two captures (the selection halo disappearing).

THE ARTEFACT IS BROKEN BY DESIGN (a TMSC with unwired `reference`/`target class`), so it is saved through
`gui_save` under the 2026-09-22 broken-intermediate permission and is NEVER RUN (34(f)).

PREDICTION CONTRACT
  B1  the loop moves to diagram (200,200) FIRST, so every later drop point is on-canvas, ExecState 1
  B2  the Block Diagram window is the MEASURED foreground at every keystroke
  B3  drop 1 opens and closes `Quick Drop`
  B4  THE DECIDER: after the deselect click the census gains exactly one `Function` -> (a);
      else after save+close+re-open it gains one -> (b); else neither and the route STOPS
  B5  with the mapping D measured, two more drops land ON THE BODY DIAGRAM (`node_labels(work,1)`)
  B6  exactly TWO TMSC on the body, no stray left on the root, and the save changes md5 away from S1

  py tools/bgrun.py --material --max-min 40 --log tools/bench/allterms_s2.log -- py -u tools/bench/allterms_s2.py
"""
import os
import sys
import time

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpAllTerms_v0_s1.vi")
SRC_MD5 = "ca44b62fbe428282719e4733e2cea785"
OUT = "OpAllTerms_v0_s2.vi"
BODY_DIAGRAM_INDEX = 1
LOOP_AT = (200, 200)                      # DIAGRAM coords: parked there before the window is opened
LOOP_SCREEN = (200, 200)                  # SCREEN point the loop's top-left is moved to once D is known
SHOTS = os.path.join(K.BENCH, "allterms_shots")
EV = "chat 2026-09-23 TMSC-in-loop: diag_allterms_cast/retarget2/donor2, cycle27-plan:2220"
EV_SAVE = "user 2026-09-22 broken-intermediate save"
QD = "To More Specific Class"
BD = {"title": ""}
# Candidates for the discriminator's hover point A and its PLACING-CLICK point B, tried in order; the
# first whose 41x41 box is one single colour in the live capture wins. All well below the toolbar row
# (y < 85) and far from the Run arrow, so no click can ever start the VI.
HOVER_TRY = [(600, 620), (640, 660), (560, 700), (700, 760), (520, 560)]
CLICK_TRY = [(1300, 620), (1360, 680), (1240, 560), (1420, 740), (1160, 800)]
DROP_OFFSETS = [(160, 140), (420, 140), (160, 300), (420, 300)]     # screen, from the loop's top-left


# ----------------------------------------------------------------- capture helpers (PIL/numpy)
def shot(s, tag):
    p = os.path.join(SHOTS, "{0}_{1}.png".format(time.strftime("%H%M%S"), tag))
    g._lv_gui("-Action", "shot", "-Out", p)
    s.R.setdefault("shots", []).append({"tag": tag, "path": p, "exists": os.path.exists(p)})
    return p


def arr(png):
    return np.asarray(Image.open(png).convert("RGB"))


def uniform_box(img, x, y, half=20):
    """(is the box one single colour, how many colours it holds) - the mechanical 'empty canvas' test."""
    y0, y1, x0, x1 = max(y - half, 0), y + half + 1, max(x - half, 0), x + half + 1
    box = img[y0:y1, x0:x1]
    if box.size == 0:
        return False, 0
    n = len(np.unique(box.reshape(-1, 3), axis=0))
    return n == 1, n


def region_changed(a, b, x, y, half=60):
    y0, y1, x0, x1 = max(y - half, 0), y + half, max(x - half, 0), x + half
    return not np.array_equal(a[y0:y1, x0:x1], b[y0:y1, x0:x1])


def find_template(img, tmpl):
    """Exact-match search anchored on the template's RAREST colour. Used to re-find the dropped node on
    screen after a close/re-open has reset the diagram's scroll, so the mapping can be re-measured
    without spending another drop."""
    th, tw, _ = tmpl.shape
    cols, counts = np.unique(tmpl.reshape(-1, 3), axis=0, return_counts=True)
    best, bestn = None, None
    for c in cols:
        n = int(np.count_nonzero(np.all(img == c, axis=-1)))
        if n and (bestn is None or n < bestn):
            best, bestn = c, n
    if best is None:
        return None
    ty, tx = np.where(np.all(tmpl == best, axis=-1))
    oy, ox = int(ty[0]), int(tx[0])
    ys, xs = np.where(np.all(img == best, axis=-1))
    for yy, xx in zip(ys.tolist(), xs.tolist()):
        y0, x0 = yy - oy, xx - ox
        if y0 < 0 or x0 < 0 or y0 + th > img.shape[0] or x0 + tw > img.shape[1]:
            continue
        if np.array_equal(img[y0:y0 + th, x0:x0 + tw], tmpl):
            return (x0, y0)
    return None


# ----------------------------------------------------------------- GUI primitives
def windows():
    return g._lv_gui("-Action", "windows")


def front(s, title):
    out = g._lv_gui("-Action", "activate", "-Title", '"{0}"'.format(title),
                    "-Exception", "VerifiedImpossible", "-Evidence", EV)
    s.fact("activate({0!r}) ok={1}".format(title, '"ok":true' in out.replace(" ", "")))
    return '"ok":true' in out.replace(" ", "")


def unwedge(s, tag=""):
    """A REAL click on the BD window's TITLE BAR. MANDATORY before any COM call after keystrokes:
    run 1 measured the 180 s hang that follows when none has landed (the skill's H5 law)."""
    g._lv_gui("-Action", "click", "-X", "400", "-Y", "10",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    time.sleep(0.6)
    s.R.setdefault("unwedge_clicks", []).append(tag)


def establish(s):
    """Open / re-open the Block Diagram window at a FIXED rect and make it the measured foreground."""
    name = os.path.basename(s.work)
    BD["title"] = "{0} Block Diagram".format(name)
    if BD["title"] not in windows():
        front(s, "{0} Front Panel".format(name))
        time.sleep(0.8)
        g._lv_gui("-Action", "keys", "-Key", "^e", "-WaitMs", "1500",
                  "-Exception", "VerifiedImpossible", "-Evidence", EV)
        time.sleep(1.2)
    g._lv_gui("-Action", "movewin", "-Title", '"{0}"'.format(BD["title"]),
              "-X", "0", "-Y", "0", "-Width", "1900", "-Height", "1030")
    time.sleep(0.8)
    ok = front(s, BD["title"])
    unwedge(s, "establish")
    return ok


def quick_drop(s, hover, click, tag):
    """ONE Quick Drop: hover at `hover`, Ctrl+Space, type, Enter, move to `click`, REAL LEFT CLICK there.

    THE PLACING CLICK IS THE POINT OF RUN 3. `archive/peer/2026-09-23-allterms-qd-invisible.md` §0/§3
    (claude/hypothesis, opus max, ANSWERED 631 s, $3.9792) refuted this recipe's whole framing from NI's
    own documentation: **Quick Drop's Enter does not place anything - it loads the item ONTO THE MOUSE
    CURSOR, and a click on the canvas places it.** Runs 1 and 2 never clicked inside the canvas at all,
    and the mandatory title-bar `unwedge` click - added to cure run 1's 180 s COM hang - is the only real
    click after Enter, so under those semantics it DISCARDED the pending object. That one mechanism
    explains both the hang (a drop pending on the cursor) and the empty traverse; (a) and (b) explain
    neither. So the gate below is no longer "the canvas changed at the hover point" - it is three
    captures: blank -> icon somewhere -> where the icon ends up after the placing click.

    NO COM inside. Returns (ok, png_before, png_after_enter, png_after_click)."""
    ok_front = front(s, BD["title"])
    g._lv_gui("-Action", "move", "-X", str(hover[0]), "-Y", str(hover[1]))
    before = shot(s, tag + "_before")
    g._lv_gui("-Action", "keys", "-Key", "^ ", "-WaitMs", "1200",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    opened = False
    for _ in range(12):
        if "Quick Drop" in windows():
            opened = True
            break
        time.sleep(1.5)
    if not opened:
        s.gate("QD[{0}] Quick Drop opened".format(tag), False, "windows {0!r}".format(windows()[:160]))
        return False, before, before, before
    g._lv_gui("-Action", "keys", "-Key", QD, "-WaitMs", "1200",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    g._lv_gui("-Action", "key", "-Key", "enter", "-WaitMs", "1500",
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    time.sleep(1.2)
    closed = "Quick Drop" not in windows()
    after_enter = shot(s, tag + "_afterenter")
    # THE PLACING CLICK - inside the canvas, never the title bar
    g._lv_gui("-Action", "move", "-X", str(click[0]), "-Y", str(click[1]))
    time.sleep(0.5)
    g._lv_gui("-Action", "click", "-X", str(click[0]), "-Y", str(click[1]),
              "-Exception", "VerifiedImpossible", "-Evidence", EV)
    time.sleep(1.2)
    after_click = shot(s, tag + "_afterclick")
    s.R.setdefault("drops", []).append({"tag": tag, "hover": hover, "click": click,
                                        "qd_opened": opened, "qd_closed": closed})
    s.gate("QD[{0}] foreground measured, Quick Drop opened and closed, placing click delivered at "
           "{1!r}".format(tag, click), ok_front and closed,
           "front={0!r} closed={1!r}".format(ok_front, closed))
    return (ok_front and closed), before, after_enter, after_click


def pick_blank(s, img, candidates, label, away_from=None, min_sep=0):
    """The first candidate whose 41x41 box is ONE colour in this very capture - the mechanical version of
    'locate the target in the capture taken just before the act' (pinned rule, 2026-09-18). A remembered
    coordinate is never used."""
    for c in candidates:
        if away_from is not None and (abs(c[0] - away_from[0]) + abs(c[1] - away_from[1])) < min_sep:
            continue
        ok, n = uniform_box(img, c[0], c[1])
        s.fact("point {0} candidate {1!r}: blank={2!r} colours={3}".format(label, c, ok, n))
        if ok:
            return c
    return None


def census(s, tag):
    """EVERY node, keyed by uid, with its Traverse class - `'Node'`, not `'Function'` (the review's §5:
    a wrong-class drop, e.g. `To More Generic Class` or a same-named subVI, must show as a count change
    instead of another silent zero). Returns {uid: class}."""
    rows, _e = s.safe("report_all(Node)", lambda: g.report_all(s.work, "Node"), [])
    d = dict((o["uid"], o["class"]) for o in (rows or []))
    s.fact("census[{0}] {1} nodes: {2!r}".format(tag, len(d), sorted(d.items())))
    return d


def on_body(s, uid):
    rows, _e = s.safe("node_labels(body)", lambda: g.node_labels(s.work, BODY_DIAGRAM_INDEX), [])
    return uid in [r["uid"] for r in (rows or [])]


def pos_of(s, uid):
    rows, _e = s.safe("report_all(Node)", lambda: g.report_all(s.work, "Node"), [])
    return next((tuple(o["pos"]) for o in (rows or []) if o["uid"] == uid), None)


def delete_uid(s, uid, cls="Function"):
    rows, _e = s.safe("report({0})".format(cls), lambda: g.report(s.work, cls), [])
    idx = next((i for i, o in enumerate(rows or []) if o["uid"] == uid), None)
    if idx is None:
        return False
    s.safe("delete_object({0},{1})".format(cls, idx), lambda: g.delete_object(s.work, cls, idx))
    s.safe("remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(s.work))
    return uid not in census(s, "after deleting {0}".format(uid))


def save_close_reopen(s, tag):
    """Hypothesis (b)'s commit: Ctrl+S (broken-intermediate permission), then unload and re-open by
    script. The scroll is NOT preserved, so the caller must re-measure the mapping."""
    before_md5 = K.md5(s.work)
    size, err = s.safe("gui_save", lambda: g.gui_save(s.work))
    time.sleep(1.0)
    after_md5 = K.md5(s.work)
    s.gate("SC[{0}] Ctrl+S moved the file (md5 changed)".format(tag), after_md5 != before_md5,
           "{0} -> {1} ({2} B) err={3!r}".format(before_md5[:8], after_md5[:8], size, err))
    s.safe("close_panel", lambda: g.close_panel(s.work))
    g.reset()
    time.sleep(2.0)
    s.safe("open_panel", lambda: g.open_panel(s.work, True))
    time.sleep(1.5)
    establish(s)
    return after_md5


# ----------------------------------------------------------------- the stage
def main(s):
    if not os.path.isdir(SHOTS):
        os.makedirs(SHOTS)
    s.start()
    p = s.work
    base = census(s, "entry")

    s.head("[B1] the loop is moved FIRST, before the window opens, so drop points land on canvas")
    newpos, _e = s.safe("move_object(ForLoop,0)", lambda: g.move_object(p, "ForLoop", 0, LOOP_AT))
    es0 = s.es("after the loop move")
    s.gate("B1 the loop is at diagram {0!r} and ExecState is still 1".format(LOOP_AT),
           tuple(newpos or ()) == LOOP_AT and es0 == 1,
           "pos {0!r} ExecState {1!r}".format(newpos, es0), fatal=True)

    s.head("[B2] the Block Diagram window, fronted without Esc and sized to a fixed rect")
    s.gate("B2 the Block Diagram window is the measured foreground", establish(s),
           BD["title"], fatal=True)

    s.head("[B3/B4] THE DISCRIMINATOR - hover at A, Enter, then the PLACING CLICK at a different point B")
    img0 = arr(shot(s, "canvas"))
    A = pick_blank(s, img0, HOVER_TRY, "A")
    B = pick_blank(s, img0, CLICK_TRY, "B", away_from=A, min_sep=300)
    s.gate("B3a two blank canvas points A and B were LOCATED IN THE CAPTURE, >=300 px apart",
           A is not None and B is not None, "A {0!r} B {1!r}".format(A, B), fatal=True)
    ok1, b1, e1, c1 = quick_drop(s, A, B, "d1")
    s.gate("B3 drop 1 completed", ok1, "hover {0!r} click {1!r}".format(A, B), fatal=True)

    # the three captures, read mechanically - this is the review's free test, taken for the first time
    img_b, img_e, img_c = arr(b1), arr(e1), arr(c1)
    at_A_enter = region_changed(img_b, img_e, A[0], A[1], half=40)
    at_A_click = region_changed(img_b, img_c, A[0], A[1], half=40)
    at_B_click = region_changed(img_b, img_c, B[0], B[1], half=40)
    s.R["pixels"] = {"A": A, "B": B, "icon_at_A_after_enter": bool(at_A_enter),
                     "icon_at_A_after_click": bool(at_A_click),
                     "icon_at_B_after_click": bool(at_B_click)}
    s.fact("PIXELS: after Enter A changed={0!r}; after the click at B, A changed={1!r} B changed={2!r}"
           .format(at_A_enter, at_A_click, at_B_click))
    new = dict((u, c) for u, c in census(s, "after the placing click").items() if u not in base)
    s.fact("NEW NODES after the placing click: {0!r}".format(sorted(new.items())))

    reopened = False
    if not new:
        # the review's §5 fallback, and the coordinator's step 3: only now is (b) worth its cost
        s.fact("no new node after the placing click - testing (b) with save + close + re-open")
        save_close_reopen(s, "d1")
        reopened = True
        new = dict((u, c) for u, c in census(s, "after save+close+re-open").items() if u not in base)

    verdict = None
    if new and reopened:
        verdict = "(b) STALE VI REFERENCE - only save+close+re-open made it visible"
    elif new and at_B_click and not at_A_click:
        verdict = "(c) CURSOR-LOADED - Enter loads the cursor, the CANVAS CLICK places it (NI doc)"
    elif new and at_A_click:
        verdict = "(a) ALREADY PLACED AT THE HOVER POINT - the click only committed it"
    elif not new:
        verdict = "(b)/none - no node exists even after a canvas click"
    else:
        verdict = "MIXED - see PIXELS and the new-node position"
    s.R["discriminator"] = {"verdict": verdict, "new": sorted(new.items())}
    s.gate("B4 THE DECIDER: a canvas click after Enter produces exactly ONE new node", len(new) == 1,
           "verdict {0}; new {1!r}".format(verdict, sorted(new.items())), fatal=True)
    s.fact("VERDICT: {0}".format(verdict))

    s.head("[B5] the mapping D, measured from the node VI Server now reports")
    u1 = sorted(new)[0]
    s.gate("B5a the new node's Traverse class is `Function` (a TMSC)", new[u1] == "Function",
           "class {0!r}".format(new[u1]))
    ppos = pos_of(s, u1)
    s.gate("B5b its diagram position is readable", ppos is not None, "pos {0!r}".format(ppos),
           fatal=True)
    anchor = B if (at_B_click and not at_A_click) else A
    if reopened:
        # the close/re-open reset the scroll, so the anchor is re-found by the node's OWN pixels
        tmpl = img_c[max(anchor[1] - 30, 0):anchor[1] + 30,
                     max(anchor[0] - 30, 0):anchor[0] + 30].copy()
        found = find_template(arr(shot(s, "relocate")), tmpl)
        s.gate("B5b2 the node was re-found on screen after the re-open", found is not None,
               "at {0!r}".format(found), fatal=True)
        anchor = (found[0] + 30, found[1] + 30)
    D = (ppos[0] - anchor[0], ppos[1] - anchor[1])
    s.R["calibration"] = {"anchor_screen": anchor, "drop_diagram": ppos, "D": D, "uid": u1}
    s.fact("CALIBRATION: the node sits at screen {0!r} = diagram {1!r}; D = {2!r}".format(
        anchor, ppos, D))

    kept = []
    if on_body(s, u1):
        kept.append(u1)
        s.fact("the discriminator's own node is ON THE BODY DIAGRAM - kept as TMSC #1")
    else:
        s.gate("B5c the discriminator's stray root node is deleted", delete_uid(s, u1),
               "uid {0}".format(u1))
    base = census(s, "after the discriminator")

    s.head("[B5c2] BRING THE LOOP TO THE MOUSE - run 3's only remaining defect was here")
    # Run 3 measured D = (1537, 1307): the window opens scrolled far right/down (the content bbox still
    # reaches the root-diagram indicator terminals at x~2928), so a loop parked at diagram (200,200) is
    # OFF-SCREEN to the upper-left and all four body candidates mapped to negative screen coordinates.
    # D is only knowable AFTER the discriminator, so the move belongs HERE, not before the window opened.
    before_move = arr(shot(s, "before_loop_move"))
    want = (LOOP_SCREEN[0] + D[0], LOOP_SCREEN[1] + D[1])
    moved, _e = s.safe("move_object(ForLoop,0)", lambda: g.move_object(p, "ForLoop", 0, want))
    front(s, BD["title"])
    after_move = arr(shot(s, "after_loop_move"))
    s.gate("B5c2 the loop is re-parked at diagram {0!r} = screen {1!r}, and the canvas THERE changed"
           .format(want, LOOP_SCREEN), tuple(moved or ()) == want
           and region_changed(before_move, after_move, LOOP_SCREEN[0], LOOP_SCREEN[1], half=60),
           "pos {0!r}".format(moved), fatal=True)

    s.head("[B5d] the real drops - hover AND click at the SAME body point, so the placement is "
           "hypothesis-independent")
    loop_screen = LOOP_SCREEN
    s.fact("the loop's top-left is at screen {0!r}".format(loop_screen))
    for k, (dx, dy) in enumerate(DROP_OFFSETS):
        if len(kept) >= 2 or s.left_s() < 240:
            break
        xy = (loop_screen[0] + dx, loop_screen[1] + dy)
        if not (10 < xy[0] < 1890 and 120 < xy[1] < 1010):
            s.fact("candidate {0!r} -> {1!r} is off-canvas - skipped".format((dx, dy), xy))
            continue
        blank, ncol = uniform_box(arr(shot(s, "c{0}_probe".format(k))), xy[0], xy[1])
        s.fact("candidate c{0} at screen {1!r}: blank={2!r} colours={3}".format(k, xy, blank, ncol))
        if not blank:
            s.fact("c{0} is not blank canvas - skipped rather than clicked onto an object".format(k))
            continue
        okk, _bb, _ee, _cc = quick_drop(s, xy, xy, "c{0}".format(k))
        if not okk:
            continue
        fresh = dict((u, c) for u, c in census(s, "after c{0}".format(k)).items() if u not in base)
        if not fresh:
            s.gate("B5 drop c{0} became visible to VI Server".format(k), False, "no new node")
            continue
        u2 = sorted(fresh)[0]
        base.update(fresh)
        if on_body(s, u2):
            kept.append(u2)
            s.fact("c{0}: uid {1} class {2!r} at {3!r} is ON THE BODY DIAGRAM".format(
                k, u2, fresh[u2], pos_of(s, u2)))
        else:
            s.fact("c{0}: uid {1} at {2!r} landed on the ROOT - deleting".format(k, u2, pos_of(s, u2)))
            s.gate("B5e stray root drop {0} deleted".format(u2), delete_uid(s, u2), "")
            base = census(s, "after deleting the stray")

    s.R["tmsc_uids"] = kept
    s.gate("B6a exactly TWO To More Specific Class nodes are on the BODY diagram", len(kept) == 2,
           "kept {0!r}".format(kept))
    shot(s, "final")

    s.head("[B6] SAVE the broken-by-design intermediate ({0})".format(EV_SAVE))
    s.save(broken_ok=True, cold_check=False)
    s.gate("B6b the artefact's md5 has moved away from S1", K.md5(s.work) != SRC_MD5,
           "md5 {0}".format(K.md5(s.work)))


S = K.Stage(SRC, SRC_MD5, "allterms_s2", fresh=True, preload=False, work_name=OUT,
            deadline_min=36.0, reserve_s=180.0,
            out_json=os.path.join(K.BENCH, "allterms_s2.json"),
            task="S2 run 3 of OpAllTerms_v0: DISCRIMINATE (a) uncommitted-while-selected vs (b) stale VI "
                 "reference for a Quick-Dropped node, then place two To More Specific Class nodes in the "
                 "For-loop body by the commit route that won, and save the broken-by-design intermediate.")
sys.exit(K.run(main, S))
