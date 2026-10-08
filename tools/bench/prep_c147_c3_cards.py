# ---
# labview: none
# hardware: none
# ---
import hashlib
import json
import os

os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def inp(p):
    return {"path": p, "md5": md5(p)}


PIN = [inp(p) for p in ("tools/stagekit.py", "tools/stagexec.py", "tools/gscript.py", "tools/bench/memory_model.json")]


def flags(lv, w):
    return {"labview": lv, "gui": False, "hardware": "none", "run_vi": False, "write": w, "status_edit": False, "git_commit": False, "peers": []}


c1 = {
    "schema": "task/1", "id": "147-c3-1", "kind": "build",
    "goal": "selftest_stagekit.py case J also stubs create_local_read (no other line); selftest_stagekit on 06b8d844 with COM blocked = 0 fails, 0 COM calls",
    "why": "PD357(c): 147-b1-4 showed pre-edit and new stagekit give identical 51/0 with COM blocked, so the J1 COM call (stagekit.py:794) is a stale self-test stub, not a regression.",
    "inputs": [inp(p) for p in ("tools/bench/cards/brief_147-c3-1.md", "tools/bench/diag_c147_b1_4_facts.md", "tools/bench/diag_c147_b1_4_run.py",
                               "tools/bench/selftest_stagekit.py", "tools/bench/selftest_td_key_c141_3.py", "tools/bench/selftest_c147_b1_2.py")] + PIN,
    "pass": [
        "selftest_stagekit.py case J also stubs create_local_read, no other line changed (git diff quoted)",
        "selftest_stagekit on stagekit 06b8d844 with COM blocked = 0 fails, 0 COM calls, rc quoted; plain run rc + counts quoted",
        "selftest_c147_b1_2 17/0 and selftest_td_key_c141_3 9/0, rc quoted",
        "stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, s06 plan/pred/in/licence/recipes unchanged; no LabVIEW process before/after"],
    "outputs": ["tools/bench/selftest_stagekit.py", "tools/bench/diag_c147_c3_1_facts.md"],
    "flags": flags("read", ["tools/bench/selftest_stagekit.py", "tools/bench/diag_c147_c3_1*", "tools/bench/selftest_stagekit*.log", "tools/bench/gate_fp_queue.jsonl"]),
    "budget": {"failures": 2, "minutes": 30}, "advances": ["M3", "R1"],
    "requires": [{"kind": "file", "name": "tools/bench/selftest_stagekit.py"}, {"kind": "file", "name": "tools/bench/diag_c147_b1_4_run.py"}],
    "rules": ["No LabVIEW process may start; check tasklist before and after",
              "Edit only case J of selftest_stagekit.py; no tool, plan, licence, recipe or memory_model.json edit",
              "Gate false positives go to gate_fp_queue via tools/gate_fp.py, never an env bypass"]}

c2 = {
    "schema": "task/1", "id": "147-c3-2", "kind": "build",
    "goal": "s06 licence gains 'renames' (5 measured); s06 build recipe calls the new gate API (:127 renames+bind; :139-144 pb_rename_rows); py_compile + dry + prerun PASS on final bytes",
    "why": "PD356(d), PD357(e)(f): D/TD/PB failed the s06 retry only on LabVIEW's input renames of #2626/#9503; stagekit 06b8d844 gates them by licence. The recipe must use the new API before the one s06 scratch.",
    "inputs": [inp(p) for p in ("tools/bench/cards/brief_147-c3-2.md", "tools/bench/diag_c147_b1_1_rescore.py", "tools/bench/selftest_c147_b1_2.py",
                               "tools/bench/diag_c147_a2_1_facts.md", "tools/recipes/stage_d1_ring_p4_s06v18.py", "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py",
                               "tools/bench/plan_ring_p4_s06v18_licence.json", "tools/bench/plan_ring_p4_s06v18.json", "tools/bench/plan_ring_p4_s06v18_pred.json",
                               "tools/bench/plan_ring_p4_s06v18_in.json")] + PIN,
    "pass": [
        "Licence has 'renames' = exactly the 5 measured (#2626 2832/4160/4165 array->element; #9503 9505/9508 Value->''), rename_by_uid kept; licence_renames() = 5 keys",
        "Build recipe calls the new gate API (renames + bind at :127, PB via pb_rename_rows and unlicensed==[] at :139-144); no other gate changed",
        "py_compile + dry of both recipes + offline stage_prerun PASS on the FINAL bytes; commands + rc + new md5s quoted",
        "New D/TD/PB path on the stored s06 retry read = ALL PASS, unlicensed empty",
        "stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, memory_model 88eeb037, plan/pred/in unchanged; no LabVIEW process before/after"],
    "outputs": ["tools/bench/plan_ring_p4_s06v18_licence.json", "tools/recipes/stage_d1_ring_p4_s06v18.py", "tools/bench/diag_c147_c3_2_facts.md"],
    "flags": flags("read", ["tools/bench/plan_ring_p4_s06v18_licence.json", "tools/recipes/stage_d1_ring_p4_s06v18.py", "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py",
                            "tools/bench/diag_c147_c3_2*", "tools/bench/prerun_records.jsonl", "tools/bench/sim/ring_p4_s06v18/**", "tools/bench/gate_fp_queue.jsonl"]),
    "budget": {"failures": 2, "minutes": 60}, "advances": ["M3", "R1"],
    "requires": [{"kind": "file", "name": "tools/recipes/stage_d1_ring_p4_s06v18.py"}, {"kind": "file", "name": "tools/stage_prerun.py"}],
    "rules": ["No LabVIEW process may start; check tasklist before and after",
              "No edit of stagekit/stagexec/gscript/elrule, self-tests, plan/pred/in, memory_model; defect = RETURN",
              "Do not touch selftest_stagekit.py (card 147-c3-1 edits it beside this one)",
              "Gate false positives go to gate_fp_queue via tools/gate_fp.py, never an env bypass"]}

for c in (c1, c2):
    json.dump(c, open("tools/bench/cards/task_%s.json" % c["id"], "w"), indent=1)
print("wrote", c1["id"], c2["id"])
