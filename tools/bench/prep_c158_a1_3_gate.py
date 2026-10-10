# ---
# labview: none
# hardware: none
# ---
"""Card 158-a1-3: what the gates say, WITHOUT running anything - (1) the prior-art disposition gate on the c156-a1-1 review,
(2) the launch gate on the FULL P5-2 step-1 scratch command, on stagexec df82d75e.

Existing tools used (none rebuilt; same calls as tools/bench/prep_c157_a1_2_gate.py): guard_peer.undisposed (the
"review N+1 while review N is undisposed" device, tools/hooks/guard_peer.py:838), guard_cycle PRIOR_ART_RE /
released_slugs / premature_build, stage_prerun.check_launch + unverified_card_names, stop_record.check_command.
prior_art_review.py --dry-run is NOT called: it writes a review card under tools/bench/cards/, outside this card's globs.
Only write: a temp card copy under %TEMP% (variant C), removed at the end.

PREDICTION: undisposed('priorart') None; newest prior-art review = c156-a1-1, no open non-novel slug. Launch gate:
A refused (PB PASS-UNVERIFIED), B refused ("names no DRY-UNVERIFIED-OK gate"), C allowed.
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
import guard_peer as GP    # noqa: E402
import stop_record         # noqa: E402

CARD = "tools/bench/cards/task_158-a1-3.json"
REVIEW = "2026-10-09-priorart-priorart-c156-a1-1-p5s02a.md"
BASE = ("py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c158_p5s02a_scratch.log -- "
        "py -u tools/recipes/stage_d1_ring_p5s02a_scratch.py")
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

card = json.load(open(os.path.join(ROOT, CARD), encoding="utf-8"))
card["rules"] = list(card["rules"]) + ["DRY-UNVERIFIED-OK: PB frame-keyed cdiff"]
tmp = os.path.join(tempfile.gettempdir(), "task_158-a1-3_uvprobe.json")
json.dump(card, open(tmp, "w", encoding="utf-8"))
variants = [("A as given", BASE, False), ("B +--unverified-card this card", BASE + " --unverified-card " + CARD, False),
            ("C +--unverified-card temp copy w/ DRY-UNVERIFIED-OK", BASE + " --unverified-card " + tmp.replace("\\", "/"), True)]
for name, cmd, want in variants:
    ok, why = SP.check_launch(cmd)
    print("CHECK_LAUNCH | %s | allow=%s | %s" % (name, ok, (why or "").strip().replace("\n", " / ")))
    print("  named_ok=%s" % (SP.unverified_card_names(cmd),))
    gates.append(bool(ok) == want)
okr, whyr = stop_record.check_command(BASE)
print("STOP_RECORD | allow=%s | %s" % (okr, (whyr or "").strip().replace("\n", " / ")[:400]))
pb = GC.premature_build(BASE)
print("PREMATURE_BUILD (prior-art timing) | %s" % ((pb or "None (no block)").strip().replace("\n", " / ")[:600]))
os.remove(tmp)
npass = sum(gates)
print(protocol.result_line({"status": "PASS" if npass == len(gates) else "FAIL",
                            "gates": {"pass": npass, "fail": len(gates) - npass},
                            "first_fail": None if npass == len(gates) else "gate vs prediction %s" % gates,
                            "artefacts": []}))
