r"""selftest_c134_1_dry - card 134-1 (a3, PD287(a), docs/violation-decisions.md repeated-failure-class 2026-10-02 10:10).
OFFLINE: no COM, no LabVIEW, nothing outside %TEMP% written (records go to a temp RECORDS file).
EXISTING checked first: tools/bench/selftest_c133_6_fr.py (FR base-set test, not the dry rule), selftest_dry_c130_5.py
(executor-stop rule). Neither tests the relabelling rule.
PREDICTION:
  T1 133-3's session-a recipe bytes (md5 ababd4ed..., from git) -> `stage_prerun --dry` = FAIL, first_fail names FR.
  T2 the fixed bytes at tools/recipes/stage_d1_ring_p3b2a.py (md5 bb5ba064...) -> DRY PASS (no UNVERIFIED gate).
     card 160-f3-1 (PD391(g)): T2a = full md5 0d1f0c15 AND the bytes without the trailing scope header == bb5ba064; T2 runs the dry
     on a temp copy whose PB compares the stored pred rows / open pairs through stagekit.pb_check (PD370(b) converter) and expects
     DRY PASS[-UNVERIFIED] with `unverified N`, N counted by PD387(e) (stage_prerun.dry_unverified_labels on the dry's output).
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
# card 160-f3-1 (PD391(g), docs/d1/ring-p5b.md:165-169): (a) since card chat-E3 the recipe carries the trailing scope header, so the
# full-file md5 the gate computes is 0d1f0c15; the gate also proves the change is header-only (bytes without it == bb5ba064).
# (b) its PB compares the stored NAME-keyed pred rows; vigraph a7eb58c7 (PD370(b), commit 18c241ec, ring-p4d.md:172-183) drops the
# rename-only slot, so the dry end lacks the four '2626|Terminal|array|0..3' rows (diag_c160_f3_1_pb.log M2). PD370(b) keeps the
# pred byte-unchanged and converts in the self-test: the dry runs on a TEMP COPY whose PB condition is the one line replaced by
# stagekit.pb_check (pos_convert / pos_convert_open_rows, stagekit.py:1774-1802) on the same stored rows and open pairs.
# (c) T2 counts unverified items by PD387(e) (stage_prerun.py:1074-1075): stage_prerun.dry_unverified_labels on the dry's output.
PB_NAME = (b'rk == PRED["cdiff_rows"] and set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"]) == '
           b'set((int(y["node"]), y["term"]) for y in P["open_rows"]),')
PB_POS = b'K.pb_check(S1f, G1, K.pred_end_graph(L, LAB, FSPAIRS), PRED["cdiff_rows"], P["open_rows"])["ok"],'


def header_free_md5(b):
    """md5 of a script's bytes without its trailing scope header (`# --- / # labview: .. / # hardware: .. / # ---`, card chat-E3);
    None when it carries none. Self-test: tools/bench/selftest_c134_1_dry.py T2a."""
    nl = b"\r\n" if b"\r\n" in b else b"\n"
    lines = b.split(nl)
    tail = lines[-5:]
    if len(tail) == 5 and tail[0] == b"# ---" and tail[1].startswith(b"# labview:") and tail[2].startswith(b"# hardware:") \
            and tail[3] == b"# ---" and tail[4] == b"":
        return md5b(nl.join(lines[:-5]) + nl)
    return None


cur = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b2a.py")
cb = open(cur, "rb").read()
gate("T2a fixed recipe md5 == 0d1f0c15, header-only change of bb5ba064", md5b(cb).startswith("0d1f0c15")
     and (header_free_md5(cb) or "").startswith("bb5ba064"), (md5b(cb), header_free_md5(cb)))
conv = os.path.join(TMP, "pbpos")
os.makedirs(conv)
conv = os.path.join(conv, "stage_d1_ring_p3b2a.py")
open(conv, "wb").write(cb.replace(PB_NAME, PB_POS))
rc, ln, out = dry(conv)
sys.argv = ["x"]
import stage_prerun as SP                                            # noqa: E402
unv = SP.merge_unverified([], SP.dry_unverified_labels(out.splitlines()))
print("  FACT  T2 PB line replaced {0}x; dry unverified by PD387(e): {1}".format(cb.count(PB_NAME), unv), flush=True)
gate("T2 bb5ba064 (+header), PB converted per PD370(b) -> DRY PASS, unverified == PD387(e) count {0}".format(len(unv)),
     cb.count(PB_NAME) == 1 and rc == 0 and ln.startswith("=== DRY PASS") and "unverified {0},".format(len(unv)) in ln
     and ("PASS-UNVERIFIED" in ln) == bool(unv), ln[:300])
# card 136-P1 (fp-30): since 135-2 the recipe's CEN2 carries a DECLARED census (plan_ring_p3b2a_pred.json), and a dry run
# prints it `UNVERIFIED-DRY  CEN2 ... (census not measured in a dry run; declared {...})`
# (tools/bench/selftest_c134_1_dry_c136_p1_t2.log:75), no longer `UNPREDICTED`. The invariant this gate guards is
# unchanged: an unmeasured census is never a PASS in a dry run. The empty-declared case stays covered by T7 below.
gate("T7a its CEN2 printed UNPREDICTED or UNVERIFIED-DRY, never PASS",
     ("UNPREDICTED  CEN2" in out or "UNVERIFIED-DRY  CEN2" in out) and "PASS  CEN2" not in out,
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
# ---
# labview: none
# hardware: none
# ---
