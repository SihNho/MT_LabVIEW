r"""diag_c116a_replay.py - card 116-1 S1 discriminating test, offline, no LabVIEW.
Replays material_marker.log:2614/:2615 (full argv recovered from the cycle-115 material transcript, since the marker log
cuts at 200 chars) through stop_record.check_command against a STUBBED store holding one undisposed record for
tools/recipes/stage_d1_l2r1.py, and prints each segment's class. Prediction (retrospective-cycle115.md:376 "likely gap is
`;`"): if the split is at fault, a READ-ONLY-program segment is classed build; if not, some other segment (awk) is.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c116a_replay.log -- py -u tools/bench/diag_c116a_replay.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import protocol as P          # noqa: E402
import stop_record as SR      # noqa: E402
R = "tools/recipes/stage_d1_l2r1.py"
SR.load_records = lambda: [{"recipe_path": R, "reviewed_sha256": "0" * 64, "review_file": "archive/peer/none-c116a.md",
                            "verdict": ["already-failed"], "released": None}]
SR.save_records = lambda recs: None
TR = os.path.join(os.path.expanduser("~"), ".claude", "projects",
                  "G--Codes-LabVIEW-Codes-MinLab-zz-LabView-VI-AAA-UNIST-2--Tracking-V6-ParallelLoop",
                  "572b728e-665d-4063-b1d0-ad1b9f13d545", "subagents", "agent-a55f825de5b187fac.jsonl")
ml = open(os.path.join(ROOT, "tools", "hooks", "material_marker.log"), encoding="utf-8", errors="replace").read().splitlines()
cmds = []
for line in open(TR, encoding="utf-8", errors="replace"):
    if "wc -l tools/recipes/stage_d1_l2r1.py;" not in line:
        continue
    try:
        o = json.loads(line)
    except ValueError:
        continue
    for c in (o.get("message") or {}).get("content") or []:
        if isinstance(c, dict) and c.get("type") == "tool_use":
            cmd = (c.get("input") or {}).get("command", "")
            if "wc -l tools/recipes/stage_d1_l2r1.py;" in cmd and cmd not in cmds:
                cmds.append(cmd)
G = []
def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-60s %s %s" % (label, "PASS" if ok else "FAIL", detail), flush=True)
for ln in (2614, 2615):
    logged = ml[ln - 1].split("STOPPED-RECIPE ", 1)[-1]
    full = [c for c in cmds if c.startswith(logged[:150]) or ("cd " in c and logged[:120] in c)]
    gate(bool(full), "M%d full argv recovered from transcript" % ln, "%d match(es)" % len(full))
    for c in full[:1]:
        print("ARGV %d %r" % (ln, c), flush=True)
        for s in SR.split_segments(c):
            print("  SEG %-9s %r" % (SR.segment_class(s, c), s[:140]), flush=True)
        print("  VERDICT %s" % ("ALLOW" if SR.check_command(c)[0] else "REFUSE"), flush=True)
npass = sum(1 for g in G if g[0])
print(P.result_line(P.make_result(npass, len(G) - npass, next((g[1] for g in G if not g[0]), None))), flush=True)
