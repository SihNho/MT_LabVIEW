r"""selftest_c116a_landed.py - card 116-3 D1/D2: audit_cycle A9 (accepted-but-unbuilt dispositions cited by code),
doc_lint L8 (violation-decisions.md HH:MM headers) and guard_card's cd-to-root rule. OFFLINE, no LabVIEW, writes only a
tempfile.mkdtemp sandbox (removed at exit).
FOUND FIRST: tools/bench/diag_c115a_dispositions.py (115-1 C1 scan: citations + deferral words, no witness),
selftest_errorlist_reuse_81.py K1-K9 (guard_card decide), violations.py DEC_RE (the header shape L8 checks).
PREDICTION CONTRACT
  S1-S6  A9 on a synthetic root: accepted+unbuilt uncited -> absent; cited by tools/x.py -> landed; cited only by a
         non-selftest tools/bench file -> absent; cited by tools/bench/selftest_* -> landed; `NOT ACCEPTED` + not applied
         -> no candidate; ACCEPTED with no unbuilt line -> no candidate
  A1     real archive, git-HEAD bytes of guard_card.py + doc_lint.py (pre-fix): retrospective-cycle77 is ABSENT
  A2     real archive, working tree (post-fix): retrospective-cycle77 is LANDED (doc_lint.py L8 cites it)
  A3     FACT (no gate): hyp-selftest-elreuse-81 before/after, and the absent count before/after
  H1-H5  L8 on a synthetic file: 2026-09-28 07:5x FAIL, bare 2026-09-28 FAIL, 2026-09-28 07:50 PASS, 2026-09-27 07:5x
         WARN, bare 2026-09-27 not reported;  H6 real violation-decisions.md: 0 FAIL, 8 WARN
  C1-C4  guard_card.pure_selftest: cd foreign -> False; cd "<ROOT>" / cd '<ROOT>' / no cd -> True
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c116a_landed.log -- py -u tools/bench/selftest_c116a_landed.py
"""
import atexit, os, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")]
import protocol as P      # noqa: E402
import audit_cycle as AC  # noqa: E402
import doc_lint as DL     # noqa: E402
import guard_card as GC   # noqa: E402

G = []


def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-78s %s %s" % (label, "PASS" if ok else "FAIL", str(detail)[:220]), flush=True)


T = tempfile.mkdtemp(prefix="c116a_landed_"); atexit.register(shutil.rmtree, T, True)


