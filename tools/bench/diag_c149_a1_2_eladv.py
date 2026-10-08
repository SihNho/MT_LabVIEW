# ---
# labview: none
# hardware: none
# ---
"""Card 149-a1-2 (OFFLINE, no LabVIEW): EL-ADVISORY of the s06 Error List read, the SAME arithmetic as
tools/recipes/stage_d1_ring_p4_s06v18_scratch.py:84-129 (OCR_ALIASES, EL_TOTAL_TOL 3, norm_ocr, elcls, el_advisory, print form) copied
verbatim. Why a copy: the recipe's own `--el-advisory` mode is refused by guard_bash's launch gate citing the OLD 12:52 failed segment of
the appended scratch log (gate FP fp-62, tools/bench/gate_fp_queue.jsonl); importing the recipe would import stagekit/gscript.
Only tools/elrule.py (offline) and the plan/pred json are read. The pred's plan-md5 key is checked the same way (plain md5 of the plan file).
PREDICTION (hand count from the read json raws): total 51 vs pred 55, diff -4 -> rc 1 RETURN; no unseen class."""
import collections
import hashlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import elrule as ELR  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
PLAN = os.path.join(B, "plan_ring_p4_s06v18.json")
PREDF = os.path.join(B, "plan_ring_p4_s06v18_pred.json")
OCR_ALIASES = (("vl", "vi"), ("v", "y"))
EL_TOTAL_TOL = 3
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()  # noqa: E731


def norm_ocr(s):
    k = re.sub(r"[^a-z0-9]", "", (s or "").lower())
    for a, b in OCR_ALIASES:
        k = k.replace(a, b)
    return k


def elcls(it):
    c = ELR.item_class("{0} {1}".format(it.get("raw", ""), it.get("detail", "")))
    if c:
        return c
    k = norm_ocr(it.get("raw"))
    if "unwiredorbadterminal" in k or ("requiredinput" in k and "notwired" in k):
        return "input"
    return "other:" + k


def el_advisory(items):
    pr = json.load(open(PREDF, encoding="utf-8"))
    el = pr.get("errorlist") or {}
    pc = el.get("per_class") or {}
    if (pr.get("plan") or {}).get("md5") != md5(PLAN):
        return 2, {"why": "pred not keyed to plan md5"}
    if not pc.get("predicted"):
        return 2, {"why": "pred has no errorlist.per_class"}
    start, want = pc["start_read"]["classes"], pc["predicted"]
    got = collections.Counter(elcls(x) for x in items or [])
    diff = dict((c, got.get(c, 0) - want.get(c, 0)) for c in sorted(set(got) | set(want)) if got.get(c, 0) != want.get(c, 0))
    unseen = sorted(c for c in got if c not in start and c not in want)
    td = len(items or []) - int(el["predicted_total"])
    rc = 1 if (unseen or abs(td) > EL_TOTAL_TOL) else 0
    return rc, {"read_total": len(items or []), "pred_total": el["predicted_total"], "total_diff": td, "per_class_diff": diff, "unseen": unseen,
                "verdict": "RETURN" if rc else "RECORDED", "got": dict(sorted(got.items()))}


items = json.load(open(os.path.join(ROOT, sys.argv[1]), encoding="utf-8")).get("items") or []
rc, rep = el_advisory(items)
print("EL-ADVISORY total read {0} pred {1} diff {2:+}; per-class diff (read - pred) {3}; unseen classes {4}; verdict {5} rc {6}".format(
    rep.get("read_total"), rep.get("pred_total"), rep.get("total_diff", 0), json.dumps(rep.get("per_class_diff"), sort_keys=True),
    rep.get("unseen"), rep.get("verdict", rep.get("why")), rc), flush=True)
print("EL-CLASSES read {0}".format(json.dumps(rep.get("got"), sort_keys=True)), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if rc == 0 else "FAIL", "gates": {"pass": int(rc == 0), "fail": int(rc != 0)},
                              "first_fail": None if rc == 0 else "EL-ADVISORY rc {0}".format(rc), "artefacts": []}), flush=True)
sys.exit(rc)
