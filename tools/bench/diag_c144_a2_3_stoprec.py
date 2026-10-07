# ---
# labview: none
# hardware: none
# ---
r"""Diagnostic, card 144-a2-3 item 2: replay the stop-record launch gate (guard_bash.stop_gate -> stop_record.check_command)
on the two commands logged REFUSED STOPPED-RECIPE at tools/hooks/material_marker.log:3332 and :3333, and on a recipe launch.

PURE replay: stop_record.save_records and guard_bash.note are replaced by no-ops, so no release is stamped into
tools/bench/stop_records.json and nothing is appended to material_marker.log. Existing tools checked first:
selftest_stoprecord_table.py / _bgrun / _offline_c107 test the table, not these logged commands.

The marker log keeps only ~200 chars of each command, so each is replayed AS LOGGED and in a RECONSTRUCTED full form
(the recipe paths cycle 143 named: p4_s02v18 / p4_s03v18).

Prediction contract:
  P1  3332 (git add ...) as logged and reconstructed -> allowed (git add is GIT_READONLY since chat-E3, fp-38)
  P2  3333 (git show HEAD:<recipe> | md5sum; ...) as logged and reconstructed -> allowed (readonly)
  P3  every recipe path token in P1/P2 is classed readonly or exempt, never build
  P4  `py tools/bgrun.py ... -- py -u tools/recipes/stage_d1_ring_p4_s04v18_scratch.py` -> recipe classed build
  P5  for every record whose build launch is refused now, the same launch is still refused (control: the gate bites)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import stop_record as SR  # noqa: E402
import guard_bash as GB  # noqa: E402
import protocol  # noqa: E402

SR.save_records = lambda records: None
GB.note = lambda marked, cmd: None
CD = 'cd "G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop" && '
R2, R3 = "tools/recipes/stage_d1_ring_p4_s02v18.py", "tools/recipes/stage_d1_ring_p4_s03v18.py"
C3332 = CD + "git add archive/peer/2026-10-03-priorart-c143-p1-p4s03v18.md tools/bench/cards/brief_143-P1.md "
C3332F = C3332 + R3 + " tools/recipes/stage_d1_ring_p4_s03v18_scratch.py && git commit -m \"143-P1 recipes\""
C3333 = CD + "git show HEAD:tools/recipes/stage_d1_ring_p4_s02v18.py | md5sum; git show HEAD:tools/recipes/st"
C3333F = (CD + "git show HEAD:%s | md5sum; git show HEAD:%s | md5sum; md5sum %s %s" % (R2, R3, R2, R3))
LAUNCH = CD + ("py tools/bgrun.py --material --max-min 50 --log tools/bench/x.log -- "
               "py -u tools/recipes/stage_d1_ring_p4_s04v18_scratch.py")
res = []


def gate(label, ok, detail):
    res.append((label, bool(ok)))
    print("%s  %s | %s" % ("PASS" if ok else "FAIL", label, detail))


def replay(cmd):
    rc = GB.stop_gate(cmd, "Bash")
    judged = GB._argument_only_view(GB._drop_lint_segments(GB._bash_escaped_quotes(cmd), SR), SR)
    keys = SR.command_keys(judged)
    rec = {k[1]: c for k, c in keys.items() if k[0] == "rel" and "tools/recipes/" in k[1]}
    return rc, rec


def main():
    for lab, cmd in (("P1 3332 as logged", C3332), ("P1 3332 reconstructed", C3332F),
                     ("P2 3333 as logged", C3333), ("P2 3333 reconstructed", C3333F)):
        rc, rec = replay(cmd)
        gate(lab + " -> allowed (stop_gate 0)", rc == 0, "rc=%s recipe-keys=%s" % (rc, rec))
        gate(lab.split()[0] + "b " + lab[3:] + " -> no recipe token classed build",
             all(c != "build" for c in rec.values()), rec)
    rc, rec = replay(LAUNCH)
    gate("P4 bgrun recipe launch -> recipe classed build", rec.get(
        "tools/recipes/stage_d1_ring_p4_s04v18_scratch.py") == "build", "rc=%s %s" % (rc, rec))
    print("INFO P4 launch stop_gate rc=%s (0 = no refusing record for this path today)" % rc)
    recs = SR.load_records()
    refused = []
    for i, r in enumerate(recs):
        p = SR._rel(r.get("recipe_path") or "")
        if not p or not os.path.isfile(os.path.join(ROOT, p)):
            continue
        launch = CD + "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u " + p
        if GB.stop_gate(launch, "Bash") == 2:
            refused.append(p)
            ro = GB.stop_gate(CD + "git add " + p + " && md5sum " + p, "Bash")
            gate("P5 refused launch of %s; git add/md5sum of it allowed" % p, ro == 0, "read rc=%s" % ro)
    print("INFO records=%d paths with a refused launch today=%d" % (len(recs), len(set(refused))))
    gate("P5 the gate still refuses at least one recipe launch", bool(refused), sorted(set(refused))[:5])
    n_fail = sum(1 for _, ok in res if not ok)
    print(protocol.result_line(protocol.make_result(len(res) - n_fail, n_fail,
                                                    next((l for l, ok in res if not ok), None))))
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
