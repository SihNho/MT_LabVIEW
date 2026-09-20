r"""probe_flatseq_offline3.py - OFFLINE: does the cached node/terminal census cover diagram 10, and where is
uid 44036 in it? Feeds M2's walk so the machine work is one pass. No LabVIEW, no COM, no serial.

PREDICTION: main_vi_nodeterms.json has a 'diagrams' key covering diagram 10, and exactly one node there has
uid 44036 with several non-source terminals carrying non-zero wire uids.
"""
import json
import os
import sys

BENCH = os.path.dirname(os.path.abspath(__file__))


def main():
    p = os.path.join(BENCH, "main_vi_nodeterms.json")
    d = json.load(open(p, encoding="utf-8"))
    dg = d["diagrams"]
    print(f"vi={d.get('vi')}", flush=True)
    print(f"diagrams cached: {len(dg)}  keys sample={sorted(dg, key=lambda k: int(k))[:15]}", flush=True)
    print(f"max diagram key = {max(int(k) for k in dg)}", flush=True)
    d10 = dg.get("10")
    print(f"\ndiagram 10 present={d10 is not None}", flush=True)
    if d10:
        print(f"   owner={d10.get('owner')!r} nodes={len(d10.get('nodes', []))}", flush=True)
        for nd in d10.get("nodes", []):
            print(f"   n={nd['n']:3d} uid={nd['uid']:6d} terms={len(nd.get('terms', []))}", flush=True)
    # locate 44036 anywhere
    hits = []
    for k, v in dg.items():
        for nd in v.get("nodes", []):
            if nd.get("uid") == 44036:
                hits.append((k, nd))
    print(f"\nuid 44036 found in {len(hits)} diagram(s)", flush=True)
    for k, nd in hits:
        print(f"   diagram {k} node index {nd['n']} owner={dg[k].get('owner')!r}", flush=True)
        for t in nd.get("terms", []):
            print(f"      T[{t['i']:2d}] {t['name']!r:34.34} is_source={t['is_source']} wire={t['wire']} "
                  f"errs={t['errs']}", flush=True)
        with open(os.path.join(BENCH, "probe_flatseq_44036.json"), "w", encoding="utf-8") as f:
            json.dump({"diagram": int(k), "node_index": nd["n"], "uid": nd["uid"],
                       "owner": dg[k].get("owner"), "terms": nd.get("terms", [])}, f, indent=1)
    print("\nOFFLINE3 DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
