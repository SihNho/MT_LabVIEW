# ---
# labview: none
# hardware: none
# ---
r"""diag_c150_a1_2_move - card 150-a1-2 (PD364(h)): relocate STATUS.md blocks VERBATIM to
archive/2026-10-08-status-cycle150-relocate.md. Byte-level: STATUS.md is UTF-8 with BOM + CRLF; every moved line's bytes
(without its CRLF) are appended to the archive (LF file) unchanged; each moved block leaves ONE pointer line.

Works FROM the before-copy tools/bench/diag_c150_a1_2_status_before.md (md5 050f34f4581c483bd9e65654210fa190), so a rerun is
idempotent. Prior art checked: earlier relocations (cards 81-1, 123-6) used the same pointer convention; no generic relocate
tool exists in tools/ (ls tools/*.py) - this is a one-shot card-local script.

PREDICTION CONTRACT: before md5 matches; anchors match (line 10 '(history) STOP - RUNNER KILLED', line 20 '(history) STOP
(lifted for one trial cycle)', line 22 '(history) STOP (lifted 03:2x)', line 73 '(cycle 149 round 3)', line 156 '  - Carries:
fp-30', line 157 '- **CYCLE 133 in brief'); new STATUS.md = 110 lines; archive grows by 3 sections, 11 + 1 + 84 = 96 moved lines.
"""
import hashlib
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

BEFORE = os.path.join(ROOT, "tools", "bench", "diag_c150_a1_2_status_before.md")
STATUS = os.path.join(ROOT, "STATUS.md")
ARCH_REL = "archive/2026-10-08-status-cycle150-relocate.md"
ARCH = os.path.join(ROOT, *ARCH_REL.split("/"))
BEFORE_MD5 = "050f34f4581c483bd9e65654210fa190"
ARCH_MD5 = "01e1727a76321f5286b05eac4d8af6d9"
POINTER = "(history) RELOCATED VERBATIM -> " + ARCH_REL + " §{n}"
# (section, first, last, title, anchor_first, anchor_last)  1-based, inclusive, lines of the BEFORE copy
BLOCKS = [
    (1, 10, 20, "STATUS.md top banner `(history)` lines", "(history) STOP - RUNNER KILLED",
     "(history) STOP (lifted for one trial cycle)"),
    (2, 22, 22, "STATUS.md top banner `(history)` line", "(history) STOP (lifted 03:2x)", "(history) STOP (lifted 03:2x)"),
    (3, 73, 156, "STATUS.md `## NEXT` paragraphs older than cycle 150 (cycle 149 round 3 down to the cycle 134 brief)",
     "(cycle 149 round 3)", "  - Carries: fp-30"),
]


def md5(b):
    return hashlib.md5(b).hexdigest()


def main():
    gp, gf, first = 0, 0, None

    def gate(ok, label):
        nonlocal gp, gf, first
        print(("PASS " if ok else "FAIL ") + label)
        if ok:
            gp += 1
        else:
            gf += 1
            first = first or label
        return ok

    raw = open(BEFORE, "rb").read()
    if not gate(md5(raw) == BEFORE_MD5, "before-copy md5 %s" % md5(raw)):
        return gp, gf, first
    cur = md5(open(STATUS, "rb").read())
    if not gate(cur == BEFORE_MD5, "live STATUS.md unchanged since the copy (md5 %s)" % cur):
        return gp, gf, first
    arch_raw = open(ARCH, "rb").read()
    already = md5(arch_raw) != ARCH_MD5
    if not gate(not already, "archive still the 12-line header (md5 %s)" % md5(arch_raw)):
        return gp, gf, first
    lines = raw.split(b"\r\n")
    assert lines[-1] == b"", "before copy must end with CRLF"
    lines = lines[:-1]
    gate(len(lines) == 203, "before lines %d == 203" % len(lines))
    for sec, a, b, _t, fa, fb in BLOCKS:
        gate(lines[a - 1].decode("utf-8").startswith(fa), "anchor L%d starts %r" % (a, fa))
        gate(lines[b - 1].decode("utf-8").startswith(fb), "anchor L%d starts %r" % (b, fb))
    gate(lines[156].decode("utf-8").startswith("- **CYCLE 133 in brief"), "L157 is the kept cycle-133 brief")
    if gf:
        return gp, gf, first

    moved_idx = set()
    new = []
    starts = {a: (sec, b) for sec, a, b, _t, _fa, _fb in BLOCKS}
    i = 1
    while i <= len(lines):
        if i in starts:
            sec, b = starts[i]
            new.append(POINTER.format(n=sec).encode("utf-8"))
            moved_idx.update(range(i, b + 1))
            i = b + 1
        else:
            new.append(lines[i - 1])
            i += 1
    out_arch = arch_raw if arch_raw.endswith(b"\n") else arch_raw + b"\n"
    for sec, a, b, title, _fa, _fb in BLOCKS:
        head = "\n## §%d - %s - STATUS.md source lines %d-%d (STATUS.md md5 %s, card 150-a1-2)\n\n" % (
            sec, title, a, b, BEFORE_MD5)
        out_arch += head.encode("utf-8")
        for k in range(a, b + 1):
            out_arch += lines[k - 1] + b"\n"
    open(ARCH, "wb").write(out_arch)
    open(STATUS, "wb").write(b"\r\n".join(new) + b"\r\n")
    gate(len(new) == 110, "new STATUS lines %d == 110" % len(new))
    gate(len(moved_idx) == 96, "moved lines %d == 96" % len(moved_idx))
    print("STATUS md5", md5(open(STATUS, "rb").read()), "ARCHIVE md5", md5(out_arch))
    return gp, gf, first


if __name__ == "__main__":
    p, f, ff = main()
    print(protocol.result_line(protocol.make_result(p, f, ff, artefacts=[
        {"path": "STATUS.md", "md5": md5(open(STATUS, "rb").read())},
        {"path": ARCH_REL, "md5": md5(open(ARCH, "rb").read())}])))
    sys.exit(0 if f == 0 else 1)
