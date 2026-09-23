"""Second pass (cycle 73 material, CLAUDE.md rule 4 / material brief "STATUS over ~110 lines: relocate the narrative
yourself"): move seven HISTORICAL cycle-67/68 `## NEXT` paragraphs VERBATIM into §3 of the same archive file.
Kept in STATUS: the DESK-CHECK rule (Pre-decided 132), TWO REPAIRS (open repairs), CARRY/commit/cap lines."""
import io
import os

ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
ST = os.path.join(ROOT, "STATUS.md")
AR = os.path.join(ROOT, "archive", "2026-09-24-status-cycle72-relocate.md")
PREFIXES = [
    "\U0001F7E2\U0001F7E2 **M3a-4 DELIVERED 2026-09-23 18:5x \u2014 THE FIRST",
    "\U0001F7E0 (SUPERSEDED the same cycle",
    "\U0001F535 **MODELS RE-PINNED 2026-09-23",
    "\U0001F7E2 **STEP 5 BUILT AND MEASURED",
    "\U0001F7E2\U0001F7E2 **M3a-4 DELIVERED 2026-09-23 18:5x \u2014 THE CURRENT BED",
    "\U0001F7E1 **THE RETROSPECTIVE RAN AND NAMED THE SAME FAULT INDEPENDENTLY",
    "\u2705 **REVIEWS THIS CYCLE, BOTH ANSWERED",
]
lines = io.open(ST, encoding="utf-8").read().split("\n")
nxt = next(i for i, l in enumerate(lines) if l.startswith("## NEXT"))
idx = []
for p in PREFIXES:
    hits = [i for i, l in enumerate(lines) if i > nxt and l.startswith(p)]
    assert len(hits) == 1, (p, hits)
    idx.append(hits[0])
idx.sort()
moved = [lines[i] for i in idx]
arch = io.open(AR, encoding="utf-8").read().rstrip("\n").split("\n")
assert not any(l.startswith("## \u00a73") for l in arch)
arch += ["", "## \u00a73 Historical cycle-67/68 `## NEXT` paragraphs (STATUS.md lines %s before this pass), VERBATIM"
         % ",".join(str(i + 1) for i in idx), ""] + moved + [""]
io.open(AR, "w", encoding="utf-8", newline="\n").write("\n".join(arch))
ptr = ("\U0001F535 **Seven historical cycle-67/68 NEXT paragraphs (M3a-4 delivered \u00d72, M4 superseded, models "
       "re-pinned, step 5, retrospective-cycle67, c89 reviews) RELOCATED VERBATIM \u2192 "
       "`archive/2026-09-24-status-cycle72-relocate.md` \u00a73** (cycle 73).")
new = []
for i, l in enumerate(lines):
    if i == idx[0]:
        new.append(ptr)
    if i in idx:
        continue
    new.append(l)
io.open(ST, "w", encoding="utf-8", newline="\n").write("\n".join(new))
print("moved %d paragraphs; STATUS %d -> %d lines" % (len(idx), len(lines), len(new)))
