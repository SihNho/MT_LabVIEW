r"""diag_d1_execstate_preload.py - cycle 35 dispatch 4, MEASUREMENT ONLY. READ-ONLY on every .vi.

QUESTION (judgement brief): cycle 35 measured on the 3StateClamping original that a cold-opened claudeDev
copy reads ExecState 0 while the SAME byte-identical file reads ExecState 1 once the ORIGINAL has been
opened read-only first (`tools/bench/diag_d0_execstate_preload.log`, 9/9, rc=0). Route B copies a DIFFERENT
original - `tools/recipes/build_d1_routeb_v0.py:172` -> `Min_Track N beads V6_ParallelLoop.vi`. Repeat the
control on THAT file. Measure, do not repair, do not build, do not re-run the D1 build.

PRIOR ART - checked before writing (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/bench/diag_d0_execstate_preload.py`  - THE PATTERN, run yesterday on the 3StateClamping original.
                                                  Reused structurally (child-per-condition, lv_restart, raw
                                                  GetVIReference, handle accounting, scratch delete). NOT
                                                  re-run: its target and its ORIGINAL are the other file.
                                                  Only the target file and the condition set differ here;
                                                  the bare-terminal census (its C3-ii, 300 s budget per
                                                  ExecState-0 reading) is DROPPED - the brief asks for the
                                                  two numbers, not a re-census.
  * `tools/bench/p2_open_copy.py:25-28`         - the original preload pattern (GetVIReference(ORIG) then
                                                  GetVIReference(COPY)). Hold-open script, no cold arm.
  * `tools/gscript.py:1920-1921`                - `exec_state()` = GetVIReference(target).ExecState with no
                                                  preload; the readings below are raw COM so the two
                                                  conditions differ ONLY in the preload.
  * `tools/gscript.py:471` subvis, `:434` report_all - read-only readers, reused. NOTHING NEW IS BUILT.
  * `tools/lv_restart.py`, `tools/bench/bench_prep.py:64` labview_handles() - reused verbatim.

WHY EACH CONDITION IS ITS OWN CHILD PROCESS: a `Find the VI named ...` modal makes GetVIReference block with
no dialog visible to the caller, and a watchdog THREAD around GetVIReference was tried and rolled back
(`tools/gscript.py.guarded_attempt_20260905`). The PROCESS-level deadline is the guarantee.

PREDICTION CONTRACT (a gate that fails is a FACT to report, not a script failure)
  G0  the ORIGINAL `Min_Track N beads V6_ParallelLoop.vi` exists; md5 recorded BEFORE; it matches route B's
      pinned `ORIG_MD5 = 2a78e17c449cacdaf5da389818526859` (build_d1_routeb_v0.py:173).
  G1  a fresh scratch copy is made into claudeDev under a unique name, md5 identical to the original.
  G2  E1a - scratch copy, COLD (nothing preloaded)      -> an integer ExecState + VI.Name, no hang.
  G3  E1b - scratch copy, ORIGINAL preloaded read-only  -> ditto, and the ORIGINAL's own ExecState recorded.
  G4  both children complete (rc=0) inside their own timeout.
  G5  the ORIGINAL's md5 is UNCHANGED at the end.
  G6  the scratch copy is deleted by the run that made it.
  UNDER TEST: if ExecState 0 is a LINKAGE artefact of the reading instance, (a) != (b) here too. If it is a
  property of this file, (a) == (b). Either answer is a fact; neither is acted on in this dispatch.

NOT DONE, deliberately: no build, no wiring, no save, no VI edit, no motor, no camera, no GUI action, no
change to SR_QUEUE_AUTHORISED / TEMP_SINK_AUTHORISED. Rig state 조립 / ASSEMBLED.
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
ROUTEB_PINNED_MD5 = "2a78e17c449cacdaf5da389818526859"      # build_d1_routeb_v0.py:173
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CHILD_TIMEOUT_S = 780

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


# --- T0(a), cycle 46: the LLB-aware existence test. `os.path.exists` is ALWAYS False for a path INSIDE a .llb
# container FILE (`...\error.llb\Simple Error Handler.vi`, `...\General command.llb\POS?.vi` - the latter cannot
# even be an NTFS filename), so the 2026-09-19 dump flagged genuine, resolved links as broken. The container's
# own existence is what can be tested; a member of a present .llb is labelled IN-LLB, never MISSING.
def llb_root(path):
    """Nearest ancestor path component of `path` whose name ends in .llb, or None."""
    p = path
    while True:
        parent = os.path.dirname(p)
        if not parent or parent == p:
            return None
        if parent.lower().endswith(".llb"):
            return parent
        p = parent


def path_status(path):
    """OK (on disk) | IN-LLB (member of an existing .llb container) | MISSING | EMPTY."""
    if not path:
        return "EMPTY"
    if os.path.exists(path):
        return "OK"
    root = llb_root(path)
    if root and os.path.isfile(root):
        return "IN-LLB"
    return "MISSING"


# ======================================================================= CHILD: one condition, one process
def child(tag, target, preload):
    import gscript as g
    from bench_prep import labview_handles

    res = {"tag": tag, "target": target, "preload": preload}
    print("=== CHILD %s  preload=%s  target=%s" % (tag, preload, os.path.basename(target)), flush=True)

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

    app = g.lv()
    refs = {}
    if preload:
        refs["orig"] = app.GetVIReference(ORIG, "", False, 0)
        res["orig_execstate"] = int(refs["orig"].ExecState)
        res["orig_name"] = str(refs["orig"].Name)
        print("  FACT ORIGINAL preloaded read-only: ExecState %d, VI.Name %r"
              % (res["orig_execstate"], res["orig_name"]), flush=True)

    refs["vi"] = app.GetVIReference(target, "", False, 0)
    res["execstate"] = int(refs["vi"].ExecState)
    res["name"] = str(refs["vi"].Name)
    print("  FACT %s ==> ExecState %d  (1 = idle/runnable, 0 = broken)   VI.Name %r"
          % (tag, res["execstate"], res["name"]), flush=True)

    # --- T0(b), cycle 46: the dump used to run ONLY `if res["execstate"] == 0` - selection on the dependent
    # variable, so there was never a comparison condition. It now runs UNCONDITIONALLY, and every row carries
    # the condition it was taken under (tag, preload, the ExecState that reading returned).
    cond = "%s preload=%s execstate=%r" % (tag, preload, res["execstate"])
    print("  --- SUBVI DUMP, run unconditionally, condition: %s" % cond, flush=True)
    try:
        diags = g.report_all(target, "Diagram")
        out, bad = [], []
        for i in range(min(8, len(diags))):
            rows, err = g.subvis(target, i, strict=False)
            if err:
                print("  FACT subvis(diagram %d) op error: %s" % (i, str(err)[:120]), flush=True)
            for row in rows:
                st = path_status(row["path"])
                out.append((cond, i, row["uid"], row["name"], row["path"], st))
                if (not row["name"]) or st in ("EMPTY", "MISSING"):
                    bad.append((cond, i, row["uid"], row["name"], row["path"], st))
        res["subvi"] = {"condition": cond, "n": len(out), "bad": len(bad), "bad_rows": bad[:10],
                        "ndiag": len(diags), "rows": out,
                        "status_counts": {s: sum(1 for r in out if r[5] == s)
                                          for s in ("OK", "IN-LLB", "MISSING", "EMPTY")}}
        print("  FACT SUBVI RESOLUTION [%s]: %d calls over the first %d of %d diagrams; status counts %r; "
              "%d with an empty name or a genuinely absent path"
              % (cond, len(out), min(8, len(diags)), len(diags), res["subvi"]["status_counts"], len(bad)),
              flush=True)
        for row in bad[:10]:
            print("      UNRESOLVED [%s] Diagram[%d] uid %d name=%r path=%r status=%s" % row, flush=True)
        for row in out[:5]:
            print("      subVI      [%s] Diagram[%d] uid %d name=%r path=%r status=%s" % row, flush=True)
    except Exception as e:                                          # noqa: BLE001
        res["subvi"] = {"condition": cond, "error": str(e)[:200]}
        print("  FACT subvi probe raised %s: %s" % (type(e).__name__, str(e)[:200]), flush=True)

    refs.clear()                       # release every reference this child opened (CLAUDE.md ref hygiene)
    g.reset()
    res["handles_end"] = labview_handles()
    print("  FACT handles at end: %d (delta %+d)" % (res["handles_end"], res["handles_end"] - h0), flush=True)
    with open(os.path.join(HERE, "d1_es_%s.json" % tag), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    return 0


# ======================================================================= PARENT
def run_condition(tag, target, preload):
    print("\n=== %s  preload=%s  target=%s" % (tag, preload, os.path.basename(target)), flush=True)
    out_json = os.path.join(HERE, "d1_es_%s.json" % tag)
    if os.path.exists(out_json):
        os.remove(out_json)
    cmd = [sys.executable, "-u", os.path.abspath(__file__), "--child", tag, target,
           "1" if preload else "0"]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=CHILD_TIMEOUT_S)
        rc, so, se = r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired as e:
        rc = "TIMEOUT"
        so = (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        se = "child exceeded %d s (modal dialog or busy LabVIEW)" % CHILD_TIMEOUT_S
    for line in so.splitlines():
        print("  " + line, flush=True)
    if se.strip():
        for line in se.strip().splitlines()[-12:]:
            print("  STDERR " + line, flush=True)
    gate("%s child completed" % tag, rc == 0, "rc=%r after %.0f s" % (rc, time.time() - t0))
    if os.path.exists(out_json):
        with open(out_json, encoding="utf-8") as f:
            return json.load(f)
    return {"tag": tag, "target": target, "preload": preload, "execstate": "NO-RESULT", "rc": rc}


def main():
    print("=== diag_d1_execstate_preload  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    gate("G0a ORIGINAL exists", os.path.exists(ORIG), ORIG)
    m_orig0 = md5(ORIG)
    fact("md5 ORIGINAL BEFORE   %s   %s   %d bytes"
         % (m_orig0, os.path.basename(ORIG), os.path.getsize(ORIG)))
    gate("G0b ORIGINAL md5 equals route B's pinned ORIG_MD5", m_orig0 == ROUTEB_PINNED_MD5,
         "disk %s vs build_d1_routeb_v0.py:173 %s" % (m_orig0, ROUTEB_PINNED_MD5))

    stamp = time.strftime("%H%M%S")
    scratch = os.path.join(CLAUDEDEV, "SCRATCH_d1_execstate_%s.vi" % stamp)
    shutil.copy2(ORIG, scratch)
    m_scratch = md5(scratch)
    fact("fresh scratch copy made in this run: %s  md5 %s  %d bytes"
         % (os.path.basename(scratch), m_scratch, os.path.getsize(scratch)))
    gate("G1 scratch copy is byte-identical to the ORIGINAL", m_scratch == m_orig0,
         "scratch %s vs original %s" % (m_scratch, m_orig0))

    results = []
    try:
        results.append(run_condition("E1a-COLD-D1SCRATCH", scratch, False))
        results.append(run_condition("E1b-PRELOAD-D1SCRATCH", scratch, True))
    finally:
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"],
                           capture_output=True, timeout=120)
            time.sleep(8)
        except Exception:
            pass
        deleted = False
        for _ in range(8):
            try:
                os.remove(scratch)
                deleted = True
                break
            except Exception:
                time.sleep(4)
        gate("G6 scratch copy deleted by the run that made it",
             deleted and not os.path.exists(scratch), os.path.basename(scratch))

    m_orig1 = md5(ORIG)
    fact("md5 ORIGINAL AFTER    %s" % m_orig1)
    gate("G5 ORIGINAL md5 UNCHANGED", m_orig1 == m_orig0, "%s -> %s" % (m_orig0, m_orig1))

    print("\n=== SUMMARY TABLE", flush=True)
    for r in results:
        print("  %-24s preload=%-5s ExecState=%-10r VI.Name=%r"
              % (r["tag"], r["preload"], r.get("execstate"), r.get("name")), flush=True)
    es = {r["tag"]: r.get("execstate") for r in results}
    hz = {r["tag"]: (r.get("handles_after_restart"), r.get("handles_end")) for r in results}
    fact("D1 route-B scratch copy: cold %r vs preloaded %r -> %s"
         % (es.get("E1a-COLD-D1SCRATCH"), es.get("E1b-PRELOAD-D1SCRATCH"),
            "IDENTICAL" if es.get("E1a-COLD-D1SCRATCH") == es.get("E1b-PRELOAD-D1SCRATCH") else "DIFFERENT"))
    fact("handles (after restart -> end): cold %r, preload %r"
         % (hz.get("E1a-COLD-D1SCRATCH"), hz.get("E1b-PRELOAD-D1SCRATCH")))
    fact("ORIGINAL's own ExecState while preloaded: %r"
         % ([r.get("orig_execstate") for r in results if r.get("preload")] or [None])[0])

    with open(os.path.join(HERE, "d1_execstate_preload.json"), "w", encoding="utf-8") as f:
        json.dump({"orig": ORIG, "orig_md5_before": m_orig0, "orig_md5_after": m_orig1,
                   "scratch_md5": m_scratch, "results": results}, f, indent=1, default=str)
    print("\n=== GATES %d pass / %d fail" % (len(PASS), len(FAIL)), flush=True)
    for x in FAIL:
        print("  FAILING: " + x, flush=True)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        sys.exit(child(sys.argv[2], sys.argv[3], sys.argv[4] == "1"))
    sys.exit(main())
