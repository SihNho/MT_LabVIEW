"""Write the six replay cards tools/bench/matbench/cards/task_mb-T<n>.json (card chat-N2, brief item 3).

T1/T3/T4 are the ORIGINAL cards (89-1, 88-1, 86-5) with the replay flags (labview none, gui false, hardware none,
run_vi false, peers [], git_commit false) and the truth file's scope; T2 is 90-6's diagnosis as a read-the-logs card;
T5 (authoring) and T6 (log-reader) are new cards written from truth_v0.json's sources. Run from the project root.
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(HERE, "cards")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
REPLAY = "REPLAY chat-N2: LabVIEW/GUI/hardware/peers/git forbidden (hook); do all offline, report the rest"


def flags(w):
    return {"labview": "none", "gui": False, "hardware": "none", "run_vi": False,
            "write": w + ["tools/bench/cards/**"], "status_edit": False, "git_commit": False, "peers": []}


def orig(cid):
    with open(os.path.join(ROOT, "tools", "bench", "cards", "task_%s.json" % cid), encoding="utf-8") as f:
        return json.load(f)


def cards():
    out = {}
    c = orig("89-1")
    c.update(id="mb-T1", flags=flags(["tools/bench/diag_c89_*", "tools/bench/sim/t0/**", "tools/bench/t0_insitu_89*"]),
             budget={"failures": 2, "minutes": 15}, rules=[REPLAY] + c["rules"],
             outputs=["tools/bench/cards/result_mb-T1.json"])
    out["T1"] = c
    out["T2"] = {
        "schema": "task/1", "id": "mb-T2", "kind": "diagnose",
        "goal": "From the logs only (no rerun): why did card 90-6's two runs both end ExecState 0? Name each run's fault",
        "why": "replay of card 90-6's diagnosis: the faults must be read from the machine's logs, not inferred",
        "inputs": [{"path": p} for p in (
            "tools/bench/cards/task_90-6.json", "tools/bench/cards/result_90-5.json",
            "tools/bench/diag_c90_t0_step3b.log", "tools/bench/diag_c90_t0_step3b_r2.log",
            "tools/bench/diag_c90_t0_step3.py", "tools/bench/diag_c90_t0_step3.log", "tools/bench/t0_sites_s1.json",
            "archive/peer/2026-09-26-c90-t0step3-movewire.md")],
        "pass": ["run 1 (diag_c90_t0_step3b.log): first site whose ExecState went 0, the op, the error it raised, log:line",
                 "run 2 (diag_c90_t0_step3b_r2.log): what went wrong and why, log:line",
                 "which sites (While-body vs For-body) the route worked on, from the logs"],
        "outputs": ["tools/bench/cards/result_mb-T2.json"], "flags": flags(["tools/bench/diag_c90_*"]),
        "budget": {"failures": 2, "minutes": 20},
        "rules": [REPLAY, "no rerun of any script; the logs are the evidence", "facts only; result/1 <=10 facts <=3 open"],
        "advances": ["M8", "M3"]}
    c = orig("88-1")
    c.update(id="mb-T3",
             goal="(A) ONLY, offline desk check: P2 rows sr1_L0/sr2_L0/sr3_L0/tun1/tun2 of the L2-A1 bed vs sim step_*.json",
             pass_=None)
    c.pop("pass_", None)
    c["pass"] = ["5-row table from tools/bench/sim/l2a1/step_*.json: planned source uid, planned sink (owner uid, class,"
                 " term), number of sources and sinks per net, each cited file:line",
                 "tools/bench/stage_d1_l2a1.json's binding for the 5 rows agrees or disagrees with the sim, cited",
                 "parts (B) and (C) of the original card are OUT of this replay"]
    c.update(flags=flags(["tools/bench/p2check_l2a1_88*", "tools/bench/diag_c88_*"]),
             budget={"failures": 2, "minutes": 20}, outputs=["tools/bench/cards/result_mb-T3.json"],
             rules=[REPLAY, "READ-ONLY desk check; no LabVIEW read of the bed", "report MEASUREMENTS only",
                    "result/1 <=10 facts <=3 open"])
    out["T3"] = c
    c = orig("86-5")
    c.update(id="mb-T4", goal="L2-A1 PRE-RUN ONLY of tools/recipes/stage_d1_l2a1.py (offline, COM stubbed): it must "
                              "PASS so the launch gate would accept. NO stage run",
             outputs=["tools/bench/prerun_l2a1_mb*", "tools/bench/cards/result_mb-T4.json"],
             budget={"failures": 2, "minutes": 20},
             flags=flags(["tools/bench/prerun_l2a1_*", "tools/bench/stage_runs.jsonl", "tools/bench/sim/l2a1/**",
                          "tools/bench/jev_gate.log", "tools/bench/jev_usage.jsonl"]),
             rules=[REPLAY, "PRE-RUN ONLY; do NOT edit stage_d1_l2a1.py or stagexec.py",
                    "a gate refusal is reported with its message, not routed around", "result/1 <=10 facts <=3 open"])
    c["pass"] = ["pre-run PASSES: command, log path, its RESULT line and gate counts",
                 "a failing pre-run gate: the gate, its cause, and what makes it pass without editing the recipe/stagexec",
                 "D1_k md5 unchanged (never opened)"]
    out["T4"] = c
    out["T5"] = {
        "schema": "task/1", "id": "mb-T5", "kind": "build",
        "goal": "AUTHOR stage K's stageplan/1 (design brief_mb-T5.md) and simulate it with tools/stagesim.py to the rows "
                "the design leaves open",
        "why": "replay of cycle 79's stage-K plan authoring: the plan file is the only thing a stage run executes (PD178(f))",
        "inputs": [{"path": p} for p in (
            "tools/bench/cards/brief_mb-T5.md", "docs/protocol/stageplan.json", "tools/bench/stageplan_l7_split.json",
            "tools/bench/graph_k_s4_20260925.json", "tools/bench/graph_loops_k_s4_20260925.json", "tools/stagesim.py")],
        "pass": ["tools/bench/matbench_out/stageplan_k_split.json exists and is valid stageplan/1 (example: "
                 "tools/bench/stageplan_l7_split.json)",
                 "py tools/stagesim.py simulate <it> tools/bench/graph_k_s4_20260925.json --out-root "
                 "tools/bench/matbench_out/sim --plan-out tools/bench/matbench_out: no failed action",
                 "every end_cdiff row is one the design leaves open (PD177(e), 178(c)) or already in the base graph; "
                 "list them in facts"],
        "outputs": ["tools/bench/matbench_out/**", "tools/bench/cards/result_mb-T5.json"],
        "flags": flags(["tools/bench/matbench_out/**"]), "budget": {"failures": 2, "minutes": 30},
        "rules": [REPLAY, "write the plan with the Write tool, never a heredoc",
                  "uids and terminal names come from the graph files, never guessed", "result/1 <=10 facts <=3 open"],
        "advances": ["M3", "R1"]}
    out["T6"] = {
        "schema": "task/1", "id": "mb-T6", "kind": "read-log",
        "goal": "Read-only: the FIRST failing gate line of tools/bench/diag_c90_t0_step3b.log (label, op, error, values, "
                "line) + its ExecState-per-site table",
        "why": "replay of the log-reader role on a real failing bgrun log with a known first failing gate",
        "inputs": [{"path": "tools/bench/diag_c90_t0_step3b.log"}],
        "pass": ["first failing gate: label, op, error code, log line", "<= 25 lines of facts; no diagnosis beyond the log"],
        "outputs": ["tools/bench/cards/result_mb-T6.json"], "flags": flags([]), "budget": {"failures": 1, "minutes": 10},
        "rules": [REPLAY, "read-only: the only file you write is your result card", "facts only, each with file:line"],
        "advances": ["M8"]}
    return out


def main():
    os.makedirs(CARDS, exist_ok=True)
    for k, v in cards().items():
        with open(os.path.join(CARDS, "task_mb-%s.json" % k), "w", encoding="utf-8") as f:
            json.dump(v, f, ensure_ascii=False, indent=1)
    print("wrote", sorted(cards()))


if __name__ == "__main__":
    main()
