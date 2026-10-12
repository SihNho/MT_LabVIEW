# ---
# labview: none
# hardware: none
# offline-args: all
# evidence: tools/bench/cards/task_166-a1-6.json
# ---
r"""diag_c166_a1_6_dry - card 166-a1-6 (OFFLINE): the stored ring recipes' DRY (`stage_prerun.py --dry <recipe> --no-record`) under the
stagekit from BEFORE assignment 166-1 (card 166-a1-4's byte copy tools/bench/diag_c166_a1_4_stagekit_pre.txt, md5 dd57c1ca; card 166-a1-3
changed errorlist_check / elpredict only, which no dry path imports) and under the current tools/stagekit.py (cards 166-a1-4 + 166-a1-6), compared.
Found before writing: tools/bench/diag_c166_a1_4_dry.py holds the run (run_one: exec the pre copy as module `stagekit` inside
stage_prerun.patch_stagekit) and the normaliser (norm); both are CALLED here (imported, PRE re-pointed), not copied. Only the outer loop is new,
because that script writes its outputs under its own card's names.
PREDICTION CONTRACT: for p5s01a, p5s01b, p5s02a .. p5s02e old == new line for line once run timestamps are cut (norm); rc equal; the p5s02d
rc 1 (CEN2 vs plan_ring_p5s02d_pred.json census) is there under both; no 'RECORD TD uid' line appears (a dry has no real read).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c166_a1_6_dry.log -- py -u tools/bench/diag_c166_a1_6_dry.py all"""
import concurrent.futures as cf
import hashlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import diag_c166_a1_4_dry as D  # noqa: E402

PRE_PIN = "dd57c1cac5d56b82c08c6ef9d7b1a22d"


def main_all():
    import protocol
    G = {"pass": 0, "fail": 0, "first": None}

    def gate(label, ok, detail=""):
        G["pass" if ok else "fail"] += 1
        G["first"] = G["first"] or (None if ok else label)
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)
    m = hashlib.md5(open(D.PRE, "rb").read()).hexdigest()
    gate("B0 pre copy {0} md5 == {1}; stagekit now {2}".format(os.path.basename(D.PRE), PRE_PIN[:8],
         hashlib.md5(open(os.path.join(ROOT, "tools", "stagekit.py"), "rb").read()).hexdigest()), m == PRE_PIN, m)
    jobs = [(s, md) for s in D.STEPS for md in ("old", "new")]

    def go(j):
        s, md = j
        p = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "run", md, "tools/recipes/stage_d1_ring_{0}.py".format(s)],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return j, p.returncode, p.stdout + p.stderr
    with cf.ThreadPoolExecutor(4) as ex:
        out = dict((j, (rc, txt)) for j, rc, txt in ex.map(go, jobs))
    for s in D.STEPS:
        (r0, t0), (r1, t1) = out[(s, "old")], out[(s, "new")]
        for md, t in (("old", t0), ("new", t1)):
            with open(os.path.join(HERE, "diag_c166_a1_6_dry_{0}_{1}.txt".format(s, md)), "w", encoding="utf-8") as f:
                f.write(t)
        a, b = t0.splitlines(), t1.splitlines()
        raw = [i + 1 for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
        na, nb = D.norm(t0), D.norm(t1)
        verdict = [x for x in b if x.startswith("DRY ") or x.startswith("RESULT")][-2:]
        rtd = [i + 1 for i, x in enumerate(b) if "RECORD TD uid" in x]
        gate("D {0}: dry old == new after cutting run timestamps (rc {1}/{2}); raw differing lines {3}; RECORD TD uid lines {4}; verdict {5}".format(
             s, r0, r1, raw[:12], rtd, verdict), na == nb and r0 == r1 and not rtd, [(x, y) for x, y in zip(na, nb) if x != y][:3])
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        rc = D.run_one(sys.argv[2], sys.argv[3])
        sys.exit(rc or 0)
    sys.exit(main_all())
