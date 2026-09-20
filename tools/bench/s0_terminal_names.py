"""s0_terminal_names.py - read-only: settle the two terminal-name questions S0's build turns on.

RAISED BY `archive/peer/2026-09-19-priorart-s0-closeref.md` A3(ii): `docs/NAMES.md` contradicts ITSELF about
the same node and the same terminal index -
    :741  "Traverse for GObjects.vi | error out, # of Refs, `References`, dup VI Refnum, ..."   (index 2)
    :230  "Traverse for GObjects.vi: terminal 2 = `GObject Refs` output"
"One of these is wrong and a by-name wire against the wrong one fails." This script asks the MACHINE instead of
picking a document. It also reads the `Close Reference` donor's own terminal names (uid 157 in
KernelBuilder_v1.vi), which no document in this project records at all.

Read-only: it opens no panel, edits nothing, saves nothing. Nothing here is a build.

PREDICTION CONTRACT:
  T1  `Traverse for GObjects.vi` on OpReport_v3.vi exposes a terminal whose EXACT name is one of
      {'References', 'GObject Refs'} and is a SOURCE. The run prints the exact bytes of every terminal, so
      whichever spelling is real, the answer is quotable.
  T2  `Close Reference` #157 in KernelBuilder_v1.vi has exactly one non-error SINK terminal; its exact name is
      printed (the input `archive/WORKLOG.md:84-86` records as having "defeated four wiring attempts").
  T3  Both nodes' full terminal lists are printed with index, name, is_source and current wire uid.

  py tools/bgrun.py --material --max-min 12 --log tools/bench/s0_terminal_names.log -- py -u tools/bench/s0_terminal_names.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402

CD = g.CLAUDEDEV
OP_V3 = os.path.join(CD, "OpReport_v3.vi")
WS_V5 = os.path.join(CD, "OpWireSource_v5.vi")
DONOR = os.path.join(CD, "KernelBuilder_v1.vi")

_P = _F = 0


def gate(label, ok, detail=""):
    global _P, _F
    if ok:
        _P += 1
        print(f"  PASS {label}  {detail}", flush=True)
    else:
        _F += 1
        # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE.
        print(f"  FAIL {label}  {detail}", flush=True)


def dump(path, want_label):
    print(f"\n-- {os.path.basename(path)}", flush=True)
    w = B.walk(path, 0)
    hits = []
    for uid, (n, label, rows) in w.items():
        if want_label(label):
            hits.append((uid, label, rows))
            print(f"   node #{uid} (index {n}) label {label!r}", flush=True)
            for r in rows:
                print(f"       [{r['i']:2d}] {r['name']!r:<34} source={r['is_source']!s:<5} wire={r['wire']}",
                      flush=True)
    return hits


def main():
    print("=== S0 TERMINAL NAMES (read-only) ===", flush=True)

    tv = dump(OP_V3, lambda l: l == "Traverse for GObjects.vi")
    gate("T0 the Traverse node was found on OpReport_v3", len(tv) == 1, str([h[0] for h in tv]))
    names = [r["name"] for r in tv[0][2]] if tv else []
    srcs = [r["name"] for r in tv[0][2] if r["is_source"]] if tv else []
    print(f"   SOURCE terminal names, exact bytes: {srcs!r}", flush=True)
    gate("T1 exactly one of {'References','GObject Refs'} is a real SOURCE name",
         len([n for n in srcs if n.strip() in ("References", "GObject Refs")]) == 1,
         f"all names {names!r}")

    cr = dump(DONOR, lambda l: l == "Close Reference")
    gate("T2a the Close Reference donor node was found", len(cr) == 1, str([h[0] for h in cr]))
    if cr:
        ns = [r for r in cr[0][2] if not r["is_source"]]
        non_err = [r["name"] for r in ns if "error" not in r["name"].strip().lower()]
        print(f"   SINK terminal names: {[r['name'] for r in ns]!r}", flush=True)
        print(f"   NON-ERROR sink (the refnum input): {non_err!r}", flush=True)
        gate("T2 exactly one non-error SINK on Close Reference", len(non_err) == 1, str(non_err))

    tw = dump(WS_V5, lambda l: l == "Traverse for GObjects.vi")
    gate("T3 OpWireSource_v5 carries the same Traverse node", len(tw) == 1, str([h[0] for h in tw]))
    if tw and tv:
        gate("T3b its terminal names are identical to OpReport_v3's",
             [r["name"] for r in tw[0][2]] == names, "")

    print(f"\nGATES: {_P} PASS / {_F} FAIL", flush=True)
    return 0 if _F == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        import traceback
        traceback.print_exc()
        print(f"\nGATES: {_P} PASS / {_F} FAIL (raised)", flush=True)
        sys.exit(1)
