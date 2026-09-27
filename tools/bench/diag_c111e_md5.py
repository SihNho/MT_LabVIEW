"""diag_c111e_md5 - card 111-5 P5, OFFLINE: md5 of the card's inputs (byte read, no LabVIEW) and of this card's outputs.
PREDICTION: every input with a card md5 hashes to that md5 (VI b705728a..., graph 8327f974..., rows f4cacbd8..., attribution e0bcf15c...,
plan_l2b1 9fb69b9b..., recipe l2b1 4ef10fc4...)."""
import hashlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_b1_20260927_193100.vi"
WANT = [(VI, "b705728ab0714dc8179fc955283800f9"), ("tools/bench/graph_l2b1_20260927.json", "8327f974cf150146b93b19f10e54afd5"),
        ("tools/bench/facts_c111b_l2b_rows.json", "f4cacbd863c4f367303729234b311f15"), ("tools/bench/facts_c111b_attribution.md", "e0bcf15c2befddede3a419d4e6779fac"),
        ("tools/bench/plan_l2b1.json", "9fb69b9b097603250ca3b9e2f87f322e"), ("tools/recipes/stage_d1_l2b1.py", "4ef10fc4047dbe69e583730ca033ef18")]
OUT = ["tools/bench/plan_l2b2a_in.json", "tools/bench/plan_l2b2a.json", "tools/recipes/stage_d1_l2b2a.py", "tools/bench/cards/split_plan_111_l2b2.md"]
md5 = lambda p: hashlib.md5(open(p if os.path.isabs(p) else os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
ok = 0
for p, w in WANT:
    m = md5(p); ok += m == w
    print("INPUT", "OK  " if m == w else "DIFF", m, w, p)
arts = []
for p in OUT:
    m = md5(p); arts.append({"path": p, "md5": m})
    print("OUTPUT", m, p, sum(1 for _ in open(os.path.join(ROOT, p), encoding="utf-8")), "lines")
bad = len(WANT) - ok
print(protocol.result_line(dict(status="PASS" if not bad else "FAIL", gates={"pass": ok, "fail": bad}, first_fail=None if not bad else "input md5 changed", artefacts=arts)))
