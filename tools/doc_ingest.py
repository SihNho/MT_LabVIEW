r"""doc_ingest.py - the MODEL half of CLAUDE.md section 4, "Documents are LINTED by code and INGESTED by a model
every cycle" (user, 2026-09-16).

"INGEST" MEANS A MODEL READS THE DOCUMENTS AND REPORTS WHAT CONTRADICTS WHAT. It is explicitly NOT an index: an
index was built for the prior-art reviewer, benchmarked against eight real items, and lost - 6.5/8 recall without
it against 5.0/8 with, and 22 % cheaper without (tools/bench/priorart_scores.md). Handed an index, a cell treats it
as the corpus and stops searching. So there is no index here either, only files.

IT REPORTS, IT NEVER RESOLVES. Which of two contradicting documents is right is judgement work (CLAUDE.md section
4's own table says so), and a recommendation from this layer would be a decision taken in the wrong session. The
task text forbids recommendations, and the peer preamble in peer.ps1 (-Role ingest) forbids them again.

WHAT THIS REUSES RATHER THAN REBUILDS (prior-art review 2026-09-16, archive/peer/2026-09-16-priorart-doc-lint.md,
which fired `helper-exists`, `already-failed` and `unread-evidence`):
  * the CHANGED-FILES list is `tools/audit_cycle.py`'s C7, parsed from its own output - not a second walker.
  * the WINDOW is `tools/retrospective.py:cycle_window()` when --cycle is given - not a second window rule.
  * the REVIEWER is the rule/consistency auditor `peer.ps1` already defines, pinned to sonnet, reached through the
    existing `-Role` mechanism (`-Role ingest`), not through a fourth `-Kind`.
  * the DISPATCH SCAFFOLDING is the shape of `tools/prior_art_review.py` (build task -> temp file -> peer.ps1).
  * `tools/logclass.py` now registers `doc_ingest`/`ingest_` as MACHINERY. This is the finding that mattered most:
    four dispatchers have broken this project by having an unregistered log name, and this one quotes documents
    VERBATIM - including their own `FAIL` and `STOP at gate` lines - so an unregistered log would have been scanned
    as a build failure and would have blocked the next build (guard_peer.py:85-89 records exactly that happening).

INVISIBLE TO EVERY GATE, BY DIRECTORY. The archive goes to `archive/ingest/`. guard_peer.py, guard_cycle.py,
violations.py, outcome_review.py and audit_cycle.py (A3 at the `any newer archive/peer/*.md` test, A4 at the
disposition scan) all glob `archive/peer/` only - verified 2026-09-16. Had an ingest pass landed there it would
have satisfied A3 for every failing log in the window, which is the failed-prediction gate switching itself off.
The one deliberate exception is audit A7 (archive wikilink direction), which walks `archive/**` and should.

  py tools/doc_ingest.py --cycle 14                    # the cycle's changed files, sonnet
  py tools/doc_ingest.py --from "2026-09-16 00:00"     # an explicit window
  py tools/doc_ingest.py --full --model opus           # all of docs/ + STATUS + CLAUDE.md, every 5 cycles
  py tools/doc_ingest.py --from ... --dry-run          # print the file list and the task, dispatch nothing
"""
import argparse
import glob
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ALWAYS = ("STATUS.md", "CLAUDE.md")

TASK_HEAD = """DOCUMENT INGEST (per-cycle consistency read).

Read the files listed below. Report ONE thing and nothing else:

  every pair of statements that CONTRADICT each other, or that contradict CLAUDE.md or STATUS.md.

Rules, all mandatory:
 1. Cite `file:line` for BOTH sides of every pair. A pair with one citation is not reportable - drop it.
 2. Quote the two statements, short, verbatim.
 3. NO RECOMMENDATIONS. Do not say which side is right, which should be changed, or what to do about it. The
    judgement session decides that; a recommendation from you is a decision taken in the wrong place.
 4. A summary line that contradicts its own section 40 lines earlier counts, and has happened in these files.
    So does a document asserting a value, a count, a time or a rule that another document states differently.
 5. Do not report stylistic differences, wording changes, or a document simply being older. A contradiction is
    two statements that cannot both be true.
 6. If you find none, say `CONTRADICTIONS: 0` and stop.

End your answer with one line:
  CONTRADICTIONS: <n>
and above it, one block per pair in this exact shape:

  PAIR <n>
    A: <file>:<line>  "<quote>"
    B: <file>:<line>  "<quote>"
    conflict: <one sentence naming what cannot both be true>
"""


def parse_ts(s):
    if not s:
        return None
    s = str(s).strip()
    try:
        return float(s)
    except ValueError:
        pass
    for f in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return time.mktime(time.strptime(s, f))
        except ValueError:
            continue
    raise SystemExit(f"cannot parse timestamp {s!r}")


def fmt(t):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(t))


C7_RE = re.compile(r"^\s*C7 files modified in the window but NOT named in [^:]+:\s*\d+\s*-\s*(.*)$", re.M)


