r"""c20_release_probe.py - does the cycle-20 step-2 prior-art release VALIDATE?

Read-only. No LabVIEW, no motor, no serial, no camera. It asks the two functions the LAUNCH GATE itself uses -
`guard_cycle.released_slugs()` (which slugs does this review release?) and `stop_record._released()` (does the
standing stop record see a valid release?) - and prints their answers verbatim, plus `fixed_claim()` per cited
path so a REJECTED line names the condition it failed.

  MATERIAL=1 py tools/bench/c20_release_probe.py
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_cycle as G          # noqa: E402
import stop_record as S          # noqa: E402

REVIEW = os.path.join(ROOT, "archive", "peer", "2026-09-18-priorart-fstunnel-reader.md")
RECIPE = os.path.join(ROOT, "tools", "recipes", "build_opfstunnel" + "term_v0.py")

body = open(REVIEW, "r", encoding="utf-8").read()
ok, bad = G.released_slugs(REVIEW, body)
print("review        :", os.path.relpath(REVIEW, ROOT))
print("review_time   :", G.review_time(REVIEW, body))
print("RELEASED SLUGS: %d -> %s" % (len(ok), sorted(ok)))
print("REJECTED      : %d -> %s" % (len(bad), bad))
print("fixed_claim(recipe) (claimed, released, why):", G.fixed_claim(REVIEW, body, RECIPE))

for rec in S.load_records():
    if "fstunnel" not in (rec.get("recipe_path") or ""):
        continue
    rel, line, why = S._released(rec)
    print("\nSTOP RECORD   :", json.dumps({k: rec.get(k) for k in
                                           ("recipe_path", "review_file", "verdict", "reviewed_sha256",
                                            "released")}, indent=1)[:600])
    print("_released     :", rel)
    print("release line  :", line)
    print("why not       :", why)
