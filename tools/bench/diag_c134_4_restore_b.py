"""Card 134-4 step 4a (PD289(d)): restore tools/bench/plan_ring_p3b2b.json to md5 1451ba90 FROM GIT HEAD, by script.
OFFLINE, no LabVIEW. The failed d2bbd289 copy is kept as plan_ring_p3b2b_c134_2_fail.json (made by 134-2; re-made here if absent).
EXISTING: git HEAD 0b72718d holds the file; `git show HEAD:<path>` gives the raw blob (LF, md5 f3dfff07 measured), the working tree
under core.autocrlf holds CRLF - so the blob is passed through `git cat-file --filters` (checkout's own EOL/smudge filters).
PREDICTION: R1 the filtered HEAD blob md5 == 1451ba90; R2 written file md5 == 1451ba90; R3 the fail copy holds d2bbd289."""
import hashlib, os, shutil, subprocess, sys                                                   # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                           # noqa: E402
PIN, FAILMD5 = "1451ba90aadc594fe74f97793eb04e92", "d2bbd289bcae4c90af9ab09b43c2ea5e"
REL = "tools/bench/plan_ring_p3b2b.json"
PB, FAILC = os.path.join(ROOT, REL), os.path.join(ROOT, "tools/bench/plan_ring_p3b2b_c134_2_fail.json")
md5b = lambda b: hashlib.md5(b).hexdigest()                                                   # noqa: E731
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", n, d), flush=True)


cur = md5b(open(PB, "rb").read())
print("  FACT  before: {0} md5 {1}".format(REL, cur), flush=True)
if not os.path.isfile(FAILC) and cur == FAILMD5:
    shutil.copyfile(PB, FAILC)
gate("R3 failed copy plan_ring_p3b2b_c134_2_fail.json holds d2bbd289", os.path.isfile(FAILC) and md5b(open(FAILC, "rb").read()) == FAILMD5)
raw = subprocess.run(["git", "show", "HEAD:" + REL], cwd=ROOT, capture_output=True, check=True).stdout
flt = subprocess.run(["git", "cat-file", "--filters", "HEAD:" + REL], cwd=ROOT, capture_output=True, check=True).stdout
print("  FACT  HEAD blob raw md5 {0}, filtered (checkout EOL) md5 {1}".format(md5b(raw), md5b(flt)), flush=True)
gate("R1 filtered HEAD blob md5 == 1451ba90", md5b(flt) == PIN)
if ok[-1][1]:
    open(PB, "wb").write(flt)
gate("R2 {0} md5 == 1451ba90 after restore".format(REL), md5b(open(PB, "rb").read()) == PIN, md5b(open(PB, "rb").read()))
nf = sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(len(ok) - nf, nf, next((n for n, c in ok if not c), None),
                                  [{"path": REL, "md5": md5b(open(PB, "rb").read())}])), flush=True)
sys.exit(1 if nf else 0)
