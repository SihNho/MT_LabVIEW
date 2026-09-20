r"""cycle18_arming_driver.py - ONE runner for cycle 18's SECOND half: omission becomes a refusal.

WHAT THIS CHAINS (CLAUDE.md usage discipline, "one batch = one runner = one notification"): the compile check,
the three edits' verification, the FULL six-case launch-gate self-test, `tools/doc_lint.py` and
`tools/doc_ingest.py --cycle 18` - not five turns.

    $env:MATERIAL='1'; py tools\bgrun.py --max-min 25 --log tools\bench\cycle18_arming.log `
        -- py -u tools\bench\cycle18_arming_driver.py

WHAT IT IS TESTING. `tools/prior_art_review.py` used to PRINT `STOP RECORD: NOT ARMED` when `--recipe` was
omitted, and carry on. A device that can be left un-armed by simple omission is not running - it is inert. So an
omission is now a refusal (non-zero exit, correct command form printed) while an explicit, reasoned opt-out
(`--no-recipe "<reason>"`, recorded in the archived review) stays available, the same distinction the GUI gate
makes with `-Exception` + `-Evidence`.

WHY `doc_lint`'s OUTPUT IS NOT ECHOED (same reason as cycle18_stopgate_driver.py, kept deliberately): it prints
"  FAIL  L6: ..." lines and `bgrun`'s inner-failure scan matches `^\s*(?:->\s*)?FAIL\b`, so echoing a PRE-EXISTING
lint failure would end this run rc=1 for something that has nothing to do with it. Full text goes to
tools/bench/cycle18_arming_doc_lint.txt; only counts are printed.

PRIOR ART CHECKED FIRST (CLAUDE.md, "check what already exists"): `ls tools/bench/cycle18_*` -> the cycle-18
stop-gate driver exists and its shape (step/run/doc-lint-to-file) is REUSED here rather than reinvented; the six
acceptance cases live in `tools/bench/stop_record_selftest.py` and are RUN here, not restated.
"""
import glob
import os
import py_compile
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PY = sys.executable
STEPS = []


def step(name, ok, detail=""):
    STEPS.append((name, bool(ok), detail))
    print(("  PASS  " if ok else "  -> FAIL  ") + name + (("   " + detail) if detail else ""), flush=True)
    return bool(ok)


def run(argv, echo=True, timeout=None):
    p = subprocess.run([PY, "-u"] + argv, cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=timeout)
    if echo:
        for line in (p.stdout or "").splitlines():
            print("    | " + line, flush=True)
        if p.stderr:
            for line in p.stderr.splitlines()[:40]:
                print("    ! " + line, flush=True)
    return p


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8", errors="replace") as f:
        return f.read()


