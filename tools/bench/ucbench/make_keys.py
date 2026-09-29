r"""make_keys - compute the MECHANICAL answer keys of ucbench L2 / L3 at their base commit (card chat-B3).

    py tools/bgrun.py --material --max-min 10 --log tools/bench/ucbench/make_keys.log -- py -u tools/bench/ucbench/make_keys.py

PREDICTION CONTRACT: one worktree at BASE (%TEMP%\ucb\keys), the BASE's own tools run there (no LabVIEW: doc_lint.py
and violations.py are pure-file readers): `py tools/violations.py` (slug -> retrospectives table) and
`py tools/doc_lint.py --skip-dispositions` (broken path / file:line citations). Raw stdout saved to keys/*.txt, the
worktree removed. The key extraction from the raw text happens in tasks.json building (next step), not here.
Ends with a RESULT line.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "matbench"))
import matbench as MB  # noqa: E402

BASE = sys.argv[1] if len(sys.argv) > 1 else "9635538^"
WT = os.path.join(os.environ.get("TEMP", r"C:\Windows\Temp"), "ucb", "keys")
OUT = os.path.join(HERE, "keys")
os.makedirs(OUT, exist_ok=True)
MB.remove_wt(WT)
MB.git("worktree", "add", "--detach", WT, BASE)
arts, fails = [], []
try:
    # L2 key = EVERY missing citation (doc_lint prints only the first 6 plan forward references), from the base's own
    # active_docs() + citation_candidates(), i.e. exactly doc_lint L2 + L2c without the output cap
    l2 = ("import sys, os, json; sys.path.insert(0, 'tools'); import doc_lint as D\n"
          "out = []\n"
          "for p in D.active_docs():\n"
          "    for path, ln, at in D.citation_candidates(D.read(p)):\n"
          "        fp = os.path.normpath(os.path.join(D.ROOT, path.replace('/', os.sep)))\n"
          "        if not os.path.isfile(fp):\n"
          "            out.append({'doc': D.rel(p), 'line': at, 'path': path, 'plan': D.rel(p).endswith('-plan.md')})\n"
          "print(json.dumps(out, indent=1))\n")
    for name, cmd in (("violations_base", [sys.executable, "tools/violations.py"]),
                      ("doc_lint_base", [sys.executable, "tools/doc_lint.py", "--skip-dispositions"]),
                      ("l2_missing_citations", [sys.executable, "-c", l2])):
        r = subprocess.run(cmd, cwd=WT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
        p = os.path.join(OUT, name + ".txt")
        with open(p, "w", encoding="utf-8") as f:
            f.write("# base %s  rc %s  cmd %s\n" % (MB.git("rev-parse", BASE).strip(), r.returncode, " ".join(cmd[1:])))
            f.write(r.stdout + ("\n--- stderr ---\n" + r.stderr if r.stderr.strip() else ""))
        print("KEYSRC %s rc %s lines %d" % (name, r.returncode, r.stdout.count("\n")), flush=True)
        arts.append({"path": os.path.relpath(p, MB.MAIN).replace("\\", "/"), "md5": MB.md5(p)})
        if not r.stdout.strip():
            fails.append(name + " empty")
finally:
    MB.remove_wt(WT)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                              "gates": {"pass": 3 - len(fails), "fail": len(fails)},
                              "first_fail": fails[0] if fails else None, "artefacts": arts}), flush=True)
