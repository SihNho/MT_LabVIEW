r"""mark_legacy_dispositions.py - one-shot backfill: `disposition: legacy` on the PRE-2026-09-15 peer archives.

WHY (judgement call made 2026-09-16, executed here, not decided here). `doc_lint` L6 / `audit_cycle` A4 FAIL on
64 of 272 archived peer exchanges whose "## What was done with it" section is still the `(Claude fills in)`
placeholder. Writing 64 real dispositions retroactively would be inventing history: for exchanges older than
2026-09-15 - the day the disposition discipline itself was adopted - nobody recorded what was done with them at
the time, and a disposition reconstructed now from the transcript is a guess wearing a fact's clothes.

So the pre-2026-09-15 backlog is CLOSED AS LEGACY, explicitly and in the file, rather than left to cry wolf
forever; the post-2026-09-15 ones stay FAILing, because those are real debt that the sessions which dispatched
them were supposed to discharge. `doc_lint.check_dispositions()` skips `disposition: legacy` for exactly this
reason (see its comment).

Existing tools checked before writing this (CLAUDE.md "before creating any new op, tool, or recipe"):
  * `tools/frontmatter.py` writes frontmatter but only the fixed field set (type/status/tags/date) - it has no way
    to set an arbitrary key, and it is a vault-wide pass, not a filtered backfill. Its block FORMAT is reused here
    verbatim (archive/peer/ -> type: peer-review, status: historical, date from the filename) so the two agree.
  * `tools/doc_lint.py` only reports; `tools/audit_cycle.py` A4 only reports.
  * no existing recipe or bench script writes peer-archive frontmatter.

PREDICTION CONTRACT (checked by the script itself, printed as GATE lines):
  G1  every file it touches is under archive/peer/ and is dated strictly before 2026-09-15
  G2  every file it touches is currently UNDISPOSED by doc_lint's own rule (missing section, empty, or placeholder)
  G3  no file's body below the frontmatter changes - only a frontmatter key is added/created
  G4  after the run, `doc_lint`'s undisposed set contains ZERO pre-2026-09-15 files

  py tools/mark_legacy_dispositions.py --dry-run
  py tools/mark_legacy_dispositions.py
"""
import argparse
import glob
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PEER = os.path.join(ROOT, "archive", "peer")

CUTOFF = "2026-09-15"                      # strictly before this date -> legacy
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
FM_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.S)
DISPOSITION_MARK = "## What was done with it"
PLACEHOLDER = "(Claude fills in)"


def read(p):
    # utf-8-SIG, deliberately. Several of these archives were written with a BOM, and a BOM sits BEFORE the
    # opening `---`, so `doc_lint.frontmatter()` (plain utf-8) reports them as having no frontmatter at all and
    # this script would otherwise prepend a SECOND block. Files it rewrites are written back BOM-less.
    with open(p, encoding="utf-8-sig", errors="replace") as f:
        return f.read()


def fm_dict(body):
    m = FM_RE.match(body)
    if not m:
        return None
    d = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def undisposed(body):
    i = body.find(DISPOSITION_MARK)
    tail = body[i + len(DISPOSITION_MARK):].strip() if i >= 0 else ""
    return i < 0 or not tail or tail.startswith(PLACEHOLDER)


def body_below_fm(body):
    m = FM_RE.match(body)
    return body[m.end():] if m else body


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(PEER, "*.md")))
    touched, skipped_recent, no_date = [], [], []
    g1 = g2 = g3 = True

    for p in files:
        name = os.path.basename(p)
        body = read(p)
        if not undisposed(body):
            continue
        m = DATE_RE.match(name)
        if not m:
            no_date.append(name)
            continue
        date = m.group(1)
        if date >= CUTOFF:
            skipped_recent.append(name)
            continue

        fm = fm_dict(body)
        if fm is not None and "disposition" in fm:
            continue
        before_body = body_below_fm(body)
        if fm is None:
            block = (
                "---\n"
                "type: peer-review\n"
                "status: historical\n"
                f"date: {date}\n"
                "tags: [peer-review, archive, labview]\n"
                "disposition: legacy\n"
                "---\n\n"
            )
            new = block + body
        else:
            mm = FM_RE.match(body)
            keys = mm.group(1).rstrip("\r\n")
            new = "---\n" + keys + "\ndisposition: legacy\n---\n" + body[mm.end():]
        if body_below_fm(new) != before_body:
            g3 = False
        if not (p.startswith(PEER) and date < CUTOFF):
            g1 = False
        touched.append((name, "created" if fm is None else "key-added"))
        if not a.dry_run:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(new)

    for name, _ in touched:
        if not DATE_RE.match(name) or DATE_RE.match(name).group(1) >= CUTOFF:
            g2 = False

    print(f"peer archives scanned : {len(files)}")
    print(f"marked legacy         : {len(touched)}" + (" (dry run)" if a.dry_run else ""))
    print(f"left FAILing (>= {CUTOFF}) : {len(skipped_recent)}")
    for n in skipped_recent:
        print(f"    DEBT {n}")
    if no_date:
        print(f"no date in filename   : {len(no_date)} -> {no_date}")

    # G4 re-read from disk
    g4 = True
    if not a.dry_run:
        for p in sorted(glob.glob(os.path.join(PEER, "*.md"))):
            b = read(p)
            if not undisposed(b):
                continue
            fmx = fm_dict(b) or {}
            if fmx.get("disposition") == "legacy":
                continue
            mm = DATE_RE.match(os.path.basename(p))
            if mm and mm.group(1) < CUTOFF:
                g4 = False
                print(f"    G4 MISS {os.path.basename(p)}")
    for label, ok in (("G1 all touched are archive/peer and pre-cutoff", g1),
                      ("G2 all touched were undisposed", g2),
                      ("G3 body below frontmatter unchanged", g3),
                      ("G4 no pre-cutoff file left undisposed-and-unmarked", g4)):
        print(f"GATE {'PASS' if ok else 'FAIL'}  {label}")
    return 0 if (g1 and g2 and g3 and g4) else 1


if __name__ == "__main__":
    sys.exit(main())
