r"""selftest_audit_a9_witness.py - card 117-3 D5: audit_cycle A9 counts as witness ONLY a code file the disposition itself
names (never tools/bench/selftest_*). OFFLINE, no LabVIEW; writes only a tempfile.mkdtemp sandbox (removed at exit).
FOUND FIRST: selftest_c116a_landed.py S1-S6 (the pre-117-3 witness rule; its S2/S4 encode that rule and flip by design).
PREDICTION CONTRACT
  W1 accepted+unbuilt, names tools/x.py which cites the stem -> landed
  W2 names tools/x.py, stem cited only by tools/bench/selftest_y.py -> absent (the elreuse-81/K9 shape)
  W3 names tools/bench/selftest_y.py which cites the stem -> absent (a selftest never witnesses)
  W4 names nothing, stem cited by tools/z.py -> absent (an unnamed file never witnesses)
  W5 names bare `z.py` (resolves to tools/hooks/z.py alone) which cites the stem -> landed
  W6 names tools/x.py that does NOT cite the stem -> absent;  W7 `NOT ACCEPTED` line naming a file -> no candidate
  W8 file named only on ANOTHER item's line -> absent (per-item scope, review archive/peer/2026-09-28-c117c-a9.md §2)
  W9 `hooks/z.py` and an absolute `.../tools/x.py` resolve; an indented continuation line belongs to its item -> landed
  R1 real archive: elreuse-81 is NOT witnessed by any tools/bench file (the K9 pin); relabelled after review c117c-a9 §1
  FACT: every real absent item with its deferred items and named files; HEAD (116-3) A9 vs this A9 on the same tree
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_audit_a9_witness.log -- py -u tools/bench/selftest_audit_a9_witness.py
"""
import atexit, os, shutil, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path[:0] = [os.path.join(ROOT, "tools")]
import protocol as P      # noqa: E402
import audit_cycle as AC  # noqa: E402

G = []


def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-74s %s %s" % (label, "PASS" if ok else "FAIL", str(detail)[:220]), flush=True)


T = tempfile.mkdtemp(prefix="a9_witness_"); atexit.register(shutil.rmtree, T, True)


def w(rel, text):
    p = os.path.join(T, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(text)


SEC = "# r\n\n## Answer\nx\n\n## What was done with it\n\n%s\n"
w("archive/peer/2026-09-28-w1.md", SEC % "- ACCEPTED; fixed in `tools/x.py:10`, the rest not built.")
w("archive/peer/2026-09-28-w2.md", SEC % "- ACCEPTED; `tools/x.py` to change, not built.")
w("archive/peer/2026-09-28-w3.md", SEC % "- ACCEPTED; pinned in tools/bench/selftest_y.py, fix not built.")
w("archive/peer/2026-09-28-w4.md", SEC % "- ACCEPTED, not applied.")
w("archive/peer/2026-09-28-w5.md", SEC % "- ACCEPTED: `z.py:3` changed; the other half left open.")
w("archive/peer/2026-09-28-w6.md", SEC % "- ACCEPTED: `tools/q.py` to change, not fixed.")
w("archive/peer/2026-09-28-w7.md", SEC % "- NOT ACCEPTED: tools/x.py not built on purpose.")
w("archive/peer/2026-09-28-w8.md", SEC % "- ACCEPTED, fixed in tools/x.py.\n- ACCEPTED, the second fix not built.")
w("archive/peer/2026-09-28-w9.md", SEC % "- ACCEPTED: the z fix in hooks/z.py is not built yet,\n  and G:/a/2. T/p/tools/x.py too.")
w("tools/x.py", "# fix for 2026-09-28-w1 and 2026-09-28-w8 and 2026-09-28-w9\n")
w("tools/q.py", "# nothing cited\n")
w("tools/hooks/z.py", "# fix for 2026-09-28-w4 and 2026-09-28-w5 and 2026-09-28-w9\n")
w("tools/bench/selftest_y.py", "# pins 2026-09-28-w2 and 2026-09-28-w3\n")
det = {}
absent, n = AC.a9_unlanded(T, "2026-09-28-*.md", detail=det)
gate("2026-09-28-w1" not in absent, "W1 named tools/x.py cites stem -> landed", det.get("2026-09-28-w1"))
gate("2026-09-28-w2" in absent, "W2 named file silent, only a selftest cites -> absent", det.get("2026-09-28-w2"))
gate("2026-09-28-w3" in absent, "W3 named selftest never witnesses -> absent", det.get("2026-09-28-w3"))
gate("2026-09-28-w4" in absent, "W4 no file named, unnamed tools/hooks/z.py cites -> absent", det.get("2026-09-28-w4"))
gate("2026-09-28-w5" not in absent, "W5 bare z.py -> tools/hooks/z.py cites -> landed", det.get("2026-09-28-w5"))
gate("2026-09-28-w6" in absent, "W6 named tools/q.py does not cite -> absent", det.get("2026-09-28-w6"))
gate(n == 8 and "2026-09-28-w7" not in det, "W7 NOT ACCEPTED is not a candidate (8 candidates)", n)
gate("2026-09-28-w8" in absent, "W8 file named on ANOTHER item's line does not witness the deferred item -> absent",
     det.get("2026-09-28-w8", {}).get("items"))
gate("2026-09-28-w9" not in absent and set(det["2026-09-28-w9"]["named"]) == {"tools/hooks/z.py", "tools/x.py"},
     "W9 hooks/z.py and an absolute .../tools/x.py resolve (continuation line joins the item) -> landed", det.get("2026-09-28-w9"))
real = {}
r_abs, r_n = AC.a9_unlanded(detail=real)
E = "2026-09-25-hyp-selftest-" + "elreuse-81"
gate(E in real and not any(r.startswith("tools/bench/") for r in real[E]["witness"]),
     "R1 real archive: elreuse-81 is not witnessed by the pinning selftest K9", real.get(E, {}).get("witness"))
print("FACT candidates %d absent %d" % (r_n, len(r_abs)), flush=True)
for s in r_abs:
    print("FACT absent %s items=%s" % (s, [(x["item"][:60], x["named"]) for x in real[s]["items"]]), flush=True)
for s in sorted(set(real) - set(r_abs)):
    print("FACT landed %s witness=%s" % (s, real[s]["witness"]), flush=True)
import importlib.util, subprocess  # noqa: E401,E402  review c117c-a9 §4 test 1: HEAD (116-3) A9 vs this A9, same tree
hp = os.path.join(T, "audit_cycle_head.py")
open(hp, "w", encoding="utf-8").write(subprocess.run(["git", "show", "HEAD:tools/audit_cycle.py"], cwd=ROOT,
                                      capture_output=True, text=True, encoding="utf-8", errors="replace").stdout)
sp = importlib.util.spec_from_file_location("audit_cycle_head", hp); H = importlib.util.module_from_spec(sp)
sp.loader.exec_module(H)
h_abs, h_n = H.a9_unlanded(root=ROOT)
print("FACT HEAD-rule candidates %d absent %d; only-new-absent %s; only-HEAD-absent %s" % (
    h_n, len(h_abs), sorted(set(r_abs) - set(h_abs)), sorted(set(h_abs) - set(r_abs))), flush=True)
npass = sum(1 for x in G if x[0]); nfail = len(G) - npass
print(P.result_line(P.make_result(npass, nfail, next((x[1] for x in G if not x[0]), None))), flush=True)
sys.exit(0 if nfail == 0 else 1)
