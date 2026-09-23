"""Rule 4 relocation (cycle 68, material): move STATUS.md lock-block lines 44-64 VERBATIM to
archive/2026-09-24-status-cycle68-relocate.md and leave one pointer key. No LabVIEW.

Prior art: earlier relocations were done by hand-Edit (e.g. archive/2026-09-21-status-cycle67-locknotes.md);
these 21 lines total ~40k tokens, so a byte-exact script is cheaper and cannot paraphrase.
Prediction contract: line 44 starts '  owner: MATERIAL dispatch — OpAllTerms_v0 STEP 1 ROUTE-FINDER', line 64 starts
'  purpose: 🔴 **THE STRAY', line 65 is '```'; archive file absent before; after: STATUS = before - 21 + 1 lines,
archive body == the removed lines byte for byte.
"""
import io, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ST = os.path.join(ROOT, "STATUS.md")
AR = os.path.join(ROOT, "archive", "2026-09-24-status-cycle68-relocate.md")
A, B = 44, 64
raw = open(ST, "rb").read().decode("utf-8")
lines = raw.split("\n")
n0 = len(lines)
ok = (lines[A - 1].startswith("  owner: MATERIAL dispatch — OpAllTerms_v0 STEP 1 ROUTE-FINDER")
      and lines[B - 1].startswith("  purpose: \U0001F534 **THE STRAY") and lines[B].startswith("```")
      and not os.path.exists(AR))
print("PRE", "PASS" if ok else "FAIL", n0, flush=True)
if not ok:
    sys.exit(1)
moved = lines[A - 1:B]
head = ("---\ntype: archive\nstatus: archived\ndate: 2026-09-24\ntags: [status-relocate]\n---\n"
        "# STATUS.md relocation — cycle 68 (2026-09-24 01:0x, material)\n\n"
        "## §1 Historical lock-block keys (STATUS.md lines 44-64 as of 2026-09-24 01:0x), VERBATIM\n\n```yaml\n")
body = "\n".join(moved) + "\n"
io.open(AR, "w", encoding="utf-8", newline="").write(head + body + "```\n")
ptr = ("  relocated_c68: 21 historical lock keys (cycles 67-68 + connectivity-map steps 0-2; `owner`/`owner_gui`x2/"
       "`purpose_*`/`owner_prev_*`/`since`/`purpose`) RELOCATED VERBATIM -> `archive/2026-09-24-status-cycle68-relocate.md` §1")
if lines[A - 1].endswith("\r"):
    ptr += "\r"
new = lines[:A - 1] + [ptr] + lines[B:]
io.open(ST, "w", encoding="utf-8", newline="").write("\n".join(new))
chk = open(AR, "rb").read().decode("utf-8")
g1 = body in chk
g2 = len(open(ST, "rb").read().decode("utf-8").split("\n")) == n0 - (B - A + 1) + 1
print("POST archive-verbatim", "PASS" if g1 else "FAIL")
print("POST status-linecount", "PASS" if g2 else "FAIL", len(new))
sys.exit(0 if g1 and g2 else 1)
