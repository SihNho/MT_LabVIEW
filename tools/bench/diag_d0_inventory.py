r"""diag_d0_inventory.py - CYCLE 30 dispatch 2: what a D0 unattended run has to touch, MEASURED.

READ-ONLY. No VI is RUN (only op VIs, which touch no instrument), no motor, no camera, no GUI click.
Rule 1: the ORIGINAL is preloaded read-only with the `tools/bench/p2_open_copy.py` pattern and md5'd
before AND after. Handle count read before and after (bench_prep.labview_handles).

PRIOR ART CHECKED BEFORE WRITING (CLAUDE.md "before creating any new op/tool/recipe"):
  - `gscript.panel_wiring()` (OpPanelWiring_v0, gscript.py:772) already returns label / indicator / uid /
    terminal wire for every TOP-LEVEL panel object in ONE op run. Reused - nothing new built.
  - `gscript.report_all()` (OpReportAll_v0, gscript.py:434) returns class / uid / pos / owner per object of a
    traverse class in ONE run. Reused to try to reach per-object CLASS and POSITION.
  - `docs/main-vi-panel-map.md` already has all 114 labels + CTL/IND + uid (2026-09-14) - but NO class and NO
    bounds, and it was measured on the WORKING COPY, not on Track_D0_copy_20260918.vi. That is the gap here.
  - `tools/bench/autofocus_panel.json` holds the same 114 rows with wires. Same gap.
  - NO op in `docs/toolkit-capabilities.md` reads `GObject.Bounds`. Width/height may therefore be unreachable;
    this run MEASURES whether Position at least is, and says so either way rather than inferring.
  - (d) is answered OFFLINE from `tools/bench/main_vi_nodeterms.json` (every diagram's nodes+terminals+wires,
    2026-09-14) - no COM call is spent on it.

PREDICTION CONTRACT
  P1 panel_wiring(D0 copy) returns 114 rows, 60 controls / 54 indicators
     (tools/bench/test_oppanelwiring.log, main VI).
  P2 uid 11819 is present, label 'Done Picking \nBeads?', indicator FALSE (a CONTROL)
     (docs/main-vi-panel-map.md:359).
  P3 uid 31543 is present, label 'Image', indicator TRUE (docs/main-vi-panel-map.md:292).
  P4 'GObject' is a valid traverse class (docs/toolkit-capabilities.md:286). Whether its members include
     FRONT-PANEL objects is UNKNOWN and is the discriminating test: does uid 31543 appear in
     report_all(copy,'GObject')? Either answer is a measurement.
  P5 md5 of the ORIGINAL identical before and after.
  P6 offline: exactly one node in main_vi_nodeterms.json carries a terminal named 'base path/filename'.

  py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_d0_inventory.log -- py -u tools/bench/diag_d0_inventory.py
"""
import hashlib
import json
import os
import sys
import traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g            # noqa: E402
from bench_prep import labview_handles  # noqa: E402

ORIG = (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
        r"\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
COPY = (r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
        r"\Track_D0_copy_20260918.vi")
NODETERMS = os.path.join(HERE, "main_vi_nodeterms.json")
OUT = os.path.join(HERE, "d0_inventory.json")

g._run.__defaults__ = (6.0, 420.0)          # the main VI is big; 180 s is too tight for a 10k traverse

PASS = []


def gate(label, ok, detail=""):
    PASS.append((label, bool(ok)))
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"   {'PASS' if ok else 'FAIL'} {label}{(' - ' + detail) if detail else ''}", flush=True)
    return ok


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


