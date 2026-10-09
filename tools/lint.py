# ---
# labview: none
# hardware: none
# ---
"""lint.py - ruff (config: ruff.toml at the project root) counted per rule and per folder class (card chat-L1,
user 2026-10-09: lint the codebase after cycle 156).

Folder classes (classify()):
  shared  - tools/*.py, tools/hooks/*.py, and every file in tools/bench/capabilities_shared.json (the import graph
            gen_capabilities writes: files another file imports)
  recipe  - tools/recipes/*.py (records of what ran; listed, never rewritten)
  bench   - every other tools/bench/**.py (one-off benches / diagnostics)
  other   - anything else under tools/

Usage:
  py tools/lint.py                      counts table (rule x class) + RESULT line
  py tools/lint.py --files shared       per-file findings for one class (file:line code message)
  py tools/lint.py --codes F821,F811    restrict to codes
  py tools/lint.py --self-test          offline self-test on canned ruff JSON (no ruff run)
Existing tooling checked first: doc_lint.py lints docs only; guard_write.py compiles single files; no ruff wrapper
existed (grep "ruff" tools/*.py -> none).
"""
import argparse
import json
import os
import subprocess
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED_JSON = os.path.join(ROOT, "tools", "bench", "capabilities_shared.json")
CLASSES = ("shared", "recipe", "bench", "other")


def norm(path):
    """Project-relative forward-slash path of `path` (absolute or relative). Returns str. Self-test: --self-test."""
    p = os.path.abspath(os.path.join(ROOT, path)) if not os.path.isabs(path) else path
    try:
        p = os.path.relpath(p, ROOT)
    except ValueError:
        pass
    return p.replace("\\", "/")


def load_shared(path=SHARED_JSON):
    """Set of project-relative paths in capabilities_shared.json (empty set if missing). Self-test: --self-test."""
    try:
        with open(path, encoding="utf-8") as f:
            return {norm(x) for x in json.load(f).get("files", [])}
    except (OSError, ValueError):
        return set()


def classify(path, shared):
    """Folder class of a file: 'shared' | 'recipe' | 'bench' | 'other' (see module docstring). Self-test: --self-test."""
    p = norm(path)
    parts = p.split("/")
    if p in shared:
        return "shared"
    if len(parts) == 2 and parts[0] == "tools":
        return "shared"
    if len(parts) == 3 and parts[:2] == ["tools", "hooks"]:
        return "shared"
    if len(parts) >= 3 and parts[:2] == ["tools", "recipes"]:
        return "recipe"
    if len(parts) >= 3 and parts[:2] == ["tools", "bench"]:
        return "bench"
    return "other"


def run_ruff(target="tools"):
    """Run ruff over `target` with the project ruff.toml; returns the list of finding dicts (ruff JSON)."""
    r = subprocess.run([sys.executable, "-m", "ruff", "check", target, "--output-format", "json", "--exit-zero"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return json.loads(r.stdout or "[]")


def tabulate(findings, shared, codes=None):
    """Counter keyed (code, class) plus per-class per-file lists. Returns (counts, files). Self-test: --self-test."""
    counts = Counter()
    files = defaultdict(list)
    for f in findings:
        code = f.get("code") or "E999"
        if codes and code not in codes:
            continue
        cls = classify(f["filename"], shared)
        counts[(code, cls)] += 1
        files[cls].append((norm(f["filename"]), f["location"]["row"], code, f.get("message", "")))
    return counts, files


def table_text(counts):
    """Markdown table rule x class with totals. Returns str. Self-test: --self-test."""
    codes = sorted({c for c, _ in counts}, key=lambda c: -sum(counts[(c, k)] for k in CLASSES))
    out = ["| rule | " + " | ".join(CLASSES) + " | total |", "|---|" + "---:|" * (len(CLASSES) + 1)]
    for c in codes:
        row = [counts[(c, k)] for k in CLASSES]
        out.append("| %s | %s | %d |" % (c, " | ".join(str(x) for x in row), sum(row)))
    tot = [sum(counts[(c, k)] for c in codes) for k in CLASSES]
    out.append("| **total** | %s | %d |" % (" | ".join(str(x) for x in tot), sum(tot)))
    return "\n".join(out)


def self_test():
    shared = {"tools/bench/fntest_lib.py"}
    cases = [("tools/stagekit.py", "shared"), ("tools/hooks/guard_bash.py", "shared"),
             ("tools/bench/fntest_lib.py", "shared"), ("tools/bench/diag_x.py", "bench"),
             ("tools/recipes/stage_a.py", "recipe"), ("tools/bench/sub/x.py", "bench"),
             (os.path.join(ROOT, "tools", "lint.py"), "shared"), ("tools/x/y.py", "other")]
    ok = fail = 0
    for p, want in cases:
        got = classify(p, shared)
        if got == want:
            ok += 1
        else:
            fail += 1
            print("FAIL classify", p, got, want)
    canned = [{"code": "F401", "filename": os.path.join(ROOT, "tools", "a.py"), "location": {"row": 3}, "message": "m"},
              {"code": "F401", "filename": os.path.join(ROOT, "tools", "recipes", "r.py"), "location": {"row": 4},
               "message": "m"},
              {"code": None, "filename": os.path.join(ROOT, "tools", "bench", "b.py"), "location": {"row": 1},
               "message": "syntax"}]
    counts, files = tabulate(canned, shared)
    checks = [counts[("F401", "shared")] == 1, counts[("F401", "recipe")] == 1, counts[("E999", "bench")] == 1,
              files["shared"][0][:3] == ("tools/a.py", 3, "F401"), "| **total** | 1 | 1 | 1 | 0 | 3 |" in table_text(counts),
              tabulate(canned, shared, codes={"F401"})[0][("E999", "bench")] == 0,
              len(load_shared()) > 0]
    for i, c in enumerate(checks):
        if c:
            ok += 1
        else:
            fail += 1
            print("FAIL check", i)
    return ok, fail


def main():
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import protocol
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", choices=CLASSES)
    ap.add_argument("--codes", default="")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.self_test:
        ok, fail = self_test()
        print("SELFTEST lint.py %d/%d" % (ok, fail))
        print(protocol.result_line(protocol.make_result(ok, fail, None if not fail else "lint self-test")))
        return 1 if fail else 0
    codes = {c.strip() for c in a.codes.split(",") if c.strip()} or None
    counts, files = tabulate(run_ruff(), load_shared(), codes)
    print(table_text(counts))
    if a.files:
        for p, row, code, msg in sorted(files[a.files]):
            print("%s:%d %s %s" % (p, row, code, msg))
    print(protocol.result_line(protocol.make_result(1, 0)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
