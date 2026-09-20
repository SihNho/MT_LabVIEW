r"""s1_subvi_paths.py - T1, cycle 46 act 5. THE FULL SUBVI PATH CENSUS on three COLD conditions.
MEASUREMENT ONLY. READ-ONLY on every .vi: no save, no edit, no drop, no delete, no motor, no camera, no GUI.

QUESTION (the mandatory review's own cheapest discriminating test, archive/peer/2026-09-19-s1-saved-copy-cold-
execstate.md): the cold-0 subVI dump taken in S1 phase B covered 7 of 98 calls, was collected only in the
FAILING condition, and its "broken link" flag was `os.path.exists` on paths INSIDE `.llb` container files.
The review's alternative hypothesis is that the phase-A save CONVERTED search-resolved links into ABSOLUTE
links to whatever was resident, with `claudeDev\background VIs_COPY\` as cold-bind bait. That is decided by
one table: the FULL 98-row (diagram uid, node uid, name, path) census on

  T1-a ARM COLD      claudeDev\D1_s1arm_savetest.vi          (the saved arm, md5 e0112963cc1b9e3be29d2bb053ba9029)
  T1-b CONTROL COLD  claudeDev\D1_s1ctl2_bytecopy.vi         (a fresh shutil.copy2 of the ORIGINAL, made here)
  T1-c ORIGINAL COLD Min_Track N beads V6_ParallelLoop.vi    (opened READ-ONLY, never saved - rule 1)

This script MEASURES and TABULATES. It decides nothing, changes no gate, touches no plan document.

PRIOR ART - checked before writing (CLAUDE.md "before creating any new op, tool or recipe"; nothing new is
built here, no new op, no new gscript function):
  * tools/bench/sweep_subvis_main.py       - THE PRODUCER of tools/bench/main_vi_subvis.json (98 rows, the
                                             pin), `g.subvis(target, i)` once per Traverse-'Diagram' index.
                                             Its loop body is reused verbatim in shape; it is NOT re-run,
                                             because it reads only the ORIGINAL and caches diagram indices
                                             from tools/bench/diagram_tree_main.json (a file of the ORIGINAL's
                                             uids, which must not be assumed to hold for a saved copy - so
                                             the diagram list is READ FROM THE MACHINE per condition here).
  * tools/gscript.py:525 subvis            - the op call (OpSubVIs_v1, creator deleted, 0 junk/call measured,
                                             purge=False). Read-only. REUSED, unmodified.
  * tools/gscript.py:488 report_all        - Diagram objects of the target -> the DIAGRAM UIDs, index-aligned
                                             with subvis()'s `diagram_index`. REUSED, unmodified.
  * tools/bench/diag_d1_execstate_preload.py:88-179 - the child-process-per-condition harness (lv_restart per
                                             child, handle accounting, per-condition JSON, process-level
                                             deadline). REUSED structurally; `tools/recipes/stage_d1_s1.py`
                                             phase B imports the same helper for the same reason: a
                                             "Find the VI named ..." modal makes GetVIReference block with no
                                             dialog visible, and a watchdog THREAD was tried and rolled back
                                             (tools/gscript.py.guarded_attempt_20260905). ONE CONDITION PER
                                             CHILD, never two copies of the main VI in one instance, and NO
                                             PRELOAD in any of the three (all three must be COLD).
  * tools/lv_restart.py, tools/bench/bench_prep.py labview_handles() - reused verbatim.

PREDICTION CONTRACT (a gate that fails is a FACT to report, not a script failure)
  G0  the ORIGINAL exists and md5 == 2a78e17c449cacdaf5da389818526859 (route B's pin) BEFORE the run.
  G1  the ARM exists and md5 == e0112963cc1b9e3be29d2bb053ba9029 (the phase-A saved file).
  G2  a fresh byte copy of the ORIGINAL is made at claudeDev\D1_s1ctl2_bytecopy.vi, md5 == the ORIGINAL's.
  G3  each of the three children completes (rc == 0) inside its own process deadline.
  G4  each condition enumerates 98 subVI call sites (the pin: main_vi_subvis.json, 98 rows).
  G5  each condition reports 170 diagrams (the pinned Diagram count, STATUS cycle-46 census).
  G6  FATAL: md5(ORIGINAL) == 2a78e17c449cacdaf5da389818526859 at the end.
  UNDER TEST, and NOT acted on here: if the three conditions agree on all 98 paths, the save did not re-bind
  anything and the review's alternative is refuted for subVI links. If ARM's paths differ, the differing rows
  ARE the answer. Either outcome is a fact for the judgement session.

NOT DONE, deliberately: no save, no VI edit, no repair of any link, no judgement on whether the arm may serve
as a stage artefact, no edit to docs/cycle27-plan.md, no gate changed. Rig state 조립 / ASSEMBLED.

  MATERIAL=1 py tools/bgrun.py --max-min 55 --log tools/bench/s1_subvi_paths.log -- py -u tools/bench/s1_subvi_paths.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)

TRACKDIR = os.path.dirname(ROOT)
ORIG = os.path.join(TRACKDIR, "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5_PIN = "2a78e17c449cacdaf5da389818526859"
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
ARM = os.path.join(CLAUDEDEV, "D1_s1arm_savetest.vi")
ARM_MD5_PIN = "e0112963cc1b9e3be29d2bb053ba9029"
CTL = os.path.join(CLAUDEDEV, "D1_s1ctl2_bytecopy.vi")
BG_COPY = os.path.join(CLAUDEDEV, "background VIs_COPY")
OUT_JSON = os.path.join(HERE, "s1_subvi_paths.json")
PIN_ROWS = 98
PIN_DIAGRAMS = 170
CHILD_TIMEOUT_S = 900

CONDS = [("T1a-ARM-COLD", ARM), ("T1b-CTL-COLD", CTL), ("T1c-ORIG-COLD", ORIG)]

PASS = []
FAIL = []


def gate(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print("  %s %s%s" % ("GATE PASS" if ok else "GATE FAIL", label,
                         ("  | " + detail) if detail else ""), flush=True)
    return ok


def fact(s):
    print("  FACT " + s, flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ======================================================================= CHILD: one condition, one process
def child(tag, target):
    import gscript as g
    from bench_prep import labview_handles

    out_json = os.path.join(HERE, "s1_paths_%s.json" % tag)
    res = {"tag": tag, "target": target, "rows": [], "diagram_errors": [], "status": "STARTED"}

    def dump():
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=1, default=str)

    print("=== CHILD %s  target=%s" % (tag, os.path.basename(target)), flush=True)
    g.reset()
    r = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                       capture_output=True, text=True, timeout=400)
    last = ((r.stdout or "").strip().splitlines() or [""])[-1]
    g.reset()
    print("  FACT lv_restart rc=%d %r" % (r.returncode, last), flush=True)
    res["restart_rc"] = r.returncode
    h0 = labview_handles()
    res["handles_after_restart"] = h0
    print("  FACT handles after restart: %d  (fresh baseline ~31,500)" % h0, flush=True)
    dump()

    g._run.__defaults__ = (6.0, 120.0)             # sweep_subvis_main.py's bound, reused
    t0 = time.time()
    try:
        diags = g.report_all(target, "Diagram")    # index-aligned with subvis()'s diagram_index
        res["n_diagrams"] = len(diags)
        print("  FACT %d Diagram objects (pin %d), %.0f s" % (len(diags), PIN_DIAGRAMS, time.time() - t0),
              flush=True)
        dump()
        for i, d in enumerate(diags):
            try:
                rows, err = g.subvis(target, i, strict=False)
            except Exception as e:                                          # noqa: BLE001
                res["diagram_errors"].append({"i": i, "duid": d["uid"], "exc": "%s: %s"
                                              % (type(e).__name__, str(e)[:160])})
                print("  FACT diagram %d (uid %d): EXC %s" % (i, d["uid"], str(e)[:140]), flush=True)
                continue
            if err:
                res["diagram_errors"].append({"i": i, "duid": d["uid"], "err": str(err)[:160]})
                print("  FACT diagram %d (uid %d): op error %s" % (i, d["uid"], str(err)[:140]), flush=True)
            for row in rows:
                res["rows"].append({"diagram_index": i, "diagram_uid": d["uid"], "node_uid": row["uid"],
                                    "name": row["name"], "path": row["path"]})
            if rows:
                print("  ROW  d[%d] uid %d : " % (i, d["uid"]) +
                      "; ".join("%s#%d -> %s" % (x["name"], x["uid"], x["path"]) for x in rows), flush=True)
            if i % 20 == 19:
                dump()                              # partial census on disk before the next block
        res["status"] = "COMPLETED"
    except Exception as e:                                                  # noqa: BLE001
        res["status"] = "RAISED"
        res["exception"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("  FACT ENUMERATION RAISED %s: %s" % (type(e).__name__, str(e)[:300]), flush=True)
    res["n_rows"] = len(res["rows"])
    res["elapsed_s"] = round(time.time() - t0, 1)
    print("  FACT %s: %d subVI call rows over %s diagrams, %d diagram errors, %.0f s, status %s"
          % (tag, res["n_rows"], res.get("n_diagrams"), len(res["diagram_errors"]), res["elapsed_s"],
             res["status"]), flush=True)

    res["ref_counts_before_reset"] = g.ref_counts()
    g.reset()
    res["ref_counts"] = g.ref_counts()
    res["handles_end"] = labview_handles()
    print("  FACT ref_counts %r ; handles at end: %d (delta %+d)"
          % (res["ref_counts"], res["handles_end"], res["handles_end"] - h0), flush=True)
    dump()
    return 0


# ======================================================================= PARENT
def run_condition(tag, target):
    print("\n=== %s  target=%s" % (tag, target), flush=True)
    out_json = os.path.join(HERE, "s1_paths_%s.json" % tag)
    if os.path.exists(out_json):
        os.remove(out_json)
    cmd = [sys.executable, "-u", os.path.abspath(__file__), "--child", tag, target]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=CHILD_TIMEOUT_S)
        rc, so, se = r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired as e:
        rc = "TIMEOUT"
        so = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        se = "child exceeded %d s (modal dialog or busy LabVIEW)" % CHILD_TIMEOUT_S
    for line in (so or "").splitlines():
        print("  " + line, flush=True)
    if (se or "").strip():
        for line in se.strip().splitlines()[-12:]:
            print("  STDERR " + line, flush=True)
    gate("G3 %s child completed" % tag, rc == 0, "rc=%r after %.0f s" % (rc, time.time() - t0))
    if os.path.exists(out_json):
        with open(out_json, encoding="utf-8") as f:
            res = json.load(f)
        res["child_rc"] = rc
        return res
    return {"tag": tag, "target": target, "status": "NO-RESULT", "child_rc": rc, "rows": [],
            "diagram_errors": [], "n_rows": 0}


def llb_root(path):
    """Nearest ancestor DIRECTORY COMPONENT of `path` whose name ends in .llb, or None."""
    p = path
    while True:
        parent = os.path.dirname(p)
        if not parent or parent == p:
            return None
        if parent.lower().endswith(".llb"):
            return parent
        p = parent


def main():
    print("=== s1_subvi_paths (T1 full subVI path census)  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    gate("G0a ORIGINAL exists", os.path.exists(ORIG), ORIG)
    m_orig0 = md5(ORIG)
    fact("md5 ORIGINAL BEFORE  %s  %d bytes" % (m_orig0, os.path.getsize(ORIG)))
    gate("G0b ORIGINAL md5 == pin", m_orig0 == ORIG_MD5_PIN, "%s vs %s" % (m_orig0, ORIG_MD5_PIN))
    gate("G1a ARM exists", os.path.exists(ARM), ARM)
    m_arm = md5(ARM) if os.path.exists(ARM) else "-"
    fact("md5 ARM  %s  %s bytes" % (m_arm, os.path.getsize(ARM) if os.path.exists(ARM) else "-"))
    gate("G1b ARM md5 == phase-A saved pin", m_arm == ARM_MD5_PIN, "%s vs %s" % (m_arm, ARM_MD5_PIN))

    if os.path.exists(CTL):
        os.remove(CTL)
    shutil.copy2(ORIG, CTL)
    m_ctl = md5(CTL)
    fact("fresh byte copy made THIS RUN: %s  md5 %s  %d bytes"
         % (os.path.basename(CTL), m_ctl, os.path.getsize(CTL)))
    gate("G2 CONTROL byte copy identical to the ORIGINAL", m_ctl == m_orig0, "%s vs %s" % (m_ctl, m_orig0))

    results = {}
    try:
        for tag, target in CONDS:
            results[tag] = run_condition(tag, target)
    finally:
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
                           capture_output=True, timeout=120)
            time.sleep(8)
        except Exception:                                                   # noqa: BLE001
            pass

    # ---------------------------------------------------------------- TABLE 1: row count per condition
    print("\n=== TABLE 1  rows per condition (pin %d rows / %d diagrams)" % (PIN_ROWS, PIN_DIAGRAMS), flush=True)
    print("  %-16s %-10s %6s %9s %8s %-s" % ("condition", "status", "rows", "diagrams", "dgr_err", "ref_counts"),
          flush=True)
    for tag, _ in CONDS:
        r = results[tag]
        print("  %-16s %-10s %6d %9s %8d %-s"
              % (tag, r.get("status"), r.get("n_rows", 0), r.get("n_diagrams"), len(r.get("diagram_errors", [])),
                 r.get("ref_counts")), flush=True)
        gate("G4 %s enumerated %d rows" % (tag, PIN_ROWS), r.get("n_rows", 0) == PIN_ROWS,
             "%d rows" % r.get("n_rows", 0))
        gate("G5 %s saw %d diagrams" % (tag, PIN_DIAGRAMS), r.get("n_diagrams") == PIN_DIAGRAMS,
             "%r" % r.get("n_diagrams"))
        if r.get("exception"):
            fact("%s exception: %s" % (tag, r["exception"]))
        for de in r.get("diagram_errors", [])[:6]:
            fact("%s diagram error: %r" % (tag, de))

    # ---------------------------------------------------------------- TABLE 2: rows whose PATH differs
    keyed = {}
    for tag, _ in CONDS:
        keyed[tag] = {(x["diagram_uid"], x["node_uid"]): x for x in results[tag].get("rows", [])}
    allkeys = sorted(set().union(*[set(k) for k in keyed.values()]) if keyed else [])
    diffs = []
    for k in allkeys:
        vals = [keyed[t].get(k) for t, _ in CONDS]
        paths = [(v["path"] if v else None) for v in vals]
        names = [(v["name"] if v else None) for v in vals]
        if len(set(paths)) > 1 or len(set(names)) > 1:
            diffs.append({"diagram_uid": k[0], "node_uid": k[1],
                          "names": dict(zip([t for t, _ in CONDS], names)),
                          "paths": dict(zip([t for t, _ in CONDS], paths))})
    print("\n=== TABLE 2  rows whose (name, path) differs between the three conditions, keyed by "
          "(diagram uid, node uid)", flush=True)
    if not diffs:
        print("  EMPTY: all three conditions agree on all %d rows (keys compared: %d)"
              % (results[CONDS[0][0]].get("n_rows", 0), len(allkeys)), flush=True)
    for d in diffs:
        print("  DIFF diagram_uid %s node_uid %s" % (d["diagram_uid"], d["node_uid"]), flush=True)
        for tag, _ in CONDS:
            print("        %-16s name=%r  path=%r" % (tag, d["names"][tag], d["paths"][tag]), flush=True)

    # ---------------------------------------------------------------- TABLE 3: where the paths point
    print("\n=== TABLE 3  parent directory of every subVI path, per condition", flush=True)
    dircounts = {}
    for tag, _ in CONDS:
        c = {}
        n_bg = 0
        for x in results[tag].get("rows", []):
            d = os.path.dirname(x["path"])
            c[d] = c.get(d, 0) + 1
            if x["path"].lower().startswith(BG_COPY.lower()):
                n_bg += 1
        dircounts[tag] = c
        print("  %-16s into 'claudeDev\\background VIs_COPY\\': %d   elsewhere: %d   distinct dirs: %d"
              % (tag, n_bg, results[tag].get("n_rows", 0) - n_bg, len(c)), flush=True)
    alldirs = sorted(set().union(*[set(c) for c in dircounts.values()]) if dircounts else [])
    print("  %-6s %-6s %-6s  directory" % tuple(t.split("-")[0] for t, _ in CONDS), flush=True)
    for d in alldirs:
        print("  %-6d %-6d %-6d  %s" % tuple([dircounts[t].get(d, 0) for t, _ in CONDS] + [d]), flush=True)

    # ---------------------------------------------------------------- TABLE 4: the bait directory on disk
    print("\n=== TABLE 4  claudeDev\\background VIs_COPY\\ on disk", flush=True)
    bg_exists = os.path.isdir(BG_COPY)
    bg_files = []
    if bg_exists:
        for dirpath, _dirnames, filenames in os.walk(BG_COPY):
            for fn in filenames:
                if fn.lower().endswith(".vi"):
                    bg_files.append(os.path.join(dirpath, fn))
    print("  exists: %s   .vi files: %d   path: %s" % (bg_exists, len(bg_files), BG_COPY), flush=True)
    orig_rows = results[CONDS[2][0]].get("rows", [])
    orig_by_name = {}
    for x in orig_rows:
        orig_by_name.setdefault(os.path.basename(x["path"]).lower(), x["path"])
    md5_pairs = []
    for f in sorted(bg_files):
        base = os.path.basename(f).lower()
        twin = orig_by_name.get(base) or orig_by_name.get(base[:-3] if base.endswith(".vi") else base + ".vi")
        if twin and os.path.exists(twin):
            try:
                a, b = md5(f), md5(twin)
            except Exception as e:                                          # noqa: BLE001
                a, b = "ERR %s" % str(e)[:40], "-"
            md5_pairs.append({"name": os.path.basename(f), "copy_path": f, "copy_md5": a,
                              "original_side_path": twin, "original_side_md5": b, "same": a == b})
    if md5_pairs:
        print("  %-42s %-34s %-34s %s" % ("subVI name", "md5 in background VIs_COPY",
                                          "md5 at the ORIGINAL's own location", "same"), flush=True)
        for p in md5_pairs:
            print("  %-42s %-34s %-34s %s" % (p["name"][:42], p["copy_md5"], p["original_side_md5"], p["same"]),
                  flush=True)
            print("      copy: %s\n      orig: %s" % (p["copy_path"], p["original_side_path"]), flush=True)
    else:
        print("  no subVI name appears in BOTH that directory and the ORIGINAL condition's own subVI locations",
              flush=True)

    # ---------------------------------------------------------------- fatal gate + artefact
    m_orig1 = md5(ORIG)
    fact("md5 ORIGINAL AFTER   %s" % m_orig1)
    gate("G6 FATAL ORIGINAL md5 UNCHANGED", m_orig1 == ORIG_MD5_PIN and m_orig1 == m_orig0,
         "%s -> %s (pin %s)" % (m_orig0, m_orig1, ORIG_MD5_PIN))

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump({"when": time.strftime("%Y-%m-%d %H:%M:%S"),
                   "orig": ORIG, "orig_md5_before": m_orig0, "orig_md5_after": m_orig1,
                   "arm": ARM, "arm_md5": m_arm, "ctl": CTL, "ctl_md5": m_ctl,
                   "conditions": results, "diffs": diffs, "dircounts": dircounts,
                   "bg_copy": {"path": BG_COPY, "exists": bg_exists, "n_vi": len(bg_files),
                               "files": sorted(bg_files)[:200], "md5_pairs": md5_pairs}},
                  f, indent=1, default=str)
    fact("artefact %s  md5 %s" % (OUT_JSON, md5(OUT_JSON)))
    print("\n=== GATES %d pass / %d fail" % (len(PASS), len(FAIL)), flush=True)
    for x in FAIL:
        print("  FAILING: " + x, flush=True)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        sys.exit(child(sys.argv[2], sys.argv[3]))
    sys.exit(main())
