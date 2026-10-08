# ---
# labview: none
# hardware: none
# evidence: archive/peer/2026-10-08-c148-a2-3-t3regress-prefix.md:85
# ---
r"""diag_c148_a2_3_unmask - card 148-a3-1 step 3 (review 2(b), archive/peer/2026-10-08-c148-a2-3-t3regress-prefix.md:73,85).
The stale plans stop R1/R2 (selftest_c133_1_fsroutes) and U1/U2 (selftest_rebase_uidreuse_c143_4) at the first check of
stage_prerun.rebase (`base is not provisional`, stage_prerun.py:4243-4244), and X17 stops E1 (selftest_stage_prerun_c106e) -
so those tests check nothing past that point. This script puts the PROVISIONAL base back on %TEMP% copies and runs the
same calls with the HEAD (07202624, pre-cycle-148) stage_prerun.py and with the disk stage_prerun.py, then compares.

HOW the two codes are made comparable: each variant runs in its OWN child interpreter; the child builds a module named
`stage_prerun` from the given SOURCE (HEAD = `git show HEAD:tools/stage_prerun.py`, rc checked; disk = tools/stage_prerun.py)
with __file__ = the main tree's tools/stage_prerun.py, so HERE/ROOT/BENCH and every data file are the SAME for both; only the
code differs (stagesim/vigraph/addrcheck/stagexec are unedited, `git diff --stat HEAD` lists only stage_prerun.py under tools/*.py).
Existing pieces reused: the cases are the ones of selftest_c133_1_fsroutes.py:42 (rebase on graph_ring_p3b1_20261002_073225,
simulate, out_root=tmp), selftest_rebase_uidreuse_c143_4.py:41 (rebase on graph_ring_p4s02_20261003_112505, simulate=False)
and selftest_stage_prerun_c106e.py:90 (--prerun stage_d1_disp.py --no-record --from-step 33 --base dispA, PRERUN_LOG_DIR=tmp).
Provisional base = the plan's finalized.plan_in file's base (plan_ring_p4_s03v18.json:335-337 -> plan_ring_p4_s03v18_in.json:8-16;
p3b2's plan_in is a gone %TEMP% file, so plan_ring_p3b2_in.json:65-73 is used). Variant A = the current plan with base := that
provisional base (the brief's wording); variant B = the _in plan itself (negative uids, the pre-rebase input).
X17 is skipped in the c106e case by replacing x17_gate in the child (stage_prerun.py:2871,2947). Originals are only READ.
PREDICTION: every case gives the same ok/detail/log lines (temp names normalised) and the c106e prerun the same gate lines at
HEAD and on disk (the cycle-148 edits :592,:848,:3150,:3415,:3433,:4474 are off the rebase path). Gates: one per case.
REVISED after run 1 (16:17, log diag_c148_a2_3_unmask.log) and review archive/peer/2026-10-08-c148-a3-1-unmask-clockstamp.md:
c106e in its own child per variant, PRERUN_LOG_DIR fresh in the child's env before import, sys.argv = the recipe argv, clock
stamps normalised, every differing line printed. c106e prediction then: both sides X5 PASS (ops 7, as s4_c106e_e1_full.log:88),
dry graph graph_dispA_step33.json, 0 FAIL / RESULT PASS, 0 differing lines. NOT RUN in card 148-a3-1 (returned first).
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c148_a2_3_unmask.log -- py -u tools/bench/diag_c148_a2_3_unmask.py
"""
import contextlib
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
SPF = os.path.join(TOOLS, "stage_prerun.py")
B = lambda p: os.path.join(ROOT, "tools", "bench", p)                               # noqa: E731
CASES = [("p3b2_A", "plan_ring_p3b2.json", "plan_ring_p3b2_in.json", "graph_ring_p3b1_20261002_073225.json", True),
         ("p3b2_B", None, "plan_ring_p3b2_in.json", "graph_ring_p3b1_20261002_073225.json", True),
         ("s03_A", "plan_ring_p4_s03v18.json", "plan_ring_p4_s03v18_in.json", "graph_ring_p4s02_20261003_112505.json", False),
         ("s03_B", None, "plan_ring_p4_s03v18_in.json", "graph_ring_p4s02_20261003_112505.json", False)]


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def norm(s, tmp):
    s = str(s).replace(tmp, "<TMP>").replace(tmp.replace("\\", "/"), "<TMP>")
    s = re.sub(r"(rebase|tmp|stage_dry|st_)[A-Za-z0-9_]{6,}", r"\1<T>", s)
    s = re.sub(r"\d{8}_\d{6}", "<TS>", s)          # run 1 (16:17): the dry's scratch VI name carries the run's clock
    return s.replace("RESULT {", "RESULT-CHILD {")


