# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-a4-1.md
# ---
"""diag_c159_a4_1_probe - card 159-a4-1, offline READ-ONLY probe (no LabVIEW, writes nothing): for every stored ring plan
with a `<plan>_pred.json` and its finalized step files, the SIMULATED new-object census (stagesim step_00 -> last step: new
objs by class + new terminals by term_class + new wire uids as Wire) against the pred's census block, filtered to the pred's
classes and unfiltered. Tells which plan can serve as the "fully declared, sim == pred" case of the self-test.
PREDICTION: a table row per plan; no exception. Exists first: stagesim step files (plan finalized.step_files), census_predict."""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import protocol  # noqa: E402


def jl(p):
    with open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8") as f:
        return json.load(f)


def snap(st):
    d = dict((int(o["uid"]), str(o["class"])) for o in st.get("objs") or [])
    for r in st.get("terminals") or []:
        d[int(r["term_uid"])] = str(r.get("term_class") or "Terminal")
        if r.get("wire_uid"):
            d[int(r["wire_uid"])] = "Wire"
    for k in (st.get("diagrams") or {}):
        d.setdefault(int(k), "Diagram")
    return d


n = bad = 0
for pp in sorted(glob.glob(os.path.join(HERE, "bench", "plan_ring_*_pred.json"))):
    plan = pp[:-len("_pred.json")] + ".json"
    if not os.path.isfile(plan):
        continue
    try:
        P, R = jl(plan), jl(pp)
        sf = (P.get("finalized") or {}).get("step_files") or []
        s0, s1 = jl(sf[0]["path"])["state"], jl(sf[-1]["path"])["state"]
    except Exception as e:  # noqa: BLE001
        print("SKIP {0}: {1}".format(os.path.basename(plan), str(e)[:120]), flush=True)
        continue
    a, b = snap(s0), snap(s1)
    new = {}
    for u in set(b) - set(a):
        new[b[u]] = new.get(b[u], 0) + 1
    dec = R.get("census") or {}
    filt = dict((c, k) for c, k in new.items() if c in dec)
    eq = filt == dict((c, int(v)) for c, v in dec.items() if int(v))
    n += 1
    print("ROW {0} overall={1} unpred={2} filtered_eq={3}\n    sim  {4}\n    pred {5}".format(
        os.path.basename(plan), R.get("census_overall"), len(R.get("census_unpredicted") or []), eq,
        json.dumps(new, sort_keys=True), json.dumps(dec, sort_keys=True)), flush=True)
print(protocol.result_line(protocol.make_result(n, bad, None, status="PASS")), flush=True)
