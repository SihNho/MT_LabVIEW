"""prerun_fix95_rerun - card 95-1: re-run offline the dry runs that crashed with KeyError 'terminals'
(prerun_records.jsonl:17 stage_replay_swap, :24/:33 stage_d1_k, :65 diag_c94c_f7911) plus the explicit
`--dry ... --graph graph_s1_20260924.json` case. COM stubbed by stage_prerun; --no-record so no launch evidence is
written. Prediction: no run prints KeyError; each prints its RESULT line (PASS or a named FAIL)."""
import os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
RUNS = [
    ("rec17 stage_replay_swap (no --graph)", ["tools/recipes/stage_replay_swap.py"]),
    ("rec24/33 stage_d1_k (no --graph)", ["tools/recipes/stage_d1_k.py"]),
    ("rec65 diag_c94c_f7911 (no --graph)", ["tools/bench/diag_c94c_f7911.py"]),
    ("S1 explicit --graph graph_s1_20260924", ["tools/bench/diag_c94c_f7911.py", "--graph", "tools/bench/graph_s1_20260924.json"]),
]
bad = []
for label, args in RUNS:
    cmd = ["py", "-u", "tools/stage_prerun.py", "--dry"] + args + ["--no-record"]
    p = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
    out = p.stdout + p.stderr
    lines = [l for l in out.splitlines() if l.strip()]
    ke = "KeyError" in out
    print("=== %s | rc=%s | KeyError=%s" % (label, p.returncode, ke))
    for l in lines[-3:]:
        print("   ", l[:400])
    if ke:
        bad.append(label)
print('RESULT {"schema":"result-line/1","status":"%s","gates":{"pass":%d,"fail":%d},"first_fail":%s,"artefacts":[]}'
      % ("PASS" if not bad else "FAIL", len(RUNS) - len(bad), len(bad), "null" if not bad else '"%s"' % bad[0]))
