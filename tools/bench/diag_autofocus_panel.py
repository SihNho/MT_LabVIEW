r"""diag_autofocus_panel.py - NAME the two autofocus objects, and settle the error-1092 failed prediction.

Run 1 (`diag_autofocus_border.py`, 2026-09-16 13:4x) resolved all three wires and hit one unpredicted failure:

    wire 3362 (the NOT's input)      source = ('Diagram', 639)   sinks: Function 10825
    wire 3268 (the modulo dividend)  source = ('Diagram', 639)   sinks: Function 2136 (autofocus modulo),
                                     SelectorTunnel 3045, LoopTunnel 2213, **Function 10068** (the PERIODIC
                                     AUTO-RESET modulo named at stage2-assembly-step-e.md:36), SubVI 1114 t0 "index i"
    report_all(MAIN, "PropertyNode") -> **error 1092** (Traverse for GObjects), which was NOT predicted

A source terminal whose owner is a `Diagram` is the signature of a FRONT-PANEL CONTROL TERMINAL - that is how
INDEX.md row 43 identified `Auto-Reset`, `Reset Tracking` and `Limit of Program`, and it says the identification
was "confirmed by `panel_wiring`". A diagram-owned CONSTANT would look the same, so the signature alone is not the
answer; `panel_wiring` is.

GOAL 1 - name them. `panel_wiring(MAIN)` returns every top-level panel object with its terminal's connected wire
UID. If wire 3362 or 3268 appears there, the control's LABEL is the answer, measured rather than inferred.

GOAL 2 - the failed prediction, with a discriminating test rather than an explanation. Two candidates:
  (H1) the CLASS NAME is wrong for a traverse on this VI. Evidence for it, from run 1's own log: OpWireSource
       reported the owner class of uid 30146 as **`Property`**, not `PropertyNode`.
  (H2) the class name is fine and something about the MAIN VI (size, a nested object, a locked diagram) breaks
       the traverse. Evidence for it: `PropertyNode` is the class name gscript uses successfully elsewhere
       (build_opownerchain_v0.py counts it on an op VI).
  The test separates them: `count`/`uids` and `report_all` are run for BOTH class names on BOTH the main VI and a
  small op VI. H1 predicts "Property" works where "PropertyNode" fails, on both VIs. H2 predicts the failure
  follows the VI, not the name.

PREDICTION CONTRACT:
  P1 `panel_wiring(MAIN)` returns ~114 rows (test_oppanelwiring.log: 114 rows, 60 controls / 54 indicators).
  P2 at least one of wires 3362 / 3268 appears as a row's `wire`.
  P3 the 2x2x2 grid above separates H1 from H2 - i.e. the failures are not identical in every cell.

Read-only on MAIN, md5 checked. Nothing is built.

  py tools/bgrun.py --max-min 20 --log tools/bench/diag_autofocus_panel.log -- py -u tools/bench/diag_autofocus_panel.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import MAIN  # noqa: E402

SMALL = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
TARGET_WIRES = {3362: "the NOT's input - can it block autofocus?", 3268: "the shared frame counter"}
OUT = os.path.join(HERE, "autofocus_panel.json")


def try_call(label, fn):
    try:
        v = fn()
        n = len(v) if hasattr(v, "__len__") else v
        print(f"  OK    {label:<46} -> {n}", flush=True)
        return {"ok": True, "result": n}
    except Exception as e:
        msg = str(e)[:150]
        print(f"  FAIL  {label:<46} -> {msg}", flush=True)
        return {"ok": False, "error": msg}


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    out = {"panel": None, "matches": [], "grid": {}, "main_md5_before": md5}
    try:
        print("=== GOAL 1: panel_wiring(MAIN) - which control drives wires 3362 / 3268", flush=True)
        rows = g.panel_wiring(MAIN)
        out["panel"] = {"rows": len(rows),
                        "controls": sum(1 for r in rows if not r["indicator"]),
                        "indicators": sum(1 for r in rows if r["indicator"])}
        out["all_rows"] = rows
        # A CONTROL WITH A BARE TERMINAL (wire 0) is used only through a local or a property node - which is
        # exactly the shape of the autofocus interval N behind Property Node #30146. This list is the candidate
        # set, and it is free: `panel_wiring` already has the answer in hand.
        bare = [r for r in rows if not r["indicator"] and r["wire"] == 0]
        print(f"\n  CONTROLS WITH A BARE TERMINAL ({len(bare)} of {out['panel']['controls']}) - the only ones a "
              f"property node or local can be reading:", flush=True)
        for r in bare:
            print(f"    {r['label']!r:<42} uid {r['uid']}", flush=True)
        print(f"  {len(rows)} rows ({out['panel']['controls']} controls / {out['panel']['indicators']} indicators)",
              flush=True)
        for r in rows:
            if r["wire"] in TARGET_WIRES:
                print(f"  *** wire {r['wire']} = front-panel {'indicator' if r['indicator'] else 'CONTROL'} "
                      f"{r['label']!r} (uid {r['uid']}, is_source={r['is_source']})   <- {TARGET_WIRES[r['wire']]}",
                      flush=True)
                out["matches"].append(r)
        for w, why in TARGET_WIRES.items():
            if not any(r["wire"] == w for r in rows):
                print(f"  --- wire {w} is NOT on any panel terminal: it is a CONSTANT or a local on diagram 639 "
                      f"({why})", flush=True)
        # the autofocus panel objects, whatever drives them, are worth printing with their wiring
        print("\n  focus/reset-related panel rows:", flush=True)
        for r in rows:
            if any(k in (r["label"] or "").lower() for k in ("focus", "auto", "reset", "limit", "program")):
                print(f"    {r['label']!r:<38} uid {r['uid']:<7} wire {r['wire']:<7} "
                      f"{'IND' if r['indicator'] else 'CTL'} src={r['is_source']}", flush=True)

        print("\n=== GOAL 2: does error 1092 follow the CLASS NAME or the VI?", flush=True)
        for vi_label, target in (("MAIN", MAIN), ("small op VI", SMALL)):
            for cls in ("PropertyNode", "Property"):
                out["grid"][f"{vi_label}|{cls}|count"] = try_call(f"count({vi_label}, {cls!r})",
                                                                  lambda t=target, c=cls: g.count(t, c))
                out["grid"][f"{vi_label}|{cls}|report_all"] = try_call(f"report_all({vi_label}, {cls!r})",
                                                                       lambda t=target, c=cls: g.report_all(t, c))
    finally:
        after = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
        out["main_md5_after"] = after
        out["main_unchanged"] = after == md5
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE.
        print(f"\n   {'PASS' if after == md5 else 'FAIL'} main VI unchanged; wrote {OUT}", flush=True)
        g._lv = None
    print(f"\n=== SUMMARY {len(out['matches'])}/{len(TARGET_WIRES)} target wires named from the panel ===", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
