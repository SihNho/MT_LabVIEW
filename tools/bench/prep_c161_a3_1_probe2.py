# ---
# labview: none
# hardware: none
# evidence: tools/bench/prep_c161_a2_1_measure.log
# ---
"""prep_c161_a3_1_probe2 - card 161-a3-1: what the three adopted scratch records (p5s01a/p5s01b/p5s02a) store for a PB replay
(json keys, R keys, PB gate line in the log's last segment). OFFLINE, read-only. PREDICTION: each has real_end_rows + stagexec."""
import os, sys, json                                                                       # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                       # noqa: E402
import protocol                                                                            # noqa: E402

for ln in (9, 10, 11):
    r = [json.loads(x) for x in open(os.path.join(K.BENCH, "adopted_scratch.jsonl"), encoding="utf-8") if x.strip()][ln - 1]
    lg = os.path.join(K.ROOT, r["log"].replace("\\", "/"))
    D = K.jload(lg[:-4] + ".json")
    print("REC", ln, r["stage"], list(r["plan_md5s"].items()), "json keys", sorted(D.keys())[:40])
    for k in ("pb", "PB", "cdiff_rows", "term_identity"):
        if k in D:
            print("  KEY", k, json.dumps(D[k], default=str)[:300])
    seg = open(lg, encoding="utf-8", errors="replace").read().split("BGRUN START")[-1]
    for x in seg.splitlines():
        if "GATE" in x and "| PB " in x or "RECORD PB" in x:
            print("  LOG", x[:600])
    for k, v in D.items():
        if isinstance(v, dict) and ("cdiff_rows" in v or "md5" in v):
            print("  SUB", k, dict((a, (b if not isinstance(b, (list, dict)) else type(b).__name__ + str(len(b)))) for a, b in v.items()))
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
