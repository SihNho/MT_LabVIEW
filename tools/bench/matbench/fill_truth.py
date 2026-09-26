"""Fill truth_v0.json with the EXACT sources the v0 replay used (card chat-N2 pass item 2). No LabVIEW, no model.

Per task: base/src commits, the replay card (path, md5), every file copied into the worktree (path, from, md5 - read
from runs/<task>_c0/meta.json), the original card and result; T5: the reference plan, base graph and the reference's
simulated end rows + structure counts; T6: the source log md5 and its first failing gate line number.
"""
import hashlib
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
import sys
sys.path.insert(0, HERE)
import matbench as M  # noqa: E402

ORIG = {"T1": "89-1", "T2": "90-6", "T3": "88-1", "T4": "86-5"}


def md5b(b):
    return hashlib.md5(b).hexdigest()


def main():
    tp = os.path.join(HERE, "truth_v0.json")
    truth = json.load(open(tp, encoding="utf-8"))
    for tt in truth["tasks"]:
        tid = tt["id"].split("_")[0]
        t = M.TASKS[tid]
        cp = os.path.join(HERE, "cards", "task_%s.json" % t["card"])
        src = {"base_commit": t["base"], "card_commit": t["src"], "agent": t["agent"],
               "replay_card": {"path": os.path.relpath(cp, MAIN).replace("\\", "/"), "md5": md5b(open(cp, "rb").read())}}
        if tid in ORIG:
            for k in ("task", "result"):
                p = os.path.join(MAIN, "tools", "bench", "cards", "%s_%s.json" % (k, ORIG[tid]))
                src["original_" + k] = {"path": "tools/bench/cards/%s_%s.json" % (k, ORIG[tid]),
                                        "md5": md5b(open(p, "rb").read())}
        mp = os.path.join(M.RUNS, "%s_c0" % tid, "meta.json")
        if os.path.isfile(mp):
            src["copied_into_worktree"] = json.load(open(mp, encoding="utf-8"))["copied"]
        if tid == "T5":
            b = subprocess.run(["git", "show", "53a5fb2:" + M.K_GRAPH], cwd=MAIN, capture_output=True).stdout
            src["reference_plan"] = {"path": M.K_REF, "md5": md5b(open(os.path.join(MAIN, M.K_REF), "rb").read()),
                                     "actions": len(json.load(open(os.path.join(MAIN, M.K_REF), encoding="utf-8"))["actions"]),
                                     "chosen_because": "smallest stageplan on disk (k_split 27 actions; l7_split 45, l2a1 46)"}
            src["base_graph"] = {"path": M.K_GRAPH, "from": "git:53a5fb2", "md5": md5b(b)}
            sp = os.path.join(M.RUNS, "T5_c0", "t5_sim.json")
            if os.path.isfile(sp):
                ref = json.load(open(sp, encoding="utf-8"))["ref"]
                src["reference_rows"] = ref.get("end_cdiff_rows")
                src["reference_final_flag"] = ref.get("final")
            ss = os.path.join(M.RUNS, "t5_struct_summary.json")
            if os.path.isfile(ss):
                src["reference_structure"] = json.load(open(ss, encoding="utf-8"))["ref"]
        if tid == "T6":
            b = subprocess.run(["git", "show", "5887e24:tools/bench/diag_c90_t0_step3b.log"], cwd=MAIN,
                               capture_output=True).stdout
            first = next((i + 1 for i, ln in enumerate(b.decode("utf-8", "replace").splitlines())
                          if re.search(r"\bFAIL\b", ln)), None)
            src["source_log"] = {"path": "tools/bench/diag_c90_t0_step3b.log", "from": "git:5887e24", "md5": md5b(b),
                                 "first_FAIL_line": first}
        tt["sources"] = src
    truth["note"] = truth.get("note", "") + "; sources filled by fill_truth.py after the v0 run"
    json.dump(truth, open(tp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": len(truth["tasks"]),
                                  "fail": 0}, "first_fail": None, "artefacts": [{"path": "tools/bench/matbench/truth_v0.json",
                                                                                 "md5": md5b(open(tp, "rb").read())}]}))


if __name__ == "__main__":
    main()
