r"""jev_ladder_remeasure.py - re-measure the REVIEW LADDER's `our-script-bug` act threshold after adding the cycle
68-70 failures to the labelled set (user 2026-09-24 03:5x, "the verdict drives the next action"). MEASURES ONLY:
jev_gate.LADDER_P is NOT changed here - the judgement session decides.

NO LabVIEW. Reads .log/.md off disk; Jev calls through tools/jev.py only (jev_gate.ladder_classify,
jev_gaterow.verdicts_for). No COM, no VISA, no motor, no camera, no GUI, no .vi. Nothing is written into
archive/peer/ or tools/bench/jev_gate.log (GATE_LOG is redirected to a temp dir; the ladder is classified directly,
the discharge is not run).

WHAT ALREADY EXISTS (checked): tools/bench/jev_wave2a_trials.py cell C is the original 16-item measurement;
`resolve_trigger` is imported from it, and the classify call is the same (n=5 consensus, gate rows 4x2, the 5
newest adversary reviews before the review's date). This file adds: the +4 items, 2 repetitions per item, and a
threshold sweep over the act rule `class == our-script-bug and p >= t`.

LABELS ADDED (true class = how each was actually resolved):
  c68-h6    q_m4_copy_probe.log     our-script-bug: stagekit.py glob read only the claudeDev top folder (review
                                    archive/peer/2026-09-24-c68-h6-fixture-listing.md; fixed in stagekit.py)
  c68-p6b   stage_d1_m4a.log        our-script-bug: vigraph's name-keyed diff + equal-TOP pairing - a reader
                                    artefact; the machine pairs were intact (…-c68-m4a-p6b-rename.md, U1-U6)
  c68-p6d   q_m4_iterlocal.log      our-script-bug: the stray node left by our step; ExecState 1 after the purge,
                                    folded into the recipe as a purge + recorded rows (…-c68-p6d-stray-invoke.md)
  c70-p1    p1_c70_resolve.log run 0  our-script-bug: gate A3 compared one tunnel uid where the measured wire had 2
                                    candidates; the gate was corrected and run 2, 57 s later, passed 7/0 with no
                                    review (docs/d1-loop12-17-split-plan.md:98-101). The brief's
                                    `p1_c70_resolve_run1.log` no longer exists; its run is run 0 of this log.

PREDICTION CONTRACT
  R1 every item resolves to a log and run                                  -> 20/20
  R2 every item gets a class and p on both repetitions                     -> 40/40 (REPORTED if short)
  R3 per threshold t in (0.80, 0.70, 0.65): acts, correct acts, DANGEROUS acts (truth new-problem classified
     our-script-bug at p >= t on ANY repetition), and already-reviewed items that would skip their discharge
     -> REPORTED, not gated; the held-out subset is the 4 items added today (never seen when 0.80 was set)
"""
import json
import os
import sys
import tempfile
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
PEER = os.path.join(ROOT, "archive", "peer")
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import jev                                   # noqa: E402
import jev_gate                              # noqa: E402
import jev_gaterow                           # noqa: E402
from jev_wave2a_trials import resolve_trigger   # noqa: E402

SET = os.path.join(HERE, "jev_ladder_set.json")
OUT = os.path.join(HERE, "jev_ladder_remeasure.json")
THRESHOLDS = (0.80, 0.70, 0.65)
REPS = 2
NEW_ITEMS = [
    {"review": "2026-09-24-c68-h6-fixture-listing.md", "label": "our-script-bug", "added": "2026-09-24",
     "why": "stagekit.py listed only the claudeDev top folder (glob without recursive) - our Python's expectation; "
            "fixed in stagekit.py fixtures_check()/fixture_listing()."},
    {"review": "2026-09-24-c68-m4a-p6b-rename.md", "label": "our-script-bug", "added": "2026-09-24",
     "why": "P6b's name-keyed diff and vigraph's equal-TOP pairing were a reader artefact; uid-keyed reads showed "
            "the machine's pairs intact (q_m4a_diffuid.log U1-U6)."},
    {"review": "2026-09-24-c68-p6d-stray-invoke.md", "label": "our-script-bug", "added": "2026-09-24",
     "why": "ExecState 0 after connect cleared by purging the stray node our step left; resolved by a purge and "
            "recorded rows in the recipe, no machine claim changed."},
    {"review": "", "log": "p1_c70_resolve.log", "run": 0, "label": "our-script-bug", "added": "2026-09-24",
     "why": "Gate A3 compared one tunnel uid where the wire had two candidates; the gate was corrected and run 2 "
            "(57 s later) passed 7/0 with no review. Was p1_c70_resolve_run1.log in jev_gate.log."},
]


def item_id(it):
    return it.get("review") or ("%s[run %s]" % (it.get("log"), it.get("run")))


def load_set():
    doc = json.load(open(SET, encoding="utf-8"))
    have = {item_id(i) for i in doc["items"]}
    added = [dict(i) for i in NEW_ITEMS if item_id(i) not in have]
    if added:
        doc["items"].extend(added)
        doc["n"] = len(doc["items"])
        doc.setdefault("amended", []).append(
            "2026-09-24: +%d items (cycles 68-70, all resolved as our own script fixes) by "
            "tools/bench/jev_ladder_remeasure.py; items may carry `log`/`run` instead of a review" % len(added))
        with open(SET, "w", encoding="utf-8") as fh:
            json.dump(doc, fh, ensure_ascii=False, indent=1)
    return doc, len(added)


