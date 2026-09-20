r"""diag_stop_condterm_panel.py - one follow-up read for cycle 15 step 1(b)(iv), after the P5 failed prediction.

WHAT ALREADY EXISTS (checked first): `g.panel_wiring(target)` (tools/gscript.py:632) already returns every
front-panel object's label / uid / indicator flag / CONNECTED WIRE UID in one op run - it is the reader that
produced docs/main-vi-panel-map.md's table. NO new op, no new reader.

THE QUESTION. tools/bench/diag_stop_save_seam.log measured wire 3457 (the `stop (end)` OR's `result`) as having
TWO sinks, both with owner class `Diagram`#639, and the 626-node terminal census claims neither. A terminal whose
owner is the diagram is either a front-panel object's terminal or a structure-owned terminal. panel_wiring
decides which: if a panel object's connected wire is 3457, that sink is a panel terminal and is NOT the loop's
conditional terminal; if NO panel object carries 3457, both sinks are non-panel diagram terminals.

PREDICTION CONTRACT:
  Q1  panel_wiring returns the two known stop rows unchanged: `stop (end)` uid 7 wire 6929, `stop (end) 2`
      uid 19587 wire 15230 (docs/main-vi-panel-map.md:280,:329) - the reader is reading the same VI.
  Q2  NO front-panel object carries wire 3457 or wire 15229.
Q2 is the discriminating one and is NOT assumed: whatever it returns is reported.

  MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/diag_stop_condterm_panel.log -- py -u tools/bench/diag_stop_condterm_panel.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import MAIN, fresh  # noqa: E402

WIRES = [3457, 15229, 6929, 15230, 22085]
OUT = os.path.join(HERE, "stop_condterm_panel.json")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    before = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    print(f"MAIN md5 before: {before}", flush=True)
    fresh()
    gates = []
    try:
        rows = g.panel_wiring(MAIN)
        print(f"panel_wiring: {len(rows)} front-panel objects", flush=True)
        by_wire = {}
        for r in rows:
            w = int(r.get("wire") or 0)
            if w:
                by_wire.setdefault(w, []).append(r)
        for w in WIRES:
            hit = by_wire.get(w, [])
            print(f"RESULT wire {w}: panel objects carrying it = "
                  + (", ".join(f"{h.get('label')!r} uid {h.get('uid')} "
                               f"{'IND' if h.get('indicator') else 'CTL'}" for h in hit) if hit else "NONE"),
                  flush=True)
        stop1 = [r for r in rows if r.get("label") == "stop (end)"]
        stop2 = [r for r in rows if r.get("label") == "stop (end) 2"]
        for nm, got, uid, wu in (("stop (end)", stop1, 7, 6929), ("stop (end) 2", stop2, 19587, 15230)):
            ok = len(got) == 1 and int(got[0].get("uid")) == uid and int(got[0].get("wire") or 0) == wu
            gates.append((f"Q1 {nm} uid {uid} wire {wu}", ok))
            print(f"  {'PASS' if ok else '-> FAIL'}  Q1 {nm} uid {uid} wire {wu}   {got}", flush=True)
        ok = not by_wire.get(3457) and not by_wire.get(15229)
        gates.append(("Q2 no panel object carries 3457 or 15229", ok))
        print(f"  {'PASS' if ok else '-> FAIL'}  Q2 no panel object carries 3457 or 15229", flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump({"md5": before, "rows": rows, "wires": {str(w): by_wire.get(w, []) for w in WIRES}},
                      f, indent=1, default=str)
    finally:
        after = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
        ok = after == before
        gates.append(("MAIN md5 unchanged", ok))
        print(f"  {'PASS' if ok else '-> FAIL'}  MAIN md5 unchanged   {after}", flush=True)
        print(f"SUMMARY {sum(1 for _, o in gates if o)}/{len(gates)} gates pass; "
              f"failing: {[n for n, o in gates if not o]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
