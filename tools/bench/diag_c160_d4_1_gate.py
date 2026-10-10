# ---
# labview: none
# hardware: none
# ---
"""Card 160-d4-1: what the prior-art gates say about the c160-d4-1 review, WITHOUT running anything.

Existing tools called (none rebuilt; same calls as tools/bench/prep_c158_a1_3_gate.py): guard_peer.undisposed (the
"review N+1 while review N is undisposed" device), guard_cycle PRIOR_ART_RE / PRIOR_ART_SLUGS / released_slugs, and
stop_record.check_command on the step-2 scratch command (not run). Writes nothing.

PREDICTION: undisposed('priorart') None; newest prior-art review = c160-d4-1, no open non-novel slug; stop_record ALLOW.
"""
import glob
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")]
os.chdir(ROOT)
import protocol          # noqa: E402
import guard_cycle as GC   # noqa: E402
import guard_peer as GP    # noqa: E402
import stop_record         # noqa: E402

REVIEW = "2026-10-10-priorart-priorart-c160-d4-1-p5s02b.md"
SCRATCH = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c161_p5s02b_scratch.log -- "
           "py -u tools/recipes/stage_d1_ring_p5s02b_scratch.py")
RECIPE = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c161_p5s02b.log -- "
          "py -u tools/recipes/stage_d1_ring_p5s02b.py")
gates = []

und = GP.undisposed("priorart")
print("UNDISPOSED priorart | %s" % (und and (os.path.basename(und[0]), und[1]),))
gates.append(und is None)
pa = sorted(glob.glob(os.path.join(GC.PEER, "*priorart*.md")), key=GC.stamp)
body = open(pa[-1], encoding="utf-8", errors="replace").read()
answer = body.split("\n## Answer", 1)[-1]
slugs = [s for s in GC.PRIOR_ART_RE.findall(answer) if s != "novel" and s in GC.PRIOR_ART_SLUGS]
rel_, bad = GC.released_slugs(pa[-1], body)
opn = [s for s in dict.fromkeys(slugs) if s not in rel_]
print("PRIOR-ART VERDICT | newest %s | non-novel %s | released %s | bad %s | open %s" % (
    os.path.relpath(pa[-1], ROOT), slugs, rel_, bad, opn))
gates.append(os.path.basename(pa[-1]) == REVIEW and not opn)
for name, cmd in (("scratch", SCRATCH), ("recipe", RECIPE)):
    allow, msg = stop_record.check_command(cmd)
    print("STOP_RECORD | %s | allow=%s | %s" % (name, allow, (msg or "").strip().replace("\n", " / ")[:400]))
    gates.append(bool(allow))
print(protocol.result_line({"status": "PASS" if all(gates) else "FAIL",
                            "gates": {"pass": sum(gates), "fail": len(gates) - sum(gates)},
                            "first_fail": None if all(gates) else "gate %d" % gates.index(False)}))