def resolve(it):
    if it.get("log"):
        logp = os.path.join(HERE, it["log"])
        txt = open(logp, encoding="utf-8", errors="replace").read()
        import re
        starts = re.findall(r"^BGRUN START (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", txt, re.M)
        run = it.get("run", -1)
        epoch = time.mktime(time.strptime(starts[run], "%Y-%m-%d %H:%M:%S")) + 60 if starts else time.time()
        if run == len(starts) - 1:
            run = -1
        return it["log"], run, epoch
    return resolve_trigger(os.path.join(PEER, it["review"]))


def main():
    print("=== JEV LADDER RE-MEASUREMENT (threshold sweep, LADDER_P unchanged = %.2f) ===" % jev_gate.LADDER_P)
    if not jev.get_key():
        print("NO KEY - nothing measured")
        return 1
    doc, nadd = load_set()
    items = doc["items"]
    print("set: %d items (%d added now)" % (len(items), nadd))
    tmp = tempfile.mkdtemp(prefix="jev_remeasure_")
    jev_gate.GATE_LOG = os.path.join(tmp, "scratch_gate.log")
    rows, unresolved = [], []
    for it in items:
        name, run, epoch = resolve(it)
        if not name:
            unresolved.append(item_id(it))
            print("  MISS %s" % item_id(it))
            continue
        logp = os.path.join(HERE, name)
        fs = jev.summarise_failure(logp, run_index=run)
        grows = jev_gaterow.verdicts_for(logp, run_index=run, max_rows=4, n=2)
        recent = jev_gate.recent_adversary_reviews(jev_gate.N_RECENT_REVIEWS, before=epoch - 1)
        rtxt = "\n".join("- %s" % os.path.basename(x) for x in recent)[:1200]
        reps = []
        for _ in range(REPS):
            cls, p, sp = jev_gate.ladder_classify(fs, grows, rtxt, purpose="ladder-remeasure", n=5)
            reps.append((cls, p))
        row = {"id": item_id(it), "log": name, "run": run, "truth": it["label"], "new": it.get("added") == "2026-09-24",
               "reps": reps}
        rows.append(row)
        print("  %-3s %-46s %-26s truth=%-22s %s" % (
            "NEW" if row["new"] else "", row["id"][:46], "%s[%s]" % (name[:20], run), it["label"],
            "  ".join("%s %.3f" % (c, p) if c else "None" for c, p in reps)))
        sys.stdout.flush()
    print("R1 resolved %d/%d%s" % (len(rows), len(items), ("  unresolved: %s" % unresolved) if unresolved else ""))
    ans = sum(1 for r in rows for c, p in r["reps"] if c is not None)
    print("R2 answered %d/%d classifications" % (ans, len(rows) * REPS))

    def sweep(sub, label):
        print("\n=== %s (n=%d) - 3-way argmax accuracy: %d/%d classifications" % (
            label, len(sub), sum(1 for r in sub for c, p in r["reps"] if c == r["truth"]), len(sub) * REPS))
        out = {}
        for t in THRESHOLDS:
            acts = [(r, c, p) for r in sub for c, p in r["reps"] if c == "our-script-bug" and p is not None and p >= t]
            good = sum(1 for r, c, p in acts if r["truth"] == "our-script-bug")
            danger_items = sorted({r["id"] for r, c, p in acts if r["truth"] == "new-problem"})
            arc_items = sorted({r["id"] for r, c, p in acts if r["truth"] == "already-reviewed-class"})
            sb = [r for r in sub if r["truth"] == "our-script-bug"]
            recall = sum(1 for r in sb for c, p in r["reps"] if c == "our-script-bug" and p >= t)
            print("  t=%.2f  acts=%d (correct %d)  script-bug recall %d/%d  DANGEROUS new-problem->script-bug items=%d %s"
                  "  already-reviewed->script-bug items=%d %s" % (
                      t, len(acts), good, recall, len(sb) * REPS, len(danger_items), danger_items,
                      len(arc_items), arc_items))
            out["%.2f" % t] = {"acts": len(acts), "correct": good, "recall": recall, "of": len(sb) * REPS,
                               "dangerous": danger_items, "already_reviewed_skips": arc_items}
        return out

    res = {"all": sweep(rows, "ALL ITEMS"), "held_out": sweep([r for r in rows if r["new"]], "HELD-OUT (the +4)"),
           "old16": sweep([r for r in rows if not r["new"]], "ORIGINAL 16")}
    maxp_np = max([p for r in rows if r["truth"] == "new-problem" for c, p in r["reps"] if c == "our-script-bug"]
                  or [0.0])
    print("\nhighest p at which a TRUE new-problem was classified our-script-bug: %.3f" % maxp_np)
    json.dump({"ts": time.strftime("%Y-%m-%d %H:%M:%S"), "rows": rows, "sweep": res,
               "max_p_newproblem_as_scriptbug": maxp_np, "ladder_p_unchanged": jev_gate.LADDER_P},
              open(OUT, "w", encoding="utf-8"), indent=1)
    print("JSON: %s" % os.path.relpath(OUT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
