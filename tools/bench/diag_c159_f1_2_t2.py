# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/brief_159-f1-2.md
# ---
r"""diag_c159_f1_2_t2 - card 159-f1-2, MEASURE only. Re-runs selftest_c134_1_dry's T2 (selftest_c134_1_dry.py:83-84:
`stage_prerun --dry tools/recipes/stage_d1_ring_p3b2a.py --no-record` must end `=== DRY PASS:` rc 0 `unverified 0`) under
module swaps, WITHOUT touching any tools/*.py on disk: a child process installs a sys.meta_path finder that serves the named
fleet modules from other bytes (a kept file or a git revision) but with __file__ = the real tools/<name>.py, so HERE/ROOT/BENCH
resolve exactly as in a normal run; stage_prerun itself is exec'd as __main__ the same way (as `py tools/stage_prerun.py`).
No COM, no LabVIEW (the dry stubs COM; dry fences subprocess and writes outside %TEMP%); scratch bytes live only in memory.
EXISTING checked: selftest_c134_1_dry.py (T2 itself; module-level code, not importable), stage_prerun.dry (stage_prerun.py:1014).
The git-by-md5 helper is inline in selftest_c134_1_dry.py:32, selftest_x10_c130_1.py:28, matbench.py:86 (no shared one); this
script takes explicit revisions instead (found by hand with git log), so it copies none of them.
PREDICTION (none of these is a pass criterion of the tools; each config's DRY line is recorded):
  C0 current bytes -> DRY FAIL first_fail GATE PB (reproduces selftest_c134_1_dry_c159_f1_1.log:6).
  C1..C7 -> measured, not predicted (the card's question).
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c159_f1_2_t2.log -- py -u tools/bench/diag_c159_f1_2_t2.py"""
import hashlib, importlib.abc, importlib.util, json, os, subprocess, sys, time     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
RECIPE = os.path.join(TOOLS, "recipes", "stage_d1_ring_p3b2a.py")
K9 = "tools/bench/selftest_c159_cen2_ends_stagekit_9cd8822e.txt"
CONFIGS = [   # (label, {module: "file:<rel>" | "git:<rev>"}, all_from_rev)
    ("C0 current bytes", {}, None),
    ("C1 stagekit 9cd8822e", {"stagekit": "file:" + K9}, None),
    ("C2 stagekit 9cd8822e + stage_prerun HEAD (9decb20f, pre-PD387(e))", {"stagekit": "file:" + K9, "stage_prerun": "git:HEAD"}, None),
    ("C3 stagekit 9cd8822e + addrcheck 951efd0e (first)", {"stagekit": "file:" + K9, "addrcheck": "git:951efd0e"}, None),
    ("C4 stagekit 9cd8822e + addrcheck 589685c8", {"stagekit": "file:" + K9, "addrcheck": "git:589685c8"}, None),
    ("C5 stage_prerun HEAD (9decb20f) alone", {"stage_prerun": "git:HEAD"}, None),
    ("C6 every tools/*.py at 421d6108 (2026-10-02 15:04, commit of the last 11/0 log)", {}, "421d6108"),
    ("C7 every tools/*.py at HEAD a9d0da22 (2026-10-09 22:51)", {}, "HEAD"),
]


def md5b(b):
    return hashlib.md5(b).hexdigest()


def src_bytes(spec, name):
    kind, ref = spec.split(":", 1)
    if kind == "file":
        return open(os.path.join(ROOT, ref), "rb").read()
    return subprocess.run(["git", "show", "{0}:tools/{1}.py".format(ref, name)], cwd=ROOT, capture_output=True, check=True).stdout


class Serve(importlib.abc.MetaPathFinder, importlib.abc.Loader):
    def __init__(self, srcs):
        self.srcs = srcs

    def find_spec(self, name, path=None, target=None):
        if name in self.srcs:
            return importlib.util.spec_from_loader(name, self, origin=os.path.join(TOOLS, name + ".py"))
        return None

    def create_module(self, spec):
        return None

    def exec_module(self, module):
        fn = os.path.join(TOOLS, module.__name__ + ".py")
        module.__file__ = fn
        exec(compile(self.srcs[module.__name__], fn, "exec"), module.__dict__)