# ------------------------------------------------------------------ (d) OFFLINE: the trace file and its name
def offline_trace_evidence(out):
    print("\n=== (d) TRACE OUTPUT - offline from main_vi_nodeterms.json (no COM) ===", flush=True)
    if not os.path.exists(NODETERMS):
        print("   census file missing; (d) not answerable offline", flush=True)
        out["d_error"] = "main_vi_nodeterms.json missing"
        return
    with open(NODETERMS, encoding="utf-8") as f:
        nt = json.load(f)
    # every (diagram, node, terminal) row, flattened once
    rows = []
    for dk, dv in nt.get("diagrams", {}).items():
        for n in dv.get("nodes", []):
            for t in n.get("terms", []):
                rows.append((dk, dv.get("owner", ""), n.get("uid"), t.get("i"), t.get("name") or "",
                             bool(t.get("is_source")), int(t.get("wire") or 0)))
    print(f"   {len(rows)} terminal rows over {len(nt.get('diagrams', {}))} diagrams", flush=True)

    def find(*needles):
        nl = [s.lower() for s in needles]
        return [r for r in rows if any(s in r[4].lower() for s in nl)]

    groups = {
        "base path/filename (save trace / save N xyz traces input)": find("base path/filename"),
        "file # to append": find("file # to append"),
        "selected path (save trace output = the actual .tra path)": find("selected path"),
        "cal cluster path": find("cal cluster path"),
        "File Dialog terminals (start path / default name / selected path?)":
            find("start path", "default name", "selected paths", "prompt"),
        "Build Path terminals": find("name or relative path", "appended path"),
        "Strip / Path-To-String": find("stripped path", "stripped filename"),
    }
    d = {}
    for title, hits in groups.items():
        print(f"\n   -- {title}: {len(hits)} row(s)", flush=True)
        for (dk, owner, uid, i, name, src, wire) in hits[:14]:
            print(f"      diagram {dk:>4} ({owner:<20.20}) node uid {uid:<7} term[{i}] {name!r:<28} "
                  f"{'SRC' if src else 'sink'} wire {wire}", flush=True)
        d[title] = [{"diagram": dk, "diagram_owner": owner, "node_uid": uid, "term": i, "name": name,
                     "is_source": src, "wire": wire} for (dk, owner, uid, i, name, src, wire) in hits]
    out["d_trace"] = d

    # who DRIVES the base path wire - offline, by scanning every row on the same wire
    bp = groups["base path/filename (save trace / save N xyz traces input)"]
    gate("P6 exactly one 'base path/filename' terminal in the census", len(bp) == 1,
         f"found {len(bp)}")
    out["d_basepath_sources"] = []
    for (dk, owner, uid, i, name, src, wire) in bp:
        if not wire:
            print(f"      node {uid} term[{i}] 'base path/filename' is BARE (wire 0)", flush=True)
            continue
        same = [r for r in rows if r[6] == wire]
        print(f"\n   -- who drives wire {wire} (the base path)? {len(same)} terminal(s) on it:", flush=True)
        for (dk2, ow2, uid2, i2, nm2, src2, w2) in same:
            print(f"      diagram {dk2:>4} ({ow2:<20.20}) node uid {uid2:<7} term[{i2}] {nm2!r:<28} "
                  f"{'SRC' if src2 else 'sink'}", flush=True)
            out["d_basepath_sources"].append({"diagram": dk2, "owner": ow2, "node_uid": uid2, "term": i2,
                                              "name": nm2, "is_source": src2, "wire": w2})
        print("   NOTE: a wire with no SRC row here is fed by a NON-node GObject (a control terminal, a "
              "constant, a tunnel) - those are not in this node census.", flush=True)


