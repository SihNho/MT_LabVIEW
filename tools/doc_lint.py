r"""doc_lint.py - the CODE half of CLAUDE.md section 4, "Documents are LINTED by code and INGESTED by a model
every cycle" (user, 2026-09-16: "특정 주기마다 .md 파일들 ingest 및 lint 하는 규약 필요해보임", cadence
"주 단위보다는 싸이클 단위 혹은 실제 실행 단위가 적절해보임").

No model, no judgement, no memory. It reads the documents and reports what is mechanically wrong with them.

WHY IT IS NEEDED AT ALL, in this project's own failures: `GLOSSARY.md` stated the wrong meaning of "Limit of
Program"; `STATUS.md` carried a work order the user had superseded a day earlier; one file's summary line
contradicted its own section 44 lines above; `camera-acquisition-facts.md:183` was quoted to justify an ordering
that `:139` of the same file refutes. Every one of those is a citation nobody re-opened. Claude writes all of these
documents (there is no other author whose discipline could be doubted), so the remedy is a mechanical check on
Claude's own writing - not a resolution to be more careful.

WHAT ALREADY EXISTED, checked before writing a line of this (prior-art review 2026-09-16,
archive/peer/2026-09-16-priorart-doc-lint.md, which fired `already-built` and `helper-exists`):
  * `tools/frontmatter.py` WRITES frontmatter and `--dry-run` lists every .md lacking it. L1 below therefore only
    REPORTS, at WARN, and names that tool as the fix. It does not reimplement it.
  * `tools/audit_cycle.py` A4 already FAILS on a placeholder disposition, with the same file list. L6 is the same
    condition, so `--skip-dispositions` turns it off - and audit_cycle passes that flag when it calls this. One
    condition, one FAIL source; running `doc_lint` standalone still checks it.
  * `tools/hooks/guard_cycle.py:130-137` already resolves a project-relative citation and reports a missing path.
    L2 reuses its shape (normpath under ROOT, isfile) rather than inventing a second resolver.
  * `tools/audit_cycle.py` A7 already lints link DIRECTION (archive must not wikilink into the active set). Not
    repeated here.

CRYING WOLF IS THE FAILURE MODE TO AVOID, and it is recorded: A4's first version "reported 66 false violations on
its first run (2026-09-15) - a checker that cries wolf gets ignored, which is worse than not having it". So L2's
citation matcher is deliberately CONSERVATIVE (a false negative is cheap, a false positive is not): it only
considers backticked or linked spans that look like a project-relative path, and skips globs, URLs, absolute
paths, and anything with a wildcard or angle bracket. L7 is WARN-only and its output is capped, because it fires in
the hundreds and this output is embedded verbatim into the retrospective's evidence block
(`tools/retrospective.py` passes audit stdout to the peer).

  py tools/doc_lint.py                     # PASS/WARN/FAIL lines, exit 1 only on FAIL
  py tools/doc_lint.py --skip-dispositions # L6 off: audit_cycle A4 owns that condition
  py tools/doc_lint.py --quiet             # counts and FAIL lines only (what audit_cycle prints)
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
DOCS = os.path.join(ROOT, "docs")
PEER = os.path.join(ROOT, "archive", "peer")
STATUS_MAX_LINES = 110          # CLAUDE.md section 4 says "~100"; the margin stops a 101-line file crying wolf

# FROZEN DOCUMENTS AND THE LINE CAP (card chat-D1, user 2026-10-02 "만약 문서가 너무 길어진다면 쪼개서 링크 거는 방식이
# 더 좋지 않은지?" -> "문서 정리안 전체"). A long plan is FROZEN IN PLACE (`status: frozen`, old lines and their numbers
# unchanged, footer appended; tools/bench/freeze_docs_d1.py) and its in-force items are indexed in a short
# `docs/<dir>/INDEX.md`. L10 caps every other active doc under docs/ at DOC_MAX_LINES (FAIL). Reference TABLES are
# looked up, not read through, so they only WARN with their size. GRANDFATHERED = docs that were already over the cap
# when it was introduced and were not named by the card (measured 2026-10-02); they WARN until judgement freezes,
# splits or exempts each one - the list only shrinks.
DOC_MAX_LINES = 400
INDEX_DIRS = ("d1",)                                  # docs/<dir>/*.md are active docs too
NOT_CAPPED_STATUS = ("frozen", "superseded")
EXEMPT_REFERENCE = ("docs/NAMES.md", "docs/toolkit-capabilities.md", "docs/camera-acquisition-facts.md")
GRANDFATHERED = ("docs/gpu-backend.md", "docs/frame-loop-wire-graph.md", "docs/restructure-plan-4.6.md",
                 "docs/keystone-op-spec.md", "docs/main-vi-panel-map.md")
FROZEN_FOOTER_RE = re.compile(r"^## FROZEN \d{4}-\d{2}-\d{2}", re.M)

RESULT = []                     # (level, check, detail) - level in PASS / WARN / FAIL


def say(level, check, detail):
    RESULT.append((level, check, detail))


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def active_docs():
    """The ACTIVE set: docs/*.md, the index directories (`docs/d1/*.md`, card chat-D1 2026-10-02) and the two root
    documents. Not archive/ - history is allowed to be stale, that is what makes it history (CLAUDE.md rule 4)."""
    out = sorted(glob.glob(os.path.join(DOCS, "*.md")))
    for d in INDEX_DIRS:
        out += sorted(glob.glob(os.path.join(DOCS, d, "*.md")))
    for n in ("STATUS.md", "CLAUDE.md"):
        p = os.path.join(ROOT, n)
        if os.path.isfile(p):
            out.append(p)
    return out


def rel(p):
    return os.path.relpath(p, ROOT).replace(os.sep, "/")


# ---------------------------------------------------------------- frontmatter

FM_RE = re.compile(r"\A﻿?---\r?\n(.*?)\r?\n---\r?\n", re.S)


def frontmatter(body):
    """The YAML block as a flat dict, or None. Deliberately not a YAML parser: these blocks are machine-written by
    tools/frontmatter.py and are `key: value` lines only."""
    m = FM_RE.match(body)
    if not m:
        return None
    d = {}
    for line in m.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            d[k.strip()] = v.strip()
    return d


def check_frontmatter():
    missing, invalid = [], []
    targets = active_docs() + sorted(glob.glob(os.path.join(PEER, "*.md")))
    for p in targets:
        fm = frontmatter(read(p))
        if fm is None:
            missing.append(rel(p))
        elif not all(k in fm for k in ("type", "status", "date")):
            invalid.append(f"{rel(p)} (has {sorted(fm)})")
    n = len(targets)
    if missing or invalid:
        say("WARN", "L1 frontmatter present and valid",
            f"{n - len(missing) - len(invalid)}/{n} ok; {len(missing)} missing, {len(invalid)} incomplete. "
            f"Fix with `py tools/frontmatter.py`. first: {(missing + invalid)[:5]}")
    else:
        say("PASS", "L1 frontmatter present and valid", f"{n}/{n} ok")


# ---------------------------------------------------------------- citations

# A citation is a backticked span, a markdown link target, or a bare path followed by `:line`. Only spans that
# LOOK like a project-relative path are considered - see the crying-wolf note in the module docstring.
SPAN_RE = re.compile(r"`([^`\n]{3,200})`|\]\(([^)\s]{3,200})\)")
TOPDIRS = ("docs/", "tools/", "archive/", "project-requirements/", ".claude/")
EXTS = (".md", ".py", ".ps1", ".json", ".log", ".txt", ".vi", ".ctl", ".toml", ".yaml", ".yml")
LINE_SUFFIX_RE = re.compile(r"^(?P<path>[^\s:]+?):(?P<a>\d+)(?:-(?P<b>\d+))?$")


def citation_candidates(body):
    """(path, lineno_or_None, line_number_in_the_document) for every span that is plausibly a project path."""
    starts = [0]
    for ch in body.splitlines(keepends=True):
        starts.append(starts[-1] + len(ch))

    def lineno(off):
        lo, hi = 0, len(starts) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if starts[mid] <= off:
                lo = mid
            else:
                hi = mid - 1
        return lo + 1

    for m in SPAN_RE.finditer(body):
        raw = (m.group(1) or m.group(2) or "").strip()
        # `{,2,3}` is brace notation and `...` is an elision, both measured as false positives on the first run
        # (`tools/recipes/probe_allow_private{,2,3}.py`, `archive/peer/...gui-rule-hole-analysis-review.md`).
        if not raw or any(c in raw for c in "*<>|?\"' {}") or "..." in raw:
            continue
        if raw.startswith(("http://", "https://", "#", "mailto:")) or re.match(r"^[A-Za-z]:[\\/]", raw):
            continue
        raw = raw.replace("\\", "/").lstrip("./")
        ln = None
        sm = LINE_SUFFIX_RE.match(raw)
        if sm:
            raw, ln = sm.group("path"), int(sm.group("a"))
        # A BARE FILENAME IS A NAME, NOT A CITATION - measured on the first run, which reported 545 "dangling" of
        # 1008 and was therefore worthless. `OpFP_v0.vi`, `Create.vi`, `test_oploopcast.log` and `build_x.py` are
        # how docs/NAMES.md and docs/GLOSSARY.md refer to things; they are identifiers, and resolving them would
        # need a search path this checker must not invent. So: a citation is a path with a DIRECTORY in it, rooted
        # at one of the project's top-level directories. That is a deliberate false negative (A4's lesson of
        # 2026-09-15: a checker that cries wolf gets ignored, which is worse than not having it).
        if not raw.startswith(TOPDIRS) or "/" not in raw:
            continue
        if raw.endswith("/") or not raw.endswith(EXTS):
            continue
        yield raw, ln, lineno(m.start())


def check_citations():
    dangling, forward, overshoot, seen = [], [], [], 0
    for p in active_docs():
        body = read(p)
        # A PLAN NAMES WHAT DOES NOT EXIST YET - that is what a plan is. `docs/cycle14-plan.md` cites the recipe,
        # log and JSON its cycle will produce, and calling those "dangling" would make this check FAIL on every
        # correctly-written plan, i.e. cry wolf permanently. They are still reported, as a WARN, because a plan
        # citing a file that never appears is exactly the drift worth seeing.
        is_plan = re.search(r"-plan\.md$", rel(p)) is not None
        for path, ln, at in citation_candidates(body):
            seen += 1
            fp = os.path.normpath(os.path.join(ROOT, path.replace("/", os.sep)))
            if not os.path.isfile(fp):
                (forward if is_plan else dangling).append(f"{rel(p)}:{at} -> {path}")
                continue
            if ln is not None:
                try:
                    total = sum(1 for _ in open(fp, encoding="utf-8", errors="replace"))
                except OSError:
                    continue
                if ln > total:
                    overshoot.append(f"{rel(p)}:{at} -> {path}:{ln} (file has {total} lines)")
    if dangling:
        say("FAIL", "L2 every cited project path exists",
            f"{len(dangling)} DANGLING of {seen} citations checked:\n" + "".join(f"       {d}\n" for d in dangling))
    else:
        say("PASS", "L2 every cited project path exists", f"{seen} citations checked, none dangling")
    if forward:
        say("WARN", "L2c plan documents cite files that do not exist yet",
            f"{len(forward)} forward reference(s) in plan documents (expected while the cycle is open): "
            f"{forward[:6]}")
    else:
        say("PASS", "L2c plan documents cite files that do not exist yet", "no forward references outstanding")
    if overshoot:
        say("WARN", "L2b cited line numbers are in range",
            f"{len(overshoot)} citation(s) point past the end of the file: {overshoot[:5]}")
    else:
        say("PASS", "L2b cited line numbers are in range", "no citation points past a file's end")


# ---------------------------------------------------------------- the rest

def check_status_length():
    p = os.path.join(ROOT, "STATUS.md")
    n = len(read(p).splitlines())
    if n > STATUS_MAX_LINES:
        say("WARN", "L3 STATUS.md stays one screen",
            f"STATUS.md:{n} lines > {STATUS_MAX_LINES}. CLAUDE.md rule 4: move the narrative to "
            f"archive/<date>-status-<topic>.md, keep lock, hardware, state, OPEN, NEXT.")
    else:
        say("PASS", "L3 STATUS.md stays one screen", f"{n} lines (limit {STATUS_MAX_LINES})")


def current_plans(docs=None):
    """Every `docs/cycle*-plan.md` (or `docs/<dir>/INDEX.md`) whose frontmatter says `status: current`, as ABSOLUTE paths.

    THE ONE predicate for "the plan" in this project - L4 below, L8, and `audit_cycle.py`'s C7 scope check all
    call this rather than keeping a copy.  C7 used to build `docs/cycle<N>-plan.md` from the cycle number, which
    went DEAD the moment the scheme moved to one plan spanning cycles 27+ (STATUS.md OPEN 56); repointing it here
    means a future rename of the scheme breaks one function, not three.  Sorted, so the caller's `[0]` is stable
    when L4 is (wrongly) reporting more than one.

    card chat-D1 (2026-10-02): an index `docs/<dir>/INDEX.md` with `status: current` is a plan too - the long cycle
    plans were frozen in place and the index is now the plan the cycle prompt, L8, C7's fallback and the
    retrospective's plan pointer read. `docs` is for the self-test only."""
    docs = docs or DOCS
    out = []
    cands = sorted(glob.glob(os.path.join(docs, "cycle*-plan.md"))) + sorted(glob.glob(os.path.join(docs, "*", "INDEX.md")))
    for p in cands:
        if (frontmatter(read(p)) or {}).get("status") == "current":
            out.append(p)
    return out


def check_one_current_plan():
    cur = [rel(p) for p in current_plans()]
    if len(cur) > 1:
        say("FAIL", "L4 at most one current plan per family",
            f"{len(cur)} cycle plans are `status: current`: {cur}. Every window, gate and C7 scope check reads "
            f"'the plan', and with two current ones it is ambiguous which.")
    else:
        say("PASS", "L4 at most one current plan per family", f"{cur or 'none'} current")


PREDECIDED_MARK_RE = re.compile(r"^#{2,6}\s*Pre-decided\b", re.M | re.I)


def check_predecided():
    """L8: the CURRENT cycle plan carries a `## Pre-decided` section (CLAUDE.md section 3 item 2, 2026-09-17).

    WARN, not FAIL: a plan is legitimately born without one, and a linter that cries wolf gets ignored (A4's
    lesson of 2026-09-15). But the section is what lets a material session APPLY a decision instead of returning
    "blocked-on-judgement" and costing a whole judgement turn - the cost STATUS.md recorded on 2026-09-17 ("a
    material session that returns blocked-on-judgement on a question the plan already answers costs a full turn
    here"). With cycles now spawned one per session by tools/cycle_runner.py, that turn is a whole session.
    """
    cur = current_plans()
    missing = [rel(p) for p in cur if not PREDECIDED_MARK_RE.search(read(p))]
    if not cur:
        say("PASS", "L8 the current plan has a `## Pre-decided` section", "no current cycle plan to check")
    elif missing:
        say("WARN", "L8 the current plan has a `## Pre-decided` section",
            f"{', '.join(missing)} has no `## Pre-decided` heading. It is the list a material session applies "
            f"without asking; without it every settled question comes back as a judgement turn.")
    else:
        say("PASS", "L8 the current plan has a `## Pre-decided` section", f"{', '.join(rel(p) for p in cur)} ok")


def check_supersedes():
    bad = []
    all_fm = {}
    for p in active_docs():
        all_fm[rel(p)] = frontmatter(read(p)) or {}
    for src, fm in all_fm.items():
        tgt = fm.get("supersedes", "")
        for t in re.findall(r"[\w./-]+\.md", tgt):
            t = t.replace("\\", "/").lstrip("./")
            if all_fm.get(t, {}).get("status") == "current":
                bad.append(f"{src} supersedes {t}, which is still `status: current`")
    if bad:
        say("WARN", "L5 superseded documents are not still current", "; ".join(bad[:5]))
    else:
        say("PASS", "L5 superseded documents are not still current",
            "no `supersedes:` target is still marked current")


DISPOSITION_MARK = "## What was done with it"
PLACEHOLDER = "(Claude fills in)"


def check_dispositions():
    """`disposition: legacy` in the frontmatter is EXCLUDED, and the exclusion is the point.

    2026-09-16: 64 of 272 peer archives were still on the `(Claude fills in)` placeholder. The disposition
    discipline itself dates from 2026-09-15; for the 39 exchanges older than that, nobody recorded at the time what
    was done with them, so a disposition written now would be reconstructed rather than remembered - a guess in a
    fact's clothes. Those 39 were closed as `disposition: legacy` by `tools/mark_legacy_dispositions.py` (which
    states the cutoff and its gates) and are skipped here. The 26 dated 2026-09-15 or later are NOT skipped: those
    are real debt owed by the sessions that dispatched them, and they keep this check FAILing until written.
    """
    blank, legacy = [], 0
    files = sorted(glob.glob(os.path.join(PEER, "*.md")))
    for p in files:
        body = read(p)
        if (frontmatter(body) or {}).get("disposition") == "legacy":
            legacy += 1
            continue
        i = body.find(DISPOSITION_MARK)
        tail = body[i + len(DISPOSITION_MARK):].strip() if i >= 0 else ""
        if i < 0 or not tail or tail.startswith(PLACEHOLDER):
            blank.append(rel(p))
    n = len(files) - legacy
    # 39 pre-2026-09-15 (2026-09-16 backfill) + 48 dated 2026-09-15..21 (2026-09-25, card chat-L1, --cutoff 2026-09-22)
    suffix = f" ({legacy} closed as `disposition: legacy`, skipped)" if legacy else ""
    if blank:
        say("FAIL", "L6 archived reviews are disposed",
            f"{n - len(blank)}/{n} disposed; {len(blank)} still blank or placeholder{suffix}. "
            f"first: {blank[:5]}")
    else:
        say("PASS", "L6 archived reviews are disposed", f"{n}/{n} disposed{suffix}")


# WARN ONLY, AND CAPPED. This fires in the hundreds by construction and its output is embedded verbatim in the
# retrospective's evidence block, so an uncapped list would drown the audit it rides on.
DECISION_WORD_RE = re.compile(r"\b(decided|MEASURED)\b|결정|측정")
DECISION_MARK_RE = re.compile(r"\b(DECIDED|MEASURED|DECISION|ANSWERED|FAILED)\s*:")


def check_marked_decisions():
    hits = []
    for p in active_docs():
        for i, line in enumerate(read(p).splitlines(), 1):
            if DECISION_WORD_RE.search(line) and not DECISION_MARK_RE.search(line):
                hits.append(f"{rel(p)}:{i}")
    if hits:
        say("WARN", "L7 decision/measurement sentences carry a mark",
            f"{len(hits)} unmarked line(s); a fact stated without `DECIDED:`/`MEASURED:`/`DECISION:` has to be "
            f"inferred rather than extracted. first: {hits[:5]}")
    else:
        say("PASS", "L7 decision/measurement sentences carry a mark", "all marked")


# L8 - violation-decisions.md decision headers carry a PARSEABLE HH:MM (card 116-3 D2; review
# archive/peer/2026-09-25-retrospective-cycle77.md F2(a), ACCEPTED, "header lint for violation-decisions.md HH:MM").
# tools/violations.py DEC_RE reads `## <slug> - YYYY-MM-DD HH:MM`; a time written as `19:2x` / `05:5x` is silently
# read as a BARE date (00:00), which misordered guard_cycle's discharge on 2026-09-25 (retrospective-cycle77.md:271).
# JUDGEMENT 116-3 OPEN-2: a header dated >= L8_FAIL_FROM that lacks a parseable HH:MM FAILs; an OLDER header whose
# time is present but unparseable WARNs (historic headers are not edited); an older bare date is not reported.
L8_FAIL_FROM = "2026-09-28"
DEC_HEAD_RE = re.compile(r"^##\s*([a-z0-9-]+)\s*[-—]\s*(\d{4}-\d{2}-\d{2})(.*)$")
DEC_TIME_RE = re.compile(r"^[ T]+\d{2}:\d{2}(?!\d|[xX])")      # the shape violations.py DEC_RE accepts, no `x`
TIMEISH_RE = re.compile(r"^[ T]+\d{1,2}:\S")


def check_decision_headers(path=None):
    p = path or os.path.join(DOCS, "violation-decisions.md")
    fails, warns = [], []
    try:
        name = rel(p)
    except ValueError:                       # a file on another drive (a self-test sandbox): keep the absolute path
        name = p.replace("\\", "/")
    for i, line in enumerate(read(p).splitlines(), 1):
        m = DEC_HEAD_RE.match(line)
        if not m or DEC_TIME_RE.match(m.group(3)):
            continue
        where = f"{name}:{i}"
        if m.group(2) >= L8_FAIL_FROM:
            fails.append(where)
        elif TIMEISH_RE.match(m.group(3)):
            warns.append(where)
    if fails:
        say("FAIL", "L8 decision headers carry HH:MM",
            f"{len(fails)} header(s) dated >= {L8_FAIL_FROM} without a parseable HH:MM (violations.py DEC_RE reads "
            f"them as bare dates): {fails[:10]}")
    elif warns:
        say("WARN", "L8 decision headers carry HH:MM",
            f"{len(warns)} older header(s) with an unparseable time (historic, not edited): {warns[:10]}")
    else:
        say("PASS", "L8 decision headers carry HH:MM", "all parse")
    return fails, warns


# L9 - a Pre-decided item carries a `USER-RULES:` line (card chat-P2 item 1, user 2026-09-28 "1~4번 적용"). Before a
# judgement session writes a new Pre-decided DESIGN item it reads docs/user-rules.md and writes `USER-RULES: U4, U6`
# (the rows it relies on) or `USER-RULES: none apply` in the item. Items numbered >= L9_FROM_ITEM (the first number
# written after 2026-09-28 17:xx; the numbering is shared by every plan's Pre-decided sections) are checked; older ones
# are history and never edited. WARN only: the line is a prompt for the reader, not a gate.
L9_FROM_ITEM = 238
PD_ITEM_RE = re.compile(r"^(\d{2,4})\.\s")
PD_END_RE = re.compile(r"^#{1,6}\s")
USER_RULES_LINE_RE = re.compile(r"USER-RULES:\s*\S")


def predecided_items(body):
    """[(number, first_line_no, text)] for every numbered item inside a `Pre-decided` section of one document."""
    out, in_pd, cur, lvl = [], False, None, 0
    for i, line in enumerate(body.splitlines(), 1):
        if PD_END_RE.match(line):
            if cur:
                out.append(cur)
                cur = None
            h = len(line) - len(line.lstrip("#"))
            if PREDECIDED_MARK_RE.match(line):
                in_pd, lvl = True, h
            elif not (in_pd and h > lvl):          # a deeper sub-heading stays inside the Pre-decided section
                in_pd = False
            continue
        if not in_pd:
            continue
        m = PD_ITEM_RE.match(line)
        if m:
            if cur:
                out.append(cur)
            cur = (int(m.group(1)), i, line + "\n")
        elif cur:
            cur = (cur[0], cur[1], cur[2] + line + "\n")
    if cur:
        out.append(cur)
    return out


def check_user_rules_lines(paths=None):
    miss = []
    for p in (paths if paths is not None else active_docs()):
        body = read(p)
        if not PREDECIDED_MARK_RE.search(body):
            continue
        try:
            name = rel(p)
        except ValueError:
            name = p.replace("\\", "/")
        for n, ln, text in predecided_items(body):
            if n >= L9_FROM_ITEM and not USER_RULES_LINE_RE.search(text):
                miss.append(f"{name}:{ln} (item {n})")
    if miss:
        say("WARN", "L9 new Pre-decided items carry a USER-RULES: line",
            f"{len(miss)} item(s) >= {L9_FROM_ITEM} without `USER-RULES:` (read docs/user-rules.md and cite the rows "
            f"relied on, or write `USER-RULES: none apply`): {miss[:10]}")
    else:
        say("PASS", "L9 new Pre-decided items carry a USER-RULES: line", f"every item >= {L9_FROM_ITEM} carries one")
    return miss


def _docname(p):
    try:
        return rel(p)
    except ValueError:
        return p.replace("\\", "/")


def is_frozen(p):
    return (frontmatter(read(p)) or {}).get("status") == "frozen"


def check_line_cap(paths=None, names=None):
    """L10 (card chat-D1): an active doc under docs/ that is not frozen/superseded stays <= DOC_MAX_LINES lines.
    `paths` / `names` (published names, e.g. `docs/NAMES.md`) exist for the self-test, which runs on a temp tree."""
    if paths is None:
        paths = [p for p in active_docs() if os.path.normpath(p).startswith(os.path.normpath(DOCS) + os.sep)]
    names = names or [_docname(p) for p in paths]
    fails, ref_warn, gf_warn, frozen = [], [], [], 0
    for p, nm in zip(paths, names):
        st = (frontmatter(read(p)) or {}).get("status", "")
        if st in NOT_CAPPED_STATUS:
            frozen += st == "frozen"
            continue
        n = len(read(p).splitlines())
        if n <= DOC_MAX_LINES:
            continue
        if nm in EXEMPT_REFERENCE:
            ref_warn.append(f"{nm} {n}")
        elif nm in GRANDFATHERED:
            gf_warn.append(f"{nm} {n}")
        else:
            fails.append(f"{nm} {n}")
    if fails:
        say("FAIL", "L10 active docs stay <= %d lines" % DOC_MAX_LINES,
            f"{len(fails)} doc(s) over the cap: {fails}. Freeze in place (`status: frozen` + footer, "
            f"tools/bench/freeze_docs_d1.py) and index what is in force, or split into linked topic files.")
    else:
        say("PASS", "L10 active docs stay <= %d lines" % DOC_MAX_LINES,
            f"none over the cap ({frozen} frozen doc(s) not capped)")
    if ref_warn:
        say("WARN", "L10a reference tables over the cap (exempt)", "; ".join(ref_warn))
    if gf_warn:
        say("WARN", "L10b grandfathered docs over the cap (judgement: freeze, split or exempt)", "; ".join(gf_warn))
    return fails, ref_warn, gf_warn


def check_frozen_footer(paths=None):
    """L11 (card chat-D1): a `status: frozen` doc carries its FROZEN footer, which names the index to read instead."""
    paths = paths if paths is not None else active_docs()
    bad = [_docname(p) for p in paths if is_frozen(p) and not FROZEN_FOOTER_RE.search(read(p))]
    if bad:
        say("WARN", "L11 frozen docs carry a FROZEN footer", f"{len(bad)} without one: {bad[:10]}")
    else:
        n = sum(1 for p in paths if is_frozen(p))
        say("PASS", "L11 frozen docs carry a FROZEN footer", f"{n} frozen doc(s), all with a footer")
    return bad


def run(skip_dispositions=False):
    del RESULT[:]
    check_frontmatter()
    check_citations()
    check_status_length()
    check_one_current_plan()
    check_predecided()
    check_supersedes()
    if not skip_dispositions:
        check_dispositions()
    else:
        say("PASS", "L6 archived reviews are disposed", "skipped - audit_cycle A4 owns this condition")
    check_marked_decisions()
    check_decision_headers()
    check_user_rules_lines([p for p in active_docs() if not is_frozen(p)])   # frozen items are never edited (chat-D1)
    check_line_cap()
    check_frozen_footer()
    return list(RESULT)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--skip-dispositions", action="store_true",
                    help="turn L6 off; tools/audit_cycle.py A4 checks the same condition and owns the FAIL")
    ap.add_argument("--quiet", action="store_true", help="counts and FAIL lines only")
    a = ap.parse_args()
    res = run(a.skip_dispositions)
    fails = [r for r in res if r[0] == "FAIL"]
    warns = [r for r in res if r[0] == "WARN"]
    for level, check, detail in res:
        if a.quiet and level != "FAIL":
            continue
        print(f"  {level}  {check}: {detail}", flush=True)
    print(f"DOC-LINT {'PASS' if not fails else 'FAIL'}: {len(fails)} fail, {len(warns)} warn, "
          f"{len(res) - len(fails) - len(warns)} pass\n", flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
