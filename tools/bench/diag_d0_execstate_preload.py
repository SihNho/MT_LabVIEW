r"""diag_d0_execstate_preload.py - cycle 35 dispatch 3, MEASUREMENT ONLY. READ-ONLY on every .vi.

QUESTION (judgement brief): the claudeDev D0 copy `Track_D0_copy_20260918.vi` read ExecState 0 four times,
while STATUS records D0 as DELIVERED on a plain copy that ran end-to-end twice. `docs/cycle27-plan.md`
Pre-decided 4 (`:48`) says opening a claudeDev copy needs the ORIGINAL preloaded read-only
(`tools/bench/p2_open_copy.py` pattern). So: is ExecState 0 a property of the VI, or of the LINKAGE state of
the LabVIEW instance that read it? Measure, do not repair.

PRIOR ART - checked before writing (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/bench/p2_open_copy.py:25-28`   - the preload pattern (GetVIReference(ORIG) then GetVIReference(COPY)).
                                            It is a HOLD-OPEN script, not a comparison; no cold arm, no restart,
                                            no census. Reused as the PATTERN, not re-run.
  * `tools/gscript.py:1920-1921`          - `exec_state()` = GetVIReference(target).ExecState, no preload, and the
                                            reference is never closed. The ExecState reads below are raw COM so
                                            the two conditions differ ONLY in the preload.
  * `tools/gscript.py:816` node_terms, `:533` node_labels, `:434` report_all, `:471` subvis - the read-only
                                            readers. All exist; NOTHING NEW IS BUILT here.
  * `tools/lv_restart.py`                 - the restart (standing authority, CLAUDE.md 3). Reused verbatim.
  * `tools/bench/bench_prep.py:64`        - labview_handles(). Reused.
  * `grep "^def " tools/gscript.py`       - 97 functions; NO reader returns `Wire.Is Broken?` from a HELD
                                            terminal reference. `docs/toolkit-capabilities.md:68` says exactly
                                            that ("NOT BUILT"), and the one that IS built (OpConnectFromWire_v0's
                                            ordered W7b readout) fires only AFTER a `Terminal.Connect Wire`, i.e.
                                            a WRITE, and `docs/NAMES.md:898-909` MEASURED that reading it
                                            perturbs the target (ExecState 1 -> 0 on an untouched scratch).
                                            => brief item C3(i) is NOT PERFORMABLE in a read-only dispatch.
                                            Stated as a fact + OPEN; C3(ii), the bare-terminal census
                                            (`docs/cycle15-plan.md` Pre-decided 4 `:129-130`), IS run.

WHY EACH CONDITION IS ITS OWN CHILD PROCESS: a `Find the VI named ...` modal makes GetVIReference block with no
dialog visible to the caller, and routing GetVIReference through a watchdog THREAD was tried and rolled back -
it blocked in cross-apartment marshalling (`tools/gscript.py.guarded_attempt_20260905`, CLAUDE.md "the
PROCESS-level deadline of bgrun is the guarantee, not per-call guards"). So each condition runs in a child with
its own `subprocess.run(timeout=...)`: a hang costs that condition, not the run.

PREDICTION CONTRACT (a gate that fails is a FACT to report, not a script failure)
  G0  both files present; md5 of the ORIGINAL recorded BEFORE; is the D0 copy byte-identical to it?
  G1  four LabVIEW restarts succeed and COM answers; handles recorded per condition.
  G2  C1a - D0 copy, COLD (nothing preloaded)      -> an integer ExecState + VI.Name, no hang.
  G3  C1b - D0 copy, ORIGINAL preloaded read-only  -> ditto.
  G4  C2a / C2b - the same two readings on a FRESH copy of the ORIGINAL made in this run.
  G5  every ExecState-0 reading is followed, BEFORE any close or delete, by subvis() (C5) and the bare-terminal
      census (C3-ii), on the live VI.
  G6  the ORIGINAL's md5 is UNCHANGED at the end; the scratch copy is deleted by the run that made it.
  UNDER TEST: if ExecState 0 is a LINKAGE artefact, (a) != (b). If it is a property of the file, (a) == (b), and
  C2 separates "this copy is damaged" from "any cold-opened copy reads broken".

NOT DONE, deliberately: no build, no wiring, no save, no VI edit, no motor, no camera, no GUI action.
Rig state 조립 / ASSEMBLED.
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
ORIG = os.path.join(TRACKDIR, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
D0COPY = os.path.join(CLAUDEDEV, "Track_D0_copy_20260918.vi")
CENSUS_BUDGET_S = 300.0
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

    if res["execstate"] == 0:
        print("  --- ExecState 0: MEASURE BEFORE CLOSING (cycle27 Pre-decided 14)", flush=True)
        # ---- C5: do the subVI calls resolve?
        try:
            diags = g.report_all(target, "Diagram")
            out, bad = [], []
            for i in range(min(8, len(diags))):
                rows, err = g.subvis(target, i, strict=False)
                if err:
                    print("  FACT subvis(diagram %d) op error: %s" % (i, str(err)[:120]), flush=True)
                for row in rows:
                    out.append((i, row["uid"], row["name"], row["path"]))
                    if (not row["name"]) or (not row["path"]) or (not os.path.exists(row["path"])):
                        bad.append((i, row["uid"], row["name"], row["path"]))
            res["subvi"] = {"n": len(out), "bad": len(bad), "bad_rows": bad[:10], "ndiag": len(diags)}
            print("  FACT SUBVI RESOLUTION: %d calls over the first %d of %d diagrams; %d with empty name/path "
                  "or a path not on disk" % (len(out), min(8, len(diags)), len(diags), len(bad)), flush=True)
            for row in bad[:10]:
                print("      UNRESOLVED Diagram[%d] uid %d name=%r path=%r" % row, flush=True)
            for row in out[:5]:
                print("      subVI      Diagram[%d] uid %d name=%r path=%r" % row, flush=True)
        except Exception as e:                                          # noqa: BLE001
            res["subvi"] = {"error": str(e)[:200]}
            print("  FACT subvi probe raised %s: %s" % (type(e).__name__, str(e)[:200]), flush=True)
        # ---- C3(ii): bare NAMED input terminals. NOT a verdict on its own - an unwired `error in (no error)`
        #      is legal LabVIEW (build_d1_routeb_v0.py:1295-1299 measured 420 such on a VI whose brokenness had
        #      nothing to do with them).
        try:
            t0 = time.time()
            diags = g.report_all(target, "Diagram")
            bare, covered, errs = [], 0, 0
            for i in range(len(diags)):
                if time.time() - t0 > CENSUS_BUDGET_S:
                    break
                try:
                    rows = g.node_labels(target, i)
                except Exception:
                    errs += 1
                    continue
                covered += 1
                for n in range(len(rows)):
                    if time.time() - t0 > CENSUS_BUDGET_S:
                        break
                    try:
                        for rr in g.node_terms(target, i, n):
                            if (not rr["is_source"]) and rr["wire"] == 0 and rr["name"]:
                                bare.append((i, n, rr["i"], rr["name"]))
                    except Exception:
                        break
            partial = (time.time() - t0) > CENSUS_BUDGET_S
            res["census"] = {"bare": len(bare), "covered": covered, "ndiag": len(diags),
                             "partial": partial, "first10": bare[:10]}
            print("  FACT BARE-TERMINAL CENSUS: %d bare named input terminals over %d/%d diagrams (%d diagram "
                  "reads raised), %.0f s%s" % (len(bare), covered, len(diags), errs, time.time() - t0,
                                               "  [BUDGET HIT - PARTIAL]" if partial else ""), flush=True)
            for row in bare[:10]:
                print("      BARE Diagram[%d] Nodes[%d].T[%d] %r" % row, flush=True)
        except Exception as e:                                          # noqa: BLE001
            res["census"] = {"error": str(e)[:200]}
            print("  FACT census raised %s: %s" % (type(e).__name__, str(e)[:200]), flush=True)

    refs.clear()                       # release every reference this child opened (CLAUDE.md ref hygiene)
    g.reset()
    res["handles_end"] = labview_handles()
    print("  FACT handles at end: %d (delta %+d)" % (res["handles_end"], res["handles_end"] - h0), flush=True)
    with open(os.path.join(HERE, "d0_es_%s.json" % tag), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=1, default=str)
    return 0


# ======================================================================= PARENT
def run_condition(tag, target, preload):
    print("\n=== %s  preload=%s  target=%s" % (tag, preload, os.path.basename(target)), flush=True)
    out_json = os.path.join(HERE, "d0_es_%s.json" % tag)
    if os.path.exists(out_json):
        os.remove(out_json)
    cmd = [sys.executable, "-u", os.path.abspath(__file__), "--child", tag, target,
           "1" if preload else "0"]
    t0 = time.time()
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=CHILD_TIMEOUT_S)
        rc, so, se = r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired as e:
        rc, so, se = "TIMEOUT", (e.stdout or b"").decode("utf-8", "replace") if isinstance(e.stdout, bytes) \
            else (e.stdout or ""), "child exceeded %d s (modal dialog or busy LabVIEW)" % CHILD_TIMEOUT_S
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
    print("=== diag_d0_execstate_preload  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    gate("G0a ORIGINAL exists", os.path.exists(ORIG), ORIG)
    gate("G0b D0 copy exists", os.path.exists(D0COPY), D0COPY)
    m_orig0 = md5(ORIG)
    m_copy = md5(D0COPY)
    fact("md5 ORIGINAL BEFORE   %s   %s   %d bytes"
         % (m_orig0, os.path.basename(ORIG), os.path.getsize(ORIG)))
    fact("md5 D0 COPY           %s   Track_D0_copy_20260918.vi   %d bytes"
         % (m_copy, os.path.getsize(D0COPY)))
    gate("G0c the D0 copy is byte-identical to the ORIGINAL", m_copy == m_orig0,
         "copy %s vs original %s" % (m_copy, m_orig0))

    stamp = time.strftime("%H%M%S")
    scratch = os.path.join(CLAUDEDEV, "SCRATCH_execstate_%s.vi" % stamp)
    shutil.copy2(ORIG, scratch)
    fact("fresh scratch copy made in this run: %s  md5 %s" % (os.path.basename(scratch), md5(scratch)))

    results = []
    try:
        results.append(run_condition("C1a-COLD-D0COPY", D0COPY, False))
        results.append(run_condition("C1b-PRELOAD-D0COPY", D0COPY, True))
        results.append(run_condition("C2a-COLD-FRESHCOPY", scratch, False))
        results.append(run_condition("C2b-PRELOAD-FRESHCOPY", scratch, True))
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
        gate("G6b scratch copy deleted by the run that made it",
             deleted and not os.path.exists(scratch), os.path.basename(scratch))

    m_orig1 = md5(ORIG)
    fact("md5 ORIGINAL AFTER    %s" % m_orig1)
    gate("G6a ORIGINAL md5 UNCHANGED", m_orig1 == m_orig0, "%s -> %s" % (m_orig0, m_orig1))

    print("\n=== SUMMARY TABLE", flush=True)
    for r in results:
        print("  %-24s preload=%-5s ExecState=%-10r VI.Name=%r"
              % (r["tag"], r["preload"], r.get("execstate"), r.get("name")), flush=True)
    es = {r["tag"]: r.get("execstate") for r in results}
    fact("D0 copy    : cold %r vs preloaded %r -> %s"
         % (es.get("C1a-COLD-D0COPY"), es.get("C1b-PRELOAD-D0COPY"),
            "IDENTICAL" if es.get("C1a-COLD-D0COPY") == es.get("C1b-PRELOAD-D0COPY") else "DIFFERENT"))
    fact("fresh copy : cold %r vs preloaded %r -> %s"
         % (es.get("C2a-COLD-FRESHCOPY"), es.get("C2b-PRELOAD-FRESHCOPY"),
            "IDENTICAL" if es.get("C2a-COLD-FRESHCOPY") == es.get("C2b-PRELOAD-FRESHCOPY") else "DIFFERENT"))
    fact("C3(i) `Wire.Is Broken?` 6371004 NOT RUN - the only built readout fires after a `Terminal.Connect Wire` "
         "(a WRITE) and docs/NAMES.md:898-909 measured that it perturbs the target; a held-terminal reader is "
         "'NOT BUILT' (docs/toolkit-capabilities.md:68). Not performable in a read-only dispatch.")

    with open(os.path.join(HERE, "d0_execstate_preload.json"), "w", encoding="utf-8") as f:
        json.dump({"orig_md5_before": m_orig0, "orig_md5_after": m_orig1, "d0_copy_md5": m_copy,
                   "results": results}, f, indent=1, default=str)
    print("\n=== GATES %d pass / %d fail" % (len(PASS), len(FAIL)), flush=True)
    for x in FAIL:
        print("  FAILING: " + x, flush=True)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        sys.exit(child(sys.argv[2], sys.argv[3], sys.argv[4] == "1"))
    sys.exit(main())