def child(tag, src, out, mode):
    # review archive/peer/2026-10-08-c148-a3-1-unmask-clockstamp.md:82,107-110 (run 1 at 16:17 was not E1's configuration):
    # PRERUN_LOG_DIR comes from the PARENT's env (stage_prerun reads LOG_DIR at import, :124), the c106e case runs in its
    # own child with no rebase case first, and sys.argv is the recipe's argv (the recipe reads its mode from sys.argv).
    sys.path.insert(0, TOOLS)
    m = types.ModuleType("stage_prerun")
    m.__file__ = SPF
    sys.modules["stage_prerun"] = m
    exec(compile(open(src, encoding="utf-8").read(), SPF, "exec"), m.__dict__)
    SP = m
    res = {"tag": tag, "src_md5": md5(src), "cases": {}, "log_dir": getattr(SP, "LOG_DIR", None)}
    for name, cur, pin, graph, sim in (CASES if mode == "rebase" else []):
        tmp = tempfile.mkdtemp(prefix="unmask_")
        try:
            pl = json.load(open(B(pin), encoding="utf-8"))
            if cur:
                cp = json.load(open(B(cur), encoding="utf-8"))
                cp["base"] = pl["base"]
                pl = cp
            tp = os.path.join(tmp, os.path.basename(cur or pin))
            json.dump(pl, open(tp, "w", encoding="utf-8"), indent=1)
            lines = []
            try:
                ok, det = SP.rebase(tp, B(graph), log=lambda *a: lines.append(" ".join(str(x) for x in a)), simulate=sim,
                                    out_root=tmp)
            except Exception as e:                                                    # noqa: BLE001
                ok, det = "EXC", "%s: %s" % (type(e).__name__, e)
            res["cases"][name] = {"ok": ok, "det": norm(det, tmp), "log": [norm(x, tmp) for x in lines]}
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    if mode != "c106e":
        json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
        return 0
    tmp = tempfile.mkdtemp(prefix="unmask_")
    try:
        SP.x17_gate = lambda plans, labels=None: (True, "X17 SKIPPED by diag_c148_a2_3_unmask")
        part = json.load(open(B("stage_d1_dispA.json"), encoding="utf-8"))["partA"]
        argv = ["--prerun", os.path.join(ROOT, "tools", "recipes", "stage_d1_disp.py"), "--no-record", "--from-step", "33",
                "--base", part["file"]]
        sys.argv = [SPF] + argv
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                rc = SP.main(argv)
        except SystemExit as e:
            rc = "EXIT %s" % e.code
        except Exception as e:                                                        # noqa: BLE001
            rc = "EXC %s: %s" % (type(e).__name__, e)
        txt = norm(buf.getvalue(), tmp)
        gl = [ln.strip() for ln in txt.splitlines() if re.match(r"^\s*(PASS|FAIL|WARN|FACT)\s", ln) or ln.startswith(("===",
                                                                                                                     "RESULT"))]
        res["cases"]["c106e_noX17"] = {"ok": rc, "det": "", "log": gl}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    json.dump(res, open(out, "w", encoding="utf-8"), indent=1)
    return 0


