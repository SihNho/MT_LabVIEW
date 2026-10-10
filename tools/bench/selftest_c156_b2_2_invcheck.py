# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-b2-2.md
# ---
"""Self-test of tools/invcheck.py (card 156-b2-2): replay the recorded runs of diag_c156_a2_1_inv.py through the module on the SAME config
(tools/bench/diag_c156_b2_2_inv_c156a21.py CONFIG) with the snapshot redirected to %TEMP%, and compare gate by gate (label, PASS/FAIL, order).
  before: recorded diag_c156_a2_1_inv_before.log (60 gates); snapshot written to a temp file (count compared with the recorded 153).
  after:  recorded diag_c156_a2_1_inv_after.log (59 gates); compared against a TEMP COPY of the recorded snapshot diag_c156_a2_1_inv_snap.json.
A gate whose status differs only because its file changed since the recording is DRIFT (old/new value listed, not counted as reproduced);
a label/order/count difference or an unexplained status difference is MISMATCH (gate FAIL). FAIL case: a temp config with a wrong pin.
Inner GATE/RESULT lines are printed with an 'inner:' prefix so only this script's own GATE and RESULT lines are top-level.
PREDICTION: label sequence equal 60/60 and 59/59; MISMATCH 0; reproduced PASS >= 1; DRIFT includes ring-p5.md 742e54c4 -> the md5 on
disk at run time (x2; card 160-f3-1, was the pin aa238a09); FAIL case exact (1 pass / 1 fail, first_fail the wrong pin, exit 1); the seven
stage-tool pins (stagexec a4df7e15 since 161-a1-1, stagesim 95a162ba since 160-f3-1) and the old inv file unchanged.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c156_b2_2_invcheck.log -- py -u tools/bench/selftest_c156_b2_2_invcheck.py"""
import os
import re
import shutil
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
B = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, B)
import invcheck                                                                                   # noqa: E402
from diag_c156_b2_2_inv_c156a21 import CONFIG                                                     # noqa: E402

G = invcheck.Gates()
TMP = tempfile.mkdtemp(prefix="selftest_c156_b2_2_")
GRE = re.compile(r"^GATE (PASS|FAIL) \| (.*?) \| (.*)$")


def recorded(log):
    return [(m.group(2), m.group(1) == "PASS", m.group(3)) for m in (GRE.match(l.rstrip("\n")) for l in open(log, encoding="utf-8")) if m]


def replay(mode, snap):
    lines = []
    cfg = dict(CONFIG, snap_path=snap)
    g = invcheck.run_inv(mode, out=lines.append, **cfg)
    for l in lines:
        print("  inner: " + l, flush=True)
    return g, lines


def compare(mode, rec, got):
    drift, mism, rep_pass, rep_fail = [], [], 0, 0
    G("{0}: gate count {1} == recorded {2}".format(mode, len(got), len(rec)), len(got) == len(rec))
    G("{0}: label sequence equal".format(mode), [r[0] for r in rec] == [x[0] for x in got],
      [(i, r[0], x[0]) for i, (r, x) in enumerate(zip(rec, got)) if r[0] != x[0]][:5])
    for i, ((lab, ok0, d0), (lab1, ok1, d1)) in enumerate(zip(rec, got)):
        d1 = str(d1)                                         # the log holds the printed form of the detail
        if lab != lab1:
            mism.append((i, lab, lab1))
        elif ok0 == ok1 and d0 == d1:
            rep_pass, rep_fail = rep_pass + ok0, rep_fail + (not ok0)
        elif d0 != d1:                                       # the file behind the gate changed since the recording
            drift.append((lab, d0[:40], d1[:200]))
        else:
            mism.append((i, lab, "status {0}->{1} with identical detail".format(ok0, ok1)))
    for x in drift:
        print("DRIFT {0} | {1} | old {2} | new {3}".format(mode, *x), flush=True)
    print("FACT {0}: reproduced {1} PASS + {2} FAIL, DRIFT {3}, MISMATCH {4}".format(mode, rep_pass, rep_fail, len(drift), len(mism)), flush=True)
    G("{0}: MISMATCH 0".format(mode), not mism, mism[:5])
    G("{0}: >= 1 recorded PASS reproduced exactly".format(mode), rep_pass >= 1, rep_pass)
    return drift