# ------------------------------------------------------------------ (b) COM: the panel inventory
WANT = {
    "image display the picks land on": lambda r: (r["label"] or "").strip().lower() == "image",
    "Done Picking Beads? (uid 11819)": lambda r: r["uid"] == 11819,
    "save path control(s)": lambda r: "path" in (r["label"] or "").lower(),
    "save name control(s)": lambda r: any(k in (r["label"] or "").lower()
                                          for k in ("file name", "filename", "name or", "file #", "file name?")),
    "experiment-loop stop control": lambda r: (r["label"] or "").lower().startswith("stop"),
    "panel parameters on the picking/calibration path": lambda r: any(
        k in (r["label"] or "").lower() for k in
        ("cross length", "pixel distance", "z step", "# to avg", "# images in stack",
         "fix to a certain pattern", "frame rate", "roi", "bandpass", "radius")),
}


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    out = {"orig": ORIG, "copy": COPY}
    out["md5_orig_before"] = md5(ORIG)
    print(f"md5 ORIGINAL BEFORE {out['md5_orig_before']}", flush=True)
    out["handles_before"] = labview_handles()
    print(f"LabVIEW handles BEFORE {out['handles_before']} (None = not running yet)", flush=True)

    offline_trace_evidence(out)

    try:
        print("\n=== (b) PANEL INVENTORY of the D0 copy (read-only COM) ===", flush=True)
        app = g.lv()
        print(f"   LabVIEW {app.Version}", flush=True)
        vi_orig = app.GetVIReference(ORIG, "", False, 0)     # preload read-only: subVIs resident by name
        st_orig = int(vi_orig.ExecState)
        print(f"   original resident, ExecState {st_orig}", flush=True)
        out["handles_after_open"] = labview_handles()
        vi_copy = app.GetVIReference(COPY, "", False, 0)
        st_copy = int(vi_copy.ExecState)
        print(f"   D0 copy loaded, ExecState {st_copy} (1 = idle/runnable, 0 = broken)", flush=True)
        out["execstate_orig"], out["execstate_copy"] = st_orig, st_copy
        gate("B0 D0 copy is runnable (ExecState 1)", st_copy == 1, f"ExecState {st_copy}")

        rows = g.panel_wiring(COPY)
        nc = sum(1 for r in rows if not r["indicator"])
        ni = sum(1 for r in rows if r["indicator"])
        out["panel_rows"] = rows
        out["panel_counts"] = {"rows": len(rows), "controls": nc, "indicators": ni}
        gate("P1 114 rows / 60 CTL / 54 IND", (len(rows), nc, ni) == (114, 60, 54),
             f"{len(rows)} rows, {nc} CTL, {ni} IND")
        by_uid = {r["uid"]: r for r in rows}
        r = by_uid.get(11819)
        gate("P2 uid 11819 = 'Done Picking \\nBeads?' CONTROL", bool(r) and not r["indicator"],
             repr(r))
        r = by_uid.get(31543)
        gate("P3 uid 31543 = 'Image', indicator", bool(r) and r["indicator"], repr(r))

        # ---- class + position: which traverse class, if any, reaches PANEL objects
        print("\n   -- traverse-class probe (does any class reach the front panel?)", flush=True)
        probe = {}
        for cls in ("Control", "Panel", "GObject", "ControlTerminal", "Boolean", "Path", "Numeric"):
            try:
                probe[cls] = {"count": int(g.count(COPY, cls))}
                print(f"      count({cls!r}) = {probe[cls]['count']}", flush=True)
            except Exception as e:
                probe[cls] = {"error": str(e)[:120]}
                print(f"      count({cls!r}) FAILED {str(e)[:110]}", flush=True)
        out["class_probe"] = probe

        panel_uids = set(by_uid)
        best = None
        for cls in ("Control", "GObject"):
            if "count" not in probe.get(cls, {}):
                continue
            try:
                objs = g.report_all(COPY, cls)
            except Exception as e:
                print(f"      report_all({cls!r}) FAILED {str(e)[:110]}", flush=True)
                out.setdefault("report_all_errors", {})[cls] = str(e)[:200]
                continue
            hit = [o for o in objs if o["uid"] in panel_uids]
            print(f"      report_all({cls!r}) = {len(objs)} objects, {len(hit)} of them are PANEL uids", flush=True)
            out.setdefault("report_all", {})[cls] = {"total": len(objs), "panel_hits": len(hit)}
            if hit and (best is None or len(hit) > best[1]):
                best = (cls, len(hit), {o["uid"]: o for o in hit})
        gate("B1 a traverse class reaches panel objects (class + position measurable)", best is not None,
             f"{best[0]} covers {best[1]}/{len(panel_uids)}" if best else
             "no traverse class returned any panel uid - class/position NOT reachable by an existing op")
        cls_pos = best[2] if best else {}
        out["panel_class_source"] = best[0] if best else None

        # ---- the table
        print("\n   -- INVENTORY (label | CTL/IND | uid | class | pos | terminal wire)", flush=True)
        table = []
        for rr in rows:
            o = cls_pos.get(rr["uid"], {})
            row = {"label": rr["label"], "kind": "IND" if rr["indicator"] else "CTL", "uid": rr["uid"],
                   "class": o.get("class"), "pos": o.get("pos"), "wire": rr["wire"],
                   "is_source": rr["is_source"]}
            table.append(row)
        out["table"] = table
        for row in table:
            print(f"      {row['label']!r:<40} {row['kind']} uid {row['uid']:<7} "
                  f"class {str(row['class']):<22.22} pos {str(row['pos']):<16} wire {row['wire']}", flush=True)

        print("\n   -- the five things the brief asks for, by name", flush=True)
        found = {}
        for want, pred in WANT.items():
            hits = [row for row in table if pred({"label": row["label"], "uid": row["uid"]})]
            found[want] = hits
            print(f"\n      == {want}: {len(hits)} hit(s)", flush=True)
            for row in hits:
                print(f"         {row['label']!r:<40} {row['kind']} uid {row['uid']:<7} "
                      f"class {str(row['class']):<22.22} pos {row['pos']} wire {row['wire']} "
                      f"src={row['is_source']}", flush=True)
            if not hits:
                print("         NOT FOUND on the top-level panel - reported as not found, not inferred away",
                      flush=True)
        out["found"] = {k: v for k, v in found.items()}
        gate("B2 every one of the 6 wanted groups has at least one hit",
             all(found[k] for k in WANT), ", ".join(k for k in WANT if not found[k]) or "all present")
    except Exception:
        traceback.print_exc()
        gate("B9 no exception", False)
    finally:
        try:
            g.reset()          # drops the Application proxy AND every cached op-VI reference
        except Exception:
            pass
        out["handles_after"] = labview_handles()
        out["md5_orig_after"] = md5(ORIG)
        gate("P5 ORIGINAL md5 unchanged", out["md5_orig_after"] == out["md5_orig_before"],
             f"{out['md5_orig_before']} -> {out['md5_orig_after']}")
        print(f"\nmd5 ORIGINAL AFTER  {out['md5_orig_after']}", flush=True)
        print(f"LabVIEW handles AFTER {out['handles_after']} (before {out['handles_before']})", flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"wrote {OUT}", flush=True)
    npass = sum(1 for _, ok in PASS if ok)
    print(f"\n=== GATES {npass} pass / {len(PASS) - npass} fail ===", flush=True)
    for lab, ok in PASS:
        if not ok:
            print(f"    FAILING: {lab}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
