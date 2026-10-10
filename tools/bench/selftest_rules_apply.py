# ---
# labview: none
# hardware: none
# ---
r"""selftest_rules_apply - card chat-X6 (discussion structure-equal-02 experiment 2) self-test of the CANDIDATE apply path
tools/rules_apply.py and the CANDIDATE pre-commit check tools/git_precommit_rules.py. OFFLINE, no LabVIEW. Runs both
scripts as subprocesses with --root on a TEMP fake tree (git-initialised); the real protected files are never written.
The one real-tree call is `rules_apply.py audit --baseline --dry` (print only; the gate checks no ledger was created).
PRIOR ART: selftest_x10_chat_m2.py (temp tree + gate() pattern).
PREDICTION: S0 baseline writes 1 ledger line, audit clean; A apply with both tokens/no drift/matching test md5s -> rc 0,
live == cand, ledger +1 'apply', audit VIA-APPLY; refusals rc 1 with live and ledger unchanged: B gpt token missing,
C gpt token in STATE.open, D live drifted, E test md5 != cand, F unprotected path; G direct edit -> audit OUT-OF-BAND
(mismatch) and a new hook file -> OUT-OF-BAND never applied; H second baseline refused; precommit: P1 staged out-of-band
file refused, P2 the same file after a proper apply + a non-protected file -> pass, P3 staged deletion refused;
R real-tree dry baseline rc 0, count > 0, no ledger file created.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_rules_apply.log -- py -u tools/bench/selftest_rules_apply.py"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                    # noqa: E402
import rules_apply as RA                                                                # noqa: E402

RA_PY = os.path.join(ROOT, "tools", "rules_apply.py")
PC_PY = os.path.join(ROOT, "tools", "git_precommit_rules.py")
DEB = "tools/bench/debate/fake"
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det).replace("RESULT {", "result {")[:600]),
          flush=True)


def run(script, root, *args):
    p = subprocess.run([sys.executable, script, "--root", root] + list(args), capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=120)
    return p.returncode, p.stdout + p.stderr


def git(root, *args):
    return subprocess.run(["git", "-C", root, "-c", "user.name=selftest", "-c", "user.email=selftest@invalid"]
                          + list(args), capture_output=True, text=True, timeout=60)


def write(root, rel, text):
    f = os.path.join(root, rel)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(text)


def ledger_n(root):
    return len(RA.read_ledger(root))


def relay(root, rnd, claude_agreed, gpt_agreed, gpt_open=()):
    for side, ag, op in (("claude", claude_agreed, ()), ("gpt", gpt_agreed, gpt_open)):
        st = {"agreed": list(ag), "open": list(op), "questions": [], "experiment": "", "user_needed": "",
              "check": "", "done": True}
        write(root, "%s/relay/round_%02d_%s.md" % (DEB, rnd, side),
              "본문\n\nSTATE " + json.dumps(st, ensure_ascii=False) + "\n")


def candidate(root, cid, rnd, changes, gpt="agreed", test_md5=None):
    """Stage a candidate: files, relay round rnd, manifest via `stage`, one test via `add-test`."""
    tok = cid + " 동의"
    relay(root, rnd, [tok, "other"], [tok] if gpt == "agreed" else [], [tok] if gpt == "open" else [])
    for rel, text in changes.items():
        write(root, "%s/%s/files/%s" % (RA.CAND_REL, cid, rel), text)
    rc, out = run(RA_PY, root, "stage", cid, "--debate", DEB, "--round", str(rnd))
    assert rc == 0, out
    arts = [{"path": rel, "md5": test_md5 or RA.md5_file(os.path.join(RA.cand_dir(root, cid), "files", rel))}
            for rel in changes]
    log = os.path.join(root, "test_%s.log" % cid)
    with open(log, "w", encoding="utf-8") as fh:
        fh.write("some test output\n" + P.result_line(P.make_result(5, 0, None, arts)) + "\n")
    rc, out = run(RA_PY, root, "add-test", cid, "--command", "py -u fake_test.py", "--log", log)
    assert rc == 0, out


def refused(root, cid, label, expect_in):
    live = {r: RA.md5_file(os.path.join(root, r)) for r in RA.protected_files(root, RA.load_protected(root))}
    n0 = ledger_n(root)
    rc, out = run(RA_PY, root, "apply", cid)
    after = {r: RA.md5_file(os.path.join(root, r)) for r in RA.protected_files(root, RA.load_protected(root))}
    gate(label, rc == 1 and "REFUSED apply" in out and expect_in in out and live == after and ledger_n(root) == n0,
         "rc=%d expect %r; %s" % (rc, expect_in, [l for l in out.splitlines() if l.startswith("FAIL")]))


def main():
    t = tempfile.mkdtemp(prefix="rules_apply_selftest_")
    try:
        os.makedirs(os.path.join(t, "tools"))
        shutil.copyfile(os.path.join(ROOT, RA.PROTECTED_REL), os.path.join(t, RA.PROTECTED_REL))
        write(t, "CLAUDE.md", "core v0\n")
        write(t, "docs/rules/a.md", "rule a v0\n")
        write(t, "tools/hooks/h.py", "X = 0\n")
        write(t, "tools/hooks/run.log", "runtime log, excluded\n")
        write(t, "notes/free.md", "not protected\n")
        # S0 baseline
        rc, out = run(RA_PY, t, "audit", "--baseline")
        gate("S0 baseline written", rc == 0 and ledger_n(t) == 1 and RA.read_ledger(t)[0]["kind"] == "baseline",
             "rc=%d ledger=%d files=%s" % (rc, ledger_n(t), [p["path"] for p in RA.read_ledger(t)[0]["paths"]]))
        gate("S0 protected list excludes logs/unprotected", sorted(p["path"] for p in RA.read_ledger(t)[0]["paths"]) ==
             ["CLAUDE.md", "docs/rules/a.md", "tools/hooks/h.py", "tools/rules_protected.json"])
        rc, out = run(RA_PY, t, "audit")
        gate("S0 audit clean after baseline", rc == 0 and "OUT-OF-BAND" not in out, "rc=%d" % rc)
        # A apply
        candidate(t, "ch-a", 1, {"docs/rules/a.md": "rule a v1\n", "tools/hooks/h.py": "X = 1\n"})
        rc, out = run(RA_PY, t, "apply", "ch-a")
        cand = RA.md5_file(os.path.join(RA.cand_dir(t, "ch-a"), "files", "tools/hooks/h.py"))
        led = RA.read_ledger(t)
        gate("A apply ok", rc == 0 and RA.md5_file(os.path.join(t, "tools/hooks/h.py")) == cand and len(led) == 2 and
             led[-1]["kind"] == "apply" and led[-1]["id"] == "ch-a" and len(led[-1]["paths"]) == 2,
             "rc=%d ledger=%d" % (rc, len(led)))
        rc, out = run(RA_PY, t, "audit")
        gate("A audit VIA-APPLY", rc == 0 and out.count("VIA-APPLY") == 2 and out.count("BASELINE ") == 2, "rc=%d" % rc)
        # refusals
        candidate(t, "ch-b", 2, {"docs/rules/a.md": "rule a v2\n"}, gpt="missing")
        refused(t, "ch-b", "B refused: gpt token missing", "FAIL  agreement:gpt")
        candidate(t, "ch-c", 3, {"docs/rules/a.md": "rule a v3\n"}, gpt="open")
        refused(t, "ch-c", "C refused: gpt token in open", "token only in STATE.open")
        candidate(t, "ch-d", 4, {"CLAUDE.md": "core v4\n"})
        write(t, "CLAUDE.md", "core v0 drifted\n")
        refused(t, "ch-d", "D refused: live drifted", "FAIL  no-drift:CLAUDE.md")
        candidate(t, "ch-e", 5, {"tools/hooks/h.py": "X = 5\n"}, test_md5="0" * 32)
        refused(t, "ch-e", "E refused: test md5 != cand", "FAIL  test0:md5s")
        candidate(t, "ch-f", 6, {"notes/free.md": "changed\n"})
        refused(t, "ch-f", "F refused: path not protected", "FAIL  protected:notes/free.md")
        # G audit out-of-band (CLAUDE.md drifted above = direct edit) + a new hook file never applied
        write(t, "tools/hooks/new.py", "Y = 1\n")
        rc, out = run(RA_PY, t, "audit")
        gate("G audit OUT-OF-BAND", rc == 1 and "FAIL  OUT-OF-BAND CLAUDE.md" in out and
             "FAIL  OUT-OF-BAND tools/hooks/new.py  never applied" in out and "PASS  VIA-APPLY tools/hooks/h.py" in out,
             [l for l in out.splitlines() if "OUT-OF-BAND" in l])
        rc, out = run(RA_PY, t, "audit", "--baseline")
        gate("H second baseline refused", rc == 1 and ledger_n(t) == 2 and "REFUSED baseline" in out, "rc=%d" % rc)
        # precommit
        os.remove(os.path.join(t, "tools/hooks/new.py"))
        write(t, "CLAUDE.md", "core v0\n")
        gi = git(t, "init", "-q")
        git(t, "add", "-A")
        gc = git(t, "commit", "-q", "-m", "init")
        gate("P0 temp git repo", gi.returncode == 0 and gc.returncode == 0, gc.stderr[:200])
        write(t, "CLAUDE.md", "core out of band\n")
        git(t, "add", "CLAUDE.md")
        rc, out = run(PC_PY, t)
        gate("P1 precommit refuses out-of-band staged file", rc == 1 and "REFUSED  staged:CLAUDE.md" in out,
             [l for l in out.splitlines() if "staged:" in l])
        candidate(t, "ch-p", 7, {"CLAUDE.md": "core v7\n"})
        rc_a, out_a = run(RA_PY, t, "apply", "ch-p")
        write(t, "notes/free.md", "free edit\n")
        git(t, "add", "CLAUDE.md", "notes/free.md")
        rc, out = run(PC_PY, t)
        gate("P2 precommit passes applied file + unprotected file", rc_a == 0 and rc == 0 and
             "PASS  staged:CLAUDE.md" in out and "notes/free.md" not in out, "apply rc=%d precommit rc=%d %s" %
             (rc_a, rc, [l for l in out.splitlines() if "staged:" in l]))
        git(t, "commit", "-q", "-m", "applied")
        git(t, "rm", "-q", "--cached", "docs/rules/a.md")
        rc, out = run(PC_PY, t)
        gate("P3 precommit refuses staged deletion", rc == 1 and "deletion of a protected file" in out, "rc=%d" % rc)
    finally:
        shutil.rmtree(t, ignore_errors=True)
    # R real tree, dry baseline only
    led = os.path.join(ROOT, RA.LEDGER_REL)
    had = os.path.exists(led)
    rc, out = run(RA_PY, ROOT, "audit", "--baseline", "--dry")
    line = [l for l in out.splitlines() if l.startswith("BASELINE DRY")]
    gate("R real-tree dry baseline (print only)", rc == 0 and line and os.path.exists(led) == had,
         (line[0] if line else out[-300:]) + " | ledger existed before=%s after=%s" % (had, os.path.exists(led)))
    for l in out.splitlines():
        if l.startswith("BASELINE-FILE"):
            print("  real " + l)
    fails = [n for n, ok in res if not ok]
    print(P.result_line(P.make_result(len(res) - len(fails), len(fails), fails[0] if fails else None)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
