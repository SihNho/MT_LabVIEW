"""census_newviobject_donors.py - READ-ONLY census of NI's 'Creating Objects' scripting examples (the donors for
OpNewFPArray_v0, docs/stage2-assembly-step-b.md B0): every node's label and terminals with wire uids, and every
front-panel control's label, so the op recipe is written from measured names. Reference-only reads (no panel opened,
nothing written); the files are the project's own copies under claudeDev/NIScriptingExamples.
  py tools/bgrun.py --max-min 6 --log tools/bench/census_newviobject_donors.log -- py -u tools/bench/census_newviobject_donors.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

D = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Creating Objects")
FILES = ["Drop Digital Numeric Inside Cluster.vi", "Adding Objects.vi", "Test - New VI Object.vi"]
g._run.__defaults__ = (6.0, 90.0)


def main():
    g._lv = None
    for f in FILES:
        p = os.path.join(D, f)
        print(f"\n######## {f}  exists={os.path.exists(p)}", flush=True)
        if not os.path.exists(p):
            continue
        try:
            print("   controls:", [(l, ind) for _i, l, ind in g.fp_labels(p)], flush=True)
        except Exception as e:
            print(f"   fp_labels EXC {str(e)[:120]}", flush=True)
        for dia in range(0, 4):
            try:
                labels = {r["uid"]: r["label"] for r in g.node_labels(p, dia)}
            except Exception as e:
                print(f"   diagram {dia}: EXC {str(e)[:100]}", flush=True); break
            if not labels:
                break
            print(f"   diagram {dia}: {len(labels)} nodes", flush=True)
            for n in range(60):
                u, rows = g.node_terms_uid(p, dia, n)
                if not u:
                    break
                print(f"      n{n} uid {u} {labels.get(u)!r}: {[(r['i'], r['name'], 'S' if r['is_source'] else 's', r['wire']) for r in rows if r['name']]}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
