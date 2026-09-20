"""read_shared_state.py - the fields of `Global motor pos.vi`, the VI Global every loop shares.

WHY THIS ONE FIRST. The restructuring's entire correctness argument is **one writer per field**. That claim
cannot be made, checked, or even stated precisely without knowing what the fields ARE. `Global motor pos.vi`
appears 9 times in the main VI and is named in ARCHITECTURE.md §5 as the cross-loop shared state - so its front
panel *is* the inter-loop contract, and reading it needs no new tooling.

It is also the part of document 3 (`main-vi-state.md`) that is reachable today. The name-reading op that would
give locals and globals their identities is blocked: `build_invoke` cannot attach super-private methods
(verified twice - 2026-09-09 and 2026-09-14, identical symptom: the node appears with only `reference out` and
`error out`, no method terminals), so the error list stays unreadable and `OpReportNodes_v0` stays unfinished.
Rather than keep pushing on that, this takes the part that is not blocked.

WHAT IT CANNOT SAY: who writes and who reads each field. That needs the call-site map. Reported as open.

READ-ONLY: the global and the motor VIs are opened and read, never saved (CLAUDE.md rule 1).

  py tools/bench/read_shared_state.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VILIB = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
TARGETS = [
    os.path.join(VILIB, "four-fold tracking", "Global motor pos.vi"),
]
g._run.__defaults__ = (6.0, 180.0)


def main():
    g._lv = None
    for path in TARGETS:
        name = os.path.basename(path)
        print(f"\n===== {name} =====", flush=True)
        if not os.path.exists(path):
            print("   NOT FOUND at", path, flush=True)
            continue
        print(f"   {path}", flush=True)
        try:
            rows = g.fp_labels(path, max_n=60)
        except Exception as e:
            print(f"   fp_labels EXC {str(e)[:200]}", flush=True)
            continue
        try:
            ref = g.lv().GetVIReference(path, "", False, 0)
        except Exception as e:
            print(f"   GetVIReference EXC {str(e)[:150]}", flush=True)
            ref = None
        print(f"   {len(rows)} front-panel objects", flush=True)
        for i, lab, ind in rows:
            val = ""
            if ref is not None and lab:
                try:
                    val = repr(ref.GetControlValue(lab))[:70]
                except Exception as e:
                    val = f"<unreadable: {str(e)[:40]}>"
            print(f"   {i:2d} {'IND' if ind else 'CTL'} {lab!r:34} = {val}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
