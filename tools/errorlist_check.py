r"""errorlist_check - the cycle-start LabVIEW Error List check (user decision 5, 2026-09-24):
"사이클 시작하기 전에 LabVIEW 컴파일 에러 창은 반드시 확인해야할듯. GUI로 에러 내용 확인하고 각 에러 더블클릭하면 에러
위치로 이동해서 보여주거든. (블락 다이어그램 켜진 상태에서)".

WHAT ALREADY EXISTS (checked first): `tools/lv_errorlist.py` reads every Error List row by capture+OCR, count-checked
against the window's own "N errors and warnings" (docs/toolkit-capabilities.md:313; test tools/bench/diag_errorlist_v0.py).
This file REUSES it unchanged except for one optional per-item hook (`on_item`), and adds: a byte-identical SCRATCH copy
(the bed itself is never opened), Ctrl+E so the block diagram is up, a double-click per item with a capture of the
block diagram before/after, a zero-item path for a runnable VI, the expected-errors comparison, and the cleanup proofs.
The selected object's UID is NOT read: `TopLevelDiagram.Selection List[]` 0x6349400 exists (NI API ref) but the fleet
has no op that reads it (`grep "Selection" tools/gscript.py` -> 0), and branching `Open VI Reference.vi reference`
into a VI-class property node is a MEASURED failure (docs/toolkit-capabilities.md:666). Recorded per item as uid=None.

PREDICTION CONTRACT: Ctrl+E opens '<scratch> Block Diagram'; Ctrl+L opens a new 'Error list' window; items read ==
the window's own N (0 for a runnable VI); each double-click fronts the block diagram and changes its capture; the
Error List is closed with Esc; the scratch is closed and deleted; the bed md5 is unchanged; no VI is run or saved.
Every GUI act goes through lv_gui.ps1 with -Exception Approved -Evidence EVID (logged to tools/gui_actions.log).

  py tools/errorlist_check.py [--vi <bed.vi>] [--expected <file.json>]      rc 0 OK / 1 MISMATCH / 2 FAIL
  expected file: {"expected": [{"match": "<substring of the row text>", "count": n}, ...]}  (default: none = [])
Last stdout line: `ERRORLIST-VERDICT: OK|MISMATCH|FAIL <json path>`.
"""
import argparse, glob, hashlib, json, os, re, shutil, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "bench"))
import gscript as g                                                                # noqa: E402
import lv_errorlist as E                                                           # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402

EVID = "user 2026-09-24 error-list check at cycle start"
E.EVIDENCE = EVID
BENCH = os.path.join(HERE, "bench")
COUNT_RE = re.compile(r"(\d+)\s*errors?\s*and\s*warnings?", re.I)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def current_bed(status_path):
    """`current-bed: <file.vi>` in STATUS wins; else the NEWEST-on-disk claudeDev D1_*.vi that STATUS names."""
    txt = open(status_path, encoding="utf-8").read()
    m = re.search(r"^current-bed:\s*(\S+\.vi)", txt, re.M)
    names = [m.group(1)] if m else sorted(set(re.findall(r"(D1_[\w\-]+\.vi)", txt)))
    paths = [os.path.join(g.CLAUDEDEV, os.path.basename(n)) for n in names]
    paths = [p for p in paths if os.path.exists(p)]
    return max(paths, key=os.path.getmtime) if paths else None


def windows_named(sub):
    return [(h, t) for h, t, _c, _r in E.top_windows(E.lv_pid()) if sub.lower() in (t or "").lower()]


def open_diagram(scratch, R):
    name = os.path.basename(scratch)
    bd = "%s Block Diagram" % name
    if windows_named(bd):
        return True
    title, fg = E._focus_vi_window(scratch, R["gui_acts_outer"])
    if not title:
        R["errors"].append("could not front the scratch: %s" % fg)
        return False
    E.shot("before_ctrl_e", R["gui_acts_outer"])
    E.send_keys("^e", R["gui_acts_outer"], "open block diagram", wait_ms=1500)
    t0 = time.time()
    while time.time() - t0 < 15 and not windows_named(bd):
        time.sleep(0.5)
    ok = bool(windows_named(bd))
    E.shot("after_ctrl_e", R["gui_acts_outer"])
    R["gui_acts_outer"].append({"act": "confirm", "tag": "ctrl+e opened the block diagram", "confirmed": ok})
    return ok


