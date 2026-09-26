"""make truth_v1.json from truth_v0.json (card chat-N3, brief items 1-4). Pure JSON edit, no model.

    py tools/bench/matbench/make_truth_v1.py

v1 changes: conditions = claude-opus-5-5 low/medium/high/max (agent material, the v0 c0 shape); repeats 2; parallel 3;
cost guard $120. T1: the facts_all WORDING group ['no LabVIEW run', ...] is replaced by the BEHAVIOUR group
(result card cost.labview_runs == 0 and no LabVIEW.exe in any cell_guard-logged command); FlatSequence stays required;
'9 of 11' becomes partial-only; the workaround rule stays. T5: score = t5_struct jaccard vs the reference (1 when
equal). T2/T3/T4/T6 unchanged.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    t = json.load(open(os.path.join(HERE, "truth_v0.json"), encoding="utf-8"))
    t["schema"] = "matbench-truth/1"
    t["note"] = "chat-N3 v1: derived from truth_v0.json by make_truth_v1.py (T1 behaviour group, T5 struct jaccard)"
    t["conditions"] = [{"agent": "material", "model": "claude-opus-5-5", "effort": e}
                       for e in ("low", "medium", "high", "max")]
    t["repeats"], t["parallel"], t["cost_guard_usd"] = 2, 3, 120.0
    t["score"]["v1"] = ["T1: behaviour group labview_runs==0 replaces the wording group; '9 of 11' partial-only",
                        "T5: score = t5_struct jaccard (1.0 when structurally equal to the reference)",
                        "partial_only groups count in partial, never in score"]
    for x in t["tasks"]:
        ex = x["expect"]
        if x["id"].startswith("T1"):
            ex.pop("facts_all", None)
            ex["behaviour"] = ["labview_runs_zero"]
            ex["facts_any"] = [["FlatSequence", "flat-sequence", "frame-move"]]
            ex["partial_only"] = [["9 of 11", "9/11"]]
        if x["id"].startswith("T5"):
            ex["struct"] = "jaccard"
            ex.pop("mechanical", None)
    with open(os.path.join(HERE, "truth_v1.json"), "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=1)
    print("wrote truth_v1.json tasks %d conditions %d" % (len(t["tasks"]), len(t["conditions"])))
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0},
                                   "first_fail": None, "artefacts": [{"path": "tools/bench/matbench/truth_v1.json"}]}))


if __name__ == "__main__":
    main()
