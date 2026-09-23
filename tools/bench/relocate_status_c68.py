"""relocate_status_c68 - CLAUDE.md rule 4 bookkeeping (no LabVIEW). Moves the HISTORICAL M3a-4 / pre-runner-tooling
lines of STATUS.md's NEXT section (all delivered by 2026-09-23 18:5x) VERBATIM into
archive/2026-09-23-status-cycle68-relocate.md and leaves one pointer line. Selects lines by their opening marker,
refuses if any marker matches != 1 line."""
import io, os
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
SP = os.path.join(ROOT, "STATUS.md")
AP = os.path.join(ROOT, "archive", "2026-09-23-status-cycle68-relocate.md")
MARKERS = ("🔴🔴 **PRE-RUNNER TOOLING (historical, all delivered)",
           "🔴🔴 **PRE-RUNNER TOOLING FIRST (user 2026-09-23 06:0x",
           "🟢🟢 **THE `ExecState` 0 BLOCKER IS NAMED",
           "🟢 **AND THE PASS CRITERION IS REACHABLE",
           "🔵 Also settled this cycle, so nobody re-measures them",
           "🔴 **FIRST ACT — M3a-4 STEP 1",
           "🔴 **SECOND ACT — M3a-4 STEP 2")
lines = io.open(SP, encoding="utf-8").read().split("\n")
idx = []
for m in MARKERS:
    hits = [i for i, l in enumerate(lines) if l.startswith(m)]
    if len(hits) != 1:
        raise SystemExit("marker {0!r}: {1} hits - nothing changed".format(m[:40], len(hits)))
    idx.append(hits[0])
moved = [lines[i] for i in sorted(idx)]
head = ("---\ntype: archive\nstatus: archived\ndate: 2026-09-23\ntags: [status-relocate]\n---\n\n"
        "# STATUS.md NEXT lines relocated VERBATIM, 2026-09-23 23:5x (cycle 68 material, rule 4)\n\n"
        "All describe M3a-4 / pre-runner tooling work DELIVERED by 2026-09-23 18:5x. Nothing rewritten.\n\n")
io.open(AP, "w", encoding="utf-8").write(head + "\n".join(moved) + "\n")
ptr = ("🔵 **M3a-4 blocker analysis, ACT 1/2 briefs, pre-runner tooling plan lines (all DELIVERED by 18:5x) RELOCATED "
       "VERBATIM → `archive/2026-09-23-status-cycle68-relocate.md`** (7 lines).")
first = min(idx)
out = [l for i, l in enumerate(lines) if i not in idx]
out.insert(first, ptr)
io.open(SP, "w", encoding="utf-8", newline="\n").write("\n".join(out))
print("moved", len(moved), "lines; STATUS", len(lines), "->", len(out))
