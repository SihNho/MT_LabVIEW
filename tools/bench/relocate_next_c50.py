"""Relocate STATUS.md's current ## NEXT section VERBATIM into an archive file (rule 4: copy, never rewrite).

Prediction contract:
  - STATUS.md contains exactly one line equal to '## NEXT'.
  - The next line starting with '## ' after it is '## Where to look — ...'.
  - The extracted block is written byte-identical (no reflow, no re-encode beyond utf-8 round-trip)
    into archive/2026-09-20-status-cycle50-relocate.md under a frontmatter block and a
    '## §1 — cycle 49's NEXT, verbatim' heading.
  - STATUS.md itself is NOT modified (judgement rewrites NEXT).
Gate lines printed as GATE n PASS/FAIL.
"""
import io, os, sys, hashlib

ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
STATUS = os.path.join(ROOT, "STATUS.md")
OUT = os.path.join(ROOT, "archive", "2026-09-20-status-cycle50-relocate.md")

fails = 0
def gate(n, cond, msg):
    global fails
    line = "GATE %s %s %s" % (n, "PASS" if cond else "FAIL", msg)
    print(line.encode("ascii", "replace").decode("ascii"))
    if not cond:
        fails += 1

with io.open(STATUS, "r", encoding="utf-8", newline="") as f:
    raw = f.read()
before_md5 = hashlib.md5(raw.encode("utf-8")).hexdigest()
lines = raw.split("\n")

idx = [i for i, l in enumerate(lines) if l.strip() == "## NEXT"]
gate(1, len(idx) == 1, "'## NEXT' occurrences=%d" % len(idx))
if len(idx) != 1:
    sys.exit(1)
start = idx[0]
end = None
for i in range(start + 1, len(lines)):
    if lines[i].startswith("## "):
        end = i
        break
gate(2, end is not None, "next '## ' heading at line %s: %r" % (end + 1 if end else None, lines[end][:40] if end else None))
if end is None:
    sys.exit(1)

block = "\n".join(lines[start:end]).rstrip("\n")
gate(3, len(block) > 2000, "block chars=%d lines=%d" % (len(block), block.count("\n") + 1))

out = (
    "---\n"
    "type: archive\n"
    "status: superseded\n"
    "date: 2026-09-20\n"
    "tags: [status-relocation, cycle50]\n"
    "---\n"
    "\n"
    "# 2026-09-20 — STATUS relocation, cycle 50\n"
    "\n"
    "Relocated VERBATIM (CLAUDE.md rule 4 — copy, never rewrite) out of `STATUS.md` by the cycle-50 material\n"
    "session. Nothing here was edited; the cycle-50 judgement session writes the replacement NEXT.\n"
    "\n"
    "## \u00a71 \u2014 cycle 49's NEXT, verbatim\n"
    "\n"
    + block + "\n"
)
with io.open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)

with io.open(OUT, "r", encoding="utf-8", newline="") as f:
    back = f.read()
gate(4, block.replace("\r\n", "\n") in back, "verbatim block present in archive file")

with io.open(STATUS, "r", encoding="utf-8", newline="") as f:
    raw2 = f.read()
after_md5 = hashlib.md5(raw2.encode("utf-8")).hexdigest()
gate(5, before_md5 == after_md5, "STATUS.md unmodified md5 %s" % after_md5)

print("ARCHIVE %s bytes=%d" % (OUT, os.path.getsize(OUT)))
print("FAILS %d" % fails)
sys.exit(1 if fails else 0)
