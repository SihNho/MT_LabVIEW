# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_167-a1-5.md
# ---
r"""diag_c167_a1_5_relocate - card 167-a1-5 Part C (OFFLINE, bytes only): proof that the STATUS.md `## NEXT` history bullets older than
cycle 164 were moved VERBATIM to archive/2026-10-12-status-cycle167-relocate.md §1 and replaced by ONE pointer line.
Found before writing: the earlier relocations (archive/2026-10-08-status-cycle150-relocate.md) were proved by hand; no shared relocation
checker exists. The bed key check CALLS errorlist_check.current_bed_text (tools/errorlist_check.py:164), as diag_c166_a1_2_hash.py:45 does.
argv[1] = save | check.
  save : copies STATUS.md bytes to tools/bench/diag_c167_a1_5_status_pre.md (the pre-edit copy) and prints its md5 and line count.
  check: the moved block = the CONTIGUOUS run of pre-edit lines from the first '- (history' bullet naming 'CYCLE 163' through the last
         line that starts with '- (history' directly after it (expected: 12 lines, CYCLE 163 ... Cycle 158 round 3).
PREDICTION CONTRACT (check):
 M  every moved line appears, byte-equal and in order, as one contiguous run in the archive file's §1 (12 of 12).
 S  STATUS.md after == pre-edit with exactly that run replaced by the one POINTER line (byte compare of the whole file, CRLF kept).
 N  line count after == before - 12 + 1.
 K  errorlist_check.current_bed_text(STATUS.md after) -> claudeDev\D1_ring_p5_20261010_172913.vi.
 R  machine keys unchanged: the 'rig-state:', 'current-bed:', 'labview-lock' lines and the '## HARDWARE' line are equal before/after.
 H  the moved lines name no cycle >= 164 (each carries 'CYCLE 16[0-3]' / 'CYCLE 159' / 'Cycle 158' text).
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c167_a1_5_relocate_<mode>.log -- py -u tools/bench/diag_c167_a1_5_relocate.py <mode>"""
import os, re, sys                                                                          # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import errorlist_check as EC                                                                # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
MODE = sys.argv[1] if len(sys.argv) > 1 else "check"
ST = os.path.join(ROOT, "STATUS.md")
PRE = os.path.join(ROOT, "tools", "bench", "diag_c167_a1_5_status_pre.md")
ARC = os.path.join(ROOT, "archive", "2026-10-12-status-cycle167-relocate.md")
POINTER = b"- (history) RELOCATED VERBATIM -> archive/2026-10-12-status-cycle167-relocate.md \xc2\xa71 (NEXT history older than cycle 164)"
BED = "D1_ring_p5_20261010_172913.vi"
gate = L.Gate(fatal_default=False)

if MODE == "save":
    raw = open(ST, "rb").read()
    open(PRE, "wb").write(raw)
    print("FACT saved {0} md5 {1} lines {2}".format(os.path.relpath(PRE, ROOT), L.md5(PRE), raw.count(b"\n")), flush=True)
    gate("W pre-edit copy byte-equal to STATUS.md", open(PRE, "rb").read() == open(ST, "rb").read())
    sys.exit(gate.result([{"path": os.path.relpath(PRE, ROOT).replace("\\", "/"), "md5": L.md5(PRE)}]))

pre = open(PRE, "rb").read().split(b"\r\n" if b"\r\n" in open(PRE, "rb").read() else b"\n")
nl = b"\r\n" if b"\r\n" in open(PRE, "rb").read() else b"\n"
a = next(i for i, x in enumerate(pre) if x.startswith(b"- (history") and b"CYCLE 163" in x[:120])
b = a
while b + 1 < len(pre) and pre[b + 1].startswith(b"- (history"):
    b += 1