def w(rel, text):
    p = os.path.join(T, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


SEC = "# r\n\n## Answer\nx\n\n## What was done with it\n\n%s\n"
w("archive/peer/2026-09-28-s-uncited.md", SEC % "- finding 1 ACCEPTED; the fix is not built this cycle.")
w("archive/peer/2026-09-28-s-code.md", SEC % "- ACCEPTED.\n- NOT fixed here: left open for judgement.")
w("archive/peer/2026-09-28-s-bench.md", SEC % "- ACCEPTED, not applied.")
w("archive/peer/2026-09-28-s-selftest.md", SEC % "- ACCEPTED, not yet applied.")
w("archive/peer/2026-09-28-s-notacc.md", SEC % "- NOT ACCEPTED: the rule was not applied because ...")
w("archive/peer/2026-09-28-s-done.md", SEC % "- ACCEPTED and applied in tools/x.py.")
w("tools/x.py", "# fix for archive/peer/2026-09-28-s-code.md\n")
w("tools/bench/diag_x.py", "# cites s-bench\n")
w("tools/bench/selftest_y.py", "# pins 2026-09-28-s-selftest\n")
absent, n = AC.a9_unlanded(T, "2026-09-28-*.md")
gate("2026-09-28-s-uncited" in absent, "S1 accepted+unbuilt, uncited -> absent", absent)
gate("2026-09-28-s-code" not in absent, "S2 cited by tools/x.py -> landed", absent)
gate("2026-09-28-s-bench" in absent, "S3 cited only by tools/bench/diag_x.py -> absent", absent)
gate("2026-09-28-s-selftest" not in absent, "S4 cited by tools/bench/selftest_y.py -> landed", absent)
gate(n == 4, "S5/S6 NOT ACCEPTED and ACCEPTED-without-unbuilt are not candidates (4 candidates)", n)


def head(rel):
    return subprocess.run(["git", "show", "HEAD:" + rel], cwd=ROOT, capture_output=True, text=True,
                          encoding="utf-8", errors="replace").stdout


over = {"tools/hooks/guard_card.py": head("tools/hooks/guard_card.py"), "tools/doc_lint.py": head("tools/doc_lint.py")}
gate(all(len(v) > 1000 for v in over.values()), "A0 git HEAD bytes of guard_card.py and doc_lint.py read",
     {k: len(v) for k, v in over.items()})
SELF = {"tools/bench/selftest_c116a_landed.py": ""}   # this file names the reviews it checks; it must not witness them
b_abs, b_n = AC.a9_unlanded(code_override=dict(over, **SELF))
a_abs, a_n = AC.a9_unlanded(code_override=SELF)
C77 = "2026-09-25-retrospective-" + "cycle77"
gate(C77 in b_abs, "A1 pre-fix (HEAD bytes): retrospective-cycle77 ABSENT", len(b_abs))
gate(C77 not in a_abs, "A2 post-fix (working tree): retrospective-cycle77 LANDED", len(a_abs))
E = "2026-09-25-hyp-selftest-" + "elreuse-81"
print("FACT A3 elreuse-81 before %s after %s; candidates %d/%d; absent before %d after %d" % (
    "absent" if E in b_abs else "landed", "absent" if E in a_abs else "landed", b_n, a_n, len(b_abs), len(a_abs)))
print("FACT A3 absent after: %s" % a_abs)
hd = os.path.join(T, "vd.md")
open(hd, "w", encoding="utf-8").write("\n".join([
    "## device-failed — 2026-09-28 07:5x (a)", "## device-failed — 2026-09-28 (b)", "## device-failed — 2026-09-28 07:50 (c)",
    "## device-failed — 2026-09-27 07:5x (d)", "## device-failed — 2026-09-27 (e)"]) + "\n")
f, wn = DL.check_decision_headers(hd)
fl, wl = [x.rsplit(":", 1)[-1] for x in f], [x.rsplit(":", 1)[-1] for x in wn]
gate("1" in fl, "H1 2026-09-28 07:5x -> FAIL", fl)
gate("2" in fl, "H2 bare 2026-09-28 -> FAIL", fl)
gate("3" not in fl and "3" not in wl, "H3 2026-09-28 07:50 -> PASS", (fl, wl))
gate(wl == ["4"], "H4 2026-09-27 07:5x -> WARN (only)", wl)
gate("5" not in fl and "5" not in wl, "H5 bare 2026-09-27 -> not reported", (fl, wl))
f, wn = DL.check_decision_headers()
gate(f == [] and len(wn) == 8, "H6 real violation-decisions.md: 0 FAIL, 8 WARN", (f, wn))
R = ROOT.replace("\\", "/")
gate(not GC.pure_selftest('cd "C:/elsewhere" && py tools/stagexec.py selftest'), "C1 cd <foreign> -> not exempt")
gate(GC.pure_selftest('cd "%s" && py -u tools/stagexec.py selftest' % R), "C2 cd \"<ROOT>\" -> exempt")
gate(GC.pure_selftest("cd '%s' && py tools/stagexec.py selftest" % ROOT), "C3 cd '<ROOT>' (backslashes) -> exempt")
gate(GC.pure_selftest("py tools/stagexec.py selftest"), "C4 no cd -> exempt")
npass = sum(1 for g in G if g[0]); nfail = len(G) - npass
print(P.result_line(P.make_result(npass, nfail, next((g[1] for g in G if not g[0]), None))), flush=True)
sys.exit(0 if nfail == 0 else 1)
