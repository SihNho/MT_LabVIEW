r"""selftest_c134_1_dry - card 134-1 (a3, PD287(a), docs/violation-decisions.md repeated-failure-class 2026-10-02 10:10).
OFFLINE: no COM, no LabVIEW, nothing outside %TEMP% written (records go to a temp RECORDS file).
EXISTING checked first: tools/bench/selftest_c133_6_fr.py (FR base-set test, not the dry rule), selftest_dry_c130_5.py
(executor-stop rule). Neither tests the relabelling rule.
PREDICTION:
  T1 133-3's session-a recipe bytes (md5 ababd4ed..., from git) -> `stage_prerun --dry` = FAIL, first_fail names FR.
  T2 the fixed bytes at tools/recipes/stage_d1_ring_p3b2a.py (md5 bb5ba064...) -> DRY PASS (no UNVERIFIED gate).
  T3 a fixture recipe whose only questionable gates read COM stubs -> DRY PASS-UNVERIFIED naming both.
  T4 check_launch refuses that PASS-UNVERIFIED record without --unverified-card; T5 allows it (dry part) with a card naming
     both gates; T6 refuses with a card naming only one.
  T7 stagekit.census_gate with declared {} prints UNPREDICTED and records no PASS.
"""
import hashlib, io, json, os, subprocess, sys, tempfile, time      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                 # noqa: E402

TMP = tempfile.mkdtemp(prefix="c134_1_dry_")
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def md5b(b):
    return hashlib.md5(b).hexdigest()


def git_bytes(path, want):
    revs = subprocess.run(["git", "log", "--format=%H", "--", path], cwd=ROOT, capture_output=True, text=True).stdout.split()
    for r in revs:
        b = subprocess.run(["git", "show", "{0}:{1}".format(r, path)], cwd=ROOT, capture_output=True).stdout
        b2 = b.replace(b"\r\n", b"\n")
        for x in (b, b2, b2.replace(b"\n", b"\r\n")):
            if md5b(x).startswith(want):
                return r, x
    return None, None


def dry(path, extra=()):
    p = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "stage_prerun.py"), "--dry", path, "--no-record"]
                       + list(extra), cwd=ROOT, capture_output=True, text=True, timeout=240)
    line = [ln for ln in p.stdout.splitlines() if ln.startswith("=== DRY ")]
    return p.returncode, (line[-1] if line else "NO DRY LINE: " + p.stdout[-400:] + p.stderr[-400:]), p.stdout


