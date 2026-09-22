r"""diag_errorlist_v0 - TEST of `tools/lv_errorlist.py` (connectivity-map-plan STEP 2). READ-ONLY.

PREDICTION CONTRACT (desk-checked; Pre-decided 138 - the Error List is read from the GUI because
`VI.Get Errors` is absent from the exported ActiveX interface, 2026-09-18):
  P1  Ctrl+L on the fronted window of a BROKEN VI opens a NEW top-level LabVIEW window whose title
      matches /error\s*list/i.  FALSIFIED by no new window (then the keystroke never dispatched).
  P2  MEASURED, NOT PREDICTED: whether UI Automation exposes the list ITEMS at all.  LabVIEW ships no
      native UIA provider; the MSAA->UIA bridge may or may not surface an owner-drawn list.  The run
      records `uia_items_exposed` either way - this is the question STEP 2 exists to answer.
  P3  The reader returns >= 1 item and `item_count == n_reported` (the window's own "N errors"),
      i.e. nothing is lost to scrolling.  If the window prints no count, the comparison is a ROW.
  P4  The bed has 11 bad wires [1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540]
      (`docs/connectivity-map-plan.md:48`), so the item count is expected to relate to 11.  RECORDED
      AS A ROW, never a gate: how LabVIEW GROUPS broken wires into error-list rows is exactly what
      has never been measured here, and predicting the grouping would be inference over measurement.
  P5  Nothing is run, nothing is saved: both scratch copies' md5 are unchanged at the end and
      `THE FILES THIS RUN LEFT ON DISK` is [].

WHAT ALREADY EXISTS (checked first): NO error-list reader anywhere (`grep -rniE "error ?list|OCR|
pywinauto|uiautomation" docs/toolkit-capabilities.md tools/*.py tools/*.ps1` -> 0 hits).  This file
adds NO new LabVIEW op and NO new GUI primitive: it is inputs + gates over `tools/lv_errorlist.py`,
which itself only re-uses `gscript._lv_gui` / `tools/lv_gui.ps1` and `gscript.open_panel`.

GUI: every act goes through `lv_gui.ps1` with `-Exception Approved -Evidence "user 2026-09-23 error
list via GUI"` and is logged to `tools/gui_actions.log`.  No toolbar/run-arrow region is ever clicked:
the only click is on a TITLE BAR whose rect was just read (gscript.gui_save's measured-foreground idiom).
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import lv_errorlist as E                                                           # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
SECOND = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a_BROKEN_20260922_005732.vi")
SECOND_MD5 = "6b3c1f3c4ba80f1fa7411a55f0218bea"
SEVERED = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
DATE = time.strftime("%Y%m%d")


def cell(s, path, tag, expect_bad):
    s.head("[{0}] Error List on {1}".format(tag, os.path.basename(path)))
    # The plan's file name: tools/bench/errorlist_<vi>_<date>.json (connectivity-map-plan.md:49).
    out = os.path.join(K.BENCH, "errorlist_{0}_{1}.json".format(
        os.path.splitext(os.path.basename(path))[0][:44], DATE))
    t0 = time.time()
    r, err = s.safe("{0} read".format(tag), lambda: E.read(path, out, log=s.fact), None)
    dt = time.time() - t0
    if not r:
        s.gate("{0} the reader returned a record".format(tag), False, err, fatal=False)
        return None
    s.R.setdefault("cells", {})[tag] = {
        "json": out, "seconds": round(dt, 1), "method": r.get("method"),
        "uia_items_exposed": r.get("uia_items_exposed"), "n_reported": r.get("n_reported"),
        "item_count": r.get("item_count"), "gui_acts": len(r.get("gui_acts") or []),
        "window": (r.get("window") or {}).get("title"), "errors": r.get("errors")}
    s.fact("{0}: {1:.1f} s ; method={2!r} ; uia_items_exposed={3!r} ; window={4!r} ; "
           "win32 children={5} ; uia tree={6} elements".format(
               tag, dt, r.get("method"), r.get("uia_items_exposed"),
               (r.get("window") or {}).get("title"), len(r.get("win32_children") or []),
               r.get("uia_tree_size")))
    s.fact("{0}: ocr_engine={1!r} ; window count N={2!r} (from {3!r})".format(
        tag, r.get("ocr_engine"), r.get("n_reported"), r.get("n_reported_from")))
    s.fact("{0}: categories (non-error header rows)={1!r}".format(
        tag, [c["raw"] for c in (r.get("categories") or [])]))
    s.fact("{0}: GUI acts={1} ; confirms={2} ; reader errors={3!r}".format(
        tag, len(r.get("gui_acts") or []),
        sum(1 for a in (r.get("gui_acts") or []) if a.get("confirmed")), r.get("errors")))
    s.gate("P1 {0} Ctrl+L opened a new window titled like an Error List".format(tag),
           bool(r.get("window")), repr((r.get("window") or {}).get("title")))
    s.gate("P3a {0} the reader returned at least one item".format(tag), r["item_count"] >= 1,
           "item_count={0}".format(r["item_count"]))
    if r.get("n_reported") is not None:
        s.gate("P3b {0} item_count == the window's own count".format(tag),
               r["item_count"] == r["n_reported"],
               "{0} vs {1}".format(r["item_count"], r["n_reported"]))
    else:
        s.row("P3b {0} window printed no N".format(tag), r["item_count"], "N not found")
    s.gate("P3c {0} every item carries verbatim text".format(tag),
           bool(r["items"]) and all((i.get("raw") or "").strip() for i in r["items"]),
           "{0} of {1} non-empty".format(
               sum(1 for i in r["items"] if (i.get("raw") or "").strip()), r["item_count"]))
    s.gate("P5a {0} closed with Esc".format(tag), bool(r.get("closed_with_esc")),
           repr(r.get("closed_with_esc")))
    s.row("P4 {0} items vs bad wires".format(tag), r["item_count"], expect_bad)
    for i in r["items"][:5]:
        s.fact("{0} item {1}: object={2!r} reason={3!r} detail={4!r} route={5}".format(
            tag, i["index"], i["object"][:60], i["reason"][:90], (i["detail"] or "")[:110],
            i.get("selection_route")))
    hits = [u for u in SEVERED if any(str(u) in (i.get("raw") or "") + (i.get("detail") or "")
                                      for i in r["items"])]
    s.row("{0} severed wire uids named in the item text".format(tag), hits, "unknown - measured")
    return r


def main(s):
    s.start()
    s.discard_work()
    s.fact("SECOND file on disk: {0} md5 {1}".format(os.path.basename(SECOND),
                                                     K.md5(SECOND) if os.path.exists(SECOND) else "MISSING"))
    a = cell(s, s.work, "bed", len(SEVERED))
    # CONTROL, measured (not guessed): run 1's own capture of this bed reads "14 errors and
    # warnings" (tools/bench/errorlist_shots/errwin_053448.png), and 14 = 3 junk Invoke-node
    # errors + the 11 severed wires.  A different N means the reader, not the VI, changed.
    s.gate("C1 the bed's window count is the 14 measured on run 1's capture",
           (a or {}).get("n_reported") == 14, repr((a or {}).get("n_reported")))
    s.gate("C2 the bed yields 14 items", (a or {}).get("item_count") == 14,
           repr((a or {}).get("item_count")))
    s.row("C3 bed items whose text names a wire", len([i for i in (a or {}).get("items") or []
                                                       if "wire" in (i.get("raw") or "").lower()]),
          11)
    s.gate("P5b the bed work copy is byte-unchanged (never saved, never run)",
           K.md5(s.work) == BED_MD5, K.md5(s.work))
    s.drop_scratch(s.work, tag="H4a")

    if os.path.exists(SECOND) and s.left_s() > 180:
        sc = s.scratch("second", source=SECOND)
        s.safe("open_panel(second)", lambda: g.open_panel(sc))
        b = cell(s, sc, "m3a_broken", None)
        s.gate("P5c the second scratch is byte-unchanged", K.md5(sc) == SECOND_MD5, K.md5(sc))
        s.fact("SECOND FILE COUNT: {0!r} items, window N={1!r}".format(
            (b or {}).get("item_count"), (b or {}).get("n_reported")))
        s.gate("C4 the second file's window count is the 11 measured on run 1's capture",
               (b or {}).get("n_reported") == 11, repr((b or {}).get("n_reported")))
    else:
        s.fact("second file skipped (exists={0}, {1:.0f} s left)".format(
            os.path.exists(SECOND), s.left_s()))
    s.fact("METHOD OUTCOME: uia_items_exposed={0!r} (bed)".format(
        (a or {}).get("uia_items_exposed")))


# `fresh=False`: a PARALLEL material session holds the LabVIEW lock for OpAllTerms_v0 STEP 1 and wrote
# into STATUS's lock block that it does not restart either. Restarting here would kill its instance.
S = K.Stage(BED, BED_MD5, "diag_errorlist_v0", fresh=False, deadline_min=24.0, reserve_s=150.0,
            out_json=os.path.join(K.BENCH, "diag_errorlist_v0.json"),
            task="STEP 2: does tools/lv_errorlist.py read EVERY Error List item of a broken VI, "
                 "count-checked against the window's own N. Read-only; no VI run, nothing saved.")
sys.exit(K.run(main, S))
