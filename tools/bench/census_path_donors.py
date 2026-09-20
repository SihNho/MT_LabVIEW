"""census_path_donors.py - READ-ONLY: which SMALL lab VI (claudeDev/background VIs_COPY) holds `Build Path`,
`Format Into String`, `String To Path` primitives, and on which diagram / node index - the donor for the
`FramePath.vi` sub-build (docs/stage2-assembly-step-b.md, revised route). Reference-only reads, nothing opened.
  py tools/bgrun.py --max-min 6 --log tools/bench/census_path_donors.log -- py -u tools/bench/census_path_donors.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

BG = os.path.join(g.CLAUDEDEV, "background VIs_COPY")
WANT = ("Build Path", "Format Into String", "String To Path", "Strip Path", "Path To String")
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    cands = sorted(f for f in os.listdir(BG) if f.lower().endswith(".vi") and os.path.getsize(os.path.join(BG, f)) < 120_000)
    print(f"{len(cands)} small VIs in {BG}", flush=True)
    found = {}
    for f in cands:
        p = os.path.join(BG, f)
        hits = []
        for dia in range(0, 12):
            try:
                rows = g.node_labels(p, dia)
            except Exception as e:
                if dia == 0:
                    print(f"   {f}: EXC {str(e)[:80]}", flush=True)
                break
            if not rows:
                break
            for k, r in enumerate(rows):
                if r["label"] in WANT:
                    hits.append((dia, k, r["uid"], r["label"]))
        if hits:
            found[f] = hits
            print(f"   {f} ({os.path.getsize(p)} B): {hits}", flush=True)
    print("\nDONORS:", {k: sorted({h[3] for h in v}) for k, v in found.items()}, flush=True)
    return 0 if found else 1


if __name__ == "__main__":
    sys.exit(main())
