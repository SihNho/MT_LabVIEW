"""rubric_check - card chat-B2: every rubric regex compiles, and the mechanical scorer applied to each case's own
known_answer hits every must_hit item and no forbidden item (a rubric its own answer key fails is broken).
Also scores fixed wrong-answer probes for the three new cases (each must hit its forbidden item or miss a must_hit).
PREDICTION: 10 cases, all regexes compile; known_answer must mean 1.0 and forbidden 0 on the 10; 3 probes caught. RESULT line.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dec_score as DS  # noqa: E402

doc = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))
cases = {c["id"]: c for c in doc["cases"]}
fails, n = [], 0
for cid, c in cases.items():
    for k in DS.ITEMS:
        for it in c["rubric"].get(k, []):
            for r in it["re"]:
                try:
                    re.compile(r)
                except re.error as e:
                    fails.append("%s %s bad regex %r: %s" % (cid, it["id"], r, e))
    m = DS.mechanical(c["known_answer"], c["rubric"])
    s = DS.combine(m, c["rubric"])
    n += 1
    ok = s["must"] == 1.0 and s["forbidden"] == 0.0
    print("%-4s %-26s key->must %.2f forbidden %.1f bonus %s %s" % ("OK" if ok else "BAD", cid, s["must"], s["forbidden"],
                                                                  s["bonus"], {k: v for k, v in m.items() if v == 0}))
    if not ok and not c.get("clean"):
        fails.append("%s answer key scores must %.2f forbidden %.1f" % (cid, s["must"], s["forbidden"]))
PROBES = {
    "S3-disp-resplit": "The plan is sound; one more complete run after the fixes is the right step.\nVERDICT: keep NEXT\n"
                       "NEXT ACT: run all 47 ops once more.",
    "T2-constvalue-void": "The COM list never reached the constant.\nROOT CAUSE: the write through create_const_loop_term "
                          "dropped the Python list so the constant is empty.\nTEST: re-run with a scalar value.",
    "R3-chat-synthesis": "The numbers are copied correctly from the report.\nDEFECT: minor - wording only.",
}
for cid, txt in PROBES.items():
    s = DS.combine(DS.mechanical(txt, cases[cid]["rubric"]), cases[cid]["rubric"])
    caught = s["forbidden"] > 0 or s["must"] < 1.0
    print("PROBE %-22s must %.2f forbidden %.1f score %.2f %s" % (cid, s["must"], s["forbidden"], s["score"],
                                                                  "caught" if caught else "MISSED"))
    if not caught or s["score"] > 0.5:
        fails.append("probe %s not caught (score %.2f)" % (cid, s["score"]))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                              "gates": {"pass": n + len(PROBES) - len(fails), "fail": len(fails)},
                              "first_fail": fails[0] if fails else None, "artefacts": []}))
sys.exit(1 if fails else 0)
