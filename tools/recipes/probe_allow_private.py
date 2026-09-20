"""probe_allow_private.py - is `Set Method (Allow Private)` itself attachable by our builder?

THE WHOLE FIX HINGES ON THIS ONE ANSWER, and it is cheap to get.

Background. Our keystone builders wrap erdosmiller's `Create Invoke Node.vi` / `Create Property Node.vi`, and a
read of those VIs (2026-09-14) shows their inputs are exactly:

    Create Invoke Node   : Class Name, ID String, Inputs, location, Diagram in
    Create Property Node : Class Name, Properties, Inputs, location, Diagram in

**No `allow private` input exists**, so the wrappers must be calling the ordinary `Set Method` (6370002) /
`Set Properties[]`, which silently refuse private members - matching every failure we have recorded
(`Control.Value` 633200D, `VI:Get Errors` 452: node created, member never attached, only generic terminals).

The documented remedy is the dedicated setter `Invoke.Set Method (Allow Private)` = **6370003**. But there is an
obvious circularity risk: to CALL that setter we need an Invoke node configured for it, and configuring it goes
through the same builder. So:

    IF 6370003 is PUBLIC   -> our builder can attach it -> no circularity -> build a private-capable creator.
    IF 6370003 is PRIVATE  -> circular -> the only route left is a donor node copied with `Create from Reference`,
                              and making that donor needs one gated GUI action, which will NOT be taken
                              unattended.

PREDICTION, stated before the run so the outcome is machine-checkable:
  * PUBLIC  -> the new Invoke node carries METHOD-SPECIFIC terminals beyond the generic four
               (`reference`, `reference out`, `error in (no error)`, `error out`) - e.g. an ID String input.
  * PRIVATE -> exactly those four and nothing else, the signature seen in both earlier failures.

Also probed, because it costs one extra call and settles the property half:
  `Property.Set Properties[] (Allow Private)` = 636F406.

SAFETY: a scratch VI, created and deleted in the same run. Nothing existing is modified.
  py tools/bgrun.py --max-min 12 --log tools/bench/probe_allow_private.log -- py -u tools/recipes/probe_allow_private.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_allow_private.vi")

GENERIC = {"reference", "reference out", "error in (no error)", "error out"}
CANDIDATES = [
    ("VI Server:Invoke", "6370003", "Invoke.Set Method (Allow Private)"),
    ("VI Server:Property", "636F406", "Property.Set Properties[] (Allow Private)"),
    # Controls: the ordinary setter, to show what a PUBLIC attach looks like on this same scratch VI.
    ("VI Server:Terminal", "6349C02", "Terminal.Create Indicator  (PUBLIC control)"),
]
g._run.__defaults__ = (6.0, 120.0)


def terminals_of(uid):
    """Terminal names of the node `uid` on the top-level diagram."""
    nodes, _w = g.net_map(S, 0, max_nodes=60, max_terms=24)
    for _i, (u, _lbl, terms) in nodes.items():
        if u == uid:
            return [t for _ti, t, _w2 in terms if t]
    return None


def main():
    g._lv = None
    try:
        g.close_panel(S)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(S):
        try:
            os.remove(S)
        except OSError:
            pass
    shutil.copyfile(SRC, S)
    g.open_panel(S)
    time.sleep(0.9)
    print(f"scratch ready, ExecState {g.exec_state(S)}\n", flush=True)

    results = []
    for cls, mid, label in CANDIDATES:
        print(f"== {label}   class={cls} id={mid}", flush=True)
        print("   predict: PUBLIC -> method-specific terminals appear; PRIVATE -> only the generic four",
              flush=True)
        try:
            new = g.build_invoke(S, cls, mid, (400 + 250 * len(results), 900))
        except Exception as e:
            print(f"   OBSERVED: EXC {str(e)[:200]}\n", flush=True)
            results.append((label, "exception", str(e)[:120]))
            continue
        if not new:
            print("   OBSERVED: no node created\n", flush=True)
            results.append((label, "no node", ""))
            continue
        uid = new[-1]["uid"]
        terms = terminals_of(uid)
        if terms is None:
            print(f"   OBSERVED: node uid {uid} created but not found by net_map\n", flush=True)
            results.append((label, "node not found", ""))
            continue
        extra = [t for t in terms if t not in GENERIC]
        verdict = "ATTACHED (public)" if extra else "NOT ATTACHED (private/refused)"
        print(f"   OBSERVED: uid={uid} terminals={terms}", flush=True)
        print(f"   -> {verdict}   method-specific: {extra}\n", flush=True)
        results.append((label, verdict, ", ".join(extra)))

    print("################ SUMMARY ################", flush=True)
    for label, verdict, extra in results:
        print(f"  {label:46} {verdict:32} {extra}", flush=True)

    ok = any(v.startswith("ATTACHED") for _l, v, _e in results[:2])
    print("\nVERDICT:", flush=True)
    if ok:
        print("  BRANCH A - an Allow-Private setter attaches, so a private-capable creator can be BUILT.",
              flush=True)
    else:
        print("  BRANCH B - the Allow-Private setters are themselves unattachable: circular.", flush=True)
        print("  The remaining scripted route is a donor node copied with `Create from Reference`, and", flush=True)
        print("  creating that donor needs one gated GUI action. NOT to be taken unattended.", flush=True)
    print("  (The third row is the control: if the PUBLIC method also shows NOT ATTACHED, the probe itself",
          flush=True)
    print("   is broken and neither verdict above means anything.)", flush=True)

    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
        print("\nscratch deleted", flush=True)
    except Exception as e:
        print("\ncleanup:", str(e)[:100], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