def make_on_item(scratch, R):
    bd = "%s Block Diagram" % os.path.basename(scratch)

    def shot_bd(tag):
        p = os.path.join(E.SHOTS, "bd_%s_%s.png" % (time.strftime("%H%M%S"), tag))
        g._lv_gui("-Action", "shotwin", "-Title", '"%s"' % bd, "-Out", p)
        return (p, md5(p)) if os.path.exists(p) else (None, None)

    def on_item(rec, acts):
        import win32gui
        b_path, b_md5 = shot_bd("before%d" % rec["index"])            # capture
        x0, y0, x1, y1 = rec["screen_rect"]                              # locate: the row on the live capture
        x, y = x0 + (x1 - x0) // 4, (y0 + y1) // 2
        g._lv_gui("-Action", "dclick", "-X", str(x), "-Y", str(y), "-Exception", "Approved", "-Evidence", EVID)
        acts.append({"act": "dclick", "tag": "item %d" % rec["index"], "screen_xy": [x, y]})
        time.sleep(1.5)
        fg = win32gui.GetWindowText(win32gui.GetForegroundWindow())       # act -> capture -> confirm
        a_path, a_md5 = shot_bd("after%d" % rec["index"])
        still = bool(windows_named("error list"))
        rec["show_error"] = {"fg_after": fg, "bd_before": b_path, "bd_after": a_path,
                             "bd_changed": bool(a_md5 and a_md5 != b_md5), "diagram_fronted": bd in fg,
                             "error_list_still_open": still, "uid": None, "class": None,
                             "uid_route": "none: Selection List[] 6349400 op not built"}
        acts.append({"act": "confirm", "tag": "item %d diagram fronted + changed" % rec["index"],
                     "confirmed": bd in fg and rec["show_error"]["bd_changed"]})
        if not still:
            raise RuntimeError("the Error List closed after the double-click")
    return on_item


def count_zero(R):
    """A runnable VI has no highlighted row, so lv_errorlist never reads N: OCR the last dialog capture whole."""
    caps = [a["path"] for a in R.get("gui_acts", []) if a.get("act") == "shotwin" and a.get("path")]
    caps += sorted(glob.glob(os.path.join(E.SHOTS, "errwin_*.png")), key=os.path.getmtime)[-1:]
    for p in caps[:1] + caps[-1:]:
        from PIL import Image
        for t, _c, _a, _b, _x in E.ocr_lines(Image.open(p).convert("RGB"), scale=2):
            m = COUNT_RE.search(t)
            if m:
                return int(m.group(1)), t, p
    return None, None, caps[-1] if caps else None