def main():
    print("=== cycle 18 (second half) - an OMISSION is a refusal; the opt-out is explicit ===", flush=True)

    print("\n[1] compile", flush=True)
    for t in ("tools/prior_art_review.py", "tools/hooks/guard_cycle.py", "tools/stop_record.py",
              "tools/bench/stop_record_selftest.py"):
        try:
            py_compile.compile(os.path.join(ROOT, t), doraise=True)
            step("compiles: " + t, True)
        except Exception as e:                                   # noqa: BLE001
            step("compiles: " + t, False, repr(e)[:160])

    print("\n[2] item 1 - prior_art_review.py refuses an omission, accepts a reasoned opt-out", flush=True)
    src = read("tools/prior_art_review.py")
    step("the flag exists and its reason is mandatory (metavar REASON)",
         '"--no-recipe"' in src and 'metavar="REASON"' in src)
    step("the silent NOT-ARMED print path is gone",
         "STOP RECORD: NOT ARMED -" not in src and "NOT ARMED BY EXPLICIT OPT-OUT" in src)
    h = run(["tools/prior_art_review.py", "--help"], echo=False)
    step("--help still works and lists both flags",
         h.returncode == 0 and "--no-recipe" in (h.stdout or "") and "--recipe" in (h.stdout or ""))
    r = run(["tools/prior_art_review.py", "--plan", "driver probe", "--slug", "driver-probe"], echo=False)
    out = (r.stdout or "") + (r.stderr or "")
    step("omission -> non-zero exit", r.returncode != 0, "rc %s" % r.returncode)
    step("the refusal prints the CURRENT command form",
         "--recipe tools/recipes/" in out and "--no-recipe" in out and "--plan-file" in out)
    b = run(["tools/prior_art_review.py", "--plan", "x", "--slug", "y", "--recipe", "tools/recipes/a.py",
             "--no-recipe", "both"], echo=False)
    step("both flags together -> refused", b.returncode != 0, "rc %s" % b.returncode)

    print("\n[3] item 2 - guard_cycle's refusal text names the true current command", flush=True)
    g = read("tools/hooks/guard_cycle.py")
    i = g.find("Dispatch it and let it finish")
    blk = g[i:i + 900] if i >= 0 else ""
    step("guard_cycle prints a command carrying --recipe",
         bool(blk) and "--recipe" in blk and "prior_art_review.py" in blk)
    step("... and names the opt-out for a review with genuinely no recipe", "--no-recipe" in blk)

    print("\n[4] item 3 - no ACTIVE file still prescribes the old command form", flush=True)
    # ACTIVE = everything but archive/ (history, never rewritten - CLAUDE.md rule 4) and tools/bench/*.log
    # (execution records of past runs, which are evidence and must keep saying what was really run).
    stale = []
    for pat in ("*.md", "docs/*.md", "tools/*.py", "tools/hooks/*.py", ".claude/*.json",
                ".claude/skills/*/*.md"):
        for p in glob.glob(os.path.join(ROOT, pat)):
            try:
                with open(p, encoding="utf-8", errors="replace") as f:
                    body = f.read()
            except OSError:
                continue
            for m in re.finditer(r"prior_art_review\.py[^\n]*--plan", body):
                window = body[m.start():m.start() + 400]
                # Either arming form counts as current; the OLD form carried neither. (`--no-recipe` does not
                # contain the substring `--recipe`, so the two tests are independent.)
                if "--recipe" not in window and "--no-recipe" not in window:
                    stale.append("%s:%d" % (os.path.relpath(p, ROOT), body[:m.start()].count("\n") + 1))
    step("every active prescription of the command carries --recipe", not stale, ", ".join(stale) or "none")

    print("\n[5] the SIX acceptance cases (plan Pre-decided 4 + the 2026-09-18 arming decision)", flush=True)
    p = run(["tools/bench/stop_record_selftest.py"])
    m = re.search(r"=== stop_record selftest: (\d+) pass, (\d+) fail ===", p.stdout or "")
    step("stop_record_selftest (all six cases)", p.returncode == 0 and bool(m) and m.group(2) == "0",
         m.group(0) if m else "no summary line")

    print("\n[6] doc_lint (full text -> tools/bench/cycle18_arming_doc_lint.txt, not echoed - see docstring)",
          flush=True)
    q = subprocess.run([PY, "-u", os.path.join(ROOT, "tools", "doc_lint.py")], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = (q.stdout or "") + (q.stderr or "")
    with open(os.path.join(HERE, "cycle18_arming_doc_lint.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    summary = ""
    for line in text.splitlines():
        if line.startswith("DOC-LINT"):
            summary = line.strip()
    nfail = len(re.findall(r"^\s{2}FAIL\s", text, re.M))
    nwarn = len(re.findall(r"^\s{2}WARN\s", text, re.M))
    npassl = len(re.findall(r"^\s{2}PASS\s", text, re.M))
    labels = ", ".join(sorted(set(re.findall(r"^\s{2}FAIL\s+(\S+)", text, re.M)))) or "(none)"
    print("    doc_lint summary line : %s" % (summary or "(none)"), flush=True)
    print("    doc_lint counts       : %d pass / %d warn / %d fail   failing checks: %s"
          % (npassl, nwarn, nfail, labels), flush=True)
    step("doc_lint's failing checks are the pre-existing L6 only",
         summary != "" and set(labels.split(", ")) <= {"L6"}, labels)

    print("\n[7] doc_ingest --cycle 18 (sonnet; REPORTED, not gated - a peer outcome is not this build's pass)",
          flush=True)
    try:
        d = run(["tools/doc_ingest.py", "--cycle", "18", "--timeout", "600"], echo=True, timeout=1000)
        dout = (d.stdout or "") + (d.stderr or "")
        contra = re.findall(r"^CONTRADICTIONS:\s*(\S+)", dout, re.M)
        print("  INGEST  rc=%s  CONTRADICTIONS=%s" % (d.returncode, contra[-1] if contra else "?"), flush=True)
    except subprocess.TimeoutExpired:
        print("  INGEST  TIMEOUT after 1000 s (reported, not gated)", flush=True)

    npass = sum(1 for _, ok, _ in STEPS if ok)
    nbad = len(STEPS) - npass
    print("\n=== cycle18 arming driver: %d pass, %d fail ===" % (npass, nbad), flush=True)
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
