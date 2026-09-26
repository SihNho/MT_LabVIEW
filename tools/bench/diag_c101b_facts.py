r"""diag_c101b_facts - card 101-4: READ-ONLY. Collects the card's facts from the r5 record (tools/bench/stage_d1_disp.json,
stamp 20260927_001537) and the logs this card wrote, into tools/bench/facts_c101b_stage.json with the md5 of every artefact.
No LabVIEW, no model; it decides nothing.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c101b_facts.log -- py -u tools/bench/diag_c101b_facts.py"""
import json, os, re, sys                                                             # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                      # noqa: E402
import stagesim as SS                                                                # noqa: E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))               # noqa: E731
R = J("tools/bench/stage_d1_disp.json")
LOG = open(os.path.join(HERE, "stage_d1_disp_r5.log"), encoding="utf-8").read().splitlines()
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def line_of(pat):
    return next((i for i, l in enumerate(LOG, 1) if re.search(pat, l)), None)


gate("F0 the record is run r5 (stamp 20260927_001537, card 101-4)", R.get("stamp") == "20260927_001537" and R.get("task") == "card 101-4",
     (R.get("stamp"), R.get("task")))
steps = [(r.get("k"), r.get("op"), (r.get("diff") or {}).get("n"), (r.get("diff") or {}).get("skipped", False)) for r in R["stagexec"]]
read = [(k, op, n) for k, op, n, sk in steps if not sk]
mb = [m["mb"] for m in R.get("meter") or [] if m.get("mb") is not None]
facts = {
    "schema": "facts/c101b", "card": "101-4", "run": "tools/bench/stage_d1_disp_r5.log", "record": "tools/bench/stage_d1_disp.json",
    "reads_compared": read, "step_diffs": R.get("step_diffs"),
    "stopped_in": {"k": 26, "log_line": line_of(r"FAIL  E1 the run reached its last op"),
                   "verb_error_line": line_of(r"OP create_local_read .* -> err")},
    "diff0_lines": {"k4": line_of(r"STEPX 04 .* diff 0"), "k5": line_of(r"STEPX 05 .* diff 0"),
                    "k24": line_of(r"STEPX 24 .* diff 0"), "k25": line_of(r"STEPX 25 .* diff 0")},
    "k12_line": line_of(r"RECORD STEP-DIFF after real op 12"), "read_retry_k15": line_of(r"read_retry k  15"),
    "meter_peak_mb": max(mb) if mb else None, "meter_last": (R.get("meter") or [None])[-1],
    "s1_md5_before_after": [R.get("input_md5_before"), R.get("input_md5_after")],
    "labview_gone_line": line_of(r"LabVIEW gone at exit: True"), "saved": R.get("saves"),
    "left_on_disk_line": line_of(r"THE FILES THIS RUN LEFT ON DISK"),
    "level": "STRUCTURAL (never run); nothing saved",
    "artefacts": dict((p, SS.md5_file(os.path.join(ROOT, p))) for p in (
        "tools/stagesim.py", "tools/stagexec.py", "tools/recipes/stage_d1_disp.py", "tools/bench/sim/disp/plan_disp.json",
        "tools/bench/sim/disp/stageplan_disp_r4_open.json", "tools/bench/diag_c101b_resim.py", "tools/bench/diag_c101b_syntax.py"))}
gate("F1 ops 4 and 5 (the two moved constants) read diff 0", facts["diff0_lines"]["k4"] and facts["diff0_lines"]["k5"], facts["diff0_lines"])
gate("F2 exactly one recorded step diff: k12, dangling_sim_only [11365]",
     [(d["k"], d["diff"]["dangling_sim_only"]) for d in R.get("step_diffs") or []] == [(12, [11365])], R.get("step_diffs"))
gate("F3 S1 md5 3e3d23ce unchanged, nothing saved, LabVIEW gone",
     facts["s1_md5_before_after"] == ["3e3d23cefd3a334001aa9d6156bf1aee"] * 2 and not R.get("saves") and facts["labview_gone_line"],
     (facts["s1_md5_before_after"], R.get("saves"), facts["labview_gone_line"]))
out = os.path.join(HERE, "facts_c101b_stage.json")
json.dump(facts, open(out, "w", encoding="utf-8"), indent=1, default=str)
print("  FACT " + json.dumps({k: facts[k] for k in ("reads_compared", "stopped_in", "diff0_lines", "k12_line", "meter_peak_mb")}, default=str), flush=True)
n = sum(1 for _l, g in gates if g)
ff = next((l for l, g in gates if not g), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": os.path.relpath(out, ROOT), "md5": SS.md5_file(out)}])), flush=True)
sys.exit(0 if ff is None else 1)
