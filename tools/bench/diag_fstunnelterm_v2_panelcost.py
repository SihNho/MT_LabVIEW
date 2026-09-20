"""diag_fstunnelterm_v2_panelcost.py - STAGE 3 of the cycle-24 firefighter chain (2026-09-18).

WHAT IT MEASURES, in one sentence: on the op(s) `tools/recipes/build_opfstunnelterm_v2.py` actually BUILT (never a
fresh donor copy), the PANEL cost of the A0h RBW repair - every front-panel object's label, uid and whether its
block-diagram terminal still carries a wire, with `error out 3` (#825) and `index 2` (#1334) called out by name and
every connector-pane-assigned panel object that is unwired listed.

MEASUREMENT ONLY. It rewires nothing, deletes nothing, saves nothing, and opens no original.

ALREADY-EXISTS CHECK (CLAUDE.md: check before creating anything new)
  * `grep "^def " tools/gscript.py` HAS the two readers this needs, both built and functionally verified:
    - `gscript.panel_wiring(target)` (2026-09-14, `tools/gscript.py:772-802`) -> [{label, indicator, uid,
      is_source, wire, term_err, wire_err}] for every TOP-LEVEL panel object; `wire` == 0 means the terminal is
      bare. Verified `tools/bench/test_oppanelwiring.log` 11/11.
    - `gscript.conpane(target)` (2026-09-10, `tools/gscript.py:2679-2703`) -> {terminal index: control label},
      None for a FREE terminal.
    NO NEW OP, NO NEW TOOL, NO NEW PROCESS DEVICE IS BUILT (user's standing order 2026-09-18 08:53).
  * `tools/bench/diag_fstunnel_preclean_twins.py` - `md5()`, `handles()`, `WATCHED`, `ORIGINALS` IMPORTED, not
    re-implemented.
  * `tools/bench/diag_fstunnel_wireterms_panel.py` already read the PANEL side on a SCRATCH copy at
    `_v1.py:403` (`…_panel_run2.log:36-51`). This file is the same question asked of the FINISHED op AFTER the
    RBW repair - a different object and a different point in time, so it is not a repeat.

PREDICTION CONTRACT (every line prints PASS/FAIL; a miss is a RESULT, not a failure)
  P1  at least one of `OpFsTunnelTerm_v0.vi` / `OpFsInnerTunnelTerm_v0.vi` exists on disk (stage 2 built it).
  P2  `panel_wiring` returns >= 30 top-level rows for each built op (the donor's own census was 38 rows / 29
      wired - `…_panel_run2.log:33`).
  P3  uid 825 (`error out 3`) is present in the census of each built op and its `wire` is 0 (UNWIRED) - the A0h
      repair removed #894, whose other terminal was that indicator (`…_panel_run2.log:36-41`).
  P4  uid 1334 (`index 2`) is present and its `wire` is 0 (UNWIRED) - #1356's panel end
      (`…_panel_run2.log:44-50`).
  P5  `conpane` is read for each built op and every conpane-assigned label is matched to a census row by label.
  P6  no original is opened and all `WATCHED` files (originals + the V6 copy + the donor) are md5-identical
      BEFORE and AFTER.
  P7  no motor, no serial port, no camera; `motor_gate.py --execute` not called (static: this file imports
      neither `serial` nor `motor_gate` and calls no `.ps1`).
  P8  every VI Server reference this file opens is closed by `gscript`'s own op wrappers; the LabVIEW handle
      count is printed BEFORE and AFTER.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                                   # noqa: E402
import diag_fstunnel_preclean_twins as TW                             # noqa: E402  helpers only

OPS = [os.path.join(g.CLAUDEDEV, "OpFsTunnelTerm_v0.vi"),
       os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")]
CALLOUT = {825: "error out 3", 1334: "index 2"}
OUT = os.path.join(HERE, "diag_fstunnelterm_v2_panelcost.json")
RES = {"gates": [], "ops": {}, "md5": {}, "handles": {}}


def must(label, ok, detail=""):
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": detail})
    print(f"  {'PASS' if ok else '-> FAIL'} {label}" + (f"  | {detail}" if detail else ""), flush=True)
    return bool(ok)


def report(path):
    name = os.path.basename(path)
    print(f"\n================ {name} ================", flush=True)
    d = {"path": path, "exists": os.path.exists(path)}
    RES["ops"][name] = d
    if not d["exists"]:
        print("   NOT ON DISK - stage 2 did not build it", flush=True)
        return d
    g.open_panel(path)
    time.sleep(0.8)
    d["exec_state"] = g.exec_state(path)
    rows = g.panel_wiring(path)
    d["rows"] = rows
    print(f"   ExecState {d['exec_state']}; {len(rows)} top-level panel objects, "
          f"{sum(1 for r in rows if r['wire'])} with a wired terminal", flush=True)
    print(f"   {'uid':>6}  {'kind':<9} {'src':<5} {'wire':>6}  label", flush=True)
    for r in rows:
        kind = "indicator" if r["indicator"] else "control"
        print(f"   {int(r['uid']):>6}  {kind:<9} {str(bool(r['is_source'])):<5} {int(r['wire']):>6}  "
              f"{r['label']!r}", flush=True)
    by_uid = {int(r["uid"]): r for r in rows}
    for uid, lab in CALLOUT.items():
        r = by_uid.get(uid)
        d[f"uid{uid}"] = None if r is None else {"label": r["label"], "wire": int(r["wire"]),
                                                 "indicator": bool(r["indicator"])}
        state = "ABSENT from the panel census" if r is None else \
            (f"WIRED to #{int(r['wire'])}" if r["wire"] else "UNWIRED (wire == 0)")
        print(f"   >>> CALLOUT uid {uid} ({lab}): {state}"
              + ("" if r is None else f"; label on the machine {r['label']!r}"), flush=True)
    try:
        cp = g.conpane(path)
    except Exception as e:
        cp = {}
        print(f"   NOTE conpane EXC {str(e)[:120]}", flush=True)
    d["conpane"] = {str(k): v for k, v in cp.items()}
    by_label = {}
    for r in rows:
        by_label.setdefault(r["label"], r)
    cp_rows, unmatched = [], []
    for idx, lab in sorted(cp.items()):
        if lab is None:
            continue
        r = by_label.get(lab)
        if r is None:
            unmatched.append((idx, lab))
            continue
        cp_rows.append((idx, lab, int(r["uid"]), int(r["wire"])))
    d["conpane_rows"] = cp_rows
    d["conpane_unmatched"] = unmatched
    unwired_cp = [(i, l, u) for (i, l, u, w) in cp_rows if w == 0]
    d["conpane_unwired"] = unwired_cp
    print(f"   connector pane: {len(cp_rows)} assigned terminal(s) matched to a census row; "
          f"{len(unmatched)} unmatched {unmatched}", flush=True)
    print(f"   ON THE CONNECTOR PANE AND UNWIRED ({len(unwired_cp)}): "
          f"{[(i, l, u) for (i, l, u) in unwired_cp]}", flush=True)
    return d


def main():
    print("=== diag_fstunnelterm_v2_panelcost: PANEL cost of the A0h RBW repair (measurement only) ===",
          flush=True)
    TW.handles("before")
    RES["handles"]["before"] = TW.RES["handles"].get("before")
    before = {p: TW.md5(p) for p in TW.WATCHED}
    RES["md5"]["before"] = before
    print(f"-- md5 before: {len(before)} files ({len(TW.ORIGINALS)} originals) --", flush=True)

    built = [p for p in OPS if os.path.exists(p)]
    must("P1 at least one of the two ops exists on disk (stage 2 built it)", bool(built),
         f"built: {[os.path.basename(p) for p in built]}")
    for p in OPS:
        d = report(p)
        if not d["exists"]:
            continue
        n = os.path.basename(p)
        must(f"P2 [{n}] panel_wiring returns >= 30 top-level rows", len(d.get("rows", [])) >= 30,
             f"{len(d.get('rows', []))} rows")
        for uid, lab in CALLOUT.items():
            got = d.get(f"uid{uid}")
            must(f"P3/P4 [{n}] uid {uid} ({lab}) is present and UNWIRED (wire == 0)",
                 got is not None and got["wire"] == 0,
                 "absent from the census" if got is None else
                 f"label {got['label']!r}, wire {got['wire']}")
        must(f"P5 [{n}] every conpane-assigned label matched a panel census row",
             not d.get("conpane_unmatched"), f"unmatched: {d.get('conpane_unmatched')}")

    after = {p: TW.md5(p) for p in TW.WATCHED}
    RES["md5"]["after"] = after
    diff = [os.path.basename(p) for p in TW.WATCHED if before.get(p) != after.get(p)]
    must(f"P6 all {len(TW.ORIGINALS)} originals (+ the V6 copy and the donor) are md5-identical before and after",
         not diff and not any(str(v).startswith("ERR") for v in after.values()), f"differing: {diff}")
    src = open(os.path.abspath(__file__), encoding="utf-8").read()
    must("P7 no motor, no serial, no camera (static: no `import serial`, no motor_gate, no .ps1 call)",
         "import serial" not in src and "motor_gate" not in src.replace("motor_gate.py --execute not", "")
         and ".ps1" not in src.replace("no `.ps1`", ""), "static scan of this file")
    TW.handles("after")
    RES["handles"]["after"] = TW.RES["handles"].get("after")
    must("P8 handle count recorded BEFORE and AFTER",
         RES["handles"]["before"] is not None and RES["handles"]["after"] is not None,
         f"{RES['handles']['before']} -> {RES['handles']['after']}")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(RES, f, indent=1, default=str)
    ok = sum(1 for x in RES["gates"] if x["ok"])
    print(f"\n=== diag_fstunnelterm_v2_panelcost: {ok} pass, {len(RES['gates']) - ok} fail ===", flush=True)
    print(f"    json {OUT}", flush=True)
    return 0 if ok == len(RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
