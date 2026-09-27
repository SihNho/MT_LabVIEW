"""card 115-1 C1 (retrospective-cycle114 discriminating test, archive/peer/2026-09-28-retrospective-cycle114.md:398): the
accepted review dispositions of 2026-09-25..28 whose NAMED FIX is absent from the code. Read-only; no LabVIEW; builds nothing.

    py tools/bench/diag_c115a_dispositions.py

Existed first: tools/doc_lint.py checks dispositions are not placeholders and prior_art_review's FIXED: rule checks a
cited path exists - neither checks the named fix is IN that file. This reads ONLY each file's `## What was done with it`
section and reports:
  A. every `path:line` / `path` citation of a tools/ or docs/ file in a disposition -> present (file exists, line within
     length) / absent;
  B. every disposition line that says a fix was accepted but NOT applied (deferral words) -> printed as DEFER for a manual
     code check (the manual verdicts are the card's C1 facts, not this script's).
Prediction contract: prints COUNT lines and one RESULT line (PASS = the scan ran; the absent list is a finding, not a fail).
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

CITE = re.compile(r"((?:tools|docs)/[A-Za-z0-9_./\-]+\.(?:py|json|md|ps1))(?::(\d+))?")
DEFER = re.compile(r"(?i)\b(not applied|not yet applied|deferred|left open|returned (?:to [a-z ]+ )?as open|still open|"
                   r"not built|not run|owed|to a later card|next card)\b")


def sections():
    for p in sorted(glob.glob(os.path.join(ROOT, "archive", "peer", "2026-09-2[5-8]-*.md"))):
        on, out = False, []
        for n, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
            if line.startswith("## What was done with it"):
                on = True
                continue
            if on and line.startswith("## "):
                on = False
            if on:
                out.append((n, line.rstrip("\n")))
        yield os.path.relpath(p, ROOT).replace("\\", "/"), out


def main():
    n_files = n_cite = n_present = 0
    absent, defers, lens = [], [], {}
    for rp, sec in sections():
        n_files += 1
        for n, line in sec:
            for path, ln in CITE.findall(line):
                n_cite += 1
                fp = os.path.join(ROOT, path)
                if not os.path.isfile(fp):
                    absent.append("{0}:{1} cites {2} - file absent".format(rp, n, path))
                    continue
                if ln:
                    if fp not in lens:
                        lens[fp] = sum(1 for _ in open(fp, encoding="utf-8", errors="replace"))
                    if int(ln) > lens[fp]:
                        absent.append("{0}:{1} cites {2}:{3} - file has {4} lines".format(rp, n, path, ln, lens[fp]))
                        continue
                n_present += 1
            if DEFER.search(line):
                defers.append("{0}:{1}: {2}".format(rp, n, line.strip()[:300]))
    for a in absent:
        print("ABSENT " + a)
    for d in defers:
        print("DEFER " + d)
    print("COUNT dispositions {0}; citations {1}: present {2} / absent {3}; defer lines {4}".format(
        n_files, n_cite, n_present, len(absent), len(defers)))
    print(protocol.result_line(protocol.make_result(1, 0, None)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
