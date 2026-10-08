# ---
# labview: none
# hardware: none
# evidence: archive/peer/2026-10-09-c153-a2-6-origmd5.md
# ---
"""diag_c153_a2_6_rsrc - card 153-a2-6, OFFLINE (bytes only, no LabVIEW): the hypothesis review's cheapest discriminating test
(archive/peer/2026-10-09-c153-a2-6-origmd5.md:74-79) before the one LabVIEW read: stat the CURRENT original 4.5 (md5 2f048e3a) and
diff it RSRC block by block against the 2026-09-18 byte snapshot claudeDev\\Track_D0_copy_20260918.vi (c39f36e0 per
archive/2026-09-18-status-cycle30-d0.md:26).
PRIOR ART: tools/bench/t2_rsrc_blockdiff.py parse_rsrc (imported; stdlib only, no COM) - nothing new built.
PREDICTION (mechanical only; which blocks differ is the MEASUREMENT, not predicted): D0 copy hashes c39f36e0; original hashes
2f048e3a before == after; both files parse with self-checks C1..C7 PASS. RESULT pass 4 fail 0."""
import datetime, hashlib, os, sys                                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [HERE, os.path.join(ROOT, "tools")]
import protocol, t2_rsrc_blockdiff as T                                                       # noqa: E401,E402
ORIG = os.path.join(os.path.dirname(ROOT), "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
D0 = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Track_D0_copy_20260918.vi"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                  # noqa: E731
G = []


def gate(label, ok, d=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


for tag, p in (("ORIGINAL", ORIG), ("D0_COPY", D0)):
    st = os.stat(p)
    print("  FACT  {0}: size {1} mtime {2} ctime {3} md5 {4}".format(tag, st.st_size, datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
          datetime.datetime.fromtimestamp(st.st_ctime).isoformat(timespec="seconds"), md5(p)), flush=True)
m0 = md5(ORIG)
gate("P1 D0 snapshot hashes c39f36e0 (the census-time original)", md5(D0).startswith("c39f36e0"), md5(D0))
L, R = open(D0, "rb").read(), open(ORIG, "rb").read()
lrec, lchk = T.parse_rsrc(L, "D0_20260918")
rrec, rchk = T.parse_rsrc(R, "ORIGINAL_NOW")
gate("P2 both parse, self-checks C1..C7 PASS", lrec["parsed"] and rrec["parsed"] and all(c["ok"] for c in lchk + rchk),
     [c["check"] for c in lchk + rchk if not c["ok"]])
print("  FACT  version candidates D0 {0} | NOW {1}".format(lrec.get("version_candidates"), rrec.get("version_candidates")), flush=True)
lm, rm = dict((b["ident"], b) for b in lrec["blocks"]), dict((b["ident"], b) for b in rrec["blocks"])
same, diff = [], []
for k in sorted(set(lm) & set(rm)):
    (same if lm[k]["sha256"] == rm[k]["sha256"] else diff).append(k)
print("  FACT  sizes D0 {0} -> NOW {1} ({2:+d} B); blocks {3} -> {4}".format(len(L), len(R), len(R) - len(L), len(lm), len(rm)), flush=True)
print("  FACT  IDENTICAL blocks ({0}): {1}".format(len(same), same), flush=True)
print("  FACT  DIFFERENT blocks ({0}): {1}".format(len(diff), ["{0} {1}->{2} B".format(k, lm[k]["total_payload"], rm[k]["total_payload"]) for k in diff]), flush=True)
print("  FACT  ONLY-D0 {0} ; ONLY-NOW {1}".format(sorted(set(lm) - set(rm)), sorted(set(rm) - set(lm))), flush=True)
for k in diff:
    for ls, rs in zip(lm[k]["sections"], rm[k]["sections"]):
        if ls.get("sha256") != rs.get("sha256"):
            print("  FACT  {0} section {1}: {2} B -> {3} B".format(k, ls.get("section_idx"), ls.get("payload_len"), rs.get("payload_len")), flush=True)
gate("P3 original hashes 2f048e3a", m0.startswith("2f048e3a"), m0)
gate("P4 original md5 after == before", md5(ORIG) == m0)
fails = [l for l, ok in G if not ok]
print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(G) - len(fails), "fail": len(fails)},
                            "first_fail": fails[0] if fails else None, "artefacts": []}), flush=True)
sys.exit(0 if not fails else 1)