def compare(items, expected):
    left = [dict(e, count=int(e.get("count", 1))) for e in expected]
    extra = []
    for it in items:
        txt = "%s %s" % (it.get("raw") or "", it.get("detail") or "")
        hit = next((e for e in left if e["count"] > 0 and e["match"].lower() in txt.lower()), None)
        if hit:
            hit["count"] -= 1
        else:
            extra.append(it.get("raw"))
    missing = [e["match"] for e in left for _ in range(e["count"])]
    return extra, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vi", default="")
    ap.add_argument("--expected", default="")
    ap.add_argument("--status", default=os.path.join(ROOT, "STATUS.md"))
    a = ap.parse_args()
    t0, ts = time.time(), time.strftime("%Y%m%d_%H%M%S")
    bed = a.vi or current_bed(a.status)
    R = {"bed": bed, "stamp": ts, "errors": [], "gui_acts_outer": [], "no_vi_was_run": True, "evidence": EVID}
    out = os.path.join(BENCH, "errorlist_%s_%s.json" % (os.path.splitext(os.path.basename(bed or "none"))[0], ts))
    verdict = "FAIL"
    if not bed or not os.path.exists(bed):
        R["errors"].append("no bed: %r" % bed)
    else:
        R["bed_md5_before"] = md5(bed)
        R["handles_before"] = labview_handles()
        exp_path = a.expected or os.path.join(BENCH, "errorlist_expected_%s.json" %
                                              os.path.splitext(os.path.basename(bed))[0])
        expected = json.load(open(exp_path, encoding="utf-8")).get("expected", []) if os.path.exists(exp_path) else []
        R["expected_file"] = exp_path if os.path.exists(exp_path) else None
        scratch = os.path.join(g.CLAUDEDEV, "_elc_%s_%s.vi" % (os.path.splitext(os.path.basename(bed))[0][:40], ts))
        shutil.copyfile(bed, scratch)
        R["scratch"], R["scratch_identical"] = scratch, md5(scratch) == R["bed_md5_before"]
        print("bed %s md5 %s -> scratch %s identical=%s" % (bed, R["bed_md5_before"], scratch,
                                                              R["scratch_identical"]), flush=True)
        try:
            g._lv = None
            g.open_panel(scratch)
            time.sleep(1.0)
            R["exec_state"] = g.exec_state(scratch)
            R["block_diagram_open"] = open_diagram(scratch, R)
            r = E.read(scratch, out.replace(".json", "_raw.json"), log=lambda s: print(s, flush=True),
                       on_item=make_on_item(scratch, R))
            R.update({k: r.get(k) for k in ("method", "n_reported", "n_reported_from", "items", "categories",
                                            "gui_acts", "closed_with_esc", "window", "ocr_engine")})
            R["errors"] += r.get("errors") or []
            if not R["items"]:
                n0, line, cap = count_zero(R)
                R["n_reported"], R["n_reported_from"], R["zero_capture"] = (
                    R["n_reported"] if R["n_reported"] is not None else n0), line, cap
                R["errors"] = [e for e in R["errors"] if "errors band" not in e and "highlighted row" not in e]
        except Exception as e:                                                     # noqa: BLE001
            R["errors"].append("%s: %s" % (type(e).__name__, str(e)[:240]))
        try:
            g.close_panel(scratch)
        except Exception as e:                                                     # noqa: BLE001
            R["errors"].append("close_panel: %s" % str(e)[:160])
        for _ in range(6):
            try:
                os.remove(scratch)
                break
            except OSError:
                time.sleep(2.0)
        R["scratch_deleted"] = not os.path.exists(scratch)
        R["bed_md5_after"] = md5(bed)
        R["handles_after"] = labview_handles()
        R["ref_counts"] = g.ref_counts()
        items = R.get("items") or []
        R["item_count"] = len(items)
        R["show_error_ok"] = sum(1 for i in items if (i.get("show_error") or {}).get("diagram_fronted"))
        R["extra"], R["missing"] = compare(items, expected)
        read_ok = (bool(R.get("window")) and R.get("n_reported") is not None and R["item_count"] == R["n_reported"]
                   and R.get("closed_with_esc") and R["scratch_deleted"]
                   and R["bed_md5_after"] == R["bed_md5_before"] and R.get("block_diagram_open"))
        verdict = ("OK" if not (R["extra"] or R["missing"]) else "MISMATCH") if read_ok else "FAIL"
    R["verdict"], R["seconds"] = verdict, round(time.time() - t0, 1)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False, default=str)
    print("items %s / window N %s ; show-error fronted %s ; extra %s ; missing %s ; errors %s ; handles %s -> %s ; "
          "bed md5 unchanged %s ; %.1f s" % (R.get("item_count"), R.get("n_reported"), R.get("show_error_ok"),
                                             len(R.get("extra") or []), len(R.get("missing") or []), R["errors"],
                                             R.get("handles_before"), R.get("handles_after"),
                                             R.get("bed_md5_after") == R.get("bed_md5_before"), R["seconds"]),
          flush=True)
    print("ERRORLIST-VERDICT: %s %s" % (verdict, out), flush=True)
    return {"OK": 0, "MISMATCH": 1}.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
