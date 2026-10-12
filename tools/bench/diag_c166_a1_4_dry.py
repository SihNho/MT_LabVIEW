# ---
# labview: none
# hardware: none
# offline-args: all
# evidence: tools/bench/cards/task_166-a1-4.json
# ---
r"""diag_c166_a1_4_dry - card 166-a1-4 (OFFLINE): the stored ring recipes' DRY (prep_c165_a3_3_dry.log's command, `stage_prerun.py --dry
<recipe>`, here with --no-record so no launch record is written) run with the PRE-change stagekit (byte copy
tools/bench/diag_c166_a1_4_stagekit_pre.txt, md5 dd57c1ca) and with the changed tools/stagekit.py, and compared.
Found before writing: selftest_c165_innerface.py B1/B2 compares stagexec.compile_plan / dry_run pre vs new (stagexec is not changed here,
it does not import stagekit); stage_prerun.dry (stage_prerun.py:1014) runs the recipe IN PROCESS and loads stagekit in patch_stagekit
(:751) after the fake gscript / COM modules are installed - so 'old' mode wraps patch_stagekit to exec the pre copy as module `stagekit`
first (the same fakes bind as its `g`). Nothing of stage_prerun is copied.
PREDICTION CONTRACT: for each of p5s01a, p5s01b, p5s02a .. p5s02e the old and new dry outputs are equal line for line once the run's own
timestamps are cut (the dry's output VI name `_<yyyymmdd>_<hhmmss>.vi`, temp dir names); the rc and the dry verdict line are equal; the
class-3 RECORD PB lines (p5s02c / d / e: 2 each) are byte-equal. (Run 1, 18:07, printed a provenance suffix on those lines and did not
cut the VI-name timestamp: 5 FAIL on exactly those lines, diag_c166_a1_4_dry.log first block; the suffix was dropped from stagekit.)
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c166_a1_4_dry.log -- py -u tools/bench/diag_c166_a1_4_dry.py all"""
import concurrent.futures as cf
import hashlib
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
PRE = os.path.join(HERE, "diag_c166_a1_4_stagekit_pre.txt")
PRE_PIN = "dd57c1cac5d56b82c08c6ef9d7b1a22d"
STEPS = ("p5s01a", "p5s01b", "p5s02a", "p5s02b", "p5s02c", "p5s02d", "p5s02e")


def run_one(mode, recipe):
    import stage_prerun as SP
    if mode == "old":
        orig = SP.patch_stagekit

        def patched():
            import types
            m = types.ModuleType("stagekit")
            m.__file__ = os.path.join(ROOT, "tools", "stagekit.py")
            sys.modules["stagekit"] = m
            exec(compile(open(PRE, encoding="utf-8").read(), m.__file__, "exec"), m.__dict__)
            return orig()
        SP.patch_stagekit = patched
    sys.argv = ["stage_prerun.py", "--dry", recipe, "--no-record"]
    return SP.main(["--dry", recipe, "--no-record"])


def norm(text):
    out = []
    for x in text.splitlines():
        x = re.sub(r"_\d{8}_\d{6}(?=\.vi)|c\d+_dry_\w+|tmp\w{8}|\b\d+\.\d+ ?s\b|'secs': [\d.]+", "<v>", x)
        out.append(x)
    return out


def main_all():
    import protocol
    G = {"pass": 0, "fail": 0, "first": None}

    def gate(label, ok, detail=""):
        G["pass" if ok else "fail"] += 1
        G["first"] = G["first"] or (None if ok else label)
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)
    m = hashlib.md5(open(PRE, "rb").read()).hexdigest()
    gate("B0 pre copy md5 == {0}".format(PRE_PIN[:8]), m == PRE_PIN, m)
    jobs = [(s, md) for s in STEPS for md in ("old", "new")]

    def go(j):
        s, md = j
        p = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "run", md, "tools/recipes/stage_d1_ring_{0}.py".format(s)],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        return j, p.returncode, p.stdout + p.stderr
    with cf.ThreadPoolExecutor(4) as ex:
        out = dict((j, (rc, txt)) for j, rc, txt in ex.map(go, jobs))
    for s in STEPS:
        (r0, t0), (r1, t1) = out[(s, "old")], out[(s, "new")]
        for md, t in (("old", t0), ("new", t1)):
            with open(os.path.join(HERE, "diag_c166_a1_4_dry_{0}_{1}.txt".format(s, md)), "w", encoding="utf-8") as f:
                f.write(t)
        a, b = t0.splitlines(), t1.splitlines()
        raw = [i + 1 for i in range(max(len(a), len(b))) if (a[i] if i < len(a) else None) != (b[i] if i < len(b) else None)]
        na, nb = norm(t0), norm(t1)
        verdict = [x for x in b if x.startswith("DRY ") or x.startswith("RESULT")][-2:]
        rec3 = [i + 1 for i, x in enumerate(b) if "RECORD PB" in x and "class 3" in x]
        gate("D {0}: dry old == new after cutting run timestamps (rc {1}/{2}); raw differing lines {3}; class-3 RECORD PB lines {4} byte-equal; "
             "verdict {5}".format(s, r0, r1, raw[:12], rec3, verdict), na == nb and r0 == r1 and not set(raw) & set(rec3),
             [(x, y) for x, y in zip(na, nb) if x != y][:3])
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
    return 0 if not G["fail"] else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "run":
        rc = run_one(sys.argv[2], sys.argv[3])
        sys.exit(rc or 0)
    sys.exit(main_all())
