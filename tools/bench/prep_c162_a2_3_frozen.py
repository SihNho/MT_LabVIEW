# ---
# labview: none
# hardware: none
# offline-args: before
# evidence: tools/bench/cards/brief_162-a2-3.md
# ---
r"""prep_c162_a2_3_frozen - card 162-a2-3 step 6 (OFFLINE): md5 snapshot of the files this card must NOT change (plan / licence / pred / EL json,
the four stage tools, recipes, hooks). `before` writes prep_c162_a2_3_frozen_before.json; `after` compares and gates equality.
Shared calls: invcheck.snapshot_files / Gates / md5 (no new logic).
PREDICTION CONTRACT: before F0 snapshot written (> 100 files); after F1 every file's md5 == before, no file added or removed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c162_a2_3_frozen_before.log -- py -u tools/bench/prep_c162_a2_3_frozen.py before"""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import invcheck as IC                                                                       # noqa: E402

GLOBS = ["tools/bench/plan_*.json", "tools/bench/errorlist_expected_*.json", "tools/stagekit.py", "tools/stagexec.py", "tools/stagesim.py",
         "tools/stage_prerun.py", "tools/recipes/**/*.py", "tools/hooks/**/*.py"]
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c162_a2_3_frozen_before.json")
mode = (sys.argv[1:] or ["before"])[0]
g = IC.Gates()
now = IC.snapshot_files(GLOBS)
if mode == "before":
    json.dump({"globs": GLOBS, "files": now}, open(SNAP, "w", encoding="utf-8"), indent=1)
    g("F0 before snapshot written: {0} files".format(len(now)), len(now) > 100, len(now))
else:
    was = json.load(open(SNAP, encoding="utf-8"))["files"]
    diff = sorted(k for k in set(was) | set(now) if was.get(k) != now.get(k))
    g("F1 after == before: {0} files, {1} differ".format(len(now), len(diff)), not diff, diff[:20])
print("FACT snapshot {0} md5 {1}".format(os.path.relpath(SNAP, ROOT), IC.md5(SNAP)), flush=True)
print(g.result([{"path": "tools/bench/prep_c162_a2_3_frozen_before.json", "md5": IC.md5(SNAP)}]), flush=True)
sys.exit(1 if g.failed else 0)