# 1. before: temp snapshot
rec_b = recorded(os.path.join(B, "diag_c156_a2_1_inv_before.log"))
snap_b = os.path.join(TMP, "snap_before.json")
gb, lb = replay("before", snap_b)
drift_b = compare("before", rec_b, gb.rows)
nb = [l for l in lb if l.startswith("FACT snapshot ")]
G("before: temp snapshot file count == recorded 153", bool(nb) and nb[0].startswith("FACT snapshot 153 files"), nb)
# 2. after: against a temp COPY of the recorded snapshot (the record is read, never written)
rec_a = recorded(os.path.join(B, "diag_c156_a2_1_inv_after.log"))
snap_a = os.path.join(TMP, "snap_recorded_copy.json")
shutil.copyfile(os.path.join(B, "diag_c156_a2_1_inv_snap.json"), snap_a)
ga, la = replay("after", snap_a)
drift_a = compare("after", rec_a, ga.rows)
# card 160-f3-1 (PD391(g)): the expected new ring-p5.md md5 is READ FROM DISK at run time (was the stale pin aa238a09)
p5_now = invcheck.md5(os.path.join(ROOT, "docs", "d1", "ring-p5.md"))
G("ring-p5.md drift listed (742e54c4 -> {0}, read from disk)".format(p5_now[:8]),
  any(x[0].startswith("md5 ring-p5.md") and x[2].startswith(p5_now[:8]) for x in drift_a),
  [x for x in drift_a if x[0].startswith("md5 ring-p5.md")])
# 3. FAIL case: a deliberately wrong pin in a temp config (expected detail = stagekit's recorded md5)
fl = []
fcfg = dict(pins={os.path.join(ROOT, "tools", "stagekit.py"): "00000000", os.path.join(ROOT, "tools", "addrcheck.py"): "207beb0d"},
            snap_path=os.path.join(TMP, "snap_fail.json"), snap_globs=[], snap_label="none")
rc = invcheck.main_inv(["x", "before"], out=fl.append, **fcfg)
for l in fl:
    print("  inner: " + l, flush=True)
want = ["GATE FAIL | md5 stagekit.py == 00000000 | 9b8f82c1a0150bcaacaf9c56e003c335",   # re-pinned 160-f2-1 from aec03c6c; 160-e5-1 from 1441bb4c; 161-a3-1 from 0b5bb678
        "GATE PASS | md5 addrcheck.py == 207beb0d | 207beb0d09102c78b1e06d1f076eec7e"]
G("FAIL case: GATE lines exact", [l for l in fl if l.startswith("GATE ")] == want, [l for l in fl if l.startswith("GATE ")])
rl = [l for l in fl if l.startswith("RESULT ")]
G("FAIL case: RESULT FAIL 1/1, first_fail the wrong pin, exit 1",
  rc == 1 and len(rl) == 1 and '"status":"FAIL"' in rl[0].replace(" ", "") and '"pass":1,"fail":1' in rl[0].replace(" ", "")
  and "md5 stagekit.py == 00000000" in rl[0], (rc, rl))
# 4. pins of the card and the record untouched
# re-pinned 160-f2-1 from stagexec 25a1494c, stagesim eb99c6ba, stagekit aec03c6c, stage_prerun 9decb20f;
# re-pinned 160-f3-1 from stagexec c4a6e0b6, stagesim a3261b56 (moved by card 160-a2-1)
# re-pinned 161-a1-1 from stagexec ddf23a31 (delete_wire = required checkpoint, PD393(a))
for rel, pin in [("tools/stagexec.py", "a4df7e15"), ("tools/stagesim.py", "95a162ba"), ("tools/stagekit.py", "9b8f82c1"),
                 ("tools/addrcheck.py", "207beb0d"), ("tools/gscript.py", "1a80236e"), ("tools/vigraph.py", "a7eb58c7"),
                 ("tools/stage_prerun.py", "7605116f"), ("tools/bench/diag_c156_a2_1_inv.py", "ab4ff13c")]:
    m = invcheck.md5(os.path.join(ROOT, *rel.split("/")))
    G("pin {0} == {1}".format(rel, pin), m.startswith(pin), m)
shutil.rmtree(TMP, ignore_errors=True)
print(G.result(), flush=True)
sys.exit(1 if G.failed else 0)
