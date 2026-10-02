r"""prep_c138_3_combos - card 138-3 pass 1 (offline, no LabVIEW): run selftest_c133_1_fsroutes + selftest_c133_6_fr in 4 module
combinations (head / simexec = new stagesim+stagexec / prerun = new stage_prerun / new = all three new).
Why not `git worktree`: the permission layer refuses `git worktree add` and `git archive` in this session (asked 2026-10-02 17:3x).
Equivalent isolation here: tools/bench/wt_c138_3/<combo>/tools/ = copies of every top-level tools/*.py + directory JUNCTIONS
to every tools/ subdirectory (bench, recipes, ...; committed fixtures, clean vs HEAD - checked below), and the three modules
placed per combo (HEAD bytes from `git show HEAD:<path>`). Tests compute ROOT from abspath(__file__), which keeps the junction
path, so they import the combo's modules. The main tree is never checked out or stashed. Prior art: prep_c138_1_regress.py
--head (preloaded HEAD copies from another dir; broke on module-relative paths, prep_c138_1_regress_head.log) - fixed here by
giving each combo its own root.
PREDICTION: 8 runs complete; table printed; `--clean` removes the trees (junctions unlinked, never followed). RESULT line."""
import hashlib, json, os, re, shutil, subprocess, sys, _winapi                      # noqa: E401
B = os.path.dirname(os.path.abspath(__file__)); R = os.path.dirname(os.path.dirname(B))   # noqa: E702
sys.path.insert(0, os.path.join(R, "tools"))
import protocol as P                                                                 # noqa: E402
WT = os.path.join(B, "wt_c138_3")
MODS = ["stagesim.py", "stagexec.py", "stage_prerun.py"]
COMBOS = {"head": [], "simexec": ["stagesim.py", "stagexec.py"], "prerun": ["stage_prerun.py"], "new": MODS}
TESTS = ["selftest_c133_1_fsroutes.py", "selftest_c133_6_fr.py"]
RES_RE = re.compile(r"^RESULT (\{.*\})\s*$", re.M)
md5 = lambda b: hashlib.md5(b).hexdigest()                                           # noqa: E731
git = lambda *a: subprocess.run(["git"] + list(a), cwd=R, capture_output=True)       # noqa: E731


def is_junction(p):
    try:
        return bool(os.lstat(p).st_file_attributes & 0x400)
    except OSError:
        return False


def clean():
    if not os.path.isdir(WT):
        return 0
    n = 0
    for c in os.listdir(WT):
        t = os.path.join(WT, c, "tools")
        if os.path.isdir(t):
            for e in os.listdir(t):
                p = os.path.join(t, e)
                if is_junction(p):
                    os.rmdir(p); n += 1                                              # noqa: E702 - unlinks the junction only
        left = [e for e in (os.listdir(t) if os.path.isdir(t) else []) if is_junction(os.path.join(t, e))]
        assert not left, "junction still present - refusing to walk: %s" % left
        for dp, dn, fn in os.walk(os.path.join(WT, c), topdown=False):
            for f in fn:
                os.remove(os.path.join(dp, f))
            for d in dn:
                os.rmdir(os.path.join(dp, d))
        os.rmdir(os.path.join(WT, c))
    os.rmdir(WT)
    return n


def main():
    if "--clean" in sys.argv:
        n = clean()
        print("CLEAN junctions unlinked", n, "wt exists", os.path.exists(WT), "bench still has", len(os.listdir(B)), "entries")
        print(P.result_line(P.make_result(int(not os.path.exists(WT)), int(os.path.exists(WT)), None if not os.path.exists(WT) else "clean")))
        return 0
    tools = os.path.join(R, "tools")
    top = sorted(f for f in os.listdir(tools) if f.endswith(".py") and os.path.isfile(os.path.join(tools, f)))
    subs = sorted(d for d in os.listdir(tools) if os.path.isdir(os.path.join(tools, d)) and d != "__pycache__")
    dirty = [ln for ln in git("status", "--porcelain", "--", "tools/*.py").stdout.decode().splitlines()]
    print("FACT top-level tools/*.py dirty vs HEAD:", dirty)
    fx = git("status", "--porcelain", "--", "tools/recipes", "tools/bench/plan_ring_p3b2.json", "tools/bench/plan_ring_p3b2a.json",
             "tools/bench/plan_ring_p3b2b.json", "tools/bench/plan_ring_p3b1.json", "tools/bench/sim/ring_p3b2_base_real_fsmap.json",
             "tools/bench/graph_ring_p3b1_20261002_073225.json", "tools/bench/graph_ring_p3b2a_fs_20261002_102553.json",
             "tools/bench/selftest_c133_1_fsroutes.py", "tools/bench/selftest_c133_6_fr.py").stdout.decode().strip()
    print("FACT fixtures/tests dirty vs HEAD: [%s]" % fx)
    head = {}
    for m in MODS:
        b = git("show", "HEAD:tools/" + m).stdout
        head[m] = b
        print("FACT %s HEAD md5 %s (%d B) work md5 %s" % (m, md5(b), len(b), md5(open(os.path.join(tools, m), "rb").read())))
    os.makedirs(WT, exist_ok=True)
    for c, newm in COMBOS.items():
        t = os.path.join(WT, c, "tools")
        os.makedirs(t, exist_ok=True)
        for f in top:
            shutil.copyfile(os.path.join(tools, f), os.path.join(t, f))
        for m in MODS:
            if m not in newm:
                open(os.path.join(t, m), "wb").write(head[m])
        for d in subs:
            if not os.path.exists(os.path.join(t, d)):
                _winapi.CreateJunction(os.path.join(tools, d), os.path.join(t, d))
        print("TREE %s new=%s md5s %s" % (c, newm, [md5(open(os.path.join(t, m), "rb").read())[:8] for m in MODS]))
    procs = {}
    for c in COMBOS:
        for tst in TESTS:
            root = os.path.join(WT, c)
            procs[(c, tst)] = subprocess.Popen([sys.executable, "-u", os.path.join(root, "tools", "bench", tst)], cwd=root,
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    rows, bad = [], 0
    for (c, tst), p in procs.items():
        try:
            out, err = p.communicate(timeout=1000)
        except subprocess.TimeoutExpired:
            p.kill(); out, err = p.communicate()                                     # noqa: E702
        m = RES_RE.findall(out or "")
        r = json.loads(m[-1]) if m else {}
        fails = [ln[:300] for ln in (out or "").splitlines() if ln.startswith("FAIL")]
        g = r.get("gates") or {}
        rows.append((c, tst, p.returncode, r.get("status", "NO-RESULT"), g.get("pass"), g.get("fail"), fails, (err or "").strip()[-300:]))
        print("ROW %-8s %-30s rc=%s %s pass=%s fail=%s" % rows[-1][:6], flush=True)
        for f in fails:
            print("    | " + f)
        if not r:
            print("    | stderr: " + (err or "").strip()[-400:].replace("\n", " / "))
        bad += r.get("status") != "PASS"
    print(P.result_line(P.make_result(len(rows) - bad, bad, None if not bad else "see ROW lines", [])))
    return 0


if __name__ == "__main__":
    sys.exit(main())
