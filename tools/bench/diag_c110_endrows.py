r"""diag_c110_endrows - card 110-1 P3 OFFLINE: a stagesim summary.json's cdiff rows (sink, S1 before, sim after) at the step named by
argv[2] (default the last), plus the rows that CHANGED between step argv[3] and argv[2]. No LabVIEW.
    py tools/bgrun.py --material --max-min 3 --log <log> -- py -u tools/bench/diag_c110_endrows.py <summary.json> [step] [prev]"""
import json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                                # noqa: E402
S = json.load(open(sys.argv[1], encoding="utf-8"))
steps = S.get("steps") or S.get("step") or []
print("SUMMARY KEYS", sorted(S.keys()), "n steps", len(steps), flush=True)
k = int(sys.argv[2]) if len(sys.argv) > 2 else len(steps) - 1
st = steps[k]
print("STEP", st.get("n"), st.get("op"), st.get("id"), "rows", len(st.get("cdiff_rows") or []), flush=True)
for r in S.get("end_cdiff_rows") or []:
    print("  END {0}".format(json.dumps(r)[:600]), flush=True)
for k2 in ("open_rows_classed", "new_classes", "undecided", "open_rows_match", "open_rows_match_legacy", "first_divergent"):
    print("  {0}: {1}".format(k2.upper(), json.dumps(S.get(k2))[:3000]), flush=True)
if len(sys.argv) > 3:
    pk = set(json.dumps(r, sort_keys=True) for r in steps[int(sys.argv[3])].get("cdiff_rows") or [])
    for r in st.get("cdiff_rows") or []:
        if json.dumps(r, sort_keys=True) not in pk:
            print("  NEW/CHANGED {0}".format(r), flush=True)
print(P.result_line(P.make_result(1, 0, None)), flush=True)