def main():
    sys.path.insert(0, TOOLS)
    import protocol as P
    tmp = tempfile.mkdtemp(prefix="unmask_par_")
    try:
        g = subprocess.run(["git", "show", "HEAD:tools/stage_prerun.py"], cwd=ROOT, capture_output=True, timeout=120)
        print("  STEP  git show HEAD:tools/stage_prerun.py rc=%s stderr=%r" % (g.returncode, g.stderr.decode("utf-8", "replace")[:300]),
              flush=True)
        if g.returncode != 0:
            print(P.result_line(P.make_result(0, 1, "git show HEAD:tools/stage_prerun.py rc %s" % g.returncode)), flush=True)
            return 1
        hs = os.path.join(tmp, "stage_prerun_HEAD.py")
        open(hs, "wb").write(g.stdout)
        print("  FACT  HEAD blob md5 %s (LF->CRLF %s); disk md5 %s" % (
            hashlib.md5(g.stdout).hexdigest(), hashlib.md5(g.stdout.replace(b"\r\n", b"\n").replace(b"\n", b"\r\n")).hexdigest(),
            md5(SPF)), flush=True)
        for c in CASES:
            for f in (c[1], c[2], c[3]):
                if f:
                    print("  FACT  input %s md5 %s" % (f, md5(B(f))), flush=True)
        outs = {"HEAD": {"cases": {}}, "DISK": {"cases": {}}}
        for mode in ("rebase", "c106e"):
            for tag, src in (("HEAD", hs), ("DISK", SPF)):
                o = os.path.join(tmp, "%s_%s.json" % (tag, mode))
                env = dict(os.environ)
                for k in ("CARD_ID", "CARD_LABVIEW", "BGRUN_LOG"):
                    env.pop(k, None)
                ld = tempfile.mkdtemp(prefix="unmask_logdir_", dir=tmp)        # fresh, empty, set BEFORE the import
                env["PRERUN_LOG_DIR"] = ld
                r = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--child", tag, src, o, mode], cwd=ROOT,
                                   env=env, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
                print("  STEP  child %s %s rc=%s stderr tail %r" % (tag, mode, r.returncode, (r.stderr or "")[-400:]), flush=True)
                if r.returncode != 0 or not os.path.isfile(o):
                    print(P.result_line(P.make_result(0, 1, "child %s %s rc %s" % (tag, mode, r.returncode))), flush=True)
                    return 1
                got = json.load(open(o, encoding="utf-8"))
                print("  FACT  child %s %s LOG_DIR %s (fresh %s)" % (tag, mode, got.get("log_dir"),
                                                                     os.path.normcase(str(got.get("log_dir"))) == os.path.normcase(ld)),
                      flush=True)
                outs[tag]["cases"].update(got["cases"])
        npass, fails = 0, []
        for name in [c[0] for c in CASES] + ["c106e_noX17"]:
            h, d = outs["HEAD"]["cases"][name], outs["DISK"]["cases"][name]
            same = h == d
            print("  CASE  %-12s HEAD ok=%s | DISK ok=%s | log lines %d/%d -> %s" % (name, h["ok"], d["ok"], len(h["log"]),
                                                                                    len(d["log"]), "EQUAL" if same else "DIFFERENT"),
                  flush=True)
            print("     | det HEAD: %s" % h["det"][:400], flush=True)
            if h["det"] != d["det"]:
                print("     | det DISK: %s" % d["det"][:400], flush=True)
            for side, v in (("HEAD", h), ("DISK", d)):
                gates = [x for x in v["log"] if re.match(r"^(PASS|FAIL|WARN)\s", x)]
                if gates:
                    print("     | gates %s: %d PASS, %d FAIL, %d WARN; first FAIL %r" % (
                        side, sum(x.startswith("PASS") for x in gates), sum(x.startswith("FAIL") for x in gates),
                        sum(x.startswith("WARN") for x in gates), next((x[:200] for x in gates if x.startswith("FAIL")), None)),
                        flush=True)
            dl = [i for i, (a, b) in enumerate(zip(h["log"], d["log"])) if a != b]
            for i in dl[:20]:
                print("     | diff line %d of %d: HEAD %r | DISK %r" % (i, len(dl), h["log"][i][:250], d["log"][i][:250]), flush=True)
            for x in h["log"][-3:]:
                print("     | tail: %s" % x[:250], flush=True)
            if same:
                npass += 1
            else:
                fails.append(name)
        print(P.result_line(P.make_result(npass, len(fails), ("HEAD vs disk differ: " + ", ".join(fails)) if fails else None)),
              flush=True)
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        sys.exit(child(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5]))
    sys.exit(main())