moved = pre[a:b + 1]
if MODE == "archive":                                                                      # the archive file, bytes copied from the pre-edit copy
    head = ["---", "type: archive", "status: frozen", "date: 2026-10-12", "tags: [status, relocation, cycle167]", "---", "",
            "# STATUS.md relocation, cycle 167 (`docs/d1/ring-p6.md` PD404 note (7), card 167-a1-5)", "",
            "Written by `tools/bench/diag_c167_a1_5_relocate.py archive` from the pre-edit copy `tools/bench/diag_c167_a1_5_status_pre.md`",
            "(md5 {0}): the STATUS.md `## NEXT` history bullets older than cycle 164 (pre-edit lines {1}..{2}), VERBATIM and in their".format(L.md5(PRE), a + 1, b + 1),
            "original order (CLAUDE.md rule 4: moved, never rewritten). STATUS.md keeps a one-line pointer to this file.", "",
            "## §1 NEXT history older than cycle 164", ""]
    if os.path.exists(ARC):
        print("FACT {0} exists already - not overwritten".format(ARC), flush=True)
        sys.exit(1)
    open(ARC, "wb").write(nl.join([h.encode("utf-8") for h in head] + moved + [b""]))
    print("FACT wrote {0} md5 {1}: {2} moved lines".format(os.path.relpath(ARC, ROOT), L.md5(ARC), len(moved)), flush=True)
    sys.exit(gate.result([{"path": "archive/2026-10-12-status-cycle167-relocate.md", "md5": L.md5(ARC)}]))
post = open(ST, "rb").read().split(nl)
print("FACT moved block = pre-edit lines {0}..{1} ({2} lines), md5 pre {3}, after {4}".format(a + 1, b + 1, len(moved), L.md5(PRE), L.md5(ST)), flush=True)
for i, x in enumerate(moved):
    print("FACT moved {0}: {1}".format(a + 1 + i, x[:90].decode("utf-8", "replace")), flush=True)
arc = open(ARC, "rb").read().split(nl if nl in open(ARC, "rb").read() else b"\n")
s1 = next(i for i, x in enumerate(arc) if x.startswith(b"## \xc2\xa71"))
pos = next((i for i in range(s1, len(arc)) if arc[i:i + len(moved)] == moved), None)
gate("M {0} moved lines byte-equal, in order, contiguous in {1} §1 (at archive line {2})".format(len(moved), os.path.basename(ARC),
     None if pos is None else pos + 1), pos is not None and len(moved) == 12, len(moved))
want = pre[:a] + [POINTER] + pre[b + 1:]
gate("S STATUS.md after == pre-edit with lines {0}..{1} replaced by the one pointer line (whole-file byte compare)".format(a + 1, b + 1),
     post == want, next((i + 1 for i, (x, y) in enumerate(zip(post, want)) if x != y), "length {0} vs {1}".format(len(post), len(want))))
gate("N line count after {0} == before {1} - {2} + 1".format(len(post) - 1, len(pre) - 1, len(moved)), len(post) == len(pre) - len(moved) + 1)
got = EC.current_bed_text(open(ST, encoding="utf-8").read())
print("FACT current_bed_text(STATUS.md after) -> {0!r}".format(got), flush=True)
gate("K current_bed_text names {0}".format(BED), bool(got) and os.path.basename(got) == BED, got)
keys = (b"rig-state:", b"current-bed:", b"## HARDWARE", b"## LabVIEW execution lock")
kp = [x for x in pre if x.startswith(keys) or b"labview-lock" in x]
kq = [x for x in post if x.startswith(keys) or b"labview-lock" in x]
gate("R machine-key lines equal before/after ({0} lines)".format(len(kp)), kp == kq and len(kp) >= 4, len(kq))
old = [bool(re.search(rb"CYCLE 16[0-3]|CYCLE 159|Cycle 158", x[:200])) and not re.search(rb"CYCLE 16[4-9]", x[:200]) for x in moved]
gate("H every moved line is about a cycle < 164 ({0} of {1})".format(sum(old), len(moved)), all(old))
sys.exit(gate.result([{"path": "archive/2026-10-12-status-cycle167-relocate.md", "md5": L.md5(ARC)}]))