# T1 - the 133-3 bytes. git holds ONE version of the recipe (0b72718d = bb5ba064, the FR fix); ababd4ed was never
# committed, so the 133-3 bytes are RECONSTRUCTED by undoing the 133-6 fix (review archive/peer/2026-10-02-c133-6-fr-p3b2a.md:22
# "bf = frames(terminal rows) UNION the base's FS frame lists ... nothing else in the gate changed") and accepted only when
# the md5 matches; otherwise the closest candidate is used and labelled.
rev, b = git_bytes("tools/recipes/stage_d1_ring_p3b2a.py", "ababd4ed")
how = "git " + str(rev)
if b is None:
    curb = open(os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b2a.py"), "rb").read()
    nl = b"\r\n" if b"\r\n" in curb else b"\n"
    lines = curb.split(nl)
    i30 = [i for i, x in enumerate(lines) if x.startswith(b"basef = lambda")]
    cands = []
    for bf in (b'    bf = frames(BASE["terminals"])', None):
        L = [x for i, x in enumerate(lines) if i not in i30]
        if bf is not None:
            L = [bf if x.strip() == b"bf = basef(BASE)" else x for x in L]
        else:
            L2 = [x for x in L if x.strip() != b"bf = basef(BASE)"]
            L = [x.replace(b"set(on) <= bf and frames(real) == bf",
                           b'set(on) <= frames(BASE["terminals"]) and frames(real) == frames(BASE["terminals"])') for x in L2]
        cands.append(nl.join(L))
    hit = [c for c in cands if md5b(c).startswith("ababd4ed")]
    b = hit[0] if hit else cands[0]
    how = "reconstructed md5 {0} ({1})".format(md5b(b), "== ababd4ed" if hit else "!= ababd4ed: closest candidate, FR rule only")
gate("T0 the 133-3 FR rule bytes (ababd4ed or the undone fix)", b is not None, how)
if b is not None:
    old = os.path.join(TMP, "stage_d1_ring_p3b2a_ababd4ed.py")
    open(old, "wb").write(b)
    rc, ln, out = dry(old)
    gate("T1 ababd4ed -> dry FAIL naming FR", ln.startswith("=== DRY FAIL") and "GATE FR" in ln, ln[:260])
# T2 - the fixed bytes
cur = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b2a.py")
gate("T2a fixed recipe md5 == bb5ba064", md5b(open(cur, "rb").read()).startswith("bb5ba064"), md5b(open(cur, "rb").read()))
rc, ln, out = dry(cur)
gate("T2 bb5ba064 -> DRY PASS (no unverified)", ln.startswith("=== DRY PASS:") and rc == 0 and "unverified 0" in ln, ln[:260])
gate("T7a its empty-declared CEN2 printed UNPREDICTED, not PASS", "UNPREDICTED  CEN2" in out and "PASS  CEN2" not in out,
     [x for x in out.splitlines() if "CEN2" in x][:2])
# T3 - stub-only fixture
BASE = json.load(open(os.path.join(ROOT, "tools", "bench", "sim", "ring_p3b2_base_real_fsmap.json"), encoding="utf-8"))
fx = os.path.join(TMP, "stage_zz_c134_1_stubonly.py")
open(fx, "w", encoding="utf-8").write(r'''"""fixture (card 134-1 self-test): two gates on COM stubs only."""
import os, sys
sys.path.insert(0, {tools!r})
import stagekit as K, gscript as g          # noqa: E401


def body(s):
    s.start()
    s.gate("ZS1 exec state is 0 (stub)", g.exec_state(s.work) == 0)
    s.gate("ZS2 stub truth", g.some_reader(s.work))
    s.gate("ZP plain python truth", 1 + 1 == 2)


if __name__ == "__main__":
    st = K.Stage({vi!r}, {md5!r}, "zz_c134_1", preload=False, deadline_min=5,
                 out_json=os.path.join(K.BENCH, "zz_c134_1.json"), task="selftest")
    sys.exit(K.run(body, st))
'''.format(tools=os.path.join(ROOT, "tools"), vi=BASE["vi"], md5=BASE["md5"]))
rc, ln, out = dry(fx, ["--graph", os.path.join(ROOT, "tools", "bench", "sim", "ring_p3b2_base_real_fsmap.json")])
gate("T3 stub-only fixture -> DRY PASS-UNVERIFIED naming ZS1 and ZS2", ln.startswith("=== DRY PASS-UNVERIFIED") and "ZS1" in ln
     and "ZS2" in ln and "ZP" not in ln.split("first_fail")[0], ln[:300])
# T3b/T3c - review archive/peer/2026-10-02-c134-1-dry-selftest.md:95-106: a stub used by an UNRELATED statement (s.es) or
# a Fake in the previous gate's detail must not relabel a FALSE gate on plain data
fx2 = os.path.join(TMP, "stage_zz_c134_1_leak.py")
open(fx2, "w", encoding="utf-8").write(r'''"""fixture (card 134-1 self-test T3b/T3c): taint leaks."""
import os, sys
sys.path.insert(0, {tools!r})
import stagekit as K, gscript as g          # noqa: E401


def body(s):
    s.start()
    s.es("x")
    s.gate("ZB plain false after an unrelated stub statement", 1 == 2)
    s.gate("ZD detail carries a stub", True, g.some_reader(s.work))
    s.gate("ZC plain false after a stub detail", 1 == 2)


if __name__ == "__main__":
    st = K.Stage({vi!r}, {md5!r}, "zz_c134_1b", preload=False, deadline_min=5,
                 out_json=os.path.join(K.BENCH, "zz_c134_1b.json"), task="selftest")
    sys.exit(K.run(body, st))
'''.format(tools=os.path.join(ROOT, "tools"), vi=BASE["vi"], md5=BASE["md5"]))
rc, ln, out = dry(fx2, ["--graph", os.path.join(ROOT, "tools", "bench", "sim", "ring_p3b2_base_real_fsmap.json")])
gate("T3b/T3c leak fixture -> DRY FAIL naming ZB, ZC also FAIL (not UNVERIFIED)", ln.startswith("=== DRY FAIL") and "GATE ZB" in ln
     and "FAIL  ZC" in out and "UNVERIFIED  ZC" not in out and "UNVERIFIED  ZB" not in out, ln[:260])
# T4-T6 - launch gate on a temp records file
sys.argv = ["x"]
import stage_prerun as SP                                            # noqa: E402
SP.RECORDS = os.path.join(TMP, "records.jsonl")
SP.STAGE_RUNS = os.path.join(TMP, "stage_runs.jsonl")
for kind, st, extra in (("dry", "PASS-UNVERIFIED", {"unverified": ["ZS1 exec state is 0 (stub)", "ZS2 stub truth"],
                                                    "dry_rule": SP.DRY_RULE}), ("prerun", "PASS", {})):
    SP.write_record(kind, fx, st, None, extra)
units = [(fx, None)]
ok4, why4 = SP._check_units(units, "py -u " + fx)
gate("T4 no card -> refused naming PASS-UNVERIFIED", not ok4 and "PASS-UNVERIFIED" in why4, why4[:240])
card = {"schema": "task/1", "id": "zz-1", "rules": ["DRY-UNVERIFIED-OK: ZS1; ZS2"]}
cp = os.path.join(TMP, "task_zz-1.json")
json.dump(card, open(cp, "w", encoding="utf-8"))
ok5, why5 = SP._check_units(units, "py -u {0} --unverified-card {1}".format(fx, cp))
gate("T5 card names ZS1 + ZS2 -> dry part allowed", ok5 or "PASS-UNVERIFIED" not in why5, why5[:240])
card["rules"] = ["DRY-UNVERIFIED-OK: ZS1"]
json.dump(card, open(cp, "w", encoding="utf-8"))
ok6, why6 = SP._check_units(units, "py -u {0} --unverified-card {1}".format(fx, cp))
gate("T6 card names only ZS1 -> refused, ZS2 named", not ok6 and "ZS2" in why6, why6[:240])
# T7 - census gate directly
import stagekit as K                                                 # noqa: E402


class _S(object):
    def __init__(self):
        self.R, self.passes = {}, []

    def gate(self, label, ok, detail="", fatal=False):
        self.passes.append((label, ok))


buf, so = io.StringIO(), sys.stdout
sys.stdout = buf
try:
    s_ = _S()
    K.Stage.census_gate(s_, "CENX", {1: "A"}, {1: "A"}, {})
finally:
    sys.stdout = so
gate("T7 census_gate declared {} -> UNPREDICTED, no gate call", "UNPREDICTED  CENX" in buf.getvalue() and not s_.passes
     and s_.R.get("unpredicted") == ["CENX"], buf.getvalue().strip()[:200])
n_f = res.count(False)
print(P.result_line(P.make_result(res.count(True), n_f, None if not n_f else "selftest_c134_1_dry")), flush=True)
sys.exit(1 if n_f else 0)
