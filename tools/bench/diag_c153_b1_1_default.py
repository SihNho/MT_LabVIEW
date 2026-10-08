# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_153-b1-1.md
# ---
"""diag_c153_b1_1_default - card 153-b1-1: the DEFAULT stagesim replay of plan_ring_p4_s09v18.json (9d622c95) on the s08 END graph
graph_ring_p4s08_20261009_033522.json (44858dbf, no fs_owner_read), into a temp dir (nothing under tools/bench is written except the
json named below). Run with the UNEDITED stagesim (128bacfb) to record today's refusal; the self-test compares against it.
PREDICTION: failed at step 1 (op 185 p4_x_n2_order) with the _diag_chain text naming FS #29721 UNMEASURED; final False."""
import json, os, sys, tempfile                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS, protocol as P                                                         # noqa: E401,E402
tmp = tempfile.mkdtemp(prefix="c153b1_default_")
S = SS.simulate(os.path.join(HERE, "plan_ring_p4_s09v18.json"), os.path.join(HERE, "graph_ring_p4s08_20261009_033522.json"),
                out_root=os.path.join(tmp, "sim"), plan_out_dir=tmp, log=print)
rec = {"stagesim_md5": SS.md5_file(os.path.join(ROOT, "tools", "stagesim.py")), "failed": S["failed"], "final": S["final"]}
print("  FACT  {0}".format(json.dumps(rec)), flush=True)
with open(os.path.join(HERE, "diag_c153_b1_1_default_before.json"), "w", encoding="utf-8") as f:
    json.dump(rec, f, indent=1)
ok = bool(S["failed"]) and S["failed"]["n"] == 1 and "29721" in S["failed"]["error"] and not S["final"]
print(P.result_line(P.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "default replay did not refuse at step 1")))
