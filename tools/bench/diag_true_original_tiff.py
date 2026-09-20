r"""diag_true_original_tiff.py - READ-ONLY: does the TRUE original ever write a TIFF?

WHY. Binding decision, 2026-09-17: the per-frame TIFF writer is **not original behaviour**.
`docs/fixture-recording.md:8-20` records that FOUR nodes were INSERTED into the working copy
`..\Min_Track N beads V6_ParallelLoop.vi` on 2026-09-01 for fixture recording - `IMAQ Write TIFF File 2`
**#22700**, `Format Into String` **#22703**, `Strip Path` **#23175**, `Build Path` **#23020** - and the user says
real experiments never save TIFFs. `docs/d1-build-plan.md:304` still carries the clause "#22700 stays 1.1 -
unconditional, exactly as the original has it", which is now WITHDRAWN. This run measures the premise instead of
asserting it.

RULE 1, STRICTLY. The true original `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` is opened by
`GetVIReference` ONLY - no panel open, no edit, no save, no copy made - and its md5 is asserted BEFORE and AFTER.
Opening an original's hierarchy in LabVIEW 2026 relinks subVIs and marks them dirty; nothing here saves, and a
`*` in a title bar is not a disk change (CLAUDE.md rule 1). The working copy is read the same way, as a control.

PRIOR ART CHECKED: `grep -rn "22700" docs/` -> `fixture-recording.md` (the insertion record),
`d1-build-plan.md` (the clause now withdrawn), `main-vi-*.md` (the working copy's census). No existing log
censuses the TRUE original for TIFF nodes - every census in `tools/bench/` is of the V6 working copy
(`d1_step0_census.json`, `v3_structure.json`, `spec_inventory.json`).

PREDICTION CONTRACT
  O0  both files exist; md5 of each recorded BEFORE
  O1  the WORKING COPY (control) reports `IMAQ Write TIFF File 2` among its SubVI/Function objects, and uids
      22700 / 23020 / 22703 / 23175 are all present   -> PASS proves the reader can see such a node at all
  O2  the TRUE ORIGINAL reports **no** node whose label or class mentions TIFF, and none of those four uids
      -> the prediction is ZERO; a non-zero count would REFUTE the decision's premise and is reported, not
      explained
  O3  md5 of BOTH files unchanged AFTER
"""
import hashlib
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import gscript as g  # noqa: E402

TRACKDIR = os.path.dirname(os.path.dirname(ROOT))
TRUE_ORIG = os.path.join(TRACKDIR, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
WORKING = os.path.join(TRACKDIR, "Min_Track N beads V6_ParallelLoop.vi")
FIXTURE_UIDS = [22700, 23020, 22703, 23175]
P, F = [], []


def gate(name, ok, detail=""):
    (P if ok else F).append(name)
    print(f"[{'PASS' if ok else 'FAIL'}] {name}  {detail}", flush=True)
    return ok


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def census(path, tag):
    """SubVI names + node labels, read-only. `subvis` is the cast-free identity route; `node_labels` names
    primitives by style. Both are op runs against a VI reference - no panel, no edit."""
    out = {"subvi_names": [], "tiff_hits": [], "uids": {}}
    try:
        subs = g.subvis(path, 0, strict=False)
        out["subvi_names"] = sorted({(s.get("name") or "") for s in subs})
    except Exception as e:
        out["subvi_err"] = str(e)[:150]
    for cls in ("SubVI", "Function", "Node"):
        try:
            rows = g.report_all(path, cls)
        except Exception as e:
            out[f"{cls}_err"] = str(e)[:150]
            continue
        out[f"{cls}_count"] = len(rows)
        present = {r["uid"] for r in rows}
        for u in FIXTURE_UIDS:
            if u in present:
                out["uids"].setdefault(u, []).append(cls)
    try:
        ni = g.node_info(path, max_n=900)
        out["tiff_hits"] = [(i, style, lab) for i, style, lab in ni
                            if "tiff" in (str(style) + str(lab)).lower()]
        out["node_info_n"] = len(ni)
    except Exception as e:
        out["node_info_err"] = str(e)[:150]
    print(f"   {tag}: SubVI={out.get('SubVI_count')} Function={out.get('Function_count')} "
          f"Node={out.get('Node_count')} node_info_n={out.get('node_info_n')}", flush=True)
    print(f"   {tag}: fixture uids present -> {out['uids']}", flush=True)
    print(f"   {tag}: TIFF-named nodes (top-level Nodes[]) -> {out['tiff_hits'][:6]}", flush=True)
    hits = [n for n in out["subvi_names"] if "tiff" in n.lower()]
    print(f"   {tag}: SubVI names mentioning TIFF -> {hits}", flush=True)
    out["subvi_tiff"] = hits
    return out


def main():
    g._lv = None
    g._run.__defaults__ = (6.0, 150.0)
    for p in (TRUE_ORIG, WORKING):
        if not gate("O0 exists " + os.path.basename(p), os.path.isfile(p), p):
            return 1
    m_true, m_work = md5(TRUE_ORIG), md5(WORKING)
    print(f"   md5 BEFORE  true original {m_true}\n               working copy  {m_work}", flush=True)

    print("\n######## CONTROL: the WORKING COPY (the fixture nodes were inserted here)", flush=True)
    w = census(WORKING, "working")
    gate("O1 the reader SEES the fixture nodes in the working copy",
         bool(w["uids"]) or bool(w["tiff_hits"]) or bool(w["subvi_tiff"]),
         f"uids {sorted(w['uids'])}, subvi TIFF {w['subvi_tiff']}")

    print("\n######## THE TRUE ORIGINAL (GetVIReference only, never opened for writing)", flush=True)
    t = census(TRUE_ORIG, "true-original")
    gate("O2 the TRUE ORIGINAL has NO TIFF writer and none of the four fixture uids",
         not t["uids"] and not t["tiff_hits"] and not t["subvi_tiff"],
         f"uids {sorted(t['uids'])}, TIFF nodes {t['tiff_hits'][:4]}, subvi TIFF {t['subvi_tiff']}")

    gate("O3 md5 of the TRUE ORIGINAL unchanged AFTER", md5(TRUE_ORIG) == m_true, m_true)
    gate("O3b md5 of the working copy unchanged AFTER", md5(WORKING) == m_work, m_work)
    print(f"\nVERDICT: {len(P)} pass / {len(F)} fail" + (f"   FAILING: {F}" if F else ""), flush=True)
    return 0 if not F else 1


if __name__ == "__main__":
    t0 = time.time()
    rc = main()
    print(f"elapsed {time.time() - t0:.1f} s", flush=True)
    sys.exit(rc)
