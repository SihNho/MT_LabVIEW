# ---
# labview: none
# hardware: none
# ---
"""Card 157-a1-2 item 4: what the launch gates say about the FULL scratch launch command, WITHOUT running it.

Existing tools used (none rebuilt): tools/stage_prerun.py check_launch (the function guard_bash.prerun_gate calls,
tools/hooks/guard_bash.py:376) and unverified_card_names; tools/hooks/guard_cycle.py premature_build (prior-art timing
gate, :719) and its verdict gate inputs (released_slugs, PRIOR_ART_RE, :730-751); tools/stop_record.check_command (:682).
Nothing launches; the only write is a temporary card copy under %TEMP% (variant C) and whatever those functions log.

PREDICTION: A (as given) refused for PB PASS-UNVERIFIED; B (+ --unverified-card this card, no DRY-UNVERIFIED-OK) refused
with "names no DRY-UNVERIFIED-OK gate"; C (+ a temp copy of this card whose rules carry
"DRY-UNVERIFIED-OK: PB frame-keyed cdiff") passes the dry/prerun records part. Prior-art: no block (recipes unchanged).
"""
import glob
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")]
os.chdir(ROOT)
import protocol          # noqa: E402
import stage_prerun as SP  # noqa: E402
import guard_cycle as GC   # noqa: E402
import stop_record         # noqa: E402

CARD = "tools/bench/cards/task_157-a1-2.json"
BASE = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c157_p5s02a_scratch.log -- "
        "py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py")
card = json.load(open(os.path.join(ROOT, CARD), encoding="utf-8"))
card["rules"] = list(card["rules"]) + ["DRY-UNVERIFIED-OK: PB frame-keyed cdiff"]
tmp = os.path.join(tempfile.gettempdir(), "task_157-a1-2_uvprobe.json")
json.dump(card, open(tmp, "w", encoding="utf-8"))
variants = [("A as given", BASE), ("B +--unverified-card this card", BASE + " --unverified-card " + CARD),
            ("C +--unverified-card temp copy w/ DRY-UNVERIFIED-OK", BASE + " --unverified-card " + tmp.replace("\\", "/"))]
gates = []
for name, cmd in variants:
    ok, why = SP.check_launch(cmd)
    print("CHECK_LAUNCH | %s | allow=%s | %s" % (name, ok, (why or "").strip().replace("\n", " / ")))
    print("  named_ok=%s" % (SP.unverified_card_names(cmd),))
    gates.append(ok)
okr, whyr = stop_record.check_command(BASE)
print("STOP_RECORD | allow=%s | %s" % (okr, (whyr or "").strip().replace("\n", " / ")[:400]))
pb = GC.premature_build(BASE)
print("PREMATURE_BUILD (prior-art timing) | %s" % ((pb or "None (no block)").strip().replace("\n", " / ")[:600]))
pa = sorted(glob.glob(os.path.join(GC.PEER, "*priorart*.md")), key=GC.stamp)
if pa:
    body = open(pa[-1], encoding="utf-8", errors="replace").read()
    answer = body.split("\n## Answer", 1)[-1]
    slugs = [s for s in GC.PRIOR_ART_RE.findall(answer) if s != "novel" and s in GC.PRIOR_ART_SLUGS]
    rel_, bad = GC.released_slugs(pa[-1], body)
    print("PRIOR-ART VERDICT | newest %s | non-novel %s | released %s | open %s" % (
        os.path.relpath(pa[-1], ROOT), slugs, rel_, [s for s in dict.fromkeys(slugs) if s not in rel_]))
os.remove(tmp)
pred = [False, False, True]
npass = sum(1 for g, p in zip(gates, pred) if g == p)
print(protocol.result_line({"status": "PASS" if npass == 3 else "FAIL", "gates": {"pass": npass, "fail": 3 - npass},
                            "first_fail": None if npass == 3 else "launch-gate variants vs prediction %s" % gates,
                            "artefacts": []}))
