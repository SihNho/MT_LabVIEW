"""diag_addsr_fail1.py - DIAGNOSTIC ONLY (RECOVERY_LOCKED: reporter reads, no edits, no save).

The failed prediction: build_opaddshiftreg_v0.py wired the TMSC's 'specific class reference' into the new Invoke's
'reference' with branch=True, predicted Wire +1 / ExecState 1, observed Wire unchanged (16) and ExecState 0.

Competing explanations:
  H1 the branch LANDED (an unchanged wire count is the documented signature of a branch) and ExecState 0 is the
     still-unwired required 'Y Position';
  H2 the wire was silently DECLINED (Loop-class invoke refusing a WhileLoop reference, or the by-name call landing
     on the duplicated OUTPUT terminal of the same name).

DISCRIMINATOR: read the Invoke node's terminals. If 'reference' (is_source False) carries the SAME wire uid as the
TMSC's 'specific class reference' output, H1 holds and H2 is dead. Also prints every terminal with its direction so
the duplicate-name question ('Add Shift Register' x2, 'Y Position' x2) is answered by measurement, not by guess.

The VI was left OPEN and UNSAVED by the stopped batch; this script only reads, and closes nothing.
  py tools/bgrun.py --max-min 6 --log tools/bench/diag_addsr_fail1.log -- py -u tools/bench/diag_addsr_fail1.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpAddShiftReg_v0.vi")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
    rows_by_uid = {}
    for n in range(60):
        u, rows = g.node_terms_uid(OP, 0, n)
        if not u:
            break
        rows_by_uid[u] = (n, labels.get(u), rows)
    tmsc = next((u for u, (n, lab, rows) in rows_by_uid.items()
                 if any(r["name"] == "specific class reference" for r in rows)), None)
    inv = next((u for u, (n, lab, rows) in rows_by_uid.items()
                if any(r["name"] == "Y Position" for r in rows)), None)
    print(f"TMSC uid {tmsc}; Invoke uid {inv}", flush=True)
    if tmsc is None or inv is None:
        print("VERDICT: INCONCLUSIVE - the nodes are not both present (the VI may have been reverted).", flush=True)
        return 1
    w_src = next((r["wire"] for r in rows_by_uid[tmsc][2]
                  if r["name"] == "specific class reference" and r["is_source"]), None)
    print(f"\nTMSC 'specific class reference' (source) wire = {w_src}", flush=True)
    print("\nInvoke terminals (index | name | is_source | wire):", flush=True)
    for r in rows_by_uid[inv][2]:
        print(f"   {r['i']:>3} | {r['name']!r:<28} | src={r['is_source']!s:<5} | wire={r['wire']}", flush=True)
    ref = [r for r in rows_by_uid[inv][2] if r["name"] == "reference" and not r["is_source"]]
    w_ref = ref[0]["wire"] if ref else None
    print(f"\nInvoke 'reference' (sink) wire = {w_ref}", flush=True)
    if w_ref and w_src and w_ref == w_src:
        print("VERDICT: H1 - the BRANCH LANDED (same wire uid on both ends). The Loop-class invoke accepted the "
              "WhileLoop reference; ExecState 0 must be explained by an unwired required input, not by the wire.", flush=True)
        rc = 0
    elif not w_ref:
        print("VERDICT: H2 - 'reference' is UNWIRED: the by-name wire call was silently declined.", flush=True)
        rc = 2
    else:
        print(f"VERDICT: neither - 'reference' carries wire {w_ref}, not the TMSC's {w_src}.", flush=True)
        rc = 3
    ys = [r for r in rows_by_uid[inv][2] if r["name"] == "Y Position"]
    print(f"\n'Y Position' terminals: {[(r['i'], r['is_source'], r['wire']) for r in ys]} "
          "(a sink AND a source of the same name = the duplicate-name trap this project hit twice before)", flush=True)
    print(f"ExecState now: {g.exec_state(OP)}", flush=True)
    return rc


if __name__ == "__main__":
    sys.exit(main())
