# ---
# labview: none
# hardware: none
# ---
r"""diag_c150_a1_2_check - card 150-a1-2 step 4: mechanical proof that the STATUS.md relocation moved lines VERBATIM.

Inputs: before-copy tools/bench/diag_c150_a1_2_status_before.md (050f34f4...), the new STATUS.md, the archive file
archive/2026-10-08-status-cycle150-relocate.md (its first 12 lines must equal the original header, md5 01e1727a...).

PREDICTION CONTRACT (all PASS): new STATUS 100..120 lines; header untouched; pointer lines == 3; new STATUS minus pointers ==
before minus moved lines (same order, byte-equal); archive body == moved lines (same order, byte-equal, per-section ranges as
the headings say); multiset(before) == multiset(kept) + multiset(archive body); every keep-listed region of the brief is in
the new STATUS byte-identical.
"""
import collections
import hashlib
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

BEFORE = os.path.join(ROOT, "tools", "bench", "diag_c150_a1_2_status_before.md")
STATUS = os.path.join(ROOT, "STATUS.md")
ARCH_REL = "archive/2026-10-08-status-cycle150-relocate.md"
ARCH = os.path.join(ROOT, *ARCH_REL.split("/"))
HEADER_MD5 = "01e1727a76321f5286b05eac4d8af6d9"
PTR_PREFIX = ("(history) RELOCATED VERBATIM -> " + ARCH_REL + " §").encode("utf-8")
HEAD_RE = re.compile(r"^## §(\d+) - .* - STATUS\.md source lines (\d+)-(\d+) ")
# keep-listed regions of brief step 2 (before-copy line numbers, inclusive)
KEEP = [("frontmatter", 1, 6), ("STOP/RESTARTED lines", 7, 9), ("START HERE", 32, 36), ("lock block", 38, 44),
        ("hardware banner + rig-state", 49, 56), ("OPEN", 61, 67), ("NEXT heading + PARALLELISM RULE", 69, 70),
        ("CYCLE 150 PURPOSE + OUTCOME ESCALATION", 71, 72), ("current-bed key + comment", 184, 185),
        ("Where to look", 199, 199)]


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

    before = open(BEFORE, "rb").read().split(b"\r\n")[:-1]
    new_raw = open(STATUS, "rb").read()
    gate(new_raw.endswith(b"\r\n") and b"\r\n" in new_raw and new_raw.startswith(b"\xef\xbb\xbf"),
         "new STATUS keeps BOM + CRLF")
    new = new_raw.split(b"\r\n")[:-1]
    gate(100 <= len(new) <= 120, "new STATUS lines %d in 100..120" % len(new))
    arch = open(ARCH, "rb").read()
    alines = arch.split(b"\n")
    header = b"\n".join(alines[:12]) + b"\n"
    gate(hashlib.md5(header).hexdigest() == HEADER_MD5, "archive 12-line header byte-identical")

    # sections of the archive body
    sections, cur = [], None
    for ln in alines[12:]:
        m = HEAD_RE.match(ln.decode("utf-8"))
        if m:
            cur = [int(m.group(1)), int(m.group(2)), int(m.group(3)), []]
            sections.append(cur)
        elif cur is not None and ln != b"":
            cur[3].append(ln)
    gate(len(sections) >= 1, "archive sections %d" % len(sections))
    moved_idx = []
    for sec, a, b, body in sections:
        exp = before[a - 1:b]
        gate(body == exp, "section %d body == before lines %d-%d (%d lines)" % (sec, a, b, len(exp)))
        moved_idx.extend(range(a, b + 1))
    moved_set = set(moved_idx)
    gate(len(moved_set) == len(moved_idx), "no line moved twice")

    ptrs = [ln for ln in new if ln.startswith(PTR_PREFIX)]
    gate(len(ptrs) == len(sections), "pointer lines %d == sections %d" % (len(ptrs), len(sections)))
    for sec, a, _b, _body in sections:
        # pointer sits where the block began: count kept lines before a
        pos = sum(1 for k in range(1, a) if k not in moved_set) + sum(1 for s2 in sections if s2[1] < a)
        gate(pos < len(new) and new[pos] == PTR_PREFIX + str(sec).encode(), "pointer for section %d at new line %d" % (sec, pos + 1))
    kept_new = [ln for ln in new if not ln.startswith(PTR_PREFIX)]
    kept_before = [before[k - 1] for k in range(1, len(before) + 1) if k not in moved_set]
    gate(kept_new == kept_before, "new STATUS minus pointers == before minus moved (%d lines, order + bytes)" % len(kept_new))
    body_all = [ln for s in sections for ln in s[3]]
    gate(collections.Counter(before) == collections.Counter(kept_new) + collections.Counter(body_all),
         "multiset before == kept + archive body (%d == %d + %d)" % (len(before), len(kept_new), len(body_all)))
    newset = set(new)
    for name, a, b in KEEP:
        ok = all(before[k - 1] in newset for k in range(a, b + 1)) and not (set(range(a, b + 1)) & moved_set)
        gate(ok, "kept byte-identical: %s (before %d-%d)" % (name, a, b))
    print("moved ranges:", [(s[0], s[1], s[2]) for s in sections])
    return gp, gf, first


if __name__ == "__main__":
    p, f, ff = main()
    md5 = lambda path: hashlib.md5(open(path, "rb").read()).hexdigest()  # noqa: E731
    print(protocol.result_line(protocol.make_result(p, f, ff, artefacts=[
        {"path": "STATUS.md", "md5": md5(STATUS)}, {"path": ARCH_REL, "md5": md5(ARCH)}])))
    sys.exit(0 if f == 0 else 1)
