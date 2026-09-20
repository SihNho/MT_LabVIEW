r"""diag_exitwhile_front.py - READ-ONLY census of `OpExitWhile_v0.vi`'s FRONT HALF, so the sentinel-driven
variant is written against measured names instead of guessed ones (CLAUDE.md: discovery paid up front).

    MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/diag_exitwhile_front.log \
        -- py -u tools/bench/diag_exitwhile_front.py

WHAT ALREADY EXISTS - checked first:
  * `OpExitWhile_v0.vi` (docs/toolkit-capabilities.md:31, test_opexitwhile.log 5/5) and its build recipe
    `archive/bench-2026-09-14-stage2-toolkit/build_opexitwhile.py`, whose header states the front half verbatim:
    "'Stop Condition' fed from a front-panel control chosen BY NAME: VI.Block Diagram -> Get Controls(Control
    Names) -> Index Array[0] -> Stop Condition."
  * `tools/bench/opexitwhile_labels.json` = {"stop_names": "Control Names"}.
  * `g.node_labels`, `g.node_terms_uid`, `g.report_all`, `g.panel_wiring`, `g.fp_labels` - all built readers.
This file ADDS no op and writes nothing; it only prints what the swap has to detach and re-attach.

PREDICTION CONTRACT:
  E1 `OpExitWhile_v0.vi` exists and reads ExecState 1.
  E2 its top-level diagram carries `Get Controls.vi`, an `Index Array`, `Exit While Loop.vi`, `Open VI Reference`
     and at least two `Get Outputs.vi` calls (the Names / Names 2 pair the donor had).
  E3 every node's terminals are printed with (name, is_source, wire) so the exact sink name on
     `Exit While Loop.vi` (expected `Stop Condition`) and the exact source name on `Get Outputs.vi`
     (expected `Outputs`) are read, never assumed.
  E4 the panel's control labels are printed, so the new `Names 3` control can be given a label that does not
     collide (the fleet's recorded trap: two terminals with the same name).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, sys.argv[1] if len(sys.argv) > 1 else "OpExitWhile_v0.vi")
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
    if not gate("E1a OpExitWhile_v0.vi on disk", os.path.exists(OP), OP):
        return 1
    g.open_panel(OP)
    es = g.exec_state(OP)
    gate("E1 ExecState 1", es == 1, f"ExecState {es}")
    for cls in ("Node", "SubVI", "Function", "Property", "Diagram", "Wire", "Constant", "ControlTerminal"):
        try:
            print(f"  COUNT {cls:16s} {g.count(OP, cls)}", flush=True)
        except Exception as e:
            print(f"  COUNT {cls:16s} <{str(e)[:50]}>", flush=True)

    labels = {}
    try:
        for r in g.node_labels(OP, 0):
            labels[r["uid"]] = r["label"]
    except Exception as e:
        print(f"  node_labels(0) failed: {str(e)[:120]}", flush=True)
    txt = " | ".join(str(v) for v in labels.values())
    print(f"  LABELS d0: {txt}", flush=True)
    gate("E2a Get Controls.vi present", "Get Controls.vi" in txt, "")
    gate("E2b Exit While Loop.vi present", "Exit While Loop.vi" in txt, "")
    gate("E2c at least two Get Outputs.vi", txt.count("Get Outputs.vi") >= 2, f"{txt.count('Get Outputs.vi')}")
    gate("E2d an Index Array present", "Index Array" in txt, "")

    print("\n=== E3: every node on diagram 0, its Traverse indices and its terminals", flush=True)
    idx_by_cls = {}
    for cls in ("Node", "SubVI", "Function", "Property"):
        try:
            idx_by_cls[cls] = [o["uid"] for o in g.report_all(OP, cls)]
        except Exception:
            idx_by_cls[cls] = []
    for cand in range(80):
        try:
            nu, rows = g.node_terms_uid(OP, 0, cand)
        except Exception as e:
            print(f"  node_terms_uid(0,{cand}) failed: {str(e)[:80]}", flush=True)
            break
        if not nu:
            break
        where = {c: (idx_by_cls[c].index(nu) if nu in idx_by_cls[c] else None) for c in idx_by_cls}
        print(f"  NODE[{cand}] uid {nu} label {labels.get(nu)!r}  traverse {where}", flush=True)
        for r in rows:
            print(f"        t{r['i']:<2} {r['name']!r:38s} src={r['is_source']}  w{r['wire']}", flush=True)

    print("\n=== E4: panel labels", flush=True)
    try:
        for r in g.panel_wiring(OP):
            print(f"  CTL uid {r['uid']} label {r['label']!r} indicator={r.get('is_indicator')} wire {r['wire']}",
                  flush=True)
    except Exception as e:
        print(f"  panel_wiring failed: {str(e)[:120]}", flush=True)
    g.close_panel(OP)
    g._lv = None
    print(f"\n=== diag_exitwhile_front: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
