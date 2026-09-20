r"""diag_filewrite_donor.py - READ-ONLY census of candidate DONORS for the D1 streaming TSV write (plan s7.1).

    MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/diag_filewrite_donor.log \
        -- py -u tools/bench/diag_filewrite_donor.py

WHAT ALREADY EXISTS - checked before this file was written (CLAUDE.md "before creating any new op/tool/recipe"):
  * `docs/toolkit-capabilities.md` row 39: `copy_by_index(donor, cls, index, target, expect_uid, finish)` =
    `OpMoveByIndex_v0` - "copies ANY object - built-in primitives included - from a donor by Traverse class+index
    with a UID guard". This is the route; nothing new is needed to COPY. What is missing is the DONOR, and that
    is what this file measures.
  * `g.drop_subvi(target, path, diagram, loc)` places a subVI CALL - so any file operation that ships as a .vi
    (not as a primitive) needs no copy and no new op at all.
  * `tools/bench/main_vi_node_labels.json` - the main VI holds `Write to Binary File` but NO text open/write/close
    chain (measured by grep, 2026-09-17).
  * `vi.lib\Erdos Miller\LV-Scripting` (85 entries, listed 2026-09-17) has NO file-I/O creator at all.
  * `tools/recipes/build_d1_v0.py:48-50` asserted "no donor in this project holds an open/write/close chain";
    `archive/peer/2026-09-17-priorart-priorart-d1-build-rev4c.md` item 4 says that assertion was made without
    consulting any census. This file IS that census.

PREDICTION CONTRACT (what a machine checks):
  D1  the NI example `examples\File IO\Text (ASCII)\Write to Text File and Read from Text File.vi` exists on disk.
  D2  a COPY of it under claudeDev opens and reports ExecState 1 (the original is never opened for writing -
      rule 1; every read below is against the COPY).
  D3  its top-level diagram's node labels contain, by label, a file OPEN, a TEXT WRITE and a CLOSE.
  D4  each of the three is located by Traverse CLASS + INDEX, which is what `copy_by_index` addresses.
  D5  the vi.lib subVI route is checked in parallel: `Open File+.vi`, `Close File+.vi`,
      `Write File+ (string).vi`, `Write Characters To File.vi` exist in `vi.lib\Utility\file.llb` -> if the three
      duties can be discharged by subVI CALLS, `drop_subvi` covers it and NO op and NO copy is needed.
  D6  the scratch copy is DELETED in the same run.
Read-only on every original. No hardware. No GUI.
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

LV = r"C:\Program Files\National Instruments\LabVIEW 2026"
EXAMPLE = os.path.join(LV, "examples", "File IO", "Text (ASCII)",
                       "Write to Text File and Read from Text File.vi")
FILELLB = os.path.join(LV, "vi.lib", "Utility", "file.llb")
SUBVI_CANDIDATES = ["Open File+.vi", "Close File+.vi", "Write File+ (string).vi", "Write Characters To File.vi"]
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_filewrite_donor_{STAMP}.vi")

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None

    gate("D1 the NI text-file example exists", os.path.exists(EXAMPLE), EXAMPLE)

    print("\n=== D5: the subVI route (no copy, no new op - drop_subvi covers a .vi)", flush=True)
    for nm in SUBVI_CANDIDATES:
        p = os.path.join(FILELLB, nm)
        gate(f"D5 {nm}", os.path.exists(p), p)

    if not os.path.exists(EXAMPLE):
        return 1

    print("\n=== D2/D3/D4: a COPY of the example, censused read-only", flush=True)
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(EXAMPLE, SCRATCH)
    try:
        g.open_panel(SCRATCH)
        es = g.exec_state(SCRATCH)
        gate("D2 the copy opens and is runnable", es == 1, f"ExecState {es}")
        for cls in ("Node", "SubVI", "Diagram", "Constant", "Wire", "ControlTerminal"):
            try:
                print(f"  COUNT {cls:16s} {g.count(SCRATCH, cls)}", flush=True)
            except Exception as e:
                print(f"  COUNT {cls:16s} <{str(e)[:60]}>", flush=True)
        # RUN 1 read `node_labels(SCRATCH, 0)` only and saw 5 of the VI's 19 nodes: the file chain lives INSIDE
        # the example's Case Structure (uid 221), on its FRAME diagrams. `Diagram` count is 6, so every diagram
        # is walked. (`report_all('Node')` is whole-VI and already returned all 19 - that is the index space
        # `copy_by_index` addresses.)
        labels = []
        ndiag = g.count(SCRATCH, "Diagram")
        for di in range(ndiag):
            try:
                rows = g.node_labels(SCRATCH, di)
            except Exception as e:
                print(f"  node_labels({di}) failed: {str(e)[:100]}", flush=True)
                continue
            for r in rows:
                r = dict(r)
                r["diagram_i"] = di
                labels.append(r)
        for r in labels:
            print(f"  NODE  d{r.get('diagram_i')}  uid {r.get('uid')}  label {r.get('label')!r}", flush=True)
        txt = " | ".join(str(r.get("label")) for r in labels).lower()
        gate("D3a a file OPEN node is on the example's diagram", "open" in txt, txt[:200])
        gate("D3b a TEXT WRITE node is on the example's diagram", "write" in txt, txt[:200])
        gate("D3c a CLOSE node is on the example's diagram", "close" in txt, txt[:200])
        print("\n=== D4: Traverse class+index for copy_by_index", flush=True)
        for cls in ("SubVI", "Node"):
            try:
                rows = g.report_all(SCRATCH, cls)
            except Exception as e:
                print(f"  report_all({cls}) failed: {str(e)[:100]}", flush=True)
                continue
            for i, o in enumerate(rows):
                print(f"  {cls}[{i}] uid {o.get('uid')} pos {o.get('pos')}", flush=True)
        try:
            for i, o in enumerate(g.subvis(SCRATCH, 0)):
                print(f"  SUBVI-CALL[{i}] uid {o.get('uid')} name {o.get('name')!r} path {o.get('path')!r}",
                      flush=True)
        except Exception as e:
            print(f"  subvis(0) failed: {str(e)[:120]}", flush=True)
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception:
            pass
        try:
            os.remove(SCRATCH)
            gate("D6 scratch copy deleted in the same run", True, SCRATCH)
        except Exception as e:
            gate("D6 scratch copy deleted in the same run", False, str(e)[:100])
        g._lv = None

    print(f"\n=== diag_filewrite_donor: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
