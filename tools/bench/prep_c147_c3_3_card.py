# ---
# labview: none
# hardware: none
# ---
import hashlib
import json
import os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def inp(p):
    return {"path": p, "md5": hashlib.md5(open(p, "rb").read()).hexdigest()}


L = "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\"
c = {
    "schema": "task/1", "id": "147-c3-3", "kind": "build",
    "goal": "PD356(e)/PD357(f): ONE s06 scratch (new gate API) on a NEW byte copy of adopted s05 3f9ac26b, ops 1..21; on structural PASS adopt D1_ring_p4s06_<stamp>.vi + final EL + fresh load + graph + load_by_vi",
    "why": "Cycle 147 pass items 7-11. 147-a1-8 built the right graph but D/TD/PB failed on LabVIEW input renames; licence renames + recipe on the new gate API are now offline-verified (147-c3-2).",
    "retry_of": "stage_d1_ring_p4_s06v18_scratch.py",
    "retry_of_card": "147-a1-8",
    "inputs": [inp(p) for p in (
        "tools/bench/cards/brief_147-c3-3.md", "tools/bench/cards/brief_147-a1-8.md", "tools/bench/cards/brief_147-a1-4.md",
        "tools/bench/diag_c147_a2_1_facts.md", "tools/bench/diag_c147_c3_2_facts.md",
        "tools/bench/plan_ring_p4_s06v18.json", "tools/bench/plan_ring_p4_s06v18_pred.json", "tools/bench/plan_ring_p4_s06v18_in.json",
        "tools/bench/plan_ring_p4_s06v18_licence.json", "tools/recipes/stage_d1_ring_p4_s06v18.py",
        "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py", "tools/stagekit.py", "tools/stagexec.py", "tools/gscript.py",
        "tools/bench/memory_model.json", "tools/bench/diag_c147_a1_1_adopt.py", "tools/bench/diag_c147_a1_1_mkgraph.py",
        "tools/bench/diag_c147_a1_1_graph.py")],
    "pass": [
        "ONE scratch, NEW byte copy of 3f9ac26b, ops 1..21: E1 real == sim at every op; SG sink gate PASS with readback; prim, D/TD/PB (renames licensed), licence PASS; peak <= 680",
        "EL ADVISORY: total + per-class vs pred 55 and the s05 read; fails only on an unseen class or |total diff| > 3",
        "Structural PASS => adopted D1_ring_p4s06_<stamp>.vi + md5, final EL expected file, per-class EL diff explained, fresh-instance load MB, graph json + md5",
        "memory_model.json: ONLY one load_by_vi entry for the adopted md5 (key-by-key diff); no limit or coefficient changed",
        "3f9ac26b, 95e408ff, 282301ca, 39511877 unchanged; handles flat; LabVIEW closed and verified gone"],
    "outputs": [
        L + "D1_ring_p4s06_<stamp>.vi",
        "tools/bench/graph_ring_p4s06_<stamp>.json",
        "tools/bench/errorlist_expected_D1_ring_p4s06_<stamp>.json",
        "tools/bench/diag_c147_c3_3_facts.md"],
    "flags": {"labview": "build", "gui": True, "hardware": "none", "run_vi": False,
              "write": ["tools/bench/diag_c147_c3_3*", "tools/bench/launch_*c147*", "tools/bench/scratch_*c147*",
                        "tools/bench/plan_ring_p4_s06v18_pred.json", "tools/bench/graph_ring_p4s06_*", "tools/bench/errorlist_*p4s06*",
                        "tools/bench/adopted_scratch.jsonl", "tools/bench/memory_model.json", "tools/bench/gate_fp_queue.jsonl",
                        "tools/bench/sim/ring_p4_s06v18/**", "tools/bench/prerun_records.jsonl", "tools/bench/jev_*", "archive/peer/**"],
              "status_edit": False, "git_commit": False, "peers": ["hypothesis", "priorart"]},
    "budget": {"failures": 2, "minutes": 120},
    "advances": ["M3", "R1"],
    "requires": [
        {"kind": "file", "name": "D1_ring_p4s05_20261008_002621.vi", "where": L[:-1]},
        {"kind": "file", "name": "tools/errorlist_check.py"},
        {"kind": "file", "name": "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py"}],
    "rules": [
        "Bed, s03, s04, adopted s05 never opened for editing; edit a byte copy only",
        "ONE scratch; RETURN at first result differing from prediction; no retry",
        "No stage-tool edits; no other plan; no motor or camera"]}
json.dump(c, open("tools/bench/cards/task_147-c3-3.json", "w"), indent=1)
print("wrote", c["id"])
