r"""frontmatter.py - give every markdown document a YAML frontmatter block, so the vault is navigable in Obsidian
AND greppable by the session.

WHY BOTH. Obsidian's backlink graph lives in the app, not in the files - Claude cannot read it. YAML frontmatter and
`[[wikilinks]]` are plain text, so they are the one representation both readers share (user, 2026-09-15). The most
valuable field is `status`, because a superseded document otherwise looks exactly like a current one: the E0 note
"the case sits after the kernel" stayed authoritative-looking for hours after the measurement disproved it.

LINK DIRECTION RULE (user, 2026-09-15: "아카이브는 아카이브 끼리만 관리하는게 좋을까?"). Archive notes must not
wikilink INTO the active set, or the graph fills with 200+ peer exchanges around every live document:

    active  -> active     wikilink, freely
    active  -> archive    wikilink, deliberately (an active claim citing its evidence)
    archive -> archive    wikilink
    archive -> active     plain path only, never a wikilink

`tools/audit_cycle.py` checks that last line; this script never writes a link that breaks it.

  py tools/frontmatter.py --dry-run          # show what would change
  py tools/frontmatter.py                    # write
  py tools/frontmatter.py --scope archive    # peer exchanges and narrative only

Fields written (an existing frontmatter block is left alone except for missing keys):
  type      reference | plan | measurement | decision | narrative | peer-review | rules | status
  status    current | superseded | historical      (archive defaults to historical)
  tags      derived from the path and the filename, plus the project-wide ones
  date      from the filename when it starts with a date, else the file's mtime
"""
import argparse
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})")
# `.agents/skills/` is the PORTABLE skill - it gets copied into other LabVIEW projects, so it must not carry this
# project's tags (CLAUDE.md: LabVIEW know-how is packaged to be exported, not as project-local notes).
SKIP_DIRS = {".git", ".obsidian", "node_modules", "__pycache__", ".claude", ".agents"}

# path prefix -> (type, status, extra tags). First match wins.
RULES = [
    ("archive/peer/",        ("peer-review", "historical", ["peer-review"])),
    ("archive/benchmarks/",  ("measurement", "current",    ["benchmark", "index"])),
    ("archive/",             ("narrative",   "historical", ["archive"])),
    ("docs/",                ("reference",   "current",    ["docs"])),
    ("project-requirements/", ("decision",   "current",    ["requirements", "user-source"])),
    ("STATUS.md",            ("status",      "current",    ["hand-off"])),
    ("CLAUDE.md",            ("rules",       "current",    ["rules"])),
    ("AGENTS.md",            ("rules",       "current",    ["rules", "peer-review"])),
    ("LEARNING.md",          ("reference",   "current",    ["teaching"])),
    ("README.md",            ("reference",   "current",    [])),
]
# filename fragment -> tag. Cheap, and it is what makes the graph filterable.
NAME_TAGS = [
    ("stage2", "stage2"), ("step-e", "reseed"), ("reseed", "reseed"), ("queue", "producer-consumer"),
    ("kernel", "kernel"), ("gpu", "gpu"), ("rotor", "rotor"), ("camera", "camera"), ("motor", "motor"),
    ("panel", "main-vi"), ("main-vi", "main-vi"), ("names", "vi-scripting"), ("toolkit", "vi-scripting"),
    ("opconstvalue", "vi-scripting"), ("opwiresource", "vi-scripting"), ("optunnelread", "vi-scripting"),
    ("opcaseframes", "vi-scripting"), ("retrospective", "process"), ("plan", "plan"), ("fixture", "fixture"),
    ("benchmark", "benchmark"), ("question", "open-question"), ("gui", "gui"),
]


def classify(rel):
    p = rel.replace("\\", "/")
    for prefix, (typ, status, tags) in RULES:
        if p.startswith(prefix) or p == prefix:
            return typ, status, list(tags)
    return "reference", "current", []


def tags_for(rel, base_tags):
    low = os.path.basename(rel).lower()
    tags = list(base_tags)
    for frag, tag in NAME_TAGS:
        if frag in low and tag not in tags:
            tags.append(tag)
    return tags


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--scope", default="all", choices=["all", "active", "archive"])
    a = ap.parse_args()
    written = skipped = 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, ROOT).replace("\\", "/")
            is_archive = rel.startswith("archive/")
            if a.scope == "active" and is_archive:
                continue
            if a.scope == "archive" and not is_archive:
                continue
            body = open(full, encoding="utf-8", errors="replace").read()
            if body.lstrip("﻿").startswith("---\n"):
                skipped += 1
                continue
            typ, status, base = classify(rel)
            tags = tags_for(rel, base)
            m = DATE_RE.match(fn)
            date = m.group(1) if m else time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(full)))
            fm = ("---\n"
                  f"type: {typ}\n"
                  f"status: {status}\n"
                  f"date: {date}\n"
                  f"tags: [{', '.join(tags)}]\n"
                  "---\n\n")
            if a.dry_run:
                print(f"  + {rel}: type={typ} status={status} tags={tags}")
            else:
                bom = "﻿" if body.startswith("﻿") else ""
                with open(full, "w", encoding="utf-8") as f:
                    f.write(bom + fm + body.lstrip("﻿"))
            written += 1
    print(f"\n{'would write' if a.dry_run else 'wrote'} frontmatter in {written} file(s); "
          f"{skipped} already had one\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
