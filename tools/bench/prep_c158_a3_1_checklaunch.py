# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c158_a2_2_checklaunch.log
# ---
"""Card 158-a3-1: the launch gate on the FULL launch command text of the PD386(e) retry (stage_prerun.check_launch(cmd), as
diag_c158_a2_2_checklaunch.py did; calls only, no LabVIEW, nothing recorded). Three forms of the retry command on the NEW log:
  A  no card at all;  B  --retry-card <this card> on the bgrun line;  C  --unverified-card <the c158-a2-2 card> (the old form).
Also: the stage's counted runs this cycle (stage_prerun.read_stage_runs / cycle_key / RETRY_CAP) and the retry card check
(stage_prerun.retry_card) for this card (no retry_of -> refused, which is what a retry_of card must fix).
PREDICTION: units == [the scratch recipe] for each; the outcomes are quoted, not predicted (the facts file says what the gate needs)."""
import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as P  # noqa: E402

BASE = "py tools/bgrun.py --material --max-min 50 {0}--log tools/bench/diag_c158_p5s02a_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py{1}"
CMDS = {"A": BASE.format("", ""), "B": BASE.format("--retry-card tools/bench/cards/task_158-a3-1.json ", ""),
        "C": BASE.format("", " --unverified-card tools/bench/cards/task_158-a2-2.json")}
g = []
for k, cmd in sorted(CMDS.items()):
    units = P.launched_stage_scripts(cmd)
    ok, why = P.check_launch(cmd)
    print("CMD {0} {1}".format(k, cmd), flush=True)
    print("  UNITS {0}".format([P.rel(u) for u in units]), flush=True)
    print("  {0} {1}".format("ALLOW" if ok else "REFUSE", (why or "").strip()[:900]), flush=True)
    g.append(("{0} units == 1 scratch recipe".format(k), len(units) == 1))
key = P.stage_key("tools/recipes/stage_d1_ring_p5s02a_scratch.py")
ck = P.cycle_key()
mine = [r for r in P.read_stage_runs() if r.get("stage") == key and r.get("cycle") == ck and r.get("by") == P.COUNTED_BY]
print("FACT stage key {0!r}; cycle {1!r}; counted runs this cycle {2}; RETRY_CAP {3}".format(key, ck, len(mine), P.RETRY_CAP), flush=True)
print("FACT retry_card(B, key) -> {0}".format(P.retry_card(CMDS["B"], key, set())), flush=True)
for lab, v in g:
    print("GATE {0} | {1}".format("PASS" if v else "FAIL", lab), flush=True)
nf = sum(1 for _, v in g if not v)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if nf == 0 else "FAIL", "gates": {"pass": len(g) - nf, "fail": nf},
                              "first_fail": next((lab for lab, v in g if not v), None), "artefacts": []}), flush=True)
sys.exit(1 if nf else 0)
