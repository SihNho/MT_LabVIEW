"""ring_p2a_md5 - card 121-2 bookkeeping (offline, no LabVIEW): md5 of the card's artefacts for result_121-2.json."""
import hashlib, os, sys                                                             # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol  # noqa: E402
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
F = ["tools/bench/plan_ring_p2a_make.py", "tools/bench/plan_ring_p2a_in.json", "tools/bench/plan_ring_p2a_pred.json", "tools/bench/plan_ring_p2a.json",
     "tools/recipes/stage_d1_ring_p2a.py", "tools/bench/stage_d1_ring_p2a_scratch.py", "tools/bench/stage_d1_ring_p2a_el.py",
     "tools/bench/stage_d1_ring_p2a_scratch_nosave.log", "tools/bench/scratch_verify/stagexec.ring_p2a_deletes_nosave_20260928_184144.json"]
arts = []
for f in F:
    p = os.path.join(ROOT, f)
    m = hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None
    n = sum(1 for _ in open(p, encoding="utf-8", errors="replace")) if m else 0
    print("{0} {1} lines={2}".format(m, f, n), flush=True)
    arts.append({"path": f, "md5": m})
ok = all(a["md5"] for a in arts)
print(protocol.result_line(protocol.make_result(len(arts) if ok else 0, 0 if ok else 1, None if ok else "missing file", arts)), flush=True)
