"""Relocate STATUS.md lock keys owner_c68..c71 and the cycle 69-71 DONE/OLD-FIRST-ACT paragraphs VERBATIM."""
import io
import os
import sys

ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
ST = os.path.join(ROOT, "STATUS.md")
AR = os.path.join(ROOT, "archive", "2026-09-24-status-cycle72-relocate.md")
lines = io.open(ST, encoding="utf-8").read().split("\n")

LOCK_PREFIXES = ("  owner_c71", "  owner_c70", "  owner_c69", "  owner_c68")
lock_idx = [i for i, l in enumerate(lines) if l.startswith(LOCK_PREFIXES)]
assert lock_idx and lock_idx == list(range(lock_idx[0], lock_idx[-1] + 1)), lock_idx

start = next(i for i, l in enumerate(lines) if l.startswith("\u2705 **CYCLE 71 DONE (for the record).**"))
end = next(i for i, l in enumerate(lines) if l.startswith("\u2705 **(DONE cycle 69) ACT 2 (a REPAIR)"))
assert start < end and end - start < 20, (start, end)
block = lines[start:end + 1]
must = ["\u2705 **CYCLE 70 DONE", "\u2705 **CYCLE 69 DONE", "\U0001F534 **(DONE cycle 71) OLD FIRST ACT",
        "\u2705 **(DONE cycle 70) OLD FIRST ACT", "\U0001F534 **OLD FIRST ACT (cycle 69, DONE)"]
for m in must:
    assert any(l.startswith(m) for l in block), m

arch = ["---", "type: archive", "status: archived", "date: 2026-09-24", "tags: [status-relocate]", "---",
        "# STATUS.md relocation \u2014 cycle 73 (2026-09-24, material; rule 4, VERBATIM)", "",
        "## \u00a71 Lock-block keys `owner_c71*` / `owner_c70*` / `owner_c69*` / `owner_c68*` "
        "(STATUS.md lines %d-%d before relocation), VERBATIM" % (lock_idx[0] + 1, lock_idx[-1] + 1), "", "```yaml"]
arch += [lines[i] for i in lock_idx] + ["```", "",
         "## \u00a72 `## NEXT` paragraphs: CYCLE 69/70/71 DONE, (DONE cycle 70/71) OLD FIRST ACT, OLD FIRST ACT "
         "(cycle 69, DONE), ACT 2 (DONE cycle 69) (STATUS.md lines %d-%d before relocation), VERBATIM"
         % (start + 1, end + 1), ""]
arch += block + [""]
io.open(AR, "w", encoding="utf-8", newline="\n").write("\n".join(arch))

lock_ptr = ("  relocated_c72: lock keys owner_c71l71b2/owner_c71l71b/owner_c71l71ab/owner_c71l71a/owner_c70l71r2/"
            "owner_c70l71/owner_c69p0/owner_c68srpair/owner_c68build/owner_c68m4q RELOCATED VERBATIM -> "
            "`archive/2026-09-24-status-cycle72-relocate.md` \u00a71")
next_ptr = ("\u2705 **CYCLES 69\u201371 DONE records + their OLD FIRST ACT / ACT 2 paragraphs RELOCATED VERBATIM \u2192 "
            "`archive/2026-09-24-status-cycle72-relocate.md` \u00a72** (cycle 73, rule 4).")
new = lines[:lock_idx[0]] + [lock_ptr] + lines[lock_idx[-1] + 1:start] + [next_ptr] + lines[end + 1:]
io.open(ST, "w", encoding="utf-8", newline="\n").write("\n".join(new))
print("lock keys %d, NEXT lines %d, STATUS %d -> %d lines" % (len(lock_idx), len(block), len(lines), len(new)))