def changed_files(start, end, cycle):
    """The cycle's changed .md files, from audit_cycle's own C7 line plus a direct mtime sweep of the ACTIVE docs.

    C7 is the `scope-creep` device (docs/violation-decisions.md, 2026-09-16 round 3) and already answers "what
    changed in this window that the plan did not name". It TRUNCATES its printed list at 12 entries and excludes
    files the plan DID name, so it is used as one input, not as the whole answer: the active documents are also
    swept directly by mtime. Two sources, union, deduplicated - a missed document is the failure mode here, and a
    duplicate costs nothing.
    """
    out = set()
    cmd = [sys.executable, os.path.join(HERE, "audit_cycle.py"),
           "--from", "%.0f" % start, "--to", "%.0f" % end]
    if cycle is not None:
        cmd += ["--cycle", str(cycle)]
    try:
        txt = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=300).stdout
        m = C7_RE.search(txt)
        if m and m.group(1).strip() not in ("none", ""):
            for item in m.group(1).split(","):
                item = item.strip().rstrip("…").strip()
                if item.endswith(".md"):
                    out.add(item)
    except Exception as e:                        # a broken audit must not silence the ingest
        print(f"   NOTE: audit_cycle C7 unavailable ({e}); falling back to the mtime sweep alone", flush=True)
    for p in sorted(glob.glob(os.path.join(ROOT, "docs", "*.md"))) + \
            [os.path.join(ROOT, n) for n in ALWAYS]:
        try:
            if start <= os.path.getmtime(p) <= end:
                out.add(os.path.relpath(p, ROOT).replace(os.sep, "/"))
        except OSError:
            continue
    for n in ALWAYS:                              # always, changed or not: they are what everything else contradicts
        if os.path.isfile(os.path.join(ROOT, n)):
            out.add(n)
    return sorted(out)


def full_set():
    out = [os.path.relpath(p, ROOT).replace(os.sep, "/")
           for p in sorted(glob.glob(os.path.join(ROOT, "docs", "*.md")))]
    return sorted(set(out) | {n for n in ALWAYS if os.path.isfile(os.path.join(ROOT, n))})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", type=int, default=None, help="derive the window from tools/retrospective.py")
    ap.add_argument("--from", dest="ts_from", default=None, help="window start, epoch or 'YYYY-MM-DD HH:MM'")
    ap.add_argument("--to", dest="ts_to", default=None, help="window end (default: now)")
    ap.add_argument("--full", action="store_true", help="all of docs/ + STATUS + CLAUDE.md (the 5-cycle pass)")
    ap.add_argument("--model", default="sonnet", help="sonnet per cycle; opus for --full every 5 cycles")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.full:
        files, basis = full_set(), "--full: every active document"
    else:
        if a.ts_from:
            start, end = parse_ts(a.ts_from), (parse_ts(a.ts_to) or time.time())
            basis = f"explicit window {fmt(start)} .. {fmt(end)}"
        elif a.cycle is not None:
            import retrospective
            start, end, wb = retrospective.cycle_window(a.cycle)
            if start is None:
                print(f"cannot derive a window for cycle {a.cycle}: {wb}")
                return 2
            basis = f"cycle {a.cycle} window {fmt(start)} .. {fmt(end)} ({wb})"
        else:
            print("need --cycle, --from or --full")
            return 2
        files = changed_files(start, end, a.cycle)

    listing = "\n".join(f"  {f}" for f in files)
    task = (f"{TASK_HEAD}\n=== THE FILES ({len(files)}) - read every one; they are relative to the project root "
            f"===\n{listing}\n\n=== HOW THIS SET WAS CHOSEN ===\n{basis}\nSTATUS.md and CLAUDE.md are always in "
            f"the set: they are the documents everything else can contradict.\n")

    slug = a.slug or f"ingest-{time.strftime('%Y-%m-%d')}" + ("-full" if a.full else "")
    scratch = os.path.join(os.environ.get("TEMP", "."), f"docingest_{slug}.txt")
    with open(scratch, "w", encoding="utf-8") as f:
        f.write(task)
    print(f"   {len(files)} file(s); {basis}", flush=True)
    print(f"   task written to {scratch} ({len(task)} chars)", flush=True)
    if a.dry_run:
        print(task)
        return 0

    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           f"& '{os.path.join(HERE, 'peer.ps1')}' -Agent claude -Role ingest -Kind fact "
           f"-Model {a.model} -TimeoutSec {a.timeout} -Slug {slug} -Task (Get-Content -Raw '{scratch}')"]
    r = subprocess.run(cmd, cwd=ROOT, text=True, timeout=a.timeout + 300)

    arch = os.path.join(ROOT, "archive", "ingest", f"{time.strftime('%Y-%m-%d')}-{slug}.md")
    n = "?"
    if os.path.isfile(arch):
        body = open(arch, encoding="utf-8", errors="replace").read()
        answer = body.split("## Answer", 1)[-1]
        m = re.findall(r"^CONTRADICTIONS:\s*(\d+)", answer, re.M)
        n = m[-1] if m else str(len(re.findall(r"^\s*PAIR\s+\d+", answer, re.M)))
    print(f"   peer.ps1 rc {r.returncode}; archived as archive/ingest/{os.path.basename(arch)}", flush=True)
    print(f"CONTRADICTIONS: {n}", flush=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