def child(cfg_i):
    _label, mods, rev = CONFIGS[cfg_i]
    srcs = {}
    if rev:
        names = subprocess.run(["git", "ls-tree", "--name-only", rev, "tools/"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.split()
        for p in names:
            if p.endswith(".py") and p.count("/") == 1:
                n = os.path.basename(p)[:-3]
                srcs[n] = src_bytes("git:" + rev, n)
    for n, spec in mods.items():
        srcs[n] = src_bytes(spec, n)
    print("SERVED " + json.dumps(dict((n, md5b(b)[:8]) for n, b in sorted(srcs.items()) if n in
                                     ("stagekit", "stage_prerun", "addrcheck", "stagexec", "stagesim", "vigraph", "jev_candidates", "gscript"))), flush=True)
    sp = srcs.pop("stage_prerun", None) or open(os.path.join(TOOLS, "stage_prerun.py"), "rb").read()
    sys.meta_path.insert(0, Serve(srcs))
    sys.path[0] = TOOLS
    sys.argv = [os.path.join(TOOLS, "stage_prerun.py"), "--dry", RECIPE, "--no-record"]
    fn = os.path.join(TOOLS, "stage_prerun.py")
    exec(compile(sp, fn, "exec"), {"__name__": "__main__", "__file__": fn, "__builtins__": __builtins__})


def main():
    sys.path.insert(0, TOOLS)
    import protocol as P                                                           # noqa: E402
    md0 = dict((n, md5b(open(os.path.join(TOOLS, n + ".py"), "rb").read())[:8]) for n in ("stagekit", "stage_prerun", "stagesim", "stagexec", "addrcheck"))
    print("MD5 BEFORE " + json.dumps(md0), flush=True)
    print("RECIPE md5 " + md5b(open(RECIPE, "rb").read()), flush=True)
    out_rows = []
    for i, (label, _m, _r) in enumerate(CONFIGS):
        t0 = time.time()
        p = subprocess.run([sys.executable, "-u", os.path.abspath(__file__), "--child", str(i)], cwd=ROOT, capture_output=True, text=True,
                           timeout=300, encoding="utf-8", errors="replace")
        lines = p.stdout.splitlines()
        dl = [x for x in lines if x.startswith("=== DRY ")]
        dl = dl[-1] if dl else "NO DRY LINE: " + (p.stdout[-300:] + p.stderr[-600:]).replace("\n", " | ")
        t2 = dl.startswith("=== DRY PASS:") and p.returncode == 0 and "unverified 0" in dl
        served = [x for x in lines if x.startswith("SERVED ")]
        keep = [x.strip()[:400] for x in lines if any(k in x for k in (" PB ", "  D new", "  TD ", "CEN2", "  FR ", "UNVERIFIED", "UNROUTABLE", "FAIL  "))]
        print("\n### {0}  ({1:.0f} s, rc {2})".format(label, time.time() - t0, p.returncode), flush=True)
        print("  " + (served[0] if served else "SERVED ?"), flush=True)
        for x in keep[:14]:
            print("   | " + x, flush=True)
        print("  T2 {0}  {1}".format("PASS" if t2 else "FAIL", dl[:330]), flush=True)
        out_rows.append({"cfg": label, "t2": "PASS" if t2 else "FAIL", "rc": p.returncode, "dry": dl[:330]})
    md1 = dict((n, md5b(open(os.path.join(TOOLS, n + ".py"), "rb").read())[:8]) for n in ("stagekit", "stage_prerun", "stagesim", "stagexec", "addrcheck"))
    print("MD5 AFTER " + json.dumps(md1) + (" UNCHANGED" if md1 == md0 else " CHANGED"), flush=True)
    json.dump(out_rows, open(os.path.join(HERE, "diag_c159_f1_2_t2.json"), "w", encoding="utf-8"), indent=1)
    c0_fail = out_rows[0]["t2"] == "FAIL" and "GATE PB" in out_rows[0]["dry"]
    ok = c0_fail and md1 == md0 and all(not r["dry"].startswith("NO DRY LINE") for r in out_rows)
    print(P.result_line({"status": "PASS" if ok else "FAIL", "gates": {"pass": int(c0_fail) + int(md1 == md0), "fail": int(not c0_fail) + int(md1 != md0)},
                         "first_fail": None if ok else ("C0 did not reproduce PB" if not c0_fail else "md5 changed or a config printed no DRY line"),
                         "artefacts": [{"path": "tools/bench/diag_c159_f1_2_t2.json", "md5": md5b(open(os.path.join(HERE, "diag_c159_f1_2_t2.json"), "rb").read())}]}), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--child":
        child(int(sys.argv[2]))
    else:
        sys.exit(main())
