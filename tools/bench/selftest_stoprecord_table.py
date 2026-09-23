r"""selftest_stoprecord_table.py - cases GENERATED from stop_record.DECISION_TABLE (cycle 73; docs/violation-
decisions.md "device-failed - 2026-09-24 06:2x": the release logic written once as a table, self-test from it).

    py tools/bgrun.py --material --max-min 10 --log tools/bench/selftest_stoprecord_table.log -- \
        py -u tools/bench/selftest_stoprecord_table.py

PRIOR ART: selftest_stoprecord_supersession.py (REVIEW/DISPOSED/UNDISPOSED templates imported, temp STORE per
case, scratch recipe under tools/recipes/ deleted in the same run). No LabVIEW.
PREDICTION CONTRACT
  T*  for every (kind, state, class) row of DECISION_TABLE, every command of that class gets the row's outcome
      ("skip" rows are built with a later allowing record, so the command's expected answer is allow)
  N*  against an UNDISPOSED record, commands that could EXECUTE the recipe through a read-only-looking program
      are refused ($(..), backtick, `| py`, `py -c exec`, `sed -i`, other_tool --recipe, `wc && py -u`)
  L*  the live read-only commands refused in cycles 71/72 (material_marker.log) are allowed
  Z   the real store is never touched; the scratch recipe is gone
"""
import hashlib
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import stop_record as sr  # noqa: E402
import selftest_stoprecord_supersession as sup  # noqa: E402  (templates only; its main() is not run)

passes, fails = [], []
STEM = "scratch_table_%d_%d" % (os.getpid(), int(time.time()))
X = "tools/recipes/%s.py" % STEM
XA = os.path.join(ROOT, "tools", "recipes", STEM + ".py")
XB = X.replace("/", "\\")

CMDS = {
    "build": ["py tools/bgrun.py --material --max-min 5 --log tools/bench/%s.log -- py -u %s" % (STEM, X),
              "py %s" % XB],
    "readonly": ["wc -l %s" % X, "sed -n 1,40p %s" % X, "(Get-Content %s | Measure-Object -Line).Lines" % XB,
                 "py -c \"import ast,sys;ast.parse(open(sys.argv[1],encoding='utf-8').read());print('ok')\" %s" % XB,
                 'grep -n "labview-lock" -A5 STATUS.md | head -8; sed -n 1,40p %s' % X,
                 'cd "%s" && cat %s' % (ROOT, X)],
    "exempt": ["py tools/stop_record.py write --recipe %s --review r.md --verdict x" % X,
               "py tools/bgrun.py --material --max-min 20 --log tools/bench/pa.log -- py tools/prior_art_review.py "
               "--slug t --recipe %s" % X],
}
NEG = ["wc -l $(py %s)" % X, "wc -l `py %s`" % X, "cat %s | py -" % X,
       "py -c \"exec(open('%s').read())\"" % X, "sed -i s/a/b/ %s" % X,
       "py tools/other_tool.py --recipe %s" % X, "wc -l %s && py -u %s" % (X, X),
       "Get-Content %s | iex" % XB]


def gate(ok, label, detail=""):
    (passes if ok else fails).append(label)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)


def fp(p):
    if not os.path.exists(p):
        return "absent"
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def review(tmp, name, verdict, disposed):
    p = os.path.join(tmp, name)
    body = sup.REVIEW.format(slug="t", date=time.strftime("%Y-%m-%d"), slug_verdict=verdict)
    if verdict != "novel":
        body += (sup.DISPOSED if disposed else sup.UNDISPOSED).format(slug_verdict=verdict)
    write(p, body)
    return p


def build_state(tmp, kind, state):
    """Plant records in the (already redirected) store so that the FIRST record for X is in `state`."""
    write(XA, "print('v1')\n")
    if kind == "blocking":
        rv = review(tmp, "b.md", "already-failed", state != "undisposed")
        sr.write_stop_record(X, rv, ["already-failed"])
    else:
        rv = review(tmp, "n.md", "novel", True)
        sr.write_novel_record(X, rv)
        if state == "undisposed":                     # the review stopped saying novel
            write(rv, open(rv, encoding="utf-8").read() + "\nPRIOR-ART: already-failed\n")
    if state in ("released", "sha-mismatch", "superseded", "unreadable") and kind == "blocking":
        sr._check(CMDS["build"][0])                   # stamp the release with v1
    if state in ("sha-mismatch", "superseded"):
        write(XA, "print('v2')\n")
    if state == "superseded":                         # a later record allowing the v2 bytes
        sr.write_novel_record(X, review(tmp, "later.md", "novel", True))
    if state == "unreadable":
        os.remove(XA)


def main():
    print("=== selftest_stoprecord_table on %s: %d table rows ===" % (sr.__file__, len(sr.DECISION_TABLE)),
          flush=True)
    real = (sr.STORE, sr.MARKER)
    before = (fp(real[0]), fp(real[1]))
    try:
        for kind, state, cls, outcome in sr.DECISION_TABLE:
            for j, cmd in enumerate(CMDS[cls]):
                tmp = tempfile.mkdtemp(prefix="srtable_")
                try:
                    sr.STORE, sr.MARKER = os.path.join(tmp, "s.json"), os.path.join(tmp, "s.marker")
                    build_state(tmp, kind, state)
                    got = sr._check(cmd)[0]
                    want = outcome in ("allow", "skip")
                    gate(got == want, "T %s/%s/%s #%d -> %s" % (kind, state, cls, j, outcome),
                         "allow=%s" % got if got == want else "allow=%s cmd=%s" % (got, cmd[:90]))
                finally:
                    sr.STORE, sr.MARKER = real
                    shutil.rmtree(tmp, ignore_errors=True)
        tmp = tempfile.mkdtemp(prefix="srtable_neg_")
        try:
            sr.STORE, sr.MARKER = os.path.join(tmp, "s.json"), os.path.join(tmp, "s.marker")
            build_state(tmp, "blocking", "undisposed")
            for j, cmd in enumerate(NEG):
                got = sr._check(cmd)[0]
                gate(not got, "N%d executing form refused" % j, "allow=%s cmd=%s" % (got, cmd[:80]))
            for j, cmd in enumerate(CMDS["readonly"]):
                gate(sr._check(cmd)[0], "L%d live read-only form allowed" % j, cmd[:80])
            gate(sr.segment_class("py -u " + X) == "build", "L6 segment_class(py -u X) == build")
        finally:
            sr.STORE, sr.MARKER = real
            shutil.rmtree(tmp, ignore_errors=True)
    finally:
        try:
            os.remove(XA)
        except OSError:
            pass
    gate(not os.path.exists(XA), "Z1 scratch recipe deleted")
    gate(before == (fp(real[0]), fp(real[1])), "Z2 real store untouched")
    print("\n=== selftest_stoprecord_table: %d pass, %d fail ===" % (len(passes), len(fails)), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
