r"""diag_savetrace_376.py - READ-ONLY census of `save trace.vi` (the main VI's `#376`), to answer the ONE
question the streaming-write prior-art review says must be answered before §7.1 is built at all.

    MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/diag_savetrace_376.log \
        -- py -u tools/bench/diag_savetrace_376.py

THE QUESTION (`archive/peer/2026-09-17-priorart-d1-op-streamwrite.md` A5 `contradicted`):
  `docs/d1-build-plan.md` §7.1 says the writer must stream "because the original saves once at the end", citing
  `archive/prose/2026-09-17-d1-d2-explained-r2.md:114` - a document THIS PROJECT WROTE. Meanwhile `#376`'s own
  terminals, measured twice (`d1_step0_census.json`; run 4's cut list), include
      t3 `file progress`   t4 `file number to append out`   t8 `saved file refnum`   t9 `file size`
  i.e. the vocabulary of a VI that keeps a file OPEN and APPENDS. **If `#376` already appends per frame, §7.1's
  separate TSV is a second artefact with no sourced requirement.** A5's words: it "can delete the work".

WHAT ALREADY EXISTS - checked before this file was written:
  * `tools/bench/diag_filewrite_donor.py` (this session) - the same shape, for the NI example; its run-1 defect
    (`node_labels(0)` sees the TOP-LEVEL diagram only, so nodes inside a Case are invisible) is fixed here from
    the start: every diagram is walked.
  * `tools/recipes/build_strtopath.py` already opens `save N xyz traces.vi` and copies uid 160 out of it, so a
    background VI being READ is established practice - but rule 1 still says never modify an original, so this
    censuses a COPY under claudeDev and deletes it in the same run.
  * `g.node_labels`, `g.report_all`, `g.count`, `g.subvis`, `g.node_terms_uid` - built readers.
  * `docs/main-vi-stop-and-save.md` §2 already measures `#6384 save N xyz traces.vi`; it does NOT census `#376`.

PREDICTION CONTRACT:
  V1 `save trace.vi` is on disk; its md5 is recorded BEFORE and AFTER (rule 1 - it is an original).
  V2 a COPY under claudeDev opens; ExecState reported (not gated - a background VI may read 0 headlessly).
  V3 every diagram is walked and every node label printed. The question is answered by the LABELS:
       `Open/Create/Replace File` / `Open File+` present  => it opens a file itself
       `Write to Text File` / `Write File+` / `Write Characters To File` present => it writes text
       `Close File` present                              => it closes
     and by whether `saved file refnum` is CARRIED THROUGH (an input AND an output) rather than opened/closed
     inside - which is what "the caller keeps the file open across calls" looks like.
  V4 the connector-pane terminal list is printed with directions, so `saved file refnum`'s direction is read,
     never inferred.
  V5 the scratch copy is deleted in the same run; the original's md5 is unchanged.
THIS FILE TAKES NO DECISION. The plan change that follows from the answer is judgement (CLAUDE.md §3).
"""
import hashlib
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

# ROOT = ...\AAA_UNIST\2. Tracking\V6_ParallelLoop -> three levels up is ...\zz_LabView VI
VI_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))
SAVETRACE = os.path.join(VI_ROOT, "background VIs", "save trace.vi")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_savetrace_{STAMP}.vi")
KEYS = ["Open/Create/Replace File", "Open File", "Write to Text File", "Write File", "Write Characters",
        "Close File", "Write to Binary File", "Write Delimited", "Format Into String", "Array To Spreadsheet"]

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    if not gate("V1a save trace.vi on disk", os.path.exists(SAVETRACE), SAVETRACE):
        return 1
    m0 = md5(SAVETRACE)
    print(f"  FACT  original md5 BEFORE: {m0}", flush=True)
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(SAVETRACE, SCRATCH)
    labels = []
    try:
        g.open_panel(SCRATCH)
        print(f"  FACT  ExecState of the copy: {g.exec_state(SCRATCH)} (not gated)", flush=True)
        for cls in ("Node", "SubVI", "Diagram", "Wire", "Constant", "ControlTerminal", "Local", "WhileLoop",
                    "ForLoop", "CaseStructure"):
            try:
                print(f"  COUNT {cls:16s} {g.count(SCRATCH, cls)}", flush=True)
            except Exception as e:
                print(f"  COUNT {cls:16s} <{str(e)[:50]}>", flush=True)
        nd = g.count(SCRATCH, "Diagram")
        for di in range(nd):
            try:
                rows = g.node_labels(SCRATCH, di)
            except Exception as e:
                print(f"  node_labels({di}) failed: {str(e)[:90]}", flush=True)
                continue
            for r in rows:
                labels.append((di, r.get("uid"), r.get("label")))
                print(f"  NODE  d{di}  uid {r.get('uid')}  label {r.get('label')!r}", flush=True)
        txt = " | ".join(str(l) for _d, _u, l in labels)
        print("\n=== V3: the answer, by label", flush=True)
        for k in KEYS:
            print(f"  {'YES' if k.lower() in txt.lower() else 'no ':3s}  {k}", flush=True)
        gate("V3 the census returned node labels", bool(labels), f"{len(labels)} nodes over {nd} diagrams")
        print("\n=== V4: subVI calls", flush=True)
        for di in range(nd):
            try:
                for o in g.subvis(SCRATCH, di):
                    print(f"  SUBVI d{di} uid {o.get('uid')} name {o.get('name')!r}", flush=True)
            except Exception:
                pass
        print("\n=== V4b: panel objects (the pane's own vocabulary)", flush=True)
        try:
            for i, lbl, ind in g.fp_labels(SCRATCH):
                print(f"  FP[{i}] {'IND' if ind else 'CTL'} {lbl!r}", flush=True)
        except Exception as e:
            print(f"  fp_labels failed: {str(e)[:120]}", flush=True)
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception:
            pass
        try:
            os.remove(SCRATCH)
            gate("V5 scratch copy deleted in the same run", True, SCRATCH)
        except Exception as e:
            gate("V5 scratch copy deleted in the same run", False, str(e)[:100])
        m1 = md5(SAVETRACE) if os.path.exists(SAVETRACE) else "<missing>"
        gate("V1b original md5 UNCHANGED after", m1 == m0, f"{m0} -> {m1}")
        g._lv = None
    print(f"\n=== diag_savetrace_376: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
